r"""svc_craft_thrown.py - THE CRAFT-CHAIN + THROWN-CLASS CONTRACT (Will 2026-08-10).

WILL, VERBATIM (2026-08-10)
---------------------------
"i meant do the mythic formulas drop. they can drop in normal as well, but the
legendary items should not drop in normal. All of the reagents need to be droppable
somewhere in the game, ideally from chests since that is where people will look. if
players farm legendary long enough, they should be able to find all the reagents
without having to farm a specific area or a specific character (except for the monster
unique droppable items like the green items that are needed to build some of the
formulas...). Yes we should make the legendary thrown weapons droppable."

THREE DEFECTS, ALL MEASURED ON THE LIVE arz 435cc485 (51,234 records, build77 era)
----------------------------------------------------------------------------------
(A) MYTHIC FORMULAS CANNOT DROP ON NORMAL. The 42 uber ("supra") craftables are built
    by 59 formula records; 42 of those sit on `arcaneformulae\supra.dbr`. The base game
    wires that pool into the EPIC and LEGENDARY act tables only:
        02_act{1..4}_arcaneformulae = LootMasterTable [ ..._table (98), supra (2) ]
        03_act{1..4}_arcaneformulae = LootMasterTable [ ..._table (95), supra (5) ]
        01_act{1..4}_arcaneformulae = LootItemTable_FixedWeight, 25 base formulas, NO supra
    So a Normal-tier mod chest reached 0 of 42 uber formulas. Will exempts FORMULAS from
    the tier rule (they are `itemClassification = Common` ItemArtifactFormula records, so
    no legendary GEAR moves at all) while legendary ITEMS stay out of Normal.

(B) 36 OF THE 78 UBER REAGENTS ARE UNREACHABLE FROM A LEGENDARY CHEST. Measured split:
       19 MI / "green" (itemClassification = Rare, the `mi_l_*` monster-infrequent items)
          -> EXEMPT BY WILL'S OWN WORDS, but each one must be PROVEN monster-farmable.
        8 ordinary base uniques that live only on act-2/act-3 banded tables the chest
          pools never name (3 torso, 3 amulet, 2 ring).
        6 IT "divine artifacts" (ItemArtifact) - craftable from base arcane formulae the
          chests DO drop, but not droppable themselves; 0 of 292 artifacts were reachable
          from any mod chest at any difficulty.
        3 records that DO NOT EXIST in this TQIT-era database at all:
          `records\xpack2\item\equipmentweapons\1hranged\{u_l_08,u_e_06,mi_l_machae}.dbr`
          are RAGNAROK (xpack2) records. All four thrown craftables (Charon's Toll, Hati,
          The Last Word, Sanguine Orbit) name exactly those three, so those four formulas
          are DEAD: they can never be completed by anybody.

(C) THE THROWN CLASS IS UNPAYABLE. 14 `WeaponHunting_RangedOneHand` records exist
    (5 Legendary, 3 Epic - all base craft results -, 3 Rare, 3 Common) and there is no
    "unique one-hand-ranged" loot table in this era's database for a master to name, so
    0 of 5 legendary thrown were reachable from anything.

THE FIX (this module is the ONE implementation; nothing may re-derive it)
-------------------------------------------------------------------------
1. MYTHIC FORMULAS ON NORMAL. `supra.dbr` is added as ONE new member of each
   `01_act{1..4}_arcaneformulae` table, at a weight computed to land on
   NORMAL_SUPRA_SHARE of that table's own total - so it is RARER on Normal (1%) than the
   base game already makes it on Epic (2%) and Legendary (5%). Base-game precedent for a
   `LootItemTable_FixedWeight` naming a loot TABLE in a `lootNameN` slot: 56 shipped
   records do it (e.g. `raremisc\01_rareunique_all.dbr` names `weapons\unique\sword_n01`).
   Nothing is removed and no weight is lowered.

2. REAGENT COMPLETABILITY. The 8 ordinary + 6 artifact reagents are placed into
   mod-owned `svc_craft_reagents_*_l01` tables that are added as MEMBERS of the
   LEGENDARY-tier hosts the chest pools already reach (`unique_torso_l01`, `amulet_l01`,
   `finger_l01`, `04_l_misc`). LEGENDARY-ONLY BY CONSTRUCTION: every one of the 14 is
   `itemClassification = Legendary`, so it may only ever enter an `_l01` / `_l`-tier host
   (R-100 #17). The 4 dead thrown formulas are repointed off the three Ragnarok ghosts
   onto thrown records that EXIST in this era (the DRX vit wands), which is the only
   possible fix - a record that is not in the database cannot be put into a pool.

3. THROWN. `records\item\loottables\svc\svc_unique_thrown_{n,e,l}01.dbr`, a
   `LootItemTable_FixedWeight` per tier (FixedWeight, not DynWeight, ON PURPOSE: every
   legendary thrown record is itemLevel 65, which sits OUTSIDE the 46-56 band the
   `_e01` DynWeight class tables use, so a level-banded table could never pay one on the
   Epic tier). Membership carries the tier law:
       n -> the two itemLevel-30 wands (Rare + Common). ZERO Legendary.
       e -> the 5 Legendary thrown.
       l -> the 5 Legendary thrown.
   The table is wired into `svc_loot_breadth._master_members` as the SEVENTH class of the
   `svc_unique_weapons_{tier}01` masters, so thrown becomes payable everywhere those
   masters are named (every mod chest's weapon row AND its guaranteed slot).

NON-REDUCTION LAW (R-180, Will 2026-08-08): no member is removed, no chance or weight is
lowered, no numSpawn equation is touched. Every edit here is additive or a strict raise.

TIER LAW (R-100 #17): asserted, not assumed - `audit_db` re-proves that the Normal branch
reaches ZERO legendary GEAR after this module runs, and the thrown Normal table is the
only new Normal-side membership it creates.

Standalone gate twin: `py tools/gate_craft_thrown_breadth.py <arz>`.
Negative tests:       `py tools/debug/negtest_craft_thrown.py <arz>`.
"""
import sys
from collections import defaultdict
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import svc_loot_breadth as SLB
from svc_loot_breadth import _n, _sc, Lookup, Expander       # ONE resolver, one expander

