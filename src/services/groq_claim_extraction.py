from typing import Any

from groq import Groq

from src.config import Settings
from src.services.claim_extraction import (
    ClaimExtractionCandidate,
    ClaimExtractionProvider,
)
from src.services.claim_extraction_conversion import ClaimExtractionConverter
from src.services.claim_extraction_schema import (
    ClaimExtractionListSchema,
)
from src.services.document_structure import ParsedSection


class GroqClaimExtractionProvider(ClaimExtractionProvider):
    def __init__(
        self,
        settings: Settings,
        model: str = "openai/gpt-oss-120b",
    ):
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is required for Groq claim extraction.")

        self.client = Groq(api_key=settings.groq_api_key)
        self.model = model
        self.converter = ClaimExtractionConverter()

    def extract(
        self,
        section: ParsedSection,
    ) -> tuple[ClaimExtractionCandidate, ...]:
        prompt = self._build_prompt(section)
        response_schema = self._groq_response_schema()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a regulatory claim extraction system. "
                        "Return only the requested structured JSON object. "
                        "Follow the structure-field nullability rules exactly."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "claim_extraction_list",
                    "strict": True,
                    "schema": response_schema,
                },
            },
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("Groq returned empty structured output.")

        schema = ClaimExtractionListSchema.model_validate_json(content)

        candidates = tuple(
            self.converter.convert(claim_schema)
            for claim_schema in schema.claims
        )

        return candidates

    @staticmethod
    def _groq_response_schema() -> dict[str, Any]:
        schema = ClaimExtractionListSchema.model_json_schema()

        def make_groq_compatible(value: Any) -> Any:
            if isinstance(value, dict):
                result = {}

                for key, child in value.items():
                    if key == "pattern":
                        continue

                    result[key] = make_groq_compatible(child)

                if result.get("type") == "object":
                    properties = result.get("properties")

                    if isinstance(properties, dict):
                        result["required"] = list(properties.keys())

                    result["additionalProperties"] = False

                return result

            if isinstance(value, list):
                return [
                    make_groq_compatible(item)
                    for item in value
                ]

            return value

        return make_groq_compatible(schema)

    @staticmethod
    def _build_prompt(section: ParsedSection) -> str:
        return f"""
Your task is to extract every independently checkable, legally meaningful
claim from the provided regulatory section.

A claim should represent a distinct legal assertion that can be checked,
compared across document versions, or used to determine applicability or
business impact.

Rules:

1. Use only information explicitly supported by the provided section.
2. Do not invent facts, entities, deadlines, fees, exceptions, or penalties.
3. Preserve the meaning of the source text.
4. Extract all distinct legally meaningful claims, but do not create
   unnecessary duplicates.
5. Do not split a single legal requirement into multiple claims merely
   because it contains several sentences, conditions, or exceptions.
6. If a REQUIREMENT contains an exception, keep that exception as part of
   the requirement's text or requirement structure only. Do NOT create a
   separate exception claim unless the exception is itself an independently
   checkable legal assertion.
7. The `claim_type` must describe the kind of claim, such as:
   REQUIREMENT, FEE, DEFINITION, APPLICABILITY, EXCEPTION, or PENALTY.
8. `structure_type` must exactly identify the one structure that represents
   the extracted claim.
9. EXACTLY ONE of these fields may contain an object for each claim:
   - requirement
   - fee
   - definition
   - applicability
   - exception
   - penalty
10. EVERY OTHER structure field MUST be null for that claim.
11. The value of `structure_type` MUST correspond to the one non-null
    structure field.
12. For requirements:
    - modality must be REQUIRED, PROHIBITED, or PERMITTED.
    - preserve deadlines when explicitly stated.
    - preserve applicability conditions when explicitly stated.
13. Entity references must contain the exact relevant entity wording from
    the source, not a fabricated canonical entity.
14. Do not resolve entities to database IDs.
15. Do not compare this section with previous versions.
16. Do not determine whether this is a policy change.
17. Do not provide explanations outside the structured output.
18. Return the claims inside the `claims` list.
19. If the section contains one legally meaningful claim, return one item.
20. If the section contains multiple independently checkable claims, return
    multiple items.

IMPORTANT STRUCTURE EXAMPLE:

If a claim has `structure_type` equal to `REQUIREMENT`, that claim MUST have:

requirement = populated object
fee = null
definition = null
applicability = null
exception = null
penalty = null

If an exception appears inside the requirement's wording, it remains part
of the requirement. It does NOT automatically become a separate claim.

Section number:
{section.section_number}

Section title:
{section.title}

Section type:
{section.section_type}

Source text:
{section.raw_text}
""".strip()
