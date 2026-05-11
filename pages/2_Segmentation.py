import streamlit as st
import numpy as np
from PIL import Image
from src.inference import MedicalEngine
from src.auth import validate_session
import cv2

if not validate_session():
    st.warning("Please login to access this module.")
    st.stop()

st.title("Tumor Segmentation")
engine = MedicalEngine()

files = st.file_uploader("Upload MRI", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if files:
    if len(files) > 5:
        st.error("Limit: 5 images.")
    else:
        for f in files:
            img = Image.open(f)
            mask = engine.run_segmentation(img)
            
            col1, col2 = st.columns(2)
            col1.image(img, caption="Original MRI", use_container_width=True)
            
            # Create color mask overlay
            mask_img = (mask * 255).astype(np.uint8)
            col2.image(mask_img, caption="AI Segmentation Mask", use_container_width=True)
            
            # Download button for mask
            result_img = Image.fromarray(mask_img)
            st.download_button("Download Mask", data=f.getvalue(), file_name=f"mask_{f.name}")