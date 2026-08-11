r"""NEGATIVE TEST: art-asset resolution must shadow PER ENTRY, not per archive.

WHY THIS EXISTS. `tools/mesh_assets.py` resolves a `.dbr`-style art reference
(`Creatures\Monster\JackalMan\ANM\JackalMan_Walk.anm`) by finding the archive
named by the reference's first path component. The mod stages its own archives
under `work\<mod>\Resources`, and since the 2026-08-06 PR-2 dye layer one of them
is called `Creatures.arc` - an ADDITIVE 288-entry archive of PC costume skins that
sits beside the base game's 3,520-entry `Creatures.arc`.

The resolver used to take the FIRST archive with a matching NAME and stop. With
the dye layer staged, that meant every base-game creature asset resolved to
"missing", which made `champion_mesh.verify` emit 65 bogus "UNRESOLVED ANIMATION"
offenders and fail a build whose change had nothing to do with animation. The
engine does not behave that way: an additive archive adds entries, it does not
delete the base archive's.

WHAT THIS ASSERTS (2 positive controls + 3 planted regressions that must be RED):
  P1  a BASE-GAME-only asset resolves, and resolves out of the BASE archive.
  P2  a MOD-only asset resolves, and resolves out of the MOD archive
      (mod archives still win for every entry they actually carry).
  N1  a genuinely absent asset still does NOT resolve (the gate is not neutered).
  N2  the OLD first-archive-only algorithm, replayed here, FAILS to find the
      base-game asset - i.e. this test would catch a revert.
  N3  an archive name that exists nowhere resolves to nothing, with no crash.

Usage:  py tools/debug/negtest_arc_chain_resolution.py
Exit 0 == all controls green and all plants red.
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))
os.chdir(REPO)                      # mod_resource_dirs() globs relative to CWD

import mesh_assets as MA            # noqa: E402
from arc_patcher import ArcArchive  # noqa: E402

BASE_ONLY = r'Creatures\Monster\JackalMan\ANM\JackalMan_Walk.anm'
ABSENT = r'Creatures\Monster\JackalMan\ANM\NoSuchClip_negtest.anm'
NO_SUCH_ARCHIVE = r'NoSuchArchive_negtest\whatever.msh'


def _chain(name):
    return MA._load_arcs(name)


def _first_archive_only(ref):
    """Replay of the PRE-FIX algorithm, for plant N2."""
    arcname, inner = MA.split_ref(ref)
    chain = _chain(arcname)
    if not chain:
        return None
    _p, a, _idx = chain[0]
    for e in a.entries:
        if e.entry_type == 3 and e.name.lower().replace('/', '\\') == inner:
            return a.get_file(e.name)
    return None


def main():
    results = []
    chain = _chain('Creatures')
    print('Creatures.arc chain (resolution order):')
    for p, a, idx in chain:
        print('   %-92s %5d entries' % (p, len(idx)))
    if len(chain) < 2:
        print('\nSETUP ERROR: fewer than 2 Creatures.arc archives are reachable, so the '
              'shadowing behaviour this test exists to pin cannot be exercised. '
              'Build into the work/ layout with the game installed.')
        return 2

    mod_paths = {str(p) for p in MA.mod_resource_dirs()}

    def in_mod(arcpath):
        return any(str(arcpath).startswith(m) for m in mod_paths)

    # ---- P1: a base-game-only asset resolves, out of the BASE archive --------
    data, arcp = MA.read_asset(BASE_ONLY)
    ok = bool(data) and not in_mod(arcp)
    results.append(('P1 base-game asset resolves from the BASE archive', ok, True,
                    '%s bytes from %s' % (len(data) if data else 0, arcp)))

    # ---- P2: a mod-only asset resolves, out of the MOD archive ---------------
    mod_entry = None
    for p, a, idx in chain:
        if in_mod(p) and idx:
            mod_entry = (p, sorted(idx)[0])
            break
    if mod_entry is None:
        results.append(('P2 mod asset resolves from the MOD archive', False, True,
                        'no mod-side Creatures.arc entry to test with'))
    else:
        mp, inner = mod_entry
        ref = 'Creatures\\' + inner
        data2, arcp2 = MA.read_asset(ref)
        ok2 = bool(data2) and in_mod(arcp2)
        results.append(('P2 mod asset resolves from the MOD archive', ok2, True,
                        '%s -> %s' % (ref, arcp2)))

    # ---- N1: a genuinely absent asset must NOT resolve -----------------------
    results.append(('N1 absent asset does NOT resolve', MA.asset_exists(ABSENT), False,
                    ABSENT))

    # ---- N2: the OLD first-archive-only algorithm must FAIL on P1's asset ----
    old = _first_archive_only(BASE_ONLY)
    results.append(('N2 pre-fix first-archive-only algorithm finds it', bool(old), False,
                    'replay of the reverted resolver'))

    # ---- N3: unknown archive name resolves to nothing, no crash --------------
    d3, p3 = MA.read_asset(NO_SUCH_ARCHIVE)
    results.append(('N3 unknown archive name resolves', bool(d3) or p3 is not None, False,
                    NO_SUCH_ARCHIVE))

    print('\n%-58s %-8s %-8s %s' % ('CHECK', 'ACTUAL', 'WANT', 'DETAIL'))
    bad = 0
    for label, actual, want, detail in results:
        good = (bool(actual) == bool(want))
        bad += 0 if good else 1
        print('%-58s %-8s %-8s %s  %s'
              % (label, bool(actual), bool(want), 'ok' if good else '*** WRONG ***', detail))

    print()
    if bad:
        print('NEGTEST FAIL: %d check(s) wrong' % bad)
        return 1
    print('NEGTEST PASS: per-entry shadowing holds - base-game assets resolve, mod '
          'archives still win for their own entries, and a genuinely missing asset '
          'still fails (the pre-fix resolver is proven RED).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
