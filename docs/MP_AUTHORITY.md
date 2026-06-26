# IKappaID Omni Packing — multiplayer authority

**Build:** 42.18 Unstable  
**Reference:** [PZwiki Networking](https://pzwiki.net/wiki/Networking)

## Rules

| Action | Who runs it |
|--------|-------------|
| Pack `OnCreate` / `setActualWeight` on bundles | Server, single-player, or listen-server host (`IKOP_MP.isAuthority()`) |
| Sandbox bundle refresh | Same |
| Recipe `OnTest` (show pack in menu) | All machines (shared `IKOP_RecipeCode.lua`) |
| Context menu sort | Client only (`IKOP_ContextMenu.lua`) |
| Recipe time tuning | Server / SP / host only |

Remote MP clients **never** call `applyStoredWeight` or `onCreateBulkPack`.

## Files

- `lua/shared/IKOP_MP.lua` — `isAuthority()`, `isRemoteClient()`, `isSinglePlayer()`
- `lua/shared/IKOP_RecipeCode.lua` — pack logic + events (was `lua/server/`)

## Testing (MP)

1. Dedicated server or Indifferent Broccoli host with sandbox options set.
2. Player A packs planks x50 — check bundle weight on server and on Player B after trade.
3. Change sandbox weight % on server — existing bundles should refresh within a few seconds.
4. Listen-server host can pack; remote client can pack (server runs OnCreate).

## Known limits

- Item `modData` is not authoritative on clients; weight must come from server `setActualWeight` sync.
- World crates are refreshed on `OnContainerUpdate` and sandbox tick, not full map scan.
