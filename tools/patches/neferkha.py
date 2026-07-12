"""tools/patches/neferkha.py - COLD TOMBS TIER-1 SET-PIECE (registry module).

Neferkha, the Rimebound Pharaoh: a frozen-necropolis boss encounter injected
into an already-reachable Egypt tomb (the broodmother-nest placement pattern,
NO new geometry, NO new entrance). Realizes the "Cold Tombs" concept as a
self-contained frost court in the Egyptian desert, where a death-priest bound
the cold of the underworld into the royal tombs so the dead would never rest.

Spec: specs/cold_tombs_finish_spec.md (Tier 1, adversarially checked).
Binding: WILL_DECISIONS_2026-07-11.md ("GO, Tier 1 set-piece MVP ... Neferkha
(default)"). amgoz1 voice: specs/amgoz1_design_voice.md.

Contract (tools/patches/README.md): MODULE_NAME + apply(db, tags), operating on
the SAME db/tags the monolith built. Runs AFTER the monolith; the fail-loud
gates run LAST over everything (nothing here escapes them). Every record is
authored in dependency order against REAL, byte-verified donor paths (probes:
tools/patches/_probe_neferkha_*.py) so the render / soul-augment / soul-summon-
identity / spawn-eligibility / boss-kit-clone-shape / MP-equation gates all pass.

DESIGN (mirrors _create_broodmother_nest exactly; the proven apex set-piece idiom):
  * Boss um_neferkha_99 DERIVES from um_khenti_31 (the shipped Egyptian frost-
    mummy Hero: MummyMelee01.msh + mummy_khenti.tex frost skin + a real cold kit
    freezingblast/khenti_iceshard/deathchillaura, and - decisively - the explicit
    unarmed/sHanded/dHanded RunAnim overrides that make a mummy summon-pet mobile
    past the D19 assert). Hero -> Boss, reband to an Egypt-superboss, cold wall,
    frost breath + iceshard + a hostile RAISE-COURT summon (uncapped frost-mummy
    churn, the broodmother brood-summon shape).
  * A short frost-court roster (frost-mummy melee + caster fodder, a Construct
    frozen tomb-guardian champion, a fast ice-wraith) placed as proxy pools.
  * The ONE summon soul (Neferkha earns it, Will's law): manual-cast summon_neferkha
    (Skill_SpawnPet, NO itemSkillAutoController) raising a friendly frost pharaoh;
    dense cold/vitality sheet with the amgoz downside (defensiveFreeze 100 - he IS
    the cold, cannot be frozen; a NEGATIVE run-speed - a frost-locked corpse is
    slow); 2 cold augments (drxcoldaura + drxdeathchillaura); racialBonus Undead.
  * Rimed Canopic Heart: a tiered N/E/L craft reagent (Frozen-Heart donor flipped
    torso -> head armor), guaranteed off the boss (Misc3 @100, difficulty-tiered)
    and off the frozen guardians (@15%).
  * TESTHUB yard placement (q_yard_ namespace) so the map lane can give Will a
    spot to fight + tune her 1:1. INERT on the canonical/Steam map.

MAP DELTA (reported, NOT applied here - the map tool is owned by the map lane):
  inject q_neferkha_lone + q_sarcophagus_{a..d} into a surveyed on-mesh Egypt
  Valley-of-the-Kings tomb interior (>=40u from native encounters, all 3
  tilesets, 100% clearance) and swap that pocket's lights blue; add the yard
  entry on the TESTHUB rig. See the module report for the proxy record paths.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # tools/ on path
import apply_svc_patches as M  # the monolith: helpers + the gate-registry globals

MODULE_NAME = 'neferkha'

# ── Bands / derivation ──────────────────────────────────────────────────────
_NK_BAND = [32, 50, 64]              # Egypt-superboss band (a notch above khenti Hero [31,53,69])
_FODDER_BAND = [26, 42, 56]          # frost-court fodder (below the boss)
_CHAMP_BAND = [30, 48, 62]           # frozen tomb-guardian champion escort
# The frost mummy skin proven to resolve (um_khenti_31 ships it -> render-safe).
_FROST_TEX = r'DRXTextures\creatures\mummy\mummy_khenti.tex'

# ── Monsters (records\creature\monster\neferkha\ - a DISTINCT namespace from the
#    pre-existing SVAERA records\creature\monster\coldtomb\ cold-zombie set) ────
_NK_BOSS = r'records\creature\monster\neferkha\um_neferkha_99.dbr'
_NK_BOSS_DONOR = r'records\creature\monster\mummy\um_khenti_31.dbr'          # frost-mummy Hero (cold kit + RunAnim overrides)
_NK_MUMMY = r'records\creature\monster\neferkha\um_frostmummy_28.dbr'        # Common melee fodder
_NK_MUMMY_DONOR = r'records\creature\monster\mummy\am_soldier_17.dbr'        # clean Egypt mummy Common (no soul)
_NK_MAGE = r'records\creature\monster\neferkha\um_frostmummymage_28.dbr'     # Common caster fodder (iceshard)
_NK_MAGE_DONOR = r'records\creature\monster\mummy\am_soldier_21.dbr'
_NK_GUARDIAN = r'records\creature\monster\neferkha\um_frostguardian_45.dbr'  # Construct Champion escort
_NK_GUARDIAN_DONOR = r'records\creature\monster\guardianstatue\am_guardianstatue_27.dbr'
_NK_WRAITH = r'records\creature\monster\neferkha\um_icewraith_28.dbr'        # Common fast harasser
_NK_WRAITH_DONOR = r'records\creature\monster\wraith\am_meleewraith_11.dbr'

# ── Hostile raise-court summon (yaoguai clone; boss-kit clone-shape invariant) ─
_NK_SUMMON = r'records\skills\boss skills\svc_neferkha_raisecourt.dbr'
_NK_SUMMON_DONOR = r'records\skills\boss skills\yaoguai_summonshadowstalkers.dbr'

# ── Court hatch pool + no-cap limit + lone pool (broodmother idiom) ───────────
_NK_HATCH_POOL = r'records\proxies egypt\pools\svc_neferkha_court.dbr'
_NK_HATCH_POOL_DONOR = r'records\proxies orient\pools\demon\firesprite_01_general06.dbr'
_NK_LIMIT = r'records\proxies egypt\limit_neferkha.dbr'
_NK_LIMIT_DONOR = r'records\proxies boss\herolimit_all.dbr'                  # base [1..75] -> bumped [1..110]
_NK_DIFFICULTY = r'records\proxies orient\difficulty_04.dbr'
_NK_POOL = r'records\drxmap\proxy\pools\svc_neferkha_lone.dbr'
_NK_POOL_DONOR = r'records\drxmap\proxy\pools\q_leinth_lone.dbr'
_NK_PROXY = r'records\drxmap\proxy\q_neferkha_lone.dbr'
_NK_PROXY_DONOR = r'records\drxmap\proxy\q_leinth_lone.dbr'
_NK_SARCO_PROXIES = [rf'records\drxmap\proxy\q_sarcophagus_{c}.dbr' for c in 'abcd']  # 4 hatch clusters

# ── Soul summon chain (friendly manual-cast raise of the frost pharaoh) ───────
_NK_SUMMON_SKILL = r'records\skills\soulskills\summon_neferkha.dbr'
_NK_PETS = [rf'records\skills\soulskills\pets\neferkha_{i}.dbr' for i in (1, 2, 3)]

# ── Rimed Canopic Heart reagent (Frozen-Heart donor, flipped to HEAD armor) ───
_NK_RELIC = {t: rf'records\item\animalrelics\svc_rimedcanopicheart\{t}_rimedcanopicheart.dbr'
             for t in ('01', '02', '03')}
_NK_RELIC_DONOR = {t: rf'records\item\animalrelics\{t}_act4_frozenheart.dbr'
                   for t in ('01', '02', '03')}
_NK_RELIC_LOOT = {t: rf'records\item\loottables\animalrelics\svc_rimedcanopicheart\{t}_rimedcanopicheart.dbr'
                  for t in ('01', '02', '03')}
_NK_RELIC_LOOT_DONOR = {t: rf'records\item\loottables\animalrelics\{t}_act3_yetifur.dbr'
                        for t in ('01', '02', '03')}
_NK_RELIC_LEVELREQ = {'01': 20, '02': 34, '03': 48}
# per-shard 5-arrays (Legendary 03; 02 ~0.66x; 01 ~0.4x). Cold + vitality; a
# canopic (embalming) reagent for the head, so a caster-leaning intelligence line.
_NK_RELIC_STATS = {
    '03': {'defensiveCold': [10.0, 20.0, 30.0, 40.0, 50.0],
           'characterLife': [50.0, 100.0, 150.0, 200.0, 250.0],
           'defensiveLife': [4.0, 8.0, 12.0, 16.0, 20.0],
           'characterIntelligence': [8.0, 16.0, 24.0, 32.0, 40.0]},
    '02': {'defensiveCold': [7.0, 14.0, 21.0, 28.0, 35.0],
           'characterLife': [33.0, 66.0, 99.0, 132.0, 165.0],
           'defensiveLife': [3.0, 6.0, 9.0, 12.0, 15.0],
           'characterIntelligence': [5.0, 10.0, 15.0, 20.0, 26.0]},
    '01': {'defensiveCold': [4.0, 8.0, 12.0, 16.0, 20.0],
           'characterLife': [20.0, 40.0, 60.0, 80.0, 100.0],
           'defensiveLife': [2.0, 4.0, 6.0, 8.0, 10.0],
           'characterIntelligence': [3.0, 6.0, 9.0, 12.0, 16.0]},
}
_NK_RELIC_SLOTS_ON = ('helmet',)                                   # head armor only
_NK_RELIC_SLOTS_OFF = ('bodyArmor', 'greaves', 'armband', 'bracelet', 'amulet', 'ring',
                       'sword', 'axe', 'mace', 'spear', 'bow', 'staff', 'shield')
_NK_RELIC_DROP_PCT = 15.0                                          # off the frozen guardians

# ── TESTHUB yard placement (q_yard_ namespace; REAL records; INERT canonically) ─
_NK_YARD_POOL = r'records\drxmap\proxy\pools\q_yard_neferkha.dbr'
_NK_YARD_PROXY = r'records\drxmap\proxy\q_yard_neferkha.dbr'

# ── Boss / court kit skills (ALL byte-verified present in the build36 arz) ─────
_SK_ICESHARD = r'records\skills\monster skills\attack_projectile\khenti_iceshard.dbr'
_SK_FREEZINGBLAST = r'records\skills\storm\freezingblast.dbr'
_SK_FREEZEBREATH = r'records\skills\boss skills\dragonliche_freezingbreath.dbr'
_SK_DEATHCHILLAURA = r'records\skills\spirit\deathchillaura.dbr'            # persistent frost aura (khenti default)
_SK_FROSTSLOW = r'records\skills\monster skills\passive_buffs\raptor_frostslow.dbr'
_SK_ARMOR = r'records\skills\monster skills\defense\armor_passive.dbr'
_SK_COLDBONUS = r'records\skills\monster skills\passive_buffs\bonusdamage_cold_+5perlevelx500.dbr'
_SK_CHANCEFREEZE = r'records\skills\monster skills\passive_buffs\chance_freeze.dbr'
_SK_CONSTRUCTRESIST = r'records\skills\monster skills\defense\construct_resists.dbr'
_SK_BOSSIMMUNITY = r'records\skills\boss skills\boss_conversionimmunity.dbr'
_SK_BOSSSCALING = r'records\skills\monster skills\passive_buffs\boss_scaling.dbr'
_SK_GP_N = r'records\skills\monster skills\globalproperties_normal01.dbr'
_SK_GP_E = r'records\skills\monster skills\globalproperties_epic01.dbr'
_SK_GP_L = r'records\skills\monster skills\globalproperties_legendary01.dbr'


def apply(db, tags):
    """Author the whole Neferkha frost-court DB side in dependency order and
    register every record with the monolith's fail-loud gate globals. Mirrors
    _create_broodmother_nest: clone donors, override existing fields only on
    kit clones, dtype-free set_field on clones (preserve each field's type),
    all refs existence-verified."""
    S, F, I = M.DATA_TYPE_STRING, M.DATA_TYPE_FLOAT, M.DATA_TYPE_INT
    sf = db.set_field

    # ── fail-loud donor existence (exact-path; has_record is exact, unlike the
    #    substring-matching _find_record) ──
    donors = [_NK_BOSS_DONOR, _NK_MUMMY_DONOR, _NK_MAGE_DONOR, _NK_GUARDIAN_DONOR,
              _NK_WRAITH_DONOR, _NK_SUMMON_DONOR, _NK_HATCH_POOL_DONOR,
              _NK_LIMIT_DONOR, _NK_POOL_DONOR, _NK_PROXY_DONOR,
              _SK_ICESHARD, _SK_FREEZINGBLAST, _SK_FREEZEBREATH, _SK_DEATHCHILLAURA,
              _SK_FROSTSLOW, _SK_ARMOR, _SK_COLDBONUS, _SK_CHANCEFREEZE,
              _SK_CONSTRUCTRESIST, _SK_BOSSIMMUNITY, _SK_BOSSSCALING,
              _SK_GP_N, _SK_GP_E, _SK_GP_L,
              M._SK_COLD_AURA, M._SK_DEATH_CHILL]
    for t in ('01', '02', '03'):
        donors += [_NK_RELIC_DONOR[t], _NK_RELIC_LOOT_DONOR[t]]
    for d in donors:
        if not db.has_record(d):
            raise SystemExit(f"NEFERKHA: donor missing (exact): {d}")

    def _clear_skill_slots_above(rec, keep):
        """Delete skillName slots above `keep` the donor carried (DELETE not
        blank, per the B-TOXEUS-2 empty-ref loader-abort law)."""
        ff = db.get_fields(rec)
        if not ff:
            return
        for key in [k for k in list(ff) if k.split('###')[0].startswith('skillName')]:
            base = key.split('###')[0]
            try:
                n = int(base[len('skillName'):])
            except ValueError:
                continue
            if n > keep:
                del ff[key]
        db._modified.add(rec)

    def _frost_common(path, donor, band, kit, caster_skill=None, tex=True):
        """Clone a clean Egypt mummy Common -> a frost-court fodder body: cold
        kit, frost skin, banded to the encounter. No soul loot (donors carry
        none -> the soul-leak gate stays satisfied)."""
        db.clone_record(donor, path)
        sf(path, 'description', 'tagSVCMonsterFrostMummy')
        sf(path, 'monsterClassification', 'Common')
        sf(path, 'charLevel', list(band))
        if tex:
            sf(path, 'baseTexture', _FROST_TEX)                # frost tint (proven to resolve)
        for i, sk in enumerate(kit, start=1):
            sf(path, f'skillName{i}', sk)
        _clear_skill_slots_above(path, len(kit))
        if caster_skill:
            sf(path, 'specialAttackSkillName', caster_skill)
            sf(path, 'specialAttackChance', 60.0)
        db._modified.add(path)

    # ── 1. Frost-court roster (fodder + champion + harasser) ──────────────────
    # frost-mummy melee: chance-freeze on hit + cold bonus damage + armor.
    _frost_common(_NK_MUMMY, _NK_MUMMY_DONOR, _FODDER_BAND,
                  [_SK_CHANCEFREEZE, _SK_COLDBONUS, _SK_ARMOR])
    # frost-mummy caster: hurls Khenti's ice shards.
    _frost_common(_NK_MAGE, _NK_MAGE_DONOR, _FODDER_BAND,
                  [_SK_ICESHARD, _SK_CHANCEFREEZE, _SK_COLDBONUS], caster_skill=_SK_ICESHARD)
    sf(_NK_MAGE, 'description', 'tagSVCMonsterFrostMummyMage')
    db._modified.add(_NK_MAGE)
    # frozen tomb-guardian (Construct champion escort): slow, armored, cannot be
    # frozen (it IS frost-bound). Keeps the GuardianStatue rig + default skin (a
    # frost guardian tex is not proven in-arc -> the cold read comes from the kit
    # + the blue lights, per the spec's render-fallback rule).
    db.clone_record(_NK_GUARDIAN_DONOR, _NK_GUARDIAN)
    sf(_NK_GUARDIAN, 'description', 'tagSVCMonsterFrostGuardian')
    sf(_NK_GUARDIAN, 'monsterClassification', 'Champion')
    sf(_NK_GUARDIAN, 'charLevel', list(_CHAMP_BAND))
    sf(_NK_GUARDIAN, 'characterLife', [1400.0, 2400.0, 3600.0])
    sf(_NK_GUARDIAN, 'scale', 1.25)
    sf(_NK_GUARDIAN, 'defensiveFreeze', 100.0)                 # frost-bound: cannot be frozen
    sf(_NK_GUARDIAN, 'defensiveCold', 60.0)
    for i, sk in enumerate([_SK_ARMOR, _SK_CONSTRUCTRESIST, _SK_CHANCEFREEZE, _SK_COLDBONUS], start=1):
        sf(_NK_GUARDIAN, f'skillName{i}', sk)
    _clear_skill_slots_above(_NK_GUARDIAN, 4)
    db._modified.add(_NK_GUARDIAN)
    # ice-wraith (Common fast harasser): the speed contrast to the slow mummies.
    db.clone_record(_NK_WRAITH_DONOR, _NK_WRAITH)
    sf(_NK_WRAITH, 'description', 'tagSVCMonsterIceWraith')
    sf(_NK_WRAITH, 'monsterClassification', 'Common')
    sf(_NK_WRAITH, 'charLevel', list(_FODDER_BAND))
    sf(_NK_WRAITH, 'defensiveCold', 50.0)
    # keep the wraith's own disruption kit; add cold passives
    for i, sk in enumerate([_SK_CHANCEFREEZE, _SK_COLDBONUS], start=2):
        sf(_NK_WRAITH, f'skillName{i}', sk)
    db._modified.add(_NK_WRAITH)

    # ── 2. Hostile RAISE-COURT summon (yaoguai clone; only existing fields
    #    changed -> loader-safe + boss-kit clone-shape invariant). Spawns PURE
    #    frost-mummy fodder (Common, no soul) so the churn is fodder, never a
    #    reagent-loot / over-tough flood; the guaranteed champion escorts come
    #    from the lone pool. burst 4 / cd 5 / petLimit 20 = "no cap" in spirit. ──
    db.clone_record(_NK_SUMMON_DONOR, _NK_SUMMON)
    sf(_NK_SUMMON, 'spawnObjects', [_NK_MUMMY])
    sf(_NK_SUMMON, 'petBurstSpawn', 4)
    sf(_NK_SUMMON, 'skillCooldownTime', 5.0)
    sf(_NK_SUMMON, 'petLimit', 20)
    db._modified.add(_NK_SUMMON)
    M._BOSS_KIT_CLONES.append((_NK_SUMMON_DONOR, _NK_SUMMON))

    # ── 3. NEFERKHA, THE RIMEBOUND PHARAOH (boss). Clone the Khenti frost-mummy
    #    Hero; upgrade Hero->Boss, reband to Egypt-superboss, cold resist wall,
    #    frost breath + iceshard + the raise-court summon. Keeps mummy_khenti.tex
    #    (frost skin) + khenti's RunAnim overrides (summon-pet mobility). ──
    db.clone_record(_NK_BOSS_DONOR, _NK_BOSS)
    B = _NK_BOSS
    sf(B, 'description', 'tagSVCMonsterNeferkha')
    sf(B, 'monsterClassification', 'Boss')
    sf(B, 'charLevel', list(_NK_BAND))
    sf(B, 'characterLife', [14000.0, 22000.0, 32000.0])
    sf(B, 'characterLifeRegen', [30.0, 60.0, 100.0])
    sf(B, 'scale', 1.7)                                        # visibly the pharaoh
    sf(B, 'actorHeight', 2.4)
    # a frost-locked corpse is SLOW - characterization via tradeoff (V1); do NOT
    # give him +speed. He is a ranged frost caster-summoner, so slowness fits. A
    # -10% modifier expresses "slow" without overriding the rig's tuned base
    # (never set an absolute characterRunSpeed here - the base unit is a small
    # float, not a percentage).
    sf(B, 'characterRunSpeedModifier', -10.0)
    # boss resistance wall (existing Monster.tpl defensive fields; he IS the cold)
    sf(B, 'defensiveLife', 100.0)
    sf(B, 'defensiveCold', 80.0)
    sf(B, 'defensiveFreeze', 100.0)
    sf(B, 'defensivePierce', 50.0)
    sf(B, 'defensivePhysical', 25.0)
    kit = [
        _SK_ICESHARD, _SK_FREEZINGBLAST, _SK_FREEZEBREATH, _NK_SUMMON,
        _SK_FROSTSLOW, _SK_ARMOR, _SK_COLDBONUS, _SK_BOSSIMMUNITY, _SK_BOSSSCALING,
        _SK_GP_N, _SK_GP_E, _SK_GP_L,
    ]
    for i, sk in enumerate(kit, start=1):
        sf(B, f'skillName{i}', sk)
    _clear_skill_slots_above(B, len(kit))
    sf(B, 'initialSkillName', _SK_DEATHCHILLAURA)              # persistent frost aura
    # AI rotation: raise the court OFTEN (the tomb churns even without the static
    # sarcophagi); iceshard + frost breath the offensive specials.
    sf(B, 'specialAttackSkillName', _NK_SUMMON)
    sf(B, 'specialAttackChance', 55.0)
    sf(B, 'specialAttack2SkillName', _SK_ICESHARD)
    sf(B, 'specialAttack2Chance', 45.0)
    sf(B, 'specialAttack3SkillName', _SK_FREEZEBREATH)
    sf(B, 'specialAttack3Chance', 45.0)
    db._modified.add(B)

    # ── 4. Sarcophagus hatch pool (firesprite clone; pure frost-court fodder,
    #    3-6 per cluster, no champion crowd-out). name mix reads as a rising
    #    court (mummies + a wraith). ──
    db.clone_record(_NK_HATCH_POOL_DONOR, _NK_HATCH_POOL)
    HP = _NK_HATCH_POOL
    sf(HP, 'FileDescription', 'Neferkha frost-court hatch (frost-mummies + wraith)')
    sf(HP, 'name1', _NK_MUMMY)
    sf(HP, 'name2', _NK_MAGE)
    sf(HP, 'name3', _NK_WRAITH)
    sf(HP, 'name4', _NK_MUMMY)
    sf(HP, 'spawnMin', 3); sf(HP, 'spawnMax', 6)
    sf(HP, 'championChance', 0.0); sf(HP, 'championMin', 0); sf(HP, 'championMax', 0)
    sf(HP, 'nameChampion1', '')
    db._modified.add(HP)

    # ── 5. No-cap [1..110] limit (clone base herolimit_all -> bump the max window
    #    to 110, the exact obsidian-limit recipe; contains the boss L64 + escort
    #    L62 with headroom). Build-order-independent (herolimit_all is base). ──
    db.clone_record(_NK_LIMIT_DONOR, _NK_LIMIT)
    for f in ('maxPlayerLevelEquationNormal', 'maxPlayerLevelEquationEpic',
              'maxPlayerLevelEquationLegendary'):
        sf(_NK_LIMIT, f, '110*1')
    sf(_NK_LIMIT, 'FileDescription', 'Neferkha frost-court no-cap limit [1..110]')
    db._modified.add(_NK_LIMIT)

    # ── 6. Lone-boss pool: 1 Neferkha + 2 guaranteed frozen-guardian escorts
    #    (spawnMax=3 / championMin=Max=2 -> 3-2 = 1 guaranteed main = the pharaoh;
    #    the spawnMax-championMax>=1 LAW holds). Clear the leinth clone-leftover
    #    3rd champion (Vashkarr/broodmother fix). ──
    def _fill_lone_pool(pool):
        db.clone_record(_NK_POOL_DONOR, pool)
        sf(pool, 'name1', _NK_BOSS); sf(pool, 'name2', _NK_BOSS); sf(pool, 'name3', _NK_BOSS)
        sf(pool, 'nameChampion1', _NK_GUARDIAN); sf(pool, 'nameChampion2', _NK_GUARDIAN)
        sf(pool, 'nameChampion3', '')
        sf(pool, 'weightChampion1', 50); sf(pool, 'weightChampion2', 50); sf(pool, 'weightChampion3', 0)
        sf(pool, 'spawnMin', 3); sf(pool, 'spawnMax', 3)
        sf(pool, 'championChance', 100.0); sf(pool, 'championMin', 2); sf(pool, 'championMax', 2)
        db._modified.add(pool)
    _fill_lone_pool(_NK_POOL)
    sf(_NK_POOL, 'FileDescription', 'Neferkha (main) + 2 frozen tomb-guardian escorts')

    def _make_proxy(proxy, pool_ref, extents, mesh_from=None, scale=None):
        db.clone_record(_NK_PROXY_DONOR, proxy)
        sf(proxy, 'pool1', pool_ref)
        sf(proxy, 'chanceToRun', 100.0)
        sf(proxy, 'difficultyLimitsFile', _NK_LIMIT)
        sf(proxy, 'difficultyEquationFile', _NK_DIFFICULTY)
        sf(proxy, 'placementExtents', float(extents))
        if mesh_from and db.has_record(mesh_from):
            m = db.get_field_value(mesh_from, 'mesh')
            m = m[0] if isinstance(m, list) else m
            if m and str(m).strip():
                sf(proxy, 'mesh', str(m))
        if scale is not None:
            sf(proxy, 'scale', float(scale))
        db._modified.add(proxy)

    # ── 7. The pharaoh placement (lone proxy) + the 4 sarcophagus hatch proxies. ─
    _make_proxy(_NK_PROXY, _NK_POOL, 3.5, mesh_from=_NK_BOSS, scale=1.7)
    for sarco in _NK_SARCO_PROXIES:
        _make_proxy(sarco, _NK_HATCH_POOL, 2.5, mesh_from=_NK_MUMMY, scale=1.0)

    # ── 8. The manual-cast Neferkha summon (3 permanent frost-pharaoh pets on the
    #    boss's own mummy rig, D19-safe via khenti's RunAnim overrides) + the
    #    player summon skill. Then NEUTRALIZE the pet's inherited HOSTILE raise-
    #    court summon (repoint every occurrence to a benign frost proc), so the
    #    friendly pet never spawns ENEMIES and carries no hostile spawner (the
    #    summon-pet skill-kit gate forbids one). The pet still casts frost. ──
    if not M._build_boss_summon(
            db, _NK_BOSS, _NK_PETS, _NK_SUMMON_SKILL,
            'tagSVCSummonNeferkha', 'tagSVCMonsterNeferkha',
            char_level=list(_NK_BAND), life=[9000.0, 14000.0, 20000.0],
            life_regen=[30.0, 60.0, 100.0],
            dmg_min=[60.0, 100.0, 150.0], dmg_max=[100.0, 160.0, 240.0], scale=1.5,
            loadout=M._mirror_source_loadout(db, _NK_BOSS)):
        raise SystemExit('NEFERKHA: summon_neferkha _build_boss_summon failed')
    _hostile = _NK_SUMMON.replace('/', '\\').lower()
    for p in _NK_PETS:
        if not db.has_record(p):
            continue
        ff = db.get_fields(p) or {}
        for k, tf in ff.items():
            for j, v in enumerate(list(tf.values)):
                if isinstance(v, str) and v.replace('/', '\\').lower() == _hostile:
                    tf.values[j] = _SK_ICESHARD               # benign frost proc, never a hostile spawner
        sf(p, 'specialAttackSkillName', _SK_ICESHARD)
        sf(p, 'specialAttackChance', 40.0)
        db._modified.add(p)

    # ── 9. THE SOUL (amgoz1 voice, the ONE summon). Dense cold/vitality sheet +
    #    2 thematic cold augments (Cold Aura + Death Chill Aura) + the amgoz
    #    downside pair: defensiveFreeze 100 (he IS the cold, cannot be frozen) AND
    #    a NEGATIVE run-speed (you move like the frost-locked dead - Medusa/
    #    Polyphemus precedent). racialBonus Undead (mastery over his own kind).
    #    Grants the MANUAL summon (_wire_summon_soul strips any inherited
    #    controller -> a pet BUTTON). 66% Finger2, ONLY on the pharaoh. ──
    def _nk_stats(t):
        m = {'n': 0.6, 'e': 0.82, 'l': 1.0}[t]
        r = lambda v: round(v * m, 1)
        lvl = {'n': 3, 'e': 4, 'l': 5}[t]
        return {
            **M._bmp(t),
            'augmentSkillName1': (S, M._SK_COLD_AURA), 'augmentSkillLevel1': (I, lvl),
            'augmentSkillName2': (S, M._SK_DEATH_CHILL), 'augmentSkillLevel2': (I, lvl),
            'racialBonusRace': (S, 'Undead'), 'racialBonusPercentDamage': (F, r(50.0)),
            'characterLife': (F, r(320.0)), 'characterLifeModifier': (F, r(12.0)),
            'characterLifeRegen': (F, r(10.0)),
            'characterIntelligence': (F, r(45.0)), 'characterIntelligenceModifier': (F, r(8.0)),
            'characterManaModifier': (F, r(12.0)),
            'characterOffensiveAbility': (F, r(80.0)),
            'characterSpellCastSpeedModifier': (I, int(r(15))),
            'offensiveColdMin': (F, r(55.0)), 'offensiveColdMax': (F, r(90.0)),
            'offensiveColdModifier': (I, int(r(35))),
            'offensiveLifeMin': (F, r(35.0)), 'offensiveLifeMax': (F, r(60.0)),
            'offensiveLifeModifier': (I, int(r(25))),
            'offensiveSlowColdMin': (F, r(55.0)), 'offensiveSlowColdDurationMin': (F, 3.0),
            'offensiveSlowRunSpeedMin': (F, r(30.0)), 'offensiveSlowRunSpeedDurationMin': (F, 2.0),
            'offensiveLifeLeechMin': (F, r(22.0)),
            'defensiveFreeze': (F, 100.0),                    # signature: cannot be frozen
            'characterRunSpeedModifier': (F, -10.0),          # downside: the frost-locked dead are slow
            'defensiveCold': (F, r(45.0)), 'defensiveLife': (F, r(22.0)),
            'characterDefensiveAbility': (F, r(55.0)),
        }
    nk_tiers = [{'diff': t, 'itemLevel': il, 'stats': _nk_stats(t)}
                for t, il in (('n', 32), ('e', 50), ('l', 64))]
    nk_souls = M._create_soul(db, 'neferkha', 'tagSVCSoulNeferkha', nk_tiers,
                              monster=_NK_BOSS, drop_rate=66.0)
    M._wire_summon_soul(db, nk_souls, _NK_SUMMON_SKILL)        # manual: strip controller, level 1/2/3
    for sp in nk_souls:                                        # render the amgoz flavor (robust to registry order)
        if db.has_record(sp):
            sf(sp, 'itemText', 'tagSVCSoulNeferkhaDESC')
            db._modified.add(sp)

    # ── 10. The Rimed Canopic Heart reagent (Frozen-Heart donor flipped to HEAD
    #    armor; cold + vitality ladder; reuse the Frozen-Heart cold completion
    #    bonuses). Guaranteed off the boss (Misc3 @100, difficulty-tiered) + off
    #    the frozen guardians (@15%). Emberscale/Sepulchral charm idiom. ──
    for t in ('01', '02', '03'):
        charm = _NK_RELIC[t]
        db.clone_record(_NK_RELIC_DONOR[t], charm)            # cold torso relic -> retheme
        sf(charm, 'description', 'tagSVCRimedCanopicHeart')
        sf(charm, 'itemText', 'tagSVCRimedCanopicHeartDESC')
        sf(charm, 'FileDescription', 'Rimed Canopic Heart: cold resist + vitality (head armor)')
        sf(charm, 'levelRequirement', _NK_RELIC_LEVELREQ[t])
        for slot in _NK_RELIC_SLOTS_ON:
            sf(charm, slot, 1)
        for slot in _NK_RELIC_SLOTS_OFF:
            sf(charm, slot, 0)
        for fname, arr in _NK_RELIC_STATS[t].items():
            sf(charm, fname, list(arr))
        db._modified.add(charm)                               # bonusTableName inherited (Frozen-Heart cold bonuses)
        # loot table (clone the yeti-fur FixedWeight table; slot 1 = the charm)
        lt = _NK_RELIC_LOOT[t]
        db.clone_record(_NK_RELIC_LOOT_DONOR[t], lt)
        sf(lt, 'lootName1', charm)
        db._modified.add(lt)
    _relic_loot_arr = [_NK_RELIC_LOOT['01'], _NK_RELIC_LOOT['02'], _NK_RELIC_LOOT['03']]
    # guaranteed apex off the boss: repurpose the khenti-inherited low-value Misc3
    # (raremisc @0.6) -> the difficulty-tiered canopic heart @100 (soul stays Finger2).
    sf(B, 'chanceToEquipMisc3', 100.0)
    sf(B, 'lootMisc3Item1', list(_relic_loot_arr), S)
    sf(B, 'chanceToEquipMisc3Item1', 100, I)
    for j in (2, 3, 4, 5, 6):
        sf(B, f'chanceToEquipMisc3Item{j}', 0, I)
    db._modified.add(B)
    # the frozen guardians also drop it (@15% on their free Misc3 slot).
    gcur = db.get_field_value(_NK_GUARDIAN, 'lootMisc3Item1')
    if gcur in (None, '', 0, []):
        sf(_NK_GUARDIAN, 'lootMisc3Item1', list(_relic_loot_arr), S)
        sf(_NK_GUARDIAN, 'chanceToEquipMisc3', _NK_RELIC_DROP_PCT)
        sf(_NK_GUARDIAN, 'chanceToEquipMisc3Item1', 100, I)
        db._modified.add(_NK_GUARDIAN)

    # ── 11. TESTHUB yard placement (q_yard_ namespace; REAL records; 100%): the
    #    full court (pharaoh + 2 guardian escorts) so the map lane can give Will a
    #    yard spot to fight + tune 1:1. INERT on the canonical/Steam map (only the
    #    TESTHUB map places it). Registered in _MOD_AUTHORED_SPAWN_PROXIES. ──
    _fill_lone_pool(_NK_YARD_POOL)
    sf(_NK_YARD_POOL, 'FileDescription', 'YARD: Neferkha frost court (pharaoh + 2 escorts) @100% (TESTHUB-only)')
    _make_proxy(_NK_YARD_PROXY, _NK_YARD_POOL, 3.5, mesh_from=_NK_BOSS, scale=1.7)

    # ── 12. Register the two boss placements for the spawn-eligibility gate
    #    (champion-crowd-out spawnMax-championMax>=1 + limit-window containment). ─
    M._MOD_AUTHORED_SPAWN_PROXIES.extend([
        {'proxy': _NK_PROXY, 'pool': _NK_POOL, 'main_monster': _NK_BOSS,
         'name': 'q_neferkha_lone (Neferkha + 2 frozen-guardian escorts)'},
        {'proxy': _NK_YARD_PROXY, 'pool': _NK_YARD_POOL, 'main_monster': _NK_BOSS,
         'name': 'q_yard_neferkha (yard: Neferkha frost court @100%)'},
    ])

    # ── 13. Tags (Text.arc COUPLED with the arz; validate_tags must pass). ──────
    tags['tagSVCMonsterNeferkha'] = 'Neferkha ~ the Rimebound Pharaoh'
    tags['tagSVCMonsterFrostMummy'] = 'Rimed Tomb-Servant'
    tags['tagSVCMonsterFrostMummyMage'] = 'Rimed Tomb-Priest'
    tags['tagSVCMonsterFrostGuardian'] = 'Frozen Tomb-Guardian'
    tags['tagSVCMonsterIceWraith'] = 'Tomb-Chill Wraith'
    tags['tagSVCSummonNeferkha'] = 'Raise Neferkha, the Rimebound Pharaoh'
    tags['tagSVCSoulNeferkha'] = '{^F}Neferkha, the Rimebound Pharaoh Soul'
    tags['tagSVCSoulNeferkhaDESC'] = (
        'Torn from Neferkha, the pharaoh a death-priest sealed in the cold of the '
        'underworld so he would never truly die. The frost gave him no rest, only '
        'ice. Call him forth to raise his rimed court at your side, and the chill '
        'of the tomb answers with him.')
    tags['tagSVCRimedCanopicHeart'] = 'Rimed Canopic Heart'
    tags['tagSVCRimedCanopicHeartDESC'] = (
        'The frost-preserved heart of a tomb-king, sealed in a canopic jar against '
        'decay. Can enhance head armor only.')

    print("  Neferkha Frost Court: boss (Khenti frost-mummy rig, band [32,50,64], "
          "HP [14k,22k,32k], cold wall, -10% run) + uncapped raise-court summon "
          "(burst 4/cd 5/petLimit 20) + frost-mummy/mage/guardian/ice-wraith roster "
          "+ hatch pool + no-cap limit + lone pool (pharaoh + 2 guardian escorts) + "
          "1 lone proxy + 4 sarcophagus proxies + manual Neferkha Soul (66% Finger2, "
          "cold augments, defensiveFreeze, -run downside, Undead racial) + guaranteed "
          "tiered Rimed Canopic Heart (Misc3@100 boss / 15% guardian) + TESTHUB yard; tags set")
