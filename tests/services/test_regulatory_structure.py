from src.services.document_ingestion import DocumentIngestionService
from src.services.regulatory_structure import RegulatoryStructureParser


PDF_PATH = "tests/fixtures/customs_proclamation_1425_2026.pdf"


def test_customs_article_51_bilingual_sections_have_clean_boundaries():
    document = DocumentIngestionService().extract(PDF_PATH)

    sections = RegulatoryStructureParser().parse(document.pages)

    article_51_sections = {
        section.section_number: section
        for section in sections
        if section.section_number in {
            "51(1)",
            "51(2)",
            "51(7)",
            "51(8)",
        }
    }

    assert set(article_51_sections) == {
        "51(1)",
        "51(2)",
        "51(7)",
        "51(8)",
    }

    section_51_1 = article_51_sections["51(1)"]

    assert "Any goods imported by sea or land" in section_51_1.raw_text
    assert "forty-five days" in section_51_1.raw_text

    assert "Any goods imported by air" not in section_51_1.raw_text
    assert "Goods entered into temporary customs storage" not in section_51_1.raw_text
    assert "Article 62" not in section_51_1.raw_text
    assert "፪/" not in section_51_1.raw_text
    assert "፯/" not in section_51_1.raw_text
    assert "፰/" not in section_51_1.raw_text
