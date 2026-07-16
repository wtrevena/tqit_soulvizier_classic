"""End-to-end verification for SVAERA adopt candidates.
Builds a FULL incoming-reference index over the SVAERA arz (one decode pass),
indexes base-game + our-shipped + SVAERA arcs for art resolution, resolves
Text tags, then evaluates each target record:
  - ABSENT from our effective DB?  (truly missing)
  - present + well-formed in SVAERA? name/desc resolves?
  - incoming references in SVAERA (loot/set/proxy) => FUNCTIONAL vs CUT
  - art (bitmap + mesh) -> SHIPPED (base or our arc) / SVAERA-ONLY arc / unknown
  - xpack skill-grant coupling?
"""
import sys
from pathlib import Path
from collections import Counter, defaultdict

TOOLS = r"C:\Users\willi\repos\tqit_soulvizier_classic\tools"
sys.path.insert(0, TOOLS)
from arz_patcher import ArzDatabase
from arc_patcher import ArcArchive

SV_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\475150\2076433374\SVAERA_customquest")
SVAERA_ARZ = SV_ROOT / "Database" / "SVAERA_customquest.arz"
SVAERA_TEXT = SV_ROOT / "Resources" / "Text.arc"
OUR_RES = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources")
GAME_RES = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Resources")
BASE_ARZ = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Database\database.arz")
OUR_ARZ = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz")

def log(*a): print(*a, file=sys.stderr)
def norm(s): return str(s).replace('/', '\\').lower().strip()

# ---- art indexes ----
def index_arc(path):
    try:
        arc = ArcArchive.from_file(path)
        return {norm(e.name) for e in arc.entries if e.name}
    except Exception as e:
        log(f"arc fail {path.name}: {e}"); return set()

log("indexing arcs (our + base + svaera)...")
ARC_INDEX = {}  # logical arc-name -> ('ours'|'base'|'svaera', set)
def add_arc(path, origin):
    nm = path.stem.lower()
    idx = index_arc(path)
    if nm not in ARC_INDEX:
        ARC_INDEX[nm] = (origin, set())
    ARC_INDEX[nm][1].update(idx)
for p in OUR_RES.glob("*.arc"): add_arc(p, 'ours')
for nm in ['Items','Creatures','XPack','Effects','Text_EN']:
    p = GAME_RES / f"{nm}.arc"
    if p.exists(): add_arc(p, 'base')
# base-game xpack subfolder arcs
for sub in ['XPack','XPack2','XPack3','XPack4']:
    d = GAME_RES / sub
    if d.exists():
        for p in d.glob("*.arc"): add_arc(p, 'base')
for nm in ['SVMesh','SVItems','SVTextures','SVEffects','Creatures','SV_NewSkins','N66_Mods','drx','Items']:
    p = SV_ROOT / "Resources" / f"{nm}.arc"
    if p.exists(): add_arc(p, 'svaera')
log(f"indexed arcs: {sorted(ARC_INDEX)}")

SHIP_ARCS = {'ours','base'}  # arcs we effectively have at runtime
def art_status(resref):
    if not resref or '\\' not in norm(resref):
        return 'none'
    rn = norm(resref)
    arcname, _, entry = rn.partition('\\')
    if arcname in ARC_INDEX:
        origin, idx = ARC_INDEX[arcname]
        if entry in idx:
            return 'SHIPPED' if origin in SHIP_ARCS else f'SVAERA-ONLY:{arcname}'
        # arc known but entry missing -> maybe in a different copy; check svaera copy under same name is impossible (merged). report missing
        return f'MISSING-IN-{origin}:{arcname}'
    return f'UNINDEXED-ARC:{arcname}'

# ---- SVAERA arz + full ref index ----
log("loading SVAERA arz...")
SV = ArzDatabase.from_arz(SVAERA_ARZ)
SVN = {norm(n): n for n in SV.record_names()}
log("building full incoming-reference index (decode all)...")
INCOMING = Counter()
FIELD_OF = defaultdict(Counter)  # target -> Counter(referrer-field)
n=0
for real in SV.record_names():
    ff = SV.get_fields(real)
    n+=1
    if n % 20000 == 0: log(f"  {n}...")
    if not ff: continue
    for k, tf in ff.items():
        fbase = k.split('###')[0]
        for v in tf.values:
            if isinstance(v, str) and v.endswith('.dbr') and '\\' in v:
                nv = norm(v)
                INCOMING[nv]+=1
                FIELD_OF[nv][fbase]+=1
