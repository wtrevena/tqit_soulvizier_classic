"""
Titan Quest .qst (Quest) binary file format — parser, builder, and specification.

Reverse-engineered from 89 quest files in Soulvizier 0.98i.
Verified via round-trip: parse → serialize produces byte-identical output for all 89 files.

FORMAT SPECIFICATION
====================

Encoding: All integers are unsigned 32-bit little-endian (uint32).

Primitive types:
  - len_string: uint32 length, followed by `length` bytes of UTF-8 text (no null terminator)
  - int_field:  uint32 value (for booleans: 0/1; for floats like delayTime: IEEE 754 bits)
  - str_field:  uint32 string_length, followed by `string_length` bytes of UTF-8

Block delimiters:
  - begin_block: len_string("begin_block") + uint32(0xB01DFACE)
  - end_block:   len_string("end_block")   + uint32(0xDEADC0DE)

Field encoding:
  - len_string(key_name) + value
  - For int fields: value = uint32
  - For string fields: value = uint32(string_length) + string_bytes
  - The game determines type by field name (see INT_FIELDS below)
  - When value is 0 for a string field, it means empty string (no bytes follow the 0)

OVERALL STRUCTURE
=================

  BEGIN_BLOCK — Quest Header
    title: str
    rewardItemTag: str          (or localRewardItemTag for scripted scenes)
    rewardGold: int             (or localRewardGold)
    rewardXP: int               (or localRewardXP)
    rewardSkill: int
    rewardAttr: int
    this->rewardItemTag[1]: str
    this->rewardGold[1]: int
    this->rewardXP[1]: int
    this->rewardItemTag[2]: str
    this->rewardGold[2]: int
    this->rewardXP[2]: int
  END_BLOCK

  BEGIN_BLOCK — Quest Steps Container
    max: int  (number of quest steps)

    For each step (exactly `max` times):

      BEGIN_BLOCK — Step Definition
        name: str
        nextTaskDescription: str
      END_BLOCK

      BEGIN_BLOCK — Trigger Container
        max: int  (number of triggers)
        For each trigger (`max` times):
          BEGIN_BLOCK trigger_header END_BLOCK
          BEGIN_BLOCK conditions END_BLOCK
          BEGIN_BLOCK actions END_BLOCK
      END_BLOCK

      BEGIN_BLOCK — Sentinel Trigger (always present, no `max` field)
        BEGIN_BLOCK empty_header END_BLOCK
        BEGIN_BLOCK conditionCount=0 END_BLOCK
        BEGIN_BLOCK actionCount=0 END_BLOCK
      END_BLOCK

  END_BLOCK — Quest Steps Container

  Trigger Header fields: displayTag, displayBitmap, comments, isActive, bRatchet

  Conditions block:
    conditionCount: int
    For each condition:
      conditionClassName: str
      BEGIN_BLOCK — condition-specific fields END_BLOCK

  Actions block:
    actionCount: int
    For each action:
      actionClassName: str
      BEGIN_BLOCK — action-specific fields END_BLOCK

FLOAT ENCODING
==============
Fields like delayTime and fadeTime store IEEE 754 single-precision floats
as raw uint32 bit patterns. Use struct.pack('<f', value) to encode.
  Examples: 0.0→0x00000000, 1.0→0x3F800000, 2.0→0x40000000,
            3.0→0x40400000, 4.0→0x40800000

COORDINATE ENCODING (Action_BoatDialog)
=======================================
x, y, z are signed 32-bit integers stored as uint32 (two's complement).
  Examples: -2317 → 0xFFFFF6F3, -90 → 0xFFFFFFA6
"""

import struct
from dataclasses import dataclass, field
from typing import Union


# ── Magic constants ──────────────────────────────────────────────────────────

BEGIN_BLOCK_MAGIC = 0xB01DFACE
END_BLOCK_MAGIC   = 0xDEADC0DE

# ── Field type classification ───────────────────────────────────────────────
# Fields whose 4-byte value is an integer (not a string length).
# Everything else is a string (4-byte length + string data).

