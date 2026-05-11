import jwt
import datetime
from passlib.context import CryptContext
import streamlit as st

# Schemes should match what you used to hash the initial passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)

def create_token(user_id):
    conf = st.secrets["auth"]
    payload = {
        "sub": str(user_id), # Ensure sub is a string
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=int(conf["jwt_expiration_hours"]))
    }
    return jwt.encode(payload, conf["jwt_secret"], algorithm=conf["jwt_algorithm"])

def validate_session():
    if "token" not in st.session_state:
        return False
    
    try:
        conf = st.secrets["auth"]
        # Decoding will automatically check 'exp' and throw an error if expired
        jwt.decode(st.session_state.token, conf["jwt_secret"], algorithms=[conf["jwt_algorithm"]])
        return True
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception):
        # Clear token if invalid or expired
        if "token" in st.session_state:
            del st.session_state["token"]
        return False
