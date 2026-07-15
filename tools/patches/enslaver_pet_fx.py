r"""enslaver_pet_fx - make the SOUL-SUMMONED Enslaver (and the marauders he raises)
wear the same dedicated ALL-BLACK rig as their encounter-monster twins (b55).

WHY THIS EXISTS (RCA in docs/reports/b55_enslaver_pet_fx.md)
------------------------------------------------------------
Will (2026-07-14): "toxeus the murderer enslaver of souls has green glow not black
like we said ... this is when i summon him from his soul" + "his poison effect is
still green, it is not the custom black one we wanted to make for him."

b38 (b38_enslaver_v2 + _create_enslaver) gave the ENCOUNTER monster
`um_toxeus_enslaver_99` a dedicated all-black rig: charcoal skeleton skin +
`charFxPakRunningNames = svc_enslaver_darksmoke_charfxpak` (a black-smoke shroud
recoloured to 343_dark_smoke) and DELETED its inherited green weapon glow
(initialSkillName=toxeus_envenomweapon). Verified present in the golden build40 arz
(um_toxeus_enslaver_99.charFxPakRunningNames = the dark-smoke pak; no buffSelf; no
green initialSkill; no deathEffect). That fix operated ONLY on the fought monster.

The SOUL-SUMMON PET (`toxeus_enslaver_1..3`) and the friendly marauders it raises
(`enslaver_marauder_1..3`) are BUILT SEPARATELY by `_build_boss_summon`, which
clones the Lyia Leafsong pet (a Maenad poison/nature caster) for a crash-safe
Pet.tpl baseline and then copies ONLY anim + skill-slot refs from the source
monster. The Lyia base carries these GREEN fields, and NONE of them is in the
builder's copy set (`_SKILL_PREFIXES` = skillName/attackSkill/specialAttack/
buffSelf/initialSkill), because the SOURCE monster does not define them, so
`_update_existing_fields` never overwrites them and they survive as residue:

  * buffSelfSkillName  = records\skills\stealth\envenomweapon.dbr
        -> Skill_BuffSelfToggled, skillWeaponTintGreen=1.0 (+Red/Blue 0.25) AND
           charFxPakSelfNames -> 343_weapon_poisoncharfxpak -> 343_Weapon_PoisonFX
           = a GREEN weapon-poison shroud the pet auto-casts (always on). THIS is
           Will's "his poison effect is still green" (same green profile as the
           toxeus_envenomweapon b38 deleted off the boss).
  * buffSelf2SkillName = records\skills\nature\heartofoak.dbr  (green FeralSpirit aura)
  * healSkillName      = records\skills\nature\regrowth_lyia.dbr  (green Regrowth heal FX)
  * deathEffect        = records\effects\nature\343_natureswrath_low_fx.dbr  (green
                         nature death; record is MISSING in the arz so it renders
                         nothing today, but it is wrong residue + a dangling ref)
  * (marauder pets only) specialAttackSkillName = sylvannymph_petskill_nature'swrath
                         (green nature AoE) AND baseTexture = maenad_lyia.tex (the
                         WRONG Lyia skin painted over the ShadowStalker demon mesh)

And crucially the pet was MISSING `charFxPakRunningNames` entirely, so it never
inherited the boss's black-smoke shroud (charFxPakRunningNames is not in the
builder's copy set). Net: the summon looked like a black skeleton emitting a GREEN
poison-weapon glow + green nature FX and no black smoke.

The kit skills the pet SHARES with the boss (toxeus_attackskill, netherstrike,
toxeus_bladestorm, chain phantomstrike/toxeus_distortreality, lifedrain,
flashpowder, lethalstrike) were RCA'd and are NOT green (nether/shadow, dream,
chaos-beam, knives) - consistent with Will confirming the ENCOUNTER is now black.
So the green is 100% pet-specific Lyia residue; the fix lives entirely on the PET
records.

WHAT THIS MODULE DOES  (FX field edits on 6 PET records only - no clones, no new
records, no textures authored; reuses b38's own dark-smoke pak + the ShadowStalker
shadow-cloak pak the marauder MONSTER already wears)
-----------------------------------------------------------------------------------
For each Enslaver-family pet, per PET SAFETY LAW (only animation/skill/FX fields
are touched; no equipment/loot field is copied Monster.tpl->Pet.tpl; no explicit
dtype on set_field; the shroud is copied verbatim from the SOURCE monster's own
TypedField so the pet's field is byte-identical to the monster it mirrors):

  1. STRIP the green Lyia residue (marker-matched, so only the known-green value is
     removed - never a legit field): buffSelfSkillName(envenom), buffSelf2SkillName
     (heartofoak), healSkillName(regrowth), deathEffect(natureswrath), and (marauder
     only) specialAttackSkillName(sylvannymph nature'swrath) + baseTexture(maenad).
     Stripping baseTexture=maenad on the marauder pet falls the ShadowStalker mesh
     back to its OWN default demon skin - exactly what the marauder MONSTER renders
     (it defines no baseTexture). The enslaver soul-pet's baseTexture is already the
     boss's NewSkeleton_Charcoal (marker does not match), so it is untouched.
  2. INHERIT the source monster's shroud: copy the SOURCE's charFxPakRunningNames
     TypedField onto the pet -> enslaver pets get svc_enslaver_darksmoke (the b38
     black smoke), marauder pets get drxshadowcloakrunning_fx_pak (the shadow cloak
     the marauder monster already wears). This is the "pet inherits its monster's
     shroud" fix and is the same charFxPakRunningNames-on-a-pet route already proven
     safe by the Vashkarr/marauder-monster shrouds.

The soul-pet's specialAttackSkillName is NOT stripped: it is the FRIENDLY
pet-of-pet marauder summon (svc_enslaver_petmarauders, wired in _create_enslaver
step 5), which does not match any green marker.

WHY ONLY THESE 6 (scope + sibling sweep)
----------------------------------------
The green Lyia residue is SYSTEMIC: 82 of 222 soul pets carry it (every
_build_boss_summon pet whose source lacks the field). But this module deliberately
fixes ONLY the Enslaver family, because the sibling sweep's precise same-class
criterion - "a monster we RETINTED with a dedicated custom FX shroud whose pet
still wears the old rig" - matches EXACTLY these two source monsters and no other:
`um_toxeus_enslaver_99` (custom svc_enslaver_darksmoke shroud) and
`um_enslaver_marauder_99` (custom drxshadowcloak shroud). Every other
_build_boss_summon source has NO custom charFxPakRunningNames, so its green pet
residue is the broader systemic artifact, not a contradiction of a deliberate
non-green identity. In particular the Devourer of Blood (`bloodtoxeus_1..3`,
crimson RevenantPoison) is EXPLICITLY EXCLUDED: the original Toxeus green poison
rig is intentional there and STAYS (Will 2026-07-14). The systemic 82-pet finding
is reported in the RCA as a separate, larger design call for Will, not mass-fixed
in this crash-history pet round.

ITEM vs PET record: the summon FX rides entirely on the PET records (resolved LIVE
from the DB when the granted summon skill fires), NOT on the soul ITEM. So the fix
reaches Will's EXISTING Enslaver soul - no fresh drop needed; a Steam restart to
reload the arz is enough.

REGISTRY ORDER: runs late (immediately before `visuals`, which writes nothing),
after the monolith built the pets and after every boss-creating module, so it edits
the FINAL pet records. Its verify() runs post-finalization (run_registry_verifies).
"""

