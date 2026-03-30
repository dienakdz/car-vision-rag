# Kich Ban Series: Build Car Vision RAG Tu So 0 Den Hoan Chinh

## Ban chi tiet theo ham
Neu ban can ban co the "cam len doc de quay", mo file:
- `docs/kich_ban_quay_chi_tiet_theo_ham.md`

## 1) Muc tieu series
Muc tieu cua series la quay duoc hanh trinh xay dung project tu dau, den luc co app chay duoc voi day du:
- Upload anh xe.
- Detect + crop xe chinh.
- Classify body type.
- RAG truy hoi tri thuc tu PDF tren Qdrant local.
- Chat voi context tu anh vua upload + KB.
- Gemini sinh cau tra loi tieng Viet.
- UI co panel phan tich va panel chat.

## 2) Dinh dang quay de de dung lai
Ap dung cung 1 format cho moi bai:
1. Hook 20-40 giay: "Bai nay se build gi?"
2. Coding 60-80% thoi luong.
3. Test live tren terminal/browser.
4. Chot bai: recap + commit.

Moi bai nen co 1 commit rieng. Goi y naming:
- `lesson-01-init`
- `lesson-02-ui-upload`
- ...

## 3) Muc tieu dau ra sau series
Sau bai cuoi, ban co:
1. Mot project FastAPI full flow vision + RAG + chat.
2. Bo KB PDF tieng Viet cho showroom.
3. Script ingest/index KB tai local.
4. Kich ban demo va troubleshooting de quay video tong ket.

## 4) Lo trinh tong quan (roadmap nhanh)
1. Bai 1: Setup project va bo khung FastAPI.
2. Bai 2: UI co upload anh + preview.
3. Bai 3: API `/predict` va upload validation.
4. Bai 4: Detect xe voi YOLO.
5. Bai 5: Crop + classify body type.
6. Bai 6: Orchestrator `analyzer` va tra JSON thong nhat.
7. Bai 7: Structured KB va hien thi insight tren UI.
8. Bai 8: Tao/tien xu ly KB PDF.
9. Bai 9: Index Qdrant local + retriever.
10. Bai 10: Noi RAG vao luong `/predict`.
11. Bai 11: Chat API + session context.
12. Bai 12: Tich hop Gemini API.
13. Bai 13: Prompt tuning + anti-copy + fallback.
14. Bai 14: Nang cap UI chat va metadata.
15. Bai 15: Hardening, debug, clean up.
16. Bai 16: Demo cuoi + script quay video hoan chinh.

---

## Bai 1 - Setup project va bo khung FastAPI
### Muc tieu
Tao bo khung app chay duoc trang `/` va static files.

### Cong viec can lam
1. Tao virtual env va cai thu vien.
2. Tao cau truc thu muc:
   - `app/api`
   - `app/core`
   - `app/services`
   - `app/templates`
   - `app/static/css`
   - `app/static/js`
   - `data/kb/pdfs`
3. Tao `run.py` va `app/main.py`.
4. Mount `static` va `uploads`.

### Lenh demo
```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python run.py
```

### Loi dan quay video (goi y)
"Bai 1 minh khoi tao bo xuong song cua project. Muc tieu la co FastAPI app chay on dinh truoc khi them AI."

### Checkpoint
- Mo duoc `http://127.0.0.1:8888`.
- App boot khong loi.

### Commit goi y
`chore: bootstrap fastapi project structure`

---

## Bai 2 - UI upload anh va preview
### Muc tieu
Co trang frontend toi thieu de chon anh, preview, bam nut phan tich.

### Cong viec can lam
1. Tao `app/templates/index.html` co:
   - Form upload.
   - Khu vuc preview.
   - Khu vuc ket qua JSON.
2. Tao `app/static/css/style.css` cho layout 2 cot.
3. Tao `app/static/js/app.js` xu ly event chon file va preview.

### Lenh demo
```powershell
python run.py
```

