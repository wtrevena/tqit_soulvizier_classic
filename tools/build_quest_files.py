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
# deployed map's QUESTS section under the plain `Quests/<name>` namespace, and the
# shipped Quests.arc stores them at the ARCHIVE ROOT (basename). We add these at the
# root, mirroring how the other ~100 `Quests/`-namespaced quests are stored.
#
# ⚠️ CORRECTION (A5 act-5 leak RCA, 2026-07-11): the earlier claim here -- "the
# engine strips the folder prefix to the basename and resolves it at the root" -- is
# WRONG for DLC-namespaced quests, and it made the IT-cap (build33) 100% INERT. The
# per-quest save identity (`.que`) is `md5(lowercased FULL registry path, backslash-
# separated)`, NOT `quests\<basename>`. Root-basename storage only overrides a quest
# REGISTERED under the plain `Quests/` namespace. A quest the map registers under
# `XPack/quests/...` or `XPack4/quests/...` is identified AND its file resolved via
# that DLC namespace, which the engine reads from the base game's UNCAPPED
# `Resources/xpack/Quests.arc` / `XPack4/Quests.arc` -- a mod copy placed at the
# plain Quests.arc root is NEVER consulted for it. That is why the post-Hades cap on
# xquest_controlsbossdoors.qst (removing the portal_hadesscandia unlock) never
# loaded, and the North portal to Act 5 leaked through. Any "port a vanilla DLC
# controller with one action removed" fix MUST land in the matching mod
# `Resources/xpack/`/`XPack4/` archive, re-point the map registry, or (as A5 does)
# be done at the DB-record level (RequireNoDLC suppression). This is the exact
# sibling of the build22 widow-letter "inert fix" lesson (PLAYBOOK failure graveyard).
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
#        Leinth's trigger; the vortex ShowNpc/dialog actions were NOT duplicated -- the
#        boat-dialog idiom was judged fragile and double-firing it riskier than the
#        residual. ** SUPERSEDED by b94: see _promote_leinth_exit_fallbacks below. That
#        residual IS the live bug (door opens, no exit portal ever appears), so the three
#        Leinth fallbacks now carry the primary's FULL action set. **]
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


# ── b94 PART C: the POST-KILL EXIT to the occultist merchant ────────────────────
# WILL'S REPORT (paraphrase; ledgered R-74): after killing Leinth there is no way out
# of the Sanctuary of the Bloodborn - "after you kill her, a portal should open".
#
# THE MACHINERY IS ALREADY BUILT, PLACED AND AIMED. Nothing new is needed:
#   * records\drxmap\bloodcave\portals\vortexportal_exit.dbr is Class=Npc (AIType
#     generic, ActorName "Ioannes", description tagLeinthExitPortal, mesh
#     XPack\Items\shrines\teleport\credits_portal.msh + the DRX vortexportal01
#     texture - it LOOKS like a vortex but IS an NPC, which is exactly what the
#     boat-dialog traveler pattern needs). Its own FileDescription reads verbatim
#     "Exits the player after the Leinth boss fight."
#   * It is PLACED exactly ONCE across all 2,282 levels: bossfight.lvl local
#     (15.00, 3.26, 66.00) = world (3441, 3.26, 3178), 6.2u from Leinth's proxy,
#     on-navmesh (0.14u to the nearest walkable cell, component #0).
#   * Text already resolves tagLeinthExitPortal = "Mystical Vortex" and
#     tagReturnFromLeinthBattle = "Leave the Sanctuary of the Bloodborn?".
#   * The primary trigger "Open door on Leinth defeat" already carries the whole
#     4-action set: OpenDoor(door_bossroom_trap) + ShowNpc(vortexportal_exit) +
#     UpdateNPCDialog(vortexportal_exit, "Dialog Needed") + BoatDialog(
#     vortexportal_exit, x/y/z, tagReturnFromLeinthBattle).
#   * Its destination decodes signed to world (-90, -103, 2321) = inside
#     HiddenValleyBorder04, 9.79u from the OCCULTIST MERCHANT
#     (Merchant_HiddenValley_General) outside the blood-cave entrance, on the SAME
#     walkable component as the merchant and his wagon. So the shipped destination
#     ALREADY IS "the occultist merchant outside the cave".
#
# THE DEFECT - A TRIGGER ASYMMETRY. The rich primary trigger is keyed on
# Condition_KillAllCreaturesFromProxy(q_leinth_lone) with isResettable=0 (one-shot),
# and that pool ALSO carries nameChampion1-3 = b_med_blooddemon_30/31/32, so the
# condition needs EVERY creature the proxy produced dead. Meanwhile the three
# Condition_KillCreature fallbacks this file added in b48 (isResettable=1, one per
# q_leinth_47/49/50) carry ONLY Action_OpenDoor. So whenever the proxy-wide condition
# does not satisfy - an unaccounted champion blood demon, a character that did not
# have the quest tracked at kill time (the widow-letter class of bug, same quest
# family), or the one-shot having already latched - the player gets exactly what Will
# reports: the boss door opens and no exit portal ever appears.
#
# THE FIX (Quests.arc ONLY - Levels.arc is BYTE-UNCHANGED, no new quest entry, so the
# ~254-entry load-window law in docs/QUEST_STATE_INJECT.md is NOT engaged and the
# QUESTS section stays at exactly its current count):
#   1. Give each of the three isResettable=1 Leinth fallbacks the primary trigger's
#      OWN action block, copied VERBATIM out of the parsed tree. Copying rather than
#      re-authoring means the npc, the destination ints and the tag are byte-identical
#      to the shipped primary by construction - there is no hand-transcription risk.
#   2. Flip the primary's Condition_KillAllCreaturesFromProxy isResettable 0 -> 1 so a
#      revisit re-arms it.
# Net: the portal appears on ANY Leinth death, on any difficulty, for fresh AND
# existing characters, however the proxy resolves. Double-firing is harmless - ShowNpc
# on an already-shown NPC and a second identical BoatDialog offer are both no-ops, the
# same reasoning b48 used for the redundant door opens.
#
# WARDEN "1 route : 1 NPC" LAW: not engaged. All four triggers bind the SAME record to
# the SAME tag and the SAME destination, vortexportal_exit is placed exactly once
# across all 2,282 levels, and bossfight.lvl contains no other NPC.
#
# CANONICAL, NOT TESTHUB-ONLY: bossfight.lvl is an SV-native level present in both map
# variants, vortexportal_exit is an SV-NATIVE placement inside SV's own bossfight blob
# (NOT one of our INJECT_SPECS / build_hub_extra_specs additions), and Quests.arc is
# variant-independent. Because the fix places nothing, there is no TESTHUB-only risk at
# all: Workshop subscribers on canonical get the identical fix.
EXIT_NPC = r'records/drxmap/bloodcave/portals/vortexportal_exit.dbr'
EXIT_TAG = 'tagReturnFromLeinthBattle'
EXIT_PRIMARY_TRIGGER = 'Open door on Leinth defeat'
EXIT_FALLBACK_TRIGGER = 'Open Boss Trap Door Fallback'
EXIT_PROXY = r'records/drxmap/proxy/q_leinth_lone.dbr'
# The four action classes the primary carries, in order. The promoted fallbacks must
# end up with exactly this multiset.
EXIT_ACTION_CLASSES = ('Action_OpenDoor', 'Action_ShowNpc',
                       'Action_UpdateNPCDialog', 'Action_BoatDialog')


def _qst_block_positions(items):
    return [i for i, it in enumerate(items) if it[0] == 'block']


def _qst_field(items, key):
    for it in items:
        if it[0] == 'field' and it[1] == key:
            return it[2][1]
    return None


def _qst_set_field(items, key, value_tuple):
    """Replace field `key` in a block's item list IN PLACE. Returns True if found."""
    for idx, it in enumerate(items):
        if it[0] == 'field' and it[1] == key:
            items[idx] = ('field', key, value_tuple)
            return True
    return False


