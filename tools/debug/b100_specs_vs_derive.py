#!/usr/bin/env python3
"""Gate-adjacent consistency check: SANCTUARY_SPECS == the derivation's own output.

The specs table in build_section_surgery.py is hand-transcribed from
b100_derive_sanctuary.py's output, and a transcription typo is silent (the gate would
re-prove every geometric invariant about whatever WAS transcribed). This asserts the two
agree element for element, ORDER INCLUDED, against a placements.json.

  py tools/debug/b100_specs_vs_derive.py local/b100_r3/placements.json
"""
import sys
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))
import build_section_surgery as BSS   # noqa: E402


def base(p):
    return p.replace('/', '\\').split('\\')[-1].lower()


def main(argv):
    jpath = argv[1] if len(argv) > 1 else str(REPO / 'local' / 'b100_r3' / 'placements.json')
    specs = [(base(s[0].decode('latin-1')), round(float(s[1]), 3),
              round(float(s[2]), 3), round(float(s[3]), 3))
             for s in BSS.INJECT_SPECS[BSS.SANCTUARY_HOST_KEY]]
    der = json.load(open(jpath))
    dj = [(base(d['dbr']), round(d['local'][0], 3), round(d['local'][1], 3),
           round(d['local'][2], 3)) for d in der]
    print(f'SANCTUARY_SPECS  n={len(specs)}')
    print(f'derivation json  n={len(dj)}  ({jpath})')
    bad = 0
    for i in range(max(len(specs), len(dj))):
        a = specs[i] if i < len(specs) else None
        b = dj[i] if i < len(dj) else None
        if a != b:
            bad += 1
            print(f'  MISMATCH idx {i}: specs={a}  derived={b}')
    print(f'\nRESULT: {"PASS - identical, order included" if not bad else f"FAIL - {bad} mismatch(es)"}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
