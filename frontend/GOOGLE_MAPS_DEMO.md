# 🗺️ Demo Google Maps Integration

## ✅ Đã tích hợp xong!

Hệ thống đã có:
- ✅ Google Maps Embed API (miễn phí 100%)
- ✅ Button "Xem bản đồ" trong mỗi ticket card
- ✅ Modal mở rộng bản đồ toàn màn hình
- ✅ Chỉ đường từ điểm đón đến điểm đến

## 🚀 Cách chạy

### 1. Đảm bảo đã có API key

File `frontend/.env.local` đã được tạo với API key:
```env
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=AIzaSyDPsrz3ACDBNKd-SFA0GBF4X9IskVURaGQ
```

### 2. Restart dev server

```bash
cd frontend
npm run dev
```

### 3. Mở browser

```
http://localhost:3000
```

### 4. Test workflow

1. **Search vé** với thông tin mặc định hoặc custom
2. Kết quả sẽ hiển thị danh sách tickets
3. Mỗi ticket có button **"Xem bản đồ"**
4. Click button → Bản đồ sẽ hiển thị ngay trong card
5. Click icon **Maximize** (↗️) → Modal fullscreen
6. Click overlay hoặc nút X để đóng modal

## 📸 Các tính năng

### 1. Button "Xem bản đồ" trong Ticket Card

```
┌──────────────────────────────────────┐
│ 1  Nhà xe Phương Trang               │
│    Cung cấp bởi: Vexere              │
│    250,000 VNĐ                       │
│                                      │
│    ⏱️ 08:00 → 10:30                 │
│    📍 2.5 km                         │
│                                      │
│    📍 Bến xe Miền Đông               │
│    TP. Hồ Chí Minh                   │
│                                      │
│    Điểm này gần bạn nhất: 2.5 km     │
│                                      │
│    [🗺️ Xem bản đồ]                  │
│    [📍 Google Maps] [🎫 Đặt vé]      │
└──────────────────────────────────────┘
```

### 2. Bản đồ nhúng trong card

```
┌──────────────────────────────────────┐
│ 1  Nhà xe Phương Trang               │
│    ...                               │
│                                      │
│    ┌────────────────────────────┐   │
│    │                       [↗️] │   │
│    │                            │   │
│    │   🗺️ Google Maps          │   │
│    │   Chỉ đường: A → B         │   │
│    │   - Tuyến đường màu xanh   │   │
│    │   - Markers điểm đón/đến   │   │
│    │                            │   │
│    └────────────────────────────┘   │
│                                      │
│    [🗺️ Ẩn bản đồ]                   │
│    [📍 Google Maps] [🎫 Đặt vé]      │
└──────────────────────────────────────┘
```

### 3. Modal fullscreen

Click icon ↗️ để mở modal:

```
╔══════════════════════════════════════╗
║  Chỉ đường                      [X]  ║
║  Bến xe Miền Đông → Điểm đến         ║
╠══════════════════════════════════════╣
║                                      ║
║                                      ║
║         🗺️ Google Maps              ║
║         (Fullscreen)                 ║
║                                      ║
║     - Interactive controls           ║
║     - Zoom in/out                    ║
║     - Street view                    ║
║     - Satellite mode                 ║
║                                      ║
║                                      ║
╚══════════════════════════════════════╝
```

## 🎯 Chi tiết implementation

### Components đã tạo

1. **`MapEmbed.tsx`**
   - Component cơ bản nhúng Google Maps iframe
   - Support 2 modes: `place` (địa điểm) và `directions` (chỉ đường)
   - Tự động fallback khi không có API key

2. **`RouteMap.tsx`**
   - Wrapper của MapEmbed với modal functionality
   - Toggle giữa compact và fullscreen
   - Handle click events để mở/đóng modal

3. **`TicketCard.tsx`** (Updated)
   - Thêm state `showMap` để toggle bản đồ
   - Thêm button "Xem bản đồ" / "Ẩn bản đồ"
   - Render `<RouteMap>` conditionally
   - Nhận `userLocation` từ parent để hiển thị vị trí người dùng

### Data flow

```
Page.tsx (user_location)
    ↓
ResultsList.tsx (query.user_location)
    ↓
TicketCard.tsx (userLocation prop)
    ↓
RouteMap.tsx (pickup, destination)
    ↓
MapEmbed.tsx (Google Maps Embed API)
```

## 🔧 Configuration

