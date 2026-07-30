r"""tools/patches/thrown_anim_rig.py - THE R-100 #15 FREEZE FIX: give every
restored thrown-wielder an animation rig that actually binds the thrown stance.

WILL, VERBATIM (R-100 #15, the most serious item in his play-session batch):

    "all of the guys that we brought back into the game which utilize thrown
    objects are all frozen in the game, they spawn and they cant move or attack
    or anything they are broken"

=============================================================================
ROOT CAUSE - MEASURED, not inferred, and it is NOT the equipment
=============================================================================
`tools/patches/thrown_restore.py` (b64) restored the base-game EQUIP/LOOT fields
on 10 creature records our own SV overlay had disarmed. That half is correct and
is untouched here. What nobody checked - across b58, b64 and every task that
claimed this rig was "proven on 3 families and re-verified" - is the ANIMATION
side, and that is where the freeze lives.

A TQ creature plays one animation block per WEAPON CLASS. Equipping a
`WeaponHunting_RangedOneHand` (a thrown weapon) puts the creature in the
`rangedOneHand` stance (or `dualRanged` when BOTH hands are thrown). The `.anm`
clips for a stance come from the creature's ANIMATION TABLE
(`charAnimationTableName`, e.g. `Records\Creature\Monster\Maenad\ANM\
ANM_Maenad.dbr`).

The base game binds the thrown stance on all four tables our roster uses.
**SV 0.98i replaces those four table records WHOLESALE with pre-thrown-weapon
versions that bind ZERO thrown-stance clips**, and our build inherits SV's. So a
restored wielder equips a javelin, enters a stance with **no run anim, no walk
anim and no attack anim**, and becomes a statue. Exactly the report.

Measured with `py tools/debug/probe_anim_tables.py <base.arz> <sv098i.arz>` and
re-measured on the SHIPPED build `local/baseline_main.arz`
(md5 6a3a491db546b603c52132237c40aa63, 51,124 records) with
`py tools/debug/probe_anim_tables.py local/baseline_main.arz`:

    animation table            stance           base TQAE   SV 0.98i / OUR BUILD
    ANM_Maenad.dbr             rangedOneHand     9 clips           0 clips
    ANM_Tiger.dbr              rangedOneHand    10 clips           0 clips
    ANM_Machae.dbr             rangedOneHand    11 clips           0 clips
    ANM_DuneRaider.dbr         dualRanged        9 clips           0 clips

(The 92 numeric `rangedOneHand*AnimSpeed/Weight` fields survive in SV's copy -
they are template defaults. Weights with nothing to weight are not a rig. That
is precisely why the earlier "the anim block is present" check passed while the
monsters shipped frozen: `thrown_wielders.verify` tested
`rangedOneHandAttackAnimWeight1 is not None`, which is TRUE on a table that
binds no clip at all.)

=============================================================================
WHICH SURFACE THE ENGINE READS - settled from shipping data, not from belief
=============================================================================
Both surfaces exist (the creature record and the animation table), so this was
measured rather than assumed - `py tools/debug/probe_anim_authority.py
<base.arz>`, over all **5,561** base-game `Class=Monster` records:

  * 2,596 records bind a Run/Walk/Attack slot on the RECORD that their table
    does not  -> the record IS read.
  * 8,884 records bind one on the TABLE that their record does not -> the table
    IS read. (Per-field fallback: record overrides, table fills in.)
  * **For `rangedOneHand` and `dualRanged` specifically: 0 records bind them at
    record level, 1,085 + 259 get them from the table ONLY.** Not one shipping
    thrower in the entire game carries its thrown anims on its own record.

So the TABLE is the surface base itself uses for this stance, and it is the
primary target here. It is not, however, sufficient on its own for the maenad
family - see "BOTH SURFACES" below - so the identical clips are written to the
creature records as well.

=============================================================================
SHARED-RECORD LAW: these four tables are HEAVILY shared -> CLONE, never edit
=============================================================================
Carrier census on the shipped build
(`py tools/debug/probe_thrown_stance_gap.py <base.arz> local/baseline_main.arz
--carriers`):

    ANM_Maenad.dbr        168 carriers, 166 NON-TARGET (every maenad, plus
                          um_lyialeafsong_18 and friends - Will's own PETS)
    ANM_Tiger.dbr          68 carriers,  66 NON-TARGET
    ANM_Machae.dbr         64 carriers,  61 NON-TARGET
    ANM_DuneRaider.dbr     30 carriers,  27 NON-TARGET

That is the `toxeus_passiveproperties` lesson again (18 carriers, 9 of them
Will's pets). So this module NEVER edits a shared table: it CLONES each one to
`<original>_thrown.dbr` BESIDE the original, restores the base thrown-stance
clips ON THE CLONE, and repoints `charAnimationTableName` on exactly the 10
roster records. verify() proves the four originals still bind zero thrown clips
(i.e. were not edited) and that every non-target carrier still names the
original table.

Cloning from OUR table (not from base) deliberately preserves every SV change to
the other stances (e.g. SV's ANM_Maenad binds 26 bow clips where base binds 10);
only the missing thrown stance is added back, verbatim from base TQAE.

=============================================================================
SCOPE - every monster this touches, and the DB-wide invariant
=============================================================================
The roster is IMPORTED from `thrown_restore.ROSTER`, so the two modules can
never drift. All 10: maenad ar_archer_06/br_archer_10, tigerman ar_archer_27/33,
machae ar/br/cr_archer_37, duneraider am_assassin_15/21/27.

The gate is stated as a ROSTER INVARIANT over the whole database, not as 10
named exceptions (process law #4): no `Class=Monster` record may equip a thrown
weapon while BOTH its own record AND its animation table leave that weapon's
stance without RunAnim + WalkAnim + AttackAnim1. `scan_frozen_throwers()` is the
single implementation, used by verify(), by the negative tests and by
`tools/debug/probe_frozen_throwers.py`.

=============================================================================
WHY THE STANCE IS RESTORED ON *BOTH* SURFACES (belt AND braces, deliberately)
=============================================================================
A second, independent SV defect turned up while building this, and it is why
table-only would have been a gamble on the largest family:

    base TQAE : records\creature\monster\maenad\anm\anm_maenad.dbr
                templateName = database\Templates\CharAnimationTable.tpl
    SV 0.98i  : the SAME path, templateName = database\Templates\Monster.tpl,
                Class = Monster, mesh = Creatures\Monster\Maenad\Maenad02.msh,
                description = tagMonsterName082

SV overwrote maenad's ANIMATION TABLE with a full MONSTER record. (The other
three tables are untouched `CharAnimationTable.tpl` in both.) 168 records still
name that path as their animation table. If the engine type-checks what
`charAnimationTableName` resolves to, every maenad's table lookup is dead and
only its own record's clips are read - which fits what we see, since maenad
creature records DO carry their own bow/spear/staff/unarmed clips and maenads
animate fine, while the thrown stance (record-level: nothing, anywhere in the
game) is exactly the one that is frozen.

We cannot settle that from the database, and this bug has already shipped broken
twice, so the module restores the identical base clips on BOTH surfaces:
  * the CLONED animation table  - correct if the table is read (8,884 shipping
    records depend on the table being read);
  * the 10 CREATURE RECORDS     - correct if the table is ignored/rejected
    (2,596 shipping records depend on the record being read).
Both carry the same verbatim base values, so whichever surface the engine
consults it gets the same animation. The maenad template corruption itself is
NOT repaired here: that is a 168-carrier shared record and repointing every
maenad in the game is a different, much larger lane. Reported as debt
(BL-R140-MAENAD-TPL-1).

Contract (tools/patches/README.md): MODULE_NAME + apply(db, tags) + verify.
"""

