from __future__ import annotations

import os
import requests
from typing import Optional
from urllib.parse import quote_plus

from backend.app.agent.normalization import normalize_city, normalize_text
from backend.app.data.mock_tickets import MOCK_TICKETS
from backend.app.schemas import MockTicket, TripQuery

# Import Mapbox tools để thay thế Google Maps
from backend.app.agent.mapbox_tools import (
    mapbox_geocode,
    mapbox_calculate_distance,
    _haversine_distance,
)


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
    """Tạo link Google Maps tìm kiếm địa điểm."""
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(address)}"


def build_booking_deeplink(provider: str, ticket_id: str) -> str:
    """Tạo deep link đến trang đặt vé của nhà cung cấp."""
    base_urls = {
        "Vexere": "https://vexere.com/vi-VN/ve-xe-khach/",
        "MoMo Travel": "https://momo.vn/travel/",
        "Xanh SM Link": "https://xanhsm.com/",
    }
    base_url = base_urls.get(provider, "https://example.com/")
    return f"{base_url}?ticket_id={ticket_id}"


def build_directions_link(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> str:
    """Tạo link Google Maps để dẫn đường từ origin đến destination."""
    return (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={origin_lat},{origin_lng}"
        f"&destination={dest_lat},{dest_lng}"
        f"&travelmode=driving"
    )


def geocode_address(address: str) -> dict:
    """
    Chuyển địa chỉ text thành tọa độ (lat, lng) - Wrapper cho Mapbox Geocoding API.
    
    Args:
        address: Địa chỉ cần tìm tọa độ (ví dụ: "Co.op Mart Bà Rịa, Việt Nam")
    
    Returns:
        dict với các key:
        - lat: Vĩ độ
        - lng: Kinh độ
        - formatted_address: Địa chỉ đầy đủ
        - success: True nếu thành công
        - error: Thông báo lỗi (nếu có)
        - method: "mapbox_geocoding", "fallback_database", hoặc "fallback_default"
    """
    # Sử dụng Mapbox Geocoding API (miễn phí 100,000 requests/tháng)
    return mapbox_geocode(address)


def calculate_distance_google_maps(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    origin_address: str = "",
    dest_address: str = "",
) -> dict:
    """
    Tính khoảng cách và thời gian di chuyển giữa 2 điểm - Wrapper cho Mapbox Directions API.
    
    Args:
        origin_lat: Vĩ độ điểm xuất phát
        origin_lng: Kinh độ điểm xuất phát
        dest_lat: Vĩ độ điểm đến
        dest_lng: Kinh độ điểm đến
        origin_address: Địa chỉ điểm xuất phát (không dùng)
        dest_address: Địa chỉ điểm đến (không dùng)
    
    Returns:
        dict với các key:
        - distance_km: Khoảng cách (km)
        - distance_text: Khoảng cách dạng text
        - duration_text: Thời gian di chuyển
        - duration_seconds: Thời gian di chuyển (giây)
        - maps_link: Link Google Maps để dẫn đường
        - success: True nếu thành công
        - error: Thông báo lỗi (nếu có)
        - method: "mapbox_directions" hoặc "haversine_fallback"
    """
    # Sử dụng Mapbox Directions API (miễn phí 100,000 requests/tháng)
    result = mapbox_calculate_distance(origin_lat, origin_lng, dest_lat, dest_lng)
    
    # Thêm maps_link (dùng Google Maps link vì miễn phí)
    result["maps_link"] = build_directions_link(origin_lat, origin_lng, dest_lat, dest_lng)
    
    return result


def find_nearest_pickup_point(
    user_lat: float,
    user_lng: float,
    pickup_points: list[dict],
) -> dict:
    """
    Tìm điểm đón gần nhất với vị trí người dùng.
    
    Args:
        user_lat: Vĩ độ người dùng
        user_lng: Kinh độ người dùng
        pickup_points: List các điểm đón, mỗi điểm có format:
            {
                "name": str,
                "address": str,
                "lat": float,
                "lng": float,
            }
    
    Returns:
        dict chứa thông tin điểm đón gần nhất và khoảng cách
    """
    if not pickup_points:
        return {
            "success": False,
            "error": "Không có điểm đón nào để so sánh",
        }
    
    nearest = None
    min_distance = float('inf')
    
    for point in pickup_points:
        result = calculate_distance_google_maps(
            user_lat, user_lng,
            point["lat"], point["lng"],
        )
        
        if result["success"] and result["distance_km"] < min_distance:
            min_distance = result["distance_km"]
            nearest = {
                **point,
                **result,
            }
    
    if nearest:
        return {
            "success": True,
            "nearest_point": nearest,
            "all_distances": [
                {
                    "name": p["name"],
                    "address": p["address"],
                    "distance_km": calculate_distance_google_maps(
                        user_lat, user_lng, p["lat"], p["lng"]
                    )["distance_km"],
                }
                for p in pickup_points
            ],
        }
    
    return {
        "success": False,
        "error": "Không thể tính khoảng cách đến bất kỳ điểm đón nào",
    }


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


def geocode_address_tool(address: str) -> str:
    """
    Tool cho Gemini Agent: Tìm tọa độ (latitude, longitude) của một địa chỉ.
    
    Args:
        address: Địa chỉ cần tìm (ví dụ: "Co.op Mart Bà Rịa", "Quận 1 Sài Gòn")
    
    Returns:
        Thông tin tọa độ dạng text để agent sử dụng
    """
    result = geocode_address(address)
    
    if result["success"]:
        return (
            f"Địa chỉ: {result['formatted_address']}\n"
            f"Tọa độ: {result['lat']}, {result['lng']}\n"
            f"Phương thức: {result['method']}\n"
            + (f"Lưu ý: {result['error']}\n" if result['error'] else "")
        )
    else:
        return f"Không thể tìm tọa độ cho địa chỉ '{address}'. Lỗi: {result['error']}"


def search_routes_by_address_tool(
    pickup_address: str,
    dropoff_address: str,
    route_id: Optional[str] = None,
) -> str:
    """
    Tool cho Gemini Agent: Tìm tuyến xe dựa trên địa chỉ đón và trả.
    Tool này tự động:
    1. Chuyển địa chỉ thành tọa độ (geocoding)
    2. Tự động phát hiện tuyến đường phù hợp (nếu không có route_id)
    3. Tìm các tuyến xe phù hợp
    4. Tính khoảng cách đến điểm đón/trả
    5. Xếp hạng và đề xuất top 3 tuyến tối ưu
    
    Args:
        pickup_address: Địa chỉ điểm đón (ví dụ: "Bà Rịa", "Vũng Tàu", "Cầu Giấy Hà Nội")
        dropoff_address: Địa chỉ điểm đến (ví dụ: "Quận 1", "Sân bay Tân Sơn Nhất", "Ninh Bình")
        route_id: ID tuyến đường (optional, auto-detect nếu không có). 
                 Ví dụ: "vungtau_saigon", "hanoi_ninhbinh"
    
    Returns:
        Gợi ý các tuyến xe phù hợp kèm thông tin chi tiết
    """
    try:
        # Bước 1: Geocode địa chỉ đón
        pickup_result = geocode_address(pickup_address)
        if not pickup_result["success"]:
            return f"Lỗi: Không thể tìm tọa độ cho địa chỉ đón '{pickup_address}'"
        
        # Bước 2: Geocode địa chỉ đích
        dropoff_result = geocode_address(dropoff_address)
        if not dropoff_result["success"]:
            return f"Lỗi: Không thể tìm tọa độ cho địa chỉ đích '{dropoff_address}'"
        
        # Bước 3: Import và gọi tool tìm tuyến
        from backend.app.agent.route_search import search_route_by_location_tool
        
        result = search_route_by_location_tool(
            pickup_lat=pickup_result["lat"],
            pickup_lng=pickup_result["lng"],
            dropoff_lat=dropoff_result["lat"],
            dropoff_lng=dropoff_result["lng"],
            pickup_address=pickup_result["formatted_address"],
            dropoff_address=dropoff_result["formatted_address"],
            route_id=route_id,
        )
        
        return result
        
    except Exception as e:
        return f"Lỗi khi tìm kiếm tuyến xe: {str(e)}"


def search_vungtau_routes_by_address_tool(
    pickup_address: str,
    dropoff_address: str,
) -> str:
    """
    LEGACY FUNCTION: Giữ lại để backward compatibility.
    Tìm tuyến xe Vũng Tàu - Sài Gòn dựa trên địa chỉ đón và trả.
    
    DEPRECATED: Sử dụng search_routes_by_address_tool() thay thế.
    """
    return search_routes_by_address_tool(
        pickup_address=pickup_address,
        dropoff_address=dropoff_address,
        route_id="vungtau_saigon",
    )



# ============================================
# TOOL TÍCH HỢP: TÌM VÉ + ĐIỂM ĐÓN/TRẢ TỐI ƯU
# ============================================

def search_route_optimized(
    pickup_address: str,
    pickup_lat: float,
    pickup_lng: float,
    dropoff_address: str,
    dropoff_lat: float,
    dropoff_lng: float,
    date: str = "2026-06-06",
    max_results: int = 3,
    route_id: Optional[str] = None,
) -> str:
    """
    Tool tích hợp: Tìm vé với điểm đón/trả tối ưu cho bất kỳ tuyến nào.
    
    WORKFLOW:
    1. Tự động phát hiện tuyến đường (nếu không có route_id)
    2. Load dữ liệu JSON tuyến đường
    3. Tìm các nhà xe và tuyến đường phù hợp
    4. Tính khoảng cách từ vị trí user đến TẤT CẢ điểm đón
    5. Tính khoảng cách từ TẤT CẢ điểm trả đến đích của user
    6. Chọn điểm đón gần nhất + điểm trả gần nhất cho mỗi tuyến
    7. Sắp xếp theo tổng điểm (giá + khoảng cách)
    8. Trả về top N tuyến tối ưu nhất
    
    Args:
        pickup_address: Địa chỉ điểm đón của user
        pickup_lat: Vĩ độ điểm đón
        pickup_lng: Kinh độ điểm đón
        dropoff_address: Địa chỉ điểm đến của user
        dropoff_lat: Vĩ độ điểm đến
        dropoff_lng: Kinh độ điểm đến
        date: Ngày đi (format: YYYY-MM-DD)
        max_results: Số lượng kết quả tối đa
        route_id: ID tuyến đường (optional, auto-detect nếu không có)
    
    Returns:
        Text gợi ý các tuyến xe phù hợp với điểm đón/trả tối ưu
    """
    try:
        from backend.app.agent.route_search import format_route_recommendation
        
        result = format_route_recommendation(
            (pickup_lat, pickup_lng),
            (dropoff_lat, dropoff_lng),
            pickup_address,
            dropoff_address,
            route_id=route_id,
        )
        
        return result
        
    except FileNotFoundError as e:
        return (
            "Xin lỗi, hiện tại chưa có dữ liệu chi tiết cho tuyến này. "
            "Vui lòng liên hệ với hệ thống để cập nhật dữ liệu."
        )
    except Exception as e:
        return f"Lỗi khi tìm kiếm tuyến xe: {str(e)}"


def search_vungtau_saigon_route_optimized(
    pickup_address: str,
    pickup_lat: float,
    pickup_lng: float,
    dropoff_address: str,
    dropoff_lat: float,
    dropoff_lng: float,
    date: str = "2026-06-06",
    max_results: int = 3,
) -> str:
    """
    LEGACY FUNCTION: Giữ lại để backward compatibility.
    Tìm vé tuyến Vũng Tàu - Sài Gòn với điểm đón/trả tối ưu.
    
    DEPRECATED: Sử dụng search_route_optimized() thay thế.
    """
    return search_route_optimized(
        pickup_address=pickup_address,
        pickup_lat=pickup_lat,
        pickup_lng=pickup_lng,
        dropoff_address=dropoff_address,
        dropoff_lat=dropoff_lat,
        dropoff_lng=dropoff_lng,
        date=date,
        max_results=max_results,
        route_id="vungtau_saigon",
    )
