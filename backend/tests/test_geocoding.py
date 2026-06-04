"""
Demo script để test geocoding và tìm tuyến xe từ địa chỉ text.
"""

from backend.app.agent.tools import (
    geocode_address,
    geocode_address_tool,
    search_vungtau_routes_by_address_tool,
)


def demo_1_geocode_addresses():
    """Demo 1: Test geocoding với nhiều địa chỉ"""
    print("=" * 80)
    print("DEMO 1: GEOCODING - CHUYỂN ĐỊA CHỈ THÀNH TỌA ĐỘ")
    print("=" * 80)
    
    addresses = [
        "Bà Rịa",
        "Vũng Tàu",
        "Quận 1, TP.HCM",
        "Sân bay Tân Sơn Nhất",
        "Quận 9, TP.HCM",
        "Co.op Mart Bà Rịa",
    ]
    
    for addr in addresses:
        result = geocode_address(addr)
        print(f"\n📍 {addr}")
        print(f"   → Tọa độ: ({result['lat']}, {result['lng']})")
        print(f"   → Địa chỉ đầy đủ: {result['formatted_address']}")
        print(f"   → Phương thức: {result['method']}")
        if result['error']:
            print(f"   ⚠️  {result['error']}")
    
    print()


def demo_2_geocode_tool_for_agent():
    """Demo 2: Test tool dành cho Gemini Agent"""
    print("=" * 80)
    print("DEMO 2: GEOCODE TOOL CHO GEMINI AGENT")
    print("=" * 80)
    
    print("\n📍 Test với địa chỉ: 'Bà Rịa'")
    print(geocode_address_tool("Bà Rịa"))
    
    print("\n📍 Test với địa chỉ: 'Quận 1 Sài Gòn'")
    print(geocode_address_tool("Quận 1 Sài Gòn"))
    
    print()


def demo_3_search_routes_from_text():
    """Demo 3: Tìm tuyến xe trực tiếp từ địa chỉ text"""
    print("=" * 80)
    print("DEMO 3: TÌM TUYẾN XE TỪ ĐỊA CHỈ TEXT (ALL-IN-ONE TOOL)")
    print("=" * 80)
    
    print("\n🔍 Tìm xe từ 'Bà Rịa' đến 'Sân bay Tân Sơn Nhất':\n")
    result = search_vungtau_routes_by_address_tool(
        pickup_address="Bà Rịa",
        dropoff_address="Sân bay Tân Sơn Nhất",
    )
    print(result)
    
    print("\n" + "=" * 80)
    print("\n🔍 Tìm xe từ 'Vũng Tàu' đến 'Quận 1':\n")
    result = search_vungtau_routes_by_address_tool(
        pickup_address="Vũng Tàu",
        dropoff_address="Quận 1",
    )
    print(result)
    
    print()


def demo_4_chat_simulation():
    """Demo 4: Giả lập cuộc hội thoại với agent"""
    print("=" * 80)
    print("DEMO 4: GIẢLẬP CUỘC HỘI THOẠI VỚI AGENT")
    print("=" * 80)
    
    conversations = [
        {
            "user": "Tôi muốn đi từ Bà Rịa đến Quận 9",
            "agent_action": "search_vungtau_routes_by_address_tool",
            "params": {"pickup_address": "Bà Rịa", "dropoff_address": "Quận 9"},
        },
        {
            "user": "Sân bay Tân Sơn Nhất ở đâu?",
            "agent_action": "geocode_address_tool",
            "params": {"address": "Sân bay Tân Sơn Nhất"},
        },
    ]
    
    for idx, conv in enumerate(conversations, 1):
        print(f"\n💬 Conversation {idx}:")
        print(f"   User: {conv['user']}")
        print(f"   Agent action: {conv['agent_action']}")
        print(f"   Params: {conv['params']}")
        print(f"\n   Agent response:")
        
        if conv['agent_action'] == "geocode_address_tool":
            result = geocode_address_tool(**conv['params'])
            print(f"   {result}")
        elif conv['agent_action'] == "search_vungtau_routes_by_address_tool":
            result = search_vungtau_routes_by_address_tool(**conv['params'])
            # Chỉ in 500 ký tự đầu để không quá dài
            print(f"   {result[:500]}...\n   [Còn nữa...]")
    
    print()


if __name__ == "__main__":
    print("\n" + "🗺️" * 40)
    print("DEMO HỆ THỐNG GEOCODING & TÌM TUYẾN XE")
    print("🗺️" * 40 + "\n")
    
    try:
        demo_1_geocode_addresses()
        demo_2_geocode_tool_for_agent()
        demo_3_search_routes_from_text()
        demo_4_chat_simulation()
        
        print("=" * 80)
        print("✅ HOÀN THÀNH TẤT CẢ DEMO!")
        print("=" * 80)
        print("\n💡 WORKFLOW HOÀN CHỈNH:")
        print("   1. User nhập địa chỉ text (ví dụ: 'Bà Rịa', 'Quận 1')")
        print("   2. Tool geocoding chuyển thành tọa độ (lat, lng)")
        print("   3. Tool tìm tuyến xe so sánh với database waypoints")
        print("   4. Tính khoảng cách bằng Haversine (hoặc Google Maps API)")
        print("   5. Trả về top 3 tuyến xe tối ưu")
        print("\n📚 KHÔNG CẦN GOOGLE MAPS API KEY:")
        print("   - Geocoding: Dùng fallback database cho địa chỉ phổ biến")
        print("   - Distance: Dùng công thức Haversine")
        print("   - Maps link: Tạo từ tọa độ, không cần API")
        print("\n🎯 KẾT LUẬN:")
        print("   Hệ thống hoạt động tốt KHÔNG CẦN API KEY!")
        print("   Chỉ cần API key nếu muốn:")
        print("   - Geocoding chính xác hơn cho địa chỉ phức tạp")
        print("   - Khoảng cách theo đường đi thực tế (không phải đường chim bay)")
        print("   - Thời gian di chuyển ước tính")
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
