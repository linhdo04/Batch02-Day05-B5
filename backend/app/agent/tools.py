"""
backend/app/agent/tools.py

Tập hợp các công cụ (tools) dùng cho AI Agent SmartTravel.
Bao gồm:
  - Tìm kiếm phương án di chuyển nội bộ (mock DB hiện có vé xe)
  - Tìm kiếm thực tế qua Tavily (vé xe, tàu, máy bay, chuyến đi)
  - Gợi ý lịch trình, địa điểm du lịch, trải nghiệm và lưu trú từ web
  - Trích xuất thông tin vé từ kết quả Tavily bằng Gemini
  - Phát hiện nhập nhằng điểm đón
  - Tạo link Google Maps & booking
"""
from __future__ import annotations

<<<<<<< HEAD
import os
import requests
from typing import Optional
=======
import logging
import os
import time
>>>>>>> fc71289c6d4de1bea0875671e93cff3b2a322760
from urllib.parse import quote_plus

import requests

from backend.app.agent.normalization import normalize_city, normalize_text
from backend.app.data.mock_tickets import MOCK_TICKETS
from backend.app.observability import elapsed_ms, log_json, summarize_text
from backend.app.schemas import MockTicket, TripQuery, WebSearchResult

<<<<<<< HEAD
# Import Mapbox tools để thay thế Google Maps
from backend.app.agent.mapbox_tools import (
    mapbox_geocode,
    mapbox_calculate_distance,
    _haversine_distance,
)

=======
logger = logging.getLogger("smarttravel.tools")


# ---------------------------------------------------------------------------
# Core helper tools (used internally & by ranking.py)
# ---------------------------------------------------------------------------
>>>>>>> fc71289c6d4de1bea0875671e93cff3b2a322760

def extract_trip_intent(query: TripQuery) -> TripQuery:
    return query


def detect_pickup_ambiguity(pickup_text: str) -> bool:
    """Return True nếu pickup_text có thể bị nhập nhằng (Thanh Phong)."""
    normalized = normalize_text(pickup_text)
    if "thanh phong" not in normalized:
        return False

    place_markers = ("giao xu", "phu my", "vung tau", "diem don", "don tai")
    operator_markers = ("nha xe", "hang xe")
    return any(marker in normalized for marker in place_markers) or not any(
        marker in normalized for marker in operator_markers
    )


def search_mock_tickets(query: TripQuery) -> list[MockTicket]:
    start = time.perf_counter()

    if query.transport_mode.value not in ("all", "bus"):
        log_json(
            logger,
            logging.INFO,
            "tool.search_mock_tickets.skipped",
            stage="tool",
            reason="transport_mode_not_in_mock_db",
            transport_mode=query.transport_mode.value,
            from_city=query.from_city,
            to_city=query.to_city,
            date=query.date,
            elapsed_ms=elapsed_ms(start),
        )
        return []

    from_city = normalize_city(query.from_city)
    to_city = normalize_city(query.to_city)

    tickets = [
        ticket
        for ticket in MOCK_TICKETS
        if normalize_city(ticket.from_city) == from_city
        and normalize_city(ticket.to_city) == to_city
        and ticket.date == query.date
    ]
    log_json(
        logger,
        logging.INFO,
        "tool.search_mock_tickets",
        stage="tool",
        from_city=query.from_city,
        to_city=query.to_city,
        normalized_from=from_city,
        normalized_to=to_city,
        date=query.date,
        result_count=len(tickets),
        elapsed_ms=elapsed_ms(start),
    )
    return tickets


def filter_by_operator(tickets: list[MockTicket], operator_text: str) -> list[MockTicket]:
    operator = normalize_text(operator_text)
    return [ticket for ticket in tickets if operator in normalize_text(ticket.operator)]


