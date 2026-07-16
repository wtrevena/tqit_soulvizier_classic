"""BL-AURA-RADIUS audit: enumerate EVERY aura-class skill in the EFFECTIVE DB
(mod arz overlaid on the base-game arz) by template/Class + radius-field
presence - NOT by name.

For each aura it captures: record path, display name, Class/template, current
radius (explicit skillTargetRadius/targetRadius on the delivery record, else on
the buffSkillName payload record, else the Templates.arc default), the full
non-zero effect list (positives AND negatives - negatives flagged because for
radius-buff templates the payload applies to EVERY friendly in radius, so a
malus WIDENS onto pets/allies with the radius), who grants/casts it (playable
mastery tree / soul ring / item / player-summonable pet / monster-only /
unreferenced), and toggle-vs-passive-vs-one-shot.

Read-only over the built arz + base arz. No build. Outputs:
  - docs/reports/b57_aura_radius.md   (the Will-veto audit table)
  - tools/aura_radius_roster.json     (machine roster for tools/patches/aura_radius.py)

Usage:
  py tools/audit_aura_radius.py [mod.arz] [base.arz] [--json OUT] [--md OUT]

Aura-shaped delivery Classes swept (radius-buff semantics, friendly targets):
  Skill_BuffRadiusToggled        toggled party aura (radius on payload)
  Skill_BuffAttackRadiusToggled  toggled aura w/ offensive component (radius on self)
  Skill_BuffRadius               one-shot radius buff (radius on payload or self)
  Skill_BuffAttackRadiusDuration duration radius buff/attack (radius on self)
  SkillSecondary_BuffRadius      pet-special radius buff
  Skill_AttackBuffRadius         attack that buffs in radius
Plus:
  SkillBuff_Passive / SkillBuff_PassiveShield records that carry an explicit
  skillTargetRadius AND are attached DIRECTLY to a creature or item (passive
  auras) - payload-only usages are folded into their delivery skill row.
  FixedItemSkill_Buff with targetRadius > 0 (scroll/consumable radius buffs).

Deliberately EXCLUDED (documented, not aura-shaped friendly buffs):
  SkillBuff_Debuf/DebufFreeze/DebufTrap/Contageous (enemy debuffs), Skill_
  AttackRadius* / OnHitAttackRadius / SkillSecondary_AttackRadius (damage
  novas/auras - radius == damage reach; widening them is a damage buff, needs
  its own mandate), Skill_BuffOther/BuffSelf* (no radius / self-only).
"""
import json
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase, DATA_TYPE_STRING  # noqa: E402
from arc_patcher import ArcArchive                     # noqa: E402

REPO = Path(__file__).resolve().parents[1]
MAIN_REPO = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic")
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition")

DELIVERY_CLASSES = {
    'Skill_BuffRadiusToggled': 'toggled aura',
    'Skill_BuffAttackRadiusToggled': 'toggled aura (offensive component)',
    'Skill_BuffRadius': 'one-shot radius buff',
    'Skill_BuffAttackRadiusDuration': 'duration radius buff',
    'SkillSecondary_BuffRadius': 'pet-special radius buff',
    'Skill_AttackBuffRadius': 'attack radius buff',
}
PASSIVE_PAYLOAD_CLASSES = {'SkillBuff_Passive', 'SkillBuff_PassiveShield'}
SCROLL_CLASS = 'FixedItemSkill_Buff'

CREATURE_CLASSES = {'monster', 'pet', 'questpet', 'player', 'npc', 'boss'}
# classes whose record is a creature that can CAST a skill it references
CASTER_CLASSES = {'monster', 'pet', 'questpet', 'boss'}
ITEM_CLASS_PREFIXES = ('armor', 'weapon', 'item', 'oneshot')
SOUL_RING_MARK = 'equipmentring\\soul\\'

RADIUS_FIELDS = ('skillTargetRadius', 'targetRadius')

# numeric payload fields that are gameplay effects (vs meta/cost/UI)
EFFECT_PREFIXES = ('character', 'defensive', 'offensive', 'retaliation',
                   'skillLifeBonus', 'damageAbsorption', 'lifeMonitor')
COST_FIELDS = {'characterManaLimitReserve', 'characterManaLimitReserveModifier',
               'characterManaLimitReserveReduction',
               'characterManaLimitReserveReductionModifier'}
META_NUMERIC = {'cameraShakeAmplitude', 'cameraShakeDurationSecs'}


def _norm(p):
    return str(p).replace('/', '\\').lower().strip()


def _base(p):
    return _norm(p).rsplit('\\', 1)[-1]


