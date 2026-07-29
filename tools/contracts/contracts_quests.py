#!/usr/bin/env python3
"""
DOMAIN E: QUEST CONTRACTS - Soulvizier Classic entity-contract-suite module.

WHY THIS EXISTS
===============
The mod keeps shipping things that LOOK complete but are dead in-game because a
required field or companion reference is missing. In the QUEST domain the failure
modes are: a quest condition/action naming a record that resolves NOWHERE at
runtime (dead trigger), a KillAllCreaturesFromProxy watching a proxy that was
never placed (quest stalls forever), an UnlockFixedItem pointed at a door that is
either absent from the map or was never locked (unlock is a no-op), a GiveItem
handing out an empty loot table (reward gives nothing), a notification/journal tag
that renders as a raw `tagXxx` string or a debug PLACEHOLDER (the silent-supra
bug), a quest whose OnLevelLoad step never fires because its registration sits
past the engine's ~256-entry load window (the widow-letter root cause), or the
widow-letter spawn-neutralization regressing into a double-letter.

Every contract's requirement is DERIVED FROM NATIVE PRECEDENT (base-game
database.arz / Text_EN.arc and the shipped artifacts), quantified in the CONTRACTS
table below, then asserted over the shipped quest artifacts.

RUNTIME RESOLUTION UNIVERSE (critical, empirically established)
===============================================================
A TQAE Custom-Quest mod loads its OWN `Database/SoulvizierClassic.arz` overlaid on
the base game `Database/database.arz`. The SVAERA base it was merged from ships an
essentially EMPTY custom arz (SVAERA_customquest.arz is a 2 KB stub), so the ONLY
record-resolution universe at runtime is:  mod arz  UNION  base-game arz
(50,353 + 74,013 = 91,595 distinct records here). Text tags resolve against
mod Text.arc (modstrings.txt) UNION base Text_EN.arc (14,777 + base = 20,948).
Record paths in .qst use forward slashes + mixed case; arz names use backslashes +
lowercase; level blobs embed placed DBR paths as lowercase-backslash. All lookups
are separator/case normalized (see `norm`).

SCOPE (false-positive discipline, mirrors tools/validate_tags.py)
=================================================================
The 106 shipped .qst are SVAERA's native questline PLUS the four ported SV
questlines. The native questline carries pre-existing upstream debt (e.g.
`sv_commonmechanics.qst`, a 671 KB vestigial crafting controller, references ~2000
SV item-upgrade records absent from mod+base+SV-098i; that crafting path is
superseded by the mod's baked make_enchantable enchanting). Flagging inherited
native debt would drown the signal, so the STRICT record/placement/loot contracts
fire only on MOD-AUTHORED content (the four ported SV quests + any record ref in a
drx*/DRX namespace or "proxies custom/"). Tag-resolution and placeholder checks are
naturally false-positive-free (the mod+base tag union resolves every native tag),
so they run over ALL quests. Inherited native dead-refs are recorded separately as
INFORMATIONAL (never as P0/P1 and never affecting the exit code); see
`run(cfg)['_informational']` and the emitted JSON.

INTERFACE
=========
  run(cfg: dict) -> list[dict]
    cfg keys: arz, text_arc, levels_arc, quests_arc, resource_arc_dir,
              base_game_dir, upstream_dir  (levels_arc/base_game_dir optional;
              placement + load-window + tag-union degrade gracefully if absent).
  CONTRACTS  = list of {id, name, asserts, derived_from}
  Standalone:  python contracts_quests.py <arz> <text_arc> <levels_arc>
                      <quests_arc> <resource_arc_dir> <base_game_dir> <upstream_dir>
               prints one JSON object per violation, exit 1 iff any P0/P1.
  Whitelist:   tools/contracts/whitelist_quests.txt  ("<CONTRACT-ID> <subject>"
               per line, '#' comments) suppresses listed (contract, subject) pairs.

This module is self-contained: it imports the repo's big loaders (arz_patcher,
arc_patcher) BY PATH and COPIES the small .qst parser (from tools/qst_format.py)
and the map-section parsers (from tools/merge_levels_binary.py) inline, editing
none of them.
"""

import sys
import re
import json
import struct
import contextlib
from pathlib import Path

# ---- import the repo's big loaders BY PATH (sanctioned; read-only) -----------
_TOOLS_DIR = Path(__file__).resolve().parent.parent   # .../tools
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
from arz_patcher import ArzDatabase          # noqa: E402
from arc_patcher import ArcArchive           # noqa: E402


# =============================================================================
# COPIED: .qst binary parser  (from tools/qst_format.py; do not edit that file)
# Round-trip-verified reader; we only need parse() + its type oracle.
# =============================================================================

_QST_INT_FIELDS = frozenset({
    'max', 'conditionCount', 'actionCount',
    'isActive', 'bRatchet', 'isNot', 'isResettable',
    'isQuestCritical', 'isQuestCritical2',
    'canReFire', 'onOff', 'fade',
    'bAlwaysClose', 'doComplete', 'doSound',
    'allowInterruptions', 'invincible', 'isPerPartyMember',
    'isQuestSkill', 'looping', 'useActionTarget',
    'enableTimeProgression',
    'rewardGold', 'rewardXP', 'rewardSkill', 'rewardAttr',
    'localRewardGold', 'localRewardXP',
    'delayTime', 'fadeTime',
    'x', 'y', 'z',
    'region', 'mode', 'type', 'value', 'index',
    'amplitude', 'animation', 'duration', 'fight',
    'timeInSecs', 'timeOfDay',
    'num', 'attributeAmount', 'experiencePts', 'moneyAmount', 'skillAmount',
})


def _qst_is_int_field(key):
    base = key
    if base.startswith('this->'):
        base = base[6:]
    if '[' in base:
        base = base[:base.index('[')]
    return base in _QST_INT_FIELDS


def _qst_valid_token_at(data, p):
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
        s = data[p + 4:p + 4 + slen].decode('ascii')
        return all(c.isalnum() or c in "_->[]() .'!-" for c in s)
    except (UnicodeDecodeError, ValueError):
        return False


def qst_parse(data):
    """Parse .qst bytes into a nested tree (list of top-level block item-lists).

    Item forms:
      ('block', sub_items)
      ('field', key, ('int', v)) | ('str', v) | ('int_or_empty', 0)
    """
    pos = [0]

    def read_u32():
        v = struct.unpack_from('<I', data, pos[0])[0]
        pos[0] += 4
        return v

    def read_len_str():
        slen = read_u32()
        s = data[pos[0]:pos[0] + slen].decode('utf-8', errors='replace')
        pos[0] += slen
        return s

    def read_field_value(key):
        val_raw = read_u32()
        if _qst_is_int_field(key):
            return ('int', val_raw)
        if val_raw == 0:
            return ('int_or_empty', 0)
        str_end = pos[0] + val_raw
        if val_raw <= 5000 and str_end <= len(data):
            try:
                sv = data[pos[0]:str_end].decode('utf-8')
                printable = all(c.isprintable() or c in '\r\n\t' for c in sv)
            except (UnicodeDecodeError, ValueError):
                printable = False
            if printable and _qst_valid_token_at(data, str_end):
                pos[0] = str_end
                return ('str', sv)
        if _qst_valid_token_at(data, pos[0]):
            return ('int', val_raw)
        raise ValueError(
            "Cannot type field '%s'=%d at 0x%04x" % (key, val_raw, pos[0] - 4))

    def parse_block():
        fields = []
        while pos[0] < len(data):
            token = read_len_str()
            if token == 'begin_block':
                read_u32()
                fields.append(('block', parse_block()))
            elif token == 'end_block':
                read_u32()
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


