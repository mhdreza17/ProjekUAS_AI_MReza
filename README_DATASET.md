# Panduan Penempatan Dataset PDF

## Struktur Direktori Dataset
\`\`\`
standards/
├── Global/
│   ├── GDPR.pdf                    # General Data Protection Regulation
│   ├── NIST_Cybersecurity_Framework.pdf
│   └── ISO_27001.pdf               # (opsional)
└── Nasional/
    ├── UU_PDP.pdf                  # UU No. 27 Tahun 2022 tentang PDP
    ├── POJK.pdf                    # Peraturan OJK terkait
    ├── BSSN_A.pdf                  # Dokumen BSSN bagian A
    ├── BSSN_B.pdf                  # Dokumen BSSN bagian B
    └── BSSN_C.pdf                  # Dokumen BSSN bagian C
\`\`\`

## Cara Penempatan File:
1. Buat folder `standards` di root project
2. Buat subfolder `Global` dan `Nasional`
3. Letakkan file PDF sesuai kategori
4. Pastikan nama file sesuai dengan yang tercantum di atas
5. File akan otomatis diproses saat aplikasi pertama kali dijalankan

## Catatan Penting:
- File PDF harus dapat dibaca (bukan scan yang buruk)
- Ukuran maksimal per file: 50MB
- Format yang didukung: PDF, DOCX, TXT
- Sistem akan membuat embeddings otomatis dari file-file ini
