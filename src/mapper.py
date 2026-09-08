from typing import Dict, Any

from src.schemas import Affidavit


class AffidavitMapper:
    def __init__(self, affidavit: Affidavit):
        self.affidavit = affidavit

    def map(self) -> Dict[str, Any]:
        a = self.affidavit

        affidavit_title = (
            f"AFFIDAVIT IN REPLY ON BEHALF OF "
            f"{a.filed_on_behalf_of.upper()}"
        )

        deponent_clause = (
            f"I, {a.deponent.name}, "
            f"{a.deponent.designation}, "
            f"{a.deponent.organisation}, "
            f"having office at {a.deponent.address}, "
            f"do hereby solemnly affirm and state as under:"
        )

        case_reference = (
            f"{a.header.proceeding_type} NO. "
            f"{a.header.case_number} OF {a.header.year}"
        )

        verification_text = self._build_verification()

        return {
            "document_type": a.document_type,

            "court": a.header.court,
            "jurisdiction": a.header.jurisdiction,
            "case_reference": case_reference,

            "petitioner": a.parties.petitioner,
            "respondent_1": a.parties.respondent_1,
            "respondent_2": a.parties.respondent_2,

            "filed_on_behalf_of": a.filed_on_behalf_of,
            "affidavit_title": affidavit_title,

            "deponent_name": a.deponent.name,
            "deponent_designation": a.deponent.designation,
            "deponent_organisation": a.deponent.organisation,
            "deponent_address": a.deponent.address,
            "deponent_clause": deponent_clause,

            "reply_paragraphs": [
                {
                    "number": paragraph.number,
                    "content": paragraph.content,
                }
                for paragraph in a.reply_paragraphs
            ],

            "exhibits": [
                {
                    "label": exhibit.label,
                    "description": exhibit.description,
                    "date": exhibit.date,
                }
                for exhibit in a.exhibits
            ],

            "prayer": a.prayer,

            "attestation": {
                "place": a.attestation.place,
                "date": a.attestation.date,
            },

            "verification": {
                "text": verification_text,
                "place": a.verification.place,
                "date": a.verification.date,
            },

            "advocate": {
                "firm": a.advocate.firm,
                "representing": a.advocate.representing,
            },
        }

    def _build_verification(self) -> str:
        v = self.affidavit.verification

        paragraph_range = (
            f"paragraphs {v.paragraph_start} to {v.paragraph_end}"
        )

        if v.includes_prayer:
            verified_content = f"{paragraph_range} and the Prayer"
        else:
            verified_content = paragraph_range

        return (
            f"I, {v.deponent}, the deponent above named, "
            f"do hereby verify that the contents of {verified_content} "
            f"are true and correct to my knowledge and belief."
        )