"""
contracts_summons.py  -  DOMAIN B: SUMMONS, PETS, AND AUTHORED-MONSTER CONTRACTS

Permanent, precedent-derived completeness contracts for the Soulvizier Classic mod.
Every contract asserts that an entity we ship has EACH requirement a functioning
base-game exemplar has. Native base-game precedent (the TQAE database.arz + its
Resource .arc archives) is the ground truth; requirement sets below are quantified
against that precedent in the module docstring of each check and in CONTRACTS[].derived_from.

Scope (see _build_context):
  * SUMMON chain reachable from OUR content: every soul (records\\...\\equipmentring\\soul\\*)
    -> its granted skill (itemSkillName, +1 hop via petSkillName/skillName) -> any skill with
    spawnObjects -> every spawn target (pet/monster).  Plus authored Skill_SpawnPet under the
    soulskills namespace.
  * MONSTER: every Monster-class record present in OUR arz but ABSENT from the base-game arz
    (mod/SV/DRX authored or ported).  This is the derivable "created" set; base monsters we only
    "materially modified" are a documented caveat (would need an SV/base field diff to isolate).

Resolution is against the MERGED runtime view:
  * record refs (records\\...\\*.dbr) resolve if present in OUR arz OR the base-game arz
    (case- and slash-insensitive), because the mod arz overlays the base at load.
  * asset refs (*.msh / *.anm / *.tex) resolve if present in any shipped mod .arc OR any
    base-game .arc; the first path component is the archive name and is stripped (verified:
    'Creatures\\Monster\\Skeleton\\RevenantFire.msh' is stored as 'monster\\skeleton\\revenantfire.msh'
    inside Creatures.arc).  A leading 'Build\\Resources\\' authoring prefix is stripped.

Interface (mandated so five parallel modules compose without shared files):
  run(cfg: dict) -> list[dict]
    cfg = {'arz','text_arc','levels_arc','quests_arc','resource_arc_dir','base_game_dir','upstream_dir'}
    each violation = {'contract','severity','subject','message','evidence'}
  CONTRACTS = [ {'id','name','asserts','derived_from'}, ... ]
  standalone: python contracts_summons.py <arz> [--base <dir>] [--res <dir>] ...
              prints violations as JSON lines, exits 1 if any P0/P1 violation else 0.

Whitelist: tools/contracts/whitelist_summons.txt, one "<CONTRACT-ID> <subject>" per line
(everything after the second token is an ignored comment). Matching lines are suppressed.

New files only; imports tools/arz_patcher.py by path; does NOT edit any shared file.
"""
import sys
import json
import struct
import re
import contextlib
from pathlib import Path

# --- import the repo's arz loader by path (no shared-file edits) ------------------
_TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
from arz_patcher import ArzDatabase  # noqa: E402


# =============================================================================
# Field-name catalogues (used by several contracts)
# =============================================================================
AUTHORED_SUMMON_NAMESPACES = ('\\skills\\soulskills\\',)
SOUL_MARKER = '\\equipmentring\\soul\\'

# skill-reference fields carried by Pet.tpl / Monster.tpl records
_SKILL_SCALAR_FIELDS = (
    'attackSkillName', 'buffSelfSkillName', 'buffSelf2SkillName', 'healSkillName',
    'initialSkillName', 'specialAttackSkillName',
    'specialAttack2SkillName', 'specialAttack3SkillName',
    'specialAttack4SkillName', 'specialAttack5SkillName',
)
_SKILL_NAME_MAX = 32           # skillName1 .. skillName32
_EQUIP_SLOTS = ('Head', 'Torso', 'LowerBody', 'Forearm', 'LeftHand', 'RightHand',
                'Finger1', 'Finger2', 'Misc1', 'Misc2', 'Misc3')
_ARMOR_SLOTS = ('Head', 'Torso', 'LowerBody')      # helmet / chestplate / greaves (the naked-Boneash triad)
_LOOT_ITEM_MAX = 6             # loot<Slot>Item1 .. loot<Slot>Item6
_CONTROLLER_FIELDS = ('controller', 'controllerAggressive', 'controllerDefensive')

# asset extensions resolved against .arc archives (everything else that looks like a
# path is treated as a database record reference)
_ASSET_EXT = ('.msh', '.anm', '.tex')


# =============================================================================
# lightweight .arc filename lister (header + string-table + records only;
# never loads the compressed data block, so 200MB+ texture arcs are cheap)
# =============================================================================
def _arc_filenames(path):
    out = set()
    try:
        with open(path, 'rb') as fh:
            head = fh.read(0x1C)
            if len(head) < 0x1C or head[0:4] != b'ARC\x00':
                return out
            num_entries = struct.unpack_from('<I', head, 8)[0]
            toc_size = struct.unpack_from('<I', head, 0x10)[0]
            string_size = struct.unpack_from('<I', head, 0x14)[0]
            toc_offset = struct.unpack_from('<I', head, 0x18)[0]
            string_start = toc_offset + toc_size
            fh.seek(string_start)
            strtab = fh.read(string_size)
            fh.seek(string_start + string_size)
            recs = fh.read(num_entries * 44)
    except (OSError, struct.error):
        return out
    names_by_off = {}
    pos = 0
    while pos < len(strtab):
        nul = strtab.find(b'\x00', pos)
        if nul < 0:
            break
        nm = strtab[pos:nul].decode('utf-8', 'replace')
        if nm:
            names_by_off[pos] = nm
        pos = nul + 1
    for i in range(num_entries):
        rp = i * 44
        if rp + 44 > len(recs):
            break
        etype = struct.unpack_from('<I', recs, rp)[0]
        soff = struct.unpack_from('<I', recs, rp + 40)[0]
        nm = names_by_off.get(soff)
        if nm and etype == 3:
            out.add(nm.lower().replace('/', '\\'))
    return out


