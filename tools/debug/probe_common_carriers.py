"""probe_common_carriers.py - R-106 safety check: WHICH of the 15 Common soul
carriers are actually DROPPERS, and which are PETS or skill records?

R-106 rules Common carriers to 0%. But `chanceToEquipFinger2` does double duty
(R-104): on a MONSTER it is the drop rate; on a PET it is a pure power switch and
the pet never drops anything. Zeroing a pet's slot would nerf Will's own summons
for no drop-side benefit - the toxeus_passiveproperties / genericbossorb_04
shared-carrier lesson in a new costume. This probe enumerates every non-zero
carrier outside the `\\creature(s)\\` monster roster with its template + Class so
the call is made on evidence.

Usage: py tools/debug/probe_common_carriers.py <built.arz>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    rows = []
    for rec in db.record_names():
        ff = db.get_fields(rec)
        if not ff:
            continue
        has_soul = False
        cur = 0.0
        cls = ''
        for k, tf in ff.items():
            fn = k.split('###')[0]
            if fn == 'lootFinger2Item1' and tf.values:
                for v in tf.values:
                    if isinstance(v, str) and 'soul' in v.lower():
                        has_soul = True
                        break
            elif fn == 'chanceToEquipFinger2' and tf.values:
                try:
                    cur = float(tf.values[0])
                except (TypeError, ValueError):
                    cur = 0.0
            elif fn == 'monsterClassification' and tf.values:
                cls = str(tf.values[0] or '')
        if has_soul and cur > 0:
            rows.append((rec, cls, cur,
                         str(db.get_field_value(rec, 'templateName') or ''),
                         str(db.get_field_value(rec, 'Class') or '')))
    print("non-zero soul carriers: %d" % len(rows))
    print("\nCOMMON-classified (R-106 rules these to 0):")
    for rec, cls, cur, tpl, kls in sorted(rows):
        if cls.lower() != 'common':
            continue
        print("  %-72s %6.2f%%  Class=%-12s tpl=%s" % (rec, cur, kls, tpl))
    print("\nCHAMPION-classified with a live rate (HELD - Will's open call):")
    for rec, cls, cur, tpl, kls in sorted(rows):
        if cls.lower() != 'champion':
            continue
        print("  %-72s %6.2f%%  Class=%-12s tpl=%s" % (rec, cur, kls, tpl))
    print("\n(unset)-classified with a live rate (HELD - never ruled):")
    for rec, cls, cur, tpl, kls in sorted(rows):
        if cls:
            continue
        print("  %-72s %6.2f%%  Class=%-12s tpl=%s" % (rec, cur, kls, tpl))


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
