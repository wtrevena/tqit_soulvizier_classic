"""boss_skill_fix - repair the skill-USAGE wiring on the new bosses (b39).

WHY THIS EXISTS (RCA in docs/reports/b39_boss_skills_rca.md)
------------------------------------------------------------
Will (2026-07-13): "the new bosses we created [are] not having or not using
skills, when you are fighting them and when they are summoned."

An audit of build38 (baseline_build38.arz) over BOTH surfaces found:

  * Surface B (SOUL-SUMMONED PET forms): HEALTHY. Every summoned pet
    (_build_boss_summon + _mirror_source_skill_kit) carries its source's
    animation+skill kit with castable specials (chance>0) that all resolve, is
    permanent (TTL absent) with a sane petLimit. No pet fix is needed.

  * Surface A (FOUGHT monster records): a family of apex bosses ships skills
    that the AI is configured to use but which are DISABLED at skillLevel 0.
    Root cause is uniform: a builder set `skillName{i}` on a cloned donor WITHOUT
    the matching `skillLevel{i}`, so the new skill inherited the donor's empty
    (level-0) slot. Two engine consequences, distinguished by skill CLASS:
      - SUMMON specials (Skill_*SpawnPet*): a level-0 summon NEVER fires. Proof:
        across the whole build38 arz, ZERO vanilla monster ships a chance>0
        SpawnPet special at level 0 (min level is 1); every level-0 SpawnPet
        special in the DB belongs to one of these um_*_99 mod bosses. So a
        level-0 summon special is an unambiguous "boss never summons" defect.
      - AttackProjectile[Ring] specials at level 0 clamp to base magnitude and
        DO fire, but the mod's donor/design level for the skill is higher (e.g.
        cyclops_terrifyingroar sits at 8-10 on every native elder cyclops). The
        boss firing its whole kit at base is the mis-built symptom.
      - PASSIVES/AURAS at level 0 apply NO effect (their bonus lives in per-level
        arrays; level 0 = nothing). boss_conversionimmunity=0 also = a
        correctness bug: the apex boss is player-CONVERTIBLE.
    Plus Helepolis, whose signature turret barrage was DISPLACED (a distinct
    defect, see below).

VANILLA IS NOT A BLANKET "level>=1" INVARIANT (round-2 vet correction)
---------------------------------------------------------------------
Unmodified vanilla DOES ship chance>0 level-0 AttackProjectile[Ring] specials
(boss_dragonliche_57/60/63 dragonliche_freezingbreath@15%, spiderblackwidow01
venomnova@50%, jg7_undeadbrother_mage monster_thunderball@50%). So "chance>0
level-0 special" is NOT a universal defect signal for arbitrary records - it has
vanilla false positives. Two consequences, both honored here:
  1. Levels are DONOR-MATCHED per skill (the level the skill sits at on the boss
     that natively uses it), NOT a blanket constant. Evidence cited per entry.
  2. The fail-loud roster scan (verify()) is SCOPED to the um_*_99 mod apex-boss
     naming convention (all mod-authored), so it never trips on a vanilla record.

WHAT THIS MODULE DOES (field edits ONLY - no clones, no souls, no pets)
-----------------------------------------------------------------------
Enables each disabled skill at its evidence-based level (no damage/stat field is
touched; only skillLevel / a Helepolis special slot). Covers the FULL roster of
defective bosses (round-1 missed um_voranthys_99 - the worst-affected, whole kit
at level 0; the fix is now roster-derived + fail-loud so a miss can't ship).

DELIBERATELY LEFT (documented in the RCA, NOT touched here):
  * globalproperties_epic01/legendary01 + all_hpscaling_passive at level 0 - the
    vanilla difficulty-scaling convention (every exemplar ships them at 0).
  * Level-0 skills NOT wired as an active special and NOT a boss passive/aura:
    Voranthys sepulchralwyrm_firebreath / dragonliche_decomposition /
    dragonliche_buffetingwings / ondeath_spawnskeleton / ondeath_necronova;
    Gorrahk/Kravmoloch attack_damagemodifier_02 / bladenova; Ilsevar lifedrain;
    Vashkarr svc_vashkarr_summonhorde / shieldcharge / deflectprojectiles /
    lowhealth_berserkerrage01; Helepolis leveler_missile (mod-only, no donor) /
    siegewalker_firespit. Enabling these would ADD casts / death-spawns / defense
    magnitude the boss is not currently configured to use = a behavior change,
    out of scope for a skill-usage repair. (They are dormant kit slots, a valid
    state; the roster scan does not flag them because they carry no special.)
  * Ephialtes (WILL_DECISIONS: deliberately single-phase / no summon) - complete.
  * Toxeus Hunt's high inherited ATTACK levels (flashpowder 78, lifedrain 50, ...)
    clamp to the skill's max array entry -> functional (max-power), not broken;
    only the Hunt's dead passives are enabled.

REGISTRY ORDER: this module runs LAST among content modules (immediately before
`visuals`, which writes nothing), so it sees the FINAL assembled records - after
the monolith AND every boss-creating registry module. All target bosses are
mod-authored um_ records (four_generals/diadochi/polis_vault/neferkha/toxeus_suite
+ the monolith obsidian/Propontis waves); no SV-original DESIGN record is touched.
Expected S4b COLLISION warnings (legal, later-wins): um_helepolis_99 (diadochi)
and um_toxeus_hunt_99 (toxeus_suite) are re-edited here. The FINALIZATION-phase
Ground Smash de-filler (run_registry_gates) touches only SOUL equipmentring
itemSkillName fields, never these monster skillLevel fields - provably disjoint.
"""

