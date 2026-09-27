from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IncidentCreate(BaseModel):
    monitor_id: UUID
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    severity: str = "MEDIUM"


class IncidentUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: str | None = None
    status: str | None = None
    severity: str | None = None


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    monitor_id: UUID
    title: str
    description: str | None
    status: str
    severity: str
    opened_at: datetime
    resolved_at: datetime | None