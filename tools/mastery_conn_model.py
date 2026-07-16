r"""mastery_conn_model - the geometry->connector model (ONE source of truth).

Decoded ground truth (tools/tex_decode.py + the base/golden arz, 2026-07-14):
a skill-tree connector is NOT baked art; it is a runtime vertical BAR encoded as a
PARALLEL PAIR of texture arrays on the base skill record:
    skillConnectionOn  = [Bottom, <mid>*, Top]   (drawn when the family is invested)
    skillConnectionOff = [Bottom, <mid>*, Top]   (dimmed, drawn in the un-invested/
                                                  planning tree - the DEFAULT view)
Both arrays are ALWAYS the SAME LENGTH.  The length equals the number of tier rows
the bar spans, from the family BASE (lowest tier, bottom of screen, largest Y) UP to
the family's TOP member (highest tier, smallest Y), inclusive:  len = top_row -
base_row + 1.  Tiles bottom->top:
    row == base : SkillBarBottom{On,Off}01.tex
    row == top  : SkillBarTop{On,Off}01.tex
    intermediate row that is ANOTHER member of the SAME family : SkillBarConnect{On,Off}01.tex
    intermediate row that is empty or a FOREIGN skill          : SkillBarMiddle{On,Off}01.tex
A skill that is a leaf modifier / standalone / single-in-column family carries NO bar
(both arrays empty; some vanilla skills keep a single vestigial [SkillBarBottomOff01]
- an attested "no connector" state, connOff length <= 1).

This exactly reproduces vanilla (validated: Warfare onslaught/battlerage/battlestandard/
warwind/warhorn, Hunting marksmanship/monsterlure/woodlore, ... 0 unexplained mismatch
on families the mod did not disturb).  So AFTER any position reflow the correct
connectors are a pure FUNCTION of the final geometry + family structure - which is what
`expected_connectors()` computes and the reflow writes and the gate enforces.  This
closes the round-1 vet HIGH (single-string skillConnectionOn, connOff left stale ->
spurious dimmed bars survive + new bars under-draw) and MEDIUM (gate blind to connOff).

Reuses tools/audit_mastery_ui.py's node/family/genuine helpers (same source of truth as
gate_mastery_ui.py + build_connection_maps.py).  Read-only here; the writer is
mastery_ui_vet.apply / hunting_occult_ui.apply via rebuild_into().

Usage:
  py tools/mastery_conn_model.py [gold_arz] [base_arz]   # validate rule vs actual arrays
  py tools/mastery_conn_model.py --base                  # validate on the base game only
"""
import sys
from collections import defaultdict
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(_TOOLS))
import audit_mastery_ui as A  # noqa: E402

# --- connector tile textures (full field-value paths, exactly as stored in the arz) --
_PFX = r"InGameUI\Icons\Skills\SkillBars"
BOTTOM_ON = _PFX + r"\SkillBarBottomOn01.tex"
MIDDLE_ON = _PFX + r"\SkillBarMiddleOn01.tex"
CONNECT_ON = _PFX + r"\SkillBarConnectOn01.tex"
TOP_ON = _PFX + r"\SkillBarTopOn01.tex"
BOTTOM_OFF = _PFX + r"\SkillBarBottomOff01.tex"
MIDDLE_OFF = _PFX + r"\SkillBarMiddleOff01.tex"
CONNECT_OFF = _PFX + r"\SkillBarConnectOff01.tex"
TOP_OFF = _PFX + r"\SkillBarTopOff01.tex"

# tier-row Y grid, largest Y (row1, bottom of screen) first
ROW_YS = sorted(A.ROW_TIER.keys(), reverse=True)   # [403,341,279,217,155,93,31]

STR_DTYPE = 2   # arz_patcher.DATA_TYPE_STRING (connOn/connOff are string arrays)


