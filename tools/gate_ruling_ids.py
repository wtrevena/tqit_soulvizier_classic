#!/usr/bin/env python3
r"""GATE: a ruling NUMBER means exactly one ruling (rulings-ledger process law 1).

THE DEFECT CLASS
----------------
`docs/WILL_RULINGS.md` is the design law of record, and every ledger reference - the
BACKLOG lane records, the debt ids (`BL-R<n>-DEBT-*`), the in-code `R-<n>:` comments
that tell a later implementer why a line exists - is keyed by the ruling NUMBER. The
number is the primary key. If two rulings share it, every one of those references
becomes ambiguous and the ledger stops being a ledger.

Numbers are allocated by reading the tail of `WILL_RULINGS.md`, which is correct for a
single worktree and wrong for this repo: lanes run in PARALLEL worktrees, each branched
from the same main, each reading the same tail, each therefore picking the same next
number. Measured on 2026-08-14 while implementing R-253: main topped out at R-249, and
of the in-flight branches FOUR had independently claimed R-250
(`fix/boss-arena-spawn-and-polish`, `fix/chest-generosity-shared-cause`,
`fix/toxeus-boss-equipment-and-soul`, `fix/toxeus-shroud`) and TWO had claimed R-251
(`fix/death-penalty-halve-again`, `fix/toxeus-boss-equipment-and-soul`). Two of the
R-250 claimants were semantically coupled - one lane opted its new chest INTO the exact
mechanism the other lane exists to delete - so merging both as written would have left
one number denoting two rulings that disagree.

Nothing detected this. The collision is invisible inside any single worktree, which is
the only place a lane ever looks. So it is checked here instead, mechanically.

THE INVARIANT
-------------
  A1 UNIQUE IN FILE : no ruling number appears twice as a `## R-<n>` heading.
  A2 NO BASE CLASH  : (--vs <ref>) every ruling this branch ADDS is absent from <ref>.
                      Renumbering after the fact is cheap; discovering the clash after
                      the merge is not.
  A3 NO LANE CLASH  : (--branches) no OTHER branch claims a number this branch adds.
                      Claims are read from both the ledger headings and the `R-<n>`
                      stamps in `tools/`, because a lane often stamps its number all
                      through its code before it writes the ruling text.
A1 always runs. A2/A3 need git and are skipped (loudly, never silently) without it.

USAGE
  py tools/gate_ruling_ids.py
  py tools/gate_ruling_ids.py --vs origin/main --branches
  py tools/gate_ruling_ids.py --negtest
"""
import re
import sys
import argparse
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = 'docs/WILL_RULINGS.md'

# A PRIMARY ruling heading is `## R-<n> [<date>] ...`. The ledger deliberately reuses a
# number for CONTINUATIONS of the same ruling - `## R-140 AMENDMENT [...]`,
# `## R-170 FOLLOW-UP - SHIP RECORD [...]`, `## R-181 SECOND AMENDMENT [...]` - and for
# multi-number wave headings - `## R-120..R-123 + R-125 [...]`,
# `## R-184/185/186 SHIPPED ADDENDUM (...)`. Those are the ledger working as designed
# (retirement protocol: intent stays legible), NOT collisions, and every one of them is
# excluded by requiring whitespace-then-`[` straight after the number. Measured: on the
# 2026-08-14 ledger this pattern yields 5 fewer false duplicates and zero real ones.
HEADING_RE = re.compile(r'^##\s+R-(\d+)\s+\[', re.M)
STAMP_RE = re.compile(r'\bR-(\d{3})\b')


# ── pure cores (negtestable without git or the filesystem) ───────────────────────────
def duplicate_ids(text):
    """A1: [(id, count)] for every ruling heading number used more than once."""
    seen = {}
    for m in HEADING_RE.finditer(text):
        seen[int(m.group(1))] = seen.get(int(m.group(1)), 0) + 1
    return sorted((i, n) for i, n in seen.items() if n > 1)


def heading_ids(text):
    return {int(m.group(1)) for m in HEADING_RE.finditer(text)}


