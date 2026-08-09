r"""gate_relic_difficulty_tiers.py - AUDIT: no wrong-tier relic (or unique) drops on
the wrong difficulty (Will 2026-08-08).

WHY THIS EXISTS
---------------
A container's relic tier is fixed by the relic table it names: 01_act*_relics =
Essence (Normal), 02_ = Embodiment (Epic), 03_ = Incarnation (Legendary); the unique
mastertables carry the same tier in their _n01 / _e01 / _l01 suffix. A single flat
FixedItemContainer cannot difficulty-scale its own loot, so the mod difficulty-scales
by wrapping each placement in a Class=Proxy whose accessory1 / accessoryEpic1 /
accessoryLegendary1 slots select a per-difficulty container:

    Proxy.accessory1        -> Normal    -> ... -> loot table (must be 01 / _n01)
    Proxy.accessoryEpic1    -> Epic      -> ... -> loot table (must be 02 / _e01)
    Proxy.accessoryLegendary1 -> Legendary -> ... -> loot table (must be 03 / _l01)

The difficulty of each branch is therefore GROUND TRUTH from the accessory slot it
hangs off, NOT from a name suffix (mod tables like polisvault_01..05 use the suffix
as a CHEST index, not a tier, so a name-only classifier gives false positives). This
gate follows the WIRING - for every Proxy in the db, it walks each difficulty
accessory slot down to the FixedItemLoot table and asserts every relic + unique slot
there names that branch's OWN difficulty tier. Base-game loot tables (boss_default_*,
c_default_*, ...) are level-banded by design and are NOT tier-locked, so only
MOD-OWNED loot tables (the \svc\ / svc_ namespace) are checked.

THE OLD GATE'S BLIND SPOT (why it is rewritten): the previous audit classified a
per-difficulty family as correct by NAME-COMPLETENESS alone (all three tiers present),
so it reported GREEN while the general-guard hoards leaked - loot_02 and loot_03 both
named unique_1h_n01 + 01_act4_relics (normal) on the Epic and Legendary branches. This
gate reads the actual per-branch tier, so that leak reds.

Usage:
  py tools/gate_relic_difficulty_tiers.py <arz>              # audit, exit 1 on any leak
  py tools/gate_relic_difficulty_tiers.py <arz> --verbose    # print every branch checked

Reused in-build by tools/patches/polis_vault.verify() (audit_proxy_chain) so the
standalone audit and the fail-loud build gate share ONE tier implementation.
"""
import re
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase

# accessory slot -> the difficulty tier it selects.
ACCESSORY_TIERS = (('accessory1', 'n'), ('accessoryEpic1', 'e'), ('accessoryLegendary1', 'l'))
_RELIC_FOR = {'n': '01', 'e': '02', 'l': '03'}
_TIER_WORD = {'n': 'Normal(Essence/01)', 'e': 'Epic(Embodiment/02)', 'l': 'Legendary(Incarnation/03)'}

# relic table: ...\loottables\relics\NN_act*_relics.dbr  (NN = 01/02/03 tier)
_RELIC_RE = re.compile(r'\\relics\\(\d\d)_act\w*_relics\.dbr$')
# unique mastertable / \unique\ table: ..._[nel]0N[a].dbr  (the n/e/l letter = tier)
_UNIQUE_TIER_RE = re.compile(r'_([nel])0\d[a-z]?\.dbr$')


def _n(s):
    return str(s).replace('/', '\\').lower()


def _scalar(v):
    return v[0] if isinstance(v, list) and v else v


class _Lookup:
    """Case-insensitive record resolver over a single arz."""
    def __init__(self, db):
        self.db = db
        self._lower = {_n(x): x for x in db.record_names()}

    def real(self, path):
        if path is None:
            return None
        if not isinstance(path, str):
            path = _scalar(path)
            if not isinstance(path, str):
                return None
        return self._lower.get(_n(path))

    def gv(self, path, field):
        r = self.real(path) if isinstance(path, str) else path
        return _scalar(self.db.get_field_value(r, field)) if r else None


# ── module-level convenience wrappers (polis_vault.verify uses real/audit_proxy_chain)
def real(db, path):
    return _Lookup(db).real(path)


def is_mod_loot(pathl):
    r"""A loot table this mod authored (its records live in the \svc\ folder or carry
    the svc_ record-name prefix). Base-game level-banded tables are out of scope."""
    pl = _n(pathl)
    return '\\svc\\' in pl or '\\svc_' in pl


def is_relic(pathl):
    return _RELIC_RE.search(_n(pathl)) is not None


def relic_tier(pathl):
    m = _RELIC_RE.search(_n(pathl))
    return m.group(1) if m else None


def is_unique(pathl):
    return 'unique' in _n(pathl)