def _norm(p):
    if p is None:
        return ''
    return str(p).strip().strip('"').lower().replace('/', '\\')


# =============================================================================
# Context: everything the checks need, built once from cfg
# =============================================================================
class Ctx:
    def __init__(self):
        self.our = None            # ArzDatabase (mod overlay)
        self.base = None           # ArzDatabase (base game)
        self.our_key = {}          # _norm(name) -> actual key in our arz
        self.base_key = {}         # _norm(name) -> actual key in base arz
        self.records_lc = set()    # merged set of _norm(record names)
        self.assets = set()        # merged set of strip-first-component asset paths
        self.summon_skills = []    # normalized skill record keys reachable from souls
        self.spawn_targets = {}    # normalized target -> set(referencing skills)
        self.pet_targets = set()   # spawn targets whose class is Pet/PetNonScaling
        self.monster_targets = set()   # spawn targets whose class is Monster*
        self.scoped_monsters = []      # Monster-class in our arz, not in base, not dev-junk
        self.monster_tier = {}         # scoped monster key -> 'authored' | 'ported'
        self.proxies = []          # Proxy-class record keys in our arz
        self.authored_monster_by_core = {}   # core token -> [monster keys]

    # ---- field access with overlay semantics (our arz wins, else base) ----
    def fv(self, name, field):
        k = _norm(name)
        akey = self.our_key.get(k)
        if akey is not None:
            v = self.our.get_field_value(akey, field)
            if v is not None:
                return v
            # field truly absent in our copy: do not fall through (our overrides base wholesale)
            return None
        akey = self.base_key.get(k)
        if akey is not None:
            return self.base.get_field_value(akey, field)
        return None

    def class_of(self, name):
        k = _norm(name)
        akey = self.our_key.get(k)
        if akey is not None:
            return self.our._record_types.get(akey, '') or (self.our.get_field_value(akey, 'Class') or '')
        akey = self.base_key.get(k)
        if akey is not None:
            return self.base._record_types.get(akey, '') or (self.base.get_field_value(akey, 'Class') or '')
        return None

    def record_exists(self, ref):
        n = _norm(ref)
        if n.startswith('database\\'):          # ArtManager-authored 'database\\records\\...' prefix
            n = n[len('database\\'):]
        return n in self.records_lc

    def asset_exists(self, ref):
        """Resolve a .msh/.anm/.tex ref against the merged arc index.

        The arc string table stores each file WITHOUT the arc's own directory prefix
        ('Creatures\\Monster\\..' -> 'monster\\..' in Creatures.arc; 'XPack\\Creatures\\Monster\\..'
        -> 'monster\\..' in xpack\\Creatures.arc), so the stored path is a SUFFIX of the reference.
        We try dropping 0..3 leading components (top-level arc = drop 1; subdir arc = drop 2)."""
        a = _norm(ref)
        if not a:
            return False
        if a.startswith('build\\resources\\'):   # ArtManager build-output prefix
            a = a[len('build\\resources\\'):]
        comps = a.split('\\')
        for start in range(0, min(3, len(comps) - 1) + 1):
            if '\\'.join(comps[start:]) in self.assets:
                return True
        return False


def _iter_list(v):
    """Field values are scalar or list; yield non-empty string entries."""
    if v is None:
        return
    if isinstance(v, list):
        for x in v:
            if isinstance(x, str) and x.strip():
                yield x
    elif isinstance(v, str):
        if v.strip():
            yield v


# A ref that the modder deliberately DISABLED: TQ never resolves a path that begins with x+'records\\'
# (the 'xrecords\\..' / 'xxxRecords\\..' convention = commented-out slot) or a *placeholder* record.
# These are intentional empty slots, not broken references, so they must NOT be flagged.
_DISABLED_RE = re.compile(r'^x+records\\', re.I)


def _is_disabled_ref(n):
    return bool(_DISABLED_RE.match(n)) or 'placeholder' in n


def _iter_refs(v):
    """Yield only entries that are genuine, ACTIVE record references (end in .dbr, not disabled).

    TQ record fields use '0'/''/tag-strings as empty-slot sentinels and 'xxxRecords\\..' /
    '*placeholder*' as deliberately-disabled slots; a real active reference always ends in .dbr
    and is not x-prefixed, so this removes those sentinel/disabled false positives (e.g.
    lootHeadItem1='0' = empty slot; skillName4='xxxRecords\\..' = commented-out skill)."""
    for x in _iter_list(v):
        n = _norm(x)
        # require a full 'records\\..' style path: endswith .dbr, contains a separator, not disabled.
        # bare basenames (no separator) have ambiguous engine resolution -> skipped to avoid FPs.
        if n.endswith('.dbr') and '\\' in n and not _is_disabled_ref(n):
            yield x


def _core_token(basename):
    """boneash_1 -> boneash ; lyialeafsong_18 -> lyialeafsong ; strip tier/level suffix."""
    b = basename.lower()
    if b.endswith('.dbr'):
        b = b[:-4]
    b = re.sub(r'\s*\([^)]*\)\s*$', '', b)          # strip "(conflicted copy ...)"
    b = re.sub(r'_(?:\d+|[nel])$', '', b)            # strip _1 / _30 / _n/_e/_l
    return b.strip()