INT_FIELDS = frozenset({
    # Structure
    'max', 'conditionCount', 'actionCount',
    # Booleans
    'isActive', 'bRatchet', 'isNot', 'isResettable',
    'isQuestCritical', 'isQuestCritical2',
    'canReFire', 'onOff', 'fade',
    'bAlwaysClose', 'doComplete', 'doSound',
    'allowInterruptions', 'invincible', 'isPerPartyMember',
    'isQuestSkill', 'looping', 'useActionTarget',
    'enableTimeProgression',
    # Numeric
    'rewardGold', 'rewardXP', 'rewardSkill', 'rewardAttr',
    'localRewardGold', 'localRewardXP',
    'delayTime', 'fadeTime',  # IEEE 754 float stored as uint32
    'x', 'y', 'z',  # signed int32 as uint32 (two's complement)
    'region', 'mode', 'type', 'value', 'index',
    'amplitude', 'animation', 'duration', 'fight',
    'timeInSecs', 'timeOfDay',
    'num', 'attributeAmount', 'experiencePts', 'moneyAmount', 'skillAmount',
})

# ── Condition classes and their specific fields ─────────────────────────────
# All conditions share: comments, isNot, isResettable, isQuestCritical
# Most also have isQuestCritical2 (exception: Condition_CounterState)

CONDITION_FIELDS = {
    'Condition_AnimationCompleted': ['characterRecord', 'idTag'],
    'Condition_CharacterHasItem': ['itemName'],
    'Condition_ConversationStart': ['personRecord'],
    'Condition_CounterState': ['name', 'mode', 'value'],
    'Condition_EnterVolume': ['volumeRecord', 'entityRecord'],
    'Condition_ExitVolume': ['volumeRecord'],
    'Condition_GotToken': ['tokenName'],
    'Condition_KillAllCreaturesFromProxy': ['proxyRecord'],
    'Condition_KillCreature': ['creatureRecord'],
    'Condition_MoveCompleted': ['characterRecord', 'idTag'],
    'Condition_OnLevelLoad': [],
    'Condition_OnQuestComplete': ['questFile'],
    'Condition_OwnsTriggerToken': ['tokenName'],
    'Condition_PickupItem': ['itemRecord'],
    'Condition_UseFixedItem': ['itemRecord'],
}

# ── Action classes and their specific fields ────────────────────────────────
# All actions share: comments, delayTime

ACTION_FIELDS = {
    'Action_BestowTriggerToken': ['tokenName'],
    'Action_BoatDialog': ['npc', 'onOff', 'x', 'y', 'z', 'tag'],
    'Action_ClearMapMarker': ['doSound'],
    'Action_ClearNPCDialog': ['npc'],
    'Action_CloseDoor': ['door', 'canReFire', 'bAlwaysClose'],
    'Action_CompleteQuestNow': ['questFile'],
    'Action_CounterUpdate': ['name', 'mode', 'value'],
    'Action_DebugText': ['debugText'],
    'Action_DisableProxy': ['proxy'],
    'Action_DispenseItemFromNpc': ['npc', 'item[0]', 'item[1]', 'item[2]',
                                   'canReFire', 'isPerPartyMember'],
    'Action_FadeOutEventMusic': ['timeInSecs'],
    'Action_FireSkill': ['skill', 'source', 'target', 'location',
                         'allowInterruptions', 'isQuestSkill', 'useActionTarget'],
    'Action_GiveAttributePoints': ['attributeAmount[0]', 'attributeAmount[1]',
                                   'attributeAmount[2]', 'region', 'locationTag', 'titleTag'],
    'Action_GiveExp': ['experiencePts[0]', 'experiencePts[1]', 'experiencePts[2]',
                       'region', 'locationTag', 'titleTag'],
    'Action_GiveItem': ['item[0]', 'item[1]', 'item[2]',
                        'num[0]', 'num[1]', 'num[2]',
                        'region', 'locationTag', 'titleTag'],
    'Action_GiveMoney': ['moneyAmount[0]', 'moneyAmount[1]', 'moneyAmount[2]',
                         'region', 'locationTag', 'titleTag'],
    'Action_GiveSkillPoints': ['skill', 'skillAmount[0]', 'skillAmount[1]',
                               'skillAmount[2]', 'region', 'locationTag', 'titleTag'],
    'Action_HideNpc': ['npc', 'canReFire', 'fadeTime', 'fade'],
    'Action_IlluminateNpc': ['npc', 'type'],
    'Action_KillCreature': ['creatureRecord', 'canReFire'],
    'Action_LoadEventMusic': ['playlist'],
    'Action_LockFixedItem': ['fixedItem'],
    'Action_NpcPlayAnimation': ['npc', 'animation', 'allowInterruptions',
                                'looping', 'idTag'],
    'Action_OpenDoor': ['door', 'canReFire'],
    'Action_OpenDynGridEntrance': ['dynGridEntranceName', 'canReFire'],
    'Action_OrientNPC': ['npc', 'location', 'canReFire'],
    'Action_Play3DSound': ['entity', 'soundEffect'],
    'Action_PlaySoundEffect': ['soundEffect'],
    'Action_RemoveItemFromInventory': ['itemName'],
    'Action_RemoveTriggerToken': ['tokenName'],
    'Action_ResetTrigger': ['name'],
    'Action_RunDelayedProxy': ['proxy'],
    'Action_ScreenShake': ['amplitude', 'duration'],
    'Action_SendTutorialEvent': ['index'],
    'Action_SetCharacterInvincible': ['npc', 'invincible', 'canReFire'],
    'Action_SetTimeOfDay': ['timeOfDay', 'enableTimeProgression'],
    'Action_ShowNpc': ['npc', 'canReFire', 'fadeTime', 'fade'],
    'Action_SpawnEntityAtLocation': ['entity', 'location'],
    'Action_TaskCreatureToLocation': ['creature', 'location', 'fight',
                                      'idTag', 'canReFire'],
    'Action_UnlockFixedItem': ['fixedItem', 'canReFire'],
    'Action_UpdateDialogTab': ['dialogPak'],
    'Action_UpdateJournalEntry': ['region', 'locationTag', 'titleTag',
                                  'fullTextTag', 'doComplete', 'doSound'],
    'Action_UpdateMapMarker': ['bulletPointTag', 'descriptionTag',
                               'doComplete', 'doSound'],
    'Action_UpdateNPCDialog': ['npc', 'dialogFile'],
}


