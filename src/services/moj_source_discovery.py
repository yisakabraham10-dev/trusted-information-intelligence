from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class DiscoveredDocument:
    title: str
    document_number: str | None
    publication_date: str | None
    document_type: str | None
    status: str | None
    source_page_url: str
    detail_url: str | None
    pdf_url: str


class MoJSourceDiscovery:
    """
    Discover regulatory documents exposed by a Ministry of Justice
    sector page.

    This service only discovers source metadata and official PDF URLs.
    It does not download files, parse PDFs, extract claims, or access
    the database.
    """

    def discover_sector(
        self,
        html: str,
        *,
        source_page_url: str,
    ) -> tuple[DiscoveredDocument, ...]:
        soup = BeautifulSoup(html, "html.parser")

        documents: list[DiscoveredDocument] = []
        seen: set[str] = set()

        for title_link in self._english_title_links(soup):
            container = self._document_container(title_link)

            if container is None:
                continue

            title = self._clean_text(title_link.get_text(" ", strip=True))
            detail_url = urljoin(source_page_url, title_link.get("href", ""))

            pdf_url = self._find_pdf_url(container, source_page_url)

            if not title or not pdf_url:
                continue

            identity = detail_url or pdf_url

            if identity in seen:
                continue

            seen.add(identity)

            documents.append(
                DiscoveredDocument(
                    title=title,
                    document_number=self._extract_document_number(container),
                    publication_date=self._extract_publication_date(container),
                    document_type=self._infer_document_type(title),
                    status=self._extract_status(container),
                    source_page_url=source_page_url,
                    detail_url=detail_url,
                    pdf_url=pdf_url,
                )
            )

        return tuple(documents)

    @staticmethod
    def _english_title_links(soup: BeautifulSoup):
        for link in soup.find_all("a", href=True):
            text = " ".join(link.get_text(" ", strip=True).split())

            if not text:
                continue

            if not text.upper().startswith(
                ("PROCLAMATION", "REGULATION", "DIRECTIVE", "COUNCIL OF MINISTERS")
            ):
                continue

            if "/en/law/" not in link["href"]:
                continue

            yield link

    @staticmethod
    def _document_container(link):
        """
        The current MoJ page renders each law as an Elementor document row.
        The useful container is the nearest ancestor containing a Download
        link and the document metadata.
        """
        for ancestor in link.parents:
            if ancestor.name != "div":
                continue

            text = ancestor.get_text(" ", strip=True)

            has_pdf = any(
                "pdf" in (candidate.get("href") or "").lower()
                for candidate in ancestor.find_all("a", href=True)
            )

            has_status = "In Force" in text or "Repealed" in text

            if has_pdf and has_status:
                return ancestor

        return None

    @staticmethod
    def _find_pdf_url(container, source_page_url: str) -> str | None:
        for link in container.find_all("a", href=True):
            href = link["href"].strip()

            if ".pdf" in href.lower():
                return urljoin(source_page_url, href)

        return None

    @staticmethod
    def _extract_document_number(container) -> str | None:
        import re

        text = " ".join(container.stripped_strings)

        match = re.search(
            r"\b(?:No\.\s*)?(\d{2,5}/\d{4})\b",
            text,
        )

        return match.group(1) if match else None

    @staticmethod
    def _extract_publication_date(container) -> str | None:
        """
        Preserve the date exactly as published by the MoJ page.

        The current MoJ markup places the publication-date metadata in the
        immediate parent of the container that holds the PDF and status.

        Calendar conversion is deliberately outside discovery.
        """
        import re

        containers = [container]

        if container.parent is not None:
            containers.append(container.parent)

        for candidate in containers:
            for text in candidate.stripped_strings:
                cleaned = " ".join(text.split())

                if "ዓ.ም" not in cleaned:
                    continue

                if re.search(r"\d{4}", cleaned):
                    return cleaned

        return None

    @staticmethod
    def _extract_status(container) -> str | None:
        text = " ".join(container.stripped_strings)

        for status in ("In Force", "Repealed", "Draft"):
            if status in text:
                return status

        return None

    @staticmethod
    def _infer_document_type(title: str) -> str | None:
        normalized = title.upper()

        if "PROCLAMATION" in normalized:
            return "PROCLAMATION"

        if "REGULATION" in normalized:
            return "REGULATION"

        if "DIRECTIVE" in normalized:
            return "DIRECTIVE"

        return None

    @staticmethod
    def _clean_text(value: str) -> str:
        return " ".join(value.split())
