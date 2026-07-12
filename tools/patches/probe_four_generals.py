"""Ground-truth probe for the four_generals build37 module.

Verifies every donor record + field the module depends on, against the built
build36 lane arz. Read-only. Run with:
  PYTHONIOENCODING=utf-8 py tools/patches/probe_four_generals.py <arz>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase


def main():
    arz = sys.argv[1] if len(sys.argv) > 1 else (
        Path(__file__).resolve().parents[2]
        / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz')
    db = ArzDatabase.from_arz(Path(arz))
    print(f"Loaded {arz} ({len(db.record_names())} records)\n")

    names = {n.replace('/', '\\').lower(): n for n in db.record_names()}

    def R(p):
        return names.get(p.replace('/', '\\').lower())

    def val(p, f):
        r = R(p)
        if not r:
            return None
        v = db.get_field_value(r, f)
        return v

    def show(p, fields):
        r = R(p)
        tag = 'OK ' if r else 'MISSING'
        print(f"[{tag}] {p}")
        if not r:
            return
        for f in fields:
            v = db.get_field_value(r, f)
            print(f"       {f} = {v!r}")

    print("=" * 70)
    print("1. THE 6 GENERAL RECORDS (edit targets)")
    print("=" * 70)
    gens = {
        'a': ['records\\xpack\\creatures\\monster\\machae\\xsq27_namedhero_a_machae_45.dbr',
              'records\\xpack\\creatures\\monster\\machae\\xsq27_namedhero_a_machae_47.dbr'],
        'b': ['records\\xpack\\creatures\\monster\\machae\\xsq27_namedhero_b_machae_45.dbr',
              'records\\xpack\\creatures\\monster\\machae\\xsq27_namedhero_b_machae_47.dbr'],
        'c': ['records\\xpack\\creatures\\monster\\machae\\xsq27_namedhero_c_machae_45.dbr',
              'records\\xpack\\creatures\\monster\\machae\\xsq27_namedhero_c_machae_47.dbr'],
    }
    for g, paths in gens.items():
        for p in paths:
            r = R(p)
            if not r:
                print(f"[MISSING] {p}")
                continue
            cls = db.get_field_value(r, 'monsterClassification')
            mesh = db.get_field_value(r, 'mesh')
            lvl = db.get_field_value(r, 'charLevel')
            life = db.get_field_value(r, 'characterLife')
            desc = db.get_field_value(r, 'description')
            # free skillName slots
            used = []
            free = []
            for i in range(1, 25):
                v = db.get_field_value(r, f'skillName{i}')
                v = v[0] if isinstance(v, list) else v
                if isinstance(v, str) and v.strip():
                    used.append((i, v.rsplit('\\', 1)[-1]))
                else:
                    free.append(i)
            # specialAttack slots
            sa = {}
            for suff in ('', '2', '3', '4', '5'):
                sk = db.get_field_value(r, f'specialAttack{suff}SkillName')
                sk = sk[0] if isinstance(sk, list) else sk
                ch = db.get_field_value(r, f'specialAttack{suff}Chance')
                ch = ch[0] if isinstance(ch, list) else ch
                rg = db.get_field_value(r, f'specialAttack{suff}Range')
                rg = rg[0] if isinstance(rg, list) else rg
                sa[suff or '1'] = (str(sk).rsplit('\\', 1)[-1] if sk else None, ch, rg)
            print(f"[OK] gen {g}: {p.rsplit(chr(92),1)[-1]}")
            print(f"       class={cls} mesh={mesh} charLevel={lvl} life={life} desc={desc}")
            print(f"       skillName used={used}")
            print(f"       free skillName slots={free[:10]}")
            print(f"       specialAttacks={sa}")
            print(f"       Finger2: chance={db.get_field_value(r,'chanceToEquipFinger2')} "
                  f"item1={db.get_field_value(r,'lootFinger2Item1')}")

    print("\n" + "=" * 70)
    print("2. ARCHER SUMMON DONOR + ARCHER SKINS")
    print("=" * 70)
    show('records\\skills\\boss skills\\nehebkau_summonscorpions.dbr',
         ['Class', 'petLimit', 'petBurstSpawn', 'spawnObjects', 'spawnObjectsTimeToLive',
          'skillCooldownTime', 'skillSpecialAnimationName'])
    for skin in ('ar', 'br', 'cr'):
        show(f'records\\xpack\\creatures\\monster\\machae\\{skin}_masterarcher_42.dbr',
             ['monsterClassification', 'mesh', 'charLevel', 'description', 'chanceToEquipFinger2'])

    print("\n" + "=" * 70)
    print("3. MARSHAL DONOR xhero_aorg_45 (+ mobility fields)")
    print("=" * 70)
    show('records\\xpack\\creatures\\monster\\machae\\xhero_aorg_45.dbr',
         ['monsterClassification', 'mesh', 'charLevel', 'characterLife', 'scale',
          'charAnimationTableName', 'description', 'skillName1', 'skillName2',
          'chanceToEquipRightHand', 'chanceToEquipLeftHand', 'chanceToEquipFinger2',
          'treasureProxyName', 'unarmedRunAnim'])

    print("\n" + "=" * 70)
    print("4. THE 3 EXISTING GENERAL SOULS (downside enrich targets)")
    print("=" * 70)
    for base in ('dysnomion', 'trophonios', 'makaria'):
        for t in ('n', 'e', 'l'):
            p = f'records\\item\\equipmentring\\soul\\machae\\{base}_soul_{t}.dbr'
            r = R(p)
            if not r:
                print(f"[MISSING] {p}")
                continue
            # look for any negative field
            negs = []
            for key, tf in (db.get_fields(r) or {}).items():
                fn = key.split('###')[0]
                for v in (tf.values or []):
                    try:
                        if float(v) < 0:
                            negs.append((fn, v))
                    except (TypeError, ValueError):
                        pass
            nt = db.get_field_value(r, 'itemNameTag')
            isk = db.get_field_value(r, 'itemSkillName')
            fd = db.get_field_value(r, 'FileDescription')
            if t == 'n':
                print(f"[OK] {base}_soul_{t}: nameTag={nt} itemSkill={isk} FileDesc={fd}")
            print(f"       {t}: negatives={negs}")

    print("\n" + "=" * 70)
    print("5. PROXY/POOL/LIMIT/ORB/FX/KIT DONORS")
    print("=" * 70)
    donors = [
        ('records\\drxmap\\proxy\\q_leinth_lone.dbr', ['pool1', 'difficultyLimitsFile', 'chanceToRun']),
        ('records\\drxmap\\proxy\\pools\\q_leinth_lone.dbr', ['name1', 'spawnMax', 'championChance', 'nameChampion1', 'nameChampion3']),
        ('records\\proxies boss\\herolimit_all.dbr', ['maxPlayerLevelEquationNormal', 'maxPlayerLevelEquationLegendary']),
        ('records\\proxies orient\\limit_bloodtoxeus.dbr', ['maxPlayerLevelEquationLegendary']),
        ('records\\item\\containers\\new\\genericbossorb_04.dbr', ['Class']),
        ('records\\proxies orient\\difficulty_04.dbr', ['Class']),
        # FX shroud donors
        ('records\\skills\\boss skills\\hades2_shadowcloud_aurabuff.dbr', ['Class', 'charFxPakSelfNames']),
        ('records\\effects\\custom\\343_dark_smoke.dbr', ['Class']),
        # marshal kit skills
        ('records\\skills\\boss skills\\boss_conversionimmunity.dbr', ['Class']),
        ('records\\skills\\monster skills\\passive_buffs\\hero_scaling.dbr', ['Class']),
        ('records\\skills\\monster skills\\globalproperties_legendary01.dbr', ['Class']),
        ('records\\skills\\monster skills\\defense\\armor_passive.dbr', ['Class']),
        ('records\\skills\\spirit\\lifedrain.dbr', ['Class', 'skillSpecialAnimationName']),
        # summon-the-boss builder deps
        ('records\\skills\\soulskills\\summon_lyia.dbr', ['Class', 'skillSpecialAnimationName']),
        ('records\\skills\\soulskills\\pets\\lyialeafsong_1.dbr', ['Class']),
    ]
    for p, fs in donors:
        show(p, fs)

    print("\n" + "=" * 70)
    print("6. GUARD DONOR CANDIDATES (machae champions) + gigantes groundbreaker")
    print("=" * 70)
    for p in ('records\\skills\\boss skills\\gigantes_groundbreaker.dbr',
              'records\\drxcreatures\\drxdishonorguard\\anapaest_45.dbr'):
        show(p, ['Class', 'monsterClassification', 'mesh'])
    # find machae champion candidates for guards
    print("\n  machae champion candidates (Champion, in machae dir):")
    cnt = 0
    for n in db.record_names():
        nl = n.replace('/', '\\').lower()
        if '\\monster\\machae\\' not in nl:
            continue
        cls = db.get_field_value(n, 'monsterClassification')
        cls = cls[0] if isinstance(cls, list) else cls
        if cls == 'Champion':
            mesh = db.get_field_value(n, 'mesh')
            mesh = mesh[0] if isinstance(mesh, list) else mesh
            print(f"    {n.rsplit(chr(92),1)[-1]}  mesh={mesh}")
            cnt += 1
            if cnt > 20:
                print("    ...")
                break

    print("\n" + "=" * 70)
    print("7. specialAttack4 boss precedent + present-but-empty check")
    print("=" * 70)
    for p in ('records\\xpack\\creatures\\monster\\bosses\\egypttelkine\\boss_egypttelkine_aktaios_27.dbr',):
        r = R(p)
        if r:
            print(f"[OK] {p}: sa4Skill={db.get_field_value(r,'specialAttack4SkillName')} "
                  f"sa4Chance={db.get_field_value(r,'specialAttack4Chance')}")
        else:
            print(f"[MISSING/altpath] {p}")

    # collision check: do any of my NEW paths already exist?
    print("\n" + "=" * 70)
    print("8. COLLISION CHECK (my NEW record paths must be ABSENT)")
    print("=" * 70)
    new_paths = [
        'records\\skills\\quest skills\\svc_xsq27\\svc_general_summonarchers_a.dbr',
        'records\\skills\\quest skills\\svc_xsq27\\svc_general_summonarchers_b.dbr',
        'records\\skills\\quest skills\\svc_xsq27\\svc_general_summonarchers_c.dbr',
        'records\\skills\\quest skills\\svc_xsq27\\svc_marshal_summonarchers.dbr',
        'records\\skills\\svc\\svc_marshal_shroud.dbr',
        'records\\xpack\\creatures\\monster\\machae\\svc_um_hadesmarshal_80.dbr',
        'records\\drxmap\\proxy\\q_hadesmarshal_lone.dbr',
        'records\\drxmap\\proxy\\pools\\q_hadesmarshal_lone.dbr',
        'records\\item\\equipmentring\\soul\\svc_uber\\hadesmarshal_soul_n.dbr',
    ]
    for p in new_paths:
        print(f"    {'EXISTS(!)' if R(p) else 'absent(ok)'}  {p}")


if __name__ == '__main__':
    main()
