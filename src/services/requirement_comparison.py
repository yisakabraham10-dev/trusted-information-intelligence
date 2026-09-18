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


class RequirementComparator:
    """
    Compare two RequirementStructure objects.

    This comparator operates at the semantic-structure level.
    Primitive comparison functions determine what changed in
    individual fields; this class determines what those field
    differences mean for claim correspondence.
    """

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
        # Any primitive comparison that is genuinely unknown means
        # that we cannot safely establish semantic correspondence.
        if any(
            comparison.kind == ComparisonKind.UNKNOWN
            for comparison in comparisons.values()
        ):
            return CorrespondenceResult(
                relationship_type="UNKNOWN",
                confidence=0.0,
                method="REQUIREMENT_STRUCTURE",
            )

        # No semantic field changed.
        if all(
            not comparison.changed
            for comparison in comparisons.values()
        ):
            return CorrespondenceResult(
                relationship_type="SAME",
                confidence=1.0,
                method="REQUIREMENT_STRUCTURE",
            )

        # At least one field changed and all changes are understood.
        return CorrespondenceResult(
            relationship_type="MODIFIED",
            confidence=1.0,
            method="REQUIREMENT_STRUCTURE",
        )


def compare_requirements(
    old: RequirementStructure,
    new: RequirementStructure,
) -> CorrespondenceResult:
    """Convenience function for comparing two requirements."""

    return RequirementComparator().compare(old, new)