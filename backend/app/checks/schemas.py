from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CheckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    monitor_id: UUID
    status: str
    status_code: int | None
    response_time_ms: float | None
    error: str | None
    checked_at: datetime