def suggest_nearby_dates(query: TripQuery) -> list[str]:
    if query.transport_mode.value not in ("all", "bus"):
        return []

    from_city = normalize_city(query.from_city)
    to_city = normalize_city(query.to_city)
    dates = {
        ticket.date
        for ticket in MOCK_TICKETS
        if normalize_city(ticket.from_city) == from_city
        and normalize_city(ticket.to_city) == to_city
    }
    return sorted(dates)[:3]


def build_maps_link(address: str) -> str:
<<<<<<< HEAD
    """Tạo link Google Maps tìm kiếm địa điểm."""
=======
    """Tạo Google Maps search URL cho một địa chỉ."""
>>>>>>> fc71289c6d4de1bea0875671e93cff3b2a322760
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(address)}"


def build_booking_deeplink(provider: str, ticket_id: str) -> str:
<<<<<<< HEAD
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
=======
    """Tạo deep-link đặt vé theo nhà cung cấp và mã vé."""
    provider_slug = normalize_text(provider).replace(" ", "-")
    return f"https://smarttravel.local/book/{provider_slug}/{ticket_id}"


# ---------------------------------------------------------------------------
# Tavily search tool
# ---------------------------------------------------------------------------

def _call_tavily(query: str, max_results: int = 5) -> list[dict]:
    """
    Gọi Tavily Search API và trả về danh sách kết quả raw.
    Mỗi result có các trường: title, url, content (snippet).
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        log_json(
            logger,
            logging.WARNING,
            "tool.tavily.skipped",
            stage="tool",
            reason="missing_TAVILY_API_KEY",
            query=query,
        )
        return []

    start = time.perf_counter()
    try:
        log_json(
            logger,
            logging.INFO,
            "tool.tavily.request",
            stage="tool",
            query=query,
            max_results=max_results,
        )
        resp = requests.post(
            "https://api.tavily.com/search",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "query": query,
                "max_results": max_results,
                "search_depth": "basic",
                "topic": "general",
                "country": "vietnam",
                "include_answer": False,
                "include_raw_content": False,
                "include_favicon": True,
            },
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        log_json(
            logger,
            logging.INFO,
            "tool.tavily.response",
            stage="tool",
            status_code=resp.status_code,
            result_count=len(results),
            elapsed_ms=elapsed_ms(start),
        )
        return results
    except Exception as exc:
        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        log_json(
            logger,
            logging.ERROR,
            "tool.tavily.error",
            stage="tool",
            error=str(exc),
            status_code=status_code,
            elapsed_ms=elapsed_ms(start),
        )
        return []


def _build_ticket_search_query(query: TripQuery) -> str:
    transport_terms = {
        "all": "vé xe vé tàu vé máy bay",
        "bus": "vé xe khách xe limousine nhà xe",
        "train": "vé tàu hỏa đường sắt ga tàu",
        "flight": "vé máy bay chuyến bay hãng bay",
    }
    provider_terms = {
        "all": "Vexere Vietnam Airlines Vietjet Traveloka MoMo Đường sắt Việt Nam",
        "bus": "Vexere MoMo nhà xe limousine",
        "train": "Đường sắt Việt Nam dsvn vé tàu ga tàu",
        "flight": "Vietnam Airlines Vietjet Bamboo Traveloka vé máy bay",
    }
    mode = query.transport_mode.value
    return (
        f"{transport_terms[mode]} {query.from_city} đi {query.to_city} ngày {query.date} "
        f"giá vé giờ đi đặt vé {provider_terms[mode]}"
    )


def search_web_ticket_sources(query: TripQuery, max_results: int = 5) -> list[WebSearchResult]:
    start = time.perf_counter()
    raw_results = _call_tavily(_build_ticket_search_query(query), max_results=max_results)
    seen_urls: set[str] = set()
    web_results: list[WebSearchResult] = []

    for result in raw_results:
        title = str(result.get("title") or "").strip()
        url = str(result.get("url") or "").strip()
        if not title or not url or url in seen_urls:
            continue

        seen_urls.add(url)
        content = str(result.get("content") or "").strip()
        web_results.append(
            WebSearchResult(
                title=title,
                url=url,
                snippet=summarize_text(content, limit=260),
            )
        )

    log_json(
        logger,
        logging.INFO,
        "tool.search_web_ticket_sources",
        stage="tool",
        from_city=query.from_city,
        to_city=query.to_city,
        date=query.date,
        transport_mode=query.transport_mode.value,
        result_count=len(web_results),
        elapsed_ms=elapsed_ms(start),
    )
    return web_results


def _extract_ticket_info_with_llm(raw_results: list[dict], query_context: str) -> str:
    """
    Dùng Gemini để trích xuất thông tin vé (tên nhà xe, giá vé, giờ đi) từ
    các đoạn text thô của Tavily. Fallback sang tóm tắt đơn giản nếu không có API key.
    """
    if not raw_results:
        log_json(
            logger,
            logging.INFO,
            "tool.extract_ticket_info.skipped",
            stage="tool",
            reason="empty_raw_results",
            query_context=query_context,
        )
        return "Không tìm thấy thông tin trên web."

    # Build raw text từ Tavily snippets
    snippets = "\n\n".join(
        f"[{i+1}] {r.get('title', '')}\nURL: {r.get('url', '')}\n{r.get('content', '')}"
        for i, r in enumerate(raw_results)
    )

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        # Fallback: trả về tóm tắt thô
        log_json(
            logger,
            logging.WARNING,
            "tool.extract_ticket_info.fallback",
            stage="tool",
            reason="missing_GEMINI_API_KEY",
            raw_result_count=len(raw_results),
        )
        lines = [f"- {r.get('title', 'N/A')}: {r.get('url', '')}" for r in raw_results]
        return "Kết quả tìm kiếm web:\n" + "\n".join(lines)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=gemini_key)
        prompt = (
            f"Bối cảnh truy vấn: {query_context}\n\n"
            "Dưới đây là các đoạn văn bản thu thập từ web. "
            "Hãy trích xuất và trình bày ngắn gọn theo định dạng danh sách: "
            "**Nhà cung cấp/hãng** | **Loại vé** | **Giá vé** | **Giờ khởi hành** | **Điểm đón/ga/sân bay** | **Link đặt vé**. "
            "Chỉ lấy thông tin thực sự có trong văn bản, bỏ qua những gì không liên quan. "
            "Nếu không tìm thấy thông tin vé xe, tàu hoặc máy bay nào, nói rõ điều đó.\n\n"
            f"Văn bản:\n{snippets}"
        )

        start = time.perf_counter()
        log_json(
            logger,
            logging.INFO,
            "llm.extract_ticket_info.request",
            stage="llm",
            model="gemini-2.5-flash",
            raw_result_count=len(raw_results),
            query_context=query_context,
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
            ),
        )
        text = response.text or "Không trích xuất được thông tin."
        log_json(
            logger,
            logging.INFO,
            "llm.extract_ticket_info.response",
            stage="llm",
            elapsed_ms=elapsed_ms(start),
            response_preview=summarize_text(text),
        )
        return text
    except Exception as exc:
        log_json(
            logger,
            logging.ERROR,
            "llm.extract_ticket_info.error",
            stage="llm",
            error=str(exc),
        )
        lines = [f"- {r.get('title', 'N/A')}: {r.get('url', '')}" for r in raw_results]
        return "Kết quả tìm kiếm web:\n" + "\n".join(lines)


# ---------------------------------------------------------------------------
# Public tools exposed to the Gemini Agent
# ---------------------------------------------------------------------------

def search_by_date_tool(from_city: str, to_city: str, date: str) -> str:
    """
    Tìm kiếm giá vé xe, tàu, máy bay và chuyến đi trên web (Tavily) theo tuyến đường và ngày.
    Kết quả được LLM trích xuất thành danh sách gọn.

    Args:
        from_city: Thành phố khởi hành (ví dụ: 'Hà Nội', 'TP.HCM').
        to_city:   Thành phố điểm đến (ví dụ: 'Đà Nẵng', 'Nha Trang').
        date:      Ngày đi theo định dạng YYYY-MM-DD (ví dụ: '2026-06-10').
    """
    query = f"vé xe tàu máy bay {from_city} đi {to_city} ngày {date} giá vé giờ đi đặt vé"
    query_context = f"Tìm phương án di chuyển từ {from_city} đến {to_city} ngày {date}"

    raw = _call_tavily(query, max_results=5)
    return _extract_ticket_info_with_llm(raw, query_context)


def _format_web_sources(raw_results: list[dict], intro: str) -> str:
    if not raw_results:
        return "Chưa tìm thấy nguồn web phù hợp. Hãy thử hỏi cụ thể hơn về điểm đến, ngày đi hoặc ngân sách."

    lines = [intro]
    for idx, result in enumerate(raw_results, 1):
        title = str(result.get("title") or "Nguồn tham khảo").strip()
        url = str(result.get("url") or "").strip()
        content = summarize_text(str(result.get("content") or "").strip(), limit=220)
        lines.append(f"{idx}. **{title}**")
        if content:
            lines.append(f"   {content}")
        if url:
            lines.append(f"   {url}")

    lines.append("Hãy mở nguồn phù hợp để xác nhận thông tin mới nhất trước khi đặt dịch vụ.")
    return "\n".join(lines)


def search_travel_guide_tool(destination_or_question: str, date: str = "", interests: str = "") -> str:
    """
    Tìm nguồn web để gợi ý lịch trình, tiện ích, địa điểm du lịch, ăn uống và trải nghiệm.

    Args:
        destination_or_question: Điểm đến hoặc câu hỏi du lịch của người dùng.
        date: Ngày đi nếu có.
        interests: Sở thích, ngân sách hoặc kiểu trải nghiệm nếu có.
    """
    query = (
        f"{destination_or_question} {date} {interests} "
        "lịch trình du lịch địa điểm tham quan ăn uống trải nghiệm khách sạn"
    ).strip()
    raw = _call_tavily(query, max_results=5)
    return _format_web_sources(raw, "Tôi tìm thấy một số nguồn để lên lịch trình và chọn trải nghiệm:")


def search_stay_options_tool(destination: str, date: str = "", budget: str = "") -> str:
    """
    Tìm nguồn web về khách sạn, homestay, khu vực lưu trú và đặt phòng.

    Args:
        destination: Điểm đến hoặc khu vực muốn lưu trú.
        date: Ngày nhận phòng nếu có.
        budget: Ngân sách hoặc hạng phòng nếu có.
    """
    query = f"{destination} {date} {budget} khách sạn homestay đặt phòng khu vực lưu trú review".strip()
    raw = _call_tavily(query, max_results=5)
    return _format_web_sources(raw, "Tôi tìm thấy một số nguồn tham khảo cho lưu trú và đặt phòng:")
>>>>>>> fc71289c6d4de1bea0875671e93cff3b2a322760


def search_and_format_tickets(
    from_city: str,
    to_city: str,
    date: str,
    priority: str = "price",
    user_lat: float = 21.0369,
    user_lng: float = 105.7897,
) -> str:
    """
