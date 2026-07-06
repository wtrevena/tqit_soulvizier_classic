"""Frida probe: hook TQAE Engine.dll navmesh loader (ProcessRLTD @ base+0x1f4ba0,
image base 0x10000000). For EVERY navmesh the engine tries to load, log WHICH
level (own GUID -> name) and whether it SUCCEEDS or is REJECTED, plus its
dependency GUID list. Read-only (hooks only observe + log).

Auto-attaches when TQ.exe appears (polls up to 60 min, heartbeat every 30s).
Answers, for the blood-cave cluster:
  - BC never appears -> its navmesh load is never attempted (region/streaming).
  - BC REJECTED      -> navmesh gate fails (log shows its dependency list).
  - BC OK            -> navmesh loads fine; the block is downstream (linker).

Log: scratchpad/frida_probe.log  (also prints live).
"""
import sys, time, json
from pathlib import Path

REPO = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic")
sys.path.insert(0, str(REPO / 'tools'))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

DEP = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic\Resources\Levels.arc")
LOG = Path(r"C:\Users\willi\AppData\Local\Temp\claude\C--Users-willi-repos\fc31fa12-e2e4-44ef-998c-7fe110587b8c\scratchpad\frida_probe.log")

print("parsing deployed map for GUID->name map ...", flush=True)
arc = ArcArchive.from_file(DEP)
data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
sec = {s['type']: s for s in parse_sections(data)}
guid2name = {}
cluster = set()
for lv in parse_level_index(data, sec[SEC_LEVELS]):
    key = lv['fname'].replace('\\', '/').lower()
    base = key.split('/')[-1].replace('.lvl', '')
    guid2name[lv['ints_raw'][36:52].hex()] = base
    if 'xbloodcave' in key or base == 'random09a':
        cluster.add(base)
print(f"  {len(guid2name)} levels mapped; {len(cluster)} in the blood-cave cluster", flush=True)

import frida

JS = r"""
const GUIDMAP = __GUIDMAP__;
const CLUSTER = __CLUSTER__;
const base = Process.getModuleByName('Engine.dll').base;
const PROC = base.add(0x1f4ba0);
send({t:'info', m:'Engine.dll base=' + base + '  ProcessRLTD=' + PROC});
function hx(ptr, n){ try { const b=new Uint8Array(ptr.readByteArray(n)); let s='';
  for (let i=0;i<n;i++) s+=('0'+b[i].toString(16)).slice(-2); return s; } catch(e){ return null; } }
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
    this.rec=findREC(this.context,args); this.nm=null;
    if (this.rec){
      const gc=this.rec.add(12).readU32();
      const own=hx(this.rec.add(16),16);
      const nm=GUIDMAP[own]||('?'+(own?own.slice(0,8):'??'));
      let deps=[]; if (gc>0&&gc<64){ for(let i=0;i<gc;i++){ const g=hx(this.rec.add(16+i*16),16); deps.push(GUIDMAP[g]||('?'+(g?g.slice(0,8):''))); } }
      this.nm=nm;
      send({t:'proc', n:++n, lvl:nm, gc:gc, deps:deps, cluster:CLUSTER.indexOf(nm)>=0});
    } else { send({t:'proc_unk', n:++n}); }
  },
  onLeave(ret){
    if (this.nm!==null){ const r=ret.toInt32();
      send({t:'result', lvl:this.nm, ret:r, ok:(r!==0), cluster:CLUSTER.indexOf(this.nm)>=0}); }
  }
});
send({t:'info', m:'HOOK INSTALLED on ProcessRLTD - walk to the wall now'});
"""
JS = JS.replace('__GUIDMAP__', json.dumps(guid2name)).replace('__CLUSTER__', json.dumps(sorted(cluster)))

logf = open(LOG, 'w', encoding='utf-8')
def out(s):
    line = time.strftime('%H:%M:%S ') + s
    print(line, flush=True); logf.write(line+'\n'); logf.flush()

results = {}          # cluster level -> 'OK'/'REJECTED'
last_summary = [0]
def summary(force=False):
    now = time.time()
    if not force and now - last_summary[0] < 15:
        return
    last_summary[0] = now
    if results:
        out('  --- cluster navmesh loads so far: ' +
            ', '.join(f'{k}={v}' for k, v in sorted(results.items())) + ' ---')

def on_message(msg, _):
    if msg['type'] == 'error':
        out('JS ERROR: ' + msg.get('description', '')); return
    p = msg.get('payload', {}); t = p.get('t')
    if t == 'info':
        out('[info] ' + p['m'])
    elif t == 'proc':
        if p['cluster']:
            out(f"[LOAD #{p['n']}] CLUSTER {p['lvl']:30s} guids={p['gc']} deps={p['deps']}")
    elif t == 'result':
        if p['cluster']:
            v = 'OK' if p['ok'] else 'REJECTED'
            results[p['lvl']] = v
            mark = '' if p['ok'] else '   <<<<< REJECTED'
            out(f"      => {p['lvl']:30s} {v} (ret={p['ret']}){mark}")
            summary(force=not p['ok'])

out("waiting for TQ.exe (poll 2s, up to 60 min) ...")
session = None
for i in range(1800):
    try:
        session = frida.attach("TQ.exe"); break
    except Exception:
        if i % 15 == 0:
            out("  ... still waiting for TQ.exe to launch")
        time.sleep(2)
if session is None:
    out("TQ.exe never appeared; stopping."); sys.exit(2)
out("ATTACHED to TQ.exe")
script = session.create_script(JS)
script.on('message', on_message)
script.load()
out(">>> hook loaded. In-game: walk OUT of the cave then back IN toward the wall (forces a fresh load of the blood room while we watch).")
try:
    while True:
        time.sleep(5); summary()
except KeyboardInterrupt:
    out("stopped.")
