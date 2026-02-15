"""Tests for the MCP server tools."""

import json

import pytest


class TestMCPTools:
    """Integration tests for MCP tools.

    Note: These tests make real HTTP requests to the Bright Sky API.
    """

    @pytest.mark.asyncio
    async def test_get_current_weather_by_city(self) -> None:
        """Test get_current_weather with city name."""
        from dwd_mcp_server.server import get_current_weather

        result = await get_current_weather("Aachen")
        data = json.loads(result)

        assert "error" not in data
        assert "temperature_c" in data
        assert data["location_query"] == "Aachen"
        assert "coordinates" in data

    @pytest.mark.asyncio
    async def test_get_current_weather_by_coordinates(self) -> None:
        """Test get_current_weather with coordinates."""
        from dwd_mcp_server.server import get_current_weather

        result = await get_current_weather("50.7753, 6.0839")
        data = json.loads(result)

        assert "error" not in data
        assert "temperature_c" in data

    @pytest.mark.asyncio
    async def test_get_current_weather_invalid_location(self) -> None:
        """Test get_current_weather with invalid location."""
        from dwd_mcp_server.server import get_current_weather

        result = await get_current_weather("")
        data = json.loads(result)

        assert "error" in data

    @pytest.mark.asyncio
    async def test_get_weather_forecast(self) -> None:
        """Test get_weather_forecast."""
        from dwd_mcp_server.server import get_weather_forecast

        result = await get_weather_forecast("Berlin", days=2)
        data = json.loads(result)

        assert "error" not in data
        assert "hourly" in data
        assert "daily_summary" in data
        assert data["days_requested"] == 2

    @pytest.mark.asyncio
    async def test_get_weather_alerts_for_location(self) -> None:
        """Test get_weather_alerts for specific location."""
        from dwd_mcp_server.server import get_weather_alerts

        result = await get_weather_alerts("Köln")
        data = json.loads(result)

        assert "error" not in data
        assert "alert_count" in data
        assert "alerts" in data
        assert data["location_query"] == "Köln"

    @pytest.mark.asyncio
    async def test_get_weather_alerts_nationwide(self) -> None:
        """Test get_weather_alerts without location (nationwide)."""
        from dwd_mcp_server.server import get_weather_alerts

        result = await get_weather_alerts(None)
        data = json.loads(result)

        assert "error" not in data
        assert "alert_count" in data
        assert "Deutschland" in data["location_query"]

    @pytest.mark.asyncio
    async def test_find_weather_station(self) -> None:
        """Test find_weather_station."""
        from dwd_mcp_server.server import find_weather_station

        result = await find_weather_station("Hamburg")
        data = json.loads(result)

        assert "error" not in data
        assert "station_count" in data
        assert "stations" in data
        assert len(data["stations"]) > 0
