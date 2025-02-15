export PATH=$PATH:~/.local/scripts
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin

bindkey -s "^[f" "tmux-sessionizer^M"

alias hibernate="systemctl hibernate"
alias zigdev="~/.zig/zig"

md2docx() {
    pandoc -t latex "$1" | pandoc -f latex --data-dir=docs/rendering/ -o "${2:-$(basename "$1" .md).docx}"
}

