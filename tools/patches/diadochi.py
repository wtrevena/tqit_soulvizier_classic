"""diadochi - build37 uber boss: THE HELEPOLIS, TAKER OF CITIES.

The colossal black-smoke Siege Stryder of the Fields of the Diadochi (Elysium
entry field), the sixth placed-uber (the WAR-MACHINE archetype). A patches-
registry content module (tools/patches/README.md): it runs AFTER the monolith
content and BEFORE the whole gate battery (run_registry_gates), over the SAME
db/tags objects the monolith authored.

Spec: scratchpad/specs/diadochi_uberboss_spec.md (adversarially checked R2).
Binding decisions folded in (WILL_DECISIONS_2026-07-11.md, DIADOCHI section):
  * Signature nova  = hero_meteorlob1_ring (meteor-lob artillery ring), NOT the
    spec-default volcanicorb_nova - "reads as siege bombardment, more distinct".
  * S1 soul grant   = RAW leveler_turretattack (the LITERAL turret shell), made
    player-castable via the pcsafe strip (self-authored here, see _author_pcsafe).
  * Smoke           = amgoz's own 343_dark_smoke via a NEW svc_ashsmoke_charfxpak.
  * HP              = 42k single-form (extreme directive; honest-flagged in spec).

What this module authors (all NEW, collision-disjoint paths):
  um_helepolis_99            - the boss (Monster derive from um_leveler_43)
  svc_diadochi_striderguard_97 - the champion escort (elysium_ss derive), x2, no soul
  q_diadochi_lone (+pool)    - the lone-boss proxy (1 boss + 2 champions, LAW)
  q_yard_diadochi (+pool)    - the TESTHUB yard placement (@100%, local only)
  svc_diadochi_ashshroud     - the black-smoke body shroud (Skill_BuffSelfToggled)
  svc_ashsmoke_charfxpak     - its CharFxPak (renders 343_dark_smoke on the body)
  pcsafe\\leveler_turretattack - the anim-stripped turret grant for the soul
  diadochi_soul_{n,e,l}      - "{^F}Ash of the Funeral Games" (turret grant + ponderous downside)

The map lane owns the two PLACEMENTS (reported as map_deltas): q_diadochi_lone
into Elysian_Fields_03 north field, and q_yard_diadochi under SVC_TEST_HUB.
This module authors ONLY records + tags; it never touches the map tooling.

Robustness notes (why this module is self-contained regardless of registry order):
  * The pcsafe turret clone is authored HERE (not left to the castability wave),
    so the soul grant is player-castable whether the wave runs before, after, or
    not-at-all relative to this module (bootstrap-merged vs temp-hook gate build).
    It reproduces _fix_granted_skill_castability's exact output (clone + delete
    skillSpecialAnimationName), so the re-run of that wave (in run_registry_gates)
    sees an already-safe grant and leaves it byte-identical.
  * Registered kit clones (ash-shroud, charfxpak) are shape-safe (single existing-
    field repoints) and appended to _BOSS_KIT_CLONES so the clone-shape gate
    validates them. Both proxies are appended to _MOD_AUTHORED_SPAWN_PROXIES so
    the spawn-eligibility gate validates them. The evocative soul tag is added to
    _HAND_DESIGNED_SOUL_TAGS so the F6 soul-naming gate keeps its name (the
    sanctioned mechanism for hand-designed uber souls; spec section 4 + amgoz V8/V9).
"""
import sys
from pathlib import Path

# tools/ (sibling of this package) must be importable for apply_svc_patches +
# arz_patcher. The registry already puts tools/ on sys.path; this makes the
# module import-safe when run standalone (probes / temp-hook gate build) too.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import apply_svc_patches as A
from arz_patcher import DATA_TYPE_STRING as S, DATA_TYPE_FLOAT as F, DATA_TYPE_INT as I

MODULE_NAME = "Fields of the Diadochi uber (the Helepolis, Taker of Cities)"

# ── NEW record paths (authored by this module) ──────────────────────────────
_SR = r'records\xpack\creatures\monster\siegestrider'
BOSS       = _SR + r'\um_helepolis_99.dbr'
CHAMP      = _SR + r'\svc_diadochi_striderguard_97.dbr'
POOL       = r'records\drxmap\proxy\pools\q_diadochi_lone.dbr'
PROXY      = r'records\drxmap\proxy\q_diadochi_lone.dbr'
YARD_POOL  = r'records\drxmap\proxy\pools\q_yard_diadochi.dbr'
YARD_PROXY = r'records\drxmap\proxy\q_yard_diadochi.dbr'
ASHSHROUD  = r'records\skills\monster skills\buff_self\svc_diadochi_ashshroud.dbr'
ASHFXPAK   = r'records\skills\monster skills\buff_self\svc_ashsmoke_charfxpak.dbr'

