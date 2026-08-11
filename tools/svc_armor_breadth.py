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
1. THE GUARANTEED SLOT IS A WEAPON SLOT. The 100%-chance slot fires every spawn
   iteration (S = 12.48 on chest_01) and every member of it is a weapon or relic table.
   Armour only ever arrives through the CHANCE rows. Untouched by this module, and now
   ENFORCED rather than merely intended: `armor_groups` skips any group whose chance is
   100, so the theme's own composition survives the sweep (see its docstring - the
   warden theme was being rewritten from 50/50 to 12.8/87.2 before that guard existed).
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
  the 3 DRX donors, i.e. the vault cage, all 8 boss hoards, the 3 guard-pair hoards, the
  3 `svc_uberorb_apex_*` orb tables and the hidden-blood-cave mega chest. Every table
  this module WRITES is also a table the gate AUDITS - `all_surfaces` and the sweep read
  the same scope rule, because a write the gate cannot see is how R-180 stayed GREEN
  through both of Will's reports.
* NO OWNER-BASED EXCLUSION EXISTS. The apex orb tables were carved out on the claim that
  b79 `fix/orb-loot-breadth` covered them; it does not, and its own docstring says so.
  See `in_scope`. The tables b79 really writes (`uberorb_default_*`, `boss_charon_*01b`)
  sit outside `\svc\` and were never in this rule.
* THE 15 R-220 ORB TABLES ARE NOW IN, AND THE OWNERSHIP RULE THAT EXCLUDED THEM IS GONE
  (BL-R181-DEBT-7, closed by `tools/patches/orb_armor_rows.py`). `uberorb_default_*` and
  `boss_charon_*01b` live outside `\svc\`, so R-181's folder-shaped ownership rule never
  reached them and R-220 widened only their WEAPON row: measured on the shipped build80
  arz all fifteen starved, weapon:armour 3.4:1 to 8.4:1 with a thinnest worn slot of
  0.007-0.044 pieces per open against the D7 floor of 0.52. `all_surfaces` no longer asks
  what FOLDER a table lives in - it asks R-220's own scope derivation which tables the
  uber orb chains reach, so a SIXTEENTH orb table is covered the day it is written, with
  no list to update. `ownership_problems` then closes the class outright: any loot table
  a module writes and no surface audits fails the build. See `tools/svc_loot_ownership.py`.
* OUT, BY EVIDENCE, MEASURED AND REPORTED RATHER THAN SILENTLY WIDENED (a Will decision,
  in the R-181 record with numbers): general MONSTER armour drops (BL-R181-DEBT-2) are
  base-game-governed here, mod-owned on 12-14 records of ~1500-1850, and
  `chanceToEquipShield` is not a field on ANY record in the db, so no monster can drop a
  shield off its body at all.
"""
import re
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import svc_loot_breadth as SLB
import svc_loot_distribution as SLD
import svc_loot_ownership as OWN

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
#
# TWO DONOR FAMILIES SPELL "unique" DIFFERENTLY, AND THAT IS WHY THE ORB TABLES STARVED
# (BL-R181-DEBT-7). The xpack/DRX family this module was written against names its
# unique-armour tables `\torso\mastertables\unique_torso_l01.dbr` - the token is
# `unique_<slot>`. The base-game LEVEL-BANDED family the nine `uberorb_default_<band>`
# tables are cloned from instead names `\torso\mastertables\unique\torsoall_n01.dbr` and
# `\head\mastertables\uniques\headall_n01.dbr` - a `unique\` (and, on head, `uniqueS\`)
# SUBFOLDER. The old expression required the token to be `unique_` right after the slot
# folder, so on those nine tables it matched only the shield member, and the four body
# slots kept the donor's weight of 27 against ~1700 of static junk. MEASURED: helm/arms/
# torso/legs 0.026 pieces per open each, against the D7 floor of 0.52.
# The expression below accepts both spellings and is strictly WIDER than the old one
# (every path the old regex matched still matches), so it can only ever raise more
# members - never fewer. Measured on the 42 pre-existing surfaces: 0 records change.
_SLOT_FOLDER_RE = re.compile(r'\\(torso|head|arms|legs|shields)\\')
_UNIQUE_ARMOR_RE = re.compile(
    r'\\(torso|head|arms|legs|shields)\\(mastertables\\)?uniques?')
# Same two-family split on the weapon side: the xpack family names the 3-class one-hand
# master `\weapons\mastertables\unique_1h_l01.dbr`, the level-banded family names
# `\weapons\mastertables\unique\1h_all_l01.dbr`, and its single-class siblings sit under
# `\weapons\mastertables\unique\` rather than `\weapons\unique\`. Without both spellings
# `balance_one_hand` cannot see that ONE member is paying axe+mace+sword, and
# `balance_weapon_row` counts three unique tables as static and over-raises the master.
_UNIQUE_1H_RE = re.compile(r'\\(unique_1h|1h_all)_[nel]0\d\.dbr$')
_SINGLE_CLASS_UNIQUE_RE = re.compile(
    r'\\weapons\\(mastertables\\)?unique\\'
    r'(axe|club|sword|spear|bow|staff|throwing)_[nel]0\d\.dbr$')
# R-180's aggregate weapon master, by name (the mirror of ARMOR_MASTER on this side).
_WEAPON_MASTER_RE = re.compile(r'\\svc_unique_weapons_[nel]01\.dbr$')

# The legendary share a WEAPON row must reach, mirroring what ARMOR_UNIQUE_WEIGHT was
# derived to produce on the body-armour rows (measured after the sweep: torso/head 50.2%,
# arms/legs 50.2%). MEASURED CAUSE, not a taste: `ARMOR_UNIQUE_WEIGHT = 850` is an
# ABSOLUTE weight derived from ONE donor family, and the armour statics happen to be
# identical across families - so every armour row lands at ~50% legendary everywhere. The
# WEAPON row's legendary members were instead left at whatever the donor shipped, and the
# two families differ sharply:
#     DRX donor / vault cage   statics 1500, uniques 1800  ->  54.5% legendary
#     uberorb apex donor       statics 2500, uniques 1050  ->  29.6% legendary
# So lifting armour to parity lifted the apex tables' armour ~17x while their weapon side
# stayed diluted, and they inverted to 0.17:1 weapon:armour - an 85%-armour surface, which
# is Will's "you overcorrected" complaint pointed the other way. Expressing the rule as a
# SHARE instead of an absolute self-corrects across donor families: the cage and the
# blood-cave donors are already above it and are left untouched (verified: 0 records
# change), and only the apex family moves.
WEAPON_ROW_LEGENDARY_SHARE = 0.50

def in_scope(path):
    """Mod-owned gear chest tables this module may write.

    NO OWNER-BASED EXCLUSIONS. A previous round of this module carved out
    `svc_uberorb_apex_{n,e,l}01c` on the stated grounds that the concurrent b79
    `fix/orb-loot-breadth` lane "owns armour slots for orb tables". That was FALSE and a
    vet proved it twice: (1) applying b79's wave to the same arz changes 15 records
    (`uberorb_default_*`, `boss_charon_*01b`, xpack `uberorb_default_*01c`) and touches
    NONE of the three apex tables; (2) b79's own module docstring says so in writing -
    the apex tables "are already widened by the time this module runs and are therefore
    a no-op here", and what it widens is "only the CLASSES the weapon row can pay".
    Nobody was widening armour on them, and because the exclusion also removed them from
    `all_surfaces()` the fail-loud gate could not see the hole either - the exact R-180
    failure mode this wave exists to end.

    They are mod-owned `\\svc\\` gear tables of the ordinary shape, and they are LIVE
    player-facing surfaces: `genericboss05_chest_{normal,epic,legendary}` (the red-uber
    Mystical Orb chests R-200 shipped to Steam) and `bosschest_leinth_{01,02,03}`. So
    they are swept and gated here like every other mod chest. The lane boundary that
    remains real is the one b79 actually writes - the `uberorb_default_*` /
    `boss_charon_*01b` tables, which live outside `\\svc\\` and were never in this
    module's ownership rule to begin with.
    """
    p = SLB._n(path)
    return p not in {SLB._n(k) for k in SLB.EXEMPT}


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


def is_guaranteed_group(db, real, g):
    r"""True when loot group `g` fires on EVERY spawn iteration.

    Read off `loot{G}Chance` rather than assumed to be group 3. That distinction is
    load-bearing and measured: on all 48 chest/hoard tables the guaranteed slot IS
    group 3, but on the three `svc_uberorb_apex_*` tables it is group 4 (g3 there is a
    10% row). A hardcoded `g == 3` would have swept the apex tables' real theme slot
    and skipped their 10% row - the same class of layout assumption `armor_groups`
    already refuses to make about which rows carry armour.
    """
    c = SLB._sc(db.get_field_value(real, 'loot%dChance' % g))
    try:
        return float(c) >= 100.0
    except (TypeError, ValueError):
        return False


def armor_groups(db, real):
    r"""The loot groups of `real` that carry worn-slot gear AND that this module owns,
    detected from the member PATHS rather than assumed to be groups 2/5/6 - a hoard
    authored from a different donor must not slip through on a layout assumption.

    THE GUARANTEED SLOT IS EXCLUDED, and that exclusion is the contract, not a detail.
    The 100%-chance slot is the THEME's instrument: `svc_loot_breadth.THEMES` writes its
    entire composition, and R-181's law is that "each theme keeps its shipped
    weapon:relic:armour split to the percent". Detecting armour rows purely from member
    paths broke that law on exactly three records - `polisvault_01_{n,e,l}c`, the WARDEN
    theme, whose guaranteed slot is deliberately 50% weapon / 50% armour (broad 500 vs
    armour master 400 + shield 60 + torso 40). Sweeping it raised the armour side to
    1700 + 850 + 850 and shipped 12.8% weapon / 87.2% armour - a theme rewritten by a
    later pass, with four documents still stating the shipped split. The sweep owns the
    CHANCE rows; the theme owns the guaranteed row. Measured: this changes 3 records of
    the 51 in scope and no other.
    """
    out = []
    for g in range(1, 7):
        if is_guaranteed_group(db, real, g):
            continue
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


def _is_unique_weapon_member(nm):
    n = SLB._n(nm)
    return bool(_WEAPON_MASTER_RE.search(n) or _UNIQUE_1H_RE.search(n)
                or _SINGLE_CLASS_UNIQUE_RE.search(n))


def balance_weapon_row(db, real, group):
    r"""Bring ONE weapon row's legendary share up to WEAPON_ROW_LEGENDARY_SHARE by
    raising the AGGREGATE WEAPON MASTER, and nothing else. Strictly a raise; returns the
    changes (empty when the row already clears the share).

    WHY THE MASTER AND NOT THE PER-CLASS MEMBERS. The obvious alternative - raise
    `bow_l01` / `staff_l01` / `spear_l01` to a common weight - was measured and rejected:
    the apex weapon row names bow and staff DIRECTLY but has no spear member and no free
    slot to add one, so raising the named members would have paid axe/mace/sword/bow/staff
    ~473 each against SPEAR's 133 - a 3.5x deficit on the exact class R-180 exists to
    protect, rebuilt by the fix for a different defect. The aggregate master pays all six
    classes evenly by construction, so putting the whole increase there leaves the
    within-weapon spread near-uniform (measured after: bow 425 vs spear 375, 1.13x).
    Same law as the armour master: "the master is the even-spread instrument, so any
    per-class bias must be expressed by a THEME, never smuggled in here."
    """
    members = SLB._slot_members(db, real, group)
    master = [(i, nm, w) for i, nm, w in members
              if _WEAPON_MASTER_RE.search(SLB._n(nm))]
    if not master:
        return []
    static = sum(w for _i, nm, w in members if not _is_unique_weapon_member(nm))
    other_unique = sum(w for _i, nm, w in members
                       if _is_unique_weapon_member(nm)
                       and not _WEAPON_MASTER_RE.search(SLB._n(nm)))
    if static <= 0:
        return []
    share = WEAPON_ROW_LEGENDARY_SHARE
    # U / (U + static) = share  ->  U = static * share / (1 - share)
    want_unique = static * share / (1.0 - share)
    target = int(round(want_unique - other_unique))
    changes = []
    for i, _nm, _w in master:
        if _raise_weight(db, real, 'loot%dWeight%d' % (group, i), target):
            changes.append('loot%dWeight%d weapon master -> %d (row legendary share '
                           '-> %.0f%%)' % (group, i, target, 100.0 * share))
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
    # Registering IS writing (svc_loot_ownership): the ledger is populated by the
    # builder, never by its callers, so a new caller cannot forget to claim a table
    # and leave its distribution owned by nobody - the BL-R181-DEBT-7 defect class.
    OWN.note_write(real, 'svc_armor_breadth.widen_armor_rows')
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
        already = False
        for g in groups:
            for i, nm, _w in SLB._slot_members(db, real, g):
                if SLB._n(master) == SLB._n(nm):
                    already = True
                    # Re-assert the weight (raise-only) rather than trusting whatever a
                    # previous run wrote. A cached/partially-built arz carrying an older
                    # ARMOR_MASTER_WEIGHT would otherwise survive the sweep untouched,
                    # and the balance this module commits to would be silently stale.
                    if _raise_weight(db, real, 'loot%dWeight%d' % (g, i),
                                     ARMOR_MASTER_WEIGHT):
                        changes.append('loot%dWeight%d armour master -> %d'
                                       % (g, i, ARMOR_MASTER_WEIGHT))
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
    # The weapon row's own corrections (the "overcorrected" half of R-181). The 1H
    # re-weight runs FIRST because the master's parity target is computed from the row's
    # final non-master unique mass, which the 1H raise is part of.
    for g in range(1, 7):
        changes.extend(balance_one_hand(db, real, g))
    # ... and the weapon side's own share parity, so lifting armour cannot invert a
    # surface. Skips the guaranteed slot for the same reason armor_groups does: that row
    # belongs to the THEME.
    for g in range(1, 7):
        if is_guaranteed_group(db, real, g):
            continue
        changes.extend(balance_weapon_row(db, real, g))
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


# ── R-220's tables, derived from R-220's own scope rule (never typed here) ───
def orb_scope(db, lk):
    r"""{norm(table): (real, tier)} for every loot table an UBER's mystical orb reaches.

    THIS IS A DERIVATION, NOT A LIST, and that is the whole point of BL-R181-DEBT-7.
    R-181 decided what it owned by asking what FOLDER a table lived in; R-220 then wrote
    fifteen tables in other folders and their armour belonged to nobody. Asking R-220's
    own `scope_tables` instead means the answer to "which orb tables exist" has exactly
    ONE implementation, on the lane that owns the orbs - so a sixteenth orb table, or a
    rewired drop chain, is inside the distribution gate the moment R-220 sees it.

    Derived MOD-ONLY (no `base_rows`). R-220 derives over mod UNION base to catch a
    base-only uber, but a base-only chain is by definition one the overlay does not
    contain and therefore one nothing can widen OR audit - `svc_orb_breadth.OUT_OF_REACH`
    is where that decision lives. Measured on the build80 arz: mod-only and union give the
    same 18 tables, and the union's one extra proxy (the Dark Obelisk) is the pinned
    out-of-reach chain. Running mod-only here keeps the distribution gate free of a
    base-arz dependency it would otherwise acquire.

    Cached per db by record count: the derivation costs a full 51k-record template scan
    and `all_surfaces` is called by apply(), by the gate and by `--calibrate`.
    """
    try:
        import svc_orb_breadth as SOB
    except ImportError as exc:              # pragma: no cover - packaging
        # Never a silent narrowing: if R-220's module is gone, the 15 orb tables drop
        # out of the audit set, which is the exact hole this function closes.
        print("  ARMOUR BREADTH: WARNING svc_orb_breadth is not importable (%r), so the "
              "uber orb loot tables are NOT in the distribution surface set this run. "
              "No silent pass: this line IS the downgrade." % (exc,))
        return {}
    # Cached ON THE DB, keyed by its record count, so two dbs in one process (the
    # negative battery builds a fresh one per case) can never read each other's scope.
    count = len(db.record_names())
    hit = getattr(db, '_svc_orb_scope_cache', None)
    if hit is None or hit[0] != count:
        hit = (count, SOB.scope_tables(db, lk))
        db._svc_orb_scope_cache = hit
    return hit[1]


def orb_surfaces(db, lk, claimed):
    """Every R-220 orb table as a surface of its own, skipping ones already claimed.

    An orb is opened alone - one uber dies, one orb drops - so unlike the cage there is
    no multi-variant pool to aggregate: the table IS the surface. The 3
    `svc_uberorb_apex_*` tables are already claimed by the mod-ownership sweep above and
    are skipped here rather than audited twice.
    """
    out = []
    for _key, (table, tier) in sorted(orb_scope(db, lk).items()):
        real = lk.real(table)
        if not real or SLB._n(real) in claimed:
            continue
        claimed.add(SLB._n(real))
        out.append(("orb %s" % SLB._n(real).rsplit('\\', 1)[-1], [real], [1], tier))
    return out


def all_surfaces(db, lk):
    r"""Every surface the distribution gate covers: the two cage chests as multi-variant
    surfaces, then every remaining in-scope mod chest table as a surface of its own, then
    the 3 DRX donors, then every loot table an uber's mystical orb reaches.

    THE DONORS ARE AUDITED BECAUSE THEY ARE WRITTEN. `armor_loot_breadth.apply()` sweeps
    `targets + SLB.DRX_DONORS.values()`, so the blood-cave mega chest
    (`loottable_hidden_bloodcave_{01,02,03}`) is a record this wave EDITS - but the donor
    names match neither half of `chest_tables`' mod-ownership rule (`\svc\` / `svc_`), so
    they fell out of the audit set while staying in the write set. A vet caught it: they
    are the most weapon-inverted surfaces in the mod (w:a 0.31 / 0.37 / 0.33) and they
    are the very case MIN_WEAPON_ARMOUR_RATIO cites as its binding derivation, yet the
    gate could not see them. Nothing may be written by this wave and left unaudited.
    """
    surfaces = cage_surfaces(lk)
    claimed = {SLB._n(t) for (_l, ts, _w, _tr) in surfaces for t in ts}
    for table in SLB.chest_tables(db, lk):
        if not in_scope(table) or SLB._n(table) in claimed:
            continue
        tier = SLB.infer_tier(db, table, lk)
        if tier is None:
            continue
        claimed.add(SLB._n(table))
        surfaces.append((SLB._n(table).rsplit('\\', 1)[-1], [table], [1], tier))
    for tier, table in sorted(SLB.DRX_DONORS.items()):
        if not lk.real(table) or SLB._n(table) in claimed:
            continue
        claimed.add(SLB._n(table))
        surfaces.append((SLB._n(table).rsplit('\\', 1)[-1], [table], [1], tier))
    surfaces.extend(orb_surfaces(db, lk, claimed))
    return surfaces


# ─────────────────────────────────────────────────────────────────────────────
# OWNERSHIP: no loot table a module writes may escape the distribution gate
# ─────────────────────────────────────────────────────────────────────────────
def ownership_problems(db, lk=None, surfaces=None):
    r"""The structural half of BL-R181-DEBT-7. Returns a list of problem strings.

    R-181 shipped a fail-loud distribution gate and it was GREEN while fifteen live
    surfaces starved, because the gate audited the tables R-181 had decided it owned and
    R-220 wrote fifteen others. No number could have caught that; only a rule about
    WRITES can. So:

        every loot table written in this build must be in the surface set.

    TWO WITNESSES (`tools/svc_loot_ownership.py` explains why one is not enough):
      * the LEDGER - the four shared loot builders register every table they touch, so
        any caller is covered, including dry runs and the negative battery;
      * the REGISTRY TOUCH LOG - `patches/__init__.run_registry` records every
        `db._modified.add()` against the module that made it, which also catches a module
        that writes loot fields RAW without going through a builder. Restricted to
        FixedItemLoot records, because that is the template the distribution model reads;
        a LootMasterTable (the masters this wave authors) is a component of a surface,
        not a surface.

    `svc_loot_breadth.EXEMPT` is the ONE escape hatch and it costs a written reason - the
    same door a non-gear mod table already uses.
    """
    lk = lk or SLB.Lookup(db)
    audited = {SLB._n(t) for (_l, ts, _w, _tr) in
               (surfaces if surfaces is not None else all_surfaces(db, lk))
               for t in ts}
    exempt = {SLB._n(k) for k in SLB.EXEMPT}
    problems = []

    def _uncovered(table_l):
        return table_l not in audited and table_l not in exempt

    for table_l, writers in sorted(OWN.writes().items()):
        if _uncovered(table_l):
            problems.append(
                "OWN1 %s is WRITTEN by %s but no distribution surface audits it. A loot "
                "table nobody audits is how BL-R181-DEBT-7 shipped fifteen starving "
                "surfaces through two green gates. Put it in a surface (derive it, never "
                "type it) or, if it is not a gear container, add it to "
                "svc_loot_breadth.EXEMPT with a reason."
                % (table_l, ', '.join(writers)))

    reg = OWN.registry_writes(db)
    if reg is None:
        print("  ARMOUR BREADTH: NOTE no registry touch log on this db "
              "(db._registry_touch_log absent), so OWN2 - the witness that catches a "
              "module writing loot rows RAW, without a shared builder - did not run this "
              "pass. The ledger witness (OWN1) still did. No silent pass: this line IS "
              "the downgrade.")
    else:
        for table_l, modules in sorted(reg.items()):
            real = lk.real(table_l)
            if not real or not SLB._n(lk.tpl(real)).endswith('fixeditemloot.tpl'):
                continue
            if _uncovered(table_l):
                problems.append(
                    "OWN2 %s is a FixedItemLoot container WRITTEN by registry module(s) "
                    "%s, and no distribution surface audits it. Same rule as OWN1: cover "
                    "it with a derived surface, or EXEMPT it with a reason."
                    % (table_l, ', '.join(modules)))
    return problems


def apply_wave(db, lk=None, quiet=True):
    r"""Apply the whole R-180 + R-181 chest wave to `db` IN MEMORY, exactly as the build
    does, and return (db, lk).

    ONE implementation, three consumers: `gate_loot_distribution.py --apply`, the
    negative tests, and any probe that needs to compare a pre-wave arz with the post-wave
    state. The `gate_relic_difficulty_tiers` precedent - the standalone tool, the in-build
    gate and the negtests must not be able to disagree about what "after the wave" means,
    which they can the moment two of them keep their own copy of this sequence.

    Safe to call on an already-built arz: every step is idempotent and raise-only.
    """
    import contextlib
    import io
    from patches import armor_loot_breadth as ALB
    from patches import chest_loot_breadth as CLB
    try:
        # R-220 (b79) runs AFTER this module in the registry and edits loot tables, so a
        # dry run that omitted it would not be measuring what the build produces. Guarded
        # by ImportError only so this file still works on a tree where b79 has not landed.
        from patches import orb_loot_breadth as OLB
    except ImportError:
        OLB = None
    try:
        # ... and BL-R181-DEBT-7's module runs after THAT, because the armour parity it
        # writes on the orb tables includes the weapon row's own share balance, which can
        # only be computed once R-220 has put the breadth master in the row.
        from patches import orb_armor_rows as OAR
    except ImportError:
        OAR = None
    try:
        # R-184/185/186 (b81) runs BEFORE chest_loot_breadth in the registry and AUTHORS
        # the thrown tables that `_master_members` names as the seventh class. Omitting it
        # here would measure a master whose thrown member silently fell out of
        # `ensure_masters` (the `if lk.real(p)` filter), i.e. NOT what the build produces.
        # Same ImportError guard as b79, for the same reason.
        from patches import craft_thrown_breadth as CTB
    except ImportError:
        CTB = None
    lk = lk or SLB.Lookup(db)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf) if quiet else contextlib.nullcontext():
        if CTB is not None:
            CTB.apply(db, None)      # registry order: it runs before chest_loot_breadth
        SLB.ensure_masters(db, lk)
        ensure_armor_masters(db, lk)
        lk.refresh()
        for N, themes in (('01', ['martial', 'hunter', 'warden']),
                          ('03', ['apex', 'adept', 'sovereign'])):
            for tier in TIERS:
                for v, theme in zip(('a', 'b', 'c'), themes):
                    if v == 'a':
                        p = (r'%s\polisvault_%s.dbr' % (_L, N) if tier == 'l'
                             else r'%s\polisvault_%s_%s.dbr' % (_L, N, tier))
                    else:
                        p = r'%s\polisvault_%s_%s%s.dbr' % (_L, N, tier, v)
                    if lk.real(p):
                        SLB.set_guaranteed_theme(db, p, tier, theme, lk)
                        SLB.widen_weapon_row(db, p, tier, lk)
        CLB.apply(db, None)
        ALB.apply(db, None)
        if OLB is not None:
            OLB.apply(db, None)          # registry order: orb_loot_breadth, then ...
        if OAR is not None:
            OAR.apply(db, None)          # ... orb_armor_rows, the last loot writer
    lk.refresh()
    return db, lk


def audit_db(db, lk=None, verbose=False):
    """The whole-build distribution audit. Returns (problems, reports)."""
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    problems, reports = [], []
    seen_labels = set()
    # D3X: the per-tier D3 era exemptions are re-proved from the bytes ONCE per audit,
    # before any surface is measured, so a carve-out can never outlive the era fact that
    # earned it (b81 / R-186; see SLD.D3_ERA_EXEMPT).
    problems.extend(SLD.era_exemption_problems(d))
    for label, tables, weights, tier in all_surfaces(db, lk):
        probs, rep = SLD.audit_surface(d, dist, label, tables, weights, tier)
        problems.extend(probs)
        reports.append(rep)
        seen_labels.add(label)
        # STALE D5 PIN: a pinned surface that has fallen back under the global cap is
        # dead config, and dead config is how an exemption outlives its reason (the
        # svc_orb_breadth.OUT_OF_REACH stale-pin discipline, applied to the same class
        # of decision). Reported, never quietly kept.
        pin = SLD.D5_PINNED.get(label)
        if pin and rep and rep.get('top_items'):
            share = rep['top_items'][0][1] / (rep['total'] or 1.0)
            if share <= SLD.MAX_ITEM_SHARE_TOTAL:
                problems.append(
                    "D5 STALE PIN: %s is pinned at %.3f but its worst single-item share "
                    "is now %.4f, under the global cap of %.3f. Remove the pin from "
                    "svc_loot_distribution.D5_PINNED - a ceiling nothing needs is a "
                    "ceiling nobody re-reads." % (label, pin[0], share,
                                                  SLD.MAX_ITEM_SHARE_TOTAL))
    for label in sorted(SLD.D5_PINNED):
        if label not in seen_labels:
            problems.append(
                "D5 STALE PIN: %s is pinned in svc_loot_distribution.D5_PINNED but is "
                "no longer a surface this gate audits. Remove the pin, or find out why "
                "the surface vanished." % label)
        if verbose and rep:
            tot = rep['total'] or 1.0
            print('    %-42s %s' % (label, '  '.join(
                '%s %.2f (%.0f%%)' % (SLD.SLOT_LABEL[s], rep['slot_mass'].get(s, 0.0),
                                      100.0 * rep['slot_mass'].get(s, 0.0) / tot)
                for s in SLD.SLOT_ORDER)))
    return problems, reports
