# -*- coding: utf-8 -*-
"""
build_site.py — render the 7-page portfolio website from data/resume.json.

Method: template–data separation (MVC / static-site generation) via Jinja2, plus
schema.org/Person JSON-LD structured data for search-engine discoverability.

Run standalone (`python build/build_site.py`) or via build/build.py.
Outputs HTML pages to the repo root and copies assets/.
"""
import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "resume.json")
TEMPLATES = os.path.join(HERE, "templates")

# Navigation: (template file, nav label). Order = nav order.
NAV = [
    ("index.html", "Home"),
    ("projects.html", "Projects"),
    ("life.html", "Life so far"),
    ("learning.html", "Presently learning"),
    ("pipeline.html", "Pipeline Learnings"),
    ("art.html", "Art"),
    ("testimonials.html", "Friends Testimonials"),
]

# Per-page SEO description (kept short; falls back to summary).
PAGE_DESC = {
    "index.html": None,  # uses basics.summary
    "projects.html": "Gen AI, LLM automation, and operational-analytics systems built by {name} at Amazon.",
    "life.html": "Career and education timeline of {name} — Amazon, IIT Madras, NPTEL.",
    "learning.html": "What {name} is currently learning: Agentic AI, RAG, software architecture, knowledge graphs.",
    "pipeline.html": "How this portfolio auto-builds from a single source of truth via GitHub Actions.",
    "art.html": "Publications, awards, and creative work by {name}.",
    "testimonials.html": "Testimonials for {name} from colleagues and peers.",
}

MONTHS = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
    "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}


def fmt_date(value):
    """'2024-08' -> 'Aug 2024'; '2016' -> '2016'; '' / None -> ''."""
    if not value:
        return ""
    parts = str(value).split("-")
    if len(parts) >= 2 and parts[1] in MONTHS:
        return f"{MONTHS[parts[1]]} {parts[0]}"
    return parts[0]


def load_data():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def build_jsonld(d):
    """schema.org/Person structured data — powers rich search results."""
    b = d["basics"]
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": b["name"],
        "jobTitle": b["label"],
        "email": f"mailto:{b['email']}",
        "url": b["url"],
        "image": b["image"],
        "address": {
            "@type": "PostalAddress",
            "addressLocality": b["location"]["city"],
            "addressRegion": b["location"]["region"],
            "addressCountry": b["location"]["countryCode"],
        },
        "sameAs": [p["url"] for p in b["profiles"]],
        "knowsAbout": sorted({kw for g in d["skills"] for kw in g["keywords"]}),
        "worksFor": {"@type": "Organization", "name": d["work"][0]["name"]},
        "alumniOf": [
            {"@type": "CollegeOrUniversity", "name": e["institution"]}
            for e in d["education"]
        ],
    }
    return json.dumps(person, ensure_ascii=False, indent=2)


def main():
    d = load_data()
    b = d["basics"]
    profiles_by_network = {p["network"]: p for p in b["profiles"]}
    current_role = d["work"][0]

    # Featured = first 4 Amazon highlights (highest-signal projects).
    featured = current_role["highlights"][:4]

    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html", "xml", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["fmt_date"] = fmt_date

    nav = [{"file": f, "label": l} for f, l in NAV]
    jsonld = build_jsonld(d)

    common = dict(
        basics=b,
        meta=d["meta"],
        nav=nav,
        profiles_by_network=profiles_by_network,
        work=d["work"],
        education=d["education"],
        skills=d["skills"],
        certificates=d["certificates"],
        awards=d["awards"],
        publications=d["publications"],
        volunteer=d["volunteer"],
        interests=d["interests"],
        hackathons=d["x_hackathons"],
        learning=d["x_presentlyLearning"],
        pipeline=d["x_pipeline"],
        testimonials=d["x_testimonials"],
        featured=featured,
        current_role=current_role,
        jsonld=jsonld,
    )

    written = []
    for page_file, _label in NAV:
        template = env.get_template(f"{page_file}.j2")
        desc_tmpl = PAGE_DESC.get(page_file)
        page_description = (
            desc_tmpl.format(name=b["name"]) if desc_tmpl else b["summary"]
        )
        html = template.render(
            page_file=page_file,
            page_title=dict(NAV)[page_file],
            page_description=page_description,
            **common,
        )
        out = os.path.join(ROOT, page_file)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        written.append(page_file)

    print(f"[build_site] wrote {len(written)} pages: {', '.join(written)}")
    return written


if __name__ == "__main__":
    main()
