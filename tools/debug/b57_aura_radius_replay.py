r"""b57 dry-run replay + fail-loud proof for tools/patches/aura_radius (no heavy build).

Applies aura_radius over a COPY of the build40 GOLDEN .arz (b33c5a44 - the FINAL
post-monolith+registry state the module sees, since it runs just before `visuals`)
and proves, read-only against the input:

  1. apply() widens exactly the roster-derived plan (party->36u / pet->18u);
  2. verify() (roster-derived, fail-loud) PASSES on the widened db;
  3. IDEMPOTENCY: a 2nd apply() is a no-op (0 SET);
  4. RADIUS-ONLY + INTENDED-RECORDS-ONLY diff vs the pristine golden: every
     modified record differs in ONLY its radius field (skillTargetRadius/
     targetRadius), no other field, no record added/removed;
  5. re-audit: every widened aura is >= its target radius;
  6. NEGATIVE test: planting a small radius on one widened record makes verify()
     fail loud (proving the guard actually guards).

Usage:  py tools/debug/b57_aura_radius_replay.py [built.arz]  [--report <md>]
Default arz: <main repo>\work\SoulvizierClassic\Database\SoulvizierClassic.arz.
Deterministic. --report writes the full old->new table (the Will-veto artifact).
"""
import io
import contextlib
import hashlib
import os
import re
import sys
from pathlib import Path

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_TOOLS, os.path.join(_TOOLS, 'patches')):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from arz_patcher import ArzDatabase          # noqa: E402
import patches.aura_radius as AR             # noqa: E402

_DEFAULT_ARZ = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic"
                    r"\work\SoulvizierClassic\Database\SoulvizierClassic.arz")


def _field_map(db, rec):
    """{fieldName: (dtype, tuple(values))} with ### keys merged in encounter order
    (mirrors validate_mastery_golden._field_map so 'only radius changed' is exact)."""
    out = {}
    ff = db.get_fields(rec)
    if not ff:
        return out
    for key, tf in ff.items():
        fname = key.split('###')[0]
        vals = [repr(round(v, 6)) if isinstance(v, float) else str(v) for v in tf.values]
        if fname in out:
            out[fname] = (out[fname][0], out[fname][1] + tuple(vals))
        else:
            out[fname] = (int(tf.dtype), tuple(vals))
    return out


