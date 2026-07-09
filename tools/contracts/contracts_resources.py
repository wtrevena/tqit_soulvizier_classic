r"""PERMANENT CONTRACT SUITE - DOMAIN C: CROSS-ARTIFACT RESOURCE RESOLUTION.

The universal net. This module asserts, over the mod's SHIPPED artifacts, that
EVERY reference the shipped .arz makes to another thing resolves to something that
actually exists in-game:
  - every .dbr-to-.dbr record reference resolves in the mod .arz UNION the base game DB;
  - every mesh/texture/animation/particle/sound/shader/font path resolves inside the
    shipped resource .arc files OR the base-game .arc files (archive-name convention);
  - every text tag referenced (by an .arz record, a quest file, or a map SD zone name)
    resolves in the mod Text.arc UNION the base game Text_EN.arc;
  - no text tag is DEFINED twice with conflicting values (the Occult-shows-as-Rogue class);
  - every record's templateName resolves in the toolset Templates.arc.
It exists because the mod keeps shipping entities that LOOK complete but are dead
in-game because a required companion reference is missing (a summon whose mesh/anim
does not resolve spawns a naked/immobile shell; a name whose tag is absent renders as a
raw tag string).

RESOLUTION MODEL (reverse-engineered + measured from the build27 baseline, 2026-07-08):
  * The mod .arz is an OVERLAY, not a superset: it carries 50,353 records (17,582 of
    which are absent from the base game); it OMITS 41,242 base records. At runtime the
    base game database.arz (74,013 records) is present underneath, so a .dbr reference
    resolves iff its target is in (mod UNION base). Proof: 945 distinct .dbr targets in
    our .arz resolve ONLY via the base game DB (e.g. proxy pools -> base monster tiers).
  * Resource archive-name convention (CLAUDE.md lesson "first path component = archive
    name"): a reference "SVItems\armor\x.tex" resolves as arc SVItems.arc + internal entry
    "armor/x.tex". Immortal-Throne / expansion resources use the two-level form
    "XPack\Items\...", "XPack2\Creatures\..." -> Resources/XPack{,2,3,4}/<Arc>.arc. Sounds
    live in the separate Audio/ folder (Audio/Sounds.arc = 1977 entries), so the index
    MUST include base_game_dir/Audio. Measured: 19,748/22,869 distinct resource refs
    resolve by full path, +170 more by basename (the DRX bare-name mesh convention, e.g.
    "m_melinoesword01.msh" ships as drx.arc::meshes/m_melinoesword01.msh); the residue are
    real dangling refs (e.g. "need art a.tex" exists in NO arc; "spritefire_att_spitfire.anm"
    is absent though the base sprite folder ships _attalpha/_attbeta/_attgamma).
  * Templates are toolset schema, referenced as "database\Templates\X.tpl" and resolved
    against Toolset/Templates.arc (566 templates). 50,353/50,353 records carry templateName.
    A missing template is EDITOR-only (the engine reads field values directly from the .arz
    at runtime), so template misses are reported at P2. 15 custom "*2.tpl"/"*3.tpl" DRX/SV
    templates are absent from the base toolset (runtime-tolerant).
  * A referenced text tag renders as raw text in-game iff it is absent from BOTH the mod
    Text.arc (modstrings.txt: 14,777 keys) AND the base game Text_EN.arc (17,541 keys).

PROVENANCE / SEVERITY: a reference we authored that dangles is a regression we own (P1,
blocks the gate); a reference inherited verbatim from the DRX overhaul, from SV 0.98i, or
from a base-game passthrough record is pre-existing third-party debt (P2, reported but
never blocks). Provenance is name/namespace-based: a subject is 'drx' if its path contains
"drx"; else 'authored' if it carries a mod-team namespace token (soulskills, crimsonverdict,
veinrender, bloodtoxeus, hemorrheus) OR is absent from BOTH SV 0.98i AND the base game (a
pure mod invention); else 'sv' if present in SV 0.98i; else 'base'. (See caveats: an SV
record we MODIFIED so as to break a ref is labelled 'sv'/P2 here, not P1, because this
module does not field-diff against upstream; it is still reported.)

INTERFACE (composes with the other four domain modules without shared files):
  run(cfg: dict) -> list[dict]
    cfg keys: arz, text_arc, levels_arc, quests_arc, resource_arc_dir, base_game_dir,
              upstream_dir   (+ optional cache_dir)
    each violation: {'contract','severity','subject','message','evidence'}
  CONTRACTS: list of {'id','name','asserts','derived_from'}

WHITELIST: tools/contracts/whitelist_resources.txt - lines "<CONTRACT-ID> <subject>"
  suppress that exact (contract, subject) pair; '#' begins a comment.

STANDALONE:
  python tools/contracts/contracts_resources.py <arz> [text_arc] [levels_arc] [quests_arc]
        [resource_arc_dir] [base_game_dir] [upstream_dir]
  prints one JSON violation per line; exits 1 if any P0/P1 survives the whitelist, else 0.
  With no args, defaults to the frozen build27 scratch baseline (for self-test).
"""
import sys
import os
import re
import json
import time
import struct
import tempfile
from pathlib import Path
from collections import defaultdict, Counter

