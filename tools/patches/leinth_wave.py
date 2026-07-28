r"""leinth_wave - b94 PART B: Leinth, the Blood Witch, becomes a real wall and
gains three new abilities, every one cloned from a PROVEN rig inside her OWN cult
family (records\drxcreatures\bloodwitch\...).

WILL'S ASK (paraphrase; the verbatim ruling is ledgered as R-71 in
docs/WILL_RULINGS.md): Leinth is too easy and her fight is one long attrition
sludge with nothing to react to. Make her stronger and give her more to do.

GROUND TRUTH (deployed arz, all three variants)
-----------------------------------------------
q_leinth_47 (charLevel 47;62;74), q_leinth_49 (49;64;76), q_leinth_50 (50;65;75);
all monsterClassification=Boss. Her passives ALREADY cap her where it does not
matter: skill14 zpassive_resists_bleedvitleechconvert_x10plvl @10 gives +100
bleed / +100 life / +100 convert / +100 life-leech / +100 mana-leech, and skill15
elementalresistance_10xlevel @3 gives +30 elemental. Net effective: bleed 100,
life 160, convert 100, elemental 50, stun 100 - and PHYSICAL 10, PIERCE 20,
POISON -15. Physical and pierce are the ONLY things that touch her, which is
exactly why a weapon build melts her while a caster respects her.

WHAT THIS MODULE CHANGES
------------------------
STATS (all three variants; the deliberate no-touch list is below)
  characterLife         32,481 -> 52,000 | 35,703 -> 57,000 | 38,924 -> 62,000 (+60%)
  defensivePhysical     10 -> 35    <- THE REAL LEVER
  defensivePierce       20 -> 45    <- THE REAL LEVER
  characterAttackSpeed  0.8 -> 1.0  (her casts actually land; still under the
                                     champions' 1.1)
  characterRunSpeed     1.0 -> 1.15 (she can reposition; far under the Enslaver's 1.5)
  characterLifeRegen    2 -> 10     (a life-leech witch should visibly heal)
  skillLevel13          1;4;7 -> 4;7;9   (cerberus_crackfire, HER EXISTING poison
                                     geysers: poison 800/850/950 and the 5%
                                     current-life component ON at every difficulty)

  DELIBERATELY NOT TOUCHED: defensivePoison stays -15. It is her documented amgoz1
  identity and the fight's counter-play (docs/amgoz1_design_voice.md). Neither is
  charLevel: she is the blood cave's main-path terminal boss at 74-76, NOT an
  uber, and pushing her to the champions' 100 would break the cave's curve and
  step on their role.

THE SUMMON CUT (b76 chumbi-freeze law)
  leinth_summon_uglies petBurstSpawn 4;6;8 -> 2;3;4 and petLimit 16 -> 6, plus the
  finite spawnObjectsTimeToLive the skill never had (the summon_caps b76
  precedent: a boss summon with no TTL never reaches a steady state). 16
  concurrent permanent chaff pets is exactly the density that froze the game in
  b76, and it is the least amgoz1-ish thing in her kit. The skill is NOT removed
  and NOT unwired - it still fires from specialAttack2, just at a sane density.

THREE NEW SKILLS - and why THREE, not four
------------------------------------------
The engine gives a Monster.tpl record exactly FIVE castable specialAttack slots
(specialAttack..specialAttack5; census over all 51,085 records: 3164/1602/894/300/
167 users, and only 3 stray specialAttack6 refs). Leinth already uses FOUR
(bloodboil, summon_uglies, bloodall_02, heatseeker), all of them her own bespoke
DRX kit. So there is exactly ONE free attack slot. The other AI-driven cast
mechanisms Monster.tpl actually supports are buffSelfSkillName (978 refs, 9 of
them SpawnPet/SpawnPetMonster, incl. a Boss) and dyingSkillName (541 refs, 18 of
them on Boss records). healSkillName is Skill_GiveBonus-only, buffOtherSkillName
is Skill_BuffOther-only and berserkSkillName is BuffSelfDuration-only, so none of
those can carry these donors.

That is 3 usable homes, so THREE new skills ship - each in the mechanism its CLASS
has precedent for - rather than a fourth that would have to displace one of her
own bespoke DRX skills (retirement protocol: player-facing content is not
displaced without Will).

  1. CRIMSON TITHE            -> skillName9  @ 8;14;20 + specialAttack5 @ 100
     donor: skills\disciple_bloodrain_bleedx50_vitx10.dbr
            (Skill_AttackProjectileAreaEffect; bloodofares_tearsofblood projectile,
             radius 8, 8s active, 30s cooldown, bleed to 1000, -25% total
             resistance, -50 defensive ability, 33% slow, 25 fumble, Crumple)
     Her own cult's Disciple blood-rain, promoted to the mistress. This is the
     single highest-value addition: the fight currently has NO telegraphed phase
     moment, and the 30s cooldown is what paces it (her four existing specials all
     sit at chance 100, so the module keeps that convention and lets the cooldown
     do the rate-limiting).

  2. CHOIR OF THE BLOODBORN   -> skillName16 @ 1;2;3 + buffSelfSkillName
     donor: skills\discipleboss_summon_melinoe.dbr (Skill_SpawnPet ->
            discipleboss_bladedancer), cut from petBurstSpawn 6 / petLimit 18 to
            2;3;4 / petLimit 6 and given a finite TTL (b76 law - the donor has
            none). Fewer, better, on-identity cult summons: a Blood Witch
            COMMANDING her cult instead of a chaff spawner.

  3. SANGUINE MIRE            -> skillName18 @ 1;2;3 + dyingSkillName
     donor: skills\leinth_skills\leinth_summon_uglies.dbr (HER OWN Skill_SpawnPet
            rig, the correct Monster-spawn shape) with spawnObjects repointed to
            her cult's own skills\seductress_bloodpuddle_monster.dbr, burst 3,
            petLimit 3, short TTL. When the Blood Witch falls, the floor of her
            sanctuary runs with blood. Fixes a genuine design hole (she has zero
            zone control today) at the one moment the player has a reason to move
            anyway - her death is also when the exit portal opens (PART C).

  amgoz1 bar: zero new art, zero new FX, zero new sound, nothing generic - every
  donor is an already-shipping record from her own blood-cult family.

STAGED-BUT-REJECTED (flagged, not silently chosen): DRX left
skills\leinth_skills\cerberus_acidpuddle_{summon,attack}.dbr wired to NOTHING in
her own folder, so they were plausibly her intended kit. They are POISON, and she
is the one boss in the mod with a -15 poison weakness; a poison-dealing,
poison-weak witch is thematically self-contradictory. Will's call - listed in the
wave report's open questions.

WHAT THIS MODULE DOES NOT TOUCH
-------------------------------
No loot field of any kind: chanceToEquipHead (her guaranteed lenithsveil),
chanceToEquipFinger2 (her 66% soul, the R-42 PLACED rate), every loot*Item* field
and treasureProxyName are snapshotted before and after and apply() fails loud if
any of them moved. No pool, no proxy, no placement, no map, no quest.

GATE
----
verify() runs in registry step 4 over the FINAL merged db and fails the build loud
unless every stat target holds on all three variants, the poison weakness is still
-15, each new skill sits in a skillName slot at level>=1 AND is wired to its cast
mechanism, every summon carries a finite TTL and a sane petLimit, her drop wiring
is untouched, and she still ranks BELOW the Enslaver on resists/speed (the mid
boss must never out-stat the uber). Planted negative test:
tools/debug/negtest_leinth_wave.py. See docs/reports/b94_leinth_wave.md.
"""
import apply_svc_patches as asp

