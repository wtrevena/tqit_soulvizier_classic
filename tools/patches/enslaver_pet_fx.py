r"""enslaver_pet_fx - make the SOUL-SUMMONED Enslaver (and the marauders he raises),
plus every other soul-summon pet whose encounter twin we retinted dark, wear the
same dedicated ALL-BLACK/dark rig as that twin (b55; b55r2 adds the Hades Marshal).

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

WHAT THIS MODULE DOES  (FX field edits on 9 PET records only - no clones, no new
records, no textures authored; reuses each source monster's OWN existing shroud:
b38's dark-smoke pak for the Enslaver, the ShadowStalker shadow-cloak pak the
marauder MONSTER already wears, and the hades2_shadowcloud pak the Hades Marshal
MONSTER already wears)
-----------------------------------------------------------------------------------
For each Enslaver-family pet, per PET SAFETY LAW (only animation/skill/FX fields
are touched; no equipment/loot field is copied Monster.tpl->Pet.tpl; no explicit
dtype on set_field; the shroud is copied verbatim from the SOURCE monster's own
TypedField so the pet's field is byte-identical to the monster it mirrors):

  1. STRIP the green Lyia residue (marker-matched, so only the known-green value is
     removed - never a legit field): buffSelfSkillName(envenom), buffSelf2SkillName
     (heartofoak), healSkillName(regrowth), deathEffect(natureswrath), and (marauder
     only) specialAttackSkillName(sylvannymph nature'swrath) + the dormant kit slot
     skillName8(sylvannymph) + baseTexture(maenad). Stripping baseTexture=maenad on
     the marauder + Hades-Marshal pets falls the ShadowStalker / MachaeHero01 mesh
     back to its OWN default skin - exactly what those MONSTERS render (they define no
     baseTexture). The enslaver soul-pet's baseTexture is already the boss's
     NewSkeleton_Charcoal (marker does not match), so it is untouched. The Hades
     Marshal pet's specialAttack + kit are its source's own hades/spirit combat kit
     (hero_hadesbolt etc. - RCA'd, not green), so no green marker matches them.
  2. INHERIT the source monster's shroud: copy the SOURCE's charFxPakRunningNames
     TypedField onto the pet -> enslaver pets get svc_enslaver_darksmoke (the b38
     black smoke), marauder pets get drxshadowcloakrunning_fx_pak (the shadow cloak
     the marauder monster already wears), Hades Marshal pets get hades2_shadowcloud
     (the dark shadow-cloud the Marshal monster already wears). Each pet ends up
     with EXACTLY its own source monster's shroud (verbatim TypedField copy).
     SAFETY: this is crash-safe (charFxPakRunningNames is a pure string FX-path
     field, not the equipment/loot class that crashes a Pet.tpl; Pet.tpl is a strict
     Character superset of Monster.tpl; the field is copied verbatim with no explicit
     dtype). It reuses each source monster's OWN existing shroud - no new record, no
     texture authored. NOTE (honest scope): no in-mod PET currently carries
     charFxPakRunningNames (0 of 51,029 golden records; only 5 MONSTERs do), so
     whether the dark smoke actually RENDERS on a pet is confirmable only in Will's
     in-game test - the pet is non-green regardless (charcoal/mesh-default skin +
     green stripped), which already satisfies "green not black"; the smoke is the
     upgrade to confirm.

The enslaver soul-pet's specialAttackSkillName is NOT stripped: it is the FRIENDLY
pet-of-pet marauder summon (svc_enslaver_petmarauders, wired in _create_enslaver
step 5), which does not match any green marker.

WHY THESE 9 (scope + sibling sweep, corrected in b55r2)
-------------------------------------------------------
The green Lyia residue is SYSTEMIC: 82 of 222 soul pets carry the 4-field buff
residue (envenom/heartofoak/regrowth/natureswrath); 89 carry the module's full
marker set (adding the maenad_lyia skin + green kit slots). It is an artifact of
EVERY _build_boss_summon pet whose source lacks the field. But this module fixes
ONLY the pets whose source we DELIBERATELY retinted dark, per the sibling sweep's
precise same-class criterion: "a monster we RETINTED with a dedicated custom FX
shroud whose pet still wears the old green rig."

Ground-truth sweep of the golden arz: EXACTLY 5 records carry a custom
charFxPakRunningNames, and all 5 are MONSTERs. Of those 5, EXACTLY 3 are
_build_boss_summon soul sources whose pets kept the green rig (the three families
here): um_toxeus_enslaver_99 (svc_enslaver_darksmoke), um_enslaver_marauder_99
(drxshadowcloak), svc_um_hadesmarshal_80 (hades2_shadowcloud). The other 2 shroud
monsters have NO soul-summon pet, so nothing diverges: um_vashkarr_99
(drxshadowcloak) - its soul is a STAT _create_soul, not a summon, and its
summonhorde raises separate fodder, not a vashkarr pet; boss_satyrshaman_55
(ringofflame) - an arena APEX, referenced only by the arena pool, no soul.
=> 3 families / 9 pets. (b55r1 fixed only 2 families / 6 pets and asserted "exactly
two ... and no other"; that was FALSE - it missed the Hades Marshal. Corrected here.)

The Devourer of Blood (`bloodtoxeus_1..3`, crimson RevenantPoison) is NOT a
same-class divergence even though it SHARES the RevenantPoison mesh with the
Enslaver: its source is `um_bloodtoxeus_99` (NO custom shroud), so it was never
retinted, and its green poison is INTENTIONAL and STAYS (Will 2026-07-14). The
module never touches it. The remaining ~77 systemic green pets (source never
retinted) are FLAGGED for Will as a separate, larger design call - not mass-fixed
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

# ── the three same-class summon-pet groups: (label, source monster, [pets]) ──
# source monster = the retinted encounter twin whose custom dark shroud the pet
# must inherit. The complete universe of "retinted-dark" monsters is the FIVE
# records that carry a custom charFxPakRunningNames in the golden arz; EXACTLY
# THREE of them are _build_boss_summon soul sources whose pets kept the old green
# Lyia rig (this list). The other two shroud monsters have NO soul pet: um_vashkarr_99
# (its soul is a STAT _create_soul, not a summon; its summonhorde raises separate
# fodder, not a vashkarr pet) and boss_satyrshaman_55 (an arena APEX, no soul).
# See the sibling-sweep section below + docs/reports/b55_enslaver_pet_fx.md.
_BOSS_MON     = _R + r'creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr'
_MARAUDER_MON = _R + r'creature\monster\shadowstalker\um_enslaver_marauder_99.dbr'
# b55r2 (sibling-sweep completion): the Hades Marshal soul-summon (Menoetes,
# Marshal of the Dead - four_generals module) is the THIRD same-class divergence.
# Source svc_um_hadesmarshal_80 carries a dedicated dark hades2_shadowcloud shroud,
# but its 3 soul pets carry the IDENTICAL green Lyia residue (envenom/heartofoak/
# regrowth/natureswrath + maenad_lyia skin over the MachaeHero01 mesh) and NO shroud.
# Its combat kit (hero_hadesbolt / hero_slowspiritbolt_ring / gigantes_groundbreaker
# / lifedrain / summonarchers) is dark/spectral/physical - RCA'd, no green - so the
# existing _GREEN_MARKERS cover its every green field with no new marker needed.
_HADESMARSHAL_MON = _R + r'xpack\creatures\monster\machae\svc_um_hadesmarshal_80.dbr'
_ENSLAVER_PETS = [_R + r'skills\soulskills\pets\toxeus_enslaver_%d.dbr' % i for i in (1, 2, 3)]
_MARAUDER_PETS = [_R + r'skills\soulskills\pets\enslaver_marauder_%d.dbr' % i for i in (1, 2, 3)]
_HADESMARSHAL_PETS = [_R + r'skills\soulskills\pets\hadesmarshal_%d.dbr' % i for i in (1, 2, 3)]
_FAMILIES = [
    ('Enslaver soul-pet', _BOSS_MON,     _ENSLAVER_PETS),
    ('Enslaved Marauder pet', _MARAUDER_MON, _MARAUDER_PETS),
    ('Hades Marshal soul-pet', _HADESMARSHAL_MON, _HADESMARSHAL_PETS),
]
_ALL_PETS = _ENSLAVER_PETS + _MARAUDER_PETS + _HADESMARSHAL_PETS

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

# ── b71 CHAIN GATE (anti-oscillation) ────────────────────────────────────────
# The b55 verify() only asserted the pet FX FIELDS in isolation, so it stayed
# green while the LIVE chain diverged (Will's build44 report: wrong summon-skill
# icon, Lyia pet-bar portrait). This gate walks the FULL live chain on the FINAL
# assembled arz - soul item -> granted summon skill -> skill icon -> spawnObjects
# -> pet records -> pet-bar portrait -> zero green markers -> marauder sub-summon
# -> pets - and fails loud if ANY link drifts. The "resolves in shipped arcs" leg
# is covered by contracts_resources (which has the arc index this DB-only verify
# does not). Values below are the b71 intended end-state; keep them in lock-step
# with apply_svc_patches _SUMMON_SKILL_ICON / _SUMMON_PET_PORTRAIT.
_LYIA_PORTRAIT = 'lyia_party'  # the Lyia-clone residue portrait that must NOT survive
# (soul-item stem, granted summon skill, expected skill-icon stem, expected
#  pet-bar portrait stem, [pet records], optional (special-attack sub-summon skill,
#  [sub-pet records], expected sub-pet shroud stem))
_R2 = 'records\\'
_CHAIN = [
    {
        'label': 'Enslaver',
        'souls': [_R2 + r'item\equipmentring\soul\svc_uber\enslaver_soul_%s.dbr' % t for t in ('n', 'e', 'l')],
        'skill': _R2 + r'skills\soulskills\summon_toxeus_enslaver.dbr',
        'icon_stem': 'deathwalkersummonup',
        'portrait_stem': 'deathwalker_party_up',
        'pets': _ENSLAVER_PETS,
        'sub_skill': _R2 + r'skills\soulskills\svc_enslaver_petmarauders.dbr',
        'sub_pets': _MARAUDER_PETS,
    },
    {
        'label': 'Hades Marshal',
        'souls': [_R2 + r'item\equipmentring\soul\svc_uber\hadesmarshal_soul_%s.dbr' % t for t in ('n', 'e', 'l')],
        'skill': _R2 + r'skills\soulskills\summon_hadesmarshal.dbr',
        'icon_stem': 'wrathofthestyxup',
        'portrait_stem': 'proxy_party_up',   # neutral (no bespoke hades portrait ships)
        'pets': _HADESMARSHAL_PETS,
        'sub_skill': None,
        'sub_pets': [],
    },
    # R-43 (b85, Will 2026-07-16): "the high priest soul should allow you to
    # summon the high priest" - bwpriest_1/2/3 are now the Blood Cult High
    # Priest HIMSELF (source c_disciple_miniboss), with the Melinoe blade-dancer
    # he casts in combat rebuilt as a tamed, non-player-facing pet-of-pet
    # (bwpriest_attendant_1/2/3, mirroring this exact Enslaver/marauder shape).
    # No bespoke party portrait ships for the Priest -> neutral proxy_party
    # (same convention as 10 other unmapped bosses, incl. Hades Marshal above).
    {
        'label': 'Blood Cult High Priest',
        'souls': [_R2 + r'item\equipmentring\soul\svc_uber\bwpriest_soul_%s.dbr' % t for t in ('n', 'e', 'l')],
        'skill': _R2 + r'skills\soulskills\summon_bwpriest.dbr',
        'icon_stem': 'bloodbathup',
        'portrait_stem': 'proxy_party_up',
        'pets': [_R2 + r'skills\soulskills\pets\bwpriest_%d.dbr' % i for i in (1, 2, 3)],
        'sub_skill': _R2 + r'skills\soulskills\svc_bwpriest_summonmelinoe.dbr',
        'sub_pets': [_R2 + r'skills\soulskills\pets\bwpriest_attendant_%d.dbr' % i for i in (1, 2, 3)],
    },
]


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


def _field1(db, rec, base):
    """First value of field `base` on `rec` (case-insensitive, ###-suffix aware), or None."""
    if not db.has_record(rec):
        return None
    fields = db.get_fields(rec) or {}
    for k in fields:
        if k.split('###')[0].lower() == base.lower() and fields[k].values:
            return str(fields[k].values[0])
    return None


def _stem(path):
    return (path or '').replace('/', '\\').rsplit('\\', 1)[-1].replace('.dbr', '').replace('.tex', '').lower()


def _green_residue_on(db, pet):
    """Return a list of green-residue problem strings for a single pet record
    (FX-field markers + dormant green kit slots). Empty == clean."""
    out = []
    fields = db.get_fields(pet) or {}
    for base_lower, needles in _GREEN_MARKERS.items():
        for key in _iter_field_keys(fields, base_lower):
            val = str(fields[key].values[0]) if fields[key].values else ''
            if any(n in val.lower() for n in needles):
                out.append('%s: GREEN residue %s=%s' % (pet.rsplit('\\', 1)[-1], base_lower, val.rsplit('\\', 1)[-1]))
    for base, val in _green_kit_slots(fields):
        out.append('%s: GREEN kit slot %s=%s' % (pet.rsplit('\\', 1)[-1], base, val.rsplit('\\', 1)[-1]))
    return out


def _verify_chain(db, problems):
    """b71 anti-oscillation: walk the LIVE soul->skill->icon->pets->portrait->green
    ->marauder chain on the FINAL db for each family in _CHAIN. Appends to problems."""
    for spec in _CHAIN:
        lbl = spec['label']
        skill = spec['skill']
        # (a) every soul tier grants the expected summon skill
        for soul in spec['souls']:
            if not db.has_record(soul):
                continue  # an absent soul tier is a separate upstream failure
            gs = (_field1(db, soul, 'itemSkillName') or '').replace('/', '\\').lower()
            if gs != skill.lower():
                problems.append('%s CHAIN: %s grants %s, expected %s'
                                % (lbl, soul.rsplit('\\', 1)[-1], gs or '<none>', skill.rsplit('\\', 1)[-1]))
        if not db.has_record(skill):
            problems.append('%s CHAIN: granted skill absent: %s' % (lbl, skill))
            continue
        # (b) skill icon == expected skeleton/identity (never the Lyia nymph)
        up = _stem(_field1(db, skill, 'skillUpBitmapName'))
        if up != spec['icon_stem']:
            problems.append('%s CHAIN: skill icon %s != expected %s' % (lbl, up or '<none>', spec['icon_stem']))
        # (c) spawnObjects == the expected pet set
        so = db.get_field_value(skill, 'spawnObjects')
        so_list = [str(x).replace('/', '\\').lower() for x in (so if isinstance(so, list) else [so] if so else [])]
        want = [p.lower() for p in spec['pets']]
        if so_list != want:
            problems.append('%s CHAIN: spawnObjects %s != expected pets %s'
                            % (lbl, [s.rsplit('\\', 1)[-1] for s in so_list], [w.rsplit('\\', 1)[-1] for w in want]))
        # (d) each pet: portrait == expected (never Lyia) AND zero green residue
        for pet in spec['pets']:
            if not db.has_record(pet):
                continue
            si = _stem(_field1(db, pet, 'StatusIcon'))
            if _LYIA_PORTRAIT in (si or ''):
                problems.append('%s CHAIN: %s pet-bar portrait still Lyia (%s)' % (lbl, pet.rsplit('\\', 1)[-1], si))
            elif si != spec['portrait_stem']:
                problems.append('%s CHAIN: %s portrait %s != expected %s'
                                % (lbl, pet.rsplit('\\', 1)[-1], si or '<none>', spec['portrait_stem']))
            # StatusIconRed is the down-variant texture of the SAME identity
            # (vanilla convention), so assert identity prefix, not the up-stem.
            sir = _stem(_field1(db, pet, 'StatusIconRed'))
            ident = spec['portrait_stem'][:-2] if spec['portrait_stem'].endswith('up') else spec['portrait_stem']
            if _LYIA_PORTRAIT in (sir or ''):
                problems.append('%s CHAIN: %s StatusIconRed still Lyia (%s)' % (lbl, pet.rsplit('\\', 1)[-1], sir))
            elif not (sir or '').startswith(ident):
                problems.append('%s CHAIN: %s StatusIconRed %s not identity %s'
                                % (lbl, pet.rsplit('\\', 1)[-1], sir or '<none>', ident))
            problems.extend(_green_residue_on(db, pet))
        # (e) marauder sub-summon: subchain pets also zero-green
        if spec['sub_skill'] and db.has_record(spec['sub_skill']):
            sub_so = db.get_field_value(spec['sub_skill'], 'spawnObjects')
            sub_list = [str(x).replace('/', '\\') for x in (sub_so if isinstance(sub_so, list) else [sub_so] if sub_so else [])]
            want_sub = [p.lower() for p in spec['sub_pets']]
            if [s.lower() for s in sub_list] != want_sub:
                problems.append('%s CHAIN: sub-summon spawnObjects %s != expected %s'
                                % (lbl, [s.rsplit('\\', 1)[-1] for s in sub_list], [w.rsplit('\\', 1)[-1] for w in want_sub]))
            for spet in spec['sub_pets']:
                if db.has_record(spet):
                    problems.extend(_green_residue_on(db, spet))


def apply(db, tags):
    assert hasattr(db, 'record_names') and hasattr(db, 'set_field'), \
        'enslaver_pet_fx.apply: db is not an ArzDatabase'
    print('\n=== b55 enslaver_pet_fx: black-rig the soul-summoned Enslaver + marauders '
          '+ Hades Marshal (b55r2) ===')
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
    """POST-FINALIZATION fail-loud gate (run_registry_verifies). Over EVERY pet in
    the three families (Enslaver soul-pet, Enslaved Marauder, Hades Marshal soul-pet)
    that exists in the FINAL assembled db, assert:
      (1) NO green Lyia-residue field survives (marker-matched), and
      (2) the pet carries the matching dark shroud in charFxPakRunningNames
          (svc_enslaver_darksmoke for the enslaver soul-pet, drxshadowcloak for the
          marauder pet, hades2_shadowcloud for the Hades Marshal pet - each == its
          OWN source monster's shroud).
    Negative-tested: planting envenomweapon back on any pet, or clearing/altering the
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
    # b71 anti-oscillation CHAIN GATE: walk the full live soul->skill->icon->pets
    # ->portrait->green->marauder chain (catches the record-level-vs-chain-level gap
    # that let build44 ship the wrong summon icon + Lyia pet-bar portrait).
    _verify_chain(db, problems)
    if problems:
        raise SystemExit('enslaver_pet_fx.verify FAILED:\n  ' + '\n  '.join(problems))
    print('  enslaver_pet_fx.verify: OK (Enslaver + marauder soul-pets carry the '
          'black shroud, zero green Lyia residue; chain icon+portrait on-identity '
          'across all %d rostered families incl. R-43 Blood Cult High Priest)'
          % len(_CHAIN))
