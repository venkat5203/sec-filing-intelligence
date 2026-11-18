from __future__ import annotations
import json, os, sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")
from src.sec_edgar import fetch_recent_filings, fetch_filing_html, analyze_filing_html, extract_filing_section, DEFAULT_CIKS, SECError
from src.ai_analysis import summarize_section

st.set_page_config(page_title="SEC Filing Intelligence", page_icon="📊", layout="wide")
CSS = """<style>.stApp{background:#0b1220;color:#eaf2f8}.block-container{max-width:1400px;padding-top:2rem}.hero{padding:24px 26px;border:1px solid #26485a;background:linear-gradient(120deg,#102a28,#101d2b);border-radius:18px;margin-bottom:18px}.eyebrow{font:11px monospace;color:#63e6be;letter-spacing:.1em}.hero h1{font-size:36px;color:#f2f8fb;margin:.3rem 0}.hero p,.muted{color:#9bb0c2}.metric-card{background:#101d2b;border:1px solid #294055;border-radius:14px;padding:16px}.metric-card small{color:#8ba4b9;letter-spacing:.08em}.metric-card h2{font-size:30px;margin:7px 0;color:#f4f8fb}.stTabs [data-baseweb=tab-list]{gap:14px}.source-note{padding:12px;border:1px solid #35594c;background:#10251f;border-radius:10px;color:#bcebd8;font-size:13px}</style>"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
SNAPSHOT = ROOT / "data" / "verified_sec_filings.json"

def load_snapshot():
    obj=json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    return pd.DataFrame(obj["records"]), obj.get("snapshot_date","unknown")

def plot(fig):
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=45,b=10),height=340)
    return fig

if "filings" not in st.session_state:
    st.session_state.filings, st.session_state.snapshot_date = load_snapshot()

df=st.session_state.filings.copy()
st.markdown("<div class='hero'><div class='eyebrow'>PUBLIC DATA · SEC EDGAR</div><h1>SEC Filing Intelligence</h1><p>Real company filings, source-linked metadata, deterministic document analysis, and optional LLM-assisted summaries.</p></div>",unsafe_allow_html=True)
st.markdown(f"<div class='source-note'>Current view: {len(df):,} real SEC filing metadata records from a verified snapshot dated {st.session_state.snapshot_date}. Full filing HTML is retrieved from SEC only when you analyze a record; original files are not rehosted.</div>",unsafe_allow_html=True)

with st.sidebar:
    st.title("Explore EDGAR")
    user_agent=st.text_input("SEC User-Agent",value=os.getenv("SEC_USER_AGENT",""),help="Include your app name and contact email. SEC public API endpoints do not require an API key, but automated access must identify itself.")
    if st.button("Refresh from live SEC API",use_container_width=True):
        try:
            with st.spinner("Requesting latest 10-K and 10-Q records from SEC EDGAR..."):
                rows=fetch_recent_filings(list(DEFAULT_CIKS.keys()),("10-K","10-Q"),per_company=5,user_agent=user_agent)
            if not rows: st.warning("No filings were returned.")
            else:
                st.session_state.filings=pd.DataFrame(rows); st.session_state.snapshot_date=pd.Timestamp.now().strftime("%Y-%m-%d"); df=st.session_state.filings.copy(); st.success(f"Retrieved {len(rows)} actual SEC filing records.")
        except Exception as e: st.error(str(e))
    st.divider()
    companies=sorted(df.company.dropna().unique())
    selected=st.multiselect("Issuer",companies,default=companies)
    forms=sorted(df.form.dropna().unique())
    selected_forms=st.multiselect("Form type",forms,default=forms)
    years=sorted(df.filing_date.dropna().astype(str).str[:4].unique())
    selected_years=st.multiselect("Filing year",years,default=years)
    st.caption("Only public SEC filings. Refreshing uses the SEC submissions API and observes sequential request pacing.")

view=df[df.company.isin(selected)&df.form.isin(selected_forms)&df.filing_date.astype(str).str[:4].isin(selected_years)].copy()
if "primary_doc_bytes" in view:
    view["size_mb"] = pd.to_numeric(view.primary_doc_bytes,errors="coerce")/1048576
else: view["size_mb"]=None
k1,k2,k3,k4=st.columns(4)
for col,label,value in [(k1,"PUBLIC FILINGS",f"{len(view):,}"),(k2,"UNIQUE ISSUERS",f"{view.cik.nunique():,}"),(k3,"PRIMARY DOC SIZE",f"{view.primary_doc_bytes.fillna(0).sum()/1048576:,.1f} MB"),(k4,"METADATA COMPLETE",f"{view.metadata_complete.fillna(False).mean()*100:.0f}%" if len(view) else "—")]:
    col.markdown(f"<div class='metric-card'><small>{label}</small><h2>{value}</h2></div>",unsafe_allow_html=True)

summary,explorer,document,method=st.tabs(["Overview","Filing Explorer","Document Analysis","Methodology"])
with summary:
    c1,c2=st.columns(2)
    if len(view):
        with c1:
            st.plotly_chart(plot(px.bar(view.groupby("ticker",as_index=False).size().sort_values("size"),x="ticker",y="size",color="ticker",title="Filings by issuer")),use_container_width=True)
        with c2:
            size=view.dropna(subset=["size_mb"])
            st.plotly_chart(plot(px.bar(size.sort_values("size_mb"),x="size_mb",y="ticker",orientation="h",title="Primary document size (MB)",color="size_mb",color_continuous_scale="Tealgrn")),use_container_width=True)
        dates=view.groupby("filing_date",as_index=False).size()
        st.plotly_chart(plot(px.line(dates,x="filing_date",y="size",markers=True,title="Filing distribution by filing date")),use_container_width=True)
    else: st.info("Choose at least one issuer, form, and year.")
with explorer:
    q=st.text_input("Search company, ticker, accession, or report period")
    rows=view.copy()
    if q:
        mask=rows.astype(str).apply(lambda c:c.str.contains(q,case=False,na=False)).any(axis=1); rows=rows[mask]
    display=[c for c in ["company","ticker","form","filing_date","report_period","accession","size_mb","filing_url"] if c in rows]
    st.dataframe(rows[display],use_container_width=True,hide_index=True)
    st.download_button("Download filtered filing metadata CSV",rows.to_csv(index=False).encode(),"sec_edgar_filings.csv","text/csv")
with document:
    st.markdown("### Analyze an original SEC filing")
    if len(view):
        labels={f"{r.ticker} · {r.form} · filed {r.filing_date}":i for i,r in view.reset_index(drop=True).iterrows()}
        choice=st.selectbox("Select filing",list(labels))
        r=view.reset_index(drop=True).iloc[labels[choice]]
        st.markdown(f"**{r.company}** · [Open original SEC filing ↗]({r.filing_url})")
        if st.button("Fetch filing and run deterministic analysis",type="primary"):
            try:
                with st.spinner("Downloading filing HTML from SEC and analyzing document structure..."):
                    html=fetch_filing_html(r.filing_url,user_agent or None)
                    result=analyze_filing_html(html)
                    risk_excerpt=extract_filing_section(html, "Item 1A - Risk Factors")
                    st.session_state.analysis=result
                    st.session_state.analysis_filing=r.accession
                    st.session_state.analysis_risk_excerpt=risk_excerpt
                    st.session_state.ai_summary = None
                    st.session_state.ai_summary_accession = None
                st.success("Fetched original SEC filing and completed text/section analysis. No full filing text was saved.")
            except Exception as e: st.error(str(e))
        if st.session_state.get("analysis_filing")==r.accession:
            result=st.session_state.analysis
            a,b,c=st.columns(3); a.metric("Document words",f"{result['document_word_count']:,}"); b.metric("Sections detected",f"{result['sections_detected']}/{result['section_count_checked']}"); c.metric("Characters",f"{result['document_char_count']:,}")
            st.markdown("#### Section detection and word counts")
            sec=pd.DataFrame([{"Section":k,"Detected":v["present"],"Occurrences":v["occurrences"],"Words":v["word_count"]} for k,v in result["sections"].items()])
            st.dataframe(sec,use_container_width=True,hide_index=True)
            st.markdown("#### Keyword frequency")
            st.json(result["keyword_counts"])
            st.caption(result["analysis_method"])
            risk_words=result["sections"].get("Item 1A - Risk Factors",{}).get("word_count")
            risk_excerpt=st.session_state.get("analysis_risk_excerpt", "")
            if risk_words and risk_excerpt:
                st.caption("The optional AI synopsis uses the extracted Item 1A Risk Factors section from this SEC filing, not an unrelated portion of the document.")
                if st.button("Generate optional AI synopsis of risk factors",disabled=not os.getenv("OPENAI_API_KEY")):
                    try:
                        st.session_state.ai_summary=summarize_section(risk_excerpt[:18000])
                        st.session_state.ai_summary_accession=r.accession
                    except Exception as e: st.error(str(e))
                if st.session_state.get("ai_summary") and st.session_state.get("ai_summary_accession")==r.accession:
                    st.markdown("#### LLM-assisted synopsis")
                    st.write(st.session_state.ai_summary)
                if not os.getenv("OPENAI_API_KEY"): st.info("Optional LLM synopsis is off. Add OPENAI_API_KEY in your private environment to enable it. Deterministic analysis works without a key.")
    else: st.info("Select filings in the sidebar first.")
with method:
    st.markdown("### Data provenance")
    st.write("The initial snapshot contains seven selected annual reports (Form 10-K) from public issuers. Each record points to the original SEC filing and filing index. The refresh button retrieves current submission metadata from SEC data.sec.gov.")
    st.markdown("### Deterministic processing")
    st.write("The analysis fetches the primary filing HTML, removes script/style markup, normalizes text, detects common 10-K section headings, calculates word counts, and measures keyword occurrences. It does not determine whether a company complies with laws or whether a risk is material.")
    st.markdown("### Limitations")
    st.write("Section headings vary between issuers and years; the heuristic detector can miss or misidentify headings. Keyword counts indicate mentions, not sentiment, severity, or legal meaning. Optional LLM output is exploratory and must be checked against the source filing. No confidential employer data is used.")
    st.markdown("### SEC sources")
    st.markdown("- [EDGAR API documentation](https://www.sec.gov/edgar/sec-api-documentation)\n- [Accessing EDGAR data](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)\n- [SEC Developer Resources](https://www.sec.gov/developer)")
