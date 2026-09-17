from services.claim_correspondence import CorrespondenceEvaluator


def test_identical_claims_are_same():
    evaluator = CorrespondenceEvaluator()

    result = evaluator.evaluate(
        "Importers must submit the form.",
        "Importers must submit the form.",
    )

    assert result.relationship_type == "SAME"
    assert result.confidence == 1.0
    assert result.method == "EXACT_NORMALIZED"


def test_whitespace_and_case_are_ignored():
    evaluator = CorrespondenceEvaluator()

    result = evaluator.evaluate(
        "Importers must submit the form.",
        "  IMPORTERS   MUST submit the form. ",
    )

    assert result.relationship_type == "SAME"


def test_different_claims_are_currently_unrelated():
    evaluator = CorrespondenceEvaluator()

    result = evaluator.evaluate(
        "Importers must submit the form.",
        "Exporters must submit the form.",
    )

    assert result.relationship_type == "UNRELATED"