<<<<<<< HEAD
    Tìm kiếm và sắp xếp danh sách vé xe khách dựa trên điểm đi, điểm đến, ngày đi và thứ tự ưu tiên.
    Các thành phố hợp lệ: 'Ha Noi', 'Da Nang', 'Hue', 'Nha Trang', 'Ho Chi Minh'.
    Định dạng ngày: YYYY-MM-DD (Ví dụ: 2026-06-06).
    Thứ tự ưu tiên có thể là: 'price' (giá rẻ nhất), 'time' (khởi hành sớm nhất), hoặc 'pickup_distance' (điểm đón gần nhất).
    """
    from backend.app.schemas import TripQuery, Priority, UserLocation
=======
    Tìm kiếm và xếp hạng phương án di chuyển từ cơ sở dữ liệu nội bộ.
    Dữ liệu mock hiện có một số tuyến xe khách để demo.
    Các thành phố hợp lệ: 'Ha Noi', 'Da Nang', 'Hue', 'Nha Trang', 'Ho Chi Minh'.
    Định dạng ngày: YYYY-MM-DD (ví dụ: 2026-06-06).
    Thứ tự ưu tiên: 'price' (giá rẻ nhất), 'time' (khởi hành sớm nhất),
    hoặc 'pickup_distance' (điểm đón gần nhất).
    """
    from backend.app.schemas import Priority, TripQuery, UserLocation
