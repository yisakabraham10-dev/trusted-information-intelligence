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


class EvidenceDetailResponse(BaseModel):
    id: UUID
    page: int | None
    quote: str
    confidence: str | None
    relation_type: str
    strength: float | None


class SourceDetailResponse(BaseModel):
    id: UUID
    name: str
    authority_tier: str
    base_url: str | None
    institution_type: str | None


class DocumentDetailResponse(BaseModel):
    id: UUID
    title: str
    document_type: str
    url: str | None
    version_id: UUID
    version_label: str | None
    publication_date: datetime | None
    effective_date: datetime | None
    source: SourceDetailResponse


class SectionDetailResponse(BaseModel):
    id: UUID
    section_number: str | None
    title: str | None
    page_start: int | None
    page_end: int | None
    document: DocumentDetailResponse


class ClaimDetailResponse(BaseModel):
    id: UUID
    claim_type: str
    text: str
    normalized_text: str | None
    effective_from: datetime | None
    effective_to: datetime | None
    status: str
    section: SectionDetailResponse
    evidence: list[EvidenceDetailResponse]


class CorrespondenceDetailResponse(BaseModel):
    id: UUID
    relationship_type: str
    confidence: float | None
    method: str
    status: str


class PolicyChangeDetailResponse(BaseModel):
    id: UUID
    change_type: str
    summary: str
    effective_date: datetime | None
    reason_claim: ClaimDetailResponse | None
    status: str
    detected_at: datetime
    old_claim: ClaimDetailResponse | None
    new_claim: ClaimDetailResponse | None
    correspondence: CorrespondenceDetailResponse | None
