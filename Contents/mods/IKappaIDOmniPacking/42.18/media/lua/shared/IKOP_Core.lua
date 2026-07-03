--[[ IKappaID Omni Packing — module constants and JVM helpers ]]

IKOP = IKOP or {}

local CORE = IKOP

CORE.MOD_ID = "IKappaIDOmniPacking"
CORE.MODULE = "IKappaIDOmniPacking"
CORE.DISPLAY_NAME = "IKappaID Omni Packing"
CORE.VERSION = "0.0.10"

CORE.LIMITS = {
    maxBundleLooseWeight = 10000,
    maxStackSize = 100,
    maxReductionPercent = 90,
}

function CORE.text(key, fallback, ...)
    if getText and key then
        local translated = getText(key, ...)
        if translated and translated ~= "" and translated ~= key then
            return translated
        end
    end
    if select("#", ...) > 0 and fallback then
        return string.format(tostring(fallback), ...)
    end
    return tostring(fallback or key or "")
end

function CORE.log(message)
    if print then
        print("[" .. CORE.DISPLAY_NAME .. "] " .. tostring(message))
    end
end

function CORE.isSinglePlayer()
    if type(isClient) ~= "function" or type(isServer) ~= "function" then
        return true
    end
    return not isClient() and not isServer()
end

function CORE.isRemoteClient()
    if type(isClient) ~= "function" or type(isServer) ~= "function" then
        return false
    end
    return isClient() and not isServer()
end

function CORE.isListenHostClient()
    if type(isClient) ~= "function" or type(isServer) ~= "function" then
        return false
    end
    return isClient() and isServer()
end

function CORE.runsOnServerJvm()
    if type(isServer) == "function" and isServer() then
        return true
    end
    return CORE.isSinglePlayer()
end

return CORE
