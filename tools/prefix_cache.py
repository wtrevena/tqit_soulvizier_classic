"""Build-speed PREFIX SNAPSHOT CACHE for build_svc_database.py (HOTSPOT 2a).

The .arz build is a linear chain of pure mutations over one ArzDatabase. Its
INVARIANT PREFIX - loading the 4 upstream/base arzs (~51k SV records + the ~74k
record base game DB) and running the deterministic assembly through
create_uber_souls (~77 s) - is recomputed on EVERY build before any build-specific
work. This module snapshots the assembled state at that boundary, keyed by a hash
of every input that determines it, so a rebuild with unchanged prefix inputs skips
the reload + reassembly (and, on a HIT, never co-resides the 4 source DBs -> lower
memory peak).

=========================  BYTE-IDENTITY LAW  =========================
A cache HIT MUST produce the EXACT same final .arz as a cold build. That holds
because:
  (1) The snapshot is a LOSSLESS pickle of the 7 ArzDatabase fields write_arz
      depends on (strings, string_to_id, _raw_records, _decoded_cache,
      _record_types, _record_timestamps, _modified) PLUS every prefix side-output
      (souls/text/legacy/thrown/graft tag dicts, base_names_low, and the
      _SV098I_* soul-provenance sets). Round-trip byte-identity - including
      running the ~322 s extended phase's further mutations on the RESTORED state -
      is proven in docs/reports/build_speed_probes/verify_cache_roundtrip.py.
  (2) The KEY covers every input that can change the prefix: the input arz md5s,
      the prefix ENV flags (SVC_GRAFT_SVAERA / SVC_RESTORE_DROPPED_NPCS - a flip is
      otherwise a silent WRONG HIT), and the hash of the whole tools/ source tree
      (a conservative SUPERSET - any prefix-code change is a MISS). So staleness is
      always a MISS, never a wrong HIT. SVC_RELEASE_DROPS / SVC_TESTING_DROPS are
      DELIBERATELY excluded: they gate only the post-snapshot extended phase, which
      re-runs every build, so a HIT under a different drops flag is still correct.

The cache is ADVISORY: any miss / corrupt / renamed / key-mismatch snapshot falls
back to a full cold build (broad except -> None). It NEVER changes output bytes; a
bug can only cost time, not correctness (guarded by verify_cache_determinism.py).

HIT-RATE NOTE (honest): because the key includes the churny apply_svc_patches.py
(hashed as part of the whole tools/ tree - the sound choice absent the §3.6 module
split), editing DB content busts the cache. The cache therefore HITS on rebuilds
whose DB source is unchanged (iterating downstream map/text/quest tooling, or
re-running an identical build) - and on every HIT also removes the 4-DB memory
co-residence. Widening the hit set needs the module split (out of this scope).

Controls (env):
  SVC_PREFIX_CACHE=0   opt OUT (default is ON since 2026-07-14: the
                       verify_cache_determinism.py full-build gate PASSed on main
                       @ 7c38c9e - cold 209s and warm 134s both produced arz md5
                       b33c5a447f3a8ca652c14f78d4ad1dd4 == build40 GOLDEN, tags
                       md5 fe855a77324e99cc37ea3326c0cdc2b2 identical, warm HIT
                       log-proven, graft-flip negative test forced a key MISS).
                       Unset/empty = ON; 0/false/no/off = OFF; other values go
                       through the same truthy parse (non-truthy = OFF).
  SVC_NO_CACHE=1       hard-disable read AND write even if enabled.
  SVC_CACHE_REFRESH=1  ignore any existing snapshot (force MISS) but still store.
"""
import os
import sys
import hashlib
import pickle
import tempfile
from pathlib import Path

_TRUE = ('1', 'true', 'yes', 'on')
_FALSE = ('', '0', 'false', 'no', 'off')
_KEY_VERSION = b"svc-prefix-snapshot-v1\0"
_RETAIN = 4  # keep the N most-recently-used snapshots (parallel-wave friendly)


