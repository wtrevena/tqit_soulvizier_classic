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
WHY THE FIX GOES IN THE TABLE AND NOT ON THE CREATURE RECORD
=============================================================================
Both surfaces exist, so this was decided from shipping data rather than belief -
`py tools/debug/probe_anim_authority.py <base.arz>`, over all **5,561**
base-game `Class=Monster` records:

  * 2,596 records bind a Run/Walk/Attack slot on the RECORD that their table
    does not  -> the record IS read.
  * 8,884 records bind one on the TABLE that their record does not -> the table
    IS read. (Per-field fallback: record overrides, table fills in.)
  * **For `rangedOneHand` and `dualRanged` specifically: 0 records bind them at
    record level, 1,085 + 259 get them from the table ONLY.** Not one shipping
    thrower in the entire game carries its thrown anims on its own record.

So the table is the load-bearing surface for this stance and the only shape with
any shipping precedent. Writing the clips onto the 10 creature records instead
would be an invented shape with zero precedent - and if the engine reads the
stance from the table alone, it would ship a third statue.

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
Will's pets). So this module NEVER edits a shared table: it CLONES each one into
its own `records\creature\monster\svc\thrown_anm\...` record, restores the base
thrown-stance clips ON THE CLONE, and repoints `charAnimationTableName` on
exactly the 10 roster records. verify() proves the four originals still bind
zero thrown clips (i.e. were not edited) and that every non-target carrier still
names the original table.

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
weapon while naming an animation table that leaves that weapon's stance without
RunAnim + WalkAnim + AttackAnim1. `scan_frozen_throwers()` is the single
implementation, used by verify(), by the negative tests and by
`tools/debug/probe_frozen_throwers.py`.

