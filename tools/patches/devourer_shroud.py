r"""devourer_shroud - THE DEVOURER'S BLACK SHADOW SHROUD.

WILL (2026-08-11), verbatim:

> "toxeus the murderer, devourer of souls we need to add the black shadow shroud
>  around him, the same one that his demon summon guys have"

--------------------------------------------------------------------------------
THE NAME DOES NOT EXIST, SO IT WAS RESOLVED FROM THE RECORDS
--------------------------------------------------------------------------------
There is no "Devourer of Souls" in this mod. The four Toxeus the Murderer variants,
read out of the shipped build83 arz (`44499f56`), with the shroud question answered
for each:

| variant (display name)                | anchor record             | its summons                                  | black shadow shroud? |
|---------------------------------------|---------------------------|----------------------------------------------|----------------------|
| Toxeus the Murderer, Enslaver of Souls| um_toxeus_enslaver_99     | Enslaved Shadow Marauders (um_enslaver_marauder_99) | **YES, on both channels** |
| Toxeus the Murderer, Devourer of Blood| um_bloodtoxeus_99         | Blood Demons (drxcreatures\blooddemon\um_devourer_bloodspawn_99) | **NO - none, on any surface** |
| Toxeus the Murderer, the Endless Hunt | um_toxeus_hunt_99/_l_99   | Coursers (bloodhounds, not demons)           | mesh-embedded ShadowStalker_Smoke |
| Toxeus the Murderer, End of All Things| pets\toxeus_eoat_1..3     | EoAT disciples                               | none (see OPEN QUESTION) |

"Devourer" + "of Souls" fuses the two boss names, so the phrase alone is ambiguous.
The DATA is not. `enslaver_shroud` (b98 + b102) already put the shroud on the
Enslaver's monster record AND all three of his pet tiers, and that shipped in
build83 - so "we need to ADD" cannot be about him, because on his surfaces it is
already there. The Devourer is the only Toxeus variant that carries NO shroud on
any surface, and his summoned minions live in the `blooddemon` folder - literally
"his demon summon guys". Target resolved: **Toxeus the Murderer, DEVOURER OF BLOOD.**

--------------------------------------------------------------------------------
GROUND TRUTH: WHAT HE HAS TODAY, AND WHY IT IS NOT A SHROUD
--------------------------------------------------------------------------------
Measured on the shipped arz, `um_bloodtoxeus_99` + `pets\bloodtoxeus_1..3`:
  * `charFxPakRunningNames` - **ABSENT on all four records.** The marauders and the
    whole Enslaver family carry `drxshadowcloakrunning_fx_pak` here. He has nothing.
  * his ONLY body FX is `svc_black_poison` (R-7, module `black_poison`) ->
    `svc_black_poison_charfxpak`, whose shape is
        particleEffectNames        = 343_dark_smoke, 343_dark_smoke   (x2)
        particleEffectAttachPoints = 'R Hand'; 'L Hand'
    i.e. two HAND emitters, not a body shroud. Will asked for a shroud "AROUND
    him", and hands are not around him. This is the exact ROUND 4 defect the
    Enslaver's own lane had to fix on itself in b98.
  * he has NO crimson shroud either, contrary to a plausible reading of his name:
    crimson is only his `baseTexture` (`newskeleton_crimson.tex`). There is no
    crimson FX record anywhere on him. So there is nothing of his own design being
    displaced here - this lane ADDS to an empty channel.

--------------------------------------------------------------------------------
THE FIX - THE MARAUDERS' EXACT FX, ON BOTH CHANNELS, ON MONSTER-RECORD FIELDS
--------------------------------------------------------------------------------
"The same one that his demon summon guys have" is taken literally: the same
EffectEntity, the same pak shape, on the same fields, as `um_enslaver_marauder_99`
carries and as `enslaver_shroud` gave the Enslaver.

  1. RUNNING channel - `charFxPakRunningNames = drxshadowcloakrunning_fx_pak` on
     every roster surface. This is the marauders' own field, byte-for-byte their
     own pak. It renders only while the character RUNS (the b98 finding), which is
     why it is necessary but not sufficient.
  2. PERSISTENT channel - `charFxPakSelfNames` is a SKILL field, never a Monster
     field, so the shipped way to hang a permanent FX on a body is a
     `Skill_BuffSelfToggled` in a free skill slot. Two records, his own:
       * `records\skills\monster skills\buff_self\svc_devourer_shroud.dbr`
       * `records\skills\monster skills\buff_self\svc_devourer_shroud_charfxpak.dbr`
     built from the same donors `enslaver_shroud` used, pointed at the same
     in-game-CONFIRMED black particle, and BODY-CENTRED (no attach points), which
     is the demons' own shape.

  ⚠️ THEY ARE HIS OWN RECORDS, NOT THE ENSLAVER'S, AND THAT IS DELIBERATE. Reusing
  `svc_enslaver_shroud` would have been one record cheaper and would have re-created
  the exact defect R-93 exists to prevent - Will's "he has no different or unique
  skills from toxeus the murderer, the enslaver of souls", which was literally true
  of 9 of his 12 slots. The FX asset is shared (that is the request); the skill
  records are not.

  ⚠️ CRASH LAW (the build28 trap), asserted rather than assumed. A `charFxPak*`
  field on a SpawnPet skill crashes the game. Everything this module writes lands
  on a MONSTER/PET record field or on a `Skill_BuffSelfToggled`, and `verify()`
  walks every skill slot on every roster member and FAILS if any `Skill_SpawnPet*`
  record in his kit has grown a `charFxPak*` field.

--------------------------------------------------------------------------------
ROSTER: DERIVED FROM TWO INDEPENDENT WITNESSES, WHICH MUST AGREE
--------------------------------------------------------------------------------
b98 shipped a monster-only shroud and Will correctly reported it as never
implemented, because he summons the PET. A hand-listed roster is how that happens.
So this module never lists the surfaces; it derives them twice and requires the two
answers to match:

  W1 - the anchor monster + every tier read from `summon_bloodtoxeus.spawnObjects`
       (append a 4th tier and it is in scope for the fix AND the gate, no code change)
  W2 - every record in the DB whose `description` is one of his two name tags
       (`tagMonsterHemorrheus` / `tagMonsterHemorrheusPet`)

W2 is the one that catches a DIFFICULTY CLONE. The Hunt already has exactly such a
clone (`um_toxeus_hunt_l_99`, minted at build time by `toxeus_hunt_endless`); if the
Devourer ever gets one, W2 sees it, W1 does not, and the gate fails loud instead of
shipping a Legendary Devourer with no shroud. Placement needs no separate leg: every
placed and roaming form of him (`q_bloodtoxeus_lone` pool name1/name2/name3 = the
three difficulties, `q_bloodtoxeus_ambush`, `egg_blooddragon`) is a PROXY pointing at
the one monster record, so fixing the record fixes every placement and every tier.

--------------------------------------------------------------------------------
WHAT THIS MODULE DOES NOT DO (reported, not silently deferred)
--------------------------------------------------------------------------------
  * IT DOES NOT REMOVE `svc_black_poison`. "ADD, never take away" - it is R-7's,
    it is `black_poison`'s to own, and the RETIREMENT PROTOCOL forbids this lane
    retiring another ruling's record. But the honest risk statement is in the
    BACKLOG as `BL-DEVSHROUD-1`: `343_dark_smoke` is NOT a colour-confirmed black
    (R-10 calls it "the green-rendering 343_dark_smoke", and `black_poison`'s own
    docstring flags it as BP-SMOKE-1), so after this change he carries a
    confirmed-black BODY shroud and an unconfirmed HAND smoke at the same time.
    That is exactly the two-emitter picture Will described on the Enslaver in R-102
    ("he has black smoke too but the green is more prominent"). If he reports green
    on the Devourer, the answer is one line - repoint `svc_black_poison_charfxpak`
    at the shadowcloak particle - and that is Will's call, not this lane's.
  * IT DOES NOT TOUCH THE END OF ALL THINGS (`pets\toxeus_eoat_1..3`). He is a
    separate named variant, a crafted supra pet, and R-102's sixth amendment
    explicitly left "does the EoAT want its own look" as Will's decision.
    Registered as `BL-DEVSHROUD-2`.
  * IT CLAIMS NOTHING ABOUT HOW THIS READS IN GAME. The particle is the one Will
    has SEEN and called black, on the marauders; the shape is derived from their
    own pak; but nobody has looked at the Devourer wearing it (`BL-DEVSHROUD-3`).
"""

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))   # tools/ on path

