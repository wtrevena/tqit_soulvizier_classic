"""Fix scaling issues in uber_soul_designs.py"""
import re

with open(r'c:\Users\willi\repos\tqit_soulvizier_classic\tools\uber_soul_designs.py', 'r') as f:
    content = f.read()

# Fix offensiveTotalDamageModifier: 0.0x -> x
for old, new in [('0.05', '5'), ('0.06', '6'), ('0.07', '7'), ('0.08', '8')]:
    content = content.replace(
        f"'offensiveTotalDamageModifier': {old}",
        f"'offensiveTotalDamageModifier': {new}"
    )

def make_booster(field_name):
    def boost_int_field(match):
        val = int(match.group(1))
        if field_name == 'characterAttackSpeedModifier':
            new_val = min(val * 3, 20) if val > 0 else max(val * 2, -20)
        elif field_name == 'characterSpellCastSpeedModifier':
            new_val = min(val * 3, 25) if val > 0 else max(val * 3, -25)
        elif field_name == 'characterRunSpeedModifier':
            new_val = min(val * 3, 15) if val > 0 else max(val * 3, -15)
        else:
            new_val = val
        return f"'{field_name}': {new_val}"
    return boost_int_field

for field in ['characterAttackSpeedModifier', 'characterSpellCastSpeedModifier', 'characterRunSpeedModifier']:
    pattern = f"'{field}': (-?\\d+)"
    content = re.sub(pattern, make_booster(field), content)

with open(r'c:\Users\willi\repos\tqit_soulvizier_classic\tools\uber_soul_designs.py', 'w') as f:
    f.write(content)

print('Fixed scaling values')
