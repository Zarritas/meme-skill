# meme-skill

Marketplace de [Claude Code](https://docs.claude.com/en/docs/claude-code) con un único plugin: **meme-reply**, un hook `Stop` que muestra un meme aleatorio como link clicable al final de cada respuesta.

```
📷 [The most confusing rabbithole I stumbled upon a while back.](https://i.redd.it/...)
```

## Instalación

Desde Claude Code:

```
/plugin marketplace add Zarritas/meme-skill
/plugin install meme-reply@meme-skill
```

Reinicia Claude Code o abre nueva sesión. A partir de ahí, al final de cada respuesta verás un link al meme.

## Desinstalación

```
/plugin uninstall meme-reply@meme-skill
/plugin marketplace remove meme-skill
```

## Actualización

```
/plugin marketplace update meme-skill
```

## Cómo funciona

1. Claude Code dispara `Stop` al terminar de responder.
2. `meme_hook.py` detecta el idioma (ver abajo) y hace `GET https://meme-api.com/gimme/<subreddit>` eligiendo aleatoriamente un subreddit del idioma.
3. Emite `{"systemMessage": "📷 [título](url)"}` → Claude Code renderiza el link.
4. Si la API falla → reintenta con el endpoint genérico, y si falla del todo, emoticon de fallback. Nunca bloquea Claude (`exit 0`).

## Idiomas soportados

| Código | Subreddits |
|--------|-----------|
| `en` | memes, dankmemes, wholesomememes, me_irl |
| `es` | MemesEnEspanol, mexicomemes, yo_ELVR, chistes, redditores, ArgentinaBenderStyle, spanishmeme |
| `pt` | brasil, portugalcaralho, HUEstation, memesbrasil |
| `fr` | Rance |
| `de` | ich_iel, okoidawappler |
| `it` | italy, Italia |

**Detección de idioma** (en orden de prioridad):

1. Variable de entorno `MEME_LANG` (acepta `en`, `es`, `pt`, `fr`, `de`, `it`, o nombres como `Español`, `Français`, etc.).
2. Campo `language` de `~/.claude/settings.json` (lo que ya usas para Claude Code).
3. Default: `en`.

Para forzar un idioma, edita el `hooks/hooks.json` del plugin después de instalarlo, o setea `MEME_LANG` en tu shell antes de lanzar Claude.

## Requisitos

- Claude Code reciente (con soporte de `/plugin`).
- Python 3.10+ (solo stdlib).
- Conexión a internet para `meme-api.com`.

## Estructura del repo

```
meme-skill/
├── .claude-plugin/
│   └── marketplace.json        # catálogo del marketplace
└── plugins/
    └── meme-reply/
        ├── .claude-plugin/
        │   └── plugin.json     # manifest del plugin
        ├── hooks/
        │   └── hooks.json      # registra el Stop hook
        ├── skills/
        │   └── meme-reply/
        │       └── SKILL.md    # skill informativa
        └── meme_hook.py        # script del hook
```

## ¿Por qué no muestra el meme como imagen?

El renderer del chat de Claude Code trata `systemMessage` como **texto markdown**, no como stream raw al terminal. Eso descarta:

- **Protocolos de imagen inline** (Kitty graphics, Sixel, iTerm2): el `systemMessage` no llega al terminal subyacente.
- **ASCII art grande** (color half-blocks o Kitty base64): los mensajes mayores de ~30KB se redirigen a archivo en lugar de mostrarse en el chat.

→ La opción robusta es el **link**: pequeño, clicable, siempre funciona.

Versiones anteriores con ASCII mono/color/Kitty están en el historial de git si te interesan.

## Licencia

MIT.
