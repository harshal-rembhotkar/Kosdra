# Kosdra

An intelligent recruitment OS built with Streamlit. It performs hybrid search over a Cosdata vector database, supports PDF/UTF-8 resume ingestion, semantic embeddings with SentenceTransformers, and a modern dashboard UI.

## Features
- Hybrid search: dense embeddings + TF‑IDF fusion
- Resume ingestion (PDF and text)
- Shortlisting workflow
- Config via `.env`
- Seed script to bootstrap a demo collection

## Requirements
- Python 3.10+
- A running Cosdata server (defaults to `http://127.0.0.1:8443`)

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` (you can copy `.env.example`):
```env
COSDATA_HOST=http://127.0.0.1:8443
COSDATA_USER=admin
COSDATA_PASS=Admin1h
COLLECTION_NAME=talentscout_prod
```

## Seed the database
This creates the collection and upserts demo candidates.
```bash
# from repo root
PYTHONPATH=. ./venv/bin/python -m scripts.seed_db
```

## Run the app
Use the venv’s Streamlit executable or module form.
```bash
# from repo root
PYTHONPATH=. ./venv/bin/streamlit run main.py
# or
PYTHONPATH=. ./venv/bin/python -m streamlit run main.py
# optional: specify a port
PYTHONPATH=. ./venv/bin/streamlit run main.py --server.port 8501
```

## Project structure
```
kosdra/
├─ main.py                    # App entrypoint (calls render_app)
├─ src/
│  ├─ config.py               # Pydantic settings (reads .env)
│  ├─ core/
│  │  └─ db_client.py         # Cosdata client manager + hybrid helper
│  ├─ services/
│  │  ├─ embedder.py          # SentenceTransformer wrapper
│  │  ├─ parser.py            # PDF/text extraction
│  │  └─ search.py            # Hybrid search logic + filtering
│  └─ ui/
│     └─ app.py               # Streamlit UI (render_app)
├─ scripts/
│  └─ seed_db.py              # Seeds demo candidates
├─ cosdata-sdk-python/        # Bundled SDK (fallback import path)
├─ requirements.txt
├─ .env.example
└─ .env
```

## Troubleshooting
- ModuleNotFoundError (e.g., pydantic_settings)
  - Ensure you’re using the venv interpreter: `source venv/bin/activate` or use `./venv/bin/python`.
  - Install deps: `./venv/bin/python -m pip install -r requirements.txt`.

- Cannot import `Client` from `cosdata`
  - `src/core/db_client.py` prefers the bundled `cosdata-sdk-python/src`, then tries `cosdata_client`, then installed `cosdata`.
  - Ensure `cosdata-sdk-python/src` exists or `cosdata-sdk` is installed in the venv.

- Streamlit not found / command not found
  - Use the venv version: `./venv/bin/streamlit run main.py` or `./venv/bin/python -m streamlit run main.py`.

- Database unavailable
  - Check your `.env` values and that Cosdata server is running and reachable.
  - The upload tab will show a friendly error if the DB is unavailable.

## Dev notes
- `main.py` adjusts `sys.path` so `kosdra.src.*` imports work when running from repo root.
- UI hardened to avoid runtime errors on missing fields or DB outages.
