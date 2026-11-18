from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource
)
from pydantic import Field, BaseModel, field_validator
from typing import Literal, Union, Tuple, Type
from dotenv import load_dotenv
from typing import (
    List,
    Dict,
    Annotated
)
import re
import os

_ENV_VAR_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")

def _resolve_env(value: str) -> str:
    def _sub(match: re.Match[str]) -> str:
        var = match.group(1)
        if var not in os.environ:
            raise ValueError(f"Environment variable '{var}' is not set")
        return os.environ[var]

    return _ENV_VAR_RE.sub(_sub, value)


class HttpMcpServerConfig(BaseModel):
    type: Literal['http']
    headers: Dict[str, str] = Field(default_factory=dict)
    url: str

    @field_validator('headers')
    @classmethod
    def _v_url(cls, v: Dict[str, str]) -> str:
        return {key: _resolve_env(val) for key, val in v.items()}


class SseMcpServerConfig(BaseModel):
    type: Literal['sse']
    url: str
    headers: Dict[str, str] | None

    @field_validator('headers')
    @classmethod
    def _v_headers(cls, v: Dict[str, str]) -> Dict[str, str]:
        return {key: _resolve_env(val) for key, val in v.items()}
    

class StdioMcpServerConfig(BaseModel):
    type: Literal['stdio'] = 'stdio'
    command: str
    args: List[str] | None
    env: Dict[str, str] | None

    @field_validator('args')
    @classmethod
    def _v_args(cls, v_list: List[str]) -> List[str]:
        return [_resolve_env(val) for val in v_list]
    
    @field_validator('env')
    @classmethod
    def _v_env(cls, v_dict: Dict[str, str]) -> Dict[str, str]:
        return {key: _resolve_env(val) for key, val in v_dict.items()}



MCPServerConfig = Union[HttpMcpServerConfig, SseMcpServerConfig, StdioMcpServerConfig]

class MCPSettings(BaseSettings):
    model_config = SettingsConfigDict(
        json_file="./eve_config.json",
        extra='ignore'
    )

    mcp_servers: Dict[str, Annotated[MCPServerConfig, Field(discriminator='type')]] = Field(
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

load_dotenv()
settings = MCPSettings()