def _tiles(base_y, top_y, occupied_ys):
    """Bar tile arrays (on, off) spanning base_y (bottom) up to top_y (top).

    Ground-truthed against vanilla (base game, 2 independent multi-gap bars -
    Warfare dualweapontraining->dualwieldtechnique_tumult and Occult
    envenomweapon->envenomweapon_delirium): an intermediate tile is CONNECT iff
    that row is OCCUPIED BY ANY SKILL IN THE COLUMN (family or not - e.g.
    envenomweapon's bar draws a CONNECT tile over the foreign, unrelated
    toxindistillation sitting mid-span), and MIDDLE iff the row is truly EMPTY.
    Tile choice is pure column-occupancy geometry; only the bar's base/top
    ENDPOINTS are family-scoped (computed by the caller)."""
    seq = [y for y in ROW_YS if top_y <= y <= base_y]   # descending Y
    on, off = [], []
    last = len(seq) - 1
    for i, y in enumerate(seq):
        if i == 0:
            on.append(BOTTOM_ON); off.append(BOTTOM_OFF)
        elif i == last:
            on.append(TOP_ON); off.append(TOP_OFF)
        elif y in occupied_ys:
            on.append(CONNECT_ON); off.append(CONNECT_OFF)
        else:
            on.append(MIDDLE_ON); off.append(MIDDLE_OFF)
    return on, off


def expected_connectors(nodes, roots):
    """Given a mastery's nodes (basename->node dict from A.collect) and family roots,
    return dict basename -> (skillConnectionOn_list, skillConnectionOff_list).

    Only family BASES that have >=1 same-column member above them get a bar; every
    other node maps to ([], []) (= no bar). The bar's SPAN (base row -> top row) is
    family-scoped (the family's own lowest/highest member); the tiles WITHIN that
    span are occupancy-scoped (see _tiles) - so a foreign skill sitting mid-span
    still earns a CONNECT tile (ground-truthed on envenomweapon, see _tiles doc).
    Pure function of geometry + family."""
    out = {bn: ([], []) for bn in nodes}
    bycol = defaultdict(list)
    for bn, n in nodes.items():
        bycol[n["x"]].append((n["y"], bn))
    for x, members in bycol.items():
        occupied_ys = {y for (y, _) in members}
        fam = defaultdict(list)
        for (y, bn) in members:
            fam[roots[bn]].append((y, bn))
        for root, mem in fam.items():
            if len(mem) < 2:
                continue
            mem.sort(key=lambda t: -t[0])       # base (largest Y) first
            base_y, base_bn = mem[0]
            top_y, _top_bn = mem[-1]
            if top_y == base_y:                  # all on one row (dup-cell); no bar
                continue
            on, off = _tiles(base_y, top_y, occupied_ys)
            out[base_bn] = (on, off)
    return out


def _roots_for(db, slot):
    nodes, _cells = A.collect(db, slot)
    canon_present = {A.canon(bn): bn for bn in nodes}
    roots = {bn: A.family_root(bn, nodes, canon_present) for bn in nodes}
    return nodes, roots


def _as_list(v):
    return v if isinstance(v, list) else ([v] if v else [])


def _has_baseline_bar(db, nodes, member_bns):
    """A family HAD an authored connector iff any of its members currently carries a
    real bar (skillConnectionOn length >= 2).  Connector EXISTENCE is authored (vanilla
    leaves many genuine base->modifier pairs unconnected, e.g. Hunting studyprey); only
    the bar SHAPE is geometric.  So we preserve existence and only reshape."""
    for bn in member_bns:
        srec = db.resolve(nodes[bn]["sn"]) if nodes[bn]["sn"] else None
        if srec and len(_as_list(db.db.get_field_value(srec, "skillConnectionOn"))) >= 2:
            return True
    return False


def _set_conn(db, srec, on_list, off_list, bn, changed, log):
    cur_on = _as_list(db.db.get_field_value(srec, "skillConnectionOn"))
    cur_off = _as_list(db.db.get_field_value(srec, "skillConnectionOff"))
    if cur_on != on_list:
        db.db.set_field(srec, "skillConnectionOn", list(on_list), STR_DTYPE)
        changed.append((bn, "skillConnectionOn"))
    if cur_off != off_list:
        db.db.set_field(srec, "skillConnectionOff", list(off_list), STR_DTYPE)
        changed.append((bn, "skillConnectionOff"))
    if log and (cur_on != on_list or cur_off != off_list):
        log("    conn %-40s -> %s" % (bn, ("bar[%d]" % len(on_list)) if on_list else "DROP"))


