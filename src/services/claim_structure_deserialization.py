from decimal import Decimal
from uuid import UUID

from src.models.claim_structure import ClaimStructure as ClaimStructureModel
from src.services.claim_structure import (
    ApplicabilityCondition,
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
    ClaimStructure,
)


class ClaimStructureDeserializer:
    """Reconstruct domain claim structures from persisted JSON."""

    def deserialize(
        self,
        persisted: ClaimStructureModel,
    ) -> ClaimStructure:
        builders = {
            "RequirementStructure": self._requirement,
            "FeeStructure": self._fee,
            "DefinitionStructure": self._definition,
            "ApplicabilityStructure": self._applicability,
            "ExceptionStructure": self._exception,
            "PenaltyStructure": self._penalty,
        }

        builder = builders.get(persisted.structure_type)

        if builder is None:
            raise ValueError(
                f"Unsupported claim structure type: "
                f"{persisted.structure_type}"
            )

        return builder(persisted.structure)

    @staticmethod
    def _entity_ref(data: dict | None) -> EntityRef | None:
        if data is None:
            return None

        return EntityRef(
            entity_id=(
                UUID(data["entity_id"])
                if data["entity_id"] is not None
                else None
            ),
            raw_text=data["raw_text"],
        )

    @staticmethod
    def _duration(data: dict | None) -> Duration | None:
        if data is None:
            return None

        return Duration(
            value=Decimal(str(data["value"])),
            unit=data["unit"],
        )

    @staticmethod
    def _quantity(data: dict) -> Quantity:
        return Quantity(
            value=Decimal(str(data["value"])),
            unit=data["unit"],
        )

    @staticmethod
    def _applicability_condition(
        data: dict,
    ) -> ApplicabilityCondition:
        return ApplicabilityCondition(
            relation_type=data["relation_type"],
            entity_type=data["entity_type"],
            entity_names=tuple(data["entity_names"]),
        )

    @classmethod
    def _requirement(
        cls,
        data: dict,
    ) -> RequirementStructure:
        return RequirementStructure(
            actor=cls._entity_ref(data["actor"]),
            modality=data["modality"],
            action=data["action"],
            object=cls._entity_ref(data["object"]),
            deadline=cls._duration(data["deadline"]),
            exception_ids=tuple(
                UUID(value)
                for value in data.get("exception_ids", [])
            ),
            applicability_conditions=tuple(
                cls._applicability_condition(condition)
                for condition in data.get(
                    "applicability_conditions",
                    [],
                )
            ),
        )

    @classmethod
    def _fee(
        cls,
        data: dict,
    ) -> FeeStructure:
        return FeeStructure(
            subject=cls._entity_ref(data["subject"]),
            attribute=data["attribute"],
            value=cls._quantity(data["value"]),
        )

    @classmethod
    def _definition(
        cls,
        data: dict,
    ) -> DefinitionStructure:
        return DefinitionStructure(
            term=data["term"],
            definition=data["definition"],
        )

    @classmethod
    def _applicability(
        cls,
        data: dict,
    ) -> ApplicabilityStructure:
        condition = data["condition"]

        return ApplicabilityStructure(
            subject=cls._entity_ref(data["subject"]),
            condition=(
                Condition(raw_text=condition)
                if condition is not None
                else None
            ),
        )

    @staticmethod
    def _exception(
        data: dict,
    ) -> ExceptionStructure:
        condition = data["condition"]

        if isinstance(condition, dict):
            condition = condition["raw_text"]

        return ExceptionStructure(
            modifies_claim_id=(
                UUID(data["modifies_claim_id"])
                if data["modifies_claim_id"] is not None
                else None
            ),
            condition=Condition(
                raw_text=condition,
            ),
        )

    @classmethod
    def _penalty(
        cls,
        data: dict,
    ) -> PenaltyStructure:
        consequence = data["consequence"]

        if isinstance(consequence, dict):
            consequence = cls._quantity(consequence)

        return PenaltyStructure(
            violation_description=data["violation_description"],
            consequence=consequence,
        )
