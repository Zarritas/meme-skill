#!/usr/bin/env python3
"""Stop hook: emite un meme aleatorio (título + URL clicable) como systemMessage.

Diseño:
  - GET https://meme-api.com/gimme → URL + título del meme.
  - Emite {"systemMessage": "📷 [título](url)"} → link clicable en el chat.
  - Cualquier fallo se traga con exit 0 → nunca bloquea Claude.
  - Solo stdlib, sin dependencias.
"""
from __future__ import annotations

import json
import random
import sys
import urllib.request

MEME_API = "https://meme-api.com/gimme"
HTTP_TIMEOUT = 4

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


def fetch_meme() -> tuple[str, str] | None:
    try:
        req = urllib.request.Request(
            MEME_API, headers={"User-Agent": "claude-code-meme-hook/2.0"}
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
