from datetime import datetime
import uuid


class RunContext:

    _ctx: "RunContext | None" = None

    def __init__(self, run_id: str | None = None):
        self.run_id = run_id or f"run-{datetime.now():%Y-%m-%d-%H%M%S}-{uuid.uuid4().hex[:6]}"
    
    @classmethod
    def current(cls) -> "RunContext":
        if cls._ctx is None:
            ctx = RunContext()
            cls._ctx = ctx
        return cls._ctx

    @classmethod
    def set(cls, run_id: str |  None = None):
        ctx = RunContext(run_id=run_id)
        cls._ctx = ctx
        return ctx
