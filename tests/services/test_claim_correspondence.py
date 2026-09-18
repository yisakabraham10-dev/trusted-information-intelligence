from decimal import Decimal
from uuid import uuid4

from src.models.claim import Claim
from src.services.claim_correspondence import CorrespondenceEvaluator
from src.services.claim_structure import (
    Duration,
    EntityRef,
    RequirementStructure,
)


def entity(raw_text: str) -> EntityRef:
    return EntityRef(
        entity_id=None,
        raw_text=raw_text,
    )


def duration(value: str, unit: str) -> Duration:
    return Duration(
        value=Decimal(value),
        unit=unit,
    )


def requirement(
    *,
    actor: str,
    modality: str,
    action: str,
    object: str,
    deadline: Duration | None,
) -> RequirementStructure:
    return RequirementStructure(
        actor=entity(actor),
        modality=modality,
        action=action,
        object=entity(object),
        deadline=deadline,
    )


def claim(
    *,
    text: str,
    claim_type: str = "REQUIREMENT",
) -> Claim:
    return Claim(
        id=uuid4(),
        section_id=uuid4(),
        claim_type=claim_type,
        text=text,
        normalized_text=None,
        effective_from=None,
        effective_to=None,
        status="ACTIVE",
    )


def test_requirement_claims_use_structured_comparison():
    old_claim = claim(
        text="Importers must submit Form X within 30 days."
    )
    new_claim = claim(
        text="Importers must submit Form X within 45 days."
    )

    old_structure = requirement(
        actor="importer",
        modality="REQUIRED",
        action="submit",
        object="Form X",
        deadline=duration("30", "days"),
    )

    new_structure = requirement(
        actor="importer",
        modality="REQUIRED",
        action="submit",
        object="Form X",
        deadline=duration("45", "days"),
    )

    result = CorrespondenceEvaluator().evaluate(
        old_claim,
        new_claim,
        old_structure=old_structure,
        new_structure=new_structure,
    )

    assert result.relationship_type == "MODIFIED"
    assert result.method == "REQUIREMENT_STRUCTURE"


def test_identical_requirement_structures_are_same():
    old_claim = claim(
        text="Importers must submit Form X within 30 days."
    )
    new_claim = claim(
        text="Importers must submit Form X within 30 days."
    )

    structure = requirement(
        actor="importer",
        modality="REQUIRED",
        action="submit",
        object="Form X",
        deadline=duration("30", "days"),
    )

    result = CorrespondenceEvaluator().evaluate(
        old_claim,
        new_claim,
        old_structure=structure,
        new_structure=structure,
    )

    assert result.relationship_type == "SAME"
    assert result.confidence == 1.0
    assert result.method == "REQUIREMENT_STRUCTURE"


def test_missing_structure_falls_back_to_text_comparison():
    old_claim = claim(
        text="Importers must submit Form X."
    )
    new_claim = claim(
        text="Importers must submit Form X."
    )

    result = CorrespondenceEvaluator().evaluate(
        old_claim,
        new_claim,
    )

    assert result.relationship_type == "SAME"
    assert result.confidence == 1.0
    assert result.method == "EXACT_NORMALIZED"


def test_missing_structure_does_not_break_existing_behavior():
    old_claim = claim(
        text="Importers must submit Form X."
    )
    new_claim = claim(
        text="Importers must submit Form Y."
    )

    result = CorrespondenceEvaluator().evaluate(
        old_claim,
        new_claim,
    )

    assert result.relationship_type == "UNRELATED"
    assert result.confidence == 0.0
    assert result.method == "EXACT_NORMALIZED"


def test_incompatible_claim_types_still_return_unrelated():
    old_claim = claim(
        text="Importers must submit Form X.",
        claim_type="REQUIREMENT",
    )
    new_claim = claim(
        text="Importers may submit Form X.",
        claim_type="PERMISSION",
    )

    result = CorrespondenceEvaluator().evaluate(
        old_claim,
        new_claim,
    )

    assert result.relationship_type == "UNRELATED"
    assert result.method == "CLAIM_TYPE_INCOMPATIBLE"