MODULE_NAME = ("Thrown-wielder ANIMATION RIG (R-100 #15): restore the thrown "
               "stance SV stripped, on cloned anim tables AND the creatures")

# Sibling module. The roster is IMPORTED (never re-listed) so this module and
# thrown_restore can never drift apart. Dual import because there are two live
# entry paths: the registry loads us as `patches.thrown_anim_rig` (package
# context -> relative import), while `py tools/patches/thrown_anim_rig.py` and
# tools/debug/probe_frozen_throwers.py load us as a top-level module with
# tools/patches on sys.path (no package -> plain import).
try:                                        # registry / package context
    from . import thrown_restore           # noqa: E402
except ImportError:                         # stand-alone script context
    import os as _os
    import sys as _sys
    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    import thrown_restore                   # noqa: E402


# ---------------------------------------------------------------------------
# The clip slots that decide whether a creature can MOVE and ATTACK in a stance.
# A stance missing any of these is a statue.
# ---------------------------------------------------------------------------
CRITICAL_SLOTS = ("RunAnim", "WalkAnim", "AttackAnim1")

# Each clone sits BESIDE the table it clones, as `<original>_thrown.dbr`.
# Deliberately NOT a fresh `records\creature\monster\svc\...` namespace: SV's
# ANM_Maenad is a `Monster.tpl` record (see the docstring), so a clone of it is a
# Class=Monster record, and dropping one of those into a new SVC namespace would
# make it look like a spawnable monster to any path-scoped gate or future reader.
# Beside the original, every clone is exactly as visible - and as classified - as
# the record it came from. The paths are new and unique, so no record is
# displaced and no other module writes them.
def _beside(table_path, suffix="_thrown"):
    assert table_path.endswith(".dbr")
    return table_path[:-len(".dbr")] + suffix + ".dbr"


