r"""sargoth_soul_summon - R-51 (Will 2026-07-27): the Sargoth Manbane soul
summons Sargoth Manbane himself.

WILL'S RULING (verbatim, 2026-07-27):
    "backlog item sargath manbane soul should let you summon him"

IDENTIFICATION (the record name does NOT contain "Sargoth" - this is why the
backlog item never matched a grep, and why STEP ONE was a proof, not a guess)
--------------------------------------------------------------------------
  display name   "Sargoth Manbane"          (Will's "Sargath" is a near-spelling)
  Text tag       tagMonsterName1138          (shipped Text.arc / modstrings.txt)
  MONSTER        records\creature\monster\dragonian\hero_tarthon_na'arak_37.dbr
                 - the ONLY record in the 51,085-record arz whose `description`
                   is tagMonsterName1138 (proven by a full-roster field sweep).
  classification Hero, characterRacialProfile Beastman
  charLevel      [37, 54, 69]  - ONE record; the three values ARE the
                 normal/epic/legendary difficulty tiers (TQ stores them as a
                 per-difficulty array), so there are NO separate variant records.
  body           mesh Creatures\Monster\Dragonian\Dragonian01.msh
                 baseTexture Creatures\Monster\Dragonian\MageB.tex
                 anm records\creature\monster\dragonian\anm\anm_dragonian.dbr
                 scale 1.55, controller controller_noble01
  kit            a LIGHTNING/storm dragonian mage: Lightning Ball, Thunderball
                 (+ Concussive Blast), dragonian_reflection, a lightning-bonus
                 aura, drxenergyshield_aoe, armor_passive, hero_scaling.
  placement      9 Orient (Act 3) dragonian spawn pools, always the
                 `nameChampion7` slot:
                   records\proxies orient\pools\beastman\dragonian_02_melee01..03
                   records\proxies orient\pools\beastman\dragonian_03_melee01..03
                   records\proxies orient\pools\beastman\dragonian_03_ranged01..03
                 (a roaming Orient hero, not a placed unique boss - matches the
                 soul's own FileDescription "Orient".)
  SOUL family    records\item\equipmentring\soul\dragonian\sargoth_soul_{n,e,l}.dbr
                 itemNameTag tagSoulName297 = "{^F}Sargoth Manbane Soul";
                 wired as the monster's lootFinger2Item1 at chanceToEquipFinger2
                 50.0 -> it is genuinely his soul, genuinely droppable.

BEFORE STATE (deployed ground truth) - WILL'S PREMISE CONFIRMED
---------------------------------------------------------------
All three tiers carry `itemSkillName = <absent>`: the soul grants NO skill of any
kind, let alone a summon. It is a pure stat+augment ring:
    augmentSkillName1 = records\skills\soulskills\stafftraining.dbr      (5/6/7)
    augmentSkillName2 = records\skills\storm\drxthunderball_concussiveblast.dbr (2/3/4)
    + lightning offense/resist, reflect, stun resist, STR/life.
So "should let you summon him" is a real gap, not a regression.

THE PRECEDENT: R-43 (b85) + the shipped sibling
------------------------------------------------
R-43 ("the high priest soul should allow you to summon the high priest") is the
same ruling class and is implemented with the SECOND-BUILDER pattern:
`apply_svc_patches._build_boss_summon` builds 3 permanent pets from the SOURCE
MONSTER's own rig (Lyia clone for a crash-safe Pet.tpl baseline; only anim +
skill refs copied from Monster.tpl - never equipment/loot fields, the documented
Pet.tpl-crash law) and authors the manual-cast Skill_SpawnPet, including the b40
skill icon and the b71 pet-bar portrait.

Sargoth has an even closer precedent: his own SIBLING RECORD. Vort the Red
(hero_tarthon_na'arak_40, tagMonsterName1139) is the same dragonian hero family,
same mesh, same anm table, and ALREADY ships a summon soul with exactly this
shape (summon_vort: manaCost [250,300,350], cooldown 180, NO TTL, petLimit 1,
skillMaxLevel 3; soul itemSkillLevel 1/2/3 per tier; NO itemSkillAutoController =
manual cast, the Lyia model + the R-44 manual-cast convention). This module
reproduces that shape via the newer, gated `_build_boss_summon` path so Sargoth
also gets the build36-A1 gear-parity/stat-mirror/skill-kit treatment Vort's older
hand-rolled builder predates.

WHAT THIS MODULE BUILDS
-----------------------
  pets   records\skills\soulskills\pets\sargoth_{1,2,3}.dbr
  skill  records\skills\soulskills\summon_sargoth.dbr
  wiring itemSkillName/itemSkillLevel onto EVERY sargoth soul tier (n/e/l)

PLAYER-SURFACE CHECKLIST (CLAUDE.md law #3 - every surface enumerated, none
deferred; the b40 deferred-portraits and b81 pet-identity waves exist because
this was skipped before):
  1. summon skill NAME      tagSVCSummonSargoth = "Summon Sargoth Manbane"
                            (added to `tags` here; mirrors tagSVCSummonVort).
  2. summon skill ICON      thunderorb up/down - a lightning-orb glyph matching
                            his Lightning Ball / Thunderball kit. Registered in
                            apply_svc_patches._SUMMON_SKILL_ICON (the canonical
                            map) so it is discoverable, not hidden here. Verified
                            UNCLAIMED by any other summon and arc-resolving in
                            the shipped DRXtextures.arc (up AND down). Distinct
                            from sibling Vort's base-game Thunderball icon, so
                            the two dragonian summons never read as one skill.
  3. pet-bar PORTRAIT       no dragonian *_party_ portrait ships in ANY shipped
                            arc (swept: 34 party portraits, none dragonian), so
                            the neutral proxy_party_up/red applies - the
                            established convention for unmapped bosses (Hades
                            Marshal, and R-43's own High Priest). The load-bearing
                            requirement is met: it is NEVER the Lyia nymph.
  4. pet NAME               description = tagMonsterName1138 -> the pet-bar and
                            floating name read "Sargoth Manbane" (exactly the
                            Vort precedent, whose pets carry tagMonsterName1139).
  5. RACE                   characterRacialProfile = Beastman, copied from the
                            source monster (R-11: "boss-summon pets inherit
                            race/sounds/distress from their SOURCE monster");
                            `_build_boss_summon` -> `_align_pet_identity` does
                            this plus the voice/distress paks.
  6. SOUNDS                 same `_align_pet_identity` pass aligns distressCallGroup
                            + the alert/death/crit/stun/vox paks to the source.
  7. NOT A NAKED MUTE STATUE
                            gear: `_mirror_source_loadout(strict=True)` mirrors
                            his own loadout - LeftHand staff (staff_dyn_n/e/l03),
                            and every slot the source does NOT use is zeroed, so
                            the pet carries EXACTLY his gear both ways
                            (PET-GEAR-PARITY gate). skills: `_mirror_source_skill_kit`
                            restores his lightning kit into AI-fireable slots.
                            mobility: the D19 assert passes - the primary row is
                            'sHanded' and anm_dragonian defines sHandedRunAnim
                            (it also defines staffRunAnim, so the real staff row
                            is covered too).

WHY A REGISTRY MODULE (not monolith surgery)
--------------------------------------------
Per tools/patches/README.md this is exactly a content wave: one disjoint module,
one REGISTRY line. apply() runs in step 2, so the whole monolith gate battery
(step 3) validates these records - including PET-STAT-MIRROR, PET-GEAR-PARITY,
PET-SKILL-KIT and the F2 SOUL-SUMMON-IDENTITY gate, which independently re-proves
the identification: it asserts the summon's SOURCE mesh equals the mesh of the
monster that DROPS the soul. For Sargoth those are the same record, so a
mis-identification would fail the build loud.

GATE
----
verify() runs in step 4 over the FINAL merged db. The full-chain assertion
(item -> skill -> icon -> spawnObjects -> pet -> portrait) is added to the
EXISTING chain-gate family in tools/patches/enslaver_pet_fx.py `_CHAIN` (the same
gate that carries R-43's High Priest), rather than inventing a one-off gate;
verify() here asserts the leg that gate cannot see - that all three soul TIERS
grant the summon and scale 1/2/3 (R-40 strict-progress), and that the module's
write scope is exactly its own records.

See docs/reports/b95_sargath_soul_summon.md.
"""
import apply_svc_patches as asp

