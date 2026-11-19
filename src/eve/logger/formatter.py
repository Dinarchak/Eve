import json
import re
from datetime import datetime
from .entry import LogEntry

_SECRET_KEYS = {"authorization", "x-api-key", "api_key", "token", "password", "secret"}
_BEARER_RE = re.compile(r"(Bearer\s+)\S+", re.IGNORECASE)
_KV_RE = re.compile(r'("?\b(?:authorization|x-api-key|api_key|token|password|secret)\b"?\s*[:=]\s*"?)([^"\s,}]+)', re.IGNORECASE)


class Formatter:
    DEFAUTL_FORMAT = (
        "[{level}] {time} | {message} | {run_id}"
    )


    def __init__(self, format: str | None = None, datefmt: str | None = None):
        self.fmt = format or self.DEFAUTL_FORMAT
        self.datefmt = datefmt or "%Y-%m-%d %H:%M:%S.%f"

    def format(self, entry: LogEntry, message: str):
        text = self.fmt(
            level=entry.level,
            time=entry.send_time.strftime(self.datefmt),
            message=entry.message,
            run_id=entry.run_id
        )

        text = self._mask(text)

        return text
    

    @staticmethod
    def _mask(text: str) -> str:
        text = _BEARER_RE.sub(r"\1***", text)
        return _KV_RE.sub(r"\1***", text)
    

class JSONFormatter:
    "JSONL-форматтер: LogEntry - JSON-строка"
    def format(entry: LogEntry):
        payload = {
            "time": entry.timestamp.isoformat(timespec="milliseconds"),
            "level": entry.level.name,
            "run_id": entry.run_id,
            "message": entry.message
        }

        return json.dumps(payload, ensure_ascii=False)