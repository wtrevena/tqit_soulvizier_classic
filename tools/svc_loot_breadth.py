r"""svc_loot_breadth.py - THE CHEST-LOOT BREADTH CONTRACT (Will 2026-08-10).

WILL, VERBATIM (2026-08-10)
---------------------------
"we need to update the chests in the test hub in the place where the Polybotes Soul
drops in the prison of souls so that they drop different items since right now I am
seeing every chest drop the same items pretty much ever playthrough, there are never
any legendary spears dropped it is basically the same items dropped over and over by
all chests. we need to expand the bredth of the legendary items dropped in the testhub
chests and also in the steam version."

THE TWO DEFECTS (measured on the live DEV arz 9c190b99, 51,204 records)
-----------------------------------------------------------------------
(a) ZERO LEGENDARY SPEARS, structurally. Every mod chest's weapon row is a clone of the
    DRX donor `loottable_hidden_bloodcave_0N`, whose loot1 names exactly:
        static_all_l01a (w1000) . static_staff_l01a (w500) . unique_1h_l01 (w200)
        . bow_l01 (w200) . staff_l01 (w200)
    `unique_1h_l01` is a LootMasterTable with exactly THREE children: axe_l01, club_l01,
    sword_l01. Spear, thrown and every 2H class are not members. The donor compensates for
    bow and staff by naming them DIRECTLY, and simply forgot the third excluded class,
    SPEAR. The only spear path left is static_all_l01a -> static_spear_l01a, a static
    randomizer table with 0 Legendary leaves. So a legendary spear was impossible - all 24
    legendary spears in the DB were unreachable from all 40 mod chest tables.

(b) THE SAME ITEMS EVERY OPEN. loot3Chance=100 with a single member (unique_1h_l01) made
    one axe/mace/sword unique the only slot that reliably fired, while loot1 (weapons) and
    loot6 (shields) fired at 14% each. Expected non-guaranteed slot hits per open: 1.13.

THE FIX (this module is the ONE implementation; nothing may re-derive it)
-------------------------------------------------------------------------
FixedItemLoot.tpl is capped at 6 groups x 6 members (measured across base + mod: max group
6, max member 6), and the donor's loot1 already uses 5 of its 6 member slots. So breadth
CANNOT be added by listing more tables in loot1. It is added the way the base game does it:
one LootMasterTable that aggregates the weapon classes, dropped into the single free slot.

  1. MASTER (per tier): `records\item\loottables\svc\svc_unique_weapons_{n,e,l}01.dbr`,
     a clone of the base `all_l01` LootMasterTable shape, naming unique_1h + spear + bow +
     staff (xpack band, matching the tables the donor already names) PLUS the base
     mastertables all_{tier}0{1,2,3} (the act-1/2/3 legendaries the xpack tables omit).
     Its name carries `unique` + the `_{tier}01` suffix ON PURPOSE, so the EXISTING
     gate_relic_difficulty_tiers tier check reads its difficulty straight off the name and
     a wrong-tier wiring reds without any new rule.
  2. WEAPON ROW: loot1Name6 = that master (the one free member slot), weight 800, and the
     dead group chances raised (loot1 14 -> 40, loot6 14 -> 30) so more than one slot fires.
  3. GUARANTEED SLOT: the loot3 weapon member is repointed from `unique_1h_*01` (3 classes)
     to the master (all 6 classes). Weights are PRESERVED, so the weapon:relic split of every
     chest is byte-identical to what shipped - only the CLASSES it can pay change.
     Per-chest THEMES add a small class-bias member on top (see THEMES).

NON-REDUCTION LAW (Will farms the Gaoler cage on Legendary; R-100 #17 / Will 2026-08-08):
numSpawn equations are never touched here, no member is ever removed, no chance is ever
lowered, and the guaranteed slot stays at 100%. Every edit is additive or a strict raise.

TIER LAW (R-100 #17 + Will 2026-08-08) is preserved by construction: every donor is resolved
through the per-tier map, so Normal only ever gains normal-tier tables (all measured
Epic-classification, 0 Legendary), Epic epic-tier, Legendary legendary-tier.

Also the audit half of the breadth gate (`audit_db`) so the standalone
`tools/gate_chest_loot_breadth.py`, the in-build registry gate
(`tools/patches/chest_loot_breadth.verify`) and the negative tests all share ONE
implementation and cannot disagree (the gate_relic_difficulty_tiers precedent).
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import DATA_TYPE_STRING as S

TIERS = ('n', 'e', 'l')
_RELIC_INDEX = {'n': '01', 'e': '02', 'l': '03'}

# ── The per-tier weapon-class donors (every one byte-verified present in the live arz) ──
_XP_UNIQUE = r'records\xpack\item\loottables\weapons\unique\%s_%s01.dbr'          # fam, tier
_XP_1H = r'records\xpack\item\loottables\weapons\mastertables\unique_1h_%s01.dbr'  # tier
_BASE_ALL = r'records\item\loottables\weapons\mastertables\unique\all_%s0%d.dbr'   # tier, idx

# The mod-owned aggregate master this module authors, one per difficulty tier.
MASTER = {t: r'records\item\loottables\svc\svc_unique_weapons_%s01.dbr' % t for t in TIERS}
_MASTER_DONOR = r'records\item\loottables\weapons\mastertables\unique\all_l01.dbr'

# Members of the aggregate master: (path template applied per tier, weight).
def _master_members(tier):
    out = [(_XP_1H % tier, 1000)]
    for fam in ('spear', 'bow', 'staff'):
        out.append((_XP_UNIQUE % (fam, tier), 1000))
    for i in (1, 2, 3):
        out.append((_BASE_ALL % (tier, i), 700))
    # THE SEVENTH CLASS (Will 2026-08-10, "yes we should make the legendary thrown
    # weapons droppable"): this TQIT-era database ships NO unique one-hand-ranged loot
    # table, so the mod authors one. Lazy import - svc_craft_thrown imports THIS module,
    # so the reference must not be resolved at import time. A tier whose thrown table
    # does not exist yet is simply skipped by ensure_masters' `if lk.real(p)` filter, and
    # the next ensure_masters call (chest_loot_breadth's, which runs after
    # craft_thrown_breadth) rewrites the master with it.
    import svc_craft_thrown as SCT
    out.append((SCT.THROWN_TABLE[tier], SCT.THROWN_MASTER_WEIGHT))
    return out


# ── Loot-slot kinds a chest theme may name (resolved per tier) ──
def kind_path(kind, tier):
    """Resolve a theme kind to its TIER-CORRECT loot table (never a mixed tier)."""
    if kind == 'broad':
        return MASTER[tier]
    if kind == 'unique_1h':
        return _XP_1H % tier
    if kind in ('spear', 'bow', 'staff', 'axe', 'club', 'sword'):
        return _XP_UNIQUE % (kind, tier)
    if kind == 'relic':
        return r'records\xpack\item\loottables\relics\%s_act4_relics.dbr' % _RELIC_INDEX[tier]
    if kind == 'shield':
        return r'records\xpack\item\loottables\shields\unique\shield_%s01.dbr' % tier
    if kind in ('torso', 'head', 'arms', 'legs'):
        return (r'records\xpack\item\loottables\%s\mastertables\unique_%s_%s01.dbr'
                % (kind, kind, tier))
    if kind in ('amulet', 'finger'):
        return r'records\xpack\item\loottables\%s\unique\%s_%s01.dbr' % (kind, kind, tier)
    raise KeyError('svc_loot_breadth: unknown loot kind %r' % kind)


# ── PER-CHEST THEMES (the "chests must not all mirror one another" half) ─────
# Each theme is the GUARANTEED (loot3) member set as [(kind, weight), ...], max 6.
# LAW: the weapon:relic weight split of the chest that shipped is preserved (the
# weapon side of every theme sums to the weight the single unique_1h member used to
# carry), so this differentiates WHAT drops, never HOW MUCH.
THEMES = {
    # Gaoler cage chest_01 (no relic in its guaranteed slot, exactly as shipped).
    'martial': [('broad', 100), ('spear', 60), ('unique_1h', 40)],
    'hunter': [('broad', 100), ('bow', 60), ('spear', 40)],
    'warden': [('broad', 100), ('shield', 60), ('torso', 40)],
    # Gaoler cage chest_03 (apex: keeps its 100/100 weapon-vs-relic split verbatim).
    'apex': [('relic', 100), ('broad', 100)],
    'adept': [('relic', 100), ('broad', 70), ('staff', 30)],
    'sovereign': [('relic', 100), ('broad', 70), ('amulet', 15), ('finger', 15)],
}
THEME_LABEL = {
    'martial': 'martial (spear + one-hand melee bias)',
    'hunter': 'hunter (bow + spear bias)',
    'warden': 'warden (shield + heavy armour bias)',
    'apex': 'apex (any weapon class + relic)',
    'adept': 'adept (staff/caster bias + relic)',
    'sovereign': 'sovereign (jewellery bias + relic)',
}

# Raised group chances (the "only one slot ever fires" half). Never lowered: the
# helper takes max(existing, target), so a richer table keeps its own value.
WEAPON_ROW_CHANCE = 40.0     # loot1 (weapons), shipped 14.0
SHIELD_ROW_CHANCE = 30.0     # loot6 (shields), shipped 14.0
BREADTH_WEIGHT = 800         # loot1Name6 weight for the aggregate master

# The DRX donor tables every mod chest is cloned from. Widened too, so the esti /
# hidden-bloodcave mega chest (a canonical + Steam chest with the identical defect)
# gains the same breadth and no future clone can re-inherit the collapsed row.
DRX_DONORS = {
    'n': r'records\drxitem\container\loottable_hidden_bloodcave_01.dbr',
    'e': r'records\drxitem\container\loottable_hidden_bloodcave_02.dbr',
    'l': r'records\drxitem\container\loottable_hidden_bloodcave_03.dbr',
}

# Mod-owned FixedItemLoot records that are NOT gear chests and are therefore out of
# breadth scope. Anything else that is mod-owned MUST satisfy the contract, so a new
# chest can never quietly ship collapsed (fail-loud-by-default).
EXEMPT = {
    r'records\item\loottables\svc\toxeus_rant_perplayer.dbr':
        'per-player Toxeus rant scroll (a single quest-flavour item, not a gear chest)',
}


# ─────────────────────────────────────────────────────────────────────────────
# db helpers (case-insensitive resolution; ArzDatabase itself is case-sensitive)
# ─────────────────────────────────────────────────────────────────────────────
def _n(s):
    return str(s).replace('/', '\\').lower()


def _sc(v):
    return v[0] if isinstance(v, list) and v else v


class Lookup:
    """Case-insensitive record resolver over one ArzDatabase (rebuilt on demand:
    modules author records while a sweep runs)."""

    def __init__(self, db):
        self.db = db
        self._lower = {_n(x): x for x in db.record_names()}

    def refresh(self):
        self._lower = {_n(x): x for x in self.db.record_names()}

    def real(self, path):
        if not path:
            return None
        if not isinstance(path, str):
            path = _sc(path)
            if not isinstance(path, str):
                return None
        return self._lower.get(_n(path))

    def gv(self, path, field):
        r = self.real(path) if isinstance(path, str) else path
        return _sc(self.db.get_field_value(r, field)) if r else None

    def tpl(self, path):
        return _n(self.gv(path, 'templateName') or '')


def is_loot_table(lk, path):
    t = lk.tpl(path)
    if t:
        return 'loot' in t.rsplit('\\', 1)[-1]
    return 'loot' in _n(lk.gv(path, 'Class') or '')


def is_mod_owned(pathl):
    r"""A loot table this mod authored: it lives in an \svc\ folder or carries the
    svc_ record-name prefix (the same rule gate_relic_difficulty_tiers uses)."""
    p = _n(pathl)
    return '\\svc\\' in p or '\\svc_' in p


# ─────────────────────────────────────────────────────────────────────────────
# WRITE SIDE
# ─────────────────────────────────────────────────────────────────────────────
def ensure_masters(db, lk=None, verbose=True):
    """Author the 3 aggregate weapon masters (idempotent: a master that already
    carries the right members is not re-written, so two callers never collide).
    Returns {tier: path} for the masters that exist afterwards."""
    lk = lk or Lookup(db)
    donor = lk.real(_MASTER_DONOR)
    if not donor:
        print("  LOOT BREADTH: WARNING master donor missing (%s); breadth masters "
              "not authored" % _MASTER_DONOR)
        return {}
    built = {}
    for tier in TIERS:
        path = MASTER[tier]
        members = [(p, w) for (p, w) in _master_members(tier) if lk.real(p)]
        if not members:
            print("  LOOT BREADTH: WARNING no weapon donors resolve for tier %r; "
                  "master skipped" % tier)
            continue
        want = [(_n(p), w) for p, w in members]
        real = lk.real(path)
        if real:
            have = []
            for i in range(1, len(members) + 1):
                nm = _sc(db.get_field_value(real, 'lootName%d' % i))
                wt = _sc(db.get_field_value(real, 'lootWeight%d' % i))
                if nm:
                    have.append((_n(nm), int(wt or 0)))
            if have == want:
                built[tier] = real           # already correct: write nothing
                continue
            path = real
        else:
            db.clone_record(donor, path)
        db.set_field(path, 'FileDescription',
                     'SVC breadth master: every unique weapon class, %s tier' % tier)
        for i, (p, w) in enumerate(members, start=1):
            _set_str(db, path, 'lootName%d' % i, lk.real(p))
            db.set_field(path, 'lootWeight%d' % i, int(w))
        # Zero any donor member slots we did not claim (no stale inherited class).
        for i in range(len(members) + 1, 31):
            if _sc(db.get_field_value(path, 'lootName%d' % i)):
                db.set_field(path, 'lootName%d' % i, '')
            if _sc(db.get_field_value(path, 'lootWeight%d' % i)) not in (None, 0):
                db.set_field(path, 'lootWeight%d' % i, 0)
        db._modified.add(path)
        built[tier] = path
        if verbose:
            print("  LOOT BREADTH: master %s = %d weapon tables (spear included)"
                  % (path.rsplit('\\', 1)[-1], len(members)))
    lk.refresh()
    return built


def _set_str(db, real, field, value):
    """Write a STRING field, passing the dtype ONLY when the field is new. House law
    (CLAUDE.md): never hand set_field an explicit dtype for a field a cloned record
    already carries; let the donor's own dtype stand."""
    exists = any(k.split('###')[0] == field for k in (db.get_fields(real) or {}))
    if exists:
        db.set_field(real, field, value)
    else:
        db.set_field(real, field, value, S)


