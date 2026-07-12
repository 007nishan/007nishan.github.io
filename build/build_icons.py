# -*- coding: utf-8 -*-
"""
build_icons.py — generate SELF-HOSTED brand-logo tiles into assets/icons/.

Why self-host: shields.io returns a BLANK badge (HTTP 200 but no logo) for
trademark-restricted brands like LinkedIn, Adobe Acrobat, and Yahoo — that was
the "empty colored box" problem. Simple Icons provides the true paths; we bake
each into a rounded, brand-colored tile with a white glyph so every logo renders
identically everywhere, with no external runtime dependency.

Each tile is a 44x44 rounded square: brand-color background + white 24px logo
centered (Simple Icons paths are on a 24x24 viewBox).

The `channel` list is the single source of truth for the Connect row order,
labels (hover text), links, and brand colors.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "resume.json")
ICON_DIR = os.path.join(ROOT, "assets", "icons")

# Simple Icons path data (24x24 viewBox), fetched once and pinned here so the
# build has no network dependency. (Regenerate via the one-off fetch if needed.)
PATHS = {
    "linkedin": "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.225 0z",
    "github": "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12",
    "x": "M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z",
    "orcid": "M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 4.378c.525 0 .947.431.947.947 0 .525-.422.947-.947.947-.525 0-.946-.422-.946-.947 0-.516.421-.947.946-.947zm-.722 3.038h1.444v10.041H6.647V7.416zm3.562 0h3.9c3.712 0 5.344 2.653 5.344 5.025 0 2.578-2.016 5.025-5.325 5.025h-3.919V7.416zm1.444 1.303v7.444h2.297c3.272 0 4.022-2.484 4.022-3.722 0-2.016-1.284-3.722-4.097-3.722h-2.222z",
    "adobeacrobatreader": "M11.298 8.5c0 1.66-1.23 2.795-2.795 2.795H6.66V5.705h1.843c1.565 0 2.795 1.135 2.795 2.795zM24 3.5v17c0 1.375-1.125 2.5-2.5 2.5h-19C1.125 23 0 21.875 0 20.5v-17C0 2.125 1.125 1 2.5 1h19C22.875 1 24 2.125 24 3.5zM8.632 13.19c2.9 0 4.86-1.94 4.86-4.69 0-2.75-1.96-4.69-4.86-4.69H4.5v13.38h2.16v-4h1.972z",
    "yahoo": "M18.988 8.245h2.667l-6.442 15.51h-2.664l1.759-4.191L9.19 8.245h2.719l1.938 4.955 1.99-4.955zm-8.312 3.042L8.42 5.821H5.529l3.692 8.83-1.377 3.283h2.72l4.65-11.113h-2.717l-1.821 4.466zM2.345 0L.019 5.577h2.884L5.229 0H2.345z",
}

# Connect-row channels: (key, label/hover, brandColor, filename).
# `link` is resolved from resume.json where possible, else fixed below.
CHANNELS = [
    {"key": "portfolio",  "label": "Portfolio",     "color": "#00719A", "type": "url"},
    {"key": "cv",         "label": "Download CV",    "color": "#EC1C24", "path": "adobeacrobatreader", "type": "cv"},
    {"key": "linkedin",   "label": "LinkedIn",       "color": "#0A66C2", "path": "linkedin"},
    {"key": "github",     "label": "GitHub",         "color": "#181717", "path": "github"},
    {"key": "orcid",      "label": "ORCID",          "color": "#A6CE39", "path": "orcid"},
    {"key": "x",          "label": "X (Twitter)",    "color": "#000000", "path": "x"},
    {"key": "email",      "label": "Email",          "color": "#6001D2", "path": "yahoo"},
]

# A hand-built globe for the Portfolio tile (no clean single-path brand mark fits).
GLOBE_PATH = ("M12 2a10 10 0 100 20 10 10 0 000-20zm6.93 6h-2.95a15.7 15.7 0 00-1.38-3.56A8.03 8.03 0 0118.93 8zM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 1.91-3.96zM4.26 14a7.96 7.96 0 010-4h3.38a16.6 16.6 0 000 4H4.26zm.81 2h2.95c.32 1.25.78 2.45 1.38 3.56A7.99 7.99 0 015.07 16zm2.95-8H5.07a7.99 7.99 0 014.33-3.56A15.7 15.7 0 008.02 8zM12 19.96c-.83-1.2-1.48-2.53-1.91-3.96h3.82c-.43 1.43-1.08 2.76-1.91 3.96zM14.34 14H9.66a14.8 14.8 0 010-4h4.68a14.8 14.8 0 010 4zm.25 5.56c.6-1.11 1.06-2.31 1.38-3.56h2.95a8.03 8.03 0 01-4.33 3.56zM16.36 14a16.6 16.6 0 000-4h3.38a7.96 7.96 0 010 4h-3.38z")


def tile_svg(color, path_d):
    """A 44x44 rounded tile: brand background, white 24x24 logo centered (scaled to ~26)."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 44 44">'
        f'<rect width="44" height="44" rx="8" fill="{color}"/>'
        f'<g transform="translate(9 9) scale(1.083)" fill="#ffffff">'
        f'<path d="{path_d}"/></g></svg>'
    )


def main():
    with open(DATA, encoding="utf-8") as f:
        d = json.load(f)
    os.makedirs(ICON_DIR, exist_ok=True)
    written = []
    for ch in CHANNELS:
        if ch["key"] == "portfolio":
            path_d = GLOBE_PATH
        else:
            path_d = PATHS[ch["path"]]
        svg = tile_svg(ch["color"], path_d)
        fp = os.path.join(ICON_DIR, f"{ch['key']}.svg")
        with open(fp, "w", encoding="utf-8") as f:
            f.write(svg)
        written.append(ch["key"])
    print(f"[build_icons] wrote {len(written)} tiles to assets/icons/: {', '.join(written)}")


if __name__ == "__main__":
    main()
