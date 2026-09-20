from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.exceptions import InvalidStateError, NotFoundError
from src.models.document_submission import DocumentSubmission
from src.services.document_ingestion import DocumentIngestionService
from src.services.document_persistence import (
    DocumentPersistenceResult,
    DocumentPersistenceService,
)
from src.services.regulatory_structure import RegulatoryStructureParser


class AcceptedDocumentIngestionService:
    """
    Ingest an accepted human-curated document submission.

    Responsibilities:
    - verify that the submission exists
    - verify that the submission has been accepted
    - extract PDF text
    - parse regulatory structure
    - persist the document and its provenance

    This service does not:
    - review submissions
    - extract claims
    - determine policy changes
    - determine business applicability
    - commit transactions
    """

    def __init__(
        self,
        document_ingestion: DocumentIngestionService | None = None,
        structure_parser: RegulatoryStructureParser | None = None,
        persistence: DocumentPersistenceService | None = None,
    ) -> None:
        self.document_ingestion = (
            document_ingestion or DocumentIngestionService()
        )
        self.structure_parser = (
            structure_parser or RegulatoryStructureParser()
        )
        self.persistence = (
            persistence or DocumentPersistenceService()
        )

    def ingest(
        self,
        db: Session,
        *,
        submission_id: UUID,
        source_id: UUID,
        title: str,
        document_type: str,
        version_label: str | None = None,
        publication_date: datetime | None = None,
        effective_date: datetime | None = None,
        url: str | None = None,
        description: str | None = None,
        notes: str | None = None,
    ) -> DocumentPersistenceResult:
        submission = db.scalar(
            select(DocumentSubmission).where(
                DocumentSubmission.id == submission_id
            )
        )

        if submission is None:
            raise NotFoundError(
                "Document submission not found."
            )

        if submission.status != "ACCEPTED":
            raise InvalidStateError(
                "Only accepted document submissions can be ingested."
            )

        document = self.document_ingestion.extract(
            submission.storage_path
        )

        parsed_sections = self.structure_parser.parse(
            document.pages
        )

        return self.persistence.persist(
            db,
            source_id=source_id,
            pdf_path=submission.storage_path,
            title=title,
            document_type=document_type,
            parsed_sections=parsed_sections,
            version_label=version_label,
            publication_date=publication_date,
            effective_date=effective_date,
            url=url,
            description=description,
            notes=notes,
        )
