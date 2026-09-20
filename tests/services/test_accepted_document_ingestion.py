from datetime import datetime
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.db.base import Base
from src.domain.exceptions import InvalidStateError, NotFoundError
from src.models.document_submission import DocumentSubmission
from src.models.source import Source
from src.services.accepted_document_ingestion import (
    AcceptedDocumentIngestionService,
)
from src.services.document_submission import DocumentSubmissionService


FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "customs_proclamation_1425_2026.pdf"
)


def make_pdf_upload() -> UploadFile:
    return UploadFile(
        filename="customs.pdf",
        file=BytesIO(FIXTURE_PATH.read_bytes()),
    )


def test_ingest_accepted_submission_persists_document(tmp_path):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        submission_service = DocumentSubmissionService(
            storage_dir=tmp_path,
        )

        submission = submission_service.create(
            db,
            file=make_pdf_upload(),
        )

        submission_service.review(
            db,
            submission_id=submission.id,
            decision="ACCEPT",
            reviewed_by="admin",
        )

        source = Source(
            name="Federal Negarit Gazette",
            authority_tier="PRIMARY",
            institution_type="OFFICIAL_PUBLICATION",
            is_active=True,
        )

        db.add(source)
        db.flush()

        result = AcceptedDocumentIngestionService().ingest(
            db,
            submission_id=submission.id,
            source_id=source.id,
            title="Customs Proclamation (Further Amendment) Proclamation",
            document_type="PROCLAMATION",
            version_label="1425/2026",
            publication_date=datetime(2026, 7, 23),
            effective_date=datetime(2026, 7, 23),
        )

        assert result.created is True
        assert result.document.id is not None
        assert result.document_version.id is not None

        section_numbers = {
            section.section_number
            for section in result.sections
        }

        assert "51(1)" in section_numbers
        assert "51(2)" in section_numbers
        assert "51(7)" in section_numbers
        assert "51(8)" in section_numbers

        assert len(result.sections) == len(result.evidence)


def test_ingest_rejects_pending_submission(tmp_path):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        submission_service = DocumentSubmissionService(
            storage_dir=tmp_path,
        )

        submission = submission_service.create(
            db,
            file=make_pdf_upload(),
        )

        source = Source(
            name="Federal Negarit Gazette",
            authority_tier="PRIMARY",
            institution_type="OFFICIAL_PUBLICATION",
            is_active=True,
        )

        db.add(source)
        db.flush()

        with pytest.raises(
            InvalidStateError,
            match="Only accepted document submissions",
        ):
            AcceptedDocumentIngestionService().ingest(
                db,
                submission_id=submission.id,
                source_id=source.id,
                title="Customs Proclamation",
                document_type="PROCLAMATION",
            )


def test_ingest_rejects_unknown_submission():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        with pytest.raises(
            NotFoundError,
            match="Document submission not found",
        ):
            AcceptedDocumentIngestionService().ingest(
                db,
                submission_id=uuid4(),
                source_id=uuid4(),
                title="Customs Proclamation",
                document_type="PROCLAMATION",
            )
