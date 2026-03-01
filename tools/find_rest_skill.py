"""Find the 'rest' skill in Soulvizier v0.4 database.

The rest skill lets players sleep to recover health quickly but makes them
vulnerable (die in one hit). Should be available to all players from start.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db_path = Path(sys.argv[1])
    db = ArzDatabase.from_arz(db_path)

    # Search for records with "rest" or "sleep" or "recover" in the name
    keywords = ['rest', 'sleep', 'recover', 'regen', 'meditat', 'camp',
                'heal', 'nap', 'prone', 'vulnerable']

    print('=== Records matching rest/sleep keywords ===')
    matches = []
    for name in sorted(db.record_names()):
        nl = name.lower()
        for kw in keywords:
            if kw in nl and ('skill' in nl or 'buff' in nl or 'player' in nl):
                matches.append(name)
                print(f'  {name}')
                break

    # Also search for skills that have both health regen and defense reduction
    print('\n=== Skills with massive health regen + defense debuff ===')
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue

        nl = name.lower()
        if 'skill' not in nl:
            continue

        has_regen = False
        has_defense_debuff = False
        has_vulnerability = False

        for key, tf in fields.items():
            rk = key.split('###')[0].lower()
            if 'healthregen' in rk or 'liferegen' in rk or 'healallregen' in rk:
                if tf.values and tf.values[0]:
                    try:
                        val = float(tf.values[0])
                        if val > 50:
                            has_regen = True
                    except (ValueError, TypeError):
                        pass
            if 'defensiveabsorption' in rk or 'defensiveprotection' in rk:
                if tf.values and tf.values[0]:
                    try:
                        val = float(tf.values[0])
                        if val < -50:
                            has_defense_debuff = True
                    except (ValueError, TypeError):
                        pass
            if 'characterdefensive' in rk and 'modifier' in rk:
                has_vulnerability = True

        if has_regen and (has_defense_debuff or has_vulnerability):
            print(f'  {name}')
            for key, tf in fields.items():
                rk = key.split('###')[0]
                vals = [str(v) for v in tf.values if v is not None]
                if vals:
                    vstr = ', '.join(vals)
                    if len(vstr) > 100:
                        vstr = vstr[:100] + '...'
                    print(f'    {rk} = {vstr}')

    # Broader search: any skill available to all players (no mastery requirement)
    print('\n=== Skills with "drx" prefix (SV custom skills) ===')
    drx_skills = []
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'drx' in nl and 'skill' in nl and '.dbr' in nl:
            # Check for rest-like characteristics
            fn = nl.split('/')[-1].split('\\')[-1].replace('.dbr', '')
            if any(kw in fn for kw in ['rest', 'sleep', 'camp', 'prone',
                                         'recov', 'regen', 'meditat', 'heal',
                                         'vuln', 'down']):
                drx_skills.append(name)
                print(f'  {name}')

    # Check player skills that are auto-granted
    print('\n=== Auto-granted / innate player skills ===')
    for name in db.record_names():
        nl = name.lower()
        if 'player' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if 'skill' in rk.lower() and tf.values:
                for v in tf.values:
                    vs = str(v).lower()
                    if any(kw in vs for kw in ['rest', 'sleep', 'camp', 'prone',
                                                 'recover', 'meditat']):
                        print(f'  {name} -> {rk} = {v}')

    # Just search ALL record names for "rest"
    print('\n=== ALL records with "rest" in name ===')
    for name in sorted(db.record_names()):
        if 'rest' in name.lower():
            print(f'  {name}')


if __name__ == '__main__':
    main()
