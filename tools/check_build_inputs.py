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
  2. the in-repo cache              (upstream/... , reference_mods/... - both gitignored;
                                     root overridable with $SVC_CACHE_ROOT / --cache-root)
  3. the MAIN checkout's cache      (gitignored caches do NOT propagate into a linked
                                     worktree, and nearly every lane runs in one)
  4. the installed-on-this-machine location (Steam game dir / Steam Workshop item)
  5. a sibling worktree that already has the cache populated
  6. a third_party/ archive        (reported as EXTRACTABLE, never silently unpacked;
                                    `--extract` does it: .zip through `zipfile`, .7z and
                                    .rar through 7-Zip, ONE nested top-level folder inside
                                    the archive tolerated, ambiguity refused)

INTEGRITY: fallbacks (2..5) are md5-verified against `EXPECTED_MD5` where a known-good
hash exists, so auto-resolution can never quietly feed the build a different upstream.
A caller-supplied path (argv) is used AS-IS with no hashing - existing invocations are
byte-identical to the pre-preflight behaviour. `--extract` md5-verifies every member it
lands (BL-b102-DEBT-1): a mismatch deletes nothing and fails loud.

ARCHIVES (`--extract`, BL-b102-DEBT-1):
  * .zip is read with `zipfile`; .7z / .rar shell out to 7-Zip, located as: $SVC_7Z when
    set (authoritative - a bad value fails loud, it never falls through), else
    `C:\\Program Files\\7-Zip\\7z.exe`, else `7z` on PATH. No 7-Zip + a non-zip archive
    needed = a LOUD failure naming the archive and the install hint, never a silent skip.
  * the expected inner path (`Database/database.arz`) is matched as a normalized SUFFIX of
    the member list, so ModDB's pristine `Soulvizier_v0.98i.7z` (members nested under
    `Soulvizier v0.98i\\`) resolves without a repack; TWO members ending in the same suffix
    is an ambiguity and is REFUSED, listing both.
  * only the needed members are extracted (`7z x <archive> <member>`), landed at the cache
    path the ladder expects, then md5-verified against `EXPECTED_MD5`.
  * the ModDB original filenames are accepted as alternates in the archive map
    (`Soulvizier_v0.98i.7z` beside the flat repack `soulvizier098i.zip`); the first archive
    present wins and the report names which one.
  * $SVC_THIRD_PARTY_DIR / --third-party points the archive search at ONE directory
    (the repo's `third_party/` and the main checkout's are then NOT searched);
    $SVC_CACHE_ROOT / --cache-root relocates the rung-2 cache root (default: this repo),
    which is also where `--extract` writes. Together they let a fresh machine or a scratch
    test restore the inputs without touching the repo's own caches.
    Off-repo copies of the four archives: `Z:\\Computer Backup\\tqit_soulvizier_classic\\
    third_party_archives\\` (README there carries the outer + inner md5s).

CLI:
  py tools/check_build_inputs.py --db      # the database build's inputs
  py tools/check_build_inputs.py --map     # the map merge's inputs
  py tools/check_build_inputs.py --all     # everything, plus the optional inputs
  py tools/check_build_inputs.py --all --extract   # populate upstream/ from third_party/
  py tools/check_build_inputs.py --all --extract --third-party <dir> --cache-root <dir>
  py tools/check_build_inputs.py --selftest [--selftest-root <scratch dir>]
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
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

# --- 7-Zip (BL-b102-DEBT-1) ---------------------------------------------------
SEVENZIP_DEFAULT = Path(r'C:/Program Files/7-Zip/7z.exe')
SEVENZIP_ENV = 'SVC_7Z'
SEVENZIP_HINT = ('install 7-Zip (`winget install 7zip.7zip`, expected at '
                 f'{SEVENZIP_DEFAULT}) or set ${SEVENZIP_ENV} to the 7z.exe to use')

