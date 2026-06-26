# IKappaID's Omni Packing — testing (B42.18)

## Tiered packing

For each material, test **5, 10, 25, 50, 100**:

1. Spawn that many loose items.
2. Packing tab → correct “Bundle … (×N)” recipe.
3. One `IKOP.*BulkN` item; weight reflects sandbox reduction.
4. Double-click or unbundle recipe → N loose items.

## No repacking

1. Pack 10 planks → `IKOP.PlankBulk10`.
2. Confirm **no** pack recipe accepts the bulk item (only loose planks work).
3. Try 10 bulk planks in inventory — pack recipes for planks should stay unavailable / fail OnTest.

## Sandbox

1. Set weight reduction to **0%** → bundle weight equals sum of loose items.
2. Set to **50%** → bundle is half of loose total.

## MP (0.0.3+)

Test on **dedicated server** or **Indifferent Broccoli** (per workspace rules).

1. Server sandbox: set material reduction to **50%**.
2. Player packs 50 planks → one bundle; weight ~half of loose total on **both** packer and another player after trade.
3. Change reduction to **25%** on server → wait ~2s → bundle weight updates in inventory.
4. **Listen-server host** can pack (was broken when authority used `isClient()` only).
5. Remote client: pack menu works; bundle weight must match server (no local re-roll from sandbox).

See `docs/MP_AUTHORITY.md`.
