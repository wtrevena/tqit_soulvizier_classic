"""
Build custom quest files and patch them into the mod's Quests.arc.

The mod's Quests.arc = SVAERA's original archive (restored clean each build) plus
the Soulvizier AREA questlines (blood cave interior, uber dungeon, widow letter,
boss arena): the original SV .qst files, ported byte-for-byte from upstream into
the Quests.arc root. Their names are already registered in the deployed map's
QUESTS section and their trigger volumes / proxies / doors / portals are already
placed in the level blobs, so backing them here (a Quests.arc-only change, no map
rebuild) makes the questlines live. See PORT_QUESTS.

Blood-cave ENTRY needs no quest at all: it is engine-native (HiddenValley01's
GridEntrance cave mouth streams into the blob-swapped SV Random09A, whose west
tunnel walks into the blood cave; the cave's 0x06 return-link walks back out).
The old quest-driven boat-dialog portal hack is REMOVED; PORTALS is kept only as
an (empty) hook - if it is ever non-empty again, a "Portal System" quest is
built into the sv_commonmechanics.qst slot as before.

This build ALSO ports TWO VANILLA base-game controller quests to hard-cap the
campaign at Immortal Throne for DLC owners (both identities already registered in
our map, so both are Quests.arc-only changes -- NO map/Levels rebuild):

  1. x4_other_001_control_expansionportals.qst (from the base game's XPack4/Quests.arc,
     identity registered at idx 232) is added with ONLY its Immortal-Throne ->
     Eternal-Embers act-portal Action_UnlockFixedItem removed, so an Eternal Embers
     (TQX4) owner no longer gets the "portal opens after Hades" transition. See
     EXPANSIONPORTALS_QUEST + _neutralize_expansionportals_it_to_ee.

  2. xquest_controlsbossdoors.qst (from the base game's Immortal-Throne archive
     Resources/xpack/Quests.arc, identity registered at idx 118) is added with ONLY
     its Immortal-Throne -> Ragnarok(Scandia) act-portal Action_UnlockFixedItem
     removed, so a Ragnarok (TQA2) owner no longer gets the Scandia act portal after
     Hades. This controller manages the IT BOSS DOORS generally (Grey Sisters, Charon,
     Kerberos, Skeletal Typhon, Hades), so the excision is surgical: only the single
     Scandia-unlock action inside the Persephone-after-Hades trigger is removed; every
     boss-door step and every other action (including the two KEPT end-of-game portals
     that terminate the arc AT Hades) is preserved byte-faithfully. See
     BOSSDOORS_QUEST + _neutralize_bossdoors_it_to_scandia.

Between the two, an owner of ANY DLC pack (Ragnarok / Atlantis / Eternal Embers) no
longer gets an act-entry portal from a Hades-end state, so the arc ends at Hades as
SV's difficulty balance assumes. Every OTHER step of both quests is preserved byte-
faithfully. See docs/IT_ENDPOINT_AUDIT.md.
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

# ── Widow-letter static-placement de-duplication ─────────────────────────────
# BUG: the widow letter never appears for existing characters. finalletter is
# QUEST-SPAWNED (widowletter.qst step 0 "Letter Control" trigger "Spawn Letter":
# Condition_OnLevelLoad + NOT OwnsToken(SQWL_PickedUpLetter) ->
# Action_SpawnEntityAtLocation(finalletter, location_letterdrop)), and the quest is
# never tracked for a character that predates it (docs/LETTER_SPAWN_DIAGNOSIS.md), so
# the spawn never fires. The robust, character-independent fix is to place finalletter
# as a STATIC 0x05 world entity at the location_letterdrop spot in
# drxFirstxistion_connection (via INJECT_SPECS), so the letter is physically present to
# pick up for ALL characters regardless of quest tracking.
#
# DUPLICATE-PREVENTION (brief C2): with the static letter always present, a character
# that DOES track the quest would otherwise see BOTH the static letter AND the
# quest-spawned one. To guarantee exactly ONE letter ever exists per character, we
# NEUTRALIZE the quest's own "Spawn Letter" action here (a byte-exact qst edit): the
# trigger keeps its conditions but drops the Action_SpawnEntityAtLocation, so the quest
# never spawns a second letter. The "Stop Letter Spawning" trigger
# (Condition_PickupItem(finalletter) -> BestowTriggerToken(SQWL_PickedUpLetter)) is left
# byte-identical, so picking up the STATIC letter still grants the token and advances the
# questline for tracking characters (Condition_PickupItem keys on the item RECORD, not on
# how the item entered the world). Net: static letter is the single instance the pickup
# condition keys on; the quest spawn is removed so no duplicate can exist.
WIDOWLETTER_QUEST = 'widowletter.qst'
# The two records that jointly + uniquely identify the letter-spawn action (the chest
# spawn uses location_treasurechest; the blocker uses blockersquirrel).
WIDOWLETTER_SPAWN_ENTITY = r'records\drxmap\quest\finalletter.dbr'
WIDOWLETTER_SPAWN_LOCATION = r'records\drxmap\quest\location_letterdrop.dbr'

# ── Immortal-Throne endpoint hard-cap (Eternal-Embers act portal removal) ────────
# WHY: SV 0.98i's difficulty balance assumes the playable arc ENDS at the end of
# Immortal Throne (Act 4 / Hades). A non-DLC player already stops there. But a player
# who owns the Eternal Embers DLC (TQX4) inherits vanilla TQAE's Immortal-Throne ->
# Eternal-Embers ACT portal: the base-game controller quest
# x4_other_001_control_expansionportals.qst (registered in OUR map's QUESTS window at
# idx 232, inherited from vanilla) holds the step "IMMORTAL THRONE Portal to Eternal
# Embers" whose single trigger "RESETTABLE: Portal From Immortal Throne" fires on
# Condition_ConversationStart(persephone_hades.dbr) -> Action_UnlockFixedItem(
# x4_other_immortalthrone_to_eternalembers_teleport_a.dbr). That fixed item is a
# FixedItemTeleport (RequireDLC=TQX4) whose FileDescription is literally "ACT PORTAL -
# Immortal Throne End teleport to Eternal Embers Beginning" -- talk to Persephone after
# Hades dies and a portal to a NEW act opens. Taking it extends the arc past Hades and
# moves the Epic/Legendary completion gate off the Hades kill, breaking SV's IT-end
# scaling for an EE owner. See docs/IT_ENDPOINT_AUDIT.md FIX OPTION 1.
#
# THE FIX (per audit, Will-approved): port this vanilla quest into the mod's Quests.arc
# with THAT ONE Action_UnlockFixedItem removed (identical surgical pattern to the
# widowletter spawn neutralization above). The quest identity is already registered at
# idx 232, so this is a Quests.arc-only change: NO map/Levels rebuild. The trigger keeps
# its persephone condition and becomes a zero-action trigger (the same shape as the
# always-present zero-action sentinel trigger), so nothing else in the quest shifts.
#
# WHAT IS DELIBERATELY KEPT (evidence-driven; see docs/IT_ENDPOINT_AUDIT.md + the ground-
# truth probes in this session): every OTHER step/action of the quest is preserved
# byte-faithfully. In particular the OTHER Persephone-after-Hades trigger -- step
# "IMMORTAL THRONE: Has EE - Normal/Epic" -> Action_UnlockFixedItem(
# endportal_hades_NORMAL_EPIC.dbr) -- is KEPT: that record is a FixedItemTyphonPortal
# (RequireDLC=TQX4, RequireNoDLC=TQA2) whose FileDescription is "End of game portal when
# completed hades (if no DLC2)". It is a game-ENDING credits portal for the EE-owner who
# does NOT own Ragnarok; it terminates the arc AT Hades (exactly the SV-desired outcome),
# so removing it would strip a legitimate end-of-game portal, not extend the arc. Every
# other step (ON LOAD PORTALS, the Ragnarok/Valhalla Odin portals, the Eternal-Embers-
# interior Pingyang/Marshland/SQ301 portals, and the "Makes it so Quest Never Completes"
# keep-alive control step) only fires once the player is already physically inside a DLC
# act, so none can move the IT completion gate; all are left intact.
#
# COMPANION CAP (Ragnarok owners): the Immortal-Throne -> RAGNAROK (Scandia) act portal
# for a TQA2 (Ragnarok) owner is opened by a DIFFERENT controller quest --
# xquest_controlsbossdoors.qst (registered in our window at idx 118) -- and is now capped
# too by _neutralize_bossdoors_it_to_scandia below (BOSSDOORS_QUEST). This function/quest
# handles ONLY the x4 Eternal-Embers portal at idx 232.
EXPANSIONPORTALS_QUEST = 'x4_other_001_control_expansionportals.qst'
# The base-game (NOT upstream-SV) archive that holds the vanilla controller quest.
BASE_GAME_XPACK4_QUESTS = Path(
    r'C:\Program Files (x86)\Steam\steamapps\common'
    r'\Titan Quest Anniversary Edition\Resources\XPack4\Quests.arc')
# The single fixedItem that uniquely identifies the IT->Eternal-Embers act-portal unlock
# to remove (the ONLY Action_UnlockFixedItem in the quest that references it).
EXPANSIONPORTALS_IT_TO_EE_FIXEDITEM = (
    r'records/xpack4/quests/item/teleport/'
    r'x4_other_immortalthrone_to_eternalembers_teleport_a.dbr')

# ── Immortal-Throne endpoint hard-cap (Ragnarok/Scandia act portal removal) ──────
# WHY: same difficulty-balance reason as the Eternal-Embers cap above, for the OTHER DLC
# path. A player who owns the Ragnarok DLC (TQA2) inherits vanilla TQAE's Immortal-Throne
# -> Ragnarok(Scandia) ACT portal. It is opened by the vanilla Immortal-Throne boss-door
# controller quest xquest_controlsbossdoors.qst (registered in OUR map's QUESTS window at
# idx 118, inherited from vanilla): its Hades boss step ("BOSS: Hades in the Palace Of
# Hades") holds a Persephone-after-Hades trigger (Condition_ConversationStart(
# persephone_hades.dbr)) that fires THREE Action_UnlockFixedItem in a row --
# fixeditemtyphonportal.dbr (the vanilla IT typhon end portal), portal_hadesscandia.dbr
# (the Ragnarok act portal), and endportal_hades.dbr (the no-DLC end-of-game credits
# portal). The MIDDLE one, records/xpack2/quests/objects/portal_hadesscandia.dbr, is a
# FixedItemTeleport (RequireDLC=TQA2) whose FileDescription is literally "The Portal to
# Scandia (if DLC2)" and whose in-file comment is "!!! TQ2A ADDITION !!!". Unlocking it
# after Hades opens a NEW act (Ragnarok) for a TQA2 owner, moving their Epic/Legendary
# completion gate off the Hades kill and breaking SV's IT-end scaling. See
# docs/IT_ENDPOINT_AUDIT.md + the it-cap part-1 vet.
#
# THE FIX (mirrors part 1 exactly): port this vanilla quest into the mod's Quests.arc with
# THAT ONE Action_UnlockFixedItem (fixedItem == portal_hadesscandia.dbr) removed. Identity
# is already registered at idx 118, so this is a Quests.arc-only change: NO map rebuild.
# The Persephone trigger keeps its condition and its OTHER two actions; only actionCount
# drops 4 -> 3 in that one block, so nothing else in the quest shifts.
#
# SURGICAL SCOPE -- this controller manages the IT BOSS DOORS generally (Grey Sisters,
# Charon, Kerberos, Skeletal Typhon, Hades one-way doors + form-swap invincibility). ALL
# of that, and everything the IT arc needs, is preserved byte-exact. In particular the two
# KEPT unlocks in the SAME trigger are deliberately retained:
#   - fixeditemtyphonportal.dbr (Class FixedItemTyphonPortal, no DLC gate) = the vanilla
#     Immortal-Throne end portal; part of the base IT finale.
#   - endportal_hades.dbr (Class FixedItemTyphonPortal, RequireNoDLC=TQA2;TQX4) = the
#     game-ENDING credits portal for a player who owns NEITHER Ragnarok NOR EE; it
#     TERMINATES the arc AT Hades (exactly the SV-desired outcome), so removing it would
#     strip a legitimate end-of-game portal, not extend the arc. The unique-key match on
#     fixedItem == portal_hadesscandia discriminates it from the adjacent, similarly-
#     commented endportal_hades action.
# portal_hadesscandia.dbr appears in EXACTLY ONE place in the whole quest (proven), so the
# fail-loud guard requires removed == 1 and asserts the two KEPT portals survive.
BOSSDOORS_QUEST = 'xquest_controlsbossdoors.qst'
# The base-game Immortal-Throne archive (lowercase 'xpack') that holds this vanilla quest.
BASE_GAME_XPACK_QUESTS = Path(
    r'C:\Program Files (x86)\Steam\steamapps\common'
    r'\Titan Quest Anniversary Edition\Resources\xpack\Quests.arc')
# The single fixedItem that uniquely identifies the IT->Ragnarok(Scandia) act-portal unlock
# to remove (the ONLY Action_UnlockFixedItem in the quest that references it).
BOSSDOORS_IT_TO_SCANDIA_FIXEDITEM = (
    r'records/xpack2/quests/objects/portal_hadesscandia.dbr')
# The two end-of-game portals in the SAME trigger that MUST survive the excision (proves we
# removed the right action and did not over-remove).
BOSSDOORS_KEPT_TYPHON_PORTAL = (
    r'records/quests/questobjects/fixeditemtyphonportal.dbr')
BOSSDOORS_KEPT_END_PORTAL = (
    r'records/xpack2/quests/objects/endportal_hades.dbr')


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


def _neutralize_widowletter_spawn(data: bytes) -> bytes:
    """Remove ONLY the finalletter->location_letterdrop spawn action from widowletter.qst.

    The letter is placed statically in the world (INJECT_SPECS); this drops the quest's
    duplicate spawn so exactly one letter can ever exist. Finds the single trigger whose
    ACTIONS block contains an Action_SpawnEntityAtLocation with BOTH
    WIDOWLETTER_SPAWN_ENTITY and WIDOWLETTER_SPAWN_LOCATION (uniquely the "Spawn Letter"
    trigger; the chest/blocker spawns use location_treasurechest), and empties that ONE
    Action_SpawnEntityAtLocation from the actions block: decrement actionCount by 1 and
    drop the matching (actionClassName field, action-fields block) pair. The trigger keeps
    its conditions; every OTHER trigger/step/action is byte-identical.

    A trigger's ACTIONS block is a flat sequence:
      [ ('field','actionCount',...),
        ('field','actionClassName',...), ('block', <action fields>),   # repeated
        ... ]
    We do not touch trigger/step counts (the trigger still exists, action-less), matching
    the always-present zero-action sentinel-trigger shape.
    """
    ent = WIDOWLETTER_SPAWN_ENTITY.replace('\\', '/').lower()
    loc = WIDOWLETTER_SPAWN_LOCATION.replace('\\', '/').lower()

    def str_fields(items):
        out = set()
        for it in items:
            if it[0] == 'block':
                out |= str_fields(it[1])
            elif it[0] == 'field' and it[2][0] == 'str':
                out.add(it[2][1].replace('\\', '/').lower())
        return out

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
        for (hpos, cpos, apos) in tg:
            actions_block = trigcont[apos][1]  # list of items in the actions block
            # walk the actions block: find an Action_SpawnEntityAtLocation classname field
            # immediately followed by a fields block that references BOTH the letter entity
            # and the letterdrop location.
            new_items = []
            i = 0
            dropped_here = 0
            while i < len(actions_block):
                it = actions_block[i]
                is_spawn = (it[0] == 'field' and it[1] == 'actionClassName'
                            and it[2][0] == 'str'
                            and it[2][1] == 'Action_SpawnEntityAtLocation')
                if is_spawn and i + 1 < len(actions_block) and actions_block[i + 1][0] == 'block':
                    fld = str_fields(actions_block[i + 1][1])
                    if ent in fld and loc in fld:
                        # drop this classname field + its fields block
                        i += 2
                        dropped_here += 1
                        removed += 1
                        continue
                new_items.append(it)
                i += 1
            if dropped_here:
                # decrement actionCount by the number dropped
                for idx, it in enumerate(new_items):
                    if it[0] == 'field' and it[1] == 'actionCount':
                        old = it[2][1]
                        new_items[idx] = ('field', 'actionCount', ('int', old - dropped_here))
                        break
                new_trigcont = list(trigcont)
                new_trigcont[apos] = ('block', new_items)
                steps_container[trigcont_pos] = ('block', new_trigcont)
                # refresh local ref for any subsequent triggers in the same container
                trigcont = new_trigcont

    if removed != 1:
        raise ValueError(
            f'{WIDOWLETTER_QUEST}: expected exactly 1 Action_SpawnEntityAtLocation '
            f'spawning {WIDOWLETTER_SPAWN_ENTITY} at {WIDOWLETTER_SPAWN_LOCATION}, '
            f'found {removed}. Upstream changed; review before shipping.')

    out = qst_format.serialize(tree)
    # sanity: the letter-spawn action must be gone (no actions block references BOTH refs),
    # the file must round-trip stably, and finalletter must still be referenced elsewhere
    # (the Condition_PickupItem / RemoveItemFromInventory refs stay).
    reparsed = qst_format.parse(out)

    def any_spawn_letter(container):
        sc = container[1]
        for sd, tc, sn in [block_positions(sc)[i:i + 3]
                           for i in range(0, len(block_positions(sc)), 3)]:
            tcb = sc[tc][1]
            tgg = [block_positions(tcb)[i:i + 3]
                   for i in range(0, len(block_positions(tcb)), 3)]
            for (h, c, a) in tgg:
                items = sc[tc][1][a][1]
                j = 0
                while j < len(items):
                    it = items[j]
                    if (it[0] == 'field' and it[1] == 'actionClassName'
                            and it[2][0] == 'str'
                            and it[2][1] == 'Action_SpawnEntityAtLocation'
                            and j + 1 < len(items) and items[j + 1][0] == 'block'):
                        fld = str_fields(items[j + 1][1])
                        if ent in fld and loc in fld:
                            return True
                    j += 1
        return False

    if any_spawn_letter(reparsed[1]):
        raise ValueError('widowletter neutralization failed: letter spawn still present')
    if qst_format.serialize(reparsed) != out:
        raise ValueError('neutralized widowletter does not round-trip stably')
    if ent not in str_fields([b for blk in reparsed for b in blk]):
        raise ValueError('widowletter neutralization removed finalletter entirely; '
                         'the pickup condition must still reference it')
    return out


def _open_base_game_arc(path: Path) -> ArcArchive:
    """Open a pristine base-game .arc (e.g. xpack or XPack4 Quests.arc) for verbatim port."""
    if not path.exists():
        raise FileNotFoundError(
            f'Base-game archive not found at {path}; cannot port the vanilla '
            f'controller quest it holds. (Is TQAE installed at the expected '
            f'Steam path?)')
    return ArcArchive.from_file(path)


def _neutralize_expansionportals_it_to_ee(data: bytes) -> bytes:
    """Remove ONLY the Immortal-Throne -> Eternal-Embers act-portal UnlockFixedItem.

    Ports x4_other_001_control_expansionportals.qst byte-faithfully EXCEPT for the
    single Action_UnlockFixedItem whose fixedItem is EXPANSIONPORTALS_IT_TO_EE_FIXEDITEM
    (uniquely the step "IMMORTAL THRONE Portal to Eternal Embers" / trigger "RESETTABLE:
    Portal From Immortal Throne"; every other unlock in the quest targets a different
    record). That action is the ONE choke point that opens a NEW act (Eternal Embers)
    from the end of Immortal Throne for a DLC owner, moving their difficulty completion
    gate off the Hades kill and breaking SV's IT-end scaling (see the module header +
    docs/IT_ENDPOINT_AUDIT.md). The trigger keeps its Condition_ConversationStart(
    persephone_hades) condition and becomes a zero-action trigger (structurally identical
    to the always-present zero-action sentinel trigger), so no other step/trigger/action
    shifts and the quest keeps working as a resettable controller for every OTHER portal.

    Same surgical shape as _neutralize_widowletter_spawn: find the trigger whose ACTIONS
    block contains an Action_UnlockFixedItem with fixedItem == the target, decrement that
    block's actionCount by 1, and drop the matching (actionClassName field, action-fields
    block) pair. Trigger/step counts are untouched.
    """
    fixed = EXPANSIONPORTALS_IT_TO_EE_FIXEDITEM.replace('\\', '/').lower()

    def str_fields(items):
        out = set()
        for it in items:
            if it[0] == 'block':
                out |= str_fields(it[1])
            elif it[0] == 'field' and it[2][0] == 'str':
                out.add(it[2][1].replace('\\', '/').lower())
        return out

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
        for (hpos, cpos, apos) in tg:
            actions_block = trigcont[apos][1]  # list of items in the actions block
            # walk the actions block: find an Action_UnlockFixedItem classname field
            # immediately followed by a fields block whose fixedItem == the target.
            new_items = []
            i = 0
            dropped_here = 0
            while i < len(actions_block):
                it = actions_block[i]
                is_unlock = (it[0] == 'field' and it[1] == 'actionClassName'
                             and it[2][0] == 'str'
                             and it[2][1] == 'Action_UnlockFixedItem')
                if is_unlock and i + 1 < len(actions_block) and actions_block[i + 1][0] == 'block':
                    fld = str_fields(actions_block[i + 1][1])
                    if fixed in fld:
                        # drop this classname field + its fields block
                        i += 2
                        dropped_here += 1
                        removed += 1
                        continue
                new_items.append(it)
                i += 1
            if dropped_here:
                # decrement actionCount by the number dropped
                for idx, it in enumerate(new_items):
                    if it[0] == 'field' and it[1] == 'actionCount':
                        old = it[2][1]
                        new_items[idx] = ('field', 'actionCount', ('int', old - dropped_here))
                        break
                new_trigcont = list(trigcont)
                new_trigcont[apos] = ('block', new_items)
                steps_container[trigcont_pos] = ('block', new_trigcont)
                trigcont = new_trigcont  # refresh for any later triggers in same container

    if removed != 1:
        raise ValueError(
            f'{EXPANSIONPORTALS_QUEST}: expected exactly 1 Action_UnlockFixedItem '
            f'unlocking {EXPANSIONPORTALS_IT_TO_EE_FIXEDITEM}, found {removed}. '
            f'Upstream/base-game changed; review before shipping.')

    out = qst_format.serialize(tree)
    # sanity: the IT->EE unlock action must be gone (no actions block references the
    # target fixedItem), the file must round-trip stably, and the OTHER Persephone-side
    # end-of-game credits portal (endportal_hades) must still be present.
    reparsed = qst_format.parse(out)

    def any_it_to_ee_unlock(container):
        sc = container[1]
        for sd, tc, sn in [block_positions(sc)[i:i + 3]
                           for i in range(0, len(block_positions(sc)), 3)]:
            tcb = sc[tc][1]
            tgg = [block_positions(tcb)[i:i + 3]
                   for i in range(0, len(block_positions(tcb)), 3)]
            for (h, c, a) in tgg:
                items = sc[tc][1][a][1]
                j = 0
                while j < len(items):
                    it = items[j]
                    if (it[0] == 'field' and it[1] == 'actionClassName'
                            and it[2][0] == 'str'
                            and it[2][1] == 'Action_UnlockFixedItem'
                            and j + 1 < len(items) and items[j + 1][0] == 'block'):
                        if fixed in str_fields(items[j + 1][1]):
                            return True
                    j += 1
        return False

    if any_it_to_ee_unlock(reparsed[1]):
        raise ValueError('expansion-portals neutralization failed: IT->EE unlock '
                         'still present')
    if qst_format.serialize(reparsed) != out:
        raise ValueError('neutralized expansion-portals quest does not round-trip stably')
    # the target fixedItem string must be gone entirely (it appears in exactly ONE place,
    # the unlock action we removed) -- guards against a partial/mismatched edit.
    if fixed in str_fields([b for blk in reparsed for b in blk]):
        raise ValueError('expansion-portals neutralization left a dangling IT->EE '
                         'fixedItem reference')
    # the KEPT end-of-game credits portal must survive (proves we removed the RIGHT one).
    if 'records/xpack2/quests/objects/endportal_hades_normal_epic.dbr' \
            not in str_fields([b for blk in reparsed for b in blk]):
        raise ValueError('expansion-portals neutralization also dropped the KEPT '
                         'endportal_hades credits portal; over-removed.')
    return out


def _neutralize_bossdoors_it_to_scandia(data: bytes) -> bytes:
    """Remove ONLY the Immortal-Throne -> Ragnarok(Scandia) act-portal UnlockFixedItem.

    Ports xquest_controlsbossdoors.qst byte-faithfully EXCEPT for the single
    Action_UnlockFixedItem whose fixedItem is BOSSDOORS_IT_TO_SCANDIA_FIXEDITEM
    (portal_hadesscandia.dbr -- uniquely the Ragnarok act portal in the Hades boss step's
    Persephone-after-Hades trigger; every OTHER unlock in the quest targets a different
    record). That action is the ONE choke point that opens a NEW act (Ragnarok / Scandia)
    from the end of Immortal Throne for a TQA2 owner, moving their difficulty completion
    gate off the Hades kill and breaking SV's IT-end scaling (see the module header +
    docs/IT_ENDPOINT_AUDIT.md). The trigger keeps its Condition_ConversationStart(
    persephone_hades) condition and its OTHER two Action_UnlockFixedItem (the vanilla IT
    typhon end portal + the no-DLC end-of-game credits portal), so no other step/trigger/
    action shifts and the controller keeps managing every OTHER boss door unchanged.

    Same surgical shape as _neutralize_expansionportals_it_to_ee: find the trigger whose
    ACTIONS block contains an Action_UnlockFixedItem with fixedItem == the target,
    decrement that block's actionCount by 1, and drop the matching (actionClassName field,
    action-fields block) pair. Trigger/step counts are untouched. (This controller manages
    the IT BOSS DOORS generally -- Grey Sisters, Charon, Kerberos, Skeletal Typhon, Hades
    one-way doors + form-swap invincibility -- so the excision is scoped to exactly the one
    Scandia-unlock action; all boss-door logic is preserved byte-exact.)
    """
    fixed = BOSSDOORS_IT_TO_SCANDIA_FIXEDITEM.replace('\\', '/').lower()
    kept_typhon = BOSSDOORS_KEPT_TYPHON_PORTAL.replace('\\', '/').lower()
    kept_end = BOSSDOORS_KEPT_END_PORTAL.replace('\\', '/').lower()

    def str_fields(items):
        out = set()
        for it in items:
            if it[0] == 'block':
                out |= str_fields(it[1])
            elif it[0] == 'field' and it[2][0] == 'str':
                out.add(it[2][1].replace('\\', '/').lower())
        return out

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
        for (hpos, cpos, apos) in tg:
            actions_block = trigcont[apos][1]  # list of items in the actions block
            # walk the actions block: find an Action_UnlockFixedItem classname field
            # immediately followed by a fields block whose fixedItem == the target.
            new_items = []
            i = 0
            dropped_here = 0
            while i < len(actions_block):
                it = actions_block[i]
                is_unlock = (it[0] == 'field' and it[1] == 'actionClassName'
                             and it[2][0] == 'str'
                             and it[2][1] == 'Action_UnlockFixedItem')
                if is_unlock and i + 1 < len(actions_block) and actions_block[i + 1][0] == 'block':
                    fld = str_fields(actions_block[i + 1][1])
                    if fixed in fld:
                        # drop this classname field + its fields block
                        i += 2
                        dropped_here += 1
                        removed += 1
                        continue
                new_items.append(it)
                i += 1
            if dropped_here:
                # decrement actionCount by the number dropped
                for idx, it in enumerate(new_items):
                    if it[0] == 'field' and it[1] == 'actionCount':
                        old = it[2][1]
                        new_items[idx] = ('field', 'actionCount', ('int', old - dropped_here))
                        break
                new_trigcont = list(trigcont)
                new_trigcont[apos] = ('block', new_items)
                steps_container[trigcont_pos] = ('block', new_trigcont)
                trigcont = new_trigcont  # refresh for any later triggers in same container

    if removed != 1:
        raise ValueError(
            f'{BOSSDOORS_QUEST}: expected exactly 1 Action_UnlockFixedItem '
            f'unlocking {BOSSDOORS_IT_TO_SCANDIA_FIXEDITEM}, found {removed}. '
            f'Upstream/base-game changed; review before shipping.')

    out = qst_format.serialize(tree)
    # sanity: the IT->Scandia unlock action must be gone (no actions block references the
    # target fixedItem), the file must round-trip stably, and BOTH kept end-of-game portals
    # (typhon + endportal_hades) must still be present.
    reparsed = qst_format.parse(out)

    def any_it_to_scandia_unlock(container):
        sc = container[1]
        for sd, tc, sn in [block_positions(sc)[i:i + 3]
                           for i in range(0, len(block_positions(sc)), 3)]:
            tcb = sc[tc][1]
            tgg = [block_positions(tcb)[i:i + 3]
                   for i in range(0, len(block_positions(tcb)), 3)]
            for (h, c, a) in tgg:
                items = sc[tc][1][a][1]
                j = 0
                while j < len(items):
                    it = items[j]
                    if (it[0] == 'field' and it[1] == 'actionClassName'
                            and it[2][0] == 'str'
                            and it[2][1] == 'Action_UnlockFixedItem'
                            and j + 1 < len(items) and items[j + 1][0] == 'block'):
                        if fixed in str_fields(items[j + 1][1]):
                            return True
                    j += 1
        return False

    if any_it_to_scandia_unlock(reparsed[1]):
        raise ValueError('boss-doors neutralization failed: IT->Scandia unlock '
                         'still present')
    if qst_format.serialize(reparsed) != out:
        raise ValueError('neutralized boss-doors quest does not round-trip stably')
    # the target fixedItem string must be gone entirely (it appears in exactly ONE place,
    # the unlock action we removed) -- guards against a partial/mismatched edit.
    all_strs = str_fields([b for blk in reparsed for b in blk])
    if fixed in all_strs:
        raise ValueError('boss-doors neutralization left a dangling IT->Scandia '
                         'fixedItem reference')
    # BOTH kept end-of-game portals must survive (proves we removed the RIGHT one, not a
    # neighbor in the same 3-unlock trigger).
    if kept_typhon not in all_strs:
        raise ValueError('boss-doors neutralization also dropped the KEPT vanilla IT '
                         'typhon end portal; over-removed.')
    if kept_end not in all_strs:
        raise ValueError('boss-doors neutralization also dropped the KEPT endportal_hades '
                         'credits portal; over-removed.')
    return out


def _build_area_quests() -> dict:
    """Return {archive_basename: qst_bytes} for the SV area questlines to add."""
    arc = _open_upstream_arc()
    out = {}

    # Byte-exact ports (all referenced records/tags resolve), EXCEPT widowletter.qst,
    # whose duplicate letter spawn is neutralized (the letter is placed statically via
    # INJECT_SPECS, so the quest must not spawn a second one). See
    # _neutralize_widowletter_spawn.
    for name in PORT_QUESTS:
        data = _upstream_quest_bytes(arc, name)
        _assert_roundtrip(name, data)
        if name == WIDOWLETTER_QUEST:
            out[name] = _neutralize_widowletter_spawn(data)
        else:
            out[name] = data

    # Blood cave interior: byte-exact except the single lost-NPC entry trigger.
    bc = _upstream_quest_bytes(arc, BLOODCAVE_INTERIOR_QUEST)
    _assert_roundtrip(BLOODCAVE_INTERIOR_QUEST, bc)
    out[BLOODCAVE_INTERIOR_QUEST] = _neutralize_bloodcave_entry_step(bc)

    # Immortal-Throne endpoint hard-cap: port the VANILLA base-game expansion-portals
    # controller (from XPack4/Quests.arc, NOT upstream SV) with the single IT->Eternal-
    # Embers act-portal UnlockFixedItem removed. Its identity is already registered in
    # the map at idx 232, so adding the body here (basename at the archive root) makes
    # the neutralized controller live with NO map/Levels change. See the module header
    # + docs/IT_ENDPOINT_AUDIT.md.
    base_arc = _open_base_game_arc(BASE_GAME_XPACK4_QUESTS)
    ep = _upstream_quest_bytes(base_arc, EXPANSIONPORTALS_QUEST)
    _assert_roundtrip(EXPANSIONPORTALS_QUEST, ep)
    out[EXPANSIONPORTALS_QUEST] = _neutralize_expansionportals_it_to_ee(ep)

    # Immortal-Throne endpoint hard-cap (Ragnarok owners): port the VANILLA base-game
    # boss-door controller (from the Immortal-Throne archive Resources/xpack/Quests.arc,
    # NOT upstream SV) with the single IT->Ragnarok(Scandia) act-portal UnlockFixedItem
    # removed. Its identity is already registered in the map at idx 118, so adding the body
    # here (basename at the archive root) makes the neutralized controller live with NO
    # map/Levels change. See the module header + docs/IT_ENDPOINT_AUDIT.md. This mirrors the
    # x4 expansion-portals cap above exactly; only the Scandia unlock is excised, every
    # boss-door step is preserved byte-faithfully.
    xpack_arc = _open_base_game_arc(BASE_GAME_XPACK_QUESTS)
    bd = _upstream_quest_bytes(xpack_arc, BOSSDOORS_QUEST)
    _assert_roundtrip(BOSSDOORS_QUEST, bd)
    out[BOSSDOORS_QUEST] = _neutralize_bossdoors_it_to_scandia(bd)
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
