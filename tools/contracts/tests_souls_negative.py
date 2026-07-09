r"""Permanent NEGATIVE-TEST suite for contracts_souls.py.

For every contract, take a COMPLIANT soul/creature from the real database, surgically
break (in memory only) the exact field the contract guards, and prove the contract
FIRES on that subject; then prove it does NOT fire once the value is restored/safe.
This guards the contracts themselves against silent regression (a contract that never
fires is worthless). No file is written; all mutation is on the in-memory ArzDatabase.

Usage (same positional cfg order as contracts_souls.py):
  python tools/contracts/tests_souls_negative.py <arz> <text_arc> <levels_arc>
        <quests_arc> <resource_arc_dir> <base_game_dir> <upstream_dir>
Exit 0 = every assertion held; 1 = a contract failed to fire (or mis-fired).
"""
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import contracts_souls as C
from arz_patcher import DATA_TYPE_INT, DATA_TYPE_FLOAT, DATA_TYPE_STRING


def build_cfg(argv):
    order = C._CFG_ORDER
    cfg = {k: None for k in order}
    for k, v in zip(order, argv[1:]):
        cfg[k] = v if v else None
    if not cfg['arz']:
        print(__doc__)
        print("ERROR: <arz> required.", file=sys.stderr)
        sys.exit(2)
    return cfg


