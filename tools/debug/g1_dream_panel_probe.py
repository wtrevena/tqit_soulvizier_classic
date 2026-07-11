"""Probe Dream (mastery 9) panectrl + xpack UI folder to size the Doppelganger UI
wiring. Read-only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase

OUR = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:/Users/willi/repos/tqit_soulvizier_classic/work/SoulvizierClassic/Database/SoulvizierClassic.arz"

db = ArzDatabase.from_arz(Path(OUR))
m = {n.lower(): n for n in db.record_names()}

for k, n in sorted(m.items()):
    if 'panectrl' in k and ('mastery 9' in k or ('dream' in k and 'ui' in k)):
        btns = db.get_field_value(n, 'tabSkillButtons')
        bp = db.get_field_value(n, 'BasePane')
        print('PANECTRL', n)
        print('   BasePane:', bp)
        print('   #buttons:', len(btns) if isinstance(btns, list) else btns)
        if isinstance(btns, list):
            for b in btns[:2]:
                print('     first:', b)
            for b in btns[-4:]:
                print('     ...', b)

xslots = [si for si in range(1, 40)
          if ('records\\xpack\\ui\\skills\\mastery 9\\skill%02d.dbr' % si).lower() in m]
print('xpack mastery9 UI slots:', xslots)
s1 = m.get('records\\xpack\\ui\\skills\\mastery 9\\skill01.dbr')
print('dream skill01 exists:', bool(s1))
if s1:
    for f in ('templateName', 'bitmapPositionX', 'bitmapPositionY', 'isCircular',
              'skillName', 'FileDescription', 'bitmapNameUp'):
        print('  ', f, '=', db.get_field_value(s1, f))

# also dump a few dream slot positions to find free cells
print('\n--- dream UI positions ---')
for si in xslots:
    n = m['records\\xpack\\ui\\skills\\mastery 9\\skill%02d.dbr' % si]
    print('  skill%02d: X=%s Y=%s circ=%s -> %s' % (
        si, db.get_field_value(n, 'bitmapPositionX'),
        db.get_field_value(n, 'bitmapPositionY'),
        db.get_field_value(n, 'isCircular'),
        db.get_field_value(n, 'skillName')))
