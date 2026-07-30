r"""enslaver_shroud - THE ENSLAVER'S BLACK SHROUD (b98, R-95).

WILL (2026-07-28), verbatim fragment: he wants the Enslaver to have
    "the same black shroud smoke his summoned demons have"

--------------------------------------------------------------------------------
THE FINDING THAT CHANGES THE TASK: HE ALREADY HAS THE FX
--------------------------------------------------------------------------------
`records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr` already carries
    charFxPakRunningNames = records\skills\stealth\drxpet\drx_pet_fx\
                            drxshadowcloakrunning_fx_pak.dbr
which is the SAME pak, pointing at the SAME EffectEntity
(`drxshadowcloakrunning_fx` -> `DRXeffects\shadowcloakrunning.pfx`, boneList
Bone_R_Weapon;Bone_L_Weapon), that `um_enslaver_marauder_99` carries. Only 14
records in the whole 51,098-record DB carry `charFxPakRunningNames` and he is one
of them. So the ask is NOT "give him the FX" - it is "make the FX he already has
actually show".

TWO CANDIDATE CAUSES; ONE ELIMINATED FROM THE ASSET BYTES.
  * ELIMINATED - bone mismatch. Both `Bone_R_Weapon` and `Bone_L_Weapon` exist on
    RevenantPoison.msh (the Enslaver's rig) exactly as they do on ShadowStalker.msh
    (the marauders'). The FX binds fine. Reported as wrong rather than shipped.
    (Worth keeping for future FX work: the WAIST attach point is named "Smoke02" on
    ShadowStalker and "Waist" on RevenantPoison, so a body-shroud FX targeting
    "Smoke02" would work on the marauders and silently do nothing on him.)
  * SURVIVING CAUSE - THE CHANNEL. `charFxPakRunningNames` renders ONLY while the
    character is RUNNING. The marauders are melee chasers that run at you
    constantly, so they smoke continuously. The Enslaver is a caster -
    characterSpellCastSpeed 2.0, summons marauders, full armour, run speed 1.5 -
    who stands and casts. His running FX almost never plays.

--------------------------------------------------------------------------------
THE FIX, ON A SHIPPED IN-HOUSE PATTERN
--------------------------------------------------------------------------------
`charFxPakSelfNames` is the PERSISTENT channel, and it is a SKILL field, never a
Monster field (184 carriers DB-wide, ZERO of them Monster-class). So the shipped way
to put a persistent FX on a monster's body is a self-buff SKILL in one of its skill
slots - which is exactly what R-7 already did for the Devourer with
`svc_black_poison` (Skill_BuffSelfToggled -> charFxPakSelfNames -> a CharFxPak).

  1. `records\skills\monster skills\buff_self\svc_enslaver_shroud.dbr` -
     Skill_BuffSelfToggled cloned from `empusamerc_enchantment`, the ONE shipped
     zero-payload self-buff toggle in this exact namespace (0 non-zero
     offensive/defensive/character fields), so the shroud carries NO combat payload
     at all. This is a VISUAL skill and only a visual skill. The donor's purple
     weapon tint (0.9, 0.1, 1.0) is zeroed to (0,0,0), which the b83 tint model
     established as the inert "NO TINT" default (195 shipped records) - a zero
     channel is OFF, not black, so this cannot recolour his weapon.
  2. `records\skills\monster skills\buff_self\svc_enslaver_shroud_charfxpak.dbr` -
     a CharFxPak cloned from the shipped `343_weapon_poisoncharfxpak` structure,
     with the particle swapped to the marauders' own `drxshadowcloakrunning_fx`
     AND the donor's attach points dropped (see ROUND 4 below).
     NOTE THE FORMAT DIFFERENCE, easy to get wrong: a CharFxPak uses
     `particleEffectAttachPoints` with FRIENDLY names ("R Hand"), whereas an
     EffectEntity uses `boneList` with raw bone names ("Bone_R_Weapon"). They are
     not interchangeable.

     ⚠️ ROUND 4 SHAPE FIX (adversarial-vet finding, 2026-07-29). Rounds 1-3 kept
     the donor's `'R Hand';'L Hand'` pair, so the Enslaver smoked from two FISTS
     while his marauders smoke from the whole BODY. The colour half of Will's ask
     was right and the shape half was not, and nothing in this file noticed,
     because every gate here checked the particle IDENTITY and none checked the
     emission SHAPE. Will asked for "the same black shroud smoke his summoned
     demons have"; same means same shape too. Read out of the built arz:
     `drxshadowcloakrunning_fx_pak` (Class FxPak) carries `particleEffectNames`
     x1 and NO `particleEffectAttachPoints` at all. The pak now mirrors that -
     one body emitter, zero attach points - and verify() DERIVES the expectation
     from the demons' live record, so if their shroud ever changes shape this
     fails loud instead of drifting. Convention check before making the change:
     of the 294 resolvable `charFxPakSelfNames` references in the DB, 248 point
     at an attach-free pak and 46 at one with attach points; 86 of the 131
     CharFxPak records omit the field entirely, and none carries an empty one -
     hence ABSENCE rather than an empty list.
     STILL NOT CLAIMED: what this looks like IN GAME. The shape now matches the
     demons' by construction and by gate, but nobody has seen it (BL-b98-DEBT-2
     below covers the colour; the shape inherits the same launch gate).
  3. Wired into the LOWEST FREE `skillName` slot on the Enslaver. NO SKILL IS
     DROPPED TO MAKE ROOM - the design brief assumed all 12 of his slots were full
     and that one would have to be sacrificed under R-26's spirit. GROUND TRUTH: he
     uses skillName1..18 and the Monster template goes to at least 23 (um_mnemophage_99
     uses skillName23), so slot 19 is free and no functional skill is touched.
  4. `charFxPakRunningNames` is KEPT as-is, so he smokes harder when he moves and
     still matches the marauders he commands.

His controller (`controller_skeleton_toxeus`) carries BuffSelfBehavior =
'WhenEnemyIsSeen', so the toggle fires the moment the fight starts.

--------------------------------------------------------------------------------
COLOUR: THE ONLY IN-GAME-CONFIRMED BLACK IN THIS WHOLE AREA
--------------------------------------------------------------------------------
The player-surface checklist forbids claiming a colour from a non-in-game-confirmed
asset. `343_dark_smoke` (the Devourer's shipped black poison particle) is explicitly
NOT confirmed - R-10 calls it "the green-rendering 343_dark_smoke" and black_poison's
own docstring flags it (BP-SMOKE-1). `hades2_shadowcloud_charfxpak` is not confirmed
either. `DRXeffects\shadowcloakrunning.pfx` IS: Will has SEEN it, on the marauders,
and called it "the black shroud smoke". That is why this module uses it and nothing
else, and it is also literally what he asked for.

--------------------------------------------------------------------------------
THE BLOCKER THIS MODULE CANNOT CLEAR (reported, NOT silently deferred)
--------------------------------------------------------------------------------
b92 proved from asset bytes that `Creatures\Monster\Skeleton\RevenantPoison.msh` -
the mesh the Enslaver wears in the DEPLOYED arz - ends with
`CreateEntity { attach = "Waist"; entity = "...RevenantPoison_FX.dbr" }` ->
`Effects\MonsterFX\Buffs\RevenantPoison.pfx`, whose colour keyframes decode to
R 0.534 / G 1.000 / B 0.591 = GREEN, compiled INTO THE MESH FILE and therefore
invisible to any .arz scan. Black body-smoke over a green waist aura will not read
as a black shroud - and after the round-4 shape fix the two now occupy the SAME
space (both body-centred, the mesh aura at the waist), so if anything the mesh
green matters more, not less.
That mesh work belongs to the green-diff lane (b92, commit 60d7789, reachable only
from tag build53-dev and NOT deployed) and turns on a Will answer about giving each
champion a different aura-free mesh. It is registered as BL-b98-DEBT-2. NO REPORT
FROM THIS LANE MAY CLAIM THE ENSLAVER READS BLACK until Will has looked at him in
game with the mesh question settled.

--------------------------------------------------------------------------------
b102 / R-102 SECOND AMENDMENT - THE SHROUD REACHED THE MONSTER AND NOTHING ELSE
--------------------------------------------------------------------------------
WILL, VERBATIM:

> "no the black is not the demon shroud i asked for, that is still not implemented.
>  the black is something else"

HE WAS RIGHT AND THIS MODULE WAS WRONG. Measured on the built arz: the shroud sat
in the MONSTER's slot 19 and on NONE of the three `pets\toxeus_enslaver_*` tiers.
Will summons the PET. So from where he stands the request was simply never
delivered, and the black he did see was the pre-existing DRX
`charFxPakRunningNames` the pet records already carried - "the black is something
else", exactly.

The blocker above is also LIFTED: R-102's fourth amendment exonerated this pak as
a green source (Will: "the demons that he summons have the proper black shroud and
they dont have any green" - they carry the byte-identical pak), and the b102
`champion_mesh` module removes the mesh-embedded green underneath it. So the
shroud can now be claimed as black on the FX side; what still needs Will's EYE is
only how it reads on the new mesh.

WHAT CHANGED HERE (one idea, not a list): the shroud is wired to a ROSTER, and the
roster is DERIVED - the monster plus every tier read out of
`summon_toxeus_enslaver.spawnObjects` at build time. A 4th tier appended to that
summon is picked up by the fix and by the gate with no code change, which is the
only way "a future tier cannot be skipped" can be true of anything.
Each pet gets the shroud in ITS OWN lowest free `skillName` slot (they use 1-12
and 15; nothing is dropped, R-26's spirit), and their controller
`controller_skelly_aggressive` carries `BuffSelfBehavior = WhenEnemyIsSeen`, the
same trigger the monster's controller uses - so the toggle actually fires on a
summoned pet rather than sitting inert in a slot.
"""

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))   # tools/ on path

