from datetime import datetime
import uuid


class RunContext:
    def __init__(self, run_id: str | None = None):
        self.run_id = run_id or f"run-{datetime.now():%Y-%m-%d-%H%M%S}-{uuid.uuid4().hex[:6]}"


    @classmethod
    def set(cls, run_id:str | None = None) -> "RunContext":
        ctx = RunContext(run_id=run_id)
        return ctx
