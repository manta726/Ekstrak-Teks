"""
Main Streamlit Application for LDB (Ekstraksi Dokumen Imigrasi)
Complete version with table display and file rename functionality
"""

import streamlit as st
import sys
import io
import time
import zipfile
import tempfile
import shutil
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

# Import extraction modules
EXTRACTION_ENABLED = False
try:
    import pdfplumber
    from extractors import extract_document_data
    EXTRACTION_ENABLED = True
    st.success("✅ Extraction modules loaded successfully!")
except ImportError as e:
    st.error(f"❌ Extraction modules not found: {e}")
    st.info("Please ensure extractors.py and pdfplumber are available.")

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
    
    .success-header {
        display: flex;
        align-items: center;
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
    }
    
    .success-icon {
        background: #28a745;
        color: white;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 0.75rem;
        font-size: 14px;
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
    
    .extraction-result {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    /* Custom table styling */
    .dataframe {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe th {
        background-color: #f8f9fa;
        color: #495057;
        font-weight: 600;
        padding: 12px;
        border-bottom: 2px solid #dee2e6;
    }
    
    .dataframe td {
        padding: 12px;
        border-bottom: 1px solid #dee2e6;
    }
    
    .dataframe tr:hover {
        background-color: #f5f5f5;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0 0;
        color: #6c757d;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #007bff;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def extract_pdf_text(uploaded_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text + "\n"
        return pdf_text.strip()
    except Exception as e:
        st.error(f"Error extracting PDF text: {str(e)}")
        return None

def generate_new_filename(extracted_data, original_filename, use_name=True, use_passport=True):
    """Generate new filename based on extracted data"""
    try:
        # Get file extension
        file_ext = Path(original_filename).suffix
        
        # Extract relevant fields
        name = extracted_data.get('Name') or extracted_data.get('Nama TKA') or extracted_data.get('nama', '')
        passport = (extracted_data.get('Passport Number') or 
                   extracted_data.get('Nomor Paspor') or 
                   extracted_data.get('nomor_paspor', ''))
        doc_type = extracted_data.get('Jenis Dokumen', 'DOC')
        
        # Clean name and passport for filename
        if name:
            name = ''.join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
            name = name.replace(' ', '_')
        
        if passport:
            passport = ''.join(c for c in passport if c.isalnum()).strip()
        
        # Build new filename
        parts = [doc_type]
        
        if use_name and name:
            parts.append(name)
        
        if use_passport and passport:
            parts.append(passport)
        
        # If no useful data found, use original name
        if len(parts) == 1:
            return original_filename
        
        new_filename = '_'.join(parts) + file_ext
        
        # Ensure filename is not too long
        if len(new_filename) > 100:
            new_filename = new_filename[:97] + file_ext
        
        return new_filename
    
    except Exception as e:
        st.error(f"Error generating filename: {str(e)}")
        return original_filename

def create_renamed_files_zip(uploaded_files, extraction_results, use_name=True, use_passport=True):
    """Create ZIP file with renamed PDFs"""
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        zip_path = Path(temp_dir) / "renamed_files.zip"
        
        renamed_files_info = {}
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for i, uploaded_file in enumerate(uploaded_files):
                # Get extraction result for this file
                if i < len(extraction_results):
                    extracted_data = extraction_results[i]
                else:
                    extracted_data = {}
                
                # Generate new filename
                new_filename = generate_new_filename(
                    extracted_data, 
                    uploaded_file.name, 
                    use_name, 
                    use_passport
                )
                
                # Store rename info
                renamed_files_info[uploaded_file.name] = {
                    'new_name': new_filename,
                    'extracted_data': extracted_data
                }
                
                # Add file to ZIP with new name
                uploaded_file.seek(0)  # Reset file pointer
                zipf.writestr(new_filename, uploaded_file.read())
        
        return zip_path, renamed_files_info
    
    except Exception as e:
        st.error(f"Error creating renamed files: {str(e)}")
        return None, {}

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
        
        # Show module status
        st.markdown("**📦 Module Status:**")
        st.markdown(f"- Database: {'✅' if DATABASE_ENABLED else '❌'}")
        st.markdown(f"- Extraction: {'✅' if EXTRACTION_ENABLED else '❌'}")
        
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
    """Render document extraction page with table display and file rename"""
    st.markdown('<div class="main-header"><h1>📄 Ekstraksi Dokumen Imigrasi</h1></div>', unsafe_allow_html=True)
    
    if not EXTRACTION_ENABLED:
        st.error("❌ Extraction modules not available. Please check extractors.py and install pdfplumber.")
        return
    
    # File upload section
    st.subheader("📤 Upload Dokumen")
    
    uploaded_files = st.file_uploader(
        "Pilih file dokumen PDF (dapat memilih multiple files)",
        type=['pdf'],
        accept_multiple_files=True,
        help="Maksimal ukuran file 50MB per file"
    )
    
    if uploaded_files:
        # Display file info
        st.subheader("📋 File yang Diupload")
        
        for i, uploaded_file in enumerate(uploaded_files):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**{i+1}. {uploaded_file.name}**")
            
            with col2:
                file_size_mb = uploaded_file.size / (1024 * 1024)
                st.write(f"Ukuran: {file_size_mb:.2f} MB")
            
            with col3:
                st.write(f"Tipe: {uploaded_file.type}")
        
        # Document type selection
        st.subheader("📋 Pilih Jenis Dokumen")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
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
        
        with col2:
            use_name = st.checkbox("Gunakan Nama untuk Rename File", value=True)
        
        with col3:
            use_passport = st.checkbox("Gunakan Nomor Paspor untuk Rename File", value=True)
        
        # Extract button
        if st.button("🚀 Mulai Ekstraksi", type="primary", use_container_width=True):
            with st.spinner("Sedang memproses dokumen..."):
                try:
                    start_time = time.time()
                    
                    # Process all files
                    all_extraction_results = []
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"Memproses file {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
                        
                        # Extract text from PDF
                        pdf_text = extract_pdf_text(uploaded_file)
                        
                        if pdf_text:
                            # Process with extraction function
                            extraction_result = extract_document_data(pdf_text, doc_type)
                            extraction_result['filename'] = uploaded_file.name
                            all_extraction_results.append(extraction_result)
                        else:
                            # Add error result
                            error_result = {
                                'filename': uploaded_file.name,
                                'Error': 'Gagal mengekstrak teks dari PDF',
                                'Jenis Dokumen': doc_type
                            }
                            all_extraction_results.append(error_result)
                        
                        # Update progress
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    processing_time = time.time() - start_time
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Log to database if available
                    if DATABASE_ENABLED and db_manager:
                        for result in all_extraction_results:
                            db_manager.log_extraction(
                                user_id=user['id'],
                                filename=result['filename'],
                                file_size=next((f.size for f in uploaded_files if f.name == result['filename']), 0),
                                document_type=doc_type,
                                extracted_data=result,
                                processing_time=processing_time / len(uploaded_files),
                                status="completed" if "Error" not in result else "failed"
                            )
                        
                        # Log activity
                        db_manager.log_activity(
                            user_id=user['id'],
                            action="BATCH_DOCUMENT_EXTRACTED",
                            details=f"Extracted {len(uploaded_files)} {doc_type} documents"
                        )
                    
                    # Display success header
                    st.markdown("""
                    <div class="success-header">
                        <div class="success-icon">✓</div>
                        <h2 style="margin: 0;">Proses Berhasil</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create tabs for results
                    tab1, tab2, tab3 = st.tabs(["📊 Extraction Result", "📄 Excel File", "📁 File Rename"])
                    
                    with tab1:
                        st.subheader("Extraction Result Data")
                        
                        # Prepare data for table
                        import pandas as pd
                        
                        # Create standardized columns based on document type
                        if doc_type == "SKTT":
                            columns = ['NIK', 'Name', 'Jenis Kelamin', 'Place of Birth', 'Date of Birth', 'Nationality', 'Occupation', 'Address']
                        elif doc_type == "EVLN":
                            columns = ['Name', 'Place of Birth', 'Date of Birth', 'Passport No', 'Passport Expiry', 'Date Issue']
                        elif doc_type in ["ITAS", "ITK"]:
                            columns = ['Name', 'Permit Number', 'Place & Date of Birth', 'Passport Number', 'Passport Expiry', 'Nationality', 'Gender']
                        elif doc_type == "NOTIFICATION":
                            columns = ['Nomor Keputusan', 'Nama TKA', 'Tempat/Tanggal Lahir', 'Kewarganegaraan', 'Nomor Paspor', 'Jabatan']
                        elif doc_type == "DKPTKA":
                            columns = ['Nama Pemberi Kerja', 'Nama TKA', 'Nomor Paspor', 'Kewarganegaraan', 'Jabatan', 'DKPTKA']
                        else:
                            # Generic columns
                            all_keys = set()
                            for result in all_extraction_results:
                                all_keys.update(result.keys())
                            columns = [k for k in all_keys if k not in ['filename', 'Jenis Dokumen', 'Error']]
                        
                        # Create DataFrame
                        table_data = []
                        for i, result in enumerate(all_extraction_results):
                            row = {'No': i + 1}
                            for col in columns:
                                row[col] = result.get(col, '-')
                            table_data.append(row)
                        
                        df = pd.DataFrame(table_data)
                        
                        # Display table with custom styling
                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "No": st.column_config.NumberColumn("No", width="small"),
                            }
                        )
                        
                        # Show statistics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Files", len(uploaded_files))
                        
                        with col2:
                            successful = len([r for r in all_extraction_results if "Error" not in r])
                            st.metric("Berhasil", successful)
                        
                        with col3:
                            failed = len([r for r in all_extraction_results if "Error" in r])
                            st.metric("Gagal", failed)
                        
                        with col4:
                            st.metric("Waktu Proses", f"{processing_time:.2f}s")
                    
                    with tab2:
                        st.subheader("Download File Excel")
                        
                        # Create Excel file
                        excel_buffer = io.BytesIO()
                        df.to_excel(excel_buffer, index=False, engine='openpyxl')
                        excel_data = excel_buffer.getvalue()
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <div style="background-color: #f8fafc; border-radius: 0.5rem; padding: 1rem; display: flex; align-items: center;">
                                <div style="background-color: #22c55e; border-radius: 0.5rem; padding: 0.75rem; margin-right: 1rem;">
                                    <span style="color: white; font-size: 1.5rem;">📊</span>
                                </div>
                                <div>
                                    <p style="margin: 0; font-weight: 600;">Hasil_Ekstraksi_{doc_type}.xlsx</p>
                                    <p style="margin: 0; color: #64748b; font-size: 0.85rem;">Excel Spreadsheet • {len(uploaded_files)} files • Diekspor pada {time.strftime('%d/%m/%Y %H:%M')}</p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.download_button(
                                label="📊 Download Excel",
                                data=excel_data,
                                file_name=f"Hasil_Ekstraksi_{doc_type}_{int(time.time())}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    
                    with tab3:
                        st.subheader("File yang Telah di-Rename")
                        
                        # Create renamed files ZIP
                        with st.spinner("Membuat file yang telah di-rename..."):
                            zip_path, renamed_files_info = create_renamed_files_zip(
                                uploaded_files, all_extraction_results, use_name, use_passport
                            )
                        
                        if zip_path and renamed_files_info:
                            # Display rename information
                            st.markdown('<div style="background-color: #f8fafc; border-radius: 0.5rem; padding: 1rem;">', unsafe_allow_html=True)
                            
                            for original_name, file_info in renamed_files_info.items():
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
                            
                            # Download ZIP button
                            with open(zip_path, "rb") as f:
                                zip_data = f.read()
                            
                            st.download_button(
                                label="📁 Download All Renamed Files (ZIP)",
                                data=zip_data,
                                file_name=f"Renamed_{doc_type}_Files_{int(time.time())}.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                            
                            # Clean up temporary files
                            shutil.rmtree(zip_path.parent)
                        
                        else:
                            st.error("❌ Gagal membuat file yang telah di-rename")
                    
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {str(e)}")
                    
                    # Log failed extraction if database available
                    if DATABASE_ENABLED and db_manager:
                        for uploaded_file in uploaded_files:
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
        uploaded_files = st.file_uploader("Upload PDF", type=['pdf'], accept_multiple_files=True)
        
        if uploaded_files and EXTRACTION_ENABLED:
            doc_options = list(DOCUMENT_TYPES.keys()) if DOCUMENT_TYPES else ['SKTT', 'EVLN', 'ITAS', 'ITK']
            doc_type = st.selectbox("Document Type", doc_options)
            
            if st.button("Process"):
                with st.spinner("Processing..."):
                    results = []
                    for uploaded_file in uploaded_files:
                        pdf_text = extract_pdf_text(uploaded_file)
                        if pdf_text:
                            result = extract_document_data(pdf_text, doc_type)
                            results.append(result)
                    
                    if results:
                        import pandas as pd
                        df = pd.DataFrame(results)
                        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
