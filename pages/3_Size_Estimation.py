import streamlit as st
from src.auth import validate_session
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Size Estimation | NeuroScan AI", layout="wide")

# 2. Security Gate
if not validate_session():
    st.switch_page("App.py")
    st.stop()

# 3. Imports and Engine
from src.inference import MedicalEngine
from src.utils import medical_header

@st.cache_resource
def load_engine():
    return MedicalEngine()

engine = load_engine()

medical_header("Tumor Size Estimation", icon="📏")

st.markdown("""
Estimate the relative mass and size of the detected tumor. 
This calculation is based on **pixel intensity ratios** and **spatial occupancy**.
""")

uploaded_files = st.file_uploader(
    "Upload MRI scans for measurement", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True,
    key="size_uploader"
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.error("🚨 Batch limit: 5 images.")
    else:
        for idx, file in enumerate(uploaded_files):
            st.write("---")
            col_img, col_metric = st.columns([1, 1])
            
            try:
                raw_img = Image.open(file).convert('RGB')
                
                with col_img:
                    st.image(raw_img, caption=f"Scan: {file.name}", use_container_width=True)
                
                with col_metric:
                    with st.spinner("Calculating metrics..."):
                        # Execute Size Estimation
                        relative_size = engine.run_size_estimation(raw_img)
                        
                        st.subheader("Metric Summary")
                        st.metric("Estimated Tumor Mass Ratio", f"{relative_size * 100:.2f}%")
                        
                        # Spatial details
                        st.write("**Analysis Details:**")
                        st.write(f"- Resolution: {raw_img.size[0]}x{raw_img.size[1]} pixels")
                        st.write(f"- Mode: Grayscale-intensity mapped")
                        
                        st.info(f"""
                        **Interpretation:**
                        The tumor occupies approximately **{relative_size * 100:.2f}%** of the total pixel 
                        intensity volume in this slice. Please compare this across sagittal, 
                        coronal, and axial planes for total volumetric estimation.
                        """)

            except Exception as e:
                st.error(f"Error analyzing {file.name}: {e}")

st.markdown("---")
st.warning("Spatial measurements (mm/cm) require DICOM metadata. PNG/JPG uploads provide relative intensity size only.")
