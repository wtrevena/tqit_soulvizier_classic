"""G1 port-record field dump (LANE B, read-only): the 6 SVAERA closure records
that must be imported for Frost Nova FX + Doppelganger pet, so the graft anchors
on verified field values (esp. dreamcopypet's difficulty-scaling skillName slot).

Usage: py tools/debug/g1_port_dump.py [svaera_arz]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase

SVAERA = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:/Program Files (x86)/Steam/steamapps/workshop/content/475150/2076433374/SVAERA_customquest/Database/SVAERA_customquest.arz"


def norm(s):
    return s.replace('/', '\\').lower().strip()


def main():
    sv = ArzDatabase.from_arz(Path(SVAERA))
    m = {norm(n): n for n in sv.record_names()}

    def dump(path):
        n = m.get(norm(path))
        print(f"\n=== {path}  ({'FOUND' if n else 'MISSING'})")
        if not n:
            return
        fields = sv.get_fields(n)
        fm = {k.split('###')[0]: tf for k, tf in fields.items()}
        for f in ('templateName', 'Class', 'actorHeight', 'characterMesh',
                  'skinConversionTable', 'petBurstSpawn',
                  'spawnObjectsTimeToLive', 'petLimit', 'charAnimationTableName'):
            if f in fm and fm[f].values:
                v = fm[f].values
                print(f"   {f} = {v if len(v) > 1 else v[0]}")

        def sk_key(s):
            digits = ''.join(c for c in s if c.isdigit())
            return (s.rstrip('0123456789'), int(digits) if digits else 0)
        for k in sorted(fm, key=sk_key):
            if k.startswith('skillName') or k.startswith('skillLevel'):
                print(f"   {k} = {fm[k].values}")
        refs = []
        for k, tf in fields.items():
            b = k.split('###')[0]
            for v in tf.values:
                if isinstance(v, str) and v.lower().endswith('.dbr'):
                    refs.append((b, v))
        if refs:
            print("   -- dbr refs --")
            for b, v in refs:
                print(f"      {b} -> {v}")

    for p in [r'records\xpack\skills\dream\pet\dreamcopypet.dbr',
              r'records\xpack\skills\dream\pet\dreamcopypet_petskill_aura.dbr',
              r'records\xpack\skills\dream\pet\anm\anm_dreamcopy.dbr',
              r'records\skills\boss skills\hero_conversionimmunity_pets.dbr',
              r'records\effects\_drx_effects\storm\storm_frostnova_fx.dbr',
              r'records\effects\_drx_effects\storm\storm_frostnova_fxpak.dbr']:
        dump(p)


if __name__ == '__main__':
    main()
