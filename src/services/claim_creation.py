from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.claim import Claim
from src.models.claim_evidence import ClaimEvidence
from src.models.claim_structure import ClaimStructure as ClaimStructureModel
from src.models.evidence import Evidence
from src.services.claim_structure import ClaimStructure


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
        structure: ClaimStructure,
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

        db.add(
            ClaimStructureModel(
                claim_id=claim.id,
                structure_type=type(structure).__name__,
                structure=self._serialize_structure(structure),
            )
        )

        return ClaimCreationResult(
            claim=claim,
            evidence=evidence_records,
        )

    @staticmethod
    def _serialize_structure(structure: ClaimStructure) -> dict:
        value = ClaimCreationService._serialize_value(structure)

        if not isinstance(value, dict):
            raise ValueError("Claim structure must serialize to an object.")

        return value

    @staticmethod
    def _serialize_value(value):
        if is_dataclass(value) and not isinstance(value, type):
            return {
                key: ClaimCreationService._serialize_value(child)
                for key, child in asdict(value).items()
            }

        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, Decimal):
            return str(value)

        if isinstance(value, tuple):
            return [
                ClaimCreationService._serialize_value(item)
                for item in value
            ]

        if isinstance(value, list):
            return [
                ClaimCreationService._serialize_value(item)
                for item in value
            ]

        if isinstance(value, dict):
            return {
                key: ClaimCreationService._serialize_value(child)
                for key, child in value.items()
            }

        return value
