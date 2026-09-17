from dataclasses import dataclass

from src.services.claim_structure import EntityRef


@dataclass(frozen=True)
class FieldComparison:
    changed: bool
    reason: str


def compare_entity_ref(
    old: EntityRef | None,
    new: EntityRef | None,
) -> FieldComparison:
    if old is None and new is None:
        return FieldComparison(
            changed=False,
            reason="BOTH_ABSENT",
        )

    if old is None or new is None:
        return FieldComparison(
            changed=True,
            reason="PRESENCE_CHANGED",
        )

    if old.entity_id is not None and new.entity_id is not None:
        return FieldComparison(
            changed=old.entity_id != new.entity_id,
            reason=(
                "ENTITY_CHANGED"
                if old.entity_id != new.entity_id
                else "SAME_ENTITY"
            ),
        )

    old_text = " ".join(old.raw_text.lower().split())
    new_text = " ".join(new.raw_text.lower().split())

    return FieldComparison(
        changed=old_text != new_text,
        reason=(
            "TEXT_CHANGED"
            if old_text != new_text
            else "SAME_NORMALIZED_TEXT"
        ),
    )