# =============================================================================
# COPIED: world01.map section parsers (from tools/merge_levels_binary.py)
# =============================================================================
SEC_LEVELS = 0x01
SEC_DATA = 0x02
SEC_QUESTS = 0x1B


def map_parse_sections(data):
    sections = []
    pos = 8
    while pos + 8 <= len(data):
        st = struct.unpack_from('<I', data, pos)[0]
        ss = struct.unpack_from('<I', data, pos + 4)[0]
        if ss > len(data) - pos - 8:
            break
        sections.append({'type': st, 'header_offset': pos,
                         'data_offset': pos + 8, 'size': ss})
        pos += 8 + ss
    return sections


def map_parse_quests(data, sec):
    buf = data[sec['data_offset']:sec['data_offset'] + sec['size']]
    count = struct.unpack_from('<I', buf, 0)[0]
    out = []
    idx = 4
    for _ in range(count):
        qlen = struct.unpack_from('<I', buf, idx)[0]
        idx += 4
        out.append(buf[idx:idx + qlen])
        idx += qlen
    return out


# =============================================================================
# constants / derivations
# =============================================================================

# The four ported SV questlines (docs: CLAUDE.md build22, PLAYBOOK §11).
SV_PORTED_QUESTS = frozenset({
    'open_bloodcave_portal.qst', 'urder.qst', 'widowletter.qst', 'bossarena.qst',
})

# .qst fields whose string value is a record path (.dbr).
RECORD_REF_FIELDS = frozenset({
    'proxyRecord', 'creatureRecord', 'itemRecord', 'itemName', 'personRecord',
    'volumeRecord', 'entityRecord', 'characterRecord', 'npc', 'door', 'fixedItem',
    'entity', 'location', 'creature', 'proxy', 'skill', 'dynGridEntranceName',
    'item[0]', 'item[1]', 'item[2]', 'dialogFile',
})

# .qst fields whose string value is a DISPLAY tag (rendered in-game).
DISPLAY_TAG_FIELDS = frozenset({
    'locationTag', 'titleTag', 'fullTextTag', 'bulletPointTag',
    'descriptionTag', 'tag', 'FileTextTag',
})

# Engine quest load window (QUEST_STATE_INJECT.md + build22): vanilla registers
# EXACTLY 256 quests and every one (idx 0..255) loads. Entries beyond vanilla's
# count never load (the widow-letter root cause: widowletter sat at idx 256 in
# the pre-build22 map). The build22 fix rebuilt the list to EXACTLY 256 entries
# with the four mod quests at idx 97-100 and idx 254-255 byte-identical to
# vanilla (x4_other_002_hcdungeon_control + x2_StartQuest -> provably load).
#   HARD_WINDOW (256): any quest at idx >= 256 never loads (absolute; only
#     reachable if the registration list overflows past vanilla's count).
#   LOAD_WINDOW (254): the proven-safe zone for MOD quests. build22 deliberately
#     kept mod quests below 254 and reserved 254-255 for the vanilla-parity pair,
#     so a mod quest at idx >= 254 is outside the proven-safe zone (and would
#     displace the boundary parity). Native quests at 254-255 are fine (they ARE
#     the vanilla pair), so the absolute check uses HARD_WINDOW for them.
LOAD_WINDOW = 254
HARD_WINDOW = 256
MAX_REGISTRATIONS = 256

# Placeholder tag class (BACKLOG B-SUPRA-NOTIFY-1): SV's debug notification tags.
PLACEHOLDER_TAG_RE = re.compile(r'tester', re.IGNORECASE)
# Placeholder tag VALUES occasionally seen in SV upstream (defensive).
PLACEHOLDER_TAG_VALUES = frozenset({'tester', 'todo', 'xxx', 'placeholder',
                                    'temp', 'test', 'fixme'})

# Loot-table record classes (base-game precedent).
LOOT_TABLE_CLASS_HINT = 'loot'   # substring match: LootItemTable_*, LootMasterTable

# FixedItem door/container classes that carry a `locked` flag.
FIXED_DOOR_CLASSES = frozenset({
    'fixeditemdoor', 'fixeditemcontainer',
})

# The widow letter static record (PLAYBOOK §11 / BLOODCAVE_QUESTS_RCA).
LETTER_RECORD = 'records/drxmap/quest/finalletter.dbr'


