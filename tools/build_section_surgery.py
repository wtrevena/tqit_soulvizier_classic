#!/usr/bin/env python3
"""
Section-level surgery: inject drxmap objects into SVAERA levels.

Strategy: MERGE SV's drxmap object strings into SVAERA's 0x05 section (append only),
and extend SVAERA's 0x14 section with default entries for the new objects.
This keeps all existing objects and their per-object metadata (0x14) in sync.

Also appends 46 SV-only levels and patches DATA2 count.
"""
import sys, struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (
    parse_sections, parse_level_index, build_level_index,
    parse_quests, build_quests, parse_bitmap_index, build_bitmap_index,
    SEC_LEVELS, SEC_DATA, SEC_DATA2, SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_BITMAPS,
    MAP_MAGIC
)

svaera_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
sv_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
output_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')


def parse_blob_sections(blob):
    """Parse internal sections of a level blob."""
    sections = []
    if len(blob) < 4:
        return sections, b''
    magic = blob[:4]
    pos = 4
    while pos + 8 <= len(blob):
        st = struct.unpack_from('<I', blob, pos)[0]
        ss = struct.unpack_from('<I', blob, pos + 4)[0]
        if ss > len(blob) - pos - 8:
            break
        sections.append({'type': st, 'size': ss, 'data': blob[pos + 8:pos + 8 + ss]})
        pos += 8 + ss
    return sections, magic


def rebuild_blob(magic, sections):
    """Rebuild a level blob from magic + sections."""
    out = bytearray(magic)
    for s in sections:
        out += struct.pack('<II', s['type'], len(s['data']))
        out += s['data']
    return bytes(out)


def parse_0x05_strings(data):
    """Parse 0x05 section as flat list of length-prefixed DBR strings."""
    if len(data) < 4:
        return []
    count = struct.unpack_from('<I', data, 0)[0]
    strings = []
    pos = 4
    for _ in range(count):
        if pos + 4 > len(data):
            break
        slen = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        if pos + slen > len(data):
            break
        strings.append(data[pos:pos + slen])
        pos += slen
    return strings


def build_0x05_data(string_list):
    """Build 0x05 section data from list of raw byte strings."""
    buf = bytearray()
    buf += struct.pack('<I', len(string_list))
    for s in string_list:
        buf += struct.pack('<I', len(s))
        buf += s
    return bytes(buf)


def parse_0x14_records(data):
    """Parse 0x14 section as variable-length records: index(4) + size(4) + payload."""
    records = []
    pos = 0
    while pos + 8 <= len(data):
        idx = struct.unpack_from('<I', data, pos)[0]
        payload_size = struct.unpack_from('<I', data, pos + 4)[0]
        if pos + 8 + payload_size > len(data):
            break
        payload = data[pos + 8:pos + 8 + payload_size]
        records.append({'index': idx, 'payload_size': payload_size, 'payload': payload})
        pos += 8 + payload_size
    return records


def build_0x14_data(records):
    """Build 0x14 section data from record list."""
    buf = bytearray()
    for r in records:
        buf += struct.pack('<II', r['index'], r['payload_size'])
        buf += r['payload']
    return bytes(buf)


# Default 0x14 record payload (20 bytes): flags=2, 0, 1, 1, 0
DEFAULT_0x14_PAYLOAD = struct.pack('<IIIII', 2, 0, 1, 1, 0)


ENTRANCE_NPC_DBR = b'records\\quests\\portal_uberdungeon_entrance.dbr'
RETURN_NPC_DBR = b'records\\quests\\portal_uberdungeon_return.dbr'
BLOODCAVE_ENTRANCE_NPC_DBR = b'records\\quests\\portal_bloodcave_entrance.dbr'
BLOODCAVE_RETURN_NPC_DBR = b'records\\quests\\portal_bloodcave_return.dbr'

# --- Merge-dropped SV content restored via SV-faithful 0x05 re-injection ---------
# The map merge keeps SVAERA's copy of every shared level, which DROPPED all SV-added
# entities on those levels. These records + their exact SV-LOCAL coords are extracted
# byte-for-byte from the SV 0.98i upstream Levels.arc (RoadToTown03A / HiddenValley01 /
# HiddenValleyBorder04 0x05 sections); these shared levels are NOT grid-shifted (SV
# corner+GUID == SVAERA's, verified), so the SV-local coord is the correct local coord
# in the merged (SVAERA) blob. See docs/DROPPED_CONTENT_AUDIT.md sections 2.2 + 2.4 +
# 3 + 4 + WAVE A/E.
#
# INJECTION-SPEC FORMAT (SV-faithful, measured against SV 0.98i's own placements):
#   Each spec is (dbr_bytes, x, y, z) OR (dbr_bytes, x, y, z, opts) where opts is a dict:
#     'flags'    : the 0x05 record flags word (default 0). SV marks tracked/unique
#                  gameplay entities (respawn shrines) with flags=1.
#     'uniqueid' : 16 raw bytes written into the v0x11/v0e record's trailing UniqueId
#                  block (only present when flags != 0). MUST be the SV-original value
#                  for entities the map's GROUPS/quest systems bind BY UniqueId.
#     'wants_0x14': whether step-7 should append a default 0x14 metadata entry for this
#                  instance (default FALSE). Measured: NONE of the restored entities
#                  (shrine, wagon, widow trio) carries a 0x14 entry in SV, and SVAERA's
#                  own shared-level 0x14 sections are SPARSE (many flags=0 entities have
#                  none), so the SV-faithful default is to NOT add a 0x14 entry. 0x14 is
#                  per-instance engine binding metadata (e.g. cave-mouth GridEntrance
#                  GUID bindings), NOT a respawn/decoration requirement.
#
# THE REBIRTH-FOUNTAIN FIX (2026-07-06, measured, gate F1): build18 injected the shrine
# with flags=0 + a ZERO UniqueId + a spurious default 0x14 entry. But SV's HiddenValley01
# shrine record is flags=1 with UniqueId feeb4bc6ce4e08c0e279b3824244aeeb and NO 0x14
# entry, and the map's `Shrine_Respawn_Orient` GROUPS(0x11) record (RespawnShrine
# category, carried into the merge from SV's GROUPS) registers respawn shrines by their
# 16-byte UniqueId (that exact value is a member). With a zero UniqueId the shrine never
# matches the group, so the respawn system never binds it: it renders but does nothing
# ("visible but does not work"). Re-injecting it flags=1 + the SV UniqueId (verified
# collision-free: 0 other flagged records in the merged map use it) makes the group match
# and the shrine functional, structure-for-structure identical to SV.
# Widow Letter quest (widowletter.qst) placement-dependent triggers:
WIDOW_LING_NPC_DBR = b'records\\drxmap\\quest\\widow_ling.dbr'          # Condition_ConversationStart
TRG_FOUNDZHIDAN_DBR = b'records\\drxmap\\quest\\trg_foundzhidan.dbr'    # Condition_EnterVolume volume
LOCATION_TREASURECHEST_DBR = b'records\\drxmap\\quest\\location_treasurechest.dbr'
# Rebirth Fountain (respawn shrine at the blood-cave surface entrance):
RESPAWNTEMPLEORIENT01_DBR = b'records\\item\\shrines\\respawntempleorient01.dbr'
# SV 0.98i HiddenValley01 shrine UniqueId (byte-exact from its flagged 0x05 record).
# This is the value the `Shrine_Respawn_Orient` RespawnShrine group binds to.
RESPAWNTEMPLEORIENT01_UNIQUEID = bytes.fromhex('feeb4bc6ce4e08c0e279b3824244aeeb')
# The Hades merchant WAGON near the cave mouth (the "caravan" Will remembers). SV places
# it at HiddenValleyBorder04; the merge dropped it (absent in build17 AND build18). It is
# a plain Decoration (flags=0, no UniqueId, no 0x14 entry in SV).
#
# CARAVAN-IDENTITY EVIDENCE (2026-07-06, gate F2 + the round-2 vet challenge): Will reported
# "the caravan at/near the cave mouth / by the fountain is gone." Three independent measures
# prove that IS this wagon, not the GoM Super-Caravan `caravan_rhodes` (NpcCaravan):
#   (1) GEOGRAPHY: this wagon sits at HiddenValleyBorder04 corner (-134,-104,2302), one tile
#       from HiddenValley01 (-134,-120,2174) where the fountain is - literally the cave-mouth
#       border. `caravan_rhodes` lives in gardenofmerchants corner (1043,0,-4074), ~6200u away
#       behind a broken entrance the player cannot currently reach. "At the cave mouth" == the
#       wagon.
#   (2) WHAT DROPPED: this wagon was dropped by the merge (SVAERA swapped it for its own
#       `TravelingVendorShopOrient01` stall; absent in build17 AND build18). `caravan_rhodes`
#       was NEVER dropped (present in SV/build17/build18/merged) - so it cannot be the thing
#       Will saw "go."
#   (3) SCENE: in SV the wagon sits beside a Horse02 + Merchant_HiddenValley_General = a
#       caravan-with-driver scene at the cave mouth (the horse + merchant NPC are still present
#       in build18; only the distinctive wagon dropped, so the visible loss is exactly this
#       wagon). Restoring `caravan_rhodes` at HV01 would be a NON-SV-faithful invention (SV
#       never places it there) and is a separate WAVE-B item (fix the GoM warp), out of scope.
# rot: SV orients the wagon at ~141.5deg yaw (NOT identity); carry the exact SV float32 matrix
# so the record is byte-exact to SV and the wagon faces the way SV authored it (avoids the
# identity-facing clip risk the vet flagged).
MERCHANT_HADES_WAGON_DBR = b'records\\xpack\\sceneryhades\\structure\\merchant\\merchant_hades_merchantwagon01.dbr'
MERCHANT_HADES_WAGON_ROT = (-0.7823697328567505, 0.0, 0.6228142380714417,
                            0.0, 1.0, 0.0,
                            -0.6228142380714417, 0.0, -0.7823697328567505)
# SV orients widow_ling at ~-66deg yaw (NOT identity); carry the exact SV float32 matrix so
# the NPC faces the way SV authored it (was written identity in build18 - cosmetic, fixed here).
WIDOW_LING_ROT = (0.40753135085105896, 0.0, -0.9131911993026733,
                  0.0, 1.0, 0.0,
                  0.9131911993026733, 0.0, 0.40753135085105896)

# --- FUNCTIONAL Super-Caravan at the blood-cave cave mouth (BUG 1, repeat report) --------
# Will still sees no usable caravan on build21. The build19 restoration placed the SV Hades
# merchant WAGON (merchant_hades_merchantwagon01, Class=Decoration) at HiddenValleyBorder04
# - a DECORATIVE, non-interactive prop off at the valley border. Will means the FUNCTIONAL
# Super-Caravan (an NpcCaravan storage NPC he can USE) at the cave mouth. Diagnosis (parsed
# from the deployed build21 map, tools/debug/diag_bugs.py + hunt_npccaravan.py):
#   - the build19 wagon IS present in build21 (HiddenValleyBorder04 world (-97.8,-102.4,2328.5),
#     Class=Decoration) - but it is not a caravan the player can interact with;
#   - NO NpcCaravan exists anywhere near the cave mouth in build21;
#   - the base game places 43 native NpcCaravan storage NPCs, ALL flags=0, non-identity rot;
#     the Silk-Road-region one (records\xpack\creatures\npc\caravan\caravan_silkroad.dbr,
#     Class=NpcCaravan, GrkCaravan01.msh) is natively placed in BaseCampForest02.lvl (the
#     same Orient Silk Road region as HiddenValley01/the cave mouth) - the thematically
#     native, byte-shape-proven exemplar to mirror.
# So we place caravan_silkroad (a REAL, interactive Super-Caravan) at the HiddenValley01 cave
# mouth, ~6u from the working Rebirth Fountain (verified on-mesh: world (-78.7,-104.4,2188.9)
# = HV01-local (55.3,15.6,14.9) is 0.00u on the largest walkable component of HV01's real
# 238KB navmesh, tools/debug/probe_hv01_walk.py; 6.04u from the fountain, clear of it). The
# record byte-shape mirrors the native caravan_silkroad placement exactly: flags=0, NO
# UniqueId, NO 0x14 entry (HV01 is v0x11 -> the record is 72 bytes; every native NpcCaravan
# is flags=0). Rotation = caravan_silkroad's own SV-native facing (from BaseCampForest02's
# 0x05 bytes) so the injected record is byte-shape identical to a real working caravan.
# The border wagon is KEPT (it is SV-faithful cave-mouth dressing that SV itself placed at
# HiddenValleyBorder04; it does not conflict with the functional caravan ~150u away).
#
# DESIGN NOTE (conscious substitution, not a byte-faithful SV restore): SV 0.98i also ships
# `caravan_rhodes.dbr` (verified in the built arz: Class=NpcCaravan, mesh GrkCaravan01.msh -
# the SAME cart mesh as caravan_silkroad), reached in SV via a dedicated
# `Levels/World/Olympus/GardenofMerchants.lvl` merchant hub, NOT physically at the
# HiddenValley01 cave mouth. We deliberately place base-game `caravan_silkroad` directly at
# the cave mouth instead, because that matches Will's stated ask (a usable caravan AT the
# cave mouth) and avoids rebuilding SV's separate Garden-of-Merchants hub/portal path. Both
# resolve as Class=NpcCaravan (functionally identical Super-Caravan storage) and render the
# same cart. If strict SV fidelity is ever wanted, the faithful route is caravan_rhodes in a
# restored GardenofMerchants hub (a much larger, portal-based change). caravan_silkroad is
# also thematically native to the Orient Silk Road region that HiddenValley01 sits in.
CARAVAN_SILKROAD_DBR = b'records\\xpack\\creatures\\npc\\caravan\\caravan_silkroad.dbr'
# Every native v0x11 NpcCaravan carries a 12-byte 0x14 metadata entry with this exact
# payload (<III> 2,0,1) - surveyed 31/32 native NpcCaravan placements
# (tools/debug/survey_caravan_0x14.py). To byte-mirror a real working caravan, the
# injected record must carry the SAME 12-byte 0x14 entry (NOT the generic 20-byte default).
CARAVAN_SILKROAD_0x14 = struct.pack('<III', 2, 0, 1)  # 020000000000000001000000
# caravan_silkroad's EXACT float32 rotation from its native BaseCampForest02 0x05 record
# (yaw ~232deg), carried verbatim so the placed Super-Caravan's byte-shape matches the
# proven native NpcCaravan placement's rotation too.
CARAVAN_SILKROAD_ROT = (-0.6152916550636292, 0.0, 0.7882996201515198,
                        0.0, 1.0, 0.0,
                        -0.7882996201515198, 0.0, -0.6152916550636292)

# --- Static Widow Letter at the letterdrop spot (BUG 2, repeat report) -------------------
# Will still sees no widow letter on build21. finalletter is QUEST-SPAWNED
# (widowletter.qst Action_SpawnEntityAtLocation on OnLevelLoad) and the quest is never
# tracked for a character that predates it (docs/LETTER_SPAWN_DIAGNOSIS.md), so the spawn
# never fires for his _Toxeus. Robust, character-independent fix: place finalletter as a
# STATIC 0x05 world entity at the SAME spot the quest's location_letterdrop marker occupies
# in drxFirstxistion_connection, so the letter is physically present to pick up for ALL
# characters (existing, fresh, and his friend), no quest tracking required.
#   - Coord = location_letterdrop's SV-LOCAL position (32.459,10.005,17.593) -> world
#     (5691.5,1.0,3308.6). Re-verified ON the CURRENT build21 carved mesh: 0.10u from a
#     walkable cell, in the largest walkable component (tools/debug/probe_hv01_walk.py).
#     Placing it at the identical local coord as the QuestLocation means the static letter
#     and (for tracking chars, if the spawn ever ran) the quest letter would coincide.
#   - drxFirstxistion_connection is an SV-only v0x0e level -> the merge routes this through
#     inject_into_sv_only_blob -> inject_into_0x05 (56-byte record). finalletter is
#     ItemEquipment/Parchment (cannotPickUp=0), placed flags=0 like any ground item, NO
#     0x14 (SV-only 0x0e items carry none). DisplayAsQuestItem=0 (no quest glyph - a small
#     scroll to spot deliberately).
#   - DUPLICATE PREVENTION: the quest's own "Spawn Letter" action is NEUTRALIZED in
#     tools/build_quest_files.py (_neutralize_widowletter_spawn), so exactly ONE letter
#     (this static one) can ever exist per character. The quest's Condition_PickupItem
#     (finalletter) still fires on picking up the static letter (it keys on the item
#     RECORD, not provenance), granting SQWL_PickedUpLetter so the questline still advances
#     for characters that track it.
FINALLETTER_DBR = b'records\\drxmap\\quest\\finalletter.dbr'

# --- Hemorrheus (Blood Toxeus) superboss proxy (docs/BLOOD_TOXEUS_DESIGN.md sec 5) ------
# The DB side (commit aa14564) built the Proxy record + its ProxyPool (with the
# champion-add override) + the um_bloodtoxeus_99 monster, all resolving in the deployed
# SoulvizierClassic.arz. This places the PROXY ENTITY into the secret hallway past the mega
# chest, mirroring EXACTLY how SV places q_leinth_lone in bossfight.lvl.
#
# EXEMPLAR BYTE-SHAPE (measured from the SV 0.98i upstream Levels.arc, the actual merge
# donor - NOT the editor-normalized decompiled_sv copy, which is a different v0x11
# extraction). q_leinth_lone in bossfight.lvl (v0x0e) is a plain 0x05 instance:
#   flags = 0 (unflagged -> NO trailing UniqueId block; 56-byte v0x0e record)
#   NO 0x14 entry (bossfight's whole 0x14 section is EMPTY, size 0 in SV upstream)
#   rotation = a specific non-identity yaw (~91.94 deg), Leinth's own facing.
# So the faithful placement is a plain flags=0 record with NO 0x14 (identical shape to the
# widow/wagon SV-only injections above), carrying the exemplar's exact rotation matrix so
# the injected record is byte-shape-identical to q_leinth_lone (position + rot + flags).
# The Proxy visual (mesh/scale/texture) lives on the DB record; the real spawn is the
# um_bloodtoxeus_99 monster via the pool.
Q_BLOODTOXEUS_LONE_DBR = b'records\\drxmap\\proxy\\q_bloodtoxeus_lone.dbr'
# M5' (build30): the ~50%-spawn variant proxy for the parchment placement (chanceToRun=50).
# COUPLED WITH DB LANE: this record is created by the DB lane; until it lands in the shipped
# arz, the parchment placement below shows as a MAP-REF-1 (placed record absent from arz) and
# the map+arz must ship together. Same proxy dir as q_bloodtoxeus_lone.
# ⚠️ M15 (2026-07-09): BOTH standalone placements are RETIRED (specs removed from
# INJECT_SPECS) - Will's mechanism change joins Toxeus to the EXISTING chest-area
# egg_blooddragon_pack pool (100%, in-place edit, single placement) and a CLONE of the
# parchment demon_01_cluster pool (50%, DB lane clones; see the M15 notes at both former
# spec sites). The constants stay for history/greps; the records remain in the arz unplaced.
Q_BLOODTOXEUS_LONE_50_DBR = b'records\\drxmap\\proxy\\q_bloodtoxeus_lone_50.dbr'
# q_leinth_lone's EXACT float32 rotation (from its SV-upstream bossfight 0x05 record bytes);
# carried verbatim so the Hemorrheus proxy's byte-shape matches the exemplar's rotation too.
Q_LEINTH_EXEMPLAR_ROT = (-0.03390489146113396, 0.0, -0.9994250535964966,
                         0.0, 1.0, 0.0,
                         0.9994250535964966, 0.0, -0.03390489146113396)

# --- A1: maze03 -> Uber Dungeon (+ Boss Arena) entrance (portal_olympianarena1) ----------
# The SV-areas campaign SKIPPED this as "ungateable offline"; the accepted pattern now is to
# implement with every offline gate achievable and ship WALK-TEST-PENDING (like the blood
# cave). Full recon: docs/ENTRANCES_POLISH_LOG.md (recon_maze03.py / recon_portal_chain.py /
# place_maze03_portal.py).
#
# MECHANISM (ROUND-2 born-open, disasm-proven; supersedes the old quest-opened model):
# `records\quests\portal_olympianarena1.dbr` is now Class **GridEntrance** (the born-open static
# cave-mouth class), swapped from GridEntranceDynamic by apply_svc_patches
# _make_portals_born_open_gridentrance. A static GridEntrance is ALWAYS-OPEN + ALWAYS-VISIBLE at
# spawn with NO quest (like every base-game cave mouth) - it never runs the Dynamic activate that
# closed the portal, so it teleports for FRESH AND PRE-EXISTING characters with no bossarena.qst
# adoption dependency (docs/DYNGRID_GATE_RCA.md sec 5; wf_c0012e88-64a). The teleport still fires
# off the SAME 0x14 binding (GridEntrance::GetConnectedPortalId/RegionId read the same offsets);
# crypt_floor1's portal_olympianarena2 (GridExitOneWay, born-open) is the paired landing (on-mesh,
# Wave 1). The bossarena.qst Action_OpenDynGridEntrance is now a harmless no-op (the record is no
# longer a DynGrid). The ONLY format consequence: a static GridEntrance's 0x14 is 60 bytes (a
# 12-byte (2,0,1) prefix + the 48-byte binding below), so the ENTRANCE payload is prefixed at
# injection time in _normalize_spec (landings keep 48 bytes). The 48-byte binding itself is
# unchanged:
#
# THE 0x14 BINDING (SV maze03's exact 48-byte payload, byte-verified from the SV upstream
# Levels.arc, and PROVEN self-consistent in the merge):
#   [0:16]  mouth_uid  = 58941143e04eb3c0d62dbd952143f05d
#   [16:32] exit_uid   = 6e513e901549b1d558db968c61bda66a  (== crypt_floor1 portal_olympianarena2
#                          mouth_uid EXACTLY -> the GridEntrance<->GridExit pair is intact)
#   [32:48] dest_guid  = dbc245c358434e0bb54760b234293cc5  (== crypt_floor1's MERGED-WORLD GUID
#                          EXACTLY -> crypt keeps its GUID in the merge, so NO remap needed)
# crypt_floor1's landing 0x14 is byte-identical SV vs merged, so restoring these exact bytes
# reconnects both sides perfectly.
#
# PLACEMENT: SV placed the portal 0.3u from a Knossos SECRET-DOOR frame (doorframesecretos01)
# in a decorated alcove at SV maze's WEST entrance (SV-local ~101,144). AE TRIMMED that west
# alcove (SV-local X=101 -> AE world X=-7974, 104u WEST of AE mesh min X=-7870 = OFF-MESH). AE
# preserves the Minotaur boss room INCLUDING q07_minotaursecretosdoor (a secret door) @ AE-local
# (289,150). The faithful AE analogue = beside that secret door. Chosen on-mesh cell (openNbr
# 8/8, on AE's Editor-baked navmesh): AE-local (290.70,1.20,152.50) = world (-7785.3,1.2,
# -3790.5): 3.0u from the secret door (mirrors SV's ~0.3u), 16.7u from the Minotaur boss proxy
# (so not ON it), 15.0u from the boss chest. Reached after the Minotaur Lord fight (main Knossos
# quest) = a sensible late-Knossos gate for an end-game Uber Dungeon. flags=0, IDENTITY rotation
# (SV's portal record uses identity - byte-verified). AE Maze03 is v0x0f; the v0x0f 0x05 record
# is base-72 (byte-verified), handled by inject_into_0x05_v11 + the widened v0f guard in
# svaera_plus_portals.py step 6. maze03 has a 0x14 section (size 0) so the step-7 x14_payload
# append lands the binding at the injected instance index.
PORTAL_OLYMPIANARENA1_DBR = b'records\\quests\\portal_olympianarena1.dbr'
# M4 (build30): a persistent portal-swirl EffectEntity co-located with a GridEntrance to make
# the born-open static portal VISIBLE (static GridEntrance has NO fx field and its placeholder
# mesh renders as a flat, near-featureless pane - the base game's swirl comes from a Dynamic
# portal's open-animation FX we do not have). map_portal_aura ships: records\drxmap\effects\
# objefx\map_portal_aura.dbr + its DRXeffects\other\map_portal_aura.pfx are both present in the
# shipped arz + DRXeffects.arc (scratchpad/m4_impl_analysis.py). flags=0, no 0x14.
PORTAL_FX_MAP_AURA_DBR = b'records\\drxmap\\effects\\objefx\\map_portal_aura.dbr'
PORTAL_OLYMPIANARENA1_0x14 = bytes.fromhex(
    '58941143e04eb3c0d62dbd952143f05d'   # mouth_uid
    '6e513e901549b1d558db968c61bda66a'   # exit_uid  (pairs crypt_floor1 portal_olympianarena2)
    'dbc245c358434e0bb54760b234293cc5')  # dest_guid (== crypt_floor1 merged GUID)
assert len(PORTAL_OLYMPIANARENA1_0x14) == 48

# --- BORN-OPEN ENTRANCE 0x14 PREFIX (round 2 openness fix, wf_c0012e88-64a) --------------
# The DB half (apply_svc_patches _make_portals_born_open_gridentrance) swaps the ENTRANCE
# record portal_olympianarena1 from GridEntranceDynamic (self-closes at every spawn -> needs
# a quest to open) to the born-open STATIC GridEntrance (always-open + always-visible, like
# every base-game cave mouth; no quest). Disasm-proven in docs/DYNGRID_GATE_RCA.md sec 5.
# GridEntrance::Read (Engine 0x10195240) consumes a 60-byte 0x14 = a 12-byte generic prefix
# (2,0,1) + the 48-byte mouth/exit/dest binding, whereas the Dynamic class read a BARE 48-byte
# 0x14. So the entrance's 0x14 MUST become 60 bytes: prepend this 12-byte prefix. Byte-verified
# against the working Silk Road cave mouth (SilkRdDngEntrance_C01_Ext 0x14 in HiddenValley01):
# its 60-byte payload's first 12 bytes are EXACTLY 02000000 00000000 01000000. The LANDING
# record portal_olympianarena2 stays GridExitOneWay (born-open) with its 48-byte 0x14 unchanged.
# _normalize_spec applies this prefix to EVERY portal_olympianarena1 spec (A1 + Sparta + Garden
# + Secret Place + all 20 hub entrances) so the map + DB halves stay in lockstep.
GRIDENTRANCE_0x14_PREFIX = struct.pack('<III', 2, 0, 1)  # 02000000 00000000 01000000
assert len(GRIDENTRANCE_0x14_PREFIX) == 12

# --- WORKSTREAM A: INVENTED Sparta Crypt L2 entrance (mirrors A1 exactly, pure-0x14) -------
# SpartaCryptLevel2 never had an entrance in SV (SV-areas Wave 5 proved: zero inbound binders
# in pristine SV either). Will's directive: INVENT one - place an entry portal inside the
# base-game Athens-battlefield crypt (CataCube02_FloorLast, the DEEPEST Athens catacomb, an
# exact thematic match for SpartaCryptLevel2's Athens-catacomb set) bound to SpartaCryptLevel2's
# MERGED GUID, landing on-mesh, + a reciprocal RETURN portal inside SpartaCryptLevel2 back to
# the crypt. Full recon + design: docs/SPARTA_CORRECTIONS_LOG.md.
#
# MECHANISM: the A1 portal pair, which ROUND 2 made born-open. The ENTRANCE record
# portal_olympianarena1 is Class GridEntrance (static, born-open, always-visible - see the A1
# block); the LANDING portal_olympianarena2 is GridExitOneWay (born-open). NOTE (round-2
# correction): the old comment here claimed "a static GridEntrance needs a reciprocal 0x06
# GridSystem descriptor" - that was a MIS-generalization from a base-game correlation (base cave
# mouths happen to ALSO front 0x06 dungeons). Disassembly proved the portal TELEPORT reads ONLY
# the 0x14 binding (GridEntrance::GetConnectedPortalId=[+0x2d8], GetConnectedRegionId=[+0x2e8]);
# the paired landing supplies the other-side portal via Region::GetPortal(exit_uid). NO 0x06 is
# consulted (docs/DYNGRID_GATE_RCA.md sec 4). So the pure-0x14 pair works born-open with NO quest
# and NO 0x06. Each instance's 0x14: entrance = 12-byte prefix + mouth+exit+dest(60B total,
# prefixed in _normalize_spec); landing = exit+zeros(48B).
#
# HOST = CataCube02_FloorLast (v0x0f, corner (-6612,0,-3218), GUID 817574a8674093619ebf6581db63274c,
#   real baked navmesh, 0 existing 0x14 = clean append; the v0f inject path is the proven A1 one).
# DEST = SpartaCryptLevel2 (v0x0e SV-ONLY, corner (-5644,0,-1451), MERGED GUID
#   797c78594040cba419340c990e6903c4, real navmesh since build23). SV-only -> inject_into_sv_only_blob,
#   which now supports x14_payload appends (0x14 section already exists at size 0).
#
# MINTED map-unique UID pairs (collision-checked vs 157,524 known UIDs, plan_sparta_portals.py):
SPARTA_M1 = bytes.fromhex('efbf54c99a6b2bc7b64f04cd0ce8d0db')  # inbound entrance mouth
SPARTA_X1 = bytes.fromhex('d76121ad4419c6d4dcab9301e18f0dca')  # inbound exit (== SC2 native door id)
SC2_MERGED_GUID = bytes.fromhex('797c78594040cba419340c990e6903c4')          # SpartaCryptLevel2
CATACUBE_FLOORLAST_GUID = bytes.fromhex('817574a8674093619ebf6581db63274c')  # CataCube02_FloorLast
PORTAL_OLYMPIANARENA2_DBR = b'records\\quests\\portal_olympianarena2.dbr'     # GridExitOneWay landing
# P1 HOST entrance -> SC2 : mouth M1, exit X1 (pairs the SC2 0x06 native door), dest = SC2 GUID
SPARTA_P1_0x14 = SPARTA_M1 + SPARTA_X1 + SC2_MERGED_GUID
assert len(SPARTA_P1_0x14) == 48
#
# ── NATIVE TWO-WAY DOOR CONVERSION (2026-07-08 wave, appended-host discriminator) ──
# LIVE-PROVEN engine gate (Will's walk tests + the fork's byte diagnosis): a GridEntrance
# hosted in an ORIGINAL-INDEX level fires; one hosted in an APPENDED SV-only level NEVER
# fires, even with a byte-perfect 0x14 (G3/S3/hub-returns all dead, G1/S1/hub-outbound all
# live). So the old P2/P3/P4 instances (landing + return entrance inside SC2 + return
# landing in the catacube) are REMOVED and replaced by the mechanism the blood cave uses
# to walk OUT: the DESTINATION level's 0x06 portal-descriptor tail. SC2 ships ONE 0x06
# descriptor authored by SV for a SpartaOptCata01 entrance that never existed - byte-
# verified DANGLING (exit 3593305c.., mouth 04aea7af.., each occurring exactly ONCE in the
# whole merged world). rewrite_0x06_descriptors repurposes that descriptor IN PLACE
# (60-byte rewrite, count stays 1): exit=SPARTA_X1, mouth=SPARTA_M1, src=catacube GUID,
# trailer=(6,0,4) = the door GRID CELL (x, layer, z) in SC2's 10x10 grid of 8u cells
# (byte-precedent: Random09A's working walk-out descriptor trailer (8,0,2) = its door
# cell; crypt_floor1 is 2-layer, hence the A1-uber conversion stays DEFERRED). Cell
# (6,0,4) center = SC2-local (52,36): on-mesh 0.14u, openNbr 8/8, 1402/1600 walkable
# cells in the 8u square, median floor Y -1.60 (== the old P2/P3 floor). The engine
# builds the door + return teleport from the descriptor alone (no 0x05 art entity needed
# in SC2), paired 1:1 with P1's 0x14 (mouth M1/exit X1) - a native bidirectional door.
# The retired minted ids (kept for the audit trail; no longer written anywhere):
#   SPARTA_M2 e8d88f28dbfe1c3fa79ae1aacc435010 / SPARTA_X2 6babdaaf344cc5476258f8e7ce8925f3
SC2_LEVEL_KEY = 'levels/world/greece/minidungeons/spartacryptlevel2.lvl'
SC2_DANGLING_EXIT = bytes.fromhex('3593305c5f449ee852833aa3692aa72c')
SC2_DANGLING_MOUTH = bytes.fromhex('04aea7af234f0eaedd5a3cbd30348aaa')
# level_key -> list of 0x06 descriptor rewrites (see rewrite_0x06_descriptors)
# P0 DISABLED (Will 2026-07-12): this repurposed SC2's dangling 0x06 descriptor into a native
# WALK-THROUGH return door (catacube <- SpartaCryptLevel2). Will's TRAVEL LAW bans every
# walk-through/proximity teleport we author, in BOTH directions of a pair. The catacube->SC2
# entrance portal is removed (INJECT_SPECS) and this return is now the in-SC2 svc_testhub_return
# NPC, so this rewrite is emptied - SC2's descriptor reverts to its SV-original dangling state
# (harmless; it was dangling in SV upstream). The spec + constants are kept above for history.
REWRITE_0X06_SPECS = {}
_RETIRED_REWRITE_0X06_SPECS = {
    SC2_LEVEL_KEY: [{
        'match_exit': SC2_DANGLING_EXIT, 'match_mouth': SC2_DANGLING_MOUTH,
        'new_exit': SPARTA_X1, 'new_mouth': SPARTA_M1,
        'new_src': CATACUBE_FLOORLAST_GUID, 'new_trailer': (6, 0, 4),
    }],
}

