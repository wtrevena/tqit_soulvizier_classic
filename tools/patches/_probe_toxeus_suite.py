"""build37 toxeus_suite implementer probe (READ-ONLY).

Verifies every donor record + field + collision-free NEW path the module needs,
against the built lane arz. Run:
  PYTHONIOENCODING=utf-8 py tools/patches/_probe_toxeus_suite.py <arz>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # tools/
from arz_patcher import ArzDatabase


def main():
    arz = sys.argv[1] if len(sys.argv) > 1 else \
        r'work/SoulvizierClassic/Database/SoulvizierClassic.arz'
    db = ArzDatabase.from_arz(Path(arz))
    print(f"\n==== PROBE against {arz} : {len(db._raw_records)} records ====\n")

    recmap = {n.replace('/', '\\').lower(): n for n in db.record_names()}

    def R(p):
        return recmap.get(p.replace('/', '\\').lower())

    def gv(rec, f):
        r = R(rec) if isinstance(rec, str) else rec
        if not r:
            return None
        return db.get_field_value(r, f)

    def show(rec, fields, label=None):
        r = R(rec)
        print(f"--- {label or rec}")
        if not r:
            print(f"    !!! MISSING: {rec}")
            return
        print(f"    path={r}  rectype={db._record_types.get(r)!r}")
        for f in fields:
            print(f"    {f} = {db.get_field_value(r, f)!r}")

    # 1. Blood Toxeus monster - Misc4 free?
    BT = r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr'
    show(BT, ['Class', 'charLevel', 'chanceToEquipMisc1', 'lootMisc1Item1',
              'chanceToEquipMisc2', 'lootMisc2Item1', 'chanceToEquipMisc3',
              'lootMisc3Item1', 'chanceToEquipMisc4', 'chanceToEquipMisc4Item1',
              'lootMisc4Item1', 'chanceToEquipFinger2', 'lootFinger2Item1',
              'chanceToEquipRightHand', 'chanceToEquipLeftHand'], 'BLOOD TOXEUS')

    # 2. finalletter chassis
    for cand in (r'records\drxmap\quest\finalletter.dbr',
                 r'records\xpack\quests\dialog\finalletter.dbr'):
        if R(cand):
            show(cand, ['Class', 'templateName', 'itemText', 'description',
                        'itemNameTag', 'FileDescription', 'mesh', 'baseTexture',
                        'bitmap', 'itemClassification', 'relicSelectionStyle'],
                 'FINALLETTER')
    # any finalletter record
    for n in db.record_names():
        if 'finalletter' in n.lower():
            print(f"    finalletter candidate: {n}  ({db._record_types.get(n)})")

    # 3. ambush proxy donor = q_bloodtoxeus_lone proxy + pool
    PX = r'records\drxmap\proxy\q_bloodtoxeus_lone.dbr'
    show(PX, ['Class', 'templateName', 'chanceToRun', 'pool1', 'mesh', 'scale',
              'difficultyLimitsFile', 'difficultyEquationFile', 'placementExtents',
              'weight1', 'baseTexture'], 'AMBUSH DONOR PROXY (q_bloodtoxeus_lone)')
    POOL = r'records\drxmap\proxy\pools\q_bloodtoxeus_lone.dbr'
    show(POOL, ['Class', 'templateName', 'FileDescription', 'name1', 'name2',
                'name3', 'nameChampion1', 'nameChampion2', 'nameChampion3',
                'spawnMin', 'spawnMax', 'championChance', 'championMin',
                'championMax', 'weight1', 'weightChampion1'], 'BT POOL (_BT_POOL)')

    # 4. ShadowStalker rig donor (am_deathstalker_55_ambush) + marauder (to differ)
    RIG = r'records\creature\monster\shadowstalker\am_deathstalker_55_ambush.dbr'
    show(RIG, ['Class', 'templateName', 'mesh', 'charAnimationTableName',
               'baseTexture', 'characterRacialProfile', 'monsterClassification',
               'charLevel', 'scale', 'actorHeight', 'characterRunSpeed',
               'attackSkillName', 'initialSkillName', 'skillName1', 'skillName2',
               'skillName3', 'skillName4', 'skillName5',
               'handHitDamageMin', 'handHitDamageMax'], 'SHADOWSTALKER RIG DONOR')
    # dump all skillName* + specialAttack* on the rig donor
    r = R(RIG)
    if r:
        print("    [rig donor skill/anim/tex fields]")
        for key, tf in (db.get_fields(r) or {}).items():
            fn = key.split('###')[0]
            if any(t in fn for t in ('skill', 'Skill', 'Anim', 'anim', 'Texture',
                                     'mesh', 'Mesh', 'charFxPak', 'Fx')):
                print(f"      {fn} = {tf.values!r}")

    MAR = r'records\creature\monster\shadowstalker\um_enslaver_marauder_99.dbr'
    show(MAR, ['Class', 'mesh', 'baseTexture', 'charAnimationTableName',
               'characterRacialProfile', 'monsterClassification', 'charLevel',
               'charFxPakRunningNames', 'scale', 'actorHeight'], 'ENSLAVER MARAUDER (avoid collision)')

    # 5. stalker kit skills (exact path resolution)
    print("\n--- STALKER KIT SKILL PATHS (resolve check) ---")
    kit = [
        r'records\skills\monster skills\attack_melee\netherstrike.dbr',
        r'records\skills\monster skills\attack_radius\toxeus_bladestorm.dbr',
        r'records\skills\stealth\flashpowder.dbr',
        r'records\skills\stealth\lethalstrike.dbr',
        r'records\skills\stealth\lethalstrike_mortalwound.dbr',
        r'records\skills\spirit\lifedrain.dbr',
        r'records\skills\monster skills\auras\character_speedall.dbr',
        r'records\skills\boss skills\boss_conversionimmunity.dbr',
        r'records\skills\monster skills\passive_buffs\hero_scaling.dbr',
        r'records\skills\monster skills\passive_buffs\toxeus_passiveproperties.dbr',
        r'records\skills\monster skills\defense\armor_passive.dbr',
        r'records\skills\monster skills\globalproperties_normal01.dbr',
        r'records\skills\monster skills\globalproperties_epic01.dbr',
        r'records\skills\monster skills\globalproperties_legendary01.dbr',
        r'records\skills\monster skills\attack_melee\toxeus_attackskill.dbr',
    ]
    for k in kit:
        rk = R(k)
        cls = db.get_field_value(rk, 'Class') if rk else None
        anim = db.get_field_value(rk, 'skillSpecialAnimationName') if rk else None
        print(f"    {'OK ' if rk else 'MISS'} {k}  Class={cls!r} specialAnim={anim!r}")

    # 5b. flashpowder castability detail (proc)
    show(r'records\skills\stealth\flashpowder.dbr',
         ['Class', 'skillSpecialAnimationName', 'skillConnectionType',
          'skillMasterLevel', 'skillMaxLevel'], 'FLASHPOWDER (soul proc)')
    show(r'records\skills\soulskills\melinoe_bloodboil.dbr',
         ['Class', 'skillSpecialAnimationName'], 'MELINOE_BLOODBOIL (ref proc)')
    # nightstalker_shadowsurge (WILL granted-skill pick for a DIFFERENT toxeus soul)
    for cand in (r'records\skills\stealth\nightstalker_shadowsurge.dbr',
                 r'records\skills\soulskills\nightstalker_shadowsurge.dbr'):
        if R(cand):
            show(cand, ['Class', 'skillSpecialAnimationName'], 'NIGHTSTALKER_SHADOWSURGE')

    # 6. soul augments
    print("\n--- SOUL AUGMENTS ---")
    for a in (r'records\skills\stealth\drxanatomy.dbr',
              r'records\skills\stealth\drxopenwound.dbr'):
        ra = R(a)
        print(f"    {'OK ' if ra else 'MISS'} {a}  Class={db.get_field_value(ra,'Class') if ra else None!r}")

    # 7. FixedItemLoot numSpawn idiom + FixedWeight inner shape
    show(r'records\item\loottables\dropables\01_n_hero_drops.dbr',
         ['Class', 'templateName', 'numSpawnMinEquation', 'numSpawnMaxEquation',
          'loot1Chance', 'loot1Name1', 'loot1Weight1'], '01_n_hero_drops (FixedItemLoot idiom)')
    for n in db.record_names():
        if '01_n_hero_drops' in n.lower():
            print(f"    hero_drops candidate: {n}")
    show(r'records\item\loottables\svc\crimsonverdict_guaranteed_l.dbr',
         ['Class', 'templateName', 'lootName1', 'lootWeight1'], 'crimsonverdict_guaranteed_l (FixedWeight inner shape)')
    # find a canonical FixedItemLoot.tpl record to copy the template header string
    print("    [sample FixedItemLoot.tpl records + numSpawn fields]")
    cnt = 0
    for n in db.record_names():
        t = db.get_field_value(n, 'templateName')
        if t and 'fixeditemloot.tpl' in str(t).lower():
            nsm = db.get_field_value(n, 'numSpawnMinEquation')
            print(f"      {n}  rectype={db._record_types.get(n)!r} numSpawnMin={nsm!r}")
            cnt += 1
            if cnt >= 4:
                break

    # 8. Hades pools for the sweep - count eligible-ish
    print("\n--- HADES PROXYPOOLS (sweep target: xpack\\proxieshades) ---")
    hades_pools = []
    for n in db.record_names():
        nl = n.replace('/', '\\').lower()
        t = db.get_field_value(n, 'templateName')
        if t and 'proxypool.tpl' in str(t).lower() and nl.startswith('records\\xpack\\proxieshades'):
            hades_pools.append(n)
    print(f"    total ProxyPool under xpack\\proxieshades = {len(hades_pools)}")
    for n in hades_pools[:6]:
        names = [db.get_field_value(n, 'name%d' % i) for i in range(1, 19)]
        names = [str(x) for x in names if x and str(x).strip()]
        wts = [db.get_field_value(n, 'weight%d' % i) for i in range(1, 19)]
        wts = [w for w in wts if w]
        print(f"      {n.split(chr(92))[-1]}  members={len(names)} weights~{wts[:6]}")

    # 9. PC anim tables (for universal-anim castability calc)
    print("\n--- PC ANIM TABLES ---")
    for n in db.record_names():
        nl = n.lower()
        if nl.endswith('.dbr') and 'animation' in nl and ('pc' in nl or 'player' in nl):
            print(f"    {n}")

    # 10. collision check: NEW paths must be ABSENT
    print("\n--- COLLISION CHECK (all should be ABSENT) ---")
    news = [
        r'records\drxmap\proxy\q_bloodtoxeus_ambush.dbr',
        r'records\item\artifacts\svc_toxeus_rant.dbr',
        r'records\item\loottables\svc\toxeus_rant_perplayer.dbr',
        r'records\item\loottables\svc\toxeus_rant_item.dbr',
        r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr',
        r'records\item\equipmentring\soul\svc_uber\toxeus_hunt_soul_n.dbr',
        r'records\item\equipmentring\soul\svc_uber\toxeus_hunt_soul_e.dbr',
        r'records\item\equipmentring\soul\svc_uber\toxeus_hunt_soul_l.dbr',
        r'records\proxies orient\limit_legendary_only.dbr',
        r'records\drxmap\proxy\q_toxeus_hunt.dbr',
    ]
    for p in news:
        print(f"    {'COLLISION!' if R(p) else 'free'}  {p}")

    # 11. ShadowStalker texture options (for a DISTINCT baseTexture)
    print("\n--- ShadowStalker / deathstalker textures (for distinct skin) ---")
    seen = set()
    for n in db.record_names():
        nl = n.lower()
        if 'shadowstalker' in nl or 'deathstalker' in nl:
            bt = db.get_field_value(n, 'baseTexture')
            mesh = db.get_field_value(n, 'mesh')
            if bt and str(bt).strip():
                key = str(bt).lower()
                if key not in seen:
                    seen.add(key)
                    print(f"    baseTexture={bt!r}  (on {n.split(chr(92))[-1]})  mesh={mesh!r}")
    # search the string table for shadowstalker textures
    print("    [string-table .tex containing shadowstalker/deathstalker/wraith]")
    for s in db.strings:
        sl = s.lower()
        if sl.endswith('.tex') and ('shadowstalker' in sl or 'deathstalker' in sl or 'nightstalker' in sl):
            print(f"      {s}")

    # 12. letterskin / parchment textures + Parchment.tpl users
    print("\n--- Parchment textures / template ---")
    for s in db.strings:
        sl = s.lower()
        if sl.endswith('.tex') and ('letter' in sl and ('skin' in sl or 'bitmap' in sl or 'ui' in sl)):
            print(f"    tex: {s}")
    for s in db.strings:
        if s.lower().endswith('qi_insurgencyscroll01.msh'):
            print(f"    scroll mesh: {s}")

    print("\n==== PROBE DONE ====")


if __name__ == '__main__':
    main()