MODULE_NAME = "Enslaver persistent black shroud (R-95)"

DATA_TYPE_INT = 0
DATA_TYPE_FLOAT = 1
DATA_TYPE_STRING = 2

_ENSLAVER = r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr'
_MARAUDER = r'records\creature\monster\shadowstalker\um_enslaver_marauder_99.dbr'
# b102 (R-102 second amendment): the surface Will actually looks at. The pet TIERS
# are never listed - they are read out of this summon's spawnObjects, so the
# roster cannot go stale when a tier is added.
_ENSLAVER_SUMMON = r'records\skills\soulskills\summon_toxeus_enslaver.dbr'
# The pets' AI controller. Named here because a self-buff toggle is inert without
# a controller that fires it; the gate asserts this rather than assuming it.
_PET_CONTROLLER_BUFF_TRIGGER = 'WhenEnemyIsSeen'

# the in-game-CONFIRMED black: the smoke Will saw on the marauders
_SHADOWCLOAK_FX = r'records\skills\stealth\drxpet\drx_pet_fx\drxshadowcloakrunning_fx.dbr'
_SHADOWCLOAK_PAK = r'records\skills\stealth\drxpet\drx_pet_fx\drxshadowcloakrunning_fx_pak.dbr'

# structure donors (both DB-verified)
_SKILL_DONOR = r'records\skills\monster skills\buff_self\empusamerc_enchantment.dbr'
_PAK_DONOR = r'records\effects\weaponenchantments\343_weapon_poisoncharfxpak.dbr'

