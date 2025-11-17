#!/usr/bin/env python

import os
import time
from typing import List, Dict

from sentence_transformers import SentenceTransformer

from cosdata import Client


def build_mock_documents() -> List[Dict]:
    docs = [
        {
            "id": "doc-1",
            "text": "Penalty for non-compliance under Section 409A is $50,000.",
            "metadata": {"statute": "409A"},
        },
        {
            "id": "doc-2",
            "text": "Penalty for non-compliance under Section 12B is $10,000.",
            "metadata": {"statute": "12B"},
        },
        {
            "id": "doc-3",
            "text": "Under Section 409A, late filing can trigger an additional 10% excise tax.",
            "metadata": {"statute": "409A"},
        },
        {
            "id": "doc-4",
            "text": "Section 12B violations may result in civil penalties and injunctions.",
            "metadata": {"statute": "12B"},
        },
        {
            "id": "doc-5",
            "text": "Breach of contract penalties are governed by Section 501C in corporate bylaws.",
            "metadata": {"statute": "501C"},
        },
    ]
    return docs


def main():
    # Initialize Cosdata client
    client = Client(host="http://localhost:8443", verify=False)

    # Embedding model
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    dim = model.get_sentence_embedding_dimension()

    collection_name = "kosdra_legal"

    # Create collection with TF-IDF enabled per requirement
    try:
        collection = client.create_collection(
            name=collection_name,
            dimension=dim,
            description="Kosdra Legal Search Collection",
            tf_idf_options={"enabled": True},
        )
    except Exception as e:
        # If already exists, just get it
        collection = client.get_collection(collection_name)

    # Create dense (cosine) index
    collection.create_index(distance_metric="cosine")

    # Create TF-IDF index with k1 and b as specified
    collection.create_tf_idf_index(
        name=f"{collection_name}_tfidf",
        k1=1.5,
        b=0.75,
    )

    # Build mock docs and embeddings
    docs = build_mock_documents()
    texts = [d["text"] for d in docs]
    embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)

    vectors = []
    for doc, emb in zip(docs, embeddings):
        vectors.append(
            {
                "id": doc["id"],
                "dense_values": emb.tolist(),
                "text": doc["text"],
                "metadata": doc.get("metadata", {}),
            }
        )

    # Upsert using transaction pattern
    with collection.transaction() as txn:
        txn.batch_upsert_vectors(vectors)
        txn_id = txn.transaction_id

    # Optional: wait briefly and poll for completion
    final_status, success = txn.poll_completion(target_status="complete", max_attempts=6, sleep_interval=2)
    if not success:
        print(f"Transaction {txn_id} did not reach 'complete'. Final status: {final_status}")
    else:
        print(f"Ingestion completed. Transaction: {txn_id}")


if __name__ == "__main__":
    main()
