# Legal Document Generation & Evaluation Agent

An AI-powered pipeline for generating and evaluating an **Affidavit in Reply** from structured case information while preserving the structure and style of a reference affidavit.

The system extracts case facts from a PDF, maps them into a structured schema, generates a `.docx` affidavit, runs deterministic validation checks, and produces an evaluation report with source-grounding analysis.

## Features

- Extracts legal entities and case facts from PDF documents
- Uses a reference affidavit to understand expected document structure
- Generates an **Affidavit in Reply** in `.docx` format
- Uses structured Pydantic models as an intermediate representation
- Runs deterministic validation checks
- Evaluates entity accuracy, completeness, structure, consistency, template fidelity, and source grounding
- Provides a Streamlit UI for end-to-end use
- Generates downloadable affidavit and evaluation report

## Architecture

```text
Reference Affidavit PDF
        |
        v
Template Analyzer
        |
        v
Template Structure

Case Information PDF
        |
        v
Text Extraction
        |
        v
Groq LLM Entity Extraction
        |
        v
Pydantic Structured Affidavit
        |
        v
Deterministic Normalization
        |
        v
Document Mapper
        |
        v
DOCX Generator
        |
        v
Deterministic Validator
        |
        v
Evaluation Engine
        |
        +--> generated_affidavit.docx
        |
        +--> evaluation_report.json
```

The design follows a simple principle:

> **LLM = understand and extract language; Python = enforce structure, validation, and correctness.**

## Tech Stack

- Python
- Streamlit
- Groq API
- `openai/gpt-oss-120b`
- PyMuPDF
- python-docx
- Pydantic
- python-dotenv
- pytest

## Project Structure

```text
legal-document-generation-agent/
├── input/
│   ├── 01 Affidavit Format Explained.pdf
│   ├── 02 Affidavit in Reply Sample.docx.pdf
│   └── 03_Case_Information.pdf
├── output/
│   ├── generated_affidavit.docx
│   └── evaluation_report.json
├── src/
│   ├── __init__.py
│   ├── schemas.py
│   ├── template_analyzer.py
│   ├── extractor.py
│   ├── mapper.py
│   ├── generator.py
│   ├── validator.py
│   └── evaluator.py
├── tests/
│   ├── test_template_analyzer.py
│   ├── test_extractor.py
│   ├── test_mapper.py
│   ├── test_generator.py
│   ├── test_validator.py
│   └── test_evaluator.py
├── app.py
├── main.py
├── pytest.ini
├── requirements.txt
├── .env.example
└── README.md
```

## How It Works

### 1. Template Understanding

The reference affidavit is parsed to identify the expected sections, including court heading, case number, cause title, affidavit title, deponent clause, numbered reply paragraphs, exhibit references, prayer, attestation, verification, and advocate block.

### 2. Entity Extraction

The case-information PDF is converted to text and sent to the Groq-hosted LLM. The model is instructed to use only the supplied case information, avoid independent legal research, avoid inventing facts, preserve supplied factual wording wherever possible, and return structured JSON matching the application schema.

### 3. Structured Intermediate Representation

The extracted response is validated using Pydantic models before document generation. This gives the pipeline a predictable intermediate representation instead of directly generating the final legal document from raw LLM output.

### 4. Document Generation

The structured case information is mapped into the reference affidavit structure and rendered as a Microsoft Word `.docx` document.

### 5. Deterministic Validation

The system performs six non-LLM checks:

1. Required fields are present
2. Reply paragraph numbering is sequential
3. Verification paragraph range matches the generated reply paragraphs
4. Declared exhibits are referenced in the reply
5. Respondent No. 2 is consistently referenced
6. Prayer section is present

### 6. Evaluation

The evaluator scores the generated affidavit across:

- **Entity Accuracy**
- **Completeness**
- **Structure**
- **Consistency**
- **Template Fidelity**
- **Source Grounding**

Source grounding checks extracted factual entities against the case-information source and compares generated reply paragraphs with the closest source passages. The report also flags passages that fall below the grounding threshold for manual review.

## Setup

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd legal-document-generation-agent
```

Create a virtual environment.

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your local environment file:

### Windows

```powershell
Copy-Item .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Add your Groq API key to `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## Run the CLI Pipeline

```bash
python main.py
```

Generated files are written to:

```text
output/generated_affidavit.docx
output/evaluation_report.json
```

## Run the Streamlit App

```bash
streamlit run app.py
```

Upload the reference affidavit PDF and case-information PDF. The app generates the affidavit, shows validation/evaluation results, and allows both outputs to be downloaded.

## Running Tests

```bash
pytest -v
```

## Environment Variables

The project requires:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Never commit your real `.env` file or API key.

## Deployment

The Streamlit application can be deployed using Streamlit Community Cloud.

Configure the deployment secret in Streamlit app settings:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

The API key should never be committed to the repository.

## Current Evaluation

The included generated artifact passes all deterministic validation checks.

Example evaluation:

```text
Validation Score: 100%
Overall Evaluation Score: ~99%
Source Grounding Score: ~97%
```

Grounding warnings are intentionally surfaced when generated reply language is not sufficiently similar to the underlying source passage rather than forcing every dimension to score 100%.

## Design Decisions

The LLM is used for language understanding and entity extraction, while deterministic Python logic handles paragraph numbering, verification ranges, exhibit consistency, mandatory fields, output structure, and evaluation. This reduces the risk of uncontrolled document generation.

The system performs no independent legal research because the generated affidavit is constrained to the supplied case information.

## Limitations

- Currently supports only **Affidavit in Reply**
- Source grounding uses textual similarity and should be treated as a review signal rather than a legal determination
- DOCX formatting follows the reference structure but is not intended to be pixel-perfect
- The application does not provide legal advice
- Generated legal documents should be reviewed by a qualified professional before actual use

## AI Assistance Disclosure

AI-assisted coding tools were used during development for implementation support, debugging, code review, and documentation.

The application itself uses a Groq-hosted language model for structured information extraction from the supplied case-information document.

## Outputs

The repository includes sample generated artifacts:

- `output/generated_affidavit.docx`
- `output/evaluation_report.json`

## Author

Ronit Mankani