_SHROUD = r'records\skills\monster skills\buff_self\svc_enslaver_shroud.dbr'
_SHROUD_PAK = r'records\skills\monster skills\buff_self\svc_enslaver_shroud_charfxpak.dbr'

# ── SHAPE (round 4 fix; see the ROUND 4 block in the docstring) ─────────────
# The demons' own pak emits from the WHOLE BODY: `drxshadowcloakrunning_fx_pak`
# carries `particleEffectNames` x1 and NO `particleEffectAttachPoints` at all.
# Round 1 cloned the 343 weapon-enchantment pak's STRUCTURE wholesale and kept
# its 'R Hand';'L Hand' attach pair, so the Enslaver smoked from two hands while
# his marauders smoked from the body - the colour half of Will's ask was right
# and the SHAPE half was not. Measured off the built arz before changing it:
# of the 294 resolvable `charFxPakSelfNames` references in the DB, 248 point at a
# pak with NO attach points and only 46 at one with any; all 14
# `charFxPakRunningNames` references (the demons' channel) are attach-free. So
# body-centred is both the faithful answer and the overwhelming convention.
_ATTACH = []            # [] == emit from the body, exactly like the demons' pak
_PARTICLE_COUNT = 1     # one entry, matching drxshadowcloakrunning_fx_pak x1


def _norm(p):
    return str(p).replace('/', '\\').lower()


def _gv1(db, rec, f):
    v = db.get_field_value(rec, f)
    return v[0] if isinstance(v, list) and v else v


def _require(db, *recs):
    missing = [r for r in recs if not db.has_record(r)]
    if missing:
        raise SystemExit("[enslaver_shroud] required record(s) missing: %s" % missing)


def _free_skillname_slot(db, rec, lo=1, hi=23):
    ff = db.get_fields(rec) or {}
    used = set()
    for k, tf in ff.items():
        b = k.split('###')[0]
        if b.startswith('skillName') and b[9:].isdigit() and tf.values \
                and str(tf.values[0]).strip():
            used.add(int(b[9:]))
    for i in range(lo, hi + 1):
        if i not in used:
            return i
    return None


