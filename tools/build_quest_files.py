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
import struct
import zlib
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


def _assert_quest_records_loadable(arc: ArcArchive):
    """PERMANENT CONTRACT (B2): make 'registered-but-silently-unloadable' impossible.

    A quest that exists in no other archive is silently skipped by the engine's
    QuestRepository if its 44-byte ARC file record leaves the native-populated fields
    zero: @36 (filename length) == 0 makes resource-open return NULL -> 'Invalid Quest
    File' -> no quest object, no .que, no tokens. This bug produced ZERO unresolved
    references and survived four rebuilds because nothing validated the record shape.

    Assert, for EVERY entry_type==3 record in the rebuilt Quests.arc:
      * @36 != 0  and  @36 == len(name)         (filename length, as native writers set it)
      * @16 != 0  and  @16 == adler32(decompress(entry))   (checksum of decompressed body)
      * the decompressed body parses via qst_format
    Native SVAERA entries already satisfy all three (verified: 101/101), so this gate
    only ever fires on a record our own writer malformed. Fail loud on any violation.
    """
    violations = []
    checked = 0
    for e in arc.entries:
        if e.entry_type != 3:
            continue
        checked += 1
        rr = e.raw_record
        name_len = struct.unpack_from('<I', rr, 36)[0]
        adler_rec = struct.unpack_from('<I', rr, 16)[0]
        expect_len = len(e.name.encode('ascii'))
        body = arc.decompress(e)
        expect_adler = zlib.adler32(body) & 0xFFFFFFFF
        if name_len == 0:
            violations.append(f'{e.name!r}: @36 filename-length is 0 (record UNLOADABLE)')
        elif name_len != expect_len:
            violations.append(
                f'{e.name!r}: @36 filename-length {name_len} != len(name) {expect_len}')
        if adler_rec == 0:
            violations.append(f'{e.name!r}: @16 adler32 is 0 (record UNLOADABLE)')
        elif adler_rec != expect_adler:
            violations.append(
                f'{e.name!r}: @16 adler32 {adler_rec:#010x} != '
                f'adler32(decompress) {expect_adler:#010x}')
        try:
            qst_format.parse(body)
        except Exception as exc:
            violations.append(f'{e.name!r}: body does not parse via qst_format ({exc})')
    if violations:
        raise ValueError(
            'QUEST RECORD CONTRACT FAILED (registered quests would silently NOT load):\n  '
            + '\n  '.join(violations))
    print(f'  quest-record contract PASS: {checked} entry_type==3 records '
          f'(all @36==len(name)!=0, @16==adler32(decompress)!=0, bodies parse)')


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


# ── Guardian-sealed door hardening (B-TEMPLE-DOOR-1, 2026-07-08) ────────────────
# LIVE REPRO (Will, public build, fresh char): killed the guardian boss in front of the
# waterfall-room "Sealed By Guardian" door and it STAYED locked. Byte-side diagnosis
# exhausted with EVERY element correct: quest registered in the load window (idx 97),
# file well-formed + native-shaped (isActive=0 and isQuestCritical2 both native-normal;
# checked against base/xpack/XPack4 archives), the watched proxy q_highpriest_lone
# placed once, on-mesh (0.10u, full 3.5u placement disc walkable) 16.9u from the door,
# its pool spawns exactly one c_disciple_miniboss (championChance=0 -> no crowd-out),
# doors + unlock actions well-formed. So the failure is a RUNTIME defect in the
# Condition_KillAllCreaturesFromProxy -> proxy-kill-credit chain that offline bytes
# cannot pin (Frida would). Note the same chamber also holds bw_acolyte_clutch_wpriestcnc
# (a priest-looking pack 21.6u from the door), so the kill Will credited may even have
# been a different monster than the proxy's.
#
# THE MITIGATION (native-precedent, design-preserving): ADD redundant triggers keyed on
# Condition_KillCreature(creatureRecord) -- the mechanism VANILLA uses to gate the Greek
# Telkine boss fight ("scripted scene - greek telkine boss fight.qst") -- alongside the
# original proxy triggers (kept intact; strictly additive). Kill-credit then keys on the
# CONCRETE monster record the player kills, independent of proxy association. Proven
# exclusivity (arz + whole-map scan): each guardian record is referenced by exactly ONE
# pool (its own lone proxy) and placed directly in ZERO levels, so "kill this record
# anywhere" is exactly equivalent to "kill this proxy's spawn":
#   c_disciple_miniboss        -> only pools/q_highpriest_lone (waterfall pair)
#   04_spiritcaller_40/41/42   -> only pools/q_shaman_lone     (ornate treasury door)
#   q_leinth_47/49/50          -> only pools/q_leinth_lone     (boss room trap door)
# Added triggers (field layout mirrors the NATIVE AE Condition_KillCreature block:
# comments/isNot/isResettable/isQuestCritical/creatureRecord):
#   step "BloodCave Doors and Portals":
#     kill c_disciple_miniboss -> UnlockFixedItem(secretdoor, 3s) + UnlockFixedItem(
#       waterblocker, 4s)                         [mirrors the original pair exactly]
#     kill 04_spiritcaller_40|41|42 (3 triggers) -> UnlockFixedItem(hc_treasurydoor02_boss)
#   step "Boss Room Crystal Gate":
#     kill q_leinth_47|49|50 (3 triggers) -> OpenDoor(door_bossroom_trap)
#       [door-open ONLY: prevents the locked-in-boss-room trap if the same defect hits
#        Leinth's trigger; the vortex ShowNpc/dialog actions are NOT duplicated -- the
#        boat-dialog idiom is fragile and double-firing it is riskier than the residual]
# Both trigger families can fire (original + redundant): the second unlock/open of an
# already-unlocked/open item is a no-op, so double-firing is harmless.
HARDEN_STEP0_NAME = 'BloodCave Doors and Portals'
HARDEN_STEP2_NAME = 'Boss Room Crystal Gate'
GUARDIAN_DISCIPLE = r'records/drxcreatures/bloodwitch/c_disciple_miniboss.dbr'
GUARDIAN_SPIRITCALLERS = [
    r'records/drxcreatures/bloodabomination/04_spiritcaller_40.dbr',
    r'records/drxcreatures/bloodabomination/04_spiritcaller_41.dbr',
    r'records/drxcreatures/bloodabomination/04_spiritcaller_42.dbr',
]
GUARDIAN_LEINTHS = [
    r'records/drxcreatures/bloodwitch/q_leinth_47.dbr',
    r'records/drxcreatures/bloodwitch/q_leinth_49.dbr',
    r'records/drxcreatures/bloodwitch/q_leinth_50.dbr',
]
DOOR_SECRET = r'records/drxmap/bloodcave/babtpl_waterfallroom_secretdoor.dbr'
DOOR_WATERBLOCKER = r'records/drxmap/bloodcave/triggers/waterblocker.dbr'
DOOR_TREASURY = r'records/drxmap/bloodcave/bossroomentrancedress/hc_treasurydoor02_boss.dbr'
DOOR_BOSSROOM_TRAP = r'records/drxmap/bloodcave/triggers/door_bossroom_trap.dbr'
DELAY_3S = 1077936128  # float32 3.0 bit pattern, as the original secretdoor unlock uses
DELAY_4S = 1082130432  # float32 4.0 bit pattern, as the original waterblocker unlock uses


