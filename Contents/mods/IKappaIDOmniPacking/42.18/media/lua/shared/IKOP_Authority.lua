--[[ Server / SP / listen-host may mutate bundle weight; remote clients read synced items only. ]]

require "IKOP_Core"

IKOP_Authority = IKOP_Authority or {}

local CORE = IKOP
local AUTH = IKOP_Authority

function AUTH.mayMutateWorldState()
    if CORE.isRemoteClient() then
        return false
    end
    return CORE.runsOnServerJvm()
end

function AUTH.guardServerMutate()
    return AUTH.mayMutateWorldState()
end

function AUTH.isAuthority()
    return AUTH.mayMutateWorldState()
end

function AUTH.isRemoteClient()
    return CORE.isRemoteClient()
end

function AUTH.isSinglePlayer()
    return CORE.isSinglePlayer()
end

return AUTH