# --- location overrides (scratch restores / fresh machines, never the repo's caches) ---
CACHE_ROOT_ENV = 'SVC_CACHE_ROOT'          # rung 2 root (default: this repo); --extract writes here
THIRD_PARTY_ENV = 'SVC_THIRD_PARTY_DIR'    # ONE archive dir (default: <repo>/third_party [+ main])

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


def cache_root() -> Path:
    """Rung-2 root: $SVC_CACHE_ROOT when set, else this repo. Read per call, never cached,
    so a CLI flag or a selftest can point it at scratch without re-importing the module."""
    v = os.environ.get(CACHE_ROOT_ENV, '').strip()
    return Path(v) if v else REPO


def third_party_dirs():
    """[(label, dir)] searched for archives. $SVC_THIRD_PARTY_DIR set = ONLY that dir."""
    v = os.environ.get(THIRD_PARTY_ENV, '').strip()
    if v:
        return [(f'${THIRD_PARTY_ENV}', Path(v))]
    out = [('third_party archive', REPO / 'third_party')]
    if MAIN_CHECKOUT is not None:
        out.append(('main-checkout third_party', MAIN_CHECKOUT / 'third_party'))
    return out


class Input:
    """One upstream build input and every place it can legitimately come from."""

    def __init__(self, key, label, env, cache_rel=None, candidates=(), archive_rel=None,
                 archive_alts=(), groups=(), optional=False, note=''):
        self.key = key
        self.label = label
        self.env = env                 # the env-var override (resolution step 1)
        self.cache_rel = cache_rel     # cache-root-RELATIVE gitignored cache path (steps 2-3)
        self.candidates = list(candidates)   # (source-label, Path) pairs (steps 4-5)
        self.archive_rel = archive_rel  # (repo-relative archive, member name) (step 6)
        self.archive_alts = list(archive_alts)  # alternate archive names, same member
        self.groups = set(groups)      # which builds need it ('db' / 'map' / 'text')
        self.optional = optional
        self.note = note

    @property
    def cache(self):
        """The rung-2 cache path (this checkout, or $SVC_CACHE_ROOT). None for
        install-resolved inputs."""
        return None if self.cache_rel is None else cache_root() / self.cache_rel

    @property
    def main_cache(self):
        """The same cache in the MAIN checkout, when this is a linked worktree."""
        if self.cache_rel is None or MAIN_CHECKOUT is None:
            return None
        return MAIN_CHECKOUT / self.cache_rel

    def archives(self):
        """[(label, archive Path, member)] in search order: per archive dir (this checkout
        first, then the main one; or ONLY $SVC_THIRD_PARTY_DIR), the primary archive name
        then each alternate. Archive names are the basenames of the repo-relative entries."""
        if not self.archive_rel:
            return []
        rel, member = self.archive_rel
        names = [Path(rel).name] + [Path(a).name for a in self.archive_alts]
        out = []
        for label, d in third_party_dirs():
            for i, name in enumerate(names):
                lab = label if i == 0 else label + ' (alternate)'
                out.append((lab, d / name, member))
        return out


