import re
import pdfplumber
from typing import Dict, Optional
from helpers import clean_text, format_date, split_birth_place_date

# ========================= Ekstraksi SKTT =========================
def extract_sktt(text):
    import re

    nik = re.search(r'NIK/Number of Population Identity\s*:\s*(\d+)', text)
    name = re.search(r'Nama/Name\s*:\s*([\w\s]+)', text)
    gender = re.search(r'Jenis Kelamin/Sex\s*:\s*(MALE|FEMALE)', text)
    birth_place_date = re.search(r'Tempat/Tgl Lahir\s*:\s*([\w\s,0-9-]+)', text)
    nationality = re.search(r'Kewarganegaraan/Nationality\s*:\s*([\w\s]+)', text)
    occupation = re.search(r'Pekerjaan/Occupation\s*:\s*([\w\s]+)', text)
    address = re.search(r'Alamat/Address\s*:\s*([\w\s,./-]+)', text)
    kitab_kitas = re.search(r'Nomor KITAP/KITAS Number\s*:\s*([\w-]+)', text)
    expiry_date = re.search(r'Berlaku Hingga s.d/Expired date\s*:\s*([\d-]+)', text)

    # Ambil blok bawah sekitar tanda tangan
    lines = text.strip().splitlines()
    date_issue = None
    for i, line in enumerate(lines):
        if "KEPALA DINAS" in line.upper():
            if i > 0:
                match = re.search(r'([A-Z\s]+),\s*(\d{2}-\d{2}-\d{4})', lines[i-1])
                if match:
                    date_issue = match.group(2)
            break

    birth_place, birth_date = split_birth_place_date(birth_place_date.group(1)) if birth_place_date else (None, None)

    return {
        "NIK": nik.group(1) if nik else None,
        "Name": clean_text(name.group(1), is_name_or_pob=True) if name else None,
        "Jenis Kelamin": gender.group(1) if gender else None,
        "Place of Birth": clean_text(birth_place, is_name_or_pob=True) if birth_place else None,
        "Date of Birth": format_date(birth_date) if birth_date else None,
        "Nationality": clean_text(nationality.group(1)) if nationality else None,
        "Occupation": clean_text(occupation.group(1)) if occupation else None,
        "Address": clean_text(address.group(1)) if address else None,
        "KITAS/KITAP": clean_text(kitab_kitas.group(1)) if kitab_kitas else None,
        "Passport Expiry": format_date(expiry_date.group(1)) if expiry_date else None,
        "Date Issue": format_date(date_issue) if date_issue else None,
        "Jenis Dokumen": "SKTT"
    }

