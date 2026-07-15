r"""BL-AURA-RADIUS (b57) - widen friendly aura effect radii so a player's aura
BONUSES reach their PETS in battle (even when not adjacent) and reach ALLIED
PLAYERS on screen in MP.

Will-mandated (docs/BACKLOG.md BL-AURA-RADIUS, 2026-07-12, re-chased 2026-07-14
citing Shadow Link). Motivating case: Shadow Link (DRX cut its payload radius to
3.0) is a party aura almost nobody takes because its reach is tiny.

WHAT THIS MODULE DOES (round 1)
-------------------------------
Grows the RADIUS FIELD ONLY (`skillTargetRadius` / `targetRadius`) of every
player-facing, POSITIVE-only friendly aura to a screen-scale party radius, so the
buff actually reaches pets/allies. It NEVER touches damage/values/effects (design
discipline #3): the only mutation is the single radius float on the payload record.

Data source: `tools/aura_radius_roster.json` (the b57 audit's machine roster -
every aura-class skill in the effective DB, template-classified, with grantor
attribution + full effect list). The plan is DERIVED from that roster + the LIVE
db at build time, so verify() is roster-derived (not a hardcoded list).

TARGET RADII (BL-AURA-RADIUS spec)
----------------------------------
  party auras (MASTERY / SOUL / ITEM grant, or a pet aura that ALSO has a
      player-facing grant)              -> PARTY_RADIUS = 36.0  (screen-scale 30-45u)
  pet-ONLY auras (cast only by a summonable pet, no player-facing grant)
                                        -> PET_RADIUS   = 18.0  (pet-combat 15-20u)
Only GROWS: an aura already at/above its target is left unchanged (never shrunk).

SCOPE / DISCIPLINE (what is HELD or DEFERRED, flagged for Will, NOT applied)
---------------------------------------------------------------------------
The mechanism (ground-truthed in the audit): a radius-buff payload applies to
EVERY friendly in radius - there is no self-only channel - so any NEGATIVE field
in a friendly-buff payload is an ally MALUS that widens onto pets/allies with the
radius. Widening an offensive-radius aura changes how many ENEMIES it hits. Both
are balance changes, so this round HOLDS them and flags them for Will's explicit
decision (BL-AURA-RADIUS balance note: "flag, do not nerf - Will decides"):
  - HOLD negative-payload friendly auras (ally malus would spread).
  - HOLD offensive-radius auras (Skill_BuffAttackRadius* / Skill_AttackBuffRadius:
    widening = combat-power change).
  - DEFER base-only auras: the aura record is not in the mod arz (base-game AE
    artifact/scroll/Neidan auras). Widening them needs an override-clone of the
    base record into the mod arz + the base arz wired into this module - an
    architectural change deferred to a Will-gated round 2.
  - DEFER field-creation (radius-0 self-buffs): a payload with NO radius field is
    a self-only buff (radius 0). ADDING a radius field converts it self->party
    scope - a bigger change than "increase the radius"; deferred + flagged. (E.g.
    Battle Standard's `defaultbuff` is intentionally radius-0; its aura component
    is the separate `triumphbuffradius` at radius 12.)
  - SKIP monster-only / unreferenced / indirect (not player-facing; widening
    would buff enemies or touch dead dev records).

WILL-MANDATED EXCEPTION - Shadow Link (`records\skills\stealth\drxbladehoning.dbr`,
Occult): its payload `drxbladehoningbuff.dbr` carries a NEGATIVE
`defensiveLife = -5/-8/-11/-14` (Vitality-Resistance reduction) that is aura-wide
by template (no self-only channel). Will explicitly named Shadow Link as THE case
to fix, so it IS widened (3.0 -> 36.0) despite the malus. The radius-only edit
cannot split the positive half (mana-regen / life-leech / pierce) from the
negative half by radius, and discipline #3 forbids touching the effect values, so
the -Vitality-Resist now reaches pets/MP allies within 36u alongside the bonuses.
This is called out in docs/reports/b57_aura_radius.md (WILL VETO) so Will can veto
if unintended.

HUNTING / OCCULT (Will's HAND-TUNED trees) - golden-freeze waivers
------------------------------------------------------------------
5 H/O auras are widened this round; 3 of their payloads are frozen in
tools/occult_hunting_golden.json (captured as buffSkillName one-hop payloads of
the Occult/Hunting tree skills). Their radius drift is owner-approved via
`owner_approved_overrides` keys (radius field only; nothing else on the record):
    field::records\skills\hunting\drxartofthehuntbuff.dbr::skillTargetRadius   (15 -> 36)
    field::records\skills\hunting\drxcallofthehuntbuff.dbr::skillTargetRadius   (15 -> 36)
    field::records\skills\stealth\drxbladehoningbuff.dbr::skillTargetRadius     ( 3 -> 36)  [Shadow Link]
The other 2 H/O widened payloads (Occult pet buffs drx_demon_regen_buff.dbr and
skill_shadowformbuff.dbr) are NOT golden-captured, so they need no waiver. Study
Prey + Smoke Screen are the 2 H/O auras HELD this round (negative / offensive).

REGISTRY placement: runs late (after hunting_occult_improvements + boss_skill_fix,
before `visuals`), so a radius edit wins any collision over the aura payloads (none
observed - the collision gate confirms disjointness).

verify() (post-finalization, fail-loud): every roster aura that this module widens
must be >= its target radius on the FINAL assembled db, else SystemExit lists every
offender. Re-derived from the roster, so a later module reverting a radius trips it.
"""
import json
from pathlib import Path

