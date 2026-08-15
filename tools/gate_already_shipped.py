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

THE RECEIPT (`BL-b98-DEBT-3`, the fourth bite)
----------------------------------------------
Everything above is advisory tooling an operator must REMEMBER to invoke, and a fourth
consecutive dispatch (`toxeus-boss-equipment-and-soul`, already shipped as build96) proved
that a habit is not a control. So a PASS now writes a RECEIPT to `local/step0_receipt.json`,
and `--verify-receipt` is a precondition wired into `scripts/package_workshop.ps1` ahead of
staging: packaging REFUSES to run when step 0 did not run green for this ship.

The receipt is bound to the repo state, not merely to a timestamp:
  R1 it exists and recorded a PASS;
  R2 it named an intended `--tag` (a ship with no build number is not a ship);
  R3 its HEAD is an ANCESTOR of the current HEAD - step 0 legitimately runs BEFORE the
     merge, so HEAD may move FORWARD after it, but it may never have DIVERGED;
  R4 the intended tag is STILL free right now (re-measured, not remembered);
  R5 the tree is still clean and `main` is still not behind origin;
  R6 if it cleared a lane, that lane is CONTAINED in HEAD now - the inverse of what S1
     demanded before the merge, which stops one lane's receipt authorising another's;
  R7 it has not already been SPENT. A green `--verify-receipt` marks the receipt CONSUMED,
     so one step-0 run authorises exactly ONE package (`BL-b98-DEBT-4`, the fifth bite).
     Before this, a receipt naming no lane was invalidated only by its tag being taken, so
     between a legitimate package and the tagging step it could authorise a SECOND package
     of different bytes inside one build-number window. An honest re-package is not blocked,
     it just re-runs step 0, which costs seconds.
`--repackage "<reason>"` is the one honest escape (a note-only re-upload of an already
shipped payload - `BL-b97-DEBT-1`): it waives R4 ONLY, demands a non-empty reason, and the
package guard prints that reason loudly instead of hiding it. It is single-use as well.

USAGE
  py tools/gate_already_shipped.py --lane fix/chest-generosity-shared-cause --tag build98-ship
  py tools/gate_already_shipped.py --claim "<dev>/Resources/Quests.arc=1764c3a2..."
  py tools/gate_already_shipped.py --verify-receipt        # what packaging runs
  py tools/gate_already_shipped.py --repackage "build97 note-only re-upload"
  py tools/gate_already_shipped.py --negtest
