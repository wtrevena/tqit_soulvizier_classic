"""build37 registry module: HADES' GENERALS UPGRADE (four_generals).

Spec: scratchpad/specs/four_generals_upgrade_spec.md (DESIGN trust) + the binding
WILL_DECISIONS_2026-07-11 FOUR GENERALS block:
  - Package (c) BOTH: per-general new abilities + two-guard honor guards + a fourth
    uber warlord.
  - Marshal = "Menoetes, Marshal of the Dead", HP [26000,32000,40000], central-hall
    (Floor_03) placement (map lane surveys).
  - General souls: enrich the three EXISTING souls with light amgoz downsides
    (coordinate with the quality/handcraft waves - no double-edits).
  - QA-watch: Trophonios's archer-muster (specialAttack4) must fire in-game; the
    autocast fallback is pre-wired (here: a redundant specialAttack5 muster slot).

CONTRACT (tools/patches/README.md): expose MODULE_NAME + apply(db, tags). The
registry runs this AFTER the monolith apply_svc_patches over the SAME db/tags
objects, then runs ALL gates last. We reuse the monolith's proven builders
(_create_soul / _svc_boss_pool / _svc_boss_proxy / _build_boss_summon / _svc_set_kit
/ _svc_clear_soul_loot) and register our spawn proxies + hand-designed soul tag with
the monolith's gate registries so the gates cover this module's records.

QUEST-SAFETY (spec §2): the base quest xSQ27 tracks the 3 generals via
Condition_KillAllCreaturesFromProxy on the untouched proxy/pool records. Every edit
here is ADDITIVE on the general MONSTER records (new skillName/specialAttack fields,
plus Dysnomion's in-place set of the present-but-empty specialAttack2 fields) -
NEVER a removal, NEVER a path/classification/proxy/pool change. Guards + the marshal
are SEPARATE proxies (invisible to the quest). Summoned archers are TTL+petLimit
bounded (nehebkau precedent). All ground-truthed vs the build36 arz by
tools/patches/probe_four_generals.py.

No em dashes (repo standing rule).
"""
import sys
from pathlib import Path

# The registry imports this module from tools/patches/; make the monolith importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import apply_svc_patches as mono
from arz_patcher import DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

MODULE_NAME = 'four_generals'

S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

# ── EXISTING donors (all DB-verified present in the build36 arz, probe) ───────
_GEN = {
    'a': [r'records\xpack\creatures\monster\machae\xsq27_namedhero_a_machae_45.dbr',
          r'records\xpack\creatures\monster\machae\xsq27_namedhero_a_machae_47.dbr'],
    'b': [r'records\xpack\creatures\monster\machae\xsq27_namedhero_b_machae_45.dbr',
          r'records\xpack\creatures\monster\machae\xsq27_namedhero_b_machae_47.dbr'],
    'c': [r'records\xpack\creatures\monster\machae\xsq27_namedhero_c_machae_45.dbr',
          r'records\xpack\creatures\monster\machae\xsq27_namedhero_c_machae_47.dbr'],
}
_ARCHER = {
    'a': r'records\xpack\creatures\monster\machae\ar_masterarcher_42.dbr',   # Machae01b (ashen)
    'b': r'records\xpack\creatures\monster\machae\br_masterarcher_42.dbr',   # Machae02B (bilious)
    'c': r'records\xpack\creatures\monster\machae\cr_masterarcher_42.dbr',   # Machae03B (crimson)
}
_WARDEN = {   # theme-matched machae Champion donors for the honor guards
    'a': r'records\xpack\creatures\monster\machae\am_warden_43.dbr',   # Machae01b
    'b': r'records\xpack\creatures\monster\machae\bm_warden_43.dbr',   # Machae02B
    'c': r'records\xpack\creatures\monster\machae\cm_warden_43.dbr',   # Machae03B
}
_NEHEBKAU = r'records\skills\boss skills\nehebkau_summonscorpions.dbr'   # Skill_SpawnPetMonster
_MARSHAL_DONOR = r'records\xpack\creatures\monster\machae\xhero_aorg_45.dbr'   # Machae Hero, MachaeHero01
_LIFEDRAIN = r'records\skills\spirit\lifedrain.dbr'                 # Dysnomion flourish (Skill_AttackSpellChaos)
_GROUNDBREAKER = r'records\xpack\skills\monsterskills\activeattackwave\gigantes_groundbreaker.dbr'
_HADESBOLT = r'records\xpack\skills\monsterskills\activeattackprojectile\hero_hadesbolt.dbr'
_SPIRITBOLT_RING = r'records\xpack\skills\monsterskills\activeattackprojectile\hero_slowspiritbolt_ring.dbr'
_SHROUD_AURA = r'records\xpack\skills\bossskills\hades2_shadowcloud_aura.dbr'          # Skill_BuffRadiusToggled
_SHROUD_FXPAK = r'records\xpack\effects\boss effects\hades2_shadowcloud_charfxpak.dbr'  # renders hades_shadowcloudfx
_ORB04 = r'records\item\containers\new\genericbossorb_04.dbr'       # apex boss orb (boss-orb law)
_LIMIT_BLOODTOXEUS = r'records\proxies orient\limit_bloodtoxeus.dbr'   # no-cap [1..110]
_ARMOR_PASSIVE = r'records\skills\monster skills\defense\armor_passive.dbr'
_BONUSDMG_PHYS = r'records\xpack\skills\monsterskills\passive\bonusdamage_physical.dbr'
_HERO_SCALING = r'records\skills\monster skills\passive_buffs\hero_scaling.dbr'
_GLOBPROP_L = r'records\skills\monster skills\globalproperties_legendary01.dbr'
_BOSS_IMMUNITY = r'records\skills\boss skills\boss_conversionimmunity.dbr'