Contract (tools/patches/README.md): MODULE_NAME + apply(db, tags) + verify.
"""

MODULE_NAME = ("Thrown-wielder ANIMATION RIG (R-100 #15): restore the thrown "
               "stance SV stripped, on cloned per-family anim tables")

import thrown_restore  # noqa: E402  (sibling module; tools/patches on sys.path)


# ---------------------------------------------------------------------------
# The clip slots that decide whether a creature can MOVE and ATTACK in a stance.
# A stance missing any of these is a statue.
# ---------------------------------------------------------------------------
CRITICAL_SLOTS = ("RunAnim", "WalkAnim", "AttackAnim1")

# Where the cloned tables live. Disjoint SVC namespace - no other module writes
# under it, and no base/SV record is displaced.
_NS = r"records\creature\monster\svc\thrown_anm"


def _norm(s):
    return str(s).replace("/", "\\").lower()


def _scalar(v):
    return v[0] if isinstance(v, list) and v else v


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
        "clone": _NS + r"\anm_maenad_thrown.dbr",
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
        "clone": _NS + r"\anm_tiger_thrown.dbr",
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
        "clone": _NS + r"\anm_machae_thrown.dbr",
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
        "clone": _NS + r"\anm_duneraider_thrown.dbr",
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


def scan_frozen_throwers(db):
    """(throwers, frozen) over the whole DB.

    throwers = [(record, stance, table)] for every Class=Monster that equips a
               thrown weapon at chance > 0.
    frozen   = [(record, stance, table, [unbound critical slots])] - the
               violators of the R-100 #15 invariant.
    """
    def gv(rec, key):
        return db.get_field_value(rec, key)

    tbl_cache = {}

    def table_binds(tbl, stance):
        key = (_norm(tbl), stance)
        if key in tbl_cache:
            return tbl_cache[key]
        missing = []
        if not db.has_record(tbl):
            # Not in the overlay -> pure base pass-through. The base tables DO
            # bind the thrown stance (measured), so a pass-through table is
            # healthy by construction; treat as bound and say so.
            tbl_cache[key] = missing
            return missing
        for slot in CRITICAL_SLOTS:
            v = _scalar(gv(tbl, stance + slot))
            if not (isinstance(v, str) and v.lower().endswith(".anm")):
                missing.append(stance + slot)
        tbl_cache[key] = missing
        return missing

    throwers, frozen = [], []
    for name in db.record_names():
        if _scalar(gv(name, "Class")) != "Monster":
            continue
        right = float(_scalar(gv(name, "chanceToEquipRightHand")) or 0)
        left = float(_scalar(gv(name, "chanceToEquipLeftHand")) or 0)
        r_thrown = right > 0 and _is_thrown_loot(gv(name, "lootRightHandItem1"))
        l_thrown = left > 0 and _is_thrown_loot(gv(name, "lootLeftHandItem1"))
        if not (r_thrown or l_thrown):
            continue
        stance = "dualRanged" if (r_thrown and l_thrown) else "rangedOneHand"
        tbl = _scalar(gv(name, "charAnimationTableName"))
        throwers.append((name, stance, tbl))
        if not tbl:
            frozen.append((name, stance, None, ["<no charAnimationTableName>"]))
            continue
        missing = table_binds(tbl, stance)
        if missing:
            frozen.append((name, stance, tbl, list(missing)))
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

    # repoint ONLY the roster records (imported, so the two modules cannot drift)
    for entry in thrown_restore.ROSTER:
        fam = _family_for(entry)
        db.set_field(entry["record"], "charAnimationTableName", fam["clone"])


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
        return _scalar(db.get_field_value(rec, key))

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
        # nobody outside the roster was repointed off the original
        moved = []
        for name in db.record_names():
            if _norm(name) in targets:
                continue
            t = gv(name, "charAnimationTableName")
            if t and _norm(t) == _norm(fam["clone"]):
                moved.append(name)
        if moved:
            errs.append("non-target carriers repointed onto %s: %s"
                        % (fam["clone"], ", ".join(sorted(moved)[:5])))

    if errs:
        raise SystemExit("thrown_anim_rig.verify FAILED:\n  " + "\n  ".join(errs))

    n_clips = sum(len(f["clips"]) for f in FAMILIES)
    print("  thrown_anim_rig.verify: OK (%d thrown wielders in the DB, 0 frozen; "
          "%d cloned animation tables carrying %d verbatim base clips; %d roster "
          "records repointed; all %d shared originals unedited)"
          % (len(throwers), len(FAMILIES), n_clips,
             len(thrown_restore.ROSTER), len(FAMILIES)))


# ---------------------------------------------------------------------------
# PLANTED NEGATIVES - each must turn the gate RED.
# ---------------------------------------------------------------------------
def _clone_db_shallow(d):
    import copy
    d2 = copy.copy(d)
    d2._decoded_cache = copy.deepcopy(d._decoded_cache)
    d2._modified = set(d._modified)
    return d2


def _negtest(db, tags):
    checks = 0
    fam0 = FAMILIES[0]
    rec0 = thrown_restore.ROSTER[0]["record"]

    def _expect_fail(mutate, label):
        nonlocal checks
        d2 = _clone_db_shallow(db)
        mutate(d2)
        try:
            verify(d2, dict(tags))
        except SystemExit:
            checks += 1
            return
        raise SystemExit("negtest: expected verify FAIL for %s, but it passed" % label)

    def _expect_pass(mutate, label):
        nonlocal checks
        d2 = _clone_db_shallow(db)
        mutate(d2)
        verify(d2, dict(tags))   # must NOT raise
        checks += 1

    # THE defect itself, re-planted three ways.
    _expect_fail(lambda d: d.set_field(fam0["clone"], fam0["stance"] + "RunAnim", ""),
                 "clone loses its thrown RUN anim (the freeze)")
    _expect_fail(lambda d: d.set_field(fam0["clone"], fam0["stance"] + "WalkAnim", ""),
                 "clone loses its thrown WALK anim")
    _expect_fail(lambda d: d.set_field(fam0["clone"], fam0["stance"] + "AttackAnim1", ""),
                 "clone loses its thrown ATTACK anim")
    # the pre-fix state: roster record still points at SV's stripped table
    _expect_fail(lambda d: d.set_field(rec0, "charAnimationTableName", fam0["table"]),
                 "roster record repointed back at SV's stripped shared table")
    # a clip that is not an .anm at all
    _expect_fail(lambda d: d.set_field(fam0["clone"], fam0["stance"] + "RunAnim",
                                       r"Creatures\Monster\Maenad\Maenad02.msh"),
                 "thrown RUN slot bound to a mesh instead of an .anm")
    # SHARED-RECORD guard: editing the original table instead of cloning
    _expect_fail(lambda d: d.set_field(fam0["table"], fam0["stance"] + "RunAnim",
                                       fam0["clips"][fam0["stance"] + "RunAnim"]),
                 "shared original table edited in place (SHARED-RECORD LAW)")
    # a NEW thrown wielder anywhere in the DB whose table lacks the stance
    def _plant_new_thrower(d):
        victim = r"records\creature\monster\maenad\ar_archer_04.dbr"
        d.set_field(victim, "chanceToEquipRightHand", 100.0)
        d.set_field(victim, "lootRightHandItem1",
                    [r"records\xpack2\item\loottables\weapons\static\1h_ranged_01b.dbr"])
    _expect_fail(_plant_new_thrower,
                 "a NON-roster monster armed with a thrown weapon on a stripped table")

    # NEGATIVE CONTROL: the gate must stay GREEN for changes it must not police.
    _expect_pass(lambda d: d.set_field(fam0["clone"], fam0["stance"] + "StunAnim",
                                       fam0["clips"][fam0["stance"] + "StunAnim"]),
                 "re-writing a non-critical clip to its own value stays green")
    _expect_pass(lambda d: d.set_field(
        r"records\creature\monster\maenad\ar_archer_04.dbr",
        "chanceToEquipRightHand", 100.0),
        "a non-thrown equip change on a sibling monster stays green")

    print("  thrown_anim_rig._negtest: OK (%d planted cases: 7 must-red, 2 must-stay-green)"
          % checks)


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
