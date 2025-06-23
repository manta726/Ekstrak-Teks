import streamlit as st
import shutil
import time
from datetime import datetime
from pathlib import Path
from auth import logout
from helpers import get_greeting

def render_enhanced_login_css():
    """Render enhanced modern CSS for login page"""
    st.markdown('''
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    
    /* Remove all borders */
    .stApp > div:first-child,
    div:empty {
        display: none !important;
    }
    
    * {
        border: none !important;
        outline: none !important;
    }
    
    /* Animated background */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(-45deg, #0f172a, #1e293b, #0f172a, #334155);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
        color: #f8fafc;
        position: relative;
        overflow: hidden;
    }
    
    /* Animated background gradient */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating particles background */
    .stApp::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(167, 139, 250, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(34, 197, 94, 0.1) 0%, transparent 50%);
        animation: float 20s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        33% { transform: translateY(-30px) rotate(2deg); }
        66% { transform: translateY(-20px) rotate(-2deg); }
    }
    
    /* Login card with glassmorphism */
    .login-card {
        position: relative;
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 24px;
        padding: 3rem 2.5rem;
        box-shadow: 
            0 25px 50px -12px rgba(0, 0, 0, 0.5),
            0 0 0 1px rgba(255, 255, 255, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin: 2rem auto;
        max-width: 420px;
        transform: translateY(20px);
        animation: slideUp 0.8s ease-out forwards;
        overflow: hidden;
    }
    
    /* Card slide up animation */
    @keyframes slideUp {
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    /* Subtle glow effect */
    .login-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.8), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Header with enhanced typography */
    .login-header {
        text-align: center;
        margin-bottom: 2.5rem;
        position: relative;
    }
    
    .login-header h1 {
        color: #ffffff !important;
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        margin: 0 0 0.75rem 0 !important;
        background: linear-gradient(135deg, #ffffff, #e2e8f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: none;
        letter-spacing: -0.025em;
        animation: titleGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes titleGlow {
        from { filter: drop-shadow(0 0 5px rgba(59, 130, 246, 0.3)); }
        to { filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.5)); }
    }
    
    .login-header p {
        color: #94a3b8 !important;
        font-size: 1rem !important;
        font-weight: 400 !important;
        margin: 0 !important;
        opacity: 0.9;
    }
    
    /* Enhanced divider */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, #475569, transparent) !important;
        margin: 2rem 0 2.5rem 0 !important;
        position: relative;
    }
    
    hr::after {
        content: '✦';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(30, 41, 59, 0.9);
        color: #64748b;
        padding: 0 1rem;
        font-size: 0.75rem;
    }
    
    /* Enhanced input fields */
    .stTextInput > div > div > input {
        background: rgba(51, 65, 85, 0.5) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        padding: 1rem 1.25rem !important;
        font-size: 0.95rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        background: rgba(51, 65, 85, 0.8) !important;
        box-shadow: 
            0 0 0 3px rgba(59, 130, 246, 0.2) !important,
            0 4px 20px rgba(59, 130, 246, 0.1) !important;
        transform: translateY(-2px) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #94a3b8 !important;
        opacity: 0.7;
    }
    
    /* Enhanced labels */
    .stTextInput > label {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        margin-bottom: 0.5rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 0.9;
    }
    
    /* Enhanced button with multiple states */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8, #1e40af) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        margin-top: 1.5rem !important;
        font-family: 'Inter', sans-serif !important;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 
            0 4px 15px rgba(59, 130, 246, 0.4),
            0 0 0 1px rgba(59, 130, 246, 0.2);
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af, #1e3a8a) !important;
        transform: translateY(-3px) !important;
        box-shadow: 
            0 8px 25px rgba(59, 130, 246, 0.5),
            0 0 0 1px rgba(59, 130, 246, 0.3) !important;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* Enhanced error messages */
    .stAlert {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 12px !important;
        color: #fca5a5 !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        backdrop-filter: blur(10px);
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    /* Form styling */
    .stForm {
        background: transparent !important;
        border: none !important;
    }
    
    /* Loading state (optional) */
    .loading {
        opacity: 0.7;
        pointer-events: none;
    }
    
    /* Responsive design */
    @media (max-width: 480px) {
        .login-card {
            margin: 1rem;
            padding: 2rem 1.5rem;
            border-radius: 16px;
        }
        
        .login-header h1 {
            font-size: 1.5rem !important;
        }
    }
    
    /* Dark scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(30, 41, 59, 0.3);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(59, 130, 246, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(59, 130, 246, 0.7);
    }
    </style>
    ''', unsafe_allow_html=True)

