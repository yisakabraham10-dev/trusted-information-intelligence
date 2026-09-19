from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.db.base import Base
from src.models.claim import Claim
from src.models.document import Document
from src.models.document_version import DocumentVersion
from src.models.evidence import Evidence
from src.models.claim_structure import ClaimStructure as ClaimStructureModel
from src.models.section import Section
from src.models.source import Source
from src.services.claim_creation import ClaimCreationService
from src.services.claim_evidence_validation import ClaimEvidenceValidator
from src.services.claim_extraction import ClaimExtractionCandidate
from src.services.claim_extraction_pipeline import ClaimExtractionPipeline
from src.services.claim_extraction_validation import ClaimExtractionValidator
from src.services.claim_structure import (
    Duration,
    EntityRef,
    RequirementStructure,
)


class FakeClaimExtractionProvider:
    def __init__(self, candidates):
        self.candidates = candidates

    def extract(self, section):
        return self.candidates


class FailingClaimCreationService(ClaimCreationService):
    def __init__(self):
        self.call_count = 0

    def create_claim(self, db, **kwargs):
        self.call_count += 1

        if self.call_count == 2:
            raise RuntimeError("Simulated claim creation failure.")

        return super().create_claim(db, **kwargs)


def make_pipeline(candidates, claim_creation_service=None):
    return ClaimExtractionPipeline(
        extraction_provider=FakeClaimExtractionProvider(candidates),
        extraction_validator=ClaimExtractionValidator(),
        evidence_validator=ClaimEvidenceValidator(),
        claim_creation_service=(
            claim_creation_service
            if claim_creation_service is not None
            else ClaimCreationService()
        ),
    )


def make_section(db):
    source = Source(
        name="Test Source",
        authority_tier="PRIMARY",
        institution_type="GOVERNMENT",
    )
    db.add(source)
    db.flush()

    document = Document(
        source_id=source.id,
        title="Test Regulatory Document",
        document_type="REGULATION",
    )
    db.add(document)
    db.flush()

    document_version = DocumentVersion(
        document_id=document.id,
        version_label="TEST-2026",
        publication_date=datetime(2026, 1, 1),
        effective_date=datetime(2026, 1, 1),
        content_hash="pipeline-test",
        status="ACTIVE",
    )
    db.add(document_version)
    db.flush()

    section = Section(
        document_version_id=document_version.id,
        section_number="51(1)",
        title=None,
        page_start=1,
        page_end=1,
        raw_text=(
            "Goods imported by sea or land shall be "
            "removed within forty-five days. "
            "The importer shall complete the necessary "
            "customs formalities."
        ),
    )
    db.add(section)
    db.flush()

    evidence = Evidence(
        section_id=section.id,
        page=1,
        quote=section.raw_text,
    )
    db.add(evidence)
    db.commit()

    parsed_section = type(
        "ParsedSectionStub",
        (),
        {
            "section_number": "51(1)",
            "title": None,
            "section_type": "REQUIREMENT",
            "raw_text": section.raw_text,
        },
    )()

    return section, evidence, parsed_section


def make_valid_candidate():
    return ClaimExtractionCandidate(
        claim_type="REQUIREMENT",
        text=(
            "Goods imported by sea or land shall be "
            "removed within forty-five days."
        ),
        section_number="51(1)",
        structure=RequirementStructure(
            actor=None,
            modality="REQUIRED",
            action="removed",
            object=EntityRef(
                entity_id=None,
                raw_text="Goods imported by sea or land",
            ),
            deadline=Duration(
                value=Decimal("45"),
                unit="DAYS",
            ),
        ),
    )


def make_second_valid_candidate():
    return ClaimExtractionCandidate(
        claim_type="REQUIREMENT",
        text=(
            "The importer shall complete the necessary "
            "customs formalities."
        ),
        section_number="51(1)",
        structure=RequirementStructure(
            actor=EntityRef(
                entity_id=None,
                raw_text="The importer",
            ),
            modality="REQUIRED",
            action="complete",
            object=EntityRef(
                entity_id=None,
                raw_text="the necessary customs formalities",
            ),
            deadline=None,
        ),
    )


