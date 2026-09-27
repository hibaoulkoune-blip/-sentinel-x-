from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AnomalyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    monitor_id: UUID
    check_id: UUID
    metric: str
    value: float
    mean: float
    standard_deviation: float
    z_score: float
    severity: str
    detected_at: datetime