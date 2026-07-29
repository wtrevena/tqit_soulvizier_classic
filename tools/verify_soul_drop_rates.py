"""
LAST-WRITER verification gate for the soul drop-rate split (Will 2026-07-14:
"Cut all soul drop rates for randomly spawning monsters to 50% from current 66%").

ROUND 2 REWRITE (vet NO-GO). Round 1's gate was a dry-run REPLAY over the
upstream golden arz that modeled ONLY wire_souls_to_monsters' own delta:
  AFTER(record) = 50 iff (golden==66 AND classifier==RANDOM) else golden.
That model is a FALSE GREEN: it cannot see what any OTHER writer that runs
later in the real build does to the same field. It missed that
create_uber_souls.py (called AFTER wire_souls_to_monsters, before every
apply_svc_patches module) creates brand-new souls for uber/hero monsters that
had none at wire-time and used to hardcode chanceToEquipFinger2=66.0
unconditionally - silently re-widening 21 of the 377 intended cuts. A replay
of one function's logic can never catch a DIFFERENT function clobbering its
output afterward.

This gate instead loads a REAL BUILT arz (one that ran the full pipeline:
wire_souls_to_monsters -> create_uber_souls -> apply_all_extended_patches ->
patches-registry) and checks the FINAL, ACTUAL chanceToEquipFinger2 value on
every soul-dropping creature - whichever writer ran LAST determined that
value - against what the shared classifier (build_svc_database.soul_drop_rate
+ soul_spawn_provenance_sets, the single source of truth) says it SHOULD be.
Any writer, present or future, anywhere in the pipeline, that sets the wrong
rate is caught here because the check is against the OUTPUT, not a model of
one function's delta. See _require_real_build() below for the fail-loud guard
that refuses to run this gate over a bare upstream/golden arz that never went
through the real pipeline (which would silently pass vacuously).

Usage:  py tools/verify_soul_drop_rates.py [built.arz]   (default: work arz)
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

DEFAULT_ARZ = HERE.parent / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'

RANDOM_CHANCE, PLACED_CHANCE, BOSS_CHANCE = 50.0, 66.0, 25.0

# create_uber_souls.py's exclusive output directory - only present in a REAL
# build (it is created by the build pipeline, never shipped in any upstream
# source arz). Used as the fail-loud "this is not a real build" guard.
_REAL_BUILD_MARKER_DIR = r'records\item\equipmentring\soul\svc_uber'


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


def _require_real_build(db):
    """Fail loud if `db` is not a REAL BUILT arz (i.e. never ran the full
    pipeline). A bare upstream/golden arz that skipped create_uber_souls +
    apply_all_extended_patches would make every check below vacuously pass
    (nothing to compare against post-wire writers) - exactly the false-green
    failure mode this rewrite exists to close. Checks for create_uber_souls'
    exclusive output directory, which only exists after a real build ran."""
    marker = _REAL_BUILD_MARKER_DIR.lower().replace('/', '\\')
    for name in db.record_names():
        if marker in name.lower().replace('/', '\\'):
            return
    raise SystemExit(
        "verify_soul_drop_rates: this arz has NO records under "
        f"{_REAL_BUILD_MARKER_DIR!r} (create_uber_souls.py's exclusive output "
        "dir) - it is NOT a real built arz (the full pipeline never ran over "
        "it). This gate checks LAST-WRITER semantics against the real build "
        "output; a bare upstream/golden arz would pass vacuously (a false "
        "green - exactly what caused the round-1 NO-GO). Build the real arz "
        "first (py tools/build_svc_database.py ...) and point this gate at "
        "it.")


def _gather(db):
    """Collect (name, cls, cur, expected, klass) for every soul-dropping
    creature in `db`. `cur` is the ACTUAL value stored in this arz (whichever
    writer ran last); `expected` is what soul_drop_rate() says it should be
    IF the drop is enabled at all (cur>0) - it has no opinion on gating."""
    random_members, placed_members = bsd.soul_spawn_provenance_sets(db)
    recs = []
    for name in db.record_names():
        if not _is_creature(name):
            continue
        f = db.get_fields(name)
        if not f or not _has_soul(f):
            continue
        cls = str(_fv(f, 'monsterClassification') or '')
        cur = _chance(f)
        expected = bsd.soul_drop_rate(name, cls, random_members, placed_members,
                                      boss_chance=BOSS_CHANCE,
                                      random_chance=RANDOM_CHANCE,
                                      placed_chance=PLACED_CHANCE)
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
        recs.append((name, cls, cur, expected, klass))
    return recs, random_members, placed_members


# ── DOCUMENTED, PRE-EXISTING EXCEPTIONS (waived, never silently dropped) ────
# These predate Will's 66->50 split entirely (docs/reports/b59_drop_rate_50.md
# section 6 + the original round-1 spot-test table already single these out)
# and are OUT OF SCOPE for this directive: the naive roster/path classifier
# cannot see a deliberate per-boss design choice made by a DIFFERENT feature,
# so it mislabels them - but the actual shipped value is the INTENDED one,
# not a regression from this change. basename -> (expected ACTUAL arz value,
# rationale). A waived record still prints (visible, tracked) and is never
# silently absorbed into a passing count; it only stops counting as a FAIL.
_KNOWN_EXCEPTIONS = {
    # legion_soul_stages (build41 lane, vetted GO): non-terminal death-transform
    # stages zeroed so Legion drops ONE soul from the terminal form only.
    'um_legion_28': (0.0, 'legion_soul_stages zeroed non-terminal stage (66->0 intended)'),
    'um_legion_28a': (0.0, 'legion_soul_stages zeroed non-terminal stage (66->0 intended)'),
    'um_legion_28b': (0.0, 'legion_soul_stages zeroed non-terminal stage (66->0 intended)'),

    # Pharaoh's Honor Guard: hand-tuned 2.25%->10% (a THIRD tier outside the
    # 25/50/66 model, predates 2026-07-14).
    **{f'boss_pharaohshonorguard{n}_{lv}': (10.0,
        "hand-tuned Pharaoh's Honor Guard rate (10%), not part of the 25/50/66 model")
       for n in (1, 2, 3, 4) for lv in (25, 28, 31)},
    # Module-authored placed/superboss records the naive path/basename
    # heuristic cosmetically mislabels (b59 report section 6 + the original
    # spot-test table already document these; the shipped value IS intended).
    'svc_um_hadesmarshal_80': (66.0,
        'module-authored placed boss (four_generals); basename svc_um_ not '
        'recognized by the naive classifier, module keeps its own 66'),
    # R-48 (Will 2026-07-27, b90): "increase the drop rate for the souls of
    # toxeus the murderer, enslaver of souls and toxeus the murderer, devourer
    # of blood to 100%". These two FOUGHT champions are carved out of the
    # RANDOM-50 / PLACED-66 / BOSS-25 split (R-42) BY NAME; the classifier is
    # untouched, so it still says 25 (Devourer) / 66 (Enslaver) and both are
    # waived here. Owned by tools/patches/toxeus_souls_100.py, whose verify()
    # re-asserts 100 on the final merged arz.
    'um_bloodtoxeus_99': (100.0,
        'R-48 (Will 2026-07-27): Toxeus the Murderer, Devourer of Blood drops '
        'his soul 100% of the time (was the module-owned superboss cap of 25); '
        'patches/toxeus_souls_100.py owns it'),
    'um_toxeus_enslaver_99': (100.0,
        'R-48 (Will 2026-07-27): Toxeus the Murderer, Enslaver of Souls drops '
        'his soul 100% of the time (was the PLACED_UBER 66); '
        'patches/toxeus_souls_100.py owns it'),
    # R-81 (Will 2026-07-28, b98): the THIRD fought Toxeus champion joins R-48.
    # This supersedes the old "deliberately capped at 25, a farmable-style
    # superboss" waiver and closes BL-b90-DEBT-4, which had named Will as the
    # owner/trigger of exactly this decision. Same owner module, same mechanism.
    'um_toxeus_hunt_99': (100.0,
        'R-81 (Will 2026-07-28): Toxeus the Murderer, the Endless Hunt drops '
        'his soul 100% of the time (was the R-42 Boss rate of 25 - the SOLE '
        'reason the soul appeared not to drop); patches/toxeus_souls_100.py owns it'),
    # b98: the Legendary-only ENDLESS PURSUIT variant (R-80) is a build-time
    # clone of um_toxeus_hunt_99 generated by patches/toxeus_hunt_endless.py
    # AFTER toxeus_souls_100 runs, so it inherits the 100 end-state by
    # construction. It is the same champion with one field changed (controller),
    # so it carries the same waiver for the same reason; toxeus_hunt_endless's
    # own verify() proves base and variant differ in EXACTLY that one field, so
    # this entry can never drift away from the base record's rate.
    'um_toxeus_hunt_l_99': (100.0,
        'R-80/R-81 (Will 2026-07-28): the Legendary endless-pursuit variant of '
        'the Endless Hunt - a clone of um_toxeus_hunt_99 differing ONLY in '
        'controller; patches/toxeus_hunt_endless.py owns it'),
    # Pre-existing "module-set Boss@66" divergences from the naive boss_-path
    # farmable heuristic (b59 report ground-truth table: "FARMABLE_BOSS(25) |
    # 66.0 -> 66.0 | 5 | unchanged"); predates and is orthogonal to the
    # RANDOM/PLACED split this gate exists to police.
    'boss_satyrshaman_55': (66.0,
        'pre-existing module-set Boss@66 (b59 report ground-truth table), '
        'orthogonal to the RANDOM/PLACED split'),
    'boss_charon_41': (66.0,
        'pre-existing module-set Boss@66 (Charon Form1/3), orthogonal to '
        'the RANDOM/PLACED split'),
    'boss_charon_43': (66.0,
        'pre-existing module-set Boss@66 (Charon Form1/3), orthogonal to '
        'the RANDOM/PLACED split'),
    'boss_charon_39': (66.0,
        'pre-existing module-set Boss@66 (Charon Form1 donor; round-2 vet '
        'NO-GO fix re-asserts 66 alongside 41/43 - create_uber_souls mints '
        'this record\'s own soul via an unpinned soul_drop_rate() call, so '
        'the naive "\\boss_" path heuristic would otherwise misclassify this '
        'PLACED Golden Bough encounter as a farmable Act boss and cut it to '
        '25, desyncing it from 41/43), orthogonal to the RANDOM/PLACED split'),

    # ── b97 SOUL-IDENTITY (Will 2026-07-27): "some of the heroes are dropping
    # the wrong souls or souls for other boss monsters". Each record below was
    # dropping a soul whose NAMED OWNER is a different creature that also drops
    # it, so tools/patches/soul_identity.py detached the roll
    # (chanceToEquipFinger2 -> 0; lootFinger2Item1 left intact). The RANDOM/
    # PLACED/BOSS classifier is deliberately NOT modified - it still says
    # 50/25 for these - so all 18 are waived here BY NAME, exactly like the
    # legion_soul_stages non-terminal zeroes above.
    #
    # ROUND 2 added 4 more identity thieves (01_akara + the soul\test\
    # us_lysiaspellbreaker_15 trio). They need NO waiver here: THIS gate is
    # itself scoped by its own _is_creature() to paths containing
    # \creature(s)\, and all four sit outside it (records\drxcreatures\ and
    # records\item\equipmentring\soul\test\). Registered as BL-b97-DEBT-7 -
    # widening this gate's roster is a separate wave because it would pull
    # every drxcreatures boss into the RANDOM/PLACED/BOSS classifier.
    # Every soul involved is
    # still dropped by its rightful owner (soul_identity's ORPHAN GUARD proves
    # it every build). Full table: docs/reports/b97_soul_identity_audit.md.
    **{bn: (0.0,
            f'b97 soul-identity: {who} was dropping the {soul} soul, which '
            f'belongs to {owner}; patches/soul_identity.py detached the roll '
            f'(loot ref kept)')
       for bn, who, soul, owner in (
           ('hero_wheedletongue_41', 'Fesil the Quick', 'Wheedletongue',
            'Wheedletongue the Magnificent'),
           ('hero_wheedletongue_43', 'Sinnet Patchfur', 'Wheedletongue',
            'Wheedletongue the Magnificent'),
           ('um_inkeyes_45', 'Blood-Eyes', 'Wheedletongue',
            'Wheedletongue the Magnificent'),
           ('um_inkeyes2_45', 'Blood-Eyes', 'Wheedletongue',
            'Wheedletongue the Magnificent'),
           ('hero_kaaltspeartail_30', 'Errak Bonecarver', 'Kaalt Speartail',
            'Kaalt Speartail'),
           ('hero_kaaltspeartail_33', 'Sartt Soulrender', 'Kaalt Speartail',
            'Kaalt Speartail'),
           ('hero_grom_31', 'Korat Bearkin', 'Grom', 'Grom'),
           ('hero_adarathelovely_43', 'Raghd Bloatworm', 'Adara the Lovely',
            'Adara the Lovely'),
           ("hero_princech'kik't_37", "Prince Ch'kik't the Horrible",
            "Z'kar Flamespinner", "Z'kar Flamespinner"),
           ('um_wahr_33', "Wahr'Ner Shadowpaw", "Nephi'tek", "Nephi'tek the Lasher"),
           ('us_nazur_34', 'Nazur the Shrouded', "Nephi'tek", "Nephi'tek the Lasher"),
           ('ur_masai_43', 'Masai-yin the Grovekeeper', 'Syrinx',
            'Syrinx of the Tainted Meadow'),
           ('ur_uber_45', 'Xuannu the Twilight Matron', 'Syrinx',
            'Syrinx of the Tainted Meadow'),
           ('um_morbi_17', 'Morbi', 'Venemurax', 'Venemurax'),
           ('us_mormo_16', 'Mormo', 'Storm Crow', 'Storm Crow'),
           ('us_frostscarab_35', 'Daechalcos', 'Scarabaeus',
            'Scarabaeus the Desert King'),
           ('us_poisonsiren_14', 'Thelxiepeia Venomlip', 'Aquardia the Coral Queen',
            'Aquardia, the Coral Queen'),
           ('um_rocksting_29', 'Colossal Scorpion', 'Rocksting', 'Rock Sting'),
       )},
}


# ── GOLDEN pre-drop-50 build (build40, md5 b33c5a44), used ONLY by the
# intended-diff hardening check below. This is a big local build artifact
# (gitignored, like every other .arz) - the check degrades to a printed
# SKIP (not a failure) when it is not present on the machine running the
# gate, so the gate battery still runs standalone/CI-clean elsewhere.
_GOLDEN_MD5 = 'b33c5a447f3a8ca652c14f78d4ad1dd4'
_GOLDEN_CANDIDATES = [HERE.parent / 'local' / 'baseline_build40.arz']


def _find_golden():
    for p in _GOLDEN_CANDIDATES:
        if p.exists():
            return p
    return None


def _check_intended_diff_vs_golden(recs, golden_path):
    """HARDENING for the MEDIUM gate-blindness finding (vet round 2 on
    feat/soul-drop-50): _check_last_writer() above uses soul_drop_rate()
    itself as its own oracle, so it is structurally BLIND to a value the
    classifier produces that is nonetheless an unintended regression against
    the shipped baseline - e.g. boss_charon_39 66->25: the naive "\\boss_"
    path heuristic says farmable-boss/25, the arz also has 25, so no
    LAST-WRITER mismatch is ever raised, even though the golden (and the
    design) says this PLACED encounter should stay 66. That bug shipped once
    already (the round-1 create_uber_souls.py NO-GO) and was only caught by a
    human diffing the build against golden by hand - this makes that diff a
    permanent, mechanical part of the gate.

    Diffs the REAL built arz's chanceToEquipFinger2 directly against the
    pre-drop-50 golden build40 arz (which already ran the full pipeline, so
    it is a fair record-for-record comparison). Every delta must be EITHER
    the intended 66->50 RANDOM_HERO cut, OR a documented _KNOWN_EXCEPTIONS
    divergence (the same waiver list _check_last_writer uses) - anything
    else is an unintended, silent regression and fails loud."""
    if golden_path is None:
        print("\n  (intended-diff-vs-golden check SKIPPED: no local golden arz "
              f"found - looked for {[str(p) for p in _GOLDEN_CANDIDATES]})")
        return []
    golden_db = ArzDatabase.from_arz(golden_path)
    golden_recs, _, _ = _gather(golden_db)
    golden_chance = {name: cur for name, cls, cur, exp, k in golden_recs}
    cur_chance = {name: cur for name, cls, cur, exp, k in recs}
    cur_klass = {name: k for name, cls, cur, exp, k in recs}

    fails = []
    diffs = 0
    for name, gcur in golden_chance.items():
        ccur = cur_chance.get(name)
        if ccur is None or abs(gcur - ccur) < 0.01:
            continue
        diffs += 1
        is_intended_cut = (abs(gcur - 66.0) < 0.01 and abs(ccur - 50.0) < 0.01
                           and cur_klass.get(name) == 'RANDOM_HERO(50)')
        bn = bsd._soul_record_basename(name)
        exc = _KNOWN_EXCEPTIONS.get(bn)
        is_documented = exc is not None and abs(ccur - exc[0]) < 0.01
        if is_intended_cut or is_documented:
            continue
        fails.append(
            f"UNINTENDED golden-diff: {name} golden(build40)={gcur}% -> "
            f"built={ccur}% - not the intended 66->50 RANDOM cut and not a "
            f"documented _KNOWN_EXCEPTIONS waiver: a silent regression "
            f"against the pre-drop-50 baseline")
    print(f"\n  Intended-diff-vs-golden ({golden_path.name}, md5 expected "
          f"{_GOLDEN_MD5}): {diffs} chanceToEquipFinger2 deltas vs golden, "
          f"{diffs - len(fails)} intended/documented, {len(fails)} UNINTENDED")
    return fails


def _check_last_writer(recs):
    """THE gate: for every ENABLED (cur>0) soul-dropper, the value actually
    present in the arz must equal the shared classifier's verdict. Gated-off
    (cur==0) records are a different axis (drop enabled at all, not the rate)
    and are only checked to confirm they stayed 0. A mismatch matching a
    _KNOWN_EXCEPTIONS entry EXACTLY (both the actual value AND the rationale
    basename) is reported as waived, not a failure - anything else, including
    a KNOWN basename now sitting at a DIFFERENT value than its documented
    exception, still fails loud. Returns (failures, waived) - failures empty
    == PASS."""
    failures = []
    waived = []
    for name, cls, cur, expected, klass in recs:
        if abs(cur) < 0.01:
            continue  # gated off - not this gate's concern (rate is moot)
        if abs(cur - expected) <= 0.01:
            continue
        bn = bsd._soul_record_basename(name)
        exc = _KNOWN_EXCEPTIONS.get(bn)
        if exc is not None and abs(cur - exc[0]) < 0.01:
            waived.append(f"WAIVED (documented exception): {name} [{klass}] "
                          f"arz={cur}% (naive classifier says {expected}%) - {exc[1]}")
            continue
        failures.append(
            f"LAST-WRITER mismatch: {name} [{klass}, cls={cls or '(none)'}] "
            f"arz has {cur}% but soul_drop_rate() says {expected}% - some "
            f"writer after wire_souls_to_monsters set the wrong rate")
    return failures, waived


def main(argv):
    gate = '--gate' in argv
    args = [a for a in argv if not a.startswith('--')]
    arz_path = Path(args[0]) if args else DEFAULT_ARZ
    print(f"Loading built arz: {arz_path}")
    db = ArzDatabase.from_arz(arz_path)
    _require_real_build(db)

    recs, random_members, placed_members = _gather(db)
    print(f"Provenance: {len(random_members)} random-pool members, "
          f"{len(placed_members)} placed-proxy members\n")

    # ---- rate distribution table by monster class (LAST-WRITER, real values) ----
    print("=" * 78)
    print("Soul-drop rate distribution (ACTUAL value currently in the built arz)")
    print("=" * 78)
    buckets = defaultdict(lambda: defaultdict(int))   # klass -> (cur,expected) -> n
    for name, cls, cur, expected, klass in recs:
        buckets[klass][(round(cur, 1), round(expected, 1))] += 1
    mismatch_count = 0
    for klass in sorted(buckets):
        print(f"\n  {klass}")
        for (cur, expected), n in sorted(buckets[klass].items()):
            gated = abs(cur) < 0.01
            bad = (not gated) and abs(cur - expected) > 0.01
            if bad:
                mismatch_count += n
            tag = '  (gated, OK)' if gated else ('  <<< MISMATCH' if bad else '  (OK)')
            print(f"      arz={cur:5.1f}%  expected={expected:5.1f}%   x{n}{tag}")
    print(f"\n  TOTAL soul-droppers: {len(recs)}   LAST-WRITER mismatches: {mismatch_count}")

    random_enabled_50 = sum(1 for n, c, cur, e, k in recs
                            if k == 'RANDOM_HERO(50)' and abs(cur - 50.0) < 0.01)
    print(f"  RANDOM_HERO records actually shipping at 50%: {random_enabled_50}")

    # ---- INVARIANT: LAST-WRITER check on the real arz ----
    failures, waived = _check_last_writer(recs)

    # ---- INVARIANT (MEDIUM hardening, vet round 2): intended-only diff vs golden ----
    print("\n" + "=" * 78)
    print("INTENDED-DIFF-VS-GOLDEN (hardens the LAST-WRITER check's blind spot)")
    print("=" * 78)
    failures.extend(_check_intended_diff_vs_golden(recs, _find_golden()))

    if waived:
        print("\n" + "=" * 78)
        print(f"WAIVED (documented pre-existing exceptions, not this directive's scope): {len(waived)}")
        print("=" * 78)
        for w in waived:
            print(f"  {w}")

    # ---- TESTING-mode survival: run the REAL forcer over this real arz ----
    # Proves the release/testing knobs are independent: forcing TESTING must
    # boost every ENABLED soul-dropper to 100 and leave every gated (0) one at
    # 0, regardless of which release rate (25/50/66) it is currently sitting
    # at. This is a property of _force_100_pct_soul_drops' own gate
    # (chance>0), not tied to any specific release value, so it is checked
    # directly on the real arz (no golden/synthetic "before" state needed).
    db_testing = ArzDatabase.from_arz(arz_path)
    asp._force_100_pct_soul_drops(db_testing)
    boosted = gated = tmode_bad = 0
    for name, cls, cur, expected, klass in recs:
        ft = db_testing.get_fields(name)
        ct = _chance(ft) if ft else 0.0
        if cur > 0:
            boosted += 1
            if abs(ct - 100.0) > 0.01:
                tmode_bad += 1
                failures.append(f"testing forcer did not boost {name} to 100 "
                                f"(release={cur}, testing={ct})")
        else:
            gated += 1
            if abs(ct) > 0.01:
                tmode_bad += 1
                failures.append(f"testing forcer re-enabled gated {name} "
                                f"(release=0, testing={ct})")
    print(f"\n  TESTING mode (real forcer over the real arz): {boosted} enabled "
          f"soul-droppers -> 100, {gated} gated stay 0: "
          f"{'OK' if tmode_bad == 0 else 'FAIL'}")

    # ---- NEGATIVE / spot tests (named ground-truth records) ----
    print("\n" + "=" * 78)
    print("NEGATIVE / SPOT TESTS")
    print("=" * 78)
    idx = {bsd._soul_record_basename(n): (n, cls, cur, exp, k) for (n, cls, cur, exp, k) in recs}
    EXPECT = {
        # basename: (expect_klass_contains or None, expect_actual_arz_value)
        'um_camelbane_32':        ('RANDOM', 50.0),   # SV uber tier, random pool
        'um_morth_18':            ('RANDOM', 50.0),
        'um_crowboar_09':         ('RANDOM', 50.0),   # <- one of the 21 NO-GO records
        'um_xix_36':              ('RANDOM', 50.0),   # <- NO-GO record (create_uber_souls)
        'um_frost_32':            ('RANDOM', 50.0),   # <- NO-GO record (create_uber_souls)
        'hero_junshan_39':        ('RANDOM', 50.0),   # <- NO-GO record (create_uber_souls)
        'hero_grom_28':           ('RANDOM', 50.0),   # plain hero roster
        'u_bloodwing_12':         ('RANDOM', 50.0),   # u_ unique, random pool
        'um_legion_28':           (None, 0.0),        # legion_soul_stages: non-terminal, zeroed (one soul/encounter)
        # R-42 FOLD-IN (b91): the Legion TERMINAL now INHERITS its chain head's
        # RANDOM provenance through the actorToSpawnOnDeath closure in
        # build_svc_database.soul_spawn_provenance_sets, so it classifies RANDOM
        # and ships 50 - closing Will's queued "death-transform terminals of
        # RANDOM chains inherit the 50 rate". Was (None, 66.0) + an open Will Q.
        'um_legion_28c':          ('RANDOM', 50.0),
        # Same fold-in, the only other LIVE mover roster-wide: the Possessed
        # Boar's death-transform spirit (head um_possessedboar IS a random-pool
        # member; double_soul_rulings deliberately leaves this terminal as the
        # surviving dropper, so its rate must follow its chain).
        'um_possessedboar_spirit': ('RANDOM', 50.0),
        # NEGATIVE half of the same fold-in: terminals of PLACED chains must NOT
        # move (placed_proxy_members is checked before random_pool_members, so a
        # placed head's stages stay 66 - the "never over-cut a placed encounter"
        # invariant). These three are now RIGHT for the right reason instead of
        # falling through the classifier's unreferenced-default.
        'um_charonform2_ferryman_99': ('PLACED', 66.0),
        'um_polisgaoler_unbound_99':  ('PLACED', 66.0),
        'um_tantalus_unbound_99':     ('PLACED', 66.0),
        'um_vashkarr_99':         ('PLACED', 66.0),   # q_vashkarr_lone
        'um_broodmother_99':      ('PLACED', 66.0),
        # svc_um_hadesmarshal_80: module-authored placed boss (four_generals sets
        # 66). Basename starts svc_um_ (not um_), so the raw classifier cosmetically
        # labels it FARMABLE, but wire_souls never rates it (module-owned) and the
        # module keeps it at its own 66 -> outcome UNCHANGED. Assert the outcome.
        'svc_um_hadesmarshal_80': (None, 66.0),
        # R-48 (Will 2026-07-27): both fought Toxeus champions ship at 100%.
        # klass still reads PLACED (the classifier is deliberately untouched);
        # the ACTUAL arz value is the carve-out.
        'um_toxeus_enslaver_99':  ('PLACED', 100.0),
        'xsq27_namedhero_a_machae_45': ('QUEST', 66.0),  # Four Generals (quest)
        'um_tantalus_99':         (None, 0.0),        # placed but gated -> stays 0
        'um_bloodtoxeus_99':      (None, 100.0),       # R-48: 25 -> 100 (Will 2026-07-27)
    }
    for bn, (want_k, want_actual) in EXPECT.items():
        if bn not in idx:
            print(f"  ? {bn}: NOT FOUND in this arz's soul-droppers")
            continue
        n, cls, cur, exp, k = idx[bn]
        ok = abs(cur - want_actual) < 0.01 and (want_k is None or want_k in k)
        if not ok:
            failures.append(f"spot-test {bn}: arz has klass={k} value={cur}, "
                            f"want {want_k}/{want_actual}")
        print(f"  {'OK ' if ok else 'XX '} {bn:32s} {cls:8s} {k:18s} arz={cur:5.1f}%  (want {want_actual:.0f}%)")

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
        if not ok:
            failures.append(f"override negtest {label}: got {got}, want {want}")
        print(f"  {'OK ' if ok else 'XX '} {label:48s} {got:5.1f}% (want {want:.0f}%)")
    if not (len(_save_p) == 0 and len(_save_r) == 0):
        failures.append(f"override sets NOT empty by default (ships a hidden pin): "
                        f"placed={sorted(_save_p)} random={sorted(_save_r)}")
    print(f"  {'OK ' if (len(_save_p)==0 and len(_save_r)==0) else 'XX '} "
          f"override sets empty by default -> shipped rates == pure roster verdict")

    # ---- NEGATIVE TEST: the R-42 death-transform provenance closure ----
    # Proves (a) the closure is what makes the Legion terminal RANDOM/50, and
    # (b) it only ever propagates FORWARD, so a PLACED chain's terminal cannot
    # be cut to 50. Planted regression: run the classifier with the closure
    # DISABLED (empty edge map) and assert the terminal falls back to 66 - i.e.
    # if someone deletes _propagate_transform_provenance, this test goes red.
    print("\n" + "=" * 78)
    print("NEGATIVE TEST: R-42 death-transform provenance closure")
    print("=" * 78)
    LEG_HEAD, LEG_TERM = 'um_legion_28', 'um_legion_28c'
    PLACED_HEAD, PLACED_TERM = 'um_tantalus_99', 'um_tantalus_unbound_99'
    edges = {LEG_HEAD: {'um_legion_28a'}, 'um_legion_28a': {'um_legion_28b'},
             'um_legion_28b': {LEG_TERM}, PLACED_HEAD: {PLACED_TERM}}
    r_seed, p_seed = {LEG_HEAD}, {PLACED_HEAD}
    r_closed = bsd._propagate_transform_provenance(r_seed, edges)
    p_closed = bsd._propagate_transform_provenance(p_seed, edges)
    r_off = bsd._propagate_transform_provenance(r_seed, {})   # planted regression
    p_off = bsd._propagate_transform_provenance(p_seed, {})
    term_path = r'records\creature\monster\eurynomus\um_legion_28c.dbr'
    placed_path = r'records\xpack\creatures\monster\lostsoul\um_tantalus_unbound_99.dbr'
    cases = [
        ('closure ON  : legion terminal -> RANDOM 50',
         bsd.soul_drop_rate(term_path, 'Hero', r_closed, p_closed), 50.0),
        ('closure OFF : legion terminal falls back to 66 (planted regression)',
         bsd.soul_drop_rate(term_path, 'Hero', r_off, p_off), 66.0),
        ('closure ON  : PLACED chain terminal STAYS 66 (never over-cut)',
         bsd.soul_drop_rate(placed_path, 'Boss', r_closed, p_closed), 66.0),
        ('no backward flow: head stays out of the terminal-seeded closure',
         0.0 if LEG_HEAD in bsd._propagate_transform_provenance({LEG_TERM}, edges)
         else 1.0, 1.0),
        ('cycle safety: a self-loop terminates',
         float(len(bsd._propagate_transform_provenance({'a'}, {'a': {'b'},
                                                              'b': {'a'}}))), 2.0),
    ]
    for label, got, want in cases:
        ok = abs(got - want) < 0.01
        if not ok:
            failures.append(f"transform-closure negtest {label}: got {got}, want {want}")
        print(f"  {'OK ' if ok else 'XX '} {label:62s} {got:6.1f} (want {want:.0f})")

    # ---- NEGATIVE TEST: plant a post-wire writer stomp, confirm the gate CATCHES it ----
    # This is the regression this whole rewrite exists to guarantee against:
    # round 1's replay-based gate could not see a downstream writer clobbering
    # a correctly-classified record. Simulate exactly that class of bug on a
    # FRESH copy of the real arz (never touches the db used above) and prove
    # _check_last_writer() now reports a failure for the planted record.
    print("\n" + "=" * 78)
    print("NEGATIVE TEST: planted post-wire writer (simulates the round-1 NO-GO)")
    print("=" * 78)
    planted_target = next((n for n, c, cur, e, k in recs
                           if k == 'RANDOM_HERO(50)' and abs(cur - 50.0) < 0.01), None)
    if planted_target is None:
        failures.append("negtest setup: no RANDOM_HERO@50 record found in this "
                        "arz to plant the stomp on - cannot prove the gate catches "
                        "the round-1 regression class")
        print("  ? no RANDOM_HERO@50 record available - negtest SKIPPED")
    else:
        db_stomped = ArzDatabase.from_arz(arz_path)
        db_stomped.set_field(planted_target, 'chanceToEquipFinger2', 66.0, DATA_TYPE_FLOAT)
        stomped_recs, _, _ = _gather(db_stomped)
        stomp_failures, _stomp_waived = _check_last_writer(stomped_recs)
        caught = any(planted_target in f for f in stomp_failures)
        if not caught:
            failures.append(
                f"NEGATIVE TEST FAILED: planted a post-wire 66% stomp on "
                f"{planted_target} (a RANDOM_HERO@50 record) and the gate did "
                f"NOT flag it - the gate cannot catch the round-1 regression class")
        print(f"  {'OK ' if caught else 'XX '} planted {planted_target} 50->66: "
              f"gate {'CAUGHT it' if caught else 'MISSED it'} "
              f"({len(stomp_failures)} failure(s) on the stomped copy)")

    # ---- verdict ----
    print("\n" + "=" * 78)
    if failures:
        print(f"FAIL: {len(failures)} invariant violation(s):")
        for m in failures[:30]:
            print(f"   - {m}")
        print("=" * 78)
        return 1 if gate else 0
    print("PASS: every enabled soul-dropper's ACTUAL rate in the real arz matches "
          "the shared classifier (RANDOM->50, PLACED/QUEST->66, BOSS->25), gated "
          "stays 0, testing-mode forcer unchanged, and the gate proves it can "
          "catch a planted post-wire stomp (the round-1 regression class).")
    print("=" * 78)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