def _slot_of(db, rec, skill):
    want = _norm(skill)
    ff = db.get_fields(rec) or {}
    for k, tf in ff.items():
        b = k.split('###')[0]
        if b.startswith('skillName') and b[9:].isdigit() and tf.values \
                and _norm(tf.values[0]) == want:
            return int(b[9:])
    return None


def _del_field(db, rec, name):
    """Remove a field slot entirely rather than blanking it to ''.

    Same rule the sibling module uses (B-TOXEUS-2): a live reference blanked to
    the empty string is a loader hazard, an ABSENT field is the shipped way to
    say "this record does not use this". 86 of the 131 CharFxPak records in the
    DB simply omit `particleEffectAttachPoints`; none of them carries an empty
    one, so absence - not emptiness - is the precedented shape.
    """
    ff = db.get_fields(rec)
    if not ff:
        return False
    hit = False
    for k in list(ff):
        if k.split('###')[0] == name:
            del ff[k]
            hit = True
    if hit:
        db._modified.add(rec)
    return hit


def _build_pak(db):
    _require(db, _PAK_DONOR, _SHADOWCLOAK_FX)
    if not db.has_record(_SHROUD_PAK):
        db.clone_record(_PAK_DONOR, _SHROUD_PAK)
    # value-only overrides on a cloned record (dtype preserved).
    db.set_field(_SHROUD_PAK, 'particleEffectNames', [_SHADOWCLOAK_FX] * _PARTICLE_COUNT)
    if _ATTACH:
        db.set_field(_SHROUD_PAK, 'particleEffectAttachPoints', list(_ATTACH))
    else:
        # BODY-CENTRED: drop the donor's hand pair so he smokes the way his
        # marauders do, which is what Will actually asked for.
        _del_field(db, _SHROUD_PAK, 'particleEffectAttachPoints')
    db._modified.add(_SHROUD_PAK)


def _build_skill(db):
    _require(db, _SKILL_DONOR)
    if not db.has_record(_SHROUD):
        db.clone_record(_SKILL_DONOR, _SHROUD)
    db.set_field(_SHROUD, 'charFxPakSelfNames', _SHROUD_PAK)
    # the donor's purple weapon tint -> the inert (0,0,0) NO-TINT default (b83 model).
    for f in ('skillWeaponTintRed', 'skillWeaponTintGreen', 'skillWeaponTintBlue'):
        if db.get_field_value(_SHROUD, f) is not None:
            db.set_field(_SHROUD, f, 0.0)
    db.set_field(_SHROUD, 'skillMaxLevel', 3)
    db.set_field(_SHROUD, 'FileDescription',
                 'SVC Enslaver: persistent black shroud (visual only, no payload)')
    db._modified.add(_SHROUD)


def _pet_tiers(db):
    """Every Enslaver pet tier, READ from the summon skill's spawnObjects.

    b102 / R-102 second amendment. b98 wired the shroud to the monster only, so
    the three tiers Will actually summons never got it and he correctly said the
    request was "still not implemented". Deriving the tiers instead of listing
    them is what makes that failure unrepeatable: append a 4th pet to the summon
    and it is in scope for both apply() and verify() with no code change.
    """
    if not db.has_record(_ENSLAVER_SUMMON):
        return []
    v = db.get_field_value(_ENSLAVER_SUMMON, 'spawnObjects')
    v = v if isinstance(v, list) else ([v] if v else [])
    out = []
    for x in v:
        s = str(x).strip()
        if s and db.has_record(s) and s not in out:
            out.append(s)
    return out


def shroud_roster(db):
    """{monster} + {every derived pet tier} - the surfaces the shroud must cover."""
    return ([_ENSLAVER] if db.has_record(_ENSLAVER) else []) + _pet_tiers(db)


def _wire_one(db, rec):
    """Put the shroud in this record's own lowest FREE skill slot."""
    slot = _slot_of(db, rec, _SHROUD) or _free_skillname_slot(db, rec)
    if slot is None:
        raise SystemExit(
            "[enslaver_shroud] no free skillName slot on %s. R-26's spirit "
            "forbids dropping a functional skill to make room - stop and ask "
            "Will rather than sacrificing one." % rec)
    db.set_field(rec, 'skillName%d' % slot, _SHROUD)
    # Level is cosmetic here (the shroud carries no payload at all - the
    # VISUAL-ONLY invariant below enforces that), so any granted level shows it.
    # The monster keeps its per-difficulty [1,2,3]; a pet tier is already ONE
    # record per tier, so a scalar 1 is the honest shape there.
    if rec == _ENSLAVER:
        db.set_field(rec, 'skillLevel%d' % slot, [1, 2, 3])
    else:
        db.set_field(rec, 'skillLevel%d' % slot, 1)
    db._modified.add(rec)
    return slot