def _promote_leinth_exit_fallbacks(data: bytes) -> bytes:
    """Give the 3 Leinth kill fallbacks the primary trigger's FULL action set, and
    make the primary re-armable. See the block comment above.

    Strictly a REPLACEMENT of the three fallbacks' action blocks with a deep copy of
    the primary's, plus one isResettable flip. No trigger is added or removed, no
    condition is retargeted, no other step is touched. Fails loud if the primary or
    any fallback is missing, if the primary does not carry the expected 4 actions, or
    if the emitted bytes do not re-parse into exactly the intended shape.
    """
    import copy

    tree = qst_format.parse(data)
    steps_container = tree[1]
    positions = _qst_block_positions(steps_container)
    step_triples = [positions[i:i + 3] for i in range(0, len(positions), 3)]

    target_step = None
    for stepdef_pos, trigcont_pos, _sentinel_pos in step_triples:
        if _qst_field(steps_container[stepdef_pos][1], 'name') == HARDEN_STEP2_NAME:
            target_step = (stepdef_pos, trigcont_pos)
            break
    if target_step is None:
        raise ValueError(
            f'{BLOODCAVE_INTERIOR_QUEST}: step {HARDEN_STEP2_NAME!r} not found; the '
            f'Leinth exit-portal fix cannot be applied.')
    _stepdef_pos, trigcont_pos = target_step
    trigcont = list(steps_container[trigcont_pos][1])
    tpos = _qst_block_positions(trigcont)
    triples = [tpos[i:i + 3] for i in range(0, len(tpos), 3)]

    # ── locate the primary (proxy-wide) trigger and harvest its action block ──
    primary = None
    for (hpos, cpos, apos) in triples:
        conds = trigcont[cpos][1]
        if _qst_field(conds, 'conditionClassName') != 'Condition_KillAllCreaturesFromProxy':
            continue
        for it in conds:
            if it[0] != 'block':
                continue
            pr = _qst_field(it[1], 'proxyRecord')
            if isinstance(pr, str) and pr.replace('\\', '/').lower() == EXIT_PROXY:
                primary = (hpos, cpos, apos)
                break
        if primary:
            break
    if primary is None:
        raise ValueError(
            f'{BLOODCAVE_INTERIOR_QUEST}: the primary '
            f'Condition_KillAllCreaturesFromProxy({EXIT_PROXY}) trigger is gone; '
            f'refusing to guess the exit-portal action set.')
    p_h, p_c, p_a = primary

    if _qst_field(trigcont[p_h][1], 'displayTag') != EXIT_PRIMARY_TRIGGER:
        raise ValueError(
            f'{BLOODCAVE_INTERIOR_QUEST}: the proxy trigger is labelled '
            f'{_qst_field(trigcont[p_h][1], "displayTag")!r}, expected '
            f'{EXIT_PRIMARY_TRIGGER!r}; upstream changed, review before shipping.')

    primary_actions = trigcont[p_a][1]
    got_classes = tuple(it[2][1] for it in primary_actions
                        if it[0] == 'field' and it[1] == 'actionClassName')
    if got_classes != EXIT_ACTION_CLASSES:
        raise ValueError(
            f'{BLOODCAVE_INTERIOR_QUEST}: the primary Leinth trigger carries actions '
            f'{got_classes}, expected {EXIT_ACTION_CLASSES}. The exit-portal action '
            f'set moved; review before shipping.')
    if int(_qst_field(primary_actions, 'actionCount') or 0) != len(EXIT_ACTION_CLASSES):
        raise ValueError(f'{BLOODCAVE_INTERIOR_QUEST}: primary actionCount != '
                         f'{len(EXIT_ACTION_CLASSES)}')
    # prove the harvested block really targets the placed exit NPC + the offer tag
    npcs = [it[2][1] for blk in primary_actions if blk[0] == 'block'
            for it in blk[1] if it[0] == 'field' and it[1] == 'npc']
    if not npcs or any(n.replace('\\', '/').lower() != EXIT_NPC for n in npcs):
        raise ValueError(f'{BLOODCAVE_INTERIOR_QUEST}: primary trigger npc targets '
                         f'{npcs}, expected only {EXIT_NPC}')
    tagvals = [it[2][1] for blk in primary_actions if blk[0] == 'block'
               for it in blk[1] if it[0] == 'field' and it[1] == 'tag']
    if tagvals != [EXIT_TAG]:
        raise ValueError(f'{BLOODCAVE_INTERIOR_QUEST}: primary BoatDialog tag is '
                         f'{tagvals}, expected [{EXIT_TAG!r}]')

    # ── 1. promote every Leinth kill fallback ────────────────────────────────
    leinths = {s.lower() for s in GUARDIAN_LEINTHS}
    promoted = 0
    for (hpos, cpos, apos) in triples:
        if (hpos, cpos, apos) == primary:
            continue
        conds = trigcont[cpos][1]
        if _qst_field(conds, 'conditionClassName') != 'Condition_KillCreature':
            continue
        hit = False
        for it in conds:
            if it[0] != 'block':
                continue
            cr = _qst_field(it[1], 'creatureRecord')
            if isinstance(cr, str) and cr.replace('\\', '/').lower() in leinths:
                hit = True
        if not hit:
            continue
        trigcont[apos] = ('block', copy.deepcopy(primary_actions))
        promoted += 1

    if promoted != len(GUARDIAN_LEINTHS):
        raise ValueError(
            f'{BLOODCAVE_INTERIOR_QUEST}: promoted {promoted} Leinth kill fallback(s), '
            f'expected exactly {len(GUARDIAN_LEINTHS)} (one per q_leinth_47/49/50). '
            f'_harden_guardian_door_unlocks must run FIRST.')

    # ── 2. re-arm the primary (one-shot -> resettable) ───────────────────────
    rearmed = 0
    for it in trigcont[p_c][1]:
        if it[0] != 'block':
            continue
        blk = list(it[1])
        if _qst_field(blk, 'proxyRecord') is None:
            continue
        if int(_qst_field(blk, 'isResettable') or 0) != 1:
            if not _qst_set_field(blk, 'isResettable', ('int', 1)):
                raise ValueError(f'{BLOODCAVE_INTERIOR_QUEST}: primary condition has '
                                 f'no isResettable field')
            rearmed += 1
        idx = trigcont[p_c][1].index(it)
        trigcont[p_c][1][idx] = ('block', blk)

    steps_container[trigcont_pos] = ('block', trigcont)
    out = qst_format.serialize(tree)

    # ── fail-loud verification on the EMITTED bytes ──────────────────────────
    reparsed = qst_format.parse(out)
    if qst_format.serialize(reparsed) != out:
        raise ValueError('promoted quest does not round-trip stably')

    steps2 = reparsed[1]
    pos2 = _qst_block_positions(steps2)
    trip2 = [pos2[i:i + 3] for i in range(0, len(pos2), 3)]
    found_step = False
    exit_triggers = 0
    for sd, tc, _sn in trip2:
        if _qst_field(steps2[sd][1], 'name') != HARDEN_STEP2_NAME:
            continue
        found_step = True
        tc_items = steps2[tc][1]
        tp2 = _qst_block_positions(tc_items)
        for (h, c, a) in [tp2[i:i + 3] for i in range(0, len(tp2), 3)]:
            conds = tc_items[c][1]
            cls = _qst_field(conds, 'conditionClassName')
            is_leinth_kill = False
            is_primary = False
            for it in conds:
                if it[0] != 'block':
                    continue
                cr = _qst_field(it[1], 'creatureRecord')
                pr = _qst_field(it[1], 'proxyRecord')
                if isinstance(cr, str) and cr.replace('\\', '/').lower() in leinths:
                    is_leinth_kill = True
                if isinstance(pr, str) and pr.replace('\\', '/').lower() == EXIT_PROXY:
                    is_primary = True
                    if int(_qst_field(it[1], 'isResettable') or 0) != 1:
                        raise ValueError('exit-portal fix: the primary Leinth trigger '
                                         'is still one-shot (isResettable != 1)')
            if not (is_leinth_kill or is_primary):
                continue
            acts = tc_items[a][1]
            classes = tuple(it[2][1] for it in acts
                            if it[0] == 'field' and it[1] == 'actionClassName')
            if classes != EXIT_ACTION_CLASSES:
                raise ValueError(
                    f'exit-portal fix: a Leinth trigger ({cls}) carries {classes}, '
                    f'expected {EXIT_ACTION_CLASSES} - every Leinth death must open '
                    f'the door AND show the exit portal')
            if int(_qst_field(acts, 'actionCount') or 0) != len(EXIT_ACTION_CLASSES):
                raise ValueError('exit-portal fix: actionCount does not match the '
                                 'promoted action list')
            exit_triggers += 1
    if not found_step:
        raise ValueError(f'exit-portal fix: step {HARDEN_STEP2_NAME!r} vanished')
    want = len(GUARDIAN_LEINTHS) + 1
    if exit_triggers != want:
        raise ValueError(
            f'exit-portal fix: {exit_triggers} Leinth-death trigger(s) carry the exit '
            f'action set, expected {want} (the proxy primary + one per variant)')
    print(f'  {BLOODCAVE_INTERIOR_QUEST}: exit portal promoted onto {promoted} '
          f'Condition_KillCreature fallback(s) + primary re-armed '
          f'({rearmed} isResettable flip); {exit_triggers}/{want} Leinth-death '
          f'triggers now ShowNpc+BoatDialog {EXIT_NPC.rsplit("/", 1)[-1]}')
    return out


# ── b94 ROUND 3 PART C: the NO-KILL exit fallback ──────────────────────────────
# WILL 2026-07-27 (Q9, answering the residual R-74 flagged): "ADD THE NO-KILL
# FALLBACK. Show the exit whenever the boss trap door is already open, regardless of
# whether the kill trigger latched - so a character who already killed her
# (INCLUDING WILL'S OWN) is rescued rather than stranded."
#
# WHY IT IS NOT LITERALLY "if the door is open": the .qst condition vocabulary has no
# door-state test. The 14 condition classes qst_format supports are AnimationCompleted,
# CharacterHasItem, ConversationStart, CounterState, EnterVolume, ExitVolume, GotToken,
# KillAllCreaturesFromProxy, KillCreature, MoveCompleted, OnLevelLoad, OnQuestComplete,
# OwnsTriggerToken, PickupItem, UseFixedItem. None reads a FixedItemDoor's open state,
# and the primary's Action_OpenDoor grants no token to test for. So the only mechanism
# that satisfies Will's REQUIREMENT (nobody is ever stranded, including his own already
# -latched character) is Condition_OnLevelLoad: every time the boss level loads, the
# exit NPC is shown and given its travel offer.
#
# DELIBERATELY WITHOUT Action_OpenDoor. The boss trap door stays earned - this trigger
# only reveals the way OUT. A player who has not killed her gains nothing but the sight
# of the vortex; the door, the fight and the loot are all untouched.
#
# THE ONE COST, STATED: because OnLevelLoad fires on EVERY entry, the vortex is visible
# from the moment the player walks into the Sanctuary rather than appearing at the
# instant she dies. That trades R-74's reveal for Will's guarantee. It is flagged in the
# wave report as a Will-decision item; if he prefers the reveal, delete this one trigger
# and the three kill fallbacks still cover every case except an already-latched
# character (which is exactly the case he asked to rescue).
#
# Double-firing is harmless and already precedented here: the existing block comment
# notes "the second unlock/open of an already-unlocked/open item is a no-op", and
# round 1 already ships the same ShowNpc/BoatDialog set on four triggers.
EXIT_NOKILL_TRIGGER = 'Show Exit Portal Fallback'
EXIT_NOKILL_ACTION_CLASSES = ('Action_ShowNpc', 'Action_UpdateNPCDialog',
                              'Action_BoatDialog')


