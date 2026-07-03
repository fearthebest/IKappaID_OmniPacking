--[[ Console, ring buffer, and per-category file logs under Lua/IKappaIDOmniPacking/logs/ ]]

require "IKOP_Core"
require "IKOP_Config"

IKOP_Log = IKOP_Log or {}

local CORE = IKOP
local LOG = IKOP_Log

LOG.MOD_DATA_KEY = "IKappaIDOmniPacking_Log"
LOG._ring = LOG._ring or {}

function LOG.enabled()
    return IKOP_Config.logEnabled == true
end

function LOG.verbose()
    return LOG.enabled() and IKOP_Config.logVerbose == true
end

function LOG.fileEnabled()
    return LOG.enabled() and IKOP_Config.logFileEnabled ~= false
end

function LOG.consoleEnabled()
    return LOG.enabled() and IKOP_Config.logConsoleEnabled ~= false
end

function LOG.maxRing()
    local max = tonumber(IKOP_Config.logMaxEntries) or 400
    if max < 50 then
        max = 50
    end
    if max > 2000 then
        max = 2000
    end
    return math.floor(max)
end

function LOG.jvm()
    if CORE.isListenHostClient() then
        return "listen-host"
    end
    if type(isServer) == "function" and isServer() then
        return "server"
    end
    if type(isClient) == "function" and isClient() then
        return "client"
    end
    return "sp"
end

function LOG.fileDir()
    if type(isServer) == "function" and isServer()
        and not (type(isClient) == "function" and isClient()) then
        return "IKappaIDOmniPacking/logs/server"
    end
    if LOG.jvm() == "server" then
        return "IKappaIDOmniPacking/logs/server"
    end
    return "IKappaIDOmniPacking/logs/client"
end

function LOG.field(value, maxLen)
    local text = tostring(value or "")
    text = string.gsub(text, "[\r\n|]", " ")
    maxLen = tonumber(maxLen) or 500
    if #text > maxLen then
        text = string.sub(text, 1, maxLen)
    end
    return text
end

function LOG.timestamp()
    if getTimestampMs then
        return LOG.field(getTimestampMs(), 24)
    end
    if getTimeInMillis then
        return LOG.field(getTimeInMillis(), 24)
    end
    return "0"
end

function LOG.formatLine(category, event, detail)
    return string.format(
        "ts=%s|jvm=%s|cat=%s|event=%s|detail=%s",
        LOG.timestamp(),
        LOG.jvm(),
        LOG.field(category, 24),
        LOG.field(event, 48),
        LOG.field(detail, 900)
    )
end

function LOG.writeFile(category, line)
    if not LOG.fileEnabled() then
        return
    end
    if type(getFileWriter) ~= "function" then
        return
    end
    local path = LOG.fileDir() .. "/" .. tostring(category or "debug") .. ".log"
    local writer = getFileWriter(path, true, true)
    if not writer then
        return
    end
    writer:write(tostring(line) .. "\r\n")
    writer:close()
end

function LOG.remember(line)
    local max = LOG.maxRing()
    LOG._ring[#LOG._ring + 1] = line
    while #LOG._ring > max do
        table.remove(LOG._ring, 1)
    end
    if CORE.runsOnServerJvm() and ModData and ModData.getOrCreate then
        local data = ModData.getOrCreate(LOG.MOD_DATA_KEY)
        data.entries = data.entries or {}
        data.entries[#data.entries + 1] = line
        while #data.entries > max do
            table.remove(data.entries, 1)
        end
    end
end

function LOG.write(category, event, detail)
    if not LOG.enabled() then
        return
    end
    local line = LOG.formatLine(category, event, detail)
    if LOG.consoleEnabled() and print then
        print("[" .. CORE.DISPLAY_NAME .. "] " .. line)
    end
    LOG.remember(line)
    LOG.writeFile(category or "debug", line)
end

function LOG.logVerbose(category, event, detail)
    if not LOG.verbose() then
        return
    end
    LOG.write(category or "debug", event or "verbose", detail or "")
end

function LOG.logAction(category, action, detail)
    if not LOG.enabled() then
        return
    end
    LOG.write(category or "action", action or "action", detail or "")
end

function LOG.logDeny(event, reason, detail)
    if not LOG.enabled() then
        return
    end
    LOG.write("deny", event or "deny", string.format(
        "reason=%s %s",
        LOG.field(reason or "?", 120),
        LOG.field(detail or "", 400)
    ))
end

function LOG.boot(message)
    LOG.write("boot", "load", (message or "mod loaded") .. " v" .. tostring(CORE.VERSION))
end

function LOG.localTail(count)
    count = math.floor(tonumber(count) or 60)
    local out = {}
    local ring = LOG._ring or {}
    local start = math.max(1, #ring - count + 1)
    for i = start, #ring do
        out[#out + 1] = ring[i]
    end
    return out
end

return LOG
