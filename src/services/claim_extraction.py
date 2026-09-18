from dataclasses import dataclass
from typing import Protocol

from src.services.claim_structure import ClaimStructure
from src.services.document_structure import ParsedSection


@dataclass(frozen=True)
class ClaimExtractionCandidate:
    claim_type: str
    text: str
    section_number: str | None
    structure: ClaimStructure


class ClaimExtractionProvider(Protocol):
    def extract(
        self,
        section: ParsedSection,
    ) -> tuple[ClaimExtractionCandidate, ...]:
        ...
