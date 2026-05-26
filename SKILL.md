---
name: meme-reply
description: Instala/desinstala un hook Stop que, al terminar cada respuesta de Claude Code, baja un meme aleatorio de meme-api.com y muestra su título como link clicable al meme original. Úsala cuando el usuario pida activar, desactivar, instalar, quitar o testear el hook de memes.
tools: Bash, Read
model: sonnet
permissionMode: default
---

# meme-reply

Hook `Stop` que decora cada turno de Claude Code con un meme aleatorio (título + link clicable a la imagen original).

## Cómo funciona

- Al terminar de responder, Claude Code dispara `Stop` y llama a `meme_hook.py`.
- `GET https://meme-api.com/gimme` → URL + título.
- Emite `{"systemMessage": "📷 [título](url)"}` → link clicable en el chat.
- Todos los errores se tragan con `exit 0` → nunca bloquea Claude.
- Solo Python stdlib, sin dependencias externas.

## Acciones soportadas

### Instalar

```bash
bash ~/.claude/skills/meme-reply/install.sh
```

Merge idempotente en `~/.claude/settings.json` (preserva el resto). Tras instalar, **reinicia Claude Code** o abre nueva sesión.

### Desinstalar

```bash
bash ~/.claude/skills/meme-reply/uninstall.sh
```

### Probar sin instalar

```bash
echo '{}' | python3 ~/.claude/skills/meme-reply/meme_hook.py
```

Debe imprimir un JSON con `systemMessage` que contenga `📷 [título](url)`.

### Ver estado

```bash
python3 -c "import json; d=json.load(open('$HOME/.claude/settings.json')); \
print([h for g in d.get('hooks',{}).get('Stop',[]) for h in g.get('hooks',[]) \
       if 'meme_hook.py' in h.get('command','')])"
```

Lista vacía → no instalado. Lista con un dict → instalado.

## Ficheros

- `meme_hook.py` — script del hook (stdlib).
- `install.sh` — registra en `settings.json`.
- `uninstall.sh` — desregistra.

## Notas

- No muestra la imagen del meme directamente. El renderer del chat trata `systemMessage` como texto markdown, no permite imágenes inline (ni Kitty graphics ni ASCII grande). La opción robusta es **link**.
- Si el usuario quiere recuperar versiones anteriores con ASCII/color/Kitty, están en el historial de git del repo.
