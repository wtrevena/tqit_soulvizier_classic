r"""probe_rig_bones - R-102: prove a mesh swap does not break the animation rig.

R-102's fourth amendment: "THE REAL RISK IS ANIMATION, NOT COLOUR. A mesh swap
re-rigs everything: the Enslaver's inline animation rows and every skill that
names a specific anim must still resolve, or he T-poses or goes uncastable."

An `.anm` clip drives a mesh by BONE NAME. A clip binds cleanly iff every bone
the clip animates exists on the mesh. This probe extracts the bone-name table
out of the `.msh` / `.anm` binaries (they are stored as NUL-terminated ASCII in
both formats) and set-compares them, so "the new mesh carries the old rig" is a
measured claim rather than a folder-name guess.

Usage:
  py tools/debug/probe_rig_bones.py --mesh "Creatures\Monster\Skeleton\RevenantPoison.msh" \
                                    --mesh "Creatures\Monster\Skeleton\SkeletonGrayBlack01New.msh"
  py tools/debug/probe_rig_bones.py --compare-anms "Creatures\Monster\Skeleton\ANM"
"""
import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arc_patcher import ArcArchive  # noqa: E402

GAME = Path(os.environ.get(
    'SVC_TQAE_DIR',
    r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition'))

ARC_DIRS = [GAME / 'Resources',
            GAME / 'Resources' / 'xpack',
            GAME / 'Resources' / 'XPack2',
            GAME / 'Resources' / 'XPack3',
            GAME / 'Resources' / 'XPack4']

# TQ rig bone names: "Bone_..." plus the root/attach helpers the exporter emits.
_BONE = re.compile(rb'(?:Bone_[A-Za-z0-9_]+|Smoke\d+|Waist|Root|Scene_Root)\x00')
_STR = re.compile(rb'[ -~]{3,}')


def _key(dbr_path):
    p = str(dbr_path).lower().replace('/', '\\').lstrip('\\')
    head = p.split('\\', 1)
    return head[0], (head[1] if len(head) > 1 else '')


_CACHE = {}


def _arc(archive_name):
    """Load `<archive_name>.arc` from whichever Resources dir has it."""
    an = archive_name.lower()
    if an in _CACHE:
        return _CACHE[an]
    for d in ARC_DIRS:
        p = d / (archive_name + '.arc')
        if p.exists():
            _CACHE[an] = (p, ArcArchive.from_file(p))
            return _CACHE[an]
    # fall back: the mod's own resources (drx.arc et al.)
    for extra in (Path('work/SoulvizierClassic/Resources'),
                  Path('local/SoulvizierClassic/Resources')):
        p = extra / (archive_name + '.arc')
        if p.exists():
            _CACHE[an] = (p, ArcArchive.from_file(p))
            return _CACHE[an]
    _CACHE[an] = (None, None)
    return _CACHE[an]


def read_asset(dbr_path):
    """Bytes of an art asset addressed the way a .dbr addresses it."""
    arcname, inner = _key(dbr_path)
    p, a = _arc(arcname)
    if a is None:
        return None, None
    for e in a.entries:
        if e.entry_type == 3 and e.name.lower().replace('/', '\\') == inner:
            return a.get_file(e.name), p
    return None, p


def bones_of(data):
    return sorted({m.group(0)[:-1].decode('ascii') for m in _BONE.finditer(data)})


def strings_of(data, limit=None):
    out = sorted({s.decode('ascii', 'replace') for s in _STR.findall(data)})
    return out[:limit] if limit else out


def list_dir(dbr_dir):
    """Every asset under an addressed directory, as .dbr-style paths."""
    arcname, inner = _key(dbr_dir.rstrip('\\') + '\\')
    p, a = _arc(arcname)
    if a is None:
        return []
    out = []
    for e in a.entries:
        n = e.name.lower().replace('/', '\\')
        if e.entry_type == 3 and n.startswith(inner):
            out.append(arcname + '\\' + e.name)
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mesh', action='append', default=[])
    ap.add_argument('--anm', action='append', default=[])
    ap.add_argument('--anm-dir', default=None)
    ap.add_argument('--show-bones', action='store_true')
    args = ap.parse_args()

    meshes = {}
    for m in args.mesh:
        data, arcp = read_asset(m)
        if data is None:
            print('MISSING MESH: %s' % m)
            continue
        meshes[m] = bones_of(data)
        print('\n%-62s %8d B  %d bones   (%s)'
              % (m, len(data), len(meshes[m]), arcp.name if arcp else '?'))
        if args.show_bones:
            for b in meshes[m]:
                print('      %s' % b)

    if len(meshes) >= 2:
        base = list(meshes)[0]
        bb = set(meshes[base])
        print('\n=== RIG COMPARISON, reference = %s ===' % base)
        for m in list(meshes)[1:]:
            mb = set(meshes[m])
            print('%s' % m)
            print('   identical rig: %s' % (mb == bb))
            print('   missing vs reference (%d): %s'
                  % (len(bb - mb), sorted(bb - mb)[:20]))
            print('   extra   vs reference (%d): %s'
                  % (len(mb - bb), sorted(mb - bb)[:20]))

    anms = list(args.anm)
    if args.anm_dir:
        anms += [a for a in list_dir(args.anm_dir) if a.lower().endswith('.anm')]
    if anms and meshes:
        print('\n=== ANM BINDING, %d clip(s) vs %d mesh(es) ==='
              % (len(anms), len(meshes)))
        for a in anms:
            data, _ = read_asset(a)
            if data is None:
                print('  MISSING ANM: %s' % a)
                continue
            ab = set(bones_of(data))
            row = []
            for m, mbones in meshes.items():
                miss = ab - set(mbones)
                row.append('%s=%s' % (m.rsplit('\\', 1)[-1],
                                      'OK' if not miss else 'MISS%d' % len(miss)))
            print('  %-46s %3d bones  %s' % (a.rsplit('\\', 1)[-1], len(ab),
                                             '  '.join(row)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
