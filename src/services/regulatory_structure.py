import re

from src.services.document_ingestion import ExtractedPage
from src.services.document_structure import ParsedSection


ETHIOPIC_DIGITS = {
    "፩": 1,
    "፪": 2,
    "፫": 3,
    "፬": 4,
    "፭": 5,
    "፮": 6,
    "፯": 7,
    "፰": 8,
    "፱": 9,
    "፲": 10,
    "፳": 20,
    "፴": 30,
    "፵": 40,
    "፶": 50,
    "፷": 60,
    "፸": 70,
    "፹": 80,
    "፺": 90,
}


class RegulatoryStructureParser:
    """
    Parse the structural hierarchy of Ethiopian regulatory documents.

    This parser is intentionally conservative.

    It identifies:
    - English amendment headings
    - English sub-articles
    - article references
    - page-level provenance

    Ethiopian Negarit Gazette documents are commonly bilingual.
    The Amharic and English versions can appear sequentially in the
    extracted PDF text, so article references must not be treated as
    a single global mutable context.

    The parser does not:
    - interpret legal meaning
    - extract claims
    - determine policy changes
    - call an LLM
    - write to the database
    """

    AMENDMENT_PATTERN = re.compile(
        r"^(\d+)\)\s+"
    )

    ARTICLE_REFERENCE_PATTERN = re.compile(
        r"Article\s+(\d+)",
        re.IGNORECASE,
    )

    AMHARIC_ARTICLE_PATTERN = re.compile(
        r"አንቀጽ\s+([፩-፺]+)"
    )

    SUB_ARTICLE_PATTERN = re.compile(
        r"^(\d+)\/\s*(.*)"
    )

    def parse(
        self,
        pages: tuple[ExtractedPage, ...],
    ) -> tuple[ParsedSection, ...]:

        sections: list[ParsedSection] = []

        # Article number associated with the current English amendment.
        current_article: str | None = None

        # Amharic article reference waiting to be associated with the
        # next English amendment.
        pending_amharic_article: str | None = None

        buffer: list[str] = []
        buffer_page_start: int | None = None
        buffer_page_end: int | None = None
        buffer_section_number: str | None = None
        buffer_section_type: str | None = None

        def flush() -> None:
            nonlocal buffer
            nonlocal buffer_page_start
            nonlocal buffer_page_end
            nonlocal buffer_section_number
            nonlocal buffer_section_type

            if not buffer or buffer_section_type is None:
                return

            sections.append(
                ParsedSection(
                    section_number=buffer_section_number,
                    title=None,
                    section_type=buffer_section_type,
                    page_start=buffer_page_start or 1,
                    page_end=(
                        buffer_page_end
                        or buffer_page_start
                        or 1
                    ),
                    raw_text="\n".join(buffer).strip(),
                )
            )

            buffer = []
            buffer_page_start = None
            buffer_page_end = None
            buffer_section_number = None
            buffer_section_type = None

        for page in pages:
            for raw_line in page.text.splitlines():
                line = raw_line.strip()

                if not line:
                    continue

                # ---------------------------------------------------------
                # Detect an Amharic article reference.
                #
                # Example:
                #
                #   ፫) የአዋጁ አንቀጽ ፶፩ ...
                #
                # This is context for a future English amendment.
                #
                # We do NOT change current_article here.
                # ---------------------------------------------------------

                amharic_article = self._extract_amharic_article_number(line)

                if amharic_article is not None:
                    pending_amharic_article = amharic_article

                # ---------------------------------------------------------
                # Detect an English amendment heading.
                #
                # Example:
                #
                #   3) Sub-Articles (1), (2), (7), and (8) of Article
                #   51 of the Proclamation...
                #
                # or:
                #
                #   3) Sub-Articles (1), (2), (7), and (8) of Article
                #
                # where Article 51 was already established by the
                # preceding Amharic amendment.
                # ---------------------------------------------------------

                amendment_match = self.AMENDMENT_PATTERN.match(line)

                if amendment_match:
                    flush()

                    amendment_number = amendment_match.group(1)

                    # First preference:
                    # article explicitly stated in the English heading.
                    english_article = (
                        self._extract_english_article_number(line)
                    )

                    if english_article is not None:
                        current_article = english_article

                    # Second preference:
                    # article established by the preceding Amharic text.
                    elif pending_amharic_article is not None:
                        current_article = pending_amharic_article

                    buffer = [line]
                    buffer_page_start = page.page_number
                    buffer_page_end = page.page_number
                    buffer_section_number = amendment_number
                    buffer_section_type = "AMENDMENT"

                    continue

                # ---------------------------------------------------------
                # English sub-article.
                #
                # We intentionally only recognize ASCII-numbered
                # sub-articles:
                #
                #   1/
                #   2/
                #   7/
                #
                # Amharic versions use Ethiopic digits:
                #
                #   ፩/
                #   ፪/
                #   ፯/
                #
                # Those are ignored structurally because the English
                # version provides the canonical MVP representation.
                # ---------------------------------------------------------

                sub_article_match = self.SUB_ARTICLE_PATTERN.match(line)

                if (
                    sub_article_match
                    and current_article is not None
                ):
                    flush()

                    sub_article = sub_article_match.group(1)
                    content = sub_article_match.group(2)

                    buffer = [content]
                    buffer_page_start = page.page_number
                    buffer_page_end = page.page_number

                    buffer_section_number = (
                        f"{current_article}({sub_article})"
                    )

                    buffer_section_type = "SUB_ARTICLE"

                    continue

                # ---------------------------------------------------------
                # Continuation of the current section.
                # ---------------------------------------------------------

                if buffer_section_type is not None:
                    buffer.append(line)
                    buffer_page_end = page.page_number

        flush()

        return tuple(sections)

    def _extract_english_article_number(
        self,
        line: str,
    ) -> str | None:
        """
        Extract an English article reference.

        Example:

            Article 62

        Returns:

            "62"
        """

        match = self.ARTICLE_REFERENCE_PATTERN.search(line)

        if match is None:
            return None

        return match.group(1)

    def _extract_amharic_article_number(
        self,
        line: str,
    ) -> str | None:
        """
        Extract an Amharic article reference.

        Example:

            ፫) የአዋጁ አንቀጽ ፶፩ ...

        Returns:

            "51"
        """

        match = self.AMHARIC_ARTICLE_PATTERN.search(line)

        if match is None:
            return None

        return str(
            self._parse_ethiopic_number(
                match.group(1)
            )
        )

    @staticmethod
    def _parse_ethiopic_number(
        value: str,
    ) -> int:
        """
        Convert the Ethiopic numeral forms used by this document.

        Examples:

            ፩   -> 1
            ፶   -> 50
            ፶፩  -> 51
            ፷፪  -> 62
            ፹፱  -> 89
        """

        total = 0

        for character in value:
            if character not in ETHIOPIC_DIGITS:
                raise ValueError(
                    f"Unsupported Ethiopic numeral character: {character}"
                )

            total += ETHIOPIC_DIGITS[character]

        return total