# ----------------------------------------------------------------------------
# Self-contained loader access: import the repo's stable .arz / .arc readers BY
# PATH (never editing them). tools/ is this file's grandparent.
# ----------------------------------------------------------------------------
_TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
from arz_patcher import ArzDatabase, DATA_TYPE_STRING   # noqa: E402
from arc_patcher import ArcArchive                      # noqa: E402


# ============================================================================
# CONSTANTS
# ============================================================================
# Compiled resource extensions that ship inside .arc files.
RES_EXT = frozenset({'msh', 'tex', 'anm', 'pfx', 'wav', 'mp3', 'ssh', 'fnt', 'ttf'})
# Source-art extensions (ArtManager compile INPUTS) that never ship in an arc; a "source\"
# reference is an editor artifact, not a runtime resource, so we do not resolve these.
SOURCE_EXT = frozenset({'tga', 'max', 'psd', 'bmp'})

# Free-text / name / tag fields that hold DESCRIPTIVE strings, never a runtime resource
# path. They must be excluded from asset detection even when a value coincidentally ends
# in a resource-looking extension: e.g. FileDescription='NEED ART B.tex' is a placeholder
# note on the Crimson Verdict helm (whose real mesh/bitmap are valid XPack paths).
ASSET_SKIP_FIELDS = frozenset({
    'FileDescription', 'ActorName', 'Class', 'description', 'itemText', 'itemNameTag',
    'lootRandomizerName', 'skillDisplayName', 'skillBaseDescription', 'setName',
})

# A tag reference is any clean tag-token value (all TQ display tags are "tag..."/"xtag...").
_TAG_TOKEN_RE = re.compile(r'^x?tag[A-Za-z0-9_]{2,60}$')
# ASCII tag tokens embedded in a quest-file / map-section byte blob.
_TAG_SCAN_RE = re.compile(rb'x?tag[A-Za-z0-9_]{2,60}')

# Mod-team namespace tokens: a subject carrying one of these is NEW content authored by the
# recent build waves - it does not exist in the base game OR in SV 0.98i (verified). These
# are a safety net on top of the primary "invention" test (absent from both upstream and
# base). NOTE: 'soulskills' is deliberately NOT here - 347/367 soulskills records ship in SV
# 0.98i, so that namespace is SV-inherited (its dangling refs are pre-existing SV debt -> P2,
# not our regression); only the genuinely-new soulskills inventions fall through to P1 via
# the invention test.
AUTHORED_TOKENS = ('crimsonverdict', 'veinrender', 'bloodtoxeus')

# Mod-authored tag prefixes (fallback when the mod_authored_tags.txt manifest is absent).
# Each has been confirmed to be authored into the mod's OWN Text.arc, never a base-game
# namespace, so it stays false-positive-free (mirrors validate_tags.py's caution).
MOD_TAG_PREFIXES = (
    'tagSoulSVC', 'tagSVCSoul', 'tagSVCSummon', 'tagSVCSet', 'tagSVCarm', 'tagSVChlm',
    'tagSVCtor', 'tagSVCwpn', 'tagSVC', 'tagDarkAperture', 'xtagMysteriousPortal',
    'tagMonsterHemorrheus', 'tagMZone', 'tagBCX',
)

# Map world-section ids (world01.map). SD (0x18) holds zone / region display-name tags.
_SEC_SD = 0x18


# ============================================================================
# CONTRACT REGISTRY (documents every contract this module asserts)
# ============================================================================
CONTRACTS = [
    {'id': 'C-RES-DBR-1',
     'name': 'Every .dbr record reference resolves',
     'asserts': 'Every records\\...\\*.dbr value referenced by a shipped .arz record exists '
                'as a record in the mod .arz UNION the base-game database.arz.',
     'derived_from': 'Runtime overlay model: 945 distinct .dbr targets resolve only via the '
                     'base DB, proving base is present at runtime; a target in neither = dead.'},
    {'id': 'C-RES-ASSET-1',
     'name': 'Every mesh/texture/fx/sound path resolves',
     'asserts': 'Every .msh/.tex/.anm/.pfx/.wav/.mp3/.ssh/.fnt/.ttf path resolves inside a '
                'shipped resource .arc or a base-game .arc via the archive-name convention '
                '(first path component = archive; XPack two-level; Audio/ folder), with a '
                'basename fallback for the DRX bare-name mesh convention.',
     'derived_from': '19,748/22,869 refs resolve by full archive path + 170 by basename on the '
                     'build27 baseline; residue (e.g. need-art placeholders) exists in no arc.'},
    {'id': 'C-RES-TAG-1',
     'name': 'Every referenced text tag resolves',
     'asserts': 'Every tag token referenced by an .arz record field, a Quests.arc quest file, '
                'or a world-map SD zone name is defined in the mod Text.arc UNION the base '
                'Text_EN.arc (else it renders as a raw tag string in-game).',
     'derived_from': 'B-TEXT-TAGS-1 (8 Crimson-Verdict tags rendered raw) + B-SUPRA-NOTIFY-1 '
                     '(placeholder tagLOCATIONTAGTESTER) + the tagMZone*/SD zone-name class.'},
    {'id': 'C-RES-TAGDUP-1',
     'name': 'No text tag is defined twice with conflicting values',
     'asserts': 'No key in the mod modstrings.txt is defined more than once with two different '
                'values (the engine keeps the FIRST, silently dropping the intended one).',
     'derived_from': 'B-MASTERY-LABEL-1: tagSkillName050/tagMasteryBrief05/tagMasteryTitle05 '
                     'defined as both Occult and Rogue -> the mastery select screen showed Rogue.'},
    {'id': 'C-RES-TAGDEAD-1',
     'name': 'Every mod-authored content tag is referenced',
     'asserts': 'Every mod-authored CONTENT tag (soul / summon / set / boss name+desc prefixes) '
                'defined in the mod Text.arc is referenced by some shipped record, quest, or map '
                '(else it is an orphaned string from a since-removed entity).',
     'derived_from': 'Orphaned soul name-tags (tagSoulSVC9005/9006) were a recurring class; '
                     'scoped to authored content prefixes to stay false-positive-free.'},
    {'id': 'C-RES-TPL-1',
     'name': 'Every templateName resolves in the toolset',
     'asserts': 'Every record templateName (database\\Templates\\*.tpl) resolves in '
                'Toolset/Templates.arc (editor/toolset completeness; runtime-tolerant -> P2).',
     'derived_from': '50,353/50,353 records carry templateName; 566 base templates; 15 custom '
                     '*2/*3.tpl DRX/SV templates are absent from the base toolset.'},
]


