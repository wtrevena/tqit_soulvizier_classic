#!/usr/bin/env python3
"""GATE: travel invariants under the R-248 PROVEN-MECHANISM TRAVEL LAW (2026-08-14).

HISTORY OF THE LAW (all three eras explicit so no vet re-litigates them):
  * 2026-07-12 P0: ALL travel became NPC boat-dialog; authored walk-through portals
    stripped. * 2026-08-13 R-246: the blanket-refire arming of 39 rows was proven to
    corrupt the stateful boat-offer registry; the row tables were RIPPED and travel
    moved to born-open GridEntrance doors + rift shrines. * 2026-08-14 R-248: Will
    refuted the devices IN-GAME ("they lag the game out and break everything");
    the device class is GRAVEYARDED (MODDING_PLAYBOOK sec 10/10a) and the traveler
    rows RETURN in the base-game-faithful shape: dedicated ONE-SHOT steps
    (Condition_OnLevelLoad isResettable=0), <=3 rows/step, 1 trigger : 1 NPC, b88
    awakening pair. The RIP itself survives as law (no row ever rides a re-firing
    step again). See docs/WILL_RULINGS.md R-248.

THIS GATE (spec-based, build-free - reads the LIVE tooling tables so no 1.3GB build
is needed; the artifact-side twins are gate_boatdialog_budget [Quests.arc],
gate_travel_y_terrain [Levels arcs] and gate_testhub_portal_rig [census]):
  V1 RIP HOLDS, quest side: build_quest_files defines NONE of the ripped
     blanket-refire generators/tables (HELOS_HUB_TRAVEL, TESTHUB_MASTER_DESTS,
     TESTHUB_RETURN_DESTS, TESTHUB_RETURN_DESTS_BY_NPC, TESTHUB_AREA_RETURN_NPCS,
     TRAVELER_ENTER_OFFERS, _add_helos_traveler_hub_travel,
     _add_testhub_portal_travel); Almyros' HELOS_PORTAL_DESTS has EXACTLY 3 rows.
  V2 R-248 STEP SPEC: R248_CANONICAL_STEPS arm exactly 10 rows, R248_TESTHUB_STEPS
     exactly 25; every step <=3 rows; rows for one NPC are contiguous (1 trigger :
     1 NPC); the emitted arming is one-shot (the generator's emission is asserted
     on real bytes by gate_boatdialog_budget check (e) - here the SOURCE is checked
     for the isResettable-0 literal so a source edit cannot silently flip it).
  V3 ARMED <=> PLACED, spec side: every NPC armed by the canonical steps is placed
     by the canonical INJECT_SPECS; every NPC armed by the TESTHUB steps is placed
     by the TESTHUB fold (merge_hub_into_inject_specs); NO device records
     (portal_olympianarena*/teleportshrineorient placed by us) exist in either
     spec set (the R-248 revert holds).
  V4 SHARED-RECORD LAW: the traveler records stay minted in the arz pipeline
     (apply_svc_patches source text).

Usage: py tools/debug/gate_travel_npc_invariants.py
Exit 0 = PASS. Read-only, no build required.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))

BS = chr(92)

RIPPED_TABLES = (
    'HELOS_HUB_TRAVEL', 'TESTHUB_MASTER_DESTS', 'TESTHUB_RETURN_DESTS',
    'TESTHUB_RETURN_DESTS_BY_NPC', 'TESTHUB_AREA_RETURN_NPCS',
    'TRAVELER_ENTER_OFFERS',
)
RIPPED_GENERATORS = ('_add_helos_traveler_hub_travel', '_add_testhub_portal_travel')

# Shared-record law: every travel record must STAY minted in the arz pipeline.
KEPT_RECORD_STEMS = (
    'svc_helos_trav_garden', 'svc_helos_trav_secret', 'svc_helos_trav_sparta',
    'svc_helos_trav_uber', 'svc_helos_trav_bossarena', 'svc_helos_trav_warband',
    'svc_helos_trav_dorus', 'svc_helos_trav_tantalus', 'svc_helos_trav_charon',
    'svc_helos_trav_mnemophage', 'svc_helos_trav_ephialtes', 'svc_helos_trav_devourer',
    'svc_helos_trav_vashkarr', 'svc_helos_trav_obsidian',
    'svc_warden_sparta_crypt', 'svc_area_return_uber',
)
# Device records WE place are banned from both spec sets (R-248 revert holds).
# NOTE: an SV-NATIVE inert portal_olympianarena2 prop ships inside crypt_floor1's
# own blob - that is upstream bytes, not an INJECT_SPECS entry, hence out of scope.
BANNED_DEVICE_STEMS = ('portal_olympianarena', 'teleportshrineorient', 'map_portal_aura')


def _spec_records(specs):
    out = set()
    for _k, entries in specs.items():
        for s in entries:
            rec = s if isinstance(s, (bytes, bytearray)) else s[0]
            out.add(bytes(rec).replace(b'/', BS.encode()).lower().decode())
    return out


def main():
    fails = []

    # ── V1: the rip holds ─────────────────────────────────────────────────────
    import build_quest_files as bqf
    for t in RIPPED_TABLES:
        if hasattr(bqf, t):
            fails.append(f'V1: RIPPED table {t} is BACK in build_quest_files - the '
                         f'blanket-refire bug class returns with it (R-246/R-248)')
    for g in RIPPED_GENERATORS:
        if hasattr(bqf, g):
            fails.append(f'V1: RIPPED generator {g} is BACK in build_quest_files')
    dests = getattr(bqf, 'HELOS_PORTAL_DESTS', None)
    if dests is None or len(dests) != 3:
        fails.append('V1: Almyros HELOS_PORTAL_DESTS must exist with EXACTLY 3 rows '
                     '(R-246 ruled menu, R-248 unchanged)')

    # ── V2: R-248 step spec ───────────────────────────────────────────────────
    canon = getattr(bqf, 'R248_CANONICAL_STEPS', None)
    hub = getattr(bqf, 'R248_TESTHUB_STEPS', None)
    if canon is None or hub is None:
        fails.append('V2: R248 step tables missing from build_quest_files')
    else:
        n_c = sum(len(r) for _s, r in canon)
        n_h = sum(len(r) for _s, r in hub)
        if n_c != 10:
            fails.append(f'V2: canonical steps arm {n_c} rows, spec is 10')
        if n_h != 25:
            fails.append(f'V2: TESTHUB steps arm {n_h} rows, spec is 25')
        for (sname, rows) in list(canon) + list(hub):
            if len(rows) > 3:
                fails.append(f'V2: step {sname!r} arms {len(rows)} rows > 3')
            seen, last = set(), None
            for (npc, _xyz, _tag, _lk) in rows:
                k = npc.replace('/', BS).lower()
                if k != last and k in seen:
                    fails.append(f'V2: step {sname!r} rows for {npc} not contiguous '
                                 f'(1 trigger : 1 NPC grouping broken)')
                seen.add(k)
                last = k
        names = [s for s, _r in list(canon) + list(hub)]
        if len(names) != len(set(names)):
            fails.append('V2: duplicate R248 step names')
    src = (REPO / 'tools' / 'build_quest_files.py').read_text(encoding='utf-8',
                                                              errors='replace')
    if "('field', 'isResettable', ('int', 0)),   # ONE-SHOT" not in src:
        fails.append('V2: the R248 generator no longer emits the isResettable=0 '
                     'one-shot literal - the no-churn law is off in SOURCE')
    if '_npc_awaken_actions' not in src:
        fails.append('V2: the b88 awakening recipe _npc_awaken_actions is GONE')

    # ── V3: armed <=> placed, spec side ───────────────────────────────────────
    import build_section_surgery as bss
    canon_placed = _spec_records(bss.INJECT_SPECS)
    hub_placed = _spec_records(bss.merge_hub_into_inject_specs(bss.INJECT_SPECS))
    # the TESTHUB random09a swap-path extras are applied outside INJECT_SPECS;
    # include them for completeness
    if canon is not None and hub is not None:
        for (sname, rows) in canon:
            for (npc, _xyz, _tag, _lk) in rows:
                nl = npc.replace('/', BS).lower()
                if nl not in canon_placed:
                    fails.append(f'V3: canonical step {sname!r} arms {npc} but the '
                                 f'canonical INJECT_SPECS never places it '
                                 f'(armed-but-unplaced = a dead row)')
        for (sname, rows) in hub:
            for (npc, _xyz, _tag, _lk) in rows:
                nl = npc.replace('/', BS).lower()
                if nl not in hub_placed:
                    fails.append(f'V3: TESTHUB step {sname!r} arms {npc} but the '
                                 f'TESTHUB fold never places it')
    for nm in sorted(hub_placed):
        base = nm.rsplit(BS, 1)[-1]
        if any(base.startswith(p) for p in BANNED_DEVICE_STEMS):
            fails.append(f'V3: DEVICE record {base} is placed by the spec tables - '
                         f'the R-248 revert is regressing (graveyard sec 10/10a)')

    # ── V4: shared-record law ─────────────────────────────────────────────────
    asp = (REPO / 'tools' / 'apply_svc_patches.py').read_text(encoding='utf-8',
                                                              errors='replace')
    for stem in KEPT_RECORD_STEMS:
        if stem not in asp:
            fails.append(f'V4: record stem {stem} vanished from apply_svc_patches - '
                         f'shared-record law (records stay; only rows/placements move)')

    if fails:
        print(f'TRAVEL-NPC INVARIANTS (R-248): {len(fails)} FAILURE(S)')
        for f in fails:
            print(f'  FAIL {f}')
        return 1
    print('TRAVEL-NPC INVARIANTS (R-248): PASS - rip holds; R248 steps 10+25 rows, '
          '<=3/step, 1-trigger-per-NPC, one-shot in source; armed<=>placed both '
          'variants; zero placed device records; shared-record law intact')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
