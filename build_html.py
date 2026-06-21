#!/usr/bin/env python3
"""Build a single self-contained interactive HTML index of AI coding & data agents for researchers.
Usage: python3 build_html.py [tools.json] [out.html]
Privacy-first: data-sensitivity suitability matrix + capability/protection signals.
"""
import json, sys, html, datetime
from collections import Counter

SRC = sys.argv[1] if len(sys.argv) > 1 else 'tools.json'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'docs/index.html'
tools = json.load(open(SRC))

TYPE_LABELS = {'ide':'IDE / editor','cli':'Terminal / CLI','cloud':'Cloud / autonomous','data':'Data analysis / notebook'}
TYPE_ORDER  = ['ide','cli','cloud','data']
DH_ORDER    = ['local','zdr','no-train','opt-out','trains']
CAP_ORDER   = ['frontier','strong','capable','basic']
OPEN_ORDER  = ['open-source','open-core','commercial']

norm=[]
for t in tools:
    rec=dict(t)
    rec['_s']=' '.join([t.get('name',''),t.get('vendor',''),t.get('notes',''),
                        ' '.join(t.get('use_cases',[])),t.get('model_backend',''),
                        TYPE_LABELS.get(t.get('type',''),'')]).lower()
    rec['runs_locally']=bool(t.get('runs_locally',False))
    acad=(t.get('academic','') or '').strip().lower()
    rec['freeacad']= acad not in ('','-','—','none','no')
    dep=(t.get('deployment','') or '').lower()
    rec['selfhost']= ('self-host' in dep) or ('on-prem' in dep) or rec['runs_locally']
    norm.append(rec)

def sort_key(m):
    return (TYPE_ORDER.index(m.get('type','')) if m.get('type','') in TYPE_ORDER else 99,
            0 if m.get('established') else 1,
            DH_ORDER.index(m.get('data_handling','')) if m.get('data_handling','') in DH_ORDER else 99,
            m.get('name','').lower())
norm.sort(key=sort_key)

today=datetime.date.today().isoformat()
total=len(norm)
n_local=sum(1 for m in norm if m['runs_locally'])
n_open=sum(1 for m in norm if m.get('openness')=='open-source')
n_special=sum(1 for m in norm if m.get('suitability',{}).get('special')=='ok')

try:
    _elixir_svg=open('assets/elixir-cz-logo.svg').read()
    if _elixir_svg.lstrip().startswith('<?xml'):
        _elixir_svg=_elixir_svg.split('?>',1)[1]
except FileNotFoundError:
    _elixir_svg=''

