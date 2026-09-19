from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class EntityRefSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_text: str


class DurationSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: Decimal
    unit: str


class QuantitySchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: Decimal
    unit: str


class ApplicabilityConditionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relation_type: str
    entity_type: str
    entity_names: list[str]


class RequirementStructureSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor: EntityRefSchema | None = None
    modality: str
    action: str
    object: EntityRefSchema | None = None
    deadline: DurationSchema | None = None
    applicability_conditions: list[ApplicabilityConditionSchema] = Field(
        default_factory=list
    )


class FeeStructureSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: EntityRefSchema
    attribute: str
    value: QuantitySchema


class DefinitionStructureSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    term: str
    definition: str


class ApplicabilityStructureSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: EntityRefSchema
    condition: str | None = None


class ExceptionStructureSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    condition: str


class PenaltyStructureSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    violation_description: str
    consequence: str


class ClaimExtractionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_type: str
    text: str
    section_number: str | None
    structure_type: str

    requirement: RequirementStructureSchema | None = None
    fee: FeeStructureSchema | None = None
    definition: DefinitionStructureSchema | None = None
    applicability: ApplicabilityStructureSchema | None = None
    exception: ExceptionStructureSchema | None = None
    penalty: PenaltyStructureSchema | None = None

class ClaimExtractionListSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claims: list[ClaimExtractionSchema]
