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
# MECHANISM (fully verified self-consistent): `records\quests\portal_olympianarena1.dbr` =
# Class GridEntranceDynamic (a quest-opened dynamic grid entrance). The ported `bossarena.qst`
# fires `Action_OpenDynGridEntrance(dynGridEntranceName=records/quests/portal_olympianarena1.dbr)`
# on Condition_OnLevelLoad - it opens the portal BY RECORD NAME, so NO Quests.arc change is
# needed; the portal record instance just has to EXIST in the loaded level. Entering it
# teleports to crypt_floor1 (Uber Dungeon) via its 0x14 binding; crypt_floor1's
# portal_olympianarena2 (GridExitOneWay) is the landing (on-mesh, Wave 1).
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
PORTAL_OLYMPIANARENA1_0x14 = bytes.fromhex(
    '58941143e04eb3c0d62dbd952143f05d'   # mouth_uid
    '6e513e901549b1d558db968c61bda66a'   # exit_uid  (pairs crypt_floor1 portal_olympianarena2)
    'dbc245c358434e0bb54760b234293cc5')  # dest_guid (== crypt_floor1 merged GUID)
assert len(PORTAL_OLYMPIANARENA1_0x14) == 48

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

# Injection specs: level name key -> list of specs (see INJECTION-SPEC FORMAT above).
# DelphiLowlands04: merchant tent at (12.88, 9.98, 2.52), quest NPC at (14.03, 10.16, 6.15)
# crypt_floor1: minotaur statue at (139.73, 11.84, 212.30), existing arena portal at (139.94, 10.01, 231.94)
# HiddenValley01: cave entrance at (14.0, 18.0, 26.0), POI at (15.84, 18.0, 26.58)
# BC_initialpathway: SV blood cave entrance level
INJECT_SPECS = {
    # Delphi NPC injection REMOVED - corrupts v0x11 blob, crashes game on world streaming
    'levels/world/uberdungeon/crypt_floor1.lvl': [
        (RETURN_NPC_DBR, 140.0, 10.0, 215.0),
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
    # GROUPS binding is by UniqueId, POSITION-INDEPENDENT, so moving it keeps the respawn
    # binding intact (group member count unchanged). Y uses the walkable-floor height at the
    # new spot (17.6). The caravan keeps its native rot + 12-byte 0x14 (2,0,1).
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
    ],
    # Static Widow Letter (BUG 2): finalletter placed at the location_letterdrop spot so it
    # is physically present for ALL characters (the quest spawn is neutralized in
    # build_quest_files.py to prevent a duplicate). SV-only v0x0e -> inject_into_0x05 (56 B),
    # flags=0, no 0x14. Local = location_letterdrop's exact SV-local coord (on-mesh 0.10u).
    'levels/world/xbloodcave/drxfirstxistion_connection.lvl': [
        (FINALLETTER_DBR, 32.459, 10.005, 17.593),
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
        (MERCHANT_HADES_WAGON_DBR, 36.22654724121094, 1.6249699592590332, 26.539936065673828,
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
        (T1_LILDUDE_01_DBR, 51.30, 1.80, 33.30),      # d_occ 18.0 d_carv 20.6
        (T1_LILDUDE_01_DBR, 49.30, 1.80, 36.10),      # d_occ 18.0 d_carv 22.3
        (T1_LILDUDE_02_DBR, 49.50, 1.80, 35.90),      # d_occ 18.0 d_carv 22.2
        (PIT_FX01_DBR, 50.70, 1.80, 34.30),
    ],
    # A1: maze03 -> Uber Dungeon (+ Boss Arena) entrance. Restore SV's portal_olympianarena1
    # (GridEntranceDynamic) at the AE-mesh-on secret-door spot with SV's exact 48-byte 0x14
    # binding (mouth+exit+dest -> crypt_floor1). AE Maze03 is a SHARED v0x0f level -> routed
    # through the (widened) step-6 v0f inject path; the x14_payload appends the binding at the
    # injected instance index (maze03 has a 0x14 section of size 0). flags=0, IDENTITY rot.
    # See the PORTAL_OLYMPIANARENA1 block above for the full mechanism + coord derivation.
    'levels/world/greece/knossos/underground/maze03.lvl': [
        (PORTAL_OLYMPIANARENA1_DBR, 290.70, 1.20, 152.50,
         {'x14_payload': PORTAL_OLYMPIANARENA1_0x14}),
    ],
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
    # Hemorrheus (Blood Toxeus) superboss, guarding the secret hallway past the mega chest
    # (docs/BLOOD_TOXEUS_DESIGN.md sec 5). Placed as a Proxy 0x05 instance, flags=0, NO 0x14
    # entry - byte-shape identical to how SV places q_leinth_lone in bossfight.lvl (measured
    # from the SV 0.98i upstream Levels.arc, v0x0e; the exemplar record is flags=0 / 56 bytes
    # / no UniqueId / no 0x14 entry). new_secretdoor_transitionhallway is an SV-only level ->
    # the merge routes this through inject_into_sv_only_blob -> inject_into_0x05 (v0x0e).
    #
    # COORD is SV-LOCAL for this level (the xBloodCave GRID_SHIFT (7840,0,2030) is applied by
    # the merge to the level's grid corner, NOT here). Derivation, verified against the
    # CURRENT build20 donor (obstacle-carved) with tools/debug/navlib.py:
    #   world centroid (4999.9, 4.0, 3467.1) is 0.000u on-mesh, IN the largest walkable
    #     component (159,742 cells; cell (519,465), area=1);
    #   shifted grid corner (from shifted_ints_raw) = (4932, 1, 3425);
    #   SV-local = world - shifted_corner = (67.9, 3.0, 42.1).
    # Round-trip: local + shifted_corner == world centroid -> same on-mesh cell (proven
    # against the same donor). Spawn is 47.1u from the exit portal (xprtl_bc2et_02 @ world
    # x=5047) and 38.9u from respawn_hadescave01 -> no instant-aggro spawn-camp on arrival.
    # Rotation = q_leinth_lone's exact float32 matrix (orientation-only; the real spawn is the
    # um_bloodtoxeus_99 monster via the pool). Y local=3.0 matches every other proxy here.
    'levels/world/xbloodcave/new_secretdoor_transitionhallway.lvl': [
        (Q_BLOODTOXEUS_LONE_DBR, 67.9, 3.0, 42.1, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
    ],
}

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
    """Inject objects into an SV-only level blob by modifying its 0x05 section."""
    secs, magic = parse_blob_sections(blob)
    if not secs:
        return blob

    modified = False
    new_secs = []
    for s in secs:
        if s['type'] == 0x05 and injections:
            new_data = inject_into_0x05(s['data'], injections)
            new_secs.append({'type': 0x05, 'data': new_data})
            modified = True
            print(f'    Injected {len(injections)} object(s) into SV-only {level_name}')
        else:
            new_secs.append(s)

    if modified:
        return rebuild_blob(magic, new_secs)
    return blob


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
