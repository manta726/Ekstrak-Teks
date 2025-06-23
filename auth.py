import hashlib
import streamlit as st

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(username, password):
    users = {
        "sinta": hash_password("sinta123"),
        "ainun": hash_password("ainun123"),
        "fatih": hash_password("fatih123")
    }
    hashed_pw = hash_password(password)
    return username in users and users[username] == hashed_pw

def login():
    if st.session_state.username and st.session_state.password:
        if check_credentials(st.session_state.username, st.session_state.password):
            st.session_state.logged_in = True
            st.session_state.login_attempt = 0
        else:
            st.session_state.login_attempt += 1

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""