"""Tests for the geocoding module."""

import pytest

from dwd_mcp_server.geocoding import GeocodingError, resolve_location


class TestResolveLocation:
    """Tests for resolve_location function."""

    @pytest.mark.asyncio
    async def test_direct_coordinates(self) -> None:
        """Test parsing direct coordinate input."""
        lat, lon = await resolve_location("50.7753,6.0839")
        assert lat == pytest.approx(50.7753)
        assert lon == pytest.approx(6.0839)

    @pytest.mark.asyncio
    async def test_direct_coordinates_with_spaces(self) -> None:
        """Test parsing coordinates with spaces."""
        lat, lon = await resolve_location("50.7753, 6.0839")
        assert lat == pytest.approx(50.7753)
        assert lon == pytest.approx(6.0839)

    @pytest.mark.asyncio
    async def test_direct_coordinates_negative(self) -> None:
        """Test parsing negative coordinates."""
        lat, lon = await resolve_location("-12.345, -67.890")
        assert lat == pytest.approx(-12.345)
        assert lon == pytest.approx(-67.890)

    @pytest.mark.asyncio
    async def test_known_city_aachen(self) -> None:
        """Test lookup of known city Aachen."""
        lat, lon = await resolve_location("Aachen")
        assert lat == pytest.approx(50.7753, rel=0.01)
        assert lon == pytest.approx(6.0839, rel=0.01)

    @pytest.mark.asyncio
    async def test_known_city_muenchen(self) -> None:
        """Test lookup of known city München."""
        lat, lon = await resolve_location("München")
        assert lat == pytest.approx(48.1351, rel=0.01)
        assert lon == pytest.approx(11.5820, rel=0.01)

    @pytest.mark.asyncio
    async def test_known_city_case_insensitive(self) -> None:
        """Test that city lookup is case-insensitive."""
        lat1, lon1 = await resolve_location("berlin")
        lat2, lon2 = await resolve_location("BERLIN")
        lat3, lon3 = await resolve_location("Berlin")

        assert lat1 == lat2 == lat3
        assert lon1 == lon2 == lon3

    @pytest.mark.asyncio
    async def test_known_city_with_umlaut_alternative(self) -> None:
        """Test city lookup with umlaut alternatives."""
        lat1, lon1 = await resolve_location("köln")
        lat2, lon2 = await resolve_location("koeln")

        assert lat1 == lat2
        assert lon1 == lon2

    @pytest.mark.asyncio
    async def test_empty_location_raises_error(self) -> None:
        """Test that empty location raises GeocodingError."""
        with pytest.raises(GeocodingError, match="cannot be empty"):
            await resolve_location("")

    @pytest.mark.asyncio
    async def test_whitespace_location_raises_error(self) -> None:
        """Test that whitespace-only location raises GeocodingError."""
        with pytest.raises(GeocodingError, match="cannot be empty"):
            await resolve_location("   ")

    @pytest.mark.asyncio
    async def test_invalid_coordinates_raises_error(self) -> None:
        """Test that invalid coordinates raise GeocodingError."""
        with pytest.raises(GeocodingError, match="Invalid coordinates"):
            await resolve_location("100.0, 6.0839")  # lat > 90

    @pytest.mark.asyncio
    async def test_nominatim_fallback(self) -> None:
        """Test Nominatim fallback for unknown location.

        Note: This test makes a real HTTP request to Nominatim.
        """
        # Use a small town not in our lookup table
        lat, lon = await resolve_location("Monschau")
        # Monschau is near Aachen
        assert 50.5 < lat < 51.0
        assert 6.0 < lon < 6.5