TIERS = SLB.TIERS

# ─────────────────────────────────────────────────────────────────────────────
# (1) MYTHIC FORMULAS ON EVERY DIFFICULTY
# ─────────────────────────────────────────────────────────────────────────────
SUPRA_POOL = r'records\xpack\item\loottables\arcaneformulae\supra.dbr'
SUPRA_SPECIAL = r'records\xpack\item\loottables\arcaneformulae\supra_special.dbr'
NORMAL_FORMULA_TABLES = tuple(
    r'records\xpack\item\loottables\arcaneformulae\01_act%d_arcaneformulae.dbr' % i
    for i in (1, 2, 3, 4))
# Measured, not chosen: the base game itself gives `supra` 2% of the Epic act tables and
# 5% of the Legendary ones. Normal sits one rung BELOW the rarest of those, which is what
# "they can drop in normal as well" plus "rarer than Epic/Legendary is fine" resolves to.
NORMAL_SUPRA_SHARE = 0.01

# ─────────────────────────────────────────────────────────────────────────────
# (3) THE THROWN CLASS
# ─────────────────────────────────────────────────────────────────────────────
THROWN_CLASS = 'WeaponHunting_RangedOneHand'
THROWN_TABLE = {t: r'records\item\loottables\svc\svc_unique_thrown_%s01.dbr' % t
                for t in TIERS}
# A clean, small `LootItemTable_FixedWeight` to clone the shape from (Class + template).
_THROWN_DONOR = SUPRA_POOL
_THROWN_CLEAR_SLOTS = 48        # supra has 42 members; clear well past it after cloning

