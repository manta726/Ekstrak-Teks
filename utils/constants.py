"""
Constants for LDB Application
"""

# Document processing status
STATUS_CODES = {
    'PENDING': 'pending',
    'PROCESSING': 'processing',
    'COMPLETED': 'completed',
    'FAILED': 'failed',
    'CANCELLED': 'cancelled'
}

# Error messages
ERROR_MESSAGES = {
    'FILE_TOO_LARGE': 'File terlalu besar. Maksimal 50MB.',
    'INVALID_FORMAT': 'Format file tidak didukung.',
    'EXTRACTION_FAILED': 'Gagal mengekstrak data dari dokumen.',
    'DATABASE_ERROR': 'Terjadi kesalahan pada database.',
    'AUTH_FAILED': 'Autentikasi gagal.',
    'ACCESS_DENIED': 'Akses ditolak.',
    'SESSION_EXPIRED': 'Sesi telah berakhir.',
}

# Success messages
SUCCESS_MESSAGES = {
    'EXTRACTION_SUCCESS': 'Dokumen berhasil diekstrak.',
    'LOGIN_SUCCESS': 'Login berhasil.',
    'LOGOUT_SUCCESS': 'Logout berhasil.',
    'REGISTRATION_SUCCESS': 'Registrasi berhasil.',
    'UPDATE_SUCCESS': 'Data berhasil diperbarui.',
}

# Document types with descriptions
DOCUMENT_TYPES = {
    'SKTT': {
        'name': 'Surat Keterangan Tinggal Terbatas',
        'description': 'Dokumen izin tinggal terbatas',
        'fields': ['nama', 'nomor_paspor', 'kebangsaan', 'tanggal_lahir', 'masa_berlaku']
    },
    'EVLN': {
        'name': 'Exit Visa Luar Negeri',
        'description': 'Visa keluar untuk warga negara asing',
        'fields': ['nama', 'nomor_paspor', 'tujuan', 'tanggal_keberangkatan', 'masa_berlaku']
    },
    'ITAS': {
        'name': 'Izin Tinggal Terbatas',
        'description': 'Izin tinggal terbatas untuk WNA',
        'fields': ['nama', 'nomor_paspor', 'sponsor', 'jenis_kegiatan', 'masa_berlaku']
    },
    'ITK': {
        'name': 'Izin Tinggal Kunjungan',
        'description': 'Izin tinggal kunjungan',
        'fields': ['nama', 'nomor_paspor', 'tujuan_kunjungan', 'lama_tinggal', 'masa_berlaku']
    },
    'NOTIFICATION': {
        'name': 'Notifikasi Imigrasi',
        'description': 'Notifikasi dari kantor imigrasi',
        'fields': ['nomor_notifikasi', 'perihal', 'tanggal', 'status']
    }
}
