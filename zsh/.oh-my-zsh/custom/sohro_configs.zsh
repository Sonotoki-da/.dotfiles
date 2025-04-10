export PATH=$PATH:~/.local/scripts
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin

bindkey -s "^[f" "tmux-sessionizer^M"

alias hibernate="systemctl hibernate"
alias zigdev="~/.zig/zig"

md2docx() {
    pandoc "$1" \
        --from=markdown_strict \
        --to=docx \
        --wrap=none \
        --markdown-headings=atx \
        --data-dir=docs/rendering/ \
        -o "${2:-$(basename "$1" .md).docx}"
}
export EDITOR=nvim
