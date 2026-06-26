# Sync repo -> Zomboid Workshop upload tree (edit here, then upload from Workshop folder).
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path $PSScriptRoot -Parent
$dst = Join-Path $env:USERPROFILE "Zomboid\Workshop\IKappaIDOmniPacking\Contents\mods"
if (-not (Test-Path (Split-Path $dst -Parent))) { throw "Workshop parent not found: $dst" }

$packs = @(
    @{ Name = "IKappaIDOmniPacking"; Src = Join-Path $repoRoot "Contents\mods\IKappaIDOmniPacking" },
    @{ Name = "IKappaIDOmniPacking_SkillBookExpansion"; Src = Join-Path $repoRoot "Contents\mods\IKappaIDOmniPacking_SkillBookExpansion" }
)

foreach ($p in $packs) {
    if (-not (Test-Path $p.Src)) { throw "Source not found: $($p.Src)" }
    $target = Join-Path $dst $p.Name
    if (Test-Path $target) { Remove-Item -Path $target -Recurse -Force }
    Copy-Item -Path $p.Src -Destination $target -Recurse -Force
    Write-Host "Synced $($p.Name) -> $target"
}
