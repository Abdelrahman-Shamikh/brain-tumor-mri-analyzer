import streamlit as st
from PIL import Image
import io
import logging

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NeuroScanAI")

def validate_image(uploaded_file):
    """
    Checks if the uploaded file is a valid, uncorrupted image without closing the handle.
    """
    try:
        # Create a copy so we don't close the original file handle
        img_copy = Image.open(io.BytesIO(uploaded_file.getvalue()))
        img_copy.verify() 
        return True
    except Exception as e:
        logger.error(f"Image validation failed for {uploaded_file.name}: {e}")
        return False

def process_image_for_display(uploaded_file):
    try:
        return Image.open(uploaded_file).convert("RGB")
    except Exception as e:
        st.error(f"Could not display image: {e}")
        return None

def medical_header(title, icon="🩺"):
    st.markdown(f"## {icon} {title}")
    st.markdown("---")

def set_page_container_style():
    st.markdown("""
        <style>
        .main { background-color: #F8F9FA; }
        .stMetric {
            background-color: #FFFFFF;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        div.stButton > button:first-child {
            background-color: #007BFF;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
        }
        div.stButton > button:hover {
            background-color: #0056b3;
            color: white;
            border: none;
        }
        .stAlert { border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)

def logout_user():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
