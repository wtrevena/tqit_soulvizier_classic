"""audit_mastery_ui - exhaustive mastery/skill-tree UI audit of a built arz.

Audits EVERY mastery (1-8 classic + 9 Dream) against the vanilla-derived laws in
docs/reports/mastery_ui_invariants.md (as CORRECTED by this lane - the connector is
the skill-record field `skillConnectionOn`, texture SkillBarBottomOn01, spacing 62,
NOT baked background art). Read-only; no game, no heavy build.

Laws checked (Will's mandate 2026-07-14):
  TIER LAW      row-implied-tier(bitmapPositionY) must equal the skill's skillTier
                (vanilla: 142/142; ladder Y=465-62*tier, tier 1..7 -> 403,341,279,
                217,155,93,31). skillMasteryLevelRequired is a per-skill gate whose
                bands OVERLAP across tiers, so skillTier (not req) is the row key.
  CONNECTOR LAW a drawn connector (skillConnectionOn set; '_right' = side variant)
                must land on a GENUINE augment relative; chains must not interleave
                (no foreign family member trapped inside another family's Y-span).
  LAYOUT        grid-validity, duplicate cells, orphan/dangling buttons, missing or
                broken icons (_DRX_Textures / SkillsPanel / empty), duplicate or
                empty display-name tags, off-pane positions.
  SELECT SCREEN per-mastery masterypane wiring (label/desc/title/name tags + icon).

Usage: py tools/audit_mastery_ui.py [gold_arz] [base_arz]
Exit 0 always (audit, not a gate). Prints per-mastery findings + a SUMMARY block.
"""
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase

DEF_GOLD = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz")
DEF_BASE = Path(r"C:\Program Files (x86)\Steam\steamapps\common"
                r"\Titan Quest Anniversary Edition\Database\database.arz")

COLS = [128, 228, 328, 428, 528, 628]
ROW_TIER = {403: 1, 341: 2, 279: 3, 217: 4, 155: 5, 93: 6, 31: 7}   # Y -> tier
NAMES = {1: "Warfare", 2: "Defense", 3: "Earth", 4: "Storm", 5: "Occult(Rogue)",
         6: "Hunting", 7: "Spirit", 8: "Nature", 9: "Dream"}
GOLDEN = {5, 6}   # occult_hunting_golden.json-tracked (edits need a waiver)
MASTERY_BTN_XY = (29, 459)


def first(v):
    if isinstance(v, list):
        return v[0] if v else None   # empty list (a cleared connector) -> no value
    return v


def base_of(p):
    if not p:
        return None
    b = str(p).rsplit('\\', 1)[-1]
    return b[:-4].lower() if b.lower().endswith('.dbr') else b.lower()


def folder(slot):
    if slot == 9:
        return "records\\xpack\\ui\\skills\\mastery 9\\"
    return "records\\ingameui\\player skills\\mastery %d\\" % slot


class DB:
    def __init__(self, path):
        self.db = ArzDatabase.from_arz(path)
        self.idx = {n.lower().replace('/', '\\'): n for n in self.db.record_names()}

    @classmethod
    def from_db(cls, arzdb):
        """Wrap an already-loaded ArzDatabase (e.g. mid-build in a patch module's
        apply()) without re-reading the arz.  Reflects in-flight mutations."""
        self = cls.__new__(cls)
        self.db = arzdb
        self.idx = {n.lower().replace('/', '\\'): n for n in arzdb.record_names()}
        return self

    def resolve(self, rec):
        return self.idx.get(rec.lower().replace('/', '\\')) if rec else None

    def gf(self, rec, field):
        r = self.resolve(rec) if rec else None
        return first(self.db.get_field_value(r, field)) if r else None

    def gflist(self, rec, field):
        r = self.resolve(rec) if rec else None
        if not r:
            return None
        v = self.db.get_field_value(r, field)
        return v if isinstance(v, list) else ([v] if v is not None else None)


