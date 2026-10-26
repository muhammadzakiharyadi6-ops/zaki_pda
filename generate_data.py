import json
import openpyxl

def build_json_database(excel_path="Metadata_DublinCore_RAG_Masjid_Syuhada.xlsx", output_json="data/metadata_syuhada.json"):
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

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    
    print(f"Berhasil mengkonversi {len(records)} data elemen ke {output_json}")

if __name__ == "__main__":
    build_json_database()