_WAND = r'records\drxitem\equipmentweapon\wands\%s.dbr'
_SUPRA = r'records\drxitem\supra\%s.dbr'
# (path, weight) per tier. WEIGHTS: the DRX wand is an ordinary legendary drop and stays
# the common outcome; the four craft-tier supras are prizes and each take 1/10th of its
# weight, so a specific supra thrown is ~7% of a thrown roll (and ~0.26% of a weapon roll
# once the class weight below is applied).
THROWN_MEMBERS = {
    # Normal: itemLevel-30 wands only. ZERO Legendary -> R-100 #17 holds by construction.
    'n': ((_WAND % 'mi_vit_wand_01', 100), (_WAND % 'm_vit_wand_01', 50)),
    'e': ((_WAND % 'u_vit_wand', 100),
          (_SUPRA % 'svc_wep_charonstoll', 10), (_SUPRA % 'svc_wep_hati', 10),
          (_SUPRA % 'svc_wep_lastword', 10), (_SUPRA % 'svc_wep_sanguineorbit', 10)),
    'l': ((_WAND % 'u_vit_wand', 100),
          (_SUPRA % 'svc_wep_charonstoll', 10), (_SUPRA % 'svc_wep_hati', 10),
          (_SUPRA % 'svc_wep_lastword', 10), (_SUPRA % 'svc_wep_sanguineorbit', 10)),
}
# Weight of the thrown member inside `svc_unique_weapons_{tier}01`. DERIVED, not chosen:
# every other class member carries 1000 for a 17-24 record class; thrown is the smallest
# unique class in the database (5 legendary records), so it takes the proportional share
# 5/20 = 0.25 of a full class weight. At 250 against the master's existing 6700 it is
# 3.6% of a weapon roll - the class becomes reachable without re-weighting the other six.
THROWN_MASTER_WEIGHT = 250

# ─────────────────────────────────────────────────────────────────────────────
# (2) REAGENT COMPLETABILITY
# ─────────────────────────────────────────────────────────────────────────────
# The three Ragnarok (xpack2) ghosts the four thrown formulas name. NOT in this database.
GHOST_REAGENTS = (
    r'records\xpack2\item\equipmentweapons\1hranged\u_l_08.dbr',
    r'records\xpack2\item\equipmentweapons\1hranged\u_e_06.dbr',
    r'records\xpack2\item\equipmentweapons\1hranged\mi_l_machae.dbr',
)
# The repoint. Each thrown craftable gets a DISTINCT reagent set drawn from the thrown
# records this era actually has, so the four recipes are no longer literally identical
# (they were: all four named the same three ghosts).
THROWN_FORMULA_REAGENTS = {
    r'records\drxitem\supra\zrecipes\svc_thrown_charonstoll_formula.dbr':
        (_WAND % 'u_vit_wand', _WAND % 'mi_vit_wand_01', _WAND % 'mi_vit_wand_02'),
    r'records\drxitem\supra\zrecipes\svc_thrown_hati_formula.dbr':
        (_WAND % 'u_vit_wand', _WAND % 'mi_vit_wand_02', _WAND % 'mi_vit_wand_03'),
    r'records\drxitem\supra\zrecipes\svc_thrown_lastword_formula.dbr':
        (_WAND % 'u_vit_wand', _WAND % 'mi_vit_wand_01', _WAND % 'mi_vit_wand_03'),
    r'records\drxitem\supra\zrecipes\svc_thrown_sanguineorbit_formula.dbr':
        (_WAND % 'mi_vit_wand_01', _WAND % 'mi_vit_wand_02', _WAND % 'mi_vit_wand_03'),
}

# The mod-owned reagent tables, one per FAMILY, LEGENDARY TIER ONLY (every reagent placed
# here is itemClassification = Legendary, so it may never enter a Normal or Epic host).
REAGENT_TABLE = {
    'torso': r'records\item\loottables\svc\svc_craft_reagents_torso_l01.dbr',
    'amulet': r'records\item\loottables\svc\svc_craft_reagents_amulet_l01.dbr',
    'ring': r'records\item\loottables\svc\svc_craft_reagents_ring_l01.dbr',
    'artifact': r'records\item\loottables\svc\svc_craft_reagents_artifact_l01.dbr',
}
# The LEGENDARY-tier host each family hangs off. Every one is a LootMasterTable that the
# legendary chest pools ALREADY reach (measured: 136 loot tables in the legendary pool
# tree), so no chest row is touched - which is what keeps this lane off the chest/hoard
# surface entirely.
REAGENT_HOST = {
    'torso': r'records\xpack\item\loottables\torso\mastertables\unique_torso_l01.dbr',
    'amulet': r'records\xpack\item\loottables\amulet\unique\amulet_l01.dbr',
    'ring': r'records\xpack\item\loottables\finger\unique\finger_l01.dbr',
    'artifact': r'records\item\loottables\raremisc\mastertables\04_l_misc.dbr',
}
# Host weights. Each is ~5% of its host's own measured total (torso 100, amulet 1000,
# finger 1000, 04_l_misc 1357), so a reagent is a rare tail on an existing branch rather
# than a re-weighting of it. Nothing existing is lowered.
REAGENT_HOST_WEIGHT = {'torso': 5, 'amulet': 50, 'ring': 50, 'artifact': 60}

