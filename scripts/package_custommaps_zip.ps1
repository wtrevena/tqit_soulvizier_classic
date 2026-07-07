#Requires -Version 5.1
<#
.SYNOPSIS
    Build a shareable CustomMaps zip of the SoulvizierClassic mod so a friend can
    install it and play multiplayer co-op (see docs/SHARE_AND_PLAY.md).
.DESCRIPTION
    Stages a CLEAN copy of work\SoulvizierClassic\ (the exact CustomMaps folder
    structure: Database\, Resources\, Maps\) into dist\SoulvizierClassic\,
    dropping dev cruft (*.md, *.txt reports, *.roundtrip / *.working_backup
    backups) that must not ship and that would break byte-identity between two
    players if only one had them. Then zips it to dist\SoulvizierClassic_CustomMaps.zip.

    The zip's top-level folder is 'SoulvizierClassic', so the friend extracts it
    straight into  My Games\Titan Quest - Immortal Throne\CustomMaps\.

    NOTE: this is a LOCAL artifact only. It does NOT upload anywhere.
.PARAMETER Source
    Which built tree to package. 'work' (default) = repo work\SoulvizierClassic\.
    'deployed' = the live CustomMaps\SoulvizierClassic\ folder (config WIN_CUSTOMMAPS).
#>
[CmdletBinding()]
param(
    [ValidateSet('work','deployed')]
    [string]$Source = 'work'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\_common.ps1"

$modName = 'SoulvizierClassic'
if ($Source -eq 'deployed') {
    $srcMod = Join-Path (Require-Config 'WIN_CUSTOMMAPS') $modName
} else {
    $srcMod = Join-Path $RepoRoot "work\$modName"
}
$distDir   = Join-Path $RepoRoot 'dist'
$stageMod  = Join-Path $distDir $modName
$zipPath   = Join-Path $distDir "${modName}_CustomMaps.zip"

Write-Host '=== Package CustomMaps zip (shareable for MP co-op) ===' -ForegroundColor Cyan
Write-Host "Source: $srcMod"

$arz = Join-Path $srcMod "Database\$modName.arz"
if (-not (Test-Path $arz)) {
    Write-Host "ERROR: $modName.arz not found under $srcMod. Build/deploy first." -ForegroundColor Red
    exit 1
}

# Clean previous staging + zip
if (Test-Path $stageMod) { Remove-Item $stageMod -Recurse -Force }
if (Test-Path $zipPath)  { Remove-Item $zipPath  -Force }
New-Item -ItemType Directory -Path $stageMod -Force | Out-Null

# Cruft that must NOT ship (dev notes / backups / round-trip artifacts).
$excludeExt  = @('.md')
$excludeName = @('Quests.arc.roundtrip','Quests.arc.working_backup','soul_audit_full.md',
                 'soul_investigation.md','uber_soul_tags.txt','uber_souls_report.md')
# Keep mod_authored_tags.txt? It is a build manifest, not needed at runtime -> drop.
$excludeName += 'mod_authored_tags.txt'

Write-Host 'Staging clean copy (dropping dev cruft)...' -ForegroundColor Yellow
$allFiles = @(Get-ChildItem $srcMod -Recurse -File)
$copied = 0; $skipped = 0
foreach ($f in $allFiles) {
    $rel = $f.FullName.Substring($srcMod.Length).TrimStart('\')
    if (($excludeExt -contains $f.Extension.ToLower()) -or ($excludeName -contains $f.Name)) {
        $skipped++
        continue
    }
    $dest = Join-Path $stageMod $rel
    $destDir = Split-Path $dest -Parent
    if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
    Copy-Item $f.FullName -Destination $dest -Force
    $copied++
}
Write-Host "  staged $copied file(s), skipped $skipped cruft file(s)" -ForegroundColor Green

# Report exact staged contents
Write-Host ''
Write-Host 'Staged contents:' -ForegroundColor Cyan
Get-ChildItem $stageMod -Recurse -File |
    Group-Object { $_.Directory.Name } |
    ForEach-Object {
        $mb = [math]::Round((($_.Group | Measure-Object Length -Sum).Sum) / 1MB, 1)
        Write-Host ("  {0,-12} {1,3} file(s)  {2,8} MB" -f $_.Name, $_.Count, $mb)
    }
$stageMB = [math]::Round((Get-ChildItem $stageMod -Recurse -File | Measure-Object Length -Sum).Sum / 1MB, 1)
Write-Host ("  TOTAL staged: $stageMB MB") -ForegroundColor Green

# Zip it (top-level folder = SoulvizierClassic)
Write-Host ''
Write-Host 'Compressing (this takes a few minutes; .arc files are already compressed)...' -ForegroundColor Yellow
Compress-Archive -Path $stageMod -DestinationPath $zipPath -CompressionLevel Optimal -Force

$zipMB = [math]::Round((Get-Item $zipPath).Length / 1MB, 1)
$sha = (Get-FileHash $zipPath -Algorithm SHA256).Hash
$arzSha = (Get-FileHash $arz -Algorithm SHA256).Hash
Write-Host ''
Write-Host "Zip ready: $zipPath ($zipMB MB)" -ForegroundColor Green
Write-Host "Zip SHA-256: $sha" -ForegroundColor Green
Write-Host "Embedded SoulvizierClassic.arz SHA-256: $arzSha" -ForegroundColor Green
Write-Host ''
Write-Host 'Friend installs by extracting so the folder lands at:' -ForegroundColor Cyan
Write-Host '  Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic\' -ForegroundColor Cyan