def _norm(s):
    return str(s).replace("/", "\\").lower()


def _scalar(v):
    return v[0] if isinstance(v, list) and v else v


def _fv(fields, key):
    r"""Scalar value of `key` in a decoded field map, or None.

    PERFORMANCE (this matters: verify() sweeps all ~51k records): the obvious
    `db.get_field_value(rec, key)` falls back to a LINEAR scan of the record's
    ~1000 fields whenever the key is ABSENT, which is the common case in a
    full-DB sweep. Reading the decoded map directly, with the same `###`
    suffix fallback `get_field_value` uses, keeps the sweep to dict lookups.
    In the real build every record is already decoded (apply_svc_patches'
    `_RecordIndex.sync_blobs` does one full pass), so the sweep adds no decode
    cost at all.
    """
    if not fields:
        return None
    tf = fields.get(key)
    if tf is None:
        for k, v in fields.items():
            if "###" in k and k.split("###")[0] == key:
                tf = v
                break
    return _scalar(tf.value) if tf is not None else None


# ---------------------------------------------------------------------------
# THE RESTORE DATA. Every value below is captured VERBATIM (path, spelling and
# letter case) from base TQAE `database.arz`, dumped by
#   py tools/debug/probe_thrown_stance_gap.py <base.arz> <mod.arz> --dump-block
# Nothing here is invented: these are the clips the shipping game itself plays
# when one of these creatures throws. Case is preserved exactly as base stores
# it (base is itself inconsistent - e.g. lowercase `maenad_unarmed_attalpha.anm`
# next to CamelCase `Maenad_UnArmed_DieAlpha.anm`); asset lookup is
# case-insensitive, and copying verbatim keeps the diff honest.
# ---------------------------------------------------------------------------
FAMILIES = [
    {
        "key": "maenad",
        "table": r"records\creature\monster\maenad\anm\anm_maenad.dbr",
        "clone": _beside(r"records\creature\monster\maenad\anm\anm_maenad.dbr"),
        "stance": "rangedOneHand",
        "clips": {
            "rangedOneHandAttackAnim1":     r"Creatures\monster\maenad\anm\maenad_unarmed_attalpha.anm",
            "rangedOneHandAttackIdleAnim":  r"Creatures\monster\maenad\anm\maenad_unarmed_attidle.anm",
            "rangedOneHandBuffOtherAnim1":  r"Creatures\monster\maenad\anm\maenad_unarmed_attgamma.anm",
            "rangedOneHandBuffSelfAnim1":   r"Creatures\monster\maenad\anm\maenad_unarmed_attgamma.anm",
            "rangedOneHandDieAnim1":        r"Creatures\Monster\Maenad\ANM\Maenad_UnArmed_DieAlpha.anm",
            "rangedOneHandRunAnim":         r"Creatures\Monster\Maenad\ANM\Maenad_OneHand_Run.anm",
            "rangedOneHandSpellAttackAnim": r"Creatures\monster\maenad\anm\maenad_unarmed_attalpha.anm",
            "rangedOneHandStunAnim":        r"Creatures\Monster\Maenad\ANM\Maenad_UnArmed_Stun.anm",
            "rangedOneHandWalkAnim":        r"Creatures\Monster\Maenad\ANM\Maenad_Walk.anm",
        },
    },
    {
        "key": "tigerman",
        "table": r"records\creature\monster\tigerman\anm\anm_tiger.dbr",
        "clone": _beside(r"records\creature\monster\tigerman\anm\anm_tiger.dbr"),
        "stance": "rangedOneHand",
        "clips": {
            "rangedOneHandAttackAnim1":     r"Creatures\monster\tigerman\anm\tigerman_dw_attbeta.anm",
            "rangedOneHandAttackAnim2":     r"Creatures\monster\tigerman\anm\tigerman_onehand_attgamma.anm",
            "rangedOneHandAttackIdleAnim":  r"Creatures\Monster\TigerMan\ANM\TigerMan_DW_AttIdle.anm",
            "rangedOneHandBuffOtherAnim1":  r"Creatures\monster\tigerman\anm\tigerman_dw_attbeta.anm",
            "rangedOneHandBuffSelfAnim1":   r"Creatures\monster\tigerman\anm\tigerman_dw_attbeta.anm",
            "rangedOneHandDieAnim1":        r"Creatures\Monster\BoarMan\ANM\BoarMan02_DieAlpha.anm",
            "rangedOneHandRunAnim":         r"Creatures\Monster\TigerMan\ANM\TigerMan_Run.anm",
            "rangedOneHandSpellAttackAnim": r"Creatures\monster\tigerman\anm\tigerman_dw_attbeta.anm",
            "rangedOneHandStunAnim":        r"Creatures\Monster\TigerMan\ANM\TigerMan_Stun.anm",
            "rangedOneHandWalkAnim":        r"Creatures\Monster\TigerMan\ANM\TigerMan_Walk.anm",
        },
    },
    {
        "key": "machae",
        "table": r"records\xpack\creatures\monster\machae\anm\anm_machae.dbr",
        "clone": _beside(r"records\xpack\creatures\monster\machae\anm\anm_machae.dbr"),
        "stance": "rangedOneHand",
        "clips": {
            "rangedOneHandAlertAnim1":      r"XPack\Creatures\Monster\Machae\ANM\Machae_OneHand_Alert.anm",
            "rangedOneHandAttackAnim1":     r"XPack\Creatures\Monster\Machae\ANM\Machae_OneHand_AttAlpha.anm",
            "rangedOneHandAttackAnim2":     r"XPack\Creatures\Monster\Machae\ANM\Machae_OneHand_AttBeta.anm",
            "rangedOneHandAttackAnim3":     r"XPack\Creatures\Monster\Machae\ANM\Machae_Spear_AttAlpha.anm",
            "rangedOneHandAttackIdleAnim":  r"XPack\Creatures\Monster\Machae\ANM\Machae_OneHand_AttIdle.anm",
            "rangedOneHandBuffOtherAnim1":  r"XPack\Creatures\Monster\Machae\ANM\Machae_OneHand_AttGamma.anm",
            "rangedOneHandBuffSelfAnim1":   r"XPack\Creatures\Monster\Machae\ANM\Machae_OneHand_AttAlpha.anm",
            "rangedOneHandRunAnim":         r"XPack\Creatures\Monster\Machae\ANM\Machae_OneHand_Run.anm",
            "rangedOneHandSpellAttackAnim": r"XPack\Creatures\Monster\Machae\ANM\Machae_OneHand_AttGamma.anm",
            "rangedOneHandStunAnim":        r"XPack\Creatures\Monster\Machae\ANM\Machae_OneHand_Stun.anm",
            "rangedOneHandWalkAnim":        r"XPack\Creatures\Monster\Machae\ANM\Machae_OneHand_Walk.anm",
        },
    },
    {
        "key": "duneraider",
        "table": r"records\creature\monster\duneraider\anm\anm_duneraider.dbr",
        "clone": _beside(r"records\creature\monster\duneraider\anm\anm_duneraider.dbr"),
        "stance": "dualRanged",
        "clips": {
            "dualRangedAttackAnim1":    r"Creatures\Monster\DuneRaider\ANM\DuneRaider_DW_AttBeta.anm",
            "dualRangedAttackAnim2":    r"Creatures\monster\duneraider\anm\duneraider_onehand_attbeta.anm",
            "dualRangedAttackAnim3":    r"Creatures\monster\duneraider\anm\duneraider_onehand_attgamma.anm",
            "dualRangedAttackIdleAnim": r"Creatures\Monster\DuneRaider\ANM\DuneRaider_Idle.anm",
            "dualRangedBuffOtherAnim1": r"Creatures\monster\duneraider\anm\duneraider_onehand_attalpha.anm",
            "dualRangedBuffSelfAnim1":  r"Creatures\monster\duneraider\anm\duneraider_onehand_attalpha.anm",
            "dualRangedRunAnim":        r"Creatures\Monster\DuneRaider\ANM\DuneRaider_Run.anm",
            "dualRangedStunAnim":       r"Creatures\Monster\DuneRaider\ANM\DuneRaider_Stun.anm",
            "dualRangedWalkAnim":       r"Creatures\Monster\DuneRaider\ANM\DuneRaider_Walk.anm",
        },
    },
]


