--[[ Boot-time loose/stack lookup per IKOP bulk fullType (spawn / admin / loot fallback). ]]

require "IKOP_Core"
require "IKOP_BulkWeight"
require "IKOP_Log"

IKOP_WeightTable = IKOP_WeightTable or {}

local CORE = IKOP
local BWT = IKOP_BulkWeight
local LOG = IKOP_Log
local TABLE = IKOP_WeightTable

local entries = {}
local built = false

local IKOP_PREFIX = "IKOP."

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

local function entryFromRecipeName(fullType, recipeName)
    local recipe = resolveUnstackRecipe(recipeName)
    if not recipe then
        return nil
    end
    local looseWeight, stackSize = BWT.sumUnstackRecipeOutputs(recipe)
    if type(looseWeight) ~= "number" or looseWeight <= 0 then
        return nil
    end
    if type(stackSize) ~= "number" or stackSize < 1 then
        stackSize = 1
    end
    if looseWeight > CORE.LIMITS.maxBundleLooseWeight then
        return nil
    end
    if stackSize > CORE.LIMITS.maxStackSize then
        stackSize = CORE.LIMITS.maxStackSize
    end
    return {
        loose = looseWeight,
        stack = stackSize,
    }
end

local function entryFromScriptItem(scriptItem)
    if not scriptItem or type(scriptItem.getFullName) ~= "function" then
        return nil
    end
    local fullType = scriptItem:getFullName()
    if type(fullType) ~= "string" or string.sub(fullType, 1, #IKOP_PREFIX) ~= IKOP_PREFIX then
        return nil
    end
    if type(scriptItem.getDoubleClickRecipe) ~= "function" then
        return nil
    end
    local recipeName = scriptItem:getDoubleClickRecipe()
    if type(recipeName) ~= "string" or recipeName == "" then
        return nil
    end
    return entryFromRecipeName(fullType, recipeName)
end

function TABLE.isBuilt()
    return built
end

function TABLE.get(fullType)
    if type(fullType) ~= "string" then
        return nil
    end
    return entries[fullType]
end

function TABLE.getLooseAndStack(fullType)
    local entry = TABLE.get(fullType)
    if not entry then
        return nil, nil
    end
    return entry.loose, entry.stack
end

local function collectBulkScriptItems()
    local list = {}
    if type(getScriptManager) ~= "function" then
        return list
    end
    local sm = getScriptManager()
    if not sm then
        return list
    end

    if type(sm.getItemsTag) == "function" then
        local tagged = nil
        if ItemTag and ResourceLocation and type(ItemTag.get) == "function" then
            tagged = sm:getItemsTag(ItemTag.get(ResourceLocation.of("ikop:bulk")))
        end
        local taggedEmpty = not tagged
        if not taggedEmpty and type(tagged.isEmpty) == "function" then
            taggedEmpty = tagged:isEmpty()
        elseif not taggedEmpty and tagged.size and type(tagged.size) == "function" then
            taggedEmpty = tagged:size() < 1
        end
        if taggedEmpty and type(sm.getItemsTag) == "function" then
            tagged = sm:getItemsTag("ikop:bulk")
        end
        if tagged and tagged.size and tagged.get then
            for i = 0, tagged:size() - 1 do
                list[#list + 1] = tagged:get(i)
            end
        end
    end

    if #list < 1 and type(sm.getAllItems) == "function" then
        local allItems = sm:getAllItems()
        if allItems and allItems.size and allItems.get then
            for i = 0, allItems:size() - 1 do
                local scriptItem = allItems:get(i)
                if scriptItem and type(scriptItem.getFullName) == "function" then
                    local fullType = scriptItem:getFullName()
                    if type(fullType) == "string"
                        and string.sub(fullType, 1, #IKOP_PREFIX) == IKOP_PREFIX then
                        list[#list + 1] = scriptItem
                    end
                end
            end
        end
    end

    return list
end

local function countEntries()
    local n = 0
    for _ in pairs(entries) do
        n = n + 1
    end
    return n
end

function TABLE.build()
    entries = {}
    built = false
    local scriptItems = collectBulkScriptItems()
    local count = 0
    for i = 1, #scriptItems do
        local scriptItem = scriptItems[i]
        local entry = entryFromScriptItem(scriptItem)
        if entry and scriptItem and type(scriptItem.getFullName) == "function" then
            local fullType = scriptItem:getFullName()
            if type(fullType) == "string" and not entries[fullType] then
                entries[fullType] = entry
                count = count + 1
            end
        end
    end
    built = true
    if LOG and LOG.logAction then
        LOG.logAction("weight", "table", string.format("built entries=%d", count))
        local plank = entries["IKOP.PlankBulk100"]
        if plank then
            LOG.logAction("weight", "table_sample", string.format(
                "PlankBulk100 loose=%.2f stack=%d",
                plank.loose,
                plank.stack
            ))
        end
    end
end

local buildRetryTicks = 0
local BUILD_RETRY_MAX = 300

local function tryBuildTable()
    if built and countEntries() > 0 then
        return
    end
    TABLE.build()
end

if Events and Events.OnGameStart then
    Events.OnGameStart.Add(tryBuildTable)
end

if Events and Events.OnTick then
    Events.OnTick.Add(function()
        if countEntries() > 0 then
            return
        end
        buildRetryTicks = buildRetryTicks + 1
        if buildRetryTicks > BUILD_RETRY_MAX then
            return
        end
        if buildRetryTicks == 1 or buildRetryTicks == 30 or buildRetryTicks == 120 then
            tryBuildTable()
        end
    end)
end

return TABLE
