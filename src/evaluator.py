import json
from pathlib import Path
from typing import Dict, Any
import re
from difflib import SequenceMatcher

from src.schemas import Affidavit
from src.validator import AffidavitValidator


class AffidavitEvaluator:

    def __init__(self, affidavit: Affidavit,source_text: str = ""):
        self.affidavit = affidavit
        self.source_text = source_text
        self.validator = AffidavitValidator(affidavit)
    def _paragraph_grounding_score(
    self,
    paragraph_text: str
) -> float:

        source = self._normalize_text(
            self.source_text
        )

        paragraph = self._normalize_text(
            paragraph_text
        )

        # Direct match
        if paragraph in source:
            return 100.0

        words = source.split()
        paragraph_words = paragraph.split()

        if not paragraph_words:
            return 0.0

        window_size = len(paragraph_words)

        best_ratio = 0.0

        # Search around approximately paragraph-sized windows
        for start in range(
            0,
            len(words),
            max(1, window_size // 4)
        ):
            end = start + window_size + 15

            candidate = " ".join(
                words[start:end]
            )

            ratio = SequenceMatcher(
                None,
                paragraph,
                candidate
            ).ratio()

            best_ratio = max(
                best_ratio,
                ratio
            )

        return round(
            best_ratio * 100,
            2
        )    

    def _normalize_text(self, text: str) -> str:
        text = text.lower()

        # Normalize quotation marks / dashes
        text = (
            text.replace("‘", "'")
            .replace("’", "'")
            .replace("“", '"')
            .replace("”", '"')
            .replace("—", "-")
        )

        # Collapse whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()


    def _text_similarity(
        self,
        generated: str,
        source: str
    ) -> float:

        generated = self._normalize_text(generated)
        source = self._normalize_text(source)

        # Exact containment gets full credit
        if generated in source:
            return 1.0

        return SequenceMatcher(
            None,
            generated,
            source
        ).ratio()    

    def evaluate(self) -> Dict[str, Any]:

        validation_result = self.validator.validate()

        checks = validation_result["checks"]

        check_map = {
            check["name"]: check
            for check in checks
        }

        entity_accuracy = self._score_entity_accuracy()
        completeness = self._score_completeness(check_map)
        structure = self._score_structure(check_map)
        consistency = self._score_consistency(check_map)
        template_fidelity = self._score_template_fidelity()
        hallucination = self._score_hallucination()

        scores = {
            "entity_accuracy": entity_accuracy,
            "completeness": completeness,
            "structure": structure,
            "consistency": consistency,
            "template_fidelity": template_fidelity,
            "hallucination": hallucination
        }

        overall_score = round(
            sum(scores.values()) / len(scores),
            2
        )

        issues = self._collect_issues(
            validation_result,
            scores
        )

        return {
            "overall_score": overall_score,
            "scores": scores,
            "issues": issues,
            "validation_summary": validation_result,
            "scoring_explanation": {
                "entity_accuracy":
                    "Checks whether key extracted entities are present and internally plausible.",
                "completeness":
                    "Checks whether required affidavit components are present.",
                "structure":
                    "Checks numbering and structural organization of the affidavit.",
                "consistency":
                    "Checks respondent, exhibit, and verification consistency.",
                "template_fidelity":
                    "Checks whether the generated structure follows the expected Affidavit in Reply format.",
                    "hallucination": (
        "Measures source grounding by checking extracted entities "
        "against the case information and comparing reply paragraphs "
        "with the closest matching source passages."
    )
            }
        }

    def _score_entity_accuracy(self) -> float:

        required_entities = [
            self.affidavit.header.court,
            self.affidavit.header.case_number,
            self.affidavit.header.year,
            self.affidavit.parties.petitioner,
            self.affidavit.parties.respondent_1,
            self.affidavit.parties.respondent_2,
            self.affidavit.deponent.name,
            self.affidavit.deponent.designation,
            self.affidavit.advocate.firm
        ]

        valid = sum(
            1
            for item in required_entities
            if item and str(item).strip()
        )

        return round(
            (valid / len(required_entities)) * 100,
            2
        )

    def _score_completeness(
        self,
        check_map: Dict[str, Dict]
    ) -> float:

        required_checks = [
            "Required fields present",
            "Prayer present"
        ]

        return self._score_checks(
            required_checks,
            check_map
        )

    def _score_structure(
        self,
        check_map: Dict[str, Dict]
    ) -> float:

        required_checks = [
            "Reply paragraph numbering",
            "Verification paragraph range"
        ]

        return self._score_checks(
            required_checks,
            check_map
        )

    def _score_consistency(
        self,
        check_map: Dict[str, Dict]
    ) -> float:

        required_checks = [
            "Exhibit consistency",
            "Respondent consistency",
            "Verification paragraph range"
        ]

        return self._score_checks(
            required_checks,
            check_map
        )

    def _score_template_fidelity(self) -> float:

        expected_sections = [
            self.affidavit.header.court,
            self.affidavit.header.jurisdiction,
            self.affidavit.affidavit_title
            or self.affidavit.filed_on_behalf_of,
            self.affidavit.reply_paragraphs,
            self.affidavit.prayer,
            self.affidavit.verification,
            self.affidavit.advocate
        ]

        present = sum(
            1
            for item in expected_sections
            if item
        )

        return round(
            (present / len(expected_sections)) * 100,
            2
        )

    
    def _score_hallucination(self) -> float:

        if not self.source_text:
            self.grounding_issues = [
                {
                    "type": "source",
                    "message": "Source text was not provided."
                }
            ]
            return 0.0

        source = self._normalize_text(
            self.source_text
        )

        scores = []
        grounding_issues = []

        # -----------------------------------------
        # Entity grounding
        # -----------------------------------------

        claims = {
            "court": self.affidavit.header.court,
            "jurisdiction": self.affidavit.header.jurisdiction,
            "case_number": self.affidavit.header.case_number,
            "year": self.affidavit.header.year,
            "petitioner": self.affidavit.parties.petitioner,
            "respondent_1": self.affidavit.parties.respondent_1,
            "respondent_2": self.affidavit.parties.respondent_2,
            "deponent_name": self.affidavit.deponent.name,
            "designation": self.affidavit.deponent.designation,
            "organisation": self.affidavit.deponent.organisation,
            "place": self.affidavit.attestation.place,
            "date": self.affidavit.attestation.date,
            "advocate_firm": self.affidavit.advocate.firm,
        }

        for field_name, claim in claims.items():

            if not claim:
                continue

            normalized_claim = self._normalize_text(
                str(claim)
            )

            if normalized_claim in source:
                scores.append(100.0)
            else:
                scores.append(0.0)

                grounding_issues.append({
                    "type": "entity",
                    "field": field_name,
                    "value": str(claim),
                    "message": (
                        f"{field_name} was not found "
                        f"in the source text."
                    )
                })

        # -----------------------------------------
        # Reply paragraph grounding
        # -----------------------------------------

        for paragraph in self.affidavit.reply_paragraphs:

            grounding_score = (
                self._paragraph_grounding_score(
                    paragraph.content
                )
            )

            scores.append(grounding_score)

            if grounding_score < 85:

                grounding_issues.append({
                    "type": "reply_paragraph",
                    "paragraph": paragraph.number,
                    "grounding_score": grounding_score,
                    "message": (
                        f"Reply paragraph {paragraph.number} "
                        f"has {grounding_score}% similarity "
                        f"to the closest source passage."
                    )
                })

        self.grounding_issues = grounding_issues

        if not scores:
            return 0.0

        return round(
            sum(scores) / len(scores),
            2
        )
    def _score_checks(
        self,
        names,
        check_map
    ) -> float:

        selected = [
            check_map[name]
            for name in names
            if name in check_map
        ]

        if not selected:
            return 0.0

        passed = sum(
            1
            for check in selected
            if check["passed"]
        )

        return round(
            (passed / len(selected)) * 100,
            2
        )

    def _collect_issues(
    self,
    validation_result,
    scores
):

        issues = []

        for check in validation_result["checks"]:

            if not check["passed"]:
                issues.append({
                    "type": "validation",
                    "check": check["name"],
                    "message": check["message"]
                })

        grounding_issues = getattr(
            self,
            "grounding_issues",
            []
        )

        issues.extend(grounding_issues)

        return issues
        def save_json(
            self,
            output_path: str
        ) -> str:

            result = self.evaluate()

            output_path = Path(output_path)
            output_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    result,
                    file,
                    indent=2,
                    ensure_ascii=False
                )

            return str(output_path)
    def save_json(self, output_path: str) -> str:
        """Save the evaluation result as a JSON file."""

        result = self.evaluate()

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                result,
                file,
                indent=2,
                ensure_ascii=False
            )

        return str(output_path)