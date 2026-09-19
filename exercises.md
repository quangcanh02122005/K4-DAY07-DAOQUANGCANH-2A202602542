# Ngày 7 — Bài tập
## Nền tảng Dữ liệu: Embedding & Vector Store | Bài tập thực hành

---

## Phần 1 — Khởi động (Cá nhân)

### Bài tập 1.1 — Cosine Similarity (Độ tương tự Cosine) bằng ngôn ngữ đời thường

Không yêu cầu toán học — hãy giải thích về mặt khái niệm:

- Điều gì xảy ra khi hai đoạn văn bản có độ tương tự cosine cao?
- Đưa ra một ví dụ cụ thể về hai câu sẽ có độ tương tự CAO và hai câu sẽ có độ tương tự THẤP.
- Tại sao độ tương tự cosine lại được ưu tiên hơn khoảng cách Euclid (Euclidean distance) đối với text embeddings?

> **Ghi kết quả vào:** Báo cáo — Phần 1 (Khởi động)

---

### Bài tập 1.2 — Bài toán tính toán Chunking

- Một tài liệu có độ dài 10,000 ký tự. Bạn tiến hành chia nhỏ (chunk) với `chunk_size=500` (kích thước chunk), `overlap=50` (độ chồng chéo). Bạn dự kiến sẽ có bao nhiêu chunks?
- Công thức: `số lượng chunk = làm_tròn_lên((độ_dài_tài_liệu - độ_chồng_chéo) / (kích_thước_chunk - độ_chồng_chéo))`
- Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk sẽ thay đổi như thế nào? Tại sao bạn lại muốn tăng độ chồng chéo?

> **Ghi kết quả vào:** Báo cáo — Phần 1 (Khởi động)

---

## Phần 2 — Lập trình cốt lõi (Cá nhân)

Hoàn thành tất cả các TODOs trong `src/chunking.py`, `src/store.py`, và `src/agent.py`. `Document` dataclass và `FixedSizeChunker` đã được triển khai sẵn làm ví dụ — hãy đọc kỹ để hiểu cấu trúc trước khi lập trình phần còn lại.

Chạy `pytest tests/` để kiểm tra tiến độ.

### Danh sách cần làm (Checklist)
- [x] `Document` dataclass — ĐÃ TRIỂN KHAI SẴN
- [x] `FixedSizeChunker` — ĐÃ TRIỂN KHAI SẴN
- [x] `SentenceChunker` — tách dựa trên ranh giới câu, nhóm lại thành các chunks
- [x] `RecursiveChunker` — thử nghiệm các dấu phân cách (separators) theo thứ tự, thực hiện đệ quy trên các đoạn có kích thước quá lớn
- [x] `compute_similarity` — công thức tính độ tương tự cosine kèm cơ chế bảo vệ chia cho 0
- [x] `ChunkingStrategyComparator` — gọi cả ba chiến lược, tính toán các chỉ số thống kê
- [x] `EmbeddingStore.__init__` — khởi tạo store trong bộ nhớ
- [x] `EmbeddingStore.add_documents` — nhúng (embed) và lưu trữ từng tài liệu
- [x] `EmbeddingStore.search` — nhúng truy vấn, xếp hạng theo tích vô hướng (dot product)
- [x] `EmbeddingStore.get_collection_size` — trả về số lượng
- [x] `EmbeddingStore.search_with_filter` — lọc theo siêu dữ liệu (metadata), sau đó tìm kiếm
- [x] `EmbeddingStore.delete_document` — xóa tất cả các chunks của một doc_id
- [x] `KnowledgeBaseAgent.answer` — truy xuất (retrieve) + tạo prompt + gọi LLM

> **Nộp code:** thư mục `src/`
> **Ghi lại hướng tiếp cận vào:** Báo cáo — Phần 4 (Hướng tiếp cận của tôi)

---

## Phần 3 — So Sánh Chiến Lược Truy Xuất (Nhóm)

### Bài tập 3.0 — Chuẩn Bị Tài Liệu (Giờ đầu tiên)

Mỗi nhóm chọn một chủ đề (domain) và chuẩn bị bộ tài liệu:

**Bước 1 — Chọn chủ đề:** FAQ (Câu hỏi thường gặp), SOP (Quy trình chuẩn), chính sách, tài liệu kỹ thuật, công thức nấu ăn, luật, y tế, v.v.

**Bước 2 — Thu thập 5-10 tài liệu.** Chỉ dùng nguồn công khai hoặc nguồn nhóm có quyền sử dụng; lưu dưới dạng `.txt` hoặc `.md` vào thư mục `data/`.

