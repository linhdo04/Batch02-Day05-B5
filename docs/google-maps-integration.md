# Google Maps Distance Tool - Hướng dẫn tích hợp

## Tổng quan

SmartBus đã được tích hợp công cụ tính khoảng cách sử dụng **Google Maps Distance Matrix API** để:
- Tính khoảng cách thực tế giữa vị trí người dùng và các điểm đón
- Tìm điểm đón gần nhất
- Tìm điểm trả tối ưu
- Tạo link Google Maps để dẫn đường

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Lấy Google Maps API Key (Tùy chọn nhưng khuyến nghị)

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project hiện có
3. Enable **Distance Matrix API**:
   - Vào "APIs & Services" > "Library"
   - Tìm "Distance Matrix API"
   - Nhấn "Enable"
4. Tạo API key:
   - Vào "APIs & Services" > "Credentials"
   - Nhấn "Create Credentials" > "API Key"
   - Copy API key

### 3. Cấu hình API Key

Tạo file `.env` ở root directory:

```bash
GOOGLE_MAPS_API_KEY=your_api_key_here
```

**Lưu ý:** Nếu không có API key, tool vẫn hoạt động bằng công thức Haversine (tính khoảng cách đường chim bay).

## Các hàm chính

### 1. `calculate_distance_google_maps()`

Tính khoảng cách và thời gian di chuyển giữa 2 điểm.

```python
from backend.app.agent.tools import calculate_distance_google_maps

result = calculate_distance_google_maps(
    origin_lat=21.0369,  # Vĩ độ điểm xuất phát
    origin_lng=105.7897,  # Kinh độ điểm xuất phát
    dest_lat=21.0285,     # Vĩ độ điểm đến
    dest_lng=105.7803,    # Kinh độ điểm đến
    origin_address="Cầu Giấy, Hà Nội",  # Optional
    dest_address="Bến xe Mỹ Đình",      # Optional
)

# Kết quả:
# {
#     "distance_km": 7.4,
#     "distance_text": "7.4 km",
#     "duration_text": "15 phút",
#     "duration_seconds": 900,
#     "maps_link": "https://www.google.com/maps/dir/?api=1&origin=...",
#     "success": True,
#     "error": None,
#     "method": "google_maps_api"  # hoặc "haversine_fallback"
# }
```

### 2. `find_nearest_pickup_point()`

Tìm điểm đón gần nhất từ danh sách các điểm đón.

```python
from backend.app.agent.tools import find_nearest_pickup_point

pickup_points = [
    {
        "name": "Bến xe Mỹ Đình",
        "address": "20 Phạm Hùng, Mỹ Đình, Nam Từ Liêm, Hà Nội",
        "lat": 21.0285,
        "lng": 105.7803,
    },
    {
        "name": "Văn phòng Cầu Giấy",
        "address": "165 Cầu Giấy, Dịch Vọng, Cầu Giấy, Hà Nội",
        "lat": 21.0333,
        "lng": 105.7947,
    },
]

result = find_nearest_pickup_point(
    user_lat=21.0369,
    user_lng=105.7897,
    pickup_points=pickup_points,
)

# Kết quả:
# {
#     "success": True,
#     "nearest_point": {
#         "name": "Văn phòng Cầu Giấy",
#         "address": "165 Cầu Giấy, Dịch Vọng, Cầu Giấy, Hà Nội",
#         "lat": 21.0333,
#         "lng": 105.7947,
#         "distance_km": 1.2,
#         "distance_text": "1.2 km",
#         "duration_text": "5 phút",
#         "maps_link": "https://www.google.com/maps/dir/?api=1&origin=..."
#     },
#     "all_distances": [...]
# }
```

### 3. `build_directions_link()`

Tạo link Google Maps để dẫn đường.

```python
from backend.app.agent.tools import build_directions_link

link = build_directions_link(
    origin_lat=21.0369,
    origin_lng=105.7897,
    dest_lat=21.0285,
    dest_lng=105.7803
)

# Kết quả:
# "https://www.google.com/maps/dir/?api=1&origin=21.0369,105.7897&destination=21.0285,105.7803&travelmode=driving"
```

