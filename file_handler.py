"""
File Handler for LDB Application
Handles PDF processing, extraction, and file management
"""

import os
import tempfile
import shutil
import zipfile
import io
import pdfplumber
import pandas as pd
from pathlib import Path

# Import extractors with fallback
try:
    from extractors import (
        extract_sktt, extract_evln, extract_itas, extract_itk, 
        extract_notifikasi, extract_dkptka_info, extract_document_data
    )
except ImportError as e:
    print(f"Warning: Could not import extractors: {e}")
    # Fallback functions
    def extract_sktt(text): return {"Error": "Extractor not available"}
    def extract_evln(text): return {"Error": "Extractor not available"}
    def extract_itas(text): return {"Error": "Extractor not available"}
    def extract_itk(text): return {"Error": "Extractor not available"}
    def extract_notifikasi(text): return {"Error": "Extractor not available"}
    def extract_dkptka_info(text): return {"Error": "Extractor not available"}
    def extract_document_data(text, doc_type): return {"Error": "Extractor not available"}

# Import helpers with fallback
try:
    from helpers import generate_new_filename
except ImportError:
    def generate_new_filename(extracted_data, use_name=True, use_passport=True):
        """Fallback filename generator"""
        name = extracted_data.get('Name') or extracted_data.get('Nama TKA') or 'Unknown'
        passport = extracted_data.get('Passport Number') or extracted_data.get('Nomor Paspor') or 'NoPassport'
        doc_type = extracted_data.get('Jenis Dokumen', 'DOC')
        
        parts = [doc_type]
        if use_name and name != 'Unknown':
            parts.append(name.replace(' ', '_'))
        if use_passport and passport != 'NoPassport':
            parts.append(passport)
        
        return '_'.join(parts) + '.pdf'

