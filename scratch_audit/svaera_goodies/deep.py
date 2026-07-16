"""Deep-dive probe for SVAERA goodies. Loads SVAERA arz + SVAERA Text.arc +
arc filename indexes ONCE. Produces:
  - art-coupling classification (art in an arc we already ship vs SVAERA-only arc)
  - sv_ew bestiary enumeration (name, mesh, art-arc, DB-reference count)
  - named-unique equipment items (real resolving name, non-xpack)
  - NpcItemUpgrader summary
  - non-xpack item sets + member items
Writes scratch_audit/svaera_goodies/deep_out.txt
"""
import sys
from pathlib import Path
from collections import defaultdict, Counter

TOOLS = r"C:\Users\willi\repos\tqit_soulvizier_classic\tools"
sys.path.insert(0, TOOLS)
from arz_patcher import ArzDatabase
from arc_patcher import ArcArchive

SV_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\475150\2076433374\SVAERA_customquest")
SVAERA_ARZ = SV_ROOT / "Database" / "SVAERA_customquest.arz"
SVAERA_TEXT = SV_ROOT / "Resources" / "Text.arc"
OUR_RES = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources")
BASE_ARZ = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Database\database.arz")
OUR_ARZ = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz")

OUT = open(r"C:\Users\willi\repos\tqit_soulvizier_classic\scratch_audit\svaera_goodies\deep_out.txt", 'w', encoding='utf-8')
def w(*a): print(*a, file=OUT)
def log(*a): print(*a, file=sys.stderr)

def norm(s): return str(s).replace('/', '\\').lower().strip()

# ---- arc filename indexes ----
# SVAERA content arcs (which we may or may not ship) and OUR shipped arcs.
# Map lowercased entry-name -> True. Keyed by arc "logical name" (basename w/o .arc, lower).
def index_arc(path):
    try:
        arc = ArcArchive.from_file(path)
    except Exception as e:
        log(f"  arc fail {path.name}: {e}")
        return set()
    return {norm(e.name) for e in arc.entries if e.name}

log("indexing arcs...")
SV_ARCS = {}   # SVAERA-side
for nm in ['SVMesh', 'SVItems', 'SVTextures', 'SVEffects', 'Creatures', 'SV_NewSkins', 'N66_Mods', 'drx', 'Items']:
    p = SV_ROOT / "Resources" / f"{nm}.arc"
    if p.exists():
        SV_ARCS[nm.lower()] = index_arc(p)
        log(f"  SVAERA {nm}.arc: {len(SV_ARCS[nm.lower()])}")

OUR_ARCS = {}  # what we ship
for p in OUR_RES.glob("*.arc"):
    nm = p.stem.lower()
    OUR_ARCS[nm] = index_arc(p)
log(f"  our shipped arcs: {sorted(OUR_ARCS)}")

def art_status(resref):
    """Given a record art path 'ArcName\\entry\\path.msh', classify."""
    if not resref or '\\' not in resref:
        return ('none', resref)
    rn = norm(resref)
    arcname, _, entry = rn.partition('\\')
    # is entry in OUR shipped arc of that name?
    ours = OUR_ARCS.get(arcname)
    if ours is not None and entry in ours:
        return ('SHIPPED', arcname)
    # also many meshes ship under generic 'creatures\\...' inside base game arcs; we can't
    # index base-game arcs cheaply here, so treat base-game 'creatures\\'/'items\\' as likely-base
    svside = SV_ARCS.get(arcname)
    if svside is not None and entry in svside:
        return (f'SVAERA-ONLY:{arcname}', arcname)
    # unknown arc name (maybe base-game arc like 'creatures','items','xpack')
    if arcname in ('creatures', 'items', 'xpack', 'effects', 'skills', 'ui', 'characters'):
        return ('BASE-LIKELY', arcname)
    return ('UNKNOWN', arcname)

