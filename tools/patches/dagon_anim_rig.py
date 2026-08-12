r"""dagon_anim_rig - unfreeze Dagon, Lord of the Poisoned Deep, and gate the whole
monster roster on the invariant he violated.

WHY THIS EXISTS (RCA: docs/reports/dagon_frozen_rca.md)
--------------------------------------------------------
Will (2026-08-11): "Dagon, lord of the poisoned deep is frozen like the maened thrown
object guys were". He named the failure class correctly.

THE PRECEDENT (R-100 #15, commits 02f1807 / 83d9fc2 / adfda67 - the frozen
thrown-wielders). Its finding, stated as a law:

    A creature is a statue when, for the stance it is in, NEITHER its own record NOR
    its `charAnimationTableName` supplies an `.anm` for RunAnim / WalkAnim /
    AttackAnim1.

Two properties of that precedent carry over verbatim:
  * The freeze lives on the ANIMATION surface, not the equipment/kit surface.
    `thrown_restore` had already fixed the maenads' equipment and they stayed frozen;
    b52's `_fix_dagon_kit` had already fixed Dagon's dead skills and he stayed frozen.
  * The invariant is the UNION of the two surfaces, because the record OVERRIDES the
    table. A record-level clip shadows the table's clip for the same slot.

THE BROKEN CHAIN (measured on the shipped build83 `44499f56`, base `database.arz`,
and `upstream/soulvizier_098i/Database/database.arz`):

    records\test\boss_dagon_66.dbr
        mesh                   = Creatures\Monster\Ichthian\IchthianMage01.msh
        charAnimationTableName = records\creature\monster\d2custom\anm\anm_dagon.dbr

    TABLE  : resolves in NEITHER the mod arz NOR the base game arz. There are ZERO
             `d2custom` records in the entire database. It contributes 0 clips.
    RECORD : binds 13 `.anm` clips - every single one a
             `Creatures\Monster\HYDRA\ANM\Hydra_*.anm`, on a creature whose mesh is
             IchthianMage01. A Hydra animation set on an Ichthian skeleton.
    ==>      `unarmedWalkAnim` is UNBOUND ON BOTH SURFACES. He equips nothing
             (chanceToEquipRightHand = chanceToEquipLeftHand = 0), so `unarmed` is his
             only stance. He has no walk animation. He stands. Statue.

NOT OURS. SV 0.98i's own database ships the identical dead table, the identical 13
Hydra clips and the identical missing WalkAnim - and `d2custom\anm\anm_dagon.dbr` is
absent from SV's OWN database too. It is the same never-shipped Diablo-namespace that
made his SKILLS dead references in b52. The record is a frankenstein: an Ichthian mesh,
a Hydra animation set, a Harpy `ActorName`, and a `d2custom` table.

WHY NO GATE CAUGHT IT - the same blind spot, twice, on one record. `thrown_anim_rig`
already states this freeze invariant DB-wide, but its `table_binds` assumes:
    "Absent from the overlay -> pure base-game pass-through ... healthy by construction"
which is the IDENTICAL assumption `validate_tags` made in b52 ("every non-mod tag
resolves from the base game"). Both are false for `d2custom`, which resolves from
nothing. (It also scopes only THROWN wielders; Dagon equips nothing at all.) The gate
below closes it the way b52 closed the tag gate: CROSS-CHECK THE BASE ARZ instead of
assuming it.

WHAT THIS MODULE DOES
---------------------
(1) Repoints `charAnimationTableName` onto `records\creature\monster\ichthian\anm\
    anm_ichthian.dbr` - the table 43 of his 44 same-mesh siblings already use. It
    resolves, it is a clean `CharAnimationTable.tpl` (NOT the `Monster.tpl` corruption
    SV inflicted on ANM_Maenad), and it binds 71 clips including all 12 unarmed slots.
    NO CLONE IS NEEDED and NO SHARED RECORD IS EDITED: unlike the maenad fix, which had
    to MODIFY its tables and therefore had to clone them under the SHARED-RECORD LAW,
    this fix only POINTS AT the table. The 43 existing carriers are untouched.

(2) Restores the stance ON BOTH SURFACES (the `adfda67` law: write identical values to
    the record and the table, so whichever surface the engine reads it gets the same
    animation). All 13 cross-rig Hydra clips are repointed to the in-rig Ichthian clip
    the table binds for that slot, and the four unbound slots - including the
    load-bearing `unarmedWalkAnim` - are added.

ANIMATION FIELDS ONLY. Not one gameplay field is touched: his b52 kit (Tidal Strike
primary, Tidal Orb, Venom Nova, Super Bite, Poison Gas Bomb), his name tag
`tagSVCMonsterDagon` ("Dagon, Lord of the Poisoned Deep"), characterRunSpeed, life,
damage, his soul and its 66% drop all survive byte-identical.

CRASH LAWS: no FX field on a monster record (animation clips are not FX), no Pet.tpl
equipment copy, no `clone_record`, no explicit `dtype` on any write.

DELIBERATELY LEFT ALONE: `ActorName = Greece_Creature_Monster_Harpy_HarpyCrag01` is a
third cross-rig leftover (42 of the 43 working same-mesh ichthians carry NO ActorName at
all). It is not the freeze, it is byte-identical in SV 0.98i, and rebinding an actor has
sound/actor consequences this lane cannot measure. Filed BL-DAGON-ACTORNAME-1.

THE GATE (`verify`) - a fail-loud playable-anim invariant for WILD MONSTERS, which is
what the class was missing (`thrown_anim_rig` gates thrown stances only):

    Every SPAWN-REFERENCED Class=Monster record must resolve, on the union of its own
    record and its charAnimationTableName (checked against the mod overlay AND the base
    game arz), an `.anm` for RunAnim + WalkAnim + AttackAnim1 in the stance it enters.

  * HARD FAIL when the violator is spawn-referenced (the Dagon case).
  * WARN when it is inert - never spawned (the `am_raptor_thunderlizard_33` case), so a
    pre-existing cut-content backlog can never block a build.
  * Base arz unavailable -> the DB-WIDE cross-check degrades to WARN with a message
    (build-safe; the `validate_tags` precedent), while the TARGETED Dagon invariant
    stays HARD.

The base-game boss `skeletaltyphon` is the control that keeps this honest: it ships a
DEAD animation table in VANILLA and animates fine, because its record binds all three
critical slots itself. A naive "dead table = fail" gate would red the base game; the
union law separates it from Dagon cleanly.

Negative tests: `py tools/patches/dagon_anim_rig.py --negtest <arz>`.
"""
import os
import sys
from pathlib import Path