def login_page():
    # Apply enhanced CSS
    render_enhanced_login_css()
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # Header
        st.markdown('''
        <div class="login-header">
            <h1>🖥️ PT LAMAN DAVINDO BAHMAN</h1>
            <p>Sistem Ekstraksi Dokumen Imigrasi</p>
        </div>
        <hr>
        ''', unsafe_allow_html=True)
        
        # Form
        with st.form("login_form"):
            st.text_input("Username", key="username", placeholder="Masukkan username Anda")
            st.text_input("Password", type="password", key="password", placeholder="Masukkan password Anda")
            
            if st.session_state.get('login_attempt', 0) > 0:
                st.error(f"❌ Username atau password salah! (Percobaan ke-{st.session_state.login_attempt})")
            
            submit = st.form_submit_button("🔐 Login")
            
            if submit:
                from auth import login
                login()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
def render_css_styles():
    """Render simple and clean CSS styles for the application"""
    st.markdown('''
    <style>
    /* Hide Streamlit branding and unnecessary elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Clean background */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Simple header styling */
    .header {
        background-color: #2c3e50;
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Clean container */
    .container {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
    }
    
    /* Simple upload area */
    .uploadfile {
        border: 2px dashed #dee2e6;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
    
    .uploadfile:hover {
        border-color: #007bff;
        background-color: #e3f2fd;
    }
    
    /* Clean cards */
    .card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    
    /* Simple alerts */
    .alert-info {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Clean buttons */
    .stButton > button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
    }
    
    /* Clean dataframe styling */
    .stDataFrame {
        border: 1px solid #dee2e6;
        border-radius: 8px;
    }
    
    /* Remove extra padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Clean text inputs */
    .stTextInput > div > div > input {
        border: 1px solid #ced4da;
        border-radius: 6px;
        padding: 0.5rem;
    }
    
    /* Clean selectbox */
    .stSelectbox > div > div > div {
        border: 1px solid #ced4da;
        border-radius: 6px;
    }
    
    /* Simple progress bar */
    .stProgress > div > div > div {
        background-color: #007bff;
    }
    
    /* Clean file uploader */
    .stFileUploader > div {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Remove default margins */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Clean typography */
    h1, h2, h3 {
        color: #2c3e50;
        font-weight: 600;
    }
    
    /* Simple divider */
    hr {
        border: none;
        height: 1px;
        background-color: #dee2e6;
        margin: 1.5rem 0;
    }
    </style>
    ''', unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state for menu navigation"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Home'
    if 'show_settings' not in st.session_state:
        st.session_state.show_settings = False

def render_main_menu():
    """Render functional main menu with navigation"""
    st.markdown("### 📋 Main Menu")
    
    menu_items = [
        {"name": "Home", "icon": "🏠", "description": "Dashboard Utama"},
        {"name": "Document", "icon": "📄", "description": "Manajemen Dokumen"},
        {"name": "Client", "icon": "👥", "description": "Data Klien"},
        {"name": "Settings", "icon": "⚙️", "description": "Pengaturan Sistem"}
    ]
    
    for item in menu_items:
        # Create button for each menu item
        if st.button(
            f"{item['icon']} {item['name']}", 
            key=f"menu_{item['name'].lower()}",
            use_container_width=True,
            help=item['description']
        ):
            st.session_state.current_page = item['name']
            if item['name'] == 'Settings':
                st.session_state.show_settings = True
            else:
                st.session_state.show_settings = False
            st.rerun()
    
    # Show current active page
    if st.session_state.current_page != 'Home':
        st.markdown(f"**📍 Halaman Aktif:** {st.session_state.current_page}")

def render_sidebar():
    """Render improved sidebar with functional main menu"""
    with st.sidebar:
        st.markdown('<div class="sidebar-header">PT LAMAN DAVINDO BAHMAN</div>', unsafe_allow_html=True)
        
        st.markdown(f'<p style="font-weight: 600; font-size: 1.2rem;">{get_greeting()}</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="alert-warning">⚠️ Please Pay the Bill</div>', unsafe_allow_html=True)
        st.button("Transfer", type="primary", use_container_width=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Render functional main menu
        render_main_menu()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Logout button
        if st.button("Logout", type="secondary", use_container_width=True):
            logout()
            st.rerun()
        
        st.caption("© 2025 PT Laman Davindo Bahman")

def render_home_content():
    """Render home page content"""
    render_header()
    uploaded_files, doc_type, use_name, use_passport = render_upload_section()
    render_file_info_panel(uploaded_files)
    
    if uploaded_files:
        process_button = render_process_button(uploaded_files)
        
        if process_button:
            with st.spinner("Memproses dokumen... Mohon tunggu sebentar."):
                from file_handler import process_pdfs
                df, excel_path, renamed_files, zip_path, temp_dir = process_pdfs(
                    uploaded_files, doc_type, use_name, use_passport
                )
            
            render_results_tabs(df, excel_path, renamed_files, zip_path, doc_type, uploaded_files)
            shutil.rmtree(temp_dir)
    else:
        render_help_info()
    
    render_help_expander()

def render_document_page():
    """Render document management page using data from CSV"""
    st.markdown('''
    <div class="header">
        <h1 style="margin-bottom: 0.5rem;">📄 Document Management</h1>
        <p style="opacity: 0.8;">Kelola dan pantau dokumen imigrasi yang telah diproses</p>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown("### 📊 Document Statistics")

    csv_path = Path("data/processed_documents.csv")
    if not csv_path.exists():
        st.warning("⚠️ Belum ada dokumen yang diproses. Silakan lakukan ekstraksi terlebih dahulu.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    try:
        df = pd.read_csv(csv_path)

        # Hitung statistik jenis dokumen
        doc_counts = df['Jenis Dokumen'].value_counts().to_dict()
        total_docs = len(df)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Documents", total_docs)
        with col2:
            st.metric("SKTT", doc_counts.get("SKTT", 0))
        with col3:
            st.metric("ITAS", doc_counts.get("ITAS", 0))
        with col4:
            st.metric("EVLN", doc_counts.get("EVLN", 0))

        st.markdown("### 📋 Recent Documents")
        st.dataframe(df.sort_values(by="Tanggal Penerbitan", ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Gagal memuat data dokumen: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)
    
def render_client_page():
    """Render client management page"""
    st.markdown('''
    <div class="header">
        <h1 style="margin-bottom: 0.5rem;">👥 Client Management</h1>
        <p style="opacity: 0.8;">Kelola data klien dan riwayat dokumen mereka</p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 👤 Client Database")
        client_data = {
            "Name": ["John Doe", "Jane Smith", "Ahmad Rahman"],
            "Nationality": ["USA", "UK", "Indonesia"],
            "Passport": ["US123456", "UK789012", "ID345678"],
            "Documents": ["3 files", "2 files", "5 files"],
            "Last Update": ["2025-06-01", "2025-05-28", "2025-06-03"]
        }
        st.dataframe(client_data, use_container_width=True)
    
    with col2:
        st.markdown("### ➕ Add New Client")
        with st.form("add_client"):
            st.text_input("Full Name")
            st.selectbox("Nationality", ["Indonesia", "USA", "UK", "Singapore", "Malaysia"])
            st.text_input("Passport Number")
            submitted = st.form_submit_button("Add Client")
            if submitted:
                st.success("✅ Client berhasil ditambahkan!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_settings_page():
    """Render settings page"""
    st.markdown('''
    <div class="header">
        <h1 style="margin-bottom: 0.5rem;">⚙️ System Settings</h1>
        <p style="opacity: 0.8;">Konfigurasi sistem dan preferensi aplikasi</p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔧 General", "📁 File Settings", "👤 User Preferences"])
    
    with tab1:
        st.markdown("### General Settings")
        st.selectbox("Default Language", ["Indonesian", "English"])
        st.selectbox("Timezone", ["Asia/Jakarta", "UTC", "Asia/Singapore"])
        st.checkbox("Enable Email Notifications", value=True)
        st.checkbox("Auto-backup Data", value=True)
    
    with tab2:
        st.markdown("### File Processing Settings")
        st.slider("Max File Size (MB)", 1, 100, 50)
        st.selectbox("Default Document Type", ["SKTT", "EVLN", "ITAS", "ITK", "Notifikasi", "DKPTKA"])
        st.checkbox("Auto-rename Files", value=True)
        st.checkbox("Create Backup Copies", value=False)
    
    with tab3:
        st.markdown("### User Preferences")
        st.selectbox("Theme", ["Light", "Dark", "Auto"])
        st.selectbox("Date Format", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        st.number_input("Items per Page", min_value=10, max_value=100, value=25)
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("✅ Settings berhasil disimpan!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_header():
    """Render modern header with gradient background"""
    st.markdown('''
    <div class="header">
        <h1 style="margin-bottom: 0.5rem;">📑 Extraction of Immigration Documents</h1>
        <p style="opacity: 0.8;">Upload the PDF file and the system will extract the data automatically</p>
    </div>
    ''', unsafe_allow_html=True)

def render_upload_section():
    """Render upload section with working CLEAR ALL button"""
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<h2>Document Upload</h2>', unsafe_allow_html=True)

    # Key uploader dinamis agar bisa di-reset
    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = "uploader_1"

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="uploadfile">', unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Upload File PDF", 
            type=["pdf"], 
            accept_multiple_files=True,
            key=st.session_state["uploader_key"]
        )

        if uploaded_files:
            st.session_state["uploaded_files"] = uploaded_files

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        doc_type = st.selectbox(
            "Select Document Type",
            ["SKTT", "EVLN", "ITAS", "ITK", "Notifikasi", "DKPTKA"]
        )

        st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
        use_name = st.checkbox("Use Name to Rename Files", value=True)
        use_passport = st.checkbox("Use Passport Number to Rename Files", value=True)
        st.markdown('</div>', unsafe_allow_html=True)

        badge_color = {
            "SKTT": "#0284c7",
            "EVLN": "#7c3aed",
            "ITAS": "#16a34a",
            "ITK": "#ca8a04",
            "Notifikasi": "#e11d48",
            "DKPTKA": "#dc2626"
        }.get(doc_type, "#64748b")

        st.markdown(f'''
        <div style="margin-top: 1rem;">
            <span style="background-color: {badge_color}; color: white; padding: 0.3rem 0.6rem; 
            border-radius: 0.25rem; font-size: 0.8rem; font-weight: 600;">
                {doc_type}
            </span>
            <span style="font-size: 0.85rem; margin-left: 0.5rem; color: #64748b;">Selected</span>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Tombol Clear All yang benar-benar mereset komponen file_uploader
    if st.session_state.get("uploaded_files"):
        col_clear = st.columns([1, 1, 1])[1]
        with col_clear:
            if st.button("🗑️ CLEAR ALL FILES", key="clear_button"):
                # Hapus file dari session
                del st.session_state["uploaded_files"]
                # Ganti key uploader agar komponen reset
                st.session_state["uploader_key"] = f"uploader_{str(int(time.time()))}"
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    return st.session_state.get("uploaded_files", []), doc_type, use_name, use_passport
    
def render_file_info_panel(uploaded_files):
    """Render file information panel"""
    if uploaded_files:
        st.markdown('<div class="container">', unsafe_allow_html=True)
        st.markdown('<h3>Uploaded Files</h3>', unsafe_allow_html=True)
        
        file_info_cols = st.columns(len(uploaded_files) if len(uploaded_files) <= 3 else 3)

        for i, uploaded_file in enumerate(uploaded_files):
            col_idx = i % 3
            with file_info_cols[col_idx]:
                st.markdown(f'''
                <div style="background-color: #f8fafc; border-radius: 0.5rem; padding: 0.75rem; margin-bottom: 0.75rem;">
                    <div style="display: flex; align-items: center;">
                        <div style="background-color: #e2e8f0; border-radius: 0.375rem; padding: 0.5rem; margin-right: 0.75rem;">
                            📄
                        </div>
                        <div>
                            <p style="margin: 0; font-weight: 600; font-size: 0.9rem;">{uploaded_file.name}</p>
                            <p style="margin: 0; color: #64748b; font-size: 0.8rem;">PDF Document</p>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_process_button(uploaded_files):
    """Render process button with file count"""
    if uploaded_files:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            return st.button(
                f"Proses {len(uploaded_files)} File PDF", 
                type="primary", 
                use_container_width=True,
                key="process_button"
            )
    return False

def render_results_tabs(df, excel_path, renamed_files, zip_path, doc_type, uploaded_files):
    """Render results in organized tabs"""
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    # Success message
    st.markdown('''
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <div style="background-color: #d1fae5; color: #047857; border-radius: 50%; width: 2rem; height: 2rem; display: flex; align-items: center; justify-content: center; margin-right: 0.75rem;">
            ✓
        </div>
        <h2 style="margin: 0;">Proses Berhasil</h2>
    </div>
    ''', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["💾 Extraction Result", "📊 Excel File", "📁 File Rename"])

    with tab1:
        st.subheader("Extraction Result Data")
        st.markdown('<div style="overflow-x: auto;">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'''
        <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1rem;">
            <div style="background-color: #f0f9ff; border-radius: 0.5rem; padding: 1rem; flex: 1;">
                <h4 style="margin: 0 0 0.5rem 0; color: #0369a1;">Total Data</h4>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0;">{len(df)}</p>
            </div>
            <div style="background-color: #f0fdf4; border-radius: 0.5rem; padding: 1rem; flex: 1;">
                <h4 style="margin: 0 0 0.5rem 0; color: #166534;">Type of Document</h4>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0;">{doc_type}</p>
            </div>
            <div style="background-color: #fef3c7; border-radius: 0.5rem; padding: 1rem; flex: 1;">
                <h4 style="margin: 0 0 0.5rem 0; color: #92400e;">Processed Files</h4>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0;">{len(uploaded_files)}</p>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with tab2:
        st.subheader("Download File Excel")

        with open(excel_path, "rb") as f:
            excel_data = f.read()

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f'''
            <div style="background-color: #f8fafc; border-radius: 0.5rem; padding: 1rem; display: flex; align-items: center;">
                <div style="background-color: #22c55e; border-radius: 0.5rem; padding: 0.75rem; margin-right: 1rem;">
                    <span style="color: white; font-size: 1.5rem;">📊</span>
                </div>
                <div>
                    <p style="margin: 0; font-weight: 600;">Hasil_Ekstraksi.xlsx</p>
                    <p style="margin: 0; color: #64748b; font-size: 0.85rem;">Excel Spreadsheet • Diekspor pada {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        with col2:
            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name="Hasil_Ekstraksi.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    with tab3:
        st.subheader("File yang Telah di-Rename")
        st.markdown('<div style="background-color: #f8fafc; border-radius: 0.5rem; padding: 1rem;">', unsafe_allow_html=True)

        for original_name, file_info in renamed_files.items():
            st.markdown(f'''
            <div style="display: flex; align-items: center; padding: 0.75rem; border-bottom: 1px solid #e2e8f0;">
                <div style="flex: 1;">
                    <p style="margin: 0; color: #64748b; font-size: 0.85rem;">Nama Asli:</p>
                    <p style="margin: 0; font-weight: 600;">{original_name}</p>
                </div>
                <div style="margin: 0 1rem;">
                    <span style="color: #64748b;">→</span>
                </div>
                <div style="flex: 1;">
                    <p style="margin: 0; color: #64748b; font-size: 0.85rem;">Nama Baru:</p>
                    <p style="margin: 0; font-weight: 600; color: #0369a1;">{file_info['new_name']}</p>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        with open(zip_path, "rb") as f:
            zip_data = f.read()

        st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
        st.download_button(
            label="Download All PDF (ZIP) Files",
            data=zip_data,
            file_name="Renamed_Files.zip",
            mime="application/zip",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_help_info():
    """Render help information when no files uploaded"""
    st.markdown('''
    <div class="alert-info">
        <h3 style="margin-top: 0;">Mulai Ekstraksi</h3>
        <p>Please upload PDF files of immigration documents to start the automatic extraction process.</p>
        <ul style="margin-bottom: 0;">
            <li>Make sure the files are in PDF format</li>
            <li>Choose the appropriate document type</li>
            <li>Customise the file naming options if required</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)

def render_help_expander():
    """Render help expander with usage instructions"""
    with st.expander("Help"):
        st.write("""
        **How to Use the Application:**
        1. Upload one or more PDF files of immigration documents
        2. Select the appropriate document type (SKTT, EVLN, ITAS, ITK, Notifikasi, DKPTKA)
        3. Specify whether to include the name and/or passport number in the file name
        4. Click the 'Process PDF' button to start extracting data
        5. View and download the extracted results in Excel format or a renamed PDF file
        
        **Note:** This app can handle multiple types of Indonesian immigration documents and will automatically extract important information from them.
        """)

def render_main_app():
    """Main application render function with page routing"""
    # Initialize session state
    initialize_session_state()
    
    # Apply CSS styles
    render_css_styles()
    
    # Render sidebar
    render_sidebar()
    
    # Route to appropriate page based on current_page
    if st.session_state.current_page == 'Home':
        render_home_content()
    elif st.session_state.current_page == 'Document':
        render_document_page()
    elif st.session_state.current_page == 'Client':
        render_client_page()
    elif st.session_state.current_page == 'Settings':
        render_settings_page()
    else:
        # Default to home if unknown page
        st.session_state.current_page = 'Home'
        render_home_content()