# ── Low-level binary helpers ────────────────────────────────────────────────

def _is_int_field(key: str) -> bool:
    """Determine if a field stores its value as a raw uint32 (vs. string)."""
    base = key
    if base.startswith('this->'):
        base = base[6:]
    if '[' in base:
        base = base[:base.index('[')]
    return base in INT_FIELDS


def _write_begin(buf: bytearray):
    _write_len_str(buf, 'begin_block')
    buf.extend(struct.pack('<I', BEGIN_BLOCK_MAGIC))


def _write_end(buf: bytearray):
    _write_len_str(buf, 'end_block')
    buf.extend(struct.pack('<I', END_BLOCK_MAGIC))


def _write_len_str(buf: bytearray, s: str):
    encoded = s.encode('utf-8')
    buf.extend(struct.pack('<I', len(encoded)))
    buf.extend(encoded)


def _write_int(buf: bytearray, key: str, val: int):
    _write_len_str(buf, key)
    buf.extend(struct.pack('<I', val & 0xFFFFFFFF))


def _write_str(buf: bytearray, key: str, val: str):
    _write_len_str(buf, key)
    encoded = val.encode('utf-8')
    buf.extend(struct.pack('<I', len(encoded)))
    buf.extend(encoded)


def _write_field(buf: bytearray, key: str, val):
    """Write a field, auto-detecting int vs string from the key name."""
    if _is_int_field(key):
        _write_int(buf, key, int(val))
    else:
        _write_str(buf, key, str(val) if val else '')


def _write_float_field(buf: bytearray, key: str, val: float):
    """Write a float value stored as uint32 IEEE 754 bits."""
    _write_len_str(buf, key)
    buf.extend(struct.pack('<f', val))


def _write_signed_int(buf: bytearray, key: str, val: int):
    """Write a signed int32 as uint32."""
    _write_len_str(buf, key)
    buf.extend(struct.pack('<i', val))


# ── Parser ──────────────────────────────────────────────────────────────────

def _is_valid_token_at(data: bytes, p: int) -> bool:
    """Check if position p could be the start of a valid begin_block/end_block/field."""
    if p >= len(data):
        return p == len(data)
    if p + 4 > len(data):
        return False
    slen = struct.unpack_from('<I', data, p)[0]
    if slen == 0 or slen > 500:
        return False
    if p + 4 + slen > len(data):
        return False
    try:
        s = data[p+4:p+4+slen].decode('ascii')
        return all(c.isalnum() or c in "_->[]() .'!-" for c in s)
    except (UnicodeDecodeError, ValueError):
        return False


