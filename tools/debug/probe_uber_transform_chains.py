r"""probe_uber_transform_chains.py - R-106 amendment CHECK: are the two "0% is a
defect" ubers really defective, or are they the HEAD of a death-transform chain
whose terminal already drops? (R-107 already retracted the third, the Gaoler.)

Usage: py tools/debug/probe_uber_transform_chains.py <built.arz>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase

SEP = chr(92)
RECS = [
    r'records\xpack\creatures\monster\bosses\02_charon\um_charon_ferryman_99.dbr',
    r'records\xpack\creatures\monster\bosses\02_charon\um_charonform2_ferryman_99.dbr',
    r'records\xpack\creatures\monster\lostsoul\um_tantalus_99.dbr',
    r'records\xpack\creatures\monster\lostsoul\um_tantalus_unbound_99.dbr',
    r'records\xpack\creatures\monster\gigantes\um_polisgaoler_99.dbr',
    r'records\xpack\creatures\monster\gigantes\um_polisgaoler_unbound_99.dbr',
]


def one(v):
    return v[0] if isinstance(v, list) and v else v


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    for r in RECS:
        if not db.has_record(r):
            print("(absent) %s" % r)
            continue
        soul = one(db.get_field_value(r, 'lootFinger2Item1')) or ''
        nxt = one(db.get_field_value(r, 'actorToSpawnOnDeath')) or ''
        print("%-32s chance=%-7s onDeath-> %-32s soul=%s"
              % (r.rsplit(SEP, 1)[-1].replace('.dbr', ''),
                 one(db.get_field_value(r, 'chanceToEquipFinger2')),
                 str(nxt).rsplit(SEP, 1)[-1].replace('.dbr', '') or '(terminal)',
                 str(soul).rsplit(SEP, 1)[-1].replace('.dbr', '')))


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
