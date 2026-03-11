<<<<<<< HEAD
# mcp-weather-server
mcp-weather-server
=======
## MCP Weather Server

This repository provides a simple **Model Context Protocol (MCP)** server written in Python that exposes weather data as tools. It is packaged so it can be published to GitHub and (optionally) to PyPI.

The server is built on the official [`mcp` Python SDK](https://modelcontextprotocol.github.io/python-sdk/) and uses the free [Open‑Meteo](https://open-meteo.com/) APIs (no API key required).

### Features

- **MCP-compliant server** using `FastMCP`
- **Two tools**:
  - `get_current_weather` – current conditions for a city
  - `get_daily_forecast` – daily forecast for a city for the next N days
- **Runs locally in Python** (stdio transport by default)

### Installation

From the project root:

```bash
pip install -e .
```

Or, using `uv`:

```bash
uv sync
```

### Running the MCP server locally

You can run the server directly via the console script:

```bash
python -m mcp_weather_server.server
```

Or, if installed as a package:

```bash
mcp-weather-server
```

By default it uses the `stdio` transport, which works with MCP-compatible clients (e.g. IDE integrations or LLM apps that support MCP).

### Connecting with MCP Inspector (optional)

To experiment via HTTP instead of stdio, you can set the transport to `streamable-http` inside `server.py` and then run:

```bash
uv run --with mcp python -m mcp_weather_server.server
```

Then start the MCP Inspector:

```bash
npx -y @modelcontextprotocol/inspector
```

and connect to `http://localhost:8000/mcp`.

>>>>>>> 748634e (feat: initialize MCP weather server package)