class Effective:
    """Mod-over-base effective record view keyed by normalized path."""

    def __init__(self, mod, base):
        self.mod, self.base = mod, base
        self.owner = {}      # norm -> (db, canonical_name)
        for n in base._raw_records:
            self.owner[_norm(n)] = (base, n)
        for n in mod._raw_records:
            self.owner[_norm(n)] = (mod, n)

    def has(self, norm):
        return norm in self.owner

    def src(self, norm):
        db, _ = self.owner[norm]
        return 'MOD' if db is self.mod else 'BASE'

    def name(self, norm):
        return self.owner[norm][1]

    def rclass(self, norm):
        db, n = self.owner[norm]
        c = db._record_types.get(n, '')
        return c

    def fields(self, norm):
        db, n = self.owner[norm]
        return db.get_fields(n)

    def raw_iter(self):
        for norm, (db, n) in self.owner.items():
            yield norm, db, n


def load_text_maps():
    """tag -> display text; mod Text.arc overrides base Text_EN.arc."""
    tags = {}

    def eat(arc_path):
        if not arc_path or not Path(arc_path).exists():
            return 0
        try:
            arc = ArcArchive.from_file(Path(arc_path))
        except Exception:
            return 0
        got = 0
        for e in arc.entries:
            if not e.name.lower().endswith('.txt'):
                continue
            try:
                txt = arc.decompress(e).decode('utf-16', errors='ignore')
            except Exception:
                continue
            for line in txt.splitlines():
                line = line.strip().lstrip('﻿')
                if not line or line.startswith('//') or '=' not in line:
                    continue
                k, _, v = line.partition('=')
                if k.strip():
                    tags[k.strip()] = v.strip()
                    got += 1
        return got

    n_base = eat(GAME / 'Text' / 'Text_EN.arc')
    mod_text = None
    for cand in (REPO / 'work' / 'SoulvizierClassic' / 'Resources' / 'Text.arc',
                 MAIN_REPO / 'work' / 'SoulvizierClassic' / 'Resources' / 'Text.arc'):
        if cand.exists():
            mod_text = cand
            break
    n_mod = eat(mod_text)
    print(f"  text tags: base {n_base}, mod {n_mod} ({mod_text})")
    return tags


def load_template_defaults():
    """basename('skill_buffradiustoggled.tpl') -> {var: defaultValue} with
    includes resolved recursively. Best-effort; returns {} if Templates.arc
    is unavailable."""
    tpl_arc = GAME / 'Toolset' / 'Templates.arc'
    if not tpl_arc.exists():
        print("  Templates.arc NOT FOUND - template defaults unresolved")
        return {}
    arc = ArcArchive.from_file(tpl_arc)
    raw = {}          # basename -> (vars{}, includes[])
    var_re = re.compile(r'name\s*=\s*"([^"]+)"')
    def_re = re.compile(r'defaultValue\s*=\s*"([^"]*)"')
    inc_re = re.compile(r'include\s*=?\s*"([^"]+\.tpl)"', re.IGNORECASE)
    for e in arc.entries:
        if not e.name.lower().endswith('.tpl'):
            continue
        try:
            txt = arc.decompress(e).decode('latin-1', errors='ignore')
        except Exception:
            continue
        variables, includes = {}, [ _base(m) for m in inc_re.findall(txt) ]
        # crude block parse: Variable { ... } blocks carry name= + defaultValue=
        for block in re.split(r'\bVariable\b', txt)[1:]:
            head = block[:block.find('}')] if '}' in block else block
            nm = var_re.search(head)
            dv = def_re.search(head)
            if nm:
                variables[nm.group(1)] = dv.group(1) if dv else ''
        raw[_base(e.name)] = (variables, includes)

    resolved = {}

    def resolve(bn, seen=None):
        seen = seen or set()
        if bn in resolved:
            return resolved[bn]
        if bn not in raw or bn in seen:
            return {}
        seen.add(bn)
        variables, includes = raw[bn]
        out = {}
        for inc in includes:
            out.update(resolve(inc, seen))
        out.update(variables)
        resolved[bn] = out
        return out

    for bn in list(raw):
        resolve(bn)
    print(f"  templates parsed: {len(resolved)}")
    return resolved


