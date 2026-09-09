r"""patch_deployed_arz - apply ONE registry module to an ALREADY-DEPLOYED .arz.

WHY THIS EXISTS (b92, 2026-07-28)
---------------------------------
Parallel lanes share one DEV custom-map folder. When b92 was ready to deploy,
`CustomMaps/SoulvizierClassicDEV/Database/SoulvizierClassicDEV.arz` had just been
replaced by ANOTHER lane's integration build carrying 13 records and 28 field
edits that are not on `main`. Copying this lane's own build over it would have
silently DELETED that lane's live work; waiting would have blocked Will's test.

This tool is the non-destructive third option: it loads the artifact that is
actually deployed, runs a registry module's OWN `apply()` + `verify()` against
it - so the module's preconditions, blast-radius proof and gate all still run -
and writes the result back atomically, with a backup and a record-diff proof.
The result is EXACTLY "what is deployed, plus this module", which is what a
merge of the two lanes would have produced for these records.

It is deliberately narrow and loud:
  * the module's apply() aborts if its preconditions do not hold;
  * the record-diff is printed and compared against the module's TARGETS;
  * --apply is required to write anything (default is a dry run);
  * the target is backed up first and md5-verified after.

USAGE
    py tools/patch_deployed_arz.py --module toxeus_mesh_aura \
        --arz "<...>/SoulvizierClassicDEV.arz" [--backup <path>] [--apply]

NOT a substitute for a real build. The reproducible artifact is always the
branch build; this only reconciles a shared DEV folder between lanes.
"""
import argparse
import hashlib
import importlib
import os
import shutil
import sys
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

from arz_patcher import ArzDatabase  # noqa: E402


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def field_map(db):
    """record -> {field: value} for every record, for the diff."""
    out = {}
    for n in db.record_names():
        f = db.get_fields(n)
        if not f:
            continue
        out[n] = {k: tuple(v.values or []) for k, v in f.items()}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--module', required=True, help='tools/patches/<name>.py')
    ap.add_argument('--arz', required=True, help='the DEPLOYED .arz to patch')
    ap.add_argument('--backup', help='where to copy the pre-patch file (default: alongside)')
    ap.add_argument('--apply', action='store_true', help='actually write (default: dry run)')
    args = ap.parse_args()

    mod = importlib.import_module(f'patches.{args.module}')
    src = os.path.abspath(args.arz)
    print(f'MODULE {args.module}  ({getattr(mod, "MODULE_NAME", "?")})')
    print(f'TARGET {src}\n       {os.path.getsize(src):,} B  md5 {md5(src)}')

    db = ArzDatabase.from_arz(Path(src))
    before = field_map(db)

    mod.apply(db, {})          # the module's own preconditions + blast-radius proof
    mod.verify(db, {})         # the module's own gate

    after = field_map(db)
    changed = {}
    for n in set(before) | set(after):
        b, a = before.get(n, {}), after.get(n, {})
        d = {k: (b.get(k), a.get(k)) for k in set(b) | set(a) if b.get(k) != a.get(k)}
        if d:
            changed[n] = d

    expected = sorted(r for _, r in getattr(mod, 'TARGETS', []))
    print(f'\nRECORD DIFF vs the deployed file: {len(changed)} modified, '
          f'0 added, 0 removed (this tool never adds or removes records)')
    for n in sorted(changed):
        for k, (b, a) in sorted(changed[n].items()):
            print(f'  ~ {n}\n      {k}: {b} -> {a}')
    if expected and sorted(changed) != expected:
        print('\nABORT: the changed set is not exactly the module TARGETS.')
        print(f'  stray:  {[n for n in sorted(changed) if n not in expected]}')
        print(f'  missed: {[n for n in expected if n not in changed]}')
        return 2

    if not args.apply:
        print('\nDRY RUN - nothing written. Re-run with --apply.')
        return 0

    backup = args.backup or (src + '.prepatch')
    shutil.copy2(src, backup)
    print(f'\nbackup -> {backup}  md5 {md5(backup)}')

    tmp = src + '.tmp_patch'
    db.write_arz(Path(tmp))
    written = md5(tmp)
    os.replace(tmp, src)
    final = md5(src)
    if final != written:
        print(f'ABORT: post-replace md5 {final} != written {written}')
        return 3
    print(f'WROTE  {src}\n       {os.path.getsize(src):,} B  md5 {final}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
