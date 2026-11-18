# Project Case Study: SEC Filing Intelligence & Document Analytics

## Business problem
Public companies submit long regulatory documents that are difficult to compare at scale. Analysts need to locate the right filing, identify key sections, check document completeness, and turn unstructured text into reviewable signals.

## Objective
Build a reproducible workflow over actual public SEC EDGAR filings: retrieve real filing metadata, fetch original filing HTML, extract and inspect text sections, calculate transparent document-quality metrics, and provide SQL/dashboard analysis.

## Dataset and provenance
The static snapshot contains seven real 10-K filings from Apple, Amazon, Meta, Microsoft, NVIDIA, FactSet, and Micron. Each record includes CIK, ticker, accession number, filing date, reporting period, primary document URL, filing index URL, and SEC source register. Snapshot date: 18 November 2026. See `SEC_SOURCE_REGISTER.md` for the official links.

## Workflow
`SEC submissions API → filing metadata → primary SEC HTML → text normalization → section detection → word/keyword metrics → SQL analysis → dashboard → optional LLM synopsis with human verification`

## Data processing
- Retrieve submissions history from `data.sec.gov/submissions/CIK##########.json`.
- Select 10-K and 10-Q forms and create the original filing URL from CIK, accession number, and primary document path.
- Fetch the original document HTML only when the user requests document analysis.
- Parse HTML into normalized text and detect common 10-K sections (Business, Risk Factors, Cybersecurity, MD&A, Financial Statements, Controls).
- Calculate total word count, section presence/word counts, and mentions of AI, cybersecurity, privacy, and cloud terminology.
- Retain derived metrics, not copies of full SEC filing text.

## Analytics and dashboard
The GitHub Pages dashboard provides issuer/year/form filters, filing counts, primary-document size comparisons, filing-date timeline, a searchable record table, direct SEC links, and CSV export. The Streamlit app adds live SEC refresh and on-demand document analysis.

## AI component
An optional LLM synopsis can summarize a selected filing section, list disclosed themes, and identify statements requiring manual verification. The prompt requires source-grounded claims and separates issuer disclosure from model interpretation. The AI feature is optional; deterministic extraction works without an API key.

## Data quality controls
- Required metadata-field completeness.
- CIK and accession structure checks.
- Filing form validation (10-K / 10-Q).
- Filing date and reporting-period parse checks.
- Primary document and index URL presence.
- Document text length and section-detection checks after retrieval.

## Evidence and claims
The static snapshot contains seven source-verified SEC filing records from seven issuers. Full-document section and keyword metrics are calculated on demand by retrieving each original SEC HTML document. Run `python scripts/analyze_selected_filings.py` to generate measured results. Do not attribute this public dataset to employer systems or claim unmeasured efficiency improvements.

## Limitations
Section-heading detection is heuristic and may miss issuer-specific formatting. Keyword counts are only indicators of mention frequency. LLM output can hallucinate or omit content and must be checked against the primary SEC filing. The seven-filing snapshot is a selected example, not a representative or exhaustive sample.