MODULE_NAME = "Leinth the Blood Witch - buff + 3 cult abilities (R-71)"

_BW = 'records\\drxcreatures\\bloodwitch\\'
_LS = _BW + 'skills\\leinth_skills\\'
_BWS = _BW + 'skills\\'

VARIANTS = (
    _BW + 'q_leinth_47.dbr',
    _BW + 'q_leinth_49.dbr',
    _BW + 'q_leinth_50.dbr',
)

# The Enslaver: the uber Leinth must never out-stat (ordering invariant).
_ENSLAVER = asp._EN_BOSS

# ── STAT TARGETS ─────────────────────────────────────────────────────────────
LIFE = {
    VARIANTS[0]: 52000.0,   # was 32,481.26
    VARIANTS[1]: 57000.0,   # was 35,702.52
    VARIANTS[2]: 62000.0,   # was 38,923.78
}
PHYS = 35.0          # was 10  <- the real lever
PIERCE = 45.0        # was 20  <- the real lever
ATTACK_SPEED = 1.0   # was 0.8 (champions sit at 1.1)
RUN_SPEED = 1.15     # was 1.0 (Enslaver sits at 1.5)
LIFE_REGEN = 10.0    # was 2
POISON_KEEP = -15.0  # HER IDENTITY - asserted unchanged, never written

