"""tools/patches/bossarena.py - THE OLYMPIAN ARENA boss finish (registry module).

Aithon, the Ember-Crowned: the finished apex of SV's Boss Arena (the "Olympian
Arena" reached from the Helos hub traveler). SV shipped this arena as a rough,
never-play-tested blockout - a VISIBLE spawn Proxy (the "green FX blob" Will
saw), THREE identical unnamed "Satyr Shaman" bosses on a bespoke fire kit, a
Player-class debug mannequin left on the floor, and no framing. Our merge already
fixed SV's dead EnterVolume trigger (build_quest_files.py:_fix_bossarena_
entervolume); this wave finishes the ENCOUNTER without touching the quest.

RCA (read-only): docs/reports/b43_bossarena_rca.md - "NOT ported wrong; SV
under-built/never-finished". This module implements case (B): design + implement
a worthy singular named Olympian arena boss per amgoz1's voice, on the EXISTING
vetted arena fire kit + rig + controller (no new/untested mechanics; the mesh is
literally SatyrShamanStarterBoss.msh - SV's own placeholder starter boss).

Binding: WILL_DECISIONS_2026-07-11.md blanket mandate (best judgement + amgoz1 +
prefer creative/extreme, WHEN feasibility-vetted). amgoz1 voice: specs/
amgoz1_design_voice.md. FLAGGED FOR WILL'S DEV-TOUR VETO (see the report §DESIGN).

Contract (tools/patches/README.md): MODULE_NAME + apply(db, tags) on the SAME
db/tags the monolith built; the fail-loud gate battery runs LAST over everything.
Disjoint from every other module (the bossarena namespace is ours alone; ref-scan
proved boss_satyrshaman_55 is referenced ONLY by the arena pool, the pool ONLY by
the proxy, the proxy by NO record - only the untouched quest names it).

WHAT THIS DOES (all DB; the map lane owns the 0x05 floor changes, reported):
  1. PROXY (defensive; NOT the blob): b43-r2 rediagnosis - the quest-spawned Proxy is
     a STANDARD invisible spawner (1003 base proxies share its exact config), so it is
     NOT Will's "green FX blob" (round-1 misdiagnosed it). Hardened to fully non-
     rendering anyway (invisibleInWorld 1 + maxTransparency 1.0 + castsShadows 0); pool
     function untouched.
  1b. GRAY PLANES + GREEN GLOW (Will's other 2 arena complaints): hide the vestigial
     Elysium arena portals. portal_olympianarena1 (GridEntrance, quest-opened) is the
     only one that renders its Elysium mesh -> the gray flat-placeholder plane AND, when
     opened, the green grid-entrance glow. Both portals hidden (invisibleInWorld 1 +
     transparent + no shadow) WITHOUT touching grid function (player travels via the
     hub/return-NPC now).
  2. THE APEX (in place; "this arena's own restoration"): boss_satyrshaman_55 ->
     "Aithon, the Ember-Crowned": name, boss scale, an apex HP/resist wall, a
     persistent RING-OF-FLAME shroud (the proven Enslaver/Marshal charFxPak
     route - ringofflame_charfx is a shipped CharFxPak). maxTransparency LEFT at the
     0.5 template default (never ghostly; forcing 0.0 risked the dissolve-in - reverted
     per the vet). KEEPS the whole vetted fire kit (flame surge,
     volcanic orb + immolation/fragmentation, meteor, fire aura, boss globals,
     conversion immunity) + the bespoke controller_arenasatyrshaman + the rich
     on-death loot (staff/caster armor/relics/heart/formulae) = the boss-tier
     reward AT the center, on clear.
  3. HONOR GUARD: one new Ember Satyr Warden champion (am_champion_11 SatyrBrute
     clone, rebanded, given the arena fire aura + flame surge) so the arena is a
     FIGHT (apex + 2 escorts), not a lone stat-check.
  4. THE POOL: 1 guaranteed apex + 2 champion honor guard (spawnMax 3, champion
     2 -> guaranteed_mains = 1; the spawnMax-championMax>=1 law, asserted inline).
  5. THE SOUL (amgoz1's signature trophy - every boss drops its soul): a hand-
     crafted "{^F}Aithon, the Ember-Crowned Soul": his own fire-nova proc that
     ERUPTS when he is struck (temperament-matched retaliation controller), his
     volcanic-orb + fire-enchant augments, a beastman racial (mastery over his
     own kind), a dense fire/burn sheet, and the amgoz downside (reckless arena
     brawler: -defensive ability) plus the identity resist (he IS fire: cannot
     burn). NO prose lore (amgoz V5); FileDescription = region "Olympus". Drops at
     66% off the apex (repoints the boss's Finger2 from the shared darksatyrshaman
     soul, which 2 OTHER satyrs - bs_shaman_10 + bs_shaman_12 - still drop).

MAP + QUEST DELTA (reported, NOT here - build_section_surgery.py + build_quest_files.py,
edited in THIS wave separately):
  - REACHABILITY (b43-r2 CRITICAL fix): the arena fight sits on an isolated raised-dais
    navmesh island (comp#2, world y~27) 28u above the low floor (comp#1, y~0) with no
    walkable bridge. SV's Helos-traveler landing was on comp#1 (unreachable from the
    fight). Retarget the outbound landing + the in-arena return NPC ONTO comp#2 (south
    dais, local ~(132,104), 26u S of the boss spawn / outside the r20 trigger, surveyed
    100% clear) so the player materialises on the arena floor and the encounter is
    experienceable. Nothing here in the arz depends on it, but the landing is the whole
    reason this boss is now reachable.
  - remove the malepc01 mannequin (0x05 inst22) + a ring of 6 orange fire-glow lights
    framing the fight floor, all on-mesh comp#2 (survey in the report).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # tools/ on path
import apply_svc_patches as M  # the monolith: helpers + gate-registry globals

MODULE_NAME = 'Aithon, the Ember-Crowned (Olympian Arena boss finish)'

S, F, I = M.DATA_TYPE_STRING, M.DATA_TYPE_FLOAT, M.DATA_TYPE_INT

# ── The arena chain (all present in build38; ref-scan proved the containment) ──
_PROXY = r'records\proxies custom\bossarena\boss_satyrshaman.dbr'          # quest-spawned Proxy (standard invisible spawner)
_POOL = r'records\proxies custom\bossarena\pools\satyr_shaman_01.dbr'      # ProxyPool (spawned 3 bosses)
_BOSS = r'records\creature\monster\bossarena\boss_satyrshaman_55.dbr'      # the apex (upgraded in place)

# ── The arena's own Elysium portals (SV-native; hidden this wave - see 1b) ─────
_PORTAL_ENTRANCE = r'records\quests\portal_olympianarena1.dbr'             # GridEntrance (quest-opened; the ONE that renders a mesh)
_PORTAL_RETURN = r'records\quests\portal_olympianarena2.dbr'              # GridExitOneWay (2 placed returns; already invisibleInWorld=1)

# ── Honor-guard champion (new, our bossarena namespace) ───────────────────────
_CHAMP = r'records\creature\monster\bossarena\ember_satyr_warden_55.dbr'
_CHAMP_DONOR = r'records\creature\monster\satyr\am_champion_11.dbr'         # SatyrBrute01 Champion (in-rig)

# ── FX shroud (proven charFxPak route; ringofflame is a shipped CharFxPak.tpl) ─
_SHROUD_FXPAK = r'records\effects\earth\ringofflame\ringofflame_charfx.dbr'

# ── Arena fire kit (all vetted, shipped; used by the apex + the honor guard) ──
_SK_FIRE_AURA = r'records\skills\monster skills\auras\damage_arenafirebonus.dbr'
_SK_FLAMESURGE = r'records\skills\monster skills\attack_projectile\arena_flamesurge.dbr'
_SK_ARMOR = r'records\skills\monster skills\defense\armor_passive.dbr'

# ── Soul design (amgoz1 voice) ────────────────────────────────────────────────
_SOUL_BASE = 'aithon_embercrown'
_SOUL_TAG = 'tagSVCSoulAithon'
_MON_TAG = 'tagSVCMonsterAithon'
_CHAMP_TAG = 'tagSVCMonsterEmberWarden'


def apply(db, tags):
    sf = db.set_field

    # ── fail-loud donor/target existence (exact paths; has_record is exact) ──
    need = [_PROXY, _POOL, _BOSS, _CHAMP_DONOR, _SHROUD_FXPAK,
            _PORTAL_ENTRANCE, _PORTAL_RETURN,
            _SK_FIRE_AURA, _SK_FLAMESURGE, _SK_ARMOR,
            M._SS_FIRE_NOVA, M._SK_VOLCANIC_ORB, M._SK_FIRE_ENCHANT, M._AC_FIRE_REACT]
    for p in need:
        if not db.has_record(p):
            raise SystemExit(f'BOSSARENA: required record missing (exact): {p}')

    # ── 1. PROXY (defensive hardening; NOT the confirmed blob) ────────────────
    # b43 r2 rediagnosis: this proxy is a STANDARD invisible spawner. 1003 base-game
    # proxies carry the identical mesh (satyrmage01) + baseTexture (Proxy01_Patrol.tex)
    # + maxTransparency 0.5 + NO invisibleInWorld, and none render as a blob in play
    # (the engine hides proxy meshes at runtime). So the proxy is NOT Will's "green FX
    # blob" (round-1 misdiagnosed it; the vet was right). Kept as cheap belt-and-braces
    # hardening only - add invisibleInWorld=1 (the definitive hide) on top of round-1's
    # transparency/shadow off. Refs kept valid; the pool/spawn function is untouched.
    sf(_PROXY, 'invisibleInWorld', 1)
    sf(_PROXY, 'maxTransparency', 1.0)
    sf(_PROXY, 'castsShadows', 0)
    db._modified.add(_PROXY)

    # ── 1b. GRAY PLANES + GREEN GLOW: hide the vestigial Elysium arena portals ─
    # Will's OTHER two arena complaints. The placed return portals (portal_olympianarena2,
    # GridExitOneWay x2) already ship invisibleInWorld=1. portal_olympianarena1
    # (GridEntrance, opened on level-load by bossarena.qst STEP-1) is the ONE portal that
    # renders its Elysium_from_TOJ mesh (no invisibleInWorld) -> the leading suspect for
    # BOTH the "giant gray untextured plane" (its flattexture01/flatbumptexture01 flat
    # placeholder) AND the "green FX blob" (an OPEN Elysium grid-entrance glow). The player
    # now arrives via the Helos traveler (b43-r2 dais landing) and leaves via the in-arena
    # return NPC, so SV's own entrance/return portals are vestigial. Hide BOTH meshes
    # (invisibleInWorld + fully transparent + no shadow) WITHOUT touching grid function
    # (Action_OpenDynGridEntrance still runs; GridExitOneWay still teleports if walked in).
    # DB-only; the arena's own portals = this arena's own restoration. (Caveat in the
    # report: if gray planes persist, the source is the Olympus STRUCTURES / SceneryOlympus
    # mount - unlikely, since the mod's Helos + Garden Olympus areas render textured -
    # Will's in-game tiebreaker: are the ring columns marble?)
    for _portal in (_PORTAL_ENTRANCE, _PORTAL_RETURN):
        sf(_portal, 'invisibleInWorld', 1)
        sf(_portal, 'maxTransparency', 1.0)
        sf(_portal, 'castsShadows', 0)
        db._modified.add(_portal)

    # ── 2. THE APEX: boss_satyrshaman_55 -> Aithon, the Ember-Crowned ─────────
    B = _BOSS
    sf(B, 'description', _MON_TAG)
    # (b43 r2: maxTransparency LEFT at the template default 0.5 - it never rendered ghostly
    #  [33k base records share 0.5]; forcing 0.0 fixed nothing and risked suppressing the
    #  ambushDissolveTexture=cloud.tex spawn-in fade. Reverted per the vet.)
    sf(B, 'scale', 1.9)                           # visibly the apex (was 1.5)
    sf(B, 'actorHeight', 2.5)
    # apex HP wall (a singular showcase boss; still SCALES to player level via the
    # quest limit window, so this is the base at his charLevel). Was [27.5k,35.8k,44k]
    # per-boss x3; a single apex at [42k,54k,66k] + 2 escorts ~= the old total.
    sf(B, 'characterLife', [42000.0, 54000.0, 66000.0])
    sf(B, 'characterLifeRegen', [30.0, 60.0, 100.0])
    # a real fire-boss resistance wall (Monster.tpl defensive fields). He IS fire:
    # cannot burn (identity resist, amgoz), high fire resist; a physical/pierce wall.
    sf(B, 'defensiveFire', 80.0)
    sf(B, 'defensiveBurn', 100.0)                 # he is living fire - cannot be burned
    sf(B, 'defensiveLife', 40.0)
    sf(B, 'defensivePhysical', 25.0)
    sf(B, 'defensivePierce', 35.0)
    # persistent ring-of-flame shroud (proven Enslaver/Marshal charFxPakRunningNames
    # route; a shipped CharFxPak). He is wreathed in his own volcanic fire.
    sf(B, 'charFxPakRunningNames', [_SHROUD_FXPAK], S)
    db._modified.add(B)
    # (kit, controller, sounds, ambush dissolve, and the full on-death loot table
    #  are all LEFT INTACT - they are the vetted arena content + the boss-tier reward.)

    # ── 3. HONOR GUARD: Ember Satyr Warden (SatyrBrute clone + arena fire) ────
    db.clone_record(_CHAMP_DONOR, _CHAMP)
    sf(_CHAMP, 'description', _CHAMP_TAG)
    sf(_CHAMP, 'monsterClassification', 'Champion')
    sf(_CHAMP, 'charLevel', [50, 64, 72])          # banded just under the apex (matches the arena tier)
    sf(_CHAMP, 'characterLife', [9000.0, 13000.0, 17000.0])
    sf(_CHAMP, 'characterLifeRegen', [12.0, 24.0, 40.0])
    sf(_CHAMP, 'scale', 1.15)
    sf(_CHAMP, 'defensiveFire', 50.0)
    sf(_CHAMP, 'defensiveBurn', 60.0)
    # keep the donor's dual-weapon melee (skillName1); add the arena fire aura +
    # a flame-surge special so the wardens read as fire satyrs, not vanilla brutes.
    sf(_CHAMP, 'skillName2', _SK_FIRE_AURA)
    sf(_CHAMP, 'initialSkillName', _SK_FIRE_AURA)
    sf(_CHAMP, 'specialAttackSkillName', _SK_FLAMESURGE)
    sf(_CHAMP, 'specialAttackChance', 40.0)
    # wardens are honor guard, not soul-droppers (soul-leak law: only the named
    # apex drops the arena soul). Clear any inherited finger-2 soul loot.
    sf(_CHAMP, 'chanceToEquipFinger2', 0.0)
    db._modified.add(_CHAMP)

    # ── 4. THE POOL: 1 guaranteed apex + 2 champion honor guard ───────────────
    P = _POOL
    sf(P, 'spawnMin', 3)
    sf(P, 'spawnMax', 3)
    sf(P, 'name1', _BOSS)                           # the apex (unchanged path, upgraded record)
    sf(P, 'nameChampion1', _CHAMP)
    sf(P, 'championChance', 100.0)
    sf(P, 'championMin', 2)
    sf(P, 'championMax', 2)
    db._modified.add(P)
    # spawnMax - championMax >= 1 LAW (asserted inline; NOT registered in the
    # global spawn-eligibility gate because this QUEST boss intentionally scales
    # to player level - its limit_quest window [Normal 29-36] is BELOW his L55, by
    # SV design - so the gate's (B) level<=window check would false-fail).
    _spawn_max = db.get_field_value(P, 'spawnMax')
    _champ_max = db.get_field_value(P, 'championMax')
    _spawn_max = _spawn_max[0] if isinstance(_spawn_max, list) else _spawn_max
    _champ_max = _champ_max[0] if isinstance(_champ_max, list) else _champ_max
    if (_spawn_max - _champ_max) < 1:
        raise SystemExit(
            f'BOSSARENA: champion-crowd-out - guaranteed main slots = '
            f'{_spawn_max - _champ_max} (spawnMax={_spawn_max}, championMax={_champ_max}); '
            f'the apex would never spawn. Need spawnMax - championMax >= 1.')

    # ── 5. THE SOUL: {^F}Aithon, the Ember-Crowned Soul (amgoz1 signature) ────
    # His own fire-nova proc, wired to ERUPT when he is struck (temperament-matched
    # retaliation: flamefragmentnova_onattacked). Volcanic-orb + fire-enchant
    # augments (his real Earth/fire moves). Beastman racial (satyr - mastery over
    # his own kind). Dense fire + a lingering ember burn. amgoz downside: a reckless
    # arena brawler pays in defence (-defensiveAbility); identity resist: he IS fire
    # (defensiveBurn 100 on the ring - cannot be burned). NO prose (V5).
    def _st(t):
        m = {'n': 0.62, 'e': 0.82, 'l': 1.0}[t]
        r = lambda v: round(v * m, 1)
        lvl = {'n': 4, 'e': 5, 'l': 6}[t]
        aug = {'n': 3, 'e': 4, 'l': 5}[t]
        return {
            **M._bmp(t),
            'itemSkillName': (S, M._SS_FIRE_NOVA), 'itemSkillLevel': (I, lvl),
            'itemSkillAutoController': (S, M._AC_FIRE_REACT),   # erupt-on-attacked (his temperament)
            'augmentSkillName1': (S, M._SK_VOLCANIC_ORB), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, M._SK_FIRE_ENCHANT), 'augmentSkillLevel2': (I, aug),
            'racialBonusRace': (S, 'Beastman'), 'racialBonusPercentDamage': (F, r(50.0)),
            # a brawny, fast satyr champion
            'characterLife': (F, r(260.0)), 'characterLifeModifier': (F, r(10.0)),
            'characterStrengthModifier': (F, r(10.0)),
            'characterOffensiveAbility': (F, r(80.0)),
            'characterAttackSpeedModifier': (I, int(r(12))),
            # fire signature (his volcanic kit, on the ring)
            'offensiveFireMin': (F, r(60.0)), 'offensiveFireMax': (F, r(100.0)),
            'offensiveFireModifier': (I, int(r(40))),
            'offensiveSlowBurnMin': (F, r(40.0)), 'offensiveSlowBurnDurationMin': (F, 3.0),
            'offensiveFireLeechMin': (F, r(12.0)),
            # identity resist (he IS fire) + the amgoz downside (reckless brawler)
            'defensiveFire': (F, r(45.0)), 'defensiveBurn': (F, 100.0),
            'characterDefensiveAbilityModifier': (F, -r(8.0)),
        }
    tiers = [{'diff': t, 'itemLevel': il, 'stats': _st(t)}
             for t, il in (('n', 50), ('e', 64), ('l', 72))]
    souls = M._create_soul(db, _SOUL_BASE, _SOUL_TAG, tiers, monster=_BOSS, drop_rate=66.0)
    # amgoz FileDescription = region only (no "aithon_embercrown soul (N)" default,
    # no prose itemText). Overwrite the _create_soul default to the act/region word.
    for sp in souls:
        if db.has_record(sp):
            sf(sp, 'FileDescription', 'Olympus')
            db._modified.add(sp)

    # ── 6. Tags (Text.arc COUPLED with the arz; validate_tags must pass) ──────
    tags[_MON_TAG] = 'Aithon, the Ember-Crowned'
    tags[_CHAMP_TAG] = 'Satyr ~ Ember Warden'
    tags[_SOUL_TAG] = '{^F}Aithon, the Ember-Crowned Soul'

    print("  Olympian Arena: Aithon, the Ember-Crowned (satyr fire apex, scale 1.9, "
          "HP [42k,54k,66k], fire/burn wall, ring-of-flame shroud) + 2 Ember Satyr "
          "Warden honor guard (pool 1 apex + 2 champions) + proxy hardened invisible "
          "+ 2 Elysium portals hidden (gray-plane/green-glow) + {^F}Aithon Soul (fire-nova "
          "erupt-on-hit, volcanic/fire-enchant augments, Beastman racial, -def downside, "
          "66% off the apex, 2 satyrs keep the shared soul); tags set")
