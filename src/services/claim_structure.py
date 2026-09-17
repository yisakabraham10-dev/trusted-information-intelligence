from dataclasses import dataclass
from decimal import Decimal
from typing import Literal
import uuid


@dataclass(frozen=True)
class EntityRef:
    entity_id: uuid.UUID | None
    raw_text: str


@dataclass(frozen=True)
class Quantity:
    value: Decimal
    unit: str


@dataclass(frozen=True)
class Duration:
    value: Decimal
    unit: str


@dataclass(frozen=True)
class Condition:
    raw_text: str


@dataclass(frozen=True)
class RequirementStructure:
    actor: EntityRef | None
    modality: Literal["REQUIRED", "PROHIBITED", "PERMITTED"]
    action: str
    object: EntityRef | None
    deadline: Duration | None
    exception_ids: tuple[uuid.UUID, ...] = ()


@dataclass(frozen=True)
class FeeStructure:
    subject: EntityRef
    attribute: str
    value: Quantity


@dataclass(frozen=True)
class DefinitionStructure:
    term: str
    definition: str


@dataclass(frozen=True)
class ApplicabilityStructure:
    subject: EntityRef
    condition: Condition | None


@dataclass(frozen=True)
class ExceptionStructure:
    modifies_claim_id: uuid.UUID | None
    condition: Condition


@dataclass(frozen=True)
class PenaltyStructure:
    violation_description: str
    consequence: Quantity | str


ClaimStructure = (
    RequirementStructure
    | FeeStructure
    | DefinitionStructure
    | ApplicabilityStructure
    | ExceptionStructure
    | PenaltyStructure
)