# cerberus_crackfire (her EXISTING poison geysers). skillMaxLevel is 10 but the
# per-level arrays carry only NINE entries (indices 0-8), so 9 is the highest
# in-range level - the design's "4;7;10" is capped to 4;7;9 for that reason.
# Effect: poison 800/850/950 and offensivePercentCurrentLifeMin 5% at every
# difficulty (it is 0 below index 3, which is why Normal currently has none).
GEYSER_SLOT = 13
GEYSER_LEVELS = [4, 7, 9]      # was [1, 4, 7]
GEYSER_SKILL = _LS + 'cerberus_crackfire.dbr'
GEYSER_MAX_INDEX = 9           # len(offensivePoisonMin) on the donor

# ── THE SUMMON CUT (b76) ─────────────────────────────────────────────────────
UGLIES = _LS + 'leinth_summon_uglies.dbr'
UGLIES_BURST = [2, 3, 4]       # was [4, 6, 8]
UGLIES_LIMIT = 6               # was 16
UGLIES_TTL = 45.0              # was absent (permanent) - b76 summon_caps law

# ── THE THREE NEW SKILLS ─────────────────────────────────────────────────────
TITHE = _LS + 'svc_leinth_crimson_tithe.dbr'
TITHE_DONOR = _BWS + 'disciple_bloodrain_bleedx50_vitx10.dbr'
TITHE_SLOT = 9
TITHE_LEVELS = [8, 14, 20]
TITHE_SPECIAL = '5'            # specialAttack5* - the ONE free attack slot
TITHE_CHANCE = 100.0           # matches her four existing specials; the donor's
                               # 30s skillCooldownTime is what paces it

CHOIR = _LS + 'svc_leinth_choir_bloodborn.dbr'
CHOIR_DONOR = _BWS + 'discipleboss_summon_melinoe.dbr'
CHOIR_SLOT = 16
CHOIR_LEVELS = [1, 2, 3]
CHOIR_BURST_HEAD = [2, 3, 4]   # levels 1/2/3; the rest of the 20-entry array
                               # is padded with the level-3 value
CHOIR_LIMIT = 6                # was 18
CHOIR_TTL = 45.0               # was absent - b76 law
CHOIR_PET = _BWS + 'discipleboss_bladedancer.dbr'

MIRE = _LS + 'svc_leinth_sanguine_mire.dbr'
MIRE_DONOR = UGLIES            # her OWN Skill_SpawnPet rig (Monster spawn shape)
MIRE_SLOT = 18
MIRE_LEVELS = [1, 2, 3]
MIRE_BURST = [3]
MIRE_LIMIT = 3
MIRE_TTL = 8.0                 # short: a death flourish, never a loot blocker
MIRE_PET = _BWS + 'seductress_bloodpuddle_monster.dbr'

NEW_SKILLS = (TITHE, CHOIR, MIRE)

# ── Text (player-surface checklist: every new skill gets a real name + flavour) ─
TAGS = {
    'tagSVCLeinthCrimsonTithe': 'Crimson Tithe',
    'tagSVCLeinthCrimsonTitheDESC':
        'The Blood Witch calls in the cave\'s debt. Her sanctuary weeps red, and '
        'everything beneath the rain is opened, slowed and made to bleed.',
    'tagSVCLeinthChoirBloodborn': 'Choir of the Bloodborn',
    'tagSVCLeinthChoirBloodbornDESC':
        'She does not shriek for rabble. She names her own, and the bladedancers '
        'of the Bloodborn step out of the dark to answer.',
    'tagSVCLeinthSanguineMire': 'Sanguine Mire',
    'tagSVCLeinthSanguineMireDESC':
        'What a Blood Witch holds, she keeps. When Leinth falls, the floor of the '
        'sanctuary drinks her and rises to take the rest.',
}