MODULE_NAME = 'enslaver_pet_fx'

_R = 'records\\'

# ── the two Enslaver-family summon-pet groups: (label, source monster, [pets]) ──
# source monster = the retinted encounter twin whose shroud the pet must inherit.
_BOSS_MON     = _R + r'creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr'
_MARAUDER_MON = _R + r'creature\monster\shadowstalker\um_enslaver_marauder_99.dbr'
_ENSLAVER_PETS = [_R + r'skills\soulskills\pets\toxeus_enslaver_%d.dbr' % i for i in (1, 2, 3)]
_MARAUDER_PETS = [_R + r'skills\soulskills\pets\enslaver_marauder_%d.dbr' % i for i in (1, 2, 3)]
_FAMILIES = [
    ('Enslaver soul-pet', _BOSS_MON,     _ENSLAVER_PETS),
    ('Enslaved Marauder pet', _MARAUDER_MON, _MARAUDER_PETS),
]
_ALL_PETS = _ENSLAVER_PETS + _MARAUDER_PETS

# ── green Lyia-clone residue markers: field base (lower) -> substrings that mark
#    the value as the known green residue. A field is stripped IFF its value
#    contains one of these substrings, so a legitimately-black field is never
#    touched. (basetexture/maenad + specialattackskillname/sylvannymph only ever
#    match the marauder pets; the enslaver soul-pet's charcoal skin + friendly
#    marauder-summon special do not match.)
_GREEN_MARKERS = {
    'buffselfskillname':      ('envenom',),
    'buffself2skillname':     ('heartofoak',),
    'healskillname':          ('regrowth',),
    'deatheffect':            ('natureswrath',),
    'specialattackskillname': ('sylvannymph', "nature'swrath"),
    'basetexture':            ('maenad',),
}
# Green skills that may ALSO sit in a `skillName<N>` KIT slot (the Lyia mirror of
# the specialAttack green nature'swrath): a skillName slot holding one of these is
# stripped (with its paired skillLevel<N>) so no controller that scans the kit can
# ever fire it. Only the marauder pet carries such a slot (skillName8); the enslaver
# soul-pet's kit is the toxeus melee/summon kit (no green slot).
_GREEN_KIT_NEEDLES = ('sylvannymph', "nature'swrath", 'natureswrath')
_SHROUD_FIELD = 'charFxPakRunningNames'


