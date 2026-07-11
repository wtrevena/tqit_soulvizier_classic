"""G1 Runemaster base-value probe (LANE B, read-only): dump the base-game
Runemaster records the buffs target (mastery tail, Menhir Wall, Mines) so the
buffs can be written with fail-loud expected-value guards. Also confirm what OUR
arz already overrides (wave2) + the golem block's tree slot, to avoid overlap.

Usage: py tools/debug/g1_runemaster_probe.py [base_arz] [our_arz]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase

BASE = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Database/database.arz"
OUR = sys.argv[2] if len(sys.argv) > 2 else \
    r"C:/Users/willi/repos/tqit_soulvizier_classic/work/SoulvizierClassic/Database/SoulvizierClassic.arz"


def norm(s):
    return s.replace('/', '\\').lower().strip()


def dump(db, m, path, fields):
    n = m.get(norm(path))
    print(f"\n=== {path}  ({'FOUND' if n else 'absent'})")
    if not n:
        return
    fm = {k.split('###')[0]: tf for k, tf in db.get_fields(n).items()}
    for f in fields:
        if f in fm and fm[f].values:
            v = fm[f].values
            disp = v if len(v) <= 6 else f"[{v[0]}..{v[-1]}] len{len(v)}"
            print(f"   {f} = {disp}")


def main():
    base = ArzDatabase.from_arz(Path(BASE))
    bm = {norm(n): n for n in base.record_names()}
    print("###### BASE GAME Runemaster records ######")
    dump(base, bm, r'records\xpack2\skills\runemaster\runemaster_mastery.dbr',
         ['characterLife', 'characterMana', 'characterDefensiveAbility',
          'characterDodgePercent', 'characterDeflectProjectile',
          'characterArmorAbsorptionPercent', 'skillMaxLevel'])
    dump(base, bm, r'records\xpack2\skills\runemaster\menhirwall.dbr',
         ['Class', 'skillCooldownTime', 'spawnObjectsTimeToLive',
          'skillActiveDuration', 'skillMaxLevel', 'skillUltimateLevel',
          'skillManaCost', 'skillDisplayName'])
    # find the mines record(s)
    print("\n=== base Runemaster records containing 'mine' ===")
    for k, n in sorted(bm.items()):
        if 'runemaster' in k and 'mine' in k:
            print(f"   {n}")
    dump(base, bm, r'records\xpack2\skills\runemaster\runemine.dbr',
         ['Class', 'skillMaxLevel', 'skillUltimateLevel', 'skillCooldownTime',
          'skillManaCost', 'skillActiveDuration', 'spawnObjectsTimeToLive',
          'skillDisplayName', 'petLimit'])

    print("\n\n###### OUR arz: what wave2 already overrides + golem slot ######")
    our = ArzDatabase.from_arz(Path(OUR))
    om = {norm(n): n for n in our.record_names()}
    for p in (r'records\xpack2\skills\runemaster\runemaster_mastery.dbr',
              r'records\xpack2\skills\runemaster\menhiraltar.dbr',
              r'records\xpack2\skills\runemaster\menhirwall.dbr',
              r'records\xpack2\skills\runemaster\runemine.dbr'):
        print(f"   OUR has override: {p.rsplit(chr(92),1)[-1]} = {norm(p) in om}")
    # RuneMaster tree slot occupancy (base, since our arz has no override)
    rm_tree = bm.get(norm(r'records\xpack2\skills\runemaster\runemaster_skilltree.dbr'))
    if rm_tree:
        fm = {k.split('###')[0]: tf for k, tf in base.get_fields(rm_tree).items()}
        hi = 0
        for i in range(1, 40):
            v = fm.get(f'skillName{i}')
            if v and v.values and str(v.values[0]).strip():
                hi = i
        print(f"\n   BASE RuneMaster_SkillTree highest skillName = {hi}")


if __name__ == '__main__':
    main()
