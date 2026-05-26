#!/usr/bin/env bash
# Instala el hook meme-reply en ~/.claude/settings.json (merge idempotente)
# y opcionalmente Pillow vía pip --user para ASCII real.
#
# Uso:
#   bash install.sh             # registra hook + intenta instalar Pillow
#   bash install.sh --no-pillow # solo registra hook
set -euo pipefail

WANT_PILLOW=1
for arg in "$@"; do
  case "$arg" in
    --no-pillow) WANT_PILLOW=0 ;;
  esac
done

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
import json, sys, os
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
        if h.get("type") == "command" and h.get("command", "").endswith("meme_hook.py"):
            h["command"] = hook_path  # actualizar path por si cambió
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

if [ "$WANT_PILLOW" -eq 1 ]; then
  # Si Pillow ya está disponible, no hacemos nada.
  if python3 -c "import PIL" 2>/dev/null; then
    echo "meme-reply: Pillow ya disponible ✓"
  else
    echo "meme-reply: instalando Pillow (opcional, para ASCII real)..."
    # Detectar venv: en venv no se usa --user. Fuera de venv, sí.
    IN_VENV=$(python3 -c "import sys; print(1 if sys.prefix != sys.base_prefix else 0)")
    if [ "$IN_VENV" = "1" ]; then
      PIP_ARGS=()
    else
      PIP_ARGS=(--user)
    fi
    if python3 -m pip install "${PIP_ARGS[@]}" --quiet Pillow 2>/tmp/meme-reply-pip.log; then
      echo "meme-reply: Pillow instalado ✓"
    elif python3 -m pip install "${PIP_ARGS[@]}" --break-system-packages --quiet Pillow 2>>/tmp/meme-reply-pip.log; then
      # Fallback PEP 668 (Debian/Ubuntu modernos).
      echo "meme-reply: Pillow instalado (con --break-system-packages) ✓"
    else
      echo "meme-reply: no se pudo instalar Pillow (el hook usará fallback). Log: /tmp/meme-reply-pip.log" >&2
    fi
  fi
fi

echo "meme-reply: listo. Reinicia Claude Code o abre una nueva sesión para activarlo."
