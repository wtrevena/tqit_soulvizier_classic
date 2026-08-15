#!/usr/bin/env python3
r"""GATE: is this ship dispatch describing work that ALREADY SHIPPED? (ship-procedure step 0)

THE DEFECT CLASS
----------------
A ship lane is dispatched from an ORCHESTRATOR BOARD, and in this repo a stale board is
the normal case, not the exception - parallel lanes advance `main` between the moment a
dispatch is written and the moment it runs. Three consecutive ship dispatches in
2026-08-15 were spent on work that was already live:

  `enslaver-shroud-ship-r250`        asked to merge `fix/toxeus-shroud` and tag build93.
                                     Its tip was already an ancestor of main; build93
                                     had shipped; main was 4 builds ahead.
  `dev-parity-r249-testhub-quests`   asked to deploy a TESTHUB `Quests.arc` because DEV
                                     "hashes `1764c3a2`". DEV actually hashed `d9f8c316`
                                     (build97). Executing it would have REVERTED Will's
                                     play surface off build97 and broken the Levels+Quests
                                     coupling.
  `chest-generosity-shared-cause`    asked to merge + ship a branch that had shipped as
                                     build95, with build96 and build97 already on top.

Each was caught by hand, by an operator who happened to look. `BL-b98-DEBT-1` asked for
the branch/tag half of that check to be mechanical; `BL-b98-DEBT-2` observed that the
branch half is not sufficient, because a dispatch can carry no branch at all and go stale
on an ARTIFACT HASH instead. This is both halves, mechanical, run BEFORE any merge or
build - the cheapest step in the procedure and the only one that can save all the rest.

A green result here is NOT permission to ship. It only says the dispatch is not already
done, which is the question that must be answered before the expensive questions.

THE INVARIANT
-------------
  S1 LANE CONTAINMENT : (--lane <ref>) the lane tip is NOT already an ancestor of the
                        integration branch. If it is, the merge is a no-op and any build
                        would re-ship identical content under a wrong build number.
  S2 TAG FREE         : (--tag <name>) the intended tag does not already exist, locally
                        or on the remote. The next free build number is always reported.
  S3 HASH TRUTH       : (--claim <path>=<md5>) every artifact hash the dispatch QUOTES is
                        what is actually on disk right now. A dispatch that reasons from
                        a hash which is no longer deployed is reasoning about the past.
  S4 TREE STATE       : the working tree is clean and the integration branch is not
                        behind its remote. A ship never starts from an unknown tree.

S1/S2/S4 need git and fail LOUD (never silently skip) when it is unavailable.

USAGE
  py tools/gate_already_shipped.py --lane fix/chest-generosity-shared-cause --tag build98-ship
  py tools/gate_already_shipped.py --claim "<dev>/Resources/Quests.arc=1764c3a2..."
  py tools/gate_already_shipped.py --negtest
"""
import re
import sys
import hashlib
import argparse
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MAIN = 'main'
BUILD_TAG_RE = re.compile(r'^build(\d+)-(ship|dev)$')


# ── pure cores (negtestable without git or the filesystem) ────────────────────────────
def next_build_number(tags):
    """S2: the next free build number from the tag history. build94-dev consumed 94 even
    though Steam skipped it, so DEV-only tags count - numbers are consumed, not shipped."""
    ns = [int(m.group(1)) for m in (BUILD_TAG_RE.match(t.strip()) for t in tags) if m]
    return (max(ns) + 1) if ns else 1


def tag_is_taken(tags, name):
    """S2: True when the intended tag name already exists in the given tag list."""
    return name.strip() in {t.strip() for t in tags}


def containment_problem(lane, contained, merge_commit=None, containing_tag=None):
    """S1: the abort message when a lane tip is already contained, else None."""
    if not contained:
        return None
    where = []
    if merge_commit:
        where.append(f'merged at {merge_commit}')
    if containing_tag:
        where.append(f'shipped as {containing_tag}')
    tail = (' (' + ', '.join(where) + ')') if where else ''
    return (f'S1: `{lane}` is ALREADY an ancestor of `{MAIN}`{tail}. There is nothing to '
            f'merge, so a build here would re-ship identical content under a build number '
            f'that is either taken or wrong. ABORT and re-verify the board against the '
            f'repo before doing anything else.')


def stale_claims(claims, hasher):
    """S3: [(path, quoted, actual)] for every quoted hash that is not what is on disk.
    `hasher` maps a path to its md5, or None when the file does not exist. A short quoted
    hash is compared on its own length, so an 8-char board excerpt still checks out."""
    out = []
    for path, quoted in claims:
        actual = hasher(path)
        q = quoted.strip().lower()
        if actual is None:
            out.append((path, q, None))
        elif not actual.lower().startswith(q):
            out.append((path, q, actual.lower()))
    return out


