"""Curated shelf-stable vanilla food for IKOP bulk packing (B42)."""
import re

from materials_catalog import _mat

FOOD_LABEL_OVERRIDES = {
    "flour2": "flour",
    "sugar": "sugar",
    "sugarbrown": "brown sugar",
    "oatsraw": "oats",
    "cornmeal2": "cornmeal",
    "cornflour2": "corn flour",
    "driedblackbeans": "dried black beans",
    "driedkidneybeans": "dried kidney beans",
    "driedchickpeas": "dried chickpeas",
    "driedlentils": "dried lentils",
    "driedsplitpeas": "dried split peas",
    "barleysheafdried": "dried barley sheaves",
    "ryesheafdried": "dried rye sheaves",
    "beefjerky": "beef jerky",
    "dehydratedmeatstick": "dehydrated meat sticks",
    "tortillachips": "tortilla chips",
    "oilvegetable": "vegetable oil",
    "oilolive": "olive oil",
    "vinegar2": "vinegar",
    "ricevinegar": "rice vinegar",
    "maplesyrup": "maple syrup",
    "peanutbutter": "peanut butter",
    "driedapricots": "dried apricots",
    "teabag2": "tea bags",
    "coffee2": "coffee",
    "sunflowerseeds": "sunflower seeds",
    "poppyseed": "poppy seeds",
    "sugarcubes": "sugar cubes",
    "candycorn": "candy corn",
    "jellybeans": "jelly beans",
    "chocolate_candy": "chocolates",
    "bouilloncube": "bouillon cubes",
    "cocoa powder": "cocoa powder",
    "cookiessugar": "sugar cookies",
    "cookiesshortbread": "shortbread cookies",
    "cookieschocolate": "chocolate cookies",
    "cookiechocolatechip": "chocolate chip cookies",
    "cookiesoatmeal": "oatmeal cookies",
    "cookiejelly": "jelly cookies",
    "grahamcrackers": "graham crackers",
    "scoutcookies": "scout cookies",
    "hihis": "Hi-His",
    "chococakes": "choco cakes",
    "cinnamonroll": "cinnamon rolls",
    "crispyricesquare": "crispy rice squares",
    "gingerbreadman": "gingerbread men",
    "plonkies": "plonkies",
    "quaggacakes": "quagga cakes",
    "snoglobes": "sno globes",
    "chocolatecoveredcoffeebeans": "chocolate covered coffee beans",
    "candycane": "candy canes",
    "chocolate_butterchunkers": "butterchunkers chocolate",
    "chocolate_crackle": "crackle chocolate",
    "chocolate_deux": "deux chocolate",
    "chocolate_galacticdairy": "galactic dairy chocolate",
    "chocolate_royspbpucks": "Roy's PB pucks",
    "chocolate_smirkers": "smirkers chocolate",
    "chocolate_sniksnak": "snik-snak chocolate",
    "driedwhitebeans": "dried white beans",
    "lavenderpetalsdried": "dried lavender petals",
    "blacksagedried": "dried black sage",
    "commonmallowdried": "dried common mallow",
    "ginseng": "ginseng",
    "wildgarlicdried": "dried wild garlic",
    "pepperjalapenodried": "dried jalapeño",
    "pepperhabanerodried": "dried habanero",
    "chamomiledried": "dried chamomile",
    "marigolddried": "dried marigold",
    "rosepetalsdried": "dried rose petals",
    "seasoning_basil": "basil seasoning",
    "seasoning_chives": "chives seasoning",
    "seasoning_cilantro": "cilantro seasoning",
    "seasoning_oregano": "oregano seasoning",
    "seasoning_parsley": "parsley seasoning",
    "seasoning_rosemary": "rosemary seasoning",
    "seasoning_sage": "sage seasoning",
    "seasoning_thyme": "thyme seasoning",
    "powderedgarlic": "powdered garlic",
    "powderedonion": "powdered onion",
    "vinegar_jug": "vinegar jug",
    "mayonnaisefull": "mayonnaise",
    "remouladefull": "remoulade",
    "dip_nachocheese": "nacho cheese dip",
    "dip_ranch": "ranch dip",
    "dip_salsa": "salsa dip",
    "cannedcarrots2": "canned carrots",
    "cannedchili": "canned chili",
    "cannedcornedbeef": "canned corned beef",
    "cannedmilk": "canned milk",
    "cannedfruitbeverage": "canned fruit beverage",
    "cannedfruitcocktail": "canned fruit cocktail",
    "cannedpeaches": "canned peaches",
    "cannedpineapple": "canned pineapple",
}