MODULE_NAME = "Dagon frozen: animation chain + monster playable-anim gate"

# ---------------------------------------------------------------------------
# The record, the dead reference it carries, and the table that cures it.
# ---------------------------------------------------------------------------
DAGON = r"records\test\boss_dagon_66.dbr"
DEAD_TABLE = r"records\creature\monster\d2custom\anm\anm_dagon.dbr"
ICHTHIAN_TABLE = r"records\creature\monster\ichthian\anm\anm_ichthian.dbr"
DAGON_MESH_KEY = "ichthianmage01"

# The clip families that do NOT belong on an IchthianMage01 rig. `Hydra` is what SV
# left on the record; the gate refuses any of them on Dagon after the fix.
WRONG_RIG_MARKER = r"\hydra\\"

_ICH = "Creatures\\Monster\\Ichthian\\ANM\\"
_JACKAL = "Creatures\\Monster\\JackalMan\\ANM\\"

# The full unarmed stance, written on the RECORD surface. Twelve of these are the
# BYTE-IDENTICAL value `anm_ichthian` binds for the same slot (so the two surfaces
# agree, per adfda67); the four the table does not bind - SpecialAnim2/3/4 and
# LongIdleAnim - are drawn from clips the table DOES bind for this stance, so every
# value is proven in-rig and proven present.
UNARMED = {
    # --- the three CRITICAL slots: without these he is a statue -------------
    "unarmedWalkAnim":         _ICH + "Ichthian_Walk.anm",       # WAS UNBOUND - the freeze
    "unarmedRunAnim":          _ICH + "Ichthian_Run.anm",
    "unarmedAttackAnim1":      _ICH + "IchthianMage_Staff_AttAlpha.anm",
    # --- the rest of the stance --------------------------------------------
    "unarmedAttackAnim2":      _ICH + "IchthianMage_Staff_AttBeta.anm",
    "unarmedAttackAnim3":      _ICH + "IchthianMage_Staff_AttGamma.anm",
    "unarmedAttackIdleAnim":   _ICH + "IchthianMage_Staff_AttIdle.anm",
    "unarmedSpellAttackAnim":  _ICH + "IchthianMage_Staff_Skill_CastProjectile.anm",
    "unarmedBuffOtherAnim1":   _ICH + "IchthianMage_Staff_Skill_BuffOther.anm",
    "unarmedBuffSelfAnim1":    _ICH + "IchthianMage_Staff_Skill_BuffOther.anm",
    "unarmedStunAnim":         _ICH + "Ichthian_Stun.anm",
    "unarmedFidgetAnim1":      _ICH + "Ichthian_Emote_AllAlpha.anm",
    # the same-mesh siblings' own death clip; the ichthian rig is JackalMan-compatible
    # (anm_ichthian itself binds JackalMan clips for the whole dHanded stance).
    "unarmedDieAnim1":         _JACKAL + "JackalMan_DieAlpha.anm",
    # one animated special per skill in his b52 kit (5 specials).
    "unarmedSpecialAnim1":     _ICH + "IchthianMage_Staff_AttBeta.anm",
    "unarmedSpecialAnim2":     _ICH + "IchthianMage_Staff_AttGamma.anm",
    "unarmedSpecialAnim3":     _ICH + "IchthianMage_Staff_Skill_CastProjectile.anm",
    "unarmedSpecialAnim4":     _ICH + "IchthianMage_Staff_AttAlpha.anm",
    "unarmedLongIdleAnim":     _ICH + "Ichthian_Emote_AllAlpha.anm",
}

