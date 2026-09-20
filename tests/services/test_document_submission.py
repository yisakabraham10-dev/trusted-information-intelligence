from io import BytesIO

import pytest
from fastapi import UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.db.base import Base
from src.domain.exceptions import ValidationError
from src.models.document_submission import DocumentSubmission
from src.services.document_submission import DocumentSubmissionService


def make_upload(
    filename: str,
    content: bytes,
) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=BytesIO(content),
    )


def test_create_submission_stores_pdf_and_marks_pending_review(
    tmp_path,
):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = DocumentSubmissionService(
            storage_dir=tmp_path,
        )

        upload = make_upload(
            "customs.pdf",
            b"%PDF-demo-content",
        )

        submission = service.create(
            db,
            file=upload,
        )

        assert isinstance(
            submission,
            DocumentSubmission,
        )

        assert submission.original_filename == "customs.pdf"
        assert submission.status == "PENDING_REVIEW"
        assert submission.content_hash
        assert submission.storage_path

        stored_file = tmp_path / f"{submission.id}.pdf"

        assert stored_file.exists()
        assert stored_file.read_bytes() == b"%PDF-demo-content"


def test_create_submission_rejects_non_pdf(
    tmp_path,
):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = DocumentSubmissionService(
            storage_dir=tmp_path,
        )

        upload = make_upload(
            "customs.txt",
            b"not a pdf",
        )

        with pytest.raises(
            ValidationError,
            match="Only PDF",
        ):
            service.create(
                db,
                file=upload,
            )


def test_create_submission_rejects_empty_file(
    tmp_path,
):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = DocumentSubmissionService(
            storage_dir=tmp_path,
        )

        upload = make_upload(
            "empty.pdf",
            b"",
        )

        with pytest.raises(
            ValidationError,
            match="uploaded PDF is empty",
        ):
            service.create(
                db,
                file=upload,
            )


def test_create_submission_rejects_duplicate_content(
    tmp_path,
):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = DocumentSubmissionService(
            storage_dir=tmp_path,
        )

        first_upload = make_upload(
            "first.pdf",
            b"%PDF-same-content",
        )

        service.create(
            db,
            file=first_upload,
        )

        second_upload = make_upload(
            "second.pdf",
            b"%PDF-same-content",
        )

        with pytest.raises(
            ValidationError,
            match="already been submitted",
        ):
            service.create(
                db,
                file=second_upload,
            )


def test_review_accepts_pending_submission(
    tmp_path,
):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = DocumentSubmissionService(
            storage_dir=tmp_path,
        )

        submission = service.create(
            db,
            file=make_upload(
                "customs.pdf",
                b"%PDF-accept-content",
            ),
        )

        reviewed = service.review(
            db,
            submission_id=submission.id,
            decision="ACCEPT",
            reviewed_by="admin",
        )

        assert reviewed.status == "ACCEPTED"
        assert reviewed.reviewed_by == "admin"
        assert reviewed.reviewed_at is not None
        assert reviewed.rejection_reason is None


def test_review_rejects_pending_submission_with_reason(
    tmp_path,
):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = DocumentSubmissionService(
            storage_dir=tmp_path,
        )

        submission = service.create(
            db,
            file=make_upload(
                "customs.pdf",
                b"%PDF-reject-content",
            ),
        )

        reviewed = service.review(
            db,
            submission_id=submission.id,
            decision="REJECT",
            reviewed_by="admin",
            rejection_reason="Not an official publication.",
        )

        assert reviewed.status == "REJECTED"
        assert reviewed.reviewed_by == "admin"
        assert reviewed.reviewed_at is not None
        assert (
            reviewed.rejection_reason
            == "Not an official publication."
        )


def test_review_reject_requires_reason(
    tmp_path,
):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = DocumentSubmissionService(
            storage_dir=tmp_path,
        )

        submission = service.create(
            db,
            file=make_upload(
                "customs.pdf",
                b"%PDF-reject-no-reason",
            ),
        )

        with pytest.raises(
            ValidationError,
            match="rejection reason is required",
        ):
            service.review(
                db,
                submission_id=submission.id,
                decision="REJECT",
                reviewed_by="admin",
            )


def test_review_rejects_invalid_decision(
    tmp_path,
):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = DocumentSubmissionService(
            storage_dir=tmp_path,
        )

        submission = service.create(
            db,
            file=make_upload(
                "customs.pdf",
                b"%PDF-invalid-decision",
            ),
        )

        with pytest.raises(
            ValidationError,
            match="Decision must be ACCEPT or REJECT",
        ):
            service.review(
                db,
                submission_id=submission.id,
                decision="MAYBE",
                reviewed_by="admin",
            )


def test_review_requires_reviewer(
    tmp_path,
):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = DocumentSubmissionService(
            storage_dir=tmp_path,
        )

        submission = service.create(
            db,
            file=make_upload(
                "customs.pdf",
                b"%PDF-no-reviewer",
            ),
        )

        with pytest.raises(
            ValidationError,
            match="Reviewer is required",
        ):
            service.review(
                db,
                submission_id=submission.id,
                decision="ACCEPT",
                reviewed_by="   ",
            )


def test_review_rejects_already_reviewed_submission(
    tmp_path,
):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = DocumentSubmissionService(
            storage_dir=tmp_path,
        )

        submission = service.create(
            db,
            file=make_upload(
                "customs.pdf",
                b"%PDF-already-reviewed",
            ),
        )

        service.review(
            db,
            submission_id=submission.id,
            decision="ACCEPT",
            reviewed_by="admin",
        )

        with pytest.raises(
            ValidationError,
            match="Only pending submissions can be reviewed",
        ):
            service.review(
                db,
                submission_id=submission.id,
                decision="REJECT",
                reviewed_by="admin",
                rejection_reason="Too late.",
            )


def test_review_rejects_unknown_submission(
    tmp_path,
):
    import uuid

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = DocumentSubmissionService(
            storage_dir=tmp_path,
        )

        with pytest.raises(
            ValidationError,
            match="Document submission not found",
        ):
            service.review(
                db,
                submission_id=uuid.uuid4(),
                decision="ACCEPT",
                reviewed_by="admin",
            )