def _truthy(raw) -> bool:
    return raw is not None and raw.strip().lower() in _TRUE


def _norm_bool_env(name: str, default: str) -> str:
    """Normalize a bool env var to 'on'/'off' the same way the build reads it, so
    the key is stable across equivalent spellings (1/true/on -> on)."""
    raw = os.environ.get(name)
    if raw is None or raw.strip() == '':
        raw = default
    return 'on' if raw.strip().lower() in _TRUE else 'off'


def enabled() -> bool:
    """True iff the cache should read+write. Default ON (flipped 2026-07-14 after
    verify_cache_determinism.py PASSed cold==warm==GOLDEN on main @ 7c38c9e);
    opt out with SVC_PREFIX_CACHE=0/off. SVC_NO_CACHE hard-wins."""
    if _truthy(os.environ.get('SVC_NO_CACHE')):
        return False
    raw = os.environ.get('SVC_PREFIX_CACHE')
    if raw is None or raw.strip() == '':
        return True
    return _truthy(raw)


def graft_on() -> bool:
    """Mirror build_svc_database's SVC_GRAFT_SVAERA read (default ON)."""
    v = os.environ.get('SVC_GRAFT_SVAERA', '1').strip().lower()
    return v not in ('0', 'false', 'no', 'off')


def _cache_dir() -> Path:
    d = Path(__file__).resolve().parent.parent / '.build_cache'
    d.mkdir(parents=True, exist_ok=True)
    return d


def _file_md5(path) -> str:
    if not path:
        return 'none'
    p = Path(path)
    if not p.exists():
        return 'absent'
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def _tools_source_fingerprint() -> str:
    """sha256 over every tools/**/*.py (path + content), sorted. A conservative
    SUPERSET of the prefix's source: any change to build code is a MISS. Cannot
    miss a reached module (unlike a hand-curated file list)."""
    tools = Path(__file__).resolve().parent
    h = hashlib.sha256()
    for py in sorted(tools.rglob('*.py'), key=lambda p: str(p).lower()):
        rel = str(py.relative_to(tools)).replace('\\', '/').lower()
        h.update(rel.encode() + b'\0')
        h.update(hashlib.sha256(py.read_bytes()).digest())
    return h.hexdigest()


def resolve_svaera_arz():
    """Best-effort resolve the SVAERA source arz (for the key) when the graft is
    on; None if unavailable. Uses the same resolver the build uses."""
    try:
        from restore_dropped_npcs import find_svaera_arz
        return find_svaera_arz()
    except Exception:
        return None


def compute_key(sv098_path, sv09_path, sv041_path, base_path) -> str:
    """Deterministic key over all prefix inputs. See the module docstring for the
    soundness argument (env fingerprint + conditional svaera + tools/ superset)."""
    h = hashlib.sha256()
    h.update(_KEY_VERSION)
    h.update(b'hashseed=' + os.environ.get('PYTHONHASHSEED', '').encode() + b'\0')
    # prefix ENV fingerprint (MANDATORY - a flip is otherwise a silent wrong hit)
    h.update(b'graft=' + _norm_bool_env('SVC_GRAFT_SVAERA', '1').encode() + b'\0')
    h.update(b'restore_npcs=' + _norm_bool_env('SVC_RESTORE_DROPPED_NPCS', '0').encode() + b'\0')
    # input arz md5s (svaera only when the graft is on - it is a prefix input only then)
    for label, p in (('sv098', sv098_path), ('sv09', sv09_path),
                     ('sv041', sv041_path), ('base', base_path)):
        h.update(f'{label}='.encode() + _file_md5(p).encode() + b'\0')
    if graft_on():
        h.update(b'svaera=' + _file_md5(resolve_svaera_arz()).encode() + b'\0')
    else:
        h.update(b'svaera=off\0')
    # prefix source (conservative superset)
    h.update(b'src=' + _tools_source_fingerprint().encode() + b'\0')
    return h.hexdigest()


