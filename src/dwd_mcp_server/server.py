"""FastMCP Server for DWD weather data via Bright Sky API."""

import json
from typing import Annotated

from mcp.server.fastmcp import FastMCP

from dwd_mcp_server.brightsky_client import (
    BrightSkyClient,
    BrightSkyError,
    format_alerts,
    format_current_weather,
    format_forecast,
    format_sources,
)
from dwd_mcp_server.geocoding import GeocodingError, resolve_location

# Initialize MCP server
mcp = FastMCP("DWD Weather Server")

# Initialize Bright Sky client
client = BrightSkyClient()


@mcp.tool()
async def get_current_weather(
    location: Annotated[
        str,
        "Ort als Stadtname (z.B. 'Aachen', 'München') oder Koordinaten (z.B. '50.7753,6.0839')",
    ],
) -> str:
    """Aktuelles Wetter für einen Ort abrufen.

    Gibt Temperatur, Luftfeuchtigkeit, Wind, Niederschlag, Bewölkung und weitere
    aktuelle Wetterdaten zurück.
    """
    try:
        lat, lon = await resolve_location(location)
    except GeocodingError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

    try:
        raw_data = await client.get_current_weather(lat, lon)
    except BrightSkyError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

    weather = format_current_weather(raw_data)
    weather["location_query"] = location
    weather["coordinates"] = {"lat": lat, "lon": lon}

    return json.dumps(weather, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_weather_forecast(
    location: Annotated[
        str,
        "Ort als Stadtname (z.B. 'Köln', 'Berlin') oder Koordinaten (z.B. '50.9375,6.9603')",
    ],
    days: Annotated[
        int,
        "Anzahl der Vorhersagetage (1-10, Standard: 3)",
    ] = 3,
) -> str:
    """Wettervorhersage für einen Ort abrufen.

    Gibt stündliche Vorhersagedaten sowie eine Tageszusammenfassung mit
    Minimal-/Maximaltemperaturen und Niederschlagssummen zurück.
    """
    try:
        lat, lon = await resolve_location(location)
    except GeocodingError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

    try:
        raw_data = await client.get_weather_forecast(lat, lon, days)
    except BrightSkyError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

    forecast = format_forecast(raw_data)
    forecast["location_query"] = location
    forecast["coordinates"] = {"lat": lat, "lon": lon}
    forecast["days_requested"] = days

    return json.dumps(forecast, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_weather_alerts(
    location: Annotated[
        str | None,
        "Optional: Ort als Stadtname oder Koordinaten."
        " Ohne Angabe werden alle Warnungen für Deutschland zurückgegeben.",
    ] = None,
) -> str:
    """Amtliche Wetterwarnungen abrufen.

    Gibt aktuelle Wetterwarnungen des DWD zurück, inklusive Warntyp, Schweregrad,
    Beschreibung und Gültigkeitszeitraum. Kann für einen bestimmten Ort oder
    deutschlandweit abgefragt werden.
    """
    lat: float | None = None
    lon: float | None = None

    if location:
        try:
            lat, lon = await resolve_location(location)
        except GeocodingError as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    try:
        raw_data = await client.get_alerts(lat, lon)
    except BrightSkyError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

    alerts = format_alerts(raw_data)
    if location:
        alerts["location_query"] = location
        alerts["coordinates"] = {"lat": lat, "lon": lon}
    else:
        alerts["location_query"] = "Deutschland (alle Warnungen)"

    return json.dumps(alerts, ensure_ascii=False, indent=2)


@mcp.tool()
async def find_weather_station(
    location: Annotated[
        str,
        "Ort als Stadtname (z.B. 'Hamburg') oder Koordinaten (z.B. '53.5511,9.9937')",
    ],
) -> str:
    """Nächstgelegene DWD-Wetterstationen finden.

    Gibt eine Liste der Wetterstationen in der Nähe des angegebenen Ortes zurück,
    inklusive Stationsname, ID und Entfernung.
    """
    try:
        lat, lon = await resolve_location(location)
    except GeocodingError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

    try:
        raw_data = await client.get_sources(lat, lon)
    except BrightSkyError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

    sources = format_sources(raw_data)
    sources["location_query"] = location
    sources["coordinates"] = {"lat": lat, "lon": lon}

    return json.dumps(sources, ensure_ascii=False, indent=2)


def run_server() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    run_server()