"""
import re
import io
import sys
import json
import hashlib
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
MAIN = 'main'
BUILD_TAG_RE = re.compile(r'^build(\d+)-(ship|dev)$')
RECEIPT = REPO / 'local' / 'step0_receipt.json'


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


def receipt_problems(receipt, head_ancestor, tag_taken, dirty_count, behind,
                     lane_now_merged=None):
    """R1-R6: why packaging must REFUSE, given a receipt dict and the live git facts.

    `receipt` is None when no step 0 has ever run. `head_ancestor` is True when the HEAD
    step 0 measured is an ancestor of the current HEAD (forward-only movement, which a
    merge legitimately causes). `lane_now_merged` is True when the lane the receipt
    cleared is contained in HEAD now - the exact INVERSE of what S1 demanded before the
    merge, and the clause that stops one lane's receipt authorising another's package.
    Returns [] when packaging may proceed."""
    if not receipt:
        return ['R1: no step-0 receipt at local/step0_receipt.json. Ship-procedure step 0 '
                'never ran for this ship. Run: py tools/gate_already_shipped.py --lane '
                '<branch-or-sha> --tag build<N>-ship']
    if receipt.get('verdict') == 'CONSUMED':
        return [f'R7: this step-0 receipt was ALREADY CONSUMED at '
                f'{receipt.get("consumed_at")}, by an earlier package run that it cleared '
                f'({receipt.get("tag") or "a repackage"}). A receipt authorises exactly ONE '
                f'package. A second one is either an honest re-run - fine, re-run step 0, it '
                f'costs seconds - or a stale dispatch riding a live receipt inside one '
                f'build-number window, which is the hole this closes. Run: py '
                f'tools/gate_already_shipped.py --lane <branch-or-sha> --tag build<N>-ship']
    out = []
    repack = (receipt.get('mode') == 'REPACKAGE')
    if receipt.get('verdict') != 'PASS':
        out.append(f'R1: the step-0 receipt records verdict '
                   f'`{receipt.get("verdict")}`, not PASS. The dispatch was refused; '
                   f'packaging it anyway is exactly the thing the gate exists to stop.')
    if not repack and not receipt.get('tag'):
        out.append('R2: the step-0 receipt names no intended --tag. A ship with no build '
                   'number is not a ship - re-run step 0 with --tag build<N>-ship.')
    if head_ancestor is False:
        out.append(f'R3: the receipt was written at HEAD `{str(receipt.get("head"))[:7]}`, '
                   f'which is NOT an ancestor of the current HEAD. The tree DIVERGED after '
                   f'step 0 ran (a reset, a rebase or the wrong checkout), so the receipt '
                   f'describes a repo state that no longer leads here. Re-run step 0.')
    if tag_taken and not repack:
        out.append(f'R4: the receipt\'s intended tag `{receipt.get("tag")}` is ALREADY '
                   f'TAKEN now. Another lane consumed the number between step 0 and '
                   f'packaging. Re-derive the build number before uploading anything.')
    if dirty_count:
        out.append(f'R5: the working tree is NOT clean ({dirty_count} path(s)). Package '
                   f'from a known tree or the uploaded payload cannot be reproduced.')
    if behind:
        out.append(f'R5: `{MAIN}` is {behind} commit(s) BEHIND `origin/{MAIN}`. Another '
                   f'lane has shipped since step 0 ran.')
    if repack and not str(receipt.get('reason') or '').strip():
        out.append('R4: this is a --repackage receipt with an EMPTY reason. The one escape '
                   'from the tag-free check has to say why, out loud, in the log.')
    if receipt.get('lane') and lane_now_merged is False:
        out.append(f'R6: the receipt cleared lane `{receipt.get("lane")}`, but that lane is '
                   f'NOT contained in HEAD. Step 0 passes a lane BEFORE the merge and '
                   f'packaging happens AFTER it, so an unmerged lane means this payload is '
                   f'not the ship the receipt cleared. Re-run step 0 for what you are '
                   f'actually packaging.')
    return out


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


# ── the receipt (BL-b98-DEBT-3: step 0 becomes a PRECONDITION, not a habit) ───────────
def write_receipt(lane, tag, claims, mode='SHIP', reason=None):
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    body = {'verdict': 'PASS', 'mode': mode, 'lane': lane, 'tag': tag,
            'reason': reason, 'head': _ok('rev-parse', 'HEAD'),
            'claims': [p for p, _ in claims],
            'when': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
    with io.open(RECEIPT, 'w', encoding='utf-8') as fh:
        json.dump(body, fh, indent=2, sort_keys=True)
    return body


def read_receipt():
    if not RECEIPT.is_file():
        return None
    try:
        with io.open(RECEIPT, encoding='utf-8') as fh:
            return json.load(fh)
    except (ValueError, OSError):
        return {'verdict': 'UNREADABLE'}


def consume_receipt(receipt):
    """BL-b98-DEBT-4: a receipt authorises exactly ONE package, then it is spent.

    The residual hole the receipt did not close: a receipt naming NO lane (the branchless
    dispatch shape of `dev-parity-r249-testhub-quests`) is invalidated only by its tag being
    consumed, so between a legitimate package and the tagging step it could authorise a
    SECOND package - of different bytes - inside one build-number window. Marking it spent
    the moment it is honoured closes that for every receipt shape, not just the branchless
    one, and it does not depend on an operator remembering to tag."""
    body = dict(receipt)
    body['verdict'] = 'CONSUMED'
    body['consumed_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with io.open(RECEIPT, 'w', encoding='utf-8') as fh:
        json.dump(body, fh, indent=2, sort_keys=True)
    return body


def verify_receipt(verbose=True, consume=True):
    """What `scripts/package_workshop.ps1` runs before it stages a single byte.

    On a green result the receipt is CONSUMED (`consume=False` peeks without spending it),
    so one step-0 run authorises exactly one package - `BL-b98-DEBT-4`."""
    if _ok('rev-parse', '--git-dir') is None:
        return ['git is unavailable, so the step-0 receipt cannot be verified. Refusing '
                'to report a PASS that was never measured.']
    r = read_receipt()
    head_ancestor = None
    tag_taken = False
    if r and r.get('head'):
        head_ancestor = (_git('merge-base', '--is-ancestor',
                              r['head'], 'HEAD').returncode == 0)
    if r and r.get('tag'):
        tags = local_tags()
        rtags = remote_tags()
        tag_taken = (tag_is_taken(tags, r['tag'])
                     or (rtags is not None and tag_is_taken(rtags, r['tag'])))
    lane_now_merged = None
    if r and r.get('lane'):
        sha = _ok('rev-parse', '--verify', f'{r["lane"]}^{{commit}}')
        lane_now_merged = (sha is not None
                           and _git('merge-base', '--is-ancestor', sha,
                                    'HEAD').returncode == 0)
    dirty = _ok('status', '--porcelain')
    behind = _ok('rev-list', '--count', f'{MAIN}..origin/{MAIN}')
    problems = receipt_problems(r, head_ancestor, tag_taken,
                                len(dirty.splitlines()) if dirty else 0,
                                int(behind) if (behind or '').isdigit() else 0,
                                lane_now_merged)
    if r and not problems:
        what = (f'REPACKAGE ({r.get("reason")})' if r.get('mode') == 'REPACKAGE'
                else f'tag {r.get("tag")}')
        if verbose:
            print(f'  receipt OK: step 0 passed {r.get("when")} for {what}, lane '
                  f'{r.get("lane") or "(none)"}, at HEAD {str(r.get("head"))[:7]} '
                  f'(an ancestor of the current HEAD)')
        if consume:
            c = consume_receipt(r)
            if verbose:
                print(f'  receipt CONSUMED at {c["consumed_at"]} - it authorised exactly '
                      f'this one package. Re-run step 0 before any further packaging.')
    return problems


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

        # ── R1-R5, the receipt: BL-b98-DEBT-3, the fourth bite ──────────────────────
        ('R1 packaging with NO receipt at all is CAUGHT (step 0 never ran)',
         bool(receipt_problems(None, True, False, 0, 0))),
        ('R1b a receipt recording a REFUSAL is CAUGHT, not honoured',
         any(p.startswith('R1') for p in receipt_problems(
             {'verdict': 'ABORT', 'tag': 'build98-ship', 'head': 'abc'},
             True, False, 0, 0))),
        ('R2 a receipt naming no intended tag is CAUGHT',
         any(p.startswith('R2') for p in receipt_problems(
             {'verdict': 'PASS', 'head': 'abc'}, True, False, 0, 0))),
        ('R3 a receipt whose HEAD is not an ancestor of HEAD is CAUGHT (diverged tree)',
         any(p.startswith('R3') for p in receipt_problems(
             {'verdict': 'PASS', 'tag': 'build98-ship', 'head': 'abc'},
             False, False, 0, 0))),
        ('R4 a receipt whose tag got CONSUMED between step 0 and packaging is CAUGHT',
         any(p.startswith('R4') for p in receipt_problems(
             {'verdict': 'PASS', 'tag': 'build98-ship', 'head': 'abc'},
             True, True, 0, 0))),
        ('R5 a dirty tree and a behind-origin main are BOTH caught',
         len([p for p in receipt_problems(
             {'verdict': 'PASS', 'tag': 'build98-ship', 'head': 'abc'},
             True, False, 3, 2) if p.startswith('R5')]) == 2),
        ('R4b a --repackage receipt with an EMPTY reason is CAUGHT',
         any(p.startswith('R4') for p in receipt_problems(
             {'verdict': 'PASS', 'mode': 'REPACKAGE', 'reason': '  ', 'head': 'abc'},
             True, True, 0, 0))),
        ('R6 a receipt whose cleared lane is NOT in HEAD is CAUGHT (packaging a '
         'different ship than step 0 cleared)',
         any(p.startswith('R6') for p in receipt_problems(
             {'verdict': 'PASS', 'tag': 'build98-ship', 'head': 'abc',
              'lane': 'fix/some-other-lane'}, True, False, 0, 0, False))),
        ('R6b the SAME receipt once its lane IS merged is NOT flagged',
         not receipt_problems({'verdict': 'PASS', 'tag': 'build98-ship', 'head': 'abc',
                               'lane': 'fix/some-other-lane'}, True, False, 0, 0, True)),
        ('R7 an ALREADY-CONSUMED receipt is CAUGHT (one receipt, one package - '
         'BL-b98-DEBT-4)',
         any(p.startswith('R7') for p in receipt_problems(
             {'verdict': 'CONSUMED', 'tag': 'build98-ship', 'head': 'abc',
              'consumed_at': '2026-08-15T05:00:00Z'}, True, False, 0, 0))),
        ('R7b a consumed BRANCHLESS receipt - the exact dev-parity shape, lane None and '
         'tag still FREE - is CAUGHT, which is the hole BL-b98-DEBT-4 named',
         any(p.startswith('R7') for p in receipt_problems(
             {'verdict': 'CONSUMED', 'tag': 'build98-ship', 'head': 'abc', 'lane': None,
              'consumed_at': '2026-08-15T05:00:00Z'}, True, False, 0, 0))),
        ('R7c a consumed REPACKAGE receipt is CAUGHT too (the escape hatch is single-use '
         'as well, so one --repackage authorises one re-upload)',
         any(p.startswith('R7') for p in receipt_problems(
             {'verdict': 'CONSUMED', 'mode': 'REPACKAGE', 'head': 'abc',
              'reason': 'note-only', 'consumed_at': '2026-08-15T05:00:00Z'},
             True, False, 0, 0))),
        ('R-CTRL a good SHIP receipt is NOT flagged',
         not receipt_problems({'verdict': 'PASS', 'tag': 'build98-ship', 'head': 'abc'},
                              True, False, 0, 0)),
        ('R-CTRL2 a REPACKAGE receipt with a real reason passes a TAKEN tag, and only that',
         not receipt_problems({'verdict': 'PASS', 'mode': 'REPACKAGE', 'head': 'abc',
                               'reason': 'build97 note-only re-upload'},
                              True, True, 0, 0)),
    ]
    ok = True
    for label, caught in cases:
        print(f'  {"CAUGHT " if caught else "MISSED "} {label}'
              + ('' if caught else '   <-- THE GATE IS BLIND HERE'))
        ok = ok and caught

    # ANTI-INERT, against the real repo: the four dispatches that were actually spent on
    # already-shipped work must each ABORT here, and a genuinely fresh ask must not.
    # The fourth is the proof that S1 catches a duplicate even when the tag it asks for is
    # FREE - `toxeus-boss-equipment-and-soul` shipped as build96 and was re-dispatched to
    # take build98, so only lane containment could tell it was already done.
    for lane, tag, want in (
            ('fix/chest-generosity-shared-cause', 'build95-ship', ('S1', 'S2')),
            ('fix/toxeus-shroud', 'build93-ship', ('S1', 'S2')),
            ('fix/toxeus-boss-equipment-and-soul', 'build98-ship', ('S1',))):
        live = run(lane=lane, tag=tag, verbose=False)
        hit = all(any(p.startswith(s) for p in live) for s in want)
        print(f'  {"CAUGHT " if hit else "MISSED "} P-LIVE the real `{lane}` + `{tag}` '
              f'dispatch aborts on {" and ".join(want)}')
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
    ap.add_argument('--verify-receipt', action='store_true',
                    help='what packaging runs: refuse unless step 0 passed for this ship')
    ap.add_argument('--repackage', metavar='REASON',
                    help='write a receipt for a note-only re-upload of an already-shipped '
                         'payload; waives the tag-free check ONLY, and the reason is '
                         'printed by the package guard')
    a = ap.parse_args()
    if a.negtest:
        print('GATE already-shipped NEGTEST')
        return 0 if negtest() else 1

    if a.verify_receipt:
        print('\n=== step-0 receipt check (packaging precondition) ===')
        problems = verify_receipt()
        if problems:
            print(f'\nGATE step-0 receipt: REFUSE TO PACKAGE ({len(problems)} problem(s))')
            for p in problems:
                print(f'  - {p}')
            print('\nNothing has been staged or uploaded. Four consecutive ship dispatches '
                  'were spent on already-shipped work; this check is why a fifth cannot be.')
            return 1
        print('\nGATE step-0 receipt: PASS - step 0 ran green for this ship.')
        return 0

    if a.repackage is not None:
        print('\n=== step-0 receipt: REPACKAGE (tag-free check waived) ===')
        if not a.repackage.strip():
            print('  --repackage needs a REASON. The escape hatch has to say why.')
            return 1
        problems = [p for p in run(a.lane, None, a.claim) if not p.startswith('S1')]
        if problems:
            print(f'\nGATE already-shipped: ABORT ({len(problems)} problem(s))')
            for p in problems:
                print(f'  - {p}')
            return 1
        b = write_receipt(a.lane, None, a.claim, mode='REPACKAGE', reason=a.repackage)
        print(f'  receipt written: {RECEIPT} (REPACKAGE, HEAD {str(b["head"])[:7]})')
        print(f'  reason: {a.repackage}')
        return 0

    print('\n=== already-shipped audit (ship-procedure step 0) ===')
    problems = run(a.lane, a.tag, a.claim)
    if problems:
        print(f'\nGATE already-shipped: ABORT ({len(problems)} problem(s))')
        for p in problems:
            print(f'  - {p}')
        print('\nDo NOT merge, build, deploy or tag. Re-derive the board from the repo '
              'and the live artifacts, then re-dispatch.')
        if RECEIPT.is_file():
            RECEIPT.unlink()
            print(f'Stale step-0 receipt removed ({RECEIPT}) - packaging will now refuse.')
        return 1
    b = write_receipt(a.lane, a.tag, a.claim)
    print(f'\nGATE already-shipped: PASS - this dispatch is not already done. (That is '
          f'all this gate says; the ship procedure still owns every other question.)')
    print(f'Receipt written to {RECEIPT} (HEAD {str(b["head"])[:7]}); packaging verifies it.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