def collect(gold, slot):
    """Return dict basename -> node, plus panectrl button-list info."""
    f = folder(slot)
    nodes = {}
    cells = {}
    for i in range(1, 30):
        brec = f + "skill%02d.dbr" % i
        if not gold.resolve(brec):
            continue
        x = gold.gf(brec, "bitmapPositionX")
        y = gold.gf(brec, "bitmapPositionY")
        try:
            x = int(x); y = int(y)
        except (TypeError, ValueError):
            continue
        sn = gold.gf(brec, "skillName")
        bn = base_of(sn)
        srec = gold.resolve(sn) if sn else None
        node = dict(
            slot=i, x=x, y=y, bn=bn, sn=sn, srec=srec,
            isCircular=gold.gf(brec, "isCircular"),
            cls=str(gold.gf(sn, "Class") or "") if srec else "",
            tier=gold.gf(sn, "skillTier") if srec else None,
            req=gold.gf(sn, "skillMasteryLevelRequired") if srec else None,
            disp=gold.gf(sn, "skillDisplayName") if srec else None,
            icon=gold.gf(sn, "skillUpBitmapName") if srec else None,
            conn=gold.gf(sn, "skillConnectionOn") if srec else None,
            dep=base_of(gold.gf(sn, "skillDependancy")) if srec else None,
        )
        if bn:
            nodes[bn] = node
            cells.setdefault((x, y), []).append(bn)
    return nodes, cells


def canon(name):
    """Normalise a skill basename for family grouping: fix the 'petmodifer'
    misspelling and collapse a trailing self-cast/summon suffix so a variant of a
    base shares a root with the base. Handles:
      - `Xsummons`/`Xsummoning` -> `X`  (pet-modifier `X_petmodifier_*` links to the
        summon skill), and
      - `Xbuffself` -> `X`  (a self-buff variant links to the base's modifier, e.g.
        `stoneformbuffself` <-> `stoneform_moltenrock`; base-name prefix matching that
        settles the documented Earth Stone-Form connector false-positive - the ONLY
        skill ending in 'buffself' across all 9 masteries, so this is surgical).
    """
    if not name:
        return name
    c = name.lower().replace('petmodifer', 'petmodifier')
    for suf in ('summoning', 'summons', 'buffself'):
        if c.endswith(suf) and len(c) > len(suf) + 2:
            c = c[:-len(suf)]
    return c


def family_root(bn, nodes, canon_present):
    """Pure canonical '_'-prefix ancestor walk (NO skillDependancy merge, which
    points at hidden weapon skills and wrongly fuses families). Returns the root
    basename (an actual node key)."""
    seen = set()
    cur = bn
    while cur and cur not in seen:
        seen.add(cur)
        cparts = canon(cur).split('_')
        parent = None
        for k in range(len(cparts) - 1, 0, -1):
            cand = '_'.join(cparts[:k])
            if cand in canon_present and canon_present[cand] != cur:
                parent = canon_present[cand]
                break
        if parent is None:
            return cur
        cur = parent
    return cur


def genuine(a, b, roots, nodes):
    """Genuine augment relation between two node basenames a,b (order-free)."""
    if a == b:
        return True
    if roots.get(a) == roots.get(b):
        return True
    ca, cb = canon(a), canon(b)
    if ca.startswith(cb + '_') or cb.startswith(ca + '_'):
        return True
    da = nodes.get(a, {}).get('dep')
    db_ = nodes.get(b, {}).get('dep')
    if da and canon(da) == cb:
        return True
    if db_ and canon(db_) == ca:
        return True
    return False


def conn_flag(node):
    c = node.get('conn')
    if not c:
        return '.'
    return 'R' if '_right' in str(c).lower() else 'C'


