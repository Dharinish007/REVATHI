"""`revathi memory graph`: one self-contained local HTML page that maps what the agents know (Phase 7h, D36).

Nodes: every note (approved, waiting, archived, episodes) plus a hub per place (you, each project, each tool).
Links: note -> its place, lesson -> the episodes behind it (sources "memory:<id>"), and likely duplicates or
conflicts (from memory.findings). No network, no libraries: the page draws itself with a small force layout.
Note text is shown with textContent only, so a note containing HTML or script can never run.
"""
import json
from datetime import datetime, timedelta, timezone

from engine import memory

SOON_DAYS = 30  # notes expiring within this many days are shown faded


def graph_data():
    trusted = {n["id"] for n in memory.approved()}
    soon = (datetime.now(timezone.utc) + timedelta(days=SOON_DAYS)).date().isoformat()
    nodes, links, hubs = [], [], {}

    def hub(key, label):
        if key not in hubs:
            hubs[key] = {"id": f"hub:{key}", "kind": "hub", "label": label}
            nodes.append(hubs[key])
        return hubs[key]["id"]

    for n in memory.notes():
        m, extra = n["meta"], n["meta"].get("x-revathi") or {}
        state = n["state"]
        if state == "approved" and n["id"] not in trusted:
            state = "untrusted"  # in an approved folder but changed, forged or expired: ignored by recall
        scope = extra.get("scope", "user")
        place = {"project": lambda: hub(f"p:{extra.get('project')}", f"project {str(extra.get('project'))[:6]}"),
                 "tool": lambda: hub(f"t:{extra.get('tool')}", f"tool {extra.get('tool')}")}.get(
            scope, lambda: hub("user", "you"))()
        nodes.append({"id": n["id"], "kind": "note", "type": m.get("type", "?"), "state": state,
                      "title": str(m.get("title", "")), "body": n["body"].strip()[:2000],
                      "sources": [str(s) for s in m.get("sources") or []],
                      "approved": [f"{v.get('by')} at {v.get('at')}" for v in m.get("verified") or []],
                      "expires": str(m.get("stale_after") or ""), "by": str((m.get("generated") or {}).get("by", "")),
                      "risk": extra.get("risk", ""),
                      "soon": bool(m.get("stale_after")) and str(m.get("stale_after")) <= soon})
        links.append({"source": n["id"], "target": place, "kind": "place"})
        for s in m.get("sources") or []:
            if str(s).startswith("memory:"):
                links.append({"source": n["id"], "target": str(s)[7:], "kind": "evidence"})
    ids = {x["id"] for x in nodes}
    links = [lk for lk in links if lk["target"] in ids]
    for f in memory.findings():
        links.append({"source": f["a"]["id"], "target": f["b"]["id"], "kind": f["kind"]})
    return {"nodes": nodes, "links": links, "made": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def html(data):
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")  # can't close the script tag early
    return PAGE.replace("__DATA__", payload)


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>REVATHI memory map</title>
<style>
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a65;--line:#d9d6cf;--panel:#ffffff;
--preference:#c2410c;--fact:#2563eb;--lesson:#7c3aed;--skill:#059669;--episode:#8a8a85;--hub:#1d1d1b;--bad:#dc2626}
@media (prefers-color-scheme:dark){:root{--bg:#161614;--fg:#ecebe6;--muted:#a3a29b;--line:#3a3934;--panel:#1f1f1c;--hub:#ecebe6}}
*{box-sizing:border-box}body{margin:0;font:14px/1.45 system-ui,sans-serif;background:var(--bg);color:var(--fg);display:flex;height:100vh}
#side{width:340px;max-width:45vw;padding:16px;border-right:1px solid var(--line);overflow:auto;background:var(--panel)}
h1{font-size:18px;margin:0 0 4px}small,.muted{color:var(--muted)}
input,select{width:100%;padding:6px 8px;margin:6px 0;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
label{display:block;margin:2px 0}.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}
#detail{margin-top:12px;padding-top:12px;border-top:1px solid var(--line);white-space:pre-wrap;word-break:break-word}
svg{flex:1;height:100vh;cursor:grab}text{font-size:11px;fill:var(--fg);pointer-events:none}
@media (max-width:700px){body{flex-direction:column}#side{width:100%;max-width:none;height:45vh}svg{height:55vh}}
</style></head><body>
<div id="side">
<h1>🧠 REVATHI memory map</h1><small id="made"></small>
<input id="q" placeholder="Search notes…">
<select id="view"><option value="all">Everything</option><option value="approved">Only what agents use (approved)</option>
<option value="inbox">Waiting for your review</option><option value="risk">Risks: untrusted, conflicts, expiring</option>
<option value="archive">Archive</option></select>
<div id="legend"></div>
<div id="detail" class="muted">Click a dot to see the note, where it came from and who approved it.</div>
</div>
<svg id="map" role="img" aria-label="Memory graph"></svg>
<script type="application/json" id="data">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent);
const TYPES=['preference','fact','lesson','skill','episode'];
const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
document.getElementById('made').textContent='Made '+D.made.replace('T',' ').slice(0,16)+' UTC · '+D.nodes.filter(n=>n.kind==='note').length+' notes';
const leg=document.getElementById('legend');
for(const t of TYPES){const l=document.createElement('label');const d=document.createElement('span');d.className='dot';d.style.background=css('--'+t);l.append(d,t);leg.append(l)}
const extra=document.createElement('small');extra.textContent='Hollow = waiting for review · red ring = untrusted · faded = expires within 30 days · red line = possible conflict · dashed = duplicate';leg.append(extra);
const svg=document.getElementById('map'),NS='http://www.w3.org/2000/svg';
const byId=new Map(D.nodes.map(n=>[n.id,n]));
D.nodes.forEach((n,i)=>{const a=i*2.399;n.x=Math.cos(a)*(40+i*4);n.y=Math.sin(a)*(40+i*4);n.vx=0;n.vy=0});
const L=D.links.map(l=>({...l,s:byId.get(l.source),t:byId.get(l.target)})).filter(l=>l.s&&l.t);
const g=document.createElementNS(NS,'g');svg.append(g);
function el(tag,attrs){const e=document.createElementNS(NS,tag);for(const k in attrs)e.setAttribute(k,attrs[k]);return e}
const lineEls=L.map(l=>{const e=el('line',{'stroke-width':l.kind==='conflict'?2:1});
 e.setAttribute('stroke',l.kind==='conflict'?css('--bad'):css('--line'));if(l.kind==='duplicate')e.setAttribute('stroke-dasharray','4 3');
 if(l.kind==='evidence')e.setAttribute('stroke',css('--muted'));g.append(e);return e});
const nodeEls=D.nodes.map(n=>{const grp=el('g',{});const r=n.kind==='hub'?9:6;
 const c=el('circle',{r});const col=n.kind==='hub'?css('--hub'):css('--'+(TYPES.includes(n.type)?n.type:'episode'));
 if(n.state==='inbox'){c.setAttribute('fill',css('--panel'));c.setAttribute('stroke',col);c.setAttribute('stroke-width',2)}else c.setAttribute('fill',col);
 if(n.state==='untrusted'){c.setAttribute('stroke',css('--bad'));c.setAttribute('stroke-width',3)}
 if(n.soon||n.state==='archive')grp.setAttribute('opacity',.35);
 const t=el('text',{x:r+3,y:4});t.textContent=(n.kind==='hub'?n.label:n.title).slice(0,40);
 grp.append(c,t);grp.style.cursor='pointer';grp.addEventListener('click',()=>show(n));g.append(grp);return grp});
function show(n){const d=document.getElementById('detail');d.className='';d.textContent='';
 const add=(label,val)=>{if(!val||(Array.isArray(val)&&!val.length))return;const b=document.createElement('b');b.textContent=label+': ';d.append(b,document.createTextNode((Array.isArray(val)?val.join('\n  '):val)+'\n'))};
 if(n.kind==='hub'){add('Place',n.label);return}
 const h=document.createElement('h3');h.textContent=n.title;d.append(h);
 add('Type',n.type+' · '+({approved:'approved (agents use it)',inbox:'waiting for your review',archive:'archived (not used)',episode:'evidence (never shown to agents)',untrusted:'untrusted: changed, forged or expired, ignored'}[n.state]||n.state));
 add('Note',n.body);add('From',n.sources);add('Approved by',n.approved);add('Expires',n.expires);add('Suggested by',n.by);add('Risk',n.risk);add('Id',n.id);
 const why=L.filter(l=>l.kind==='evidence'&&l.s===n).map(l=>l.t.title);add('Why we believe it',why);
 const clash=L.filter(l=>(l.kind==='conflict'||l.kind==='duplicate')&&(l.s===n||l.t===n)).map(l=>l.kind+' with: '+(l.s===n?l.t:l.s).title);add('Check',clash)}
function visible(n){const q=document.getElementById('q').value.toLowerCase(),v=document.getElementById('view').value;
 if(n.kind==='hub')return true;if(q&&!(n.title+' '+n.body).toLowerCase().includes(q))return false;
 if(v==='all')return true;if(v==='risk')return n.state==='untrusted'||n.soon||L.some(l=>l.kind==='conflict'&&(l.s===n||l.t===n));
 return n.state===v}
function filter(){D.nodes.forEach((n,i)=>nodeEls[i].style.display=visible(n)?'':'none');
 L.forEach((l,i)=>lineEls[i].style.display=visible(l.s)&&visible(l.t)?'':'none')}
document.getElementById('q').addEventListener('input',filter);document.getElementById('view').addEventListener('change',filter);
let scale=1,ox=0,oy=0,drag=null;
function tick(){for(let i=0;i<D.nodes.length;i++){const a=D.nodes[i];for(let j=i+1;j<D.nodes.length;j++){const b=D.nodes[j];
 let dx=a.x-b.x,dy=a.y-b.y,d2=dx*dx+dy*dy+.01;if(d2>90000)continue;const f=400/d2;a.vx+=dx*f;a.vy+=dy*f;b.vx-=dx*f;b.vy-=dy*f}}
 for(const l of L){const dx=l.t.x-l.s.x,dy=l.t.y-l.s.y,d=Math.sqrt(dx*dx+dy*dy)||1,k=(d-(l.kind==='place'?70:50))*.01;
 l.s.vx+=dx/d*k*d*.05;l.s.vy+=dy/d*k*d*.05;l.t.vx-=dx/d*k*d*.05;l.t.vy-=dy/d*k*d*.05}
 for(const n of D.nodes){n.vx-=n.x*.002;n.vy-=n.y*.002;n.x+=n.vx*.5;n.y+=n.vy*.5;n.vx*=.6;n.vy*=.6}}
function draw(){const w=svg.clientWidth,h=svg.clientHeight;g.setAttribute('transform',`translate(${w/2+ox},${h/2+oy}) scale(${scale})`);
 L.forEach((l,i)=>{const e=lineEls[i];e.setAttribute('x1',l.s.x);e.setAttribute('y1',l.s.y);e.setAttribute('x2',l.t.x);e.setAttribute('y2',l.t.y)});
 D.nodes.forEach((n,i)=>nodeEls[i].setAttribute('transform',`translate(${n.x},${n.y})`))}
let steps=0;(function run(){if(steps++<300){tick();draw();requestAnimationFrame(run)}})();
svg.addEventListener('wheel',e=>{e.preventDefault();scale=Math.min(4,Math.max(.2,scale*(e.deltaY<0?1.1:.9)));draw()},{passive:false});
svg.addEventListener('pointerdown',e=>{drag={x:e.clientX-ox,y:e.clientY-oy}});
addEventListener('pointerup',()=>drag=null);addEventListener('pointermove',e=>{if(drag){ox=e.clientX-drag.x;oy=e.clientY-drag.y;draw()}});
addEventListener('resize',draw);
</script></body></html>
"""
