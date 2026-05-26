# meme-reply

Hook `Stop` de [Claude Code](https://docs.claude.com/en/docs/claude-code) que, cuando Claude termina de responder, descarga un meme aleatorio de [meme-api.com](https://meme-api.com) y lo muestra convertido a ASCII como `systemMessage`.

![preview](docs/preview.gif) <!-- opcional: añade un gif si quieres -->

## Instalación

```bash
git clone <URL_DEL_REPO> ~/.claude/skills/meme-reply
bash ~/.claude/skills/meme-reply/install.sh
```

El installer:
- Registra el hook en `~/.claude/settings.json` (merge idempotente, no toca el resto).
- Intenta instalar Pillow (`pip install --user Pillow` o equivalente en venv) para ASCII real.
- Si Pillow no puede instalarse no pasa nada: el hook usa un fallback con título + emoticon.

Después **reinicia Claude Code** o abre una sesión nueva — los hooks se cargan al arrancar.

## Desinstalación

```bash
bash ~/.claude/skills/meme-reply/uninstall.sh
```

Quita la entrada del hook de `settings.json`. No toca Pillow.

## Modos

Variables de entorno (configurables en la entry del hook):

| Var | Default | Efecto |
|-----|---------|--------|
| `MEME_COLOR` | `0` | `1` activa half-blocks unicode + truecolor ANSI (mucho mejor visual, requiere terminal con truecolor). |
| `MEME_WIDTH` | `80` | Ancho en columnas. |
| `MEME_MAX_ROWS` | `45` | Filas máximas (limita el tamaño del bloque). |
| `MEME_INVERT` | `auto` | `auto`/`on`/`off`. Para terminal con fondo claro usa `on`. |

Para activar color permanentemente edita `~/.claude/settings.json` y antepón al comando:

```json
{
  "type": "command",
  "command": "MEME_COLOR=1 /home/USUARIO/.claude/skills/meme-reply/meme_hook.py"
}
```

## Probar sin instalar

```bash
echo '{"hook_event_name":"Stop"}' \
  | python3 ~/.claude/skills/meme-reply/meme_hook.py
```

Debe emitir un JSON `{"systemMessage": "..."}`.

## Cómo funciona

- `Stop` event → ejecuta `meme_hook.py`.
- `GET https://meme-api.com/gimme` → URL imagen + título.
- **Con Pillow**:
  - Modo mono (default): bloques unicode ` ░▒▓█` + dithering Floyd-Steinberg + equalize + auto-invert.
  - Modo color: half-blocks `▀` con truecolor ANSI y run-length encoding.
- **Sin Pillow**: muestra título + emoticon ASCII + URL del meme.
- Cualquier error se traga con `exit 0` → nunca bloquea Claude.

## Requisitos

- Python 3.10+ (stdlib).
- Pillow (opcional, para ASCII real). El installer lo intenta.
- Terminal con truecolor para modo `MEME_COLOR=1` (foot, kitty, alacritty, ghostty, gnome-terminal moderno, wezterm, iTerm2).

## Ficheros

- `meme_hook.py` — script del hook.
- `install.sh` / `uninstall.sh` — registro en `settings.json`.
- `SKILL.md` — descripción para Claude Code (invocable como skill).

## Licencia

MIT.
