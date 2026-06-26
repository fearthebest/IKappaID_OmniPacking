"""Regenerate ikop_items.txt, ikop_recipes.txt, EN translations. Run from repo root."""
import json
import os
import sys
from pathlib import Path

from materials_catalog import EXTRA_MATERIALS, build_seed_materials

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MEDIA = REPO_ROOT / "Contents" / "mods" / "IKappaIDOmniPacking" / "42.18" / "media"

SIZES = [5, 10, 25, 50, 100]

# Custom IKOP sprites: media/textures/Item_IKOPBulk5.png → Icon = IKOPBulk5
# (flat Item_ prefix — reliable; subfolder IKOP/Bulk5 is wiki-documented but inconsistent in B42 notes)
TIER_ICON = {
    5: "IKOPBulk5",
    10: "IKOPBulk10",
    25: "IKOPBulk25",
    50: "IKOPBulk50",
    100: "IKOPBulk100",
}


def ikop_bundle_icon(_mat: dict, tier: int) -> str:
    return TIER_ICON[tier]


# Ground mesh when bundle is dropped (vanilla parcel models — same approach as OCsPacking).
# See https://pzwiki.net/wiki/WorldStaticModel and OCP box items.
TIER_WSM_FOOD = {
    5: "Parcel_Food_ExtraSmall",
    10: "Parcel_Food_Small",
    25: "Parcel_Food_Small",
    50: "Parcel_Food_Medium",
    100: "Parcel_Food_Medium",
}
TIER_WSM_MATERIAL = {
    5: "Parcel_Food_ExtraSmall",
    10: "Parcel_Food_Small",
    25: "Parcel_Food_Medium",
    50: "Parcel_Hardware_Large",
    100: "Parcel_Hardware_Large",
}
TIER_WSM_LITERATURE = {
    5: "BookYellowBrown_Ground",
    10: "BookClosedGround",
    25: "MagazineGround",
    50: "Parcel_Food_Small",
    100: "Parcel_Food_Medium",
}


def ikop_bundle_wsm(mat: dict, tier: int) -> str:
    if mat.get("is_food"):
        return TIER_WSM_FOOD[tier]
    display = mat.get("display_category", "Material")
    item_type = mat.get("item_type", "base:normal")
    if display == "FirstAid":
        return "MedicalParcel_Green"
    if item_type == "base:literature" or display == "Literature":
        return TIER_WSM_LITERATURE[tier]
    return TIER_WSM_MATERIAL[tier]


def size_key(n: int) -> str:
    return f"{n:03d}"


