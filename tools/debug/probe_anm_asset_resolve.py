r"""PROBE (read-only): do the thrown-stance `.anm` clips actually EXIST as assets?

The animation-table fix is worthless if the clips it binds are not shipped. This
resolves every `.anm` path that `tools/patches/thrown_anim_rig.py` binds against
BOTH the base-game `Resources\*.arc` set AND the mod's own `Resources\*.arc`
(the mod overlays; either hit resolves in-game), and reports MISSING loudly.

An `.anm` path's FIRST path component is the archive name, exactly like the soul
icon rule in CLAUDE.md (`Creatures\Monster\...` -> `Creatures.arc`;
`XPack\Creatures\...` -> `xpack\Creatures.arc`).

Usage:
  py tools/debug/probe_anm_asset_resolve.py <game_dir> [<mod_resources_dir>]
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # tools/
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "patches"))
from arc_patcher import ArcArchive  # noqa: E402
import thrown_anim_rig  # noqa: E402


def norm(s):
    return str(s).replace("/", "\\").lower()


def index_dir(root):
    """{lowercased inner-path -> arc file} over every .arc under `root`."""
    idx = {}
    if not root or not Path(root).is_dir():
        return idx
    for arc in sorted(Path(root).rglob("*.arc")):
        try:
            a = ArcArchive.from_file(arc)
        except Exception as exc:                      # pragma: no cover
            print("  [skip] %s (%s)" % (arc, exc))
            continue
        for entry in a.entries:          # ArcEntry objects, not name strings
            if getattr(entry, "name", ""):
                idx.setdefault(norm(entry.name), arc)
    return idx


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    game = Path(sys.argv[1])
    mod_res = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    print("indexing base-game arcs under %s ..." % (game / "Resources"))
    base_idx = index_dir(game / "Resources")
    print("  %d entries" % len(base_idx))
    mod_idx = {}
    if mod_res:
        print("indexing mod arcs under %s ..." % mod_res)
        mod_idx = index_dir(mod_res)
        print("  %d entries" % len(mod_idx))

    wanted = thrown_anim_rig.referenced_anms()
    print("\nthrown-stance .anm clips to resolve: %d" % len(wanted))
    missing = []
    for a in sorted(wanted):
        # an .anm path in a DBR is arc-inner-relative WITHOUT the leading
        # archive-name component; try both spellings.
        cands = [norm(a)]
        parts = norm(a).split("\\")
        if len(parts) > 1:
            cands.append("\\".join(parts[1:]))
            if len(parts) > 2:
                cands.append("\\".join(parts[2:]))
        hit = None
        for c in cands:
            if c in mod_idx:
                hit = ("MOD", mod_idx[c].name, c)
                break
            if c in base_idx:
                hit = ("BASE", base_idx[c].name, c)
                break
        if hit:
            # print the EXACT inner path that matched, so an archive-name
            # stripping artifact can never masquerade as a resolution.
            print("  OK   [%-4s %-16s] %-62s  <- inner %s"
                  % (hit[0], hit[1], a, hit[2]))
        else:
            missing.append(a)
            print("  MISS %s" % a)

    print("\nRESULT: %d/%d resolve, %d MISSING"
          % (len(wanted) - len(missing), len(wanted), len(missing)))
    raise SystemExit(1 if missing else 0)


if __name__ == "__main__":
    main()