# ── DONORS (all DB-verified present in the build36 work arz) ─────────────────
DONOR_BOSS   = _SR + r'\um_leveler_43.dbr'                 # Hero siege strider (the Leveler)
DONOR_CHAMP  = _SR + r'\elysium_ss_siegestrider_40.dbr'    # Elysium shade-strider (Champion)
DONOR_SHROUD = r'records\skills\monster skills\buff_self\bloodtoxeus_envenomweapon.dbr'  # mod's own Skill_BuffSelfToggled body shroud
DONOR_FXPAK  = r'records\drxcreatures\bloodwitch\skills\skilleffects\charfxpak_leinth_aura.dbr'  # CharFxPak
DARK_SMOKE   = r'records\effects\custom\343_dark_smoke.dbr'  # amgoz's SV dark-smoke EffectEntity
DONOR_POOL   = r'records\drxmap\proxy\pools\q_leinth_lone.dbr'
DONOR_PROXY  = r'records\drxmap\proxy\q_leinth_lone.dbr'
LIMIT        = r'records\proxies orient\limit_bloodtoxeus.dbr'   # no-cap [1..110] > L97
DIFFICULTY   = r'records\proxies orient\difficulty_04.dbr'
ORB          = r'records\item\containers\new\genericbossorb_04.dbr'  # apex boss orb (Proxy)
SIEGE_MESH   = r'XPack\Creatures\Monster\SiegeWalker\SiegeMonster01A.msh'

# ── KIT SKILLS (all exist; anim is 'Turret' or empty = siege-rig-castable) ──
SK_TURRET   = r'records\skills\monster skills\attack_projectile\leveler_turretattack.dbr'   # anim 'Turret'
SK_LASER    = r'records\skills\monster skills\attack_projectile\leveler_laserburst.dbr'     # empty
SK_MISSILE  = r'records\skills\monster skills\attack_projectile\leveler_missile.dbr'        # empty
SK_FIRESPIT = r'records\xpack\skills\monsterskills\activeattackprojectile\siegewalker_firespit.dbr'   # empty
SK_METEOR   = r'records\xpack\skills\monsterskills\activeattackprojectile\hero_meteorlob1_ring.dbr'   # empty (WILL nova)
SK_PROXYSUM = r'records\skills\monster skills\summoning_pets\leveler_proxysummon.dbr'       # Skill_SpawnPet -> proxy_35, petLimit 8
SK_BLEEDIMM = r'records\xpack\skills\monsterskills\passive\ascacophus_bleeddamageimmunity.dbr'
SK_CONVIMM  = r'records\skills\boss skills\boss_conversionimmunity.dbr'
SK_GP_LEG   = r'records\skills\monster skills\globalproperties_legendary01.dbr'

# ── SOUL ─────────────────────────────────────────────────────────────────────
SOUL_BASE = 'diadochi'                                   # -> svc_uber\diadochi_soul_{n,e,l}.dbr
SOUL_TAG  = 'tagSVCSoulDiadochiAsh'
SOUL_GRANT_PCSAFE = A._PCSAFE_DIR + r'\leveler_turretattack.dbr'

# ── TAGS ─────────────────────────────────────────────────────────────────────
TAG_BOSS  = 'tagSVCMonsterHelepolis'
TAG_CHAMP = 'tagSVCMonsterStriderGuard'
TAG_HOARD = 'tagSVCDiadochiHoard'                        # R-131 / R-100 #16: his new chest

BAND = [58, 80, 97]                                      # charLevel N/E/L (EXTREME, below the L100 crown)
HP   = [24000.0, 32000.0, 42000.0]                       # WILL: keep 42k single-form


def _del_field(db, rec, name):
    """Delete a field entirely (field-absence parity), the monolith idiom used by
    _create_blood_toxeus_fx. Used for baseTexture (-> default siege skin) and the
    pcsafe anim strip."""
    fields = db.get_fields(rec)
    if not fields:
        return
    for key in [k for k in fields if k.split('###')[0] == name]:
        del fields[key]
    db._modified.add(rec)


