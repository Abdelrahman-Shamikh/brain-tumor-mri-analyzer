import streamlit as st
from PIL import Image
import pandas as pd
import plotly.express as px
from src.inference import MedicalEngine
from src.auth import validate_session

# --- Security Gate ---
if not validate_session():
    st.error("🔒 Access Denied. Please log in from the Home page.")
    st.stop()

# --- Page Config ---
st.set_page_config(page_title="Classification | NeuroScan AI", layout="wide")

# --- Initialize Inference Engine ---
@st.cache_resource
def get_engine():
    return MedicalEngine()

engine = get_engine()

# --- UI Header ---
st.title("🧠 Brain Tumor Classification")
st.markdown("""
Upload up to **5 MRI images** for automated diagnostic classification. 
The system identifies: *Glioma, Meningioma, Pituitary, or No Tumor*.
""")

# --- File Upload Logic ---
files = st.file_uploader(
    "Choose MRI Scans", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True
)

if files:
    if len(files) > 5:
        st.error("🚨 Batch limit exceeded. Please upload a maximum of 5 images.")
    else:
        # Create columns for batch display if multiple files are uploaded
        for idx, f in enumerate(files):
            st.write("---")
            col_img, col_res = st.columns([1, 2])
            
            # Load and Pre-process Image
            try:
                img = Image.open(f).convert('RGB')
                col_img.image(img, caption=f"MRI Scan: {f.name}", use_container_width=True)
                
                with st.spinner(f"Analyzing scan {idx+1}..."):
                    # Execute Inference
                    class_idx, confidence, probabilities = engine.run_classification(img)
                    
                    # Map Classes (Ensure these match your training order)
                    classes = ["Glioma", "Meningioma", "No Tumor", "Pituitary"]
                    prediction = classes[class_idx]
                    
                    # Display Results
                    with col_res:
                        st.subheader(f"Analysis Result: {prediction}")
                        
                        # Metric visualizer
                        st.progress(float(confidence))
                        st.metric("Confidence Score", f"{confidence * 100:.2f}%")
                        
                        # Probability Chart
                        df_probs = pd.DataFrame({
                            "Tumor Type": classes,
                            "Probability": probabilities
                        })
                        
                        fig = px.bar(
                            df_probs, 
                            x="Tumor Type", 
                            y="Probability",
                            color="Probability",
                            color_continuous_scale="Blues",
                            text_auto='.2%'
                        )
                        fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Clinical Note
                        if prediction == "No Tumor":
                            st.success("✅ The model detected no visible tumorous growth in this scan.")
                        else:
                            st.warning(f"⚠️ Findings are consistent with **{prediction}**. Clinical correlation required.")

            except Exception as e:
                st.error(f"Error processing {f.name}: {e}")

# --- Footer ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("© 2026 NeuroScan AI | Confirmed Medical Professional Access Only.")
st.markdown("---")
st.info("💡 **AI assistance only** — this tool is a decision-support system and not a substitute for a radiologist's diagnosis.")