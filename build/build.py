# -*- coding: utf-8 -*-
"""
build.py — master orchestrator for the single-source-of-truth pipeline.

Runs every spoke that derives from data/resume.json:
    1. build_site.py   -> 7 HTML pages (the website)
    2. build_cv_tex.py -> cv/Nishanur_Rahman_CV.tex   (PDF compiled by CI/local LaTeX)
    3. build_docx.py   -> cv/Nishanur_Rahman_CV.docx
    4. build_kg.py     -> knowledge-graph/cv-graph.json
    5. build_linkedin.py -> linkedin.md (paste-ready)

Usage:
    python build/build.py            # run everything
    python build/build.py site       # run only the site
    python build/build.py site kg    # run a subset

The .tex -> .pdf compile is NOT done here (needs a LaTeX toolchain). CI runs it;
locally, run `pdflatex` in cv/ if you have TeX installed. Everything else is pure
Python (jinja2 + python-docx).
"""
import importlib
import sys
import time

# name -> module under build/
SPOKES = {
    "site": "build_site",
    "cv_tex": "build_cv_tex",
    "docx": "build_docx",
    "kg": "build_kg",
    "linkedin": "build_linkedin",
    "readme": "build_readme",
}


def run(names):
    sys.path.insert(0, __file__.rsplit("build", 1)[0] + "build")
    t0 = time.perf_counter()
    print("=" * 68)
    print("SSOT build — regenerating all surfaces from data/resume.json")
    print("=" * 68)
    for name in names:
        mod_name = SPOKES[name]
        mod = importlib.import_module(mod_name)
        importlib.reload(mod)
        mod.main()
    dt = time.perf_counter() - t0
    print("-" * 68)
    print(f"Done in {dt:.2f}s. Surfaces regenerated: {', '.join(names)}")
    print("Note: LinkedIn stays assisted-manual (no public write API) — see linkedin.md")


if __name__ == "__main__":
    requested = sys.argv[1:]
    if not requested:
        requested = list(SPOKES.keys())
    unknown = [r for r in requested if r not in SPOKES]
    if unknown:
        raise SystemExit(f"Unknown spoke(s): {unknown}. Choose from {list(SPOKES)}")
    run(requested)
