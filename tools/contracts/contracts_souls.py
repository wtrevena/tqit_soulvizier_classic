r"""PERMANENT CONTRACT SUITE - DOMAIN A: SOULS AND GRANTED-SKILL CONTRACTS.

This module asserts, over the mod's SHIPPED artifacts, that every soul-ring record
(and its granted-skill chain) carries EACH AND EVERY requirement that a functioning
example carries in the base game / SV upstream. It exists because the mod keeps
shipping souls that LOOK complete in a tooltip but are dead in-game: granted skills
whose tooltip renders but never proc (219 souls shipped in build27 were missing
itemSkillLevel), augments that do nothing, names that render as raw tags.

METHOD (every contract): the requirement is DERIVED from native precedent (quantified
below), implemented as a check over our own artifacts, negative-tested (see
tools/contracts/tests_souls_negative.py, which breaks a compliant record and proves the
contract fires), and run over the frozen build27 baseline. Precedent was measured
2026-07-08 from:
  - TQAE base game   database.arz  (74,013 records)
  - SV 0.98i upstream database.arz  (51,186 records)

PRECEDENT (ground truth, measured):
  * itemSkillLevel: 876/876 (100%) of base-game granted-skill items set itemSkillLevel,
    all >= 1; SV 0.98i 1837/1837 present, 1831 >= 1. => a granted item skill MUST carry
    itemSkillLevel >= 1 or it instantiates at level 0 = inactive (the Crommyonian-Sow /
    B-SOUL-PROC-1 bug, 219 souls).
  * granted-skill Class: base grants only records whose Class starts with "Skill_"
    (876/876). The set of Classes ever granted via itemSkillName (base UNION SV) = the
    53-member GRANTABLE_SET below (the "usable-when-item-cast" signal).
  * itemSkillAutoController: 228/228 base (606/606 SV) controllers used by granted items
    have templateName == database\templates\skillautocastcontroller.tpl, chanceToRun > 0,
    and a non-empty triggerType drawn from exactly 7 values (BASE_TRIGGER_TYPES). No
    base/SV granted controller uses any other triggerType.
  * augmentSkillLevelN: base 584/584 (slot1) + 181/181 (slot2) and SV 1445/1445 + 687/687
    granted augments carry a companion level >= 1; augment skills' Class is Skill_* or
    SkillSecondary_*.
  * itemSkillLevel <= skillMaxLevel is NOT asserted: the base game itself has 26
    granted items with itemSkillLevel > the skill's skillMaxLevel (item-grants
    legitimately exceed the player-investable cap), so an upper bound would be
    false-positive against native precedent. See caveats.
  * Soul name tags: 2000/2000 real souls' itemNameTag resolves in (base Text_EN.arc UNION
    mod Text.arc); 1997/2000 name strings begin with the {^F} pink color prefix (the soul
    convention; the 3 exceptions are the "Any Soul" filler item).
  * Soul level-only design law: 2095/2095 real souls have strength/dexterity/intelligence
    requirement == 0 (souls gate on levelRequirement only; no stat requirements).
  * Soul-drop classification: only Hero/Boss/Quest creatures may carry a live soul drop
    (mirrors the shipped wire_souls_to_monsters / _verify_no_unclassified_soul_leaks gate).
  * itemCostName: universal on our souls (2191/2191, all resolving); optional in the base
    game (76/330 rings) so the contract only requires it to RESOLVE when present.
  * bitmap: 2191/2191 soul icons resolve into SVItems.arc.

INTERFACE (composes with the other four domain modules without shared files):
  run(cfg: dict) -> list[dict]
    cfg keys: arz, text_arc, levels_arc, quests_arc, resource_arc_dir, base_game_dir,
              upstream_dir   (souls uses arz, text_arc, resource_arc_dir, base_game_dir)
    each violation: {'contract','severity','subject','message','evidence'}
  CONTRACTS: list of {'id','name','asserts','derived_from'}

WHITELIST: tools/contracts/whitelist_souls.txt - lines "<CONTRACT-ID> <subject>" suppress
that exact (contract, subject) pair (KNOWN-INTENTIONAL deviations, documented inline).

STANDALONE:
  python tools/contracts/contracts_souls.py <arz> [text_arc] [levels_arc] [quests_arc]
        [resource_arc_dir] [base_game_dir] [upstream_dir]
  prints one JSON violation per line; exits 1 if any P0/P1 survives the whitelist, else 0.
"""
import sys
import os
import json
import contextlib
from pathlib import Path

