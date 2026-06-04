# Tích hợp Tuyến Vũng Tàu - Sài Gòn với Điểm Đón/Trả Tối Ưu

## 🎯 Tổng quan

Hệ thống đã được tích hợp hoàn chỉnh để tìm kiếm vé xe Vũng Tàu - Sài Gòn với khả năng:

1. ✅ **Load dữ liệu JSON chi tiết** về các nhà xe và tuyến đường
2. ✅ **Geocoding với fallback database** (không cần Google Maps API key)
3. ✅ **Hybrid Workflow**: Search API → Enrich với waypoints từ database
4. ✅ **Tính khoảng cách thực tế** từ vị trí user đến TẤT CẢ điểm đón (Haversine fallback)
5. ✅ **Tính khoảng cách** từ TẤT CẢ điểm trả đến đích của user
6. ✅ **Chọn điểm đón/trả tối ưu** (gần nhất)
7. ✅ **Sắp xếp theo tổng điểm** (giá + khoảng cách)
8. ✅ **Tạo link Google Maps** dẫn đường cho user
9. ✅ **Hoạt động HOÀN TOÀN không cần API key**

## 📂 Cấu trúc Files

```
backend/
├── app/
│   ├── agent/
│   │   ├── tools.py                    # Tool tích hợp: search_vungtau_saigon_route_optimized()
│   │   └── vungtau_routes.py          # Logic xử lý tuyến VT-SG
│   └── data/
│       └── vungtau_saigon.json        # Dữ liệu nhà xe, tuyến, waypoints
└── tests/
    └── test_vungtau_integration.py    # Tests tích hợp
```

## 🚀 Workflow Hoạt Động

### 🎯 Workflow 1: Direct Search (search_vungtau_routes_by_address_tool)

```
User nhập vị trí đón + vị trí đến
         ↓
geocode_address() ← Chuyển địa chỉ thành tọa độ (fallback database)
         ↓
load_vungtau_saigon_data()  ← Load JSON
         ↓
find_optimal_route()  ← Tìm tuyến phù hợp
         ↓
┌─────────────────────────────────────────┐
│ Cho MỖI nhà xe và MỖI tuyến đường:     │
├─────────────────────────────────────────┤
│ 1. Lấy TẤT CẢ điểm đón (pickup points) │
│ 2. Tính khoảng cách user → từng điểm   │
│ 3. Chọn điểm đón GẦN NHẤT              │
│                                         │
│ 4. Lấy TẤT CẢ điểm trả (dropoff points)│
│ 5. Tính khoảng cách từng điểm → đích   │
│ 6. Chọn điểm trả GẦN ĐẾN ĐÍCH NHẤT     │
└─────────────────────────────────────────┘
         ↓
Tính điểm tổng hợp = pickup_distance + dropoff_distance
         ↓
Sắp xếp theo điểm (gần nhất lên đầu)
         ↓
format_route_recommendation()  ← Format kết quả
         ↓
Trả về top 3 tuyến tối ưu nhất với:
- Giá vé
- Điểm đón gần nhất + khoảng cách
- Điểm trả gần đích nhất + khoảng cách
- Link Google Maps dẫn đường
- Hotline nhà xe
```

### 🔄 Workflow 2: Hybrid (RECOMMENDED - enrich_search_results_with_waypoints_tool)

**Ưu điểm**: Tận dụng search API có sẵn (Vexere, scraping) + Enrich với waypoints chi tiết

```
┌─────────────────────────────────────────┐
│ BƯỚC 1: TÌM VÉ (Search API/Mock)       │
│ - Gọi search_and_format_tickets()      │
│ - Hoặc scrape từ Vexere API            │
│ - Kết quả: List vé với tên nhà xe     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ BƯỚC 2: GEOCODE ADDRESSES              │
│ - user_pickup_address → lat/lng        │
│ - user_dropoff_address → lat/lng       │
│ - Sử dụng fallback database            │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ BƯỚC 3: ENRICH TỪNG VÉ                 │
│ Cho MỖI vé trong search results:       │
│   1. Extract operator name & route     │
│   2. Match với vungtau_saigon.json     │
│      - normalize_text() cho matching   │
│      - Case-insensitive                │
│   3. Lấy waypoints từ matched route    │
│   4. Tính khoảng cách pickup/dropoff   │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ BƯỚC 4: FORMAT & RETURN                │
│ - Vé gốc từ search API                 │
│ + Điểm đón gần nhất (+ khoảng cách)   │
│ + Điểm trả gần đích nhất (+ khoảng cách)│
│ + Link Google Maps navigation          │
│ + Thông tin liên hệ nhà xe             │
└─────────────────────────────────────────┘
```

