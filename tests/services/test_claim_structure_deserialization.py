from decimal import Decimal

from src.models.claim_structure import ClaimStructure
from src.services.claim_structure import (
    Duration,
    EntityRef,
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
