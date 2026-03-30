# Kich Ban Quay Chi Tiet Theo Ham (Doc La Quay Duoc)

## 0) Cach dung tai lieu nay
1. Moi bai co 6 phan co dinh:
   - Muc tieu bai.
   - File va ham can tao/sua.
   - Vi sao tao tung ham.
   - Ham lam gi (input/output + luong goi).
   - Loi dan de doc khi quay (teleprompter).
   - Test ngay sau bai.
2. Ban co the quay theo dung thu tu Bai 1 -> Bai 16.
3. Moi bai ket thuc bang 1 commit rieng.

---

## Bai 1 - Khoi tao bo khung project

### Muc tieu
Co app FastAPI chay duoc, mount static va uploads, san sang cho cac bai AI.

### File va ham
1. `run.py`
   - entrypoint chay uvicorn.
2. `app/main.py`
   - `app_lifespan(_: FastAPI)`.

### Vi sao tao cac ham nay
1. `run.py` can thiet de start app nhanh, de quay video khong can command dai.
2. `app_lifespan` can de quan ly tai nguyen runtime (sau nay dong Qdrant client an toan).

### Ham lam gi
1. `app_lifespan`
   - Input: FastAPI app (khong dung truc tiep).
   - Output: khong tra du lieu, chi quan ly startup/shutdown.
   - Luong goi: FastAPI tu dong goi khi app bat/tat.
   - Gia tri: tranh leak resource sau nhieu lan reload.

### Teleprompter
"Bai 1 minh chi lam xong khung. Dieu quan trong la app phai co lifecycle ro rang de ve sau them AI ma khong vo cau truc. Minh tao `app_lifespan` ngay tu dau de quan ly tai nguyen he thong, dac biet la vector DB client."

### Test
```powershell
python run.py
```
Mo `http://127.0.0.1:8888`.

### Commit
`chore: bootstrap fastapi app with lifecycle`

---

## Bai 2 - Tao UI upload va preview

### Muc tieu
Co giao dien cho user chon anh, xem preview, va cho ket qua API.

### File va ham
1. `app/templates/index.html`
2. `app/static/css/style.css`
3. `app/static/js/app.js`
   - `formatConfidence`
   - preview listener cho `fileInput`

### Vi sao tao cac ham nay
1. `formatConfidence`: chuan hoa cach hien thi `%`, tranh lap logic o nhieu cho.
2. preview listener: user biet da chon dung anh truoc khi gui len server.

### Ham lam gi
1. `formatConfidence(value)`
   - Input: so thap phan 0..1.
   - Output: chuoi `%` da lam tron 2 chu so.
2. `fileInput.addEventListener("change", ...)`
   - Input: file moi nguoi dung chon.
   - Output: cap nhat anh preview trong UI.
   - Luong goi: trigger khi user doi file.

### Teleprompter
"Truoc khi nhay vao model, minh uu tien UX co ban. Ham preview giup user xac nhan input, con `formatConfidence` giup output on dinh ngay tu dau."

### Test
1. Chon file anh.
2. Kiem tra preview da hien.

### Commit
`feat: add upload ui and image preview`

---

## Bai 3 - Xay API `/predict` va validation upload

### Muc tieu
Nhan file an toan: dung loai file, dung kich thuoc, luu file co id duy nhat.

### File va ham
1. `app/api/routes.py`
   - `_validate_upload_size(file: UploadFile) -> None`
   - `home(request: Request)`
   - `predict(file: UploadFile = File(...))`

### Vi sao tao cac ham nay
1. `_validate_upload_size`: tach rule business ra khoi endpoint de de test, de doc.
2. `predict`: la gateway cua luong phan tich.
3. dat file bang UUID: tranh trung ten va ghi de.

### Ham lam gi
1. `_validate_upload_size`
   - Input: UploadFile.
   - Output: khong tra gi; throw HTTPException neu vuot nguong.
2. `predict`
   - Input: file upload.
   - Output: JSON `{success, filename, result}`.
   - Luong goi:
     - check ext.
     - check size.
     - luu file vao `uploads/`.
     - goi `analyze_car_image` (threadpool).

### Teleprompter
"Ham `predict` khong nen lam tat ca moi thu. Minh tach validation thanh `_validate_upload_size` de endpoint gon va ro. Day la pattern dung lai duoc cho cac API upload khac."

