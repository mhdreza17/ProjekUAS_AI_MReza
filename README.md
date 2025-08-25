
# 🤖 ReguBot - AI Compliance Checker

BY :
MUHAMMAD REZA 
2221101826
III RPLK TAHUN 2025
REKAYASA KRIPTOGRAFI 
POLITEKNIK SIBER DAN SANDI NEGARA


## 📝 Overview & Konsep Sistem

**ReguBot** adalah sistem AI multi-agent yang dirancang untuk melakukan analisis kepatuhan (compliance) dokumen digital secara otomatis, evidence-based, dan sepenuhnya berjalan secara lokal/offline. Sistem ini menggabungkan beberapa agent AI yang saling berkolaborasi untuk menghasilkan audit compliance yang akurat, terstruktur, dan dapat dipertanggungjawabkan.

### Konsep Multi-Agent AI
ReguBot terdiri dari 5 agent spesialis, masing-masing memiliki tugas dan keahlian berbeda:

1. **Document Collector Agent**: Ekstraksi dan validasi teks dari dokumen (PDF, DOCX, TXT), termasuk OCR untuk dokumen scan.
2. **Standard Retriever Agent**: Mengambil dan memetakan regulasi/standar compliance yang relevan dari database vektor lokal (ChromaDB), lengkap dengan metadata pasal/artikel/section.
3. **Compliance Checker Agent**: Menganalisis dokumen terhadap standar yang dipilih menggunakan LLM (Groq Llama), menilai tingkat kepatuhan, menemukan evidence, dan memberikan penjelasan serta referensi pasal/artikel yang jelas.
4. **Report Generator Agent**: Membuat laporan audit compliance profesional (PDF/DOCX) yang berisi breakdown score, evidence, referensi regulasi, rekomendasi, dan roadmap implementasi.
5. **QA Agent**: Chatbot interaktif untuk tanya jawab, konsultasi, dan penjelasan detail hasil analisis, dengan jawaban berbasis regulasi dan referensi pasal.

### Alur Kerja Sistem
1. **Upload Dokumen**: User mengunggah dokumen digital yang akan dianalisis.
2. **Pilih Standar Compliance**: User memilih satu atau lebih standar regulasi (GDPR, NIST, UU PDP, POJK, BSSN).
3. **Analisis Multi-Agent**: Kelima agent bekerja secara paralel:
	- Ekstraksi teks dan preprocessing
	- Pemetaan regulasi dan chunking pasal/artikel
	- Analisis kepatuhan, evidence extraction, scoring berbobot
	- Pembuatan laporan audit lengkap
	- Chatbot QA siap menjawab pertanyaan user
4. **Review Hasil**: User dapat melihat compliance score, daftar issues, requirements yang sudah terpenuhi, rekomendasi, dan referensi pasal/artikel secara detail.
5. **Download Laporan**: Hasil analisis dapat diunduh dalam format PDF/DOCX.
6. **Tanya Chatbot**: User dapat bertanya tentang hasil analisis, improvement, atau detail regulasi.

### Keunggulan ReguBot
- **Evidence-Based**: Semua temuan compliance didukung oleh evidence konkret dari dokumen dan referensi pasal/artikel regulasi.
- **Explainable AI**: Penjelasan, rekomendasi, dan referensi yang dihasilkan dapat dipertanggungjawabkan secara akademis dan profesional.
- **100% Offline & Secure**: Tidak ada data yang keluar dari mesin user, cocok untuk kebutuhan audit internal dan presentasi akademik.
- **Interaktif & Informatif**: Dashboard modern, laporan profesional, dan chatbot QA membuat sistem mudah digunakan dan sangat informatif.
- **Extensible**: Standar regulasi dapat ditambah/diubah sesuai kebutuhan riset atau bisnis.

Sistem ini sangat cocok untuk tugas akhir, riset compliance AI, audit internal, maupun presentasi di mata kuliah AI karena menggabungkan konsep multi-agent, NLP, LLM, retrieval-augmented generation, dan explainable AI dalam satu platform yang utuh.

## 🌟 Fitur Utama

- **🔒 100% Lokal & Offline**: Semua data diproses di mesin Anda, tidak ada data yang keluar
- **🤖 Multi-Agent AI System**: 5 agent khusus yang bekerja sama untuk analisis mendalam
- **📄 Multi-Format Support**: PDF, DOCX, TXT dengan OCR untuk dokumen scan
- **🎯 Compliance Standards**: GDPR, NIST, UU PDP, POJK, BSSN
- **📊 Laporan Profesional**: Export ke PDF dan DOCX
- **💬 Interactive Chatbot**: Tanya jawab tentang hasil analisis
- **⚡ Powered by Groq**: AI processing yang cepat dan akurat

