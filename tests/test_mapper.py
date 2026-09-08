from src.extractor import CaseInformationExtractor
from src.mapper import AffidavitMapper


def test_affidavit_mapper():
    extractor = CaseInformationExtractor(
        "input/03_Case_Information.pdf"
    )

    affidavit = extractor.extract_entities()

    mapper = AffidavitMapper(affidavit)

    mapped = mapper.map()

    assert mapped["court"] == (
        "IN THE HIGH COURT OF JUDICATURE AT BOMBAY"
    )

    assert mapped["jurisdiction"] == (
        "ORDINARY ORIGINAL CIVIL JURISDICTION"
    )

    assert mapped["case_reference"] == (
        "WRIT PETITION NO. 1847 OF 2026"
    )

    assert mapped["affidavit_title"] == (
        "AFFIDAVIT IN REPLY ON BEHALF OF RESPONDENT NO. 2"
    )

    assert mapped["deponent_name"] == "Arvind Rajan"

    assert "Arvind Rajan" in mapped["deponent_clause"]

    assert "Deputy Metropolitan Commissioner" in (
        mapped["deponent_clause"]
    )

    assert len(mapped["reply_paragraphs"]) == 6

    assert mapped["reply_paragraphs"][0]["number"] == 1

    assert len(mapped["exhibits"]) == 1

    assert mapped["exhibits"][0]["label"] == "EXHIBIT-‘A’"

    assert mapped["attestation"]["place"] == "Mumbai"

    assert mapped["attestation"]["date"] == (
        "5 September 2026"
    )

    assert "paragraphs 1 to 6" in (
        mapped["verification"]["text"]
    )

    assert "Prayer" in mapped["verification"]["text"]

    assert mapped["advocate"]["firm"] == (
        "Rajan & Associates"
    )