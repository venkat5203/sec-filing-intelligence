from __future__ import annotations
import argparse, csv, json, os, sys
from pathlib import Path
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.sec_edgar import fetch_recent_filings, DEFAULT_CIKS

def main():
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description="Refresh actual public filing metadata from SEC EDGAR")
    parser.add_argument("--forms", nargs="+", default=["10-K", "10-Q"], choices=["10-K", "10-Q"])
    parser.add_argument("--per-company", type=int, default=5)
    parser.add_argument("--ciks", nargs="*", default=list(DEFAULT_CIKS))
    args = parser.parse_args()
    rows = fetch_recent_filings(args.ciks, tuple(args.forms), args.per_company)
    if not rows:
        raise SystemExit("No SEC filings were returned. Check the CIK list and SEC_USER_AGENT.")
    out_csv = ROOT / "data" / "live_sec_filings.csv"
    out_json = ROOT / "data" / "live_sec_filings.json"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    out_json.write_text(json.dumps({"source":"SEC EDGAR API","records":rows}, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows):,} live filing records to {out_csv} and {out_json}")

if __name__ == "__main__": main()
