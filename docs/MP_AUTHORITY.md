# IKappaID Omni Packing — multiplayer authority

**Build:** 42.18 Unstable  
**Reference:** [PZwiki Networking](https://pzwiki.net/wiki/Networking)

## Rules

| Action | Who runs it |
|--------|-------------|
| Bundle weight (`setCustomWeight`, `setActualWeight`, modData stamp) | Server JVM or single-player only (`IKOP_Authority.guardServerMutate()`) |
| Sandbox bundle refresh | Same |
| Recipe `OnTest` (show pack in menu) | All machines (shared `IKOP_RecipeCode.lua`) |
| Context menu sort | Client only (`IKOP_ContextMenu.lua`) |
| Recipe time tuning | Server / SP / host only |

Remote MP clients **never** run weight Lua. No client mirrors, tooltip hooks, or weight commands.

## Weight pipeline (IKST-style)

1. **Boot** — `IKOP_WeightTable.lua` builds loose/stack per `IKOP.*` bulk type from unstack recipes.
2. **Commit** — `lua/server/IKOP_WeightAuthority.lua` → `commitWeight(player, item)` stamps modData, sets weight, calls vanilla sync (`syncItemFields`, `syncItemModData`, `sendItemStats`).
3. **Acquire** — `lua/server/IKOP_WeightHooks.lua` commits after `sendAddItemToContainer` (IKST `giveItem`), SP `AddItem`, loot, ground drops.
4. **Craft** — `OnCreate` → `commitWeightFromCraft` using consumed item weights.
5. **Display** — engine sync only; client is read-only slave to server stats.

## Files

- `lua/shared/IKOP_WeightTable.lua` — boot-time lookup table (read-only)
- `lua/server/IKOP_WeightAuthority.lua` — sole weight writer
- `lua/server/IKOP_WeightHooks.lua` — item-acquire hooks
- `lua/shared/IKOP_RecipeCode.lua` — OnTest + thin OnCreate delegate
- `lua/shared/IKOP_MP.lua` — `isAuthority()`, `isRemoteClient()`

## Testing (MP)

1. Dedicated server or Indifferent Broccoli host with sandbox options set.
2. IKST spawn `IKOP.PlankBulk100` — server log `weight|commit|packed=150` (at 50% reduction); tooltip shows ~150.
3. Player A packs planks x50 — check bundle weight on server and on Player B after trade.
4. Change sandbox weight % on server — existing bundles refresh on next sandbox tick.
5. Listen-server host can pack; remote client sees synced weight only (no IKOP client weight code).

## Known limits

- Item `modData` is not auto-synced to clients in MP; weight must come from server `setActualWeight` + `sendItemStats`.
- If server log shows correct weight but tooltip still shows 1.0, debug server sync order (commit after `sendAddItemToContainer`) — do not add client weight patches.
