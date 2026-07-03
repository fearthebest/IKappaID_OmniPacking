require "IKOP_Core"
require "IKOP_Config"
require "IKOP_Authority"
require "IKOP_Log"

local CORE = IKOP
local LOG = IKOP_Log

if CORE.runsOnServerJvm() then
    LOG.boot("shared bootstrap (server JVM)")
elseif CORE.isRemoteClient() then
    LOG.boot("shared bootstrap (remote client)")
else
    LOG.boot("shared bootstrap (local client / SP)")
end