**Quy tắc dữ liệu bắt buộc:**
- Không đưa dữ liệu cá nhân, thông tin đăng nhập, hồ sơ nội bộ hoặc nội dung có quyền sử dụng không rõ ràng vào repo.
- Với mỗi tài liệu, ghi `source_url`, `retrieved_at` (ngày lấy) và `document_version` hoặc ngày hiệu lực nếu nguồn có nêu.
- Đưa ba trường trên vào siêu dữ liệu (metadata) khi nạp (ingest); chúng giúp kiểm tra độ mới và truy vết câu trả lời.

> **Mẹo chuyển PDF sang Markdown:**
> - `pip install marker-pdf` → `marker_single input.pdf output/` (chất lượng cao, giữ cấu trúc)
> - `pip install pymupdf4llm` → `pymupdf4llm.to_markdown("input.pdf")` (nhanh, đơn giản)
> - Hoặc sao chép-dán (copy-paste) nội dung từ PDF/web vào file `.txt`

Ghi vào bảng:

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Nội quy Thư viện Đại học Ngoại thương | https://hcmc.ftu.edu.vn/thu-vien/tin-tuc-thu-vien/noi-quy-thu-vien/ | 19/09/2026 / 10/08/2026 | 4.218 | `audience=all`, `category=rules`, `language=vi` |
| 2 | Nội quy Thư viện Đại học Công nghiệp Hà Nội | https://lib.haui.edu.vn/opac80/ChinhSach.aspx | 19/09/2026 / `not-stated` | 7.832 | `audience=all`, `category=policy`, `language=vi` |
| 3 | Quy định sử dụng Thư viện HUIT | https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien | 19/09/2026 / `not-stated` | 13.345 | `audience=all`, `category=policy`, `language=vi` |
| 4 | Mượn trả tài liệu VNUA | https://infolib.vnua.edu.vn/dich-vu/muon-tra-tai-lieu | 19/09/2026 / `not-stated` | 1.457 | `audience=all`, `category=borrowing`, `language=vi` |
| 5 | Dịch vụ sử dụng phòng họp nhóm HUST | https://library.hust.edu.vn/vi/node/1362 | 19/09/2026 / `not-stated` | 1.717 | `audience=student`, `category=facility`, `language=vi` |
| 6 | Mượn trả tài liệu đọc tại chỗ HUST | https://library.hust.edu.vn/vi/node/1300 | 19/09/2026 / `not-stated` | 1.761 | `audience=student`, `category=circulation`, `language=vi` |
| 7 | Quy trình làm thẻ thư viện cho cán bộ HUST | https://library.hust.edu.vn/vi/node/1034 | 19/09/2026 / `not-stated` | 1.298 | `audience=faculty`, `category=service`, `language=vi` |
| 8 | Quy định làm thẻ bạn đọc HUST | https://library.hust.edu.vn/vi/node/305 | 19/09/2026 / `not-stated` | 1.479 | `audience=student`, `category=service`, `language=vi` |
| 9 | Thủ tục thanh toán ra trường tại thư viện HUST | https://library.hust.edu.vn/vi/node/61 | 19/09/2026 / `not-stated` | 2.344 | `audience=student`, `category=graduation`, `language=vi` |
| 10 | Quy định phòng đọc tự chọn HUST | https://library.hust.edu.vn/vi/node/57 | 19/09/2026 / `not-stated` | 2.160 | `audience=all`, `category=facility`, `language=vi` |

**Bước 3 — Thiết kế cấu trúc metadata (metadata schema):** Mỗi tài liệu cần `source_url`, `retrieved_at`, `document_version` và ít nhất 2 trường hữu ích cho việc truy xuất (ví dụ: `audience`, `department`, `category`, `language`, `difficulty`).

> **Ghi kết quả vào:** Báo cáo — Phần 2 (Lựa chọn tài liệu)

---

### Bài tập 3.1 — Thiết Kế Chiến Lược Truy Xuất (Mỗi người thử riêng)

Mỗi thành viên **tự chọn chiến lược riêng** để thử nghiệm trên cùng bộ tài liệu của nhóm.

**Bước 1 — Đường cơ sở (Baseline):** Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu. Ghi lại kết quả.

