from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from src.services.claim_structure import Duration, EntityRef, Quantity


class ComparisonKind(str, Enum):
    SAME = "SAME"
    VALUE_CHANGED = "VALUE_CHANGED"
    UNIT_CHANGED = "UNIT_CHANGED"
    DIMENSION_CHANGED = "DIMENSION_CHANGED"
    PRESENCE_CHANGED = "PRESENCE_CHANGED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class FieldComparison:
    changed: bool
    kind: ComparisonKind
    reason: str


@dataclass(frozen=True)
class UnitInfo:
    dimension: str
    factor: Decimal | None


# Units used by Quantity.
#
# The factor converts the unit into the canonical unit
# for its dimension.
#
# Example:
#   1 kg -> 1000 g
#
# Calendar durations such as months and years are intentionally
# NOT included here. They are handled by DURATION_UNIT_REGISTRY.
UNIT_REGISTRY: dict[str, UnitInfo] = {
    "": UnitInfo("count", Decimal("1")),
    "g": UnitInfo("mass", Decimal("1")),
    "kg": UnitInfo("mass", Decimal("1000")),
    "%": UnitInfo("percent", Decimal("1")),
    "ETB": UnitInfo("currency", None),
    "USD": UnitInfo("currency", None),
}


# Units used specifically by Duration.
#
# Fixed-duration units can safely be converted.
# Calendar units cannot safely be converted without a reference
# date, so their factor is intentionally None.
DURATION_UNIT_REGISTRY: dict[str, UnitInfo] = {
    "seconds": UnitInfo("duration", Decimal("1")),
    "minutes": UnitInfo("duration", Decimal("60")),
    "hours": UnitInfo("duration", Decimal("3600")),
    "days": UnitInfo("duration", Decimal("86400")),
    "weeks": UnitInfo("duration", Decimal("604800")),
    "months": UnitInfo("calendar_duration", None),
    "years": UnitInfo("calendar_duration", None),
}


def compare_entity_ref(
    old: EntityRef | None,
    new: EntityRef | None,
) -> FieldComparison:
    """Compare two entity references."""

    if old is None and new is None:
        return FieldComparison(
            changed=False,
            kind=ComparisonKind.SAME,
            reason="BOTH_ABSENT",
        )

    if old is None or new is None:
        return FieldComparison(
            changed=True,
            kind=ComparisonKind.PRESENCE_CHANGED,
            reason="PRESENCE_CHANGED",
        )

    # If both references resolve to known entities, compare their IDs.
    if old.entity_id is not None and new.entity_id is not None:
        return FieldComparison(
            changed=old.entity_id != new.entity_id,
            kind=(
                ComparisonKind.SAME
                if old.entity_id == new.entity_id
                else ComparisonKind.VALUE_CHANGED
            ),
            reason=(
                "SAME_ENTITY"
                if old.entity_id == new.entity_id
                else "ENTITY_CHANGED"
            ),
        )

    # Otherwise compare the extracted raw text conservatively.
    old_text = " ".join(old.raw_text.lower().split())
    new_text = " ".join(new.raw_text.lower().split())

    return FieldComparison(
        changed=old_text != new_text,
        kind=(
            ComparisonKind.SAME
            if old_text == new_text
            else ComparisonKind.VALUE_CHANGED
        ),
        reason=(
            "SAME_NORMALIZED_TEXT"
            if old_text == new_text
            else "TEXT_CHANGED"
        ),
    )


