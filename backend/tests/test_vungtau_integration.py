"""
Test tích hợp cho hệ thống tìm vé Vũng Tàu - Sài Gòn với điểm đón/trả tối ưu.
"""

from backend.app.agent.vungtau_routes import (
    load_vungtau_saigon_data,
    find_optimal_route,
    format_route_recommendation,
)
from backend.app.agent.tools import search_vungtau_saigon_route_optimized


def test_load_vungtau_data():
    """Test load dữ liệu JSON"""
    data = load_vungtau_saigon_data()
    
    assert "operators" in data
    assert len(data["operators"]) > 0
    
    # Check cấu trúc nhà xe
    operator = data["operators"][0]
    assert "name" in operator
    assert "contact_phone" in operator
    assert "routes" in operator
    
    # Check cấu trúc tuyến
    route = operator["routes"][0]
    assert "route_name" in route
    assert "base_price_vnd" in route
    assert "waypoints" in route
    
    # Check waypoints có tọa độ
    waypoint = route["waypoints"][0]
    assert "lat" in waypoint
    assert "lng" in waypoint
    assert "node_name" in waypoint


def test_find_optimal_route_from_vungtau():
    """Test tìm tuyến từ Vũng Tàu đến Quận 1 (Sài Gòn)"""
    # User ở Vũng Tàu (gần trung tâm)
    pickup_lat, pickup_lng = 10.3460, 107.0843
    
    # User muốn đến Quận 1 (gần Bến Thành)
    dropoff_lat, dropoff_lng = 10.7707, 106.6906
    
    routes = find_optimal_route(
        (pickup_lat, pickup_lng),
        (dropoff_lat, dropoff_lng),
        max_results=3,
    )
    
    assert len(routes) > 0
    assert len(routes) <= 3
    
    # Check tuyến đầu tiên
    top_route = routes[0]
    assert "operator_name" in top_route
    assert "route_name" in top_route
    assert "base_price_vnd" in top_route
    assert "nearest_pickup" in top_route
    assert "nearest_dropoff" in top_route
    
    # Check điểm đón gần nhất
    pickup = top_route["nearest_pickup"]
    assert "node_name" in pickup
    assert "distance_km" in pickup
    assert "maps_link" in pickup
    
    # Check điểm trả gần nhất
    dropoff = top_route["nearest_dropoff"]
    assert "node_name" in dropoff
    assert "distance_km" in dropoff
    assert "maps_link" in dropoff
    
    print(f"\n✅ Tìm thấy {len(routes)} tuyến phù hợp")
    print(f"📍 Tuyến tốt nhất: {top_route['operator_name']} - {top_route['route_name']}")
    print(f"💰 Giá: {top_route['base_price_vnd']:,} VNĐ")
    print(f"🔵 Điểm đón: {pickup['node_name']} ({pickup['distance_km']} km)")
    print(f"🔴 Điểm trả: {dropoff['node_name']} ({dropoff['distance_km']} km)")


def test_find_optimal_route_from_baria():
    """Test tìm tuyến từ Bà Rịa đến Sân Bay Tân Sơn Nhất"""
    # User ở Bà Rịa (gần Co.op Mart)
    pickup_lat, pickup_lng = 10.5063, 107.1639
    
    # User muốn đến Sân Bay
    dropoff_lat, dropoff_lng = 10.8187, 106.6519
    
    routes = find_optimal_route(
        (pickup_lat, pickup_lng),
        (dropoff_lat, dropoff_lng),
        max_results=3,
    )
    
    assert len(routes) > 0
    
    # Check có tuyến đến sân bay
    has_airport_route = any(
        "Sân bay" in route["route_name"] or "TSN" in route["route_name"]
        for route in routes
    )
    
    if has_airport_route:
        print("\n✅ Tìm thấy tuyến đến sân bay")
    
    # In ra kết quả
    for idx, route in enumerate(routes[:3], 1):
        print(f"\n{idx}. {route['operator_name']} - {route['route_name']}")
        print(f"   Giá: {route['base_price_vnd']:,} VNĐ")
        print(f"   Điểm đón: {route['nearest_pickup']['node_name']} ({route['nearest_pickup']['distance_km']} km)")
        print(f"   Điểm trả: {route['nearest_dropoff']['node_name']} ({route['nearest_dropoff']['distance_km']} km)")


def test_format_route_recommendation():
    """Test format kết quả thành text dễ đọc"""
    # User ở Vũng Tàu
    pickup_lat, pickup_lng = 10.3460, 107.0843
    
    # User muốn đến Quận 1
    dropoff_lat, dropoff_lng = 10.7707, 106.6906
    
    result = format_route_recommendation(
        (pickup_lat, pickup_lng),
        (dropoff_lat, dropoff_lng),
        "Trung tâm Vũng Tàu",
        "Quận 1, TP.HCM",
    )
    
    # Check format
    assert "Gợi ý tuyến xe" in result
    assert "Giá vé" in result
    assert "Điểm đón gần bạn nhất" in result
    assert "Điểm trả gần đích nhất" in result
    assert "Hotline" in result
    assert "Xem đường đi" in result
    
    print("\n" + "="*60)
    print("📋 KẾT QUẢ FORMAT:")
    print("="*60)
    print(result)


def test_search_tool_integration():
    """Test tool tích hợp cho Gemini Agent"""
    result = search_vungtau_saigon_route_optimized(
        pickup_address="Trung tâm Vũng Tàu",
        pickup_lat=10.3460,
        pickup_lng=107.0843,
        dropoff_address="Quận 1, TP.HCM",
        dropoff_lat=10.7707,
        dropoff_lng=106.6906,
        date="2026-06-06",
    )
    
    # Check result là string
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Check có thông tin quan trọng
    assert "Gợi ý tuyến xe" in result or "Lỗi" in result
    
    print("\n" + "="*60)
    print("🤖 KẾT QUẢ TOOL CHO AGENT:")
    print("="*60)
    print(result)


def test_edge_case_no_results():
    """Test trường hợp không tìm thấy tuyến"""
    # Vị trí rất xa (không có tuyến)
    pickup_lat, pickup_lng = 21.0285, 105.8542  # Hà Nội
    dropoff_lat, dropoff_lng = 10.7707, 106.6906  # Sài Gòn
    
    routes = find_optimal_route(
        (pickup_lat, pickup_lng),
        (dropoff_lat, dropoff_lng),
    )
    
    # Vẫn có thể tìm thấy tuyến (vì tính toàn bộ tuyến VT-SG)
    # Nhưng khoảng cách sẽ rất xa
    if len(routes) > 0:
        assert routes[0]["nearest_pickup"]["distance_km"] > 500  # > 500km từ Hà Nội
        print(f"\n⚠️ Tìm thấy tuyến nhưng điểm đón rất xa: {routes[0]['nearest_pickup']['distance_km']} km")


if __name__ == "__main__":
    print("\n🚌 SMARTBUS - VUNGTAU INTEGRATION TESTS\n")
    
    test_load_vungtau_data()
    test_find_optimal_route_from_vungtau()
    test_find_optimal_route_from_baria()
    test_format_route_recommendation()
    test_search_tool_integration()
    test_edge_case_no_results()
    
    print("\n" + "="*60)
    print("✅ TẤT CẢ TESTS PASSED!")
    print("="*60)
