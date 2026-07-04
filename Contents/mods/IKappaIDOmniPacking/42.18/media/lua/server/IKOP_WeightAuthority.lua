--[[ Server / SP only: compute bundle weight, stamp modData, vanilla sync. Clients do nothing. ]]

if type(isClient) == "function" and isClient()
    and type(isServer) == "function" and not isServer() then
    return
end

require "IKOP_Core"
require "IKOP_Sandbox"
require "IKOP_Authority"
require "IKOP_Log"
require "IKOP_BulkWeight"
require "IKOP_WeightTable"
require "IKOP_RecipeCode"

IKOP_WeightAuthority = IKOP_WeightAuthority or {}

local CORE = IKOP
local AUTH = IKOP_Authority
local LOG = IKOP_Log
local BWT = IKOP_BulkWeight
local WTBL = IKOP_WeightTable
local RC = IKOP_RecipeCode
local WA = IKOP_WeightAuthority

local function itemHasFn(item, name)
    return item ~= nil and type(item[name]) == "function"
end

local function isValidLooseWeight(weight)
    if type(weight) ~= "number" or weight <= 0 then
        return false
    end
    return weight <= CORE.LIMITS.maxBundleLooseWeight
end

local function isValidStackSize(stackSize)
    if type(stackSize) ~= "number" or stackSize < 1 then
        return false
    end
    return stackSize <= CORE.LIMITS.maxStackSize
end

local function resolvePlayerForItem(item)
    if not item or not itemHasFn(item, "getContainer") then
        return nil
    end
    local container = item:getContainer()
    if not container or not itemHasFn(container, "getParent") then
        return nil
    end
    local parent = container:getParent()
    if parent and type(parent.getInventory) == "function"
        and type(parent.getPrimaryHandItem) == "function" then
        return parent
    end
    return nil
end

local function resolvePlayer(player, item)
    if player and type(player.getInventory) == "function" then
        return player
    end
    return resolvePlayerForItem(item)
end

local function finishWeightSync(player, item)
    if not item then
        return
    end
    if itemHasFn(item, "syncItemFields") then
        item:syncItemFields()
    end
    player = resolvePlayer(player, item)
    if type(syncItemFields) == "function" and player then
        syncItemFields(player, item)
    end
    if type(syncItemModData) == "function" and player then
        syncItemModData(player, item)
    end
    if type(sendItemStats) == "function" then
        sendItemStats(item)
    end
    local container = nil
    if itemHasFn(item, "getContainer") then
        container = item:getContainer()
    end
    if container and itemHasFn(container, "setDrawDirty") then
        container:setDrawDirty(true)
    end
end

local function applyPackedWeightToItem(item, packedWeight)
    item:setActualWeight(packedWeight)
    item:setCustomWeight(true)
    if itemHasFn(item, "setWeight") then
        item:setWeight(packedWeight)
    end
end

local function resolveLooseWeight(md)
    if not md then
        return nil
    end
    local looseWeight = md.IKOP_looseWeight
    if isValidLooseWeight(looseWeight) then
        return looseWeight
    end
    local packedWeight = md.IKOP_packedWeight
    local oldPct = md.IKOP_reductionPercent
    if type(packedWeight) ~= "number" or packedWeight <= 0 then
        return nil
    end
    if type(oldPct) ~= "number" or oldPct < 0 or oldPct > CORE.LIMITS.maxReductionPercent then
        return nil
    end
    local denom = 1.0 - (oldPct / 100.0)
    if denom <= 0.01 then
        return nil
    end
    looseWeight = packedWeight / denom
    if not isValidLooseWeight(looseWeight) then
        return nil
    end
    md.IKOP_looseWeight = looseWeight
    return looseWeight
end

local function weightAlreadyCommitted(item, packedWeight)
    if not itemHasFn(item, "isCustomWeight") or not item:isCustomWeight() then
        return false
    end
    if not itemHasFn(item, "getActualWeight") then
        return false
    end
    local actual = item:getActualWeight()
    if type(actual) ~= "number" then
        return false
    end
    return math.abs(actual - packedWeight) <= 0.05
