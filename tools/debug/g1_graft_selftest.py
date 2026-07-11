"""BUILD36 LANE B graft self-test (cheap, no full rebuild): load the already-built
work .arz as the live db, run graft_svaera_mastery_skills + _apply_runemaster_buffs
against the real base + SVAERA arzs, then assert every invariant the full build's
gates will check. Writes to a scratch .arz and reloads to prove serialization.

Usage: py tools/debug/g1_graft_selftest.py [our_arz] [base_arz] [svaera_arz] [scratch_out]
Exit 0 = all asserts pass.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build_svc_database as B
from arz_patcher import ArzDatabase
from validate_player_skill_anims import check_db as check_anims

OUR = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:/Users/willi/repos/tqit_soulvizier_classic/work/SoulvizierClassic/Database/SoulvizierClassic.arz"
BASE = sys.argv[2] if len(sys.argv) > 2 else \
    r"C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Database/database.arz"
SVAERA = sys.argv[3] if len(sys.argv) > 3 else \
    r"C:/Program Files (x86)/Steam/steamapps/workshop/content/475150/2076433374/SVAERA_customquest/Database/SVAERA_customquest.arz"
SCRATCH = sys.argv[4] if len(sys.argv) > 4 else \
    r"C:/Users/willi/AppData/Local/Temp/claude/C--Users-willi-repos/fc31fa12-e2e4-44ef-998c-7fe110587b8c/scratchpad/graft_selftest.arz"


def norm(s):
    return s.replace('/', '\\').lower().strip()


FAILS = []


def check(cond, msg):
    print(f"  {'PASS' if cond else 'FAIL'}: {msg}")
    if not cond:
        FAILS.append(msg)


def gv(db, name, f):
    v = db.get_field_value(name, f)
    return (v[0] if isinstance(v, list) and v else v)


def main():
    print("Loading work + base + SVAERA ...")
    db = ArzDatabase.from_arz(Path(OUR))
    base_db = ArzDatabase.from_arz(Path(BASE))
    svaera_db = ArzDatabase.from_arz(Path(SVAERA))

    tags = B.graft_svaera_mastery_skills(db, base_db, svaera_db)
    B._apply_runemaster_buffs(db, base_db)

    print("\n===== ASSERTIONS =====")
    m = {norm(n): n for n in db.record_names()}

    # 1) the 18 grafted skill/pet records + 3 asset-closure records present
    must_exist = [
        r'records\skills\warfare\drx_clubslam.dbr',
        r'records\skills\warfare\drx_clubslam_fissure.dbr',
        r'records\skills\warfare\drx_ancestralmod.dbr',
        r'records\skills\defensive\drx_activeblock.dbr',
        r'records\skills\defensive\drx_summonphalanx.dbr',
        r'records\skills\earth\drx_firenova.dbr',
        r'records\skills\earth\drxrupture.dbr',
        r'records\skills\earth\drxrupture_burning.dbr',
        r'records\skills\earth\drxrupture_flare.dbr',
        r'records\skills\storm\drx_lightningdash.dbr',
        r'records\skills\storm\drxfrostnova.dbr',
        r'records\skills\nature\drx_earthbind.dbr',
        r'records\skills\nature\drx_nymph_petmodifier_rootwave.dbr',
        r'records\skills\nature\drx_nymph_petskill_rootwave.dbr',       # closure
        r'records\xpack\skills\dream\drx_summoncopy.dbr',
        r'records\xpack\skills\dream\pet\dreamcopypet.dbr',             # closure
        r'records\xpack\skills\dream\pet\dreamcopypet_petskill_aura.dbr',  # closure
        r'records\skills\boss skills\hero_conversionimmunity_pets.dbr',   # closure
        r'records\effects\_drx_effects\storm\storm_frostnova_fx.dbr',   # asset
        r'records\effects\_drx_effects\storm\storm_frostnova_fxpak.dbr',  # asset
        r'records\xpack\skills\dream\pet\anm\anm_dreamcopy.dbr',        # asset
    ]
    miss = [p for p in must_exist if norm(p) not in m]
    check(not miss, f"all {len(must_exist)} closure records present (missing: {miss})")

    # 2) tree wiring
    tree_expect = {
        r'records\skills\warfare\drxwarfareskilltree.dbr': {
            27: r'records\skills\warfare\drx_clubslam.dbr',
            28: r'records\skills\warfare\drx_clubslam_fissure.dbr',
            29: r'records\skills\warfare\drx_ancestralmod.dbr'},
        r'records\skills\defensive\drxdefensiveskilltree.dbr': {
            26: r'records\skills\defensive\drx_activeblock.dbr',
            27: r'records\skills\defensive\drx_summonphalanx.dbr'},
        r'records\skills\earth\drxearthskilltree.dbr': {
            26: r'records\skills\earth\drx_firenova.dbr',
            27: r'records\skills\earth\drxrupture.dbr',
            28: r'records\skills\earth\drxrupture_burning.dbr',
            29: r'records\skills\earth\drxrupture_flare.dbr'},
        r'records\skills\storm\drxstormskilltree.dbr': {
            26: r'records\skills\storm\drx_lightningdash.dbr',
            27: r'records\skills\storm\drxfrostnova.dbr'},
        r'records\skills\nature\drxnatureskilltree.dbr': {
            26: r'records\skills\nature\drx_earthbind.dbr',
            27: r'records\skills\nature\drx_nymph_petmodifier_rootwave.dbr'},
        r'records\xpack\skills\dream\drxdreamskilltree.dbr': {
            26: r'records\xpack\skills\dream\drx_summoncopy.dbr'},
    }
    for tree, slots in tree_expect.items():
        tn = m.get(norm(tree))
        for slot, want in slots.items():
            got = gv(db, tn, f'skillName{slot}')
            check(norm(str(got)) == norm(want),
                  f"{tree.rsplit(chr(92),1)[-1]}[skillName{slot}] = {want.rsplit(chr(92),1)[-1]} (got {got})")

    # 3) UI slots present + registered in panels
    ui_expect = [
        (r'records\ingameui\player skills\mastery 1', 26),
        (r'records\ingameui\player skills\mastery 1', 27),
        (r'records\ingameui\player skills\mastery 1', 28),
        (r'records\ingameui\player skills\mastery 2', 25),
        (r'records\ingameui\player skills\mastery 2', 26),
        (r'records\ingameui\player skills\mastery 3', 25),
        (r'records\ingameui\player skills\mastery 3', 26),
        (r'records\ingameui\player skills\mastery 3', 27),
        (r'records\ingameui\player skills\mastery 3', 28),
        (r'records\ingameui\player skills\mastery 4', 26),
        (r'records\ingameui\player skills\mastery 4', 27),
        (r'records\ingameui\player skills\mastery 8', 25),
        (r'records\ingameui\player skills\mastery 8', 26),
        (r'records\xpack\ui\skills\mastery 9', 25),
    ]
    for base, slot in ui_expect:
        check(norm(r'%s\skill%02d.dbr' % (base, slot)) in m,
              f"UI slot exists: {base.rsplit(chr(92),1)[-1]}\\skill{slot:02d}")

    # panel registration: ingameui xpack3 override must list the new buttons
    for mi, hi in ((1, 28), (2, 26), (3, 28), (4, 27), (8, 26)):
        pane = m.get(norm(r'records\xpack3\ui\skills\mastery %d\panectrl.dbr' % mi))
        btns = gv(db, pane, 'tabSkillButtons') if pane else None
        btns = db.get_field_value(pane, 'tabSkillButtons') if pane else []
        want = norm(r'Records\InGameUI\Player Skills\Mastery %d\Skill%02d.dbr' % (mi, hi))
        has = any(norm(b) == want for b in (btns or []))
        check(has, f"xpack3 panectrl M{mi} lists skill{hi:02d}")

    # Dream panectrl lists skill25
    dp = m.get(norm(r'records\xpack\ui\skills\mastery 9\panectrl.dbr'))
    dbtns = db.get_field_value(dp, 'tabSkillButtons') if dp else []
    check(any(norm(b) == norm(r'records\xpack\ui\skills\mastery 9\skill25.dbr') for b in (dbtns or [])),
          "Dream panectrl lists skill25")

    # 4) drxrupture dangling refs cleared
    r2 = gv(db, m.get(norm(r'records\skills\earth\drxrupture.dbr')), 'particleEffectName2')
    check(not r2, f"drxrupture particleEffectName2 cleared (got {r2!r})")

    # 5) Runemaster buffs
    mw = m.get(norm(r'records\xpack2\skills\runemaster\menhirwall.dbr'))
    check(mw is not None and float(gv(db, mw, 'skillCooldownTime')) == 18.0
          and float(gv(db, mw, 'spawnObjectsTimeToLive')) == 14.0,
          "menhirwall buffed (cd 18, ttl 14)")
    mn = m.get(norm(r'records\xpack2\skills\runemaster\mines.dbr'))
    check(mn is not None and float(gv(db, mn, 'skillCooldownTime')) == 8.0
          and float(gv(db, mn, 'skillActiveDuration')) == 14.0,
          "mines buffed (cd 8, dur 14)")

    # 6) tags
    check(len(tags) == 12, f"12 SV-authored tags returned (got {len(tags)})")

    # 7) Occult/Hunting (mastery/UI 5,6) untouched: their highest UI slot unchanged
    for mi, exp_hi in ((5, 26), (6, 24)):
        hi = max((si for si in range(1, 40)
                  if norm(r'records\ingameui\player skills\mastery %d\skill%02d.dbr' % (mi, si)) in m),
                 default=0)
        check(hi == exp_hi, f"mastery {mi} (Occult/Hunting) UI unchanged (highest slot {hi}=={exp_hi})")

    # 8) player-anim gate PASS
    print("\n----- player-skill anim gate -----")
    try:
        viol = check_anims(db, base_db=base_db, fail=False)
        check(not viol, f"player-anim gate: {len(viol)} violation(s)")
    except SystemExit as e:
        check(False, f"player-anim gate raised: {e}")

    # 9) serialization round-trip
    print("\n----- serialization round-trip -----")
    db.write_arz(Path(SCRATCH))
    rl = ArzDatabase.from_arz(Path(SCRATCH))
    rlm = {norm(n): n for n in rl.record_names()}
    check(all(norm(p) in rlm for p in must_exist), "all grafted records survive write+reload")
    check(norm(gv(rl, rlm.get(norm(r'records\skills\warfare\drxwarfareskilltree.dbr')), 'skillName27'))
          == norm(r'records\skills\warfare\drx_clubslam.dbr'),
          "tree wiring survives write+reload")

    print("\n" + "=" * 60)
    print(f"RESULT: {'ALL PASS' if not FAILS else 'FAIL (%d)' % len(FAILS)}")
    for f in FAILS:
        print(f"   - {f}")
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(main())