# The 14 reagents that no chest could pay, by family. COMMITTED (not derived at apply
# time) so the placement is deterministic and reviewable; `audit_db` then re-proves
# completability over the FINAL database, so a future content change that strands a
# different reagent fails loud instead of silently shipping.
REAGENT_PLACEMENTS = {
    'torso': (
        r'records\item\equipmentarmor\um_l_mantleofamunra.dbr',
        r'records\item\equipmentarmor\um_e_raimentoflogos.dbr',
        r'records\item\equipmentarmor\u_l_wyrmskinharness.dbr',
    ),
    'amulet': (
        r'records\item\equipmentamulet\u_e_blessingofthegods.dbr',
        r'records\sandbox\chris\chrisamulet01.dbr',
        r'records\sandbox\chris\chrisrelic2.dbr',
    ),
    'ring': (
        r"records\item\equipmentring\u_e_thoth'smark.dbr",
        r'records\item\equipmentring\u_l_blackpearlring.dbr',
    ),
    'artifact': (
        r'records\xpack\item\artifacts\l_da_thothsglory.dbr',
        r'records\xpack\item\artifacts\l_da_ikonofzeus.dbr',
        r'records\xpack\item\artifacts\l_da_mardukstabletofdestiny.dbr',
        r'records\xpack\item\artifacts\l_da_goldeneyeofsunwukong.dbr',
        r'records\xpack\item\artifacts\e_da_crescentmoonofartemis.dbr',
        r'records\xpack\item\artifacts\e_da_demetersbounty.dbr',
    ),
}
REAGENT_ITEM_WEIGHT = 100

# MI / "green" reagents: Will's own exemption ("except for the monster unique droppable
# items like the green items"). The RULE is `itemClassification == 'Rare'`; this list is
# the committed roster that rule produced on the live arz, and `audit_db` fails loud if
# the derived set ever diverges from it, so neither can rot silently.
MI_CLASSIFICATION = 'Rare'
MI_REAGENTS = (
    'mi_l_arachnos', 'mi_l_bandari', 'mi_l_dragonian', 'mi_l_empousa', 'mi_l_gigantes2',
    'mi_l_ichthianmelee', 'mi_l_lamiamelee', 'mi_l_liche', 'mi_l_minotaur',
    'mi_l_neanderthalmage', 'mi_l_satyrbrigand', 'mi_l_satyrmage', 'mi_l_tigermanchampion',
    'mi_l_tigermanmage', 'mi_l_tigermanmelee', 'mi_l_troglodytemelee',
    'mi_l_tropicalarachnos', 'mi_l_wraith',
)


# ─────────────────────────────────────────────────────────────────────────────
# shared derivations (the craft chain, read straight off the records)
# ─────────────────────────────────────────────────────────────────────────────
def _is_supra_result(path):
    p = _n(path)
    return '\\supra\\' in p and p.endswith('.dbr') and '\\recipes\\' not in p \
        and '\\zrecipes\\' not in p


def uber_formulas(db, lk):
    """{formula record: result record} for every formula that builds a supra craftable."""
    out = {}
    for name in db.record_names():
        cls = str(_sc(db.get_field_value(name, 'Class')) or '')
        if 'formula' not in cls.lower():
            continue
        art = _sc(db.get_field_value(name, 'artifactName'))
        if isinstance(art, str) and _is_supra_result(art):
            out[name] = art
    return out


def reagents_of(db, formula):
    """The reagent paths a formula names, in slot order."""
    out = []
    ff = db.get_fields(formula) or {}
    for k in sorted(ff, key=lambda z: z.split('###')[0]):
        b = k.split('###')[0]
        if b.startswith('reagent') and b.endswith('BaseName'):
            for v in ff[k].values:
                if isinstance(v, str) and v:
                    out.append(v)
    return out


def reagent_universe(db, lk, forms=None):
    """{reagent path (lowercased): set(craftable)} over every uber formula."""
    forms = forms if forms is not None else uber_formulas(db, lk)
    users = defaultdict(set)
    for f, result in forms.items():
        for r in reagents_of(db, f):
            users[_n(r)].add(_n(result))
    return users


