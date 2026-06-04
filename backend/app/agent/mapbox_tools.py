"""
Mapbox API Integration - MIỄN PHÍ 100,000 requests/tháng
==========================================================

Thay thế Google Maps APIs bằng Mapbox:
- Geocoding API: Chuyển địa chỉ → tọa độ
- Directions API: Tính khoảng cách + thời gian thực tế (driving)
- Matrix API: Tính khoảng cách nhiều điểm cùng lúc

Ưu điểm:
- ✅ 100,000 requests FREE/tháng (không cần thẻ)
- ✅ Chỉ cần email signup
- ✅ Khoảng cách chính xác (theo đường bộ thực tế)
- ✅ Có thời gian di chuyển

Docs: https://docs.mapbox.com/api/
"""

from __future__ import annotations

import os
import requests
from typing import Optional, Dict, List, Tuple
from math import radians, sin, cos, sqrt, atan2


def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Tính khoảng cách giữa 2 tọa độ theo công thức Haversine (khoảng cách đường chim bay).
    Dùng làm fallback khi không có API key hoặc API lỗi.
    
    Returns:
        Khoảng cách tính bằng km
    """
    R = 6371  # Bán kính Trái Đất (km)
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)
    
    a = sin(delta_lat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return distance


def mapbox_geocode(address: str) -> Dict:
    """
    Chuyển địa chỉ text thành tọa độ (lat, lng) sử dụng Mapbox Geocoding API.
    
    API: https://docs.mapbox.com/api/search/geocoding/
    Free tier: 100,000 requests/tháng
    
    Args:
        address: Địa chỉ cần tìm tọa độ (ví dụ: "Bà Rịa, Việt Nam")
    
    Returns:
        dict với các key:
        - lat: Vĩ độ
        - lng: Kinh độ
        - formatted_address: Địa chỉ đầy đủ được format bởi Mapbox
        - success: True nếu thành công, False nếu thất bại
        - error: Thông báo lỗi (nếu có)
        - method: "mapbox_geocoding" hoặc "fallback_database"
    """
    api_key = os.getenv("MAPBOX_ACCESS_TOKEN")
    
    # Fallback database cho các địa điểm phổ biến
    known_locations = {
        "vung tau": {"lat": 10.3460, "lng": 107.0843, "name": "Vũng Tàu"},
        "vũng tàu": {"lat": 10.3460, "lng": 107.0843, "name": "Vũng Tàu"},
        "ba ria": {"lat": 10.5063, "lng": 107.1639, "name": "Bà Rịa"},
        "bà rịa": {"lat": 10.5063, "lng": 107.1639, "name": "Bà Rịa"},
        "quan 1": {"lat": 10.7707, "lng": 106.6906, "name": "Quận 1, TP.HCM"},
        "quận 1": {"lat": 10.7707, "lng": 106.6906, "name": "Quận 1, TP.HCM"},
        "tan son nhat": {"lat": 10.8187, "lng": 106.6519, "name": "Sân bay Tân Sơn Nhất"},
        "tân sơn nhất": {"lat": 10.8187, "lng": 106.6519, "name": "Sân bay Tân Sơn Nhất"},
        "san bay": {"lat": 10.8187, "lng": 106.6519, "name": "Sân bay Tân Sơn Nhất"},
        "sân bay": {"lat": 10.8187, "lng": 106.6519, "name": "Sân bay Tân Sơn Nhất"},
        "sai gon": {"lat": 10.7769, "lng": 106.7009, "name": "Sài Gòn"},
        "sài gòn": {"lat": 10.7769, "lng": 106.7009, "name": "Sài Gòn"},
        "ho chi minh": {"lat": 10.7769, "lng": 106.7009, "name": "TP. Hồ Chí Minh"},
        "hồ chí minh": {"lat": 10.7769, "lng": 106.7009, "name": "TP. Hồ Chí Minh"},
        "tp.hcm": {"lat": 10.7769, "lng": 106.7009, "name": "TP. Hồ Chí Minh"},
        "tphcm": {"lat": 10.7769, "lng": 106.7009, "name": "TP. Hồ Chí Minh"},
    }
    
    # Fallback: Nếu không có API key
    if not api_key:
        normalized = address.lower().strip()
        for keyword, location in known_locations.items():
            if keyword in normalized:
                return {
                    "lat": location["lat"],
                    "lng": location["lng"],
                    "formatted_address": location["name"],
                    "success": True,
                    "error": "No Mapbox API key, using fallback database",
                    "method": "fallback_database",
                }
        
        # Trả về tọa độ mặc định
        return {
            "lat": 10.7769,
            "lng": 106.7009,
            "formatted_address": address,
            "success": True,
            "error": "No Mapbox API key, using default coordinates",
            "method": "fallback_default",
        }
    
    try:
        # Gọi Mapbox Geocoding API
        # Docs: https://docs.mapbox.com/api/search/geocoding/#forward-geocoding
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{requests.utils.quote(address)}.json"
        params = {
            "access_token": api_key,
            "country": "VN",  # Giới hạn kết quả trong Việt Nam
            "language": "vi",  # Ưu tiên tên tiếng Việt
            "limit": 1,  # Chỉ lấy kết quả đầu tiên
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("features"):
            raise Exception("No results found")
        
        # Lấy kết quả đầu tiên
        feature = data["features"][0]
        coordinates = feature["geometry"]["coordinates"]  # [lng, lat]
        place_name = feature.get("place_name", address)
        
        return {
            "lat": coordinates[1],  # Latitude
            "lng": coordinates[0],  # Longitude
            "formatted_address": place_name,
            "success": True,
            "error": None,
            "method": "mapbox_geocoding",
        }
        
    except Exception as e:
        # Fallback về database nếu API thất bại
        normalized = address.lower().strip()
        for keyword, location in known_locations.items():
            if keyword in normalized:
                return {
                    "lat": location["lat"],
                    "lng": location["lng"],
                    "formatted_address": location["name"],
                    "success": True,
                    "error": f"Mapbox API error (using fallback): {str(e)}",
                    "method": "fallback_database",
                }
        
        # Cuối cùng, trả về tọa độ mặc định
        return {
            "lat": 10.7769,
            "lng": 106.7009,
            "formatted_address": address,
            "success": True,
            "error": f"Mapbox API error, using default: {str(e)}",
            "method": "fallback_default",
        }


def mapbox_calculate_distance(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
) -> Dict:
    """
    Tính khoảng cách và thời gian di chuyển giữa 2 điểm sử dụng Mapbox Directions API.
    
    API: https://docs.mapbox.com/api/navigation/directions/
    Free tier: 100,000 requests/tháng
    
    Args:
        origin_lat: Vĩ độ điểm xuất phát
        origin_lng: Kinh độ điểm xuất phát
        dest_lat: Vĩ độ điểm đến
        dest_lng: Kinh độ điểm đến
    
    Returns:
        dict với các key:
        - distance_km: Khoảng cách (km)
        - distance_text: Khoảng cách dạng text (ví dụ: "5.2 km")
        - duration_text: Thời gian di chuyển (ví dụ: "15 phút")
        - duration_seconds: Thời gian di chuyển (giây)
        - success: True nếu thành công, False nếu thất bại
        - error: Thông báo lỗi (nếu có)
        - method: "mapbox_directions" hoặc "haversine_fallback"
    """
    api_key = os.getenv("MAPBOX_ACCESS_TOKEN")
    
    # Fallback: Tính khoảng cách theo công thức Haversine nếu không có API key
    if not api_key:
        distance_km = _haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
        return {
            "distance_km": round(distance_km, 2),
            "distance_text": f"{distance_km:.1f} km",
            "duration_text": "Không xác định",
            "duration_seconds": 0,
            "success": True,
            "error": "No Mapbox API key, using Haversine",
            "method": "haversine_fallback",
        }
    
    try:
        # Gọi Mapbox Directions API
        # Docs: https://docs.mapbox.com/api/navigation/directions/#retrieve-directions
        # Profile: driving-traffic (có real-time traffic)
        coordinates = f"{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
        url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{coordinates}"
        
        params = {
            "access_token": api_key,
            "geometries": "geojson",
            "overview": "simplified",  # Không cần geometry chi tiết
            "steps": "false",  # Không cần turn-by-turn
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != "Ok":
            raise Exception(f"API returned code: {data.get('code')}")
        
        if not data.get("routes"):
            raise Exception("No routes found")
        
        # Lấy route đầu tiên (fastest)
        route = data["routes"][0]
        distance_meters = route["distance"]
        duration_seconds = route["duration"]
        
        distance_km = distance_meters / 1000
        duration_minutes = duration_seconds / 60
        
        return {
            "distance_km": round(distance_km, 2),
            "distance_text": f"{distance_km:.1f} km",
            "duration_text": f"{duration_minutes:.0f} phút" if duration_minutes < 60 else f"{duration_minutes/60:.1f} giờ",
            "duration_seconds": int(duration_seconds),
            "success": True,
            "error": None,
            "method": "mapbox_directions",
        }
        
    except Exception as e:
        # Fallback về Haversine nếu API thất bại
        distance_km = _haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
        return {
            "distance_km": round(distance_km, 2),
            "distance_text": f"{distance_km:.1f} km",
            "duration_text": "Không xác định",
            "duration_seconds": 0,
            "success": True,
            "error": f"Mapbox API error (using Haversine): {str(e)}",
            "method": "haversine_fallback",
        }


def mapbox_matrix_distance(
    origins: List[Tuple[float, float]],
    destinations: List[Tuple[float, float]],
) -> Dict:
    """
    Tính khoảng cách từ nhiều điểm xuất phát đến nhiều điểm đến cùng lúc.
    
    API: https://docs.mapbox.com/api/navigation/matrix/
    Free tier: 100,000 requests/tháng
    Giới hạn: Tối đa 25 locations (origins + destinations)
    
    Args:
        origins: List các tọa độ điểm xuất phát [(lat1, lng1), (lat2, lng2), ...]
        destinations: List các tọa độ điểm đến [(lat1, lng1), (lat2, lng2), ...]
    
    Returns:
        dict với các key:
        - matrix: Ma trận khoảng cách (km) - matrix[i][j] = khoảng cách từ origin[i] đến dest[j]
        - durations: Ma trận thời gian (seconds)
        - success: True nếu thành công
        - error: Thông báo lỗi (nếu có)
        - method: "mapbox_matrix" hoặc "haversine_fallback"
    """
    api_key = os.getenv("MAPBOX_ACCESS_TOKEN")
    
    # Fallback: Tính từng cặp bằng Haversine
    if not api_key:
        matrix = []
        durations = []
        for origin_lat, origin_lng in origins:
            row_dist = []
            row_dur = []
            for dest_lat, dest_lng in destinations:
                dist_km = _haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
                row_dist.append(round(dist_km, 2))
                row_dur.append(0)  # Không có duration
            matrix.append(row_dist)
            durations.append(row_dur)
        
        return {
            "matrix": matrix,
            "durations": durations,
            "success": True,
            "error": "No Mapbox API key, using Haversine",
            "method": "haversine_fallback",
        }
    
    try:
        # Gọi Mapbox Matrix API
        # Docs: https://docs.mapbox.com/api/navigation/matrix/#matrix
        
        # Format coordinates: lng,lat;lng,lat;...
        all_coords = origins + destinations
        if len(all_coords) > 25:
            raise Exception("Too many locations (max 25)")
        
        coordinates = ";".join([f"{lng},{lat}" for lat, lng in all_coords])
        url = f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving/{coordinates}"
        
        # Sources = origins (indices 0 to len(origins)-1)
        # Destinations = destinations (indices len(origins) to end)
        sources_indices = ";".join(str(i) for i in range(len(origins)))
        dest_indices = ";".join(str(i) for i in range(len(origins), len(all_coords)))
        
        params = {
            "access_token": api_key,
            "sources": sources_indices,
            "destinations": dest_indices,
            "annotations": "distance,duration",
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != "Ok":
            raise Exception(f"API returned code: {data.get('code')}")
        
        # Parse matrix results
        distances = data.get("distances", [])  # meters
        durations = data.get("durations", [])  # seconds
        
        # Convert to km
        matrix_km = [[round(d / 1000, 2) if d is not None else None for d in row] for row in distances]
        
        return {
            "matrix": matrix_km,
            "durations": durations,
            "success": True,
            "error": None,
            "method": "mapbox_matrix",
        }
        
    except Exception as e:
        # Fallback về Haversine
        matrix = []
        durations = []
        for origin_lat, origin_lng in origins:
            row_dist = []
            row_dur = []
            for dest_lat, dest_lng in destinations:
                dist_km = _haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
                row_dist.append(round(dist_km, 2))
                row_dur.append(0)
            matrix.append(row_dist)
            durations.append(row_dur)
        
        return {
            "matrix": matrix,
            "durations": durations,
            "success": True,
            "error": f"Mapbox API error (using Haversine): {str(e)}",
            "method": "haversine_fallback",
        }
