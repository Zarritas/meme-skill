#!/usr/bin/env bash
# Quita el hook meme-reply de ~/.claude/settings.json.
set -euo pipefail

SETTINGS="${HOME}/.claude/settings.json"
if [ ! -f "$SETTINGS" ]; then
  echo "meme-reply: $SETTINGS no existe, nada que hacer"
  exit 0
fi

python3 - "$SETTINGS" <<'PY'
import json, sys
settings_path = sys.argv[1]
with open(settings_path) as f:
    data = json.load(f)

hooks = data.get("hooks", {})
stop = hooks.get("Stop", [])
removed = 0
new_stop = []
for group in stop:
    kept = [h for h in group.get("hooks", []) if not (
        h.get("type") == "command" and h.get("command", "").endswith("meme_hook.py")
    )]
    removed += len(group.get("hooks", [])) - len(kept)
    if kept:
        new_group = dict(group)
        new_group["hooks"] = kept
        new_stop.append(new_group)

if new_stop:
    hooks["Stop"] = new_stop
elif "Stop" in hooks:
    del hooks["Stop"]
if not hooks and "hooks" in data:
    del data["hooks"]

with open(settings_path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")

print(f"meme-reply: {removed} entrada(s) eliminadas de {settings_path}")
PY
