r"""svc_armor_breadth.py - THE ARMOUR-PARITY CONTRACT (Will 2026-08-10, R-181).

WILL, VERBATIM (2026-08-10)
---------------------------
"also what about the armor? i am not really seeing armor drops like shields, chest
plates, helmets, etc."

WHY R-180 DID NOT ALREADY FIX THIS
-----------------------------------
R-180 asked a REACHABILITY question ("can this chest pay a legendary spear at all")
and answered it. Armour was never structurally unreachable: MEASURED on the shipped
build76 arz `16994072`, all 51 mod chest tables reach all five worn slots and ZERO have
an empty slot. The defect is the RATE. Per open of the Gaoler cage's chest_01 the
shipped build pays

    11.56 legendary WEAPONS   vs   0.17 helms + 0.26 arms + 0.68 torso + 0.29 legs
                                    + 1.25 shields  =  2.65 armour pieces

a weapon:armour mass ratio of 4.36 : 1, and a helm at 1.2% of the chest's legendary
mass. Over a six-chest cage run that is 58.5 weapons against 12.4 armour pieces. Will
is not misperceiving a wide pool; he is correctly reading a starving one.

THE THREE CAUSES, ALL MEASURED, ALL FIXED HERE
-----------------------------------------------
1. THE GUARANTEED SLOT IS A WEAPON SLOT. `loot3Chance = 100` fires every spawn
   iteration (S = 12.48 on chest_01) and every member of it is a weapon or relic table.
   Armour only ever arrives through the CHANCE rows. Untouched by this module: the
   guaranteed slot's weapon:relic split is R-180 law and Will farms it.
2. THE ARMOUR ROWS FIRE COLDER THAN THE WEAPON ROW. R-180 lifted the weapon row to 40%
   and the shield row to 30% and left the torso/head row at 33% and the arms/legs row at
   31%. This module lifts every armour row to the SAME 40% the weapon row already has.
3. INSIDE AN ARMOUR ROW, LEGENDARY ARMOUR IS A ROUNDING ERROR. The DRX donor rows are
   ~90% STATIC (common/magical/rare randomiser) by weight: the torso/head row gives
   `unique_torso_l01` + `unique_head_l01` a combined 200 of 1888 (10.6%), the arms/legs
   row 400 of 2088 (19.2%), the shield row 100 of 931 (10.7%). This module raises each
   unique-armour member to ARMOR_UNIQUE_WEIGHT so the legendary half of an armour row is
   comparable to the weapon row's, and drops one aggregate ARMOUR MASTER into a free
   member slot so a single member pays all five worn slots evenly.

THE ARMOUR MASTER (the R-180 machinery, reused verbatim)
---------------------------------------------------------
`records\item\loottables\svc\svc_unique_armor_{n,e,l}01.dbr`, a clone of the same base
`all_l01` LootMasterTable shape R-180's weapon master uses, naming the five per-slot
unique tables at EQUAL weight:
    unique_head_{t}01 . unique_arms_{t}01 . unique_torso_{t}01 . unique_legs_{t}01
    . shield_{t}01
Its name carries `unique` + the `_{tier}01` suffix ON PURPOSE, exactly as R-180's weapon
master does, so `gate_relic_difficulty_tiers` reads its difficulty straight off the name
and a wrong-tier wiring reds without a new rule.

THE SHIELD-CLASS TRAP, RECORDED SO IT IS NEVER RE-LEARNED
----------------------------------------------------------
A shield's engine `Class` is `WeaponArmor_Shield`, NOT `ArmorProtective_*`. Any audit
written as `Class.startswith('Armor')` reports ZERO shields; any weapon audit written as
`startswith('Weapon')` counts every shield as a weapon. Both errors erase shields from
the armour side - the exact slot Will named first. The one authority on the mapping is
`svc_loot_distribution.GEAR_SLOTS`; nothing here re-derives it.

NON-REDUCTION (R-100 #17 / Will 2026-08-08 / R-180), re-proven per edit
------------------------------------------------------------------------
numSpawn equations are never touched, no member is ever removed, no group chance is ever
lowered (`_raise_chance` takes max(existing, target) and refuses to wake a dormant row),
no member weight is ever lowered, and the guaranteed slot stays at 100%. Expected drops
per open therefore strictly RISE. What changes inside an armour row is its COMPOSITION:
the legendary share goes up and the static/junk share goes down as a fraction - which is
the ask, since "i am not really seeing armor drops" is a report about legendaries on a
Legendary farm, not about total item count.

SCOPE BOUNDARY, STATED SO NOBODY WIDENS IT BY ACCIDENT
-------------------------------------------------------
* IN: every mod-owned gear chest loot table (the `\svc\` / `svc_` rule R-180 set) plus
  the 3 DRX donors, i.e. the vault cage, all 8 boss hoards, the 3 guard-pair hoards and
  the hidden-blood-cave mega chest.
* OUT, BY OWNER: the `svc_uberorb_*` orb tables belong to the concurrent
  `fix/orb-loot-breadth` lane (b79), which owns armour slots for orb tables. They are
  listed loudly on every run and registered as debt, never silently skipped.
* OUT, BY EVIDENCE: general MONSTER armour drops. Measured and reported, NOT changed -
  see the R-181 report; that is a Will decision, not a silent scope widening.
"""
import re
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import svc_loot_breadth as SLB
import svc_loot_distribution as SLD

