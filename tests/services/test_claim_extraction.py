from decimal import Decimal

from src.services.claim_extraction import (
    ClaimExtractionCandidate,
    ClaimExtractionService,
)
from src.services.claim_structure import (
    Duration,
    EntityRef,
    RequirementStructure,
)
from src.services.document_structure import ParsedSection


def test_claim_extraction_candidate_can_represent_a_requirement():
    importer = EntityRef(
        entity_id=None,
        raw_text="importers",
    )

    structure = RequirementStructure(
        actor=importer,
        modality="REQUIRED",
        action="remove",
        object=EntityRef(
            entity_id=None,
            raw_text="goods",
        ),
        deadline=Duration(
            value=Decimal("45"),
            unit="DAYS",
        ),
    )

    candidate = ClaimExtractionCandidate(
        claim_type="REQUIREMENT",
        text="Goods transported by sea or land must be removed within 45 days.",
        section_number="51(1)",
        structure=structure,
    )

    assert candidate.claim_type == "REQUIREMENT"
    assert candidate.section_number == "51(1)"
    assert candidate.text.startswith("Goods transported")
    assert candidate.structure == structure


def test_claim_extraction_provider_defines_extraction_contract():
    from src.services.claim_extraction import ClaimExtractionProvider

    assert hasattr(ClaimExtractionProvider, "extract")


def test_claim_extraction_service_delegates_to_provider():
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

    candidate = ClaimExtractionCandidate(
        claim_type="REQUIREMENT",
        text=section.raw_text,
        section_number=section.section_number,
        structure=RequirementStructure(
            actor=None,
            modality="REQUIRED",
            action="remove",
            object=EntityRef(
                entity_id=None,
                raw_text="goods transported by sea or land",
            ),
            deadline=Duration(
                value=Decimal("45"),
                unit="DAYS",
            ),
        ),
    )

    class FakeProvider:
        def extract(self, received_section):
            assert received_section == section
            return (candidate,)

    service = ClaimExtractionService(FakeProvider())

    result = service.extract(section)

    assert result == (candidate,)
