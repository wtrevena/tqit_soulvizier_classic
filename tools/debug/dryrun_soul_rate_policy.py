"""dryrun_soul_rate_policy.py - what R-105/R-106/R-107 will change, BEFORE building.

Runs build_svc_database.ruled_soul_equip_rate over a built arz and prints the
exact per-cohort move table plus every named record the rulings single out.

Usage: py tools/debug/dryrun_soul_rate_policy.py <built.arz> [--names]
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase
import build_svc_database as bsd
import apply_svc_patches as asp

NAMED = ['um_polisgaoler_99', 'um_polisgaoler_unbound_99', 'um_charon_ferryman_99',
         'um_charonform2_ferryman_99', 'um_tantalus_99', 'um_tantalus_unbound_99',
         'um_toxeus_enslaver_99', 'um_bloodtoxeus_99', 'um_toxeus_hunt_99',
         'um_toxeus_hunt_l_99', 'um_calybe_20', 'um_lyialeafsong_18',
         'svc_um_hadesmarshal_80', 'boss_charon_39', 'boss_charon_41',
         'boss_charon_43', 'boss_satyrshaman_55', 'um_legion_28c']


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    rmem, pmem = bsd.soul_spawn_provenance_sets(db)
    moves = Counter()
    held = Counter()
    per_move = defaultdict(list)
    total = 0
    idx = {}
    for rec, cls, cur in asp._soul_carrier_roster(db):
        total += 1
        idx[bsd._soul_record_basename(rec)] = (rec, cls, cur)
        t = bsd.ruled_soul_equip_rate(rec, cls, cur, rmem, pmem)
        if t is None:
            held[(cls or '(unset)', round(cur, 2))] += 1
            continue
        if abs(t - cur) < 0.01:
            continue
        moves[(round(cur, 2), round(t, 2))] += 1
        per_move[(round(cur, 2), round(t, 2))].append((rec, cls))
    print("soul carriers: %d" % total)
    print("\nMOVE TABLE (current -> ruled):")
    tot = 0
    for (a, b), n2 in sorted(moves.items(), key=lambda kv: (-kv[1], kv[0])):
        tot += n2
        print("   %7.2f%% -> %7.2f%%   x%d" % (a, b, n2))
    print("   TOTAL CHANGED: %d" % tot)
    print("\nHELD (not ruled - untouched):")
    for (cls, cur), n2 in sorted(held.items(), key=lambda kv: (-kv[1],)):
        print("   cls=%-10s cur=%6.2f%%  x%d" % (cls, cur, n2))
    print("\nNAMED RECORDS the rulings single out:")
    for bn in NAMED:
        if bn not in idx:
            print("   %-30s (not a soul carrier in this arz)" % bn)
            continue
        rec, cls, cur = idx[bn]
        t = bsd.ruled_soul_equip_rate(rec, cls, cur, rmem, pmem)
        print("   %-30s cls=%-8s %6.2f%% -> %s" %
              (bn, cls or '(unset)', cur, 'HELD' if t is None else '%.2f%%' % t))
    if '--names' in argv:
        for k in sorted(per_move):
            if moves[k] <= 25:
                print("\n  %s:" % (k,))
                for rec, cls in sorted(per_move[k]):
                    print("      %-70s %s" % (rec, cls))


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
