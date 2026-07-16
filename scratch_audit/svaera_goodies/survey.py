"""Comprehensive SVAERA goodies survey. Loads all 4 DBs ONCE and:
  A) For each interesting authored-new family: count, sample records (Class,
     template, name tag, in-SV098?), and XPack-coupling scan.
  B) Provenance: are all_sv\* records genuinely new or relocated SV dupes?
     (compare field signatures against SV098 records with matching leaf name)
  C) Divergence: for content records common to SVAERA & base & SV098, count how
     many SVAERA diverges from BOTH -> SVAERA-authored rebalance/fix.
Writes scratch_audit/svaera_goodies/survey_out.txt
"""
import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, r"C:\Users\willi\repos\tqit_soulvizier_classic\tools")
from arz_patcher import ArzDatabase

PATHS = {
    'sv':   Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\475150\2076433374\SVAERA_customquest\Database\SVAERA_customquest.arz"),
    'our':  Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz"),
    'sv098':Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Database\database.arz"),
    'base': Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Database\database.arz"),
}

def norm(s):
    return str(s).replace('/', '\\').lower().strip()

print("loading DBs...", file=sys.stderr)
DB = {k: ArzDatabase.from_arz(p) for k, p in PATHS.items()}
NAMES = {k: {norm(n): n for n in DB[k].record_names()} for k in DB}
print("loaded.", file=sys.stderr)

base_n = set(NAMES['base'])
our_n = set(NAMES['our'])
sv098_n = set(NAMES['sv098'])
sv_n = set(NAMES['sv'])
eff_ours = our_n | base_n
absent = sv_n - eff_ours

OUT = open(r"C:\Users\willi\repos\tqit_soulvizier_classic\scratch_audit\svaera_goodies\survey_out.txt", 'w', encoding='utf-8')
def w(*a):
    print(*a, file=OUT)

def flat(dbk, nname):
    real = NAMES[dbk].get(nname)
    if real is None:
        return None
    ff = DB[dbk].get_fields(real)
    if not ff:
        return {}
    out = {}
    for k, tf in ff.items():
        b = k.split('###')[0]
        if b not in out:
            out[b] = ';'.join(str(v) for v in tf.values)
    return out

def name_tag(ff):
    for kk in ('itemNameTag', 'description', 'skillDisplayName', 'actorName', 'monsterName', 'itemSetName', 'petBonusName'):
        if ff.get(kk):
            return f"{kk}={ff[kk]}"
    return ''

def xpack_coupled(ff):
    """True if any string value references xpack art/skills/records (DLC coupling)."""
    for v in ff.values():
        lv = v.lower()
        if 'xpack2' in lv or 'xpack3' in lv or 'xpack4' in lv or '\\xpack\\' in lv:
            return True
    return False

def survey_family(fam, limit=10):
    matches = sorted(x for x in absent if fam in x)
    w(f"\n{'='*70}\n### FAMILY '{fam}': {len(matches)} records absent-from-ours")
    cls_counter = Counter()
    coupled = 0
    in098 = 0
    for nn in matches:
        ff = flat('sv', nn) or {}
        cls_counter[ff.get('Class', '?')] += 1
        if xpack_coupled(ff):
            coupled += 1
        if nn in sv098_n:
            in098 += 1
    w(f"  Class histogram: {dict(cls_counter.most_common(8))}")
    w(f"  xpack-coupled: {coupled}/{len(matches)}   also-in-SV098(same path): {in098}")
    w(f"  --- sample (up to {limit}) ---")
    for nn in matches[:limit]:
        real = NAMES['sv'][nn]
        ff = flat('sv', nn) or {}
        cls = ff.get('Class', '?')
        tmpl = Path(ff.get('templateName', '?')).name
        cp = 'XPACK' if xpack_coupled(ff) else ''
        w(f"    {cls:20} {tmpl:24} {cp:5} {real}")
        nt = name_tag(ff)
        if nt:
            w(f"        {nt}")

# ---- A) authored-new content families ----
CONTENT_FAMILIES = [
    'all_sv\\item', 'all_sv\\skills', 'all_sv\\creature',
    'skills\\soulskills', 'item\\sets', 'item\\equipmentring',
    'item\\equipmentweapon', 'creature\\monster', 'creature\\npc',
    'creature\\hero', 'sv_endgame', 'game\\svic', 'sv_ew',
    'item\\artifacts', 'item\\relics', 'item\\animalrelics', 'item\\charms',
    'skills\\item skills', 'item\\petbonus', 'effects\\weaponenchantments',
    'item\\attachitems', 'item\\questitems',
]
for fam in CONTENT_FAMILIES:
    survey_family(fam)

# ---- B) all_sv provenance: relocated SV dupe or genuinely new? ----
w(f"\n{'='*70}\n### PROVENANCE CHECK: all_sv leaf-name overlap with SV098")
# build map of SV098 leaf-names (last path component) -> full name
def leaf(nn):
    return nn.split('\\')[-1]
sv098_leaf = defaultdict(list)
for nn in sv098_n:
    sv098_leaf[leaf(nn)].append(nn)
our_leaf = defaultdict(list)
for nn in our_n:
    our_leaf[leaf(nn)].append(nn)

for fam in ('all_sv\\item', 'all_sv\\skills', 'all_sv\\creature'):
    matches = sorted(x for x in absent if fam in x)
    leaf_in098 = sum(1 for x in matches if leaf(x) in sv098_leaf)
    leaf_inour = sum(1 for x in matches if leaf(x) in our_leaf)
    w(f"  {fam}: {len(matches)} recs; leaf-name matches SV098={leaf_in098}, matches OURS={leaf_inour}")
    # show a few examples of leaf matches (candidate relocated dupes)
    shown = 0
    for x in matches:
        if leaf(x) in our_leaf and shown < 5:
            w(f"     DUPE? {x}  <->  {our_leaf[leaf(x)][0]}")
            shown += 1

OUT.close()
print("wrote survey_out.txt", file=sys.stderr)
