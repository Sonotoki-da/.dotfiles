import os

with open(os.path.expanduser("~") + "/snippets.md", encoding="utf-8") as f:
    data = f.read()

for snippet in data.split("\n\n")[:-1]:
    s = snippet.split("\n")
    print(f"{s[0]} -- {s[1]}")