### Test
1. Upload file txt -> phai bao loi type.
2. Upload file qua lon -> phai bao loi size.
3. Upload file hop le -> tra JSON.

### Commit
`feat: implement predict endpoint with upload guards`

---

## Bai 4 - Detect xe voi YOLO

### Muc tieu
Tu anh upload, tim danh sach xe va chon xe chinh.

### File va ham
1. `app/services/detector.py`
   - `detect_car(image_path: str) -> dict`

### Vi sao tao ham nay
1. Detect la gate dau pipeline.
2. Neu khong detect duoc xe thi dung som, tranh classify sai du lieu.
3. Tra danh sach `cars` + `main_car` de UI va debug de xem model thay gi.

### Ham lam gi
1. `detect_car`
   - Input: duong dan anh.
   - Output:
     - `detected`
     - `total_cars`
     - `main_car` (bbox lon nhat)
     - `cars` (tat ca xe detect duoc)
   - Logic:
     - chay YOLO.
     - loc class `car`.
     - tinh `area` bbox.
     - sort giam dan theo area.

### Teleprompter
"Tai sao chon xe co `area` lon nhat lam `main_car`? Vi trong anh thuc te, xe can phan tich thuong la chu the chinh. Cach nay don gian, de hieu, va du on cho demo."

### Test
Upload anh co 1 xe va anh co nhieu xe.

### Commit
`feat: add yolo car detection and main object selection`

---

## Bai 5 - Crop xe va classify body type

### Muc tieu
Tap trung classifier vao vung xe chinh va tra top-k body type.

### File va ham
1. `app/utils/image.py`
   - `crop_image(image_path, bbox, output_path) -> dict`
2. `app/services/classifier.py`
   - `load_classifier()`
   - `build_confidence_message(confidence: float) -> str`
   - `classify_body_type(crop_image_path: str) -> dict`

### Vi sao tao cac ham nay
1. `crop_image`: tach utility anh ra khoi analyzer.
2. `load_classifier`: lazy-load + cache model, tranh load lai moi request.
3. `build_confidence_message`: dong nhat thong diep cho UI.
4. `classify_body_type`: ham nghiep vu chinh cho phan loai.

### Ham lam gi
1. `crop_image`
   - Input: anh goc + bbox.
   - Output: metadata anh crop (`crop_path`, size, `bbox_used`).
   - Co clamp bbox vao kich thuoc anh de tranh loi out-of-bound.
2. `load_classifier`
   - Input: khong.
   - Output: `(model, class_names)` hoac `(None, None)` neu chua co model.
3. `classify_body_type`
   - Input: path anh crop.
   - Output:
     - `predicted_label`
     - `confidence`
     - `top_k`
     - `is_uncertain`
     - `message`

### Teleprompter
"Minh bo sung `top_k` vi trong bai toan nhan dang body type, 1 nhan duy nhat doi khi chua du. Top-k giup minh va user hieu do bat dinh cua model."

### Test
1. Co model: tra confidence + top_k.
2. Chua co model: tra message fallback ro rang.

### Commit
`feat: add car crop utility and body type classifier`

---

## Bai 6 - Analyzer orchestration

### Muc tieu
Dong goi full pipeline detect -> crop -> classify -> knowledge trong 1 service.

### File va ham
1. `app/services/analyzer.py`
   - `build_analysis_summary(classification_result: dict) -> str`
   - `analyze_car_image(image_path: str) -> dict`

### Vi sao tao cac ham nay
1. `build_analysis_summary`: tach text summary theo confidence threshold.
2. `analyze_car_image`: orchestration trung tam, giup route don gian.

### Ham lam gi
1. `build_analysis_summary`
   - Input: ket qua classifier.
   - Output: 1 cau tong ket de user doc nhanh.
2. `analyze_car_image`
   - Input: path anh upload.
   - Output: payload day du:
     - detection
     - crop
     - classification
     - knowledge (structured + pdf)
     - summary
   - Luong goi:
     - detect fail -> tra nhanh.
     - detect pass -> crop -> classify -> knowledge.
     - ghi `last_prediction` vao session memory.

### Teleprompter
"Analyzer la diem hop nhat tat ca service. Kien truc nay giup endpoint `/predict` chi con vai dong, de test va de maintain."