def parse(data: bytes) -> list:
    """Parse .qst binary data into a nested tree.

    Returns a list of top-level blocks. Each block is a list of items:
      ('block', sub_items)           — nested begin/end block
      ('field', key, ('int', val))   — integer field
      ('field', key, ('str', val))   — string field
    """
    pos = [0]

    def read_u32():
        val = struct.unpack_from('<I', data, pos[0])[0]
        pos[0] += 4
        return val

    def read_len_str():
        slen = read_u32()
        s = data[pos[0]:pos[0]+slen].decode('utf-8', errors='replace')
        pos[0] += slen
        return s

    def read_field_value(key):
        val_raw = read_u32()

        if _is_int_field(key):
            return ('int', val_raw)

        if val_raw == 0:
            return ('int_or_empty', 0)

        str_end = pos[0] + val_raw
        if val_raw <= 5000 and str_end <= len(data):
            try:
                str_val = data[pos[0]:str_end].decode('utf-8')
                is_printable = all(c.isprintable() or c in '\r\n\t' for c in str_val)
            except (UnicodeDecodeError, ValueError):
                is_printable = False
            if is_printable and _is_valid_token_at(data, str_end):
                pos[0] = str_end
                return ('str', str_val)

        if _is_valid_token_at(data, pos[0]):
            return ('int', val_raw)

        raise ValueError(
            f"Cannot determine type for field '{key}' = {val_raw} at 0x{pos[0]-4:04x}")

    def parse_block():
        fields = []
        while pos[0] < len(data):
            token = read_len_str()
            if token == 'begin_block':
                read_u32()  # magic
                fields.append(('block', parse_block()))
            elif token == 'end_block':
                read_u32()  # magic
                return fields
            else:
                fields.append(('field', token, read_field_value(token)))
        return fields

    blocks = []
    while pos[0] < len(data):
        token = read_len_str()
        if token == 'begin_block':
            read_u32()
            blocks.append(parse_block())
    return blocks


def serialize(blocks: list) -> bytes:
    """Serialize a parsed tree back to .qst binary data."""
    buf = bytearray()

    def write_items(items):
        for item in items:
            if item[0] == 'block':
                _write_begin(buf)
                write_items(item[1])
                _write_end(buf)
            elif item[0] == 'field':
                key = item[1]
                val_type, val = item[2]
                _write_len_str(buf, key)
                if val_type == 'str':
                    encoded = val.encode('utf-8')
                    buf.extend(struct.pack('<I', len(encoded)))
                    buf.extend(encoded)
                else:
                    buf.extend(struct.pack('<I', val))

    for block in blocks:
        _write_begin(buf)
        write_items(block)
        _write_end(buf)

    return bytes(buf)


# ── High-level builder ──────────────────────────────────────────────────────

@dataclass
class Condition:
    """A quest trigger condition."""
    class_name: str
    comments: str = ''
    is_not: int = 0
    is_resettable: int = 0
    is_quest_critical: int = 0
    is_quest_critical2: int = 0
    fields: dict = field(default_factory=dict)


@dataclass
class Action:
    """A quest trigger action."""
    class_name: str
    comments: str = ''
    delay_time: float = 0.0
    fields: dict = field(default_factory=dict)


@dataclass
class Trigger:
    """A quest step trigger with conditions and actions."""
    display_tag: str = ''
    display_bitmap: str = ''
    comments: str = ''
    is_active: int = 0
    b_ratchet: int = 0
    conditions: list = field(default_factory=list)
    actions: list = field(default_factory=list)


@dataclass
class QuestStep:
    """A quest step containing triggers."""
    name: str = 'New Quest Step'
    next_task_description: str = ''
    triggers: list = field(default_factory=list)


@dataclass
class Quest:
    """Top-level quest definition."""
    title: str = ''
    reward_item_tag: str = ''
    reward_gold: int = 0
    reward_xp: int = 0
    reward_skill: int = 0
    reward_attr: int = 0
    reward_item_tag_1: str = ''
    reward_gold_1: int = 0
    reward_xp_1: int = 0
    reward_item_tag_2: str = ''
    reward_gold_2: int = 0
    reward_xp_2: int = 0
    use_local_rewards: bool = False
    steps: list = field(default_factory=list)


def float_to_uint32(f: float) -> int:
    """Convert a float to its IEEE 754 uint32 representation."""
    return struct.unpack('<I', struct.pack('<f', f))[0]


def signed_to_uint32(i: int) -> int:
    """Convert a signed int32 to uint32 (two's complement)."""
    return struct.unpack('<I', struct.pack('<i', i))[0]