CONTRACTS = [
    {
        'id': 'QST-REC-EXISTS',
        'name': 'Mod-quest record references resolve at runtime',
        'asserts': 'Every proxy/monster/item/door/entity/location/skill/dialog '
                   '.dbr referenced by a mod-authored quest (the 4 ported SV '
                   'quests + any drx/proxies-custom ref) exists in the mod arz '
                   'UNION the base-game arz.',
        'derived_from': 'Runtime resolves mod SoulvizierClassic.arz (50,353 recs) '
                        'over base database.arz (74,013 recs); SVAERA_customquest.arz '
                        'is a 2 KB empty stub, so mod+base is the whole universe. '
                        'All 4 SV quests resolve 100% on the build27 baseline.',
    },
    {
        'id': 'QST-PROXY-PLACED',
        'name': 'KillAllCreaturesFromProxy watches a placed proxy',
        'asserts': 'Every Condition_KillAllCreaturesFromProxy proxyRecord in a '
                   'mod quest is not only in the arz but PLACED in the merged map '
                   '(its .dbr path is embedded in a level blob); else the kill '
                   'condition can never be satisfied and the quest stalls.',
        'derived_from': 'A placed proxy entity stores its .dbr path in its level '
                        'blob (lowercase-backslash). Verified: the 3 blood-cave '
                        'guardian proxies (q_highpriest/q_shaman/q_leinth_lone) are '
                        'all placed. Ties to BACKLOG B-TEMPLE-DOOR-1.',
    },
    {
        'id': 'QST-DOOR-UNLOCK',
        'name': 'Action_UnlockFixedItem targets a placed locked door',
        'asserts': 'Every Action_UnlockFixedItem fixedItem in a mod quest resolves, '
                   'is placed in the map, and (if a FixedItemDoor/Container) starts '
                   'locked=1; unlocking an absent or already-open door is a no-op.',
        'derived_from': 'Base-game guardian-gated doors ship locked=1. The 4 mod '
                        'drx doors that are unlock targets (waterfall secretdoor, '
                        'waterblocker, hc_treasurydoor02_boss, tj_door01) are all '
                        'locked=1 and placed. Ties to BACKLOG B-TEMPLE-DOOR-1.',
    },
    {
        'id': 'QST-GIVEITEM-NONEMPTY',
        'name': 'Action_GiveItem hands out a resolvable, non-empty reward',
        'asserts': 'Every Action_GiveItem item[0..2] in a mod quest resolves in '
                   'mod+base arz, and if it is a loot table it has >=1 lootName '
                   'entry that itself resolves (an empty/all-dead table gives '
                   'nothing).',
        'derived_from': 'supra_special (the hidden-chest reward) is a '
                        'LootItemTable_FixedWeight with 25 recipe entries, all of '
                        'which resolve. Ties to BACKLOG B-CHEST-1 / B-SUPRA-NOTIFY-1.',
    },
    {
        'id': 'QST-TAG-RESOLVES',
        'name': 'Displayed quest tags resolve to Text',
        'asserts': 'Every notification/journal display tag a quest shows '
                   '(locationTag/titleTag/fullTextTag/bulletPointTag/'
                   'descriptionTag/tag/FileTextTag) resolves in mod Text.arc '
                   'UNION base Text_EN.arc; else the raw tag string shows in-game.',
        'derived_from': 'Mirrors tools/validate_tags.py against the mod+base tag '
                        'union (20,948 tags). All 314 displayed quest tags resolve '
                        'on the build27 baseline.',
    },
    {
        'id': 'QST-TAG-PLACEHOLDER',
        'name': 'Displayed quest tags are not debug placeholders',
        'asserts': 'No displayed quest tag is a known SV debug placeholder '
                   '(tagTitleTagTESTER / tagLOCATIONTAGTESTER class, i.e. a '
                   'TESTER-named key or a placeholder value); these produce the '
                   'silent/mislabeled reward notification.',
        'derived_from': 'BACKLOG B-SUPRA-NOTIFY-1: the Esfri supra-formula grant in '
                        'open_bloodcave_portal.qst uses tagLOCATIONTAGTESTER + '
                        'tagTitleTagTESTER, so the reward notification is a '
                        'placeholder (players miss the reward).',
    },
    {
        'id': 'QST-LOAD-WINDOW',
        'name': 'OnLevelLoad quests load within the engine window',
        'asserts': 'Each ported SV quest is registered in the map QUESTS section '
                   'inside the proven-safe zone (index < 254); no OnLevelLoad '
                   'quest is registered at index >= 256 (vanilla\'s count); the '
                   'registration list is <= 256 entries. Past the window the '
                   'engine never loads the quest so OnLevelLoad never fires. '
                   '(Native quests at the vanilla-parity slots 254-255 load '
                   'normally and are not flagged.)',
        'derived_from': 'QUEST_STATE_INJECT.md + build22: vanilla world01.map '
                        'registers exactly 256 quests and all load; entries past '
                        'the original ~254 never load (the widow-letter bug). Fix '
                        'placed the 4 SV quests at idx 97-100.',
    },
    {
        'id': 'QST-WIDOW-LETTER',
        'name': 'Widow-letter single-letter deploy coupling holds',
        'asserts': 'widowletter.qst contains ZERO Action_SpawnEntityAtLocation '
                   'targeting finalletter.dbr (spawn neutralized) AND the static '
                   'finalletter.dbr is placed in the map; violating either yields '
                   'no letter or a double letter.',
        'derived_from': 'PLAYBOOK §11 + CLAUDE.md build22 deploy coupling: the '
                        'letter is placed statically in the map, so the quest\'s '
                        'own spawn action is removed (build_quest_files.py). '
                        'Baseline: 0 spawn actions, letter placed.',
    },
    {
        'id': 'QST-LEINTH-EXIT',
        'name': 'Every Leinth death opens the Sanctuary exit portal',
        'asserts': 'In open_bloodcave_portal.qst step "Boss Room Crystal Gate", '
                   'EVERY trigger whose condition fires on Leinth dying (the '
                   'Condition_KillAllCreaturesFromProxy(q_leinth_lone) primary AND '
                   'each Condition_KillCreature(q_leinth_47/49/50) fallback) carries '
                   'the FULL exit action set - Action_OpenDoor(door_bossroom_trap) + '
                   'Action_ShowNpc(vortexportal_exit) + Action_UpdateNPCDialog('
                   'vortexportal_exit) + Action_BoatDialog(vortexportal_exit, '
                   'tagReturnFromLeinthBattle) - and the primary is isResettable=1. '
                   'A trigger that opens the door WITHOUT showing the portal strands '
                   'the player in the boss room.',
        'derived_from': 'b94 PART C: the shipped build had the rich action set ONLY '
                        'on the one-shot proxy primary, while the three b48 '
                        'Condition_KillCreature fallbacks carried Action_OpenDoor '
                        'alone - so whenever the proxy-wide condition did not '
                        'satisfy the door opened and no exit portal ever appeared '
                        '(Will\'s live report). vortexportal_exit is placed exactly '
                        'once (bossfight.lvl) and its destination already lands '
                        '9.8u from the occultist merchant, so this is a '
                        'Quests.arc-only invariant.',
    },
    {
        'id': 'QST-LEINTH-NOKILL',
        'name': 'A no-kill exit fallback rescues already-latched characters',
        'asserts': 'In open_bloodcave_portal.qst step "Boss Room Crystal Gate" there '
                   'is EXACTLY ONE Condition_OnLevelLoad trigger tagged "Show Exit '
                   'Portal Fallback" carrying Action_ShowNpc + Action_UpdateNPCDialog '
                   '+ Action_BoatDialog on vortexportal_exit with tag '
                   'tagReturnFromLeinthBattle, and it must NOT carry Action_OpenDoor '
                   '(the boss trap door stays earned). Zero such triggers = a '
                   'character who already killed Leinth while the one-shot primary '
                   'was latched is permanently stranded; two or more = duplicated '
                   'travel offers on one NPC.',
        'derived_from': 'Will 2026-07-27, answering the residual R-74 flagged: "ADD '
                        'THE NO-KILL FALLBACK. Show the exit whenever the boss trap '
                        'door is already open, regardless of whether the kill trigger '
                        'latched - so a character who already killed her (INCLUDING '
                        'WILL\'S OWN) is rescued rather than stranded." The .qst '
                        'condition vocabulary has no door-state test, so '
                        'Condition_OnLevelLoad is the only mechanism that satisfies '
                        'the requirement; Action_OpenDoor is deliberately stripped so '
                        'the fallback reveals the way out without granting the fight.',
    },
]

