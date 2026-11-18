from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.sec_edgar import fetch_filing_html, analyze_filing_html, SECError

def main():
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description="Analyze selected filing URLs from the verified SEC snapshot")
    parser.add_argument("--limit", type=int, default=7)
    args = parser.parse_args()
    source = json.loads((ROOT / "data" / "verified_sec_filings.json").read_text(encoding="utf-8"))
    results = []
    for row in source["records"][:max(1,args.limit)]:
        print(f"Fetching {row['ticker']} {row['form']} filed {row['filing_date']}...")
        html = fetch_filing_html(row["filing_url"])
        result = {k: row[k] for k in ["company","ticker","form","filing_date","report_period","accession","filing_url"]}
        result.update(analyze_filing_html(html))
        results.append(result)
        time.sleep(0.15)
    output = ROOT / "data" / "filing_analysis.json"
    output.write_text(json.dumps({"source":"SEC EDGAR primary filing documents","analyzed_on":time.strftime("%Y-%m-%d"),"records":results}, indent=2), encoding="utf-8")
    print(f"Saved analysis metadata to {output}. Original filing HTML was not copied into the repository.")

if __name__ == "__main__": main()