## Tích hợp với Agent

### Use Case 1: Tìm điểm đón gần nhất

Agent có thể gọi tool này khi user hỏi "điểm đón nào gần tôi nhất?"

```python
def suggest_nearest_pickup_for_user(user_location: dict, tickets: list):
    """
    Gợi ý điểm đón gần nhất cho từng vé.
    """
    for ticket in tickets:
        # Giả sử ticket có thông tin tọa độ điểm đón
        result = calculate_distance_google_maps(
            origin_lat=user_location["lat"],
            origin_lng=user_location["lng"],
            dest_lat=ticket.pickup_lat,
            dest_lng=ticket.pickup_lng,
        )
        
        ticket.distance_km = result["distance_km"]
        ticket.duration_text = result["duration_text"]
        ticket.maps_link = result["maps_link"]
    
    # Sắp xếp theo khoảng cách
    tickets.sort(key=lambda x: x.distance_km)
    
    return tickets[:3]  # Top 3 gần nhất
```

### Use Case 2: Tính khoảng cách cho tất cả điểm đón của một nhà xe

Khi user chọn một nhà xe có nhiều điểm đón:

```python
def calculate_all_pickup_distances(user_lat, user_lng, bus_operator):
    """
    Tính khoảng cách từ user đến tất cả điểm đón của một nhà xe.
    """
    # Lấy danh sách điểm đón của nhà xe
    pickup_points = get_pickup_points_for_operator(bus_operator)
    
    # Tìm điểm đón gần nhất
    result = find_nearest_pickup_point(user_lat, user_lng, pickup_points)
    
    if result["success"]:
        nearest = result["nearest_point"]
        return f"""
        🚌 Nhà xe {bus_operator} có {len(pickup_points)} điểm đón.
        
        ✅ GẦN BẠN NHẤT:
        📍 {nearest['name']}
        📫 {nearest['address']}
        📏 Cách bạn: {nearest['distance_text']} ({nearest['duration_text']})
        🗺️  Xem đường đi: {nearest['maps_link']}
        """
```

### Use Case 3: Tính khoảng cách điểm trả với đích đến

```python
def suggest_optimal_dropoff(destination_lat, destination_lng, dropoff_points):
    """
    Gợi ý điểm trả gần đích đến nhất.
    """
    result = find_nearest_pickup_point(
        user_lat=destination_lat,
        user_lng=destination_lng,
        pickup_points=dropoff_points,
    )
    
    if result["success"]:
        nearest = result["nearest_point"]
        return {
            "dropoff_point": nearest["name"],
            "address": nearest["address"],
            "distance_from_destination": nearest["distance_km"],
            "maps_link": nearest["maps_link"],
        }
```

### Use Case 4: Tích hợp vào tool cho Gemini Agent

Để agent có thể tự động gọi tool tính khoảng cách:

```python
def calculate_pickup_distance_tool(
    user_lat: float,
    user_lng: float,
    pickup_lat: float,
    pickup_lng: float,
    pickup_name: str = "",
) -> str:
    """
    Tool cho agent: Tính khoảng cách từ vị trí người dùng đến điểm đón.
    
    Args:
        user_lat: Vĩ độ người dùng
        user_lng: Kinh độ người dùng
        pickup_lat: Vĩ độ điểm đón
        pickup_lng: Kinh độ điểm đón
        pickup_name: Tên điểm đón (tùy chọn)
    
    Returns:
        Thông tin khoảng cách dạng text để agent trả lời user
    """
    result = calculate_distance_google_maps(
        origin_lat=user_lat,
        origin_lng=user_lng,
        dest_lat=pickup_lat,
        dest_lng=pickup_lng,
    )
    
    if result["success"]:
        return (
            f"Điểm đón {pickup_name if pickup_name else 'này'} cách bạn {result['distance_text']}, "
            f"mất khoảng {result['duration_text']} để di chuyển. "
            f"Xem đường đi tại: {result['maps_link']}"
        )
    else:
        return f"Không thể tính khoảng cách. Lỗi: {result['error']}"


# Thêm vào config tools của Gemini
from google.genai import types

tools = [
    search_and_format_tickets,
    resolve_pickup_ambiguity_tool,
    calculate_pickup_distance_tool,  # ← Tool mới
]

config = types.GenerateContentConfig(
    system_instruction="...",
    tools=tools,
)
```

