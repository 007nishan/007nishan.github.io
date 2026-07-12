# -*- coding: utf-8 -*-
"""
build_readme.py — generate a professional, standardized README.md from
data/resume.json.

The README is part of the chain (generated from the SSOT, cross-links every
presence) — NOT a stand-alone hand-edited file. It is CV/profile-facing only:
it never mentions the build pipeline, LinkedIn strategy, or internal planning.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "resume.json")
OUT = os.path.join(ROOT, "README.md")

_MONTHS = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May",
           "06": "Jun", "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct",
           "11": "Nov", "12": "Dec"}


def _fmt_month(value):
    """'2022-09' -> 'Sep 2022'; '2016' -> '2016'; '' -> ''."""
    if not value:
        return ""
    parts = str(value).split("-")
    if len(parts) >= 2 and parts[1] in _MONTHS:
        return f"{_MONTHS[parts[1]]} {parts[0]}"
    return parts[0]

# Shields.io badge config per network: (label, color, logo).
BADGE = {
    "LinkedIn": ("LinkedIn", "0A66C2", "linkedin"),
    "GitHub": ("GitHub", "181717", "github"),
    "ORCID": ("ORCID", "A6CE39", "orcid"),
    "X": ("X", "000000", "x"),
}


def badge(profile):
    # Pure HTML (not markdown) so it renders reliably inside <p align="center">.
    label, color, logo = BADGE.get(profile["network"], (profile["network"], "555", ""))
    logo_part = f"&logo={logo}&logoColor=white" if logo else ""
    img = f"https://img.shields.io/badge/{label}-{color}?style=for-the-badge{logo_part}"
    return (f'<a href="{profile["url"]}"><img alt="{label}" '
            f'src="{img}"></a>')


# Base URL for the self-hosted logo tiles (raw so they render in BOTH repos —
# the profile repo can't use relative paths). Points at the site repo.
ICONS_RAW = "https://raw.githubusercontent.com/007nishan/007nishan.github.io/main/assets/icons"

# Connect row: (icon file key, hover label, link-resolver). Order = display order.
CONNECT = [
    ("portfolio", "Portfolio", "site"),
    ("cv",        "Download CV (PDF)", "cv"),
    ("linkedin",  "LinkedIn",  "LinkedIn"),
    ("github",    "GitHub",    "GitHub"),
    ("orcid",     "ORCID",     "ORCID"),
    ("x",         "X (Twitter)", "X"),
    ("email",     "Email",     "email"),
]


def _icon_ver(key):
    """Short content hash of an icon file, appended as ?v= so GitHub's image
    proxy (camo) fetches the current logo instead of a cached one."""
    import hashlib
    fp = os.path.join(ROOT, "assets", "icons", f"{key}.svg")
    try:
        with open(fp, "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()[:8]
    except FileNotFoundError:
        return "1"


def connect_tile(key, label, url):
    """Clickable self-hosted logo tile with a hover tooltip (title attr).
    No text label, no visible URL — just the logo; hover shows the name."""
    return (f'<a href="{url}" title="{label}">'
            f'<img alt="{label}" title="{label}" height="40" '
            f'src="{ICONS_RAW}/{key}.svg?v={_icon_ver(key)}"></a>')


def build(d):
    b = d["basics"]
    site = b["url"]
    profiles = b["profiles"]
    by_net = {p["network"]: p for p in profiles}

    L = []

    # --- Header ---
    L.append(f"<h1 align=\"center\">{b['name']}</h1>")
    L.append(f"<p align=\"center\"><em>{b['label']}</em></p>")
    L.append("")

    # --- Badge row (cross-links every presence) ---
    L.append('<p align="center">')
    L.append("  " + " ".join(badge(p) for p in profiles))
    L.append("</p>")
    L.append("")
    # Absolute URLs so this README renders correctly in BOTH repos
    # (007nishan.github.io AND the 007nishan/007nishan profile repo).
    # NOTE: no emoji anywhere — brand LOGO badges (above) carry the color;
    # headings rely on GitHub's native h2 rule + typography. This keeps the
    # look consistent across all platforms and screen readers (no tofu glyphs).
    cv_pdf = site.rstrip("/") + "/Nishanur_Rahman_CV.pdf"
    L.append('<p align="center">')
    L.append(f'  <a href="{site}"><strong>Portfolio &amp; CV</strong></a> &nbsp;·&nbsp;')
    L.append(f'  <a href="{cv_pdf}"><strong>Download CV (PDF)</strong></a>')
    L.append("</p>")
    L.append("")
    L.append("---")
    L.append("")

    # --- Summary ---
    L.append("## About")
    L.append("")
    L.append(b["summary"])
    L.append("")

    # --- Current focus (top role highlights, CV-facing) ---
    current = d["work"][0]
    L.append(f"## Currently — {current['position']} @ {current['name']}")
    L.append("")
    for hi in current["highlights"][:5]:
        first_sentence = hi["description"].split(". ")[0].rstrip(".") + "."
        L.append(f"- **{hi['name']}** — {first_sentence}")
    L.append("")

    # --- Skills ---
    L.append("## Skills")
    L.append("")
    for g in d["skills"]:
        L.append(f"- **{g['name']}:** {', '.join(g['keywords'])}")
    L.append("")

    # --- Education ---
    L.append("## Education")
    L.append("")
    for e in d["education"]:
        when = e.get("x_dateDisplay") or (e.get("endDate") or "")
        score = f" · {e['score']}" if e.get("score") else ""
        L.append(f"- **{e['studyType']} in {e['area']}** — {e['institution']}{score} ({when})")
    L.append("")

    # --- Hackathons ---
    if d.get("x_hackathons"):
        L.append("## Hackathons")
        L.append("")
        for h in d["x_hackathons"]:
            L.append(f"- **[{h['name']}]({h['url']})** — {h['event']} ({h['year']}). {h['tagline']}.")
        L.append("")

    # --- Certifications & Awards ---
    L.append("## Certifications & Awards")
    L.append("")
    cert_names = "; ".join(c["name"] for c in d["certificates"])
    L.append(f"**Certifications:** {cert_names}.")
    L.append("")
    for a in d["awards"]:
        when = _fmt_month(a.get("date"))
        L.append(f"- **{a['title']}** — {a['awarder']}{(' · ' + when) if when else ''}. {a['summary']}")
    L.append("")

    # --- Publications ---
    if d.get("publications"):
        L.append("## Publications")
        L.append("")
        for p in d["publications"]:
            title = f"[{p['name']}]({p['url']})" if p.get("url") else p["name"]
            L.append(f"- **{title}** — {p['publisher']} ({p['releaseDate']}). {p['summary']}")
        L.append("")

    # --- Connect: ONE centered row of clickable, self-hosted logo tiles.
    # No platform names, no visible URLs — hover a logo to see its name.
    L.append("## Connect")
    L.append("")
    link_for = {
        "site": site,
        "cv": cv_pdf,
        "email": f"mailto:{b['email']}",
        **{p["network"]: p["url"] for p in profiles},
    }
    chips = []
    for key, label, resolver in CONNECT:
        url = link_for.get(resolver)
        if url:
            chips.append(connect_tile(key, label, url))
    L.append('<p align="center">')
    L.append("  " + "\n  ".join(chips))
    L.append("</p>")
    L.append("")
    L.append("---")
    L.append(f"<p align=\"center\"><sub>Last updated {d['meta']['lastModified']} · "
             f"<a href=\"{site}\">{site}</a></sub></p>")
    L.append("")

    return "\n".join(L)


def main():
    with open(DATA, encoding="utf-8") as f:
        d = json.load(f)
    content = build(d)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[build_readme] wrote {OUT} ({len(content)} chars)")


if __name__ == "__main__":
    main()