def _mk_kill_trigger(display, creature_record, actions):
    """Build one trigger triple (header, conditions, actions) in qst tree form.

    actions: list of (action_class, record_key, dbr, delay_bits) tuples, e.g.
    ('Action_UnlockFixedItem', 'fixedItem', dbr, DELAY_3S) or
    ('Action_OpenDoor', 'door', dbr, 0).
    Field layouts mirror byte-verified native/AE shapes exactly (see the block comment).
    """
    header = ('block', [
        ('field', 'displayTag', ('str', display)),
        ('field', 'displayBitmap', ('int_or_empty', 0)),
        ('field', 'comments', ('int_or_empty', 0)),
        ('field', 'isActive', ('int', 0)),
        ('field', 'bRatchet', ('int', 0)),
    ])
    conditions = ('block', [
        ('field', 'conditionCount', ('int', 1)),
        ('field', 'conditionClassName', ('str', 'Condition_KillCreature')),
        ('block', [
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'isNot', ('int', 0)),
            ('field', 'isResettable', ('int', 1)),
            ('field', 'isQuestCritical', ('int', 0)),
            ('field', 'creatureRecord', ('str', creature_record)),
        ]),
    ])
    act_items = [('field', 'actionCount', ('int', len(actions)))]
    for cls, key, dbr, delay in actions:
        act_items.append(('field', 'actionClassName', ('str', cls)))
        act_items.append(('block', [
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'delayTime', ('int', delay)),
            ('field', key, ('str', dbr)),
            ('field', 'canReFire', ('int', 0)),
        ]))
    return [header, conditions, ('block', act_items)]


