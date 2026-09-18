from decimal import Decimal
from uuid import uuid4

from src.services.claim_structure import (
    Duration,
    EntityRef,
    RequirementStructure,
)
from src.services.requirement_comparison import (
    compare_requirements,
)


def entity(
    raw_text: str,
    entity_id=None,
) -> EntityRef:
    return EntityRef(
        entity_id=entity_id,
        raw_text=raw_text,
    )


def duration(
    value: str,
    unit: str,
) -> Duration:
    return Duration(
        value=Decimal(value),
        unit=unit,
    )


def requirement(
    *,
    actor: EntityRef | None,
    modality: str,
    action: str,
    object: EntityRef | None,
    deadline: Duration | None,
) -> RequirementStructure:
    return RequirementStructure(
        actor=actor,
        modality=modality,
        action=action,
        object=object,
        deadline=deadline,
    )


def test_identical_requirements_are_same():
    actor_id = uuid4()
    object_id = uuid4()

    old = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=duration("30", "days"),
    )

    new = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=duration("30", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "SAME"
    assert result.confidence == 1.0
    assert result.method == "REQUIREMENT_STRUCTURE"


def test_changed_deadline_is_modified():
    actor_id = uuid4()
    object_id = uuid4()

    old = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=duration("30", "days"),
    )

    new = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=duration("45", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "MODIFIED"


def test_changed_action_is_modified():
    actor_id = uuid4()
    object_id = uuid4()

    old = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=duration("30", "days"),
    )

    new = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="file",
        object=entity("Form X", object_id),
        deadline=duration("30", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "MODIFIED"


def test_changed_object_is_modified():
    actor_id = uuid4()

    old = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X"),
        deadline=duration("30", "days"),
    )

    new = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="submit",
        object=entity("Form Y"),
        deadline=duration("30", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "MODIFIED"


def test_changed_actor_is_modified():
    object_id = uuid4()

    old = requirement(
        actor=entity("importers"),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=duration("30", "days"),
    )

    new = requirement(
        actor=entity("licensed importers"),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=duration("30", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "MODIFIED"


def test_changed_modality_is_modified():
    actor_id = uuid4()
    object_id = uuid4()

    old = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=duration("30", "days"),
    )

    new = requirement(
        actor=entity("importers", actor_id),
        modality="PERMITTED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=duration("30", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "MODIFIED"


def test_unknown_deadline_comparison_requires_review():
    actor_id = uuid4()
    object_id = uuid4()

    old = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=duration("1", "months"),
    )

    new = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=duration("30", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "UNKNOWN"


def test_added_deadline_is_modified():
    actor_id = uuid4()
    object_id = uuid4()

    old = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=None,
    )

    new = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=duration("30", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "MODIFIED"


def test_removed_deadline_is_modified():
    actor_id = uuid4()
    object_id = uuid4()

    old = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=duration("30", "days"),
    )

    new = requirement(
        actor=entity("importers", actor_id),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X", object_id),
        deadline=None,
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "MODIFIED"