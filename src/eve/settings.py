from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource
)
from pydantic import Field, BaseModel
from typing import Literal, Union, Tuple, Type

# load config

class StdioServerConfig(BaseModel):
    """Локальный MCP-сервер, запускаемый командой (stdio-транспорт)."""
    type: Literal["stdio"] = "stdio"
    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)


class SSEServerConfig(BaseModel):
    """Удалённый сервер по Server-Sent Events."""
    type: Literal["sse"]
    url: str
    headers: dict[str, str] = Field(default_factory=dict)


class HTTPServerConfig(BaseModel):
    """Удалённый сервер по HTTP (streamable http)."""
    type: Literal["http"]
    url: str
    headers: dict[str, str] = Field(default_factory=dict)

ServerConfig = Union[StdioServerConfig, SSEServerConfig, HTTPServerConfig]


class MCPSettings(BaseSettings):
    model_config = SettingsConfigDict(
        json_file="./eve_config.json",
        extra='ignore'
    )

    mcp_servers: dict[str, ServerConfig] = Field(
        default_factory=dict,
        alias="mcpServers"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        # Явно добавляем JSON-источник. Порядок: init > env > dotenv > secrets > json
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            JsonConfigSettingsSource(settings_cls, json_file="./eve_config.json"),
        )

settings = MCPSettings()