**Khi nào dùng Hybrid Workflow?**
- ✅ Có sẵn search API (Vexere, internal API)
- ✅ Muốn kết hợp real-time availability với waypoints
- ✅ Database JSON chỉ lưu waypoints (không phải full ticket data)
- ✅ Linh hoạt thêm/bớt nhà xe mới

## 📊 Dữ liệu JSON

File `backend/app/data/vungtau_saigon.json` chứa:

### Cấu trúc Operators

```json
{
  "operators": [
    {
      "operator_id": "OP_TOANTHANG",
      "name": "Toàn Thắng Limousine",
      "type": "Limousine",
      "contact_phone": "1900 6968",
      "routes": [...]
    }
  ]
}
```

### Cấu trúc Routes

```json
{
  "route_id": "TT_VT_SGN_TSN",
  "route_name": "Vũng Tàu - Sân Bay Tân Sơn Nhất",
  "base_price_vnd": 200000,
  "transit_supported": true,
  "waypoints": [...]
}
```

### Cấu trúc Waypoints

**QUAN TRỌNG:** Mỗi waypoint phải có `lat` và `lng`!

```json
{
  "order": 1,
  "node_name": "Nội thành Vũng Tàu",
  "type": "pickup_transit",
  "eta_offset_mins": 0,
  "lat": 10.3460,  // ← BẮT BUỘC
  "lng": 107.0843  // ← BẮT BUỘC
}
```

**Các loại waypoint:**
- `pickup` - Điểm đón thông thường
- `pickup_transit` - Hỗ trợ đón tận nơi trong khu vực
- `dropoff` - Điểm trả
- `terminal` - Bến xe / văn phòng (có thể là cả đón lẫn trả)

## 🔧 API / Tools

### 1. `geocode_address(address: str)` ⭐ NEW

Chuyển địa chỉ text thành tọa độ (lat, lng) với fallback database.

```python
from backend.app.agent.tools import geocode_address

result = geocode_address("Bà Rịa")
# {
#   "lat": 10.5063,
#   "lng": 107.1639,
#   "formatted_address": "Bà Rịa",
#   "success": True,
#   "method": "fallback_database"
# }
```

**Fallback Database** (không cần API key):
- Vũng Tàu / vũng tàu: `10.3460, 107.0843`
- Bà Rịa / bà rịa: `10.5063, 107.1639`
- Quận 1 / quận 1: `10.7707, 106.6906`
- Sân bay Tân Sơn Nhất: `10.8187, 106.6519`
- Quận 9 / Thủ Đức: `10.8500, 106.7800`
- Bến xe Miền Đông: `10.8150, 106.7117`
- Sài Gòn / TP.HCM: `10.7769, 106.7009`

### 2. `enrich_ticket_with_waypoints()` ⭐ NEW

Match ticket từ search API với database JSON và tìm điểm đón/trả tối ưu.

```python
from backend.app.agent.vungtau_routes import enrich_ticket_with_waypoints

enriched = enrich_ticket_with_waypoints(
    operator_name="Toàn Thắng Limousine",
    route_keywords=["Vũng Tàu", "Sân Bay", "Tân Sơn Nhất"],
    user_pickup_lat=10.5063,
    user_pickup_lng=107.1639,
    user_dropoff_lat=10.8187,
    user_dropoff_lng=106.6519,
)

# Result:
# {
#   "success": True,
#   "operator_name": "Toàn Thắng Limousine",
#   "route_name": "Vũng Tàu - Sân Bay Tân Sơn Nhất",
#   "base_price_vnd": 200000,
#   "nearest_pickup": {
#       "node_name": "Co.op Mart Bà Rịa",
#       "distance_km": 0.0,
#       "maps_link": "..."
#   },
#   "nearest_dropoff": {
#       "node_name": "Sân bay Tân Sơn Nhất",
#       "distance_km": 0.0,
#       "maps_link": "..."
#   }
# }
```