### Environment Variables

```env
# frontend/.env.local
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=YOUR_API_KEY_HERE
```

**Lưu ý:**
- Prefix `NEXT_PUBLIC_` bắt buộc
- Không commit file này vào git
- Restart dev server sau khi thay đổi

### Tùy chỉnh

**1. Thay đổi kích thước bản đồ:**

Edit `RouteMap.tsx`:
```tsx
const height = mode === "compact" ? 200 : 400;
// Thay đổi 200 (compact) và 400 (full)
```

**2. Thay đổi style modal:**

Edit `RouteMap.tsx` trong phần modal styles:
```tsx
style={{
  maxWidth: '900px',  // Thay đổi width
  maxHeight: '90vh',  // Thay đổi height
  borderRadius: '12px', // Thay đổi bo góc
}}
```

**3. Thêm custom markers:**

Hiện tại Embed API không support custom markers.
Để có custom markers, cần upgrade lên **Maps JavaScript API** (cần billing).

## 🐛 Troubleshooting

### Issue 1: Không thấy button "Xem bản đồ"

**Check:**
1. Component `TicketCard` đã được update chưa?
2. Import `Map` icon từ `lucide-react` chưa?
3. Restart dev server chưa?

### Issue 2: Click button nhưng không hiển thị bản đồ

**Check:**
1. Console có lỗi không?
2. File `.env.local` có tồn tại không?
3. API key đã được set đúng chưa?
4. Đã restart dev server sau khi tạo `.env.local` chưa?

### Issue 3: Bản đồ hiển thị lỗi "This page can't load Google Maps correctly"

**Nguyên nhân:**
- API key không hợp lệ
- API key có restrictions (IP, domain, ...)

**Cách sửa:**
1. Vào: https://console.cloud.google.com/apis/credentials
2. Click vào API key của bạn
3. Ở phần "Application restrictions":
   - Chọn **"None"** để test
   - Hoặc thêm `http://localhost:3000/*` vào whitelist
4. Save và đợi 1-2 phút
5. Refresh browser

### Issue 4: Backend không trả về tọa độ

**Hiện tại:** Backend chưa trả về `pickup_lat` và `pickup_lng`.

**Solution:** Có 3 cách:

**Cách 1: Fallback về user_location (đang dùng)**
```tsx
const pickupCoords = ticket.pickup_lat && ticket.pickup_lng
  ? { lat: ticket.pickup_lat, lng: ticket.pickup_lng }
  : userLocation || { lat: 10.7769, lng: 106.7009 };
```

**Cách 2: Backend trả về tọa độ (recommended)**

Update backend để trả về tọa độ:
```python
# backend/app/agent/service.py
ticket_dict = {
    "id": ticket.id,
    # ... other fields
    "pickup_lat": 10.8150,  # Add this
    "pickup_lng": 106.7117, # Add this
}
```

**Cách 3: Frontend tự geocode (không khuyến khích vì cần billing)**

## 📊 So sánh với các APIs khác

| Feature | Embed API | JavaScript API | Geocoding API |
|---------|-----------|----------------|---------------|
| Hiển thị bản đồ | ✅ Yes | ✅ Yes | ❌ No |
| Chỉ đường | ✅ Yes | ✅ Yes | ❌ No |
| Custom markers | ❌ No | ✅ Yes | ❌ No |
| Interactive | ⚠️ Limited | ✅ Full | ❌ No |
| Chi phí | ✅ Free | ⚠️ $7/1k | ⚠️ $5/1k |
| Cần billing | ❌ No | ✅ Yes | ✅ Yes |
| Use case | Display only | Full featured | Coordinates only |

**Kết luận:** Embed API là lựa chọn tốt nhất cho demo và MVP!

## 🎉 Demo checklist

- [x] Tích hợp Google Maps Embed API
- [x] Component MapEmbed
- [x] Component RouteMap
- [x] Update TicketCard với button toggle
- [x] Modal fullscreen
- [x] Environment variables
- [x] Documentation
- [ ] Backend trả về pickup coordinates (optional)
- [ ] Custom styling (optional)
- [ ] Interactive map upgrade (future)

## 📚 Resources

- [Google Maps Embed API Docs](https://developers.google.com/maps/documentation/embed)
- [Embed API Parameters](https://developers.google.com/maps/documentation/embed/embedding-map)
- [Next.js Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)

Enjoy your new maps integration! 🎉🗺️
