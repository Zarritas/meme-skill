---
name: meme-reply
description: Instala/desinstala un hook Stop que, al terminar cada respuesta de Claude Code, baja un meme aleatorio de meme-api.com y lo muestra convertido a ASCII como systemMessage. Úsala cuando el usuario pida activar, desactivar, instalar, quitar, configurar o testear el hook de memes.
tools: Bash, Read
model: sonnet
permissionMode: default
---

# meme-reply

Hook `Stop` que decora cada turno de Claude Code con un meme aleatorio en ASCII.

## Cómo funciona

- Al terminar de responder, Claude Code dispara `Stop` y llama a `meme_hook.py`.
- El script hace `GET https://meme-api.com/gimme` (meme aleatorio).
- Si **Pillow** está instalado → descarga la imagen y la convierte a ASCII (60 cols, rampa ` .:-=+*#%@`).
- Si no → muestra el título del meme + un emoticon de fallback + URL.
- Emite `{"systemMessage": "<ascii>"}` → Claude Code lo renderiza al usuario.
- Cualquier error se traga silenciosamente con `exit 0` (nunca bloquea Claude).

## Acciones soportadas

Cuando se invoque la skill, el usuario suele querer una de estas operaciones. Ejecuta solo la pedida.

### Instalar

```bash
bash ~/.claude/skills/meme-reply/install.sh
```

- Merge idempotente del hook en `~/.claude/settings.json` (preserva el resto).
- Intenta `pip install --user Pillow` (silencioso si falla — el hook tiene fallback).
- Flag `--no-pillow` para saltarse la instalación de Pillow.

Tras instalar avisa al usuario: **hay que reiniciar Claude Code o abrir nueva sesión** para que cargue los hooks.

### Desinstalar

```bash
bash ~/.claude/skills/meme-reply/uninstall.sh
```

Quita la entrada del hook de `settings.json`. No desinstala Pillow.

### Probar sin instalar

```bash
echo '{"session_id":"x","transcript_path":"/tmp/x","cwd":"'$PWD'","permission_mode":"default","hook_event_name":"Stop"}' \
  | python3 ~/.claude/skills/meme-reply/meme_hook.py
```

Debe imprimir un JSON con `systemMessage` que contiene el ASCII (o el fallback).

### Ver estado

```bash
python3 -c "import json; d=json.load(open('$HOME/.claude/settings.json')); \
print([h for g in d.get('hooks',{}).get('Stop',[]) for h in g.get('hooks',[]) \
       if h.get('command','').endswith('meme_hook.py')])"
```

Lista vacía → no instalado. Lista con un dict → instalado.

## Ficheros

- `meme_hook.py` — el script del hook (Python stdlib + Pillow opcional).
- `install.sh` — registra el hook + instala Pillow.
- `uninstall.sh` — desregistra el hook.

## Portabilidad

- Solo requiere `python3` (stdlib). Pillow es opcional.
- Path absoluto del hook se resuelve en `install.sh` con `$HOME` del usuario que lo ejecuta → válido para cualquier cuenta.
- No requiere root (instala Pillow con `pip --user`).

## Cuándo NO usarla

- Si el usuario quiere personalizar el origen del meme (carpeta local, otra API), avisa de que la skill actualmente usa solo `meme-api.com` y hay que editar `MEME_API` en `meme_hook.py`.
- Si el usuario quiere mapeo según contenido de la respuesta (no random), avisa de que esa decisión se rechazó al diseñar y habría que reabrirla.
