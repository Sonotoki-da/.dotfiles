-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

local dap = require("dap")

-- Add a function to toggle justMyCode
local function toggle_justMyCode()
  local current_config = dap.configurations.python[1] -- Assuming you're using the first config
  current_config.justMyCode = not current_config.justMyCode
  print("justMyCode is now " .. tostring(current_config.justMyCode))
end

-- Create a command to call the toggle function
vim.api.nvim_create_user_command("ToggleJustMyCode", toggle_justMyCode, {})

-- Example usage in keymappings:
-- Add this to your which-key or other keymapping config
vim.keymap.set("n", "<leader>dm", ":ToggleJustMyCode<CR>")