TIERS = SLB.TIERS

# ── The per-slot unique-armour donors (every one byte-verified in the live arz) ──
_XP_ARMOR_MASTER = (r'records\xpack\item\loottables\%s\mastertables'
                    r'\unique_%s_%s01.dbr')                    # slot, slot, tier
_XP_SHIELD = r'records\xpack\item\loottables\shields\unique\shield_%s01.dbr'

# The mod-owned aggregate armour master this module authors, one per difficulty tier.
ARMOR_MASTER = {t: r'records\item\loottables\svc\svc_unique_armor_%s01.dbr' % t
                for t in TIERS}
_MASTER_DONOR = r'records\item\loottables\weapons\mastertables\unique\all_l01.dbr'

# One member per WORN SLOT, all at the same weight: the master is the even-spread
# instrument, so any per-slot bias must be expressed by a THEME, never smuggled in here.
_SLOT_WEIGHT = 1000


def armor_master_members(tier):
    out = []
    for slot in ('head', 'arms', 'torso', 'legs'):
        out.append((_XP_ARMOR_MASTER % (slot, slot, tier), _SLOT_WEIGHT))
    out.append((_XP_SHIELD % tier, _SLOT_WEIGHT))
    return out


# ── The committed rates (every one has a stated derivation) ──────────────────
# R-180 lifted the weapon row to 40 and the shield row to 30 and left the two body-armour
# rows where the DRX donor had them (33 and 31). Parity means one number: the weapon
# row's. This is the "40/30 band" of the brief, resolved to its top.
ARMOR_ROW_CHANCE = 40.0
# Weight for a unique-armour member inside an armour row. Derived, not chosen: it is the
# value that brings the legendary share of the donor's torso/head row (static members
# summing to 1188) to ~50%, matching what the weapon row's own master already carries.
ARMOR_UNIQUE_WEIGHT = 850
# Weight for the aggregate armour master in the one free member slot it claims. DERIVED,
# not copied from R-180's BREADTH_WEIGHT: the only armour row with a free member slot in
# the DRX donor shape is the SHIELD row, so whatever the master carries there is competing
# with a shield member at ARMOR_UNIQUE_WEIGHT. At 800 the shield slot took 40.5% of the
# whole armour side (D9, cap 44%, even 20%); at 2 x ARMOR_UNIQUE_WEIGHT the master
# out-weighs the row's own slot and the shield share falls to 37.3% while every other worn
# slot rises. Measured both ways - this is the value that balances the armour side, not a
# round number.
ARMOR_MASTER_WEIGHT = 2 * ARMOR_UNIQUE_WEIGHT

# Path shapes. A member is "unique armour" when it lives under a worn-slot folder AND on
# the `unique` path (the mastertables/unique split the base game itself uses).
_SLOT_FOLDER_RE = re.compile(r'\\(torso|head|arms|legs|shields)\\')
_UNIQUE_ARMOR_RE = re.compile(
    r'\\(torso|head|arms|legs|shields)\\(mastertables\\unique_\w+|unique)\\?')
_UNIQUE_1H_RE = re.compile(r'\\unique_1h_[nel]0\d\.dbr$')
_SINGLE_CLASS_UNIQUE_RE = re.compile(
    r'\\weapons\\unique\\(axe|club|sword|spear|bow|staff|throwing)_[nel]0\d\.dbr$')

# Tables owned by the concurrent orb lane (b79 `fix/orb-loot-breadth`), which covers
# armour slots for ORB tables. Never written here; always PRINTED.
ORB_LANE_PREFIX = 'svc_uberorb_'


def is_orb_lane_table(path):
    return ORB_LANE_PREFIX in SLB._n(path).rsplit('\\', 1)[-1]


def in_scope(path):
    """Mod-owned gear chest tables this module may write."""
    p = SLB._n(path)
    if p in {SLB._n(k) for k in SLB.EXEMPT}:
        return False
    return not is_orb_lane_table(p)


