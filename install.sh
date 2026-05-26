#!/usr/bin/env bash
# Registra el hook meme-reply en ~/.claude/settings.json (merge idempotente).
# Sin dependencias externas — solo Python stdlib.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_PATH="$SCRIPT_DIR/meme_hook.py"
SETTINGS="${HOME}/.claude/settings.json"

if [ ! -f "$HOOK_PATH" ]; then
  echo "meme-reply: no se encuentra $HOOK_PATH" >&2
  exit 1
fi

mkdir -p "$(dirname "$SETTINGS")"
if [ ! -f "$SETTINGS" ]; then
  echo "{}" > "$SETTINGS"
fi

python3 - "$SETTINGS" "$HOOK_PATH" <<'PY'
import json, sys
settings_path, hook_path = sys.argv[1], sys.argv[2]
with open(settings_path) as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError:
        print(f"meme-reply: settings.json no es JSON válido: {settings_path}", file=sys.stderr)
        sys.exit(1)

hooks = data.setdefault("hooks", {})
stop = hooks.setdefault("Stop", [])

# Buscar entrada existente del meme-hook (por path del comando).
already = False
for group in stop:
    for h in group.get("hooks", []):
        if h.get("type") == "command" and "meme_hook.py" in h.get("command", ""):
            h["command"] = hook_path  # actualizar path (quita env vars antiguas)
            already = True

if not already:
    stop.append({
        "hooks": [{"type": "command", "command": hook_path}],
    })

with open(settings_path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")

print(f"meme-reply: hook {'actualizado' if already else 'registrado'} en {settings_path}")
PY

echo "meme-reply: listo. Reinicia Claude Code o abre una nueva sesión para activarlo."