def main():
    arz = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith('--') \
        else _DEFAULT_ARZ
    report = None
    if '--report' in sys.argv:
        report = Path(sys.argv[sys.argv.index('--report') + 1])
    if not arz.exists():
        print('golden arz not found: %s' % arz)
        sys.exit(2)
    md5 = hashlib.md5(arz.read_bytes()).hexdigest()
    print('golden arz : %s' % arz)
    print('golden md5 : %s' % md5)

    ref = ArzDatabase.from_arz(arz)     # pristine reference (never mutated)
    work = ArzDatabase.from_arz(arz)    # working copy

    plan = AR.build_plan(work)
    print('\n########## PLAN (roster-derived) ##########')
    print('  widen            : %d' % len(plan['widen']))
    print('  hold negative    : %d' % len(plan['hold_neg']))
    print('  hold offensive   : %d' % len(plan['hold_off']))
    print('  defer base-only  : %d' % len(plan['defer_base']))
    print('  defer field-add  : %d' % len(plan['defer_fieldadd']))
    print('  skip non-player  : %d' % plan['skip'])

    print('\n########## APPLY ##########')
    AR.apply(work, {})
    print('\n########## verify() (roster-derived, fail-loud) ##########')
    AR.verify(work, {})

    print('\n########## IDEMPOTENCY (2nd apply -> 0 SET) ##########')
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        AR.apply(work, {})
    n_set2 = sum(1 for ln in buf.getvalue().splitlines() if '[SET]' in ln)
    print('2nd apply SET edits: %d (expect 0)' % n_set2)

    print('\n########## RADIUS-ONLY + INTENDED-RECORDS-ONLY DIFF ##########')
    modified = sorted(work._modified)
    edit_set = {p['edit'] for p in plan['widen'] if p['old'] < p['target'] - 1e-6}
    only_radius = True
    ghost = set(modified) - edit_set
    missing = edit_set - set(modified)
    if ghost:
        only_radius = False
        print('  !!! UNEXPECTED modified records (not in plan): %s' % sorted(ghost)[:8])
    if missing:
        only_radius = False
        print('  !!! PLANNED edits NOT modified: %s' % sorted(missing)[:8])
    recs_added_removed = set(work.record_names()) ^ set(ref.record_names())
    if recs_added_removed:
        only_radius = False
        print('  !!! records ADDED/REMOVED: %s' % sorted(recs_added_removed)[:8])
    bad_field = []
    for rec in modified:
        fref, fwork = _field_map(ref, rec), _field_map(work, rec)
        diff = {k for k in set(fref) | set(fwork) if fref.get(k) != fwork.get(k)}
        if diff - set(AR._RADIUS_FIELDS):
            bad_field.append((rec, sorted(diff)))
    if bad_field:
        only_radius = False
        for rec, d in bad_field[:8]:
            print('  !!! %s changed non-radius field(s): %s' % (rec, d))
    print('  modified records            : %d' % len(modified))
    print('  all in the intended plan    : %s' % (not ghost and not missing))
    print('  records added/removed       : %d' % len(recs_added_removed))
    print('  changed ONLY a radius field : %s' % (not bad_field))

    print('\n########## RE-AUDIT (every widened aura >= target) ##########')
    reaudit = AR.build_plan(work)
    below = [p for p in reaudit['widen'] if p['old'] < p['target'] - 1e-6]
    print('  widened auras below target  : %d (expect 0)' % len(below))

    print('\n########## NEGATIVE TEST (plant small radius -> verify must FAIL) ##########')
    widenable = [p for p in plan['widen'] if p['old'] < p['target'] - 1e-6]
    # Prefer Shadow Link (Will's motivating case) as the victim for a clear proof.
    victim = next((p for p in widenable if 'drxbladehoningbuff' in p['edit']), widenable[0])
    work.set_field(victim['edit'], victim['field'],
                   float(1.0) if victim['dtype'] == AR._DATA_TYPE_FLOAT else 1)
    caught = False
    try:
        AR.verify(work, {})
    except SystemExit as e:
        caught = 'below target' in str(e)
        print('  verify() correctly RAISED on %s:' % victim['edit'])
        for ln in str(e).splitlines()[:3]:
            print('    ' + ln)
    print('  NEGATIVE TEST:', 'PASS' if caught else 'FAIL')

    ok = (n_set2 == 0 and only_radius and not below and caught)
    print('\nRESULT:', 'PASS' if ok else 'FAIL')

    if report is not None:
        _write_report(report, arz, md5, plan)
        print('wrote report %s' % report)
    sys.exit(0 if ok else 1)


def _grantor(p):
    return '+'.join(k for k in ('MASTERY', 'SOUL', 'ITEM', 'PET') if k in p['cat'])


def _label(display, record):
    """A readable aura label: the display name when it reads like a proper skill
    NAME (letters/spaces/apostrophes/hyphens, not a sentence/stat/ALLCAPS/dev-note),
    else the record basename. Cosmetic only - the record path is authoritative."""
    base = record.rsplit('\\', 1)[-1]
    if base.endswith('.dbr'):
        base = base[:-4]
    d = (display or '').strip()
    if d and len(d) <= 28 and not d.isupper() and re.match(r"^[A-Za-z][A-Za-z '\-]+$", d):
        return d
    return base


def _off_effects(r):
    """Short offensive-effect summary for a debuf payload (proves it is enemy-facing)."""
    hits = [e for e in (r.get('effects_positive') or []) if e.startswith('offensive')]
    return '; '.join(hits[:3]) + (' ...' if len(hits) > 3 else '')


