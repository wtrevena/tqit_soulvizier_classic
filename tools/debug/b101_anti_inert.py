r"""ANTI-INERT control for the build101 ship (R-257).

A gate that cannot fail is not a gate. This runs `enslaver_shroud.verify()`
against an arz that ALREADY SHIPPED and that Will PHOTOGRAPHED NOT RENDERING
(build100 / build99's `6b89bb5d`), and requires it to RED.

Usage:
  py tools/debug/b101_anti_inert.py <arz>      # expect RED  (exit 0 = control held)
  py tools/debug/b101_anti_inert.py <arz> --expect-green

Exit 0 = the control behaved as required. Exit 1 = it did not, and the gate row
this backs must NOT be written down as evidence.
"""
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arz_patcher import ArzDatabase  # noqa: E402
from patches import enslaver_shroud  # noqa: E402


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    arz = argv[1]
    expect_green = '--expect-green' in argv

    print('=== ANTI-INERT CONTROL (R-257 / build101) ===')
    print('  arz under test : %s' % arz)
    print('  expectation    : %s' % ('GREEN (post-fix bytes)' if expect_green
                                     else 'RED (pre-fix bytes that shipped and did not render)'))
    print()

    db = ArzDatabase.from_arz(Path(arz))

    red = False
    detail = ''
    try:
        enslaver_shroud.verify(db)
    except BaseException as exc:  # the module reds by raising
        red = True
        detail = '%s: %s' % (type(exc).__name__, exc)
        print('--- verify() RAISED ---')
        traceback.print_exc(limit=3)
    else:
        print('--- verify() returned without raising (GREEN) ---')

    print()
    if expect_green:
        ok = not red
        print('CONTROL %s: wanted GREEN, got %s' % ('HELD' if ok else 'BROKEN',
                                                    'RED' if red else 'GREEN'))
    else:
        ok = red
        print('CONTROL %s: wanted RED, got %s' % ('HELD' if ok else 'BROKEN',
                                                  'RED' if red else 'GREEN'))
        if red:
            print('  RED detail: %s' % detail[:2000])
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