>>>>>>> fc71289c6d4de1bea0875671e93cff3b2a322760
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

<<<<<<< HEAD
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
=======
    if response.web_results:
        result = (
            f"Tôi tìm thấy nguồn web cho chặng {from_city} → {to_city} ngày {date}:\n\n"
        )
        for idx, source in enumerate(response.web_results, 1):
            result += f"{idx}. **{source.title}**\n   {source.url}\n"
            if source.snippet:
                result += f"   {source.snippet}\n"
            result += "\n"

        if response.warning:
            result += f"Lưu ý: {response.warning}\n"
        return result

    if response.path == "failure":
        dates_str = ", ".join(response.suggested_dates) if response.suggested_dates else "không có"
        return (
            f"Không tìm thấy phương án di chuyển trong dữ liệu nội bộ cho chặng {from_city} → {to_city} ngày {date}.\n"
            f"Các ngày gần nhất có dữ liệu: {dates_str}."
        )

    result = (
        f"Đã tìm thấy {len(response.tickets)} phương án phù hợp nhất "
        f"({from_city} → {to_city}, {date}, ưu tiên: {p.value}):\n\n"
    )
    for idx, t in enumerate(response.tickets, 1):
        result += (
            f"{idx}. **{t.operator}** (qua {t.provider})\n"
            f"   💰 Giá: {t.price_vnd:,} VNĐ\n"
            f"   🕐 {t.departure_time} → {t.arrival_time}\n"
            f"   📍 Điểm đón: {t.pickup_point} ({t.pickup_distance_km:.1f} km từ bạn)\n"
            f"   🗺️ [Bản đồ]({t.maps_url})  |  🎫 [Đặt vé]({t.booking_url})\n"
            f"   ℹ️ {t.rank_reason}\n\n"
        )

    if response.warning:
        result += f"⚠️ {response.warning}\n"