import re

MODULE_NAME = 'boss_skill_fix'

# ── boss records (final paths in the built arz) ─────────────────────────────
_R = 'records\\'
HELEPOLIS   = _R + r'xpack\creatures\monster\siegestrider\um_helepolis_99.dbr'
DORUS       = _R + r'xpack\creatures\monster\lostsoul\um_dorus_99.dbr'
KRAVMOLOCH  = _R + r'creature\monster\skeleton\um_kravmoloch_99.dbr'
GORRAHK     = _R + r'creature\monster\skeleton\um_gorrahk_99.dbr'
ILSEVAR     = _R + r'creature\monster\skeleton\um_ilsevar_99.dbr'
VORANTHYS   = _R + r'creature\monster\questbosses\um_voranthys_99.dbr'
VASHKARR    = _R + r'creature\monster\dragonian\um_vashkarr_99.dbr'
SARKOTH     = _R + r'creature\monster\abyssalliche\um_sarkoth_99.dbr'
BROODMOTHER = _R + r'creature\monster\sepulchralwyrm\um_broodmother_99.dbr'
TOXEUS_HUNT = _R + r'creature\monster\shadowstalker\um_toxeus_hunt_99.dbr'

# ── LEVEL-0 SPECIALS the AI casts (chance>0) that reference a level-0 kit skill.
# (label, record, [(skill_substr, level), ...])  -- LEVEL IS DONOR-MATCHED PER
# SKILL (the level the skill sits at on the boss that natively/canonically uses
# it), never a blanket constant. Enabling ONLY sets skillLevel; no damage/stat
# field is touched. Evidence per skill:
#   dragonliche_freezingbreath 2  = um_neferkha_99 (cold-apex sibling; sole positive carrier)
#   alastor_summonskeletonwarrior 2, alastor_summonskeletonarcher 2 = boss_necromancer_alastor_18 (native Alastor)
#   aktaios_summontombguardians 1 = boss_egypttelkine_aktaios_27 (native Aktaios)
#   cyclops_groundsmash 4         = the mod's OWN design magnitude (soul-grant tier 3/4/5, central)
#   cyclops_terrifyingroar 8      = bm_eldercyclops_33/36 (native elder cyclops; tier 8-10, low end)
#   halimedes_terrifyingroar 3    = um_vashkarr_99 (sibling apex; carries it @3)
#   svc_dorus_raisecourt 1        = its own skillMaxLevel is 1 (1 is the only functional level)
_SPECIALS = [
    ('Voranthys', VORANTHYS, [('dragonliche_freezingbreath', 2),
                              ('alastor_summonskeletonwarrior', 2),
                              ('alastor_summonskeletonarcher', 2),
                              ('aktaios_summontombguardians', 1)]),
    ('Gorrahk',    GORRAHK,    [('cyclops_groundsmash', 4), ('cyclops_terrifyingroar', 8)]),
    ('Kravmoloch', KRAVMOLOCH, [('cyclops_groundsmash', 4), ('cyclops_terrifyingroar', 8)]),
    ('Ilsevar',    ILSEVAR,    [('halimedes_terrifyingroar', 3)]),
    ('Dorus',      DORUS,      [('svc_dorus_raisecourt', 1)]),
]