def _slot_members(db, real, group):
    """[(index, name, weight)] for the occupied members of one loot group."""
    out = []
    for i in range(1, 7):
        nm = _sc(db.get_field_value(real, 'loot%dName%d' % (group, i)))
        if nm:
            wt = _sc(db.get_field_value(real, 'loot%dWeight%d' % (group, i)))
            out.append((i, str(nm), int(wt or 0)))
    return out


def _first_free_member(db, real, group):
    for i in range(1, 7):
        if not _sc(db.get_field_value(real, 'loot%dName%d' % (group, i))):
            return i
    return None


def _raise_chance(db, real, group, target):
    cur = _sc(db.get_field_value(real, 'loot%dChance' % group))
    cur = float(cur) if cur is not None else 0.0
    if cur <= 0.0 or cur >= target:
        return False        # never switch a dormant slot ON, never lower a chance
    db.set_field(real, 'loot%dChance' % group, float(target))
    return True


def widen_weapon_row(db, table, tier, lk=None):
    """Put the aggregate weapon master into the ONE free loot1 member slot and raise
    the two dead group chances. Additive + idempotent: returns the list of changes
    (empty when the table already carries the breadth)."""
    lk = lk or Lookup(db)
    real = lk.real(table)
    master = lk.real(MASTER[tier])
    if not real or not master:
        return []
    changes = []
    have = {_n(nm) for (_i, nm, _w) in _slot_members(db, real, 1)}
    if _n(master) not in have:
        idx = _first_free_member(db, real, 1)
        if idx is None:
            # 6/6 members already: the master cannot be added without dropping a
            # class, and dropping one is never allowed. Fail loud, do not guess.
            raise SystemExit(
                "svc_loot_breadth: %s has no free loot1 member slot for the breadth "
                "master (FixedItemLoot caps at 6); resolve by hand" % table)
        _set_str(db, real, 'loot1Name%d' % idx, master)
        db.set_field(real, 'loot1Weight%d' % idx, int(BREADTH_WEIGHT))
        changes.append('loot1Name%d=breadth master' % idx)
    if _raise_chance(db, real, 1, WEAPON_ROW_CHANCE):
        changes.append('loot1Chance->%g' % WEAPON_ROW_CHANCE)
    if _raise_chance(db, real, 6, SHIELD_ROW_CHANCE):
        changes.append('loot6Chance->%g' % SHIELD_ROW_CHANCE)
    if changes:
        db._modified.add(real)
    return changes


