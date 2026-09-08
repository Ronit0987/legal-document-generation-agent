from typing import Dict, List, Any

from src.schemas import Affidavit
from src.mapper import AffidavitMapper


class AffidavitValidator:

    def __init__(self, affidavit: Affidavit):
        self.affidavit = affidavit
        self.mapped = AffidavitMapper(affidavit).map()

    def validate(self) -> Dict[str, Any]:

        checks = []

        checks.append(self._check_required_fields())
        checks.append(self._check_paragraph_sequence())
        checks.append(self._check_verification_range())
        checks.append(self._check_exhibit_consistency())
        checks.append(self._check_party_consistency())
        checks.append(self._check_prayer())

        passed = sum(1 for check in checks if check["passed"])
        total = len(checks)

        score = round((passed / total) * 100, 2)

        return {
            "score": score,
            "passed_checks": passed,
            "total_checks": total,
            "checks": checks
        }

    def _check_required_fields(self) -> Dict:
        required = [
            self.mapped["court"],
            self.mapped["jurisdiction"],
            self.mapped["case_reference"],
            self.mapped["petitioner"],
            self.mapped["respondent_1"],
            self.mapped["respondent_2"],
            self.mapped["affidavit_title"],
            self.mapped["deponent_name"]
        ]

        passed = all(
            value is not None and str(value).strip()
            for value in required
        )

        return {
            "name": "Required fields present",
            "passed": passed,
            "message": (
                "All required fields are present."
                if passed
                else "One or more required fields are missing."
            )
        }

    def _check_paragraph_sequence(self) -> Dict:
        numbers = [
            paragraph["number"]
            for paragraph in self.mapped["reply_paragraphs"]
        ]

        expected = list(range(1, len(numbers) + 1))

        passed = numbers == expected

        return {
            "name": "Reply paragraph numbering",
            "passed": passed,
            "message": (
                f"Paragraph sequence is valid: {numbers}"
                if passed
                else f"Expected {expected}, found {numbers}"
            )
        }

    def _check_verification_range(self) -> Dict:
        paragraph_count = len(
            self.mapped["reply_paragraphs"]
        )

        verification = self.affidavit.verification

        passed = (
            verification.paragraph_start == 1
            and verification.paragraph_end == paragraph_count
        )

        return {
            "name": "Verification paragraph range",
            "passed": passed,
            "message": (
                f"Verification correctly covers paragraphs "
                f"1 to {paragraph_count}."
                if passed
                else (
                    f"Verification range does not match "
                    f"{paragraph_count} reply paragraphs."
                )
            )
        }

    def _check_exhibit_consistency(self) -> Dict:

        exhibit_labels = [
            exhibit["label"]
            for exhibit in self.mapped["exhibits"]
        ]

        document_text = " ".join(
            paragraph["content"]
            for paragraph in self.mapped["reply_paragraphs"]
        )

        missing = [
            label
            for label in exhibit_labels
            if label not in document_text
        ]

        passed = len(missing) == 0

        return {
            "name": "Exhibit consistency",
            "passed": passed,
            "message": (
                "All declared exhibits are referenced "
                "in the reply paragraphs."
                if passed
                else f"Missing exhibit references: {missing}"
            )
        }

    def _check_party_consistency(self) -> Dict:

        respondent = self.mapped["respondent_2"]

        text = " ".join(
            paragraph["content"]
            for paragraph in self.mapped["reply_paragraphs"]
        )

        passed = respondent in text

        return {
            "name": "Respondent consistency",
            "passed": passed,
            "message": (
                "Respondent No. 2 is consistently referenced."
                if passed
                else (
                    "Respondent No. 2 entity is not referenced "
                    "in the reply body."
                )
            )
        }

    def _check_prayer(self) -> Dict:

        prayer = self.mapped["prayer"]

        passed = bool(
            prayer
            and any(item.strip() for item in prayer)
        )

        return {
            "name": "Prayer present",
            "passed": passed,
            "message": (
                "Prayer section is present."
                if passed
                else "Prayer section is missing."
            )
        }