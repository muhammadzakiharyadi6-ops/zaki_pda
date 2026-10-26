import streamlit as st
import json
import os
import pandas as pd
import openpyxl
from rag_engine import SyuhadaRAGEngine

# Configuration Page Streamlit
st.set_page_config(
    page_title="Syuhada-ArchBot | RAG Metadata Cagar Budaya",
    page_icon="🕌",
    layout="wide"
)

# Custom CSS Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        color: #1E293B;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 20px;
    }
    .stChatMessage {
        border-radius: 8px;
    }
    .doc-card {
        background-color: #F1F5F9;
        border-left: 4px solid #3B82F6;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)

def ensure_data_file():
    os.makedirs("data", exist_ok=True)
    json_path = "data/metadata_syuhada.json"
    excel_path = "Metadata_DublinCore_RAG_Masjid_Syuhada.xlsx"
    
    if not os.path.exists(json_path) and os.path.exists(excel_path):
        wb = openpyxl.load_workbook(excel_path)
        ws = wb["Metadata Elemen Arsitektur"]
        
        records = []
        for row in ws.iter_rows(min_row=4, values_only=True):
            if not row or not row[0]:
                continue
                
            element_id = str(row[0]).strip()
            drawing_code = str(row[1]).strip() if row[1] else ""
            title = str(row[2]).strip() if row[2] else ""
            category = str(row[3]).strip() if row[3] else ""
            room_code = str(row[4]).strip() if row[4] else ""
            building_level = str(row[5]).strip() if row[5] else ""
            materials = str(row[6]).strip() if row[6] else ""
            dimensions = str(row[7]).strip() if row[7] else ""
            year_built = str(row[8]).strip() if row[8] else ""
            description = str(row[9]).strip() if row[9] else ""
            significance = str(row[10]).strip() if row[10] else ""
            condition = str(row[11]).strip() if row[11] else ""
            preservation = str(row[12]).strip() if row[12] else ""
            source_doc = str(row[13]).strip() if row[13] else ""

            full_text = f"Elemen: {title} ({element_id}). Kode Gambar: {drawing_code}. Kategori: {category}. Lokasi: {room_code}, {building_level}. Dimensi: {dimensions}. Bahan: {materials}. Deskripsi: {description}. Peringkat Signifikansi: {significance}. Kondisi Kerusakan: {condition}. Rekomendasi Pemugaran: {preservation}. Sumber: {source_doc}."

            doc_entry = {
                "chunk_id": f"{element_id}_FULL",
                "text": full_text,
                "metadata": {
                    "element_id": element_id,
                    "drawing_code": drawing_code,
                    "title": title,
                    "category": category,
                    "room_code": room_code,
                    "building_level": building_level,
                    "materials": materials,
                    "dimensions": dimensions,
                    "year_built": year_built,
                    "significance": significance,
                    "condition": condition,
                    "preservation_policy": preservation,
                    "source_doc": source_doc
                }
            }
            records.append(doc_entry)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

ensure_data_file()

st.sidebar.image("https://img.icons8.com/color/96/mosque.png", width=64)
st.sidebar.title("📌 Navigasi & Setup")

api_key_env = os.getenv("GEMINI_API_KEY")
if not api_key_env and "GEMINI_API_KEY" in st.secrets:
    api_key_env = st.secrets["GEMINI_API_KEY"]

user_api_key = st.sidebar.text_input("Gemini API Key:", value=api_key_env if api_key_env else "", type="password", help="Dapatkan API Key dari Google AI Studio")

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filter & Eksplorasi Data")

@st.cache_data
def load_metadata():
    json_path = "data/metadata_syuhada.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

raw_data = load_metadata()
if not raw_data:
    st.error("File database metadata tidak ditemukan. Pastikan file Excel 'Metadata_DublinCore_RAG_Masjid_Syuhada.xlsx' ada di dalam repository GitHub Anda.")
    st.stop()

df_elements = pd.DataFrame([d["metadata"] for d in raw_data])

selected_category = st.sidebar.selectbox("Filter Kategori:", ["Semua Kategori"] + list(df_elements["category"].unique()))
selected_level = st.sidebar.selectbox("Filter Lantai:", ["Semua Lantai"] + list(df_elements["building_level"].unique()))

df_filtered = df_elements.copy()
if selected_category != "Semua Kategori":
    df_filtered = df_filtered[df_filtered["category"] == selected_category]
if selected_level != "Semua Lantai":
    df_filtered = df_filtered[df_filtered["building_level"] == selected_level]

st.sidebar.write(f"Menampilkan **{len(df_filtered)}** elemen.")

st.markdown('<p class="main-title">🕌 Syuhada-ArchBot (RAG AI Cagar Budaya)</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Sistem Tanya-Jawab Berbasis Metadata Dublin Core & Pedoman Pelestarian Masjid Peringatan Syuhada Yogyakarta</p>', unsafe_allow_html=True)

tab_chat, tab_explorer, tab_schema = st.tabs(["💬 Chatbot RAG", "📋 Eksplorasi Inventarisasi Data", "📐 Skema Metadata (DCMI)"])

@st.cache_resource
def get_rag_engine(key):
    return SyuhadaRAGEngine(api_key=key)

rag_engine = get_rag_engine(user_api_key)

with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Assalamu'alaikum / Selamat datang! Saya adalah **Syuhada-ArchBot**, asisten AI preservasi cagar budaya Masjid Syuhada Yogyakarta. Silakan tanyakan informasi mengenai elemen arsitektur, kerusakan, atau rekomendasi pemugaran."}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "retrieved_docs" in message and message["retrieved_docs"]:
                with st.expander("📚 Sumber Metadata RAG Terkait"):
                    for doc in message["retrieved_docs"]:
                        m = doc["metadata"]
                        st.markdown(f"""
                        <div class="doc-card">
                            <b>[{m['element_id']}] {m['title']}</b> ({m['drawing_code']})<br/>
                            📍 <i>{m['building_level']} - {m['room_code']}</i> | 🏷️ Kategori: {m['category']}<br/>
                            📄 Sumber: {m['source_doc']}
                        </div>
                        """, unsafe_allow_html=True)

    if prompt := st.chat_input("Tanyakan sesuatu (contoh: Bagaimana kondisi kubah utama dan rekomendasinya?)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Mencari metadata & mengolah jawaban AI..."):
                response_text, retrieved_docs = rag_engine.generate_response(prompt)
                st.markdown(response_text)
                
                if retrieved_docs:
                    with st.expander("📚 Sumber Metadata RAG Terkait"):
                        for doc in retrieved_docs:
                            m = doc["metadata"]
                            st.markdown(f"""
                            <div class="doc-card">
                                <b>[{m['element_id']}] {m['title']}</b> ({m['drawing_code']})<br/>
                                📍 <i>{m['building_level']} - {m['room_code']}</i> | 🏷️ Kategori: {m['category']}<br/>
                                📄 Sumber: {m['source_doc']}
                            </div>
                            """, unsafe_allow_html=True)

        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_text,
            "retrieved_docs": retrieved_docs
        })

