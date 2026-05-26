#!/usr/bin/env python3
"""Stop hook: emite un meme aleatorio convertido a ASCII como systemMessage.

Diseño:
  - Stdin recibe el payload Stop estándar (lo ignoramos: meme aleatorio).
  - GET https://meme-api.com/gimme → URL imagen + título.
  - Si hay Pillow: descarga imagen y la convierte a ASCII.
  - Si no hay Pillow: muestra título + emoticon de fallback.
  - Salida JSON con {"systemMessage": "<ascii>"} → se renderiza al usuario.
  - Cualquier fallo se traga silenciosamente (exit 0) para no bloquear Claude.
"""
from __future__ import annotations

import json
import os
import random
import sys
import urllib.request

MEME_API = "https://meme-api.com/gimme"
# Rampa de bloques unicode, vacío → denso. Diseñada para terminal con
# fondo oscuro: píxel oscuro → " " (no brilla), píxel claro → "█" (brilla).
BLOCK_RAMP = " ░▒▓█"
ASCII_WIDTH = int(os.environ.get("MEME_WIDTH", "80"))
MAX_ROWS = int(os.environ.get("MEME_MAX_ROWS", "45"))
ASPECT = 2.2  # alto/ancho de una celda de terminal típica
HTTP_TIMEOUT = 4  # segundos
COLOR_MODE = os.environ.get("MEME_COLOR", "0") == "1"
# auto: invierte la rampa si el meme tiene fondo claro (terminal oscuro)
# off: nunca invierte. on: siempre invierte (terminal con fondo claro).
INVERT_MODE = os.environ.get("MEME_INVERT", "auto").lower()

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
    """Imprime el JSON de salida del hook Stop y termina."""
    sys.stdout.write(json.dumps({"systemMessage": system_message}))
    sys.stdout.flush()
    sys.exit(0)


def fetch_meme() -> tuple[str, str] | None:
    """Devuelve (title, image_url) o None si falla."""
    try:
        req = urllib.request.Request(
            MEME_API, headers={"User-Agent": "claude-code-meme-hook/1.0"}
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


def download_bytes(url: str) -> bytes | None:
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "claude-code-meme-hook/1.0"}
        )
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            return resp.read()
    except Exception:
        return None


def _image_to_ascii_mono(image_bytes: bytes) -> str | None:
    """Modo monocromo: bloques unicode + dithering Floyd-Steinberg.

    Mapea cada píxel a uno de 5 bloques (` ░▒▓█`). El dither de Pillow
    (en C) compensa los pocos niveles con patrón de puntos.
    """
    try:
        from PIL import Image, ImageOps  # type: ignore
        import io
    except ImportError:
        return None

    try:
        img = Image.open(io.BytesIO(image_bytes))
        # PNG con alfa → componer sobre fondo blanco para no contaminar.
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            rgba = img.convert("RGBA")
            bg.paste(rgba, mask=rgba.split()[-1])
            img = bg
        else:
            img = img.convert("RGB")

        w, h = img.size
        if w == 0 or h == 0:
            return None
        new_w = ASCII_WIDTH
        new_h = max(1, int(h * new_w / w / ASPECT))
        if new_h > MAX_ROWS:
            new_h = MAX_ROWS
        img = img.resize((new_w, new_h), Image.LANCZOS)
        img_l = img.convert("L")
        # equalize distribuye el histograma → más detalle visible que autocontrast.
        img_l = ImageOps.equalize(img_l)

        # Decidir inversión:
        # - "on": siempre invierte (terminal con fondo claro).
        # - "off": nunca.
        # - "auto" (default): invierte si el meme tiene fondo mayoritariamente claro.
        if INVERT_MODE == "on":
            invert = True
        elif INVERT_MODE == "off":
            invert = False
        else:
            mean = sum(img_l.tobytes()) / (new_w * new_h)
            invert = mean > 140
        ramp = BLOCK_RAMP[::-1] if invert else BLOCK_RAMP
        n_levels = len(ramp)

        # Construir paleta de grises uniformes (n_levels colores) y cuantizar
        # con dithering Floyd-Steinberg nativo de Pillow.
        palette = bytearray()
        for i in range(n_levels):
            g = i * 255 // (n_levels - 1)
            palette.extend([g, g, g])
        palette.extend([0] * ((256 - n_levels) * 3))
        pal_img = Image.new("P", (1, 1))
        pal_img.putpalette(palette)

        quantized = img_l.convert("RGB").quantize(
            palette=pal_img, dither=Image.FLOYDSTEINBERG
        )
        indices = quantized.tobytes()

        lines = []
        for y in range(new_h):
            row = []
            for x in range(new_w):
                idx = indices[y * new_w + x]
                if idx >= n_levels:
                    idx = n_levels - 1
                row.append(ramp[idx])
            lines.append("".join(row))
        return "\n".join(lines)
    except Exception:
        return None


