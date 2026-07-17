"""PERMANENT UNLOCK-ALIGNMENT GATE (b77, fail-loud like the A7 golden guard).

Every LIVE mastery skill button (one listed in its mastery's
panectrl.tabSkillButtons) must obey, on the FINAL written .arz:

  1. skillTier == the row the button is DRAWN on (bitmapPositionY -> row via
     Y = 465 - 62*tier), so a skill's real unlock cost matches its visual row
     (Will's 2026-07-16 directive). Only checked for buttons whose skill record
     carries a skillTier (petmodifiers / positional-only leaves have none -> skip,
     mirroring the b74 audit's "tiered skills" scope).
  2. effective unlock gate == the tier threshold, i.e.
     skillMasteryLevelRequired <= pointThreshold(drawn_row), so no hidden
     secondary floor lifts a skill above its row - EXCEPT the by-construction
     REQ-EXCEEDS-ROW waivers below (SV-faithful modifier / leaf chain-slots;
     vanilla ships 14 of the same class; each cited to the b74 audit JSON).

pointThreshold(tier 1..7) = 1 / 4 / 10 / 16 / 24 / 32 / 40.
rows t1..t7 -> Y {403,341,279,217,155,93,31}; columns X {128,228,328,428,528,628}.

Wired into the DB build right after the A7 golden guard (build_svc_database.py) so a
green build is unlock-aligned by construction. A planted drifted tier fails the gate
(negative test: --negtest).

usage:
  validate : py tools/gate_unlock_alignment.py <arz>
  negtest  : py tools/gate_unlock_alignment.py <arz> --negtest
exit codes: 0 = PASS, 1 = one or more live buttons drift, 2 = usage/load error.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase  # noqa: E402

_ROW_FROM_Y = {403: 1, 341: 2, 279: 3, 217: 4, 155: 5, 93: 6, 31: 7}
_TIER_THRESHOLD = {1: 1, 2: 4, 3: 10, 4: 16, 5: 24, 6: 32, 7: 40}

# masteries 1-8 UI dir + m9 (Dream) xpack dir; each has a panectrl.dbr.
_PANECTRL = ([("records\\ingameui\\player skills\\mastery %d\\panectrl.dbr" % m, m)
              for m in range(1, 9)]
             + [("records\\xpack\\ui\\skills\\mastery 9\\panectrl.dbr", 9)])

# ── REQ-EXCEEDS-ROW WAIVER MANIFEST (13; b74 audit §5) ────────────────────────
# skill basename (no .dbr, lowercase) -> SV-faithful citation. Each is tier==row
# (only skillMasteryLevelRequired lifts the effective gate above the row threshold);
# vanilla ships 14 of the same modifier/leaf chain-slot class. 11 of 13 match SV098's
# own skillMasteryLevelRequired byte-for-byte (gt_tier_req in tools/unlock_alignment_audit.json);
# 2 overlays (warwind_refinement, soulsiphontotem) have no SV098 GT and are +1 benign.
_REQ_WAIVERS = {
    "drxdualwieldtechnique_crosscut": "SV098 req24 on row4/thr16 (dual-wield leaf; audit §5)",
    "drxwarwind":                     "SV098 req15 on row2/thr4  (War Dance; audit §5)",
    "drxwarwind_lacerate":            "SV098 req25 on row4/thr16 (War Dance modifier; audit §5)",
    "drxwarwind_refinement":          "overlay, no SV098 GT, +1 benign (audit §5)",
    "drxbatter_rendarmor":            "SV098 req15 on row3/thr10 (Batter modifier; audit §5)",
    "drxrally_defiance":              "SV098 req30 on row5/thr24 (Rally modifier; audit §5)",
    "drxringofflame":                 "SV098 req10 on row1/thr1  (Ring of Flame; audit §5)",
    "drxensnare_barbednetting":       "SV098 req24 on row3/thr10 (Ensnare modifier; audit §5)",
    "drxherbalism":                   "SV098 req5  on row2/thr4  (Herbalism; audit §5)",
    "drxweaponskill_gouge":           "SV098 req5  on row1/thr1  (Weapon Skill leaf; audit §5)",
    "drxvisionofdeath":               "SV098 req5  on row1/thr1  (Vision of Death; audit §5)",
    "drxsoulsiphontotem":             "overlay, no SV098 GT, +1 benign (audit §5)",
    "drxplague_fatigue":              "SV098 req18 on row4/thr16 (Plague modifier; audit §5)",
}


def _first(v):
    return (v[0] if v else None) if isinstance(v, list) else v


def _load(arz_path):
    return ArzDatabase.from_arz(Path(arz_path))


def _resolver(db):
    nl = {n.lower().replace('/', '\\'): n for n in db.record_names()}

    def R(rec):
        rec = str(rec).replace('/', '\\')
        return rec if db.has_record(rec) else nl.get(rec.lower())
    return R


def validate(arz_path, plant_drift=False):
    print("=" * 72)
    print("UNLOCK-ALIGNMENT GATE (b77)")
    print("  arz :", arz_path)
    db = _load(arz_path)
    R = _resolver(db)

    if plant_drift:
        # negative test: pick a live, tiered button and corrupt its tier so the gate
        # MUST fail. Fire Nova (Earth m3 skill25) is a known live tier-7 button post-fix.
        target = R("records\\skills\\earth\\drx_firenova.dbr")
        if target:
            db.set_field(target, "skillTier", 3, 0)  # 3 != drawn row7 -> must be caught
            print("  [negtest] planted drxfirenova skillTier=3 (drawn row7) - gate MUST fail")

    checked = tier_drift = req_over = waived = skipped = 0
    fails = []
    for pc_path, mslot in _PANECTRL:
        pc = R(pc_path)
        if pc is None:
            continue
        lst = db.get_field_value(pc, "tabSkillButtons") or []
        if not isinstance(lst, list):
            lst = [lst]
        for entry in lst:
            btn = R(entry)
            if btn is None or "\\mastery.dbr" in str(entry).lower():
                continue
            y = _first(db.get_field_value(btn, "bitmapPositionY"))
            if y is None:
                continue
            row = _ROW_FROM_Y.get(int(y))
            if row is None:
                fails.append("m%d %s OFF-GRID (y=%s not a lattice row)"
                             % (mslot, str(entry).rsplit('\\', 1)[-1], y))
                continue
            sn = _first(db.get_field_value(btn, "skillName"))
            sk = R(sn) if sn else None
            if sk is None:
                fails.append("m%d %s dangling skillName %r (no skill record)"
                             % (mslot, str(entry).rsplit('\\', 1)[-1], sn))
                continue
            checked += 1
            base = str(sk).rsplit('\\', 1)[-1].lower()[:-4]
            tier = _first(db.get_field_value(sk, "skillTier"))
            req = _first(db.get_field_value(sk, "skillMasteryLevelRequired"))
            try:
                reqn = int(req) if req is not None else 0
            except (TypeError, ValueError):
                reqn = 0
            thr = _TIER_THRESHOLD[row]
            # 1. tier == drawn row (only for tiered skills)
            if tier is not None:
                if int(tier) != row:
                    tier_drift += 1
                    fails.append("m%d %s (%s): skillTier=%s but DRAWN row%d (thr%d) - "
                                 "TIER-DRIFT" % (mslot, base, sk, tier, row, thr))
            else:
                skipped += 1
            # 2. req <= row threshold, unless waived
            if reqn > thr:
                if base in _REQ_WAIVERS:
                    waived += 1
                else:
                    req_over += 1
                    fails.append("m%d %s (%s): skillMasteryLevelRequired=%d > row%d "
                                 "threshold %d and NOT waived - REQ-OVER"
                                 % (mslot, base, sk, reqn, row, thr))

    print("  live buttons checked        : %d (%d tiered, %d positional-only)"
          % (checked, checked - skipped, skipped))
    print("  REQ-EXCEEDS-ROW waivers hit : %d / %d in manifest" % (waived, len(_REQ_WAIVERS)))
    if fails:
        for f in fails:
            print("  FAIL:", f)
        print("RESULT: FAIL - %d tier-drift + %d req-over (see above)"
              % (tier_drift, req_over))
        return 1
    print("RESULT: PASS - every live button's skillTier == drawn row and "
          "req <= threshold (waivers aside)")
    return 0


def main(argv):
    args = argv[1:]
    if not args:
        print(__doc__)
        return 2
    neg = "--negtest" in args
    args = [a for a in args if a != "--negtest"]
    if not args:
        print("usage: py tools/gate_unlock_alignment.py <arz> [--negtest]")
        return 2
    rc = validate(args[0], plant_drift=neg)
    if neg:
        # invert: the negative test PASSES iff the gate FAILED on the planted drift.
        if rc == 0:
            print("NEGTEST RESULT: FAIL - gate did NOT catch the planted drift")
            return 1
        print("NEGTEST RESULT: PASS - gate correctly caught the planted drift")
        return 0
    return rc


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
