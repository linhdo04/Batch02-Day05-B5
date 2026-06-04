# Từ Evidence Đến Build Slice

## 1. Cụm evidence

Các cụm evidence chính cần được giữ lại:

- "Mất thời gian so sánh vé trên nhiều nền tảng"
- "Khó quyết nhanh vì phải tự cân giữa giá, giờ đi và điểm đón"
- "Điểm đón là yếu tố quyết định nhưng khó nhìn ra lựa chọn nào gần"
- "AI có thể hiểu sai địa danh hoặc tên nhà xe, dẫn đến chọn nhầm điểm đón"

## 2. Insight

Insight cốt lõi của nhóm:

```text
Người đi tỉnh định kỳ không chỉ cần danh sách vé liên tỉnh.
Họ thật ra cần một trợ lý giúp rút ngắn thời gian ra quyết định,
vì evidence cho thấy họ đang phải tự so giá, lọc giờ và kiểm tra điểm đón trên nhiều nền tảng.
```

Diễn giải ngắn gọn:

```text
User không thiếu lựa chọn vé.
Điều họ thiếu là hỗ trợ so sánh theo trade-off thật của chuyến đi,
vì một lựa chọn rẻ hơn chưa chắc tốt hơn nếu giờ đi lệch hoặc điểm đón quá xa.
```

## 3. Opportunity

Opportunity phù hợp với evidence hiện có:

```text
Cơ hội là dùng AI để augment việc xếp hạng top 3 vé theo giá, giờ đi và độ gần điểm đón,
giúp user ra quyết định nhanh hơn,
trong khi vẫn kiểm soát rủi ro nhập nhằng địa danh/nhà xe bằng bước xác nhận.
```

## 4. Chọn build slice

Build slice được chọn cần trả lời rõ 5 câu hỏi sau:

| Câu hỏi               | Đạt khi                                                                                       |
| --------------------- | --------------------------------------------------------------------------------------------- |
| User cụ thể chưa?     | Có: người đi tỉnh định kỳ đang cần chọn vé liên tỉnh nhanh và an tâm hơn.                     |
| Task đủ hẹp chưa?     | Có: demo một flow AI gợi ý top 3 vé thay vì build toàn bộ assistant đặt vé.                   |
| AI decision rõ chưa?  | Có: AI xếp hạng vé theo giá, giờ đi và điểm đón gần.                                          |
| Failure path rõ chưa? | Có: test case AI nhầm địa danh như "Giáo xứ Thanh Phong" với "Nhà xe Thanh Phong".            |
| Có evidence không?    | Có: đã có self-use, phỏng vấn nhanh, demo lỗi và pattern từ Vexere, MoMo Travel, Google Maps. |

## 5. Quyết định: giữ, giảm scope, hay đổi hướng?

Quyết định hiện tại của nhóm:

| Tình huống                   | Quyết định                                                                                   |
| ---------------------------- | -------------------------------------------------------------------------------------------- |
| Evidence đã chỉ ra pain rõ   | Giữ domain vé xe liên tỉnh và tiếp tục build sâu vào flow so sánh/gợi ý.                     |
| Ý tưởng ban đầu quá rộng     | Cắt từ assistant đặt vé rộng xuống flow gợi ý top 3 vé.                                      |
| AI nên đóng vai trò gì       | Chọn augmentation: AI gợi ý, xếp hạng và cảnh báo rủi ro thay vì tự đặt vé end-to-end.       |
| Rủi ro cao                   | Buộc user xác nhận khi hệ thống phát hiện nhập nhằng điểm đón hoặc tên nhà xe.               |
| Không demo được trong 1 ngày | Đưa payment thật, booking thật và dữ liệu live vào backlog; giữ mock data và deep-link demo. |

## 6. Câu chốt cuối

Tuyên bố chốt để cả nhóm dùng thống nhất:

```text
Dựa trên evidence từ self-use, phỏng vấn nhanh, demo lỗi NER và competitor review,
nhóm sẽ build flow AI gợi ý top 3 vé xe liên tỉnh cho người đi tỉnh định kỳ.
Mục tiêu là giảm thời gian so sánh giá, giờ đi và điểm đón.
AI sẽ đóng vai trò augmentation trong việc xếp hạng và cảnh báo các case nhập nhằng,
đồng thời nhóm sẽ test failure path khi AI chọn nhầm địa danh hoặc điểm đón.
```

## 7. Backlog

Những phần **không build trong Day 06**:

- Tích hợp thanh toán hoặc booking thật trong app
- Đồng bộ dữ liệu vé live từ nhà xe hoặc nền tảng đối tác
- Mở rộng xử lý NER/địa chỉ vượt ngoài các case demo trọng điểm
