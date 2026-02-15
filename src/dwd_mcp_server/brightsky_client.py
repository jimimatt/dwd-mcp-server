"""HTTP client for the Bright Sky API (DWD weather data)."""

from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import httpx

BRIGHTSKY_BASE_URL = "https://api.brightsky.dev"
DEFAULT_TIMEZONE = "Europe/Berlin"


class BrightSkyError(Exception):
    """Raised when Bright Sky API request fails."""


class BrightSkyClient:
    """Async HTTP client for the Bright Sky API."""

    def __init__(self, base_url: str = BRIGHTSKY_BASE_URL, timeout: float = 30.0) -> None:
        """Initialize the Bright Sky client.

        Args:
            base_url: API base URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        """Make an HTTP GET request to the API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            BrightSkyError: If request fails
        """
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise BrightSkyError("No weather data found for the given location.") from e
                raise BrightSkyError(f"API request failed: {e.response.status_code} - {e.response.text}") from e
            except httpx.HTTPError as e:
                raise BrightSkyError(f"API request failed: {e}") from e

            return response.json()

    async def get_current_weather(self, lat: float, lon: float) -> dict[str, Any]:
        """Get current weather for a location.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Current weather data with keys:
            - weather: Current weather observation
            - sources: Data sources used
        """
        params = {
            "lat": lat,
            "lon": lon,
            "tz": DEFAULT_TIMEZONE,
        }
        return await self._request("/current_weather", params)

    async def get_weather_forecast(
        self,
        lat: float,
        lon: float,
        days: int = 3,
    ) -> dict[str, Any]:
        """Get weather forecast for a location.

        Args:
            lat: Latitude
            lon: Longitude
            days: Number of days to forecast (1-10)

        Returns:
            Forecast data with keys:
            - weather: List of hourly forecast entries
            - sources: Data sources used
        """
        days = max(1, min(days, 10))

        now = datetime.now(tz=ZoneInfo(DEFAULT_TIMEZONE))
        date = now.strftime("%Y-%m-%d")
        last_date = (now + timedelta(days=days)).strftime("%Y-%m-%d")

        params = {
            "lat": lat,
            "lon": lon,
            "date": date,
            "last_date": last_date,
            "tz": DEFAULT_TIMEZONE,
        }
        return await self._request("/weather", params)

    async def get_alerts(self, lat: float | None = None, lon: float | None = None) -> dict[str, Any]:
        """Get weather alerts, optionally filtered by location.

        Args:
            lat: Latitude (optional)
            lon: Longitude (optional)

        Returns:
            Alerts data with keys:
            - alerts: List of active weather alerts
        """
        params: dict[str, Any] = {
            "tz": DEFAULT_TIMEZONE,
        }
        if lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon

        return await self._request("/alerts", params)

    async def get_sources(self, lat: float, lon: float, max_dist: int = 50000) -> dict[str, Any]:
        """Find nearby weather stations.

        Args:
            lat: Latitude
            lon: Longitude
            max_dist: Maximum distance in meters

        Returns:
            Sources data with keys:
            - sources: List of nearby weather stations
        """
        params = {
            "lat": lat,
            "lon": lon,
            "max_dist": max_dist,
        }
        return await self._request("/sources", params)


# Wind direction conversion
WIND_DIRECTIONS = [
    ("N", 0, 22.5),
    ("NO", 22.5, 67.5),
    ("O", 67.5, 112.5),
    ("SO", 112.5, 157.5),
    ("S", 157.5, 202.5),
    ("SW", 202.5, 247.5),
    ("W", 247.5, 292.5),
    ("NW", 292.5, 337.5),
    ("N", 337.5, 360),
]


def wind_direction_to_text(degrees: float | None) -> str:
    """Convert wind direction from degrees to German text.

    Args:
        degrees: Wind direction in degrees (0-360)

    Returns:
        German wind direction (N, NO, O, SO, S, SW, W, NW)
    """
    if degrees is None:
        return "unbekannt"

    degrees = degrees % 360
    for direction, start, end in WIND_DIRECTIONS:
        if start <= degrees < end:
            return direction
    return "N"


def format_timestamp(iso_timestamp: str | None) -> str:
    """Format ISO timestamp to readable German format.

    Args:
        iso_timestamp: ISO 8601 timestamp string

    Returns:
        Formatted date/time string (e.g., "Sa, 15.02.2026 14:00")
    """
    if not iso_timestamp:
        return "unbekannt"

    try:
        dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        weekday = weekdays[dt.weekday()]
        return f"{weekday}, {dt.strftime('%d.%m.%Y %H:%M')}"
    except (ValueError, IndexError):
        return iso_timestamp


def format_current_weather(data: dict[str, Any]) -> dict[str, Any]:
    """Format current weather data for LLM consumption.

    Args:
        data: Raw API response from /current_weather

    Returns:
        Formatted weather data
    """
    weather = data.get("weather", {})
    sources = data.get("sources", [])
    station = sources[0] if sources else {}

    return {
        "timestamp": format_timestamp(weather.get("timestamp")),
        "temperature_c": weather.get("temperature"),
        "feels_like_c": weather.get("apparent_temperature"),
        "humidity_percent": weather.get("relative_humidity"),
        "wind_speed_kmh": weather.get("wind_speed_10"),
        "wind_direction": wind_direction_to_text(weather.get("wind_direction_10")),
        "wind_direction_degrees": weather.get("wind_direction_10"),
        "wind_gust_kmh": weather.get("wind_gust_speed_10"),
        "precipitation_mm": weather.get("precipitation_10"),
        "pressure_hpa": weather.get("pressure_msl"),
        "visibility_m": weather.get("visibility"),
        "cloud_cover_percent": weather.get("cloud_cover"),
        "dew_point_c": weather.get("dew_point"),
        "condition": weather.get("condition"),
        "icon": weather.get("icon"),
        "station_name": station.get("station_name"),
        "station_distance_m": station.get("distance"),
    }


def format_forecast(data: dict[str, Any]) -> dict[str, Any]:
    """Format weather forecast data for LLM consumption.

    Args:
        data: Raw API response from /weather

    Returns:
        Formatted forecast with hourly data and daily summaries
    """
    weather_list = data.get("weather", [])
    sources = data.get("sources", [])
    station = sources[0] if sources else {}

    # Format hourly data
    hourly = []
    for entry in weather_list:
        hourly.append(
            {
                "timestamp": format_timestamp(entry.get("timestamp")),
                "temperature_c": entry.get("temperature"),
                "precipitation_mm": entry.get("precipitation"),
                "precipitation_probability_percent": entry.get("precipitation_probability"),
                "wind_speed_kmh": entry.get("wind_speed"),
                "wind_direction": wind_direction_to_text(entry.get("wind_direction")),
                "cloud_cover_percent": entry.get("cloud_cover"),
                "condition": entry.get("condition"),
                "icon": entry.get("icon"),
            }
        )

    # Calculate daily summaries
    daily_data: dict[str, list[dict[str, Any]]] = {}
    for entry in weather_list:
        ts = entry.get("timestamp", "")
        if ts:
            date = ts[:10]  # YYYY-MM-DD
            if date not in daily_data:
                daily_data[date] = []
            daily_data[date].append(entry)

    daily_summary = []
    for date, entries in sorted(daily_data.items()):
        temps = [t for e in entries if (t := e.get("temperature")) is not None]
        precip = [e.get("precipitation") or 0 for e in entries]
        precip_prob = [p for e in entries if (p := e.get("precipitation_probability")) is not None]

        # Find dominant condition (most common non-None)
        conditions = [c for e in entries if (c := e.get("condition")) is not None]
        dominant_condition = max(set(conditions), key=conditions.count) if conditions else None

        try:
            dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S%z")
            weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
            weekday = weekdays[dt.weekday()]
        except ValueError:
            weekday = date

        daily_summary.append(
            {
                "date": date,
                "weekday": weekday,
                "temp_min_c": min(temps) if temps else None,
                "temp_max_c": max(temps) if temps else None,
                "precipitation_total_mm": round(sum(precip), 1),
                "precipitation_probability_max_percent": max(precip_prob) if precip_prob else None,
                "condition": dominant_condition,
            }
        )

    return {
        "hourly": hourly,
        "daily_summary": daily_summary,
        "station_name": station.get("station_name"),
    }


def format_alerts(data: dict[str, Any]) -> dict[str, Any]:
    """Format weather alerts data for LLM consumption.

    Args:
        data: Raw API response from /alerts

    Returns:
        Formatted alerts list
    """
    alerts_list = data.get("alerts", [])

    formatted_alerts = []
    for alert in alerts_list:
        formatted_alerts.append(
            {
                "headline": alert.get("headline_de") or alert.get("headline"),
                "headline_en": alert.get("headline"),
                "severity": alert.get("severity"),
                "event": alert.get("event_de") or alert.get("event"),
                "event_en": alert.get("event"),
                "description": alert.get("description_de") or alert.get("description"),
                "instruction": alert.get("instruction_de") or alert.get("instruction"),
                "onset": format_timestamp(alert.get("onset")),
                "expires": format_timestamp(alert.get("expires")),
                "effective": format_timestamp(alert.get("effective")),
                "regions": [
                    {
                        "name": loc.get("name"),
                        "district": loc.get("district"),
                        "state": loc.get("state"),
                    }
                    for loc in alert.get("locations", [])
                ],
            }
        )

    return {
        "alert_count": len(formatted_alerts),
        "alerts": formatted_alerts,
    }


def format_sources(data: dict[str, Any]) -> dict[str, Any]:
    """Format weather station sources for LLM consumption.

    Args:
        data: Raw API response from /sources

    Returns:
        Formatted list of nearby stations
    """
    sources_list = data.get("sources", [])

    formatted_sources = []
    for source in sources_list:
        formatted_sources.append(
            {
                "station_name": source.get("station_name"),
                "station_id": source.get("dwd_station_id"),
                "distance_m": source.get("distance"),
                "lat": source.get("lat"),
                "lon": source.get("lon"),
                "observation_types": source.get("observation_type", []),
            }
        )

    return {
        "station_count": len(formatted_sources),
        "stations": formatted_sources,
    }
