from typing import List, Dict
from ..core.db_client import db
from .embedder import EmbedderService
from ..config import settings

def search_candidates(query: str, strictness: float = 0.5, filters: Dict = None, top_k: int | None = None, fusion_k: float | None = None) -> List[Dict]:
    # Defaults from config
    if top_k is None:
        top_k = settings.DEFAULT_TOP_K
    if fusion_k is None:
        fusion_k = settings.DEFAULT_FUSION_K
    # 1. Vector Search (Semantic)
    dense_vec = EmbedderService.encode(query)
    
    # 2. Keyword Search (Constraint Enforcement)
    augmented_query = query
    if filters:
        if filters.get("visa"): augmented_query += " " + filters["visa"]
        if filters.get("clearance"): augmented_query += " " + filters["clearance"]
        if filters.get("must"):
            augmented_query += " " + " ".join(filters["must"])

    # 3. Execute Hybrid Search
    raw_results = db.manual_hybrid_search(dense_vec, augmented_query, top_k=top_k, fusion_k=fusion_k)

    def normalize(r: Dict) -> Dict:
        # Some servers nest payload under keys like 'vector', 'item', or 'data'
        container = r
        for k in ("vector", "item", "data"):
            if isinstance(r.get(k), dict):
                container = r.get(k)
                break
        meta = r.get("metadata") or container.get("metadata") or r.get("meta") or {}
        text = (
            r.get("text")
            or r.get("raw_text")
            or r.get("document")
            or container.get("text")
            or container.get("raw_text")
            or container.get("document")
            or ""
        )
        rid = (
            r.get("id")
            or container.get("id")
            or meta.get("id")
            or meta.get("doc_id")
            or f"doc-{abs(hash(text))%10_000_000}"
        )
        score = r.get("score") or container.get("score") or r.get("similarity") or 0
        return {**r, "metadata": meta, "text": text, "id": rid, "score": score}

    results = [normalize(r) for r in (raw_results or [])]

    # Fallback to text search if hybrid returned nothing
    if not results:
        try:
            col = db.get_collection()
            tfidf_resp = col.search.text(augmented_query, top_k=top_k, return_raw_text=True)
            maybe_list = tfidf_resp.get("results") if isinstance(tfidf_resp, dict) else tfidf_resp
            results = [normalize(r) for r in (maybe_list or [])]
        except Exception:
            results = []

    # Enrich missing text by fetching vector by id
    try:
        if results:
            col = db.get_collection()
            for r in results:
                if not r.get("text") and r.get("id"):
                    try:
                        vec = col.vectors.get(r["id"])
                        if getattr(vec, "text", None):
                            r["text"] = vec.text
                    except Exception:
                        pass
            # As a secondary fallback, try a TF-IDF search and backfill text by id
            if any(not (x.get("text") or "") for x in results):
                try:
                    tfidf_resp2 = col.search.text(augmented_query, top_k=max(top_k, 50), return_raw_text=True)
                    tfidf_list = tfidf_resp2.get("results") if isinstance(tfidf_resp2, dict) else tfidf_resp2
                    tfidf_map = {}
                    for item in tfidf_list or []:
                        _id = item.get("id") or (item.get("vector") or {}).get("id")
                        _text = item.get("text") or item.get("raw_text") or (item.get("vector") or {}).get("text")
                        if _id and _text:
                            tfidf_map[_id] = _text
                    for r in results:
                        if not r.get("text") and r.get("id") in tfidf_map:
                            r["text"] = tfidf_map[r["id"]]
                except Exception:
                    pass
    except Exception:
        pass

    final_results = []
    for r in results:
        meta = r.get("metadata", {})
        text = r.get("text", "")

        # --- HARD FILTER LOGIC ---
        if filters:
            if filters.get("visa"):
                visa_val = str(meta.get("visa", "")).lower()
                if (filters["visa"].lower() not in visa_val) and (filters["visa"].lower() not in text.lower()):
                    continue
            if filters.get("clearance"):
                clear_val = str(meta.get("clearance", "")).lower()
                if (filters["clearance"].lower() not in clear_val) and (filters["clearance"].lower() not in text.lower()):
                    continue
            # Experience filter (metadata 'exp')
            if filters.get("min_exp") is not None:
                try:
                    exp_val = meta.get("exp")
                    if exp_val is None:
                        raise ValueError
                    if int(exp_val) < int(filters["min_exp"]):
                        continue
                except Exception:
                    # If exp missing or unparsable, treat as failing the min_exp requirement
                    continue
            # Role/location contains
            if filters.get("role_contains") and filters["role_contains"].lower() not in str(meta.get("role", "")).lower():
                continue
            if filters.get("location_contains") and filters["location_contains"].lower() not in str(meta.get("location", "")).lower():
                continue
            # Must and exclude keyword constraints on text
            if filters.get("must"):
                lower_text = text.lower()
                if any(kw.lower() not in lower_text for kw in filters["must"]):
                    continue
            if filters.get("exclude"):
                lower_text = text.lower()
                if any(kw.lower() in lower_text for kw in filters["exclude"]):
                    continue

        # --- STRICTNESS LOGIC ---
        if strictness > 0.7:
            key_terms = [w.strip(".,") for w in query.split() if len(w) > 2]
            missing = [t for t in key_terms if t.lower() not in text.lower()]
            if missing:
                continue

        # --- MATCH EXPLANATION ---
        skills_found = []
        common_skills = ["python", "java", "aws", "kubernetes", "react", "pmp", "mba", "terraform", "pytorch"]
        for skill in common_skills:
            if skill in query.lower() and skill in text.lower():
                skills_found.append(skill.capitalize())

        # --- SCORE THRESHOLD ---
        if filters and filters.get("min_score") is not None:
            try:
                if float(r.get("score") or 0.0) < float(filters["min_score"]):
                    continue
            except Exception:
                pass

        r["match_explanation"] = f"Matched on {', '.join(skills_found)}" if skills_found else "Semantic/Text Match"
        final_results.append(r)

    # If everything was filtered out, optionally relax constraints (env flag)
    if not final_results and settings.RELAX_ON_EMPTY:
        try:
            # Prefer whatever we already have, sorted by score desc
            relaxed = sorted(results, key=lambda x: float(x.get("score") or 0), reverse=True)[:top_k]
            for r in relaxed:
                r.setdefault("match_explanation", "Relaxed match (filters too strict)")
            if relaxed:
                return relaxed
        except Exception:
            pass

        # Last resort: plain text search on original query (no augmented filters)
        try:
            col = db.get_collection()
            tfidf_resp = col.search.text(query, top_k=top_k, return_raw_text=True)
            maybe_list = tfidf_resp.get("results") if isinstance(tfidf_resp, dict) else tfidf_resp
            relaxed2 = [normalize(r) for r in (maybe_list or [])]
            for r in relaxed2:
                r.setdefault("match_explanation", "Text match (no filters)")
            return relaxed2
        except Exception:
            return []

    # Drop unusable items (must have id and text)
    clean = [r for r in final_results if r.get("id") and (r.get("text") or "").strip()]
    return clean[:top_k]