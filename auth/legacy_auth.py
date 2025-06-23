"""
Legacy authentication functions for backward compatibility
"""
import streamlit as st

def logout():
    """Legacy logout function for backward compatibility"""
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Set logged out state
    st.session_state.logged_in = False
    st.session_state.authenticated = False
    st.session_state.user = None
    
    st.success("✅ Logout berhasil!")
    st.rerun()

def login():
    """Legacy login function - redirects to new auth system"""
    st.warning("⚠️ Menggunakan sistem login lama. Silakan gunakan sistem baru.")
    
    # Simple legacy login
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Simple validation for legacy system
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_role = "admin"
            st.success("✅ Login berhasil!")
            st.rerun()
        else:
            st.error("❌ Username atau password salah!")