# ============================================================================
# LIGHT ARC TABLE-OF-CONTENTS READER (filenames only; never loads data blocks)
# ============================================================================
def _arc_entry_names(path):
    """Return the list of file-entry names in an .arc, reading ONLY the header + string
    table + record table (not the multi-hundred-MB data blocks). Fast on huge arcs."""
    try:
        with open(path, 'rb') as f:
            header = f.read(28)
            if header[0:4] != b'ARC\x00':
                return []
            num_entries = struct.unpack_from('<I', header, 8)[0]
            toc_size = struct.unpack_from('<I', header, 0x10)[0]
            string_size = struct.unpack_from('<I', header, 0x14)[0]
            toc_offset = struct.unpack_from('<I', header, 0x18)[0]
            string_start = toc_offset + toc_size
            f.seek(string_start)
            stab = f.read(string_size)
            f.seek(string_start + string_size)
            recs = f.read(num_entries * 44)
    except (OSError, struct.error):
        return []
    names = []
    for i in range(num_entries):
        rp = i * 44
        if rp + 44 > len(recs):
            break
        etype = struct.unpack_from('<I', recs, rp)[0]
        str_off = struct.unpack_from('<I', recs, rp + 40)[0]
        nul = stab.find(b'\x00', str_off)
        nm = stab[str_off:nul].decode('utf-8', 'replace') if nul >= 0 else ''
        if etype == 3 and nm:
            names.append(nm)
    return names


# ============================================================================
# CACHE (stable base-game / upstream indexes are cached as JSON; keyed by a
# size+mtime signature so a changed input auto-invalidates. The mod .arz itself
# is never cached - it is the artifact under test.)
# ============================================================================
def _sig(*paths):
    parts = []
    for p in paths:
        try:
            st = os.stat(p)
            parts.append(f"{p}:{st.st_size}:{int(st.st_mtime)}")
        except OSError:
            parts.append(f"{p}:missing")
    return "|".join(parts)


def _cache_dir(cfg):
    d = cfg.get('cache_dir') if isinstance(cfg, dict) else None
    if not d:
        d = os.path.join(tempfile.gettempdir(), 'svc_contracts_cache_resources')
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        return None
    return d


def _cache_load(cdir, name, sig):
    if not cdir:
        return None
    p = os.path.join(cdir, name)
    try:
        with open(p, 'r', encoding='utf-8') as f:
            blob = json.load(f)
        if blob.get('sig') == sig:
            return blob.get('data')
    except (OSError, ValueError):
        return None
    return None


def _cache_store(cdir, name, sig, data):
    if not cdir:
        return
    try:
        with open(os.path.join(cdir, name), 'w', encoding='utf-8') as f:
            json.dump({'sig': sig, 'data': data}, f)
    except OSError:
        pass


