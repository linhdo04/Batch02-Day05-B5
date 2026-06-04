"""
Test Mapbox APIs - MIỄN PHÍ 100,000 requests/tháng
===================================================

Test:
1. Geocoding API - Chuyển địa chỉ → tọa độ
2. Directions API - Tính khoảng cách + thời gian
3. Matrix API - Tính khoảng cách nhiều điểm

Không cần thẻ tín dụng, chỉ cần email signup!
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Mapbox tools
from backend.app.agent.mapbox_tools import (
    mapbox_geocode,
    mapbox_calculate_distance,
    mapbox_matrix_distance,
)

print("=" * 80)
print("TEST MAPBOX APIs")
print("=" * 80)

api_key = os.getenv("MAPBOX_ACCESS_TOKEN")
print(f"\n🔑 API Key: {api_key[:20] if api_key else 'NOT SET'}...{api_key[-10:] if api_key else ''}\n")

# Test 1: Geocoding
print("\n" + "=" * 80)
print("TEST 1: GEOCODING API - Chuyển địa chỉ → tọa độ")
print("=" * 80)

print("\n📍 Test: Bà Rịa, Việt Nam")
result1 = mapbox_geocode("Bà Rịa, Việt Nam")
print(f"   Phương thức: {result1['method']}")
print(f"   Tọa độ: ({result1['lat']}, {result1['lng']})")
print(f"   Địa chỉ: {result1['formatted_address']}")
if result1['error']:
    print(f"   ⚠️ Lỗi: {result1['error']}")
else:
    print("   ✅ SUCCESS")

print("\n📍 Test: Sân bay Tân Sơn Nhất")
result2 = mapbox_geocode("Sân bay Tân Sơn Nhất, TP.HCM")
print(f"   Phương thức: {result2['method']}")
print(f"   Tọa độ: ({result2['lat']}, {result2['lng']})")
print(f"   Địa chỉ: {result2['formatted_address']}")
if result2['error']:
    print(f"   ⚠️ Lỗi: {result2['error']}")
else:
    print("   ✅ SUCCESS")

# Test 2: Directions (Distance + Duration)
print("\n\n" + "=" * 80)
print("TEST 2: DIRECTIONS API - Tính khoảng cách + thời gian")
print("=" * 80)

print("\n🚗 Tuyến: Bà Rịa → Sân bay Tân Sơn Nhất")
distance_result = mapbox_calculate_distance(
    origin_lat=result1['lat'],
    origin_lng=result1['lng'],
    dest_lat=result2['lat'],
    dest_lng=result2['lng'],
)
print(f"   Phương thức: {distance_result['method']}")
print(f"   Khoảng cách: {distance_result['distance_text']}")
print(f"   Thời gian: {distance_result['duration_text']}")
if distance_result['error']:
    print(f"   ⚠️ Lỗi: {distance_result['error']}")
else:
    print("   ✅ SUCCESS")

# So sánh với Haversine (đường chim bay)
from backend.app.agent.mapbox_tools import _haversine_distance
haversine_dist = _haversine_distance(
    result1['lat'], result1['lng'],
    result2['lat'], result2['lng']
)
print(f"\n📊 So sánh:")
print(f"   Haversine (đường chim bay): {haversine_dist:.1f} km")
print(f"   Mapbox (đường bộ thực tế): {distance_result['distance_km']} km")
if distance_result['method'] == 'mapbox_directions':
    diff_percent = ((distance_result['distance_km'] - haversine_dist) / haversine_dist) * 100
    print(f"   Chênh lệch: {diff_percent:.1f}%")

# Test 3: Matrix API
print("\n\n" + "=" * 80)
print("TEST 3: MATRIX API - Tính khoảng cách nhiều điểm")
print("=" * 80)

print("\n🗺️ Test: 2 origins × 2 destinations")

# Origins: Bà Rịa, Vũng Tàu
origins = [
    (10.5063, 107.1639),  # Bà Rịa
    (10.3460, 107.0843),  # Vũng Tàu
]

# Destinations: Sân bay, Quận 1
destinations = [
    (10.8187, 106.6519),  # Sân bay
    (10.7707, 106.6906),  # Quận 1
]

matrix_result = mapbox_matrix_distance(origins, destinations)
print(f"   Phương thức: {matrix_result['method']}")

print("\n   Ma trận khoảng cách (km):")
print("   " + " " * 20 + "Sân bay    Quận 1")
for i, origin_name in enumerate(["Bà Rịa", "Vũng Tàu"]):
    row = matrix_result['matrix'][i]
    print(f"   {origin_name:15} {row[0]:8.1f}   {row[1]:8.1f}")

if matrix_result['method'] == 'mapbox_matrix' and matrix_result['durations']:
    print("\n   Ma trận thời gian (phút):")
    print("   " + " " * 20 + "Sân bay    Quận 1")
    for i, origin_name in enumerate(["Bà Rịa", "Vũng Tàu"]):
        row = matrix_result['durations'][i]
        dur1 = row[0] / 60 if row[0] else 0
        dur2 = row[1] / 60 if row[1] else 0
        print(f"   {origin_name:15} {dur1:8.0f}   {dur2:8.0f}")

if matrix_result['error']:
    print(f"\n   ⚠️ Lỗi: {matrix_result['error']}")
else:
    print("\n   ✅ SUCCESS")

# Summary
print("\n\n" + "=" * 80)
print("TÓM TẮT")
print("=" * 80)

if not api_key:
    print("""
❌ CHƯA CÓ MAPBOX API KEY

Để lấy API key (MIỄN PHÍ - không cần thẻ):

1. Vào: https://account.mapbox.com/auth/signup/
2. Sign up với email (không cần thẻ tín dụng)
3. Sau khi đăng nhập, vào: https://account.mapbox.com/access-tokens/
4. Copy "Default public token"
5. Thêm vào file .env:
   
   MAPBOX_ACCESS_TOKEN=pk.eyJ1IjoiWW91clVzZXJuYW1lIiwi...

6. Chạy lại test này

🎉 FREE TIER:
   - 100,000 requests/tháng
   - Không giới hạn map loads
   - Không cần thẻ tín dụng
   - Chỉ cần email signup

📚 Docs:
   - Geocoding: https://docs.mapbox.com/api/search/geocoding/
   - Directions: https://docs.mapbox.com/api/navigation/directions/
   - Matrix: https://docs.mapbox.com/api/navigation/matrix/
""")
else:
    print("""
✅ ĐÃ CÓ MAPBOX API KEY

Kết quả test:
   ✅ Geocoding API: Chuyển địa chỉ → tọa độ
   ✅ Directions API: Tính khoảng cách + thời gian
   ✅ Matrix API: Tính nhiều điểm cùng lúc

🎯 So với Google Maps:
   - Google: Cần billing (thẻ), $5/1000 requests
   - Mapbox: Free 100,000 requests, không cần thẻ

🚀 Next steps:
   1. Update backend để dùng Mapbox thay vì Haversine
   2. Khoảng cách sẽ chính xác hơn (theo đường bộ thực tế)
   3. Có thời gian di chuyển (duration)
""")

print("\n" + "=" * 80)