MODULE_NAME = "Devourer of Blood: black shadow shroud (Will 2026-08-11)"

# ── the roster anchors ──────────────────────────────────────────────────────
_DEVOURER = r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr'
_DEVOURER_SUMMON = r'records\skills\soulskills\summon_bloodtoxeus.dbr'
# W2: his name tags. A difficulty clone or a 4th pet keeps the description tag,
# which is how a hand-listed roster is caught going stale.
_NAME_TAGS = ('tagmonsterhemorrheus', 'tagmonsterhemorrheuspet')

# ── the demons whose shroud is being copied ─────────────────────────────────
# um_devourer_bloodspawn_99 is HIS summon; um_enslaver_marauder_99 is the record
# that actually CARRIES the shroud Will has seen and called black. Both are named:
# the first is who he meant, the second is where the asset provably lives.
_BLOODSPAWN = r'records\drxcreatures\blooddemon\um_devourer_bloodspawn_99.dbr'
_MARAUDER = r'records\creature\monster\shadowstalker\um_enslaver_marauder_99.dbr'

# the in-game-CONFIRMED black: the smoke Will saw on the marauders and called
# "the proper black shroud" (R-102 fourth amendment).
_SHADOWCLOAK_FX = r'records\skills\stealth\drxpet\drx_pet_fx\drxshadowcloakrunning_fx.dbr'
_SHADOWCLOAK_PAK = r'records\skills\stealth\drxpet\drx_pet_fx\drxshadowcloakrunning_fx_pak.dbr'

# structure donors - the same two `enslaver_shroud` uses, so the two champions'
# shrouds are the same construction as well as the same asset.
_SKILL_DONOR = r'records\skills\monster skills\buff_self\empusamerc_enchantment.dbr'
_PAK_DONOR = r'records\effects\weaponenchantments\343_weapon_poisoncharfxpak.dbr'

# HIS OWN records (R-93: his kit may not be made of the Enslaver's records)
_SHROUD = r'records\skills\monster skills\buff_self\svc_devourer_shroud.dbr'
_SHROUD_PAK = r'records\skills\monster skills\buff_self\svc_devourer_shroud_charfxpak.dbr'

# the FX that must SURVIVE this lane (ADD, never take away) - R-7's black poison
_BLACK_POISON = r'records\skills\monster skills\buff_self\svc_black_poison.dbr'

# SHAPE: [] == emit from the whole body, exactly like the demons' own pak, which
# carries particleEffectNames x1 and NO particleEffectAttachPoints. A hand pair
# (the 343 weapon-enchantment donor's shape) would smoke from two fists instead of
# "around him", and that difference is invisible to any colour check.
_ATTACH = []
_PARTICLE_COUNT = 1

_BUFF_TRIGGER = 'WhenEnemyIsSeen'


def _norm(p):
    return str(p).replace('/', '\\').lower()


def _gv1(db, rec, f):
    v = db.get_field_value(rec, f)
    return v[0] if isinstance(v, list) and v else v


