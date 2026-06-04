"""
Test script để kiểm tra hệ thống tìm kiếm tuyến xe generic.
Kiểm tra với cả 2 tuyến: Vũng Tàu - Sài Gòn và Hà Nội - Ninh Bình.
"""

from backend.app.agent.tools import search_routes_by_address_tool
from backend.app.agent.route_search import (
    load_route_config,
    detect_route_from_addresses,
    get_all_operators_info,
)


def test_route_config():
    """Test 1: Kiểm tra load route config."""
    print("=" * 80)
    print("TEST 1: Load Route Config")
    print("=" * 80)
    
    try:
        config = load_route_config()
        print(f"✅ Loaded {len(config['routes'])} routes:")
        for route in config["routes"]:
            print(f"  - {route['name']} (ID: {route['id']})")
            print(f"    File: {route['data_file']}")
            print(f"    Cities: {', '.join(route['cities'][:3])}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def test_route_detection():
    """Test 2: Kiểm tra auto-detect tuyến."""
    print("=" * 80)
    print("TEST 2: Auto-Detect Route")
    print("=" * 80)
    
    test_cases = [
        ("Vũng Tàu", "Sài Gòn", "vungtau_saigon"),
        ("Bà Rịa", "Quận 1 TP.HCM", "vungtau_saigon"),
        ("Hà Nội", "Ninh Bình", "hanoi_ninhbinh"),
        ("Cầu Giấy", "Tam Cốc", "hanoi_ninhbinh"),
        ("Random Place 1", "Random Place 2", None),
    ]
    
    for pickup, dropoff, expected in test_cases:
        detected = detect_route_from_addresses(pickup, dropoff)
        status = "✅" if detected == expected else "❌"
        print(f"{status} {pickup} → {dropoff}: {detected} (expected: {expected})")
    
    print()


def test_list_all_operators():
    """Test 3: Liệt kê tất cả nhà xe."""
    print("=" * 80)
    print("TEST 3: List All Operators")
    print("=" * 80)
    
    try:
        result = get_all_operators_info()
        print(result)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def test_vungtau_saigon_route():
    """Test 4: Tìm tuyến Vũng Tàu - Sài Gòn."""
    print("=" * 80)
    print("TEST 4: Search Vũng Tàu - Sài Gòn Route")
    print("=" * 80)
    
    try:
        # Test với auto-detect
        result = search_routes_by_address_tool(
            pickup_address="Bà Rịa",
            dropoff_address="Quận 1 Sài Gòn",
        )
        print(result)
        print()
        
        # Test với explicit route_id
        result2 = search_routes_by_address_tool(
            pickup_address="Vũng Tàu",
            dropoff_address="Sân bay Tân Sơn Nhất",
            route_id="vungtau_saigon",
        )
        print(result2)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()


def test_hanoi_ninhbinh_route():
    """Test 5: Tìm tuyến Hà Nội - Ninh Bình."""
    print("=" * 80)
    print("TEST 5: Search Hà Nội - Ninh Bình Route")
    print("=" * 80)
    
    try:
        # Test với auto-detect
        result = search_routes_by_address_tool(
            pickup_address="Cầu Giấy, Hà Nội",
            dropoff_address="Tràng An, Ninh Bình",
        )
        print(result)
        print()
        
        # Test với explicit route_id
        result2 = search_routes_by_address_tool(
            pickup_address="Sân bay Nội Bài",
            dropoff_address="Tam Cốc",
            route_id="hanoi_ninhbinh",
        )
        print(result2)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()


def test_operators_by_route():
    """Test 6: Liệt kê nhà xe theo tuyến."""
    print("=" * 80)
    print("TEST 6: List Operators by Route")
    print("=" * 80)
    
    # Test Vũng Tàu - Sài Gòn
    print("📍 TUYẾN: VŨNG TÀU - SÀI GÒN")
    print("-" * 80)
    try:
        result = get_all_operators_info(route_id="vungtau_saigon")
        print(result)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test Hà Nội - Ninh Bình
    print("📍 TUYẾN: HÀ NỘI - NINH BÌNH")
    print("-" * 80)
    try:
        result = get_all_operators_info(route_id="hanoi_ninhbinh")
        print(result)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


if __name__ == "__main__":
    print("\n")
    print("🚀 GENERIC ROUTE SEARCH SYSTEM TEST")
    print("=" * 80)
    print()
    
    # Chạy tất cả tests
    test_route_config()
    test_route_detection()
    test_list_all_operators()
    test_operators_by_route()
    test_vungtau_saigon_route()
    test_hanoi_ninhbinh_route()
    
    print("=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
