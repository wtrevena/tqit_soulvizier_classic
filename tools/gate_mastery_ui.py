"""gate_mastery_ui - PERMANENT fail-loud gate for the mastery/skill-tree UI laws.

Will's mandate (2026-07-14, verbatim laws):
  TIER LAW      - "every skill is on the right level vertically on the page based
                  on how many points is needed for it": a button's row
                  (bitmapPositionY) must equal its skill's skillTier.
  CONNECTOR LAW - "the only skills that should be connected together should be
                  ones that genuinely augment one another": a drawn connector
                  (skillConnectionOn) must land on a genuine augment relative, and
                  no foreign family member may be trapped inside another family's
                  column span (INTERLEAVE) nor a modifier stranded out of its
                  base's column (OFFCOL).
Plus the layout hygiene the same audit proved: on-grid, no duplicate cell, icon
resolves, no duplicate/empty display-name, select-screen tag wiring intact.

This gate re-uses the EXACT analysis functions of tools/audit_mastery_ui.py (one
source of truth for the math, so gate and audit never drift), keys every finding
to a STABLE id, and FAILS LOUD (exit 1) on any finding not listed in the waiver
manifest tools/mastery_ui_waivers.json. The waiver manifest is the honest ledger
of the known-deferred defects (each Will-design-decision / graft-broken-skillTier
/ golden-trade-off carries a justification string), mirroring the A7 golden gate's
owner_approved_overrides pattern: a NEW or regressed defect can never ship, while
the documented backlog is tracked, not silently blocking the build.

Wired into the DB build gate battery (build_svc_database.py, after the A7 golden
guard) AND runnable standalone:

  py tools/gate_mastery_ui.py [gold_arz] [base_arz] [--text Text.arc] [--waivers f]
  py tools/gate_mastery_ui.py --list          # print every current finding + key
  py tools/gate_mastery_ui.py --stale-ok      # do not fail on stale waivers

exit codes: 0 = PASS (every finding waived), 1 = unwaived finding (or stale waiver
without --stale-ok), 2 = usage/load error.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(_TOOLS))

# ONE source of truth for the UI math: reuse the audit module's helpers verbatim.
import audit_mastery_ui as A  # noqa: E402
from arc_patcher import ArcArchive  # noqa: E402

WAIVERS_DEFAULT = _TOOLS / "mastery_ui_waivers.json"

# Select-mastery screen tag families the engine keeps FIRST-definition-wins
# (B-MASTERY-LABEL-1). The text-side dup gate (build_text_arc.check_duplicate_tags)
# is the primary guard; this gate cross-checks the shipped Text.arc when given one.
_SELECT_TAGS = [
    "tagMasteryBrief0%d", "tagMasteryTitle0%d", "tagMasteryDescription0%d",
    "tagSkillName0%d0",
]


def analyze(gold):
    """Return a flat list of (key, category, message) for EVERY law/hygiene
    finding across masteries 1-9, reproducing audit_mastery_ui's checks with a
    stable key per finding. Key form: '<CATEGORY>::m<slot>::<id>'."""
    findings = []

    def add(slot, category, ident, msg):
        findings.append(("%s::m%d::%s" % (category, slot, ident), category, msg))

    for slot in range(1, 10):
        nodes, cells = A.collect(gold, slot)
        canon_present = {}
        for bn in nodes:
            canon_present[A.canon(bn)] = bn
        roots = {bn: A.family_root(bn, nodes, canon_present) for bn in nodes}

        # GRID + DUPCELL + TIER + ICON + NAME
        disp_seen = defaultdict(list)
        for bn, n in nodes.items():
            x, y = n["x"], n["y"]
            if x not in A.COLS or y not in A.ROW_TIER:
                add(slot, "GRID", bn, "%s at off-grid (%d,%d) slot%02d" % (bn, x, y, n["slot"]))
            rt = A.ROW_TIER.get(y)
            try:
                st = int(n["tier"]) if n["tier"] not in (None, "") else None
            except (TypeError, ValueError):
                st = None
            if st and rt and st != rt:
                add(slot, "TIER", bn, "%s on row%s(y=%d) but skillTier=%d" % (bn, rt, y, st))
            ic = str(n["icon"] or "")
            low = ic.lower()
            if n["srec"] is None:
                add(slot, "ICON", bn, "%s -> skillName record MISSING (%s)" % (bn, n["sn"]))
            elif ic == "":
                add(slot, "ICON", bn, "%s has EMPTY skillUpBitmapName" % bn)
            elif low.startswith("_drx_textures") or low.startswith("skillspanel"):
                add(slot, "ICON", bn, "%s icon unresolvable: %s" % (bn, ic))
            d = n["disp"]
            if n["srec"] is not None:
                if d in (None, ""):
                    add(slot, "NAME", bn, "%s has EMPTY skillDisplayName" % bn)
                else:
                    disp_seen[str(d)].append(bn)
        for xy, bns in cells.items():
            if len(bns) > 1:
                add(slot, "DUPCELL", "%d_%d" % (xy[0], xy[1]),
                    "cell %s occupied by %d: %s" % (xy, len(bns), ", ".join(sorted(bns))))
        for tag, bns in disp_seen.items():
            if len(bns) > 1:
                add(slot, "DUPNAME", tag, "display tag %s shared by: %s" % (tag, ", ".join(sorted(bns))))

        # CONNECTOR spurious targets
        bycol = defaultdict(list)
        for bn, n in nodes.items():
            bycol[n["x"]].append((n["y"], bn))
        for x in bycol:
            bycol[x].sort()
        for bn, n in nodes.items():
            fl = A.conn_flag(n)
            if fl == "C":
                col = bycol[n["x"]]
                above = [(yy, b) for (yy, b) in col if yy < n["y"]]
                if above:
                    ay, ab = max(above)
                    if not A.genuine(ab, bn, roots, nodes):
                        add(slot, "CONN", bn,
                            "%s [C] connector points UP at unrelated %s (y %d->%d)" % (bn, ab, n["y"], ay))
            elif fl == "R":
                rc = bycol.get(n["x"] + 100, [])
                rel = [b for (yy, b) in rc if A.genuine(b, bn, roots, nodes)]
                if not rel:
                    add(slot, "CONN", bn,
                        "%s [R] side-connector has NO relative in column %d" % (bn, n["x"] + 100))

        # INTERLEAVE (trapped foreign family member)
        for x in bycol:
            fam_ys = defaultdict(list)
            for (yy, bn) in bycol[x]:
                fam_ys[roots[bn]].append(yy)
            spans = {r: (min(ys), max(ys)) for r, ys in fam_ys.items() if len(ys) >= 2}
            for (yy, bn) in bycol[x]:
                r = roots[bn]
                for orr, (lo, hi) in spans.items():
                    if orr != r and lo < yy < hi:
                        add(slot, "INTERLEAVE", bn,
                            "%s (fam %s) trapped inside %s span (col %d, y=%d in %d..%d)"
                            % (bn, r, orr, x, yy, lo, hi))
                        break

        # OFFCOL (modifier base present but different column)
        for bn, n in nodes.items():
            r = roots[bn]
            if r != bn and r in nodes and nodes[r]["x"] != n["x"]:
                sev = " (HAS CONNECTOR)" if A.conn_flag(n) != "." else ""
                add(slot, "OFFCOL", bn,
                    "%s (col %d) base %s in col %d%s" % (bn, n["x"], r, nodes[r]["x"], sev))

    return findings


def check_select_tags(text_path):
    """Cross-check the shipped Text.arc: each select-screen tag family
    (tagMasteryBrief0N/Title0N/Description0N/SkillName0N0) must have a single
    CONFLICTING-value-free definition (engine keeps first; a 2nd conflicting
    def = the Rogue-label class). Returns list of (key, category, message)."""
    out = []
    arc = ArcArchive.from_file(Path(text_path))
    defs = defaultdict(list)   # tag -> list of values (any file)
    want = set()
    for slot in range(1, 10):
        for pat in _SELECT_TAGS:
            want.add((pat % slot).lower())
    for entry in arc.entries:
        name = (getattr(entry, "name", "") or "")
        if not name.lower().endswith(".txt"):
            continue
        txt = arc.get_text(name)
        if txt is None:
            continue
        for line in txt.splitlines():
            line = line.strip().lstrip("﻿")
            if not line or line.startswith("//") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            kl = k.strip().lower()
            if kl in want:
                defs[k.strip()].append(v)
    for tag, vals in defs.items():
        if len(set(vals)) > 1:
            out.append(("SELECT::%s" % tag, "SELECT",
                        "select-screen tag %s has %d CONFLICTING definitions: %r"
                        % (tag, len(set(vals)), sorted(set(vals)))))
    return out


def load_waivers(path):
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    # accept either {"waivers": {...}} or a bare {...}
    return data.get("waivers", data) if isinstance(data, dict) else {}


def validate(gold_arz, base_arz=None, text_path=None, waivers_path=WAIVERS_DEFAULT,
             stale_ok=False, list_only=False):
    print("=" * 72)
    print("MASTERY/SKILL-TREE UI LAW GATE (TIER + CONNECTOR + layout hygiene)")
    print("  arz     : %s" % gold_arz)
    print("  text    : %s" % (text_path or "(none - select-tag cross-check SKIPPED)"))
    print("  waivers : %s" % waivers_path)
    gold = A.DB(Path(gold_arz))
    findings = analyze(gold)
    if text_path:
        findings += check_select_tags(text_path)

    if list_only:
        by_cat = defaultdict(list)
        for key, cat, msg in findings:
            by_cat[cat].append((key, msg))
        for cat in sorted(by_cat):
            print("\n[%s] %d" % (cat, len(by_cat[cat])))
            for key, msg in sorted(by_cat[cat]):
                print("  %-52s %s" % (key, msg))
        print("\nTOTAL findings: %d" % len(findings))
        return 0

    waivers = load_waivers(waivers_path)
    found_keys = {k for k, _, _ in findings}
    hard = [(k, c, m) for k, c, m in findings if k not in waivers]
    waived = [(k, c, m) for k, c, m in findings if k in waivers]
    stale = sorted(set(waivers) - found_keys)

    by_cat = defaultdict(int)
    for k, c, m in findings:
        by_cat[c] += 1
    print("\n  findings by category: " + ", ".join("%s=%d" % (c, by_cat[c]) for c in sorted(by_cat)))
    print("  total=%d  waived=%d  unwaived=%d  stale-waivers=%d"
          % (len(findings), len(waived), len(hard), len(stale)))

    for k in stale:
        print("  STALE WAIVER (no longer a finding - fixed? remove it): %s" % k)

    if hard:
        print("\n  UNWAIVED FINDINGS (these BLOCK the build):")
        for k, c, m in sorted(hard):
            print("    [%s] %s\n        %s" % (c, k, m))
        print("\nRESULT: FAIL - %d unwaived mastery-UI law violation(s). Either fix "
              "the placement (tools/patches/mastery_ui_vet.py) so the finding "
              "disappears, or - only with Will's design sign-off - add the exact "
              "key above to tools/mastery_ui_waivers.json with a justification."
              % len(hard))
        return 1

    if stale and not stale_ok:
        print("\nRESULT: FAIL - %d stale waiver(s): a waived key is no longer a "
              "finding (a fix landed). Remove it from the manifest so the gate "
              "stays honest (or pass --stale-ok)." % len(stale))
        return 1

    print("\nRESULT: PASS - every mastery-UI finding is covered by a justified "
          "waiver (%d waived). No new/unwaived TIER or CONNECTOR defect can ship."
          % len(waived))
    return 0


def main(argv):
    args = [a for a in argv[1:]]
    text_path = None
    waivers = WAIVERS_DEFAULT
    stale_ok = "--stale-ok" in args
    list_only = "--list" in args
    args = [a for a in args if a not in ("--stale-ok", "--list")]
    if "--text" in args:
        i = args.index("--text")
        text_path = args[i + 1]
        del args[i:i + 2]
    if "--waivers" in args:
        i = args.index("--waivers")
        waivers = args[i + 1]
        del args[i:i + 2]
    gold = args[0] if len(args) > 0 else str(A.DEF_GOLD)
    base = args[1] if len(args) > 1 else str(A.DEF_BASE)
    try:
        return validate(gold, base, text_path, waivers, stale_ok, list_only)
    except FileNotFoundError as e:
        print("gate_mastery_ui: input not found: %s" % e)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
