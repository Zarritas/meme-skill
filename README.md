# meme-reply

Hook `Stop` para [Claude Code](https://docs.claude.com/en/docs/claude-code) que, cuando Claude termina de responder, descarga un meme aleatorio de [meme-api.com](https://meme-api.com) y muestra su título como **link clicable** al meme original.

```
📷 [The most confusing rabbithole I stumbled upon a while back.](https://i.redd.it/...)
```

## Instalación

```bash
git clone https://github.com/Zarritas/meme-skill ~/.claude/skills/meme-reply
bash ~/.claude/skills/meme-reply/install.sh
```

Después **reinicia Claude Code** o abre una sesión nueva.

## Desinstalación

```bash
bash ~/.claude/skills/meme-reply/uninstall.sh
```

## Cómo funciona

1. Claude Code dispara el evento `Stop` al terminar de responder.
2. `meme_hook.py` hace `GET https://meme-api.com/gimme`.
3. Emite `{"systemMessage": "📷 [título](url)"}` que Claude Code renderiza como link.
4. Si la API falla → emoticon de fallback. Nunca bloquea Claude (todos los errores se tragan con `exit 0`).

## Requisitos

- Python 3.10+ (solo stdlib).
- Conexión a internet.

## ¿Por qué no muestra el meme como imagen?

Porque el chat de Claude Code renderiza `systemMessage` como **texto markdown**, no como stream raw al terminal. Eso descarta:

- **Protocolos de imagen inline** (Kitty graphics, Sixel, iTerm2): los `systemMessage` no pasan al terminal subyacente, se renderizan dentro del chat.
- **ASCII art** (color o mono): aunque ANSI básico sí pasa por algún canal, el `systemMessage` tiene límite de tamaño (~10–30KB). Un meme convertido a half-blocks color pesa ~70KB → se redirige a archivo. Mono cabría pero la calidad visual es pobre.

→ La opción robusta es **link**: pequeño, clicable, siempre funciona.

## Ficheros

- `meme_hook.py` — script del hook (Python stdlib, sin dependencias).
- `install.sh` / `uninstall.sh` — registro idempotente en `~/.claude/settings.json`.
- `SKILL.md` — descripción para Claude Code (invocable como skill).

## Licencia

MIT.
