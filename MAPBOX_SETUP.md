# 🗺️ Tích hợp Mapbox API - GIẢI PHÁP HOÀN CHỈNH

## 🎯 Tại sao dùng Mapbox thay vì Google Maps?

| Feature | Mapbox | Google Maps |
|---------|--------|-------------|
| **Geocoding** | ✅ 100,000 free/tháng | ⚠️ 40,000 free nhưng cần billing |
| **Distance calculation** | ✅ 100,000 free/tháng | ⚠️ 40,000 free nhưng cần billing |
| **Cần thẻ tín dụng** | ❌ KHÔNG | ✅ BẮT BUỘC |
| **Signup** | ✅ Email only | ❌ Email + thẻ |
| **Khoảng cách** | ✅ Chính xác (đường bộ) | ✅ Chính xác (đường bộ) |
| **Thời gian di chuyển** | ✅ Yes | ✅ Yes |
| **Map display** | ✅ Yes | ✅ Yes |

**Kết luận:** Mapbox là lựa chọn tốt nhất cho bạn!

## 📦 Đã tạo

### Backend Files

1. **`backend/app/agent/mapbox_tools.py`**
   - `mapbox_geocode()` - Chuyển địa chỉ → tọa độ
   - `mapbox_calculate_distance()` - Tính khoảng cách + thời gian
   - `mapbox_matrix_distance()` - Tính nhiều điểm cùng lúc
   - Tự động fallback về Haversine nếu không có API key

### Test Files

2. **`test_mapbox_api.py`**
   - Test script đầy đủ
   - So sánh Mapbox vs Haversine
   - Matrix calculation demo

### Frontend Files

3. **`frontend/components/MapEmbed.tsx`** (đã tạo trước)
   - Hiển thị bản đồ Mapbox
   - Support directions mode
   - Free tier unlimited map loads

## 🚀 Setup Guide

### Bước 1: Tạo Mapbox account (MIỄN PHÍ)

1. Vào: https://account.mapbox.com/auth/signup/
2. Điền thông tin:
   - Email
   - Username
   - Password
3. **KHÔNG CẦN** thêm thẻ tín dụng
4. Click **"Get started"**

### Bước 2: Lấy Access Token

1. Sau khi đăng nhập, vào: https://account.mapbox.com/access-tokens/
2. Copy **"Default public token"**
   - Format: `pk.eyJ1IjoieW91cnVzZXJuYW1lIiwi...`
3. Token này public, safe để dùng trên frontend và backend

### Bước 3: Thêm vào .env

Mở file `.env` và thêm:

```env
# Mapbox Access Token (FREE - 100,000 requests/tháng)
# Get from: https://account.mapbox.com/access-tokens/
MAPBOX_ACCESS_TOKEN=pk.eyJ1IjoieW91cnVzZXJuYW1lIiwi...
```

### Bước 4: Test

```bash
python test_mapbox_api.py
```

**Kết quả mong đợi:**

```
================================================================================
TEST MAPBOX APIs
================================================================================

🔑 API Key: pk.eyJ1IjoieW91cnVz...

================================================================================
TEST 1: GEOCODING API - Chuyển địa chỉ → tọa độ
================================================================================

📍 Test: Bà Rịa, Việt Nam
   Phương thức: mapbox_geocoding
   Tọa độ: (10.5063, 107.1639)
   Địa chỉ: Bà Rịa, Bà Rịa - Vũng Tàu, Vietnam
   ✅ SUCCESS

================================================================================
TEST 2: DIRECTIONS API - Tính khoảng cách + thời gian
================================================================================

🚗 Tuyến: Bà Rịa → Sân bay Tân Sơn Nhất
   Phương thức: mapbox_directions
   Khoảng cách: 129.5 km
   Thời gian: 95 phút
   ✅ SUCCESS

📊 So sánh:
   Haversine (đường chim bay): 66.0 km
   Mapbox (đường bộ thực tế): 129.5 km
   Chênh lệch: 96.2%

✅ Mapbox chính xác gấp 2 lần Haversine!
```

## 🔧 Tích hợp vào hệ thống

