import streamlit as st
import pandas as pd
from utils import get_complaints, update_complaint_status, get_cg_theme

def admin_dashboard():
    st.markdown("# 👨‍💼 Admin Dashboard")
    st.markdown("**🔐 Admin authentication required**")
    
    # Simple password (use secrets in production)
    if st.text_input("Admin Password") == "cgadmin123":
        df = get_complaints()
        
        # Admin Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Complaints", len(df))
        with col2:
            avg_resolution = df['resolved_at'].apply(lambda x: pd.Timestamp.now() if x=='' else pd.Timestamp(x)).diff().mean()
            st.metric("Avg Resolution Time", f"{avg_resolution.days} days")
        with col3:
            resolution_rate = len(df[df['status']=='Resolved'])/len(df)*100
            st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
        
        # Complaint Management
        st.markdown("### 📋 All Complaints")
        for idx, row in df.iterrows():
            with st.expander(f"**{row['complaint_id']}** - {row['location']}"):
                col1, col2 = st.columns([3,1])
                with col1:
                    st.write(f"**Severity**: {row['severity']} | **Status**: {row['status']}")
                    st.write(f"**Created**: {row['created_at']}")
                with col2:
                    if st.button(f"Mark Resolved", key=f"resolve_{idx}"):
                        update_complaint_status(row['complaint_id'], 'Resolved', pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))
                        st.success("✅ Marked as Resolved!")
                        st.rerun()
    else:
        st.warning("❌ Incorrect password")