# ── git plumbing ─────────────────────────────────────────────────────────────────────
def _git(*args):
    return subprocess.run(('git',) + args, cwd=REPO, capture_output=True,
                          text=True, encoding='utf-8', errors='replace')


def _ok(*args):
    r = _git(*args)
    return r.stdout.strip() if r.returncode == 0 else None


def md5_of(path):
    p = Path(path)
    if not p.is_file():
        return None
    h = hashlib.md5()
    with p.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b''):
            h.update(chunk)
    return h.hexdigest()


def local_tags():
    out = _ok('tag', '--list')
    return out.splitlines() if out else []


def remote_tags():
    out = _ok('ls-remote', '--tags', 'origin')
    if out is None:
        return None
    names = set()
    for line in out.splitlines():
        parts = line.split('refs/tags/')
        if len(parts) == 2:
            names.add(parts[1].replace('^{}', '').strip())
    return sorted(names)


def _contained(lane):
    """(resolved_sha, is_ancestor_of_main) or (None, None) when the ref does not resolve."""
    sha = _ok('rev-parse', '--verify', f'{lane}^{{commit}}')
    if sha is None:
        return None, None
    r = _git('merge-base', '--is-ancestor', sha, MAIN)
    return sha, (r.returncode == 0)


def _merge_commit_for(sha):
    out = _ok('log', '--merges', '--ancestry-path', '--format=%h %s', f'{sha}..{MAIN}')
    return out.splitlines()[-1] if out else None


def _containing_tag(sha):
    out = _ok('tag', '--contains', sha, '--sort=creatordate')
    lines = [x for x in (out.splitlines() if out else []) if BUILD_TAG_RE.match(x.strip())]
    return lines[0].strip() if lines else None


# ── driver ───────────────────────────────────────────────────────────────────────────
def run(lane=None, tag=None, claims=(), verbose=True):
    problems = []
    if _ok('rev-parse', '--git-dir') is None:
        return ['git is unavailable, so S1/S2/S4 cannot be answered. Refusing to report '
                'a PASS that was never measured.']

    tags = local_tags()
    rtags = remote_tags()
    nxt = next_build_number(tags if rtags is None else sorted(set(tags) | set(rtags)))
    if verbose:
        print(f'  tag history: {len(tags)} local tag(s); next free build number = {nxt}')

    if lane:
        sha, contained = _contained(lane)
        if sha is None:
            problems.append(f'S1: `{lane}` does not resolve to a commit. A dispatch that '
                            f'names a branch nobody can find is stale by definition.')
        else:
            p = containment_problem(lane, contained, _merge_commit_for(sha),
                                    _containing_tag(sha))
            if p:
                problems.append(p)
            elif verbose:
                ahead = _ok('rev-list', '--count', f'{MAIN}..{sha}') or '?'
                print(f'  S1 OK: `{lane}` ({sha[:7]}) is NOT contained in {MAIN}; '
                      f'{ahead} commit(s) to integrate')

    if tag:
        if tag_is_taken(tags, tag):
            problems.append(f'S2: tag `{tag}` ALREADY EXISTS locally. It points at '
                            f'{_ok("rev-list", "-n", "1", tag) or "?"}. The next free '
                            f'build number is {nxt}.')
        elif rtags is not None and tag_is_taken(rtags, tag):
            problems.append(f'S2: tag `{tag}` already exists ON THE REMOTE. The next free '
                            f'build number is {nxt}.')
        elif verbose:
            print(f'  S2 OK: `{tag}` is free (local and remote)')

    if claims:
        for path, quoted, actual in stale_claims(claims, md5_of):
            if actual is None:
                problems.append(f'S3: the dispatch quotes `{quoted}` for {path}, but that '
                                f'file DOES NOT EXIST. Re-inventory before planning.')
            else:
                problems.append(
                    f'S3: STALE HASH. The dispatch quotes `{quoted}` for {path}; it is '
                    f'actually `{actual}`. Acting on the quoted state could REVERT what '
                    f'is deployed - re-derive the board from the live bytes first.')
        if verbose and not problems:
            print(f'  S3 OK: {len(claims)} quoted artifact hash(es) match the live bytes')

    dirty = _ok('status', '--porcelain')
    if dirty:
        problems.append(f'S4: the working tree is NOT clean ({len(dirty.splitlines())} '
                        f'path(s)). A ship never starts from an unknown tree.')
    behind = _ok('rev-list', '--count', f'{MAIN}..origin/{MAIN}')
    if behind and behind != '0':
        problems.append(f'S4: `{MAIN}` is {behind} commit(s) BEHIND `origin/{MAIN}`. '
                        f'Another lane has shipped since this dispatch was written.')
    return problems


