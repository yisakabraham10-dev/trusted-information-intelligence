import uuid

from src.models.claim import Claim
from src.services.claim_correspondence import CorrespondenceEvaluator


def make_claim(
    text: str,
    normalized_text: str | None = None,
    claim_type: str = "REQUIREMENT",
) -> Claim:
    return Claim(
        section_id=uuid.uuid4(),
        claim_type=claim_type,
        text=text,
        normalized_text=normalized_text,
    )


def test_identical_claims_are_same():
    evaluator = CorrespondenceEvaluator()

    old_claim = make_claim(
        "Importers must submit the form.",
    )
    new_claim = make_claim(
        "Importers must submit the form.",
    )

    result = evaluator.evaluate(old_claim, new_claim)

    assert result.relationship_type == "SAME"
    assert result.confidence == 1.0
    assert result.method == "EXACT_NORMALIZED"


def test_whitespace_and_case_are_ignored():
    evaluator = CorrespondenceEvaluator()

    old_claim = make_claim(
        "Importers must submit the form.",
    )
    new_claim = make_claim(
        "  IMPORTERS   MUST submit the form. ",
    )

    result = evaluator.evaluate(old_claim, new_claim)

    assert result.relationship_type == "SAME"


def test_different_claims_are_currently_unrelated():
    evaluator = CorrespondenceEvaluator()

    old_claim = make_claim(
        "Importers must submit the form.",
    )
    new_claim = make_claim(
        "Exporters must submit the form.",
    )

    result = evaluator.evaluate(old_claim, new_claim)

    assert result.relationship_type == "UNRELATED"


def test_existing_normalized_text_is_used():
    evaluator = CorrespondenceEvaluator()

    old_claim = make_claim(
        "Importers must submit the FORM.",
        normalized_text="importers must submit the form.",
    )
    new_claim = make_claim(
        "Importers must submit the form.",
        normalized_text="importers must submit the form.",
    )

    result = evaluator.evaluate(old_claim, new_claim)

    assert result.relationship_type == "SAME"
