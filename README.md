# 🕌 Syuhada-ArchBot: RAG Chatbot Cagar Budaya (Google Gemini + Streamlit)

Aplikasi Chatbot RAG (*Retrieval-Augmented Generation*) untuk publikasi data inventarisasi elemen arsitektur & rekomendasi preservasi cagar budaya **Masjid Peringatan Syuhada Yogyakarta** berbasis **Google Gemini API**.

---

## 📁 Isi Berkas Repositori

```text
syuhada_rag_app/
├── .streamlit/
│   └── config.toml          # Konfigurasi tema visual Streamlit
├── data/
│   └── metadata_syuhada.json# Database JSON hasil ekstraksi Excel
├── app.py                   # Aplikasi utama Streamlit (UI & Chat Interface)
├── rag_engine.py            # Engine RAG (Google Gemini + Hybrid Search)
├── generate_data.py         # Script pembaca Excel -> JSON Database
├── requirements.txt         # Dependency library Python
└── README.md                # Panduan deployment ini
```

---

## 🚀 Panduan Menjalankan Secara Lokal

1. **Ekstrak berkas ZIP** ini ke dalam komputer Anda.
2. Buka Terminal / Command Prompt pada folder hasil ekstrak.
3. Install semua library pendukung:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan aplikasi Streamlit:
   ```bash
   streamlit run app.py
   ```
5. Buka browser di `http://localhost:8501`, lalu masukkan **Google Gemini API Key** Anda pada bagian sidebar.

---

## 🌐 Panduan Deployment ke Streamlit Community Cloud (streamlit.io)

1. **Upload / Push** seluruh folder/berkas di dalam ZIP ini ke repositori baru di **GitHub** Anda.
2. Buka **[share.streamlit.io](https://share.streamlit.io/)** dan login dengan akun GitHub Anda.
3. Klik tombol **"New app"**.
4. Pilih repositori GitHub Anda, branch `main`, dan isi Main file path dengan `app.py`.
5. Klik **Advanced settings...** -> **Secrets**, lalu tambahkan API Key Gemini Anda:
   ```toml
   GEMINI_API_KEY = "AIzaSy... (API Key Anda di sini)"
   ```
6. Klik **Save** lalu **Deploy!**. Aplikasi Anda siap diakses secara umum oleh publik.
