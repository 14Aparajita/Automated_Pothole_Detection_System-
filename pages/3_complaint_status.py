import streamlit as st
from utils import get_complaints

def complaint_status():
    st.markdown("# 📊 Track Complaint Status")
    
    complaint_id = st.text_input("Enter Complaint ID (e.g., CG-PH-0001)")
    
    if complaint_id:
        df = get_complaints()
        complaint = df[df['complaint_id'] == complaint_id]
        
        if not complaint.empty:
            row = complaint.iloc[0]
            st.success(f"✅ **Complaint Found!**")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Status", row['status'])
            with col2:
                st.metric("Severity", row['severity'])
            with col3:
                st.metric("Location", row['location'])
            
            if row['image_path'] and row['image_path'].startswith('temp/'):
                try:
                    st.image(row['image_path'], caption="Pothole Image")
                except:
                    st.info("Image not available")
        else:
            st.error("❌ Complaint ID not found!")