def _harden_guardian_door_unlocks(data: bytes) -> bytes:
    """ADD the redundant Condition_KillCreature door triggers (see the block comment).

    Strictly additive: appends 4 triggers to the "BloodCave Doors and Portals" step and
    3 triggers to the "Boss Room Crystal Gate" step (each step's trigger-container `max`
    incremented to match); every existing byte of every other field is untouched. Fails
    loud if the steps are missing, if the original proxy triggers vanished, or if the
    result does not re-parse/round-trip with exactly the expected additions.
    """
    def block_positions(items):
        return [i for i, it in enumerate(items) if it[0] == 'block']

    def field_val(items, key):
        for it in items:
            if it[0] == 'field' and it[1] == key:
                return it[2][1]
        return None

    additions = {
        HARDEN_STEP0_NAME: (
            [_mk_kill_trigger('Unlock Waterfall Door Fallback', GUARDIAN_DISCIPLE,
                              [('Action_UnlockFixedItem', 'fixedItem', DOOR_SECRET, DELAY_3S),
                               ('Action_UnlockFixedItem', 'fixedItem', DOOR_WATERBLOCKER, DELAY_4S)])]
            + [_mk_kill_trigger('Unlock Ornate Door Fallback', sc,
                                [('Action_UnlockFixedItem', 'fixedItem', DOOR_TREASURY, 0)])
               for sc in GUARDIAN_SPIRITCALLERS]),
        HARDEN_STEP2_NAME: (
            [_mk_kill_trigger('Open Boss Trap Door Fallback', ql,
                              [('Action_OpenDoor', 'door', DOOR_BOSSROOM_TRAP, 0)])
             for ql in GUARDIAN_LEINTHS]),
    }

    tree = qst_format.parse(data)
    steps_container = tree[1]
    positions = block_positions(steps_container)
    step_triples = [positions[i:i + 3] for i in range(0, len(positions), 3)]

    patched_steps = 0
    for stepdef_pos, trigcont_pos, sentinel_pos in step_triples:
        stepdef = steps_container[stepdef_pos][1]
        name = field_val(stepdef, 'name')
        if name not in additions:
            continue
        new_triples = additions[name]
        trigcont = list(steps_container[trigcont_pos][1])
        n_before = None
        for idx, it in enumerate(trigcont):
            if it[0] == 'field' and it[1] == 'max':
                n_before = it[2][1]
                trigcont[idx] = ('field', 'max', ('int', n_before + len(new_triples)))
                break
        if n_before is None:
            raise ValueError(f'{BLOODCAVE_INTERIOR_QUEST}: step {name!r} trigger '
                             f'container has no max field')
        for triple in new_triples:
            trigcont.extend(triple)
        steps_container[trigcont_pos] = ('block', trigcont)
        patched_steps += 1

    if patched_steps != 2:
        raise ValueError(
            f'{BLOODCAVE_INTERIOR_QUEST}: expected to harden exactly 2 steps '
            f'({HARDEN_STEP0_NAME!r}, {HARDEN_STEP2_NAME!r}), hardened {patched_steps}. '
            f'Upstream changed; review before shipping.')

    out = qst_format.serialize(tree)

    # ── fail-loud verification on the emitted bytes ──
    reparsed = qst_format.parse(out)
    if qst_format.serialize(reparsed) != out:
        raise ValueError('hardened quest does not round-trip stably')

    def collect(items, key, cls_key, cls_val, out_list):
        """Collect values of `key` inside blocks following a classname field == cls_val."""
        i = 0
        while i < len(items):
            it = items[i]
            if it[0] == 'block':
                collect(it[1], key, cls_key, cls_val, out_list)
            elif (it[0] == 'field' and it[1] == cls_key and it[2][0] == 'str'
                    and it[2][1] == cls_val and i + 1 < len(items)
                    and items[i + 1][0] == 'block'):
                v = field_val(items[i + 1][1], key)
                if v is not None:
                    out_list.append(v.replace('\\', '/').lower())
            i += 1

    flat = [it for blk in reparsed for it in blk]
    kills, proxies = [], []
    collect(flat, 'creatureRecord', 'conditionClassName', 'Condition_KillCreature', kills)
    collect(flat, 'proxyRecord', 'conditionClassName',
            'Condition_KillAllCreaturesFromProxy', proxies)
    want_kills = sorted([GUARDIAN_DISCIPLE.lower()] +
                        [s.lower() for s in GUARDIAN_SPIRITCALLERS] +
                        [s.lower() for s in GUARDIAN_LEINTHS])
    if sorted(kills) != want_kills:
        raise ValueError(f'hardening verification failed: Condition_KillCreature set is '
                         f'{sorted(kills)}, expected {want_kills}')
    for p in ('records/drxmap/proxy/q_highpriest_lone.dbr',
              'records/drxmap/proxy/q_shaman_lone.dbr',
              'records/drxmap/proxy/q_leinth_lone.dbr'):
        if p not in proxies:
            raise ValueError(f'hardening dropped the ORIGINAL proxy trigger for {p}; '
                             f'the change must be strictly additive')
    return out


# -- Esti's Hidden Chest supra-formula de-duplication (B1, 2026-07-08) -----------
# WHY: the Esti (Esfri) hidden chest in the blood cave grants a random supra arcane
# formula. In build28 the ONLY source of that formula is a QUEST action: each of the 3
# "Open Chest" triggers in open_bloodcave_portal.qst step "Hidden Chest Control" fires an
# Action_GiveItem(records/xpack/item/loottables/arcaneformulae/supra_special.dbr) straight
# into the bag (the chest CONTAINER itself drops only random gear/gold -- see the closed
# B-CHEST-1 RCA in docs/BACKLOG.md). Lane A (build29) is adding that supra formula to the
# physical chest's own loot table, so the container itself drops it. With BOTH sources live
# an opener would receive TWO formulas -- one from the loot table and one from this quest
# action. To keep exactly ONE grant, we DROP the quest's Action_GiveItem(supra_special) from
# each of the 3 "Open Chest" triggers, leaving Lane A's container-loot grant as the single
# source.
#
# THE FIX (same surgical shape as _neutralize_widowletter_spawn / the two IT-cap
# neutralizers): in the "Hidden Chest Control" step, for EACH of the 3 "Open Chest" triggers,
# find the Action_GiveItem whose item references supra_special and drop that (actionClassName
# field, action-fields block) pair, decrementing that trigger's actionCount 4 -> 3. The two
# Action_UpdateJournalEntry actions (the "Esti's Chest" journal popups) and the
# Action_BestowTriggerToken('OpenedHiddenChest') in each trigger are KEPT byte-identical, so
# the one-time-per-character token + journal chain is untouched; the separate "Disable Chest"
# trigger (Condition_OnLevelLoad + OwnsToken -> Action_DisableProxy) is left byte-identical.
# Trigger/step counts are untouched (still 4 triggers in the step); only actionCount drops in
# the 3 Open Chest triggers, so nothing else in the quest shifts.
#
# DEPLOY COUPLING (must ship together): this Quests.arc change ships together with Lane A's
# arz (which adds the supra formula to the chest loot table) AND the shared Text.arc build.
# Neither alone is correct -- arz-only still double-grants via this quest action; Quests-only
# yields ZERO formula. See docs/HANDOFF_LIVE_STATE.md deploy couplings + B-CHEST-1.
ESTI_CHEST_STEP_NAME = 'Hidden Chest Control'
ESTI_CHEST_OPEN_TRIGGER_TAG = 'Open Chest'
ESTI_CHEST_DISABLE_TRIGGER_TAG = 'Disable Chest'
ESTI_CHEST_SUPRA_ITEM = r'records/xpack/item/loottables/arcaneformulae/supra_special.dbr'
ESTI_CHEST_OPEN_TRIGGERS = 3    # exactly 3 "Open Chest" triggers (one per chest variant)
ESTI_CHEST_KEEP_JOURNAL = 2     # Action_UpdateJournalEntry KEPT per Open Chest trigger
ESTI_CHEST_KEEP_TOKEN = 1       # Action_BestowTriggerToken KEPT per Open Chest trigger
# The Disable Chest proxy + the bestowed token that MUST survive (prove we kept the chain).
ESTI_CHEST_DISABLE_PROXY = r'records/drxitem/container/proxy_hidden_bloodcave_chest.dbr'
ESTI_CHEST_TOKEN = 'OpenedHiddenChest'


