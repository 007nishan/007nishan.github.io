# -*- coding: utf-8 -*-
"""
build_icons.py — generate SELF-HOSTED brand-logo tiles into assets/icons/.

Why self-host: shields.io returns a BLANK badge for trademark-restricted brands
(LinkedIn, Adobe, Yahoo). We bake each logo into a rounded brand-colored tile
with a white glyph so every tile renders identically everywhere, offline.

IMPORTANT: the brand paths below are the EXACT Simple Icons path data (verified
by length against the upstream SVGs) — never hand-approximated. Portfolio (globe),
CV (document+download) and Email (envelope) use simple, unambiguous custom marks
that always render cleanly (avoids the multi-subpath brand-logo distortion).

Order of CHANNELS = the Connect-row display order.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ICON_DIR = os.path.join(ROOT, "assets", "icons")

# key -> (hover label, brand color, path key)
CHANNELS = [
    ("portfolio", "Portfolio",   "#00719A"),
    ("cv",        "Download CV",  "#A70E13"),
    ("linkedin",  "LinkedIn",     "#0A66C2"),
    ("github",    "GitHub",       "#181717"),
    ("orcid",     "ORCID",        "#A6CE39"),
    ("x",         "X (Twitter)",  "#000000"),
    ("email",     "Email",        "#0A66C2"),
]

PATHS = {
    "portfolio": "M12 2a10 10 0 100 20 10 10 0 000-20zm6.93 6h-2.95a15.7 15.7 0 00-1.38-3.56A8.03 8.03 0 0118.93 8zM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 1.91-3.96zM4.26 14a7.96 7.96 0 010-4h3.38a16.6 16.6 0 000 4H4.26zm.81 2h2.95c.32 1.25.78 2.45 1.38 3.56A7.99 7.99 0 015.07 16zm2.95-8H5.07a7.99 7.99 0 014.33-3.56A15.7 15.7 0 008.02 8zM12 19.96c-.83-1.2-1.48-2.53-1.91-3.96h3.82c-.43 1.43-1.08 2.76-1.91 3.96zM14.34 14H9.66a14.8 14.8 0 010-4h4.68a14.8 14.8 0 010 4zm.25 5.56c.6-1.11 1.06-2.31 1.38-3.56h2.95a8.03 8.03 0 01-4.33 3.56zM16.36 14a16.6 16.6 0 000-4h3.38a7.96 7.96 0 010 4h-3.38z",
    "cv": "M6 2h8l6 6v14a2 2 0 01-2 2H6a2 2 0 01-2-2V4a2 2 0 012-2zm7 1.5V9h5.5L13 3.5zM12 11a1 1 0 00-1 1v4.6l-1.8-1.8-1.4 1.4L12 20l4.2-3.8-1.4-1.4L13 16.6V12a1 1 0 00-1-1z",
    "linkedin": "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z",
    "github": "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12",
    "orcid": "M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 4.378c.525 0 .947.431.947.947s-.422.947-.947.947a.95.95 0 0 1-.947-.947c0-.525.422-.947.947-.947zm-.722 3.038h1.444v10.041H6.647V7.416zm3.562 0h3.9c3.712 0 5.344 2.653 5.344 5.025 0 2.578-2.016 5.025-5.325 5.025h-3.919V7.416zm1.444 1.303v7.444h2.297c3.272 0 4.022-2.484 4.022-3.722 0-2.016-1.284-3.722-4.097-3.722h-2.222z",
    "x": "M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z",
    "email": "M2 4h20a1 1 0 011 1v14a1 1 0 01-1 1H2a1 1 0 01-1-1V5a1 1 0 011-1zm10 7L3.2 5.5h17.6L12 11zm-9 1.2V18.5l5.4-4.3L3 12.2zm18 0l-5.4 2L21 18.5v-6.3zM12 13.3l-2.9-1.9L4.4 19h15.2l-4.7-5.6L12 13.3z"
}


def tile_svg(color, path_d):
    """A 44x44 rounded tile: brand background + white 24x24 glyph centered."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 44 44">'
        f'<rect width="44" height="44" rx="8" fill="{color}"/>'
        f'<g transform="translate(9 9) scale(1.083)" fill="#ffffff">'
        f'<path d="{path_d}"/></g></svg>'
    )


def main():
    os.makedirs(ICON_DIR, exist_ok=True)
    written = []
    for key, _label, color in CHANNELS:
        svg = tile_svg(color, PATHS[key])
        with open(os.path.join(ICON_DIR, f"{key}.svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        written.append(key)
    print(f"[build_icons] wrote {len(written)} tiles to assets/icons/: {', '.join(written)}")


if __name__ == "__main__":
    main()