# ── QST-LEINTH-EXIT constants ───────────────────────────────────────────────
# NOTE: norm() lowercases and converts to FORWARD slashes, so every constant
# compared through norm() is stored in that form (same convention as LETTER_RECORD).
LEINTH_QUEST = 'open_bloodcave_portal.qst'
LEINTH_STEP = 'Boss Room Crystal Gate'
LEINTH_EXIT_NPC = 'records/drxmap/bloodcave/portals/vortexportal_exit.dbr'
LEINTH_EXIT_TAG = 'tagReturnFromLeinthBattle'
LEINTH_EXIT_DOOR = 'records/drxmap/bloodcave/triggers/door_bossroom_trap.dbr'
LEINTH_PROXY = 'records/drxmap/proxy/q_leinth_lone.dbr'
LEINTH_VARIANTS = {
    'records/drxcreatures/bloodwitch/q_leinth_47.dbr',
    'records/drxcreatures/bloodwitch/q_leinth_49.dbr',
    'records/drxcreatures/bloodwitch/q_leinth_50.dbr',
}
LEINTH_EXIT_ACTIONS = ('Action_OpenDoor', 'Action_ShowNpc',
                       'Action_UpdateNPCDialog', 'Action_BoatDialog')

# ── QST-LEINTH-NOKILL constants (b94 round 3, Will 2026-07-27) ──────────────
LEINTH_NOKILL_TAG = 'Show Exit Portal Fallback'
LEINTH_NOKILL_COND = 'Condition_OnLevelLoad'
LEINTH_NOKILL_ACTIONS = ('Action_ShowNpc', 'Action_UpdateNPCDialog',
                         'Action_BoatDialog')


# =============================================================================
# helpers
# =============================================================================

@contextlib.contextmanager
def _stdout_to_stderr():
    """Redirect stdout to stderr for the duration. ArzDatabase.from_arz prints
    load progress to stdout; this keeps the module's stdout a pure JSON-lines
    stream (the standalone interface) while progress still shows on stderr."""
    old = sys.stdout
    sys.stdout = sys.stderr
    try:
        yield
    finally:
        sys.stdout = old


def norm(s):
    """Normalize a record/quest path: lowercase, forward slashes, no leading
    'database/' or '/'. Matches arz names (lowercase-backslash) and map blobs."""
    if not s:
        return ''
    s = s.strip().lower().replace('\\', '/').lstrip('/')
    if s.startswith('database/'):
        s = s[len('database/'):]
    return s


def is_mod_ref(nref, quest_basename):
    """A record ref is mod-authored iff it lives in the quest we ported OR is a
    DRX / proxies-custom namespace record (no base-game path contains 'drx')."""
    if quest_basename in SV_PORTED_QUESTS:
        return True
    return ('drx' in nref) or ('proxies custom/' in nref)


def walk_conditions_actions(tree):
    """Yield (kind, class_name, fields) for every condition/action in a parsed
    .qst tree. kind in {'cond','act'}; fields = {field_key: (type, value)}."""
    out = []

    def rec(items):
        i = 0
        n = len(items)
        while i < n:
            it = items[i]
            if it[0] == 'field' and it[1] in ('conditionClassName', 'actionClassName'):
                kind = 'cond' if it[1] == 'conditionClassName' else 'act'
                cls = it[2][1]
                fields = {}
                if i + 1 < n and items[i + 1][0] == 'block':
                    for f in items[i + 1][1]:
                        if f[0] == 'field':
                            fields[f[1]] = f[2]
                    i += 2
                    out.append((kind, cls, fields))
                    continue
                out.append((kind, cls, fields))
            elif it[0] == 'block':
                rec(it[1])
            i += 1

    for blk in tree:
        rec(blk)
    return out


def str_fields(fields):
    """Return {key: value} for non-empty string fields only."""
    return {k: v[1] for k, v in fields.items()
            if isinstance(v, tuple) and v[0] == 'str' and v[1]}


def load_quests(quests_arc_path):
    """Return {basename: [(kind, cls, fields), ...]} for every .qst in the arc.

    Also returns a dict {basename: raw_bytes} for optional re-use."""
    arc = ArcArchive.from_file(Path(quests_arc_path))
    quests = {}
    raw = {}
    for e in arc.entries:
        if e.entry_type != 3 or not e.name.lower().endswith('.qst'):
            continue
        base = e.name.replace('\\', '/').split('/')[-1]
        data = arc.decompress(e)
        raw[base] = data
        try:
            quests[base] = walk_conditions_actions(qst_parse(data))
        except Exception as ex:   # pragma: no cover - malformed blob
            quests[base] = [('_parse_error', str(ex), {})]
    return quests, raw


def load_arz(path):
    """Return (ArzDatabase, {norm_name: stored_name}) or (None, {}) if absent."""
    p = Path(path)
    if not p.exists():
        return None, {}
    db = ArzDatabase.from_arz(p)
    names = {norm(n): n for n in db.record_names()}
    return db, names


def load_text_tags(arc_path):
    """Return {tag: value} for every tag=value line across all .txt in the arc."""
    p = Path(arc_path)
    if not p.exists():
        return {}
    arc = ArcArchive.from_file(p)
    tags = {}
    for e in arc.entries:
        if e.entry_type != 3 or not e.name.lower().endswith('.txt'):
            continue
        text = arc.get_text(e.name)
        if not text:
            continue
        for line in text.split('\n'):
            line = line.strip('\r')
            if not line or line.lstrip().startswith('//') or '=' not in line:
                continue
            k, _, v = line.partition('=')
            tags.setdefault(k.strip(), v.strip())
    return tags


def load_map(levels_arc_path):
    """Decompress world01.map once; return (registrations, reg_index, placed_set)
    or (None, None, None) if unavailable.

    registrations = list of quest form names (str, as registered)
    reg_index     = {stem_lower: first_index}
    placed_set    = set of normalized .dbr paths embedded anywhere in the map."""
    p = Path(levels_arc_path) if levels_arc_path else None
    if not p or not p.exists():
        return None, None, None
    arc = ArcArchive.from_file(p)
    file_entries = [e for e in arc.entries if e.entry_type == 3]
    if not file_entries:
        return None, None, None
    data = arc.decompress(file_entries[0])
    secs = {s['type']: s for s in map_parse_sections(data)}
    registrations = []
    reg_index = {}
    if SEC_QUESTS in secs:
        for i, qb in enumerate(map_parse_quests(data, secs[SEC_QUESTS])):
            name = qb.decode('ascii', 'replace')
            registrations.append(name)
            stem = name.replace('\\', '/').split('/')[-1].lower()
            if stem.endswith('.qst'):
                stem = stem[:-4]
            elif stem.endswith('.que'):
                stem = stem[:-4]
            reg_index.setdefault(stem, i)
    placed = set()
    for m in re.finditer(rb'records\\[\x20-\x7e]{3,220}?\.dbr', data):
        placed.add(m.group(0).decode('latin-1').lower().replace('\\', '/'))
    del data
    return registrations, reg_index, placed


def _v(contract, severity, subject, message, evidence):
    return {'contract': contract, 'severity': severity, 'subject': subject,
            'message': message, 'evidence': evidence}


def _class_of(name, moddb, mod_names, basedb, base_names):
    """Return (Class_string_lower, ArzDatabase_owning_it, stored_name) or
    (None, None, None). Prefers the mod arz (mod records override base)."""
    n = norm(name)
    if n in mod_names and moddb is not None:
        stored = mod_names[n]
        cls = moddb.get_field_value(stored, 'Class')
        return (str(cls).lower() if cls else ''), moddb, stored
    if n in base_names and basedb is not None:
        stored = base_names[n]
        cls = basedb.get_field_value(stored, 'Class')
        return (str(cls).lower() if cls else ''), basedb, stored
    return None, None, None


