r"""build36 A1 NEGATIVE TEST for the three new pet gates (parity / gear / skill-kit).

Runs each gate against a KNOWN-BAD baseline arz (default: the e3810219 pre-build36
snapshot) and asserts it FAILS (raises SystemExit) - the "must flag bloodtoxeus /
toxeus_enslaver / enslaver_marauder (bare-fisted + Lyia-speed) and Pygmalion /
Aquardia / Dayria (buff-slot summon)" guarantee. Optionally also runs them against
a GOOD (build36) arz and asserts they now PASS.

usage: py tools/debug/negtest_pet_gates.py [<bad.arz>] [<good.arz>]
exit 0 = all three gates fired on the bad arz (and passed on the good arz if given).
exit 1 = a gate failed to fire on the bad arz, or still fails on the good arz.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase           # noqa: E402
import apply_svc_patches as A                  # noqa: E402

DEFAULT_BAD = (r'C:/Users/willi/repos/tqit_soulvizier_classic/local/db_backups'
               r'/pre_portal_rig_2026-07-10/SoulvizierClassic.arz.baseline_e3810219')

# The three known-bad _build_boss_summon families (source, [pets]) for parity+gear.
BAD_PAIRS = [
    (r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr',
     [r'records\skills\soulskills\pets\bloodtoxeus_%d.dbr' % i for i in (1, 2, 3)]),
    (r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr',
     [r'records\skills\soulskills\pets\toxeus_enslaver_%d.dbr' % i for i in (1, 2, 3)]),
    (r'records\creature\monster\shadowstalker\um_enslaver_marauder_99.dbr',
     [r'records\skills\soulskills\pets\enslaver_marauder_%d.dbr' % i for i in (1, 2, 3)]),
]


def _fires(fn, *args):
    try:
        fn(*args)
        return None                    # did NOT raise -> gate passed
    except SystemExit as e:
        return str(e)                  # raised -> gate fired


def run(arz, expect_fire):
    db = ArzDatabase.from_arz(Path(arz))
    fails = []
    for name, fn, args in (
        ('PET-STAT-MIRROR', A._verify_summon_pet_parity, (db, BAD_PAIRS)),
        ('PET-GEAR-PARITY', A._verify_summon_pet_gear, (db, BAD_PAIRS)),
        ('PET-SKILL-KIT', A._verify_summon_pet_skill_kit, (db,)),
    ):
        r = _fires(fn, *args)
        fired = r is not None
        verdict = 'FIRED' if fired else 'PASS'
        print(f"  {name}: {verdict}  {('-> ' + r[:140]) if fired else ''}")
        if fired != expect_fire:
            fails.append(name)
    return fails


if __name__ == '__main__':
    bad = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BAD
    print('=== NEGATIVE (all three gates MUST fire on the known-bad arz) ===')
    print('   ', bad)
    bad_fails = run(bad, expect_fire=True)
    good_fails = []
    if len(sys.argv) > 2:
        print('\n=== POSITIVE (all three gates MUST pass on the build36 arz) ===')
        print('   ', sys.argv[2])
        good_fails = run(sys.argv[2], expect_fire=False)
    if bad_fails:
        print('\nNEGTEST FAIL: gate(s) did not fire on the bad arz:', bad_fails)
        raise SystemExit(1)
    if good_fails:
        print('\nPOSTEST FAIL: gate(s) still fail on the good arz:', good_fails)
        raise SystemExit(1)
    print('\nNEGTEST OK: all three pet gates fire on the known-bad baseline'
          + (' and pass on the build36 arz.' if len(sys.argv) > 2 else '.'))