### 3. `enrich_search_results_with_waypoints_tool()` ⭐ NEW - HYBRID WORKFLOW

Tool cho Gemini Agent để enrich kết quả search với waypoints.

```python
from backend.app.agent.vungtau_routes import enrich_search_results_with_waypoints_tool
import json

# Giả sử đây là kết quả từ search API
tickets = [
    {
        "operator": "Toàn Thắng Limousine",
        "route": "Vũng Tàu - Sân Bay Tân Sơn Nhất",
        "price": 200000,
        "departure": "08:00"
    }
]

result = enrich_search_results_with_waypoints_tool(
    tickets_json=json.dumps(tickets),
    user_pickup_address="Bà Rịa",
    user_dropoff_address="Sân bay Tân Sơn Nhất"
)

print(result)  # Text formatted sẵn cho user
```

### 4. `find_optimal_route()` - DIRECT SEARCH

Tìm tuyến xe tối ưu dựa trên vị trí.

```python
from backend.app.agent.vungtau_routes import find_optimal_route

routes = find_optimal_route(
    pickup_location=(10.3460, 107.0843),  # (lat, lng) điểm đón
    dropoff_location=(10.7707, 106.6906),  # (lat, lng) điểm đến
    max_results=3,
)

# Kết quả
for route in routes:
    print(f"Nhà xe: {route['operator_name']}")
    print(f"Tuyến: {route['route_name']}")
    print(f"Giá: {route['base_price_vnd']:,} VNĐ")
    print(f"Điểm đón: {route['nearest_pickup']['node_name']} ({route['nearest_pickup']['distance_km']} km)")
    print(f"Điểm trả: {route['nearest_dropoff']['node_name']} ({route['nearest_dropoff']['distance_km']} km)")
```

### 2. `search_vungtau_saigon_route_optimized()` - Tool cho Agent

Tool này được thiết kế để Gemini Agent có thể gọi trực tiếp (Direct Search Workflow).

```python
from backend.app.agent.tools import search_vungtau_saigon_route_optimized

result = search_vungtau_saigon_route_optimized(
    pickup_address="Trung tâm Vũng Tàu",
    pickup_lat=10.3460,
    pickup_lng=107.0843,
    dropoff_address="Quận 1, TP.HCM",
    dropoff_lat=10.7707,
    dropoff_lng=106.6906,
    date="2026-06-06",
    max_results=3,
)

print(result)  # Text đã format sẵn cho user
```

### 6. `search_vungtau_routes_by_address_tool()` ⭐ RECOMMENDED

One-step tool: Tự động geocode + tìm tuyến + format.

```python
from backend.app.agent.tools import search_vungtau_routes_by_address_tool

result = search_vungtau_routes_by_address_tool(
    pickup_address="Bà Rịa",
    dropoff_address="Sân bay Tân Sơn Nhất"
)
print(result)  # Formatted text với top 3 tuyến
```

## 🎯 So Sánh 2 Workflows

| Feature | Direct Search | Hybrid (Recommended) |
|---------|---------------|----------------------|
| **Data Source** | JSON database only | Search API + JSON enrichment |
| **Use Case** | Tuyến đặc biệt (VT-SG) | General search + enrich |
| **Flexibility** | Medium | High |
| **Real-time availability** | ❌ | ✅ (from search API) |
| **Waypoint details** | ✅ | ✅ |
| **Setup complexity** | Simple | Medium |
| **Best for** | Fixed routes | Dynamic routes |

**Khi nào dùng gì?**
- **Direct Search**: User tìm tuyến cụ thể (Vũng Tàu → Sài Gòn)
- **Hybrid**: Có search API sẵn, muốn thêm waypoint details

## 🧪 Testing

### Test Hybrid Workflow (RECOMMENDED)

```bash
python -m backend.app.agent.test_hybrid_workflow
```

