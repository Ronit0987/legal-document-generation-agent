import json
from pathlib import Path
import os
import streamlit as st

from src.template_analyzer import TemplateAnalyzer
from src.extractor import CaseInformationExtractor
from src.generator import AffidavitGenerator
from src.validator import AffidavitValidator
from src.evaluator import AffidavitEvaluator


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


st.set_page_config(
    page_title="Legal Document Generation Agent",
    page_icon="⚖️",
    layout="wide"
)

try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass
st.title("⚖️ Legal Document Generation & Evaluation Agent")

st.caption(
    "Generate and validate an Affidavit in Reply from case information."
)


reference_file = st.file_uploader(
    "Upload Reference Affidavit PDF",
    type=["pdf"]
)

case_file = st.file_uploader(
    "Upload Case Information PDF",
    type=["pdf"]
)


if st.button(
    "Generate Affidavit",
    type="primary",
    use_container_width=True
):

    if not reference_file or not case_file:
        st.error(
            "Please upload both the reference affidavit "
            "and the case information PDF."
        )

    else:

        try:

            with st.spinner("Processing documents..."):

                # -------------------------------------
                # Save uploaded files temporarily
                # -------------------------------------

                tmp_dir = Path("tmp")
                tmp_dir.mkdir(exist_ok=True)

                reference_path = (
                    tmp_dir / "reference_affidavit.pdf"
                )

                case_path = (
                    tmp_dir / "case_information.pdf"
                )

                reference_path.write_bytes(
                    reference_file.getbuffer()
                )

                case_path.write_bytes(
                    case_file.getbuffer()
                )

                # -------------------------------------
                # 1. Template analysis
                # -------------------------------------

                analyzer = TemplateAnalyzer(
                    str(reference_path)
                )

                template_structure = (
                    analyzer.analyze_structure()
                )

                # -------------------------------------
                # 2. Case extraction
                # -------------------------------------

                extractor = CaseInformationExtractor(
                    str(case_path)
                )

                source_text = extractor.extract_text()

                affidavit = extractor.extract_entities()

                # -------------------------------------
                # 3. Generate affidavit
                # -------------------------------------

                generated_path = (
                    OUTPUT_DIR /
                    "generated_affidavit.docx"
                )

                generator = AffidavitGenerator(
                    affidavit
                )

                generator.generate(
                    str(generated_path)
                )

                # -------------------------------------
                # 4. Validation
                # -------------------------------------

                validator = AffidavitValidator(
                    affidavit
                )

                validation_result = (
                    validator.validate()
                )

                # -------------------------------------
                # 5. Evaluation
                # -------------------------------------

                evaluator = AffidavitEvaluator(
                    affidavit,
                    source_text=source_text
                )

                evaluation_result = (
                    evaluator.evaluate()
                )

                evaluation_path = (
                    OUTPUT_DIR /
                    "evaluation_report.json"
                )

                evaluator.save_json(
                    str(evaluation_path)
                )

            st.success(
                "Affidavit generated successfully."
            )

            # =====================================
            # SUMMARY
            # =====================================

            st.subheader("Generation Summary")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Validation Score",
                f"{validation_result['score']}%"
            )

            col2.metric(
                "Evaluation Score",
                f"{evaluation_result['overall_score']}%"
            )

            col3.metric(
                "Reply Paragraphs",
                len(affidavit.reply_paragraphs)
            )

            # =====================================
            # CASE INFORMATION
            # =====================================

            st.subheader("Extracted Case Information")

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    "**Court:**",
                    affidavit.header.court
                )

                st.write(
                    "**Jurisdiction:**",
                    affidavit.header.jurisdiction
                )

                st.write(
                    "**Case:**",
                    (
                        f"{affidavit.header.proceeding_type} "
                        f"No. {affidavit.header.case_number} "
                        f"of {affidavit.header.year}"
                    )
                )

                st.write(
                    "**Petitioner:**",
                    affidavit.parties.petitioner
                )

            with col2:

                st.write(
                    "**Respondent No. 2:**",
                    affidavit.parties.respondent_2
                )

                st.write(
                    "**Deponent:**",
                    affidavit.deponent.name
                )

                st.write(
                    "**Designation:**",
                    affidavit.deponent.designation
                )

                st.write(
                    "**Advocate:**",
                    affidavit.advocate.firm
                )

            # =====================================
            # VALIDATION
            # =====================================

            st.subheader("Deterministic Validation")

            for check in validation_result["checks"]:

                if check["passed"]:
                    st.success(
                        f"PASS — {check['name']}: "
                        f"{check['message']}"
                    )

                else:
                    st.error(
                        f"FAIL — {check['name']}: "
                        f"{check['message']}"
                    )

            # =====================================
            # EVALUATION
            # =====================================

            st.subheader("Evaluation Scores")

            scores = evaluation_result["scores"]

            score_cols = st.columns(3)

            score_cols[0].metric(
                "Entity Accuracy",
                f"{scores['entity_accuracy']}%"
            )

            score_cols[1].metric(
                "Completeness",
                f"{scores['completeness']}%"
            )

            score_cols[2].metric(
                "Structure",
                f"{scores['structure']}%"
            )

            score_cols = st.columns(3)

            score_cols[0].metric(
                "Consistency",
                f"{scores['consistency']}%"
            )

            score_cols[1].metric(
                "Template Fidelity",
                f"{scores['template_fidelity']}%"
            )

            score_cols[2].metric(
                "Source Grounding",
                f"{scores['hallucination']}%"
            )

            # =====================================
            # ISSUES
            # =====================================

            if evaluation_result["issues"]:

                st.subheader("Detected Issues")

                for issue in evaluation_result["issues"]:
                    st.warning(
                        issue["message"]
                    )

            else:
                st.success(
                    "No evaluation issues detected."
                )

            # =====================================
            # DOWNLOADS
            # =====================================

            st.subheader("Download Outputs")

            col1, col2 = st.columns(2)

            with open(
                generated_path,
                "rb"
            ) as file:

                col1.download_button(
                    label="Download Generated Affidavit",
                    data=file,
                    file_name="generated_affidavit.docx",
                    mime=(
                        "application/vnd.openxmlformats-"
                        "officedocument.wordprocessingml."
                        "document"
                    ),
                    use_container_width=True
                )

            evaluation_json = json.dumps(
                evaluation_result,
                indent=2,
                ensure_ascii=False
            )

            col2.download_button(
                label="Download Evaluation Report",
                data=evaluation_json,
                file_name="evaluation_report.json",
                mime="application/json",
                use_container_width=True
            )

            # =====================================
            # OPTIONAL DEBUG VIEW
            # =====================================

            with st.expander(
                "View Extracted Structured Data"
            ):

                st.json(
                    affidavit.model_dump()
                )

            with st.expander(
                "View Template Analysis"
            ):

                st.json(
                    template_structure
                )

        except Exception as exc:

            st.error(
                f"Pipeline failed: {exc}"
            )