import uuid
from datetime import datetime

import pytest

from src.db.session import SessionLocal
from src.models.claim import Claim
from src.models.claim_correspondence import ClaimCorrespondence
from src.models.document import Document
from src.models.document_version import DocumentVersion
from src.models.policy_change import PolicyChange
from src.models.policy_change_claim import PolicyChangeClaim
from src.models.policy_change_correspondence import (
    PolicyChangeCorrespondence,
)
from src.models.section import Section
from src.models.source import Source
from src.services.change_detector import ChangeDetectionResult
from src.services.policy_change_service import PolicyChangeService


@pytest.fixture
def session():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.rollback()
        db.close()


def create_section_graph(session, *, suffix: str) -> Section:
    source = Source(
        id=uuid.uuid4(),
        name=f"Test Source {suffix}",
        authority_tier="PRIMARY",
        base_url="https://example.com",
        institution_type="GOVERNMENT",
        description="Test source.",
        is_active=True,
    )

    session.add(source)
    session.flush()

    document = Document(
        id=uuid.uuid4(),
        source_id=source.id,
        title=f"Test Document {suffix}",
        document_type="REGULATION",
        url="https://example.com/document",
        description="Test document.",
    )

    session.add(document)
    session.flush()

    document_version = DocumentVersion(
        id=uuid.uuid4(),
        document_id=document.id,
        version_label="1.0",
        publication_date=datetime(2026, 1, 1),
        effective_date=datetime(2026, 1, 1),
        content_hash=uuid.uuid4().hex * 2,
        status="CURRENT",
    )

    session.add(document_version)
    session.flush()

    section = Section(
        id=uuid.uuid4(),
        document_version_id=document_version.id,
        section_number="1",
        title="Requirements",
        page_start=1,
        page_end=1,
        raw_text="Import requirements.",
    )

    session.add(section)
    session.flush()

    return section


def create_claim(
    session,
    *,
    section_id,
    text: str,
) -> Claim:
    claim = Claim(
        id=uuid.uuid4(),
        section_id=section_id,
        claim_type="REQUIREMENT",
        text=text,
        normalized_text=" ".join(text.lower().split()),
        effective_from=None,
        effective_to=None,
        status="ACTIVE",
    )

    session.add(claim)
    session.flush()

    return claim


def test_create_modified_policy_change(session):
    old_section = create_section_graph(
        session,
        suffix="old",
    )

    new_section = create_section_graph(
        session,
        suffix="new",
    )

    old_claim = create_claim(
        session,
        section_id=old_section.id,
        text="Importers must submit Form X within 30 days.",
    )

    new_claim = create_claim(
        session,
        section_id=new_section.id,
        text="Importers must submit Form X within 45 days.",
    )

    correspondence = ClaimCorrespondence(
        id=uuid.uuid4(),
        claim_a_id=old_claim.id,
        claim_b_id=new_claim.id,
        relationship_type="MODIFIED",
        confidence=1.0,
        method="REQUIREMENT_STRUCTURE",
        status="VERIFIED",
    )

    session.add(correspondence)
    session.flush()

    detection = ChangeDetectionResult(
        change_type="MODIFIED",
        summary="An existing claim was modified.",
    )

    result = PolicyChangeService().create(
        session,
        detection=detection,
        claim_correspondence=correspondence,
        old_claim=old_claim,
        new_claim=new_claim,
        effective_date=datetime(2026, 10, 1),
    )

    session.commit()

    policy_change = session.get(
        PolicyChange,
        result.policy_change_id,
    )

    assert policy_change is not None
    assert policy_change.change_type == "MODIFIED"
    assert (
        policy_change.summary
        == "An existing claim was modified."
    )
    assert policy_change.effective_date == datetime(
        2026,
        10,
        1,
    )

    claim_links = (
        session.query(PolicyChangeClaim)
        .filter_by(policy_change_id=policy_change.id)
        .all()
    )

    assert len(claim_links) == 2

    roles = {
        link.claim_id: link.role
        for link in claim_links
    }

    assert roles[old_claim.id] == "OLD"
    assert roles[new_claim.id] == "NEW"

    correspondence_link = (
        session.query(PolicyChangeCorrespondence)
        .filter_by(policy_change_id=policy_change.id)
        .one()
    )

    assert (
        correspondence_link.correspondence_id
        == correspondence.id
    )


def test_create_added_policy_change(session):
    section = create_section_graph(
        session,
        suffix="added",
    )

    new_claim = create_claim(
        session,
        section_id=section.id,
        text="Importers must register electronically.",
    )

    detection = ChangeDetectionResult(
        change_type="ADDED",
        summary="A new claim was added.",
    )

    result = PolicyChangeService().create(
        session,
        detection=detection,
        new_claim=new_claim,
    )

    session.commit()

    policy_change = session.get(
        PolicyChange,
        result.policy_change_id,
    )

    assert policy_change is not None
    assert policy_change.change_type == "ADDED"

    claim_links = (
        session.query(PolicyChangeClaim)
        .filter_by(policy_change_id=policy_change.id)
        .all()
    )

    assert len(claim_links) == 1
    assert claim_links[0].claim_id == new_claim.id
    assert claim_links[0].role == "NEW"


def test_create_removed_policy_change(session):
    section = create_section_graph(
        session,
        suffix="removed",
    )

    old_claim = create_claim(
        session,
        section_id=section.id,
        text="Importers must submit Form X.",
    )

    detection = ChangeDetectionResult(
        change_type="REMOVED",
        summary="An existing claim was removed.",
    )

    result = PolicyChangeService().create(
        session,
        detection=detection,
        old_claim=old_claim,
    )

    session.commit()

    policy_change = session.get(
        PolicyChange,
        result.policy_change_id,
    )

    assert policy_change is not None
    assert policy_change.change_type == "REMOVED"

    claim_links = (
        session.query(PolicyChangeClaim)
        .filter_by(policy_change_id=policy_change.id)
        .all()
    )

    assert len(claim_links) == 1
    assert claim_links[0].claim_id == old_claim.id
    assert claim_links[0].role == "OLD"


def test_policy_change_requires_at_least_one_claim(session):
    detection = ChangeDetectionResult(
        change_type="MODIFIED",
        summary="An existing claim was modified.",
    )

    with pytest.raises(
        ValueError,
        match="At least one claim must be provided.",
    ):
        PolicyChangeService().create(
            session,
            detection=detection,
        )