def _family_for(entry):
    """Which FAMILIES row owns a thrown_restore.ROSTER entry (by family key)."""
    for fam in FAMILIES:
        if fam["key"] == entry["family"]:
            return fam
    raise SystemExit(
        "thrown_anim_rig: thrown_restore.ROSTER carries family %r with no "
        "animation-rig entry. A new thrown family MUST bring its own stance "
        "restore - otherwise it ships frozen (R-100 #15)." % entry["family"])


def referenced_anms():
    """Every distinct .anm clip this module binds (asset-resolution probe)."""
    out = set()
    for fam in FAMILIES:
        out.update(fam["clips"].values())
    return out


def expected_stance(entry):
    """The stance a roster entry's weapon selects: both hands thrown ->
    dualRanged, otherwise rangedOneHand."""
    return "dualRanged" if entry["dual"] else "rangedOneHand"


# ---------------------------------------------------------------------------
# THE INVARIANT (single implementation, shared by verify/negtest/the probe)
# ---------------------------------------------------------------------------
def _is_thrown_loot(vals):
    """A loot slot resolves to a WeaponHunting_RangedOneHand.

    The thrown loot tables live under the Ragnarok `xpack2` namespace and are
    BASE-only records (pure pass-through, absent from the mod overlay), so a
    `has_record`/Class lookup alone cannot see them. This is the same
    ground-truth-verified path test `thrown_restore.verify` uses - the base
    thrown tables are exactly `...\\weapons\\{static,monster,unique}\\
    {1h_ranged_*,ni/ei/li_roh_*,roh_*}.dbr`.
    """
    vals = vals if isinstance(vals, list) else [vals]
    for v in vals:
        if not v:
            continue
        s = _norm(v)
        if "1h_ranged" in s or "\\roh_" in s or "_roh_" in s:
            return True
    return False