### Test
Upload 1 anh khong co xe, 1 anh co xe.

### Commit
`refactor: add analyzer orchestration service`

---

## Bai 7 - Structured KB cho body type

### Muc tieu
Tra insight co cau truc cho tung body type (uu/nhuoc, best-for, vi du).

### File va ham
1. `app/services/structured_kb.py`
   - `_load_structured_kb() -> list[dict]`
   - `get_structured_body_type_knowledge(label: str | None)`
2. `data/kb/cars.json`

### Vi sao tao cac ham nay
1. `_load_structured_kb` co `@lru_cache` de tranh doc file moi request.
2. `get_structured_body_type_knowledge` de map tu nhan classifier sang tri thuc co cau truc.

### Ham lam gi
1. `_load_structured_kb`
   - Input: khong.
   - Output: list knowledge items.
   - Co xu ly loi file khong ton tai / JSON loi.
2. `get_structured_body_type_knowledge`
   - Input: label (`sedan`, `suv`...).
   - Output: item knowledge phu hop hoac `None`.

### Teleprompter
"Day la lop tri thuc de app trinh bay duoc ngay ca khi RAG chua manh. Structured KB luon la fallback huu ich."

### Test
Kiem tra UI hien danh sach `characteristics`, `pros`, `cons`.

### Commit
`feat: add structured knowledge lookup by body type`

---

## Bai 8 - Tao va ingest KB PDF

### Muc tieu
Chuyen PDF thanh chunks co metadata de san sang index vector.

### File va ham
1. `scripts/generate_seed_kb_pdfs.py` (tao bo tai lieu mau tieng Viet)
2. `scripts/ingest_pdfs.py`
   - `clean_text`
   - `chunk_text`
   - `extract_pdf_text`
   - `infer_body_type_from_text`
   - `detect_section_type`
   - `main`

### Vi sao tao cac ham nay
1. `clean_text`: giam noise OCR/layout.
2. `chunk_text`: chia doan vua cho retrieval.
3. `extract_pdf_text`: tach text theo trang.
4. `infer_body_type_from_text`: fallback gan nhan body type khi metadata file thieu.
5. `detect_section_type`: bo sung metadata de filter sau nay.

### Ham lam gi
1. `chunk_text(text, chunk_size=800, overlap=150)`
   - Input: text dai.
   - Output: list chunks co overlap.
   - Ly do overlap: tranh mat context o ranh gioi chunk.
2. `main`
   - Duyet tat ca PDF trong `data/kb/pdfs`.
   - Build payload metadata tung chunk.
   - Ghi ra `data/kb/pdf_chunks.json`.

### Teleprompter
"Chat luong RAG phu thuoc rat manh vao chunking. Minh dung overlap de giu mach cau, tranh truong hop y chinh nam dung ngay diem cat chunk."

### Test
```powershell
python scripts/generate_seed_kb_pdfs.py
python scripts/ingest_pdfs.py
```
Mo `data/kb/pdf_chunks.json` kiem tra.

### Commit
`feat: add pdf seed generation and chunk ingest pipeline`

---

## Bai 9 - Index Qdrant local

### Muc tieu
Nhet chunks vao vector DB de truy van semantic.

### File va ham
1. `scripts/index_pdf_chunks.py`
   - `load_chunks()`
   - `main()`
2. `app/services/qdrant_store.py`
   - `get_qdrant_client()`
   - `close_qdrant_client()`

### Vi sao tao cac ham nay
1. `get_qdrant_client`: singleton, tranh mo nhieu instance gay lock local storage.
2. `close_qdrant_client`: dong ket noi khi app tat.
3. Script index tach rieng khoi runtime app de deployment de quan ly.

### Ham lam gi
1. `load_chunks`
   - Input: file `pdf_chunks.json`.
   - Output: list chunk records.
2. `main` (index script)
   - Tao client Qdrant local.
   - Set embedding model.
   - Xoa collection cu neu co.
   - Add documents + metadata + ids.
3. `get_qdrant_client`
   - Tao client 1 lan, tai su dung cho retriever.

### Teleprompter
"Voi Qdrant local, loi hay gap la lock folder khi co 2 process cung mo. Minh giai quyet bang singleton trong app va script index chay rieng."

### Test
```powershell
python scripts/index_pdf_chunks.py
```

