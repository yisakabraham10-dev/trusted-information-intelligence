from decimal import Decimal

from src.services.claim_extraction import ClaimExtractionCandidate
from src.services.claim_structure import (
    Duration,
    EntityRef,
    RequirementStructure,
)


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