def _unbound_slots(fields, stance):
    """Which CRITICAL_SLOTS this decoded field map leaves without an .anm."""
    out = []
    for s in CRITICAL_SLOTS:
        v = _fv(fields, stance + s)
        if not (isinstance(v, str) and v.lower().endswith(".anm")):
            out.append(stance + s)
    return out


def scan_frozen_throwers(db):
    """(throwers, frozen) over the whole DB.

    throwers = [(record, stance, table)] for every Class=Monster that equips a
               thrown weapon at chance > 0.
    frozen   = [(record, stance, table, [unbound critical slots])] - the
               violators of the R-100 #15 invariant.

    A slot counts as bound if EITHER the creature record or its animation table
    supplies it: that is the real engine-level freeze condition (per-field
    fallback, measured over 5,561 base monsters), and stating it as the union is
    what lets the gate be true of the whole roster rather than of our 10 - every
    shipping base thrower binds this stance on the TABLE only, so a
    record-only test would flag the entire base game.
    """
    by_lower = {_norm(n): n for n in db.record_names()}
    tbl_cache = {}

    def table_binds(tbl, stance):
        """critical slots this table leaves UNBOUND for `stance` ([] == healthy)"""
        key = (_norm(tbl), stance)
        if key in tbl_cache:
            return tbl_cache[key]
        real = by_lower.get(_norm(tbl))
        if real is None:
            # Absent from the overlay -> pure base-game pass-through. The base
            # tables DO bind the thrown stance (measured: 9/10/11/9 clips), so a
            # pass-through table is healthy by construction.
            tbl_cache[key] = []
            return []
        missing = _unbound_slots(db.get_fields(real), stance)
        tbl_cache[key] = missing
        return missing

    throwers, frozen = [], []
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields or _fv(fields, "Class") != "Monster":
            continue
        right = float(_fv(fields, "chanceToEquipRightHand") or 0)
        left = float(_fv(fields, "chanceToEquipLeftHand") or 0)
        if right <= 0 and left <= 0:
            continue
        r_thrown = right > 0 and _is_thrown_loot(
            fields["lootRightHandItem1"].value if "lootRightHandItem1" in fields else None)
        l_thrown = left > 0 and _is_thrown_loot(
            fields["lootLeftHandItem1"].value if "lootLeftHandItem1" in fields else None)
        if not (r_thrown or l_thrown):
            continue
        stance = "dualRanged" if (r_thrown and l_thrown) else "rangedOneHand"
        tbl = _fv(fields, "charAnimationTableName")
        throwers.append((name, stance, tbl))
        # union of the two surfaces: a slot is unbound only if NEITHER supplies it
        on_record = set(_unbound_slots(fields, stance))
        if not tbl:
            if on_record:
                frozen.append((name, stance, None, sorted(on_record)))
            continue
        missing = on_record & set(table_binds(tbl, stance))
        if missing:
            frozen.append((name, stance, tbl, sorted(missing)))
    return throwers, frozen


# ---------------------------------------------------------------------------
def apply(db, tags):
    """Clone each family's animation table, restore the base thrown-stance
    clips on the CLONE, and repoint the roster records onto it.

    Never edits a shared table. Never touches equipment/loot/stats (that is
    thrown_restore's half). Adds exactly len(FAMILIES) records.
    """
    # case-insensitive resolver: clone_record keys off the exact stored name.
    real = {_norm(n): n for n in db.record_names()}

    for fam in FAMILIES:
        src = real.get(_norm(fam["table"]))
        if src is None:
            raise SystemExit(
                "thrown_anim_rig: animation table %s is absent from the "
                "overlay. It must exist (SV replaces it) for the clone-and-"
                "restore to run. See the module docstring." % fam["table"])
        if db.has_record(fam["clone"]):
            raise SystemExit(
                "thrown_anim_rig: clone target %s already exists - another "
                "module owns that path. Refusing to overwrite." % fam["clone"])
        db.clone_record(src, fam["clone"])
        # Restore the thrown stance, verbatim from base TQAE. These keys are
        # ABSENT on SV's table, so set_field infers STRING (matching every
        # sibling `*Anim*` clip field). No explicit dtype - clone-safe.
        for field, clip in fam["clips"].items():
            db.set_field(fam["clone"], field, clip)

    for entry in thrown_restore.ROSTER:
        fam = _family_for(entry)
        rec = entry["record"]
        # (a) repoint ONLY the roster records at the clone
        db.set_field(rec, "charAnimationTableName", fam["clone"])
        # (b) SECOND SURFACE: the SAME verbatim base clips on the creature
        #     record itself, because SV turned ANM_Maenad into a Monster.tpl
        #     record and we cannot prove from the DB that the engine still
        #     accepts it as an animation table (docstring, BL-R140-MAENAD-TPL-1).
        #     Identical values, so whichever surface the engine reads it gets the
        #     same animation; applied to all four families for uniformity rather
        #     than special-casing maenad.
        for field, clip in fam["clips"].items():
            db.set_field(rec, field, clip)


