#!/usr/bin/env python3
"""Stop hook: emite un meme aleatorio (título + URL clicable) como systemMessage.

Diseño:
  - Detecta idioma (MEME_LANG env var, o campo `language` de ~/.claude/settings.json,
    default `en`) y elige un subreddit aleatorio de la lista de ese idioma.
  - GET https://meme-api.com/gimme/<subreddit> → URL + título del meme.
  - Emite {"systemMessage": "📷 [título](url)"} → link clicable en el chat.
  - Si falla con el subreddit elegido, reintenta una vez con el endpoint genérico.
  - Cualquier fallo se traga con exit 0 → nunca bloquea Claude.
  - Solo stdlib, sin dependencias.
"""
from __future__ import annotations

import json
import os
import random
import sys
import urllib.request

MEME_API = "https://meme-api.com/gimme"
HTTP_TIMEOUT = 4

# Subreddits curados por idioma (humor / memes generales). Validados contra
# meme-api.com — solo se incluyen los que responden con HTTP 200 y URL válida.
LANG_SUBREDDITS: dict[str, list[str]] = {
    "en": ["memes", "dankmemes", "wholesomememes", "me_irl"],
    "es": [
        "MemesEnEspanol", "mexicomemes", "yo_ELVR", "chistes",
        "redditores", "ArgentinaBenderStyle", "spanishmeme",
    ],
    "pt": ["brasil", "portugalcaralho", "HUEstation", "memesbrasil"],
    "fr": ["Rance"],
    "de": ["ich_iel", "okoidawappler"],
    "it": ["italy", "Italia"],
}

# Mapeo de nombres comunes (en cualquier capitalización) a códigos de 2 letras.
LANGUAGE_MAP: dict[str, str] = {
    "español": "es", "espanol": "es", "spanish": "es", "es": "es", "es-es": "es",
    "português": "pt", "portugues": "pt", "portuguese": "pt", "pt": "pt", "pt-pt": "pt", "pt-br": "pt",
    "français": "fr", "francais": "fr", "french": "fr", "fr": "fr", "fr-fr": "fr",
    "deutsch": "de", "german": "de", "de": "de", "de-de": "de",
    "italiano": "it", "italian": "it", "it": "it", "it-it": "it",
    "english": "en", "en": "en", "en-us": "en", "en-gb": "en",
}

FALLBACK_FACES = [
    r"¯\_(ツ)_/¯",
    r"( ͡° ͜ʖ ͡°)",
    r"ಠ_ಠ",
    r"(╯°□°)╯︵ ┻━┻",
    r"(◕‿◕)",
    r"ლ(ಠ益ಠლ)",
    r"(•_•) ( •_•)>⌐■-■ (⌐■_■)",
    r"щ(ºДºщ)",
]


def emit(system_message: str) -> None:
    sys.stdout.write(json.dumps({"systemMessage": system_message}))
    sys.stdout.flush()
    sys.exit(0)


def detect_lang() -> str:
    """Resuelve el idioma efectivo: env var → settings.json → en."""
    # 1. MEME_LANG explícito.
    raw = os.environ.get("MEME_LANG", "").strip().lower()
    if raw:
        return LANGUAGE_MAP.get(raw, "en")

    # 2. Campo `language` del settings.json del usuario.
    try:
        with open(os.path.expanduser("~/.claude/settings.json")) as f:
            settings = json.load(f)
        raw = str(settings.get("language", "")).strip().lower()
        if raw:
            return LANGUAGE_MAP.get(raw, "en")
    except Exception:
        pass

    return "en"


def _fetch(endpoint: str) -> tuple[str, str] | None:
    """Hace GET a meme-api con el endpoint dado, devuelve (title, url) o None."""
    try:
        req = urllib.request.Request(
            endpoint, headers={"User-Agent": "claude-code-meme-hook/3.0"}
        )
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        url = data.get("url")
        title = data.get("title") or "meme"
        if not url:
            return None
        return title, url
    except Exception:
        return None


def fetch_meme() -> tuple[str, str] | None:
    lang = detect_lang()
    subreddits = LANG_SUBREDDITS.get(lang, LANG_SUBREDDITS["en"])
    subreddit = random.choice(subreddits)

    result = _fetch(f"{MEME_API}/{subreddit}")
    if result:
        return result

    # Fallback: endpoint genérico (siempre en inglés).
    return _fetch(MEME_API)


def main() -> None:
    try:
        sys.stdin.read()
    except Exception:
        pass

    meme = fetch_meme()
    if meme is None:
        emit(f"🎲 meme offline {random.choice(FALLBACK_FACES)}")
        return

    title, url = meme
    emit(f"📷 [{title}]({url})")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
