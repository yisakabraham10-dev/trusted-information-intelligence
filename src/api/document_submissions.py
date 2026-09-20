from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.dependencies import get_db
from src.domain.exceptions import (
    InvalidStateError,
    NotFoundError,
    ValidationError,
)
from src.models.document_submission import DocumentSubmission
from src.schemas.document_submission import (
    DocumentSubmissionIngestionRequest,
    DocumentSubmissionIngestionResponse,
    DocumentSubmissionResponse,
    DocumentSubmissionReviewRequest,
    DocumentSubmissionReviewResponse,
)
from src.services.accepted_document_ingestion import (
    AcceptedDocumentIngestionService,
)
from src.services.document_submission import DocumentSubmissionService


router = APIRouter(
    prefix="/document-submissions",
    tags=["document-submissions"],
)


@router.post(
    "",
    response_model=DocumentSubmissionResponse,
)
def create_document_submission(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        submission = DocumentSubmissionService().create(
            db,
            file=file,
        )
        db.commit()
    except ValidationError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return submission


@router.post(
    "/{submission_id}/review",
    response_model=DocumentSubmissionReviewResponse,
)
def review_document_submission(
    submission_id: UUID,
    request: DocumentSubmissionReviewRequest,
    db: Session = Depends(get_db),
):
    try:
        submission = DocumentSubmissionService().review(
            db,
            submission_id=submission_id,
            decision=request.decision,
            reviewed_by=request.reviewed_by,
            rejection_reason=request.rejection_reason,
        )
        db.commit()
    except ValidationError as exc:
        db.rollback()

        status_code = (
            404
            if str(exc) == "Document submission not found."
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc

    return submission


@router.post(
    "/{submission_id}/ingest",
    response_model=DocumentSubmissionIngestionResponse,
)
def ingest_document_submission(
    submission_id: UUID,
    request: DocumentSubmissionIngestionRequest,
    db: Session = Depends(get_db),
):
    try:
        result = AcceptedDocumentIngestionService().ingest(
            db,
            submission_id=submission_id,
            source_id=request.source_id,
            title=request.title,
            document_type=request.document_type,
            version_label=request.version_label,
            publication_date=request.publication_date,
            effective_date=request.effective_date,
            url=request.url,
            description=request.description,
            notes=request.notes,
        )

        db.commit()

    except NotFoundError as exc:
        db.rollback()

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except InvalidStateError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except ValidationError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return DocumentSubmissionIngestionResponse(
        document_id=result.document.id,
        document_version_id=result.document_version.id,
        section_count=len(result.sections),
        evidence_count=len(result.evidence),
        created=result.created,
    )


@router.get(
    "/{submission_id}/file",
)
def preview_document_submission(
    submission_id: UUID,
    db: Session = Depends(get_db),
):
    submission = db.scalar(
        select(DocumentSubmission).where(
            DocumentSubmission.id == submission_id
        )
    )

    if submission is None:
        raise HTTPException(
            status_code=404,
            detail="Document submission not found.",
        )

    path = Path(submission.storage_path)

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Submitted document file not found.",
        )

    return FileResponse(
        path=path,
        media_type="application/pdf",
        content_disposition_type="inline",
        filename=submission.original_filename,
    )