# The slots that decide whether a creature can MOVE and ATTACK. Identical to
# thrown_anim_rig.CRITICAL_SLOTS - the same law, stated for every stance.
CRITICAL_SLOTS = ("RunAnim", "WalkAnim", "AttackAnim1")

STANCES = ("unarmed", "oneHanded", "sHanded", "dHanded", "bow", "spear", "staff",
           "rangedOneHand", "dualRanged")


# ---------------------------------------------------------------------------
def _norm(s):
    return str(s).replace("/", "\\").lower()


def _scalar(v):
    return v[0] if isinstance(v, list) and v else v


def _fv(fields, key):
    """Scalar value of `key` in a decoded field map, or None.

    Reads the decoded map directly (same reason thrown_anim_rig._fv does: verify()
    sweeps ~51k records and `get_field_value`'s absent-key path is a linear scan of
    each record's ~1000 fields).
    """
    if not fields:
        return None
    tf = fields.get(key)
    if tf is None:
        low = key.lower()
        for k, t in fields.items():
            if k.lower() == low:
                tf = t
                break
    if tf is None:
        return None
    return _scalar(tf.value)


def _is_anm(v):
    return isinstance(v, str) and v.lower().endswith(".anm")


def _clips(fields):
    """{slot: clip} for every field of a decoded map whose value is an .anm."""
    out = {}
    if not fields:
        return out
    for k, tf in fields.items():
        v = _scalar(tf.value)
        if _is_anm(v):
            out[k] = v
    return out


# ---------------------------------------------------------------------------
def discover_base_arz():
    """Best-effort discovery of the player's base-game `database.arz`.

    Mirrors `build_text_arc.discover_base_text_en` exactly (SVC_TQAE_ROOT, then the
    default Steam library, then libraryfolders.vdf). Returns an existing Path or None -
    and None is never fatal: the DB-wide cross-check degrades to WARN, per the
    validate_tags precedent, while the targeted Dagon invariant stays hard.
    """
    import re
    candidates = []
    root_env = os.environ.get("SVC_TQAE_ROOT")
    if root_env and root_env.strip():
        candidates.append(Path(root_env.strip()))
    default_steam = Path(r"C:\Program Files (x86)\Steam")
    candidates.append(default_steam / "steamapps" / "common" /
                      "Titan Quest Anniversary Edition")
    vdf = default_steam / "steamapps" / "libraryfolders.vdf"
    if vdf.is_file():
        try:
            for m in re.finditer(r'"path"\s+"([^"]+)"',
                                 vdf.read_text(encoding="utf-8", errors="ignore")):
                lib = m.group(1).replace("\\\\", "\\")
                candidates.append(Path(lib) / "steamapps" / "common" /
                                  "Titan Quest Anniversary Edition")
        except Exception:
            pass  # a malformed vdf never blocks the build
    for root in candidates:
        arz = root / "Database" / "database.arz"
        try:
            if arz.is_file():
                return arz
        except OSError:
            continue
    return None


