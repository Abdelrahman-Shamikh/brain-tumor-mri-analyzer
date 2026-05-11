import streamlit as st
from src.database import DatabaseManager
from src.auth import hash_password, verify_password, create_token, validate_session

# --- 1. SET PAGE CONFIG (ONLY ONCE) ---
st.set_page_config(
    page_title="NeuroScan AI Portal", 
    page_icon="🧠", 
    layout="centered"
)

# --- 2. INITIALIZE DATABASE ---
db = DatabaseManager()

# --- 3. HELPER COMPONENTS ---
def footer():
    st.markdown("---")
    st.caption("⚠️ AI assistance only — not a substitute for professional diagnosis. Developed for licensed medical use.")

# --- 4. MAIN LOGIC ---

# CHECK SESSION IMMEDIATELY
if validate_session():
    # --- AUTHENTICATED UI ---
    st.title(f"Welcome, {st.session_state.user['fullname']}")
    st.sidebar.success(f"Logged in: {st.session_state.user['fullname']}")
    
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("""
    ### Clinical Dashboard
    Please select a specialized analysis module to begin.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧠 Classification", use_container_width=True):
            st.switch_page("pages/1_Classification.py")
    
    with col2:
        if st.button("🔬 Segmentation", use_container_width=True):
            st.switch_page("pages/2_Segmentation.py")
            
    with col3:
        if st.button("📏 Size Estimation", use_container_width=True):
            st.switch_page("pages/3_Size_Estimation.py")
            
    st.info("💡 You can also use the sidebar on the left to navigate between modules.")
    footer()
    
else:
    # --- LOGIN / REGISTRATION UI ---
    st.title("🩺 NeuroScan AI")
    st.subheader("Institutional Login")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        email = st.text_input("Email", key="l_email")
        password = st.text_input("Password", type="password", key="l_pwd")
        
        if st.button("Access Dashboard", use_container_width=True):
            user = db.execute_query("SELECT * FROM users WHERE email=%s", (email,), fetch=True)
            if user and verify_password(password, user[0]['password_hash']):
                st.session_state.token = create_token(user[0]['id'])
                st.session_state.user = user[0]
                st.success("Authenticated. Redirecting...")
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with tab2:
        st.header("Medical Professional Registration")
        f_name = st.text_input("Full Name (with Title)")
        r_email = st.text_input("Email Address")
        r_pwd = st.text_input("Password", type="password")
        c_pwd = st.text_input("Confirm Password", type="password")
        agree = st.checkbox("I confirm that I am a licensed doctor and agree to the medical usage terms.")
        
        if st.button("Create Account", use_container_width=True):
            if r_pwd != c_pwd:
                st.warning("Passwords do not match.")
            elif len(r_pwd) < 8:
                st.warning("Password must be at least 8 characters.")
            elif not agree:
                st.warning("You must confirm medical licensing to proceed.")
            else:
                try:
                    h_pwd = hash_password(r_pwd)
                    db.execute_query(
                        "INSERT INTO users (fullname, email, password_hash, is_doctor) VALUES (%s,%s,%s,%s)", 
                        (f_name, r_email, h_pwd, True)
                    )
                    st.success("Account created! Please switch to Login tab.")
                except Exception as e:
                    st.error("Registration failed. Email may already be registered.")
    
    footer()