# ── NEW record paths (all collision-checked ABSENT in build36, probe §8) ──────
_SUMMON = {
    'a': r'records\skills\quest skills\svc_xsq27\svc_general_summonarchers_a.dbr',
    'b': r'records\skills\quest skills\svc_xsq27\svc_general_summonarchers_b.dbr',
    'c': r'records\skills\quest skills\svc_xsq27\svc_general_summonarchers_c.dbr',
}
_MARSHAL_MUSTER = r'records\skills\quest skills\svc_xsq27\svc_marshal_summonarchers.dbr'
_MARSHAL = r'records\xpack\creatures\monster\machae\svc_um_hadesmarshal_80.dbr'
_MARSHAL_POOL = r'records\drxmap\proxy\pools\q_hadesmarshal_lone.dbr'
_MARSHAL_PROXY = r'records\drxmap\proxy\q_hadesmarshal_lone.dbr'
_MARSHAL_YARD_POOL = r'records\drxmap\proxy\pools\q_yard_hadesmarshal.dbr'
_MARSHAL_YARD_PROXY = r'records\drxmap\proxy\q_yard_hadesmarshal.dbr'
_MARSHAL_SUMMON = r'records\skills\soulskills\summon_hadesmarshal.dbr'
_MARSHAL_PETS = [r'records\skills\soulskills\pets\hadesmarshal_%d.dbr' % i for i in (1, 2, 3)]
# 6 guard monsters (2 per general) + 3 guard-pair pools/proxies
_GUARD = {
    'a': [r'records\xpack\creatures\monster\machae\svc_general_a_guard1.dbr',
          r'records\xpack\creatures\monster\machae\svc_general_a_guard2.dbr'],
    'b': [r'records\xpack\creatures\monster\machae\svc_general_b_guard1.dbr',
          r'records\xpack\creatures\monster\machae\svc_general_b_guard2.dbr'],
    'c': [r'records\xpack\creatures\monster\machae\svc_general_c_guard1.dbr',
          r'records\xpack\creatures\monster\machae\svc_general_c_guard2.dbr'],
}
_GUARD_POOL = {g: r'records\drxmap\proxy\pools\q_general_%s_guardpair.dbr' % g for g in 'abc'}
_GUARD_PROXY = {g: r'records\drxmap\proxy\q_general_%s_guardpair.dbr' % g for g in 'abc'}
_GUARD_NAME_TAG = {
    'a': ['tagSVCGuardDysA', 'tagSVCGuardDysB'],
    'b': ['tagSVCGuardMakA', 'tagSVCGuardMakB'],
    'c': ['tagSVCGuardTroA', 'tagSVCGuardTroB'],
}
_MARSHAL_SOUL_TAG = 'tagSVCSoulHadesMarshal'
_GEN_BAND = [42, 58, 72]
_MARSHAL_BAND = [50, 66, 80]
_DIFFICULTY04 = r'records\proxies orient\difficulty_04.dbr'


# ── small field helpers ───────────────────────────────────────────────────────
def _has_field(db, rec, field):
    ff = db.get_fields(rec) or {}
    return any(k.split('###')[0] == field for k in ff)


def _setf(db, rec, field, value, dtype):
    """Set a field preserving dtype when it already exists (the cloned-record
    dtype-corruption law), or creating it with an explicit dtype when absent."""
    if _has_field(db, rec, field):
        db.set_field(rec, field, value)          # existing: preserve dtype
    else:
        db.set_field(rec, field, value, dtype)   # new field: explicit dtype


