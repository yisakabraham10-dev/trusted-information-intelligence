from decimal import Decimal
from types import SimpleNamespace

from src.config import Settings
from src.services.claim_extraction_schema import (
    ClaimExtractionSchema,
    DurationSchema,
    EntityRefSchema,
    RequirementStructureSchema,
)
from src.services.document_structure import ParsedSection
from src.services.gemini_claim_extraction import (
    GeminiClaimExtractionProvider,
)


def test_gemini_provider_converts_structured_response_to_candidate(monkeypatch):
    section = ParsedSection(
        section_number="51(1)",
        title=None,
        section_type="SUB_ARTICLE",
        page_start=12,
        page_end=12,
        raw_text=(
            "Goods transported by sea or land shall be removed "
            "within forty-five days."
        ),
    )

    structured_output = ClaimExtractionSchema(
        claim_type="REQUIREMENT",
        text="Goods transported by sea or land shall be removed within forty-five days.",
        section_number="51(1)",
        structure_type="REQUIREMENT",
        requirement=RequirementStructureSchema(
            actor=None,
            modality="REQUIRED",
            action="remove",
            object=EntityRefSchema(
                raw_text="goods transported by sea or land",
            ),
            deadline=DurationSchema(
                value=Decimal("45"),
                unit="days",
            ),
            applicability_conditions=[],
        ),
    )

    captured = {}

    class FakeModels:
        def generate_content(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                parsed=structured_output,
                text=None,
            )

    class FakeClient:
        def __init__(self):
            self.models = FakeModels()

    monkeypatch.setattr(
        "src.services.gemini_claim_extraction.genai.Client",
        lambda api_key: FakeClient(),
    )

    settings = Settings(
        database_url="sqlite://",
        gemini_api_key="test-key",
    )

    provider = GeminiClaimExtractionProvider(settings)

    result = provider.extract(section)

    assert len(result) == 1

    candidate = result[0]

    assert candidate.claim_type == "REQUIREMENT"
    assert candidate.section_number == "51(1)"
    assert candidate.structure.modality == "REQUIRED"
    assert candidate.structure.deadline.value == Decimal("45")
    assert candidate.structure.deadline.unit == "DAYS"

    assert captured["model"] == "gemini-3.6-flash"
    assert captured["contents"]
    assert "forty-five days" in captured["contents"]