def _author_pcsafe_turret(db):
    """Self-author pcsafe\\leveler_turretattack: clone the raw turret barrage and
    DELETE its 'Turret' special anim, exactly as _fix_granted_skill_castability
    would. This makes the soul's RAW-turret grant (WILL's literal turret shell)
    player-castable independent of when/whether the castability wave runs relative
    to this module. Idempotent: if the record already exists (wave ran first, or a
    re-run), we simply re-assert the anim is stripped."""
    clone = SOUL_GRANT_PCSAFE
    if not db.has_record(clone):
        if not db.clone_record(SK_TURRET, clone):
            raise SystemExit("diadochi: failed to clone leveler_turretattack -> pcsafe")
    _del_field(db, clone, 'skillSpecialAnimationName')
    return clone


def _soul_stats(diff):
    """S1 THE BOMBARDMENT: the engine's own turret barrage as an on-hit proc +
    a PONDEROUS amgoz downside + a dense WAR-MACHINE stat signature (physical
    siege guns + furnace fire + armor-piercing + siege-impact stun + armored hull).
    Laddered 0.6 / 0.82 / 1.0 (Vashkarr/Dorus soul cadence)."""
    m = {'n': 0.6, 'e': 0.82, 'l': 1.0}[diff]
    r = lambda v: round(v * m, 1)
    return {
        **A._bmp(diff),                                  # per-tier soul icon
        'FileDescription': (S, 'Hades'),                 # amgoz V5: the act/region word (matches leveler_soul)
        # ── the grant: the LITERAL turret barrage (raw leveler_turretattack,
        #    pcsafe-stripped so a PC can play it) fired on every hit ──
        'itemSkillName': (S, SOUL_GRANT_PCSAFE),
        'itemSkillLevel': (I, {'n': 4, 'e': 6, 'l': 8}[diff]),
        'itemSkillAutoController': (S, A._AC_ON_HIT),    # base_atself_onanyhit (Self controller: no autoTargetRadius dependency)
        # ── amgoz downside (mandatory, thematic): PONDEROUS. you fire like a
        #    siege gun and you move like one (Polyphemus -speed precedent, scaled
        #    up for an uber). Two coherent "siege-engine grind" penalties. ──
        'characterRunSpeedModifier': (F, {'n': -12.0, 'e': -15.0, 'l': -18.0}[diff]),
        'characterAttackSpeedModifier': (F, {'n': -6.0, 'e': -8.0, 'l': -10.0}[diff]),
        # ── upsides (war machine; dense per amgoz's exemplar bar) ──
        'characterStrength': (F, r(40.0)), 'characterStrengthModifier': (F, r(10.0)),
        'characterOffensiveAbility': (F, r(120.0)),
        'characterLife': (F, r(360.0)), 'characterLifeModifier': (F, r(10.0)),
        'offensivePhysicalMin': (F, r(80.0)), 'offensivePhysicalMax': (F, r(130.0)),
        'offensivePhysicalModifier': (F, r(40.0)),
        'offensiveFireMin': (F, r(45.0)), 'offensiveFireMax': (F, r(80.0)),   # the furnace
        'offensiveFireModifier': (F, r(25.0)),
        'offensivePierceRatioModifier': (F, r(20.0)),    # armor-piercing shells
        'offensiveStunMin': (F, 0.5), 'offensiveStunMax': (F, r(1.5)),        # siege impact staggers
        'offensiveStunChance': (F, r(18.0)),
        'characterDefensiveAbility': (F, r(70.0)),
        'defensivePhysical': (F, r(28.0)), 'defensiveFire': (F, r(25.0)),     # armored hull
        'defensivePierce': (F, r(22.0)),
    }