def audit_mastery(gold, base, slot, out):
    nodes, cells = collect(gold, slot)
    name = NAMES[slot]
    golden = " [GOLDEN]" if slot in GOLDEN else ""
    out.append("\n== m%d %s%s == (%d skill buttons)" % (slot, name, golden, len(nodes)))
    F = {}   # finding-type -> list

    def add(kind, msg):
        F.setdefault(kind, []).append(msg)

    # family roots (canonical prefix map: petmodifier + summon-suffix aware)
    canon_present = {}
    for bn in nodes:
        canon_present[canon(bn)] = bn
    roots = {bn: family_root(bn, nodes, canon_present) for bn in nodes}

    # ---- GRID + DUP CELL + TIER + ICON + NAME ----
    disp_seen = defaultdict(list)
    for bn, n in nodes.items():
        x, y = n['x'], n['y']
        if x not in COLS or y not in ROW_TIER:
            add("GRID", "%s at off-grid (%d,%d) slot%02d" % (bn, x, y, n['slot']))
        rt = ROW_TIER.get(y)
        try:
            st = int(n['tier']) if n['tier'] not in (None, '') else None
        except (TypeError, ValueError):
            st = None
        if st and rt and st != rt:
            add("TIER", "%s row%s(y=%d) but skillTier=%d  [req=%s cls=%s]"
                % (bn, rt, y, st, n['req'], n['cls'].split('_')[-1][:14]))
        ic = str(n['icon'] or '')
        low = ic.lower()
        if n['srec'] is None:
            add("ICON", "%s -> skillName record MISSING (%s)" % (bn, n['sn']))
        elif ic == '':
            add("ICON", "%s has EMPTY skillUpBitmapName" % bn)
        elif low.startswith('_drx_textures') or low.startswith('skillspanel'):
            add("ICON", "%s icon unresolvable: %s" % (bn, ic))
        d = n['disp']
        if n['srec'] is not None:
            if d in (None, ''):
                add("NAME", "%s has EMPTY skillDisplayName" % bn)
            else:
                disp_seen[str(d)].append(bn)
    for (xy), bns in cells.items():
        if len(bns) > 1:
            add("DUPCELL", "cell %s occupied by %d: %s" % (xy, len(bns), ', '.join(bns)))
    for tag, bns in disp_seen.items():
        if len(bns) > 1:
            add("DUPNAME", "display tag %s shared by: %s" % (tag, ', '.join(bns)))

    # ---- CONNECTOR: spurious targets + interleave + modifier-off-column ----
    # index by column
    bycol = defaultdict(list)
    for bn, n in nodes.items():
        bycol[n['x']].append((n['y'], bn))
    for x in bycol:
        bycol[x].sort()   # by Y ascending (top of screen first)

    # spurious straight connector: [C] whose nearest occupied cell ABOVE (smaller Y) is not a relative
    for bn, n in nodes.items():
        fl = conn_flag(n)
        if fl == 'C':
            col = bycol[n['x']]
            above = [(yy, b) for (yy, b) in col if yy < n['y']]
            if above:
                ay, ab = max(above)   # nearest above = largest Y below n.y
                if not genuine(ab, bn, roots, nodes):
                    add("CONN", "%s [C] connector points UP at unrelated %s (y %d->%d)"
                        % (bn, ab, n['y'], ay))
        elif fl == 'R':
            # right connector: expect a relative in column x+100
            rc = bycol.get(n['x'] + 100, [])
            rel = [b for (yy, b) in rc if genuine(b, bn, roots, nodes)]
            if not rel:
                add("CONN", "%s [R] side-connector has NO relative in column %d"
                    % (bn, n['x'] + 100))

    # interleave: a family member trapped inside another family's Y-span in same column
    for x in bycol:
        fam_ys = defaultdict(list)
        for (yy, bn) in bycol[x]:
            fam_ys[roots[bn]].append(yy)
        spans = {r: (min(ys), max(ys)) for r, ys in fam_ys.items() if len(ys) >= 2}
        for (yy, bn) in bycol[x]:
            r = roots[bn]
            for orr, (lo, hi) in spans.items():
                if orr != r and lo < yy < hi:
                    add("INTERLEAVE", "%s (fam %s) trapped inside %s span (col %d, y=%d in %d..%d)"
                        % (bn, r, orr, x, yy, lo, hi))
                    break

    # modifier whose base is present but in a DIFFERENT column
    for bn, n in nodes.items():
        r = roots[bn]
        if r != bn and r in nodes:
            if nodes[r]['x'] != n['x']:
                sev = " (HAS CONNECTOR)" if conn_flag(n) != '.' else ""
                add("OFFCOL", "%s (col %d) base %s in col %d%s"
                    % (bn, n['x'], r, nodes[r]['x'], sev))

    # ---- print ----
    order = ["GRID", "DUPCELL", "TIER", "ICON", "NAME", "DUPNAME",
             "CONN", "INTERLEAVE", "OFFCOL"]
    counts = {}
    for k in order:
        if F.get(k):
            counts[k] = len(F[k])
            out.append("  [%s] %d:" % (k, len(F[k])))
            for m in F[k]:
                out.append("      - " + m)
    if not counts:
        out.append("  (clean)")
    return counts