### Loi dan quay video
"Muc tieu bai nay la tao khung UI de nhin thay toan bo ket qua theo thoi gian thuc. Chua can AI, uu tien luong thao tac."

### Checkpoint
- Chon file xong thay preview.
- UI responsive o desktop + mobile.

### Commit goi y
`feat: add upload ui with preview`

---

## Bai 3 - API /predict va upload validation
### Muc tieu
Nhan file an toan, validate dung dinh dang va gioi han size.

### Cong viec can lam
1. Tao `app/api/routes.py`:
   - `GET /` render `index.html`.
   - `POST /predict` nhan `UploadFile`.
2. Them validation:
   - extension (`jpg`, `jpeg`, `png`, `webp`)
   - max size file
3. Luu file vao `uploads/`.
4. Frontend `app.js` goi `/predict`.

### Lenh demo
```powershell
curl -X POST "http://127.0.0.1:8888/predict" -F "file=@uploads/test.jpg"
```

### Loi dan quay video
"Day la bai quan trong de tranh input xau ngay tu dau. Neu upload layer on, cac bai AI phia sau se de debug hon."

### Checkpoint
- File sai dinh dang bi chan.
- File qua lon bi chan.
- File hop le tra ve JSON.

### Commit goi y
`feat: implement predict upload endpoint with validation`

---

## Bai 4 - Detect xe voi YOLO
### Muc tieu
Tu anh upload, tim bounding box xe chinh.

### Cong viec can lam
1. Tao `app/services/detector.py`.
2. Load YOLO (`yolo11n.pt`).
3. Filter class car/truck/bus.
4. Chon object co diem tin cay cao nhat.
5. Tra payload detect:
   - `detected`
   - `main_car`
   - `all_detections`

### Lenh demo
```powershell
python run.py
```
Upload anh co xe va anh khong co xe de test 2 nhanh.

### Loi dan quay video
"Detect la gate dau tien cua pipeline vision. Neu detect fail thi dung som de tranh classify sai."

### Checkpoint
- Anh co xe: co bbox hop ly.
- Anh khong co xe: thong bao ro rang.

### Commit goi y
`feat: add yolo car detection service`

---

## Bai 5 - Crop anh xe + classify body type
### Muc tieu
Crop xe chinh tu bbox va classify body type (`sedan/suv/pickup/hatchback`).

### Cong viec can lam
1. Tao `app/utils/image.py` de crop.
2. Tao `app/services/classifier.py`:
   - load model classifier
   - transform anh
   - output top-k + confidence
3. Quan ly class labels (`models/classifier/body_type_classes.json`).

### Lenh demo
```powershell
python scripts/train_classifier.py
python run.py
```

### Loi dan quay video
"Pipeline vision se di theo thu tu detect -> crop -> classify. Crop giup classifier tap trung vao xe thay vi background."

### Checkpoint
- Co file crop trong `uploads/`.
- API tra `predicted_label`, `confidence`, `top_k`.

### Commit goi y
`feat: integrate crop and body type classifier`

---

## Bai 6 - Analyzer orchestration va JSON thong nhat
### Muc tieu
Dong goi toan bo vision flow vao `analyze_car_image`.

### Cong viec can lam
1. Tao `app/services/analyzer.py`:
   - detect
   - crop
   - classify
   - summary
2. Luu context prediction gan nhat (`session_store`).
3. Dinh nghia response schema thuc te cho frontend.

### Lenh demo
```powershell
python run.py
```

### Loi dan quay video
"Thay vi de routes.py qua tai, minh dung analyzer lam orchestration layer cho de bao tri."

### Checkpoint
- `/predict` tra ket qua gom detect + classify + summary.
- Frontend hien dung thong tin.

### Commit goi y
`refactor: add analyzer orchestration layer`

---

## Bai 7 - Structured KB cho body type
### Muc tieu
Tra them insight co cau truc, khong chi la nhan class.

### Cong viec can lam
1. Tao `app/services/structured_kb.py`.
2. Dinh nghia data cho tung body type:
   - characteristics
   - pros
   - cons
   - best_for
   - examples
