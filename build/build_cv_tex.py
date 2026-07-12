# -*- coding: utf-8 -*-
"""
build_cv_tex.py — generate the LaTeX CV (Nishanur_Rahman_CV.tex) from
data/resume.json. The .tex is compiled to PDF by TeX Live (locally or in CI).

The preamble/macros are reproduced verbatim from the hand-tuned original so the
PDF layout is unchanged; only the *content* is now data-driven (DRY).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "resume.json")
OUT = os.path.join(ROOT, "cv", "Nishanur_Rahman_CV.tex")

MONTHS = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
    "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}

# Order matters: backslash first, then the rest. Unicode punctuation last.
_ESCAPES = [
    ("\\", r"\textbackslash{}"),
    ("&", r"\&"),
    ("%", r"\%"),
    ("$", r"\$"),
    ("#", r"\#"),
    ("_", r"\_"),
    ("{", r"\{"),
    ("}", r"\}"),
    ("~", r"\textasciitilde{}"),
    ("^", r"\textasciicircum{}"),
    ("—", "---"),   # em dash
    ("–", "--"),    # en dash
    ("“", "``"), ("”", "''"),   # curly double quotes
    ("‘", "`"), ("’", "'"),      # curly single quotes / apostrophe
]


def tex(s):
    """Escape a plain string for LaTeX body text."""
    if s is None:
        return ""
    out = str(s)
    for a, b in _ESCAPES:
        out = out.replace(a, b)
    return out


def tex_url(u):
    """Escape a URL for use inside \\href{...} (only # needs escaping here)."""
    return u.replace("#", r"\#")


def fmt_date(value):
    if not value:
        return ""
    parts = str(value).split("-")
    if len(parts) >= 2 and parts[1] in MONTHS:
        return f"{MONTHS[parts[1]]} {parts[0]}"
    return parts[0]


def date_range(job):
    if job.get("x_dateDisplay"):
        return tex(job["x_dateDisplay"])
    start = fmt_date(job.get("startDate"))
    end = fmt_date(job.get("endDate")) if job.get("endDate") else "Present"
    return f"{tex(start)} - {tex(end)}"


PREAMBLE = r"""%-------------------------------------------------------------------------------
% Nishanur Rahman - Resume / CV
% GENERATED FILE -- do not edit by hand. Source of truth: data/resume.json
% Regenerate with: python build/build_cv_tex.py  (or python build/build.py)
%-------------------------------------------------------------------------------
\documentclass[a4paper,11pt]{article}

\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{latexsym}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{enumitem}
\usepackage{tabularx}
\usepackage{hyperref}
\hypersetup{
  colorlinks=true,
  urlcolor=blue,
  linkcolor=blue,
  citecolor=blue,
}
\usepackage{geometry}

\geometry{a4paper, left=0.5in, right=0.5in, top=0.5in, bottom=0.5in}
\pagestyle{empty}

\urlstyle{rm}
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}
  {\scshape\large}{}{0em}{}[\color{black}\titlerule]
\titlespacing*{\section}{0pt}{8pt}{4pt}

\newcommand{\resumeItem}[2]{%
  \item\textbf{#1}: #2%
}
\newcommand{\resumeSubItem}[2]{\resumeItem{#1}{#2}}
\newcommand{\resumeSubheading}[4]{%
  \item
  \begin{tabularx}{0.99\textwidth}{@{}X@{\extracolsep{\fill}}r@{}}
    \textbf{#1} & #2 \\
    \textit{\small #3} & \textit{\small #4} \\
  \end{tabularx}%
}
\renewcommand{\labelitemii}{$\circ$}
\newcommand{\resumeSubHeadingListStart}{%
  \begin{itemize}[leftmargin=0.0in, label={}, topsep=2pt, parsep=2pt, itemsep=2pt]%
}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{%
  \begin{itemize}[leftmargin=*, topsep=2pt, parsep=1pt, itemsep=2pt]%
}
\newcommand{\resumeItemListEnd}{\end{itemize}}

%===============================================================================
\begin{document}
"""


def build(d):
    b = d["basics"]
    profiles = {p["network"]: p for p in b["profiles"]}
    linkedin = profiles["LinkedIn"]["url"]

    L = [PREAMBLE]

    # ---- Heading ----
    L.append("\n%----------HEADING--------------------------------------------------------------\n")
    L.append(r"""\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}
  \textbf{\LARGE {NAME}} & Email: \href{mailto:{EMAIL}}{{EMAILT}} \\
  \href{{LINK}}{LinkedIn: {LINK}} & Mobile:~~~{PHONE} \\
\end{tabular*}
"""
        .replace("{NAME}", tex(b["name"]))
        .replace("{EMAILT}", tex(b["email"]))
        .replace("{EMAIL}", b["email"])
        .replace("{PHONE}", tex(b["phone"]))
        .replace("{LINK}", linkedin))

    # ---- Summary ----
    L.append("\n%-----------SUMMARY-------------------------------------------------------------\n")
    L.append("\\section{Summary}\n")
    L.append(tex(b["summary"]) + "\n")

    # ---- Skills ----
    L.append("\n%-----------SKILLS--------------------------------------------------------------\n")
    L.append("\\section{Skills}\n\\resumeSubHeadingListStart\n")
    for g in d["skills"]:
        L.append("  \\resumeSubItem{%s}{%s}\n" % (tex(g["name"]), tex(", ".join(g["keywords"]))))
    L.append("\\resumeSubHeadingListEnd\n")

    # ---- Experience ----
    L.append("\n%-----------EXPERIENCE---------------------------------------------------------\n")
    L.append("\\section{Experience}\n\\resumeSubHeadingListStart\n")
    for job in d["work"]:
        pos = job["position"]
        if job.get("x_employment") and job["x_employment"] not in (job.get("x_dateDisplay") or ""):
            pos = f"{pos} ({job['x_employment']})"
        L.append("  \\resumeSubheading{%s}{%s}{%s}{%s}\n" % (
            tex(job["name"]), tex(job.get("location", "")), tex(pos), date_range(job)))
        if job.get("highlights"):
            L.append("  \\resumeItemListStart\n")
            for hi in job["highlights"]:
                L.append("    \\resumeItem{%s}{%s}\n" % (tex(hi["name"]), tex(hi["description"])))
            L.append("  \\resumeItemListEnd\n")
    L.append("\\resumeSubHeadingListEnd\n")

    # ---- Hackathons ----
    if d.get("x_hackathons"):
        L.append("\n%-----------HACKATHONS---------------------------------------------------------\n")
        L.append("\\section{Hackathons}\n\\resumeSubHeadingListStart\n")
        for h in d["x_hackathons"]:
            href = "\\href{%s}{%s}" % (tex_url(h["url"]), tex(h["event"]))
            L.append("  \\resumeSubheading{%s}{%s}{%s}{%s}\n" % (
                tex(h["name"]), href, tex(h["tagline"]), tex(h["year"])))
            L.append("  \\resumeItemListStart\n")
            for hi in h["highlights"]:
                L.append("    \\resumeItem{%s}{%s}\n" % (tex(hi["name"]), tex(hi["description"])))
            # Submission line with clickable link
            L.append("    \\resumeItem{Submission}{%s \\href{%s}{View hackathon idea}.}\n" % (
                tex(h["status"]), tex_url(h["url"])))
            L.append("  \\resumeItemListEnd\n")
        L.append("\\resumeSubHeadingListEnd\n")

    # ---- Education ----
    L.append("\n%-----------EDUCATION----------------------------------------------------------\n")
    L.append("\\section{Education}\n\\resumeSubHeadingListStart\n")
    for e in d["education"]:
        degree = f"{e['studyType']} in {e['area']}" if e.get("studyType") else e["area"]
        if e.get("score"):
            degree = f"{e['studyType']} - {e['area']}; {e['score']}"
        right = e.get("x_dateDisplay") or fmt_date(e.get("endDate"))
        L.append("  \\resumeSubheading{%s}{%s}{%s}{%s}\n" % (
            tex(e["institution"]), tex(e.get("location", "")), tex(degree), tex(right)))
        if e.get("courses"):
            L.append("  \\resumeItemListStart\n")
            L.append("    \\item[] \\textit{\\textbf{Relevant coursework:} %s.}\n" % tex(", ".join(e["courses"])))
            L.append("  \\resumeItemListEnd\n")
    L.append("\\resumeSubHeadingListEnd\n")

    # ---- Certifications & Awards ----
    L.append("\n%-----------CERTIFICATIONS & AWARDS--------------------------------------------\n")
    L.append("\\section{Certifications and Awards}\n")
    cert_names = "; ".join(c["name"] for c in d["certificates"])
    L.append("\\resumeSubHeadingListStart\n")
    L.append("  \\resumeSubItem{Certifications}{%s. (Verifiable on my \\href{%s}{LinkedIn}.)}\n" % (
        tex(cert_names), linkedin))
    for a in d["awards"]:
        detail = a["summary"]
        when = fmt_date(a.get("date"))
        body = f"{a['awarder']} --- {detail} {when}." if when else f"{a['awarder']} --- {detail}"
        L.append("  \\resumeSubItem{%s}{%s}\n" % (tex(a["title"]), tex(body)))
    L.append("\\resumeSubHeadingListEnd\n")

    # ---- Publications ----
    if d.get("publications"):
        L.append("\n%-----------PUBLICATIONS-------------------------------------------------------\n")
        L.append("\\section{Publications}\n\\resumeSubHeadingListStart\n")
        for p in d["publications"]:
            # summary already carries the citation + findings prose
            body = "\\textit{%s} \\href{%s}{View Publication}." % (tex(p["summary"]), tex_url(p["url"])) \
                if p.get("url") else "\\textit{%s}" % tex(p["summary"])
            L.append("  \\resumeSubItem{%s}{%s}\n" % (tex(p["name"]), body))
        L.append("\\resumeSubHeadingListEnd\n")

    # ---- Volunteer & Hobbies ----
    L.append("\n%-----------VOLUNTEER & HOBBIES------------------------------------------------\n")
    L.append("\\section{Volunteer Experience and Hobbies}\n\\resumeSubHeadingListStart\n")
    for v in d["volunteer"]:
        L.append("  \\resumeSubheading{%s}{%s}{%s}{%s}\n" % (
            tex(v["organization"]), tex(v.get("location", "")), tex(v["summary"]), tex(v.get("x_dateDisplay", ""))))
    L.append("\\resumeSubHeadingListEnd\n")
    hobbies = next((g["keywords"] for g in d["interests"] if g["name"] == "Hobbies"), [])
    if hobbies:
        L.append("\\vspace{4pt}\n")
        L.append("\\noindent\\textbf{Hobbies:} %s\n" % tex(", ".join(hobbies)))

    L.append("\n\\end{document}\n")
    return "".join(L)


def main():
    with open(DATA, encoding="utf-8") as f:
        d = json.load(f)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    content = build(d)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[build_cv_tex] wrote {OUT} ({len(content)} chars)")


if __name__ == "__main__":
    main()