def main(argv):
    # --json / --md override the output paths (per the module docstring); default to
    # the committed artifacts. Parse them out so a regeneration can target scratch
    # files without clobbering the real roster/report (the defaults are destructive).
    md_out = REPO / 'docs' / 'reports' / 'b57_aura_radius.md'
    json_out = REPO / 'tools' / 'aura_radius_roster.json'
    positional, i = [], 1
    while i < len(argv):
        a = argv[i]
        if a == '--json' and i + 1 < len(argv):
            json_out = Path(argv[i + 1]); i += 2; continue
        if a == '--md' and i + 1 < len(argv):
            md_out = Path(argv[i + 1]); i += 2; continue
        positional.append(a); i += 1
    mod_arz = Path(positional[0]) if len(positional) > 0 else None
    base_arz = Path(positional[1]) if len(positional) > 1 else GAME / 'Database' / 'database.arz'
    if mod_arz is None:
        for cand in (REPO / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz',
                     MAIN_REPO / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'):
            if cand.exists():
                mod_arz = cand
                break

    print(f"mod arz : {mod_arz}")
    print(f"base arz: {base_arz}")
    mod = ArzDatabase.from_arz(mod_arz)
    base = ArzDatabase.from_arz(base_arz)
    eff = Effective(mod, base)
    print(f"effective records: {len(eff.owner)}")

    tags = load_text_maps()
    tpl_defaults = load_template_defaults()

    # ---- streaming pass: reverse-ref index + lite field capture -------------
    print("pass 1: reverse-reference index over the effective DB ...")
    refs_into = defaultdict(list)        # dst_norm -> [(src_norm, field)]
    lite = {}                            # norm -> small dict of wanted fields
    WANT_SCALAR = {'buffSkillName', 'skillDisplayName', 'FileDescription',
                   'itemNameTag', 'description', 'templateName', 'Class',
                   'petBonusName', 'racialBonusRace'}
    WANT_VALS = {'skillTargetRadius', 'targetRadius', 'skillTargetNumber',
                 'skillActiveDuration', 'skillManaCost'}
    n_done = 0
    for norm, db, n in eff.raw_iter():
        _, compressed = db._raw_records[n]
        try:
            fields = db._decode_fields(compressed)
        except Exception:
            continue
        small = {}
        for key, tf in fields.items():
            fname = key.split('###')[0]
            if tf.dtype == DATA_TYPE_STRING:
                for v in tf.values:
                    if isinstance(v, str) and v.lower().endswith('.dbr'):
                        refs_into[_norm(v)].append((norm, fname))
                if fname in WANT_SCALAR and tf.values:
                    small[fname] = tf.values[0]
            else:
                if fname in WANT_VALS and tf.values:
                    small[fname] = list(tf.values)
        if small:
            lite[norm] = small
        n_done += 1
        if n_done % 20000 == 0:
            print(f"  {n_done}/{len(eff.owner)}")
    print(f"  edges into {len(refs_into)} referenced targets")

    # ---- playable mastery trees --------------------------------------------
    playable_trees = {}                  # tree_norm -> label
    for pc in ('records\\xpack\\creatures\\pc\\malepc01.dbr',
               'records\\xpack\\creatures\\pc\\femalepc01.dbr'):
        if not eff.has(pc):
            continue
        f = eff.fields(pc)
        for key, tf in f.items():
            fname = key.split('###')[0]
            if fname.startswith('skillTree') and tf.values:
                t = _norm(tf.values[0])
                if eff.has(t):
                    playable_trees.setdefault(t, fname)
    # label each tree by its mastery record's display tag
    tree_label = {}
    _LABEL_FIX = {'runemaster_skilltree': 'Rune Mastery',
                  'neidanskilltree': 'Neidan Mastery',
                  'questrewardskilltree': 'Quest rewards'}
    for t in playable_trees:
        label = _LABEL_FIX.get(_base(t).replace('.dbr', ''),
                               _base(t).replace('.dbr', ''))
        f = eff.fields(t)
        for key, tf in (f or {}).items():
            if key.split('###')[0].startswith('skillName') and tf.values:
                child = _norm(tf.values[0])
                if eff.has(child) and eff.rclass(child) == 'Skill_Mastery':
                    dt = lite.get(child, {}).get('skillDisplayName')
                    if dt:
                        label = tags.get(dt, dt)
                    break
        tree_label[t] = label
    print("playable trees:")
    for t, slot in sorted(playable_trees.items(), key=lambda kv: kv[1]):
        print(f"  {slot:12s} {tree_label[t]:20s} {t}")

    # ---- grantor walk --------------------------------------------------------
    def classify_referrer(norm):
        c = eff.rclass(norm)
        cl = c.lower()
        if c == 'SkillTree':
            return 'tree'
        if c == 'Skill_Mastery':
            return 'mastery'
        if cl in CREATURE_CLASSES:
            return 'creature'
        if cl.startswith(ITEM_CLASS_PREFIXES):
            return 'soul' if SOUL_RING_MARK in norm else 'item'
        return 'other'

    _creature_memo = {}

    def creature_is_player_pet(cnorm, depth=0):
        """True if the creature has an upward grant chain to a playable tree,
        soul, or item (=> summonable by the player)."""
        if cnorm in _creature_memo:
            return _creature_memo[cnorm]
        _creature_memo[cnorm] = (False, ())   # cycle guard
        hits = walk_up(cnorm)
        ok = bool(hits['mastery_trees'] or hits['souls'] or hits['items'])
        _creature_memo[cnorm] = (ok, hits)
        return _creature_memo[cnorm]

    def walk_up(start_norm, max_depth=10):
        """Collect grantors reachable UP the reverse-ref graph."""
        out = {'mastery_trees': set(), 'souls': set(), 'items': set(),
               'creatures': set(), 'other_trees': set()}
        seen = {start_norm}
        frontier = [start_norm]
        for _ in range(max_depth):
            nxt = []
            for cur in frontier:
                for src, field in refs_into.get(cur, ()):  # noqa: B905
                    if src in seen:
                        continue
                    seen.add(src)
                    kind = classify_referrer(src)
                    if kind == 'tree':
                        if src in playable_trees:
                            out['mastery_trees'].add(src)
                        else:
                            out['other_trees'].add(src)
                            nxt.append(src)
                    elif kind == 'mastery':
                        nxt.append(src)   # mastery record; its tree sits above
                    elif kind == 'soul':
                        out['souls'].add(src)
                    elif kind == 'item':
                        out['items'].add(src)
                    elif kind == 'creature':
                        out['creatures'].add(src)
                        nxt.append(src)   # continue up to its summoner
                    else:
                        nxt.append(src)
            frontier = nxt
            if not frontier:
                break
        return out

    # ---- resolve one aura row ------------------------------------------------
    def radius_of(norm):
        """(values, source) - explicit self / explicit payload / template default."""
        li = lite.get(norm, {})
        for f in RADIUS_FIELDS:
            if f in li:
                return li[f], 'self'
        payload = li.get('buffSkillName')
        pnorm = _norm(payload) if payload else None
        if pnorm and eff.has(pnorm):
            pl = lite.get(pnorm, {})
            for f in RADIUS_FIELDS:
                if f in pl:
                    return pl[f], 'payload'
        # template default: payload template if payload else self template
        t = None
        if pnorm and eff.has(pnorm):
            t = lite.get(pnorm, {}).get('templateName')
        if not t:
            t = li.get('templateName')
        if t:
            d = tpl_defaults.get(_base(t), {})
            for f in RADIUS_FIELDS:
                if f in d and d[f] not in ('', None):
                    try:
                        return [float(d[f])], f'template default ({_base(t)})'
                    except ValueError:
                        pass
        # ground-truthed 2026-07-14: every Templates.arc definition of
        # skillTargetRadius has an EMPTY defaultValue -> engine zero-init.
        # No explicit field anywhere == radius 0 (caster-only in practice).
        return [0.0], 'default-0 (no explicit radius field)'

    def effects_of(norm):
        """Non-zero gameplay effect fields from the payload (or self)."""
        li = lite.get(norm, {})
        payload = li.get('buffSkillName')
        pnorm = _norm(payload) if payload else None
        source = pnorm if (pnorm and eff.has(pnorm)) else norm
        f = eff.fields(source)
        pos, neg, notes = [], [], []
        if not f:
            return pos, neg, notes, source
        for key, tf in f.items():
            fname = key.split('###')[0]
            if tf.dtype == DATA_TYPE_STRING:
                if fname == 'petBonusName' and tf.values:
                    notes.append(f"petBonusName={tf.values[0]}")
                continue
            if not tf.values:
                continue
            vals = [v for v in tf.values if isinstance(v, (int, float))]
            if not vals or all(abs(v) < 1e-9 for v in vals):
                continue
            if fname in META_NUMERIC:
                continue
            if fname in COST_FIELDS:
                notes.append(f"{fname}={_fmt(vals)}")
                continue
            if not fname.startswith(EFFECT_PREFIXES):
                # keep skill-mechanics numbers as notes, skip pure UI ints
                if fname in ('skillActiveDuration', 'skillManaCost',
                             'skillTargetNumber', 'refreshTime', 'skillCooldownTime'):
                    notes.append(f"{fname}={_fmt(vals)}")
                continue
            (neg if min(vals) < 0 else pos).append(f"{fname}={_fmt(vals)}")
        return pos, neg, notes, source

    def _fmt(vals):
        s = [f"{v:g}" for v in vals[:4]]
        return '/'.join(s) + ('..' if len(vals) > 4 else '')

    def display_name(norm):
        li = lite.get(norm, {})
        tag = li.get('skillDisplayName') or li.get('itemNameTag') or li.get('description')
        if tag and tags.get(tag):
            return tags[tag].replace('{^F}', '').replace('^F', '').strip()
        if tag:
            return f"<{tag}>"
        fd = li.get('FileDescription')
        return fd if fd else _base(norm).replace('.dbr', '')

    # ---- build the roster ----------------------------------------------------
    print("pass 2: roster ...")
    rows = []
    payload_only = set()   # SkillBuff_Passive used as payload of some delivery row

    for norm in eff.owner:
        cls = eff.rclass(norm)
        if cls in DELIVERY_CLASSES:
            li = lite.get(norm, {})
            pn = li.get('buffSkillName')
            if pn:
                payload_only.add(_norm(pn))

    for norm in sorted(eff.owner):
        cls = eff.rclass(norm)
        row_kind = None
        if cls in DELIVERY_CLASSES:
            row_kind = DELIVERY_CLASSES[cls]
        elif cls in PASSIVE_PAYLOAD_CLASSES:
            li = lite.get(norm, {})
            has_radius = any(f in li for f in RADIUS_FIELDS)
            if not has_radius or norm in payload_only:
                continue
            # only if attached directly to a creature or item
            attached = False
            for src, field in refs_into.get(norm, ()):  # noqa: B905
                k = classify_referrer(src)
                if k in ('creature', 'soul', 'item') and field.lower() != 'buffskillname':
                    attached = True
                    break
            if not attached:
                continue
            row_kind = 'passive radius aura (creature/item-attached)'
        elif cls == SCROLL_CLASS:
            li = lite.get(norm, {})
            if 'targetRadius' not in li or not li['targetRadius'] or \
                    max(li['targetRadius']) <= 0:
                continue
            row_kind = 'scroll/consumable radius buff'
        else:
            continue

        rvals, rsrc = radius_of(norm)
        pos, neg, notes, effect_src = effects_of(norm)
        grants = walk_up(norm)
        # CASTERS = creatures that reference the aura DIRECTLY (depth-1).
        # Creatures found deeper in the walk are chain context, not casters.
        pets, monsters, pc_direct = [], [], False
        for src, field in refs_into.get(norm, ()):  # noqa: B905
            cl = eff.rclass(src).lower()
            if cl == 'player':
                pc_direct = True
                continue
            if cl in CASTER_CLASSES and field.lower() != 'buffskillname':
                ok, chains = creature_is_player_pet(src)
                (pets if ok else monsters).append(src)
        masteries = sorted(tree_label[t] for t in grants['mastery_trees'])
        souls = sorted(grants['souls'])
        items = sorted(grants['items'])
        referenced = bool(refs_into.get(norm))

        cat = []
        if masteries:
            cat.append('MASTERY')
        if souls:
            cat.append('SOUL')
        if items or cls == SCROLL_CLASS:
            cat.append('ITEM')
        if pets:
            cat.append('PET')
        if not cat:
            cat.append('MONSTER-ONLY' if monsters else
                       ('UNREFERENCED' if not referenced else 'INDIRECT-ONLY'))

        ho = any('hunting' in m.lower() or 'occult' in m.lower()
                 for m in masteries)

        rows.append(OrderedDict(
            record=eff.name(norm), norm=norm, src=eff.src(norm),
            cls=cls, kind=row_kind,
            display=display_name(norm),
            radius=rvals, radius_source=rsrc,
            effects_positive=pos, effects_negative=neg, notes=notes,
            effect_record=eff.name(effect_src) if eff.has(effect_src) else effect_src,
            masteries=masteries,
            souls=[eff.name(s) for s in souls],
            items=[eff.name(i) for i in items][:12],
            pet_casters=[eff.name(p) for p in sorted(set(pets))],
            monster_casters=[eff.name(m) for m in sorted(set(monsters))][:8],
            n_monster_casters=len(set(monsters)),
            pc_direct=pc_direct,
            category=cat, hunting_occult=ho,
        ))

    # ---- draft per-aura proposal (RULE ONLY - Will decides; nothing applied) --
    OFFENSIVE_CLASSES = {'Skill_BuffAttackRadiusToggled',
                         'Skill_BuffAttackRadiusDuration', 'Skill_AttackBuffRadius'}

    def _payload_offensive(r):
        """The record we would edit (effect_record) is an ENEMY debuf, so its
        skillTargetRadius is DAMAGE/DEBUF reach - widening it is a combat-power
        change, not a friendly-bonus reach. Detected by payload Class
        SkillBuff_Debuf* / SkillBuff_Contageous, or debufSkill=1. Note the offensive
        fields are stored POSITIVE (offensiveXxxMin), so effects_negative never sees
        them and the delivery class is friendly - this is the guard that catches
        friendly-looking Skill_BuffRadius(Toggled) deliveries of a debuf payload."""
        pn = _norm(r['effect_record'])
        if not eff.has(pn):
            return False
        c = eff.rclass(pn)
        if c.startswith('SkillBuff_Debuf') or c == 'SkillBuff_Contageous':
            return True
        f = eff.fields(pn)
        for key, tf in (f or {}).items():
            if key.split('###')[0] == 'debufSkill' and tf.values:
                try:
                    if int(tf.values[0]) == 1:
                        return True
                except (TypeError, ValueError):
                    pass
        return False

    for r in rows:
        cur = max(r['radius']) if r['radius'] else None
        player_facing = any(c in r['category'] for c in
                            ('MASTERY', 'SOUL', 'ITEM', 'PET'))
        if not player_facing:
            r['proposal'] = 'no change (enemy/dead record)'
        elif r['effects_negative']:
            r['proposal'] = 'HOLD - malus is aura-wide; widening spreads it (Will decision)'
        elif r['cls'] in OFFENSIVE_CLASSES:
            r['proposal'] = 'REVIEW - offensive radius component; widening changes combat power'
        elif _payload_offensive(r):
            r['proposal'] = ('HOLD - offensive PAYLOAD (SkillBuff_Debuf/debufSkill); '
                             'widening = damage/debuf reach (Will decision)')
        elif cur is None:
            r['proposal'] = 'RESOLVE radius first (no value found)'
        elif 'PET' in r['category'] and not ('MASTERY' in r['category'] or
                                             'SOUL' in r['category'] or
                                             'ITEM' in r['category']):
            r['proposal'] = f"pet aura: >= 18 (cur {cur:g})" if cur < 18 else f'keep {cur:g}'
        else:
            r['proposal'] = f"party aura: >= 36 (cur {cur:g})" if cur < 36 else f'keep {cur:g}'

    # ---- counts / gates -------------------------------------------------------
    def has_cat(r, c):
        return c in r['category']
    n_mastery = sum(1 for r in rows if has_cat(r, 'MASTERY'))
    n_soul = sum(1 for r in rows if has_cat(r, 'SOUL'))
    n_item = sum(1 for r in rows if has_cat(r, 'ITEM'))
    n_pet = sum(1 for r in rows if has_cat(r, 'PET'))
    n_monster = sum(1 for r in rows if r['category'] == ['MONSTER-ONLY'])
    n_unref = sum(1 for r in rows if r['category'] == ['UNREFERENCED'])
    n_indirect = sum(1 for r in rows if r['category'] == ['INDIRECT-ONLY'])
    n_neg = sum(1 for r in rows if r['effects_negative'])
    player_rows = [r for r in rows if any(c in r['category'] for c in
                                          ('MASTERY', 'SOUL', 'ITEM', 'PET'))]

    def _rng(rs):
        vals = [v for r in rs if r['radius'] for v in r['radius']]
        return f"{min(vals):g}-{max(vals):g}" if vals else 'n/a'

    summary = OrderedDict(
        auras_total=len(rows), mastery=n_mastery, soul_granted=n_soul,
        pet=n_pet, item_granted=n_item, monster_only=n_monster,
        unreferenced=n_unref, indirect_only=n_indirect,
        with_negatives=n_neg,
        current_radius_range=_rng(player_rows),
        current_radius_range_all=_rng(rows),
    )
    print("SUMMARY:", json.dumps(summary))

    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(
        {'summary': summary,
         'playable_trees': {t: tree_label[t] for t in playable_trees},
         'rows': rows}, indent=1), encoding='utf-8')
    print(f"wrote {json_out}")

    write_markdown(md_out, summary, rows,
                   {t: (playable_trees[t], tree_label[t]) for t in playable_trees},
                   mod_arz, base_arz)
    print(f"wrote {md_out}")
    return summary, rows


