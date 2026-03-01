"""Check default caravan stash settings in the SV 0.98i database."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

db = ArzDatabase.from_arz(Path(sys.argv[1]))

for name in db.record_names():
    nl = name.lower()
    if 'caravan' in nl and ('stash' in nl or 'storage' in nl or 'inventory' in nl):
        print(f'RECORD: {name}')
        fields = db.get_fields(name)
        if fields:
            for key, tf in sorted(fields.items()):
                rk = key.split('###')[0]
                if tf.values and tf.values[0] is not None:
                    v = tf.values[0]
                    if isinstance(v, str) and len(v) > 60:
                        v = '...' + v[-40:]
                    print(f'  {rk} = {v}')
        print()
