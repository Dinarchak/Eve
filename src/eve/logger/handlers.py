from .formatter import Formatter, JSONFormatter
from .entry import LogEntry
from typing import TextIO
from pathlib import Path
import threading
import sys


class Handler:
    def __init__(self, formatter: Formatter)
        self._fmtter = formatter

    def emit(self, entry: LogEntry):
        raise NotImplementedError
    
    def handle(self, entry: LogEntry) -> None:
        with self._lock:
            self.emit(entry)


class StdioHadler(Handler):
    def __init__(self, formatter: Formatter, stream: TextIO | None = None):
        super().__init__(formatter)
        self._stream = stream or sys.stdout


    def emit(self, entry: LogEntry):
        self._stream.write(self._fmtter.format(entry) + '\n')
        self._stream.flush()


class FileHandler(Handler):
    def __init__(self, formatter: Formatter | JSONFormatter, path: "str | Path"):
        super().__init__(formatter=formatter)
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(self._path, "a", encoding="utf-8")

    def emit(self, entry: LogEntry):
        self._file.write(self._fmtter.format(entry) + '\n')
        self._file.flush()

    def close(self):
        self._file.close()


class RotatingFileHandler(FileHandler):
    def __init__(self, formatter, path, max_bytes: int = 10_000_000, backup_count: int = 5):
        self._max_bytes = max_bytes
        self._backup_count = backup_count
        super().__init__(formatter, path)

    def emit(self, entry: LogEntry) -> None:
        super().emit(entry)
        if self._file.tell() >= self._max_bytes:
            self._rotate()

    def _rotate(self) -> None:
        self._file.close()
        for i in range(self._backup_count - 1, 0, -1):
            src = self._path.with_suffix(f"{self._path.suffix}.{i}")
            dst = self._path.with_suffix(f"{self._path.suffix}.{i + 1}")
            if src.exists():
                src.replace(dst)
        self._path.replace(self._path.with_suffix(f"{self._path.suffix}.1"))
        self._file = open(self._path, "a", encoding="utf-8")