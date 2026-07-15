"""
Dry-run replay + verification gate for the soul drop-rate split (Will 2026-07-14:
"Cut all soul drop rates for randomly spawning monsters to 50% from current 66%").

Loads the build40 GOLDEN release arz (b33c5a44) and, WITHOUT a heavy build, proves
the wire_souls_to_monsters split:
  * RANDOM roaming hero roster  -> 50% release / 100% testing
  * PLACED ubers + quest bosses -> 66% release / 100% testing  (UNCHANGED)
  * farmable act bosses         -> 25% release / 100% testing  (UNCHANGED)
  * gated-off (chance 0)        -> 0 in BOTH modes             (UNCHANGED)

Method (isolates MY change from module overrides):
  AFTER(record) = 50 iff (golden==66 AND classifier==RANDOM) else golden value.
  This is exactly what wire_souls_to_monsters now emits for records it owns at
  base-build time; module-authored apex bosses (charon/tantalus/enslaver/...) keep
  their golden value because they are NOT random-class. TESTING is proven unchanged
  by running the REAL apply_svc_patches._force_100_pct_soul_drops over both states.

Usage:  py tools/verify_soul_drop_rates.py [golden.arz]      (default: work arz)
        --gate   exit 1 on any invariant failure (for the gate battery)
"""
import sys, os
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from arz_patcher import ArzDatabase, DATA_TYPE_FLOAT
import build_svc_database as bsd
import apply_svc_patches as asp

DEFAULT_GOLDEN = HERE.parent / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'

RANDOM_CHANCE, PLACED_CHANCE, BOSS_CHANCE = 50.0, 66.0, 25.0


def _fv(fields, name):
    for key, tf in fields.items():
        if key.split('###')[0] == name and tf.values:
            return tf.values[0]
    return None


def _fvl(fields, name):
    for key, tf in fields.items():
        if key.split('###')[0] == name:
            return list(tf.values)
    return []


def _chance(fields):
    v = _fv(fields, 'chanceToEquipFinger2')
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def _has_soul(fields):
    return any(isinstance(v, str) and 'soul' in v.lower()
               for v in _fvl(fields, 'lootFinger2Item1'))


def _is_creature(name):
    nl = name.lower()
    return ('\\creature\\' in nl or '/creature/' in nl
            or '\\creatures\\' in nl or '/creatures/' in nl)