def build_quest(quest: Quest) -> bytes:
    """Build a complete .qst binary file from a Quest dataclass.

    Structure per step:
      1. Step definition block (name, nextTaskDescription)
      2. Trigger container block (max=N, N trigger sets)
      3. Sentinel trigger block (1 empty trigger, no max field)
    """
    buf = bytearray()

    # ── Quest Header block ──
    _write_begin(buf)
    _write_str(buf, 'title', quest.title)

    if quest.use_local_rewards:
        _write_str(buf, 'localRewardItemTag', quest.reward_item_tag)
        _write_int(buf, 'localRewardGold', quest.reward_gold)
        _write_int(buf, 'localRewardXP', quest.reward_xp)
    else:
        _write_str(buf, 'rewardItemTag', quest.reward_item_tag)
        _write_int(buf, 'rewardGold', quest.reward_gold)
        _write_int(buf, 'rewardXP', quest.reward_xp)

    _write_int(buf, 'rewardSkill', quest.reward_skill)
    _write_int(buf, 'rewardAttr', quest.reward_attr)
    _write_str(buf, 'this->rewardItemTag[1]', quest.reward_item_tag_1)
    _write_int(buf, 'this->rewardGold[1]', quest.reward_gold_1)
    _write_int(buf, 'this->rewardXP[1]', quest.reward_xp_1)
    _write_str(buf, 'this->rewardItemTag[2]', quest.reward_item_tag_2)
    _write_int(buf, 'this->rewardGold[2]', quest.reward_gold_2)
    _write_int(buf, 'this->rewardXP[2]', quest.reward_xp_2)
    _write_end(buf)

    # ── Quest Steps Container ──
    _write_begin(buf)
    _write_int(buf, 'max', len(quest.steps))

    for step in quest.steps:
        _build_step(buf, step)

    _write_end(buf)

    return bytes(buf)


def _build_step(buf: bytearray, step: QuestStep):
    """Build a quest step: definition + trigger container + sentinel."""
    # Step definition
    _write_begin(buf)
    _write_str(buf, 'name', step.name)
    _write_str(buf, 'nextTaskDescription', step.next_task_description)
    _write_end(buf)

    # Trigger container (with max and active triggers)
    _write_begin(buf)
    _write_int(buf, 'max', len(step.triggers))
    for trigger in step.triggers:
        _build_trigger_set(buf, trigger)
    _write_end(buf)

    # Sentinel trigger block (no max, single empty trigger)
    _write_begin(buf)
    _build_trigger_set(buf, Trigger())
    _write_end(buf)


def _build_trigger_set(buf: bytearray, trigger: Trigger):
    """Build a trigger set: header block + conditions block + actions block."""
    # Trigger header
    _write_begin(buf)
    _write_str(buf, 'displayTag', trigger.display_tag)
    _write_str(buf, 'displayBitmap', trigger.display_bitmap)
    _write_str(buf, 'comments', trigger.comments)
    _write_int(buf, 'isActive', trigger.is_active)
    _write_int(buf, 'bRatchet', trigger.b_ratchet)
    _write_end(buf)

    # Conditions block
    _write_begin(buf)
    _write_int(buf, 'conditionCount', len(trigger.conditions))
    for cond in trigger.conditions:
        _build_condition(buf, cond)
    _write_end(buf)

    # Actions block
    _write_begin(buf)
    _write_int(buf, 'actionCount', len(trigger.actions))
    for action in trigger.actions:
        _build_action(buf, action)
    _write_end(buf)


def _build_condition(buf: bytearray, cond: Condition):
    """Build a single condition entry."""
    _write_str(buf, 'conditionClassName', cond.class_name)
    _write_begin(buf)
    _write_str(buf, 'comments', cond.comments)
    _write_int(buf, 'isNot', cond.is_not)
    _write_int(buf, 'isResettable', cond.is_resettable)
    _write_int(buf, 'isQuestCritical', cond.is_quest_critical)
    if cond.class_name != 'Condition_CounterState':
        _write_int(buf, 'isQuestCritical2', cond.is_quest_critical2)
    for key, val in cond.fields.items():
        _write_field(buf, key, val)
    _write_end(buf)