def _neutralize_esti_chest_supra(data: bytes) -> bytes:
    """Remove the supra-formula Action_GiveItem from each "Open Chest" trigger.

    In open_bloodcave_portal.qst step "Hidden Chest Control", each of the 3 "Open Chest"
    triggers fires Action_UpdateJournalEntry x2 + Action_BestowTriggerToken +
    Action_GiveItem(supra_special) (actionCount 4). This drops ONLY the
    Action_GiveItem(supra_special) block from each (actionCount 4 -> 3), keeping the two
    journal actions and the token, and leaving the separate "Disable Chest" trigger
    byte-identical. Prevents a double supra grant once Lane A adds the formula to the chest's
    own loot table (B1 / B-CHEST-1; see the module-level comment above this function).

    Fail-loud AND idempotent: requires the step + exactly 3 "Open Chest" triggers + the
    "Disable Chest" trigger (else raise -- e.g. a copy lacking the step raises), removes 0 or
    3 supra GiveItem blocks (a second application on already-neutralized bytes removes 0 and
    returns the bytes unchanged), and verifies the KEEP set (2 journal + 1 token per Open
    Chest trigger), the Disable Chest proxy, and the token all survive while no supra
    reference remains anywhere in the quest.

    A trigger's ACTIONS block is a flat sequence:
      [ ('field','actionCount',...),
        ('field','actionClassName',...), ('block', <action fields>),   # repeated
        ... ]
    We drop the (actionClassName field, fields block) pair for the matching GiveItem and
    decrement actionCount; every OTHER trigger/step/action is byte-identical.
    """
    supra = ESTI_CHEST_SUPRA_ITEM.replace('\\', '/').lower()

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

    def field_val(items, key):
        for it in items:
            if it[0] == 'field' and it[1] == key:
                return it[2][1]
        return None

    def action_class_count(actions_items, cls):
        return sum(1 for it in actions_items
                   if it[0] == 'field' and it[1] == 'actionClassName'
                   and it[2][0] == 'str' and it[2][1] == cls)

    tree = qst_format.parse(data)
    steps_container = tree[1]
    positions = block_positions(steps_container)
    step_triples = [positions[i:i + 3] for i in range(0, len(positions), 3)]

    # locate the "Hidden Chest Control" step (fail loud if absent -- e.g. a copy lacking it).
    target = None
    for stepdef_pos, trigcont_pos, sentinel_pos in step_triples:
        if field_val(steps_container[stepdef_pos][1], 'name') == ESTI_CHEST_STEP_NAME:
            target = (stepdef_pos, trigcont_pos, sentinel_pos)
            break
    if target is None:
        raise ValueError(
            f'{BLOODCAVE_INTERIOR_QUEST}: step {ESTI_CHEST_STEP_NAME!r} not found; cannot '
            f'neutralize the Esti-chest supra grant. Upstream changed; review before shipping.')
    _stepdef_pos, trigcont_pos, _sentinel_pos = target
    trigcont = list(steps_container[trigcont_pos][1])
    tgp = block_positions(trigcont)
    tg = [tgp[i:i + 3] for i in range(0, len(tgp), 3)]

    # partition the step's triggers by displayTag.
    open_triggers = [(h, c, a) for (h, c, a) in tg
                     if field_val(trigcont[h][1], 'displayTag') == ESTI_CHEST_OPEN_TRIGGER_TAG]
    disable_triggers = [(h, c, a) for (h, c, a) in tg
                        if field_val(trigcont[h][1], 'displayTag')
                        == ESTI_CHEST_DISABLE_TRIGGER_TAG]
    if len(open_triggers) != ESTI_CHEST_OPEN_TRIGGERS:
        raise ValueError(
            f'{BLOODCAVE_INTERIOR_QUEST}: expected exactly {ESTI_CHEST_OPEN_TRIGGERS} '
            f'{ESTI_CHEST_OPEN_TRIGGER_TAG!r} triggers in step {ESTI_CHEST_STEP_NAME!r}, '
            f'found {len(open_triggers)}. Upstream changed; review before shipping.')
    if len(disable_triggers) != 1:
        raise ValueError(
            f'{BLOODCAVE_INTERIOR_QUEST}: expected exactly 1 '
            f'{ESTI_CHEST_DISABLE_TRIGGER_TAG!r} trigger in step {ESTI_CHEST_STEP_NAME!r}, '
            f'found {len(disable_triggers)}. Upstream changed; review before shipping.')

    # drop the supra Action_GiveItem from each Open Chest trigger's actions block.
    removed = 0
    for (hpos, cpos, apos) in open_triggers:
        actions_block = trigcont[apos][1]
        new_items = []
        i = 0
        dropped_here = 0
        while i < len(actions_block):
            it = actions_block[i]
            is_give = (it[0] == 'field' and it[1] == 'actionClassName'
                       and it[2][0] == 'str' and it[2][1] == 'Action_GiveItem')
            if is_give and i + 1 < len(actions_block) and actions_block[i + 1][0] == 'block':
                if supra in str_fields(actions_block[i + 1][1]):
                    # drop this classname field + its fields block
                    i += 2
                    dropped_here += 1
                    removed += 1
                    continue
            new_items.append(it)
            i += 1
        if dropped_here:
            for idx, it in enumerate(new_items):
                if it[0] == 'field' and it[1] == 'actionCount':
                    new_items[idx] = ('field', 'actionCount', ('int', it[2][1] - dropped_here))
                    break
            trigcont[apos] = ('block', new_items)

    # fresh -> removed exactly 3 (one per trigger); already-neutralized -> removed 0
    # (idempotent). Any other count is a partial/corrupt edit.
    if removed not in (0, ESTI_CHEST_OPEN_TRIGGERS):
        raise ValueError(
            f'{BLOODCAVE_INTERIOR_QUEST}: expected 0 or {ESTI_CHEST_OPEN_TRIGGERS} supra '
            f'Action_GiveItem removals across the {ESTI_CHEST_OPEN_TRIGGER_TAG!r} triggers, '
            f'made {removed}. Upstream changed; review before shipping.')

    steps_container[trigcont_pos] = ('block', trigcont)

    # postcondition on each Open Chest trigger: KEEP set intact, no supra GiveItem left,
    # actionCount consistent with the remaining actions.
    for (hpos, cpos, apos) in open_triggers:
        acts = trigcont[apos][1]
        if supra in str_fields(acts):
            raise ValueError(f'{BLOODCAVE_INTERIOR_QUEST}: an {ESTI_CHEST_OPEN_TRIGGER_TAG!r} '
                             f'trigger still references supra_special after removal.')
        if action_class_count(acts, 'Action_UpdateJournalEntry') != ESTI_CHEST_KEEP_JOURNAL:
            raise ValueError(f'{BLOODCAVE_INTERIOR_QUEST}: an {ESTI_CHEST_OPEN_TRIGGER_TAG!r} '
                             f'trigger lost an Action_UpdateJournalEntry; over-removed.')
        if action_class_count(acts, 'Action_BestowTriggerToken') != ESTI_CHEST_KEEP_TOKEN:
            raise ValueError(f'{BLOODCAVE_INTERIOR_QUEST}: an {ESTI_CHEST_OPEN_TRIGGER_TAG!r} '
                             f'trigger lost its Action_BestowTriggerToken; over-removed.')
        acount = field_val(acts, 'actionCount')
        n_actions = sum(1 for it in acts
                        if it[0] == 'field' and it[1] == 'actionClassName')
        if acount != n_actions:
            raise ValueError(f'{BLOODCAVE_INTERIOR_QUEST}: actionCount ({acount}) != number of '
                             f'actions ({n_actions}) in an {ESTI_CHEST_OPEN_TRIGGER_TAG!r} '
                             f'trigger.')
        want = ESTI_CHEST_KEEP_JOURNAL + ESTI_CHEST_KEEP_TOKEN
        if acount != want:
            raise ValueError(f'{BLOODCAVE_INTERIOR_QUEST}: an {ESTI_CHEST_OPEN_TRIGGER_TAG!r} '
                             f'trigger has actionCount {acount}, expected {want} '
                             f'({ESTI_CHEST_KEEP_JOURNAL} journal + {ESTI_CHEST_KEEP_TOKEN} '
                             f'token) after removal; an unexpected action survived.')

    # the Disable Chest trigger must still fire Action_DisableProxy on its proxy.
    (dh, dc, da) = disable_triggers[0]
    if action_class_count(trigcont[da][1], 'Action_DisableProxy') != 1:
        raise ValueError(f'{BLOODCAVE_INTERIOR_QUEST}: the {ESTI_CHEST_DISABLE_TRIGGER_TAG!r} '
                         f'trigger lost its Action_DisableProxy; it must be left intact.')

    out = qst_format.serialize(tree)

    # -- fail-loud verification on the emitted bytes --
    reparsed = qst_format.parse(out)
    if qst_format.serialize(reparsed) != out:
        raise ValueError('neutralized esti-chest quest does not round-trip stably')
    # the supra item must be gone from the WHOLE quest (it appears ONLY in the 3 GiveItem
    # blocks we removed -- item[0..2] x 3), and the Disable Chest proxy + the OpenedHiddenChest
    # token must remain (proves we kept the one-time-per-character chain, not stripped it).
    all_strs = str_fields([b for blk in reparsed for b in blk])
    if supra in all_strs:
        raise ValueError('esti-chest neutralization left a dangling supra_special reference')
    if ESTI_CHEST_DISABLE_PROXY.replace('\\', '/').lower() not in all_strs:
        raise ValueError('esti-chest neutralization dropped the Disable Chest proxy; '
                         'the Disable Chest trigger must be left intact')
    if ESTI_CHEST_TOKEN.lower() not in all_strs:
        raise ValueError('esti-chest neutralization dropped the OpenedHiddenChest token; '
                         'the one-time-per-character token chain must be kept')
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

    # Blood cave interior: byte-exact except (1) the single lost-NPC entry trigger is
    # neutralized, and (2) the guardian-sealed door unlocks are HARDENED with redundant
    # native-shape Condition_KillCreature triggers (B-TEMPLE-DOOR-1 live repro; see
    # _harden_guardian_door_unlocks).
    # NOTE (build29, 2026-07-09): the Esti-chest supra-formula Action_GiveItem is DELIBERATELY
    # KEPT (the earlier _neutralize_esti_chest_supra de-dup is NOT applied). Rationale: the
    # whole reason the chest granted nothing was B2 (the quest never LOADED, arc-record bug);
    # with B2 fixed the quest loads and its original SV Action_GiveItem(supra_special) is the
    # correct exactly-once, per-difficulty-locked grant. The alternative chest-loot grant is
    # engine-impossible to make exactly-1 (FixedItemContainer lootNChance are roulette weights,
    # disasm-proven in Lane A A4), so the DB lane correctly left the chest tables untouched.
    # Keeping the quest grant + NOT touching the chest = the authentic mechanism, restored by B2.
    bc = _upstream_quest_bytes(arc, BLOODCAVE_INTERIOR_QUEST)
    _assert_roundtrip(BLOODCAVE_INTERIOR_QUEST, bc)
    out[BLOODCAVE_INTERIOR_QUEST] = _harden_guardian_door_unlocks(
        _neutralize_bloodcave_entry_step(bc))

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


