import time
import sys
import os

# Allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.db_client import db
from src.services.embedder import EmbedderService

def run_seed():
    print("🌱 Seeding Database...")
    
    # 1. Reset Collection
    collection = db.get_collection(reset=True)
    
    # 2. Mock Data
    candidates = [
        {
            "name": "Alice Chen", "role": "Senior Engineer",
            "text": "Senior Python Engineer. 8 years exp. PMP Certified. US Citizen with Top Secret Clearance.",
            "meta": {"location": "SF", "visa": "US Citizen", "clearance": "Top Secret"}
        },
        {
            "name": "Wei Zhang", "role": "AI Researcher",
            "text": "PhD in Computer Vision. Published papers on Transformers. Asian Citizen seeking global roles.",
            "meta": {"location": "Singapore", "visa": "Asian Citizen", "clearance": "None"}
        },
        {
            "name": "Bob Smith", "role": "Tech Lead",
            "text": "Python Tech Lead. Mentors juniors. Good at architecture. (Missing PMP).",
            "meta": {"location": "NY", "visa": "US Citizen", "clearance": "None"}
        },
        {
            "name": "Ivan Petrov", "role": "Cloud Architect",
            "text": "Expert in AWS/Azure. 15 years experience. H1B Visa sponsorship required.",
            "meta": {"location": "Remote", "visa": "H1B", "clearance": "None"}
        }
    ]
    
    # 3. Embed & Upload
    print("🧠 Embedding...")
    texts = [c["text"] for c in candidates]
    vectors = EmbedderService.encode_batch(texts)
    
    upload_batch = []
    for i, (cand, vec) in enumerate(zip(candidates, vectors)):
        upload_batch.append({
            "id": f"seed-{i}",
            "dense_values": vec,
            "text": cand["text"],
            "metadata": {**cand["meta"], "name": cand["name"], "role": cand["role"]}
        })
        
    print("💾 Transacting...")
    with collection.transaction() as txn:
        txn.batch_upsert_vectors(upload_batch)
    
    # Wait for index
    txn.poll_completion(target_status="complete", max_attempts=10)
    print("✅ Database Seeded Successfully!")

if __name__ == "__main__":
    run_seed()