# ── UBER DUNGEON NATIVE RETURN DOOR (M1, build30) ──────────────────────────────────
# Resolves the "crypt_floor1 is 2-layer, hence the A1-uber conversion stays DEFERRED"
# note above, now that the 2-layer door-cell layer RE is solved (tasks/wx21win4f.output,
# RE + independent Verify both "solved"): doorY is the 0-based vertical GRID-LAYER index
# (< glay), layer 0 = lowest floor. crypt_floor1 realizes ONE navmesh floor at world Y=10
# = layer 0, so doorY=0. The forward maze03 -> crypt door already works via maze03's
# INJECTED born-open GridEntrance mouth portal_olympianarena1 (0x14 inst[447]: mouth
# 58941143.., exit 6e513e90.., dest crypt GUID) - the "maze03 host 0x14 UNCHANGED"
# constraint. crypt currently ALSO carries the native GridExitOneWay LANDING
# portal_olympianarena2 (0x05 inst[192] + a 48B 0x14 whose mouth == 6e513e90). This wave
# converts the door to the pure-native two-way mechanism the blood cave + Sparta use:
#   (a) APPEND a reciprocal 0x06 descriptor to crypt whose (exit, mouth, src) MIRROR the
#       maze03 host mouth + maze03's level GUID, at the landing door cell (17, 0, 28) =
#       (floor(139.94/8), layer 0, floor(231.94/8)); the engine then builds the paired
#       two-way portal (UniqueId == exit 6e513e90) from the descriptor alone (Random09A
#       walk-tested precedent), giving the RETURN leg.
#   (b) REMOVE the landing portal_olympianarena2 + its 0x14 so it does not register a
#       SECOND portal with the same id 6e513e90 as the new descriptor (Random09A has NO
#       landing entity, only the descriptor). See remove_0x05_instances_by_0x14_uid.
# NOTE: crypt also has an INJECTED-but-inert portal_uberdungeon_return (0x05, no 0x14) at
# (140,10,215), 13u from the door cell - out of M1 scope, harmless to the mechanism
# (no 0x14 = registers no portal); flagged as a residual, not touched here.
CRYPT_FLOOR1_LEVEL_KEY = 'levels/world/uberdungeon/crypt_floor1.lvl'
MAZE03_GUID = bytes.fromhex('cdef89ae834a4adf1214609306708c02')      # maze03 level GUID (host)
UBER_RETURN_EXIT = bytes.fromhex('6e513e901549b1d558db968c61bda66a')  # == maze03 host mouth's exit
UBER_RETURN_MOUTH = bytes.fromhex('58941143e04eb3c0d62dbd952143f05d')  # == maze03 host mouth's mouth
# level_key -> list of 0x06 descriptors to APPEND (see append_0x06_descriptors)
# P0 DISABLED (Will 2026-07-12): this appended a native WALK-THROUGH return door
# (maze03 <- crypt_floor1, the Uber Dungeon exit). The maze03->crypt entrance portal is removed
# (INJECT_SPECS) and the Uber return is now the in-crypt svc_testhub_return NPC, so this append
# is emptied - crypt reverts to its SV-baseline 0x06 (no invented return door). Kept for history.
APPEND_0X06_SPECS = {}
_RETIRED_APPEND_0X06_SPECS = {
    CRYPT_FLOOR1_LEVEL_KEY: [{
        'exit': UBER_RETURN_EXIT, 'mouth': UBER_RETURN_MOUTH, 'src': MAZE03_GUID,
        'cell': (17, 0, 28),
    }],
}
# level_key -> list of 0x05-instance removals keyed by a uid inside the instance's 0x14
# binding (see remove_0x05_instances_by_0x14_uid). The landing's 0x14 mouth == the new
# descriptor's exit, so keying on that uid deletes exactly the duplicate-id landing.
# P0 DISABLED (Will 2026-07-12): this deleted crypt_floor1's SV-native GridExitOneWay landing
# portal_olympianarena2 (inst[192]) only because the now-retired APPEND_0X06 return door reused
# its portal id. With that append gone the deletion is unnecessary AND would touch an SV-original
# record (banned) - so it is emptied; the SV landing stays exactly as SV shipped it (inert,
# GridExitOneWay does not teleport-on-touch). Kept for history.
REMOVE_0X05_BY_0X14_UID_SPECS = {}
_RETIRED_REMOVE_0X05_BY_0X14_UID_SPECS = {
    CRYPT_FLOOR1_LEVEL_KEY: [{
        'uid': UBER_RETURN_EXIT, 'uid_field': 'mouth',
        'expect_dbr': PORTAL_OLYMPIANARENA2_DBR, 'expect_0x14_size': 48,
    }],
}

# ── MAP-REF-1 DE-PLACEMENT (M2, build30) ───────────────────────────────────────────
# The 68 SV town NPCs / setdress placed in these (mostly base-game) town levels reference
# records that are ABSENT from the shipped arz (fully restoring them needs a 3169-record
# SVAERA economy import + external mesh/texture arcs + merchant tags = out of build30 scope;
# left in place they silently fail to spawn / show raw-named). INTERIM build30 DEFAULT
# (Will informed, can override to full-restore-later): DE-PLACE all 68 so the MAP-REF-1
# contract passes at 0 and the push-gate can ship. remove_0x05_instances_by_dbr strips each
# placement (all instances of each dbr) from its level blob, reindexing 0x14. Source of truth:
# scratchpad/contracts_violations_map.json (DB lane D3); this dict is the committed copy so the
# build reproduces without the scratch file. Setdress paths carry a LEADING SPACE (SV-authored
# corrupt path) - preserved exactly. level_key -> [record paths to de-place].
REMOVE_BY_DBR_SPECS = {
    'levels/world/babylon/hanginggardensexit01.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_02a_babylon-outskirts.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_02b_babylon-outskirts.dbr',
    ],
    'levels/world/egypt/memphis/256x256memphiscityarea.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\02_egypt_dyer_03a_memphis.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\02_egypt_dyer_03b_memphis.dbr',
    ],
    'levels/world/egypt/rhakotis/rhakotis02.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\02_egypt_dyer_01a_rhakotis.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\02_egypt_dyer_01b_rhakotis.dbr',
    ],
    'levels/world/egypt/thebes/thebes02.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\02_egypt_dyer_06a_thebes.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\02_egypt_dyer_06b_thebes.dbr',
    ],
    'levels/world/greece/area002/valley01.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_02a_sparta.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_02b_sparta.dbr',
    ],
    'levels/world/greece/area004/coastaltown01.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_04a_megara.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_04b_megara.dbr',
    ],
    'levels/world/greece/athens/athenscity03.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_10a_athens_.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_10b_athens.dbr',
    ],
    'levels/world/greece/delphi/delphicenter01.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_07a_delphi.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_07b_delphi.dbr',
    ],
    'levels/world/greece/delphi/delphilowlands04.lvl': [
        b'records\\proxies greek\\area005\\ag_magical_oceanid_02n.dbr',
    ],
    # N1/build31 addition: the Helos SOUL COLLECTORS are LATENT MAP-REF-1s exposed when the N1
    # portal made startingfarmland06d a mod-touched (scanned) level - the placements predate
    # build31 (SVAERA-era; the records are in NO arz, so they have silently never spawned).
    # Same record family and same interim policy as sc_orient_greatwall_01/02 above.
    'levels/world/greece/startingtownver2/startingfarmland06d.lvl': [
        b'records\\creature\\npc\\soulcollectors\\sc_greece_helos.dbr',
        b'records\\creature\\npc\\soulcollectors\\sc_greece_helos_02.dbr',
    ],
    'levels/world/greece/knossos/knossostownstarta.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_12a_herakleion.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_12b_herakleion.dbr',
    ],
    'levels/world/orient/changan/changancity06.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_07a_changan.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_07b_changan.dbr',
    ],
    'levels/world/orient/greatwall/roadtotown03a.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_06a_village-of-zhidan.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_06b_village-of-zhidan.dbr',
        b'records\\creature\\npc\\alchemists\\03_orient_alchemist_greatwall.dbr',
        b'records\\creature\\npc\\item_breaker\\a03_free_upgrader_greatwall.dbr',
        b'records\\creature\\npc\\item_upgrader\\a03_unique_upgrader_greatwall.dbr',
        b'records\\creature\\npc\\soulcollectors\\sc_orient_greatwall_01.dbr',
        b'records\\creature\\npc\\soulcollectors\\sc_orient_greatwall_02.dbr',
        b'records\\creature\\npc\\uniquetrader\\03_orient_trader_greatwall.dbr',
        b'records\\sceneryorient\\structure\\building\\town\\setdress\\ orienttownsetdresssqbasketveg02.dbr',
        b'records\\sceneryorient\\structure\\building\\town\\setdress\\ orienttownsetdresstablegroup.dbr',
        b'records\\xpack\\creatures\\npc\\enchanter\\enchanter_greatwall.dbr',
    ],
    'levels/world/orient/silkroad/basecampforest02.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_03a_shangshung-village.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_03b_shangshung-village.dbr',
    ],
    'levels/world/orient/silkroad/hiddenvalley01.lvl': [
        b'records\\sceneryorient\\structure\\building\\town\\setdress\\ orienttownsetdresstablegroup.dbr',
    ],
    'xpack/levels/area01_rhodes/rhodes_cityfinal_01.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\04_hades_dyer_01a_rhodes.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\04_hades_dyer_01b_rhodes.dbr',
    ],
    'xpack/levels/area04_styx/undergrounds/styx_cryptug_stonetransitioniii01.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\04_hades_dyer_05a_city-of-lost-souls.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\04_hades_dyer_05b_city-of-lost-souls.dbr',
    ],
    'xpack/levels/area06_elysian/elysian_fields_04.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\04_hades_dyer_07a_elysium.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\04_hades_dyer_07b_elysium.dbr',
    ],
    'xpack2/levels/asgard/underground/valhollcave08.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_10a_valholl.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_10b_valholl.dbr',
    ],
    'xpack2/levels/celticheartlands/glauberg02.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_05a_glauberg.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_05b_glauberg.dbr',
    ],
    'xpack2/levels/celticheartlands/heuneburgoutskirts02.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_03a_heuneburg.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_03b_heuneburg.dbr',
    ],
    'xpack2/levels/corinthia/corinthia.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_01a_corinth.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_01b_corinth.dbr',
    ],
    'xpack2/levels/darklands/underground/mfc01.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_09a_dark-lands.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_09b_dark-lands.dbr',
    ],
    'xpack2/levels/scandia/kinggylfissettlement.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_07a_gylfis-settlement.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_07b_gylfis-settlement.dbr',
    ],
    'xpack3/levels/atlantis/atlantishigh02b.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\04b_atlantis_dyer_07a_atlantis-high-district.dbr',
    ],
    'xpack3/levels/iberia/atlasmountains14.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\04b_atlantis_dyer_04a_atlas-mountains.dbr',
    ],
    'xpack3/levels/iberia/gadir01.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\04b_atlantis_dyer_01a_gadir.dbr',
    ],
    'xpack3/levels/tartarus/underground/transitioncave01.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\04b_atlantis_dyer_08a_tartarus.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\04b_atlantis_dyer_08b_tartarus.dbr',
    ],
    'xpack4/levels/act1/06ricefields/1_6ricefields04.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_05a_village-of-xiao.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_05b_village-of-xiao.dbr',
    ],
    'xpack4/levels/act1/underground/yaosummerresidence.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_01a_summer-palace.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_01b_summer-palace.dbr',
    ],
    'xpack4/levels/act2/01pingyang/2_1pingyang05.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_06a_pingyang.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_06b_pingyang.dbr',
    ],
    'xpack4/levels/act3/01thedunes/3_1thedunes01.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_09a_asyut-encampment.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_09b_asyut-encampment.dbr',
    ],
    'xpack4/levels/act3/01thedunes/3_1thedunes20.lvl': [
        b'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_13a_thebes.dbr',
        b'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_13b_thebes.dbr',
    ],
}

# ── M6: DE-PLACE the DANGLING Olympus respawn shrine (Will 2026-07-09) ───────────────
# DIFFERENT rationale from REMOVE_BY_DBR_SPECS above (that dict is MAP-REF-1: records
# ABSENT from the arz). Here the record RESOLVES fine (it is the base-game xpack2 respawn
# shrine), but its RESPAWN-SYSTEM BINDING is broken in the merged world: OlympusFinal02
# (the single base-game Olympus level; region "Lower Olympus" = tagRegionName146) places
# StrategicMovementRespawnShrine records\xpack2\item\shrines\respawn\respawn_olympus_new.dbr
# at world (414.8,43.0,822.6) with flags=1 + UniqueId 90de912a674ae54b8c7cb2a8d4ae1348.
# In VANILLA that UniqueId is a member of the world GROUPS(0x11) `Shrine_Respawn_Hades`
# record (53 members), so the respawn system binds it and it works. In OUR merged (SVAERA-
# base) world that GROUPS record carries only 51 members and the shrine's UniqueId is ABSENT
# (byte-verified: scratchpad/check_respawn.py) - a SVAERA-merge-inherited dangling binding,
# present since the earliest merged baseline (NOT a wave regression). Result: the shrine
# RENDERS but never functions as a respawn point ("visible but does not work"), exactly the
# same failure class as the Duister teleportshrineorient01 (docs/BACKLOG.md B-PORTAL-3) and
# the build18 rebirth fountain. Will's request (verbatim): "there is a non working respawn
# trophy in lower olympus that needs to be removed." De-placing the (already non-functional)
# 0x05 instance + its 12-byte 0x14 removes the dead prop with ZERO gameplay change (it never
# bound a respawn anyway). Placed EXACTLY ONCE in the whole merged world (verified), so the
# per-level by-dbr removal is unambiguous. NOTE (reported to Will): the sibling
# teleportshrineolympus01 in the SAME level is dangling the SAME way (Shrine_Teleport_Hades
# 5->4); left in place pending Will's call (he named only the respawn one). An ALTERNATIVE to
# removal is to RE-BIND the UniqueId into Shrine_Respawn_Hades (restore a working Olympus
# respawn point); removal was chosen per Will's explicit instruction.
REMOVE_DANGLING_SHRINE_SPECS = {
    'levels/world/olympus/olympusfinal02.lvl': [
        b'records\\xpack2\\item\\shrines\\respawn\\respawn_olympus_new.dbr',
    ],
}

# ── M14: DE-PLACE stray cross-expansion props (audit 2026-07-10 Lane A, cosmetic) ────
# records\xpack3\scenery\atlantis\underground\tombstone.dbr = an Atlantis-DLC
# FixedItemQuestObject (locked=1, description = the literal dev placeholder 'Hogge', no
# quest reference in any of the 6 quest arcs) placed ONCE inside the Greek base-game
# minidungeon MonsterCave01B (v0f, instance [58], local (13.03,1.00,14.43), flags=0,
# no 0x14). A cross-expansion merge artifact: a locked, non-interactive prop a curious
# player clicks and gets nothing from. Same de-place mechanism as M2/M6; the record
# RESOLVES in the arz (base XPack3), so this is neither MAP-REF-1 nor a dangling
# binding - simply a stray prop with no function.
REMOVE_STRAY_PROP_SPECS = {
    'levels/world/greece/minidungeons/monstercave01b.lvl': [
        b'records\\xpack3\\scenery\\atlantis\\underground\\tombstone.dbr',
    ],
}

# ── M8 PHASE-1 PILOT: the PORTAL-MASTER NPC (Model C, Will-approved 2026-07-09) ──────
# Will chose Model C (an NPC you talk to who teleports you) as the portal model going
# forward; Model B (FixedItemTeleport class-swap) is DEAD (its destination is encoded
# NOWHERE in data - not the record, not the 0x14, not SD - the engine resolves vanilla
# pairs internally, so a swapped gate teleports nowhere); Model A (walk-through
# GridEntrance) stays as the transitional fallback and NO existing portal is removed in
# Phase 1. Mechanism = the base-game boatman: Action_BoatDialog(npc, onOff, x, y, z, tag)
# (used by 'quest 8 part i - greece to egypt' + 'quest 7 - knossos'; the mod already has
# make_boat_dialog_action in qst_format.py). Its x/y/z are WORLD coordinates as SIGNED
# INTEGERS (base exemplar: Knossos->Rhakotis x=-1966 y=13 z=4423 stored two's-complement).
#
# COORDINATE FORMULA (double-validated 2026-07-09): world = LEVELS-index corner
# (ints_raw[6,7,8]) + instance-local. Proof 1: drxBC2 corner (5275,-27,2955) + Toxeus
# local (13.10,28.00,137.70) = world (5288.10,1.00,3092.70), and the level 0x0b navmesh
# floor at that exact cell reads Y=1.00. Proof 2: the base boat target (-1966,13,4423)
# falls at a small positive local offset inside the Rhakotis dock levels.
#
# THE NPC (Phase-1 pilot, ONE instance): HOST = startingfarmland06d (Helos village,
# v0x11 shared). SPOT local (76.50, 0.60, 189.50) = world (-5971.50, 1.60, 917.50):
# the Helos town-portal plaza, visually grouped with the portal corner - 5.7u S of the
# TeleportShrineHelios01 device (74.18,0.50,194.65), 7.7u E of Starting_PortalMan
# (68.92,0.34,188.25), 6.0u NE of the H1 Garden portal (74.00,0.40,184.00 - far enough
# that walking to the NPC cannot cross H1's ~3u teleport plane), 8.9u from the R2 return
# landing (68.00,-0.40,181.00 - arrivals see him immediately), nearest decor >= 8.5u
# (statue 68.50,193.18). Navmesh-verified (scratchpad npc_spot_check.py vs the level's
# own 0x0b): ON-MESH exact cell, floor local Y=0.60 (spec Y matches the floor), 100%
# walkable coverage in a 3u square, CONNECTED (engine 4-adj/climb model) to H1, R2, the
# shrine and PortalMan. Plane-crossing rules do NOT apply (NPC, not a portal).
#
# DESTINATIONS for the boat-dialog quest (proven landing points; world = corner+local,
# rounded to int for the qst fields; all four spots carry >= 3u walkable clearance):
#   Garden of Merchants  gardenofmerchants   corner (1043,0,-4074)  local (130.30,-39.00,73.10)
#       -> world (1173, -39, -4001)   [= the N1 H2 landing, caravan_rhodes merchant hub]
#   The Secret Place     darkforestenter     corner (-2420,0,-5820) local (23.90,2.00,30.50)
#       -> world (-2396, 2, -5790)    [= the A2 S2 landing, cluster entry]
#   Uber Dungeon         crypt_floor1        corner (-2578,0,-2682) local (139.94,10.01,231.94)
#       -> world (-2438, 10, -2450)   [= the SV-native A1 arrival spot; its landing ENTITY was
#                                      removed in the build30 native-door conversion but the
#                                      SPOT is the proven walkable arrival point by the arena
#                                      portal / minotaur statue]
#   Sparta Crypt depths  spartacryptlevel2   corner (-5644,0,-1451) local (42.30,-1.60,42.30)
#       -> world (-5602, -2, -1409)   [= the hub landing spot, >= 10u from the native door cell]
#
# ✅ WIRED (build32a, 2026-07-10): the DB lane's build32 Group A (commit 3638ba4) shipped
# records\quests\portal_master_helos.dbr in the arz (27e6742012833cf63da33035cb618353) +
# the boat-dialog rides sv_commonmechanics.qst in Quests.arc (6ff23c29..., 4 destination
# hits verified by decompressed-entry scan). The spec below is LIVE in INJECT_SPECS under
# startingfarmland06d (v0x11 shared -> the proven step-6/7 v11 injection; flags=0,
# identity rot, no 0x14 - the Starting_PortalMan NPC byte-shape, same path as the shipped
# Olympus herald). DEPLOY COUPLING: this map ships together with that Quests.arc
# (Levels+Quests law - the dialog lives quest-side).
# Phase 2 (after Will's pilot walk-test): return-side portal-masters in each area, then
# retire the GridEntrance portals per Will's call.
PORTAL_MASTER_NPC_DBR = b'records\\quests\\portal_master_helos.dbr'  # matches the arz record
PORTAL_MASTER_HOST_KEY = 'levels/world/greece/startingtownver2/startingfarmland06d.lvl'
PORTAL_MASTER_SPEC = (PORTAL_MASTER_NPC_DBR, 76.50, 0.60, 189.50)  # WIRED (build32a)

# ── M12 CAMPAIGN BLOCKER: Olympus->Rhodes continuation NPC (Will, 2026-07-09) ────────
# RCA (M7, now CONFIRMED in-game): the base post-Typhon portal xq00_olympus_portaltorhodes
# (FixedItemTeleport, locked=1) is present + unchanged in our map, and the Q1 quest lane
# added an Action_UnlockFixedItem on the "Olympus - Typhon Defeated" token (in "quest that
# controls bosses and their doors.qst" - condition = Condition_OnLevelLoad + that token,
# satisfiable). Will killed Typhon on a fresh session, the unlock event is present in the
# DEV Quests, and STILL no working portal. This EMPIRICALLY PROVES the M7 finding:
# FixedItemTeleport's Olympus->Rhodes DESTINATION is ENGINE-INTERNAL (the base end-of-TQ
# campaign pairing), encoded NOWHERE in data (not the record, not the 0x14, not SD) and
# never activated for a Custom Quest total conversion; unlocking the gate cannot supply a
# destination. (Render side is NOT the root cause: the mesh XPack\Items\Shrines\Teleport\
# Credits_Portal.msh + the Egypt_Hatshepsut_PortalGate idle/activate anms all RESOLVE in
# the base XPack Items.arc, inherited cleanly by the mod - so the locked gate can render,
# it just teleports nowhere.)
#
# FIX = Model C boat-dialog NPC at the summit -> Action_BoatDialog to the Rhodes arrival
# (data-driven world coord, no engine hook), exactly like the M8 portal-master.
#
# THE NPC: HOST = OlympusFinal02 (v0x11 shared; the ONLY Olympus level; regions "Lower
# Olympus"/"Olympus Summit"). SPOT local (305.80, 90.20, 490.80) = world
# (1155.80, 90.20, -3190.20): 4.0u due +Z of the locked portal xq00_olympus_portaltorhodes
# (instance [41], local (305.79,90.11,486.84)) on the Typhon-summit plateau where the
# player fights + kills Typhon - the exact spot Will looks for the missing portal. Navmesh-
# verified vs OlympusFinal02's own 0x0b (scratchpad m12.py): ON-MESH exact cell, floor
# world Y=90.20, 100% walkable coverage in a 3u square, CONNECTED (engine 4-adj/climb model)
# to the portal cell; ZERO entities within 18u (open plateau -> prominent, unobstructed).
# Plane-crossing rules do NOT apply (NPC, not a portal).
#
# BOAT-DIALOG DESTINATION (for the DB/Quests lane): the Rhodes arrival is the base game's
# OWN paired target xq00_rhodes_olympusportaltarget.dbr, placed at Rhodes_CityFinal_01
# instance [439], corner (585,-11,-6692) + local (114.65,52.13,226.26) = WORLD
# (699.65, 41.13, -6465.74). The navmesh floor at that x/z is world Y=41.20 (target marker
# floats ~0.07u above floor). Action_BoatDialog x/y/z = SIGNED-INT world coords (base
# exemplar decoded: Knossos->Rhakotis stores x=-1966 as two's-complement):
#   Rhodes arrival  ->  x = 700,  y = 41,  z = -6466   (on-mesh, Rhodes_CityFinal_01)
#
# ✅ WIRED (build31g, 2026-07-09 overnight): the DB/Quests lane shipped the record + the
# boat-dialog quest in Q3 commit 36a6212 ('herald record name+spec now FINAL'; arz bd6ae869
# carries records\quests\portal_master_olympus.dbr cloned from the proven Knossos boatman;
# Quests 3db3764c hosts the Action_BoatDialog to (700,41,-6466); both DEV-deployed by that
# lane). The spec below is LIVE in INJECT_SPECS under olympusfinal02 (v0x11 shared ->
# step-6/7 v11 injection; flags=0, identity rot, no 0x14 - the Starting_PortalMan NPC
# byte-shape). The map half completes the coupled set. Note: the locked xq00 gate stays
# placed (harmless; also has the Q3 instant kill-unlock as belt-and-suspenders).
OLYMPUS_RHODES_NPC_DBR = b'records\\quests\\portal_master_olympus.dbr'  # matches the arz record
OLYMPUS_RHODES_HOST_KEY = 'levels/world/olympus/olympusfinal02.lvl'
OLYMPUS_RHODES_NPC_SPEC = (OLYMPUS_RHODES_NPC_DBR, 305.80, 90.20, 490.80)  # WIRED (build31g)

# ── M9 WIRED (build32b): Vashkarr, Eldest of the Ancients (N4-DB, Will signed off) ───
# HOST = Levels/World/Orient/Underground/Random05A.lvl (the cave via ToTomb02 east of
# Chang'an; base-game v0x0e -> the new SVAERA-side v0e injection branch, commit 5af756c).
# The 'Majestic Chest' (GoldenChest_Normal_02, inst [25] @ local (24.01,1.00,28.70))
# stays UNTOUCHED per the design. SPOT local (24.00, 1.00, 31.70) = 3.0u in FRONT of the
# chest (guarding it, per Will's M15 'spawn AT the treasure' taste): navmesh-verified
# (level's own 0x0b, 60,356 cells): on-mesh exact cell, floorY 1.0, 95% walkable coverage
# in a 3.5u square (room for the spawnMax=3 escort; the at-chest spot itself is only 65%
# vs a wall). NOTE: the native Hero_Djinn_BloodSisters proxy also lives in this room
# (6.8u from the chest) - fights can stack, accepted (the design chose this cave).
# byte-shape = q_leinth_lone exemplar (flags=0, no 0x14, exemplar rot).
# ✅ WIRED (build32b, 2026-07-10): the DB lane's build32 Group C (commit 36ab4ee) shipped
# q_vashkarr_lone + pools\q_vashkarr_lone + um_vashkarr_99 in the arz (27e67420...).
# FIRST LIVE USE of the v0e SVAERA-host branch (5af756c): parse-back gate = random05a
# 0x05 instance count 59 -> 60 + blob re-parse to exact stream end + on-mesh re-verify.
VASHKARR_PROXY_DBR = b'records\\drxmap\\proxy\\q_vashkarr_lone.dbr'
VASHKARR_HOST_KEY = 'levels/world/orient/underground/random05a.lvl'
VASHKARR_SPEC = (VASHKARR_PROXY_DBR, 24.00, 1.00, 31.70,
                 {'rot': Q_LEINTH_EXEMPLAR_ROT})  # WIRED (build32b)

# ── A1 WIRED (build36 CONVERGENCE): Enslaver warband set-piece (amendment map delta) ──
# The DB lane (_create_enslaver_warband, apply_svc_patches.py) shipped the championChance
# set-piece in the arz: pool/proxy q_enslaver_warband -> 1 um_toxeus_enslaver_99 leader +
# 4 "{^r}Enslaved Shadow Marauder" champions PRESENT AT SPAWN (spawnMax=5 / championMin=
# Max=4 / championChance=100, chanceToRun=100, limit_obsidianbosses [1..110],
# placementExtents 4.0 on the proxy). Registered in _MOD_AUTHORED_SPAWN_PROXIES + the
# roaming-sweep leak-guard allow-set _EN_YARD_POOLS. This is the ONE map-lane step: place
# the single proxy entity in a shadow-touched blood-cave pocket. HOST = drxFirstXistion_
# connection (the FLAT widow-letter connection chamber - SAME level + inject path as
# FINALLETTER above). SPOT LOCAL (21.1,10.0,-6.5) world (5680,10,3285) SURVEYED on the
# canonical 0x0b (tools/debug/survey_uberboss_spots.py --base 56): on-mesh 0.00u, clr 100%
# in ALL 3 tilesets (Normal/Epic/Legendary), MAIN component #1/109590; floor localY 10.00
# (byte-matches the finalletter y=10.005 in this level); 11.5u from the nearest native (rock
# dress), ~26.6u from the widow finalletter (no spawn-camping the quest letter). SV-only
# v0x0e -> inject_into_sv_only_blob (56 B), flags=0, no 0x14, q_leinth_lone exemplar rot
# (the q_vashkarr_lone byte-shape). COUPLED SHIP: needs the arz's q_enslaver_warband records.
EN_WARBAND_PROXY_DBR = b'records\\drxmap\\proxy\\q_enslaver_warband.dbr'
EN_WARBAND_HOST_KEY = 'levels/world/xbloodcave/drxfirstxistion_connection.lvl'
EN_WARBAND_SPEC = (EN_WARBAND_PROXY_DBR, 21.1, 10.0, -6.5, {'rot': Q_LEINTH_EXEMPLAR_ROT})