def apply(db, tags):
    sf = db.set_field

    # Fail-loud on any missing donor (the monolith idiom).
    for donor in (DONOR_BOSS, DONOR_CHAMP, DONOR_SHROUD, DONOR_FXPAK, DARK_SMOKE,
                  DONOR_POOL, DONOR_PROXY, LIMIT, DIFFICULTY, ORB, SK_TURRET,
                  SK_LASER, SK_MISSILE, SK_FIRESPIT, SK_METEOR, SK_PROXYSUM,
                  SK_BLEEDIMM, SK_CONVIMM, SK_GP_LEG):
        if not db.has_record(donor):
            raise SystemExit("diadochi: REQUIRED donor missing: %s" % donor)

    # ── 1. THE BLACK SMOKE (Layer 1: the always-on body shroud) ──────────────
    # CharFxPak: clone the Leinth-aura pak; repoint its ONE particle ref to amgoz's
    # dark smoke. Skill_BuffSelfToggled: clone the mod's OWN Toxeus body-shroud;
    # repoint its ONE charFxPakSelfNames ref to the new pak. Both are single
    # existing-field repoints => shape-safe (registered below).
    db.clone_record(DONOR_FXPAK, ASHFXPAK)
    sf(ASHFXPAK, 'particleEffectNames', DARK_SMOKE)      # fx_leinth_aura_base -> 343_dark_smoke
    db._modified.add(ASHFXPAK)

    db.clone_record(DONOR_SHROUD, ASHSHROUD)
    sf(ASHSHROUD, 'charFxPakSelfNames', ASHFXPAK)        # charfxpak_leinth_aura -> our dark-smoke pak
    db._modified.add(ASHSHROUD)

    # ── 2. THE HELEPOLIS (boss). Monster derive from the Leveler (NOT a
    #    registered kit clone -> free to add resist/boss/effect fields). ────────
    db.clone_record(DONOR_BOSS, BOSS)
    M = BOSS
    sf(M, 'description', TAG_BOSS)
    sf(M, 'monsterClassification', 'Boss')               # souls drop; orb + soul key off Boss
    _del_field(db, M, 'baseTexture')                     # drop the Leveler's custom skin -> default siege skin
    sf(M, 'charLevel', list(BAND))                       # [58,80,97]
    sf(M, 'characterLife', list(HP))                     # [24000,32000,42000] (WILL: keep 42k)
    sf(M, 'characterLifeRegen', [20.0, 40.0, 70.0])
    sf(M, 'scale', 3.2)                                  # HUGE (map lane may dial to 3.0/2.8 on the placement re-survey)
    # boss resistance wall (new FLOAT fields; a colossal armored war engine)
    sf(M, 'defensivePhysical', 30.0)
    sf(M, 'defensivePierce', 45.0)
    sf(M, 'defensiveFire', 35.0)
    sf(M, 'defensiveElementalResistance', 30.0)
    # the black-smoke identity + spawn/death smoke theatrics
    sf(M, 'initialSkillName', ASHSHROUD)                 # spawns already wreathed in walking black smoke
    sf(M, 'spawnEffect', DARK_SMOKE)                     # a smoke burst as the furnaces light
    sf(M, 'deathEffect', DARK_SMOKE)                     # a detonation of black smoke as it ruptures
    # the WAR-MACHINE kit. Leveler already gives skillName1=turret, 2=laser,
    # 3=bleed-immune, 4=conv-immune, 5=proxysummon, 10/11=globalprops N/E,
    # 12=hero_scaling. ADD missile/firespit/legendary-globalprops in FREE slots;
    # make the meteor-lob ring the SPECIAL. Every skill's anim is 'Turret' or empty.
    sf(M, 'skillName6', SK_MISSILE)
    sf(M, 'skillName7', SK_FIRESPIT)
    sf(M, 'skillName8', SK_GP_LEG)                       # legendary global-props (the Leveler capped at 72 never needed it)
    sf(M, 'specialAttackSkillName', SK_METEOR)           # the meteor-lob artillery ring (WILL's signature nova)
    sf(M, 'specialAttackChance', 50.0)                   # fires often (spec ~45-55): the field is swept by the bombardment
    # the boss orb on FINAL death (this boss is single-form -> its record is terminal)
    sf(M, 'treasureProxyName', ORB, S)                   # genericbossorb_04 (apex, like um_bloodcrow_50)
    sf(M, 'dropItems', 1, I)
    db._modified.add(M)

    # ── 3. The champion escort (elysium shade-strider laddered to the band).
    #    Monster derive (only existing-field overrides). Champion, NO soul. ─────
    db.clone_record(DONOR_CHAMP, CHAMP)
    sf(CHAMP, 'description', TAG_CHAMP)
    sf(CHAMP, 'monsterClassification', 'Champion')
    sf(CHAMP, 'charLevel', list(BAND))                   # laddered beside the boss (native strider caps at 71)
    sf(CHAMP, 'characterLife', [10000.0, 14000.0, 19000.0])   # a lesser siege strider (2 of them < the boss's pool)
    sf(CHAMP, 'scale', 2.4)                              # bigger than the reenactment striders (2.0), smaller than the boss (3.2)
    sf(CHAMP, 'chanceToEquipFinger2', 0.0)               # NO soul drop (only the Helepolis drops it)
    db._modified.add(CHAMP)

    # ── 4. Lone-boss pool: 1 boss + 2 GUARANTEED champion escorts. The corrected
    #    championChance LAW: guaranteed mains = spawnMax - championMax = 3-2 = 1. ─
    def _pool(pool_path, desc):
        db.clone_record(DONOR_POOL, pool_path)
        sf(pool_path, 'FileDescription', desc)
        sf(pool_path, 'name1', BOSS, S)
        sf(pool_path, 'name2', BOSS, S)
        sf(pool_path, 'name3', BOSS, S)
        sf(pool_path, 'nameChampion1', CHAMP, S)
        sf(pool_path, 'nameChampion2', CHAMP, S)
        sf(pool_path, 'nameChampion3', '', S)            # clear the leinth clone's 3rd champion (Vashkarr fix)
        sf(pool_path, 'weightChampion1', 50, I)
        sf(pool_path, 'weightChampion2', 50, I)
        sf(pool_path, 'weightChampion3', 0, I)
        sf(pool_path, 'spawnMin', 3, I)
        sf(pool_path, 'spawnMax', 3, I)
        sf(pool_path, 'championChance', 100.0, F)
        sf(pool_path, 'championMin', 2, I)
        sf(pool_path, 'championMax', 2, I)
        db._modified.add(pool_path)

    _pool(POOL, 'Helepolis (main) + 2 Diadochi strider-guard champion escorts')

    # ── 5. Proxy (q_leinth_lone precedent): the boss + escorts, no-cap limit,
    #    siege silhouette preview, chanceToRun 100. Map lane injects it. ────────
    def _proxy(proxy_path, pool_ref):
        db.clone_record(DONOR_PROXY, proxy_path)
        sf(proxy_path, 'mesh', SIEGE_MESH)               # preview silhouette = a strider (not the blood-witch)
        sf(proxy_path, 'scale', 3.2)
        sf(proxy_path, 'pool1', pool_ref)
        sf(proxy_path, 'chanceToRun', 100.0, F)          # always run the pool (Dorus/Propontis/Broodmother precedent)
        sf(proxy_path, 'difficultyLimitsFile', LIMIT)    # limit_bloodtoxeus [1..110] > the boss's L97 band -> NO downscale
        sf(proxy_path, 'difficultyEquationFile', DIFFICULTY)
        sf(proxy_path, 'placementExtents', 4.0)          # room for the scale-3.2 colossus
        db._modified.add(proxy_path)

    _proxy(PROXY, POOL)

    # ── 5b. R-131 / R-100 #16 - THE HOARD HE NEVER HAD ────────────────────────
    # Will, verbatim: "the machine uber boss destroyer of cities ... doesnt drop a
    # chest". He never did: b37 shipped him with a soul + the apex orb and no hoard
    # at all, so this is a GAP being closed, not a design being reversed.
    #
    # Built by the SAME two monolith helpers the other five placed ubers use, so the
    # Helepolis lands on the identical chain rather than inventing a mechanism:
    #   _svc_build_dedicated_hoard  -> loot table -> FixedItemContainer -> accessory pool
    #                                  (x3 difficulty tiers, Boss-locked, bespoke name)
    #   _svc_build_world_chest_proxy-> a standalone Class=Proxy container the MAP lane
    #                                  places, which is why _proxy() above deliberately
    #                                  leaves this boss's accessory tiers EMPTY.
    # ORDERING (checked, not assumed): the registry runs BEFORE run_registry_gates, and
    # _svc_wire_boss_hoard_chests + _svc_verify_world_chests both live inside that
    # battery - so a hoard authored here IS wired to its own bespoke loot table (R-251,
    # by name shape, which `svc_diadochihoard_<tier>` matches) and IS covered by the
    # world-chest invariant ('diadochi' is in _SVC_FIXED_UBER_CHESTS). It is also
    # authored EARLY ENOUGH in the registry that the loot-breadth and armour-parity
    # modules still widen it. Falls back to the shared Obsidian pool if a donor is
    # missing, exactly like the monolith callers, so a donor gap degrades to "a hoard"
    # rather than to "no chest again".
    _dia_hoard = A._svc_build_dedicated_hoard(db, 'diadochi', TAG_HOARD) or A._SVC_HOARD_POOL
    A._svc_build_world_chest_proxy(db, 'diadochi', _dia_hoard)

    # ── 6. THE SOUL - "{^F}Ash of the Funeral Games" (S1 the bombardment). The
    #    RAW turret barrage, made castable by the pcsafe strip authored above.
    #    _create_soul wires it onto the boss's Finger2 (66%, the bespoke-uber rate)
    #    and REPLACES the Leveler soul the donor pointed at. ──────────────────────
    _author_pcsafe_turret(db)
    tiers = [{'diff': t, 'itemLevel': il, 'stats': _soul_stats(t)}
             for t, il in (('n', 58), ('e', 80), ('l', 97))]
    A._create_soul(db, SOUL_BASE, SOUL_TAG, tiers, monster=BOSS, drop_rate=66.0)

    # ── 7. TESTHUB yard placement (REAL records; map lane injects under
    #    SVC_TEST_HUB only). Tuning the boss tunes the yard fight 1:1. ──────────
    _pool(YARD_POOL, 'YARD: Helepolis + 2 strider-guard escorts @100% (TESTHUB-only)')
    _proxy(YARD_PROXY, YARD_POOL)

    # ── 8. Tags (Text.arc) ────────────────────────────────────────────────────
    tags[TAG_BOSS] = '{^r}The Helepolis, Taker of Cities'
    tags[TAG_CHAMP] = '{^r}Diadochi Strider-Guard'
    # R-131 / R-100 #16: the hoard's player-visible name. Follows the shipped
    # "<Boss>'s <flavour>-Hoard" convention (Tantalus's Hoard / Ferryman's Toll-Hoard
    # / Ephialtes's Dread-Hoard) and reads straight off his own title - what a Taker
    # of Cities is standing on is the spoil of the cities he took.
    tags[TAG_HOARD] = "Helepolis's Spoil-Hoard"
    tags[SOUL_TAG] = '{^F}Ash of the Funeral Games'
    tags[SOUL_TAG + 'DESC'] = (
        'The great engine that took the cities of the Successor Wars and never '
        'powered down. Its soul turns your every strike into a rain of siege-fire, '
        'though the weight of it slows your stride to a siege-walker grind.')

    # ── 9. Register into the shared gate-input registries so the LAST-running
    #    gate battery (run_registry_gates) validates this module's content. All
    #    idempotent (guarded) in case apply() is ever re-entered in one process. ─
    for pair in ((DONOR_FXPAK, ASHFXPAK), (DONOR_SHROUD, ASHSHROUD)):
        if pair not in A._BOSS_KIT_CLONES:
            A._BOSS_KIT_CLONES.append(pair)              # clone-shape gate (B-TOXEUS-2)

    for spec in (
        {'proxy': PROXY, 'pool': POOL, 'main_monster': BOSS,
         'name': 'q_diadochi_lone (the Helepolis + 2 strider-guard escorts)'},
        {'proxy': YARD_PROXY, 'pool': YARD_POOL, 'main_monster': BOSS,
         'name': 'q_yard_diadochi (yard: the Helepolis + escorts @100%)'},
    ):
        if not any(s.get('proxy') == spec['proxy'] for s in A._MOD_AUTHORED_SPAWN_PROXIES):
            A._MOD_AUTHORED_SPAWN_PROXIES.append(spec)   # spawn-eligibility gate

    # The F6 soul-naming gate keeps a hand-designed uber soul's evocative name only
    # if its tag is in _HAND_DESIGNED_SOUL_TAGS (the sanctioned mechanism; spec 4).
    # The frozenset is immutable, so rebind the module attribute (the gate reads it
    # from this module's globals at call time, after this module runs).
    A._HAND_DESIGNED_SOUL_TAGS = frozenset(A._HAND_DESIGNED_SOUL_TAGS) | {SOUL_TAG}

    print("  diadochi: the Helepolis (Boss [58,80,97] HP 24/32/42k, scale 3.2, "
          "black-smoke shroud + meteor-lob nova + turret/laser/missile/firespit + "
          "drone muster) + 2 strider-guard champions + lone pool/proxy + apex orb "
          "+ '{^F}Ash of the Funeral Games' soul (pcsafe turret grant, ponderous "
          "downside) + TESTHUB yard; tags + gate registrations set. Map lane places it.")