end

local function lookupLooseAndStack(item, looseWeight, stackSize)
    if isValidLooseWeight(looseWeight) and isValidStackSize(stackSize) then
        return looseWeight, stackSize
    end
    if itemHasFn(item, "getModData") then
        local md = item:getModData()
        if md then
            local loose = resolveLooseWeight(md)
            local stack = md.IKOP_stackSize
            if isValidLooseWeight(loose) and isValidStackSize(stack) then
                return loose, stack
            end
        end
    end
    if itemHasFn(item, "getFullType") then
        local fullType = item:getFullType()
        if WTBL and type(WTBL.getLooseAndStack) == "function" then
            local loose, stack = WTBL.getLooseAndStack(fullType)
            if isValidLooseWeight(loose) and isValidStackSize(stack) then
                return loose, stack
            end
            if WTBL.isBuilt and type(WTBL.isBuilt) == "function"
                and WTBL.build and type(WTBL.build) == "function"
                and not WTBL.isBuilt() then
                WTBL.build()
                loose, stack = WTBL.getLooseAndStack(fullType)
                if isValidLooseWeight(loose) and isValidStackSize(stack) then
                    return loose, stack
                end
            end
        end
        if BWT and type(BWT.estimateFromItem) == "function" then
            local loose, stack = BWT.estimateFromItem(item)
            if isValidLooseWeight(loose) and isValidStackSize(stack) then
                return loose, stack
            end
        end
    end
    return nil, nil
end

function WA.commitWeight(player, item, opts)
    if not AUTH.guardServerMutate() then
        return false
    end
    if not item or not RC.isBulkPackItem(item) then
        return false
    end
    if not itemHasFn(item, "getModData")
        or not itemHasFn(item, "setActualWeight")
        or not itemHasFn(item, "setCustomWeight") then
        return false
    end

    opts = opts or {}
    local looseWeight, stackSize = lookupLooseAndStack(item, opts.looseWeight, opts.stackSize)
    if not isValidLooseWeight(looseWeight) or not isValidStackSize(stackSize) then
        if LOG and itemHasFn(item, "getFullType") then
            LOG.logDeny("commitWeight", "lookup_failed", "type=" .. tostring(item:getFullType()))
        end
        return false
    end

    local perUnitWeight = opts.perUnitWeight
    if type(perUnitWeight) ~= "number" or perUnitWeight <= 0 then
        perUnitWeight = looseWeight / stackSize
    end

    local reduction = IKOP_Sandbox.getWeightReductionFractionForBulk(item, perUnitWeight)
    local packedWeight = looseWeight * (1.0 - reduction)
    local minWeight = IKOP_Sandbox.getMinimumBundleWeight()
    if packedWeight < minWeight then
        packedWeight = minWeight
    end

    if weightAlreadyCommitted(item, packedWeight) then
        local md = item:getModData()
        if md and type(md.IKOP_packedWeight) == "number"
            and math.abs(md.IKOP_packedWeight - packedWeight) <= 0.05 then
            return true
        end
    end

    if not BWT.stampModData(item, looseWeight, stackSize, perUnitWeight) then
        return false
    end

    applyPackedWeightToItem(item, packedWeight)
    player = resolvePlayer(player, item)
    finishWeightSync(player, item)

    if LOG and itemHasFn(item, "getFullType") and itemHasFn(item, "getActualWeight") then
        local displayWeight = item:getActualWeight()
        local scriptWeight = itemHasFn(item, "getWeight") and item:getWeight() or -1
        local itemId = itemHasFn(item, "getID") and item:getID() or "?"
        LOG.logAction("weight", "commit", string.format(
            "type=%s id=%s packed=%.2f actual=%.2f script=%.2f custom=%s",
            tostring(item:getFullType()),
            tostring(itemId),
            packedWeight,
            displayWeight,
            scriptWeight,
            tostring(itemHasFn(item, "isCustomWeight") and item:isCustomWeight() or false)
        ))
    end
    return true
