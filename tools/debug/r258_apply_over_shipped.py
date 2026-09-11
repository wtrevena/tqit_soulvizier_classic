r"""R-258: apply the module over a BUILT arz and write the result, then RECORD-DIFF it.

WHAT THIS IS, AND WHAT IT IS NOT. This is **not** the cold build and must never be
reported as one (the `BL-R257-DEBT-3` law: a module's `--negtest` being green is not
proof; the build's own entrypoint is). It was written on 2026-09-09 because the cold
build's MANDATORY inputs were not on this machine THAT DAY - `upstream/`,
`reference_mods/` and `third_party/` had been emptied/removed that morning, so
`tools/build_svc_database.py` could not start (its `check_build_inputs.preflight`
hard-fails on `sv098i_arz` + `sv09_arz` before anything else runs). THAT IS HISTORY:
the inputs were recovered on 2026-09-10 (five of six from the NAS archives, SV 0.4.1
re-downloaded; off-repo copy at Z:\Computer Backup\tqit_soulvizier_classic\
third_party_archives\) and the cold build RAN - arz 7dad9a8ad377ff9a65d17c144a57dde3,
55,631,843 B, 51,355 records, det-2x plus a byte-identical third run by the vet, with
the same record-diff this tool predicted (ADDED 3 / CHANGED 1 / REMOVED 0). The cold
artifact is the artifact of record; this tool's output (e819a9a3) is EVIDENCE ONLY, and
the tool stays useful as an attributed record-diff over any baseline.

What it DOES give, on real bytes rather than a stub: the module's own `apply()` run
over the 51,352 shipped records, the result WRITTEN to a real `.arz` through the same
`ArzDatabase.write_arz` the build uses, the gate re-run on the written file, and a
full record-diff of the written file against the baseline with every delta attributed.

    py tools/debug/r258_apply_over_shipped.py <baseline.arz> <out.arz>
    py tools/debug/r258_apply_over_shipped.py <baseline.arz> <out.arz> --diff-only

EVERY delta must be attributable to R-258:
  ADDED (3)    records\item\loottables\svc\svc_devourersoul_guaranteed_{n,e,l}.dbr
  CHANGED (1)  records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr, and on
               it ONLY the four fields this ruling writes:
                 lootMisc1Item3            (NEW - the three guaranteed soul tables)
                 chanceToEquipMisc1Item3   0  -> 100
                 chanceToEquipMisc1Item1   80 -> 0   (health potions muted)
                 chanceToEquipMisc1Item2   20 -> 0   (energy potions muted)
  REMOVED      MUST BE ZERO.
Anything else is UNATTRIBUTED and a NO-GO.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from arz_patcher import ArzDatabase                        # noqa: E402
from patches import devourer_soul_delivery as DSD          # noqa: E402

DEVOURER = DSD._DEVOURER
NEW_RECORDS = {DSD._norm(p) for p in DSD._SOUL_TAB}
ALLOWED_FIELDS = {
    'lootMisc1Item3',
    'chanceToEquipMisc1Item3',
    'chanceToEquipMisc1Item1',
    'chanceToEquipMisc1Item2',
}


def snapshot(db):
    out = {}
    for name in db.record_names():
        f = db.get_fields(name) or {}
        rec = {}
        for k, tf in f.items():
            base = str(k).split('###')[0]
            vals = tf if isinstance(tf, (list, tuple)) else getattr(tf, 'values', [tf])
            rec[base] = tuple(str(v) for v in vals)
        out[DSD._norm(name)] = rec
    return out


def diff(base, new):
    added = sorted(set(new) - set(base))
    removed = sorted(set(base) - set(new))
    changed = {}
    for n in sorted(set(base) & set(new)):
        a, b = base[n], new[n]
        moved = {}
        for k in sorted(set(a) | set(b)):
            if a.get(k) != b.get(k):
                moved[k] = (a.get(k), b.get(k))
        if moved:
            changed[n] = moved
    return added, removed, changed


def report(added, removed, changed):
    bad = []
    print("\n=== RECORD-DIFF: ADDED %d / REMOVED %d / CHANGED %d ==="
          % (len(added), len(removed), len(changed)))
    for n in added:
        ok = n in NEW_RECORDS
        print("  ADDED   %-70s %s" % (n, 'R-258 soul table' if ok else 'UNATTRIBUTED'))
        if not ok:
            bad.append('ADDED ' + n)
    for n in removed:
        print("  REMOVED %-70s UNATTRIBUTED (this lane retires nothing)" % n)
        bad.append('REMOVED ' + n)
    for n, moved in changed.items():
        if n != DSD._norm(DEVOURER):
            print("  CHANGED %-70s UNATTRIBUTED (only the Devourer may move)" % n)
            bad.append('CHANGED ' + n)
            continue
        print("  CHANGED %s" % n)
        for k, (a, b) in moved.items():
            ok = k in ALLOWED_FIELDS
            print("      %-26s %r -> %r   %s"
                  % (k, a, b, 'R-258' if ok else 'UNATTRIBUTED'))
            if not ok:
                bad.append('FIELD %s::%s' % (n, k))
    return bad


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    base_path, out_path = Path(argv[1]), Path(argv[2])
    diff_only = '--diff-only' in argv
    print("baseline: %s" % base_path)
    print("output  : %s" % out_path)

    base_db = ArzDatabase.from_arz(base_path)
    before = snapshot(base_db)

    if not diff_only:
        DSD.apply(base_db, {})
        problems = DSD._check(base_db)
        if problems:
            for p in problems:
                print("  GATE STILL RED AFTER apply(): %s" % p)
            return 1
        out_path.parent.mkdir(parents=True, exist_ok=True)
        base_db.write_arz(out_path)
        print("  written: %s (%d bytes)" % (out_path, out_path.stat().st_size))

    new_db = ArzDatabase.from_arz(out_path)
    after = snapshot(new_db)
    print("  records: baseline %d -> built %d" % (len(before), len(after)))

    bad = report(*diff(before, after))

    print("\n=== the gate, re-run on the WRITTEN file ===")
    gate = DSD._check(new_db)
    for p in gate:
        print("  R-258 OFFENDER: %s" % p)
    if not gate:
        share = DSD._row_share(new_db, DSD._resolve(new_db, DEVOURER),
                               DSD._SLOT, DSD._SOUL_ROW)
        print("  R-258 gate PASS on the written bytes; measured soul share %.4f%%"
              % share)

    if bad or gate:
        print("\nRESULT: NO-GO - %d unattributed delta(s), %d gate problem(s)"
              % (len(bad), len(gate)))
        return 1
    print("\nRESULT: GO - every delta attributed to R-258, zero unexplained, gate green")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
