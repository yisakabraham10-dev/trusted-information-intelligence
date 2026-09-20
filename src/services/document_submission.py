from datetime import datetime
from hashlib import sha256
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.exceptions import ValidationError
from src.models.document_submission import DocumentSubmission


class DocumentSubmissionService:
    """
    Store and register human-curated regulatory document submissions.

    This service does not:
    - parse PDF contents
    - extract claims
    - interpret legal meaning
    - determine policy changes
    - ingest accepted documents

    Acceptance is handled separately so that upload and review remain
    distinct workflow stages.
    """

    def __init__(
        self,
        storage_dir: str | Path = "storage/document_submissions",
    ) -> None:
        self.storage_dir = Path(storage_dir)

    def create(
        self,
        db: Session,
        *,
        file: UploadFile,
    ) -> DocumentSubmission:
        if not file.filename:
            raise ValidationError(
                "A filename is required."
            )

        if not file.filename.lower().endswith(".pdf"):
            raise ValidationError(
                "Only PDF files are accepted."
            )

        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        content = file.file.read()

        if not content:
            raise ValidationError(
                "The uploaded PDF is empty."
            )

        content_hash = sha256(content).hexdigest()

        existing = db.scalar(
            select(DocumentSubmission).where(
                DocumentSubmission.content_hash == content_hash
            )
        )

        if existing is not None:
            raise ValidationError(
                "This document has already been submitted."
            )

        from uuid import uuid4

        submission_id = uuid4()

        storage_path = (
            self.storage_dir
            / f"{submission_id}.pdf"
        )

        storage_path.write_bytes(content)

        submission = DocumentSubmission(
            id=submission_id,
            original_filename=file.filename,
            storage_path=str(storage_path),
            content_hash=content_hash,
            status="PENDING_REVIEW",
        )

        db.add(submission)
        db.flush()

        return submission

    def review(
        self,
        db: Session,
        *,
        submission_id: UUID,
        decision: str,
        reviewed_by: str,
        rejection_reason: str | None = None,
    ) -> DocumentSubmission:
        submission = db.scalar(
            select(DocumentSubmission).where(
                DocumentSubmission.id == submission_id
            )
        )

        if submission is None:
            raise ValidationError(
                "Document submission not found."
            )

        if submission.status != "PENDING_REVIEW":
            raise ValidationError(
                "Only pending submissions can be reviewed."
            )

        normalized_decision = decision.strip().upper()

        if normalized_decision not in {"ACCEPT", "REJECT"}:
            raise ValidationError(
                "Decision must be ACCEPT or REJECT."
            )

        normalized_reviewer = reviewed_by.strip()

        if not normalized_reviewer:
            raise ValidationError(
                "Reviewer is required."
            )

        if (
            normalized_decision == "REJECT"
            and not rejection_reason
        ):
            raise ValidationError(
                "A rejection reason is required."
            )

        submission.status = (
            "ACCEPTED"
            if normalized_decision == "ACCEPT"
            else "REJECTED"
        )
        submission.reviewed_at = datetime.utcnow()
        submission.reviewed_by = normalized_reviewer

        if normalized_decision == "REJECT":
            submission.rejection_reason = rejection_reason.strip()
        else:
            submission.rejection_reason = None

        db.flush()

        return submission
