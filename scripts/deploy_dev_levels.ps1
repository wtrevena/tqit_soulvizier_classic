<#
.SYNOPSIS
  Deploy a built Levels.arc to the SoulvizierClassicDEV CustomMaps folder, safely.

.DESCRIPTION
  Written for the b89 ocean_extension05 hotfix (2026-07-27), when the deploy had to wait
  for Will's running TQ.exe to exit (the game holds Levels.arc open for the whole session,
  and killing his game is never an option).

  Safety properties:
    * NEVER kills or launches TQ / Steam. If TQ.exe is running it either waits (-WaitForTQ)
      or exits non-zero.
    * Copies to a temp file IN THE TARGET DIRECTORY, md5-verifies the temp against the
      source, and only then replaces the live file. An interrupted run can therefore never
      leave a half-written Levels.arc behind.
    * Backs up the file it is about to replace (unless -NoBackup).
    * Hashes the sibling arz / Text.arc / Quests.arc before AND after and fails loudly if
      any of them changed - the map deploy must touch nothing else.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts/deploy_dev_levels.ps1 `
      -Source  "<repo>/.claude/worktrees/ocean05-hotfix/local/build_b89/Levels_merged_TESTHUB.arc" `
      -Backup  "<repo>/.claude/worktrees/ocean05-hotfix/local/build_b89/DEV_Levels_deployed_prev.arc" `
      -WaitForTQ
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Source,
    [string]$Target = 'C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassicDEV\Resources\Levels.arc',
    [string]$Backup,
    [switch]$NoBackup,
    [switch]$WaitForTQ,
    [int]$WaitMinutes = 240,
    [int]$SettleSeconds = 20
)

$ErrorActionPreference = 'Stop'

function Md5([string]$p) { (Get-FileHash -Path $p -Algorithm MD5).Hash.ToLower() }

if (-not (Test-Path $Source)) { throw "source not found: $Source" }
$targetDir = Split-Path -Parent $Target
if (-not (Test-Path $targetDir)) { throw "target dir not found: $targetDir" }

$srcHash = Md5 $Source
$srcLen = (Get-Item $Source).Length
Write-Output ("SOURCE {0}`n       {1:N0} bytes  md5 {2}" -f $Source, $srcLen, $srcHash)

# --- sibling artifacts that MUST NOT change -------------------------------------------
$resDir = $targetDir
$modDir = Split-Path -Parent $resDir
$siblings = @{}
foreach ($rel in @('Text.arc', 'Quests.arc')) {
    $p = Join-Path $resDir $rel
    if (Test-Path $p) { $siblings[$rel] = Md5 $p }
}
Get-ChildItem (Join-Path $modDir 'Database') -Filter *.arz -ErrorAction SilentlyContinue |
    ForEach-Object { $siblings[$_.Name] = Md5 $_.FullName }
Write-Output "SIBLINGS BEFORE:"
$siblings.GetEnumerator() | Sort-Object Name | ForEach-Object { Write-Output ("  {0,-28} {1}" -f $_.Key, $_.Value) }

# --- wait for the game to close (never kill it) ---------------------------------------
function TargetWritable {
    try {
        $fs = [System.IO.File]::Open($Target, [System.IO.FileMode]::Open,
                                     [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        $fs.Close(); return $true
    } catch { return $false }
}

$deadline = (Get-Date).AddMinutes($WaitMinutes)
while ($true) {
    $tq = Get-Process -Name TQ -ErrorAction SilentlyContinue
    if (-not $tq -and (-not (Test-Path $Target) -or (TargetWritable))) {
        # Let a just-closed game finish releasing handles (and OneDrive settle), then
        # RE-CHECK: if the player relaunched during the settle we go back to waiting
        # rather than racing the live game.
        if ($SettleSeconds -gt 0) { Start-Sleep -Seconds $SettleSeconds }
        if (-not (Get-Process -Name TQ -ErrorAction SilentlyContinue) -and (TargetWritable)) { break }
        Write-Output "  (TQ came back / file re-locked during settle - still waiting)"
    }
    if (-not $WaitForTQ) {
        throw ("TQ.exe is running (or Levels.arc is locked) - refusing to deploy under a live game. " +
               "Quit TQ (and Steam, per the standing restart law) and re-run, or pass -WaitForTQ.")
    }
    if ((Get-Date) -gt $deadline) { throw "timed out after $WaitMinutes min waiting for TQ.exe to exit" }
    Start-Sleep -Seconds 10
}

# --- backup what we are about to replace ----------------------------------------------
if (-not $NoBackup -and (Test-Path $Target)) {
    if (-not $Backup) { $Backup = Join-Path (Split-Path -Parent $Source) 'DEV_Levels_deployed_prev.arc' }
    if (-not (Test-Path $Backup)) {
        Copy-Item -LiteralPath $Target -Destination $Backup -Force
        Write-Output ("BACKUP  {0}  md5 {1}" -f $Backup, (Md5 $Backup))
    } else {
        Write-Output ("BACKUP  already present, kept: {0}" -f $Backup)
    }
}

# --- temp-in-target-dir, verify, then replace -----------------------------------------
$tmp = Join-Path $targetDir ('Levels.arc.deploy-' + [guid]::NewGuid().ToString('N').Substring(0, 8) + '.tmp')
try {
    Copy-Item -LiteralPath $Source -Destination $tmp -Force
    $tmpHash = Md5 $tmp
    if ($tmpHash -ne $srcHash) { throw "staged copy md5 $tmpHash != source $srcHash - aborting" }
    Write-Output "STAGED  temp copy verified against source."
    Move-Item -LiteralPath $tmp -Destination $Target -Force
} finally {
    if (Test-Path $tmp) { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
}

# --- verify ---------------------------------------------------------------------------
$outHash = Md5 $Target
$outLen = (Get-Item $Target).Length
Write-Output ("DEPLOYED {0}`n         {1:N0} bytes  md5 {2}" -f $Target, $outLen, $outHash)
if ($outHash -ne $srcHash) { throw "DEPLOY VERIFY FAILED: deployed $outHash != built $srcHash" }

$changed = @()
Write-Output "SIBLINGS AFTER:"
foreach ($k in ($siblings.Keys | Sort-Object)) {
    $p = Join-Path $resDir $k
    if (-not (Test-Path $p)) { $p = Join-Path (Join-Path $modDir 'Database') $k }
    $h = Md5 $p
    Write-Output ("  {0,-28} {1}{2}" -f $k, $h, $(if ($h -ne $siblings[$k]) { '   <<< CHANGED' } else { '' }))
    if ($h -ne $siblings[$k]) { $changed += $k }
}
if ($changed.Count -gt 0) { throw ("sibling artifact(s) changed during deploy: " + ($changed -join ', ')) }

Write-Output "DEPLOY OK - Levels.arc == built artifact; arz/Text/Quests byte-unchanged."
Write-Output "REMINDER (standing law): fully quit TQ AND Steam, restart Steam, then launch TQ, before testing."
