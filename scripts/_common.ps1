<#
.SYNOPSIS
    Shared config loader for all project scripts.
.DESCRIPTION
    Reads local/config.env and exposes values as $Config hashtable.
    Source this at the top of every script: . "$PSScriptRoot\_common.ps1"
#>

$script:RepoRoot = Split-Path -Parent $PSScriptRoot
$script:ConfigFile = Join-Path $RepoRoot 'local\config.env'

if (-not (Test-Path $ConfigFile)) {
    Write-Host 'ERROR: local/config.env not found. Run scripts/doctor.ps1 first.' -ForegroundColor Red
    exit 1
}

$script:Config = @{}
Get-Content $ConfigFile | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
    $parts = $_ -split '=', 2
    if ($parts.Count -eq 2) {
        $Config[$parts[0].Trim()] = $parts[1].Trim()
    }
}

function Require-Config($key) {
    if (-not $Config[$key]) {
        Write-Host "ERROR: Required config key '$key' is empty. Re-run doctor.ps1." -ForegroundColor Red
        exit 1
    }
    return $Config[$key]
}
