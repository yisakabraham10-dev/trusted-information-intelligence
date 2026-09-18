from dataclasses import dataclass
from typing import Protocol

from src.services.document_ingestion import ExtractedPage


@dataclass(frozen=True)
class ParsedSection:
    section_number: str | None
    title: str | None
    section_type: str
    page_start: int
    page_end: int
    raw_text: str


class DocumentStructureParser(Protocol):
    def parse(
        self,
        pages: tuple[ExtractedPage, ...],
    ) -> tuple[ParsedSection, ...]:
        ...