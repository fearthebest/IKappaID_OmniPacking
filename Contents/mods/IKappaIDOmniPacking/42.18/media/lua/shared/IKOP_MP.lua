--[[ Back-compat alias: IKOP_MP -> IKOP_Authority ]]

require "IKOP_Authority"

IKOP_MP = IKOP_MP or {}

function IKOP_MP.isSinglePlayer()
    return IKOP_Authority.isSinglePlayer()
end

function IKOP_MP.isAuthority()
    return IKOP_Authority.isAuthority()
end

function IKOP_MP.isRemoteClient()
    return IKOP_Authority.isRemoteClient()
end

return IKOP_MP