# Loose Base.* only — shelf-stable dry goods, snacks, spices (no drainables / open bottles / raw meat).
FOOD_SHORTS = [
    # dry staples
    "Flour2", "SugarBrown", "Salt", "Rice", "Pasta", "Macaroni", "OatsRaw",
    "Cornmeal2", "Cornflour2", "BouillonCube", "CocoaPowder",
    # dried legumes & grains
    "DriedBlackBeans", "DriedKidneyBeans", "DriedChickpeas", "DriedLentils", "DriedSplitPeas",
    "BarleySheafDried", "RyeSheafDried",
    # snacks & preserved
    "BeefJerky", "DehydratedMeatStick", "TortillaChips", "Crackers", "Ramen", "GranolaBar",
    "Popcorn", "PorkRinds", "DriedApricots",
    # chips
    "Crisps", "Crisps2", "Crisps3", "Crisps4",
    # candy
    "CandyCorn", "JellyBeans", "Marshmallows", "Chocolate_Candy", "GummyBears", "Gum",
    "HardCandies", "MintCandy", "RockCandy",
    # oils, spreads, condiments (sealed units)
    "Honey", "PeanutButter", "MapleSyrup", "RiceVinegar", "OilVegetable", "OilOlive",
    "Margarine", "Lard", "Butter",
    # spices & dried herbs
    "Cinnamon", "Pepper", "SeasoningSalt", "BasilDried", "OreganoDried", "RosemaryDried",
    "SageDried", "ThymeDried", "ParsleyDried", "ChivesDried", "MintHerbDried",
    # beverages (dry)
    "Teabag2", "Coffee2",
    # seeds & misc dry
    "SunflowerSeeds", "PoppySeed", "SugarCubes", "BalsamicVinegar",
    # canned (whole sealed tins — not Open* variants)
    "TinnedBeans", "TunaTin", "CannedCorn", "CannedPeas", "CannedPotato2", "CannedTomato2",
    "CannedMushroomSoup", "CannedSardines", "CannedBolognese", "Dogfood",
    # cookies, snacks, chocolate (OCP overlap OK)
    "CookiesSugar", "CookiesShortbread", "CookiesChocolate", "CookieChocolateChip",
    "CookiesOatmeal", "CookieJelly", "GrahamCrackers", "ScoutCookies",
    "HiHis", "ChocoCakes", "CinnamonRoll", "CrispyRiceSquare", "Gingerbreadman",
    "Plonkies", "Pretzel", "QuaggaCakes", "SnoGlobes", "ChocolateCoveredCoffeeBeans",
    "Candycane",
    "Chocolate", "Chocolate_Butterchunkers", "Chocolate_Crackle", "Chocolate_Deux",
    "Chocolate_GalacticDairy", "Chocolate_RoysPBPucks", "Chocolate_Smirkers", "Chocolate_SnikSnak",
    "Cereal", "Cheese", "Salami", "Yoghurt", "DriedWhiteBeans", "Sugar",
    # dried herbs & seasonings
    "LavenderPetalsDried", "BlackSageDried", "CommonMallowDried", "Ginseng",
    "WildGarlicDried", "PepperJalapenoDried", "PepperHabaneroDried",
    "ChamomileDried", "MarigoldDried", "RosePetalsDried",
    "Seasoning_Basil", "Seasoning_Chives", "Seasoning_Cilantro", "Seasoning_Oregano",
    "Seasoning_Parsley", "Seasoning_Rosemary", "Seasoning_Sage", "Seasoning_Thyme",
    "PowderedGarlic", "PowderedOnion",
    # sealed condiments & dips
    "Ketchup", "Mustard", "Soysauce", "TomatoPaste", "BBQSauce", "Hotsauce",
    "SesameOil", "Marinara", "JamFruit", "JamMarmalade", "Pickles",
    "Vinegar2", "Vinegar_Jug", "MayonnaiseFull", "RemouladeFull",
    "Dip_NachoCheese", "Dip_Ranch", "Dip_Salsa",
    # extra canned goods
    "CannedCarrots2", "CannedChili", "CannedCornedBeef", "CannedMilk",
    "CannedFruitBeverage", "CannedFruitCocktail", "CannedPeaches", "CannedPineapple",
]


def _food_key(short: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", short)
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).lower().strip("_")


def _food_label(short: str) -> str:
    key = _food_key(short).replace("_", "")
    if key in FOOD_LABEL_OVERRIDES:
        return FOOD_LABEL_OVERRIDES[key]
    return re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", short).replace("_", " ").lower()


def _food(short: str, icon=None, wsm=None, static_model=None, tags=None, label=None):
    key = _food_key(short)
    return _mat(
        f"food_{key}",
        f"{short}Bulk",
        f"Base.{short}",
        label or _food_label(short),
        icon or short,
        wsm=wsm or short,
        static_model=static_model,
        tags=tags,
        display_category="Food",
        item_type="base:normal",
        is_food=True,
    )


def build_food_materials(meta_by_short: dict) -> list:
    out = []
    for short in FOOD_SHORTS:
        meta = meta_by_short.get(short, {})
        if meta.get("use_delta"):
            continue
        item_type = meta.get("item_type", "base:food")
        if item_type and item_type not in ("base:food", ""):
            continue
        icon = meta.get("icon") or short
        wsm = meta.get("wsm") or meta.get("static") or icon
        static_model = meta.get("static")
        tags = meta.get("tags")
        out.append(_food(short, icon=icon, wsm=wsm, static_model=static_model, tags=tags))
    return out