3. Noi structured KB vao `analyzer.py`.
4. Render tren UI.

### Lenh demo
```powershell
python run.py
```

### Loi dan quay video
"Class label don le chua du de tu van. Structured KB giup co ngay bo y de user doc nhanh."

### Checkpoint
- Sau khi upload, panel insight hien danh sach uu/nhuoc diem ro rang.

### Commit goi y
`feat: add structured body type knowledge`

---

## Bai 8 - Xay bo du lieu KB PDF
### Muc tieu
Co KB PDF tieng Viet phu hop domain showroom.

### Cong viec can lam
1. Dat PDF vao `data/kb/pdfs`.
2. Neu chua co du, tao seed tai lieu bang:
   - `scripts/generate_seed_kb_pdfs.py`
3. Tien xu ly chunk:
   - `scripts/ingest_pdfs.py`
4. Tao `data/kb/pdf_chunks.json`.

### Lenh demo
```powershell
python scripts/generate_seed_kb_pdfs.py
python scripts/ingest_pdfs.py
```

### Loi dan quay video
"Chatbot RAG manh hay khong phu thuoc chat luong KB. Bai nay minh uu tien noi dung dung domain showroom."

### Checkpoint
- Co file `pdf_chunks.json`.
- Moi chunk co metadata: `source_file`, `kb_type`, `body_type`, `page`.

### Commit goi y
`feat: add kb pdf generation and chunking pipeline`

---

## Bai 9 - Index KB vao Qdrant local
### Muc tieu
Nhung chunks vao vector DB va truy hoi duoc.

### Cong viec can lam
1. Tao `scripts/index_pdf_chunks.py`.
2. Tao `app/services/qdrant_store.py`:
   - singleton qdrant client
   - set embedding model (`all-MiniLM-L6-v2`)
3. Tao collection `car_pdf_kb`.
4. Add documents + metadata + ids.

### Lenh demo
```powershell
python scripts/index_pdf_chunks.py
```

### Loi dan quay video
"Day la buoc bien du lieu PDF thanh tri nho truy van ngu nghia. Sau bai nay moi co RAG dung nghia."

### Checkpoint
- Index thanh cong va in tong so chunks.
- Khong gap lock file qdrant local.

### Loi thuong gap va cach xu ly
1. Loi `already accessed by another instance`.
   - Tat app dang chay roi index lai.
2. Van dinh du lieu cu.
   - Xoa collection roi re-index.

### Commit goi y
`feat: index pdf chunks into local qdrant`

---

## Bai 10 - Retriever va noi RAG vao /predict
### Muc tieu
Sau khi classify, truy hoi ngay tai lieu lien quan de tao `pdf.summary`.

### Cong viec can lam
1. Tao `app/services/retriever.py`:
   - `retrieve_pdf_knowledge`
   - filter theo `kb_type`, `body_type`
   - fallback khi khong co match strict
2. Noi retriever vao `analyzer.py`.
3. Tra `knowledge.pdf` trong response.

### Lenh demo
```powershell
python run.py
```
Upload nhieu anh body type khac nhau de so sanh nguon truy hoi.

### Loi dan quay video
"Tu bai nay, ket qua phan tich anh khong con la model-only, ma da co bo tri thuc bo sung tu KB PDF."

### Checkpoint
- `/predict` co `knowledge.pdf.summary`.
- `retrieved_docs` dung body type uu tien.

### Commit goi y
`feat: connect qdrant retriever to predict pipeline`

---

## Bai 11 - Chat API va session context
### Muc tieu
Co endpoint chat de hoi tiep ve anh vua upload.

### Cong viec can lam
1. Tao `app/api/chat_routes.py` (`POST /chat`).
2. Tao `app/services/chat.py`:
   - classify intent (`vehicle/company/general`)
   - lay last prediction tu `session_store`
   - retriever theo intent
3. Them fallback answer khi LLM chua co.

### Lenh demo
```powershell
curl -X POST "http://127.0.0.1:8888/chat" -H "Content-Type: application/json" -d "{\"message\":\"xe suv la gi\"}"
```