end

local function maxPerUnitWeightFromConsumed(data)
    local maxPerUnit = 0.0
    if not data or type(data.getAllConsumedItems) ~= "function" then
        return maxPerUnit
    end
    local consumed = data:getAllConsumedItems()
    if not consumed then
        return maxPerUnit
    end
    for i = 0, consumed:size() - 1 do
        local consumedItem = consumed:get(i)
        if consumedItem and itemHasFn(consumedItem, "getActualWeight") then
            local w = consumedItem:getActualWeight()
            if type(w) == "number" and w > 0 then
                local count = 1
                if itemHasFn(consumedItem, "getCount") then
                    local c = consumedItem:getCount()
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
    if not data or type(data.getAllConsumedItems) ~= "function" then
        return total, itemCount
    end
    local consumed = data:getAllConsumedItems()
    if not consumed then
        return total, itemCount
    end
    for i = 0, consumed:size() - 1 do
        local consumedItem = consumed:get(i)
        if consumedItem then
            if itemHasFn(consumedItem, "getCount") then
                local c = consumedItem:getCount()
                if type(c) == "number" and c > 0 then
                    itemCount = itemCount + c
                else
                    itemCount = itemCount + 1
                end
            else
                itemCount = itemCount + 1
            end
            if itemHasFn(consumedItem, "getActualWeight") then
                local w = consumedItem:getActualWeight()
                if type(w) == "number" and w > 0 then
                    total = total + w
                end
            end
        end
    end
    return total, itemCount
end

local function getCreatedBulkItem(data)
    if not data or type(data.getAllCreatedItems) ~= "function" then
        return nil
    end
    local created = data:getAllCreatedItems()
    if not created or created:isEmpty() then
        return nil
    end
    return created:get(0)
end

function WA.commitWeightFromCraft(data, character)
    if not AUTH.guardServerMutate() then
        if LOG then
            LOG.logVerbose("deny", "commitWeightFromCraft", "remote client")
        end
        return false
    end

    local bulk = getCreatedBulkItem(data)
    if not bulk then
        return false
    end

    local looseWeight, stackSize = sumConsumedWeight(data)
    if not isValidLooseWeight(looseWeight) then
        LOG.logDeny("commitWeightFromCraft", "invalid_loose_weight", "weight=" .. tostring(looseWeight))
        return false
    end
    if not isValidStackSize(stackSize) then
        LOG.logDeny("commitWeightFromCraft", "invalid_stack_size", "size=" .. tostring(stackSize))
        return false
    end

    local perUnitWeight = maxPerUnitWeightFromConsumed(data)
    local ok = WA.commitWeight(character, bulk, {
        looseWeight = looseWeight,
        stackSize = stackSize,
        perUnitWeight = perUnitWeight,
    })

    if ok and LOG and itemHasFn(bulk, "getFullType") then
        local packed = 0
        local md = itemHasFn(bulk, "getModData") and bulk:getModData() or nil
        if md and type(md.IKOP_packedWeight) == "number" then
            packed = md.IKOP_packedWeight
        end
        LOG.logAction("pack", "create", string.format(
            "type=%s loose=%.2f stack=%d packed=%.2f",
            tostring(bulk:getFullType()),
            looseWeight,
            stackSize,
            packed
        ))
    end
    return ok
end

local function restoreContainerBulkWeights(container, player)
    if not container or type(container.getItems) ~= "function" then
        return
    end
    local items = container:getItems()
    if not items then
        return
    end
    for i = 0, items:size() - 1 do
        local item = items:get(i)
        if item then
            if RC.isBulkPackItem(item) then
                WA.commitWeight(player, item)
            end
            if itemHasFn(item, "getInventory") then
                local sub = item:getInventory()
                if sub then
                    restoreContainerBulkWeights(sub, player)
                end
            end
        end
    end
end

local function restorePlayerBulkWeights(player)
    if not player or type(player.getInventory) ~= "function" then
        return
    end
    restoreContainerBulkWeights(player:getInventory(), player)
end