# ----------------------------------------------------------------------------
# Self-contained loader access: import the repo's stable, battle-tested .arz /
# .arc readers BY PATH (never editing them). tools/ is this file's grandparent
# (tools/contracts/contracts_souls.py), located relative to __file__ so the
# module runs standalone from any working directory.
# ----------------------------------------------------------------------------
_TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
from arz_patcher import ArzDatabase          # noqa: E402
from arc_patcher import ArcArchive           # noqa: E402


# ============================================================================
# DERIVED CONSTANTS (see module docstring PRECEDENT for the measured provenance)
# ============================================================================
SOUL_RING_MARK = 'equipmentring\\soul\\'   # a soul ring lives under this path
SOUL_PATH_MARKERS = ('\\soul\\', '/soul/')

# A soul-ring record: Class == ArmorJewelry_Ring and path under equipmentring\soul\.
SOUL_RING_CLASS = 'ArmorJewelry_Ring'
# Clone-base skeletons that ship in the .arz but are never dropped/equipped. Excluded
# from every soul contract (they carry placeholder tags / no granted level by design).
TEMPLATE_BASENAME = 'soultemplate'

# Granted-skill activation chain (B-SOUL-PROC-1) --------------------------------
CTRL_TEMPLATE = 'database\\templates\\skillautocastcontroller.tpl'
# The ONLY triggerType values any base-game (228) or SV (606) granted controller uses.
BASE_TRIGGER_TYPES = frozenset({
    'AttackEnemy', 'HitByEnemy', 'HitByMelee', 'LowHealth',
    'OnEquip', 'HitByProjectile', 'LowMana',
})
SKILL_CLASS_PREFIX = 'Skill_'
AUGMENT_CLASS_PREFIXES = ('Skill_', 'SkillSecondary_')

# The 53 skill Classes the base game (47) UNION SV 0.98i (45) ever grant via an item's
# itemSkillName field - the "usable when auto-cast from an item" signal. A granted skill
# whose Class is outside this set is likely monster-only / unusable as an item proc.
GRANTABLE_SET = frozenset({
    'Skill_AttackBuff', 'Skill_AttackBuffRadius', 'Skill_AttackChain', 'Skill_AttackInherent',
    'Skill_AttackProjectile', 'Skill_AttackProjectileAreaEffect', 'Skill_AttackProjectileBurst',
    'Skill_AttackProjectileDebuf', 'Skill_AttackProjectileFan', 'Skill_AttackProjectileMultiHit',
    'Skill_AttackProjectileRing', 'Skill_AttackProjectileSpawnPet', 'Skill_AttackRadius',
    'Skill_AttackRadiusLightning', 'Skill_AttackSpell', 'Skill_AttackSpellChaos',
    'Skill_AttackSpellTeleportSelf', 'Skill_AttackWave', 'Skill_AttackWeapon',
    'Skill_AttackWeaponBlink', 'Skill_AttackWeaponCharge', 'Skill_AttackWeaponRangedSpread',
    'Skill_BuffAttackRadiusDuration', 'Skill_BuffAttackRadiusToggled', 'Skill_BuffOther',
    'Skill_BuffRadius', 'Skill_BuffRadiusToggled', 'Skill_BuffSelfColossus',
    'Skill_BuffSelfDuration', 'Skill_BuffSelfImmobilize', 'Skill_BuffSelfInvulnerable',
    'Skill_BuffSelfToggled', 'Skill_DefensiveGround', 'Skill_DefensiveProjectileGroundRing',
    'Skill_DefensiveWall', 'Skill_DispelMagic', 'Skill_DropProjectileTelekinesis',
    'Skill_GiveBonus', 'Skill_Modifier', 'Skill_MonsterGenerator', 'Skill_OnHitAttackRadius',
    'Skill_Passive', 'Skill_PassiveOnHitBuffSelf', 'Skill_PassiveOnItemUsedBuffSelf',
    'Skill_PassiveOnLifeBuffSelf', 'Skill_PassiveOnTargetKilled', 'Skill_RefreshCooldown',
    'Skill_SpawnPet', 'Skill_SpawnPetMonster', 'Skill_WPAttack_BasicAttack',
    'Skill_WeaponPool_ChargedFinale', 'Skill_WeaponPool_ChargedLinear', 'Skill_WeaponPool_WarmUp',
})