def rebuild_into(db, slot, seed_skills=(), drops=(), log=None):
    """Recompute geometry-correct skillConnectionOn/Off for the families the reflow
    touched in mastery `slot`.  `db` is an audit_mastery_ui.DB wrapper (positions must
    already be moved; connOn/Off still baseline).

    seed_skills: basenames whose FAMILY should be reshaped (any moved skill + any
        connector-edited skill).  For each such family that HAD an authored bar, put a
        geometry-shaped bar on the family BASE (lowest row in its column) and CLEAR the
        bar on every other member.  Families with no baseline bar are left untouched
        (so no connector is spuriously added, e.g. studyprey).
    drops: basenames to force-clear regardless (standalone/leaf skills carrying a
        SPURIOUS bar that no family reshape would remove - the audit's CONN drops).

    Only skillConnectionOn/Off (STRING arrays) change; never a gameplay field.  Returns
    the list of (basename, field) pairs changed.  Parity (len(on)==len(off)) holds by
    construction.  This is the single writer the gate re-derives against."""
    nodes, roots = _roots_for(db, slot)
    exp = expected_connectors(nodes, roots)
    changed = []
    seed_roots = {roots[s] for s in seed_skills if s in roots}

    # 1) reshape every touched family that had an authored bar.
    fam_members = defaultdict(list)
    for bn in nodes:
        fam_members[roots[bn]].append(bn)
    for root in seed_roots:
        members = fam_members[root]
        if not _has_baseline_bar(db, nodes, members):
            continue                    # authored no-bar family: leave alone
        # base of the bar = the family member carrying the geometry bar (its column's
        # lowest-row member); expected_connectors already keys the bar to that node.
        base_bn = next((bn for bn in members if exp[bn][0]), None)
        for bn in members:
            srec = db.resolve(nodes[bn]["sn"]) if nodes[bn]["sn"] else None
            if not srec:
                continue
            want_on, want_off = exp[bn] if bn == base_bn else ([], [])
            if not want_on and len(_as_list(db.db.get_field_value(srec, "skillConnectionOn"))) < 2 \
                    and len(_as_list(db.db.get_field_value(srec, "skillConnectionOff"))) <= 1:
                continue                # already a clean no-bar member: no diff
            _set_conn(db, srec, want_on, want_off, bn, changed, log)

    # 2) force-drop explicit standalone/leaf spurious bars.
    for bn in drops:
        if bn not in nodes:
            continue
        srec = db.resolve(nodes[bn]["sn"]) if nodes[bn]["sn"] else None
        if not srec:
            continue
        if len(_as_list(db.db.get_field_value(srec, "skillConnectionOn"))) >= 2 or \
                len(_as_list(db.db.get_field_value(srec, "skillConnectionOff"))) >= 2:
            _set_conn(db, srec, [], [], bn, changed, log)
    return changed


# -------------------------------------------------- gate defects (parity + span) -----
# The two invariants a connector must satisfy, both attested 107/107 in vanilla+golden:
#   PARITY  len(skillConnectionOn) == len(skillConnectionOff), OR both <= 1 (the vanilla
#           "no bar" state - connOff can keep a single vestigial [SkillBarBottomOff01]).
#           The round-1 reflow broke this: it cleared connOn but left connOff at 2-7
#           stale elements (dimmed bar survives), or set a single-element connOn against
#           a multi-element connOff (new bar under-draws).
#   SPAN    a drawn bar's TOP tile must land EXACTLY on an occupied cell (a real skill):
#           straight [C] bar of length L on (x,y) tops out at y-(L-1)*62 in the SAME
#           column; a '_right' [R] bar tops out in column x+100. A bar that lands on an
#           empty cell under-draws (too short) or over-draws (too long / points at void).
# Both are pure geometry (no family assumption) so they never false-positive on the
# hand-tuned summon->generic-pet-modifier connection (drx_summon_shadow_stalker) that
# the name detector cannot see - its 2-tile bar still lands on an occupied cell.
_SPACING = 62


def _is_right(lst):
    return any("_right" in str(t).lower() for t in (lst or []))