local function restoreOnlinePlayerBulkWeights()
    if type(getNumActivePlayers) ~= "function" or type(getSpecificPlayer) ~= "function" then
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
    if not AUTH.guardServerMutate() then
        return
    end
    if type(playerIndex) ~= "number" then
        return
    end
    restorePlayerBulkWeights(getSpecificPlayer(playerIndex))
end

local function resolveItemContainer(object)
    if not object then
        return nil
    end
    if object.getItems and not object.getContainer then
        return object
    end
    if object.getContainer then
        return object:getContainer()
    end
    return nil
end

local function onContainerUpdate(object)
    if not AUTH.guardServerMutate() then
        return
    end
    local container = resolveItemContainer(object)
    if container then
        restoreContainerBulkWeights(container, nil)
    end
end

local lastKnownOptionsFingerprint = nil

local function syncOptionsFingerprint()
    lastKnownOptionsFingerprint = IKOP_Sandbox.getOptionsFingerprint()
end

local function onSandboxOptionsMaybeChanged()
    if not AUTH.guardServerMutate() then
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

    LOG.logAction("sandbox", "refresh", "bundle weights + recipe times")
    restoreOnlinePlayerBulkWeights()
    if IKOP_RecipeTuning and type(IKOP_RecipeTuning.applyAll) == "function" then
        IKOP_RecipeTuning.applyAll()
    end
end

local sandboxCheckTicks = 0
local SANDBOX_CHECK_INTERVAL = 120

local function onTickSandboxCheck()
    if not AUTH.guardServerMutate() then
        return
    end
    sandboxCheckTicks = sandboxCheckTicks + 1
    if sandboxCheckTicks < SANDBOX_CHECK_INTERVAL then
        return
    end
    sandboxCheckTicks = 0
    onSandboxOptionsMaybeChanged()
end

local weightScanTicks = 0
local WEIGHT_SCAN_INTERVAL = 60

local function getOpenedContainerForLocalPlayer()
    if not ISInventoryPage or not ISInventoryPage.getContainers then
        return nil
    end
    if not getPlayer then
        return nil
    end
    local playerObj = getPlayer()
    if not playerObj or not playerObj.getPlayerNum then
        return nil
    end
    local page = ISInventoryPage.getContainers(playerObj:getPlayerNum())
    if not page or not page.getInventory then
        return nil
    end
    return page:getInventory()
end

local function onTickBulkWeightScan()
    if not AUTH.guardServerMutate() then
        return
    end
    weightScanTicks = weightScanTicks + 1
    if weightScanTicks % WEIGHT_SCAN_INTERVAL ~= 0 then
        return
    end
    restoreOnlinePlayerBulkWeights()
    local opened = getOpenedContainerForLocalPlayer()
    if opened then
        restoreContainerBulkWeights(opened, nil)
    end
end

if Events then
    if Events.OnGameStart then
        Events.OnGameStart.Add(function()
            if not AUTH.guardServerMutate() then
                return
            end
            if WTBL and type(WTBL.build) == "function" and not WTBL.isBuilt() then
                WTBL.build()
            end
            syncOptionsFingerprint()
            restoreOnlinePlayerBulkWeights()
            if IKOP_RecipeTuning and type(IKOP_RecipeTuning.applyAll) == "function" then
                IKOP_RecipeTuning.applyAll()
            end
            LOG.logAction("boot", "refresh", "player bundle weights")
        end)
    end
    if Events.OnCreatePlayer then
        Events.OnCreatePlayer.Add(onPlayerInventoryReady)
    end
    if Events.OnContainerUpdate then
        Events.OnContainerUpdate.Add(onContainerUpdate)
    end
    if Events.OnFillContainer then
        Events.OnFillContainer.Add(function(_roomType, _containerType, container)
            if AUTH.guardServerMutate() then
                restoreContainerBulkWeights(container, nil)
            end
        end)
    end
    if Events.OnTick then
        Events.OnTick.Add(onTickSandboxCheck)
        Events.OnTick.Add(onTickBulkWeightScan)
    end
end

return WA
