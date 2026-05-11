import streamlit as st
import time
from src.database import DatabaseManager
from src.auth import hash_password, verify_password, create_token, validate_session
from src.utils import set_page_container_style, medical_header

# --- Page Configuration ---
st.set_page_config(
    page_title="NeuroScan AI | Medical Portal",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Apply medical-themed CSS styling
set_page_container_style()

# Initialize Database
db = DatabaseManager()

def login_user(email, password):
    """Handles authentication and session creation."""
    user = db.execute_query("SELECT * FROM users WHERE email=%s", (email,), fetch=True)
    if user and verify_password(password, user[0]['password_hash']):
        st.session_state.token = create_token(user[0]['id'])
        st.session_state.user = user[0]
        return True
    return False

def main():
    # --- AUTHENTICATION GATE ---
    if not validate_session():
        st.title("🩺 NeuroScan AI Portal")
        st.subheader("Advanced Brain MRI Analysis Suite")
        
        tab1, tab2 = st.tabs(["🔐 Clinical Login", "📝 Professional Registration"])
        
        with tab1:
            email = st.text_input("Institutional Email", placeholder="doctor@hospital.com")
            pwd = st.text_input("Password", type="password")
            
            if st.button("Sign In to Dashboard", use_container_width=True):
                if email and pwd:
                    if login_user(email, pwd):
                        st.success("✅ Authenticated. Accessing Clinical Hub...")
                        time.sleep(1)
                        st.rerun() # Rerun to show the dashboard cards
                    else:
                        st.error("Invalid credentials. Please check your email and password.")
                else:
                    st.warning("Please fill in all fields.")

        with tab2:
            st.info("Registration is restricted to licensed medical professionals.")
            new_name = st.text_input("Full Name (with Title)")
            new_email = st.text_input("Email Address")
            new_pwd = st.text_input("Create Password", type="password")
            conf_pwd = st.text_input("Confirm Password", type="password")
            
            agree = st.checkbox("I confirm that I am a licensed medical professional.")
            
            if st.button("Register Account", use_container_width=True):
                if not agree:
                    st.error("You must confirm your medical status.")
                elif new_pwd != conf_pwd:
                    st.error("Passwords do not match.")
                else:
                    try:
                        h_pwd = hash_password(new_pwd)
                        db.execute_query(
                            "INSERT INTO users (fullname, email, password_hash, is_doctor) VALUES (%s,%s,%s,%s)",
                            (new_name, new_email, h_pwd, True)
                        )
                        st.success("Account created! You can now log in.")
                    except Exception:
                        st.error("Registration failed: Email may already be in use.")

    else:
        # --- AUTHENTICATED DASHBOARD (Cards Shown First) ---
        medical_header(f"Welcome, {st.session_state.user['fullname']}")
        
        st.markdown("### 🏥 Diagnostic Control Center")
        st.write("Select a specialized AI module below to begin patient analysis.")

        # Dashboard Grid
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("### 🧠 \n**Classification**")
            st.caption("Identify tumor types (Glioma, Meningioma, Pituitary).")
            if st.button("Launch Classifier", use_container_width=True):
                st.switch_page("pages/1_Classification.py")

        with col2:
            st.success("### 🔬 \n**Segmentation**")
            st.caption("Generate binary masks to isolate tumor regions.")
            if st.button("Launch Segmenter", use_container_width=True):
                st.switch_page("pages/2_Segmentation.py")

        with col3:
            st.warning("### 📏 \n**Size Estimation**")
            st.caption("Calculate relative area and mass ratios.")
            if st.button("Launch Estimator", use_container_width=True):
                st.switch_page("pages/3_Size_Estimation.py")

        # Sidebar Logout
        st.sidebar.title("NeuroScan AI")
        if st.sidebar.button("🚪 Log Out", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # --- Footer ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        "<center><small><b>Research Use Only</b> | Subject to HIPAA/GDPR Standards</small></center>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
