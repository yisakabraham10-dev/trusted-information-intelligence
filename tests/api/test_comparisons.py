import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from src.db.dependencies import get_db
from src.db.session import SessionLocal
from src.main import app
from src.models.claim import Claim
from src.models.claim_evidence import ClaimEvidence
from src.models.claim_structure import ClaimStructure
from src.models.document import Document
from src.models.document_version import DocumentVersion
from src.models.evidence import Evidence
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


def create_section(db, *, suffix):
    source = Source(
        name=f"Comparison API Source {suffix}",
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
        title=f"Comparison API Document {suffix}",
        document_type="PROCLAMATION",
        description=None,
        url=None,
    )
    db.add(document)
    db.flush()

    version = DocumentVersion(
        document_id=document.id,
        version_label=suffix,
        publication_date=None,
        effective_date=None,
        content_hash=f"comparison-{uuid.uuid4().hex}",
    )
    db.add(version)
    db.flush()

    section = Section(
        document_version_id=version.id,
        section_number="51(1)",
        title=None,
        page_start=3,
        page_end=3,
        raw_text="Imported goods must be removed within the applicable period.",
    )
    db.add(section)
    db.flush()

    return section


def create_claim(
    db,
    *,
    section,
    text,
    deadline_days,
    with_evidence=True,
):
    claim = Claim(
        section_id=section.id,
        claim_type="REQUIREMENT",
        text=text,
        normalized_text=text.upper(),
    )
    db.add(claim)
    db.flush()

    if with_evidence:
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

    structure = ClaimStructure(
        claim_id=claim.id,
        structure_type="RequirementStructure",
        structure={
            "actor": {
                "entity_id": None,
                "raw_text": "Importers",
            },
            "modality": "REQUIRED",
            "action": "submit",
            "object": {
                "entity_id": None,
                "raw_text": "Form X",
            },
            "deadline": {
                "value": str(Decimal(deadline_days)),
                "unit": "DAYS",
            },
            "exception_ids": [],
            "applicability_conditions": [],
        },
    )
    db.add(structure)
    db.flush()

    return claim


def test_compare_claims_returns_modified_change(client, db):
    old_section = create_section(db, suffix="old")
    new_section = create_section(db, suffix="new")

    old_claim = create_claim(
        db,
        section=old_section,
        text="Importers must submit Form X within 30 days.",
        deadline_days="30",
    )
    new_claim = create_claim(
        db,
        section=new_section,
        text="Importers must submit Form X within 45 days.",
        deadline_days="45",
    )

    db.commit()

    response = client.post(
        f"/claims/{old_claim.id}/compare/{new_claim.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["old_claim_id"] == str(old_claim.id)
    assert data["new_claim_id"] == str(new_claim.id)

    assert data["correspondence"]["relationship_type"] == "MODIFIED"
    assert data["correspondence"]["method"]
    assert "VALUE_CHANGED: 30 DAYS -> 45 DAYS" in (
        data["correspondence"]["changes"]
    )

    assert data["detection"]["change_type"] == "MODIFIED"
    assert data["policy_change"]["change_type"] == "MODIFIED"
    assert data["policy_change"]["policy_change_id"]


def test_compare_claims_returns_requires_review_without_evidence(
    client,
    db,
):
    old_section = create_section(db, suffix="old-no-evidence")
    new_section = create_section(db, suffix="new-no-evidence")

    old_claim = create_claim(
        db,
        section=old_section,
        text="Importers must submit Form X within 30 days.",
        deadline_days="30",
        with_evidence=False,
    )
    new_claim = create_claim(
        db,
        section=new_section,
        text="Importers must submit Form X within 45 days.",
        deadline_days="45",
        with_evidence=True,
    )

    db.commit()

    response = client.post(
        f"/claims/{old_claim.id}/compare/{new_claim.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["correspondence"] is None
    assert data["detection"]["change_type"] == "REQUIRES_REVIEW"
    assert data["policy_change"] is None


def test_compare_claims_returns_404_when_old_claim_does_not_exist(
    client,
    db,
):
    section = create_section(db, suffix="new-only")

    new_claim = create_claim(
        db,
        section=section,
        text="Importers must submit Form X within 45 days.",
        deadline_days="45",
    )

    db.commit()

    missing_claim_id = uuid.uuid4()

    response = client.post(
        f"/claims/{missing_claim_id}/compare/{new_claim.id}"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": f"Old claim not found: {missing_claim_id}"
    }


def test_compare_claims_returns_404_when_new_claim_does_not_exist(
    client,
    db,
):
    section = create_section(db, suffix="old-only")

    old_claim = create_claim(
        db,
        section=section,
        text="Importers must submit Form X within 30 days.",
        deadline_days="30",
    )

    db.commit()

    missing_claim_id = uuid.uuid4()

    response = client.post(
        f"/claims/{old_claim.id}/compare/{missing_claim_id}"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": f"New claim not found: {missing_claim_id}"
    }
