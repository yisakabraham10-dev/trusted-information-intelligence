import re
from dataclasses import dataclass

from src.services.claim_extraction import ClaimExtractionCandidate
from src.services.claim_structure import RequirementStructure
from src.services.document_structure import ParsedSection


@dataclass(frozen=True)
class ClaimEvidenceValidationResult:
    supported: bool
    errors: tuple[str, ...]


class ClaimEvidenceValidator:
    def validate(
        self,
        candidate: ClaimExtractionCandidate,
        section: ParsedSection,
    ) -> ClaimEvidenceValidationResult:
        source_text = self._normalize(section.raw_text)

        if not isinstance(candidate.structure, RequirementStructure):
            return ClaimEvidenceValidationResult(
                supported=False,
                errors=("Unsupported claim structure for evidence validation.",),
            )

        structure = candidate.structure
        errors: list[str] = []

        if not self._modality_supported(structure.modality, source_text):
            errors.append("Requirement modality is not supported by source section.")

        if not self._action_supported(structure.action, source_text):
            errors.append("Requirement action is not supported by source section.")

        if structure.object is not None:
            object_text = self._normalize(structure.object.raw_text)

            if object_text not in source_text:
                errors.append("Requirement object is not supported by source section.")

        if structure.deadline is not None:
            if not self._deadline_supported(
                structure.deadline.value,
                structure.deadline.unit,
                source_text,
            ):
                errors.append("Requirement deadline is not supported by source section.")

        return ClaimEvidenceValidationResult(
            supported=not errors,
            errors=tuple(errors),
        )

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    @staticmethod
    def _modality_supported(modality: str, source_text: str) -> bool:
        if modality == "REQUIRED":
            return bool(re.search(r"\b(shall|must|required to)\b", source_text))

        if modality == "PROHIBITED":
            return bool(re.search(r"\b(shall not|must not|prohibited)\b", source_text))

        if modality == "PERMITTED":
            return bool(re.search(r"\b(may|permitted|allowed)\b", source_text))

        return False

    @staticmethod
    def _action_supported(action: str, source_text: str) -> bool:
        action = action.lower().strip()

        if action in source_text:
            return True

        if action.endswith("e") and action[:-1] + "ed" in source_text:
            return True

        if action.endswith("e") and action[:-1] + "ing" in source_text:
            return True

        return False

    @staticmethod
    def _deadline_supported(
        value,
        unit: str,
        source_text: str,
    ) -> bool:
        if unit.upper() != "DAYS":
            return False

        number_words = {
            0: "zero",
            1: "one",
            2: "two",
            3: "three",
            4: "four",
            5: "five",
            6: "six",
            7: "seven",
            8: "eight",
            9: "nine",
            10: "ten",
            11: "eleven",
            12: "twelve",
            13: "thirteen",
            14: "fourteen",
            15: "fifteen",
            16: "sixteen",
            17: "seventeen",
            18: "eighteen",
            19: "nineteen",
            20: "twenty",
            30: "thirty",
            40: "forty",
            50: "fifty",
            60: "sixty",
            70: "seventy",
            80: "eighty",
            90: "ninety",
        }

        numeric_value = int(value)

        if str(numeric_value) in source_text:
            return True

        if numeric_value in number_words:
            if re.search(
                rf"\b{number_words[numeric_value]}\s+days?\b",
                source_text,
            ):
                return True

        if 21 <= numeric_value <= 99:
            tens = (numeric_value // 10) * 10
            ones = numeric_value % 10

            if tens in number_words and ones in number_words:
                phrase = f"{number_words[tens]}[- ]{number_words[ones]}"

                if re.search(rf"\b{phrase}\s+days?\b", source_text):
                    return True

        return False