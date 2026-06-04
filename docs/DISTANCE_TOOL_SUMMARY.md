# Google Maps Distance Tool - Tóm tắt triển khai

## ✅ Đã hoàn thành

Tôi đã tạo một hệ thống tính khoảng cách hoàn chỉnh cho SmartBus với các tính năng sau:

### 1. **Tools chính đã tạo** (`backend/app/agent/tools.py`)

#### `calculate_distance_google_maps()`
- Tính khoảng cách và thời gian di chuyển giữa 2 tọa độ
- Hỗ trợ Google Maps Distance Matrix API
- Tự động fallback về Haversine nếu không có API key
- Trả về: khoảng cách (km), thời gian, link Google Maps dẫn đường

#### `find_nearest_pickup_point()`
- Tìm điểm đón gần nhất từ danh sách các điểm
- So sánh khoảng cách của tất cả điểm với vị trí user
- Trả về điểm gần nhất kèm thông tin chi tiết và link dẫn đường

#### `build_directions_link()`
- Tạo link Google Maps để dẫn đường từ A đến B
- Có thể gửi cho user để mở trong Maps app

#### `_haversine_distance()`
- Tính khoảng cách đường chim bay (fallback method)
- Không cần API key, hoạt động offline

### 2. **File tài liệu và ví dụ**

✅ **`docs/google-maps-integration.md`** - Hướng dẫn đầy đủ:
- Cách cài đặt và cấu hình API key
- Hướng dẫn sử dụng từng function
- 4 use cases tích hợp với agent
- Best practices và troubleshooting

✅ **`backend/app/agent/distance_example.py`** - 4 ví dụ chạy được:
- Ví dụ 1: Tính khoảng cách cơ bản
- Ví dụ 2: Tìm điểm đón gần nhất
- Ví dụ 3: Tích hợp với hệ thống vé
- Ví dụ 4: Tạo link dẫn đường

### 3. **Tests** (`backend/tests/test_agent.py`)

Đã thêm 7 test cases mới:
- ✅ `test_calculate_distance_haversine` - Kiểm tra tính khoảng cách với Haversine
- ✅ `test_build_directions_link` - Kiểm tra tạo link dẫn đường
- ✅ `test_find_nearest_pickup_point` - Kiểm tra tìm điểm đón gần nhất
- ✅ `test_find_nearest_pickup_point_empty` - Test edge case
- ✅ `test_haversine_distance` - Test công thức Haversine
- ✅ `test_distance_integration_with_search` - Test tích hợp với tìm vé

Tất cả tests đều **PASS** ✅

### 4. **Dependencies đã cài**

Đã thêm vào `requirements.txt`:
- `requests>=2.31,<3` - Để gọi Google Maps API
- `python-dotenv>=1.0,<2` - Để load API key từ .env

## 🎯 Use Cases chính

### Use Case 1: Tính khoảng cách từ user đến điểm đón

```python
from backend.app.agent.tools import calculate_distance_google_maps

result = calculate_distance_google_maps(
    origin_lat=21.0369,  # Vị trí user
    origin_lng=105.7897,
    dest_lat=21.0285,    # Điểm đón
    dest_lng=105.7803,
)

print(f"Khoảng cách: {result['distance_text']}")
print(f"Thời gian: {result['duration_text']}")
print(f"Dẫn đường: {result['maps_link']}")
```

### Use Case 2: Agent gợi ý điểm đón gần nhất

```python
from backend.app.agent.tools import find_nearest_pickup_point

pickup_points = [
    {"name": "Bến xe Mỹ Đình", "address": "...", "lat": 21.0285, "lng": 105.7803},
    {"name": "Cầu Giấy Office", "address": "...", "lat": 21.0333, "lng": 105.7947},
]

result = find_nearest_pickup_point(
    user_lat=21.0369,
    user_lng=105.7897,
    pickup_points=pickup_points,
)

nearest = result["nearest_point"]
print(f"Điểm gần nhất: {nearest['name']} - {nearest['distance_text']}")
print(f"Link dẫn đường: {nearest['maps_link']}")
```

### Use Case 3: Tích hợp vào Gemini Agent

Agent có thể gọi tool này để trả lời câu hỏi như:
- "Điểm đón nào gần tôi nhất?"
- "Bến xe Mỹ Đình cách tôi bao xa?"
- "Làm sao để đến điểm đón?"

```python
def calculate_pickup_distance_tool(
    user_lat: float,
    user_lng: float,
    pickup_lat: float,
    pickup_lng: float,
) -> str:
    """Tool cho Gemini Agent"""
    result = calculate_distance_google_maps(
        origin_lat=user_lat,
        origin_lng=user_lng,
        dest_lat=pickup_lat,
        dest_lng=pickup_lng,
    )
    
    return (
        f"Điểm đón cách bạn {result['distance_text']}, "
        f"mất khoảng {result['duration_text']}. "
        f"Xem đường đi: {result['maps_link']}"
    )

# Thêm vào tools của agent
tools = [
    search_and_format_tickets,
    resolve_pickup_ambiguity_tool,
    calculate_pickup_distance_tool,  # ← Tool mới
]
```