TPL = r"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Coding &amp; Data Agents for Researchers</title>
<style>
:root{
 --bg:#f6f7f9;--panel:#fff;--ink:#1a1d24;--muted:#5b6472;--line:#e3e7ee;--accent:#2563eb;
 --chip:#eef1f6;--chipline:#dce1ea;--rowhover:#f0f4fb;--detail:#f8fafc;
 --dhlocal:#0f6e56;--dhlocalbg:#e1f5ee;--dhzdr:#3b6d11;--dhzdrbg:#eaf3de;
 --dhnotrain:#185fa5;--dhnotrainbg:#e6f1fb;--dhoptout:#854f0b;--dhoptoutbg:#faeeda;
 --dhtrains:#a32d2d;--dhtrainsbg:#fceaea;
 --ok:#0f7a3d;--cfg:#9a5b00;--no:#a13a3a;--star:#e8a800;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:13.5px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1340px;margin:0 auto;padding:16px 18px 90px}
header.top{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap}
h1{font-size:21px;margin:0 0 4px}
.sub{color:var(--muted);font-size:12.5px;max-width:880px}
.maxim{font-style:italic;color:var(--ink)}
.disclaimer{background:#fff8e6;border:1px solid #f0e0b0;color:#6b5310;border-radius:10px;padding:9px 13px;font-size:12px;margin:12px 0 2px}
.draftbar{background:#eef4fd;border:1px solid #cfe0f6;color:#1c4f8a;border-radius:10px;padding:7px 13px;font-size:12px;margin:10px 0 0}
.hright{display:flex;flex-direction:column;align-items:flex-end;gap:12px}
.dedi{display:flex;align-items:center;gap:11px;text-decoration:none}.dedi:hover{text-decoration:none}
.elixir-logo svg{height:50px;width:auto;display:block}.elixir-logo .cls-2{fill:#4d4848}
.dedi-cap{font-size:12px;line-height:1.35;color:var(--muted);text-align:right}.dedi-cap b{color:var(--ink);font-weight:700}
.ask{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:11px 14px;margin:14px 0 0}
.ask .q{font-size:13px;font-weight:600;margin-bottom:7px}
.dcbtns{display:flex;gap:7px;flex-wrap:wrap}
.dc{border:1px solid var(--chipline);background:var(--chip);border-radius:999px;padding:6px 13px;font-size:12.5px;cursor:pointer;user-select:none}
.dc.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.dc small{display:block;font-size:10.5px;opacity:.7;font-weight:400}
.dcexpl{font-size:11.5px;color:var(--muted);margin-top:9px}
.dchint{font-size:12px;color:var(--muted);margin-top:6px;min-height:16px}
.dhkey{display:flex;flex-wrap:wrap;gap:7px 16px;align-items:center;margin:12px 0 2px;padding-top:11px;border-top:1px solid var(--line);font-size:11.5px;color:var(--muted)}
.dhkey>span{display:inline-flex;align-items:center;gap:6px}
.dhkeylbl{font-weight:600;text-transform:uppercase;letter-spacing:.04em}
.controls{position:sticky;top:0;z-index:30;background:var(--bg);padding:10px 0 8px;border-bottom:1px solid var(--line);margin:12px 0 4px}
.searchrow{display:flex;gap:9px;flex-wrap:wrap;align-items:center}
#q{flex:1;min-width:240px;padding:9px 12px;border:1px solid var(--line);border-radius:10px;background:var(--panel);font-size:14px}
.toolbtn{background:var(--panel);border:1px solid var(--line);color:var(--ink);border-radius:8px;padding:8px 11px;cursor:pointer;font-size:13px}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:9px;align-items:center}
.chips .lbl{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin-right:2px}
.chip{background:var(--chip);border:1px solid var(--chipline);border-radius:999px;padding:4px 10px;font-size:12px;cursor:pointer;user-select:none}
.chip.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.chip .c{opacity:.6;margin-left:5px;font-size:10.5px}
.chip.tog.on{background:var(--dhlocal);border-color:var(--dhlocal)}
.countpill{font-size:12px;color:var(--muted);margin:9px 0 0}
details.qc{margin:12px 0;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:4px 14px}
details.qc summary{cursor:pointer;font-weight:600;padding:7px 0}
.qcrow{display:flex;flex-wrap:wrap;gap:7px;padding:6px 0 10px}
.qcbtn{background:var(--chip);border:1px solid var(--chipline);border-radius:8px;color:var(--accent);font-size:12px;padding:5px 11px;cursor:pointer}
table.main{width:100%;border-collapse:collapse;font-size:13px}
table.main thead th{text-align:left;padding:8px 7px;border-bottom:2px solid var(--line);font-size:11px;text-transform:uppercase;letter-spacing:.03em;color:var(--muted);white-space:nowrap}
th.suit{text-align:center;cursor:pointer;width:62px}
th.suit.act{color:var(--ink);background:var(--detail)}
table.main tbody td{padding:9px 7px;border-bottom:1px solid var(--line);vertical-align:top}
tr.row{cursor:pointer}tr.row:hover{background:var(--rowhover)}
tr.dim{opacity:.4}
.exp{color:var(--muted);width:14px;display:inline-block;transition:transform .12s}tr.open .exp{transform:rotate(90deg)}
.nm{font-weight:700}.vend{color:var(--muted);font-size:11.5px;margin-left:5px}
.estar{color:var(--star);margin-left:4px}
.pill{font-size:11px;padding:2px 9px;border-radius:999px;font-weight:600;white-space:nowrap;display:inline-block}
.dh-local{background:var(--dhlocalbg);color:var(--dhlocal)}.dh-zdr{background:var(--dhzdrbg);color:var(--dhzdr)}
.dh-no-train{background:var(--dhnotrainbg);color:var(--dhnotrain)}.dh-opt-out{background:var(--dhoptoutbg);color:var(--dhoptout)}
.dh-trains{background:var(--dhtrainsbg);color:var(--dhtrains)}
.gate{font-size:10px;color:var(--cfg);margin-top:3px;line-height:1.25;max-width:155px}
.cap{font-size:11px;padding:2px 8px;border-radius:6px;background:var(--chip);color:var(--muted);font-weight:600;white-space:nowrap}
.cap-frontier{background:#ece9fc;color:#5b21b6}.cap-strong{background:#e1f5ee;color:var(--dhlocal)}
.bdep{font-size:10.5px;color:var(--muted);margin-left:5px;white-space:nowrap}
td.s{text-align:center;font-size:15px;font-weight:700}td.s.act{background:var(--detail)}
.s-ok{color:var(--ok)}.s-cfg{color:var(--cfg)}.s-no{color:var(--no)}
td.lnk a{font-size:14px;margin-right:6px}
tr.detailrow td{background:var(--detail);padding:2px 8px 14px 28px}
.detail .kv{font-size:12.5px;margin:4px 0}.detail .kv b{color:var(--muted);font-weight:600}
.detail .links a{display:inline-block;font-size:12px;border:1px solid var(--line);padding:3px 9px;border-radius:7px;margin:4px 7px 0 0;background:var(--panel)}
.tagrow{display:flex;gap:5px;flex-wrap:wrap;margin-top:5px}
.tg{font-size:11px;border:1px solid var(--chipline);border-radius:6px;padding:1px 7px;color:var(--muted)}
.grouprow td{background:var(--bg);font-size:11.5px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);font-weight:700;padding:14px 7px 5px;border-bottom:1px solid var(--line)}
footer{margin-top:30px;color:var(--muted);font-size:12px;border-top:1px solid var(--line);padding-top:14px}
.legend{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;font-size:11.5px}
.ver{font-size:10.5px;color:var(--muted)}
</style></head><body><div class="wrap">
<header class="top"><div class="htext">
<h1>AI Coding &amp; Data Agents for Researchers</h1>
<div class="sub">A privacy-first guide to AI coding and data-analysis tools for scientific work. Start from <b>your data</b>, see what's appropriate, and what it costs in capability.
<span class="maxim">As open as possible, as closed as necessary.</span></div>
</div>
<div class="hright">
<a class="dedi" href="https://www.elixir-czech.cz/" target="_blank" rel="noopener" title="ELIXIR-CZ">
<span class="elixir-logo">__ELIXIRSVG__</span>
<span class="dedi-cap">Dedicated to <b>ELIXIR-CZ</b><br>Czech national node of ELIXIR</span></a>
</div></header>
<div class="draftbar">Web-verified against vendor docs &amp; privacy pages on 2026-06-20. Privacy and pricing change fast — confirm your exact plan/tier and region before relying on any row.</div>
<div class="disclaimer"><b>Classify your data first</b> (ELIXIR <a href="https://rdmkit.elixir-europe.org/data_sensitivity" target="_blank" rel="noopener">RDMkit · Data sensitivity</a>). This is decision-support, not legal advice — <b>confirm with your DPO / data steward and the vendor's own terms before using sensitive or regulated data.</b> Privacy &amp; pricing change often; each row shows when it was last checked.</div>

<div class="ask">
 <div class="q">What data will you put into the tool?</div>
 <div class="dcbtns" id="dcb">
  <div class="dc" data-dc="nonsensitive">Non-sensitive<small>public · anonymised · synthetic</small></div>
  <div class="dc" data-dc="personal">Personal<small>pseudonymised · GDPR</small></div>
  <div class="dc" data-dc="special">Special-category<small>health · genetic · clinical</small></div>
 </div>
 <div class="dcexpl">Non-sensitive = public / anonymised / synthetic &nbsp;·&nbsp; Personal = pseudonymised (GDPR) &nbsp;·&nbsp; Special-category = health / genetic / clinical (GDPR Art.&nbsp;9)</div>
 <div class="dchint" id="dchint">Pick your data class to see what's suitable — or browse all below.</div>
 <div class="dhkey"><span class="dhkeylbl">What the data-handling labels mean —</span>
 <span><span class="pill dh-local">Local</span> runs on your own hardware; data never leaves</span>
 <span><span class="pill dh-zdr">Zero-retention</span> cloud, but nothing stored or trained on (usually enterprise/API)</span>
 <span><span class="pill dh-no-train">No-train</span> not used for training, but may be retained</span>
 <span><span class="pill dh-opt-out">Opt-out</span> trains on your data unless you turn it off</span>
 <span><span class="pill dh-trains">Trains by default</span> your inputs train the vendor's model</span>
 </div>
</div>

<div class="controls">
 <div class="searchrow">
  <input id="q" type="search" placeholder="Search tool, vendor, use case…  space = AND  (e.g. local notebook, self-host)">
  <button class="toolbtn" id="reset">Reset</button>
 </div>
 <div class="chips" id="typechips"><span class="lbl">Type</span></div>
 <div class="chips" id="dhchips"><span class="lbl">Data handling</span></div>
 <div class="chips" id="capchips"><span class="lbl">Capability</span></div>
 <div class="chips" id="togchips"><span class="lbl">Only</span></div>
 <div class="countpill" id="count"></div>
</div>

<details class="qc"><summary>⚡ Best starting points — by need</summary>
<div class="qcrow" id="qc"></div></details>

<table class="main"><thead><tr>
<th class="nosort"></th><th>Tool</th><th>Type</th><th>Data handling</th><th>Capability</th>
<th class="suit" data-dc="nonsensitive" title="Non-sensitive: public / anonymised / synthetic">Non-sens.</th>
<th class="suit" data-dc="personal" title="Personal (pseudonymised) — GDPR">Personal</th>
<th class="suit" data-dc="special" title="Special-category — health / genetic / clinical (GDPR Art. 9)">Special</th>
<th class="nosort">Links</th>
</tr></thead><tbody id="tb"></tbody></table><div id="empty"></div>

<footer>
<b>__TOTAL__</b> tools · __NLOCAL__ run locally · __NOPEN__ open-source · __NSPECIAL__ usable for special-category data. Updated __TODAY__.
<div class="legend"><span>The pill shows the <b>best</b> data option; the <span style="color:var(--cfg)">▸ line beneath</span> is the plan/tier or setting you must use to get it — the default or free plan is usually less private. No line = applies on the default plan (local / self-host).</span></div>
<div class="legend">
<span><b>Suitability:</b></span><span class="s-ok">✓ suitable</span><span class="s-cfg">⚠ only with config/tier</span><span class="s-no">✗ not appropriate</span>
</div>
<div class="legend"><span><span class="estar">★</span> widely adopted / established choice — sorted first within each section</span></div>
<div class="legend"><span><span class="bdep">↔ model</span> capability depends on the model you connect (bring-your-own-model tools): a frontier API gives top capability, a local model keeps data private but lower.</span></div>
<div style="margin-top:10px"><b>Curated, not exhaustive</b> — this is a useful shortlist, not a complete catalogue. Some niche, enterprise-only, or single-purpose tools (e.g. code-review bots) are intentionally omitted for clarity and to keep the privacy data maintainable.</div>
<div style="margin-top:8px">Data classes follow ELIXIR <a href="https://rdmkit.elixir-europe.org/data_sensitivity" target="_blank" rel="noopener">RDMkit</a>. A discovery aid — verify each tool's current terms with the vendor and your institution before relying on it.</div>
</footer>
</div>
<script>
const DATA=__DATA__;
const TYPE_LABELS=__TYPELABELS__,TYPE_ORDER=__TYPEORDER__;
const DH_LABELS={'local':'Local / self-host','zdr':'Zero-retention','no-train':'No-train','opt-out':'Opt-out','trains':'Trains by default'};
const DH_SHORT={'local':'Local','zdr':'ZDR','no-train':'No-train','opt-out':'Opt-out','trains':'Trains'};
const TYPE_SHORT={'ide':'IDE','cli':'CLI','cloud':'Cloud','data':'Data'};
const DH_ORDER=__DHORDER__;
const CAP_LABELS={'frontier':'Frontier','strong':'Strong','capable':'Capable','basic':'Basic'},CAP_ORDER=__CAPORDER__;
const DC_LABELS={'nonsensitive':'Non-sensitive','personal':'Personal (pseudonymised)','special':'Special-category'};
const SUIT={'ok':['✓','s-ok','suitable'],'cfg':['⚠','s-cfg','only with config/tier'],'no':['✗','s-no','not appropriate']};
const esc=s=>(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const st={q:'',types:new Set(),dh:new Set(),cap:new Set(),tog:new Set(),dc:null};

function counts(f,order){const c={};order.forEach(k=>c[k]=0);DATA.forEach(m=>{if(c[m[f]]!==undefined)c[m[f]]++});return c}
const typeC=counts('type',TYPE_ORDER),dhC=counts('data_handling',DH_ORDER),capC=counts('capability',CAP_ORDER);
function chips(el,order,labels,cnts,set){order.forEach(k=>{if(cnts&&!cnts[k])return;const d=document.createElement('div');d.className='chip';d.dataset.k=k;d.innerHTML=labels[k]+(cnts?'<span class="c">'+cnts[k]+'</span>':'');d.onclick=()=>{set.has(k)?set.delete(k):set.add(k);d.classList.toggle('on');render()};el.appendChild(d)})}
chips(document.getElementById('typechips'),TYPE_ORDER,TYPE_LABELS,typeC,st.types);
chips(document.getElementById('dhchips'),DH_ORDER,DH_LABELS,dhC,st.dh);
chips(document.getElementById('capchips'),CAP_ORDER,CAP_LABELS,capC,st.cap);
[['established','Widely used ★'],['runsLocal','Runs locally'],['selfHost','Self-hostable'],['freeAcad','Free / academic']].forEach(([k,lab])=>{const d=document.createElement('div');d.className='chip tog';d.innerHTML=lab;d.onclick=()=>{st.tog.has(k)?st.tog.delete(k):st.tog.add(k);d.classList.toggle('on');render()};document.getElementById('togchips').appendChild(d)});

const QC=[
 {t:'I have clinical / special-category data',f:()=>{setDC('special')}},
 {t:'Must run offline / on HPC',f:()=>{clearAll();st.tog.add('runsLocal');syncTog()}},
 {t:'On a budget / student',f:()=>{clearAll();st.tog.add('freeAcad');syncTog()}},
 {t:'I work in notebooks (R / Jupyter)',f:()=>{clearAll();st.types.add('data');syncChips()}},
 {t:'Frontier capability, non-sensitive data',f:()=>{clearAll();setDC('nonsensitive');st.cap.add('frontier');syncChips()}},
];
const qcEl=document.getElementById('qc');QC.forEach(x=>{const b=document.createElement('button');b.className='qcbtn';b.textContent=x.t;b.onclick=()=>{x.f();render()};qcEl.appendChild(b)});

const qEl=document.getElementById('q');
qEl.addEventListener('input',e=>{st.q=e.target.value.toLowerCase();render()});
document.getElementById('reset').onclick=()=>{clearAll();qEl.value='';render()};
function clearAll(){st.q='';st.types.clear();st.dh.clear();st.cap.clear();st.tog.clear();st.dc=null;syncChips();syncTog();syncDC()}
function syncChips(){document.querySelectorAll('#typechips .chip').forEach(c=>c.classList.toggle('on',st.types.has(c.dataset.k)));document.querySelectorAll('#dhchips .chip').forEach(c=>c.classList.toggle('on',st.dh.has(c.dataset.k)));document.querySelectorAll('#capchips .chip').forEach(c=>c.classList.toggle('on',st.cap.has(c.dataset.k)))}
function syncTog(){const map={established:'Widely used ★',runsLocal:'Runs locally',selfHost:'Self-hostable',freeAcad:'Free / academic'};document.querySelectorAll('#togchips .chip').forEach(c=>c.classList.toggle('on',st.tog.has(Object.keys(map).find(k=>map[k]===c.textContent))))}

function setDC(v){st.dc=st.dc===v?null:v;syncDC()}
function syncDC(){document.querySelectorAll('#dcb .dc').forEach(d=>d.classList.toggle('on',d.dataset.dc===st.dc));
 document.querySelectorAll('th.suit').forEach(th=>th.classList.toggle('act',th.dataset.dc===st.dc))}
document.querySelectorAll('#dcb .dc').forEach(d=>d.onclick=()=>{setDC(d.dataset.dc);render()});
document.querySelectorAll('th.suit').forEach(th=>th.onclick=()=>{setDC(th.dataset.dc);render()});

function togMatch(m){if(st.tog.has('established')&&!m.established)return false;if(st.tog.has('runsLocal')&&!m.runs_locally)return false;if(st.tog.has('selfHost')&&!m.selfhost)return false;if(st.tog.has('freeAcad')&&!m.freeacad)return false;return true}
function match(m){if(st.types.size&&!st.types.has(m.type))return false;if(st.dh.size&&!st.dh.has(m.data_handling))return false;if(st.cap.size&&!st.cap.has(m.capability))return false;if(!togMatch(m))return false;for(const tk of st.q.split(/\s+/).filter(Boolean)){if(!m._s.includes(tk))return false}return true}

function suitCell(m,dc){const v=(m.suitability||{})[dc]||'no';const[ic,cl,t]=SUIT[v];const act=st.dc===dc?' act':'';const note=(m.suitability_notes||{})[dc];return '<td class="s'+act+'"><span class="'+cl+'" title="'+esc(t+(note?' — '+note:''))+'">'+ic+'</span></td>'}
function dhPill(m){return '<span class="pill dh-'+m.data_handling+'" title="'+esc((DH_LABELS[m.data_handling]||'')+' — '+(m.data_handling_note||''))+'">'+(DH_SHORT[m.data_handling]||m.data_handling)+'</span>'}
function capPill(m){return '<span class="cap cap-'+m.capability+'">'+(CAP_LABELS[m.capability]||m.capability)+'</span>'+(m.backend_dependent?'<span class="bdep" title="Bring-your-own-model tool: capability depends on the model you connect — a frontier API gives frontier capability, a local model keeps it private but lower">↔ model</span>':'')}
function links(m,all){const L=m.links||{};let o=[];const add=(u,ic,lab)=>{if(u)o.push('<a href="'+u+'" target="_blank" rel="noopener" title="'+lab+'">'+(all?ic+' '+lab:ic)+'</a>')};add(L.docs,'📄','Docs');add(L.pricing,'💲','Pricing');add(L.privacy,'🔒','Privacy');return o.join(all?'':' ')}

function rowHtml(m){const open=st.openset.has(m.name);const dim=st.dc&&(m.suitability||{})[st.dc]==='no';
 let h='<tr class="row'+(open?' open':'')+(dim?' dim':'')+'" data-n="'+esc(m.name)+'">'
 +'<td><span class="exp">▸</span></td>'
 +'<td><span class="nm">'+esc(m.name)+'</span>'+(m.established?'<span class="estar" title="widely adopted / established choice">★</span>':'')+'<span class="vend">'+esc(m.vendor)+'</span></td>'
 +'<td title="'+esc(TYPE_LABELS[m.type]||'')+'">'+esc(TYPE_SHORT[m.type]||m.type)+'</td>'
 +'<td>'+dhPill(m)+(m.tier_gate?'<div class="gate"><i style="font-style:normal">▸ </i>'+esc(m.tier_gate)+'</div>':'')+'</td>'
 +'<td>'+capPill(m)+'</td>'
 +suitCell(m,'nonsensitive')+suitCell(m,'personal')+suitCell(m,'special')
 +'<td class="lnk">'+links(m,false)+'</td></tr>';
 if(open){const sn=m.suitability_notes||{};
  h+='<tr class="detailrow"><td colspan="9"><div class="detail">'
   +'<div class="kv"><b>What it is:</b> '+esc(m.notes||'')+'</div>'
   +'<div class="kv"><b>Data handling:</b> '+esc(m.data_handling_note||'')+'</div>'
   +(sn.personal?'<div class="kv"><b>Personal data:</b> '+esc(sn.personal)+'</div>':'')
   +(sn.special?'<div class="kv"><b>Special-category:</b> '+esc(sn.special)+'</div>':'')
   +'<div class="kv"><b>Model backend:</b> '+esc(m.model_backend||'')+' &nbsp; <b>Deployment:</b> '+esc(m.deployment||'')+'</div>'
   +'<div class="kv"><b>Pricing:</b> '+esc(m.pricing||'')+' &nbsp; <b>Academic:</b> '+esc(m.academic||'—')+'</div>'
   +'<div class="tagrow">'+(m.compliance||[]).map(c=>'<span class="tg">'+esc(c)+'</span>').join('')+(m.use_cases||[]).map(c=>'<span class="tg">'+esc(c)+'</span>').join('')+'</div>'
   +'<div class="links">'+links(m,true)+'</div>'
   +'<div class="ver">last checked '+esc(m.verified||'')+'</div>'
   +'</div></td></tr>';}
 return h}
st.openset=new Set();

function render(){let rows=DATA.filter(match);
 const tb=document.getElementById('tb'),emp=document.getElementById('empty'),cnt=document.getElementById('count');
 if(st.dc){rows.sort((a,b)=>{const r={ok:0,cfg:1,no:2};return (r[(a.suitability||{})[st.dc]||'no']-r[(b.suitability||{})[st.dc]||'no'])||((a.established?0:1)-(b.established?0:1))||(a.name.toLowerCase()<b.name.toLowerCase()?-1:1)})}
 cnt.textContent=rows.length+' of '+DATA.length+' tools shown';
 const hint=document.getElementById('dchint');
 if(st.dc){const ok=rows.filter(m=>(m.suitability||{})[st.dc]==='ok').length,cfg=rows.filter(m=>(m.suitability||{})[st.dc]==='cfg').length,no=rows.length-ok-cfg;
  hint.innerHTML='<b>'+DC_LABELS[st.dc]+':</b> '+ok+' ready · '+cfg+' with config/tier · '+no+' not appropriate. <span style="color:var(--muted)">(rows dimmed = not appropriate for this data)</span>'+(st.dc==='special'?'<br><span style="color:var(--muted)">Only tools that run on infrastructure you control are suitable — cloud services, even with ZDR / HIPAA-BAA, are not recommended for identifiable or controlled-access (DUA) data. Confirm with your DPO / IRB.</span>':'');}
 else hint.textContent='Pick your data class to see what\'s suitable — or browse all below.';
 if(!rows.length){tb.innerHTML='';emp.innerHTML='<div style="text-align:center;color:var(--muted);padding:40px 0">No tools match. Clear a filter.</div>';return}emp.innerHTML='';
 if(!st.dc){let h='',cur=null;rows.forEach(m=>{if(m.type!==cur){cur=m.type;const n=rows.filter(x=>x.type===cur).length;h+='<tr class="grouprow"><td colspan="9">'+esc(TYPE_LABELS[cur])+' · '+n+'</td></tr>'}h+=rowHtml(m)});tb.innerHTML=h;}
 else tb.innerHTML=rows.map(rowHtml).join('');
 tb.querySelectorAll('tr.row').forEach(tr=>tr.onclick=e=>{if(e.target.tagName==='A')return;const n=tr.dataset.n;st.openset.has(n)?st.openset.delete(n):st.openset.add(n);render()});}
render();
</script></body></html>"""

out=(TPL
 .replace('__ELIXIRSVG__',_elixir_svg)
 .replace('__DATA__',json.dumps(norm))
 .replace('__TYPELABELS__',json.dumps(TYPE_LABELS))
 .replace('__TYPEORDER__',json.dumps(TYPE_ORDER))
 .replace('__DHORDER__',json.dumps(DH_ORDER))
 .replace('__CAPORDER__',json.dumps(CAP_ORDER))
 .replace('__TODAY__',today).replace('__TOTAL__',str(total))
 .replace('__NLOCAL__',str(n_local)).replace('__NOPEN__',str(n_open)).replace('__NSPECIAL__',str(n_special)))

import os
os.makedirs(os.path.dirname(OUT) or '.',exist_ok=True)
open(OUT,'w').write(out)
print(f'Wrote {OUT}  ({total} tools, {n_local} local, {n_open} open-source, {n_special} special-category-ok)')
print('type:',dict(Counter(m["type"] for m in norm)))
print('data_handling:',dict(Counter(m["data_handling"] for m in norm)))
print('capability:',dict(Counter(m["capability"] for m in norm)))
