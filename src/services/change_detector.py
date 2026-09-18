from dataclasses import dataclass

from src.services.claim_correspondence import CorrespondenceResult


@dataclass(frozen=True)
class ChangeDetectionResult:
    change_type: str
    summary: str


class ChangeDetector:
    """
    Convert claim correspondence into a policy-change classification.

    This service does not:
    - discover claim correspondence
    - persist database records
    - decide whether two claims correspond

    It only interprets an already-evaluated correspondence.
    """

    def detect(
        self,
        correspondence: CorrespondenceResult,
        old_claim_exists: bool = True,
        new_claim_exists: bool = True,
    ) -> ChangeDetectionResult | None:
        if not old_claim_exists and not new_claim_exists:
            raise ValueError(
                "At least one claim must exist."
            )

        if not old_claim_exists:
            return ChangeDetectionResult(
                change_type="ADDED",
                summary="A new claim was added.",
            )

        if not new_claim_exists:
            return ChangeDetectionResult(
                change_type="REMOVED",
                summary="An existing claim was removed.",
            )

        if correspondence.relationship_type == "MODIFIED":
            return ChangeDetectionResult(
                change_type="MODIFIED",
                summary="An existing claim was modified.",
            )

        if correspondence.relationship_type == "SAME":
            return None

        return None