def classify_reagent(db, lk, path):
    """'missing' | 'mi' | 'artifact' | 'ordinary'."""
    real = lk.real(path)
    if not real:
        return 'missing'
    ic = str(_sc(db.get_field_value(real, 'itemClassification')) or '')
    cls = str(_sc(db.get_field_value(real, 'Class')) or '')
    if ic == MI_CLASSIFICATION:
        return 'mi'
    if cls.startswith('ItemArtifact'):
        return 'artifact'
    return 'ordinary'


def chest_pool(db, lk, ex, tier):
    """The set of leaf items every mod chest of `tier` can pay (lowercased)."""
    out = set()
    exempt = {_n(k) for k in SLB.EXEMPT}
    for table in SLB.chest_tables(db, lk):
        if _n(table) in exempt:
            continue
        if SLB.infer_tier(db, table, lk) == tier:
            out |= {_n(x) for x in ex.leaves(table)}
    return out


def monster_sources(db, lk, reagent):
    """Loot tables under a \\monster\\ folder that name `reagent` (the MI evidence)."""
    target = _n(reagent)
    out = set()
    for rec in db.record_names():
        rl = _n(rec)
        if '\\loottables\\' not in rl or '\\monster\\' not in rl:
            continue
        for k, tf in (db.get_fields(rec) or {}).items():
            b = k.split('###')[0].lower()
            if 'weight' in b or 'chance' in b or 'equation' in b:
                continue
            for v in tf.values:
                if isinstance(v, str) and _n(v) == target:
                    out.add(rec)
    return sorted(out)


# ─────────────────────────────────────────────────────────────────────────────
# WRITE SIDE
# ─────────────────────────────────────────────────────────────────────────────
def _members(db, real):
    """[(index, name, weight)] for the occupied lootNameN members of a table."""
    out = []
    for k in (db.get_fields(real) or {}):
        b = k.split('###')[0]
        if not b.startswith('lootName'):
            continue
        try:
            i = int(b[len('lootName'):])
        except ValueError:
            continue
        v = _sc(db.get_field_value(real, b))
        if v:
            w = _sc(db.get_field_value(real, 'lootWeight%d' % i)) or 0
            out.append((i, str(v), int(w)))
    return sorted(out)


def _first_free(db, real, limit=64):
    used = {i for i, _nm, _w in _members(db, real)}
    for i in range(1, limit):
        if i not in used:
            return i
    return None


def add_member(db, real, path, weight, lk=None):
    """Add ONE member to a loot table, idempotently. Never touches an existing member,
    never lowers a weight. Returns a change string or None."""
    lk = lk or Lookup(db)
    target = lk.real(path) or path
    for _i, nm, _w in _members(db, real):
        if _n(nm) == _n(target):
            return None                      # already a member: leave it exactly as-is
    idx = _first_free(db, real)
    if idx is None:
        raise SystemExit("svc_craft_thrown: %s has no free lootName slot for %s"
                         % (real, target))
    SLB._set_str(db, real, 'lootName%d' % idx, target)
    db.set_field(real, 'lootWeight%d' % idx, int(weight))
    return 'lootName%d=%s (w=%d)' % (idx, _n(target).rsplit('\\', 1)[-1], weight)


def wire_mythic_formulas_into_normal(db, lk=None, verbose=True):
    """(1) `supra` becomes a member of every Normal-tier act formula table."""
    lk = lk or Lookup(db)
    supra = lk.real(SUPRA_POOL)
    if not supra:
        print("  CRAFT/THROWN: WARNING supra pool missing (%s); Normal formulas not "
              "wired" % SUPRA_POOL)
        return []
    changes = []
    for table in NORMAL_FORMULA_TABLES:
        real = lk.real(table)
        if not real:
            print("  CRAFT/THROWN: WARNING Normal formula table missing: %s" % table)
            continue
        existing = _members(db, real)
        if any(_n(nm) == _n(supra) for _i, nm, _w in existing):
            continue                          # idempotent
        total = sum(w for _i, _nm, w in existing)
        # weight w such that w / (total + w) == NORMAL_SUPRA_SHARE
        weight = max(1, int(round(total * NORMAL_SUPRA_SHARE / (1.0 - NORMAL_SUPRA_SHARE))))
        c = add_member(db, real, supra, weight, lk)
        if c:
            changes.append('%s: %s [%.2f%% of %d]'
                           % (_n(real).rsplit('\\', 1)[-1], c,
                              100.0 * weight / float(total + weight), total + weight))
    if verbose:
        for c in changes:
            print("  CRAFT/THROWN: mythic formulas on Normal - %s" % c)
    return changes