### Loi dan quay video
"Muc tieu la giu context lien tuc giua vision va chat: user upload 1 lan, sau do hoi tiep ma khong can lap lai."

### Checkpoint
- Chat tra ve `intent`, `sources`, `generation`.
- Co context body type gan nhat.

### Commit goi y
`feat: add contextual chat endpoint`

---

## Bai 12 - Tich hop Gemini API
### Muc tieu
Dung LLM de tao cau tra loi tu nhien tu context RAG.

### Cong viec can lam
1. Tao `.env.example` va `.env`.
2. Them config:
   - `LLM_API_BASE`
   - `LLM_API_KEY`
   - `LLM_MODEL=gemini-2.5-flash`
3. Tao `app/services/llm.py`:
   - build system/user prompt
   - call `generateContent`
   - parse text
   - metadata generation mode
4. Noi `chat.py` -> `generate_answer_with_rag`.

### Lenh demo
```powershell
python run.py
```
Sau do chat tren UI de xem answer from LLM.

### Loi dan quay video
"RAG phan retrieval chi tim tai lieu. Phan LLM moi la lop dien giai de bien context thanh cau tra loi co van phong tu nhien."

### Checkpoint
- `generation.mode = llm`.
- Meta co `model: gemini-2.5-flash`.

### Commit goi y
`feat: integrate gemini for rag answer generation`

---

## Bai 13 - Prompt tuning, anti-copy va fallback chat dep
### Muc tieu
Giam tinh trang copy nguyen chunk, tang chat luong ngon ngu.

### Cong viec can lam
1. Prompt style theo intent/cau hoi:
   - compact / standard / comparison / advisory
2. Them guardrails:
   - cam format dump `Tham khao [n]: ...`
   - phat hien copy context (ngram overlap)
   - paraphrase pass neu bi copy
3. Fallback khong dump raw text, chi de source refs + huong hoi tiep.
4. UI hien metadata:
   - `answer_style`
   - `refined`
   - `dequoted`

### Lenh demo
```powershell
python run.py
```
Test 3 cau:
1. "xe suv la gi"
2. "so sanh sedan va suv"
3. "tra loi ngan gon 2 cau"

### Loi dan quay video
"Prompt engineering la noi chat luong tra loi thay doi ro nhat. Muc tieu la de doc, dung y, khong copy paste chunk."

### Checkpoint
- Cau tra loi linh hoat theo style.
- Khong con hien khoi text dump.

### Loi thuong gap va cach xu ly
1. `gemini_http_error_429`.
   - Het quota free tier, doi cooldown hoac nang quota.
2. `llm_not_configured`.
   - Kiem tra `LLM_API_KEY` trong `.env`.

### Commit goi y
`feat: improve rag prompting with anti-copy and robust fallback`

---

## Bai 14 - Nang cap UI chat (de quay video dep hon)
### Muc tieu
UI co trai nghiem ro: status context, quick prompts, bong chat de doc.

### Cong viec can lam
1. Chia layout 2 panel:
   - Vision Analysis
   - Assistant Chat
2. Them chips goi y cau hoi nhanh.
3. Hien status context body type dang dung.
4. Hien metadata nho ben duoi message assistant.

### Lenh demo
```powershell
python run.py
```

### Loi dan quay video
"Bai nay khong them AI moi, nhung nang cap kha nang trinh bay. Video dep hon va nguoi xem de theo doi logic he thong."

### Checkpoint
- Chat panel scroll on.
- Message user/assistant tach bong ro rang.

### Commit goi y
`feat: redesign frontend with vision panel and chat panel`

---

## Bai 15 - Hardening va clean project cho ban quay cuoi
### Muc tieu
On dinh hoa he thong va bo sung huong xu ly su co thuong gap.

### Cong viec can lam
1. Dong qdrant client an toan khi app shutdown.
2. Viet section troubleshooting trong README:
   - qdrant lock
   - stale KB data
   - Gemini 429
