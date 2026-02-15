# DWD MCP Server

An MCP server (Model Context Protocol) for weather data from the German Weather Service (DWD) via [Bright Sky API](https://brightsky.dev/).

## Features

- **Current Weather** (`get_current_weather`) - Temperature, wind, precipitation, cloud cover, etc.
- **Weather Forecast** (`get_weather_forecast`) - Hourly forecasts and daily summaries
- **Weather Alerts** (`get_weather_alerts`) - Official DWD warnings (storm, thunderstorm, frost, etc.)
- **Weather Stations** (`find_weather_station`) - Find nearest DWD stations

## Installation

### With uv (recommended)

```bash
# Clone repository
git clone https://github.com/your-username/dwd-mcp-server.git
cd dwd-mcp-server

# Install dependencies
uv sync

# Development dependencies (optional)
uv sync --extra dev
```

### With pip

```bash
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

## Usage

### Start as MCP server

```bash
# With uv
uv run dwd-mcp-server start

# Or directly with Python
python -m dwd_mcp_server.cli start
```

### Integrate with Claude Desktop

Add the following configuration to your Claude Desktop `config.json`:

```json
{
  "mcpServers": {
    "dwd-weather": {
      "command": "uv",
      "args": ["--directory", "/path/to/dwd-mcp-server", "run", "dwd-mcp-server", "start"]
    }
  }
}
```

### Integrate with Claude Code

```bash
claude mcp add dwd-weather -- uv --directory /path/to/dwd-mcp-server run dwd-mcp-server start
```

## MCP Tools

### `get_current_weather`

Get current weather for a location.

**Parameters:**

- `location` (string, required): City name (e.g., "Aachen", "Munich") or coordinates (e.g., "50.7753,6.0839")

**Example response:**

```json
{
  "timestamp": "Sat, 15.02.2026 14:00",
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

Get weather forecast for a location.

**Parameters:**

- `location` (string, required): City name or coordinates
- `days` (integer, optional): Number of days (1-10, default: 3)

**Returns:** Hourly data and daily summaries with min/max temperatures.

### `get_weather_alerts`

Get official weather alerts.

**Parameters:**

- `location` (string, optional): City name or coordinates. If omitted: all alerts for Germany.

**Returns:** List of active alerts with type, severity, description, and validity period.

### `find_weather_station`

Find nearest DWD weather stations.

**Parameters:**

- `location` (string, required): City name or coordinates

**Returns:** List of stations with name, ID, and distance.

## Geocoding

The server accepts various location inputs:

1. **Direct coordinates:** `"50.7753,6.0839"` or `"50.7753, 6.0839"`
2. **German cities:** `"Aachen"`, `"Munich"`, `"Cologne"` (approx. 100 cities included)
3. **Nominatim fallback:** For unknown locations, OpenStreetMap/Nominatim is queried

## Tests

```bash
# With uv
uv run pytest

# With pytest directly
pytest
```

## Technology Stack

- **MCP Framework:** [mcp Python SDK](https://github.com/modelcontextprotocol/python-sdk) (FastMCP)
- **HTTP Client:** httpx (async)
- **Data Source:** [Bright Sky API](https://brightsky.dev/) (DWD Open Data)
- **Geocoding:** Built-in city table + Nominatim fallback

## License

MIT

## Data Sources

- Weather data: [DWD Open Data](https://www.dwd.de/EN/ourservices/opendata/opendata.html)
- API: [Bright Sky](https://brightsky.dev/)
- Geocoding: [Nominatim/OpenStreetMap](https://nominatim.openstreetmap.org/)