def _added(mine, base):
    """The ruling numbers this ledger defines that the base ledger does not."""
    return heading_ids(mine) - heading_ids(base)


def lane_clashes(added, claims_by_branch, me):
    """A3: {id: [other branches claiming it]} for ids this branch adds."""
    out = {}
    for rid in sorted(added):
        others = sorted(b for b, ids in claims_by_branch.items()
                        if b != me and rid in ids)
        if others:
            out[rid] = others
    return out


# ── git plumbing ─────────────────────────────────────────────────────────────────────
def _git(*args):
    return subprocess.run(('git',) + args, cwd=REPO, capture_output=True,
                          text=True, encoding='utf-8', errors='replace')


def _show(ref, path):
    r = _git('show', f'{ref}:{path}')
    return r.stdout if r.returncode == 0 else None


def current_branch():
    r = _git('rev-parse', '--abbrev-ref', 'HEAD')
    return r.stdout.strip() if r.returncode == 0 else '(detached)'


def branch_claims():
    """{branch: {ruling ids it mentions}} over every local branch - ledger headings
    plus R-<n> stamps under tools/ (lanes stamp code before they write the ruling)."""
    r = _git('branch', '--format=%(refname:short)')
    if r.returncode != 0:
        return None
    claims = {}
    for b in [x.strip() for x in r.stdout.splitlines() if x.strip()]:
        ids = set()
        txt = _show(b, LEDGER)
        if txt:
            ids |= heading_ids(txt)
        g = _git('grep', '-h', '-o', '-E', r'\bR-[0-9]{3}\b', b, '--', 'tools/')
        if g.returncode == 0:
            ids |= {int(s.split('-')[1]) for s in g.stdout.split()}
        claims[b] = ids
    return claims


# ── driver ───────────────────────────────────────────────────────────────────────────
def run(vs=None, branches=False, verbose=True):
    problems = []
    path = REPO / LEDGER
    if not path.exists():
        return [f'{LEDGER} not found at {path}']
    mine = path.read_text(encoding='utf-8', errors='replace')
    ids = heading_ids(mine)

    for rid, n in duplicate_ids(mine):
        problems.append(f'A1: R-{rid} appears {n} times as a `## R-{rid}` heading in '
                        f'{LEDGER}. One number, one ruling.')

    added = set()
    if vs:
        base = _show(vs, LEDGER)
        if base is None:
            problems.append(f'A2: cannot read {LEDGER} at {vs} - resolve the ref or '
                            f'drop --vs; skipping silently is how the ledger rots.')
        else:
            base_ids = heading_ids(base)
            added = ids - base_ids
            # an id "added" here that ALSO exists there is impossible by set algebra;
            # the real clash is a heading whose TEXT differs for the same number.
            for rid in sorted(ids & base_ids):
                a = _section(mine, rid)
                b = _section(base, rid)
                if a and b and a.split('\n', 1)[0] != b.split('\n', 1)[0]:
                    problems.append(
                        f'A2: R-{rid} exists in {vs} with a DIFFERENT title - this '
                        f'branch reused a number that was already taken.\n'
                        f'       here: {a.splitlines()[0][:110]}\n'
                        f'       {vs}: {b.splitlines()[0][:110]}')

    if branches:
        claims = branch_claims()
        me = current_branch()
        if claims is None:
            problems.append('A3: git branch enumeration failed; cannot check for '
                            'parallel-lane collisions.')
        else:
            if not added:
                base = _show(vs, LEDGER) if vs else None
                added = ids - heading_ids(base) if base else set()
            clash = lane_clashes(added, claims, me)
            for rid, others in clash.items():
                problems.append(
                    f'A3: R-{rid} is also claimed by {", ".join(others)}. Parallel '
                    f'lanes each read the same ledger tail and pick the same next '
                    f'number; one of them must renumber BEFORE integration, and the '
                    f'two rulings must cross-reference.')
            if verbose:
                print(f'  branch claims scanned: {len(claims)} branches; this branch '
                      f'({me}) adds {sorted(added) or "none"}')
    if verbose:
        print(f'GATE ruling-ids: {LEDGER} defines {len(ids)} rulings '
              f'(highest R-{max(ids) if ids else 0})')
    return problems


