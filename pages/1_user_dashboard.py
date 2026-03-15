import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_complaints, get_cg_theme
import folium
from streamlit_folium import folium_static

def user_dashboard():
    st.markdown("# 👤 User Dashboard")
    
    df = get_complaints()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Complaints", len(df))
    with col2:
        pending = len(df[df['status'] == 'Pending'])
        st.metric("Pending", pending)
    with col3:
        resolved = len(df[df['status'] == 'Resolved'])
        st.metric("Resolved", resolved)
    with col4:
        high_sev = len(df[df['severity'] == 2])
        st.metric("High Priority", high_sev)
    
    # My Complaints (mock user filter)
    st.markdown("### 📋 My Recent Complaints")
    recent = df.tail(5)[['complaint_id', 'location', 'severity', 'status', 'created_at']]
    st.dataframe(recent, use_container_width=True)
    
    # Map
    st.markdown("### 🗺️ Pothole Heatmap")
    if not df.empty:
        m = folium.Map(location=[21.2514, 81.6299], zoom_start=8)
        for idx, row in df.iterrows():
            folium.CircleMarker(
                [row['lat'], row['lng']],
                radius=8+row['severity']*3,
                popup=f"ID: {row['complaint_id']}<br>Severity: {row['severity']}<br>Status: {row['status']}",
                color='red' if row['severity'] == 2 else 'orange' if row['severity'] == 1 else 'green',
                fill=True,
                fillOpacity=0.7
            ).add_to(m)
        folium_static(m, width=1200, height=400)