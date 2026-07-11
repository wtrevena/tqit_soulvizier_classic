r"""Probe the real equip-slot gear on the Blood-Toxeus source chain + built pets,
to ground the P3-2 comment rewrite in verified fact.

usage: py tools/debug/bt_gear_probe.py <arz> [record ...]
default records: um_toxeus_99, um_bloodtoxeus_99, bloodtoxeus_1/2/3
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase  # noqa: E402

SLOTS = ['RightHand', 'LeftHand', 'Head', 'Torso', 'Forearm', 'LowerBody', 'ArmBand']
DEFAULT = [
    r'records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr',
    r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr',
    r'records\skills\soulskills\pets\bloodtoxeus_1.dbr',
    r'records\skills\soulskills\pets\bloodtoxeus_2.dbr',
    r'records\skills\soulskills\pets\bloodtoxeus_3.dbr',
]


def main(arz, recs):
    db = ArzDatabase.from_arz(Path(arz))
    names = {n.replace('/', '\\').lower(): n for n in db.record_names()}
    for r in recs:
        real = names.get(r.replace('/', '\\').lower())
        print("=" * 70)
        print(r, '->', 'FOUND' if real else 'ABSENT')
        if not real:
            continue
        for slot in SLOTS:
            ch = db.get_field_value(real, 'chanceToEquip%s' % slot)
            it = db.get_field_value(real, 'loot%sItem1' % slot)
            if ch or it:
                print(f"  {slot:10s} chance={ch} item1={it}")


if __name__ == '__main__':
    arz = sys.argv[1]
    recs = sys.argv[2:] or DEFAULT
    main(arz, recs)
