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
    make_boat_dialog_action,
)

ENTRANCE_NPC = 'records/quests/portal_uberdungeon_entrance.dbr'
RETURN_NPC = 'records/quests/portal_uberdungeon_return.dbr'

# Grid-space coordinates (from level index ints_raw[6,7,8] + dims/2)
CRYPT_FLOOR1_X, CRYPT_FLOOR1_Y, CRYPT_FLOOR1_Z = -2498, 0, -2602
DELPHI04_X, DELPHI04_Y, DELPHI04_Z = -8836, 0, -800

REPEAT_STEPS = 200


def _make_portal_quest(title, npc_dbr, tag, x, y, z) -> bytes:
    quest = Quest(title=title)
    step = QuestStep(
        name='Portal Setup',
        triggers=[Trigger(
            display_tag='New Trigger',
            conditions=[make_on_level_load_condition()],
            actions=[
                make_show_npc_action(npc_dbr, can_refire=1),
                make_boat_dialog_action(npc_dbr, tag, x, y, z),
            ],
        )]
    )
    for _ in range(REPEAT_STEPS):
        quest.steps.append(step)
    return build_quest(quest)


def main():
    entrance_data = _make_portal_quest(
        'Uber Dungeon Entrance',
        ENTRANCE_NPC, 'tagNewPortal1Desc',
        CRYPT_FLOOR1_X, CRYPT_FLOOR1_Y, CRYPT_FLOOR1_Z,
    )
    print(f'Built uberdungeon_entrance.qst ({len(entrance_data)} bytes)')

    return_data = _make_portal_quest(
        'Uber Dungeon Return',
        RETURN_NPC, 'tagNewPortal1Desc',
        DELPHI04_X, DELPHI04_Y, DELPHI04_Z,
    )
    print(f'Built uberdungeon_return.qst ({len(return_data)} bytes)')

    quests_arc_path = Path(r'work\SoulvizierClassic\Resources\Quests.arc')
    if not quests_arc_path.exists():
        for p in Path(r'work\SoulvizierClassic\Resources').rglob('Quests.arc'):
            quests_arc_path = p
            break

    # Write .qst files to a temp directory, then use ArchiveTool to add them
    # to the existing Quests.arc.  This preserves the original arc binary
    # format (our arc_patcher rewrite changes compression/alignment and may
    # produce arcs TQ cannot read).
    import tempfile, shutil, subprocess, os

    tmp_dir = Path(tempfile.mkdtemp(prefix='svc_quests_'))
    try:
        (tmp_dir / 'uberdungeon_entrance.qst').write_bytes(entrance_data)
        (tmp_dir / 'uberdungeon_return.qst').write_bytes(return_data)

        if quests_arc_path.exists():
            archive_tool = os.environ.get('TQ_ARCHIVETOOL', '')
            if not archive_tool or not Path(archive_tool).exists():
                archive_tool = (
                    r'C:\Program Files (x86)\Steam\steamapps\common'
                    r'\Titan Quest Anniversary Edition\ArchiveTool.exe'
                )

            if Path(archive_tool).exists():
                result = subprocess.run(
                    [archive_tool, str(quests_arc_path), '-add',
                     str(tmp_dir), str(tmp_dir), '9'],
                    capture_output=True, text=True,
                )
                if result.returncode == 0:
                    print(f'Added quest files via ArchiveTool')
                    print(f'  ARC size: {quests_arc_path.stat().st_size / 1024:.1f} KB')
                else:
                    print(f'WARNING: ArchiveTool failed: {result.stderr}')
                    print('Falling back to arc_patcher...')
                    arc = ArcArchive.from_file(quests_arc_path)
                    arc.add_file('uberdungeon_entrance.qst', entrance_data)
                    arc.add_file('uberdungeon_return.qst', return_data)
                    arc.write(quests_arc_path)
                    print(f'Patched via arc_patcher: {quests_arc_path.stat().st_size / 1024:.1f} KB')
            else:
                print('WARNING: ArchiveTool not found, using arc_patcher')
                arc = ArcArchive.from_file(quests_arc_path)
                arc.add_file('uberdungeon_entrance.qst', entrance_data)
                arc.add_file('uberdungeon_return.qst', return_data)
                arc.write(quests_arc_path)
                print(f'Patched via arc_patcher: {quests_arc_path.stat().st_size / 1024:.1f} KB')
        else:
            (Path('local') / 'uberdungeon_entrance.qst').write_bytes(entrance_data)
            (Path('local') / 'uberdungeon_return.qst').write_bytes(return_data)
            print('WARNING: Quests.arc not found, wrote standalone files to local/')
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    main()
