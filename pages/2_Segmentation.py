import streamlit as st
from src.auth import validate_session
import numpy as np
from PIL import Image
import cv2

# 1. Page Configuration
st.set_page_config(page_title="Tumor Segmentation | NeuroScan AI", layout="wide")

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

medical_header("Brain Tumor Segmentation", icon="🔬")

st.markdown("""
Extract the precise tumor boundaries using deep segmentation. 
Upload MRI scans to generate **binary masks** and **overlay visualizations**.
""")

uploaded_files = st.file_uploader(
    "Upload MRI scans for segmentation", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True,
    key="seg_uploader"
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.error("🚨 Batch limit: 5 images.")
    else:
        for idx, file in enumerate(uploaded_files):
            st.write("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            
            try:
                raw_img = Image.open(file).convert('RGB')
                
                with st.spinner(f"Segmenting {file.name}..."):
                    # Execute Segmentation (Returns 0/1 mask as numpy array)
                    mask = engine.run_segmentation(raw_img)
                    
                    # Process images for display
                    mask_visual = (mask * 255).astype(np.uint8)
                    
                    # Create an overlay (Red tint where mask is 1)
                    img_np = np.array(raw_img.resize((256, 256)))
                    overlay = img_np.copy()
                    overlay[mask == 1] = [255, 0, 0] # Red color for tumor
                    combined = cv2.addWeighted(img_np, 0.7, overlay, 0.3, 0)

                    with col1:
                        st.image(raw_img, caption="Original MRI", use_container_width=True)
                    
                    with col2:
                        st.image(mask_visual, caption="AI Binary Mask", use_container_width=True)
                        # Provide mask download
                        mask_pil = Image.fromarray(mask_visual)
                        import io
                        buf = io.BytesIO()
                        mask_pil.save(buf, format="PNG")
                        st.download_button("Download Mask", buf.getvalue(), f"mask_{file.name}.png", "image/png")

                    with col3:
                        st.image(combined, caption="Tumor Overlay", use_container_width=True)
                        st.info("Red region indicates the identified tumor mass.")

            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")

st.markdown("---")
st.caption("AI segmentation is based on the DynUNet architecture trained on multisequence MRI.")