## Chạy ví dụ

Chạy file ví dụ để xem các use cases:

```bash
cd backend
python -m app.agent.distance_example
```

## So sánh: Google Maps API vs Haversine

| Tiêu chí | Google Maps API | Haversine Fallback |
|----------|----------------|-------------------|
| **Độ chính xác** | Cao (theo đường đi thực tế) | Trung bình (đường chim bay) |
| **Thời gian di chuyển** | ✅ Có | ❌ Không |
| **Yêu cầu API key** | ✅ Có | ❌ Không |
| **Chi phí** | Free tier: 40,000 requests/tháng | Miễn phí hoàn toàn |
| **Tốc độ** | ~500ms | <1ms |

## Best Practices

### 1. Cache kết quả

```python
# Cache khoảng cách giữa các địa điểm cố định
DISTANCE_CACHE = {}

def get_cached_distance(user_lat, user_lng, dest_lat, dest_lng):
    key = f"{user_lat},{user_lng}|{dest_lat},{dest_lng}"
    if key not in DISTANCE_CACHE:
        DISTANCE_CACHE[key] = calculate_distance_google_maps(
            user_lat, user_lng, dest_lat, dest_lng
        )
    return DISTANCE_CACHE[key]
```

### 2. Batch requests

Nếu cần tính nhiều khoảng cách, gom lại thành batch để giảm số lượng API calls.

### 3. Fallback gracefully

Tool đã được thiết kế để tự động fallback về Haversine nếu API thất bại.

### 4. Giới hạn số lượng điểm

Chỉ tính khoảng cách cho top N điểm đón gần nhất (theo Haversine trước) để tiết kiệm API calls.

```python
def smart_find_nearest(user_lat, user_lng, all_points, limit=5):
    # Bước 1: Lọc nhanh bằng Haversine
    distances = []
    for point in all_points:
        haversine_dist = _haversine_distance(
            user_lat, user_lng, point["lat"], point["lng"]
        )
        distances.append((point, haversine_dist))
    
    # Bước 2: Chỉ tính chính xác cho top N
    top_points = sorted(distances, key=lambda x: x[1])[:limit]
    
    # Bước 3: Dùng Google Maps API cho top N
    final_results = []
    for point, _ in top_points:
        result = calculate_distance_google_maps(
            user_lat, user_lng, point["lat"], point["lng"]
        )
        final_results.append((point, result))
    
    return sorted(final_results, key=lambda x: x[1]["distance_km"])
```

## Troubleshooting

### Lỗi: "API returned status: REQUEST_DENIED"

- Kiểm tra API key có đúng không
- Kiểm tra Distance Matrix API đã được enable chưa
- Kiểm tra billing có được setup chưa (Google yêu cầu thẻ tín dụng)

### Lỗi: "API returned status: OVER_QUERY_LIMIT"

- Bạn đã vượt quota miễn phí (40,000 requests/tháng)
- Giải pháp: Implement caching hoặc upgrade plan

### Tool luôn dùng Haversine

- Kiểm tra file `.env` có tồn tại không
- Kiểm tra tên biến là `GOOGLE_MAPS_API_KEY` (đúng chính tả)
- Chạy `python -c "import os; print(os.getenv('GOOGLE_MAPS_API_KEY'))"` để verify

## Tài liệu tham khảo

- [Google Maps Distance Matrix API](https://developers.google.com/maps/documentation/distance-matrix)
- [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula)
- [Google Maps API Pricing](https://developers.google.com/maps/billing-and-pricing/pricing)
