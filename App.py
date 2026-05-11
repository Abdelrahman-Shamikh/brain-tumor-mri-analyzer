import streamlit as st
from src.database import DatabaseManager
from src.auth import hash_password, verify_password, create_token, validate_session

st.set_page_config(page_title="NeuroScan AI Portal", page_icon="🧠", layout="centered")

db = DatabaseManager()

# Footer Disclaimer Component
def footer():
    st.markdown("---")
    st.caption("⚠️ AI assistance only — not a substitute for professional diagnosis. Developed for licensed medical use.")

if not validate_session():
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.header("Sign In")
        email = st.text_input("Email", key="l_email")
        password = st.text_input("Password", type="password", key="l_pwd")
        if st.button("Access Dashboard"):
            user = db.execute_query("SELECT * FROM users WHERE email=%s", (email,), fetch=True)
            if user and verify_password(password, user[0]['password_hash']):
                st.session_state.token = create_token(user[0]['id'])
                st.session_state.user = user[0]
                st.success("Authenticated. Redirecting...")
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with tab2:
        st.header("Medical Professional Registration")
        f_name = st.text_input("Full Name")
        r_email = st.text_input("Email Address")
        r_pwd = st.text_input("Password", type="password")
        c_pwd = st.text_input("Confirm Password", type="password")
        agree = st.checkbox("I confirm that I am a licensed doctor/medical professional and agree to the medical usage terms.")
        
        if st.button("Create Account"):
            if r_pwd != c_pwd:
                st.warning("Passwords do not match.")
            elif not agree:
                st.warning("You must confirm medical licensing to proceed.")
            else:
                h_pwd = hash_password(r_pwd)
                db.execute_query("INSERT INTO users (fullname, email, password_hash, is_doctor) VALUES (%s,%s,%s,%s)", 
                                 (f_name, r_email, h_pwd, True))
                st.success("Account created! Please switch to Login tab.")
    footer()
else:
    st.title("Main Dashboard")
    st.sidebar.success(f"Logged in: {st.session_state.user['fullname']}")
    if st.sidebar.button("Log Out"):
        del st.session_state.token
        st.rerun()
    
    st.markdown("""
    ### Welcome to NeuroScan AI
    Please select a module from the sidebar to begin analysis.
    
    - **Classification:** Categorize the type of tumor.
    - **Segmentation:** Isolate the tumor area.
    - **Estimation:** Measure volume and pixel-wise dimensions.
    """)
    footer()