def _mdesc(r, full=True):
    """Effect cell: positives, NEGATIVES highlighted, notes."""
    parts = []
    if r['effects_positive']:
        pos = r['effects_positive']
        parts.append('; '.join(pos[:6]) + (f" +{len(pos)-6} more" if len(pos) > 6 else ''))
    if r['effects_negative']:
        parts.append('**NEG: ' + '; '.join(r['effects_negative']) + '**')
    if r['notes']:
        parts.append('_' + '; '.join(r['notes'][:4]) + '_')
    return '<br>'.join(parts) if parts else '(no numeric payload found)'


def _mgrant(r):
    g = []
    if r['masteries']:
        g.append('mastery: ' + ', '.join(r['masteries']))
    if r['souls']:
        names = sorted({s.rsplit('\\', 1)[-1].replace('.dbr', '') for s in r['souls']})
        g.append(f"souls({len(r['souls'])}): " + ', '.join(names[:5]) +
                 (' ...' if len(names) > 5 else ''))
    if r['items']:
        names = sorted({i.rsplit('\\', 1)[-1].replace('.dbr', '') for i in r['items']})
        g.append(f"items: " + ', '.join(names[:4]) + (' ...' if len(names) > 4 else ''))
    if r['pet_casters']:
        names = [p.rsplit('\\', 1)[-1].replace('.dbr', '') for p in r['pet_casters']]
        g.append('pet cast: ' + ', '.join(names[:5]) + (' ...' if len(names) > 5 else ''))
    if r['n_monster_casters']:
        g.append(f"monster cast x{r['n_monster_casters']}")
    if r.get('pc_direct'):
        g.append('PC-record direct')
    if g:
        return '; '.join(g)
    return ('referenced, no terminal grantor'
            if r['category'] == ['INDIRECT-ONLY'] else 'UNREFERENCED')