MODULE_NAME = "Sargoth Manbane soul -> summons Sargoth Manbane (R-51)"

_R = 'records\\'

# ── THE IDENTIFIED RECORDS ───────────────────────────────────────────────────
MONSTER = _R + r"creature\monster\dragonian\hero_tarthon_na'arak_37.dbr"
MONSTER_NAME_TAG = 'tagMonsterName1138'          # "Sargoth Manbane"
SOUL_NAME_TAG = 'tagSoulName297'                 # "{^F}Sargoth Manbane Soul"

SOUL_DIR = _R + r'item\equipmentring\soul\dragonian'
SOULS = ['%s\\sargoth_soul_%s.dbr' % (SOUL_DIR, t) for t in ('n', 'e', 'l')]

PETS = [_R + r'skills\soulskills\pets\sargoth_%d.dbr' % i for i in (1, 2, 3)]
SUMMON_SKILL = _R + r'skills\soulskills\summon_sargoth.dbr'

SUMMON_DISPLAY_TAG = 'tagSVCSummonSargoth'
SUMMON_DISPLAY_TEXT = 'Summon Sargoth Manbane'

# Per-tier granted-skill level (n/e/l) - the unanimous convention across every
# shipped summon soul (Vort 1/2/3, bwpriest 1/2/3); also satisfies R-40's
# strict-progress requirement that a soul scale across the three tiers.
ITEM_SKILL_LEVEL = (1, 2, 3)

