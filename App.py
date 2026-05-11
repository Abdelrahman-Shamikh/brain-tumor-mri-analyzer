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

# Apply medical-themed CSS styling from utils
set_page_container_style()

# Initialize Database
db = DatabaseManager()

def login_user(email, password):
    """Handles the authentication logic and session creation."""
    user = db.execute_query("SELECT * FROM users WHERE email=%s", (email,), fetch=True)
    if user and verify_password(password, user[0]['password_hash']):
        # Store JWT and user info in session
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
                        st.success("✅ Authenticated. Redirecting to Classification Module...")
                        time.sleep(1.5)
                        # REDIRECT: Move user to the first analysis page automatically
                        st.switch_page("pages/1_Classification.py")
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
            
            agree = st.checkbox("I confirm that I am a licensed doctor/medical professional and agree to the medical usage terms.")
            
            if st.button("Register Account", use_container_width=True):
                if not agree:
                    st.error("You must confirm your medical status to register.")
                elif new_pwd != conf_pwd:
                    st.error("Passwords do not match.")
                elif len(new_pwd) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    try:
                        h_pwd = hash_password(new_pwd)
                        db.execute_query(
                            "INSERT INTO users (fullname, email, password_hash, is_doctor) VALUES (%s,%s,%s,%s)",
                            (new_name, new_email, h_pwd, True)
                        )
                        st.success("Account created successfully! Please switch to the Login tab.")
                    except Exception as e:
                        st.error(f"Registration failed: Email may already be in use.")

        st.markdown("---")
        st.caption("NeuroScan AI v1.0.0 | Production-Ready Medical Interface")

    else:
        # --- AUTHENTICATED DASHBOARD ---
        medical_header(f"Welcome, {st.session_state.user['fullname']}")
        
        st.sidebar.title("Navigation")
        if st.sidebar.button("🚪 Log Out", use_container_width=True):
            # Clear all session data
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("""
        ### Clinical Overview
        Select a diagnostic module below to begin analyzing patient MRI scans.
        """)

        # Quick Access Cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🧠")
            if st.button("Tumor Classification", use_container_width=True):
                st.switch_page("pages/1_Classification.py")
            st.caption("Identify tumor types (Glioma, Meningioma, etc.)")

        with col2:
            st.markdown("### 🔬")
            if st.button("Tumor Segmentation", use_container_width=True):
                st.switch_page("pages/2_Segmentation.py")
            st.caption("Generate binary masks and isolate tumor regions.")

        with col3:
            st.markdown("### 📏")
            if st.button("Size Estimation", use_container_width=True):
                st.switch_page("pages/3_Size_Estimation.py")
            st.caption("Calculate relative tumor area and dimensions.")

        st.info("💡 Tip: You can also use the sidebar on the left to switch between modules at any time.")

    # --- Global Footer ---
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        "<center><small><b>AI assistance only — not a substitute for professional diagnosis.</b><br>"
        "All data processed is subject to medical privacy standards.</small></center>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