# ── LEVEL-0 self-auras the boss is meant to project (level 0 = no aura).
#   character_speedall 3 = um_vashkarr_99 (sibling apex; carries it @3)
#   drxdeathchillaura 3  = standard aura-enable level (matches the mod's character_speedall aura precedent)
_AURAS = [
    ('Gorrahk',    GORRAHK,    [('character_speedall', 3)]),
    ('Kravmoloch', KRAVMOLOCH, [('character_speedall', 3)]),
    ('Ilsevar',    ILSEVAR,    [('drxdeathchillaura', 3)]),
]

# ── LEVEL-0 core passives (a passive at level 0 applies NO bonus). Enable at the
# standard boss-passive floor of 1 (every sibling's conversionimmunity/scaling/
# hero_scaling sits at 1 - this is a binary enable, not a magnitude guess).
# boss_conversionimmunity=0 is ALSO a correctness bug (apex boss is convertible).
_PASSIVES = [
    ('Voranthys',   VORANTHYS,   [('boss_conversionimmunity', 1), ('boss_scaling', 1)]),
    ('Toxeus Hunt', TOXEUS_HUNT, [('boss_conversionimmunity', 1), ('hero_scaling', 1),
                                  ('toxeus_passiveproperties', 1)]),
    ('Vashkarr',    VASHKARR,    [('boss_conversionimmunity', 1), ('boss_scaling', 1)]),
    ('Sarkoth',     SARKOTH,     [('boss_conversionimmunity', 1), ('boss_scaling', 1)]),
    ('Broodmother', BROODMOTHER, [('boss_scaling', 1)]),
]

# armor_passive shipped at level 0 (ZERO armor rating vs every sibling: Vashkarr 75,
# Ilsevar 39, Dorus 62) -> set to the boss's own charLevel (the conservative TQ
# floor; armor_passive is a defensive passive, not a damage field). Gorrahk 40,
# Kravmoloch 74.
_ARMOR = [('Gorrahk', GORRAHK), ('Kravmoloch', KRAVMOLOCH)]

# Helepolis turret restore constants (donor um_leveler_43's bare turret special).
_TURRET_SUBSTR = 'leveler_turretattack'
_METEOR_LEVEL = 9          # hero_meteorlob1_ring donor: xhero_ironskin_41 @9 (the lower of 2 carriers)
_TURRET_CHANCE = 80.0      # donor leveler fires the turret as its primary special @80%

# Records this module is RESPONSIBLE for (used by the roster coverage assertion).
_TARGET_RECORDS = {rec for _l, rec, _f in _SPECIALS} | {HELEPOLIS} | \
                  {rec for _l, rec, _f in _AURAS} | {rec for _l, rec, _f in _PASSIVES} | \
                  {rec for _l, rec in _ARMOR}


# ── generic field helpers (operate on the EXISTING kit; no hardcoded skill paths) ──
def _slot_of(db, rec, substr):
    """(idx, skillref) of the skillName<idx> slot whose value contains `substr`
    (case-insensitive), lowest index wins; else (None, None)."""
    ff = db.get_fields(rec) or {}
    hits = []
    for k, tf in ff.items():
        base = k.split('###')[0]
        if base.startswith('skillName') and base[9:].isdigit() and tf.values:
            v = str(tf.values[0])
            if substr in v.lower():
                hits.append((int(base[9:]), v))
    hits.sort()
    return hits[0] if hits else (None, None)


def _level_of(db, rec, idx):
    v = db.get_field_value(rec, 'skillLevel%d' % idx)
    return v[0] if isinstance(v, list) else v


def _enable_skill(db, rec, substr, level, out, only_if_zero=True):
    """Set skillLevel<i> for the kit slot holding `substr`. If only_if_zero, act
    only when the current level is 0/absent (idempotent + never clobbers a real
    design level). Existing INT field stays INT (no explicit dtype)."""
    idx, _ref = _slot_of(db, rec, substr)
    if idx is None:
        out.append(('MISS', rec, substr, 'no skillName slot'))
        return False
    cur = _level_of(db, rec, idx)
    if only_if_zero and cur not in (0, None):
        out.append(('SKIP', rec, substr, 'level already %s' % cur))
        return False
    db.set_field(rec, 'skillLevel%d' % idx, int(level))
    out.append(('SET-LVL', rec, '%s (slot %d)' % (substr, idx), '%s -> %d' % (cur, level)))
    return True


