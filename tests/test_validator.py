from src.extractor import CaseInformationExtractor
from src.validator import AffidavitValidator


def test_affidavit_validator():

    extractor = CaseInformationExtractor(
        "input/03_Case_Information.pdf"
    )

    affidavit = extractor.extract_entities()

    validator = AffidavitValidator(affidavit)

    result = validator.validate()

    assert result["total_checks"] >= 3
    assert result["passed_checks"] == result["total_checks"]
    assert result["score"] == 100.0

    check_names = [
        check["name"]
        for check in result["checks"]
    ]

    assert "Reply paragraph numbering" in check_names
    assert "Verification paragraph range" in check_names
    assert "Exhibit consistency" in check_names