# ---------------------------------------------------------------------------
def verify(db, tags):
    """Gate for R-100 #15.

    1. ROSTER INVARIANT (DB-wide, not 10 named exceptions): no Class=Monster
       record equips a thrown weapon while its animation table leaves that
       weapon's stance without Run + Walk + Attack.
    2. Every roster record points at THIS module's clone for its family.
    3. Every clone binds every clip the family declares.
    4. SHARED-RECORD PROOF: the four ORIGINAL tables were not edited - they
       still bind ZERO thrown-stance clips - and no non-target carrier was
       repointed.
    """
    errs = []

    def gv(rec, key):
        return _fv(db.get_fields(rec), key)

    # ---- 1. the roster invariant -------------------------------------------
    throwers, frozen = scan_frozen_throwers(db)
    if not throwers:
        errs.append("no thrown-weapon wielder found in the DB at all - the "
                    "invariant would be vacuously true; thrown_restore must "
                    "have stopped arming anything")
    for rec, stance, tbl, missing in frozen:
        errs.append("FROZEN THROWER %s: equips a thrown weapon (stance %s) but "
                    "table %s leaves %s unbound - it will spawn unable to move "
                    "or attack (R-100 #15)" % (rec, stance, tbl, ", ".join(missing)))

    # ---- 2/3. roster wiring + clone completeness ---------------------------
    for entry in thrown_restore.ROSTER:
        fam = _family_for(entry)
        rec = entry["record"]
        if not db.has_record(rec):
            errs.append("roster record %s missing" % rec)
            continue
        got = gv(rec, "charAnimationTableName")
        if _norm(got) != _norm(fam["clone"]):
            errs.append("%s charAnimationTableName=%r, expected this module's "
                        "clone %r" % (rec, got, fam["clone"]))
        want = expected_stance(entry)
        if want != fam["stance"]:
            errs.append("%s selects stance %s but family %s restores %s"
                        % (rec, want, fam["key"], fam["stance"]))
        # SECOND SURFACE: the creature record must carry the clips too, so the
        # rig survives even if the engine refuses SV's Monster.tpl "table".
        rff = db.get_fields(rec)
        for field, clip in fam["clips"].items():
            got = _fv(rff, field)
            if _norm(got) != _norm(clip):
                errs.append("%s (creature record, 2nd surface) %s=%r, expected "
                            "the verbatim base clip %r" % (rec, field, got, clip))

    for fam in FAMILIES:
        clone = fam["clone"]
        if not db.has_record(clone):
            errs.append("missing cloned animation table %s" % clone)
            continue
        for field, clip in fam["clips"].items():
            got = gv(clone, field)
            if _norm(got) != _norm(clip):
                errs.append("%s %s=%r, expected the verbatim base clip %r"
                            % (clone, field, got, clip))
        for slot in CRITICAL_SLOTS:
            v = gv(clone, fam["stance"] + slot)
            if not (isinstance(v, str) and v.lower().endswith(".anm")):
                errs.append("%s %s%s is not an .anm clip (%r) - the stance "
                            "would still be dead" % (clone, fam["stance"], slot, v))

    # ---- 4. SHARED-RECORD proof --------------------------------------------
    targets = {_norm(e["record"]) for e in thrown_restore.ROSTER}
    clone_of = {_norm(f["clone"]): f for f in FAMILIES}
    # ONE sweep for every family's carrier check (not one sweep per family).
    moved = {}
    for name in db.record_names():
        if _norm(name) in targets:
            continue
        t = _fv(db.get_fields(name), "charAnimationTableName")
        if t and _norm(t) in clone_of:
            moved.setdefault(_norm(t), []).append(name)

    for fam in FAMILIES:
        orig = fam["table"]
        if not db.has_record(orig):
            errs.append("original animation table %s vanished" % orig)
            continue
        for slot in CRITICAL_SLOTS:
            v = gv(orig, fam["stance"] + slot)
            if isinstance(v, str) and v.lower().endswith(".anm"):
                errs.append("SHARED-RECORD VIOLATION: original table %s now "
                            "binds %s%s=%r - this module must CLONE, never edit "
                            "a table with non-target carriers"
                            % (orig, fam["stance"], slot, v))
        hits = moved.get(_norm(fam["clone"]), [])
        if hits:
            errs.append("non-target carriers repointed onto %s: %s"
                        % (fam["clone"], ", ".join(sorted(hits)[:5])))

    if errs:
        raise SystemExit("thrown_anim_rig.verify FAILED:\n  " + "\n  ".join(errs))

    n_clips = sum(len(f["clips"]) for f in FAMILIES)
    n_rec_clips = sum(len(_family_for(e)["clips"]) for e in thrown_restore.ROSTER)
    print("  thrown_anim_rig.verify: OK (%d thrown wielders in the DB, 0 frozen; "
          "%d cloned animation tables carrying %d verbatim base clips + the same "
          "clips on %d repointed creature records (%d clips, 2nd surface); all %d "
          "shared originals unedited, 0 non-target carriers moved)"
          % (len(throwers), len(FAMILIES), n_clips,
             len(thrown_restore.ROSTER), n_rec_clips, len(FAMILIES)))


