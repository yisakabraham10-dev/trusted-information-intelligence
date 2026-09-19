from decimal import Decimal

from src.services.claim_extraction import ClaimExtractionCandidate
from src.services.claim_structure import (
    Duration,
    EntityRef,
    RequirementStructure,
)
from src.services.claim_evidence_validation import (
    ClaimEvidenceValidator,
)
from src.services.document_structure import ParsedSection


def test_supported_claim_passes_evidence_validation():
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
        text="Goods transported by sea or land must be removed within 45 days.",
        section_number="51(1)",
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

    result = ClaimEvidenceValidator().validate(candidate, section)

    assert result.supported is True
    assert result.errors == ()


def test_unsupported_claim_fails_evidence_validation():
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
        text="Goods must be removed within 90 days.",
        section_number="51(1)",
        structure=RequirementStructure(
            actor=None,
            modality="REQUIRED",
            action="remove",
            object=EntityRef(
                entity_id=None,
                raw_text="goods transported by sea or land",
            ),
            deadline=Duration(
                value=Decimal("90"),
                unit="DAYS",
            ),
        ),
    )

    result = ClaimEvidenceValidator().validate(candidate, section)

    assert result.supported is False
    assert "Requirement deadline is not supported by source section." in result.errors  

def test_equivalent_number_word_is_supported_by_source():
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
        text="Goods transported by sea or land must be removed within 45 days.",
        section_number="51(1)",
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

    result = ClaimEvidenceValidator().validate(candidate, section)

    assert result.supported is True
    assert result.errors == ()
