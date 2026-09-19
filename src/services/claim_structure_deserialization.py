from decimal import Decimal
from uuid import UUID

from src.models.claim_structure import ClaimStructure as ClaimStructureModel
from src.services.claim_structure import (
    ApplicabilityCondition,
    Duration,
    EntityRef,
    RequirementStructure,
)


class ClaimStructureDeserializer:
    """Reconstruct domain claim structures from persisted JSON."""

    def deserialize(
        self,
        persisted: ClaimStructureModel,
    ) -> RequirementStructure:
        if persisted.structure_type != "RequirementStructure":
            raise ValueError(
                f"Unsupported claim structure type: "
                f"{persisted.structure_type}"
            )

        data = persisted.structure

        actor_data = data["actor"]
        object_data = data["object"]
        deadline_data = data["deadline"]

        actor = (
            EntityRef(
                entity_id=(
                    UUID(actor_data["entity_id"])
                    if actor_data["entity_id"] is not None
                    else None
                ),
                raw_text=actor_data["raw_text"],
            )
            if actor_data is not None
            else None
        )

        object_ = (
            EntityRef(
                entity_id=(
                    UUID(object_data["entity_id"])
                    if object_data["entity_id"] is not None
                    else None
                ),
                raw_text=object_data["raw_text"],
            )
            if object_data is not None
            else None
        )

        deadline = (
            Duration(
                value=Decimal(str(deadline_data["value"])),
                unit=deadline_data["unit"],
            )
            if deadline_data is not None
            else None
        )

        applicability_conditions = tuple(
            ApplicabilityCondition(
                relation_type=condition["relation_type"],
                entity_type=condition["entity_type"],
                entity_names=tuple(condition["entity_names"]),
            )
            for condition in data.get("applicability_conditions", [])
        )

        return RequirementStructure(
            actor=actor,
            modality=data["modality"],
            action=data["action"],
            object=object_,
            deadline=deadline,
            exception_ids=tuple(
                UUID(value)
                for value in data.get("exception_ids", [])
            ),
            applicability_conditions=applicability_conditions,
        )