MODULE_NAME = "Aura radius widening (BL-AURA-RADIUS)"

# ── policy ──────────────────────────────────────────────────────────────────
PARTY_RADIUS = 36.0      # screen-scale (spec: 30-45u) - reaches allies on screen
PET_RADIUS = 18.0        # pet-combat range (spec: 15-20u)

_RADIUS_FIELDS = ('skillTargetRadius', 'targetRadius')
_DATA_TYPE_FLOAT = 1

# Offensive-radius delivery classes: the payload is projected onto ENEMIES, so
# widening is a combat-power change (HOLD - Will decides).
_OFFENSIVE_CLASSES = {
    'Skill_BuffAttackRadiusToggled',
    'Skill_BuffAttackRadiusDuration',
    'Skill_AttackBuffRadius',
}

# Will-mandated negative-aura exception (widen despite its ally malus).
_SHADOWLINK = {r'records\skills\stealth\drxbladehoning.dbr'}

_ROSTER = Path(__file__).resolve().parents[1] / 'aura_radius_roster.json'


def _norm(p):
    return str(p).replace('/', '\\').lower().strip()


def _load_roster():
    if not _ROSTER.is_file():
        raise SystemExit(
            "aura_radius: roster missing (%s) - regenerate with "
            "`py tools/audit_aura_radius.py` (the module is roster-derived)" % _ROSTER)
    try:
        return json.loads(_ROSTER.read_text(encoding='utf-8'))['rows']
    except Exception as e:  # noqa: BLE001
        raise SystemExit("aura_radius: roster unreadable (%s): %r" % (_ROSTER, e))


def _player_facing(row):
    return any(c in row['category'] for c in ('MASTERY', 'SOUL', 'ITEM', 'PET'))


def _pet_only(row):
    cats = set(row['category'])
    return 'PET' in cats and not ({'MASTERY', 'SOUL', 'ITEM'} & cats)


def _target(row):
    return PET_RADIUS if _pet_only(row) else PARTY_RADIUS


def _decision(row):
    """widen | hold-neg | hold-off | skip (per the module docstring policy)."""
    if not _player_facing(row):
        return 'skip'
    if _norm(row['norm']) in _SHADOWLINK:
        return 'widen'                     # Will-mandated exception (negative aura)
    if row['effects_negative']:
        return 'hold-neg'                  # ally malus would spread
    if row['cls'] in _OFFENSIVE_CLASSES:
        return 'hold-off'                  # combat-power change
    return 'widen'


def _radius_field(db, canon):
    """(field_name, dtype, current_max) for the record's existing radius field,
    or (None, None, None) if it has no explicit radius field (radius 0)."""
    ff = db.get_fields(canon)
    if not ff:
        return None, None, None
    for key, tf in ff.items():
        fname = key.split('###')[0]
        if fname in _RADIUS_FIELDS:
            vals = [float(v) for v in tf.values if isinstance(v, (int, float))]
            return fname, int(tf.dtype), (max(vals) if vals else 0.0)
    return None, None, None