# =============================================================================
# context (so the per-contract checks are unit-testable in isolation)
# =============================================================================

class Ctx:
    __slots__ = ('quests', 'raw', 'moddb', 'mod_names', 'basedb', 'base_names',
                 'union', 'tags', 'registrations', 'reg_index', 'placed',
                 'have_map', 'have_base_arz', 'have_tag_union')

    def __init__(self):
        self.quests = {}
        self.raw = {}
        self.moddb = None
        self.mod_names = {}
        self.basedb = None
        self.base_names = {}
        self.union = set()
        self.tags = set()
        self.registrations = None
        self.reg_index = None
        self.placed = None
        self.have_map = False
        self.have_base_arz = False
        self.have_tag_union = False


def build_context(cfg):
    # All loaders run with stdout redirected to stderr so the arz loader's
    # progress prints never pollute the module's JSON-lines stdout contract.
    with _stdout_to_stderr():
        ctx = Ctx()
        ctx.quests, ctx.raw = load_quests(cfg['quests_arc'])
        ctx.moddb, ctx.mod_names = load_arz(cfg['arz'])

        base_dir = cfg.get('base_game_dir')
        if base_dir:
            base_arz = Path(base_dir) / 'Database' / 'database.arz'
            ctx.basedb, ctx.base_names = load_arz(base_arz)
            ctx.have_base_arz = ctx.basedb is not None
        ctx.union = set(ctx.mod_names) | set(ctx.base_names)

        mod_tags = load_text_tags(cfg['text_arc'])
        base_tags = {}
        if base_dir:
            base_text = Path(base_dir) / 'Text' / 'Text_EN.arc'
            base_tags = load_text_tags(base_text)
            ctx.have_tag_union = bool(base_tags)
        ctx.tags = set(mod_tags) | set(base_tags)

        regs, ridx, placed = load_map(cfg.get('levels_arc'))
        ctx.registrations, ctx.reg_index, ctx.placed = regs, ridx, placed
        ctx.have_map = placed is not None
    return ctx


# =============================================================================
# per-contract checks
# =============================================================================

def check_rec_exists(ctx, informational):
    """QST-REC-EXISTS. Mod-quest record refs must resolve in mod+base arz.
    Inherited native missing refs go to `informational` (not returned)."""
    viols = []
    for quest, ca in sorted(ctx.quests.items()):
        for kind, cls, fields in ca:
            for fk, val in str_fields(fields).items():
                if fk not in RECORD_REF_FIELDS or not val.lower().endswith('.dbr'):
                    continue
                nref = norm(val)
                if nref in ctx.union:
                    continue
                if is_mod_ref(nref, quest):
                    viols.append(_v(
                        'QST-REC-EXISTS', 'P1', '%s :: %s.%s' % (quest, cls, fk),
                        'mod quest references a record that resolves in neither '
                        'the mod arz nor the base-game arz (dead trigger)',
                        '%s -> %s' % (val, nref)))
                else:
                    informational.append(_v(
                        'QST-REC-EXISTS(inherited)', 'P2',
                        '%s :: %s.%s' % (quest, cls, fk),
                        'inherited native quest references a record absent from '
                        'mod+base arz (pre-existing SVAERA/upstream debt)', val))
    return viols


def check_proxy_placed(ctx):
    """QST-PROXY-PLACED. Mod KillAllCreaturesFromProxy proxies must be map-placed."""
    if not ctx.have_map:
        return []
    viols = []
    seen = set()
    for quest, ca in sorted(ctx.quests.items()):
        for kind, cls, fields in ca:
            if cls != 'Condition_KillAllCreaturesFromProxy':
                continue
            val = str_fields(fields).get('proxyRecord')
            if not val:
                continue
            nref = norm(val)
            if not is_mod_ref(nref, quest):
                continue
            key = (quest, nref)
            if key in seen:
                continue
            seen.add(key)
            if nref not in ctx.union:
                continue   # QST-REC-EXISTS owns the missing-record case
            if nref not in ctx.placed:
                viols.append(_v(
                    'QST-PROXY-PLACED', 'P1', '%s :: %s' % (quest, val),
                    'KillAllCreaturesFromProxy watches a proxy that exists in the '
                    'arz but is NOT placed in the merged map; the condition can '
                    'never be satisfied so the quest stalls',
                    'proxy %s not found in any level blob' % nref))
    return viols


def check_door_unlock(ctx):
    """QST-DOOR-UNLOCK. Mod Action_UnlockFixedItem targets = placed locked doors."""
    viols = []
    seen = set()
    for quest, ca in sorted(ctx.quests.items()):
        for kind, cls, fields in ca:
            if cls != 'Action_UnlockFixedItem':
                continue
            val = str_fields(fields).get('fixedItem')
            if not val:
                continue
            nref = norm(val)
            if not is_mod_ref(nref, quest):
                continue
            key = (quest, nref)
            if key in seen:
                continue
            seen.add(key)
            if nref not in ctx.union:
                continue   # QST-REC-EXISTS owns the missing-record case
            klass, owner, stored = _class_of(val, ctx.moddb, ctx.mod_names,
                                              ctx.basedb, ctx.base_names)
            # locked check: only for FixedItem door/container classes
            if klass in FIXED_DOOR_CLASSES:
                locked = owner.get_field_value(stored, 'locked') if owner else None
                if isinstance(locked, list):
                    locked = locked[0] if locked else None
                # Flag only an EXPLICIT locked=0 (a door authored unlocked yet
                # handed to an unlock action = no-op). A door with no `locked`
                # field is left alone to avoid false positives on classes/records
                # that do not carry the flag.
                if locked == 0:
                    viols.append(_v(
                        'QST-DOOR-UNLOCK', 'P2', '%s :: %s' % (quest, val),
                        'Action_UnlockFixedItem targets a %s authored unlocked '
                        '(locked=0); the unlock is a no-op'
                        % klass, 'Class=%s locked=0' % klass))
            # placement check (map available)
            if ctx.have_map and nref not in ctx.placed:
                viols.append(_v(
                    'QST-DOOR-UNLOCK', 'P1', '%s :: %s' % (quest, val),
                    'Action_UnlockFixedItem targets a door not placed in the '
                    'merged map; the unlock affects nothing',
                    'door %s not found in any level blob' % nref))
    return viols


