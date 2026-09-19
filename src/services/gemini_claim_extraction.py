from typing import Any

from google import genai
from google.genai import types

from src.config import Settings
from src.services.claim_extraction import (
    ClaimExtractionCandidate,
    ClaimExtractionProvider,
)
from src.services.claim_extraction_conversion import ClaimExtractionConverter
from src.services.claim_extraction_schema import ClaimExtractionSchema
from src.services.document_structure import ParsedSection


class GeminiClaimExtractionProvider(ClaimExtractionProvider):
    def __init__(
        self,
        settings: Settings,
        model: str = "gemini-3.6-flash",
    ):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = model
        self.converter = ClaimExtractionConverter()

    def extract(
        self,
        section: ParsedSection,
    ) -> tuple[ClaimExtractionCandidate, ...]:
        prompt = self._build_prompt(section)

        response_schema = self._gemini_response_schema()

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )

        if response.parsed is not None:
            schema = ClaimExtractionSchema.model_validate(response.parsed)
        else:
            if not response.text:
                raise ValueError(
                    "Gemini returned neither parsed structured output nor text."
                )

            schema = ClaimExtractionSchema.model_validate_json(response.text)

        candidate = self.converter.convert(schema)

        return (candidate,)

    @staticmethod
    def _gemini_response_schema() -> dict[str, Any]:
        schema = ClaimExtractionSchema.model_json_schema()

        def remove_unsupported_fields(value: Any) -> Any:
            if isinstance(value, dict):
                return {
                    key: remove_unsupported_fields(child)
                    for key, child in value.items()
                    if key != "additionalProperties"
                }

            if isinstance(value, list):
                return [
                    remove_unsupported_fields(item)
                    for item in value
                ]

            return value

        return remove_unsupported_fields(schema)

    @staticmethod
    def _build_prompt(section: ParsedSection) -> str:
        return f"""
You are a regulatory claim extraction system.

Your task is to extract exactly one legally meaningful claim from the
provided regulatory section.

Rules:

1. Use only information explicitly supported by the provided section.
2. Do not invent facts, entities, deadlines, fees, exceptions, or penalties.
3. Preserve the meaning of the source text.
4. Extract the most important actionable or legally meaningful claim.
5. If the section does not contain a meaningful claim, still return the
   required schema using the closest directly supported claim.
6. The claim_type must describe the kind of claim, such as:
   REQUIREMENT, FEE, DEFINITION, APPLICABILITY, EXCEPTION, or PENALTY.
7. structure_type must exactly identify which structure field is populated.
8. Populate exactly one of:
   requirement, fee, definition, applicability, exception, penalty.
9. For requirements:
   - modality must be REQUIRED, PROHIBITED, or PERMITTED.
   - preserve deadlines when explicitly stated.
   - preserve applicability conditions when explicitly stated.
10. Entity references must contain the exact relevant entity wording from
    the source, not a fabricated canonical entity.
11. Do not resolve entities to database IDs.
12. Do not compare this section with previous versions.
13. Do not determine whether this is a policy change.
14. Do not provide explanations outside the structured output.

Section number:
{section.section_number}

Section title:
{section.title}

Section type:
{section.section_type}

Source text:
{section.raw_text}
""".strip()
