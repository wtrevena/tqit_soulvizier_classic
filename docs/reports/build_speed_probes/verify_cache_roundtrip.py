"""Scoped BYTE-IDENTITY proof for the prefix snapshot cache (HOTSPOT 2a), runnable
WITHOUT a full 6-min build (build40 owns the machine). Proves the two things that
actually matter for the IRON LAW:

  TEST 1  static identity  - snapshot -> pickle -> restore -> write == direct write.
  TEST 2  CONTINUE-path identity - the restored mid-build state, run through the
          SAME further mutations the extended phase would apply (set_field/
          clone_record/ensure_string), writes byte-identical to the never-pickled
          db. This is the proof probe-06 (static-only) could NOT give and the one
          the prior-spec critic demanded.
  TEST 3  real store()/load() disk round-trip (atomic write + key verify) is md5-id.
  TEST 4  key invalidation logic: env flags + input md5 + source fingerprint all
          move the key; SVC_RELEASE_DROPS deliberately does NOT (post-snapshot).

The FINAL acceptance gate (cold-vs-warm FULL-build md5) is verify_cache_
determinism.py, which the integrator runs once build40 is done - a full build is
out of scope here. Read-only vs the repo (scratch outputs only). Memory-light:
one arz + a small decoded subset.

Usage:  py verify_cache_roundtrip.py <input.arz> <scratch_dir>
"""
import sys, os, hashlib, pickle, importlib.util
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[3] / 'tools'
sys.path.insert(0, str(TOOLS))
import arz_patcher as A
import prefix_cache as PC
from arz_patcher import (DATA_TYPE_INT, DATA_TYPE_FLOAT, DATA_TYPE_STRING)