def _add_leinth_exit_nokill_fallback(data: bytes) -> bytes:
    """ADD one Condition_OnLevelLoad trigger carrying the primary's portal actions
    minus Action_OpenDoor. Strictly additive: one trigger appended to the
    "Boss Room Crystal Gate" step, its container `max` incremented to match. Fails
    loud if the primary is missing, if its action set moved, if stripping OpenDoor
    does not leave exactly the 3 expected actions, or if the emitted bytes do not
    re-parse into the intended shape. Idempotent: a second run is a no-op.
    """
    import copy

    tree = qst_format.parse(data)
    steps_container = tree[1]
    positions = _qst_block_positions(steps_container)
    step_triples = [positions[i:i + 3] for i in range(0, len(positions), 3)]

    target = None
    for stepdef_pos, trigcont_pos, _sent in step_triples:
        if _qst_field(steps_container[stepdef_pos][1], 'name') == HARDEN_STEP2_NAME:
            target = trigcont_pos
            break
    if target is None:
        raise ValueError(f'{BLOODCAVE_INTERIOR_QUEST}: step {HARDEN_STEP2_NAME!r} not '
                         f'found; the no-kill exit fallback cannot be applied.')
    trigcont = list(steps_container[target][1])
    tpos = _qst_block_positions(trigcont)
    triples = [tpos[i:i + 3] for i in range(0, len(tpos), 3)]

    # idempotence: already added?
    for (hpos, _c, _a) in triples:
        if _qst_field(trigcont[hpos][1], 'displayTag') == EXIT_NOKILL_TRIGGER:
            print(f'  {BLOODCAVE_INTERIOR_QUEST}: no-kill exit fallback already '
                  f'present; no-op')
            return data

    # harvest the primary's action block (it is the single source of truth for the
    # NPC record, the destination coordinates and the offer tag)
    primary_actions = None
    for (_h, cpos, apos) in triples:
        conds = trigcont[cpos][1]
        if _qst_field(conds, 'conditionClassName') != 'Condition_KillAllCreaturesFromProxy':
            continue
        for it in conds:
            if it[0] == 'block' and isinstance(_qst_field(it[1], 'proxyRecord'), str) \
                    and _qst_field(it[1], 'proxyRecord').replace('\\', '/').lower() == EXIT_PROXY:
                primary_actions = trigcont[apos][1]
                break
        if primary_actions is not None:
            break
    if primary_actions is None:
        raise ValueError(
            f'{BLOODCAVE_INTERIOR_QUEST}: the primary '
            f'Condition_KillAllCreaturesFromProxy({EXIT_PROXY}) trigger is gone; '
            f'refusing to guess the exit-portal action set for the no-kill fallback.')
    got = tuple(it[2][1] for it in primary_actions
                if it[0] == 'field' and it[1] == 'actionClassName')
    if got != EXIT_ACTION_CLASSES:
        raise ValueError(
            f'{BLOODCAVE_INTERIOR_QUEST}: primary carries {got}, expected '
            f'{EXIT_ACTION_CLASSES}; _promote_leinth_exit_fallbacks must run FIRST.')

    # strip Action_OpenDoor (classname field + its following block), keep the rest
    kept, i = [], 0
    src = list(primary_actions)
    while i < len(src):
        it = src[i]
        if it[0] == 'field' and it[1] == 'actionClassName':
            blk = src[i + 1] if i + 1 < len(src) else None
            if blk is None or blk[0] != 'block':
                raise ValueError(f'{BLOODCAVE_INTERIOR_QUEST}: action {it[2][1]!r} has '
                                 f'no parameter block')
            if it[2][1] != 'Action_OpenDoor':
                kept.append(('field', 'actionClassName', ('str', it[2][1])))
                kept.append(('block', copy.deepcopy(blk[1])))
            i += 2
            continue
        i += 1
    kept_classes = tuple(it[2][1] for it in kept
                         if it[0] == 'field' and it[1] == 'actionClassName')
    if kept_classes != EXIT_NOKILL_ACTION_CLASSES:
        raise ValueError(
            f'{BLOODCAVE_INTERIOR_QUEST}: stripping Action_OpenDoor left '
            f'{kept_classes}, expected {EXIT_NOKILL_ACTION_CLASSES}')

    header = ('block', [
        ('field', 'displayTag', ('str', EXIT_NOKILL_TRIGGER)),
        ('field', 'displayBitmap', ('int_or_empty', 0)),
        ('field', 'comments', ('int_or_empty', 0)),
        ('field', 'isActive', ('int', 0)),
        ('field', 'bRatchet', ('int', 0)),
    ])
    conditions = ('block', [
        ('field', 'conditionCount', ('int', 1)),
        ('field', 'conditionClassName', ('str', 'Condition_OnLevelLoad')),
        ('block', [
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'isNot', ('int', 0)),
            ('field', 'isResettable', ('int', 1)),   # re-arms on every entry
            ('field', 'isQuestCritical', ('int', 0)),
        ]),
    ])
    actions = ('block', [('field', 'actionCount', ('int', len(EXIT_NOKILL_ACTION_CLASSES)))]
               + kept)

    bumped = False
    for idx, it in enumerate(trigcont):
        if it[0] == 'field' and it[1] == 'max':
            trigcont[idx] = ('field', 'max', ('int', it[2][1] + 1))
            bumped = True
            break
    if not bumped:
        raise ValueError(f'{BLOODCAVE_INTERIOR_QUEST}: step {HARDEN_STEP2_NAME!r} '
                         f'trigger container has no max field')
    trigcont.extend([header, conditions, actions])
    steps_container[target] = ('block', trigcont)
    out = qst_format.serialize(tree)

    # ── fail-loud verification on the EMITTED bytes ─────────────────────────
    reparsed = qst_format.parse(out)
    if qst_format.serialize(reparsed) != out:
        raise ValueError('no-kill exit fallback does not round-trip stably')
    steps2 = reparsed[1]
    pos2 = _qst_block_positions(steps2)
    found = 0
    for sd, tc, _sn in [pos2[i:i + 3] for i in range(0, len(pos2), 3)]:
        if _qst_field(steps2[sd][1], 'name') != HARDEN_STEP2_NAME:
            continue
        items = steps2[tc][1]
        tp = _qst_block_positions(items)
        for (h, c, a) in [tp[i:i + 3] for i in range(0, len(tp), 3)]:
            if _qst_field(items[h][1], 'displayTag') != EXIT_NOKILL_TRIGGER:
                continue
            found += 1
            if _qst_field(items[c][1], 'conditionClassName') != 'Condition_OnLevelLoad':
                raise ValueError('no-kill fallback: condition class is not OnLevelLoad')
            cls = tuple(it[2][1] for it in items[a][1]
                        if it[0] == 'field' and it[1] == 'actionClassName')
            if cls != EXIT_NOKILL_ACTION_CLASSES:
                raise ValueError(f'no-kill fallback: emitted actions {cls}')
            if 'Action_OpenDoor' in cls:
                raise ValueError('no-kill fallback must NOT open the boss trap door')
            npcs = [it[2][1] for blk in items[a][1] if blk[0] == 'block'
                    for it in blk[1] if it[0] == 'field' and it[1] == 'npc']
            if not npcs or any(n.replace('\\', '/').lower() != EXIT_NPC for n in npcs):
                raise ValueError(f'no-kill fallback: npc targets {npcs}, expected '
                                 f'only {EXIT_NPC}')
            tagvals = [it[2][1] for blk in items[a][1] if blk[0] == 'block'
                       for it in blk[1] if it[0] == 'field' and it[1] == 'tag']
            if tagvals != [EXIT_TAG]:
                raise ValueError(f'no-kill fallback: BoatDialog tag {tagvals}')
    if found != 1:
        raise ValueError(f'no-kill fallback: emitted {found} trigger(s), expected 1')
    print(f'  {BLOODCAVE_INTERIOR_QUEST}: no-kill exit fallback added '
          f'(Condition_OnLevelLoad -> ShowNpc+UpdateNPCDialog+BoatDialog, NO '
          f'OpenDoor) - an already-latched character is never stranded again')
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
            # Q4-2 rides the same port: align the honor-branch chest watch.
            out[name] = _fix_widowletter_chest_branch(
                _neutralize_widowletter_spawn(data))
        elif name == 'bossarena.qst':
            # Q4-1: retarget the arena-entry volume to the placed record.
            out[name] = _fix_bossarena_entervolume(data)
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
    # b94 PART C: after the b48 hardening has added the 3 Leinth kill fallbacks,
    # PROMOTE them to carry the primary trigger's FULL exit-portal action set and
    # re-arm the primary (see _promote_leinth_exit_fallbacks). Order is load-bearing:
    # the promotion asserts the 3 fallbacks exist, so hardening must run first.
    # b94 ROUND 3: then ADD the no-kill fallback Will asked for on 2026-07-27 - a
    # Condition_OnLevelLoad trigger carrying the same ShowNpc/UpdateNPCDialog/
    # BoatDialog set WITHOUT Action_OpenDoor, so a character who already killed her
    # while the one-shot was latched is rescued instead of stranded. It runs LAST
    # because it harvests (and asserts) the promoted primary's action block.
    bc = _upstream_quest_bytes(arc, BLOODCAVE_INTERIOR_QUEST)
    _assert_roundtrip(BLOODCAVE_INTERIOR_QUEST, bc)
    out[BLOODCAVE_INTERIOR_QUEST] = _add_leinth_exit_nokill_fallback(
        _promote_leinth_exit_fallbacks(
            _harden_guardian_door_unlocks(
                _neutralize_bloodcave_entry_step(bc))))

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


# ── Q2 (build32, Group A): Helos portal-master -> 4 SV-area boat destinations ─
# Will chose Model C (boat-dialog NPC) for SV-area travel. This mirrors
# _add_olympus_rhodes_travel exactly: a single Action_BoatDialog trigger
# appended to an already-registered, always-loaded host quest. The difference:
# ONE trigger with FOUR Action_BoatDialog actions (one per SV destination), all
# on the SAME npc (records\quests\portal_master_helos.dbr, shipped by
# apply_svc_patches _create_helos_portal_master). Base precedent: quest 8
# registers Knossos->Rhakotis on ONE boatman via Action_BoatDialog; multiple
# calls on one npc accumulate destinations on its menu. NO token gate - the SV
# side-areas are optional and available from the start (Condition_OnLevelLoad
# fires on every level load and re-registers the four ports idempotently).
# HOST = sv_commonmechanics.qst (registered idx 96, always loaded), its
# "never completes / refire" step - the natural home for a standing OnLevelLoad
# trigger; NO new QUESTS registration (registry law). Field shapes mirror the
# herald's byte-verified idioms; x/y/z are signed-int world coords (base
# exemplar decoded: two's-complement negatives). Landing coords come from the
# map lane's build_section_surgery.py PORTAL_MASTER destination list.
HELOS_PORTAL_HOST_QUEST = 'sv_commonmechanics.qst'
HELOS_PORTAL_HOST_STEP = ('Makes it so Quest Never Completes -- '
                          'Allows for refiring on triggers')
HELOS_PORTAL_NPC = r'records\quests\portal_master_helos.dbr'
# (world x, y, z), boat-menu label tag - one per SV side-area destination.
HELOS_PORTAL_DESTS = [
    ((1173, -39, -4001), 'tagSVCHelosToGarden'),   # Garden of Merchants (N1 H2 landing)
    ((-2396, 2, -5790), 'tagSVCHelosToSecret'),    # The Secret Place (A2 S2 landing)
    ((-2438, 10, -2450), 'tagSVCHelosToUber'),     # Uber Dungeon (SV-native A1 arrival)
    ((-5602, -2, -1409), 'tagSVCHelosToSparta'),   # Sparta Crypt (hub landing)
]
# RECONCILIATION NOTE (b62 TRAVELERS-INTO-AREAS, Will 2026-07-14 final - "reconcile the Almyros
# divergent tagSVCHelosToSparta dest"): tagSVCHelosToUber/tagSVCHelosToSparta above land INSIDE
# the interior (crypt_floor1 / spartacryptlevel2), while the SAME tags on the live hub traveler
# (svc_helos_trav_uber/_sparta, HELOS_HUB_TRAVEL below) land at the OUTER door/catacomb approach
# point instead. Investigated and DELIBERATELY LEFT AS-IS - this is NOT a bug to unify, because the
# two NPCs serve genuinely different roles on genuinely different builds:
#   - portal_master_helos (Almyros) is placed ONLY on canonical/Steam (0x in TESTHUB - de-duped by
#     merge_hub_into_inject_specs). On canonical there is NO outer-door traveler at all
#     (svc_area_return_sparta/_uber are TESTHUB-only, per T2), so Almyros's interior landing IS the
#     sole live mechanism canonical/Steam players use to reach these two areas today. Redirecting
#     it to the door coordinate would silently STRAND every canonical player who currently reaches
#     the crypt/dungeon this way (no traveler exists at the door on canonical to compensate) - a
#     live regression, not a fix.
#   - svc_helos_trav_sparta/_uber are TESTHUB-only (per Will's v2 hub design: "teleport me next to
#     the door you'd use in game, not the final destination") and are correctly paired with the
#     TESTHUB-only svc_area_return_sparta/_uber (which now carry the enter-offer into the interior;
#     see TRAVELER_ENTER_OFFERS below) - a deliberately different, richer round trip for the dev/
#     test surface.
# Reusing the SAME menu-label tag across the two builds for the SAME area name is intentional and
# harmless (never the same level in either build, so gate_traveler_responds' same-level route-
# collision check never sees both at once - verified: canonical places Almyros but not the hub
# traveler; TESTHUB places the hub traveler but not Almyros). Left BOTH tables byte-unchanged.


