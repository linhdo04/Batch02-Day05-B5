# 🗺️ Tích hợp Google Maps vào Frontend (MIỄN PHÍ)

## 📊 Tổng quan

Đã tích hợp **Google Maps Embed API** vào frontend để hiển thị:
- ✅ Bản đồ điểm đón trong mỗi ticket card
- ✅ Chỉ đường từ điểm đón đến điểm đến
- ✅ Modal mở rộng bản đồ toàn màn hình
- ✅ **100% MIỄN PHÍ** - Không cần billing account

## 🎯 Ưu điểm so với Geocoding/Distance Matrix APIs

| Feature | Embed API | Geocoding/Distance Matrix |
|---------|-----------|---------------------------|
| **Chi phí** | ✅ Miễn phí 100% | ❌ Cần billing account |
| **Setup** | ✅ Chỉ cần API key | ❌ Cần enable billing + APIs |
| **Use case** | ✅ Hiển thị bản đồ | ❌ Tính toán tọa độ/khoảng cách |
| **Quota** | ✅ Unlimited | ❌ 40,000 requests/month |

## 📂 Files đã tạo

### 1. `frontend/components/MapEmbed.tsx`
Component cơ bản để nhúng Google Maps Embed iframe.

**Props:**
- `pickup`: Tọa độ điểm đón `{ lat, lng }`
- `destination`: Tọa độ điểm đến `{ lat, lng }`
- `mode`: `"place"` (hiển thị địa điểm) hoặc `"directions"` (chỉ đường)
- `height`: Chiều cao bản đồ (px)

**Ví dụ:**
```tsx
<MapEmbed
  pickup={{ lat: 10.3460, lng: 107.0843 }}
  destination={{ lat: 10.7769, lng: 106.7009 }}
  mode="directions"
  height={300}
/>
```

### 2. `frontend/components/RouteMap.tsx`
Component cao cấp với tính năng modal mở rộng.

**Props:**
- `pickup`: Tọa độ điểm đón
- `destination`: Tọa độ điểm đến
- `pickupName`: Tên điểm đón
- `destinationName`: Tên điểm đến
- `mode`: `"compact"` (nhỏ) hoặc `"full"` (lớn)
- `expandable`: Có thể mở rộng thành modal

**Features:**
- ✅ Bản đồ compact trong ticket card
- ✅ Button mở rộng ở góc phải
- ✅ Modal fullscreen khi click mở rộng
- ✅ Click overlay để đóng modal

### 3. `frontend/components/TicketCard.tsx` (Updated)
Thêm button "Xem bản đồ" vào mỗi ticket card.

**Changes:**
- Thêm state `showMap` để toggle hiển thị bản đồ
- Thêm button "Xem bản đồ" / "Ẩn bản đồ"
- Render `<RouteMap>` khi `showMap = true`
- Thêm prop `userLocation` để hiển thị vị trí người dùng

### 4. `frontend/.env.local`
Environment variables cho Google Maps API key.

```env
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=AIzaSyDPsrz3ACDBNKd-SFA0GBF4X9IskVURaGQ
```

**Lưu ý:** 
- Prefix `NEXT_PUBLIC_` là bắt buộc để Next.js expose biến cho client-side
- File `.env.local` không được commit vào git (đã có trong `.gitignore`)

## 🚀 Cách sử dụng

### Bước 1: Lấy API Key (nếu chưa có)

1. Vào: https://console.cloud.google.com/apis/credentials
2. Click **"Create Credentials"** → **"API Key"**
3. Copy API key
4. **KHÔNG CẦN** enable billing
5. **KHÔNG CẦN** enable Geocoding/Distance Matrix APIs
6. Chỉ cần API key là đủ!

### Bước 2: Thêm API Key vào `.env.local`

Tạo file `frontend/.env.local`:
```env
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=YOUR_API_KEY_HERE
```

### Bước 3: Restart dev server

```bash
cd frontend
npm run dev
```

### Bước 4: Test

1. Mở http://localhost:3000
2. Search vé
3. Click button **"Xem bản đồ"** trong ticket card
4. Bản đồ sẽ hiển thị chỉ đường từ điểm đón đến điểm đến
5. Click icon **Maximize** để mở modal fullscreen

