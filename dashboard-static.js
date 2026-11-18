const DATA_URL = "assets/sec_filings.json";
let records = [];
const $ = (id) => document.getElementById(id);
const fmt = (n) => Number(n || 0).toLocaleString("en-IN");
const mb = (n) => n == null ? "N/A" : (Number(n)/1048576).toFixed(2) + " MB";
function filtered(){
 const issuer=$('issuerFilter').value, year=$('yearFilter').value, form=$('formFilter').value, q=$('recordSearch').value.trim().toLowerCase();
 return records.filter(r => (issuer==='all'||r.ticker===issuer) && (year==='all'||r.filing_date.slice(0,4)===year) && (form==='all'||r.form===form) && (!q||[r.company,r.ticker,r.cik,r.accession,r.form,r.report_period].join(' ').toLowerCase().includes(q)));
}
function options(id, values, label){ const el=$(id); values.forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;el.appendChild(o);}); }
function renderBars(id, items, formatter){const max=Math.max(...items.map(x=>x.value),1);$(id).innerHTML=items.map(x=>`<div class="bar-row"><span>${x.label}</span><div class="bar-track"><div class="bar-fill" style="width:${Math.max(2,x.value/max*100)}%"></div></div><span class="bar-value">${formatter(x.value)}</span></div>`).join('')||'<span class="loading">No data for these filters.</span>';}
function render(){
 const rows=filtered(), issuers=new Set(rows.map(r=>r.ticker));
 $('kpiFilings').textContent=fmt(rows.length); $('kpiIssuers').textContent=fmt(issuers.size);
 const totalBytes=rows.reduce((a,r)=>a+(Number(r.primary_doc_bytes)||0),0); $('kpiSize').textContent=mb(totalBytes);
 const complete=rows.filter(r=>r.metadata_complete).length; $('kpiCompleteness').textContent=rows.length?(complete/rows.length*100).toFixed(0)+'%':'—';
 const byIssuer={}; rows.forEach(r=>byIssuer[r.ticker]=(byIssuer[r.ticker]||0)+1);
 renderBars('issuerChart',Object.entries(byIssuer).map(([label,value])=>({label,value})).sort((a,b)=>b.value-a.value),fmt);
 renderBars('sizeChart',rows.filter(r=>r.primary_doc_bytes).map(r=>({label:r.ticker,value:Number(r.primary_doc_bytes)/1048576})).sort((a,b)=>b.value-a.value),v=>v.toFixed(1));
 const dates=rows.slice().sort((a,b)=>a.filing_date.localeCompare(b.filing_date));
 const grouped={};dates.forEach(r=>{const m=r.filing_date.slice(0,7);grouped[m]=(grouped[m]||0)+1;});
 const months=Object.entries(grouped).sort((a,b)=>a[0].localeCompare(b[0])), maxMonth=Math.max(1,...months.map(x=>x[1]));
 $('timelineChart').innerHTML=months.map(([month,count])=>`<div class="timeline-cell"><div class="timeline-bar-wrap"><div class="timeline-bar" style="height:${count/maxMonth*58}px"></div></div><b>${count}</b><small>${month}</small></div>`).join('')||'<span class="loading">No filings for these filters.</span>';
 $('recordsBody').innerHTML=rows.slice().sort((a,b)=>b.filing_date.localeCompare(a.filing_date)).map(r=>`<tr><td><span class="company-name">${r.company}</span></td><td><span class="ticker">${r.ticker}</span></td><td>${r.report_period||'—'}</td><td>${r.filing_date}</td><td>${r.form}</td><td>${mb(r.primary_doc_bytes)}</td><td><a class="source-link" href="${r.filing_url}" target="_blank" rel="noreferrer">Open SEC filing ↗</a></td></tr>`).join('')||'<tr><td colspan="7" class="loading">No matching SEC filings.</td></tr>';
 $('recordCount').textContent=`${fmt(rows.length)} filing records`;
 $('sourceNote').textContent=`Showing ${rows.length} of ${records.length} verified source records. SEC links open the original filing; this dashboard does not reproduce full filing text.`;
}
function download(){const rows=filtered();if(!rows.length)return;const cols=['company','ticker','cik','form','filing_date','report_period','accession','primary_document','primary_doc_bytes','filing_url','index_url'];const csv=[cols.join(','),...rows.map(r=>cols.map(k=>'"'+String(r[k]??'').replaceAll('"','""')+'"').join(','))].join('\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));const a=document.createElement('a');a.href=url;a.download='sec-edgar-filings.csv';a.click();URL.revokeObjectURL(url);}
async function init(){try{const res=await fetch(DATA_URL);if(!res.ok)throw new Error('Could not load the SEC filing snapshot.');const data=await res.json();records=data.records||[];$('snapshotDate').textContent=data.snapshot_date||'Point-in-time';options('issuerFilter',[...new Set(records.map(r=>r.ticker))].sort());options('yearFilter',[...new Set(records.map(r=>r.filing_date.slice(0,4)))].sort());options('formFilter',[...new Set(records.map(r=>r.form))].sort());['issuerFilter','yearFilter','formFilter','recordSearch'].forEach(id=>$(id).addEventListener(id==='recordSearch'?'input':'change',render));$('resetFilters').addEventListener('click',()=>{['issuerFilter','yearFilter','formFilter'].forEach(id=>$(id).value='all');$('recordSearch').value='';render();});$('downloadCsv').addEventListener('click',download);render();}catch(e){$('recordsBody').innerHTML=`<tr><td colspan="7" class="loading">${e.message} Serve the repository with GitHub Pages or a local HTTP server.</td></tr>`;}}
init();