import json
from pathlib import Path

from src.extractor import CaseInformationExtractor
from src.evaluator import AffidavitEvaluator


def test_affidavit_evaluator():

    extractor = CaseInformationExtractor(
        "input/03_Case_Information.pdf"
    )

    affidavit = extractor.extract_entities()
    source_text = extractor.extract_text()
    evaluator = AffidavitEvaluator(affidavit,
                                       source_text=source_text)

    result = evaluator.evaluate()

    assert "overall_score" in result
    assert "scores" in result
    assert "issues" in result

    assert result["overall_score"] >= 90

    assert "entity_accuracy" in result["scores"]
    assert "completeness" in result["scores"]
    assert "structure" in result["scores"]
    assert "consistency" in result["scores"]
    assert "template_fidelity" in result["scores"]
    assert "hallucination" in result["scores"]

    output_path = evaluator.save_json(
        "output/evaluation_report.json"
    )

    assert Path(output_path).exists()

    with open(
        output_path,
        "r",
        encoding="utf-8"
    ) as file:
        saved = json.load(file)

    assert saved["overall_score"] == result["overall_score"]