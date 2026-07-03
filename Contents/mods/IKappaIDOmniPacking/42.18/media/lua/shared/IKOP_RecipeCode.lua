--[[
  IKappaID Omni Packing — recipe hooks (shared SP / MP).
  OnTest: all environments (MP clients need pack menu checks).
  OnCreate: delegates to server-only IKOP_WeightAuthority.
]]

require "IKOP_Core"
require "IKOP_Sandbox"

IKOP_RecipeCode = IKOP_RecipeCode or {}

local IKOP_MODULE_PREFIX = "IKOP."

local function itemHasFn(item, name)
    return item ~= nil and type(item[name]) == "function"
end

function IKOP_RecipeCode.isBulkPackItem(item)
    if not itemHasFn(item, "getFullType") then
        return false
    end
    local fullType = item:getFullType()
    if type(fullType) ~= "string" then
        return false
    end
    return string.sub(fullType, 1, #IKOP_MODULE_PREFIX) == IKOP_MODULE_PREFIX
end

local IKOP_WOODCUTTING_LOOSE = {
    ["Base.Firewood"] = true,
}

local function isCategoryPackingEnabled(category)
    if category == "Food" then
        return IKOP_Sandbox.isFoodPackingEnabled()
    end
    return IKOP_Sandbox.isMaterialPackingEnabled()
end

function IKOP_RecipeCode.canPackLooseStack(item, character)
    if not IKOP_Sandbox.isMaterialPackingEnabled() then
        return false
    end
    if IKOP_RecipeCode.isBulkPackItem(item) then
        return false
    end
    if itemHasFn(item, "getDisplayCategory") then
        local category = item:getDisplayCategory()
        if category == "Food" then
            return false
        end
    end
    if itemHasFn(item, "getFullType") then
        local fullType = item:getFullType()
        if type(fullType) == "string" and IKOP_WOODCUTTING_LOOSE[fullType] then
            return true
        end
    end
    if RecipeCodeOnTest and type(RecipeCodeOnTest.genericPacking) == "function" then
        return RecipeCodeOnTest.genericPacking(item, character)
    end
    return true
end

local function canPackStackTier(item, character, stackSize)
    if not IKOP_Sandbox.isStackTierEnabled(stackSize) then
        return false
    end
    return IKOP_RecipeCode.canPackLooseStack(item, character)
end

function IKOP_RecipeCode.canPackStackTier5(item, character)
    return canPackStackTier(item, character, 5)
end

function IKOP_RecipeCode.canPackStackTier10(item, character)
    return canPackStackTier(item, character, 10)
end

function IKOP_RecipeCode.canPackStackTier25(item, character)
    return canPackStackTier(item, character, 25)
end

function IKOP_RecipeCode.canPackStackTier50(item, character)
    return canPackStackTier(item, character, 50)
end

function IKOP_RecipeCode.canPackStackTier100(item, character)
    return canPackStackTier(item, character, 100)
end

local function canUnstackStackTier(item, character, stackSize)
    if not IKOP_Sandbox.isStackTierEnabled(stackSize) then
        return false
    end
    if not IKOP_RecipeCode.isBulkPackItem(item) then
        return false
    end
    if itemHasFn(item, "getDisplayCategory") then
        return isCategoryPackingEnabled(item:getDisplayCategory())
    end
    return IKOP_Sandbox.isMaterialPackingEnabled()
end

function IKOP_RecipeCode.canUnstackStackTier5(item, character)
    return canUnstackStackTier(item, character, 5)
end

function IKOP_RecipeCode.canUnstackStackTier10(item, character)
    return canUnstackStackTier(item, character, 10)
end

function IKOP_RecipeCode.canUnstackStackTier25(item, character)
    return canUnstackStackTier(item, character, 25)
end

function IKOP_RecipeCode.canUnstackStackTier50(item, character)
    return canUnstackStackTier(item, character, 50)
end

function IKOP_RecipeCode.canUnstackStackTier100(item, character)
    return canUnstackStackTier(item, character, 100)
end

function IKOP_RecipeCode.canPackLooseFood(item, character)
    if not IKOP_Sandbox.isFoodPackingEnabled() then
        return false
    end
    if IKOP_RecipeCode.isBulkPackItem(item) then
        return false
    end
    if not itemHasFn(item, "getDisplayCategory") then
        return false
    end
    if item:getDisplayCategory() ~= "Food" then
        return false
    end
    if itemHasFn(item, "getFullType") then
        local fullType = item:getFullType()
        if type(fullType) == "string" and string.sub(fullType, 1, 5) ~= "Base." then
            return false
        end
    end
    if RecipeCodeOnTest and type(RecipeCodeOnTest.genericPacking) == "function" then
        return RecipeCodeOnTest.genericPacking(item, character)
    end
    return true
end

function IKOP_RecipeCode.canPackLooseSkillBook(item, character)
    if not IKOP_Sandbox.isSkillBookPackingEnabled() then
        return false
    end
    if IKOP_RecipeCode.isBulkPackItem(item) then
        return false
    end
    if not itemHasFn(item, "getFullType") then
        return false
    end
    local fullType = item:getFullType()
    if type(fullType) ~= "string" then
        return false
    end
    local name
    if string.sub(fullType, 1, 5) == "Base." then
        name = string.sub(fullType, 6)
    elseif string.sub(fullType, 1, 22) == "SkillBookExpansionB42." then
        name = string.sub(fullType, 23)
    else
        return false
    end
    if string.sub(name, -3) == "Set" and string.sub(name, 1, 4) == "Book" then
        return false
    end
    if RecipeCodeOnTest and type(RecipeCodeOnTest.genericPacking) == "function" then
        return RecipeCodeOnTest.genericPacking(item, character)
    end
    return true
end

function IKOP_RecipeCode.canUnstackSkillBookSet(item, character)
    if not IKOP_Sandbox.isSkillBookPackingEnabled() then
        return false
    end
    if not IKOP_RecipeCode.isBulkPackItem(item) then
        return false
    end
    if not itemHasFn(item, "getFullType") then
        return false
    end
    local fullType = item:getFullType()
    return type(fullType) == "string" and string.find(fullType, "SkillBundle", 1, true) ~= nil
end

function IKOP_RecipeCode.onCreateBulkPack(data, character)
    if not IKOP_WeightAuthority then
        require "IKOP_WeightAuthority"
    end
    if IKOP_WeightAuthority and type(IKOP_WeightAuthority.commitWeightFromCraft) == "function" then
        IKOP_WeightAuthority.commitWeightFromCraft(data, character)
    end
end

return IKOP_RecipeCode
