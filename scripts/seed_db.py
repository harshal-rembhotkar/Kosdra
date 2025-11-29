import sys
import os
import time

# Ensure python can find the 'kosdra' package from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kosdra.src.core.db_client import db
from kosdra.src.services.embedder import EmbedderService

def run_seed():
    print("🌱 Seeding Kosdra Database...")
    try:
        col = db.get_collection(reset=True)
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    candidates = [
        {
            "name": "Alice Chen", "role": "Senior Engineer",
            "text": "Senior Python Engineer. 8 years exp. PMP Certified. US Citizen with Top Secret Clearance. Expert in Kubernetes.",
            "meta": {"location": "SF", "visa": "US Citizen", "clearance": "Top Secret", "skills": "Python, Kubernetes, PMP", "exp": 8}
        },
        {
            "name": "Wei Zhang", "role": "AI Researcher",
            "text": "PhD in Computer Vision. Published papers on Transformers. Asian Citizen seeking global roles. PyTorch expert.",
            "meta": {"location": "Singapore", "visa": "Asian Citizen", "clearance": "None", "skills": "PyTorch, CV, AI", "exp": 5}
        },
        {
            "name": "Ravi Patel", "role": "DevOps Lead",
            "text": "DevOps expert. Terraform, AWS, Kubernetes. Asian Citizen available immediately. Built CI/CD for fintech.",
            "meta": {"location": "Bangalore", "visa": "Asian Citizen", "clearance": "None", "skills": "AWS, Terraform, CI/CD", "exp": 6}
        },
        {
            "name": "Bob Smith", "role": "Tech Lead",
            "text": "Python Tech Lead. Mentors juniors. Good at system architecture. (Missing PMP certification).",
            "meta": {"location": "New York", "visa": "US Citizen", "clearance": "None", "skills": "Python, Architecture, Mentoring", "exp": 10}
        },
        {
            "name": "Ivan Petrov", "role": "Cloud Architect",
            "text": "Expert in AWS/Azure. 15 years experience. H1B Visa sponsorship required.",
            "meta": {"location": "Remote", "visa": "H1B", "clearance": "None", "skills": "AWS, Azure, Cloud", "exp": 15}
        }
    ]
    
    print("🧠 Embedding...")
    texts = [c["text"] for c in candidates]
    vectors = EmbedderService.encode_batch(texts)
    
    batch = []
    for i, (cand, vec) in enumerate(zip(candidates, vectors)):
        batch.append({
            "id": f"seed-{i}",
            "dense_values": vec,
            "text": cand["text"],
            "metadata": {**cand["meta"], "name": cand["name"], "role": cand["role"]}
        })
        
    print("💾 Transacting...")
    with col.transaction() as txn:
        txn.batch_upsert_vectors(batch)
    
    txn.poll_completion(target_status="complete", max_attempts=10)
    print("✅ Database Seeded!")

if __name__ == "__main__":
    run_seed()