def _section(text, rid):
    m = re.search(r'^##\s+R-%d\b.*?(?=^##\s+R-\d|\Z)' % rid, text, re.M | re.S)
    return m.group(0) if m else None


def negtest():
    """Planted negatives. Each must be CAUGHT by the pure cores - no git, no files."""
    good = ('## R-248 [x] A\ntext\n\n## R-249 [y] B\ntext\n\n## R-253 [z] C\ntext\n')
    dup = ('## R-248 [x] A\ntext\n\n## R-250 [y] B\ntext\n\n## R-250 [z] C\ntext\n')
    base = ('## R-248 [x] A\ntext\n\n## R-249 [y] B\ntext\n')
    cases = [
        ('N1 the same number used twice in one ledger', bool(duplicate_ids(dup))),
        ('N1b a clean ledger is NOT flagged', not duplicate_ids(good)),
        ('N2 a number added here that another lane also claims',
         bool(lane_clashes(_added(good, base),
                           {'lane-a': {253}, 'lane-b': {251}}, 'lane-b'))),
        ('N2b the same add with no other claimant is NOT flagged',
         not lane_clashes(_added(good, base),
                          {'lane-a': {240}, 'lane-b': {251}}, 'lane-b')),
        # N1c guards the tightening itself: the ledger's amendment/follow-up/wave
        # headings reuse a number ON PURPOSE and must never read as a collision, but a
        # real second PRIMARY heading for the same number still must (N1 above), so the
        # exclusion cannot have been bought by blinding the check.
        ('N1c amendment / follow-up / wave headings are NOT collisions',
         not duplicate_ids(
             '## R-140 [2026-07-30] IMPLEMENTED - x\ntext\n\n'
             '## R-140 AMENDMENT [2026-07-30] Three corrections\ntext\n\n'
             '## R-170 [2026-08-06] IMPLEMENTED - y\ntext\n\n'
             '## R-170 FOLLOW-UP - SHIP RECORD [2026-08-10] b63\ntext\n\n'
             '## R-181 SECOND AMENDMENT [2026-08-11] IMPLEMENTED\ntext\n\n'
             '## R-120..R-123 + R-125 [2026-07-30] - wave\ntext\n\n'
             '## R-184/185/186 SHIPPED ADDENDUM (2026-08-11)\ntext\n')),
        ('N3 the historical 2026-08-14 four-way R-250 collision would be caught',
         len(lane_clashes({250},
                          {'fix/boss-arena-spawn-and-polish': {250},
                           'fix/chest-generosity-shared-cause': {250},
                           'fix/toxeus-boss-equipment-and-soul': {250, 251},
                           'fix/toxeus-shroud': {250}},
                          'fix/boss-arena-spawn-and-polish')[250]) == 3),
    ]
    ok = True
    for label, caught in cases:
        print(f'  {"CAUGHT " if caught else "MISSED "} {label}'
              + ('' if caught else '   <-- THE GATE IS BLIND HERE'))
        ok = ok and caught
    live = run(verbose=False)
    print(f'  {"PASS   " if not live else "FAIL   "} P0 this ledger is clean')
    for p in live:
        print(f'      - {p}')
    return ok and not live


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--vs', help='base ref to compare the ledger against (e.g. main)')
    ap.add_argument('--branches', action='store_true',
                    help='also check every local branch for the same claim')
    ap.add_argument('--negtest', action='store_true')
    a = ap.parse_args()
    if a.negtest:
        print('GATE ruling-ids NEGTEST')
        return 0 if negtest() else 1
    problems = run(a.vs, a.branches)
    if problems:
        print(f'\nGATE ruling-ids: FAIL ({len(problems)} problem(s))')
        for p in problems:
            print(f'  - {p}')
        return 1
    print('GATE ruling-ids: PASS - every ruling number denotes exactly one ruling')
    return 0


if __name__ == '__main__':
    sys.exit(main())