_UNIQUE_1H_RE = re.compile(r'\\unique_1h_[nel]0\d\.dbr$')


def retarget_guaranteed_weapon(db, table, tier, lk=None):
    """Blast radius (F5): on a chest whose GUARANTEED loot3 slot pays a 3-class
    `unique_1h_*01`, repoint that member at the aggregate master. Weight untouched,
    so the guaranteed weapon:relic split is byte-identical - only the classes it can
    pay widen (axe/mace/sword -> every weapon class, spear included).

    A table that ALREADY names the master in its guaranteed slot has been THEMED by
    its owner (set_guaranteed_theme), and a theme's explicit per-class member is
    deliberate bias, not a collapse. Those are left completely alone: re-aiming them
    would both duplicate the master and erase the theme (measured in the dry-run),
    and it would make this sweep a second writer of another module's records."""
    lk = lk or Lookup(db)
    real = lk.real(table)
    master = lk.real(MASTER[tier])
    if not real or not master:
        return []
    members = _slot_members(db, real, 3)
    if any(_n(nm) == _n(master) for _i, nm, _w in members):
        return []
    changes = []
    for i, nm, _w in members:
        if _UNIQUE_1H_RE.search(_n(nm)):
            _set_str(db, real, 'loot3Name%d' % i, master)
            changes.append('loot3Name%d: unique_1h -> breadth master' % i)
    if changes:
        db._modified.add(real)
    return changes


