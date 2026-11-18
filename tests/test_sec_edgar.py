import unittest
from src.sec_edgar import html_to_text, analyze_filing_html, extract_filing_section, DEFAULT_CIKS, DEFAULT_TICKERS

class FilingParserTests(unittest.TestCase):
    def test_html_text_cleanup(self):
        text=html_to_text('<html><script>skip()</script><body><h1>ITEM 1. BUSINESS</h1><p>Real filing words here.</p></body></html>')
        self.assertIn('ITEM 1. BUSINESS',text)
        self.assertNotIn('skip()',text)
    def test_detects_common_10k_sections(self):
        html='''<html><body><h2>TABLE OF CONTENTS</h2>ITEM 1. BUSINESS ITEM 1A. RISK FACTORS ITEM 7. MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS ITEM 8. FINANCIAL STATEMENTS <h2>ITEM 1. BUSINESS</h2><p>Company operations and services.</p><h2>ITEM 1A. RISK FACTORS</h2><p>Risk and uncertainty disclosures.</p><h2>ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS</h2><p>Management discusses performance.</p><h2>ITEM 8. FINANCIAL STATEMENTS</h2><p>Consolidated financial statements.</p></body></html>'''
        result=analyze_filing_html(html)
        self.assertGreaterEqual(result['sections_detected'],4)
        self.assertGreater(result['document_word_count'],10)
        self.assertTrue(result['sections']['Item 1A - Risk Factors']['present'])
    def test_risk_section_extraction_stops_at_next_item(self):
        html = """<html><body><p>TABLE OF CONTENTS ITEM 1A. RISK FACTORS ITEM 1B. UNRESOLVED STAFF COMMENTS</p>
        <h2>ITEM 1A. RISK FACTORS</h2><p>Risk language unique to this section.</p>
        <h2>ITEM 1B. UNRESOLVED STAFF COMMENTS</h2><p>This later section must not be included.</p></body></html>"""
        excerpt = extract_filing_section(html, "Item 1A - Risk Factors")
        self.assertIn("Risk language unique", excerpt)
        self.assertNotIn("This later section", excerpt)

    def test_default_companies_have_tickers(self):
        self.assertEqual(len(DEFAULT_CIKS), 7)
        self.assertEqual(set(DEFAULT_CIKS), set(DEFAULT_TICKERS))

    def test_keyword_frequency_is_deterministic(self):
        result=analyze_filing_html('<p>AI and artificial intelligence. Cybersecurity. Privacy and cloud services.</p>')
        self.assertEqual(result['keyword_counts']['artificial_intelligence'],1)
        self.assertEqual(result['keyword_counts']['cybersecurity'],1)
        self.assertEqual(result['keyword_counts']['data_privacy'],1)
        self.assertEqual(result['keyword_counts']['cloud'],1)

if __name__=='__main__': unittest.main()
