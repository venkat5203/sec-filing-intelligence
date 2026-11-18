# SEC Filing Intelligence & Document Analytics

**A real-data portfolio project using publicly filed SEC EDGAR annual reports.**

[Open the interactive browser dashboard](./dashboard.html) · [Open the portfolio website](./index.html)

## Why this is real data

The repository snapshot contains **7 real Form 10-K filings from 7 public issuers**. Every row includes a company CIK, ticker, filing date, reporting period, accession number, primary-document URL, filing-index URL, and SEC source link. The snapshot was checked on **18 November 2026**. These are actual SEC EDGAR filings, not generated supplier records. See [`SEC_SOURCE_REGISTER.md`](SEC_SOURCE_REGISTER.md).

The repository does not rehost full filing documents. The static dashboard links directly to SEC originals. The Python workflow can fetch the original HTML at runtime, analyze the document structure, and retain compact metrics rather than full source text.

## Project objective

Build a reproducible document intelligence workflow that: (1) ingests real public filing metadata, (2) retrieves the original 10-K/10-Q HTML, (3) extracts text, (4) detects common filing sections, (5) calculates transparent document-quality and keyword metrics, (6) supports SQL analysis and an interactive dashboard, and (7) optionally uses an LLM to draft a sourced synopsis for human review.

## Verified source snapshot

| Metric | Value |
|---|---:|
| Real SEC filings in static snapshot | 7 |
| Unique issuers | 7 |
| Filing form | 10-K |
| Snapshot date | 2026-11-18 |
| Earliest filing date | 2026-01-29 |
| Latest filing date | 2026-11-03 |

The snapshot is a selected portfolio sample, not a complete universe of public-company filings. Use the live refresh tool to retrieve current filings for the configured CIKs.

## Technology

- Python, pandas, requests, BeautifulSoup
- SEC EDGAR submissions API and SEC Archives filing documents
- SQL / SQLite-ready schema and queries
- Streamlit and Plotly
- HTML, CSS, JavaScript for a GitHub Pages dashboard
- Optional OpenAI Responses API for LLM-assisted section summaries

## Repository structure

```text
.
├── index.html                      # Personal portfolio landing page
├── dashboard.html                  # Browser dashboard for real SEC snapshot
├── dashboard-static.js             # Filters, charts, table, CSV export
├── dashboard-static.css            # Dashboard styling
├── dashboard/app.py                # Python-backed live dashboard
├── assets/sec_filings.json         # Real SEC metadata snapshot for GitHub Pages
├── data/verified_sec_filings.csv   # Real SEC metadata snapshot
├── data/verified_sec_filings.json  # Source metadata and links
├── scripts/refresh_sec_data.py     # Live SEC API metadata refresh
├── scripts/analyze_selected_filings.py # Fetch and analyze original filings
├── scripts/load_sec_sqlite.py      # Load real SEC metadata into SQLite
├── src/sec_edgar.py                # SEC API client and HTML analysis
├── src/ai_analysis.py              # Optional LLM synopsis
├── sql/schema.sql                  # Filing table schema
├── sql/analysis_queries.sql        # Analysis and quality queries
├── prompts/sec_filing_analysis.md  # LLM prompt and evaluation guide
├── tests/                          # Automated parser tests
└── SEC_SOURCE_REGISTER.md          # Official source register
```

## Run locally

1. Install Python 3.10+ and create a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`. Set `SEC_USER_AGENT` to an identifying app name and a contact email you control. Example: `SEC_USER_AGENT=PortfolioAnalytics your-email@example.com`.
4. Start the app: `streamlit run dashboard/app.py`.
5. In the sidebar, choose **Refresh from live SEC API** to load the latest 10-K/10-Q metadata for the selected companies.
6. Open **Document Analysis**, select a filing, and choose **Fetch filing and run deterministic analysis**. The app fetches the original HTML from SEC; it does not pretend that text has already been downloaded in the static snapshot.

The initial view loads the verified real-data snapshot without a network call. Live refresh and document analysis require internet access. SEC public data endpoints do not require an API key, but automated requests must identify the client and follow SEC fair-access guidance.

## Refresh data from the command line

```bash
cp .env.example .env
# Edit .env and set SEC_USER_AGENT
python scripts/refresh_sec_data.py --forms 10-K 10-Q --per-company 5
```

This writes `data/live_sec_filings.csv` and `data/live_sec_filings.json`. Run the app to explore them, or copy the chosen verified snapshot into the static site assets if you want to update GitHub Pages.

## Load real SEC metadata into SQLite

```bash
python scripts/load_sec_sqlite.py
```

The script loads the included seven source-verified SEC filing records into `data/sec_edgar.sqlite`. To load newly refreshed metadata instead, pass `--input data/live_sec_filings.json`. The SQLite file is a local generated output and is excluded from Git.

## Analyze the selected filing set

```bash
python scripts/analyze_selected_filings.py --limit 7
```

This fetches the official primary-document HTML and calculates word count, common section presence/word counts, and selected keyword frequencies. It saves only derived analysis metadata to `data/filing_analysis.json`; the original HTML is not copied into this repository.

## Optional LLM analysis

Set `OPENAI_API_KEY` privately in your local `.env` or deployment secret store. The app then enables an optional synopsis of the risk-factor section. API usage may incur charges. Never commit secrets or submit confidential employer/customer records. LLM output is an assistive draft and must be checked against the original SEC source.

## GitHub Pages deployment

1. Create a public GitHub repository, for example `sec-filing-intelligence`.
2. Upload the repository contents to the root of the `main` branch.
3. Open **Settings → Pages**. Select **Deploy from a branch**, branch `main`, folder `/(root)`, then save.
4. After the Pages build completes, the portfolio will be at `https://YOUR_USERNAME.github.io/REPOSITORY/` and the browser dashboard at `https://YOUR_USERNAME.github.io/REPOSITORY/dashboard.html`.

GitHub Pages runs the static HTML/JavaScript dashboard only. It cannot execute Python or call the SEC API server-side. Use Streamlit Community Cloud for the live Python dashboard; configure `SEC_USER_AGENT` in its Secrets settings.

## LinkedIn positioning

Use the wording in [`LINKEDIN_LAUNCH_POST.md`](LINKEDIN_LAUNCH_POST.md). Describe this as a project using **real public SEC filings**. Do not claim this dataset came from ARDEM, Amazon employment systems, or private business operations.

## Important limitations

- The seven-row static snapshot is real but deliberately small and selected; it is not statistically representative.
- Section extraction is heuristic. SEC filings vary in layout and heading wording; false positives and missed sections are possible.
- Keyword counts measure mentions, not sentiment, severity, compliance, or materiality.
- LLM summaries can omit or misstate information; validate every point against the original source.
- The project demonstrates document analytics. It is not legal, accounting, investment, or compliance advice.

## Sources

- [SEC EDGAR API documentation](https://www.sec.gov/edgar/sec-api-documentation)
- [SEC Accessing EDGAR Data](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)
- [SEC Developer Resources](https://www.sec.gov/developer)
