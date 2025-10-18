export PATH=$PATH:~/.local/scripts
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin

bindkey -s "^[f" "tmux-sessionizer^M"

alias hibernate="systemctl hibernate"
alias zigdev="~/Projects/zig/build-release/stage3/bin/zig"
alias nvimdev="NVIM_APPNAME='zigvim' ~/Projects/neovim/zig-out/bin/nvim"

md2docx() {
    pandoc --from=markdown-smart --data-dir=docs/rendering/ -o "${2:-$(basename "$1" .md).docx}" "$1"
}
export EDITOR=nvim
