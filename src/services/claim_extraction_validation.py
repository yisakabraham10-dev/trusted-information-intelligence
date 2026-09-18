from dataclasses import dataclass

from src.services.claim_extraction import ClaimExtractionCandidate


@dataclass(frozen=True)
class ClaimExtractionValidationResult:
    valid: bool
    errors: tuple[str, ...]


class ClaimExtractionValidator:
    def validate(
        self,
        candidate: ClaimExtractionCandidate,
    ) -> ClaimExtractionValidationResult:
        errors: list[str] = []

        if not candidate.text.strip():
            errors.append("Claim text cannot be empty.")

        if not candidate.claim_type.strip():
            errors.append("Claim type cannot be empty.")

        if candidate.section_number is None or not candidate.section_number.strip():
            errors.append("Section number cannot be empty.")

        return ClaimExtractionValidationResult(
            valid=not errors,
            errors=tuple(errors),
        )
