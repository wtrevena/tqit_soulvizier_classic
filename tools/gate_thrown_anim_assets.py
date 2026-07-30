r"""THROWN-ANIM ASSET GATE (R-140 wave, fail-loud): every `.anm` clip a thrown
wielder relies on must actually EXIST in the shipped arc set.

WHY THIS EXISTS SEPARATELY FROM `thrown_anim_rig.verify`
--------------------------------------------------------
`thrown_anim_rig.verify` proves the DATABASE is right: the thrown stance is
bound, on both surfaces, with the verbatim base clip strings. It cannot prove
those strings point at a file that ships. That is the same gap that produced the
defect it fixes - SV left `rangedOneHand*AnimSpeed` numerics in place, the old
`thrown_wielders.verify` saw non-None values and went green, and the monsters
shipped as statues anyway. A clip path that resolves nowhere is the identical
failure one layer down: green database, frozen monster.

R-100 #15's brief states the requirement directly - *"prove for each that its
attack/move animations resolve on its actual mesh"* and *"GATE: every thrown
wielder's referenced anms resolve; planted negative on a broken binding."*
This file is that gate.

THE INVARIANT (stated over the whole roster, not over our 10 records)
---------------------------------------------------------------------
    For every `Class=Monster` record that equips a thrown weapon, every `.anm`
    this database binds for that weapon's stance - on the creature record OR on
    its animation table - must resolve in the shipped arc set under the engine's
    own archive-scoping rule.

Resolution is delegated to `validate_render_chain.EngineArcResolver`, the
repo's canonical engine-faithful resolver, rather than a second local copy: a
plain `<Arc>\<inner>` ref resolves in the mod's Resources `<Arc>.arc` first then
base `<game>\Resources\<Arc>.arc`, while an `XPackN\<Arc>\<inner>` ref resolves
ONLY in `<game>\Resources\XPackN\<Arc>.arc`. That scoping is exactly what a
hand-rolled "strip the first component" check gets wrong - the machae family's
9 clips live in `Resources\xpack\Creatures.arc` and a naive matcher reports all
9 as MISSING when they are in fact present.

The thrower enumeration is IMPORTED from `patches.thrown_anim_rig`
(`scan_frozen_throwers`), never re-implemented, so the gate and the module can
never disagree about who is a thrown wielder.

usage:
  py tools/gate_thrown_anim_assets.py <mod.arz> <mod_resources_dir> <game_dir>
  py tools/gate_thrown_anim_assets.py <mod.arz> <mod_resources_dir> <game_dir> --selftest
exit 0 = PASS, 1 = FAIL, 2 = load error.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "patches"))

from arz_patcher import ArzDatabase                    # noqa: E402
from validate_render_chain import EngineArcResolver    # noqa: E402
import thrown_anim_rig                                 # noqa: E402

STANCES = ("rangedOneHand", "dualRanged")
CRITICAL = thrown_anim_rig.CRITICAL_SLOTS


def _n(s):
    return str(s).replace("/", "\\").lower()


def _scalar(v):
    return v[0] if isinstance(v, list) and v else v


def _stance_clips(db, rec, stance):
    """{field: clip} for every <stance>* field on `rec` holding an .anm."""
    out = {}
    for k, tf in (db.get_fields(rec) or {}).items():
        key = k.split("###")[0]
        if not key.startswith(stance):
            continue
        v = _scalar(tf.value)
        if isinstance(v, str) and v.lower().endswith(".anm"):
            out[key] = v
    return out


def collect(db):
    """[(record, stance, field, clip, surface)] - every thrown-stance clip this
    database binds for a thrown wielder, from BOTH surfaces.

    A creature whose animation table is absent from the overlay is a pure
    base-game pass-through: the engine reads base's own table, which this mod
    never wrote, so there is nothing for this gate to police there.
    """
    idx = {_n(x): x for x in db.record_names()}
    throwers, _ = thrown_anim_rig.scan_frozen_throwers(db)
    rows = []
    for rec, stance, tbl in throwers:
        for field, clip in _stance_clips(db, rec, stance).items():
            rows.append((rec, stance, field, clip, "record"))
        real = idx.get(_n(tbl)) if tbl else None
        if real is not None:
            for field, clip in _stance_clips(db, real, stance).items():
                rows.append((real, stance, field, clip, "table"))
    return throwers, rows


def validate(arz, mod_res, game_dir, db=None, quiet=False):
    """(ok, message). `db` lets the selftest re-validate a mutated in-memory DB."""
    if db is None:
        db = ArzDatabase.from_arz(Path(arz))
    res = EngineArcResolver(mod_res, game_dir)

    throwers, rows = collect(db)
    errs = []

    if not throwers:
        errs.append("no thrown-weapon wielder found at all - the gate would be "
                    "vacuously true; the thrown restore must have stopped arming "
                    "anything")

    # (A) RESOLUTION - the reason this gate exists
    seen = {}
    for rec, stance, field, clip, surface in rows:
        key = _n(clip)
        if key not in seen:
            seen[key] = res.resolve(clip)
        ok, detail = seen[key]
        if not ok:
            errs.append("UNRESOLVED ANM %s (%s surface) %s = %r -> %s. The "
                        "stance is bound in the database but the clip does not "
                        "ship, so the creature still cannot play it (R-100 #15)."
                        % (rec, surface, field, clip, detail))

    # (B) the critical slots must be bound at all, on one surface or the other
    _, frozen = thrown_anim_rig.scan_frozen_throwers(db)
    for rec, stance, tbl, missing in frozen:
        errs.append("FROZEN THROWER %s (stance %s, table %s): %s unbound on BOTH "
                    "surfaces - it spawns unable to move or attack"
                    % (rec, stance, tbl, ", ".join(missing)))

    n_clips = len(seen)
    if errs:
        return False, ("THROWN-ANIM ASSET GATE: FAIL (%d problem(s))\n  " % len(errs)
                       + "\n  ".join(errs))
    msg = ("THROWN-ANIM ASSET GATE: PASS - %d thrown wielder(s), %d distinct .anm "
           "clip(s) bound across both surfaces, %d/%d resolve in the shipped arc "
           "set, 0 frozen" % (len(throwers), n_clips, n_clips, n_clips))
    if not quiet:
        print(msg)
    return True, msg


# ---------------------------------------------------------------------------
# PLANTED NEGATIVES - the gate is worthless unless these actually turn it RED.
# ---------------------------------------------------------------------------
def _selftest(arz, mod_res, game_dir):
    db = ArzDatabase.from_arz(Path(arz))
    ok, msg = validate(arz, mod_res, game_dir, db=db, quiet=True)
    if not ok:
        print(msg)
        raise SystemExit("selftest cannot run: the gate is already RED on the "
                         "unmodified build")
    print("baseline: %s" % msg)

    throwers, _ = thrown_anim_rig.scan_frozen_throwers(db)
    if not throwers:
        raise SystemExit("selftest: no thrower to plant on")
    rec, stance, tbl = sorted(throwers)[0]
    idx = {_n(x): x for x in db.record_names()}
    table = idx.get(_n(tbl))
    run = stance + "RunAnim"
    stun = stance + "StunAnim"
    checks = 0

    def _case(pairs, mutate, label, expect_fail=True):
        nonlocal checks
        snap = [(r, k, db.get_field_value(r, k)) for r, k in pairs]
        mutate()
        try:
            passed, _m = validate(arz, mod_res, game_dir, db=db, quiet=True)
        finally:
            for r, k, old in snap:
                db.set_field(r, k, old if old is not None else "")
        state = "RED" if not passed else "GREEN"
        want = "RED" if expect_fail else "GREEN"
        print("  [%s] %-64s -> %s" % ("ok " if state == want else "BAD", label, state))
        if state != want:
            raise SystemExit("negtest: expected %s for %s, got %s" % (want, label, state))
        checks += 1

    # 1. the brief's own case: a broken binding (path that ships nowhere)
    _case([(rec, run)],
          lambda: db.set_field(rec, run, r"Creatures\Monster\Maenad\ANM\NoSuchClip_XYZ.anm"),
          "critical clip bound to a path that ships nowhere")
    # 2. the XPACK-SCOPE bug this resolver exists to catch: a real file, named
    #    under the wrong expansion scope, resolves nowhere.
    _case([(rec, run)],
          lambda: db.set_field(rec, run,
                               r"XPack2\Creatures\Monster\Machae\ANM\Machae_OneHand_Run.anm"),
          "real clip referenced under the WRONG XPack scope")
    # 3. a clip that exists but is not an animation
    _case([(rec, run)],
          lambda: db.set_field(rec, run, r"Creatures\Monster\Maenad\NoSuchMesh_XYZ.anm"),
          "critical clip bound to a non-existent asset with an .anm name")
    # 4. the freeze itself - the slot lost on BOTH surfaces
    if table is not None:
        _case([(rec, run), (table, run)],
              lambda: (db.set_field(rec, run, ""), db.set_field(table, run, "")),
              "critical clip lost on BOTH surfaces (the statue state)")
    # 5. an unresolvable clip on the TABLE surface, not the record
    if table is not None:
        _case([(table, run)],
              lambda: db.set_field(table, run, r"Creatures\Monster\Maenad\ANM\Ghost_XYZ.anm"),
              "unresolvable clip on the TABLE surface")
    # 6. MUST STAY GREEN: a non-critical slot rewritten to another REAL clip
    _case([(rec, stun)],
          lambda: db.set_field(rec, stun, r"Creatures\Monster\Maenad\ANM\Maenad_Walk.anm"),
          "non-critical slot repointed at a DIFFERENT clip that does ship",
          expect_fail=False)

    ok, msg = validate(arz, mod_res, game_dir, db=db, quiet=True)
    if not ok:
        raise SystemExit("negtest: gate did not return to GREEN after restore:\n" + msg)
    print("SELFTEST: PASS (%d planted cases - 5 must-RED, 1 must-stay-GREEN - and "
          "the gate is GREEN again after full restore)" % checks)


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    arz, mod_res, game_dir = argv[1], argv[2], argv[3]
    if "--selftest" in argv:
        _selftest(arz, mod_res, game_dir)
        return 0
    try:
        ok, msg = validate(arz, mod_res, game_dir)
    except Exception as e:                                   # noqa: BLE001
        print("THROWN-ANIM ASSET GATE: LOAD ERROR %s" % e)
        return 2
    if not ok:
        print(msg)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
