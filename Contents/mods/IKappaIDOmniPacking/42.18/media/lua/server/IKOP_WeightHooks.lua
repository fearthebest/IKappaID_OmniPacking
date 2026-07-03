--[[ Server / SP: commit bundle weight after items enter containers (IKST giveItem, loot, ground). ]]

if type(isClient) == "function" and isClient()
    and type(isServer) == "function" and not isServer() then
    return
end

require "IKOP_Core"
require "IKOP_Log"
require "IKOP_RecipeCode"
require "IKOP_WeightAuthority"

local CORE = IKOP
local LOG = IKOP_Log
local RC = IKOP_RecipeCode
local WA = IKOP_WeightAuthority

local function isInventoryItemArg(arg)
    return arg ~= nil and type(arg.getFullType) == "function"
end

local function resolvePlayerFromContainer(container)
    if not container or type(container.getParent) ~= "function" then
        return nil
    end
    local parent = container:getParent()
    if parent and type(parent.getInventory) == "function"
        and type(parent.getPrimaryHandItem) == "function" then
        return parent
    end
    return nil
end

local function onItemAcquired(container, item, source)
    if not isInventoryItemArg(item) then
        return
    end
    if not RC.isBulkPackItem(item) then
        return
    end
    local player = resolvePlayerFromContainer(container)
    if LOG and LOG.logAction then
        LOG.logAction("weight", "acquire", string.format(
            "source=%s type=%s",
            tostring(source or "?"),
            tostring(item:getFullType())
        ))
    end
    WA.commitWeight(player, item)
end

local function installSendAddItemHook()
    if CORE._sendAddItemHooked then
        return true
    end
    if type(sendAddItemToContainer) ~= "function" then
        return false
    end
    local original = sendAddItemToContainer
    function sendAddItemToContainer(container, item)
        original(container, item)
        onItemAcquired(container, item, "sendAddItemToContainer")
    end
    CORE._sendAddItemHooked = true
    if LOG then
        LOG.logAction("hook", "sendAddItemToContainer", "installed")
    end
    return true
end

local function installContainerAddHook()
    if CORE._containerAddHooked then
        return true
    end
    if not ItemContainer or not ItemContainer.class then
        return false
    end
    if not __classmetatables then
        return false
    end
    local meta = __classmetatables[ItemContainer.class]
    if not meta or not meta.__index then
        return false
    end
    local index = meta.__index
    if not index.AddItem or index.IKOP_AddItem then
        return false
    end
    local original = index.AddItem
    index.IKOP_AddItem = original
    function index:AddItem(...)
        local result = original(self, ...)
        if CORE.runsOnServerJvm()
            and (CORE.isSinglePlayer() or not CORE._sendAddItemHooked) then
            local arg1 = ...
            if isInventoryItemArg(arg1) then
                onItemAcquired(self, arg1, "AddItem")
            elseif isInventoryItemArg(result) then
                onItemAcquired(self, result, "AddItem")
            end
        end
        return result
    end
    CORE._containerAddHooked = true
    if LOG then
        LOG.logAction("hook", "ItemContainer.AddItem", "installed")
    end
    return true
end

local function installHooks()
    local sendOk = installSendAddItemHook()
    local addOk = installContainerAddHook()
    if not sendOk and not addOk and LOG then
        LOG.logVerbose("hook", "pending", "sendAddItem=no AddItem=no")
    end
    return sendOk or addOk
end

local hookRetryTicks = 0
local HOOK_RETRY_MAX = 600

local function onWorldObjectAdded(object)
    if not object or type(object.getItem) ~= "function" then
        return
    end
    local item = object:getItem()
    if not RC.isBulkPackItem(item) then
        return
    end
    WA.commitWeight(nil, item)
end

if Events and Events.OnGameBoot then
    Events.OnGameBoot.Add(installHooks)
end
if Events and Events.OnGameStart then
    Events.OnGameStart.Add(installHooks)
end
installHooks()

if Events and Events.OnTick then
    Events.OnTick.Add(function()
        if CORE._sendAddItemHooked and CORE._containerAddHooked then
            return
        end
        hookRetryTicks = hookRetryTicks + 1
        if hookRetryTicks > HOOK_RETRY_MAX then
            return
        end
        if hookRetryTicks == 1 or hookRetryTicks == 10 or hookRetryTicks == 60
            or hookRetryTicks == 180 then
            installHooks()
        end
    end)
end

if Events and Events.OnObjectAdded then
    Events.OnObjectAdded.Add(onWorldObjectAdded)
end
