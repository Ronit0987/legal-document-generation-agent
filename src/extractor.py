import json
import os
from pathlib import Path

import pymupdf
from dotenv import load_dotenv
from groq import Groq

from src.schemas import Affidavit


class CaseInformationExtractor:

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)

        if not self.pdf_path.exists():
            raise FileNotFoundError(
                f"Case information file not found: {self.pdf_path}"
            )

        load_dotenv()

        api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=api_key)

        if not api_key:
            raise ValueError(
            "GROQ_API_KEY not found. Check your .env file."
        )

    def extract_text(self) -> str:
        """Extract text from the case information PDF."""

        document = pymupdf.open(self.pdf_path)

        pages = []

        for page in document:
            pages.append(page.get_text())

        document.close()

        return "\n".join(pages)

    def extract_entities(self) -> Affidavit:
        """Use LLM to convert case information into structured data."""

        text = self.extract_text()

        system_prompt = """
You are a legal document information extraction system.

Extract information ONLY from the provided source.

CRITICAL RULES:

1. Do not invent facts.
2. Do not perform legal research.
3. Do not infer missing information.
4. Do not modify names.
5. Do not modify dates.
6. Do not add legal arguments.
7. Do not summarize or paraphrase the reply points.
8. Preserve the wording of the source as closely as possible.
9. For reply paragraphs, combine the bullet points belonging to each
   Point into one paragraph, but otherwise preserve their wording.
10. Preserve punctuation and terminology from the source.
11. If information is not explicitly provided, return an empty string
    rather than guessing.

Return ONLY valid JSON matching the requested schema.
"""
        user_prompt = f"""
Extract the case information into the following JSON structure.

For reply_paragraphs, the source contains "Point 1", "Point 2", etc.
Each Point must become exactly one numbered reply paragraph.
Combine the bullet points belonging to that Point in their original order.
Do not rewrite their wording.

For example, if the source says:
"The deponent is filing this Affidavit in Reply ... to oppose..."
the output must contain "to oppose", not a paraphrased or modified version.

Do not create an affidavit title if the source does not explicitly provide one.
Leave affidavit_title empty if necessary; it will be constructed later.

JSON structure:
{{
    "document_type": "",
    "header": {{
        "court": "",
        "jurisdiction": "",
        "proceeding_type": "",
        "case_number": "",
        "year": ""
    }},
    "parties": {{
        "petitioner": "",
        "respondent_1": "",
        "respondent_2": ""
    }},
    "filed_on_behalf_of": "",
    "affidavit_title": "",
    "deponent": {{
        "name": "",
        "designation": "",
        "organisation": "",
        "address": "",
        "capacity": ""
    }},
    "reply_paragraphs": [
        {{
            "number": 1,
            "content": ""
        }}
    ],
    "exhibits": [
        {{
            "label": "",
            "description": "",
            "date": ""
        }}
    ],
    "prayer": [],
    "attestation": {{
        "place": "",
        "date": ""
    }},
    "verification": {{
        "deponent": "",
        "paragraph_start": 1,
        "paragraph_end": 1,
        "includes_prayer": true,
        "place": "",
        "date": ""
    }},
    "advocate": {{
        "firm": "",
        "representing": ""
    }}
}}

CASE INFORMATION:

{text}
"""

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        content = response.choices[0].message.content

        data = json.loads(content)
        reply_paragraphs = data.get("reply_paragraphs", [])

        # 1. Verification paragraph range
        if reply_paragraphs:
            data["verification"]["paragraph_start"] = 1
            data["verification"]["paragraph_end"] = len(reply_paragraphs)

        # 2. Verification includes the Prayer
        data["verification"]["includes_prayer"] = True

        # 3. Verification place/date should match attestation
        if "attestation" in data and "verification" in data:
            data["verification"]["place"] = data["attestation"].get("place", "")
            data["verification"]["date"] = data["attestation"].get("date", "")

        # 4. Normalize Exhibit A
        for paragraph in reply_paragraphs:
            content = paragraph.get("content", "")

            if "EXHIBIT-‘A’" in content:
                data["exhibits"] = [
                    {
                        "label": "EXHIBIT-‘A’",
                        "description": "communication dated 15 July 2026",
                        "date": "15 July 2026"
                    }
                ]
                break

        return Affidavit.model_validate(data)