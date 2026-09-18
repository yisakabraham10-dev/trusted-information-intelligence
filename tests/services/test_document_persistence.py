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
from src.services.document_persistence import DocumentPersistenceService
from src.services.document_structure import ParsedSection


def test_document_persistence(tmp_path: Path):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"fake pdf content")

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

        parsed_sections = (
            ParsedSection(
                section_number="51(1)",
                title=None,
                section_type="SUB_ARTICLE",
                page_start=3,
                page_end=3,
                raw_text="Imported goods must be removed within 45 days.",
            ),
            ParsedSection(
                section_number="51(2)",
                title=None,
                section_type="SUB_ARTICLE",
                page_start=4,
                page_end=4,
                raw_text="Goods imported by air must be removed within 30 days.",
            ),
        )

        service = DocumentPersistenceService()

        result = service.persist(
            db,
            source_id=source.id,
            pdf_path=pdf_path,
            title="Customs Proclamation (Further Amendment) Proclamation",
            document_type="PROCLAMATION",
            parsed_sections=parsed_sections,
            version_label="1425/2026",
            publication_date=datetime(2026, 7, 23),
            effective_date=datetime(2026, 7, 23),
        )

        assert result.created is True

        assert result.document.id is not None
        assert result.document_version.id is not None

        assert len(result.sections) == 2
        assert len(result.evidence) == 2

        assert result.sections[0].section_number == "51(1)"
        assert result.sections[0].page_start == 3

        assert result.evidence[0].quote == (
            "Imported goods must be removed within 45 days."
        )

        stored_document = db.scalar(select(Document))
        stored_version = db.scalar(select(DocumentVersion))
        stored_sections = db.scalars(select(Section)).all()
        stored_evidence = db.scalars(select(Evidence)).all()

        assert stored_document is not None
        assert stored_version is not None

        assert len(stored_sections) == 2
        assert len(stored_evidence) == 2