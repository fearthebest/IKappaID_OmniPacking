# Milestone 0.0.2 — Single-player release candidate

**Date:** 2026-05-28  
**Target:** Build 42.18 Unstable  
**Next:** Multiplayer support (server authority for bundle weight, client display only).

## Shipped in 0.0.2

- Large material catalog (~234 stack types × tiers 5/10/25/50/100) plus vanilla skill-book slipcases.
- Expanded sandbox (weight % per category, heavy-item bonus, pack/unpack time, tier toggles, refresh on change, menu sort).
- Sandbox UI: readable labels via `translate/EN/Sandbox.json` (B42 JSON format).
- Server-side bundle weight and sandbox refresh (`IKOP_RecipeCode.lua`).
- Optional SBE addon pack (separate mod id; not a dependency).

## Test before MP work

- Single player: pack/unpack, change sandbox %, confirm existing bundles refresh.
- Confirm debug log shows: `overrides .../sandbox.json` for IKappaIDOmniPacking.

## MP planning notes

- Follow [Networking](https://pzwiki.net/wiki/Networking): server mutates item weight; clients do not double-apply.
- Reuse IKFRVP-style split: shared readers, server `OnCreate`/refresh, client UI only where needed.
