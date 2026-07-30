#!/usr/bin/env python3
r"""b102 record-diff: every delta must be ATTRIBUTABLE to R-105/R-106/R-107,
R-100 #11 or R-100 #17. Anything else is an unattributed change and fails.

Usage:
  py tools/debug/b102_record_diff.py <baseline.arz> <built.arz>

Baseline = a build of `main` in THIS environment, made BEFORE any of this lane's
edits (local/baseline_main.arz, md5 6a3a491db546b603c52132237c40aa63,
55,475,226 B, 51,124 records, main @ 7efd107).

THE THREE LEGITIMATE DELTA CLASSES, each checked against the code that produced
it rather than against a list typed into this file:

  A  chanceToEquipFinger2 on a soul carrier, and the new value is EXACTLY what
     build_svc_database.ruled_soul_equip_rate() says (the ONE shared
     classifier). No other field on that record may differ.
  B  reagent1/2/3BaseName on one of the 12 lesserpotionofexperience formulas,
     and the change is ADDITIVE ONLY - every baseline entry still present, in
     the same order, with new entries appended.
  C  the Polis vault loot tables' guaranteed slots moving off the normal-tier
     donors (unique_1h_n01 / 01_act4_relics) onto the chest's own legendary
     tier (unique_1h_l01 / 03_act4_relics).

A REMOVED record is ALWAYS a failure (retirement protocol: this lane withdrew
chest PLACEMENTS, never records). An ADDED record is a failure too - none of the
three items creates content.

Exit 0 = every delta attributed, 0 removed, 0 added.
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / 'patches'))

from arz_patcher import ArzDatabase          # noqa: E402
import build_svc_database as bsd             # noqa: E402
import apply_svc_patches as asp              # noqa: E402
import soul_act_classifier as sac            # noqa: E402


def norm(s):
    return str(s).lower().replace('/', '\\')


def fields_of(db, name):
    out = {}
    ff = db.get_fields(name)
    if not ff:
        return out
    for k, tf in ff.items():
        out.setdefault(k.split('###')[0], list(tf.values))
    return out


_NORMAL_TIER = ('unique_1h_n01.dbr', '01_act4_relics.dbr')
_LEGENDARY_TIER = ('unique_1h_l01.dbr', '03_act4_relics.dbr')


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    old = ArzDatabase.from_arz(Path(argv[1]))
    new = ArzDatabase.from_arz(Path(argv[2]))
    old_names = {norm(n): n for n in old.record_names()}
    new_names = {norm(n): n for n in new.record_names()}
    print("baseline records: %d   built records: %d" % (len(old_names), len(new_names)))

    removed = sorted(set(old_names) - set(new_names))
    added = sorted(set(new_names) - set(old_names))
    print("REMOVED: %d    ADDED: %d" % (len(removed), len(added)))

    # the ruled rate for every carrier, from the SHARED classifier over the BUILT db
    rmem, pmem = bsd.soul_spawn_provenance_sets(new)
    ruled = {}
    for rec, cls, cur in asp._soul_carrier_roster(new):
        ruled[norm(rec)] = bsd.ruled_soul_equip_rate(rec, cls, cur, rmem, pmem)
    # the 12 formulas
    _act_of, formulas = sac.read_formula_membership(new)
    formula_recs = {norm(r) for r in formulas.values()}
    # the vault loot tables
    import polis_vault as pv
    vault_loot = {norm(x) for x in pv._CHEST_LOOT}

    classes = Counter()
    unattributed = []
    field_hist = Counter()
    for key in sorted(set(old_names) & set(new_names)):
        fo = fields_of(old, old_names[key])
        fn = fields_of(new, new_names[key])
        changed = [f for f in set(fo) | set(fn) if fo.get(f) != fn.get(f)]
        if not changed:
            continue
        for f in changed:
            field_hist[f] += 1
        ok = True
        why = []
        for f in changed:
            if f == 'chanceToEquipFinger2' and key in ruled:
                want = ruled[key]
                got = float(fn.get(f, [0])[0])
                if want is not None and abs(got - want) < 0.01:
                    why.append('A')
                    continue
                ok = False
                why.append('A?%s(want %s got %s)' % (f, want, got))
            elif f in sac.REAGENT_FIELDS and key in formula_recs:
                before = [norm(v) for v in fo.get(f, [])]
                after = [norm(v) for v in fn.get(f, [])]
                if after[:len(before)] == before and len(after) >= len(before):
                    why.append('B')
                    continue
                ok = False
                why.append('B?%s(not additive)' % f)
            elif key in vault_loot and f.lower().startswith('loot'):
                b = norm(fo.get(f, [''])[0] if fo.get(f) else '')
                a = norm(fn.get(f, [''])[0] if fn.get(f) else '')
                if any(b.endswith(m) for m in _NORMAL_TIER) and \
                   any(a.endswith(m) for m in _LEGENDARY_TIER):
                    why.append('C')
                    continue
                ok = False
                why.append('C?%s(%s -> %s)' % (f, b, a))
            else:
                ok = False
                why.append('X:%s' % f)
        if ok:
            classes[''.join(sorted(set(why)))] += 1
        else:
            unattributed.append((new_names[key], why))

    print("\nATTRIBUTED modified records by class:")
    for k, v in sorted(classes.items()):
        print("   class %-6s %d" % (k or '(none)', v))
    print("   TOTAL attributed: %d" % sum(classes.values()))
    print("\nchanged-field histogram: %s" % dict(field_hist))

    fail = False
    if removed:
        fail = True
        print("\nFAIL - REMOVED records (%d):" % len(removed))
        for r in removed[:20]:
            print("   ", r)
    if added:
        fail = True
        print("\nFAIL - ADDED records (%d):" % len(added))
        for r in added[:20]:
            print("   ", r)
    if unattributed:
        fail = True
        print("\nFAIL - UNATTRIBUTED modified records (%d):" % len(unattributed))
        for r, why in unattributed[:25]:
            print("    %-72s %s" % (r, why))
    if fail:
        return 1
    print("\nPASS: %d modified records, ALL attributed to R-105/106/107 (A), "
          "R-100 #11 (B) or R-100 #17 (C); 0 REMOVED, 0 ADDED."
          % sum(classes.values()))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
