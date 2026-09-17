from dataclasses import dataclass


@dataclass(frozen=True)
class CorrespondenceResult:
    relationship_type: str
    confidence: float
    method: str


class CorrespondenceEvaluator:
    def evaluate(
        self,
        old_text: str,
        new_text: str,
    ) -> CorrespondenceResult:
        old_normalized = self._normalize(old_text)
        new_normalized = self._normalize(new_text)

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
    def _normalize(text: str) -> str:
        return " ".join(text.lower().split())