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


def icon_only(network, url, color, logo):
    """A single clickable, icon-only brand logo (no text label, no visible URL).
    shields.io for-the-badge, colored so it stays visible on GitHub dark mode.
    All slugs verified to return HTTP 200."""
    img = (f"https://img.shields.io/badge/-{color}"
           f"?style=for-the-badge&logo={logo}&logoColor=white")
    return f'<a href="{url}" title="{network}"><img alt="{network}" src="{img}" height="34"></a>'


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

    # --- Connect: ONE centered row of clickable, icon-only brand logos.
    # No platform names, no visible URLs — click any logo to go there.
    # Includes Portfolio, CV, socials, and Email (mailto) so nothing is lost.
    L.append("## Connect")
    L.append("")
    chips = [
        icon_only("Portfolio", site, "00719A", "githubpages"),
        icon_only("Download CV", cv_pdf, "A70E13", "adobeacrobatreader"),
    ]
    for p in profiles:
        _label, color, logo = BADGE.get(p["network"], (p["network"], "555555", ""))
        if logo:
            chips.append(icon_only(p["network"], p["url"], color, logo))
    chips.append(icon_only("Email", f"mailto:{b['email']}", "333333", "gmail"))
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
