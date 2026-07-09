"""Negative tests for contracts_summons.py.

For every contract: take a COMPLIANT record from the real DB, surgically break it IN MEMORY,
prove the contract now fires on that subject, then restore and prove it stops firing. Contracts
that already catch a real shipped bug (SUMMON-PET-NAKED, MONSTER-SPAWN-ELIGIBILITY) are proven by
their real-data firing. This is the established break-a-copy-prove-it-fires pattern.

Usage:
  python tools/contracts/tests_summons_negative.py [<arz>] [--base <TQAE dir>] [--res <arc dir>]
Defaults to the frozen build27 baseline copy in the session scratchpad if no arz is given.
Exit 0 if every contract's negative test PASSES, else 1.
"""
import sys
import contextlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import contracts_summons as C  # noqa: E402

_DEFAULT_BASELINE = (r'C:/Users/willi/AppData/Local/Temp/claude/C--Users-willi-repos/'
                     r'55f6c1cb-5e9b-466b-a25d-f3fb1a0c56a8/scratchpad/contracts_baseline/'
                     r'SoulvizierClassic.arz')


def build(argv):
    arz = _DEFAULT_BASELINE
    base = res = None
    i = 0
    while i < len(argv):
        if argv[i] == '--base' and i + 1 < len(argv):
            base = argv[i + 1]; i += 2
        elif argv[i] == '--res' and i + 1 < len(argv):
            res = argv[i + 1]; i += 2
        else:
            arz = argv[i]; i += 1
    cfg = C._default_cfg(arz, base, res)
    with contextlib.redirect_stdout(sys.stderr):
        return C._build_context(cfg)