INPUTS = [
    Input('sv098i_arz', 'SV 0.98i database.arz', 'SVC_SV098I_ARZ',
          'upstream/soulvizier_098i/Database/database.arz',
          archive_rel=('third_party/soulvizier098i.zip', 'Database/database.arz'),
          archive_alts=('third_party/Soulvizier_v0.98i.7z',),
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
          archive_alts=('third_party/Soulvizier_v0.98i.7z',),
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
          archive_alts=('third_party/Soulvizier_v0.98i.7z',),
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
          archive_alts=('third_party/Soulvizier_v0.98i.7z',),
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


# --- archive layer (BL-b102-DEBT-1) -------------------------------------------

def find_7z():
    """(path-or-None, detail). $SVC_7Z is authoritative when set: a value that is not a
    file is a loud miss, it never falls through to the default locations."""
    env_val = os.environ.get(SEVENZIP_ENV, '').strip()
    if env_val:
        p = Path(env_val)
        if p.is_file():
            return p, f'${SEVENZIP_ENV}'
        return None, f'${SEVENZIP_ENV}={env_val} is not a file'
    if SEVENZIP_DEFAULT.is_file():
        return SEVENZIP_DEFAULT, 'default install location'
    on_path = shutil.which('7z')
    if on_path:
        return Path(on_path), 'PATH'
    return None, (f'${SEVENZIP_ENV} unset, {SEVENZIP_DEFAULT} absent, no `7z` on PATH')


def _is_zip(arc: Path) -> bool:
    return arc.suffix.lower() == '.zip'


def _norm(name: str) -> str:
    return name.replace('\\', '/').lstrip('./').lower()


def _run_7z(seven: Path, args, cwd=None):
    """Run 7z with UTF-8 console output. Returns (rc, stdout, stderr)."""
    cmd = [str(seven)] + list(args)
    proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (proc.returncode,
            proc.stdout.decode('utf-8', errors='replace'),
            proc.stderr.decode('utf-8', errors='replace'))


def list_archive(arc: Path, seven=None):
    """FILE members of an archive (directories dropped), names exactly as the container
    stores them. .zip via `zipfile`; anything else via `7z l -slt -ba`. Raises RuntimeError
    with the loud diagnostic when the archive cannot be listed."""
    arc = Path(arc)
    if _is_zip(arc):
        with zipfile.ZipFile(arc) as z:
            return [i.filename for i in z.infolist() if not i.is_dir()]
    if seven is None:
        seven, why = find_7z()
        if seven is None:
            raise RuntimeError(f'7-Zip NOT FOUND ({why}) - cannot list {arc.name}; '
                               f'{SEVENZIP_HINT}')
    rc, out, err = _run_7z(seven, ['l', '-slt', '-ba', '-sccUTF-8', str(arc)])
    if rc != 0:
        raise RuntimeError(f'7z l failed (rc={rc}) on {arc}: {(err or out).strip()[:400]}')
    members = []
    block = {}
    for line in out.splitlines() + ['']:
        line = line.rstrip('\r')
        if not line.strip():
            if block:
                path = block.get('Path')
                is_dir = (block.get('Folder') == '+'
                          or block.get('Attributes', '').startswith('D'))
                if path and not is_dir:
                    members.append(path)
            block = {}
            continue
        if ' = ' in line:
            k, v = line.split(' = ', 1)
            block[k.strip()] = v.strip()
        elif line.endswith(' ='):
            block[line[:-2].strip()] = ''
    return members


def match_member(members, want):
    """The ONE member whose normalized path equals `want` or ends with '/' + `want`.
    Returns (member, None) or (None, reason). Two candidates = ambiguity = refused."""
    w = _norm(want)
    hits = [m for m in members if _norm(m) == w or _norm(m).endswith('/' + w)]
    if len(hits) == 1:
        return hits[0], None
    if not hits:
        return None, f'{want!r} not in the archive (no member ends with that path)'
    return None, (f'AMBIGUOUS: {len(hits)} members end with {want!r}, refusing to guess: '
                  + ', '.join(repr(h) for h in hits))


def _prune_empty_dirs(root: Path):
    """Remove empty directories under `root` bottom-up (rmdir only - never a recursive
    delete; anything left behind stays and is reported by the caller)."""
    if not root.is_dir():
        return
    for d in sorted((p for p in root.rglob('*') if p.is_dir()), key=lambda p: -len(p.parts)):
        try:
            d.rmdir()
        except OSError:
            pass
    try:
        root.rmdir()
    except OSError:
        pass


def _extract_zip_member(arc: Path, real: str, dest: Path):
    """Stream one zip member to `dest` (written as `<dest>.part`, then renamed)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + '.part')
    with zipfile.ZipFile(arc) as z, z.open(real) as src, part.open('wb') as dst:
        while True:
            chunk = src.read(1 << 22)
            if not chunk:
                break
            dst.write(chunk)
    if dest.exists():
        dest.unlink()
    part.replace(dest)


def _extract_7z_members(seven: Path, arc: Path, plan, staging: Path):
    """`7z x` the listed members into `staging`, then move each to its cache path.
    `plan` = [(key, real member, dest Path)]. Returns {key: error-or-None}."""
    staging.mkdir(parents=True, exist_ok=True)
    rc, out, err = _run_7z(seven, ['x', '-y', '-sccUTF-8', f'-o{staging}', str(arc)]
                           + [real for _k, real, _d in plan])
    errors = {}
    if rc != 0:
        msg = f'7z x failed (rc={rc}) on {arc.name}: {(err or out).strip()[:400]}'
        for key, _real, _dest in plan:
            errors[key] = msg
        return errors
    for key, real, dest in plan:
        src = staging / real.replace('\\', '/')
        if not src.is_file():
            errors[key] = f'7z x reported success but {real!r} is not in {staging}'
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            dest.unlink()
        shutil.move(str(src), str(dest))
        errors[key] = None
    _prune_empty_dirs(staging)
    if staging.exists():
        leftovers = [str(p) for p in staging.rglob('*') if p.is_file()]
        if leftovers:
            print(f'  EXTRACT: NOTE - staging dir {staging} still holds '
                  f'{len(leftovers)} file(s), left in place: {leftovers[:5]}')
    return errors


def extract_from_third_party(keys, dry_run=False):
    """Populate the rung-2 cache from third_party/ archives. Returns [(key, msg, ok)].

    Per input: skip when the cache already exists; take the FIRST PRESENT archive among
    its primary + alternate names (reported); list it; match the member as a normalized
    suffix (ambiguity refused); extract ONLY that member (grouped per archive so a solid
    .7z is decoded once); md5-verify against EXPECTED_MD5. A mismatch deletes nothing and
    is reported as a failure. `ok` False = something the operator must look at.
    """
    results = {}
    order = []
    per_archive = {}          # arc Path -> [(key, member, dest)]
    seven, seven_why = find_7z()

    for key in keys:
        inp = BY_KEY[key]
        order.append(key)
        if inp.cache is None:
            results[key] = ('resolved from an install location, not a repo cache', True)
            continue
        if inp.cache.is_file():
            results[key] = (f'already present: {inp.cache}', True)
            continue
        arcs = inp.archives()
        if not arcs:
            results[key] = ('no third_party archive for this input', True)
            continue
        present = [(lab, a, m) for lab, a, m in arcs if a.is_file()]
        if not present:
            searched = ', '.join(str(a) for _l, a, _m in arcs)
            results[key] = (f'no archive present (searched: {searched})', False)
            continue
        label, arc, member = present[0]
        if not _is_zip(arc) and seven is None:
            results[key] = (f'FAIL: {arc.name} is a {arc.suffix} archive and 7-Zip was NOT '
                            f'FOUND ({seven_why}) - {SEVENZIP_HINT}; nothing extracted for '
                            f'{inp.label}', False)
            continue
        if dry_run:
            results[key] = (f'WOULD extract {member} from {arc.name} [{label}] -> {inp.cache}',
                            True)
            continue
        per_archive.setdefault(arc, []).append((key, member, inp.cache, label))

    for arc, wants in per_archive.items():
        try:
            members = list_archive(arc, seven)
        except (RuntimeError, OSError, zipfile.BadZipFile) as e:
            for key, _m, _d, _l in wants:
                results[key] = (f'FAIL: cannot list {arc.name}: {e}', False)
            continue
        plan = []
        for key, member, dest, label in wants:
            real, why = match_member(members, member)
            if real is None:
                results[key] = (f'FAIL: {arc.name} [{label}]: {why}', False)
                continue
            plan.append((key, real, dest, label))
        if not plan:
            continue
        if _is_zip(arc):
            errors = {}
            for key, real, dest, _label in plan:
                try:
                    _extract_zip_member(arc, real, dest)
                    errors[key] = None
                except (OSError, zipfile.BadZipFile) as e:
                    errors[key] = f'zip extract failed: {e}'
        else:
            staging = cache_root() / '.svc_extract_tmp' / arc.stem
            errors = _extract_7z_members(seven, arc, [(k, r, d) for k, r, d, _l in plan],
                                         staging)
        for key, real, dest, label in plan:
            err = errors.get(key)
            if err:
                results[key] = (f'FAIL: {arc.name} [{label}] :: {real!r}: {err}', False)
                continue
            ok, detail = _hash_ok(key, dest)
            if ok:
                results[key] = (f'extracted {real!r} from {arc.name} [{label}] -> {dest} '
                                f'({detail})', True)
            else:
                results[key] = (f'FAIL: *** HASH MISMATCH *** {real!r} from {arc.name} '
                                f'[{label}] -> {dest} ({detail}); the file is LEFT IN PLACE '
                                f'(nothing deleted) and the ladder will REJECT it - wrong '
                                f'archive? check the outer md5 against the NAS README', False)
    return [(k, results[k][0], results[k][1]) for k in order]


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
    seven = None
    for label, arc, member in inp.archives():
        state = 'PRESENT' if arc.is_file() else 'absent'
        lines.append(f'         {n}. {label:<24} {arc} :: {member}  [{state}]')
        n += 1
        if arc.is_file():
            if _is_zip(arc):
                lines.append('            -> EXTRACTABLE: '
                             'py tools/check_build_inputs.py --all --extract')
            else:
                if seven is None:
                    seven = find_7z()
                if seven[0] is not None:
                    lines.append(f'            -> EXTRACTABLE (7-Zip via {seven[1]}): '
                                 'py tools/check_build_inputs.py --all --extract')
                else:
                    lines.append(f'            -> needs 7-Zip, NOT FOUND ({seven[1]}): '
                                 f'{SEVENZIP_HINT}, then '
                                 'py tools/check_build_inputs.py --all --extract')
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


def _selftest_archives(root: Path, check):
    """The archive-layer cases (BL-b102-DEBT-1), planted under `root` (a scratch dir,
    never the repo): every archive lives in `<root>/third_party`, every extraction lands
    under `<root>/cache`, through the same $SVC_THIRD_PARTY_DIR / $SVC_CACHE_ROOT
    overrides an operator uses for a scratch restore."""
    tp = root / 'third_party'
    cache = root / 'cache'
    tp.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    good = b'the real upstream database.arz bytes ' * 64
    bad = b'an impostor ' * 64
    good_md5 = hashlib.md5(good).hexdigest()

    def plant_zip(name, entries):
        p = tp / name
        with zipfile.ZipFile(p, 'w', zipfile.ZIP_DEFLATED) as z:
            for n, data in entries:
                z.writestr(n, data)
        return p

    def reg(key, cache_rel, archive, alts=()):
        BY_KEY[key] = Input(key, f'SELFTEST {key}', 'SVC_SELFTEST_' + key.strip('_').upper(),
                            cache_rel, archive_rel=(f'third_party/{archive}',
                                                    'Database/database.arz'),
                            archive_alts=tuple(f'third_party/{a}' for a in alts),
                            note='synthetic')
        EXPECTED_MD5[key] = good_md5
        return key

    saved = {k: os.environ.get(k) for k in (CACHE_ROOT_ENV, THIRD_PARTY_ENV, SEVENZIP_ENV)}
    os.environ[CACHE_ROOT_ENV] = str(cache)
    os.environ[THIRD_PARTY_ENV] = str(tp)
    os.environ.pop(SEVENZIP_ENV, None)
    keys = []
    try:
        # ARC-1: a nested top-level folder resolves by SUFFIX (the ModDB .7z layout), lands
        # at the cache path the ladder expects, and md5 == the pin.
        plant_zip('nested.zip', [('Some Mod v1/Readme.txt', b'hi'),
                                 ('Some Mod v1/Database/database.arz', good),
                                 ('Some Mod v1/Database/templates.arc', b'x')])
        k1 = reg('__st_nested__', 'upstream/__selftest__/nested/Database/database.arz',
                 'nested.zip')
        keys.append(k1)
        (key, msg, ok), = extract_from_third_party([k1])
        dest = BY_KEY[k1].cache
        check('ARC-1 nested-folder archive resolves by suffix', ok and dest.is_file(), msg[:120])
        check('ARC-1 landed bytes match the pin', dest.is_file() and md5(dest) == good_md5)
        check('ARC-1 landed under $SVC_CACHE_ROOT, not the repo',
              str(dest).startswith(str(cache)), str(dest))
        try:
            got = resolve(k1, verbose=False)
            check('ARC-1 the ladder then resolves the landed file (hashed)', got == dest)
        except MissingInput:
            check('ARC-1 the ladder then resolves the landed file (hashed)', False)

        # ARC-2: two members ending in the same suffix = ambiguity = REFUSED, both listed.
        plant_zip('ambig.zip', [('A/Database/database.arz', good),
                                ('B/Database/database.arz', good)])
        k2 = reg('__st_ambig__', 'upstream/__selftest__/ambig/Database/database.arz',
                 'ambig.zip')
        keys.append(k2)
        (key, msg, ok), = extract_from_third_party([k2])
        check('ARC-2 ambiguous suffix refused', not ok and 'AMBIGUOUS' in msg, msg[:160])
        check('ARC-2 refusal lists both members', 'A/Database' in msg and 'B/Database' in msg)
        check('ARC-2 nothing landed', not BY_KEY[k2].cache.exists())

        # ARC-3: a member whose bytes do not match the pin is refused; the file is left in
        # place (nothing deleted) and the ladder REJECTS it.
        plant_zip('badpin.zip', [('Database/database.arz', bad)])
        k3 = reg('__st_badpin__', 'upstream/__selftest__/badpin/Database/database.arz',
                 'badpin.zip')
        keys.append(k3)
        (key, msg, ok), = extract_from_third_party([k3])
        check('ARC-3 wrong pin refused (HASH MISMATCH)', not ok and 'HASH MISMATCH' in msg,
              msg[:120])
        check('ARC-3 mismatched file left in place, nothing deleted',
              BY_KEY[k3].cache.is_file())
        try:
            resolve(k3, verbose=False)
            check('ARC-3 the ladder rejects the mismatched file', False, 'resolved it')
        except MissingInput:
            check('ARC-3 the ladder rejects the mismatched file', True)

        # ARC-4: the flat .zip layout (the existing path) still resolves by exact name.
        plant_zip('flat.zip', [('Database/database.arz', good), ('Resources/Text_EN.arc', b'x')])
        k4 = reg('__st_flat__', 'upstream/__selftest__/flat/Database/database.arz', 'flat.zip')
        keys.append(k4)
        (key, msg, ok), = extract_from_third_party([k4])
        check('ARC-4 flat zip (existing layout) extracts, md5 == pin',
              ok and md5(BY_KEY[k4].cache) == good_md5, msg[:120])

        # ARC-5: alternates - primary absent, alternate present -> used and NAMED; then
        # both present -> the first (primary) wins.
        plant_zip('alternate.zip', [('Some Mod v1/Database/database.arz', good)])
        k5 = reg('__st_alt__', 'upstream/__selftest__/alt/Database/database.arz',
                 'primary.zip', alts=('alternate.zip',))
        keys.append(k5)
        (key, msg, ok), = extract_from_third_party([k5])
        check('ARC-5 alternate archive name used when the primary is absent',
              ok and 'alternate.zip' in msg and '(alternate)' in msg, msg[:140])
        BY_KEY[k5].cache.unlink()
        plant_zip('primary.zip', [('Database/database.arz', good)])
        (key, msg, ok), = extract_from_third_party([k5])
        check('ARC-5 first present archive wins (primary over alternate), reported',
              ok and 'primary.zip' in msg and 'alternate.zip' not in msg, msg[:140])

        # ARC-6: 7-Zip ABSENT and a non-zip archive needed = LOUD failure naming the
        # archive + the install hint (simulated with $SVC_7Z pointing at nothing).
        (tp / 'needs7z.7z').write_bytes(b'not really a 7z; never opened')
        k6 = reg('__st_no7z__', 'upstream/__selftest__/no7z/Database/database.arz',
                 'needs7z.7z')
        keys.append(k6)
        os.environ[SEVENZIP_ENV] = str(root / 'nonexistent-7z.exe')
        try:
            (key, msg, ok), = extract_from_third_party([k6])
            check('ARC-6 7-Zip absent: non-zip archive FAILS LOUD (not skipped)',
                  not ok and 'needs7z.7z' in msg and 'NOT FOUND' in msg, msg[:160])
            check('ARC-6 failure carries the install hint + $SVC_7Z',
                  'winget install 7zip.7zip' in msg and SEVENZIP_ENV in msg)
            check('ARC-6 nothing landed', not BY_KEY[k6].cache.exists())
            rep = _report_missing(BY_KEY[k6])
            check('ARC-6 the NOT FOUND report names the archive and the hint',
                  'needs7z.7z' in rep and 'winget install 7zip.7zip' in rep)
            # the zip path must keep working with 7-Zip absent (it never needs it)
            BY_KEY[k4].cache.unlink()
            (key, msg, ok), = extract_from_third_party([k4])
            check('ARC-6 .zip extraction does not need 7-Zip', ok, msg[:100])
        finally:
            os.environ.pop(SEVENZIP_ENV, None)

        # ARC-7: the real 7-Zip path - a .7z with ONE nested top-level folder, listed with
        # `7z l -slt -ba`, ONLY the needed member extracted, md5 == pin. 7-Zip missing on
        # this machine is a FAIL here: the resolver's contract now includes it.
        seven, why = find_7z()
        if seven is None:
            check('ARC-7 real .7z round trip (7-Zip present)', False,
                  f'7-Zip NOT FOUND ({why}); {SEVENZIP_HINT}')
        else:
            src = root / 'src7z' / 'Nested Mod v2'
            (src / 'Database').mkdir(parents=True, exist_ok=True)
            (src / 'Resources').mkdir(parents=True, exist_ok=True)
            (src / 'Database' / 'database.arz').write_bytes(good)
            (src / 'Database' / 'templates.arc').write_bytes(b'not wanted')
            (src / 'Resources' / 'Text_EN.arc').write_bytes(b'not wanted either')
            arc7 = tp / 'real.7z'
            if arc7.exists():
                arc7.unlink()
            rc, out, err = _run_7z(seven, ['a', '-t7z', '-y', str(arc7), 'Nested Mod v2'],
                                   cwd=str(root / 'src7z'))
            check('ARC-7 planted a nested .7z with 7-Zip', rc == 0 and arc7.is_file(),
                  (err or out).strip()[-120:])
            k7 = reg('__st_real7z__', 'upstream/__selftest__/real7z/Database/database.arz',
                     'real.7z')
            keys.append(k7)
            members = list_archive(arc7, seven)
            check('ARC-7 `7z l -slt -ba` lists files only (3 members, no dirs)',
                  len(members) == 3 and all('.' in Path(m).name for m in members),
                  str(members))
            (key, msg, ok), = extract_from_third_party([k7])
            dest = BY_KEY[k7].cache
            check('ARC-7 .7z nested member extracted via 7-Zip, md5 == pin',
                  ok and dest.is_file() and md5(dest) == good_md5, msg[:140])
            staging = cache / '.svc_extract_tmp'
            stray = [str(p) for p in staging.rglob('*')] if staging.exists() else []
            check('ARC-7 only the needed member landed; staging pruned (rmdir only)',
                  not stray, str(stray[:3]))
    finally:
        for k in keys:
            BY_KEY.pop(k, None)
            EXPECTED_MD5.pop(k, None)
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def selftest(root=None):
    """PLANTED NEGATIVE TESTS for the preflight itself (law #4: a new surface ships
    its gate). Runs entirely on synthetic inputs - touches no build artifact. `root` =
    the scratch dir the archive cases plant into (default: a temporary directory)."""
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

    # the archive layer (BL-b102-DEBT-1), planted under the scratch root
    if root is not None:
        r = Path(root) / 'selftest'
        r.mkdir(parents=True, exist_ok=True)
        print(f'  archive cases planted under {r}')
        _selftest_archives(r, check)
    else:
        with tempfile.TemporaryDirectory() as td:
            print(f'  archive cases planted under {td}')
            _selftest_archives(Path(td), check)
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--db', action='store_true', help='check the database-build inputs')
    ap.add_argument('--map', action='store_true', help='check the map-merge inputs')
    ap.add_argument('--text', action='store_true', help='check the text-arc inputs')
    ap.add_argument('--all', action='store_true', help='check every input (incl optional)')
    ap.add_argument('--extract', action='store_true',
                    help='populate the cache from third_party/ archives (.zip via zipfile; '
                         '.7z/.rar via 7-Zip; one nested top folder tolerated)')
    ap.add_argument('--dry-run', action='store_true', help='with --extract: report only')
    ap.add_argument('--verify-hashes', action='store_true',
                    help='md5 every resolved input, including caller-default locations')
    ap.add_argument('--cache-root', metavar='DIR',
                    help=f'rung-2 cache root (= ${CACHE_ROOT_ENV}); --extract writes here. '
                         'Default: this repo')
    ap.add_argument('--third-party', metavar='DIR',
                    help=f'the ONE archive dir to search (= ${THIRD_PARTY_ENV}). Default: '
                         '<repo>/third_party, then the main checkout\'s')
    ap.add_argument('--selftest', action='store_true',
                    help='run the planted negative tests for the resolver itself')
    ap.add_argument('--selftest-root', metavar='DIR',
                    help='with --selftest: the scratch dir the archive cases plant into '
                         '(default: a temporary directory)')
    args = ap.parse_args()

    if args.cache_root:
        os.environ[CACHE_ROOT_ENV] = str(Path(args.cache_root).resolve())
    if args.third_party:
        os.environ[THIRD_PARTY_ENV] = str(Path(args.third_party).resolve())

    if args.selftest:
        print('=== check_build_inputs SELFTEST (planted negative tests) ===')
        fails = selftest(args.selftest_root)
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

    extract_failed = []
    if args.extract:
        print('=== extract missing inputs from third_party/ ===')
        print(f'  cache root : {cache_root()}')
        print('  archives   : ' + ', '.join(f'{lab} {d}' for lab, d in third_party_dirs()))
        seven, why = find_7z()
        print(f'  7-Zip      : {seven if seven else "NOT FOUND"} ({why})')
        for key, msg, ok in extract_from_third_party(keys, dry_run=args.dry_run):
            print(f'  {key:<20} {msg}')
            if not ok:
                extract_failed.append(key)
        if extract_failed:
            print(f'  EXTRACT: FAIL - {len(extract_failed)} input(s) not restored: '
                  + ', '.join(extract_failed))
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
    if extract_failed:
        print(f'RESULT: FAIL - --extract could not restore: {", ".join(extract_failed)}')
        return 1
    print(f'RESULT: PASS ({len(keys)} input(s) resolvable)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