**Output:**
```
🚌 Gợi ý tuyến xe từ Bà Rịa đến Sân bay Tân Sơn Nhất:

**1. Toàn Thắng Limousine** (Limousine)
   📍 Tuyến: Vũng Tàu - Sân Bay Tân Sơn Nhất
   💰 Giá vé: 200,000 VNĐ
   📞 Hotline: 1900 6968

   🔵 Điểm đón gần bạn nhất:
      • Co.op Mart Bà Rịa
      • Cách bạn: 0.0 km ← Perfect match!
      • 🗺️ [Xem đường đi](...)

   🔴 Điểm trả gần đích nhất:
      • Sân bay Tân Sơn Nhất - Ga Quốc Nội
      • Cách đích: 0.0 km ← Perfect match!
      • 🗺️ [Xem đường đi](...)

   ✅ Hỗ trợ đón/trả tận nơi
```

### Test Direct Search

Chạy tất cả tests:

```bash
python -m pytest backend/tests/test_vungtau_integration.py -v -s
```

### Test Cases

1. ✅ **test_load_vungtau_data** - Kiểm tra load JSON
2. ✅ **test_find_optimal_route_from_vungtau** - Tìm tuyến từ Vũng Tàu → Quận 1
3. ✅ **test_find_optimal_route_from_baria** - Tìm tuyến từ Bà Rịa → Sân Bay
4. ✅ **test_format_route_recommendation** - Kiểm tra format output
5. ✅ **test_search_tool_integration** - Kiểm tra tool cho agent
6. ✅ **test_edge_case_no_results** - Kiểm tra edge cases

### Kết quả Test

```
✅ Tìm thấy 3 tuyến phù hợp
📍 Tuyến tốt nhất: Hoa Mai Limousine - Vũng Tàu - Quận 1 (Cao Tốc)
💰 Giá: 200,000 VNĐ
🔵 Điểm đón: Nội thành Vũng Tàu (0.0 km)
🔴 Điểm trả: VP Quận 1 (83 Nguyễn Thái Bình) (0.0 km)
```

## 📱 Tích hợp vào Chat Agent

### Thêm tool vào Gemini Agent

Cập nhật file `backend/app/agent/service.py`:

```python
from backend.app.agent.tools import (
    search_and_format_tickets,
    resolve_pickup_ambiguity_tool,
    search_vungtau_saigon_route_optimized,  # ← Thêm tool mới
)

# Trong chat_agent()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=[
            search_and_format_tickets,
            resolve_pickup_ambiguity_tool,
            search_vungtau_saigon_route_optimized,  # ← Thêm vào list
        ],
    )
)
```

### Cập nhật System Instruction

```python
system_instruction = (
    "Bạn là Trợ lý SmartBus...\n"
    "...\n"
    "5. Nếu user tìm vé Vũng Tàu - Sài Gòn, hãy gọi tool `search_vungtau_saigon_route_optimized` "
    "với tọa độ và địa chỉ điểm đón/trả của user để tìm tuyến xe tối ưu nhất.\n"
)
```

## 🎯 Use Cases

### Use Case 1: Tìm vé từ Vũng Tàu đến Quận 1

**User Input:**
> "Tôi ở Vũng Tàu (10.3460, 107.0843), muốn đi Quận 1, TP.HCM (10.7707, 106.6906)"

**Agent gọi:**
```python
search_vungtau_saigon_route_optimized(
    pickup_address="Vũng Tàu",
    pickup_lat=10.3460,
    pickup_lng=107.0843,
    dropoff_address="Quận 1, TP.HCM",
    dropoff_lat=10.7707,
    dropoff_lng=106.6906,
)
```

**Kết quả:**
- Top 3 nhà xe được sắp xếp theo độ phù hợp
- Mỗi nhà xe có:
  - Điểm đón gần user nhất (0-0.5 km)
  - Điểm trả gần đích nhất (0-0.2 km)
  - Link Google Maps dẫn đường
  - Giá vé, hotline

### Use Case 2: Tìm vé từ Bà Rịa đến Sân Bay

**User Input:**
> "Từ Bà Rịa (10.5063, 107.1639) đến Sân Bay Tân Sơn Nhất (10.8187, 106.6519)"

**Kết quả:**
- Ưu tiên các tuyến có điểm trả tại Sân Bay
- Điểm đón: Co.op Mart Bà Rịa (0 km)
- Điểm trả: Sân Bay Tân Sơn Nhất (0 km)

### Use Case 3: User không biết tọa độ

