"""Generate expansion_materials.py entries from gap list + extras (pzfans metadata)."""
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from materials_catalog import _mat
from fetch_item_meta import fetch_meta

EXTRA_SHORTS = [
  # Junk — small loose items, no vanilla 5–100 bulk
  "Cork", "BrokenGlass", "Brochure", "BusinessCard", "ChessBlack", "ChessWhite",
  "CameraFilm", "Comb", "RubberBand", "Matches", "Pencil", "Pen",
  "TongueDepressor", "FishingHook", "FishingLine", "CottonBalls",
  # Electronics
  "Battery",
  # Animal parts (small)
  "ChickenFeather",
  # Tool — craft parts / small tools haulable in bulk (not equipped main tools)
  "Needle_Forged", "Needle_Bone", "Needle_Brass", "KnittingNeedles", "KnittingNeedles_Bone",
  "Bellows", "CrudeWhetstone", "HacksawBlade", "HandScytheBlade",
  # Cooking — non-food hardware
  "BakingSoda", "Chopsticks", "CocktailUmbrella",
]

SKIP_SHORTS = {
  "Chalk",  # removed B42.19
  "Lure",  # split into JigLure / MinnowLure B42.19
  "RailroadTrack", "RailroadTrackPiece",  # removed B42.19
  "PropaneTank",  # fluid container
  "IndustrialDye",  # fluid dye bottle
  "CeramicCrucibleSmall_Iron",
  "CeramicCrucibleSmall_Steel",
  "CeramicCrucibleWithGlass",
}

SKIP_TYPE = re.compile(r"food|weapon|clothing|container", re.I)


def camel_label(short: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", short)
    s = s.replace("_", " ")
    return s.lower()


def bulk_prefix(short: str) -> str:
    return f"{short}Bulk"


def key_from_short(short: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", short)
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).lower().strip("_")


def load_gaps() -> list[str]:
    gap_file = Path(__file__).parent / "_gap_shorts.txt"
    shorts = []
    if gap_file.is_file():
        for line in gap_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                shorts.append(line)
    return shorts


def build_entry(short: str, meta: dict):
    if meta.get("error"):
        icon = short
        wsm = short
    else:
        icon = meta.get("icon") or short
        wsm = meta.get("wsm") or meta.get("static") or icon

    tags = meta.get("tags")
    display_category = meta.get("category") or "Material"
    item_type = "base:normal"
    it = meta.get("item_type", "")
    if it:
        if "literature" in it:
            item_type = "base:literature"
            display_category = "Literature"
        elif "drainable" in it:
            item_type = "base:drainable"

    survival_gear = tags and "base:thread" in tags

    return _mat(
        key_from_short(short),
        bulk_prefix(short),
        f"Base.{short}",
        camel_label(short),
        icon,
        wsm=wsm,
        static_model=meta.get("static"),
        tags=tags,
        display_category=display_category,
        item_type=item_type,
        survival_gear=bool(survival_gear),
    )


def main():
    shorts = []
    seen = set()
    for s in load_gaps() + EXTRA_SHORTS:
        if s in seen or s in SKIP_SHORTS:
            continue
        seen.add(s)
        shorts.append(s)

    entries = []
    skipped = []
    for i, short in enumerate(shorts):
        meta = fetch_meta(short)
        if SKIP_TYPE.search(meta.get("item_type", "")) and "drainable" not in meta.get("item_type", ""):
            skipped.append((short, meta.get("item_type")))
            continue
        entries.append(build_entry(short, meta))
        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{len(shorts)}", file=sys.stderr)
        time.sleep(0.12)

    out = Path(__file__).parent / "expansion_materials.py"
    lines = [
        '"""Auto-generated packable expansion (vanilla gaps + selected junk/tool/cooking)."""',
        "from materials_catalog import _mat",
        "",
        "EXPANSION_MATERIALS = [",
    ]
    for e in entries:
        parts = [
            f'    _mat("{e["key"]}", "{e["bulk_prefix"]}", "{e["loose"]}", "{e["label"]}", "{e["icon"]}"',
        ]
        if e.get("wsm"):
            parts[0] += f', wsm="{e["wsm"]}"'
        opts = []
        if e.get("static_model"):
            opts.append(f'static_model="{e["static_model"]}"')
        if e.get("tags"):
            opts.append(f'tags="{e["tags"]}"')
        if e.get("display_category") != "Material":
            opts.append(f'display_category="{e["display_category"]}"')
        if e.get("item_type") != "base:normal":
            opts.append(f'item_type="{e["item_type"]}"')
        if e.get("survival_gear"):
            opts.append("survival_gear=True")
        if opts:
            if e.get("wsm"):
                parts[0] += ", " + ", ".join(opts)
            else:
                parts[0] += ", " + ", ".join(opts)
        parts[0] += "),"
        lines.append(parts[0])
    lines.append("]")
    lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(entries)} entries to {out}")
    if skipped:
        print(f"Skipped {len(skipped)}:", skipped[:10])


if __name__ == "__main__":
    main()