def referenced_anms():
    """Every distinct `.anm` asset this module binds (for the asset probe).

    Mirrors `thrown_anim_rig.referenced_anms` so one probe can resolve the whole
    frozen class: `py tools/debug/probe_anm_asset_resolve.py <game_dir> <mod_res>`.
    """
    return sorted(set(UNARMED.values()))


_BASE_CACHE = {}


def _base_record_names():
    """Lowercased record-name set of the base game arz, or None if unavailable.

    Cached: verify() may run more than once in a session and the base arz is 74k
    records.
    """
    if "names" in _BASE_CACHE:
        return _BASE_CACHE["names"]
    names = None
    p = discover_base_arz()
    if p is not None:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
            from arz_patcher import ArzDatabase  # noqa: E402
            names = {_norm(n) for n in ArzDatabase.from_arz(p).record_names()}
        except Exception:
            names = None  # a load failure degrades to WARN, never blocks the build
    _BASE_CACHE["names"] = names
    return names


# ---------------------------------------------------------------------------
# THE INVARIANT (one implementation, shared by verify / negtest / the probe)
# ---------------------------------------------------------------------------
def _complete_stances(on_record):
    """Stances for which the RECORD alone binds the whole critical set."""
    return sorted(s for s in STANCES
                  if all(_is_anm(on_record.get(s + c)) for c in CRITICAL_SLOTS))


def scan_frozen_monsters(db, base_names=None):
    r"""(violations, spawn_referenced, base_available) over the whole DB.

    THE INVARIANT
    -------------
        A Class=Monster record that NAMES a `charAnimationTableName` which resolves
        in NEITHER the mod overlay NOR the base game must supply, ON ITS OWN RECORD,
        a complete critical set (RunAnim + WalkAnim + AttackAnim1) for at least one
        stance. Otherwise nothing in the game can animate it: it is a statue.

    violations = [(record, table, table_state, [what is missing])]

    WHY THIS EXACT SHAPE, AND NOT THE OBVIOUS ONE. Two weaker statements were
    measured against the shipped build83 and both cry wolf:

      * "every monster must bind Run/Walk/Attack1 for every stance it binds any clip
        for" -> 1,399 violations, mostly base monsters carrying a stray clip for a
        stance they never enter.
      * "every monster must bind Run/Walk/Attack1 for the stance it fights in"
        -> 60 spawn-referenced violations, ALL of them correct base-game design:
        rooted plants (quilvine / nightblossom / deathvine / hellflower) that attack
        in place, static props with Class=Monster (siege towers, crystal shards,
        talos_decoration, manticore_bones), flying bosses with no walk clip (hydras,
        carrion birds), and non-combat quest NPCs with no attack clip. Immobility is
        AUTHORED all over the base game, so "missing a clip" cannot be the signal.

    What separates Dagon from every one of those is not a missing clip - it is a
    DANGLING REFERENCE. A rooted quilvine names `anm_quilvine`, which loads and
    deliberately binds no walk. Dagon names `d2custom\anm\anm_dagon`, which loads
    from nothing. Authored immobility resolves; a broken chain does not. That is the
    same "resolves from nothing" class b52 closed in validate_tags, and it is the
    only condition here that is unambiguously a defect rather than a design choice.

    A record that names NO table at all is likewise authored intent (the base game
    ships hundreds of props that way), not a dangling reference, so it is out of
    scope.

    `table_state` is "ok" (resolves in the mod overlay), "base" (resolves in the base
    game arz), "dead" (resolves NOWHERE - the finding) or "none" (no table named).

    Base-game `skeletaltyphon` is the control: it carries a DEAD table in VANILLA and
    animates fine, because its own record binds all three critical slots. It passes
    on the record-surface clause, which is why this gate does not red the base game.
    """
    by_lower = {_norm(n): n for n in db.record_names()}
    base_available = base_names is not None
    tbl_cache = {}

    def table_state(tbl):
        key = _norm(tbl)
        if key in tbl_cache:
            return tbl_cache[key]
        if key in by_lower:
            res = "ok"
        elif base_available and key in base_names:
            # Resolves from the base game: healthy by construction - the base game
            # animates with it.
            res = "base"
        elif base_available:
            res = "dead"        # PROVEN dead: absent from BOTH the mod and the base
        else:
            res = "unknown"     # no base arz -> cannot prove; never a finding
        tbl_cache[key] = res
        return res

    # Which records are named by some OTHER record (i.e. can actually spawn).
    spawn_referenced = set()
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        self_n = _norm(name)
        for tf in fields.values():
            v = tf.value
            for vv in (v if isinstance(v, list) else [v]):
                if isinstance(vv, str) and vv.lower().endswith(".dbr"):
                    n = _norm(vv)
                    if n != self_n:
                        spawn_referenced.add(n)

    violations = []
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields or _fv(fields, "Class") != "Monster":
            continue
        if not _fv(fields, "mesh"):
            continue  # spawner_* proxies etc: Class=Monster but nothing to animate
        tbl = _fv(fields, "charAnimationTableName")
        if not tbl or not str(tbl).strip():
            continue  # names no table: authored intent, not a dangling reference
        state = table_state(tbl)
        if state != "dead":
            continue
        on_record = _clips(fields)
        complete = _complete_stances(on_record)
        if not complete:
            have = sorted(k for k in on_record
                          if any(k.endswith(c) for c in CRITICAL_SLOTS))
            violations.append((name, tbl, state,
                               "its animation table resolves NOWHERE and its own "
                               "record completes no stance (critical clips on the "
                               "record: %s)" % (", ".join(have) or "NONE")))
    return violations, spawn_referenced, base_available


