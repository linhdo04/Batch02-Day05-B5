from __future__ import annotations

from urllib.parse import quote_plus

from backend.app.agent.normalization import normalize_city, normalize_text
from backend.app.data.mock_tickets import MOCK_TICKETS
from backend.app.schemas import MockTicket, TripQuery


def extract_trip_intent(query: TripQuery) -> TripQuery:
    return query


def detect_pickup_ambiguity(pickup_text: str) -> bool:
    normalized = normalize_text(pickup_text)
    if "thanh phong" not in normalized:
        return False

    place_markers = ("giao xu", "phu my", "vung tau", "diem don", "don tai")
    operator_markers = ("nha xe", "hang xe")
    return any(marker in normalized for marker in place_markers) or not any(
        marker in normalized for marker in operator_markers
    )


def search_mock_tickets(query: TripQuery) -> list[MockTicket]:
    from_city = normalize_city(query.from_city)
    to_city = normalize_city(query.to_city)

    return [
        ticket
        for ticket in MOCK_TICKETS
        if normalize_city(ticket.from_city) == from_city
        and normalize_city(ticket.to_city) == to_city
        and ticket.date == query.date
    ]


def filter_by_operator(tickets: list[MockTicket], operator_text: str) -> list[MockTicket]:
    operator = normalize_text(operator_text)
    return [ticket for ticket in tickets if operator in normalize_text(ticket.operator)]


def suggest_nearby_dates(query: TripQuery) -> list[str]:
    from_city = normalize_city(query.from_city)
    to_city = normalize_city(query.to_city)
    dates = {
        ticket.date
        for ticket in MOCK_TICKETS
        if normalize_city(ticket.from_city) == from_city and normalize_city(ticket.to_city) == to_city
    }
    return sorted(dates)[:3]


def build_maps_link(address: str) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(address)}"


import os
import requests

# Existing imports
from urllib.parse import quote_plus

from backend.app.agent.normalization import normalize_city, normalize_text
from backend.app.data.mock_tickets import MOCK_TICKETS
from backend.app.schemas import MockTicket, TripQuery

# Existing functions ... (keep existing content unchanged up to line 61)

def search_by_date_tool(date: str) -> str:
    """Search for tickets on a specific date using Tavily API if available.
    Returns a string message with results or a fallback notice.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return f"Không có API key cho Tavily. Vui lòng kiểm tra cấu hình. Đang tìm vé cho ngày {date}."
    try:
        url = "https://api.tavily.com/search"
        params = {"query": f"vé xe ngày {date}", "api_key": api_key, "max_results": 5}
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        # Simplify output
        results = data.get("results", [])
        if not results:
            return f"Không tìm thấy kết quả trên Tavily cho ngày {date}."
        txt = f"Kết quả tìm kiếm từ Tavily cho ngày {date}:\n"
        for i, r in enumerate(results, 1):
            txt += f"{i}. {r.get('title', 'Không tiêu đề')} - {r.get('url', '')}\n"
        return txt
    except Exception as e:
        return f"Lỗi khi gọi Tavily API: {e}. Đang cố gắng tìm vé nội bộ cho ngày {date}."



def search_and_format_tickets(
    from_city: str,
    to_city: str,
    date: str,
    priority: str = "price",
    user_lat: float = 21.0369,
    user_lng: float = 105.7897,
) -> str:
    """
    Tìm kiếm và sắp xếp danh sách vé xe khách dựa trên điểm đi, điểm đến, ngày đi và thứ tự ưu tiên.
    Các thành phố hợp lệ: 'Ha Noi', 'Da Nang', 'Hue', 'Nha Trang', 'Ho Chi Minh'.
    Định dạng ngày: YYYY-MM-DD (Ví dụ: 2026-06-06).
    Thứ tự ưu tiên có thể là: 'price' (giá rẻ nhất), 'time' (khởi hành sớm nhất), hoặc 'pickup_distance' (điểm đón gần nhất).
    """
    from backend.app.schemas import TripQuery, Priority, UserLocation
    from backend.app.agent.service import search_trip

    p = Priority.price
    if priority == "time":
        p = Priority.time
    elif priority == "pickup_distance":
        p = Priority.pickup_distance

    query = TripQuery(
        from_city=from_city,
        to_city=to_city,
        date=date,
        priority=p,
        user_location=UserLocation(label="User location", lat=user_lat, lng=user_lng),
    )

    response = search_trip(query, skip_ambiguity=True)

    if response.path == "failure":
        dates_str = ", ".join(response.suggested_dates) if response.suggested_dates else "Không có"
        return (
            f"Không tìm thấy vé xe cho chặng {from_city} -> {to_city} ngày {date}.\n"
            f"Gợi ý các ngày có vé gần nhất: {dates_str}."
        )

    result = f"Đã tìm thấy {len(response.tickets)} vé phù hợp nhất cho chặng {from_city} -> {to_city} ngày {date} (Sắp xếp theo: {p.value}):\n\n"
    for idx, t in enumerate(response.tickets, 1):
        result += (
            f"{idx}. Hãng xe: {t.operator} (Cung cấp bởi: {t.provider})\n"
            f"   - Giá vé: {t.price_vnd:,} VNĐ\n"
            f"   - Khởi hành: {t.departure_time} | Đến nơi: {t.arrival_time}\n"
            f"   - Điểm đón: {t.pickup_point} ({t.pickup_address})\n"
            f"   - Khoảng cách đến bạn: {t.pickup_distance_km:.1f} km\n"
            f"   - Bản đồ điểm đón: {t.maps_url}\n"
            f"   - Link đặt vé: {t.booking_url}\n"
            f"   - Lý do gợi ý: {t.rank_reason}\n\n"
        )

    if response.warning:
        result += f"⚠️ Lưu ý: {response.warning}\n"

    return result


def resolve_pickup_ambiguity_tool(pickup_text: str) -> str:
    """
    Kiểm tra xem thông tin điểm đón của hành khách có bị nhập nhằng hay không.
    Ví dụ: 'Thanh Phong' có thể là tên nhà xe (Nha xe Thanh Phong) hoặc địa danh điểm đón (Giáo xứ Thanh Phong).
    """
    if detect_pickup_ambiguity(pickup_text):
        return (
            "PHÁT HIỆN NHẬP NHẰNG: Điểm đón 'Thanh Phong' có thể hiểu theo 2 nghĩa:\n"
            "1. Địa danh điểm đón: Giáo xứ Thanh Phong ở Phú Mỹ, Vũng Tàu.\n"
            "2. Hãng xe: Nhà xe Thanh Phong chạy tuyến TP.HCM - Đà Nẵng.\n"
            "Vui lòng hỏi lại hành khách để xác nhận họ muốn được đón tại Giáo xứ Thanh Phong hay đặt vé Nhà xe Thanh Phong."
        )
    return "Không phát hiện nhập nhằng điểm đón."