def _build_action(buf: bytearray, action: Action):
    """Build a single action entry."""
    _write_str(buf, 'actionClassName', action.class_name)
    _write_begin(buf)
    _write_str(buf, 'comments', action.comments)
    _write_int(buf, 'delayTime', float_to_uint32(action.delay_time))
    for key, val in action.fields.items():
        if key in ('x', 'y', 'z'):
            _write_signed_int(buf, key, int(val))
        elif _is_int_field(key):
            _write_int(buf, key, int(val))
        else:
            _write_str(buf, key, str(val) if val else '')
    _write_end(buf)


# ── Convenience builders for common quest patterns ──────────────────────────

def make_on_level_load_condition(*, is_resettable=0, is_quest_critical=0) -> Condition:
    return Condition('Condition_OnLevelLoad',
                     is_resettable=is_resettable,
                     is_quest_critical=is_quest_critical)


def make_kill_creature_condition(creature_dbr: str, *,
                                 is_resettable=0, is_quest_critical=0) -> Condition:
    return Condition('Condition_KillCreature',
                     is_resettable=is_resettable,
                     is_quest_critical=is_quest_critical,
                     fields={'creatureRecord': creature_dbr})


def make_kill_all_from_proxy_condition(proxy_dbr: str, *,
                                       is_resettable=0, is_quest_critical=0) -> Condition:
    return Condition('Condition_KillAllCreaturesFromProxy',
                     is_resettable=is_resettable,
                     is_quest_critical=is_quest_critical,
                     fields={'proxyRecord': proxy_dbr})


def make_enter_volume_condition(volume_dbr: str, entity_dbr: str = '', *,
                                is_resettable=0, is_quest_critical=0) -> Condition:
    return Condition('Condition_EnterVolume',
                     is_resettable=is_resettable,
                     is_quest_critical=is_quest_critical,
                     fields={'volumeRecord': volume_dbr,
                             'entityRecord': entity_dbr})


def make_character_has_item_condition(item_dbr: str, *,
                                      is_resettable=0, is_quest_critical=0) -> Condition:
    return Condition('Condition_CharacterHasItem',
                     is_resettable=is_resettable,
                     is_quest_critical=is_quest_critical,
                     fields={'itemName': item_dbr})


def make_owns_trigger_token_condition(token: str, *, is_not=0,
                                       is_resettable=0, is_quest_critical=0) -> Condition:
    return Condition('Condition_OwnsTriggerToken',
                     is_not=is_not,
                     is_resettable=is_resettable,
                     is_quest_critical=is_quest_critical,
                     fields={'tokenName': token})


def make_show_npc_action(npc_dbr: str, *, delay=0.0, can_refire=1) -> Action:
    return Action('Action_ShowNpc', delay_time=delay,
                  fields={'npc': npc_dbr, 'canReFire': can_refire,
                          'fadeTime': 0, 'fade': 0})


def make_unlock_fixed_item_action(item_dbr: str, *, delay=0.0, can_refire=0) -> Action:
    return Action('Action_UnlockFixedItem', delay_time=delay,
                  fields={'fixedItem': item_dbr, 'canReFire': can_refire})


def make_open_dyn_grid_entrance_action(dbr: str, *, delay=0.0, can_refire=0) -> Action:
    return Action('Action_OpenDynGridEntrance', delay_time=delay,
                  fields={'dynGridEntranceName': dbr, 'canReFire': can_refire})


def make_update_npc_dialog_action(npc_dbr: str, dialog_dbr: str, *,
                                   delay=0.0) -> Action:
    return Action('Action_UpdateNPCDialog', delay_time=delay,
                  fields={'npc': npc_dbr, 'dialogFile': dialog_dbr})


def make_boat_dialog_action(npc_dbr: str, tag: str,
                             x: int, y: int, z: int, *,
                             delay=0.0, on_off=1) -> Action:
    return Action('Action_BoatDialog', delay_time=delay,
                  fields={'npc': npc_dbr, 'onOff': on_off,
                          'x': x, 'y': y, 'z': z, 'tag': tag})


def make_spawn_entity_action(entity_dbr: str, location_dbr: str, *,
                              delay=0.0) -> Action:
    return Action('Action_SpawnEntityAtLocation', delay_time=delay,
                  fields={'entity': entity_dbr, 'location': location_dbr})


def make_open_door_action(door_dbr: str, *, delay=0.0, can_refire=0) -> Action:
    return Action('Action_OpenDoor', delay_time=delay,
                  fields={'door': door_dbr, 'canReFire': can_refire})


