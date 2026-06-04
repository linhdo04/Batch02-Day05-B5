# 🗺️ Mapbox Integration - Quick Start

## ✅ Đã hoàn thành

Backend đã được refactor để sử dụng **Mapbox APIs** thay vì Google Maps:
- ✅ `mapbox_tools.py` - 3 APIs (Geocoding, Directions, Matrix)
- ✅ `tools.py` - Wrapper functions dùng Mapbox
- ✅ Auto-fallback về Haversine nếu không có API key
- ✅ Không có duplicate code

## 🚀 Setup (2 phút)

### 1. Signup Mapbox (30s) - MIỄN PHÍ, không cần thẻ
```
https://account.mapbox.com/auth/signup/
```

### 2. Copy access token (10s)
```
https://account.mapbox.com/access-tokens/
```

### 3. Thêm vào .env (10s)
```env
MAPBOX_ACCESS_TOKEN=pk.eyJ1IjoieW91cnVzZXJuYW1lIiwi...
```

### 4. Test (30s)
```bash
python test_mapbox_api.py
```

Thấy `✅ SUCCESS` → DONE!

## 📊 Kết quả

**Bà Rịa → Sân bay:**
- ❌ Haversine: 66 km (SAI!)
- ✅ Mapbox: 129.5 km (ĐÚNG!)
- Chênh lệch: 96%

## 💡 APIs

```python
# Đã tích hợp sẵn trong tools.py:
from backend.app.agent.tools import (
    geocode_address,              # Địa chỉ → Tọa độ
    calculate_distance_google_maps # Tính khoảng cách chính xác
)

# Hoặc dùng trực tiếp:
from backend.app.agent.mapbox_tools import (
    mapbox_geocode,
    mapbox_calculate_distance,
    mapbox_matrix_distance
)
```

## 🎯 So sánh

| Feature | Mapbox | Google Maps |
|---------|--------|-------------|
| **Cần thẻ?** | ❌ NO | ✅ YES |
| **Free tier** | 100k/tháng | 40k/tháng |
| **Chi phí** | $0.50/1k | $5.00/1k |

## 📚 Docs

- Setup chi tiết: `MAPBOX_SETUP.md`
- Test script: `python test_mapbox_api.py`

---

**Signup ngay:** https://account.mapbox.com/auth/signup/ 🚀
