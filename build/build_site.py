# -*- coding: utf-8 -*-
"""
build_site.py — render the PUBLIC website from data/resume.json.

The public site is intentionally CV-ONLY: a single index.html that presents the
full CV to anyone with the link. Nothing about the build pipeline, LinkedIn
strategy, or internal planning is published. (The full multi-page templates still
exist under build/templates/ but are NOT rendered to the public site.)

Method: template–data separation (static-site generation) via Jinja2, plus
schema.org/Person JSON-LD structured data for search-engine discoverability.

Run standalone (`python build/build_site.py`) or via build/build.py.
"""
import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "resume.json")
TEMPLATES = os.path.join(HERE, "templates")

# The ONLY page published publicly. Template: cv.html.j2 -> index.html.
PUBLIC_PAGE = ("index.html", "cv.html.j2")

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

    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html", "xml", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["fmt_date"] = fmt_date

    jsonld = build_jsonld(d)

    # Only CV-relevant data is passed to the public page. Internal-only sections
    # (x_pipeline, x_presentlyLearning, testimonials, LinkedIn strategy) are
    # deliberately NOT rendered to the public site.
    page_file, template_name = PUBLIC_PAGE
    template = env.get_template(template_name)
    html = template.render(
        page_file=page_file,
        page_title="CV",
        page_description=b["summary"],
        basics=b,
        meta=d["meta"],
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
        jsonld=jsonld,
    )
    out = os.path.join(ROOT, page_file)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[build_site] wrote public CV page: {page_file}")
    return [page_file]


if __name__ == "__main__":
    main()
