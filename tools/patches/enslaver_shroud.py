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
     a CharFxPak cloned from the shipped `343_weapon_poisoncharfxpak` structure
     (particleEffectAttachPoints 'R Hand';'L Hand'), with the particle swapped to
     the marauders' own `drxshadowcloakrunning_fx`.
     NOTE THE FORMAT DIFFERENCE, easy to get wrong: a CharFxPak uses
     `particleEffectAttachPoints` with FRIENDLY names ("R Hand"), whereas an
     EffectEntity uses `boneList` with raw bone names ("Bone_R_Weapon"). They are
     not interchangeable.
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
invisible to any .arz scan. Black hand-smoke over a green waist aura will not read
as a black shroud.
That mesh work belongs to the green-diff lane (b92, commit 60d7789, reachable only
from tag build53-dev and NOT deployed) and turns on a Will answer about giving each
champion a different aura-free mesh. It is registered as BL-b98-DEBT-2. NO REPORT
FROM THIS LANE MAY CLAIM THE ENSLAVER READS BLACK until Will has looked at him in
game with the mesh question settled.
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

# the in-game-CONFIRMED black: the smoke Will saw on the marauders
_SHADOWCLOAK_FX = r'records\skills\stealth\drxpet\drx_pet_fx\drxshadowcloakrunning_fx.dbr'
_SHADOWCLOAK_PAK = r'records\skills\stealth\drxpet\drx_pet_fx\drxshadowcloakrunning_fx_pak.dbr'

# structure donors (both DB-verified)
_SKILL_DONOR = r'records\skills\monster skills\buff_self\empusamerc_enchantment.dbr'
_PAK_DONOR = r'records\effects\weaponenchantments\343_weapon_poisoncharfxpak.dbr'

_SHROUD = r'records\skills\monster skills\buff_self\svc_enslaver_shroud.dbr'
_SHROUD_PAK = r'records\skills\monster skills\buff_self\svc_enslaver_shroud_charfxpak.dbr'

_ATTACH = ['R Hand', 'L Hand']


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


def _build_pak(db):
    _require(db, _PAK_DONOR, _SHADOWCLOAK_FX)
    if not db.has_record(_SHROUD_PAK):
        db.clone_record(_PAK_DONOR, _SHROUD_PAK)
    # value-only overrides on a cloned record (dtype preserved).
    db.set_field(_SHROUD_PAK, 'particleEffectNames', [_SHADOWCLOAK_FX] * len(_ATTACH))
    db.set_field(_SHROUD_PAK, 'particleEffectAttachPoints', list(_ATTACH))
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


def _wire(db):
    _require(db, _ENSLAVER)
    slot = _slot_of(db, _ENSLAVER, _SHROUD) or _free_skillname_slot(db, _ENSLAVER)
    if slot is None:
        raise SystemExit(
            "[enslaver_shroud] no free skillName slot on the Enslaver. R-26's "
            "spirit forbids dropping a functional skill to make room - stop and "
            "ask Will rather than sacrificing one.")
    db.set_field(_ENSLAVER, 'skillName%d' % slot, _SHROUD)
    db.set_field(_ENSLAVER, 'skillLevel%d' % slot, [1, 2, 3])
    db._modified.add(_ENSLAVER)
    print("  shroud wired into skillName%d (NO existing skill dropped); "
          "charFxPakRunningNames kept as-is." % slot)


def apply(db, tags):
    print("\n=== [enslaver_shroud] b98 THE ENSLAVER'S BLACK SHROUD (R-95) ===")
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
        ap = db.get_field_value(_SHROUD_PAK, 'particleEffectAttachPoints') or []
        ap = ap if isinstance(ap, list) else [ap]
        if [str(x) for x in ap] != _ATTACH:
            problems.append(
                "shroud pak particleEffectAttachPoints=%r != %r. A CharFxPak takes "
                "FRIENDLY attach names, not EffectEntity boneList bone names."
                % (ap, _ATTACH))
        if len(names) != len(ap):
            problems.append("shroud pak has %d particle(s) for %d attach point(s)"
                            % (len(names), len(ap)))

    if not db.has_record(_SHADOWCLOAK_FX):
        problems.append("the confirmed shadowcloak EffectEntity is missing: %s"
                        % _SHADOWCLOAK_FX)
    elif not _gv1(db, _SHADOWCLOAK_FX, 'effectFile'):
        problems.append("%s has no effectFile" % _SHADOWCLOAK_FX)

    if not db.has_record(_ENSLAVER):
        problems.append("Enslaver missing: %s" % _ENSLAVER)
    else:
        slot = _slot_of(db, _ENSLAVER, _SHROUD)
        if slot is None:
            problems.append("the shroud is not in any of the Enslaver's skillName slots")
        else:
            lv = db.get_field_value(_ENSLAVER, 'skillLevel%d' % slot)
            lv0 = lv[0] if isinstance(lv, list) and lv else lv
            if not lv0:
                problems.append("shroud sits at skillLevel%d=%r (level 0 is not granted)"
                                % (slot, lv))
        # R-26 spirit: nothing was dropped to make room.
        if _norm(_gv1(db, _ENSLAVER, 'charFxPakRunningNames')) != _norm(_SHADOWCLOAK_PAK):
            problems.append(
                "the Enslaver's own charFxPakRunningNames was changed (%r). This "
                "module must ADD the persistent channel, never take away the "
                "running one that matches his marauders."
                % _gv1(db, _ENSLAVER, 'charFxPakRunningNames'))
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
          "Enslaver skill slot; his running FX and the marauders' are untouched. "
          "IN-GAME BLACK IS NOT CLAIMED (BL-b98-DEBT-2: the mesh-embedded green).")
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

    def _base():
        db = _Stub()
        db.d[_SHADOWCLOAK_FX] = {'effectFile': [r'DRXeffects\shadowcloakrunning.pfx']}
        db.d[_SHROUD_PAK] = {'particleEffectNames': [_SHADOWCLOAK_FX, _SHADOWCLOAK_FX],
                             'particleEffectAttachPoints': list(_ATTACH)}
        db.d[_SHROUD] = {'Class': ['Skill_BuffSelfToggled'],
                         'charFxPakSelfNames': [_SHROUD_PAK],
                         'skillWeaponTintRed': [0.0], 'skillWeaponTintGreen': [0.0],
                         'skillWeaponTintBlue': [0.0]}
        db.d[_ENSLAVER] = {'skillName19': [_SHROUD], 'skillLevel19': [1, 2, 3],
                           'charFxPakRunningNames': [_SHADOWCLOAK_PAK]}
        db.d[_MARAUDER] = {'charFxPakRunningNames': [_SHADOWCLOAK_PAK]}
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