# ---------------------------------------------------------------------------
def apply(db, tags):
    """Repoint Dagon's animation table and restore his unarmed stance on BOTH
    surfaces. Idempotent; fail-loud if the ground truth moved."""
    if not db.has_record(DAGON):
        raise SystemExit(
            "dagon_anim_rig: %s is ABSENT. Dagon is promoted into 23 ichthian spawn "
            "pools by the monolith's _add_dagon_to_ichthian_pools; if the record is "
            "gone that promotion is broken and this module's premise is void." % DAGON)
    if not db.has_record(ICHTHIAN_TABLE):
        raise SystemExit(
            "dagon_anim_rig: the cure table %s is ABSENT. It is the table 43 of "
            "Dagon's 44 same-mesh siblings use; without it there is nothing proven to "
            "repoint onto." % ICHTHIAN_TABLE)

    mesh = _fv(db.get_fields(DAGON), "mesh")
    if not mesh or DAGON_MESH_KEY not in _norm(mesh):
        raise SystemExit(
            "dagon_anim_rig: Dagon's mesh is %r, not an IchthianMage01 rig. The whole "
            "clip set below is chosen to MATCH that mesh; on a different rig it would "
            "be exactly the cross-rig defect this module exists to remove." % (mesh,))

    # (1) the table. Pure repoint - the shared table is READ, never edited, so no
    #     clone is required and no non-target carrier is disturbed.
    db.set_field(DAGON, "charAnimationTableName", ICHTHIAN_TABLE)

    # (2) the record surface: every slot, in-rig, identical to the table where the
    #     table binds it.
    for slot, clip in UNARMED.items():
        db.set_field(DAGON, slot, clip)


# ---------------------------------------------------------------------------
def verify(db, tags):
    """Fail-loud gate. Targeted Dagon invariant (always hard) + the DB-wide
    playable-anim invariant for every spawn-referenced monster."""
    _verify_dagon(db)
    _verify_roster(db)


