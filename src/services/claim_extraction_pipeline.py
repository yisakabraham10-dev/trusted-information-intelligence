from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from src.services.claim_creation import ClaimCreationResult, ClaimCreationService
from src.services.claim_evidence_validation import ClaimEvidenceValidator
from src.services.claim_extraction import (
    ClaimExtractionCandidate,
    ClaimExtractionProvider,
)
from src.services.claim_extraction_validation import ClaimExtractionValidator
from src.services.document_structure import ParsedSection


@dataclass(frozen=True)
class ClaimExtractionPipeline:
    extraction_provider: ClaimExtractionProvider
    extraction_validator: ClaimExtractionValidator
    evidence_validator: ClaimEvidenceValidator
    claim_creation_service: ClaimCreationService

    def process(
        self,
        db: Session,
        *,
        section_id: UUID,
        parsed_section: ParsedSection,
    ) -> ClaimCreationResult:
        candidates = self.extraction_provider.extract(parsed_section)

        if not candidates:
            raise ValueError("Claim extraction produced no candidates.")

        if len(candidates) != 1:
            raise ValueError(
                "Claim extraction pipeline currently requires exactly one candidate."
            )

        candidate = candidates[0]

        extraction_result = self.extraction_validator.validate(candidate)

        if not extraction_result.valid:
            raise ValueError(
                "Claim extraction validation failed: "
                + "; ".join(extraction_result.errors)
            )

        from src.models.evidence import Evidence

        evidence = (
            db.query(Evidence)
            .filter(Evidence.section_id == section_id)
            .order_by(Evidence.page.asc(), Evidence.id.asc())
            .first()
        )

        if evidence is None:
            raise ValueError(
                f"No evidence found for section {section_id}."
            )

        evidence_result = self.evidence_validator.validate(
            candidate,
            parsed_section,
        )

        if not evidence_result.supported:
            raise ValueError(
                "Claim evidence validation failed: "
                + "; ".join(evidence_result.errors)
            )

        return self.claim_creation_service.create_claim(
            db,
            section_id=section_id,
            claim_type=candidate.claim_type,
            text=candidate.text,
            evidence_ids=(evidence.id,),
        )
