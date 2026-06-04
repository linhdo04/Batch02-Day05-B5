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