def _wire(db):
    _require(db, _ENSLAVER)
    roster = shroud_roster(db)
    tiers = _pet_tiers(db)
    if not tiers:
        raise SystemExit(
            "[enslaver_shroud] %s spawns no resolvable pet, so the tier roster "
            "is EMPTY. That is the exact b98 failure this module now exists to "
            "prevent (shroud on the monster, nothing on what Will summons) - "
            "stop rather than ship a monster-only shroud again." % _ENSLAVER_SUMMON)
    for rec in roster:
        slot = _wire_one(db, rec)
        print("  shroud -> skillName%-2d on %s%s"
              % (slot, rec, '   (MONSTER)' if rec == _ENSLAVER else '   (PET TIER)'))
    print("  %d surface(s) wired (1 monster + %d derived pet tier(s)); NO existing "
          "skill dropped; charFxPakRunningNames kept as-is everywhere."
          % (len(roster), len(tiers)))


def apply(db, tags):
    print("\n=== [enslaver_shroud] b98 THE ENSLAVER'S BLACK SHROUD (R-95) "
          "+ b102 every pet tier (R-102 2nd amendment) ===")
    _build_pak(db)
    _build_skill(db)
    _wire(db)
    print("=== [enslaver_shroud] done (verify() runs post-finalization) ===\n")
    return tags


