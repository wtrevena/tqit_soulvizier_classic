"""Frida probe #2: the navmesh LOADS fine (proven), so the wall is the inter-level
WALK LINK. Hook Region::FindCrossedPortal @ base+0x20c110 (thiscall, ecx=region);
it iterates the region's portal array [region+0x8c .. +0x90] and each portal has a
destination-region GUID (portal+0xdc per the disasm). Dump, per region, the list of
destination levels its portals point to -> see whether the passage region even HAS a
portal to the blood room. Read-only. Self-validating: if the dumped dest-GUIDs map to
real level names, the struct offsets are right.

Auto-attaches when TQ.exe is running. In-game: stand in the passage and CLICK to move
(esp. toward the wall) so FindCrossedPortal runs on the passage's region.
Log: scratchpad/frida_portals.log
"""
import sys, time, json
from pathlib import Path
REPO = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic")
sys.path.insert(0, str(REPO / 'tools'))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
DEP = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic\Resources\Levels.arc")
LOG = Path(r"C:\Users\willi\AppData\Local\Temp\claude\C--Users-willi-repos\fc31fa12-e2e4-44ef-998c-7fe110587b8c\scratchpad\frida_portals.log")

print("parsing map for GUID->name ...", flush=True)
arc = ArcArchive.from_file(DEP)
data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
sec = {s['type']: s for s in parse_sections(data)}
guid2name = {}
cluster = set()
for lv in parse_level_index(data, sec[SEC_LEVELS]):
    key = lv['fname'].replace('\\', '/').lower(); base = key.split('/')[-1].replace('.lvl', '')
    guid2name[lv['ints_raw'][36:52].hex()] = base
    if 'xbloodcave' in key or base == 'random09a': cluster.add(base)
print(f"  {len(guid2name)} levels; {len(cluster)} cluster", flush=True)

import frida
JS = r"""
const GUIDMAP = __GUIDMAP__; const CLUSTER = __CLUSTER__;
const base = Process.getModuleByName('Engine.dll').base;
const FCP = base.add(0x20c110);   // Region::FindCrossedPortal (ecx = region)
send({t:'info', m:'Engine.dll base='+base+'  FindCrossedPortal='+FCP});
function hx(ptr,n){ try{ const b=new Uint8Array(ptr.readByteArray(n)); let s='';
  for(let i=0;i<n;i++) s+=('0'+b[i].toString(16)).slice(-2); return s; }catch(e){ return null; } }
const dumped = {};   // region ptr -> already fully reported (skip expensive rescan => no lag)
// try several plausible portal-struct dest-GUID offsets; pick whichever yields known names
const GUID_OFFS = [0xdc, 0xd8, 0xe0, 0x2e8, 0x1c, 0x20];
Interceptor.attach(FCP, {
  onEnter(args){
    const region = this.context.ecx;
    try {
      if (region.isNull()) return;
      const rkey = region.toString();
      if (dumped[rkey]) return;                  // already handled this region -> cheap early-out
      const beg = region.add(0x8c).readPointer();
      const end = region.add(0x90).readPointer();
      if (beg.isNull() || end.isNull()) return;
      const bytes = end.sub(beg).toInt32();
      if (bytes < 0 || bytes > 0x4000) return;   // sanity
      const nptr = bytes >> 2;                    // assume Portal* array
      if (nptr <= 0 || nptr > 256) return;
      // build a list of dest-level names across the portals
      let dests = [];
      for (let i=0;i<nptr;i++){
        let portal; try { portal = beg.add(i*4).readPointer(); } catch(e){ continue; }
        if (portal.isNull()) continue;
        // find the dest GUID by trying candidate offsets
        for (const off of GUID_OFFS){
          const g = hx(portal.add(off), 16);
          if (g && GUIDMAP[g]) { dests.push(GUIDMAP[g]+'@'+off.toString(16)); break; }
        }
      }
      dumped[rkey] = 1;                          // mark handled (valid array seen) => no rescan
      const sig = dests.sort().join(',');
      const hasCluster = dests.some(d => CLUSTER.indexOf(d.split('@')[0])>=0);
      send({t:'portals', region:rkey, count:nptr, dests:dests, cluster:hasCluster});
    } catch(e){}
  }
});
send({t:'info', m:'FindCrossedPortal hook installed - CLICK to move in-game'});
"""
JS = JS.replace('__GUIDMAP__', json.dumps(guid2name)).replace('__CLUSTER__', json.dumps(sorted(cluster)))
logf = open(LOG, 'w', encoding='utf-8')
def out(s):
    line = time.strftime('%H:%M:%S ') + s; print(line, flush=True); logf.write(line+'\n'); logf.flush()
def on_message(msg, _):
    if msg['type'] == 'error': out('JS ERROR: '+msg.get('description','')); return
    p = msg.get('payload', {}); t = p.get('t')
    if t == 'info': out('[info] '+p['m'])
    elif t == 'portals':
        tag = '  <<< HAS CLUSTER DEST' if p['cluster'] else ''
        out(f"[region {p['region']}] {p['count']} portals -> dests={p['dests']}{tag}")
out("waiting for TQ.exe ...")
session = None
for i in range(1800):
    try: session = frida.attach("TQ.exe"); break
    except Exception:
        if i % 15 == 0: out("  ... still waiting for TQ.exe")
        time.sleep(2)
if session is None: out("TQ.exe not found; stopping."); sys.exit(2)
out("ATTACHED"); script = session.create_script(JS); script.on('message', on_message); script.load()
out(">>> hook loaded. In-game: stand in the passage and CLICK toward the wall a few times.")
try:
    while True: time.sleep(5)
except KeyboardInterrupt: out("stopped.")