# ── M10 WIRED (build32b): Obsidian Halls treasure roulette corners (N6-DB) ───────────
# 4 corner proxies (chanceToRun=25 each, shared warband pool q_obs_warband) in the Act-3
# Obsidian Halls: tombobs01 + tombobs02 (Levels/World/Orient/TyphonUG/, base-game v0x0e
# -> the v0e branch, M9-proven live). Corner coords = the design doc's surveyed on-mesh
# spots (docs/OBSIDIAN_ROULETTE_DESIGN.md: calibration 23/23 + 36/36 floor markers):
#   A tombobs02 (50.4, 1.0, 143.6)    C tombobs02 (200.4, 1.0, 97.6)
#   B tombobs01 (220.8, 1.0, 89.6)    D tombobs01 (92.8, 1.0, 47.6)  [nudged, see below]
# ✅ WIRED (build32b, 2026-07-10): the DB lane's build32 Group F (commit 6c6c0cd) shipped
# q_obs_roulette_{a,b,c,d} + pools\q_obs_warband + the obsidianhoard chest chains in the
# arz (9265619d...); all 4 proxy paths byte-verified against the landed record table.
# ON-MESH RE-VERIFY (vs the levels' own 0x0b in the build32a map, all 3 tilesets +
# 3.5u/49-sample clearance): A 100%, B 100%, C 100% (all walkable in every tileset).
# CORNER D at the surveyed (90.8,45.6) CONFIRMED TIGHT: walkable only in the radius-0.4
# tileset (NOT 0.6/0.8), 71% clearance -> NUDGED +2.0/+2.0 within the same corner pocket
# to (92.8, 1.0, 47.6): walkable in ALL 3 tilesets, 100% clearance, same flat floor as
# corner B (floor probe local Y 1.2 at both spots; spec keeps the design's Y=1.0
# convention). byte-shape = q_leinth_lone exemplar (flags=0, no 0x14, exemplar rot).
OBS_ROULETTE_SPECS = {
    'levels/world/orient/typhonug/tombobs02.lvl': [
        (b'records\\drxmap\\proxy\\q_obs_roulette_a.dbr', 50.4, 1.0, 143.6,
         {'rot': Q_LEINTH_EXEMPLAR_ROT}),
        (b'records\\drxmap\\proxy\\q_obs_roulette_c.dbr', 200.4, 1.0, 97.6,
         {'rot': Q_LEINTH_EXEMPLAR_ROT}),
    ],
    'levels/world/orient/typhonug/tombobs01.lvl': [
        (b'records\\drxmap\\proxy\\q_obs_roulette_b.dbr', 220.8, 1.0, 89.6,
         {'rot': Q_LEINTH_EXEMPLAR_ROT}),
        (b'records\\drxmap\\proxy\\q_obs_roulette_d.dbr', 92.8, 1.0, 47.6,
         {'rot': Q_LEINTH_EXEMPLAR_ROT}),
    ],
}  # WIRED (build32b): merged into INJECT_SPECS right after its definition below

