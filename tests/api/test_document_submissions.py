import io
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.db.dependencies import get_db
from src.db.session import SessionLocal
from src.main import app
from src.models.document import Document
from src.models.document_submission import DocumentSubmission
from src.models.document_version import DocumentVersion
from src.models.evidence import Evidence
from src.models.section import Section
from src.models.source import Source


@pytest.fixture
def db():
    session = SessionLocal()

    try:
        session.query(DocumentSubmission).delete()
        session.commit()

        yield session

    finally:
        session.query(DocumentSubmission).delete()
        session.commit()
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_create_document_submission_returns_pending_review(
    client,
    db,
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    response = client.post(
        "/document-submissions",
        files={
            "file": (
                "customs.pdf",
                io.BytesIO(b"%PDF-demo-content"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["original_filename"] == "customs.pdf"
    assert data["status"] == "PENDING_REVIEW"
    assert data["content_hash"]
    assert data["id"]
    assert data["uploaded_at"]

    submission = db.get(
        DocumentSubmission,
        uuid.UUID(data["id"]),
    )

    assert submission is not None
    assert submission.original_filename == "customs.pdf"
    assert submission.status == "PENDING_REVIEW"


def test_create_document_submission_rejects_non_pdf(
    client,
):
    response = client.post(
        "/document-submissions",
        files={
            "file": (
                "customs.txt",
                io.BytesIO(b"not a pdf"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Only PDF files are accepted."
    }


def test_create_document_submission_rejects_empty_file(
    client,
):
    response = client.post(
        "/document-submissions",
        files={
            "file": (
                "empty.pdf",
                io.BytesIO(b""),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "The uploaded PDF is empty."
    }


def test_create_document_submission_rejects_duplicate_content(
    client,
    db,
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    first_response = client.post(
        "/document-submissions",
        files={
            "file": (
                "first.pdf",
                io.BytesIO(b"%PDF-same-content"),
                "application/pdf",
            )
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/document-submissions",
        files={
            "file": (
                "second.pdf",
                io.BytesIO(b"%PDF-same-content"),
                "application/pdf",
            )
        },
    )

    assert second_response.status_code == 400
    assert second_response.json() == {
        "detail": "This document has already been submitted."
    }


def test_preview_document_submission_returns_pdf(
    client,
    db,
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    upload_response = client.post(
        "/document-submissions",
        files={
            "file": (
                "customs.pdf",
                io.BytesIO(b"%PDF-preview-content"),
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 200

    submission_id = upload_response.json()["id"]

    response = client.get(
        f"/document-submissions/{submission_id}/file"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content == b"%PDF-preview-content"
    assert (
        "inline"
        in response.headers["content-disposition"]
    )


def test_preview_document_submission_returns_404_for_unknown_submission(
    client,
):
    submission_id = uuid.uuid4()

    response = client.get(
        f"/document-submissions/{submission_id}/file"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document submission not found."
    }


def test_preview_document_submission_returns_404_when_file_is_missing(
    client,
    db,
    tmp_path,
):
    submission = DocumentSubmission(
        original_filename="missing.pdf",
        storage_path=str(
            tmp_path / "does-not-exist.pdf"
        ),
        content_hash="a" * 64,
        status="PENDING_REVIEW",
    )

    db.add(submission)
    db.commit()

    response = client.get(
        f"/document-submissions/{submission.id}/file"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Submitted document file not found."
    }


def test_review_document_submission_accepts_pending_submission(
    client,
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    upload_response = client.post(
        "/document-submissions",
        files={
            "file": (
                "customs.pdf",
                io.BytesIO(b"%PDF-review-accept"),
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 200

    submission_id = upload_response.json()["id"]

    response = client.post(
        f"/document-submissions/{submission_id}/review",
        json={
            "decision": "ACCEPT",
            "reviewed_by": "admin",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == submission_id
    assert data["original_filename"] == "customs.pdf"
    assert data["status"] == "ACCEPTED"
    assert data["reviewed_by"] == "admin"
    assert data["reviewed_at"]
    assert data["rejection_reason"] is None


def test_review_document_submission_rejects_with_reason(
    client,
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    upload_response = client.post(
        "/document-submissions",
        files={
            "file": (
                "customs.pdf",
                io.BytesIO(b"%PDF-review-reject"),
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 200

    submission_id = upload_response.json()["id"]

    response = client.post(
        f"/document-submissions/{submission_id}/review",
        json={
            "decision": "REJECT",
            "reviewed_by": "admin",
            "rejection_reason": "Not an official publication.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "REJECTED"
    assert data["reviewed_by"] == "admin"
    assert data["reviewed_at"]
    assert (
        data["rejection_reason"]
        == "Not an official publication."
    )


def test_review_document_submission_reject_requires_reason(
    client,
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    upload_response = client.post(
        "/document-submissions",
        files={
            "file": (
                "customs.pdf",
                io.BytesIO(b"%PDF-review-no-reason"),
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 200

    submission_id = upload_response.json()["id"]

    response = client.post(
        f"/document-submissions/{submission_id}/review",
        json={
            "decision": "REJECT",
            "reviewed_by": "admin",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "A rejection reason is required."
    }


def test_review_document_submission_rejects_invalid_decision(
    client,
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    upload_response = client.post(
        "/document-submissions",
        files={
            "file": (
                "customs.pdf",
                io.BytesIO(b"%PDF-review-invalid"),
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 200

    submission_id = upload_response.json()["id"]

    response = client.post(
        f"/document-submissions/{submission_id}/review",
        json={
            "decision": "MAYBE",
            "reviewed_by": "admin",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Decision must be ACCEPT or REJECT."
    }


def test_review_document_submission_returns_404_for_unknown_submission(
    client,
):
    submission_id = uuid.uuid4()

    response = client.post(
        f"/document-submissions/{submission_id}/review",
        json={
            "decision": "ACCEPT",
            "reviewed_by": "admin",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document submission not found."
    }


def test_review_document_submission_rejects_already_reviewed_submission(
    client,
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    upload_response = client.post(
        "/document-submissions",
        files={
            "file": (
                "customs.pdf",
                io.BytesIO(b"%PDF-review-twice"),
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 200

    submission_id = upload_response.json()["id"]

    first_response = client.post(
        f"/document-submissions/{submission_id}/review",
        json={
            "decision": "ACCEPT",
            "reviewed_by": "admin",
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        f"/document-submissions/{submission_id}/review",
        json={
            "decision": "REJECT",
            "reviewed_by": "admin",
            "rejection_reason": "Too late.",
        },
    )

    assert second_response.status_code == 400
    assert second_response.json() == {
        "detail": "Only pending submissions can be reviewed."
    }


def create_ingestion_source(db):
    source = Source(
        name="API Ingestion Test Source",
        authority_tier="PRIMARY",
        base_url=None,
        institution_type=None,
        description=None,
        is_active=True,
    )

    db.add(source)
    db.flush()

    return source


def test_ingest_accepted_document_submission(
    client,
    db,
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    source = create_ingestion_source(db)
    db.commit()

    pdf_path = (
        Path(__file__).resolve().parents[1]
        / "fixtures"
        / "customs_proclamation_1425_2026.pdf"
    )

    upload_response = client.post(
        "/document-submissions",
        files={
            "file": (
                "customs_proclamation_1425_2026.pdf",
                open(pdf_path, "rb"),
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 200

    submission_id = upload_response.json()["id"]

    review_response = client.post(
        f"/document-submissions/{submission_id}/review",
        json={
            "decision": "ACCEPT",
            "reviewed_by": "admin",
        },
    )

    assert review_response.status_code == 200

    response = client.post(
        f"/document-submissions/{submission_id}/ingest",
        json={
            "source_id": str(source.id),
            "title": "Customs Proclamation (Further Amendment) Proclamation",
            "document_type": "PROCLAMATION",
            "version_label": "1425/2026",
            "publication_date": "2026-07-23T00:00:00",
            "effective_date": "2026-07-23T00:00:00",
            "url": (
                "https://justice.gov.et/wp-content/uploads/2026/08/"
                "%E1%8A%A0%E1%8B%8B%E1%8C%85-%E1%89%81%E1%8C%A5%E1%88%AD-"
                "1425-2018.pdf"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"]
    assert data["document_version_id"]
    assert data["section_count"] > 0
    assert data["evidence_count"] > 0
    assert data["created"] is True

    document = db.get(
        Document,
        uuid.UUID(data["document_id"]),
    )

    version = db.get(
        DocumentVersion,
        uuid.UUID(data["document_version_id"]),
    )

    assert document is not None
    assert version is not None
    assert document.source_id == source.id
    assert document.url == (
        "https://justice.gov.et/wp-content/uploads/2026/08/"
        "%E1%8A%A0%E1%8B%8B%E1%8C%85-%E1%89%81%E1%8C%A5%E1%88%AD-"
        "1425-2018.pdf"
    )
    assert version.document_id == document.id

    sections = db.query(Section).filter(
        Section.document_version_id == version.id
    ).all()

    evidence = db.query(Evidence).join(
        Section,
        Evidence.section_id == Section.id,
    ).filter(
        Section.document_version_id == version.id
    ).all()

    assert len(sections) == data["section_count"]
    assert len(evidence) == data["evidence_count"]

    section_numbers = {
        section.section_number
        for section in sections
    }

    assert "51(1)" in section_numbers
    assert "51(2)" in section_numbers
    assert "51(7)" in section_numbers
    assert "51(8)" in section_numbers


def test_ingest_pending_document_submission_returns_400(
    client,
    tmp_path,
    monkeypatch,
    db,
):
    monkeypatch.chdir(tmp_path)

    source = create_ingestion_source(db)
    db.commit()

    upload_response = client.post(
        "/document-submissions",
        files={
            "file": (
                "pending.pdf",
                io.BytesIO(b"%PDF-pending"),
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 200

    submission_id = upload_response.json()["id"]

    response = client.post(
        f"/document-submissions/{submission_id}/ingest",
        json={
            "source_id": str(source.id),
            "title": "Pending Document",
            "document_type": "PROCLAMATION",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "Only accepted document submissions can be ingested."
        )
    }


def test_ingest_unknown_document_submission_returns_404(
    client,
    db,
):
    source = create_ingestion_source(db)
    db.commit()

    submission_id = uuid.uuid4()

    response = client.post(
        f"/document-submissions/{submission_id}/ingest",
        json={
            "source_id": str(source.id),
            "title": "Unknown Document",
            "document_type": "PROCLAMATION",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document submission not found."
    }
