import streamlit as st
from database.models import DatabaseManager
from typing import Optional, Dict
import time

class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0
        if 'last_attempt_time' not in st.session_state:
            st.session_state.last_attempt_time = 0
    
    def login_form(self):
        """Display login form"""
        st.title("🔐 Login - Ekstraksi Dokumen Imigrasi")
        
        # Check for rate limiting
        current_time = time.time()
        if (st.session_state.login_attempts >= 3 and 
            current_time - st.session_state.last_attempt_time < 300):  # 5 minutes
            st.error("Terlalu banyak percobaan login. Silakan coba lagi dalam 5 menit.")
            return False
        
        with st.form("login_form"):
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("### Masuk ke Sistem")
                username = st.text_input("Username", placeholder="Masukkan username")
                password = st.text_input("Password", type="password", placeholder="Masukkan password")
                
                col_login, col_register = st.columns(2)
                
                with col_login:
                    login_clicked = st.form_submit_button("🚀 Login", use_container_width=True)
                
                with col_register:
                    register_clicked = st.form_submit_button("📝 Daftar", use_container_width=True)
        
        if login_clicked:
            if username and password:
                user = self.db.authenticate_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.session_state.login_attempts = 0
                    
                    # Log successful login
                    self.db.log_activity(
                        user_id=user['id'],
                        action="LOGIN_SUCCESS",
                        details=f"User {username} logged in successfully"
                    )
                    
                    st.success("Login berhasil! Mengalihkan...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    st.session_state.last_attempt_time = current_time
                    
                    # Log failed login
                    self.db.log_activity(
                        user_id=None,
                        action="LOGIN_FAILED",
                        details=f"Failed login attempt for username: {username}"
                    )
                    
                    st.error("Username atau password salah!")
            else:
                st.error("Silakan isi username dan password!")
        
        if register_clicked:
            st.session_state.show_register = True
            st.rerun()
        
        # Show default credentials info
        with st.expander("ℹ️ Informasi Login Default"):
            st.info("""
            **Akun Default:**
            - Username: `admin`
            - Password: `admin123`
            
            Silakan ganti password setelah login pertama kali.
            """)
        
        return False
    
    def register_form(self):
        """Display registration form"""
        st.title("📝 Registrasi Pengguna Baru")
        
        with st.form("register_form"):
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("### Buat Akun Baru")
                username = st.text_input("Username", placeholder="Pilih username unik")
                email = st.text_input("Email", placeholder="alamat@email.com")
                full_name = st.text_input("Nama Lengkap", placeholder="Nama lengkap Anda")
                password = st.text_input("Password", type="password", placeholder="Minimal 6 karakter")
                confirm_password = st.text_input("Konfirmasi Password", type="password", placeholder="Ulangi password")
                
                col_register, col_back = st.columns(2)
                
                with col_register:
                    register_clicked = st.form_submit_button("✅ Daftar", use_container_width=True)
                
                with col_back:
                    back_clicked = st.form_submit_button("⬅️ Kembali", use_container_width=True)
        
        if register_clicked:
            if not all([username, email, full_name, password, confirm_password]):
                st.error("Semua field harus diisi!")
            elif len(password) < 6:
                st.error("Password minimal 6 karakter!")
            elif password != confirm_password:
                st.error("Konfirmasi password tidak cocok!")
            elif "@" not in email:
                st.error("Format email tidak valid!")
            else:
                success = self.db.create_user(
                    username=username,
                    email=email,
                    password=password,
                    full_name=full_name
                )
                
                if success:
                    # Log registration
                    self.db.log_activity(
                        user_id=None,
                        action="USER_REGISTERED",
                        details=f"New user registered: {username} ({email})"
                    )
                    
                    st.success("Registrasi berhasil! Silakan login dengan akun baru Anda.")
                    time.sleep(2)
                    st.session_state.show_register = False
                    st.rerun()
                else:
                    st.error("Username atau email sudah digunakan!")
        
        if back_clicked:
            st.session_state.show_register = False
            st.rerun()
    
    def logout(self):
        """Logout user"""
        if st.session_state.user:
            # Log logout
            self.db.log_activity(
                user_id=st.session_state.user['id'],
                action="LOGOUT",
                details=f"User {st.session_state.user['username']} logged out"
            )
        
        st.session_state.authenticated = False
        st.session_state.user = None
        if 'show_register' in st.session_state:
            del st.session_state.show_register
        st.rerun()
    
    def require_auth(self):
        """Decorator to require authentication"""
        self.initialize_session_state()
        
        if not st.session_state.authenticated:
            if 'show_register' in st.session_state and st.session_state.show_register:
                self.register_form()
            else:
                self.login_form()
            return False
        return True
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current logged in user"""
        return st.session_state.user if st.session_state.authenticated else None
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        user = self.get_current_user()
        return user and user.get('role') == 'admin'
