r"""Dump the FULL field set (name, dtype, values) of the base-game Runemaster
mastery-10 panectrl records, so the Lane A golem panel-override can be
reconstructed faithfully without base_db (which is freed before the golem runs).

usage: py tools/debug/rg_panel_fields.py <base_game.arz>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase  # noqa: E402

PANES = [
    r'records\xpack2\ui\skills\mastery 10\panectrl.dbr',
    r'records\xpack3\ui\skills\mastery 10\panectrl.dbr',
]


def main(arz):
    db = ArzDatabase.from_arz(Path(arz))
    names = {n.replace('/', '\\').lower(): n for n in db.record_names()}
    for p in PANES:
        real = names.get(p.replace('/', '\\').lower())
        print("=" * 78)
        print(p, '->', real)
        if not real:
            print("  ABSENT")
            continue
        ff = db.get_fields(real)
        for k, tf in ff.items():
            fname = k.split('###')[0]
            print(f"  {fname} | dtype={tf.dtype} | n={len(tf.values)}")
            if fname != 'tabSkillButtons':
                print(f"      values={list(tf.values)}")


if __name__ == '__main__':
    main(sys.argv[1])
