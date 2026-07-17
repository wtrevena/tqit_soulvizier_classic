#!/usr/bin/env python3
r"""MAP PLACED-RECORD RESOLUTION GATE (b82, blood-cave crash family).

CRASH-CLASS INVARIANT (the HARD gate): a MAP-PLACED entity must reference a
`records\...\.dbr` that EXISTS in the shipped .arz (mod layered over base). If a
placed record does NOT exist, the engine instantiates that placement with a
null/dangling record pointer; when the owning zone/region is streamed out, that
null entry is dereferenced -> the near-null READ access violation (0xc0000005)
seen in every blood-cave crash dump. This is the "placed-record NON-EXISTENCE"
offender class. The existing render-chain validators (validate_render_chain*.py)
only cover DB-SPAWNED summon pets; MAP-PLACED records in the Levels.arc level
blobs were an uncovered gap. contracts_map.py MAP-REF-1 covers the SV-scoped
0x05 placements map-wide; THIS gate adds a blood-cave-focused WHOLE-BLOB scan
(every embedded record ref, not just 0x05 instances) plus a transitive chain
walk (below).

SCOPE OF THE HARD GATE (precise): the gate rules out ONLY the placed-record
NON-EXISTENCE class - a placed ref whose target record is absent from the arz
union. It deliberately does NOT hard-fail on dangling ASSET refs (mesh / tex /
pfx / anim / sound) or dangling CHILD records (skills / effects / loot tables)
reached transitively: the engine LOGS-AND-CONTINUES on those (the crash dump's
own game-log tail shows exactly this - "Unable to create skill (shieldcharge)",
"AnimationSelected: Invalid reference" - all benign). Treating those as gate
failures would false-positive on tolerated base/DRX-upstream and SV cosmetic
debt (e.g. records\drxmap\bloodcave\dng_hadescrypt01.dbr resolves as a record
yet 4 of its 50 feature meshes are stored flat in drx.arc without the \Entrance\
subpath - invisible boss-entrance decoration, not a crash). So the gate's HARD
claim is exactly "no NON-EXISTENT placed record"; nothing broader.

CHAIN-WALK COVERAGE (diagnostic, non-failing): after the hard depth-0 check, the
gate transitively walks each resolved placed record's `.dbr` sub-references and
enumerates every dangling child record and asset ref it reaches, CLASSIFIED
(skills / effects / loot / disabled xxx--/-- prefix / other; asset refs by ext).
This DEMONSTRATES the chain resolves as far as the engine tolerates and prints
exactly which dangles are the engine-log-and-continue class. It is informational
(it never changes the exit code) precisely because the forensics + the dump log
prove those dangles are benign; the crash is the map-structural Engine.dll
navmesh-load condition (docs/reports/b82_bloodcave_crash_rca.md), not a dangling
asset. Pass --no-chain to skip the walk (faster).

RESOLUTION MODEL: the engine resolves a placed record from the mod .arz LAYERED
OVER the base game database.arz, so resolution is the UNION (mod + base). A ref
absent from BOTH = the true dangling-placement offender. `--base <database.arz>`
supplies the base arz; without it the check is mod-only (every base-game scenery
ref shows as a false "missing"). `--base` accepts a comma-separated list so
`--all` (whole map) can union the Ragnarok/Atlantis/EE DLC databases; the blood-
cave cluster (default scope) needs only base + mod.

usage:
  py tools/contracts/gate_placed_record_resolution.py <Levels.arc> <mod.arz> \
      --base "<game>/Database/database.arz" [--all] [--no-chain] [--negtest]
exit 0 = PASS, 1 = FAIL (NON-EXISTENT placed ref found), 2 = load error.
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

# transitive chain-walk asset extensions (engine LOGS-AND-CONTINUES on any missing
# one; enumerated for coverage, never a gate failure).
ASSET_EXTS = ('.msh', '.tex', '.tga', '.anm', '.pfx', '.wav', '.mp3', '.ssh', '.a2t')

# SV/restored namespace markers (our authored content vs base/DLC upstream).
SV_MARKERS = ('all_sv\\', 'drxmap\\', '\\sv\\', 'records\\sv', 'svitems\\')


def _norm(p: str) -> str:
    return p.replace('/', '\\').lower().strip()


def _disabled(npath: str) -> bool:
    """Intentionally-disabled ref (author convention): xxx / -- prefix on the base
    name or a path segment. The engine never instantiates these."""
    base = npath.split('\\')[-1]
    return (base.startswith('xxx') or base.startswith('--')
            or npath.startswith('xxx') or '\\xxx' in npath or '\\--' in npath)


def _is_sv(npath: str) -> bool:
    return any(m in npath for m in SV_MARKERS)


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


def _targeted_levels(levels, do_all):
    out = []
    for lv in levels:
        fn = lv['fname'].lower()
        if do_all or any(s in fn for s in BLOODCAVE_SUBSTRINGS):
            out.append(lv)
    return out


def scan_placed(data, targeted):
    """Return (per_blob_sum, global_refs, missing_by_ref) for the hard depth-0
    placed-record check. missing_by_ref is filled by the caller against arz_keys."""
    per_blob_sum = 0
    global_refs = {}    # ref -> [levels that embed it]
    for lv in targeted:
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        refs = extract_dbr_refs(blob)
        per_blob_sum += len(refs)
        for r in refs:
            global_refs.setdefault(r, []).append(lv['fname'])
    return per_blob_sum, global_refs


def _record_child_refs(dbs, name):
    """Every .dbr and asset reference inside one record's field VALUES, across the
    arz union (first db that has the record wins)."""
    fields = None
    for db in dbs:
        fields = db.get_fields(name)
        if fields is not None:
            break
    if not fields:
        return set(), set()
    dbrs, assets = set(), set()
    for _k, tf in fields.items():
        vals = getattr(tf, 'values', None)
        if vals is None:
            v0 = getattr(tf, 'value', None)
            vals = v0 if isinstance(v0, list) else [v0]
        for v in vals:
            if not isinstance(v, str):
                continue
            for tok in v.split(';'):
                t = tok.strip()
                if not t:
                    continue
                low = t.lower()
                if low.endswith('.dbr'):
                    dbrs.add(_norm(t))
                elif low.endswith(ASSET_EXTS):
                    assets.add(_norm(t))
    return dbrs, assets


def walk_chain(dbs, arz_keys, seed_refs):
    """Transitive .dbr walk from every resolvable seed placed record. Returns a
    dict of coverage stats + the classified dangling child records. NON-FAILING."""
    seen = set()
    frontier = [r for r in seed_refs if r in arz_keys]
    missing_children = set()
    asset_refs = set()
    nodes = 0
    while frontier:
        nxt = []
        for rec in frontier:
            if rec in seen:
                continue
            seen.add(rec)
            nodes += 1
            dbrs, assets = _record_child_refs(dbs, rec)
            asset_refs |= assets
            for d in dbrs:
                if d in arz_keys:
                    if d not in seen:
                        nxt.append(d)
                else:
                    missing_children.add(d)
        frontier = nxt
    # classify the dangling children (all engine-tolerated log-and-continue)
    buckets = {'skills': [], 'effects': [], 'loot': [], 'disabled': [],
               'sv_other': [], 'base_other': []}
    for m in sorted(missing_children):
        if _disabled(m):
            buckets['disabled'].append(m)
        elif 'records\\skills\\' in m:
            buckets['skills'].append(m)
        elif 'records\\effects\\' in m:
            buckets['effects'].append(m)
        elif 'loot' in m:
            buckets['loot'].append(m)
        elif _is_sv(m):
            buckets['sv_other'].append(m)
        else:
            buckets['base_other'].append(m)
    return {'nodes': nodes, 'missing_children': missing_children,
            'asset_refs': asset_refs, 'buckets': buckets}


def run(arc_path: Path, arz_path: Path, do_all: bool, base_arz=None, do_chain=True):
    data, levels = load_map_levels(arc_path)
    print(f'[load] {arc_path.name}: {len(levels)} level blobs')
    db = ArzDatabase.from_arz(arz_path)
    dbs = [db]
    arz_keys = build_arz_key_set(db)
    print(f'[load] {arz_path.name}: {len(arz_keys)} records')
    if base_arz:
        for bp in base_arz:
            base_db = ArzDatabase.from_arz(bp)
            dbs.append(base_db)
            base_keys = build_arz_key_set(base_db)
            print(f'[load] base {bp.name}: {len(base_keys)} records')
            arz_keys |= base_keys
        print(f'[load] union mod+base: {len(arz_keys)} records')

    targeted = _targeted_levels(levels, do_all)
    print(f'[scope] {len(targeted)} target level blobs '
          f'({"ALL" if do_all else "blood-cave cluster"})')

    per_blob_sum, global_refs = scan_placed(data, targeted)
    print(f'[scan] {len(global_refs)} globally-distinct placed-record refs '
          f'({per_blob_sum} counting per-blob duplicates) across targeted blobs')

    missing = {r: lvls for r, lvls in global_refs.items() if r not in arz_keys}
    rc = 0
    if missing:
        print(f'\nFAIL: {len(missing)} placed record ref(s) do NOT EXIST in the arz '
              f'union (NON-EXISTENCE / null-deref-on-teardown crash class):')
        for r in sorted(missing):
            lvls = sorted(set(missing[r]))
            shown = ', '.join(lvls[:4]) + (' ...' if len(lvls) > 4 else '')
            print(f'  MISSING  {r}   <- {shown}')
        rc = 1
    else:
        print('\nPASS: every map-placed record ref in the targeted blobs EXISTS in '
              'the arz union (placed-record NON-EXISTENCE crash class ruled out).')

    # ---- transitive chain-walk coverage (diagnostic; never changes rc) ----
    if do_chain:
        seeds = [r for r in global_refs if r in arz_keys]
        cov = walk_chain(dbs, arz_keys, seeds)
        b = cov['buckets']
        print(f'\n[chain] walked {cov["nodes"]} records transitively from '
              f'{len(seeds)} placed seeds; {len(cov["asset_refs"])} distinct asset '
              f'refs (mesh/tex/pfx/anim/sound) reached.')
        print(f'[chain] {len(cov["missing_children"])} dangling CHILD .dbr refs, ALL '
              f'engine-tolerated (log-and-continue; see the crash dump log tail):')
        print(f'          skills={len(b["skills"])}  effects={len(b["effects"])}  '
              f'loot={len(b["loot"])}  disabled={len(b["disabled"])}  '
              f'sv_other={len(b["sv_other"])}  base_other={len(b["base_other"])}')
        if b['sv_other']:
            print('        SV-namespace dangles (cosmetic/FX upstream debt, not the crash):')
            for m in b['sv_other'][:20]:
                print(f'          - {m}')
        print('[chain] NOTE: dangling child/asset refs are NOT gate failures - the '
              'engine skips them and continues (forensics: crash is Engine.dll '
              'navmesh-load, not a dangling asset).')
    return rc


def _plant_ref_into_blob(data, levels, fake_ref: bytes):
    r"""Splice a fake `records\...\.dbr` byte string into a real blood-cave level
    blob's region of the in-memory map buffer (over throwaway bytes at the blob
    tail). Returns (mutated_data, fname) so the negtest exercises the REAL
    DBR_RE + scan loop end-to-end, not an in-memory tautology."""
    buf = bytearray(data)
    for lv in levels:
        if any(s in lv['fname'].lower() for s in BLOODCAVE_SUBSTRINGS):
            off = lv['data_offset']
            length = lv['data_length']
            if length < len(fake_ref) + 8:
                continue
            # overwrite a slice near the blob end; bracket with NULs so the regex
            # sees a clean standalone string (mirrors how real refs sit in a blob).
            pos = off + length - len(fake_ref) - 4
            buf[pos - 1] = 0
            buf[pos:pos + len(fake_ref)] = fake_ref
            buf[pos + len(fake_ref)] = 0
            return bytes(buf), lv['fname']
    return None, None


def negtest(arc_path: Path, arz_path: Path, base_arz=None):
    """END-TO-END negative test: plant a guaranteed-non-existent placed ref into a
    REAL blood-cave blob's bytes, then run the ACTUAL scan (DBR_RE extraction +
    resolution loop) and assert it flags exactly that ref. This exercises the real
    extractor and scan, not a `fake not in keys` tautology."""
    data, levels = load_map_levels(arc_path)
    db = ArzDatabase.from_arz(arz_path)
    arz_keys = build_arz_key_set(db)
    if base_arz:
        for bp in base_arz:
            arz_keys |= build_arz_key_set(ArzDatabase.from_arz(bp))
    fake = rb'records\_negtest_planted_dangling_placement_xyz.dbr'
    fake_norm = _norm(fake.decode('ascii'))

    # 1. sanity: the planted ref must genuinely not exist (else the test is void)
    if fake_norm in arz_keys:
        print('NEGTEST FAIL: the planted ref unexpectedly EXISTS in the arz union')
        return 1
    # 2. sanity: a clean scan of the unmutated map must NOT already contain it
    targeted = _targeted_levels(levels, False)
    _sum, clean_refs = scan_placed(data, targeted)
    if fake_norm in clean_refs:
        print('NEGTEST FAIL: planted ref already present before planting (void test)')
        return 1
    # 3. plant into a real blob and re-run the REAL scan
    mutated, fname = _plant_ref_into_blob(data, levels, fake)
    if mutated is None:
        print('NEGTEST FAIL: no blood-cave blob large enough to plant into')
        return 1
    _sum2, refs2 = scan_placed(mutated, targeted)
    if fake_norm not in refs2:
        print('NEGTEST FAIL: DBR_RE/scan did not extract the planted ref from the blob')
        return 1
    missing = {r for r in refs2 if r not in arz_keys}
    if fake_norm not in missing:
        print('NEGTEST FAIL: planted ref extracted but not flagged as non-existent')
        return 1
    print(f'NEGTEST PASS: planted dangling placed ref end-to-end extracted from '
          f'{fname} and flagged as NON-EXISTENT (rc would be 1).')
    return 0


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
    for a in argv[1:]:
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
    do_chain = '--no-chain' not in argv
    base_arz = [Path(p) for p in base.split(',')] if base else None
    if '--negtest' in argv:
        if len(args) < 2:
            print('usage: ... <Levels.arc> <mod.arz> --base <db.arz> --negtest'); return 2
        return negtest(Path(args[0]), Path(args[1]), base_arz)
    if len(args) < 2:
        print('usage: py tools/contracts/gate_placed_record_resolution.py '
              '<Levels.arc> <mod.arz> --base <database.arz> [--all] [--no-chain] [--negtest]')
        return 2
    try:
        return run(Path(args[0]), Path(args[1]), do_all, base_arz, do_chain)
    except Exception as e:
        print(f'LOAD ERROR: {e}')
        import traceback; traceback.print_exc()
        return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
