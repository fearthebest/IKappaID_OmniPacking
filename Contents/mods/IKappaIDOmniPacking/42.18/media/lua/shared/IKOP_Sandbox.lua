--[[
  IKappaID's Omni Packing — sandbox option readers (shared SP / MP client / server).
  Access: SandboxVars.IKappaIDOmniPacking.*
]]

IKOP_Sandbox = IKOP_Sandbox or {}

local MOD = "IKappaIDOmniPacking"

local function vars()
    if not SandboxVars or not SandboxVars.IKappaIDOmniPacking then
        return nil
    end
    return SandboxVars.IKappaIDOmniPacking
end

local function clampInt(value, defaultValue, minValue, maxValue)
    if type(value) ~= "number" then
        value = defaultValue
    end
    value = math.floor(value + 0.5)
    if value < minValue then
        return minValue
    end
    if value > maxValue then
        return maxValue
    end
    return value
end

local function clampDouble(value, defaultValue, minValue, maxValue)
    if type(value) ~= "number" then
        value = defaultValue
    end
    if value < minValue then
        return minValue
    end
    if value > maxValue then
        return maxValue
    end
    return value
end

local function boolOption(key, defaultValue)
    local v = vars()
    if not v then
        return defaultValue
    end
    local value = v[key]
    if value == nil then
        return defaultValue
    end
    return value == true
end

function IKOP_Sandbox.getMaterialsWeightReductionPercent()
    local v = vars()
    return clampInt(v and v.WeightReductionPercent, 17, 0, 90)
end

function IKOP_Sandbox.getSkillBookWeightReductionPercent()
    local v = vars()
    return clampInt(v and v.SkillBookWeightReductionPercent, 17, 0, 90)
end

function IKOP_Sandbox.getLiteratureWeightReductionPercent()
    local v = vars()
    return clampInt(v and v.LiteratureWeightReductionPercent, 17, 0, 90)
end

function IKOP_Sandbox.getFoodWeightReductionPercent()
    local v = vars()
    return clampInt(v and v.FoodWeightReductionPercent, 17, 0, 90)
end

function IKOP_Sandbox.getHeavyItemExtraReductionPercent()
    local v = vars()
    return clampInt(v and v.HeavyItemExtraReductionPercent, 0, 0, 50)
end

function IKOP_Sandbox.getHeavyItemWeightThreshold()
    local v = vars()
    return clampDouble(v and v.HeavyItemWeightThreshold, 10.0, 1.0, 40.0)
end

function IKOP_Sandbox.getMinimumBundleWeight()
    local v = vars()
    return clampDouble(v and v.MinimumBundleWeight, 0.1, 0.01, 5.0)
end

function IKOP_Sandbox.getPackTimeMultiplier()
    local v = vars()
    return clampInt(v and v.PackTimeMultiplier, 100, 25, 300)
end

function IKOP_Sandbox.getUnpackTimeMultiplier()
    local v = vars()
    return clampInt(v and v.UnpackTimeMultiplier, 100, 25, 300)
end

function IKOP_Sandbox.isMaterialPackingEnabled()
    return boolOption("EnableMaterialPacking", true)
end

function IKOP_Sandbox.isFoodPackingEnabled()
    return boolOption("EnableFoodPacking", true)
end

function IKOP_Sandbox.isSkillBookPackingEnabled()
    return boolOption("EnableSkillBookPacking", true)
end

function IKOP_Sandbox.isStackTierEnabled(stackSize)
    if type(stackSize) ~= "number" then
        return false
    end
    if stackSize == 5 then
        return boolOption("EnableStackTier5", true)
    end
    if stackSize == 10 then
        return boolOption("EnableStackTier10", true)
    end
    if stackSize == 25 then
        return boolOption("EnableStackTier25", true)
    end
    if stackSize == 50 then
        return boolOption("EnableStackTier50", true)
    end
    if stackSize == 100 then
        return boolOption("EnableStackTier100", true)
    end
    return false
end

function IKOP_Sandbox.shouldRefreshBundlesOnSandboxChange()
    return boolOption("RefreshBundlesOnSandboxChange", true)
end

function IKOP_Sandbox.shouldSortPackingMenu()
    return boolOption("SortPackingMenuByStackSize", true)
end

---@param looseWeight number|nil weight of one loose unit before stacking multiplier
function IKOP_Sandbox.getWeightReductionFractionForBulk(item, looseWeight)
    if not item or type(item.getFullType) ~= "function" then
        return IKOP_Sandbox.getMaterialsWeightReductionPercent() / 100.0
    end

    local fullType = item:getFullType()
    if type(fullType) == "string" then
        if string.find(fullType, "SkillBundle", 1, true) then
            return IKOP_Sandbox.getSkillBookWeightReductionPercent() / 100.0
        end
    end

    local category
    if type(item.getDisplayCategory) == "function" then
        category = item:getDisplayCategory()
    end
    if category == "Food" then
        return IKOP_Sandbox.getFoodWeightReductionPercent() / 100.0
    end
    if category == "Literature" or category == "SkillBook" then
        return IKOP_Sandbox.getLiteratureWeightReductionPercent() / 100.0
    end

    local pct = IKOP_Sandbox.getMaterialsWeightReductionPercent()
    local extra = IKOP_Sandbox.getHeavyItemExtraReductionPercent()
    if extra > 0 and type(looseWeight) == "number" and looseWeight > 0 then
        local perUnit = looseWeight
        if type(item.getCount) == "function" then
            local count = item:getCount()
            if type(count) == "number" and count > 0 then
                perUnit = looseWeight / count
            end
        end
        if perUnit >= IKOP_Sandbox.getHeavyItemWeightThreshold() then
            pct = pct + extra
            if pct > 90 then
                pct = 90
            end
        end
    end

    return pct / 100.0
end

function IKOP_Sandbox.getWeightReductionPercentIntForBulk(item, looseWeight)
    return math.floor(IKOP_Sandbox.getWeightReductionFractionForBulk(item, looseWeight) * 100.0 + 0.5)
end

--- Fingerprint for mid-game sandbox refresh (weight + timing + tiers).
function IKOP_Sandbox.getOptionsFingerprint()
    local v = vars()
    if not v then
        return ""
    end
    return table.concat({
        tostring(IKOP_Sandbox.getFoodWeightReductionPercent()),
        tostring(IKOP_Sandbox.getMaterialsWeightReductionPercent()),
        tostring(IKOP_Sandbox.getSkillBookWeightReductionPercent()),
        tostring(IKOP_Sandbox.getLiteratureWeightReductionPercent()),
        tostring(IKOP_Sandbox.getHeavyItemExtraReductionPercent()),
        tostring(IKOP_Sandbox.getMinimumBundleWeight()),
        tostring(IKOP_Sandbox.getPackTimeMultiplier()),
        tostring(IKOP_Sandbox.getUnpackTimeMultiplier()),
        tostring(IKOP_Sandbox.isMaterialPackingEnabled()),
        tostring(IKOP_Sandbox.isFoodPackingEnabled()),
        tostring(IKOP_Sandbox.isSkillBookPackingEnabled()),
        tostring(IKOP_Sandbox.isStackTierEnabled(5)),
        tostring(IKOP_Sandbox.isStackTierEnabled(10)),
        tostring(IKOP_Sandbox.isStackTierEnabled(25)),
        tostring(IKOP_Sandbox.isStackTierEnabled(50)),
        tostring(IKOP_Sandbox.isStackTierEnabled(100)),
    }, "|")
end
