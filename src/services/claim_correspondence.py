from dataclasses import dataclass

from src.models.claim import Claim


@dataclass(frozen=True)
class CorrespondenceResult:
    relationship_type: str
    confidence: float
    method: str


class CorrespondenceEvaluator:
    def evaluate(
        self,
        old_claim: Claim,
        new_claim: Claim,
    ) -> CorrespondenceResult:
        old_normalized = self._get_normalized_text(old_claim)
        new_normalized = self._get_normalized_text(new_claim)

        if old_normalized == new_normalized:
            return CorrespondenceResult(
                relationship_type="SAME",
                confidence=1.0,
                method="EXACT_NORMALIZED",
            )

        return CorrespondenceResult(
            relationship_type="UNRELATED",
            confidence=0.0,
            method="EXACT_NORMALIZED",
        )

    @staticmethod
    def _get_normalized_text(claim: Claim) -> str:
        if claim.normalized_text is not None:
            return claim.normalized_text

        return " ".join(claim.text.lower().split())
