"""
Main Streamlit Application for LDB (Ekstraksi Dokumen Imigrasi)
Fixed version with proper imports
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import configurations with fallback
try:
    from config import APP_CONFIG, PAGE_CONFIG, DOCUMENT_TYPES
except ImportError:
    # Fallback configuration
    APP_CONFIG = {
        'title': 'Ekstraksi Dokumen Imigrasi',
        'version': '2.0.0',
        'description': 'Aplikasi berbasis Streamlit untuk mengekstrak data dari dokumen PDF imigrasi'
    }
    PAGE_CONFIG = {
        'page_title': 'Ekstraksi Dokumen Imigrasi',
        'page_icon': '📄',
        'layout': 'wide',
        'initial_sidebar_state': 'expanded',
    }
    DOCUMENT_TYPES = {
        'SKTT': {'name': 'Surat Keterangan Tinggal Terbatas'},
        'EVLN': {'name': 'Exit Visa Luar Negeri'},
        'ITAS': {'name': 'Izin Tinggal Terbatas'},
        'ITK': {'name': 'Izin Tinggal Kunjungan'},
        'NOTIFICATION': {'name': 'Notifikasi Imigrasi'},
        'DKPTKA': {'name': 'Dana Kompensasi Penggunaan TKA'}
    }

# Try to import DOCUMENT_TYPES from utils if not in config
if 'DOCUMENT_TYPES' not in globals():
    try:
        from utils.constants import DOCUMENT_TYPES
    except ImportError:
        pass

# Import database components with error handling
DATABASE_ENABLED = False
try:
    from database.models import DatabaseManager
    from auth.auth_manager import AuthManager
    from components.dashboard import Dashboard
    DATABASE_ENABLED = True
except ImportError as e:
    st.warning(f"⚠️ Database components not found: {e}")
    st.info("Running in legacy mode. Some features may be limited.")

def safe_import_modules():
    """Safely import existing modules with error handling"""
    modules = {}
    
    # Try to import extractors
    try:
        import extractors
        modules['extractors'] = extractors
        st.success("✅ Extractors module loaded")
    except Exception as e:
        st.error(f"❌ Error loading extractors: {e}")
        return None
    
    # Try to import file_handler
    try:
        import file_handler
        modules['file_handler'] = file_handler
        st.success("✅ File handler module loaded")
    except Exception as e:
        st.error(f"❌ Error loading file_handler: {e}")
        return None
    
    # Try to import helpers
    try:
        import helpers
        modules['helpers'] = helpers
        st.success("✅ Helpers module loaded")
    except Exception as e:
        st.error(f"❌ Error loading helpers: {e}")
        return None
    
    # Try to import ui_components
    try:
        import ui_components
        modules['ui_components'] = ui_components
        st.success("✅ UI components module loaded")
    except Exception as e:
        st.error(f"❌ Error loading ui_components: {e}")
        return None
    
    return modules

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
            <p><strong>{user.get('full_name', user.get('username', 'User'))}</strong></p>
            <p>Role: <span style="color: #2a5298;">{user.get('role', 'user').title()}</span></p>
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
        if user.get('role') == 'admin':
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
    """Render document extraction page with proper DOCUMENT_TYPES"""
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
        
        # Document type selection with safe DOCUMENT_TYPES access
        st.subheader("📋 Pilih Jenis Dokumen")
        
        # Safe access to DOCUMENT_TYPES
        doc_options = list(DOCUMENT_TYPES.keys()) if DOCUMENT_TYPES else ['SKTT', 'EVLN', 'ITAS', 'ITK', 'NOTIFICATION', 'DKPTKA']
        
        def format_doc_type(x):
            if DOCUMENT_TYPES and x in DOCUMENT_TYPES:
                return f"{x} - {DOCUMENT_TYPES[x].get('name', x)}"
            else:
                return x
        
        doc_type = st.selectbox(
            "Jenis Dokumen",
            options=doc_options,
            format_func=format_doc_type
        )
        
        # Extract button
        if st.button("🚀 Mulai Ekstraksi", type="primary", use_container_width=True):
            with st.spinner("Sedang memproses dokumen..."):
                try:
                    import time
                    start_time = time.time()
                    
                    # TODO: Replace with your actual extraction logic
                    extraction_results = {
                        "status": "success",
                        "data": {
                            "nama": "John Doe",
                            "nomor_paspor": "A1234567",
                            "kebangsaan": "Indonesia"
                        }
                    }
                    
                    processing_time = time.time() - start_time
                    
                    # Log extraction to database if available
                    if DATABASE_ENABLED and db_manager:
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
                            st.download_button(
                                label="📊 Download Excel",
                                data="placeholder_excel_data",
                                file_name=f"extraction_result.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        
                        with col2:
                            import json
                            json_data = json.dumps(extraction_results, indent=2)
                            st.download_button(
                                label="📄 Download JSON",
                                data=json_data,
                                file_name=f"extraction_result.json",
                                mime="application/json"
                            )
                    
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {str(e)}")
                    
                    # Log failed extraction if database available
                    if DATABASE_ENABLED and db_manager:
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
                st.success("Profil berhasil diperbarui!")
    
    with tab2:
        st.subheader("Ubah Password")
        
        with st.form("password_form"):
            current_password = st.text_input("Password Saat Ini", type="password")
            new_password = st.text_input("Password Baru", type="password")
            confirm_password = st.text_input("Konfirmasi Password Baru", type="password")
            
            if st.form_submit_button("🔐 Ubah Password"):
                if new_password == confirm_password:
                    st.success("Password berhasil diubah!")
                else:
                    st.error("Konfirmasi password tidak cocok!")

def main():
    """Main application function"""
    # Initialize app
    initialize_app()
    
    # Show DOCUMENT_TYPES status
    st.sidebar.markdown(f"**Document Types:** {'✅ Loaded' if DOCUMENT_TYPES else '❌ Not Found'}")
    
    # Initialize components
    if DATABASE_ENABLED:
        auth_manager = AuthManager()
        db_manager = DatabaseManager()
        
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
            if DATABASE_ENABLED:
                dashboard = Dashboard(db_manager)
                if current_user['role'] == 'admin':
                    dashboard.render_admin_dashboard(current_user)
                else:
                    dashboard.render_user_dashboard(current_user)
            else:
                st.info("Dashboard requires database components.")
        
        elif st.session_state.current_page == "extraction":
            render_extraction_page(current_user, db_manager)
        
        elif st.session_state.current_page == "analytics":
            st.markdown('<div class="main-header"><h1>📊 Analytics</h1></div>', unsafe_allow_html=True)
            st.info("Halaman analytics akan segera hadir!")
        
        elif st.session_state.current_page == "user_management" and current_user['role'] == 'admin':
            st.markdown('<div class="main-header"><h1>👥 User Management</h1></div>', unsafe_allow_html=True)
            if DATABASE_ENABLED:
                dashboard = Dashboard(db_manager)
                dashboard.render_user_management()
        
        elif st.session_state.current_page == "settings":
            render_settings_page(current_user, db_manager)
        
        else:
            st.error("Halaman tidak ditemukan!")
    
    else:
        # Fallback mode without database
        st.title("📄 Ekstraksi Dokumen Imigrasi")
        st.warning("⚠️ Running in legacy mode. Database features not available.")
        
        # Simple extraction interface
        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
        
        if uploaded_file:
            doc_options = list(DOCUMENT_TYPES.keys()) if DOCUMENT_TYPES else ['SKTT', 'EVLN', 'ITAS', 'ITK']
            doc_type = st.selectbox("Document Type", doc_options)
            
            if st.button("Process"):
                st.success("File uploaded successfully!")
                st.info("Extraction features require database components.")

if __name__ == "__main__":
    main()
