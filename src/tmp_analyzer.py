from pathlib import Path
from typing import Dict, List

import fitz  # PyMuPDF


class TemplateAnalyzer:
    """
    Analyzes the reference affidavit and converts its structure
    into a reusable template definition.
    """

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)

        if not self.pdf_path.exists():
            raise FileNotFoundError(
                f"Reference document not found: {self.pdf_path}"
            )

    def extract_text(self) -> str:
        """Extract text from the reference PDF."""

        document = fitz.open(self.pdf_path)

        pages = []

        for page in document:
            pages.append(page.get_text())

        document.close()

        return "\n".join(pages)

    def analyze_structure(self) -> Dict:
        """
        Identify the major structural components of the
        reference Affidavit in Reply.
        """

        text = self.extract_text()

        template = {
            "document_type": "Affidavit in Reply",

            "sections": [
                {
                    "name": "court_heading",
                    "required": True,
                    "description": "Court and jurisdiction heading"
                },
                {
                    "name": "case_details",
                    "required": True,
                    "description": "Proceeding type, case number and year"
                },
                {
                    "name": "cause_title",
                    "required": True,
                    "description": "Petitioner and respondent details"
                },
                {
                    "name": "affidavit_title",
                    "required": True,
                    "description": "Title identifying the answering respondent"
                },
                {
                    "name": "deponent_clause",
                    "required": True,
                    "description": "Identity, designation, organisation and address of deponent"
                },
                {
                    "name": "reply_paragraphs",
                    "required": True,
                    "description": "Numbered paragraphs containing the reply"
                },
                {
                    "name": "exhibits",
                    "required": False,
                    "description": "Documents referred to as exhibits"
                },
                {
                    "name": "prayer",
                    "required": True,
                    "description": "Reliefs requested by the answering respondent"
                },
                {
                    "name": "attestation",
                    "required": True,
                    "description": "Place, date and attestation/deponent section"
                },
                {
                    "name": "verification",
                    "required": True,
                    "description": "Verification of the affidavit paragraphs and prayer"
                },
                {
                    "name": "advocate_block",
                    "required": True,
                    "description": "Advocate/firm and representation details"
                }
            ],

            "formatting_rules": {
                "numbered_reply_paragraphs": True,
                "prayer_is_separate_section": True,
                "verification_is_separate_section": True,
                "exhibit_reference_must_match": True
            },

            "source_text_length": len(text)
        }

        return template

    def save_template(self, output_path: str):
        """Save the analyzed template as JSON."""

        import json

        template = self.analyze_structure()

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(template, file, indent=2)

        return output_file