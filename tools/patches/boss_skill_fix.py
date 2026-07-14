"""boss_skill_fix - repair the skill-USAGE wiring on the new bosses (b39).

WHY THIS EXISTS (RCA in docs/reports/b39_boss_skills_rca.md)
------------------------------------------------------------
Will (2026-07-13): "the new bosses we created [are] not having or not using
skills, when you are fighting them and when they are summoned."

An audit of build38a (baseline_build38.arz) over BOTH surfaces found:

  * Surface B (SOUL-SUMMONED PET forms): HEALTHY. Every summoned pet
    (_build_boss_summon + _mirror_source_skill_kit) carries its source's
    animation+skill kit with castable specials (chance>0) that all resolve, is
    permanent (TTL absent) with a sane petLimit. No pet fix is needed.

  * Surface A (FOUGHT monster records): a family of bosses ships with skills
    that are WIRED to fire/apply but DISABLED at skillLevel 0. Root cause is
    uniform: a builder set `skillName{i}` on a cloned donor WITHOUT setting the
    matching `skillLevel{i}`, so the new skill inherited the donor's empty
    (level-0) slot. The engine then either never casts the special (a level-0
    special-attack) or never applies the passive/aura (a level-0 buff). Against
    the vanilla invariant (proven over 7 base/xpack exemplars: active skills and
    armor_passive are ALWAYS >=1; only globalproperties_epic/legendary +
    all_hpscaling are level-0 by difficulty convention) these are defects.

WHAT THIS MODULE DOES (field edits ONLY - no clones, no souls, no pets)
-----------------------------------------------------------------------
1. HELEPOLIS (diadochi): its signature turret barrage was DISPLACED - the module
   overwrote specialAttackSkillName (the leveler's turret, vanilla 80%) with the
   meteor nova, so the siege engine never fired its cannon. Restore the turret as
   a special, give the meteor a real skillName slot+level, and light up the
   dormant missile/firespit "war-machine kit" (skillName6/7 shipped at level 0).

2. LEVEL-0 SPECIAL ATTACKS (chance>0 but the referenced skill is level 0 in its
   skillName slot): bump each to a modest level matching the mod's well-built
   bosses (Neferkha raisecourt=3, Alkyoneus slam=3, Menoetes groundbreaker=2).
     Dorus svc_dorus_raisecourt; Kravmoloch + Gorrahk cyclops_groundsmash +
     cyclops_terrifyingroar; Ilsevar halimedes_terrifyingroar.

3. LEVEL-0 AURAS/PASSIVES the boss is meant to have on (enable, minimal/standard
   level - NOT a damage rebalance):
     Kravmoloch/Gorrahk character_speedall (aura) + armor_passive (=charLevel,
     they shipped with ZERO armor rating vs every sibling); Ilsevar
     drxdeathchillaura; Toxeus Hunt boss_conversionimmunity/hero_scaling/
     toxeus_passiveproperties; Vashkarr/Sarkoth boss_conversionimmunity+
     boss_scaling; Broodmother boss_scaling. (boss_conversionimmunity=0 also = a
     correctness bug: the apex boss was player-CONVERTIBLE.)

DELIBERATELY LEFT (documented in the RCA, NOT touched here):
  * globalproperties_epic01/legendary01 + all_hpscaling_passive at level 0 - the
    vanilla difficulty-scaling convention (every exemplar ships them at 0).
  * Magnitude % passives at level 0 that are NOT wired to fire (bladenova,
    attack_damagemodifier_02, deflectprojectiles_passive, Vashkarr's vestigial
    svc_vashkarr_summonhorde/shieldcharge, Ilsevar lifedrain) - enabling them
    would change damage/defense magnitude or add casts (a rebalance / behavior
    change), which is out of scope for a skill-usage repair.
  * Ephialtes (WILL_DECISIONS: deliberately single-phase / no summon) - its kit
    is complete and intentional.
  * The Toxeus Hunt's high inherited attack levels (flashpowder 78, lifedrain 50,
    ...): out-of-range monster skill levels clamp to the skill's max, so they are
    functional (max-power), not broken; only the Hunt's dead passives are fixed.

REGISTRY ORDER: this module runs LAST among content modules (immediately before
`visuals`, which writes nothing), so it sees the FINAL assembled records - after
the monolith AND every boss-creating registry module (four_generals, diadochi,
polis_vault, neferkha, toxeus_suite). Expected S4b COLLISION warnings: it re-edits
um_helepolis_99 (diadochi) and um_toxeus_hunt_99 (toxeus_suite); later-wins is the
intended semantics. All monolith-created bosses (Dorus/Kravmoloch/Gorrahk/Vashkarr/
Sarkoth/Broodmother) predate the registry, so no collision is logged for them.
"""