# ── the drop fields that MUST NOT move (scope proof) ────────────────────────
_DROP_PREFIXES = ('chanceToEquip', 'loot', 'treasureProxyName', 'dropItems')


def _v1(db, rec, field):
    v = db.get_field_value(rec, field)
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _fields(db, rec):
    out = {}
    ff = db.get_fields(rec)
    if not ff:
        return out
    for k, tf in ff.items():
        out.setdefault(k.split('###')[0], list(tf.values))
    return out


def _drop_snapshot(db, recs):
    snap = {}
    for r in recs:
        ff = _fields(db, r)
        snap[r] = {k: v for k, v in ff.items()
                   if any(k.startswith(p) for p in _DROP_PREFIXES)}
    return snap


def _require(db, rec, what):
    if not db.has_record(rec):
        raise SystemExit(
            "[leinth_wave] %s MISSING from the db: %s. Refusing to ship a build "
            "that silently drops this wave." % (what, rec))


def _clone_new(db, donor, dest, label):
    _require(db, donor, 'donor rig (%s)' % label)
    if db.has_record(dest):
        raise SystemExit(
            "[leinth_wave] %s already exists (%s) - another writer claimed this "
            "path. Refusing to overwrite." % (dest, label))
    db.clone_record(donor, dest)


def _free_slot(db, rec, slot, label):
    cur = _v1(db, rec, 'skillName%d' % slot)
    if isinstance(cur, str) and cur.strip():
        raise SystemExit(
            "[leinth_wave] %s: skillName%d is NOT free (holds %r) - %s would "
            "silently displace an existing skill." % (rec, slot, cur, label))


