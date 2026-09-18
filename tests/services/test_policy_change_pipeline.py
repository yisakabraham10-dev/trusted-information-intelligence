import uuid
from datetime import datetime
from decimal import Decimal

import pytest

from src.db.session import SessionLocal
from src.models.claim import Claim
from src.models.claim_correspondence import ClaimCorrespondence
from src.models.document import Document
from src.models.document_version import DocumentVersion
from src.models.policy_change import PolicyChange
from src.models.section import Section
from src.models.source import Source
from src.services.change_detector import ChangeDetector
from src.services.claim_correspondence import CorrespondenceEvaluator
from src.services.claim_structure import (
    Duration,
    EntityRef,
    RequirementStructure,
)
from src.services.policy_change_service import PolicyChangeService


@pytest.fixture
def session():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.rollback()
        db.close()


def create_section(
    session,
    *,
    suffix: str,
) -> Section:
    source = Source(
        id=uuid.uuid4(),
        name=f"Pipeline Test Source {suffix}",
        authority_tier="PRIMARY",
        institution_type="GOVERNMENT",
        base_url="https://example.com",
        description="End-to-end test source.",
        is_active=True,
    )

    session.add(source)
    session.flush()

    document = Document(
        id=uuid.uuid4(),
        source_id=source.id,
        title=f"Pipeline Test Document {suffix}",
        document_type="REGULATION",
        url="https://example.com/document",
        description="End-to-end test document.",
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
        title="Import Requirements",
        page_start=1,
        page_end=1,
        raw_text="Importers must submit Form X within the specified period.",
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


def create_requirement(
    *,
    deadline_days: str,
) -> RequirementStructure:
    return RequirementStructure(
        actor=EntityRef(
            entity_id=None,
            raw_text="importer",
        ),
        modality="REQUIRED",
        action="submit",
        object=EntityRef(
            entity_id=None,
            raw_text="Form X",
        ),
        deadline=Duration(
            value=Decimal(deadline_days),
            unit="days",
        ),
    )


def test_modified_requirement_flows_into_policy_change(
    session,
):
    old_section = create_section(
        session,
        suffix="old",
    )

    new_section = create_section(
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

    old_structure = create_requirement(
        deadline_days="30",
    )

    new_structure = create_requirement(
        deadline_days="45",
    )

    # 1. Evaluate correspondence.
    correspondence_result = CorrespondenceEvaluator().evaluate(
        old_claim,
        new_claim,
        old_structure=old_structure,
        new_structure=new_structure,
    )

    assert correspondence_result.relationship_type == "MODIFIED"
    assert (
        correspondence_result.method
        == "REQUIREMENT_STRUCTURE"
    )

    # 2. Persist the correspondence.
    correspondence = ClaimCorrespondence(
        id=uuid.uuid4(),
        claim_a_id=old_claim.id,
        claim_b_id=new_claim.id,
        relationship_type=(
            correspondence_result.relationship_type
        ),
        confidence=correspondence_result.confidence,
        method=correspondence_result.method,
        status="VERIFIED",
    )

    session.add(correspondence)
    session.flush()

    # 3. Detect the policy change.
    detection = ChangeDetector().detect(
        correspondence_result,
    )

    assert detection is not None
    assert detection.change_type == "MODIFIED"

    # 4. Persist the policy change.
    persistence_result = PolicyChangeService().create(
        session,
        detection=detection,
        claim_correspondence=correspondence,
        old_claim=old_claim,
        new_claim=new_claim,
        effective_date=datetime(2026, 10, 1),
    )

    session.commit()

    # 5. Verify the final persisted result.
    policy_change = session.get(
        PolicyChange,
        persistence_result.policy_change_id,
    )

    assert policy_change is not None
    assert policy_change.change_type == "MODIFIED"
    assert (
        policy_change.summary
        == (
            "An existing claim was modified: "
            "VALUE_CHANGED: 30 days -> 45 days."
        )
    )
    assert policy_change.effective_date == datetime(
        2026,
        10,
        1,
    )