### Commit
`feat: add qdrant local store and indexing script`

---

## Bai 10 - Retriever va noi RAG vao predict

### Muc tieu
Sau classify, truy hoi ngay context PDF lien quan.

### File va ham
1. `app/services/retriever.py`
   - `_format_hits`
   - `_safe_limit`
   - `_query_context`
   - `build_query_from_classification`
   - `_build_vehicle_filter`
   - `retrieve_vehicle_context`
   - `retrieve_company_context`
   - `retrieve_pdf_knowledge`
2. `app/services/analyzer.py` (goi `retrieve_pdf_knowledge`)

### Vi sao tao cac ham nay
1. `_format_hits`: chuan hoa ket qua Qdrant thanh schema on dinh.
2. `_safe_limit`: chan limit qua cao.
3. `_build_vehicle_filter`: giam duplicate logic filter.
4. `retrieve_vehicle_context`: tim strict theo body type truoc, fail moi fallback.
5. `retrieve_company_context`: phuc vu chat policy/showroom.
6. `build_query_from_classification`: dua top-k vao query de retrieval linh hoat hon.

### Ham lam gi
1. `retrieve_pdf_knowledge`
   - Input: label + top_k.
   - Output:
     - query da dung
     - summary (chunk dau)
     - retrieved_docs
2. `retrieve_vehicle_context`
   - Input: body_type + query.
   - Output: docs da loc theo `kb_type=vehicle_template`.

### Teleprompter
"Retriever la phan quyet dinh RAG co dung ngu canh hay khong. Minh dung chien luoc 2 tang: strict filter truoc, fallback sau."

### Test
Upload anh sedan va suv, so sanh `source_file` tra ve.

### Commit
`feat: add retriever and connect pdf rag to predict`

---

## Bai 11 - Chat endpoint + session context

### Muc tieu
User hoi tiep sau khi upload ma khong can lap lai ngup canh.

### File va ham
1. `app/services/session_store.py`
   - `set_last_prediction`
   - `get_last_prediction`
2. `app/api/chat_routes.py`
   - `chat(req: ChatRequest)`
3. `app/services/chat.py`
   - `classify_chat_intent`
   - `_build_fallback_answer`
   - `chat_with_context`

### Vi sao tao cac ham nay
1. `session_store`: luu ngu canh image gan nhat (single-user local).
2. `classify_chat_intent`: chia query theo nhom de truy hoi dung kho tri thuc.
3. `_build_fallback_answer`: dam bao app van tra loi duoc khi LLM fail.
4. `chat_with_context`: orchestration cho chat luong.

### Ham lam gi
1. `chat_with_context`
   - Input: message text.
   - Output:
     - `intent`
     - `answer`
     - `sources`
     - `generation`
   - Luong:
     - lam sach message.
     - lay `last_prediction`.
     - chon retriever theo intent.
     - goi LLM.
     - fallback neu can.

### Teleprompter
"Tai bai nay minh chua doi multi-user. Session memory trong RAM la du cho self project va quay demo nhanh."

### Test
1. Upload anh.
2. Chat: "xe vua upload la gi?"

### Commit
`feat: add chat api with session context`

---

## Bai 12 - Tich hop Gemini cho generate answer

### Muc tieu
Dung model ngon ngu de dien giai context RAG thanh cau tra loi tu nhien.

### File va ham
1. `.env.example`, `.env`
2. `app/core/config.py` (LLM env vars)
3. `app/services/llm.py`
   - `_build_prediction_context`
   - `_build_source_context`
   - `_build_prompts`
   - `_send_json`
   - `_extract_gemini_text`
   - `generate_answer_with_rag`

### Vi sao tao cac ham nay
1. Tach prompt builder va HTTP sender de de test.
2. `_extract_gemini_text` de absorb format response cua Gemini.
3. `generate_answer_with_rag` la API noi bo duy nhat de `chat.py` goi.

### Ham lam gi
1. `_build_source_context`
   - Input: docs retriever.
   - Output: context co citation index `[1], [2]`.
2. `_send_json`
   - Input: url + payload.
   - Output: `(data, err_meta)`.
   - Co bat `HTTPError` va tra `reason` dung.
3. `generate_answer_with_rag`
   - Input: message + prediction + docs + intent.
   - Output: `(answer_or_none, generation_meta)`.