# dev-only / non-shipped monster namespaces & names (excluded from monster scope entirely)
_DEV_MARKERS = ('conflicted copy', 'modstridende kopi', 'copy of', '\\test\\', '\\test_',
                'test_shadowstalker', '\\zzdev\\', '\\aaadarkrogue\\', '\\aaa', '\\e3 demo',
                '\\dev\\', 'zdev')
# clearly-authored (our) monster namespaces / names -> blocking severity
_AUTHORED_MARKERS = ('\\drxmap\\', 'bloodtoxeus', 'hemorrheus')


def _monster_tier(key):
    """Classify a not-in-base Monster: 'dev' (junk, excluded) | 'authored' (our content, blocking)
    | 'ported' (SV/DRX/XPack inherited, P2 informational)."""
    p = key.lower()
    if any(m in p for m in _DEV_MARKERS):
        return 'dev'
    if any(m in p for m in _AUTHORED_MARKERS):
        return 'authored'
    return 'ported'


def _sev_for_tier(base_sev, tier):
    """Authored monsters keep the base severity; ported (inherited) debt is downgraded to P2."""
    return base_sev if tier == 'authored' else 'P2'


def _monster_core_token(key):
    b = key.split('\\')[-1]
    if b.endswith('.dbr'):
        b = b[:-4]
    b = re.sub(r'\s*\([^)]*\)\s*$', '', b)
    b = re.sub(r'^(?:um_|am_|b_med_|b_|xsq\d+_|x)', '', b.lower())
    b = re.sub(r'_(?:\d+|[nel])$', '', b)
    return b.strip()


def _safe_eval_number(expr):
    """Evaluate a numeric ProxyLimits equation like '110 * 1'; None if it has game variables."""
    if expr is None:
        return None
    s = str(expr).strip()
    if not s:
        return None
    if not re.fullmatch(r'[0-9.\s+\-*/()]+', s):
        return None
    try:
        return float(eval(s, {'__builtins__': {}}, {}))  # noqa: S307 - sanitized above
    except Exception:
        return None


# =============================================================================
def _build_context(cfg):
    ctx = Ctx()
    # the arz loader prints progress to stdout; keep stdout clean for JSON-lines output
    with contextlib.redirect_stdout(sys.stderr):
        ctx.our = ArzDatabase.from_arz(Path(cfg['arz']))
        base_arz = Path(cfg['base_game_dir']) / 'Database' / 'database.arz'
        ctx.base = ArzDatabase.from_arz(base_arz)

    for n in ctx.our.record_names():
        ctx.our_key[_norm(n)] = n
    for n in ctx.base.record_names():
        ctx.base_key[_norm(n)] = n
    ctx.records_lc = set(ctx.our_key.keys()) | set(ctx.base_key.keys())

    # ---- arc asset index (mod arcs + base arcs, recursive) ----
    arc_files = []
    res_dir = Path(cfg['resource_arc_dir'])
    if res_dir.is_dir():
        arc_files += sorted(res_dir.glob('*.arc'))
    base_res = Path(cfg['base_game_dir']) / 'Resources'
    if base_res.is_dir():
        arc_files += sorted(base_res.rglob('*.arc'))
    for p in arc_files:
        ctx.assets |= _arc_filenames(p)

    # ---- monster scope: Monster-class in our arz, absent from base (created/ported) ----
    #      tiered: 'authored' (our blood-cave/named content) -> blocking; 'ported' (SV/DRX/XPack
    #      inherited) -> P2 informational; 'dev' (junk/test/conflicted-copy) -> excluded.
    for k, actual in ctx.our_key.items():
        rt = ctx.our._record_types.get(actual, '')
        if rt == 'Monster' and k not in ctx.base_key:
            tier = _monster_tier(k)
            if tier == 'dev':
                continue
            ctx.scoped_monsters.append(k)
            ctx.monster_tier[k] = tier
            ctx.authored_monster_by_core.setdefault(_monster_core_token(k), []).append(k)
        if rt == 'Proxy':
            ctx.proxies.append(k)

    # ---- summon skills reachable from souls (+ soulskills namespace) ----
    granted = set()
    for k in ctx.our_key:
        if SOUL_MARKER in k:
            sk = ctx.fv(k, 'itemSkillName')
            for one in _iter_list(sk):
                granted.add(_norm(one))
            # one hop: soul-granted skill may delegate to a spawn skill
    # expand one hop through skill-link fields
    hop = set()
    for sk in list(granted):
        if not ctx.record_exists(sk):
            continue
        for link in ('petSkillName', 'skillName', 'buffSkillName', 'modifierSkillName'):
            for one in _iter_list(ctx.fv(sk, link)):
                hop.add(_norm(one))
    candidate_skills = granted | hop
    # add authored Skill_SpawnPet under soulskills namespace
    for k, actual in ctx.our_key.items():
        if any(ns in k for ns in AUTHORED_SUMMON_NAMESPACES):
            cls = ctx.our._record_types.get(actual, '')
            if cls.startswith('Skill_') or cls == 'SkillSecondary_PetSpawn':
                candidate_skills.add(k)

    for sk in candidate_skills:
        if not ctx.record_exists(sk):
            # a soul granting a missing skill is a separate (soul-augment) concern; skip here
            continue
        so = ctx.fv(sk, 'spawnObjects')
        targets = list(_iter_refs(so))   # active .dbr targets only (skip '0'/disabled sentinels)
        if not targets:
            continue
        ctx.summon_skills.append(sk)
        for t in targets:
            tn = _norm(t)
            ctx.spawn_targets.setdefault(tn, set()).add(sk)
            cls = ctx.class_of(tn) or ''
            if cls in ('Pet', 'PetNonScaling'):
                ctx.pet_targets.add(tn)
            elif cls.startswith('Monster') or cls == 'Monster':
                ctx.monster_targets.add(tn)
            elif cls == '' and not ctx.record_exists(tn):
                pass  # missing; reported by SUMMON-SPAWN-RESOLVE
    ctx.summon_skills = sorted(set(ctx.summon_skills))
    return ctx