MODULE_NAME = 'boss_skill_fix'

# ── boss records (final paths in the built arz) ─────────────────────────────
_R = 'records\\'
HELEPOLIS = _R + r'xpack\creatures\monster\siegestrider\um_helepolis_99.dbr'
DORUS     = _R + r'xpack\creatures\monster\lostsoul\um_dorus_99.dbr'
KRAVMOLOCH = _R + r'creature\monster\skeleton\um_kravmoloch_99.dbr'
GORRAHK   = _R + r'creature\monster\skeleton\um_gorrahk_99.dbr'
ILSEVAR   = _R + r'creature\monster\skeleton\um_ilsevar_99.dbr'
VASHKARR  = _R + r'creature\monster\dragonian\um_vashkarr_99.dbr'
SARKOTH   = _R + r'creature\monster\abyssalliche\um_sarkoth_99.dbr'
BROODMOTHER = _R + r'creature\monster\sepulchralwyrm\um_broodmother_99.dbr'
TOXEUS_HUNT = _R + r'creature\monster\shadowstalker\um_toxeus_hunt_99.dbr'

# skill-usage tuning levels (anchored to the mod's own well-built bosses: their
# special-attack skills sit at 2-4; boss passives/immunities at 1). These ENABLE
# a disabled skill; they do NOT touch any damage/stat field.
_LVL_SPECIAL = 4       # a level-0 special attack the boss is configured to cast
_LVL_SUMMON = 3        # a level-0 summon special (Neferkha raisecourt precedent)
_LVL_AURA = 3          # a level-0 self-aura (character_speedall / deathchillaura)
_LVL_PASSIVE = 1       # a standard boss passive/immunity/scaling (minimal enable)


# ── helpers (operate on the EXISTING kit; no hardcoded skill paths) ─────────
def _slot_of(db, rec, substr):
    """Return (idx, skillref) of the skillName<idx> slot whose value contains
    `substr` (case-insensitive), else (None, None). First match wins."""
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
    v = v[0] if isinstance(v, list) else v
    return v


def _enable_skill(db, rec, substr, level, out, only_if_zero=True):
    """Set skillLevel<i> for the kit slot holding `substr`. If only_if_zero, act
    only when the current level is 0/absent (idempotent + never clobbers a real
    design level). Records the action in `out`."""
    idx, ref = _slot_of(db, rec, substr)
    if idx is None:
        out.append(('MISS', rec, substr, 'no skillName slot'))
        return False
    cur = _level_of(db, rec, idx)
    if only_if_zero and cur not in (0, None):
        out.append(('SKIP', rec, substr, 'level already %s' % cur))
        return False
    db.set_field(rec, 'skillLevel%d' % idx, int(level))   # existing INT field -> stays INT
    out.append(('SET-LVL', rec, '%s (slot %d)' % (substr, idx), '%s -> %d' % (cur, level)))
    return True


def _kit_ref(db, rec, substr):
    _idx, ref = _slot_of(db, rec, substr)
    return ref


def _free_skillname_slot(db, rec, lo=1, hi=24):
    ff = db.get_fields(rec) or {}
    used = set()
    for k, tf in ff.items():
        base = k.split('###')[0]
        if base.startswith('skillName') and base[9:].isdigit():
            if tf.values and str(tf.values[0]).strip():
                used.add(int(base[9:]))
    for i in range(lo, hi + 1):
        if i not in used:
            return i
    return None


def _special_used(db, rec, suffix):
    v = db.get_field_value(rec, 'specialAttack%sSkillName' % suffix)
    v = v[0] if isinstance(v, list) else v
    return bool(v and str(v).strip())


