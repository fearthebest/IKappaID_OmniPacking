--[[
  IKappaID's Omni Packing — recipe hooks (shared SP / MP).
  OnCreate + weight refresh: server / SP / listen-server host only (IKOP_MP.isAuthority).
  OnTest: all environments (MP clients need pack menu checks).
]]

require "IKOP_Sandbox"
require "IKOP_MP"

IKOP_RecipeCode = IKOP_RecipeCode or {}

local IKOP_MODULE_PREFIX = "IKOP."

function IKOP_RecipeCode.isBulkPackItem(item)
    if not item or not item.getFullType then
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
    if item and item.getDisplayCategory then
        local category = item:getDisplayCategory()
        if category == "Food" then
            return false
        end
    end
    if item and item.getFullType then
        local fullType = item:getFullType()
        if type(fullType) == "string" and IKOP_WOODCUTTING_LOOSE[fullType] then
            return true
        end
    end
    if RecipeCodeOnTest and RecipeCodeOnTest.genericPacking then
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
    if item and item.getDisplayCategory then
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
    if not item or not item.getDisplayCategory then
        return false
    end
    if item:getDisplayCategory() ~= "Food" then
        return false
    end
    if item.getFullType then
        local fullType = item:getFullType()
        if type(fullType) == "string" and string.sub(fullType, 1, 5) ~= "Base." then
            return false
        end
    end
    if RecipeCodeOnTest and RecipeCodeOnTest.genericPacking then
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
    if not item or not item.getFullType then
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
    if RecipeCodeOnTest and RecipeCodeOnTest.genericPacking then
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
    if not item or not item.getFullType then
        return false
    end
    local fullType = item:getFullType()
    return type(fullType) == "string" and string.find(fullType, "SkillBundle", 1, true) ~= nil
end

local function maxPerUnitWeightFromConsumed(data)
    local maxPerUnit = 0.0
    if not data or not data.getAllConsumedItems then
        return maxPerUnit
    end
    local consumed = data:getAllConsumedItems()
    if not consumed then
        return maxPerUnit
    end
    for i = 0, consumed:size() - 1 do
        local item = consumed:get(i)
        if item and item.getActualWeight then
            local w = item:getActualWeight()
            if type(w) == "number" and w > 0 then
                local count = 1
                if item.getCount then
                    local c = item:getCount()
                    if type(c) == "number" and c > 0 then
                        count = c
                    end
                end
                local perUnit = w / count
                if perUnit > maxPerUnit then
                    maxPerUnit = perUnit
                end
            end
        end
    end
    return maxPerUnit
end

local function sumConsumedWeight(data)
    local total = 0.0
    local itemCount = 0
    if not data or not data.getAllConsumedItems then
        return total, itemCount
    end
    local consumed = data:getAllConsumedItems()
    if not consumed then
        return total, itemCount
    end
    for i = 0, consumed:size() - 1 do
        local item = consumed:get(i)
        if item then
            if item.getCount then
                local c = item:getCount()
                if type(c) == "number" and c > 0 then
                    itemCount = itemCount + c
                else
                    itemCount = itemCount + 1
                end
            else
                itemCount = itemCount + 1
            end
            if item.getActualWeight then
                local w = item:getActualWeight()
                if type(w) == "number" and w > 0 then
                    total = total + w
                end
            end
        end
    end
    return total, itemCount
end

local function getCreatedBulkItem(data)
    if not data or not data.getAllCreatedItems then
        return nil
    end
    local created = data:getAllCreatedItems()
    if not created or created:isEmpty() then
        return nil
    end
    return created:get(0)
end

local function applyWeightToBulk(bulk, looseWeight, stackSize, perUnitWeight)
    if not bulk then
        return
    end

    local reduction = IKOP_Sandbox.getWeightReductionFractionForBulk(bulk, perUnitWeight)
    local packedWeight = looseWeight * (1.0 - reduction)
    local minWeight = IKOP_Sandbox.getMinimumBundleWeight()
    if packedWeight < minWeight then
        packedWeight = minWeight
    end

    local md = bulk:getModData()
    if md then
        md.IKOP_looseWeight = looseWeight
        md.IKOP_packedWeight = packedWeight
        md.IKOP_reductionPercent = IKOP_Sandbox.getWeightReductionPercentIntForBulk(bulk, perUnitWeight)
        md.IKOP_stackSize = stackSize
    end

    IKOP_RecipeCode.applyStoredWeight(bulk)
end

function IKOP_RecipeCode.onCreateBulkPack(data, character)
    if not IKOP_MP.isAuthority() then
        return
    end

    local bulk = getCreatedBulkItem(data)
    if not bulk then
        return
    end

    local looseWeight, stackSize = sumConsumedWeight(data)
    if looseWeight <= 0 then
        return
    end

    local perUnitWeight = maxPerUnitWeightFromConsumed(data)
    applyWeightToBulk(bulk, looseWeight, stackSize, perUnitWeight)
end

local function resolveLooseWeight(md)
    if not md then
        return nil
    end
    local looseWeight = md.IKOP_looseWeight
    if type(looseWeight) == "number" and looseWeight > 0 then
        return looseWeight
    end
    local packedWeight = md.IKOP_packedWeight
    local oldPct = md.IKOP_reductionPercent
    if type(packedWeight) ~= "number" or packedWeight <= 0 then
        return nil
    end
    if type(oldPct) ~= "number" or oldPct < 0 or oldPct >= 90 then
        return nil
    end
    local denom = 1.0 - (oldPct / 100.0)
    if denom <= 0.01 then
        return nil
    end
    looseWeight = packedWeight / denom
    md.IKOP_looseWeight = looseWeight
    return looseWeight
