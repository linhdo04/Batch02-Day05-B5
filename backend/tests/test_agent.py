from backend.app.agent.service import clarify_trip, search_trip
from backend.app.schemas import ClarificationChoice, ClarificationRequest, PathType, Priority, TripQuery


def test_ranks_cheapest_first() -> None:
    response = search_trip(TripQuery(priority=Priority.price))

    assert response.path == PathType.low_confidence
    assert response.tickets[0].operator == "Sao Viet Express"
    assert response.tickets[0].price_vnd == 390000


def test_ranks_nearest_pickup_first() -> None:
    response = search_trip(TripQuery(priority=Priority.pickup_distance))

    assert response.tickets[0].operator == "Queen Cafe VIP"
    assert response.tickets[0].pickup_distance_km == 1.2


def test_detects_thanh_phong_ambiguity() -> None:
    response = search_trip(TripQuery(pickup_text="Giao xu Thanh Phong"))

    assert response.path == PathType.clarification
    assert response.clarification_options == [
        ClarificationChoice.pickup_place,
        ClarificationChoice.bus_operator,
    ]


def test_suggests_nearby_dates_when_no_ticket() -> None:
    response = search_trip(TripQuery(to_city="Nha Trang", date="2026-06-06"))

    assert response.path == PathType.failure
    assert response.suggested_dates == ["2026-06-07"]


def test_clarify_pickup_place_returns_ranked_options() -> None:
    query = TripQuery(pickup_text="Giao xu Thanh Phong")
    response = clarify_trip(ClarificationRequest(query=query, choice=ClarificationChoice.pickup_place))

    assert response.path == PathType.low_confidence
    assert response.tickets
    assert "địa danh" in response.warning


def test_chat_agent_detects_ambiguity() -> None:
    from backend.app.agent.service import chat_agent
    from backend.app.schemas import ChatRequest

    req = ChatRequest(message="đón tôi ở Thanh Phong")
    reply = chat_agent(req)
    assert "Giáo xứ Thanh Phong" in reply or "Nhà xe Thanh Phong" in reply
    assert "Bạn muốn" in reply or "nhập nhằng" in reply


def test_chat_agent_finds_tickets() -> None:
    from backend.app.agent.service import chat_agent
    from backend.app.schemas import ChatRequest

    req = ChatRequest(message="tìm vé từ Hà Nội đi Đà Nẵng ngày 6/6/2026")
    reply = chat_agent(req)
    assert "Sao Viet Express" in reply or "Queen Cafe VIP" in reply
    assert "390,000" in reply or "420,000" in reply


# ========================================
# NEW TESTS FOR DISTANCE CALCULATION TOOLS
# ========================================

def test_calculate_distance_haversine():
    """Test distance calculation using Haversine formula (no API key)"""
    from backend.app.agent.tools import calculate_distance_google_maps
    import os
    
    # Ensure no API key for this test
    original_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if "GOOGLE_MAPS_API_KEY" in os.environ:
        del os.environ["GOOGLE_MAPS_API_KEY"]
    
    try:
        # Cầu Giấy to Mỹ Đình (should be around 7-8 km)
        result = calculate_distance_google_maps(
            origin_lat=21.0369,
            origin_lng=105.7897,
            dest_lat=21.0285,
            dest_lng=105.7803,
        )
        
        assert result["success"] is True
        assert result["method"] == "haversine_fallback"
        assert 1 < result["distance_km"] < 3  # Haversine gives straight line distance
        assert result["maps_link"] is not None
        assert "google.com/maps/dir" in result["maps_link"]
    finally:
        # Restore original key
        if original_key:
            os.environ["GOOGLE_MAPS_API_KEY"] = original_key


def test_build_directions_link():
    """Test Google Maps directions link generation"""
    from backend.app.agent.tools import build_directions_link
    
    link = build_directions_link(21.0369, 105.7897, 21.0285, 105.7803)
    
    assert "https://www.google.com/maps/dir/" in link
    assert "origin=21.0369,105.7897" in link
    assert "destination=21.0285,105.7803" in link
    assert "travelmode=driving" in link


def test_find_nearest_pickup_point():
    """Test finding nearest pickup point from list"""
    from backend.app.agent.tools import find_nearest_pickup_point
    
    pickup_points = [
        {
            "name": "Far Point",
            "address": "Far away",
            "lat": 21.1000,
            "lng": 105.9000,
        },
        {
            "name": "Close Point",
            "address": "Very close",
            "lat": 21.0370,
            "lng": 105.7900,
        },
        {
            "name": "Medium Point",
            "address": "Medium distance",
            "lat": 21.0500,
            "lng": 105.8000,
        },
    ]
    
    # User at Cầu Giấy
    result = find_nearest_pickup_point(
        user_lat=21.0369,
        user_lng=105.7897,
        pickup_points=pickup_points,
    )
    
    assert result["success"] is True
    assert result["nearest_point"]["name"] == "Close Point"
    assert result["nearest_point"]["distance_km"] < 1  # Very close
    assert len(result["all_distances"]) == 3


def test_find_nearest_pickup_point_empty():
    """Test finding nearest point with empty list"""
    from backend.app.agent.tools import find_nearest_pickup_point
    
    result = find_nearest_pickup_point(
        user_lat=21.0369,
        user_lng=105.7897,
        pickup_points=[],
    )
    
    assert result["success"] is False
    assert "error" in result


def test_haversine_distance():
    """Test Haversine formula directly"""
    from backend.app.agent.tools import _haversine_distance
    
    # Hanoi to Da Nang (around 600km)
    distance = _haversine_distance(21.0285, 105.8542, 16.0544, 108.2022)
    
    assert 600 < distance < 700  # Approximately 600km


def test_distance_integration_with_search():
    """Test that distance calculation integrates with ticket search"""
    from backend.app.agent.tools import search_and_format_tickets
    
    result = search_and_format_tickets(
        from_city="Ha Noi",
        to_city="Da Nang",
        date="2026-06-06",
        priority="pickup_distance",
        user_lat=21.0369,
        user_lng=105.7897,
    )
    
    # Should return formatted text with distance info
    assert "Đã tìm thấy" in result
    assert "Khoảng cách đến bạn" in result
    assert "km" in result
    assert "Bản đồ điểm đón" in result
