🦁 Kosdra: The AI-Native Recruitment Engine

Stop guessing. Start hiring with precision.

Kosdra is an intelligent recruitment platform that solves the "Semantic Gap" in hiring by combining the power of Vector Search (for skills & context) with Keyword Search (for strict requirements). Built on Cosdata.io, it ensures recruiters find the best talent, not just the candidates who stuffed their resumes with SEO keywords.

🛑 The Problem: Why Hiring is Broken

Recruitment tools today fall into two traps:

Keyword Search Failures: If a candidate writes "mentored juniors" but the recruiter searches for "Leadership," a standard keyword search misses them entirely. You lose great talent because of vocabulary mismatches.

Vector Search Failures: Pure AI search is too "fuzzy." If a job requires a "Top Secret Clearance" or "US Citizenship", a standard vector search might return a brilliant candidate who is a foreign national because their skills match perfectly. This wastes the recruiter's time.

✅ The Solution: Hybrid Search

Kosdra uses a Hybrid Search Engine powered by Cosdata to get the best of both worlds:

Vectors (Dense Index): Understand that "Kubernetes" implies "Cloud Skills" and "Mentoring" implies "Leadership."

Keywords (Sparse Index): Strictly enforce mandatory requirements like Visa Status, Security Clearance, and Certifications (e.g., "PMP").

🚀 Key Features

🔍 Context-Aware Search

Find candidates who mean what you're looking for, even if they use different words.

🛡️ Precision Filters (The "Trap" Solvers)

Citizenship/Visa Filter: Instantly filter out candidates who don't meet legal work requirements (e.g., "Asian Citizen" or "US Citizen").

Clearance Levels: Enforce "Top Secret" or "Secret" clearance requirements with 100% accuracy.

📊 Recruitment Analytics

A built-in dashboard to visualize your talent pool by skill, experience, and location.

📁 Seamless Workflow

Upload: Drag & Drop PDF/Word resumes.

Parse: Automatically extract text and metadata.

Shortlist: One-click shortlisting and CSV export for your team.

🛠️ Tech Stack

Database: Cosdata.io (Hybrid Vector Database)

Embeddings: sentence-transformers/all-MiniLM-L6-v2

Frontend: Streamlit

Backend: Python (Modular Architecture)

Parsing: PyPDF

🏃‍♂️ Quick Start

Clone the Repository

git clone [https://github.com/yourusername/kosdra.git](https://github.com/yourusername/kosdra.git)
cd kosdra


Start Cosdata Server
Follow the instructions in COSDATA_SETUP.md to get your database running.

Install Dependencies

pip install -r requirements.txt


Seed the Database (Loads mock "Trap" candidates for testing)

PYTHONPATH=. python -m kosdra.scripts.seed_db


Run the App

PYTHONPATH=. streamlit run kosdra/main.py


🏆 Hackathon Goals

This project was built for the Cosdata Hackathon 2025 to demonstrate the power of Hybrid Search in a real-world, high-stakes application. By leveraging Cosdata's transactional integrity and dual-indexing capabilities, Kosdra proves that AI can be both smart and precise.