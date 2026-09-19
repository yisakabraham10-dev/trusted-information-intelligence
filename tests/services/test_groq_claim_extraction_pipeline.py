from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.config import Settings
from src.db.base import Base
from src.models.claim import Claim
from src.models.claim_evidence import ClaimEvidence
from src.models.evidence import Evidence
from src.models.section import Section
from src.models.source import Source
from src.services.claim_creation import ClaimCreationService
from src.services.claim_evidence_validation import ClaimEvidenceValidator
from src.services.claim_extraction_pipeline import ClaimExtractionPipeline
from src.services.claim_extraction_validation import ClaimExtractionValidator
from src.services.document_ingestion import DocumentIngestionService
from src.services.document_persistence import DocumentPersistenceService
from src.services.groq_claim_extraction import GroqClaimExtractionProvider
from src.services.regulatory_structure import RegulatoryStructureParser


FIXTURE = Path(
    "tests/fixtures/customs_proclamation_1425_2026.pdf"
)


def test_real_groq_claim_extraction_pipeline_persists_claim():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        source = Source(
            name="Federal Negarit Gazette",
            authority_tier="PRIMARY",
            institution_type="OFFICIAL_PUBLICATION",
            base_url=None,
            description="Official Ethiopian legal publication.",
        )
        db.add(source)
        db.commit()

        ingestion = DocumentIngestionService()
        ingested_document = ingestion.extract(FIXTURE)

        parser = RegulatoryStructureParser()
        parsed_sections = parser.parse(
            ingested_document.pages
        )

        parsed_section = next(
            section
            for section in parsed_sections
            if section.section_number == "51(1)"
        )

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

        section = db.scalar(
            select(Section).where(
                Section.document_version_id
                == persisted.document_version.id,
                Section.section_number == "51(1)",
            )
        )

        assert section is not None

        evidence = db.scalar(
            select(Evidence).where(
                Evidence.section_id == section.id
            )
        )

        assert evidence is not None

        settings = Settings()

        provider = GroqClaimExtractionProvider(
            settings
        )

        pipeline = ClaimExtractionPipeline(
            extraction_provider=provider,
            extraction_validator=ClaimExtractionValidator(),
            evidence_validator=ClaimEvidenceValidator(),
            claim_creation_service=ClaimCreationService(),
        )

        result = pipeline.process(
            db,
            section_id=section.id,
            parsed_section=parsed_section,
        )

        claim = result.claim

        assert claim.id is not None
        assert claim.section_id == section.id
        assert claim.claim_type == "REQUIREMENT"
        assert claim.text
        assert "forty-five days" in claim.text.lower()

        assert len(result.evidence) == 1
        assert result.evidence[0].id == evidence.id

        claim_evidence = db.scalar(
            select(ClaimEvidence).where(
                ClaimEvidence.claim_id == claim.id,
                ClaimEvidence.evidence_id == evidence.id,
            )
        )

        assert claim_evidence is not None
        assert claim_evidence.relation_type == "SUPPORTS"

        print("\n--- GROQ PIPELINE RESULT ---")
        print(f"Claim ID: {claim.id}")
        print(f"Claim type: {claim.claim_type}")
        print(f"Section: {parsed_section.section_number}")
        print(f"Claim: {claim.text}")
        print(f"Evidence ID: {evidence.id}")
        print("----------------------------")