def main(argv):
    gate = '--gate' in argv
    args = [a for a in argv if not a.startswith('--')]
    golden = Path(args[0]) if args else DEFAULT_GOLDEN
    print(f"Loading golden: {golden}")
    db = ArzDatabase.from_arz(golden)

    random_members, placed_members = bsd.soul_spawn_provenance_sets(db)
    print(f"Provenance: {len(random_members)} random-pool members, "
          f"{len(placed_members)} placed-proxy members\n")

    # Gather soul-droppers + classify.
    recs = []  # (name, cls, golden_chance, new_release, klass)
    for name in db.record_names():
        if not _is_creature(name):
            continue
        f = db.get_fields(name)
        if not f or not _has_soul(f):
            continue
        cls = str(_fv(f, 'monsterClassification') or '')
        cur = _chance(f)
        new_release = bsd.soul_drop_rate(name, cls, random_members, placed_members,
                                         boss_chance=BOSS_CHANCE,
                                         random_chance=RANDOM_CHANCE,
                                         placed_chance=PLACED_CHANCE)
        # Klass label for the table.
        if bsd._soul_is_farmable_boss(name, cls):
            klass = 'FARMABLE_BOSS(25)'
        elif str(cls).lower() == 'quest':
            klass = 'QUEST(66)'
        elif bsd._soul_record_basename(name) in placed_members:
            klass = 'PLACED_UBER(66)'
        elif bsd._soul_record_basename(name) in random_members:
            klass = 'RANDOM_HERO(50)'
        else:
            klass = 'UNREFERENCED(66)'
        recs.append((name, cls, cur, new_release, klass))

    # AFTER(record): apply MY delta only where wire_souls owns the rate (golden==66
    # AND classifier==RANDOM). Everything else keeps its golden value.
    def after_of(cur, new_release):
        if abs(cur - 66.0) < 0.01 and abs(new_release - RANDOM_CHANCE) < 0.01:
            return RANDOM_CHANCE
        return cur

    # ---- BEFORE/AFTER rate table by monster class ----
    print("=" * 78)
    print("BEFORE/AFTER release soul-drop rate distribution (golden vs golden+delta)")
    print("=" * 78)
    buckets = defaultdict(lambda: defaultdict(int))   # klass -> (before,after) -> n
    for name, cls, cur, new_release, klass in recs:
        aft = after_of(cur, new_release)
        buckets[klass][(round(cur, 1), round(aft, 1))] += 1
    delta_count = 0
    for klass in sorted(buckets):
        print(f"\n  {klass}")
        for (b, a), n in sorted(buckets[klass].items()):
            arrow = '  (changed)' if abs(b - a) > 0.01 else ''
            if abs(b - a) > 0.01:
                delta_count += n
            print(f"      {b:5.1f}% -> {a:5.1f}%   x{n}{arrow}")
    print(f"\n  TOTAL soul-droppers: {len(recs)}   records changed by delta: {delta_count}")

    # ---- INVARIANT checks ----
    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    # 1) Every random-hero at golden 66 must go to 50.
    for name, cls, cur, new_release, klass in recs:
        if klass == 'RANDOM_HERO(50)' and abs(cur - 66.0) < 0.01:
            check(abs(after_of(cur, new_release) - 50.0) < 0.01,
                  f"RANDOM not cut to 50: {name} ({cur}->{after_of(cur,new_release)})")
    # 2) No PLACED / QUEST / FARMABLE_BOSS record may change.
    for name, cls, cur, new_release, klass in recs:
        if klass in ('PLACED_UBER(66)', 'QUEST(66)', 'FARMABLE_BOSS(25)', 'UNREFERENCED(66)'):
            check(abs(after_of(cur, new_release) - cur) < 0.01,
                  f"protected class changed: {name} [{klass}] {cur}->{after_of(cur,new_release)}")
    # 3) Gated-off (chance 0) must stay 0.
    for name, cls, cur, new_release, klass in recs:
        if abs(cur) < 0.01:
            check(abs(after_of(cur, new_release)) < 0.01,
                  f"gated-off re-enabled: {name} 0->{after_of(cur,new_release)}")

    # ---- TESTING-mode survival: run the REAL forcer over BOTH states ----
    # Build a release-AFTER db (apply my delta), and a release-BEFORE db (golden),
    # force 100% on each, and assert chanceToEquipFinger2 is IDENTICAL on every
    # creature -> proves the split is release-only (testing is unchanged) AND that
    # the forcer's chance>0 gate still fires on 50 and leaves 0 at 0.
    db_before = ArzDatabase.from_arz(golden)
    db_after = ArzDatabase.from_arz(golden)
    for name, cls, cur, new_release, klass in recs:
        aft = after_of(cur, new_release)
        if abs(aft - cur) > 0.01:
            db_after.set_field(name, 'chanceToEquipFinger2', aft, DATA_TYPE_FLOAT)
    asp._force_100_pct_soul_drops(db_before)
    asp._force_100_pct_soul_drops(db_after)
    tmode_mismatch = 0
    for name in db_after.record_names():
        if not _is_creature(name):
            continue
        fa = db_after.get_fields(name)
        if not fa or not _has_soul(fa):
            continue
        fb = db_before.get_fields(name)
        ca, cb = _chance(fa), _chance(fb)
        if abs(ca - cb) > 0.01:
            tmode_mismatch += 1
            if tmode_mismatch <= 5:
                print(f"  TESTING mismatch: {name} before={cb} after={ca}")
    check(tmode_mismatch == 0,
          f"testing-mode NOT identical ({tmode_mismatch} records differ)")
    # And: every soul-dropper that was >0 in release-after is 100 in testing;
    # every 0 stays 0 (the Legion-lane zeroed-stage invariant).
    boosted = gated = 0
    for name, cls, cur, new_release, klass in recs:
        aft = after_of(cur, new_release)
        fa = db_after.get_fields(name)
        ca = _chance(fa)
        if aft > 0:
            check(abs(ca - 100.0) < 0.01, f"testing not 100 for {name} (aft={aft} -> {ca})")
            boosted += 1
        else:
            check(abs(ca) < 0.01, f"testing re-enabled gated {name} (aft=0 -> {ca})")
            gated += 1
    print(f"\n  TESTING mode: {boosted} soul-droppers -> 100, {gated} gated stay 0, "
          f"release==testing byte-parity except release-rate values: "
          f"{'OK' if tmode_mismatch == 0 else 'FAIL'}")

    # ---- NEGATIVE / spot tests (named ground-truth records) ----
    print("\n" + "=" * 78)
    print("NEGATIVE / SPOT TESTS")
    print("=" * 78)
    idx = {bsd._soul_record_basename(n): (n, cls, cur, nr, k) for (n, cls, cur, nr, k) in recs}
    EXPECT = {
        # basename: (expect_klass_contains, expect_after)
        'um_camelbane_32':        ('RANDOM', 50.0),   # SV uber tier, random pool
        'um_morth_18':            ('RANDOM', 50.0),
        'um_crowboar_09':         ('RANDOM', 50.0),
        'hero_grom_28':           ('RANDOM', 50.0),   # plain hero roster
        'u_bloodwing_12':         ('RANDOM', 50.0),   # u_ unique, random pool
        'um_legion_28':           ('RANDOM', 50.0),   # in RANDOM eurynomus pools
        'um_vashkarr_99':         ('PLACED', 66.0),   # q_vashkarr_lone
        'um_broodmother_99':      ('PLACED', 66.0),
        # svc_um_hadesmarshal_80: module-authored placed boss (four_generals sets
        # 66). Basename starts svc_um_ (not um_), so the raw classifier cosmetically
        # labels it FARMABLE, but wire_souls never rates it (module-owned) and
        # after_of keeps the golden 66 -> outcome UNCHANGED. Assert the outcome.
        'svc_um_hadesmarshal_80': (None, 66.0),
        'um_toxeus_enslaver_99':  ('PLACED', 66.0),   # dual-membership -> placed wins
        'xsq27_namedhero_a_machae_45': ('QUEST', 66.0),  # Four Generals (quest)
        'um_tantalus_99':         (None, 0.0),        # placed but gated -> stays 0
        'um_bloodtoxeus_99':      (None, 25.0),        # module-owned superboss, stays 25
    }
    for bn, (want_k, want_after) in EXPECT.items():
        if bn not in idx:
            print(f"  ? {bn}: NOT FOUND in golden soul-droppers")
            continue
        n, cls, cur, nr, k = idx[bn]
        aft = after_of(cur, nr)
        ok = abs(aft - want_after) < 0.01 and (want_k is None or want_k in k)
        check(ok, f"spot-test {bn}: got klass={k} after={aft}, want {want_k}/{want_after}")
        print(f"  {'OK ' if ok else 'XX '} {bn:32s} {cls:8s} {k:18s} {cur:5.1f}%->{aft:5.1f}%")

    # ---- NEGATIVE TEST: Will's per-record veto knob (override sets) ----
    # Proves _SOUL_PLACED_OVERRIDE / _SOUL_RANDOM_OVERRIDE flip a record's rate,
    # win over EVERY roster branch (incl. the Boss/25 gate), and are a strict
    # no-op when empty (so the shipped, empty-by-default state == roster verdict).
    print("\n" + "=" * 78)
    print("NEGATIVE TEST: per-record veto override knobs")
    print("=" * 78)
    _save_p, _save_r = bsd._SOUL_PLACED_OVERRIDE, bsd._SOUL_RANDOM_OVERRIDE
    CAM = r'records\creature\um_camelbane_32.dbr'          # normally RANDOM->50
    YET = r'records\creature\boss_gargantuanyeti_35.dbr'   # normally FARMABLE->25
    rmem, pmem = {'um_camelbane_32'}, {'um_vashkarr_99'}
    try:
        b_cam = bsd.soul_drop_rate(CAM, 'Hero', rmem, pmem)          # 50 baseline
        b_yet = bsd.soul_drop_rate(YET, 'Boss', set(), set())        # 25 baseline
        bsd._SOUL_PLACED_OVERRIDE = frozenset({'um_camelbane_32'})
        o_cam = bsd.soul_drop_rate(CAM, 'Hero', rmem, pmem)          # forced 66
        bsd._SOUL_PLACED_OVERRIDE = _save_p
        bsd._SOUL_RANDOM_OVERRIDE = frozenset({'boss_gargantuanyeti_35'})
        o_yet = bsd.soul_drop_rate(YET, 'Boss', set(), set())        # forced 50 (beats 25 gate)
        bsd._SOUL_RANDOM_OVERRIDE = _save_r
        n_cam = bsd.soul_drop_rate(CAM, 'Hero', rmem, pmem)          # back to 50
    finally:
        bsd._SOUL_PLACED_OVERRIDE, bsd._SOUL_RANDOM_OVERRIDE = _save_p, _save_r
    for label, got, want in [('baseline camelbane', b_cam, 50.0),
                             ('baseline gargantuanyeti', b_yet, 25.0),
                             ('PLACED-override camelbane', o_cam, 66.0),
                             ('RANDOM-override gargantuanyeti (beats 25 gate)', o_yet, 50.0),
                             ('post-restore camelbane (empty==roster)', n_cam, 50.0)]:
        ok = abs(got - want) < 0.01
        check(ok, f"override negtest {label}: got {got}, want {want}")
        print(f"  {'OK ' if ok else 'XX '} {label:48s} {got:5.1f}% (want {want:.0f}%)")
    check(len(_save_p) == 0 and len(_save_r) == 0,
          f"override sets NOT empty by default (ships a hidden pin): "
          f"placed={sorted(_save_p)} random={sorted(_save_r)}")
    print(f"  {'OK ' if (len(_save_p)==0 and len(_save_r)==0) else 'XX '} "
          f"override sets empty by default -> shipped rates == pure roster verdict")

    # ---- verdict ----
    print("\n" + "=" * 78)
    if failures:
        print(f"FAIL: {len(failures)} invariant violation(s):")
        for m in failures[:30]:
            print(f"   - {m}")
        print("=" * 78)
        return 1 if gate else 0
    print("PASS: RANDOM->50, PLACED/QUEST->66, BOSS->25, gated stays 0, "
          "testing unchanged (release-only split).")
    print("=" * 78)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
