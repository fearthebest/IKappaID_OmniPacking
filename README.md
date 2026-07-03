# IKappaID Omni Packing

Bulk-pack vanilla materials, shelf-stable food, magazines, and skill book sets into stacks of 5, 10, 25, 50, or 100 for Project Zomboid Build 42.

| | |
|---|---|
| **Mod ID** | `IKappaIDOmniPacking` |
| **Version** | 0.0.10 |
| **Target build** | B42.18+ (tested on 42.19) |
| **Author** | IKappaID |

## Overview

Omni Packing adds tiered bundle items for loose `Base.*` materials and food, vanilla 24-skill slipcases, and optional Skill Book Expansion integration. Sandbox options control weight reduction, enabled tiers, and pack/unpack timing.

## Features

- Approximately 970 packable loose `Base.*` types across five stack tiers
- Vanilla 24-skill slipcases (levels 1–5 per set)
- Optional addon: **IKappaIDOmniPacking_SkillBookExpansion** ([Skill Book Expansion](https://steamcommunity.com/sharedfiles/filedetails/?id=3557111695))
- Multiplayer: server sets bundle weight; clients use synced items ([docs/MP_AUTHORITY.md](docs/MP_AUTHORITY.md))
- Structured logging: `IKOP_Log.lua` writes to `console.txt` and `Zomboid/Lua/IKappaIDOmniPacking/logs/{client|server}/*.log` (toggle in `IKOP_Config.lua`)

## Repository structure

```text
.
├── README.md
├── workshop.txt
├── Contents/
│   └── mods/
│       ├── IKappaIDOmniPacking/42.18/              # Main mod (Core, Authority, Log, RecipeCode, …)
│       └── IKappaIDOmniPacking_SkillBookExpansion/42.18/  # Optional addon
├── scripts/           # Python generators and catalog sources
├── docs/              # Scope, testing, and MP notes
└── art/icons/         # Icon previews (not loaded by the game)
```

## Installation (players)

Copy `Contents/mods/IKappaIDOmniPacking` into your Zomboid mods folder, or subscribe on Steam Workshop when published. Enable the Skill Book Expansion addon only if that dependency mod is present.

## Development

**Regenerate item and recipe scripts:**

```powershell
python scripts/generate_scripts.py
python scripts/generate_scripts_sbe.py
```

**Validate catalog against vanilla items:**

```powershell
python scripts/validate_catalog.py "C:\Path\To\ProjectZomboid\media\scripts\generated\items"
```

**Sync to Steam Workshop upload tree:**

```powershell
powershell -File scripts/sync_to_workshop.ps1
```

## Documentation

| Document | Description |
|----------|-------------|
| [SCOPE.md](docs/SCOPE.md) | Pack rules and material list overview |
| [TESTING.md](docs/TESTING.md) | Playtest checklist |
| [MP_AUTHORITY.md](docs/MP_AUTHORITY.md) | Multiplayer weight authority |
| [FOR-SBE-ADDON.md](docs/FOR-SBE-ADDON.md) | Skill Book Expansion addon |

## License

All rights reserved unless a `LICENSE` file is added later.

## Links

- **Support:** https://ko-fi.com/ikappaid

Community mod — not affiliated with or endorsed by The Indie Stone.
