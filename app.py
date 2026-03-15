import streamlit as st

st.set_page_config(page_title="APIS — Automated Pothole Intelligence System", layout="wide")

import utils.model_utils as mu
import utils.db as db
from utils.ui import render_shell

render_shell(
    page_title="Control Center — Overview",
    page_subtitle="Monitor model health, data flow and complaint lifecycle for the state of Chhattisgarh.",
)

st.sidebar.markdown('<div class="sidebar-header">APIS Control Center</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="nav-group-label">DETECTION</div>', unsafe_allow_html=True)
st.sidebar.markdown("- Detect\n- Batch\n- Compare")
st.sidebar.markdown('<div class="nav-group-label">ANALYTICS</div>', unsafe_allow_html=True)
st.sidebar.markdown("- Dashboard\n- Complaints")
st.sidebar.markdown('<div class="nav-group-label">SYSTEM</div>', unsafe_allow_html=True)
st.sidebar.markdown("- Settings & About")

st.sidebar.subheader("Models availability")
for m in mu.available_models():
    status = "found" if m["exists"] else "missing"
    st.sidebar.write(f"- **{m['name']}** — {status}")

db.init_db()

st.markdown("### How it works")
st.markdown(
    """
1. **Capture** — Upload dashcam or drone road imagery.  
2. **Detect** — APIS (YOLOv8) localises and classifies potholes.  
3. **File** — Auto-generate geo-tagged complaints in the local registry.  
4. **Track** — Monitor resolution on the dashboard and complaints screen.
"""
)