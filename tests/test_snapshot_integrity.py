import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class RealSecSnapshotTests(unittest.TestCase):
    def test_snapshot_contains_only_source_linked_sec_filings(self):
        payload = json.loads((ROOT / "data" / "verified_sec_filings.json").read_text(encoding="utf-8"))
        records = payload["records"]
        self.assertEqual(len(records), 7)
        self.assertEqual(len({r["cik"] for r in records}), 7)
        for row in records:
            self.assertEqual(row["source"], "U.S. SEC EDGAR")
            self.assertEqual(row["form"], "10-K")
            self.assertTrue(row["filing_url"].startswith("https://www.sec.gov/Archives/edgar/data/"))
            self.assertTrue(row["index_url"].startswith("https://www.sec.gov/Archives/edgar/data/"))
            self.assertTrue(row["accession"] and row["primary_document"] and row["ticker"])

if __name__ == "__main__":
    unittest.main()