# Soul-drop classification (mirrors apply_svc_patches _find_soul_drop_leaks) ------
HERO_BOSS_QUEST = frozenset({'Hero', 'Boss', 'Quest'})
EQUIP_SLOTS = ('Finger1', 'Finger2', 'Head', 'Torso', 'LowerBody', 'Forearm',
               'RightHand', 'LeftHand', 'Misc1', 'Misc2', 'Misc3')
CREATURE_MARKERS = ('\\creature\\', '\\creatures\\')

# Soul level-only design law -----------------------------------------------------
STAT_REQ_FIELDS = ('strengthRequirement', 'dexterityRequirement', 'intelligenceRequirement')

# Name string color convention ---------------------------------------------------
SOUL_NAME_COLOR_PREFIX = '{^F}'   # pink/magenta; required on soul name strings

# Skill-granting string fields on a soul (each is a DBR path that must resolve).
SOUL_SKILL_FIELDS = ('itemSkillName', 'augmentSkillName1', 'augmentSkillName2',
                     'augmentSkillName3', 'augmentSkillName4', 'itemSkillAutoController')


# ============================================================================
# CONTRACT DESCRIPTORS
# ============================================================================
CONTRACTS = [
    {'id': 'SOUL-SKILL-REF-RESOLVES', 'name': 'Soul skill/controller references resolve',
     'asserts': 'every itemSkillName / augmentSkillName1..4 / itemSkillAutoController path on a '
                'soul resolves to a real record in the .arz (a dangling ref grants nothing).',
     'derived_from': 'base game 876/876 granted refs resolve; mirrors _verify_soul_augments_resolve'},
    {'id': 'SOUL-ITEMCOST-RESOLVES', 'name': 'Soul itemCostName resolves',
     'asserts': 'if a soul sets itemCostName, the referenced cost record exists in the .arz.',
     'derived_from': 'base rings use resolving itemcost_* records; our souls 2191/2191 resolve'},
    {'id': 'SOUL-ICON-RESOLVES', 'name': 'Soul icon/bitmap resolves in resource arcs',
     'asserts': 'every soul bitmap is non-empty and its <Arc>\\path.tex resolves inside the '
                'shipped resource arc (mod Resources UNION base-game Resources).',
     'derived_from': 'base game: 100% of jewelry has a resolving bitmap; our souls 2191/2191 in SVItems'},
    {'id': 'SOUL-PROC-ACTIVATION', 'name': 'Granted item-skill activation chain is live',
     'asserts': 'a soul that sets itemSkillName has itemSkillLevel >= 1, the granted record Class '
                'starts with Skill_, and any itemSkillAutoController has template '
                'SkillAutoCastController.tpl + chanceToRun > 0 + a triggerType in the base-game set.',
     'derived_from': 'base 876/876 set itemSkillLevel>=1; 228/228 controllers conform; 7 base triggers'},
    {'id': 'SOUL-AUGMENT-LEVEL', 'name': 'Augment skill has companion level and real Class',
     'asserts': 'every augmentSkillNameN set on a soul has augmentSkillLevelN present and >= 1, and '
                'the augment skill Class starts with Skill_ or SkillSecondary_.',
     'derived_from': 'base 584/584 + 181/181 and SV 1445/1445 + 687/687 augments carry level>=1'},
    {'id': 'SOUL-NAME-RESOLVES', 'name': 'Soul name tag resolves in Text',
     'asserts': "a soul's itemNameTag resolves in base Text_EN.arc UNION mod Text.arc (else the raw "
                'tag string renders in-game).',
     'derived_from': 'in-game text overlay model; 2000/2000 real souls resolve on the baseline'},
    {'id': 'SOUL-NAME-COLOR', 'name': 'Soul name string uses the {^F} color prefix',
     'asserts': "a soul's resolved name string begins with {^F} (the pink soul-name convention).",
     'derived_from': '1997/2000 real soul name strings begin with {^F} (the 3 anysoul are whitelisted)'},
    {'id': 'SOUL-LEVEL-ONLY', 'name': 'Souls gate on level only (no stat requirement)',
     'asserts': 'a soul has strengthRequirement == dexterityRequirement == intelligenceRequirement '
                '== 0 (this mod design law: souls require character level only).',
     'derived_from': "mod design law; 2095/2095 baseline souls have zero stat requirements"},
    {'id': 'SOUL-DROP-CLASSIFICATION', 'name': 'Only Hero/Boss/Quest creatures drop souls',
     'asserts': 'no creature whose monsterClassification is not Hero/Boss/Quest carries a soul ring '
                'in an equip slot with chanceToEquip<slot> > 0.',
     'derived_from': 'mod design law; mirrors _verify_no_unclassified_soul_leaks (0 leaks in build27)'},
    {'id': 'SOUL-GRANT-USABILITY', 'name': 'Granted item-skill Class is item-castable',
     'asserts': "a soul's itemSkillName grants a skill whose Class is within the base-UNION-SV set of "
                'Classes ever granted via an item (else it may be a monster-only/unusable skill).',
     'derived_from': 'base(47) UNION SV(45) = 53 grantable Classes; our souls 0 outside on baseline'},
]


