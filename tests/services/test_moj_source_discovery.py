from pathlib import Path

from src.services.moj_source_discovery import MoJSourceDiscovery


FIXTURE_PATH = Path(
    "tests/fixtures/moj/trade-commercial-regulations.html"
)

SOURCE_PAGE_URL = (
    "https://justice.gov.et/en/sector/trade-commercial-regulations/"
)

EXPECTED_TITLE = (
    "REGULATION No. 574/2025 COUNCIL OF MINISTERS REGULATION "
    "FOR THE IMPLEMENTATION OF THE CONCESSION OF DUTY TARIFF "
    "RATES ON GOODS FOR THE AFRICAN CONTINENTAL FREE TRADE AREA"
)

EXPECTED_DETAIL_URL = (
    "https://justice.gov.et/en/law/"
    "%e1%8b%a8%e1%8a%a0%e1%8d%8d%e1%88%aa%e1%8a%ab-%e1%8a%a0%e1%88%85%e1%8c%89%e1%88%ab%e1%8b%8a-"
    "%e1%8a%90%e1%8c%bb-%e1%8a%95%e1%8c%8d%e1%8b%b5-%e1%89%80%e1%8c%a0%e1%8a%93-%"
    "e1%88%b5%e1%88%9d%e1%88%9d/"
)

EXPECTED_PDF_URL = (
    "https://justice.gov.et/wp-content/uploads/2026/01/"
    "ደንብ-ቁጥር-574-2017-2.pdf"
)


def load_fixture() -> str:
    return FIXTURE_PATH.read_text(encoding="utf-8")


def test_discovers_574_regulation():
    documents = MoJSourceDiscovery().discover_sector(
        load_fixture(),
        source_page_url=SOURCE_PAGE_URL,
    )

    assert len(documents) == 1

    document = documents[0]

    assert document.title == EXPECTED_TITLE
    assert document.document_number == "574/2017"
    assert document.document_type == "REGULATION"
    assert document.status == "In Force"
    assert document.publication_date == "ሀምሌ 07÷ 2017 ዓ.ም."
    assert document.detail_url == EXPECTED_DETAIL_URL
    assert document.pdf_url == EXPECTED_PDF_URL


def test_deduplicates_repeated_document_entries():
    documents = MoJSourceDiscovery().discover_sector(
        load_fixture(),
        source_page_url=SOURCE_PAGE_URL,
    )

    matches = [
        document
        for document in documents
        if "574/2025" in document.title
    ]

    assert len(matches) == 1


def test_preserves_official_pdf_url():
    documents = MoJSourceDiscovery().discover_sector(
        load_fixture(),
        source_page_url=SOURCE_PAGE_URL,
    )

    assert documents[0].pdf_url == EXPECTED_PDF_URL
    assert documents[0].pdf_url.startswith(
        "https://justice.gov.et/wp-content/uploads/"
    )
    assert documents[0].pdf_url.endswith(".pdf")
