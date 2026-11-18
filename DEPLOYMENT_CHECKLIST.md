# Deployment checklist

## GitHub Pages (static site)
- [ ] Create a public repository, e.g. `sec-filing-intelligence`.
- [ ] Upload the extracted project files to the repository root.
- [ ] Confirm `assets/sec_filings.json` is present.
- [ ] Enable Pages from `main` / `/(root)`.
- [ ] Open the portfolio page and `/dashboard.html`.
- [ ] Test issuer, year, and form filters.
- [ ] Test search, official SEC links, and CSV export.

## Streamlit (live data and document analysis)
- [ ] Deploy `dashboard/app.py` from this repository.
- [ ] Add `SEC_USER_AGENT` under deployment secrets. The value must identify the app and contain a working contact email.
- [ ] Test live SEC metadata refresh.
- [ ] Test on-demand retrieval and analysis of a public filing.
- [ ] Configure `OPENAI_API_KEY` privately only if the optional LLM synopsis is needed.

## Before sharing
- [ ] Keep the SEC source register and original filing links.
- [ ] Do not add private employer/customer records or API keys.
- [ ] Do not claim the selected seven filings represent all public companies.
- [ ] Do not claim AI summaries are audited or authoritative.
- [ ] Keep LinkedIn metrics consistent with the actual live project output.