def _kit_ref(db, rec, substr):
    return _slot_of(db, rec, substr)[1]


def _free_skillname_slot(db, rec, lo=1, hi=24):
    ff = db.get_fields(rec) or {}
    used = set()
    for k, tf in ff.items():
        base = k.split('###')[0]
        if base.startswith('skillName') and base[9:].isdigit() and tf.values \
                and str(tf.values[0]).strip():
            used.add(int(base[9:]))
    for i in range(lo, hi + 1):
        if i not in used:
            return i
    return None


def _special_used(db, rec, suffix):
    v = db.get_field_value(rec, 'specialAttack%sSkillName' % suffix)
    v = v[0] if isinstance(v, list) else v
    return bool(v and str(v).strip())


def _special_refs(db, rec):
    """Normalized set of skillrefs already wired into ANY specialAttack slot."""
    ff = db.get_fields(rec) or {}
    out = set()
    for k, tf in ff.items():
        b = k.split('###')[0]
        if b.startswith('specialAttack') and b.endswith('SkillName') and tf.values \
                and str(tf.values[0]).strip():
            out.add(str(tf.values[0]).replace('/', '\\').lower())
    return out


def _set_special(db, rec, suffix, skillref, chance, rng, out, delay=10.0, timeout=1.0):
    """Wire specialAttack<suffix> = skillref @ chance (+ range/delay/timeout). Only
    writes an EMPTY slot (never clobbers an existing special)."""
    if _special_used(db, rec, suffix):
        out.append(('SKIP', rec, 'specialAttack%s' % suffix, 'slot already used'))
        return False
    db.set_field(rec, 'specialAttack%sSkillName' % suffix, skillref)
    db.set_field(rec, 'specialAttack%sChance' % suffix, float(chance))
    db.set_field(rec, 'specialAttack%sRange' % suffix, rng)
    db.set_field(rec, 'specialAttack%sDelay' % suffix, float(delay))
    db.set_field(rec, 'specialAttack%sTimeout' % suffix, float(timeout))
    out.append(('SET-SPEC', rec, 'specialAttack%s=%s' % (suffix, skillref.rsplit(chr(92), 1)[-1]),
                'chance %s' % chance))
    return True


# ── roster helpers (roster-DERIVED, not a hardcoded list) ───────────────────
_UM99_RE = re.compile(r'\\um_[^\\]*_99\.dbr$', re.I)


def _roster_um99(db):
    """Every mod apex-boss monster record (um_*_99 naming convention). All
    mod-authored, so scanning them for the level-0-special defect never
    false-positives on a vanilla record."""
    out = []
    for rec in db.record_names():
        rl = rec.lower()
        if _UM99_RE.search(rl) and ('\\monster\\' in rl or '\\creatures\\monster\\' in rl):
            out.append(rec)
    return sorted(out)


def _l0_specials(db, rec):
    """[(special_field, skillref, chance)] for every specialAttack the AI casts
    (chance>0) whose skill sits in a skillName slot at level 0 - the exact
    "tries to cast, does nothing" defect. Specials NOT in a skillName slot are
    ignored (a slotless special fires at base; it is not this defect)."""
    ff = db.get_fields(rec) or {}
    # level by normalized skillName ref
    names, levels = {}, {}
    for k, tf in ff.items():
        b = k.split('###')[0]
        if b.startswith('skillName') and b[9:].isdigit() and tf.values:
            names[int(b[9:])] = str(tf.values[0])
        m = re.match(r'skillLevel(\d+)$', b)
        if m and tf.values:
            levels[int(m.group(1))] = tf.values[0]
    lvl_by_ref = {names[i].replace('/', '\\').lower(): levels.get(i, 0) for i in names}
    out = []
    for k, tf in ff.items():
        b = k.split('###')[0]
        m = re.match(r'specialAttack(\d*)SkillName$', b)
        if not (m and tf.values and str(tf.values[0]).strip()):
            continue
        suf = m.group(1)
        ref = str(tf.values[0]).replace('/', '\\').lower()
        ch = db.get_field_value(rec, 'specialAttack%sChance' % suf)
        ch = ch[0] if isinstance(ch, list) else ch
        if (ch or 0) > 0 and lvl_by_ref.get(ref) == 0:
            out.append(('specialAttack%s' % suf, ref.rsplit('\\', 1)[-1], ch))
    return out