**Bước 2 — Chọn hoặc thiết kế chiến lược của bạn:**
- Dùng 1 trong 3 chiến lược có sẵn (built-in strategies) với tham số tối ưu, HOẶC
- Thiết kế chiến lược tùy chỉnh cho chủ đề của bạn (ví dụ: chia nhỏ theo cặp Câu hỏi-Đáp án, theo các phần (sections), theo tiêu đề (headers))
- Mỗi thành viên nên thử một chiến lược **khác nhau** để có cơ sở so sánh

```python
class CustomChunker:
    """Chiến lược chia nhỏ tùy chỉnh cho [chủ đề của bạn].

    Lý do thiết kế: [giải thích tại sao chiến lược này phù hợp với dữ liệu của bạn]
    """

    def chunk(self, text: str) -> list[str]:
        # Viết mã nguồn của bạn ở đây
        ...
```

**Bước 3 — So sánh:** So sánh chiến lược tùy chỉnh/được tinh chỉnh (custom/tuned strategy) với đường cơ sở (baseline) trên cùng tài liệu.

| Thành viên | Chiến lược | Cấu hình | Số chunk | Điểm benchmark |
|---|---|---|---:|---:|
| Đinh Quang Lâm (02875) | Fixed-size | `chunk_size=500`, `overlap=50` | 80 | 1/10 |
| Đào Quang Cảnh (02542) | Recursive | `chunk_size=500` | 87 | 1/10 |
| Hoàng Công Minh (02774) | Heading + recursive fallback | `chunk_size=500` | 137 | 2/10 |

Heading chunking đạt điểm cao nhất trong lần chạy bằng `MockEmbedder` vì giữ nguyên mục chứa yêu cầu ảnh làm thẻ và đưa đáp án Q3 lên top-1. Tuy nhiên mock embedding không hiểu ngữ nghĩa, nên kết quả chỉ dùng để minh họa luồng benchmark và tác động của cấu trúc chunk.

> **Ghi kết quả vào:** Báo cáo — Phần 3 (Chiến lược chia nhỏ - Chunking Strategy)

---

### Bài tập 3.2 — Chuẩn Bị Câu Hỏi Đánh Giá (Benchmark Queries)

Mỗi nhóm viết **đúng 5 câu hỏi đánh giá** kèm theo **câu trả lời chuẩn (gold answers)**.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Theo HUST, đến nhận phòng học nhóm muộn quá bao lâu thì lịch đặt phòng bị hủy? | Muộn quá 15 phút thì thư viện có quyền hủy lịch và cấp phòng cho nhóm khác. | `dich-vu-su-dung-phong-hop-nhom` — mục “3. Thực hiện” |
| 2 | Khi mượn tài liệu đọc tại chỗ ở HUST, mỗi lần được lấy tối đa bao nhiêu quyển và phải trả ở đâu, lúc nào? | Tối đa 2 quyển/lần; trả trước 17h30 tại phòng 411. | `muon-tra-tai-lieu-inhouse` — “Quy trình mượn/trả” |
| 3 | Ảnh làm thẻ thư viện cho cán bộ HUST phải đáp ứng yêu cầu gì? | Ảnh tối thiểu 300 pixel, tỷ lệ 1x1, nền trắng và gửi tới `tttts@hust.edu.vn`. | `quy-trinh-lam-the-can-bo` — mục “2. Thủ tục và địa điểm đăng ký” |
| 4 | Theo HaUI, sinh viên được mượn tối đa bao nhiêu tài liệu và trong thời gian bao lâu? | Tối đa 5 tài liệu/lần; tài liệu tham khảo 15 ngày, giáo trình một học kỳ. | `haui-library-policy` — Điều 5 |
| 5 | Tôi cần làm gì để hoàn tất thủ tục công nợ tại thư viện? | Kiểm tra tài khoản/email, trả sách và xử lý vi phạm, kiểm tra lại tài khoản rồi đề nghị khóa tài khoản. | `thu-tuc-thanh-toan-ra-truong`; lọc `audience=student` |

**Yêu cầu:**
- Câu hỏi phải đa dạng (không hỏi 5 câu có nội dung/cấu trúc giống hệt nhau)
- Câu trả lời chuẩn phải cụ thể và có thể kiểm chứng (verify) từ tài liệu
- Ít nhất 1 câu hỏi yêu cầu lọc bằng metadata (metadata filtering) để trả lời tốt

> **Ghi kết quả vào:** Báo cáo — Phần 6 (Kết quả — Câu hỏi đánh giá & Câu trả lời chuẩn)

---

### Bài tập 3.3 — Dự Đoán Độ Tương Tự Cosine (Cá nhân)

