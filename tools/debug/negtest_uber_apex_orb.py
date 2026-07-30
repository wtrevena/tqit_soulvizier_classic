#!/usr/bin/env python3
r"""Planted negative + positive tests for the apex-orb gate
(tools/patches/uber_apex_orb.py :: verify).

A gate that never fires is worthless (the contract-suite discipline). This proves
the orb-calibre + roster gate actually catches every failure mode it claims to
guard.

⚠️ R-99 RE-AUTHORING NOTE (2026-07-29). The b94 version of this harness asserted
"a THIRD record on genericbossorb_05 must FAIL", i.e. it encoded a COUNT of two
champions. R-99 put every Toxeus variant on the apex orb, so a count is now the
WRONG invariant and would red the build the moment the ruling landed. The
invariant it was protecting - no scope creep onto the apex tier - is still real
and is NOT weakened here: it is restated as a SET equality (the orb05 carriers
are exactly the derived Toxeus roster), tested in BOTH directions:
  * NEGATIVE 2 still plants a NON-Toxeus record on orb05 and still requires FAIL;
  * NEGATIVES 15..N plant the opposite failure - one per roster record, each
    losing its orb - and require FAIL for every single one.

POSITIVE 1: the real built .arz must PASS.
NEGATIVE 1: a champion put back on genericbossorb_04 must FAIL (the whole point).
NEGATIVE 2: a NON-Toxeus record pointed at genericbossorb_05 must FAIL (scope
            creep onto the apex tier - R-99's opening reassurance).
NEGATIVE 3: an orb05 loot table whose numSpawn multiplier is cut below Leinth's
            must FAIL (calibre regression).
NEGATIVE 4: an orb05 loot4Chance dropped back to the orb04 value must FAIL.
NEGATIVE 5: a unique-entry weight lowered below Leinth's must FAIL.
NEGATIVE 6: a broken orb05 chain link (pool -> chest) must FAIL.
NEGATIVE 7: R-48 collateral damage (a champion's soul rate cut) must FAIL.
NEGATIVE 8: an orb04 consumer chest retargeted (donor-chain tamper) must FAIL.

The Will-2026-07-27 half (Leinth is INCLUDED, upgraded, never nerfed):
NEGATIVE 9 : a Leinth chest reverted to her old mid-tier loot table must FAIL
             (she would be left behind on the Act-3 band).
NEGATIVE 10: a Leinth chest reverted to the Act-3 down-scaling level equation
             must FAIL (her items would stay down-tiered on normal/epic).
NEGATIVE 11: a Leinth chest whose bespoke mesh was clobbered must FAIL
             (the re-tier must never cost her identity).
NEGATIVE 12: a Leinth chest switched to the champions' POORER bossgoldgenerator
             must FAIL (that is a gold nerf: x24/x32 vs typhon's x48/x64).
NEGATIVE 13: a Leinth VARIANT repointed at the generic orb must FAIL
             (her bespoke "Leinth's Essense" proxy must stay hers - R-73).
NEGATIVE 14: an apex loot group cut below her ORIGINAL table's chance must FAIL
             (the computed no-nerf proof).

The Will-2026-07-29 half (R-99: EVERY Toxeus variant is on the apex orb):
NEGATIVE 15..N: ONE PER ROSTER RECORD - that record loses its orb (repointed at
             the lower generic tier) and the gate must FAIL. Generated from the
             DERIVED roster, so a variant added later automatically gets its own
             planted negative instead of being trusted.
NEGATIVE R1: a Toxeus variant the pin does not know about must FAIL (planted by
             dropping a member from ROSTER_PINNED - the "silently dropped roster"
             failure R-99 exists to close).
NEGATIVE R2: a pinned Toxeus variant missing from the db must FAIL (a rename or a
             deletion of a ratified record).
NEGATIVE R3: the SECOND, name-tag derivation must fire - a non-Toxeus boss given a
             Toxeus display tag must FAIL (this is the derivation that catches a
             Toxeus authored outside the 'toxeus' path namespace).
             ⚠️ THIS TEST FOUND A REAL GATE HOLE, so do not "simplify" its donor.
             The donor `boss_titan_typhon_42` is deliberately a BESPOKE-template
             boss (`database\Templates\Typhon2.tpl`, not Monster.tpl). The second
             derivation used to filter on Monster.tpl, so this subtest came back
             gate=PASS - meaning a boss on a bespoke template could wear a
             champion's display tag and both derivations would miss it. The
             derivation was widened to every template except Pet.tpl; picking a
             friendlier Monster.tpl donor would have hidden the bug instead.

COUNT: 29 subtests as of the R-99 roster of 8 (2 positives + negatives 1-14 +
one per roster record + R1-R5). The roster half is GENERATED, so the count grows
by itself when a variant is ratified - it is not a number to keep in sync by hand.
NEGATIVE R4: the base-game false-positive pin must be LOAD-BEARING - with
             _TAG_FALSE_POSITIVES emptied, the two am_assassin records must FAIL
             the gate, proving the second derivation really evaluates them.
NEGATIVE R5: a DONOR tier stripped below its measured consumer floor must FAIL
             (genericbossorb_01, which um_toxeus_21 left, is protected exactly
             like genericbossorb_04).

Usage: py tools/debug/negtest_uber_apex_orb.py [<built.arz>]
Exit 0 = every subtest behaves as specified.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))                 # tools/
sys.path.insert(0, str(HERE.parent / 'patches'))     # not needed, but harmless
from arz_patcher import ArzDatabase                  # noqa: E402
from patches import uber_apex_orb as M               # noqa: E402


def run_gate(db):
    try:
        M.verify(db, {})
        return 'PASS'
    except SystemExit:
        return 'FAIL'


def main():
    arz = sys.argv[1] if len(sys.argv) > 1 else \
        str(HERE.parents[1] / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz')
    p = Path(arz)
    if not p.exists():
        print(f'ERROR: arz not found: {arz}')
        return 2
    db = ArzDatabase.from_arz(p)

    results = []
    skipped = []

    def sub(label, mutate, want):
        """Snapshot -> mutate -> gate -> restore."""
        saved = []
        for rec, field in mutate.get('_touch', []):
            saved.append((rec, field, db.get_field_value(rec, field)))
        mutate['do']()
        got = run_gate(db)
        for rec, field, val in saved:
            db.set_field(rec, field, val)
        results.append((label, got, want))

    def sub_const(label, name, value, want):
        """Same, for a MODULE constant rather than a db field.

        Some failure modes are properties of the roster CONTRACT, not of any one
        record (a variant the pin never heard of; a pinned variant that vanished;
        a false-positive pin that stopped being load-bearing). Those are planted
        where they live - on the module's own constants - rather than faked with
        a db edit that would be testing something else.
        """
        old = getattr(M, name)
        setattr(M, name, value)
        got = run_gate(db)
        setattr(M, name, old)
        results.append((label, got, want))

    ENSLAVER, DEVOURER = (r for _l, r in M._CHAMPIONS)
    N_TABLE = M.CHAIN['normal'][5]
    N_POOL = M.CHAIN['normal'][1]
    ORB04_CHEST_N = M.CHAIN['normal'][2]

    # POSITIVE 1
    results.append(('positive 1 (real built arz)', run_gate(db), 'PASS'))

    # ── the DERIVED roster, printed so the harness's own scope is auditable ──
    roster = M.toxeus_roster(db)
    print('\nDERIVED Toxeus roster (%d records) - one planted negative each:'
          % len(roster))
    for r in roster:
        print('   %-64s -> %s'
              % (r, str(M._v1(db, r, M._TREASURE)).rsplit('\\', 1)[-1]))

    # NEGATIVE 1: champion back on orb04
    sub('negative 1 (Enslaver reverted to genericbossorb_04)',
        {'_touch': [(ENSLAVER, M._TREASURE)],
         'do': lambda: db.set_field(ENSLAVER, M._TREASURE, M.ORB04)}, 'FAIL')

    # NEGATIVE 2: a NON-Toxeus record joins orb05 (scope creep onto the apex tier)
    third = r'records\creature\monster\questbosses\boss_titan_typhon_42.dbr'
    if db.has_record(third):
        sub('negative 2 (a NON-Toxeus record points at genericbossorb_05)',
            {'_touch': [(third, M._TREASURE)],
             'do': lambda: db.set_field(third, M._TREASURE, M.ORB05)}, 'FAIL')
    else:
        skipped.append('negative 2 (donor record %s absent)' % third)

    # NEGATIVE 3: spawn multiplier cut below Leinth's
    sub('negative 3 (orb05 numSpawnMin multiplier cut below Leinth)',
        {'_touch': [(N_TABLE, 'numSpawnMinEquation')],
         'do': lambda: db.set_field(N_TABLE, 'numSpawnMinEquation',
                                    '(3+(1.6*numberOfPlayers))*0.9')}, 'FAIL')

    # NEGATIVE 4: loot4Chance back to the orb04 value
    sub('negative 4 (orb05 loot4Chance reverted to 12.7)',
        {'_touch': [(N_TABLE, 'loot4Chance')],
         'do': lambda: db.set_field(N_TABLE, 'loot4Chance', 12.7)}, 'FAIL')

    # NEGATIVE 5: a unique weight lowered
    uw_key = None
    ff = M._fields(db, N_TABLE)
    for k, v in sorted(ff.items()):
        if k.startswith('loot') and 'Name' in k and v and isinstance(v[0], str) \
                and 'unique' in v[0].lower():
            uw_key = k.replace('Name', 'Weight')
            break
    if uw_key:
        sub('negative 5 (an orb05 unique-entry weight cut below Leinth\'s 50)',
            {'_touch': [(N_TABLE, uw_key)],
             'do': lambda: db.set_field(N_TABLE, uw_key, 27)}, 'FAIL')
    else:
        skipped.append('negative 5 (no unique entry found on %s)' % N_TABLE)

    # NEGATIVE 6: broken chain link
    sub('negative 6 (orb05 normal pool no longer points at its chest)',
        {'_touch': [(N_POOL, 'fixedItemName1')],
         'do': lambda: db.set_field(N_POOL, 'fixedItemName1',
                                    r'records\item\containers\new\nope.dbr')}, 'FAIL')

    # NEGATIVE 7: R-48 collateral damage
    sub('negative 7 (Devourer soul rate cut below R-48\'s 100)',
        {'_touch': [(DEVOURER, 'chanceToEquipFinger2')],
         'do': lambda: db.set_field(DEVOURER, 'chanceToEquipFinger2', 25.0)}, 'FAIL')

    # NEGATIVE 8: donor-chain tamper
    sub('negative 8 (the orb04 normal chest retargeted - donor chain tampered)',
        {'_touch': [(ORB04_CHEST_N, 'tables')],
         'do': lambda: db.set_field(ORB04_CHEST_N, 'tables', N_TABLE)}, 'FAIL')

    # ── the Will-2026-07-27 half: Leinth is INCLUDED and must not be nerfed ──
    L_CHEST_N = M.LEINTH_CHESTS['normal']
    L_OLD_TABLE_N = M.LEINTH_TABLES_BY_DIFF['normal']

    # NEGATIVE 9: Leinth left behind on her old mid-tier table
    sub('negative 9 (Leinth normal chest reverted to her old Act-3 loot table)',
        {'_touch': [(L_CHEST_N, 'tables')],
         'do': lambda: db.set_field(L_CHEST_N, 'tables', L_OLD_TABLE_N)}, 'FAIL')

    # NEGATIVE 10: Leinth left on the down-scaling level equation
    sub('negative 10 (Leinth normal chest reverted to the c03 down-scaling equation)',
        {'_touch': [(L_CHEST_N, 'levelEquationFile')],
         'do': lambda: db.set_field(
             L_CHEST_N, 'levelEquationFile',
             r'records\item\containers\c03_containerlevelequation.dbr')}, 'FAIL')

    # NEGATIVE 11: her bespoke identity clobbered by the re-tier
    sub('negative 11 (Leinth chest mesh clobbered with the generic orb mesh)',
        {'_touch': [(L_CHEST_N, 'mesh')],
         'do': lambda: db.set_field(L_CHEST_N, 'mesh',
                                    r'DRX\meshes\bossorbmesh.msh')}, 'FAIL')

    # NEGATIVE 12: her richer gold generator swapped for the champions' poorer one
    sub('negative 12 (Leinth chest switched to the POORER bossgoldgenerator)',
        {'_touch': [(L_CHEST_N, 'goldGenerator')],
         'do': lambda: db.set_field(
             L_CHEST_N, 'goldGenerator',
             r'records\item\miscellaneous\gold\bossgoldgenerator.dbr')}, 'FAIL')

    # NEGATIVE 13: a Leinth variant repointed at the generic orb (identity loss)
    L_VARIANT = M.LEINTH_VARIANTS[0]
    sub('negative 13 (q_leinth_47 repointed at the generic orb, losing her Essense)',
        {'_touch': [(L_VARIANT, M._TREASURE)],
         'do': lambda: db.set_field(L_VARIANT, M._TREASURE, M.ORB05)}, 'FAIL')

    # NEGATIVE 14: the computed no-nerf proof - an apex group cut below her original
    sub('negative 14 (apex loot2Chance cut below Leinth\'s original 25.0)',
        {'_touch': [(N_TABLE, 'loot2Chance')],
         'do': lambda: db.set_field(N_TABLE, 'loot2Chance', 1.0)}, 'FAIL')

    # ══ the Will-2026-07-29 half (R-99): EVERY Toxeus variant is on the orb ══
    # ONE planted negative PER ROSTER RECORD, generated from the DERIVED roster
    # so a variant added later gets its own negative automatically. Each one is
    # "this record lost its orb"; the gate must FAIL on every single one, which
    # is the property the old two-champion count could not express.
    for i, rec in enumerate(roster, start=15):
        short = rec.rsplit('\\', 1)[-1][:-4]
        sub('negative %d (R-99 roster: %s loses its apex orb)' % (i, short),
            {'_touch': [(rec, M._TREASURE)],
             'do': (lambda r=rec: db.set_field(r, M._TREASURE, M.ORB04))}, 'FAIL')

    # NEGATIVE R1: a Toxeus variant the pin has never heard of.
    # Planted by dropping the LAST member from ROSTER_PINNED, which makes the
    # derived roster carry one record the pin does not contain - byte-for-byte
    # the situation that let the Endless Hunt ship with no orb.
    sub_const('negative R1 (a DERIVED Toxeus variant is not in ROSTER_PINNED)',
              'ROSTER_PINNED', tuple(M.ROSTER_PINNED[:-1]), 'FAIL')

    # NEGATIVE R2: a pinned Toxeus variant that is not in the db (rename/deletion).
    sub_const('negative R2 (a ROSTER_PINNED variant is missing from the db)',
              'ROSTER_PINNED',
              tuple(M.ROSTER_PINNED)
              + (r'records\creature\monster\skeleton\um_toxeus_ghost_77.dbr',),
              'FAIL')

    # NEGATIVE R3: the SECOND (name-tag) derivation fires on a Toxeus authored
    # outside the 'toxeus' path namespace.
    tag_donor = r'records\creature\monster\questbosses\boss_titan_typhon_42.dbr'
    hunt_tag = M._v1(db, M._HUNT, 'description')
    if db.has_record(tag_donor) and hunt_tag:
        sub('negative R3 (a non-Toxeus Monster given the Toxeus display tag %s)'
            % hunt_tag,
            {'_touch': [(tag_donor, 'description')],
             'do': lambda: db.set_field(tag_donor, 'description', hunt_tag)}, 'FAIL')
    else:
        skipped.append('negative R3 (tag donor %s or the Hunt tag absent)' % tag_donor)

    # NEGATIVE R4: the base-game false-positive pin must be LOAD-BEARING. With it
    # emptied, am_assassin_04/06 (which really do carry tagMonsterName190) must
    # trip the second derivation - proving the pin suppresses a REAL hit rather
    # than documenting an imaginary one.
    sub_const('negative R4 (_TAG_FALSE_POSITIVES emptied - the base-game '
              'am_assassin tag-sharers must trip the gate)',
              '_TAG_FALSE_POSITIVES', (), 'FAIL')

    # NEGATIVE R5: a DONOR tier stripped below its measured consumer floor.
    # genericbossorb_01 is the tier um_toxeus_21 left; its other 10 consumers are
    # protected exactly like orb04's 19.
    roster_low = {M._norm(r) for r in roster}
    orb01_others = [c for c in M._consumers_of(db, M.ORB01)
                    if M._norm(c) not in roster_low]
    if orb01_others:
        victim = orb01_others[0]
        sub('negative R5 (%s pulled off genericbossorb_01 - donor tier stripped '
            'below its floor)' % victim.rsplit('\\', 1)[-1][:-4],
            {'_touch': [(victim, M._TREASURE)],
             'do': lambda: db.set_field(victim, M._TREASURE, M.ORB04)}, 'FAIL')
    else:
        skipped.append('negative R5 (genericbossorb_01 has no non-Toxeus consumer)')

    # FINAL POSITIVE: everything restored, gate green again
    results.append(('positive 2 (all mutations restored)', run_gate(db), 'PASS'))

    ok = 0
    print()
    for label, got, want in results:
        good = got == want
        ok += good
        print(f'  [{"PASS" if good else "FAIL"}] {label}: gate={got} (expected {want})')
    for s in skipped:
        print(f'  [SKIP] {s}')
    print(f'\n{ok}/{len(results)} subtests behaved as specified'
          + (f' ; {len(skipped)} SKIPPED' if skipped else ''))
    if skipped:
        # A silently skipped subtest is a gate that is not being tested. Never
        # let that pass quietly.
        print('  WARNING: skipped subtests above are NOT proof of anything.')
    return 0 if ok == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