def _image_to_ascii_color(image_bytes: bytes) -> str | None:
    """Modo color: half-blocks unicode + truecolor ANSI (2× resolución vertical)."""
    try:
        from PIL import Image  # type: ignore
        import io
    except ImportError:
        return None

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = img.size
        if w == 0 or h == 0:
            return None
        # Con half-blocks cada celda contiene 2 píxeles verticales → aspect 1:1.
        # Pero la altura *en filas de texto* sigue dependiendo de ASPECT del terminal.
        # Cada fila renderiza 2 píxeles verticales; queremos rows ≤ MAX_ROWS.
        new_w = ASCII_WIDTH
        new_h = max(2, int(h * new_w / w))
        if new_h % 2:
            new_h += 1
        if new_h // 2 > MAX_ROWS:
            new_h = MAX_ROWS * 2
        img = img.resize((new_w, new_h), Image.LANCZOS)
        px = img.load()

        # Run-length: solo emitir la secuencia ANSI cuando el color cambia.
        lines = []
        reset = "\x1b[0m"
        for y in range(0, new_h, 2):
            row = []
            last_fg = last_bg = None
            for x in range(new_w):
                fg = px[x, y]
                bg = px[x, y + 1]
                if fg != last_fg and bg != last_bg:
                    row.append(
                        f"\x1b[38;2;{fg[0]};{fg[1]};{fg[2]};"
                        f"48;2;{bg[0]};{bg[1]};{bg[2]}m"
                    )
                elif fg != last_fg:
                    row.append(f"\x1b[38;2;{fg[0]};{fg[1]};{fg[2]}m")
                elif bg != last_bg:
                    row.append(f"\x1b[48;2;{bg[0]};{bg[1]};{bg[2]}m")
                row.append("▀")
                last_fg, last_bg = fg, bg
            row.append(reset)
            lines.append("".join(row))
        return "\n".join(lines)
    except Exception:
        return None


def image_to_ascii(image_bytes: bytes) -> str | None:
    if COLOR_MODE:
        return _image_to_ascii_color(image_bytes)
    return _image_to_ascii_mono(image_bytes)


def main() -> None:
    # Drenar stdin (el hook lo envía aunque no lo usemos).
    try:
        sys.stdin.read()
    except Exception:
        pass

    meme = fetch_meme()
    if meme is None:
        emit(f"🎲 meme offline {random.choice(FALLBACK_FACES)}")
        return

    title, url = meme
    image_bytes = download_bytes(url)
    if image_bytes is None:
        emit(f"📷 {title}\n   (no se pudo descargar) {random.choice(FALLBACK_FACES)}")
        return

    ascii_art = image_to_ascii(image_bytes)
    if ascii_art is None:
        emit(
            f"📷 {title}\n"
            f"   {random.choice(FALLBACK_FACES)}\n"
            f"   (instala Pillow para ASCII real: pip install --user Pillow)\n"
            f"   {url}"
        )
        return

    # En modo color no envolvemos en code-block: las secuencias ANSI deben
    # llegar tal cual al terminal para que se rendericen.
    if COLOR_MODE:
        emit(f"📷 {title}\n{ascii_art}")
    else:
        emit(f"📷 {title}\n```\n{ascii_art}\n```")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Pase lo que pase, no bloquear Claude.
        sys.exit(0)
