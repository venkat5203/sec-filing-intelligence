"""Fetch and analyze real public SEC EDGAR filing data.

SEC Fair Access: identify the application with a descriptive User-Agent and
keep request rates conservative. The repository snapshot is a point-in-time
set of verified filings; this client refreshes it from SEC submissions APIs.
"""
from __future__ import annotations

import os
import re
import time
from typing import Any
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

SEC_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"
DEFAULT_CIKS = {
    "0000320193": "Apple Inc.",
    "0001018724": "Amazon.com, Inc.",
    "0001326801": "Meta Platforms, Inc.",
    "0000789019": "Microsoft Corporation",
    "0001045810": "NVIDIA Corporation",
    "0001013237": "FactSet Research Systems Inc.",
    "0000723125": "Micron Technology, Inc.",
}
DEFAULT_TICKERS = {
    "0000320193": "AAPL", "0001018724": "AMZN", "0001326801": "META",
    "0000789019": "MSFT", "0001045810": "NVDA", "0001013237": "FDS",
    "0000723125": "MU",
}

class SECError(RuntimeError):
    """Raised when SEC data cannot be retrieved or parsed."""


def sec_headers(user_agent: str | None = None) -> dict[str, str]:
    agent = (user_agent or os.getenv("SEC_USER_AGENT", "")).strip()
    if not agent or "@" not in agent:
        raise SECError("Set SEC_USER_AGENT to an app name and contact email, for example 'PortfolioApp contact@example.com'.")
    return {"User-Agent": agent, "Accept-Encoding": "gzip, deflate", "Host": "www.sec.gov"}


def _get_json(url: str, user_agent: str | None = None) -> dict[str, Any]:
    headers = sec_headers(user_agent)
    headers.pop("Host", None)
    try:
        response = requests.get(url, headers=headers, timeout=35)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise SECError(f"SEC request failed for {url}: {exc}") from exc
    except ValueError as exc:
        raise SECError(f"SEC returned non-JSON data for {url}") from exc


def fetch_recent_filings(ciks: list[str] | None = None, forms: tuple[str, ...] = ("10-K", "10-Q"), per_company: int = 5, user_agent: str | None = None) -> list[dict[str, Any]]:
    """Read actual filing metadata from the SEC submissions API."""
    ciks = [str(c).zfill(10) for c in (ciks or list(DEFAULT_CIKS))]
    out: list[dict[str, Any]] = []
    for pos, cik in enumerate(ciks):
        if pos:
            time.sleep(0.15)  # conservative sequential request pacing
        payload = _get_json(SEC_SUBMISSIONS.format(cik=cik), user_agent)
        company = payload.get("name") or DEFAULT_CIKS.get(cik, cik)
        recent = payload.get("filings", {}).get("recent", {})
        forms_col = recent.get("form", [])
        accs = recent.get("accessionNumber", [])
        dates = recent.get("filingDate", [])
        report_dates = recent.get("reportDate", [])
        docs = recent.get("primaryDocument", [])
        sizes = recent.get("primaryDocDescription", [])
        added = 0
        for i, form in enumerate(forms_col):
            if form not in forms:
                continue
            accession = accs[i]
            compact = accession.replace("-", "")
            primary = docs[i] if i < len(docs) else ""
            if not primary:
                continue
            url = f"{SEC_ARCHIVES}/{int(cik)}/{compact}/{quote(primary)}"
            index_url = f"{SEC_ARCHIVES}/{int(cik)}/{compact}/{accession}-index.html"
            out.append({
                "company": company, "ticker": DEFAULT_TICKERS.get(cik, ""), "cik": cik, "form": form,
                "filing_date": dates[i], "report_period": report_dates[i] if i < len(report_dates) else "",
                "accession": accession, "accession_compact": compact,
                "primary_document": primary, "primary_doc_bytes": None,
                "documents_count": None, "industry": "",
                "filing_url": url, "index_url": index_url, "source": "U.S. SEC EDGAR",
                "source_snapshot_date": time.strftime("%Y-%m-%d"), "metadata_complete": bool(company and cik and form and dates[i] and accession and primary),
            })
            added += 1
            if added >= per_company:
                break
    return sorted(out, key=lambda r: r.get("filing_date", ""), reverse=True)


def fetch_filing_html(url: str, user_agent: str | None = None) -> str:
    """Download the original public filing HTML for in-memory analysis only."""
    headers = sec_headers(user_agent)
    headers.pop("Host", None)
    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or "utf-8"
        return response.text
    except requests.RequestException as exc:
        raise SECError(f"Could not download filing: {exc}") from exc