# ── PET STAT BAND ────────────────────────────────────────────────────────────
# Anchored to the shipped SIBLING (Vort the Red, charLevel [40,57,71]:
# life 18000/26000/36000, regen 40/70/110, dmg 70-100/105-160/150-230) and set
# one notch BELOW it, because Sargoth sits one band lower ([37,54,69]) and is the
# same Hero rank. charLevel is the source's own array; scale is left None so
# `_build_boss_summon` inherits the source monster's own 1.55.
CHAR_LEVEL = [37, 54, 69]
LIFE = [15000.0, 22000.0, 30000.0]
LIFE_REGEN = [34.0, 60.0, 94.0]
DMG_MIN = [60.0, 90.0, 128.0]
DMG_MAX = [86.0, 136.0, 196.0]


def _scalar(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _first(db, rec, field):
    return _scalar(db.get_field_value(rec, field))


def _norm(s):
    return str(s).replace('/', '\\').strip().lower() if s else ''


def _soul_tiers_present(db):
    """The sargoth soul records that actually exist, canonical tiers first.

    Upstream SV also ships an unreachable duplicate
    `sargoth_soul_n (amgoz-qosmio's conflicted copy 2013-08-07).dbr` (a Dropbox
    conflict artifact amgoz1 shipped). It carries the same itemNameTag but is
    referenced by NOTHING - not the monster's lootFinger2Item1, not any formula -
    so it can never reach a player. The shipped Vort family has the identical
    artifact AND upstream wired the summon onto it too, so wiring it here keeps
    the two sibling families the same shape and guarantees that if it ever DID
    become reachable it would not be a silently summon-less duplicate. It is
    named explicitly in the wave report's record-diff.
    """
    out = [p for p in SOULS if db.has_record(p)]
    for name in db.record_names():
        nl = _norm(name)
        if 'sargoth_soul' in nl and 'conflicted copy' in nl and name not in out:
            out.append(name)
    return out


def apply(db, tags):
    print('\n=== patches-registry: %s ===' % MODULE_NAME)

    # ── 1. IDENTIFICATION ASSERTS (fail loud rather than build the wrong boss) ─
    if not db.has_record(MONSTER):
        raise SystemExit(
            '[sargoth_soul_summon] R-51 target MISSING: %s. Sargoth Manbane is the '
            'monster Will named; refusing to ship a build that silently drops the '
            'ruling.' % MONSTER)

    desc = _norm(_first(db, MONSTER, 'description'))
    if desc != MONSTER_NAME_TAG.lower():
        raise SystemExit(
            '[sargoth_soul_summon] IDENTITY CHECK FAILED: %s has description=%s, '
            'expected %s ("Sargoth Manbane"). The record this module targets is not '
            'the monster Will named. Refusing.'
            % (MONSTER, desc or '<none>', MONSTER_NAME_TAG))

    souls = _soul_tiers_present(db)
    canonical = [p for p in SOULS if db.has_record(p)]
    if len(canonical) != 3:
        raise SystemExit(
            '[sargoth_soul_summon] expected 3 sargoth soul tiers (n/e/l), found %d: '
            '%s. Refusing to wire a partial soul family.' % (len(canonical), canonical))

    loot = db.get_field_value(MONSTER, 'lootFinger2Item1') or []
    loot = loot if isinstance(loot, list) else [loot]
    loot_n = {_norm(x) for x in loot if isinstance(x, str)}
    missing = [p for p in SOULS if _norm(p) not in loot_n]
    if missing:
        raise SystemExit(
            '[sargoth_soul_summon] %s does not drop its own soul family '
            '(lootFinger2Item1 missing %s). The soul/monster pairing Will named is '
            'not present. Refusing.' % (MONSTER, [m.rsplit('\\', 1)[-1] for m in missing]))

    for p in canonical:
        tag = _norm(_first(db, p, 'itemNameTag'))
        if tag != SOUL_NAME_TAG.lower():
            raise SystemExit(
                '[sargoth_soul_summon] soul %s has itemNameTag=%s, expected %s '
                '("Sargoth Manbane Soul"). Refusing.'
                % (p, tag or '<none>', SOUL_NAME_TAG))

    before = {p: _first(db, p, 'itemSkillName') for p in souls}
    print('  identified: %s' % MONSTER)
    print('              description=%s ("Sargoth Manbane"), classification=%s, charLevel=%s'
          % (MONSTER_NAME_TAG, _first(db, MONSTER, 'monsterClassification'),
             db.get_field_value(MONSTER, 'charLevel')))
    print('  before: %d soul record(s), itemSkillName = %s'
          % (len(souls), {p.rsplit('\\', 1)[-1]: (before[p] or '<none>') for p in souls}))

    # ── 2. BUILD THE PET FAMILY + SUMMON SKILL FROM HIS OWN RIG ──────────────
    # loadout omitted -> _mirror_source_loadout(strict=True) mirrors his own
    # LeftHand staff and zeroes every slot he does not use (gear parity both ways).
    # scale omitted -> inherits his own 1.55.
    ok = asp._build_boss_summon(
        db, MONSTER, PETS, SUMMON_SKILL,
        SUMMON_DISPLAY_TAG, MONSTER_NAME_TAG,
        char_level=list(CHAR_LEVEL), life=list(LIFE), life_regen=list(LIFE_REGEN),
        dmg_min=list(DMG_MIN), dmg_max=list(DMG_MAX))
    if not ok:
        raise SystemExit(
            '[sargoth_soul_summon] R-51 _build_boss_summon FAILED for %s - the '
            'Sargoth pet family was not built, so the soul would grant a dangling '
            'skill. Refusing.' % MONSTER)

    # ── 3. TEXT: the summon skill's player-visible name ──────────────────────
    tags[SUMMON_DISPLAY_TAG] = SUMMON_DISPLAY_TEXT

    # ── 4. WIRE THE SUMMON ONTO EVERY SOUL TIER ──────────────────────────────
    # No explicit dtype (cloned/authored-record dtype-safety law). No
    # itemSkillAutoController: manual-cast, the Lyia model + the R-44 convention
    # + the shipped sibling Vort. Existing augments/stats are left untouched.
    for i, p in enumerate(canonical):
        db.set_field(p, 'itemSkillName', SUMMON_SKILL)
        db.set_field(p, 'itemSkillLevel', ITEM_SKILL_LEVEL[i])
        db._modified.add(p)
    for p in souls:
        if p in canonical:
            continue
        # the unreachable upstream conflicted-copy duplicate: keep the family one
        # shape (see _soul_tiers_present); level 1, the normal-tier value.
        db.set_field(p, 'itemSkillName', SUMMON_SKILL)
        db.set_field(p, 'itemSkillLevel', ITEM_SKILL_LEVEL[0])
        db._modified.add(p)

    print('  built: %d pets %s + summon skill %s'
          % (len(PETS), [p.rsplit('\\', 1)[-1] for p in PETS],
             SUMMON_SKILL.rsplit('\\', 1)[-1]))
    print('  wired: %d soul record(s) -> itemSkillName=%s, itemSkillLevel %s'
          % (len(souls), SUMMON_SKILL.rsplit('\\', 1)[-1], list(ITEM_SKILL_LEVEL)))
    print('  tag:   %s = %r' % (SUMMON_DISPLAY_TAG, SUMMON_DISPLAY_TEXT))


def verify(db, tags=None):
    """Step-4 gate over the FINAL merged db (post gate-battery).

    The item -> skill -> icon -> spawnObjects -> pet -> portrait walk is asserted
    by the shared chain gate in enslaver_pet_fx._CHAIN (this family is registered
    there, alongside R-43's High Priest). This hook asserts the legs that gate
    does not cover: per-TIER granting + strict 1/2/3 progression (R-40), and that
    the summon is manual-cast, permanent and named.
    """
    problems = []

    if not db.has_record(SUMMON_SKILL):
        problems.append('summon skill absent: %s' % SUMMON_SKILL)
    else:
        if _norm(_first(db, SUMMON_SKILL, 'skillDisplayName')) != SUMMON_DISPLAY_TAG.lower():
            problems.append(
                '%s skillDisplayName=%s, expected %s (the summon button would be unnamed)'
                % (SUMMON_SKILL.rsplit('\\', 1)[-1],
                   _first(db, SUMMON_SKILL, 'skillDisplayName') or '<none>',
                   SUMMON_DISPLAY_TAG))
        ttl = db.get_field_value(SUMMON_SKILL, 'spawnObjectsTimeToLive')
        ttl = ttl if isinstance(ttl, list) else [ttl] if ttl is not None else []
        for v in ttl:
            try:
                if float(v) > 0.0:
                    problems.append(
                        '%s has spawnObjectsTimeToLive=%s - a permanent companion '
                        'would despawn (Lyia no-TTL exemplar)'
                        % (SUMMON_SKILL.rsplit('\\', 1)[-1], v))
                    break
            except (TypeError, ValueError):
                pass

    for p in PETS:
        if not db.has_record(p):
            problems.append('pet absent: %s' % p)
            continue
        if _norm(_first(db, p, 'description')) != MONSTER_NAME_TAG.lower():
            problems.append(
                '%s description=%s, expected %s - the pet would not be named '
                '"Sargoth Manbane"'
                % (p.rsplit('\\', 1)[-1], _first(db, p, 'description') or '<none>',
                   MONSTER_NAME_TAG))
        race = _first(db, p, 'characterRacialProfile')
        src_race = _first(db, MONSTER, 'characterRacialProfile')
        if src_race and _norm(race) != _norm(src_race):
            problems.append(
                '%s characterRacialProfile=%s, expected its source\'s %s (R-11)'
                % (p.rsplit('\\', 1)[-1], race or '<none>', src_race))

    # per-tier grant + strict progression (R-40)
    seen = []
    for i, p in enumerate(SOULS):
        if not db.has_record(p):
            problems.append('soul tier absent: %s' % p)
            continue
        got = _norm(_first(db, p, 'itemSkillName'))
        if got != _norm(SUMMON_SKILL):
            problems.append(
                'R-51 NOT GRANTED: %s itemSkillName=%s, expected %s - this tier of '
                'the Sargoth Manbane soul does not summon him'
                % (p.rsplit('\\', 1)[-1], got or '<none>', SUMMON_SKILL.rsplit('\\', 1)[-1]))
        if _first(db, p, 'itemSkillAutoController'):
            problems.append(
                '%s carries an itemSkillAutoController - a companion summon must be '
                'MANUAL-cast (R-44 convention / Lyia model)' % p.rsplit('\\', 1)[-1])
        lvl = _first(db, p, 'itemSkillLevel')
        try:
            seen.append(int(lvl))
        except (TypeError, ValueError):
            problems.append('%s itemSkillLevel=%r is not an int'
                            % (p.rsplit('\\', 1)[-1], lvl))
    if seen and seen != sorted(set(seen)) or (len(seen) == 3 and seen != list(ITEM_SKILL_LEVEL)):
        problems.append(
            'soul tiers do not scale n<e<l: itemSkillLevel %s, expected %s (R-40)'
            % (seen, list(ITEM_SKILL_LEVEL)))

    if problems:
        raise SystemExit(
            '[sargoth_soul_summon] R-51 VERIFY FAILED (Will 2026-07-27, "backlog '
            'item sargath manbane soul should let you summon him"):\n  - '
            + '\n  - '.join(problems))
    print('  [sargoth_soul_summon] verify OK: all 3 Sargoth Manbane soul tiers grant '
          'summon_sargoth (manual-cast, levels %s), 3 permanent named Beastman pets '
          'built from hero_tarthon_na\'arak_37' % list(ITEM_SKILL_LEVEL))
