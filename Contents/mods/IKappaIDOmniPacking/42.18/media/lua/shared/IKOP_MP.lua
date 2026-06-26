--[[
  IKappaID's Omni Packing — multiplayer authority helpers (B42).
  Server and single-player may mutate item weight; remote clients do not.
  See https://pzwiki.net/wiki/Networking
]]

IKOP_MP = IKOP_MP or {}

function IKOP_MP.isSinglePlayer()
    return not isClient() and not isServer()
end

--- True when this machine may set bundle weight (dedicated server, SP, or listen-server host).
function IKOP_MP.isAuthority()
    if isClient() and not isServer() then
        return false
    end
    return isServer() or IKOP_MP.isSinglePlayer()
end

function IKOP_MP.isRemoteClient()
    return isClient() and not isServer()
end
