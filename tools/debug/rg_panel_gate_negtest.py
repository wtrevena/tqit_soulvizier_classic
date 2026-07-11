r"""build36 round-2 A8: unit + NEGATIVE test for the Runemaster golem-panel wiring
+ gate, run WITHOUT the full DB build. Exercises _rg_wire_runemaster_panel +
_verify_runemaster_golem_button against a real baseline arz db.

  POSITIVE: after wiring, both mastery-10 panectrl overrides exist, carry Skill23,
            and have 23 (xpack2) / 25 (xpack3) buttons; the gate PASSES.
  NEGATIVE: drop Skill23 from a pane -> gate FAILS (SystemExit); delete a pane ->
            gate FAILS; button not pointing at the summon -> gate FAILS.

usage: py tools/debug/rg_panel_gate_negtest.py <baseline.arz>
exit 0 = all assertions held, 1 = a case behaved wrong.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase, DATA_TYPE_STRING  # noqa: E402
import apply_svc_patches as A  # noqa: E402


def _gate_raises(db):
    try:
        A._verify_runemaster_golem_button(db)
        return False
    except SystemExit:
        return True


def _btns(db, pane):
    return [str(b) for b in (db.get_field_value(pane, 'tabSkillButtons') or [])]


def main(arz):
    db = ArzDatabase.from_arz(Path(arz))
    fails = []

    # minimal golem presence so the gate is ACTIVE (baseline predates the graft)
    A._ensure_record(db, A._RG_SUMMON, '')
    A._ensure_record(db, A._RG_UI, '')
    db.set_field(A._RG_UI, 'skillName', [A._RG_SUMMON], DATA_TYPE_STRING)

    # ---- POSITIVE: wire + gate passes -------------------------------------
    A._rg_wire_runemaster_panel(db)
    want = A._RG_UI_BTN.replace('/', '\\').lower()
    for pane, n in ((A._RG_PANE_XPACK2, 23), (A._RG_PANE_XPACK3, 25)):
        if not db.has_record(pane):
            fails.append(f"POSITIVE: pane {pane} not created")
            continue
        bl = _btns(db, pane)
        if not any(b.replace('/', '\\').lower() == want for b in bl):
            fails.append(f"POSITIVE: {pane} lacks Skill23")
        if len(bl) != n:
            fails.append(f"POSITIVE: {pane} has {len(bl)} buttons, expected {n}")
    if _gate_raises(db):
        fails.append("POSITIVE: gate FAILED on a correctly-wired db")
    else:
        print("POSITIVE ok: both panes wired, Skill23 present, gate PASSES")

    # idempotency: wiring twice must not double-append
    A._rg_wire_runemaster_panel(db)
    if len(_btns(db, A._RG_PANE_XPACK3)) != 25:
        fails.append("IDEMPOTENCY: second wire changed the button count")
    else:
        print("IDEMPOTENCY ok: re-wiring did not duplicate Skill23")

    # ---- NEGATIVE 1: drop Skill23 from xpack3 -> gate must FAIL ------------
    bl = [b for b in _btns(db, A._RG_PANE_XPACK3)
          if b.replace('/', '\\').lower() != want]
    db.set_field(A._RG_PANE_XPACK3, 'tabSkillButtons', bl, DATA_TYPE_STRING)
    if _gate_raises(db):
        print("NEGATIVE-1 ok: dropping Skill23 from a pane -> gate FAILS")
    else:
        fails.append("NEGATIVE-1: gate PASSED after Skill23 removed from xpack3")

    # ---- NEGATIVE 2: re-wire, then delete xpack2 pane -> gate must FAIL ----
    A._rg_wire_runemaster_panel(db)                       # restore both panes
    if A._RG_PANE_XPACK2 in db._raw_records:
        del db._raw_records[A._RG_PANE_XPACK2]
    if _gate_raises(db):
        print("NEGATIVE-2 ok: missing xpack2 panectrl -> gate FAILS")
    else:
        fails.append("NEGATIVE-2: gate PASSED with the xpack2 panectrl deleted")

    # ---- NEGATIVE 3: button not pointing at the summon -> gate FAILS -------
    A._rg_wire_runemaster_panel(db)
    db.set_field(A._RG_UI, 'skillName', [r'records\bogus\wrong.dbr'], DATA_TYPE_STRING)
    if _gate_raises(db):
        print("NEGATIVE-3 ok: Skill23 button pointing elsewhere -> gate FAILS")
    else:
        fails.append("NEGATIVE-3: gate PASSED with the button mis-pointed")

    print("=" * 60)
    if fails:
        for f in fails:
            print("  ASSERT FAILED:", f)
        print(f"RESULT: {len(fails)} failure(s)")
        return 1
    print("RESULT: PASS - gate flags every seeded violation, green when correct")
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1]))
