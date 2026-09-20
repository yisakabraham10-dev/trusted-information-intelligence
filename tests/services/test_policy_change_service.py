import uuid
from datetime import datetime

import pytest

from src.db.session import SessionLocal
from src.domain.exceptions import InvalidStateError
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
        name=f"Source {suffix}",
        authority_tier="PRIMARY",
        base_url=None,
        institution_type=None,
        description=None,
        is_active=True,
    )
    session.add(source)
    session.flush()

    document = Document(
        source_id=source.id,
        title=f"Document {suffix}",
        document_type="PROCLAMATION",
        description=None,
        url=None,
    )
    session.add(document)
    session.flush()

    version = DocumentVersion(
        document_id=document.id,
        version_label=f"Version {suffix}",
        publication_date=None,
        effective_date=None,
        content_hash=f"hash-{suffix}",
    )
    session.add(version)
    session.flush()

    section = Section(
        document_version_id=version.id,
        section_number=f"51({suffix})",
        title=None,
        page_start=3,
        page_end=3,
        raw_text="Imported goods must be removed within 45 days.",
    )
    session.add(section)
    session.flush()

    return section


def create_claim(
    session,
    *,
    section: Section,
    text: str,
) -> Claim:
    claim = Claim(
        section_id=section.id,
        claim_type="REQUIREMENT",
        text=text,
    )
    session.add(claim)
    session.flush()
    return claim


def test_policy_change_persists_old_claim_relationship(session):
    section = create_section_graph(session, suffix="old")
    old_claim = create_claim(
        session,
        section=section,
        text="Imported goods must be removed within 60 days.",
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

    policy_change = session.get(PolicyChange, result.policy_change_id)

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


def test_policy_change_persists_new_claim_relationship(session):
    section = create_section_graph(session, suffix="new")
    new_claim = create_claim(
        session,
        section=section,
        text="Imported goods must be removed within 45 days.",
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

    policy_change = session.get(PolicyChange, result.policy_change_id)

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


def test_policy_change_persists_correspondence(session):
    old_section = create_section_graph(session, suffix="old-correspondence")
    new_section = create_section_graph(session, suffix="new-correspondence")

    old_claim = create_claim(
        session,
        section=old_section,
        text="Imported goods must be removed within 60 days.",
    )

    new_claim = create_claim(
        session,
        section=new_section,
        text="Imported goods must be removed within 45 days.",
    )

    correspondence = ClaimCorrespondence(
        claim_a_id=old_claim.id,
        claim_b_id=new_claim.id,
        relationship_type="MODIFIED",
        confidence=1.0,
        method="STRUCTURED",
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
    )

    links = (
        session.query(PolicyChangeCorrespondence)
        .filter_by(policy_change_id=result.policy_change_id)
        .all()
    )

    assert len(links) == 1
    assert links[0].correspondence_id == correspondence.id


def test_policy_change_requires_at_least_one_claim(session):
    detection = ChangeDetectionResult(
        change_type="MODIFIED",
        summary="An existing claim was modified.",
    )

    with pytest.raises(
        InvalidStateError,
        match="At least one claim must be provided.",
    ):
        PolicyChangeService().create(
            session,
            detection=detection,
        )
