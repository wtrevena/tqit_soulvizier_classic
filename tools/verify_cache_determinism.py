"""ACCEPTANCE GATE for the prefix snapshot cache: prove a warm (cache HIT) build is
BYTE-IDENTICAL to a cold build, on the REAL full build. This is the determinism law
applied to the cache and the gate that must be green before the cache default is
flipped to ON. It runs FULL builds, so it belongs to the integrator on a clean
machine (NOT during a concurrent heavy build).

What it does (PYTHONHASHSEED pinned by build_svc_database itself):
  1. COLD  : SVC_PREFIX_CACHE=1 SVC_CACHE_REFRESH=1  -> forces a MISS, runs the real
             prefix, STORES the snapshot. Records md5(out) + md5(uber_soul_tags.txt).
  2. WARM  : SVC_PREFIX_CACHE=1                       -> HITs the stored snapshot.
  3. ASSERT md5_cold == md5_warm  AND  tags_cold == tags_warm.  Any diff = FAIL.
  4. ENV-FLIP negative test (guards the wrong-hit class): rebuild with
     SVC_GRAFT_SVAERA=0 and assert the arz md5 DIFFERS from the graft-ON md5 (i.e.
     the flag flip forced a fresh cold result, not a stale graft-ON HIT).

Usage:
  py verify_cache_determinism.py <sv098.arz> <sv09.arz> <sv041.arz> <base.arz> <workdir>

Exit 0 = PASS (cache is byte-identical). Non-zero = FAIL (do NOT enable the cache).
"""
import sys, os, subprocess, hashlib, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE / 'build_svc_database.py'


def md5(p):
    if not Path(p).exists():
        return None
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def run_build(sv098, sv09, sv041, base, out_arz, env_extra):
    env = dict(os.environ)
    env['PYTHONHASHSEED'] = '0'
    env['PYTHONIOENCODING'] = 'utf-8'
    env.update(env_extra)
    Path(out_arz).parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(BUILD), sv098, sv09, sv041, str(out_arz), base]
    print(f"\n>>> build ({env_extra}) -> {out_arz}")
    r = subprocess.run(cmd, env=env)
    if r.returncode != 0:
        raise SystemExit(f"build FAILED (exit {r.returncode}) for env {env_extra}")
    return out_arz


def main():
    if len(sys.argv) < 6:
        print(__doc__)
        sys.exit(2)
    sv098, sv09, sv041, base, workdir = sys.argv[1:6]
    wd = Path(workdir)
    cold = wd / 'cold' / 'SoulvizierClassic.arz'
    warm = wd / 'warm' / 'SoulvizierClassic.arz'
    graftoff = wd / 'graftoff' / 'SoulvizierClassic.arz'

    # 1. COLD (forces a MISS + stores the snapshot)
    run_build(sv098, sv09, sv041, base, cold,
              {'SVC_PREFIX_CACHE': '1', 'SVC_CACHE_REFRESH': '1'})
    md5_cold = md5(cold)
    tags_cold = md5(cold.parent / 'uber_soul_tags.txt')

    # 2. WARM (HIT)
    run_build(sv098, sv09, sv041, base, warm, {'SVC_PREFIX_CACHE': '1'})
    md5_warm = md5(warm)
    tags_warm = md5(warm.parent / 'uber_soul_tags.txt')

    print("\n================ RESULT ================")
    print(f"  arz  cold: {md5_cold}")
    print(f"  arz  warm: {md5_warm}")
    print(f"  tags cold: {tags_cold}")
    print(f"  tags warm: {tags_warm}")
    ok = (md5_cold == md5_warm and tags_cold == tags_warm
          and md5_cold is not None)
    print(f"  COLD == WARM (arz + tags): {ok}")

    # 4. ENV-FLIP negative test (only meaningful if the graft was on for cold/warm)
    graft_on = os.environ.get('SVC_GRAFT_SVAERA', '1').strip().lower() \
        not in ('0', 'false', 'no', 'off')
    flip_ok = True
    if graft_on:
        run_build(sv098, sv09, sv041, base, graftoff,
                  {'SVC_PREFIX_CACHE': '1', 'SVC_GRAFT_SVAERA': '0'})
        md5_off = md5(graftoff)
        flip_ok = (md5_off is not None and md5_off != md5_cold)
        print(f"  arz graft-OFF: {md5_off}")
        print(f"  GRAFT flip forces a DIFFERENT result (no stale hit): {flip_ok}")
    else:
        print("  (graft already off; skipped the graft-flip negative test)")

    passed = ok and flip_ok
    print("========================================")
    print("PASS" if passed else "FAIL")
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
