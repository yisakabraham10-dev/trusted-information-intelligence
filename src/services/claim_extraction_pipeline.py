from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.exceptions import ValidationError

from src.services.claim_creation import ClaimCreationResult, ClaimCreationService
from src.services.claim_evidence_validation import ClaimEvidenceValidator
from src.services.claim_extraction import (
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
    ) -> tuple[ClaimCreationResult, ...]:
        candidates = self.extraction_provider.extract(parsed_section)

        if not candidates:
            raise ValidationError("Claim extraction produced no candidates.")

        from src.models.evidence import Evidence

        evidence = (
            db.query(Evidence)
            .filter(Evidence.section_id == section_id)
            .order_by(Evidence.page.asc(), Evidence.id.asc())
            .first()
        )

        if evidence is None:
            raise ValidationError(
                f"No evidence found for section {section_id}."
            )

        # Phase 1: validate every candidate before creating
        # anything in the database.
        for candidate in candidates:
            extraction_result = self.extraction_validator.validate(
                candidate
            )

            if not extraction_result.valid:
                raise ValidationError(
                    "Claim extraction validation failed: "
                    + "; ".join(extraction_result.errors)
                )

            evidence_result = self.evidence_validator.validate(
                candidate,
                parsed_section,
            )

            if not evidence_result.supported:
                raise ValidationError(
                    "Claim evidence validation failed: "
                    + "; ".join(evidence_result.errors)
                )

        # Phase 2: create every claim inside the caller-owned transaction.
        results = tuple(
            self.claim_creation_service.create_claim(
                db,
                section_id=section_id,
                claim_type=candidate.claim_type,
                text=candidate.text,
                evidence_ids=(evidence.id,),
                structure=candidate.structure,
            )
            for candidate in candidates
        )

        return results

        return results