# ── Q1 (build31, Will campaign blocker): Olympus -> Rhodes portal unlock ─────
# The Olympus summit portal (OlympusFinal02 instance [41] =
# records\xpack\quests\objects\xq00_olympus_portaltorhodes.dbr, FixedItemTeleport,
# locked=1, staticPortal=1, "Opened by Zeus after Typhon Killed") is unlocked in
# the base CAMPAIGN by an engine-internal hook that does NOT fire in a Custom
# Quest - no quest anywhere references the record (M7 RCA, verified across all 6
# quest arcs), so in the mod the portal has NEVER opened and Act 4 travel from
# Olympus was dead.
#
# THE FIX: append ONE trigger to the vanilla boss-door controller
# 'quest that controls bosses and their doors.qst' (ALREADY inside SVAERA's
# Quests.arc + registered in the map's QUESTS window; the controller never
# completes - its last step exists to keep it refiring - and it ALREADY
# evaluates the exact token in its Typhon repeat-loot trigger, proving the
# context is live):
#   Condition_OnLevelLoad + Condition_OwnsTriggerToken('Olympus - Typhon
#   Defeated')  ->  Action_UnlockFixedItem(xq00_olympus_portaltorhodes,
#   canReFire=1)
# Repeat-on-load + canReFire=1 makes the unlock idempotent and RETROACTIVE:
# an existing character who already holds the token (quest 15 grants it on the
# kill, byte-identical base-vs-mod) gets the portal unlocked on next load.
# Every field layout below mirrors THIS quest's own byte-verified shapes: the
# condition blocks carry isQuestCritical but NOT isQuestCritical2 (older file
# format), and this file's Action_UnlockFixedItem carries NO delayTime field
# (unlike the x4 controller's) - copy the host file, never another file.
TYPHON_HOST_QUEST = 'quest that controls bosses and their doors.qst'
TYPHON_HOST_STEP = 'BOSS: Change the Loot Drops From Telkines & Typhon on Repeat Battles'
TYPHON_TOKEN = 'Olympus - Typhon Defeated'
RHODES_PORTAL = r'records\xpack\quests\objects\xq00_olympus_portaltorhodes.dbr'