def apply(db, tags):
    print("\n=== patches-registry: %s ===" % MODULE_NAME)

    for v in VARIANTS:
        _require(db, v, 'Leinth variant')
    _require(db, GEYSER_SKILL, 'her geyser skill')
    _require(db, UGLIES, 'her ugly-summon skill')
    _require(db, CHOIR_PET, 'the Bloodborn bladedancer pet')
    _require(db, MIRE_PET, 'the blood-puddle monster')

    drops_before = _drop_snapshot(db, VARIANTS)

    # ── 1. the three new skill records ───────────────────────────────────────
    _clone_new(db, TITHE_DONOR, TITHE, 'Crimson Tithe')
    db.set_field(TITHE, 'skillDisplayName', 'tagSVCLeinthCrimsonTithe')
    db.set_field(TITHE, 'skillBaseDescription', 'tagSVCLeinthCrimsonTitheDESC')
    db.set_field(TITHE, 'FileDescription',
                 'Leinth: the Bloodborn blood-rain, promoted from her cult Disciple (b94)')
    db._modified.add(TITHE)

    _clone_new(db, CHOIR_DONOR, CHOIR, 'Choir of the Bloodborn')
    donor_burst = db.get_field_value(CHOIR_DONOR, 'petBurstSpawn')
    n = len(donor_burst) if isinstance(donor_burst, list) else 1
    burst = list(CHOIR_BURST_HEAD) + [CHOIR_BURST_HEAD[-1]] * max(0, n - len(CHOIR_BURST_HEAD))
    db.set_field(CHOIR, 'petBurstSpawn', burst[:max(n, len(CHOIR_BURST_HEAD))])
    db.set_field(CHOIR, 'petLimit', CHOIR_LIMIT)
    db.set_field(CHOIR, 'spawnObjectsTimeToLive', CHOIR_TTL)
    db.set_field(CHOIR, 'skillDisplayName', 'tagSVCLeinthChoirBloodborn')
    db.set_field(CHOIR, 'skillBaseDescription', 'tagSVCLeinthChoirBloodbornDESC')
    db.set_field(CHOIR, 'FileDescription',
                 'Leinth: fewer, better cult summons (b76 density law) (b94)')
    db._modified.add(CHOIR)

    _clone_new(db, MIRE_DONOR, MIRE, 'Sanguine Mire')
    db.set_field(MIRE, 'spawnObjects', [MIRE_PET])
    db.set_field(MIRE, 'petBurstSpawn', list(MIRE_BURST))
    db.set_field(MIRE, 'petLimit', MIRE_LIMIT)
    db.set_field(MIRE, 'spawnObjectsTimeToLive', MIRE_TTL)
    db.set_field(MIRE, 'skillDisplayName', 'tagSVCLeinthSanguineMire')
    db.set_field(MIRE, 'skillBaseDescription', 'tagSVCLeinthSanguineMireDESC')
    db.set_field(MIRE, 'FileDescription',
                 'Leinth: her death floods the sanctuary floor (b94)')
    db._modified.add(MIRE)

    for k, v in TAGS.items():
        tags[k] = v
    print("  authored 3 cult skills (%s) + %d Text tags"
          % (', '.join(s.rsplit('\\', 1)[-1] for s in NEW_SKILLS), len(TAGS)))

    # ── 2. the summon cut on her existing ugly spam ─────────────────────────
    prev_burst = db.get_field_value(UGLIES, 'petBurstSpawn')
    prev_limit = _v1(db, UGLIES, 'petLimit')
    db.set_field(UGLIES, 'petBurstSpawn', list(UGLIES_BURST))
    db.set_field(UGLIES, 'petLimit', UGLIES_LIMIT)
    if not (_v1(db, UGLIES, 'spawnObjectsTimeToLive') or 0):
        db.set_field(UGLIES, 'spawnObjectsTimeToLive', UGLIES_TTL)
    db._modified.add(UGLIES)
    print("  leinth_summon_uglies: petBurstSpawn %s -> %s, petLimit %s -> %d, "
          "TTL -> %.0fs (b76 density law; the skill stays wired at specialAttack2)"
          % (prev_burst, UGLIES_BURST, prev_limit, UGLIES_LIMIT, UGLIES_TTL))

    # ── 3. per-variant stats + kit wiring ───────────────────────────────────
    for rec in VARIANTS:
        before = (_v1(db, rec, 'characterLife'), _v1(db, rec, 'defensivePhysical'),
                  _v1(db, rec, 'defensivePierce'))

        db.set_field(rec, 'characterLife', LIFE[rec])
        db.set_field(rec, 'defensivePhysical', PHYS)
        db.set_field(rec, 'defensivePierce', PIERCE)
        db.set_field(rec, 'characterAttackSpeed', ATTACK_SPEED)
        db.set_field(rec, 'characterRunSpeed', RUN_SPEED)
        db.set_field(rec, 'characterLifeRegen', LIFE_REGEN)

        # her EXISTING geysers, raised in place
        cur_geyser = _v1(db, rec, 'skillName%d' % GEYSER_SLOT)
        if not isinstance(cur_geyser, str) or 'cerberus_crackfire' not in cur_geyser.lower():
            raise SystemExit(
                "[leinth_wave] %s: skillName%d is %r, expected cerberus_crackfire "
                "- her geyser slot moved; refusing to raise the wrong skill."
                % (rec, GEYSER_SLOT, cur_geyser))
        prev_g = db.get_field_value(rec, 'skillLevel%d' % GEYSER_SLOT)
        db.set_field(rec, 'skillLevel%d' % GEYSER_SLOT, list(GEYSER_LEVELS))

        # the three new skills, each into a PROVEN-FREE kit slot
        for slot, skill, levels, label in (
                (TITHE_SLOT, TITHE, TITHE_LEVELS, 'Crimson Tithe'),
                (CHOIR_SLOT, CHOIR, CHOIR_LEVELS, 'Choir of the Bloodborn'),
                (MIRE_SLOT, MIRE, MIRE_LEVELS, 'Sanguine Mire')):
            _free_slot(db, rec, slot, label)
            db.set_field(rec, 'skillName%d' % slot, skill)
            db.set_field(rec, 'skillLevel%d' % slot, list(levels))

        # cast wiring: the ONE free attack slot + the two non-attack mechanisms
        if _v1(db, rec, 'specialAttack%sSkillName' % TITHE_SPECIAL):
            raise SystemExit(
                "[leinth_wave] %s: specialAttack%s is already taken - Crimson "
                "Tithe would displace it." % (rec, TITHE_SPECIAL))
        db.set_field(rec, 'specialAttack%sSkillName' % TITHE_SPECIAL, TITHE)
        db.set_field(rec, 'specialAttack%sChance' % TITHE_SPECIAL, TITHE_CHANCE)
        for field, skill, label in (('buffSelfSkillName', CHOIR, 'Choir of the Bloodborn'),
                                    ('dyingSkillName', MIRE, 'Sanguine Mire')):
            cur = _v1(db, rec, field)
            if isinstance(cur, str) and cur.strip():
                raise SystemExit(
                    "[leinth_wave] %s: %s already holds %r - %s would displace it."
                    % (rec, field, cur, label))
            db.set_field(rec, field, skill)

        db._modified.add(rec)
        print("  %s: life %s -> %g | phys %s -> %g | pierce %s -> %g | "
              "geysers %s -> %s | +3 skills (slots %d/%d/%d) | specialAttack%s + "
              "buffSelf + dying wired"
              % (rec.rsplit('\\', 1)[-1], before[0], LIFE[rec], before[1], PHYS,
                 before[2], PIERCE, prev_g, GEYSER_LEVELS,
                 TITHE_SLOT, CHOIR_SLOT, MIRE_SLOT, TITHE_SPECIAL))

    # ── SCOPE PROOF: not one loot field moved ───────────────────────────────
    drops_after = _drop_snapshot(db, VARIANTS)
    if drops_after != drops_before:
        moved = []
        for r in VARIANTS:
            for k in sorted(set(drops_before[r]) | set(drops_after[r])):
                if drops_before[r].get(k) != drops_after[r].get(k):
                    moved.append('%s.%s' % (r.rsplit('\\', 1)[-1], k))
        raise SystemExit(
            "[leinth_wave] DROP SCOPE VIOLATION: %s moved. This module must never "
            "touch her 100%% lenithsveil head drop, her 66%% soul (R-42 PLACED "
            "rate) or her chest proxy." % moved)
    print("  scope proof: 0 of %d loot/drop fields moved across the 3 variants "
          "(veil 100%%, soul 66%%, bosschestproxy_leinth all intact)"
          % sum(len(v) for v in drops_before.values()))


