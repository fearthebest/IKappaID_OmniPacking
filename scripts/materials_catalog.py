"""Extra packable vanilla materials for IKappaID Omni Packing (B42)."""
import re

SEED_ITEM_NAMES = [
    "BasilSeed", "BellPepperSeed", "BlackSageSeed", "BroadleafPlantainSeed", "BroccoliSeed",
    "CabbageSeed", "CarrotSeed", "CauliflowerSeed", "ChamomileSeed", "ChivesSeed", "ComfreySeed",
    "CommonMallowSeed", "CucumberSeed", "GarlicSeed", "HabaneroSeed", "HempSeed", "HopsSeed",
    "JalapenoSeed", "KaleSeed", "LavenderSeed", "LeekSeed", "LemonGrassSeed", "LettuceSeed",
    "MarigoldSeed", "MintSeed", "OnionSeed", "OreganoSeed", "ParsleySeed", "PotatoSeed",
    "RedRadishSeed", "RoseSeed", "RosemarySeed", "SageSeed", "SpinachSeed", "StrewberrieSeed",
    "SugarBeetSeed", "SweetPotatoSeed", "ThymeSeed", "TobaccoSeed", "TomatoSeed", "TurnipSeed",
    "WatermelonSeed", "WildGarlicSeed", "ZucchiniSeed",
]

SEED_LABEL_OVERRIDES = {
    "strewberrie": "strawberry seeds",
    "redradish": "radish seeds",
    "sweetpotato": "sweet potato seeds",
    "sugarbeet": "sugar beet seeds",
    "wildgarlic": "wild garlic seeds",
    "lemongrass": "lemon grass seeds",
    "bellpepper": "bell pepper seeds",
    "blacksage": "black sage seeds",
    "broadleafplantain": "broadleaf plantain seeds",
    "commonmallow": "common mallow seeds",
}


def _mat(
    key,
    bulk_prefix,
    loose,
    label,
    icon,
    wsm=None,
    static_model=None,
    tags=None,
    metal_unit=None,
    display_category="Material",
    item_type="base:normal",
    survival_gear=False,
    is_food=False,
):
    return {
        "key": key,
        "bulk_prefix": bulk_prefix,
        "loose": loose,
        "label": label,
        "icon": icon,
        "wsm": wsm,
        "static_model": static_model,
        "tags": tags,
        "metal_unit": metal_unit,
        "display_category": display_category,
        "item_type": item_type,
        "survival_gear": survival_gear,
        "is_food": is_food,
    }


def _camel_label(base: str) -> str:
    words = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", base).lower()
    return words


def build_seed_materials():
    out = []
    for seed in SEED_ITEM_NAMES:
        base = seed.replace("Seed", "")
        key = re.sub(r"[^a-z0-9]+", "_", base.lower()).strip("_")
        label = SEED_LABEL_OVERRIDES.get(key)
        if not label:
            label = _camel_label(base) + " seeds"
        out.append(
            _mat(
                f"seed_{key}",
                f"{seed}Bulk",
                f"Base.{seed}",
                label,
                "Seeds_Generic",
                wsm="Seeds_Generic",
            )
        )
    return out


# Woodcutting: loose logs, vanilla multi-log stacks, firewood (improvised weapon item).
WOODCUTTING_MATERIALS = [
    _mat("log", "LogBulk", "Base.Log", "logs", "Logs", "Log", static_model="Log",
         tags="base:isfirefuel;base:log"),
    _mat("log_stacks_2", "LogStacks2Bulk", "Base.LogStacks2", "2-log stacks", "Logs2", "TwoLogsStack",
         static_model="TwoLogsStack", tags="base:isfirefuel;base:log"),
    _mat("log_stacks_3", "LogStacks3Bulk", "Base.LogStacks3", "3-log stacks", "Logs3", "ThreeLogsStack",
         static_model="ThreeLogsStack", tags="base:isfirefuel;base:log"),
    _mat("log_stacks_4", "LogStacks4Bulk", "Base.LogStacks4", "4-log stacks", "Logs4", "FourLogsStack",
         static_model="FourLogsStack", tags="base:isfirefuel;base:log"),
    _mat("firewood", "FirewoodBulk", "Base.Firewood", "firewood", "Firewood_Log"),
]

