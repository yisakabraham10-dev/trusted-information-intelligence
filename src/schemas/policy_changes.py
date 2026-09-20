from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PolicyChangeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    change_type: str
    summary: str
    effective_date: datetime | None
    reason_claim_id: UUID | None
    status: str
    detected_at: datetime