# ---- SVAERA arz + text ----
log("loading SVAERA arz...")
SV = ArzDatabase.from_arz(SVAERA_ARZ)
SVN = {norm(n): n for n in SV.record_names()}
log("loading base + our name sets...")
BASE = ArzDatabase.from_arz(BASE_ARZ); BN = {norm(n) for n in BASE.record_names()}
OUR = ArzDatabase.from_arz(OUR_ARZ); ON = {norm(n) for n in OUR.record_names()}
EFF = BN | ON
absent = set(SVN) - EFF

log("loading SVAERA Text.arc...")
TXT = ArcArchive.from_file(SVAERA_TEXT)
TAGS = {}
for e in TXT.entries:
    if not e.name or not e.name.lower().endswith('.txt'):
        continue
    try:
        data = TXT.decompress(e)
    except Exception:
        continue
    for enc in ('utf-16-le', 'utf-8', 'latin-1'):
        try:
            txt = data.decode(enc)
            break
        except Exception:
            txt = None
    if not txt:
        continue
    for line in txt.splitlines():
        if '=' in line:
            k, _, v = line.partition('=')
            k = k.strip()
            if k and k not in TAGS:
                TAGS[k.lower()] = v.strip()
log(f"  loaded {len(TAGS)} tags")

def resolve_tag(t):
    if not t: return ''
    return TAGS.get(t.lower(), '')

def flat(nname):
    real = SVN.get(nname)
    if not real: return {}
    ff = SV.get_fields(real)
    if not ff: return {}
    out = {}
    for k, tf in ff.items():
        b = k.split('###')[0]
        if b not in out:
            out[b] = ';'.join(str(v) for v in tf.values)
    return out

# ---- build a targeted reference index: scan proxy/pool/generator/nest/spawn records ----
log("building reference index (prox/pool/gen/nest/spawn)...")
REFERRERS = defaultdict(list)  # target-norm -> [referrer names]
ref_scan_names = [n for n in SVN if any(k in n for k in ('prox', 'pool', 'generator', 'nest', 'spawn', 'boss', 'quest'))]
log(f"  scanning {len(ref_scan_names)} candidate referrer records")
for rn in ref_scan_names:
    ff = SV.get_fields(SVN[rn])
    if not ff: continue
    for k, tf in ff.items():
        for v in tf.values:
            if isinstance(v, str) and ('\\' in v) and v.lower().endswith('.dbr'):
                REFERRERS[norm(v)].append(rn)

def ref_count(nname):
    return len(REFERRERS.get(nname, []))

# =====================================================================
# A) sv_ew bestiary
w("="*72)
w("### sv_ew BESTIARY (SVAERA 'extra wildlife' namespace, low xpack coupling)")
ew_monsters = sorted(n for n in absent if n.startswith('sv_ew\\') and 'monster' in flat(n).get('Class','').lower())
# also catch by templateName monster.tpl
ew_all = sorted(n for n in absent if n.startswith('sv_ew\\'))
mon = []
for n in ew_all:
    ff = flat(n)
    if 'monster.tpl' in ff.get('templateName','').lower():
        mon.append(n)
w(f"sv_ew total records: {len(ew_all)}; monster.tpl records: {len(mon)}")
# group by creature folder (sv_ew\creature\monster\<folder>\...)
by_folder = defaultdict(list)
for n in ew_all:
    parts = n.split('\\')
    # sv_ew, creature, monster, <folder>, ...
    folder = parts[3] if len(parts) > 3 else parts[-1]
    by_folder[folder].append(n)
w(f"folders: {sorted(by_folder)}")
for folder in sorted(by_folder):
    recs = by_folder[folder]
    mons = [r for r in recs if 'monster.tpl' in flat(r).get('templateName','').lower()]
    w(f"\n  -- folder '{folder}': {len(recs)} recs, {len(mons)} monster records")
    for r in mons[:8]:
        ff = flat(r)
        nm = resolve_tag(ff.get('description','')) or ff.get('description','')
        cls = ff.get('monsterClassification','?')
        mesh = ff.get('actorClass') or ''
        # meshes come from charAnimTable-> we approximate via 'skinName'/'chestMesh' etc; scan art refs
        art_refs = [v for kk, v in ff.items() for v in [ff[kk]] if isinstance(v, str) and ('.msh' in v.lower() or '.tex' in v.lower())]
        w(f"     {cls:10} rc={ref_count(r):2} name='{nm}'  {r}")
        # art via mesh field
        meshf = ff.get('mesh') or ff.get('chestMesh') or ''
        if meshf:
            st, arc = art_status(meshf)
            w(f"                mesh={meshf} [{st}]")

