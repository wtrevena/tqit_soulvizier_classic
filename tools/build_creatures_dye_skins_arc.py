r"""Build the mod's Creatures.arc holding the Soulvizier costume-dye PC skins.

WHY THIS EXISTS (PR-2, 2026-08-06)
----------------------------------
The Garden-of-Merchants "special / costume dyes" (OneShot_Dye records) reskin the
player character to custom `Creatures\PC\{Male,Female}\...tex` textures. Those skin
textures live ONLY in Soulvizier 0.98i's own `Creatures.arc` (amgoz1's AllSkins
pack). The mod's bootstrap COPIED that arc and then STRIPPED it (Step 2b, "cosmetic,
game falls back to base skins") - but the AllSkins paths do NOT exist in the base
game, so the engine painted the PC flat GREY. That is the Flozer44 "dyes turn me
grey" report (PR-2).

This tool rebuilds a Creatures.arc for the mod that contains EXACTLY the SV skin
entries that are NOT already in the base game (purely ADDITIVE - it overrides ZERO
base asset). Shipping it makes every obtainable costume dye resolve.

It is SOURCE-ONLY: it reads SV 0.98i's Creatures.arc (resolved from the build-input
cache / third_party zip) and the base-game Creatures.arc, and writes the filtered
arc. Deterministic. See docs/BACKLOG.md PR-2 and tools/gate_dye_skins.py.
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive


def _norm(name: str) -> str:
    return name.replace('\\', '/').lower()


def build(sv_creatures: Path, base_creatures: Path, out: Path):
    sv = ArcArchive.from_file(sv_creatures)
    base = ArcArchive.from_file(base_creatures)
    base_names = set(_norm(e.name) for e in base.entries
                     if e.entry_type == 3 and e.name)

    kept, dropped_overlap = [], []
    for e in sv.entries:
        if e.entry_type != 3 or not e.name:
            continue
        if _norm(e.name) in base_names:
            dropped_overlap.append(e.name)   # exists in base -> do NOT override
        else:
            kept.append(e)                    # net-new skin -> ship it

    # Rebuild a fresh archive holding only the kept (net-new) entries, so the output
    # is provably additive and carries no dead string-table names.
    out_arc = ArcArchive()
    out_arc.version = sv.version
    for e in kept:
        data = sv.get_file(e.name)
        if data is None:
            raise SystemExit(f"could not decompress {e.name} from {sv_creatures}")
        out_arc.add_file(e.name, data)

    out.parent.mkdir(parents=True, exist_ok=True)
    out_arc.write(out)

    print(f"source SV Creatures.arc : {sv_creatures}  ({len(sv.entries)} entries)")
    print(f"base Creatures.arc      : {base_creatures} ({len(base_names)} entries)")
    print(f"kept (net-new, shipped) : {len(kept)}")
    print(f"dropped (overlap w/base): {len(dropped_overlap)} -> {dropped_overlap}")
    print(f"wrote                   : {out}  ({out.stat().st_size} bytes)")
    return kept, dropped_overlap


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sv-creatures', help='SV 0.98i Creatures.arc (source of the skins)')
    ap.add_argument('--base-creatures', help='base-game Creatures.arc')
    ap.add_argument('--out', required=True, help='output Creatures.arc path')
    a = ap.parse_args()

    sv = a.sv_creatures
    base = a.base_creatures
    if not sv or not base:
        # resolve via the shared build-input preflight when not given explicitly
        import check_build_inputs as cbi
        if not sv:
            try:
                sv = cbi.resolve('sv098i_creatures_arc')
            except cbi.MissingInput:
                # only present as a third_party archive -> unpack it into the cache
                cbi.extract_from_third_party(['sv098i_creatures_arc'])
                sv = cbi.resolve('sv098i_creatures_arc')
        if not base:
            base = cbi.resolve('base_creatures_arc')
    build(Path(sv), Path(base), Path(a.out))


if __name__ == '__main__':
    main()