def _verify_dagon(db):
    fields = db.get_fields(DAGON)
    if not fields:
        raise SystemExit("dagon_anim_rig GATE: %s is absent." % DAGON)

    tbl = _fv(fields, "charAnimationTableName")
    if _norm(tbl or "") != _norm(ICHTHIAN_TABLE):
        raise SystemExit(
            "dagon_anim_rig GATE: Dagon's charAnimationTableName is %r, expected %s. "
            "%s" % (tbl, ICHTHIAN_TABLE,
                    "This is the SHIPPED BUG re-planted." if _norm(tbl or "") ==
                    _norm(DEAD_TABLE) else "The repoint did not land."))
    if not db.has_record(ICHTHIAN_TABLE):
        raise SystemExit("dagon_anim_rig GATE: %s does not resolve." % ICHTHIAN_TABLE)

    on_record = _clips(fields)
    tbinds = _clips(db.get_fields(ICHTHIAN_TABLE))

    # BOTH surfaces, per adfda67: the record must carry the full stance itself, so a
    # future corruption of the shared table cannot re-freeze him.
    missing = [s for s in UNARMED if not _is_anm(on_record.get(s))]
    if missing:
        crit = [m for m in missing if any(m.endswith(c) for c in CRITICAL_SLOTS)]
        raise SystemExit(
            "dagon_anim_rig GATE: Dagon's record leaves %d unarmed slot(s) unbound: %s"
            "%s" % (len(missing), ", ".join(sorted(missing)),
                    "  <-- CRITICAL: %s unbound is the statue state Will reported."
                    % ", ".join(sorted(crit)) if crit else ""))

    # every value must be the exact clip we chose, and must agree with the table
    # wherever the table binds the same slot
    for slot, want in UNARMED.items():
        got = on_record.get(slot)
        if _norm(got) != _norm(want):
            raise SystemExit(
                "dagon_anim_rig GATE: Dagon's %s = %r, expected %r." % (slot, got, want))
        t = tbinds.get(slot)
        if t is not None and _norm(t) != _norm(want):
            raise SystemExit(
                "dagon_anim_rig GATE: surfaces disagree on %s - record %r vs table %r. "
                "adfda67 requires identical values on both, so the engine gets the same "
                "animation whichever surface it reads." % (slot, want, t))

    # no cross-rig clip may survive on an Ichthian-mesh record
    strays = {k: v for k, v in on_record.items() if WRONG_RIG_MARKER in _norm(v) + "\\"}
    if strays:
        raise SystemExit(
            "dagon_anim_rig GATE: %d cross-rig HYDRA clip(s) still bound on Dagon's "
            "ICHTHIAN mesh: %s. That is the animation-resolution mismatch this module "
            "exists to remove." % (len(strays),
                                   ", ".join("%s=%s" % (k, v) for k, v in sorted(strays.items()))))

    # the fix must not have touched his identity or his b52 kit
    if _fv(fields, "description") != "tagSVCMonsterDagon":
        raise SystemExit(
            "dagon_anim_rig GATE: Dagon's description tag is %r, expected "
            "tagSVCMonsterDagon - the b52 name fix was clobbered."
            % _fv(fields, "description"))
    primary = _norm(_fv(fields, "specialAttackSkillName") or "")
    if "ichthian_tidalstrike" not in primary:
        raise SystemExit(
            "dagon_anim_rig GATE: Dagon's primary is %r, expected his b52 Tidal Strike "
            "(WILL_DECISIONS). This module writes animation fields ONLY; a changed kit "
            "means something else overwrote it." % primary)


def _verify_roster(db):
    base_names = _base_record_names()
    violations, spawn_referenced, base_available = scan_frozen_monsters(db, base_names)

    if not base_available:
        print("  dagon_anim_rig GATE: WARN - the base game database.arz was not found "
              "(SVC_TQAE_ROOT / Steam), so a table absent from the mod overlay cannot "
              "be PROVEN dead. The DB-wide monster playable-anim cross-check is "
              "degraded to WARN for this build; the targeted Dagon invariant above "
              "ran hard. This is the validate_tags precedent - a missing base install "
              "never blocks a build.")

    hard, warn = [], []
    for v in violations:
        (hard if _norm(v[0]) in spawn_referenced else warn).append(v)

    for rec, tbl, state, why in sorted(warn):
        print("  dagon_anim_rig GATE: WARN - %s would stand frozen (%s; table=%s) but "
              "it is NOT spawn-referenced, so it never appears in game. Inert cut "
              "content: recorded, not blocked." % (rec, why, tbl))

    if hard:
        lines = ["dagon_anim_rig GATE: %d SPAWN-REFERENCED monster(s) have an "
                 "animation chain that cannot resolve, and will stand frozen in game "
                 "exactly as Dagon and the maenad throwers did:" % len(hard)]
        for rec, tbl, state, why in sorted(hard):
            lines.append("    %s" % rec)
            lines.append("        charAnimationTableName = %s   [%s]" % (tbl, state))
            lines.append("        %s" % why)
        lines.append("    Fix by repointing charAnimationTableName at a table that "
                     "RESOLVES (the sibling records on the same mesh are the proven "
                     "donor), or by binding RunAnim+WalkAnim+AttackAnim1 for one "
                     "stance on the record itself. Authored immobility is fine - a "
                     "table that resolves and binds nothing never trips this gate; a "
                     "reference that resolves from NOTHING always does.")
        raise SystemExit("\n".join(lines))

    print("  dagon_anim_rig GATE: OK - Dagon animates on both surfaces (%d unarmed "
          "slots, 0 cross-rig clips, table=%s); no spawn-referenced monster carries a "
          "dangling animation chain (%d inert violator(s) warned)."
          % (len(UNARMED), ICHTHIAN_TABLE, len(warn)))


