r"""build_connection_maps - the AUTHORITATIVE per-mastery skill-tree CONNECTION MAP.

Ground truth established by the TEXTURE DECODER (2026-07-14, feat/mastery-ui-vet):

  1. THE CONNECTORS ARE NOT BAKED INTO THE BACKGROUND ART.  Decoding all 9 effective
     <Class>SkillBackground01.tex panes (uncompressed 32-bit BGRA, 919x540) shows the
     art carries ONLY 6 horizontal tier "shelf" lines (at image y {397,335,273,211,
     149,87} = a 62 px pitch, aligned to the button rows Y=465-62*tier) plus the frame
     and mastery-art holes.  There are ZERO vertical skill-to-skill lines in the art.
     (This falsifies mastery_ui_invariants.md section 2a's "baked art" conclusion and
     confirms mastery_ui_vet_audit.md section 1's correction.)

  2. A CONNECTOR IS A RUNTIME-DRAWN BAR from the skill-record field `skillConnectionOn`.
     Straight bar  = InGameUI\Icons\Skills\SkillBars\SkillBarBottomOn01.tex  (15x62,
        base InGameUI.arc) -> an L / vertical riser in the SAME column.
     Diagonal bar  = DRXtextures\Skill Icons\SkillBarBottomOn01_right.tex   (80x62,
        mod DRXtextures.arc) -> a riser in the column to the RIGHT.
     `skillConnectionSpacing`=62 is the render TILE pitch, not the reach.

  3. REACH RULE (proven on the clean base game: 43 connectors, 0 real spurious):
     a skill S carrying `skillConnectionOn` draws a bar UP (toward lower Y / higher
     tier) to the NEAREST OCCUPIED cell above it - spanning any empty gap - in
       * the SAME column        for the straight  (SkillBarBottomOn01)    variant, and
       * the column to the RIGHT for the diagonal (..._right)             variant.
     The connected pair is (S, that nearest-occupied-above cell's skill).

  => The connection a player SEES is fully computable from the arz (button positions +
     which skills carry skillConnectionOn + variant).  No screenshot needed.  A layout
     is CORRECT iff, for every S carrying a connector, its nearest-occupied-above (in
     the connector's direction) is a GENUINE augment of S (same `<base>_<suffix>` /
     summon-pet family, or a `skillDependancy` pair), and every intended base->modifier
     family is realised with no FOREIGN skill trapped between the base and its top
     modifier in that column.

This module reuses tools/audit_mastery_ui.py's EXACT node/family/genuine helpers (one
source of truth, same as gate_mastery_ui.py), derives the edges, and emits:
  tools/mastery_connection_maps.json  (machine-readable: geometry + per-mastery edges)
and feeds docs/reports/mastery_connection_maps.md.

Usage:
  py tools/build_connection_maps.py [gold_arz] [base_arz] [--json out.json]
  py tools/build_connection_maps.py --validate   # base-game genuine pairs + negative
"""
import json
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(_TOOLS))
import audit_mastery_ui as A  # noqa: E402  (DB, collect, canon, family_root, genuine, COLS, ROW_TIER, NAMES)

# --- decoded connector-texture geometry (facts from tools/tex_decode.py) -------------
CONNECTOR_TEX = {
    "straight": {
        "field_value": r"InGameUI\Icons\Skills\SkillBars\SkillBarBottomOn01.tex",
        "arc": "base InGameUI.arc",
        "size": [15, 62], "format": "uncompressed 32-bit BGRA",
        "geometry": "vertical riser, same column, reaches the nearest occupied cell above",
        "flag": "C",
    },
    "right": {
        "field_value": r"DRXtextures\Skill Icons\SkillBarBottomOn01_right.tex",
        "arc": "mod DRXtextures.arc",
        "size": [80, 62], "format": "uncompressed 32-bit BGRA",
        "geometry": "diagonal riser up-and-right, reaches the nearest occupied cell above in the column to the RIGHT",
        "flag": "R",
    },
    "spacing_px": 62,
    "note": "spacing is the render tile pitch (one tier row), NOT the connector reach",
}