def _write_report(path, arz, md5, plan):
    """Emit the full old->new widen table + held/deferred lists (the Will veto)."""
    changed = sorted((p for p in plan['widen'] if p['old'] < p['target'] - 1e-6),
                     key=lambda p: (not p['ho'], p['edit']))
    L = []
    L.append('<!-- generated by tools/debug/b57_aura_radius_replay.py --report -->\n')
    L.append('### Full widen table (%d records, radius field only)\n\n' % len(changed))
    L.append('| # | aura | edit record (payload) | field | old | new | grant | H/O | neg |\n')
    L.append('|---|---|---|---|---|---|---|---|---|\n')
    for i, p in enumerate(changed, 1):
        L.append('| %d | %s | `%s` | %s | %g | %g | %s | %s | %s |\n'
                 % (i, _label(p['display'], p['edit']), p['edit'], p['field'],
                    p['old'], p['target'],
                    _grantor(p), 'Y' if p['ho'] else '', 'Y' if p['negative'] else ''))
    L.append('\n### HELD - negative-payload friendly auras (ally malus would spread; Will decides) (%d)\n\n'
             % len(plan['hold_neg']))
    L.append('| aura | record | class | grant |\n|---|---|---|---|\n')
    for r in sorted(plan['hold_neg'], key=lambda r: r['norm']):
        L.append('| %s | `%s` | %s | %s |\n'
                 % (_label(r['display'], r['record']), r['record'], r['cls'],
                    '+'.join(k for k in ('MASTERY', 'SOUL', 'ITEM', 'PET') if k in r['category'])))
    L.append('\n### HELD - offensive-radius auras (combat-power change; Will decides) (%d)\n\n'
             % len(plan['hold_off']))
    L.append("Two kinds: (a) offensive DELIVERY class (`Skill_BuffAttackRadius*` / "
             "`Skill_AttackBuffRadius` - radius sits on the attack skill), and (b) offensive "
             "PAYLOAD (round-2 guard) - a friendly-looking `Skill_BuffRadius`/`Toggled` "
             "delivery whose `buffSkillName` payload is an enemy debuf (`SkillBuff_Debuf` / "
             "`debufSkill=1`); its `skillTargetRadius` is DAMAGE/DEBUF reach. Both = combat "
             "power; widened only if Will asks.\n\n")
    L.append('| aura | delivery record | delivery class | grant | held because |\n'
             '|---|---|---|---|---|\n')
    for r in sorted(plan['hold_off'], key=lambda r: r['norm']):
        reason = r.get('_hold_reason', 'offensive delivery class')
        if reason.startswith('payload'):
            eff = _off_effects(r)
            if eff:
                reason = '%s (%s)' % (reason, eff)
        L.append('| %s | `%s` | %s | %s | %s |\n'
                 % (_label(r['display'], r['record']), r['record'], r['cls'],
                    '+'.join(k for k in ('MASTERY', 'SOUL', 'ITEM', 'PET') if k in r['category']),
                    reason))
    L.append('\n### DEFERRED - base-only (needs an override-clone; round 2) (%d)\n\n'
             % len(plan['defer_base']))
    for r in sorted(plan['defer_base'], key=lambda r: r['norm']):
        L.append('- `%s` (%s, %s)\n' % (r['record'], r['cls'], r['display']))
    L.append('\n### DEFERRED - field-creation (radius-0 self-buff; scope change; round 2) (%d)\n\n'
             % len(plan['defer_fieldadd']))
    for r in sorted(plan['defer_fieldadd'], key=lambda r: r['norm']):
        L.append('- `%s` (%s, %s)\n' % (r['record'], r['cls'], r['display']))
    path.write_text(''.join(L), encoding='utf-8')


if __name__ == '__main__':
    main()
