r"""dagon_anim_rig - unfreeze Dagon, Lord of the Poisoned Deep, and gate what can be
gated of the freeze class he belongs to.

WHY THIS EXISTS (RCA: docs/reports/dagon_frozen_rca.md)
--------------------------------------------------------
Will (2026-08-11): "Dagon, lord of the poisoned deep is frozen like the maened thrown
object guys were". He named the failure class correctly: the freeze lives on the
ANIMATION surface, exactly as it did for the thrown-wielders in R-100 #15
(02f1807 / 83d9fc2 / adfda67), and it survives a correct fix to the equipment/kit
surface. `thrown_restore` fixed the maenads' equipment and they stayed frozen; b52's
`_fix_dagon_kit` fixed Dagon's dead skills and he stayed frozen. Same shape, twice.

THE CAUSE: A WRONG RIG WITH NO FALLBACK (measured on the shipped build83 `44499f56`,
the base `database.arz`, `upstream/soulvizier_098i/Database/database.arz`, and the
`.msh`/`.anm` binaries in the base game's `Resources\*.arc`).

    records\test\boss_dagon_66.dbr
        mesh                   = Creatures\Monster\Ichthian\IchthianMage01.msh
        charAnimationTableName = records\creature\monster\d2custom\anm\anm_dagon.dbr

    RECORD : binds 13 `.anm` clips, every one a `Creatures\Monster\HYDRA\ANM\*` clip,
             on a creature whose mesh is IchthianMage01. Measured in the assets: the
             Hydra clips drive a 101-bone hydra rig (Bone_MainNeck01..08,
             Bone_L_BkNeck*, Bone_L_Claw*, three sets of head/jaw bones). The
             IchthianMage01 mesh has 30 bones and NONE of that hierarchy: 8 of the
             101 clip bones exist on this mesh (8%). His own rig's clips, by
             comparison, land 22 of 30 (73%). Corroborated in the DB: 54 base-game
             records carry this mesh and drive it with ichthian / jackalman / satyr /
             neanderthal / boarman / eurynomus clips. NOT ONE base record pairs a
             Hydra clip with it, and Dagon is the ONLY record in build83 that does.
    TABLE  : the one surface that could have supplied rig-correct clips instead
             resolves in NEITHER the mod arz NOR the base game arz. There are ZERO
             `d2custom` records in either database. It contributes 0 clips.
    ==>      Every animation he can reach is authored for a skeleton he does not have,
             and there is no second surface to fall back to. He stands.

WHAT IS *NOT* THE CAUSE, AND HOW WE KNOW. `unarmedWalkAnim` is unbound on both his
surfaces, which looks like the R-100 #15 condition and was this lane's first (wrong)
verdict. His own donor refutes it: `records\creature\monster\questbosses\
boss_hydra_66.dbr` is the record he was copied from (977 of their 1,043 shared fields
hold identical values; the 13 clips match BY SLOT AND BY VALUE), and that record names
NO animation table at all, binds NO walk clip in any stance, and animates perfectly in
the shipping game. Missing-walk plus dead-table is therefore not sufficient to freeze
anything. The ONE thing SV changed when it made Dagon out of the Hydra was the MESH.

NOT OURS. SV 0.98i's own database ships the identical dead table and the identical 13
Hydra clips on the identical Ichthian mesh, and `d2custom\anm\anm_dagon.dbr` is absent
from SV's OWN database too. It is the same never-shipped Diablo-namespace that made his
SKILLS dead references in b52. The record is a frankenstein: an Ichthian mesh, a Hydra
animation set, a Harpy `ActorName`, and a `d2custom` table.

WHAT THIS MODULE DOES
---------------------
(1) Repoints `charAnimationTableName` onto `records\creature\monster\ichthian\anm\
    anm_ichthian.dbr` - the table 43 of his 44 same-mesh siblings already use. It
    resolves, it is a clean `CharAnimationTable.tpl` (NOT the `Monster.tpl` corruption
    SV inflicted on ANM_Maenad), and it binds 71 clips including all 12 unarmed slots.
    NO CLONE IS NEEDED and NO SHARED RECORD IS EDITED: unlike the maenad fix, which had
    to MODIFY its tables and therefore had to clone them under the SHARED-RECORD LAW,
    this fix only POINTS AT the table. The 43 existing carriers are untouched.

(2) Rebuilds the unarmed stance ON BOTH SURFACES (the `adfda67` law: write identical
    values to the record and the table, so whichever surface the engine reads it gets
    the same animation). Every one of the 13 cross-rig Hydra clips is replaced by an
    IN-RIG clip, and the unbound slots (including `unarmedWalkAnim`) are added.

(3) Gives his three NAMED specials an animation. The engine matches a skill's
    `skillSpecialAnimationName` to a `<stance>SpecialAnimRef<N>` on the creature and
    plays the paired `<stance>SpecialAnim<N>`. His four ref slots were Hydra leftovers
    (IceBreath / FireBreath / PoisonBreath / SuperBite) of which only SuperBite matches
    his kit, so TIDAL STRIKE - his signature move and a WILL_DECISIONS item - had no
    animation of its own. The refs now name what his kit actually casts.

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

THE GATE (`verify`), AND EXACTLY WHAT IT DOES AND DOES NOT COVER
---------------------------------------------------------------
TARGETED (always hard, one record, encodes the mechanism above): Dagon's table must
resolve; all 17 unarmed slots must be bound on the record and agree with the table
wherever the table binds the same slot; EVERY clip he binds must come from a family the
SHIPPING GAME ITSELF drives an IchthianMage01 with (a 54-record base-game census, in
which Hydra never appears); each named special in his kit must own a ref slot; and his
b52 identity (name tag + Tidal Strike primary) must survive.

DB-WIDE (the roster clause): a Class=Monster record with a mesh that NAMES a
`charAnimationTableName` resolving in NEITHER the mod overlay NOR the base game arz
must complete RunAnim + WalkAnim + AttackAnim1 for at least one stance ON ITS OWN
RECORD. HARD when the violator is spawn-referenced, WARN when it is inert, and the
whole clause degrades to WARN when no base install is found (the `validate_tags`
precedent: a missing base game never blocks a build).

  THAT ROSTER CLAUSE CLOSES THE DANGLING-TABLE HALF OF THE CLASS, NOT THE CROSS-RIG
  HALF. It is what caught Dagon from the outside, and it would have caught him at the
  moment SV wrote the dead table. It would NOT catch a monster whose table resolves
  while its record overrides the critical slots with clips for the wrong skeleton, and
  no cheap DB-wide invariant does: three candidate generalisations were implemented and
  MEASURED against build83, and every one cries wolf (bone-overlap thresholds put
  proven base-game pairs as low as 10%, cross-family clip use spans 4,406 pairs, and
  "a family the base game never pairs with this mesh" fires 322 times on inherited SV
  records that ship and play). The blind spot is registered in docs/BACKLOG.md as
  BL-DAGON-CROSSRIG-DEBT-1 with those numbers, and the offline sweep that produced them
  is the way to check it. Per-record, the targeted clause above IS the cross-rig gate,
  and it is the pattern to copy onto the next custom monster.

The base-game boss `skeletaltyphon` is the control that keeps the roster clause honest:
it ships a DEAD animation table in VANILLA and animates fine, because its record binds
all three critical slots itself (with GiantTurtle clips, on a mesh the shipping game
proves that rig for). A naive "dead table = fail" gate would red the base game; the
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

# THE RIG ALLOWLIST. Measured, not assumed: 54 base-game Class=Monster records carry
# `IchthianMage01.msh`, and between their own clips and the tables they name they drive
# it with exactly these six clip families. The shipping game is the proof that each one
# animates this skeleton. `hydra` is NOT among them, and Dagon was the only record in
# build83 that paired a Hydra clip with this mesh. The gate refuses any family outside
# this set on his record, which is the mechanism itself rather than a blacklist of the
# one family SV happened to leave behind.
PROVEN_CLIP_FAMILIES = ("ichthian", "jackalman", "satyr", "neanderthal",
                        "boarman", "eurynomus")

_ICH = "Creatures\\Monster\\Ichthian\\ANM\\"
_JACKAL = "Creatures\\Monster\\JackalMan\\ANM\\"

# The full unarmed stance, written on the RECORD surface. Measured against the table:
# TWELVE of these seventeen are the BYTE-IDENTICAL value `anm_ichthian` binds for the
# same slot (so the two surfaces agree, per adfda67), ZERO differ from it, and the
# remaining FIVE are slots the table does not bind at all - `unarmedDieAnim1`,
# `unarmedLongIdleAnim` and `unarmedSpecialAnim2/3/4`. Those five are drawn from clips
# the table DOES bind elsewhere for this rig, so every value here is proven in-rig and
# proven present as an asset.
UNARMED = {
    # --- the three CRITICAL slots: without these he is a statue -------------
    "unarmedWalkAnim":         _ICH + "Ichthian_Walk.anm",       # was unbound
    "unarmedRunAnim":          _ICH + "Ichthian_Run.anm",        # was a HYDRA clip
    "unarmedAttackAnim1":      _ICH + "IchthianMage_Staff_AttAlpha.anm",   # was HYDRA
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
    # (anm_ichthian itself binds JackalMan clips for the whole dHanded stance, and the
    # base game drives this mesh with JackalMan clips on 54 records).
    "unarmedDieAnim1":         _JACKAL + "JackalMan_DieAlpha.anm",
    # --- the four NAME-KEYED special slots (see UNARMED_SPECIAL_REFS) -------
    "unarmedSpecialAnim1":     _ICH + "IchthianMage_Staff_AttBeta.anm",
    # what `anm_ichthian` itself pairs with the name TidalStrike (spearSpecialAnim1)
    "unarmedSpecialAnim2":     _ICH + "IchthianMage_Staff_Skill_BuffOther.anm",
    "unarmedSpecialAnim3":     _ICH + "IchthianMage_Staff_Skill_CastProjectile.anm",
    "unarmedSpecialAnim4":     _ICH + "IchthianMage_Staff_AttGamma.anm",
    "unarmedLongIdleAnim":     _ICH + "Ichthian_Emote_AllAlpha.anm",
}

# The NAME-KEYED half of the special slots. The engine plays a skill's animation by
# matching the skill record's `skillSpecialAnimationName` against these refs and playing
# the paired `unarmedSpecialAnim<N>`; an unmatched name silently falls through to the
# generic attack animation (measured: 1,202 of the base game's 2,048 monsters whose kit
# demands a named animation leave at least one demand unanswered on BOTH surfaces, so
# this degrades gracefully and is never a freeze).
# Dagon's four refs were Hydra leftovers - IceBreath / FireBreath / PoisonBreath /
# SuperBite - and his kit demands TidalStrike, SuperBite and PoisonBomb, so only
# SuperBite matched and his SIGNATURE MOVE had no animation of its own.
#   ref1 keeps the table's own value so record and table agree on slot 1 (adfda67); it
#   is inert for his kit because he has no SkonerosBolt.
UNARMED_SPECIAL_REFS = {
    "unarmedSpecialAnimRef1": "SkonerosBolt",
    "unarmedSpecialAnimRef2": "TidalStrike",
    "unarmedSpecialAnimRef3": "PoisonBomb",
    "unarmedSpecialAnimRef4": "SuperBite",
}

# His kit's skill records, read at gate time so the invariant follows the KIT rather
# than a hardcoded list: whatever `skillSpecialAnimationName` those records name is
# checked against the four ref slots above.
KIT_SKILL_FIELDS = ("specialAttackSkillName",) + tuple(
    "skillName%d" % i for i in range(1, 13))

# The names his b52 kit demanded when this module was written (measured 2026-08-11:
# ichthian_tidalstrike -> TidalStrike, hydra_superbite -> SuperBite,
# nehebkau_poisongasbomb -> PoisonBomb; tidalorb and venomnova name none). Losing an
# animation for one of THESE is the regression this module exists to prevent, so it is
# HARD. A name that appears later, because another lane changed his kit, is a WARN: it
# is worth knowing and it is not worth blocking a build over, since an unanswered name
# degrades to the generic attack animation rather than freezing anything.
KIT_NAMED_SPECIALS = ("TidalStrike", "SuperBite", "PoisonBomb")

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


def _fam(path):
    r"""The creature folder a mesh or clip belongs to.

    `Creatures\Monster\Ichthian\ANM\Ichthian_Run.anm` -> `ichthian`
    `Creatures\Monster\Ichthian\IchthianMage01.msh`   -> `ichthian`
    """
    parts = [p for p in _norm(path).split("\\") if p and p != "anm"]
    return parts[-2] if len(parts) >= 2 else "?"


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


def _base_db():
    """The loaded base-game ArzDatabase, or None if it is unavailable.

    Cached: verify() may run more than once in a session and the base arz is 74k
    records. A load failure is never fatal - every clause that uses it degrades to
    WARN, per the validate_tags precedent.
    """
    if "db" in _BASE_CACHE:
        return _BASE_CACHE["db"]
    bdb = None
    p = discover_base_arz()
    if p is not None:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
            from arz_patcher import ArzDatabase  # noqa: E402
            bdb = ArzDatabase.from_arz(p)
        except Exception:
            bdb = None
    _BASE_CACHE["db"] = bdb
    return bdb


def _base_record_names():
    """Lowercased record-name set of the base game arz, or None if unavailable."""
    if "names" in _BASE_CACHE:
        return _BASE_CACHE["names"]
    bdb = _base_db()
    names = None if bdb is None else {_norm(n) for n in bdb.record_names()}
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

    SCOPE, STATED PLAINLY. This is the DANGLING-REFERENCE half of the freeze class.
    It catches the record that names an animation table nothing can load and has no
    self-contained stance to fall back on, which is how Dagon got here and is exactly
    the condition SV created when it wrote `d2custom\anm\anm_dagon`. It does NOT
    catch a monster whose table resolves while its record overrides the critical
    slots with clips authored for another skeleton: record clips win per field, so
    that record passes here and stands still in game. The cross-rig half is gated
    PER RECORD in `_verify_dagon` (a mesh-specific allowlist measured from the base
    game) and is registered DB-wide as BL-DAGON-CROSSRIG-DEBT-1, with the three
    measured reasons no cheap DB-wide form of it survives contact with build83.

    It scans `db.record_names()`, i.e. the MOD OVERLAY, which is the right scope for
    a build gate: it is what this build ships. (For the record, the merged
    mod-plus-base view holds 7,112 Class=Monster records carrying a mesh and 8
    dead-table namers; the extra one is base-only `...\test\soundtest\testsubject3`,
    which completes four stances on its own record and is not a violation. The
    violation set is identical either way.)

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

    # Which of the (very few) violators are actually reachable in game?
    #
    # COST, MEASURED (not guessed - an earlier note in this spot blamed this scan for
    # 47s and was WRONG): asking "does any OTHER record name this path" touches every
    # value of every record, ~51k records. On the shipped build83 the WHOLE sweep,
    # this scan included, costs 3.0s once the records are decoded - and the real build
    # has already decoded all of them (apply_svc_patches' _RecordIndex.sync_blobs does
    # one full pass), exactly as thrown_anim_rig records for its own sweep. The 47s a
    # standalone run appears to spend here is the one-time DECODE of 51k records,
    # which the build pays with or without this gate.
    # It still runs ONLY when there is a violation, reads `tf.values` directly rather
    # than the `.value` property, and stops as soon as every violator is proven
    # reachable.
    spawn_referenced = set()
    if violations:
        targets = {_norm(v[0]) for v in violations}
        for name in db.record_names():
            fields = db.get_fields(name)
            if not fields:
                continue
            self_n = _norm(name)
            for tf in fields.values():
                for vv in tf.values:
                    # `vv[-1:] in "rR"` is a one-index reject for the ~99.9% of
                    # values that cannot be a .dbr path, and it is case-blind, so
                    # no `.DBR` spelling can slip past the fast path.
                    if type(vv) is str and vv[-1:] in ("r", "R"):
                        n = _norm(vv)
                        if n in targets and n != self_n:
                            spawn_referenced.add(n)
            if len(spawn_referenced) == len(targets):
                break   # every violator already proven reachable
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

    # (3) the name-keyed half of the special slots, so his kit's named skills reach a
    #     clip instead of falling through to the generic attack animation.
    for slot, ref in UNARMED_SPECIAL_REFS.items():
        db.set_field(DAGON, slot, ref)


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

    # THE MECHANISM ITSELF, checked FIRST so a real regression is reported as what it
    # is: no clip from a family the shipping game does not drive this mesh with may
    # survive on the record. This is what actually froze him - Hydra clips on an
    # Ichthian skeleton - and it is stated as an allowlist so ANY wrong rig trips it,
    # not just the one family SV left behind.
    strays = {k: v for k, v in on_record.items()
              if _fam(v) not in PROVEN_CLIP_FAMILIES}
    if strays:
        raise SystemExit(
            "dagon_anim_rig GATE: %d clip(s) on Dagon come from a rig the shipping game "
            "never drives an IchthianMage01 mesh with: %s. Proven families for this mesh "
            "(54 base-game carriers): %s. A clip authored for another skeleton cannot "
            "animate this one - that is the defect this module exists to remove."
            % (len(strays),
               ", ".join("%s=%s [%s]" % (k, v, _fam(v))
                         for k, v in sorted(strays.items())),
               ", ".join(PROVEN_CLIP_FAMILIES)))

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

    # every named special in his KIT must own a ref slot, or it plays no animation of
    # its own. Read from the skill records so the invariant follows the kit.
    _verify_special_refs(db, fields, on_record)

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


def _verify_special_refs(db, fields, on_record):
    """Every NAMED special in Dagon's kit must own a ref slot with a bound clip.

    This is the "resolves an animation for every attack type it can perform" half of
    the invariant, at the only granularity the engine actually offers: the skill record
    names a `skillSpecialAnimationName`, the creature answers with
    `unarmedSpecialAnimRef<N>`, and the paired `unarmedSpecialAnim<N>` is what plays.
    An unmatched name is not a freeze (1,202 base-game monsters carry one), but on THIS
    record it silently cost Tidal Strike its animation, so here it is a hard failure.
    """
    for slot, want in UNARMED_SPECIAL_REFS.items():
        got = _fv(fields, slot)
        if str(got or "") != want:
            raise SystemExit(
                "dagon_anim_rig GATE: Dagon's %s = %r, expected %r. The four ref slots "
                "are how the engine finds a skill's animation; the shipped values were "
                "Hydra leftovers (IceBreath / FireBreath / PoisonBreath / SuperBite)."
                % (slot, got, want))

    bound_refs = {}
    for slot, ref in UNARMED_SPECIAL_REFS.items():
        anim_slot = slot.replace("Ref", "")
        if _is_anm(on_record.get(anim_slot)):
            bound_refs[ref] = anim_slot

    bdb = _base_db()
    # `has_record` is case-SENSITIVE and record paths are spelled inconsistently across
    # the database, so resolve case-insensitively or this clause invents dead
    # references that are not dead.
    ci_mod = {_norm(n): n for n in db.record_names()}
    ci_base = {} if bdb is None else {_norm(n): n for n in bdb.record_names()}

    def _skill_fields(path):
        key = _norm(path)
        if key in ci_mod:
            return db.get_fields(ci_mod[key])
        if key in ci_base:
            return bdb.get_fields(ci_base[key])
        return None

    unresolved, demanded = [], {}
    for f in KIT_SKILL_FIELDS:
        skill = _fv(fields, f)
        if not skill or not str(skill).strip():
            continue
        sf = _skill_fields(skill)
        if sf is None:
            unresolved.append((f, skill))
            continue
        name = _fv(sf, "skillSpecialAnimationName")
        if name and str(name).strip():
            demanded.setdefault(str(name).strip(), []).append(f)

    missing = sorted(n for n in demanded if n not in bound_refs)
    hard = [n for n in missing if n in KIT_NAMED_SPECIALS]
    soft = [n for n in missing if n not in KIT_NAMED_SPECIALS]
    if hard:
        raise SystemExit(
            "dagon_anim_rig GATE: %d named special(s) from Dagon's b52 kit have no ref "
            "slot, so they play no animation of their own: %s. His refs are %s. Bind the "
            "name in an unarmedSpecialAnimRef<N> whose unarmedSpecialAnim<N> is an in-rig "
            "clip." % (len(hard),
                       ", ".join("%s (from %s)" % (n, ", ".join(demanded[n]))
                                 for n in hard),
                       ", ".join("%s=%s" % (s, r)
                                 for s, r in sorted(UNARMED_SPECIAL_REFS.items()))))
    if soft:
        print("  dagon_anim_rig GATE: WARN - Dagon's kit has grown %d named special(s) "
              "this module did not wire an animation for: %s. They fall through to the "
              "generic attack animation, which is cosmetic and never a freeze, so this "
              "does not block. Whoever added them should take a ref slot."
              % (len(soft), ", ".join("%s (from %s)" % (n, ", ".join(demanded[n]))
                                      for n in soft)))

    if unresolved:
        print("  dagon_anim_rig GATE: WARN - %d skill slot(s) on Dagon name a record "
              "that resolves in NEITHER the mod overlay NOR the base game%s, so their "
              "animation names could not be read: %s. These are PRE-EXISTING SV 0.98i "
              "residue of the same never-shipped D2 namespace b52 cleaned out of his "
              "primary kit, they are inert, and they are filed as BL-DAGON-DEADSKILLS-1. "
              "A NEW name in this list is a regression."
              % (len(unresolved),
                 "" if bdb is not None else " (base arz not found, so this list is "
                 "unproven)",
                 ", ".join("%s=%s" % (f, s) for f, s in unresolved)))


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
          "slots, every clip from a rig the base game proves for his mesh, %d named "
          "specials bound, table=%s); and DB-wide no spawn-referenced monster names an "
          "animation table that resolves from nothing (%d inert violator(s) warned). "
          "That DB-wide clause covers the dangling-table half of the freeze class only "
          "- see BL-DAGON-CROSSRIG-DEBT-1."
          % (len(UNARMED), len(UNARMED_SPECIAL_REFS), ICHTHIAN_TABLE, len(warn)))


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

    KEYS = ["charAnimationTableName"] + list(UNARMED) + list(UNARMED_SPECIAL_REFS)

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
    # 5: a cross-rig clip survives on the ichthian mesh - THE MECHANISM, re-planted
    case("leave a Hydra clip on the Ichthian-mesh record (THE WRONG RIG)",
         lambda: db.set_field(DAGON, "unarmedRunAnim",
                              r"Creatures\Monster\Hydra\ANM\Hydra_Run.anm"), verify)
    # 5b: and it is an ALLOWLIST, not a blacklist of Hydra. Medusa clips are proven on
    #     medusa01.msh by the base game and are still wrong for this skeleton.
    case("bind a Medusa clip (a family proven on ANOTHER mesh) - allowlist, not "
         "a hydra blacklist",
         lambda: db.set_field(DAGON, "unarmedWalkAnim",
                              r"Creatures\Monster\Medusa\ANM\Medusa_Walk.anm"), verify)
    # 5c: the ref slots must hold the values this module declares
    case("revert a ref slot to its Hydra leftover (IceBreath)",
         lambda: db.set_field(DAGON, "unarmedSpecialAnimRef2", "IceBreath"), verify)
    # 5d: THE KIT CLAUSE, exercised on its own. Both the module's declaration and the
    #     record are moved together to a name his kit does not cast, so the exact-value
    #     check passes and only the kit-derived clause can fire. This is the state the
    #     record SHIPPED in: a ref set that answers no skill he owns.
    _keep = UNARMED_SPECIAL_REFS["unarmedSpecialAnimRef2"]
    try:
        UNARMED_SPECIAL_REFS["unarmedSpecialAnimRef2"] = "IceBreath"
        case("no ref answers TidalStrike (SIGNATURE MOVE unanimated - the shipped "
             "state of the ref slots)",
             lambda: db.set_field(DAGON, "unarmedSpecialAnimRef2", "IceBreath"), verify)
    finally:
        UNARMED_SPECIAL_REFS["unarmedSpecialAnimRef2"] = _keep
        db.set_field(DAGON, "unarmedSpecialAnimRef2", _keep)
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