def _add_helos_portal_travel(data: bytes) -> bytes:
    """Append the 4-destination Helos portal-master boat-dialog trigger to the
    sv_commonmechanics refire step. Strictly additive (one trigger triple with
    four Action_BoatDialog actions; the step's trigger-container max is bumped
    by 1). Fails loud if the host step is missing, the bytes do not round-trip,
    or the reference-count deltas do not land exactly."""
    def field_val(items, key):
        for it in items:
            if it[0] == 'field' and it[1] == key:
                return it[2][1]
        return None

    helos_header = ('block', [
        ('field', 'displayTag', ('str', 'SVC: Helos Portal-Master - SV Area Travel')),
        ('field', 'displayBitmap', ('int_or_empty', 0)),
        ('field', 'comments', ('int_or_empty', 0)),
        ('field', 'isActive', ('int', 0)),
    ])
    helos_conditions = ('block', [
        ('field', 'conditionCount', ('int', 1)),
        ('field', 'conditionClassName', ('str', 'Condition_OnLevelLoad')),
        ('block', [
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'isNot', ('int', 0)),
            ('field', 'isResettable', ('int', 1)),
            ('field', 'isQuestCritical', ('int', 1)),
        ]),
    ])

    def _boatdialog(xyz, tag):
        x, y, z = xyz
        return [
            ('field', 'actionClassName', ('str', 'Action_BoatDialog')),
            ('block', [
                ('field', 'comments', ('int_or_empty', 0)),
                ('field', 'delayTime', ('int', 0)),
                ('field', 'npc', ('str', HELOS_PORTAL_NPC)),
                ('field', 'onOff', ('int', 1)),
                ('field', 'x', ('int', x & 0xFFFFFFFF)),
                ('field', 'y', ('int', y & 0xFFFFFFFF)),
                ('field', 'z', ('int', z & 0xFFFFFFFF)),
                ('field', 'tag', ('str', tag)),
            ]),
        ]

    helos_action_items = [('field', 'actionCount', ('int', len(HELOS_PORTAL_DESTS)))]
    for xyz, tag in HELOS_PORTAL_DESTS:
        helos_action_items.extend(_boatdialog(xyz, tag))
    helos_actions = ('block', helos_action_items)

    tree = qst_format.parse(data)
    steps_container = tree[1]
    positions = [i for i, it in enumerate(steps_container) if it[0] == 'block']
    step_triples = [positions[i:i + 3] for i in range(0, len(positions), 3)]

    patched = 0
    for stepdef_pos, trigcont_pos, _sentinel_pos in step_triples:
        stepdef = steps_container[stepdef_pos][1]
        if field_val(stepdef, 'name') != HELOS_PORTAL_HOST_STEP:
            continue
        trigcont = list(steps_container[trigcont_pos][1])
        bumped = False
        for idx, it in enumerate(trigcont):
            if it[0] == 'field' and it[1] == 'max':
                trigcont[idx] = ('field', 'max', ('int', it[2][1] + 1))
                bumped = True
                break
        if not bumped:
            raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: host step has no '
                             f'trigger max')
        trigcont.extend([helos_header, helos_conditions, helos_actions])
        steps_container[trigcont_pos] = ('block', trigcont)
        patched += 1

    if patched != 1:
        raise ValueError(
            f'{HELOS_PORTAL_HOST_QUEST}: expected to patch exactly 1 step '
            f'({HELOS_PORTAL_HOST_STEP!r}), patched {patched}. Upstream '
            f'changed; review before shipping.')

    out = qst_format.serialize(tree)
    if qst_format.serialize(qst_format.parse(out)) != out:
        raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: patched quest does not '
                         f'round-trip stably')
    low = out.replace(b'/', b'\\').lower()
    low_in = data.replace(b'/', b'\\').lower()

    def _delta(needle):
        nd = needle.replace('/', '\\').lower().encode()
        return low.count(nd) - low_in.count(nd)
    if _delta(HELOS_PORTAL_NPC) != len(HELOS_PORTAL_DESTS):
        raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: portal-master NPC '
                         f'reference count must increase by exactly '
                         f'{len(HELOS_PORTAL_DESTS)} (one per destination)')
    for _xyz, tag in HELOS_PORTAL_DESTS:
        if _delta(tag) != 1:
            raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: destination tag '
                             f'{tag} reference count must increase by exactly 1')
    return out


# ── PORTAL RIG (2026-07-10, GROUP 2 unblock): TESTHUB Model C travel triggers ─
# The flag-gated LOCAL-ONLY travel rig. Two boat-dialog triggers appended to the
# SAME always-loaded sv_commonmechanics refire step (registry law: no new QUESTS
# registration), each keyed on a DISTINCT rig NPC record (apply_svc_patches
# _create_testhub_portal_npcs). Mirrors _add_helos_portal_travel exactly, only
# with two triggers instead of one, and MUST key on the new rig NPCs ONLY - never
# on canonical Almyros/portal_master_helos, or the Boss Arena / Blood Cave ports
# would leak into the shipped Helos menu (spec risk #3).
#   HUB (svc_testhub_master):  7 ports - Garden, Secret, Uber, Sparta, Boss
#       Arena, Blood Cave interior, Helos return.
#   RETURN (svc_testhub_return): 2 ports - Helos, Blood Cave interior.
# INERT on canonical: the ports register onto NPCs the canonical map never places
# (D3 unplaced-record no-op; the Almyros precedent). ALL 7 landing coords were
# surveyed ON-MESH against the canonical d5259629 map. NOTE: Garden/Secret/Uber/
# Sparta reuse the shipped Almyros table (re-verified on-mesh); Boss Arena was
# 0x0b-surveyed (on-mesh, 90u off volume_startolympianarena); Blood Cave was
# RE-DERIVED (the spec's old (-168,19,2162) is ~6200u stale - Random09A now sits
# at corner (5979,18,3243)); Helos return surveyed on-mesh.
TESTHUB_MASTER_NPC = r'records\quests\svc_testhub_master.dbr'
TESTHUB_RETURN_NPC = r'records\quests\svc_testhub_return.dbr'
TESTHUB_MASTER_DESTS = [
    ((1173, -39, -4001), 'tagSVCHelosToGarden'),      # Garden of Merchants (GardenofMerchants.lvl)
    ((-2396, 2, -5790), 'tagSVCHelosToSecret'),       # The Secret Place (DarkForestEnter.lvl)
    ((-2438, 10, -2450), 'tagSVCHelosToUber'),        # The Uber Dungeon (crypt_floor1.lvl)
    ((-5602, -2, -1409), 'tagSVCHelosToSparta'),      # The Sparta Crypt (SpartaCryptLevel2.lvl)
    ((-429, 27, -3538), 'tagSVCTestHubToBossArena'),  # Boss Arena (boss_arena.lvl; b43-r2: ON the raised arena dais comp#2 [world y~27], 26u S of the boss spawn / outside the r20 trigger. Was (-433,0,-3602) on comp#1 - the low floor, unreachable from the fight [28u cliff, isolated navmesh island])
    ((6018, 19, 3293), 'tagSVCTestHubToBloodCave'),   # Blood Cave interior (Random09A.lvl)
    ((-5980, 1, 909), 'tagSVCTestHubToHelos'),        # Helos plaza (StartingFarmland06D.lvl)
]
TESTHUB_RETURN_DESTS = [
    ((-5980, 1, 909), 'tagSVCTestHubToHelos'),        # Helos plaza
    ((6018, 19, 3293), 'tagSVCTestHubToBloodCave'),   # Blood Cave interior
]
# TRAVELERS-INTO-AREAS b62 (Will 2026-07-14 final, item 2): per-NPC override of the shared 2-port
# TESTHUB_RETURN_DESTS. Sparta's + Uber's interior return NPC (already stranded there) now returns
# to WHERE THE PLAYER TRAVELED FROM: primary = the paired ORIGIN entrance (the outer landing where
# the area's enter-offer traveler stands - see TRAVELER_ENTER_OFFERS below), secondary = Helos. A
# static 2-option dialog (the engine has no dynamic "where you came from" state - this is the best
# static approximation of Will's ask; flagged for him in the report). Garden/Secret/Boss-Arena are
# NOT overridden here and keep the existing Helos+BloodCave menu unchanged: they are single-hop
# from Helos already (their "origin" already IS Helos), so touching them isn't required by this
# design and would only widen this wave's blast radius.
TESTHUB_RETURN_DESTS_BY_NPC = {
    r'records\quests\svc_testhub_return_sparta.dbr': [
        ((-6587, 1, -3180), 'tagSVCReturnToAthensCatacomb'),  # origin: Athens catacomb door (primary)
        ((-5980, 1, 909),   'tagSVCTestHubToHelos'),          # Helos plaza (secondary)
    ],
    r'records\quests\svc_testhub_return_uber.dbr': [
        ((-7793, 1, -3793), 'tagSVCReturnToLabyrinthDoor'),   # origin: Knossos maze03 Minotaur door (primary)
        ((-5980, 1, 909),   'tagSVCTestHubToHelos'),          # Helos plaza (secondary)
    ],
}
# b48 SPARTA-MUTE round 3 (WARDEN-SPLIT of svc_testhub_return): svc_testhub_return was PLACED in 5
# levels (Garden/Secret/Uber/Sparta canonical + Boss Arena TESTHUB) but a boat-dialog record binds
# its menu to ONE entity, so 4 of the 5 returns spawned MUTE. It is split into these 5 DISTINCT
# per-area records, each placed ONCE and given its OWN 2-port trigger below (records: apply_svc_
# patches TESTHUB_AREA_RETURN_NPCS; placement: build_section_surgery). Names carry the area so the
# trigger displayTag + the map placement + the arz record all read the same lineage.
TESTHUB_AREA_RETURN_NPCS = [
    r'records\quests\svc_testhub_return_garden.dbr',
    r'records\quests\svc_testhub_return_secret.dbr',
    r'records\quests\svc_testhub_return_uber.dbr',
    r'records\quests\svc_testhub_return_sparta.dbr',
    r'records\quests\svc_testhub_return_bossarena.dbr',
]


