import streamlit as st
from PIL import Image
from src.inference import MedicalEngine
from src.auth import validate_session

if not validate_session():
    st.stop()

st.title("Tumor Size Estimation")
engine = MedicalEngine()

files = st.file_uploader("Upload MRI", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if files:
    for f in files:
        img = Image.open(f)
        size_raw = engine.run_size_estimation(img)
        
        st.image(img, width=400)
        st.metric("Estimated Tumor Area (Relative)", f"{size_raw * 100:.2f}%")
        
        st.info("""
        **Metric Summary:**
        The percentage represents the ratio of identified tumor pixels 
        relative to the total image area based on the loaded intensity model.
        """)