def verify(db, tags=None):
    problems = []

    if not db.has_record(_SHROUD):
        problems.append("shroud skill missing: %s" % _SHROUD)
    else:
        if _gv1(db, _SHROUD, 'Class') != 'Skill_BuffSelfToggled':
            problems.append("shroud Class=%r != Skill_BuffSelfToggled"
                            % _gv1(db, _SHROUD, 'Class'))
        if _norm(_gv1(db, _SHROUD, 'charFxPakSelfNames')) != _norm(_SHROUD_PAK):
            problems.append("shroud charFxPakSelfNames=%r != %s"
                            % (_gv1(db, _SHROUD, 'charFxPakSelfNames'), _SHROUD_PAK))
        # VISUAL-ONLY invariant: a shroud must never quietly become a stat buff.
        ff = db.get_fields(_SHROUD) or {}
        payload = []
        for k, tf in ff.items():
            b = k.split('###')[0]
            if not (b.startswith('offensive') or b.startswith('defensive')
                    or b.startswith('character')):
                continue
            for v in (tf.values or []):
                if isinstance(v, (int, float)) and v:
                    payload.append(b)
                    break
        if payload:
            problems.append(
                "VISUAL-ONLY: the shroud picked up a combat payload (%s). It is a "
                "cosmetic buff; a stat change here silently rebalances the Enslaver."
                % sorted(set(payload))[:6])
        for f in ('skillWeaponTintRed', 'skillWeaponTintGreen', 'skillWeaponTintBlue'):
            t = _gv1(db, _SHROUD, f)
            if t not in (None, 0, 0.0):
                problems.append("shroud %s=%r (must stay the inert 0 NO-TINT default; "
                                "the donor's purple tint would recolour his weapon)"
                                % (f, t))

    if not db.has_record(_SHROUD_PAK):
        problems.append("shroud CharFxPak missing: %s" % _SHROUD_PAK)
    else:
        names = db.get_field_value(_SHROUD_PAK, 'particleEffectNames') or []
        names = names if isinstance(names, list) else [names]
        if not names or any(_norm(n) != _norm(_SHADOWCLOAK_FX) for n in names):
            problems.append(
                "COLOUR PROVENANCE: the shroud pak must use ONLY %s - the marauders' "
                "own shadowcloak smoke, the single in-game-CONFIRMED black in this "
                "area. Got %r. (343_dark_smoke and hades2_shadowcloud are NOT "
                "colour-confirmed; R-10 calls 343_dark_smoke green-rendering.)"
                % (_SHADOWCLOAK_FX, names))
        # SHAPE leg (round 4). Will asked for "the same black shroud smoke his
        # summoned demons have" - same means same SHAPE as well as same colour.
        # The demons' pak has no attach points, so neither may this one: a hand
        # pair would put the smoke on two fists instead of round the body, and
        # that difference is invisible to every colour check in this file.
        apf = db.get_field_value(_SHROUD_PAK, 'particleEffectAttachPoints')
        ap = [str(x) for x in (apf if isinstance(apf, list) else [apf] if apf else []) if str(x).strip()]
        if [str(x) for x in ap] != _ATTACH:
            problems.append(
                "SHAPE: shroud pak particleEffectAttachPoints=%r, expected %r. The "
                "demons' own %s emits from the WHOLE BODY with no attach points; an "
                "attach pair (the 343 weapon-enchantment donor's shape) would smoke "
                "from the hands instead and would NOT be 'the same shroud his "
                "summoned demons have'. Bone names (Bone_R_Weapon) are doubly wrong "
                "here - those belong on an EffectEntity boneList, never on a pak."
                % (ap, _ATTACH, _SHADOWCLOAK_PAK.rsplit('\\', 1)[-1]))
        if len(names) != _PARTICLE_COUNT:
            problems.append(
                "shroud pak has %d particleEffectNames entr(ies), expected %d. The "
                "donor duplicated its effect once per attach point; with no attach "
                "points there is exactly one body emitter, as on the demons' pak."
                % (len(names), _PARTICLE_COUNT))

    # The SHAPE expectation above is only honest if it is DERIVED from the record
    # it claims to copy. Read the demons' own pak and require that it really is
    # attach-free; if the marauders' shroud ever grows attach points, this gate
    # fails loud instead of silently letting the two drift apart.
    if db.has_record(_SHADOWCLOAK_PAK):
        dapf = db.get_field_value(_SHADOWCLOAK_PAK, 'particleEffectAttachPoints')
        dap = [str(x) for x in (dapf if isinstance(dapf, list) else [dapf] if dapf else [])
               if str(x).strip()]
        if dap != _ATTACH:
            problems.append(
                "the DEMONS' pak %s now has particleEffectAttachPoints=%r while this "
                "module still copies %r. The shape reference moved; re-derive "
                "_ATTACH from it rather than leaving the two shrouds different."
                % (_SHADOWCLOAK_PAK, dap, _ATTACH))
    else:
        problems.append("the demons' shape/colour reference pak is missing: %s"
                        % _SHADOWCLOAK_PAK)

    if not db.has_record(_SHADOWCLOAK_FX):
        problems.append("the confirmed shadowcloak EffectEntity is missing: %s"
                        % _SHADOWCLOAK_FX)
    elif not _gv1(db, _SHADOWCLOAK_FX, 'effectFile'):
        problems.append("%s has no effectFile" % _SHADOWCLOAK_FX)

    # ── ROSTER LEG (b102, R-102 second amendment). The shroud must be on the
    #    MONSTER *and* on every pet tier, and the tier list must be DERIVED, or
    #    the b98 failure repeats the next time a tier is added: Will summons the
    #    pet, so a monster-only shroud is, from where he stands, not implemented.
    if not db.has_record(_ENSLAVER):
        problems.append("Enslaver missing: %s" % _ENSLAVER)
    if not db.has_record(_ENSLAVER_SUMMON):
        problems.append(
            "the Enslaver summon skill is missing (%s), so the pet-tier roster "
            "cannot be derived and a tier could be silently skipped"
            % _ENSLAVER_SUMMON)
    tiers = _pet_tiers(db)
    if db.has_record(_ENSLAVER_SUMMON) and not tiers:
        problems.append(
            "%s spawns NO resolvable pet: the derived tier roster is EMPTY. b98 "
            "shipped a monster-only shroud exactly this way and Will reported it "
            "as never implemented." % _ENSLAVER_SUMMON)

    for rec in shroud_roster(db):
        is_pet = rec != _ENSLAVER
        slot = _slot_of(db, rec, _SHROUD)
        if slot is None:
            problems.append(
                "SHROUD MISSING on %s%s - the shroud is in none of its skillName "
                "slots. R-102's second amendment: b98 wired the MONSTER ONLY, all "
                "three pet tiers were skipped, and the pet is what Will summons."
                % (rec, ' (PET TIER)' if is_pet else ' (MONSTER)'))
            continue
        lv = db.get_field_value(rec, 'skillLevel%d' % slot)
        lv0 = lv[0] if isinstance(lv, list) and lv else lv
        if not lv0:
            problems.append("%s: shroud sits at skillLevel%d=%r (level 0 is not "
                            "granted, so it never displays)" % (rec, slot, lv))
        if is_pet:
            # A self-buff toggle is inert unless the controller fires it. The
            # pets run controller_skelly_aggressive; assert the trigger rather
            # than assuming it, so a controller repoint cannot silently kill the
            # shroud on the exact surface Will looks at.
            ctrl = _gv1(db, rec, 'controller')
            if not ctrl or not db.has_record(str(ctrl)):
                problems.append("%s has no resolvable controller (%r), so its "
                                "self-buff shroud can never fire" % (rec, ctrl))
            else:
                trig = _gv1(db, str(ctrl), 'BuffSelfBehavior')
                if str(trig) != _PET_CONTROLLER_BUFF_TRIGGER:
                    problems.append(
                        "%s: controller %s has BuffSelfBehavior=%r, expected %r. A "
                        "Skill_BuffSelfToggled that the AI never toggles is a slot "
                        "with nothing in it."
                        % (rec, ctrl, trig, _PET_CONTROLLER_BUFF_TRIGGER))
        # R-26 spirit + "ADD, never take away": the pre-existing DRX running FX
        # (the black smoke Will already sees) must survive on every surface that
        # had it. The monster and the pet tiers all carry it on main.
        run = _gv1(db, rec, 'charFxPakRunningNames')
        if _norm(run) != _norm(_SHADOWCLOAK_PAK):
            problems.append(
                "%s: charFxPakRunningNames is %r, expected %s. This module must "
                "ADD the persistent channel, never take away the running one that "
                "matches his marauders." % (rec, run, _SHADOWCLOAK_PAK))
    if db.has_record(_MARAUDER):
        if _norm(_gv1(db, _MARAUDER, 'charFxPakRunningNames')) != _norm(_SHADOWCLOAK_PAK):
            problems.append("the marauders lost their shadowcloak running FX (%r)"
                            % _gv1(db, _MARAUDER, 'charFxPakRunningNames'))

    if problems:
        for p in problems:
            print("  ENSLAVER-SHROUD OFFENDER: %s" % p)
        raise SystemExit("enslaver_shroud.verify FAILED: %d problem(s)" % len(problems))
    print("  [enslaver_shroud].verify OK: persistent shroud on the marauders' own "
          "confirmed shadowcloak smoke, visual-only (no payload, no tint), in a FREE "
          "slot on ALL %d surface(s) - the monster AND every derived pet tier (%d), "
          "each with a controller that actually fires self-buffs; every running FX "
          "untouched. WHAT IS STILL NOT CLAIMED: how it READS in game - only Will's "
          "eye settles that (BL-R102-DEBT-1)."
          % (len(shroud_roster(db)), len(_pet_tiers(db))))
    return tags


