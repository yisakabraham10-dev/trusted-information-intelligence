from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentSubmissionResponse(BaseModel):
    id: UUID
    original_filename: str
    content_hash: str
    status: str
    uploaded_at: datetime


class DocumentSubmissionReviewRequest(BaseModel):
    decision: str
    reviewed_by: str
    rejection_reason: str | None = None


class DocumentSubmissionReviewResponse(BaseModel):
    id: UUID
    original_filename: str
    status: str
    reviewed_at: datetime
    reviewed_by: str
    rejection_reason: str | None


class DocumentSubmissionIngestionRequest(BaseModel):
    source_id: UUID
    title: str
    document_type: str
    version_label: str | None = None
    publication_date: datetime | None = None
    effective_date: datetime | None = None
    url: str | None = None
    description: str | None = None
    notes: str | None = None


class DocumentSubmissionIngestionResponse(BaseModel):
    document_id: UUID
    document_version_id: UUID
    section_count: int
    evidence_count: int
    created: bool