def _add_testhub_portal_travel(data: bytes) -> bytes:
    """Append the TESTHUB per-area RETURN boat-dialog triggers (Model C) to the
    sv_commonmechanics refire step: one Condition_OnLevelLoad trigger per warden-split
    per-area return record (len(TESTHUB_AREA_RETURN_NPCS) = 5), each carrying the same
    2-port menu (Helos + Blood Cave) svc_testhub_return used. Strictly additive (the
    step's trigger max is bumped by len(TESTHUB_AREA_RETURN_NPCS)). Fails loud if the host
    step is missing, the bytes do not round-trip, or the reference-count deltas do not land
    exactly.

    b48 SPARTA-MUTE (round 3, docs/reports/b48_sparta_mute.md - WARDEN-SPLIT of the return):
    svc_testhub_return was PLACED in 5 levels (Garden/Secret/Uber/Sparta canonical + Boss
    Arena TESTHUB), but an Action_BoatDialog binds its menu to the ONE entity the record
    resolves to, so only the first-bound return responded and the other 4 spawned MUTE
    (the documented warden law - one record == one live placement). It is now split into 5
    DISTINCT per-area records, each placed once and given its OWN 2-port trigger here, so
    every return fires. The single svc_testhub_return trigger this function used to emit is
    REPLACED by these 5; svc_testhub_return itself is retired (unplaced + untriggered = an
    inert record kept in the arz).

    NOTE (round-1 rationale RETRACTED in round 2): the svc_testhub_master 7-port trigger is
    dropped elsewhere, but NOT because of any 'bounded boat-offer registry / past-the-cap
    overflow' - that theory was debunked (the base game fires 20+ OnLevelLoad boat triggers
    in one step, and the LATE unique-route travelers were exactly the ones that WORKED). The
    real Sparta mute was an in-LEVEL route collision with the canonical Almyros (fixed by the
    plaza de-dup in build_section_surgery.merge_hub_into_inject_specs); dropping the UNPLACED
    svc_testhub_master is harmless cleanup under per-level route ownership, not a mute fix."""
    def field_val(items, key):
        for it in items:
            if it[0] == 'field' and it[1] == key:
                return it[2][1]
        return None

    def _boatdialog(npc, xyz, tag):
        x, y, z = xyz
        return [
            ('field', 'actionClassName', ('str', 'Action_BoatDialog')),
            ('block', [
                ('field', 'comments', ('int_or_empty', 0)),
                ('field', 'delayTime', ('int', 0)),
                ('field', 'npc', ('str', npc)),
                ('field', 'onOff', ('int', 1)),
                ('field', 'x', ('int', x & 0xFFFFFFFF)),
                ('field', 'y', ('int', y & 0xFFFFFFFF)),
                ('field', 'z', ('int', z & 0xFFFFFFFF)),
                ('field', 'tag', ('str', tag)),
            ]),
        ]

    def _trigger(display, npc, dests):
        header = ('block', [
            ('field', 'displayTag', ('str', display)),
            ('field', 'displayBitmap', ('int_or_empty', 0)),
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'isActive', ('int', 0)),
        ])
        conditions = ('block', [
            ('field', 'conditionCount', ('int', 1)),
            ('field', 'conditionClassName', ('str', 'Condition_OnLevelLoad')),
            ('block', [
                ('field', 'comments', ('int_or_empty', 0)),
                ('field', 'isNot', ('int', 0)),
                ('field', 'isResettable', ('int', 1)),
                ('field', 'isQuestCritical', ('int', 1)),
            ]),
        ])
        action_items = [('field', 'actionCount', ('int', len(dests)))]
        for xyz, tag in dests:
            action_items.extend(_boatdialog(npc, xyz, tag))
        actions = ('block', action_items)
        return [header, conditions, actions]

    tree = qst_format.parse(data)
    steps_container = tree[1]
    positions = [i for i, it in enumerate(steps_container) if it[0] == 'block']
    step_triples = [positions[i:i + 3] for i in range(0, len(positions), 3)]

    patched = 0
    for stepdef_pos, trigcont_pos, _sentinel_pos in step_triples:
        stepdef = steps_container[stepdef_pos][1]
        if field_val(stepdef, 'name') != HELOS_PORTAL_HOST_STEP:
            continue
        trigcont = list(steps_container[trigcont_pos][1])
        bumped = False
        for idx, it in enumerate(trigcont):
            if it[0] == 'field' and it[1] == 'max':
                # b48 round 3: +len(TESTHUB_AREA_RETURN_NPCS) (one 2-port trigger per warden-split
                # per-area return). The single svc_testhub_return trigger + the dead
                # svc_testhub_master trigger are both gone.
                trigcont[idx] = ('field', 'max',
                                 ('int', it[2][1] + len(TESTHUB_AREA_RETURN_NPCS)))
                bumped = True
                break
        if not bumped:
            raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: host step has no '
                             f'trigger max')
        # b48 SPARTA-MUTE round 3 (WARDEN-SPLIT): one 2-port return trigger per distinct per-area
        # record (replaces the single svc_testhub_return trigger). svc_testhub_master stays dropped.
        # b62 TRAVELERS-INTO-AREAS: Sparta/Uber use TESTHUB_RETURN_DESTS_BY_NPC (return-to-origin);
        # every other per-area return keeps the shared TESTHUB_RETURN_DESTS (Helos + Blood Cave).
        for npc in TESTHUB_AREA_RETURN_NPCS:
            dests = TESTHUB_RETURN_DESTS_BY_NPC.get(npc, TESTHUB_RETURN_DESTS)
            trigcont.extend(_trigger(f'SVC: TESTHUB Return NPC ({npc.split(chr(92))[-1]})',
                                     npc, dests))
        steps_container[trigcont_pos] = ('block', trigcont)
        patched += 1

    if patched != 1:
        raise ValueError(
            f'{HELOS_PORTAL_HOST_QUEST}: TESTHUB rig expected to patch exactly 1 '
            f'step ({HELOS_PORTAL_HOST_STEP!r}), patched {patched}. Upstream '
            f'changed; review before shipping.')

    out = qst_format.serialize(tree)
    if qst_format.serialize(qst_format.parse(out)) != out:
        raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: TESTHUB-patched quest does '
                         f'not round-trip stably')
    low = out.replace(b'/', b'\\').lower()
    low_in = data.replace(b'/', b'\\').lower()

    def _delta(needle):
        nd = needle.replace('/', '\\').lower().encode()
        return low.count(nd) - low_in.count(nd)
    # b48 round 3 (WARDEN-SPLIT): svc_testhub_master stays dead-inert (dropped), svc_testhub_return
    # is now RETIRED here (its single trigger is replaced by the 5 per-area triggers), and each of
    # the 5 distinct per-area records gains exactly one 2-port trigger.
    if _delta(TESTHUB_MASTER_NPC) != 0:
        raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: svc_testhub_master must NOT be '
                         f'referenced (b48: dead 7-port master dropped)')
    if _delta(TESTHUB_RETURN_NPC) != 0:
        raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: svc_testhub_return must NOT be '
                         f'referenced (b48 round 3: retired; warden-split into per-area records)')
    for npc in TESTHUB_AREA_RETURN_NPCS:
        dests = TESTHUB_RETURN_DESTS_BY_NPC.get(npc, TESTHUB_RETURN_DESTS)
        if _delta(npc) != len(dests):
            raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: per-area return {npc} reference count '
                             f'must increase by exactly {len(dests)} '
                             f'(got {_delta(npc)})')
    from collections import Counter
    want = Counter()
    for npc in TESTHUB_AREA_RETURN_NPCS:
        dests = TESTHUB_RETURN_DESTS_BY_NPC.get(npc, TESTHUB_RETURN_DESTS)
        for _xyz, tag in dests:
            want[tag] += 1
    for tag, n in want.items():
        if _delta(tag) != n:
            raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: destination tag {tag} '
                             f'reference count must increase by exactly {n} '
                             f'(got {_delta(tag)})')
    return out


