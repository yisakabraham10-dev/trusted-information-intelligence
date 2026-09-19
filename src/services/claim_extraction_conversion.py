from src.services.claim_extraction import ClaimExtractionCandidate
from src.services.claim_extraction_schema import ClaimExtractionSchema
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
)


class ClaimExtractionConversionError(ValueError):
    """Raised when a wire-schema extraction cannot become a domain candidate."""


class ClaimExtractionConverter:
    def convert(
        self,
        schema: ClaimExtractionSchema,
    ) -> ClaimExtractionCandidate:
        structure_type = schema.structure_type.strip().upper()

        structure_fields = {
            "REQUIREMENT": schema.requirement,
            "FEE": schema.fee,
            "DEFINITION": schema.definition,
            "APPLICABILITY": schema.applicability,
            "EXCEPTION": schema.exception,
            "PENALTY": schema.penalty,
        }

        if structure_type not in structure_fields:
            raise ClaimExtractionConversionError(
                f"Unsupported structure type: {schema.structure_type}"
            )

        populated_structures = [
            name
            for name, value in structure_fields.items()
            if value is not None
        ]

        if len(populated_structures) != 1:
            raise ClaimExtractionConversionError(
                "Exactly one claim structure must be populated."
            )

        if populated_structures[0] != structure_type:
            raise ClaimExtractionConversionError(
                "Populated claim structure does not match structure type."
            )

        builders = {
            "REQUIREMENT": self._requirement,
            "FEE": self._fee,
            "DEFINITION": self._definition,
            "APPLICABILITY": self._applicability,
            "EXCEPTION": self._exception,
            "PENALTY": self._penalty,
        }

        structure = builders[structure_type](schema)

        return ClaimExtractionCandidate(
            claim_type=schema.claim_type,
            text=schema.text,
            section_number=schema.section_number,
            structure=structure,
        )

    @staticmethod
    def _requirement(schema: ClaimExtractionSchema) -> RequirementStructure:
        if schema.requirement is None:
            raise ClaimExtractionConversionError(
                "REQUIREMENT extraction is missing requirement structure."
            )

        data = schema.requirement

        modality = data.modality.strip().upper()
        if modality not in {"REQUIRED", "PROHIBITED", "PERMITTED"}:
            raise ClaimExtractionConversionError(
                f"Unsupported requirement modality: {data.modality}"
            )

        actor = (
            EntityRef(entity_id=None, raw_text=data.actor.raw_text)
            if data.actor is not None
            else None
        )

        object_ref = (
            EntityRef(entity_id=None, raw_text=data.object.raw_text)
            if data.object is not None
            else None
        )

        deadline = (
            Duration(
                value=data.deadline.value,
                unit=data.deadline.unit.upper(),
            )
            if data.deadline is not None
            else None
        )

        applicability_conditions = tuple(
            ApplicabilityCondition(
                relation_type=condition.relation_type,
                entity_type=condition.entity_type,
                entity_names=tuple(condition.entity_names),
            )
            for condition in data.applicability_conditions
        )

        return RequirementStructure(
            actor=actor,
            modality=modality,
            action=data.action,
            object=object_ref,
            deadline=deadline,
            applicability_conditions=applicability_conditions,
        )

    @staticmethod
    def _fee(schema: ClaimExtractionSchema) -> FeeStructure:
        if schema.fee is None:
            raise ClaimExtractionConversionError(
                "FEE extraction is missing fee structure."
            )

        data = schema.fee

        return FeeStructure(
            subject=EntityRef(
                entity_id=None,
                raw_text=data.subject.raw_text,
            ),
            attribute=data.attribute,
            value=Quantity(
                value=data.value.value,
                unit=data.value.unit,
            ),
        )

    @staticmethod
    def _definition(schema: ClaimExtractionSchema) -> DefinitionStructure:
        if schema.definition is None:
            raise ClaimExtractionConversionError(
                "DEFINITION extraction is missing definition structure."
            )

        data = schema.definition

        return DefinitionStructure(
            term=data.term,
            definition=data.definition,
        )

    @staticmethod
    def _applicability(
        schema: ClaimExtractionSchema,
    ) -> ApplicabilityStructure:
        if schema.applicability is None:
            raise ClaimExtractionConversionError(
                "APPLICABILITY extraction is missing applicability structure."
            )

        data = schema.applicability

        condition = (
            Condition(raw_text=data.condition)
            if data.condition is not None
            else None
        )

        return ApplicabilityStructure(
            subject=EntityRef(
                entity_id=None,
                raw_text=data.subject.raw_text,
            ),
            condition=condition,
        )

    @staticmethod
    def _exception(schema: ClaimExtractionSchema) -> ExceptionStructure:
        if schema.exception is None:
            raise ClaimExtractionConversionError(
                "EXCEPTION extraction is missing exception structure."
            )

        return ExceptionStructure(
            modifies_claim_id=None,
            condition=Condition(raw_text=schema.exception.condition),
        )

    @staticmethod
    def _penalty(schema: ClaimExtractionSchema) -> PenaltyStructure:
        if schema.penalty is None:
            raise ClaimExtractionConversionError(
                "PENALTY extraction is missing penalty structure."
            )

        data = schema.penalty

        return PenaltyStructure(
            violation_description=data.violation_description,
            consequence=data.consequence,
        )
