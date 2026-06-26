# IKappaID's Omni Packing

Project Zomboid **Build 42** mod: bulk-pack vanilla materials, shelf-stable food, magazines, and skill book sets into stacks of **5, 10, 25, 50, or 100**.

| | |
|---|---|
| **Mod ID** | `IKappaIDOmniPacking` |
| **Target build** | B42.18+ (tested on 42.19) |
| **Version** | 0.0.10 |

## Features

- ~970 packable loose `Base.*` types (materials + food) across five stack tiers
- Vanilla **24 skill** slipcases (Lv 1–5 per set)
- Optional addon: **IKappaIDOmniPacking_SkillBookExpansion** ([Skill Book Expansion](https://steamcommunity.com/sharedfiles/filedetails/?id=3557111695))
- Sandbox weight reduction, tier toggles, pack/unpack timing
- MP: server sets bundle weight; clients use synced items ([docs/MP_AUTHORITY.md](docs/MP_AUTHORITY.md))

## Install (players)

Copy `Contents/mods/IKappaIDOmniPacking` into your Zomboid mods folder, or subscribe on Steam Workshop when published.

## Development

### Layout

```
Contents/mods/IKappaIDOmniPacking/42.18/     # main mod (Lua, scripts, textures)
Contents/mods/IKappaIDOmniPacking_SkillBookExpansion/42.18/  # optional addon
scripts/          # Python generators and catalog sources
docs/             # scope, testing, MP notes
art/icons/        # icon previews (not loaded by the game)
```

### Regenerate item/recipe scripts

```powershell
python scripts/generate_scripts.py
python scripts/generate_scripts_sbe.py   # Skill Book Expansion addon
```

### Validate catalog against vanilla items

```powershell
python scripts/validate_catalog.py "C:\Path\To\ProjectZomboid\media\scripts\generated\items"
```

### Sync to Steam Workshop upload tree

```powershell
powershell -File scripts/sync_to_workshop.ps1
```

## Docs

- [SCOPE.md](docs/SCOPE.md) — pack rules and material list overview
- [TESTING.md](docs/TESTING.md) — playtest checklist
- [MP_AUTHORITY.md](docs/MP_AUTHORITY.md) — multiplayer weight authority
- [FOR-SBE-ADDON.md](docs/FOR-SBE-ADDON.md) — Skill Book Expansion addon

## License

All rights reserved unless a `LICENSE` file is added later.
