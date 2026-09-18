import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.claim import Claim
from src.models.claim_correspondence import ClaimCorrespondence
from src.models.policy_change import PolicyChange
from src.models.policy_change_claim import PolicyChangeClaim
from src.models.policy_change_correspondence import (
    PolicyChangeCorrespondence,
)
from src.services.change_detector import ChangeDetectionResult


@dataclass(frozen=True)
class PolicyChangePersistenceResult:
    policy_change_id: uuid.UUID
    change_type: str


class PolicyChangeService:
    """
    Persist a detected policy change and its relationships.

    This service is responsible for persistence only.
    Change classification belongs to ChangeDetector.
    """

    def create(
        self,
        session: Session,
        *,
        detection: ChangeDetectionResult,
        claim_correspondence: ClaimCorrespondence | None = None,
        old_claim: Claim | None = None,
        new_claim: Claim | None = None,
        reason_claim_id: uuid.UUID | None = None,
        effective_date: datetime | None = None,
    ) -> PolicyChangePersistenceResult:
        if old_claim is None and new_claim is None:
            raise ValueError(
                "At least one claim must be provided."
            )

        policy_change = PolicyChange(
            id=uuid.uuid4(),
            change_type=detection.change_type,
            summary=detection.summary,
            effective_date=effective_date,
            reason_claim_id=reason_claim_id,
            status="ACTIVE",
        )

        session.add(policy_change)
        session.flush()

        if old_claim is not None:
            session.add(
                PolicyChangeClaim(
                    policy_change_id=policy_change.id,
                    claim_id=old_claim.id,
                    role="OLD",
                )
            )

        if new_claim is not None:
            session.add(
                PolicyChangeClaim(
                    policy_change_id=policy_change.id,
                    claim_id=new_claim.id,
                    role="NEW",
                )
            )

        if claim_correspondence is not None:
            session.add(
                PolicyChangeCorrespondence(
                    policy_change_id=policy_change.id,
                    correspondence_id=claim_correspondence.id,
                )
            )

        session.flush()

        return PolicyChangePersistenceResult(
            policy_change_id=policy_change.id,
            change_type=policy_change.change_type,
        )