# =============================================================================
# helper: does a record have working animation capability?
# =============================================================================
def _anim_problem(ctx, key):
    """Return (severity, message, evidence) if the shared animation table is broken, else None.

    Only the PROVABLE failure is flagged: charAnimationTableName is set but resolves to no record
    (guaranteed T-pose / immobile / floating-weapon = the bug-F class).  Records with NO shared
    table are NOT flagged: base-game precedent shows 206/341 pets animate purely from inline anim
    fields, and statically proving an inline anim set is 'complete enough to move' across every
    weapon-stance variant is not reliable (documented caveat)."""
    at = next(_iter_refs(ctx.fv(key, 'charAnimationTableName')), None)
    if at and not ctx.record_exists(at):
        return ('P0', 'charAnimationTableName set but does not resolve (T-pose/immobile)',
                'charAnimationTableName=%s (absent from mod+base arz)' % at)
    return None


def _mesh_problem(ctx, key, require_mesh=True):
    """require_mesh=True for pets (334/341 base pets set a mesh; absent => invisible pet).
    require_mesh=False for monsters (69 base monsters are legitimately meshless fx/proxy
    creatures), so for monsters only a SET-but-UNRESOLVED mesh is a defect."""
    m = next(_iter_list(ctx.fv(key, 'mesh')), None)
    if not m or not _norm(m).endswith('.msh'):
        if require_mesh:
            return ('P1', 'no mesh (invisible unless intentional aura/helper pet)', 'mesh field empty/absent')
        return None
    if not ctx.asset_exists(m):
        return ('P0', 'mesh does not resolve in any shipped or base-game arc (invisible/naked)',
                'mesh=%s' % m)
    return None


# =============================================================================
# CONTRACT CHECKS  (each returns list of violation dicts)
# =============================================================================
def check_summon_spawn_resolve(ctx):
    """Every spawnObjects target of an our-content summon skill resolves in the merged DB."""
    out = []
    for tgt, skills in sorted(ctx.spawn_targets.items()):
        if ctx.record_exists(tgt):
            continue
        skl = sorted(skills)
        soul_reachable = any('\\soulskills\\' in s for s in skl)
        sev = 'P0' if soul_reachable else 'P2'
        out.append(dict(contract='SUMMON-SPAWN-RESOLVE', severity=sev, subject=tgt,
                        message='summon spawnObjects target does not exist in mod+base arz'
                                + ('' if soul_reachable else ' (inherited SV/DRX summon skill; likely dead path)'),
                        evidence='referenced by %s' % (skl[0] if len(skl) == 1 else '%d skills e.g. %s' % (len(skl), skl[0]))))
    return out


def check_summon_pet_mesh(ctx):
    """Every summon spawn target sets a mesh that resolves (base precedent: 334/341 pets)."""
    out = []
    for tgt in sorted(ctx.pet_targets | ctx.monster_targets):
        if not ctx.record_exists(tgt):
            continue
        prob = _mesh_problem(ctx, tgt)
        if prob:
            sev, msg, ev = prob
            out.append(dict(contract='SUMMON-PET-MESH', severity=sev, subject=tgt,
                            message='summon target: ' + msg, evidence=ev))
    return out


def check_summon_pet_anim(ctx):
    """Every summon target that sets a shared charAnimationTableName must have it resolve (a broken
    table ref = T-pose/immobile = the bug-F class). See _anim_problem for why inline-anim pets are
    not flagged (base precedent + non-provable statically)."""
    out = []
    for tgt in sorted(ctx.pet_targets | ctx.monster_targets):
        if not ctx.record_exists(tgt):
            continue
        prob = _anim_problem(ctx, tgt)
        if prob:
            sev, msg, ev = prob
            out.append(dict(contract='SUMMON-PET-ANIM', severity=sev, subject=tgt,
                            message='summon target: ' + msg, evidence=ev))
    return out


def check_summon_pet_controller(ctx):
    """Every Pet-class summon target has a resolving AI controller (base precedent: 341/341)."""
    out = []
    for tgt in sorted(ctx.pet_targets):
        if not ctx.record_exists(tgt):
            continue
        present = []
        unresolved = []
        for f in _CONTROLLER_FIELDS:
            v = next(_iter_refs(ctx.fv(tgt, f)), None)
            if v:
                present.append((f, v))
                if not ctx.record_exists(v):
                    unresolved.append((f, v))
        if not present:
            out.append(dict(contract='SUMMON-PET-CONTROLLER', severity='P1', subject=tgt,
                            message='pet has no AI controller (base pets: 341/341 set one; likely immobile)',
                            evidence='none of %s set' % ','.join(_CONTROLLER_FIELDS)))
        elif len(unresolved) == len(present):
            out.append(dict(contract='SUMMON-PET-CONTROLLER', severity='P1', subject=tgt,
                            message='pet AI controller(s) do not resolve',
                            evidence='; '.join('%s=%s' % (f, v) for f, v in unresolved)))
    return out