# ========================= Ekstraksi EVLN =========================
def extract_evln(text):
    # Inisialisasi data
    data = {
        "Name": "",
        "Place of Birth": "",
        "Date of Birth": "",
        "Passport No": "",
        "Passport Expiry": "",
        "Date Issue": "",  # Kolom baru yang ditambahkan
        "Jenis Dokumen": "EVLN"
    }
    
    lines = text.split("\n")
    
    # Cari nama berdasarkan sapaan seperti Dear Mr./Ms.
    for i, line in enumerate(lines):
        if re.search(r"Dear\s+(Mr\.|Ms\.|Sir|Madam)?", line, re.IGNORECASE):
            if i + 1 < len(lines):
                name_candidate = lines[i + 1].strip()
                if 3 < len(name_candidate) < 50:
                    if 'clean_text' in globals():
                        data["Name"] = clean_text(name_candidate, is_name_or_pob=True)
                    else:
                        data["Name"] = re.sub(r'[^A-Z ]', '', name_candidate.upper())
            break
    
    # Parsing baris lain
    for line in lines:
        if not data["Name"] and re.search(r"(?i)\bName\b|\bNama\b", line):
            parts = line.split(":")
            if len(parts) > 1:
                data["Name"] = clean_text(parts[1], is_name_or_pob=True)
        
        elif re.search(r"(?i)\bPlace of Birth\b|\bTempat Lahir\b", line):
            parts = line.split(":")
            if len(parts) > 1:
                pob_text = parts[1].strip()
                # Hapus "Visa Type" jika ada
                pob_cleaned = re.sub(r'\s*Visa\s*Type\s*.*', '', pob_text)
        
        elif re.search(r"(?i)\bDate of Birth\b|\bTanggal Lahir\b", line):
            match = re.search(r"(\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})", line)
            if match:
                data["Date of Birth"] = format_date(match.group(1))
        
        elif re.search(r"(?i)\bPassport No\b", line):
            match = re.search(r"\b([A-Z0-9]+)\b", line)
            if match:
                data["Passport No"] = match.group(1)
        
        elif re.search(r"(?i)\bPassport Expiry\b", line):
            match = re.search(r"(\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})", line)
            if match:
                data["Passport Expiry"] = format_date(match.group(1))
        
        elif re.search(r"(?i)\bDate of issue\b|\bTanggal Penerbitan\b", line):  # Diperbaiki untuk mencocokkan format dokumen
            match = re.search(r"(\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})", line)
            if match:
                data["Date Issue"] = format_date(match.group(1))
    
    # Ekstraksi Date Issue dengan pattern khusus
    if not data["Date Issue"]:
        issue_patterns = [
            r"(?i)(?:Date\s+of\s+Issue|Issue\s+Date|Issued\s+on|Tanggal\s+Penerbitan)\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})",
            r"(?i)(?:Issued|Diterbitkan)\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})"
        ]
        
        for pattern in issue_patterns:
            match = re.search(pattern, text)
            if match:
                data["Date Issue"] = format_date(match.group(1))
                break
    
    # Jika belum dapat issue date, cari tanggal yang tahunnya antara 2020-2025
    if not data["Date Issue"]:
        dates_found = re.findall(r"(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})", text)
        for date_str in dates_found:
            formatted_date = format_date(date_str)
            year = int(formatted_date.split('/')[-1])
            if 2020 <= year <= 2025 and formatted_date != data["Date of Birth"] and formatted_date != data["Passport Expiry"]:
                data["Date Issue"] = formatted_date
                break
    
    return data, '', pob_text, flags=re.IGNORECASE)
                data["Place of Birth"] = clean_text(pob_cleaned, is_name_or_pob=True)
        
        elif re.search(r"(?i)\bDate of Birth\b|\bTanggal Lahir\b", line):
            match = re.search(r"(\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})", line)
            if match:
                data["Date of Birth"] = format_date(match.group(1))
        
        elif re.search(r"(?i)\bPassport No\b", line):
            match = re.search(r"\b([A-Z0-9]+)\b", line)
            if match:
                data["Passport No"] = match.group(1)
        
        elif re.search(r"(?i)\bPassport Expiry\b", line):
            match = re.search(r"(\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})", line)
            if match:
                data["Passport Expiry"] = format_date(match.group(1))
        
        elif re.search(r"(?i)\bDate of issue\b|\bTanggal Penerbitan\b", line):  # Diperbaiki untuk mencocokkan format dokumen
            match = re.search(r"(\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})", line)
            if match:
                data["Date Issue"] = format_date(match.group(1))
    
    # Ekstraksi Date Issue dengan pattern khusus
    if not data["Date Issue"]:
        issue_patterns = [
            r"(?i)(?:Date\s+of\s+Issue|Issue\s+Date|Issued\s+on|Tanggal\s+Penerbitan)\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})",
            r"(?i)(?:Issued|Diterbitkan)\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})"
        ]
        
        for pattern in issue_patterns:
            match = re.search(pattern, text)
            if match:
                data["Date Issue"] = format_date(match.group(1))
                break
    
    # Jika belum dapat issue date, cari tanggal yang tahunnya antara 2020-2025
    if not data["Date Issue"]:
        dates_found = re.findall(r"(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})", text)
        for date_str in dates_found:
            formatted_date = format_date(date_str)
            year = int(formatted_date.split('/')[-1])
            if 2020 <= year <= 2025 and formatted_date != data["Date of Birth"] and formatted_date != data["Passport Expiry"]:
                data["Date Issue"] = formatted_date
                break
    
    return data
    