def test_pipeline_creates_claim_from_validated_extraction():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        section, evidence, parsed_section = make_section(db)

        pipeline = make_pipeline((make_valid_candidate(),))

        results = pipeline.process(
            db,
            section_id=section.id,
            parsed_section=parsed_section,
        )

        assert len(results) == 1

        result = results[0]

        assert result.claim.id is not None
        assert result.claim.claim_type == "REQUIREMENT"
        assert result.claim.text == make_valid_candidate().text
        assert len(result.evidence) == 1
        assert result.evidence[0].id == evidence.id

        stored_structure = (
            db.query(ClaimStructureModel)
            .filter(ClaimStructureModel.claim_id == result.claim.id)
            .one()
        )

        assert stored_structure.structure_type == "RequirementStructure"
        assert stored_structure.structure["modality"] == "REQUIRED"
        assert stored_structure.structure["action"] == "removed"
        assert stored_structure.structure["deadline"]["value"] == "45"
        assert stored_structure.structure["deadline"]["unit"] == "DAYS"


def test_pipeline_creates_multiple_claims_in_one_transaction():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        section, evidence, parsed_section = make_section(db)

        first_candidate = make_valid_candidate()
        second_candidate = make_second_valid_candidate()

        pipeline = make_pipeline(
            (
                first_candidate,
                second_candidate,
            )
        )

        results = pipeline.process(
            db,
            section_id=section.id,
            parsed_section=parsed_section,
        )

        assert len(results) == 2

        first_result = results[0]
        second_result = results[1]

        assert first_result.claim.id is not None
        assert second_result.claim.id is not None

        assert first_result.claim.text == first_candidate.text
        assert second_result.claim.text == second_candidate.text

        assert first_result.claim.id != second_result.claim.id

        assert len(first_result.evidence) == 1
        assert len(second_result.evidence) == 1

        assert first_result.evidence[0].id == evidence.id
        assert second_result.evidence[0].id == evidence.id


def test_pipeline_rejects_valid_and_invalid_candidates_without_persisting():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        section, _, parsed_section = make_section(db)

        valid_candidate = make_valid_candidate()

        invalid_candidate = ClaimExtractionCandidate(
            claim_type="",
            text="",
            section_number="",
            structure=make_valid_candidate().structure,
        )

        pipeline = make_pipeline(
            (
                valid_candidate,
                invalid_candidate,
            )
        )

        with pytest.raises(
            ValueError,
            match="Claim extraction validation failed",
        ):
            pipeline.process(
                db,
                section_id=section.id,
                parsed_section=parsed_section,
            )

        persisted_claims = db.query(Claim).all()

        assert persisted_claims == []


def test_pipeline_rolls_back_when_claim_creation_fails_mid_transaction():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        section, _, parsed_section = make_section(db)

        first_candidate = make_valid_candidate()
        second_candidate = make_second_valid_candidate()

        failing_creation_service = FailingClaimCreationService()

        pipeline = make_pipeline(
            (
                first_candidate,
                second_candidate,
            ),
            claim_creation_service=failing_creation_service,
        )

        with pytest.raises(
            RuntimeError,
            match="Simulated claim creation failure",
        ):
            pipeline.process(
                db,
                section_id=section.id,
                parsed_section=parsed_section,
            )

        persisted_claims = db.query(Claim).all()

        assert persisted_claims == []


def test_pipeline_rejects_empty_extraction():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        section, _, parsed_section = make_section(db)

        pipeline = make_pipeline(())

        with pytest.raises(ValueError, match="no candidates"):
            pipeline.process(
                db,
                section_id=section.id,
                parsed_section=parsed_section,
            )


def test_pipeline_rejects_invalid_extraction_before_evidence_validation():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        section, _, parsed_section = make_section(db)

        invalid_candidate = ClaimExtractionCandidate(
            claim_type="",
            text="",
            section_number="",
            structure=make_valid_candidate().structure,
        )

        pipeline = make_pipeline((invalid_candidate,))

        with pytest.raises(
            ValueError,
            match="Claim extraction validation failed",
        ):
            pipeline.process(
                db,
                section_id=section.id,
                parsed_section=parsed_section,
            )