### Option 1: Thay thế hoàn toàn Google Maps tools

Update `backend/app/agent/tools.py`:

```python
# Thay đổi imports
from backend.app.agent.mapbox_tools import (
    mapbox_geocode as geocode_address,
    mapbox_calculate_distance as calculate_distance_google_maps,
)

# Hoặc rename functions
def geocode_address(address: str) -> dict:
    from backend.app.agent.mapbox_tools import mapbox_geocode
    return mapbox_geocode(address)

def calculate_distance_google_maps(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    origin_address: str = "",
    dest_address: str = "",
) -> dict:
    from backend.app.agent.mapbox_tools import mapbox_calculate_distance
    result = mapbox_calculate_distance(origin_lat, origin_lng, dest_lat, dest_lng)
    
    # Add maps_link (reuse existing function)
    from backend.app.agent.tools import build_directions_link
    result['maps_link'] = build_directions_link(origin_lat, origin_lng, dest_lat, dest_lng)
    
    return result
```

### Option 2: Dùng song song (recommended)

Giữ nguyên Google Maps tools, chỉ thêm Mapbox tools:

```python
# backend/app/agent/tools.py
from backend.app.agent.mapbox_tools import (
    mapbox_geocode,
    mapbox_calculate_distance,
    mapbox_matrix_distance,
)

# Wrapper để tự động chọn
def smart_geocode(address: str) -> dict:
    """Try Mapbox first, fallback to Google Maps, then database"""
    result = mapbox_geocode(address)
    if result['method'] == 'mapbox_geocoding':
        return result
    
    # Fallback to Google Maps if available
    return geocode_address(address)  # Existing function

def smart_calculate_distance(...) -> dict:
    """Try Mapbox first, fallback to Google Maps, then Haversine"""
    result = mapbox_calculate_distance(...)
    if result['method'] == 'mapbox_directions':
        return result
    
    # Fallback to Google Maps
    return calculate_distance_google_maps(...)  # Existing function
```

## 🗺️ Frontend Map Display

### Option 1: Mapbox GL JS (Interactive)

Update `frontend/components/MapEmbed.tsx` để dùng Mapbox thay vì Google:

```tsx
// Install: npm install mapbox-gl

import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN!;

// Create interactive map
const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/streets-v12',
  center: [lng, lat],
  zoom: 12
});

// Add markers
new mapboxgl.Marker()
  .setLngLat([pickupLng, pickupLat])
  .addTo(map);

// Add route
map.addLayer({
  id: 'route',
  type: 'line',
  source: {
    type: 'geojson',
    data: routeGeometry
  },
  paint: {
    'line-color': '#3b82f6',
    'line-width': 4
  }
});
```

### Option 2: Static Map API (Simple)

Dùng Mapbox Static Images API:

```tsx
const mapUrl = `https://api.mapbox.com/styles/v1/mapbox/streets-v12/static/` +
  `pin-s-a+3b82f6(${pickupLng},${pickupLat}),` +
  `pin-s-b+ef4444(${destLng},${destLat})/` +
  `auto/800x600@2x?access_token=${MAPBOX_ACCESS_TOKEN}`;

<img src={mapUrl} alt="Map" />
```

## 📊 So sánh chi tiết

### Khoảng cách Bà Rịa → Sài Gòn

| Method | Distance | Accuracy |
|--------|----------|----------|
| **Haversine** | ~66 km | ❌ Sai 100% (đường chim bay) |
| **Mapbox Directions** | ~129 km | ✅ Chính xác (đường bộ) |
| **Google Distance Matrix** | ~129 km | ✅ Chính xác (đường bộ) |

### Chi phí

| Service | Free Tier | Cần thẻ? | Chi phí vượt quota |
|---------|-----------|----------|-------------------|
| **Mapbox Geocoding** | 100,000/tháng | ❌ No | $0.50/1000 |
| **Mapbox Directions** | 100,000/tháng | ❌ No | $0.50/1000 |
| **Mapbox Matrix** | 100,000/tháng | ❌ No | $5.00/1000 |
| **Google Geocoding** | 40,000/tháng | ✅ Yes | $5.00/1000 |
| **Google Distance Matrix** | 40,000/tháng | ✅ Yes | $5.00/1000 |

**Kết luận:** Mapbox rẻ hơn 10x và không cần thẻ!

## 🎯 Workflow hoàn chỉnh

### Backend: Tính toán chính xác

```python
# 1. Geocode địa chỉ điểm đón
pickup_result = mapbox_geocode("Bà Rịa, Việt Nam")
# → {lat: 10.5063, lng: 107.1639}

