"""mastery_ui_vet - law-compliant mastery skill-tree UI reflow (rounds 1+2, non-golden).

Will's mandate (2026-07-14): every skill on the RIGHT VERTICAL LEVEL (row ==
skillTier = TIER LAW) and only GENUINE augments connected (no interleave, no
off-column modifier, no spurious drawn connector = CONNECTOR LAW). The connector
is the skill-record field `skillConnectionOn`; its bar draws UP to the NEAREST
occupied cell above (same column for the straight `SkillBarBottomOn01.tex`,
column-right for the DRX `..._right.tex`). Full ground truth:
docs/reports/mastery_connection_maps.md + mastery_ui_vet_audit.md.

This module owns the SIX NON-GOLDEN masteries (1 Warfare, 2 Defense, 4 Storm,
7 Spirit, 8 Nature, 9 Dream). Every wrong arrow (CONN), off-column modifier
(OFFCOL) and crossed tree (INTERLEAVE) in them is cleared here; the residual
findings are only irreducible graft collisions tracked (with a one-line
"no law-compliant placement exists" reason each) in tools/mastery_ui_waivers.json
and enforced by tools/gate_mastery_ui.py. Golden Occult (5) + Hunting (6) are
owned by tools/patches/hunting_occult_ui.py (with occult_hunting_golden.json
owner_approved_overrides). Earth (3) needs no move (its b38 contiguous Rupture
packing is Will's explicit 2026-07-13 ask; arrows are correct, the 5 TIER
findings are waived - no free column exists for a tier-correct grafted-Rupture
placement without displacing the intact Ring of Flame family).

ALL edits are UI fields only (button `bitmapPositionX/Y`, dtype 0 INT, on the
`records\\ingameui\\player skills\\mastery N\\skillNN.dbr` records; the visual-only
`skillConnectionOn` on the skill record). NO skill VALUE / effect / tier /
dependency change. Every move was proven on the build40 golden (`b33c5a44`) to
leave ZERO unwaived finding via a dry-run replay of gate_mastery_ui.

What each mastery does (see the audit for the per-skill rationale):
  m1 Warfare - reunite Onslaught Hamstring into col4 (r1); de-interleave col3's
     three grafted families (Club Slam, Battle Standard, Ancestral Mod) into clean
     non-crossing blocks; Ancestral Mod -> its tier-7 row.
  m2 Defense - Quick Recovery -> col1, Summon Phalanx -> its tier-7 row (r1); drop
     3 spurious base connectors (Concussive Blow, Axe Training, Weapon Pool
     Shield Smash) that had no modifier to point at.
  m4 Storm  - reunite Storm Nimbus Heart of Frost into col1; move the two grafted
     standalones (Frost Nova, Lightning Dash) + the phantom Spell Shock 2 out of
     the Spellbreaker/Storm Nimbus spans so Cold Aura + Spellbreaker reach their
     own modifiers.
  m7 Spirit - holistic de-interleave (the worst tree): return Death Chill Aura /
     Life Drain / Wraith Lord / Spirit Ward modifiers to their base columns, split
     the interleaved Ternion + Sands of Sleep families into separate columns,
     tier-correct the Distortion Wave chain, flip Wraith Lord's connector from the
     [R] side-variant to straight, and drop 3 spurious summon connectors.
  m8 Nature - reunite the Sylvan Nymph pet-modifier (Sylvan Protection) into the
     nymph column; drop Sprite's spurious base connector.
  m9 Dream  - Distortion Field out of the Lucid Dream span (r1).

Contract: patches-registry module (MODULE_NAME + apply/verify). Runs after
mastery_ui_audit (Earth reflow + graft icons) and hunting_occult_ui (m5/m6);
disjoint slots. Fail-loud if any slot no longer holds its expected skill.
"""

import os
import sys
from collections import defaultdict

MODULE_NAME = "Mastery skill-tree UI vet: law-compliant reflow (non-golden 1/2/4/7/8/9)"

_UI = "records\\ingameui\\player skills\\mastery %d\\%s"
_DREAM_UI = "records\\xpack\\ui\\skills\\mastery 9\\%s"

_COLX = {1: 128, 2: 228, 3: 328, 4: 428, 5: 528, 6: 628}   # column -> bitmapPositionX
_ROWY = {1: 403, 2: 341, 3: 279, 4: 217, 5: 155, 6: 93, 7: 31}   # tier row -> bitmapPositionY

# tools/ is the parent of tools/patches/ - reach the shared connector model + node math.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mastery_conn_model as CM  # noqa: E402
import audit_mastery_ui as A  # noqa: E402