# ============================================================================
# ARC RESOURCE INDEX (reconstructed full lowercase paths + basenames + templates)
# ============================================================================
def _iter_arc_files(base_game_dir, resource_arc_dir):
    """Yield (kind, folder_prefix, arc_path) for every arc that ships at runtime.
    kind='top' -> reconstruct <arcbase>/<entry>; kind='xpack' -> <folder>/<arcbase>/<entry>;
    kind='tpl' -> the toolset templates arc."""
    base = Path(base_game_dir) if base_game_dir else None
    # Mod resource arcs (override/add) + base Resources + base Audio (sounds live here).
    top_roots = []
    if resource_arc_dir:
        top_roots.append(Path(resource_arc_dir))
    if base:
        top_roots += [base / 'Resources', base / 'Audio']
    for root in top_roots:
        if root and root.is_dir():
            for arc in sorted(root.glob('*.arc')):
                yield ('top', None, arc)
    # Expansion arcs: XPack{,2,3,4} under both the mod resource dir and the base game.
    xp_roots = []
    if resource_arc_dir:
        xp_roots += [d for d in Path(resource_arc_dir).glob('XPack*') if d.is_dir()]
    if base:
        xp_roots += [d for d in (base / 'Resources').glob('XPack*') if d.is_dir()]
    for root in xp_roots:
        for arc in sorted(root.glob('*.arc')):
            yield ('xpack', root.name.lower(), arc)
    # Toolset templates.
    if base:
        tpl = base / 'Toolset' / 'Templates.arc'
        if tpl.is_file():
            yield ('tpl', None, tpl)


def build_arc_index(cfg):
    """Return (res_paths, basenames, tpl_entries). res_paths = set of reconstructed
    lowercase archive paths; basenames = set of entry leaf names; tpl_entries = set of
    lowercase template entry paths (rooted at 'templates/'). Cached by input signature."""
    base_game_dir = cfg.get('base_game_dir')
    resource_arc_dir = cfg.get('resource_arc_dir')
    arc_paths = [str(p) for (_, __, p) in _iter_arc_files(base_game_dir, resource_arc_dir)]
    sig = _sig(*arc_paths)
    cdir = _cache_dir(cfg)
    cached = _cache_load(cdir, 'arc_index.json', sig)
    if cached is not None:
        return (set(cached['res']), set(cached['base']), set(cached['tpl']))

    res_paths, basenames, tpl_entries = set(), set(), set()
    for kind, folder, arc in _iter_arc_files(base_game_dir, resource_arc_dir):
        ab = arc.stem.lower()
        for e in _arc_entry_names(arc):
            el = e.lower().replace('\\', '/')
            if kind == 'tpl':
                tpl_entries.add(el)
                continue
            if kind == 'xpack':
                res_paths.add(f"{folder}/{ab}/{el}")
            else:
                res_paths.add(f"{ab}/{el}")
            basenames.add(el.rsplit('/', 1)[-1])
    _cache_store(cdir, 'arc_index.json', sig,
                 {'res': sorted(res_paths), 'base': sorted(basenames), 'tpl': sorted(tpl_entries)})
    return res_paths, basenames, tpl_entries


# ============================================================================
# TAG UNIVERSE (mod modstrings + base Text_EN) and duplicate detection
# ============================================================================
def _parse_kv(text):
    """Yield (key, value) for each 'key=value' line (skip blanks / // comments)."""
    for line in text.split('\n'):
        line = line.strip('\r').strip()
        if not line or line.startswith('//'):
            continue
        if '=' in line:
            k, _, v = line.partition('=')
            yield k.strip(), v.strip()


def _arc_text_files(arc_path):
    """Yield (name, text) for every .txt entry in an arc (small text arcs only)."""
    try:
        arc = ArcArchive.from_file(Path(arc_path))
    except Exception:
        return
    for e in arc.entries:
        if e.entry_type == 3 and e.name.lower().endswith('.txt'):
            t = arc.get_text(e.name)
            if t is not None:
                yield e.name, t


def load_mod_tags(text_arc):
    """Return (defined_keys:set, conflicting:dict[key->set(values)]) from the mod Text.arc."""
    kv = []
    for _, txt in _arc_text_files(text_arc):
        kv.extend(_parse_kv(txt))
    keys = set(k for k, v in kv)
    byk = defaultdict(set)
    for k, v in kv:
        byk[k].add(v)
    conflicting = {k: vs for k, vs in byk.items() if len(vs) > 1}
    return keys, conflicting


def load_base_tags(cfg):
    """Return the set of tag keys defined by the base game Text_EN.arc (cached)."""
    base = cfg.get('base_game_dir')
    if not base:
        return set()
    bt = Path(base) / 'Text' / 'Text_EN.arc'
    if not bt.is_file():
        return set()
    sig = _sig(str(bt))
    cdir = _cache_dir(cfg)
    cached = _cache_load(cdir, 'base_tags.json', sig)
    if cached is not None:
        return set(cached)
    keys = set()
    for _, txt in _arc_text_files(bt):
        for k, v in _parse_kv(txt):
            keys.add(k)
    _cache_store(cdir, 'base_tags.json', sig, sorted(keys))
    return keys


def load_mod_manifest(cfg):
    """Return the mod-authored tag set from mod_authored_tags.txt (next to Text.arc or in
    the resource dir), or None if absent."""
    cands = []
    if cfg.get('text_arc'):
        cands.append(Path(cfg['text_arc']).parent / 'mod_authored_tags.txt')
    if cfg.get('resource_arc_dir'):
        cands.append(Path(cfg['resource_arc_dir']) / 'mod_authored_tags.txt')
    for p in cands:
        if p.is_file():
            keys = set()
            for line in p.read_text(encoding='utf-8').split('\n'):
                line = line.strip('\r').strip()
                if not line or line.startswith('//'):
                    continue
                key = line.partition('=')[0].strip() if '=' in line else line
                if key:
                    keys.add(key)
            return keys
    return None