# ------------------------------------------------------------------- db snapshot
def _snapshot_db_state(db) -> dict:
    """The 7 ArzDatabase fields that fully determine write_arz output + all
    downstream mutation. Nothing else in ArzDatabase affects bytes."""
    return {
        'strings': db.strings,
        'string_to_id': db.string_to_id,
        'raw_records': db._raw_records,
        'decoded_cache': db._decoded_cache,
        'record_types': db._record_types,
        'record_timestamps': db._record_timestamps,
        'modified': db._modified,
    }


def _restore_db(state: dict):
    from arz_patcher import ArzDatabase
    db = ArzDatabase()
    db.strings = state['strings']
    db.string_to_id = state['string_to_id']
    db._raw_records = state['raw_records']
    db._decoded_cache = state['decoded_cache']
    db._record_types = state['record_types']
    db._record_timestamps = state['record_timestamps']
    db._modified = state['modified']
    return db


# Keys of the prefix payload dict shared by _run_prefix (MISS) and load (HIT).
_PAYLOAD_SIDE_KEYS = ('souls', 'text_tags', 'legacy_tags', 'thrown_tags',
                      'graft_tags', 'base_names_low', 'sv098i_all_paths',
                      'sv098i_soul_paths')


def _snapshot_path(key: str) -> Path:
    return _cache_dir() / f'prefix-{key[:16]}.pkl'


def store(key: str, pfx: dict) -> None:
    """Pickle the prefix payload (db STATE + side outputs) atomically. Never
    raises into the build (advisory)."""
    try:
        payload = {'key': key, 'db_state': _snapshot_db_state(pfx['db'])}
        for k in _PAYLOAD_SIDE_KEYS:
            payload[k] = pfx.get(k)
        path = _snapshot_path(key)
        fd, tmp = tempfile.mkstemp(prefix=path.name + '.tmp.', dir=str(path.parent))
        try:
            with os.fdopen(fd, 'wb') as f:
                pickle.dump(payload, f, pickle.HIGHEST_PROTOCOL)  # streamed, low peak
            os.replace(tmp, path)   # atomic; a concurrent reader never sees a torn file
        finally:
            if os.path.exists(tmp):
                try: os.remove(tmp)
                except OSError: pass
        _prune()
        print(f"  prefix-cache: STORED snapshot {path.name}")
    except Exception as e:
        print(f"  prefix-cache: store skipped ({e})")


def load(key: str):
    """Return a prefix payload dict shaped exactly like _run_prefix's result
    (db object + db09=db41=None + side outputs), or None on any miss/error/refresh.
    A stored-key mismatch is refused (defends a hand-copied file)."""
    if _truthy(os.environ.get('SVC_CACHE_REFRESH')):
        print("  prefix-cache: SVC_CACHE_REFRESH set -> forced MISS")
        return None
    path = _snapshot_path(key)
    if not path.exists():
        print(f"  prefix-cache: MISS ({path.name} absent)")
        return None
    try:
        with open(path, 'rb') as f:
            payload = pickle.load(f)
        if payload.get('key') != key:
            print("  prefix-cache: MISS (stored key mismatch - refusing)")
            return None
        os.utime(path, None)  # bump mtime for LRU retention
        out = {'db': _restore_db(payload['db_state']), 'db09': None, 'db41': None}
        for k in _PAYLOAD_SIDE_KEYS:
            out[k] = payload.get(k)
        print(f"  prefix-cache: HIT {path.name} (skipped load + prefix)")
        return out
    except Exception as e:
        print(f"  prefix-cache: MISS (unreadable snapshot: {e})")
        return None


def _prune() -> None:
    """Keep only the _RETAIN most-recently-used snapshots (by mtime). Non-fatal."""
    try:
        snaps = sorted(_cache_dir().glob('prefix-*.pkl'),
                       key=lambda p: p.stat().st_mtime, reverse=True)
        for old in snaps[_RETAIN:]:
            try: old.unlink()
            except OSError: pass
    except Exception:
        pass
