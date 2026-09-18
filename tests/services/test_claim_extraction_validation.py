from decimal import Decimal

from src.services.claim_extraction import ClaimExtractionCandidate
from src.services.claim_structure import (
    Duration,
    EntityRef,
    RequirementStructure,
)
from src.services.claim_extraction_validation import (
    ClaimExtractionValidator,
)


def test_valid_requirement_candidate_passes_structural_validation():
    candidate = ClaimExtractionCandidate(
        claim_type="REQUIREMENT",
        text="Goods must be removed within 45 days.",
        section_number="51(1)",
        structure=RequirementStructure(
            actor=None,
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
        ),
    )

    result = ClaimExtractionValidator().validate(candidate)

    assert result.valid is True
    assert result.errors == ()


def test_empty_claim_text_fails_structural_validation():
    candidate = ClaimExtractionCandidate(
        claim_type="REQUIREMENT",
        text="",
        section_number="51(1)",
        structure=RequirementStructure(
            actor=None,
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
        ),
    )

    result = ClaimExtractionValidator().validate(candidate)

    assert result.valid is False
    assert "Claim text cannot be empty." in result.errors


def test_empty_claim_type_fails_structural_validation():
    candidate = ClaimExtractionCandidate(
        claim_type="",
        text="Goods must be removed within 45 days.",
        section_number="51(1)",
        structure=RequirementStructure(
            actor=None,
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
        ),
    )

    result = ClaimExtractionValidator().validate(candidate)

    assert result.valid is False
    assert "Claim type cannot be empty." in result.errors


def test_empty_claim_type_fails_structural_validation():
    candidate = ClaimExtractionCandidate(
        claim_type="",
        text="Goods must be removed within 45 days.",
        section_number="51(1)",
        structure=RequirementStructure(
            actor=None,
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
        ),
    )

    result = ClaimExtractionValidator().validate(candidate)

    assert result.valid is False
    assert "Claim type cannot be empty." in result.errors


def test_empty_section_number_fails_structural_validation():
    candidate = ClaimExtractionCandidate(
        claim_type="REQUIREMENT",
        text="Goods must be removed within 45 days.",
        section_number="",
        structure=RequirementStructure(
            actor=None,
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
        ),
    )

    result = ClaimExtractionValidator().validate(candidate)

    assert result.valid is False
    assert "Section number cannot be empty." in result.errors


def test_empty_section_number_fails_structural_validation():
    candidate = ClaimExtractionCandidate(
        claim_type="REQUIREMENT",
        text="Goods must be removed within 45 days.",
        section_number="",
        structure=RequirementStructure(
            actor=None,
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
        ),
    )

    result = ClaimExtractionValidator().validate(candidate)

    assert result.valid is False
    assert "Section number cannot be empty." in result.errors