def _negtest():
    """py tools/patches/enslaver_shroud.py --negtest"""
    from collections import OrderedDict

    class _TF(object):
        def __init__(self, v):
            self.values = v

    class _Stub(object):
        def __init__(self):
            self.d = {}
            self._modified = set()

        def has_record(self, n):
            return n in self.d

        def record_names(self):
            return list(self.d)

        def get_fields(self, n):
            f = self.d.get(n)
            if f is None:
                return None
            return OrderedDict((k, _TF(v)) for k, v in f.items())

        def get_field_value(self, n, f):
            return self.d.get(n, {}).get(f)

        def set_field(self, n, f, v, dt=None):
            self.d.setdefault(n, {})[f] = v if isinstance(v, list) else [v]

    _PETS = [r'records\skills\soulskills\pets\toxeus_enslaver_%d.dbr' % i
             for i in (1, 2, 3)]
    _CTRL = (r'records\skills\spirit\drxpet\drxpet_controllers'
             r'\controller_skelly_aggressive.dbr')

    def _base():
        db = _Stub()
        db.d[_SHADOWCLOAK_FX] = {'effectFile': [r'DRXeffects\shadowcloakrunning.pfx']}
        # the demons' pak: one body emitter, NO attach points (this is the shape
        # the module derives its own from).
        db.d[_SHADOWCLOAK_PAK] = {'particleEffectNames': [_SHADOWCLOAK_FX]}
        db.d[_SHROUD_PAK] = {'particleEffectNames': [_SHADOWCLOAK_FX] * _PARTICLE_COUNT}
        db.d[_SHROUD] = {'Class': ['Skill_BuffSelfToggled'],
                         'charFxPakSelfNames': [_SHROUD_PAK],
                         'skillWeaponTintRed': [0.0], 'skillWeaponTintGreen': [0.0],
                         'skillWeaponTintBlue': [0.0]}
        db.d[_ENSLAVER] = {'skillName19': [_SHROUD], 'skillLevel19': [1, 2, 3],
                           'charFxPakRunningNames': [_SHADOWCLOAK_PAK]}
        db.d[_MARAUDER] = {'charFxPakRunningNames': [_SHADOWCLOAK_PAK]}
        db.d[_CTRL] = {'BuffSelfBehavior': [_PET_CONTROLLER_BUFF_TRIGGER]}
        db.d[_ENSLAVER_SUMMON] = {'spawnObjects': list(_PETS)}
        for p in _PETS:
            db.d[p] = {'skillName13': [_SHROUD], 'skillLevel13': [1],
                       'controller': [_CTRL],
                       'charFxPakRunningNames': [_SHADOWCLOAK_PAK]}
        return db

    plants = [
        ('unconfirmed colour asset swapped in',
         lambda db: db.d[_SHROUD_PAK].__setitem__(
             'particleEffectNames',
             [r'records\effects\custom\343_dark_smoke.dbr'] * 2)),
        ('the shroud grows a combat payload',
         lambda db: db.d[_SHROUD].__setitem__('offensivePhysicalMin', [500.0])),
        ('the donor purple tint comes back',
         lambda db: db.d[_SHROUD].__setitem__('skillWeaponTintBlue', [1.0])),
        ('the shroud falls out of the Enslaver kit',
         lambda db: db.d[_ENSLAVER].pop('skillName19')),
        ('his running FX is taken away instead of added to',
         lambda db: db.d[_ENSLAVER].__setitem__('charFxPakRunningNames', [''])),
        ('bone names used where attach-point names belong',
         lambda db: db.d[_SHROUD_PAK].__setitem__(
             'particleEffectAttachPoints', ['Bone_R_Weapon', 'Bone_L_Weapon'])),
        # ROUND 4: the defect the vet found. Hands-only emission passes every
        # colour check and is still the WRONG SHROUD, so it gets its own plant.
        ('the donor hand-pair comes back (hands-only, not the demons body shroud)',
         lambda db: db.d[_SHROUD_PAK].__setitem__(
             'particleEffectAttachPoints', ['R Hand', 'L Hand'])),
        ('one emitter per (absent) attach point becomes two duplicate emitters',
         lambda db: db.d[_SHROUD_PAK].__setitem__(
             'particleEffectNames', [_SHADOWCLOAK_FX, _SHADOWCLOAK_FX])),
        ('the demons shape reference itself drifts to a hand pair',
         lambda db: db.d[_SHADOWCLOAK_PAK].__setitem__(
             'particleEffectAttachPoints', ['R Hand', 'L Hand'])),
        ('the demons shape/colour reference pak disappears',
         lambda db: db.d.pop(_SHADOWCLOAK_PAK)),
        # ── b102 / R-102 second amendment: the defect Will reported as "still not
        #    implemented". Every one of these passed b98's gate unchanged.
        ('THE b98 DEFECT ITSELF: shroud on the monster, on NO pet tier',
         lambda db: [db.d[p].pop('skillName13') for p in _PETS]),
        ('one pet tier is skipped while the other two are wired',
         lambda db: db.d[_PETS[1]].pop('skillName13')),
        ('a NEW 4th pet tier is summoned and never gets the shroud',
         lambda db: (db.d.__setitem__(
             r'records\skills\soulskills\pets\toxeus_enslaver_4.dbr',
             {'controller': [_CTRL],
              'charFxPakRunningNames': [_SHADOWCLOAK_PAK]}),
             db.d[_ENSLAVER_SUMMON].__setitem__(
                 'spawnObjects', _PETS + [
                     r'records\skills\soulskills\pets\toxeus_enslaver_4.dbr']))),
        ('the summon loses its spawnObjects, so the tier roster goes silently empty',
         lambda db: db.d[_ENSLAVER_SUMMON].__setitem__('spawnObjects', [])),
        ('a pet gets the shroud at level 0 (present in a slot, never displayed)',
         lambda db: db.d[_PETS[0]].__setitem__('skillLevel13', [0])),
        ('the pets controller stops firing self-buffs, so the toggle is inert',
         lambda db: db.d[_CTRL].__setitem__('BuffSelfBehavior', ['NeverBuff'])),
        ('a pet loses the pre-existing DRX running smoke instead of gaining a shroud',
         lambda db: db.d[_PETS[2]].__setitem__('charFxPakRunningNames', [''])),
    ]
    try:
        verify(_base())
    except SystemExit as e:
        print("NEGTEST SETUP FAIL: the clean stub should PASS but raised: %s" % e)
        return 1
    bad = 0
    for label, plant in plants:
        db = _base()
        plant(db)
        try:
            verify(db)
        except SystemExit:
            print("  negtest OK  (caught): %s" % label)
            continue
        print("  negtest FAIL (missed): %s" % label)
        bad += 1
    print("negtest: %d/%d plants caught" % (len(plants) - bad, len(plants)))
    return 1 if bad else 0


if __name__ == '__main__':
    import sys
    sys.exit(_negtest() if '--negtest' in sys.argv else 0)