def set_guaranteed_theme(db, table, tier, theme, lk=None):
    """Write a chest THEME into the guaranteed loot3 slot (the per-chest character).
    Members are resolved TIER-CORRECT, filtered to donors that exist, and written in
    order; unclaimed member slots are cleared so no donor member survives. The slot
    stays at 100% (never lowered)."""
    lk = lk or Lookup(db)
    real = lk.real(table)
    if not real:
        return []
    spec = THEMES[theme]
    members = []
    for kind, weight in spec:
        p = lk.real(kind_path(kind, tier))
        if p:
            members.append((p, int(weight)))
    if not members:
        raise SystemExit("svc_loot_breadth: theme %r resolves to no donor at tier %r "
                         "(table %s)" % (theme, tier, table))
    if len(members) > 6:
        raise SystemExit("svc_loot_breadth: theme %r has %d members; FixedItemLoot "
                         "allows 6" % (theme, len(members)))
    for i in range(1, 7):
        if i <= len(members):
            _set_str(db, real, 'loot3Name%d' % i, members[i - 1][0])
            db.set_field(real, 'loot3Weight%d' % i, members[i - 1][1])
        else:
            if _sc(db.get_field_value(real, 'loot3Name%d' % i)):
                db.set_field(real, 'loot3Name%d' % i, '')
            if _sc(db.get_field_value(real, 'loot3Weight%d' % i)) not in (None, 0):
                db.set_field(real, 'loot3Weight%d' % i, 0)
    db.set_field(real, 'loot3Chance', 100.0)
    db._modified.add(real)
    return ['loot3=%s theme (%d members)' % (theme, len(members))]


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT SIDE (shared by the standalone gate, the in-build gate and the negtests)
# ─────────────────────────────────────────────────────────────────────────────
# Every weapon class a gear chest must be able to pay at its own tier. SPEAR IS
# NAMED EXPLICITLY: its absence is the exact defect Will reported.
REQUIRED_WEAPON_CLASSES = (
    'WeaponMelee_Axe',
    'WeaponMelee_Mace',
    'WeaponMelee_Sword',
    'WeaponHunting_Spear',
    'WeaponHunting_Bow',
    'WeaponMagical_Staff',
)
# The item classification a chest of each tier must pay. MEASURED: every *_n01 unique
# table in the DB is 100% Epic-classification (0 Legendary), which is the Normal tier's
# top rung and exactly what R-100 #17 / Will 2026-08-08 require (no legendary gear on
# Normal). Epic and Legendary chests must reach true Legendary items.
TARGET_IC = {'n': 'Epic', 'e': 'Legendary', 'l': 'Legendary'}
# Distinct target-classification items a chest must be able to roll. MEASURED by the
# dry-run against the live DEV arz 9c190b99 (docs/BACKLOG.md gate record):
#   tier   before this wave   after      floor
#   n      99 Epic            181 Epic   150
#   e      90 Legendary       111        95
#   l      258 Legendary      308        260
# Each floor sits ~15% under the measured value (so ordinary content edits do not trip
# it) and ABOVE the collapsed pre-wave value (so a silent revert to the 3-class weapon
# row reds on B2 even if B1 were somehow satisfied).
POOL_FLOOR = {'n': 150, 'e': 95, 'l': 260}
# Legendary GEAR is forbidden on the Normal branch (tier law). Formulae are exempt:
# 7 ItemArtifactFormula records are legendary-classified and legitimately reach Normal.
_LEG_ON_NORMAL_EXEMPT_CLASSES = {'ItemArtifactFormula', 'ItemArtifact'}