def extract_pdf_text(uploaded_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_text = ""
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text + "\n"
        return pdf_text.strip()
    except Exception as e:
        print(f"Error extracting PDF text: {str(e)}")
        return None

def process_single_pdf(uploaded_file, doc_type):
    """Process a single PDF file and extract data"""
    try:
        # Extract text from PDF
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            texts = [page.extract_text() for page in pdf.pages if page.extract_text()]
            full_text = "\n".join(texts)
        
        # Extract data based on document type
        if doc_type == "SKTT":
            extracted_data = extract_sktt(full_text)
        elif doc_type == "EVLN":
            extracted_data = extract_evln(full_text)
        elif doc_type == "ITAS":
            extracted_data = extract_itas(full_text)
        elif doc_type == "ITK":
            extracted_data = extract_itk(full_text)
        elif doc_type == "Notifikasi" or doc_type == "NOTIFICATION":
            extracted_data = extract_notifikasi(full_text)
        elif doc_type == "DKPTKA":
            extracted_data = extract_dkptka_info(full_text)
        else:
            # Use generic extractor if available
            try:
                extracted_data = extract_document_data(full_text, doc_type)
            except:
                extracted_data = {"Error": f"Unsupported document type: {doc_type}"}
        
        # Add filename to extracted data
        extracted_data['filename'] = uploaded_file.name
        
        return extracted_data
    
    except Exception as e:
        return {
            'filename': uploaded_file.name,
            'Error': f"Failed to process PDF: {str(e)}",
            'Jenis Dokumen': doc_type
        }

def process_pdfs(uploaded_files, doc_type, use_name=True, use_passport=True):
    """
    Process multiple PDF files and return extracted data with renamed files
    
    Args:
        uploaded_files: List of uploaded file objects
        doc_type: Document type (SKTT, EVLN, ITAS, ITK, Notifikasi, DKPTKA)
        use_name: Whether to use name in filename
        use_passport: Whether to use passport number in filename
    
    Returns:
        tuple: (dataframe, excel_path, renamed_files_dict, zip_path, temp_dir)
    """
    all_data = []
    renamed_files = {}
    temp_dir = tempfile.mkdtemp()
    
    try:
        for uploaded_file in uploaded_files:
            # Process single PDF
            extracted_data = process_single_pdf(uploaded_file, doc_type)
            all_data.append(extracted_data)
            
            # Generate new filename
            new_filename = generate_new_filename(extracted_data, use_name, use_passport)
            
            # Save renamed file to temp directory
            temp_file_path = os.path.join(temp_dir, new_filename)
            with open(temp_file_path, 'wb') as f:
                uploaded_file.seek(0)  # Reset file pointer
                f.write(uploaded_file.read())
            
            renamed_files[uploaded_file.name] = {
                'new_name': new_filename, 
                'path': temp_file_path,
                'extracted_data': extracted_data
            }
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Create Excel file
        excel_path = os.path.join(temp_dir, "Hasil_Ekstraksi.xlsx")
        df.to_excel(excel_path, index=False, engine='openpyxl')
        
        # Create ZIP file with renamed PDFs
        zip_path = os.path.join(temp_dir, "Renamed_Files.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_info in renamed_files.values():
                zipf.write(file_info['path'], arcname=file_info['new_name'])
        
        return df, excel_path, renamed_files, zip_path, temp_dir
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise e

def process_pdfs_batch(uploaded_files, doc_type, use_name=True, use_passport=True, progress_callback=None):
    """
    Process multiple PDF files with progress tracking
    
    Args:
        uploaded_files: List of uploaded file objects
        doc_type: Document type
        use_name: Whether to use name in filename
        use_passport: Whether to use passport number in filename
        progress_callback: Function to call with progress updates
    
    Returns:
        tuple: (results_list, temp_dir)
    """
    all_results = []
    temp_dir = tempfile.mkdtemp()
    
    try:
        total_files = len(uploaded_files)
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Update progress
            if progress_callback:
                progress_callback(i / total_files, f"Processing {uploaded_file.name}")
            
            # Process single PDF
            extracted_data = process_single_pdf(uploaded_file, doc_type)
            
            # Generate new filename
            new_filename = generate_new_filename(extracted_data, use_name, use_passport)
            
            # Save renamed file
            temp_file_path = os.path.join(temp_dir, new_filename)
            with open(temp_file_path, 'wb') as f:
                uploaded_file.seek(0)
                f.write(uploaded_file.read())
            
            result = {
                'original_name': uploaded_file.name,
                'new_name': new_filename,
                'file_path': temp_file_path,
                'extracted_data': extracted_data,
                'file_size': uploaded_file.size
            }
            
            all_results.append(result)
        
        # Final progress update
        if progress_callback:
            progress_callback(1.0, "Processing complete")
        
        return all_results, temp_dir
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise e

def create_excel_from_results(results, output_path=None):
    """Create Excel file from extraction results"""
    try:
        # Extract data for DataFrame
        data_for_df = [result['extracted_data'] for result in results]
        df = pd.DataFrame(data_for_df)
        
        # Set output path
        if output_path is None:
            output_path = tempfile.mktemp(suffix='.xlsx')
        
        # Save to Excel
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        return output_path, df
    
    except Exception as e:
        raise Exception(f"Failed to create Excel file: {str(e)}")

def create_zip_from_results(results, output_path=None):
    """Create ZIP file from renamed files"""
    try:
        if output_path is None:
            output_path = tempfile.mktemp(suffix='.zip')
        
        with zipfile.ZipFile(output_path, 'w') as zipf:
            for result in results:
                if os.path.exists(result['file_path']):
                    zipf.write(result['file_path'], arcname=result['new_name'])
        
        return output_path
    
    except Exception as e:
        raise Exception(f"Failed to create ZIP file: {str(e)}")

def cleanup_temp_directory(temp_dir):
    """Clean up temporary directory"""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Warning: Failed to clean up temp directory {temp_dir}: {e}")

def get_file_info(uploaded_file):
    """Get information about uploaded file"""
    return {
        'name': uploaded_file.name,
        'size': uploaded_file.size,
        'type': uploaded_file.type,
        'size_mb': round(uploaded_file.size / (1024 * 1024), 2)
    }

def validate_pdf_file(uploaded_file):
    """Validate if uploaded file is a valid PDF"""
    try:
        # Check file extension
        if not uploaded_file.name.lower().endswith('.pdf'):
            return False, "File must be a PDF"
        
        # Check file size (50MB limit)
        max_size = 50 * 1024 * 1024  # 50MB
        if uploaded_file.size > max_size:
            return False, f"File size exceeds 50MB limit (current: {uploaded_file.size / (1024*1024):.1f}MB)"
        
        # Try to open with pdfplumber
        uploaded_file.seek(0)
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            if len(pdf.pages) == 0:
                return False, "PDF file appears to be empty"
        
        uploaded_file.seek(0)  # Reset file pointer
        return True, "Valid PDF file"
    
    except Exception as e:
        return False, f"Invalid PDF file: {str(e)}"

# Legacy compatibility functions
def extract_text_from_pdf(uploaded_file):
    """Legacy function for backward compatibility"""
    return extract_pdf_text(uploaded_file)

def process_documents(uploaded_files, document_type, use_name_in_filename=True, use_passport_in_filename=True):
    """Legacy function for backward compatibility"""
    return process_pdfs(uploaded_files, document_type, use_name_in_filename, use_passport_in_filename)