def _require(db, paths, label):
    missing = [p for p in paths if not mono._find_record(db, p)]
    if missing:
        raise SystemExit(
            "four_generals: REQUIRED donor(s) missing (%s): %s" % (label, missing))


# ═══════════════════════════════════════════════════════════════════════════════
def apply(db, tags):
    """Build the whole four_generals DB side in dependency order and register the
    new spawn proxies + hand-designed soul tag with the monolith gate registries."""
    print("\n=== build37 four_generals: Hades' Generals upgrade (abilities + guards + Menoetes) ===")

    # Fail loud if any critical donor is missing (this item ships as its own build).
    _require(db, [p for pair in _GEN.values() for p in pair], "generals")
    _require(db, list(_ARCHER.values()) + list(_WARDEN.values()), "machae skins")
    _require(db, [_NEHEBKAU, _MARSHAL_DONOR, _LIFEDRAIN, _GROUNDBREAKER, _HADESBOLT,
                  _SPIRITBOLT_RING, _SHROUD_AURA, _SHROUD_FXPAK, _ORB04,
                  _LIMIT_BLOODTOXEUS], "shared donors")
    for base in ('dysnomion', 'trophonios', 'makaria'):
        _require(db, [r'records\item\equipmentring\soul\machae\%s_soul_%s.dbr' % (base, t)
                      for t in 'nel'], "general souls")

    _build_muster_skills(db)          # 1. archer-muster skills (generals + marshal)
    _upgrade_generals(db)             # 2. edit the 6 general records (abilities)
    _build_marshal(db, tags)          # 3. the Menoetes marshal boss + shroud + orb
    _build_guards(db, tags)           # 4. 6 honor-guard champions
    _build_guard_placements(db)       # 5. guard pools/proxies (map lane places)
    _build_marshal_placement(db)      # 6. marshal pool/proxy/yard (map lane places)
    _build_marshal_soul(db, tags)     # 7. summon-the-marshal soul (Marshal's Command)
    _enrich_general_souls(db)         # 8. add a light amgoz downside to the 3 shipping souls
    _set_tags(db, tags)               # 9. Text tags
    _self_check(db)                   # 10. fail-loud resolution self-check

    print("=== four_generals: DONE (3 general upgrades + 6 guards + Menoetes marshal "
          "+ soul enrichment; map lane owns placements) ===")
    return tags


# ── 1. Archer-muster summon skills (Skill_SpawnPetMonster) ────────────────────
def _build_muster_skills(db):
    """Clone nehebkau_summonscorpions -> per-general + marshal archer musters.
    petLimit 3 (squad, not swarm), burst 3, a finite TTL (quest-safety §2.3;
    nehebkau ships no TTL - we add it deliberately), periodic cooldown. The special
    anim is blanked so each muster reuses the general's own proven cast (the machae
    rig already casts sa1/2/3; spec §3.1). These clones are NOT registered in the
    boss-kit clone-shape gate: adding spawnObjectsTimeToLive (absent on the donor,
    but a valid Skill_SpawnPetMonster field) is a deliberate class-valid add."""
    def one(dst, spawn_objs, pet_limit, cooldown):
        db.clone_record(_NEHEBKAU, dst)
        db.set_field(dst, 'spawnObjects', list(spawn_objs))   # preserve STRING dtype
        db.set_field(dst, 'petLimit', pet_limit)
        db.set_field(dst, 'petBurstSpawn', 3)
        _setf(db, dst, 'spawnObjectsTimeToLive', 20.0, F)     # finite TTL (quest-safe)
        db.set_field(dst, 'skillCooldownTime', float(cooldown))
        _setf(db, dst, 'skillSpecialAnimationName', '', S)    # reuse the slot's cast anim
        db._modified.add(dst)

    for g in 'abc':
        one(_SUMMON[g], [_ARCHER[g]], 3, 20.0)
    # the marshal commands ALL THREE generals' archers: a bigger petLimit-5 volley
    one(_MARSHAL_MUSTER, [_ARCHER['a'], _ARCHER['b'], _ARCHER['c']], 5, 18.0)
    print("  1. archer musters: 3 general summons (petLimit 3, TTL 20) + marshal "
          "muster (petLimit 5, all 3 skins)")