# Each entry: key, bulk_prefix, loose FullType, display label, icon, world/static model fields, tags, metal_value per unit (optional)
MATERIALS = [
    # --- original six ---
    {
        "key": "scrap_metal",
        "bulk_prefix": "ScrapMetalBulk",
        "loose": "Base.ScrapMetal",
        "label": "scrap metal",
        "icon": "ScrapMetal",
        "wsm": "ScrapMetal",
        "static_model": None,
        "tags": "base:smeltableironsmall",
        "metal_unit": 30.0,
        "survival_gear": True,
    },
    {
        "key": "planks",
        "bulk_prefix": "PlankBulk",
        "loose": "Base.Plank",
        "label": "planks",
        "icon": "Plank",
        "wsm": "Plank",
        "static_model": None,
        "tags": None,
        "metal_unit": None,
    },
    {
        "key": "sheet_metal",
        "bulk_prefix": "SheetMetalBulk",
        "loose": "Base.SheetMetal",
        "label": "sheet metal",
        "icon": "SheetMetal",
        "wsm": "MetalSheet",
        "static_model": None,
        "tags": "base:smeltablesteellarge;base:hasmetal",
        "metal_unit": 80.0,
    },
    {
        "key": "small_sheet_metal",
        "bulk_prefix": "SmallSheetMetalBulk",
        "loose": "Base.SmallSheetMetal",
        "label": "small sheet metal",
        "icon": "MetalSheetSmall",
        "wsm": "MetalSheetSmall",
        "static_model": None,
        "tags": "base:smeltablesteelsmall;base:smallsheetmetal;base:hasmetal",
        "metal_unit": 20.0,
    },
    {
        "key": "metal_bars",
        "bulk_prefix": "MetalBarBulk",
        "loose": "Base.MetalBar",
        "label": "metal bars",
        "icon": "SteelRod_Full",
        "wsm": None,
        "static_model": None,
        "tags": None,
        "metal_unit": None,
    },
    {
        "key": "metal_pipes",
        "bulk_prefix": "MetalPipeBulk",
        "loose": "Base.MetalPipe",
        "label": "metal pipes",
        "icon": "MetalTube",
        "wsm": None,
        "static_model": None,
        "tags": None,
        "metal_unit": None,
    },
    # --- bulk haul (no vanilla 5–100 tier); logs → materials_catalog WOODCUTTING_MATERIALS ---
    {
        "key": "charcoal",
        "bulk_prefix": "CharcoalBulk",
        "loose": "Base.Charcoal",
        "label": "charcoal",
        "icon": "Charcoal",
        "wsm": "Charcoal_Ground",
        "static_model": None,
        "tags": "base:charcoal;base:isfirefuel",
        "metal_unit": None,
    },
    {
        "key": "iron_ingot",
        "bulk_prefix": "IronIngotBulk",
        "loose": "Base.IronIngot",
        "label": "iron ingots",
        "icon": "Ingot_Iron",
        "wsm": "IronIngot",
        "static_model": "IronIngot",
        "tags": "base:hasmetal;base:ingot",
        "metal_unit": None,
    },
    {
        "key": "steel_ingot",
        "bulk_prefix": "SteelIngotBulk",
        "loose": "Base.SteelIngot",
        "label": "steel ingots",
        "icon": "Ingot_Steel",
        "wsm": "SteelIngot",
        "static_model": "SteelIngot",
        "tags": "base:hasmetal;base:steelmaterial;base:ingot",
        "metal_unit": None,
    },
    {
        "key": "glass_panel",
        "bulk_prefix": "GlassPanelBulk",
        "loose": "Base.GlassPanel",
        "label": "glass panels",
        "icon": "GlassPane",
        "wsm": "GlassPanel",
        "static_model": "GlassPanel",
        "tags": "base:glass",
        "metal_unit": None,
    },
    {
        "key": "limestone",
        "bulk_prefix": "LimestoneBulk",
        "loose": "Base.Limestone",
        "label": "limestone",
        "icon": "Limestone",
        "wsm": "Limestone",
        "static_model": None,
        "tags": "base:stone;base:limestone",
        "metal_unit": None,
    },
    {
        "key": "clay",
        "bulk_prefix": "ClayBulk",
        "loose": "Base.Clay",
        "label": "clay",
        "icon": "Clay",
        "wsm": "Clay",
        "static_model": "Clay",
        "tags": None,
        "metal_unit": None,
    },
    {
        "key": "magazine",
        "bulk_prefix": "MagazineBulk",
        "loose": "Base.Magazine",
        "label": "magazines",
        "icon": "Magazine",
        "wsm": "MagazineGround",
        "static_model": "Magazine",
        "tags": "base:magazine",
        "metal_unit": None,
        "display_category": "Literature",
        "item_type": "base:literature",
    },
    {
        "key": "newspaper",
        "bulk_prefix": "NewspaperBulk",
        "loose": "Base.Newspaper",
        "label": "newspapers",
        "icon": "Newspaper",
        "wsm": "Newspaper_Ground",
        "static_model": "Newspaper",
        "tags": "base:newspaper",
        "metal_unit": None,
        "display_category": "Literature",
        "item_type": "base:literature",
    },
]

MATERIALS.extend(EXTRA_MATERIALS)
MATERIALS.extend(build_seed_materials())

# Loose skill books 1–5 per row → one IKOP slipcase (vanilla PackSetOfBooks has no sandbox weight reduction).
# prefix: Base.BookCarpentry1 … BookCarpentry5 (mechanics uses BookMechanic).
# ColorBlue, ColorGreen, ColorRed — copied from vanilla Book*Set slipcases.
BOOK_SKILLS = [
    {"key": "aiming", "label": "aiming", "prefix": "BookAiming", "color": (210, 50, 50)},
    {"key": "husbandry", "label": "husbandry", "prefix": "BookHusbandry", "color": (210, 50, 50)},
    {"key": "butchering", "label": "butchering", "prefix": "BookButchering", "color": (0, 0, 78)},
    {"key": "carpentry", "label": "carpentry", "prefix": "BookCarpentry", "color": (210, 50, 50)},
    {"key": "carving", "label": "carving", "prefix": "BookCarving", "color": (253, 162, 206)},
    {"key": "cooking", "label": "cooking", "prefix": "BookCooking", "color": (210, 50, 50)},
    {"key": "electrician", "label": "electrician", "prefix": "BookElectrician", "color": (210, 50, 50)},
    {"key": "farming", "label": "farming", "prefix": "BookFarming", "color": (10, 220, 10)},
    {"key": "firstaid", "label": "first aid", "prefix": "BookFirstAid", "color": (210, 50, 50)},
    {"key": "fishing", "label": "fishing", "prefix": "BookFishing", "color": (210, 50, 50)},
    {"key": "foraging", "label": "foraging", "prefix": "BookForaging", "color": (250, 206, 135)},
    {"key": "glassmaking", "label": "glassmaking", "prefix": "BookGlassmaking", "color": (9, 23, 38)},
    {"key": "longblade", "label": "long blade", "prefix": "BookLongBlade", "color": (38, 9, 23)},
    {"key": "masonry", "label": "masonry", "prefix": "BookMasonry", "color": (100, 195, 171)},
    {"key": "mechanics", "label": "mechanics", "prefix": "BookMechanic", "color": (210, 50, 50)},
    {"key": "blacksmith", "label": "blacksmith", "prefix": "BookBlacksmith", "color": (72, 69, 58)},
    {"key": "metalwelding", "label": "metal welding", "prefix": "BookMetalWelding", "color": (75, 75, 75)},
    {"key": "reloading", "label": "reloading", "prefix": "BookReloading", "color": (210, 50, 50)},
    {"key": "tailoring", "label": "tailoring", "prefix": "BookTailoring", "color": (194, 194, 244)},
    {"key": "tracking", "label": "tracking", "prefix": "BookTracking", "color": (9, 23, 38)},
    {"key": "trapping", "label": "trapping", "prefix": "BookTrapping", "color": (210, 50, 50)},
    {"key": "flintknapping", "label": "flint knapping", "prefix": "BookFlintKnapping", "color": (250, 206, 135)},
    {"key": "maintenance", "label": "maintenance", "prefix": "BookMaintenance", "color": (210, 50, 50)},
    {"key": "pottery", "label": "pottery", "prefix": "BookPottery", "color": (67, 104, 203)},
]


