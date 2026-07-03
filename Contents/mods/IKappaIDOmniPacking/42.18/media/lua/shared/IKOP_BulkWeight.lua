--[[ Estimate bundle weight from unstack recipe when modData is missing (spawn / admin / loot). ]]

require "IKOP_Core"
require "IKOP_Sandbox"
require "IKOP_Log"

IKOP_BulkWeight = IKOP_BulkWeight or {}

local LOG = IKOP_Log
local CORE = IKOP

local function itemHasFn(item, name)
    return item ~= nil and type(item[name]) == "function"
end

local function unitWeightForFullType(fullType)
    if type(fullType) ~= "string" or fullType == "" then
        return 0
    end
    if type(instanceItem) ~= "function" then
        return 0
    end
    local inst = instanceItem(fullType)
    if not inst or type(inst.getActualWeight) ~= "function" then
        return 0
    end
    local w = inst:getActualWeight()
    if type(w) ~= "number" or w <= 0 then
        return 0
    end
    return w
end

local function scriptItemWeight(scriptItem)
    if not scriptItem then
        return 0
    end
    if type(scriptItem.getActualWeight) == "function" then
        local w = scriptItem:getActualWeight()
        if type(w) == "number" and w > 0 then
            return w
        end
    end
    if type(scriptItem.getFullName) == "function" then
        return unitWeightForFullType(scriptItem:getFullName())
    end
    return 0
end

local function parseOutputLine(originalLine)
    if type(originalLine) ~= "string" then
        return nil, nil
    end
    local amount, itemType = string.match(originalLine, "item%s+(%d+)%s+([%w%.]+)")
    if amount and itemType then
        local n = tonumber(amount)
        if n and n > 0 then
            return n, itemType
        end
    end
    return nil, nil
end

local function outputLineWeight(output)
    if not output then
        return 0, 0
    end
    local amount = 1
    if type(output.getIntAmount) == "function" then
        amount = output:getIntAmount()
    elseif type(output.getAmount) == "function" then
        amount = math.floor(output:getAmount())
    end
    if type(amount) ~= "number" or amount < 1 then
        amount = 1
    end

    local unit = 0
    if type(output.getPossibleResultItems) == "function" then
        local items = output:getPossibleResultItems()
        if items and items:size() >= 1 then
            unit = scriptItemWeight(items:get(0))
        end
    end

    if unit <= 0 and type(output.getOriginalLine) == "function" then
        local lineAmount, itemType = parseOutputLine(output:getOriginalLine())
        if lineAmount and lineAmount > 0 then
            amount = lineAmount
        end
        if itemType then
            unit = unitWeightForFullType(itemType)
        end
    end

    if unit <= 0 then
        return 0, 0
    end
    return unit * amount, amount
end

function IKOP_BulkWeight.sumUnstackRecipeOutputs(recipe)
    local totalWeight = 0
    local totalCount = 0
    if not recipe or type(recipe.getOutputs) ~= "function" then
        return totalWeight, totalCount
    end
    local outputs = recipe:getOutputs()
    if not outputs then
        return totalWeight, totalCount
    end
    for i = 0, outputs:size() - 1 do
        local w, c = outputLineWeight(outputs:get(i))
        totalWeight = totalWeight + w
        totalCount = totalCount + c
    end
    return totalWeight, totalCount
end

local function recipeNameFromScriptItem(scriptItem)
    if not scriptItem or type(scriptItem.getDoubleClickRecipe) ~= "function" then
        return nil
    end
    local name = scriptItem:getDoubleClickRecipe()
    if type(name) ~= "string" or name == "" then
        return nil
    end
    return name
end

function IKOP_BulkWeight.getUnstackRecipeName(item)
    if itemHasFn(item, "getDoubleClickRecipe") then
        local name = item:getDoubleClickRecipe()
        if type(name) == "string" and name ~= "" then
            return name
        end
    end
    if itemHasFn(item, "getScriptItem") then
        return recipeNameFromScriptItem(item:getScriptItem())
    end
    return nil
end

local function resolveUnstackRecipe(recipeName)
    if type(recipeName) ~= "string" or recipeName == "" then
        return nil
    end
    if type(getScriptManager) ~= "function" then
        return nil
    end
    local sm = getScriptManager()
    if not sm then
        return nil
    end
    if type(sm.getCraftRecipe) == "function" then
        local recipe = sm:getCraftRecipe(recipeName)
        if recipe then
            return recipe
        end
    end
    if type(sm.getRecipe) == "function" then
        return sm:getRecipe(recipeName)
    end
    return nil
end

function IKOP_BulkWeight.estimateFromItem(item)
    local recipeName = IKOP_BulkWeight.getUnstackRecipeName(item)
    if not recipeName then
        if LOG and itemHasFn(item, "getFullType") then
            LOG.logDeny("estimateFromItem", "no_recipe_name", "type=" .. tostring(item:getFullType()))
        end
        return nil, nil
    end
    local recipe = resolveUnstackRecipe(recipeName)
    if not recipe then
        if LOG then
            LOG.logDeny("estimateFromItem", "no_recipe", "name=" .. tostring(recipeName))
        end
        return nil, nil
    end
    local looseWeight, stackSize = IKOP_BulkWeight.sumUnstackRecipeOutputs(recipe)
    if type(looseWeight) ~= "number" or looseWeight <= 0 then
        if LOG then
            LOG.logDeny("estimateFromItem", "zero_loose_weight", "recipe=" .. tostring(recipeName))
        end
        return nil, nil
    end
    if type(stackSize) ~= "number" or stackSize < 1 then
        stackSize = 1
    end
    if looseWeight > CORE.LIMITS.maxBundleLooseWeight then
        return nil, nil
    end
    if stackSize > CORE.LIMITS.maxStackSize then
        stackSize = CORE.LIMITS.maxStackSize
    end
    return looseWeight, stackSize
end

function IKOP_BulkWeight.stampModData(item, looseWeight, stackSize, perUnitWeight)
    if not itemHasFn(item, "getModData") then
        return false
    end
    local md = item:getModData()
    if not md then
        return false
    end
    local reduction = IKOP_Sandbox.getWeightReductionFractionForBulk(item, perUnitWeight)
    local packedWeight = looseWeight * (1.0 - reduction)
    local minWeight = IKOP_Sandbox.getMinimumBundleWeight()
    if packedWeight < minWeight then
        packedWeight = minWeight
    end
    md.IKOP_looseWeight = looseWeight
    md.IKOP_packedWeight = packedWeight
    md.IKOP_reductionPercent = IKOP_Sandbox.getWeightReductionPercentIntForBulk(item, perUnitWeight)
    md.IKOP_stackSize = stackSize
    md.IKOP_weightSeeded = true
    return true
end

return IKOP_BulkWeight
