"""
Main Streamlit Application for LDB (Ekstraksi Dokumen Imigrasi)
Enhanced with Database Integration
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import configurations and components
from config import APP_CONFIG, PAGE_CONFIG
from auth import AuthManager
from database import DatabaseManager
from components import Dashboard

# Import your existing modules (adjust imports based on your current structure)
try:
    from extractors import *  # Your existing extractors
    from file_handler import *  # Your existing file handler
    from helpers import *  # Your existing helpers
    from ui_components import *  # Your existing UI components
except ImportError as e:
    st.error(f"Error importing existing modules: {e}")
    st.info("Please ensure your existing modules are properly structured.")

def initialize_app():
    """Initialize the Streamlit application"""
    st.set_page_config(**PAGE_CONFIG)
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2a5298;
    }
    
    .sidebar-info {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar(user, auth_manager):
    """Render sidebar with user info and navigation"""
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-info">
            <h3>👋 Selamat datang!</h3>
            <p><strong>{user['full_name'] or user['username']}</strong></p>
            <p>Role: <span style="color: #2a5298;">{user['role'].title()}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation menu
        st.subheader("📋 Menu Navigasi")
        
        # Main pages
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        if st.button("📄 Ekstraksi Dokumen", use_container_width=True):
            st.session_state.current_page = "extraction"
            st.rerun()
        
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()
        
        # Admin only pages
        if user['role'] == 'admin':
            st.divider()
            st.subheader("👑 Admin Menu")
            
            if st.button("👥 User Management", use_container_width=True):
                st.session_state.current_page = "user_management"
                st.rerun()
        
        st.divider()
        
        # Settings and logout
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.current_page = "settings"
            st.rerun()
        
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            auth_manager.logout()

def render_extraction_page(user, db_manager):
    """Render document extraction page"""
    st.markdown('<div class="main-header"><h1>📄 Ekstraksi Dokumen Imigrasi</h1></div>', unsafe_allow_html=True)
    
    # File upload section
    st.subheader("📤 Upload Dokumen")
    
    uploaded_file = st.file_uploader(
        "Pilih file dokumen (PDF, JPG, PNG)",
        type=['pdf', 'jpg', 'jpeg', 'png'],
        help="Maksimal ukuran file 50MB"
    )
    
    if uploaded_file is not None:
        # Display file info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Nama File:** {uploaded_file.name}")
        
        with col2:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.info(f"**Ukuran:** {file_size_mb:.2f} MB")
        
        with col3:
            file_type = uploaded_file.type
            st.info(f"**Tipe:** {file_type}")
        
        # Document type selection
        st.subheader("📋 Pilih Jenis Dokumen")
        
        doc_type = st.selectbox(
            "Jenis Dokumen",
            options=list(DOCUMENT_TYPES.keys()),
            format_func=lambda x: f"{x} - {DOCUMENT_TYPES[x]['name']}"
        )
        
        # Extract button
        if st.button("🚀 Mulai Ekstraksi", type="primary", use_container_width=True):
            with st.spinner("Sedang memproses dokumen..."):
                try:
                    import time
                    start_time = time.time()
                    
                    # TODO: Replace with your actual extraction logic
                    # This is a placeholder - integrate with your existing extractors.py
                    extraction_results = {
                        "status": "success",
                        "data": {
                            "nama": "John Doe",
                            "nomor_paspor": "A1234567",
                            "kebangsaan": "Indonesia"
                        }
                    }
                    
                    processing_time = time.time() - start_time
                    
                    # Log extraction to database
                    extraction_id = db_manager.log_extraction(
                        user_id=user['id'],
                        filename=uploaded_file.name,
                        file_size=uploaded_file.size,
                        document_type=doc_type,
                        extracted_data=extraction_results,
                        processing_time=processing_time,
                        status="completed"
                    )
                    
                    # Log activity
                    db_manager.log_activity(
                        user_id=user['id'],
                        action="DOCUMENT_EXTRACTED",
                        details=f"Successfully extracted {doc_type} document: {uploaded_file.name}"
                    )
                    
                    st.success("✅ Ekstraksi berhasil!")
                    
                    # Display results
                    st.subheader("📊 Hasil Ekstraksi")
                    
                    if extraction_results["status"] == "success":
                        for key, value in extraction_results["data"].items():
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                        
                        # Download options
                        st.subheader("💾 Download Hasil")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # TODO: Implement Excel export
                            st.download_button(
                                label="📊 Download Excel",
                                data="placeholder_excel_data",
                                file_name=f"extraction_{extraction_id}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        
                        with col2:
                            # TODO: Implement JSON export
                            import json
                            json_data = json.dumps(extraction_results, indent=2)
                            st.download_button(
                                label="📄 Download JSON",
                                data=json_data,
                                file_name=f"extraction_{extraction_id}.json",
                                mime="application/json"
                            )
                    
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {str(e)}")
                    
                    # Log failed extraction
                    db_manager.log_extraction(
                        user_id=user['id'],
                        filename=uploaded_file.name,
                        file_size=uploaded_file.size,
                        document_type=doc_type,
                        extracted_data={"error": str(e)},
                        processing_time=0,
                        status="failed"
                    )

def render_settings_page(user, db_manager):
    """Render settings page"""
    st.markdown('<div class="main-header"><h1>⚙️ Pengaturan</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👤 Profil", "🔐 Keamanan"])
    
    with tab1:
        st.subheader("Informasi Profil")
        
        with st.form("profile_form"):
            full_name = st.text_input("Nama Lengkap", value=user.get('full_name', ''))
            email = st.text_input("Email", value=user.get('email', ''))
            
            if st.form_submit_button("💾 Simpan Perubahan"):
                # TODO: Implement profile update
                st.success("Profil berhasil diperbarui!")
    
    with tab2:
        st.subheader("Ubah Password")
        
        with st.form("password_form"):
            current_password = st.text_input("Password Saat Ini", type="password")
            new_password = st.text_input("Password Baru", type="password")
            confirm_password = st.text_input("Konfirmasi Password Baru", type="password")
            
            if st.form_submit_button("🔐 Ubah Password"):
                if new_password == confirm_password:
                    # TODO: Implement password change
                    st.success("Password berhasil diubah!")
                else:
                    st.error("Konfirmasi password tidak cocok!")

def main():
    """Main application function"""
    # Initialize app
    initialize_app()
    
    # Initialize components
    auth_manager = AuthManager()
    db_manager = DatabaseManager()
    dashboard = Dashboard(db_manager)
    
    # Require authentication
    if not auth_manager.require_auth():
        return
    
    # Get current user
    current_user = auth_manager.get_current_user()
    
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Render sidebar
    render_sidebar(current_user, auth_manager)
    
    # Render main content based on current page
    if st.session_state.current_page == "dashboard":
        if current_user['role'] == 'admin':
            dashboard.render_admin_dashboard(current_user)
        else:
            dashboard.render_user_dashboard(current_user)
    
    elif st.session_state.current_page == "extraction":
        render_extraction_page(current_user, db_manager)
    
    elif st.session_state.current_page == "analytics":
        st.markdown('<div class="main-header"><h1>📊 Analytics</h1></div>', unsafe_allow_html=True)
        st.info("Halaman analytics akan segera hadir!")
    
    elif st.session_state.current_page == "user_management" and current_user['role'] == 'admin':
        st.markdown('<div class="main-header"><h1>👥 User Management</h1></div>', unsafe_allow_html=True)
        dashboard.render_user_management()
    
    elif st.session_state.current_page == "settings":
        render_settings_page(current_user, db_manager)
    
    else:
        st.error("Halaman tidak ditemukan!")

if __name__ == "__main__":
    main()
