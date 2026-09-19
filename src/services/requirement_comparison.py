from dataclasses import dataclass

from src.services.claim_structure import RequirementStructure
from src.services.primitive_comparison import (
    ComparisonKind,
    FieldComparison,
    compare_entity_ref,
    compare_optional_duration,
)


@dataclass(frozen=True)
class CorrespondenceResult:
    relationship_type: str
    confidence: float
    method: str
    changes: tuple[str, ...] = ()


class RequirementComparator:
    def compare(
        self,
        old: RequirementStructure,
        new: RequirementStructure,
    ) -> CorrespondenceResult:
        comparisons = {
            "actor": compare_entity_ref(
                old.actor,
                new.actor,
            ),
            "modality": self._compare_modality(
                old.modality,
                new.modality,
            ),
            "action": self._compare_text(
                old.action,
                new.action,
            ),
            "object": compare_entity_ref(
                old.object,
                new.object,
            ),
            "deadline": compare_optional_duration(
                old.deadline,
                new.deadline,
            ),
        }

        return self._build_result(comparisons)

    @staticmethod
    def _compare_modality(
        old: str,
        new: str,
    ) -> FieldComparison:
        if old == new:
            return FieldComparison(
                changed=False,
                kind=ComparisonKind.SAME,
                reason="SAME_MODALITY",
            )

        return FieldComparison(
            changed=True,
            kind=ComparisonKind.VALUE_CHANGED,
            reason=f"MODALITY_CHANGED: {old} -> {new}",
        )

    @staticmethod
    def _compare_text(
        old: str,
        new: str,
    ) -> FieldComparison:
        old_normalized = " ".join(old.lower().split())
        new_normalized = " ".join(new.lower().split())

        if old_normalized == new_normalized:
            return FieldComparison(
                changed=False,
                kind=ComparisonKind.SAME,
                reason="SAME_NORMALIZED_TEXT",
            )

        return FieldComparison(
            changed=True,
            kind=ComparisonKind.VALUE_CHANGED,
            reason=f"TEXT_CHANGED: {old} -> {new}",
        )

    @staticmethod
    def _build_result(
        comparisons: dict[str, FieldComparison],
    ) -> CorrespondenceResult:
        if any(
            comparison.kind == ComparisonKind.UNKNOWN
            for comparison in comparisons.values()
        ):
            return CorrespondenceResult(
                relationship_type="UNKNOWN",
                confidence=0.0,
                method="REQUIREMENT_STRUCTURE",
            )

        changes = tuple(
            comparison.reason
            for comparison in comparisons.values()
            if comparison.changed
        )

        if not changes:
            return CorrespondenceResult(
                relationship_type="SAME",
                confidence=1.0,
                method="REQUIREMENT_STRUCTURE",
            )

        return CorrespondenceResult(
            relationship_type="MODIFIED",
            confidence=1.0,
            method="REQUIREMENT_STRUCTURE",
            changes=changes,
        )


def compare_requirements(
    old: RequirementStructure,
    new: RequirementStructure,
) -> CorrespondenceResult:
    """Convenience function for comparing two requirements."""
    return RequirementComparator().compare(old, new)