# ── HELOS TRAVELER HUB v2 (2026-07-13, Will) : per-area boat-dialog travel triggers ──────────
# Will v1: "put teleport guys in helos, one person each." Will v2 (this pass): (i) "instead of
# teleporting me to the final destination area, teleport me next to the NPC/door you would talk
# to/use in game to travel there, so I test those guys AND know where everything is at"; (ii) "add
# travelers to all other new fixed-place bosses, at the AREA ENTRANCE amid regular mobs (not the
# boss horde)." So each landing below = the NATURAL IN-GAME APPROACH POINT, NOT the interior/boss.
# ONE Condition_OnLevelLoad trigger per traveler NPC (25 = 14 outbound + 11 area returns), each
# with a SINGLE Action_BoatDialog, all appended to the always-loaded sv_commonmechanics refire
# step (registry law: no new QUESTS registration). Mirrors _add_helos_portal_travel exactly. Keys
# ONLY on the DISTINCT svc_helos_trav_* / svc_area_return_* records (never Almyros/portal_master_
# helos) - each record placed exactly once map-side (WARDEN LAW). Records ship in the arz
# (apply_svc_patches _create_helos_traveler_hub); INERT on canonical (the canonical map places
# NONE of these NPCs -> the boat-dialog has no entity to bind, a no-op). Landing coords = SIGNED-
# INT world (grid_corner + level-local), ALL surveyed ON-MESH in the main walkable component vs
# the built TESTHUB map (tools/debug/survey_hub_v2_landings.py, 2026-07-13). Returns land at the
# Helos plaza spot (same as TESTHUB_RETURN_DESTS).
_HHUB = r'records\quests'
HELOS_HUB_TRAVEL = [
    # (npc record, (world x, y, z), boat-menu label tag)  -- OUTBOUND (all placed in Helos)
    # KEEP: Garden/Secret/BossArena already land at their natural approach (merchant hub w/ rift +
    # return NPC / forest-cluster entry / arena forecourt 90u off the boss volume) - no boss to
    # move away from.
    (_HHUB + r'\svc_helos_trav_garden.dbr',     (1173, -39, -4001),  'tagSVCHelosToGarden'),
    (_HHUB + r'\svc_helos_trav_secret.dbr',     (-2396,   2, -5790), 'tagSVCHelosToSecret'),
    # RETARGET (v2): land at the in-game DOOR / entrance / travel-settlement, amid regular mobs.
    (_HHUB + r'\svc_helos_trav_sparta.dbr',     (-6587,   1, -3180), 'tagSVCHelosToSparta'),      # Sparta-Crypt DOOR: deepest Athens catacomb (catacube02_floorlast stairs-down), amid beastmen. b44 NUDGE: was (-6588,-3180), collided AG_Beastmen_Gorgon_02N @2.72u -> now 3.69u clr 100%
    (_HHUB + r'\svc_helos_trav_uber.dbr',       (-7793,   1, -3793), 'tagSVCHelosToUber'),        # Knossos->Uber DOOR: Minotaur secret door (maze03), amid the labyrinth
    (_HHUB + r'\svc_helos_trav_bossarena.dbr',  (-429,   27, -3538), 'tagSVCTestHubToBossArena'),  # b43-r2: ON the arena dais comp#2 (was (-433,0,-3602) comp#1, unreachable from the fight)
    (_HHUB + r'\svc_helos_trav_warband.dbr',    (5699,    1,  3315), 'tagSVCHelosToWarband'),     # blood-cave connection chamber, at the regular demon pack (~35u off the Enslaver horde)
    (_HHUB + r'\svc_helos_trav_dorus.dbr',      (428,     1, -8113), 'tagSVCHelosToDorus'),       # b47 RELOCATE: Tomb03 (Tomb of the Queens) landing ~8u NW of Kroisos (436,-8117); was tomb01 entrance
    (_HHUB + r'\svc_helos_trav_tantalus.dbr',   (-346,  -12, -10131),'tagSVCHelosToTantalus'),    # Styx swamp stairs ENTRANCE, amid anouran (~36u off Tantalus)
    (_HHUB + r'\svc_helos_trav_charon.dbr',     (-480,  -12, -9591), 'tagSVCHelosToCharon'),      # Styx river Hades-CITY (boatman + storyteller + rift shrine), then walk E to the Golden Bough
    (_HHUB + r'\svc_helos_trav_mnemophage.dbr', (169,   -10, -11418),'tagSVCHelosToMnemophage'),  # Mnemosyne cave stairs-up ENTRANCE (~20u off the boss glyph ring)
    (_HHUB + r'\svc_helos_trav_ephialtes.dbr',  (-1756,   3, -13198),'tagSVCHelosToEphialtes'),   # Dread Halls stairs-up ENTRANCE (~130u off the deep-SW boss vault)
    # NEW (v2 order-ii): map-placed bosses the original 11 did not cover. Land at the area entrance
    # amid regular mobs; walk to the boss.
    (_HHUB + r'\svc_helos_trav_devourer.dbr',   (5349,    1,  3009), 'tagSVCHelosToDevourer'),    # drxbc2 blood-cave chamber, amid demon/hound packs (~92u off Toxeus the Devourer's egg-pack corner). b44 NUDGE: was (5345,3010), collided burstvessle_01 @0.58u DEADLY -> now 3.16u clr 100%
    (_HHUB + r'\svc_helos_trav_vashkarr.dbr',   (-227,    1,  146),  'tagSVCHelosToVashkarr'),    # random05a Chang'an cave N end (~28u off Vashkarr)
    (_HHUB + r'\svc_helos_trav_obsidian.dbr',   (-1827, -74,  -462), 'tagSVCHelosToObsidian'),    # tombobs02 Obsidian Halls stairs-down entrance (covers 4 roulette wardens + the broodmother nest)
    # RETURNS (each placed once inside its area; all travel back to the Helos plaza)
    (_HHUB + r'\svc_area_return_dorus.dbr',      (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    (_HHUB + r'\svc_area_return_tantalus.dbr',   (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    (_HHUB + r'\svc_area_return_charon.dbr',     (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    (_HHUB + r'\svc_area_return_mnemophage.dbr', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    (_HHUB + r'\svc_area_return_ephialtes.dbr',  (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    (_HHUB + r'\svc_area_return_warband.dbr',    (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    (_HHUB + r'\svc_area_return_uber.dbr',       (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    (_HHUB + r'\svc_area_return_sparta.dbr',     (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    (_HHUB + r'\svc_area_return_devourer.dbr',   (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    (_HHUB + r'\svc_area_return_vashkarr.dbr',   (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    (_HHUB + r'\svc_area_return_obsidian.dbr',   (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
]


def _add_helos_traveler_hub_travel(data: bytes) -> bytes:
    """Append one Condition_OnLevelLoad boat-dialog trigger per Helos-hub NPC (17: 11 outbound +
    6 returns) to the sv_commonmechanics refire step. Strictly additive (the step's trigger max is
    bumped by len(HELOS_HUB_TRAVEL)). Fails loud if the host step is missing, the bytes do not
    round-trip, or the reference-count deltas do not land exactly (one per distinct NPC record;
    per-tag Counter deltas)."""
    def field_val(items, key):
        for it in items:
            if it[0] == 'field' and it[1] == key:
                return it[2][1]
        return None

    def _trigger(display, npc, xyz, tag):
        x, y, z = xyz
        header = ('block', [
            ('field', 'displayTag', ('str', display)),
            ('field', 'displayBitmap', ('int_or_empty', 0)),
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'isActive', ('int', 0)),
        ])
        conditions = ('block', [
            ('field', 'conditionCount', ('int', 1)),
            ('field', 'conditionClassName', ('str', 'Condition_OnLevelLoad')),
            ('block', [
                ('field', 'comments', ('int_or_empty', 0)),
                ('field', 'isNot', ('int', 0)),
                ('field', 'isResettable', ('int', 1)),
                ('field', 'isQuestCritical', ('int', 1)),
            ]),
        ])
        actions = ('block', [
            ('field', 'actionCount', ('int', 1)),
            ('field', 'actionClassName', ('str', 'Action_BoatDialog')),
            ('block', [
                ('field', 'comments', ('int_or_empty', 0)),
                ('field', 'delayTime', ('int', 0)),
                ('field', 'npc', ('str', npc)),
                ('field', 'onOff', ('int', 1)),
                ('field', 'x', ('int', x & 0xFFFFFFFF)),
                ('field', 'y', ('int', y & 0xFFFFFFFF)),
                ('field', 'z', ('int', z & 0xFFFFFFFF)),
                ('field', 'tag', ('str', tag)),
            ]),
        ])
        return [header, conditions, actions]

    tree = qst_format.parse(data)
    steps_container = tree[1]
    positions = [i for i, it in enumerate(steps_container) if it[0] == 'block']
    step_triples = [positions[i:i + 3] for i in range(0, len(positions), 3)]

    patched = 0
    for stepdef_pos, trigcont_pos, _sentinel_pos in step_triples:
        stepdef = steps_container[stepdef_pos][1]
        if field_val(stepdef, 'name') != HELOS_PORTAL_HOST_STEP:
            continue
        trigcont = list(steps_container[trigcont_pos][1])
        bumped = False
        for idx, it in enumerate(trigcont):
            if it[0] == 'field' and it[1] == 'max':
                trigcont[idx] = ('field', 'max', ('int', it[2][1] + len(HELOS_HUB_TRAVEL)))
                bumped = True
                break
        if not bumped:
            raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: host step has no trigger max')
        for i, (npc, xyz, tag) in enumerate(HELOS_HUB_TRAVEL):
            trigcont.extend(_trigger(f'SVC: Helos Traveler Hub {i:02d}', npc, xyz, tag))
        steps_container[trigcont_pos] = ('block', trigcont)
        patched += 1

    if patched != 1:
        raise ValueError(
            f'{HELOS_PORTAL_HOST_QUEST}: Helos hub expected to patch exactly 1 step '
            f'({HELOS_PORTAL_HOST_STEP!r}), patched {patched}. Upstream changed; review.')

    out = qst_format.serialize(tree)
    if qst_format.serialize(qst_format.parse(out)) != out:
        raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: Helos-hub-patched quest does not '
                         f'round-trip stably')
    low = out.replace(b'/', b'\\').lower()
    low_in = data.replace(b'/', b'\\').lower()

    def _delta(needle):
        nd = needle.replace('/', '\\').lower().encode()
        return low.count(nd) - low_in.count(nd)
    from collections import Counter
    npc_want = Counter(npc for npc, _xyz, _tag in HELOS_HUB_TRAVEL)
    for npc, n in npc_want.items():
        if _delta(npc) != n:
            raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: hub NPC {npc} reference count must '
                             f'increase by exactly {n} (got {_delta(npc)})')
    tag_want = Counter(tag for _npc, _xyz, tag in HELOS_HUB_TRAVEL)
    for tag, n in tag_want.items():
        if _delta(tag) != n:
            raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: hub label tag {tag} reference count '
                             f'must increase by exactly {n} (got {_delta(tag)})')
    return out


# ── TRAVELERS-INTO-AREAS b62 (Will 2026-07-14 final, item 1): ENTER-OFFERS ────────────────────
# The in-world traveler standing NEAR a sealed SV area also offers to take the player INTO it.
# Ground-truthed (docs/reports/travelers_into_areas_sweep.md): of every in-world return NPC, only
# TWO gate a truly SEALED separate deep area with an EXISTING placed NPC on both the outer AND
# inner end - spartacryptlevel2 (outer: svc_area_return_sparta @ CataCube02_FloorLast; inner:
# svc_testhub_return_sparta) and crypt_floor1/Uber Dungeon (outer: svc_area_return_uber @ Maze03;
# inner: svc_testhub_return_uber). Each outer NPC gets ONE extra Condition_OnLevelLoad trigger
# (its own boat menu ALREADY carries the Helos-return route via HELOS_HUB_TRAVEL above; "multiple
# triggers on one NPC accumulate boat-menu ports" is the same proven mechanism Almyros's dormant
# 4-port menu and every multi-dest hub NPC already rely on). Landings verified on-mesh +
# collision-clear (tools/debug/gate_landing_clearance.py PASS): enter_sparta_crypt is a 2u NUDGE
# off Almyros's dormant (-5602,-2,-1409) landing (2.38u from a sarcophagus there) to a clean spot
# still 3.16u from the existing svc_testhub_return_sparta; enter_uber_dungeon reuses Almyros's
# dormant (-2438,10,-2450) unchanged (clean, 3.00u off svc_testhub_return_uber).
#
# The Secret Place's murderbossroom (the sweep's third sealed area) is NOT wired here - it has NO
# placed NPC on either end (box-adjacency-proven isolated from the rest of the Secret_Place
# cluster), so an enter-offer without a paired return would strand the player with no way back
# (the P0-A "no way back" class of bug). It needs a new map-lane NPC placement first; flagged as a
# BACKLOG follow-up.
TRAVELER_ENTER_OFFERS = [
    (r'records\quests\svc_area_return_sparta.dbr', (-5596, -2, -1410), 'tagSVCEnterSpartaCrypt'),
    (r'records\quests\svc_area_return_uber.dbr',   (-2438, 10, -2450), 'tagSVCEnterUberDungeon'),
]


def _add_traveler_enter_offers(data: bytes) -> bytes:
    """Append one extra Condition_OnLevelLoad boat-dialog trigger per TRAVELER_ENTER_OFFERS entry
    to the sv_commonmechanics refire step (strictly additive: bumps the step's trigger max by
    len(TRAVELER_ENTER_OFFERS)). Mirrors _add_helos_traveler_hub_travel exactly. Fails loud if the
    host step is missing, the bytes do not round-trip, or the reference-count deltas do not land
    exactly (both NPCs already carry a route from HELOS_HUB_TRAVEL, so their reference count rises
    by 1 more here, not from 0)."""
    def field_val(items, key):
        for it in items:
            if it[0] == 'field' and it[1] == key:
                return it[2][1]
        return None

    def _trigger(display, npc, xyz, tag):
        x, y, z = xyz
        header = ('block', [
            ('field', 'displayTag', ('str', display)),
            ('field', 'displayBitmap', ('int_or_empty', 0)),
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'isActive', ('int', 0)),
        ])
        conditions = ('block', [
            ('field', 'conditionCount', ('int', 1)),
            ('field', 'conditionClassName', ('str', 'Condition_OnLevelLoad')),
            ('block', [
                ('field', 'comments', ('int_or_empty', 0)),
                ('field', 'isNot', ('int', 0)),
                ('field', 'isResettable', ('int', 1)),
                ('field', 'isQuestCritical', ('int', 1)),
            ]),
        ])
        actions = ('block', [
            ('field', 'actionCount', ('int', 1)),
            ('field', 'actionClassName', ('str', 'Action_BoatDialog')),
            ('block', [
                ('field', 'comments', ('int_or_empty', 0)),
                ('field', 'delayTime', ('int', 0)),
                ('field', 'npc', ('str', npc)),
                ('field', 'onOff', ('int', 1)),
                ('field', 'x', ('int', x & 0xFFFFFFFF)),
                ('field', 'y', ('int', y & 0xFFFFFFFF)),
                ('field', 'z', ('int', z & 0xFFFFFFFF)),
                ('field', 'tag', ('str', tag)),
            ]),
        ])
        return [header, conditions, actions]

    tree = qst_format.parse(data)
    steps_container = tree[1]
    positions = [i for i, it in enumerate(steps_container) if it[0] == 'block']
    step_triples = [positions[i:i + 3] for i in range(0, len(positions), 3)]

    patched = 0
    for stepdef_pos, trigcont_pos, _sentinel_pos in step_triples:
        stepdef = steps_container[stepdef_pos][1]
        if field_val(stepdef, 'name') != HELOS_PORTAL_HOST_STEP:
            continue
        trigcont = list(steps_container[trigcont_pos][1])
        bumped = False
        for idx, it in enumerate(trigcont):
            if it[0] == 'field' and it[1] == 'max':
                trigcont[idx] = ('field', 'max', ('int', it[2][1] + len(TRAVELER_ENTER_OFFERS)))
                bumped = True
                break
        if not bumped:
            raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: host step has no trigger max')
        for i, (npc, xyz, tag) in enumerate(TRAVELER_ENTER_OFFERS):
            trigcont.extend(_trigger(f'SVC: Traveler Enter-Offer {i:02d}', npc, xyz, tag))
        steps_container[trigcont_pos] = ('block', trigcont)
        patched += 1

    if patched != 1:
        raise ValueError(
            f'{HELOS_PORTAL_HOST_QUEST}: enter-offers expected to patch exactly 1 step '
            f'({HELOS_PORTAL_HOST_STEP!r}), patched {patched}. Upstream changed; review.')

    out = qst_format.serialize(tree)
    if qst_format.serialize(qst_format.parse(out)) != out:
        raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: enter-offer-patched quest does not '
                         f'round-trip stably')
    low = out.replace(b'/', b'\\').lower()
    low_in = data.replace(b'/', b'\\').lower()

    def _delta(needle):
        nd = needle.replace('/', '\\').lower().encode()
        return low.count(nd) - low_in.count(nd)
    from collections import Counter
    npc_want = Counter(npc for npc, _xyz, _tag in TRAVELER_ENTER_OFFERS)
    for npc, n in npc_want.items():
        if _delta(npc) != n:
            raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: enter-offer NPC {npc} reference count '
                             f'must increase by exactly {n} (got {_delta(npc)})')
    tag_want = Counter(tag for _npc, _xyz, tag in TRAVELER_ENTER_OFFERS)
    for tag, n in tag_want.items():
        if _delta(tag) != n:
            raise ValueError(f'{HELOS_PORTAL_HOST_QUEST}: enter-offer label tag {tag} reference '
                             f'count must increase by exactly {n} (got {_delta(tag)})')
    return out


# ── Q4 (build31, dead-content audit Lane D): surgical quest-ref fixes ────────
# All three are string-value edits inside otherwise byte-faithful quests; each
# helper walks the parse tree, replaces exactly the expected count of values,
# and asserts a stable round-trip. See docs/DEAD_CONTENT_AUDIT_2026-07-10.md.

def _replace_field_values(data: bytes, quest_label: str, field_name: str,
                          wanted_old, new_value: str, expect: int) -> bytes:
    """Replace the value of every ('field', field_name) whose normalized value
    is in wanted_old (a set of normalized paths) with new_value (written in
    the file's own separator style). Fails loud unless exactly `expect`
    replacements happen and the output round-trips stably."""
    def norm(s):
        return s.replace('/', '\\').lower()

    wanted = {norm(w) for w in wanted_old}
    tree = qst_format.parse(data)
    replaced = 0

    def walk(items):
        nonlocal replaced
        for i, it in enumerate(items):
            if isinstance(it, list):
                walk(it)
            elif isinstance(it, tuple) and it[0] == 'block':
                walk(it[1])
            elif isinstance(it, tuple) and it[0] == 'field' \
                    and it[1] == field_name \
                    and isinstance(it[2][1], str) and norm(it[2][1]) in wanted:
                style_fwd = '/' in it[2][1]
                nv = new_value.replace('\\', '/') if style_fwd \
                    else new_value.replace('/', '\\')
                items[i] = ('field', field_name, (it[2][0], nv))
                replaced += 1
    walk(tree if isinstance(tree, list) else [tree])
    if replaced != expect:
        raise ValueError(f'{quest_label}: expected exactly {expect} '
                         f'{field_name} replacement(s), made {replaced}')
    out = qst_format.serialize(tree)
    if qst_format.serialize(qst_format.parse(out)) != out:
        raise ValueError(f'{quest_label}: patched quest does not round-trip')
    return out


def _fix_bossarena_entervolume(data: bytes) -> bytes:
    """Q4-1: bossarena.qst STEP 1 waits on EnterVolume(portal_olympianarena)
    which is placed NOWHERE; the volume actually placed in boss_arena.lvl is
    volume_startolympianarena (SV-inherited authoring bug, byte-verified
    against upstream). One-line retarget makes the Satyr Shaman arena boss
    spawn."""
    return _replace_field_values(
        data, 'bossarena.qst', 'volumeRecord',
        {r'records\quests\portal_olympianarena.dbr'},
        r'records\quests\volume_startolympianarena.dbr', expect=1)


def _fix_widowletter_chest_branch(data: bytes) -> bytes:
    """Q4-2: the honor/dishonor branch spawns chest_goldenchest_normal_03 but
    its three 'Block Chest' UseFixedItem conditions watch the per-difficulty
    goldenchest_01/02/03 variants that are never spawned -> the moral-choice
    branch never fires. Align the watched records to the spawned chest."""
    return _replace_field_values(
        data, 'widowletter.qst', 'itemRecord',
        {r'records\drxmap\quest\goldenchest_01_normal.dbr',
         r'records\drxmap\quest\goldenchest_02_epic.dbr',
         r'records\drxmap\quest\goldenchest_03_legendary.dbr'},
        r'records\drxmap\quest\chest_goldenchest_normal_03.dbr', expect=3)


CHESTSWAP_QUEST = 'quest that controls boss chest swap.qst'


def _fix_chimera_chest_typo(data: bytes) -> bytes:
    """Q4-3 (coordinated with fix_chimera_chest_double_ext in
    build_svc_database.py, which renames the arz records in the same wave):
    the chest-swap controller's UseFixedItem watches the double-extension
    bosschest13_chimera_epic.dbr.dbr; retarget to the renamed single-.dbr."""
    return _replace_field_values(
        data, CHESTSWAP_QUEST, 'itemRecord',
        {r'records\item\containers\boss\bosschest13_chimera_epic.dbr.dbr'},
        r'records\item\containers\boss\bosschest13_chimera_epic.dbr', expect=1)


def _add_typhon_rhodes_unlock(data: bytes) -> bytes:
    """Append the Rhodes-portal unlock trigger to the Typhon repeat-loot step.

    Strictly additive (one trigger triple; the step's trigger-container max is
    incremented). Fails loud if the host step is missing, if the emitted bytes
    do not round-trip, or if the addition is not exactly one unlock action.

    ── FIDELITY DECISION: **KEEP** (2026-07-28, `fix/debt-docs`; owner of the
    asserts below). ────────────────────────────────────────────────────────────
    This trigger is the ONLY non-SVAERA-faithful edit in our Quests.arc, and it
    is INERT on its own: Q1 shipped as build30.3 and FAILED in-game (Will killed
    Typhon, the unlock event fired, no portal), because the base game opens
    `xq00_olympus_portaltorhodes` from ENGINE CODE (an end-of-campaign event that
    never fires in Custom Quest) and no quest in SVAERA OR the base game
    references that portal at all. The Q3 quests-lane archive
    (docs/BACKLOG.md, 2026-07-09) therefore RECOMMENDED reverting this function
    for pure SVAERA fidelity - and then parked the call as "DECISION DEFERRED to
    coordinator". It has ridden every Quests build since, undecided.

    The decision is now made and it is KEEP, for four reasons:
      1. It is a byte-SUPERSET, not a mutation. The only file it touches is the
         already-in-arc, already-registered, never-completing controller
         'quest that controls bosses and their doors.qst'; every SVAERA behaviour
         in that file is preserved verbatim (the Q3 byte analysis found this to
         be the single file that differs from SVAERA, by +804 B of pure append).
      2. Q3's kill-gated instant unlock (`_add_olympus_rhodes_travel`) builds on
         the SAME host step and the SAME `Action_UnlockFixedItem` on the SAME
         portal record. Reverting Q1 would not restore SVAERA fidelity - Q3
         would still be there - it would only delete the token+OnLevelLoad
         RELOAD path, which is what gives an EXISTING Typhon-slayer (Will's main)
         the portal without re-killing the boss. Strictly less capability.
      3. It is harmless when it does nothing. `canReFire=1` + `OnLevelLoad` makes
         it idempotent and retroactive; an unlock on an engine-locked fixed item
         is a no-op, which is exactly the observed build30.3 outcome.
      4. Reverting costs a Quests.arc rebuild + a coupled redeploy (Levels+Quests
         ship together) for zero player-visible benefit.

    OWNER OF THE SURVIVAL GATE: this decision. The `patched != 1` / round-trip /
    exactly-one-portal-reference / token-count asserts below exist to keep this
    append a byte-superset across upstream changes - they are not orphaned. If a
    future lane DOES revert this, it must delete the asserts with it and record
    the reversal in the ledger. Source: docs/BACKLOG.md "Q3 archive (2026-07-09
    day)" -> "Q1 unlock trigger recommendation".
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


def rebuild_sv_area_quests_only(quests_arc_path: Path, out_path: Path = None):
    """SURGICAL mode: re-derive ONLY the 4 SV area questlines into an EXISTING
    Quests.arc, leaving every other entry byte-identical.

    WHY THIS EXISTS (b94). `main()` restores a pristine
    `reference_mods\\SVAERA_customquest\\Resources\\Quests.arc` first because its
    Q1/Q2/Q3/testhub steps APPEND triggers to native SVAERA quests and are therefore
    not idempotent - re-running them over an already-built arc would double them. On
    a machine where the (gitignored) reference_mods checkout is absent, that restore
    is silently skipped and a full `main()` run would corrupt those native quests.

    The 4 SV area questlines have no such problem: each is re-derived from the
    UPSTREAM SV bytes and written with `add_file`/`set_file`, so re-deriving them is
    idempotent by construction. This entry point does exactly that and nothing else,
    which is also the right shape for a Quests-only wave (b94 PART C): the emitted
    arc differs from its input in EXACTLY the entries listed below, which is directly
    provable with an entry-by-entry blob diff.

    Returns (changed, unchanged) entry-name lists.
    """
    out_path = out_path or quests_arc_path
    arc = ArcArchive.from_file(quests_arc_path)
    before = {e.name: arc.get_file(e.name) for e in arc.entries}

    area_quests = _build_area_quests()
    for name, data in area_quests.items():
        arc.add_file(name, data)
    arc.write(out_path)

    arc2 = ArcArchive.from_file(out_path)
    after = {e.name: arc2.get_file(e.name) for e in arc2.entries}
    changed = sorted(n for n in set(before) | set(after)
                     if before.get(n) != after.get(n))
    unchanged = sorted(n for n in set(before) & set(after)
                       if before.get(n) == after.get(n))
    print(f'  SV-area-only rebuild: {len(changed)} entry/entries changed, '
          f'{len(unchanged)} byte-identical')
    for n in changed:
        print(f'    CHANGED  {n}  ({len(before.get(n) or b"")} -> '
              f'{len(after.get(n) or b"")} bytes)')
    for name, data in area_quests.items():
        back = arc2.get_file(name)
        if back != data:
            raise SystemExit(f'{name} did not round-trip through Quests.arc')
    _assert_quest_records_loadable(arc2)
    return changed, unchanged


def promote_leinth_exit_in_arc(quests_arc_path: Path, out_path: Path = None):
    """SURGICAL mode (b94 PART C): apply _promote_leinth_exit_fallbacks to the
    open_bloodcave_portal.qst entry ALREADY inside an existing Quests.arc.

    WHY A SECOND SURGICAL MODE. rebuild_sv_area_quests_only() re-derives the SV area
    quests from the UPSTREAM SV archive; on a machine where the (gitignored)
    `upstream/soulvizier_098i/Resources/XPack/Quests.arc` extraction is absent that is
    impossible. The shipped entry, however, is by construction exactly
    `_harden_guardian_door_unlocks(_neutralize_bloodcave_entry_step(<upstream bytes>))`
    - the input the promotion step expects - so applying the promotion to the shipped
    entry produces byte-for-byte what a full pipeline run produces. The promotion also
    asserts that shape (primary proxy trigger + exactly 3 Leinth kill fallbacks + the
    4-action set) and refuses otherwise, so it cannot be applied to the wrong bytes.

    IDEMPOTENT: re-running replaces each fallback's action block with the same copy of
    the primary's and finds isResettable already 1, so a second run is a no-op.

    Returns (changed, unchanged) entry-name lists.
    """
    out_path = out_path or quests_arc_path
    arc = ArcArchive.from_file(quests_arc_path)
    before = {e.name: arc.get_file(e.name) for e in arc.entries}

    target = None
    for e in arc.entries:
        if e.name.lower().endswith(BLOODCAVE_INTERIOR_QUEST):
            target = e.name
            break
    if target is None:
        raise SystemExit(f'{BLOODCAVE_INTERIOR_QUEST} is not in {quests_arc_path}; '
                         f'the blood-cave questline must be ported first.')
    src = arc.get_file(target)
    _assert_roundtrip(target, src)
    # b94 ROUND 3: the surgical path applies the SAME two-step chain the full build
    # does, so a hand-patched Quests.arc can never drift from a built one.
    arc.set_file(target, _add_leinth_exit_nokill_fallback(
        _promote_leinth_exit_fallbacks(src)))
    arc.write(out_path)

    arc2 = ArcArchive.from_file(out_path)
    after = {e.name: arc2.get_file(e.name) for e in arc2.entries}
    changed = sorted(n for n in set(before) | set(after)
                     if before.get(n) != after.get(n))
    unchanged = sorted(n for n in set(before) & set(after)
                       if before.get(n) == after.get(n))
    # EXACTLY the blood-cave entry may move. `[]` is the idempotent re-run (the arc was
    # already promoted, so the same bytes came back out); anything else is a leak.
    if changed not in ([target], []):
        raise SystemExit(
            f'exit-portal fix: {len(changed)} entry/entries changed {changed}, '
            f'expected EXACTLY [{target!r}] (or [] on an already-promoted arc) - a '
            f'Quests-only wave must not disturb any other quest.')
    print(f'  Leinth-exit promotion: {len(changed)} entry changed ({target}: '
          f'{len(before[target])} -> {len(after[target])} bytes'
          f'{" - IDEMPOTENT no-op, already promoted" if not changed else ""}), '
          f'{len(unchanged)} entries byte-identical')
    _assert_quest_records_loadable(arc2)
    return changed, unchanged


def main():
    # SURGICAL mode (b94 PART C): --promote-leinth-exit <in.arc> [out.arc]
    if '--promote-leinth-exit' in sys.argv:
        i = sys.argv.index('--promote-leinth-exit')
        rest = sys.argv[i + 1:]
        if not rest:
            raise SystemExit('usage: build_quest_files.py --promote-leinth-exit '
                             '<in.arc> [out.arc]')
        src = Path(rest[0])
        dst = Path(rest[1]) if len(rest) > 1 else src
        promote_leinth_exit_in_arc(src, dst)
        return

    # SURGICAL mode (b94): --sv-areas-only <in.arc> [out.arc] re-derives ONLY the 4 SV
    # area questlines into an existing arc. See rebuild_sv_area_quests_only.
    if '--sv-areas-only' in sys.argv:
        i = sys.argv.index('--sv-areas-only')
        rest = sys.argv[i + 1:]
        if not rest:
            raise SystemExit('usage: build_quest_files.py --sv-areas-only <in.arc> [out.arc]')
        src = Path(rest[0])
        dst = Path(rest[1]) if len(rest) > 1 else src
        rebuild_sv_area_quests_only(src, dst)
        return

    # Start from SVAERA's original Quests.arc (clean)
    svaera_quests = Path(r'reference_mods\SVAERA_customquest\Resources\Quests.arc')
    quests_arc_path = Path(r'work\SoulvizierClassic\Resources\Quests.arc')

    import shutil
    if svaera_quests.exists():
        shutil.copy2(svaera_quests, quests_arc_path)
        print(f'Restored clean Quests.arc from SVAERA ({quests_arc_path.stat().st_size / 1024:.1f} KB)')
    else:
        # FAIL LOUD: without the pristine base the Q1/Q2/Q3/testhub APPEND steps below
        # would double-append onto an already-built arc (they are not idempotent).
        raise SystemExit(
            f'build_quest_files: the pristine SVAERA base {svaera_quests} is MISSING. '
            f'A full rebuild would double-append the Q1/Q2/Q3/testhub triggers onto an '
            f'already-built Quests.arc. Run scripts/sync_reference_mods.ps1 first, or '
            f'use --sv-areas-only <arc> for a Quests-only SV-area wave.')

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

    # Q2 (Group A): Helos portal-master 4-destination boat-dialog appended to
    # the always-loaded sv_commonmechanics refire step (registry law: no new
    # registration). PORTALS is empty (blood-cave walk-in), so this quest is the
    # clean SVAERA original here; if PORTALS is ever restored it replaces this
    # quest and the loud step-not-found failure is the correct signal to review.
    raw_cm = arc.get_file(HELOS_PORTAL_HOST_QUEST)
    if raw_cm is None:
        raise SystemExit(f'Q2: host quest missing: {HELOS_PORTAL_HOST_QUEST}')
    patched_cm = _add_helos_portal_travel(raw_cm)
    # Portal rig (GROUP 2 unblock): TESTHUB Model C hub + return boat-dialog
    # triggers, chained onto the just-patched quest (same refire step). Keyed on
    # the DISTINCT rig NPC records only; INERT on canonical (no rig NPC placed).
    patched_cm = _add_testhub_portal_travel(patched_cm)
    # Helos traveler hub v2 (Will 2026-07-13): 25 per-area boat-dialog triggers (14 outbound + 11
    # returns), chained onto the same refire step. Keyed on the DISTINCT svc_helos_trav_* /
    # svc_area_return_* records only; INERT on canonical (no hub NPC placed there).
    patched_cm = _add_helos_traveler_hub_travel(patched_cm)
    # TRAVELERS-INTO-AREAS b62 (Will 2026-07-14 final): 2 enter-offer triggers (Sparta Crypt +
    # Uber Dungeon), chained onto the same refire step. Keyed on the ALREADY-PLACED
    # svc_area_return_sparta / svc_area_return_uber only; INERT on canonical (neither is placed
    # there). The paired return-to-origin destinations are wired inside _add_testhub_portal_travel
    # above via TESTHUB_RETURN_DESTS_BY_NPC.
    patched_cm = _add_traveler_enter_offers(patched_cm)
    arc.set_file(HELOS_PORTAL_HOST_QUEST, patched_cm)
    print(f'Q2: Helos portal-master {len(HELOS_PORTAL_DESTS)}-destination '
          f'boat-dialog appended to {HELOS_PORTAL_HOST_QUEST} '
          f'({len(raw_cm)} -> {len(patched_cm)} bytes)')
    print(f'Helos traveler hub: {len(HELOS_HUB_TRAVEL)} per-area boat-dialog triggers '
          f'appended to {HELOS_PORTAL_HOST_QUEST}')
    print(f'Portal rig: TESTHUB hub ({len(TESTHUB_MASTER_DESTS)} ports) + return '
          f'({len(TESTHUB_RETURN_DESTS)} ports) boat-dialog appended to '
          f'{HELOS_PORTAL_HOST_QUEST}')
    print(f'Traveler enter-offers: {len(TRAVELER_ENTER_OFFERS)} enter-offer triggers appended to '
          f'{HELOS_PORTAL_HOST_QUEST} (Sparta Crypt + Uber Dungeon); return-to-origin wired via '
          f'TESTHUB_RETURN_DESTS_BY_NPC on svc_testhub_return_{{sparta,uber}}')

    # Q4-3: chimera chest double-extension retarget (arz records renamed by
    # fix_chimera_chest_double_ext in build_svc_database.py, same wave).
    raw_cs = arc.get_file(CHESTSWAP_QUEST)
    if raw_cs is None:
        raise SystemExit(f'Q4-3: host quest missing: {CHESTSWAP_QUEST}')
    patched_cs = _fix_chimera_chest_typo(raw_cs)
    arc.set_file(CHESTSWAP_QUEST, patched_cs)
    print(f'Q4-3: chimera chest .dbr.dbr retargeted in {CHESTSWAP_QUEST}')

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
