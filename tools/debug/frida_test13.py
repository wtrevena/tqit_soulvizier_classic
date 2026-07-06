"""Combined debugger for the build13 (lattice-aligned) walk test.

One frida agent, two instruments, read-only:
  1. Interceptor on ProcessRLTD (Engine+0x1f4ba0): every navmesh load ->
     level name (own GUID -> name from the NEW deployed map), OK/REJECTED,
     dependency list. Cluster levels flagged loudly.
  2. RPC region-manager sweep every 15s (global Engine+0x3743f0 ->
     [[G]+0x34]+0x50] vector<Region*> by level index): resident regions,
     navmeshOK flag ([region+0x50]=Level, flag @Level+0x6a48), dead byte,
     portal arrays (+0x8c / +0x128; portal dest GUID @+0xdc, open @+0xfc).
Auto-attaches when TQ.exe appears (polls up to 60 min).
Log: scratchpad/frida_test13.log
"""
import sys, time, json
from pathlib import Path
REPO = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic")
sys.path.insert(0, str(REPO / 'tools'))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
DEP = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic\Resources\Levels.arc")
LOG = Path(r"C:\Users\willi\AppData\Local\Temp\claude\C--Users-willi-repos\fc31fa12-e2e4-44ef-998c-7fe110587b8c\scratchpad\frida_test13.log")

print("parsing NEW deployed map for index/GUID->name ...", flush=True)
arc = ArcArchive.from_file(DEP)
data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
sec = {s['type']: s for s in parse_sections(data)}
names = []
guid2name = {}
cluster = set()
for lv in parse_level_index(data, sec[SEC_LEVELS]):
    key = lv['fname'].replace('\\', '/').lower(); base = key.split('/')[-1].replace('.lvl', '')
    names.append(base)
    guid2name[lv['ints_raw'][36:52].hex()] = base
    if 'xbloodcave' in key or base == 'random09a': cluster.add(base)
print(f"  {len(names)} levels; cluster={len(cluster)}", flush=True)

import frida
JS = r"""
const NAMES = __NAMES__; const GUIDMAP = __GUIDMAP__; const CLUSTER = __CLUSTER__;
const base = Process.getModuleByName('Engine.dll').base;
const G = base.add(0x3743f0);
const PROC = base.add(0x1f4ba0);
function hx(ptr,n){ try{ const b=new Uint8Array(ptr.readByteArray(n)); let s='';
  for(let i=0;i<n;i++) s+=('0'+b[i].toString(16)).slice(-2); return s; }catch(e){ return null; } }
function rd(p){ try{ return p.readPointer(); }catch(e){ return null; } }
function ru8(p){ try{ return p.readU8(); }catch(e){ return -1; } }
function isREC(ptr){ try { const b=new Uint8Array(ptr.readByteArray(4));
  return b[0]===0x52&&b[1]===0x45&&b[2]===0x43&&b[3]===0x02; } catch(e){ return false; } }
function findREC(ctx, args){
  const cands=[ctx.ecx, ctx.edx, ctx.esi, ctx.eax];
  for (let i=0;i<10;i++){ try { cands.push(args[i]); } catch(e){} }
  for (const c of cands){ if (!c) continue;
    try { if (!c.isNull() && isREC(c)) return c; } catch(e){}
    try { const p=c.readPointer(); if (!p.isNull() && isREC(p)) return p; } catch(e){} }
  return null;
}
let n=0;
Interceptor.attach(PROC, {
  onEnter(args){
    this.nm=null;
    const rec=findREC(this.context,args);
    if (rec){
      const gc=rec.add(12).readU32();
      const own=hx(rec.add(16),16);
      const nm=GUIDMAP[own]||('?'+(own?own.slice(0,8):'??'));
      let deps=[]; if (gc>0&&gc<64){ for(let i=0;i<gc;i++){ const g=hx(rec.add(16+i*16),16); deps.push(GUIDMAP[g]||('?'+(g?g.slice(0,8):''))); } }
      this.nm=nm;
      send({t:'proc', n:++n, lvl:nm, gc:gc, deps:deps, cluster:CLUSTER.indexOf(nm)>=0});
    }
  },
  onLeave(ret){
    if (this.nm!==null){ const r=ret.toInt32();
      send({t:'result', lvl:this.nm, ret:r, ok:(r!==0), cluster:CLUSTER.indexOf(this.nm)>=0}); }
  }
});
function portalArr(region, off){
  const beg = rd(region.add(off)), end = rd(region.add(off+4));
  if (!beg || !end || beg.isNull()) return null;
  const bytes = end.sub(beg).toInt32();
  if (bytes < 0 || bytes > 0x4000 || (bytes & 3)) return null;
  const nn = bytes >> 2; if (nn > 256) return null;
  const out = [];
  for (let i=0;i<nn;i++){
    const p = rd(beg.add(i*4)); if (!p || p.isNull()) { out.push({dest:'(null)',open:-1}); continue; }
    const g = hx(p.add(0xdc),16);
    out.push({dest:(g&&GUIDMAP[g])||('?'+(g?g.slice(0,8):'??')), open:ru8(p.add(0xfc))});
  }
  return out;
}
rpc.exports = {
  sweep(){
    const res = {live:[], detail:[], err:null};
    try {
      const P = rd(G);
      if (!P || P.isNull()){ res.err='global null (menu/loading)'; return res; }
      const mgr = rd(P.add(0x34));
      if (!mgr || mgr.isNull()){ res.err='manager null (menu/loading)'; return res; }
      const beg = rd(mgr.add(0x50)), end = rd(mgr.add(0x54));
      if (!beg || !end){ res.err='region array null'; return res; }
      const nn = end.sub(beg).toInt32() >> 2;
      res.count = nn;
      for (let i=0;i<nn && i<NAMES.length;i++){
        const r = rd(beg.add(i*4)); if (!r || r.isNull()) continue;
        const lvl = rd(r.add(0x50));
        if (!lvl || lvl.isNull()) continue;               // not resident
        let nm = NAMES[i];
        const og = hx(r.add(0x14),16);
        if (og && GUIDMAP[og] && GUIDMAP[og] !== nm) nm = NAMES[i]+'!='+GUIDMAP[og];
        else if (og && GUIDMAP[og]) nm = nm + '*';
        const flag = ru8(lvl.add(0x6a48));
        const dead = ru8(r.add(0x74));
        const pa = portalArr(r, 0x8c), pb = portalArr(r, 0x128);
        const brief = {i:i, nm:nm, flag:flag, dead:dead,
                       na:(pa?pa.length:-1), nb:(pb?pb.length:-1)};
        res.live.push(brief);
        const bn = nm.replace('*','');
        const interesting = CLUSTER.indexOf(bn)>=0 || bn==='hiddenvalley01' ||
          (pa && pa.length>0) || (pb && pb.length>0);
        if (interesting) res.detail.push({i:i, nm:nm, flag:flag, dead:dead, pa:pa, pb:pb});
      }
    } catch(e){ res.err = ''+e; }
    return res;
  }
};
send({t:'info', m:'agent ready: ProcessRLTD hook + sweep; Engine.dll base='+base});
"""
JS = JS.replace('__NAMES__', json.dumps(names)).replace('__GUIDMAP__', json.dumps(guid2name)).replace('__CLUSTER__', json.dumps(sorted(cluster)))

