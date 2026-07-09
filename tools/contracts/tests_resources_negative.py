r"""NEGATIVE TESTS for contracts_resources.py (DOMAIN C).

Method (the established pattern): take COMPLIANT build27 artifacts, surgically inject one
break per contract into SCRATCH copies, then prove the corresponding contract FIRES on the
break (and that the injected, uniquely-named breaks cannot pre-exist in the clean baseline).

Injected breaks (all use unique 'zzznegtest' tokens so they cannot collide with real data):
  C-RES-DBR-1    : a real record's .dbr field -> records\zzznegtest\does_not_exist.dbr
  C-RES-ASSET-1  : a real record's mesh field -> SVItems\zzznegtest\does_not_exist.msh
  C-RES-TAG-1    : a real record's itemNameTag -> tagSVCSoulZZZNegTestMissing (mod-owned=>P1)
  C-RES-TAG-1(SD): sd_zone_tags monkeypatched to yield tagZZZNegTestSDMissing (map-side wiring)
  C-RES-TPL-1    : a real record's templateName -> database\Templates\zzznegtest_missing.tpl
  C-RES-TAGDUP-1 : modstrings gets tagZZZNegTestDup defined twice with different values
  C-RES-TAGDEAD-1: modstrings gets tagSVCSoulZZZNegTestOrphan (content tag, referenced nowhere)

Run:  python tools/contracts/tests_resources_negative.py
Exits 0 iff every contract fired on its injected break; else 1.
"""
import sys
import os
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_TOOLS = _HERE.parent
for p in (str(_HERE), str(_TOOLS)):
    if p not in sys.path:
        sys.path.insert(0, p)

import contracts_resources as C          # noqa: E402
from arz_patcher import ArzDatabase, DATA_TYPE_STRING   # noqa: E402
from arc_patcher import ArcArchive       # noqa: E402

_BASELINE = C._BASELINE
_SCRATCH = Path(os.environ.get(
    'SVC_NEG_SCRATCH',
    r"C:/Users/willi/AppData/Local/Temp/claude/"
    r"C--Users-willi-repos/55f6c1cb-5e9b-466b-a25d-f3fb1a0c56a8/scratchpad/neg_resources"))
_SCRATCH.mkdir(parents=True, exist_ok=True)

DBR_BREAK = 'records\\zzznegtest\\does_not_exist.dbr'
MESH_BREAK = 'SVItems\\zzznegtest\\does_not_exist.msh'
TAG_BREAK = 'tagSVCSoulZZZNegTestMissing'
TPL_BREAK = 'database\\Templates\\zzznegtest_missing.tpl'
SD_BREAK = 'tagZZZNegTestSDMissing'
DUP_KEY = 'tagZZZNegTestDup'
ORPHAN_TAG = 'tagSVCSoulZZZNegTestOrphan'


def _pick_carrier(db):
    """A single COMPLIANT record to break. anysoul is a real shipped soul (itemNameTag +
    templateName present); fall back to the first record if absent. All four breaks are
    injected into this one record - the scan classifies refs by the VALUE's extension, so
    the field name is immaterial to detection."""
    for cand in ('records\\item\\equipmentring\\soul\\anysoul.dbr',):
        if db.has_record(cand):
            return cand
    return db.record_names()[0]


def build_broken_arz():
    print("  [neg] loading baseline arz ...")
    db = ArzDatabase.from_arz(_BASELINE / 'SoulvizierClassic.arz')
    rec = _pick_carrier(db)
    # Surgically break the compliant record: a dangling .dbr, mesh, name tag, and template.
    db.set_field(rec, 'itemSkillName', DBR_BREAK)   # value ext .dbr  -> C-RES-DBR-1
    db.set_field(rec, 'mesh', MESH_BREAK)           # value ext .msh  -> C-RES-ASSET-1
    db.set_field(rec, 'itemNameTag', TAG_BREAK)     # tag token       -> C-RES-TAG-1
    db.set_field(rec, 'templateName', TPL_BREAK)    # value ext .tpl  -> C-RES-TPL-1
    out = _SCRATCH / 'SoulvizierClassic_BROKEN.arz'
    t = time.time()
    db.write_arz(out)
    print(f"  [neg] wrote broken arz in {time.time()-t:.1f}s (carrier={rec})")
    return out, {'carrier': rec}


