from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    section_id: UUID
    claim_type: str
    text: str
    normalized_text: str | None
    effective_from: datetime | None
    effective_to: datetime | None
    status: str
    created_at: datetime