def ensure_thrown_tables(db, lk=None, verbose=True):
    """(3) Author `svc_unique_thrown_{n,e,l}01`. Idempotent: a table that already carries
    exactly the right members is not rewritten."""
    lk = lk or Lookup(db)
    donor = lk.real(_THROWN_DONOR)
    if not donor:
        print("  CRAFT/THROWN: WARNING thrown donor missing (%s); thrown tables not "
              "authored" % _THROWN_DONOR)
        return {}
    built = {}
    for tier in TIERS:
        path = THROWN_TABLE[tier]
        members = [(lk.real(p), w) for (p, w) in THROWN_MEMBERS[tier] if lk.real(p)]
        if not members:
            print("  CRAFT/THROWN: WARNING no thrown records resolve for tier %r; table "
                  "skipped" % tier)
            continue
        want = [(_n(p), w) for p, w in members]
        real = lk.real(path)
        if real:
            have = [(_n(nm), w) for _i, nm, w in _members(db, real)]
            if have == want:
                built[tier] = real
                continue
            path = real
        else:
            db.clone_record(donor, path)
        db.set_field(path, 'FileDescription',
                     'SVC thrown class: every unique one-hand-ranged weapon, %s tier'
                     % tier)
        for i, (p, w) in enumerate(members, start=1):
            SLB._set_str(db, path, 'lootName%d' % i, p)
            db.set_field(path, 'lootWeight%d' % i, int(w))
        for i in range(len(members) + 1, _THROWN_CLEAR_SLOTS):
            if _sc(db.get_field_value(path, 'lootName%d' % i)):
                db.set_field(path, 'lootName%d' % i, '')
            if _sc(db.get_field_value(path, 'lootWeight%d' % i)) not in (None, 0):
                db.set_field(path, 'lootWeight%d' % i, 0)
        built[tier] = path
        if verbose:
            print("  CRAFT/THROWN: %s = %d thrown record(s)"
                  % (_n(path).rsplit('\\', 1)[-1], len(members)))
    lk.refresh()
    return built


def ensure_reagent_tables(db, lk=None, verbose=True):
    """(2a) Author the per-family reagent tables and hang each off its LEGENDARY host."""
    lk = lk or Lookup(db)
    donor = lk.real(_THROWN_DONOR)
    if not donor:
        print("  CRAFT/THROWN: WARNING reagent donor missing; reagent tables not authored")
        return {}
    built = {}
    for family, path in sorted(REAGENT_TABLE.items()):
        items = [lk.real(p) for p in REAGENT_PLACEMENTS[family]]
        missing = [p for p, r in zip(REAGENT_PLACEMENTS[family], items) if not r]
        if missing:
            # Fail loud: a committed reagent that no longer resolves is a real defect,
            # never something to place silently or skip.
            raise SystemExit("svc_craft_thrown: committed reagent(s) do not resolve in "
                             "the db: %s" % ', '.join(missing))
        want = [(_n(p), REAGENT_ITEM_WEIGHT) for p in items]
        real = lk.real(path)
        if real:
            have = [(_n(nm), w) for _i, nm, w in _members(db, real)]
            if have != want:
                path = real
            else:
                built[family] = real
                continue
        else:
            db.clone_record(donor, path)
        db.set_field(path, 'FileDescription',
                     'SVC uber-craft reagents (%s), legendary tier' % family)
        for i, p in enumerate(items, start=1):
            SLB._set_str(db, path, 'lootName%d' % i, p)
            db.set_field(path, 'lootWeight%d' % i, int(REAGENT_ITEM_WEIGHT))
        for i in range(len(items) + 1, _THROWN_CLEAR_SLOTS):
            if _sc(db.get_field_value(path, 'lootName%d' % i)):
                db.set_field(path, 'lootName%d' % i, '')
            if _sc(db.get_field_value(path, 'lootWeight%d' % i)) not in (None, 0):
                db.set_field(path, 'lootWeight%d' % i, 0)
        built[family] = path
        if verbose:
            print("  CRAFT/THROWN: %s = %d reagent(s)"
                  % (_n(path).rsplit('\\', 1)[-1], len(items)))
    lk.refresh()
    return built