# Smithing, construction, fabric, stone, electronics, leather, misc (no drainables / weapons / heavy ores).
EXTRA_MATERIALS = [
    # --- smithing metals ---
    _mat("iron_block", "IronBlockBulk", "Base.IronBlock", "iron blocks", "IronBillet", "IronBlock", static_model="IronBlock",
         tags="base:hasmetal;base:ironmaterial;base:block;base:smeltableironlarge"),
    _mat("steel_block", "SteelBlockBulk", "Base.SteelBlock", "steel blocks", "SteelBillet", "SteelBlock", static_model="SteelBlock",
         tags="base:hasmetal;base:steelmaterial;base:block;base:smeltablesteellarge"),
    _mat("iron_chunk", "IronChunkBulk", "Base.IronChunk", "iron chunks", "IronChunk", "IronChunk", static_model="IronChunk",
         tags="base:hasmetal;base:ironmaterial;base:chunk"),
    _mat("steel_chunk", "SteelChunkBulk", "Base.SteelChunk", "steel chunks", "SteelChunk", "SteelChunk", static_model="SteelChunk",
         tags="base:hasmetal;base:steelmaterial;base:chunk"),
    _mat("iron_bar_quarter", "IronBarQuarterBulk", "Base.IronBarQuarter", "iron bar quarters", "IronBar_Quarter",
         "IronBarStockQuarter", tags="base:hasmetal;base:ironmaterial;base:barstockquarter;base:smeltableironsmall"),
    _mat("steel_bar_quarter", "SteelBarQuarterBulk", "Base.SteelBarQuarter", "steel bar quarters", "SteelBar_Quarter",
         "SteelBarStockQuarter", tags="base:hasmetal;base:steelmaterial;base:barstockquarter;base:smeltablesteelsmall"),
    _mat("iron_piece", "IronPieceBulk", "Base.IronPiece", "iron pieces", "IronBar_Tenth", "IronBarStockPiece",
         tags="base:hasmetal;base:ironmaterial;base:metalpiece"),
    _mat("steel_piece", "SteelPieceBulk", "Base.SteelPiece", "steel pieces", "SteelBar_Tenth", "SteelBarStockPiece",
         tags="base:hasmetal;base:steelmaterial;base:metalpiece"),
    _mat("pierced_iron_ingot", "PiercedIronIngotBulk", "Base.PiercedIronIngot", "pierced iron ingots", "Ingot_Iron_Hole",
         "PiercedIronIngot", static_model="PiercedIronIngot", tags="base:hasmetal;base:piercedingot;base:smeltableironlarge"),
    _mat("pierced_iron_block", "PiercedIronBlockBulk", "Base.PiercedIronBlock", "pierced iron blocks", "Billet_Iron_Hole",
         "PiercedIronBlock", tags="base:hasmetal;base:ironmaterial;base:block"),
    _mat("pierced_iron_chunk", "PiercedIronChunkBulk", "Base.PiercedIronChunk", "pierced iron chunks", "Chunk_Iron_Hole",
         "PiercedIronChunk", tags="base:hasmetal;base:ironmaterial;base:chunk"),
    _mat("pierced_steel_ingot", "PiercedSteelIngotBulk", "Base.PiercedSteelIngot", "pierced steel ingots", "Ingot_Steel_Hole",
         "PiercedSteelIngot", static_model="PiercedSteelIngot", tags="base:hasmetal;base:steelmaterial;base:piercedingot"),
    _mat("pierced_steel_block", "PiercedSteelBlockBulk", "Base.PiercedSteelBlock", "pierced steel blocks", "Billet_Steel_Hole",
         "PiercedSteelBlock", tags="base:hasmetal;base:steelmaterial;base:block"),
    _mat("pierced_steel_chunk", "PiercedSteelChunkBulk", "Base.PiercedSteelChunk", "pierced steel chunks", "Chunk_Steel_Hole",
         "PiercedSteelChunk", tags="base:hasmetal;base:steelmaterial;base:chunk"),
    _mat("brass_ingot", "BrassIngotBulk", "Base.BrassIngot", "brass ingots", "Ingot_Brass", "BrassIngot", static_model="BrassIngot",
         tags="base:hasmetal;base:ingot"),
    _mat("copper_ingot", "CopperIngotBulk", "Base.CopperIngot", "copper ingots", "Ingot_Copper", "CopperIngot", static_model="CopperIngot",
         tags="base:hasmetal;base:ingot"),
    _mat("copper_sheet", "CopperSheetBulk", "Base.CopperSheet", "copper sheets", "Sheet_Copper_Large", "CopperSheet", metal_unit=80.0),
    _mat("small_copper_sheet", "SmallCopperSheetBulk", "Base.SmallCopperSheet", "small copper sheets", "Sheet_Copper_Small",
         "SmallCopperSheet", metal_unit=20.0),
    _mat("iron_scrap", "IronScrapBulk", "Base.IronScrap", "iron scrap", "Iron_Scrap", "IronScrap", tags="base:hasmetal"),
    _mat("steel_scrap", "SteelScrapBulk", "Base.SteelScrap", "steel scrap", "Steel_Scrap", "SteelScrap", tags="base:hasmetal;base:steelmaterial"),
    _mat("copper_scrap", "CopperScrapBulk", "Base.CopperScrap", "copper scrap", "Copper_Scrap", "CopperScrap", tags="base:hasmetal"),
    _mat("aluminum_scrap", "AluminumScrapBulk", "Base.AluminumScrap", "aluminum scrap", "Aluminum_Scrap", "AluminumScrap", tags="base:hasmetal"),
    _mat("brass_scrap", "BrassScrapBulk", "Base.BrassScrap", "brass scrap", "Brass_Scrap", "BrassScrap", tags="base:hasmetal"),
    _mat("coke", "CokeBulk", "Base.Coke", "coke", "CokeCoal", "Coke", tags="base:charcoal;base:isfirefuel"),
    _mat("charcoal_crafted", "CharcoalCraftedBulk", "Base.CharcoalCrafted", "crafted charcoal", "Charcoal", "Charcoal_Ground",
         tags="base:charcoal;base:isfirefuel"),
    _mat("iron_band", "IronBandBulk", "Base.IronBand", "iron bands", "Metal_Band", "IronBand", tags="base:hasmetal;base:smeltableironlarge"),
    _mat("iron_band_small", "IronBandSmallBulk", "Base.IronBandSmall", "small iron bands", "Metal_BandSmall", "IronBandSmall",
         tags="base:hasmetal;base:smeltableironsmall"),
    _mat("steel_rod_quarter", "SteelRodQuarterBulk", "Base.SteelRodQuarter", "steel rod quarters", "SteelRod_Quarter", "SteelRodQuarter",
         tags="base:hasmetal;base:steelmaterial"),
    _mat("steel_slug", "SteelSlugBulk", "Base.SteelSlug", "steel slugs", "SteelRod_Slug", "SteelSlug", tags="base:hasmetal;base:steelmaterial"),
    # --- construction / hardware ---
    _mat("concrete_powder", "ConcretePowderBulk", "Base.ConcretePowder", "concrete powder", "Concrete_Powder", "BagofConcretePowder"),
    _mat("plaster_powder", "PlasterPowderBulk", "Base.PlasterPowder", "plaster powder", "Plaster_Powder", "BagOfPlasterPowder", survival_gear=True),
    _mat("wallpaper_paste_powder", "WallpaperPastePowderBulk", "Base.WallpaperPastePowder", "wallpaper paste powder",
         "WallpaperPastePowder", "WallpaperPastePowder", survival_gear=True),
    _mat("clay_brick", "ClayBrickBulk", "Base.ClayBrick", "clay bricks", "ClayBrick_Fired", "ClayBrick", static_model="ClayBrick"),
    _mat("clay_brick_unfired", "ClayBrickUnfiredBulk", "Base.ClayBrickUnfired", "unfired clay bricks", "ClayBrick_Unfired",
         "ClayBrickUnfired", static_model="ClayBrickUnfired"),
    _mat("nails", "NailsBulk", "Base.Nails", "nails", "Nails", "Nails", tags="base:fishinghook;base:hasmetal", survival_gear=True),
    _mat("screws", "ScrewsBulk", "Base.Screws", "screws", "Screws", "Screws", tags="base:hasmetal"),
    _mat("nuts_bolts", "NutsBoltsBulk", "Base.NutsBolts", "nuts and bolts", "NutsBolts", "NutsAndBolts", tags="base:hasmetal"),
    _mat("doorknob", "DoorknobBulk", "Base.Doorknob", "doorknobs", "DoorKnob", "DoorKnob", tags="base:hasmetal", metal_unit=10.0),
    _mat("hinge", "HingeBulk", "Base.Hinge", "hinges", "Doorhinge", "DoorHinge", tags="base:hasmetal", metal_unit=10.0),
    _mat("pipe", "PipeBulk", "Base.Pipe", "pipes", "Pipe", "PlasticPipe", display_category="Junk"),
    _mat("empty_jar", "EmptyJarBulk", "Base.EmptyJar", "empty jars", "GlassJar", "JarGlass_Ground", static_model="JarGlass_Ground",
         tags="base:glass;base:jar", display_category="Cooking", survival_gear=True),
    _mat("jar_lid", "JarLidBulk", "Base.JarLid", "jar lids", "JarLid", "LidJar", tags="base:hasmetal;base:showcondition",
         display_category="Cooking", survival_gear=True),
    # --- rope / fabric / fiber ---
    _mat("rope", "RopeBulk", "Base.Rope", "rope", "Rope2", "Rope_Looped", tags="base:rope", survival_gear=True),
    _mat("sheet_rope", "SheetRopeBulk", "Base.SheetRope", "sheet rope", "SheetRope", "SheetRope",
         tags="base:rope;base:isfirefuel;base:isfiretinder"),
    _mat("barbed_wire", "BarbedWireBulk", "Base.BarbedWire", "barbed wire", "BarbedWire", "BarbedWire",
         tags="base:hasmetal", metal_unit=20.0),
    _mat("leather_strips", "LeatherStripsBulk", "Base.LeatherStrips", "leather strips", "LeatherStrips", "LeatherStrips",
         tags="base:binding;base:isfirefuel;base:isfiretinder"),
    _mat("denim_strips", "DenimStripsBulk", "Base.DenimStrips", "denim strips", "DenimStrips", "DenimStrips",
         tags="base:binding;base:isfirefuel;base:isfiretinder"),
    _mat("ripped_sheets", "RippedSheetsBulk", "Base.RippedSheets", "ripped sheets", "Rag", "RippedSheets",
         tags="base:binding;base:isfirefuel;base:isfiretinder", display_category="Household"),
    _mat("burlap_piece", "BurlapPieceBulk", "Base.BurlapPiece", "burlap pieces", "Burlap", "BurlapPiece"),
    _mat("twigs", "TwigsBulk", "Base.Twigs", "twigs", "Twigs", "Twigs", tags="base:isfirefuel;base:isfiretinder"),
    _mat("flax_dried", "FlaxDriedBulk", "Base.FlaxDried", "dried flax", "Flax_Dried", "FlaxBundleDried"),
    _mat("flax_tow", "FlaxTowBulk", "Base.FlaxTow", "flax tow", "Flax_Tow", "FlaxTow"),
    _mat("hemp_scutched", "HempScutchedBulk", "Base.HempScutched", "scutched hemp", "Hemp_Scutched", "HempScutched"),
    _mat("wool_raw", "WoolRawBulk", "Base.WoolRaw", "raw wool", "WoolRaw", "WoolRaw_Ground"),
    _mat("animal_sinew", "AnimalSinewBulk", "Base.AnimalSinew", "animal sinew", "Sinew", "Animal_Sinew",
         display_category="AnimalPart"),
    # --- stone / flint ---
    _mat("sharped_stone", "SharpedStoneBulk", "Base.SharpedStone", "sharpened stones", "RockSharpened", "ChippedStone",
         static_model="ChippedStone", tags="base:showcondition;base:sharpknife;base:flintpiece"),
    _mat("flat_stone", "FlatStoneBulk", "Base.FlatStone", "flat stones", "FlatRock", "FlatStone", static_model="FlatStone"),
    _mat("stone_blade", "StoneBladeBulk", "Base.StoneBlade", "stone blades", "SpearHead_Stone_Crude01", "StoneSpearhead",
         static_model="StoneSpearhead", tags="base:showcondition;base:spearhead"),
    _mat("stone_blade_long", "StoneBladeLongBulk", "Base.StoneBladeLong", "long stone blades", "SpearHead_Stone_Crude02",
         "StoneSpearheadLong", static_model="StoneSpearheadLong", tags="base:showcondition;base:spearhead"),
    # --- electronics ---
    _mat("electronics_scrap", "ElectronicsScrapBulk", "Base.ElectronicsScrap", "electronics scrap", "ElectronicsScrap",
         "ElectronicsScrap", metal_unit=5.0, display_category="Electronics"),
    _mat("electric_wire", "ElectricWireBulk", "Base.ElectricWire", "electric wire", "Wires_Multicolor", "ElectricWireNew",
         tags="base:hasmetal", display_category="Electronics"),
    _mat("amplifier", "AmplifierBulk", "Base.Amplifier", "amplifiers", "Amplifier", "Amplifier", metal_unit=8.0,
         tags="base:showcondition;base:hasmetal", display_category="Electronics"),
    _mat("light_bulb", "LightBulbBulk", "Base.LightBulb", "light bulbs", "LightBulb", "LightBulb",
         tags="base:showcondition;base:hasmetal", display_category="Electronics"),
    # --- crude leather (tan, dry) ---
    _mat("leather_crude_small_tan", "LeatherCrudeSmallTanBulk", "Base.Leather_Crude_Small_Tan", "small tanned crude leather",
         "LeatherHide_CrudeTainted", "Leather_CrudeTainted_Small", tags="base:leathercrudetannedsmall"),
    _mat("leather_crude_medium_tan", "LeatherCrudeMediumTanBulk", "Base.Leather_Crude_Medium_Tan", "medium tanned crude leather",
         "LeatherHide_CrudeTainted", "Leather_CrudeTainted_Medium", tags="base:leathercrudetannedmedium"),
    _mat("leather_crude_large_tan", "LeatherCrudeLargeTanBulk", "Base.Leather_Crude_Large_Tan", "large tanned crude leather",
         "LeatherHide_CrudeTainted", "Leather_CrudeTainted", tags="base:leathercrudetannedlarge"),
    # --- misc materials ---
    _mat("ceramic_ingot_cast", "CeramicIngotCastBulk", "Base.CeramicIngotCast", "ceramic ingot casts", "CeramicCast_Bar_Fired",
         "CeramicIngotCast", static_model="CeramicIngotCast"),
    _mat("tire_piece", "TirePieceBulk", "Base.TirePiece", "tire pieces", "Tire_Quarter", "TirePiece", static_model="TirePiece",
         tags="base:isfirefuel"),
    _mat("dogbane", "DogbaneBulk", "Base.Dogbane", "dogbane", "Dogbane", "Dogbane_Ground"),
]

