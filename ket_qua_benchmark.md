# Kết quả benchmark (R2) — Lab 7

Đây là kết quả benchmark chạy trên corpus trong data/ecommerce/ (6 tài liệu). Script: `bench.py` (chunk_size=400, top_k=3). Output đã được lưu ở `ket_qua_benchmark.txt` và `ket_qua_benchmark.csv`.

## Tóm tắt
- Indexed chunks: 20
- Chunk size: 400
- Top-K: 3

---

## Query 1
Query: Người bán TikTok Shop phải xem xét yêu cầu trả hàng/hoàn tiền của người mua trong bao lâu? Nếu không xử lý đúng hạn thì điều gì xảy ra?
Filter: {'platform': 'tiktok_shop', 'audience': 'seller', 'category': 'return_refund'}

Top-1: tiktok-shop-return-refund-seller#chunk4 — score=0.0676
Excerpt: - Người bán nhận được yêu cầu từ người mua. - Người bán kiểm tra và xử lý trong thời gian quy định. - Yêu cầu được tiếp tục nếu người mua gửi hàng trả đúng hạn. - Nếu không xử lý đúng hạn hoặc [...]

Top-2: tiktok-shop-return-refund-seller#chunk2 — score=0.0650
Excerpt: # Chính sách trả hàng/hoàn tiền cho người bán trên TikTok Shop ## Thời hạn xem xét yêu cầu Người bán phải xem xét yêu cầu trong vòng 1 ngày theo lịch kể từ khi nhận được yêu cầu. Nếu người bán [...]

Top-3: tiktok-shop-return-refund-seller#chunk3 — score=-0.0052
Excerpt: Sau khi yêu cầu trả hàng được phê duyệt, người mua có 10 ngày theo lịch để vận chuyển sản phẩm trả hàng. Nếu không gửi trong thời hạn này, yêu cầu sẽ bị đóng và không thực hiện hoàn tiền. ## Quy [...]

---

## Query 2
Query: Sau khi yêu cầu trả hàng trên TikTok Shop được phê duyệt, người mua có bao nhiêu thời gian để gửi sản phẩm? Điều gì xảy ra nếu gửi trễ?
Filter: {'platform': 'tiktok_shop', 'audience': 'seller', 'category': 'return_refund'}

Top-1: tiktok-shop-return-refund-seller#chunk4 — score=0.1293
Top-2: tiktok-shop-refund-proposal-seller#chunk3 — score=0.0732
Top-3: tiktok-shop-return-refund-seller#chunk1 — score=0.0152

---

## Query 3
Query: Trên TikTok Shop, hoàn tiền toàn bộ khác hoàn tiền một phần ở điểm nào đối với khả năng người mua gửi yêu cầu hậu mãi tiếp theo?
Filter: {'platform': 'tiktok_shop', 'audience': 'seller', 'category': 'return_refund'}

Top-1: tiktok-shop-return-refund-seller#chunk3 — score=0.2112
Top-2: tiktok-shop-refund-proposal-seller#chunk1 — score=0.0687
Top-3: tiktok-shop-refund-proposal-seller#chunk3 — score=-0.0023

---

## Query 4
Query: Người bán trên Shopee có trách nhiệm gì về bảo hành, và người mua cần đáp ứng những điều kiện cơ bản nào để được bảo hành?
Filter: {'platform': 'shopee', 'audience': 'both', 'category': 'warranty'}

Top-1: shopee-warranty-policy-both#chunk3 — score=0.0988
Top-2: shopee-warranty-policy-both#chunk1 — score=0.0105
Top-3: shopee-warranty-policy-both#chunk2 — score=-0.0622

---

## Query 5
Query: Khi người mua gửi yêu cầu trả hàng/hoàn tiền trên Shopee, yêu cầu thường được xử lý trong bao lâu và tiền được hoàn trong bao lâu nếu yêu cầu được chấp nhận?
Filter: {'platform': 'shopee', 'audience': 'buyer', 'category': 'return_refund'}

Top-1: shopee-return-refund-guide-buyer#chunk3 — score=0.1956
Top-2: shopee-return-refund-guide-buyer#chunk1 — score=0.0577
Top-3: shopee-return-refund-guide-buyer#chunk2 — score=0.0489

---

> Ghi chú: excerpts được rút gọn khi cần. Kết quả sử dụng MockEmbedder (deterministic) nên có thể lặp lại khi chạy trên cùng môi trường ảo.
