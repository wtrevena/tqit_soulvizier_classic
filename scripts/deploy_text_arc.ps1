# Deploy the original SV 0.98i Text_EN.arc to fix all text tag resolution
# Run this after closing Titan Quest

$svTextArc = "C:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Text_EN.arc"
$deployedArc = "C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic\Resources\Text_EN.arc"

$tqProcs = Get-Process -Name "*TQ*","*Titan*" -ErrorAction SilentlyContinue
if ($tqProcs) {
    Write-Host "WARNING: Titan Quest is still running. Close it first!" -ForegroundColor Red
    $tqProcs | Format-Table Name, Id -AutoSize
    exit 1
}

Copy-Item $svTextArc $deployedArc -Force
$size = (Get-Item $deployedArc).Length
Write-Host "Deployed Text_EN.arc: $size bytes" -ForegroundColor Green

$arcTool = "C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\ArchiveTool.exe"
$listing = & $arcTool $deployedArc -list 2>&1
Write-Host "  Files in arc: $($listing.Count)"
Write-Host "  Done!" -ForegroundColor Green