# =============================================================================
# GATE (registry step 4 - runs over the FINAL merged db)
# =============================================================================
def _kit_level(db, rec, skill):
    """The skillLevel array of `skill` in a skillName slot on `rec`, or None."""
    ff = db.get_fields(rec) or {}
    low = skill.lower()
    for k, tf in ff.items():
        b = k.split('###')[0]
        if not (b.startswith('skillName') and b[9:].isdigit()):
            continue
        if tf.values and str(tf.values[0]).replace('/', '\\').lower() == low:
            return db.get_field_value(rec, 'skillLevel%s' % b[9:])
    return None


def verify(db, tags=None):
    problems = []

    for rec in VARIANTS:
        if not db.has_record(rec):
            problems.append("Leinth variant MISSING from the final db: %s" % rec)
            continue
        label = rec.rsplit('\\', 1)[-1]

        def _num(field):
            v = _v1(db, rec, field)
            try:
                return float(v)
            except (TypeError, ValueError):
                return None

        checks = (('characterLife', LIFE[rec]), ('defensivePhysical', PHYS),
                  ('defensivePierce', PIERCE), ('characterAttackSpeed', ATTACK_SPEED),
                  ('characterRunSpeed', RUN_SPEED), ('characterLifeRegen', LIFE_REGEN))
        for field, want in checks:
            got = _num(field)
            if got is None or abs(got - want) > 0.01:
                problems.append("%s: %s=%r, expected %g (a later writer moved it)"
                                % (label, field, got, want))

        # HER IDENTITY: the poison weakness must survive untouched.
        poison = _num('defensivePoison')
        if poison is None or abs(poison - POISON_KEEP) > 0.01:
            problems.append(
                "%s: defensivePoison=%r but it MUST stay %g - the poison weakness "
                "is her amgoz1 identity and the fight's counter-play"
                % (label, poison, POISON_KEEP))

        # she must NOT have been pushed to uber tier
        lv = db.get_field_value(rec, 'charLevel')
        if isinstance(lv, list) and any(int(x) >= 100 for x in lv):
            problems.append("%s: charLevel %s reaches uber tier - she is the blood "
                            "cave's main-path boss, not a Toxeus champion" % (label, lv))

        # geysers raised, in range
        g = db.get_field_value(rec, 'skillLevel%d' % GEYSER_SLOT)
        g = g if isinstance(g, list) else [g]
        if [int(x) for x in g] != GEYSER_LEVELS:
            problems.append("%s: geyser skillLevel%d=%r, expected %s"
                            % (label, GEYSER_SLOT, g, GEYSER_LEVELS))
        if any(int(x) > GEYSER_MAX_INDEX for x in g if x is not None):
            problems.append("%s: geyser level exceeds the %d-entry per-level arrays"
                            % (label, GEYSER_MAX_INDEX))

        # each new skill is in a kit slot at level>=1 AND wired to a cast mechanism
        for skill, want_levels, wiring, lbl in (
                (TITHE, TITHE_LEVELS,
                 ('specialAttack%sSkillName' % TITHE_SPECIAL,), 'Crimson Tithe'),
                (CHOIR, CHOIR_LEVELS, ('buffSelfSkillName',), 'Choir of the Bloodborn'),
                (MIRE, MIRE_LEVELS, ('dyingSkillName',), 'Sanguine Mire')):
            lvls = _kit_level(db, rec, skill)
            lvls = lvls if isinstance(lvls, list) else ([lvls] if lvls is not None else [])
            if not lvls or min(int(x) for x in lvls) < 1:
                problems.append("%s: %s is not in a skillName slot at level>=1 "
                                "(levels=%r) - a level-0 skill never fires"
                                % (label, lbl, lvls))
            elif [int(x) for x in lvls] != want_levels:
                problems.append("%s: %s levels %r, expected %s"
                                % (label, lbl, lvls, want_levels))
            for field in wiring:
                got = _v1(db, rec, field)
                if not isinstance(got, str) or got.replace('/', '\\').lower() != skill.lower():
                    problems.append("%s: %s=%r, expected %s (%s would never be "
                                    "cast)" % (label, field, got, skill, lbl))
        ch = _num('specialAttack%sChance' % TITHE_SPECIAL)
        if ch is None or ch <= 0:
            problems.append("%s: specialAttack%sChance=%r (<=0 = never cast)"
                            % (label, TITHE_SPECIAL, ch))

        # her four ORIGINAL specials must all still be wired (nothing displaced)
        for suf in ('', '2', '3', '4'):
            if not _v1(db, rec, 'specialAttack%sSkillName' % suf):
                problems.append("%s: specialAttack%s lost its skill - this wave "
                                "must be purely additive" % (label, suf or '1'))

        # drops untouched
        if abs((_num('chanceToEquipHead') or 0) - 100.0) > 0.01:
            problems.append("%s: chanceToEquipHead=%r, expected 100 (lenithsveil)"
                            % (label, _num('chanceToEquipHead')))
        soul = _num('chanceToEquipFinger2')
        if soul is None or soul <= 0:
            problems.append("%s: chanceToEquipFinger2=%r - her soul drop is gone"
                            % (label, soul))
        tp = _v1(db, rec, 'treasureProxyName')
        if not isinstance(tp, str) or 'bosschestproxy_leinth' not in tp.lower():
            problems.append("%s: treasureProxyName=%r - her bespoke chest moved "
                            "(this wave must NOT nerf or repoint it)" % (label, tp))

    # every new skill record exists, resolves and (if a summon) is TTL-capped
    for skill in NEW_SKILLS:
        if not db.has_record(skill):
            problems.append("new skill record MISSING: %s" % skill)
            continue
        cls = _v1(db, skill, 'Class')
        if not cls:
            problems.append("%s has no Class - the clone did not take" % skill)
        if isinstance(cls, str) and 'SpawnPet' in cls:
            ttl = _v1(db, skill, 'spawnObjectsTimeToLive')
            try:
                ttl = float(ttl or 0)
            except (TypeError, ValueError):
                ttl = 0.0
            if ttl <= 0:
                problems.append("%s: summon with no finite spawnObjectsTimeToLive "
                                "(b76 chumbi-freeze law)" % skill)
            lim = _v1(db, skill, 'petLimit')
            try:
                lim = int(lim or 0)
            except (TypeError, ValueError):
                lim = 0
            if lim <= 0 or lim > 8:
                problems.append("%s: petLimit=%r (must be a small positive cap)"
                                % (skill, lim))
            # get_field_value returns the SCALAR for a single-entry array, so this
            # must be normalised to a list before iterating (iterating a bare str
            # would walk its characters).
            spawns = db.get_field_value(skill, 'spawnObjects') or []
            if isinstance(spawns, str):
                spawns = [spawns]
            for p in spawns:
                if isinstance(p, str) and p and not db.has_record(p):
                    problems.append("%s spawns a MISSING record %s" % (skill, p))
                    break
        for tag_field in ('skillDisplayName', 'skillBaseDescription'):
            t = _v1(db, skill, tag_field)
            if isinstance(t, str) and t.startswith('tagSVCLeinth') and tags is not None:
                if t not in tags:
                    problems.append("%s references Text tag %s which the module "
                                    "never added" % (skill, t))

    # the ugly cut held
    if db.has_record(UGLIES):
        burst = db.get_field_value(UGLIES, 'petBurstSpawn')
        burst = burst if isinstance(burst, list) else [burst]
        lim = _v1(db, UGLIES, 'petLimit')
        ttl = _v1(db, UGLIES, 'spawnObjectsTimeToLive')
        if [int(x) for x in burst] != UGLIES_BURST:
            problems.append("leinth_summon_uglies petBurstSpawn=%r, expected %s"
                            % (burst, UGLIES_BURST))
        if int(lim or 0) != UGLIES_LIMIT:
            problems.append("leinth_summon_uglies petLimit=%r, expected %d"
                            % (lim, UGLIES_LIMIT))
        if not (float(ttl or 0) > 0):
            problems.append("leinth_summon_uglies has no finite TTL (b76 law)")
    else:
        problems.append("leinth_summon_uglies MISSING - her specialAttack2 is dead")

    # ORDERING INVARIANT: the mid boss must not out-stat the uber champion.
    if db.has_record(_ENSLAVER):
        def _e(f):
            v = _v1(db, _ENSLAVER, f)
            try:
                return float(v)
            except (TypeError, ValueError):
                return None
        for field, mine in (('defensivePhysical', PHYS), ('defensivePierce', PIERCE),
                            ('characterAttackSpeed', ATTACK_SPEED),
                            ('characterRunSpeed', RUN_SPEED)):
            theirs = _e(field)
            if theirs is not None and mine > theirs + 1e-6:
                problems.append(
                    "ORDERING: Leinth's %s (%g) now EXCEEDS the Enslaver's (%g) - "
                    "a charLevel 74-76 mid boss must never out-stat a charLevel "
                    "100 uber" % (field, mine, theirs))

    if problems:
        raise SystemExit(
            "[leinth_wave] R-71 VERIFY FAILED (Leinth buff + cult abilities):\n"
            "  - " + "\n  - ".join(problems))
    print("  [leinth_wave] verify OK: 3 variants at life %s / phys %g / pierce %g "
          "/ poison %g (identity KEPT); geysers %s; 3 cult skills wired "
          "(specialAttack%s + buffSelf + dying); every summon TTL-capped; drops "
          "untouched; still ranked below the Enslaver"
          % ([int(LIFE[v]) for v in VARIANTS], PHYS, PIERCE, POISON_KEEP,
             GEYSER_LEVELS, TITHE_SPECIAL))