def unique_tier(pathl):
    m = _UNIQUE_TIER_RE.search(_n(pathl))
    return m.group(1) if m else None


def _loot_string_slots(db, loot_real):
    """(field, value) for every loot* string slot on a FixedItemLoot table."""
    ff = db.get_fields(loot_real) or {}
    out = []
    for k, tf in ff.items():
        b = k.split('###')[0]
        if not b.lower().startswith('loot'):
            continue
        for v in tf.values:
            if isinstance(v, str) and v:
                out.append((b, v))
    return out


def check_loot_table_tier(db, lk, loot_path, want, ctx=''):
    """Every relic + unique slot on a MOD-OWNED loot table must match `want`
    (n/e/l). Returns a list of human-readable problem strings (empty = clean)."""
    problems = []
    loot_real = lk.real(loot_path)
    if not loot_real:
        return problems  # a missing table is a wiring problem caught elsewhere, not a tier leak
    want_relic = _RELIC_FOR[want]
    base = _n(loot_path).rsplit('\\', 1)[-1]
    for field, val in _loot_string_slots(db, loot_real):
        vl = _n(val)
        if is_relic(vl):
            t = relic_tier(vl)
            if t is not None and t != want_relic:
                problems.append("%s%s :: %s = %s -> relic tier %s, but this is the %s "
                                "branch" % (ctx, base, field, val, t, _TIER_WORD[want]))
        elif is_unique(vl):
            t = unique_tier(vl)
            if t is not None and t != want:
                problems.append("%s%s :: %s = %s -> unique tier %s, but this is the %s "
                                "branch" % (ctx, base, field, val, t, _TIER_WORD[want]))
    return problems


def _containers_from_pool(db, lk, pool_path):
    """The FixedItemContainer(s) a ProxyAccessoryPool can spawn (fixedItemName1..8)."""
    out = []
    pr = lk.real(pool_path)
    if not pr:
        return out
    for i in range(1, 9):
        fin = lk.gv(pr, 'fixedItemName%d' % i)
        if fin:
            out.append(fin)
    return out


def audit_proxy_chain(db, proxy_path, lk=None, verbose=False, counter=None):
    """Walk one Proxy's difficulty accessory slots down to their loot tables and
    tier-check every MOD-OWNED loot table reached. Returns a list of problems. If a
    mutable `counter` list is passed, appends one entry per mod-owned loot table
    actually audited (so the whole-build report can count real coverage)."""
    lk = lk or _Lookup(db)
    pr = lk.real(proxy_path)
    if not pr:
        return []
    problems = []
    pbase = _n(proxy_path).rsplit('\\', 1)[-1]
    for slot, want in ACCESSORY_TIERS:
        pool = lk.gv(pr, slot)
        if not pool:
            continue
        for cont in _containers_from_pool(db, lk, pool):
            loot = lk.gv(cont, 'tables')
            if not loot or not is_mod_loot(loot):
                continue
            if counter is not None:
                counter.append((pbase, slot, _n(loot).rsplit('\\', 1)[-1]))
            ctx = '%s[%s] ' % (pbase, slot)
            if verbose:
                print("    check %s %s -> %s" % (ctx, _TIER_WORD[want],
                                                 _n(loot).rsplit('\\', 1)[-1]))
            problems.extend(check_loot_table_tier(db, lk, loot, want, ctx))
    return problems


def audit_db(db, verbose=False):
    """Whole-build audit: every Proxy record, every mod-owned loot table reachable
    from a difficulty accessory slot. Returns (problems, n_branches_checked)."""
    lk = _Lookup(db)
    problems = []
    branches = []
    for name in db.record_names():
        if db._record_types.get(name) != 'Proxy':
            continue
        if not any(db.get_field_value(name, slot) for slot, _ in ACCESSORY_TIERS):
            continue
        problems.extend(audit_proxy_chain(db, name, lk, verbose=verbose,
                                          counter=branches))
    return problems, len(branches)


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/gate_relic_difficulty_tiers.py <arz> [--verbose]")
        return 2
    verbose = '--verbose' in argv[2:]
    db = ArzDatabase.from_arz(Path(argv[1]))
    problems, checked = audit_db(db, verbose=verbose)
    print("\n=== relic/unique difficulty-tier audit ===")
    print("mod-owned per-difficulty loot branches audited: %d" % checked)
    if problems:
        print("WRONG-TIER MEMBERS: %d" % len(problems))
        for p in problems:
            print("  LEAK  %s" % p)
        print("\nGATE FAIL: a relic/unique drops on the wrong difficulty.")
        return 1
    print("GATE PASS: every mod-owned per-difficulty loot table names only its own "
          "tier (Normal=Essence/01, Epic=Embodiment/02, Legendary=Incarnation/03).")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
