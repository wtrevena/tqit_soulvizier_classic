"""Quick verify the stash records in deployed database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

db = ArzDatabase.from_arz(Path(sys.argv[1]))

sw = 'records\\xpack\\ui\\caravan\\stashwindow.dbr'
si = 'records\\xpack\\ui\\caravan\\stashinventory.dbr'

for name, label in [(sw, 'StashWindow'), (si, 'StashInventory')]:
    fields = db.get_fields(name)
    if not fields:
        print(f'{label}: MISSING!')
        continue
    print(f'\n{label}:')
    for key, tf in sorted(fields.items(), key=lambda x: x[0]):
        rk = key.split('###')[0]
        vals = ', '.join(str(v) for v in tf.values)
        print(f'  {rk} = {vals}')
