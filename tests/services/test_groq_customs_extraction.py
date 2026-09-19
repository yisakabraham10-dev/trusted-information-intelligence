from pathlib import Path

from src.config import Settings
from src.services.document_ingestion import DocumentIngestionService
from src.services.groq_claim_extraction import GroqClaimExtractionProvider
from src.services.regulatory_structure import RegulatoryStructureParser


FIXTURE = Path(
    "tests/fixtures/customs_proclamation_1425_2026.pdf"
)


def test_groq_extracts_customs_article_51_requirement():
    settings = Settings()

    ingestion = DocumentIngestionService()
    ingested_document = ingestion.extract(FIXTURE)

    parser = RegulatoryStructureParser()
    parsed_sections = parser.parse(ingested_document.pages)

    section = next(
        section
        for section in parsed_sections
        if section.section_number == "51(1)"
    )

    provider = GroqClaimExtractionProvider(settings)

    candidates = provider.extract(section)

    assert len(candidates) == 1

    candidate = candidates[0]

    print("\n--- GROQ CLAIM ---")
    print(f"Claim type: {candidate.claim_type}")
    print(f"Section: {candidate.section_number}")
    print(f"Text: {candidate.text}")
    print(f"Structure: {candidate.structure}")
    print("------------------")

    assert candidate.claim_type
    assert candidate.text
    assert candidate.section_number == "51(1)"
    assert candidate.structure is not None