def check_summon_pet_classification(ctx):
    """Every Pet-class summon target sets monsterClassification (base precedent: 341/341)."""
    out = []
    for tgt in sorted(ctx.pet_targets):
        if not ctx.record_exists(tgt):
            continue
        v = next(_iter_list(ctx.fv(tgt, 'monsterClassification')), None)
        if not v:
            out.append(dict(contract='SUMMON-PET-CLASSIFICATION', severity='P1', subject=tgt,
                            message='pet has no monsterClassification (base pets: 341/341 set one)',
                            evidence='monsterClassification empty/absent'))
    return out


def _skill_refs(ctx, key):
    refs = []
    for f in _SKILL_SCALAR_FIELDS:
        for v in _iter_refs(ctx.fv(key, f)):
            refs.append((f, v))
    for i in range(1, _SKILL_NAME_MAX + 1):
        f = 'skillName%d' % i
        for v in _iter_refs(ctx.fv(key, f)):
            refs.append((f, v))
    return refs


def check_summon_pet_skills(ctx):
    """Every skill referenced by a Pet-class summon target resolves in the merged DB."""
    out = []
    for tgt in sorted(ctx.pet_targets):
        if not ctx.record_exists(tgt):
            continue
        bad = [(f, v) for (f, v) in _skill_refs(ctx, tgt) if not ctx.record_exists(v)]
        if bad:
            out.append(dict(contract='SUMMON-PET-SKILLS', severity='P1', subject=tgt,
                            message='pet references %d skill(s) that do not resolve' % len(bad),
                            evidence='; '.join('%s=%s' % (f, v) for f, v in bad[:4])))
    return out


def check_summon_pet_equip_resolve(ctx):
    """For every equip slot with chanceToEquip>0, at least one loot<Slot>Item* resolves."""
    out = []
    for tgt in sorted(ctx.pet_targets):
        if not ctx.record_exists(tgt):
            continue
        broken_slots = []
        for slot in _EQUIP_SLOTS:
            ch = ctx.fv(tgt, 'chanceToEquip%s' % slot)
            try:
                chv = float(ch) if ch is not None else 0.0
            except (TypeError, ValueError):
                chv = 0.0
            if chv <= 0.0:
                continue
            has_item = False
            any_ref = False
            for i in range(1, _LOOT_ITEM_MAX + 1):
                for v in _iter_refs(ctx.fv(tgt, 'loot%sItem%d' % (slot, i))):
                    any_ref = True
                    if ctx.record_exists(v):
                        has_item = True
                        break
                if has_item:
                    break
            if not has_item:
                broken_slots.append((slot, chv, any_ref))
        if broken_slots:
            ev = '; '.join('%s(chance=%.0f,%s)' % (s, c, 'refs-unresolved' if r else 'no-item-list')
                           for s, c, r in broken_slots)
            out.append(dict(contract='SUMMON-PET-EQUIP-RESOLVE', severity='P1', subject=tgt,
                            message='pet configured to equip %d slot(s) with no resolving item (empty in that slot)' % len(broken_slots),
                            evidence=ev))
    return out


def check_summon_pet_naked(ctx):
    """Pet vs matched source monster: armor slots the source wears (Head/Torso/LowerBody) but the
    pet leaves at chance 0 => the pet lost its body armor (the naked-Boneash regression class).
    Heuristic source match by core name token; only fires on a UNIQUE authored-monster match."""
    out = []
    for tgt in sorted(ctx.pet_targets):
        if not ctx.record_exists(tgt) or '\\soulskills\\pets\\' not in tgt:
            continue
        core = _core_token(tgt.split('\\')[-1])
        sources = ctx.authored_monster_by_core.get(core, [])
        # also try base-game source by exact core (e.g. um_<core>_NN in base)
        if len(sources) != 1:
            continue
        src = sources[0]
        stripped = []
        for slot in _ARMOR_SLOTS:
            sc = ctx.fv(src, 'chanceToEquip%s' % slot)
            pc = ctx.fv(tgt, 'chanceToEquip%s' % slot)
            try:
                scv = float(sc) if sc is not None else 0.0
            except (TypeError, ValueError):
                scv = 0.0
            try:
                pcv = float(pc) if pc is not None else 0.0
            except (TypeError, ValueError):
                pcv = 0.0
            if scv < 50.0 or pcv > 0.0:
                continue
            # confirm the source actually has a resolving item in that slot
            src_has = any(ctx.record_exists(v)
                          for i in range(1, _LOOT_ITEM_MAX + 1)
                          for v in _iter_refs(ctx.fv(src, 'loot%sItem%d' % (slot, i))))
            if src_has:
                stripped.append(slot)
        if stripped:
            out.append(dict(contract='SUMMON-PET-NAKED', severity='P1', subject=tgt,
                            message='summon pet spawns without body armor its source monster wears (naked-Boneash class)',
                            evidence='source %s equips %s (chance>=50) but pet chance=0 for those slots'
                                     % (src, '+'.join(stripped))))
    return out


# soul-summon archetypes that are TACTICAL/TEMPORARY by design (positive TTL is correct);
# these are excluded from the permanent-pet TTL contract. Kept explicit + whitelistable.
_TEMPORARY_SUMMON_TOKENS = (
    'hydra', 'chimera', 'chimaera', 'hellflower', 'battlestandard', 'standard',
    'iceward', 'bladetrap', 'slamsummon', 'flamesprite', 'hazur', 'tatos',
    'trap', 'wall', 'totem', 'nova', 'mirage', 'sprite',
)


