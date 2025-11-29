import streamlit as st
import pandas as pd
import plotly.express as px
import time
import json

from ..services.search import search_candidates
from ..services.parser import extract_text_from_file
from ..services.embedder import EmbedderService
from ..core.db_client import db

st.set_page_config(page_title="Kosdra HR", layout="wide", page_icon="🦁")

if 'shortlist' not in st.session_state:
    st.session_state.shortlist = []

def toggle_shortlist(candidate):
    exists = next((item for item in st.session_state.shortlist if item['id'] == candidate['id']), None)
    if exists:
        st.session_state.shortlist.remove(exists)
        st.toast(f"Removed {candidate['name']}")
    else:
        st.session_state.shortlist.append(candidate)
        st.toast(f"Shortlisted {candidate['name']}")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .metric-card { background-color: #1E1E1E; padding: 15px; border-radius: 8px; border: 1px solid #333; text-align: center; }
    .candidate-card { background-color: #1E1E1E; border: 1px solid #333; border-radius: 10px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #FFD700; }
    .candidate-card:hover { border-color: #FFA500; transform: translateY(-2px); transition: 0.2s; }
    .tag { background: #333; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 5px; color: #EEE; }
    .match-reason { font-size: 0.85rem; color: #888; font-style: italic; margin-top: 8px; }
    .pro-badge { background: linear-gradient(45deg, #FFD700, #FFA500); color: black; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; vertical-align: super; }
</style>
""", unsafe_allow_html=True)

def render_app():
    if 'shortlist' not in st.session_state:
        st.session_state['shortlist'] = []
    with st.sidebar:
        st.title("🦁 Kosdra")
        st.caption("Intelligent Recruitment OS")
        st.divider()
        
        st.header("Filters Panel")
        strictness = st.slider("Keyword Strictness", 0.0, 1.0, 0.6, help="Balance between Vibe (0.0) and Facts (1.0)")
        
        st.subheader("Mandatory Requirements")
        f_us = st.checkbox("US Citizen")
        f_asian = st.checkbox("Asian Citizen")
        f_sec = st.checkbox("Remote")
        
        st.subheader("Experience & Keywords")
        min_exp = st.number_input("Minimum Experience (years)", min_value=0, max_value=50, value=0, key="flt_min_exp")
        must_kw = st.text_input("Must-have keywords (comma-separated)", placeholder="python, kubernetes", key="flt_must")
        excl_kw = st.text_input("Exclude keywords (comma-separated)", placeholder="junior, internship", key="flt_excl")

        st.subheader("Role & Location")
        role_contains = st.text_input("Role contains", placeholder="Software Engineer", key="flt_role")
        loc_contains = st.text_input("Location contains", placeholder="San Francisco", key="flt_loc")

        st.subheader("Search Tuning")
        results_count = st.slider("Results count", 5, 50, 15, help="How many results to return", key="flt_topk")
        fusion_balance = st.slider("Hybrid fusion constant (k)", 10, 200, 60, help="Higher leans more on dense embeddings", key="flt_fusion")
        min_score_pct = st.slider("Minimum match score (%)", 0, 100, 0, help="Filter out low-scoring matches", key="flt_min_score")

        if st.button("Reset Filters"):
            for k in ["flt_min_exp", "flt_must", "flt_excl", "flt_role", "flt_loc", "flt_topk", "flt_fusion"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

        filters = {}
        if f_us: filters["visa"] = "US Citizen"
        if f_asian: filters["visa"] = "Asian Citizen"
        if f_sec: filters["clearance"] = "Top Secret"
        if min_exp and min_exp > 0: filters["min_exp"] = int(min_exp)
        if must_kw.strip(): filters["must"] = [k.strip() for k in must_kw.split(",") if k.strip()]
        if excl_kw.strip(): filters["exclude"] = [k.strip() for k in excl_kw.split(",") if k.strip()]
        if role_contains.strip(): filters["role_contains"] = role_contains.strip()
        if loc_contains.strip(): filters["location_contains"] = loc_contains.strip()
        if min_score_pct and int(min_score_pct) > 0:
            filters["min_score"] = float(min_score_pct) / 100.0

        st.markdown("---")
        st.markdown("**Premium Features** <span class='pro-badge'>PRO</span>", unsafe_allow_html=True)
        st.checkbox("Hide PII (Bias Redaction)", disabled=True)
        st.checkbox("Team Comments", disabled=True)

    t_dash, t_search, t_upload = st.tabs(["📊 Dashboard", "🔍 Talent Search", "📤 Import Resumes"])

    with t_dash:
        st.markdown("### Recruitment Overview")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Active Candidates", "1,240", "+12%")
        c2.metric("Interviews", "45", "+5")
        c3.metric("Offers Sent", "12", "2 pending")
        c4.metric("Time to Hire", "18 Days", "-2 Days")
        st.markdown("---")
        
        df = pd.DataFrame({
            "Skill": ["Python", "Kubernetes", "React", "AWS", "Java", "Go"],
            "Candidates": [450, 320, 280, 310, 150, 90]
        })
        fig = px.bar(
            df,
            x="Skill",
            y="Candidates",
            title="Talent Pool by Skill",
            color="Candidates",
            color_continuous_scale="sunset"
        )
        st.plotly_chart(fig, use_container_width=True)

    with t_search:
        c_search, c_short = st.columns([3, 1])
        with c_search:
            query = st.text_area("Search Query / Job Description", height=80, 
                               placeholder="e.g. Senior Python Engineer with PMP certification...",
                               value="Senior Python Engineer with PMP certification")
            
            if st.button("Find Candidates", type="primary"):
                with st.spinner("Running Hybrid Search..."):
                    results = search_candidates(
                        query,
                        strictness,
                        filters,
                        top_k=results_count,
                        fusion_k=float(fusion_balance),
                    )
                
                if not results:
                    st.warning("No candidates match your specific criteria.")
                else:
                    st.success(f"Found {len(results)} qualified candidates")
                    st.session_state['last_results'] = results
                    for r in results:
                        meta = r.get("metadata") or {}
                        # Clamp score to 0..1 for percentage display
                        try:
                            _raw_score = float(r.get('score') or 0)
                            _clamped = max(0.0, min(1.0, _raw_score))
                        except Exception:
                            _clamped = 0.0
                        score_pct = int(_clamped * 100)

                        # Safe display values
                        disp_name = meta.get('name') or 'Candidate'
                        disp_role = meta.get('role') or 'Applicant'
                        disp_loc = meta.get('location') or 'Unknown'
                        disp_visa = meta.get('visa') or 'Unknown'
                        disp_exp = meta.get('exp', 'Unknown')

                        is_shortlisted = any(c['id'] == r.get('id') for c in st.session_state.get('shortlist', []))
                        btn_label = "➖ Remove" if is_shortlisted else "➕ Shortlist"
                        
                        match_reason = r.get("match_explanation", "Semantic Match")

                        snippet = (r.get('text') or '')[:200]
                        if not snippet:
                            snippet = "No preview available"
                        hl_terms = set()
                        if filters.get('must'):
                            hl_terms.update([t for t in filters['must']])
                        for t in query.split():
                            if len(t) > 3:
                                hl_terms.add(t)
                        for t in sorted(hl_terms, key=len, reverse=True):
                            try:
                                snippet = snippet.replace(t, f"<mark>{t}</mark>")
                                snippet = snippet.replace(t.capitalize(), f"<mark>{t.capitalize()}</mark>")
                            except Exception:
                                pass

                        st.markdown(f"""
                        <div class="candidate-card">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <h3 style="margin:0; color:#FFF;">{disp_name}</h3>
                                    <span style="color:#AAA; font-size:0.9rem;">{disp_role}</span>
                                </div>
                                <div style="text-align:right;">
                                    <span style="font-size:1.5rem; font-weight:800; color:#FFD700;">{score_pct}%</span>
                                </div>
                            </div>
                            <div style="margin:10px 0;">
                                <span class="tag">📍 {disp_loc}</span>
                                <span class="tag">🛂 {disp_visa}</span>
                                <span class="tag">💡 {disp_exp} Yrs Exp</span>
                            </div>
                            <p style=\"color:#CCC; font-size:0.95rem;\">{snippet}...</p>
                            <div class="match-reason">ℹ️ {match_reason}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2 = st.columns([1, 5])
                        with c1:
                            if st.button(btn_label, key=f"sl_{r.get('id')}"):
                                toggle_shortlist({"name": disp_name, "id": r.get("id")})
                                st.rerun()
                        with c2:
                            st.download_button("📄 Download JSON", data=json.dumps(r, indent=2), file_name=f"{disp_name}.json", key=f"dl_{r.get('id','unknown')}")

        with c_short:
            st.markdown("### ⭐ Shortlist")
            if not st.session_state.get('shortlist', []):
                st.info("No candidates selected.")
            else:
                for item in st.session_state.get('shortlist', []):
                    st.markdown(f"**{item['name']}**")
                
                if st.button("Export Shortlist (CSV)"):
                    df = pd.DataFrame(st.session_state.shortlist)
                    csv = df.to_csv().encode('utf-8')
                    st.download_button("Download CSV", csv, "shortlist.csv", "text/csv")
                if st.button("Clear Shortlist"):
                    st.session_state['shortlist'] = []
                    st.rerun()

            st.markdown("---")
            st.markdown("### 📤 Export Results")
            if st.session_state.get('last_results'):
                df_all = pd.DataFrame([
                    {
                        "id": x.get("id"),
                        "name": (x.get("metadata", {}) or {}).get("name"),
                        "role": (x.get("metadata", {}) or {}).get("role"),
                        "location": (x.get("metadata", {}) or {}).get("location"),
                        "visa": (x.get("metadata", {}) or {}).get("visa"),
                        "exp": (x.get("metadata", {}) or {}).get("exp"),
                        "score": x.get("score"),
                    }
                    for x in st.session_state['last_results']
                ])
                csv_all = df_all.to_csv(index=False).encode('utf-8')
                st.download_button("Download Results CSV", csv_all, "results.csv", "text/csv")

    with t_upload:
        st.header("Import Resumes")
        st.markdown("Drag and drop PDF/Word resumes here to auto-index them.")
        with st.expander("Paste a resume (quick test)"):
            p_name = st.text_input("Name", key="paste_name")
            p_role = st.text_input("Role", key="paste_role", placeholder="Software Engineer")
            p_loc = st.text_input("Location", key="paste_loc", placeholder="Remote")
            p_visa = st.text_input("Visa", key="paste_visa", placeholder="US Citizen / Asian Citizen / Unknown")
            p_clear = st.text_input("Clearance", key="paste_clear", placeholder="None / Top Secret")
            p_exp = st.number_input("Experience (years)", min_value=0, max_value=50, value=3, key="paste_exp")
            p_text = st.text_area("Resume Text", height=150, key="paste_text", placeholder="Paste resume/plain text here...")
            c1p, c2p = st.columns(2)
            with c1p:
                if st.button("Index Pasted Resume"):
                    if not p_text.strip():
                        st.warning("Please paste resume text.")
                    else:
                        try:
                            col = db.get_collection()
                            vec = EmbedderService.encode(p_text)
                            item = {
                                "id": f"paste-{int(time.time())}",
                                "dense_values": vec,
                                "text": p_text,
                                "metadata": {"name": p_name or "Candidate", "role": p_role or "Applicant", "location": p_loc or "", "visa": p_visa or "Unknown", "clearance": p_clear or "None", "exp": int(p_exp)},
                            }
                            with col.transaction() as txn:
                                txn.batch_upsert_vectors([item])
                            st.success("Pasted resume indexed. Go to Talent Search to query.")
                        except Exception as e:
                            st.error(f"Failed to index pasted resume: {e}")
            with c2p:
                if st.button("Index Sample Resume"):
                    sample_text = (
                        "Senior Software Engineer with 7 years experience in Python, AWS, Kubernetes, and React. "
                        "PMP certified. US Citizen. Led teams to build scalable microservices and CI/CD pipelines."
                    )
                    try:
                        col = db.get_collection()
                        vec = EmbedderService.encode(sample_text)
                        item = {
                            "id": f"sample-{int(time.time())}",
                            "dense_values": vec,
                            "text": sample_text,
                            "metadata": {"name": "Sample Candidate", "role": "Software Engineer", "location": "Remote", "visa": "US Citizen", "clearance": "None", "exp": 7},
                        }
                        with col.transaction() as txn:
                            txn.batch_upsert_vectors([item])
                        st.success("Sample resume indexed. Go to Talent Search to query.")
                    except Exception as e:
                        st.error(f"Failed to index sample resume: {e}")
        files = st.file_uploader("", accept_multiple_files=True)
        if files and st.button("Process Batch"):
            try:
                col = db.get_collection()
            except Exception as e:
                st.error(f"Database unavailable: {e}")
                return
            bar = st.progress(0)
            batch = []
            for i, f in enumerate(files):
                text = extract_text_from_file(f)
                vec = EmbedderService.encode(text)
                visa = "US Citizen" if "US Citizen" in text else ("Asian Citizen" if "Asian" in text else "Unknown")
                batch.append({
                    "id": f"upl-{int(time.time())}-{i}",
                    "dense_values": vec,
                    "text": text,
                    "metadata": {"name": f.name, "role": "Applicant", "visa": visa, "clearance": "None"}
                })
                bar.progress((i+1)/len(files))
            
            with col.transaction() as txn:
                txn.batch_upsert_vectors(batch)
            txn.poll_completion(target_status="complete", max_attempts=10)
            st.success(f"✅ Successfully indexed {len(files)} resumes!")