# ── 2. Upgrade the 6 general records (ADDITIVE; quest-safe §2.1) ──────────────
def _upgrade_generals(db):
    """Wire each general's archer muster (Will's ask) + Dysnomion's leech flourish.
    ADD skillName/specialAttack fields; for Dysnomion, SET the present-but-empty
    specialAttack2Chance/Range. Never remove a field; never touch path/class/proxy/
    pool. Applied to BOTH kit-identical variants (_45 and _47) of each general.
    The muster fires from a specialAttack slot at AnyRange so archers arrive from
    anywhere; skillLevel 1 = active (petLimit is fixed on the summon skill)."""
    # --- Dysnomion (a): summon on skillName6 + the present-but-empty sa2; leech
    #     flourish (spirit\lifedrain) on skillName7 + sa3 (his kit is the thinnest). ---
    for rec in _GEN['a']:
        _setf(db, rec, 'skillName6', _SUMMON['a'], S)
        _setf(db, rec, 'skillLevel6', 1, I)
        _setf(db, rec, 'specialAttack2SkillName', _SUMMON['a'], S)
        _setf(db, rec, 'specialAttack2Chance', 35.0, F)      # was present-but-empty 0.0
        _setf(db, rec, 'specialAttack2Range', 'AnyRange', S)  # was present LongRange
        _setf(db, rec, 'specialAttack2Timeout', 2.0, F)
        _setf(db, rec, 'specialAttack2Delay', 14.0, F)
        _setf(db, rec, 'skillName7', _LIFEDRAIN, S)
        _setf(db, rec, 'skillLevel7', 3, I)
        _setf(db, rec, 'specialAttack3SkillName', _LIFEDRAIN, S)
        _setf(db, rec, 'specialAttack3Chance', 30.0, F)
        _setf(db, rec, 'specialAttack3Range', 'AnyRange', S)
        db._modified.add(rec)

    # --- Makaria (b): summon on skillName9 + the clean-add sa3 ---
    for rec in _GEN['b']:
        _setf(db, rec, 'skillName9', _SUMMON['b'], S)
        _setf(db, rec, 'skillLevel9', 1, I)
        _setf(db, rec, 'specialAttack3SkillName', _SUMMON['b'], S)
        _setf(db, rec, 'specialAttack3Chance', 35.0, F)
        _setf(db, rec, 'specialAttack3Range', 'AnyRange', S)
        _setf(db, rec, 'specialAttack3Timeout', 2.0, F)
        _setf(db, rec, 'specialAttack3Delay', 14.0, F)
        db._modified.add(rec)

    # --- Trophonios (c): summon on skillName9 + sa4 (boss-proven slot). QA-watch:
    #     the muster is ALSO pre-wired on sa5 as the autocast fallback so it fires
    #     reliably (both are boss-used engine slots; petLimit 3 caps the total). ---
    for rec in _GEN['c']:
        _setf(db, rec, 'skillName9', _SUMMON['c'], S)
        _setf(db, rec, 'skillLevel9', 1, I)
        for suff in ('4', '5'):
            _setf(db, rec, 'specialAttack%sSkillName' % suff, _SUMMON['c'], S)
            _setf(db, rec, 'specialAttack%sChance' % suff, 35.0, F)
            _setf(db, rec, 'specialAttack%sRange' % suff, 'AnyRange', S)
            _setf(db, rec, 'specialAttack%sTimeout' % suff, 2.0, F)
            _setf(db, rec, 'specialAttack%sDelay' % suff, 14.0, F)
        db._modified.add(rec)

    print("  2. generals upgraded: Dysnomion (muster sa2 + lifedrain sa3), Makaria "
          "(muster sa3), Trophonios (muster sa4 + sa5 fallback); all _45 + _47, additive")


