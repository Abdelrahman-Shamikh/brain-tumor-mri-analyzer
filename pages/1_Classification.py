import streamlit as st
from src.auth import validate_session
import pandas as pd
import plotly.express as px
from PIL import Image

# 1. MUST BE FIRST: Page Configuration
st.set_page_config(page_title="Tumor Classification | NeuroScan AI", layout="wide")

# 2. SECOND: Security Gate
if not validate_session():
    # If the session is invalid, redirect to login page immediately
    st.switch_page("App.py")
    st.stop()

# 3. THIRD: Imports and Engine Initialization
# We import these inside the session check to save memory if access is denied
from src.inference import MedicalEngine
from src.utils import medical_header

@st.cache_resource
def load_engine():
    return MedicalEngine()

engine = load_engine()

# --- UI Header ---
medical_header("Brain Tumor Classification", icon="🧠")

st.markdown("""
Upload up to **5 MRI images** (JPG, JPEG, PNG). 
The AI will analyze the scans and provide a diagnostic classification among: 
**Glioma, Meningioma, Pituitary, or No Tumor.**
""")

# --- File Upload Section ---
uploaded_files = st.file_uploader(
    "Drag and drop MRI scans here", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True,
    key="clf_uploader"
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.error("🚨 Batch limit exceeded. Please upload a maximum of 5 images.")
    else:
        # Iterate through uploaded scans
        for idx, file in enumerate(uploaded_files):
            st.write("---")
            col_img, col_res = st.columns([1, 1.5])
            
            try:
                # Process image
                raw_img = Image.open(file).convert('RGB')
                
                with col_img:
                    st.image(raw_img, caption=f"Scan: {file.name}", use_container_width=True)
                
                with col_res:
                    with st.spinner(f"Analyzing {file.name}..."):
                        # Execute Inference using your specific logic (150x150 resize)
                        class_idx, confidence, probabilities = engine.run_classification(raw_img)
                        
                        # Label Mapping
                        labels = ["Glioma", "Meningioma", "No Tumor", "Pituitary"]
                        prediction = labels[class_idx]
                        
                        # Result Display
                        st.subheader(f"Finding: {prediction}")
                        st.write(f"**AI Confidence Score:** `{confidence * 100:.2f}%`")
                        
                        # Probability Visualization
                        df_probs = pd.DataFrame({
                            "Diagnosis": labels,
                            "Probability": probabilities
                        })
                        
                        fig = px.bar(
                            df_probs, 
                            x="Diagnosis", 
                            y="Probability",
                            color="Probability",
                            color_continuous_scale="Blues",
                            text_auto='.2%'
                        )
                        fig.update_layout(height=250, margin=dict(l=0, r=0, t=20, b=0))
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Medical Guidance Alert
                        if prediction == "No Tumor":
                            st.success("✅ Analysis complete: No tumorous growth detected.")
                        else:
                            st.warning(f"⚠️ High probability of **{prediction}**. Please correlate with clinical symptoms.")

            except Exception as e:
                st.error(f"Could not process image {file.name}: {e}")

# --- Global Footer ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("NeuroScan AI System | Production Inference Engine")
