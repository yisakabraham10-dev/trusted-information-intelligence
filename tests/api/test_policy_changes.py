import uuid

import pytest
from fastapi.testclient import TestClient

from src.db.dependencies import get_db
from src.db.session import SessionLocal
from src.main import app
from src.models.claim import Claim
from src.models.claim_correspondence import ClaimCorrespondence
from src.models.claim_evidence import ClaimEvidence
from src.models.document import Document
from src.models.document_version import DocumentVersion
from src.models.evidence import Evidence
from src.models.policy_change import PolicyChange
from src.models.policy_change_claim import PolicyChangeClaim
from src.models.policy_change_correspondence import (
    PolicyChangeCorrespondence,
)
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


def create_claim_graph(db, *, suffix, text):
    source = Source(
        name=f"Detail API Source {suffix}",
        authority_tier="PRIMARY",
        base_url="https://example.gov.et",
        institution_type="GOVERNMENT",
        description=None,
        is_active=True,
    )
    db.add(source)
    db.flush()

    document = Document(
        source_id=source.id,
        title=f"Detail API Document {suffix}",
        document_type="PROCLAMATION",
        description=None,
        url="https://example.gov.et/document.pdf",
    )
    db.add(document)
    db.flush()

    version = DocumentVersion(
        document_id=document.id,
        version_label=suffix,
        publication_date=None,
        effective_date=None,
        content_hash=f"detail-{uuid.uuid4().hex}",
    )
    db.add(version)
    db.flush()

    section = Section(
        document_version_id=version.id,
        section_number="51(1)",
        title="Temporary customs storage",
        page_start=3,
        page_end=3,
        raw_text=text,
    )
    db.add(section)
    db.flush()

    claim = Claim(
        section_id=section.id,
        claim_type="REQUIREMENT",
        text=text,
        normalized_text=text.upper(),
    )
    db.add(claim)
    db.flush()

    evidence = Evidence(
        section_id=section.id,
        page=3,
        quote=text,
        confidence="HIGH",
    )
    db.add(evidence)
    db.flush()

    db.add(
        ClaimEvidence(
            claim_id=claim.id,
            evidence_id=evidence.id,
            relation_type="SUPPORTS",
            strength=1.0,
        )
    )
    db.flush()

    return claim


def create_policy_change_detail_graph(db):
    old_text = (
        "Imported goods must be removed within 60 days."
    )
    new_text = (
        "Imported goods must be removed within 45 days."
    )

    old_claim = create_claim_graph(
        db,
        suffix="old",
        text=old_text,
    )
    new_claim = create_claim_graph(
        db,
        suffix="new",
        text=new_text,
    )

    correspondence = ClaimCorrespondence(
        claim_a_id=old_claim.id,
        claim_b_id=new_claim.id,
        relationship_type="MODIFIED",
        confidence=1.0,
        method="STRUCTURED",
        status="CONFIRMED",
    )
    db.add(correspondence)
    db.flush()

    policy_change = PolicyChange(
        change_type="MODIFIED",
        summary=(
            "An existing claim was modified: "
            "deadline changed from 60 days to 45 days."
        ),
        effective_date=None,
        reason_claim_id=None,
    )
    db.add(policy_change)
    db.flush()

    db.add_all(
        [
            PolicyChangeClaim(
                policy_change_id=policy_change.id,
                claim_id=old_claim.id,
                role="OLD",
            ),
            PolicyChangeClaim(
                policy_change_id=policy_change.id,
                claim_id=new_claim.id,
                role="NEW",
            ),
            PolicyChangeCorrespondence(
                policy_change_id=policy_change.id,
                correspondence_id=correspondence.id,
            ),
        ]
    )
    db.commit()

    return policy_change, old_claim, new_claim


def test_get_policy_change_returns_policy_change(client, db):
    policy_change = PolicyChange(
        change_type="MODIFIED",
        summary="An existing claim was modified: deadline changed from 60 days to 45 days.",
        effective_date=None,
        reason_claim_id=None,
    )

    db.add(policy_change)
    db.commit()

    response = client.get(
        f"/policy-changes/{policy_change.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(policy_change.id)
    assert data["change_type"] == "MODIFIED"
    assert data["summary"] == (
        "An existing claim was modified: "
        "deadline changed from 60 days to 45 days."
    )
    assert data["effective_date"] is None
    assert data["reason_claim_id"] is None
    assert data["status"] == "ACTIVE"


def test_get_policy_change_returns_404_when_policy_change_does_not_exist(
    client,
):
    policy_change_id = uuid.uuid4()

    response = client.get(
        f"/policy-changes/{policy_change_id}"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Policy change not found."
    }


def test_get_policy_change_detail_returns_evidence_chain(
    client,
    db,
):
    policy_change, old_claim, new_claim = (
        create_policy_change_detail_graph(db)
    )

    response = client.get(
        f"/policy-changes/{policy_change.id}/detail"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(policy_change.id)
    assert data["change_type"] == "MODIFIED"

    assert data["old_claim"]["id"] == str(old_claim.id)
    assert data["old_claim"]["text"] == (
        "Imported goods must be removed within 60 days."
    )

    assert data["new_claim"]["id"] == str(new_claim.id)
    assert data["new_claim"]["text"] == (
        "Imported goods must be removed within 45 days."
    )

    assert data["correspondence"]["relationship_type"] == "MODIFIED"
    assert data["correspondence"]["confidence"] == 1.0
    assert data["correspondence"]["method"] == "STRUCTURED"

    old_evidence = data["old_claim"]["evidence"][0]

    assert old_evidence["page"] == 3
    assert old_evidence["quote"] == (
        "Imported goods must be removed within 60 days."
    )
    assert old_evidence["relation_type"] == "SUPPORTS"
    assert old_evidence["strength"] == 1.0

    old_section = data["old_claim"]["section"]

    assert old_section["section_number"] == "51(1)"
    assert old_section["page_start"] == 3
    assert old_section["page_end"] == 3

    old_document = old_section["document"]

    assert old_document["title"] == "Detail API Document old"
    assert old_document["document_type"] == "PROCLAMATION"
    assert old_document["version_label"] == "old"

    assert old_document["source"]["name"] == "Detail API Source old"
    assert old_document["source"]["authority_tier"] == "PRIMARY"


def test_get_policy_change_detail_returns_404_when_policy_change_does_not_exist(
    client,
):
    policy_change_id = uuid.uuid4()

    response = client.get(
        f"/policy-changes/{policy_change_id}/detail"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Policy change not found."
    }
