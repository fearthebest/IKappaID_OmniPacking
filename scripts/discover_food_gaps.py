"""Find packable vanilla food (non-drainable base:food) not yet in IKOP."""
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_scripts import MATERIALS
from fetch_item_meta import fetch_meta

PACKED = {m["loose"] for m in MATERIALS}
LINE_RE = re.compile(r"Base\.(\w+)\s+\S*\s*Food")

SKIP_SUFFIX = re.compile(
    r"(Box|Carton|Pack|Bundle|Bowl|Soup|Stew|Pot|Tray|Rotten|Burnt|Frozen|"
    r"Unbaked|Batter|Prep|Dough|Open|Closed|Empty|Petrol|Rare|Slices|Sandwich|"
    r"Burger|Pizza|Juice|Pop|Wine|Beer|Whiskey|Vodka|Water|Cigarette)$",
    re.I,
)


def fetch_food_shorts() -> list[str]:
    items = []
    for page in range(1, 12):
        url = f"https://pzfans.com/en/wiki/items/category/Food/?page={page}"
        req = urllib.request.Request(url, headers={"User-Agent": "IKOP-food/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="replace")
        except OSError:
            break
        count = 0
        for line in html.splitlines():
            m = LINE_RE.search(line)
            if m:
                items.append(m.group(1))
                count += 1
        if count == 0:
            break
    return list(dict.fromkeys(items))


def is_packable_food(short: str, meta: dict) -> bool:
    if meta.get("error"):
        return False
    item_type = meta.get("item_type", "")
    if item_type and item_type != "base:food":
        return False
    if meta.get("use_delta"):
        return False
    return True


def main():
    shorts = [s for s in fetch_food_shorts() if f"Base.{s}" not in PACKED and not SKIP_SUFFIX.search(s)]
    print(f"candidate shorts (suffix filter): {len(shorts)}", file=sys.stderr)

    gaps = []
    for i, short in enumerate(shorts):
        meta = fetch_meta(short)
        if not is_packable_food(short, meta):
            continue
        gaps.append(short)
        if (i + 1) % 25 == 0:
            print(f"  scanned {i + 1}/{len(shorts)}", file=sys.stderr)
        time.sleep(0.1)

    print(f"packable food gaps: {len(gaps)}")
    for short in gaps:
        print(short)


if __name__ == "__main__":
    main()
