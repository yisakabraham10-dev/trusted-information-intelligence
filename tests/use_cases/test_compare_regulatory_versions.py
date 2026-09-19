import uuid
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.db.base import Base
from src.models.claim import Claim
from src.models.claim_correspondence import ClaimCorrespondence
from src.models.claim_structure import ClaimStructure as ClaimStructureModel
from src.models.policy_change import PolicyChange
from src.models.policy_change_claim import PolicyChangeClaim
from src.models.policy_change_correspondence import (
    PolicyChangeCorrespondence,
)
from src.models.section import Section
from src.models.document import Document
from src.models.document_version import DocumentVersion
from src.models.source import Source
from src.services.claim_structure import (
    Duration,
    EntityRef,
    RequirementStructure,
)
from src.use_cases.compare_regulatory_versions import (
    CompareRegulatoryVersions,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        yield db


def create_section(
    session: Session,
    *,
    suffix: str,
) -> Section:
    source = Source(
        id=uuid.uuid4(),
        name=f"Test Source {suffix}",
        authority_tier="PRIMARY",
        institution_type="GOVERNMENT",
        base_url="https://example.com",
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
        url=f"https://example.com/{suffix}",
        description="Test document.",
    )
    session.add(document)
    session.flush()

    version = DocumentVersion(
        id=uuid.uuid4(),
        document_id=document.id,
        version_label=suffix,
        publication_date=None,
        effective_date=None,
        content_hash=uuid.uuid4().hex * 2,
        status="CURRENT",
    )
    session.add(version)
    session.flush()

    section = Section(
        id=uuid.uuid4(),
        document_version_id=version.id,
        section_number="1",
        title="Requirements",
        page_start=1,
        page_end=1,
        raw_text="Test requirement.",
    )
    session.add(section)
    session.flush()

    return section


def create_claim(
    session: Session,
    *,
    section_id: uuid.UUID,
    text: str,
    normalized_text: str | None = None,
) -> Claim:
    claim = Claim(
        id=uuid.uuid4(),
        section_id=section_id,
        claim_type="REQUIREMENT",
        text=text,
        normalized_text=normalized_text,
        effective_from=None,
        effective_to=None,
        status="ACTIVE",
    )
    session.add(claim)
    session.flush()

    return claim


def add_requirement_structure(
    session: Session,
    *,
    claim_id: uuid.UUID,
    deadline_days: str,
) -> ClaimStructureModel:
    structure = RequirementStructure(
        actor=EntityRef(
            entity_id=None,
            raw_text="Importers",
        ),
        modality="REQUIRED",
        action="submit",
        object=EntityRef(
            entity_id=None,
            raw_text="Form X",
        ),
        deadline=Duration(
            value=Decimal(deadline_days),
            unit="DAYS",
        ),
    )

    model = ClaimStructureModel(
        claim_id=claim_id,
        structure_type="RequirementStructure",
        structure={
            "actor": {
                "entity_id": None,
                "raw_text": structure.actor.raw_text,
            },
            "modality": structure.modality,
            "action": structure.action,
            "object": {
                "entity_id": None,
                "raw_text": structure.object.raw_text,
            },
            "deadline": {
                "value": str(structure.deadline.value),
                "unit": structure.deadline.unit,
            },
            "exception_ids": [],
            "applicability_conditions": [],
        },
    )

    session.add(model)
    session.flush()

    return model


def test_compare_modified_versions_persists_full_workflow(
    session: Session,
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

    add_requirement_structure(
        session,
        claim_id=old_claim.id,
        deadline_days="30",
    )
    add_requirement_structure(
        session,
        claim_id=new_claim.id,
        deadline_days="45",
    )

    session.commit()

    result = CompareRegulatoryVersions().execute(
        session,
        old_claim_id=old_claim.id,
        new_claim_id=new_claim.id,
    )

    assert result.old_claim_id == old_claim.id
    assert result.new_claim_id == new_claim.id

    assert result.correspondence is not None
    assert result.correspondence.relationship_type == "MODIFIED"
    assert (
        "VALUE_CHANGED: 30 DAYS -> 45 DAYS"
        in result.correspondence.changes
    )

    assert result.detection is not None
    assert result.detection.change_type == "MODIFIED"

    assert result.policy_change is not None
    assert result.policy_change.change_type == "MODIFIED"

    correspondence = session.scalar(
        select(ClaimCorrespondence).where(
            ClaimCorrespondence.claim_a_id == old_claim.id,
            ClaimCorrespondence.claim_b_id == new_claim.id,
        )
    )

    assert correspondence is not None
    assert correspondence.relationship_type == "MODIFIED"

    policy_change = session.get(
        PolicyChange,
        result.policy_change.policy_change_id,
    )

    assert policy_change is not None
    assert policy_change.change_type == "MODIFIED"

    claim_links = session.scalars(
        select(PolicyChangeClaim).where(
            PolicyChangeClaim.policy_change_id
            == policy_change.id
        )
    ).all()

    assert {
        (link.claim_id, link.role)
        for link in claim_links
    } == {
        (old_claim.id, "OLD"),
        (new_claim.id, "NEW"),
    }

    correspondence_link = session.scalar(
        select(PolicyChangeCorrespondence).where(
            PolicyChangeCorrespondence.policy_change_id
            == policy_change.id,
            PolicyChangeCorrespondence.correspondence_id
            == correspondence.id,
        )
    )

    assert correspondence_link is not None


def test_compare_same_versions_does_not_create_policy_change(
    session: Session,
):
    old_section = create_section(
        session,
        suffix="same-old",
    )
    new_section = create_section(
        session,
        suffix="same-new",
    )

    text = "Importers must submit Form X."

    old_claim = create_claim(
        session,
        section_id=old_section.id,
        text=text,
        normalized_text=text.lower(),
    )
    new_claim = create_claim(
        session,
        section_id=new_section.id,
        text=text,
        normalized_text=text.lower(),
    )

    add_requirement_structure(
        session,
        claim_id=old_claim.id,
        deadline_days="30",
    )
    add_requirement_structure(
        session,
        claim_id=new_claim.id,
        deadline_days="30",
    )

    session.commit()

    result = CompareRegulatoryVersions().execute(
        session,
        old_claim_id=old_claim.id,
        new_claim_id=new_claim.id,
    )

    assert result.correspondence is not None
    assert result.correspondence.relationship_type == "SAME"
    assert result.detection is None
    assert result.policy_change is None

    policy_changes = session.scalars(
        select(PolicyChange)
    ).all()

    assert policy_changes == []


def test_compare_added_claim(
    session: Session,
):
    section = create_section(
        session,
        suffix="added",
    )

    new_claim = create_claim(
        session,
        section_id=section.id,
        text="Importers must register electronically.",
    )

    session.commit()

    result = CompareRegulatoryVersions().execute(
        session,
        old_claim_id=None,
        new_claim_id=new_claim.id,
    )

    assert result.old_claim_id is None
    assert result.new_claim_id == new_claim.id
    assert result.correspondence is None

    assert result.detection is not None
    assert result.detection.change_type == "ADDED"

    assert result.policy_change is not None
    assert result.policy_change.change_type == "ADDED"

    claim_links = session.scalars(
        select(PolicyChangeClaim).where(
            PolicyChangeClaim.policy_change_id
            == result.policy_change.policy_change_id
        )
    ).all()

    assert len(claim_links) == 1
    assert claim_links[0].claim_id == new_claim.id
    assert claim_links[0].role == "NEW"


def test_compare_removed_claim(
    session: Session,
):
    section = create_section(
        session,
        suffix="removed",
    )

    old_claim = create_claim(
        session,
        section_id=section.id,
        text="Importers must submit Form X.",
    )

    session.commit()

    result = CompareRegulatoryVersions().execute(
        session,
        old_claim_id=old_claim.id,
        new_claim_id=None,
    )

    assert result.old_claim_id == old_claim.id
    assert result.new_claim_id is None
    assert result.correspondence is None

    assert result.detection is not None
    assert result.detection.change_type == "REMOVED"

    assert result.policy_change is not None
    assert result.policy_change.change_type == "REMOVED"

    claim_links = session.scalars(
        select(PolicyChangeClaim).where(
            PolicyChangeClaim.policy_change_id
            == result.policy_change.policy_change_id
        )
    ).all()

    assert len(claim_links) == 1
    assert claim_links[0].claim_id == old_claim.id
    assert claim_links[0].role == "OLD"


def test_compare_requires_at_least_one_claim(
    session: Session,
):
    with pytest.raises(
        ValueError,
        match="At least one claim must be provided.",
    ):
        CompareRegulatoryVersions().execute(
            session,
            old_claim_id=None,
            new_claim_id=None,
        )


def test_compare_rolls_back_correspondence_when_policy_persistence_fails(
    session: Session,
):
    old_section = create_section(
        session,
        suffix="rollback-old",
    )
    new_section = create_section(
        session,
        suffix="rollback-new",
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

    add_requirement_structure(
        session,
        claim_id=old_claim.id,
        deadline_days="30",
    )
    add_requirement_structure(
        session,
        claim_id=new_claim.id,
        deadline_days="45",
    )

    session.commit()

    class FailingPolicyChangeService:
        def create(self, *args, **kwargs):
            raise RuntimeError("policy persistence failed")

    use_case = CompareRegulatoryVersions(
        policy_change_service=FailingPolicyChangeService(),
    )

    with pytest.raises(
        RuntimeError,
        match="policy persistence failed",
    ):
        use_case.execute(
            session,
            old_claim_id=old_claim.id,
            new_claim_id=new_claim.id,
        )

    correspondence = session.scalar(
        select(ClaimCorrespondence).where(
            ClaimCorrespondence.claim_a_id == old_claim.id,
            ClaimCorrespondence.claim_b_id == new_claim.id,
        )
    )

    assert correspondence is None

    assert session.scalars(
        select(PolicyChange)
    ).all() == []
