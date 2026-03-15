# pages/01_Detect.py
import streamlit as st

st.set_page_config(page_title="Detect - APIS", layout="wide")

from utils.model_utils import available_models, load_model
from utils.infer_utils import save_uploaded_file, model_predict_on_image, draw_boxes_on_image
import utils.geo_utils as gu
import utils.db as db
from utils.ui import render_shell
import cv2, os, uuid

render_shell(
    page_title="Detect — Single Image",
    page_subtitle="Upload a road image and run the approved APIS model to detect potholes.",
)

models = available_models()
available = [m for m in models if m["exists"]]
if not available:
    st.error("No models found in /models. Add model_a.pt etc.")
    st.stop()

model_choice = st.selectbox("Choose Model", [m["name"] for m in available])
selected_model_path = [m["path"] for m in available if m["name"]==model_choice][0]

uploaded = st.file_uploader("Upload Road Image", type=["jpg","jpeg","png"])
if uploaded:
    image_path = save_uploaded_file(uploaded)
    image = cv2.imread(image_path)
    st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Uploaded Image", use_column_width=True)

    if st.button("Run Detection"):
        with st.spinner("Running model..."):
            model = load_model(selected_model_path)
            detections = model_predict_on_image(model, image, conf=0.35)
        if not detections:
            st.info("No detections.")
        else:
            st.success(f"{len(detections)} detections")
            drawn = draw_boxes_on_image(image.copy(), detections)
            st.image(cv2.cvtColor(drawn, cv2.COLOR_BGR2RGB), caption="Detections", use_column_width=True)

            # show table
            rows=[]
            for i,d in enumerate(detections):
                lat,lon = gu.mock_gps_nearby()
                rows.append({
                    "Index": i+1,
                    "BBox": [round(x,1) for x in d["bbox"]],
                    "Conf": round(d["confidence"],3),
                    "Severity": d["severity"],
                    "Lat": lat,
                    "Lon": lon
                })
            st.table(rows)

            if st.button("File complaints for all"):
                cnt=0
                for d in detections:
                    lat, lon = gu.mock_gps_nearby()
                    pid = f"PID_{uuid.uuid4().hex[:8]}"
                    db.add_complaint(pid, model_choice, image_path, lat, lon, d["severity"], reinspection_days=7)
                    cnt+=1
                st.success(f"Filed {cnt} complaints (local DB).")