def check_summon_ttl_permanent(ctx):
    """A soul-granted summon that is a permanent companion (Lyia exemplar) must not set a finite
    positive spawnObjectsTimeToLive (it would despawn). Known tactical/temporary archetypes are
    excluded (whitelist-backed)."""
    out = []
    for sk in ctx.summon_skills:
        if '\\soulskills\\' not in sk:
            continue
        ttl = ctx.fv(sk, 'spawnObjectsTimeToLive')
        vals = [float(x) for x in _iter_list_num(ttl)]
        if not vals or all(v <= 0.0 for v in vals):
            continue
        base = sk.split('\\')[-1]
        if any(tok in base for tok in _TEMPORARY_SUMMON_TOKENS):
            continue
        out.append(dict(contract='SUMMON-TTL-PERMANENT', severity='P1', subject=sk,
                        message='soul-granted summon has a positive spawnObjectsTimeToLive; a permanent '
                                'companion pet would despawn (Lyia Leafsong = no-TTL exemplar)',
                        evidence='spawnObjectsTimeToLive=%s' % (vals if len(vals) > 1 else vals[0])))
    return out


def _iter_list_num(v):
    if v is None:
        return
    if isinstance(v, list):
        for x in v:
            try:
                yield float(x)
            except (TypeError, ValueError):
                continue
    else:
        try:
            yield float(v)
        except (TypeError, ValueError):
            return


# ---- MONSTER contracts (monsters in our arz, not in base; tiered authored/ported) ----------
def _monster_scope(ctx):
    # exclude records already covered as summon targets (avoid double-report)
    return [m for m in ctx.scoped_monsters if m not in ctx.pet_targets and m not in ctx.monster_targets]


def check_monster_mesh(ctx):
    out = []
    for m in _monster_scope(ctx):
        prob = _mesh_problem(ctx, m, require_mesh=False)
        if prob:
            sev, msg, ev = prob
            tier = ctx.monster_tier.get(m, 'ported')
            out.append(dict(contract='MONSTER-MESH', severity=_sev_for_tier(sev, tier), subject=m,
                            message='%s monster: %s' % (tier, msg), evidence=ev))
    return out


def check_monster_anim(ctx):
    out = []
    for m in _monster_scope(ctx):
        prob = _anim_problem(ctx, m)
        if prob:
            sev, msg, ev = prob
            tier = ctx.monster_tier.get(m, 'ported')
            out.append(dict(contract='MONSTER-ANIM', severity=_sev_for_tier(sev, tier), subject=m,
                            message='%s monster: %s' % (tier, msg), evidence=ev))
    return out


def _loot_refs(ctx, key):
    refs = []
    for slot in _EQUIP_SLOTS:
        for i in range(1, _LOOT_ITEM_MAX + 1):
            for v in _iter_refs(ctx.fv(key, 'loot%sItem%d' % (slot, i))):
                refs.append(('loot%sItem%d' % (slot, i), v))
    return refs


def check_monster_skills_loot(ctx):
    """Monsters' skill and equipment-loot references resolve in the merged DB."""
    out = []
    for m in _monster_scope(ctx):
        bad_sk = [(f, v) for (f, v) in _skill_refs(ctx, m) if not ctx.record_exists(v)]
        bad_lo = [(f, v) for (f, v) in _loot_refs(ctx, m) if not ctx.record_exists(v)]
        if bad_sk or bad_lo:
            parts = []
            if bad_sk:
                parts.append('%d skill' % len(bad_sk))
            if bad_lo:
                parts.append('%d loot' % len(bad_lo))
            ev_items = (bad_sk + bad_lo)[:4]
            tier = ctx.monster_tier.get(m, 'ported')
            out.append(dict(contract='MONSTER-SKILLS-LOOT', severity=_sev_for_tier('P1', tier), subject=m,
                            message='%s monster has %s reference(s) that do not resolve' % (tier, ' + '.join(parts)),
                            evidence='; '.join('%s=%s' % (f, v) for f, v in ev_items)))
    return out