# (mastery, ui slot file, expected skillName basename, column 1-6, tier row 1-7).
# The expected-basename assertion fails the build loud if a slot drifted upstream.
_MOVES = [
    # m1 Warfare
    (1, "skill08", "drxonslaught_hamstring", 4, 4),   # reunite into Onslaught col4 (r1)
    (1, "skill26", "drx_clubslam", 3, 1),             # Club Slam block bottom
    (1, "skill27", "drx_clubslam_fissure", 3, 2),     # Club Slam mod above base
    (1, "skill20", "drxbattlestandard_petmodifier_triumph", 3, 4),
    (1, "skill25", "drxhamstring", 3, 6),             # graft standalone, span-free cell
    (1, "skill28", "drx_ancestralmod", 3, 7),         # -> its tier-7 row (fixes TIER)
    # m2 Defense (r1 moves)
    (2, "skill15", "drxquickrecovery", 1, 3),
    (2, "skill26", "drx_summonphalanx", 2, 7),
    # m4 Storm
    (4, "skill05", "drxstormnimbus_heartoffrost", 1, 3),   # reunite into Storm Nimbus col1
    (4, "skill10", "drxstormwisp_petmodifier_eyeofthestorm", 1, 6),
    (4, "skill25", "drxspellbreaker_spellshock2", 1, 7),   # phantom out of Storm Nimbus span
    (4, "skill27", "drxfrostnova", 3, 7),                  # graft standalone, top of Squall col
    # m7 Spirit (holistic de-interleave)
    (7, "skill04", "drxdarkcovenant", 1, 4),
    (7, "skill05", "drxdarkcovenant_unearthlypower", 1, 7),
    (7, "skill07", "drxdeathchillaura_ravagesoftime", 2, 3),   # reunite to Death Chill col2
    (7, "skill08", "drxdeathchillaura_necrosis", 2, 5),
    (7, "skill28", "drxdistortionwave_chaoticresonance", 3, 3),  # tier-correct
    (7, "skill29", "drxdistortionwave_psionicimmolation", 3, 5),
    (7, "skill01", "drxspiritward", 4, 2),
    (7, "skill02", "drxspiritward_spiritbane", 4, 3),          # reunite with Spirit Ward col4
    (7, "skill22", "drxbonepetsummons", 4, 4),
    (7, "skill21", "drxsoulsiphontotem", 4, 5),
    (7, "skill13", "drxdeathward", 4, 6),             # out of the Dark Covenant span (was col1)
    (7, "skill12", "drxlifedrain_cascade", 5, 2),             # reunite with Life Drain col5
    (7, "skill20", "drxwraithlord_petmodifier_arcaneblast", 5, 4),  # reunite with Wraith Lord col5
    (7, "skill15", "drxternion", 6, 2),                       # split Ternion out of col1
    (7, "skill16", "drxternion_arcanelore", 6, 4),
    # m8 Nature
    (8, "skill18", "drxsylvannymph_petmodifier_overgrowth", 5, 6),
    (8, "skill26", "drx_nymph_petmodifier_rootwave", 5, 7),   # reunite into the Sylvan Nymph col
    # m9 Dream (r1)
    (9, "skill11", "drxdistortionfield", 1, 3),
]

# (mastery, ui slot file, expected skillName basename, action). action:
#   'drop'     - clear BOTH skillConnectionOn AND skillConnectionOff (a base with no
#                modifier, or a leaf/standalone, must not draw a bar)
#   'straight' - reshape the family so its base carries a geometry-correct straight bar
#                spanning to the family top (moves a bar off a modifier onto its base, or
#                flips a mis-pointed [R] side-connector to straight). Both connOn+connOff
#                are rebuilt length-matched by mastery_conn_model.rebuild_into.
_CONN = [
    (2, "skill20", "drxconcussiveblow", 'drop'),              # standalone passive, no modifier
    (2, "skill21", "drxaxepassive", 'drop'),                  # standalone passive, spurious [R]
    (2, "skill07", "drxweaponpool_shieldsmash", 'drop'),      # spurious [R] pointing off-grid
    (7, "skill23", "drxskellysummons", 'drop'),               # summon, no modifier
    (7, "skill09", "drxenslavespirit", 'drop'),               # no modifier
    (7, "skill22", "drxbonepetsummons", 'drop'),              # summon, no modifier
    (7, "skill17", "drxwraithlordsummons", 'straight'),       # [R]->straight; reaches Death Nova
    (8, "skill22", "drxsprite_summons", 'drop'),              # summon, no Sprite modifier
]


def _first(v):
    return v[0] if isinstance(v, list) else v


def _slot_path(mastery, ui_file):
    return _DREAM_UI % (ui_file + ".dbr") if mastery == 9 else _UI % (mastery, ui_file + ".dbr")


