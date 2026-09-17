from src.services.claim_structure import ClaimStructure


def test_claim_structure_can_represent_a_requirement():
    structure = ClaimStructure(
        subject="importers",
        predicate="must submit",
        object="form x",
        constraints=("within 30 days",),
    )

    assert structure.subject == "importers"
    assert structure.predicate == "must submit"
    assert structure.object == "form x"
    assert structure.constraints == ("within 30 days",)

