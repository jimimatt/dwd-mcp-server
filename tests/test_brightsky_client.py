"""Tests for the Bright Sky API client."""

import pytest

from dwd_mcp_server.brightsky_client import (
    BrightSkyClient,
    format_current_weather,
    format_timestamp,
    wind_direction_to_text,
)


class TestWindDirectionToText:
    """Tests for wind_direction_to_text function."""

    def test_north(self) -> None:
        assert wind_direction_to_text(0) == "N"
        assert wind_direction_to_text(360) == "N"
        assert wind_direction_to_text(10) == "N"

    def test_northeast(self) -> None:
        assert wind_direction_to_text(45) == "NO"
        assert wind_direction_to_text(30) == "NO"

    def test_east(self) -> None:
        assert wind_direction_to_text(90) == "O"

    def test_southeast(self) -> None:
        assert wind_direction_to_text(135) == "SO"

    def test_south(self) -> None:
        assert wind_direction_to_text(180) == "S"

    def test_southwest(self) -> None:
        assert wind_direction_to_text(225) == "SW"

    def test_west(self) -> None:
        assert wind_direction_to_text(270) == "W"

    def test_northwest(self) -> None:
        assert wind_direction_to_text(315) == "NW"

    def test_none_returns_unknown(self) -> None:
        assert wind_direction_to_text(None) == "unbekannt"


class TestFormatTimestamp:
    """Tests for format_timestamp function."""

    def test_valid_timestamp(self) -> None:
        result = format_timestamp("2026-02-15T14:00:00+01:00")
        assert "15.02.2026" in result
        assert "14:00" in result

    def test_utc_timestamp(self) -> None:
        result = format_timestamp("2026-02-15T14:00:00Z")
        assert "15.02.2026" in result

    def test_none_returns_unknown(self) -> None:
        assert format_timestamp(None) == "unbekannt"

    def test_empty_returns_unknown(self) -> None:
        assert format_timestamp("") == "unbekannt"

    def test_weekday_included(self) -> None:
        # 2026-02-15 is a Sunday
        result = format_timestamp("2026-02-15T14:00:00+01:00")
        assert result.startswith("So,")


class TestFormatCurrentWeather:
    """Tests for format_current_weather function."""

    def test_formats_all_fields(self) -> None:
        raw_data = {
            "weather": {
                "timestamp": "2026-02-15T14:00:00+01:00",
                "temperature": 8.2,
                "apparent_temperature": 5.5,
                "relative_humidity": 78,
                "wind_speed_10": 22.3,
                "wind_direction_10": 270,
                "wind_gust_speed_10": 35.0,
                "precipitation_10": 0.0,
                "pressure_msl": 1015.2,
                "visibility": 25000,
                "cloud_cover": 75,
                "dew_point": 4.5,
                "condition": "cloudy",
                "icon": "cloudy",
            },
            "sources": [
                {
                    "station_name": "Aachen-Orsbach",
                    "distance": 5234,
                }
            ],
        }

        result = format_current_weather(raw_data)

        assert result["temperature_c"] == 8.2
        assert result["feels_like_c"] == 5.5
        assert result["humidity_percent"] == 78
        assert result["wind_speed_kmh"] == 22.3
        assert result["wind_direction"] == "W"
        assert result["wind_direction_degrees"] == 270
        assert result["wind_gust_kmh"] == 35.0
        assert result["precipitation_mm"] == 0.0
        assert result["pressure_hpa"] == 1015.2
        assert result["visibility_m"] == 25000
        assert result["cloud_cover_percent"] == 75
        assert result["condition"] == "cloudy"
        assert result["station_name"] == "Aachen-Orsbach"
        assert result["station_distance_m"] == 5234

    def test_handles_missing_source(self) -> None:
        raw_data = {
            "weather": {"temperature": 10.0},
            "sources": [],
        }

        result = format_current_weather(raw_data)

        assert result["temperature_c"] == 10.0
        assert result["station_name"] is None


class TestBrightSkyClientIntegration:
    """Integration tests for BrightSkyClient.

    Note: These tests make real HTTP requests to the Bright Sky API.
    """

    @pytest.mark.asyncio
    async def test_get_current_weather(self) -> None:
        """Test fetching current weather for Aachen."""
        client = BrightSkyClient()
        result = await client.get_current_weather(lat=50.7753, lon=6.0839)

        assert "weather" in result
        assert "sources" in result
        assert result["weather"].get("temperature") is not None

    @pytest.mark.asyncio
    async def test_get_weather_forecast(self) -> None:
        """Test fetching weather forecast."""
        client = BrightSkyClient()
        result = await client.get_weather_forecast(lat=50.7753, lon=6.0839, days=2)

        assert "weather" in result
        assert isinstance(result["weather"], list)
        assert len(result["weather"]) > 0

    @pytest.mark.asyncio
    async def test_get_alerts(self) -> None:
        """Test fetching weather alerts."""
        client = BrightSkyClient()
        result = await client.get_alerts(lat=50.7753, lon=6.0839)

        assert "alerts" in result
        assert isinstance(result["alerts"], list)

    @pytest.mark.asyncio
    async def test_get_sources(self) -> None:
        """Test finding nearby weather stations."""
        client = BrightSkyClient()
        result = await client.get_sources(lat=50.7753, lon=6.0839)

        assert "sources" in result
        assert isinstance(result["sources"], list)
        assert len(result["sources"]) > 0