# ============================================================================
# RECORD-NAME SETS (mod / base / upstream) for .dbr resolution + provenance
# ============================================================================
def _load_names(arz_path):
    """Load ONLY record names (lowercased, forward-slash) from an .arz - no field decode."""
    db = ArzDatabase.from_arz(Path(arz_path))
    return set(n.lower().replace('\\', '/') for n in db.record_names())


def load_base_names(cfg):
    base = cfg.get('base_game_dir')
    if not base:
        return set()
    p = Path(base) / 'Database' / 'database.arz'
    if not p.is_file():
        return set()
    sig = _sig(str(p))
    cdir = _cache_dir(cfg)
    cached = _cache_load(cdir, 'base_names.json', sig)
    if cached is not None:
        return set(cached)
    names = _load_names(p)
    _cache_store(cdir, 'base_names.json', sig, sorted(names))
    return names


def load_upstream_names(cfg):
    up = cfg.get('upstream_dir')
    if not up:
        return set()
    for cand in (Path(up) / 'soulvizier_098i' / 'Database' / 'database.arz',
                 Path(up) / 'Database' / 'database.arz'):
        if cand.is_file():
            sig = _sig(str(cand))
            cdir = _cache_dir(cfg)
            cached = _cache_load(cdir, 'upstream_names.json', sig)
            if cached is not None:
                return set(cached)
            names = _load_names(cand)
            _cache_store(cdir, 'upstream_names.json', sig, sorted(names))
            return names
    return set()


# ============================================================================
# QUEST-FILE and MAP-SD tag references
# ============================================================================
def quest_tag_refs(quests_arc):
    """Return {tag: set(quest_file_names)} for tag tokens embedded in every quest file."""
    out = defaultdict(set)
    if not quests_arc or not Path(quests_arc).is_file():
        return out
    try:
        arc = ArcArchive.from_file(Path(quests_arc))
    except Exception:
        return out
    for e in arc.entries:
        if e.entry_type != 3 or not e.name.lower().endswith('.qst'):
            continue
        try:
            data = arc.decompress(e)
        except Exception:
            continue
        for m in _TAG_SCAN_RE.findall(data):
            out[m.decode('latin-1')].add(e.name)
    return out


def sd_zone_tags(cfg):
    """Return the set of tag tokens embedded in the world map SD (0x18) section (zone /
    region / POI display names). Cached by map signature; guarded (best-effort)."""
    lv = cfg.get('levels_arc')
    if not lv or not Path(lv).is_file():
        return set(), "levels_arc not provided or missing"
    sig = _sig(str(lv))
    cdir = _cache_dir(cfg)
    cached = _cache_load(cdir, 'sd_zone_tags.json', sig)
    if cached is not None:
        return set(cached), None
    try:
        arc = ArcArchive.from_file(Path(lv))
        worlds = [e for e in arc.entries if e.entry_type == 3 and e.name.lower().endswith('.map')]
        if not worlds:
            return set(), "no .map entry in levels_arc"
        world = next((e for e in worlds if 'world01' in e.name.lower()), worlds[0])
        data = arc.decompress(world)
        # section walk: [8-byte prefix][ (u32 type, u32 size, size bytes) ... ]
        pos, tags = 8, set()
        n = len(data)
        while pos + 8 <= n:
            st = struct.unpack_from('<I', data, pos)[0]
            ss = struct.unpack_from('<I', data, pos + 4)[0]
            if ss > n - pos - 8:
                break
            if st == _SEC_SD:
                seg = data[pos + 8:pos + 8 + ss]
                for m in _TAG_SCAN_RE.findall(seg):
                    tags.add(m.decode('latin-1'))
            pos += 8 + ss
        _cache_store(cdir, 'sd_zone_tags.json', sig, sorted(tags))
        return tags, None
    except Exception as exc:  # pragma: no cover - degrade gracefully, never false-positive
        return set(), f"SD parse failed ({type(exc).__name__}: {exc})"