logf = open(LOG, 'w', encoding='utf-8')
def out(s):
    line = time.strftime('%H:%M:%S ') + s; print(line, flush=True); logf.write(line+'\n'); logf.flush()

def on_message(msg, _):
    if msg['type'] == 'error': out('JS ERROR: '+msg.get('description','')); return
    p = msg.get('payload', {}); t = p.get('t')
    if t == 'info': out('[info] '+p['m'])
    elif t == 'proc':
        if p['cluster']:
            out(f"[LOAD #{p['n']}] CLUSTER {p['lvl']:32s} guids={p['gc']} deps={p['deps']}")
    elif t == 'result':
        if p['cluster']:
            v = 'OK' if p['ok'] else 'REJECTED   <<<<<'
            out(f"      => {p['lvl']:32s} {v} (ret={p['ret']})")

out("waiting for TQ.exe (launch the game now) ...")
session = None
for i in range(1800):
    try: session = frida.attach("TQ.exe"); break
    except Exception:
        if i % 30 == 0 and i: out("  ... still waiting for TQ.exe")
        time.sleep(2)
if session is None: out("TQ.exe never appeared; stopping."); sys.exit(2)
out("ATTACHED to TQ.exe")
script = session.create_script(JS); script.on('message', on_message); script.load()

def fmt_portals(tag, arr):
    if arr is None: return f"      {tag}: (unreadable)"
    if not arr:     return f"      {tag}: EMPTY"
    lines = [f"      {tag}: {len(arr)} portal(s)"]
    for p in arr: lines.append(f"         -> {p['dest']:34s} open={p['open']}")
    return '\n'.join(lines)

last_sig = None
while True:
    time.sleep(15)
    try: res = script.exports_sync.sweep()
    except Exception as e:
        out(f"sweep RPC failed (game exited?): {e}"); break
    if res.get('err'):
        continue   # menu/loading - quiet
    live = res['live']; detail = res['detail']
    sig = json.dumps(detail, sort_keys=True)
    if sig != last_sig:
        last_sig = sig
        out(f"=== SWEEP: {len(live)} resident ===")
        out("  " + ', '.join(f"{b['nm']}[f={b['flag']},A={b['na']}]" for b in live))
        for d in detail:
            out(f"  [idx {d['i']}] {d['nm']}  navmeshOK={d['flag']} dead={d['dead']}")
            out(fmt_portals('A(+0x8c) ', d['pa']))
            out(fmt_portals('B(+0x128)', d['pb']))
        out("=== END ===")
out("debugger stopped.")