def write_book_skills(lines, rlines, recipes, items, book_list, section_comment: str) -> None:
    lines.append(f"    /* {section_comment} */")
    lines.append("")
    for skill in book_list:
        key = skill["key"]
        prefix = skill["prefix"]
        module = skill.get("module", "Base")
        bundle_item = f"{prefix}SkillBundle"
        pack_id = f"ikop_pack_books_{key}"
        unstack_id = f"ikop_unstack_books_{key}"
        cb, cg, cr = skill["color"]

        lines.extend([
            f"    item {bundle_item}",
            "    {",
            "        DisplayCategory = SkillBook,",
            "        ItemType = base:normal,",
            "        Weight = 1.0,",
            "        Icon = BookSlipcase,",
            "        IconColorMask = BookSlipcase_Mask,",
            "        WorldStaticModel = BookSlipcase,",
            f"        ColorBlue = {cb},",
            f"        ColorGreen = {cg},",
            f"        ColorRed = {cr},",
            "        Tags = ikop:bulk;base:ignorezombiedensity,",
            f"        DoubleClickRecipe = {unstack_id},",
            "    }",
            "",
        ])

        input_lines = []
        output_lines = []
        for level in range(1, 6):
            book = f"{module}.{prefix}{level}"
            input_lines.append(
                f"            item 1 [{book}] flags[AllowFavorite;InheritFavorite;IsExclusive],"
            )
            output_lines.append(f"            item 1 {book},")

        rlines.extend([
            f"    craftRecipe {pack_id}",
            "    {",
            "        timedAction = PackingBox,",
            "        time = 100,",
            "        OnCreate = IKOP_RecipeCode.onCreateBulkPack,",
            "        OnTest = IKOP_RecipeCode.canPackLooseSkillBook,",
            "        Tags = InHandCraft;Packing,",
            "        category = Packing,",
            "        inputs",
            "        {",
            *input_lines,
            "        }",
            "        outputs",
            "        {",
            f"            item 1 IKOP.{bundle_item},",
            "        }",
            "    }",
            "",
            f"    craftRecipe {unstack_id}",
            "    {",
            "        timedAction = UnPackBox,",
            "        time = 80,",
            "        OnTest = IKOP_RecipeCode.canUnstackSkillBookSet,",
            "        Tags = InHandCraft;Packing;CanBeDoneInDark,",
            "        category = Packing,",
            "        inputs",
            "        {",
            f"            item 1 [IKOP.{bundle_item}] flags[AllowFavorite;InheritFavorite],",
            "        }",
            "        outputs",
            "        {",
            *output_lines,
            "        }",
            "    }",
            "",
        ])

        label = skill["label"]
        title = label.title() if key != "firstaid" else "First Aid"
        recipes[pack_id] = f"Bundle {label} skill books (Lv 1–5)"
        recipes[unstack_id] = f"Unbundle {label} skill books (Lv 1–5)"
        items[f"IKOP.{bundle_item}"] = f"{title} skill books (Lv 1–5)"


