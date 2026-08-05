"""The 12-skill proof table, read straight off a built arz with no lane code."""
import re, sys
from pathlib import Path
ROOT = Path(sys.argv[1]); ARZ = Path(sys.argv[2])
sys.path.insert(0, str(ROOT / 'tools'))
from arz_patcher import ArzDatabase
db = ArzDatabase.from_arz(ARZ)
rm = {n.replace('/', '\\').lower(): n for n in db.record_names()}
R = lambda p: rm.get(str(p).replace('/', '\\').strip().lower()) if p else None
def F(r): return db.get_fields(r) or {}
def s(r, n):
    if not r: return None
    for k, tf in F(r).items():
        if k.split('###')[0] == n and tf.values: return str(tf.values[0])
    return None

NAMES = {
    ('a', 1): 'Ravok the Lawless ~ Machae Reaver',
    ('a', 2): 'Sethuun ~ Machae Soul-Warden',
    ('b', 1): 'Bhikru the Bilespitter ~ Machae Venomancer',
    ('b', 2): 'Nakoth ~ Machae Plague-Ward',
    ('c', 1): 'Kharzun the Ember ~ Machae Pyre-Ward',
    ('c', 2): 'Voreth ~ Machae Cinder-Reaver',
}
SLOTS = [('skillName4', 'specialAttack2SkillName'), ('skillName5', 'specialAttack3SkillName')]

print('| # | guard | slot | skill wired in the BUILT arz | Class | special anim | rig declares | CAN FIRE? |')
print('|---|---|---|---|---|---|---|---|')
n = 0
for g in 'abc':
    for i in (1, 2):
        mon = R(r'records\xpack\creatures\monster\machae\svc_general_%s_guard%d.dbr' % (g, i))
        tbl = R(s(mon, 'charAnimationTableName'))
        clips = set()
        for k, tf in F(tbl).items():
            m = re.match(r'(.+?)SpecialAnimRef(\d+)$', k.split('###')[0])
            if m and int(m.group(2)) <= 15 and tf.values and str(tf.values[0]).strip():
                clips.add(str(tf.values[0]).strip().lower())
        for sk_slot, sp_slot in SLOTS:
            n += 1
            sk = s(mon, sk_slot)
            sp = s(mon, sp_slot)
            rec = R(sk)
            anim = s(rec, 'skillSpecialAnimationName')
            a = (anim or '').strip()
            ok = (not a) or (a.lower() in clips)
            print('| %d | %s | %s + %s | `%s` | %s | %s | %s | **%s** |'
                  % (n, NAMES[(g, i)], sk_slot, sp_slot.replace('SkillName', ''),
                     (sk or '').split('\\')[-1], s(rec, 'Class'),
                     ('`%s`' % a) if a else '(none)',
                     ', '.join(sorted(clips)),
                     'YES' if ok else 'NO'))
            assert sp == sk, 'slot mismatch %s %s' % (sk, sp)

print()
print('| slot-1 special (all six inherited it dead) | wired to | anim | CAN FIRE? |')
print('|---|---|---|---|')
for g in 'abc':
    for i in (1, 2):
        mon = R(r'records\xpack\creatures\monster\machae\svc_general_%s_guard%d.dbr' % (g, i))
        sk = s(mon, 'specialAttackSkillName')
        k3 = s(mon, 'skillName3')
        rec = R(sk)
        a = (s(rec, 'skillSpecialAnimationName') or '').strip()
        print('| %s | `%s` (skillName3 `%s`) | %s | **%s** |'
              % (NAMES[(g, i)].split(' ~ ')[0], (sk or '').split('\\')[-1],
                 (k3 or '').split('\\')[-1], ('`%s`' % a) if a else '(none)',
                 'YES' if not a else 'CHECK'))

print()
print('=== the 5 blank-anim clones + their SHIPPED donors (shared-record law) ===')
CL = [(r'records\xpack\skills\monsterskills\activeattackprojectile\hero_vomitbile.dbr',
       r'records\skills\svc\svc_machaeguard_vomitbile.dbr'),
      (r'records\xpack\skills\monsterskills\activeattackprojectile\empusavenomancer_venombolt.dbr',
       r'records\skills\svc\svc_machaeguard_venombolt.dbr'),
      (r'records\xpack\skills\monsterskills\activeattackwave\hero_flamewave.dbr',
       r'records\skills\svc\svc_machaeguard_flamewave.dbr'),
      (r'records\xpack\skills\monsterskills\activeattackmelee\gigantes_shieldcharge.dbr',
       r'records\skills\svc\svc_machaeguard_embercharge.dbr'),
      (r'records\skills\defensive\shieldcharge.dbr',
       r'records\skills\svc\svc_machaeguard_shieldcharge.dbr')]
guards = {R(r'records\xpack\creatures\monster\machae\svc_general_%s_guard%d.dbr' % (g, i))
          for g in 'abc' for i in (1, 2)}
for d, c in CL:
    dr, cr = R(d), R(c)
    others = 0
    for rec in db.record_names():
        if rec in guards:
            continue
        for k, tf in (F(rec) or {}).items():
            f = k.split('###')[0]
            if f.startswith('skillName') or f.startswith('specialAttack'):
                for v in (tf.values or []):
                    if isinstance(v, str) and v.replace('/', '\\').lower() == d.lower():
                        others += 1
    print('  donor %-36s anim=%-14r  |  clone %-34s anim=%-8r  Class match=%s  donor kept %d non-guard carrier slot(s)'
          % (d.split('\\')[-1], s(dr, 'skillSpecialAnimationName'),
             c.split('\\')[-1], s(cr, 'skillSpecialAnimationName'),
             s(dr, 'Class') == s(cr, 'Class'), others))
