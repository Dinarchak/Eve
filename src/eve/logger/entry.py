from .level import Level
from datetime import datetime
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class LogEntry:
    level: Level
    message: str
    run_id: str
    send_time: datetime
