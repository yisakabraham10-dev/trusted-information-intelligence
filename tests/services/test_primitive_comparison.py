import uuid

from src.services.claim_structure import EntityRef
from src.services.primitive_comparison import compare_entity_ref


def test_both_missing_entities_are_unchanged():
    result = compare_entity_ref(None, None)

    assert result.changed is False
    assert result.reason == "BOTH_ABSENT"


def test_missing_entity_is_a_change():
    entity = EntityRef(
        entity_id=None,
        raw_text="importers",
    )

    result = compare_entity_ref(None, entity)

    assert result.changed is True
    assert result.reason == "PRESENCE_CHANGED"


def test_same_canonical_entity_is_unchanged():
    entity_id = uuid.uuid4()

    old = EntityRef(
        entity_id=entity_id,
        raw_text="importers",
    )

    new = EntityRef(
        entity_id=entity_id,
        raw_text="commercial importers",
    )

    result = compare_entity_ref(old, new)

    assert result.changed is False
    assert result.reason == "SAME_ENTITY"


def test_different_canonical_entities_are_changed():
    old = EntityRef(
        entity_id=uuid.uuid4(),
        raw_text="importers",
    )

    new = EntityRef(
        entity_id=uuid.uuid4(),
        raw_text="exporters",
    )

    result = compare_entity_ref(old, new)

    assert result.changed is True
    assert result.reason == "ENTITY_CHANGED"


def test_normalized_text_is_used_when_canonical_entities_are_missing():
    old = EntityRef(
        entity_id=None,
        raw_text="  Commercial   Importers ",
    )

    new = EntityRef(
        entity_id=None,
        raw_text="commercial importers",
    )

    result = compare_entity_ref(old, new)

    assert result.changed is False
    assert result.reason == "SAME_NORMALIZED_TEXT"


def test_different_text_is_changed_when_entities_are_unresolved():
    old = EntityRef(
        entity_id=None,
        raw_text="commercial importers",
    )

    new = EntityRef(
        entity_id=None,
        raw_text="licensed importers",
    )

    result = compare_entity_ref(old, new)

    assert result.changed is True
    assert result.reason == "TEXT_CHANGED"