def wire_reagent_hosts(db, lk=None, verbose=True):
    """(2b) Add each reagent table to its legendary host master (additive, idempotent)."""
    lk = lk or Lookup(db)
    changes = []
    for family, host in sorted(REAGENT_HOST.items()):
        host_real = lk.real(host)
        table = lk.real(REAGENT_TABLE[family])
        if not host_real or not table:
            print("  CRAFT/THROWN: WARNING reagent host or table missing for %r" % family)
            continue
        c = add_member(db, host_real, table, REAGENT_HOST_WEIGHT[family], lk)
        if c:
            changes.append('%s <- %s' % (_n(host_real).rsplit('\\', 1)[-1], c))
    if verbose:
        for c in changes:
            print("  CRAFT/THROWN: reagent host - %s" % c)
    return changes


def repoint_thrown_formula_reagents(db, lk=None, verbose=True):
    """(2c) Move the 4 thrown formulas off the three Ragnarok ghost records."""
    lk = lk or Lookup(db)
    changes = []
    for formula, reagents in sorted(THROWN_FORMULA_REAGENTS.items()):
        real = lk.real(formula)
        if not real:
            print("  CRAFT/THROWN: WARNING thrown formula missing: %s" % formula)
            continue
        resolved = [lk.real(p) for p in reagents]
        if any(r is None for r in resolved):
            raise SystemExit("svc_craft_thrown: thrown-formula replacement reagent(s) do "
                             "not resolve: %s" % formula)
        touched = []
        for i, target in enumerate(resolved, start=1):
            field = 'reagent%dBaseName' % i
            cur = _sc(db.get_field_value(real, field))
            if cur is not None and _n(cur) == _n(target):
                continue
            SLB._set_str(db, real, field, target)
            touched.append('%s=%s' % (field, _n(target).rsplit('\\', 1)[-1]))
        if touched:
            changes.append('%s: %s' % (_n(real).rsplit('\\', 1)[-1], ', '.join(touched)))
    if verbose:
        for c in changes:
            print("  CRAFT/THROWN: thrown formula repoint - %s" % c)
    return changes


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT SIDE (shared by the standalone gate, the in-build verify and the negtests)
# ─────────────────────────────────────────────────────────────────────────────
def thrown_problems(db, table, tier, ex, lk=None):
    """(d) THE THROWN-CLASS RULE, folded into the class-breadth gate family.

    Every mod chest must be able to pay the one-hand-ranged class at its own tier:
      C1 tiers e/l - at least one thrown record of the tier's TARGET classification
         (Legendary), i.e. the class is genuinely payable at end game;
      C2 tier n    - at least one thrown record of ANY classification (measured: this
         TQIT-era db has no droppable Epic-classification thrown record at all - the only
         three are base-game craft RESULTS - so Normal's thrown presence is carried by the
         itemLevel-30 Rare/Common wand band), and ZERO Legendary thrown (the tier law).
    """
    lk = lk or (ex.lk if hasattr(ex, 'lk') else Lookup(db))
    base = _n(table).rsplit('\\', 1)[-1]
    problems = []
    reachable = []
    for it in ex.leaves(table):
        if str(_sc(db.get_field_value(it, 'Class')) or '') == THROWN_CLASS:
            reachable.append(it)
    if tier == 'n':
        if not reachable:
            problems.append(
                "C2 %s [n tier] reaches NO %s item; the thrown class is unpayable on "
                "Normal" % (base, THROWN_CLASS))
        leaked = [x for x in reachable
                  if str(_sc(db.get_field_value(x, 'itemClassification')) or '')
                  == 'Legendary']
        if leaked:
            problems.append(
                "C2 %s [n tier] reaches %d LEGENDARY thrown item(s) (tier law: no "
                "legendary gear on Normal); e.g. %s"
                % (base, len(leaked), sorted(leaked)[0]))
    else:
        want = SLB.TARGET_IC[tier]
        good = [x for x in reachable
                if str(_sc(db.get_field_value(x, 'itemClassification')) or '') == want]
        if not good:
            problems.append(
                "C1 %s [%s tier] reaches no %s %s item (the thrown class is unpayable at "
                "its own tier)" % (base, tier, want, THROWN_CLASS))
    return problems