## 📸 Screenshots

### Ticket Card với button "Xem bản đồ"
```
┌─────────────────────────────────────┐
│ 1  Nhà xe Phương Trang              │
│    ⏱️ 08:00 → 10:30  📍 2.5 km     │
│    📍 Bến xe Miền Đông              │
│                                     │
│    [🗺️ Xem bản đồ] [📍 Google Maps]│
└─────────────────────────────────────┘
```

### Bản đồ được hiển thị
```
┌─────────────────────────────────────┐
│ 1  Nhà xe Phương Trang              │
│    ...                               │
│    ┌───────────────────────────┐   │
│    │                           │   │
│    │   [Google Maps Embed]     │   │
│    │   Chỉ đường từ A → B      │   │
│    │                      [↗️]  │   │
│    └───────────────────────────┘   │
│    [🗺️ Ẩn bản đồ] [📍 Google Maps] │
└─────────────────────────────────────┘
```

## 🔧 Customization

### Thay đổi chiều cao bản đồ

Edit `RouteMap.tsx`:
```tsx
const height = mode === "compact" ? 250 : 500; // Thay 200 → 250
```

### Thay đổi zoom level

Edit `MapEmbed.tsx` (cho mode "view"):
```tsx
embedUrl += `&zoom=12`; // Thay 10 → 12
```

### Thêm markers tùy chỉnh

Embed API không support custom markers. Để làm điều này, cần:
1. Enable billing
2. Dùng **Maps JavaScript API**
3. Implement interactive map với custom markers

## 🐛 Troubleshooting

### Lỗi: "Thiếu Google Maps API key"

**Nguyên nhân:** Biến `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` chưa được set.

**Cách sửa:**
1. Tạo file `frontend/.env.local`
2. Thêm `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=YOUR_KEY`
3. Restart dev server (`npm run dev`)

### Lỗi: "This page can't load Google Maps correctly"

**Nguyên nhân 1:** API key không hợp lệ.
- Kiểm tra API key đã copy đúng chưa
- Vào https://console.cloud.google.com/apis/credentials để verify

**Nguyên nhân 2:** API key có restrictions.
- Vào API key settings
- Ở phần "Application restrictions":
  - Chọn **"None"** (để test)
  - Hoặc thêm domain của bạn (ví dụ: `localhost:3000`)

### Bản đồ không hiển thị chỉ đường

**Nguyên nhân:** Thiếu tọa độ `pickup` hoặc `destination`.

**Cách sửa:** Backend cần trả về `pickup_lat` và `pickup_lng` trong response:
```python
# backend/app/schemas.py hoặc service.py
ticket_dict = {
    "id": "...",
    "pickup_point": "Bến xe Miền Đông",
    "pickup_lat": 10.8150,  # ✅ Thêm field này
    "pickup_lng": 106.7117, # ✅ Thêm field này
    # ...
}
```

## 📚 Tài liệu tham khảo

- Google Maps Embed API: https://developers.google.com/maps/documentation/embed
- Embed API Pricing: https://developers.google.com/maps/documentation/embed/usage-and-billing (FREE!)
- Next.js Environment Variables: https://nextjs.org/docs/basic-features/environment-variables

## 🎉 Next Steps

Nếu muốn nâng cấp lên **Interactive Map** (tương tác đầy đủ):
1. Enable billing (cần thẻ tín dụng)
2. Enable Maps JavaScript API
3. Dùng thư viện `@react-google-maps/api`
4. Implement custom markers, clustering, search box, etc.

**Ưu điểm Interactive Map:**
- ✅ Custom markers
- ✅ Click vào marker để xem thông tin
- ✅ Autocomplete search box
- ✅ Traffic layer
- ✅ Street View

**Nhược điểm:**
- ❌ Cần billing account
- ❌ Phức tạp hơn để implement
- ❌ Chi phí: $7/1000 map loads (sau 28,000 loads miễn phí/tháng)

Nhưng với **Embed API hiện tại**, bạn đã có đủ để demo và sử dụng thực tế!
