# Start here — SEC Filing Intelligence

This project is built on **real public company filings from SEC EDGAR**. The included snapshot contains seven actual Form 10-K filings, each linked to its original SEC filing page and filing index.

## Quick publication steps
1. Extract this ZIP.
2. Create a public GitHub repository named `sec-filing-intelligence`.
3. Upload the extracted project files to the repository root (not the ZIP file).
4. Open **Settings → Pages → Deploy from a branch → main → /(root)**.
5. Open the published website and append `/dashboard.html` for the interactive SEC filing dashboard.

## Run the live document workflow
1. Install Python 3.10+ and run `pip install -r requirements.txt`.
2. Copy `.env.example` to `.env`. Replace the example contact email in `SEC_USER_AGENT` with an email address you control.
3. Start `streamlit run dashboard/app.py`.
4. Click **Refresh from live SEC API** to retrieve current 10-K/10-Q filing metadata.
5. Open **Document Analysis**, select a filing, and click **Fetch filing and run deterministic analysis**. The app downloads the original SEC HTML and calculates document/section metrics.
6. For SQL practice, run `python scripts/load_sec_sqlite.py`, then use the queries in `sql/analysis_queries.sql`.

## What is real, and what runs live
- The seven included filing metadata records are real and link to the official SEC EDGAR documents.
- The static GitHub Pages dashboard visualizes those seven source-verified filing records.
- The Streamlit app can refresh current records and retrieve original filing text when deployed or run on a machine with internet access.
- The optional LLM synopsis requires your own private API key. Deterministic extraction, validation, metadata analysis, and SQL loading do not require an AI key.

The SEC data is public. Do not upload confidential employer/customer records or secrets.
