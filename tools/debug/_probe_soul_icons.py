r"""b40 RCA probe: enumerate every soul's granted-skill icon in an .arz.

For each record under records\item\equipmentring\soul, read itemSkillName
(the granted skill), resolve that skill record, and report its Class +
skillUpBitmapName / skillDownBitmapName / bitmapName. Group by icon to show
how many souls share one icon (the Lyia-nymph default hypothesis).

Usage: py tools/debug/_probe_soul_icons.py <path-to.arz>
"""
import sys
import os
from collections import defaultdict, OrderedDict
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from arz_patcher import ArzDatabase


def field0(fields, name):
    """Return the first value of field `name` (handles ### suffix keys)."""
    if not fields:
        return None
    for key, tf in fields.items():
        if key.split('###')[0] == name and tf.values and str(tf.values[0]).strip():
            return str(tf.values[0])
    return None


def norm(p):
    return (p or '').replace('/', '\\').lower()


def main():
    arz_path = sys.argv[1]
    db = ArzDatabase.from_arz(Path(arz_path))
    names = list(db.record_names())

    # Build a lower-cased lookup for skill resolution
    by_lower = {norm(n): n for n in names}

    def resolve(ref):
        r = norm(ref)
        if r in by_lower:
            return by_lower[r]
        # try with records\ prefix normalisation
        if not r.startswith('records\\') and ('records\\' + r) in by_lower:
            return by_lower['records\\' + r]
        return None

    souls = [n for n in names
             if 'equipmentring\\soul' in norm(n) and norm(n).endswith('.dbr')]
    print(f"ARZ: {arz_path}")
    print(f"Total records: {len(names)}   soul records: {len(souls)}")

    # Lyia reference summon
    lyia = resolve(r'records\skills\soulskills\summon_lyia.dbr')
    if lyia:
        lf = db.get_fields(lyia)
        print("\n=== Lyia reference summon (summon_lyia.dbr) ===")
        print("  Class:", field0(lf, 'Class'))
        print("  skillUpBitmapName:", field0(lf, 'skillUpBitmapName'))
        print("  skillDownBitmapName:", field0(lf, 'skillDownBitmapName'))
        print("  bitmapName:", field0(lf, 'bitmapName'))

    icon_groups = defaultdict(list)   # skillUpBitmapName -> [(soul, skill)]
    no_skill = []
    non_spawnpet = []
    skill_cache = {}

    for soul in sorted(souls):
        sf = db.get_fields(soul)
        isk = field0(sf, 'itemSkillName')
        if not isk:
            no_skill.append(soul)
            continue
        skrec = resolve(isk)
        if not skrec:
            icon_groups[f'<UNRESOLVED SKILL {isk}>'].append((soul, isk))
            continue
        kf = db.get_fields(skrec)
        cls = field0(kf, 'Class')
        up = field0(kf, 'skillUpBitmapName')
        if cls != 'Skill_SpawnPet':
            non_spawnpet.append((soul, skrec, cls, up))
            continue
        icon_groups[up or '<NONE>'].append((soul, skrec))

    print(f"\n=== SUMMON souls grouped by skillUpBitmapName "
          f"({sum(len(v) for k,v in icon_groups.items())} summon souls) ===")
    for icon, entries in sorted(icon_groups.items(), key=lambda kv: -len(kv[1])):
        print(f"\n[{len(entries)}] icon = {icon}")
        for soul, skrec in sorted(entries):
            print(f"    {soul.rsplit(chr(92),1)[-1]:38s} -> {skrec.rsplit(chr(92),1)[-1]}")

    print(f"\n=== Non-SpawnPet granted skills ({len(non_spawnpet)}) [proc/aura souls; not in scope] ===")
    procs_by_icon = defaultdict(int)
    for soul, skrec, cls, up in non_spawnpet:
        procs_by_icon[(cls, up)] += 1
    for (cls, up), cnt in sorted(procs_by_icon.items(), key=lambda kv: -kv[1]):
        print(f"    [{cnt}] {cls:28s} up={up}")

    print(f"\n=== Souls with NO itemSkillName ({len(no_skill)}) ===")
    for s in no_skill[:20]:
        print("   ", s.rsplit(chr(92), 1)[-1])
    if len(no_skill) > 20:
        print(f"    ... +{len(no_skill)-20} more")


if __name__ == '__main__':
    main()