Gọi hàm `compute_similarity()` trên 5 cặp câu. **Trước khi chạy**, hãy dự đoán xem cặp câu nào sẽ có độ tương tự cao nhất/thấp nhất. Ghi lại các dự đoán của bạn và kết quả thực tế. Suy ngẫm xem điều gì khiến bạn ngạc nhiên nhất.

> **Ghi kết quả vào:** Báo cáo — Phần 5 (Dự đoán độ tương tự)

---

### Bài tập 3.4 — Chạy Đánh Giá & So Sánh Trong Nhóm

**Bước 1:** Mỗi thành viên chạy 5 câu hỏi đánh giá với chiến lược riêng. Ghi lại kết quả top-3 cho mỗi câu hỏi.

**Bước 2:** So sánh kết quả trong nhóm:
- Chiến lược nào cho việc truy xuất tốt nhất? Tại sao?
- Có câu hỏi nào mà chiến lược A tốt hơn B nhưng lại ngược lại ở câu hỏi khác không?
- Lọc bằng metadata (Metadata filtering) có giúp ích không?

**Bước 3:** Thảo luận và rút ra bài học — chuẩn bị cho phần demo (thuyết trình) với các nhóm khác.

| Chiến lược | Q1 | Q2 | Q3 | Q4 | Q5 | Tổng |
|---|---:|---:|---:|---:|---:|---:|
| Fixed-size | 0 | 0 | 1 | 0 | 0 | 1/10 |
| Recursive | 0 | 0 | 1 | 0 | 0 | 1/10 |
| Heading | 0 | 0 | 2 | 0 | 0 | 2/10 |

**A/B metadata filter:** Với Q5, khi không lọc, top-3 chứa tài liệu `all` và `faculty` không đúng đối tượng. Khi dùng `metadata_filter={"audience": "student"}`, các tài liệu sai đối tượng bị loại trước similarity search; tuy vậy top-3 vẫn chưa chứa đáp án vì `MockEmbedder` không mã hóa ngữ nghĩa.

> **Ghi kết quả vào:** Báo cáo — Phần 6 (Kết quả)
> **Gợi ý đánh giá:** xem danh sách kiểm tra ngắn trong `README.md` mục **Cách Tự Đánh Giá Kết Quả Retrieval** hoặc chi tiết hơn trong file `docs/EVALUATION.md`.

---

### Bài tập 3.5 — Phân Tích Lỗi (Failure Analysis)

Tìm ít nhất **1 trường hợp lỗi (failure case)** trong quá trình so sánh. Mô tả:
- Câu hỏi nào mà quá trình truy xuất gặp thất bại?
- Tại sao? (do chunk quá nhỏ/quá lớn, thiếu metadata, câu hỏi mơ hồ, v.v.)
- Đề xuất cải thiện?

**Failure case đã quan sát:** Q2 trả đúng `doc_id=muon-tra-tai-lieu-inhouse` ở top-1 nhưng chunk chỉ chứa bước nhận tài liệu, không chứa “tối đa 2 quyển” hay “trả trước 17h30 tại phòng 411”. Nếu chỉ chấm theo `doc_id`, kết quả sẽ bị đánh giá sai là thành công.

**Nguyên nhân:** HeadingChunker tách từng `Bước` thành chunk riêng, trong khi gold answer cần thông tin từ cả quy trình mượn và trả; mock embedding cũng không ưu tiên được chunk chứa số liệu.

**Cải thiện:** Gom các bước thuộc cùng quy trình vào một section, thêm overlap hoặc parent heading, dùng embedding đa ngôn ngữ thật và bổ sung keyword/BM25 cho con số, thời gian và số phòng.

> **Ghi kết quả vào:** Báo cáo — Phần 7 (Những gì tôi học được)
> **Gợi ý:** phân tích lỗi nên tham chiếu từ các góc nhìn như độ chính xác (precision), tính mạch lạc của chunk (chunk coherence), tính hữu dụng của metadata, và chất lượng thông tin nền (grounding quality).

---

## Danh Sách Kiểm Tra Nộp Bài (Submission Checklist)

- [x] Vượt qua tất cả các bài kiểm thử (tests): `pytest tests/ -v` — 42/42 passed
- [x] Cập nhật thư mục `src/` (cá nhân)
- [x] Hoàn thành báo cáo nhóm (`report/REPORT_NHOM.md` — 1 file/nhóm)
- [x] Hoàn thành báo cáo cá nhân (`report/REPORT_CANHAN.md` — 1 file/sinh viên)