def check_giveitem(ctx):
    """QST-GIVEITEM-NONEMPTY. Mod GiveItem targets resolve and (if loot) non-empty."""
    viols = []
    seen = set()
    for quest, ca in sorted(ctx.quests.items()):
        for kind, cls, fields in ca:
            if cls != 'Action_GiveItem':
                continue
            sf = str_fields(fields)
            for fk in ('item[0]', 'item[1]', 'item[2]'):
                val = sf.get(fk)
                if not val or not val.lower().endswith('.dbr'):
                    continue
                nref = norm(val)
                if not is_mod_ref(nref, quest):
                    continue
                key = (quest, nref)
                if key in seen:
                    continue
                seen.add(key)
                if nref not in ctx.union:
                    continue   # QST-REC-EXISTS owns the missing-record case
                klass, owner, stored = _class_of(val, ctx.moddb, ctx.mod_names,
                                                  ctx.basedb, ctx.base_names)
                if klass and LOOT_TABLE_CLASS_HINT in klass:
                    f = owner.get_fields(stored) if owner else {}
                    entries = []
                    for k in f:
                        base = k.split('###')[0].lower()
                        if base.startswith('lootname') and f[k].values and f[k].values[0]:
                            entries.append(f[k].values[0])
                    resolvable = [e for e in entries if norm(e) in ctx.union]
                    if not entries:
                        viols.append(_v(
                            'QST-GIVEITEM-NONEMPTY', 'P1', '%s :: %s' % (quest, val),
                            'Action_GiveItem hands out a loot table with zero '
                            'lootName entries (gives nothing)',
                            'Class=%s lootNames=0' % klass))
                    elif not resolvable:
                        viols.append(_v(
                            'QST-GIVEITEM-NONEMPTY', 'P1', '%s :: %s' % (quest, val),
                            'Action_GiveItem loot table has entries but NONE '
                            'resolve in mod+base arz (gives nothing)',
                            'Class=%s lootNames=%d resolvable=0'
                            % (klass, len(entries))))
    return viols


def check_tags(ctx):
    """QST-TAG-RESOLVES + QST-TAG-PLACEHOLDER. Runs over ALL quests (the mod+base
    tag union makes resolution false-positive-free)."""
    viols = []
    seen_missing = set()
    seen_ph = set()
    for quest, ca in sorted(ctx.quests.items()):
        for kind, cls, fields in ca:
            for fk, val in str_fields(fields).items():
                if fk not in DISPLAY_TAG_FIELDS:
                    continue
                if not val.lower().startswith('tag'):
                    continue
                # placeholder?
                if (PLACEHOLDER_TAG_RE.search(val)
                        or val.lower() in PLACEHOLDER_TAG_VALUES):
                    k = (quest, val)
                    if k not in seen_ph:
                        seen_ph.add(k)
                        viols.append(_v(
                            'QST-TAG-PLACEHOLDER', 'P2', '%s :: %s.%s' % (quest, cls, fk),
                            'quest displays a debug PLACEHOLDER tag (TESTER class); '
                            'the notification/journal text is a placeholder',
                            'tag=%s' % val))
                # resolution (only meaningful when a tag union is loaded)
                if ctx.have_tag_union and val not in ctx.tags:
                    k = (quest, val)
                    if k not in seen_missing:
                        seen_missing.add(k)
                        viols.append(_v(
                            'QST-TAG-RESOLVES', 'P1', '%s :: %s.%s' % (quest, cls, fk),
                            'quest displays a tag that resolves in neither mod '
                            'Text.arc nor base Text_EN.arc; the raw tag string '
                            'shows in-game', 'tag=%s' % val))
    return viols


def _has_on_level_load(ca):
    return any(cls == 'Condition_OnLevelLoad' for kind, cls, f in ca)


def check_load_window(ctx):
    """QST-LOAD-WINDOW. Mod OnLevelLoad quests must register within the window."""
    if not ctx.have_map or ctx.reg_index is None:
        return []
    viols = []
    # (a) total registration budget
    if ctx.registrations is not None and len(ctx.registrations) > MAX_REGISTRATIONS:
        viols.append(_v(
            'QST-LOAD-WINDOW', 'P1', 'world01.map QUESTS',
            'the map registers more quests than vanilla\'s proven-loading count; '
            'entries past the window never load',
            '%d registrations > %d' % (len(ctx.registrations), MAX_REGISTRATIONS)))
    # (b) each ported SV quest must be registered and inside the window
    for q in sorted(SV_PORTED_QUESTS):
        if q not in ctx.quests:
            continue
        stem = q[:-4] if q.endswith('.qst') else q
        idx = ctx.reg_index.get(stem)
        if idx is None:
            viols.append(_v(
                'QST-LOAD-WINDOW', 'P1', q,
                'ported SV quest is NOT registered in the map QUESTS section; it '
                'never loads (OnLevelLoad never fires)', 'stem %s absent' % stem))
        elif idx >= LOAD_WINDOW:
            viols.append(_v(
                'QST-LOAD-WINDOW', 'P1', q,
                'ported SV quest is registered past the engine load window; it '
                'never loads for any character (widow-letter root cause)',
                'idx %d >= %d' % (idx, LOAD_WINDOW)))
    # (c) any OnLevelLoad quest registered at/after the absolute window (256):
    #     these never load. Native quests at the vanilla-parity slots 254-255 are
    #     fine (they ARE the vanilla pair), so this uses HARD_WINDOW, not the
    #     stricter mod-only LOAD_WINDOW applied in (b).
    for quest, ca in sorted(ctx.quests.items()):
        if not _has_on_level_load(ca):
            continue
        stem = quest[:-4] if quest.endswith('.qst') else quest
        idx = ctx.reg_index.get(stem)
        if idx is not None and idx >= HARD_WINDOW:
            viols.append(_v(
                'QST-LOAD-WINDOW', 'P1', quest,
                'OnLevelLoad quest registered past vanilla\'s 256-entry count; it '
                'never loads so its level-load actions never fire',
                'idx %d >= %d' % (idx, HARD_WINDOW)))
    return viols


def check_widow_letter(ctx):
    """QST-WIDOW-LETTER. Spawn neutralization + static letter placement coupling."""
    viols = []
    q = 'widowletter.qst'
    ca = ctx.quests.get(q)
    if ca is None:
        return viols
    spawns = 0
    for kind, cls, fields in ca:
        if cls != 'Action_SpawnEntityAtLocation':
            continue
        ent = str_fields(fields).get('entity')
        if ent and norm(ent) == LETTER_RECORD:
            spawns += 1
    if spawns > 0:
        viols.append(_v(
            'QST-WIDOW-LETTER', 'P0', q,
            'widowletter.qst still spawns finalletter.dbr; combined with the '
            'static map letter this yields a DOUBLE letter (neutralization '
            'regressed)', '%d Action_SpawnEntityAtLocation targeting the letter'
            % spawns))
    if ctx.have_map and ctx.placed is not None and LETTER_RECORD not in ctx.placed:
        viols.append(_v(
            'QST-WIDOW-LETTER', 'P1', q,
            'the static finalletter.dbr is NOT placed in the merged map and the '
            'quest spawn is neutralized, so the player never receives the letter',
            'letter %s absent from map + quest spawn neutralized' % LETTER_RECORD))
    return viols


