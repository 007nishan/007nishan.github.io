# -*- coding: utf-8 -*-
"""
build_kg.py — regenerate the CV knowledge graph (knowledge-graph/cv-graph.json)
from data/resume.json.

Method (unchanged from the original hand-built graph, now automated):
  * Structure: Property Graph Model (Angles & Gutierrez 2008; openCypher/Neo4j)
  * Ontology:  schema.org/Person, JSON Resume schema, ESCO skills framing
  * Pipeline:  entities -> relations -> ontology mapping (Hogan et al., ACM CSUR 2021)

Node types: person, organization, role, project, skillgroup, skill, education,
credential, award, publication, volunteering, hobby, hackathon.
Deterministic slug-based IDs keep the graph stable across rebuilds so it merges
cleanly with portfolio-v2/knowledge-graph/graph.json.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "resume.json")
OUT = os.path.join(ROOT, "knowledge-graph", "cv-graph.json")


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return s[:40]


def build(d):
    b = d["basics"]
    nodes = []
    edges = []
    orgs = {}  # normalized org label -> node id

    def add_org(label, **props):
        key = label.strip()
        if key in orgs:
            return orgs[key]
        nid = "org_" + slug(label)
        orgs[key] = nid
        nodes.append({"id": nid, "type": "organization", "label": label, **props})
        return nid

    # ---- Person ----
    nodes.append({
        "id": "person", "type": "person", "label": b["name"],
        "email": b["email"], "phone": b["phone"],
        "linkedin": next((p["url"] for p in b["profiles"] if p["network"] == "LinkedIn"), None),
        "location": f"{b['location']['city']}, {b['location']['countryCode']}",
        "headline": b["label"],
    })

    # ---- Skill groups + skills ----
    for g in d["skills"]:
        sg_id = "sg_" + slug(g["name"])
        nodes.append({"id": sg_id, "type": "skillgroup", "label": g["name"]})
        if g["name"].lower().startswith("soft"):
            edges.append({"from": "person", "to": sg_id, "rel": "has"})
        for kw in g["keywords"]:
            sk_id = "sk_" + slug(kw)
            if not any(n["id"] == sk_id for n in nodes):
                nodes.append({"id": sk_id, "type": "skill", "label": kw, "group": sg_id})
                edges.append({"from": sk_id, "to": sg_id, "rel": "inGroup"})

    def skill_id(label):
        return "sk_" + slug(label)

    # ---- Work / roles / projects ----
    for job in d["work"]:
        org_id = add_org(job["name"], location=job.get("location"))
        role_id = "role_" + slug(job["name"]) + "_" + slug(job["position"])
        nodes.append({
            "id": role_id, "type": "role", "label": job["position"], "org": org_id,
            "employment": job.get("x_employment"), "start": job.get("startDate"),
            "end": job.get("endDate"), "current": job.get("endDate") is None,
        })
        rel = "holds" if job.get("endDate") is None else "held"
        edges.append({"from": "person", "to": role_id, "rel": rel})
        edges.append({"from": role_id, "to": org_id, "rel": "at"})
        for hi in job.get("highlights", []):
            proj_id = "proj_" + slug(hi["name"])
            nodes.append({"id": proj_id, "type": "project", "label": hi["name"],
                          "org": org_id, "summary": hi["description"]})
            edges.append({"from": role_id, "to": proj_id, "rel": "delivered"})
            # naive skill linking from description keywords
            for kw_label, kw in [("LLM", "LLM"), ("RAG", "RAG"),
                                 ("Reinforcement Learning", "Reinforcement Learning"),
                                 ("Flask", "Flask"), ("AWS", "AWS Cloud")]:
                if kw_label.lower() in hi["description"].lower():
                    sid = skill_id(kw)
                    if any(n["id"] == sid for n in nodes):
                        edges.append({"from": proj_id, "to": sid, "rel": "uses"})

    # ---- Hackathons ----
    for h in d.get("x_hackathons", []):
        org_id = add_org(h["event"], url=h.get("url"), domain="hackathon")
        proj_id = "proj_" + slug(h["name"])
        nodes.append({"id": proj_id, "type": "hackathon", "label": h["name"],
                      "org": org_id, "year": h.get("year"), "status": h.get("status"),
                      "summary": h.get("tagline"), "url": h.get("url")})
        edges.append({"from": "person", "to": proj_id, "rel": "built"})
        edges.append({"from": proj_id, "to": org_id, "rel": "submittedTo"})

    # ---- Education ----
    for e in d["education"]:
        org_id = add_org(e["institution"], location=e.get("location"))
        edu_id = "edu_" + slug(e["institution"])
        nodes.append({"id": edu_id, "type": "education",
                      "label": f"{e['studyType']} in {e['area']}", "org": org_id,
                      "status": e.get("x_dateDisplay"), "score": e.get("score"),
                      "courses": e.get("courses", [])})
        rel = "studies" if (e.get("x_dateDisplay") or "").lower() == "pursuing" else "studied"
        edges.append({"from": "person", "to": edu_id, "rel": rel})
        edges.append({"from": edu_id, "to": org_id, "rel": "at"})

    # ---- Certificates ----
    for c in d["certificates"]:
        cid = "cert_" + slug(c["name"])
        nodes.append({"id": cid, "type": "credential", "label": c["name"],
                      "issuer": c.get("issuer") or None})
        edges.append({"from": "person", "to": cid, "rel": "earned"})

    # ---- Awards ----
    for a in d["awards"]:
        aid = "award_" + slug(a["title"])
        nodes.append({"id": aid, "type": "award", "label": a["title"],
                      "date": a.get("date"), "awarder": a.get("awarder"),
                      "detail": a.get("summary")})
        edges.append({"from": "person", "to": aid, "rel": "won"})

    # ---- Publications ----
    for p in d["publications"]:
        venue_id = add_org(p["publisher"], domain="Academic journal")
        pid = "pub_" + slug(p["name"])
        nodes.append({"id": pid, "type": "publication", "label": p["name"],
                      "venue": venue_id, "url": p.get("url"),
                      "citation": p.get("summary")})
        edges.append({"from": "person", "to": pid, "rel": "authored"})
        edges.append({"from": pid, "to": venue_id, "rel": "publishedIn"})

    # ---- Volunteering ----
    for v in d["volunteer"]:
        vid = "vol_" + slug(v["organization"])
        nodes.append({"id": vid, "type": "volunteering", "label": v["organization"],
                      "location": v.get("location"), "year": v.get("x_dateDisplay"),
                      "detail": v.get("summary")})
        edges.append({"from": "person", "to": vid, "rel": "volunteered"})

    # ---- Hobbies ----
    hobbies = next((g["keywords"] for g in d["interests"] if g["name"] == "Hobbies"), [])
    if hobbies:
        nodes.append({"id": "hobbies", "type": "hobby", "label": "Hobbies", "items": hobbies})
        edges.append({"from": "person", "to": "hobbies", "rel": "enjoys"})

    graph = {
        "$schema": "knowledge-graph/v1",
        "generatedFrom": {
            "source": "data/resume.json",
            "sourceType": "resume/cv",
            "generator": "build/build_kg.py",
            "method": {
                "structure": "Property Graph Model (Angles & Gutierrez 2008; openCypher/Neo4j)",
                "ontology": ["schema.org/Person", "JSON Resume schema (jsonresume.org)", "ESCO skills framing"],
                "pipeline": "entities -> relations -> ontology mapping (Hogan et al., ACM CSUR 2021)",
            },
            "notes": "Auto-generated from the single source of truth. Metrics recorded as-claimed and are unverified. Merges with portfolio-v2/knowledge-graph/graph.json under a shared personal graph.",
        },
        "nodes": nodes,
        "edges": edges,
    }
    return graph


def validate(graph):
    ids = [n["id"] for n in graph["nodes"]]
    dupes = {i for i in ids if ids.count(i) > 1}
    idset = set(ids)
    dangling = [e for e in graph["edges"] if e["from"] not in idset or e["to"] not in idset]
    return dupes, dangling


def main():
    with open(DATA, encoding="utf-8") as f:
        d = json.load(f)
    graph = build(d)
    dupes, dangling = validate(graph)
    if dupes:
        raise SystemExit(f"[build_kg] ERROR duplicate node ids: {dupes}")
    if dangling:
        raise SystemExit(f"[build_kg] ERROR dangling edges: {dangling[:5]}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)
    print(f"[build_kg] wrote {OUT} — {len(graph['nodes'])} nodes, {len(graph['edges'])} edges "
          f"(validated: no dupes, no dangling edges)")


if __name__ == "__main__":
    main()
