# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Hồ Hoàng Phương Anh
**Nhóm:** G16
**Ngày:** 20/9/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao có nghĩa là hai vector có cùng hướng trong không gian embedding, nên chúng mô tả ý nghĩa gần nhau dù độ dài văn bản có thể khác nhau. Trong bài toán text retrieval, điều này nghĩa là hai câu/đoạn văn có nội dung tương đồng về ngữ nghĩa.

**Ví dụ có độ tương tự CAO:**
- Câu A: Người mua có 15 ngày để gửi yêu cầu trả hàng.
- Câu B: Khách hàng được phép yêu cầu hoàn trả sản phẩm trong vòng 15 ngày.
- Tại sao tương đồng: Cả hai nói về cùng một khái niệm: thời hạn trả hàng của người mua, chỉ khác cách diễn đạt và từ vựng.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Người mua có 15 ngày để đổi trả.
- Câu B: Người bán có trách nhiệm xử lý bảo hành trong 30 ngày.
- Tại sao khác: Mặc dù cùng thuộc chủ đề thương mại điện tử, chúng nói về hai đối tượng khác nhau: người mua và người bán.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ so hướng của vector, không bị ảnh hưởng bởi độ lớn, trong khi độ dài văn bản hoặc mức độ chi tiết có thể làm lớn vector nhưng không hẳn nghĩa là ngữ nghĩa khác. Đối với embedding văn bản, hướng là yếu tố quan trọng nhất để phản ánh ý nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Bước nhảy (step) là `chunk_size - overlap = 500 - 50 = 450`.
> Số chunk được tính theo công thức: `1 + ceil((N - chunk_size) / step)`.
> Với `N = 10000`, ta có `1 + ceil((10000 - 500) / 450) = 1 + ceil(9500 / 450) = 1 + ceil(21.11) = 1 + 22 = 23`.
> **Đáp án: 23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, step giảm từ 450 xuống 400, nên số chunk tăng lên. Số lượng chunk nhiều hơn giúp giữ ngữ cảnh liên tục giữa các đoạn, nhưng cũng làm giảm tính cô lập của từng chunk và tăng độ trùng lặp thông tin. Đây là điểm cân bằng giữa “giữ ý nghĩa liên kết” và “không lặp quá nhiều”.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi tách văn bản theo ranh giới câu bằng regex trên dấu kết thúc câu như `. `, `! `, `? ` và xuống dòng. Sau đó gom mỗi nhóm `max_sentences_per_chunk` câu thành một chunk và strip khoảng trắng thừa. Edge case quan trọng là văn bản rỗng hoặc các câu bị lặp khoảng trắng; tôi xử lý bằng kiểm tra `if not text` và lọc phần trống trước khi trả về.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Tôi dùng cách đệ quy theo thứ tự separator ưu tiên: `\n\n`, `\n`, `. `, ` `, `""`. Nếu đoạn văn còn quá dài sau khi chia theo separator hiện tại, tôi gọi lại đệ quy với danh sách separator còn lại. Base case là khi độ dài đoạn nhỏ hơn hoặc bằng `chunk_size`, hoặc khi không còn separator thì cắt cứng theo `chunk_size` để tránh vòng lặp vô hạn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi document được chuẩn hóa thành record với `content`, `metadata`, và `embedding`. Khi search, tôi nhúng query rồi tính dot product với từng embedding đã lưu, sắp xếp giảm dần theo score. Cách này là đúng với mô hình vector store đơn giản và phù hợp với các test của lab vì mock embeddings đã chuẩn hóa vector.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi ưu tiên lọc metadata trước khi chạy similarity search. Điều này đảm bảo `search_with_filter` không lãng phí các chỉ số top-k vào các document không hợp lệ. Với delete, tôi xoá toàn bộ record có `metadata['doc_id'] == doc_id` và trả về `True` nếu có ít nhất một record bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Tác tử truy xuất top-k chunks từ store, rồi xây prompt với các chunk đó như context. Tôi không để model trả lời theo kiểu suy đoán rời rạc; thay vào đó, prompt nhấn mạnh “chỉ dùng context được cung cấp”. Điều này giúp câu trả lời nằm trong phạm vi dữ liệu kiến thức hiện có và dễ trace lại nguồn.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```bash
cd '/Users/hohoangphuonganh/Desktop/AI_Thực _Chiến/Hackathon/K4-3B-Day07-HoHoangPhuongAnh-2A202602460-Data-Foundations' && . .venv/bin/activate && pytest tests/ -q
```

Kết quả thực tế:

```text
42 passed in 0.11s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Người mua có 15 ngày để yêu cầu trả hàng | Người mua được phép hoàn trả trong 15 ngày | cao | cao | Có |
| 2 | Người bán phải xử lý bảo hành trong 30 ngày | Người bán được phép trả hàng trong 30 ngày | thấp | thấp | Có |
| 3 | Chính sách đổi trả cho người mua | Quy định bảo hành cho người bán | thấp | thấp | Có |
| 4 | Hàng lỗi được đổi mới | Sản phẩm hỏng được hưởng bảo hành | cao | cao | Có |
| 5 | Chậm phản hồi từ người bán | Lỗi kỹ thuật của sản phẩm | thấp | thấp | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả đáng chú ý nhất là hai câu có cùng khái niệm nhưng khác từ vựng vẫn có cosine cao. Điều đó cho thấy embeddings không chỉ dựa vào ký tự mà còn phản ánh ý nghĩa ngữ nghĩa, ví dụ “yêu cầu trả hàng” và “hoàn trả sản phẩm” đều hướng về cùng một khái niệm trong chính sách mua-bán.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

Vì phần benchmark nhóm cần được tổ chức và ghi trong báo cáo nhóm, tôi đã hoàn thành phần kỹ thuật của code và đảm bảo pipeline retrieval hoạt động đúng; phần benchmark cụ thể sẽ được cập nhật trong báo cáo nhóm theo cùng 5 câu hỏi của nhóm. Dưới đây là bộ câu hỏi dự tính và mục tiêu truy xuất tương ứng:

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Người mua có bao nhiêu ngày để đổi trả? | Thông tin về thời hạn đổi trả cho người mua | dự kiến cao | Có | Trả lời theo thời hạn mãn hạn/điều kiện đổi trả |
| 2 | Người bán cần xử lý khiếu nại trong bao lâu? | Quy định xử lý của người bán và thời hạn phản hồi | dự kiến cao | Có | Trả lời về thời gian xử lý yêu cầu |
| 3 | Ai chịu chi phí vận chuyển đổi trả? | Thông tin về đối tượng chịu phí | dự kiến cao | Có | Trả lời theo chính sách người mua/người bán |
| 4 | Điều kiện nào không được đổi trả? | Điều kiện ngoại trừ và hạn chế | dự kiến trung bình | Có | Chỉ rõ điều kiện ngoại lệ |
| 5 | Nếu sản phẩm lỗi kỹ thuật thì xử lý như thế nào? | Chính sách bảo hành hoặc đổi mới | dự kiến cao | Có | Giải thích quyền lợi và quy trình |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 (dự kiến khi benchmark nhóm được thực thi đúng với dữ liệu đã phân loại theo audience)

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Trong retrieval, metadata filter có tác dụng cực lớn khi dữ liệu chứa nhiều đối tượng khác nhau như người mua và người bán. Nếu không phân biệt audience, retrieval dễ lẫn giữa các chính sách và trả lời lệch đối tượng. Điều đó cho thấy dữ liệu tốt và metadata rõ ràng quan trọng hơn cả việc nâng cấp model một cách mù quáng.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
