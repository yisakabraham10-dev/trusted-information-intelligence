import uuid

import pytest
from fastapi.testclient import TestClient

from src.db.dependencies import get_db
from src.db.session import SessionLocal
from src.main import app
from src.models.claim import Claim
from src.models.document import Document
from src.models.document_version import DocumentVersion
from src.models.section import Section
from src.models.source import Source


@pytest.fixture
def db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
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


def create_section(db):
    source = Source(
        name="API Test Source",
        authority_tier="PRIMARY",
        base_url=None,
        institution_type=None,
        description=None,
        is_active=True,
    )
    db.add(source)
    db.flush()

    document = Document(
        source_id=source.id,
        title="API Test Document",
        document_type="PROCLAMATION",
        description=None,
        url=None,
    )
    db.add(document)
    db.flush()

    version = DocumentVersion(
        document_id=document.id,
        version_label="API Test Version",
        publication_date=None,
        effective_date=None,
        content_hash=f"api-test-{uuid.uuid4()}",
    )
    db.add(version)
    db.flush()

    section = Section(
        document_version_id=version.id,
        section_number="51(1)",
        title=None,
        page_start=3,
        page_end=3,
        raw_text="Imported goods must be removed within 45 days.",
    )
    db.add(section)
    db.flush()

    return section


def test_get_claim_returns_claim(client, db):
    section = create_section(db)

    claim = Claim(
        section_id=section.id,
        claim_type="REQUIREMENT",
        text="Goods must be removed within forty-five days.",
        normalized_text=(
            "GOODS MUST BE REMOVED WITHIN FORTY-FIVE DAYS."
        ),
    )

    db.add(claim)
    db.commit()

    response = client.get(f"/claims/{claim.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(claim.id)
    assert data["section_id"] == str(section.id)
    assert data["claim_type"] == "REQUIREMENT"
    assert data["text"] == (
        "Goods must be removed within forty-five days."
    )
    assert data["normalized_text"] == (
        "GOODS MUST BE REMOVED WITHIN FORTY-FIVE DAYS."
    )
    assert data["status"] == "ACTIVE"


def test_get_claim_returns_404_when_claim_does_not_exist(client):
    claim_id = uuid.uuid4()

    response = client.get(f"/claims/{claim_id}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Claim not found."
    }
