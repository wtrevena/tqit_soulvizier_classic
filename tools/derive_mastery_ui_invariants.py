"""Derive + prove the mastery/skill-tree UI invariants from the BASE-GAME arz.

Read-only. No game, no heavy build. Reproduces every number cited in
docs/reports/mastery_ui_invariants.md:

  TIER LAW      - Y row <-> skillTier ladder (Y = 465 - 62*tier); 0 violations across 9 masteries.
  GRID          - fixed 6x6 grid X{128..628}/Y{403..93}; mastery button off-grid at (29,459).
  CONNECTOR LAW - visual connection is columnar co-placement (modifier shares base column),
                  NOT skillDependancy (a gameplay-only prereq); 66/66 vanilla modifiers column-aligned.
  SELECT SCREEN - masterypane.dbr slot wiring (tagMasteryBrief0N label / tagMasteryDescription0N desc /
                  <Class>Button*01.tex icon) vs tree pane (panectrl skillTabTitle=tagMasteryTitle0N).

Usage:
  py tools/derive_mastery_ui_invariants.py [path\\to\\base\\database.arz]
Exit code 0 iff all invariants hold (0 tier violations, 0 off-column modifiers, 0 off-grid skills).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase

DEFAULT_BASE = Path(r"C:\Program Files (x86)\Steam\steamapps\common"
                    r"\Titan Quest Anniversary Edition\Database\database.arz")

# The proven vanilla grid.
ROW_TIER = {403: 1, 341: 2, 279: 3, 217: 4, 155: 5, 93: 6}   # Y -> tier
GRID_X = {128, 228, 328, 428, 528, 628}
MASTERY_BTN_XY = (29, 459)   # the off-grid mastery node (tier 0)

# slot -> (ui folder, class label). 1-8 classic; 9 = Dream (xpack).
MASTERIES = [
    (1, "records\\ingameui\\player skills\\mastery 1\\", "Warfare"),
    (2, "records\\ingameui\\player skills\\mastery 2\\", "Defense"),
    (3, "records\\ingameui\\player skills\\mastery 3\\", "Earth"),
    (4, "records\\ingameui\\player skills\\mastery 4\\", "Storm"),
    (5, "records\\ingameui\\player skills\\mastery 5\\", "Rogue"),
    (6, "records\\ingameui\\player skills\\mastery 6\\", "Hunting"),
    (7, "records\\ingameui\\player skills\\mastery 7\\", "Spirit"),
    (8, "records\\ingameui\\player skills\\mastery 8\\", "Nature"),
    (9, "records\\xpack\\ui\\skills\\mastery 9\\", "Dream"),
]


def main():
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BASE
    db = ArzDatabase.from_arz(base)
    idx = {n.lower().replace('/', '\\'): n for n in db.record_names()}

    def resolve(rec):
        return idx.get(rec.lower().replace('/', '\\')) if rec else None

    def first(v):
        return v[0] if isinstance(v, list) else v

    def base_of(p):
        if not p:
            return None
        b = p.rsplit('\\', 1)[-1]
        return b[:-4] if b.lower().endswith('.dbr') else b

    tier_checked = tier_viol = 0
    grid_viol = 0
    col_same = col_diff = 0
    col_diffs = []

    for slot, folder, cls in MASTERIES:
        pos = {}   # skill-basename(lower) -> (x, y, tier, disp)
        for i in range(1, 21):
            rec = resolve(folder + "skill%02d.dbr" % i)
            if rec is None:
                continue
            x = first(db.get_field_value(rec, "bitmapPositionX"))
            y = first(db.get_field_value(rec, "bitmapPositionY"))
            sn = first(db.get_field_value(rec, "skillName"))
            srec = resolve(sn) if sn else None
            st = first(db.get_field_value(srec, "skillTier")) if srec else None
            disp = base_of(sn)
            if disp:
                pos[disp.lower()] = (x, y, st, disp)
            # GRID
            if x not in GRID_X or y not in ROW_TIER:
                grid_viol += 1
                print("  GRID off-grid: m%d skill%02d (%s) X=%s Y=%s" % (slot, i, disp, x, y))
            # TIER
            if st and st > 0:
                tier_checked += 1
                if ROW_TIER.get(y) != st:
                    tier_viol += 1
                    print("  TIER viol: m%d %s Y=%s impliedTier=%s skillTier=%s"
                          % (slot, disp, y, ROW_TIER.get(y), st))
        # CONNECTOR: modifier <base>_<suffix> shares base column
        for b, (x, y, st, disp) in pos.items():
            if '_' not in b:
                continue
            parent = b.rsplit('_', 1)[0]
            while parent and parent not in pos:
                parent = parent.rsplit('_', 1)[0] if '_' in parent else None
            if parent and parent in pos:
                px, py, pst, pdisp = pos[parent]
                if px == x:
                    col_same += 1
                else:
                    col_diff += 1
                    col_diffs.append((slot, disp, x, pdisp, px))

    for slot, disp, x, pdisp, px in col_diffs:
        print("  CONNECTOR off-column: m%d %s(x=%s) base %s(x=%s)" % (slot, disp, x, pdisp, px))

    # SELECT-SCREEN wiring proof (classic pane; slot 1 sampled + list-length checks)
    mp = resolve(r"records\ingameui\player skills\select mastery\masterypane.dbr")
    xmp = resolve(r"records\xpack\ui\skills\select mastery\masterypane.dbr")
    m1text = resolve(r"records\ingameui\player skills\select mastery\mastery1text.dbr")
    brief = db.get_field_value(m1text, "textTag") if m1text else None
    desc_tags = db.get_field_value(mp, "masteryMasterySelectedDescriptionTags") if mp else None
    xbtns = db.get_field_value(xmp, "masteryMasteryButtons") if xmp else None

    print("\n=== MASTERY UI INVARIANTS (base %s) ===" % base.name)
    print("GRID      : X in %s, Y in %s ; mastery btn off-grid at %s"
          % (sorted(GRID_X), sorted(ROW_TIER, reverse=True), MASTERY_BTN_XY))
    print("GRID      : off-grid skill buttons = %d (expect 0)" % grid_viol)
    print("TIER LAW  : Y=465-62*tier ; checked %d skills w/ skillTier ; violations = %d (expect 0)"
          % (tier_checked, tier_viol))
    print("CONNECTOR : modifier<->base same-column %d ; off-column %d (expect 0)"
          % (col_same, col_diff))
    print("CONNECTOR : skillDependancy is a gameplay prereq, NOT the visual link (see report 2b)")
    print("SELECT    : mastery1text.textTag = %r (expect tagMasteryBrief01)" % brief)
    print("SELECT    : masteryMasterySelectedDescriptionTags[0] = %r (expect tagMasteryDescription01)"
          % (first(desc_tags) if desc_tags else None))
    print("SELECT    : xpack masteryMasteryButtons count = %s (expect 9)"
          % (len(xbtns) if isinstance(xbtns, list) else xbtns))

    ok = (grid_viol == 0 and tier_viol == 0 and col_diff == 0
          and brief == "tagMasteryBrief01")
    print("\nRESULT: %s" % ("ALL INVARIANTS HOLD" if ok else "INVARIANT FAILURE"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