def build_plan(db):
    """Derive the round-1 plan from the roster + the LIVE db. Deterministic,
    read-only. Returns dict with 'widen' (list of edit dicts) + the held/deferred/
    skipped tallies (rows) for reporting."""
    rows = _load_roster()
    dbmap = {_norm(n): n for n in db.record_names()}
    plan = {'widen': [], 'defer_base': [], 'defer_fieldadd': [],
            'hold_neg': [], 'hold_off': [], 'skip': 0}
    for row in rows:
        d = _decision(row)
        if d == 'skip':
            plan['skip'] += 1
            continue
        if d == 'hold-neg':
            plan['hold_neg'].append(row)
            continue
        if d == 'hold-off':
            plan['hold_off'].append(row)
            continue
        # widen: resolve the record whose radius field we grow. Radius lives on
        # the delivery record itself for 'self' source, else on the buffSkillName
        # payload the audit examined (effect_record). A default-0/template row has
        # no radius field YET, but the record it WOULD live on is that same record,
        # so base-only vs field-creation is classified the same way as a real one.
        src = row['radius_source']
        edit = _norm(row['norm']) if src == 'self' else _norm(row['effect_record'])
        canon = dbmap.get(edit)
        if canon is None:                  # aura record not in the mod arz (base-only)
            plan['defer_base'].append(row)
            continue
        fname, dtype, cur = _radius_field(db, canon)
        if fname is None:                  # in the mod arz but has NO radius field
            plan['defer_fieldadd'].append(row)   # field-creation (self->party scope)
            continue
        plan['widen'].append({
            'delivery': row['norm'], 'edit': canon, 'field': fname, 'dtype': dtype,
            'old': cur, 'target': _target(row), 'ho': row['hunting_occult'],
            'display': row['display'], 'cat': row['category'], 'cls': row['cls'],
            'negative': bool(row['effects_negative']),
        })
    return plan


def apply(db, tags):
    plan = build_plan(db)
    w = plan['widen']
    print("  [aura_radius] plan: widen %d, hold %d neg + %d off, defer %d base-only + "
          "%d field-add, skip %d non-player"
          % (len(w), len(plan['hold_neg']), len(plan['hold_off']),
             len(plan['defer_base']), len(plan['defer_fieldadd']), plan['skip']))
    changed = kept = 0
    for e in sorted(w, key=lambda x: x['edit']):
        if e['old'] >= e['target'] - 1e-6:
            kept += 1                      # already reaches; never shrink
            continue
        val = float(e['target']) if e['dtype'] == _DATA_TYPE_FLOAT else int(e['target'])
        db.set_field(e['edit'], e['field'], val)
        changed += 1
        print("    [SET] %-62s %-16s %g -> %g%s%s"
              % (e['edit'], e['field'], e['old'], e['target'],
                 '  [H/O]' if e['ho'] else '',
                 '  [NEG-aura widened per Will]' if e['negative'] else ''))
    print("  [aura_radius] %d record(s) widened (radius field only), %d already>=target"
          % (changed, kept))


def verify(db, tags):
    """Fail-loud: every roster aura this module widens must be >= its target radius
    on the FINAL assembled db. Re-derived from the roster (build_plan re-reads the
    live radius into 'old'), so a reverted/planted-small radius trips it."""
    plan = build_plan(db)
    offenders = []
    for e in plan['widen']:
        if e['old'] < e['target'] - 1e-6:
            offenders.append(e)
    if offenders:
        lines = ["aura_radius verify FAIL (A-AURA): %d widened aura(s) below target "
                 "radius on the final db:" % len(offenders)]
        for e in sorted(offenders, key=lambda x: x['edit']):
            lines.append("  %-62s %-16s = %g  (< target %g)  [%s]"
                         % (e['edit'], e['field'], e['old'], e['target'], e['display']))
        raise SystemExit("\n".join(lines))
    print("  [aura_radius] verify OK: %d widened aura(s) all >= target radius "
          "(party %g / pet %g)" % (len(plan['widen']), PARTY_RADIUS, PET_RADIUS))