# ============================================================================
# ARZ SINGLE-PASS REFERENCE SCAN
# ============================================================================
def scan_arz_refs(arz_path):
    """Single decode pass over the mod .arz. Returns a dict of reference maps:
       subjects: set of lowercased record names
       dbr:  {target_low: {subject_orig: [field,...]}}
       asset:{ref_low:   {subject_orig: [field,...]}}
       tpl:  {tpl_low:    {subject_orig: [field,...]}}
       tag:  {tag:        {subject_orig: [field,...]}}
    Subjects are kept in their original (backslash) form for readable output."""
    db = ArzDatabase.from_arz(Path(arz_path))
    subjects = set()
    dbr = defaultdict(lambda: defaultdict(list))
    asset = defaultdict(lambda: defaultdict(list))
    tpl = defaultdict(lambda: defaultdict(list))
    tag = defaultdict(lambda: defaultdict(list))
    for orig in db.record_names():
        subjects.add(orig.lower().replace('\\', '/'))
        fields = db.get_fields(orig)
        if not fields:
            continue
        for key, tf in fields.items():
            if tf.dtype != DATA_TYPE_STRING:
                continue
            fn = key.split('###')[0]
            for v in tf.values:
                if not isinstance(v, str) or not v:
                    continue
                vs = v.strip()
                if _TAG_TOKEN_RE.match(vs):
                    tag[vs][orig].append(fn)
                    continue
                low = vs.lower().replace('\\', '/')
                leaf = low.rsplit('/', 1)[-1]
                if '.' not in leaf:
                    continue
                ext = leaf.rsplit('.', 1)[-1]
                if ext == 'dbr':
                    dbr[low][orig].append(fn)
                elif ext == 'tpl':
                    tpl[low][orig].append(fn)
                elif ext in RES_EXT:
                    if low.split('/', 1)[0] == 'source' or ext in SOURCE_EXT:
                        continue  # ArtManager source input, not a shipped runtime resource
                    if fn in ASSET_SKIP_FIELDS:
                        continue  # free-text/name/tag field, not a resource-loading path
                    asset[low][orig].append(fn)
    scan_arz_refs.last_record_count = len(subjects)
    return {'subjects': subjects, 'dbr': dbr, 'asset': asset, 'tpl': tpl, 'tag': tag}


# ============================================================================
# PROVENANCE / SEVERITY
# ============================================================================
def make_provenance(up_names, base_names):
    def prov(subject_orig):
        low = subject_orig.lower().replace('\\', '/')
        if 'drx' in low:
            return 'drx'
        if any(tok in low for tok in AUTHORED_TOKENS):
            return 'authored'
        if low in up_names:
            return 'sv'
        if low in base_names:
            return 'base'
        return 'authored'   # present in neither upstream nor base => a mod invention
    return prov


def _sev_for_prov(p):
    return 'P1' if p == 'authored' else 'P2'


# ============================================================================
# RESOLVERS
# ============================================================================
def make_asset_resolver(res_paths, basenames):
    def resolve(ref_low):
        if ref_low in res_paths:
            return True
        return ref_low.rsplit('/', 1)[-1] in basenames
    return resolve


def make_tag_owner(manifest, base_tags):
    def owned(tag):
        if manifest is not None:
            if tag in manifest:
                return True
        if tag.startswith(MOD_TAG_PREFIXES):
            return True
        return False
    return owned


# ============================================================================
# CONTRACT EVALUATION
# ============================================================================
def _fmt_refs(field_map, cap=5):
    """Compact 'field->N recs' style evidence for a single missing target."""
    items = []
    for subj, flds in list(field_map.items())[:cap]:
        items.append(f"{subj} [{','.join(sorted(set(flds)))}]")
    extra = len(field_map) - cap
    if extra > 0:
        items.append(f"(+{extra} more record(s))")
    return "; ".join(items)