def run_tests(ctx):
    results = {}

    def setf(nkey, field, value):
        ctx.our.set_field(ctx.our_key.get(C._norm(nkey)), field, value)

    def getf(nkey, field):
        return ctx.fv(nkey, field)

    def fires(fn, subj):
        return any(subj.lower() in v['subject'].lower() for v in fn(ctx))

    def negtest(cid, fn, subject, break_fn, restore_fn):
        before = fires(fn, subject)
        break_fn()
        after = fires(fn, subject)
        restore_fn()
        again = fires(fn, subject)
        results[cid] = 'PASS' if (not before and after and not again) else \
            'FAIL(before=%s,after=%s,restored=%s)' % (before, after, again)

    pets = sorted(ctx.pet_targets)

    def clean_pet(pred):
        for p in pets:
            if ctx.record_exists(p) and pred(p):
                return p
        return None

    # SUMMON-SPAWN-RESOLVE: inject a missing target reachable from a soul-skill
    fake = 'records\\zzz_neg_test_missing.dbr'
    ctx.spawn_targets[fake] = {'records\\skills\\soulskills\\summon_boneash.dbr'}
    r1 = fires(C.check_summon_spawn_resolve, 'zzz_neg_test_missing')
    del ctx.spawn_targets[fake]
    r2 = fires(C.check_summon_spawn_resolve, 'zzz_neg_test_missing')
    results['SUMMON-SPAWN-RESOLVE'] = 'PASS' if (r1 and not r2) else 'FAIL(%s,%s)' % (r1, r2)

    p = clean_pet(lambda x: not C._mesh_problem(ctx, x))
    o = getf(p, 'mesh')
    negtest('SUMMON-PET-MESH', C.check_summon_pet_mesh, p,
            lambda: setf(p, 'mesh', 'Creatures\\zzz\\does_not_exist_neg.msh'),
            lambda: setf(p, 'mesh', o))

    p = clean_pet(lambda x: next(C._iter_refs(ctx.fv(x, 'charAnimationTableName')), None)
                  and C._anim_problem(ctx, x) is None)
    o = getf(p, 'charAnimationTableName')
    negtest('SUMMON-PET-ANIM', C.check_summon_pet_anim, p,
            lambda: setf(p, 'charAnimationTableName', 'records\\zzz\\neg_anim_missing.dbr'),
            lambda: setf(p, 'charAnimationTableName', o))

    p = clean_pet(lambda x: any(C._iter_refs(ctx.fv(x, f)) for f in C._CONTROLLER_FIELDS))
    o = {f: getf(p, f) for f in C._CONTROLLER_FIELDS}
    negtest('SUMMON-PET-CONTROLLER', C.check_summon_pet_controller, p,
            lambda: [setf(p, f, '') for f in C._CONTROLLER_FIELDS],
            lambda: [setf(p, f, o[f] if o[f] is not None else '') for f in C._CONTROLLER_FIELDS])

    p = clean_pet(lambda x: bool(next(C._iter_list(ctx.fv(x, 'monsterClassification')), None)))
    o = getf(p, 'monsterClassification')
    negtest('SUMMON-PET-CLASSIFICATION', C.check_summon_pet_classification, p,
            lambda: setf(p, 'monsterClassification', ''),
            lambda: setf(p, 'monsterClassification', o))

    p = clean_pet(lambda x: not any(not ctx.record_exists(v) for _f, v in C._skill_refs(ctx, x)))
    o = getf(p, 'skillName1')
    negtest('SUMMON-PET-SKILLS', C.check_summon_pet_skills, p,
            lambda: setf(p, 'skillName1', 'records\\skills\\zzz_neg_skill_missing.dbr'),
            lambda: setf(p, 'skillName1', o if o is not None else ''))

    p = clean_pet(lambda x: True)
    oc = getf(p, 'chanceToEquipHead')
    oi = [getf(p, 'lootHeadItem%d' % i) for i in range(1, 7)]

    def _b():
        setf(p, 'chanceToEquipHead', 100.0)
        for i in range(1, 7):
            setf(p, 'lootHeadItem%d' % i, '')

    def _r():
        setf(p, 'chanceToEquipHead', oc if oc is not None else 0.0)
        for i in range(1, 7):
            setf(p, 'lootHeadItem%d' % i, oi[i - 1] if oi[i - 1] is not None else '')
    negtest('SUMMON-PET-EQUIP-RESOLVE', C.check_summon_pet_equip_resolve, p, _b, _r)

    # SUMMON-PET-NAKED: real-data positive (boneash)
    results['SUMMON-PET-NAKED'] = 'PASS' if fires(C.check_summon_pet_naked, 'boneash_1') \
        else 'FAIL(no real fire)'

    sb = 'records\\skills\\soulskills\\summon_boneash.dbr'
    o = getf(sb, 'spawnObjectsTimeToLive')
    negtest('SUMMON-TTL-PERMANENT', C.check_summon_ttl_permanent, 'summon_boneash',
            lambda: setf(sb, 'spawnObjectsTimeToLive', 45.0),
            lambda: setf(sb, 'spawnObjectsTimeToLive', o if o is not None else 0.0))

    mon = next((m for m in ctx.scoped_monsters if ctx.monster_tier.get(m) == 'authored'
                and not C._mesh_problem(ctx, m, require_mesh=False)
                and C._anim_problem(ctx, m) is None), None) \
        or 'records\\xpack\\creatures\\monster\\skeleton\\um_bloodtoxeus_99.dbr'
    o = getf(mon, 'mesh')
    negtest('MONSTER-MESH', C.check_monster_mesh, mon,
            lambda: setf(mon, 'mesh', 'Creatures\\zzz\\neg_monster_mesh.msh'),
            lambda: setf(mon, 'mesh', o))
    o = getf(mon, 'charAnimationTableName')
    negtest('MONSTER-ANIM', C.check_monster_anim, mon,
            lambda: setf(mon, 'charAnimationTableName', 'records\\zzz\\neg_monster_anim.dbr'),
            lambda: setf(mon, 'charAnimationTableName', o if o is not None else ''))
    o = getf(mon, 'skillName1')
    negtest('MONSTER-SKILLS-LOOT', C.check_monster_skills_loot, mon,
            lambda: setf(mon, 'skillName1', 'records\\skills\\zzz_neg_monster_skill.dbr'),
            lambda: setf(mon, 'skillName1', o if o is not None else ''))

    # MONSTER-SPAWN-ELIGIBILITY: real-data positive (bw_priest_houndmaster crowd-out)
    results['MONSTER-SPAWN-ELIGIBILITY'] = 'PASS' if \
        fires(C.check_monster_spawn_eligibility, 'bw_priest_houndmaster') else 'FAIL(no real fire)'
    return results


def main(argv):
    ctx = build(argv)
    results = run_tests(ctx)
    print('=== contracts_summons negative tests ===')
    allpass = True
    for cid, _fn in C._CHECKS:
        r = results.get(cid, '(not tested)')
        allpass = allpass and (r == 'PASS')
        print('  %-30s %s' % (cid, r))
    print('ALL PASS' if allpass else 'SOME FAILED')
    return 0 if allpass else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