class Expander:
    """Loot-tree -> leaf item expander with memoisation (a whole-build audit expands
    40+ chest tables over a 51k-record db; without the memo it is minutes)."""

    _WALK_PREFIX = ('loot', 'item', 'table', 'bonustable')

    def __init__(self, db, lk=None):
        self.db = db
        self.lk = lk or Lookup(db)
        self._memo = {}

    def leaves(self, path):
        key = _n(path)
        hit = self._memo.get(key)
        if hit is not None:
            return hit
        out = set()
        self._walk(path, set(), out, 0)
        frozen = frozenset(out)
        self._memo[key] = frozen
        return frozen

    def _walk(self, path, stack, out, depth):
        key = _n(path)
        if key in stack or depth > 12:
            return
        real = self.lk.real(path)
        if not real:
            return
        if not is_loot_table(self.lk, real):
            out.add(real)
            return
        memo = self._memo.get(key)
        if memo is not None:
            out |= memo
            return
        stack.add(key)
        sub = set()
        for k, tf in (self.db.get_fields(real) or {}).items():
            b = k.split('###')[0].lower()
            if not b.startswith(self._WALK_PREFIX):
                continue
            if 'weight' in b or 'chance' in b or 'equation' in b:
                continue
            for v in tf.values:
                if isinstance(v, str) and v.lower().endswith('.dbr'):
                    self._walk(v, stack, sub, depth + 1)
        stack.discard(key)
        self._memo[key] = frozenset(sub)
        out |= sub

    def classify(self, item):
        return (str(_sc(self.db.get_field_value(item, 'itemClassification')) or ''),
                str(_sc(self.db.get_field_value(item, 'Class')) or ''))

    def pool(self, table, ic):
        """{Class: set(item)} for the leaves of `table` with itemClassification `ic`."""
        by_class = defaultdict(set)
        for it in self.leaves(table):
            c, cls = self.classify(it)
            if c == ic:
                by_class[cls].add(it)
        return by_class