## 🏗️ Arsitektur Multi-Agent

### 1. 📥 Document Collector Agent
- Ekstraksi teks dari PDF, DOCX, TXT
- OCR untuk dokumen scan menggunakan Tesseract
- Validasi format dan preprocessing

### 2. 🔍 Compliance Checker Agent  
- Analisis kepatuhan menggunakan Groq AI
- Perbandingan dengan standar regulasi
- Identifikasi issues dan compliance gaps

### 3. 📚 Standard Retriever Agent
- Database vektor lokal dengan ChromaDB
- RAG (Retrieval-Augmented Generation)
- Pencarian semantik regulasi yang relevan

### 4. 📄 Report Generator Agent
- Generate laporan profesional
- Export ke PDF dan DOCX
- Struktur laporan yang komprehensif

### 5. 💬 Interactive QA Agent
- Chatbot untuk tanya jawab
- Jawaban berdasarkan analisis dan regulasi
- Referensi pasal yang akurat

DOKUMENTASI 
<img width="745" height="666" alt="image" src="https://github.com/user-attachments/assets/32aff688-3ff6-4f00-9548-d7ea836d14f0" />

## 🚀 Instalasi dan Setup

### Prasyarat
- Python 3.8+
- Tesseract OCR
- Groq API Key

### Langkah 1: Clone Repository
\`\`\`bash
git clone <repository-url>
cd regubot-system
\`\`\`

### Langkah 2: Setup Virtual Environment
\`\`\`bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
\`\`\`

### Langkah 3: Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Langkah 4: Install Tesseract OCR

**Windows:**
1. Download dari: https://github.com/UB-Mannheim/tesseract/wiki
2. Install dan tambahkan ke PATH

**Ubuntu/Debian:**
\`\`\`bash
sudo apt-get install tesseract-ocr tesseract-ocr-ind
\`\`\`

**macOS:**
\`\`\`bash
brew install tesseract tesseract-lang
\`\`\`

### Langkah 5: Setup Environment Variables
\`\`\`bash
cp .env.example .env
\`\`\`

Edit `.env` dan tambahkan Groq API Key:
\`\`\`env
GROQ_API_KEY=your_groq_api_key_here
\`\`\`

### Langkah 6: Setup Direktori Standards
\`\`\`bash
mkdir -p standards/Global
mkdir -p standards/Nasional
\`\`\`

Tambahkan file PDF regulasi ke direktori yang sesuai:
- `standards/Global/`: GDPR.pdf, NIST.pdf
- `standards/Nasional/`: UU_PDP.pdf, POJK.pdf, BSSN_A.pdf, BSSN_B.pdf, BSSN_C.pdf

### Langkah 7: Jalankan Aplikasi
\`\`\`bash
python app.py
\`\`\`

Buka browser dan akses: http://localhost:5000

## 📖 Cara Penggunaan

### 1. Upload Dokumen
- Drag & drop atau browse file (PDF/DOCX/TXT)
- Maksimal ukuran file: 10MB
- Sistem akan otomatis ekstrak teks

### 2. Pilih Standar Compliance
- **Global**: GDPR, NIST
- **Nasional**: UU PDP, POJK, BSSN
- Pilih satu atau lebih standar

### 3. Mulai Analisis
- Klik "Mulai Analisis Compliance"
- Pantau progress 5 agent yang bekerja
- Tunggu hingga analisis selesai

### 4. Review Hasil
- **Compliance Score**: Persentase kepatuhan
- **Issues**: Daftar ketidaksesuaian dengan penjelasan
- **Compliant Items**: Requirements yang sudah terpenuhi
- **Recommendations**: Saran perbaikan

### 5. Download Laporan
- Format PDF untuk presentasi
- Format DOCX untuk editing

### 6. Tanya Chatbot
- Ajukan pertanyaan tentang hasil analisis
- Contoh: "Mengapa bagian ini tidak compliant?"
- Dapatkan jawaban dengan referensi pasal

## 🔧 Konfigurasi Lanjutan

### Menambah Standar Baru
1. Tambahkan file PDF ke direktori `standards/`
2. Restart aplikasi untuk reload database
3. Standar akan otomatis terdeteksi

### Mengubah Model AI
Edit `agents/compliance_checker.py` dan `agents/qa_agent.py`:
```python
model="llama-3.1-70b-versatile"  # Ganti dengan model lain
