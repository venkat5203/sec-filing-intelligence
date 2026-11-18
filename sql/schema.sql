CREATE TABLE IF NOT EXISTS sec_filings (
  accession TEXT PRIMARY KEY,
  cik TEXT NOT NULL,
  company TEXT NOT NULL,
  ticker TEXT,
  form TEXT NOT NULL,
  filing_date DATE NOT NULL,
  report_period DATE,
  primary_document TEXT NOT NULL,
  primary_doc_bytes INTEGER,
  filing_url TEXT NOT NULL,
  index_url TEXT NOT NULL,
  source TEXT NOT NULL DEFAULT 'U.S. SEC EDGAR'
);
CREATE INDEX IF NOT EXISTS idx_sec_filings_ticker ON sec_filings(ticker);
CREATE INDEX IF NOT EXISTS idx_sec_filings_filing_date ON sec_filings(filing_date);