def check_monster_spawn_eligibility(ctx):
    """For proxies whose pool spawns an authored monster: (a) the difficultyLimitsFile player-level
    bracket must be non-degenerate (min<=max, max>=1) so the encounter can ever spawn; (b) the pool
    must not crowd the named monster out (championChance>=100 with championMin>=spawnMax) -> the
    Toxeus no-spawn bug class."""
    out = []
    scoped_set = set(ctx.scoped_monsters)
    for px in ctx.proxies:
        # collect pool records referenced by this proxy
        pools = [_norm(v) for i in range(1, 9) for v in _iter_refs(ctx.fv(px, 'pool%d' % i))]
        # which scoped (mod) monsters does this proxy spawn?
        spawns = []
        for pool in pools:
            if not ctx.record_exists(pool):
                continue
            for j in range(1, 9):
                for v in _iter_refs(ctx.fv(pool, 'name%d' % j)):
                    if _norm(v) in scoped_set:
                        spawns.append((_norm(v), pool))
        if not spawns:
            continue
        px_tier = _monster_tier(px)     # tier of the proxy itself (drxmap => authored)
        # (a) player-level bracket
        dlf = next(_iter_refs(ctx.fv(px, 'difficultyLimitsFile')), None)
        if not dlf:
            out.append(dict(contract='MONSTER-SPAWN-ELIGIBILITY', severity=_sev_for_tier('P1', px_tier), subject=px,
                            message='proxy spawning a mod monster has no difficultyLimitsFile',
                            evidence='spawns %s' % spawns[0][0]))
        elif not ctx.record_exists(dlf):
            out.append(dict(contract='MONSTER-SPAWN-ELIGIBILITY', severity=_sev_for_tier('P1', px_tier), subject=px,
                            message='proxy difficultyLimitsFile does not resolve',
                            evidence='difficultyLimitsFile=%s' % dlf))
        else:
            for diff in ('Normal', 'Epic', 'Legendary'):
                lo = _safe_eval_number(ctx.fv(dlf, 'minPlayerLevelEquation%s' % diff))
                hi = _safe_eval_number(ctx.fv(dlf, 'maxPlayerLevelEquation%s' % diff))
                if lo is None or hi is None:
                    continue  # game-variable equation: not statically provable (caveat)
                if hi < 1 or hi < lo:
                    out.append(dict(contract='MONSTER-SPAWN-ELIGIBILITY', severity=_sev_for_tier('P1', px_tier), subject=px,
                                    message='proxy player-level bracket is degenerate on %s (never spawns)' % diff,
                                    evidence='%s: min=%.0f max=%.0f (spawns %s)' % (dlf, lo, hi, spawns[0][0])))
                    break
        # (b) champion crowd-out
        seen_pools = set()
        for _mon, pool in spawns:
            if pool in seen_pools:
                continue
            seen_pools.add(pool)
            ccv = _safe_eval_number(ctx.fv(pool, 'championChance')) or 0.0
            cminv = int(_safe_eval_number(ctx.fv(pool, 'championMin')) or 0)
            smaxv = int(_safe_eval_number(ctx.fv(pool, 'spawnMax')) or 0)
            has_named = any(_iter_refs(ctx.fv(pool, 'name%d' % j)) for j in range(1, 9))
            has_champ = any(_iter_refs(ctx.fv(pool, 'nameChampion%d' % j)) for j in range(1, 9))
            if ccv >= 100.0 and has_champ and has_named and smaxv > 0 and cminv >= smaxv:
                out.append(dict(contract='MONSTER-SPAWN-ELIGIBILITY', severity=_sev_for_tier('P1', _monster_tier(pool)), subject=pool,
                                message='pool crowds out its named monster: championChance=100 fills every '
                                        'slot with champions (the Blood-Toxeus no-spawn class)',
                                evidence='championChance=%.0f championMin=%d spawnMax=%d (named=%s)' % (ccv, cminv, smaxv, _mon)))
    return out


# =============================================================================
# CONTRACTS registry
# =============================================================================
_CHECKS = [
    ('SUMMON-SPAWN-RESOLVE', check_summon_spawn_resolve),
    ('SUMMON-PET-MESH', check_summon_pet_mesh),
    ('SUMMON-PET-ANIM', check_summon_pet_anim),
    ('SUMMON-PET-CONTROLLER', check_summon_pet_controller),
    ('SUMMON-PET-CLASSIFICATION', check_summon_pet_classification),
    ('SUMMON-PET-SKILLS', check_summon_pet_skills),
    ('SUMMON-PET-EQUIP-RESOLVE', check_summon_pet_equip_resolve),
    ('SUMMON-PET-NAKED', check_summon_pet_naked),
    ('SUMMON-TTL-PERMANENT', check_summon_ttl_permanent),
    ('MONSTER-MESH', check_monster_mesh),
    ('MONSTER-ANIM', check_monster_anim),
    ('MONSTER-SKILLS-LOOT', check_monster_skills_loot),
    ('MONSTER-SPAWN-ELIGIBILITY', check_monster_spawn_eligibility),
]
# NOTE: a monster-classification contract was designed and then DROPPED: base-game precedent
# refutes it as a universal requirement (1131/5489 = 20.6% of real base combat monsters set no
# monsterClassification, the engine defaulting it). It is retained only for PETS
# (SUMMON-PET-CLASSIFICATION), where base precedent is 341/341.

