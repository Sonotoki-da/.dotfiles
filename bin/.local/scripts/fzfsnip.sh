selected="$(python ./snippets.py | fzf -i -e)"

echo -e "$selected" | sed -e 's/.*-- //' | wl-copy
