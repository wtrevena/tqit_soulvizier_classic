"""
Build custom quest files and patch them into the mod's Quests.arc.

Creates two quest files for the Uber Dungeon portal system:
- uberdungeon_entrance.qst: configures entrance portal at Crisaeos Falls
- uberdungeon_return.qst: configures return portal inside the Uber Dungeon

Each quest has many repeated OnLevelLoad steps because the TQ quest system
advances through steps sequentially. BoatDialog/ShowNpc only take effect when
the target NPC's level is loaded. By repeating the step ~200 times, we ensure
the actions fire successfully regardless of how many level transitions the
player makes before reaching the portal.
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

ENTRANCE_NPC = r'records\quests\portal_uberdungeon_entrance.dbr'
RETURN_NPC = r'records\quests\portal_uberdungeon_return.dbr'
BLOODCAVE_ENTRANCE_NPC = r'records\quests\portal_bloodcave_entrance.dbr'
BLOODCAVE_RETURN_NPC = r'records\quests\portal_bloodcave_return.dbr'

# Grid-space coordinates (from level index ints_raw[6,7,8])
# Using SVAERA's coordinates since we use SVAERA's base map
CRYPT_FLOOR1_X, CRYPT_FLOOR1_Y, CRYPT_FLOOR1_Z = -2498, 0, -2602
DELPHI04_X, DELPHI04_Y, DELPHI04_Z = -8868, 0, -832  # SVAERA coords (was -8836,0,-800 for SV)

# Blood cave coordinates (SV-only levels, coords from SV's level index)
BC_INITIAL_X, BC_INITIAL_Y, BC_INITIAL_Z = -2101, 18, 1293
HIDDENVALLEY01_X, HIDDENVALLEY01_Y, HIDDENVALLEY01_Z = -134, -120, 2174

REPEAT_STEPS = 200


DIALOG_NEEDED_DBR = r'Records\Dialog\Story\Dialog Needed.dbr'


def _make_portal_quest(title, npc_dbr, tag, x, y, z) -> bytes:
    quest = Quest(title=title)
    step = QuestStep(
        name='Portal Setup',
        triggers=[Trigger(
            display_tag='New Trigger',
            conditions=[make_on_level_load_condition()],
            actions=[
                make_show_npc_action(npc_dbr, can_refire=1),
                make_update_npc_dialog_action(npc_dbr, DIALOG_NEEDED_DBR),
                make_boat_dialog_action(npc_dbr, tag, x, y, z),
            ],
        )]
    )
    for _ in range(REPEAT_STEPS):
        quest.steps.append(step)
    return build_quest(quest)


def main():
    # Build all quest files
    quest_files = {}

    quest_files['uberdungeon_entrance.qst'] = _make_portal_quest(
        'Uber Dungeon Entrance',
        ENTRANCE_NPC, 'tagNewPortal1Desc',
        CRYPT_FLOOR1_X, CRYPT_FLOOR1_Y, CRYPT_FLOOR1_Z,
    )
    print(f'Built uberdungeon_entrance.qst ({len(quest_files["uberdungeon_entrance.qst"])} bytes)')

    quest_files['uberdungeon_return.qst'] = _make_portal_quest(
        'Uber Dungeon Return',
        RETURN_NPC, 'tagNewPortal1Desc',
        DELPHI04_X, DELPHI04_Y, DELPHI04_Z,
    )
    print(f'Built uberdungeon_return.qst ({len(quest_files["uberdungeon_return.qst"])} bytes)')

    quest_files['bloodcave_entrance.qst'] = _make_portal_quest(
        'Blood Cave Entrance',
        BLOODCAVE_ENTRANCE_NPC, 'tagNewPortal1Desc',
        BC_INITIAL_X, BC_INITIAL_Y, BC_INITIAL_Z,
    )
    print(f'Built bloodcave_entrance.qst ({len(quest_files["bloodcave_entrance.qst"])} bytes)')

    quest_files['bloodcave_return.qst'] = _make_portal_quest(
        'Blood Cave Return',
        BLOODCAVE_RETURN_NPC, 'tagNewPortal1Desc',
        HIDDENVALLEY01_X, HIDDENVALLEY01_Y, HIDDENVALLEY01_Z,
    )
    print(f'Built bloodcave_return.qst ({len(quest_files["bloodcave_return.qst"])} bytes)')

    # Start from SVAERA's original Quests.arc (clean, no accumulated junk)
    svaera_quests = Path(r'reference_mods\SVAERA_customquest\Resources\Quests.arc')
    quests_arc_path = Path(r'work\SoulvizierClassic\Resources\Quests.arc')

    import shutil
    if svaera_quests.exists():
        shutil.copy2(svaera_quests, quests_arc_path)
        print(f'Restored clean Quests.arc from SVAERA ({quests_arc_path.stat().st_size / 1024:.1f} KB)')

    # Add quest files using arc_patcher with correct filenames
    # NOTE: ArchiveTool stores full temp paths — do NOT use it
    arc = ArcArchive.from_file(quests_arc_path)
    for name, data in quest_files.items():
        arc.add_file(name, data)
    arc.write(quests_arc_path)
    print(f'Added {len(quest_files)} quest files via arc_patcher')
    print(f'  ARC size: {quests_arc_path.stat().st_size / 1024:.1f} KB')

    # Verify entries
    arc2 = ArcArchive.from_file(quests_arc_path)
    custom_found = sum(1 for e in arc2.entries if any(
        q in e.name.lower() for q in ['bloodcave', 'uberdungeon']))
    print(f'  Custom quest entries in ARC: {custom_found}')


if __name__ == '__main__':
    main()
