from pathlib import Path

from docx import Document

from src.extractor import CaseInformationExtractor
from src.generator import AffidavitGenerator


def test_generate_affidavit():
    extractor = CaseInformationExtractor(
        "input/03_Case_Information.pdf"
    )

    affidavit = extractor.extract_entities()

    generator = AffidavitGenerator(affidavit)

    output_path = generator.generate(
        "output/generated_affidavit.docx"
    )

    assert Path(output_path).exists()

    doc = Document(output_path)

    full_text = "\n".join(
        paragraph.text
        for paragraph in doc.paragraphs
    )

    assert "IN THE HIGH COURT OF JUDICATURE AT BOMBAY" in full_text

    assert "WRIT PETITION NO. 1847 OF 2026" in full_text

    assert (
        "AFFIDAVIT IN REPLY ON BEHALF OF RESPONDENT NO. 2"
        in full_text
    )

    assert "Arvind Rajan" in full_text

    assert "EXHIBIT-‘A’" in full_text

    assert "paragraphs 1 to 6" in full_text

    assert "PRAYER" in full_text

    assert "VERIFICATION" in full_text

    assert "Rajan & Associates" in full_text