def _leinth_step_triggers(raw_bytes):
    """[(display_tag, condition_class, [condition_field_dicts], [action_class],
    {action_class: [field_dicts]})] for every trigger in the Leinth boss-room step.

    Walks the qst tree structurally (steps container -> flat (stepdef, trigger
    container, sentinel) triples -> flat (header, conditions, actions) triples)
    so the check is per-TRIGGER, not a flat action census: the whole defect class
    is a trigger that has SOME of the actions.
    """
    def bpos(items):
        return [i for i, it in enumerate(items) if it[0] == 'block']

    def fval(items, key):
        for it in items:
            if it[0] == 'field' and it[1] == key:
                return it[2][1]
        return None

    tree = qst_parse(raw_bytes)
    if len(tree) < 2:
        return None
    steps = tree[1]
    sp = bpos(steps)
    for sd, tc, _sn in [sp[i:i + 3] for i in range(0, len(sp), 3)]:
        if fval(steps[sd][1], 'name') != LEINTH_STEP:
            continue
        trig = steps[tc][1]
        tp = bpos(trig)
        out = []
        for (h, c, a) in [tp[i:i + 3] for i in range(0, len(tp), 3)]:
            conds = trig[c][1]
            acts = trig[a][1]
            cond_blocks = [dict((f[1], f[2]) for f in it[1] if f[0] == 'field')
                           for it in conds if it[0] == 'block']
            act_classes = [it[2][1] for it in acts
                           if it[0] == 'field' and it[1] == 'actionClassName']
            act_blocks = {}
            cur = None
            for it in acts:
                if it[0] == 'field' and it[1] == 'actionClassName':
                    cur = it[2][1]
                elif it[0] == 'block' and cur:
                    act_blocks.setdefault(cur, []).append(
                        dict((f[1], f[2]) for f in it[1] if f[0] == 'field'))
                    cur = None
            out.append((fval(trig[h][1], 'displayTag'),
                        fval(conds, 'conditionClassName'),
                        cond_blocks, act_classes, act_blocks))
        return out
    return None


def check_leinth_exit(ctx):
    """QST-LEINTH-EXIT. Every Leinth-death trigger must ALSO show the exit portal."""
    viols = []
    raw = (ctx.raw or {}).get(LEINTH_QUEST)
    if raw is None:
        return viols
    try:
        triggers = _leinth_step_triggers(raw)
    except Exception as ex:                      # pragma: no cover - malformed blob
        return [_v('QST-LEINTH-EXIT', 'P1', LEINTH_QUEST,
                   'could not parse the boss-room step to verify the exit portal',
                   repr(ex))]
    if triggers is None:
        return [_v('QST-LEINTH-EXIT', 'P1', LEINTH_QUEST,
                   'step %r not found; the Leinth exit portal cannot be verified'
                   % LEINTH_STEP, 'step missing from the shipped quest')]

    death_triggers = 0
    for tag, cls, cond_blocks, act_classes, act_blocks in triggers:
        is_primary = any(
            norm(b['proxyRecord'][1]) == LEINTH_PROXY
            for b in cond_blocks
            if isinstance(b.get('proxyRecord'), tuple) and b['proxyRecord'][0] == 'str')
        is_kill = any(
            norm(b['creatureRecord'][1]) in LEINTH_VARIANTS
            for b in cond_blocks
            if isinstance(b.get('creatureRecord'), tuple) and b['creatureRecord'][0] == 'str')
        if not (is_primary or is_kill):
            continue
        death_triggers += 1
        subject = '%s :: %s' % (LEINTH_QUEST, tag or cls)

        missing = [a for a in LEINTH_EXIT_ACTIONS if a not in act_classes]
        if missing:
            viols.append(_v(
                'QST-LEINTH-EXIT', 'P0', subject,
                'a Leinth-death trigger is missing %s, so this death path opens the '
                'boss door but never shows the Sanctuary exit portal - the player is '
                'stranded in the boss room' % ', '.join(missing),
                'carries %s' % (act_classes or '[]')))
            continue

        for cls_name in ('Action_ShowNpc', 'Action_UpdateNPCDialog', 'Action_BoatDialog'):
            for blk in act_blocks.get(cls_name, []):
                npc = blk.get('npc')
                if not (isinstance(npc, tuple) and npc[0] == 'str'
                        and norm(npc[1]) == LEINTH_EXIT_NPC):
                    viols.append(_v(
                        'QST-LEINTH-EXIT', 'P0', subject,
                        '%s targets %r, not the placed exit NPC vortexportal_exit'
                        % (cls_name, npc), 'expected %s' % LEINTH_EXIT_NPC))
        for blk in act_blocks.get('Action_BoatDialog', []):
            tagv = blk.get('tag')
            if not (isinstance(tagv, tuple) and tagv[0] == 'str'
                    and tagv[1] == LEINTH_EXIT_TAG):
                viols.append(_v(
                    'QST-LEINTH-EXIT', 'P0', subject,
                    'the exit BoatDialog offer tag is %r, not %s - the player gets a '
                    'raw tag or no prompt' % (tagv, LEINTH_EXIT_TAG),
                    'expected tag %s' % LEINTH_EXIT_TAG))
        for blk in act_blocks.get('Action_OpenDoor', []):
            d = blk.get('door')
            if not (isinstance(d, tuple) and d[0] == 'str'
                    and norm(d[1]) == LEINTH_EXIT_DOOR):
                viols.append(_v(
                    'QST-LEINTH-EXIT', 'P1', subject,
                    'the Leinth-death OpenDoor targets %r, not the boss-room trap door'
                    % (d,), 'expected %s' % LEINTH_EXIT_DOOR))
        if is_primary:
            for b in cond_blocks:
                pr = b.get('proxyRecord')
                if isinstance(pr, tuple) and pr[0] == 'str' and norm(pr[1]) == LEINTH_PROXY:
                    rs = b.get('isResettable')
                    val = rs[1] if isinstance(rs, tuple) else rs
                    if int(val or 0) != 1:
                        viols.append(_v(
                            'QST-LEINTH-EXIT', 'P1', subject,
                            'the primary proxy trigger is one-shot (isResettable=%r), '
                            'so a character who already latched it never re-arms the '
                            'exit portal on a revisit' % (val,),
                            'isResettable must be 1'))

    want = 1 + len(LEINTH_VARIANTS)
    if death_triggers < want:
        viols.append(_v(
            'QST-LEINTH-EXIT', 'P1', LEINTH_QUEST,
            'only %d Leinth-death trigger(s) found in step %r, expected %d (the proxy '
            'primary + one Condition_KillCreature fallback per variant); a missing '
            'fallback is a death path with no exit' % (death_triggers, LEINTH_STEP, want),
            '%d of %d' % (death_triggers, want)))
    return viols


