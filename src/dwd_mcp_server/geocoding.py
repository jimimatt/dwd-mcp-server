"""Geocoding module for resolving location names to coordinates."""

import re

import httpx

from dwd_mcp_server.german_cities import get_city_coordinates

# Regex pattern for direct coordinate input: "lat,lon" or "lat, lon"
COORDINATE_PATTERN = re.compile(r"^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$")

# Nominatim API for fallback geocoding
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {
    "User-Agent": "dwd-mcp-server/0.1.0 (https://github.com/dwd-mcp-server)",
}


class GeocodingError(Exception):
    """Raised when location cannot be resolved to coordinates."""


async def resolve_location(location: str) -> tuple[float, float]:
    """Resolve a location string to (latitude, longitude) coordinates.

    Supports three input formats:
    1. Direct coordinates: "50.7753,6.0839" or "50.7753, 6.0839"
    2. Known German city name: "Aachen", "München", etc.
    3. Fallback: Nominatim API lookup for other locations

    Args:
        location: Location string (coordinates, city name, or address)

    Returns:
        Tuple of (latitude, longitude)

    Raises:
        GeocodingError: If location cannot be resolved
    """
    location = location.strip()

    if not location:
        raise GeocodingError("Location cannot be empty")

    # 1. Check for direct coordinate input
    match = COORDINATE_PATTERN.match(location)
    if match:
        lat = float(match.group(1))
        lon = float(match.group(2))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise GeocodingError(f"Invalid coordinates: lat={lat}, lon={lon}")
        return (lat, lon)

    # 2. Look up in internal city table
    coords = get_city_coordinates(location)
    if coords is not None:
        return coords

    # 3. Fallback: Nominatim API
    return await _nominatim_lookup(location)


async def _nominatim_lookup(query: str) -> tuple[float, float]:
    """Look up coordinates using the Nominatim (OpenStreetMap) API.

    Args:
        query: Location search query

    Returns:
        Tuple of (latitude, longitude)

    Raises:
        GeocodingError: If lookup fails or no results found
    """
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "de",  # Prefer German results
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                NOMINATIM_URL,
                params=params,
                headers=NOMINATIM_HEADERS,
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise GeocodingError(f"Nominatim API request failed: {e}") from e

        data = response.json()

        if not data:
            raise GeocodingError(
                f"Location '{query}' not found. Try using coordinates (lat,lon) or a known German city name."
            )

        result = data[0]
        return (float(result["lat"]), float(result["lon"]))
