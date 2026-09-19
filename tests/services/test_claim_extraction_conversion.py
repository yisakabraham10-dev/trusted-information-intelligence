from decimal import Decimal

import pytest

from src.services.claim_extraction_conversion import (
    ClaimExtractionConversionError,
    ClaimExtractionConverter,
)
from src.services.claim_extraction_schema import (
    ApplicabilityStructureSchema,
    ClaimExtractionSchema,
    DefinitionStructureSchema,
    EntityRefSchema,
    ExceptionStructureSchema,
    FeeStructureSchema,
    PenaltyStructureSchema,
    QuantitySchema,
    RequirementStructureSchema,
    DurationSchema,
)
from src.services.claim_structure import (
    ApplicabilityStructure,
    DefinitionStructure,
    ExceptionStructure,
    FeeStructure,
    PenaltyStructure,
    RequirementStructure,
)


def test_requirement_schema_converts_to_requirement_structure():
    schema = ClaimExtractionSchema(
        claim_type="REQUIREMENT",
        text="Goods must be removed within 45 days.",
        section_number="51(1)",
        structure_type="REQUIREMENT",
        requirement=RequirementStructureSchema(
            actor=EntityRefSchema(raw_text="importer"),
            modality="REQUIRED",
            action="remove",
            object=EntityRefSchema(raw_text="goods"),
            deadline=DurationSchema(
                value=Decimal("45"),
                unit="DAYS",
            ),
        ),
    )

    candidate = ClaimExtractionConverter().convert(schema)

    assert isinstance(candidate.structure, RequirementStructure)
    assert candidate.claim_type == "REQUIREMENT"
    assert candidate.section_number == "51(1)"
    assert candidate.structure.modality == "REQUIRED"
    assert candidate.structure.action == "remove"
    assert candidate.structure.deadline.value == Decimal("45")
    assert candidate.structure.deadline.unit == "DAYS"


def test_fee_schema_converts_to_fee_structure():
    schema = ClaimExtractionSchema(
        claim_type="FEE",
        text="The importer shall pay a processing fee.",
        section_number="12",
        structure_type="FEE",
        fee=FeeStructureSchema(
            subject=EntityRefSchema(raw_text="importer"),
            attribute="processing fee",
            value=QuantitySchema(
                value=Decimal("100"),
                unit="ETB",
            ),
        ),
    )

    candidate = ClaimExtractionConverter().convert(schema)

    assert isinstance(candidate.structure, FeeStructure)
    assert candidate.structure.subject.raw_text == "importer"
    assert candidate.structure.attribute == "processing fee"
    assert candidate.structure.value.value == Decimal("100")


def test_definition_schema_converts_to_definition_structure():
    schema = ClaimExtractionSchema(
        claim_type="DEFINITION",
        text="Importer means a person who imports goods.",
        section_number="3",
        structure_type="DEFINITION",
        definition=DefinitionStructureSchema(
            term="Importer",
            definition="A person who imports goods.",
        ),
    )

    candidate = ClaimExtractionConverter().convert(schema)

    assert isinstance(candidate.structure, DefinitionStructure)
    assert candidate.structure.term == "Importer"


def test_applicability_schema_converts_to_applicability_structure():
    schema = ClaimExtractionSchema(
        claim_type="APPLICABILITY",
        text="This provision applies to importers.",
        section_number="4",
        structure_type="APPLICABILITY",
        applicability=ApplicabilityStructureSchema(
            subject=EntityRefSchema(raw_text="importers"),
            condition="when importing goods",
        ),
    )

    candidate = ClaimExtractionConverter().convert(schema)

    assert isinstance(candidate.structure, ApplicabilityStructure)
    assert candidate.structure.subject.raw_text == "importers"
    assert candidate.structure.condition.raw_text == "when importing goods"


def test_exception_schema_converts_to_exception_structure():
    schema = ClaimExtractionSchema(
        claim_type="EXCEPTION",
        text="This requirement does not apply during force majeure.",
        section_number="5",
        structure_type="EXCEPTION",
        exception=ExceptionStructureSchema(
            condition="during force majeure",
        ),
    )

    candidate = ClaimExtractionConverter().convert(schema)

    assert isinstance(candidate.structure, ExceptionStructure)
    assert candidate.structure.modifies_claim_id is None
    assert candidate.structure.condition.raw_text == "during force majeure"


def test_penalty_schema_converts_to_penalty_structure():
    schema = ClaimExtractionSchema(
        claim_type="PENALTY",
        text="Failure to comply results in a fine.",
        section_number="6",
        structure_type="PENALTY",
        penalty=PenaltyStructureSchema(
            violation_description="Failure to comply",
            consequence="fine",
        ),
    )

    candidate = ClaimExtractionConverter().convert(schema)

    assert isinstance(candidate.structure, PenaltyStructure)
    assert candidate.structure.violation_description == "Failure to comply"
    assert candidate.structure.consequence == "fine"


def test_missing_matching_structure_fails():
    schema = ClaimExtractionSchema(
        claim_type="REQUIREMENT",
        text="Goods must be removed.",
        section_number="51(1)",
        structure_type="REQUIREMENT",
    )

    with pytest.raises(ClaimExtractionConversionError):
        ClaimExtractionConverter().convert(schema)


def test_invalid_requirement_modality_fails():
    schema = ClaimExtractionSchema(
        claim_type="REQUIREMENT",
        text="Goods must be removed.",
        section_number="51(1)",
        structure_type="REQUIREMENT",
        requirement=RequirementStructureSchema(
            modality="MAYBE",
            action="remove",
        ),
    )

    with pytest.raises(ClaimExtractionConversionError):
        ClaimExtractionConverter().convert(schema)


def test_multiple_structure_payload_fails():
    schema = ClaimExtractionSchema(
        claim_type="REQUIREMENT",
        text="Goods must be removed.",
        section_number="51(1)",
        structure_type="REQUIREMENT",
        requirement=RequirementStructureSchema(
            modality="REQUIRED",
            action="remove",
        ),
        fee=FeeStructureSchema(
            subject=EntityRefSchema(raw_text="importer"),
            attribute="processing fee",
            value=QuantitySchema(
                value=Decimal("100"),
                unit="ETB",
            ),
        ),
    )

    with pytest.raises(ClaimExtractionConversionError):
        ClaimExtractionConverter().convert(schema)