# ── 3. Menoetes, Marshal of the Dead (the fourth general / uber warlord) ──────
def _build_marshal(db, tags):
    """Clone the machae Hero xhero_aorg -> a Boss warlord over the three generals.
    HP [26000,32000,40000] (Will's binding decision - above the generals' real
    [20244,25305,30366] at every difficulty), L[50,66,80], scale 2.0, MachaeHero01
    rig, Hades' black-smoke shroud, apex boss orb. Kit layers all three generals'
    war themes + the archer muster (on sa5, pet-copy-safe: the summon-the-marshal
    pet never inherits a hostile spawner - _mirror_source_skill_kit skips it)."""
    db.clone_record(_MARSHAL_DONOR, _MARSHAL)
    sf = db.set_field
    sf(_MARSHAL, 'monsterClassification', 'Boss')            # souls + boss orb key off Boss
    sf(_MARSHAL, 'description', 'tagSVCMonsterHadesMarshal')
    sf(_MARSHAL, 'charLevel', list(_MARSHAL_BAND))
    sf(_MARSHAL, 'characterLife', [26000.0, 32000.0, 40000.0])
    sf(_MARSHAL, 'characterLifeRegen', [20.0, 40.0, 70.0])
    sf(_MARSHAL, 'scale', 2.0)
    sf(_MARSHAL, 'actorHeight', 2.4)
    # Hades' black-smoke identity: cast the Hades shadow-cloud aura at spawn AND
    # trail his lord's smoke as he moves (the proven Enslaver charFxPakRunningNames
    # visual route, Will's B5 decision). Both are shipped Hades assets (no new FX).
    _setf(db, _MARSHAL, 'initialSkillName', _SHROUD_AURA, S)
    _setf(db, _MARSHAL, 'charFxPakRunningNames', [_SHROUD_FXPAK], S)
    # a genuine boss wall: resistances at the general tier + apex orb
    sf(_MARSHAL, 'defensivePhysical', 30.0)
    sf(_MARSHAL, 'defensiveLife', 40.0)
    sf(_MARSHAL, 'defensivePierce', 35.0)
    _setf(db, _MARSHAL, 'treasureProxyName', _ORB04, S)      # apex boss orb (orb law)
    # WAR-COUNCIL ENFORCER kit (all EXISTING skills). specials: sa1 hadesbolt,
    # sa2 spiritbolt-ring, sa3 groundbreaker, sa4 lifedrain, sa5 = the archer muster.
    kit = [
        (_ARMOR_PASSIVE, 1), (_BONUSDMG_PHYS, 1), (_HERO_SCALING, 1),
        (_GLOBPROP_L, 1), (_BOSS_IMMUNITY, 1),
        (_HADESBOLT, 2), (_SPIRITBOLT_RING, 2), (_GROUNDBREAKER, 2),
        (_LIFEDRAIN, 3), (_MARSHAL_MUSTER, 1),
    ]
    special = [
        ('', _HADESBOLT, 45.0), ('2', _SPIRITBOLT_RING, 40.0),
        ('3', _GROUNDBREAKER, 40.0), ('4', _LIFEDRAIN, 40.0),
        ('5', _MARSHAL_MUSTER, 40.0),
    ]
    mono._svc_set_kit(db, _MARSHAL, kit, special)
    # ranges for the new special slots (sa1/2 inherit xhero_aorg's; set 3/4/5)
    _setf(db, _MARSHAL, 'specialAttack3Range', 'MediumRange', S)
    _setf(db, _MARSHAL, 'specialAttack4Range', 'AnyRange', S)
    _setf(db, _MARSHAL, 'specialAttack5Range', 'AnyRange', S)
    db._modified.add(_MARSHAL)
    print("  3. Menoetes marshal: Boss L[50,66,80] HP[26000,32000,40000] scale 2.0, "
          "MachaeHero01 + Hades black smoke, apex orb, war-council kit + muster (sa5)")


# ── 4. Six honor-guard champions (2 per general; SV/DRX guard pattern §4a) ────
def _build_guards(db, tags):
    """Two named elite machae honor-guards flank each general. Cloned from the
    theme-matched warden Champion (silhouette-distinct from the general's
    QuestMachae01), laddered to the general band, soul loot cleared (Champion), a
    modest scale bump so they read as elite honor-guards, not trash."""
    for g in 'abc':
        for idx, gpath in enumerate(_GUARD[g]):
            db.clone_record(_WARDEN[g], gpath)
            sf = db.set_field
            sf(gpath, 'monsterClassification', 'Champion')
            sf(gpath, 'description', _GUARD_NAME_TAG[g][idx])
            sf(gpath, 'charLevel', list(_GEN_BAND))
            sf(gpath, 'characterLife', [3200.0, 4200.0, 5400.0])
            sf(gpath, 'scale', 1.45)
            mono._svc_clear_soul_loot(db, gpath)   # Champions drop no soul (orb/soul law)
            db._modified.add(gpath)
    print("  4. honor guards: 6 named machae Champions (2 per general), theme-matched, "
          "no soul")