# ============================================================================
# HELPERS
# ============================================================================
@contextlib.contextmanager
def _quiet():
    """Redirect stdout to stderr so the shared .arz loader's progress prints do NOT
    pollute this module's pure-JSON stdout (the loader uses print())."""
    saved = sys.stdout
    sys.stdout = sys.stderr
    try:
        yield
    finally:
        sys.stdout = saved


def _norm(path):
    """Normalize a DBR/texture path the way the engine resolves references."""
    return str(path).replace('/', '\\').lower().strip()


def _basename(name):
    return _norm(name).rsplit('\\', 1)[-1]


class _Ctx:
    """Loaded artifacts + memoized lookups shared by every contract."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.notes = []          # human-readable caveats (missing optional inputs)
        with _quiet():
            self.db = ArzDatabase.from_arz(Path(cfg['arz']))
        self.recmap = {_norm(n): n for n in self.db.record_names()}
        self._field_cache = {}
        self._text_tags = None
        self._arc_paths = {}     # arc-name -> set(normalized internal paths)

    # --- .arz field access -------------------------------------------------
    def fval(self, rec, field):
        """First value-list for a field on a record (None if absent/empty)."""
        ff = self.db.get_fields(rec)
        if not ff:
            return None
        for key, tf in ff.items():
            if key.split('###')[0] == field and tf.values:
                return tf.values
        return None

    def fscalar(self, rec, field):
        v = self.fval(rec, field)
        return v[0] if v else None

    def resolves(self, path):
        return _norm(path) in self.recmap

    def record_class(self, rec):
        c = self.fval(rec, 'Class')
        return c[0] if c else None

    # --- soul-record set ---------------------------------------------------
    def real_souls(self):
        """Class==ArmorJewelry_Ring under equipmentring\\soul\\, minus clone templates."""
        out = []
        for n in self.db.record_names():
            nl = _norm(n)
            if SOUL_RING_MARK not in nl:
                continue
            if self.record_class(n) != SOUL_RING_CLASS:
                continue
            if TEMPLATE_BASENAME in _basename(n):
                continue
            out.append(n)
        return out

    # --- Text tag resolution (base Text_EN.arc UNION mod Text.arc) ----------
    def text_tags(self):
        if self._text_tags is not None:
            return self._text_tags
        tags = {}
        # base first (lower precedence), then mod overlays on top.
        base_dir = self.cfg.get('base_game_dir')
        if base_dir:
            base_text = Path(base_dir) / 'Text' / 'Text_EN.arc'
            if base_text.is_file():
                self._merge_arc_tags(base_text, tags)
            else:
                self.notes.append(f"base Text_EN.arc not found at {base_text}; "
                                  "SOUL-NAME-RESOLVES checked against mod Text only "
                                  "(may over-report base-provided tags)")
        else:
            self.notes.append("no base_game_dir in cfg; SOUL-NAME-RESOLVES checked "
                              "against mod Text only")
        mod_text = self.cfg.get('text_arc')
        if mod_text and Path(mod_text).is_file():
            self._merge_arc_tags(Path(mod_text), tags)
        else:
            self.notes.append("mod text_arc missing; SOUL-NAME-* not checked")
            self._text_tags = None
            return None
        self._text_tags = tags
        return tags

    @staticmethod
    def _merge_arc_tags(arc_path, into):
        arc = ArcArchive.from_file(arc_path)
        for e in arc.entries:
            nm = getattr(e, 'name', '')
            if not nm.lower().endswith('.txt'):
                continue
            txt = arc.get_text(nm)
            if not txt:
                continue
            for line in txt.split('\n'):
                line = line.strip('\r').strip()
                if not line or line.startswith('//') or '=' not in line:
                    continue
                k, _, v = line.partition('=')
                into[k.strip()] = v   # later arcs overlay earlier ones

    # --- resource-arc (.tex) resolution ------------------------------------
    def _arc_path_set(self, arc_name):
        """Normalized internal file paths present in <arc_name> across mod + base."""
        if arc_name in self._arc_paths:
            return self._arc_paths[arc_name]
        s = set()
        candidates = []
        res_dir = self.cfg.get('resource_arc_dir')
        if res_dir:
            candidates.append(Path(res_dir) / f"{arc_name}.arc")
        base_dir = self.cfg.get('base_game_dir')
        if base_dir:
            base_res = Path(base_dir) / 'Resources'
            candidates.append(base_res / f"{arc_name}.arc")
            for sub in ('xpack', 'XPack2', 'XPack3', 'XPack4'):
                candidates.append(base_res / sub / f"{arc_name}.arc")
        for cand in candidates:
            try:
                if cand.is_file():
                    arc = ArcArchive.from_file(cand)
                    for e in arc.entries:
                        if getattr(e, 'entry_type', 0) == 3:
                            s.add(_norm(e.name))
            except Exception:
                continue
        self._arc_paths[arc_name] = s
        return s

    def resolve_tex(self, texpath):
        """True if a "<Arc>\\internal\\path.tex" resolves in the shipped resource arcs."""
        p = _norm(texpath)
        parts = p.split('\\')
        if len(parts) < 2:
            return False
        arc_name, internal = parts[0], '\\'.join(parts[1:])
        aset = self._arc_path_set(arc_name)
        if not aset:
            return None   # arc not available -> cannot check
        return internal in aset or p in aset


def _v(contract, severity, subject, message, evidence):
    return {'contract': contract, 'severity': severity, 'subject': subject,
            'message': message, 'evidence': str(evidence)}


# ============================================================================
# CONTRACTS
# ============================================================================
def _c_skill_ref_resolves(ctx, souls, out):
    for n in souls:
        for field in SOUL_SKILL_FIELDS:
            for val in (ctx.fval(n, field) or []):
                if isinstance(val, str) and val.strip() and not ctx.resolves(val):
                    out.append(_v('SOUL-SKILL-REF-RESOLVES', 'P0', n,
                                  f"{field} does not resolve to a record (granted skill is a "
                                  f"silent no-op)", f"{field}={val}"))


def _c_itemcost_resolves(ctx, souls, out):
    for n in souls:
        ic = ctx.fscalar(n, 'itemCostName')
        if isinstance(ic, str) and ic.strip() and not ctx.resolves(ic):
            out.append(_v('SOUL-ITEMCOST-RESOLVES', 'P1', n,
                          "itemCostName does not resolve to a record", f"itemCostName={ic}"))


def _c_icon_resolves(ctx, souls, out):
    checked_any = False
    for n in souls:
        b = ctx.fscalar(n, 'bitmap')
        if not (isinstance(b, str) and b.strip()):
            out.append(_v('SOUL-ICON-RESOLVES', 'P1', n,
                          "soul has no bitmap (renders as a blank/placeholder icon)",
                          f"bitmap={b!r}"))
            continue
        res = ctx.resolve_tex(b)
        if res is None:
            # arc for this bitmap not available to the checker; note once.
            continue
        checked_any = True
        if not res:
            out.append(_v('SOUL-ICON-RESOLVES', 'P1', n,
                          "soul bitmap does not resolve in any shipped resource arc",
                          f"bitmap={b}"))
    if not checked_any and souls:
        ctx.notes.append("SOUL-ICON-RESOLVES: resource arcs unavailable "
                         "(resource_arc_dir/base_game_dir); icon paths not verified")


def _c_proc_activation(ctx, souls, out):
    for n in souls:
        isn = ctx.fscalar(n, 'itemSkillName')
        if not (isinstance(isn, str) and isn.strip()):
            continue
        # granted skill Class must be Skill_*
        sk = ctx.recmap.get(_norm(isn))
        if sk:
            cls = ctx.fscalar(sk, 'Class')
            if not (cls and str(cls).startswith(SKILL_CLASS_PREFIX)):
                out.append(_v('SOUL-PROC-ACTIVATION', 'P1', n,
                              "itemSkillName does not point at a Skill_* record",
                              f"itemSkillName={isn} Class={cls}"))
        # itemSkillLevel present and >= 1 (the 219-soul B-SOUL-PROC-1 defect)
        lvl = ctx.fscalar(n, 'itemSkillLevel')
        if lvl is None:
            out.append(_v('SOUL-PROC-ACTIVATION', 'P1', n,
                          "itemSkillLevel ABSENT: granted skill instantiates at level 0 = "
                          "inactive, never procs", f"itemSkillName={isn}"))
        elif int(lvl) < 1:
            out.append(_v('SOUL-PROC-ACTIVATION', 'P1', n,
                          f"itemSkillLevel == {int(lvl)}: level-0 grant = inactive, never procs",
                          f"itemSkillName={isn} itemSkillLevel={int(lvl)}"))
        # controller (if set + resolves) must be a live SkillAutoCastController
        ctl = ctx.fscalar(n, 'itemSkillAutoController')
        if isinstance(ctl, str) and ctl.strip():
            cr = ctx.recmap.get(_norm(ctl))
            if cr:   # unresolved controllers are already SOUL-SKILL-REF-RESOLVES
                tpl = ctx.fscalar(cr, 'templateName')
                if not (tpl and _norm(tpl) == CTRL_TEMPLATE):
                    out.append(_v('SOUL-PROC-ACTIVATION', 'P1', n,
                                  "itemSkillAutoController has wrong templateName",
                                  f"controller={ctl} templateName={tpl}"))
                chance = ctx.fscalar(cr, 'chanceToRun')
                if chance is None or float(chance) <= 0:
                    out.append(_v('SOUL-PROC-ACTIVATION', 'P1', n,
                                  "itemSkillAutoController chanceToRun <= 0 (never fires)",
                                  f"controller={ctl} chanceToRun={chance}"))
                trig = ctx.fscalar(cr, 'triggerType')
                if not (isinstance(trig, str) and trig.strip()):
                    out.append(_v('SOUL-PROC-ACTIVATION', 'P1', n,
                                  "itemSkillAutoController has empty triggerType",
                                  f"controller={ctl}"))
                elif trig not in BASE_TRIGGER_TYPES:
                    out.append(_v('SOUL-PROC-ACTIVATION', 'P2', n,
                                  "itemSkillAutoController triggerType not used by any base-game "
                                  "granted controller", f"controller={ctl} triggerType={trig}"))


def _c_augment_level(ctx, souls, out):
    for n in souls:
        for i in (1, 2, 3, 4):
            asn = ctx.fscalar(n, f'augmentSkillName{i}')
            if not (isinstance(asn, str) and asn.strip()):
                continue
            alvl = ctx.fscalar(n, f'augmentSkillLevel{i}')
            if alvl is None:
                out.append(_v('SOUL-AUGMENT-LEVEL', 'P1', n,
                              f"augmentSkillName{i} set but augmentSkillLevel{i} ABSENT "
                              f"(+0 to skill = no effect)", f"augmentSkillName{i}={asn}"))
            elif int(alvl) < 1:
                out.append(_v('SOUL-AUGMENT-LEVEL', 'P1', n,
                              f"augmentSkillLevel{i} == {int(alvl)} (+0 to skill = no effect)",
                              f"augmentSkillName{i}={asn} augmentSkillLevel{i}={int(alvl)}"))
            sk = ctx.recmap.get(_norm(asn))
            if sk:
                cls = ctx.fscalar(sk, 'Class')
                if not (cls and str(cls).startswith(AUGMENT_CLASS_PREFIXES)):
                    out.append(_v('SOUL-AUGMENT-LEVEL', 'P1', n,
                                  f"augmentSkillName{i} Class is not a skill",
                                  f"augmentSkillName{i}={asn} Class={cls}"))


def _c_name_resolves_and_color(ctx, souls, out):
    tags = ctx.text_tags()
    if tags is None:
        return
    for n in souls:
        nt = ctx.fscalar(n, 'itemNameTag')
        if not (isinstance(nt, str) and nt.strip()):
            out.append(_v('SOUL-NAME-RESOLVES', 'P1', n,
                          "soul has no itemNameTag", f"itemNameTag={nt!r}"))
            continue
        tag = nt.strip()
        if tag not in tags:
            out.append(_v('SOUL-NAME-RESOLVES', 'P1', n,
                          "itemNameTag resolves in neither base Text_EN.arc nor mod Text.arc "
                          "(raw tag renders in-game)", f"itemNameTag={tag}"))
            continue
        val = tags[tag]
        if not val.startswith(SOUL_NAME_COLOR_PREFIX):
            out.append(_v('SOUL-NAME-COLOR', 'P2', n,
                          "soul name string does not begin with the {^F} pink color prefix",
                          f"{tag}={val[:40]!r}"))


def _c_level_only(ctx, souls, out):
    for n in souls:
        for field in STAT_REQ_FIELDS:
            v = ctx.fscalar(n, field)
            if v is not None and float(v) != 0:
                out.append(_v('SOUL-LEVEL-ONLY', 'P1', n,
                              f"{field} is nonzero (souls must gate on level only)",
                              f"{field}={v}"))


def _c_drop_classification(ctx, souls, out):
    """Independent re-implementation of the shipped soul-leak gate: a non-HBQ creature
    with a soul ring in a slot at chanceToEquip<slot> > 0 leaks a soul drop."""
    for n in ctx.db.record_names():
        nl = _norm(n)
        if not any(m in nl for m in CREATURE_MARKERS):
            continue
        ff = ctx.db.get_fields(n)
        if not ff:
            continue
        # fast screen: any soul ring in any loot*Item* field?
        has_soul = False
        for key, tf in ff.items():
            fn = key.split('###')[0]
            if fn.startswith('loot') and 'Item' in fn and tf.values:
                if any(isinstance(x, str) and SOUL_RING_MARK in _norm(x) for x in tf.values):
                    has_soul = True
                    break
        if not has_soul:
            continue
        mc = ctx.fscalar(n, 'monsterClassification')
        if mc in HERO_BOSS_QUEST:
            continue
        for slot in EQUIP_SLOTS:
            soul_item = None
            for i in range(1, 7):
                vals = ctx.fval(n, f'loot{slot}Item{i}') or []
                for x in vals:
                    if isinstance(x, str) and SOUL_RING_MARK in _norm(x):
                        soul_item = x
                        break
                if soul_item:
                    break
            if not soul_item:
                continue
            ch = ctx.fscalar(n, f'chanceToEquip{slot}')
            try:
                ch = float(ch)
            except (TypeError, ValueError):
                ch = 0.0
            if ch > 0:
                out.append(_v('SOUL-DROP-CLASSIFICATION', 'P1', n,
                              f"non-Hero/Boss/Quest creature (class={mc!r}) drops a soul",
                              f"chanceToEquip{slot}={ch} -> {soul_item}"))


def _c_grant_usability(ctx, souls, out):
    for n in souls:
        isn = ctx.fscalar(n, 'itemSkillName')
        if not (isinstance(isn, str) and isn.strip()):
            continue
        sk = ctx.recmap.get(_norm(isn))
        if not sk:
            continue   # unresolved handled by SOUL-SKILL-REF-RESOLVES
        cls = ctx.fscalar(sk, 'Class')
        if cls and str(cls).startswith(SKILL_CLASS_PREFIX) and cls not in GRANTABLE_SET:
            out.append(_v('SOUL-GRANT-USABILITY', 'P2', n,
                          "granted itemSkillName Class is outside the base-UNION-SV set ever "
                          "granted via an item (may be monster-only / unusable as an item proc)",
                          f"itemSkillName={isn} Class={cls}"))


_CONTRACT_FUNCS = (
    _c_skill_ref_resolves,
    _c_itemcost_resolves,
    _c_icon_resolves,
    _c_proc_activation,
    _c_augment_level,
    _c_name_resolves_and_color,
    _c_level_only,
    _c_drop_classification,
    _c_grant_usability,
)


# ============================================================================
# WHITELIST
# ============================================================================
def _load_whitelist():
    """(contract, normalized-subject) pairs to suppress, from whitelist_souls.txt."""
    wl = set()
    path = Path(__file__).resolve().parent / 'whitelist_souls.txt'
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
    """Run every soul contract over the artifacts named in cfg; return violations."""
    ctx = _Ctx(cfg)
    souls = ctx.real_souls()
    raw = []
    for fn in _CONTRACT_FUNCS:
        fn(ctx, souls, raw)

    wl = _load_whitelist()
    violations = [x for x in raw if (x['contract'], _norm(x['subject'])) not in wl]

    run.last_notes = ctx.notes
    run.last_soul_count = len(souls)
    run.last_suppressed = len(raw) - len(violations)
    return violations


# ============================================================================
# STANDALONE CLI
# ============================================================================
_CFG_ORDER = ('arz', 'text_arc', 'levels_arc', 'quests_arc',
              'resource_arc_dir', 'base_game_dir', 'upstream_dir')


def _cfg_from_argv(argv):
    if len(argv) < 2:
        print(__doc__)
        print("ERROR: at least the <arz> path is required.", file=sys.stderr)
        sys.exit(2)
    cfg = {k: None for k in _CFG_ORDER}
    for key, val in zip(_CFG_ORDER, argv[1:]):
        cfg[key] = val
    return cfg


def main(argv):
    cfg = _cfg_from_argv(argv)
    if not Path(cfg['arz']).is_file():
        print(f"ERROR: .arz not found: {cfg['arz']}", file=sys.stderr)
        sys.exit(2)
    violations = run(cfg)
    for v in violations:
        print(json.dumps(v, ensure_ascii=False))
    # Human-readable summary + notes to stderr (stdout stays pure JSON lines).
    from collections import Counter
    by_c = Counter(v['contract'] for v in violations)
    print(f"\n[contracts_souls] souls checked: {getattr(run, 'last_soul_count', '?')}; "
          f"violations: {len(violations)}; suppressed by whitelist: "
          f"{getattr(run, 'last_suppressed', 0)}", file=sys.stderr)
    for cid, k in by_c.most_common():
        sev = next((c for c in violations if c['contract'] == cid), {}).get('severity', '?')
        print(f"   {cid:26s} {k:5d}  ({sev})", file=sys.stderr)
    for note in getattr(run, 'last_notes', []):
        print(f"   NOTE: {note}", file=sys.stderr)
    p0p1 = [v for v in violations if v['severity'] in ('P0', 'P1')]
    sys.exit(1 if p0p1 else 0)


if __name__ == '__main__':
    main(sys.argv)
