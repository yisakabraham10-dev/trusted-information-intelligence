from decimal import Decimal
import uuid

from src.services.claim_structure import (
    ApplicabilityStructure,
    Condition,
    DefinitionStructure,
    Duration,
    EntityRef,
    ExceptionStructure,
    FeeStructure,
    PenaltyStructure,
    Quantity,
    RequirementStructure,
)


def test_requirement_structure_can_represent_a_requirement():
    importer = EntityRef(
        entity_id=None,
        raw_text="importers",
    )

    form = EntityRef(
        entity_id=None,
        raw_text="form x",
    )

    structure = RequirementStructure(
        actor=importer,
        modality="REQUIRED",
        action="submit",
        object=form,
        deadline=Duration(
            value=Decimal("30"),
            unit="DAYS",
        ),
    )

    assert structure.actor == importer
    assert structure.modality == "REQUIRED"
    assert structure.action == "submit"
    assert structure.object == form
    assert structure.deadline.value == Decimal("30")
    assert structure.deadline.unit == "DAYS"


def test_fee_structure_can_represent_a_fee():
    importer = EntityRef(
        entity_id=None,
        raw_text="commercial importers",
    )

    structure = FeeStructure(
        subject=importer,
        attribute="customs duty",
        value=Quantity(
            value=Decimal("35"),
            unit="PERCENT",
        ),
    )

    assert structure.subject == importer
    assert structure.attribute == "customs duty"
    assert structure.value.value == Decimal("35")
    assert structure.value.unit == "PERCENT"


def test_definition_structure_can_represent_a_definition():
    structure = DefinitionStructure(
        term="importer",
        definition="a person or entity importing goods for commercial purposes",
    )

    assert structure.term == "importer"
    assert structure.definition == (
        "a person or entity importing goods for commercial purposes"
    )


def test_applicability_structure_can_represent_applicability():
    subject = EntityRef(
        entity_id=None,
        raw_text="commercial importers",
    )

    structure = ApplicabilityStructure(
        subject=subject,
        condition=Condition(
            raw_text="when importing goods for commercial purposes",
        ),
    )

    assert structure.subject == subject
    assert structure.condition.raw_text == (
        "when importing goods for commercial purposes"
    )


def test_exception_structure_can_represent_an_exception():
    claim_id = uuid.uuid4()

    structure = ExceptionStructure(
        modifies_claim_id=claim_id,
        condition=Condition(
            raw_text="unless the importer is exempt",
        ),
    )

    assert structure.modifies_claim_id == claim_id
    assert structure.condition.raw_text == "unless the importer is exempt"


def test_penalty_structure_can_represent_a_penalty():
    structure = PenaltyStructure(
        violation_description="failure to submit the required form",
        consequence=Quantity(
            value=Decimal("10000"),
            unit="ETB",
        ),
    )

    assert structure.violation_description == (
        "failure to submit the required form"
    )
    assert structure.consequence.value == Decimal("10000")
    assert structure.consequence.unit == "ETB"