def _require(db, *recs):
    missing = [r for r in recs if not db.has_record(r)]
    if missing:
        raise SystemExit("[devourer_shroud] required record(s) missing: %s" % missing)


def _skill_slots(db, rec):
    """{slot index: skill path} for every non-blank skillName<i> on rec."""
    out = {}
    for k, tf in (db.get_fields(rec) or {}).items():
        b = k.split('###')[0]
        if b.startswith('skillName') and b[9:].isdigit() and tf.values \
                and str(tf.values[0]).strip():
            out[int(b[9:])] = str(tf.values[0])
    return out


def _level_slots(db, rec):
    """{slot index} for every skillLevel<i> field PRESENT on rec, blank name or not."""
    out = set()
    for k, tf in (db.get_fields(rec) or {}).items():
        b = k.split('###')[0]
        if b.startswith('skillLevel') and b[10:].isdigit() and tf.values:
            out.add(int(b[10:]))
    return out


def _free_slot(db, rec, lo=1, hi=23):
    """The lowest FULLY free slot - free in skillName AND in skillLevel.

    Measured on the shipped build83 arz, `pets\\bloodtoxeus_1..3` carry ORPHAN
    skillLevel arrays with no skillName beside them (slot 8 = [4,6,8], 9 = [1,2,3],
    13 = [1], 14 = [1,2,3], 16 = [12], 17 = [1]) - SV-donor residue. A name-only
    freeness test calls slot 8 free and silently OVERWRITES a per-difficulty array,
    which is a field change this lane cannot explain in a record diff and which
    would quietly disarm the slot if anything ever filled its name. Slot 18+ is
    genuinely empty on all three, and 19+ on the monster, so demanding both costs
    nothing here and makes the write purely ADDITIVE.
    """
    used = set(_skill_slots(db, rec)) | _level_slots(db, rec)
    for i in range(lo, hi + 1):
        if i not in used:
            return i
    return None


def _slot_of(db, rec, skill):
    want = _norm(skill)
    for i, p in _skill_slots(db, rec).items():
        if _norm(p) == want:
            return i
    return None


def _find_resources_dir():
    r"""The staged mod `Resources\` dir, for the A9-style render-resolution leg.

    `$SVC_MOD_RESOURCES` wins. Otherwise walk up for `work\SoulvizierClassic\
    Resources` - and because `work/` is gitignored, a WORKTREE has none, so the
    MAIN checkout is followed through the worktree's `.git` FILE
    (`gitdir: <main>/.git/worktrees/<name>`), the same hop
    `tools/check_build_inputs.py` uses to make a worktree build work at all.
    """
    import os
    env = os.environ.get('SVC_MOD_RESOURCES')
    if env and _Path(env).is_dir():
        return _Path(env)
    roots = []
    for base in _Path(__file__).resolve().parents:
        roots.append(base)
        g = base / '.git'
        if g.is_file():
            try:
                txt = g.read_text(encoding='utf-8', errors='ignore').strip()
            except OSError:
                txt = ''
            if txt.startswith('gitdir:'):
                gd = _Path(txt.split(':', 1)[1].strip())
                for anc in [gd] + list(gd.parents):
                    if anc.name == '.git':
                        roots.append(anc.parent)
                        break
    for r in roots:
        cand = r / 'work' / 'SoulvizierClassic' / 'Resources'
        if cand.is_dir():
            return cand
    return None


def fx_asset_resolution(db, resources=None):
    r"""A9-STYLE RENDER RESOLUTION on the pak: does the particle actually SHIP?

    The record chain can be perfect and the boss still smoke nothing if the
    `.pfx` the EffectEntity names is not inside a shipped `.arc` - resolution is
    not rendering (the A9/D5 lesson, `tools/validate_render_chain.py`). This walks
    the WHOLE chain the engine walks:

        skill.charFxPakSelfNames -> pak.particleEffectNames -> fx.effectFile
              -> `<Arc>\<inner>.pfx` inside `<mod Resources>\<Arc>.arc`

    and requires the Devourer's chain to land on the SAME shipped file as the
    demons' own. Returns (status, detail) with status PASS / FAIL / SKIP; SKIP is
    announced loudly by the caller rather than counted as a pass, because a gate
    that cannot see the payload has not answered the question.
    """
    fx = _gv1(db, _SHROUD_PAK, 'particleEffectNames')
    if isinstance(fx, list):
        fx = fx[0] if fx else None
    if not fx or not db.has_record(str(fx)):
        return ('FAIL', 'the shroud pak names no resolvable EffectEntity (%r)' % fx)
    eff = _gv1(db, str(fx), 'effectFile')
    if not eff:
        return ('FAIL', '%s has no effectFile' % fx)
    res = _Path(resources) if resources else _find_resources_dir()
    if res is None or not res.is_dir():
        return ('SKIP', 'no staged mod Resources dir found (set $SVC_MOD_RESOURCES); '
                        'the .pfx SHIPPING could not be checked')
    parts = str(eff).replace('/', '\\').split('\\')
    if len(parts) < 2:
        return ('FAIL', 'effectFile %r has no archive component' % eff)
    arcname, inner = parts[0], '/'.join(parts[1:]).lower()
    cand = res / (arcname + '.arc')
    if not cand.exists():
        hits = [p for p in res.glob('*.arc') if p.stem.lower() == arcname.lower()]
        cand = hits[0] if hits else None
    if cand is None:
        return ('FAIL', '%s.arc is not in the shipped payload, so %r cannot render'
                        % (arcname, eff))
    try:
        _sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
        from arc_patcher import ArcArchive
        names = {(e.name or '').lower().replace('\\', '/')
                 for e in ArcArchive.from_file(cand).entries}
    except Exception as e:                                  # noqa: BLE001
        return ('SKIP', 'could not read %s (%s)' % (cand.name, e))
    if inner not in names:
        return ('FAIL', '%r is NOT inside %s - the shroud would resolve to nothing '
                        'and he would smoke nothing' % (eff, cand.name))
    return ('PASS', '%s -> %s (%d entries)' % (eff, cand.name, len(names)))


