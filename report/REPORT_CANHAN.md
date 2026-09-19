# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đào Quang Cảnh
**Nhóm:** G19
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Cosine similarity cao nghĩa là hai vector embedding hướng gần giống nhau, nên hai đoạn văn bản được mô hình biểu diễn là gần nhau về mặt ngữ nghĩa. Giá trị gần `1` biểu thị tương đồng cao, gần `0` biểu thị ít liên quan, còn gần `-1` biểu thị hướng đối nghịch.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên có thể gia hạn sách đang mượn.
- Câu B: Người học được phép kéo dài thời hạn sử dụng tài liệu thư viện.
- Tại sao tương đồng: Hai câu dùng từ vựng khác nhau nhưng cùng diễn đạt việc sinh viên kéo dài thời gian mượn tài liệu.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Thư viện mở cửa lúc tám giờ sáng.
- Câu B: Mạng nơ-ron được huấn luyện bằng thuật toán lan truyền ngược.
- Tại sao khác: Hai câu thuộc hai chủ đề và mục đích hoàn toàn khác nhau: giờ phục vụ thư viện và kỹ thuật học máy.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine tập trung vào hướng của vector, tức mẫu đặc trưng ngữ nghĩa, và ít bị ảnh hưởng bởi độ lớn vector do độ dài văn bản. Khoảng cách Euclid còn chịu tác động của độ lớn nên hai văn bản cùng nghĩa nhưng có độ dài hoặc chuẩn vector khác nhau có thể bị xem là xa nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: `ceil((10.000 - 50) / (500 - 50)) = ceil(9.950 / 450) = ceil(22,111...) = 23`.
> Đáp án: **23 chunks**. Kết quả kiểm tra bằng `FixedSizeChunker` cũng trả về `23`.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100: `ceil((10.000 - 100) / (500 - 100)) = ceil(9.900 / 400) = 25`, tức tăng từ 23 lên **25 chunks**; kết quả thực chạy cũng là 25. Overlap lớn hơn giúp giữ ngữ cảnh và thông tin nằm sát ranh giới giữa hai chunk, đổi lại làm tăng dữ liệu trùng lặp, số embedding và chi phí lưu trữ/truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex lookbehind `(?<=[.!?])(?:[ \t]+|\n+)` để tách tại khoảng trắng hoặc xuống dòng nằm sau dấu kết câu, nhờ đó dấu câu vẫn được giữ lại. Các câu được `strip`, loại phần rỗng rồi gom theo `max_sentences_per_chunk`; văn bản rỗng trả về `[]`. Cách đơn giản này chưa nhận biết chữ viết tắt như `TS.`, `v.v.` hoặc dấu chấm trong số thập phân nên có thể cắt sai các trường hợp đó.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử separator theo thứ tự `\n\n`, `\n`, `. `, khoảng trắng rồi chuỗi rỗng; mảnh vượt `chunk_size` tiếp tục được chia bằng separator ưu tiên thấp hơn. Sau khi chia sâu, các mảnh nhỏ liền kề được gom lại đến sát giới hạn để tránh tạo nhiều chunk vụn. Ba base case là văn bản rỗng, văn bản đã không vượt kích thước, và hết separator/đến separator rỗng thì cắt cứng theo số ký tự.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Store chỉ dùng bộ nhớ: `add_documents` tạo một record cho mỗi `Document`, sao chép metadata, bổ sung `doc_id` nếu thiếu và tính embedding đúng một lần khi nạp. `search` embedding câu hỏi rồi dùng `_search_records` tính dot product với từng record, sắp xếp điểm giảm dần và trả tối đa `top_k`; embedding không được đưa vào kết quả để output gọn.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc toàn bộ record có metadata khớp tất cả điều kiện trước, sau đó mới gọi chung `_search_records`; cách này không để tài liệu sai metadata chiếm các vị trí top-k. `delete_document` loại tất cả record có `metadata['doc_id']` bằng ID tài liệu cần xóa, vì một tài liệu gốc có thể tạo nhiều chunk, rồi trả `True` khi kích thước store thực sự giảm.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent truy xuất top-k, đánh số từng chunk `[1]`, `[2]`, `[3]` và kèm `source_url`, `source` hoặc `doc_id` để câu trả lời có thể truy vết. Prompt yêu cầu chỉ sử dụng ngữ cảnh, trích dẫn số nguồn và nói rõ khi thiếu thông tin nhằm hạn chế bịa đặt. Nếu store không trả kết quả, agent trả thông báo ngay và không gọi `llm_fn`.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1
rootdir: D:\Vinuni\day7\K4-L3A-Data-Foundations
collected 42 items

tests/test_solution.py ..........................................       [100%]

============================= 42 passed in 0.09s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên có thể gia hạn sách. | Người học được kéo dài thời hạn mượn tài liệu. | Cao | 0,0284 | Không |
| 2 | Thư viện mở cửa lúc tám giờ. | Mạng nơ-ron học từ dữ liệu. | Thấp | 0,0669 | Có (điểm gần 0) |
| 3 | Mượn sách tại thư viện. | Vay tài liệu ở trung tâm học liệu. | Cao | 0,0033 | Không |
| 4 | Quy định sử dụng phòng học nhóm. | Hướng dẫn đặt phòng thảo luận. | Cao | -0,0871 | Không |
| 5 | Cán bộ cần làm thẻ thư viện. | Sinh viên phải trả sách trước khi tốt nghiệp. | Thấp | -0,1541 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là các cặp đồng nghĩa ở câu 1, 3 và 4 đều có điểm gần 0 hoặc âm. Nguyên nhân là `MockEmbedder` tạo vector từ MD5 chứ không học ngữ nghĩa; vì vậy các điểm này chỉ kiểm tra luồng tính toán, không thể dùng để đánh giá khả năng hiểu nghĩa của embedding thật.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Nhận phòng nhóm muộn quá bao lâu? | Quy định HaUI về hoàn trả tài liệu trước khi rời trường | 0,3280 | Không | Không đủ ngữ cảnh để trả lời thời hạn 15 phút. |
| 2 | Mượn in-house tối đa bao nhiêu và trả ở đâu/lúc nào? | Đúng tài liệu HUST nhưng chỉ chứa bước nhận tài liệu, không có số lượng/giờ trả | 0,2843 | Không | Không đủ chi tiết để trả lời đầy đủ gold answer. |
| 3 | Yêu cầu ảnh làm thẻ cho cán bộ HUST? | Mục thủ tục làm thẻ, chứa yêu cầu 300 pixel, tỷ lệ 1x1, nền trắng | 0,0959 | Có | Có thể trả lời đúng từ chunk top-1 và trích nguồn. |
| 4 | Sinh viên HaUI được mượn bao nhiêu và bao lâu? | Bước nhận thẻ điện tử của HUST | 0,3262 | Không | Không đủ ngữ cảnh để trả lời quy định HaUI. |
| 5 | Hoàn tất thủ tục công nợ thư viện? | Bước xuất trình thẻ sinh viên khi mượn in-house | 0,1476 | Không | Không đủ ngữ cảnh để trả lời thủ tục ra trường. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 1 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Kết quả cho thấy cần kiểm tra nội dung chunk thay vì chỉ kiểm tra tài liệu gốc: Q2 có đúng `doc_id` ở top-1 nhưng vẫn không chứa đáp án. So sánh chiến lược cũng chỉ có ý nghĩa khi giữ nguyên corpus, query, top-k và embedding backend; nếu thay nhiều biến cùng lúc thì không thể biết cải thiện đến từ đâu.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 2 / 10 |
| **Tổng phần cá nhân** | **52 / 60** |
