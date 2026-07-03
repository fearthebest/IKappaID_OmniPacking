# Sync dev repo -> Zomboid Workshop upload tree.
# Usage: powershell -File scripts\sync_to_workshop.ps1

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path $PSScriptRoot -Parent
$workshopRoot = Join-Path $env:USERPROFILE "Zomboid\Workshop\IKappaID Omni Packing"
$dstMods = Join-Path $workshopRoot "Contents\mods"

New-Item -ItemType Directory -Force -Path $dstMods | Out-Null

$packs = @(
    @{ Name = "IKappaIDOmniPacking"; Src = Join-Path $repoRoot "Contents\mods\IKappaIDOmniPacking" },
    @{ Name = "IKappaIDOmniPacking_SkillBookExpansion"; Src = Join-Path $repoRoot "Contents\mods\IKappaIDOmniPacking_SkillBookExpansion" }
)

foreach ($p in $packs) {
    if (-not (Test-Path $p.Src)) {
        throw "Source not found: $($p.Src)"
    }
    $target = Join-Path $dstMods $p.Name
    if (Test-Path $target) {
        Remove-Item -Path $target -Recurse -Force
    }
    Copy-Item -Path $p.Src -Destination $target -Recurse -Force
    Write-Host "Synced $($p.Name) -> $target"
}

$workshopTxt = Join-Path $repoRoot "workshop.txt"
if (Test-Path $workshopTxt) {
    Copy-Item -Path $workshopTxt -Destination (Join-Path $workshopRoot "workshop.txt") -Force
    Write-Host "Copied workshop.txt"
}

Write-Host "Done. Workshop pack: $workshopRoot"