# effective pane-background texture each mastery actually loads (golden arz
# skillpanebasebitmap.dbr::bitmapName -> in base InGameUI.arc; no mod override)
EFFECTIVE_BG = {
    1: r"InGameUI\Skills\WarfareSkillBackground01.tex",
    2: r"InGameUI\Skills\DefenseSkillBackground01.tex",
    3: r"InGameUI\Skills\EarthSkillBackground01.tex",
    4: r"InGameUI\Skills\StormSkillBackground01.tex",
    5: r"InGameUI\Skills\StealthSkillBackground01.tex",   # Occult reuses Stealth pane
    6: r"InGameUI\Skills\HuntingSkillBackground01.tex",
    7: r"InGameUI\Skills\SpiritSkillBackground01.tex",
    8: r"InGameUI\Skills\NatureSkillBackground01.tex",
    9: r"InGameUI\Skills\SpiritSkillBackground01.tex",     # Dream shares Spirit pane
}
BG_TIER_SHELVES_Y = [397, 335, 273, 211, 149, 87]   # measured in the 919x540 art
COL_OF = {x: i + 1 for i, x in enumerate(A.COLS)}     # x-px -> column 1..6


def _col(x):
    return COL_OF.get(x)


def _row(y):
    return A.ROW_TIER.get(y)


def edges_for(db, slot):
    """Return (nodes, edges) for one mastery. Each edge is the connector a player sees."""
    nodes, cells = A.collect(db, slot)
    canon_present = {A.canon(bn): bn for bn in nodes}
    roots = {bn: A.family_root(bn, nodes, canon_present) for bn in nodes}
    occ = {(n["x"], n["y"]): bn for bn, n in nodes.items()}
    edges = []
    for bn, n in nodes.items():
        conn = n.get("conn")
        if not conn:
            continue
        right = "_right" in str(conn).lower()
        x, y = n["x"], n["y"]
        tcol_x = x + 100 if right else x
        # nearest occupied cell ABOVE (smaller Y) in the target column
        tgt_bn = tgt_xy = None
        for yy in sorted([yv for (xv, yv) in occ if xv == tcol_x and yv < y], reverse=True):
            tgt_bn, tgt_xy = occ[(tcol_x, yy)], (tcol_x, yy)
            break
        if tgt_bn is None:
            kind = "void"
            gen = False
        else:
            gen = A.genuine(bn, tgt_bn, roots, nodes)
            kind = "genuine" if gen else "spurious"
        edges.append({
            "variant": "R" if right else "C",
            "src_skill": bn,
            "src_cell": [_col(x), _row(y)],
            "src_tier_field": n.get("tier"),
            "tgt_skill": tgt_bn,
            "tgt_cell": [_col(tgt_xy[0]), _row(tgt_xy[1])] if tgt_xy else None,
            "genuine": gen,
            "kind": kind,
        })
    edges.sort(key=lambda e: (e["src_cell"][0] or 9, -(e["src_cell"][1] or 0)))
    return nodes, edges


def build(db):
    out = {"masteries": {}}
    for slot in range(1, 10):
        nodes, edges = edges_for(db, slot)
        occupied = sorted(
            [{"cell": [_col(n["x"]), _row(n["y"])], "skill": bn,
              "connector": ("R" if "_right" in str(n["conn"]).lower() else "C") if n.get("conn") else None}
             for bn, n in nodes.items()],
            key=lambda o: (o["cell"][0] or 9, -(o["cell"][1] or 0)))
        out["masteries"][str(slot)] = {
            "name": A.NAMES[slot],
            "golden_tracked": slot in A.GOLDEN,
            "effective_background_tex": EFFECTIVE_BG[slot],
            "occupied_cells": occupied,
            "connector_edges": edges,
            "counts": {
                "connectors": len(edges),
                "genuine": sum(e["kind"] == "genuine" for e in edges),
                "spurious": sum(e["kind"] == "spurious" for e in edges),
                "void": sum(e["kind"] == "void" for e in edges),
            },
        }
    return out


