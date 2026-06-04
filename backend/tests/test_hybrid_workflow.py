"""
Demo workflow HYBRID: Search API first → Enrich with waypoints
"""

import json
from backend.app.agent.vungtau_routes import enrich_search_results_with_waypoints_tool


def demo_1_mock_search_api():
    """Demo 1: Giả lập kết quả từ search API"""
    print("=" * 80)
    print("DEMO 1: GIẢLẬP KẾT QUẢ TỪ SEARCH API")
    print("=" * 80)
    
    # Giả sử đây là kết quả từ search API (có thể từ Vexere, scraping, hoặc mock data)
    search_results = [
        {
            "id": "ticket-001",
            "operator": "Toàn Thắng Limousine",
            "route": "Vũng Tàu - Sân Bay Tân Sơn Nhất",
            "price": 200000,
            "departure": "08:00",
            "arrival": "10:30",
        },
        {
            "id": "ticket-002",
            "operator": "Hoa Mai Limousine",
            "route": "Vũng Tàu - Quận 1",
            "price": 200000,
            "departure": "09:00",
            "arrival": "11:15",
        },
        {
            "id": "ticket-003",
            "operator": "Vie Limousine",
            "route": "Vũng Tàu - Quận 1",
            "price": 220000,
            "departure": "10:00",
            "arrival": "12:15",
        },
    ]
    
    print("✅ Kết quả từ search API (hoặc scraping Vexere):")
    print(json.dumps(search_results, indent=2, ensure_ascii=False))
    print()
    
    return search_results


def demo_2_enrich_with_waypoints():
    """Demo 2: Enrich kết quả search với waypoints"""
    print("=" * 80)
    print("DEMO 2: ENRICH VỚI THÔNG TIN ĐIỂM ĐÓN/TRẢ TỪ DATABASE")
    print("=" * 80)
    
    # Bước 1: Lấy kết quả từ search API
    search_results = demo_1_mock_search_api()
    
    # Bước 2: Enrich với waypoints
    print("\n🔧 Đang enrich với thông tin điểm đón/trả từ database JSON...")
    print()
    
    tickets_json = json.dumps(search_results)
    
    enriched_result = enrich_search_results_with_waypoints_tool(
        tickets_json=tickets_json,
        user_pickup_address="Bà Rịa",
        user_dropoff_address="Sân bay Tân Sơn Nhất",
    )
    
    print(enriched_result)


def demo_3_different_route():
    """Demo 3: Test với tuyến khác"""
    print("\n" + "=" * 80)
    print("DEMO 3: TEST VỚI TUYẾN VŨNG TÀU → QUẬN 1")
    print("=" * 80)
    
    search_results = [
        {
            "operator": "Hoa Mai Limousine",
            "route": "Vũng Tàu - Quận 1 (Cao Tốc)",
            "price": 200000,
        },
        {
            "operator": "Vie Limousine",
            "route": "Vũng Tàu - Quận 1 (Ghế Massage)",
            "price": 220000,
        },
    ]
    
    tickets_json = json.dumps(search_results)
    
    enriched_result = enrich_search_results_with_waypoints_tool(
        tickets_json=tickets_json,
        user_pickup_address="Vũng Tàu",
        user_dropoff_address="Quận 1",
    )
    
    print(enriched_result)


def demo_4_workflow_explanation():
    """Demo 4: Giải thích workflow"""
    print("\n" + "=" * 80)
    print("DEMO 4: WORKFLOW HOÀN CHỈNH")
    print("=" * 80)
    
    workflow = """
    
    🎯 WORKFLOW HYBRID (RECOMMENDED):
    
    ┌─────────────────────────────────────────┐
    │  BƯỚC 1: TÌM VÉ (Search API/Mock)      │
    │  - Agent gọi search_and_format_tickets() │
    │  - Hoặc scrape từ Vexere API            │
    │  - Kết quả: List vé với tên nhà xe     │
    └─────────────────┬───────────────────────┘
                      │
                      ▼
    ┌─────────────────────────────────────────┐
    │  BƯỚC 2: LỌC TÊN NHÀ XE & TUYẾN        │
    │  - Operator: "Toàn Thắng Limousine"     │
    │  - Route: "Vũng Tàu - Sân Bay TSN"     │
    └─────────────────┬───────────────────────┘
                      │
                      ▼
    ┌─────────────────────────────────────────┐
    │  BƯỚC 3: MATCH VỚI DATABASE JSON        │
    │  - Tìm trong vungtau_saigon.json        │
    │  - Match operator.name                  │
    │  - Match route.route_name               │
    └─────────────────┬───────────────────────┘
                      │
                      ▼
    ┌─────────────────────────────────────────┐
    │  BƯỚC 4: LẤY WAYPOINTS                  │
    │  - Pickup points: List điểm đón         │
    │  - Dropoff points: List điểm trả        │
    │  - Mỗi point có: lat, lng, name         │
    └─────────────────┬───────────────────────┘
                      │
                      ▼
    ┌─────────────────────────────────────────┐
    │  BƯỚC 5: TÍNH KHOẢNG CÁCH              │
    │  - User location → All pickup points    │
    │  - All dropoff points → Destination     │
    │  - Dùng Haversine (không cần API)      │
    └─────────────────┬───────────────────────┘
                      │
                      ▼
    ┌─────────────────────────────────────────┐
    │  BƯỚC 6: ENRICH & RETURN               │
    │  - Vé + Điểm đón gần nhất              │
    │  - Vé + Điểm trả gần đích nhất         │
    │  - Kèm link Google Maps                │
    └─────────────────────────────────────────┘
    
    
    ✅ ƯU ĐIỂM:
    - Tận dụng được search API có sẵn (Vexere, scraping)
    - Database JSON chỉ cần lưu waypoints (nhẹ hơn)
    - Linh hoạt: Có thể thêm nhiều nhà xe khác
    - Không phụ thuộc hoàn toàn vào JSON database
    
    📚 TOOLS CẦN THIẾT:
    1. search_and_format_tickets() - Tìm vé (đã có)
    2. enrich_search_results_with_waypoints_tool() - Enrich waypoints (MỚI)
    3. geocode_address() - Chuyển địa chỉ → tọa độ (đã có)
    4. calculate_distance_google_maps() - Tính khoảng cách (đã có)
    
    """
    
    print(workflow)


if __name__ == "__main__":
    print("\n" + "🔄" * 40)
    print("DEMO WORKFLOW HYBRID: SEARCH FIRST → ENRICH WITH WAYPOINTS")
    print("🔄" * 40 + "\n")
    
    try:
        # Demo 1: Show raw search results
        print()
        
        # Demo 2: Enrich với waypoints
        demo_2_enrich_with_waypoints()
        
        # Demo 3: Test với tuyến khác
        demo_3_different_route()
        
        # Demo 4: Giải thích workflow
        demo_4_workflow_explanation()
        
        print("=" * 80)
        print("✅ HOÀN THÀNH TẤT CẢ DEMO!")
        print("=" * 80)
        print("\n🎯 KẾT LUẬN:")
        print("   Workflow HYBRID cho phép:")
        print("   1. Tìm vé từ nhiều nguồn (API, scraping, mock)")
        print("   2. Enrich với thông tin chi tiết từ database JSON")
        print("   3. Tính khoảng cách động dựa trên vị trí user")
        print("   4. Không cần Google Maps API key!")
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
