"""
Test Google Maps API với API key thật.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.app.agent.tools import (
    geocode_address,
    calculate_distance_google_maps,
)


def test_geocoding_with_api():
    """Test geocoding với Google Maps API"""
    print("=" * 80)
    print("TEST 1: GEOCODING VỚI GOOGLE MAPS API")
    print("=" * 80)
    
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    print(f"✅ API Key loaded: {api_key[:20]}..." if api_key else "❌ No API key")
    print()
    
    # Test các địa chỉ
    addresses = [
        "Bà Rịa, Bà Rịa - Vũng Tàu, Việt Nam",
        "Vũng Tàu, Bà Rịa - Vũng Tàu, Việt Nam",
        "Sân bay Tân Sơn Nhất, TP.HCM, Việt Nam",
        "Quận 1, TP.HCM, Việt Nam",
    ]
    
    for addr in addresses:
        result = geocode_address(addr)
        print(f"📍 {addr}")
        print(f"   → Tọa độ: {result['lat']}, {result['lng']}")
        print(f"   → Địa chỉ: {result['formatted_address']}")
        print(f"   → Phương thức: {result['method']}")
        if result['error']:
            print(f"   ⚠️  Lưu ý: {result['error']}")
        print()


def test_distance_calculation_with_api():
    """Test tính khoảng cách với Google Maps API"""
    print("=" * 80)
    print("TEST 2: TÍNH KHOẢNG CÁCH VỚI GOOGLE MAPS API")
    print("=" * 80)
    print()
    
    # Test case 1: Bà Rịa → Sân bay TSN
    print("🚗 Test Case 1: Bà Rịa → Sân bay Tân Sơn Nhất")
    result1 = calculate_distance_google_maps(
        origin_lat=10.5063,
        origin_lng=107.1639,
        dest_lat=10.8187,
        dest_lng=106.6519,
        origin_address="Bà Rịa",
        dest_address="Sân bay TSN"
    )
    
    print(f"   ✅ Khoảng cách: {result1['distance_text']}")
    print(f"   ✅ Thời gian: {result1['duration_text']}")
    print(f"   ✅ Phương thức: {result1['method']}")
    print(f"   🗺️  Link: {result1['maps_link'][:80]}...")
    print()
    
    # Test case 2: Vũng Tàu → Quận 1
    print("🚗 Test Case 2: Vũng Tàu → Quận 1")
    result2 = calculate_distance_google_maps(
        origin_lat=10.3460,
        origin_lng=107.0843,
        dest_lat=10.7707,
        dest_lng=106.6906,
        origin_address="Vũng Tàu",
        dest_address="Quận 1"
    )
    
    print(f"   ✅ Khoảng cách: {result2['distance_text']}")
    print(f"   ✅ Thời gian: {result2['duration_text']}")
    print(f"   ✅ Phương thức: {result2['method']}")
    print(f"   🗺️  Link: {result2['maps_link'][:80]}...")
    print()


def test_comparison_api_vs_haversine():
    """So sánh kết quả giữa Google Maps API và Haversine"""
    print("=" * 80)
    print("TEST 3: SO SÁNH GOOGLE MAPS API vs HAVERSINE")
    print("=" * 80)
    print()
    
    from backend.app.agent.tools import _haversine_distance
    
    # Bà Rịa → Sân bay
    origin_lat, origin_lng = 10.5063, 107.1639
    dest_lat, dest_lng = 10.8187, 106.6519
    
    # Tính bằng API
    api_result = calculate_distance_google_maps(
        origin_lat, origin_lng, dest_lat, dest_lng
    )
    
    # Tính bằng Haversine
    haversine_km = _haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
    
    print("📊 Kết quả:")
    print(f"   Google Maps API: {api_result['distance_km']} km ({api_result['distance_text']})")
    print(f"   Haversine:       {haversine_km:.2f} km")
    print(f"   Chênh lệch:      {abs(api_result['distance_km'] - haversine_km):.2f} km")
    print()
    
    if api_result['method'] == 'google_maps_api':
        print("   ✅ Google Maps API đang hoạt động!")
        print(f"   ⏱️  Thời gian di chuyển: {api_result['duration_text']}")
    else:
        print("   ⚠️  Đang dùng Haversine fallback (không có API key hoặc API lỗi)")
    print()


def main():
    """Run all tests"""
    print("\n" + "🔑" * 40)
    print("TEST GOOGLE MAPS API")
    print("🔑" * 40 + "\n")
    
    try:
        # Test 1: Geocoding
        test_geocoding_with_api()
        
        # Test 2: Distance calculation
        test_distance_calculation_with_api()
        
        # Test 3: Comparison
        test_comparison_api_vs_haversine()
        
        print("=" * 80)
        print("✅ HOÀN THÀNH TẤT CẢ TESTS!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
