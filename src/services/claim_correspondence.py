from dataclasses import dataclass

from src.models.claim import Claim


@dataclass(frozen=True)
class CorrespondenceResult:
    relationship_type: str
    confidence: float
    method: str


class CorrespondenceEvaluator:
    COMPATIBLE_CLAIM_TYPES = {
        "REQUIREMENT": {"REQUIREMENT"},
        "PROHIBITION": {"PROHIBITION"},
        "PERMISSION": {"PERMISSION"},
        "FEE": {"FEE"},
        "DEADLINE": {"DEADLINE"},
    }

    def evaluate(
        self,
        old_claim: Claim,
        new_claim: Claim,
    ) -> CorrespondenceResult:
        if not self._claim_types_compatible(old_claim, new_claim):
            return CorrespondenceResult(
                relationship_type="UNRELATED",
                confidence=1.0,
                method="CLAIM_TYPE_INCOMPATIBLE",
            )

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

    @classmethod
    def _claim_types_compatible(
        cls,
        old_claim: Claim,
        new_claim: Claim,
    ) -> bool:
        compatible_types = cls.COMPATIBLE_CLAIM_TYPES.get(
            old_claim.claim_type,
            set(),
        )

        return new_claim.claim_type in compatible_types

    @staticmethod
    def _get_normalized_text(claim: Claim) -> str:
        if claim.normalized_text is not None:
            return claim.normalized_text

        return " ".join(claim.text.lower().split())