# ---------------------------------------------------------------------------
# PLANTED NEGATIVES - each must turn the gate RED.
# ---------------------------------------------------------------------------
def _negtest(db, tags):
    """Plant each defect shape into the REAL db, run verify(), then restore the
    exact prior field state.

    Save/restore rather than a deepcopy of `db`: `_decoded_cache` holds ~51k
    decoded records, so copying it once per case (9 cases) is minutes of work
    and gigabytes. Restoration is exact - the pre-value is read back with the
    same accessor and re-written, and `_modified` is rewound to its prior
    contents - and it is proved: verify() is re-run at the end and must be
    GREEN again, so nothing leaks between cases or out of the negative test.
    """
    checks = 0
    fam0 = FAMILIES[0]
    rec0 = thrown_restore.ROSTER[0]["record"]
    victim = r"records\creature\monster\maenad\ar_archer_04.dbr"   # non-roster sibling

    def _snapshot(pairs):
        return [(rec, key, db.get_field_value(rec, key)) for rec, key in pairs]

    def _restore(snap, mod_before):
        for rec, key, old in snap:
            db.set_field(rec, key, old if old is not None else "")
        db._modified.clear()
        db._modified.update(mod_before)

    def _case(pairs, mutate, label, expect_fail=True):
        nonlocal checks
        mod_before = set(db._modified)
        snap = _snapshot(pairs)
        mutate()
        try:
            verify(db, dict(tags))
            passed = True
        except SystemExit:
            passed = False
        finally:
            _restore(snap, mod_before)
        if expect_fail and passed:
            raise SystemExit("negtest: expected verify FAIL for %s, but it PASSED" % label)
        if not expect_fail and not passed:
            raise SystemExit("negtest: expected verify PASS for %s, but it FAILED" % label)
        checks += 1

    S = fam0["stance"]

    # --- MUST RED: the defect itself, re-planted three ways -----------------
    _case([(fam0["clone"], S + "RunAnim")],
          lambda: db.set_field(fam0["clone"], S + "RunAnim", ""),
          "clone loses its thrown RUN anim (the freeze)")
    _case([(fam0["clone"], S + "WalkAnim")],
          lambda: db.set_field(fam0["clone"], S + "WalkAnim", ""),
          "clone loses its thrown WALK anim")
    _case([(fam0["clone"], S + "AttackAnim1")],
          lambda: db.set_field(fam0["clone"], S + "AttackAnim1", ""),
          "clone loses its thrown ATTACK anim")
    # --- MUST RED: the exact PRE-FIX state ----------------------------------
    _case([(rec0, "charAnimationTableName")],
          lambda: db.set_field(rec0, "charAnimationTableName", fam0["table"]),
          "roster record repointed back at SV's stripped shared table (the shipped bug)")
    # --- MUST RED: a slot bound to something that is not an animation -------
    _case([(fam0["clone"], S + "RunAnim")],
          lambda: db.set_field(fam0["clone"], S + "RunAnim",
                               r"Creatures\Monster\Maenad\Maenad02.msh"),
          "thrown RUN slot bound to a MESH instead of an .anm")
    # --- MUST RED: SHARED-RECORD LAW violation ------------------------------
    _case([(fam0["table"], S + "RunAnim")],
          lambda: db.set_field(fam0["table"], S + "RunAnim", fam0["clips"][S + "RunAnim"]),
          "shared ORIGINAL table edited in place instead of cloned")
    # --- MUST RED: the SECOND surface loses its clips -----------------------
    _case([(rec0, S + "RunAnim")],
          lambda: db.set_field(rec0, S + "RunAnim", ""),
          "creature record (2nd surface) loses its thrown RUN anim")
    _case([(rec0, S + "AttackAnim1")],
          lambda: db.set_field(rec0, S + "AttackAnim1", ""),
          "creature record (2nd surface) loses its thrown ATTACK anim")
    # --- MUST RED: the TRUE engine freeze - BOTH surfaces lose the same slot,
    #     which is the only state the DB-wide invariant itself calls frozen ----
    _case([(rec0, S + "RunAnim"), (fam0["clone"], S + "RunAnim")],
          lambda: (db.set_field(rec0, S + "RunAnim", ""),
                   db.set_field(fam0["clone"], S + "RunAnim", "")),
          "BOTH surfaces lose the thrown RUN anim (the actual statue state)")
    # --- MUST RED: the class, not the 10 instances - ANY new thrown wielder
    #     anywhere in the DB, on a stance-stripped table and with no record
    #     clips of its own ----------------------------------------------------
    def _plant_new_thrower():
        db.set_field(victim, "chanceToEquipRightHand", 100.0)
        db.set_field(victim, "lootRightHandItem1",
                     [r"records\xpack2\item\loottables\weapons\static\1h_ranged_01b.dbr"])
    _case([(victim, "chanceToEquipRightHand"), (victim, "lootRightHandItem1")],
          _plant_new_thrower,
          "a NON-roster monster armed with a thrown weapon on a stripped table")

    # --- MUST STAY GREEN: things this gate must NOT police ------------------
    _case([(victim, "chanceToEquipRightHand")],
          lambda: db.set_field(victim, "chanceToEquipRightHand", 100.0),
          "a NON-thrown equip change on a sibling monster", expect_fail=False)
    _case([(fam0["clone"], S + "StunAnim")],
          lambda: db.set_field(fam0["clone"], S + "StunAnim",
                               r"Creatures\Monster\Maenad\ANM\Maenad_UnArmed_Stun.anm"),
          "a NON-critical clip slot rewritten", expect_fail=False)

    # restoration proof: the gate is green again on the untouched db
    verify(db, dict(tags))
    print("  thrown_anim_rig._negtest: OK (%d planted cases - 10 must-RED, 2 must-stay-GREEN "
          "- and verify is GREEN again after full restore)" % checks)