_TIER_SUFFIX_RE = re.compile(r'_([nel])0\d[a-z]?\.dbr$')
_RELIC_TIER_RE = re.compile(r'\\relics\\(\d\d)_act\w*_relics\.dbr$')
_TIER_FOR_RELIC = {'01': 'n', '02': 'e', '03': 'l'}


def infer_tier(db, table, lk):
    """A chest table's difficulty tier, read from the tables it NAMES (never from its
    own file name - the polisvault_0N suffix is a chest index, not a tier). Majority
    vote over every tier-suffixed member; None when the table names none."""
    real = lk.real(table)
    if not real:
        return None
    votes = Counter()
    for k, tf in (db.get_fields(real) or {}).items():
        if not k.split('###')[0].lower().startswith('loot'):
            continue
        for v in tf.values:
            if not isinstance(v, str) or not v.lower().endswith('.dbr'):
                continue
            vl = _n(v)
            m = _RELIC_TIER_RE.search(vl)
            if m:
                votes[_TIER_FOR_RELIC[m.group(1)]] += 1
                continue
            m = _TIER_SUFFIX_RE.search(vl)
            if m:
                votes[m.group(1)] += 1
    if not votes:
        return None
    return votes.most_common(1)[0][0]


def chest_tables(db, lk=None):
    """Every mod-owned FixedItemLoot record (the breadth contract's scope), sorted."""
    lk = lk or Lookup(db)
    out = []
    for name in db.record_names():
        if not _n(lk.tpl(name)).endswith('fixeditemloot.tpl'):
            continue
        if is_mod_owned(name):
            out.append(name)
    return sorted(out)


