"""Build wave2_materials.py from discover_packable_gaps output (_packable_gaps.txt)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_scripts import MATERIALS
from materials_catalog import _mat

PACKED = {m["loose"].replace("Base.", "") for m in MATERIALS}

GAP_LINE = re.compile(
    r"^([A-Za-z0-9_]+)\s+(\w+)\s+(base:\w+)\s*$"
)

EXCLUDE_SHORT = {
    "Animal_Item_Dummy",
    "TestMug",
    "DebugFluid",
    "BucketWaterDebug",
    "BeerCanPack",
    "BeerPack",
    "PotForged",
}

EXCLUDE_RE = [
    re.compile(r"^Test", re.I),
    re.compile(r"Debug", re.I),
    re.compile(r"_Packed$", re.I),
    re.compile(r"_Wet$", re.I),
    re.compile(r"_Prop$", re.I),
]

EXCLUDE_WIKI = {"WaterContainer"}


def camel_label(short: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", short)
    return s.replace("_", " ").lower()


def key_from_short(short: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", short)
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).lower().strip("_")


def should_skip(short: str, wiki_cat: str) -> bool:
    if short in PACKED or short in EXCLUDE_SHORT:
        return True
    if wiki_cat in EXCLUDE_WIKI:
        return True
    return any(p.search(short) for p in EXCLUDE_RE)


def parse_gaps(path: Path) -> list[tuple[str, str, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = GAP_LINE.match(line.strip())
        if m:
            rows.append((m.group(1), m.group(2), m.group(3)))
    return rows


def build_entry(short: str, wiki_cat: str, item_type: str):
    display = wiki_cat
    if item_type == "base:literature":
        display = "Literature"
    survival = False
    tags = None
    if short in ("Zipties",):
        survival = True
    return _mat(
        f"w2_{key_from_short(short)}",
        f"{short}Bulk",
        f"Base.{short}",
        camel_label(short),
        short,
        wsm=short,
        tags=tags,
        display_category=display,
        item_type=item_type,
        survival_gear=survival,
    )


def main():
    gap_file = Path(__file__).parent / "_packable_gaps.txt"
    if not gap_file.is_file():
        print("Run discover_packable_gaps.py first.", file=sys.stderr)
        sys.exit(1)

    entries = []
    skipped = 0
    for short, wiki_cat, item_type in parse_gaps(gap_file):
        if should_skip(short, wiki_cat):
            skipped += 1
            continue
        entries.append(build_entry(short, wiki_cat, item_type))

    out = Path(__file__).parent / "wave2_materials.py"
    lines = [
        '"""Wave 2 packables from multi-category pzfans scan. Regenerate via generate_wave2_catalog.py."""',
        "from materials_catalog import _mat",
        "",
        "WAVE2_MATERIALS = [",
    ]
    for e in entries:
        parts = [
            f'    _mat("{e["key"]}", "{e["bulk_prefix"]}", "{e["loose"]}", "{e["label"]}", "{e["icon"]}"',
        ]
        opts = []
        if e.get("wsm"):
            opts.append(f'wsm="{e["wsm"]}"')
        if e.get("display_category") != "Material":
            opts.append(f'display_category="{e["display_category"]}"')
        if e.get("item_type") != "base:normal":
            opts.append(f'item_type="{e["item_type"]}"')
        if e.get("survival_gear"):
            opts.append("survival_gear=True")
        if opts:
            parts[0] += ", " + ", ".join(opts)
        parts[0] += "),"
        lines.append(parts[0])
    lines.append("]")
    lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(entries)} entries to {out} (skipped {skipped})")


if __name__ == "__main__":
    main()