# ── Q3 (build31, Will escalation): INSTANT Rhodes unlock + herald fallback ──
# Will (verbatim): "this is not the right unlock path to have to walk away and
# walk back in ... restore it to how it normally is in the base fucking game."
# ACCEPTANCE: kill Typhon -> the portal opens IMMEDIATELY, in view, no reload.
# Mechanism: a kill-gated trigger on the SAME host step -
#   Condition_KillAllCreaturesFromProxy(BossProxy_20_Typhon_Titan)
#     -> Action_UnlockFixedItem(xq00_olympus_portaltorhodes, canReFire=1)
# The proxy record is byte-verified LIVE: 'quest 15 - save olympus from
# typhon.qst' bestows the 'Olympus - Typhon Defeated' token on EXACTLY this
# condition shape, and Will HOLDS that token from his kill - the proxy name
# and the kill-condition mechanism are proven in his own session. Live
# in-session Action_UnlockFixedItem is equally proven (the blood-cave
# guardian-door quests open doors live). The Q1 token-gated OnLevelLoad
# trigger is KEPT: a character already holding the token (Will's main) gets
# the portal on next level entry without re-killing.
# Herald fallback (Model C): the map-placed NPC portal_master_olympus gets an
# Action_BoatDialog binding to the Rhodes arrival - the base game's OWN paired
# target xq00_rhodes_olympusportaltarget at world (700, 41, -6466) (signed-int
# coords, M12 navmesh-verified ON-MESH). Field shapes: conditions mirror the
# HOST's own byte-verified idioms (isQuestCritical w/o isQuestCritical2; the
# KillAllCreaturesFromProxy block mirrors the host's 19 existing ones);
# Action_BoatDialog mirrors base quest 7 (the only real-engine exemplar:
# comments, delayTime, npc, onOff, x, y, z, tag).
TYPHON_PROXY = r'Records\Proxies Boss\Boss\BossProxy_20_Typhon_Titan.dbr'
OLYMPUS_HERALD_NPC = r'records\quests\portal_master_olympus.dbr'
OLYMPUS_HERALD_TRAVEL_TAG = 'tagSVCOlympusRhodesTravel'
RHODES_ARRIVAL_XYZ = (700, 41, -6466)


