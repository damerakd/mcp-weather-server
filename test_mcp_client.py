import asyncio
import json
import sys
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    """
    Simple script to sanity‑check the local MCP weather server.

    It will:
    - start the server process via stdio
    - list available tools
    - call `get_current_weather` for a sample city
    """
    # Use the same Python interpreter that's running this script and point
    # directly at the server script, so this works even without installing
    # the package in the environment.
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["src/mcp_weather_server/server.py"],
    )

    async with AsyncExitStack() as stack:
        read, write = await stack.enter_async_context(stdio_client(server_params))
        session: ClientSession = await stack.enter_async_context(
            ClientSession(read, write)
        )

        await session.initialize()

        tools = (await session.list_tools()).tools
        print("Tools exposed by server:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")

        print("\nCalling get_current_weather for Berlin...")
        result = await session.call_tool(
            "get_current_weather",
            arguments={"city": "Guntur", "country": "IND"},
        )

        print("\nPretty JSON result:")
        if result.structuredContent and "result" in result.structuredContent:
            print(json.dumps(result.structuredContent["result"], indent=2))
        else:
            print(result)


if __name__ == "__main__":
    asyncio.run(main())

