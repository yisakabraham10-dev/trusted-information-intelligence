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
from src.services.claim_structure import (
    Duration,
    EntityRef,
    RequirementStructure,
)
from src.services.document_ingestion import DocumentIngestionService
from src.services.document_persistence import DocumentPersistenceService
from src.services.regulatory_structure import RegulatoryStructureParser
from src.services.policy_change_service import PolicyChangeService


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
        # 7. Create the NEW 2026 claim
        # =========================================================
        claim_service = ClaimCreationService()

        new_result = claim_service.create_claim(
            db,
            section_id=new_section.id,
            claim_type="REQUIREMENT",
            text=(
                "Imported goods transported by sea or land "
                "must be removed from temporary customs "
                "storage within 45 days from the date of entry."
            ),
            normalized_text=(
                "imported goods sea land remove temporary "
                "customs storage within 45 days"
            ),
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
        # 8. Create the OLD 2014 document version
        #
        # This is currently a source-backed test representation
        # of Article 51(1)'s previous 60-day rule.
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
        # 9. Create the OLD Article 51(1) section
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
        # 10. Create evidence for the OLD claim
        # =========================================================
        old_evidence = Evidence(
            section_id=old_section.id,
            page=1,
            quote=old_section.raw_text,
        )

        db.add(old_evidence)
        db.commit()

        # =========================================================
        # 11. Create the OLD 2014 claim
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
        # 12. Build semantic structures for both claims
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
        # 13. Compare OLD vs NEW
        # =========================================================
        evaluator = CorrespondenceEvaluator()

        correspondence_result = evaluator.evaluate(
            old_claim,
            new_claim,
            old_structure=old_structure,
            new_structure=new_structure,
        )

        assert (
            correspondence_result.relationship_type
            == "MODIFIED"
        )

        assert (
            correspondence_result.method
            == "REQUIREMENT_STRUCTURE"
        )

        assert correspondence_result.confidence == 1.0

        # =========================================================
        # 14. Persist ClaimCorrespondence
        # =========================================================
        correspondence = ClaimCorrespondence(
            claim_a_id=old_claim.id,
            claim_b_id=new_claim.id,
            relationship_type=(
                correspondence_result.relationship_type
            ),
            confidence=correspondence_result.confidence,
            method=correspondence_result.method,
            status="CONFIRMED",
        )

        db.add(correspondence)
        db.commit()

        assert correspondence.id is not None

        # =========================================================
        # 15. Detect the policy change
        # =========================================================
        detector = ChangeDetector()

        detection = detector.detect(
            correspondence_result,
            old_claim_exists=True,
            new_claim_exists=True,
        )

        assert detection is not None
        assert detection.change_type == "MODIFIED"

        # =========================================================
        # 16. Persist PolicyChange
        # =========================================================
        policy_service = PolicyChangeService()

        persistence_result = policy_service.create(
            db,
            detection=detection,
            old_claim=old_claim,
            new_claim=new_claim,
            claim_correspondence=correspondence,
            effective_date=datetime(2026, 7, 23),
        )

        assert persistence_result.policy_change_id is not None
        assert persistence_result.change_type == "MODIFIED"

        # =========================================================
        # 17. Verify the PolicyChange
        # =========================================================
        stored_change = db.scalar(
            select(PolicyChange).where(
                PolicyChange.id
                == persistence_result.policy_change_id
            )
        )

        assert stored_change is not None
        assert stored_change.change_type == "MODIFIED"
        assert stored_change.effective_date == datetime(
            2026, 7, 23
        )

        # =========================================================
        # 18. Verify provenance:
        #
        # PolicyChange
        #      ↓
        # ClaimCorrespondence
        #      ↓
        # New Claim
        #      ↓
        # ClaimEvidence
        #      ↓
        # Evidence
        #      ↓
        # Article 51(1)
        #      ↓
        # 2026 Customs Proclamation
        # =========================================================
        new_claim_evidence = db.scalar(
            select(ClaimEvidence).where(
                ClaimEvidence.claim_id == new_claim.id,
                ClaimEvidence.evidence_id == new_evidence.id,
            )
        )

        assert new_claim_evidence is not None
        assert new_claim_evidence.relation_type == "SUPPORTS"
        assert new_claim_evidence.strength == 1.0

        # =========================================================
        # 19. Verify the final change summary
        # =========================================================
        assert "60 days" in stored_change.summary
        assert "45 days" in stored_change.summary

