import jwt
import datetime
from passlib.context import CryptContext
import streamlit as st

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)

def create_token(user_id):
    conf = st.secrets["auth"]
    payload = {
        "sub": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=int(conf["jwt_expiration_hours"]))
    }
    return jwt.encode(payload, conf["jwt_secret"], algorithm=conf["jwt_algorithm"])

def validate_session():
    # Check if both token and user object exist in the current session
    if "token" not in st.session_state or "user" not in st.session_state:
        return False
    
    try:
        conf = st.secrets["auth"]
        # Decode the token to check for expiration
        jwt.decode(
            st.session_state.token, 
            conf["jwt_secret"], 
            algorithms=[conf["jwt_algorithm"]]
        )
        return True
    except Exception as e:
        # If token is expired or invalid, clear session
        return False
