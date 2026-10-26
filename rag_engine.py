import json
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
from google.genai import types

class SyuhadaRAGEngine:
    def __init__(self, data_path="data/metadata_syuhada.json", api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
        else:
            self.documents = []

        if self.documents:
            self.texts = [doc["text"] for doc in self.documents]
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
            self.doc_vectors = self.vectorizer.fit_transform(self.texts)
        else:
            self.texts = []
            self.vectorizer = None
            self.doc_vectors = None

    def retrieve(self, query: str, top_k: int = 4):
        if not self.documents or self.doc_vectors is None:
            return []
            
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.doc_vectors).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.01:
                results.append(self.documents[idx])
        
        query_upper = query.upper()
        exact_matches = [
            doc for doc in self.documents 
            if doc["metadata"]["element_id"].upper() in query_upper 
            or doc["metadata"]["drawing_code"].upper() in query_upper
        ]
        
        combined = exact_matches + [r for r in results if r not in exact_matches]
        return combined[:top_k]

    def generate_response(self, query: str, chat_history: list = None):
        if not self.client:
            return "⚠️ Gemini API Key belum dikonfigurasi. Silakan masukkan API Key di sidebar atau environment variable.", []

        retrieved_docs = self.retrieve(query, top_k=4)

        if not retrieved_docs:
            context_str = "Tidak ditemukan data spesifik pada dokumen metadata."
        else:
            context_str = "\n\n---\n\n".join([
                f"[KODE ELEMEN: {doc['metadata']['element_id']} | KODE GAMBAR: {doc['metadata']['drawing_code']}]\n"
                f"Judul: {doc['metadata']['title']}\n"
                f"Kategori: {doc['metadata']['category']} | Lokasi: {doc['metadata']['building_level']} ({doc['metadata']['room_code']})\n"
                f"Dimensi & Material: {doc['metadata']['dimensions']}, {doc['metadata']['materials']}\n"
                f"Deskripsi: {doc['text']}\n"
                f"Signifikansi: {doc['metadata']['significance']}\n"
                f"Kondisi: {doc['metadata']['condition']}\n"
                f"Rekomendasi Pemugaran: {doc['metadata']['preservation_policy']}\n"
                f"Sumber Dokumen: {doc['metadata']['source_doc']}"
                for doc in retrieved_docs
            ])

        system_instruction = """Anda adalah 'Syuhada-ArchBot', seorang Dokumentalis Senior dan Arsitek Preservasi Cagar Budaya yang menguasai metadata Dublin Core serta Pedoman Pelestarian Masjid Syuhada Yogyakarta.

Tugas Anda:
1. Menjawab pertanyaan pengguna terkait sejarah, arsitektur, kondisi fisik, kerusakan, dan rekomendasi pelestarian Masjid Syuhada secara presisi berdasarkan konteks terlampir.
2. Selalu gunakan konteks hasil retrieval metadata Dublin Core (DCMA) yang diberikan.
3. Cantumkan Kode Elemen (contoh: MSJ-ELE-J01), Kode Gambar (contoh: ED.VIII.01), dan Sitasi Sumber Dokumen (contoh: Dok 05 Hal. 74) pada setiap jawaban teknis.
4. Gunakan istilah arsitektur yang baku (seperti pointed arch, pilaster, flat slab, drop panel capital, rising damp, reversible repair).
5. Jika data tidak tersedia dalam konteks, jawab dengan jujur bahwa informasi tersebut tidak tercantum dalam dokumen inventarisasi metadata. Jangan mengarang informasi (halusinasi)."""

        prompt = f"KONTEKS DOKUMEN METADATA ARSITEKTUR:\n{context_str}\n\nPERTANYAAN PENGGUNA:\n{query}"

        try:
            response = self.client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                    top_p=0.95
                )
            )
            return response.text, retrieved_docs
        except Exception as e:
            return f"Terjadi kesalahan saat menghubungi API Gemini: {str(e)}", retrieved_docs
