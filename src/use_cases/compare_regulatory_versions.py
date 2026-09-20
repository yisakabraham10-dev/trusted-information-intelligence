import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.exceptions import InvalidStateError, NotFoundError

from src.models.claim import Claim
from src.models.claim_correspondence import ClaimCorrespondence
from src.models.claim_evidence import ClaimEvidence
from src.models.claim_structure import ClaimStructure as ClaimStructureModel
from src.services.change_detector import ChangeDetectionResult, ChangeDetector
from src.services.claim_correspondence import (
    CorrespondenceEvaluator,
    CorrespondenceResult,
)
from src.services.claim_structure_deserialization import (
    ClaimStructureDeserializer,
)
from src.services.policy_change_service import PolicyChangePersistenceResult
from src.services.policy_change_service import PolicyChangeService


@dataclass(frozen=True)
class CompareRegulatoryVersionsResult:
    old_claim_id: uuid.UUID | None
    new_claim_id: uuid.UUID | None
    correspondence: CorrespondenceResult | None
    detection: ChangeDetectionResult | None
    policy_change: PolicyChangePersistenceResult | None


class CompareRegulatoryVersions:
    """
    Compare two regulatory claims and persist a detected policy change.

    This is an application-level workflow. It owns the transaction for
    the complete comparison operation.
    """

    def __init__(
        self,
        *,
        deserializer: ClaimStructureDeserializer | None = None,
        evaluator: CorrespondenceEvaluator | None = None,
        detector: ChangeDetector | None = None,
        policy_change_service: PolicyChangeService | None = None,
    ) -> None:
        self._deserializer = (
            deserializer or ClaimStructureDeserializer()
        )
        self._evaluator = (
            evaluator or CorrespondenceEvaluator()
        )
        self._detector = detector or ChangeDetector()
        self._policy_change_service = (
            policy_change_service or PolicyChangeService()
        )

    def execute(
        self,
        session: Session,
        *,
        old_claim_id: uuid.UUID | None,
        new_claim_id: uuid.UUID | None,
        effective_date: datetime | None = None,
        reason_claim_id: uuid.UUID | None = None,
    ) -> CompareRegulatoryVersionsResult:
        if old_claim_id is None and new_claim_id is None:
            raise InvalidStateError(
                "At least one claim must be provided."
            )

        old_claim = self._get_claim(session, old_claim_id)
        new_claim = self._get_claim(session, new_claim_id)

        if old_claim_id is not None and old_claim is None:
            raise NotFoundError(
                f"Old claim not found: {old_claim_id}"
            )

        if new_claim_id is not None and new_claim is None:
            raise NotFoundError(
                f"New claim not found: {new_claim_id}"
            )

        try:
            correspondence = None
            claim_correspondence = None

            claims_to_check = tuple(
                claim
                for claim in (old_claim, new_claim)
                if claim is not None
            )

            for claim in claims_to_check:
                if not self._has_supporting_evidence(
                    session,
                    claim.id,
                ):
                    return CompareRegulatoryVersionsResult(
                        old_claim_id=old_claim.id if old_claim else None,
                        new_claim_id=new_claim.id if new_claim else None,
                        correspondence=None,
                        detection=ChangeDetectionResult(
                            change_type="REQUIRES_REVIEW",
                            summary=(
                                "The claim does not have supporting evidence "
                                "that can be verified by the system."
                            ),
                        ),
                        policy_change=None,
                    )

            if old_claim is not None and new_claim is not None:
                old_structure = self._get_structure(
                    session,
                    old_claim.id,
                )
                new_structure = self._get_structure(
                    session,
                    new_claim.id,
                )

                if old_structure is None:
                    raise NotFoundError(
                        f"Semantic structure not found for old claim: "
                        f"{old_claim.id}"
                    )

                if new_structure is None:
                    raise NotFoundError(
                        f"Semantic structure not found for new claim: "
                        f"{new_claim.id}"
                    )

                old_domain_structure = self._deserializer.deserialize(
                    old_structure
                )
                new_domain_structure = self._deserializer.deserialize(
                    new_structure
                )

                correspondence = self._evaluator.evaluate(
                    old_claim,
                    new_claim,
                    old_domain_structure,
                    new_domain_structure,
                )

                claim_correspondence = ClaimCorrespondence(
                    id=uuid.uuid4(),
                    claim_a_id=old_claim.id,
                    claim_b_id=new_claim.id,
                    relationship_type=correspondence.relationship_type,
                    confidence=correspondence.confidence,
                    method=correspondence.method,
                    status="PENDING",
                )

                session.add(claim_correspondence)
                session.flush()

            detection = self._detector.detect(
                correspondence
                or CorrespondenceResult(
                    relationship_type="UNRELATED",
                    confidence=0.0,
                    method="CLAIM_ABSENCE",
                ),
                old_claim_exists=old_claim is not None,
                new_claim_exists=new_claim is not None,
            )

            if detection is None:
                session.commit()

                return CompareRegulatoryVersionsResult(
                    old_claim_id=old_claim.id if old_claim else None,
                    new_claim_id=new_claim.id if new_claim else None,
                    correspondence=correspondence,
                    detection=None,
                    policy_change=None,
                )

            if detection.change_type == "REQUIRES_REVIEW":
                session.commit()

                return CompareRegulatoryVersionsResult(
                    old_claim_id=old_claim.id if old_claim else None,
                    new_claim_id=new_claim.id if new_claim else None,
                    correspondence=correspondence,
                    detection=detection,
                    policy_change=None,
                )

            policy_change = self._policy_change_service.create(
                session,
                detection=detection,
                claim_correspondence=claim_correspondence,
                old_claim=old_claim,
                new_claim=new_claim,
                reason_claim_id=reason_claim_id,
                effective_date=effective_date,
            )

            session.commit()

            return CompareRegulatoryVersionsResult(
                old_claim_id=old_claim.id if old_claim else None,
                new_claim_id=new_claim.id if new_claim else None,
                correspondence=correspondence,
                detection=detection,
                policy_change=policy_change,
            )

        except Exception:
            session.rollback()
            raise

    @staticmethod
    def _get_claim(
        session: Session,
        claim_id: uuid.UUID | None,
    ) -> Claim | None:
        if claim_id is None:
            return None

        return session.scalar(
            select(Claim).where(Claim.id == claim_id)
        )

    @staticmethod
    def _get_structure(
        session: Session,
        claim_id: uuid.UUID,
    ) -> ClaimStructureModel | None:
        return session.scalar(
            select(ClaimStructureModel).where(
                ClaimStructureModel.claim_id == claim_id
            )
        )

    @staticmethod
    def _has_supporting_evidence(
        session: Session,
        claim_id: uuid.UUID,
    ) -> bool:
        evidence_id = session.scalar(
            select(ClaimEvidence.evidence_id)
            .where(
                ClaimEvidence.claim_id == claim_id,
                ClaimEvidence.relation_type == "SUPPORTS",
                ClaimEvidence.strength > 0,
            )
            .limit(1)
        )

        return evidence_id is not None