# ========================= Ekstraksi ITAS =========================
def extract_itas(text):
    data = {}
    
    # Extract Name
    name_match = re.search(r"([A-Z\s]+)\nPERMIT NUMBER", text)
    data["Name"] = name_match.group(1).strip() if name_match else None
    
    # Extract Permit Number
    permit_match = re.search(r"PERMIT NUMBER\s*:\s*([A-Z0-9-]+)", text)
    data["Permit Number"] = permit_match.group(1) if permit_match else None
    
    # Extract Stay Permit Expiry
    expiry_match = re.search(r"STAY PERMIT EXPIRY\s*:\s*([\d/]+)", text)
    data["Stay Permit Expiry"] = format_date(expiry_match.group(1)) if expiry_match else None
    
    # Extract Place & Date of Birth
    place_date_birth_match = re.search(r"Place / Date of Birth\s*.*:\s*([A-Za-z\s]+)\s*/\s*([\d-]+)", text)
    if place_date_birth_match:
        place = place_date_birth_match.group(1).strip()
        date = place_date_birth_match.group(2).strip()
        data["Place & Date of Birth"] = f"{place}, {format_date(date)}"
    else:
        data["Place & Date of Birth"] = None
    
    # Extract Passport Number
    passport_match = re.search(r"Passport Number\s*: ([A-Z0-9]+)", text)
    data["Passport Number"] = passport_match.group(1) if passport_match else None
    
    # Extract Passport Expiry
    passport_expiry_match = re.search(r"Passport Expiry\s*: ([\d-]+)", text)
    data["Passport Expiry"] = format_date(passport_expiry_match.group(1)) if passport_expiry_match else None
    
    # Extract Nationality
    nationality_match = re.search(r"Nationality\s*: ([A-Z]+)", text)
    data["Nationality"] = nationality_match.group(1) if nationality_match else None
    
    # Extract Gender
    gender_match = re.search(r"Gender\s*: ([A-Z]+)", text)
    data["Gender"] = gender_match.group(1) if gender_match else None
    
    # Extract Address
    address_match = re.search(r"Address\s*:\s*(.+)", text)
    data["Address"] = address_match.group(1).strip() if address_match else None
    
    # Extract Occupation
    occupation_match = re.search(r"Occupation\s*:\s*(.+)", text)
    data["Occupation"] = occupation_match.group(1).strip() if occupation_match else None
    
    # Extract Guarantor
    guarantor_match = re.search(r"Guarantor\s*:\s*(.+)", text)
    data["Guarantor"] = guarantor_match.group(1).strip() if guarantor_match else None
    
    # Extract Date Issue - mencari tanggal di bagian bawah dokumen
    date_issue_match = re.search(r"([A-Za-z]+),\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", text)
    if date_issue_match:
        day = date_issue_match.group(2)
        month = date_issue_match.group(3)
        year = date_issue_match.group(4)
        # Convert month name to number
        month_dict = {
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12'
        }
        month_num = month_dict.get(month, month)
        date_str = f"{day.zfill(2)}/{month_num}/{year}"
        data["Date Issue"] = format_date(date_str)
    else:
        # Fallback: cari pattern tanggal lain di dokumen
        fallback_date_match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", text)
        if fallback_date_match:
            data["Date Issue"] = format_date(fallback_date_match.group(0))
        else:
            data["Date Issue"] = None
    
    data["Jenis Dokumen"] = "ITAS"
    return data