def _iter_field_keys(fields, base_lower):
    """All raw keys (incl. ###N suffix variants) whose base name == base_lower."""
    return [k for k in list(fields) if k.split('###')[0].lower() == base_lower]


def _green_kit_slots(fields):
    """(base_name, value) for every skillName<N> slot whose value is a green kit
    skill. Deterministic over the ordered field dict."""
    out = []
    for k in list(fields):
        base = k.split('###')[0]
        if base.lower().startswith('skillname') and base[9:].isdigit() and fields[k].values:
            val = str(fields[k].values[0])
            if any(n in val.lower() for n in _GREEN_KIT_NEEDLES):
                out.append((base, val))
    return out


def _strip_green(db, pet):
    """Remove every green-marked residue field from a pet record. Returns the list
    of (field, value) stripped. Direct dict-key deletion -> field ABSENT in the
    re-encoded record (write_arz re-encodes _modified from the decoded cache; a
    deleted key is simply not emitted)."""
    fields = db.get_fields(pet)
    if not fields:
        return []
    stripped = []
    for base_lower, needles in _GREEN_MARKERS.items():
        for key in _iter_field_keys(fields, base_lower):
            tf = fields[key]
            val = str(tf.values[0]) if tf.values else ''
            if any(n in val.lower() for n in needles):
                del fields[key]
                stripped.append((key.split('###')[0], val.rsplit('\\', 1)[-1].rsplit('/', 1)[-1]))
    # dormant green kit slots: strip skillName<N> (+ its paired skillLevel<N>) that
    # holds a green nature'swrath skill, so it can never be fired by any controller.
    for base, val in _green_kit_slots(fields):
        idx = base[9:]
        for k in _iter_field_keys(fields, base.lower()) + _iter_field_keys(fields, ('skillLevel' + idx).lower()):
            del fields[k]
        stripped.append((base, val.rsplit('\\', 1)[-1]))
    if stripped:
        db._modified.add(pet)
    return stripped


def _inherit_shroud(db, pet, source):
    """Copy the SOURCE monster's charFxPakRunningNames TypedField verbatim onto the
    pet (dtype + values), so the pet wears exactly the monster's shroud. Idempotent.
    Returns the shroud value set, or None if the source carries no shroud."""
    src_fields = db.get_fields(source) or {}
    src_key = next((k for k in src_fields
                    if k.split('###')[0].lower() == _SHROUD_FIELD.lower()
                    and src_fields[k].values), None)
    if src_key is None:
        return None
    src_tf = src_fields[src_key]
    shroud_val = str(src_tf.values[0])
    pet_fields = db.get_fields(pet)
    if pet_fields is None:
        return None
    # remove any existing shroud key(s) then install a fresh copy of the source's
    for k in _iter_field_keys(pet_fields, _SHROUD_FIELD.lower()):
        del pet_fields[k]
    from arz_patcher import TypedField
    pet_fields[_SHROUD_FIELD] = TypedField(src_tf.dtype, list(src_tf.values))
    db._modified.add(pet)
    return shroud_val.rsplit('\\', 1)[-1]