**User Input:**
> "Tìm vé từ Vũng Tàu đến Sài Gòn"

**Agent workflow:**
1. Hỏi user: "Bạn ở đâu tại Vũng Tàu? (ví dụ: Trung tâm, Bãi Sau, ...)"
2. Hỏi: "Bạn muốn đến đâu tại Sài Gòn? (ví dụ: Quận 1, Sân Bay, Bến Xe Miền Đông, ...)"
3. Tra cứu tọa độ (hoặc dùng địa danh mặc định)
4. Gọi tool

## 🔄 Mở rộng cho các tuyến khác

### Thêm tuyến mới

1. Tạo file JSON mới: `backend/app/data/hanoi_halong.json`
2. Copy cấu trúc từ `vungtau_saigon.json`
3. Thêm tọa độ (lat/lng) cho TẤT CẢ waypoints
4. Tạo module mới: `backend/app/agent/hanoi_routes.py`
5. Tạo tool mới: `search_hanoi_halong_route_optimized()`

### Template JSON cho tuyến mới

```json
{
  "region": "North_Vietnam",
  "route_group": "HN-HL",
  "operators": [
    {
      "operator_id": "OP_XXX",
      "name": "Tên Nhà Xe",
      "type": "Limousine",
      "contact_phone": "1900 xxxx",
      "routes": [
        {
          "route_id": "XXX_HN_HL",
          "route_name": "Hà Nội - Hạ Long",
          "base_price_vnd": 150000,
          "transit_supported": true,
          "waypoints": [
            {
              "order": 1,
              "node_name": "Bến xe...",
              "type": "pickup",
              "eta_offset_mins": 0,
              "lat": 21.xxxx,  // ← BẮT BUỘC
              "lng": 105.xxxx  // ← BẮT BUỘC
            }
          ]
        }
      ]
    }
  ]
}
```

## 📈 Performance

- **Load JSON:** ~1ms (cached sau lần đầu)
- **Tính khoảng cách:** ~1ms mỗi điểm (Haversine) hoặc ~500ms (Google API)
- **Tìm tuyến tối ưu:** ~10-50ms cho 5 nhà xe
- **Total response time:** <100ms (không có API key) hoặc ~2-3s (với API key)

## ⚠️ Lưu ý

### 1. Tọa độ là BẮT BUỘC

Mỗi waypoint PHẢI có `lat` và `lng`. Nếu thiếu, tool sẽ bỏ qua waypoint đó.

### 2. Độ chính xác tọa độ

- Sử dụng Google Maps để lấy tọa độ chính xác
- Định dạng: Decimal degrees (ví dụ: 10.3460, 107.0843)
- Độ chính xác: 4 chữ số sau dấu phẩy (~10m)

### 3. Caching

Dữ liệu JSON được cache trong memory sau lần load đầu tiên. 
Nếu cập nhật JSON, cần restart server.

### 4. Không có API Key

Tool vẫn hoạt động tốt với Haversine fallback:
- ✅ Tính khoảng cách (đường chim bay)
- ✅ Tạo link Google Maps
- ❌ Không có thời gian di chuyển

## 🎓 Best Practices

1. **Luôn thêm tọa độ cho waypoints mới**
2. **Test sau mỗi lần cập nhật JSON**
3. **Sử dụng tên waypoint rõ ràng** (ví dụ: "Co.op Mart Bà Rịa" thay vì "Điểm đón 1")
4. **Sắp xếp waypoints theo thứ tự** (order: 1, 2, 3, ...)
5. **Phân loại type chính xác** (pickup, dropoff, terminal)

## 🚀 Next Steps

1. ✅ Tích hợp vào Gemini Agent
2. ⏳ Thêm dữ liệu cho các tuyến khác (Hà Nội - Hạ Long, HCM - Đà Lạt, ...)
3. ⏳ Tích hợp geocoding API để tự động lấy tọa độ từ địa chỉ
4. ⏳ Thêm filter theo giá, loại xe, thời gian
5. ⏳ Cache kết quả tìm kiếm

## 📞 Support

Xem thêm:
- **Full documentation:** `docs/google-maps-integration.md`
- **Distance tools:** `backend/app/agent/tools.py`
- **Tests:** `backend/tests/test_vungtau_integration.py`