def _del_field(db, rec, name):
    """Remove a field slot entirely rather than blanking it to ''.

    86 of the 131 CharFxPak records in the DB simply omit
    `particleEffectAttachPoints` and none carries an empty one, so ABSENCE - not
    emptiness - is the precedented shape, and a live reference blanked to '' is a
    loader hazard.
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


# ── ROSTER: two witnesses ───────────────────────────────────────────────────

def _tiers_from_summon(db):
    """W1: every pet tier, READ from the soul-summon's spawnObjects."""
    if not db.has_record(_DEVOURER_SUMMON):
        return []
    v = db.get_field_value(_DEVOURER_SUMMON, 'spawnObjects')
    v = v if isinstance(v, list) else ([v] if v else [])
    out = []
    for x in v:
        s = str(x).strip()
        if s and db.has_record(s) and s not in out:
            out.append(s)
    return out


def _by_name_tag(db):
    """W2: every record in the DB described by one of his name tags.

    This is the witness that catches a DIFFICULTY CLONE - the Hunt already has one
    (`um_toxeus_hunt_l_99`); if the Devourer ever gets one it keeps his description
    tag, W1 never sees it, and the gate fails instead of shipping him unshrouded on
    Legendary.
    """
    out = []
    for n in db.record_names():
        d = _gv1(db, n, 'description')
        if d and str(d).lower() in _NAME_TAGS:
            cls = str(_gv1(db, n, 'Class') or '')
            if cls.startswith('Monster') or cls.startswith('Pet'):
                out.append(n)
    return sorted(out)


def shroud_roster(db):
    """W1 U W2 - every surface of the Devourer that must wear the shroud."""
    w1 = ([_DEVOURER] if db.has_record(_DEVOURER) else []) + _tiers_from_summon(db)
    seen, out = set(), []
    for r in w1 + _by_name_tag(db):
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


# ── BUILD ───────────────────────────────────────────────────────────────────

def _build_pak(db):
    _require(db, _PAK_DONOR, _SHADOWCLOAK_FX)
    if not db.has_record(_SHROUD_PAK):
        db.clone_record(_PAK_DONOR, _SHROUD_PAK)
    # value-only overrides on a cloned record (dtype preserved - the dtype lesson).
    db.set_field(_SHROUD_PAK, 'particleEffectNames', [_SHADOWCLOAK_FX] * _PARTICLE_COUNT)
    if _ATTACH:
        db.set_field(_SHROUD_PAK, 'particleEffectAttachPoints', list(_ATTACH))
    else:
        _del_field(db, _SHROUD_PAK, 'particleEffectAttachPoints')
    db._modified.add(_SHROUD_PAK)


def _build_skill(db):
    _require(db, _SKILL_DONOR)
    if not db.has_record(_SHROUD):
        db.clone_record(_SKILL_DONOR, _SHROUD)
    db.set_field(_SHROUD, 'charFxPakSelfNames', _SHROUD_PAK)
    # the donor's purple weapon tint -> the inert (0,0,0) NO-TINT default (b83 model)
    for f in ('skillWeaponTintRed', 'skillWeaponTintGreen', 'skillWeaponTintBlue'):
        if db.get_field_value(_SHROUD, f) is not None:
            db.set_field(_SHROUD, f, 0.0)
    db.set_field(_SHROUD, 'skillMaxLevel', 3)
    db.set_field(_SHROUD, 'FileDescription',
                 'SVC Devourer of Blood: black shadow shroud (visual only, no payload)')
    db._modified.add(_SHROUD)


def _wire_one(db, rec):
    """Both channels on one surface. Returns (slot, running_added)."""
    # PERSISTENT channel - his own self-buff in HIS OWN lowest free slot.
    slot = _slot_of(db, rec, _SHROUD) or _free_slot(db, rec)
    if slot is None:
        raise SystemExit(
            "[devourer_shroud] no free skillName slot on %s. R-26's spirit forbids "
            "dropping a functional skill to make room - stop and ask Will rather "
            "than sacrificing one." % rec)
    db.set_field(rec, 'skillName%d' % slot, _SHROUD)
    # The monster keeps its per-difficulty [1,2,3]; a pet tier IS one record per
    # tier, so a scalar 1 is the honest shape there. Level is cosmetic (the shroud
    # carries no payload at all), it only has to be non-zero to display.
    db.set_field(rec, 'skillLevel%d' % slot, [1, 2, 3] if rec == _DEVOURER else 1)

    # RUNNING channel - the marauders' own field, their own pak.
    cur = _gv1(db, rec, 'charFxPakRunningNames')
    running_added = False
    if not cur:
        db.set_field(rec, 'charFxPakRunningNames', _SHADOWCLOAK_PAK)
        running_added = True
    elif _norm(cur) != _norm(_SHADOWCLOAK_PAK):
        # Someone else owns this channel on this record. ADD, never take away:
        # stop rather than clobber another lane's FX.
        raise SystemExit(
            "[devourer_shroud] %s already carries charFxPakRunningNames=%r, which "
            "is NOT the demons' pak. This module refuses to overwrite another "
            "lane's running FX - resolve the ownership question first." % (rec, cur))
    db._modified.add(rec)
    return slot, running_added


