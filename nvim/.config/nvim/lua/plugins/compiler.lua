return {
  { -- This plugin
    "Zeioth/compiler.nvim",
    cmd = { "CompilerOpen", "CompilerToggleResults", "CompilerRedo" },
    dependencies = { "stevearc/overseer.nvim", "nvim-telescope/telescope.nvim" },
    opts = {},
    keys = {
      { "<leader>dd", "<cmd>CompilerOpen<cr>", noremap = true, silent = true, desc = "Open compiler" },
      {
        "<leader>dq",
        "<cmd>CompilerToggleResults<cr>",
        noremap = true,
        silent = true,
        desc = "Toggle compiler results",
      },
      { "<leader>dQ", "<cmd>CompilerStop<cr>", noremap = true, silent = true, desc = "Stop compiler" },
    },
  },
  { -- The task runner we use
    "stevearc/overseer.nvim",
    commit = "6271cab7ccc4ca840faa93f54440ffae3a3918bd",
    cmd = { "CompilerOpen", "CompilerToggleResults", "CompilerRedo" },
    opts = {
      task_list = {
        direction = "bottom",
        min_height = 25,
        max_height = 25,
        default_detail = 1,
      },
    },
  },
}