def negtest():
    """Planted negatives, every one drawn from a dispatch that actually went stale."""
    real_tags = ['build93-ship', 'build94-dev', 'build95-ship', 'build96-ship',
                 'build97-ship']
    fake = {'C:/live/Quests.arc': 'd9f8c31654cbd8c80efe5ab7be573d77',
            'C:/live/gone.arc': None}
    cases = [
        ('N1 a lane tip already contained in main is CAUGHT (the build95 case)',
         bool(containment_problem('fix/chest-generosity-shared-cause', True,
                                  'ee5252d merge R-251', 'build95-ship'))),
        ('N1b a lane tip NOT contained is NOT flagged',
         containment_problem('fix/death-penalty-halve-again', False) is None),
        ('N2 an already-taken tag is CAUGHT (build95-ship)',
         tag_is_taken(real_tags, 'build95-ship')),
        ('N2b a free tag is NOT flagged (build98-ship)',
         not tag_is_taken(real_tags, 'build98-ship')),
        ('N3 the next free build number is 98, and build94-dev consumed 94',
         next_build_number(real_tags) == 98
         and next_build_number(['build93-ship', 'build94-dev']) == 95),
        ('N3b an empty tag history does not crash or skip a number',
         next_build_number([]) == 1),
        ('N4 the historical stale DEV Quests claim `1764c3a2` is CAUGHT',
         len(stale_claims([('C:/live/Quests.arc', '1764c3a2')], fake.get)) == 1),
        ('N4b the TRUE live hash for the same file is NOT flagged',
         not stale_claims([('C:/live/Quests.arc', 'd9f8c316')], fake.get)),
        ('N4c a full-length true hash is NOT flagged',
         not stale_claims([('C:/live/Quests.arc',
                            'd9f8c31654cbd8c80efe5ab7be573d77')], fake.get)),
        ('N5 a quoted hash for a file that does not exist is CAUGHT',
         stale_claims([('C:/live/gone.arc', 'deadbeef')], fake.get)[0][2] is None),
    ]
    ok = True
    for label, caught in cases:
        print(f'  {"CAUGHT " if caught else "MISSED "} {label}'
              + ('' if caught else '   <-- THE GATE IS BLIND HERE'))
        ok = ok and caught

    # ANTI-INERT, against the real repo: the three dispatches that were actually spent on
    # already-shipped work must each ABORT here, and a genuinely fresh ask must not.
    for lane, tag in (('fix/chest-generosity-shared-cause', 'build95-ship'),
                      ('fix/toxeus-shroud', 'build93-ship')):
        live = run(lane=lane, tag=tag, verbose=False)
        hit = any(p.startswith('S1') for p in live) and any(p.startswith('S2')
                                                            for p in live)
        print(f'  {"CAUGHT " if hit else "MISSED "} P-LIVE the real `{lane}` + `{tag}` '
              f'dispatch aborts on S1 and S2')
        ok = ok and hit
    clean = run(tag='build98-ship', verbose=False)
    print(f'  {"PASS   " if not clean else "FAIL   "} P0 a fresh build98-ship ask on a '
          f'clean tree is GREEN')
    for p in clean:
        print(f'      - {p}')
    return ok and not clean


def _claim(s):
    if '=' not in s:
        raise argparse.ArgumentTypeError('--claim wants <path>=<md5>')
    path, md5 = s.rsplit('=', 1)
    return (path.strip().strip('"'), md5.strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--lane', help='the lane branch/sha the dispatch says to integrate')
    ap.add_argument('--tag', help='the build tag the dispatch intends to create')
    ap.add_argument('--claim', type=_claim, action='append', default=[],
                    help='<path>=<md5> an artifact hash the dispatch quotes (repeatable)')
    ap.add_argument('--negtest', action='store_true')
    a = ap.parse_args()
    if a.negtest:
        print('GATE already-shipped NEGTEST')
        return 0 if negtest() else 1
    print('\n=== already-shipped audit (ship-procedure step 0) ===')
    problems = run(a.lane, a.tag, a.claim)
    if problems:
        print(f'\nGATE already-shipped: ABORT ({len(problems)} problem(s))')
        for p in problems:
            print(f'  - {p}')
        print('\nDo NOT merge, build, deploy or tag. Re-derive the board from the repo '
              'and the live artifacts, then re-dispatch.')
        return 1
    print('\nGATE already-shipped: PASS - this dispatch is not already done. (That is '
          'all this gate says; the ship procedure still owns every other question.)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
