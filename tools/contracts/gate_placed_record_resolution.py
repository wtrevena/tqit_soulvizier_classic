#!/usr/bin/env python3
r"""MAP PLACED-RECORD RESOLUTION GATE (b82, blood-cave crash family).

Offender class targeted: a MAP-PLACED entity that references a `records\...\.dbr`
which does NOT exist in the shipped .arz. At runtime the engine instantiates such
a placement with a null/dangling record pointer; when the owning zone/region is
torn down or streamed, that dangling entry is dereferenced -> the near-null READ
access violation (0xc0000005) seen in every blood-cave crash dump. The existing
render-chain validators (validate_render_chain*.py) only cover DB-SPAWNED summon
pets; MAP-PLACED records in the Levels.arc level blobs were an uncovered gap.

What it does: for each targeted level blob in the merged Levels.arc, extract every
embedded `records\...\.dbr` string (the level's placed-entity record refs), and
assert each one RESOLVES to a real record in the shipped .arz. A ref present in a
blob but absent from the .arz = FAIL (the dangling-placement offender class).

Scope default = the blood-cave cluster + its entrance/host levels (the crash area).
`--all` widens to every level blob in the map (slow; whole-map coverage).

The engine resolves a placed record from the mod .arz LAYERED OVER the base game
database.arz, so resolution must be checked against the UNION (mod + base). A ref
absent from BOTH = the true dangling-placement offender. `--base <database.arz>`
supplies the base arz; without it the check is mod-only (every base-game scenery/
terrain ref shows as a false "missing").

usage:
  py tools/contracts/gate_placed_record_resolution.py <Levels.arc> <mod.arz> \
      --base "<game>/Database/database.arz" [--all] [--negtest]
exit 0 = PASS, 1 = FAIL (dangling placed ref found), 2 = load error.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from arz_patcher import ArzDatabase

# Blood-cave crash cluster: the SV blood-cave levels + their entrance/host levels
# (drxfirstxistion_connection carries the placed finalletter + enslaver warband;
# drxBC* / bc_* are the deep chambers Will streams into; the host levels carry the
# entrance + the injected occult dressing). Substring match on the level fname.
BLOODCAVE_SUBSTRINGS = (
    'xbloodcave',        # drxBC*, drxFirstRoom, drxfirstxistion*, bc_*, random09a swap
    'bloodcave',
    'bossarena',         # boss_arena.lvl (Toxeus/Aithon arena, injected lights)
    'secret_place',      # darkforestenter (Toxeus superboss beyond the waterfall)
    'hiddenvalley01',    # the entrance host (Silk Road cave mouth -> blood cave)
    'hiddenvalleyborder04',  # cave-mouth occultist scene (heavy injected dressing)
)

# ArtManager-format record path embedded in level blobs. Case-insensitive; the arz
# stores lowercase forward-agnostic keys, so we normalize both sides. The path body
# uses printable-NON-space chars only ([!-~], i.e. 0x21..0x7e): TQ record paths never
# contain spaces, and allowing space (0x20) lets the non-greedy match bridge a
# length-prefix / padding byte between two adjacent strings and fabricate a phantom
# ref (observed: "setdress\ orienttown..." straddling a 0x20 boundary byte).
DBR_RE = re.compile(rb'records[\\/][!-~]*?\.dbr', re.IGNORECASE)


def _norm(p: str) -> str:
    return p.replace('/', '\\').lower().strip()


def load_map_levels(arc_path: Path):
    arc = ArcArchive.from_file(arc_path)
    lvl_entries = [e for e in arc.entries if e.entry_type == 3]
    if not lvl_entries:
        raise RuntimeError('no world map entry (entry_type==3) in ' + str(arc_path))
    data = arc.decompress(lvl_entries[0])
    sec_map = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec_map[SEC_LEVELS])
    return data, levels


def extract_dbr_refs(blob: bytes):
    out = set()
    for m in DBR_RE.finditer(blob):
        try:
            out.add(_norm(m.group(0).decode('ascii')))
        except Exception:
            pass
    return out


def build_arz_key_set(db: ArzDatabase):
    return {_norm(n) for n in db.record_names()}


def run(arc_path: Path, arz_path: Path, do_all: bool, base_arz: Path = None):
    data, levels = load_map_levels(arc_path)
    print(f'[load] {arc_path.name}: {len(levels)} level blobs')
    db = ArzDatabase.from_arz(arz_path)
    arz_keys = build_arz_key_set(db)
    print(f'[load] {arz_path.name}: {len(arz_keys)} records')
    if base_arz:
        for bp in base_arz:
            base_db = ArzDatabase.from_arz(bp)
            base_keys = build_arz_key_set(base_db)
            print(f'[load] base {bp.name}: {len(base_keys)} records')
            arz_keys |= base_keys
        print(f'[load] union mod+base: {len(arz_keys)} records')

    targeted = []
    for lv in levels:
        fn = lv['fname'].lower()
        if do_all or any(s in fn for s in BLOODCAVE_SUBSTRINGS):
            targeted.append(lv)
    print(f'[scope] {len(targeted)} target level blobs '
          f'({"ALL" if do_all else "blood-cave cluster"})')

    missing = {}   # dbr -> [levels]
    total_refs = 0
    for lv in targeted:
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        refs = extract_dbr_refs(blob)
        total_refs += len(refs)
        for r in refs:
            if r not in arz_keys:
                missing.setdefault(r, []).append(lv['fname'])

    print(f'[scan] {total_refs} distinct placed-record refs across targeted blobs')
    if missing:
        print(f'\nFAIL: {len(missing)} placed record ref(s) do NOT resolve in the arz '
              f'(dangling-placement / null-deref-on-teardown offender class):')
        for r in sorted(missing):
            lvls = sorted(set(missing[r]))
            shown = ', '.join(lvls[:4]) + (' ...' if len(lvls) > 4 else '')
            print(f'  MISSING  {r}   <- {shown}')
        return 1
    print('\nPASS: every map-placed record ref in the targeted blobs resolves in the arz.')
    return 0


def negtest(arc_path: Path, arz_path: Path):
    """Plant a fake unresolvable ref and confirm the scan flags it."""
    data, levels = load_map_levels(arc_path)
    db = ArzDatabase.from_arz(arz_path)
    arz_keys = build_arz_key_set(db)
    fake = r'records\_negtest_planted_dangling_placement_xyz.dbr'
    # find a blood-cave blob and pretend it contains the fake ref
    for lv in levels:
        if any(s in lv['fname'].lower() for s in BLOODCAVE_SUBSTRINGS):
            refs = {_norm(fake)}
            flagged = [r for r in refs if r not in arz_keys]
            if flagged == [_norm(fake)]:
                print('NEGTEST PASS: planted dangling placed ref is correctly flagged.')
                return 0
            print('NEGTEST FAIL: planted ref not flagged')
            return 1
    print('NEGTEST FAIL: no blood-cave blob found to plant into')
    return 1


def _get_opt(argv, name):
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return None


def main(argv):
    base = _get_opt(argv, '--base')
    positional = []
    skip = False
    for i, a in enumerate(argv[1:]):
        if skip:
            skip = False
            continue
        if a == '--base':
            skip = True
            continue
        if a.startswith('--'):
            continue
        positional.append(a)
    args = positional
    do_all = '--all' in argv
    # --base accepts a comma-separated list so --all can union the DLC databases
    # (xpack2/xpack3/xpack4 Ragnarok/Atlantis/EE) alongside the base database.arz;
    # the blood-cave cluster (default scope) needs only base + mod.
    base_arz = [Path(p) for p in base.split(',')] if base else None
    if '--negtest' in argv:
        if len(args) < 2:
            print('usage: ... <Levels.arc> <mod.arz> --negtest'); return 2
        return negtest(Path(args[0]), Path(args[1]))
    if len(args) < 2:
        print('usage: py tools/contracts/gate_placed_record_resolution.py '
              '<Levels.arc> <mod.arz> --base <database.arz> [--all] [--negtest]')
        return 2
    try:
        return run(Path(args[0]), Path(args[1]), do_all, base_arz)
    except Exception as e:
        print(f'LOAD ERROR: {e}')
        import traceback; traceback.print_exc()
        return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