3. Them script clear/reindex KB (neu can).
4. Tinh chinh env defaults:
   - `LLM_MAX_TOKENS`
   - `CHAT_RETRIEVAL_LIMIT`
   - `LLM_CONTEXT_CHARS`

### Lenh demo
```powershell
python scripts/ingest_pdfs.py
python scripts/index_pdf_chunks.py
python run.py
```

### Loi dan quay video
"Phan hardening la phan khien demo that bai hay thanh cong. Minh uu tien an toan va kha nang recover nhanh."

### Checkpoint
- Restart app nhieu lan khong crash qdrant.
- Re-index xong ket qua chat cap nhat dung KB moi.

### Commit goi y
`chore: harden runtime and add troubleshooting guide`

---

## Bai 16 - Demo tong ket va video final
### Muc tieu
Quay 1 video end-to-end tu upload anh den chat RAG.

### Kich ban quay de xuat (8-12 phut)
1. 0:00-0:40
   - Gioi thieu bai toan.
2. 0:40-2:00
   - Upload anh, xem detect + classify.
3. 2:00-3:30
   - Mo ket qua structured KB va PDF KB.
4. 3:30-6:00
   - Chat 3 tinh huong:
     - dinh nghia body type
     - so sanh
     - cau hoi policy showroom
5. 6:00-7:30
   - Show metadata generation mode.
6. 7:30-9:00
   - Cho thay script ingest/index nhanh.
7. 9:00-10:00
   - Noi bai hoc rut ra va huong mo rong.

### Cau hoi demo mau
1. "Xe vua upload la body type gi?"
2. "Sedan va SUV khac nhau nhu the nao cho gia dinh 4 nguoi?"
3. "Showroom co ho tro tra gop khong?"
4. "Cho toi checklist test drive."
5. "Tu van mua xe theo ngan sach tam trung."

### Checkpoint
- Toan bo luong chay muot.
- Khong co raw text dump dai dong.
- Video ket thuc bang roadmap mo rong.

### Commit goi y
`docs: add final demo script and walkthrough`

---

## 5) Checklist "Definition of Done" cho toan project
1. Upload anh hop le, xu ly duoc trong app.
2. Detect + crop + classify chay on.
3. Structured KB hien thi day du.
4. KB PDF duoc ingest va index vao Qdrant.
5. `/predict` co ket qua RAG.
6. `/chat` su dung context tu image + retriever.
7. Gemini response mode chay duoc khi con quota.
8. Fallback khong dump raw context.
9. UI co 2 panel (analysis/chat) de demo.
10. README co huong dan setup + troubleshooting.

## 6) Ke hoach quay de it loi
1. Truoc khi quay:
   - re-index KB
   - clear uploads cu neu can
   - test 3-5 cau chat mau
2. Trong luc quay:
   - mo san terminal 1 (server)
   - terminal 2 (scripts/commands)
   - browser voi tab Network mo san
3. Sau khi quay:
   - chen chapter theo bai
   - them link source code va commit theo lesson

## 7) Huong mo rong cho season 2
1. Multi-user session store (Redis).
2. Qdrant server mode (tranh local lock).
3. Eval set cho chat quality.
4. Logging/telemetry theo request id.
5. Deploy len cloud va ci/cd.

---

## 8) Script mo dau video (mau 45-60 giay)
"Series nay minh se build Car Vision RAG tu con so 0. Dau vao la 1 anh xe, dau ra la phan tich body type ket hop tri thuc showroom va chatbot tieng Viet. Minh chia theo tung bai nho: setup, vision, RAG, chat va hardening. Moi bai co code, test, commit ro rang de ban co the lam lai 1:1."

## 9) Script ket video (mau 30-45 giay)
"Den day chung ta da hoan thanh mot app vision + RAG + chat co the demo thuc te. Diem quan trong khong chi la model, ma la cach thiet ke pipeline, chat luong KB, va fallback khi he thong gap su co. O video tiep theo, minh co the mo rong sang multi-user, eval chat quality, va deploy production."