# ── table driver ────────────────────────────────────────────────────────────
def _apply_table(db, table, out):
    for label, rec, fixes in table:
        if not db.has_record(rec):
            out.append(('MISS', rec, label, 'record absent'))
            continue
        touched = False
        for substr, lvl in fixes:
            touched |= _enable_skill(db, rec, substr, lvl, out)
        if touched:
            db._modified.add(rec)


def _fix_armor(db, out):
    for label, rec in _ARMOR:
        if not db.has_record(rec):
            out.append(('MISS', rec, label + ' armor', 'record absent'))
            continue
        idx, _ref = _slot_of(db, rec, 'armor_passive')
        if idx is None:
            out.append(('MISS', rec, label + ' armor', 'no armor_passive slot'))
            continue
        if _level_of(db, rec, idx) not in (0, None):
            out.append(('SKIP', rec, label + ' armor', 'already leveled'))
            continue
        cl = db.get_field_value(rec, 'charLevel')
        cl = cl[0] if isinstance(cl, list) else cl
        lvl = int(cl) if cl else 50
        db.set_field(rec, 'skillLevel%d' % idx, lvl)
        out.append(('SET-LVL', rec, '%s armor_passive (slot %d)' % (label, idx),
                    '0 -> %d (charLevel)' % lvl))
        db._modified.add(rec)


def _fix_helepolis(db, out):
    """Restore Helepolis's displaced siege cannon. The diadochi module overwrote
    the leveler's bare specialAttackSkillName (leveler_turretattack @80%) with the
    meteor nova, so the turret - still in skillName1 @ level 5 - no longer fires as
    a special. Two edits, no clones/no rebalance:
      (a) give the meteor (bare specialAttackSkillName, currently SLOTLESS) a real
          skillName slot at its donor level, so it fires at intended magnitude;
      (b) re-wire the turret (already level 5 in the kit) into a free special slot
          @80% (donor chance) - the cannon fires again.
    leveler_missile (mod-only, no donor) + siegewalker_firespit stay dormant (see
    the module docstring's "deliberately left")."""
    rec = HELEPOLIS
    if not db.has_record(rec):
        out.append(('MISS', rec, 'helepolis', 'record absent'))
        return
    # (a) meteor -> real skillName slot @ donor level (idempotent).
    meteor = db.get_field_value(rec, 'specialAttackSkillName')
    meteor = meteor[0] if isinstance(meteor, list) else meteor
    if meteor and 'meteor' in str(meteor).lower() and _slot_of(db, rec, 'meteorlob')[0] is None:
        slot = _free_skillname_slot(db, rec)
        if slot:
            db.set_field(rec, 'skillName%d' % slot, str(meteor))
            db.set_field(rec, 'skillLevel%d' % slot, _METEOR_LEVEL)
            out.append(('SET-KIT', rec, 'skillName%d=meteorlob' % slot, 'lvl %d' % _METEOR_LEVEL))
    # (b) restore the turret as a free numbered special (kit level 5 unchanged).
    turret = _kit_ref(db, rec, _TURRET_SUBSTR)
    if not turret:
        out.append(('MISS', rec, 'turret restore', 'no leveler_turretattack in kit'))
    elif turret.replace('/', '\\').lower() in _special_refs(db, rec):
        out.append(('SKIP', rec, 'turret restore', 'already wired as a special'))  # idempotent
    else:
        # first empty of specialAttack3/4/5 (Helepolis ships '' + 2 only)
        placed = False
        for suf in ('3', '4', '5'):
            if not _special_used(db, rec, suf):
                _set_special(db, rec, suf, turret, _TURRET_CHANCE, 'AnyRange', out,
                             delay=10.0, timeout=1.0)
                placed = True
                break
        if not placed:
            out.append(('SKIP', rec, 'turret restore', 'no free special slot'))
    db._modified.add(rec)