# -------- validation against known-genuine vanilla pairs + the negative control ------
GENUINE_PAIRS = [   # (mastery slot, base skill, its modifier) - must be a drawn edge
    (1, "onslaught", "onslaught_ignorepain"),
    (1, "battlerage", "battlerage_crushingblow"),
    (1, "warwind", "warwind_lacerate"),
    (1, "warhorn", "warhorn_doomhorn"),
    (1, "battlestandard", "battlestandard_petmodifier_triumph"),
    (1, "dualweapontraining", "dualwieldtechnique_jumpslash"),  # via skillDependancy
    (6, "marksmanship", "marksmanship_punctureshotarrows"),
    (6, "takedown", "takedown_eviscerate"),
    (6, "monsterlure", "monsterlure_petmodifier_detonate"),
]
# negative control: these two are adjacent in Warfare col 1 but must NOT be a drawn pair
NEGATIVE = (1, "weapontraining", "dualweapontraining")


def validate(base_db):
    ok = True
    print("=== VALIDATION on base game (vanilla ground truth) ===")
    per_slot = {slot: {e["src_skill"]: e for e in edges_for(base_db, slot)[1]}
                for slot in range(1, 10)}
    # also index edges as undirected connected pairs
    pairs = {slot: {frozenset((e["src_skill"], e["tgt_skill"]))
                    for e in edges_for(base_db, slot)[1] if e["tgt_skill"]}
             for slot in range(1, 10)}
    print("-- 5+ known-genuine pairs must be drawn AND genuine:")
    for slot, base, mod in GENUINE_PAIRS:
        e = per_slot[slot].get(base)
        drawn = e is not None and e["tgt_skill"] == mod
        gen = drawn and e["genuine"]
        status = "PASS" if (drawn and gen) else "FAIL"
        if not (drawn and gen):
            ok = False
        print("   [%s] m%d %-20s -> %-32s (drawn=%s genuine=%s)"
              % (status, slot, base, mod, drawn, gen))
    print("-- negative control must NOT be a connected pair:")
    slot, a, b = NEGATIVE
    connected = frozenset((a, b)) in pairs[slot]
    status = "PASS" if not connected else "FAIL"
    if connected:
        ok = False
    print("   [%s] m%d %s <-> %s connected=%s (expect False)" % (status, slot, a, b, connected))
    # base-game global cleanliness: count non-genuine drawn edges
    tot = spur = 0
    spur_list = []
    for slot in range(1, 10):
        for e in edges_for(base_db, slot)[1]:
            tot += 1
            if e["kind"] != "genuine":
                spur += 1
                spur_list.append((slot, e["src_skill"], e["tgt_skill"], e["kind"]))
    print("-- base-game connectors: %d total, %d non-genuine" % (tot, spur))
    for slot, s, t, k in spur_list:
        print("     m%d %s -> %s (%s)" % (slot, s, t, k))
    print("=== VALIDATION %s ===" % ("PASS" if ok else "FAIL"))
    return ok


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    gold = Path(args[0]) if len(args) > 0 else A.DEF_GOLD
    base = Path(args[1]) if len(args) > 1 else A.DEF_BASE
    if "--validate" in argv:
        return 0 if validate(A.DB(base)) else 1
    outp = _TOOLS / "mastery_connection_maps.json"
    if "--json" in argv:
        outp = Path(argv[argv.index("--json") + 1])
    gdb = A.DB(gold)
    data = build(gdb)
    data["_meta"] = {
        "generator": "tools/build_connection_maps.py",
        "golden_arz": str(gold),
        "connector_texture_geometry": CONNECTOR_TEX,
        "background_tier_shelf_y_px": BG_TIER_SHELVES_Y,
        "background_format": "uncompressed 32-bit BGRA, 919x540, no baked connectors",
        "reach_rule": ("skillConnectionOn draws to the NEAREST OCCUPIED cell above in the "
                       "same column (straight) or column-right (right); spans gaps"),
        "grid": {"cols_px": A.COLS, "row_tier_y": A.ROW_TIER},
    }
    outp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tot = sum(m["counts"]["connectors"] for m in data["masteries"].values())
    spur = sum(m["counts"]["spurious"] + m["counts"]["void"] for m in data["masteries"].values())
    print("wrote %s : 9 masteries, %d connector edges, %d non-genuine (spurious/void)"
          % (outp, tot, spur))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
