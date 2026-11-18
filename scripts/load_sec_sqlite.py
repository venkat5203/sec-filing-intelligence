from __future__ import annotations
import argparse, json, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    parser = argparse.ArgumentParser(description="Load source-linked SEC EDGAR filing metadata into SQLite")
    parser.add_argument("--input", default="data/verified_sec_filings.json", help="SEC records JSON file")
    parser.add_argument("--db", default="data/sec_edgar.sqlite", help="SQLite database path")
    args = parser.parse_args()
    source = (ROOT / args.input).resolve()
    db_path = (ROOT / args.db).resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    rows = payload.get("records", [])
    if not rows:
        raise SystemExit(f"No filing records found in {source}")
    schema = (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as con:
        con.executescript(schema)
        con.executemany(
            """INSERT OR REPLACE INTO sec_filings
            (accession,cik,company,ticker,form,filing_date,report_period,primary_document,primary_doc_bytes,filing_url,index_url,source)
            VALUES (:accession,:cik,:company,:ticker,:form,:filing_date,:report_period,:primary_document,:primary_doc_bytes,:filing_url,:index_url,:source)""",
            rows,
        )
        count = con.execute("SELECT COUNT(*) FROM sec_filings").fetchone()[0]
    print(f"Loaded {len(rows):,} source-linked SEC filing records. Database now contains {count:,} records: {db_path}")

if __name__ == "__main__":
    main()