end

function IKOP_RecipeCode.applyStoredWeight(item)
    if not IKOP_MP.isAuthority() then
        return
    end
    if not IKOP_RecipeCode.isBulkPackItem(item) then
        return
    end
    if not item.getModData or not item.getActualWeight or not item.setActualWeight or not item.setCustomWeight then
        return
    end

    local md = item:getModData()
    if not md then
        return
    end

    local looseWeight = resolveLooseWeight(md)
    if not looseWeight then
        return
    end

    local stackSize = md.IKOP_stackSize
    if type(stackSize) ~= "number" or stackSize <= 0 then
        stackSize = 1
    end
    local perUnitWeight = looseWeight / stackSize

    local reduction = IKOP_Sandbox.getWeightReductionFractionForBulk(item, perUnitWeight)
    local packedWeight = looseWeight * (1.0 - reduction)
    local minWeight = IKOP_Sandbox.getMinimumBundleWeight()
    if packedWeight < minWeight then
        packedWeight = minWeight
    end

    md.IKOP_looseWeight = looseWeight
    md.IKOP_packedWeight = packedWeight
    md.IKOP_reductionPercent = IKOP_Sandbox.getWeightReductionPercentIntForBulk(item, perUnitWeight)

    item:setActualWeight(packedWeight)
    item:setCustomWeight(true)

    if item.setWeight then
        item:setWeight(packedWeight)
    end
end

local function restoreContainerBulkWeights(container)
    if not container or not container.getItems then
        return
    end
    local items = container:getItems()
    if not items then
        return
    end
    for i = 0, items:size() - 1 do
        local item = items:get(i)
        if item then
            if IKOP_RecipeCode.isBulkPackItem(item) then
                IKOP_RecipeCode.applyStoredWeight(item)
            end
            if item.getInventory then
                local sub = item:getInventory()
                if sub then
                    restoreContainerBulkWeights(sub)
                end
            end
        end
    end
end

local function restorePlayerBulkWeights(player)
    if not player or not player.getInventory then
        return
    end
    restoreContainerBulkWeights(player:getInventory())
end

local function restoreOnlinePlayerBulkWeights()
    if not getNumActivePlayers or not getSpecificPlayer then
        return
    end
    local n = getNumActivePlayers()
    if type(n) ~= "number" or n < 1 then
        return
    end
    for i = 0, n - 1 do
        restorePlayerBulkWeights(getSpecificPlayer(i))
    end
end

local function onPlayerInventoryReady(playerIndex)
    if not IKOP_MP.isAuthority() then
        return
    end
    if type(playerIndex) ~= "number" then
        return
    end
    restorePlayerBulkWeights(getSpecificPlayer(playerIndex))
end

local function onContainerUpdate(container)
    if not IKOP_MP.isAuthority() then
        return
    end
    restoreContainerBulkWeights(container)
end

local lastKnownOptionsFingerprint = nil

local function syncOptionsFingerprint()
    lastKnownOptionsFingerprint = IKOP_Sandbox.getOptionsFingerprint()
end

local function onSandboxOptionsMaybeChanged()
    if not IKOP_MP.isAuthority() then
        return
    end
    if not IKOP_Sandbox.shouldRefreshBundlesOnSandboxChange() then
        syncOptionsFingerprint()
        return
    end

    local fingerprint = IKOP_Sandbox.getOptionsFingerprint()
    if lastKnownOptionsFingerprint == nil then
        lastKnownOptionsFingerprint = fingerprint
        return
    end
    if fingerprint == lastKnownOptionsFingerprint then
        return
    end
    lastKnownOptionsFingerprint = fingerprint

    restoreOnlinePlayerBulkWeights()
    if IKOP_RecipeTuning and IKOP_RecipeTuning.applyAll then
        IKOP_RecipeTuning.applyAll()
    end
end

local sandboxCheckTicks = 0
local SANDBOX_CHECK_INTERVAL = 120

local function onTickSandboxCheck()
    if not IKOP_MP.isAuthority() then
        return
    end
    sandboxCheckTicks = sandboxCheckTicks + 1
    if sandboxCheckTicks < SANDBOX_CHECK_INTERVAL then
        return
    end
    sandboxCheckTicks = 0
    onSandboxOptionsMaybeChanged()
end

if Events then
    if Events.OnGameStart then
        Events.OnGameStart.Add(function()
            if not IKOP_MP.isAuthority() then
                return
            end
            syncOptionsFingerprint()
            restoreOnlinePlayerBulkWeights()
            if IKOP_RecipeTuning and IKOP_RecipeTuning.applyAll then
                IKOP_RecipeTuning.applyAll()
            end
        end)
    end
    if Events.OnCreatePlayer then
        Events.OnCreatePlayer.Add(onPlayerInventoryReady)
    end
    if Events.OnContainerUpdate then
        Events.OnContainerUpdate.Add(onContainerUpdate)
    end
    if Events.OnTick then
        Events.OnTick.Add(onTickSandboxCheck)
    end
end
