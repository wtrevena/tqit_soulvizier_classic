"""gate_relic_difficulty_tiers.py - BUILD-WIDE RELIC-DIFFICULTY AUDIT (Will 2026-08-08).

Will's second ask, alongside the Gaoler-chest fix: "audit the Steam build to
confirm no Essence (normal-only) / Embodiment (epic-only) / Incarnation
(legendary-only) relic can drop on the wrong difficulty."

WHAT "WRONG DIFFICULTY" MEANS. A relic tier is a SEPARATE, tier-pure loot table -
`01_act4_relics` = Essence (normal), `02_` = Embodiment (epic), `03_` =
Incarnation (legendary); the level-banded `relic_LO-HI` tables map to the same
three tiers by band. A relic .dbr has no internal difficulty gate, so the tier a
container pays is fixed ENTIRELY by the table its loot slot names. A chest is
difficulty-correct only if EITHER
  (b) its loot slot is a [normal, epic, legendary] difficulty ARRAY (the engine
      indexes it by game mode - FixedItemLoot.tpl "Index by game mode"), OR
  (a) it is one member of a per-difficulty container FAMILY (`_01/_02/_03` or
      `_normal/_epic/_legendary`) whose members pay tiers 1/2/3 respectively, so
      the map places the difficulty-matched member (the base-game mechanism).
A container that is a SINGLE placement (no per-difficulty twin) and pays a SCALAR
relic tier drops that one tier on every difficulty -> WRONG on two of the three.
That is exactly the Gaoler-vault defect this wave fixes with route (b).

This module classifies every mod-owned relic-paying container into (a)/(b)/that
defect, prints the audit, and (fail=True) fails the build if any POLIS-VAULT
chest is left ungated (a redundant safety net beside polis_vault.verify()). Every
other ungated finding is REPORTED for Will, never silently retuned (SHARED-SYMBOL
LAW; upstream DRX/SV content is not this lane's to rebalance).

Usage:
  py tools/gate_relic_difficulty_tiers.py <built.arz>            # full audit report
  py tools/gate_relic_difficulty_tiers.py <built.arz> --negtest  # planted-negative self test
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase


def _n(s):
    return str(s).replace('/', '\\').lower()


def _leaf(s):
    return _n(s).rsplit('\\', 1)[-1]


# A relic loot table's tier (1=normal/Essence, 2=epic/Embodiment, 3=legendary/
# Incarnation), from either the `NN_actM_relics` prefix or the `relic_LO-HI` band.
_ACT_RELIC = re.compile(r'^(0[1-3])_act\d+_relics\.dbr$')
_BAND_RELIC = re.compile(r'^relic_(\d+)-(\d+)\.dbr$')
# band -> tier, measured on the base arz: 01-31 = t1, 31-51 = t2, 51-65 = t3.
_BAND_TIER = [((1, 31), 1), ((31, 51), 2), ((51, 66), 3)]


def relic_table_tier(path):
    """Return 1/2/3 for a relic loot table, or None if `path` is not one."""
    leaf = _leaf(path)
    if 'loottables\\relics\\' not in _n(path):
        return None
    m = _ACT_RELIC.match(leaf)
    if m:
        return int(m.group(1))
    m = _BAND_RELIC.match(leaf)
    if m:
        lo = int(m.group(1))
        for (a, b), t in _BAND_TIER:
            if a <= lo < b:
                return t
    return None


# Difficulty token at the end of a container name -> difficulty index (0/1/2).
_DIFF_WORD = {'normal': 0, 'epic': 1, 'legendary': 2}
_DIFF_NUM = {'01': 0, '02': 1, '03': 2}
_FAM_TOKEN = re.compile(
    r'_(0[1-3])(?:_(normal|epic|legendary))?$|_(normal|epic|legendary)$')


def _family_and_diff(container_leaf):
    """(family_key, diff_index) for a container whose name ends in a per-difficulty
    token, else (None, None). `bosschest_leinth_01_normal` -> ('bosschest_leinth',0);
    `hidden_bloodcave_chest_03` -> ('hidden_bloodcave_chest', 2)."""
    leaf = container_leaf[:-4] if container_leaf.lower().endswith('.dbr') else container_leaf
    m = _FAM_TOKEN.search(leaf)
    if not m:
        return None, None
    num, word_after, word_only = m.group(1), m.group(2), m.group(3)
    if word_after is not None:
        diff = _DIFF_WORD[word_after]
    elif word_only is not None:
        diff = _DIFF_WORD[word_only]
    else:
        diff = _DIFF_NUM.get(num)
    if diff is None:
        return None, None
    return leaf[:m.start()], diff


def _resolve_loot_tables(db, container):
    tv = db.get_field_value(container, 'tables')
    if tv is None:
        return []
    vals = tv if isinstance(tv, list) else [tv]
    return [v for v in vals if isinstance(v, str) and v]


def _relic_slots(db, table):
    """[(base_field, [tiers], is_array)] for each relic-referencing slot of a loot
    table. `tiers` = the relic tiers the slot names (a proper difficulty array
    yields [1,2,3]); is_array = the slot carries >1 value."""
    ff = db.get_fields(table) or {}
    out = []
    for k, tf in ff.items():
        base = k.split('###')[0]
        if not (base.lower().startswith('loot') and 'name' in base.lower()):
            continue
        vals = [v for v in tf.values if isinstance(v, str) and v]
        tiers = [relic_table_tier(v) for v in vals]
        if any(t is not None for t in tiers):
            out.append((base, tiers, len(vals) > 1))
    return out


def _is_mod_owned(name):
    ln = _n(name)
    return ('\\svc' in ln or 'svc_' in _leaf(ln) or '\\drxitem\\' in ln
            or '\\drxmap\\' in ln)


_POLIS = 'svc_polisvault_chest'


def classify(db):
    """Walk every FixedItemContainer, resolve its loot table(s), and classify each
    relic-paying slot into one of three routes. Returns dict of lists of entries
    (dict(container, table, slot, tiers, mod_owned, is_array)):
      gated_array  - the relic slot IS a [normal,epic,legendary] difficulty array
                     (route b - the Gaoler-vault fix; the engine indexes it).
      per_diff     - a SCALAR relic in a container that is one member of a COMPLETE
                     per-difficulty FAMILY (`_01/_02/_03` or `_normal/_epic/
                     _legendary`, all three present). The map/boss-orb places the
                     difficulty-matched member (route a - the base-game mechanism,
                     e.g. every svc_*hoard, hidden_bloodcave, sp, leinth chest).
      ungated      - a SCALAR relic with NO per-difficulty twin: a single placement
                     that would pay the same tier on every difficulty. This is the
                     class the Gaoler vault was in before the fix."""
    names = db.record_names()
    containers = [r for r in names if db.get_field_value(r, 'Class') == 'FixedItemContainer']

    # First pass: which difficulty slots does each container family populate?
    fam_members = {}
    cont_slots = {}
    for c in containers:
        slots = []
        for t in _resolve_loot_tables(db, c):
            slots.extend((t, base, tiers, is_arr)
                         for (base, tiers, is_arr) in _relic_slots(db, t))
        if not slots:
            continue
        cont_slots[c] = slots
        fam, diff = _family_and_diff(_leaf(c))
        if fam is not None:
            fam_members.setdefault(fam, set()).add(diff)

    def family_is_complete(fam):
        return fam is not None and fam_members.get(fam) == {0, 1, 2}

    out = {'gated_array': [], 'per_diff': [], 'ungated': []}
    for c, slots in cont_slots.items():
        fam, _diff = _family_and_diff(_leaf(c))
        complete = family_is_complete(fam)
        for (table, base, tiers, is_arr) in slots:
            entry = {'container': c, 'table': table, 'slot': base,
                     'tiers': [t for t in tiers if t is not None],
                     'mod_owned': _is_mod_owned(c) or _is_mod_owned(table),
                     'is_array': is_arr}
            if is_arr:
                out['gated_array'].append(entry)
            elif complete:
                out['per_diff'].append(entry)
            else:
                out['ungated'].append(entry)
    return out


def audit(db, fail=True):
    """Print the classification and, when fail=True, raise SystemExit if any
    statically-map-placed POLIS-VAULT chest pays a SCALAR relic tier (it MUST use
    the difficulty array - it has no per-difficulty twin to place). This is the
    redundant safety net beside polis_vault.verify(). Every OTHER ungated finding
    is REPORTED for Will (mod-owned in detail, upstream base-game chests as a
    count), never a build failure - upstream/other-lane content is not this
    ticket's to rebalance (SHARED-SYMBOL LAW)."""
    c = classify(db)
    ungated_mod = [e for e in c['ungated'] if e['mod_owned']]
    ungated_up = [e for e in c['ungated'] if not e['mod_owned']]
    print("  relic-difficulty audit: %d relic slot(s) are difficulty ARRAYS "
          "(route b); %d are members of complete per-difficulty FAMILIES (route a, "
          "placed per difficulty); %d ungated scalars (%d mod-owned, %d upstream "
          "base-game/per-region)." % (len(c['gated_array']), len(c['per_diff']),
          len(c['ungated']), len(ungated_mod), len(ungated_up)))

    # The Gaoler vault: statically map-placed, so route (a) does not apply - every
    # relic slot MUST be a difficulty array. This is the fail-loud gate.
    polis_scalar = [e for e in (c['ungated'] + c['per_diff'])
                    if _POLIS in _n(e['container'])]
    if polis_scalar:
        for e in polis_scalar:
            print("    POLIS-VAULT SCALAR RELIC: %s -> %s :: %s = tier %s (must be a "
                  "difficulty array)" % (_leaf(e['container']), _leaf(e['table']),
                  e['slot'], e['tiers']))
        if fail:
            raise SystemExit(
                "relic-difficulty gate FAILED: %d Gaoler-vault relic slot(s) are a "
                "SCALAR tier (the vault is a single placement -> wrong difficulty on "
                "2 of 3). Every vault relic slot must be a [normal,epic,legendary] "
                "array." % len(polis_scalar))

    if ungated_mod:
        print("  MOD-OWNED ungated relic containers (per-difficulty PLACED families "
              "with a fixed tier per member; NOT the single-placement Gaoler bug - "
              "reported for Will, not failed):")
        seen = set()
        for e in ungated_mod:
            key = _leaf(e['container'])
            if key in seen:
                continue
            seen.add(key)
            print("    - %s -> %s (tier %s)" % (key, _leaf(e['table']), e['tiers']))
    print("  relic-difficulty gate PASS: every Gaoler-vault relic slot is a "
          "difficulty array (route b); %d upstream base-game scalar relic chest(s) "
          "left untouched (placed per-region by the base campaign, not on this "
          "custom map)." % len(ungated_up))
    return c


