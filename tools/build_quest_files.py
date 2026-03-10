"""
Build custom quest files and patch them into the mod's Quests.arc.

Strategy: Build a combined portal quest with all 4 portals (uber dungeon entrance/
return, blood cave entrance/return) and inject it into the sv_commonmechanics.qst
slot, which is the only quest slot proven to load in Custom Quest mode.

Each quest step has 4 triggers (one per portal), each with OnLevelLoad condition
and ShowNpc + UpdateNpcDialog + BoatDialog actions. Steps are repeated ~200 times
because TQ advances through steps sequentially and the actions only take effect
when the target NPC's level is loaded.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from qst_format import (
    Quest, QuestStep, Trigger, build_quest,
    make_on_level_load_condition,
    make_show_npc_action,
    make_update_npc_dialog_action,
    make_boat_dialog_action,
)

# Use EXISTING NPCs already placed by the level editor (real game entities)
# Binary 0x05 injection creates rendered meshes but NOT interactive entities
ENTRANCE_NPC = r'Records\Creature\NPC\Merchants\Greece\Merchant_Delphi_Quest.dbr'
RETURN_NPC = r'records\quests\portal_uberdungeon_return.dbr'
BLOODCAVE_ENTRANCE_NPC = r'records\creature\npc\speaking\orient\silkroad_villager1.dbr'
BLOODCAVE_RETURN_NPC = r'records\quests\portal_bloodcave_return.dbr'

# BoatDialog coords: world-space position where the player spawns.
# Must be within the walkable area of the destination level's DATA2 grid.
# DATA2 grid scale: 4 cells per world unit.
# Walkable center = grid_origin + (center_col/4, 0, center_row/4)
CRYPT_FLOOR1_X, CRYPT_FLOOR1_Y, CRYPT_FLOOR1_Z = -8148, 0, -256  # DIAG14: ruinedcity02 (idx 30, SV blob swap test)
DELPHI04_X, DELPHI04_Y, DELPHI04_Z = -8868, 0, -832  # outdoor, grid origin is walkable

# Blood cave entrance: bc_initialpathway walkable center (shifted grid)
# Grid shift (+1663, 0, +922) → new grid origin (-438, 18, 2215)
# Local walkable center (41, 0, 29) → world (-397, 18, 2244)
BC_INITIAL_X, BC_INITIAL_Y, BC_INITIAL_Z = -397, 18, 2244
# Return to HiddenValley01: confirmed walkable near the cave entrance NPC
HIDDENVALLEY01_X, HIDDENVALLEY01_Y, HIDDENVALLEY01_Z = -118, -102, 2200

REPEAT_STEPS = 200

DIALOG_NEEDED_DBR = r'Records\Dialog\Story\Dialog Needed.dbr'

# Portal definitions: (npc_dbr, tag, x, y, z)
PORTALS = [
    (ENTRANCE_NPC, 'tagNewPortal1Desc', CRYPT_FLOOR1_X, CRYPT_FLOOR1_Y, CRYPT_FLOOR1_Z),
    (RETURN_NPC, 'tagNewPortal1Desc', DELPHI04_X, DELPHI04_Y, DELPHI04_Z),
    (BLOODCAVE_ENTRANCE_NPC, 'tagNewPortal1Desc', BC_INITIAL_X, BC_INITIAL_Y, BC_INITIAL_Z),
    (BLOODCAVE_RETURN_NPC, 'tagNewPortal1Desc', HIDDENVALLEY01_X, HIDDENVALLEY01_Y, HIDDENVALLEY01_Z),
]


def _make_combined_portal_quest() -> bytes:
    """Build a single quest with all portal triggers in each step."""
    quest = Quest(title='Portal System')
    triggers = []
    for npc_dbr, tag, x, y, z in PORTALS:
        triggers.append(Trigger(
            display_tag='New Trigger',
            conditions=[make_on_level_load_condition()],
            actions=[
                make_show_npc_action(npc_dbr, can_refire=1),
                make_update_npc_dialog_action(npc_dbr, DIALOG_NEEDED_DBR),
                make_boat_dialog_action(npc_dbr, tag, x, y, z),
            ],
        ))
    step = QuestStep(name='Portal Setup', triggers=triggers)
    for _ in range(REPEAT_STEPS):
        quest.steps.append(step)
    return build_quest(quest)


def main():
    # Build combined portal quest
    portal_qst = _make_combined_portal_quest()
    print(f'Built combined portal quest ({len(portal_qst)} bytes, {len(PORTALS)} portals)')

    # Start from SVAERA's original Quests.arc (clean)
    svaera_quests = Path(r'reference_mods\SVAERA_customquest\Resources\Quests.arc')
    quests_arc_path = Path(r'work\SoulvizierClassic\Resources\Quests.arc')

    import shutil
    if svaera_quests.exists():
        shutil.copy2(svaera_quests, quests_arc_path)
        print(f'Restored clean Quests.arc from SVAERA ({quests_arc_path.stat().st_size / 1024:.1f} KB)')

    # Replace sv_commonmechanics.qst with our combined portal quest
    # This is the ONLY quest slot proven to load in Custom Quest mode
    arc = ArcArchive.from_file(quests_arc_path)
    replaced = False
    for e in arc.entries:
        if 'sv_commonmechanics' in e.name.lower():
            arc.set_file(e.name, portal_qst)
            replaced = True
            print(f'Replaced {e.name} with portal quest')
            break
    if not replaced:
        print('WARNING: sv_commonmechanics.qst not found in Quests.arc!')

    arc.write(quests_arc_path)
    print(f'  ARC size: {quests_arc_path.stat().st_size / 1024:.1f} KB')

    # Verify
    arc2 = ArcArchive.from_file(quests_arc_path)
    for e in arc2.entries:
        if 'sv_commonmechanics' in e.name.lower():
            print(f'  sv_commonmechanics.qst: {e.decomp_size} bytes')


if __name__ == '__main__':
    main()
