import asyncio
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Weather MCP Server", json_response=True)


GEOCODE_ENDPOINT = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_ENDPOINT = "https://api.open-meteo.com/v1/forecast"


async def _geocode_city(
    city: str,
    country: Optional[str] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    """Resolve a city name (and optional country) into latitude/longitude."""
    close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=10.0)
        close_client = True

    params: Dict[str, Any] = {
        "name": city,
        "count": 1,
    }
    if country:
        params["country"] = country

    try:
        resp = await client.get(GEOCODE_ENDPOINT, params=params)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        if close_client:
            await client.aclose()
        raise RuntimeError(f"Geocoding request failed: {exc}") from exc

    data = resp.json()
    results: List[Dict[str, Any]] = data.get("results") or []
    if not results:
        if close_client:
            await client.aclose()
        raise ValueError(f"Could not find location for city='{city}', country='{country}'.")

    best = results[0]

    if close_client:
        await client.aclose()

    return {
        "name": best.get("name") or city,
        "country": best.get("country"),
        "latitude": best["latitude"],
        "longitude": best["longitude"],
    }


@mcp.tool()
async def get_current_weather(
    city: str,
    country: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get current weather conditions for a city.

    Args:
        city: City name, e.g. "Berlin".
        country: Optional country filter, e.g. "DE" or "Germany".

    Returns:
        A JSON object with location info and current weather (temperature, wind speed, etc.).
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        location = await _geocode_city(city, country=country, client=client)

        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current_weather": True,
        }

        try:
            resp = await client.get(FORECAST_ENDPOINT, params=params)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Weather request failed: {exc}") from exc

        data = resp.json()
        current = data.get("current_weather") or {}

    return {
        "location": location,
        "current_weather": current,
    }


@mcp.tool()
async def get_daily_forecast(
    city: str,
    country: Optional[str] = None,
    days: int = 3,
) -> Dict[str, Any]:
    """
    Get a simple daily weather forecast for the next N days for a city.

    Args:
        city: City name, e.g. "Berlin".
        country: Optional country filter, e.g. "DE" or "Germany".
        days: Number of days to include (1–7).

    Returns:
        A JSON object with location info and an array of daily forecasts.
    """
    if days < 1 or days > 7:
        raise ValueError("days must be between 1 and 7.")

    async with httpx.AsyncClient(timeout=10.0) as client:
        location = await _geocode_city(city, country=country, client=client)

        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
            "forecast_days": days,
        }

        try:
            resp = await client.get(FORECAST_ENDPOINT, params=params)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Forecast request failed: {exc}") from exc

        data = resp.json()
        daily = data.get("daily") or {}

    return {
        "location": location,
        "daily": daily,
    }


def main(transport: str = "stdio") -> None:
    """
    Entry point for running the MCP server locally.

    Args:
        transport: Either "stdio" (default) or "streamable-http".
    """

    async def _run() -> None:
        mcp.run(transport=transport)

    asyncio.run(_run())


if __name__ == "__main__":
    import os

    # Allow selecting transport via environment variable for convenience.
    # Supported: "stdio" (default) and "streamable-http".
    transport = os.getenv("MCP_WEATHER_TRANSPORT", "stdio")
    main(transport=transport)

