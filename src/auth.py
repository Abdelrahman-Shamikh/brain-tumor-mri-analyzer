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

# src/auth.py

def validate_session():
    # If the token isn't in state, they aren't logged in
    if "token" not in st.session_state:
        return False
    
    try:
        import jwt
        conf = st.secrets["auth"]
        # Decode without checking expiration first to see if it's even valid
        jwt.decode(st.session_state.token, conf["jwt_secret"], algorithms=[conf["jwt_algorithm"]])
        return True
    except Exception as e:
        # If the token expired or is corrupted, clear it
        if "token" in st.session_state:
            del st.session_state["token"]
        return False
    except Exception as e:
        # If token is expired or invalid, clear session
        return False
