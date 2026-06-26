--[[
  IKappaID's Omni Packing — sort bulk-pack options on the item context submenu.

  B42 fills that submenu via ISInventoryPaneContextMenu.addNewCraftingDynamicalContextMenu
  in recipe-list order from CraftRecipeManager (not by recipe id or display name).
]]

require "IKOP_Sandbox"

IKOP_ContextMenu = {}

---@param recipe CraftRecipe|nil
---@return number|nil
function IKOP_ContextMenu.getStackSizeFromRecipe(recipe)
    if not recipe then
        return nil
    end
    local getName = recipe.getName
    if type(getName) ~= "function" then
        return nil
    end
    local name = getName(recipe)
    if type(name) ~= "string" then
        return nil
    end
    if string.sub(name, 1, 11) ~= "ikop_stack_" then
        return nil
    end
    local suffix = string.match(name, "_(%d+)$")
    if not suffix then
        return nil
    end
    local n = tonumber(suffix)
    if not n or n < 1 then
        return nil
    end
    return n
end

---@param recipeList ArrayList
---@return ArrayList
function IKOP_ContextMenu.sortRecipeList(recipeList)
    if not recipeList or recipeList:size() <= 1 then
        return recipeList
    end
    if not IKOP_Sandbox.shouldSortPackingMenu() then
        return recipeList
    end

    local hasIkopStack = false
    for i = 0, recipeList:size() - 1 do
        if IKOP_ContextMenu.getStackSizeFromRecipe(recipeList:get(i)) then
            hasIkopStack = true
            break
        end
    end
    if not hasIkopStack then
        return recipeList
    end

    local sorted = {}
    for i = 0, recipeList:size() - 1 do
        sorted[#sorted + 1] = recipeList:get(i)
    end

    table.sort(sorted, function(a, b)
        local sizeA = IKOP_ContextMenu.getStackSizeFromRecipe(a)
        local sizeB = IKOP_ContextMenu.getStackSizeFromRecipe(b)
        if sizeA and sizeB then
            if sizeA ~= sizeB then
                return sizeA < sizeB
            end
        elseif sizeA then
            return true
        elseif sizeB then
            return false
        end
        local nameA = a:getName()
        local nameB = b:getName()
        if Translator and Translator.getRecipeName and string.sort then
            return string.sort(Translator.getRecipeName(nameA), Translator.getRecipeName(nameB))
        end
        return nameA < nameB
    end)

    local out = ArrayList.new()
    for i = 1, #sorted do
        out:add(sorted[i])
    end
    return out
end

local function installContextMenuSort()
    if not ISInventoryPaneContextMenu or not ISInventoryPaneContextMenu.addNewCraftingDynamicalContextMenu then
        return
    end
    if ISInventoryPaneContextMenu.IKOP_addNewCraftingDynamicalContextMenu then
        return
    end
    ISInventoryPaneContextMenu.IKOP_addNewCraftingDynamicalContextMenu =
        ISInventoryPaneContextMenu.addNewCraftingDynamicalContextMenu

    function ISInventoryPaneContextMenu.addNewCraftingDynamicalContextMenu(selectedItem, context, recipeList, player, containerList)
        local ordered = IKOP_ContextMenu.sortRecipeList(recipeList)
        ISInventoryPaneContextMenu.IKOP_addNewCraftingDynamicalContextMenu(
            selectedItem, context, ordered, player, containerList
        )
    end
end

if Events and Events.OnGameBoot then
    Events.OnGameBoot.Add(installContextMenuSort)
else
    installContextMenuSort()
end