# ─────────────────────────────────────────────────────────────────────────────
# WRITE SIDE
# ─────────────────────────────────────────────────────────────────────────────
def ensure_armor_masters(db, lk=None, verbose=True):
    """Author the 3 aggregate armour masters. Idempotent by the same rule R-180's
    `ensure_masters` uses: a master already carrying exactly the right members is not
    re-written, so two callers never collide."""
    lk = lk or SLB.Lookup(db)
    donor = lk.real(_MASTER_DONOR)
    if not donor:
        print("  ARMOUR BREADTH: WARNING master donor missing (%s); armour masters "
              "not authored" % _MASTER_DONOR)
        return {}
    built = {}
    for tier in TIERS:
        path = ARMOR_MASTER[tier]
        members = [(p, w) for (p, w) in armor_master_members(tier) if lk.real(p)]
        if not members:
            print("  ARMOUR BREADTH: WARNING no armour donors resolve for tier %r; "
                  "master skipped" % tier)
            continue
        want = [(SLB._n(p), w) for p, w in members]
        real = lk.real(path)
        if real:
            have = []
            for i in range(1, len(members) + 1):
                nm = SLB._sc(db.get_field_value(real, 'lootName%d' % i))
                wt = SLB._sc(db.get_field_value(real, 'lootWeight%d' % i))
                if nm:
                    have.append((SLB._n(nm), int(wt or 0)))
            if have == want:
                built[tier] = real
                continue
            path = real
        else:
            db.clone_record(donor, path)
        db.set_field(path, 'FileDescription',
                     'SVC armour master: every worn slot (helm/arms/torso/legs/shield), '
                     '%s tier' % tier)
        for i, (p, w) in enumerate(members, start=1):
            SLB._set_str(db, path, 'lootName%d' % i, lk.real(p))
            db.set_field(path, 'lootWeight%d' % i, int(w))
        for i in range(len(members) + 1, 31):
            if SLB._sc(db.get_field_value(path, 'lootName%d' % i)):
                db.set_field(path, 'lootName%d' % i, '')
            if SLB._sc(db.get_field_value(path, 'lootWeight%d' % i)) not in (None, 0):
                db.set_field(path, 'lootWeight%d' % i, 0)
        db._modified.add(path)
        built[tier] = path
        if verbose:
            print("  ARMOUR BREADTH: master %s = %d worn slots at equal weight"
                  % (path.rsplit('\\', 1)[-1], len(members)))
    lk.refresh()
    return built


def armor_groups(db, real):
    """The loot groups of `real` that carry worn-slot gear, detected from the member
    PATHS rather than assumed to be groups 2/5/6 - a hoard authored from a different
    donor must not slip through on a layout assumption."""
    out = []
    for g in range(1, 7):
        members = SLB._slot_members(db, real, g)
        if any(_SLOT_FOLDER_RE.search(SLB._n(nm)) for _i, nm, _w in members):
            out.append(g)
    return out


def _raise_weight(db, real, field, target):
    cur = SLB._sc(db.get_field_value(real, field))
    cur = int(cur) if cur is not None else 0
    if cur <= 0 or cur >= target:
        return False            # never wake a disabled member, never lower a weight
    db.set_field(real, field, int(target))
    return True


def balance_one_hand(db, real, group):
    r"""`unique_1h_*01` pays THREE classes from ONE member slot. Wherever it sits beside
    SINGLE-class unique weapon tables, set its weight to 3x the largest such sibling, so
    axe/mace/sword each carry a single class's mass instead of a third of one. Strictly
    a raise, and idempotent (the target is recomputed from the siblings, not accumulated).
    This is the loot1 twin of the same correction `svc_loot_breadth._master_members`
    makes inside the aggregate master."""
    members = SLB._slot_members(db, real, group)
    siblings = [w for _i, nm, w in members
                if _SINGLE_CLASS_UNIQUE_RE.search(SLB._n(nm))]
    if not siblings:
        return []
    target = max(siblings) * SLB._ONE_HAND_CLASSES
    changes = []
    for i, nm, _w in members:
        if _UNIQUE_1H_RE.search(SLB._n(nm)):
            if _raise_weight(db, real, 'loot%dWeight%d' % (group, i), target):
                changes.append('loot%dWeight%d unique_1h -> %d (3 classes)'
                               % (group, i, target))
    return changes


