from decimal import Decimal
from uuid import UUID

import pytest

from src.models.claim_structure import ClaimStructure
from src.services.claim_structure import (
    ApplicabilityStructure,
    Condition,
    DefinitionStructure,
    Duration,
    EntityRef,
    ExceptionStructure,
    FeeStructure,
    PenaltyStructure,
    Quantity,
    RequirementStructure,
)
from src.services.claim_structure_deserialization import (
    ClaimStructureDeserializer,
)


def test_deserializes_persisted_requirement_structure():
    persisted = ClaimStructure(
        claim_id=None,
        structure_type="RequirementStructure",
        structure={
            "actor": {
                "entity_id": None,
                "raw_text": "importers",
            },
            "modality": "REQUIRED",
            "action": "remove",
            "object": {
                "entity_id": None,
                "raw_text": "imported goods",
            },
            "deadline": {
                "value": "45",
                "unit": "DAYS",
            },
            "exception_ids": [],
            "applicability_conditions": [],
        },
    )

    result = ClaimStructureDeserializer().deserialize(persisted)

    assert result == RequirementStructure(
        actor=EntityRef(
            entity_id=None,
            raw_text="importers",
        ),
        modality="REQUIRED",
        action="remove",
        object=EntityRef(
            entity_id=None,
            raw_text="imported goods",
        ),
        deadline=Duration(
            value=Decimal("45"),
            unit="DAYS",
        ),
    )


def test_deserializes_persisted_fee_structure():
    entity_id = UUID("11111111-1111-1111-1111-111111111111")

    persisted = ClaimStructure(
        claim_id=None,
        structure_type="FeeStructure",
        structure={
            "subject": {
                "entity_id": str(entity_id),
                "raw_text": "importer",
            },
            "attribute": "customs duty",
            "value": {
                "value": "35",
                "unit": "PERCENT",
            },
        },
    )

    result = ClaimStructureDeserializer().deserialize(persisted)

    assert result == FeeStructure(
        subject=EntityRef(
            entity_id=entity_id,
            raw_text="importer",
        ),
        attribute="customs duty",
        value=Quantity(
            value=Decimal("35"),
            unit="PERCENT",
        ),
    )


def test_deserializes_persisted_definition_structure():
    persisted = ClaimStructure(
        claim_id=None,
        structure_type="DefinitionStructure",
        structure={
            "term": "temporary customs storage",
            "definition": "A designated location for temporarily stored goods.",
        },
    )

    result = ClaimStructureDeserializer().deserialize(persisted)

    assert result == DefinitionStructure(
        term="temporary customs storage",
        definition="A designated location for temporarily stored goods.",
    )


def test_deserializes_persisted_applicability_structure():
    entity_id = UUID("22222222-2222-2222-2222-222222222222")

    persisted = ClaimStructure(
        claim_id=None,
        structure_type="ApplicabilityStructure",
        structure={
            "subject": {
                "entity_id": str(entity_id),
                "raw_text": "importers",
            },
            "condition": "goods imported by sea",
        },
    )

    result = ClaimStructureDeserializer().deserialize(persisted)

    assert result == ApplicabilityStructure(
        subject=EntityRef(
            entity_id=entity_id,
            raw_text="importers",
        ),
        condition=Condition(
            raw_text="goods imported by sea",
        ),
    )


def test_deserializes_persisted_exception_structure():
    claim_id = UUID("33333333-3333-3333-3333-333333333333")

    persisted = ClaimStructure(
        claim_id=None,
        structure_type="ExceptionStructure",
        structure={
            "modifies_claim_id": str(claim_id),
            "condition": {
                "raw_text": "unless otherwise authorized",
            },
        },
    )

    result = ClaimStructureDeserializer().deserialize(persisted)

    assert result == ExceptionStructure(
        modifies_claim_id=claim_id,
        condition=Condition(
            raw_text="unless otherwise authorized",
        ),
    )


def test_deserializes_persisted_penalty_structure_with_quantity():
    persisted = ClaimStructure(
        claim_id=None,
        structure_type="PenaltyStructure",
        structure={
            "violation_description": "Failure to comply",
            "consequence": {
                "value": "5000",
                "unit": "ETB",
            },
        },
    )

    result = ClaimStructureDeserializer().deserialize(persisted)

    assert result == PenaltyStructure(
        violation_description="Failure to comply",
        consequence=Quantity(
            value=Decimal("5000"),
            unit="ETB",
        ),
    )


def test_deserializes_persisted_penalty_structure_with_text():
    persisted = ClaimStructure(
        claim_id=None,
        structure_type="PenaltyStructure",
        structure={
            "violation_description": "Failure to comply",
            "consequence": "Suspension of the license",
        },
    )

    result = ClaimStructureDeserializer().deserialize(persisted)

    assert result == PenaltyStructure(
        violation_description="Failure to comply",
        consequence="Suspension of the license",
    )


def test_deserializing_unsupported_structure_type_fails():
    persisted = ClaimStructure(
        claim_id=None,
        structure_type="UnknownStructure",
        structure={},
    )

    with pytest.raises(
        ValueError,
        match="Unsupported claim structure type",
    ):
        ClaimStructureDeserializer().deserialize(persisted)
