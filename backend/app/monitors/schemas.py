from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class MonitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    url: HttpUrl
    interval_seconds: int = Field(default=60, ge=5)
    timeout_seconds: int = Field(default=10, ge=1)
    enabled: bool = True


class MonitorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    url: HttpUrl | None = None
    interval_seconds: int | None = Field(default=None, ge=5)
    timeout_seconds: int | None = Field(default=None, ge=1)
    enabled: bool | None = None


class MonitorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    url: str
    interval_seconds: int
    timeout_seconds: int
    enabled: bool
    created_at: datetime
    updated_at: datetime


class MonitorCheckResponse(BaseModel):
    monitor_id: UUID
    status: str
    status_code: int | None
    response_time_ms: float | None
    error: str | None