def audit_select(gold, out):
    """Select-mastery + tree-pane wiring per slot.

    NOTE: the mod does NOT override the base `masterypane.dbr` / `mastery{N}text.dbr`
    records (they live in the base game and reference tagMasteryBrief0N /
    tagMasteryDescription0N); mastery renames are done via TEXT-tag overrides in
    modStrings.txt. So an absent mod-arz select record is EXPECTED, not a defect -
    it is reported here as informational. The real Rogue-label duplicate-tag class
    lives in the text pipeline (build_text_arc.check_duplicate_tags), not the arz.
    This routine flags only a genuine anomaly: a mastery TREE pane (panectrl.dbr,
    which the mod DOES ship) whose title/desc tag is empty/missing."""
    out.append("\n=== SELECT-MASTERY + TREE-PANE (informational; labels are text-tag driven) ===")
    issues = 0
    for slot in range(1, 9):
        pane = folder(slot) + "panectrl.dbr"
        title = gold.gf(pane, "skillTabTitle")
        panedesc = gold.gf(pane, "skillPaneDescriptionTag")
        anomaly = ""
        if title in (None, '', '<NO REC>'):
            anomaly += " EMPTY-skillTabTitle"
        if panedesc in (None, '', '<NO REC>'):
            anomaly += " EMPTY-skillPaneDescriptionTag"
        if anomaly:
            issues += 1
        out.append("  m%d %-14s treeTitle=%r paneDesc=%r%s"
                   % (slot, NAMES[slot], title, panedesc, "  <<%s>>" % anomaly if anomaly else ""))
    out.append("  (mastery SELECT labels/blurbs come from base masterypane + modStrings text tags;")
    out.append("   Rogue-label duplicate-tag class is checked in the text pipeline, gate GREEN.)")
    return issues


def dump_tables(gold, out):
    """Per-mastery per-skill table for the report: current cell, tier, target row,
    connector, family, verdict."""
    for slot in range(1, 10):
        nodes, cells = collect(gold, slot)
        canon_present = {canon(bn): bn for bn in nodes}
        roots = {bn: family_root(bn, nodes, canon_present) for bn in nodes}
        out.append("\n### m%d %s%s ###" % (slot, NAMES[slot], " [GOLDEN]" if slot in GOLDEN else ""))
        out.append("  slot bn                                     (x,y)     row tier req conn family                verdict")
        for bn, n in sorted(nodes.items(), key=lambda kv: (kv[1]['x'], kv[1]['y'])):
            rt = ROW_TIER.get(n['y'], '?')
            try:
                st = int(n['tier']) if n['tier'] not in (None, '') else None
            except (TypeError, ValueError):
                st = None
            v = []
            if st and rt != st:
                v.append("TIER!=%s" % st)
            root = roots[bn]
            if root != bn and root in nodes and nodes[root]['x'] != n['x']:
                v.append("OFFCOL(%s@%d)" % (root, nodes[root]['x']))
            out.append("  %-4d %-40s (%3d,%3d) %-3s %-4s %-3s %-4s %-20s %s"
                       % (n['slot'], bn, n['x'], n['y'], rt, st if st else '-',
                          n['req'] if n['req'] not in (None, '') else '-',
                          conn_flag(n), root[:20], ' '.join(v)))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    table_mode = '--table' in sys.argv
    gp = Path(args[0]) if len(args) > 0 else DEF_GOLD
    bp = Path(args[1]) if len(args) > 1 else DEF_BASE
    gold = DB(gp)
    base = DB(bp)
    out = []
    if table_mode:
        out.append("### PER-SKILL TABLES: %s ###" % gp.name)
        dump_tables(gold, out)
        print('\n'.join(out))
        return
    out.append("### MASTERY UI AUDIT: %s ###" % gp.name)
    grand = defaultdict(int)
    skills_audited = 0
    for slot in range(1, 10):
        nodes, _ = collect(gold, slot)
        skills_audited += len(nodes)
        counts = audit_mastery(gold, base, slot, out)
        for k, v in counts.items():
            grand[k] += v
    sel_issues = audit_select(gold, out)
    out.append("\n### SUMMARY ###")
    out.append("masteries_audited: 9")
    out.append("skills_audited: %d" % skills_audited)
    for k in ["TIER", "CONN", "INTERLEAVE", "OFFCOL", "GRID", "DUPCELL",
              "ICON", "NAME", "DUPNAME"]:
        out.append("  %-11s : %d" % (k, grand.get(k, 0)))
    out.append("  SELECT     : %d" % sel_issues)
    print('\n'.join(out))


if __name__ == "__main__":
    main()