# ---------------------------------------------------------------------------
# Stand-alone dry-run (no heavy build):
#   py tools/patches/thrown_anim_rig.py <mod.arz>
# Proves the PRE-STATE (frozen throwers exist), applies thrown_restore then this
# module, and shows the POST-STATE (0 frozen) + verify + planted negatives.
# ---------------------------------------------------------------------------
def _selftest(mod_arz):
    import sys
    from pathlib import Path
    HERE = Path(__file__).resolve().parent.parent  # tools/
    sys.path.insert(0, str(HERE))
    from arz_patcher import ArzDatabase

    print("loading mod overlay %s ..." % mod_arz)
    db = ArzDatabase.from_arz(Path(mod_arz))
    tags = {}

    print("\n--- PRE-STATE (as SHIPPED: thrown_restore has already run in this arz) ---")
    pre_throwers, pre_frozen = scan_frozen_throwers(db)
    print("  thrown wielders: %d   FROZEN: %d" % (len(pre_throwers), len(pre_frozen)))
    for rec, stance, tbl, missing in sorted(pre_frozen):
        print("    FROZEN %s  stance=%s  table=%s" % (rec, stance, tbl))

    before = set(db.record_names())
    apply(db, tags)
    added = sorted(set(db.record_names()) - before)
    intended = sorted(f["clone"] for f in FAMILIES)
    print("\nintended-only record delta: +%d" % len(added))
    for a in added:
        print("    + %s" % a)
    assert added == intended, "added != intended (%s)" % (set(added) ^ set(intended))

    modified = sorted(db._modified)
    allowed = set(intended) | {e["record"] for e in thrown_restore.ROSTER}
    stray = [m for m in modified if m not in allowed]
    assert not stray, "STRAY modifications outside clones+roster: %s" % stray
    print("modified records: %d (all within %d clones + %d roster records)"
          % (len(modified), len(intended), len(thrown_restore.ROSTER)))

    print("\n--- POST-STATE ---")
    post_throwers, post_frozen = scan_frozen_throwers(db)
    print("  thrown wielders: %d   FROZEN: %d" % (len(post_throwers), len(post_frozen)))

    verify(db, tags)
    _negtest(db, tags)
    print("\nthrown_anim_rig DRY-RUN: PASS (%d frozen -> %d; +%d records; verify OK; negtest OK)"
          % (len(pre_frozen), len(post_frozen), len(added)))


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("usage: py tools/patches/thrown_anim_rig.py <mod.arz>")
        raise SystemExit(2)
    _selftest(sys.argv[1])
