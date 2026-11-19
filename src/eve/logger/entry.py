from .level import Level
from datetime import datetime
from dataclasses import dataclass

@dataclass(frozen=True)
class LogEntry:
    level: Level
    message: str
    run_id: int
    send_time: datetime