def widen_armor_rows(db, table, tier, lk=None):
    """Lift EVERY armour row of one chest table to parity with the weapon row, and give
    it a member that pays all five worn slots. Additive + idempotent; returns the list of
    changes (empty when the table already carries the parity)."""
    lk = lk or SLB.Lookup(db)
    real = lk.real(table)
    master = lk.real(ARMOR_MASTER[tier])
    if not real:
        return []
    changes = []
    groups = armor_groups(db, real)
    for g in groups:
        if SLB._raise_chance(db, real, g, ARMOR_ROW_CHANCE):
            changes.append('loot%dChance->%g' % (g, ARMOR_ROW_CHANCE))
        for i, nm, _w in SLB._slot_members(db, real, g):
            if _UNIQUE_ARMOR_RE.search(SLB._n(nm)):
                if _raise_weight(db, real, 'loot%dWeight%d' % (g, i),
                                 ARMOR_UNIQUE_WEIGHT):
                    changes.append('loot%dWeight%d %s -> %d'
                                   % (g, i, SLB._n(nm).rsplit('\\', 1)[-1],
                                      ARMOR_UNIQUE_WEIGHT))
    # One armour master, into the first armour row that still has a free member slot.
    if master and groups:
        already = any(SLB._n(master) == SLB._n(nm)
                      for g in groups for _i, nm, _w in SLB._slot_members(db, real, g))
        if not already:
            for g in groups:
                idx = SLB._first_free_member(db, real, g)
                if idx is not None:
                    SLB._set_str(db, real, 'loot%dName%d' % (g, idx), master)
                    db.set_field(real, 'loot%dWeight%d' % (g, idx),
                                 int(ARMOR_MASTER_WEIGHT))
                    changes.append('loot%dName%d=armour master' % (g, idx))
                    break
            else:
                # Every armour row is 6/6. Never drop a member to make room - report it,
                # and let the distribution gate decide whether the rates still clear.
                print("  ARMOUR BREADTH: NOTE %s has no free armour-row member slot; "
                      "parity rests on the row chance + unique weights alone"
                      % SLB._n(real).rsplit('\\', 1)[-1])
    # The weapon row's own 1H correction (the "overcorrected" half of R-181).
    for g in range(1, 7):
        changes.extend(balance_one_hand(db, real, g))
    if changes:
        db._modified.add(real)
    return changes


# ─────────────────────────────────────────────────────────────────────────────
# THE SURFACES (what a player experiences as ONE loot event)
#
# A surface is not a table: the Gaoler cage is six physical chests over two records,
# each record resolving one of three themed variants at spawn. The distribution gate
# audits SURFACES, because "4 copies of the same spear in one cage run" is a
# statement about a surface, not about a table.
# ─────────────────────────────────────────────────────────────────────────────
_L = r'records\item\loottables\svc'
_VARIANT_W = (50, 25, 25)


def cage_surfaces(lk):
    """The Polis Daemonai Warden's vault cage: chest_01 and chest_03, on EACH difficulty
    branch, with the 3 themed variants at the ProxyAccessoryPool weights polis_vault
    writes. Auditing all three branches matters: a themed variant is only ever met
    alongside its two siblings, so judging one in isolation would both over-flag a
    deliberate theme and under-flag the mix the player actually opens."""
    out = []
    for N in ('01', '03'):
        for tier in TIERS:
            tabs, wts = [], []
            for v, w in zip(('a', 'b', 'c'), _VARIANT_W):
                if v == 'a':
                    p = (r'%s\polisvault_%s.dbr' % (_L, N) if tier == 'l'
                         else r'%s\polisvault_%s_%s.dbr' % (_L, N, tier))
                else:
                    p = r'%s\polisvault_%s_%s%s.dbr' % (_L, N, tier, v)
                if lk.real(p):
                    tabs.append(p)
                    wts.append(w)
            if tabs:
                out.append(('gaoler cage chest_%s [%s]' % (N, tier), tabs, wts, tier))
    return out


def all_surfaces(db, lk):
    """Every surface the distribution gate covers: the two cage chests as multi-variant
    surfaces, then every remaining in-scope mod chest table as a surface of its own."""
    surfaces = cage_surfaces(lk)
    claimed = {SLB._n(t) for (_l, ts, _w, _tr) in surfaces for t in ts}
    for table in SLB.chest_tables(db, lk):
        if not in_scope(table) or SLB._n(table) in claimed:
            continue
        tier = SLB.infer_tier(db, table, lk)
        if tier is None:
            continue
        surfaces.append((SLB._n(table).rsplit('\\', 1)[-1], [table], [1], tier))
    return surfaces


def audit_db(db, lk=None, verbose=False):
    """The whole-build distribution audit. Returns (problems, reports)."""
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    problems, reports = [], []
    for label, tables, weights, tier in all_surfaces(db, lk):
        probs, rep = SLD.audit_surface(d, dist, label, tables, weights, tier)
        problems.extend(probs)
        reports.append(rep)
        if verbose and rep:
            tot = rep['total'] or 1.0
            print('    %-42s %s' % (label, '  '.join(
                '%s %.2f (%.0f%%)' % (SLD.SLOT_LABEL[s], rep['slot_mass'].get(s, 0.0),
                                      100.0 * rep['slot_mass'].get(s, 0.0) / tot)
                for s in SLD.SLOT_ORDER)))
    return problems, reports
