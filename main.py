from pathlib import Path

from src.template_analyzer import TemplateAnalyzer
from src.extractor import CaseInformationExtractor
from src.mapper import AffidavitMapper
from src.generator import AffidavitGenerator
from src.validator import AffidavitValidator
from src.evaluator import AffidavitEvaluator


REFERENCE_PATH = "input/02 Affidavit in Reply Sample.docx.pdf"
CASE_INFO_PATH = "input/03_Case_Information.pdf"

OUTPUT_DIR = Path("output")
AFFIDAVIT_OUTPUT = OUTPUT_DIR / "generated_affidavit.docx"
EVALUATION_OUTPUT = OUTPUT_DIR / "evaluation_report.json"


def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("LEGAL DOCUMENT GENERATION & EVALUATION AGENT")
    print("=" * 60)

    # --------------------------------------------------
    # Step 1: Analyze reference affidavit
    # --------------------------------------------------

    print("\n[1/6] Analyzing reference affidavit...")

    template_analyzer = TemplateAnalyzer(
        REFERENCE_PATH
    )

    template_structure = (
        template_analyzer.analyze_structure()
    )

    print(
        f"Detected document type: "
        f"{template_structure['document_type']}"
    )

    # --------------------------------------------------
    # Step 2: Extract case information
    # --------------------------------------------------

    print("\n[2/6] Extracting case information...")

    extractor = CaseInformationExtractor(
        CASE_INFO_PATH
    )

    source_text = extractor.extract_text()

    affidavit = extractor.extract_entities()

    print(
        f"Case: "
        f"{affidavit.header.case_number}/"
        f"{affidavit.header.year}"
    )

    print(
        f"Deponent: {affidavit.deponent.name}"
    )

    # --------------------------------------------------
    # Step 3: Map extracted information
    # --------------------------------------------------

    print("\n[3/6] Mapping document structure...")

    mapper = AffidavitMapper(
        affidavit
    )

    mapped = mapper.map()

    print(
        f"Mapped {len(mapped['reply_paragraphs'])} "
        f"reply paragraphs."
    )

    # --------------------------------------------------
    # Step 4: Generate DOCX
    # --------------------------------------------------

    print("\n[4/6] Generating affidavit...")

    generator = AffidavitGenerator(
        affidavit
    )

    generated_path = generator.generate(
        str(AFFIDAVIT_OUTPUT)
    )

    print(
        f"Generated: {generated_path}"
    )

    # --------------------------------------------------
    # Step 5: Run deterministic validation
    # --------------------------------------------------

    print("\n[5/6] Running validation checks...")

    validator = AffidavitValidator(
        affidavit
    )

    validation_result = validator.validate()

    print(
        f"Validation score: "
        f"{validation_result['score']}%"
    )

    for check in validation_result["checks"]:
        status = (
            "PASS"
            if check["passed"]
            else "FAIL"
        )

        print(
            f"  [{status}] "
            f"{check['name']}"
        )

    # --------------------------------------------------
    # Step 6: Generate evaluation report
    # --------------------------------------------------

    print("\n[6/6] Generating evaluation report...")

    evaluator = AffidavitEvaluator(
        affidavit,
        source_text=source_text
    )

    evaluation = evaluator.evaluate()

    evaluator.save_json(
        str(EVALUATION_OUTPUT)
    )

    print(
        f"Overall evaluation score: "
        f"{evaluation['overall_score']}%"
    )

    print(
        f"Evaluation report: "
        f"{EVALUATION_OUTPUT}"
    )

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()