# Two-hand / heavy haul (RequiresEquippedBothHands and/or base:heavyitem). Same 5–100 tiers as other materials.
HEAVY_MATERIALS = [
    _mat("iron_bloom", "IronBloomBulk", "Base.IronBloom", "iron blooms", "IronBloom", "IronBloom", static_model="IronBloom",
         tags="base:hasmetal;base:heavyitem;base:ironsource"),
    _mat("iron_ore", "IronOreBulk", "Base.IronOre", "iron ore", "IronOre", "IronOre", static_model="IronOre",
         tags="base:hasmetal;base:heavyitem;base:ironore;base:ironsource"),
    _mat("copper_ore", "CopperOreBulk", "Base.CopperOre", "copper ore", "CopperOre", "CopperOre", static_model="CopperOre",
         tags="base:hasmetal;base:heavyitem;base:copperore;base:coppersource"),
    _mat("large_plank", "LargePlankBulk", "Base.LargePlank", "large planks", "RailroadTie", "RailroadTie", static_model="RailroadTie",
         tags="base:heavyitem"),
    _mat("blacksmith_anvil", "BlacksmithAnvilBulk", "Base.BlacksmithAnvil", "blacksmith anvils", "Anvil_Forged",
         "BlacksmithAnvil", static_model="BlacksmithAnvil", tags="base:hasmetal;base:heavyitem", display_category="Tool"),
    _mat("blacksmith_anvil_untreated", "BlacksmithAnvilUntreatedBulk", "Base.BlacksmithAnvilUntreated",
         "untreated blacksmith anvils", "Anvil_Forged", "BlacksmithAnvilUntreated", static_model="BlacksmithAnvilUntreated",
         tags="base:hasmetal;base:heavyitem"),
    _mat("block_anvil", "BlockAnvilBulk", "Base.BlockAnvil", "block anvils", "BlockAnvil", "BlockAnvil", static_model="BlockAnvil",
         tags="base:hasmetal;base:heavyitem", display_category="Tool"),
    _mat("block_anvil_untreated", "BlockAnvilUntreatedBulk", "Base.BlockAnvilUntreated", "untreated block anvils", "BlockAnvil",
         "BlockAnvil", static_model="BlockAnvil", tags="base:hasmetal;base:heavyitem"),
    _mat("bench_anvil", "BenchAnvilBulk", "Base.BenchAnvil", "bench anvils", "Anvil_Forged", "BenchAnvil", static_model="BenchAnvil",
         tags="base:hasmetal;base:heavyitem", display_category="Tool"),
    _mat("bench_anvil_untreated", "BenchAnvilUntreatedBulk", "Base.BenchAnvilUntreated", "untreated bench anvils", "Anvil_Forged",
         "BenchAnvilUntreated", static_model="BenchAnvilUntreated", tags="base:hasmetal;base:heavyitem"),
    _mat("stone_anvil", "StoneAnvilBulk", "Base.StoneAnvil", "stone anvils", "Anvil_Stone", "StoneAnvil",
         tags="base:heavyitem", display_category="Tool"),
    _mat("stone_wheel", "StoneWheelBulk", "Base.StoneWheel", "stone wheels", "StoneWheel", "StoneWheel_Big", tags="base:heavyitem"),
    _mat("stone_wheel_small", "StoneWheelSmallBulk", "Base.StoneWheelSmall", "small stone wheels", "StoneWheelSmall",
         "StoneWheel_Small", tags="base:heavyitem"),
    _mat("large_stone", "LargeStoneBulk", "Base.LargeStone", "large stones", "Boulder", "LargeStone", tags="base:heavyitem"),
    _mat("barricade_cube_folded", "BarricadeCubeFoldedBulk", "Base.BarricadeCube_Folded", "folded HESCO bastions",
         "HESCOBastion_Folded", "BarricadeCube_Folded"),
    _mat("heavy_chain", "HeavyChainBulk", "Base.HeavyChain", "heavy chains", "HeavyChain", "HeavyChain", static_model="HeavyChain",
         tags="base:hasmetal", display_category="Tool"),
    _mat("heavy_chain_hook", "HeavyChainHookBulk", "Base.HeavyChain_Hook", "heavy chain hooks", "HeavyChain_Hook",
         "HeavyChain_Hook", static_model="HeavyChain_Hook", tags="base:hasmetal", display_category="Tool"),
    _mat("firewood_bundle", "FirewoodBundleBulk", "Base.FirewoodBundle", "firewood bundles", "Firewood_Bundle", "FirewoodBundle",
         static_model="FirewoodBundle", tags="base:isfirefuel"),
    _mat("bucket_large_wood", "BucketLargeWoodBulk", "Base.BucketLargeWood", "large wooden buckets", "QuenchBucket_Empty",
         "BucketLargeWood", static_model="BucketLargeWood_Hand", tags="base:bucket;base:hasmetal", display_category="WaterContainer"),
    _mat("ceramic_crucible", "CeramicCrucibleBulk", "Base.CeramicCrucible", "ceramic crucibles", "Ceramic_Crucible_Fired",
         "CeramicCrucible", static_model="CeramicCrucible"),
    _mat("generator", "GeneratorBulk", "Base.Generator", "generators", "Generator", metal_unit=500.0,
         tags="base:heavyitem;base:generator;base:hasmetal;base:ignorezombiedensity;base:showcondition", display_category="Electronics"),
    _mat("generator_yellow", "GeneratorYellowBulk", "Base.Generator_Yellow", "yellow generators", "Generator2", metal_unit=500.0,
         tags="base:heavyitem;base:generator;base:hasmetal;base:ignorezombiedensity;base:showcondition", display_category="Electronics"),
    _mat("generator_blue", "GeneratorBlueBulk", "Base.Generator_Blue", "blue generators", "Generator3", metal_unit=500.0,
         tags="base:heavyitem;base:generator;base:hasmetal;base:ignorezombiedensity;base:showcondition", display_category="Electronics"),
    _mat("generator_old", "GeneratorOldBulk", "Base.Generator_Old", "old generators", "Generator4", metal_unit=500.0,
         tags="base:heavyitem;base:generator;base:hasmetal;base:ignorezombiedensity;base:showcondition", display_category="Electronics"),
    _mat("large_meteorite", "LargeMeteoriteBulk", "Base.LargeMeteorite", "large meteorites", "Meteorite", "Meteorite",
         static_model="Meteorite", tags="base:hasmetal;base:heavyitem;base:ironore;base:ironsource;base:ismemento",
         display_category="Memento"),
]

from release_candidate import RELEASE_CANDIDATE_MATERIALS
from expansion_materials import EXPANSION_MATERIALS
from food_materials import FOOD_MATERIALS

try:
    from wave2_materials import WAVE2_MATERIALS
except ImportError:
    WAVE2_MATERIALS = []

EXTRA_MATERIALS.extend(HEAVY_MATERIALS)
EXTRA_MATERIALS.extend(RELEASE_CANDIDATE_MATERIALS)
EXTRA_MATERIALS.extend(EXPANSION_MATERIALS)
EXTRA_MATERIALS.extend(WAVE2_MATERIALS)
EXTRA_MATERIALS.extend(FOOD_MATERIALS)
EXTRA_MATERIALS[:0] = WOODCUTTING_MATERIALS
