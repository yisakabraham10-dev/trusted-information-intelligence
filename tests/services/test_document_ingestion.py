from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class IngestedDocument:
    pages: tuple[ExtractedPage, ...]


class DocumentIngestionService:
    """
    Extract text from a PDF while preserving page-level provenance.

    This service does not:
    - interpret legal meaning
    - create claims
    - determine policy changes
    - call an LLM
    - modify source text
    """

    def extract(
        self,
        pdf_path: str | Path,
    ) -> IngestedDocument:
        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Expected a PDF file, got: {path.suffix}"
            )

        reader = PdfReader(str(path))

        pages: list[ExtractedPage] = []

        for index, page in enumerate(reader.pages):
            text = page.extract_text() or ""

            pages.append(
                ExtractedPage(
                    page_number=index + 1,
                    text=text,
                )
            )

        return IngestedDocument(
            pages=tuple(pages),
        )