SECTION_PATTERNS = {
    "Item 1 - Business": r"\bITEM\s+1\.?\s+BUSINESS\b",
    "Item 1A - Risk Factors": r"\bITEM\s+1A\.?\s+RISK\s+FACTORS\b",
    "Item 1C - Cybersecurity": r"\bITEM\s+1C\.?\s+CYBERSECURITY\b",
    "Item 7 - MD&A": r"\bITEM\s+7\.?\s+MANAGEMENT.{0,8}S\s+DISCUSSION\s+AND\s+ANALYSIS\b",
    "Item 8 - Financial Statements": r"\bITEM\s+8\.?\s+FINANCIAL\s+STATEMENTS\b",
    "Item 9A - Controls": r"\bITEM\s+9A\.?\s+CONTROLS\s+AND\s+PROCEDURES\b",
}


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "ix:header", "ix:hidden"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def analyze_filing_html(html: str) -> dict[str, Any]:
    """Create compact, factual document-quality metrics; never retain full filing text."""
    text = html_to_text(html)
    sections: dict[str, dict[str, Any]] = {}
    matches: list[tuple[int, str]] = []
    for label, pattern in SECTION_PATTERNS.items():
        found = list(re.finditer(pattern, text, flags=re.IGNORECASE))
        # Contents pages may repeat a heading. Use the final occurrence as a
        # pragmatic start marker for the body section, then bound by next marker.
        if found:
            match = found[-1]
            matches.append((match.start(), label))
            sections[label] = {"present": True, "occurrences": len(found), "word_count": None}
        else:
            sections[label] = {"present": False, "occurrences": 0, "word_count": 0}
    matches.sort()
    for idx, (start, label) in enumerate(matches):
        end = matches[idx + 1][0] if idx + 1 < len(matches) else min(len(text), start + 250000)
        section_text = text[start:end]
        sections[label]["word_count"] = len(re.findall(r"\b[\w'-]+\b", section_text))
    keywords = {
        "artificial_intelligence": r"\bartificial intelligence\b|\bmachine learning\b|\bgenerative AI\b",
        "cybersecurity": r"\bcybersecurity\b|\bcyber security\b|\binformation security\b",
        "data_privacy": r"\bprivacy\b|\bpersonal information\b|\bdata protection\b",
        "cloud": r"\bcloud computing\b|\bcloud services\b|\bcloud infrastructure\b",
    }
    keyword_counts = {k: len(re.findall(p, text, flags=re.IGNORECASE)) for k, p in keywords.items()}
    section_count = sum(1 for v in sections.values() if v["present"])
    return {
        "document_word_count": len(re.findall(r"\b[\w'-]+\b", text)),
        "document_char_count": len(text),
        "sections_detected": section_count,
        "section_count_checked": len(SECTION_PATTERNS),
        "sections": sections,
        "keyword_counts": keyword_counts,
        "analysis_method": "Deterministic HTML text and heading analysis; not an AI-generated legal interpretation.",
    }


def extract_filing_section(html: str, section_label: str, max_chars: int = 80000) -> str:
    """Extract one section from a public filing for optional human/LLM review.

    Uses the final occurrence of the requested heading to reduce table-of-
    contents false positives, then stops at the next known section heading.
    The result is returned in memory and should not be committed as raw filing text.
    """
    if section_label not in SECTION_PATTERNS:
        raise ValueError(f"Unknown filing section: {section_label}")
    text = html_to_text(html)
    target_matches = list(re.finditer(SECTION_PATTERNS[section_label], text, flags=re.IGNORECASE))
    if not target_matches:
        return ""
    start = target_matches[-1].start()
    next_starts = []
    for label, pattern in SECTION_PATTERNS.items():
        if label == section_label:
            continue
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            if match.start() > start:
                next_starts.append(match.start())
    # Risk Factors normally ends before Item 1B/1C, which may not appear in
    # the compact list above. Include these boundary headings explicitly.
    if section_label == "Item 1A - Risk Factors":
        boundary = re.compile(r"\bITEM\s+(?:1B|1C|2)\.?\s+[A-Z]", re.IGNORECASE)
        for match in boundary.finditer(text, start + 1):
            next_starts.append(match.start())
    end = min(next_starts) if next_starts else min(len(text), start + max_chars)
    end = min(end, start + max_chars)
    return text[start:end].strip()