def _add_olympus_rhodes_travel(data: bytes) -> bytes:
    """Append the instant kill-gated unlock + the herald boat-dialog binding
    to the Typhon host step (two trigger triples; strictly additive; the
    step's trigger-container max is incremented by 2). Fails loud if the host
    step is missing, the bytes do not round-trip, or the reference counts do
    not land exactly."""
    def field_val(items, key):
        for it in items:
            if it[0] == 'field' and it[1] == key:
                return it[2][1]
        return None

    kill_header = ('block', [
        ('field', 'displayTag', ('str', 'SVC: Instant Rhodes Unlock On Typhon Kill')),
        ('field', 'displayBitmap', ('int_or_empty', 0)),
        ('field', 'comments', ('int_or_empty', 0)),
        ('field', 'isActive', ('int', 0)),
    ])
    kill_conditions = ('block', [
        ('field', 'conditionCount', ('int', 1)),
        ('field', 'conditionClassName', ('str', 'Condition_KillAllCreaturesFromProxy')),
        ('block', [
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'isNot', ('int', 0)),
            ('field', 'isResettable', ('int', 1)),
            ('field', 'isQuestCritical', ('int', 0)),
            ('field', 'proxyRecord', ('str', TYPHON_PROXY)),
        ]),
    ])
    kill_actions = ('block', [
        ('field', 'actionCount', ('int', 1)),
        ('field', 'actionClassName', ('str', 'Action_UnlockFixedItem')),
        ('block', [
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'fixedItem', ('str', RHODES_PORTAL)),
            ('field', 'canReFire', ('int', 1)),
        ]),
    ])

    x, y, z = RHODES_ARRIVAL_XYZ
    herald_header = ('block', [
        ('field', 'displayTag', ('str', 'SVC: Olympus Herald - Sail To Rhodes')),
        ('field', 'displayBitmap', ('int_or_empty', 0)),
        ('field', 'comments', ('int_or_empty', 0)),
        ('field', 'isActive', ('int', 0)),
    ])
    herald_conditions = ('block', [
        ('field', 'conditionCount', ('int', 2)),
        ('field', 'conditionClassName', ('str', 'Condition_OnLevelLoad')),
        ('block', [
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'isNot', ('int', 0)),
            ('field', 'isResettable', ('int', 1)),
            ('field', 'isQuestCritical', ('int', 1)),
        ]),
        ('field', 'conditionClassName', ('str', 'Condition_OwnsTriggerToken')),
        ('block', [
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'isNot', ('int', 0)),
            ('field', 'isResettable', ('int', 1)),
            ('field', 'isQuestCritical', ('int', 1)),
            ('field', 'tokenName', ('str', TYPHON_TOKEN)),
        ]),
    ])
    herald_actions = ('block', [
        ('field', 'actionCount', ('int', 1)),
        ('field', 'actionClassName', ('str', 'Action_BoatDialog')),
        ('block', [
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'delayTime', ('int', 0)),
            ('field', 'npc', ('str', OLYMPUS_HERALD_NPC)),
            ('field', 'onOff', ('int', 1)),
            ('field', 'x', ('int', x & 0xFFFFFFFF)),
            ('field', 'y', ('int', y & 0xFFFFFFFF)),
            ('field', 'z', ('int', z & 0xFFFFFFFF)),
            ('field', 'tag', ('str', OLYMPUS_HERALD_TRAVEL_TAG)),
        ]),
    ])

    tree = qst_format.parse(data)
    steps_container = tree[1]
    positions = [i for i, it in enumerate(steps_container) if it[0] == 'block']
    step_triples = [positions[i:i + 3] for i in range(0, len(positions), 3)]

    patched = 0
    for stepdef_pos, trigcont_pos, _sentinel_pos in step_triples:
        stepdef = steps_container[stepdef_pos][1]
        if field_val(stepdef, 'name') != TYPHON_HOST_STEP:
            continue
        trigcont = list(steps_container[trigcont_pos][1])
        bumped = False
        for idx, it in enumerate(trigcont):
            if it[0] == 'field' and it[1] == 'max':
                trigcont[idx] = ('field', 'max', ('int', it[2][1] + 2))
                bumped = True
                break
        if not bumped:
            raise ValueError(f'{TYPHON_HOST_QUEST}: host step has no trigger max')
        trigcont.extend([kill_header, kill_conditions, kill_actions,
                         herald_header, herald_conditions, herald_actions])
        steps_container[trigcont_pos] = ('block', trigcont)
        patched += 1

    if patched != 1:
        raise ValueError(
            f'{TYPHON_HOST_QUEST}: expected to patch exactly 1 step '
            f'({TYPHON_HOST_STEP!r}), patched {patched}. Upstream changed; '
            f'review before shipping.')

    out = qst_format.serialize(tree)
    reparsed = qst_format.parse(out)
    if qst_format.serialize(reparsed) != out:
        raise ValueError(f'{TYPHON_HOST_QUEST}: patched quest does not '
                         f'round-trip stably')
    low = out.replace(b'/', b'\\').lower()
    low_in = data.replace(b'/', b'\\').lower()

    def _delta(needle):
        nd = needle.replace('/', '\\').lower().encode()
        return low.count(nd) - low_in.count(nd)
    if _delta(RHODES_PORTAL) != 1:
        raise ValueError(f'{TYPHON_HOST_QUEST}: Rhodes portal reference count '
                         f'must increase by exactly 1 (the kill unlock)')
    if _delta(TYPHON_PROXY) != 1:
        raise ValueError(f'{TYPHON_HOST_QUEST}: Typhon proxy reference count '
                         f'must increase by exactly 1 (the host already '
                         f'references it in its own repeat-battle triggers)')
    if _delta(OLYMPUS_HERALD_NPC) != 1:
        raise ValueError(f'{TYPHON_HOST_QUEST}: herald NPC reference count '
                         f'must increase by exactly 1')
    return out


