"""
Build custom quest files and patch them into the mod's Quests.arc.

Two independent quest payloads are written into the mod's Quests.arc:

1. The combined PORTAL quest (title "Portal System"): all portals (uber dungeon
   entrance/return, blood cave entrance/return) built into the sv_commonmechanics.qst
   slot, which is the quest slot proven to load in Custom Quest mode. Each step has a
   trigger per portal with an OnLevelLoad condition plus ShowNpc + UpdateNpcDialog +
   BoatDialog actions; steps repeat ~200 times because TQ advances through steps
   sequentially and the actions only take effect when the target NPC's level is loaded.
   This drives ENTRY into the Soulvizier areas (e.g. the blood cave via HiddenValley01).

2. The Soulvizier AREA questlines (blood cave interior, uber dungeon, widow letter,
   boss arena): the original SV .qst files, ported byte-for-byte from upstream into the
   Quests.arc root ALONGSIDE (never replacing) the portal quest. Their names are already
   registered in the deployed map's QUESTS section and their trigger volumes / proxies /
   doors / portals are already placed in the level blobs, so backing them here (a
   Quests.arc-only change, no map rebuild) makes the questlines live. See PORT_QUESTS.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
import qst_format
from qst_format import (
    Quest, QuestStep, Trigger, build_quest,
    make_on_level_load_condition,
    make_show_npc_action,
    make_update_npc_dialog_action,
    make_boat_dialog_action,
)

REPEAT_STEPS = 200

DIALOG_NEEDED_DBR = r'Records\Dialog\Story\Dialog Needed.dbr'

# Portal definitions: (npc_dbr, tag, x, y, z)
# The blood-cave entrance/return portal HACK has been REMOVED (blood-cave walk-in):
# the authentic SV entry is engine-native (HiddenValley01's GridEntrance cave mouth
# streams in the blob-swapped Random09A whose west tunnel leads into the blood cave;
# the reciprocal walk-out returns to HiddenValley01). No quest-driven teleport is
# needed. PORTALS is intentionally empty; when empty, the sv_commonmechanics portal
# quest is left untouched (see main()) so no degenerate empty quest is written.
PORTALS = []

# ── Soulvizier area questlines ───────────────────────────────────────────────
# Source .qst files live in upstream SV 0.98i's XPack Quests.arc. They round-trip
# byte-exact through qst_format. Each name below is ALREADY registered in the
# deployed map's QUESTS section (as Quests/<name> and/or XPack/Quests/<name>), and
# the shipped Quests.arc stores every quest at the ARCHIVE ROOT (basename only) --
# the engine strips the folder prefix to the basename and resolves it at the root.
# So we add these at the root, mirroring how the other ~100 quests are stored.
UPSTREAM_SV_QUESTS = Path(
    r'upstream\soulvizier_098i\Resources\XPack\Quests.arc')

# Quests to port verbatim (records + tags all resolve in the built .arz / Text.arc).
PORT_QUESTS = [
    'urder.qst',       # uber dungeon questline (20 records, 3 tags; all present)
    'widowletter.qst', # widow letter questline (16 records, 4 tags; all present)
    'bossarena.qst',   # boss arena (4 records, 0 tags; all present)
]

# Blood cave interior questline. Ported like the others EXCEPT one v1 surgical edit:
# STEP 3 ("Duister") TRIGGER 1 ("Duister PortalDude") drives the LOST original terrain
# entrance at the Garden of Merchants -- its ShowNpc/BoatDialog target
# records\creature\npc\speaking\greece\starting_storyteller.dbr ("Duister") does NOT
# exist in the built .arz (it belonged to the terrain doorway the SVAERA merge dropped;
# the quest-portal replaced that entry path). That single trigger is the ONLY broken
# reference in the whole quest. For v1 we NEUTRALIZE just that trigger (see
# _neutralize_bloodcave_entry_step) and rely on the already-fixed HiddenValley01 portal
# in the sv_commonmechanics portal quest for blood-cave entry. Every other trigger --
# the interior doors/portals/boss traps (steps 0-2), the two OTHER Garden-of-Merchants
# triggers in step 3 (OCV token + merchant reveals, whose records DO exist), and the
# hidden-chest rewards (step 4) -- is left byte-identical to upstream.
BLOODCAVE_INTERIOR_QUEST = 'open_bloodcave_portal.qst'

# The lost-terrain NPC that marks the trigger to neutralize.
BLOODCAVE_LOST_NPC = r'records\creature\npc\speaking\greece\starting_storyteller.dbr'


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


# ── Soulvizier area-quest porting ────────────────────────────────────────────

def _open_upstream_arc() -> ArcArchive:
    if not UPSTREAM_SV_QUESTS.exists():
        raise FileNotFoundError(
            f'Upstream SV Quests.arc not found at {UPSTREAM_SV_QUESTS}; '
            f'cannot port the SV area questlines.')
    return ArcArchive.from_file(UPSTREAM_SV_QUESTS)


def _upstream_quest_bytes(arc: ArcArchive, basename: str) -> bytes:
    """Return the raw bytes of an upstream .qst by basename (archive stores at root)."""
    bl = basename.lower()
    for e in arc.entries:
        if e.entry_type != 3:
            continue
        n = e.name.lower()
        if n == bl or n.endswith('/' + bl) or n.endswith('\\' + bl):
            return arc.decompress(e)
    raise KeyError(f'{basename} not found in {UPSTREAM_SV_QUESTS}')


def _assert_roundtrip(basename: str, data: bytes):
    """Fail loud if the .qst does not survive a parse->serialize round-trip byte-exact."""
    rebuilt = qst_format.serialize(qst_format.parse(data))
    if rebuilt != data:
        raise ValueError(
            f'{basename}: qst_format round-trip is NOT byte-exact '
            f'({len(rebuilt)} vs {len(data)} bytes); refusing to ship a mangled quest.')


def _neutralize_bloodcave_entry_step(data: bytes) -> bytes:
    """Drop STEP 3's single trigger that targets the lost terrain NPC.

    Parses open_bloodcave_portal.qst, finds the one trigger in the "Duister" step
    whose actions reference BLOODCAVE_LOST_NPC (starting_storyteller.dbr, absent from
    the .arz), removes that trigger's (header, conditions, actions) block group, and
    decrements the step's trigger-container `max`. Everything else is untouched. The
    result is re-serialized through qst_format (still a valid, stable round-trip).

    qst tree layout: tree = [header_block, steps_container]. The steps container's
    sub-blocks come in flat triples per step: (stepdef, trigger_container, sentinel).
    A trigger container holds a `max` field then flat triples per trigger:
    (trigger_header, conditions, actions). The sentinel trigger is its own separate
    block after the container, so decrementing `max` and dropping one trigger triple
    is sufficient and safe.
    """
    needle = BLOODCAVE_LOST_NPC.replace('\\', '/').lower()

    def block_mentions(items, s):
        hit = False
        def walk(its):
            nonlocal hit
            for it in its:
                if it[0] == 'block':
                    walk(it[1])
                elif (it[0] == 'field' and it[2][0] == 'str'
                        and it[2][1].replace('\\', '/').lower() == s):
                    hit = True
        walk(items)
        return hit

    def block_positions(items):
        return [i for i, it in enumerate(items) if it[0] == 'block']

    tree = qst_format.parse(data)
    steps_container = tree[1]
    step_triples = [block_positions(steps_container)[i:i + 3]
                    for i in range(0, len(block_positions(steps_container)), 3)]

    removed = 0
    for stepdef_pos, trigcont_pos, sentinel_pos in step_triples:
        trigcont = steps_container[trigcont_pos][1]
        tg = [block_positions(trigcont)[i:i + 3]
              for i in range(0, len(block_positions(trigcont)), 3)]
        # find trigger group(s) whose actions block references the lost NPC
        drop = set()
        n_before = len(tg)
        for (hpos, cpos, apos) in tg:
            if block_mentions(trigcont[apos][1], needle):
                drop.update((hpos, cpos, apos))
                removed += 1
        if not drop:
            continue
        new_trigcont = [it for i, it in enumerate(trigcont) if i not in drop]
        # decrement max by the number of trigger groups dropped
        n_dropped = len({p for grp in tg for p in grp if p in drop}) // 3
        for idx, it in enumerate(new_trigcont):
            if it[0] == 'field' and it[1] == 'max':
                new_trigcont[idx] = ('field', 'max', ('int', n_before - n_dropped))
                break
        steps_container[trigcont_pos] = ('block', new_trigcont)

    if removed != 1:
        raise ValueError(
            f'{BLOODCAVE_INTERIOR_QUEST}: expected exactly 1 trigger referencing '
            f'{BLOODCAVE_LOST_NPC}, found {removed}. Upstream changed; review before '
            f'shipping.')

    out = qst_format.serialize(tree)
    # sanity: re-parse and confirm the reference is gone and the file is stable
    if block_mentions(qst_format.parse(out), needle):
        raise ValueError('neutralization failed: lost-NPC reference still present')
    if qst_format.serialize(qst_format.parse(out)) != out:
        raise ValueError('neutralized quest does not round-trip stably')
    return out


def _build_area_quests() -> dict:
    """Return {archive_basename: qst_bytes} for the SV area questlines to add."""
    arc = _open_upstream_arc()
    out = {}

    # Byte-exact ports (all referenced records/tags resolve).
    for name in PORT_QUESTS:
        data = _upstream_quest_bytes(arc, name)
        _assert_roundtrip(name, data)
        out[name] = data

    # Blood cave interior: byte-exact except the single lost-NPC entry trigger.
    bc = _upstream_quest_bytes(arc, BLOODCAVE_INTERIOR_QUEST)
    _assert_roundtrip(BLOODCAVE_INTERIOR_QUEST, bc)
    out[BLOODCAVE_INTERIOR_QUEST] = _neutralize_bloodcave_entry_step(bc)
    return out


def main():
    # Start from SVAERA's original Quests.arc (clean)
    svaera_quests = Path(r'reference_mods\SVAERA_customquest\Resources\Quests.arc')
    quests_arc_path = Path(r'work\SoulvizierClassic\Resources\Quests.arc')

    import shutil
    if svaera_quests.exists():
        shutil.copy2(svaera_quests, quests_arc_path)
        print(f'Restored clean Quests.arc from SVAERA ({quests_arc_path.stat().st_size / 1024:.1f} KB)')

    # Replace sv_commonmechanics.qst with our combined portal quest ONLY if any
    # portals are defined. The blood-cave portal hack was removed (walk-in entry),
    # leaving PORTALS empty; in that case we leave the clean SVAERA
    # sv_commonmechanics.qst untouched rather than write a degenerate empty quest.
    arc = ArcArchive.from_file(quests_arc_path)
    if PORTALS:
        portal_qst = _make_combined_portal_quest()
        print(f'Built combined portal quest ({len(portal_qst)} bytes, {len(PORTALS)} portals)')
        replaced = False
        for e in arc.entries:
            if 'sv_commonmechanics' in e.name.lower():
                arc.set_file(e.name, portal_qst)
                replaced = True
                print(f'Replaced {e.name} with portal quest')
                break
        if not replaced:
            print('WARNING: sv_commonmechanics.qst not found in Quests.arc!')
    else:
        print('No portals defined (blood-cave walk-in) - leaving clean '
              'sv_commonmechanics.qst untouched.')

    # Add the Soulvizier AREA questlines at the archive root, ALONGSIDE the portal
    # quest (never replacing it). Their names are already registered in the map's
    # QUESTS section and their level entities are already placed, so this is enough
    # to make the questlines live (Quests.arc-only; no map rebuild).
    area_quests = _build_area_quests()
    for name, data in area_quests.items():
        arc.add_file(name, data)
        print(f'Added area quest {name} ({len(data)} bytes)')

    arc.write(quests_arc_path)
    print(f'  ARC size: {quests_arc_path.stat().st_size / 1024:.1f} KB')

    # Verify: reopen and confirm both the portal quest and every area quest are present
    # and decompress back to the exact bytes we wrote.
    arc2 = ArcArchive.from_file(quests_arc_path)
    for e in arc2.entries:
        if 'sv_commonmechanics' in e.name.lower():
            print(f'  sv_commonmechanics.qst: {e.decomp_size} bytes')
    for name, data in area_quests.items():
        back = arc2.get_file(name)
        ok = back is not None and back == data
        print(f'  {name}: {"OK" if ok else "MISMATCH"} '
              f'({len(back) if back else 0} bytes)')
        if not ok:
            print(f'    ERROR: {name} did not round-trip through Quests.arc!')


if __name__ == '__main__':
    main()
