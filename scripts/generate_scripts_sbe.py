"""Regenerate optional addon scripts for Skill Book Expansion (3557111695)."""
import json
import os
import sys
from pathlib import Path

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from generate_scripts import write_book_skills  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SBE_MEDIA = (
    REPO_ROOT / "Contents" / "mods" / "IKappaIDOmniPacking_SkillBookExpansion" / "42.18" / "media"
)

SBE_BOOK_SKILLS = [
    {"key": "sbe_axe", "label": "axe", "prefix": "BookAxe", "color": (38, 9, 23), "module": "SkillBookExpansionB42"},
    {"key": "sbe_long_blunt", "label": "long blunt", "prefix": "BookBlunt", "color": (210, 50, 50), "module": "SkillBookExpansionB42"},
    {"key": "sbe_short_blunt", "label": "short blunt", "prefix": "BookSmallBlunt", "color": (210, 50, 50), "module": "SkillBookExpansionB42"},
    {"key": "sbe_short_blade", "label": "short blade", "prefix": "BookSmallBlade", "color": (210, 50, 50), "module": "SkillBookExpansionB42"},
    {"key": "sbe_spear", "label": "spear", "prefix": "BookSpear", "color": (210, 50, 50), "module": "SkillBookExpansionB42"},
    {"key": "sbe_nimble", "label": "nimble", "prefix": "BookNimble", "color": (253, 162, 206), "module": "SkillBookExpansionB42"},
    {"key": "sbe_sneaking", "label": "sneaking", "prefix": "BookSneaking", "color": (210, 50, 50), "module": "SkillBookExpansionB42"},
    {"key": "sbe_sprinting", "label": "sprinting", "prefix": "BookSprinting", "color": (210, 50, 50), "module": "SkillBookExpansionB42"},
    {"key": "sbe_lightfooted", "label": "lightfooted", "prefix": "BookLightfooted", "color": (10, 220, 10), "module": "SkillBookExpansionB42"},
    {"key": "sbe_strength", "label": "strength", "prefix": "BookStrength", "color": (9, 23, 38), "module": "SkillBookExpansionB42"},
    {"key": "sbe_fitness", "label": "fitness", "prefix": "BookFitness", "color": (210, 50, 50), "module": "SkillBookExpansionB42"},
]


def write_sbe_media(root: str) -> None:
    lines = ["module IKOP", "{", ""]
    rlines = ["module IKOP", "{", ""]
    recipes = {}
    items = {}
    write_book_skills(
        lines, rlines, recipes, items, SBE_BOOK_SKILLS,
        "Skill Book Expansion (SkillBookExpansionB42): volumes 1-5 per skill",
    )
    lines.append("}")
    rlines.append("}")
    os.makedirs(f"{root}/scripts", exist_ok=True)
    os.makedirs(f"{root}/lua/shared/Translate/EN", exist_ok=True)
    with open(f"{root}/scripts/ikop_sbe_items.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(f"{root}/scripts/ikop_sbe_recipes.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(rlines))
    with open(f"{root}/lua/shared/Translate/EN/Recipes.json", "w", encoding="utf-8") as f:
        json.dump(recipes, f, indent=4)
    with open(f"{root}/lua/shared/Translate/EN/ItemName.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4)


if __name__ == "__main__":
    media = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_SBE_MEDIA)
    write_sbe_media(media)
    print("Wrote SBE addon", media, "—", len(SBE_BOOK_SKILLS), "skill sets")
