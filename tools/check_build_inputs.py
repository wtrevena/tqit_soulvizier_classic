#!/usr/bin/env python3
"""ONE preflight resolver for every UPSTREAM input the SVC build pipeline consumes.

WHY (BL-b90-DEBT-2 / BL-b89-DEBT-4b): `upstream/` and `reference_mods/` are gitignored
caches that are routinely EMPTY or partial on a fresh machine/worktree. Before this
module, a lane that needed a DB or MAP build died deep inside `ArcArchive` / `ArzDatabase`
with a bare `FileNotFoundError` naming a path nobody had ever heard of - the only way to
recover was to find the right paragraph in `docs/BACKLOG.md`. Every build entrypoint now
runs its inputs through `preflight()` first, so a missing input fails ONCE, LOUDLY, naming
the exact env var to set and every place that was searched.

RESOLUTION ORDER (per input, first hit wins):
  1. the explicit env var override  (e.g. $SVC_SV098I_ARZ, $SVC_SVAERA_ARC)
  2. the in-repo cache              (upstream/... , reference_mods/... - both gitignored)
  3. the MAIN checkout's cache      (gitignored caches do NOT propagate into a linked
                                     worktree, and nearly every lane runs in one)
  4. the installed-on-this-machine location (Steam game dir / Steam Workshop item)
  5. a sibling worktree that already has the cache populated
  6. a third_party/ archive        (reported as EXTRACTABLE, never silently unpacked;
                                    `--extract` does it for .zip archives)

INTEGRITY: fallbacks (2..5) are md5-verified against `EXPECTED_MD5` where a known-good
hash exists, so auto-resolution can never quietly feed the build a different upstream.
A caller-supplied path (argv) is used AS-IS with no hashing - existing invocations are
byte-identical to the pre-preflight behaviour.

CLI:
  py tools/check_build_inputs.py --db      # the database build's inputs
  py tools/check_build_inputs.py --map     # the map merge's inputs
  py tools/check_build_inputs.py --all     # everything, plus the optional inputs
  py tools/check_build_inputs.py --all --extract   # populate upstream/ from third_party/
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _main_checkout(repo: Path = REPO):
    """The MAIN git checkout when `repo` is a linked worktree, else None.

    `upstream/`, `reference_mods/` and `third_party/` are gitignored, so `git worktree
    add` gives a lane an EMPTY cache even though the main checkout is fully populated.
    Resolved from the worktree's `.git` FILE (`gitdir: <main>/.git/worktrees/<name>`)
    rather than by string-matching the path, so it works for worktrees anywhere.
    """
    dotgit = repo / '.git'
    if not dotgit.is_file():
        return None                      # a normal checkout (or not a repo at all)
    try:
        line = dotgit.read_text(encoding='utf-8', errors='replace').strip()
    except OSError:
        return None
    if not line.lower().startswith('gitdir:'):
        return None
    gitdir = Path(line.split(':', 1)[1].strip())
    if not gitdir.is_absolute():
        gitdir = (repo / gitdir).resolve()
    # <main>/.git/worktrees/<name>  ->  <main>
    for parent in gitdir.parents:
        if parent.name == '.git':
            main = parent.parent
            return main if main != repo and main.is_dir() else None
    return None


MAIN_CHECKOUT = _main_checkout()

# --- known machine locations (documented, not guessed) -----------------------
STEAM_TQAE = Path(r'C:/Program Files (x86)/Steam/steamapps/common'
                  r'/Titan Quest Anniversary Edition')
STEAM_WORKSHOP = Path(r'C:/Program Files (x86)/Steam/steamapps/workshop/content/475150')
SVAERA_WORKSHOP = STEAM_WORKSHOP / '2076433374' / 'SVAERA_customquest'
WORKTREES = (MAIN_CHECKOUT or REPO) / '.claude' / 'worktrees'

# md5 of the known-good upstream artifacts. Measured 2026-07-28 on Will's machine; the
# four DB hashes match the ones recorded in the b90 BACKLOG entry byte-for-byte.
EXPECTED_MD5 = {
    'sv098i_arz':        '11773cdc9bffd9a1b9753beab718843c',   # SV 0.98i database.arz
    'sv09_arz':          'b31951df8cf80fa6eb97eb14f593b192',   # SV 0.9   database.arz
    'sv041_arz':         '056d6f4e321790d1c9723b5bcbb10f45',   # SV 0.4.1 database.arz
    'sv098i_text_arc':   '29505ac24d1f9403d89f34c5e2e761a2',   # SV 0.98i Text_EN.arc
    'sv098i_levels_arc': '0b575c9dcd95461ec4ef2dea351f7d36',   # SV 0.98i Levels.arc
    'svaera_levels_arc': 'a1e13e48b3de499df31a5ca4d919030d',   # SVAERA 1.14 Levels.arc
    'svaera_arz':        '7bad88043e5c1be0c83fce1e8522ce8a',   # SVAERA_customquest.arz
    'sv098i_creatures_arc': '5ef9d00a9dd5ecebb0e3ada5385a1b31',  # SV 0.98i Creatures.arc (AllSkins costume-dye PC skins)
    # base_arz is the player's own TQAE install: version-dependent, deliberately unpinned.
    # base_creatures_arc is likewise the player's own TQAE install - unpinned.
}


class Input:
    """One upstream build input and every place it can legitimately come from."""

    def __init__(self, key, label, env, cache_rel=None, candidates=(), archive_rel=None,
                 groups=(), optional=False, note=''):
        self.key = key
        self.label = label
        self.env = env                 # the env-var override (resolution step 1)
        self.cache_rel = cache_rel     # repo-RELATIVE gitignored cache path (steps 2-3)
        self.candidates = list(candidates)   # (source-label, Path) pairs (steps 4-5)
        self.archive_rel = archive_rel  # (repo-relative archive, member name) (step 6)
        self.groups = set(groups)      # which builds need it ('db' / 'map' / 'text')
        self.optional = optional
        self.note = note

    @property
    def cache(self):
        """The in-repo cache path (this checkout). None for install-resolved inputs."""
        return None if self.cache_rel is None else REPO / self.cache_rel

    @property
    def main_cache(self):
        """The same cache in the MAIN checkout, when this is a linked worktree."""
        if self.cache_rel is None or MAIN_CHECKOUT is None:
            return None
        return MAIN_CHECKOUT / self.cache_rel

    def archives(self):
        """[(label, archive Path, member)] - this checkout first, then the main one."""
        if not self.archive_rel:
            return []
        rel, member = self.archive_rel
        out = [('third_party archive', REPO / rel, member)]
        if MAIN_CHECKOUT is not None:
            out.append(('main-checkout third_party', MAIN_CHECKOUT / rel, member))
        return out


INPUTS = [
    Input('sv098i_arz', 'SV 0.98i database.arz', 'SVC_SV098I_ARZ',
          'upstream/soulvizier_098i/Database/database.arz',
          archive_rel=('third_party/soulvizier098i.zip', 'Database/database.arz'),
          groups=('db',), note='amgoz1 SV 0.98i - the DB build base'),
    Input('sv09_arz', 'SV 0.9 database.arz', 'SVC_SV09_ARZ',
          'upstream/soulvizier_0.9/Database/database.arz',
          archive_rel=('third_party/Soulvizier_0.9.rar', 'Database/database.arz'),
          groups=('db',), note='potion drops + legacy donor'),
    Input('sv041_arz', 'SV 0.4.1 database.arz', 'SVC_SV041_ARZ',
          'upstream/soulvizier_041/Database/database.arz',
          archive_rel=('third_party/soulvizier-beta04.1.rar', 'Database/database.arz'),
          groups=('db',), note='legacy-skill donor'),
    Input('base_arz', 'base game (TQAE) database.arz', 'SVC_BASE_ARZ',
          candidates=(('Steam TQAE install', STEAM_TQAE / 'Database' / 'database.arz'),),
          groups=('db',), note="the player's own TQAE install - never pinned by hash"),
    Input('sv098i_text_arc', 'SV 0.98i Text_EN.arc', 'SVC_SV098I_TEXT_ARC',
          'upstream/soulvizier_098i/Resources/Text_EN.arc',
          archive_rel=('third_party/soulvizier098i.zip', 'Resources/Text_EN.arc'),
          groups=('text',), note='modstrings.txt source'),
    Input('svaera_levels_arc', 'SVAERA Levels.arc (merge base)', 'SVC_SVAERA_ARC',
          'reference_mods/SVAERA_customquest/Resources/Levels.arc',
          candidates=(('Steam Workshop item 2076433374',
                       SVAERA_WORKSHOP / 'Resources' / 'Levels.arc'),),
          groups=('map',), note='soa SVAERA 1.14 - the world the merge builds ON'),
    Input('sv098i_levels_arc', 'SV 0.98i Levels.arc (merge donor)', 'SVC_SV_ARC',
          'upstream/soulvizier_098i/Resources/Levels.arc',
          candidates=(('build36-map worktree cache',
                       WORKTREES / 'build36-map' / 'upstream' / 'soulvizier_098i'
                       / 'Resources' / 'Levels.arc'),),
          archive_rel=('third_party/soulvizier098i.zip', 'Resources/Levels.arc'),
          groups=('map',), note='SV drxmap levels grafted into the SVAERA world'),
    Input('svaera_arz', 'SVAERA_customquest.arz (mastery graft source)', 'SVC_SVAERA_ARZ',
          candidates=(('Steam Workshop item 2076433374',
                       SVAERA_WORKSHOP / 'Database' / 'SVAERA_customquest.arz'),),
          groups=('db',), optional=True,
          note='build36 lane-B graft; skip the graft with SVC_GRAFT_SVAERA=0'),
    Input('sv098i_creatures_arc', 'SV 0.98i Creatures.arc (costume-dye PC skins)',
          'SVC_SV098I_CREATURES_ARC',
          'upstream/soulvizier_098i/Resources/Creatures.arc',
          archive_rel=('third_party/soulvizier098i.zip', 'Resources/Creatures.arc'),
          groups=('resources',),
          note='amgoz1 AllSkins PC skins the Garden costume dyes reskin to (PR-2)'),
    Input('base_creatures_arc', 'base game (TQAE) Creatures.arc', 'SVC_BASE_CREATURES_ARC',
          candidates=(('Steam TQAE install', STEAM_TQAE / 'Resources' / 'Creatures.arc'),),
          groups=('resources',),
          note="the player's own TQAE install - overlap reference, never pinned"),
]

BY_KEY = {i.key: i for i in INPUTS}


def md5(path: Path, _chunk=1 << 22) -> str:
    h = hashlib.md5()
    with Path(path).open('rb') as fh:
        for block in iter(lambda: fh.read(_chunk), b''):
            h.update(block)
    return h.hexdigest()


def _hash_ok(key, path):
    """(ok, detail). True when no hash is pinned for this input."""
    want = EXPECTED_MD5.get(key)
    if not want:
        return True, 'no pinned hash'
    got = md5(path)
    return got == want, f'md5 {got}' + ('' if got == want else f' != expected {want}')


class MissingInput(Exception):
    """Raised (and rendered) when an input cannot be resolved anywhere."""


def _ladder(inp: Input):
    """Yield (source-label, Path) in resolution order, env var first."""
    env_val = os.environ.get(inp.env)
    if env_val and env_val.strip():
        yield f'${inp.env}', Path(env_val.strip())
    if inp.cache is not None:
        yield 'in-repo cache', inp.cache
    if inp.main_cache is not None:
        yield 'main-checkout cache', inp.main_cache
    for label, p in inp.candidates:
        yield label, p


def _report_missing(inp: Input) -> str:
    lines = [f'FATAL: build input NOT FOUND - {inp.label}']
    if inp.note:
        lines.append(f'       ({inp.note})')
    lines.append('       searched, in order:')
    env_val = os.environ.get(inp.env)
    n = 1
    lines.append(f'         {n}. ${inp.env} = ' + (env_val if env_val else '<unset>'))
    n += 1
    for label, p in _ladder(inp):
        if label.startswith('$'):
            continue
        lines.append(f'         {n}. {label:<24} {p}')
        n += 1
    for label, arc, member in inp.archives():
        state = 'PRESENT' if arc.is_file() else 'absent'
        lines.append(f'         {n}. {label:<24} {arc} :: {member}  [{state}]')
        n += 1
        if arc.is_file():
            if arc.suffix.lower() == '.zip':
                lines.append('            -> EXTRACTABLE: '
                             'py tools/check_build_inputs.py --all --extract')
            else:
                lines.append(f'            -> extract {member!r} from {arc} by hand '
                             f'(.rar needs WinRAR/7-Zip) into {inp.cache}')
    lines.append(f'       FIX: set ${inp.env} to the file, or restore the cache.')
    return '\n'.join(lines)


def resolve(key, given=None, verbose=True):
    """Resolve one input to an existing Path, or raise MissingInput.

    `given` (e.g. an argv path) short-circuits everything when it exists - the build
    behaves exactly as it did before this module. Only the FALLBACK ladder is hashed.
    """
    inp = BY_KEY[key]
    if given is not None:
        g = Path(given)
        if g.is_file():
            return g
        if verbose:
            print(f'  PREFLIGHT: {inp.label}: supplied path does not exist ({g}) '
                  f'- falling back to the resolution ladder')
    for label, p in _ladder(inp):
        if not p.is_file():
            continue
        ok, detail = _hash_ok(key, p)
        if not ok:
            print(f'  PREFLIGHT: {inp.label}: REJECTED {label} {p} ({detail})')
            continue
        if verbose:
            print(f'  PREFLIGHT: {inp.label:<42} OK via {label}')
            print(f'             {p}')
        return p
    raise MissingInput(_report_missing(inp))


def preflight(*keys, given=None, verbose=True):
    """Resolve every key, collecting ALL failures before exiting.

    Returns {key: Path}. `given` = {key: caller-supplied path} (argv wins when present).
    Exits the process with the full diagnostic if anything is unresolvable - fail LOUD,
    once, naming every env var to set (BL-b90-DEBT-2).
    """
    given = given or {}
    out, errs = {}, []
    for k in keys:
        try:
            out[k] = resolve(k, given.get(k), verbose=verbose)
        except MissingInput as e:
            errs.append(str(e))
    if errs:
        raise SystemExit('\n\n'.join(errs) + '\n\n'
                         'Run `py tools/check_build_inputs.py --all` for the full '
                         'input inventory (CLAUDE.md "Build & deploy commands").')
    return out


DB_KEYS = tuple(i.key for i in INPUTS if 'db' in i.groups and not i.optional)
MAP_KEYS = tuple(i.key for i in INPUTS if 'map' in i.groups and not i.optional)
TEXT_KEYS = tuple(i.key for i in INPUTS if 'text' in i.groups and not i.optional)


def extract_from_third_party(keys, dry_run=False):
    """Populate the in-repo cache from third_party/ .zip archives. Returns [(key, msg)]."""
    results = []
    for key in keys:
        inp = BY_KEY[key]
        if inp.cache is None:
            results.append((key, 'resolved from an install location, not a repo cache'))
            continue
        if inp.cache.is_file():
            results.append((key, f'already present: {inp.cache}'))
            continue
        zips = [(a, m) for _l, a, m in inp.archives()
                if a.is_file() and a.suffix.lower() == '.zip']
        if not inp.archives():
            results.append((key, 'no third_party archive for this input'))
            continue
        if not zips:
            arc, member = inp.archives()[0][1], inp.archives()[0][2]
            results.append((key, f'no usable .zip archive ({arc.name}) - '
                                 f'extract {member!r} by hand'))
            continue
        arc, member = zips[0]
        if dry_run:
            results.append((key, f'WOULD extract {member} from {arc.name} -> {inp.cache}'))
            continue
        with zipfile.ZipFile(arc) as z:
            names = {n.replace('\\', '/').lower(): n for n in z.namelist()}
            real = names.get(member.replace('\\', '/').lower())
            if real is None:
                results.append((key, f'{member!r} not in {arc.name}'))
                continue
            inp.cache.parent.mkdir(parents=True, exist_ok=True)
            with z.open(real) as src, inp.cache.open('wb') as dst:
                while True:
                    chunk = src.read(1 << 22)
                    if not chunk:
                        break
                    dst.write(chunk)
        ok, detail = _hash_ok(key, inp.cache)
        results.append((key, f'extracted -> {inp.cache} ({detail})'
                             + ('' if ok else '  *** HASH MISMATCH ***')))
    return results


def selftest():
    """PLANTED NEGATIVE TESTS for the preflight itself (law #4: a new surface ships
    its gate). Runs entirely on synthetic inputs - touches no build artifact."""
    import tempfile
    fails = []

    def check(name, cond, detail=''):
        print(f'  [{"PASS" if cond else "FAIL"}] {name}' + (f'  ({detail})' if detail else ''))
        if not cond:
            fails.append(name)

    # NEG-1: an input that exists NOWHERE must raise, naming its env var + every rung.
    key = '__selftest_missing__'
    BY_KEY[key] = Input(key, 'SELFTEST missing input', 'SVC_SELFTEST_MISSING',
                        'upstream/__selftest__/nope.arz',
                        archive_rel=('third_party/__selftest__.zip', 'nope.arz'),
                        note='synthetic')
    try:
        preflight(key, verbose=False)
        check('NEG-1 unresolvable input fails loud', False, 'preflight returned!')
    except SystemExit as e:
        msg = str(e)
        check('NEG-1 unresolvable input fails loud', True)
        check('NEG-1 message names the env var', '$SVC_SELFTEST_MISSING' in msg)
        check('NEG-1 message lists the in-repo cache rung', 'in-repo cache' in msg)
        check('NEG-1 message lists the third_party rung', 'third_party' in msg)
        check('NEG-1 message is NOT a bare FileNotFoundError',
              'build input NOT FOUND' in msg and 'FIX:' in msg)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        good = td / 'good.bin'
        good.write_bytes(b'the real upstream')
        bad = td / 'bad.bin'
        bad.write_bytes(b'an impostor')
        good_md5 = md5(good)

        # NEG-2: a pinned-hash input must REJECT a fallback whose bytes differ, and keep
        # walking the ladder to the correct one (silent substitution is the failure mode
        # this whole module exists to prevent).
        key2 = '__selftest_hash__'
        BY_KEY[key2] = Input(key2, 'SELFTEST hashed input', 'SVC_SELFTEST_HASH',
                             candidates=(('impostor rung', bad), ('good rung', good)),
                             note='synthetic')
        EXPECTED_MD5[key2] = good_md5
        try:
            got = resolve(key2, verbose=False)
            check('NEG-2 hash-mismatched fallback rejected, good rung used', got == good,
                  str(got))
        except MissingInput:
            check('NEG-2 hash-mismatched fallback rejected, good rung used', False,
                  'nothing resolved')

        # NEG-3: when EVERY rung mismatches, resolve must fail rather than return junk.
        key3 = '__selftest_allbad__'
        BY_KEY[key3] = Input(key3, 'SELFTEST all-bad input', 'SVC_SELFTEST_ALLBAD',
                             candidates=(('impostor rung', bad),), note='synthetic')
        EXPECTED_MD5[key3] = good_md5
        try:
            resolve(key3, verbose=False)
            check('NEG-3 all-mismatched input fails rather than returning junk', False,
                  'returned a path')
        except MissingInput:
            check('NEG-3 all-mismatched input fails rather than returning junk', True)

        # POS-1: a caller-supplied (argv) path that EXISTS short-circuits the ladder
        # unhashed - existing build invocations keep their exact old behaviour.
        got = resolve(key3, given=bad, verbose=False)
        check('POS-1 existing caller path used as-is (no hashing)', got == bad, str(got))

    for k in ('__selftest_missing__', '__selftest_hash__', '__selftest_allbad__'):
        BY_KEY.pop(k, None)
        EXPECTED_MD5.pop(k, None)
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--db', action='store_true', help='check the database-build inputs')
    ap.add_argument('--map', action='store_true', help='check the map-merge inputs')
    ap.add_argument('--text', action='store_true', help='check the text-arc inputs')
    ap.add_argument('--all', action='store_true', help='check every input (incl optional)')
    ap.add_argument('--extract', action='store_true',
                    help='populate the in-repo cache from third_party/ .zip archives')
    ap.add_argument('--dry-run', action='store_true', help='with --extract: report only')
    ap.add_argument('--verify-hashes', action='store_true',
                    help='md5 every resolved input, including caller-default locations')
    ap.add_argument('--selftest', action='store_true',
                    help='run the planted negative tests for the resolver itself')
    args = ap.parse_args()

    if args.selftest:
        print('=== check_build_inputs SELFTEST (planted negative tests) ===')
        fails = selftest()
        print()
        print(f'RESULT: {"FAIL " + str(fails) if fails else "PASS (selftest clean)"}')
        return 1 if fails else 0

    if not (args.db or args.map or args.text or args.all):
        args.all = True

    keys = []
    if args.all:
        keys = [i.key for i in INPUTS]
    else:
        if args.db:
            keys += list(DB_KEYS)
        if args.map:
            keys += list(MAP_KEYS)
        if args.text:
            keys += list(TEXT_KEYS)
    keys = list(dict.fromkeys(keys))

    if args.extract:
        print('=== extract missing inputs from third_party/ ===')
        for key, msg in extract_from_third_party(keys, dry_run=args.dry_run):
            print(f'  {key:<20} {msg}')
        print()

    print('=== build-input preflight ===')
    missing = []
    for key in keys:
        inp = BY_KEY[key]
        found = None
        for label, p in _ladder(inp):
            if p.is_file():
                found = (label, p)
                break
        tag = 'OPTIONAL' if inp.optional else 'REQUIRED'
        if found is None:
            print(f'  [MISSING ] {inp.label}  ({tag}, set ${inp.env})')
            if not inp.optional:
                missing.append(inp)
            continue
        label, p = found
        extra = ''
        if args.verify_hashes:
            ok, detail = _hash_ok(key, p)
            extra = f'  [{detail}]' if ok else f'  [*** {detail} ***]'
            if not ok:
                missing.append(inp)
        print(f'  [FOUND   ] {inp.label}')
        print(f'             via {label}: {p}{extra}')

    print()
    if missing:
        print('RESULT: FAIL - unresolved/mismatched inputs:')
        for inp in missing:
            print()
            print(_report_missing(inp))
        return 1
    print(f'RESULT: PASS ({len(keys)} input(s) resolvable)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
