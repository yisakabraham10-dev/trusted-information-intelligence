from decimal import Decimal
from unittest.mock import MagicMock, patch

from src.config import Settings
from src.services.claim_extraction_schema import (
    ClaimExtractionSchema,
    DurationSchema,
    EntityRefSchema,
    RequirementStructureSchema,
)
from src.services.document_structure import ParsedSection
from src.services.groq_claim_extraction import GroqClaimExtractionProvider


def _build_section() -> ParsedSection:
    return ParsedSection(
        section_number="51(1)",
        title="Removal of goods from temporary customs storage",
        section_type="subsection",
        page_start=1,
        page_end=1,
        raw_text=(
            "Goods transported by sea or land shall be removed "
            "within forty-five days."
        ),
    )


def _build_structured_output() -> ClaimExtractionSchema:
    return ClaimExtractionSchema(
        claim_type="REQUIREMENT",
        text=(
            "Goods transported by sea or land shall be removed "
            "within forty-five days."
        ),
        section_number="51(1)",
        structure_type="REQUIREMENT",
        requirement=RequirementStructureSchema(
            actor=None,
            modality="REQUIRED",
            action="remove",
            object=EntityRefSchema(
                raw_text="Goods transported by sea or land"
            ),
            deadline=DurationSchema(
                value=Decimal("45"),
                unit="DAYS",
            ),
            applicability_conditions=[],
        ),
        fee=None,
        definition=None,
        applicability=None,
        exception=None,
        penalty=None,
    )


def _build_fake_response(structured_output: ClaimExtractionSchema) -> MagicMock:
    fake_response = MagicMock()
    fake_response.choices = [
        MagicMock(
            message=MagicMock(
                content=structured_output.model_dump_json()
            )
        )
    ]
    return fake_response


def test_groq_claim_extraction_returns_converted_candidate():
    section = _build_section()
    structured_output = _build_structured_output()
    fake_response = _build_fake_response(structured_output)

    settings = Settings()

    with patch("src.services.groq_claim_extraction.Groq") as mock_groq:
        mock_client = mock_groq.return_value
        mock_client.chat.completions.create.return_value = fake_response

        provider = GroqClaimExtractionProvider(settings)

        candidates = provider.extract(section)

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate.claim_type == "REQUIREMENT"

    assert candidate.text == (
        "Goods transported by sea or land shall be removed "
        "within forty-five days."
    )

    assert candidate.section_number == "51(1)"

    assert candidate.structure.modality == "REQUIRED"
    assert candidate.structure.action == "remove"

    assert candidate.structure.object is not None
    assert (
        candidate.structure.object.raw_text
        == "Goods transported by sea or land"
    )

    assert candidate.structure.deadline is not None
    assert candidate.structure.deadline.value == Decimal("45")
    assert candidate.structure.deadline.unit == "DAYS"


def test_groq_claim_extraction_uses_expected_model_and_prompt():
    section = _build_section()
    structured_output = _build_structured_output()
    fake_response = _build_fake_response(structured_output)

    settings = Settings()

    with patch("src.services.groq_claim_extraction.Groq") as mock_groq:
        mock_client = mock_groq.return_value
        mock_client.chat.completions.create.return_value = fake_response

        provider = GroqClaimExtractionProvider(settings)

        provider.extract(section)

        mock_client.chat.completions.create.assert_called_once()

        call_kwargs = (
            mock_client.chat.completions.create.call_args.kwargs
        )

    assert call_kwargs["model"] == "openai/gpt-oss-120b"

    messages = call_kwargs["messages"]

    user_message = next(
        message
        for message in messages
        if message["role"] == "user"
    )

    assert "forty-five days" in user_message["content"]
    assert "51(1)" in user_message["content"]


def test_groq_response_schema_adds_strict_object_requirements():
    schema = GroqClaimExtractionProvider._groq_response_schema()

    def inspect_schema(value):
        if isinstance(value, dict):
            if value.get("type") == "object":
                assert value["additionalProperties"] is False

                properties = value.get("properties", {})

                if properties:
                    assert set(value["required"]) == set(properties)

            for child in value.values():
                inspect_schema(child)

        elif isinstance(value, list):
            for item in value:
                inspect_schema(item)

    inspect_schema(schema)


def test_groq_response_schema_removes_unsupported_patterns():
    schema = GroqClaimExtractionProvider._groq_response_schema()

    def inspect_schema(value):
        if isinstance(value, dict):
            assert "pattern" not in value

            for child in value.values():
                inspect_schema(child)

        elif isinstance(value, list):
            for item in value:
                inspect_schema(item)

    inspect_schema(schema)