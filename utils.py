import cv2
import numpy as np
from ultralytics import YOLO
import pandas as pd
from datetime import datetime
import streamlit as st
import os
import zipfile

class PotholeDetector:
    def __init__(self, model_path='best.pt'):
        # Handle ZIP file automatically
        model_path = self._ensure_model_file(model_path)
        try:
            self.model = YOLO(model_path)
            st.success("✅ YOLO model loaded successfully!")
            self.severity_colors = {0: '🟢 Low', 1: '🟡 Medium', 2: '🔴 High'}
        except Exception as e:
            st.error(f"❌ Model loading failed: {e}")
            st.info("📥 Please place 'best.pt' or 'best.pt.zip' in the folder")
            self.model = None
    
    def _ensure_model_file(self, model_path):
        """Auto-extract best.pt.zip if needed"""
        if model_path.endswith('.zip'):
            st.info("📦 Extracting model from ZIP...")
            with zipfile.ZipFile(model_path, 'r') as zip_ref:
                zip_ref.extractall('.')
            # Find best.pt in extracted files
            for root, dirs, files in os.walk('.'):
                if 'best.pt' in files:
                    model_path = os.path.join(root, 'best.pt')
                    st.success(f"✅ Extracted model to: {model_path}")
                    return model_path
        
        # Check if best.pt exists
        if not os.path.exists(model_path):
            possible_paths = ['best.pt', 'best.pt.zip', 'weights/best.pt', 'models/best.pt']
            for path in possible_paths:
                if os.path.exists(path):
                    st.success(f"✅ Found model at: {path}")
                    return path
        
        return model_path
    
    def detect_potholes(self, image_path):
        if self.model is None:
            return [], cv2.imread(image_path)
        
        try:
            results = self.model(image_path)
            detections = []
            
            for r in results:
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        
                        area = (x2 - x1) * (y2 - y1)
                        severity = 0
                        if area > 5000: severity = 2
                        elif area > 2000: severity = 1
                        
                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(conf),
                            'severity': severity,
                            'severity_label': self.severity_colors[severity]
                        })
            
            annotated = results[0].plot() if len(results) > 0 else cv2.imread(image_path)
            return detections, annotated
        except Exception as e:
            st.error(f"Detection error: {e}")
            return [], cv2.imread(image_path)

# Database functions (same as before)
def init_db():
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists('data/complaints.csv'):
        df = pd.DataFrame(columns=[
            'complaint_id', 'location', 'lat', 'lng', 'severity', 
            'image_path', 'status', 'created_at', 'resolved_at'
        ])
        df.to_csv('data/complaints.csv', index=False)

def add_complaint(location, lat, lng, severity, image_path):
    df = pd.read_csv('data/complaints.csv')
    new_complaint = {
        'complaint_id': f'CG-PH-{len(df)+1:04d}',
        'location': location,
        'lat': lat,
        'lng': lng,
        'severity': severity,
        'image_path': image_path,
        'status': 'Pending',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'resolved_at': ''
    }
    df = pd.concat([df, pd.DataFrame([new_complaint])], ignore_index=True)
    df.to_csv('data/complaints.csv', index=False)
    return new_complaint['complaint_id']

def get_complaints():
    try:
        return pd.read_csv('data/complaints.csv')
    except:
        return pd.DataFrame()

def update_complaint_status(complaint_id, status, resolved_at=None):
    df = pd.read_csv('data/complaints.csv')
    df.loc[df['complaint_id'] == complaint_id, 'status'] = status
    if resolved_at:
        df.loc[df['complaint_id'] == complaint_id, 'resolved_at'] = resolved_at
    df.to_csv('data/complaints.csv', index=False)

def get_cg_theme():
    return {"primary": "#2E7D32", "secondary": "#FF6F00", "background": "#F5F5F5"}