def md5_file(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def load_and_seed(arz_path, n_modify=200):
    """Load the arz and modify a subset to build an interesting MID-BUILD state
    (decoded_cache + modified set populated), like the prefix would leave it."""
    db = A.ArzDatabase.from_arz(Path(arz_path))
    names = db.record_names()
    seed = names[:n_modify]
    for i, nm in enumerate(seed):
        db.set_field(nm, 'svcCacheSeedInt', i, DATA_TYPE_INT)
    return db, names


def snapshot_via_pickle(db):
    """Round-trip the db STATE through pickle exactly like the cache does."""
    state = PC._snapshot_db_state(db)
    return PC._restore_db(pickle.loads(pickle.dumps(state, pickle.HIGHEST_PROTOCOL)))


def mutate_continue(db, names):
    """A deterministic stand-in for the extended phase: new fields on existing
    records, cloned records, new strings. MUST be applied identically to both dbs."""
    targets = names[500:560]
    for nm in targets:
        db.set_field(nm, 'svcContinueInt', 4242, DATA_TYPE_INT)
        db.set_field(nm, 'svcContinueStr', 'svc_probe_' + nm[-6:], DATA_TYPE_STRING)
        db.set_field(nm, 'svcContinueFloat', 3.25, DATA_TYPE_FLOAT)
    for nm in names[600:610]:
        db.clone_record(nm, nm + '_svccacheclone')
    for k in range(50):
        db.ensure_string(f'svc_cache_probe_string_{k}')


def write_md5(db, out):
    db.write_arz(Path(out))
    return md5_file(out)


def test_1(arz, scratch):
    print("=== TEST 1: static snapshot identity ===")
    db = load_and_seed(arz)[0]
    db_b = snapshot_via_pickle(db)              # snapshot BEFORE any write
    a = write_md5(db, scratch / 't1_direct.arz')
    b = write_md5(db_b, scratch / 't1_restore.arz')
    print(f"  direct : {a}\n  restore: {b}\n  IDENTICAL: {a == b}")
    return a == b


def test_2(arz, scratch):
    print("\n=== TEST 2: CONTINUE-path identity (restored state + further mutation) ===")
    db, names = load_and_seed(arz)
    db_b = snapshot_via_pickle(db)              # snapshot BEFORE the continue phase
    mutate_continue(db, names)                  # identical mutations on both
    mutate_continue(db_b, names)
    a = write_md5(db, scratch / 't2_direct.arz')
    b = write_md5(db_b, scratch / 't2_restore.arz')
    print(f"  direct+mut : {a}\n  restore+mut: {b}\n  IDENTICAL: {a == b}")
    return a == b


def test_3(arz, scratch):
    print("\n=== TEST 3: real store()/load() disk round-trip ===")
    os.environ['SVC_PREFIX_CACHE'] = '1'
    os.environ.pop('SVC_NO_CACHE', None)
    os.environ.pop('SVC_CACHE_REFRESH', None)
    db, names = load_and_seed(arz)
    pfx = {'db': db, 'db09': None, 'db41': None, 'souls': [{'x': 1}],
           'text_tags': [('t', 'v')], 'legacy_tags': {}, 'thrown_tags': {},
           'graft_tags': {}, 'base_names_low': {'a\\b'},
           'sv098i_all_paths': {'p1'}, 'sv098i_soul_paths': {'p2'}}
    key = 'roundtrip_test_key_' + '0' * 16
    PC.store(key, pfx)
    got = PC.load(key)
    ok_side = (got['souls'] == pfx['souls'] and got['text_tags'] == pfx['text_tags']
               and got['sv098i_soul_paths'] == pfx['sv098i_soul_paths']
               and got['db09'] is None and got['db41'] is None)
    a = write_md5(db, scratch / 't3_direct.arz')
    b = write_md5(got['db'], scratch / 't3_loaded.arz')
    print(f"  direct: {a}\n  loaded: {b}\n  db IDENTICAL: {a == b}   side-outputs OK: {ok_side}")
    try: (PC._snapshot_path(key)).unlink()
    except OSError: pass
    return a == b and ok_side


def test_4():
    print("\n=== TEST 4: key invalidation logic ===")
    saved_env = {k: os.environ.get(k) for k in
                 ('SVC_GRAFT_SVAERA', 'SVC_RESTORE_DROPPED_NPCS', 'SVC_RELEASE_DROPS')}
    saved_fns = (PC._file_md5, PC._tools_source_fingerprint, PC.resolve_svaera_arz)
    md5map = {'sv098': 'A', 'sv09': 'B', 'sv041': 'C', 'base': 'D', 'svaera': 'S'}
    PC._file_md5 = lambda p: md5map.get(str(p), 'X')
    PC._tools_source_fingerprint = lambda: 'SRCFP'
    PC.resolve_svaera_arz = lambda: 'svaera'
    def key(**env):
        for k in saved_env:
            os.environ.pop(k, None)
        for k, v in env.items():
            os.environ[k] = v
        return PC.compute_key('sv098', 'sv09', 'sv041', 'base')
    results = {}
    base = key(SVC_GRAFT_SVAERA='1')
    results['stable']          = (base == key(SVC_GRAFT_SVAERA='1'))
    results['graft_flip']      = (base != key(SVC_GRAFT_SVAERA='0'))
    results['restore_flip']    = (base != key(SVC_GRAFT_SVAERA='1', SVC_RESTORE_DROPPED_NPCS='1'))
    results['release_ignored'] = (base == key(SVC_GRAFT_SVAERA='1', SVC_RELEASE_DROPS='0'))
    # input arz md5 sensitivity
    PC._file_md5 = lambda p: (md5map.get(str(p), 'X') if str(p) != 'base' else 'D2')
    results['base_md5_moves']  = (base != key(SVC_GRAFT_SVAERA='1'))
    PC._file_md5 = lambda p: md5map.get(str(p), 'X')
    # source fingerprint sensitivity
    PC._tools_source_fingerprint = lambda: 'SRCFP2'
    results['src_moves']       = (base != key(SVC_GRAFT_SVAERA='1'))
    PC._tools_source_fingerprint = lambda: 'SRCFP'
    # svaera md5: matters when graft ON, ignored when graft OFF
    off = key(SVC_GRAFT_SVAERA='0')
    PC.resolve_svaera_arz = lambda: 'svaera2'
    results['svaera_moves_on'] = (base != key(SVC_GRAFT_SVAERA='1'))
    results['svaera_ign_off']  = (off == key(SVC_GRAFT_SVAERA='0'))
    # restore
    PC._file_md5, PC._tools_source_fingerprint, PC.resolve_svaera_arz = saved_fns
    for k, v in saved_env.items():
        if v is None: os.environ.pop(k, None)
        else: os.environ[k] = v
    for name, ok in results.items():
        print(f"  {name:18s}: {ok}")
    return all(results.values())


if __name__ == '__main__':
    arz = Path(sys.argv[1])
    scratch = Path(sys.argv[2]); scratch.mkdir(parents=True, exist_ok=True)
    r1 = test_1(arz, scratch)
    r2 = test_2(arz, scratch)
    r3 = test_3(arz, scratch)
    r4 = test_4()
    print(f"\nRESULT: static={r1} continue={r2} store_load={r3} key_logic={r4}")
    sys.exit(0 if (r1 and r2 and r3 and r4) else 1)
