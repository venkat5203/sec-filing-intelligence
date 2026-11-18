-- 1. Filings by issuer and form
SELECT ticker, company, form, COUNT(*) AS filing_count
FROM sec_filings GROUP BY ticker, company, form ORDER BY filing_count DESC;

-- 2. Monthly filing volume
SELECT substr(filing_date, 1, 7) AS filing_month, COUNT(*) AS filings
FROM sec_filings GROUP BY filing_month ORDER BY filing_month;

-- 3. Largest primary filing documents
SELECT ticker, company, filing_date, ROUND(primary_doc_bytes / 1048576.0, 2) AS primary_doc_mb
FROM sec_filings WHERE primary_doc_bytes IS NOT NULL ORDER BY primary_doc_bytes DESC;

-- 4. Metadata quality: identify incomplete source records
SELECT accession, ticker,
       CASE WHEN cik IS NULL OR cik = '' THEN 1 ELSE 0 END AS missing_cik,
       CASE WHEN filing_date IS NULL OR filing_date = '' THEN 1 ELSE 0 END AS missing_filing_date,
       CASE WHEN primary_document IS NULL OR primary_document = '' THEN 1 ELSE 0 END AS missing_primary_document,
       CASE WHEN filing_url IS NULL OR filing_url = '' THEN 1 ELSE 0 END AS missing_document_url
FROM sec_filings
WHERE cik IS NULL OR cik = '' OR filing_date IS NULL OR filing_date = ''
   OR primary_document IS NULL OR primary_document = '' OR filing_url IS NULL OR filing_url = '';
