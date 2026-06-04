---
name: meme-reply
description: Información y prueba del hook meme-reply. Úsala cuando el usuario pida probar el meme, ver estado del hook, o entender qué hace este plugin. La instalación y desinstalación se gestionan con `/plugin install` y `/plugin uninstall`, no desde aquí.
tools: Bash, Read
model: sonnet
permissionMode: default
---

# meme-reply

Este plugin añade un hook `Stop` que, al terminar cada respuesta de Claude Code, descarga un meme aleatorio de [meme-api.com](https://meme-api.com) y muestra su título como **link clicable** al meme original.

## Cómo funciona

- Claude Code dispara el evento `Stop` al terminar de responder.
- El hook detecta idioma (`MEME_LANG` → `language` de settings.json → `en`) y elige un subreddit aleatorio de la lista de ese idioma.
- `GET https://meme-api.com/gimme/<subreddit>` → si falla, reintento con endpoint genérico.
- Emite `{"systemMessage": "📷 [título](url)"}` que Claude Code renderiza como link.
- Todos los errores se tragan con `exit 0` → nunca bloquea Claude.
- Solo Python stdlib, sin dependencias externas.

### Idiomas

Soportados: `en`, `es`, `pt`, `fr`, `de`, `it`. Configurables con la variable de entorno `MEME_LANG` (también acepta nombres como `Español`, `Français`). Por defecto se detecta del `language` de tu `~/.claude/settings.json`.

## Acciones

### Probar el hook manualmente

```bash
echo '{}' | python3 "${CLAUDE_PLUGIN_ROOT}/meme_hook.py"
```

Debe imprimir un JSON como `{"systemMessage": "📷 [título](url)"}`.

### Gestión del plugin

Se hace desde Claude Code, no desde esta skill:

- **Instalar**: `/plugin install meme-reply@meme-skill`
- **Desinstalar**: `/plugin uninstall meme-reply@meme-skill`
- **Actualizar**: `/plugin marketplace update meme-skill`

## Por qué solo muestra link y no imagen

El chat de Claude Code renderiza `systemMessage` como **texto markdown**, no como stream raw al terminal. Eso descarta protocolos de imagen inline (Kitty graphics, Sixel) y limita el ASCII grande (los mensajes mayores de ~30KB se redirigen a archivo). Un link clicable es pequeño, robusto y funciona siempre.
