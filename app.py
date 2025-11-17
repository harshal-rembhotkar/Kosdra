#!/usr/bin/env python

import os
import json
from typing import Dict, Any, List

import requests
import streamlit as st
from sentence_transformers import SentenceTransformer

from cosdata import Client


def search_hybrid(collection, dense_vec: List[float], text_query: str, top_k: int = 5, return_raw_text: bool = True):
    base_url = collection.client.base_url
    url = f"{base_url}/collections/{collection.name}/search/hybrid"

    # Payload mirrors SDK style and hybrid expectations
    payload = {
        "dense": {
            "query_vector": dense_vec,
            "top_k": top_k,
        },
        "text": {
            "query": text_query,
            "top_k": top_k,
            "return_raw_text": return_raw_text,
        },
        "fusion_constant_k": 60.0,
        "return_raw_text": return_raw_text,
    }

    resp = requests.post(
        url,
        headers=collection.client._get_headers(),
        data=json.dumps(payload),
        verify=collection.client.verify_ssl,
    )
    if resp.status_code != 200:
        raise Exception(f"Hybrid search failed: {resp.text}")
    return resp.json()


def main():
    st.set_page_config(page_title="Kosdra Legal Search", layout="wide")
    st.title("Kosdra Legal Search")

    # Initialize client and collection
    client = Client(host="http://localhost:8443", verify=False)
    collection = client.get_collection("kosdra_legal")

    # Load embedding model
    @st.cache_resource(show_spinner=False)
    def load_model():
        return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    model = load_model()

    query = st.text_input("Search legal penalties or statutes (e.g., 'Penalties for Section 409A')", "")
    top_k = st.number_input("Top K", min_value=1, max_value=50, value=5, step=1)

    if query:
        with st.spinner("Searching..."):
            dense_vec = model.encode([query], normalize_embeddings=True)[0].tolist()
            results = search_hybrid(collection, dense_vec, query, top_k=top_k, return_raw_text=True)

        # Normalize display
        rows = []
        for r in results.get("results", []):
            # Try to extract metadata/statute and raw text
            statute = None
            text = None

            # Some backends return nested fields; handle common shapes
            meta = r.get("metadata") or {}
            statute = meta.get("statute") if isinstance(meta, dict) else None
            text = r.get("text") or r.get("raw_text")

            rows.append({
                "Score": r.get("score"),
                "Statute": statute,
                "Text": text,
            })

        st.subheader("Results")
        st.dataframe(rows, use_container_width=True)


if __name__ == "__main__":
    main()