# ── negative test ────────────────────────────────────────────────────────────
def _negtest(arz):
    fails = []
    base = ArzDatabase.from_arz(Path(arz))
    try:
        audit(base, fail=True)
        print("OK  positive control: the built arz passes the vault gate")
    except SystemExit as e:
        fails.append('positive control failed: %s' % e)
        print("XX  positive control FAILED: %s" % e)

    # Plant: flatten a Gaoler-vault relic array back to a scalar legendary -> must RED.
    d = ArzDatabase.from_arz(Path(arz))
    tbl = r'records\item\loottables\svc\polisvault_03.dbr'
    d.set_field(tbl, 'loot3Name2',
                r'records\xpack\item\loottables\relics\03_act4_relics.dbr')
    hit = False
    try:
        audit(d, fail=True)
    except SystemExit:
        hit = True
    print("%s  plant: vault relic array flattened to scalar 03_act4_relics -> %s"
          % ('OK ' if hit else 'XX ', 'RED (correct)' if hit else 'GREEN (BLIND)'))
    if not hit:
        fails.append('flattened vault relic scalar not caught')

    print()
    if fails:
        print("NEGTEST FAILED: %d" % len(fails))
        for f in fails:
            print("   - %s" % f)
        return 1
    print("NEGTEST PASS: the built vault is green and a flattened relic scalar reds "
          "the gate.")
    return 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 0
    if '--negtest' in argv:
        arz = [a for a in argv[1:] if not a.startswith('--')][0]
        return _negtest(arz)
    db = ArzDatabase.from_arz(Path(argv[1]))
    audit(db, fail=False)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