def _mradius(r):
    if not r['radius']:
        return f"? ({r['radius_source']})"
    vals = r['radius']
    s = f"{vals[0]:g}" if len(set(vals)) == 1 else \
        f"{min(vals):g}-{max(vals):g}"
    tag = {'self': '', 'payload': ' (payload)'}.get(r['radius_source'],
                                                    f" ({r['radius_source']})")
    return s + tag


def _mrow(r):
    ho = ' **[H/O]**' if r['hunting_occult'] else ''
    kind = 'toggle' if 'toggled' in r['kind'] else (
        'passive' if 'passive' in r['kind'] else 'one-shot')
    return (f"| {r['display']}{ho} | `{r['record']}` | {r['cls']} ({kind}) | "
            f"{_mradius(r)} | {_mdesc(r)} | {_mgrant(r)} | {r['proposal']} |\n")


_TABLE_HDR = ("| Aura | record | Class (cast) | radius | effects (payload) | "
              "granted/cast by | draft proposal |\n"
              "|---|---|---|---|---|---|---|\n")


def write_markdown(md_out, summary, rows, trees, mod_arz, base_arz):
    import hashlib
    md5 = hashlib.md5(Path(mod_arz).read_bytes()).hexdigest()
    L = []
    L.append("# BL-AURA-RADIUS audit - every aura-class skill in the effective DB (b57)\n\n")
    L.append("> AUDIT ONLY - no records modified. This is the enumeration + per-aura "
             "ground truth that the `tools/patches/aura_radius.py` registry module will "
             "implement against. Draft-proposal column applies the BL-AURA-RADIUS spec rule "
             "(party auras -> screen-scale 30-45u, pet auras -> >=15-20u); Will decides.\n\n")
    L.append(f"- Effective DB = mod arz OVER base arz (per-record overlay, case-insensitive)\n"
             f"- mod arz: `{mod_arz}` md5 `{md5}` (build40 GOLDEN)\n"
             f"- base arz: `{base_arz}`\n"
             f"- generated by `tools/audit_aura_radius.py` (re-runnable, read-only); "
             f"machine roster: `tools/aura_radius_roster.json`\n\n")

    L.append("## Counts\n\n")
    L.append("| metric | value |\n|---|---|\n")
    for k, v in summary.items():
        L.append(f"| {k} | {v} |\n")
    L.append("\nCategory counts overlap (an aura can be mastery- AND soul-granted). "
             "`current_radius_range` is over player-reachable rows "
             "(MASTERY/SOUL/ITEM/PET); `_all` includes monster auras.\n\n")

    L.append("## Mechanism (ground-truthed on this DB)\n\n")
    L.append("- `Skill_BuffRadiusToggled` (the classic party aura): the radius lives on the "
             "**buffSkillName payload record** (`SkillBuff_Passive.skillTargetRadius`), NOT on "
             "the toggled skill record. Vanilla example: Blade Honing payload = 16.0; DRX cut "
             "Shadow Link's payload to **3.0**.\n"
             "- `Skill_BuffAttackRadiusToggled` / `Skill_BuffAttackRadiusDuration`: radius sits "
             "on the skill record itself (`skillTargetRadius`).\n"
             "- The payload applies to **every friendly in radius** - there is no self-only "
             "channel in these templates. Any NEGATIVE field in the payload therefore widens "
             "onto pets/allies together with the radius (see the negatives section).\n"
             "- `FixedItemSkill_Buff.targetRadius`: scroll/consumable radius buffs.\n"
             "- Records with no explicit radius anywhere: every Templates.arc definition "
             "of `skillTargetRadius` carries an EMPTY defaultValue (engine zero-init), so "
             "no-field == radius 0 == caster-only in practice (flagged `default-0`).\n\n")

    L.append("## Playable trees resolved from `malepc01/femalepc01`\n\n")
    L.append("| slot | tree | record |\n|---|---|---|\n")
    for t, (slot, label) in sorted(trees.items(), key=lambda kv: int(kv[1][0].replace('skillTree', ''))):
        L.append(f"| {slot} | {label} | `{t}` |\n")
    L.append("\n")

    def sect(title, blurb, pred, full=True):
        sel = [r for r in rows if pred(r)]
        L.append(f"## {title} ({len(sel)})\n\n")
        if blurb:
            L.append(blurb + "\n\n")
        if not sel:
            L.append("(none)\n\n")
            return
        L.append(_TABLE_HDR)
        for r in sorted(sel, key=lambda r: (not r['hunting_occult'],
                                            ','.join(r['masteries']), r['norm'])):
            L.append(_mrow(r))
        L.append("\n")

    sect("WILL VETO - Hunting/Occult mastery auras",
         "These belong to Will's HAND-TUNED trees. Under BL-AURA-RADIUS their RADIUS "
         "fields may change (golden-freeze waiver per changed field, justified in "
         "`tools/occult_hunting_golden.json`) - **nothing else on these records**.",
         lambda r: r['hunting_occult'])
    sect("Auras with NEGATIVE payload fields (widen-with-care)",
         "The payload applies to every friendly in radius, so the malus below is "
         "**aura-wide already** - today it just rarely reaches anyone at small radius. "
         "Widening these without a decision spreads the malus onto pets/MP allies. "
         "Flagged, NOT nerfed - Will decides (BL-AURA-RADIUS balance note).",
         lambda r: r['effects_negative'])
    sect("Mastery auras (all trees)", "Granted from a playable skill tree.",
         lambda r: 'MASTERY' in r['category'])
    sect("Soul-granted auras", "Granted by soul rings via itemSkillName/augment.",
         lambda r: 'SOUL' in r['category'] and 'MASTERY' not in r['category'])
    sect("Pet auras (cast by player-summonable pets)",
         "The aura is on the PET's own skill list; the pet is reachable via a "
         "mastery/soul/item summon chain.",
         lambda r: 'PET' in r['category'] and not
         ({'MASTERY', 'SOUL'} & set(r['category'])))
    sect("Item-granted auras (non-soul items, incl. scrolls)", None,
         lambda r: 'ITEM' in r['category'] and not
         ({'MASTERY', 'SOUL', 'PET'} & set(r['category'])))
    sect("Monster-only auras (enemy power - default NO CHANGE)",
         "Cast only by non-summonable monsters. Widening these BUFFS ENEMIES; "
         "excluded from the widening wave unless Will asks.",
         lambda r: r['category'] == ['MONSTER-ONLY'])
    sect("Indirect-only (referenced, but no terminal grantor found)", None,
         lambda r: r['category'] == ['INDIRECT-ONLY'])

    unref = [r for r in rows if r['category'] == ['UNREFERENCED']]
    L.append(f"## Unreferenced duplicates ({len(unref)})\n\n")
    L.append("Dev copies (`skills\\skills\\`, `backup\\`, `old\\`, `copy of`) and "
             "leftovers nothing in the effective DB references. Enumerated for "
             "completeness; default NO CHANGE (dead records).\n\n")
    for r in unref:
        L.append(f"- `{r['record']}` ({r['cls']}, radius {_mradius(r)})\n")
    L.append("\n")

    L.append("## Method + exclusions\n\n")
    L.append("- Sweep is by **Class/template + radius-field presence** over ALL "
             f"{summary['auras_total']} matching records - not by name. Delivery classes: "
             "Skill_BuffRadiusToggled, Skill_BuffAttackRadiusToggled, Skill_BuffRadius, "
             "Skill_BuffAttackRadiusDuration, SkillSecondary_BuffRadius, Skill_AttackBuffRadius; "
             "plus creature/item-attached SkillBuff_Passive(Shield) with explicit radius; plus "
             "FixedItemSkill_Buff with targetRadius>0.\n"
             "- Excluded as NOT friendly-aura-shaped: SkillBuff_Debuf* / SkillBuff_Contageous "
             "(enemy debuffs), Skill_AttackRadius* / Skill_OnHitAttackRadius / "
             "SkillSecondary_AttackRadius (damage novas - radius == damage reach), "
             "Skill_BuffOther / Skill_BuffSelf* (no radius / self-only).\n"
             "- Grantor attribution walks the reverse-reference graph up (depth<=10): playable "
             "trees from the PC records, soul rings (`equipmentring\\soul\\`), items "
             "(itemSkillName/augment), direct creature casters with summon-chain reachability "
             "for pet-vs-monster.\n"
             "- RADIUS FIELDS ONLY will ever be touched by the implementing module - never "
             "damage/values (BL-AURA-RADIUS design discipline #3).\n")
    md_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.write_text(''.join(L), encoding='utf-8')


if __name__ == '__main__':
    main(sys.argv)