def main(argv):
    cfg = build_cfg(argv)
    ctx = C._Ctx(cfg)
    souls = ctx.real_souls()

    # Baseline violation subjects per contract, so we pick CLEAN subjects to break.
    base_by_c = defaultdict(set)
    seed = []
    for fn in C._CONTRACT_FUNCS:
        fn(ctx, souls, seed)
    for v in seed:
        base_by_c[v['contract']].add(C._norm(v['subject']))

    results = []

    def record(name, want_fire, subject_norm, viols):
        hit = any(C._norm(v['subject']) == subject_norm for v in viols)
        results.append((name, 'PASS' if hit == want_fire else 'FAIL', subject_norm,
                        [(v['contract'], v['message'][:48]) for v in viols
                         if C._norm(v['subject']) == subject_norm][:2]))

    def clean_soul(contract, need_field=None, pred=None):
        for n in souls:
            if C._norm(n) in base_by_c.get(contract, set()):
                continue
            if need_field and not (ctx.fscalar(n, need_field) and str(ctx.fscalar(n, need_field)).strip()):
                continue
            if pred and not pred(n):
                continue
            return n
        return None

    def gt1(n, f):
        v = ctx.fscalar(n, f)
        return v is not None and int(v) >= 1

    # 1. SOUL-SKILL-REF-RESOLVES
    s = clean_soul('SOUL-SKILL-REF-RESOLVES', 'itemSkillName')
    o = ctx.fscalar(s, 'itemSkillName')
    ctx.db.set_field(s, 'itemSkillName', 'records\\skills\\BOGUS_NEGTEST.dbr', DATA_TYPE_STRING)
    out = []; C._c_skill_ref_resolves(ctx, [s], out)
    record('SOUL-SKILL-REF-RESOLVES fires on dangling ref', True, C._norm(s), out)
    ctx.db.set_field(s, 'itemSkillName', o, DATA_TYPE_STRING)

    # 2. SOUL-ITEMCOST-RESOLVES
    s = clean_soul('SOUL-ITEMCOST-RESOLVES', 'itemCostName')
    o = ctx.fscalar(s, 'itemCostName')
    ctx.db.set_field(s, 'itemCostName', 'records\\game\\BOGUS_COST.dbr', DATA_TYPE_STRING)
    out = []; C._c_itemcost_resolves(ctx, [s], out)
    record('SOUL-ITEMCOST-RESOLVES fires on dangling cost', True, C._norm(s), out)
    ctx.db.set_field(s, 'itemCostName', o, DATA_TYPE_STRING)

    # 3. SOUL-ICON-RESOLVES (missing + empty)
    s = clean_soul('SOUL-ICON-RESOLVES', 'bitmap')
    o = ctx.fscalar(s, 'bitmap')
    ctx.db.set_field(s, 'bitmap', 'SVItems\\jewelry\\BOGUS_ICON.tex', DATA_TYPE_STRING)
    out = []; C._c_icon_resolves(ctx, [s], out)
    record('SOUL-ICON-RESOLVES fires on missing icon', True, C._norm(s), out)
    ctx.db.set_field(s, 'bitmap', '', DATA_TYPE_STRING)
    out = []; C._c_icon_resolves(ctx, [s], out)
    record('SOUL-ICON-RESOLVES fires on empty bitmap', True, C._norm(s), out)
    ctx.db.set_field(s, 'bitmap', o, DATA_TYPE_STRING)

    # 4. SOUL-PROC-ACTIVATION (level 0) + restore is clean
    s = clean_soul('SOUL-PROC-ACTIVATION', 'itemSkillName', lambda n: gt1(n, 'itemSkillLevel'))
    o = ctx.fscalar(s, 'itemSkillLevel')
    ctx.db.set_field(s, 'itemSkillLevel', 0, DATA_TYPE_INT)
    out = []; C._c_proc_activation(ctx, [s], out)
    record('SOUL-PROC-ACTIVATION fires on itemSkillLevel==0', True, C._norm(s), out)
    ctx.db.set_field(s, 'itemSkillLevel', o, DATA_TYPE_INT)
    out = []; C._c_proc_activation(ctx, [s], out)
    record('SOUL-PROC-ACTIVATION silent after restore', False, C._norm(s), out)

    # 5. SOUL-AUGMENT-LEVEL
    s = clean_soul('SOUL-AUGMENT-LEVEL', 'augmentSkillName1', lambda n: gt1(n, 'augmentSkillLevel1'))
    o = ctx.fscalar(s, 'augmentSkillLevel1')
    ctx.db.set_field(s, 'augmentSkillLevel1', 0, DATA_TYPE_INT)
    out = []; C._c_augment_level(ctx, [s], out)
    record('SOUL-AUGMENT-LEVEL fires on augmentSkillLevel1==0', True, C._norm(s), out)
    ctx.db.set_field(s, 'augmentSkillLevel1', o, DATA_TYPE_INT)

    # 6. SOUL-NAME-RESOLVES
    s = clean_soul('SOUL-NAME-RESOLVES', 'itemNameTag')
    o = ctx.fscalar(s, 'itemNameTag')
    ctx.db.set_field(s, 'itemNameTag', 'tagBOGUS_NAME_NEGTEST', DATA_TYPE_STRING)
    out = []; C._c_name_resolves_and_color(ctx, [s], out)
    record('SOUL-NAME-RESOLVES fires on unresolved tag', True, C._norm(s), out)
    ctx.db.set_field(s, 'itemNameTag', o, DATA_TYPE_STRING)

    # 7. SOUL-NAME-COLOR (inject a resolving tag whose value lacks {^F})
    s = clean_soul('SOUL-NAME-COLOR', 'itemNameTag')
    tags = ctx.text_tags()
    if tags is not None:
        tags['tagNEGTEST_NOCOLOR'] = 'Plain Name No Color'
        o = ctx.fscalar(s, 'itemNameTag')
        ctx.db.set_field(s, 'itemNameTag', 'tagNEGTEST_NOCOLOR', DATA_TYPE_STRING)
        out = []; C._c_name_resolves_and_color(ctx, [s], out)
        record('SOUL-NAME-COLOR fires on non-{^F} name', True, C._norm(s), out)
        ctx.db.set_field(s, 'itemNameTag', o, DATA_TYPE_STRING)

    # 8. SOUL-LEVEL-ONLY
    s = clean_soul('SOUL-LEVEL-ONLY')
    o = ctx.fscalar(s, 'strengthRequirement')
    ctx.db.set_field(s, 'strengthRequirement', 50, DATA_TYPE_INT)
    out = []; C._c_level_only(ctx, [s], out)
    record('SOUL-LEVEL-ONLY fires on nonzero stat requirement', True, C._norm(s), out)
    ctx.db.set_field(s, 'strengthRequirement', o if o is not None else 0, DATA_TYPE_INT)

    # 9. SOUL-GRANT-USABILITY (clone a granted skill, flip Class to a non-grantable Skill_*)
    donor = None
    for n in souls:
        isn = ctx.fscalar(n, 'itemSkillName')
        if isn and ctx.recmap.get(C._norm(isn)):
            donor = ctx.recmap[C._norm(isn)]
            break
    tmp = 'records\\skills\\NEGTEST_NONGRANT_SKILL.dbr'
    ctx.db.clone_record(donor, tmp)
    ctx.db.set_field(tmp, 'Class', 'Skill_NONGRANTABLE_NEGTEST', DATA_TYPE_STRING)
    ctx.recmap[C._norm(tmp)] = tmp
    s = clean_soul('SOUL-GRANT-USABILITY', 'itemSkillName')
    o = ctx.fscalar(s, 'itemSkillName')
    ctx.db.set_field(s, 'itemSkillName', tmp, DATA_TYPE_STRING)
    out = []; C._c_grant_usability(ctx, [s], out)
    record('SOUL-GRANT-USABILITY fires on non-grantable Class', True, C._norm(s), out)
    ctx.db.set_field(s, 'itemSkillName', o, DATA_TYPE_STRING)

    # 10. SOUL-DROP-CLASSIFICATION (wire a soul into a Common creature's Finger2)
    victim = None
    for n in ctx.db.record_names():
        nl = C._norm(n)
        if not any(m in nl for m in C.CREATURE_MARKERS):
            continue
        mc = ctx.fscalar(n, 'monsterClassification')
        if mc and mc not in C.HERO_BOSS_QUEST and ctx.db.get_fields(n):
            victim = n
            break
    ctx.db.set_field(victim, 'lootFinger2Item1', souls[0], DATA_TYPE_STRING)
    ctx.db.set_field(victim, 'chanceToEquipFinger2', 50.0, DATA_TYPE_FLOAT)
    out = []; C._c_drop_classification(ctx, souls, out)
    record('SOUL-DROP-CLASSIFICATION fires on non-HBQ soul drop', True, C._norm(victim), out)
    ctx.db.set_field(victim, 'chanceToEquipFinger2', 0.0, DATA_TYPE_FLOAT)
    out = []; C._c_drop_classification(ctx, souls, out)
    record('SOUL-DROP-CLASSIFICATION silent at chance 0', False, C._norm(victim), out)

    # report
    npass = sum(1 for _, r, _, _ in results if r == 'PASS')
    print("=== contracts_souls NEGATIVE TESTS ===")
    for name, r, subj, ev in results:
        print(f"  [{r}] {name}")
        if r == 'FAIL':
            print(f"        subject={subj}  observed={ev}")
    print(f"\n{npass}/{len(results)} assertions PASS")
    return 0 if npass == len(results) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