def _set_special(db, rec, suffix, skillref, chance, rng, out, delay=10.0, timeout=2.0):
    """Wire specialAttack<suffix> = skillref @ chance (+ range/delay/timeout).
    Only writes an EMPTY slot (never clobbers an existing special)."""
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


# ── 1. Helepolis: restore the displaced siege battery ───────────────────────
def _fix_helepolis(db, out):
    rec = HELEPOLIS
    if not db.has_record(rec):
        out.append(('MISS', rec, 'helepolis', 'record absent'))
        return
    # (a) the meteor nova sits on specialAttack (slot '') but has NO skillName slot
    #     -> no defined level. Give it a real slot (idempotent: skip if present).
    meteor = db.get_field_value(rec, 'specialAttackSkillName')
    meteor = meteor[0] if isinstance(meteor, list) else meteor
    if meteor and 'meteor' in str(meteor).lower():
        if _slot_of(db, rec, 'meteorlob')[0] is None:
            slot = _free_skillname_slot(db, rec)
            if slot:
                db.set_field(rec, 'skillName%d' % slot, str(meteor))
                db.set_field(rec, 'skillLevel%d' % slot, _LVL_SPECIAL)
                out.append(('SET-KIT', rec, 'skillName%d=meteorlob' % slot, 'lvl %d' % _LVL_SPECIAL))
    # (b) enable the dormant missile + firespit (skillName slots at level 0).
    _enable_skill(db, rec, 'leveler_missile', _LVL_SPECIAL, out)
    _enable_skill(db, rec, 'siegewalker_firespit', _LVL_SPECIAL, out)
    # (c) RESTORE the turret barrage (the boss's own weapon, displaced by the
    #     meteor) + wire missile/firespit as specials so the war-machine fires.
    #     Free special slots on Helepolis: 3,4,5 (it ships '' + 2 only).
    turret = _kit_ref(db, rec, 'leveler_turretattack')
    missile = _kit_ref(db, rec, 'leveler_missile')
    firespit = _kit_ref(db, rec, 'siegewalker_firespit')
    if turret:
        _set_special(db, rec, '3', turret, 55.0, 'AnyRange', out)
    if missile:
        _set_special(db, rec, '4', missile, 35.0, 'AnyRange', out)
    if firespit:
        _set_special(db, rec, '5', firespit, 30.0, 'MediumRange', out, delay=12.0)
    db._modified.add(rec)


# ── 2 + 3. table-driven level-0 fixes ───────────────────────────────────────
# (label, record, [(skill_substr, level), ...])  - each enables a disabled skill.
_LEVEL0_SPECIALS = [
    ('Dorus',      DORUS,     [('dorus_raisecourt', _LVL_SUMMON)]),
    ('Kravmoloch', KRAVMOLOCH,[('cyclops_groundsmash', _LVL_SPECIAL), ('cyclops_terrifyingroar', _LVL_SPECIAL)]),
    ('Gorrahk',    GORRAHK,   [('cyclops_groundsmash', _LVL_SPECIAL), ('cyclops_terrifyingroar', _LVL_SPECIAL)]),
    ('Ilsevar',    ILSEVAR,   [('halimedes_terrifyingroar', _LVL_SPECIAL)]),
]
_AURAS = [
    ('Kravmoloch', KRAVMOLOCH,[('character_speedall', _LVL_AURA)]),
    ('Gorrahk',    GORRAHK,   [('character_speedall', _LVL_AURA)]),
    ('Ilsevar',    ILSEVAR,   [('drxdeathchillaura', _LVL_AURA)]),
]
_PASSIVES = [
    ('Toxeus Hunt', TOXEUS_HUNT, [('boss_conversionimmunity', _LVL_PASSIVE),
                                  ('hero_scaling', _LVL_PASSIVE),
                                  ('toxeus_passiveproperties', _LVL_PASSIVE)]),
    ('Vashkarr',    VASHKARR,    [('boss_conversionimmunity', _LVL_PASSIVE), ('boss_scaling', _LVL_PASSIVE)]),
    ('Sarkoth',     SARKOTH,     [('boss_conversionimmunity', _LVL_PASSIVE), ('boss_scaling', _LVL_PASSIVE)]),
    ('Broodmother', BROODMOTHER, [('boss_scaling', _LVL_PASSIVE)]),
]
# armor_passive shipped at level 0 (ZERO armor rating) -> set to the boss's own
# charLevel (the conservative TQ-standard, matching sibling Vashkarr=75@L72).
_ARMOR = [('Kravmoloch', KRAVMOLOCH), ('Gorrahk', GORRAHK)]


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
        out.append(('SET-LVL', rec, '%s armor_passive (slot %d)' % (label, idx), '0 -> %d (charLevel)' % lvl))
        db._modified.add(rec)


