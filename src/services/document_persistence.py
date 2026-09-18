from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.document import Document
from src.models.document_version import DocumentVersion
from src.models.evidence import Evidence
from src.models.section import Section
from src.services.document_structure import ParsedSection


@dataclass(frozen=True)
class DocumentPersistenceResult:
    document: Document
    document_version: DocumentVersion
    sections: tuple[Section, ...]
    evidence: tuple[Evidence, ...]
    created: bool


class DocumentPersistenceService:
    """
    Persist an extracted regulatory document while preserving provenance.

    Responsibilities:
    - create or reuse a Document
    - create a DocumentVersion
    - persist parsed Sections
    - create source Evidence for each section
    - calculate the immutable content hash
    - keep the operation transactional

    This service does not:
    - extract PDF text
    - interpret legal meaning
    - create Claims
    - determine PolicyChanges
    - call an LLM
    """

    def persist(
        self,
        db: Session,
        *,
        source_id: UUID,
        pdf_path: str | Path,
        title: str,
        document_type: str,
        parsed_sections: tuple[ParsedSection, ...],
        version_label: str | None = None,
        publication_date: datetime | None = None,
        effective_date: datetime | None = None,
        url: str | None = None,
        description: str | None = None,
        notes: str | None = None,
    ) -> DocumentPersistenceResult:
        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a PDF file, got: {path.suffix}")

        content_hash = self._calculate_hash(path)

        try:
            document = self._get_or_create_document(
                db=db,
                source_id=source_id,
                title=title,
                document_type=document_type,
                url=url,
                description=description,
            )

            existing_version = db.scalar(
                select(DocumentVersion).where(
                    DocumentVersion.document_id == document.id,
                    DocumentVersion.content_hash == content_hash,
                )
            )

            if existing_version is not None:
                sections = tuple(
                    db.scalars(
                        select(Section)
                        .where(Section.document_version_id == existing_version.id)
                        .order_by(Section.page_start, Section.section_number)
                    ).all()
                )

                evidence = tuple(
                    db.scalars(
                        select(Evidence)
                        .where(Evidence.section_id.in_(
                            [section.id for section in sections]
                        ))
                        .order_by(Evidence.page)
                    ).all()
                ) if sections else ()

                return DocumentPersistenceResult(
                    document=document,
                    document_version=existing_version,
                    sections=sections,
                    evidence=evidence,
                    created=False,
                )

            document_version = DocumentVersion(
                document_id=document.id,
                version_label=version_label,
                publication_date=publication_date,
                effective_date=effective_date,
                storage_path=str(path),
                content_hash=content_hash,
                status="CURRENT",
                notes=notes,
            )

            db.add(document_version)
            db.flush()

            sections: list[Section] = []
            evidence: list[Evidence] = []

            for parsed_section in parsed_sections:
                section = Section(
                    document_version_id=document_version.id,
                    section_number=parsed_section.section_number,
                    title=parsed_section.title,
                    page_start=parsed_section.page_start,
                    page_end=parsed_section.page_end,
                    raw_text=parsed_section.raw_text,
                )

                db.add(section)
                db.flush()

                sections.append(section)

                evidence_record = Evidence(
                    section_id=section.id,
                    page=parsed_section.page_start,
                    quote=parsed_section.raw_text,
                    confidence=None,
                )

                db.add(evidence_record)
                evidence.append(evidence_record)

            db.commit()

            return DocumentPersistenceResult(
                document=document,
                document_version=document_version,
                sections=tuple(sections),
                evidence=tuple(evidence),
                created=True,
            )

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def _calculate_hash(path: Path) -> str:
        digest = sha256()

        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)

        return digest.hexdigest()

    @staticmethod
    def _get_or_create_document(
        *,
        db: Session,
        source_id: UUID,
        title: str,
        document_type: str,
        url: str | None,
        description: str | None,
    ) -> Document:
        document = db.scalar(
            select(Document).where(
                Document.source_id == source_id,
                Document.title == title,
            )
        )

        if document is not None:
            return document

        document = Document(
            source_id=source_id,
            title=title,
            document_type=document_type,
            url=url,
            description=description,
        )

        db.add(document)
        db.flush()

        return document