CONTRACTS = [
    {'id': 'SUMMON-SPAWN-RESOLVE', 'name': 'Summon spawn target exists',
     'asserts': 'every spawnObjects target of an our-content summon skill exists in the merged (mod+base) DB',
     'derived_from': 'base-game summon skills resolve 100% of spawnObjects targets against the base arz'},
    {'id': 'SUMMON-PET-MESH', 'name': 'Summon target has a resolving mesh',
     'asserts': 'every summon target sets mesh and the mesh resolves in a shipped or base .arc',
     'derived_from': '334/341 base-game Pet records set a mesh; all base pet meshes resolve in Creatures/XPack arcs'},
    {'id': 'SUMMON-PET-ANIM', 'name': 'Summon target animation table resolves',
     'asserts': 'if a summon target sets charAnimationTableName it must resolve to a real record (else T-pose/immobile, the bug-F class)',
     'derived_from': 'base pets that use a shared table (135/341) always point at an existing CharAnimationTable record; a broken ref = no animation'},
    {'id': 'SUMMON-PET-CONTROLLER', 'name': 'Pet has an AI controller',
     'asserts': 'every Pet-class summon target sets a resolving controller/controllerAggressive/controllerDefensive',
     'derived_from': '341/341 base-game Pet records set controller'},
    {'id': 'SUMMON-PET-CLASSIFICATION', 'name': 'Pet sets monsterClassification',
     'asserts': 'every Pet-class summon target sets monsterClassification',
     'derived_from': '341/341 base-game Pet records set monsterClassification'},
    {'id': 'SUMMON-PET-SKILLS', 'name': 'Pet skill refs resolve',
     'asserts': 'every attackSkillName/buffSelf*/healSkillName/skillName1..N on a pet resolves in the merged DB',
     'derived_from': 'base pets reference only existing skill records (grant-chain must terminate in real skills)'},
    {'id': 'SUMMON-PET-EQUIP-RESOLVE', 'name': 'Configured equip slots have a resolving item',
     'asserts': 'for each slot with chanceToEquip>0, at least one loot<Slot>Item* resolves to an existing item',
     'derived_from': 'a base creature with chanceToEquip<Slot> > 0 always has a resolving item pool for that slot'},
    {'id': 'SUMMON-PET-NAKED', 'name': 'Summon pet keeps its source armor',
     'asserts': 'armor slots (Head/Torso/LowerBody) the matched source monster equips are not left at chance 0 on the pet',
     'derived_from': 'the source monster (e.g. um_boneash_30) equips helmet/chest/greaves at 100%; a naked pet drops them (Will bug report)'},
    {'id': 'SUMMON-TTL-PERMANENT', 'name': 'Permanent companion has no despawn timer',
     'asserts': 'a soul-granted (soulskills) companion summon does not set a positive spawnObjectsTimeToLive, excluding tactical/temporary archetypes',
     'derived_from': 'Lyia Leafsong (working permanent pet) sets no spawnObjectsTimeToLive; the CLAUDE.md pet lesson mandates removing it for permanent pets'},
    {'id': 'MONSTER-MESH', 'name': 'Mod monster has a resolving mesh',
     'asserts': 'every Monster in our arz but not in base sets a mesh that resolves in an .arc (authored=P0, ported SV/DRX=P2)',
     'derived_from': 'base-game monsters set a resolving mesh; an unresolved mesh = invisible/naked monster'},
    {'id': 'MONSTER-ANIM', 'name': 'Mod monster animation table resolves',
     'asserts': 'if a mod monster sets charAnimationTableName it must resolve (authored=P0, ported=P2)',
     'derived_from': 'base-game monsters point at an existing CharAnimationTable; a broken ref = immobile monster'},
    {'id': 'MONSTER-SKILLS-LOOT', 'name': 'Mod monster skill+loot refs resolve',
     'asserts': 'every skillName*/attackSkill*/specialAttack* and loot<Slot>Item* on an authored monster resolves',
     'derived_from': 'base-game monsters reference only existing skill and loottable records'},
    {'id': 'MONSTER-SPAWN-ELIGIBILITY', 'name': 'Authored monster can actually spawn',
     'asserts': 'proxies spawning authored monsters have a non-degenerate player-level bracket and do not crowd the named monster out with 100% champions',
     'derived_from': 'the Blood-Toxeus no-spawn bug: championChance=100 with 1 slot replaced the boss; ProxyLimits gates by player level (min<=max, max>=1)'},
]


# =============================================================================
# whitelist
# =============================================================================
def _load_whitelist():
    wl = set()
    p = Path(__file__).resolve().parent / 'whitelist_summons.txt'
    if p.is_file():
        for line in p.read_text(encoding='utf-8', errors='replace').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            toks = line.split(None, 1)
            if len(toks) >= 2:
                cid = toks[0]
                subj = toks[1].split('#', 1)[0].strip()
                wl.add((cid, _norm(subj)))
            else:
                wl.add((toks[0], None))
    return wl


# =============================================================================
# public entry point
# =============================================================================
def run(cfg):
    ctx = _build_context(cfg)
    wl = _load_whitelist()
    viols = []
    for cid, fn in _CHECKS:
        for v in fn(ctx):
            key = (v['contract'], _norm(v['subject']))
            if key in wl or (v['contract'], None) in wl:
                continue
            viols.append(v)
    sev_rank = {'P0': 0, 'P1': 1, 'P2': 2}
    viols.sort(key=lambda x: (sev_rank.get(x['severity'], 9), x['contract'], x['subject']))
    return viols


def _default_cfg(arz, base_game_dir=None, res_dir=None):
    base = base_game_dir or r'C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition'
    here = Path(arz).resolve().parent
    res = res_dir or str((here / 'Resources'))
    return {
        'arz': arz,
        'text_arc': str(here / 'Text.arc'),
        'levels_arc': str(here / 'Levels_merged.arc'),
        'quests_arc': str(here / 'Quests.arc'),
        'resource_arc_dir': res,
        'base_game_dir': base,
        'upstream_dir': '',
    }


def main(argv):
    if not argv:
        print('usage: contracts_summons.py <arz> [--base <TQAE dir>] [--res <resource arc dir>]',
              file=sys.stderr)
        return 2
    arz = argv[0]
    base = None
    res = None
    i = 1
    while i < len(argv):
        if argv[i] == '--base' and i + 1 < len(argv):
            base = argv[i + 1]; i += 2
        elif argv[i] == '--res' and i + 1 < len(argv):
            res = argv[i + 1]; i += 2
        else:
            i += 1
    cfg = _default_cfg(arz, base, res)
    viols = run(cfg)
    for v in viols:
        print(json.dumps(v, ensure_ascii=False))
    n_block = sum(1 for v in viols if v['severity'] in ('P0', 'P1'))
    print('# %d violations (%d P0/P1, %d P2)' % (len(viols), n_block, len(viols) - n_block),
          file=sys.stderr)
    return 1 if n_block else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
