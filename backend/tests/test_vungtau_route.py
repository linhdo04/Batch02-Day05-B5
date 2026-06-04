"""
Demo script để test tìm kiếm tuyến Vũng Tàu - Sài Gòn với dữ liệu thực.
"""

from backend.app.agent.vungtau_routes import (
    search_route_by_location_tool,
    get_all_operators_info,
    find_optimal_route,
)


def demo_1_list_all_operators():
    """Demo 1: Liệt kê tất cả nhà xe"""
    print("=" * 80)
    print("DEMO 1: LIỆT KÊ TẤT CẢ NHÀ XE TUYẾN VŨNG TÀU - SÀI GÒN")
    print("=" * 80)
    
    result = get_all_operators_info()
    print(result)
    print()


def demo_2_search_from_baria_to_airport():
    """Demo 2: Tìm xe từ Bà Rịa đến Sân Bay Tân Sơn Nhất"""
    print("=" * 80)
    print("DEMO 2: TÌM XE TỪ BÀ RỊA ĐẾN SÂN BAY TÂN SƠN NHẤT")
    print("=" * 80)
    
    # Tọa độ Bà Rịa (Co.op Mart)
    pickup_lat = 10.5063
    pickup_lng = 107.1639
    
    # Tọa độ Sân Bay Tân Sơn Nhất
    dropoff_lat = 10.8187
    dropoff_lng = 106.6519
    
    result = search_route_by_location_tool(
        pickup_lat=pickup_lat,
        pickup_lng=pickup_lng,
        dropoff_lat=dropoff_lat,
        dropoff_lng=dropoff_lng,
        pickup_address="Co.op Mart Bà Rịa",
        dropoff_address="Sân Bay Tân Sơn Nhất",
    )
    
    print(result)
    print()


def demo_3_search_from_vungtau_to_quan1():
    """Demo 3: Tìm xe từ Vũng Tàu (trung tâm) đến Quận 1"""
    print("=" * 80)
    print("DEMO 3: TÌM XE TỪ VŨNG TÀU (TRUNG TÂM) ĐẾN QUẬN 1")
    print("=" * 80)
    
    # Tọa độ trung tâm Vũng Tàu
    pickup_lat = 10.3460
    pickup_lng = 107.0843
    
    # Tọa độ Quận 1 (Nguyễn Thái Bình)
    dropoff_lat = 10.7707
    dropoff_lng = 106.6906
    
    result = search_route_by_location_tool(
        pickup_lat=pickup_lat,
        pickup_lng=pickup_lng,
        dropoff_lat=dropoff_lat,
        dropoff_lng=dropoff_lng,
        pickup_address="Trung tâm Vũng Tàu",
        dropoff_address="Quận 1, TP.HCM",
    )
    
    print(result)
    print()


def demo_4_search_from_vungtau_to_quan9():
    """Demo 4: Tìm xe từ Vũng Tàu đến Quận 9 (Khu Công Nghệ Cao)"""
    print("=" * 80)
    print("DEMO 4: TÌM XE TỪ VŨNG TÀU ĐẾN QUẬN 9 (KHU CÔNG NGHỆ CAO)")
    print("=" * 80)
    
    # Tọa độ Vũng Tàu
    pickup_lat = 10.3460
    pickup_lng = 107.0843
    
    # Tọa độ Khu Công Nghệ Cao Quận 9
    dropoff_lat = 10.8500
    dropoff_lng = 106.7800
    
    result = search_route_by_location_tool(
        pickup_lat=pickup_lat,
        pickup_lng=pickup_lng,
        dropoff_lat=dropoff_lat,
        dropoff_lng=dropoff_lng,
        pickup_address="Vũng Tàu",
        dropoff_address="Khu Công Nghệ Cao, Quận 9",
    )
    
    print(result)
    print()


def demo_5_raw_search():
    """Demo 5: Xem dữ liệu thô trả về từ find_optimal_route"""
    print("=" * 80)
    print("DEMO 5: DỮ LIỆU THÔ TRẢ VỀ (JSON FORMAT)")
    print("=" * 80)
    
    pickup_lat = 10.5063
    pickup_lng = 107.1639
    dropoff_lat = 10.8187
    dropoff_lng = 106.6519
    
    routes = find_optimal_route(
        (pickup_lat, pickup_lng),
        (dropoff_lat, dropoff_lng),
        max_results=2,
    )
    
    import json
    print(json.dumps(routes, indent=2, ensure_ascii=False))
    print()


if __name__ == "__main__":
    print("\n" + "🚌" * 40)
    print("DEMO HỆ THỐNG TÌM KIẾM TUYẾN XE VŨNG TÀU - SÀI GÒN")
    print("🚌" * 40 + "\n")
    
    try:
        demo_1_list_all_operators()
        demo_2_search_from_baria_to_airport()
        demo_3_search_from_vungtau_to_quan1()
        demo_4_search_from_vungtau_to_quan9()
        demo_5_raw_search()
        
        print("=" * 80)
        print("✅ HOÀN THÀNH TẤT CẢ DEMO!")
        print("=" * 80)
        print("\n💡 LƯU Ý:")
        print("   - Tất cả khoảng cách được tính bằng công thức Haversine (không cần API key)")
        print("   - Link Google Maps được tạo tự động để dẫn đường")
        print("   - Hệ thống tự động chọn điểm đón/trả gần nhất cho user")
        print("\n📚 ĐỂ TÍCH HỢP VÀO FRONTEND:")
        print("   - Agent có thể gọi search_route_by_location_tool() với lat/lng của user")
        print("   - Frontend nhận text markdown và hiển thị cho user")
        print("   - User có thể click vào link Maps để xem đường đi")
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
