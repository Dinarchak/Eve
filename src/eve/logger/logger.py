from typing import List
from .handlers import Handler
from .level import Level
from .context import RunContext
from .entry import LogEntry
from datetime import datetime, timezone

class Logger:
    def __init__(self, name: str, hadlers: List[Handler], threshold: Level):
        self._name = name
        self._handlers = hadlers
        self._threshold = threshold

    def log(
            self,
            message: str,
            level: Level | str
            ) -> None:
        lvl = Level.parse(level)
        if lvl < self._threshold:
            return
        
        ctx = RunContext.current()
        entry = LogEntry(
            level=lvl,
            message=message,
            run_id=ctx.run_id,
            send_time=datetime.now(timezone.utc)
        )


        for handler in self._handlers:
            try:
                handler.emit(entry)
            except:
                pass

    def debug(self, message: str): self.log(Level.DEBUG, message)
    def info(self, message: str): self.log(Level.INFO, message)
    def warning(self, message: str): self.log(Level.WARNING, message)
    def error(self, message: str):
        self.log(Level.ERROR, message)