def apply(db, tags):
    print("\n=== [devourer_shroud] THE DEVOURER'S BLACK SHADOW SHROUD "
          "(Will 2026-08-11) ===")
    _require(db, _DEVOURER)
    roster = shroud_roster(db)
    tiers = _tiers_from_summon(db)
    if not tiers:
        raise SystemExit(
            "[devourer_shroud] %s spawns no resolvable pet, so the tier roster is "
            "EMPTY. That is the exact b98 failure (shroud on the monster, nothing "
            "on what Will summons) - stop rather than ship a monster-only shroud."
            % _DEVOURER_SUMMON)
    _build_pak(db)
    _build_skill(db)
    for rec in roster:
        slot, ran = _wire_one(db, rec)
        print("  shroud -> skillName%-2d %s  %s%s"
              % (slot, '+ charFxPakRunningNames' if ran else '(running FX already ok)',
                 rec, '   (MONSTER)' if rec == _DEVOURER else '   (PET TIER)'))
    print("  %d surface(s) wired (1 monster + %d derived pet tier(s)) on the "
          "marauders' own confirmed shadowcloak smoke; NO existing skill dropped; "
          "svc_black_poison untouched." % (len(roster), len(tiers)))
    print("=== [devourer_shroud] done (verify() runs post-finalization) ===\n")
    return tags


# ── GATE ────────────────────────────────────────────────────────────────────

