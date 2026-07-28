r"""sweep_soul_drop_slots - the R-39 "roster drop-slot sweep".

WHAT IT ANSWERS
---------------
"Is any monster in the roster wired so its soul can never actually drop?"

A soul reaches the player through FOUR fields that must agree on ONE equip slot:

    loot<Slot>Item1            the soul (or the difficulty-indexed n/e/l triple)
    chanceToEquip<Slot>        the roll that the slot pays out at all      (> 0)
    chanceToEquip<Slot>Item1   the soul's weight within that slot          (> 0)
    dropItems                  equipped items drop on death                (== 1)

Any one of those at zero silently kills the drop while the record still *looks*
wired. This sweep reports every disagreement, classified.

WHAT IS **NOT** A DEFECT (the two design rules this sweep encodes)
------------------------------------------------------------------
1. RANK GATING. Only Hero/Boss/Quest-rank monsters drop souls;
   `wire_souls_to_monsters` deliberately zeroes `chanceToEquipFinger2` on
   Common/Champion records that merely INHERIT soul loot from a shared parent
   (the build13 yeti fix - 419 records). A zero on a Common/Champion is the
   design working, so those are excluded outright.
2. TERMINAL-FORM GATING. A multi-form boss drops its soul on the LAST form only.
   The shallower forms keep the loot ref but sit at chance 0 and carry
   `actorToSpawnOnDeath` pointing at the next form. This sweep FOLLOWS that chain
   and only reports a gated dropper if the chain does NOT end at a record that
   actually pays out. That is a mechanical test, not a hand-maintained waiver
   list, so a genuinely broken chain still fails.

Everything left over is either a real defect or is covered by a named ruling in
docs/WILL_RULINGS.md, which the WAIVERS table below cites explicitly.

USAGE
-----
    py tools/sweep_soul_drop_slots.py <arz> [<arz> ...]
    py tools/sweep_soul_drop_slots.py <arz> --gate     # exit 1 on any UNWAIVED finding

Read-only: never writes a record, never touches the build.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arz_patcher import ArzDatabase

BS = chr(92)
DROPPERS = {'Hero', 'Boss', 'Quest'}
SLOTS = ('Finger1', 'Finger2', 'Misc1', 'Misc2', 'Misc3', 'Head', 'Torso',
         'LeftHand', 'RightHand', 'Forearm', 'LowerBody')

# Records whose gated/odd wiring is DESIGN, each citing the ruling or report that
# made it so. Matched as a case-insensitive substring of the record path.
# RETIREMENT PROTOCOL: nothing here is ever deleted on the strength of this sweep;
# a waiver means "the ledger already decided this", not "safe to remove".
WAIVERS = (
    ('aphiastas', 'keres', 'A4 Aphiastas-zero: chanceToEquipFinger2=0 on the 7 Aphiastas '
                           'keres records is deliberate (docs/BACKLOG.md A4)'),
    ('um_afaistas', 'keres', 'A4 Aphiastas-zero: the record spells the family "afaistas" '
                             'while its soul spells it "aphiastas" - same de-wired family '
                             '(docs/BACKLOG.md A4)'),
    ('_illusion', '', 'illusion duplicate of a real hero: dropItems=0 is deliberate, or the '
                      'phantom would duplicate the original\'s loot'),
    ('legion_28', 'eurynomus', 'b56 legion soul stages: only the TERMINAL stage drops; the '
                               'shallower stages keep inert loot refs (R-ledger b56)'),
    ('conflicted copy', '', 'malformed upstream amgoz duplicate record (b78 noise class) - '
                            'not a placed encounter'),
    ('copy of ', '', 'upstream working-copy junk record - not a placed encounter'),
    (BS + 'skills' + BS + 'test' + BS, '', 'SV test-harness record, never placed'),
)


def _scalar(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _val(db, rec, field, default=None):
    v = _scalar(db.get_field_value(rec, field))
    return default if v is None else v


def _list(db, rec, field):
    f = db.get_fields(rec)
    if not f:
        return []
    for key, tf in f.items():
        if key.split('###')[0] == field:
            return list(tf.values)
    return []


def _waiver_for(rec):
    low = rec.lower()
    for needle, extra, why in WAIVERS:
        if needle.lower() in low and (not extra or extra.lower() in low):
            return why
    return None


def _chain_pays_out(db, rec, seen=None):
    """Follow actorToSpawnOnDeath; True if any form in the chain pays a soul out."""
    seen = seen or set()
    cur = rec
    while cur and cur.lower() not in seen:
        seen.add(cur.lower())
        try:
            if float(_val(db, cur, 'chanceToEquipFinger2', 0.0) or 0.0) > 0.0:
                return cur
        except (TypeError, ValueError):
            pass
        nxt = _val(db, cur, 'actorToSpawnOnDeath')
        nxt = str(nxt).strip() if nxt else ''
        if not nxt or not db.has_record(nxt):
            return None
        cur = nxt
    return None


def sweep(db):
    findings = []
    for name in db.record_names():
        f = db.get_fields(name)
        if not f:
            continue
        cls = f.get('Class')
        if not cls or not str(cls.values[0]).startswith('Monster'):
            continue
        rank = str(_val(db, name, 'monsterClassification', '') or '')
        if rank not in DROPPERS:
            continue                      # design rule 1: rank gating
        for slot in SLOTS:
            loot = [str(v) for v in _list(db, name, 'loot%sItem1' % slot)]
            if not any((BS + 'soul' + BS) in p.lower() for p in loot):
                continue
            real = [p for p in loot if p and p != '#']
            try:
                chance = float(_val(db, name, 'chanceToEquip%s' % slot, 0.0) or 0.0)
            except (TypeError, ValueError):
                chance = 0.0
            try:
                weight = float(_val(db, name, 'chanceToEquip%sItem1' % slot, 0.0) or 0.0)
            except (TypeError, ValueError):
                weight = 0.0
            raw_drop = _val(db, name, 'dropItems')
            drop_set = raw_drop is not None
            try:
                drop = int(raw_drop or 0)
            except (TypeError, ValueError):
                drop = 0

            dangling = [p for p in real if not db.has_record(p)]
            if dangling:
                findings.append(('P0-DANGLING-SOUL', rank, name, slot,
                                 'soul record does not exist: %s' % dangling[0]))
            if chance > 0 and weight <= 0:
                findings.append(('P0-ZERO-WEIGHT', rank, name, slot,
                                 'chanceToEquip%s=%g but the soul has weight %g in '
                                 'that slot - the roll can fire and never pay the '
                                 'soul' % (slot, chance, weight)))
            if chance > 0 and drop_set and drop != 1:
                findings.append(('P0-NO-DROPITEMS', rank, name, slot,
                                 'dropItems=%d explicitly, while 881/888 active soul '
                                 'droppers set it to 1 - every equipped item on this '
                                 'record, the soul included, is suppressed on death'
                                 % drop))
            elif chance > 0 and not drop_set:
                # The field is simply absent, so the record inherits the Monster.tpl
                # default. That default is not established here, so this is reported
                # as an unknown rather than asserted as a defect.
                findings.append(('P2-DROPITEMS-UNSET', rank, name, slot,
                                 'dropItems is ABSENT (inherits the template default); '
                                 '881/888 active soul droppers set it explicitly to 1'))
            if chance <= 0:
                terminal = _chain_pays_out(db, name)
                if terminal is None:
                    findings.append(('P1-GATED-DROPPER', rank, name, slot,
                                     'chanceToEquip%s=0 and no form in its '
                                     'actorToSpawnOnDeath chain pays the soul out - '
                                     'this soul is unobtainable' % slot))
            if len(real) not in (1, 3):
                findings.append(('P2-ODD-TRIPLE', rank, name, slot,
                                 'loot%sItem1 has %d real entries (expected 1 or the '
                                 'n/e/l triple)' % (slot, len(real))))
    return findings


def main(argv):
    gate = '--gate' in argv
    paths = [a for a in argv[1:] if not a.startswith('--')]
    if not paths:
        print(__doc__)
        return 2
    worst = 0
    for p in paths:
        db = ArzDatabase.from_arz(Path(p))
        findings = sweep(db)
        unwaived, waived = [], []
        for row in findings:
            (waived if _waiver_for(row[2]) else unwaived).append(row)
        print('\n=== ROSTER DROP-SLOT SWEEP: %s ===' % p)
        print('  findings: %d total  (%d unwaived / %d waived by a named ruling)'
              % (len(findings), len(unwaived), len(waived)))
        for kind, rank, rec, slot, why in sorted(unwaived):
            print('  [%s] %-6s %s (%s)\n        %s' % (kind, rank, rec, slot, why))
        for kind, rank, rec, slot, why in sorted(waived):
            print('  WAIVED [%s] %s (%s)\n        finding: %s\n        waiver : %s'
                  % (kind, rec, slot, why, _waiver_for(rec)))
        if not unwaived:
            print('  RESULT: PASS - every Hero/Boss/Quest soul in the roster is '
                  'reachable (directly or via its terminal form)')
        else:
            print('  RESULT: FAIL - %d unwaived drop-slot defect(s)' % len(unwaived))
            worst = 1
    return worst if gate else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