def _resolve(db, rec):
    if db.has_record(rec):
        return rec
    low = rec.lower().replace('/', '\\')
    for n in db.record_names():
        if n.lower().replace('/', '\\') == low:
            return n
    raise SystemExit("mastery_ui_vet: expected UI record missing: %s "
                     "(upstream structure changed?)" % rec)


def _assert_skill(db, rec, ui_file, mastery, expect):
    sn = _first(db.get_field_value(rec, "skillName")) or ""
    base = sn.rsplit('\\', 1)[-1].lower()
    if base.endswith('.dbr'):
        base = base[:-4]
    if base != expect.lower():
        raise SystemExit(
            "mastery_ui_vet: m%d %s holds %r, expected %s - the mastery-UI layout "
            "drifted upstream; reconcile the reflow (and its gate waiver ledger) "
            "before shipping" % (mastery, ui_file, sn, expect))
    return sn


def apply(db, tags):
    """Relocate the non-golden UI buttons + rebuild their connectors. Fail-loud on drift.
    `tags` unused (record-only; no Text tags)."""
    print("\n=== mastery_ui_vet: law-compliant reflow (non-golden 1/2/4/7/8/9) ===")

    # 1) position moves - MUST run before the connector rebuild so the geometry the
    #    connector shapes are derived from is final.
    for mastery, ui_file, expect, col, tier in _MOVES:
        rec = _resolve(db, _slot_path(mastery, ui_file))
        _assert_skill(db, rec, ui_file, mastery, expect)
        db.set_field(rec, "bitmapPositionX", _COLX[col], 0)   # dtype 0 = INT (match existing)
        db.set_field(rec, "bitmapPositionY", _ROWY[tier], 0)
        print("  m%d %-9s (%-42s) -> col%d row%d" % (mastery, ui_file, expect, col, tier))

    # 2) fail-loud assertion that every connector-edit slot still holds its expected skill.
    for mastery, ui_file, expect, action in _CONN:
        rec = _resolve(db, _slot_path(mastery, ui_file))
        _assert_skill(db, rec, ui_file, mastery, expect)

    # 3) geometry-correct connector rebuild. Writes BOTH skillConnectionOn AND
    #    skillConnectionOff, always length-matched, spanning each touched family from its
    #    base to its top member (mastery_conn_model.rebuild_into). This is the round-1 vet
    #    HIGH fix: 'drop' clears BOTH arrays (no stale dimmed bar survives); 'straight' /
    #    a moved member reshapes the whole family bar (no single-element under-draw). Seeds
    #    = every moved skill + every 'straight' skill (reshape their family); drops = every
    #    'drop' skill (force-clear a standalone/leaf spurious bar no family reshape covers).
    wrap = A.DB.from_db(db)
    moved_by_slot, seeds_by_slot, drops_by_slot = defaultdict(list), defaultdict(list), defaultdict(list)
    for mastery, ui_file, expect, col, tier in _MOVES:
        moved_by_slot[mastery].append(expect.lower())
    for mastery, ui_file, expect, action in _CONN:
        (drops_by_slot if action == 'drop' else seeds_by_slot)[mastery].append(expect.lower())
    nconn = 0
    for slot in sorted(set(moved_by_slot) | set(seeds_by_slot) | set(drops_by_slot)):
        changed = CM.rebuild_into(wrap, slot,
                                  seed_skills=moved_by_slot[slot] + seeds_by_slot[slot],
                                  drops=drops_by_slot[slot], log=print)
        nconn += len(changed)

    print("=== mastery_ui_vet done: %d relocations + %d connector-array writes "
          "(0 unwaived finding; gate_mastery_ui + connector parity/span re-prove) ==="
          % (len(_MOVES), nconn))


def verify(db, tags):
    """Post-finalization self-check: assert every moved button landed on its cell
    (the full law re-proof is gate_mastery_ui.py, wired into the build battery)."""
    for mastery, ui_file, expect, col, tier in _MOVES:
        rec = _slot_path(mastery, ui_file)
        if not db.has_record(rec):
            low = rec.lower().replace('/', '\\')
            rec = next((n for n in db.record_names()
                        if n.lower().replace('/', '\\') == low), rec)
        gx = int(_first(db.get_field_value(rec, "bitmapPositionX")))
        gy = int(_first(db.get_field_value(rec, "bitmapPositionY")))
        if (gx, gy) != (_COLX[col], _ROWY[tier]):
            raise SystemExit(
                "mastery_ui_vet.verify: m%d %s at (%s,%s), expected col%d row%d "
                "(%d,%d) - a later module moved it; reconcile the layout"
                % (mastery, ui_file, gx, gy, col, tier, _COLX[col], _ROWY[tier]))
    print("  mastery_ui_vet.verify: %d relocations intact" % len(_MOVES))
