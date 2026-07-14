"""b39 dry-run replay + fail-loud proof for boss_skill_fix (no heavy build).

Applies boss_skill_fix over a COPY of a built .arz (the FINAL post-monolith+registry
state the module sees at run time, since it runs last before `visuals`), runs its
roster-derived verify(), proves idempotency, re-audits surfaces A+B over all 10
target bosses, asserts the whole um_*_99 roster is clean of level-0 specials, and
runs a NEGATIVE test proving the roster scan fails loud on an uncovered boss.

Usage:  py tools/debug/b39_boss_skill_replay.py <built.arz>
Read-only against the input (loads into memory; never writes the arz). Deterministic.
"""
import os, sys, pathlib, re, io, contextlib

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_TOOLS, os.path.join(_TOOLS, 'debug'), os.path.join(_TOOLS, 'patches')):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from arz_patcher import ArzDatabase          # noqa: E402
import b39_boss_skill_audit as A             # noqa: E402
import boss_skill_fix as BF                  # noqa: E402


def snapshot(aud, rec):
    """(castable_specials, level0_specials, dead_core_passives) for a fought boss."""
    skills = aud.skill_slots(rec)
    lvl_by_ref = {A._n(s): lv for (s, lv) in skills.values()}
    castable = level0 = 0
    for (_slot, s, chance, _rng) in aud.special_slots(rec):
        ch = 0.0 if chance is None else float(chance)
        if aud.resolves(s) and ch > 0:
            castable += 1
        if (lvl_by_ref.get(A._n(s)) == 0) and ch > 0:
            level0 += 1
    dead_re = re.compile(r'(armor_passive|hero_scaling|boss_scaling|_conversionimmunity|passiveproperties)', re.I)
    dead = sum(1 for (s, lv) in skills.values() if lv == 0 and dead_re.search(A._base(s)))
    return (castable, level0, dead)


def main():
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print('Usage: py tools/debug/b39_boss_skill_replay.py <built.arz>')
        sys.exit(2)
    db = ArzDatabase.from_arz(pathlib.Path(sys.argv[1]))
    aud = A.Auditor(db)

    targets = [
        ('Helepolis', BF.HELEPOLIS), ('Voranthys', BF.VORANTHYS), ('Dorus', BF.DORUS),
        ('Kravmoloch', BF.KRAVMOLOCH), ('Gorrahk', BF.GORRAHK), ('Ilsevar', BF.ILSEVAR),
        ('Vashkarr', BF.VASHKARR), ('Sarkoth', BF.SARKOTH), ('Broodmother', BF.BROODMOTHER),
        ('Toxeus Hunt', BF.TOXEUS_HUNT),
    ]
    before = {rec: snapshot(aud, rec) for _l, rec in targets}

    print('\n########## APPLY ##########')
    BF.apply(db, {})
    print('\n########## verify() (roster-derived, fail-loud) ##########')
    BF.verify(db, {})

    print('\n########## IDEMPOTENCY (2nd apply -> 0 SET) ##########')
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        BF.apply(db, {})
    n_set2 = sum(1 for ln in buf.getvalue().splitlines() if '[SET' in ln)
    print('2nd apply SET edits: %d (expect 0)' % n_set2)

    after = {rec: snapshot(aud, rec) for _l, rec in targets}
    print('\n########## BEFORE -> AFTER (surface A) ##########')
    print('%-14s %-26s %-26s' % ('boss', 'BEFORE (cast/lvl0/dead)', 'AFTER (cast/lvl0/dead)'))
    ok = True
    for label, rec in targets:
        b, a = before[rec], after[rec]
        bad = (a[1] != 0 or a[2] != 0)
        ok = ok and not bad
        print('%-14s %-26s %-26s%s' % (label, str(b), str(a), '  <-- DEFECT' if bad else ''))

    print('\n########## ROSTER-WIDE (all um_*_99) ##########')
    roster = BF._roster_um99(db)
    leftover = [(r.rsplit('\\', 1)[-1], BF._l0_specials(db, r)) for r in roster if BF._l0_specials(db, r)]
    print('um_*_99 scanned: %d ; with chance>0 level-0 special: %d' % (len(roster), len(leftover)))
    for name, l0 in leftover:
        print('   !!! %s %s' % (name, l0))

    print('\n########## SURFACE B spot-check (pets untouched) ##########')
    for base in ('hadesmarshal_1', 'neferkha_1', 'voranthys_1', 'bloodtoxeus_1'):
        pet = A.M + r'skills\soulskills\pets\%s.dbr' % base
        n_ai = sum(1 for slot in ('attackSkillName', 'specialAttackSkillName',
                                  'specialAttack2SkillName', 'specialAttack3SkillName',
                                  'specialAttack4SkillName', 'specialAttack5SkillName')
                   if (aud.gv(pet, slot) or '').strip())
        print('  %-16s AI-slots=%d %s' % (base, n_ai, '' if db.has_record(pet) else '(MISSING)'))

    print('\n########## NEGATIVE TEST (roster scan must catch an UNCOVERED miss) ##########')
    victim = BF._R + r'xpack\creatures\monster\gigantes\um_polisgaoler_99.dbr'
    assert victim not in BF._TARGET_RECORDS
    db.set_field(victim, 'skillName20', r'records\skills\boss skills\aktaios_summontombguardians.dbr')
    db.set_field(victim, 'skillLevel20', 0)
    db.set_field(victim, 'specialAttack9SkillName', r'records\skills\boss skills\aktaios_summontombguardians.dbr')
    db.set_field(victim, 'specialAttack9Chance', 40.0)
    caught = False
    try:
        BF.verify(db, {})
    except SystemExit as e:
        caught = 'UNCOVERED' in str(e)
        print('verify() correctly RAISED:')
        for ln in str(e).splitlines()[:3]:
            print('   ' + ln)
    print('NEGATIVE TEST:', 'PASS' if caught else 'FAIL')

    print('\nRESULT:', 'PASS' if (ok and not leftover and n_set2 == 0 and caught) else 'FAIL')
    sys.exit(0 if (ok and not leftover and n_set2 == 0 and caught) else 1)


if __name__ == '__main__':
    main()
