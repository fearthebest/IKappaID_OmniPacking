--[[
  Apply pack/unpack recipe times from sandbox multipliers (OnGameStart + sandbox changes).
]]

require "IKOP_Sandbox"
require "IKOP_MP"

IKOP_RecipeTuning = IKOP_RecipeTuning or {}

local function stackSizeFromRecipeName(name)
    if type(name) ~= "string" then
        return nil
    end
    local suffix = string.match(name, "_(%d+)$")
    return tonumber(suffix)
end

local function setRecipeTime(recipe, ticks)
    if not recipe or type(ticks) ~= "number" then
        return
    end
    ticks = math.max(1, math.floor(ticks + 0.5))
    if recipe.setTime then
        recipe:setTime(ticks)
    end
end

local function tuneRecipe(recipe)
    if not recipe or not recipe.getName then
        return
    end
    local name = recipe:getName()
    if type(name) ~= "string" then
        return
    end

    if string.sub(name, 1, 11) == "ikop_stack_" then
        local size = stackSizeFromRecipeName(name)
        if not size then
            return
        end
        local base = 80 + size * 2
        setRecipeTime(recipe, base * IKOP_Sandbox.getPackTimeMultiplier() / 100.0)
        return
    end

    if string.sub(name, 1, 13) == "ikop_unstack_" then
        setRecipeTime(recipe, 80 * IKOP_Sandbox.getUnpackTimeMultiplier() / 100.0)
        return
    end

    if string.sub(name, 1, 15) == "ikop_pack_books_" then
        setRecipeTime(recipe, 100 * IKOP_Sandbox.getPackTimeMultiplier() / 100.0)
        return
    end

    if string.sub(name, 1, 17) == "ikop_unstack_books_" then
        setRecipeTime(recipe, 80 * IKOP_Sandbox.getUnpackTimeMultiplier() / 100.0)
    end
end

function IKOP_RecipeTuning.applyAll()
    if not IKOP_MP.isAuthority() then
        return
    end
    if not CraftRecipeManager or not CraftRecipeManager.getRecipe then
        return
    end

    local names = {
        "ikop_stack_logs_005", "ikop_stack_logs_010", "ikop_stack_logs_025", "ikop_stack_logs_050", "ikop_stack_logs_100",
        "ikop_unstack_logs_005",
        "ikop_pack_books_carpentry", "ikop_unstack_books_carpentry",
    }

    for i = 1, #names do
        tuneRecipe(CraftRecipeManager.getRecipe(names[i]))
    end

    if CraftRecipeManager.getAllRecipes then
        local all = CraftRecipeManager.getAllRecipes()
        if all then
            for j = 0, all:size() - 1 do
                local recipe = all:get(j)
                if recipe and recipe.getName then
                    local name = recipe:getName()
                    if type(name) == "string" and string.sub(name, 1, 4) == "ikop" then
                        tuneRecipe(recipe)
                    end
                end
            end
        end
    end
end

if Events and Events.OnGameStart then
    Events.OnGameStart.Add(IKOP_RecipeTuning.applyAll)
end