def make_bestow_token_action(token: str, *, delay=0.0) -> Action:
    return Action('Action_BestowTriggerToken', delay_time=delay,
                  fields={'tokenName': token})


# ── Self-test ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from arc_patcher import ArcArchive

    arc_path = Path(__file__).parent.parent / 'upstream' / 'soulvizier_098i' / 'Resources' / 'XPack' / 'Quests.arc'
    arc = ArcArchive.from_file(arc_path)

    # Round-trip all 89 files
    ok = fail = 0
    for entry in arc.entries:
        if entry.entry_type == 3 and entry.name.lower().endswith('.qst'):
            orig = arc.decompress(entry)
            tree = parse(orig)
            rebuilt = serialize(tree)
            if rebuilt == orig:
                ok += 1
            else:
                fail += 1
                print(f'FAIL: {entry.name}')

    print(f'Round-trip: {ok} OK, {fail} FAIL out of {ok + fail}')

    # Build typhonportal.qst from scratch and compare
    print('\nBuild test: creating typhonportal-like quest...')
    q = Quest(title='Typhon Portal')
    q.steps.append(QuestStep(
        triggers=[Trigger(
            display_tag='New Trigger',
            conditions=[
                make_kill_all_from_proxy_condition(
                    r'Records\Proxies Boss\Boss\BossProxy_20_Typhon_Titan.dbr'),
            ],
            actions=[
                make_unlock_fixed_item_action(
                    'records/xpack/quests/objects/xq00_olympus_portaltorhodes.dbr',
                    can_refire=1),
                make_open_dyn_grid_entrance_action(
                    'records/xpack/quests/objects/xq00_olympus_portaltorhodes.dbr',
                    can_refire=1),
            ],
        )]
    ))
    built = build_quest(q)

    orig = arc.get_file('typhonportal.qst')
    if built == orig:
        print(f'  PERFECT MATCH with original typhonportal.qst ({len(built)} bytes)')
    else:
        print(f'  Size: built={len(built)} orig={len(orig)}')
        for i in range(min(len(built), len(orig))):
            if built[i] != orig[i]:
                print(f'  First diff at 0x{i:04x}: built=0x{built[i]:02x} orig=0x{orig[i]:02x}')
                # Show surrounding context
                ctx_start = max(0, i - 16)
                ctx_end = min(len(orig), i + 32)
                print(f'  Built context: ...{built[ctx_start:ctx_end].hex(" ")}')
                print(f'  Orig  context: ...{orig[ctx_start:ctx_end].hex(" ")}')
                break
        else:
            print(f'  Length mismatch only: built={len(built)} orig={len(orig)}')

    # Build bossarena.qst from scratch and compare
    print('\nBuild test: creating bossarena-like quest...')
    q2 = Quest(title='BossArena')
    q2.steps.append(QuestStep(
        triggers=[Trigger(
            display_tag='New Trigger',
            conditions=[make_on_level_load_condition()],
            actions=[
                make_show_npc_action('records/quests/portal_olympianarena1.dbr'),
                make_open_dyn_grid_entrance_action(
                    'records/quests/portal_olympianarena1.dbr', can_refire=1),
                make_unlock_fixed_item_action(
                    'records/quests/portal_olympianarena1.dbr', can_refire=1),
            ],
        )]
    ))
    q2.steps.append(QuestStep(
        triggers=[Trigger(
            display_tag='New Trigger',
            conditions=[
                Condition('Condition_EnterVolume',
                          fields={'volumeRecord': 'records/quests/portal_olympianarena.dbr',
                                  'entityRecord': ''}),
            ],
            actions=[
                Action('Action_SpawnEntityAtLocation', delay_time=2.0,
                       fields={'entity': 'records/proxies custom/bossarena/boss_satyrshaman.dbr',
                               'location': 'records/quests/location_bossarenacenter.dbr'}),
            ],
        )]
    ))
    built2 = build_quest(q2)
    orig2 = arc.get_file('bossarena.qst')
    if built2 == orig2:
        print(f'  PERFECT MATCH with original bossarena.qst ({len(built2)} bytes)')
    else:
        print(f'  Size: built={len(built2)} orig={len(orig2)}')
        for i in range(min(len(built2), len(orig2))):
            if built2[i] != orig2[i]:
                print(f'  First diff at 0x{i:04x}: built=0x{built2[i]:02x} orig=0x{orig2[i]:02x}')
                break