# ── entry points ────────────────────────────────────────────────────────────
def apply(db, tags):
    assert hasattr(db, 'record_names') and hasattr(db, 'set_field'), \
        'boss_skill_fix.apply: db is not an ArzDatabase'
    print('\n=== b39 boss_skill_fix: repair fought-boss skill-usage wiring ===')
    out = []
    _apply_table(db, _SPECIALS, out)
    _apply_table(db, _AURAS, out)
    _apply_table(db, _PASSIVES, out)
    _fix_armor(db, out)
    _fix_helepolis(db, out)

    sets = [o for o in out if o[0].startswith('SET')]
    miss = [o for o in out if o[0] == 'MISS']
    for kind, rec, what, detail in out:
        print('  [%-8s] %-26s %-42s %s' % (kind, rec.rsplit('\\', 1)[-1], what, detail))
    print('  boss_skill_fix: %d edit(s), %d miss(es)' % (len(sets), len(miss)))
    # Fail loud only if a TARGET boss record is missing (a real regression).
    hard = [o for o in miss if 'record absent' in o[3]]
    if hard:
        raise SystemExit('boss_skill_fix: target boss record(s) missing: %s'
                         % ', '.join(sorted({o[1] for o in hard})))


def verify(db, tags=None):
    """POST-FINALIZATION, roster-DERIVED fail-loud gate (run_registry_verifies).

    (1) ROSTER SCAN: over EVERY um_*_99 apex-boss record (not a hardcoded list),
        fail loud on ANY chance>0 level-0 special. This is what catches a missed
        or newly-added boss (the round-1 um_voranthys_99 miss) and any
        finalization regression that re-zeroes a special - the build itself
        refuses to ship a boss that "tries to cast, does nothing". Scoped to
        um_*_99 (all mod-authored) so it never trips on a vanilla level-0
        AttackProjectile special (dragonliche/blackwidow/etc).
    (2) RE-ASSERT every fix this module applied survived finalization: each table
        skill is now level>=1, each _ARMOR armor_passive is level>=1, and
        Helepolis's restored turret special is present."""
    problems = []

    # (1) roster-derived scan
    uncovered = []
    for rec in _roster_um99(db):
        for (field, skill, ch) in _l0_specials(db, rec):
            msg = '%s: %s (chance %s) -> level-0 skill %s' % (
                rec.rsplit('\\', 1)[-1], field, ch, skill)
            problems.append(msg)
            if rec not in _TARGET_RECORDS:
                uncovered.append(rec.rsplit('\\', 1)[-1])

    # (2) re-assert the module's own fixes landed + survived finalization
    for _label, rec, fixes in _SPECIALS + _AURAS + _PASSIVES:
        if not db.has_record(rec):
            problems.append('%s: TARGET RECORD MISSING (regression)' % rec.rsplit('\\', 1)[-1])
            continue
        for substr, _lvl in fixes:
            idx, _ref = _slot_of(db, rec, substr)
            if idx is None:
                problems.append('%s: skill %s vanished from kit (regression)'
                                % (rec.rsplit('\\', 1)[-1], substr))
            elif (_level_of(db, rec, idx) or 0) < 1:
                problems.append('%s: %s re-zeroed after finalization (regression)'
                                % (rec.rsplit('\\', 1)[-1], substr))
    for _label, rec in _ARMOR:
        idx, _ref = _slot_of(db, rec, 'armor_passive')
        if idx is None or (_level_of(db, rec, idx) or 0) < 1:
            problems.append('%s: armor_passive not enabled (regression)'
                            % rec.rsplit('\\', 1)[-1])
    if db.has_record(HELEPOLIS):
        ff = db.get_fields(HELEPOLIS) or {}
        turret_special = any(
            k.split('###')[0].startswith('specialAttack')
            and k.split('###')[0].endswith('SkillName')
            and tf.values and _TURRET_SUBSTR in str(tf.values[0]).lower()
            for k, tf in ff.items())
        if not turret_special:
            problems.append('Helepolis: turret barrage not restored (regression)')

    if uncovered:
        problems.insert(0, 'UNCOVERED apex boss(es) with a level-0 special (add to '
                        'boss_skill_fix): %s' % ', '.join(sorted(set(uncovered))))
    if problems:
        raise SystemExit('boss_skill_fix.verify FAILED:\n  ' + '\n  '.join(problems))
    print('  boss_skill_fix.verify: OK (roster um_*_99 clean of level-0 specials; '
          'all enables survived finalization)')
