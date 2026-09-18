from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.claim import Claim
from src.models.claim_evidence import ClaimEvidence
from src.models.evidence import Evidence


@dataclass(frozen=True)
class ClaimCreationResult:
    claim: Claim
    evidence: tuple[Evidence, ...]


class ClaimCreationService:
    """
    Create source-backed Claims from already-verified document evidence.

    This service does not:
    - interpret arbitrary documents
    - call an LLM
    - determine whether a claim changed
    - compare claims across versions
    - create PolicyChanges

    A claim must already have a source section and evidence.
    """

    def create_claim(
        self,
        db: Session,
        *,
        section_id: UUID,
        claim_type: str,
        text: str,
        evidence_ids: tuple[UUID, ...],
        normalized_text: str | None = None,
        effective_from: datetime | None = None,
        effective_to: datetime | None = None,
        status: str = "ACTIVE",
    ) -> ClaimCreationResult:
        if not text.strip():
            raise ValueError("Claim text cannot be empty.")

        if not evidence_ids:
            raise ValueError(
                "A claim must have at least one supporting evidence record."
            )

        evidence_records = tuple(
            db.query(Evidence)
            .filter(
                Evidence.id.in_(evidence_ids),
                Evidence.section_id == section_id,
            )
            .all()
        )

        if len(evidence_records) != len(set(evidence_ids)):
            raise ValueError(
                "Every evidence record must exist and belong to the claim section."
            )

        claim = Claim(
            section_id=section_id,
            claim_type=claim_type,
            text=text,
            normalized_text=normalized_text,
            effective_from=effective_from,
            effective_to=effective_to,
            status=status,
        )

        db.add(claim)
        db.flush()

        for evidence in evidence_records:
            db.add(
                ClaimEvidence(
                    claim_id=claim.id,
                    evidence_id=evidence.id,
                    relation_type="SUPPORTS",
                    strength=1.0,
                )
            )

        db.commit()

        return ClaimCreationResult(
            claim=claim,
            evidence=evidence_records,
        )