def compare_quantity(
    old: Quantity,
    new: Quantity,
) -> FieldComparison:
    """Compare two quantities without making unsafe conversions."""

    # Same unit: direct numeric comparison.
    if old.unit == new.unit:
        if old.value == new.value:
            return FieldComparison(
                changed=False,
                kind=ComparisonKind.SAME,
                reason="IDENTICAL_VALUE_AND_UNIT",
            )

        return FieldComparison(
            changed=True,
            kind=ComparisonKind.VALUE_CHANGED,
            reason=(
                f"VALUE_CHANGED: "
                f"{old.value} {old.unit} -> "
                f"{new.value} {new.unit}"
            ),
        )

    old_info = UNIT_REGISTRY.get(old.unit)
    new_info = UNIT_REGISTRY.get(new.unit)

    # We do not know one or both units.
    if old_info is None or new_info is None:
        return FieldComparison(
            changed=True,
            kind=ComparisonKind.UNKNOWN,
            reason=(
                f"UNRECOGNIZED_UNIT: "
                f"{old.unit!r} or {new.unit!r}"
            ),
        )

    # Different dimensions cannot represent the same quantity.
    if old_info.dimension != new_info.dimension:
        return FieldComparison(
            changed=True,
            kind=ComparisonKind.DIMENSION_CHANGED,
            reason=(
                f"DIMENSION_CHANGED: "
                f"{old.unit} ({old_info.dimension}) -> "
                f"{new.unit} ({new_info.dimension})"
            ),
        )

    # Same dimension, but conversion is not safely defined.
    if old_info.factor is None or new_info.factor is None:
        return FieldComparison(
            changed=True,
            kind=ComparisonKind.UNKNOWN,
            reason=(
                f"NO_FIXED_CONVERSION: "
                f"{old.unit} -> {new.unit}"
            ),
        )

    old_canonical = old.value * old_info.factor
    new_canonical = new.value * new_info.factor

    # Different representation, same semantic quantity.
    if old_canonical == new_canonical:
        return FieldComparison(
            changed=True,
            kind=ComparisonKind.UNIT_CHANGED,
            reason=(
                f"EQUIVALENT_UNITS: "
                f"{old.value} {old.unit} = "
                f"{new.value} {new.unit}"
            ),
        )

    return FieldComparison(
        changed=True,
        kind=ComparisonKind.VALUE_CHANGED,
        reason=(
            f"VALUE_CHANGED: "
            f"{old.value} {old.unit} -> "
            f"{new.value} {new.unit}"
        ),
    )


def compare_optional_quantity(
    old: Quantity | None,
    new: Quantity | None,
) -> FieldComparison:
    """Compare quantities where either side may be absent."""

    if old is None and new is None:
        return FieldComparison(
            changed=False,
            kind=ComparisonKind.SAME,
            reason="BOTH_ABSENT",
        )

    if old is None or new is None:
        return FieldComparison(
            changed=True,
            kind=ComparisonKind.PRESENCE_CHANGED,
            reason="PRESENCE_CHANGED",
        )

    return compare_quantity(old, new)


def compare_duration(
    old: Duration,
    new: Duration,
) -> FieldComparison:
    """Compare two durations using only safe fixed conversions."""

    # Same unit: direct numeric comparison.
    if old.unit == new.unit:
        if old.value == new.value:
            return FieldComparison(
                changed=False,
                kind=ComparisonKind.SAME,
                reason="IDENTICAL_VALUE_AND_UNIT",
            )

        return FieldComparison(
            changed=True,
            kind=ComparisonKind.VALUE_CHANGED,
            reason=(
                f"VALUE_CHANGED: "
                f"{old.value} {old.unit} -> "
                f"{new.value} {new.unit}"
            ),
        )

    old_info = DURATION_UNIT_REGISTRY.get(old.unit)
    new_info = DURATION_UNIT_REGISTRY.get(new.unit)

    # We do not know one or both duration units.
    if old_info is None or new_info is None:
        return FieldComparison(
            changed=True,
            kind=ComparisonKind.UNKNOWN,
            reason=(
                f"UNRECOGNIZED_DURATION_UNIT: "
                f"{old.unit!r} or {new.unit!r}"
            ),
        )

    # Months and years deliberately have no fixed conversion factor.
    #
    # Therefore:
    #   1 month != automatically 30 days
    #   1 year != automatically 365 days
    if old_info.factor is None or new_info.factor is None:
        return FieldComparison(
            changed=True,
            kind=ComparisonKind.UNKNOWN,
            reason=(
                f"NO_FIXED_CONVERSION: "
                f"{old.unit} -> {new.unit}"
            ),
        )

    old_canonical = old.value * old_info.factor
    new_canonical = new.value * new_info.factor

    # Different units, same actual duration.
    if old_canonical == new_canonical:
        return FieldComparison(
            changed=True,
            kind=ComparisonKind.UNIT_CHANGED,
            reason=(
                f"EQUIVALENT_DURATION_UNITS: "
                f"{old.value} {old.unit} = "
                f"{new.value} {new.unit}"
            ),
        )

    return FieldComparison(
        changed=True,
        kind=ComparisonKind.VALUE_CHANGED,
        reason=(
            f"VALUE_CHANGED: "
            f"{old.value} {old.unit} -> "
            f"{new.value} {new.unit}"
        ),
    )


def compare_optional_duration(
    old: Duration | None,
    new: Duration | None,
) -> FieldComparison:
    """Compare durations where either side may be absent."""

    if old is None and new is None:
        return FieldComparison(
            changed=False,
            kind=ComparisonKind.SAME,
            reason="BOTH_ABSENT",
        )

    if old is None or new is None:
        return FieldComparison(
            changed=True,
            kind=ComparisonKind.PRESENCE_CHANGED,
            reason="PRESENCE_CHANGED",
        )

    return compare_duration(old, new)