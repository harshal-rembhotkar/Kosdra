import streamlit as st
import json
from ..services.search import search_candidates
from ..services.parser import extract_text_from_file
from ..services.embedder import EmbedderService
from ..core.db_client import db
import time

def render_app():
    st.set_page_config(page_title="TalentScout", layout="wide", page_icon="🕵️‍♀️")
    
    # Styling
    st.markdown("""
    <style>
        .card {
            background: #1E1E1E; border: 1px solid #333; border-radius: 8px; padding: 20px; margin-bottom: 10px; border-left: 4px solid #4CAF50;
        }
        .tag { background: #333; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

    st.title("🕵️‍♀️ TalentScout")
    st.caption("Context-Aware Recruitment Engine")

    # Sidebar
    with st.sidebar:
        st.header("Filters")
        strictness = st.slider("Strictness", 0.0, 1.0, 0.5)
        
        st.subheader("Requirements")
        f_us = st.checkbox("🇺🇸 US Citizen")
        f_asian = st.checkbox("🌏 Asian Citizen")
        f_sec = st.checkbox("🔐 Clearance")
        
        filters = {}
        if f_us: filters["visa"] = "US Citizen"
        if f_asian: filters["visa"] = "Asian Citizen"
        if f_sec: filters["clearance"] = "Secret"

    # Main Tabs
    t_search, t_upload = st.tabs(["🔍 Search", "📤 Upload"])

    with t_search:
        query = st.text_area("Job Description", height=80, value="Senior Python engineer with leadership skills.")
        
        if st.button("Find Candidates", type="primary"):
            with st.spinner("Searching..."):
                results = search_candidates(query, strictness, filters)
            
            if not results:
                st.warning("No matches found.")
            else:
                st.success(f"Found {len(results)} Candidates")
                for r in results:
                    meta = r.get("metadata", {})
                    st.markdown(f"""
                    <div class="card">
                        <h3>{meta.get('name')} <span style="font-size:0.8em; color:#888">({meta.get('role')})</span></h3>
                        <div style="margin:10px 0;">
                            <span class="tag">📍 {meta.get('location')}</span>
                            <span class="tag">🛂 {meta.get('visa')}</span>
                        </div>
                        <p style="color:#CCC;">{r.get('text')}</p>
                    </div>
                    """, unsafe_allow_html=True)

    with t_upload:
        files = st.file_uploader("Upload Resumes", accept_multiple_files=True)
        if files and st.button("Process"):
            col = db.get_collection()
            bar = st.progress(0)
            
            batch = []
            for i, f in enumerate(files):
                text = extract_text_from_file(f)
                vec = EmbedderService.encode(text)
                batch.append({
                    "id": f"upl-{int(time.time())}-{i}",
                    "dense_values": vec,
                    "text": text,
                    "metadata": {"name": f.name, "role": "Applicant", "visa": "Unknown"}
                })
                bar.progress((i+1)/len(files))
            
            with col.transaction() as txn:
                txn.batch_upsert_vectors(batch)
            st.success("Uploaded!")
