from decimal import Decimal
from uuid import uuid4

from src.services.claim_structure import Duration, EntityRef, Quantity
from src.services.primitive_comparison import (
    ComparisonKind,
    compare_duration,
    compare_entity_ref,
    compare_optional_duration,
    compare_optional_quantity,
    compare_quantity,
)


def quantity(value: str, unit: str) -> Quantity:
    return Quantity(
        value=Decimal(value),
        unit=unit,
    )


def duration(value: str, unit: str) -> Duration:
    return Duration(
        value=Decimal(value),
        unit=unit,
    )


def test_same_entity_reference():
    entity_id = uuid4()

    old = EntityRef(
        entity_id=entity_id,
        raw_text="importers",
    )

    new = EntityRef(
        entity_id=entity_id,
        raw_text="licensed importers",
    )

    result = compare_entity_ref(old, new)

    assert result.changed is False
    assert result.kind == ComparisonKind.SAME
    assert result.reason == "SAME_ENTITY"


def test_changed_entity_reference():
    old = EntityRef(
        entity_id=uuid4(),
        raw_text="importers",
    )

    new = EntityRef(
        entity_id=uuid4(),
        raw_text="exporters",
    )

    result = compare_entity_ref(old, new)

    assert result.changed is True
    assert result.kind == ComparisonKind.VALUE_CHANGED
    assert result.reason == "ENTITY_CHANGED"


def test_entity_reference_falls_back_to_text():
    old = EntityRef(
        entity_id=None,
        raw_text="Importers",
    )

    new = EntityRef(
        entity_id=None,
        raw_text="  importers  ",
    )

    result = compare_entity_ref(old, new)

    assert result.changed is False
    assert result.kind == ComparisonKind.SAME


def test_entity_reference_presence_changed():
    old = None

    new = EntityRef(
        entity_id=uuid4(),
        raw_text="importers",
    )

    result = compare_entity_ref(old, new)

    assert result.changed is True
    assert result.kind == ComparisonKind.PRESENCE_CHANGED


def test_same_quantity():
    result = compare_quantity(
        quantity("35", "%"),
        quantity("35", "%"),
    )

    assert result.changed is False
    assert result.kind == ComparisonKind.SAME


def test_value_changed():
    result = compare_quantity(
        quantity("35", "%"),
        quantity("40", "%"),
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.VALUE_CHANGED


def test_dimension_changed():
    result = compare_quantity(
        quantity("35", "%"),
        quantity("35", "ETB"),
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.DIMENSION_CHANGED


def test_equivalent_mass_with_different_units():
    result = compare_quantity(
        quantity("1", "kg"),
        quantity("1000", "g"),
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.UNIT_CHANGED


def test_different_mass_value():
    result = compare_quantity(
        quantity("1", "kg"),
        quantity("900", "g"),
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.VALUE_CHANGED


def test_unknown_currency_conversion():
    result = compare_quantity(
        quantity("35", "USD"),
        quantity("35", "ETB"),
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.UNKNOWN


def test_unrecognized_unit():
    result = compare_quantity(
        quantity("1", "widgets"),
        quantity("1", "kg"),
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.UNKNOWN


def test_optional_quantity_both_absent():
    result = compare_optional_quantity(None, None)

    assert result.changed is False
    assert result.kind == ComparisonKind.SAME


def test_optional_quantity_added():
    result = compare_optional_quantity(
        None,
        quantity("30", "kg"),
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.PRESENCE_CHANGED


def test_optional_quantity_removed():
    result = compare_optional_quantity(
        quantity("30", "kg"),
        None,
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.PRESENCE_CHANGED


def test_same_duration():
    result = compare_duration(
        duration("30", "days"),
        duration("30", "days"),
    )

    assert result.changed is False
    assert result.kind == ComparisonKind.SAME


def test_changed_duration_value():
    result = compare_duration(
        duration("30", "days"),
        duration("45", "days"),
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.VALUE_CHANGED


def test_equivalent_duration_units():
    result = compare_duration(
        duration("1", "days"),
        duration("24", "hours"),
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.UNIT_CHANGED


def test_unknown_month_to_day_conversion():
    result = compare_duration(
        duration("1", "months"),
        duration("30", "days"),
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.UNKNOWN


def test_unknown_year_to_month_conversion():
    result = compare_duration(
        duration("1", "years"),
        duration("12", "months"),
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.UNKNOWN


def test_unrecognized_duration_unit():
    result = compare_duration(
        duration("10", "fortnights"),
        duration("10", "days"),
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.UNKNOWN


def test_optional_duration_both_absent():
    result = compare_optional_duration(None, None)

    assert result.changed is False
    assert result.kind == ComparisonKind.SAME


def test_optional_duration_added():
    result = compare_optional_duration(
        None,
        duration("30", "days"),
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.PRESENCE_CHANGED


def test_optional_duration_removed():
    result = compare_optional_duration(
        duration("30", "days"),
        None,
    )

    assert result.changed is True
    assert result.kind == ComparisonKind.PRESENCE_CHANGED