def _add_typhon_rhodes_unlock(data: bytes) -> bytes:
    """Append the Rhodes-portal unlock trigger to the Typhon repeat-loot step.

    Strictly additive (one trigger triple; the step's trigger-container max is
    incremented). Fails loud if the host step is missing, if the emitted bytes
    do not round-trip, or if the addition is not exactly one unlock action.
    """
    def field_val(items, key):
        for it in items:
            if it[0] == 'field' and it[1] == key:
                return it[2][1]
        return None

    header = ('block', [
        ('field', 'displayTag', ('str', 'SVC: Unlock Olympus Portal To Rhodes')),
        ('field', 'displayBitmap', ('int_or_empty', 0)),
        ('field', 'comments', ('int_or_empty', 0)),
        ('field', 'isActive', ('int', 0)),
    ])
    conditions = ('block', [
        ('field', 'conditionCount', ('int', 2)),
        ('field', 'conditionClassName', ('str', 'Condition_OnLevelLoad')),
        ('block', [
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'isNot', ('int', 0)),
            ('field', 'isResettable', ('int', 1)),
            ('field', 'isQuestCritical', ('int', 1)),
        ]),
        ('field', 'conditionClassName', ('str', 'Condition_OwnsTriggerToken')),
        ('block', [
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'isNot', ('int', 0)),
            ('field', 'isResettable', ('int', 1)),
            ('field', 'isQuestCritical', ('int', 1)),
            ('field', 'tokenName', ('str', TYPHON_TOKEN)),
        ]),
    ])
    actions = ('block', [
        ('field', 'actionCount', ('int', 1)),
        ('field', 'actionClassName', ('str', 'Action_UnlockFixedItem')),
        ('block', [
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'fixedItem', ('str', RHODES_PORTAL)),
            ('field', 'canReFire', ('int', 1)),
        ]),
    ])

    tree = qst_format.parse(data)
    steps_container = tree[1]
    positions = [i for i, it in enumerate(steps_container) if it[0] == 'block']
    step_triples = [positions[i:i + 3] for i in range(0, len(positions), 3)]

    patched = 0
    for stepdef_pos, trigcont_pos, _sentinel_pos in step_triples:
        stepdef = steps_container[stepdef_pos][1]
        if field_val(stepdef, 'name') != TYPHON_HOST_STEP:
            continue
        trigcont = list(steps_container[trigcont_pos][1])
        bumped = False
        for idx, it in enumerate(trigcont):
            if it[0] == 'field' and it[1] == 'max':
                trigcont[idx] = ('field', 'max', ('int', it[2][1] + 1))
                bumped = True
                break
        if not bumped:
            raise ValueError(f'{TYPHON_HOST_QUEST}: host step has no trigger max')
        trigcont.extend([header, conditions, actions])
        steps_container[trigcont_pos] = ('block', trigcont)
        patched += 1

    if patched != 1:
        raise ValueError(
            f'{TYPHON_HOST_QUEST}: expected to patch exactly 1 step '
            f'({TYPHON_HOST_STEP!r}), patched {patched}. Upstream changed; '
            f'review before shipping.')

    out = qst_format.serialize(tree)
    reparsed = qst_format.parse(out)
    if qst_format.serialize(reparsed) != out:
        raise ValueError(f'{TYPHON_HOST_QUEST}: patched quest does not '
                         f'round-trip stably')
    # exactly one new unlock action pointing at the portal (qst strings are
    # 8-bit, so byte-level search is exact)
    hits = out.replace(b'/', b'\\').lower().count(
        RHODES_PORTAL.replace('/', '\\').lower().encode())
    if hits != 1:
        raise ValueError(f'{TYPHON_HOST_QUEST}: expected exactly 1 reference '
                         f'to the Rhodes portal after the patch, found {hits}')
    tok = TYPHON_TOKEN.encode()
    if out.count(tok) != data.count(tok) + 1:
        raise ValueError(f'{TYPHON_HOST_QUEST}: token reference count did not '
                         f'increase by exactly 1')
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

    # Q1 (build31): unlock the Olympus -> Rhodes portal for Typhon-slayers.
    # The host quest is an EXISTING SVAERA-arc entry, so this is a set_file
    # (in-place replacement), not an add.
    raw = arc.get_file(TYPHON_HOST_QUEST)
    if raw is None:
        raise SystemExit(f'Q1: host quest missing from Quests.arc: '
                         f'{TYPHON_HOST_QUEST}')
    patched = _add_typhon_rhodes_unlock(raw)
    print(f'Q1: Typhon->Rhodes portal unlock appended to {TYPHON_HOST_QUEST} '
          f'({len(raw)} -> {len(patched)} bytes)')
    # Q3 (Will escalation): instant kill-gated unlock + herald boat-dialog on
    # the same host step. Q1's token-gated reload path is KEPT above.
    patched2 = _add_olympus_rhodes_travel(patched)
    arc.set_file(TYPHON_HOST_QUEST, patched2)
    print(f'Q3: instant Typhon-kill unlock + Olympus herald boat-dialog '
          f'appended ({len(patched)} -> {len(patched2)} bytes)')

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

    # PERMANENT CONTRACT (B2): every quest record must be structurally loadable, or the
    # engine silently skips it (the four SV questlines were dead for four rebuilds because
    # their 44-byte ARC records left @16/@20/@24/@36 zero). Fail the build loud otherwise.
    _assert_quest_records_loadable(arc2)


if __name__ == '__main__':
    main()