# ── 5. Guard placements (SEPARATE proxies -> quest-invisible §2.2) ────────────
def _build_guard_placements(db):
    """One guard-pair pool + proxy per general (spawnMin=Max=2, championChance=0 ->
    exactly the 2 named guards). SEPARATE from the quest pools; the map lane injects
    each proxy beside its general. Registered with the spawn-eligibility gate."""
    for g in 'abc':
        pool, proxy = _GUARD_POOL[g], _GUARD_PROXY[g]
        db.clone_record(mono._SVC_LEINTH_POOL, pool)
        sf = db.set_field
        sf(pool, 'FileDescription', 'four_generals: %s honor-guard pair' % g)
        sf(pool, 'name1', _GUARD[g][0]); sf(pool, 'weight1', 100)
        sf(pool, 'name2', _GUARD[g][1]); sf(pool, 'weight2', 100)
        sf(pool, 'name3', ''); sf(pool, 'weight3', 0)
        for i in (1, 2, 3):     # clear the leinth-donor champion residue
            sf(pool, 'nameChampion%d' % i, ''); sf(pool, 'weightChampion%d' % i, 0)
        sf(pool, 'spawnMin', 2); sf(pool, 'spawnMax', 2)
        sf(pool, 'championChance', 0.0); sf(pool, 'championMin', 0); sf(pool, 'championMax', 0)
        db._modified.add(pool)
        # proxy (clone the leinth lone placer; no-cap limit contains L72)
        db.clone_record(mono._SVC_LEINTH_PROXY, proxy)
        sf(proxy, 'pool1', pool)
        sf(proxy, 'chanceToRun', 100.0)
        sf(proxy, 'difficultyLimitsFile', _LIMIT_BLOODTOXEUS)
        sf(proxy, 'difficultyEquationFile', _DIFFICULTY04)
        sf(proxy, 'placementExtents', 5.0)
        db._modified.add(proxy)
        mono._MOD_AUTHORED_SPAWN_PROXIES.append({
            'proxy': proxy, 'pool': pool, 'main_monster': _GUARD[g][0],
            'name': 'q_general_%s_guardpair (2 honor guards, championChance=0)' % g})
    print("  5. guard placements: 3 guard-pair pools + proxies (SEPARATE from quest "
          "pools; map lane flanks each general)")


# ── 6. Marshal placement (boss + 2 escorts; the boss-guarantee LAW) ──────────
def _build_marshal_placement(db):
    """Lone-boss pool/proxy (1 marshal + 2 grandmaster-archer champion escorts via
    the spawnMax=3/championChance=100/championMin=Max=2 law) + a TESTHUB yard copy.
    limit_bloodtoxeus ([1..110]) contains the L80 marshal. Registered with the
    spawn-eligibility gate. The apex boss orb on the marshal IS the chest reward, so
    the proxy carries no separate hoard (spec: orb + soul is already a double reward)."""
    escort = _ARCHER['c']   # a Machae Grandmaster Archer Champion (no soul)
    # canonical placement (central hall, map lane surveys)
    mono._svc_boss_pool(db, _MARSHAL_POOL, _MARSHAL, escort,
                        'Menoetes (main) + 2 machae grandmaster-archer champion escorts')
    mono._svc_boss_proxy(db, _MARSHAL_PROXY, _MARSHAL_POOL, _LIMIT_BLOODTOXEUS,
                         r'XPack\Creatures\Monster\Machae\MachaeHero01.msh', 2.0,
                         hoard_pools=None)
    mono._MOD_AUTHORED_SPAWN_PROXIES.append({
        'proxy': _MARSHAL_PROXY, 'pool': _MARSHAL_POOL, 'main_monster': _MARSHAL,
        'name': 'q_hadesmarshal_lone (Menoetes + 2 archer-champion escorts)'})
    # TESTHUB yard (REAL records; @100% via the same law; map lane places it)
    mono._svc_boss_pool(db, _MARSHAL_YARD_POOL, _MARSHAL, escort,
                        'YARD: Menoetes + 2 escorts @100% (TESTHUB-only)')
    mono._svc_boss_proxy(db, _MARSHAL_YARD_PROXY, _MARSHAL_YARD_POOL, _LIMIT_BLOODTOXEUS,
                         r'XPack\Creatures\Monster\Machae\MachaeHero01.msh', 2.0,
                         hoard_pools=None)
    mono._MOD_AUTHORED_SPAWN_PROXIES.append({
        'proxy': _MARSHAL_YARD_PROXY, 'pool': _MARSHAL_YARD_POOL, 'main_monster': _MARSHAL,
        'name': 'q_yard_hadesmarshal (TESTHUB yard @100%)'})
    print("  6. marshal placement: q_hadesmarshal_lone (1 boss + 2 escorts) + yard; "
          "limit_bloodtoxeus contains L80; apex orb is the loot")