def evaluate(cfg, notes):
    refs = scan_arz_refs(cfg['arz'])
    mod_names = refs['subjects']
    base_names = load_base_names(cfg)
    up_names = load_upstream_names(cfg)
    all_names = mod_names | base_names
    prov = make_provenance(up_names, base_names)
    res_paths, basenames, tpl_entries = build_arc_index(cfg)
    resolve_asset = make_asset_resolver(res_paths, basenames)
    mod_tags, conflicting = load_mod_tags(cfg['text_arc']) if cfg.get('text_arc') else (set(), {})
    base_tags = load_base_tags(cfg)
    all_tags = mod_tags | base_tags
    manifest = load_mod_manifest(cfg)
    tag_owned = make_tag_owner(manifest, base_tags)

    if not base_names:
        notes.append("base game DB not loaded (base_game_dir missing) - .dbr resolution is "
                     "mod-arz-only and WILL over-report; provide base_game_dir.")
    if not res_paths:
        notes.append("resource arc index empty - asset resolution skipped.")
    if not all_tags:
        notes.append("no text tags loaded (text_arc/base_game_dir missing) - tag checks limited.")

    out = []

    # ---- C-RES-DBR-1: every .dbr reference resolves in mod UNION base -----------
    # Aggregate per referencing subject: list its dangling targets.
    dbr_by_subject = defaultdict(dict)   # subject_orig -> {target: [fields]}
    for target, field_map in refs['dbr'].items():
        if target in all_names:
            continue
        for subj, flds in field_map.items():
            dbr_by_subject[subj][target] = flds
    for subj, targets in dbr_by_subject.items():
        p = prov(subj)
        sample = sorted(targets)[:4]
        ev = "; ".join(f"{t} <-[{','.join(sorted(set(targets[t])))}]" for t in sample)
        if len(targets) > 4:
            ev += f"; (+{len(targets) - 4} more)"
        out.append({'contract': 'C-RES-DBR-1', 'severity': _sev_for_prov(p),
                    'subject': subj,
                    'message': f"{len(targets)} unresolved .dbr reference(s) ({p})",
                    'evidence': ev})

    # ---- C-RES-ASSET-1: every mesh/tex/fx/sound path resolves -------------------
    asset_by_subject = defaultdict(dict)
    for ref, field_map in refs['asset'].items():
        if resolve_asset(ref):
            continue
        for subj, flds in field_map.items():
            asset_by_subject[subj][ref] = flds
    for subj, missing in asset_by_subject.items():
        p = prov(subj)
        sample = sorted(missing)[:4]
        ev = "; ".join(f"{r} <-[{','.join(sorted(set(missing[r])))}]" for r in sample)
        if len(missing) > 4:
            ev += f"; (+{len(missing) - 4} more)"
        out.append({'contract': 'C-RES-ASSET-1', 'severity': _sev_for_prov(p),
                    'subject': subj,
                    'message': f"{len(missing)} unresolved resource path(s) ({p})",
                    'evidence': ev})

    # ---- C-RES-TAG-1: every referenced tag resolves (arz + quests + map SD) -----
    # (a) arz record tag refs
    tag_by_subject = defaultdict(dict)   # subject_orig -> {tag: [fields]}
    for t, field_map in refs['tag'].items():
        if t in all_tags:
            continue
        for subj, flds in field_map.items():
            tag_by_subject[subj][t] = flds
    for subj, missing in tag_by_subject.items():
        owned = any(tag_owned(t) for t in missing)
        sev = 'P1' if owned else 'P2'
        sample = sorted(missing)[:6]
        ev = "; ".join(f"{t} [{','.join(sorted(set(missing[t])))}]" for t in sample)
        if len(missing) > 6:
            ev += f"; (+{len(missing) - 6} more)"
        out.append({'contract': 'C-RES-TAG-1', 'severity': sev, 'subject': subj,
                    'message': f"{len(missing)} referenced tag(s) absent from mod+base Text"
                               f"{' (mod-owned)' if owned else ''}",
                    'evidence': ev})
    # (b) quest-file tag refs
    qrefs = quest_tag_refs(cfg.get('quests_arc'))
    q_by_file = defaultdict(set)
    for t, files in qrefs.items():
        if t in all_tags:
            continue
        for fnm in files:
            q_by_file[fnm].add(t)
    for fnm, missing in q_by_file.items():
        owned = any(tag_owned(t) for t in missing)
        sev = 'P1' if owned else 'P2'
        sample = sorted(missing)[:8]
        ev = ", ".join(sample) + (f"; (+{len(missing) - 8} more)" if len(missing) > 8 else "")
        out.append({'contract': 'C-RES-TAG-1', 'severity': sev,
                    'subject': f"quest:{fnm}",
                    'message': f"{len(missing)} tag(s) referenced by quest file absent from Text"
                               f"{' (mod-owned)' if owned else ''}",
                    'evidence': ev})
    # (c) map SD zone-name tag refs
    sd_tags, sd_note = sd_zone_tags(cfg)
    if sd_note:
        notes.append(f"SD zone-tag check: {sd_note}")
    sd_missing = sorted(t for t in sd_tags if t not in all_tags)
    if sd_missing:
        owned_m = [t for t in sd_missing if tag_owned(t)]
        # one violation per missing SD tag keeps the map-location subject precise
        for t in sd_missing:
            owned = tag_owned(t)
            out.append({'contract': 'C-RES-TAG-1', 'severity': 'P1' if owned else 'P2',
                        'subject': f"world01.map:SD:{t}",
                        'message': f"map SD zone/region tag {t} absent from Text"
                                   f"{' (mod-owned)' if owned else ''}",
                        'evidence': f"referenced in world map SD (0x18) section"})

    # ---- C-RES-TAGDUP-1: no conflicting duplicate tag definitions ---------------
    # A display-content tag ('tag'/'xtag' key) with conflicting values is the Occult->Rogue
    # class (visible in-game) -> P1. A non-'tag' engine format-string key (e.g.
    # SkillManaCostReductionModifier: Cooldown vs Recharge) is a cosmetic tooltip-wording
    # collision -> P2 (reported, does not block the gate).
    for key, vals in conflicting.items():
        sv = sorted(vals)
        is_display = key.lower().startswith(('tag', 'xtag'))
        out.append({'contract': 'C-RES-TAGDUP-1', 'severity': 'P1' if is_display else 'P2',
                    'subject': key,
                    'message': f"tag defined {len(vals)}x with conflicting values "
                               f"(engine keeps the first, drops the rest)",
                    'evidence': " | ".join(repr(x)[:60] for x in sv[:3])})

    # ---- C-RES-TAGDEAD-1: mod-authored content tags that are never referenced ---
    # Referenced-tag universe = arz tag refs UNION quest tag refs UNION SD tags.
    referenced = set(refs['tag'].keys()) | set(qrefs.keys()) | set(sd_tags)
    # Content-tag prefixes only (names/descs of authored entities); exclude UI/skill/format.
    CONTENT_PREFIXES = ('tagSoulSVC', 'tagSVCSoul', 'tagSVCSummon', 'tagSVCSet',
                        'tagSVCarm', 'tagSVChlm', 'tagSVCtor', 'tagSVCwpn')
    for key in sorted(mod_tags):
        if not key.startswith(CONTENT_PREFIXES):
            continue
        base_key = key[:-4] if key.endswith('DESC') else key  # a DESC's base may carry the ref
        if key in referenced or (key + 'DESC') in referenced:
            continue
        # A description tag is "referenced" implicitly if its name tag is referenced.
        if key.endswith('DESC') and key[:-4] in referenced:
            continue
        out.append({'contract': 'C-RES-TAGDEAD-1', 'severity': 'P2', 'subject': key,
                    'message': "mod-authored content tag defined in Text.arc but never referenced",
                    'evidence': "no arz/quest/map reference found (orphaned entity string?)"})

    # ---- C-RES-TPL-1: every templateName resolves in the toolset ----------------
    if tpl_entries:
        tpl_by_subject = defaultdict(list)
        for ref, field_map in refs['tpl'].items():
            r = ref[len('database/'):] if ref.startswith('database/') else ref
            if r in tpl_entries:
                continue
            for subj in field_map:
                tpl_by_subject[subj].append(ref)
        for subj, missing in tpl_by_subject.items():
            out.append({'contract': 'C-RES-TPL-1', 'severity': 'P2', 'subject': subj,
                        'message': f"{len(set(missing))} templateName not in toolset "
                                   f"Templates.arc (editor-only; runtime-tolerant)",
                        'evidence': "; ".join(sorted(set(missing))[:3])})
    else:
        notes.append("toolset Templates.arc not loaded - C-RES-TPL-1 skipped.")

    return out


