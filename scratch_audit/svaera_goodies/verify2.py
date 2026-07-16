"""Second verify pass: Robes of the Pythia + Thoth's Favor sets art status,
plus classification/level of the 3 fully-shipped Greek sets' members, plus a
curated legendary-uniques theme/art sample."""
import sys
from pathlib import Path

TOOLS = r"C:\Users\willi\repos\tqit_soulvizier_classic\tools"
sys.path.insert(0, TOOLS)
from arz_patcher import ArzDatabase
from arc_patcher import ArcArchive

SV_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\475150\2076433374\SVAERA_customquest")
OUR_RES = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources")
GAME_RES = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Resources")

def norm(s): return str(s).replace('/', '\\').lower().strip()
def log(*a): print(*a, file=sys.stderr)

ARC_INDEX={}
def add_arc(path, origin):
    try: arc=ArcArchive.from_file(path)
    except Exception: return
    nm=path.stem.lower()
    ARC_INDEX.setdefault(nm,(origin,set()))[1].update(norm(e.name) for e in arc.entries if e.name)
for p in OUR_RES.glob("*.arc"): add_arc(p,'ours')
for nm in ['Items','Creatures']:
    p=GAME_RES/f"{nm}.arc"
    if p.exists(): add_arc(p,'base')
for sub in ['XPack','XPack2','XPack3','XPack4']:
    d=GAME_RES/sub
    if d.exists():
        for p in d.glob("*.arc"): add_arc(p,'base')
SHIP={'ours','base'}
def art(resref):
    if not resref or '\\' not in norm(resref): return 'none'
    a,_,e=norm(resref).partition('\\')
    if a in ARC_INDEX:
        o,idx=ARC_INDEX[a]
        return ('SHIPPED' if o in SHIP else f'SV-ONLY:{a}') if e in idx else f'MISSING:{a}'
    return f'UNIDX:{a}'

SV=ArzDatabase.from_arz(SV_ROOT/"Database"/"SVAERA_customquest.arz")
SVN={norm(n):n for n in SV.record_names()}
TXT=ArcArchive.from_file(SV_ROOT/"Resources"/"Text.arc"); TAGS={}
for e in TXT.entries:
    if not e.name or not e.name.lower().endswith('.txt'): continue
    try: d=TXT.decompress(e)
    except Exception: continue
    t=None
    for enc in ('utf-16-le','utf-8','latin-1'):
        try: t=d.decode(enc); break
        except Exception: pass
    if not t: continue
    for ln in t.splitlines():
        if '=' in ln:
            k,_,v=ln.partition('='); k=k.strip()
            if k and k.lower() not in TAGS: TAGS[k.lower()]=v.strip()
def rtag(t): return TAGS.get(t.lower(),'') if t else ''
def flat(nn):
    r=SVN.get(nn)
    if not r: return None
    ff=SV.get_fields(r)
    if not ff: return {}
    o={}
    for k,tf in ff.items():
        b=k.split('###')[0]
        if b not in o: o[b]=';'.join(str(x) for x in tf.values)
    return o

def show_set(rec):
    ff=flat(norm(rec))
    if ff is None: print(f"{rec}: MISSING"); return
    print(f"\n{rec}  set='{rtag(ff.get('setName',''))}'")
    for m in ff.get('setMembers','').split(';'):
        if not m.strip(): continue
        mff=flat(norm(m))
        if mff is None: print(f"   MEMBER MISSING {m}"); continue
        print(f"   {mff.get('itemClassification',''):10} lv{mff.get('levelRequirement','') or mff.get('itemLevel',''):>3} '{rtag(mff.get('itemNameTag',''))}' bmp->{art(mff.get('bitmap',''))} msh->{art(mff.get('mesh',''))}")

for s in ['records\\item\\sets\\drxset052.dbr','records\\item\\sets\\drxset049.dbr',
          'records\\item\\sets\\drxset051.dbr','records\\item\\sets\\drxset053.dbr',
          'records\\item\\sets\\drxset058.dbr']:
    show_set(s)

print("\n--- curated legendary uniques: theme + art ---")
for u in ['records\\item\\equipmentweapon\\staff\\u_mod_scepteroflamashtu.dbr',
          'records\\item\\equipmentweapon\\club\\u_mod_stormcrack.dbr',
          'records\\item\\equipmentweapon\\club\\u_mod_naturesrevenge.dbr',
          'records\\item\\equipmenthelm\\_u_mod_osirisatef.dbr',
          'records\\item\\equipmentamulet\\u_mod_vengeanceofsekhmet.dbr',
          'records\\item\\equipmentring\\u_mod_symbolofhathor.dbr']:
    ff=flat(norm(u))
    if ff is None: print(f"  MISSING {u}"); continue
    print(f"  [{ff.get('itemClassification','')}] '{rtag(ff.get('itemNameTag',''))}' lv{ff.get('levelRequirement','')} bmp->{art(ff.get('bitmap',''))} msh->{art(ff.get('mesh',''))}")