def find_defects(db, slots=range(1, 10)):
    """Return [(slot, category, ident, message)] for CONNPARITY + CONNSPAN violations
    across the given masteries. Pure geometry; reuses A.collect for positions. This is
    the connOff/under-draw guard the round-1 vet asked for (its MEDIUM: the gate was
    blind to skillConnectionOff). Zero findings on vanilla + a correct reflow."""
    out = []
    for slot in slots:
        nodes, _cells = A.collect(db, slot)
        occupied = {(n["x"], n["y"]) for n in nodes.values()}
        for bn, n in nodes.items():
            sn = n["sn"]
            on = _as_list(db.db.get_field_value(db.resolve(sn), "skillConnectionOn")) if sn else []
            off = _as_list(db.db.get_field_value(db.resolve(sn), "skillConnectionOff")) if sn else []
            lon, loff = len(on), len(off)
            # PARITY: a real bar must have matched on/off; "no bar" = both <= 1.
            if lon != loff and not (lon <= 1 and loff <= 1):
                out.append((slot, "CONNPARITY", bn,
                            "%s skillConnectionOn len=%d != skillConnectionOff len=%d "
                            "(a bar must set BOTH arrays equal-length; 'no bar' = both<=1)"
                            % (bn, lon, loff)))
            # SPAN: a drawn bar (>=2 tiles) must top out on an occupied cell.
            if lon >= 2:
                col = n["x"] + (100 if _is_right(on) else 0)
                top_y = n["y"] - (lon - 1) * _SPACING
                if (col, top_y) not in occupied:
                    out.append((slot, "CONNSPAN", bn,
                                "%s %s bar len=%d tops out at (col %d, y=%d) which is EMPTY "
                                "(under/over-draws - must land on a skill)"
                                % (bn, "[R]" if _is_right(on) else "[C]", lon, col, top_y)))
    return out


# ---------------------------------------------------------------- validation ---------
def _basenames(lst):
    return [str(x).rsplit("\\", 1)[-1].lower() for x in (lst or [])]


def validate(db, label):
    """Existence-guarded, case-insensitive proof that the geometry model reproduces the
    authored connectors: for every skill that CARRIES a bar (connOn >= 2), the model's
    shape must match exactly. Families the author left UNCONNECTED (vanilla studyprey /
    darkcovenant / heartofoak ...) are skipped - connector EXISTENCE is authored, only
    the bar SHAPE is geometric (this is why rebuild_into preserves existence)."""
    print("\n=== connector-model validation: %s ===" % label)
    total = checked = mism = 0
    for slot in range(1, 10):
        nodes, roots = _roots_for(db, slot)
        exp = expected_connectors(nodes, roots)
        for bn, n in nodes.items():
            sn = n["sn"]
            cur_on = _as_list(db.db.get_field_value(db.resolve(sn), "skillConnectionOn") if sn else None)
            cur_off = _as_list(db.db.get_field_value(db.resolve(sn), "skillConnectionOff") if sn else None)
            total += 1
            if len(cur_on) < 2:
                continue                       # authored no-bar member: nothing to prove
            checked += 1
            want_on, want_off = exp[bn]
            if _basenames(cur_on) != _basenames(want_on) or _basenames(cur_off) != _basenames(want_off):
                mism += 1
                print("  m%d %-38s SHAPE mismatch:\n      actual on=%s off=%s\n      model  on=%s off=%s"
                      % (slot, bn, _basenames(cur_on), _basenames(cur_off),
                         _basenames(want_on), _basenames(want_off)))
    print("  %d nodes, %d carry a bar, %d shape-mismatch vs the geometry model "
          "(0 = the model reproduces every authored bar exactly)" % (total, checked, mism))
    return mism


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if "--base" in argv:
        db = A.DB(A.DEF_BASE)
        validate(db, "BASE game (vanilla ground truth)")
        d = find_defects(db)
        print("  find_defects on BASE: %d (expect 0)" % len(d))
        for s, c, i, m in d:
            print("    m%d [%s] %s" % (s, c, m))
        return 0
    gold = Path(args[0]) if len(args) > 0 else A.DEF_GOLD
    base = Path(args[1]) if len(args) > 1 else A.DEF_BASE
    validate(A.DB(base), "BASE game (vanilla ground truth)")
    gdb = A.DB(gold)
    validate(gdb, "GOLDEN build40 (pre-reflow; mismatches = the bugs to fix)")
    d = find_defects(gdb)
    print("\n  find_defects on GOLDEN: %d parity/span violations" % len(d))
    for s, c, i, m in d:
        print("    m%d [%s] %s" % (s, c, m))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
