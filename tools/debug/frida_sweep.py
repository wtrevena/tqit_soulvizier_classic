"""Frida probe #3: PURE MEMORY SWEEP (no hooks at all -> zero lag/crash risk).

Walks the engine's region-manager live array (global @ Engine+0x3743f0, per
docs/CAVE_ENTRY_CHAIN_TRACE.md: [G+0x34]=manager, [mgr+0x50]=vector<Region*>
indexed BY LEVEL INDEX, so index -> level name comes straight from the map's
LEVELS section order). For every LIVE region dump:
  - level name (self-identified by array index)
  - [region+0x50] Level*  ->  [level+0x6a48] navmesh-loaded-OK flag
  - [region+0x74] skip/dead byte (linker skips region if nonzero)
  - portal array A [region+0x8c..0x90]   (FindCrossedPortal iterates this)
  - portal array B [region+0x128..0x12c] (the LINKER iterates this)
    per portal: dest level (GUID @+0xdc), open flag (@+0xfc)
Full detail for blood-cave-cluster regions + hiddenvalley01 (working reference);
one-line summary for everything else. Re-sweeps every 15s, reprints on change.
Log: scratchpad/frida_sweep.log
"""
import sys, time, json
from pathlib import Path
REPO = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic")
sys.path.insert(0, str(REPO / 'tools'))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
DEP = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic\Resources\Levels.arc")
LOG = Path(r"C:\Users\willi\AppData\Local\Temp\claude\C--Users-willi-repos\fc31fa12-e2e4-44ef-998c-7fe110587b8c\scratchpad\frida_sweep.log")

print("parsing map for index->name ...", flush=True)
arc = ArcArchive.from_file(DEP)
data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
sec = {s['type']: s for s in parse_sections(data)}
names = []          # index -> base name (LEVELS section order == level index)
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
function hx(ptr,n){ try{ const b=new Uint8Array(ptr.readByteArray(n)); let s='';
  for(let i=0;i<n;i++) s+=('0'+b[i].toString(16)).slice(-2); return s; }catch(e){ return null; } }
function rd(p){ try{ return p.readPointer(); }catch(e){ return null; } }
function ru8(p){ try{ return p.readU8(); }catch(e){ return -1; } }
function portalArr(region, off){
  const beg = rd(region.add(off)), end = rd(region.add(off+4));
  if (!beg || !end || beg.isNull()) return null;
  const bytes = end.sub(beg).toInt32();
  if (bytes < 0 || bytes > 0x4000 || (bytes & 3)) return null;
  const n = bytes >> 2; if (n > 256) return null;
  const out = [];
  for (let i=0;i<n;i++){
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
      // truth from live disasm @0x10194a9b: eax=[G]; eax=[eax+0x34]; beg=[eax+0x50]; end=[eax+0x54]
      const P = rd(G);
      if (!P || P.isNull()){ res.err='global null (not in-game yet?)'; return res; }
      const mgr = rd(P.add(0x34));
      if (!mgr || mgr.isNull()){ res.err='manager null (not in-game yet?)'; return res; }
      const beg = rd(mgr.add(0x50)), end = rd(mgr.add(0x54));
      if (!beg || !end){ res.err='region array null'; return res; }
      const n = end.sub(beg).toInt32() >> 2;
      res.count = n;
      for (let i=0;i<n && i<NAMES.length;i++){
        // GROUNDED MODEL (GetConnectedRegion tail @0x10206450: returns arr[idx] directly):
        //   arr[i]      = REGION: guid@+0x14, Level*@+0x50, dead@+0x74, portals@+0x8c/+0x128
        //   [reg+0x50]  = LEVEL:  navmesh-OK flag @+0x6a48
        const r = rd(beg.add(i*4)); if (!r || r.isNull()) continue;
        const lvl = rd(r.add(0x50));
        const resident = (lvl && !lvl.isNull());
        if (!resident) continue;                 // only report stream-resident regions
        let nm = NAMES[i];
        const og = hx(r.add(0x14),16);
        if (og && GUIDMAP[og] && GUIDMAP[og] !== nm) nm = NAMES[i]+'!='+GUIDMAP[og];
        else if (og && GUIDMAP[og]) nm = nm + '*';                       // * = GUID-confirmed
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
send({t:'info', m:'sweep agent ready; Engine.dll base='+base});
"""
JS = JS.replace('__NAMES__', json.dumps(names)).replace('__GUIDMAP__', json.dumps(guid2name)).replace('__CLUSTER__', json.dumps(sorted(cluster)))

logf = open(LOG, 'w', encoding='utf-8')
def out(s):
    line = time.strftime('%H:%M:%S ') + s; print(line, flush=True); logf.write(line+'\n'); logf.flush()
def on_message(msg, _):
    if msg['type'] == 'error': out('JS ERROR: '+msg.get('description','')); return
    p = msg.get('payload', {})
    if p.get('t') == 'info': out('[info] '+p['m'])

out("waiting for TQ.exe ...")
session = None
for i in range(1800):
    try: session = frida.attach("TQ.exe"); break
    except Exception:
        if i % 15 == 0: out("  ... waiting for TQ.exe")
        time.sleep(2)
if session is None: out("TQ.exe not found; stopping."); sys.exit(2)
out("ATTACHED")
script = session.create_script(JS); script.on('message', on_message); script.load()

def fmt_portals(tag, arr):
    if arr is None: return f"      {tag}: (unreadable)"
    if not arr:     return f"      {tag}: EMPTY (0 portals)"
    lines = [f"      {tag}: {len(arr)} portal(s)"]
    for p in arr:
        lines.append(f"         -> {p['dest']:34s} open={p['open']}")
    return '\n'.join(lines)

last_sig = None
while True:
    try: res = script.exports_sync.sweep()
    except Exception as e:
        out(f"sweep RPC failed: {e}"); time.sleep(15); continue
    if res.get('err'):
        out(f"sweep: {res['err']}")
    else:
        live = res['live']; detail = res['detail']
        sig = json.dumps(detail, sort_keys=True)
        if sig != last_sig:
            last_sig = sig
            out(f"=== SWEEP: {len(live)} live regions (array={res.get('count')}) ===")
            out("  live: " + ', '.join(f"{b['nm']}[f={b['flag']},d={b['dead']},A={b['na']},B={b['nb']}]" for b in live))
            for d in detail:
                out(f"  [idx {d['i']}] {d['nm']}  navmeshOK={d['flag']} dead={d['dead']}")
                out(fmt_portals('A(+0x8c) ', d['pa']))
                out(fmt_portals('B(+0x128)', d['pb']))
            out("=== END SWEEP ===")
    time.sleep(15)
