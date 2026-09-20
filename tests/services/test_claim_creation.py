import pytest
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.db.base import Base
from src.domain.exceptions import ValidationError
from src.models.claim import Claim
from src.models.claim_evidence import ClaimEvidence
from src.models.evidence import Evidence
from src.models.section import Section
from src.services.claim_creation import ClaimCreationService
from src.services.claim_structure import EntityRef, RequirementStructure


def _requirement_structure() -> RequirementStructure:
    return RequirementStructure(
        actor=None,
        modality="REQUIRED",
        action="remove",
        object=EntityRef(
            entity_id=None,
            raw_text="Imported goods",
        ),
        deadline=None,
    )


def test_claim_creation_requires_evidence():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        section = Section(
            document_version_id=uuid4(),
            section_number="51(1)",
            title=None,
            page_start=3,
            page_end=3,
            raw_text="Imported goods must be removed within 45 days.",
        )

        db.add(section)
        db.commit()

        service = ClaimCreationService()

        with pytest.raises(
            ValidationError,
            match="evidence",
        ):
            service.create_claim(
                db,
                section_id=section.id,
                claim_type="REQUIREMENT",
                text="Imported goods must be removed within 45 days.",
                evidence_ids=(),
                structure=_requirement_structure(),
            )


def test_claim_creation_persists_claim_and_evidence_link():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        section = Section(
            document_version_id=uuid4(),
            section_number="51(1)",
            title=None,
            page_start=3,
            page_end=3,
            raw_text="Imported goods must be removed within 45 days.",
        )

        db.add(section)
        db.flush()

        evidence = Evidence(
            section_id=section.id,
            page=3,
            quote="Imported goods must be removed within 45 days.",
        )

        db.add(evidence)
        db.commit()

        service = ClaimCreationService()

        result = service.create_claim(
            db,
            section_id=section.id,
            claim_type="REQUIREMENT",
            text="Imported goods must be removed within 45 days.",
            normalized_text="imported goods remove within 45 days",
            evidence_ids=(evidence.id,),
            structure=_requirement_structure(),
        )

        assert result.claim.id is not None
        assert result.claim.claim_type == "REQUIREMENT"
        assert result.claim.text == (
            "Imported goods must be removed within 45 days."
        )

        stored_claim = db.scalar(select(Claim))

        assert stored_claim is not None
        assert stored_claim.id == result.claim.id

        links = db.scalars(select(ClaimEvidence)).all()

        assert len(links) == 1
        assert links[0].claim_id == result.claim.id
        assert links[0].evidence_id == evidence.id
        assert links[0].relation_type == "SUPPORTS"
