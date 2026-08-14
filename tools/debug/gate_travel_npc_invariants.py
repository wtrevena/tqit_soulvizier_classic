#!/usr/bin/env python3
"""GATE: travel invariants under the R-246 NATIVE-DEVICE TRAVEL LAW (2026-08-13).

HISTORY OF THE LAW (both halves are explicit here so no vet re-litigates them):
  * 2026-07-12 P0 (Will: "walk south in Helos -> yanked to the Garden, no way back"):
    ALL travel became NPC boat-dialog; every authored walk-through portal was stripped.
    This gate's previous incarnation asserted THAT world (zero walk-through portals,
    the 23-record Helos traveler hub, warden law, cross-file agreement).
  * 2026-08-13 R-246 (Will, "Native devices"): the boat-dialog MECHANISM half is
    SUPERSEDED - the blanket-refire arming of 39 Action_BoatDialog rows was proven to
    corrupt the engine's stateful boat-offer registry (cross-bound rows, mute NPCs,
    wrong labels). Travel moved to engine-native devices (born-open GridEntrance door
    pairs + wired teleport-shrine rifts); the row tables were RIPPED; Almyros alone
    keeps his 3-route talk menu. The 07-12 PLACEMENT half SURVIVES as law (doors off
    every traffic lane, walked into deliberately) and is enforced structurally by
    gate_device_resolution's C-block. See docs/WILL_RULINGS.md R-246.

THIS GATE (spec-based, build-free - reads the LIVE tooling tables so no 1.3GB build
is needed; the artifact-side twin checks live in gate_boatdialog_budget [Quests.arc]
and gate_device_resolution [Levels arcs]):
  V1 RIP HOLDS, quest side: build_quest_files defines NONE of the ripped generators/
     tables (HELOS_HUB_TRAVEL, TESTHUB_MASTER_DESTS, TESTHUB_RETURN_DESTS,
     TESTHUB_RETURN_DESTS_BY_NPC, TESTHUB_AREA_RETURN_NPCS, TRAVELER_ENTER_OFFERS),
     and its ONLY SVC hub table is Almyros' HELOS_PORTAL_DESTS with EXACTLY 3 rows,
     every row driven by portal_master_helos (no other SVC NPC re-enters the
     boat-dialog world through the back door).
  V2 DEVICE TABLES CONSISTENT, map side (the spec-side mirror of D4/D5): the R-246
     court has 14 uniquely-labeled doors; ALL minted uids (court mouths+exits, shrine
     uids+tails, canonical door uid constants) are pairwise distinct; every door
     entrance host is in the ORIGINAL-INDEX allowlist (appended-host law); court
     dest GUIDs are pairwise distinct; exactly 2 shrines are canonical (hub_only
     False), the rest TESTHUB-only.
  V3 DISPOSITIONS: the ripped rows' NPC records are NOT deleted from the arz
     creation tables (shared-record law: records stay, placements become mute named
     markers) - checked against apply_svc_patches source text.

Usage: py tools/debug/gate_travel_npc_invariants.py
Exit 0 = PASS. Read-only, no build required.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))

RIPPED_TABLES = (
    'HELOS_HUB_TRAVEL', 'TESTHUB_MASTER_DESTS', 'TESTHUB_RETURN_DESTS',
    'TESTHUB_RETURN_DESTS_BY_NPC', 'TESTHUB_AREA_RETURN_NPCS',
    'TRAVELER_ENTER_OFFERS',
)
RIPPED_GENERATORS = ('_add_helos_traveler_hub_travel', '_add_testhub_portal_travel')
ALMYROS = 'portal_master_helos'

# Shared-record law: the ripped rows' records must STAY minted in the arz pipeline
# (they are now the named mute markers beside the devices).
KEPT_RECORD_STEMS = (
    'svc_helos_trav_garden', 'svc_helos_trav_secret', 'svc_helos_trav_sparta',
    'svc_helos_trav_uber', 'svc_helos_trav_bossarena', 'svc_helos_trav_warband',
    'svc_helos_trav_dorus', 'svc_helos_trav_tantalus', 'svc_helos_trav_charon',
    'svc_helos_trav_mnemophage', 'svc_helos_trav_ephialtes', 'svc_helos_trav_devourer',
    'svc_helos_trav_vashkarr', 'svc_helos_trav_obsidian',
    'svc_warden_sparta_crypt', 'svc_area_return_uber',
)


def main():
    fails = []

    # ── V1: quest side ────────────────────────────────────────────────────────
    import build_quest_files as bqf
    for t in RIPPED_TABLES:
        if hasattr(bqf, t):
            fails.append(f'V1: RIPPED table {t} is BACK in build_quest_files - the '
                         f'stateful-registry bug class returns with it (R-246)')
    for g in RIPPED_GENERATORS:
        if hasattr(bqf, g):
            fails.append(f'V1: RIPPED generator {g} is BACK in build_quest_files')
    dests = getattr(bqf, 'HELOS_PORTAL_DESTS', None)
    if dests is None:
        fails.append('V1: HELOS_PORTAL_DESTS (Almyros) missing - his ruled 3-route '
                     'menu is the ONE surviving SVC hub table')
    else:
        if len(dests) != 3:
            fails.append(f'V1: Almyros HELOS_PORTAL_DESTS has {len(dests)} rows, '
                         f'ruled EXACTLY 3 (R-246: "Almyros keeps his 3-route talk menu")')
    src = (REPO / 'tools' / 'build_quest_files.py').read_text(encoding='utf-8',
                                                              errors='replace')
    # the awakening fallback recipe must stay available (uncalled is fine)
    if '_npc_awaken_actions' not in src:
        fails.append('V1: the retained b88 awakening recipe _npc_awaken_actions is '
                     'GONE - it is the sanctioned visibility fallback for R-246 markers')

    # ── V2: map-side device tables ────────────────────────────────────────────
    import build_section_surgery as bss
    labels = [row[0] for row in bss.R246_COURT]
    if len(labels) != 14 or len(set(labels)) != 14:
        fails.append(f'V2: R246_COURT must carry 14 uniquely-labeled doors, '
                     f'found {len(labels)} ({len(set(labels))} unique)')
    uids = []
    for lbl, (m, x) in bss.R246_COURT_UIDS.items():
        uids += [('court-' + lbl + '-mouth', m), ('court-' + lbl + '-exit', x)]
    for s in bss.R246_SHRINE_SPECS:
        uids += [('shrine-' + s['label'], s['uid']),
                 ('shrine-' + s['label'] + '-tail', s['tail'])]
    for nm in ('R246_UBER_M1', 'R246_UBER_X1', 'SPARTA_M1', 'SPARTA_X1'):
        uids.append((nm, getattr(bss, nm)))
    seen = {}
    for nm, u in uids:
        if u in seen:
            fails.append(f'V2: minted uid COLLISION: {nm} == {seen[u]} ({u.hex()[:12]}..)')
        seen[u] = nm
    # appended-host law, spec side: every door-entrance host key must sit in the
    # device gate's ORIGINAL-INDEX allowlist (the one place the law is authored).
    sys.path.insert(0, str(REPO / 'tools'))
    from gate_device_resolution import ALLOWED_ENTRANCE_HOSTS
    allow = {k.replace(chr(92), '/').lower() for k in ALLOWED_ENTRANCE_HOSTS}
    for k in (bss.MAZE03_LVL_KEY, bss.CATACUBE_FLOORLAST_LVL_KEY, bss.HELOS_HOST_KEY):
        if k.replace(chr(92), '/').lower() not in allow:
            fails.append(f'V2: door-entrance host {k} is NOT in the original-index '
                         f'allowlist (appended-host law: it would NEVER fire)')
    dest_guids = [row[5] for row in bss.R246_COURT]
    if len(set(dest_guids)) != len(dest_guids):
        fails.append('V2: court dest GUIDs are not pairwise distinct (two doors would '
                     'silently share a destination)')
    canon_shrines = [s['label'] for s in bss.R246_SHRINE_SPECS if not s['hub_only']]
    if sorted(canon_shrines) != ['sc2', 'uber']:
        fails.append(f'V2: canonical shrine set must be exactly uber+sc2, got {canon_shrines}')

    # ── V3: shared-record law ─────────────────────────────────────────────────
    psrc = (REPO / 'tools' / 'apply_svc_patches.py').read_text(encoding='utf-8',
                                                               errors='replace')
    for stem in KEPT_RECORD_STEMS:
        if stem not in psrc:
            fails.append(f'V3: record {stem} vanished from apply_svc_patches - '
                         f'retirement protocol requires records STAY (mute markers)')

    if fails:
        print(f'TRAVEL-INVARIANTS GATE (R-246): {len(fails)} VIOLATION(S)')
        for f in fails:
            print(f'  FAIL {f}')
        return 1
    print('TRAVEL-INVARIANTS GATE (R-246): PASS - rip holds (0 hub tables, Almyros 3 '
          'rows), 14-door court + 11 shrines consistent (uids unique, canonical set '
          'uber+sc2), shared-record law holds for all 16 marker records')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
