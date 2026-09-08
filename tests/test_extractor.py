from src.extractor import CaseInformationExtractor


def test_extract_case_information():

    extractor = CaseInformationExtractor(
        "input/03_Case_Information.pdf"
    )

    affidavit = extractor.extract_entities()

    assert affidavit.document_type == "Affidavit in Reply"

    assert affidavit.header.case_number == "1847"
    assert affidavit.header.year == "2026"

    assert affidavit.parties.petitioner == "Sunrise Housing Private Limited"

    assert (
        affidavit.parties.respondent_2
        == "Mumbai Metropolitan Region Development Authority"
    )
    assert "to oppose" in affidavit.reply_paragraphs[0].content
    assert "tooppose" not in affidavit.reply_paragraphs[0].content
    assert affidavit.deponent.name == "Arvind Rajan"

    assert len(affidavit.reply_paragraphs) == 6

    assert len(affidavit.exhibits) == 1

    assert affidavit.exhibits[0].label == "EXHIBIT-‘A’"

    assert affidavit.verification.includes_prayer is True

    assert affidavit.exhibits[0].label == "EXHIBIT-‘A’"
    assert affidavit.exhibits[0].description == "communication dated 15 July 2026"
    assert affidavit.exhibits[0].date == "15 July 2026"

    import json

    print(
        json.dumps(
        affidavit.model_dump(),
        indent=2,
        ensure_ascii=False
        )
    )

    assert affidavit.document_type == "Affidavit in Reply"