# ── 7. Marshal's Command soul (summon-the-marshal; house boss-soul pattern) ───
def _build_marshal_soul(db, tags):
    """The apex soul: raise Menoetes himself to march at the bearer's side (the
    proven _build_boss_summon boss-soul pattern - source mesh == dropper mesh, so the
    F2 summon-identity gate is native-clean; the hostile archer muster on the marshal
    is auto-dropped from the friendly pet). Downside: the weight of command slows the
    bearer's stride (amgoz V1). Wired to the marshal's Finger2. Hand-designed name
    (registered with the naming-gate whitelist)."""
    ok = mono._build_boss_summon(
        db, _MARSHAL, _MARSHAL_PETS, _MARSHAL_SUMMON,
        'tagSVCSummonHadesMarshal', 'tagSVCMonsterHadesMarshal',
        char_level=list(_MARSHAL_BAND),
        life=[13000.0, 17000.0, 22000.0], life_regen=[25.0, 45.0, 75.0],
        dmg_min=[80.0, 120.0, 175.0], dmg_max=[130.0, 195.0, 280.0], scale=2.0)
    if not ok:
        raise SystemExit("four_generals: marshal summon build failed (source missing)")

    def stats(t, il):
        m = {'n': 0.62, 'e': 0.82, 'l': 1.0}[t]
        lv = {'n': 1, 'e': 2, 'l': 3}[t]
        r = lambda v: round(v * m, 1)
        return {
            **mono._bmp(t),
            'itemSkillName': (S, _MARSHAL_SUMMON), 'itemSkillLevel': (I, lv),
            'characterStrength': (I, int(r(60))), 'characterDexterity': (I, int(r(45))),
            'characterOffensiveAbility': (F, r(90.0)),
            'offensivePhysicalModifier': (F, r(30.0)),
            'characterLife': (F, r(320.0)), 'characterLifeModifier': (F, r(10.0)),
            'defensivePhysical': (F, r(18.0)), 'defensiveLife': (F, r(20.0)),
            # the amgoz1 downside: the weight of command slows the bearer's stride
            'characterRunSpeedModifier': (F, {'n': -8.0, 'e': -9.0, 'l': -10.0}[t]),
        }
    tiers = [{'diff': t, 'itemLevel': il, 'stats': stats(t, il)}
             for t, il in (('n', 55), ('e', 74), ('l', 90))]
    for p in mono._create_soul(db, 'hadesmarshal', _MARSHAL_SOUL_TAG, tiers,
                               monster=_MARSHAL, drop_rate=66.0):
        db.set_field(p, 'FileDescription', 'Hades')     # amgoz1 V5 region word
        db._modified.add(p)

    # keep the evocative "{^F}Marshal's Command" name (not the {^F}<Monster> Soul
    # standard) - register with the hand-designed naming-gate whitelist (frozenset
    # reassignment; _verify_soul_naming reads the module global at call time).
    mono._HAND_DESIGNED_SOUL_TAGS = frozenset(mono._HAND_DESIGNED_SOUL_TAGS) | {_MARSHAL_SOUL_TAG}
    print("  7. Marshal's Command soul: summon-the-marshal (3 pets + skill), "
          "run-speed downside, Finger2@66; hand-designed name whitelisted")


# ── 8. Enrich the 3 EXISTING general souls with a light amgoz downside (§5.1) ─
def _enrich_general_souls(db):
    """The three general souls already ship (build36) all-upside. Add ONE themed
    amgoz-V1 downside to each - an in-place field EDIT (never _create_soul, never a
    new path). KEEP name tag / itemSkillName / augments / drop-wiring untouched.
    COORDINATION: the granted-skill-quality wave may also touch these three souls;
    the downside here sits on a DEFENSIVE stat it does not edit. If the manifest runs
    four_generals BEFORE skill_quality (per the report note), later-wins leaves this
    downside intact (no field collision expected)."""
    # dysnomion (spirit): the lawless anarch keeps no discipline -> reckless, exposed
    _downside(db, 'dysnomion', 'characterDefensiveAbility', {'n': -25.0, 'e': -35.0, 'l': -45.0})
    # makaria (poison): the blessed-death soul saps the bearer's own vigor
    _downside(db, 'makaria', 'characterLife', {'n': -90.0, 'e': -130.0, 'l': -180.0})
    # trophonios (flame): the oracle's fire runs hot and burns the bearer's own
    # energy. NOTE the shipping soul ALREADY carries +fire resist (defensiveFire =
    # 32/41/51 n/e/l, byte-verified) - writing a negative onto that field would
    # OVERWRITE the signature upside, not ADD a downside (spec 5.1: "touch ONLY the
    # one ADDED downside field", keep the upsides intact). So the downside rides
    # characterMana (max energy; base 0.0 on the record -> purely additive), the
    # spec's own "-characterEnergy" alternative. The +fire-res upside is preserved.
    _downside(db, 'trophonios', 'characterMana', {'n': -40.0, 'e': -60.0, 'l': -80.0})
    print("  8. general-soul enrichment: light amgoz downsides on dysnomion/makaria/"
          "trophonios (name/skill/augments untouched)")


def _downside(db, base, field, tiers):
    for t in 'nel':
        p = r'records\item\equipmentring\soul\machae\%s_soul_%s.dbr' % (base, t)
        r = mono._find_record(db, p)
        if not r:
            print("     WARN: %s soul %s missing; downside skipped" % (base, t))
            continue
        _setf(db, r, field, tiers[t], F)
        db._modified.add(r)