def check_leinth_nokill_exit(ctx):
    """QST-LEINTH-NOKILL. Exactly one OnLevelLoad exit fallback, and it must not
    open the boss trap door."""
    viols = []
    raw = (ctx.raw or {}).get(LEINTH_QUEST)
    if raw is None:
        return viols
    try:
        triggers = _leinth_step_triggers(raw)
    except Exception as ex:                      # pragma: no cover - malformed blob
        return [_v('QST-LEINTH-NOKILL', 'P1', LEINTH_QUEST,
                   'could not parse the boss-room step to verify the no-kill exit',
                   repr(ex))]
    if triggers is None:
        return [_v('QST-LEINTH-NOKILL', 'P1', LEINTH_QUEST,
                   'step %r not found; the no-kill exit fallback cannot be verified'
                   % LEINTH_STEP, 'step missing from the shipped quest')]

    found = 0
    for tag, cls, _cond_blocks, act_classes, act_blocks in triggers:
        if cls != LEINTH_NOKILL_COND or tag != LEINTH_NOKILL_TAG:
            continue
        found += 1
        subject = '%s :: %s' % (LEINTH_QUEST, tag)

        missing = [a for a in LEINTH_NOKILL_ACTIONS if a not in act_classes]
        if missing:
            viols.append(_v(
                'QST-LEINTH-NOKILL', 'P0', subject,
                'the no-kill exit fallback is missing %s, so an already-latched '
                'character still gets no travel offer and stays stranded'
                % ', '.join(missing), 'carries %s' % (act_classes or '[]')))
        if 'Action_OpenDoor' in act_classes:
            viols.append(_v(
                'QST-LEINTH-NOKILL', 'P0', subject,
                'the no-kill fallback carries Action_OpenDoor - it fires on every '
                'level load, so the boss trap door would open for a player who never '
                'fought Leinth', 'carries %s' % (act_classes,)))
        for cls_name in LEINTH_NOKILL_ACTIONS:
            for blk in act_blocks.get(cls_name, []):
                npc = blk.get('npc')
                if not (isinstance(npc, tuple) and npc[0] == 'str'
                        and norm(npc[1]) == LEINTH_EXIT_NPC):
                    viols.append(_v(
                        'QST-LEINTH-NOKILL', 'P0', subject,
                        '%s targets %r, not the placed exit NPC vortexportal_exit'
                        % (cls_name, npc), 'expected %s' % LEINTH_EXIT_NPC))
        for blk in act_blocks.get('Action_BoatDialog', []):
            tagv = blk.get('tag')
            if not (isinstance(tagv, tuple) and tagv[0] == 'str'
                    and tagv[1] == LEINTH_EXIT_TAG):
                viols.append(_v(
                    'QST-LEINTH-NOKILL', 'P0', subject,
                    'the no-kill BoatDialog offer tag is %r, not %s - the player gets '
                    'a raw tag or no prompt' % (tagv, LEINTH_EXIT_TAG),
                    'expected tag %s' % LEINTH_EXIT_TAG))

    if found == 0:
        viols.append(_v(
            'QST-LEINTH-NOKILL', 'P0', LEINTH_QUEST,
            'no %s trigger tagged %r in step %r - a character who already killed '
            'Leinth while the one-shot primary was latched (Will\'s own _Toxeus) is '
            'permanently stranded in the Sanctuary'
            % (LEINTH_NOKILL_COND, LEINTH_NOKILL_TAG, LEINTH_STEP),
            'expected exactly 1, found 0'))
    elif found > 1:
        viols.append(_v(
            'QST-LEINTH-NOKILL', 'P1', LEINTH_QUEST,
            'found %d no-kill exit fallbacks, expected exactly 1 - duplicated '
            'ShowNpc/BoatDialog on a single NPC' % found,
            'expected 1, found %d' % found))
    return viols


# =============================================================================
# whitelist + orchestration
# =============================================================================

def load_whitelist():
    """Return a set of (contract_id, subject) pairs to suppress."""
    wl = Path(__file__).resolve().parent / 'whitelist_quests.txt'
    pairs = set()
    if not wl.exists():
        return pairs
    for line in wl.read_text(encoding='utf-8', errors='replace').split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            pairs.add((parts[0].strip(), parts[1].strip()))
    return pairs


def run(cfg):
    """Run every quest contract; return the whitelist-filtered list of in-scope
    violation dicts (the mandated interface). Callers that also want the
    inherited-native informational findings + context flags should call
    run_detailed()."""
    return run_detailed(cfg)['violations']


def run_detailed(cfg):
    """Like run() but returns {'violations': [...], 'informational': [...],
    'context_flags': {...}} for richer reporting."""
    ctx = build_context(cfg)
    informational = []

    viols = []
    viols += check_rec_exists(ctx, informational)
    viols += check_proxy_placed(ctx)
    viols += check_door_unlock(ctx)
    viols += check_giveitem(ctx)
    viols += check_tags(ctx)
    viols += check_load_window(ctx)
    viols += check_widow_letter(ctx)
    viols += check_leinth_exit(ctx)
    viols += check_leinth_nokill_exit(ctx)

    wl = load_whitelist()
    if wl:
        viols = [v for v in viols if (v['contract'], v['subject']) not in wl]

    sev_rank = {'P0': 0, 'P1': 1, 'P2': 2}
    viols.sort(key=lambda v: (sev_rank.get(v['severity'], 9), v['contract'],
                              v['subject']))
    return {
        'violations': viols,
        'informational': informational,
        'context_flags': {
            'quests_parsed': len(ctx.quests),
            'mod_arz_records': len(ctx.mod_names),
            'base_arz_records': len(ctx.base_names),
            'union_records': len(ctx.union),
            'tags_union': len(ctx.tags),
            'have_base_arz': ctx.have_base_arz,
            'have_tag_union': ctx.have_tag_union,
            'have_map': ctx.have_map,
            'map_registrations': (len(ctx.registrations)
                                  if ctx.registrations is not None else None),
            'placed_dbr_paths': (len(ctx.placed)
                                 if ctx.placed is not None else None),
        },
    }


def _cfg_from_argv(argv):
    keys = ['arz', 'text_arc', 'levels_arc', 'quests_arc', 'resource_arc_dir',
            'base_game_dir', 'upstream_dir']
    cfg = {}
    for i, k in enumerate(keys):
        cfg[k] = argv[i] if i < len(argv) else None
    return cfg


def _main(argv):
    args = argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print(__doc__)
        print("\nusage: contracts_quests.py <arz> <text_arc> <levels_arc> "
              "<quests_arc> <resource_arc_dir> <base_game_dir> <upstream_dir>")
        return 0
    cfg = _cfg_from_argv(args)
    if not cfg.get('arz') or not cfg.get('quests_arc') or not cfg.get('text_arc'):
        sys.stderr.write("ERROR: arz, text_arc and quests_arc are required\n")
        return 2
    result = run_detailed(cfg)
    for v in result['violations']:
        sys.stdout.write(json.dumps(v, ensure_ascii=True) + '\n')
    # summary to stderr (does not pollute the JSON-lines stdout contract)
    flags = result['context_flags']
    sys.stderr.write(
        "\n[contracts_quests] %d violation(s); %d inherited-informational; "
        "flags=%s\n" % (len(result['violations']),
                        len(result['informational']), json.dumps(flags)))
    has_blocking = any(v['severity'] in ('P0', 'P1')
                       for v in result['violations'])
    return 1 if has_blocking else 0


if __name__ == '__main__':
    sys.exit(_main(sys.argv))
