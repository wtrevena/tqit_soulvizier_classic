r"""Explain the build93 shroud SLOT MOVE (skillName13 -> skillName18) on the
three Enslaver pet tiers, from the artifacts themselves.

The R-250 lane record predicted "exactly one field (`controller`) on each of the
4 roster surfaces". On the shipped build83-era arz that held. Against the
build92 arz the three PET tiers show 4 changed fields each, because the module's
free-slot test now unions the orphan `skillLevel` arrays into the used set
(BL-R250-DEBT-4) instead of testing `skillName` freeness alone.

This prints, for each pet tier and each arz, every skillName<i> and skillLevel<i>
slot, so the move is a MEASUREMENT and not an assumption.

  py tools/debug/b93_shroud_slot_probe.py <old.arz> <new.arz>
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_TOOLS))

from arz_patcher import ArzDatabase                      # noqa: E402

PETS = [r'records\skills\soulskills\pets\toxeus_enslaver_%d.dbr' % i
        for i in (1, 2, 3)]
SHROUD = r'records\skills\monster skills\buff_self\svc_enslaver_shroud.dbr'


def slots(db, rec):
    names, levels = {}, {}
    for k, tf in (db.get_fields(rec) or {}).items():
        b = k.split('###')[0]
        if b.startswith('skillName') and b[9:].isdigit():
            v = str(tf.values[0]) if tf.values else ''
            if v.strip():
                names[int(b[9:])] = v
        elif b.startswith('skillLevel') and b[10:].isdigit() and tf.values:
            levels[int(b[10:])] = list(tf.values)
    return names, levels


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    old = ArzDatabase.from_arz(Path(argv[1]))
    new = ArzDatabase.from_arz(Path(argv[2]))

    bad = 0
    for pet in PETS:
        print('\n=== %s ===' % pet)
        on, ol = slots(old, pet)
        nn, nl = slots(new, pet)
        allslots = sorted(set(on) | set(ol) | set(nn) | set(nl))
        print('  slot | OLD name                          OLD lvl | NEW name                          NEW lvl')
        for i in allslots:
            a = (on.get(i) or '-').rsplit('\\', 1)[-1]
            b = (nn.get(i) or '-').rsplit('\\', 1)[-1]
            print('  %4d | %-33s %-7s | %-33s %-7s'
                  % (i, a[:33], ol.get(i, '-'), b[:33], nl.get(i, '-')))

        # 1. the shroud moved, and nothing else did
        oldslot = next((i for i, v in on.items() if v.lower() == SHROUD.lower()), None)
        newslot = next((i for i, v in nn.items() if v.lower() == SHROUD.lower()), None)
        print('  shroud slot: OLD=%s -> NEW=%s' % (oldslot, newslot))

        # 2. NO functional skill was displaced or lost
        oldkit = {v.lower() for i, v in on.items() if i != oldslot}
        newkit = {v.lower() for i, v in nn.items() if i != newslot}
        lost, gained = oldkit - newkit, newkit - oldkit
        if lost or gained:
            bad += 1
            print('  !! KIT CHANGED beyond the shroud: lost=%s gained=%s'
                  % (sorted(lost), sorted(gained)))
        else:
            print('  OK  every OTHER skill in the kit is identical (%d skills)' % len(oldkit))

        # 3. WHY 18: every slot below it is occupied in the NEW db by a name OR a level
        if newslot:
            blockers = []
            for i in range(1, newslot):
                if i in nn or i in nl:
                    blockers.append('%d:%s' % (i, 'name' if i in nn else 'LEVEL-only'))
            print('  WHY slot %d: slots 1..%d all occupied -> %s'
                  % (newslot, newslot - 1, ', '.join(blockers)))
            free = [i for i in range(1, newslot) if i not in nn and i not in nl]
            if free:
                bad += 1
                print('  !! slot %s was free and unused - the move is NOT explained' % free)

        # 4. the orphan level array the OLD build clobbered
        if oldslot is not None:
            print('  orphan skillLevel%d: OLD=%s NEW=%s  (name-only freeness test '
                  'wrote a skill over a live per-difficulty array)'
                  % (oldslot, ol.get(oldslot, 'ABSENT'), nl.get(oldslot, 'ABSENT')))

    print('\nRESULT: %s' % ('UNEXPLAINED DIFFERENCES - investigate' if bad
                            else 'EXPLAINED - shroud slot move only, kits otherwise identical'))
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
