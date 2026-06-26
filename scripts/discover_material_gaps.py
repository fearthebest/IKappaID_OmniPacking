"""Compare pzfans Material category vs IKOP catalog; print packable gaps."""
import re
import sys
import urllib.request

sys.path.insert(0, __file__.rsplit("\\scripts\\", 1)[0] + "\\scripts")
from generate_scripts import MATERIALS

PACKED = {m["loose"] for m in MATERIALS}

SKIP_NAME = re.compile(
    r"(Box of |Carton of |Bundle|Stack -|Stacks?[234]|Bulk|Bucket of |Bag of |"
    r"Carved Bucket|Bowl of |\(Unfired\)|\(Furred\)|\(Unprocessed\)|\(Wet\)|"
    r"Half \(|Quarter \(|with Iron|with Steel|Can of |TestCan)",
    re.I,
)
SKIP_SUFFIX = re.compile(
    r"(Box|Carton|Bundle|Stacks?[234]|Bulk|Case|Crate|Seedling|"
    r"Full$|_Full$|_Wet$|_Fur$|_Fur_Tan$|_Fur_Tan_Wet$|"
    r"Blade$|Blade_Broken|_Broken|Head$|Mold$|MoldUnfired$|Unfired$|"
    r"Carton$|PopCommon$|Crafted$|DirtyBundle$|StripsBundle$|BarbedWireStack$|"
    r"ConcreteFull$|PlasterFull$|ClayCement$|WallpaperPaste$|GlazeBowl$|"
    r"Crucible_Iron$|Crucible_Steel$|FabricRoll_|Leather_|CowLeather_|"
    r"PigLeather_|PigletLeather_|CalfLeather_|LambLeather_|DeerLeather_|"
    r"Hide$|CowHide$|DeerHide$|DappleDeerHide$|TestCan)",
    re.I,
)
# Keep loose singles; skip containers, pre-packed vanilla stacks, hides (breed variants), weapon parts.

LINE_RE = re.compile(r"Base\.(\w+)\s+\S*\s*Material\s*")


def fetch_page(page: int) -> str:
    url = f"https://pzfans.com/en/wiki/items/category/Material/?page={page}"
    req = urllib.request.Request(url, headers={"User-Agent": "IKOP-discover/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_materials(html: str):
    out = []
    for line in html.splitlines():
        m = LINE_RE.search(line)
        if m:
            short = m.group(1)
            out.append((short, f"Base.{short}"))
    return out


def main():
    all_items = []
    for page in range(1, 8):
        try:
            html = fetch_page(page)
            items = parse_materials(html)
            print(f"page {page}: {len(items)} items", file=sys.stderr)
            all_items.extend(items)
        except Exception as exc:
            print(f"page {page} failed: {exc}", file=sys.stderr)

    seen = set()
    gaps = []
    for short, ft in all_items:
        if ft in seen:
            continue
        seen.add(ft)
        if ft in PACKED:
            continue
        name = short  # display label generated later
        if SKIP_NAME.search(name):
            continue
        if SKIP_SUFFIX.search(short):
            continue
        gaps.append((name, ft, short))

    print(f"total wiki materials: {len(seen)}")
    print(f"already packed: {len(PACKED)}")
    print(f"gaps: {len(gaps)}")
    print()
    for name, ft, short in sorted(gaps, key=lambda x: x[0].lower()):
        print(f"{ft:45} # {name}")


if __name__ == "__main__":
    main()