# ========================= Ekstraksi ITK =========================
def extract_itk(text):
    data = {}
    
    # Extract Name
    name_match = re.search(r"([A-Z\s]+)\nPERMIT NUMBER", text)
    data["Name"] = name_match.group(1).strip() if name_match else None
    
    # Extract Permit Number
    permit_match = re.search(r"PERMIT NUMBER\s*:\s*([A-Z0-9-]+)", text)
    data["Permit Number"] = permit_match.group(1) if permit_match else None
    
    # Extract Stay Permit Expiry
    expiry_match = re.search(r"STAY PERMIT EXPIRY\s*:\s*([\d/]+)", text)
    data["Stay Permit Expiry"] = format_date(expiry_match.group(1)) if expiry_match else None
    
    # Extract Place & Date of Birth
    place_date_birth_match = re.search(r"Place / Date of Birth\s*.*:\s*([A-Za-z\s]+)\s*/\s*([\d-]+)", text)
    if place_date_birth_match:
        place = place_date_birth_match.group(1).strip()
        date = place_date_birth_match.group(2).strip()
        data["Place & Date of Birth"] = f"{place}, {format_date(date)}"
    else:
        data["Place & Date of Birth"] = None
    
    # Extract Passport Number
    passport_match = re.search(r"Passport Number\s*: ([A-Z0-9]+)", text)
    data["Passport Number"] = passport_match.group(1) if passport_match else None
    
    # Extract Passport Expiry
    passport_expiry_match = re.search(r"Passport Expiry\s*: ([\d-]+)", text)
    data["Passport Expiry"] = format_date(passport_expiry_match.group(1)) if passport_expiry_match else None
    
    # Extract Nationality
    nationality_match = re.search(r"Nationality\s*: ([A-Z]+)", text)
    data["Nationality"] = nationality_match.group(1) if nationality_match else None
    
    # Extract Gender
    gender_match = re.search(r"Gender\s*: ([A-Z]+)", text)
    data["Gender"] = gender_match.group(1) if gender_match else None
    
    # Extract Address
    address_match = re.search(r"Address\s*:\s*(.+)", text)
    data["Address"] = address_match.group(1).strip() if address_match else None
    
    # Extract Occupation
    occupation_match = re.search(r"Occupation\s*:\s*(.+)", text)
    data["Occupation"] = occupation_match.group(1).strip() if occupation_match else None
    
    # Extract Guarantor
    guarantor_match = re.search(r"Guarantor\s*:\s*(.+)", text)
    data["Guarantor"] = guarantor_match.group(1).strip() if guarantor_match else None
    
    # Extract Date Issue - mencari tanggal di bagian bawah dokumen
    date_issue_match = re.search(r"([A-Za-z]+),\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", text)
    if date_issue_match:
        day = date_issue_match.group(2)
        month = date_issue_match.group(3)
        year = date_issue_match.group(4)
        # Convert month name to number
        month_dict = {
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12'
        }
        month_num = month_dict.get(month, month)
        date_str = f"{day.zfill(2)}/{month_num}/{year}"
        data["Date Issue"] = format_date(date_str)
    else:
        # Fallback: cari pattern tanggal lain di dokumen
        fallback_date_match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", text)
        if fallback_date_match:
            data["Date Issue"] = format_date(fallback_date_match.group(0))
        else:
            data["Date Issue"] = None
    
    data["Jenis Dokumen"] = "ITK"
    return data

