from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.business_profile_entity import BusinessProfileEntity
from src.models.entity import Entity
from src.services.claim_structure import ApplicabilityCondition


class ApplicabilityStatus(str, Enum):
    APPLIES = "APPLIES"
    DOES_NOT_APPLY = "DOES_NOT_APPLY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ApplicabilityResult:
    status: ApplicabilityStatus
    matched_conditions: tuple[ApplicabilityCondition, ...]
    unmatched_conditions: tuple[ApplicabilityCondition, ...]
    reason: str


class ApplicabilityService:
    """
    Deterministically evaluate whether a policy change condition
    applies to a business profile.

    The service does not use:
    - LLM inference
    - embeddings
    - fuzzy matching
    - semantic similarity

    Missing business information produces UNKNOWN rather than
    DOES_NOT_APPLY.
    """

    def evaluate(
        self,
        db: Session,
        *,
        business_profile_id: UUID,
        conditions: tuple[ApplicabilityCondition, ...],
    ) -> ApplicabilityResult:
        if not conditions:
            return ApplicabilityResult(
                status=ApplicabilityStatus.UNKNOWN,
                matched_conditions=(),
                unmatched_conditions=(),
                reason="No applicability conditions were provided.",
            )

        matched: list[ApplicabilityCondition] = []
        unmatched: list[ApplicabilityCondition] = []

        for condition in conditions:
            entities = (
                db.query(Entity)
                .join(
                    BusinessProfileEntity,
                    BusinessProfileEntity.entity_id == Entity.id,
                )
                .filter(
                    BusinessProfileEntity.business_profile_id
                    == business_profile_id,
                    BusinessProfileEntity.relation_type
                    == condition.relation_type,
                    Entity.entity_type == condition.entity_type,
                )
                .all()
            )

            normalized_names = {
                entity.name.strip().upper()
                for entity in entities
            }

            expected_names = {
                name.strip().upper()
                for name in condition.entity_names
            }

            if normalized_names & expected_names:
                matched.append(condition)
            else:
                unmatched.append(condition)

        if unmatched:
            known_relation_types = {
                condition.relation_type
                for condition in conditions
            }

            known_profile_relations = {
                relation_type
                for relation_type, in (
                    db.query(BusinessProfileEntity.relation_type)
                    .filter(
                        BusinessProfileEntity.business_profile_id
                        == business_profile_id
                    )
                    .distinct()
                    .all()
                )
            }

            missing_relation_types = (
                known_relation_types - known_profile_relations
            )

            if missing_relation_types:
                return ApplicabilityResult(
                    status=ApplicabilityStatus.UNKNOWN,
                    matched_conditions=tuple(matched),
                    unmatched_conditions=tuple(unmatched),
                    reason=(
                        "The business profile does not contain enough "
                        "information to determine applicability."
                    ),
                )

            return ApplicabilityResult(
                status=ApplicabilityStatus.DOES_NOT_APPLY,
                matched_conditions=tuple(matched),
                unmatched_conditions=tuple(unmatched),
                reason=(
                    "The business profile contains information that "
                    "does not satisfy the applicability conditions."
                ),
            )

        return ApplicabilityResult(
            status=ApplicabilityStatus.APPLIES,
            matched_conditions=tuple(matched),
            unmatched_conditions=(),
            reason="All applicability conditions are satisfied.",
        )