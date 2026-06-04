"""
Module xử lý dữ liệu tuyến xe linh động cho nhiều tuyến khác nhau.
Tích hợp với distance tools để tìm điểm đón/trả tối ưu.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from backend.app.agent.tools import calculate_distance_google_maps
from backend.app.agent.normalization import normalize_text


# Cache dữ liệu JSON cho nhiều tuyến (dict of dicts)
_ROUTE_DATA_CACHE: Dict[str, Dict] = {}

# Cache route config
_ROUTE_CONFIG_CACHE: Optional[Dict] = None


def load_route_config() -> Dict:
    """
    Load cấu hình tuyến đường từ routes_config.json.
    """
    global _ROUTE_CONFIG_CACHE
    
    if _ROUTE_CONFIG_CACHE is not None:
        return _ROUTE_CONFIG_CACHE
    
    current_dir = Path(__file__).parent.parent
    config_path = current_dir / "data" / "routes_config.json"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file cấu hình tuyến: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        _ROUTE_CONFIG_CACHE = json.load(f)
    
    return _ROUTE_CONFIG_CACHE


def detect_route_from_addresses(pickup_address: str, dropoff_address: str) -> Optional[str]:
    """
    Tự động phát hiện tuyến đường dựa trên địa chỉ đón và trả.
    
    Args:
        pickup_address: Địa chỉ điểm đón
        dropoff_address: Địa chỉ điểm đến
    
    Returns:
        ID tuyến đường (ví dụ: "vungtau_saigon") hoặc None nếu không tìm thấy
    """
    config = load_route_config()
    
    pickup_normalized = normalize_text(pickup_address)
    dropoff_normalized = normalize_text(dropoff_address)
    
    # Tìm tuyến match với cities
    for route in config["routes"]:
        if not route.get("active", True):
            continue
        
        cities = [normalize_text(city) for city in route["cities"]]
        
        # Kiểm tra xem cả 2 địa chỉ có chứa city nào trong danh sách không
        pickup_match = any(city in pickup_normalized for city in cities)
        dropoff_match = any(city in dropoff_normalized for city in cities)
        
        if pickup_match and dropoff_match:
            return route["id"]
    
    return None


def load_route_data(route_id: Optional[str] = None, data_file: Optional[str] = None) -> Dict:
    """
    Load dữ liệu tuyến đường từ file JSON.
    Sử dụng cache để tránh load lại nhiều lần.
    
    Args:
        route_id: ID tuyến đường từ routes_config.json (ví dụ: "vungtau_saigon")
        data_file: Tên file JSON (ví dụ: "vungtau_saigon.json") - dùng nếu không có route_id
    
    Returns:
        Dict chứa dữ liệu tuyến đường
    """
    global _ROUTE_DATA_CACHE
    
    # Xác định file cần load
    if route_id:
        config = load_route_config()
        route_config = next((r for r in config["routes"] if r["id"] == route_id), None)
        
        if not route_config:
            raise ValueError(f"Không tìm thấy tuyến với ID: {route_id}")
        
        data_file = route_config["data_file"]
        cache_key = route_id
    elif data_file:
        cache_key = data_file
    else:
        raise ValueError("Phải cung cấp route_id hoặc data_file")
    
    # Check cache
    if cache_key in _ROUTE_DATA_CACHE:
        return _ROUTE_DATA_CACHE[cache_key]
    
    # Load từ file
    current_dir = Path(__file__).parent.parent
    json_path = current_dir / "data" / data_file
    
    if not json_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Cache lại
    _ROUTE_DATA_CACHE[cache_key] = data
    
    return data


def load_vungtau_saigon_data() -> Dict:
    """
    LEGACY FUNCTION: Giữ lại để backward compatibility.
    Load dữ liệu tuyến Vũng Tàu - Sài Gòn từ file JSON.
    """
    return load_route_data(route_id="vungtau_saigon")


def find_optimal_route(
    pickup_location: tuple[float, float],
    dropoff_location: tuple[float, float],
    max_results: int = 3,
    route_id: Optional[str] = None,
    data_file: Optional[str] = None,
) -> List[Dict]:
    """
    Tìm tuyến xe tối ưu dựa trên vị trí đón và trả của user.
    
    Args:
        pickup_location: (lat, lng) điểm đón của user
        dropoff_location: (lat, lng) điểm đích của user
        max_results: Số lượng kết quả tối đa
        route_id: ID tuyến đường (optional, ví dụ: "vungtau_saigon")
        data_file: Tên file JSON (optional, ví dụ: "vungtau_saigon.json")
    
    Returns:
        List các tuyến xe được xếp hạng theo độ phù hợp
    """
    data = load_route_data(route_id=route_id, data_file=data_file)
    results = []
    
    pickup_lat, pickup_lng = pickup_location
    dropoff_lat, dropoff_lng = dropoff_location
    
    # Duyệt qua tất cả nhà xe và tuyến đường
    for operator in data["operators"]:
        for route in operator["routes"]:
            # Tìm điểm đón gần nhất
            pickup_points = [
                wp for wp in route["waypoints"]
                if wp["type"] in ["pickup", "pickup_transit", "terminal"]
                and "lat" in wp and "lng" in wp
            ]
            
            # Tìm điểm trả gần nhất
            dropoff_points = [
                wp for wp in route["waypoints"]
                if wp["type"] in ["dropoff", "terminal"]
                and "lat" in wp and "lng" in wp
            ]
            
            if not pickup_points or not dropoff_points:
                continue
            
            # Tính khoảng cách đến tất cả điểm đón
            nearest_pickup = None
            min_pickup_distance = float('inf')
            
            for point in pickup_points:
                dist_result = calculate_distance_google_maps(
                    pickup_lat, pickup_lng,
                    point["lat"], point["lng"]
                )
                
                if dist_result["distance_km"] < min_pickup_distance:
                    min_pickup_distance = dist_result["distance_km"]
                    nearest_pickup = {
                        **point,
                        "distance_km": dist_result["distance_km"],
                        "distance_text": dist_result["distance_text"],
                        "duration_text": dist_result["duration_text"],
                        "maps_link": dist_result["maps_link"],
                    }
            
            # Tính khoảng cách từ tất cả điểm trả đến đích
            nearest_dropoff = None
            min_dropoff_distance = float('inf')
            
            for point in dropoff_points:
                dist_result = calculate_distance_google_maps(
                    point["lat"], point["lng"],
                    dropoff_lat, dropoff_lng
                )
                
                if dist_result["distance_km"] < min_dropoff_distance:
                    min_dropoff_distance = dist_result["distance_km"]
                    nearest_dropoff = {
                        **point,
                        "distance_km": dist_result["distance_km"],
                        "distance_text": dist_result["distance_text"],
                        "duration_text": dist_result["duration_text"],
                        "maps_link": dist_result["maps_link"],
                    }
            
            # Tính điểm tổng hợp (càng gần càng tốt)
            total_distance = min_pickup_distance + min_dropoff_distance
            
            results.append({
                "operator_name": operator["name"],
                "operator_type": operator["type"],
                "contact_phone": operator["contact_phone"],
                "route_name": route["route_name"],
                "route_id": route["route_id"],
                "base_price_vnd": route["base_price_vnd"],
                "transit_supported": route["transit_supported"],
                "nearest_pickup": nearest_pickup,
                "nearest_dropoff": nearest_dropoff,
                "total_distance_km": round(total_distance, 2),
                "score": total_distance,  # Điểm càng thấp càng tốt
            })
    
    # Sắp xếp theo điểm (gần nhất lên đầu)
    results.sort(key=lambda x: x["score"])
    
    return results[:max_results]


def format_route_recommendation(
    pickup_location: tuple[float, float],
    dropoff_location: tuple[float, float],
    pickup_address: str = "",
    dropoff_address: str = "",
    route_id: Optional[str] = None,
    data_file: Optional[str] = None,
) -> str:
    """
    Format gợi ý tuyến xe thành text dễ đọc cho user.
    
    Args:
        pickup_location: (lat, lng) điểm đón
        dropoff_location: (lat, lng) điểm đích
        pickup_address: Địa chỉ điểm đón (optional)
        dropoff_address: Địa chỉ điểm đích (optional)
        route_id: ID tuyến đường (optional, auto-detect nếu không có)
        data_file: Tên file JSON (optional)
    
    Returns:
        Text gợi ý các tuyến xe phù hợp
    """
    try:
        # Auto-detect route nếu không có route_id
        if not route_id and not data_file:
            route_id = detect_route_from_addresses(pickup_address, dropoff_address)
            
            if not route_id:
                return (
                    "Xin lỗi, không thể tự động xác định tuyến đường phù hợp. "
                    "Vui lòng cung cấp thêm thông tin hoặc thử địa điểm khác."
                )
        
        routes = find_optimal_route(
            pickup_location, 
            dropoff_location, 
            route_id=route_id, 
            data_file=data_file
        )
        
        if not routes:
            return (
                "Xin lỗi, hiện tại chưa có tuyến xe nào phù hợp với yêu cầu của bạn. "
                "Vui lòng thử tìm kiếm với địa điểm khác."
            )
        
        result = f"🚌 **Gợi ý tuyến xe từ {pickup_address or 'vị trí của bạn'} đến {dropoff_address or 'điểm đến'}:**\n\n"
        
        for idx, route in enumerate(routes, 1):
            pickup = route["nearest_pickup"]
            dropoff = route["nearest_dropoff"]
            
            result += f"**{idx}. {route['operator_name']}** ({route['operator_type']})\n"
            result += f"   📍 **Tuyến:** {route['route_name']}\n"
            result += f"   💰 **Giá vé:** {route['base_price_vnd']:,} VNĐ\n"
            result += f"   📞 **Hotline:** {route['contact_phone']}\n\n"
            
            result += f"   **🔵 Điểm đón gần bạn nhất:**\n"
            result += f"      • {pickup['node_name']}\n"
            result += f"      • Cách bạn: {pickup['distance_text']}\n"
            if pickup['duration_text'] != "Không xác định":
                result += f"      • Thời gian đến điểm đón: {pickup['duration_text']}\n"
            result += f"      • 🗺️ [Xem đường đi]({pickup['maps_link']})\n\n"
            
            result += f"   **🔴 Điểm trả gần đích nhất:**\n"
            result += f"      • {dropoff['node_name']}\n"
            result += f"      • Cách điểm đến: {dropoff['distance_text']}\n"
            if dropoff['duration_text'] != "Không xác định":
                result += f"      • Thời gian từ điểm trả đến đích: {dropoff['duration_text']}\n"
            result += f"      • 🗺️ [Xem đường đi]({dropoff['maps_link']})\n\n"
            
            if route["transit_supported"]:
                result += f"   ✅ Nhà xe hỗ trợ đón/trả tận nơi trong nội thành\n\n"
            
            result += "   " + "-" * 50 + "\n\n"
        
        result += "\n💡 **Lưu ý:**\n"
        result += "- Giá vé có thể thay đổi tùy vào thời điểm đặt\n"
        result += "- Nên gọi điện xác nhận điểm đón/trả trước khi đặt vé\n"
        result += "- Một số nhà xe có thể đón/trả tận nơi (kiểm tra với nhà xe)\n"
        
        return result
        
    except Exception as e:
        return f"Lỗi khi tìm kiếm tuyến xe: {str(e)}"


def search_route_by_location_tool(
    pickup_lat: float,
    pickup_lng: float,
    dropoff_lat: float,
    dropoff_lng: float,
    pickup_address: str = "",
    dropoff_address: str = "",
    route_id: Optional[str] = None,
) -> str:
    """
    Tool cho Gemini Agent: Tìm kiếm tuyến xe dựa trên vị trí đón và trả.
    
    Args:
        pickup_lat: Vĩ độ điểm đón
        pickup_lng: Kinh độ điểm đón
        dropoff_lat: Vĩ độ điểm đích
        dropoff_lng: Kinh độ điểm đích
        pickup_address: Địa chỉ điểm đón (optional)
        dropoff_address: Địa chỉ điểm đích (optional)
        route_id: ID tuyến đường (optional, auto-detect nếu không có)
    
    Returns:
        Text gợi ý các tuyến xe phù hợp
    """
    return format_route_recommendation(
        (pickup_lat, pickup_lng),
        (dropoff_lat, dropoff_lng),
        pickup_address,
        dropoff_address,
        route_id=route_id,
    )


def get_all_operators_info(route_id: Optional[str] = None, data_file: Optional[str] = None) -> str:
    """
    Tool cho Gemini Agent: Lấy thông tin tất cả nhà xe trên một tuyến.
    
    Args:
        route_id: ID tuyến đường (optional, ví dụ: "vungtau_saigon")
        data_file: Tên file JSON (optional)
    
    Returns:
        Danh sách tất cả nhà xe và tuyến đường
    """
    try:
        # Nếu không có route_id, lấy tất cả tuyến đang active
        if not route_id and not data_file:
            config = load_route_config()
            result = "🚌 **Danh sách tất cả tuyến xe:**\n\n"
            
            for route_config in config["routes"]:
                if not route_config.get("active", True):
                    continue
                
                result += f"**{route_config['name']}** (ID: {route_config['id']})\n"
                result += f"   📂 File: {route_config['data_file']}\n"
                result += f"   🌍 Khu vực: {route_config['region']}\n\n"
            
            result += "\n💡 **Gợi ý:** Để xem chi tiết nhà xe trên một tuyến, hãy cung cấp route_id!\n"
            return result
        
        data = load_route_data(route_id=route_id, data_file=data_file)
        
        result = f"🚌 **Danh sách nhà xe tuyến {data.get('route_group', 'N/A')}:**\n\n"
        
        for idx, operator in enumerate(data["operators"], 1):
            result += f"**{idx}. {operator['name']}** ({operator['type']})\n"
            result += f"   📞 Hotline: {operator['contact_phone']}\n"
            result += f"   📍 Số tuyến: {len(operator['routes'])} tuyến\n"
            
            for route in operator["routes"]:
                result += f"      • {route['route_name']} - {route['base_price_vnd']:,} VNĐ\n"
            
            result += "\n"
        
        result += "\n💡 **Gợi ý:** Để tìm tuyến xe phù hợp nhất, hãy cho tôi biết địa điểm đón và địa điểm đến của bạn!\n"
        
        return result
        
    except Exception as e:
        return f"Lỗi khi lấy thông tin nhà xe: {str(e)}"


def enrich_ticket_with_waypoints(
    operator_name: str,
    route_keywords: list[str],
    user_pickup_lat: float,
    user_pickup_lng: float,
    user_dropoff_lat: float,
    user_dropoff_lng: float,
    route_id: Optional[str] = None,
    data_file: Optional[str] = None,
) -> dict:
    """
    Enrich thông tin vé từ search API với waypoints từ database JSON.
    
    Args:
        operator_name: Tên nhà xe (ví dụ: "Toàn Thắng Limousine")
        route_keywords: Keywords để match route (ví dụ: ["Vũng Tàu", "Sài Gòn", "Sân Bay"])
        user_pickup_lat: Vĩ độ điểm đón của user
        user_pickup_lng: Kinh độ điểm đón của user
        user_dropoff_lat: Vĩ độ đích của user
        user_dropoff_lng: Kinh độ đích của user
        route_id: ID tuyến đường (optional)
        data_file: Tên file JSON (optional)
    
    Returns:
        dict chứa thông tin điểm đón/trả tối ưu và waypoints
    """
    try:
        from backend.app.agent.tools import calculate_distance_google_maps
        
        data = load_route_data(route_id=route_id, data_file=data_file)
        
        # Tìm operator matching (case-insensitive, ignore spaces)
        operator = None
        normalized_operator_name = normalize_text(operator_name).replace(" ", "")
        
        for op in data["operators"]:
            normalized_op_name = normalize_text(op["name"]).replace(" ", "")
            if normalized_operator_name in normalized_op_name or normalized_op_name in normalized_operator_name:
                operator = op
                break
        
        if not operator:
            return {
                "success": False,
                "error": f"Không tìm thấy nhà xe '{operator_name}' trong database",
            }
        
        # Tìm route matching với keywords (case-insensitive)
        matched_route = None
        max_match_score = 0
        
        for route in operator["routes"]:
            route_name_normalized = normalize_text(route["route_name"])
            match_score = sum(1 for kw in route_keywords if normalize_text(kw) in route_name_normalized)
            
            if match_score > max_match_score:
                max_match_score = match_score
                matched_route = route
        
        # Nếu không match được, lấy route đầu tiên
        if not matched_route and operator["routes"]:
            matched_route = operator["routes"][0]
        
        if not matched_route:
            return {
                "success": False,
                "error": f"Không tìm thấy tuyến phù hợp cho nhà xe '{operator_name}'",
            }
        
        # Tìm điểm đón gần nhất
        pickup_points = [
            wp for wp in matched_route["waypoints"]
            if wp["type"] in ["pickup", "pickup_transit", "terminal"]
            and "lat" in wp and "lng" in wp
        ]
        
        nearest_pickup = None
        min_pickup_distance = float('inf')
        
        for point in pickup_points:
            dist_result = calculate_distance_google_maps(
                user_pickup_lat, user_pickup_lng,
                point["lat"], point["lng"]
            )
            
            if dist_result["distance_km"] < min_pickup_distance:
                min_pickup_distance = dist_result["distance_km"]
                nearest_pickup = {
                    **point,
                    "distance_km": dist_result["distance_km"],
                    "distance_text": dist_result["distance_text"],
                    "duration_text": dist_result["duration_text"],
                    "maps_link": dist_result["maps_link"],
                }
        
        # Tìm điểm trả gần nhất
        dropoff_points = [
            wp for wp in matched_route["waypoints"]
            if wp["type"] in ["dropoff", "terminal"]
            and "lat" in wp and "lng" in wp
        ]
        
        nearest_dropoff = None
        min_dropoff_distance = float('inf')
        
        for point in dropoff_points:
            dist_result = calculate_distance_google_maps(
                point["lat"], point["lng"],
                user_dropoff_lat, user_dropoff_lng
            )
            
            if dist_result["distance_km"] < min_dropoff_distance:
                min_dropoff_distance = dist_result["distance_km"]
                nearest_dropoff = {
                    **point,
                    "distance_km": dist_result["distance_km"],
                    "distance_text": dist_result["distance_text"],
                    "duration_text": dist_result["duration_text"],
                    "maps_link": dist_result["maps_link"],
                }
        
        return {
            "success": True,
            "operator_name": operator["name"],
            "operator_type": operator["type"],
            "contact_phone": operator["contact_phone"],
            "route_name": matched_route["route_name"],
            "route_id": matched_route["route_id"],
            "base_price_vnd": matched_route["base_price_vnd"],
            "transit_supported": matched_route["transit_supported"],
            "nearest_pickup": nearest_pickup,
            "nearest_dropoff": nearest_dropoff,
            "all_pickups": pickup_points,
            "all_dropoffs": dropoff_points,
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": f"Lỗi khi enrich waypoints: {str(e)}\n{traceback.format_exc()}",
        }


def enrich_search_results_with_waypoints_tool(
    tickets_json: str,
    user_pickup_address: str,
    user_dropoff_address: str,
    route_id: Optional[str] = None,
) -> str:
    """
    Tool cho Gemini Agent: Enrich kết quả tìm vé với thông tin điểm đón/trả từ database.
    
    Workflow:
    1. Agent gọi search API/tool để tìm vé
    2. Agent nhận list vé (JSON string)
    3. Agent gọi tool này để enrich mỗi vé với waypoints
    
    Args:
        tickets_json: JSON string chứa list vé từ search API
                     Format: [{"operator": "...", "route": "...", "price": ...}, ...]
        user_pickup_address: Địa chỉ đón của user
        user_dropoff_address: Địa chỉ đích của user
        route_id: ID tuyến đường (optional, auto-detect nếu không có)
    
    Returns:
        Text formatted với thông tin chi tiết điểm đón/trả
    """
    try:
        import json
        from backend.app.agent.tools import geocode_address
        
        # Auto-detect route nếu không có route_id
        if not route_id:
            route_id = detect_route_from_addresses(user_pickup_address, user_dropoff_address)
        
        # Parse tickets JSON
        tickets = json.loads(tickets_json)
        
        # Geocode user locations
        pickup_result = geocode_address(user_pickup_address)
        dropoff_result = geocode_address(user_dropoff_address)
        
        if not pickup_result["success"] or not dropoff_result["success"]:
            return "Lỗi: Không thể xác định tọa độ điểm đón hoặc đích"
        
        result = f"🚌 **Gợi ý tuyến xe từ {user_pickup_address} đến {user_dropoff_address}:**\n\n"
        
        enriched_count = 0
        for idx, ticket in enumerate(tickets[:3], 1):  # Top 3
            operator_name = ticket.get("operator", "")
            route_name = ticket.get("route", "")
            
            # Tách keywords từ route name
            route_keywords = [kw.strip() for kw in route_name.split("-") if kw.strip()]
            
            # Enrich với waypoints
            enriched = enrich_ticket_with_waypoints(
                operator_name=operator_name,
                route_keywords=route_keywords,
                user_pickup_lat=pickup_result["lat"],
                user_pickup_lng=pickup_result["lng"],
                user_dropoff_lat=dropoff_result["lat"],
                user_dropoff_lng=dropoff_result["lng"],
                route_id=route_id,
            )
            
            if not enriched["success"]:
                continue
            
            enriched_count += 1
            pickup = enriched["nearest_pickup"]
            dropoff = enriched["nearest_dropoff"]
            
            result += f"**{idx}. {enriched['operator_name']}** ({enriched['operator_type']})\n"
            result += f"   📍 **Tuyến:** {enriched['route_name']}\n"
            result += f"   💰 **Giá vé:** {enriched['base_price_vnd']:,} VNĐ\n"
            result += f"   📞 **Hotline:** {enriched['contact_phone']}\n\n"
            
            if pickup:
                result += f"   **🔵 Điểm đón gần bạn nhất:**\n"
                result += f"      • {pickup['node_name']}\n"
                result += f"      • Cách bạn: {pickup['distance_text']}\n"
                if pickup['duration_text'] != "Không xác định":
                    result += f"      • Thời gian: {pickup['duration_text']}\n"
                result += f"      • 🗺️ [Xem đường đi]({pickup['maps_link']})\n\n"
            
            if dropoff:
                result += f"   **🔴 Điểm trả gần đích nhất:**\n"
                result += f"      • {dropoff['node_name']}\n"
                result += f"      • Cách đích: {dropoff['distance_text']}\n"
                if dropoff['duration_text'] != "Không xác định":
                    result += f"      • Thời gian: {dropoff['duration_text']}\n"
                result += f"      • 🗺️ [Xem đường đi]({dropoff['maps_link']})\n\n"
            
            if enriched["transit_supported"]:
                result += f"   ✅ Hỗ trợ đón/trả tận nơi\n\n"
            
            result += "   " + "-" * 50 + "\n\n"
        
        if enriched_count == 0:
            result += "Xin lỗi, không tìm thấy thông tin chi tiết điểm đón/trả cho các vé này.\n"
        
        result += "\n💡 **Lưu ý:** Nên gọi điện xác nhận điểm đón/trả trước khi đặt vé.\n"
        
        return result
        
    except Exception as e:
        return f"Lỗi khi enrich kết quả: {str(e)}"