# ---------------------------------------------------------------------------
# NEGATIVE TESTS - re-plant the defect and prove the gate goes RED
# ---------------------------------------------------------------------------
def _negtest(arz_path):
    """Re-plant the defect, prove the gate goes RED, prove nothing leaks."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from arz_patcher import ArzDatabase  # noqa: E402

    db = ArzDatabase.from_arz(Path(arz_path))
    apply(db, {})
    try:
        verify(db, {})
    except SystemExit as e:
        print("PRECONDITION FAILED: the gate is RED on the FIXED db:\n%s" % e)
        return 1

    KEYS = ["charAnimationTableName"] + list(UNARMED)

    def snap(rec, keys):
        f = db.get_fields(rec)
        return {k: _fv(f, k) for k in keys}

    def restore(rec, s):
        for k, v in s.items():
            if v is not None:
                db.set_field(rec, k, v)

    good = snap(DAGON, KEYS)
    results = []

    def case(label, mutate, gate, expect_red=True, rec=DAGON, keys=None):
        """Run `gate` after `mutate`, record the colour, then restore."""
        ks = keys or KEYS
        s = snap(rec, ks)
        mutate()
        red, msg = False, ""
        try:
            gate(db, {}) if gate is verify else gate(db)
        except SystemExit as e:
            red, msg = True, str(e).splitlines()[0]
        restore(rec, s)
        restore(DAGON, good)
        results.append((red == expect_red, label, "RED" if red else "GREEN",
                        "RED" if expect_red else "GREEN", msg))

    def roster(d):
        _verify_roster(d)

    # ---- the Dagon-targeted clauses -------------------------------------
    # 1: the shipped bug, verbatim
    case("repoint the table back at the dead d2custom table (THE SHIPPED BUG)",
         lambda: db.set_field(DAGON, "charAnimationTableName", DEAD_TABLE), verify)
    # 2-4: each critical slot lost from the record surface (table left correct, so
    #      this exercises the BOTH-SURFACES clause of adfda67, not the table check)
    for slot in ("unarmedWalkAnim", "unarmedRunAnim", "unarmedAttackAnim1"):
        case("lose %s from the record surface (adfda67 both-surfaces law)" % slot,
             (lambda s=slot: db.set_field(DAGON, s, "")), verify)
    # 5: a cross-rig clip survives on the ichthian mesh
    case("leave a Hydra clip on the Ichthian-mesh record (cross-rig)",
         lambda: db.set_field(DAGON, "unarmedRunAnim",
                              r"Creatures\Monster\Hydra\ANM\Hydra_Run.anm"), verify)
    # 6: a mesh bound where an animation table belongs
    case("point charAnimationTableName at a .msh instead of a table .dbr",
         lambda: db.set_field(DAGON, "charAnimationTableName",
                              r"Creatures\Monster\Ichthian\IchthianMage01.msh"), verify)
    # 7: the b52 kit must not be collateral damage of an anim-only module
    case("clobber the b52 Tidal Strike primary (identity guard)",
         lambda: db.set_field(DAGON, "specialAttackSkillName",
                              r"records\skills\boss skills\hydra_superbite.dbr"),
         verify, keys=KEYS + ["specialAttackSkillName"])

    # ---- the ROSTER clauses (must hold with no knowledge of Dagon) --------
    # 8: THE STATUE STATE, reached independently: dead table AND no complete stance
    #    on the record. This is the exact engine condition, and the roster gate must
    #    catch it on its own.
    def statue():
        db.set_field(DAGON, "charAnimationTableName", DEAD_TABLE)
        for s in UNARMED:
            db.set_field(DAGON, s, "")
    case("dead table AND no complete stance on the record (THE STATUE STATE) "
         "- ROSTER gate", statue, roster)
    # 9: the invariant is roster-wide, not Dagon-shaped. am_raptor_thunderlizard_33 is
    #    a REAL already-frozen record the gate currently only WARNs because nothing
    #    spawns it; promote it into a live pool and the SAME gate must escalate to RED.
    #    (No clone_record - the crash laws forbid it and none is needed.)
    inert = r"records\test\am_raptor_thunderlizard_33.dbr"
    carrier = r"records\proxies greek\area001\pools\beastmen\icthian_01_shamanmelee01.dbr"
    if db.has_record(inert) and db.has_record(carrier):
        case("promote the INERT frozen raptor into a live spawn pool (WARN must "
             "escalate to RED) - ROSTER gate",
             lambda: db.set_field(carrier, "nameChampion1", inert), roster,
             rec=carrier, keys=["nameChampion1"])
    else:
        results.append((False, "promote the inert frozen raptor", "SKIP", "RED",
                        "record or carrier absent"))
    # 10: MUST STAY GREEN - a non-critical slot is not a freeze
    case("drop unarmedFidgetAnim1 (non-critical) - ROSTER gate",
         lambda: db.set_field(DAGON, "unarmedFidgetAnim1", ""), roster,
         expect_red=False)
    # 11: MUST STAY GREEN - the base-game control. skeletaltyphon ships a DEAD
    #     animation table in VANILLA and animates fine because its record completes
    #     the stance. If this ever reds, the gate is flagging the base game.
    typhon = r"records\xpack\creatures\monster\bosses\04_skeletaltyphon\skeletaltyphon.dbr"
    if db.has_record(typhon):
        tf = db.get_fields(typhon)
        state = "dead table + complete record surface: %s" % ", ".join(
            _complete_stances(_clips(tf)))
        case("base-game skeletaltyphon untouched (%s) - ROSTER gate" % state,
             lambda: None, roster, expect_red=False, rec=typhon,
             keys=["charAnimationTableName"])
    else:
        results.append((False, "skeletaltyphon control", "SKIP", "GREEN", "absent"))
    # 12: MUST STAY GREEN - an authored-immobile monster on a table that RESOLVES.
    #     A rooted quilvine binds no run/walk on purpose; only a chain that resolves
    #     from NOTHING is a defect.
    vine = r"records\creature\monster\quilvine\am_quillvine_17.dbr"
    if db.has_record(vine):
        case("rooted quilvine (authored immobility, table RESOLVES) - ROSTER gate",
             lambda: None, roster, expect_red=False, rec=vine,
             keys=["charAnimationTableName"])

    print("\n=== dagon_anim_rig NEGATIVE TESTS ===")
    bad = 0
    for ok, label, got, want, msg in results:
        print("  [%s] %-78s got=%-5s want=%s" % ("PASS" if ok else "FAIL",
                                                 label, got, want))
        if msg:
            print("         %s" % msg[:160])
        bad += 0 if ok else 1

    try:
        verify(db, {})
        print("\n  post-restore verify: GREEN (no case leaked)")
    except SystemExit as e:
        print("\n  post-restore verify: RED - A CASE LEAKED\n%s" % e)
        bad += 1
    print("\n%s (%d/%d)" % ("ALL NEGATIVE TESTS PASS" if not bad
                            else "NEGTEST FAILURES", len(results) - bad, len(results)))
    return 1 if bad else 0




if __name__ == "__main__":
    if "--negtest" in sys.argv:
        args = [a for a in sys.argv[1:] if not a.startswith("--")]
        if not args:
            print("usage: py tools/patches/dagon_anim_rig.py --negtest <arz>")
            raise SystemExit(2)
        raise SystemExit(_negtest(args[0]))
    print(__doc__)