def apply(db, tags):
    assert hasattr(db, 'record_names') and hasattr(db, 'set_field'), \
        'enslaver_pet_fx.apply: db is not an ArzDatabase'
    print('\n=== b55 enslaver_pet_fx: black-rig the soul-summoned Enslaver + marauders ===')
    touched = 0
    for label, source, pets in _FAMILIES:
        if not db.has_record(source):
            # the whole enslaver group was skipped upstream (donor missing) - nothing
            # to repoint; leave a note, verify() will only assert over pets that exist.
            print('  [skip] %-22s source monster absent: %s' % (label, source))
            continue
        for pet in pets:
            if not db.has_record(pet):
                print('  [skip] %-22s pet absent: %s' % (label, pet.rsplit('\\', 1)[-1]))
                continue
            stripped = _strip_green(db, pet)
            shroud = _inherit_shroud(db, pet, source)
            touched += 1
            name = pet.rsplit('\\', 1)[-1]
            sg = ', '.join('%s=%s' % (f, v) for f, v in stripped) or '(none)'
            print('  [black]  %-24s strip: %s' % (name, sg))
            print('           %-24s shroud <- %s' % ('', shroud or '<source has none>'))
    print('  enslaver_pet_fx: repointed %d pet(s) to the black rig' % touched)


def verify(db, tags=None):
    """POST-FINALIZATION fail-loud gate (run_registry_verifies). Over EVERY
    Enslaver-family pet that exists in the FINAL assembled db, assert:
      (1) NO green Lyia-residue field survives (marker-matched), and
      (2) the pet carries the matching black shroud in charFxPakRunningNames
          (svc_enslaver_darksmoke for the soul-pet, drxshadowcloak for the marauder
          pet - each == its source monster's shroud).
    Negative-tested: planting envenomweapon back on any pet, or clearing the
    shroud, fails this gate."""
    problems = []
    for label, source, pets in _FAMILIES:
        src_shroud = None
        if db.has_record(source):
            sf = db.get_fields(source) or {}
            k = next((kk for kk in sf
                      if kk.split('###')[0].lower() == _SHROUD_FIELD.lower() and sf[kk].values), None)
            if k:
                src_shroud = str(sf[k].values[0]).replace('/', '\\').lower()
        for pet in pets:
            if not db.has_record(pet):
                # enslaver group not built at all (donor missing) is a separate
                # upstream failure the group's own build guards catch; not this
                # module's to assert. Only flag if SOME of the family built.
                continue
            fields = db.get_fields(pet) or {}
            # (1) no green residue: FX fields + dormant green kit slots
            for base_lower, needles in _GREEN_MARKERS.items():
                for key in _iter_field_keys(fields, base_lower):
                    val = str(fields[key].values[0]) if fields[key].values else ''
                    if any(n in val.lower() for n in needles):
                        problems.append('%s: GREEN residue survived %s=%s'
                                        % (pet.rsplit('\\', 1)[-1], base_lower, val.rsplit('\\', 1)[-1]))
            for base, val in _green_kit_slots(fields):
                problems.append('%s: GREEN kit slot survived %s=%s'
                                % (pet.rsplit('\\', 1)[-1], base, val.rsplit('\\', 1)[-1]))
            # (2) matching black shroud present
            pk = next((kk for kk in fields
                       if kk.split('###')[0].lower() == _SHROUD_FIELD.lower() and fields[kk].values), None)
            if pk is None:
                problems.append('%s: missing %s (black shroud not inherited)'
                                % (pet.rsplit('\\', 1)[-1], _SHROUD_FIELD))
            elif src_shroud is not None:
                pv = str(fields[pk].values[0]).replace('/', '\\').lower()
                if pv != src_shroud:
                    problems.append('%s: shroud %s != source shroud %s'
                                    % (pet.rsplit('\\', 1)[-1], pv.rsplit('\\', 1)[-1],
                                       src_shroud.rsplit('\\', 1)[-1]))
    if problems:
        raise SystemExit('enslaver_pet_fx.verify FAILED:\n  ' + '\n  '.join(problems))
    print('  enslaver_pet_fx.verify: OK (Enslaver + marauder soul-pets carry the '
          'black shroud, zero green Lyia residue)')
