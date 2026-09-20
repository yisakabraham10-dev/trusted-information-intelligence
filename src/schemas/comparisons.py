from uuid import UUID

from pydantic import BaseModel


class CorrespondenceResponse(BaseModel):
    relationship_type: str
    confidence: float
    method: str
    changes: list[str]


class ChangeDetectionResponse(BaseModel):
    change_type: str
    summary: str


class PolicyChangePersistenceResponse(BaseModel):
    policy_change_id: UUID
    change_type: str


class CompareRegulatoryVersionsResponse(BaseModel):
    old_claim_id: UUID
    new_claim_id: UUID
    correspondence: CorrespondenceResponse | None
    detection: ChangeDetectionResponse | None
    policy_change: PolicyChangePersistenceResponse | None
