# -*- coding: utf-8 -*-
"""
build_linkedin.py — generate linkedin.md: paste-ready, keyword-optimized blocks
for the LinkedIn profile, derived from data/resume.json.

WHY THIS IS ASSISTED-MANUAL, NOT AUTO-PUSH:
LinkedIn has no public write API for personal profiles. Nothing can
programmatically edit your profile. So this spoke produces text you paste, plus a
sync checklist — the honest ceiling for the LinkedIn surface.

Method / framing (from the profile-optimization brief):
  * Information theory — treat each field as a rate-limited channel; front-load
    the highest-mutual-information terms (keywords recruiters actually search)
    within LinkedIn's truncation limits (headline ~220 chars; About preview
    ~2 lines before "see more").
  * Signal-to-noise — omit filler ("passionate", "results-driven") that has
    near-zero mutual information with recruiter queries.
  * Network science — Featured/keywords chosen to bridge clusters (Ops + AI/ML +
    Data Science), raising discoverability across adjacent talent pools.

Character limits enforced (LinkedIn, 2026):
  headline <= 220, about <= 2600, experience title <= 100.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "resume.json")
OUT = os.path.join(ROOT, "linkedin.md")

LIMITS = {"headline": 220, "about": 2600, "title": 100}


def budget(text, key):
    limit = LIMITS[key]
    n = len(text)
    flag = "OK" if n <= limit else "OVER LIMIT"
    return f"{n}/{limit} chars — {flag}"


def build(d):
    b = d["basics"]
    skills = {g["name"]: g["keywords"] for g in d["skills"]}
    current = d["work"][0]

    # ---- Headline: front-load highest-MI role terms + domains ----
    headline = ("Gen AI & LLM Automation at Amazon | RAG · Self-Improving Systems | "
                "Data Science @ IIT Madras | Python · AWS · Full-Stack")
    if len(headline) > LIMITS["headline"]:
        headline = headline[:LIMITS["headline"]]

    # ---- About: first 2 lines carry the signal (shown before "see more") ----
    about_lead = ("I build Gen AI systems that prevent defects in Amazon's Last Mile operations — "
                  "self-improving RAG assistants, real-time quality dashboards, and SLA engines.")
    about_line2 = ("Operations + Data Science, 3+ years turning messy operational problems into "
                   "scalable, LLM-powered automation.")
    featured_projects = current["highlights"][:4]
    about_body = "\n\n".join([
        about_lead + " " + about_line2,
        "What I work on:",
        "\n".join(f"• {p['name']} — {p['description'].split('.')[0]}." for p in featured_projects),
        "Toolkit: " + ", ".join(skills["AI/ML"] + skills["Languages"][:3] + ["AWS"]) + ".",
        "Currently pursuing a BS in Data Science & Applications at IIT Madras. "
        "Open to conversations on applied AI/ML, LLM systems, and operations analytics.",
    ])

    # ---- High-value keyword bank (mutual information with recruiter search) ----
    keyword_bank = sorted(set(
        skills["AI/ML"] + skills["Languages"] + skills["Platforms"]
        + ["Generative AI", "LLM", "RAG", "Prompt Engineering", "MLOps",
           "Operations Analytics", "Data Science", "Automation", "Amazon"]
    ))

    lines = []
    lines.append("# LinkedIn — paste-ready blocks\n")
    lines.append(f"> Generated from `data/resume.json` on {d['meta']['lastModified']}. "
                 "LinkedIn has **no public write API**, so this is assisted-manual: "
                 "copy each block into the matching profile field.\n")
    lines.append("> Framing: each field is a rate-limited channel — highest "
                 "mutual-information (recruiter-searched) terms are front-loaded; "
                 "filler is omitted to maximize signal-to-noise.\n")

    lines.append("\n## 1. Headline")
    lines.append(f"_({budget(headline, 'headline')})_\n")
    lines.append("```\n" + headline + "\n```")

    lines.append("\n## 2. About")
    lines.append(f"_({budget(about_body, 'about')}; first ~2 lines show before “see more” — "
                 "keep the signal there)_\n")
    lines.append("```\n" + about_body + "\n```")

    lines.append("\n## 3. Experience — current role title")
    exp_title = f"{current['position']} — {current['name']}"
    lines.append(f"_({budget(exp_title, 'title')})_\n")
    lines.append("```\n" + exp_title + "\n```")

    lines.append("\n### Experience description (paste under the role)")
    exp_desc = "\n".join(f"• {p['name']}: {p['description']}" for p in current["highlights"])
    lines.append("```\n" + exp_desc + "\n```")

    lines.append("\n## 4. Skills section (add these — ordered by search value)")
    lines.append("```\n" + "\n".join(keyword_bank) + "\n```")

    lines.append("\n## 5. Featured (network-bridging picks)")
    lines.append("Pin these so your profile bridges the Ops, AI/ML, and Data-Science "
                 "clusters (raises cross-cluster discoverability):")
    lines.append(f"- **Portfolio site** — {b['url']}")
    for h in d.get("x_hackathons", []):
        lines.append(f"- **{h['name']}** — {h['url']}")
    for p in d.get("publications", []):
        lines.append(f"- **{p['name']}** — {p.get('url','')}")

    lines.append("\n## 6. Sync checklist (do after any resume.json change)")
    lines.append("- [ ] Paste Headline (field 1)")
    lines.append("- [ ] Paste About (field 2)")
    lines.append("- [ ] Update current-role title + description (fields 3–4)")
    lines.append("- [ ] Reconcile Skills list (field 5) — add missing, remove stale")
    lines.append("- [ ] Confirm Featured links (field 6) still resolve")
    lines.append("- [ ] Set profile URL vanity + banner if changed")

    return "\n".join(lines) + "\n"


def main():
    with open(DATA, encoding="utf-8") as f:
        d = json.load(f)
    content = build(d)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[build_linkedin] wrote {OUT} ({len(content)} chars)")


if __name__ == "__main__":
    main()
