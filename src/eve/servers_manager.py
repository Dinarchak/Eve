import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSessionGroup, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client

from settings import settings


def to_ollama_tool(name: str, tool) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,                       # уже с префиксом от hook
            "description": tool.description or "",
            "parameters": tool.input_schema,
        },
    }


def prefix_hook(name: str, server_info) -> str:
    return f"{server_info.name}.{name}"


async def connect_server(group: ClientSessionGroup, stack: AsyncExitStack,
                         name: str, cfg) -> None:
    t = cfg.type
    if t == "stdio":
        await group.connect_to_server(StdioServerParameters(
            command=cfg.command,
            args=cfg.args or [],
            env=cfg.env,
        ))
    elif t == "sse":
        read, write = await stack.enter_async_context(sse_client(cfg.url))
        await group.connect_to_server(None, session_params={
            "read_stream": read, "write_stream": write,
        })
    elif t == "http":
        read, write, _ = await stack.enter_async_context(streamable_http_client(cfg.url))
        await group.connect_to_server(None, session_params={
            "read_stream": read, "write_stream": write,
        })
    else:
        raise ValueError(f"unknown transport: {t}")


async def build_group(stack: AsyncExitStack) -> tuple[ClientSessionGroup, AsyncExitStack, list[dict]]:
    await stack.__aenter__()                       # живёт до закрытия приложения

    group = await stack.enter_async_context(
        ClientSessionGroup(component_name_hook=prefix_hook)
    )

    for server_name, cfg in settings.mcp_servers.items():
        print(f"Connecting {server_name} ({cfg.type})")
        await connect_server(group, stack, server_name, cfg)

    # tools уже с префиксами, потому что hook сработал при регистрации
    ollama_tools = [to_ollama_tool(n, t) for n, t in group.tools.items()]
    return group, ollama_tools