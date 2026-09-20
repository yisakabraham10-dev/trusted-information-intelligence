from pathlib import Path

import pytest
from pypdf import PdfWriter

from src.domain.exceptions import ValidationError
from src.services.document_ingestion import (
    DocumentIngestionService,
)


def create_pdf(path: Path, page_count: int = 1) -> None:
    writer = PdfWriter()

    for _ in range(page_count):
        writer.add_blank_page(width=612, height=792)

    with path.open("wb") as file:
        writer.write(file)


def test_extract_rejects_missing_file(tmp_path):
    service = DocumentIngestionService()

    with pytest.raises(
        FileNotFoundError,
        match="PDF file not found",
    ):
        service.extract(tmp_path / "missing.pdf")


def test_extract_rejects_non_pdf_file(tmp_path):
    service = DocumentIngestionService()

    path = tmp_path / "document.txt"
    path.write_text("not a PDF")

    with pytest.raises(
        ValidationError,
        match="Expected a PDF file",
    ):
        service.extract(path)


def test_extract_returns_pages_for_valid_pdf(tmp_path):
    service = DocumentIngestionService()

    path = tmp_path / "document.pdf"
    create_pdf(path, page_count=2)

    result = service.extract(path)

    assert len(result.pages) == 2


def test_extract_preserves_page_numbers(tmp_path):
    service = DocumentIngestionService()

    path = tmp_path / "document.pdf"
    create_pdf(path, page_count=3)

    result = service.extract(path)

    assert [page.page_number for page in result.pages] == [1, 2, 3]


def test_extract_handles_pages_without_extractable_text(tmp_path):
    service = DocumentIngestionService()

    path = tmp_path / "document.pdf"
    create_pdf(path)

    result = service.extract(path)

    assert result.pages[0].text == ""
