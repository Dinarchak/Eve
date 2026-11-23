from typing import List
from .handlers import Handler, FileHandler, RotatingFileHandler, StreamHandler
from pathlib import Path
from .level import Level
from .context import RunContext
from .entry import LogEntry
from datetime import datetime, timezone
from .formatter import JSONFormatter, Formatter


class EveLogger:
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


class EveLoggerFactory:
    _handlers: list[Handler] = []
    _threshold: Level = Level.INFO
    _configured = False


    @classmethod
    def setup(
        cls,
        level: "str | Level" = "INFO",
        output: str = "stdout",
        file: "str | None" = None,
        fmt: "str | None" = None,
        datefmt: str = "%Y-%m-%d %H:%M:%S.%f",
        json_format: bool = False,
        rotate: "dict | None" = None,
        run_id: "str | None" = None
    ) -> EveLogger:
        if output not in {"stdout", "stderr", "file", "both"}:
            raise ValueError(f"Unknown output: {output}")
        if output in {"file", "both"} and not file:
            raise ValueError("file is required when output='file' or 'both'")
        
        RunContext.set(run_id)
        cls._threshold = Level.parse(level)
        formatter = JSONFormatter if json_format else Formatter(format=fmt, datefmt=datefmt)
        handlers: list[Handler] = []

        if output in {"stdout", "both"}:
            handlers.append(StreamHandler(formatter))
        if output in {"stderr", "both"}:
            import sys
            handlers.append(StreamHandler(formatter, stream=sys.stderr))
        if output in {"file", "both"}:
            if rotate:
                handlers.append(RotatingFileHandler(
                    formatter, Path(file),
                    max_bytes=rotate.get("max_bytes", 10_000_000),
                    backup_count=rotate.get("backup_count", 5),
                ))
            else:
                handlers.append(FileHandler(formatter, Path(file)))
        cls._handlers = handlers
        cls._configured = True
        return cls.get("eve")


    @classmethod
    def get(cls, name: str) -> EveLogger:
        if not cls._configured:
            raise RuntimeError("EveLoggerFactory.setup() must be called before get()")
        
        return EveLogger(name, cls._handlers, cls._threshold)
    
    @classmethod
    def run_id(cls) -> str:
        return RunContext.current().run_id