def verify(db, tags=None):
    problems = []

    # ── the skill ───────────────────────────────────────────────────────────
    if not db.has_record(_SHROUD):
        problems.append("shroud skill missing: %s" % _SHROUD)
    else:
        if _gv1(db, _SHROUD, 'Class') != 'Skill_BuffSelfToggled':
            problems.append("shroud Class=%r != Skill_BuffSelfToggled"
                            % _gv1(db, _SHROUD, 'Class'))
        if _norm(_gv1(db, _SHROUD, 'charFxPakSelfNames')) != _norm(_SHROUD_PAK):
            problems.append("shroud charFxPakSelfNames=%r != %s"
                            % (_gv1(db, _SHROUD, 'charFxPakSelfNames'), _SHROUD_PAK))
        # VISUAL-ONLY: a shroud must never quietly become a stat buff on a boss
        # Will has said he cannot kill (R-102 fifth amendment).
        payload = []
        for k, tf in (db.get_fields(_SHROUD) or {}).items():
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
                "cosmetic buff; a stat change here silently buffs a boss Will has "
                "already said he cannot kill." % sorted(set(payload))[:6])
        for f in ('skillWeaponTintRed', 'skillWeaponTintGreen', 'skillWeaponTintBlue'):
            t = _gv1(db, _SHROUD, f)
            if t not in (None, 0, 0.0):
                problems.append("shroud %s=%r (must stay the inert 0 NO-TINT default; "
                                "the donor's purple tint would recolour his weapon)"
                                % (f, t))
        # R-93: his kit may not be built out of the Enslaver's records.
        if 'enslaver' in _norm(_SHROUD):
            problems.append("R-93: the Devourer's shroud must be HIS OWN record, "
                            "not the Enslaver's (%s)" % _SHROUD)

    # ── the pak: colour + shape, both DERIVED from the demons' own ──────────
    if not db.has_record(_SHROUD_PAK):
        problems.append("shroud CharFxPak missing: %s" % _SHROUD_PAK)
    else:
        names = db.get_field_value(_SHROUD_PAK, 'particleEffectNames') or []
        names = names if isinstance(names, list) else [names]
        if not names or any(_norm(n) != _norm(_SHADOWCLOAK_FX) for n in names):
            problems.append(
                "COLOUR PROVENANCE: the shroud pak must use ONLY %s - the demons' "
                "own shadowcloak smoke, the single in-game-CONFIRMED black in this "
                "area (Will, R-102: 'the demons that he summons have the proper "
                "black shroud'). Got %r. 343_dark_smoke is NOT colour-confirmed - "
                "R-10 calls it green-rendering." % (_SHADOWCLOAK_FX, names))
        if len(names) != _PARTICLE_COUNT:
            problems.append(
                "shroud pak has %d particleEffectNames entr(ies), expected %d. The "
                "donor duplicated its effect once per attach point; with no attach "
                "points there is exactly ONE body emitter, as on the demons' pak."
                % (len(names), _PARTICLE_COUNT))
        apf = db.get_field_value(_SHROUD_PAK, 'particleEffectAttachPoints')
        ap = [str(x) for x in (apf if isinstance(apf, list) else [apf] if apf else [])
              if str(x).strip()]
        if ap != _ATTACH:
            problems.append(
                "SHAPE: shroud pak particleEffectAttachPoints=%r, expected %r. Will "
                "asked for a shroud AROUND him; the demons' %s emits from the WHOLE "
                "BODY with no attach points. A hand pair (the 343 donor's shape, and "
                "exactly what svc_black_poison already does to him) smokes from two "
                "fists instead. Bone names (Bone_R_Weapon) are doubly wrong here - "
                "those belong on an EffectEntity boneList, never on a pak."
                % (ap, _ATTACH, _SHADOWCLOAK_PAK.rsplit('\\', 1)[-1]))

    # the SHAPE expectation is only honest if DERIVED from the record it copies.
    if db.has_record(_SHADOWCLOAK_PAK):
        dapf = db.get_field_value(_SHADOWCLOAK_PAK, 'particleEffectAttachPoints')
        dap = [str(x) for x in (dapf if isinstance(dapf, list) else [dapf] if dapf else [])
               if str(x).strip()]
        if dap != _ATTACH:
            problems.append(
                "the DEMONS' pak %s now has particleEffectAttachPoints=%r while this "
                "module still copies %r. The shape reference moved; re-derive _ATTACH "
                "from it rather than letting the two shrouds drift apart."
                % (_SHADOWCLOAK_PAK, dap, _ATTACH))
        dn = db.get_field_value(_SHADOWCLOAK_PAK, 'particleEffectNames') or []
        dn = dn if isinstance(dn, list) else [dn]
        if [_norm(x) for x in dn] != [_norm(_SHADOWCLOAK_FX)] * _PARTICLE_COUNT:
            problems.append(
                "the DEMONS' pak %s no longer emits exactly %r; this module's "
                "'same shroud' claim is derived from it and is now false (got %r)."
                % (_SHADOWCLOAK_PAK, _SHADOWCLOAK_FX, dn))
    else:
        problems.append("the demons' shape/colour reference pak is missing: %s"
                        % _SHADOWCLOAK_PAK)

    if not db.has_record(_SHADOWCLOAK_FX):
        problems.append("the confirmed shadowcloak EffectEntity is missing: %s"
                        % _SHADOWCLOAK_FX)
    elif not _gv1(db, _SHADOWCLOAK_FX, 'effectFile'):
        problems.append("%s has no effectFile (A9 render resolution: the pak would "
                        "resolve to nothing)" % _SHADOWCLOAK_FX)

    # ── A9-STYLE RENDER RESOLUTION on the pak: resolution is not rendering ──
    if db.has_record(_SHROUD_PAK):
        status, detail = fx_asset_resolution(db)
        if status == 'FAIL':
            problems.append("A9 RENDER RESOLUTION: %s" % detail)
        elif status == 'SKIP':
            print("  [devourer_shroud] A9 render resolution DOWNGRADED (not a pass): %s"
                  % detail)
        else:
            print("  [devourer_shroud] A9 render resolution PASS: %s" % detail)

    # the demon he actually summons must still exist - "his demon summon guys" is
    # the whole reason this asset was chosen.
    if not db.has_record(_BLOODSPAWN):
        problems.append("the Devourer's summoned demons are missing (%s), so the "
                        "premise of Will's request no longer holds" % _BLOODSPAWN)
    if db.has_record(_MARAUDER):
        if _norm(_gv1(db, _MARAUDER, 'charFxPakRunningNames')) != _norm(_SHADOWCLOAK_PAK):
            problems.append(
                "the shroud's provenance record %s no longer carries %s on "
                "charFxPakRunningNames (got %r). That record IS the in-game proof "
                "this smoke is black; without it the colour claim is unevidenced."
                % (_MARAUDER, _SHADOWCLOAK_PAK, _gv1(db, _MARAUDER, 'charFxPakRunningNames')))
    else:
        problems.append("the shroud provenance record is missing: %s" % _MARAUDER)

    # ── ROSTER: the two witnesses must agree ────────────────────────────────
    if not db.has_record(_DEVOURER):
        problems.append("Devourer missing: %s" % _DEVOURER)
    if not db.has_record(_DEVOURER_SUMMON):
        problems.append(
            "the Devourer soul-summon is missing (%s), so the pet-tier roster "
            "cannot be derived and a tier could be silently skipped"
            % _DEVOURER_SUMMON)
    tiers = _tiers_from_summon(db)
    if db.has_record(_DEVOURER_SUMMON) and not tiers:
        problems.append(
            "%s spawns NO resolvable pet: the derived tier roster is EMPTY. b98 "
            "shipped a monster-only shroud exactly this way and Will reported it "
            "as never implemented." % _DEVOURER_SUMMON)
    w1 = set([_DEVOURER] if db.has_record(_DEVOURER) else []) | set(tiers)
    w2 = set(_by_name_tag(db))
    if w2 and w1 and w2 - w1:
        problems.append(
            "ROSTER WITNESS DISAGREEMENT: %r carr(y) a Devourer name tag but are "
            "not reachable from the anchor + summon. A difficulty clone or a new "
            "tier has appeared (the Hunt has exactly such a clone, "
            "um_toxeus_hunt_l_99) and would ship with no shroud."
            % sorted(w2 - w1))

    roster = shroud_roster(db)
    for rec in roster:
        is_pet = rec != _DEVOURER
        slot = _slot_of(db, rec, _SHROUD)
        if slot is None:
            problems.append(
                "SHROUD MISSING on %s%s - it is in none of its skillName slots. "
                "R-102's second amendment: b98 wired the MONSTER ONLY, every pet "
                "tier was skipped, and the pet is what Will summons."
                % (rec, ' (PET TIER)' if is_pet else ' (MONSTER)'))
        else:
            lv = db.get_field_value(rec, 'skillLevel%d' % slot)
            lv = list(lv) if isinstance(lv, list) else ([lv] if lv is not None else [])
            want = [1, 2, 3] if rec == _DEVOURER else [1]
            if not lv or not lv[0]:
                problems.append("%s: shroud sits at skillLevel%d=%r (level 0 is not "
                                "granted, so it never displays)" % (rec, slot, lv))
            elif lv != want:
                problems.append(
                    "%s: shroud skillLevel%d=%r, expected %r. The monster carries the "
                    "per-difficulty [1,2,3]; a pet tier IS one record per tier, so a "
                    "scalar 1 is its honest shape. A different array here means "
                    "another module has written this slot after us."
                    % (rec, slot, lv, want))
        # RUNNING channel - the marauders' own field on every surface.
        run = _gv1(db, rec, 'charFxPakRunningNames')
        if _norm(run) != _norm(_SHADOWCLOAK_PAK):
            problems.append(
                "%s: charFxPakRunningNames=%r, expected %s. This is the field and "
                "the pak his demons carry; 'the same one that his demon summon guys "
                "have' means this channel too, not only the persistent one."
                % (rec, run, _SHADOWCLOAK_PAK))
        # a self-buff toggle is inert unless the controller fires it
        ctrl = _gv1(db, rec, 'controller')
        if not ctrl or not db.has_record(str(ctrl)):
            problems.append("%s has no resolvable controller (%r), so its self-buff "
                            "shroud can never fire" % (rec, ctrl))
        else:
            trig = _gv1(db, str(ctrl), 'BuffSelfBehavior')
            if str(trig) != _BUFF_TRIGGER:
                problems.append(
                    "%s: controller %s has BuffSelfBehavior=%r, expected %r. A "
                    "Skill_BuffSelfToggled the AI never toggles is a slot with "
                    "nothing in it." % (rec, ctrl, trig, _BUFF_TRIGGER))
        # ADD, never take away: R-7's black poison must survive on every surface
        # that had it. (Its colour is a separate open question - BL-DEVSHROUD-1.)
        if _slot_of(db, rec, _BLACK_POISON) is None:
            problems.append(
                "%s LOST svc_black_poison. This lane ADDS a shroud; R-7 owns that "
                "record and the RETIREMENT PROTOCOL forbids this lane retiring it."
                % rec)
        # ── CRASH LAW (the build28 trap) ────────────────────────────────────
        # A charFxPak* field on a SpawnPet skill crashes the game. Assert it over
        # this record's WHOLE kit, not just the slots this module writes.
        for i, sk in sorted(_skill_slots(db, rec).items()):
            if not db.has_record(sk):
                continue
            cls = str(_gv1(db, sk, 'Class') or '')
            if not cls.startswith('Skill_SpawnPet'):
                continue
            bad = sorted({k.split('###')[0]
                          for k in (db.get_fields(sk) or {})
                          if k.split('###')[0].lower().startswith('charfxpak')})
            if bad:
                problems.append(
                    "CRASH LAW: %s skillName%d -> %s is %s and carries %r. FX belong "
                    "on MONSTER-RECORD fields or a Skill_BuffSelfToggled, NEVER a "
                    "charFxPak on a SpawnPet skill - that is the build28 crash trap."
                    % (rec, i, sk, cls, bad))

    if problems:
        for p in problems:
            print("  DEVOURER-SHROUD OFFENDER: %s" % p)
        raise SystemExit("devourer_shroud.verify FAILED: %d problem(s)" % len(problems))
    print("  [devourer_shroud].verify OK: the Devourer of Blood wears the demons' own "
          "confirmed shadowcloak smoke on BOTH channels (persistent self-buff + the "
          "marauders' charFxPakRunningNames), body-centred like theirs, visual-only "
          "(no payload, no tint), on ALL %d surface(s) - the monster AND every derived "
          "pet tier (%d) - each with a controller that actually fires self-buffs; "
          "svc_black_poison intact everywhere; no charFxPak on any SpawnPet skill in "
          "his kit (crash law). WHAT IS STILL NOT CLAIMED: how it READS in game "
          "(BL-DEVSHROUD-3), and the 343_dark_smoke hand-smoke that now coexists with "
          "it (BL-DEVSHROUD-1)." % (len(roster), len(tiers)))
    return tags