# ── BROODNEST WIRED (build35, 2026-07-11): Broodmother Nest apex set-piece (CANONICAL) ─
# docs/BROODMOTHER_NEST_DESIGN.md, the deferred climax of the N7 sepulchral-wyrm-horde
# chain. This is the FIRST canonical-map content change since build32b (Will-approved:
# "proceed with the broodmother nest implementation", 7 decisions delegated = take each
# doc recommendation). Host = tombobs02 (the doc's recommended primary), the SAME Act-3
# Obsidian Halls hall the roulette (above) already dresses, so the "treasure-tomb climax"
# reading is coherent. The DB lane (arz a947e98d) shipped the proxy records FIRST
# (MAP-REF-1 ordering): q_broodmother_lone (Proxy, pool svc_broodmother_pool -> 1 mother
# um_broodmother_99 + 2 um_sepulchralwyrm_40 escorts, placementExtents 3.5) and 6 egg-
# cluster proxies q_broodnest_egg_{a..f} (Proxy, pool svc_broodnest_hatch -> 3-6 common
# wyrmlings, placementExtents 2.5). All are the q_leinth_lone byte-shape (flags=0, no
# 0x14, exemplar rot) and inject via the same v0e branch (inject_into_sv_only_blob) the
# roulette uses.
#
# SURVEYED AT IMPLEMENT TIME against the canonical map's own tombobs02 0x0b (all 3
# tilesets = agent radii 0.4/0.6/0.8), the M9/M10 pattern:
#   nest CENTER local (184.0, 192.0) sits in the deep south chamber, a 14.0u-radius disc
#   that is fully walkable in ALL 3 tilesets; floor probe local Y = 1.20 (spec keeps Y at
#   the floor per the doc). The mother sits at center; the 6 eggs ring her at radius 10u.
# For EACH of the 7 spots (mother + 6 eggs): on-mesh in all 3 tilesets (nearest walkable
#   largest-comp cell <= 0.14u), 100% clearance measured BOTH over a 3.5u/49-sample square
#   AND over a filled disc at the record's real placementExtents (mother 3.5u, eggs 2.5u)
#   in all 3 tilesets, and nearest EXISTING native 0x05 instance > placementExtents+2u
#   (mother 14.4u, min egg 5.0u to a native tomb-monster proxy = ambient, no navmesh
#   blocker). No nudge was needed (every spot hit 100% on the first survey).
# SEPARATION from the roulette (Will's >=40u rule so encounters do not merge): the nearest
#   nest point is 82.0u from the corner-C warband edge (placementExtents 4.0) and 128.2u
#   from corner-A; corner A local (50.4,143.6), corner C local (200.4,97.6). Min point-to-
#   corner-centre distances: dCornerA >= 132.2u, dCornerC >= 86.0u. Far past 40u.
BROODNEST_HOST_KEY = 'levels/world/orient/typhonug/tombobs02.lvl'
Q_BROODMOTHER_LONE_DBR = b'records\\drxmap\\proxy\\q_broodmother_lone.dbr'
Q_BROODNEST_EGG_A_DBR = b'records\\drxmap\\proxy\\q_broodnest_egg_a.dbr'
Q_BROODNEST_EGG_B_DBR = b'records\\drxmap\\proxy\\q_broodnest_egg_b.dbr'
Q_BROODNEST_EGG_C_DBR = b'records\\drxmap\\proxy\\q_broodnest_egg_c.dbr'
Q_BROODNEST_EGG_D_DBR = b'records\\drxmap\\proxy\\q_broodnest_egg_d.dbr'
Q_BROODNEST_EGG_E_DBR = b'records\\drxmap\\proxy\\q_broodnest_egg_e.dbr'
Q_BROODNEST_EGG_F_DBR = b'records\\drxmap\\proxy\\q_broodnest_egg_f.dbr'
BROODNEST_SPECS = {
    BROODNEST_HOST_KEY: [
        (Q_BROODMOTHER_LONE_DBR, 184.0, 1.2, 192.0, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
        (Q_BROODNEST_EGG_A_DBR, 184.0, 1.2, 202.0, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
        (Q_BROODNEST_EGG_B_DBR, 175.3, 1.2, 197.0, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
        (Q_BROODNEST_EGG_C_DBR, 175.3, 1.2, 187.0, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
        (Q_BROODNEST_EGG_D_DBR, 184.0, 1.2, 182.0, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
        (Q_BROODNEST_EGG_E_DBR, 192.7, 1.2, 187.0, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
        (Q_BROODNEST_EGG_F_DBR, 192.7, 1.2, 197.0, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
    ],
}  # WIRED (build35): APPENDED to INJECT_SPECS[tombobs02] after the roulette corners below

# ── BUILD36 UBER/SUPER BOSS PLACEMENTS (CANONICAL, 2026-07-11) ─────────────────
# Five new hand-designed apex bosses, each placed by ONE `q_*_lone` proxy in a
# native base-game AE level. svaera_plus_portals.py's AE-inject loop dispatches by
# the host's ACTUAL blob version: 4 hosts are v0x0f/v0x11 (SwampBorder/RiverEdge/
# Mnemosyne01/StoneCity) -> inject_into_0x05_v11 (base-72), and Tomb01 (M4 Dorus) is
# v0x0e -> the base-56 inject_into_sv_only_blob branch. BOTH branches are proven by
# the shipped precedents on the same versions: the Obsidian roulette + Broodmother
# nest inject into tombobs01/02 (also v0x0e, base-56), and maze03 (v0x0f) uses the
# base-72 path. So each of the 5 hosts routes through an already-proven injector.
# Each proxy is the proven `q_leinth_lone` byte-shape: flags=0, no 0x14, exemplar
# rotation. Coords are LEVEL-LOCAL (world - grid-corner), surveyed on each host
# level's own 0x0b (all 3 tilesets) by the design specs and re-verified on the
# BUILT map by tools/debug/survey_uberboss_spots.py (the native 0x0b is byte-
# identical base-vs-merged, so the survey holds). Each boss's Boss-locked hoard
# chest rides as the proxy's DB-side accessory pool (spawns WITH the boss), so the
# map lane places exactly ONE proxy per boss - no separate chest placement.
#
# DB coupling: the q_*_lone proxy records (+ pools + hoard chests + souls) are
# authored by the parallel DB lanes against the SAME specs. Until the arz merges,
# MAP-REF-1 flags these proxy paths as not-yet-in-arz (EXPECTED); the convergence
# delta-vet cross-checks placement<->record-path parity before any deploy.
# Specs: scratchpad/specs/{propontis,tantalus,goldenbough,mnemosyne,dreadhalls}_uberboss_spec.md
#
# M4 DORUS THE DROWNED KING  - Propontis tomb, Medea_TempleUG_Tomb01 [784], corner (260,0,-8522)
DORUS_HOST_KEY = 'xpack/levels/area02_medea/undergrounds/medea_templeug_tomb01.lvl'
Q_DORUS_LONE_DBR = b'records\\drxmap\\proxy\\q_dorus_lone.dbr'
# M5 TANTALUS THE INSATIABLE - Den of Tantalus, Styx_SwampBorder_01 [755], corner (-396,0,-10209), v0x0f
TANTALUS_HOST_KEY = 'xpack/levels/area04_styx/styx_swampborder_01.lvl'
Q_TANTALUS_LONE_DBR = b'records\\drxmap\\proxy\\q_tantalus_lone.dbr'
# M6 CHARON AT THE GOLDEN BOUGH - Styx_RiverEdge_01, corner (-524,0,-9697), v0x11
GOLDENBOUGH_HOST_KEY = 'xpack/levels/area04_styx/styx_riveredge_01.lvl'
Q_GOLDENBOUGH_LONE_DBR = b'records\\drxmap\\proxy\\q_goldenbough_lone.dbr'
# M7 THE MNEMOPHAGE - Cave of Mnemosyne, Judgment_TempleUG_Mnemosyne01 [801], corner (127,-13,-11509), v0x11
MNEMOPHAGE_HOST_KEY = 'xpack/levels/area05_judgment/undergrounds/judgment_templeug_mnemosyne01.lvl'
Q_MNEMOPHAGE_LONE_DBR = b'records\\drxmap\\proxy\\q_mnemophage_lone.dbr'
# M8 EPHIALTES, THE DREAD - Dread Halls back corner, Judgment_StoneCity_Exit01 [931], corner (-1844,0,-13320), v0x11
DREAD_HOST_KEY = 'xpack/levels/area05_judgment/undergrounds/judgment_stonecity_exit01.lvl'
Q_EPHIALTES_LONE_DBR = b'records\\drxmap\\proxy\\q_ephialtes_lone.dbr'

UBERBOSS_SPECS = {
    # R4 FRAME FIX: every boss placement is now the SPEC-PRIMARY coord. The R1-R3 "nudges" were
    # ALL artifacts of a 16u frame bug in tools/debug/survey_uberboss_spots.py (fixed R4): the
    # survey compared 0x05-local query coords directly against the 0x0b navmesh-cell frame, but
    # the base-game XPack hosts carry a fixed (16,16) offset between the LEVELS-index grid corner
    # (which 0x05 coords are relative to) and the 0x0b navmesh origin (center-dims). So the tool
    # mis-read every spec-primary as off-mesh / near-wall / low-clearance and drove bogus nudges.
    # Re-surveyed in the CORRECTED frame (grid_corner-anchored; floor-instance calibration reads
    # ~0-1u; confirmed independently by the specs' own navlib survey): every spec-primary is
    # ON-mesh in the main component at clr 100% all 3 tilesets. Reverting to the spec coords
    # restores spec fidelity + clean map<->record convergence parity.
    #
    # M4 Dorus: PRIMARY hall-toward-vault. spec local (52.0,1.2,60.0) = world (312,1.2,-8462).
    # Corrected-frame survey: d=0.14u, clr@4.0 100%/100%/100% (N/E/L), comp#1. (R3 shipped the
    # bogus +4.2u nudge (49,63); reverted.)
    DORUS_HOST_KEY: [
        (Q_DORUS_LONE_DBR, 52.0, 1.2, 60.0, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
    ],
    # M5 Tantalus: PRIMARY den floor by the pj_denoftantalus POI. spec local (54.0,-15.2,114.3)
    # = world (-342,-15.2,-10094.7). Corrected-frame survey: d=0.10u, clr@3.5 100%/100%/100%,
    # comp#1. (R3 shipped the bogus +4.5u nudge (50,116); reverted.)
    TANTALUS_HOST_KEY: [
        (Q_TANTALUS_LONE_DBR, 54.0, -15.2, 114.3, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
    ],
    # M6 Charon: the Shrine of the Golden Bough. The spec's DEFAULT primary is the SUMMIT beside
    # the eternal flame, with the temple FORECOURT as the mandated fallback if the boss+2-champion
    # ring is non-walkable on the tight summit. Corrected-frame survey CONFIRMS the summit is
    # genuinely tight - summit local (217.7,1.2,12.5) reads d=0.00 but clr@3.5 only 92%/91%/82%
    # (N/E/L); 18% of the champion ring hangs off on Legendary (matches the spec's ~2.8u<3.5u-
    # extents warning). So the spec FORECOURT is used: local (187.9,-7.0,46.9) = world
    # (-336.1,-7.0,-9650.1), d=0.00u, clr@3.5 100%/100%/100%, comp#1, between the two colossal
    # statues. (R3 shipped a +3u nudge (185,48) off the spec forecourt; reverted to the spec
    # coord.) SUMMIT stays a viable in-game A/B if Will accepts the tighter champion ring.
    GOLDENBOUGH_HOST_KEY: [
        (Q_GOLDENBOUGH_LONE_DBR, 187.9, -7.0, 46.9, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
        # SUMMIT alt (spec default, tight 82% Leg): (Q_GOLDENBOUGH_LONE_DBR, 217.7, 1.2, 12.5, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
    ],
    # M7 Mnemophage: PRIMARY north node of the machae boss-glyph ritual ring (the boss rises
    # within the glyphs). spec local (43.0,3.0,71.0) = world (170,~-10,-11438); Charon torch ~31u
    # SE. Corrected-frame survey: d=0.14u, clr@3.5 100%/100%/100%, comp#1. Already spec-exact in
    # R3 (the one spot the frame bug happened not to move); UNCHANGED. ALT-B = local (41.0,3.0,61.0).
    MNEMOPHAGE_HOST_KEY: [
        (Q_MNEMOPHAGE_LONE_DBR, 43.0, 3.0, 71.0, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
    ],
    # M8 Ephialtes: PRIMARY SW deep back corner of the Dread Halls terminal reward vault. spec
    # local (15.9,3.2,34.7) = world (-1828.1,3.2,-13285.3). The R3 report called this "off-mesh
    # 7.2u" - that was the frame bug (it surveyed grid-local 15.9 = the wrong world point -1844.1;
    # the true world point -1828.1 is on-mesh). Corrected-frame survey: d=0.00u, clr@3.5
    # 100%/100%/100%, comp#1 = the spec-intended deepest-SW back corner per Will's "back corner"
    # order. (R3 shipped the bogus +11.7u NE nudge (22,45) to a shallower spot; reverted.)
    DREAD_HOST_KEY: [
        (Q_EPHIALTES_LONE_DBR, 15.9, 3.2, 34.7, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
    ],
}  # WIRED (build36): merged into INJECT_SPECS collision-guarded below (native AE v0f/v11 branch)


def rewrite_0x06_descriptors(blob, specs, level_name=''):
    """Rewrite existing 60-byte portal descriptors at the tail of a level's 0x06.

    The 0x06 portal list tail = [u32 64][u32 count][count x 60B descriptor], each
    descriptor = [exit 16][mouth 16][srcGUID 16][3x u32 trailer] (byte-decoded from the
    deployed map; the trailer = the door grid cell (x, layer, z) - Random09A precedent).
    Each spec matches ONE descriptor by its current (exit, mouth) ids and rewrites all
    60 bytes in place; the count and every other byte of the blob are unchanged.
    Fails loud unless every spec matches exactly once.
    """
    secs, magic = parse_blob_sections(blob)
    out_secs = []
    rewrote = 0
    for s in secs:
        if s['type'] != 0x06:
            out_secs.append(s)
            continue
        d6 = bytearray(s['data'])
        n = len(d6)
        found = None
        for count in range(1, 9):
            hdr_off = n - (8 + count * 60)
            if hdr_off < 0:
                break
            f0, c = struct.unpack_from('<2I', d6, hdr_off)
            if f0 == 64 and c == count:
                found = (hdr_off, count)
                break
        if found is None:
            raise ValueError(f'{level_name}: 0x06 has no [64][count] portal tail to rewrite')
        hdr_off, count = found
        for spec in specs:
            hits = []
            for i in range(count):
                off = hdr_off + 8 + i * 60
                if (bytes(d6[off:off + 16]) == spec['match_exit']
                        and bytes(d6[off + 16:off + 32]) == spec['match_mouth']):
                    hits.append(off)
            if len(hits) != 1:
                raise ValueError(
                    f'{level_name}: 0x06 descriptor match (exit {spec["match_exit"].hex()[:12]}..) '
                    f'found {len(hits)} times, expected exactly 1')
            off = hits[0]
            d6[off:off + 16] = spec['new_exit']
            d6[off + 16:off + 32] = spec['new_mouth']
            d6[off + 32:off + 48] = spec['new_src']
            struct.pack_into('<3I', d6, off + 48, *spec['new_trailer'])
            rewrote += 1
            print(f'    0x06 REWRITE {level_name}: desc@{off} -> exit={spec["new_exit"].hex()[:12]}.. '
                  f'mouth={spec["new_mouth"].hex()[:12]}.. src={spec["new_src"].hex()[:12]}.. '
                  f'cell={spec["new_trailer"]}')
        out_secs.append({'type': 0x06, 'data': bytes(d6)})
    if rewrote != len(specs):
        raise ValueError(f'{level_name}: rewrote {rewrote} 0x06 descriptors, expected {len(specs)}')
    return rebuild_blob(magic, out_secs)


def append_0x06_descriptors(blob, specs, level_name=''):
    """APPEND new 60-byte reciprocal-door descriptors to a level's 0x06 tail block.

    (rewrite_0x06_descriptors edits an existing descriptor in place with the count fixed;
    this GROWS the block. Needed for crypt_floor1, whose native block already has count=2,
    where the Uber return door is a THIRD descriptor - the append the older function cannot
    do; it also keys off f0==64 which is only the SIZE of a single-descriptor block.)

    The 0x06 GridSystem section = [u32 1][u32 2][u32 1][u32 payloadlen][payloadlen bytes of
    GridSystem body][descriptor tail block]. The tail block = [u32 marker=2][u32 size=
    4+count*60][u32 count][count x 60B descriptor] and ALWAYS ends at the section end; the
    grid header's payloadlen (int[3]) points at (block_start - 16) i.e. block_start ==
    16 + payloadlen, and EXCLUDES the descriptor tail, so appending descriptors leaves
    payloadlen untouched (byte-proven on crypt: payloadlen 19585, block@19601). Each 60B
    descriptor = [exit 16][mouth 16][srcGUID 16][doorX u32][doorY u32][doorZ u32] where
    doorX/doorZ are 0-based grid cells (floor(local/cellSize)) and doorY is the 0-based
    vertical LAYER index (layer 0 = lowest floor; tasks/wx21win4f.output). This mirrors the
    native cave/tomb two-way-door mechanism: the destination's reciprocal 0x06 descriptor +
    the host's 0x14 GridEntrance mouth build the paired portal, no landing entity needed
    (Random09A walk-tested precedent).

    Each spec: {'exit': 16B, 'mouth': 16B, 'src': 16B, 'cell': (dx, dy, dz)}. Bumps
    count += len(specs), size += len(specs)*60, appends the descriptor bytes at the section
    end (preserving the existing descriptors). Fails loud unless exactly one well-formed
    0x06 section is present, and refuses to append a descriptor whose exit id already exists.
    """
    secs, magic = parse_blob_sections(blob)
    out_secs = []
    appended = 0
    saw_06 = 0
    for s in secs:
        if s['type'] != 0x06:
            out_secs.append(s)
            continue
        saw_06 += 1
        d6 = bytes(s['data'])
        n = len(d6)
        if n < 16:
            raise ValueError(f'{level_name}: 0x06 too small ({n} B) for a descriptor tail')
        one, two, oneb, payloadlen = struct.unpack_from('<4I', d6, 0)
        if not (one == 1 and two == 2 and oneb == 1):
            raise ValueError(f'{level_name}: 0x06 header {(one, two, oneb)} != (1,2,1); '
                             f'not a GridSystem section, refusing to append')
        block_start = 16 + payloadlen
        if block_start + 12 > n:
            raise ValueError(f'{level_name}: 0x06 descriptor block start {block_start} '
                             f'past section end {n}')
        marker, size, count = struct.unpack_from('<3I', d6, block_start)
        if marker != 2:
            raise ValueError(f'{level_name}: 0x06 tail marker {marker} != 2 at {block_start}')
        if size != 4 + count * 60:
            raise ValueError(f'{level_name}: 0x06 tail size {size} != 4+count*60 '
                             f'({4 + count * 60}) for count={count}')
        if block_start + 12 + count * 60 != n:
            raise ValueError(f'{level_name}: 0x06 descriptor block does not end at section '
                             f'end (block_end {block_start + 12 + count * 60} != {n})')
        existing_exits = {bytes(d6[block_start + 12 + i * 60:block_start + 12 + i * 60 + 16])
                          for i in range(count)}
        new_bytes = bytearray()
        for spec in specs:
            ex, mo, sr = spec['exit'], spec['mouth'], spec['src']
            dx, dy, dz = spec['cell']
            if not (len(ex) == 16 and len(mo) == 16 and len(sr) == 16):
                raise ValueError(f'{level_name}: descriptor exit/mouth/src must be 16 bytes each')
            if ex in existing_exits:
                raise ValueError(f'{level_name}: 0x06 already has a descriptor with exit '
                                 f'{ex.hex()[:12]}..; refusing to append a duplicate')
            desc = ex + mo + sr + struct.pack('<3I', dx, dy, dz)
            assert len(desc) == 60
            new_bytes += desc
            existing_exits.add(ex)
            print(f'    0x06 APPEND {level_name}: exit={ex.hex()[:12]}.. mouth={mo.hex()[:12]}.. '
                  f'src={sr.hex()[:12]}.. cell=({dx},{dy},{dz}) (count {count}->{count + len(specs)})')
        new_count = count + len(specs)
        new_size = size + len(specs) * 60
        d6new = bytearray(d6)
        struct.pack_into('<3I', d6new, block_start, 2, new_size, new_count)
        d6new += new_bytes
        out_secs.append({'type': 0x06, 'data': bytes(d6new)})
        appended += len(specs)
    if saw_06 != 1:
        raise ValueError(f'{level_name}: expected exactly 1 0x06 section, found {saw_06}')
    if appended != len(specs):
        raise ValueError(f'{level_name}: appended {appended} descriptors, expected {len(specs)}')
    return rebuild_blob(magic, out_secs)


# ── DUISTER RETURN: wire the INERT RogueEncampment rift shrine (2026-07-08 wave) ────
# The Secret Place / Duister cluster has NO working return (its return GridEntrances are
# appended-host = never fire, see the native-door block above), and terrain levels have
# no 0x06 descriptor tail to repurpose. SV's DESIGNED return for these areas is the
# TeleportShrine (rift/portal-pad) network: GardenofMerchants ships teleportshrine_gom
# FULLY WIRED (0x05 inst[254] flags=1 uid e08e87ff.. + GROUPS record
# 'DRXShrineTeleport_Duister' cat 'TeleportShrine') - activating it joins the portal
# network = the way back out. RogueEncampment ships the SAME-CLASS shrine
# (teleportshrineorient01.dbr, Class StrategicMovementTeleportShrine, 0x05 inst[74]
# @ local (76,0,66)) but INERT: flags=0, no UniqueId, no GROUPS member (byte-verified
# vs SV upstream - SV itself never finished wiring it). Wire it by mirroring the Garden
# shrine's byte-shape exactly:
#   (1) 0x05: flags 0 -> 1 + append the 16-byte UniqueId (set_0x05_flags_uid);
#   (2) GROUPS: append a 1-member 'TeleportShrine' record (sub_count=2, the category
#       constant across all 10 native TeleportShrine records; member = uid(16) +
#       levelGUID(16) + pos(12) == the 0x05 pos; 20-byte tail = an opaque record-unique
#       id(16) + u32 0, mirroring the Garden record's tail shape).
# NO 0x14 (the Garden shrine has none). Engine tolerance for partial wiring is proven
# by the native dangling 'Scandia01_02' TeleportShrine record (unresolved level, no 0x05
# partner, ships in every build). Minted ids below are byte-verified collision-free
# against the whole merged world (recon_wave4_0708 + the doorshub gate re-checks).
ROGUE_ENCAMPMENT_KEY = 'xpack/levels/secret_place/rogueencampment.lvl'
ROGUE_ENCAMPMENT_GUID = bytes.fromhex('f31e50a12e45ca1dec8a328a9b5d87c5')
TELEPORTSHRINEORIENT01_DBR = b'records\\item\\shrines\\teleportshrineorient01.dbr'
DUISTER_SHRINE_POS = (76.00, 0.00, 66.00)   # the existing inert instance's exact 0x05 pos
DUISTER_SHRINE_UID = bytes.fromhex('feedcafe6100000000000000000000a1')   # minted, unique
DUISTER_SHRINE_TAIL16 = bytes.fromhex('feedcafe6200000000000000000000a2')  # minted, unique
DUISTER_SHRINE_GROUP_NAME = 'DRXShrineTeleport_RogueEncampment'
# level_key -> list of {dbr, from_xyz, uid}: set flags=1 + UniqueId on an EXISTING instance
FLAG_UID_SPECS = {
    ROGUE_ENCAMPMENT_KEY: [{
        'dbr': TELEPORTSHRINEORIENT01_DBR,
        'from_xyz': DUISTER_SHRINE_POS,
        'uid': DUISTER_SHRINE_UID,
    }],
}


def set_0x05_flags_uid(section_data, dbr, from_xyz, uid, base_size, level_name=''):
    """Set flags=1 + insert the 16-byte UniqueId on an EXISTING 0x05 instance.

    Walks the section flag-aware (record = base_size + 16 iff flags != 0), finds the
    single instance whose string-table dbr matches `dbr` (case/sep-insensitive) AND
    whose position is within 0.05u of from_xyz, asserts it currently has flags == 0,
    rewrites flags to 1 and inserts `uid` right after the 56-byte core (the byte-shape
    of every natively-flagged v0x0e record, e.g. the Garden shrine / HV01 fountain).
    Instance indices are unchanged (only byte offsets after the record shift).
    """
    assert len(uid) == 16
    want = bytes(dbr).replace(b'/', b'\\').lower()
    scount = struct.unpack_from('<I', section_data, 0)[0]
    pos = 4
    strings = []
    for _ in range(scount):
        slen = struct.unpack_from('<I', section_data, pos)[0]
        pos += 4
        strings.append(section_data[pos:pos + slen])
        pos += slen
    inst_count = struct.unpack_from('<I', section_data, pos)[0]
    pos += 4
    hits = []
    for i in range(inst_count):
        str_idx, = struct.unpack_from('<I', section_data, pos)
        x, y, z = struct.unpack_from('<3f', section_data, pos + 40)
        flags, = struct.unpack_from('<I', section_data, pos + 52)
        rec_size = base_size + (16 if flags != 0 else 0)
        sdbr = strings[str_idx].replace(b'/', b'\\').lower() if str_idx < len(strings) else b''
        if (sdbr == want and abs(x - from_xyz[0]) < 0.05 and abs(y - from_xyz[1]) < 0.05
                and abs(z - from_xyz[2]) < 0.05):
            hits.append((i, pos, flags))
        pos += rec_size
    if len(hits) != 1:
        raise ValueError(f'{level_name}: flags/uid target {dbr!r}@{from_xyz} matched '
                         f'{len(hits)} instances, expected exactly 1')
    i, rec_off, flags = hits[0]
    if flags != 0:
        raise ValueError(f'{level_name}: instance {i} already flagged ({flags}); refusing')
    out = bytearray(section_data)
    struct.pack_into('<I', out, rec_off + 52, 1)
    insert_at = rec_off + 56          # right after the 56-byte core (v0x0e flagged shape)
    out[insert_at:insert_at] = uid
    print(f'    FLAG+UID {level_name}: inst[{i}] {dbr.decode("ascii", "replace").split(chr(92))[-1]} '
          f'flags 0->1 uid={uid.hex()[:12]}..')
    return bytes(out)


def build_teleport_shrine_group_record():
    """The GROUPS record dict wiring the RogueEncampment shrine into the portal network.

    Mirrors the Garden shrine's record byte-shape exactly (measured: sub_count=2 like all
    10 native TeleportShrine records; 1 member = uid+levelGUID+pos(12); 20-byte tail =
    opaque unique id(16) + u32 0). Consumed by svaera_plus_portals step 2c via
    _rebuild_groups (same path as every other GROUPS record).
    """
    raw = (DUISTER_SHRINE_UID + ROGUE_ENCAMPMENT_GUID
           + struct.pack('<3f', *DUISTER_SHRINE_POS)
           + DUISTER_SHRINE_TAIL16 + struct.pack('<I', 0))
    assert len(raw) == 64
    return {'sub_count': 2, 'name': DUISTER_SHRINE_GROUP_NAME,
            'category': 'TeleportShrine', 'member_count': 1, 'raw_data': raw}

# --- B1: smoke/dark-cloud occult atmosphere over the entrance area (Will's ask) -----------
# SV dressed the cave-mouth "special area" (the Hades merchant = "the occultist") with an
# occult FX/light scene the merge DROPPED. These are ALL Class EffectEntity / light /
# Decoration / Tile (NO aggro), re-injected SV-faithfully at SV's EXACT local coords
# (HiddenValleyBorder04 is a shared level, NOT grid-shifted -> SV-local == merged-local).
# Byte-extracted from the SV upstream Border04 0x05 (recon_greece_occultist.py). All resolve
# in the built arz. flags=0, no 0x14 (SV places none for these).
FOG_OCCULT_FX01_DBR = b'records\\drxmap\\effects\\fog_occult_fx01.dbr'
OCCULTISTAURA_FX01_DBR = b'records\\drxmap\\effects\\occultistaura_fx01.dbr'
PIT_FX01_DBR = b'records\\drxmap\\effects\\pit_fx01.dbr'
LIGHT_10M_DYN_PURPLE_DBR = b'records\\xpack\\effects\\lights\\dynamic\\10mlight_dyn_purple.dbr'
LIGHT_10M_DYN_RED_DBR = b'records\\xpack\\effects\\lights\\dynamic\\10mlight_dyn_red.dbr'
LIGHT_5M_STAT_BLUE_DBR = b'records\\lights\\staticlights\\5mlight_stat_blue.dbr'
MC_HADES_WOODPYRE01_DBR = b'records\\xpack\\sceneryhades\\structure\\camp\\monstercamp\\mc_hades_woodpyre01.dbr'
MC_HADES_ANOURANFIREPIT02_DBR = b'records\\xpack\\sceneryhades\\structure\\camp\\monstercamp\\mc_hades_anouranfirepit02.dbr'
DRXMAP_TOTEM_DBR = b'records\\drxmap\\dress2\\totem.dbr'
FX_DISCIPLE_AURA_01_DBR = b'records\\drxcreatures\\bloodwitch\\skills\\skilleffects\\fx_disciple_aura_eyechantment01.dbr'
FX_DISCIPLE_AURA_02_DBR = b'records\\drxcreatures\\bloodwitch\\skills\\skilleffects\\fx_disciple_aura_eyechantment02.dbr'
# SV's EXACT non-identity rotations for the props it orients (byte-verified from SV's own
# Border04 0x05). Most B1 records are identity; these three physical props are angled, so
# carrying their exact matrix makes the injected record byte-shape identical to SV's placement
# (a firepit/pyre and two cult totems face specific ways in the scene).
WOODPYRE_ROT = (0.224837, 0.0, -0.974396, 0.0, 1.0, 0.0, 0.974396, 0.0, 0.224837)
TOTEM_ROT_A = (-0.329537, 0.0, -0.944143, 0.0, 1.0, 0.0, 0.944143, 0.0, -0.329537)   # @ (40.24,12.34)
TOTEM_ROT_B = (-0.372804, 0.0, -0.92791, 0.0, 1.0, 0.0, 0.92791, 0.0, -0.372804)     # @ (46.46,29.55)
LIGHT_PURPLE_ROT = (0.99995, 0.0, 0.010048, 0.0, 1.0, 0.0, -0.010048, 0.0, 0.99995)  # @ (47.03,29.58)

# --- B2: exploding sprites near the occultist (Will's ask), aggro-safe standoff -----------
# Mirror the WORKING Greece pit-sprite cluster (SV DelphiLowlands02): a t1_pitspawner (the
# emitter) + a few t1_lildude around a pit_fx. Class Monster (aggro) - so the >=18u standoff
# from the occultist merchant is load-bearing (Greece's working merchant->sprite standoff is
# 10.8-11.6u; 18u has a >6u margin, and the sprites sit on the FAR/north side of the occultist
# so the player approaching from the south fountain never crosses them). SV uses IDENTITY
# rotation for these (byte-verified). All resolve in the arz. flags=0, no 0x14.
T1_LILDUDE_01_DBR = b'records\\drxmap\\pitsprites\\t1_lildude_01.dbr'
T1_LILDUDE_02_DBR = b'records\\drxmap\\pitsprites\\t1_lildude_02.dbr'
T1_PITSPAWNER_01_DBR = b'records\\drxmap\\pitsprites\\t1_pitspawner_01.dbr'
T1_PITSPAWNER_02_DBR = b'records\\drxmap\\pitsprites\\t1_pitspawner_02.dbr'

# --- B-SMOKE-1 (2026-07-08): the REST of SV's dropped Delphi occultist-region scene ------
# recon_wave4_0708 delphi: SV-vs-merged 0x05 diff on the three shared Delphi levels
# (corners byte-identical, so SV-local == merged-local). The C4 wave restored only the
# ATMOSPHERE emitters; SVAERA also dropped the pit-sprite MONSTERS, the caged-sprite
# props, and the scene's sound objects. All restored at SV's exact float32 coords + rots
# below. Resolution byte-verified: the 13 drxmap records in the built SoulvizierClassic
# .arz, the 2 base-game sound objects in database.arz. flags=0, no 0x14 (SV places none).
T1_LILDUDE_DRESS_01_DBR = b'records\\drxmap\\dress\\t1_lildude_01.dbr'   # caged-sprite props
T1_LILDUDE_DRESS_02_DBR = b'records\\drxmap\\dress\\t1_lildude_02.dbr'   # (Decoration, no aggro)
T1_LILDUDE_DRESS_03_DBR = b'records\\drxmap\\dress\\t1_lildude_03.dbr'
VITSTAFF_01_DBR = b'records\\drxmap\\dress\\vitstaff_01.dbr'
VITSTAFF_05_DBR = b'records\\drxmap\\dress\\vitstaff_05.dbr'
CAGE_SMALL_DBR = b'records\\drxmap\\dress\\cage_small.dbr'
CAGE_MEDIUM_DBR = b'records\\drxmap\\dress\\cage_medium.dbr'
CAGE_BINDING_FX01_DBR = b'records\\drxmap\\effects\\cage_binding_fx01.dbr'
SOUNDOBJECT_DEMONCAGE_DBR = b'records\\drxmap\\sounds\\soundobject_demoncagebindingloop.dbr'
SOUNDOBJECT_CAGEGLOW_DBR = b'records\\xpack\\sounds\\soundobjects\\soundobject_cageglow.dbr'
BIGOBSIDIAN_DBR = b'records\\sounds\\soundobjects\\bigobsidian.dbr'

# =====================================================================================
# ============  DOORS + TEST HUB + BUILD24/25 FEEDBACK WAVE (this session) =============
# =====================================================================================
# Mirrors the Sparta machinery verbatim (docs/DOORS_HUB_LOG.md). Every new cross-level
# portal reuses portal_olympianarena1.dbr (GridEntranceDynamic, opened globally by the
# EXISTING bossarena.qst Condition_OnLevelLoad -> Action_OpenDynGridEntrance by record
# name) + portal_olympianarena2.dbr (GridExitOneWay landing), each instance carrying its
# OWN 48-byte 0x14 binding: entrance = mouth+exit+dest, landing = mouth(==entrance.exit)+
# zeros(32). NO Quests.arc change, NO 0x06, NO new records - same constraint/price as
# Sparta (portals render with the Olympian-arena mesh). All UIDs minted map-unique
# (collision-checked vs 157,548 known map UIDs, tools/debug/plan_doors_hub.py).

# --- C2/C4 atmosphere records (new DBR constants; existing ones reused above) ---------
# C4 restores 21 SV-dropped atmosphere emitters at SV's EXACT float32 coords + rotations
# (byte-shape identical to SV's own placement). C2 adds the Hades firepit "volcano bowl"
# at the sprite spawner. All Class EffectEntity/light/Decoration/Tile (NO aggro), flags=0,
# no 0x14 (SV places none). SV corners == shipped corners for HV01+Delphi (verified), so
# SV-local == merged-local. Coords + rotations extracted via extract_c4_atmosphere.py.
MC_HADES_ANOURANFIREPIT03_DBR = b'records\\xpack\\sceneryhades\\structure\\camp\\monstercamp\\mc_hades_anouranfirepit03.dbr'
MC_HADES_ANOURANFIREPITMD01_DBR = b'records\\xpack\\sceneryhades\\structure\\camp\\monstercamp\\mc_hades_anouranfirepitmd01.dbr'
PIT_FX02_DBR = b'records\\drxmap\\effects\\pit_fx02.dbr'
BUGCLOUD_SMALLFX_DBR = b'records\\xpack\\effects\\particles\\environment\\bugcloud_smallfx.dbr'
MERCHANT_DELPHI_OCCULTTENT01_DBR = b'records\\drxmap\\dress\\merchant_delphi_occulttent01.dbr'
LIGHT_5M_DYN_ORANGE_DBR = b'records\\lights\\dynamiclights\\5mlight_dyn_orange.dbr'
LIGHT_10M_SIMPLE_RED_DBR = b'records\\xpack\\effects\\lights\\simple\\10mlight_simple_red.dbr'
LIGHT_15M_SIMPLE_PURPLE_DBR = b'records\\xpack\\effects\\lights\\simple\\15mlight_simple_purple.dbr'
LIGHT_10M_STATNL_BLUE_DBR = b'records\\lights\\nightlights\\static nightlight\\10mlight_statnl_blue.dbr'
LIGHT_5M_DYN_GREEN_DBR = b'records\\lights\\dynamiclights\\5mlight_dyn_green.dbr'
CAMPFIRE01_DBR = b'records\\sceneryorient\\structure\\camps\\setdress\\campfire01.dbr'
# SV-exact non-identity rotations (byte-verified via extract_c4_atmosphere.py). Records not
# listed here use IDENTITY (SV places them identity).
HV01_TOTEM_ROT = (-4.371138828673793e-08, 0.0, -1.0, 0.0, 1.0, 0.0, 1.0, 0.0, -4.371138828673793e-08)  # both HV01 totems
HV01_5M_DYN_ORANGE_ROT = (0.9999160766601562, 0.0, 0.012954838573932648, 0.0, 1.0, 0.0, -0.012954838573932648, 0.0, 0.9999160766601562)
DELPHI_OCCULTTENT_ROT = (0.7340660691261292, 0.0, -0.6790779232978821, 0.0, 1.0, 0.0, 0.6790779232978821, 0.0, 0.7340660691261292)
DELPHI_STATNL_BLUE_ROT = (0.9988024234771729, 0.0, 0.04892538860440254, 0.0, 1.0, 0.0, -0.04892538860440254, 0.0, 0.9988024234771729)
DELPHI_5M_DYN_GREEN_ROT = (0.8890920281410217, 0.0, 0.4577282667160034, 0.0, 1.0, 0.0, -0.4577282667160034, 0.0, 0.8890920281410217)
DELPHI_ANOURANFIREPIT03_ROT = (0.7082276344299316, 0.0, -0.7059841156005859, 0.0, 1.0, 0.0, 0.7059841156005859, 0.0, 0.7082276344299316)

# --- A1 GARDEN OF MERCHANTS door (canonical + hub) : HV01 <-> GardenofMerchants ------
# HOST = HiddenValley01 (v0x11 shared), portal beside the moved Super-Caravan at HV01 north
# (16u E of caravan_silkroad, >=15u from fountain/caravan/hostiles). DEST = GardenofMerchants
# (v0x0e SV-only); the landing sits in the caravan_rhodes COMPONENT (comp #1, 112,172 cells -
# NOT the main comp) so the player arrives IN the merchant hub. Unlocks the caravan_rhodes
# Super-Caravan region. G1<->G4 sep 14.4u; G2<->G3 sep 12u.
GARDEN_gM1 = bytes.fromhex('a8605b3120dc06df34ac0734e531052e')  # in mouth
GARDEN_gX1 = bytes.fromhex('f9f0d0051580d19a9680a9c62c617f23')  # in exit (== G2 landing mouth)
GARDEN_gM2 = bytes.fromhex('8f83a7e17a10749081b657243a7eb98b')  # return mouth
GARDEN_gX2 = bytes.fromhex('4aecb0aa270c1563687f67c52281d6cc')  # return exit (== G4 landing mouth)
GOM_GUID = bytes.fromhex('15f9d3d7214d56d42a2ac6abd6114d78')          # GardenofMerchants merged GUID
HV01_GUID = bytes.fromhex('ce93e328b14a5eba7ab5be8e623fa215')         # HiddenValley01 merged GUID
GARDEN_G1_0x14 = GARDEN_gM1 + GARDEN_gX1 + GOM_GUID   # HV01 entrance -> GoM
GARDEN_G2_0x14 = GARDEN_gX1 + b'\x00' * 32            # GoM landing (inbound)
GARDEN_G3_0x14 = GARDEN_gM2 + GARDEN_gX2 + HV01_GUID  # GoM entrance -> HV01 (return)
GARDEN_G4_0x14 = GARDEN_gX2 + b'\x00' * 32            # HV01 landing (return)
for _p in (GARDEN_G1_0x14, GARDEN_G2_0x14, GARDEN_G3_0x14, GARDEN_G4_0x14):
    assert len(_p) == 48

# --- N1 (build31): SECOND Garden entrance from HELOS (first town, Act 1 Greece) ------------
# Will: "the portal to Duister [= Garden of Merchants] should be put in the first town".
# ADDITIVE: the HV01 camp entrance (G1-G4) stays; Helos gets its OWN pair with freshly minted
# UIDs (the hub lesson: every cross-level pair uses its own UIDs, zero cross-talk with
# A1/A2/Sparta/hub pairs; both minted UIDs verified ABSENT from both shipped maps). H1 =
# entrance in startingfarmland06d (Helos village, v0x11 shared -> step-6/7 x14_payload append)
# + co-located map_portal_aura swirl (M4 recipe: static GridEntrance is otherwise near-
# invisible). H2 = inbound landing in the Garden's caravan_rhodes component near G2.
# RETURN IS THE EXISTING G3 SHRINE -> HV01 (coordinator decision build31). ⚠️ Flagged: an
# Act-1 player who enters from Helos and takes the return shrine lands in HiddenValley01
# (Act 3 Orient) - walk-test-gated; if Will dislikes it, add a hub-style second return pair
# (Garden -> Helos) with 2 more minted UIDs.
HELOS_hM1 = bytes.fromhex('f2f9cbfb79166ec992e1281b2fd25207')  # Helos entrance mouth
HELOS_hX1 = bytes.fromhex('1460bdc60254e065833db5ec4f502128')  # Helos entrance exit (== H2 landing mouth)
HELOS_H1_0x14 = HELOS_hM1 + HELOS_hX1 + GOM_GUID   # Helos entrance -> GoM
HELOS_H2_0x14 = HELOS_hX1 + b'\x00' * 32           # GoM landing (inbound from Helos)
for _p in (HELOS_H1_0x14, HELOS_H2_0x14):
    assert len(_p) == 48

# --- N1b (build31): Garden -> HELOS RETURN pair (coordinator-approved stranding fix) --------
# The Garden's classic G3 return shrine sends EVERYONE to HiddenValley01 (Act 3) - stranding
# an Act-1 player who entered from Helos. N1b adds a SECOND, independent return: R1 = return
# entrance IN the Garden near the H2 landing ("the way you came in is the way back"), R2 =
# landing in the Helos portal plaza offset from H1. G3 stays untouched for Act-3 players.
# Fresh minted UID pair (verified absent from both shipped maps, scratchpad/n1b_recon.py).
# HELOS_GUID = startingfarmland06d's merged level-index GUID, extracted with the SAME method
# that reproduces GOM_GUID/HV01_GUID byte-exactly (validated against GOM in n1b_recon.py).
HELOS_GUID = bytes.fromhex('5d8f9b96c54ca73098922e8463d1d665')  # startingfarmland06d merged GUID
HELOS_rM1 = bytes.fromhex('c6826e2998fff966f6318064f4f5277c')  # Garden return-entrance mouth
HELOS_rX1 = bytes.fromhex('9570d357607d0ffcbb99eb7d5e4274f0')  # return exit (== R2 landing mouth)
HELOS_R1_0x14 = HELOS_rM1 + HELOS_rX1 + HELOS_GUID  # GoM return entrance -> Helos
HELOS_R2_0x14 = HELOS_rX1 + b'\x00' * 32            # Helos landing (return from GoM)
for _p in (HELOS_R1_0x14, HELOS_R2_0x14):
    assert len(_p) == 48

# --- A2 SECRET PLACE door (canonical + hub) : rhodes_secretvista_01 <-> darkforestenter -
# HOST = rhodes_secretvista_01 (v0x0f shared) - a scenic Rhodes overlook (thematic "hidden
# secret place" host, same Rhodes region as the Secret Place cluster, ZERO hostiles); portal
# at a tucked-away east-edge nook (17.8u from any decor). DEST = darkforestenter (v0x0e
# SV-only) = the 11-level Secret Place cluster's ENTRY (SV_AREAS_CAMPAIGN Wave 3a).
SECRET_sM1 = bytes.fromhex('bab0519fdc5f79a364f3b3eb492927ac')
SECRET_sX1 = bytes.fromhex('f6474fb1f4ba46d01a4deefaebba1480')
SECRET_sM2 = bytes.fromhex('46d2a8ba61db650f148f3944f56f4923')
SECRET_sX2 = bytes.fromhex('c513d76bc21a59cacdc21296f99e0862')
DFE_GUID = bytes.fromhex('1397c8e754491051bcd1be9cc4dd092f')            # darkforestenter merged GUID
SECRETVISTA01_GUID = bytes.fromhex('88b842ba1a4329176dc2a995c33eda29')  # rhodes_secretvista_01 merged GUID
SECRET_S1_0x14 = SECRET_sM1 + SECRET_sX1 + DFE_GUID           # vista entrance -> DFE
SECRET_S2_0x14 = SECRET_sX1 + b'\x00' * 32                    # DFE landing (inbound)
SECRET_S3_0x14 = SECRET_sM2 + SECRET_sX2 + SECRETVISTA01_GUID # DFE entrance -> vista (return)
SECRET_S4_0x14 = SECRET_sX2 + b'\x00' * 32                    # vista landing (return)
for _p in (SECRET_S1_0x14, SECRET_S2_0x14, SECRET_S3_0x14, SECRET_S4_0x14):
    assert len(_p) == 48

# --- TEST HUB (SVC_TEST_HUB=1 only) : blood-cave Random09A -> 5 destinations ----------
# 5 one-way pairs from inside Random09A (blood cave, near the mouth/entry, on-mesh, no combat
# proxies inside), each with a reciprocal RETURN to the cave. Each destination gets 4 UIDs
# (in_mouth,in_exit,ret_mouth,ret_exit). Random09A is the blob-swapped SV-only doorway cave
# (v0x0e; its merged GUID d840e7ae.. is the KEPT AE GUID). Destinations: maze03 (v0x0f shared),
# murderbossroom / SpartaCryptLevel2 / darkforestenter / GardenofMerchants (v0x0e SV-only).
RANDOM09A_GUID = bytes.fromhex('d840e7ae4a42c504453f13a47940bc55')
MAZE03_GUID = bytes.fromhex('cdef89ae834a4adf1214609306708c02')
MURDERBOSSROOM_GUID = bytes.fromhex('2817751af24828502c9d7ea5f0a5c6ab')
SC2_HUB_GUID = bytes.fromhex('797c78594040cba419340c990e6903c4')  # SpartaCryptLevel2 (same as SC2_MERGED_GUID)
# Per-destination minted UID quads (in_mouth, in_exit, ret_mouth, ret_exit):
HUB_UIDS = {
    'maze03':            ('91ccd4fb07261e482d01b72fde2cf4c5', 'e2b46e1a433c791d83e212ca2b99c97c',
                          '2394fc8c0de5045a1ae4679949e650ce', 'ead10570d4b66b6d294801bd2a903d24'),
    'murderbossroom':    ('8d29a9068e3853bf1ec9de68891b68dd', '114b77af27717a5da706fc5f5bd340a5',
                          '37e8f289cfb58dd4452b85f87c5e57e7', '2d0279f4ebf5a29cf894b91bdc878417'),
    'spartacryptlevel2': ('e9d6531602f1a9ccbe8a47089628d8cb', '249305cf8e7a4e0204fa5a55339d14a2',
                          '47a5bb8cdd2268158eb9eca40fde05ed', '63fdac4e140eab8b4c7a2b0650e4a1db'),
    'darkforestenter':   ('3a00c5d5108198c8d8372bd6fa4b1fef', 'f690898bbe4395f1019189477b9ce1dd',
                          '887a8bb55a8f182d0e58b0feb6cac3c0', '6e4614c6bf42e026d52378c8da3885f2'),
    'gardenofmerchants': ('0ad82f095231c69a7f47ca205c46b76f', '957fb0b7be921d6b3770f287d29a9bb4',
                          '1e404b95c182f8988d1bd701b87ba980', '540455d4336172ea9e746eedc7e84407'),
}
HUB_DEST_GUID = {
    'maze03': MAZE03_GUID, 'murderbossroom': MURDERBOSSROOM_GUID,
    'spartacryptlevel2': SC2_HUB_GUID, 'darkforestenter': DFE_GUID, 'gardenofmerchants': GOM_GUID,
}


def _hub_pair_0x14(dest_key):
    """Return (cave_entrance_0x14, dest_landing_0x14, dest_ret_entrance_0x14, cave_ret_landing_0x14)
    for one hub destination, mirroring the A1/Sparta shape."""
    im, ix, rm, rx = (bytes.fromhex(h) for h in HUB_UIDS[dest_key])
    dg = HUB_DEST_GUID[dest_key]
    cave_entrance = im + ix + dg               # in the cave, -> dest
    dest_landing = ix + b'\x00' * 32           # in dest, inbound landing (mouth == cave entrance exit)
    dest_ret_entrance = rm + rx + RANDOM09A_GUID  # in dest, -> cave (return)
    cave_ret_landing = rx + b'\x00' * 32       # in cave, return landing
    for _p in (cave_entrance, dest_landing, dest_ret_entrance, cave_ret_landing):
        assert len(_p) == 48
    return cave_entrance, dest_landing, dest_ret_entrance, cave_ret_landing


# --- P0 (Will 2026-07-12): the canonical NPC-dialog RETURN traveler --------------------------
# svc_testhub_return.dbr is a Model C boat-dialog NPC (2-port menu: Helos + Blood Cave) cloned
# from the proven Knossos boatman. apply_svc_patches._create_testhub_portal_npcs adds the RECORD
# to the arz UNCONDITIONALLY, and build_quest_files._add_testhub_portal_travel adds its
# Action_BoatDialog to sv_commonmechanics.qst UNCONDITIONALLY - both already ship in the LIVE
# build36 arz/Quests, INERT only because the canonical map never PLACED the NPC. This P0 removes
# every walk-through portal and PROMOTES this return NPC into the SV-only dest areas (Garden,
# Secret Place, Uber, Sparta) so every area a player can reach via the Helos portal-master has a
# talk-to-travel way back - NO map/arz/Quests rebuild coupling beyond the already-shipped records.
# (Same record path as SVC_TESTHUB_RETURN_DBR, defined for the TESTHUB rig further below.)
SVC_RETURN_NPC_DBR = b'records\\quests\\svc_testhub_return.dbr'

# Injection specs: level name key -> list of specs (see INJECTION-SPEC FORMAT above).
# DelphiLowlands04: merchant tent at (12.88, 9.98, 2.52), quest NPC at (14.03, 10.16, 6.15)
# crypt_floor1: minotaur statue at (139.73, 11.84, 212.30), existing arena portal at (139.94, 10.01, 231.94)
# HiddenValley01: cave entrance at (14.0, 18.0, 26.0), POI at (15.84, 18.0, 26.58)
# BC_initialpathway: SV blood cave entrance level
INJECT_SPECS = {
    # Delphi NPC injection REMOVED - corrupts v0x11 blob, crashes game on world streaming
    # (LEGACY note: that early failure used the old generate_default_0x14 path; the LIVE
    # v11 injector [inject_into_0x05_v11, step 6/7] is proven by the HV01 caravan/fountain
    # + the Helos H1/R2 portals, all v0x11 walk-verified.)
    'levels/world/uberdungeon/crypt_floor1.lvl': [
        (RETURN_NPC_DBR, 140.0, 10.0, 215.0),
    ],
    # M12/Q3 HERALD (build31g): the Olympus->Rhodes continuation NPC ("Hermes the herald"),
    # the Model-C boat-dialog teleporter that replaces the dead engine FixedItemTeleport as
    # the guaranteed post-Typhon path to Rhodes/Immortal Throne. Record + boat-dialog quest
    # shipped by the DB/Quests lane (Q3 36a6212: arz bd6ae869 +1 record cloned from the
    # Knossos boatman; Quests 3db3764c Action_BoatDialog -> world (700,41,-6466) = the base
    # game's own Rhodes arrival target, navmesh-verified). SPOT local (305.80,90.20,490.80)
    # = world (1155.80,90.20,-3190.20): 4.0u +Z of the locked xq00 portal [41] on the Typhon
    # plateau - navmesh-verified exact cell, floor-matched Y, 100% 3u clearance, connected
    # to the portal cell, zero entities within 18u (see the M12 spec block for the full
    # evidence). v0x11 shared level -> the proven step-6/7 v11 injection; flags=0, identity
    # rot, no 0x14 (Starting_PortalMan NPC byte-shape).
    'levels/world/olympus/olympusfinal02.lvl': [
        OLYMPUS_RHODES_NPC_SPEC,
    ],
    # Widow Letter questline (WAVE E): restore the 3 SV entities the widowletter.qst
    # conditions reference. widow_ling = the NPC (Condition_ConversationStart),
    # trg_foundzhidan = the trigger volume (Condition_EnterVolume), and
    # location_treasurechest = the chest location. Coords are SV-LOCAL, byte-exact from
    # the SV upstream RoadToTown03A 0x05 (this shared level is NOT grid-shifted). All
    # three are flags=0 with NO 0x14 entry in SV (measured), so no 0x14 is appended.
    # Coords below are the EXACT SV 0.98i float32 values (full precision, so the packed
    # bytes are byte-identical to SV's own placement - gate F1 parity to zero), extracted
    # via tools/debug/extract_sv_coords.py.
    'levels/world/orient/greatwall/roadtotown03a.lvl': [
        (WIDOW_LING_NPC_DBR, 66.50193786621094, -63.34101867675781, 50.108333587646484,
         {'rot': WIDOW_LING_ROT}),
        (TRG_FOUNDZHIDAN_DBR, 77.0739517211914, -63.86141586303711, 61.606048583984375),
        (LOCATION_TREASURECHEST_DBR, 27.196889877319336, -63.62507247924805, 34.70340347290039),
    ],
    # Rebirth Fountain + Super-Caravan - MOVED to the occultist's side (B3, Will's ask).
    # Will: the beastman swarm proxies spawn-camp and kill players respawning at the OLD spot
    # (the nearest ag_beastman_neanderthal_02t proxy was 9.1u from the old fountain). The fix
    # moves BOTH the respawn fountain and the caravan NORTH to HV01's north end (the occultist
    # side, adjacent to the HiddenValleyBorder04 merchant/occultist scene), 100+u from every
    # hostile spawn proxy and on the largest walkable component. This is a MOVE (the old coord
    # is simply changed, so the old placement is gone).
    #   4 HV01 hostiles (NOT touched): ag_beastman_neanderthal_02t/02n/03t + encact3.
    #   New fountain HV01-local (35.70,17.60,143.10) world (-98.3,-102.4,2317.1): 100.5u from
    #     the nearest hostile (was 9.1u), 9.2u from the occultist merchant, openNbr 8/8.
    #   New caravan  HV01-local (41.70,17.80,143.10) world (-92.3,-102.2,2317.1): 6.0u E of the
    #     new fountain, 100.9u from hostiles, openNbr 8/8. (tools/debug/plan_b_final.py)
    # The fountain KEEPS flags=1 + the SV UniqueId (feeb4bc6...) - the Shrine_Respawn_Orient
    # GROUPS member is keyed by that UniqueId. CORRECTION (this session, C1): the GROUPS member is
    # NOT position-independent - it carries a POSITION triplet (UID+levelGUID+pos) and the engine
    # RESPAWNS the player at THAT position, not the 0x05 instance. Moving the 0x05 alone (build24)
    # left the GROUPS position STALE -> the player kept respawning at the old spot (Will's report).
    # The fix is patch_respawn_group_position() in svaera_plus_portals.py step 2b, which rewrites the
    # GROUPS member pos to match this 0x05 coord (native-shrine parity). Y = walkable floor (17.6).
    # The caravan keeps its native rot + 12-byte 0x14 (2,0,1).
    'levels/world/orient/silkroad/hiddenvalley01.lvl': [
        (RESPAWNTEMPLEORIENT01_DBR, 35.70, 17.60, 143.10,
         {'flags': 1, 'uniqueid': RESPAWNTEMPLEORIENT01_UNIQUEID}),
        (CARAVAN_SILKROAD_DBR, 41.70, 17.80, 143.10,
         {'rot': CARAVAN_SILKROAD_ROT, 'x14_payload': CARAVAN_SILKROAD_0x14}),
        # B1 atmosphere over the NEW respawn area (a couple of occult emitters so the moved
        # respawn portal reads as the atmospheric entrance too). EffectEntity/light = no aggro,
        # flags=0, no 0x14. Placed a few u around the new fountain, off the walk line.
        (LIGHT_10M_DYN_PURPLE_DBR, 33.5, 17.6, 145.0),
        (LIGHT_10M_DYN_RED_DBR, 38.0, 17.8, 145.0),
        (FOG_OCCULT_FX01_DBR, 35.7, 17.6, 146.5),
        # --- C4 (this session): restore the 6 SV-dropped HV01 atmosphere emitters at SV's
        # EXACT float32 coords + rotations (byte-shape identical to SV's own placement). SV had
        # FAR MORE entrance atmosphere than shipped; build24 restored only the Border04 emitters.
        # These are the HV01 surface totems + campfire + coloured lights SV placed and the merge
        # dropped (extract_c4_atmosphere.py). flags=0, no 0x14. Pure visual (EffectEntity/light/
        # Decoration) - no aggro, no on-mesh requirement (authored heights).
        (DRXMAP_TOTEM_DBR, 65.0, 12.004941940307617, 106.0, {'rot': HV01_TOTEM_ROT}),
        (DRXMAP_TOTEM_DBR, 65.0, 12.004964828491211, 98.0, {'rot': HV01_TOTEM_ROT}),
        # ROUND-2 (vet fix): SV placed 2x 10mlight_dyn_purple + 2x 10mlight_dyn_red as the
        # occult UNDER-LIGHTING for each of the 2 HV01 totems above (SV-098i HV01: ~0.3-0.5u XZ /
        # ~4u ABOVE each totem, flags=0, IDENTITY rot - byte-verified independently via
        # verify_c4_hv01_totemlights.py). Round-1 omitted these (the extract TARGETS list did not
        # include the dyn_purple/dyn_red substrings), so the restored totems appeared WITHOUT their
        # SV purple/red under-glow. These are the SEPARATE totem lights, NOT the B1 new-fountain
        # purple/red at local ~(33.5/38.0,145) ~50u away. Pure visual (light, no aggro/0x14/mesh).
        # Coords are SV's exact float32; identity rot -> no rot override (SV places them identity).
        (LIGHT_10M_DYN_PURPLE_DBR, 65.4732666015625, 16.431617736816406, 106.04359436035156),
        (LIGHT_10M_DYN_PURPLE_DBR, 65.3399887084961, 16.19445037841797, 98.02886962890625),
        (LIGHT_10M_DYN_RED_DBR, 65.44312286376953, 16.418643951416016, 106.00531005859375),
        (LIGHT_10M_DYN_RED_DBR, 65.39828491210938, 16.303573608398438, 98.03968811035156),
        (LIGHT_15M_SIMPLE_PURPLE_DBR, 45.061309814453125, 29.081031799316406, 102.41687774658203),
        (CAMPFIRE01_DBR, 38.722877502441406, 15.005194664001465, 89.65540313720703),
        (LIGHT_5M_DYN_ORANGE_DBR, 38.88533020019531, 15.425609588623047, 90.27568817138672,
         {'rot': HV01_5M_DYN_ORANGE_ROT}),
        (LIGHT_10M_SIMPLE_RED_DBR, 46.9508056640625, 25.032676696777344, 112.49130249023438),
        # --- P0 WALK-THROUGH-PORTAL REMOVAL (Will 2026-07-12): the A1 Garden-of-Merchants
        # HV01 host door (G1 GridEntrance walk-through entrance + its map_portal_aura swirl +
        # the G4 return landing) is REMOVED. Will's TRAVEL LAW: NO walk-through/proximity
        # teleport anywhere we author - the ONLY approved travel is the proven NPC boat-dialog
        # (talk -> confirm). The Garden is now reached ONLY via the Helos portal-master NPC
        # (PORTAL_MASTER_SPEC, canonical) and left via the in-Garden svc_testhub_return NPC
        # (promoted to canonical below) or the SV-wired teleportshrine_gom rift. The
        # GARDEN_G1_0x14/GARDEN_G4_0x14 constants remain defined (unused) for history.
    ],
    # Static Widow Letter (BUG 2): finalletter placed at the location_letterdrop spot so it
    # is physically present for ALL characters (the quest spawn is neutralized in
    # build_quest_files.py to prevent a duplicate). SV-only v0x0e -> inject_into_0x05 (56 B),
    # flags=0, no 0x14. Local = location_letterdrop's exact SV-local coord (on-mesh 0.10u).
    'levels/world/xbloodcave/drxfirstxistion_connection.lvl': [
        (FINALLETTER_DBR, 32.459, 10.005, 17.593),
        # A1 (build36 CONVERGENCE): the Enslaver warband set-piece proxy (see the
        # EN_WARBAND_SPEC block above for the full survey evidence). ONE proxy, flat floor
        # (localY 10.0), ~26.6u from the finalletter above; SV-only v0e inject, flags=0,
        # no 0x14, exemplar rot. COUPLED SHIP with the arz's q_enslaver_warband records.
        EN_WARBAND_SPEC,
        # M15 (2026-07-09, Will mechanism change): the standalone ~50% parchment Toxeus proxy
        # (q_bloodtoxeus_lone_50 @ the finalletter's exact coords, the M5' build30 placement -
        # byte-verified d=0.0u ON the Tattered Parchment) is REMOVED. New mechanism = the DB
        # lane adds um_bloodtoxeus_99 at 50% to the pool of the 'little demon guys' group ON
        # the parchment: records\drxmap\proxy\demon_01_cluster.dbr, THIS level inst [25] @
        # local (37.16,10.01,20.46), 5.5u from the letter. ⚠️ demon_01_cluster is placed 30x
        # across the blood cave (24x drxFirstRoom, 6x drxBC2, 1x here) - the DB lane MUST
        # CLONE the proxy+pool (never edit the shared pool in place, or Toxeus rolls 50% at
        # all 30 spawn points); the map then repoints ONLY inst [25] to the clone (de-place
        # by dbr in this level [single instance here] + re-inject the clone at the exact
        # original bytes: pos (37.158714,10.005000,20.461723), identity rot, flags=1,
        # uniqueid 00ec9e28d14b2ca6f287fb8ed314ffe9 [verified NOT GROUPS-bound], no 0x14).
        # Keeping the standalone alongside the group-add = two independent 50% rolls = 25%
        # double-Toxeus (the old bug reborn) - hence the removal. ⚠️ COUPLED SHIP with the
        # DB lane's arz. History: M5' spec kept in git (build31e and earlier).
    ],
    # HiddenValleyBorder04 = the cave-mouth "occultist" scene (the Hades merchant
    # Merchant_HiddenValley_General + wagon, which SV dressed with occult FX). The merge kept
    # SVAERA's copy and DROPPED all the SV occult dressing. This block restores:
    #   - the Hades merchant WAGON (WAVE A, already shipped): the "caravan" dressing at the
    #     border. Plain Decoration, flags=0, no 0x14.
    #   - B1: the smoke/dark-cloud OCCULT ATMOSPHERE Will asked for (fog/aura/pit + coloured
    #     lights + firepit/pyre + totems + disciple aura). ALL Class EffectEntity/light/
    #     Decoration/Tile (NO aggro). SV-LOCAL coords are byte-exact from SV's own Border04
    #     0x05 (NOT grid-shifted -> SV-local == merged-local). flags=0, no 0x14 (SV places none).
    #   - B2: the exploding pit-sprites, mirroring the WORKING Greece cluster (DelphiLowlands02:
    #     a t1_pitspawner + t1_lildude around a pit_fx). Class Monster (aggro) -> placed on the
    #     FAR/north side of the occultist (cluster ~seed B04-local (50.7,1.8,34.3), 18.0u from
    #     the merchant >> Greece's proven-safe 10.8u standoff, and 24u/21u from the moved
    #     fountain/caravan) so a player respawning at the south fountain and walking to the
    #     merchant never crosses them. IDENTITY rotation (SV uses identity). See
    #     docs/ENTRANCES_POLISH_LOG.md + tools/debug/plan_b_final.py.
    'levels/world/orient/silkroad/hiddenvalleyborder04.lvl': [
        # B1/B2 CORRECTION (build23) + C3 CORRECTION (this session): Will's build24/25 feedback
        # = "wagon on the RIGHT-HAND side of the driver NPC (from the standard game camera)". TQ
        # camera: North(+Z)=top of screen -> screen-RIGHT = East = +X. build25 had the wagon at
        # (23.0,20.0) = WEST (screen-left) of the driver (25.5,22.5). C3 recomposes the caravan in
        # the same west bench (clear of the occult camp): wagon EAST (+X) of the driver. New wagon
        # local (26.70,1.62,19.90) = 4.0u E of the moved driver (22.70,19.90) = screen-RIGHT; wagon
        # d_merchant=10.0u (clickable), 4u N of the horse (hitched in front), min 4.9u from occult
        # props, on-mesh <0.3u. The horse+driver MOVE via MOVE_SPECS (native records). Keeps the SV
        # wagon yaw. See docs/DOORS_HUB_LOG.md C3.
        (MERCHANT_HADES_WAGON_DBR, 26.70, 1.62, 19.90,
         {'rot': MERCHANT_HADES_WAGON_ROT}),
        # --- B1 occult atmosphere (SV Border04 exact local coords) ---
        (FOG_OCCULT_FX01_DBR, 26.641, 1.476, 24.831),
        (FOG_OCCULT_FX01_DBR, 36.901, 1.624, 23.884),
        (OCCULTISTAURA_FX01_DBR, 41.010, 1.514, 21.990),
        (PIT_FX01_DBR, 26.981, 0.379, 24.936),
        (LIGHT_10M_DYN_PURPLE_DBR, 47.033, 6.513, 29.578, {'rot': LIGHT_PURPLE_ROT}),
        (LIGHT_10M_DYN_PURPLE_DBR, 41.085, 6.509, 12.375),
        (LIGHT_10M_DYN_RED_DBR, 47.312, 6.617, 29.640),
        (LIGHT_10M_DYN_RED_DBR, 41.136, 6.563, 12.398),
        (LIGHT_5M_STAT_BLUE_DBR, 32.350, 6.055, 24.497),
        (LIGHT_5M_STAT_BLUE_DBR, 35.645, 7.138, 24.220),
        (MC_HADES_WOODPYRE01_DBR, 27.653, 0.943, 25.309, {'rot': WOODPYRE_ROT}),
        (MC_HADES_ANOURANFIREPIT02_DBR, 27.354, 1.591, 25.044),
        (DRXMAP_TOTEM_DBR, 40.240, 1.616, 12.337, {'rot': TOTEM_ROT_A}),
        (DRXMAP_TOTEM_DBR, 46.461, 1.621, 29.552, {'rot': TOTEM_ROT_B}),
        (FX_DISCIPLE_AURA_01_DBR, 38.679, 4.959, 29.893),
        (FX_DISCIPLE_AURA_02_DBR, 38.916, 4.920, 29.634),
        # --- B2 exploding pit-sprites (far/north side of the occultist) ---
        # A compact cluster mirroring Greece's spawner+lildude+pit_fx. EVERY spot on-mesh,
        # >=18u from the occultist merchant, and >=20u from BOTH the moved fountain and caravan
        # (tools/debug/plan_b_final.py + verified by gate_polish_placement.py).
        (T1_PITSPAWNER_01_DBR, 50.70, 1.80, 34.30),   # d_occ 18.0 d_carv 21.2
        # B-SPRITE-1 (2026-07-08): the sprites "spawn once then never again". arz recon:
        # t1_pitspawner_01 is an INVINCIBLE (invincible=1, ControllerStationaryMonster) Monster whose
        # self-buff skill t1_skill_pitspawner_lildude_0x (Skill_SpawnPetMonster, cooldown 12s /
        # petLimit 5 / burst 3) plus its specialAttack summons re-summon the lildude sprites while it
        # is present. The WORKING SV 0.98i exemplar (DelphiLowlands02) runs a REDUNDANT pitspawner
        # PAIR per pit: t1_pitspawner_01 + t1_pitspawner_02 (~5u apart) + more seed lildude; SVAERA
        # dropped Delphi's sprites entirely, so this injected HVBorder04 pit is the ONLY sprite pit in
        # the whole mod and we shipped just ONE spawner. Adding the second spawner mirrors the exemplar
        # density (a second independent self-summoning source + a second combat target to keep the
        # specialAttack summons firing). MAP-SIDE, low-confidence: it is faithful + harmless (invincible,
        # on-mesh, standoff-safe) but does NOT change the respawn ENGINE (the DBR summon AI). The
        # DEFINITIVE respawn fix = a dedicated Proxy driver (like HiddenValley01's respawning beastman
        # proxies) is a NEW DBR (DB lane) - see coordination_needed. On-mesh 0.00u, comp #0 (same as
        # spawner_01 + occultist), 18.0u occultist standoff (== the existing spawner), 2.8u N of
        # spawner_01. Verified: tools/debug/recon_border04_spawner_0708.py.
        (T1_PITSPAWNER_02_DBR, 50.70, 1.80, 37.10),   # d_occ 18.0, 2.8u N of spawner_01, on-mesh 0.00u
        (T1_LILDUDE_01_DBR, 51.30, 1.80, 33.30),      # d_occ 18.0 d_carv 20.6
        (T1_LILDUDE_01_DBR, 49.30, 1.80, 36.10),      # d_occ 18.0 d_carv 22.3
        (T1_LILDUDE_02_DBR, 49.50, 1.80, 35.90),      # d_occ 18.0 d_carv 22.2
        (PIT_FX01_DBR, 50.70, 1.80, 34.30),
        # --- C2 (this session): purple occult PYRE/VOLCANO visual anchor AT the sprite spawner.
        # Will pointed at the wagon-side occult purple-flame art. The spawner already carries
        # pit_fx01 (DRXeffects\other\pitfx.pfx = the purple occult flame); ADD the Hades firepit
        # "volcano bowl" (mc_hades_anouranfirepit02, Class Tile) at the same spot so the spawner
        # reads as a solid purple flaming volcano. Sprite coords UNCHANGED (add-only). On-mesh
        # 0.00u. flags=0, no 0x14 (Tile).
        (MC_HADES_ANOURANFIREPIT02_DBR, 50.70, 1.80, 34.30),
    ],
    # A1: maze03 -> Uber Dungeon walk-through GridEntrance = REMOVED (P0, Will 2026-07-12).
    # No walk-through/proximity teleport anywhere we author. The Uber Dungeon is now reached
    # via the Helos portal-master NPC (its boat-dialog carries the Uber landing coord) and
    # left via the in-crypt svc_testhub_return NPC (promoted to canonical below). The paired
    # crypt-side APPEND_0X06 return door + REMOVE_0X05 landing-strip are DISABLED (see above).
    # maze03 (base AE v0f) reverts to no injection.
    # WORKSTREAM A: INVENTED Sparta Crypt L2 walk-through entrance = REMOVED (P0, Will
    # 2026-07-12). The CataCube02_FloorLast -> SpartaCryptLevel2 born-open GridEntrance was a
    # walk-through/proximity teleport; no such triggers anywhere we author. Sparta Crypt is now
    # reached via the Helos portal-master NPC (its boat-dialog carries the SC2 landing coord)
    # and left via the in-SC2 svc_testhub_return NPC (promoted to canonical below). The paired
    # SC2-side REWRITE_0X06 return door is DISABLED (see above). catacube (base AE v0f) reverts
    # to no injection.
    # DEST = SpartaCryptLevel2: NO 0x05 injections anymore (2026-07-08 wave). The old
    # P2 (inbound landing) + P3 (return entrance) are REMOVED: P3 was appended-host = never
    # fires (live-proven engine gate), and P2's mouth uid (SPARTA_X1) now belongs to the
    # native 0x06 descriptor door that replaces both (REWRITE_0X06_SPECS above) - keeping
    # P2 would collide with the door's id. The engine renders the door from the repurposed
    # descriptor natively (grid cell (6,0,4)); arrival lands the player at the door cell.
    # REMOVED (blood-cave walk-in): the surface-side portal NPC. The authentic SV
    # entry is engine-native - HiddenValley01's existing GridEntrance cave mouth
    # + its 0x14 GUID binding stream in the (blob-swapped) Random09A, whose west
    # tunnel leads into the blood cave. No surface NPC to inject.
    # 'levels/world/orient/silkroad/hiddenvalley01.lvl': [
    #     (BLOODCAVE_ENTRANCE_NPC_DBR, 16.0, 18.0, 26.0),
    # ],
    # REMOVED (blood-cave walk-in): the cave-side return portal NPC. The return is
    # the reciprocal terrain walk-out (SV-Random09A's 0x06 embeds HiddenValley01's
    # GUID), so no return NPC is needed either.
    # 'levels/world/xbloodcave/bc_initialpathway.lvl': [
    #     (BLOODCAVE_RETURN_NPC_DBR, 20.0, 5.0, 12.0),
    # ],
    # M15 (2026-07-09, Will mechanism change): the standalone chest-room Blood Toxeus proxy
    # (q_bloodtoxeus_lone @ drxbc2 local (13.10,28.00,137.70), the M5' build30 placement) is
    # REMOVED. New mechanism = the DB lane adds um_bloodtoxeus_99 at 100% to the pool of the
    # EXISTING chest-area pack proxy records\drxmap\proxy\egg_blooddragon_pack.dbr (drxBC2
    # inst [1084] @ local (13.17,28.00,136.06), 1.6u from the old spot; verified placed exactly
    # ONCE in the whole merged world, so an IN-PLACE pool edit is safe - no clone/repoint
    # needed map-side). ⚠️ COUPLED SHIP: this map (standalone removed) + the DB lane's pool
    # edit deploy TOGETHER - the map alone = no chest-room Toxeus at all. History: M5' spec
    # kept in git (build31e and earlier).
    # ===== A2 SECRET PLACE door: rhodes_secretvista_01 HOST walk-through portals = REMOVED
    # (P0, Will 2026-07-12). The vista-side S1 GridEntrance (walk-through entrance -> Secret
    # Place) + S4 return landing are gone - no walk-through/proximity teleport anywhere we
    # author. The Secret Place (darkforestenter) is reached via the Helos portal-master NPC
    # and left via the in-area svc_testhub_return NPC (promoted to canonical below) + the
    # SV-wired RogueEncampment teleportshrineorient01 rift (FLAG_UID_SPECS, kept). vista (base
    # AE v0f) reverts to no injection.
    # ===== A2 SECRET PLACE dest (darkforestenter, v0x0e SV-only): walk-through portals REMOVED,
    # NPC RETURN promoted to canonical (P0, Will 2026-07-12). The S2 inbound landing + the S3
    # walk-through return entrance are gone. In their place: svc_testhub_return (Model C
    # boat-dialog NPC; records\quests\svc_testhub_return.dbr ships in the arz UNCONDITIONALLY -
    # apply_svc_patches _create_testhub_portal_npcs - with a 2-port menu Helos + Blood Cave via
    # sv_commonmechanics.qst _add_testhub_portal_travel). Placing its instance canonically
    # activates the existing dialog (no arz/Quests rebuild). Coord = the build34 TESTHUB survey
    # spot 3u E of the Helos-master boat-dialog landing (on-mesh, comp 0, clr 100%).
    'xpack/levels/secret_place/darkforestenter.lvl': [
        (SVC_RETURN_NPC_DBR, 27.0, 1.0, 30.0),
    ],
    # ===== A1 GARDEN OF MERCHANTS dest (GardenofMerchants, v0x0e SV-only): walk-through portals
    # REMOVED, NPC RETURN promoted to canonical (P0, Will 2026-07-12). ALL four Garden-side
    # walk-through portals are gone: G2 (HV01 inbound landing), G3 (walk-through return -> HV01),
    # H2 (Helos inbound landing), R1 (walk-through return -> Helos) + R1's map_portal_aura swirl.
    # THIS is the far end of the LIVE Steam bug ("walk south in Helos -> yanked to the Garden with
    # no way back"): both the HV01 and Helos walk-through entries into the Garden are now deleted.
    # In their place: svc_testhub_return (Model C boat-dialog NPC, ships in the arz uncondition-
    # ally, 2-port Helos + Blood Cave) placed 3u E of the boat-dialog landing. The SV-wired
    # teleportshrine_gom rift (native, untouched) is the second way back. Coord = the build34
    # TESTHUB survey spot (on-mesh, caravan_rhodes comp #1, clr 100%).
    'levels/world/olympus/gardenofmerchants.lvl': [
        (SVC_RETURN_NPC_DBR, 133.0, -39.0, 73.0),
    ],
    # ===== UBER DUNGEON (crypt_floor1, v0x0e SV-only): NPC RETURN promoted to canonical (P0,
    # Will 2026-07-12). Replaces the disabled maze03<->crypt walk-through door + its APPEND_0X06
    # native return. svc_testhub_return placed 3u S of the Helos-master boat-dialog Uber landing
    # (-2438,10,-2450). SV-only v0e -> inject_into_sv_only_blob (same path as Vashkarr). On-mesh
    # (build34 TESTHUB survey, single comp, clr 96%). flags=0, no 0x14.
    'levels/world/uberdungeon/crypt_floor1.lvl': [
        (SVC_RETURN_NPC_DBR, 140.0, 10.0, 229.0),
    ],
    # ===== SPARTA CRYPT (spartacryptlevel2, v0x0e SV-only): NPC RETURN promoted to canonical (P0,
    # Will 2026-07-12). Replaces the disabled catacube<->SC2 walk-through door + its REWRITE_0X06
    # native return. svc_testhub_return placed 3u E of the Helos-master boat-dialog Sparta landing
    # (-5602,-2,-1409). SV-only v0e -> inject_into_sv_only_blob. On-mesh (build34 TESTHUB survey,
    # comp 0, clr 100%). flags=0, no 0x14.
    'levels/world/greece/minidungeons/spartacryptlevel2.lvl': [
        (SVC_RETURN_NPC_DBR, 45.0, -1.6, 42.0),
    ],
    # ===== HELOS (startingfarmland06d, v0x11 shared): THE LIVE STEAM P0 (Will 2026-07-12) =====
    # "you cant walk south in helios since you get teleported right to the garden of merchants
    # with no way back." The N1/N1b Helos->Garden WALK-THROUGH door is DELETED: H1 (born-open
    # GridEntrance @ (74.00,0.40,184.00), the portal Will walked into), its co-located
    # map_portal_aura swirl, and the R2 return landing @ (68.00,-0.40,181.00) are ALL removed.
    # The ONLY travel out of Helos is now the portal-master NPC below (talk -> boat-dialog ->
    # confirm destination) - Will's approved pattern, no walk-through/proximity teleport.
    'levels/world/greece/startingtownver2/startingfarmland06d.lvl': [
        # M8 (build32a): the Helos portal-master NPC (Model C boat-dialog). KEPT - this is the
        # proven "talk to travel" traveler and is now Helos's SOLE cross-area travel mechanism.
        # Its 4-destination menu (Garden / Secret Place / Uber Dungeon / Sparta Crypt) rides
        # sv_commonmechanics.qst (build_quest_files _add_helos_portal_travel). flags=0, no 0x14.
        PORTAL_MASTER_SPEC,
    ],
    # M9 (build32b): Vashkarr, Eldest of the Ancients - boss proxy guarding the Majestic
    # Chest in the FotA cave (Random05A, base-game v0x0e). FIRST LIVE USE of the v0e
    # SVAERA-host injection branch (5af756c): routes through inject_into_sv_only_blob
    # (base-56), NOT step 7's v11 0x14-append pass. Parse-back gate: 59 -> 60 instances.
    VASHKARR_HOST_KEY: [
        VASHKARR_SPEC,
    ],
    # ===== C4 (this session): Greece occultist region atmosphere restore (SV-exact) =====
    # SV's Delphi "Crisaeos Falls" occultist region had the SAME regional smoke Will remembers
    # (occult fog + pit + Hades firepits + coloured lights). The merge dropped it. Restore at SV's
    # EXACT float32 coords + rotations (extract_c4_atmosphere.py). ALL v0x11 shared levels with
    # SPARSE 0x14 -> the SAFE append-only path (atmosphere = flags=0 = NO 0x14 appended; the naive
    # wholesale-0x14-regen that crashed in a674c49 does NOT run for these). Pure visual, no aggro.
    # DelphiLowlands04 = the occultist TENT scene (5 records):
    'levels/world/greece/delphi/delphilowlands04.lvl': [
        (MERCHANT_DELPHI_OCCULTTENT01_DBR, 12.882176399230957, 9.980415344238281, 2.524287223815918,
         {'rot': DELPHI_OCCULTTENT_ROT}),
        (FOG_OCCULT_FX01_DBR, 19.344999313354492, 10.004997253417969, 2.115000009536743),
        (FOG_OCCULT_FX01_DBR, 8.53499984741211, 10.004997253417969, 15.024999618530273),
        (LIGHT_10M_STATNL_BLUE_DBR, 15.212060928344727, 16.30961799621582, 5.173452377319336,
         {'rot': DELPHI_STATNL_BLUE_ROT}),
        (LIGHT_5M_DYN_GREEN_DBR, 14.883951187133789, 11.311467170715332, 4.744840621948242,
         {'rot': DELPHI_5M_DYN_GREEN_ROT}),
        # --- B-SMOKE-1 (2026-07-08): the dropped CAGE scene at the occultist tent (binding
        # fx + cages + caged-sprite dress + vitstaffs + the cage sound loop), SV-exact
        # coords/rots (recon_wave4_0708 delphi). Decoration/EffectEntity/SoundObject only -
        # no aggro. flags=0, no 0x14 (SV places none).
        (CAGE_BINDING_FX01_DBR, 2.5120930671691895, 10.257486343383789, 11.083516120910645,
         {'rot': (0.8221694231033325, 0.0, 0.5692428350448608,
                  0.0, 1.0, 0.0,
                  -0.5692428350448608, 0.0, 0.8221694231033325)}),
        (CAGE_MEDIUM_DBR, 1.8174877166748047, 10.003944396972656, 12.080963134765625,
         {'rot': (0.5028848052024841, 0.0, -0.8643534183502197,
                  0.0, 1.0, 0.0,
                  0.8643534183502197, 0.0, 0.5028848052024841)}),
        (T1_LILDUDE_DRESS_02_DBR, 1.4740500450134277, 11.881990432739258, 10.670920372009277,
         {'rot': (-0.9482517838478088, 0.0, -0.3175193667411804,
                  0.0, 1.0, 0.0,
                  0.3175193667411804, 0.0, -0.9482517838478088)}),
        (T1_LILDUDE_DRESS_03_DBR, 2.658547878265381, 11.852787017822266, 9.270751953125,
         {'rot': (0.4952678978443146, 0.0, -0.8687403202056885,
                  0.0, 1.0, 0.0,
                  0.8687403202056885, 0.0, 0.4952678978443146)}),
        (SOUNDOBJECT_DEMONCAGE_DBR, 2.19281005859375, 9.999998092651367, 10.903641700744629),
        (CAGE_SMALL_DBR, 2.534714698791504, 11.812200546264648, 9.186098098754883,
         {'rot': (0.3389511704444885, 0.0, -0.9408039450645447,
                  0.0, 1.0, 0.0,
                  0.9408039450645447, 0.0, 0.3389511704444885)}),
        (CAGE_SMALL_DBR, 1.4819526672363281, 11.844521522521973, 10.7604341506958,
         {'rot': (-0.22213487327098846, 0.0, 0.9750158786773682,
                  0.0, 1.0, 0.0,
                  -0.9750158786773682, 0.0, -0.22213487327098846)}),
        (CAGE_MEDIUM_DBR, 0.139495849609375, 10.004996299743652, 9.855687141418457,
         {'rot': (0.3385816514492035, 0.0, -0.9409369826316833,
                  0.0, 1.0, 0.0,
                  0.9409369826316833, 0.0, 0.3385816514492035)}),
        (CAGE_MEDIUM_DBR, 3.1532297134399414, 10.004997253417969, 9.70942497253418,
         {'rot': (0.34604352712631226, 0.0, -0.9382184147834778,
                  0.0, 1.0, 0.0,
                  0.9382184147834778, 0.0, 0.34604352712631226)}),
        (T1_LILDUDE_DRESS_01_DBR, 3.8037586212158203, 10.004998207092285, 9.676807403564453,
         {'rot': (-0.21790535748004913, 0.0, -0.9759699702262878,
                  0.0, 1.0, 0.0,
                  0.9759699702262878, 0.0, -0.21790535748004913)}),
        (T1_LILDUDE_DRESS_01_DBR, 2.9295451641082764, 10.004998207092285, 8.955889701843262,
         {'rot': (-0.8212995529174805, 0.0, 0.5704973936080933,
                  0.0, 1.0, 0.0,
                  -0.5704973936080933, 0.0, -0.8212995529174805)}),
        (T1_LILDUDE_DRESS_01_DBR, 2.944338798522949, 10.004997253417969, 10.272355079650879,
         {'rot': (0.640135645866394, 0.0, -0.7682619094848633,
                  0.0, 1.0, 0.0,
                  0.7682619094848633, 0.0, 0.640135645866394)}),
        (VITSTAFF_01_DBR, 12.787829399108887, 11.219710350036621, 7.1061553955078125,
         {'rot': (0.9818659424781799, 0.14403623342514038, -0.12325886636972427,
                  0.11613059043884277, 0.05692309886217117, 0.9916014671325684,
                  0.14984282851219177, -0.9879338145256042, 0.03916383907198906)}),
        (VITSTAFF_05_DBR, 12.282719612121582, 11.395538330078125, 8.074625968933105,
         {'rot': (0.1790051907300949, -0.009947560727596283, -0.9837979674339294,
                  0.9677491188049316, 0.181934654712677, 0.17424550652503967,
                  0.17725369334220886, -0.9832603931427002, 0.04219392314553261)}),
    ],
    # DelphiLowlands02 = the pit-sprites / lava-pit "volcano" scene (8 records):
    'levels/world/greece/delphi/delphilowlands02.lvl': [
        (PIT_FX02_DBR, 52.12237548828125, 10.881780624389648, 116.73532104492188),
        (MC_HADES_ANOURANFIREPITMD01_DBR, 52.255706787109375, 10.331375122070312, 116.76100158691406),
        (BUGCLOUD_SMALLFX_DBR, 44.85322570800781, 10.314421653747559, 125.21780395507812),
        (FOG_OCCULT_FX01_DBR, 54.708003997802734, 10.246397972106934, 121.40185546875),
        (FOG_OCCULT_FX01_DBR, 56.388099670410156, 10.308216094970703, 121.92228698730469),
        (PIT_FX01_DBR, 79.44921112060547, 10.288912773132324, 122.02896118164062),
        (FOG_OCCULT_FX01_DBR, 81.38713073730469, 10.411105155944824, 122.9507827758789),
        (MC_HADES_ANOURANFIREPIT03_DBR, 79.54350280761719, 9.956783294677734, 122.13789367675781,
         {'rot': DELPHI_ANOURANFIREPIT03_ROT}),
        # --- B-SMOKE-1 (2026-07-08): the dropped LIVE pit-sprite scene (SV-exact). The two
        # Delphi pits get their spawner pairs + seed lildudes back (Monster class, aggro -
        # SV's own placement, the "working Greece cluster" the HVBorder04 pit mirrors) plus
        # the scene sound objects. Coords/rots byte-exact from SV 0.98i (recon_wave4_0708).
        (T1_LILDUDE_02_DBR, 49.064998626708984, 10.335891723632812, 119.2449951171875),
        (T1_LILDUDE_02_DBR, 53.27499771118164, 10.388538360595703, 113.59500122070312),
        (T1_LILDUDE_01_DBR, 55.334999084472656, 10.315872192382812, 114.48500061035156),
        (T1_PITSPAWNER_01_DBR, 55.00510787963867, 10.848041534423828, 117.33020782470703),
        (BIGOBSIDIAN_DBR, 53.17753982543945, 10.589143753051758, 119.64012908935547,
         {'rot': (0.999930739402771, -0.011760160326957703, -0.00041142263216897845,
                  0.011761130765080452, 0.9999278783798218, 0.002441165503114462,
                  0.0003826844331342727, -0.0024458353873342276, 0.9999969601631165)}),
        (T1_PITSPAWNER_02_DBR, 49.529090881347656, 11.298062324523926, 118.4052734375,
         {'rot': (0.9999987483024597, 0.0, -0.0015911301597952843,
                  0.0, 1.0, 0.0,
                  0.0015911301597952843, 0.0, 0.9999987483024597)}),
        (T1_LILDUDE_01_DBR, 54.78499984741211, 10.467788696289062, 119.15499877929688),
        (T1_LILDUDE_01_DBR, 76.59500122070312, 9.97555160522461, 120.54499816894531),
        (T1_PITSPAWNER_01_DBR, 80.52296447753906, 10.787839889526367, 123.01321411132812),
        (SOUNDOBJECT_CAGEGLOW_DBR, 80.39462280273438, 9.97697639465332, 124.99458312988281,
         {'rot': (0.999902606010437, 0.013953262008726597, -0.0002705814258661121,
                  -0.013954824768006802, 0.9998777508735657, -0.007057285401970148,
                  0.00017207619384862483, 0.00706037413328886, 0.9999750852584839)}),
        (T1_LILDUDE_01_DBR, 82.1449966430664, 9.968833923339844, 121.71499633789062),
    ],
    # DelphiLowlands03 = sprite-dress continuation (2 C4 records + B-SMOKE-1 restores):
    'levels/world/greece/delphi/delphilowlands03.lvl': [
        (BUGCLOUD_SMALLFX_DBR, 123.81183624267578, 10.15844440460205, 6.107987403869629),
        (BUGCLOUD_SMALLFX_DBR, 123.97244262695312, 10.947917938232422, 8.745109558105469),
        # --- B-SMOKE-1: dropped caged-sprite DRESS props (Decoration, no aggro), SV-exact.
        (T1_LILDUDE_DRESS_02_DBR, 127.98994445800781, 10.004997253417969, 8.962763786315918,
         {'rot': (-0.13307425379753113, 0.0, -0.9911060929298401,
                  0.0, 1.0, 0.0,
                  0.9911060929298401, 0.0, -0.13307425379753113)}),
        (T1_LILDUDE_DRESS_02_DBR, 127.3948974609375, 10.004997253417969, 10.090458869934082,
         {'rot': (0.9828716516494751, 0.0, -0.18429139256477356,
                  0.0, 1.0, 0.0,
                  0.18429139256477356, 0.0, 0.9828716516494751)}),
        (VITSTAFF_01_DBR, 125.63081359863281, 10.04549503326416, 1.2841295003890991,
         {'rot': (0.9663739800453186, 0.2503989338874817, 0.0584961362183094,
                  -0.25052839517593384, 0.9680951237678528, -0.005229487083852291,
                  -0.057939283549785614, -0.009601302444934845, 0.9982739686965942)}),
        (VITSTAFF_01_DBR, 125.35291290283203, 10.09128475189209, 0.9109594821929932,
         {'rot': (0.9992513656616211, 0.038682721555233, -0.0006079100421629846,
                  -0.03868189826607704, 0.9992507100105286, 0.0013141712406650186,
                  0.0006582902278751135, -0.001289672334678471, 0.9999989867210388)}),
        (VITSTAFF_01_DBR, 125.24671936035156, 10.073407173156738, 0.9723517894744873,
         {'rot': (0.9805499911308289, 0.0, -0.1962699145078659,
                  0.0, 1.0, 0.0,
                  0.1962699145078659, 0.0, 0.9805499911308289)}),
    ],
}

# M10 (build32b): merge the Obsidian roulette corner placements (defined above with their
# survey + re-verify evidence) into INJECT_SPECS. Collision-guarded: neither tombobs level
# hosts any other injection; a future key collision must be resolved by explicit list
# merge, not silent clobber.
for _m10_key in OBS_ROULETTE_SPECS:
    assert _m10_key not in INJECT_SPECS, f'M10 host key collision with INJECT_SPECS: {_m10_key}'
INJECT_SPECS.update(OBS_ROULETTE_SPECS)

# BROODNEST (build35): merge the Broodmother Nest set-piece (CANONICAL) into INJECT_SPECS.
# tombobs02 ALREADY carries the 2 roulette corners (merged just above), so this APPENDS the
# 7 nest proxies to that level's existing list rather than clobbering it (order-preserving:
# the 2 roulette instances keep their indices, the nest lands after them). This is the first
# canonical-map content change since build32b; it applies to BOTH map variants because it
# lives in the base INJECT_SPECS (canonical uses INJECT_SPECS directly; TESTHUB layers the
# hub extras on top). Assert the only expected collision is the shared tombobs02 host.
for _bn_key, _bn_specs in BROODNEST_SPECS.items():
    assert _bn_key == BROODNEST_HOST_KEY, f'unexpected broodnest host {_bn_key}'
    INJECT_SPECS.setdefault(_bn_key, [])
    INJECT_SPECS[_bn_key] = list(INJECT_SPECS[_bn_key]) + list(_bn_specs)

# UBERBOSS (build36, 2026-07-11): merge the 5 new apex-boss lone proxies into
# INJECT_SPECS. Each host is a DISTINCT native AE level not touched by any other
# injection (the roulette/broodnest live in tombobs01/02), so a plain collision-
# guarded assignment is correct; a future collision must be resolved by explicit
# list-merge, never silent clobber. Applies to BOTH map variants (canonical uses
# INJECT_SPECS directly; TESTHUB layers hub extras on top) - these are shipped
# content bosses, like the Broodmother nest.
for _ub_key, _ub_specs in UBERBOSS_SPECS.items():
    assert _ub_key not in INJECT_SPECS, f'build36 uberboss host key collision with INJECT_SPECS: {_ub_key}'
    INJECT_SPECS[_ub_key] = list(_ub_specs)

# --- MOVE_SPECS: reposition EXISTING (native) instances in place (Workstream B) -----------
# The merge already places these records; move_0x05_instances rewrites ONLY their 12
# position bytes (rotation/flags/string-index preserved), so the caravan scene composes
# around the moved wagon without the wagon overlapping the occultist merchant.
#   Format: level_key -> [ {dbr, x, y, z, match?, from_xyz?} ]  (coords are LEVEL-LOCAL)
#   match defaults to 'all'; both targets below have exactly ONE instance in Border04
#   (verified: Horse02 x1 @ local (34.45,1.62,19.85); silkroad_villager1 x1 @ (39.11,1.62,
#   29.95)) so 'all' is unambiguous. from_xyz is the ORIGINAL SVAERA-native position (the merge
#   re-runs from the fresh SVAERA blob each build, so from_xyz stays the native coord).
#   C3 CORRECTION (this session): recompose so the wagon is EAST (screen-right) of the driver.
#     silkroad_villager1 (driver) -> (22.70,1.62,19.90) world (-111.3,-102.4,2321.9) [WEST of the
#                          wagon; wagon at (26.70,19.90) is 4u E = screen-right; on-mesh, 13.7u from
#                          merchant = clickable]
#     Horse02          -> (26.70,1.62,15.90) world (-107.3,-102.4,2317.9) [4u S of the wagon =
#                          hitched in front, on-mesh <0.3u, 12u from merchant]
HORSE02_DBR = b'Records/Creature/Ambient/Horse02.dbr'
SILKROAD_VILLAGER1_DBR = b'records\\creature\\npc\\speaking\\orient\\silkroad_villager1.dbr'
MOVE_SPECS = {
    'levels/world/orient/silkroad/hiddenvalleyborder04.lvl': [
        {'dbr': HORSE02_DBR, 'x': 26.70, 'y': 1.62, 'z': 15.90,
         'from_xyz': (34.445534, 1.620424, 19.845734)},
        {'dbr': SILKROAD_VILLAGER1_DBR, 'x': 22.70, 'y': 1.62, 'z': 19.90,
         'from_xyz': (39.108494, 1.619662, 29.949188)},
    ],
}

# ===== TEST HUB (SVC_TEST_HUB=1 only) - a SEPARATE ARTIFACT (local/Levels_merged_TESTHUB.arc) =====
# 5 one-way pairs from inside the blood cave (Random09A, near the mouth/entry, on-mesh, NO combat
# proxies inside the cave) to maze03 / murderbossroom / SpartaCryptLevel2 / darkforestenter /
# GardenofMerchants, each with a reciprocal RETURN to the cave. Cave cells S0..S4 = the 5 outbound
# entrances; S5..S9 = the 5 return-landings (all >=10u apart). Each destination gets a landing +
# a return-entrance. The flag-OFF (canonical) build must be BYTE-IDENTICAL to the flag-ON build
# minus these hub entities - proven by gate_hub_identity.py (diff = ONLY the hub blobs). Each hub
# pair uses its OWN minted UIDs (HUB_UIDS) so there is NO cross-talk with A1/A2/Sparta pairs.
#
# The 5 cave entrances (S0..S4) each carry cave_entrance_0x14 (mouth+exit+dest); the 5 cave return
# landings (S5..S9) each carry cave_ret_landing_0x14 (ret-exit+zeros). Order pairs S<i> outbound
# with S<i+5> return for the SAME destination.
_HUB_CAVE_ENTRANCES = [  # (local x,y,z) for S0..S4 = the 5 outbound entrances (in Random09A)
    (21.10, 1.00, 12.10), (21.10, 1.00, 22.10), (21.10, 1.00, 32.10),
    (21.10, 1.00, 42.10), (24.30, 1.00, 57.90),
]
_HUB_CAVE_RETURNS = [    # (local x,y,z) for S5..S9 = the 5 return landings (in Random09A)
    (29.10, 1.00, 48.10), (29.90, 1.00, 16.90), (29.90, 1.00, 26.90),
    (29.90, 1.00, 36.90), (34.30, 1.00, 57.50),
]
# destination order (must match the cave-entrance order): each = (dest_key, dest_level_key,
# landing_local, ret_entrance_local)
_HUB_DESTS = [
    ('maze03', 'levels/world/greece/knossos/underground/maze03.lvl',
     (290.70, 1.20, 148.50), (292.50, 1.20, 156.30)),
    ('murderbossroom', 'xpack/levels/secret_place/murderbossroom.lvl',
     (52.90, 3.00, 28.10), (52.90, 3.00, 39.90)),
    # SC2's Sparta P2/P3 portals were REMOVED 2026-07-08 (native 0x06 door conversion);
    # the hub landing/ret coords are kept unchanged (they were already >=10u from the
    # native door cell (6,0,4) center at local (52,36): land d=11.5, ret d=22.3).
    ('spartacryptlevel2', 'levels/world/greece/minidungeons/spartacryptlevel2.lvl',
     (42.30, -1.60, 42.30), (29.70, -1.60, 36.30)),
    # darkforestenter also hosts the A2 S2/S3 portals; hub landing/ret spaced >=10u from them.
    ('darkforestenter', 'xpack/levels/secret_place/darkforestenter.lvl',
     (29.90, 1.40, 38.50), (21.10, 6.80, 20.90)),
    # gardenofmerchants also hosts the A1 G2/G3 portals; hub landing/ret in the caravan comp,
    # >=10u from G2/G3 (8u from the caravan).
    ('gardenofmerchants', 'levels/world/olympus/gardenofmerchants.lvl',
     (136.30, -39.00, 71.10), (136.30, -39.00, 87.10)),
]

# --- TEST-HUB EXTRA (M5', build30): NO extra Toxeus -----------------------------------------
# M15 (2026-07-09) UPDATE: the Blood Toxeus now has ZERO standalone INJECT_SPECS placements.
# Both M5' standalones (chest room q_bloodtoxeus_lone + parchment q_bloodtoxeus_lone_50) are
# RETIRED - Toxeus joins the pools of the EXISTING chest-area egg_blooddragon_pack (100%) and
# a clone of the parchment demon_01_cluster (50%), both DB-lane arz edits (see the M15 notes
# at the former spec sites). The old TESTHUB-only cave-mouth spawn stays retired too.
#
# --- MONSTER TEST YARD (build33, TESTHUB-only) ----------------------------------------------
# Will (mod author) wants to fight+tune every new hostile monster from build31/32 in one place.
# The DB lane (arz e3810219) added 7 dedicated Proxy records + their ProxyPool records under
# records\drxmap\proxy\, each pointing at the REAL shipped monster records (never clones), so
# tuning those records tunes the yard fight 1:1. They are added UNCONDITIONALLY to the shared
# arz but stay INERT because ONLY the TESTHUB map places them (build_hub_extra_specs, folded in
# by merge_hub_into_inject_specs only when SVC_TEST_HUB=1). The canonical/Steam map references
# none -> byte-identical d5259629. SPOT B reuses the EXISTING q_vashkarr_lone proxy (already
# placed once canonical at FotA; a second TESTHUB-only placement here needs no new DB record).
# All proxies placed flags=0, no 0x14 (the q_vashkarr_lone proxy byte-shape precedent).
# Coords re-surveyed 2026-07-10 against the canonical HV01 0x0b navmesh (single fixed Silk Road
# navmesh, no tileset variants): every spot on-mesh, on-largest-component, >=98% clear at its
# pool's placementExtents (all 100% here), spawn spots spaced+off the villager (41.7,103.2)/
# fountain (Z143)/garden-portal (Z128+) reference entities.
Q_YARD_ENSLAVER_DBR      = b'records\\drxmap\\proxy\\q_yard_enslaver.dbr'
Q_YARD_MARAUDERS_DBR     = b'records\\drxmap\\proxy\\q_yard_marauders.dbr'
Q_YARD_OBS_SARKOTH_DBR   = b'records\\drxmap\\proxy\\q_yard_obs_sarkoth.dbr'
Q_YARD_OBS_GORRAHK_DBR   = b'records\\drxmap\\proxy\\q_yard_obs_gorrahk.dbr'
Q_YARD_OBS_VORANTHYS_DBR = b'records\\drxmap\\proxy\\q_yard_obs_voranthys.dbr'
Q_YARD_OBS_ILSEVAR_DBR   = b'records\\drxmap\\proxy\\q_yard_obs_ilsevar.dbr'
Q_YARD_WYRM_DBR          = b'records\\drxmap\\proxy\\q_yard_wyrm.dbr'
# build35: the broodmother yard proxy (DB lane created q_yard_broodmother + its pool =
# 1 um_broodmother_99 mother + 2 um_sepulchralwyrm_40 escorts @100%, placementExtents 3.5).
Q_YARD_BROODMOTHER_DBR   = b'records\\drxmap\\proxy\\q_yard_broodmother.dbr'
# VASHKARR_PROXY_DBR (records\drxmap\proxy\q_vashkarr_lone.dbr) is defined above (SPOT B reuse).
# build36 (M1): the Dorus/Drowned-King yard proxy. DB lane (apply_svc_patches, q_yard_dorus)
# created q_yard_dorus + its pool = 1 um_dorus_99 king + 2 royal-guard escorts @100%
# (placementExtents 4.0) so Will can test the Propontis superboss fight at the hub.
Q_YARD_DORUS_DBR         = b'records\\drxmap\\proxy\\q_yard_dorus.dbr'
HV01_LVL_KEY = 'levels/world/orient/silkroad/hiddenvalley01.lvl'

# --- PORTAL TEST RIG (build34, TESTHUB-only; Model C boat-dialog NPCs) -----------------------
# Will (mod author) wants a flag-gated LOCAL-ONLY travel rig to reach EVERY restored SV area from
# Helos AND from the blood-cave entrance, verify each area (real gold portals), then return to the
# normal map. Mechanism = Model C: BoatDialog portal-master NPCs (the proven Almyros shape), NOT
# born-open GridEntrance portals (RETIRED this wave: they ship the B-PORTAL-1/2/3 blue-pane /
# walkway-force-teleport / dead-appended-host-return bugs; see merge_hub_into_inject_specs).
# The DB lane (arz c7da07f6) added 2 NPC records (clones of the boat-dialog donor
# knossos_boatmantoegypt), boat-dialog triggers in sv_commonmechanics.qst, and 7 Text tags:
#   svc_testhub_master (HUB portal-master, 7 ports)   -> placed at Helos + the blood-cave mouth,
#   svc_testhub_return (RETURN NPC, 2 ports Helos+Blood Cave) -> placed once inside each of the 5
#     restored SV areas (Garden/Secret/Uber/Sparta/BossArena), a few u from that area's boat-dialog
#     landing so Will sees it on arrival.
# Records added UNCONDITIONALLY to the shared arz/Quests/Text but INERT on canonical/Steam (the
# canonical map places NONE of these NPCs). ONLY the TESTHUB map (build_hub_extra_specs, folded in
# by merge_hub_into_inject_specs when SVC_TEST_HUB=1) places them -> canonical stays byte-identical.
# Coords surveyed 2026-07-10 against the CANONICAL 0x0b navmeshes (byte-identical to TESTHUB for
# every host): every spot on-mesh, on the SAME connected component as that area's boat-dialog
# landing coord (reachable after the teleport), >=96% clear at a 3.0u disc, flags=0 no-0x14
# (the q_vashkarr_lone byte-shape). Retiring the GridEntrance hub reverts TESTHUB random09a to the
# canonical SV blood-cave swap blob (the normal INJECT_SPECS loop no longer overrides it), so the
# blood-cave hub-master coord is valid against that SV navmesh (see the R09_LVL_KEY note below).
SVC_TESTHUB_MASTER_DBR = b'records\\quests\\svc_testhub_master.dbr'  # RETIRED as a placement (build36 warden split); constant kept for reference
SVC_TESTHUB_RETURN_DBR = b'records\\quests\\svc_testhub_return.dbr'
# WARDEN SPLIT (build36, M3): the single svc_testhub_master was placed in TWO levels
# (Helos + blood cave); Action_BoatDialog binds its menu to ONE entity per record
# path, so the second placement rendered mute-but-visible (warden diagnosis H1). The
# DB lane splits it into two singly-placed records (each clones the boatman, REUSES the
# same name/chat tags -> no Text change). Point Helos at ..._helos and the cave at
# ..._cave; each is now the proven single-placement Almyros configuration.
SVC_TESTHUB_MASTER_HELOS_DBR = b'records\\quests\\svc_testhub_master_helos.dbr'
SVC_TESTHUB_MASTER_CAVE_DBR  = b'records\\quests\\svc_testhub_master_cave.dbr'
# Host-level keys (reuse the existing constants where defined).
HELOS_HOST_KEY    = PORTAL_MASTER_HOST_KEY   # startingfarmland06d (AE v0x11); Almyros host
R09_LVL_KEY       = 'levels/world/orient/underground/random09a.lvl'  # SV blood-cave swap blob
GARDEN_LVL_KEY    = 'levels/world/olympus/gardenofmerchants.lvl'          # SV-only v0e
SECRET_LVL_KEY    = 'xpack/levels/secret_place/darkforestenter.lvl'       # SV-only v0e
UBER_LVL_KEY      = CRYPT_FLOOR1_LEVEL_KEY                                 # crypt_floor1 SV-only v0e
SPARTA_LVL_KEY    = 'levels/world/greece/minidungeons/spartacryptlevel2.lvl'  # SV-only v0e
BOSSARENA_LVL_KEY = 'levels/world/bossarena/boss_arena.lvl'               # SV-only v0e


def build_hub_extra_specs():
    """TEST-HUB non-portal entity additions (level_key -> [specs]). Folded into INJECT_SPECS ONLY
    when SVC_TEST_HUB=1 (append-only -> canonical blobs byte-unchanged). Each is a 4-tuple
    (dbr, x, y, z) -> flags=0, no 0x14, identity rot. Two groups:

    (1) MONSTER TEST YARD (build33; RESPACED build36 M1): 10 proxy placements in HiddenValley01
        (Silk Road), a down-valley gauntlet from the blood-cave mouth (Enslaver + marauders,
        Vashkarr + 2 champs, the NEW Drowned King Dorus, the 4 Obsidian guardians + warbands,
        the broodmother apex, the wyrm horde). Respaced to min pairwise 32.2u (was ~1-11u).

    (2) PORTAL TEST RIG (build34, Model C): the 2 svc_testhub_master hub NPCs (Helos plaza +
        blood-cave mouth) and the 5 svc_testhub_return NPCs (one inside each restored SV area).
        All coords surveyed on-mesh (see the module note above the DBR constants). NOTE: the
        random09a (R09_LVL_KEY) placement is EXCLUDED from the normal INJECT_SPECS fold by
        merge_hub_into_inject_specs and applied instead via the special swap path in
        svaera_plus_portals.py (random09a is rebuilt from the SV blood-cave blob there; the normal
        loop would inject into the discarded AE blob). It still lives in this dict as the single
        source of truth for the coord."""
    return {
        # M1 (build36): RESPACED to de-crowd (Will: "pets too crowded"). The old layout packed
        # 9 groups into ~1-11u clusters (the 3 gauntlet bosses within ~11u; the 4 Obsidian within
        # ~11u). This spreads all 10 groups (the 9 build33/35 residents + the NEW q_yard_dorus)
        # across HiddenValley01's full walkable valley at min pairwise 32.2u, every spot on-mesh in
        # all 3 tilesets with clr@2.5 >= 91%, and every spot in the SAME walkable component as the
        # cave-mouth/camp (flood-fill verified reachable on foot). Coords re-surveyed on the built
        # HV01 0x0b; floor Y from the nearest ground instances (the engine snaps spawns to terrain).
        #   GEOMETRIC LIMIT: Will asked for >=60u, but HV01's walkable footprint (a winding valley,
        #   only ~23% of its bounding box is floor) physically cannot fit 10 (or even 9) spawn spots
        #   at 60u - the absolute on-mesh ceiling for 10 points is ~45u, and ~32u once reachability +
        #   a clear spawn disc are required. 32u still separates every group by ~a screen-width (vs
        #   the old ~1-11u), which resolves the crowding. True 60u would need either fewer yard
        #   groups or a larger FLAT host level - flagged for Will in docs/reports/build36_map_report.md.
        HV01_LVL_KEY: [
            (Q_YARD_ENSLAVER_DBR,      33.0,  15.9,  41.0),   # SW  clr@2.5=98%
            (Q_YARD_MARAUDERS_DBR,     71.0,  13.5,  31.0),   # S   clr@2.5=100%
            (VASHKARR_PROXY_DBR,      101.0,  -1.5,  43.0),   # SE  clr@2.5=96%  (Vashkarr + 2 champs)
            (Q_YARD_DORUS_DBR,         65.0, -10.0,  63.0),   # NEW build36  clr@2.5=100%  (Drowned King)
            (Q_YARD_OBS_SARKOTH_DBR,   63.0,   9.9,  97.0),   # C   clr@2.5=95%
            (Q_YARD_OBS_GORRAHK_DBR,  127.0,  -2.3,  93.0),   # C   clr@2.5=92%
            (Q_YARD_OBS_VORANTHYS_DBR,157.0,  -0.4, 111.0),   # C   clr@2.5=100%
            (Q_YARD_BROODMOTHER_DBR,  107.0,   1.4, 123.0),   # apex  clr@2.5=100% clr@3.5=100% (roomiest)
            (Q_YARD_OBS_ILSEVAR_DBR,   71.0,   0.0, 129.0),   # C   clr@2.5=91%
            (Q_YARD_WYRM_DBR,          55.0,  17.6, 157.0),   # D horde  clr@2.5=100%
        ],
        # -- PORTAL RIG: 2 HUB masters (build36 warden split: each a distinct, singly-placed record) --
        # Helos plaza: placed at local (72.0,0.8,184.0), SW of the canonical Almyros NPC
        # (76.5,0.6,189.5), 7.1u away - clear click-separation for H5 insurance (the record split is
        # the REAL muteness fix; the coord only needs both NPCs individually clickable).
        # R5 MOVE (was (64.5,0.8,189.5)): once the survey FRAME BUG (a fixed 16u 0x05-vs-0x0b offset)
        # was corrected, (64.5,189.5) read on-mesh but NEAR A WALL - clr 64/51/42% (N/E/L) at a 3.0u
        # disc (the R3 "100%" was the raw-frame artifact). RE-SURVEYED on the built map with the
        # corrected-frame tool: (72.0,184.0) reads d=0.14u / clr 100% in ALL 3 tilesets, comp#1 (the
        # main reachable component). Points at the split ..._helos record. TESTHUB-only.
        HELOS_HOST_KEY: [
            (SVC_TESTHUB_MASTER_HELOS_DBR, 72.0, 0.8, 184.0),
        ],
        # Blood-cave mouth (random09a SV swap blob): the spec's cave-mouth approach band; world
        # (6011,19,3288); comp 0 (same as the cave-mouth entry corridor AND the return landing at
        # (6018,19,3293)); 8.6u from that return landing so the repeated test loop barely walks;
        # clr@3.0=100%. Yard is in HV01 (a different level) -> the >=40u-from-yard rule is moot.
        # APPLIED VIA THE SWAP PATH (see merge_hub_into_inject_specs + svaera_plus_portals.py).
        # Points at the split ..._cave record (coords unchanged).
        R09_LVL_KEY: [
            (SVC_TESTHUB_MASTER_CAVE_DBR, 32.0, 1.0, 45.0),
        ],
        # -- PORTAL RIG: RETURN NPCs --
        # P0 (Will 2026-07-12): the Garden / Secret Place / Uber / Sparta return NPCs were PROMOTED
        # into the BASE INJECT_SPECS (they became canonical when the walk-through portals were
        # removed), so they are intentionally NO LONGER listed here - merge_hub_into_inject_specs
        # appends hub-extra ON TOP of base, so listing them here too would DOUBLE-place them in the
        # TESTHUB build. The TESTHUB build inherits all four from base. ONLY the Boss Arena return
        # stays TESTHUB-only (Boss Arena is not in the canonical Helos portal-master's 4-dest menu;
        # only the 7-port TESTHUB hub master reaches it).
        # The Boss Arena (boss_arena): 3u E of landing (-433,0,-3602); comp 0; clr@3.0=100%; the
        # landing is ~90u off volume_startolympianarena (DB lane), so this NPC stays well off it.
        BOSSARENA_LVL_KEY: [
            (SVC_TESTHUB_RETURN_DBR, 131.0, 0.0, 40.0),
        ],
    }


def patch_respawn_group_position(groups_data, shrine_uid, new_xyz, level_name=''):
    """C1 FIX (respawn position): rewrite the POSITION triplet of a respawn-shrine member in the
    world GROUPS(0x11) section, keyed by the shrine's 16-byte UniqueId.

    ROOT CAUSE (byte-proven, docs/DOORS_HUB_LOG.md C1): the engine respawns the player at the
    position recorded in the GROUPS respawnorient member, NOT at the shrine's 0x05 instance. Each
    member is `UID(16) + levelGUID(16) + position(3xfloat32,12)`; every NATIVE respawn shrine's
    GROUPS position == its 0x05 position. When build24 MOVED the HV01 fountain's 0x05 instance, the
    GROUPS member position stayed the OLD (49.263,15.634,14.950) value, so the player kept
    respawning at the pre-move spot (Will's disproven-activation-caching report). This rewrites the
    12 position bytes at UID+32 to the fountain's NEW 0x05 position so GROUPS == 0x05 (native parity).

    Idempotent + surgical: finds the UID, asserts the levelGUID+pos layout is present, rewrites ONLY
    the 12 position bytes. Asserts the UID is found EXACTLY once (a respawn shrine has one member).
    Returns the modified groups bytes.
    """
    buf = bytearray(groups_data)
    n = buf.count(shrine_uid)
    if n == 0:
        raise ValueError(f'respawn shrine UID {shrine_uid.hex()} not found in GROUPS '
                         f'({level_name}) - cannot patch respawn position')
    if n != 1:
        raise ValueError(f'respawn shrine UID {shrine_uid.hex()} appears {n}x in GROUPS '
                         f'({level_name}) - ambiguous, refusing to patch')
    off = buf.find(shrine_uid)
    pos_off = off + 32  # UID(16) + levelGUID(16) -> position triplet
    if pos_off + 12 > len(buf):
        raise ValueError(f'GROUPS respawn member truncated at UID {shrine_uid.hex()} ({level_name})')
    old = struct.unpack_from('<3f', buf, pos_off)
    struct.pack_into('<3f', buf, pos_off, float(new_xyz[0]), float(new_xyz[1]), float(new_xyz[2]))
    print(f'    C1: GROUPS respawn member {shrine_uid.hex()[:12]}.. pos '
          f'({old[0]:.3f},{old[1]:.3f},{old[2]:.3f}) -> ({new_xyz[0]:.2f},{new_xyz[1]:.2f},{new_xyz[2]:.2f})')
    return bytes(buf)


def build_hub_inject_specs():
    """RETIRED (build34): the 20 born-open GridEntrance hub portal instances. Superseded by the
    Model C boat-dialog rig (build_hub_extra_specs). No longer folded into INJECT_SPECS by
    merge_hub_into_inject_specs, and no longer applied to random09a by the swap path - it shipped
    the B-PORTAL-1/2/3 bugs (blue-pane render, walkway force-teleport, dead returns from every
    appended SV-only host) that Will retired. Kept here (unused) for reference + possible fallback.
    Returns a dict of (level_key -> [specs]) - the 20 hub portal instances."""
    R09_KEY = 'levels/world/orient/underground/random09a.lvl'
    hub = {R09_KEY: []}
    for i, (dest_key, dest_lvl, land_xyz, ret_xyz) in enumerate(_HUB_DESTS):
        cave_entrance, dest_landing, dest_ret_entrance, cave_ret_landing = _hub_pair_0x14(dest_key)
        # Cave entrance S<i> (portal_olympianarena1, -> dest)
        ex, ey, ez = _HUB_CAVE_ENTRANCES[i]
        hub[R09_KEY].append((PORTAL_OLYMPIANARENA1_DBR, ex, ey, ez, {'x14_payload': cave_entrance}))
        # Cave return landing S<i+5> (portal_olympianarena2, landing from dest)
        rx, ry, rz = _HUB_CAVE_RETURNS[i]
        hub[R09_KEY].append((PORTAL_OLYMPIANARENA2_DBR, rx, ry, rz, {'x14_payload': cave_ret_landing}))
        # Dest landing (portal_olympianarena2) + dest return-entrance (portal_olympianarena1)
        lx, ly, lz = land_xyz
        rex, rey, rez = ret_xyz
        hub.setdefault(dest_lvl, [])
        hub[dest_lvl].append((PORTAL_OLYMPIANARENA2_DBR, lx, ly, lz, {'x14_payload': dest_landing}))
        hub[dest_lvl].append((PORTAL_OLYMPIANARENA1_DBR, rex, rey, rez, {'x14_payload': dest_ret_entrance}))
    return hub


def merge_hub_into_inject_specs(base_specs):
    """Return a NEW INJECT_SPECS dict = base_specs with the TEST-HUB extras appended
    (order-preserving: hub entities are APPENDED after any base entries on the same level, so base
    instance indices are unchanged -> the flag-OFF/canonical build's non-hub blobs stay
    byte-identical). Does not mutate base_specs.

    build34: RETIRES the born-open GridEntrance hub (build_hub_inject_specs is NO LONGER folded in;
    it shipped the retired B-PORTAL-1/2/3 bugs). Folds in ONLY build_hub_extra_specs (the monster
    test yard + the Model C portal rig). The random09a (R09_LVL_KEY) entry is EXCLUDED here because
    random09a is rebuilt from the SV blood-cave blob by the special swap path in
    svaera_plus_portals.py; the normal INJECT_SPECS loop would inject into the DISCARDED AE blob
    (and, worse, leaving R09 in inject_specs makes ae_patched_blobs override the swap at compaction
    -> TESTHUB random09a would wrongly become the AE silkroad blob, the pre-existing build33 quirk).
    The swap path applies build_hub_extra_specs()[R09_LVL_KEY] directly to the SV swap blob."""
    out = {k: list(v) for k, v in base_specs.items()}
    for k, specs in build_hub_extra_specs().items():
        if k == R09_LVL_KEY:
            continue  # applied via the swap path (SV blood-cave blob), not the normal loop
        out.setdefault(k, [])
        out[k] = list(out[k]) + list(specs)
    return out


UBER_DUNGEON_QUEST_NAMES = ['Quests/uberdungeon_entrance.qst', 'Quests/uberdungeon_return.qst']
BLOODCAVE_QUEST_NAMES = ['Quests/bloodcave_entrance.qst', 'Quests/bloodcave_return.qst']
ALL_CUSTOM_QUEST_NAMES = UBER_DUNGEON_QUEST_NAMES + BLOODCAVE_QUEST_NAMES


# Identity 3x3 rotation matrix (flat, row-major) - the default when a spec omits 'rot'.
IDENTITY_ROT = (1.0, 0.0, 0.0,
                0.0, 1.0, 0.0,
                0.0, 0.0, 1.0)


def _normalize_spec(spec):
    """Normalize an injection spec into
    (dbr_bytes, x, y, z, flags, uniqueid, wants_0x14, rot, x14_payload).

    Accepts a 4-tuple (dbr, x, y, z) or a 5-tuple (dbr, x, y, z, opts_dict). opts keys:
    'flags' (int, default 0), 'uniqueid' (16 raw bytes, default 16 zero bytes),
    'wants_0x14' (bool, default False), 'rot' (a 9-float flat row-major 3x3 rotation
    matrix, default IDENTITY_ROT), 'x14_payload' (raw bytes, default None). Asserts hard
    on malformed opts so a bad spec can never silently corrupt a blob.

    'rot' carries the entity's SV-original ORIENTATION so an injected record is byte-exact
    to SV's own placement (not just position-exact). SV orients some entities off-identity
    (e.g. the Hades merchant wagon at ~141.5deg yaw, widow_ling at ~-66deg yaw); writing
    identity there would face them the wrong way and risk clipping terrain/walls differently
    than SV authored. Pass the exact SV float32 values (full precision) so struct.pack
    reproduces SV's rotation bytes exactly.

    'x14_payload' carries the EXACT per-instance 0x14 metadata bytes to append for this
    instance (used when the native placement being mirrored carries a specific 0x14 entry
    that is NOT the generic 20-byte default). Setting it implies wants_0x14=True. Example:
    every native v0x11 NpcCaravan carries a 12-byte 0x14 payload (2,0,1) - to byte-mirror a
    working caravan the injected record must carry that same 12-byte entry (not the 20-byte
    default). When None, a wanting instance gets DEFAULT_0x14_PAYLOAD (20 bytes).
    """
    if len(spec) == 4:
        dbr, x, y, z = spec
        opts = {}
    elif len(spec) == 5:
        dbr, x, y, z, opts = spec
        if not isinstance(opts, dict):
            raise ValueError(f'injection spec opts must be a dict, got {type(opts)}: {spec!r}')
    else:
        raise ValueError(f'injection spec must be a 4- or 5-tuple, got len {len(spec)}: {spec!r}')
    flags = int(opts.get('flags', 0))
    uniqueid = opts.get('uniqueid', b'\x00' * 16)
    if not isinstance(uniqueid, (bytes, bytearray)) or len(uniqueid) != 16:
        raise ValueError(f'injection spec uniqueid must be exactly 16 bytes: {spec!r}')
    if flags == 0 and uniqueid != b'\x00' * 16:
        raise ValueError(
            f'injection spec sets a non-zero uniqueid but flags==0; the trailing UniqueId '
            f'block only exists when flags != 0 (SV rule). Set flags=1: {spec!r}')
    rot = tuple(opts.get('rot', IDENTITY_ROT))
    if len(rot) != 9:
        raise ValueError(f'injection spec rot must be exactly 9 floats (flat 3x3): {spec!r}')
    rot = tuple(float(v) for v in rot)
    x14_payload = opts.get('x14_payload', None)
    if x14_payload is not None:
        if not isinstance(x14_payload, (bytes, bytearray)):
            raise ValueError(f'injection spec x14_payload must be raw bytes: {spec!r}')
        x14_payload = bytes(x14_payload)
        # BORN-OPEN ENTRANCE (round 2): the entrance record portal_olympianarena1 is now a
        # static GridEntrance, whose GridEntrance::Read consumes a 60-byte 0x14 (12-byte
        # (2,0,1) prefix + 48-byte binding). Every portal_olympianarena1 spec passes a bare
        # 48-byte binding (mouth+exit+dest); prepend the prefix here so the on-disk 0x14 is
        # the 60-byte GridEntrance shape. Landings (portal_olympianarena2, GridExitOneWay)
        # keep their 48-byte 0x14. Idempotent-guarded: if a 60-byte payload is ever passed
        # directly it is left as-is. See docs/DYNGRID_GATE_RCA.md sec 5 + the constant above.
        if bytes(dbr).replace(b'/', b'\\').lower() == PORTAL_OLYMPIANARENA1_DBR.replace(b'/', b'\\').lower():
            if len(x14_payload) == 48:
                x14_payload = GRIDENTRANCE_0x14_PREFIX + x14_payload
            elif len(x14_payload) == 60 and x14_payload[:12] == GRIDENTRANCE_0x14_PREFIX:
                pass  # already prefixed (idempotent)
            else:
                raise ValueError(
                    f'portal_olympianarena1 entrance x14_payload must be a 48-byte binding '
                    f'(to be prefixed to 60) or an already-60-byte GridEntrance payload; '
                    f'got {len(x14_payload)} bytes: {spec!r}')
    # x14_payload implies wants_0x14; otherwise honor the explicit flag.
    wants_0x14 = bool(opts.get('wants_0x14', False)) or (x14_payload is not None)
    return (bytes(dbr), float(x), float(y), float(z), flags, bytes(uniqueid), wants_0x14,
            rot, x14_payload)


def _build_0x05_record(str_idx, x, y, z, flags, uniqueid, base_size, rot=IDENTITY_ROT):
    """Build one 0x05 instance record, byte-exact to SV/AE layout.

    base_size = 56 (v0x0e) or 72 (v0x11). Measured record layout (probe_v11_flagged.py):
      core (56 B) = str_idx(4) + rotation 3x3(36) + position(12) + flags(4)
      then, in order:
        * a 16-byte UniqueId block IFF flags != 0  (v0e: bytes +56..+72; v11: +56..+72)
        * a 16-byte ZERO PAD block IFF the section is v0x11 (the pad v0e->v11 appends to
          EVERY record; v11: unflagged +56..+72, flagged +72..+88)
    So the four cases are: v0e unflagged=56, v0e flagged=72, v11 unflagged=72,
    v11 flagged=88 - exactly the sizes the flag-walk (`base + 16 if flags`) implies and
    the SV 0.98i HiddenValley01 shrine (v0e, 72 B, UniqueId at +56) confirms.

    rot = flat row-major 3x3 rotation matrix (9 floats). Defaults to identity; pass SV's
    exact float32 values to reproduce SV's orientation bytes exactly.
    """
    if base_size not in (56, 72):
        raise ValueError(f'unsupported 0x05 base record size {base_size}')
    if len(rot) != 9:
        raise ValueError(f'rotation matrix must be 9 floats, got {len(rot)}')
    core = struct.pack('<I', str_idx)                        # string_index
    core += struct.pack('<fffffffff', *rot)                   # 3x3 rotation (SV-exact or identity)
    core += struct.pack('<fff', x, y, z)                       # world position
    core += struct.pack('<I', flags)                           # flags
    assert len(core) == 56
    record = bytearray(core)
    if flags != 0:
        record += uniqueid                                     # 16-byte UniqueId
    if base_size == 72:
        record += b'\x00' * 16                                 # v0x11 trailing zero pad
    return bytes(record)


def inject_into_0x05(section_data, injections):
    """Append new objects to a v0x0e 0x05 section.

    section_data: raw bytes of the 0x05 section
    injections: list of specs (see _normalize_spec: 4-tuple or 5-tuple with opts)

    Returns modified section_data with new strings and instance records appended.

    v0x0e 0x05 format:
      uint32 string_count
      string_count * {uint32 length, char[length] dbr_path}
      uint32 instance_count
      instance_count * 56-byte records:
        +0:  uint32  string_index
        +4:  float[9] rotation_matrix (3x3, flat row-major, no padding)
        +40: float   world_x
        +44: float   world_y
        +48: float   world_z
        +52: uint32  flags (0 = normal)
    """
    if not injections:
        return section_data

    pos = 0
    string_count = struct.unpack_from('<I', section_data, pos)[0]
    pos += 4

    existing_strings = []
    for _ in range(string_count):
        slen = struct.unpack_from('<I', section_data, pos)[0]
        pos += 4
        existing_strings.append(section_data[pos:pos + slen])
        pos += slen

    strings_end = pos
    instance_count = struct.unpack_from('<I', section_data, strings_end)[0]
    instances_start = strings_end + 4
    instances_data = section_data[instances_start:]

    new_strings = list(existing_strings)
    new_instances = bytearray(instances_data)
    new_instance_count = instance_count

    for spec in injections:
        dbr_bytes, x, y, z, flags, uniqueid, _wants14, rot, _x14pl = _normalize_spec(spec)
        if dbr_bytes in new_strings:
            str_idx = new_strings.index(dbr_bytes)
        else:
            str_idx = len(new_strings)
            new_strings.append(dbr_bytes)
        new_instances += _build_0x05_record(str_idx, x, y, z, flags, uniqueid,
                                            base_size=56, rot=rot)
        new_instance_count += 1

    out = bytearray()
    out += struct.pack('<I', len(new_strings))
    for s in new_strings:
        out += struct.pack('<I', len(s))
        out += s
    out += struct.pack('<I', new_instance_count)
    out += new_instances
    return bytes(out)


def inject_into_sv_only_blob(blob, injections, level_name):
    """Inject objects into an SV-only level blob by modifying its 0x05 section, and
    (NEW) append per-instance 0x14 bindings for any spec that carries an x14_payload.

    0x14 support (needed for the Sparta Crypt L2 entrance's GridExitOneWay landing +
    GridEntranceDynamic return portal, which live in the SV-only SpartaCryptLevel2 and
    each need a 48-byte 0x14 binding - the A1 machinery, now for an SV-only level):
      * A 0x14 entry is keyed by INSTANCE INDEX. The injected instances occupy the tail
        [orig_instance_count, new_instance_count) in spec order, so a spec's binding is
        keyed by (orig_instance_count + spec_index) - IDENTICAL accounting to the shared-
        level step-7 append in svaera_plus_portals.
      * The 0x14 section is preserved verbatim and only APPENDED to; a hard collision
        assert guards against index mis-accounting. If the blob has NO 0x14 section but a
        spec wants one, a fresh 0x14 section is created (SpartaCryptLevel2 already has an
        empty 0x14 section, so this is a defensive fallback, matching maze03's empty-0x14).
      * Backward-compatible: specs without x14_payload (the Hemorrheus proxy, widow trio,
        finalletter) append NO 0x14 entry, so existing SV-only injections are unchanged.
    """
    secs, magic = parse_blob_sections(blob)
    if not secs:
        return blob

    # Count original 0x05 instances BEFORE injection (for 0x14 index accounting).
    orig_instance_count = 0
    for s in secs:
        if s['type'] == 0x05:
            orig_instance_count = count_0x05_instances(s['data'])
            break

    # Decide which injected instances want a 0x14 entry (tail index + payload).
    want_idx = []  # list of (instance_index, payload_bytes)
    for j, spec in enumerate(injections):
        _, _, _, _, _flags, _uid, wants_0x14, _rot, x14pl = _normalize_spec(spec)
        if wants_0x14:
            want_idx.append((orig_instance_count + j,
                             x14pl if x14pl is not None else DEFAULT_0x14_PAYLOAD))

    modified = False
    has_0x14 = any(s['type'] == 0x14 for s in secs)
    new_secs = []
    for s in secs:
        if s['type'] == 0x05 and injections:
            new_data = inject_into_0x05(s['data'], injections)
            new_secs.append({'type': 0x05, 'data': new_data})
            modified = True
            print(f'    Injected {len(injections)} object(s) into SV-only {level_name}')
        elif s['type'] == 0x14 and want_idx:
            merged = _append_0x14_entries(s['data'], want_idx, level_name)
            new_secs.append({'type': 0x14, 'data': merged})
            modified = True
        else:
            new_secs.append(s)

    # If a 0x14 was requested but the blob had no 0x14 section, create one now.
    if want_idx and not has_0x14:
        created = _append_0x14_entries(b'', want_idx, level_name)
        # Insert 0x14 right after 0x05 (its canonical neighbour), else append.
        insert_at = len(new_secs)
        for i, s in enumerate(new_secs):
            if s['type'] == 0x05:
                insert_at = i + 1
                break
        new_secs.insert(insert_at, {'type': 0x14, 'data': created})
        modified = True
        print(f'    Created 0x14 section in SV-only {level_name} '
              f'({len(want_idx)} binding(s))')

    if modified:
        return rebuild_blob(magic, new_secs)
    return blob


def _append_0x14_entries(orig_0x14_data, want_idx, level_name):
    """Append (index, payload) entries to an existing 0x14 section body, VERBATIM +
    append-only, with a hard collision assert (mirrors svaera_plus_portals step-7).

    orig_0x14_data may be b'' (create a fresh section). Each 0x14 record is
    index(4) + payload_size(4) + payload.
    """
    orig = bytearray(orig_0x14_data)
    existing_idx = set()
    pos = 0
    while pos + 8 <= len(orig):
        idx = struct.unpack_from('<I', orig, pos)[0]
        psz = struct.unpack_from('<I', orig, pos + 4)[0]
        existing_idx.add(idx)
        pos += 8 + psz
    for idx, payload in want_idx:
        if idx in existing_idx:
            raise ValueError(
                f'0x14 append collision in SV-only {level_name}: instance index {idx} '
                f'already has a 0x14 entry. The 0x05 injection accounting is wrong; '
                f'refusing to corrupt the blob.')
        orig += struct.pack('<II', idx, len(payload))
        orig += payload
        existing_idx.add(idx)
    print(f'    0x14: appended {len(want_idx)} binding(s) to SV-only {level_name} '
          f'(instance idx {[i for i, _ in want_idx]})')
    return bytes(orig)


V0E_RECORD_SIZE = 56
V11_RECORD_SIZE = 72
V0E_MAGIC = struct.pack('<I', 0x0e4c564c)
V11_MAGIC = struct.pack('<I', 0x114c564c)


def transplant_rec02(donor_0x0b_data, target_ints_raw):
    """Transplant a real 0x0b (REC\\x02) section from a donor SVAERA level.

    Patches the header (GUID blocks, center coords, dimensions) to match
    the target level while keeping the donor's sub-records and mesh data
    intact. The mesh data is in local coordinates relative to the level
    center, so updating the header repositions the entire mesh.

    Header layout (variable size based on difficulty_count N):
      [0-11]:       REC\\x02 magic + uint32(1) + uint32(payload_size)
      [12-15]:      uint32 difficulty_count (N)
      [16..16+N*16]: N x 16-byte GUID/hash blocks
      [+0..+12]:    Level center (3 x int32)
      [+12..+24]:   Level dimensions (3 x uint32)
      [+24..]:      Sub-records and mesh data (unchanged)
    """
    data = bytearray(donor_0x0b_data)

    if len(data) < 88 or data[:4] != b'REC\x02':
        return bytes(data)

    vals = struct.unpack_from('<13i', target_ints_raw, 0)
    uvals = struct.unpack_from('<13I', target_ints_raw, 0)
    guid = target_ints_raw[36:52]  # ints_raw[9..12]

    # Read difficulty count to find field offsets. This is the number of
    # 16-byte GUID/hash blocks between the fixed header and the center/dims.
    # Real TQAE 0x0b sections use a WIDE range here (surveyed 1..13 across the
    # 2214 SVAERA 0x0b levels; ~half are >4), so it must NOT be capped at 4.
    # Capping it (the old `>4 -> 3` guard) put center_start at the wrong offset
    # for any donor with diff_count>4, so the center/dims were written INTO the
    # GUID region and the real center stayed at the donor's position -> the
    # transplanted navmesh was NOT repositioned. Only fall back if the value is
    # implausible for the actual section length.
    diff_count = struct.unpack_from('<I', data, 12)[0]
    if diff_count < 1 or 16 + diff_count * 16 + 24 > len(data):
        diff_count = 3  # implausible header; safe default

    guid_start = 16
    center_start = guid_start + diff_count * 16
    dims_start = center_start + 12

    if dims_start + 12 > len(data):
        return bytes(data)

    # Patch GUID blocks
    for i in range(diff_count):
        off = guid_start + i * 16
        data[off:off + 16] = guid

    # Patch center coords (grid_corner + half_dimensions)
    center_x = vals[6] + vals[3]
    center_y = vals[7] + vals[1]
    center_z = vals[8] + vals[5]
    struct.pack_into('<iii', data, center_start, center_x, center_y, center_z)

    # Patch dimensions
    dim_x = uvals[3] + 16
    dim_y = max(uvals[4] - 4, 1) if uvals[4] >= 5 else uvals[4] + 12
    dim_z = uvals[5] + 16
    struct.pack_into('<III', data, dims_start, dim_x, dim_y, dim_z)

    return bytes(data)


def build_minimal_rec02(ints_raw):
    """Build a minimal valid 0x0b (REC\\x02) section body.

    Contains the REC\\x02 header with correct level coords plus the standard
    44-byte Recast parameter header and zero tile counts.  This is enough for
    ProcessRLTD to initialize the RLTD handler with valid Recast build
    parameters.  Level::CreatePathMesh / ProcessRLTD_flow can then generate
    the actual navigation mesh from the level's entity geometry at runtime.

    REC\\x02 format:
      [0-3]:   'REC\\x02' magic
      [4-7]:   uint32 version = 1
      [8-11]:  uint32 payload_size (everything after first 12 bytes)
      [12-15]: uint32 diff_count (3 = Normal/Epic/Legendary)
      [16-63]: 3 x 16-byte GUID blocks
      [64-75]: center coords (3 x int32)
      [76-87]: dimensions (3 x uint32)
      --- Body ---
      [88-131]:  44-byte Recast parameter header (standard values)
      [132-147]: 4 x uint32 tile counts = 0 (no pre-built tiles)
    """
    vals = struct.unpack_from('<13i', ints_raw, 0)
    uvals = struct.unpack_from('<13I', ints_raw, 0)
    guid = ints_raw[36:52]  # ints_raw[9..12]

    diff_count = 3
    # Center = grid_corner + half_dimensions
    center_x = vals[6] + vals[3]
    center_y = vals[7] + vals[1]
    center_z = vals[8] + vals[5]
    # Dimensions with padding (matching transplant_rec02 logic)
    dim_x = uvals[3] + 16
    dim_y = max(uvals[4] - 4, 1) if uvals[4] >= 5 else uvals[4] + 12
    dim_z = uvals[5] + 16

    data = bytearray()
    data += b'REC\x02'                              # magic
    data += struct.pack('<I', 1)                     # version
    data += struct.pack('<I', 0)                     # payload_size (patched below)
    data += struct.pack('<I', diff_count)            # diff_count
    for _ in range(diff_count):
        data += guid                                 # GUID blocks
    data += struct.pack('<3i', center_x, center_y, center_z)  # center
    data += struct.pack('<3I', dim_x, dim_y, dim_z)  # dimensions

    # 44-byte Recast parameter header (identical across all TQAE levels)
    data += struct.pack('<3f', 0.0, 0.0, 0.0)        # 3x zero
    data += struct.pack('<2f', 0.2, 0.2)              # cellSize, cellHeight
    data += struct.pack('<2I', 64, 64)                # tileSize (cells)
    data += struct.pack('<f', 2.0)                    # agentHeight
    data += struct.pack('<f', 0.4)                    # agentMaxClimb
    data += struct.pack('<f', 1.0)                    # agentRadius
    data += struct.pack('<f', 1.3)                    # unknown param

    # 4 x uint32 tile counts = 0 (no pre-built tiles)
    data += struct.pack('<4I', 0, 0, 0, 0)

    # Patch payload_size = total - 12 (magic + version + payload_size field)
    struct.pack_into('<I', data, 8, len(data) - 12)

    return bytes(data)


def inject_rec02_into_blob(blob, ints_raw, donor_data=None, use_stub=False,
                           pre_positioned=False):
    """Add a 0x0b (REC\\x02) section to a level blob that lacks one.

    Three donor modes (checked in this order):
      * use_stub=True: build a minimal REC\\x02 stub with Recast parameters but
        no pre-built tiles (the dead-code fallback; kept so levels with NO donor
        - e.g. the 7 ocean-scenery blood-cave levels - still get a valid, if
        empty, section and the build stays green).
      * pre_positioned=True with donor_data: insert donor_data VERBATIM. The
        donor is an already-correct 0x0b (e.g. from tools/gen_bc_navmeshes.py):
        its GUID list already resolves in the merged world and its center is
        already shifted to the merged grid. transplant_rec02 must NOT run - it
        would overwrite the neighbor GUIDs with the own GUID and recompute the
        center from ints_raw, corrupting a section that is already right.
      * donor_data alone (pre_positioned=False): transplant_rec02(donor,
        ints_raw) - reposition an Editor-baked donor's header to this level's
        (shifted) grid. Kept for any future Editor-baked donor.

    Also strips any 0x0a sections to prevent ProcessRLTD reinit from undoing
    the 0x0b handler state (0x0a routes to the same handler via Engine.dll patch).

    Returns the modified blob, or the original if it already has 0x0b.
    """
    secs, magic = parse_blob_sections(blob)
    if not secs:
        return blob

    # Check if 0x0b already exists
    if any(s['type'] == 0x0b for s in secs):
        return blob

    if use_stub:
        rec02_data = build_minimal_rec02(ints_raw)
    elif donor_data is not None and pre_positioned:
        # Already-correct 0x0b: insert as-is (no transplant repositioning).
        rec02_data = donor_data
    elif donor_data is not None:
        rec02_data = transplant_rec02(donor_data, ints_raw)
    else:
        return blob

    # Strip any 0x0a sections (would re-trigger ProcessRLTD init after 0x0b)
    secs = [s for s in secs if s['type'] != 0x0a]

    # Insert 0x0b after 0x09 (grid) if present, otherwise at end before 0x17
    insert_idx = len(secs)
    for i, s in enumerate(secs):
        if s['type'] == 0x09:
            insert_idx = i + 1
            break
        elif s['type'] == 0x17:
            insert_idx = i
            break

    secs.insert(insert_idx, {'type': 0x0b, 'data': rec02_data})
    return rebuild_blob(magic, secs)


def convert_0x05_v0e_to_v11(data):
    """Convert v0x0e 0x05 section data (56-byte records) to v0x11 format (72-byte records).

    The string table is identical between formats. Only the instance records differ:
    v0x11 has 16 extra zero bytes appended to each 56-byte v0x0e record.
    """
    pos = 0
    string_count = struct.unpack_from('<I', data, pos)[0]
    pos += 4

    # Skip past string table (identical format)
    for _ in range(string_count):
        if pos + 4 > len(data):
            return None
        slen = struct.unpack_from('<I', data, pos)[0]
        pos += 4 + slen

    strings_end = pos
    if strings_end + 4 > len(data):
        return None

    instance_count = struct.unpack_from('<I', data, strings_end)[0]
    instances_start = strings_end + 4
    instances_data = data[instances_start:]

    expected = instance_count * V0E_RECORD_SIZE
    if len(instances_data) < expected:
        return None

    # Build v0x11 instance data: each v0x0e 56-byte record + 16 zero bytes
    v11_instances = bytearray()
    for i in range(instance_count):
        offset = i * V0E_RECORD_SIZE
        v11_instances += instances_data[offset:offset + V0E_RECORD_SIZE]
        v11_instances += b'\x00' * 16

    # Reassemble: string table (unchanged) + v0x11 instance records
    out = bytearray(data[:strings_end])
    out += struct.pack('<I', instance_count)
    out += v11_instances
    # Include any trailing data after instances (unlikely but safe)
    trailing_start = instances_start + expected
    if trailing_start < len(data):
        out += data[trailing_start:]
    return bytes(out)


def inject_into_0x05_v11(section_data, injections):
    """Append new objects to a v0x11 0x05 section.

    A v0x11 instance record is VARIABLE length: a 72-byte base record, plus a
    trailing 16-byte UniqueId block when the record's flags field (at +52) != 0
    (the v0x11 analogue of the v0e "56 + 16 if flags@52 != 0" rule the merge's
    v0e->v11 converter and the audit's SV-side parser both document). Some shared
    levels (e.g. RoadToTown03A: 23 of 288 records flagged = +368 bytes) carry these
    flagged records, so we MUST walk the existing instance block record-by-record to
    find its true end and preserve every original byte VERBATIM; slicing a fixed
    instance_count*72 would drop the flagged records' UniqueId tails and corrupt the
    v0x11 blob. New injected records are written unflagged (72 bytes, 16 zero pad).
    """
    if not injections:
        return section_data

    pos = 0
    string_count = struct.unpack_from('<I', section_data, pos)[0]
    pos += 4

    existing_strings = []
    for _ in range(string_count):
        slen = struct.unpack_from('<I', section_data, pos)[0]
        pos += 4
        existing_strings.append(section_data[pos:pos + slen])
        pos += slen

    strings_end = pos
    instance_count = struct.unpack_from('<I', section_data, strings_end)[0]
    instances_start = strings_end + 4
    # Variable-length walk over the existing records to find the true block end.
    ipos = instances_start
    for _ in range(instance_count):
        if ipos + V11_RECORD_SIZE > len(section_data):
            raise ValueError(
                f'v0x11 0x05 instance block underrun: expected {instance_count} '
                f'records, ran out of data after offset {ipos}')
        flags = struct.unpack_from('<I', section_data, ipos + 52)[0]
        ipos += V11_RECORD_SIZE + (16 if flags != 0 else 0)
    # Preserve the entire original instance block (base + any flagged UniqueId tails)
    # plus any trailing bytes exactly, so nothing existing is disturbed.
    instances_data = section_data[instances_start:ipos]
    tail_after_instances = section_data[ipos:]

    new_strings = list(existing_strings)
    new_instances = bytearray(instances_data)
    new_instance_count = instance_count

    for spec in injections:
        dbr_bytes, x, y, z, flags, uniqueid, _wants14, rot, _x14pl = _normalize_spec(spec)
        if dbr_bytes in new_strings:
            str_idx = new_strings.index(dbr_bytes)
        else:
            str_idx = len(new_strings)
            new_strings.append(dbr_bytes)
        # v0x11 record: 56-byte core (+16 UniqueId if flagged) + 16-byte zero pad.
        # Unflagged -> 72 B (old behaviour); flagged -> 88 B with the SV UniqueId at +56.
        new_instances += _build_0x05_record(str_idx, x, y, z, flags, uniqueid,
                                            base_size=72, rot=rot)
        new_instance_count += 1

    out = bytearray()
    out += struct.pack('<I', len(new_strings))
    for s in new_strings:
        out += struct.pack('<I', len(s))
        out += s
    out += struct.pack('<I', new_instance_count)
    out += new_instances
    # Any bytes after the instance block are not instance records; a correctly
    # parsed v0x11 0x05 section has none (tail is b''). Preserve defensively.
    out += tail_after_instances
    return bytes(out)


def move_0x05_instances(section_data, moves, base_size, level_name=''):
    """Rewrite the POSITION (x,y,z) of EXISTING instances in a 0x05 section IN PLACE.

    Used to reposition NATIVE records the merge already placed (e.g. moving the
    HiddenValleyBorder04 Horse02 + silkroad_villager1 so the caravan scene composes
    around the moved wagon without the wagon overlapping the occultist merchant). Only
    the 12 position bytes (at record offset +40) are overwritten; string_index, rotation,
    flags, UniqueId tail, and the v11 zero pad are all preserved byte-for-byte, so the
    record's shape and every other field are untouched. This is a surgical, bounded edit
    (no append, no reindex) - the safest way to move an existing instance.

    moves: list of dicts {dbr: bytes, x, y, z, nth (optional, default match ALL instances
    of that dbr), match (optional 'all'|'first'|int index-among-that-dbr)}. To disambiguate
    when a level places the same record several times, pass match=<k> to move only the k-th
    (0-based) instance of that dbr, or the exact current (x,y,z) via 'from_xyz' to target one.

    A hard assert fires if a move matches ZERO instances (so a typo cannot silently no-op).
    base_size = 56 (v0e) or 72 (v11); records are walked flag-aware (+16 if flags@+52 != 0).
    Returns the modified section bytes.
    """
    if not moves:
        return section_data

    pos = 0
    string_count = struct.unpack_from('<I', section_data, pos)[0]
    pos += 4
    strings = []
    for _ in range(string_count):
        slen = struct.unpack_from('<I', section_data, pos)[0]
        pos += 4
        strings.append(section_data[pos:pos + slen])
        pos += slen
    strings_end = pos
    instance_count = struct.unpack_from('<I', section_data, strings_end)[0]
    instances_start = strings_end + 4

    # normalize moves -> {str_idx: [ (matcher, x,y,z) ]}
    norm = []
    for mv in moves:
        dbr = mv['dbr']
        if dbr not in strings:
            raise ValueError(f'move target dbr not present in {level_name} 0x05 string '
                             f'table: {dbr!r}')
        sidx = strings.index(dbr)
        norm.append(dict(sidx=sidx, x=float(mv['x']), y=float(mv['y']), z=float(mv['z']),
                         match=mv.get('match', 'all'), from_xyz=mv.get('from_xyz'),
                         dbr=dbr, hits=0))

    buf = bytearray(section_data)
    ipos = instances_start
    per_dbr_seen = {}
    for _ in range(instance_count):
        if ipos + base_size > len(buf):
            raise ValueError(f'0x05 instance underrun while moving in {level_name}')
        rec_sidx = struct.unpack_from('<I', buf, ipos)[0]
        cx, cy, cz = struct.unpack_from('<3f', buf, ipos + 40)
        flags = struct.unpack_from('<I', buf, ipos + 52)[0]
        rec_size = base_size + (16 if flags != 0 else 0)
        k = per_dbr_seen.get(rec_sidx, 0)
        for m in norm:
            if m['sidx'] != rec_sidx:
                continue
            take = False
            if m['from_xyz'] is not None:
                fx, fy, fz = m['from_xyz']
                take = (abs(cx - fx) < 0.5 and abs(cy - fy) < 0.5 and abs(cz - fz) < 0.5)
            elif m['match'] == 'all':
                take = True
            elif m['match'] == 'first':
                take = (k == 0)
            elif isinstance(m['match'], int):
                take = (k == m['match'])
            if take:
                struct.pack_into('<3f', buf, ipos + 40, m['x'], m['y'], m['z'])
                m['hits'] += 1
        per_dbr_seen[rec_sidx] = k + 1
        ipos += rec_size

    for m in norm:
        if m['hits'] == 0:
            raise ValueError(f'move matched ZERO instances in {level_name} for '
                             f'{m["dbr"]!r} (match={m["match"]}, from_xyz={m["from_xyz"]}) '
                             f'- refusing to silently no-op')
        print(f'    Moved {m["hits"]} instance(s) of {m["dbr"].decode("ascii","replace")} '
              f'in {level_name} -> ({m["x"]:.2f},{m["y"]:.2f},{m["z"]:.2f})')
    return bytes(buf)


def remove_0x05_instances_by_0x14_uid(blob, specs, level_name=''):
    """Remove ONE 0x05 instance (and its 0x14 binding) identified by a uid in its 0x14
    record, reindexing every later 0x14 record. The inverse of the append-only injectors.

    Used to delete the native GridExitOneWay LANDING (portal_olympianarena2) when a level is
    converted to a native 0x06 two-way door: the landing's 0x14 binding registers a portal
    with the SAME id the new 0x06 descriptor now owns, so it must go (Random09A, the walk-
    tested exemplar, has NO landing entity - only the descriptor). This is the "remove-by-uid
    path the section-surgery tooling did not have" the Uber-door RE flagged.

    Each spec: {'uid': 16B, 'uid_field': 'mouth'|'exit'|'dest', 'expect_dbr': bytes (the
    0x05 dbr the target instance MUST carry - safety), 'expect_0x14_size': int (48 or 60)}.
    Mechanism (fail-loud at every step):
      1. Find the SINGLE 0x14 record whose selected binding field == uid -> removed_idx.
      2. Walk the 0x05 section flag-aware (base 56 for v0x0e, 72 for v0x11/0x0f), assert it
         lands EXACTLY at the section end, and assert the instance at removed_idx carries
         expect_dbr. Excise that instance's record bytes; decrement the instance count. The
         string table is left intact (an orphan string is harmless and avoids reindexing
         every remaining instance's string index).
      3. Remove the 0x14 record at removed_idx; decrement the `index` of every 0x14 record
         whose index > removed_idx (the 0x05 instances after it shifted down by one). Re-
         assert the post-removal 0x05 flag-aware walk lands exactly at the new section end.
    Only 0x14 keys on the 0x05 instance index in these level blobs (0x06 keys by uid/cell;
    0x0b by GUID; 0x17 is terrain-bound resource hashes), so no other section is reindexed.
    """
    if not specs:
        return blob
    secs, magic = parse_blob_sections(blob)
    ver = magic[3] if magic[:3] == b'LVL' else None
    base = 72 if ver in (0x11, 0x0f) else 56
    d05 = d14 = None
    for s in secs:
        if s['type'] == 0x05:
            d05 = bytearray(s['data'])
        elif s['type'] == 0x14:
            d14 = bytearray(s['data'])
    if d05 is None or d14 is None:
        raise ValueError(f'{level_name}: remove-by-uid needs both 0x05 and 0x14 sections '
                         f'(0x05={d05 is not None}, 0x14={d14 is not None})')

    def _field_off(psz, fld):
        # 48B binding = [mouth 16][exit 16][dest 16]; 60B = [prefix 12] + the 48B binding
        prefix = 0 if psz == 48 else (12 if psz == 60 else None)
        if prefix is None:
            return None
        return prefix + {'mouth': 0, 'exit': 16, 'dest': 32}[fld]

    # parse 0x14 records once; the list is carried across specs (indices stay consistent)
    recs = []
    pos = 0
    while pos + 8 <= len(d14):
        idx, psz = struct.unpack_from('<II', d14, pos)
        if pos + 8 + psz > len(d14):
            raise ValueError(f'{level_name}: 0x14 truncated record at {pos}')
        recs.append({'index': idx, 'psz': psz, 'payload': bytes(d14[pos + 8:pos + 8 + psz])})
        pos += 8 + psz
    if pos != len(d14):
        raise ValueError(f'{level_name}: 0x14 walk did not consume the section '
                         f'({pos} != {len(d14)})')

    for spec in specs:
        uid = spec['uid']
        fld = spec['uid_field']
        assert len(uid) == 16
        # 1. locate the single matching 0x14 record
        hits = [r for r in recs
                if _field_off(r['psz'], fld) is not None
                and r['payload'][_field_off(r['psz'], fld):_field_off(r['psz'], fld) + 16] == uid]
        if len(hits) != 1:
            raise ValueError(f'{level_name}: 0x14 field {fld}=={uid.hex()[:12]}.. matched '
                             f'{len(hits)} record(s), expected exactly 1')
        target = hits[0]
        removed_idx = target['index']
        if 'expect_0x14_size' in spec and target['psz'] != spec['expect_0x14_size']:
            raise ValueError(f'{level_name}: 0x14 target size {target["psz"]} != expected '
                             f'{spec["expect_0x14_size"]}')
        # 2. excise the 0x05 instance at removed_idx (flag-aware, exact-consumption asserts)
        scount = struct.unpack_from('<I', d05, 0)[0]
        p = 4
        strings = []
        for _ in range(scount):
            sl = struct.unpack_from('<I', d05, p)[0]
            p += 4
            strings.append(bytes(d05[p:p + sl]))
            p += sl
        icount = struct.unpack_from('<I', d05, p)[0]
        icount_off = p
        inst_start = p + 4
        q = inst_start
        target_off = target_size = target_sidx = None
        for i in range(icount):
            if q + base > len(d05):
                raise ValueError(f'{level_name}: 0x05 instance underrun at i={i}')
            sidx = struct.unpack_from('<I', d05, q)[0]
            flags = struct.unpack_from('<I', d05, q + 52)[0]
            rs = base + (16 if flags != 0 else 0)
            if i == removed_idx:
                target_off, target_size, target_sidx = q, rs, sidx
            q += rs
        if q != len(d05):
            raise ValueError(f'{level_name}: 0x05 flag-aware walk did not land at section '
                             f'end ({q} != {len(d05)}); base={base}')
        if target_off is None:
            raise ValueError(f'{level_name}: 0x05 has no instance at index {removed_idx} '
                             f'(icount={icount})')
        tdbr = strings[target_sidx] if target_sidx < len(strings) else b''
        if 'expect_dbr' in spec:
            want = bytes(spec['expect_dbr']).replace(b'/', b'\\').lower()
            if tdbr.replace(b'/', b'\\').lower() != want:
                raise ValueError(f'{level_name}: 0x05 instance[{removed_idx}] dbr {tdbr!r} '
                                 f'!= expected {spec["expect_dbr"]!r}')
        new05 = bytearray(d05[:target_off]) + bytearray(d05[target_off + target_size:])
        struct.pack_into('<I', new05, icount_off, icount - 1)
        # re-assert the shrunk 0x05 still walks exactly to its end
        q2 = inst_start
        for _ in range(icount - 1):
            flags = struct.unpack_from('<I', new05, q2 + 52)[0]
            q2 += base + (16 if flags != 0 else 0)
        if q2 != len(new05):
            raise ValueError(f'{level_name}: post-removal 0x05 walk mismatch '
                             f'({q2} != {len(new05)})')
        d05 = new05
        print(f'    0x05 REMOVE {level_name}: inst[{removed_idx}] '
              f'{tdbr.decode("ascii", "replace").split(chr(92))[-1]} ({target_size} B) '
              f'icount {icount}->{icount - 1}')
        # 3. drop the 0x14 record at removed_idx; decrement index of records after it
        newrecs = []
        for r in recs:
            if r['index'] == removed_idx:
                continue
            ni = r['index'] - 1 if r['index'] > removed_idx else r['index']
            newrecs.append({'index': ni, 'psz': r['psz'], 'payload': r['payload']})
        print(f'    0x14 REMOVE {level_name}: dropped idx={removed_idx}, '
              f'{len(recs)}->{len(newrecs)} record(s)')
        recs = newrecs

    new14 = bytearray()
    for r in recs:
        new14 += struct.pack('<II', r['index'], r['psz'])
        new14 += r['payload']

    out_secs = []
    for s in secs:
        if s['type'] == 0x05:
            out_secs.append({'type': 0x05, 'data': bytes(d05)})
        elif s['type'] == 0x14:
            out_secs.append({'type': 0x14, 'data': bytes(new14)})
        else:
            out_secs.append(s)
    return rebuild_blob(magic, out_secs)


def remove_0x05_instances_by_dbr(blob, dbrs, level_name=''):
    """DE-PLACE every 0x05 instance whose .dbr string matches one of `dbrs`, reindexing the
    0x14 bindings of the instances that shift down. Returns (new_blob, removed_count).

    Used for MAP-REF-1 (M2): SV NPCs / setdress placed in a level whose record is ABSENT from
    the shipped arz (they silently fail to spawn - naked/missing content). De-placing the 0x05
    reference is the interim build30 fix (full restore = a 3169-record SVAERA economy import,
    deferred). MAP-REF-1 keys on records referenced by an ACTIVE INSTANCE, so removing the
    instance clears the violation (the now-orphan string is left in the table - harmless, and
    removing it would reindex every other instance's string index).

    `dbrs` = iterable of record paths (case/sep-insensitive, matched EXACTLY incl. any leading
    space - some SV setdress paths carry one). ALL instances of each matching dbr are removed
    (a record placed N times -> N removals). Fail-loud unless every dbr matches >= 1 instance
    (typo guard). Reindex rule (only 0x14 keys on the instance index in these blobs): a 0x14
    record bound to a removed instance is dropped; every other record's index decreases by the
    number of removed indices below it, so it keeps pointing at the SAME instance. Flag-aware
    walk (base 56 v0x0e / 72 v0x11-v0x0f) with exact-consumption asserts before and after.
    """
    want = {bytes(x).replace(b'/', b'\\').lower() for x in dbrs}
    if not want:
        return blob, 0
    secs, magic = parse_blob_sections(blob)
    ver = magic[3] if magic[:3] == b'LVL' else None
    base = 72 if ver in (0x11, 0x0f) else 56
    d05 = d14 = None
    for s in secs:
        if s['type'] == 0x05:
            d05 = bytearray(s['data'])
        elif s['type'] == 0x14:
            d14 = bytearray(s['data'])
    if d05 is None:
        raise ValueError(f'{level_name}: remove-by-dbr needs a 0x05 section')
    scount = struct.unpack_from('<I', d05, 0)[0]
    p = 4
    strings = []
    for _ in range(scount):
        sl = struct.unpack_from('<I', d05, p)[0]
        p += 4
        strings.append(bytes(d05[p:p + sl]))
        p += sl
    icount = struct.unpack_from('<I', d05, p)[0]
    icount_off = p
    inst_start = p + 4
    q = inst_start
    spans = []          # (index, off, size) for every instance, in order
    remove_idx = []     # indices to remove (ascending, since we walk in order)
    matched = set()
    for i in range(icount):
        if q + base > len(d05):
            raise ValueError(f'{level_name}: 0x05 instance underrun at i={i}')
        sidx = struct.unpack_from('<I', d05, q)[0]
        flags = struct.unpack_from('<I', d05, q + 52)[0]
        rs = base + (16 if flags != 0 else 0)
        sdbr = strings[sidx].replace(b'/', b'\\').lower() if sidx < len(strings) else b''
        spans.append((i, q, rs))
        if sdbr in want:
            remove_idx.append(i)
            matched.add(sdbr)
        q += rs
    if q != len(d05):
        raise ValueError(f'{level_name}: 0x05 flag-aware walk did not land at section end '
                         f'({q} != {len(d05)}); base={base}')
    missing = want - matched
    if missing:
        raise ValueError(f'{level_name}: remove-by-dbr matched NO instance for '
                         f'{len(missing)} requested dbr(s): '
                         f'{sorted(x.decode("ascii", "replace") for x in missing)[:6]}')
    remove_set = set(remove_idx)
    # rebuild 0x05 keeping non-removed instances in order; decrement icount
    keep = bytearray(d05[:inst_start])
    for (i, off, rs) in spans:
        if i not in remove_set:
            keep += d05[off:off + rs]
    struct.pack_into('<I', keep, icount_off, icount - len(remove_idx))
    q2 = inst_start
    for _ in range(icount - len(remove_idx)):
        flags = struct.unpack_from('<I', keep, q2 + 52)[0]
        q2 += base + (16 if flags != 0 else 0)
    if q2 != len(keep):
        raise ValueError(f'{level_name}: post-removal 0x05 walk mismatch ({q2} != {len(keep)})')
    # reindex 0x14: drop records bound to a removed instance; shift the rest down
    new14 = None
    if d14 is not None:
        pos = 0
        nb = bytearray()
        while pos + 8 <= len(d14):
            idx, psz = struct.unpack_from('<II', d14, pos)
            if pos + 8 + psz > len(d14):
                raise ValueError(f'{level_name}: 0x14 truncated record at {pos}')
            payload = d14[pos + 8:pos + 8 + psz]
            if idx not in remove_set:
                shift = sum(1 for r in remove_idx if r < idx)
                nb += struct.pack('<II', idx - shift, psz)
                nb += payload
            pos += 8 + psz
        if pos != len(d14):
            raise ValueError(f'{level_name}: 0x14 walk did not consume section '
                             f'({pos} != {len(d14)})')
        new14 = bytes(nb)
    out_secs = []
    for s in secs:
        if s['type'] == 0x05:
            out_secs.append({'type': 0x05, 'data': bytes(keep)})
        elif s['type'] == 0x14 and new14 is not None:
            out_secs.append({'type': 0x14, 'data': new14})
        else:
            out_secs.append(s)
    print(f'    0x05 DE-PLACE {level_name}: removed {len(remove_idx)} instance(s) of '
          f'{len(want)} dbr(s), icount {icount}->{icount - len(remove_idx)}')
    return rebuild_blob(magic, out_secs), len(remove_idx)


def count_0x05_instances(data):
    """Count instances in a 0x05 section (works for both v0x0e and v0x11)."""
    pos = 0
    string_count = struct.unpack_from('<I', data, pos)[0]
    pos += 4
    for _ in range(string_count):
        if pos + 4 > len(data):
            return 0
        slen = struct.unpack_from('<I', data, pos)[0]
        pos += 4 + slen
    if pos + 4 > len(data):
        return 0
    return struct.unpack_from('<I', data, pos)[0]


def generate_default_0x14(instance_count):
    """Generate default 0x14 records for all instances.

    Each record: index(4) + payload_size(4) + payload(20).
    Default payload: flags=2, 0, 1, 1, 0.
    """
    buf = bytearray()
    for i in range(instance_count):
        buf += struct.pack('<II', i, len(DEFAULT_0x14_PAYLOAD))
        buf += DEFAULT_0x14_PAYLOAD
    return bytes(buf)


def convert_v0e_blob_to_v11(blob, level_name=''):
    """Convert an entire v0x0e level blob to v0x11 format.

    Used for SV-only levels and shared levels where AE is also v0x0e.
    - Converts 0x05 instance records (56→72 bytes)
    - Removes 0x09 grid section (v0x0e-only, replaced by DATA2 in v0x11)
    - Adds 0x14 metadata section (required for v0x11 interactivity)
    - Changes blob magic from v0x0e to v0x11
    """
    secs, magic = parse_blob_sections(blob)
    if not secs:
        return None

    new_secs = []
    instance_count = 0
    has_0x14 = False

    for s in secs:
        if s['type'] == 0x05:
            # Convert 0x05 from 56-byte to 72-byte records
            converted = convert_0x05_v0e_to_v11(s['data'])
            if converted is None:
                return None
            new_secs.append({'type': 0x05, 'data': converted})
            instance_count = count_0x05_instances(converted)
        elif s['type'] == 0x09:
            # Skip 0x09 grid section (v0x0e-only)
            continue
        elif s['type'] == 0x0a:
            # Keep 0x0a as-is (PTH\x04 TQIT pathfinding - different format from 0x0b/REC\x02)
            new_secs.append({'type': 0x0a, 'data': s['data']})
        elif s['type'] == 0x14:
            has_0x14 = True
            new_secs.append(s)
        else:
            new_secs.append(s)

    # Add 0x14 metadata if not already present
    if not has_0x14 and instance_count > 0:
        new_secs.append({'type': 0x14, 'data': generate_default_0x14(instance_count)})

    return rebuild_blob(V11_MAGIC, new_secs)


def perform_section_surgery(ae_blob, sv_blob, level_name):
    """
    Hybrid blob: inject SV's drxmap objects into SVAERA's level blob.

    Format-aware: detects AE blob's version (v0x11 vs v0x0e) and handles accordingly:
    - v0x11 AE blob: Convert SV's v0x0e 0x05 records (56-byte) to v0x11 (72-byte),
      keep v0x11 magic and all SVAERA terrain/pathfinding sections.
      Generates default 0x14 metadata for all instances (required for v0x11 interactivity).
    - v0x0e AE blob (e.g. Random09A): Return 'use_sv_blob' signal to caller,
      since both versions share the same format and SV's blob has the grid connection.
    """
    ae_secs, ae_magic = parse_blob_sections(ae_blob)
    sv_secs, sv_magic = parse_blob_sections(sv_blob)

    if not ae_secs or not sv_secs:
        return None, "empty sections"

    sv_05 = [s for s in sv_secs if s['type'] == 0x05]
    if not sv_05:
        return None, "SV has no 0x05 section"
    if b'drxmap' not in sv_05[0]['data']:
        return None, "SV 0x05 has no drxmap"

    ae_version = struct.unpack_from('<B', ae_magic, 3)[0] if len(ae_magic) >= 4 else 0

    # v0x0e AE blobs (e.g. Random09A): use SV's full blob instead of surgery.
    # Both versions share the same format and SV's blob has grid connections (0x09).
    if ae_version != 0x11:
        return None, "use_sv_blob"

    # v0x11 AE blob: convert SV's v0x0e 0x05 data to v0x11 format
    sv_05_data = sv_05[0]['data']

    # First convert 56-byte records to 72-byte records
    v11_05_data = convert_0x05_v0e_to_v11(sv_05_data)
    if v11_05_data is None:
        return None, "failed to convert 0x05 v0e->v11"

    # Inject any new objects (portals, targets) using v0x11 format
    level_key = level_name.replace('\\', '/').lower()
    if level_key in INJECT_SPECS:
        v11_05_data = inject_into_0x05_v11(v11_05_data, INJECT_SPECS[level_key])
        print(f'    Injected {len(INJECT_SPECS[level_key])} object(s) into 0x05 (v0x11)')

    # Generate default 0x14 metadata for all instances in the new 0x05
    # v0x11 levels require 0x14 records for objects to be interactive (fountains, etc.)
    instance_count = count_0x05_instances(v11_05_data)
    new_0x14_data = generate_default_0x14(instance_count)

    new_secs = []
    for s in ae_secs:
        if s['type'] == 0x05:
            new_secs.append({'type': 0x05, 'data': v11_05_data})
        elif s['type'] == 0x14:
            new_secs.append({'type': 0x14, 'data': new_0x14_data})
        else:
            new_secs.append(s)

    # Keep v0x11 magic - matching SVAERA's terrain/pathfinding format
    result = rebuild_blob(ae_magic, new_secs)

    sv_05_count = struct.unpack_from('<I', sv_05[0]['data'], 0)[0]
    ae_05 = [s for s in ae_secs if s['type'] == 0x05]
    ae_05_count = struct.unpack_from('<I', ae_05[0]['data'], 0)[0] if ae_05 else 0
    drx_count = result.count(b'drxmap')
    return result, f"hybrid v11: strings {ae_05_count}->{sv_05_count}, 0x14: {instance_count} records, drxmap: {drx_count}"


def main():
    print('Loading SVAERA...')
    ae_arc = ArcArchive.from_file(svaera_arc_path)
    ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
    ae_sections = parse_sections(ae_data)
    ae_sec_map = {s['type']: s for s in ae_sections}
    ae_levels = parse_level_index(ae_data, ae_sec_map[SEC_LEVELS])
    ae_quests = parse_quests(ae_data, ae_sec_map[SEC_QUESTS])
    ae_bitmaps = parse_bitmap_index(ae_data, ae_sec_map[SEC_BITMAPS])
    bmp_unknown = struct.unpack_from('<I', ae_data, ae_sec_map[SEC_BITMAPS]['data_offset'])[0]
    print(f'  {len(ae_levels)} levels')

    print('Loading SV...')
    sv_arc = ArcArchive.from_file(sv_arc_path)
    sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
    sv_sec_map = {s['type']: s for s in parse_sections(sv_data)}
    sv_levels = parse_level_index(sv_data, sv_sec_map[SEC_LEVELS])
    sv_quests = parse_quests(sv_data, sv_sec_map[SEC_QUESTS])
    print(f'  {len(sv_levels)} levels')

    # Build name lookups
    ae_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(ae_levels)}
    sv_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(sv_levels)}

    # Identify levels
    sv_only = []
    sv_shared_drx = []
    for lv in sv_levels:
        key = lv['fname'].replace('\\', '/').lower()
        chunk = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if key not in ae_by_name:
            sv_only.append(lv)
        elif b'drxmap' in chunk:
            sv_shared_drx.append((lv, ae_by_name[key]))

    print(f'\n  SV-only: {len(sv_only)} levels to append')
    print(f'  Shared with drxmap: {len(sv_shared_drx)} levels for section surgery')

    # Perform section surgery on shared levels
    print('\n=== Section Surgery ===')
    surgery_blobs = {}  # ae_idx -> new blob
    sv_full_blob_levels = {}  # ae_idx -> (sv_blob, sv_lv) for v0x0e levels
    for sv_lv, ae_idx in sv_shared_drx:
        ae_lv = ae_levels[ae_idx]
        ae_blob = ae_data[ae_lv['data_offset']:ae_lv['data_offset'] + ae_lv['data_length']]
        sv_blob = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + sv_lv['data_length']]

        result, info = perform_section_surgery(ae_blob, sv_blob, ae_lv['fname'])
        if result:
            surgery_blobs[ae_idx] = result
            print(f'  OK: {ae_lv["fname"]} ({info})')
        elif info == "use_sv_blob":
            sv_full_blob_levels[ae_idx] = (sv_blob, sv_lv)
            print(f'  FULL: {ae_lv["fname"]} (using SV full blob + ints_raw)')
        else:
            print(f'  SKIP: {ae_lv["fname"]} ({info})')

    # Merge quests
    ae_quest_set = set(q.lower() for q in ae_quests)
    new_quests = [q for q in sv_quests if q.lower() not in ae_quest_set]
    merged_quests = ae_quests + new_quests

    # Add custom quests for Uber Dungeon portal wiring
    existing_lower = set(q.lower() if isinstance(q, str) else q.decode('ascii', errors='replace').lower()
                         for q in merged_quests)
    added = 0
    for qname in UBER_DUNGEON_QUEST_NAMES:
        if qname.lower() not in existing_lower:
            merged_quests.append(qname.encode('ascii'))
            existing_lower.add(qname.lower())
            added += 1
    print(f'\n  Quests: {len(ae_quests)} + {len(new_quests)} new + {added} custom = {len(merged_quests)}')

    # Collect blobs to append (SV-only + surgically modified shared levels)
    append_blobs = []
    sv_only_blob_indices = []
    for lv in sv_only:
        sv_only_blob_indices.append(len(append_blobs))
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]

        # Inject objects into SV-only levels if specified
        lv_key = lv['fname'].replace('\\', '/').lower()
        if lv_key in INJECT_SPECS:
            blob = inject_into_sv_only_blob(blob, INJECT_SPECS[lv_key], lv['fname'])

        append_blobs.append(blob)

    surgery_blob_indices = {}
    for ae_idx, blob in surgery_blobs.items():
        surgery_blob_indices[ae_idx] = len(append_blobs)
        append_blobs.append(blob)

    sv_full_blob_indices = {}
    for ae_idx, (sv_blob, sv_lv) in sv_full_blob_levels.items():
        sv_full_blob_indices[ae_idx] = len(append_blobs)
        append_blobs.append(sv_blob)

    total_append = sum(len(b) for b in append_blobs)
    print(f'  Total append data: {total_append/(1024**2):.1f} MB')

    # Build new sections
    print('\nBuilding merged map...')
    merged_levels = [dict(lv) for lv in ae_levels]
    for lv in sv_only:
        merged_levels.append(dict(lv))

    merged_bitmaps = [dict(b) for b in ae_bitmaps]
    for _ in sv_only:
        merged_bitmaps.append({'offset': 0, 'length': 0})

    new_quests_data = build_quests(merged_quests)
    new_levels_data = build_level_index(merged_levels)
    new_bitmaps_data = build_bitmap_index(merged_bitmaps, bmp_unknown)

    groups_data = ae_data[ae_sec_map[SEC_GROUPS]['data_offset']:ae_sec_map[SEC_GROUPS]['data_offset'] + ae_sec_map[SEC_GROUPS]['size']]
    sd_data = ae_data[ae_sec_map[SEC_SD]['data_offset']:ae_sec_map[SEC_SD]['data_offset'] + ae_sec_map[SEC_SD]['size']]

    unknown_sec = [s for s in ae_sections if s['type'] not in
                   (SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_LEVELS, SEC_BITMAPS, SEC_DATA2, SEC_DATA)]
    unknown_sections_data = [(s['type'], ae_data[s['data_offset']:s['data_offset'] + s['size']]) for s in unknown_sec]

    # Calculate offsets
    orig_pre_data_size = ae_sec_map[SEC_DATA2]['header_offset']
    new_pre_data_size = 8
    new_pre_data_size += 8 + len(new_quests_data)
    new_pre_data_size += 8 + len(groups_data)
    new_pre_data_size += 8 + len(sd_data)
    new_pre_data_size += 8 + len(new_levels_data)
    new_pre_data_size += 8 + len(new_bitmaps_data)
    for _, ud in unknown_sections_data:
        new_pre_data_size += 8 + len(ud)

    offset_shift = new_pre_data_size - orig_pre_data_size

    data2_raw = bytearray(ae_data[ae_sec_map[SEC_DATA2]['data_offset']:ae_sec_map[SEC_DATA2]['data_offset'] + ae_sec_map[SEC_DATA2]['size']])
    data_raw = ae_data[ae_sec_map[SEC_DATA]['data_offset']:ae_sec_map[SEC_DATA]['data_offset'] + ae_sec_map[SEC_DATA]['size']]

    struct.pack_into('<I', data2_raw, 4, len(merged_levels))
    data2_raw = bytes(data2_raw)

    # Calculate append start
    append_start = new_pre_data_size + 8 + len(data2_raw) + 8 + len(data_raw)

    # Fix offsets
    for i in range(len(ae_levels)):
        merged_levels[i]['data_offset'] = ae_levels[i]['data_offset'] + offset_shift

    # Surgically modified shared levels: point to appended blob
    for ae_idx, blob_idx in surgery_blob_indices.items():
        blob_offset = append_start + sum(len(append_blobs[j]) for j in range(blob_idx))
        merged_levels[ae_idx]['data_offset'] = blob_offset
        merged_levels[ae_idx]['data_length'] = len(append_blobs[blob_idx])

    # Full SV blob levels (v0x0e): use SV's ints_raw + full blob
    for ae_idx, blob_idx in sv_full_blob_indices.items():
        blob_offset = append_start + sum(len(append_blobs[j]) for j in range(blob_idx))
        sv_lv = sv_full_blob_levels[ae_idx][1]
        merged_levels[ae_idx]['data_offset'] = blob_offset
        merged_levels[ae_idx]['data_length'] = len(append_blobs[blob_idx])
        merged_levels[ae_idx]['ints_raw'] = sv_lv['ints_raw']

    # SV-only levels: point to appended data
    for i, sv_blob_idx in enumerate(sv_only_blob_indices):
        lv_idx = len(ae_levels) + i
        blob_offset = append_start + sum(len(append_blobs[j]) for j in range(sv_blob_idx))
        merged_levels[lv_idx]['data_offset'] = blob_offset

    # Fix bitmap offsets
    for i in range(len(ae_bitmaps)):
        if merged_bitmaps[i]['offset'] > 0:
            merged_bitmaps[i]['offset'] = ae_bitmaps[i]['offset'] + offset_shift

    # Zero bitmap entries for sv_full_blob levels (e.g. Random09A)
    for ae_idx in sv_full_blob_levels:
        merged_bitmaps[ae_idx]['offset'] = 0
        merged_bitmaps[ae_idx]['length'] = 0

    new_levels_data = build_level_index(merged_levels)
    new_bitmaps_data = build_bitmap_index(merged_bitmaps, bmp_unknown)

    # Write
    out = bytearray()
    header2 = new_pre_data_size - 8
    out += struct.pack('<II', MAP_MAGIC, header2)
    out += struct.pack('<II', SEC_QUESTS, len(new_quests_data)) + new_quests_data
    out += struct.pack('<II', SEC_GROUPS, len(groups_data)) + groups_data
    out += struct.pack('<II', SEC_SD, len(sd_data)) + sd_data
    out += struct.pack('<II', SEC_LEVELS, len(new_levels_data)) + new_levels_data
    out += struct.pack('<II', SEC_BITMAPS, len(new_bitmaps_data)) + new_bitmaps_data
    for utype, udata in unknown_sections_data:
        out += struct.pack('<II', utype, len(udata)) + udata
    out += struct.pack('<II', SEC_DATA2, len(data2_raw)) + data2_raw
    extended_data_size = len(data_raw) + total_append
    out += struct.pack('<II', SEC_DATA, extended_data_size) + data_raw
    for blob in append_blobs:
        out += blob

    result = bytes(out)

    # Verify
    print('\n=== Verification ===')
    v_sections = parse_sections(result)
    v_sec_map = {s['type']: s for s in v_sections}
    v_levels = parse_level_index(result, v_sec_map[SEC_LEVELS])

    bad_offsets = sum(1 for lv in v_levels if lv['data_offset'] + lv['data_length'] > len(result))
    bad_magic = sum(1 for lv in v_levels if result[lv['data_offset']:lv['data_offset'] + 3] != b'LVL')
    d2_count = struct.unpack_from('<I', result, v_sec_map[SEC_DATA2]['data_offset'] + 4)[0]

    # Verify surgery levels still have correct LVL version (should be 0x11)
    surgery_vers = {}
    for ae_idx in surgery_blobs:
        lv = v_levels[ae_idx]
        ver = result[lv['data_offset'] + 3]
        surgery_vers[ae_idx] = ver
    for ae_idx in sv_full_blob_levels:
        lv = v_levels[ae_idx]
        ver = result[lv['data_offset'] + 3]
        surgery_vers[ae_idx] = ver

    print(f'  Levels: {len(v_levels)}')
    print(f'  DATA2 count: {d2_count}')
    print(f'  Bad offsets: {bad_offsets}')
    print(f'  Bad magic: {bad_magic}')
    print(f'  drxmap refs: {result.count(b"drxmap")}')
    print(f'  Surgery level versions: {set(f"0x{v:02x}" for v in surgery_vers.values())}')
    print(f'  Size: {len(result)/(1024**2):.1f} MB, under 2GB: {len(result) < 2147483647}')

    # Package into ARC
    print(f'\nPackaging into ARC...')
    arc = ArcArchive.from_file(svaera_arc_path)
    arc.set_file('world/world01.map', result)
    arc.write(output_arc)
    print(f'  ARC: {output_arc.stat().st_size/(1024**2):.1f} MB')

    del ae_data, sv_data, result
    print('Done!')


if __name__ == '__main__':
    main()
