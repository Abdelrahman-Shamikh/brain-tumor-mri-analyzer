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
    Checks if the uploaded file is a valid, uncorrupted image.
    """
    try:
        img = Image.open(uploaded_file)
        img.verify()  # Verify it's actually an image
        return True
    except Exception as e:
        logger.error(f"Image validation failed for {uploaded_file.name}: {e}")
        return False

def process_image_for_display(uploaded_file):
    """
    Safely opens an image for UI preview.
    """
    try:
        return Image.open(uploaded_file).convert("RGB")
    except Exception as e:
        st.error(f"Could not display image: {e}")
        return None

def medical_header(title, icon="🩺"):
    """
    Standardized header used across all medical modules.
    """
    st.markdown(f"## {icon} {title}")
    st.markdown("---")

def set_page_container_style():
    """
    Custom CSS to make the Streamlit UI look more professional and 'medical'.
    """
    st.markdown("""
        <style>
        .main {
            background-color: #F8F9FA;
        }
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
        }
        .stAlert {
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

def logout_user():
    """
    Clears the session and redirects to home.
    """
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()