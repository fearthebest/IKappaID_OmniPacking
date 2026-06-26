"""Build food_materials.py from food_catalog + pzfans metadata."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fetch_item_meta import fetch_meta
from food_catalog import FOOD_SHORTS, build_food_materials, _food_key, _food_label


def main():
    meta_by_short = {}
    for short in FOOD_SHORTS:
        meta_by_short[short] = fetch_meta(short)
        time.sleep(0.1)

    materials = build_food_materials(meta_by_short)
    lines = [
        '"""Generated food packables (shelf-stable Base.*). Regenerate via generate_food_materials.py."""',
        "from materials_catalog import _mat",
        "",
        "FOOD_MATERIALS = [",
    ]
    for m in materials:
        parts = [
            f'    _mat("{m["key"]}", "{m["bulk_prefix"]}", "{m["loose"]}", "{m["label"]}", "{m["icon"]}"',
        ]
        opts = []
        if m.get("wsm"):
            opts.append(f'wsm="{m["wsm"]}"')
        if m.get("static_model"):
            opts.append(f'static_model="{m["static_model"]}"')
        if m.get("tags"):
            opts.append(f'tags="{m["tags"]}"')
        opts.append('display_category="Food"')
        opts.append('item_type="base:normal"')
        opts.append("is_food=True")
        if opts:
            parts[0] += ", " + ", ".join(opts)
        parts[0] += "),"
        lines.append(parts[0])
    lines.append("]")
    lines.append("")

    out = Path(__file__).parent / "food_materials.py"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(materials)} food entries to {out}")


if __name__ == "__main__":
    main()
