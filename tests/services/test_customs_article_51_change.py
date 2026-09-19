from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.db.base import Base
from src.models.claim import Claim
from src.models.claim_correspondence import ClaimCorrespondence
from src.models.claim_evidence import ClaimEvidence
from src.models.document_version import DocumentVersion
from src.models.evidence import Evidence
from src.models.policy_change import PolicyChange
from src.models.section import Section
from src.models.source import Source
from src.services.change_detector import ChangeDetector
from src.services.claim_correspondence import CorrespondenceEvaluator
from src.services.claim_creation import ClaimCreationService
from src.services.claim_evidence_validation import ClaimEvidenceValidator
from src.services.claim_extraction import ClaimExtractionCandidate
from src.services.claim_extraction_validation import ClaimExtractionValidator
from src.services.claim_structure import (
    Duration,
    EntityRef,
    RequirementStructure,
)
from src.services.document_ingestion import DocumentIngestionService
from src.services.document_persistence import DocumentPersistenceService
from src.services.policy_change_service import PolicyChangeService
from src.services.regulatory_structure import RegulatoryStructureParser


FIXTURE = Path(
    "tests/fixtures/customs_proclamation_1425_2026.pdf"
)


def test_customs_article_51_60_to_45_day_change():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        # =========================================================
        # 1. Create the official source
        # =========================================================
        source = Source(
            name="Federal Negarit Gazette",
            authority_tier="PRIMARY",
            institution_type="OFFICIAL_PUBLICATION",
            base_url=None,
            description="Official Ethiopian legal publication.",
        )

        db.add(source)
        db.commit()

        # =========================================================
        # 2. Extract the real 2026 Customs Proclamation
        # =========================================================
        ingestion = DocumentIngestionService()
        ingested_document = ingestion.extract(FIXTURE)

        assert len(ingested_document.pages) == 18

        full_text = "\n".join(
            page.text
            for page in ingested_document.pages
        )

        assert "1425/2026" in full_text

        # =========================================================
        # 3. Parse the regulatory structure
        # =========================================================
        parser = RegulatoryStructureParser()

        parsed_sections = parser.parse(
            ingested_document.pages
        )

        section_numbers = [
            section.section_number
            for section in parsed_sections
        ]

        assert "51(1)" in section_numbers
        assert "51(2)" in section_numbers
        assert "51(7)" in section_numbers
        assert "51(8)" in section_numbers

        # =========================================================
        # 4. Persist the real 2026 document
        # =========================================================
        persistence = DocumentPersistenceService()

        persisted = persistence.persist(
            db,
            source_id=source.id,
            pdf_path=FIXTURE,
            title=(
                "Customs Proclamation "
                "(Further Amendment) Proclamation"
            ),
            document_type="PROCLAMATION",
            parsed_sections=parsed_sections,
            version_label="1425/2026",
            publication_date=datetime(2026, 7, 23),
            effective_date=datetime(2026, 7, 23),
        )

        assert persisted.created is True
        assert persisted.document_version is not None

        # =========================================================
        # 5. Find real Article 51(1)
        # =========================================================
        new_section = db.scalar(
            select(Section).where(
                Section.document_version_id
                == persisted.document_version.id,
                Section.section_number == "51(1)",
            )
        )

        assert new_section is not None

        # =========================================================
        # 6. Find the evidence supporting Article 51(1)
        # =========================================================
        new_evidence = db.scalar(
            select(Evidence).where(
                Evidence.section_id == new_section.id
            )
        )

        assert new_evidence is not None
        assert "forty-five days" in new_evidence.quote.lower()

        # =========================================================
        # 7. Create a deterministic representation of the NEW
        #    claim extracted from Article 51(1)
        #
        #    The live Gemini provider is tested separately.
        #    This integration test verifies the deterministic
        #    pipeline after extraction.
        # =========================================================
        parsed_new_section = next(
            section
            for section in parsed_sections
            if section.section_number == "51(1)"
        )

        candidate = ClaimExtractionCandidate(
            claim_type="REQUIREMENT",
            text=(
                "Any goods imported by sea or land must be removed "
                "from the temporary customs storage within forty-five "
                "days from the date of entry into the storage after "
                "the necessary customs formalities have been completed."
            ),
            section_number="51(1)",
            structure=RequirementStructure(
                actor=EntityRef(
                    entity_id=None,
                    raw_text="Any goods imported by sea or land",
                ),
                modality="REQUIRED",
                action="be removed from the temporary customs storage",
                object=None,
                deadline=Duration(
                    value=Decimal("45"),
                    unit="DAYS",
                ),
            ),
        )

        extraction_validation = ClaimExtractionValidator().validate(
            candidate
        )

        assert extraction_validation.valid, (
            extraction_validation.errors
        )

        evidence_validation = ClaimEvidenceValidator().validate(
            candidate,
            parsed_new_section,
        )

        assert evidence_validation.supported, (
            evidence_validation.errors
        )

        # =========================================================
        # 8. Persist the NEW 2026 claim
        # =========================================================
        claim_service = ClaimCreationService()

        new_result = claim_service.create_claim(
            db,
            section_id=new_section.id,
            claim_type=candidate.claim_type,
            text=candidate.text,
            normalized_text=candidate.text.lower(),
            evidence_ids=(new_evidence.id,),
            effective_from=datetime(2026, 7, 23),
        )

        new_claim = new_result.claim

        assert new_claim.id is not None
        assert new_claim.claim_type == "REQUIREMENT"
        assert new_claim.effective_from == datetime(
            2026, 7, 23
        )

        # =========================================================
        # 9. Create the OLD 2014 document version
        #
        # This is a source-backed test representation of the
        # previous Article 51(1) 60-day rule.
        # =========================================================
        old_version = DocumentVersion(
            document_id=persisted.document.id,
            version_label="859/2014",
            publication_date=datetime(2014, 7, 8),
            effective_date=datetime(2014, 7, 8),
            content_hash="old-customs-859-2014-test",
            status="SUPERSEDED",
        )

        db.add(old_version)
        db.flush()

        # =========================================================
        # 10. Create the OLD Article 51(1) section
        # =========================================================
        old_section = Section(
            document_version_id=old_version.id,
            section_number="51(1)",
            title=None,
            page_start=1,
            page_end=1,
            raw_text=(
                "Goods imported by sea or land shall be "
                "removed from temporary customs storage "
                "within 60 days."
            ),
        )

        db.add(old_section)
        db.flush()

        # =========================================================
        # 11. Create evidence for the OLD claim
        # =========================================================
        old_evidence = Evidence(
            section_id=old_section.id,
            page=1,
            quote=old_section.raw_text,
        )

        db.add(old_evidence)
        db.commit()

        # =========================================================
        # 12. Create the OLD 2014 claim
        # =========================================================
        old_result = claim_service.create_claim(
            db,
            section_id=old_section.id,
            claim_type="REQUIREMENT",
            text=(
                "Imported goods transported by sea or land "
                "must be removed from temporary customs "
                "storage within 60 days."
            ),
            normalized_text=(
                "imported goods sea land remove temporary "
                "customs storage within 60 days"
            ),
            evidence_ids=(old_evidence.id,),
            effective_from=datetime(2014, 7, 8),
        )

        old_claim = old_result.claim

        assert old_claim.id is not None
        assert old_claim.claim_type == "REQUIREMENT"
        assert old_claim.effective_from == datetime(
            2014, 7, 8
        )

        # =========================================================
        # 13. Build semantic structures for both claims
        # =========================================================
        old_structure = RequirementStructure(
            actor=EntityRef(
                entity_id=None,
                raw_text="importer",
            ),
            modality="REQUIRED",
            action="remove",
            object=EntityRef(
                entity_id=None,
                raw_text="imported goods",
            ),
            deadline=Duration(
                value=Decimal("60"),
                unit="days",
            ),
        )

        new_structure = RequirementStructure(
            actor=EntityRef(
                entity_id=None,
                raw_text="importer",
            ),
            modality="REQUIRED",
            action="remove",
            object=EntityRef(
                entity_id=None,
                raw_text="imported goods",
            ),
            deadline=Duration(
                value=Decimal("45"),
                unit="days",
            ),
        )

        # =========================================================
        # 14. Determine claim correspondence
        # =========================================================
        correspondence_evaluator = CorrespondenceEvaluator()

        correspondence_result = correspondence_evaluator.evaluate(
            old_claim,
            new_claim,
            old_structure=old_structure,
            new_structure=new_structure,
        )

        assert correspondence_result.relationship_type == "MODIFIED"
        assert correspondence_result.confidence == 1.0
        assert (
            correspondence_result.method
            == "REQUIREMENT_STRUCTURE"
        )

        assert (
            "VALUE_CHANGED: 60 days -> 45 days"
            in correspondence_result.changes
        )

        # =========================================================
        # 15. Persist the claim correspondence
        # =========================================================
        correspondence = ClaimCorrespondence(
            claim_a_id=old_claim.id,
            claim_b_id=new_claim.id,
            relationship_type=(
                correspondence_result.relationship_type
            ),
            confidence=correspondence_result.confidence,
            method=correspondence_result.method,
        )

        db.add(correspondence)
        db.commit()

        assert correspondence.id is not None

        # =========================================================
        # 16. Detect the semantic policy change
        # =========================================================
        detector = ChangeDetector()

        change_result = detector.detect(
            correspondence_result,
        )

        assert change_result is not None
        assert change_result.change_type == "MODIFIED"
        assert "60 days" in change_result.summary
        assert "45 days" in change_result.summary

        # =========================================================
        # 17. Persist PolicyChange
        # =========================================================
        policy_service = PolicyChangeService()

        policy_result = policy_service.create(
            db,
            detection=change_result,
            claim_correspondence=correspondence,
            old_claim=old_claim,
            new_claim=new_claim,
            effective_date=datetime(2026, 7, 23),
        )

        assert policy_result.policy_change_id is not None
        assert policy_result.change_type == "MODIFIED"

        # =========================================================
        # 18. Load the persisted PolicyChange
        # =========================================================
        policy_change = db.scalar(
            select(PolicyChange).where(
                PolicyChange.id
                == policy_result.policy_change_id
            )
        )

        assert policy_change is not None
        assert policy_change.change_type == "MODIFIED"
        assert policy_change.summary == change_result.summary
        assert policy_change.effective_date == datetime(
            2026, 7, 23
        )

        # =========================================================
        # 19. Verify claim -> evidence provenance
        # =========================================================
        persisted_claim_evidence = db.scalar(
            select(ClaimEvidence).where(
                ClaimEvidence.claim_id == new_claim.id,
                ClaimEvidence.evidence_id == new_evidence.id,
            )
        )

        assert persisted_claim_evidence is not None
        assert (
            persisted_claim_evidence.relation_type
            == "SUPPORTS"
        )

        # =========================================================
        # 20. Verify evidence -> section -> document provenance
        # =========================================================
        assert new_evidence.section_id == new_section.id

        assert (
            new_section.document_version_id
            == persisted.document_version.id
        )

        persisted_document_version = db.scalar(
            select(DocumentVersion).where(
                DocumentVersion.id
                == persisted.document_version.id
            )
        )

        assert persisted_document_version is not None
        assert (
            persisted_document_version.version_label
            == "1425/2026"
        )

        # =========================================================
        # 21. Verify the detected semantic change
        # =========================================================
        assert old_structure.deadline is not None
        assert new_structure.deadline is not None

        assert (
            old_structure.deadline.value
            == Decimal("60")
        )

        assert (
            new_structure.deadline.value
            == Decimal("45")
        )

        assert (
            old_structure.deadline.unit.lower()
            == "days"
        )

        assert (
            new_structure.deadline.unit.lower()
            == "days"
        )

        # =========================================================
        # 22. Verify the final policy-change summary
        # =========================================================
        assert "VALUE_CHANGED: 60 days -> 45 days" in (
            change_result.summary
        )