log("ref index done.")

log("loading base + our name sets...")
BASE = ArzDatabase.from_arz(BASE_ARZ); BN={norm(n) for n in BASE.record_names()}
OUR = ArzDatabase.from_arz(OUR_ARZ); ON={norm(n) for n in OUR.record_names()}
EFF = BN|ON

log("loading text...")
TXT = ArcArchive.from_file(SVAERA_TEXT); TAGS={}
for e in TXT.entries:
    if not e.name or not e.name.lower().endswith('.txt'): continue
    try: data=TXT.decompress(e)
    except Exception: continue
    txt=None
    for enc in ('utf-16-le','utf-8','latin-1'):
        try: txt=data.decode(enc); break
        except Exception: pass
    if not txt: continue
    for line in txt.splitlines():
        if '=' in line:
            k,_,v=line.partition('='); k=k.strip()
            if k and k.lower() not in TAGS: TAGS[k.lower()]=v.strip()
def rtag(t): return TAGS.get(t.lower(),'') if t else ''

def flat(nname):
    real=SVN.get(nname)
    if not real: return None
    ff=SV.get_fields(real)
    if not ff: return {}
    out={}
    for k,tf in ff.items():
        b=k.split('###')[0]
        if b not in out: out[b]=';'.join(str(x) for x in tf.values)
    return out

def has_xpack_skill(ff):
    for kk in ('itemSkillName','petBonusName','skillName'):
        v=ff.get(kk,'')
        if 'xpack2' in v.lower() or 'xpack3' in v.lower() or 'xpack4' in v.lower():
            return v
    return ''

def evaluate(name, label=''):
    nn=norm(name)
    print(f"\n=== {label or name} ===")
    print(f"  record: {name}")
    ff=flat(nn)
    if ff is None:
        print("  !! NOT IN SVAERA"); return
    absent = nn not in EFF
    print(f"  ABSENT from effective-ours: {absent}")
    cls=ff.get('Class','?'); print(f"  Class={cls} classification={ff.get('itemClassification','')}")
    nm=rtag(ff.get('itemNameTag','')) or rtag(ff.get('description','')) or rtag(ff.get('setName',''))
    print(f"  name/desc resolves: '{nm}'  (tag={ff.get('itemNameTag') or ff.get('description') or ff.get('setName')})")
    inc=INCOMING.get(nn,0)
    print(f"  incoming refs in SVAERA: {inc}  fields={dict(FIELD_OF.get(nn, {}))}")
    for artf in ('bitmap','mesh','shaderName'):
        if ff.get(artf):
            print(f"  art {artf}={ff[artf]} -> {art_status(ff[artf])}")
    xp=has_xpack_skill(ff)
    if xp: print(f"  !! xpack skill grant: {xp}")
    # set members
    if ff.get('setMembers'):
        print(f"  setMembers={ff['setMembers']}")
        for m in ff['setMembers'].split(';'):
            if not m.strip(): continue
            mff=flat(norm(m))
            if mff is None:
                print(f"      MEMBER MISSING IN SVAERA: {m}"); continue
            mabsent = norm(m) not in EFF
            mnm=rtag(mff.get('itemNameTag',''))
            print(f"      member absent={mabsent} name='{mnm}' bitmap->{art_status(mff.get('bitmap',''))} mesh->{art_status(mff.get('mesh',''))} refs={INCOMING.get(norm(m),0)}")

TARGETS = [
    ('records\\item\\sets\\drxset051.dbr', "SET: Hector's Bronze Armor"),
    ('records\\item\\sets\\drxset053.dbr', "SET: Patroclus' Disguise"),
    ('records\\item\\sets\\drxset058.dbr', "SET: Might of Hephaestus"),
    ('records\\item\\sets\\newset002.dbr', "SET: The Hunting Paradox"),
    ('records\\item\\sets\\newset005.dbr', "SET: The Elephantine Triad"),
    ('sv_ew\\creature\\monster\\oceanid\\am_moonmaiden_13.dbr', "MONSTER: Artemisian Oceanid Moon Maiden"),
    ('sv_ew\\creature\\monster\\moonwolf\\bm_moonwolf_10.dbr', "MONSTER: Moon Wolf Hound of Artemis"),
    ('records\\item\\equipmentweapon\\club\\u_mod_meteorite.dbr', "UNIQUE: Meteorite (mace)"),
]
for t, lab in TARGETS:
    evaluate(t, lab)
