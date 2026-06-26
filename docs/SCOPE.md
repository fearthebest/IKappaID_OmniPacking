# IKappaID's Omni Packing — scope (B42.18)

## Stack sizes

Each material can be packed at **5, 10, 25, 50, or 100** (separate craft recipes per size).

Recipe IDs use zero-padded suffixes (`_005`, `_010`, … `_100`) for stable naming. **Item right-click submenu order** is fixed in `lua/client/IKOP_ContextMenu.lua` (vanilla `addNewCraftingDynamicalContextMenu` does not sort by name).

**Bundle weight after save/load:** `setActualWeight` plus `setCustomWeight(true)` on pack (vanilla fish pattern); `IKOP_packedWeight` in modData is re-applied on `OnGameStart` / `OnCreatePlayer` (server / SP only).

## Packable materials (loose `Base.*` only)

| Material | Loose item | Notes |
|----------|------------|--------|
| Scrap metal | `Base.ScrapMetal` | MetalValue scaled |
| Planks | `Base.Plank` | |
| Sheet metal | `Base.SheetMetal` | |
| Small sheet metal | `Base.SmallSheetMetal` | |
| Metal bars | `Base.MetalBar` | |
| Metal pipes | `Base.MetalPipe` | |
| Logs | `Base.Log` | Beyond vanilla 2/3 log stacks |
| Charcoal | `Base.Charcoal` | |
| Iron ingots | `Base.IronIngot` | |
| Steel ingots | `Base.SteelIngot` | |
| Glass panels | `Base.GlassPanel` | |
| Limestone | `Base.Limestone` | |
| Clay | `Base.Clay` | |
| Magazines | `Base.Magazine` | Literature bulk; unpack creates fresh items |
| Newspapers | `Base.Newspaper` | Literature bulk |

## Skill books (Lv 1–5 per skill)

One **complete skill set** = volumes `…1` … `…5` → `IKOP.Book…SkillBundle` slipcase (sandbox weight reduction, `ikop:bulk`).

| Source | Mod |
|--------|-----|
| **Vanilla `Base.*`** | **IKappaIDOmniPacking** (no required mods) |
| **[Skill Book Expansion](https://steamcommunity.com/sharedfiles/filedetails/?id=3557111695)** | Optional addon **IKappaIDOmniPacking_SkillBookExpansion** (`require=IKappaIDOmniPacking;SkillBookExpansionB42`) |

Main mod has **zero** `require=` entries. SBE slipcases live only in the optional addon.

- **Not** 5/10/25/50/100 tiers for books (always exactly five volumes per craft).
- Rejects vanilla / SBE `Book*Set` slipcases and IKOP bundles as inputs (`canPackLooseSkillBook`).
- Vanilla `PackSetOfBooks` still exists (fixed 4.0 weight); IKOP recipes are the lighter option.

**Not in scope:** nails/screws/ammo boxes, canned food cases, rags/rope/wire ×12, cigarettes, drainables, weapons/ammo.

Regenerate scripts: `Things for-from Cursor\IKappaIDOmniPacking\scripts\generate_scripts.py`

## Repack rule

**Packed IKOP bundles cannot be packed again.**

- All bundle items use tag `ikop:bulk` and FullType `IKOP.*`
- Pack recipes only accept **loose** `Base.*` inputs
- `OnTest = IKOP_RecipeCode.canPackLooseStack` rejects any `IKOP` / `ikop:bulk` item

## Sandbox

- **WeightReductionPercent** (0–90, default 17): `bundle weight = sum(loose packed) × (1 − %/100)`

## MP

- Weight set in `OnCreate` on server / singleplayer only.
