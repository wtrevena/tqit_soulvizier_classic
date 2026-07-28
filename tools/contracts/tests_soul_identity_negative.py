r"""Permanent NEGATIVE-TEST for the b97 soul-IDENTITY gate (tools/patches/soul_identity.py).

A gate that never fires is worthless. This suite proves, over a real built/shipped .arz:

  T1 POSITIVE   the FIXED db is clean - verify() passes (no creature drops another
                named creature's soul).
  T2 NEGATIVE   re-arming ONE of today's REAL mismatches (Fesil the Quick, base-game
                record hero_wheedletongue_41, dropping "Wheedletongue the Magnificent
                Soul" - see docs/reports/b97_soul_identity_audit.md) makes verify()
                FAIL, naming that record. This is the planted reproduction of the bug
                Will reported on 2026-07-27.
  T3 NEGATIVE   a SYNTHETIC cross-wire (hand a clean hero a foreign, owned soul) is
                caught too, so the gate is not accidentally special-cased to T2.
  T4 GUARD      a SHARED-ARCHETYPE family (Satyr Fire Magi: no carrier owns the name,
                so the named uniques are the only source) is NOT flagged. This is the
                orphan-safety half of the rule: a future "tighten it" change that
                starts zeroing archetype souls fails HERE instead of in-game.
  T5 GUARD      identity is judged on DISPLAY NAME, never the .dbr filename. Proves
                the exact base-game trap: filename 'hero_wheedletongue_41' contains
                'wheedletongue', yet the record is "Fesil the Quick" and must NOT
                count as a match.

All mutation is in-memory; no file is written.

Usage:
  py tools/contracts/tests_soul_identity_negative.py <arz> [sv098i_Text_EN.arc] [mod_Text.arc]
Exit 0 = every assertion held; 1 = the gate failed to fire (or mis-fired).
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent))

from arz_patcher import ArzDatabase, DATA_TYPE_FLOAT  # noqa: E402
from audit_soul_identity import load_arc_tags  # noqa: E402

# The planted reproduction: a REAL mismatch from the 2026-07-27 audit.
_T2_RECORD = r"records\creature\monster\ratman\hero_wheedletongue_41.dbr"
_T2_MONSTER = "Fesil the Quick"
_T2_SOUL = "Wheedletongue the Magnificent"

# A family with NO identity-owning carrier -> must never be flagged (orphan safety).
_T4_FAMILY = 'satyrfiremagi'

_CHANCE = 'chanceToEquipFinger2'
_LOOT = 'lootFinger2Item1'

_fails = []


def check(name, ok, detail=''):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ''))
    if not ok:
        _fails.append(name)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    arz = argv[1]
    repo = _HERE.parent.parent
    sv_text = Path(argv[2]) if len(argv) > 2 else (
        repo / 'upstream' / 'soulvizier_098i' / 'Resources' / 'Text_EN.arc')
    tagmap = load_arc_tags(sv_text)
    if len(argv) > 3:
        load_arc_tags(argv[3], tagmap)
    if not tagmap:
        print("ERROR: no display-name tags loaded; the gate cannot be tested.",
              file=sys.stderr)
        return 2

    import apply_svc_patches as asp
    asp._SV098I_NAME_TAGS = dict(tagmap)
    from patches import soul_identity as si

    print(f"negative-test: {arz}\n  display-name tags: {len(tagmap)}")
    db = ArzDatabase.from_arz(Path(arz))

    # ── T1: the shipped db is clean ─────────────────────────────────────────
    try:
        si.verify(db, {})
        check("T1 fixed db passes verify()", True)
    except SystemExit as exc:
        check("T1 fixed db passes verify()", False, str(exc)[:400])

    # ── T5: identity is display-name, not filename ──────────────────────────
    check("T5 filename is NOT identity "
          f"('hero_wheedletongue_41' vs {_T2_MONSTER!r})",
          not si.identity_match(_T2_MONSTER, f"{{^F}}{_T2_SOUL} Soul"),
          "a filename-based matcher would call this a match")
    check("T5 the REAL owner still matches its own soul",
          si.identity_match(_T2_SOUL, f"{{^F}}{_T2_SOUL} Soul"))

    # ── T2: re-arm the real mismatch -> verify() must FAIL ──────────────────
    if not db.has_record(_T2_RECORD):
        check(f"T2 planted record present ({_T2_RECORD})", False, "record missing")
    else:
        prev = si._scalar(db.get_field_value(_T2_RECORD, _CHANCE))
        loot = db.get_field_value(_T2_RECORD, _LOOT)
        has_soul = any('soul' in str(s).lower()
                       for s in (loot if isinstance(loot, list) else [loot]))
        check("T2 planted record still carries its (detached) foreign soul loot",
              has_soul, f"{_LOOT}={loot}")
        db.set_field(_T2_RECORD, _CHANCE, 50.0, DATA_TYPE_FLOAT)
        try:
            si.verify(db, {})
            check(f"T2 re-armed {_T2_MONSTER!r} -> verify() FIRES", False,
                  "gate did NOT fire on a real, reproduced mismatch")
        except SystemExit as exc:
            msg = str(exc)
            check(f"T2 re-armed {_T2_MONSTER!r} -> verify() FIRES", True)
            check("T2 the failure names the offending record",
                  _T2_RECORD.lower() in msg.lower())
            check("T2 the failure names the rightful owner",
                  _T2_SOUL.lower() in msg.lower())
        db.set_field(_T2_RECORD, _CHANCE, float(prev or 0.0), DATA_TYPE_FLOAT)

    # ── T3: a SYNTHETIC cross-wire is caught as well ────────────────────────
    thieves, families = si.find_identity_thieves(db, {})
    check("T3 precondition: db clean before planting", not thieves)
    donor_fam = next((f for f, e in families.items()
                      if e['matched'] and len(e['matched']) >= 1), None)
    victim = next((r for f, e in families.items() if f != donor_fam
                   for r, _d in e['matched']), None)
    if donor_fam and victim:
        donor_soul = sorted(families[donor_fam]['souls'])[0]
        keep_loot = db.get_field_value(victim, _LOOT)
        db.set_field(victim, _LOOT, donor_soul)
        try:
            si.verify(db, {})
            check("T3 synthetic cross-wire -> verify() FIRES", False,
                  f"planted {donor_fam!r} soul on {victim} undetected")
        except SystemExit:
            check("T3 synthetic cross-wire -> verify() FIRES", True,
                  f"planted {donor_fam!r} soul on {victim}")
        db.set_field(victim, _LOOT, keep_loot)
    else:
        check("T3 synthetic cross-wire", False, "no donor/victim pair available")

    # ── T4: archetype families must NOT be flagged (orphan safety) ──────────
    thieves, families = si.find_identity_thieves(db, {})
    check("T4 db clean again after un-planting", not thieves)
    fam = families.get(_T4_FAMILY)
    if fam is None:
        check(f"T4 archetype family {_T4_FAMILY!r} present", False, "family absent")
    else:
        check(f"T4 archetype family {_T4_FAMILY!r} has NO identity-owning carrier",
              not fam['matched'],
              f"{len(fam['unmatched'])} named unique(s) carry it")
        check(f"T4 archetype family {_T4_FAMILY!r} keeps a LIVE carrier "
              f"(soul stays obtainable)",
              any(si._chance_of(db, r) > 0 for r, _d in fam['unmatched']))

    print(f"\n{'FAILED: ' + ', '.join(_fails) if _fails else 'ALL ASSERTIONS HELD'}")
    return 1 if _fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
