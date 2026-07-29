#!/usr/bin/env python3
r"""b99 content-wave record-diff: every changed record must be ATTRIBUTABLE to one
of the four merged lanes.

Usage:
  py tools/debug/b99_record_diff.py <baseline.arz> <built.arz>

Baseline = a build of `main` (a0276ab). Built = a build of integration/content-wave
(main + feat/death-xp-penalty + feat/sargath-soul + feat/vashkarr-soul +
fix/soul-identity).

Prints ADDED / REMOVED / CHANGED with field-level before -> after, then buckets
every delta into a lane by an ATTRIBUTION RULE derived from that lane's own stated
scope. Exit 1 if any record/field cannot be attributed - an unexplained delta is a
NO-GO condition for the wave.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase  # noqa: E402


def norm(s):
    return s.lower().replace('/', '\\')


# ── ATTRIBUTION RULES ───────────────────────────────────────────────────────
# (lane, record-predicate, allowed-field-predicate). First match wins; a delta
# that matches no rule is UNATTRIBUTED and fails the gate.
_SARGOTH_NEW = re.compile(
    r'^records\\skills\\soulskills\\(pets\\sargoth_[123]|summon_sargoth)\.dbr$', re.I)
_VASHKARR = re.compile(r'^records\\item\\equipmentring\\soul\\svc_uber\\vashkarr_soul_[nel]\.dbr$', re.I)
# NB: the family includes SV's shipped Dropbox artefact
# "sargoth_soul_n (amgoz-qosmio's conflicted copy 2013-08-07).dbr" - the module
# wires 4 records, not 3, so the rule must not anchor on a bare _[nel].dbr tail.
_SARGOTH_SOULS = re.compile(r'^records\\item\\equipmentring\\soul\\dragonian\\sargoth_soul_[nel]\b.*\.dbr$', re.I)

def _ANY_RECORD(_r):
    """Sentinel record-predicate for a FIELD-scoped rule (see attribute())."""
    return True


RULES = [
    ('b93 death-xp-penalty',
     lambda r: r == r'records\xpack\game\gameengine.dbr',
     lambda f: f in {'deathPenaltyEquation', 'deathPenaltyMax'}),

    ('b95 sargoth-soul (new pet/skill records)',
     lambda r: bool(_SARGOTH_NEW.match(r)),
     lambda f: True),

    ('b95 sargoth-soul (itemSkill wiring on the 3 SV-original soul tiers)',
     lambda r: bool(_SARGOTH_SOULS.match(r)),
     lambda f: f in {'itemSkillName', 'itemSkillLevel'}),

    ('b96 vashkarr-soul (retune)',
     lambda r: bool(_VASHKARR.match(r)),
     lambda f: True),

    # soul_identity is scoped by FIELD, not by path: it may zero
    # chanceToEquipFinger2 on any live soul carrier anywhere in the roster.
    ('b97 soul-identity (detach the identity thieves)',
     _ANY_RECORD,
     lambda f: f == 'chanceToEquipFinger2'),
]


def attribute(rec, fields):
    """-> (lane, unattributed_fields). lane None when nothing matches.

    `fields` is empty for an ADDED record. The soul_identity rule matches ANY
    record (it is field-scoped, not path-scoped), so without this guard it would
    silently absorb every added record into the wrong bucket - a mis-attribution
    is as bad as a missed one here, since the whole point is naming the owner.
    An added record must therefore match a rule on its PATH.
    """
    for lane, rec_ok, fld_ok in RULES:
        if not fields and rec_ok is _ANY_RECORD:
            continue
        if rec_ok(rec):
            bad = {f for f in fields if not fld_ok(f)}
            if not bad:
                return lane, set()
            # record matched but some fields are out of that lane's scope: try
            # a later rule for the leftovers (e.g. soul_identity's field rule).
            for lane2, rec_ok2, fld_ok2 in RULES:
                if lane2 is lane:
                    continue
                if rec_ok2(rec) and all(fld_ok2(f) for f in bad):
                    return lane + ' + ' + lane2, set()
            return lane, bad
    return None, set(fields)


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    base = ArzDatabase.from_arz(Path(argv[0]))
    built = ArzDatabase.from_arz(Path(argv[1]))

    bmap = {norm(n): n for n in base.record_names()}
    tmap = {norm(n): n for n in built.record_names()}
    bnames, tnames = set(bmap), set(tmap)
    added = sorted(tnames - bnames)
    removed = sorted(bnames - tnames)

    def val(f, k):
        return (f[k].dtype, list(f[k].values)) if k in f else None

    changed = {}
    for n in sorted(bnames & tnames):
        fb = base.get_fields(bmap[n]) or {}
        ft = built.get_fields(tmap[n]) or {}
        d = {}
        for k in sorted(set(fb) | set(ft)):
            vb, vt = val(fb, k), val(ft, k)
            if vb != vt:
                d[k] = (vb, vt)
        if d:
            changed[n] = d

    print('=' * 78)
    print('b99 CONTENT-WAVE RECORD DIFF')
    print('  baseline : %s' % argv[0])
    print('  built    : %s' % argv[1])
    print('  records  : baseline %d -> built %d' % (len(bnames), len(tnames)))
    print('  ADDED %d / REMOVED %d / CHANGED %d' % (len(added), len(removed), len(changed)))
    print('=' * 78)

    buckets = defaultdict(list)
    unattributed = []

    for n in added:
        lane, bad = attribute(n, set())
        if lane is None:
            unattributed.append(('ADDED', n, set()))
        else:
            buckets[lane].append('ADDED   ' + n)

    for n in removed:
        unattributed.append(('REMOVED', n, set()))

    for n, d in changed.items():
        lane, bad = attribute(n, set(d))
        if lane is None or bad:
            unattributed.append(('CHANGED', n, bad or set(d)))
            if lane:
                buckets[lane].append('CHANGED ' + n + '  (PARTIAL - see unattributed)')
        else:
            buckets[lane].append('CHANGED ' + n + '  [' + ', '.join(sorted(d)) + ']')

    print('\n--- ATTRIBUTION BY LANE ---')
    for lane in sorted(buckets):
        print('\n[%s]  %d record(s)' % (lane, len(buckets[lane])))
        for line in buckets[lane][:40]:
            print('   ' + line)
        if len(buckets[lane]) > 40:
            print('   ... +%d more' % (len(buckets[lane]) - 40))

    print('\n--- FIELD DETAIL (changed records) ---')
    for n, d in changed.items():
        print('\n  %s' % n)
        for k, (vb, vt) in d.items():
            print('     %-28s %r -> %r' % (k, vb, vt))

    print('\n' + '=' * 78)
    if unattributed:
        print('UNATTRIBUTED DELTAS: %d  ** NO-GO **' % len(unattributed))
        for kind, n, bad in unattributed:
            print('   %-8s %s %s' % (kind, n, ('fields=' + ','.join(sorted(bad))) if bad else ''))
        return 1
    print('RESULT: PASS - every added/removed/changed record is attributable to one '
          'of the four merged lanes.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