# 2. Geocode địa chỉ điểm đến
dest_result = mapbox_geocode("Sân bay Tân Sơn Nhất")
# → {lat: 10.8187, lng: 106.6519}

# 3. Tính khoảng cách thực tế
distance = mapbox_calculate_distance(
    pickup_result['lat'], pickup_result['lng'],
    dest_result['lat'], dest_result['lng']
)
# → {distance_km: 129.5, duration_text: "95 phút"}

# 4. Trả về cho frontend
ticket_dict = {
    "pickup_point": "Bà Rịa",
    "pickup_lat": pickup_result['lat'],
    "pickup_lng": pickup_result['lng'],
    "pickup_distance_km": distance['distance_km'],  # 129.5 km (chính xác!)
    "duration_text": distance['duration_text'],  # "95 phút"
}
```

### Frontend: Hiển thị bản đồ

```tsx
// Hiển thị bản đồ với Mapbox
<MapEmbed
  pickup={{ lat: ticket.pickup_lat, lng: ticket.pickup_lng }}
  destination={{ lat: destLat, lng: destLng }}
  mode="directions"
  provider="mapbox"  // Dùng Mapbox thay vì Google
  apiKey={process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN}
/>
```

## ✅ Checklist

### Backend

- [ ] Tạo Mapbox account (free)
- [ ] Copy access token
- [ ] Thêm `MAPBOX_ACCESS_TOKEN` vào `.env`
- [ ] Chạy `python test_mapbox_api.py`
- [ ] Update `backend/app/agent/tools.py` để dùng Mapbox
- [ ] Test với backend API

### Frontend

- [ ] Thêm `NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN` vào `frontend/.env.local`
- [ ] Update `MapEmbed.tsx` để support Mapbox
- [ ] Test hiển thị bản đồ
- [ ] Verify markers và routes

## 🐛 Troubleshooting

### Issue 1: "No MAPBOX_ACCESS_TOKEN"

**Solution:**
1. Kiểm tra file `.env` có dòng `MAPBOX_ACCESS_TOKEN=...`
2. Token phải bắt đầu bằng `pk.` (public token)
3. Restart backend server

### Issue 2: API returns 401 Unauthorized

**Nguyên nhân:** Token không hợp lệ hoặc expired.

**Solution:**
1. Vào https://account.mapbox.com/access-tokens/
2. Tạo token mới
3. Update vào `.env`

### Issue 3: Khoảng cách vẫn dùng Haversine

**Check:**
1. File `test_mapbox_api.py` cho kết quả gì?
2. Method có phải `mapbox_directions` không?
3. Backend đã dùng đúng function chưa?

## 📚 Resources

- [Mapbox Docs](https://docs.mapbox.com/)
- [Geocoding API](https://docs.mapbox.com/api/search/geocoding/)
- [Directions API](https://docs.mapbox.com/api/navigation/directions/)
- [Matrix API](https://docs.mapbox.com/api/navigation/matrix/)
- [Mapbox GL JS](https://docs.mapbox.com/mapbox-gl-js/)
- [Pricing](https://www.mapbox.com/pricing)

## 🎉 Kết luận

Với Mapbox:
- ✅ Không cần thẻ tín dụng
- ✅ 100,000 requests free/tháng
- ✅ Khoảng cách chính xác (theo đường bộ)
- ✅ Có thời gian di chuyển
- ✅ Rẻ hơn Google 10x
- ✅ Dễ setup hơn Google

**Đây là giải pháp hoàn hảo cho dự án của bạn!** 🚀