def audit_table(db, table, tier, ex, floor=None):
    """The per-chest breadth contract. Returns a list of problem strings.
      B1 every REQUIRED weapon class is reachable at the tier's own classification
         (SPEAR named explicitly - the reported defect);
      B2 the distinct target-classification pool is at least POOL_FLOOR[tier];
      B3 (Normal only) no legendary GEAR leaked in (tier law, formulae exempt);
      C1/C2 the THROWN (one-hand-ranged) class is payable at the tier - the seventh
         class, added 2026-08-10. It carries its own rule rather than joining
         REQUIRED_WEAPON_CLASSES because the tier expectations differ: measured, this
         TQIT-era db has no droppable Epic-classification thrown record at all, so
         Normal's presence is carried by the itemLevel-30 wand band while Epic and
         Legendary must reach a true Legendary thrown. Implementation lives in
         tools/svc_craft_thrown.thrown_problems (ONE implementation, as with B1-B3).
    """
    problems = []
    base = _n(table).rsplit('\\', 1)[-1]
    ic = TARGET_IC[tier]
    by_class = ex.pool(table, ic)
    total = sum(len(v) for v in by_class.values())
    missing = [c for c in REQUIRED_WEAPON_CLASSES if not by_class.get(c)]
    if missing:
        problems.append(
            "B1 %s [%s tier] reaches NO %s item of class(es): %s (a chest must be able "
            "to pay every weapon class at its own tier)"
            % (base, tier, ic, ', '.join(missing)))
    fl = POOL_FLOOR[tier] if floor is None else floor
    if total < fl:
        problems.append("B2 %s [%s tier] reaches only %d distinct %s items, floor is %d "
                        "(the pool collapsed)" % (base, tier, total, ic, fl))
    if tier == 'n':
        leaked = set()
        for cls, items in ex.pool(table, 'Legendary').items():
            if cls and cls not in _LEG_ON_NORMAL_EXEMPT_CLASSES:
                leaked |= items
        if leaked:
            problems.append("B3 %s [normal tier] reaches %d LEGENDARY gear item(s) "
                            "(tier law: Normal pays Essence/normal-tier only); e.g. %s"
                            % (base, len(leaked), sorted(leaked)[0]))
    # C1/C2 - the thrown class. Lazy import: svc_craft_thrown imports this module.
    import svc_craft_thrown as SCT
    problems.extend(SCT.thrown_problems(db, table, tier, ex))
    return problems


def audit_db(db, verbose=False, lk=None):
    """Whole-build breadth audit over every mod-owned chest loot table.
    Returns (problems, stats) where stats = {table: (tier, pool_size, classes)}."""
    lk = lk or Lookup(db)
    ex = Expander(db, lk)
    problems = []
    stats = {}
    exempt_low = {_n(k) for k in EXEMPT}
    for table in chest_tables(db, lk):
        if _n(table) in exempt_low:
            continue
        tier = infer_tier(db, table, lk)
        if tier is None:
            problems.append("B0 %s names no tier-identifiable loot table; it is either "
                            "not a gear chest (add it to svc_loot_breadth.EXEMPT with a "
                            "reason) or its rows are empty" % table)
            continue
        probs = audit_table(db, table, tier, ex)
        problems.extend(probs)
        by_class = ex.pool(table, TARGET_IC[tier])
        stats[table] = (tier, sum(len(v) for v in by_class.values()),
                        {c: len(v) for c, v in sorted(by_class.items())})
        if verbose:
            print("    %-58s [%s] %4d %s items, %d classes"
                  % (_n(table).rsplit('\\', 1)[-1], tier, stats[table][1],
                     TARGET_IC[tier], len(by_class)))
    return problems, stats


def differentiation_problems(db, families, lk=None):
    """B3 (differentiation): the loot tables a placed chest can spawn must not be
    field-identical to one another. `families` = {label: [table, ...]}. A future
    copy-paste that re-flattens a cage back to one table reds here."""
    lk = lk or Lookup(db)
    problems = []
    for label, tables in sorted(families.items()):
        sigs = {}
        for t in tables:
            real = lk.real(t)
            if not real:
                problems.append("B3 %s: table missing: %s" % (label, t))
                continue
            sig = tuple(sorted(
                (k.split('###')[0], tuple(str(x) for x in tf.values))
                for k, tf in (db.get_fields(real) or {}).items()))
            if sig in sigs:
                problems.append("B3 %s: %s is field-identical to %s (the chests would "
                                "mirror one another)"
                                % (label, _n(t).rsplit('\\', 1)[-1],
                                   _n(sigs[sig]).rsplit('\\', 1)[-1]))
            else:
                sigs[sig] = t
    return problems
