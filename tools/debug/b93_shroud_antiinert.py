r"""ANTI-INERT CONTROL for the R-250 shroud gate (build93 ship lane).

A gate that passes on the artifact it is supposed to condemn is inert. This runs
`enslaver_shroud.verify()` against an arbitrary .arz and reports which way it went,
so the ship record can show the gate measured in BOTH directions on the artifacts
that actually shipped.

Run it on the THEN-SHIPPED arz (expect FAIL) and on the newly built arz (expect OK).

  py tools/debug/b93_shroud_antiinert.py <arz> [--expect fail|pass]

Exit 0 iff the outcome matched --expect (default: just report, exit 0).

NOTE (BL-R240-DEBT-8): run the control on a POST-R-240 artifact. A pre-R-240 arz
reds for unrelated reasons and that red is the control passing, not a defect.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_TOOLS))
sys.path.insert(0, str(_TOOLS.parent))

from arz_patcher import ArzDatabase                      # noqa: E402
from patches import enslaver_shroud                      # noqa: E402


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    arz = Path(argv[1])
    expect = None
    if '--expect' in argv:
        expect = argv[argv.index('--expect') + 1].lower()

    print('anti-inert control: enslaver_shroud.verify() vs %s' % arz)
    db = ArzDatabase.from_arz(arz)
    print('  loaded %d records' % len(db._raw_records))

    outcome, detail = 'pass', ''
    try:
        enslaver_shroud.verify(db)
    except SystemExit as exc:
        outcome, detail = 'fail', str(exc)

    print('OUTCOME: %s %s' % (outcome.upper(), detail))
    if expect is None:
        return 0
    if outcome != expect:
        print('CONTROL BROKEN: expected %s, got %s' % (expect.upper(), outcome.upper()))
        return 1
    print('CONTROL OK: matched --expect %s' % expect)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