### Teleprompter
"RAG khong phai chi retrieval. Lop LLM moi bien cac doan context thanh cau tra loi co van phong, co cau truc, va de doc cho nguoi dung."

### Test
Kiem tra response chat co:
- `generation.mode = llm`
- `generation.model = gemini-2.5-flash`

### Commit
`feat: integrate gemini llm for rag answer generation`

---

## Bai 13 - Prompt tuning de tra loi dai hon va linh hoat hon

### Muc tieu
Giam cau tra loi cuc ngan, them style theo loai cau hoi.

### File va ham
1. `app/services/llm.py`
   - `_classify_answer_style`
   - `_build_style_instruction`
   - `_should_expand_answer`
   - `_build_expand_payload`
   - `_enrich_if_still_short`

### Vi sao tao cac ham nay
1. `_classify_answer_style`: cung mot model nhung can output khac nhau cho "so sanh", "tu van", "ngan gon".
2. `_should_expand_answer`: neu answer qua ngan thi chay pass viet lai.
3. `_enrich_if_still_short`: them follow-up question de mo rong hoi dap.

### Ham lam gi
1. `_classify_answer_style(message)`
   - Output: `compact/comparison/advisory/standard`.
2. `_build_expand_payload(...)`
   - Tao prompt "viet lai day du hon" cho pass 2.
3. `_enrich_if_still_short(...)`
   - Noi them:
     - body type confidence (neu co)
     - source refs
     - cau hoi tiep theo intent.

### Teleprompter
"Prompt tuning o day khong phai viet cho dep, ma la dat quy tac output de chat phan ung dung ngu canh nguoi dung."

### Test
1. "Tra loi ngan gon 2 cau"
2. "So sanh sedan va suv"
3. "Tu van mua xe cho gia dinh 4 nguoi"

### Commit
`feat: add style-based prompting and answer expansion`

---

## Bai 14 - Anti-copy context va fallback dep

### Muc tieu
Khong de model copy nguyen van chunk tu KB.

### File va ham
1. `app/services/llm.py`
   - `_normalize_whitespace`
   - `_ascii_fold`
   - `_tokenize_words`
   - `_contains_context_copy`
   - `_strip_reference_dump`
   - `_build_paraphrase_payload`
2. `app/services/chat.py`
   - cap nhat `_build_fallback_answer` (khong dump raw doc text)

### Vi sao tao cac ham nay
1. `_contains_context_copy`: phat hien overlap theo n-gram.
2. `_build_paraphrase_payload`: buoc model viet lai tu nhien khi bi copy.
3. `_strip_reference_dump`: xoa dinh dang xau kieu `Tham khao [1]: ...`.
4. fallback moi: du LLM loi van lich su, khong vo UX.

### Ham lam gi
1. `_contains_context_copy(answer, docs, ngram_words=11)`
   - Output: `True/False`.
2. `_build_paraphrase_payload(...)`
   - Prompt cho pass "dequoted".
3. `_build_fallback_answer(...)`
   - Tra answer tong quat + source refs + goi y hoi lai.

### Teleprompter
"Neu khong co lop anti-copy, chatbot se trong nhu dang dan lai tai lieu. Muc tieu cua bai nay la giu tinh xac thuc cua RAG, nhung van co ngon ngu tu nhien."

### Test
Hoi: "xe suv la xe gi?" va kiem tra khong con doan dump dai.

### Commit
`feat: add anti-copy pipeline and cleaner fallback response`

---

## Bai 15 - Nang cap UI chat de demo dep va de debug

### Muc tieu
UI chat co typing state, metadata generation, quick prompts.

### File va ham
1. `app/static/js/app.js`
   - `setList`
   - `setChatStatus`
   - `scrollChatToBottom`
   - `appendMessage`
   - `syncAnalysisToUI`
   - `sendChatMessage`
2. `app/templates/index.html`, `app/static/css/style.css`

### Vi sao tao cac ham nay
1. `appendMessage`: 1 diem duy nhat ve render bong chat.
2. `syncAnalysisToUI`: map response JSON -> UI widgets.
3. `sendChatMessage`: xu ly async call + error + metadata.

### Ham lam gi
1. `sendChatMessage(message)`
   - Goi `/chat`.
   - Hien typing placeholder.
   - append assistant message + meta (`intent`, `sources`, `gen`, `model`, `style`, `refined`, `dequoted`).