# ========================= Ekstraksi Notifikasi =========================
def extract_notifikasi(text):
    data = {
        "Nomor Keputusan": "",
        "Nama TKA": "",
        "Tempat/Tanggal Lahir": "",
        "Kewarganegaraan": "",
        "Alamat Tempat Tinggal": "",
        "Nomor Paspor": "",
        "Jabatan": "",
        "Lokasi Kerja": "",
        "Berlaku": "",
        "Date Issue": ""
    }
    
    def find(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    # Extract Nomor Keputusan
    nomor_keputusan_match = re.search(r"NOMOR\s+([A-Z0-9./-]+)", text, re.IGNORECASE)
    data["Nomor Keputusan"] = nomor_keputusan_match.group(1).strip() if nomor_keputusan_match else ""
    
    # Extract basic information
    data["Nama TKA"] = find(r"Nama TKA\s*:\s*(.*)")
    data["Tempat/Tanggal Lahir"] = find(r"Tempat/Tanggal Lahir\s*:\s*(.*)")
    data["Kewarganegaraan"] = find(r"Kewarganegaraan\s*:\s*(.*)")
    data["Alamat Tempat Tinggal"] = find(r"Alamat Tempat Tinggal\s*:\s*(.*)")
    data["Nomor Paspor"] = find(r"Nomor Paspor\s*:\s*(.*)")
    data["Jabatan"] = find(r"Jabatan\s*:\s*(.*)")
    data["Lokasi Kerja"] = find(r"Lokasi Kerja\s*:\s*(.*)")
    
    # Extract validity period
    valid_match = re.search(
        r"Berlaku\s*:?\s*(\d{2}[-/]\d{2}[-/]\d{4})\s*(?:s\.?d\.?|sampai dengan)?\s*(\d{2}[-/]\d{2}[-/]\d{4})",
        text, re.IGNORECASE)
    if not valid_match:
        valid_match = re.search(
            r"Tanggal Berlaku\s*:?\s*(\d{2}[-/]\d{2}[-/]\d{4})\s*s\.?d\.?\s*(\d{2}[-/]\d{2}[-/]\d{4})",
            text, re.IGNORECASE)
    if valid_match:
        start_date = format_date(valid_match.group(1))
        end_date = format_date(valid_match.group(2))
        data["Berlaku"] = f"{start_date} - {end_date}"
    
    # Extract Date Issue (tanggal ditetapkan)
    # Pattern untuk "Pada tanggal : DD Month YYYY" atau "Pada tanggal : DD-MM-YYYY"
    date_issue_match = re.search(
        r"Pada tanggal\s*:\s*(\d{1,2})\s+(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+(\d{4})",
        text, re.IGNORECASE)
    
    if date_issue_match:
        day = date_issue_match.group(1).zfill(2)
        month_name = date_issue_match.group(2)
        year = date_issue_match.group(3)
        
        # Convert month name to number
        month_map = {
            'januari': '01', 'februari': '02', 'maret': '03', 'april': '04',
            'mei': '05', 'juni': '06', 'juli': '07', 'agustus': '08',
            'september': '09', 'oktober': '10', 'november': '11', 'desember': '12'
        }
        month = month_map.get(month_name.lower(), '01')
        data["Date Issue"] = f"{day}/{month}/{year}"
    else:
        # Alternative pattern for numeric date format
        date_issue_match = re.search(
            r"Pada tanggal\s*:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})",
            text, re.IGNORECASE)
        if date_issue_match:
            data["Date Issue"] = format_date(date_issue_match.group(1))
    
    return data

# ========================= Ekstraksi DKPTKA (IMPROVED) =========================
def extract_dkptka_info(full_text: str) -> Dict[str, Optional[str]]:
    """
    Ekstraksi informasi DKPTKA yang diperbaiki dengan akurasi tinggi
    """
    
    def safe_extract(pattern: str, text: str, group: int = 1, flags: int = re.IGNORECASE) -> Optional[str]:
        """Ekstraksi aman dengan error handling"""
        try:
            match = re.search(pattern, text, flags)
            if match:
                result = match.group(group).strip()
                # Clean up extra whitespace
                result = re.sub(r'\s+', ' ', result)
                return result if result else None
            return None
        except Exception:
            return None

    def clean_extracted_text(text: str) -> Optional[str]:
        """Membersihkan teks dari karakter tidak perlu"""
        if not text:
            return None
        # Remove extra whitespace, newlines, and special characters
        cleaned = re.sub(r'\s+', ' ', text.strip())
        cleaned = re.sub(r'["\'\n\r\t]+', ' ', cleaned).strip()
        return cleaned if cleaned else None

    try:
        result = {}

        # 1. Extract Nama Pemberi Kerja
        company_patterns = [
            r'Nama\s+Pemberi\s+Kerja\s*:\s*([^\n]+)',  # Format standar
            r'([A-Z][A-Z\s]*PT\.?[A-Z\s]*)\s*(?=\n.*Alamat)',  # Nama sebelum alamat
            r'I\.\s*Pemberi\s+Kerja\s+TKA.*?:\s*\n\s*\d+\.\s*Nama\s+Pemberi\s+Kerja\s*:\s*([^\n]+)',  # Format dengan section
        ]
        
        company_name = None
        for pattern in company_patterns:
            company_name = safe_extract(pattern, full_text)
            if company_name:
                company_name = clean_extracted_text(company_name)
                break
        
        result["Nama Pemberi Kerja"] = company_name

        # 2. Extract Alamat - menangani format multi-line
        address_patterns = [
            r'Alamat\s*:\s*(.*?)(?=\n\s*\d+\.\s*Nomor\s+Telepon|\n\s*3\.|$)',
            r'Alamat\s*:\s*(.*?)(?=Nomor\s+Telepon|Email|$)',
        ]
        
        address = None
        for pattern in address_patterns:
            address_match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
            if address_match:
                address_text = address_match.group(1)
                # Clean multi-line address
                address = re.sub(r'\n\s*', ' ', address_text.strip())
                address = re.sub(r'\s+', ' ', address)
                break
        
        result["Alamat"] = clean_extracted_text(address)

        # 3. Extract Nomor Telepon
        phone_patterns = [
            r'Nomor\s+Telepon\s*:\s*([0-9\-\+\(\)\s]+)',
            r'Telepon\s*:\s*([0-9\-\+\(\)\s]+)',
        ]
        
        phone = None
        for pattern in phone_patterns:
            phone = safe_extract(pattern, full_text)
            if phone:
                # Clean phone number format
                phone = re.sub(r'[^\d\-\+\(\)]', '', phone)
                break
        
        result["No Telepon"] = phone

        # 4. Extract Email
        email_patterns = [
            r'Email\s*:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'E-mail\s*:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        ]
        
        email = None
        for pattern in email_patterns:
            email = safe_extract(pattern, full_text)
            if email:
                break
        
        result["Email"] = email

        # 5. Extract Nama TKA
        tka_patterns = [
            r'Nama\s+TKA\s*:\s*([A-Z\s]+?)(?=\n\s*\d+\.|\n\s*Tempat)',
            r'Nama\s+TKA\s*:\s*([^\n]+)',
        ]
        
        tka_name = None
        for pattern in tka_patterns:
            tka_name = safe_extract(pattern, full_text)
            if tka_name:
                break
        
        result["Nama TKA"] = clean_extracted_text(tka_name)

        # 6. Extract Tempat/Tanggal Lahir
        birth_patterns = [
            r'Tempat\s*/\s*Tgl\s+Lahir\s*:\s*([^,\n]+,\s*\d{1,2}\s+\w+\s+\d{4})',
            r'Tempat.*?Lahir\s*:\s*([^\n]+)',
        ]
        
        birth_info = None
        for pattern in birth_patterns:
            birth_info = safe_extract(pattern, full_text)
            if birth_info:
                break
        
        result["Tempat/Tanggal Lahir"] = clean_extracted_text(birth_info)

        # 7. Extract Nomor Paspor
        passport_patterns = [
            r'Nomor\s+Paspor\s*:\s*([A-Z0-9]+)',
            r'Paspor\s*:\s*([A-Z0-9]+)',
        ]
        
        passport = None
        for pattern in passport_patterns:
            passport = safe_extract(pattern, full_text)
            if passport:
                break
        
        result["Nomor Paspor"] = passport

        # 8. Extract Kewarganegaraan
        nationality_patterns = [
            r'Kewarganegaraan\s*:\s*([A-Z\s]+?)(?=\n\s*\d+\.|\n\s*Jabatan)',
            r'Kewarganegaraan\s*:\s*([^\n]+)',
        ]
        
        nationality = None
        for pattern in nationality_patterns:
            nationality = safe_extract(pattern, full_text)
            if nationality:
                break
        
        result["Kewarganegaraan"] = clean_extracted_text(nationality)

        # 9. Extract Jabatan
        position_patterns = [
            r'Jabatan\s*:\s*([A-Z\s]+?)(?=\n\s*\d+\.|\n\s*Kanim)',
            r'Jabatan\s*:\s*([^\n]+)',
        ]
        
        position = None
        for pattern in position_patterns:
            position = safe_extract(pattern, full_text)
            if position:
                break
        
        result["Jabatan"] = clean_extracted_text(position)

        # 10. Extract Kanim
        kanim_patterns = [
            r'Kanim\s+Perpanjangan\s+ITAS/ITAP\s*:\s*([A-Za-z\s]+?)(?=\n\s*\d+\.|\n\s*Lokasi)',
            r'Kanim.*?:\s*([^\n]+)',
        ]
        
        kanim = None
        for pattern in kanim_patterns:
            kanim = safe_extract(pattern, full_text)
            if kanim:
                break
        
        result["Kanim"] = clean_extracted_text(kanim)

        # 11. Extract Lokasi Kerja
        location_patterns = [
            r'Lokasi\s+Kerja\s*:\s*([A-Za-z\(\)\s]+?)(?=\n\s*\d+\.|\n\s*Jangka)',
            r'Lokasi\s+Kerja\s*:\s*([^\n]+)',
        ]
        
        work_location = None
        for pattern in location_patterns:
            work_location = safe_extract(pattern, full_text)
            if work_location:
                break
        
        result["Lokasi Kerja"] = clean_extracted_text(work_location)

        # 12. Extract Jangka Waktu
        duration_patterns = [
            r'Jangka\s+Waktu\s*:\s*(.*?)(?=\n\s*III\.|$)',
            r'Jangka\s+Waktu\s*:\s*([^\n]+)',
        ]
        
        duration = None
        for pattern in duration_patterns:
            duration_match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
            if duration_match:
                duration_text = duration_match.group(1).strip()
                # Clean multi-line duration
                duration = re.sub(r'\n\s*', ' ', duration_text)
                duration = re.sub(r'\s+', ' ', duration).strip()
                break
        
        result["Jangka Waktu"] = duration

        # 13. Extract Tanggal Penerbitan
        issue_date_patterns = [
            r'Tanggal\s+Penerbitan\s*:\s*(\d{1,2}\s+\w+\s+\d{4})',
            r'Tanggal\s+Penerbitan\s*:\s*(\d{1,2}[\-/]\d{1,2}[\-/]\d{4})',
        ]
        
        issue_date = None
        for pattern in issue_date_patterns:
            issue_date = safe_extract(pattern, full_text)
            if issue_date:
                break
        
        result["Tanggal Penerbitan"] = issue_date

        # 14. Extract Kode Billing Pembayaran DKPTKA - tangani baris terputus
        billing_code = None

        # Pecah text menjadi list baris
        lines = full_text.splitlines()
        for i, line in enumerate(lines):
            # Cari baris yang mengandung 'Kode Billing Pembayaran'
            if 'Kode Billing Pembayaran' in line:
                # Cek dua baris setelahnya
                next_lines = lines[i+1:i+4]  # Antisipasi 2 baris ke bawah
                joined = " ".join(next_lines)
                match = re.search(r'(\d{12,})', joined)
                if match:
                    billing_code = match.group(1).strip()
                    break

        result["Kode Billing Pembayaran"] = billing_code
        
        # 15. Extract No Rekening
        account_patterns = [
            r'No\s+Rekening\s*:\s*([0-9]+)',
            r'Rekening\s*:\s*([0-9]+)',
        ]
        
        account_no = None
        for pattern in account_patterns:
            account_no = safe_extract(pattern, full_text)
            if account_no:
                break
        
        result["No Rekening"] = account_no

        # 17. Extract DKPTKA Amount
        dkptka_patterns = [
            r'DKPTKA\s+yang\s+dibayarkan\s*:\s*(.*?)(?=\n\s*Setelah|\n\s*V\.|\n\s*\*|$)',
            r'DKPTKA.*?:\s*(US\$[^\n]+)',
        ]
        
        dkptka_amount = None
        for pattern in dkptka_patterns:
            dkptka_match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
            if dkptka_match:
                dkptka_text = dkptka_match.group(1).strip()
                # Clean multi-line DKPTKA amount
                dkptka_amount = re.sub(r'\n\s*', ' ', dkptka_text)
                dkptka_amount = re.sub(r'\s+', ' ', dkptka_amount).strip()
                break
        
        result["DKPTKA"] = dkptka_amount

        # 18. Set document type
        result["Jenis Dokumen"] = "DKPTKA"

        # Filter out None values and empty strings
        filtered_result = {}
        for key, value in result.items():
            if value and str(value).strip():
                filtered_result[key] = value
            else:
                filtered_result[key] = None

        return filtered_result

    except Exception as e:
        return {
            "Error": f"Gagal mengekstrak data DKPTKA: {str(e)}",
            "Jenis Dokumen": "DKPTKA"
        }


def validate_dkptka_data(extracted_data: Dict) -> Dict[str, str]:
    """
    Validasi data DKPTKA yang diekstrak dan memberikan feedback
    Termasuk validasi Kode Billing Pembayaran
    """
    validation_result = {
        "status": "valid",
        "missing_fields": [],
        "warnings": []
    }
    
    # Required fields for DKPTKA (updated with new field)
    required_fields = [
        "Nama Pemberi Kerja",
        "Alamat", 
        "Nama TKA",
        "Nomor Paspor",
        "Kode Billing Pembayaran",
        "DKPTKA"
    ]
    
    missing_fields = []
    for field in required_fields:
        if not extracted_data.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        validation_result["status"] = "incomplete"
        validation_result["missing_fields"] = missing_fields
    
    # Check format warnings
    if extracted_data.get("Email") and "@" not in str(extracted_data["Email"]):
        validation_result["warnings"].append("Format email mungkin tidak valid")
    
    if extracted_data.get("No Telepon") and not re.search(r'\d', str(extracted_data["No Telepon"])):
        validation_result["warnings"].append("Format nomor telepon mungkin tidak valid")
    
    # Validate Kode Billing Pembayaran
    billing_code = extracted_data.get("Kode Billing Pembayaran")
    if billing_code:
        if not re.match(r'^\d{10,}$', str(billing_code)):
            validation_result["warnings"].append("Format kode billing pembayaran mungkin tidak valid (harus berupa angka minimal 10 digit)")
    
    return validation_result

# ========================= Main Extraction Function =========================
def extract_document_data(text: str, document_type: str) -> Dict:
    """
    Main function to extract data based on document type
    """
    extractors = {
        "SKTT": extract_sktt,
        "EVLN": extract_evln,
        "ITAS": extract_itas,
        "ITK": extract_itk,
        "NOTIFIKASI": extract_notifikasi,
        "DKPTKA": extract_dkptka_info
    }
    
    if document_type.upper() in extractors:
        try:
            return extractors[document_type.upper()](text)
        except Exception as e:
            return {
                "Error": f"Gagal mengekstrak dokumen {document_type}: {str(e)}",
                "Jenis Dokumen": document_type
            }
    else:
        return {
            "Error": f"Tipe dokumen {document_type} tidak didukung",
            "Jenis Dokumen": document_type
        }


# ========================= Test Function =========================
def test_extraction(text: str, document_type: str):
    """Test function untuk menguji ekstraksi berbagai jenis dokumen"""
    print(f"=== HASIL EKSTRAKSI {document_type.upper()} ===")
    
    # Extract data
    extracted_data = extract_document_data(text, document_type)
    
    # Display results
    for key, value in extracted_data.items():
        print(f"{key:<25}: {value}")
    
    # Special validation for DKPTKA
    if document_type.upper() == "DKPTKA":
        print("\n=== VALIDASI DATA DKPTKA ===")
        validation = validate_dkptka_data(extracted_data)
        print(f"Status: {validation['status']}")
        
        if validation['missing_fields']:
            print(f"Field yang hilang: {', '.join(validation['missing_fields'])}")
        
        if validation['warnings']:
            print(f"Peringatan: {'; '.join(validation['warnings'])}")
    
    return extracted_data