# ============================================================================
# WHITELIST
# ============================================================================
def _norm(s):
    return s.strip().lower().replace('\\', '/')


def _load_whitelist():
    wl = set()
    path = Path(__file__).resolve().parent / 'whitelist_resources.txt'
    if not path.is_file():
        return wl
    for line in path.read_text(encoding='utf-8').split('\n'):
        line = line.split('#', 1)[0].strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            wl.add((parts[0].strip(), _norm(parts[1])))
    return wl


# ============================================================================
# PUBLIC ENTRYPOINT
# ============================================================================
def run(cfg):
    """Run every resource-resolution contract over the artifacts named in cfg."""
    notes = []
    t0 = time.time()
    raw = evaluate(cfg, notes)
    wl = _load_whitelist()
    violations = [x for x in raw if (x['contract'], _norm(x['subject'])) not in wl]
    run.last_notes = notes
    run.last_suppressed = len(raw) - len(violations)
    run.last_record_count = getattr(scan_arz_refs, 'last_record_count', None)
    run.last_seconds = time.time() - t0
    return violations


# ============================================================================
# STANDALONE CLI
# ============================================================================
_CFG_ORDER = ('arz', 'text_arc', 'levels_arc', 'quests_arc',
              'resource_arc_dir', 'base_game_dir', 'upstream_dir')

_BASELINE = Path(r"C:/Users/willi/AppData/Local/Temp/claude/"
                 r"C--Users-willi-repos/55f6c1cb-5e9b-466b-a25d-f3fb1a0c56a8/"
                 r"scratchpad/contracts_baseline")
_DEFAULT_BASE_GAME = r"C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition"
_DEFAULT_UPSTREAM = r"C:/Users/willi/repos/tqit_soulvizier_classic/upstream"


def _cfg_from_argv(argv):
    cfg = {k: None for k in _CFG_ORDER}
    if len(argv) < 2:
        # Self-test default: the frozen build27 scratch baseline.
        cfg.update({
            'arz': str(_BASELINE / 'SoulvizierClassic.arz'),
            'text_arc': str(_BASELINE / 'Text.arc'),
            'levels_arc': str(_BASELINE / 'Levels_merged.arc'),
            'quests_arc': str(_BASELINE / 'Quests.arc'),
            'resource_arc_dir': str(_BASELINE / 'Resources'),
            'base_game_dir': _DEFAULT_BASE_GAME,
            'upstream_dir': _DEFAULT_UPSTREAM,
        })
        return cfg
    for key, val in zip(_CFG_ORDER, argv[1:]):
        cfg[key] = val
    return cfg


def main(argv):
    cfg = _cfg_from_argv(argv)
    if not cfg['arz'] or not Path(cfg['arz']).is_file():
        print(f"ERROR: .arz not found: {cfg['arz']}", file=sys.stderr)
        sys.exit(2)
    violations = run(cfg)
    for v in violations:
        print(json.dumps(v, ensure_ascii=False))
    by_cs = Counter((v['contract'], v['severity']) for v in violations)
    print(f"\n[contracts_resources] records: {getattr(run, 'last_record_count', '?')}; "
          f"violations: {len(violations)}; suppressed: {getattr(run, 'last_suppressed', 0)}; "
          f"{getattr(run, 'last_seconds', 0):.1f}s", file=sys.stderr)
    for (cid, sev), k in sorted(by_cs.items()):
        print(f"   {cid:16s} {sev}  {k:6d}", file=sys.stderr)
    for note in getattr(run, 'last_notes', []):
        print(f"   NOTE: {note}", file=sys.stderr)
    p0p1 = [v for v in violations if v['severity'] in ('P0', 'P1')]
    sys.exit(1 if p0p1 else 0)


if __name__ == '__main__':
    main(sys.argv)