# ── NEGATIVE TEST ───────────────────────────────────────────────────────────

def _negtest():
    """py tools/patches/devourer_shroud.py --negtest"""
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

    _PETS = [r'records\skills\soulskills\pets\bloodtoxeus_%d.dbr' % i for i in (1, 2, 3)]
    _CTRL_M = r'records\controllers\monster\controller_skeleton_toxeus.dbr'
    _CTRL_P = (r'records\skills\spirit\drxpet\drxpet_controllers'
               r'\controller_skelly_aggressive.dbr')
    _SPAWN = r'records\skills\boss skills\svc_devourer_summonbloodspawn.dbr'

    def _base():
        db = _Stub()
        db.d[_SHADOWCLOAK_FX] = {'effectFile': [r'DRXeffects\shadowcloakrunning.pfx']}
        db.d[_SHADOWCLOAK_PAK] = {'particleEffectNames': [_SHADOWCLOAK_FX]}
        db.d[_SHROUD_PAK] = {'particleEffectNames': [_SHADOWCLOAK_FX] * _PARTICLE_COUNT}
        db.d[_SHROUD] = {'Class': ['Skill_BuffSelfToggled'],
                         'charFxPakSelfNames': [_SHROUD_PAK],
                         'skillWeaponTintRed': [0.0], 'skillWeaponTintGreen': [0.0],
                         'skillWeaponTintBlue': [0.0]}
        db.d[_BLACK_POISON] = {'Class': ['Skill_BuffSelfToggled']}
        db.d[_MARAUDER] = {'Class': ['Monster'],
                           'charFxPakRunningNames': [_SHADOWCLOAK_PAK]}
        db.d[_BLOODSPAWN] = {'Class': ['Monster']}
        db.d[_SPAWN] = {'Class': ['Skill_SpawnPetMonster'], 'spawnObjects': [_BLOODSPAWN]}
        db.d[_CTRL_M] = {'BuffSelfBehavior': [_BUFF_TRIGGER]}
        db.d[_CTRL_P] = {'BuffSelfBehavior': [_BUFF_TRIGGER]}
        db.d[_DEVOURER] = {'Class': ['Monster'], 'description': ['tagMonsterHemorrheus'],
                           'controller': [_CTRL_M],
                           'charFxPakRunningNames': [_SHADOWCLOAK_PAK],
                           'skillName3': [_BLACK_POISON],
                           'skillName18': [_SPAWN],
                           'skillName19': [_SHROUD], 'skillLevel19': [1, 2, 3]}
        db.d[_DEVOURER_SUMMON] = {'Class': ['Skill_SpawnPet'], 'spawnObjects': list(_PETS)}
        for p in _PETS:
            db.d[p] = {'Class': ['Pet'], 'description': ['tagMonsterHemorrheusPet'],
                       'controller': [_CTRL_P],
                       'charFxPakRunningNames': [_SHADOWCLOAK_PAK],
                       'skillName3': [_BLACK_POISON],
                       'skillName8': [_SHROUD], 'skillLevel8': [1]}
        return db

    plants = [
        ('THE WHOLE ASK: the Devourer never gets the shroud at all',
         lambda db: db.d[_DEVOURER].pop('skillName19')),
        ('shroud on the monster, on NO pet tier (the b98 defect verbatim)',
         lambda db: [db.d[p].pop('skillName8') for p in _PETS]),
        ('one pet tier is skipped while the other two are wired',
         lambda db: db.d[_PETS[1]].pop('skillName8')),
        ('a NEW 4th pet tier is summoned and never gets the shroud',
         lambda db: (db.d.__setitem__(
             r'records\skills\soulskills\pets\bloodtoxeus_4.dbr',
             {'Class': ['Pet'], 'description': ['tagMonsterHemorrheusPet'],
              'controller': [_CTRL_P], 'skillName3': [_BLACK_POISON]}),
             db.d[_DEVOURER_SUMMON].__setitem__(
                 'spawnObjects',
                 _PETS + [r'records\skills\soulskills\pets\bloodtoxeus_4.dbr']))),
        ('a LEGENDARY difficulty clone appears (the um_toxeus_hunt_l_99 pattern)',
         lambda db: db.d.__setitem__(
             r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_l_99.dbr',
             {'Class': ['Monster'], 'description': ['tagMonsterHemorrheus'],
              'controller': [_CTRL_M], 'skillName3': [_BLACK_POISON]})),
        ('the summon loses its spawnObjects, so the tier roster goes silently empty',
         lambda db: db.d[_DEVOURER_SUMMON].__setitem__('spawnObjects', [])),
        ('the RUNNING channel is never added (only half the demons\' shroud)',
         lambda db: db.d[_DEVOURER].pop('charFxPakRunningNames')),
        ('a pet loses the running channel',
         lambda db: db.d[_PETS[2]].__setitem__('charFxPakRunningNames', [''])),
        ('unconfirmed colour asset swapped in (343_dark_smoke)',
         lambda db: db.d[_SHROUD_PAK].__setitem__(
             'particleEffectNames', [r'records\effects\custom\343_dark_smoke.dbr'])),
        ('the donor hand-pair comes back (hands, not "around him")',
         lambda db: db.d[_SHROUD_PAK].__setitem__(
             'particleEffectAttachPoints', ['R Hand', 'L Hand'])),
        ('bone names used where attach-point names belong',
         lambda db: db.d[_SHROUD_PAK].__setitem__(
             'particleEffectAttachPoints', ['Bone_R_Weapon', 'Bone_L_Weapon'])),
        ('one emitter per (absent) attach point becomes two duplicate emitters',
         lambda db: db.d[_SHROUD_PAK].__setitem__(
             'particleEffectNames', [_SHADOWCLOAK_FX, _SHADOWCLOAK_FX])),
        ('the demons\' shape reference itself drifts to a hand pair',
         lambda db: db.d[_SHADOWCLOAK_PAK].__setitem__(
             'particleEffectAttachPoints', ['R Hand', 'L Hand'])),
        ('the demons\' pak stops emitting the confirmed particle',
         lambda db: db.d[_SHADOWCLOAK_PAK].__setitem__(
             'particleEffectNames', [r'records\effects\custom\343_dark_smoke.dbr'])),
        ('the provenance record loses the shroud, so "it is black" is unevidenced',
         lambda db: db.d[_MARAUDER].__setitem__('charFxPakRunningNames', [''])),
        ('the effect entity resolves to no .pfx (A9 render resolution)',
         lambda db: db.d[_SHADOWCLOAK_FX].__setitem__('effectFile', [''])),
        ('A9: the .pfx names a file that is NOT in the shipped payload',
         lambda db: db.d[_SHADOWCLOAK_FX].__setitem__(
             'effectFile', [r'DRXeffects\this_pfx_does_not_ship.pfx'])),
        ('A9: the .pfx names an archive the mod does not ship at all',
         lambda db: db.d[_SHADOWCLOAK_FX].__setitem__(
             'effectFile', [r'NoSuchArchive\shadowcloakrunning.pfx'])),
        ('the shroud grows a combat payload',
         lambda db: db.d[_SHROUD].__setitem__('offensivePhysicalMin', [500.0])),
        ('the donor purple tint comes back',
         lambda db: db.d[_SHROUD].__setitem__('skillWeaponTintBlue', [1.0])),
        ('the shroud stops being a self-buff toggle',
         lambda db: db.d[_SHROUD].__setitem__('Class', ['Skill_AttackRadius'])),
        ('the shroud sits at level 0 (in a slot, never displayed)',
         lambda db: db.d[_PETS[0]].__setitem__('skillLevel8', [0])),
        ('a later module overwrites the pet shroud level with a per-difficulty array',
         lambda db: db.d[_PETS[0]].__setitem__('skillLevel8', [4, 6, 8])),
        ('the monster shroud loses its per-difficulty [1,2,3]',
         lambda db: db.d[_DEVOURER].__setitem__('skillLevel19', [1])),
        ('a controller stops firing self-buffs, so the toggle is inert',
         lambda db: db.d[_CTRL_P].__setitem__('BuffSelfBehavior', ['NeverBuff'])),
        ('R-7\'s black poison is taken away instead of added to',
         lambda db: db.d[_DEVOURER].pop('skillName3')),
        ('CRASH LAW: a charFxPak lands on his SpawnPet skill (the build28 trap)',
         lambda db: db.d[_SPAWN].__setitem__('charFxPakSelfNames', [_SHROUD_PAK])),
        ('the demons he summons disappear, so the request premise is gone',
         lambda db: db.d.pop(_BLOODSPAWN)),
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
