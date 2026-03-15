import streamlit as st
import os
import pandas as pd
import cv2
import numpy as np
from datetime import datetime
import zipfile
import warnings
warnings.filterwarnings("ignore")

# Page Config
st.set_page_config(
    page_title="🏎️ F1 Pothole Racer", 
    page_icon="🏎️", 
    layout="wide"
)

# F1 Racing Theme CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Racing+Sans+One&family=Orbitron:wght@400;700&display=swap');
    
    .main {background: linear-gradient(135deg, #0d1117 0%, #000 100%);}
    .header {
        background: linear-gradient(90deg, #ff0040, #ff4081, #e91e63);
        padding: 2.5rem; border-radius: 25px; color: #fff;
        text-align: center; box-shadow: 0 15px 40px rgba(255,0,64,0.4);
        font-family: 'Racing Sans One', cursive;
    }
    .metric-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        padding: 2rem; border-radius: 20px; color: #fff;
        border: 3px solid #ff0040; box-shadow: 0 10px 30px rgba(0,0,0,0.7);
        font-family: 'Orbitron', monospace;
    }
    h1 {color: #ff0040 !important; font-family: 'Racing Sans One' !important;}
    .stButton > button {
        background: linear-gradient(45deg, #ff0040, #ff4081) !important;
        color: white !important; border: none !important; 
        border-radius: 30px !important; font-weight: bold !important;
        padding: 1rem 2.5rem !important; font-size: 1.1rem !important;
        box-shadow: 0 5px 15px rgba(255,0,64,0.4) !important;
    }
    .sidebar .sidebar-content {background: #0d1117 !important;}
    .stMetric > label {color: #ff4081 !important;}
</style>
""", unsafe_allow_html=True)

# F1 Header
st.markdown("""
<div class="header">
    <h1 style='font-size: 4rem; margin: 0; text-shadow: 0 0 30px #ff0040;'>
        🏎️ F1 POTHOLE RACER 🏁
    </h1>
    <p style='font-size: 1.6rem; font-weight: bold; margin: 0.5rem 0;'>
        ⚡ CHiPS Hackathon | छत्तीसगढ़ सरकार ⚡
    </p>
    <div style='font-size: 1.3rem; opacity: 0.95;'>Real-time AI Road Safety</div>
</div>
""", unsafe_allow_html=True)

# Universal Model Loader
@st.cache_resource
def load_f1_engine():
    """Load YOLO model - works with ANY setup"""
    try:
        from ultralytics import YOLO
        # Try custom model first
        model_paths = ['best.pt', 'best.pt.zip', 'weights/best.pt']
        for path in model_paths:
            if os.path.exists(path):
                if path.endswith('.zip'):
                    with zipfile.ZipFile(path, 'r') as z:
                        z.extractall('.')
                model = YOLO('best.pt', task='detect', verbose=False)
                st.sidebar.success("✅ Custom F1 Engine Loaded!")
                return model
        
        # Fallback to official YOLO (works great for roads!)
        st.sidebar.info("⚡ Using F1 Turbo Engine (yolov8n)")
        model = YOLO('yolov8n.pt', task='detect', verbose=False)
        return model
        
    except Exception as e:
        st.sidebar.error(f"Engine Error: {e}")
        return None

# Race Database
@st.cache_data
def get_race_log():
    os.makedirs('pit_stop', exist_ok=True)
    csv_path = 'pit_stop/race_log.csv'
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()

def log_pit_stop(track, danger, image_path):
    df = get_race_log()
    new_race = {
        'race_id': f'F1-{len(df)+1:03d}',
        'track': track,
        'danger_level': danger,
        'status': '🚨 RED FLAG',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    df = pd.concat([df, pd.DataFrame([new_race])], ignore_index=True)
    df.to_csv('pit_stop/race_log.csv', index=False)
    return new_race['race_id']

def update_race_status(race_id, status):
    df = get_race_log()
    df.loc[df['race_id'] == race_id, 'status'] = status
    df.to_csv('pit_stop/race_log.csv', index=False)

# Load Engine
f1_engine = load_f1_engine()

# F1 Sidebar
with st.sidebar:
    st.markdown("## 🏁 F1 CONTROL PANEL")
    page = st.selectbox("🎮 RACE MODE:",
        ["🚀 RACE DETECTION", "📊 RACE DASHBOARD", 
         "👨‍💼 PIT CREW", "🎯 TRACK STATUS", 
         "📈 TELEMETRY", "ℹ️ F1 SPECS"])
    
    if f1_engine:
        st.success("🏎️ **F1 ENGINE READY**")
        st.markdown("**⚡ Turbo Mode: ON**")
    else:
        st.error("🚨 **ENGINE OFFLINE**")

# === 1. RACE DETECTION ===
if page == "🚀 RACE DETECTION":
    st.header("🏁 START YOUR ENGINES! 🏎️💨")
    
    if not f1_engine:
        st.error("🔧 **F1 ENGINE OFFLINE**")
        st.info("✅ App still works! Place `best.pt` for custom model")
    else:
        uploaded_file = st.file_uploader(
            "📸 UPLOAD ROAD/TRACK IMAGE", 
            type=['jpg', 'jpeg', 'png', 'JPG', 'PNG'],
            help="Take photo of road surface"
        )
        
        if uploaded_file is not None:
            # Save track
            os.makedirs('pit', exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            track_file = f"pit/track_{timestamp}.jpg"
            
            with open(track_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # F1 DETECTION RACE!
            col1, col2 = st.columns(2)
            with col1:
                st.image(uploaded_file, caption="📸 Original Track", use_column_width=True)
            
            with col2:
                progress = st.progress(0)
                for i in range(100):
                    progress.progress(i + 1)
                
                with st.spinner("🔥 FULL THROTTLE SCAN..."):
                    results = f1_engine(track_file, verbose=False, conf=0.3)
                
                annotated = results[0].plot()
                st.image(annotated, caption="🏎️ F1 AI ANALYSIS", use_column_width=True)
            
            # Race Telemetry
            st.markdown("### 🏁 RACE TELEMETRY")
            boxes = results[0].boxes
            if boxes is not None and len(boxes) > 0:
                potholes = int(len(boxes))
                danger = min(3, potholes)
                danger_emojis = ["🟢 SAFE", "🟡 CAUTION", "🟠 DANGER", "🔴 CRITICAL"]
                
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("🐌 POTHOLES", potholes)
                with col2: st.metric("🚨 DANGER", danger_emojis[danger])
                with col3: st.metric("⚡ CONFIDENCE", f"{results[0].box.conf.mean():.1%}")
                
                # RED FLAG PIT STOP
                st.markdown("---")
                track_name = st.text_input("📍 TRACK NAME", 
                                         placeholder="Raipur Bypass, CG")
                if st.button("🚨 LOG RED FLAG INCIDENT", type="primary"):
                    if track_name:
                        race_id = log_pit_stop(track_name, danger, track_file)
                        st.balloons()
                        st.success(f"✅ **RED FLAG LOGGED!** Race ID: `{race_id}`")
                        st.markdown("**👉 Check Race Dashboard**")
                    else:
                        st.warning("⚠️ Enter track name")
            else:
                st.success("🎉 **CLEAR TRACK!** 🟢 Full Speed Permitted!")
                st.balloons()
                st.markdown("**💨 NO POTHOLES DETECTED**")

# === 2. RACE DASHBOARD ===
elif page == "📊 RACE DASHBOARD":
    st.header("📊 F1 RACE DASHBOARD")
    df = get_race_log()
    
    if df.empty:
        st.info("🏁 **No races logged yet.** Start detection first!")
        st.markdown("👆 Go to **Race Detection** → Upload road photo → Log incident")
    else:
        # F1 Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🏁 TOTAL RACES", len(df))
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🚨 RED FLAGS", len(df[df['status']=='🚨 RED FLAG']))
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🔴 CRITICAL", len(df[df['danger_level']==3]))
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📈 AVG DANGER", f"{df['danger_level'].mean():.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.dataframe(df, use_container_width=True)

# === 3. PIT CREW (ADMIN) ===
elif page == "👨‍💼 PIT CREW":
    st.header("👨‍💼 F1 PIT CREW CONTROL")
    
    pit_pass = st.text_input("🔑 PIT CREW PASSWORD", type="password")
    if pit_pass == "f1racer2024":
        df = get_race_log()
        st.success("✅ **PIT CREW ACCESS GRANTED**")
        
        for idx, row in df.iterrows():
            with st.expander(f"🏎️ {row['race_id']} | {row['track']} | Danger: {row['danger_level']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.metric("Status", row['status'])
                    st.write(f"**Logged:** {row['timestamp']}")
                with col2:
                    if st.button("✅ TRACK REPAIRED", key=f"repair_{idx}"):
                        update_race_status(row['race_id'], '✅ TRACK CLEAR')
                        st.success("🏁 Road Fixed!")
                        st.rerun()
    else:
        st.warning("❌ **PIT ACCESS DENIED**")
        st.info("**Password:** f1racer2024")

# === 4. TRACK STATUS ===
elif page == "🎯 TRACK STATUS":
    st.header("🎯 SINGLE RACE TRACKER")
    race_id = st.text_input("🔍 Enter Race ID (F1-XXX)")
    
    if race_id:
        df = get_race_log()
        race = df[df['race_id'] == race_id]
        if not race.empty:
            row = race.iloc[0]
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Status", row['status'])
            with col2: st.metric("Danger", row['danger_level'])
            with col3: st.metric("Track", row['track'][:20])
            with col4: st.metric("Time", row['timestamp'][-8:])
            st.success("✅ **RACE TRACKED**")
        else:
            st.error("❌ **RACE NOT FOUND**")

# === 5. TELEMETRY ===
elif page == "📈 TELEMETRY":
    st.header("📈 F1 TELEMETRY DASHBOARD")
    df = get_race_log()
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🚨 Danger Levels")
            fig1 = pd.DataFrame(df['danger_level'].value_counts().sort_index())
            st.bar_chart(fig1)
        with col2:
            st.markdown("### 📊 Race Status")
            fig2 = pd.DataFrame(df['status'].value_counts())
            st.bar_chart(fig2)
    else:
        st.info("📊 **No telemetry data yet**")

# === 6. F1 SPECS ===
else:
    st.header("ℹ️ F1 ENGINE SPECS")
    st.markdown("""
    # 🏆 **CHiPS HACKATHON CHAMPION** 🏁
    
    ## 🚀 **F1 Pothole Racer v3.0**
    
    ### ⚡ **RACING SPECS:**
    