# =====================================================================
# B) named-unique equipment (real resolving name, non-xpack)
w("\n" + "="*72)
w("### NAMED-UNIQUE EQUIPMENT (absent, itemNameTag resolves, non-xpack art)")
EQUIP_CLASSES = ('WeaponMelee', 'WeaponHunting', 'WeaponMagical', 'WeaponArmor',
                 'ArmorProtective', 'ArmorJewelry')
def xpack_coupled(ff):
    for v in ff.values():
        lv = v.lower()
        if 'xpack2' in lv or 'xpack3' in lv or 'xpack4' in lv or '\\xpack\\' in lv:
            return True
    return False
uniques = []
for n in absent:
    ff = flat(n)
    cls = ff.get('Class','')
    if not any(cls.startswith(c) for c in EQUIP_CLASSES):
        continue
    tag = ff.get('itemNameTag','')
    nm = resolve_tag(tag)
    classi = ff.get('itemClassification','')
    if not nm:
        continue
    if classi.lower() not in ('rare','epic','legendary','unique','monsterinfrequent'):
        # keep only "unique-ish" quality to cut noise
        if classi.lower() not in ('quest',):
            pass
    uniques.append((classi, cls, nm, tag, n, ff))
# sort: legendary/epic first
order = {'legendary':0,'epic':1,'rare':2,'monsterinfrequent':3,'unique':1}
uniques.sort(key=lambda t: (order.get(t[0].lower(), 9), t[0], t[2]))
w(f"total named uniques (absent, resolving tag): {len(uniques)}")
cnt_by_cls = Counter(t[0] for t in uniques)
w(f"by classification: {dict(cnt_by_cls)}")
shown = 0
for classi, cls, nm, tag, n, ff in uniques:
    if xpack_coupled(ff):
        continue
    if classi.lower() not in ('legendary','epic','rare','monsterinfrequent'):
        continue
    meshf = ff.get('bitmap') or ff.get('mesh') or ''
    st, arc = art_status(meshf) if meshf else ('none','')
    lvl = ff.get('itemLevel','') or ff.get('levelRequirement','')
    w(f"  [{classi:14}] {cls:22} lv{lvl:>3} '{nm}'  [{st}]  {n}")
    shown += 1
    if shown >= 45:
        w("  ... (truncated)")
        break

# =====================================================================
# C) NpcItemUpgrader
w("\n" + "="*72)
w("### NpcItemUpgrader (QoL item-upgrade NPCs)")
upg = sorted(n for n in absent if flat(n).get('Class','') == 'NpcItemUpgrader')
w(f"count: {len(upg)}")
for n in upg[:6]:
    ff = flat(n)
    w(f"  {n}")
    for kk in ('description','upgradeItems','upgradeCost','specialConversationOffset'):
        if ff.get(kk):
            w(f"      {kk}={ff[kk][:100]}")

# =====================================================================
# D) non-xpack item sets + member items
w("\n" + "="*72)
w("### NON-XPACK ITEM SETS")
sets_ = sorted(n for n in absent if n.startswith('records\\item\\sets\\') and flat(n).get('templateName','').lower().endswith('itemset.tpl'))
for n in sets_:
    ff = flat(n)
    if xpack_coupled(ff):
        continue
    setname = resolve_tag(ff.get('setName','')) or ff.get('setName','')
    members = [v for kk, tf_v in ff.items() for v in [ff[kk]] if kk.startswith('setMembers')]
    w(f"  {n}  name='{setname}'")
    mm = ff.get('setMembers','')
    if mm:
        w(f"      members={mm}")

OUT.close()
log("wrote deep_out.txt")
