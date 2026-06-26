"""Scan pzfans categories for packable vanilla Base.* not yet in IKOP."""
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_scripts import MATERIALS
from fetch_item_meta import fetch_meta

PACKED = {m["loose"].replace("Base.", "") for m in MATERIALS}

CATEGORIES = [
    "Material",
    "Tool",
    "Household",
    "Electronics",
    "Junk",
    "Cooking",
    "Medical",
    "Camping",
    "Literature",
    "AnimalPart",
    "Memento",
    "WaterContainer",
]

LINE_RE = re.compile(r"Base\.(\w+)\s+\S*\s*(\w+)")

SKIP_SUFFIX = re.compile(
    r"(Box|Carton|Bundle|Stacks?[234]|Bulk|Case|Crate|Seedling|"
    r"Full$|_Full$|_Wet$|_Fur$|_Fur_Tan$|_Fur_Tan_Wet$|"
    r"Blade$|Blade_Broken|_Broken|Head$|Mold$|MoldUnfired$|Unfired$|"
    r"Carton$|PopCommon$|Crafted$|DirtyBundle$|StripsBundle$|BarbedWireStack$|"
    r"ConcreteFull$|PlasterFull$|ClayCement$|WallpaperPaste$|GlazeBowl$|"
    r"Crucible_Iron$|Crucible_Steel$|FabricRoll_|Leather_|CowLeather_|"
    r"PigLeather_|PigletLeather_|CalfLeather_|LambLeather_|DeerLeather_|"
    r"Hide$|CowHide$|DeerHide$|DappleDeerHide$|TestCan|Recipe$|Open$|"
    r"Rotten$|Burnt$|Frozen$|Unbaked$|Batter$|Prep$|Dough$|Empty$|"
    r"Petrol$|Slices$|Sandwich$|Burger$|Pizza$|Juice$|Pop$|Wine$|Beer$|"
    r"Whiskey$|Vodka$|Water$|Cigarette$|Melted$|Skinned$|Dead$|"
    r"Bowl$|Soup$|Stew$|Pot$|Tray$|Pan$|Recipe$|Craft$)",
    re.I,
)

SKIP_NAME = re.compile(
    r"(Box of |Carton of |Bundle|Stack -|Stacks?[234]|Bulk|Bucket of |Bag of |"
    r"Carved Bucket|Bowl of |\(Unfired\)|\(Furred\)|\(Unprocessed\)|\(Wet\)|"
    r"Half \(|Quarter \(|with Iron|with Steel|Can of |TestCan|Dead )",
    re.I,
)

PACKABLE_TYPES = {
    "base:normal",
    "base:literature",
    "base:drainable",
}

SKIP_ITEM_TYPES = re.compile(
    r"weapon|clothing|container|key|map|moveable",
    re.I,
)


def fetch_category(category: str) -> list[tuple[str, str]]:
    items = []
    for page in range(1, 20):
        url = f"https://pzfans.com/en/wiki/items/category/{category}/?page={page}"
        req = urllib.request.Request(url, headers={"User-Agent": "IKOP-discover-all/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="replace")
        except OSError:
            break
        count = 0
        for line in html.splitlines():
            m = LINE_RE.search(line)
            if m:
                items.append((m.group(1), m.group(2)))
                count += 1
        if count == 0:
            break
    return items


def short_ok(short: str) -> bool:
    if short in PACKED:
        return False
    if SKIP_SUFFIX.search(short):
        return False
    if SKIP_NAME.search(short):
        return False
    return True


def meta_ok(short: str, meta: dict, wiki_cat: str) -> bool:
    if meta.get("error"):
        return False
    item_type = (meta.get("item_type") or "").lower()
    if not item_type:
        return wiki_cat in ("Material", "Tool", "Junk", "Household", "Electronics", "Medical", "Camping")
    if item_type == "base:food":
        return False
    if SKIP_ITEM_TYPES.search(item_type):
        return False
    if item_type not in PACKABLE_TYPES:
        return False
    tags = meta.get("tags") or ""
    if "base:heavyitem" in tags and short not in ("PropaneTank",):
        # heavy haul is OK for IKOP — keep
        pass
    if "base:weapon" in tags or "base:gun" in tags:
        return False
    return True


def main():
    seen: set[str] = set()
    candidates: list[tuple[str, str, dict]] = []

    for cat in CATEGORIES:
        rows = fetch_category(cat)
        print(f"{cat}: {len(rows)} wiki rows", file=sys.stderr)
        for short, _ in rows:
            if short in seen or not short_ok(short):
                continue
            seen.add(short)
            candidates.append((short, cat, {}))

    print(f"unique candidates after suffix filter: {len(candidates)}", file=sys.stderr)

    packable = []
    for i, (short, cat, _) in enumerate(candidates):
        meta = fetch_meta(short)
        if meta_ok(short, meta, cat):
            packable.append((short, cat, meta))
        if (i + 1) % 20 == 0:
            print(f"  meta {i + 1}/{len(candidates)}", file=sys.stderr)
        time.sleep(0.08)

    print(f"packable gaps: {len(packable)}")
    for short, cat, meta in sorted(packable, key=lambda x: (x[1], x[0])):
        it = meta.get("item_type", "?")
        dc = meta.get("category", cat)
        print(f"{short:40} {dc:15} {it}")


if __name__ == "__main__":
    main()
