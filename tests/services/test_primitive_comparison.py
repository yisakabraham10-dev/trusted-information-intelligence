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


def entity(raw_text: str):
    return EntityRef(
        entity_id=uuid4(),
        raw_text=raw_text,
    )


def duration(value: str, unit: str):
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
):
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

    old = RequirementStructure(
        actor=EntityRef(actor_id, "importers"),
        modality="REQUIRED",
        action="submit",
        object=EntityRef(object_id, "Form X"),
        deadline=duration("30", "days"),
    )

    new = RequirementStructure(
        actor=EntityRef(actor_id, "importers"),
        modality="REQUIRED",
        action="submit",
        object=EntityRef(object_id, "Form X"),
        deadline=duration("30", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "SAME"


def test_changed_deadline_is_modified():
    actor = entity("importers")
    form = entity("Form X")

    old = requirement(
        actor=actor,
        modality="REQUIRED",
        action="submit",
        object=form,
        deadline=duration("30", "days"),
    )

    new = requirement(
        actor=actor,
        modality="REQUIRED",
        action="submit",
        object=form,
        deadline=duration("45", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "MODIFIED"


def test_changed_action_is_modified():
    actor = entity("importers")
    form = entity("Form X")

    old = requirement(
        actor=actor,
        modality="REQUIRED",
        action="submit",
        object=form,
        deadline=duration("30", "days"),
    )

    new = requirement(
        actor=actor,
        modality="REQUIRED",
        action="file",
        object=form,
        deadline=duration("30", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "MODIFIED"


def test_changed_object_is_modified():
    actor = entity("importers")

    old = requirement(
        actor=actor,
        modality="REQUIRED",
        action="submit",
        object=entity("Form X"),
        deadline=duration("30", "days"),
    )

    new = requirement(
        actor=actor,
        modality="REQUIRED",
        action="submit",
        object=entity("Form Y"),
        deadline=duration("30", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "MODIFIED"


def test_changed_actor_is_modified():
    old = requirement(
        actor=entity("importers"),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X"),
        deadline=duration("30", "days"),
    )

    new = requirement(
        actor=entity("licensed importers"),
        modality="REQUIRED",
        action="submit",
        object=entity("Form X"),
        deadline=duration("30", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "MODIFIED"


def test_changed_modality_is_modified():
    actor = entity("importers")
    form = entity("Form X")

    old = requirement(
        actor=actor,
        modality="REQUIRED",
        action="submit",
        object=form,
        deadline=duration("30", "days"),
    )

    new = requirement(
        actor=actor,
        modality="PERMITTED",
        action="submit",
        object=form,
        deadline=duration("30", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "MODIFIED"


def test_unknown_deadline_comparison_requires_review():
    actor_id = uuid4()
    object_id = uuid4()

    old = RequirementStructure(
        actor=EntityRef(actor_id, "importers"),
        modality="REQUIRED",
        action="submit",
        object=EntityRef(object_id, "Form X"),
        deadline=Duration(Decimal("1"), "months"),
    )

    new = RequirementStructure(
        actor=EntityRef(actor_id, "importers"),
        modality="REQUIRED",
        action="submit",
        object=EntityRef(object_id, "Form X"),
        deadline=Duration(Decimal("30"), "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "UNKNOWN"


def test_added_deadline_is_modified():
    actor = entity("importers")
    form = entity("Form X")

    old = requirement(
        actor=actor,
        modality="REQUIRED",
        action="submit",
        object=form,
        deadline=None,
    )

    new = requirement(
        actor=actor,
        modality="REQUIRED",
        action="submit",
        object=form,
        deadline=duration("30", "days"),
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "MODIFIED"


def test_removed_deadline_is_modified():
    actor = entity("importers")
    form = entity("Form X")

    old = requirement(
        actor=actor,
        modality="REQUIRED",
        action="submit",
        object=form,
        deadline=duration("30", "days"),
    )

    new = requirement(
        actor=actor,
        modality="REQUIRED",
        action="submit",
        object=form,
        deadline=None,
    )

    result = compare_requirements(old, new)

    assert result.relationship_type == "MODIFIED"