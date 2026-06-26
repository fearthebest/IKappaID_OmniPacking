"""List IKOP loose Base.* types missing from vanilla item scripts (B42 sanity check)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_scripts import MATERIALS

DEFAULT_VANILLA = Path(
    r"B:\SteamLibrary\steamapps\common\ProjectZomboid\media\scripts\generated\items"
)


def load_vanilla_items(items_root: Path) -> set[str]:
    items: set[str] = set()
    if not items_root.is_dir():
        raise SystemExit(f"Vanilla items folder not found: {items_root}")
    for p in items_root.rglob("*.txt"):
        txt = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"^\s*item\s+(\w+)", txt, re.M):
            items.add("Base." + m.group(1))
    return items


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_VANILLA
    vanilla = load_vanilla_items(root)
    missing = sorted(
        m["loose"]
        for m in MATERIALS
        if m["loose"].startswith("Base.") and m["loose"] not in vanilla
    )
    if missing:
        print(f"Missing in vanilla ({root.name}): {len(missing)}")
        for x in missing:
            print(x)
        return 1
    print(f"OK — all {len(MATERIALS)} catalog loose types exist in vanilla.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