# ── 9. Text tags (spec §8; no em dashes; NO general-soul tags - they ship) ────
def _set_tags(db, tags):
    tags['tagSVCMonsterHadesMarshal'] = '{^r}Menoetes, Marshal of the Dead'
    tags['tagSVCSoulHadesMarshal'] = "{^F}Marshal's Command"
    tags['tagSVCSoulHadesMarshalDESC'] = (
        'The marshal Hades set over his three generals, wreathed in his lord\'s black '
        'smoke. His soul calls Menoetes himself back from death to march at the '
        'bearer\'s side, though the weight of his command slows their own stride.')
    tags['tagSVCSummonHadesMarshal'] = 'Summon Menoetes, Marshal of the Dead'
    # the six honor guards (amgoz V9 machae phonetics + role hook; spec §8)
    tags['tagSVCGuardDysA'] = '{^r}Ravok the Lawless ~ Machae Reaver'
    tags['tagSVCGuardDysB'] = '{^r}Sethuun ~ Machae Soul-Warden'
    tags['tagSVCGuardMakA'] = '{^r}Bhikru the Bilespitter ~ Machae Venomancer'
    tags['tagSVCGuardMakB'] = '{^r}Nakoth ~ Machae Plague-Ward'
    tags['tagSVCGuardTroA'] = '{^r}Kharzun the Ember ~ Machae Pyre-Ward'
    tags['tagSVCGuardTroB'] = '{^r}Voreth ~ Machae Cinder-Reaver'
    print("  9. tags: marshal (name/soul/desc/summon) + 6 guards; NO general-soul tags "
          "(they ship at tagSoulName248/249/250)")


# ── 10. Fail-loud resolution self-check (the spec §6.4 refs-resolve proof) ────
def _self_check(db):
    problems = []

    def res(p):
        return mono._find_record(db, p) is not None

    # every new skill/monster/pool/proxy/soul record exists
    created = (list(_SUMMON.values()) + [_MARSHAL_MUSTER, _MARSHAL, _MARSHAL_SUMMON,
               _MARSHAL_POOL, _MARSHAL_PROXY, _MARSHAL_YARD_POOL, _MARSHAL_YARD_PROXY]
               + [p for pair in _GUARD.values() for p in pair]
               + list(_GUARD_POOL.values()) + list(_GUARD_PROXY.values())
               + _MARSHAL_PETS
               + [r'records\item\equipmentring\soul\svc_uber\hadesmarshal_soul_%s.dbr' % t
                  for t in 'nel'])
    for p in created:
        if not res(p):
            problems.append("created record missing: %s" % p)

    # each general's new skill refs resolve + muster spawnObjects resolve
    for g in 'abc':
        if not res(_SUMMON[g]):
            problems.append("summon skill missing: %s" % _SUMMON[g])
        if not res(_ARCHER[g]):
            problems.append("archer skin missing: %s" % _ARCHER[g])
    # the marshal muster spawns real archer skins
    spawn = db.get_field_value(_MARSHAL_MUSTER, 'spawnObjects') or []
    for sp in (spawn if isinstance(spawn, list) else [spawn]):
        if sp and not res(sp):
            problems.append("marshal muster spawnObject dangling: %s" % sp)
    # the marshal's shroud + orb + kit refs resolve
    for p in (_SHROUD_AURA, _SHROUD_FXPAK, _ORB04, _MARSHAL_MUSTER, _GROUNDBREAKER,
              _HADESBOLT, _SPIRITBOLT_RING, _LIFEDRAIN):
        if not res(p):
            problems.append("marshal kit/shroud ref missing: %s" % p)
    # generals still Quest-class + still drop their souls (quest-identity intact)
    for g, pair in _GEN.items():
        for rec in pair:
            r = mono._find_record(db, rec)
            cls = db.get_field_value(r, 'monsterClassification')
            cls = cls[0] if isinstance(cls, list) else cls
            if cls != 'Quest':
                problems.append("general %s no longer Quest-class (%s)" % (rec, cls))
            ch = db.get_field_value(r, 'chanceToEquipFinger2')
            ch = ch[0] if isinstance(ch, list) else ch
            if not ch or float(ch) <= 0:
                problems.append("general %s lost its soul drop (Finger2=%s)" % (rec, ch))

    if problems:
        for p in problems[:30]:
            print("  FOUR-GENERALS SELF-CHECK OFFENDER: %s" % p)
        raise SystemExit("four_generals self-check FAILED: %d problem(s)" % len(problems))
    print("  10. self-check OK: all new records resolve; generals stay Quest-class + "
          "keep their soul drops (quest identity intact)")
