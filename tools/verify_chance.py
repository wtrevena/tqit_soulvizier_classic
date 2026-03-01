import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

db = ArzDatabase.from_arz(Path(sys.argv[1]))

tests = [
    'records\\creature\\monster\\satyr\\um_petraeus_07.dbr',
    'records\\creature\\monster\\harpy\\um_aello_14.dbr',
    'records\\creature\\monster\\skeleton\\um_hekos_13.dbr',
    'records\\creature\\monster\\questbosses\\boss_gorgon_medusa_18.dbr',
]
for name in tests:
    c = db.get_field_value(name, 'lootFinger2Chance')
    i = db.get_field_value(name, 'lootFinger2Item1')
    print(f'{name.split(chr(92))[-1]}: chance={c}, item={str(i)[:60] if i else None}')