2. `syncAnalysisToUI(result)`
   - Cap nhat anh goc, anh crop, label, confidence, knowledge lists.

### Teleprompter
"Frontend nay khong chi de dep. No la cong cu debug truc tiep, vi meta generation cho minh biet dang di nhanh LLM hay fallback."

### Test
1. Upload anh -> chat status cap nhat theo label.
2. Gui message -> thay meta phia duoi assistant.

### Commit
`feat: improve chat ui with generation metadata and context status`

---

## Bai 16 - Hardening, doc troubleshooting, demo final

### Muc tieu
Chot project o trang thai quay demo on dinh, xu ly duoc loi hay gap.

### File va ham
1. `app/services/qdrant_store.py`
   - xac nhan `atexit.register(close_qdrant_client)`.
2. `README.md`
   - section setup + troubleshooting.
3. scripts ingest/index.

### Vi sao can buoc nay
1. Khi quay video, loi runtime thuong den tu env/quota/lock.
2. Co troubleshooting script se giup ban xu ly tai cho, khong cat video.

### Checklist truoc khi bam quay final
1. Chay lai ingest + index:
```powershell
python scripts/ingest_pdfs.py
python scripts/index_pdf_chunks.py
```
2. Bat app:
```powershell
python run.py
```
3. Test nhanh:
   - 1 anh sedan
   - 1 cau hoi vehicle
   - 1 cau hoi company

### Teleprompter
"Bai cuoi khong them tinh nang moi. Muc tieu la bien project thanh mot san pham demo on dinh, co cach xu ly su co ro rang, va co the quay mot mach."

### Commit
`chore: harden runtime and finalize demo documentation`

---

## Phu luc A - Script doc khi code (mau ngan theo tung bai)

### Mau doc cho moi bai (ban copy dung format nay)
1. "Muc tieu bai nay la ..."
2. "Minh tao ham ... vi ..."
3. "Input cua ham la ..., output la ..."
4. "Ham nay duoc goi o dau trong flow ..."
5. "Minh test ngay bang cach ..."
6. "Neu co loi ..., huong xu ly la ..."

### Vi du mau cho Bai 10 (Retriever)
"Trong bai nay minh tao `_build_vehicle_filter` de tranh lap logic filter. Input cua ham la `body_type` va co `strict_body_type`. Output la `models.Filter` cho Qdrant. Ham nay duoc goi boi `retrieve_vehicle_context`, dau tien tim strict theo body type, neu khong co ket qua thi fallback sang vehicle template chung."

---

## Phu luc B - Thu tu quay 1 video full 10-12 phut
1. 00:00-00:40 Gioi thieu bai toan.
2. 00:40-02:00 Upload anh, show detect + classify.
3. 02:00-03:30 Show structured KB + PDF summary.
4. 03:30-06:00 Chat vehicle va company.
5. 06:00-07:30 Show metadata generation.
6. 07:30-08:30 Neu Gemini 429, show fallback dep.
7. 08:30-10:30 Show ingest/index scripts.
8. 10:30-12:00 Tong ket kien truc va huong mo rong.

---

## Phu luc C - Cau tra loi nhanh cho comment nguoi xem
1. "Tai sao dung Qdrant local?"
   - "De setup nhanh cho local demo. Production nen dung Qdrant server."
2. "Tai sao khong goi thang LLM ma can RAG?"
   - "Viec trich nguon noi bo showroom can tinh chinh xac va truy vet, RAG giai quyet phan nay."
3. "Tai sao co fallback?"
   - "De he thong khong chet im khi LLM quota loi hoac key loi."
4. "Tai sao can anti-copy?"
   - "De chatbot khong trong nhu copy tai lieu, van dung ngu canh nhung dien giai tu nhien."

---

## Phu luc D - Danh sach command dung lai khi quay
```powershell
# setup
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt

# run app
python run.py

# generate kb pdf (neu can)
python scripts/generate_seed_kb_pdfs.py

# ingest + index kb
python scripts/ingest_pdfs.py
python scripts/index_pdf_chunks.py
```

---

## Chot
Neu ban muon quay theo "series tung bai", dung file nay lam teleprompter.
Neu ban muon quay "1 video full", dung Phu luc B + D.
