from src.template_analyzer import TemplateAnalyzer




def test_template_analyzer():

    analyzer = TemplateAnalyzer(
        "input/02 Affidavit in Reply Sample.docx.pdf"
    )

    template = analyzer.analyze_structure()

    assert template["document_type"] == "Affidavit in Reply"

    section_names = [
        section["name"]
        for section in template["sections"]
    ]

    assert "court_heading" in section_names
    assert "case_details" in section_names
    assert "cause_title" in section_names
    assert "reply_paragraphs" in section_names
    assert "prayer" in section_names
    assert "verification" in section_names