def audit_formula_reachability(db, lk, ex):
    """(a) Every uber craftable must have at least one chest-droppable formula on EVERY
    difficulty tier - Normal included (Will: "they can drop in normal as well")."""
    problems = []
    forms = uber_formulas(db, lk)
    craftables = {_n(v) for v in forms.values()}
    stats = {}
    for tier in TIERS:
        pool = chest_pool(db, lk, ex, tier)
        covered = {_n(result) for f, result in forms.items() if _n(f) in pool}
        stats[tier] = (len(covered), len(craftables),
                       len([f for f in forms if _n(f) in pool]), len(forms))
        missing = sorted(craftables - covered)
        if missing:
            problems.append(
                "F1 [%s tier] %d of %d uber craftables have NO chest-droppable formula "
                "(e.g. %s)" % (tier, len(missing), len(craftables), missing[0]))
    return problems, stats


def audit_reagent_completability(db, lk, ex):
    """(c) Every NON-MI reagent of every uber craftable must be reachable from the
    LEGENDARY-tier chest pools, and every MI exemption must be proven monster-farmable."""
    problems = []
    forms = uber_formulas(db, lk)
    users = reagent_universe(db, lk, forms)
    pool_l = chest_pool(db, lk, ex, 'l')
    buckets = defaultdict(list)
    for reagent in sorted(users):
        buckets[classify_reagent(db, lk, reagent)].append(reagent)

    if buckets['missing']:
        problems.append(
            "G0 %d reagent(s) name a record that does not exist in this database: %s"
            % (len(buckets['missing']),
               ', '.join(_n(x).rsplit('\\', 1)[-1] for x in buckets['missing'])))

    unreachable = [r for r in buckets['ordinary'] + buckets['artifact']
                   if r not in pool_l]
    if unreachable:
        problems.append(
            "G1 %d non-MI reagent(s) are unreachable from every Legendary-tier chest "
            "pool (Will: farm legendary long enough -> find all the reagents): %s"
            % (len(unreachable),
               ', '.join(_n(x).rsplit('\\', 1)[-1] for x in sorted(unreachable))))

    derived_mi = {_n(x).rsplit('\\', 1)[-1][:-4] for x in buckets['mi']}
    committed = set(MI_REAGENTS)
    if derived_mi != committed:
        problems.append(
            "G2 the MI exemption roster drifted: derived-not-committed=%s "
            "committed-not-derived=%s (the list in svc_craft_thrown.MI_REAGENTS must be "
            "updated in the same commit as whatever moved)"
            % (sorted(derived_mi - committed) or 'none',
               sorted(committed - derived_mi) or 'none'))

    stats = {'total': len(users), 'mi': len(buckets['mi']),
             'ordinary': len(buckets['ordinary']), 'artifact': len(buckets['artifact']),
             'missing': len(buckets['missing']),
             'reachable_l': len([r for r in users if r in pool_l]),
             'buckets': {k: sorted(v) for k, v in buckets.items()}}
    return problems, stats


def audit_db(db, verbose=False, lk=None):
    """The whole craft+thrown contract over one (final) database."""
    lk = lk or Lookup(db)
    ex = Expander(db, lk)
    problems = []
    fprob, fstats = audit_formula_reachability(db, lk, ex)
    problems.extend(fprob)
    rprob, rstats = audit_reagent_completability(db, lk, ex)
    problems.extend(rprob)

    # thrown presence, per mod chest table (the class-breadth family)
    exempt = {_n(k) for k in SLB.EXEMPT}
    tprob = []
    audited = 0
    for table in SLB.chest_tables(db, lk):
        if _n(table) in exempt:
            continue
        tier = SLB.infer_tier(db, table, lk)
        if tier is None:
            continue
        audited += 1
        tprob.extend(thrown_problems(db, table, tier, ex, lk))
    if not audited:
        problems.append("C0 no mod chest table was audited for the thrown class at all "
                        "(scope rule broken - it must never be empty)")
    problems.extend(tprob)

    if verbose:
        for tier in TIERS:
            c, tot, fr, ftot = fstats[tier]
            print("    formulas [%s] %d/%d craftables covered, %d/%d formula records "
                  "reachable" % (tier, c, tot, fr, ftot))
        print("    reagents: %d total = %d MI + %d ordinary + %d artifact + %d missing; "
              "%d reachable from Legendary chests"
              % (rstats['total'], rstats['mi'], rstats['ordinary'], rstats['artifact'],
                 rstats['missing'], rstats['reachable_l']))
        print("    thrown: %d mod chest table(s) audited" % audited)
    return problems, {'formulas': fstats, 'reagents': rstats, 'chests': audited}
