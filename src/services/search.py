from typing import List, Dict
from ..core.db_client import db
from .embedder import EmbedderService

def search_candidates(query: str, strictness: float = 0.5, filters: Dict = None) -> List[Dict]:
    """
    Orchestrates the Hybrid Search + Filtering Logic.
    """
    # 1. Generate Vector
    dense_vec = EmbedderService.encode(query)
    
    # 2. Inject Filters into Query for Sparse Boost
    # If a filter is active (e.g. "US Citizen"), appending it to the query 
    # helps the TF-IDF engine prioritize it on the server side.
    augmented_query = query
    if filters:
        if filters.get("visa"): augmented_query += " " + filters["visa"]
        if filters.get("clearance"): augmented_query += " " + filters["clearance"]

    # 3. Execute Database Search
    raw_results = db.manual_hybrid_search(dense_vec, augmented_query, top_k=20)
    
    # 4. Apply Business Logic Filters (Strictness)
    final_results = []
    
    for r in raw_results:
        meta = r.get("metadata", {})
        text = r.get("text", "")
        
        # Hard Filter Logic (The "Pro" Feature)
        if filters:
            if filters.get("visa") and filters["visa"] not in text:
                continue
            if filters.get("clearance") and filters["clearance"] not in text:
                continue
                
        # Keyword Strictness Logic
        # If strictness is high, ensure Proper Nouns in query exist in text
        if strictness > 0.7:
            key_terms = [w for w in query.split() if w[0].isupper() and len(w) > 2]
            missing = [t for t in key_terms if t.lower() not in text.lower()]
            if missing:
                continue 
                
        final_results.append(r)
        
    return final_results
