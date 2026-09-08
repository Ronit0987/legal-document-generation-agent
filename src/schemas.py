from typing import List, Optional
from pydantic import BaseModel


class Header(BaseModel):
    court: str
    jurisdiction: str
    proceeding_type: str
    case_number: str
    year: str


class Parties(BaseModel):
    petitioner: str
    respondent_1: str
    respondent_2: str


class Deponent(BaseModel):
    name: str
    designation: str
    organisation: str
    address: str
    capacity: str


class ReplyParagraph(BaseModel):
    number: int
    content: str


class Exhibit(BaseModel):
    label: str
    description: str
    date: Optional[str] = None


class Attestation(BaseModel):
    place: str
    date: str


class Verification(BaseModel):
    deponent: str
    paragraph_start: int
    paragraph_end: int
    includes_prayer: bool
    place: str
    date: str


class Advocate(BaseModel):
    firm: str
    representing: str


class Affidavit(BaseModel):
    document_type: str
    header: Header
    parties: Parties
    filed_on_behalf_of: str
    affidavit_title: str
    deponent: Deponent
    reply_paragraphs: List[ReplyParagraph]
    exhibits: List[Exhibit]
    prayer: List[str]
    attestation: Attestation
    verification: Verification
    advocate: Advocate