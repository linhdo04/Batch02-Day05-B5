from backend.app.agent.service import clarify_trip, search_trip
from backend.app.schemas import (
    ClarificationChoice,
    ClarificationRequest,
    PathType,
    Priority,
    TripQuery,
    WebSearchResult,
)


def test_ranks_cheapest_first() -> None:
    response = search_trip(TripQuery(priority=Priority.price))

    assert response.path == PathType.low_confidence
    assert response.tickets[0].operator == "Sao Viet Express"
    assert response.tickets[0].price_vnd == 390000


def test_ranks_nearest_pickup_first() -> None:
    response = search_trip(TripQuery(priority=Priority.pickup_distance))

    assert response.tickets[0].operator == "Queen Cafe VIP"
    assert response.tickets[0].pickup_distance_km == 1.2


def test_finds_hanoi_to_thanh_hoa_with_accented_city_names() -> None:
    response = search_trip(
        TripQuery(
            from_city="Hà Nội",
            to_city="Thanh Hóa",
            date="2026-06-06",
            priority=Priority.price,
        )
    )

    assert response.path == PathType.happy
    assert len(response.tickets) == 3
    assert response.tickets[0].operator == "Thanh Hoa Limousine"
    assert response.tickets[0].price_vnd == 100000


def test_detects_thanh_phong_ambiguity() -> None:
    response = search_trip(TripQuery(pickup_text="Giao xu Thanh Phong"))

    assert response.path == PathType.clarification
    assert response.clarification_options == [
        ClarificationChoice.pickup_place,
        ClarificationChoice.bus_operator,
    ]


def test_suggests_nearby_dates_when_no_ticket(monkeypatch) -> None:
    monkeypatch.setattr("backend.app.agent.service.search_web_ticket_sources", lambda query: [])

    response = search_trip(TripQuery(to_city="Nha Trang", date="2026-06-06"))

    assert response.path == PathType.failure
    assert response.suggested_dates == ["2026-06-07"]


def test_falls_back_to_tavily_sources_when_mock_has_no_ticket(monkeypatch) -> None:
    monkeypatch.setattr(
        "backend.app.agent.service.search_web_ticket_sources",
        lambda query: [
            WebSearchResult(
                title="Vé xe Hà Nội đi Hải Phòng",
                url="https://example.com/ha-noi-hai-phong",
                snippet="Có nhiều nhà xe mở bán theo ngày.",
            )
        ],
    )

    response = search_trip(TripQuery(from_city="Hà Nội", to_city="Hải Phòng"))

    assert response.path == PathType.low_confidence
    assert response.tickets == []
    assert len(response.web_results) == 1
    assert response.web_results[0].url == "https://example.com/ha-noi-hai-phong"


def test_tavily_call_uses_bearer_auth(monkeypatch) -> None:
    from backend.app.agent import tools

    captured: dict = {}

    class FakeResponse:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"results": [{"title": "Ticket result", "url": "https://example.com"}]}

    def fake_post(url: str, *, headers: dict, json: dict, timeout: int) -> FakeResponse:
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")
    monkeypatch.setattr(tools.requests, "post", fake_post)

    results = tools._call_tavily("vé xe Hà Nội đi Hải Phòng", max_results=1)

    assert results
    assert captured["headers"]["Authorization"] == "Bearer tvly-test"
    assert "api_key" not in captured["json"]
    assert captured["json"]["country"] == "vietnam"


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


<<<<<<< HEAD
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
=======
def test_chat_agent_searches_route_before_gemini(monkeypatch) -> None:
    from backend.app.agent.service import chat_agent
    from backend.app.schemas import ChatRequest

    monkeypatch.setattr(
        "backend.app.agent.service.search_web_ticket_sources",
        lambda query: [
            WebSearchResult(
                title="Đặt vé xe từ Hà Nội đi Cao Bằng - Vexere.com",
                url="https://vexere.com/vi-VN/ve-xe-khach-tu-ha-noi-di-cao-bang-cao-bang-124t21211.html",
                snippet="Đặt mua vé xe 15 nhà xe đi Cao Bằng từ Hà Nội.",
            )
        ],
    )

    req = ChatRequest(message="tìm cho tôi vé rẻ nhất đi HN đến Cao Bằng ngày 6/6/2026")
    reply = chat_agent(req)

    assert "Hà Nội" in reply or "Ha Noi" in reply
    assert "Cao Bang" in reply
    assert "Vexere.com" in reply
    assert "có muốn tôi tìm" not in reply.lower()
>>>>>>> fc71289c6d4de1bea0875671e93cff3b2a322760