>>>>>>> fc71289c6d4de1bea0875671e93cff3b2a322760

    return result


def resolve_pickup_ambiguity_tool(pickup_text: str) -> str:
    """
<<<<<<< HEAD
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
=======
    Kiểm tra nhập nhằng điểm đón. 'Thanh Phong' có thể là:
    1. Địa danh: Giáo xứ Thanh Phong (Phú Mỹ, Vũng Tàu).
    2. Nhà xe: Nhà xe Thanh Phong (tuyến TP.HCM – Đà Nẵng).
    """
    if detect_pickup_ambiguity(pickup_text):
        return (
            "PHÁT HIỆN NHẬP NHẰNG – 'Thanh Phong' có thể hiểu theo 2 nghĩa:\n"
            "1. 📍 Địa danh điểm đón: Giáo xứ Thanh Phong, Phú Mỹ, Vũng Tàu.\n"
            "2. 🚌 Hãng xe: Nhà xe Thanh Phong (tuyến TP.HCM – Đà Nẵng).\n"
            "Vui lòng xác nhận: bạn muốn được đón tại Giáo xứ Thanh Phong, "
            "hay muốn đặt vé Nhà xe Thanh Phong?"
        )
    return "Không phát hiện nhập nhằng điểm đón."
>>>>>>> fc71289c6d4de1bea0875671e93cff3b2a322760
