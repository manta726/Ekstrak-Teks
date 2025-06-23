import re
from datetime import datetime
import base64

def clean_text(text, is_name_or_pob=False):
    text = re.sub(r"Reference No|Payment Receipt No|Jenis Kelamin|Kewarganegaraan|Pekerjaan|Alamat", "", text)
    if is_name_or_pob:
        text = re.sub(r"\.", "", text)
    text = re.sub(r"[^A-Za-z0-9\s,./-]", "", text).strip()
    return " ".join(text.split())

def format_date(date_str):
    match = re.search(r"(\d{2})[-/](\d{2})[-/](\d{4})", date_str)
    if match:
        day, month, year = match.groups()
        return f"{day}/{month}/{year}"
    return date_str

def split_birth_place_date(text):
    if text:
        parts = text.split(", ")
        if len(parts) == 2:
            return parts[0].strip(), format_date(parts[1])
    return text, None

def sanitize_filename_part(text):
    return re.sub(r'[^\w\s-]', '', text).strip()

def generate_new_filename(extracted_data, use_name=True, use_passport=True, max_length=30):
    def safe_part(text):
        if not text:
            return ""
        # Ganti newline dengan spasi
        text = text.replace("\n", " ").replace("\r", " ")
        # Bersihkan karakter aneh
        text = sanitize_filename_part(text)
        # Potong maksimal max_length karakter
        if len(text) > max_length:
            text = text[:max_length].strip()
        return text

    name_raw = (
        extracted_data.get("Name") or
        extracted_data.get("Nama TKA") or
        ""
    )
    passport_raw = (
        extracted_data.get("Passport Number") or
        extracted_data.get("Nomor Paspor") or
        extracted_data.get("Passport No") or
        extracted_data.get("KITAS/KITAP") or
        ""
    )
    name = safe_part(name_raw) if use_name and name_raw else ""
    passport = safe_part(passport_raw) if use_passport and passport_raw else ""

    parts = [p for p in [name, passport] if p]
    base_name = " ".join(parts) if parts else "RENAMED"

    # Tambahkan ekstensi .pdf
    return f"{base_name}.pdf"

def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Selamat Pagi"
    elif 12 <= hour < 17:
        return "Selamat Siang"
    else:
        return "Selamat Malam"

def get_binary_file_downloader_html(bin_data, file_label='File', button_text='Download'):
    bin_str = base64.b64encode(bin_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}" style="text-decoration:none;"><button style="background-color:#4CAF50; color:white; padding:10px 20px; border:none; border-radius:4px; cursor:pointer;">{button_text}</button></a>'
    return href
