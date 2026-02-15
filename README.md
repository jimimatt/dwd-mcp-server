# DWD MCP Server

Ein MCP-Server (Model Context Protocol) für Wetterdaten des Deutschen Wetterdienstes (DWD) via [Bright Sky API](https://brightsky.dev/).

## Features

- **Aktuelles Wetter** (`get_current_weather`) - Temperatur, Wind, Niederschlag, Bewölkung etc.
- **Wettervorhersage** (`get_weather_forecast`) - Stündliche Vorhersage und Tageszusammenfassungen
- **Wetterwarnungen** (`get_weather_alerts`) - Amtliche DWD-Warnungen (Sturm, Gewitter, Frost etc.)
- **Wetterstationen** (`find_weather_station`) - Nächstgelegene DWD-Stationen finden

## Installation

### Mit uv (empfohlen)

```bash
# Repository klonen
git clone https://github.com/your-username/dwd-mcp-server.git
cd dwd-mcp-server

# Dependencies installieren
uv sync

# Entwicklungs-Dependencies (optional)
uv sync --extra dev
```

### Mit pip

```bash
pip install -e .

# Mit Entwicklungs-Dependencies
pip install -e ".[dev]"
```

## Verwendung

### Als MCP-Server starten

```bash
# Mit uv
uv run dwd-mcp-server

# Oder direkt mit Python
python -m dwd_mcp_server.server
```

### In Claude Desktop einbinden

Füge folgende Konfiguration zu deiner Claude Desktop `config.json` hinzu:

```json
{
  "mcpServers": {
    "dwd-weather": {
      "command": "uv",
      "args": ["--directory", "/pfad/zu/dwd-mcp-server", "run", "dwd-mcp-server"]
    }
  }
}
```

### In Claude Code einbinden

```bash
claude mcp add dwd-weather -- uv --directory /pfad/zu/dwd-mcp-server run dwd-mcp-server
```

## MCP Tools

### `get_current_weather`

Aktuelles Wetter für einen Ort abrufen.

**Parameter:**
- `location` (string, required): Ortsname (z.B. "Aachen", "München") oder Koordinaten (z.B. "50.7753,6.0839")

**Beispiel-Rückgabe:**
```json
{
  "timestamp": "Sa, 15.02.2026 14:00",
  "temperature_c": 8.2,
  "feels_like_c": 5.5,
  "humidity_percent": 78,
  "wind_speed_kmh": 22.3,
  "wind_direction": "W",
  "precipitation_mm": 0.0,
  "cloud_cover_percent": 75,
  "condition": "cloudy",
  "station_name": "Aachen-Orsbach"
}
```

### `get_weather_forecast`

Wettervorhersage für einen Ort abrufen.

**Parameter:**
- `location` (string, required): Ortsname oder Koordinaten
- `days` (integer, optional): Anzahl Tage (1-10, Standard: 3)

**Rückgabe:** Stündliche Daten und Tageszusammenfassungen mit Min/Max-Temperaturen.

### `get_weather_alerts`

Amtliche Wetterwarnungen abrufen.

**Parameter:**
- `location` (string, optional): Ortsname oder Koordinaten. Ohne Angabe: alle Warnungen für Deutschland.

**Rückgabe:** Liste aktiver Warnungen mit Typ, Schweregrad, Beschreibung und Gültigkeitszeitraum.

### `find_weather_station`

Nächstgelegene DWD-Wetterstationen finden.

**Parameter:**
- `location` (string, required): Ortsname oder Koordinaten

**Rückgabe:** Liste der Stationen mit Name, ID und Entfernung.

## Geocoding

Der Server akzeptiert verschiedene Ortsangaben:

1. **Direkte Koordinaten:** `"50.7753,6.0839"` oder `"50.7753, 6.0839"`
2. **Deutsche Städte:** `"Aachen"`, `"München"`, `"Köln"` (ca. 100 Städte integriert)
3. **Nominatim-Fallback:** Für unbekannte Orte wird OpenStreetMap/Nominatim abgefragt

## Tests

```bash
# Mit uv
uv run pytest

# Mit pytest direkt
pytest
```

## Technologie-Stack

- **MCP Framework:** [mcp Python SDK](https://github.com/modelcontextprotocol/python-sdk) (FastMCP)
- **HTTP Client:** httpx (async)
- **Datenquelle:** [Bright Sky API](https://brightsky.dev/) (DWD Open Data)
- **Geocoding:** Integrierte Städtetabelle + Nominatim-Fallback

## Lizenz

MIT

## Datenquellen

- Wetterdaten: [DWD Open Data](https://www.dwd.de/EN/ourservices/opendata/opendata.html)
- API: [Bright Sky](https://brightsky.dev/)
- Geocoding: [Nominatim/OpenStreetMap](https://nominatim.openstreetmap.org/)
