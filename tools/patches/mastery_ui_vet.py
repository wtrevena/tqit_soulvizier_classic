"""mastery_ui_vet - clean, no-regression mastery skill-tree UI relocations (round 1).

Will's mandate (2026-07-14): every skill on the RIGHT VERTICAL LEVEL (row ==
skillTier = TIER LAW) and only GENUINE augments connected (no interleave / no
off-column modifier = CONNECTOR LAW). The full build40 audit
(docs/reports/mastery_ui_vet_audit.md) found 66 findings across 9 masteries.

Most of them cannot be fixed without Will's design decision: the SVAERA/DRX graft
added MORE skill families than the 6-column grid can hold at tier-correct cells
(Earth col428 = 4 families with tier collisions; Storm/Spirit are full), some
grafted modifiers carry contradictory skillTier values (Warfare clubslam: a tier-2
base above tier-7 modifiers), Storm stormnimbus has TWO tier-2 modifiers that
cannot both stack on its column, one Storm button is an SV-original DEAD reference,
and Occult (m5) + Hunting (m6) are Will's GOLDEN hand-tuned trees. Those are tracked
in tools/mastery_ui_waivers.json (each with a justification) and gated by
tools/gate_mastery_ui.py so no NEW defect can ship while the backlog is visible.

This module applies ONLY the relocations that PROVABLY satisfy BOTH laws with a
FREE target cell and ZERO new finding (verified by re-running gate_mastery_ui.py
on the patched arz). Each moves exactly one UI button (bitmapPositionX/Y, dtype 0
INT) - no skill VALUE / effect / tier / dependency change, no golden-tracked
mastery touched (m1/m2/m9 only, so the A7 Occult/Hunting golden stays untouched):

  m1 Warfare  skill08 drxonslaught_hamstring   (628,217) -> (428,217)
     the Onslaught modifier was stranded in Warhorn's column 628 (OFFCOL) and
     trapped in Warhorn's span (INTERLEAVE) and its connector drew up at the
     unrelated Warhorn Doomhorn (CONN). 428 is Onslaught's own column and t4
     (y217) == its skillTier 4 and the cell is free -> all three findings clear,
     connector now lands on Onslaught Craven (same family). Fixes 3.

  m2 Defense  skill15 drxquickrecovery         (228,279) -> (128,279)
     Quick Recovery (standalone tier-3) sat inside Adrenaline's column-228 span
     (INTERLEAVE) and stole Adrenaline's connector (CONN). 128 t3 (y279) == its
     tier and is free and lands in no family span -> both clear; Adrenaline's
     connector now reaches its own Resilience. Fixes 2.

  m2 Defense  skill26 drx_summonphalanx        (428,155) -> (228,31)
     Summon Phalanx has skillTier 7 but sat on row 5 (TIER) inside Battle
     Awareness's column-428 span (INTERLEAVE). 228 t7 (y31) == its tier 7, is
     free, and sits below every family span in that column -> both clear. Fixes 2.

  m9 Dream    skill11 drxdistortionfield       (228,279) -> (128,279)
     Distortion Field (standalone tier-3) was trapped inside the Lucid Dream span
     in column 228 (INTERLEAVE). 128 t3 (y279) == its tier 3 and is free and in
     no family span in that column -> clears. Fixes 1.

Total: 4 moves, 8 findings cleared, 0 new. Every target cell was proven free +
tier-correct + non-interleaving against the build40 per-skill table before landing;
the coupled tools/gate_mastery_ui.py re-proves it every build.

Contract: patches-registry module (MODULE_NAME + apply(db, tags)). Disjoint from
mastery_ui_audit (m3 Earth reflow + graft icons + m9 Dream background) and
hunting_occult_ui (m5/m6 + backgrounds); runs after both. Fail-loud if any slot no
longer holds its expected skill (upstream layout drift) rather than moving a
different button. `tags` unused (record-only; no Text tags).
"""

MODULE_NAME = "Mastery skill-tree UI vet: clean tier/connector relocations (round 1)"

_UI = "records\\ingameui\\player skills\\mastery %d\\%s"
_DREAM_UI = "records\\xpack\\ui\\skills\\mastery 9\\%s"

# (mastery slot, ui slot file, expected skillName basename, new X, new Y). The
# expected-basename assertion fails the build loud if the slot drifted upstream.
_MOVES = [
    (1, "skill08.dbr", "drxonslaught_hamstring", 428, 217),
    (2, "skill15.dbr", "drxquickrecovery",       128, 279),
    (2, "skill26.dbr", "drx_summonphalanx",      228,  31),
    (9, "skill11.dbr", "drxdistortionfield",     128, 279),
]


def _first(v):
    return v[0] if isinstance(v, list) else v


def _slot_path(slot, ui_file):
    return _DREAM_UI % ui_file if slot == 9 else _UI % (slot, ui_file)


def apply(db, tags):
    """Relocate the 4 clean-win mastery UI buttons. Fail-loud on any drift."""
    print("\n=== mastery_ui_vet: clean tier/connector relocations (round 1) ===")

    def _resolve(rec):
        if db.has_record(rec):
            return rec
        low = rec.lower().replace('/', '\\')
        for n in db.record_names():
            if n.lower().replace('/', '\\') == low:
                return n
        raise SystemExit("mastery_ui_vet: expected UI record missing: %s "
                         "(upstream structure changed?)" % rec)

    for slot, ui_file, expect, x, y in _MOVES:
        rec = _resolve(_slot_path(slot, ui_file))
        sn = _first(db.get_field_value(rec, "skillName")) or ""
        base = sn.rsplit('\\', 1)[-1].lower()
        if base.endswith('.dbr'):
            base = base[:-4]
        if base != expect.lower():
            raise SystemExit(
                "mastery_ui_vet: m%d %s holds %r, expected %s - the mastery-UI "
                "layout drifted upstream; reconcile the relocation (and its gate "
                "waiver ledger) before shipping" % (slot, ui_file, sn, expect))
        db.set_field(rec, "bitmapPositionX", x, 0)   # dtype 0 = INT (match existing)
        db.set_field(rec, "bitmapPositionY", y, 0)
        print("  m%d %-12s (%s) -> (%d,%d)" % (slot, ui_file, expect, x, y))

    print("=== mastery_ui_vet done: %d clean relocations "
          "(8 audit findings cleared, 0 new; gate_mastery_ui re-proves) ===" % len(_MOVES))


def verify(db, tags):
    """Post-finalization self-check: assert the 4 buttons landed on their target
    cells (a cheap invariant; the full law re-proof is gate_mastery_ui.py, wired
    into the build battery after the A7 golden guard)."""
    for slot, ui_file, expect, x, y in _MOVES:
        rec = _slot_path(slot, ui_file)
        if not db.has_record(rec):
            low = rec.lower().replace('/', '\\')
            rec = next((n for n in db.record_names()
                        if n.lower().replace('/', '\\') == low), rec)
        gx = _first(db.get_field_value(rec, "bitmapPositionX"))
        gy = _first(db.get_field_value(rec, "bitmapPositionY"))
        if (int(gx), int(gy)) != (x, y):
            raise SystemExit(
                "mastery_ui_vet.verify: m%d %s at (%s,%s), expected (%d,%d) - a "
                "later module moved it; reconcile the layout" % (slot, ui_file, gx, gy, x, y))
    print("  mastery_ui_vet.verify: 4 relocations intact")