## 🚀 Cách sử dụng

### Bước 1: Chạy ví dụ (không cần API key)

```bash
python -m backend.app.agent.distance_example
```

Tool sẽ tự động dùng Haversine fallback nếu không có API key.

### Bước 2 (Tùy chọn): Thêm Google Maps API Key

1. Lấy API key từ [Google Cloud Console](https://console.cloud.google.com/)
2. Enable "Distance Matrix API"
3. Tạo file `.env`:

```bash
GOOGLE_MAPS_API_KEY=your_api_key_here
```

4. Chạy lại ví dụ để thấy kết quả chính xác hơn với thời gian di chuyển

### Bước 3: Chạy tests

```bash
python -m pytest backend/tests/test_agent.py -v
```

## 📊 So sánh: Với vs Không có API Key

| Tính năng | Có API Key | Không có API Key |
|-----------|------------|------------------|
| Khoảng cách | ✅ Theo đường đi thực tế | ⚠️ Đường chim bay (Haversine) |
| Thời gian di chuyển | ✅ Có | ❌ Không |
| Link Google Maps | ✅ Có | ✅ Có |
| Độ chính xác | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**Kết luận:** Tool vẫn hoạt động tốt không cần API key, nhưng có API key sẽ cho kết quả chính xác hơn.

## 🎨 Workflow tích hợp vào SmartBus

```
┌─────────────────┐
│ User nhập vị trí│
│  + tuyến xe     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Agent tìm các vé phù hợp│
└────────┬────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ calculate_distance_google_maps │ ◄── Tool mới
│ - Tính khoảng cách user → điểm │
│   đón của từng vé              │
└────────┬───────────────────────┘
         │
         ▼
┌─────────────────────────┐
│ find_nearest_pickup_point│ ◄── Tool mới
│ - Tìm điểm đón gần nhất │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Agent gợi ý top 3 vé:    │
│ 1. Vé A - 1.2km - link🗺️ │
│ 2. Vé B - 3.5km - link🗺️ │
│ 3. Vé C - 5.8km - link🗺️ │
└──────────────────────────┘
```

## 📁 Files đã tạo/sửa đổi

1. ✅ `backend/app/agent/tools.py` - Thêm 4 functions mới
2. ✅ `backend/app/agent/distance_example.py` - File ví dụ (MỚI)
3. ✅ `backend/tests/test_agent.py` - Thêm 7 tests
4. ✅ `docs/google-maps-integration.md` - Tài liệu đầy đủ (MỚI)
5. ✅ `docs/DISTANCE_TOOL_SUMMARY.md` - File này (MỚI)
6. ✅ `requirements.txt` - Thêm requests và python-dotenv

## 🎯 Next Steps (Đề xuất)

### 1. Thêm tọa độ thực cho điểm đón trong mock data

Hiện tại `mock_tickets.py` không có lat/lng cho điểm đón. Nên thêm:

```python
MockTicket(
    id="vx-hn-dn-001",
    # ... existing fields
    pickup_lat=21.0285,  # ← Thêm
    pickup_lng=105.7803,  # ← Thêm
)
```

### 2. Tích hợp vào service.py

Sửa `search_trip()` để tự động tính khoảng cách thực thay vì dùng mock distance:

```python
def search_trip(query: TripQuery):
    tickets = search_mock_tickets(query)
    
    # Tính khoảng cách thực cho từng vé
    for ticket in tickets:
        result = calculate_distance_google_maps(
            query.user_location.lat,
            query.user_location.lng,
            ticket.pickup_lat,
            ticket.pickup_lng,
        )
        ticket.pickup_distance_km = result["distance_km"]
    
    ranked = rank_tickets(tickets, query.priority)
    # ...
```

### 3. Tích hợp vào Gemini Agent

Thêm `calculate_pickup_distance_tool` vào danh sách tools của Gemini.

### 4. Frontend integration

Hiển thị link Google Maps trên frontend để user có thể click vào xem đường đi.

## 🔥 Demo nhanh

Chạy lệnh này để xem tool hoạt động:

```bash
python -m backend.app.agent.distance_example
```

Output:
```
🚌 SMARTBUS - GOOGLE MAPS DISTANCE TOOL EXAMPLES

============================================================
VÍ DỤ 1: Tính khoảng cách giữa 2 điểm
============================================================
Từ: Cầu Giấy, Hà Nội
Đến: Bến xe Mỹ Đình
Khoảng cách: 1.4 km
Thời gian: Không xác định
Phương thức tính: haversine_fallback
Link dẫn đường: https://www.google.com/maps/dir/?api=1&origin=...

[... 3 ví dụ khác ...]

✅ Hoàn thành tất cả ví dụ!
```

## 📞 Hỗ trợ

Xem chi tiết tại:
- **Tài liệu đầy đủ:** `docs/google-maps-integration.md`
- **Code ví dụ:** `backend/app/agent/distance_example.py`
- **Tests:** `backend/tests/test_agent.py` (dòng 103+)
