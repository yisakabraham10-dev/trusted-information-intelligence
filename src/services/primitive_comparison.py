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


UNIT_REGISTRY: dict[str, UnitInfo] = {
    "": UnitInfo("count", Decimal("1")),
    "g": UnitInfo("mass", Decimal("1")),
    "kg": UnitInfo("mass", Decimal("1000")),
    "days": UnitInfo("duration", Decimal("1")),
    "months": UnitInfo("duration", None),
    "years": UnitInfo("duration", Decimal("365")),
    "%": UnitInfo("percent", Decimal("1")),
    "ETB": UnitInfo("currency", None),
    "USD": UnitInfo("currency", None),
}


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
                f"{old.value}{old.unit} -> {new.value}{new.unit}"
            ),
        )

    old_info = UNIT_REGISTRY.get(old.unit)
    new_info = UNIT_REGISTRY.get(new.unit)

    if old_info is None or new_info is None:
        return FieldComparison(
            changed=True,
            kind=ComparisonKind.UNKNOWN,
            reason=(
                f"UNRECOGNIZED_UNIT: "
                f"{old.unit!r} or {new.unit!r}"
            ),
        )

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

    if old_canonical == new_canonical:
        return FieldComparison(
            changed=True,
            kind=ComparisonKind.UNIT_CHANGED,
            reason=(
                f"EQUIVALENT_UNITS: "
                f"{old.value}{old.unit} = "
                f"{new.value}{new.unit}"
            ),
        )

    return FieldComparison(
        changed=True,
        kind=ComparisonKind.VALUE_CHANGED,
        reason=(
            f"VALUE_CHANGED: "
            f"{old.value}{old.unit} -> {new.value}{new.unit}"
        ),
    )


def compare_optional_quantity(
    old: Quantity | None,
    new: Quantity | None,
) -> FieldComparison:
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
                f"{old.value}{old.unit} -> {new.value}{new.unit}"
            ),
        )

    old_info = DURATION_UNIT_REGISTRY.get(old.unit)
    new_info = DURATION_UNIT_REGISTRY.get(new.unit)

    if old_info is None or new_info is None:
        return FieldComparison(
            changed=True,
            kind=ComparisonKind.UNKNOWN,
            reason=(
                f"UNRECOGNIZED_DURATION_UNIT: "
                f"{old.unit!r} or {new.unit!r}"
            ),
        )

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

    if old_canonical == new_canonical:
        return FieldComparison(
            changed=True,
            kind=ComparisonKind.UNIT_CHANGED,
            reason=(
                f"EQUIVALENT_DURATION_UNITS: "
                f"{old.value}{old.unit} = "
                f"{new.value}{new.unit}"
            ),
        )

    return FieldComparison(
        changed=True,
        kind=ComparisonKind.VALUE_CHANGED,
        reason=(
            f"VALUE_CHANGED: "
            f"{old.value}{old.unit} -> {new.value}{new.unit}"
        ),
    )


def compare_optional_duration(
    old: Duration | None,
    new: Duration | None,
) -> FieldComparison:
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