with tab_explorer:
    st.subheader("Daftar Inventarisasi Elemen Arsitektur")
    st.dataframe(
        df_filtered[["element_id", "drawing_code", "title", "category", "building_level", "significance", "condition"]],
        use_container_width=True,
        column_config={
            "element_id": "Kode Elemen",
            "drawing_code": "Kode Gambar",
            "title": "Nama Elemen",
            "category": "Kategori",
            "building_level": "Lantai",
            "significance": "Signifikansi",
            "condition": "Kondisi Kerusakan"
        }
    )

with tab_schema:
    st.subheader("Pemetaan Skema Dublin Core (DCMI) ke RAG Pipeline")
    st.markdown("""
    Sistem RAG ini menggunakan adaptasi **Dublin Core Metadata Initiative (DCMI)** untuk menstrukturkan data fisik dan kondisi bangunan cagar budaya:
    
    * **`dc:identifier`**: Mapping ke `element_id` dan `drawing_code` untuk keterlacakan gambar kerja CAD.
    * **`dc:title`**: Mapping ke `title` elemen arsitektur.
    * **`dc:description`**: Berisi deskripsi arsitektur teknis dan nota mekanika struktur.
    * **`dc:coverage`**: Menyimpan level lantai (`building_level`) dan kode ruangan (`room_code`).
    * **`dc:relation`**: Menyimpan tingkat **Signifikansi Cagar Budaya**, diagnosis **Kondisi Kerusakan**, serta **Rekomendasi Pemugaran**.
    * **`dc:source`**: Menyimpan sitasi halaman dan dokumen rujukan resmi (Dok 01 s.d. Dok 05).
    """)