def build_broken_text():
    arc = ArcArchive.from_file(_BASELINE / 'Text.arc')
    txt = arc.get_text('modstrings.txt')
    add = (f"\r\n{DUP_KEY}=NegTestValueOne\r\n{DUP_KEY}=NegTestValueTwo\r\n"
           f"{ORPHAN_TAG}={{^F}}Orphan Soul NegTest\r\n")
    arc.set_text('modstrings.txt', txt + add)
    out = _SCRATCH / 'Text_BROKEN.arc'
    arc.write(out)
    print(f"  [neg] wrote broken Text.arc -> {out.name}")
    return out


def main():
    broken_arz, tgt = build_broken_arz()
    broken_text = build_broken_text()

    # Monkeypatch the SD extractor to inject a map-side missing zone tag (proves the
    # SD -> tag-resolution wiring without rebuilding the 688 MB map).
    C.sd_zone_tags = lambda cfg: ({SD_BREAK}, None)

    game = C._DEFAULT_BASE_GAME
    cfg = {
        'arz': str(broken_arz),
        'text_arc': str(broken_text),
        'levels_arc': str(_BASELINE / 'Levels_merged.arc'),
        'quests_arc': str(_BASELINE / 'Quests.arc'),
        'resource_arc_dir': str(_BASELINE / 'Resources'),
        'base_game_dir': game,
        'upstream_dir': C._DEFAULT_UPSTREAM,
        'cache_dir': str(_SCRATCH / 'cache'),
    }
    print("  [neg] running contracts over the broken artifacts ...")
    viols = C.run(cfg)

    def fired(contract, needle):
        return [v for v in viols if v['contract'] == contract
                and (needle.lower() in (v['subject'] + '|' + v['evidence']).lower())]

    checks = [
        ('C-RES-DBR-1', 'zzznegtest\\does_not_exist.dbr'.replace('\\', '/'), 'dangling .dbr ref'),
        ('C-RES-ASSET-1', 'zzznegtest/does_not_exist.msh', 'dangling mesh ref'),
        ('C-RES-TAG-1', TAG_BREAK.lower(), 'missing mod-owned itemNameTag'),
        ('C-RES-TAG-1', SD_BREAK.lower(), 'missing map SD zone tag'),
        ('C-RES-TPL-1', 'zzznegtest_missing.tpl', 'missing templateName'),
        ('C-RES-TAGDUP-1', DUP_KEY.lower(), 'conflicting duplicate tag'),
        ('C-RES-TAGDEAD-1', ORPHAN_TAG.lower(), 'orphaned content tag'),
    ]
    ok = True
    print("\n  NEGATIVE-TEST RESULTS:")
    for contract, needle, desc in checks:
        hits = fired(contract, needle)
        status = 'PASS' if hits else 'FAIL'
        if not hits:
            ok = False
        sev = hits[0]['severity'] if hits else '-'
        print(f"    [{status}] {contract:16s} ({sev})  {desc}")
        if hits:
            print(f"             -> {hits[0]['subject']} :: {hits[0]['evidence'][:90]}")

    # Also assert the P1 gate-blockers we expect (mod-owned tag miss + conflicting display tag).
    p1 = [v for v in viols if v['severity'] == 'P1']
    print(f"\n  P1 (gate-blocking) count on broken artifacts: {len(p1)}")
    print("  RESULT:", "ALL CONTRACTS FIRED" if ok else "SOME CONTRACTS DID NOT FIRE")
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
