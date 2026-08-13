"""R-247.5/6 probe: dump the Endless Hunt + EoAT + Toxeus-soul chain (read-only).

Usage: py tools/debug/r247_hunt_chain_probe.py <arz> [substring ...]

Prints every field of each record whose name contains any given substring
(default: the R-247 Hunt/EoAT/soul roster). Read-only ground truth for the
R-247 rulings 5 + 6 fixes.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase  # noqa: E402

DEFAULT_SUBSTRINGS = [
    'um_toxeus_hunt', 'toxeus_hunt_soul', 'svc_hunt_', 'runbreaker',
    'toxeus_eoat', 'soul_of_toxeus', 'svc_rite_guaranteed',
    'enslaver_soul_', 'blood_toxeus_soul_', r'skeleton\toxeus_soul',
    'summon_bloodtoxeus', 'summon_toxeus', 'um_hunt_courser',
    'svc_courser', 'hunt_courser', 'ferryman_soul',
]


def main():
    arz = Path(sys.argv[1])
    subs = [s.lower() for s in (sys.argv[2:] or DEFAULT_SUBSTRINGS)]
    db = ArzDatabase.from_arz(arz)
    for rec in sorted(db.record_names(), key=str.lower):
        rl = rec.lower()
        if not any(s in rl for s in subs):
            continue
        print('=' * 90)
        print(rec)
        ff = db.get_fields(rec) or {}
        for k, tf in ff.items():
            vals = tf.values
            if vals is None or vals == [] or vals == [''] or vals == [0] or vals == [0.0]:
                continue
            print('  %-42s %r' % (k.split('###')[0], vals if len(vals) > 1 else vals[0]))


if __name__ == '__main__':
    main()
