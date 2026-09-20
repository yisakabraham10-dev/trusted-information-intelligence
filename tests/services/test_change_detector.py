import pytest

from src.services.change_detector import ChangeDetector
from src.services.claim_correspondence import CorrespondenceResult


def correspondence(
    relationship_type: str,
    confidence: float = 1.0,
    method: str = "TEST",
) -> CorrespondenceResult:
    return CorrespondenceResult(
        relationship_type=relationship_type,
        confidence=confidence,
        method=method,
    )


def test_modified_correspondence_produces_modified_change():
    result = ChangeDetector().detect(
        correspondence("MODIFIED")
    )

    assert result is not None
    assert result.change_type == "MODIFIED"
    assert result.summary == "An existing claim was modified."


def test_same_correspondence_produces_no_change():
    result = ChangeDetector().detect(
        correspondence("SAME")
    )

    assert result is None


def test_missing_old_claim_produces_added_change():
    result = ChangeDetector().detect(
        correspondence("UNRELATED"),
        old_claim_exists=False,
        new_claim_exists=True,
    )

    assert result is not None
    assert result.change_type == "ADDED"
    assert result.summary == "A new claim was added."


def test_missing_new_claim_produces_removed_change():
    result = ChangeDetector().detect(
        correspondence("UNRELATED"),
        old_claim_exists=True,
        new_claim_exists=False,
    )

    assert result is not None
    assert result.change_type == "REMOVED"
    assert result.summary == "An existing claim was removed."


def test_unrelated_correspondence_produces_no_change():
    result = ChangeDetector().detect(
        correspondence("UNRELATED")
    )

    assert result is None


def test_possible_conflict_does_not_create_change_yet():
    result = ChangeDetector().detect(
        correspondence("POSSIBLE_CONFLICT")
    )

    assert result is None


def test_both_claims_missing_is_invalid():
    with pytest.raises(ValueError):
        ChangeDetector().detect(
            correspondence("UNRELATED"),
            old_claim_exists=False,
            new_claim_exists=False,
        )

def test_unknown_correspondence_requires_review():
    result = ChangeDetector().detect(
        correspondence("UNKNOWN", confidence=0.0)
    )

    assert result is not None
    assert result.change_type == "REQUIRES_REVIEW"
    assert result.summary == (
        "The system could not reliably determine whether "
        "the claims correspond."
    )
