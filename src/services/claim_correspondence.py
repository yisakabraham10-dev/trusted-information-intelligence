from dataclasses import dataclass

from src.models.claim import Claim
from src.services.claim_structure import ClaimStructure
from src.services.requirement_comparison import compare_requirements


@dataclass(frozen=True)
class CorrespondenceResult:
    relationship_type: str
    confidence: float
    method: str
    changes: tuple[str, ...] = ()


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
        old_structure: ClaimStructure | None = None,
        new_structure: ClaimStructure | None = None,
    ) -> CorrespondenceResult:
        if not self._claim_types_compatible(
            old_claim,
            new_claim,
        ):
            return CorrespondenceResult(
                relationship_type="UNRELATED",
                confidence=1.0,
                method="CLAIM_TYPE_INCOMPATIBLE",
            )

        structured_result = self._evaluate_structured(
            old_claim,
            new_claim,
            old_structure,
            new_structure,
        )

        if structured_result is not None:
            return structured_result

        return self._evaluate_text(
            old_claim,
            new_claim,
        )

    @staticmethod
    def _evaluate_structured(
        old_claim: Claim,
        new_claim: Claim,
        old_structure: ClaimStructure | None,
        new_structure: ClaimStructure | None,
    ) -> CorrespondenceResult | None:
        if (
            old_claim.claim_type != "REQUIREMENT"
            or old_structure is None
            or new_structure is None
        ):
            return None

        result = compare_requirements(
            old_structure,
            new_structure,
        )

        return CorrespondenceResult(
            relationship_type=result.relationship_type,
            confidence=result.confidence,
            method=result.method,
            changes=result.changes,
        )

    @staticmethod
    def _evaluate_text(
        old_claim: Claim,
        new_claim: Claim,
    ) -> CorrespondenceResult:
        old_normalized = CorrespondenceEvaluator._get_normalized_text(
            old_claim
        )
        new_normalized = CorrespondenceEvaluator._get_normalized_text(
            new_claim
        )

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
        if claim.normalized_text:
            return " ".join(
                claim.normalized_text.lower().split()
            )

        return " ".join(
            claim.text.lower().split()
        )

    @classmethod
    def _claim_types_compatible(
        cls,
        old_claim: Claim,
        new_claim: Claim,
    ) -> bool:
        compatible_types = cls.COMPATIBLE_CLAIM_TYPES.get(
            old_claim.claim_type
        )

        if compatible_types is None:
            return old_claim.claim_type == new_claim.claim_type

        return new_claim.claim_type in compatible_types
