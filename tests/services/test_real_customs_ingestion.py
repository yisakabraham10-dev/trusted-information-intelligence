from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.db.base import Base
from src.models.document import Document
from src.models.document_version import DocumentVersion
from src.models.evidence import Evidence
from src.models.section import Section
from src.models.source import Source
from src.services.document_ingestion import DocumentIngestionService
from src.services.document_persistence import DocumentPersistenceService
from src.services.document_structure import ParsedSection
from src.services.regulatory_structure import RegulatoryStructureParser


FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "customs_proclamation_1425_2026.pdf"
)


def test_real_customs_proclamation_can_be_ingested_and_persisted():
    assert FIXTURE_PATH.exists(), (
        f"Customs proclamation fixture not found: {FIXTURE_PATH}"
    )

    # ---------------------------------------------------------
    # 1. Extract the real PDF
    # ---------------------------------------------------------
    ingestion_service = DocumentIngestionService()

    document = ingestion_service.extract(FIXTURE_PATH)

    assert len(document.pages) == 18

    assert any(
        "1425/2026" in page.text
        for page in document.pages
    )

    # ---------------------------------------------------------
    # 2. Parse the regulatory structure
    # ---------------------------------------------------------
    parser = RegulatoryStructureParser()

    parsed_sections = parser.parse(document.pages)

    assert parsed_sections

    section_numbers = {
        section.section_number
        for section in parsed_sections
    }

    # These are the important amended Article 51 sections.
    assert "51(1)" in section_numbers
    assert "51(2)" in section_numbers
    assert "51(7)" in section_numbers
    assert "51(8)" in section_numbers

    # ---------------------------------------------------------
    # 3. Create an isolated database
    # ---------------------------------------------------------
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        source = Source(
            name="Federal Negarit Gazette",
            authority_tier="PRIMARY",
            institution_type="OFFICIAL_PUBLICATION",
            is_active=True,
        )

        db.add(source)
        db.commit()
        db.refresh(source)

        # -----------------------------------------------------
        # 4. Persist the real document
        # -----------------------------------------------------
        persistence_service = DocumentPersistenceService()

        result = persistence_service.persist(
            db,
            source_id=source.id,
            pdf_path=FIXTURE_PATH,
            title="Customs Proclamation (Further Amendment) Proclamation",
            document_type="PROCLAMATION",
            parsed_sections=parsed_sections,
            version_label="1425/2026",
            publication_date=datetime(2026, 7, 23),
            effective_date=datetime(2026, 7, 23),
        )

        # -----------------------------------------------------
        # 5. Verify persistence
        # -----------------------------------------------------
        assert result.created is True

        assert result.document.id is not None
        assert result.document_version.id is not None

        assert len(result.sections) == len(parsed_sections)
        assert len(result.evidence) == len(parsed_sections)

        # -----------------------------------------------------
        # 6. Verify the important Article 51 sections
        # -----------------------------------------------------
        stored_sections = db.scalars(
            select(Section).where(
                Section.document_version_id
                == result.document_version.id
            )
        ).all()

        stored_by_number = {
            section.section_number: section
            for section in stored_sections
        }

        for number in ("51(1)", "51(2)", "51(7)", "51(8)"):
            assert number in stored_by_number

            section = stored_by_number[number]

            assert section.raw_text
            assert section.page_start is not None

        # -----------------------------------------------------
        # 7. Verify evidence is connected to those sections
        # -----------------------------------------------------
        stored_evidence = db.scalars(
            select(Evidence)
            .where(
                Evidence.section_id.in_(
                    [
                        stored_by_number[number].id
                        for number in (
                            "51(1)",
                            "51(2)",
                            "51(7)",
                            "51(8)",
                        )
                    ]
                )
            )
        ).all()

        assert len(stored_evidence) == 4

        for evidence in stored_evidence:
            assert evidence.quote
            assert evidence.page is not None

        # -----------------------------------------------------
        # 8. Verify the document/version metadata
        # -----------------------------------------------------
        stored_document = db.scalar(select(Document))

        stored_version = db.scalar(
            select(DocumentVersion).where(
                DocumentVersion.id == result.document_version.id
            )
        )

        assert stored_document is not None
        assert stored_document.title == (
            "Customs Proclamation (Further Amendment) Proclamation"
        )

        assert stored_version is not None
        assert stored_version.version_label == "1425/2026"
        assert stored_version.publication_date == datetime(2026, 7, 23)
        assert stored_version.effective_date == datetime(2026, 7, 23)

        # The PDF must have an immutable content hash.
        assert stored_version.content_hash
        assert len(stored_version.content_hash) == 64

        # -----------------------------------------------------
        # 9. Verify the actual Article 51(1) evidence
        # -----------------------------------------------------
        article_51_1 = stored_by_number["51(1)"]

        article_51_1_evidence = db.scalar(
            select(Evidence).where(
                Evidence.section_id == article_51_1.id
            )
        )

        assert article_51_1_evidence is not None
        assert article_51_1_evidence.quote
        assert article_51_1_evidence.page == article_51_1.page_start