#!/usr/bin/env python3
"""B100 WEAPON/HAND GATE TEXT GATE - the Text.arc half of process law #4.

The DB half lives in `tools/patches/weapon_gate_truth.py` verify(): it asserts
the CONTRACTed skill records still carry the exact gating fields their shipped
tooltip was written against. That half cannot see Text.arc (the .arz and
Text.arc are built by two different tools), so it cannot notice a tooltip that
was edited to drop the clause.

This module closes the other direction. It reads the BUILT `.arz` and the BUILT
`Text.arc` back off disk and asserts, for every contracted record:

  * its `skillBaseDescription` still points at the tag the contract names, and
  * that tag RESOLVES in Text.arc (mod tags in modstrings.txt first, then the
    base-game Text_EN.arc the engine loads underneath it), and
  * the rendered string CONTAINS every clause the record's gating fields demand
    ("Allows and requires dual wielding." for dualWieldOnly=1; the weapon-class
    sentence when a qualifying-weapon list is present).

So: change the record without the text -> the DB half reds. Change the text
without the record -> this half reds. Change both consistently -> green.

Usage:
    py tools/validate_weapon_gate_text.py <built.arz> <built Text.arc> [<base Text_EN.arc>]

Exit 0 = PASS. Exit 1 = FAIL (fail-loud; the build does not ship).
Negative tests: tools/debug/negtest_weapon_gate_truth.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'patches'))

from arz_patcher import ArzDatabase          # noqa: E402
from arc_patcher import ArcArchive           # noqa: E402
import weapon_gate_truth as WGT              # noqa: E402

DEFAULT_BASE_TEXT = (r"C:\Program Files (x86)\Steam\steamapps\common"
                     r"\Titan Quest Anniversary Edition\Text\Text_EN.arc")


def load_tags(arc_path):
    """tag -> value for every key=value line in every file of an .arc."""
    tags = {}
    arc = ArcArchive.from_file(Path(arc_path))
    names = (sorted(arc.entries.keys()) if isinstance(arc.entries, dict)
             else [e.name for e in arc.entries])
    for name in names:
        data = arc.get_file(name)
        if not data:
            continue
        try:
            text = (data.decode('utf-16') if data[:2] in (b'\xff\xfe', b'\xfe\xff')
                    else data.decode('utf-8-sig', errors='replace'))
        except Exception:
            continue
        for line in text.splitlines():
            if '=' not in line or line.lstrip().startswith('//'):
                continue
            key, _, value = line.partition('=')
            # The engine keeps the FIRST definition of a duplicated tag.
            tags.setdefault(key.strip(), value)
    return tags


def required_clauses_for(gate):
    """Clauses the SHIPPED text must contain, derived from the LIVE gating
    fields (never from the contract) - so a record that grew a gate is caught."""
    weapons, dual_wield_only, _melee_only = gate
    need = []
    if dual_wield_only:
        need.append(WGT.CLAUSE_DUAL_WIELD)
    if weapons:
        need.append(WGT.CLAUSE_SWORD_OR_AXE if weapons == frozenset({'Sword', 'Axe'})
                    else '<no clause authored for weapon set %s>' % sorted(weapons))
    return need


def validate(arz_path, text_path, base_text_path=None):
    print("=" * 72)
    print("B100 WEAPON/HAND GATE TEXT GATE")
    print(f"  arz  : {arz_path}")
    print(f"  text : {text_path}")
    db = ArzDatabase.from_arz(Path(arz_path))
    tags = load_tags(text_path)
    base_tags = {}
    bp = base_text_path or DEFAULT_BASE_TEXT
    if bp and Path(bp).exists():
        base_tags = load_tags(bp)
        print(f"  base : {bp} ({len(base_tags)} tags, loaded underneath)")
    else:
        print(f"  base : (none - base-game Text_EN.arc not found at {bp!r}; "
              f"only mod tags can resolve)")

    failures = []
    for rec, spec in sorted(WGT.CONTRACT.items()):
        if not db.has_record(rec):
            failures.append(f"{spec['label']}: record MISSING from the arz ({rec})")
            continue
        tag = WGT._get_field(db, rec, 'skillBaseDescription')
        if tag != spec['tag']:
            failures.append(
                f"{spec['label']}: skillBaseDescription is {tag!r}, contract "
                f"requires {spec['tag']!r} ({rec})")
            continue
        text = tags.get(tag, base_tags.get(tag))
        if text is None:
            failures.append(
                f"{spec['label']}: tag {tag!r} does NOT resolve in the built "
                f"Text.arc or the base-game text - the tooltip would render as "
                f"raw tag text in game ({rec})")
            continue
        gate = WGT.gate_of(db, rec)
        need = required_clauses_for(gate)
        missing = [c for c in need if c not in text]
        print(f"  {spec['label']}: {tag} -> {text!r}")
        print(f"      live gate: weapons={sorted(gate[0])} dualWieldOnly={gate[1]} "
              f"meleeOnly={gate[2]}; clauses required: {need}")
        for c in missing:
            failures.append(
                f"{spec['label']}: the shipped tooltip does NOT state its own "
                f"gate - missing clause {c!r}. Live gate is weapons="
                f"{sorted(gate[0])} dualWieldOnly={gate[1]}. Either restore the "
                f"clause in tools/build_text_arc.py TEXT_FIX_TAGS, or - if the "
                f"MECHANICS deliberately changed - update the record, the "
                f"CONTRACT in tools/patches/weapon_gate_truth.py and this text "
                f"together ({rec})")

    if failures:
        for f in failures:
            print(f"  GATE FAILURE: {f}")
        print(f"RESULT: FAIL - {len(failures)} weapon/hand-gate honesty "
              f"violation(s). A skill whose bonuses are silently dead unless "
              f"the player dual wields MUST say so on its own tooltip "
              f"(docs/WILL_RULINGS.md R-100).")
        return 1
    print(f"RESULT: PASS - {len(WGT.CONTRACT)} contracted tooltip(s) state the "
          f"gate their records actually enforce")
    return 0


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    base = argv[3] if len(argv) > 3 else None
    return validate(argv[1], argv[2], base)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