def write_media(root: str) -> None:
    lines = ["module IKOP", "{", ""]
    rlines = ["module IKOP", "{", ""]
    recipes = {}
    items = {}

    for mat in MATERIALS:
        key = mat["key"]
        bulk_prefix = mat["bulk_prefix"]
        loose = mat["loose"]
        label = mat["label"]
        icon = mat["icon"]
        wsm = mat.get("wsm")
        static_model = mat.get("static_model")
        extra_tags = mat.get("tags")
        metal_unit = mat.get("metal_unit")
        display_category = mat.get("display_category", "Material")
        item_type = mat.get("item_type", "base:normal")
        survival_gear = mat.get("survival_gear", False)
        is_food = mat.get("is_food", False)

        for n in SIZES:
            sk = size_key(n)
            iname = f"{bulk_prefix}{n}"
            stack_id = f"ikop_stack_{key}_{sk}"
            unstack_id = f"ikop_unstack_{key}_{sk}"
            on_test_pack = "IKOP_RecipeCode.canPackLooseFood" if is_food else f"IKOP_RecipeCode.canPackStackTier{n}"
            bundle_icon = ikop_bundle_icon(mat, n)
            bundle_wsm = ikop_bundle_wsm(mat, n)

            lines.extend([
                f"    item {iname}",
                "    {",
                f"        DisplayCategory = {display_category},",
                f"        ItemType = {item_type},",
                "        Weight = 1.0,",
                f"        Icon = {bundle_icon},",
            ])
            if metal_unit:
                lines.append(f"        MetalValue = {metal_unit * n:.1f},")
            lines.append(f"        WorldStaticModel = {bundle_wsm},")
            if survival_gear:
                lines.append("        SurvivalGear = true,")

            tags = "ikop:bulk"
            if extra_tags:
                tags += ";" + extra_tags
            lines.extend([
                f"        Tags = {tags},",
                f"        DoubleClickRecipe = {unstack_id},",
                "    }",
                "",
            ])

            time_pack = 80 + n * 2
            rlines.extend([
                f"    craftRecipe {stack_id}",
                "    {",
                "        timedAction = PackingBox,",
                f"        time = {time_pack},",
                "        OnCreate = IKOP_RecipeCode.onCreateBulkPack,",
                f"        OnTest = {on_test_pack},",
                "        Tags = InHandCraft;Packing,",
                "        category = Packing,",
                "        inputs",
                "        {",
                f"            item {n} [{loose}] mode:destroy flags[AllowFavorite;InheritFavorite;ItemCount;IsExclusive],",
                "        }",
                "        outputs",
                "        {",
                f"            item 1 IKOP.{iname},",
                "        }",
                "    }",
                "",
                f"    craftRecipe {unstack_id}",
                "    {",
                "        timedAction = UnPackBox,",
                "        time = 80,",
                f"        OnTest = IKOP_RecipeCode.canUnstackStackTier{n},",
                "        Tags = InHandCraft;Packing;CanBeDoneInDark,",
                "        category = Packing,",
                "        inputs",
                "        {",
                f"            item 1 [IKOP.{iname}] flags[AllowFavorite;InheritFavorite],",
                "        }",
                "        outputs",
                "        {",
                f"            item {n} {loose},",
                "        }",
                "    }",
                "",
            ])
            recipes[stack_id] = f"Bundle {label} (×{n})"
            recipes[unstack_id] = f"Unbundle {label} (×{n})"
            title_label = label.title()
            if key == "log":
                title_label = "Logs"
            elif key == "magazine":
                title_label = "Magazines"
            elif key == "newspaper":
                title_label = "Newspapers"
            elif key == "book":
                title_label = "Books"
            elif key == "comic_book":
                title_label = "Comic books"
            elif key == "journal":
                title_label = "Journals"
            elif key == "notebook":
                title_label = "Notebooks"
            elif key == "sheet_paper":
                title_label = "Sheets of paper"
            items[f"IKOP.{iname}"] = f"{title_label} (bulk ×{n})"

    write_book_skills(
        lines, rlines, recipes, items, BOOK_SKILLS,
        "Skill book sets (vanilla Base): volumes 1-5 per skill",
    )

    lines.append("}")
    rlines.append("}")

    os.makedirs(f"{root}/scripts", exist_ok=True)
    os.makedirs(f"{root}/lua/shared/Translate/EN", exist_ok=True)
    with open(f"{root}/scripts/ikop_items.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(f"{root}/scripts/ikop_recipes.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(rlines))
    with open(f"{root}/lua/shared/Translate/EN/Recipes.json", "w", encoding="utf-8") as f:
        json.dump(recipes, f, indent=4)
    with open(f"{root}/lua/shared/Translate/EN/ItemName.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4)


if __name__ == "__main__":
    media = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_MEDIA)
    write_media(media)
    print(
        "Wrote",
        media,
        "—",
        len(MATERIALS),
        "materials ×",
        len(SIZES),
        "sizes +",
        len(BOOK_SKILLS),
        "vanilla skill sets",
    )
