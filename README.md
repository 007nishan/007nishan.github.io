# Nishanur Rahman — portfolio (`007nishan.github.io`)

A personal portfolio site that **builds itself from a single source of truth**.
Edit one file, push, and every surface updates automatically.

## Single source of truth

```
                    data/resume.json   ← EDIT ONLY THIS
                          │
   ┌──────────┬───────────┼────────────┬─────────────────┐
   ▼          ▼           ▼            ▼                 ▼
7 HTML pages  CV → PDF     CV → DOCX    linkedin.md      knowledge-graph/
(the site)   (LaTeX/CI)  (python-docx) (paste blocks)   cv-graph.json
```

`data/resume.json` follows the [JSON Resume](https://jsonresume.org/schema) open
standard, extended with `x_*` fields for site-specific content (hackathons,
"presently learning", the pipeline page, testimonials).

**Principle:** DRY — *"every piece of knowledge must have a single, unambiguous,
authoritative representation"* (Hunt & Thomas, *The Pragmatic Programmer*, 1999).

## How to update anything

1. Edit **`data/resume.json`** only.
2. Commit & push to `main`.
3. GitHub Actions ([`.github/workflows/build.yml`](.github/workflows/build.yml))
   rebuilds all surfaces, compiles the CV PDF with TeX Live, commits the
   regenerated artifacts, and GitHub Pages redeploys — typically within ~1–2 min.

That's the "any change reflects everywhere" loop. No file is edited by hand
except `resume.json` (and, optionally, `assets/style.css` for design).

### Build locally

```bash
pip install jinja2 python-docx
python build/build.py            # regenerate everything
python build/build.py site       # just the website
python build/build.py site kg    # a subset (site + knowledge graph)
```

The CV **PDF** needs a LaTeX toolchain (`pdflatex cv/Nishanur_Rahman_CV.tex`);
if you don't have one locally, CI compiles it on push. Everything else is pure
Python.

## Layout

| Path | What it is | Edited by |
|---|---|---|
| `data/resume.json` | **Single source of truth** | **You** |
| `build/build.py` | Master orchestrator | generator |
| `build/build_site.py` + `build/templates/` | Website renderer (Jinja2) | generator |
| `build/build_cv_tex.py` | CV → LaTeX | generator |
| `build/build_docx.py` | CV → Word | generator |
| `build/build_kg.py` | Knowledge graph (property graph) | generator |
| `build/build_linkedin.py` | LinkedIn paste blocks | generator |
| `assets/style.css` | Site styles | hand-editable |
| `*.html` (root) | Generated pages served by Pages | **generated — don't edit** |
| `cv/`, `knowledge-graph/`, `linkedin.md` | Generated artifacts | **generated — don't edit** |

## The LinkedIn caveat (honest)

LinkedIn has **no public write API** for personal profiles, so nothing can
auto-push edits there. `linkedin.md` gives you keyword-optimized, character-limit-
checked, paste-ready blocks plus a sync checklist — assisted-manual by necessity.

## Methods / standards used

- **JSON Resume** schema (jsonresume.org) — canonical résumé data model.
- **Static-site generation / template–data separation** — Jinja2.
- **schema.org/Person + JSON-LD** — structured data for search discoverability.
- **Property Graph Model** (Angles & Gutiérrez 2008) with schema.org + ESCO
  ontology — the knowledge graph.
- **Information theory** (channel capacity, signal-to-noise, mutual information)
  — the LinkedIn block optimization.
- **CI/CD build-on-push** — GitHub Actions.