def apply(db, tags):
    assert hasattr(db, 'record_names') and hasattr(db, 'set_field'), \
        'boss_skill_fix.apply: db is not an ArzDatabase'
    print('\n=== b39 boss_skill_fix: repair fought-boss skill-usage wiring ===')
    out = []
    _fix_helepolis(db, out)
    _apply_table(db, _LEVEL0_SPECIALS, out)
    _apply_table(db, _AURAS, out)
    _apply_table(db, _PASSIVES, out)
    _fix_armor(db, out)

    sets = [o for o in out if o[0].startswith('SET')]
    miss = [o for o in out if o[0] == 'MISS']
    for kind, rec, what, detail in out:
        short = rec.rsplit('\\', 1)[-1]
        print('  [%-8s] %-26s %-42s %s' % (kind, short, what, detail))
    print('  boss_skill_fix: %d edit(s), %d miss(es)' % (len(sets), len(miss)))
    # Fail loud if a TARGET boss record is missing (a real regression), but tolerate
    # per-skill SKIP (idempotent re-runs) and never fabricate records.
    hard = [o for o in miss if 'record absent' in o[3]]
    if hard:
        raise SystemExit('boss_skill_fix: target boss record(s) missing: %s'
                         % ', '.join(sorted({o[1] for o in hard})))
    return


def verify(db, tags=None):
    """POST-FINALIZATION check: every skill this module enabled is now level>=1,
    and every level-0 special-attack among the target bosses is resolved. Runs in
    run_registry_verifies (after the gate battery finalizes the db)."""
    import re as _re
    problems = []
    targets = [HELEPOLIS, DORUS, KRAVMOLOCH, GORRAHK, ILSEVAR, VASHKARR, SARKOTH,
               BROODMOTHER, TOXEUS_HUNT]
    for rec in targets:
        if not db.has_record(rec):
            continue
        ff = db.get_fields(rec) or {}
        # level by skillName slot
        names, levels = {}, {}
        for k, tf in ff.items():
            b = k.split('###')[0]
            if b.startswith('skillName') and b[9:].isdigit() and tf.values:
                names[int(b[9:])] = str(tf.values[0])
            m = _re.match(r'skillLevel(\d+)$', b)
            if m and tf.values:
                levels[int(m.group(1))] = tf.values[0]
        lvl_by_ref = {names[i].replace('/', '\\').lower(): levels.get(i, 0) for i in names}
        # a specialAttack the AI is configured to CAST (chance>0) that points at a
        # kit skill still at level 0 is the exact "tries to cast, does nothing" bug.
        for k, tf in ff.items():
            b = k.split('###')[0]
            mm = _re.match(r'specialAttack(\d*)SkillName$', b)
            if mm and tf.values and str(tf.values[0]).strip():
                suf = mm.group(1)
                ref = str(tf.values[0]).replace('/', '\\').lower()
                ch = db.get_field_value(rec, 'specialAttack%sChance' % suf)
                ch = ch[0] if isinstance(ch, list) else ch
                if (ch or 0) > 0 and lvl_by_ref.get(ref) == 0:
                    problems.append('%s: %s (chance %s) -> level-0 skill %s'
                                    % (rec.rsplit('\\', 1)[-1], b, ch, ref.rsplit('\\', 1)[-1]))
    if problems:
        raise SystemExit('boss_skill_fix.verify: unresolved level-0 special(s):\n  '
                         + '\n  '.join(problems))
    print('  boss_skill_fix.verify: OK (no level-0 special attacks on target bosses)')
