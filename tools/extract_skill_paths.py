"""Extract full record paths for all skills used by existing SV souls.
This gives us the exact paths to use in our soul designs.
"""
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    augments = {}
    granted = {}
    controllers = {}

    for name in db.record_names():
        nl = name.lower()
        if ('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl:
            if '\\test\\' in nl:
                continue
            fields = db.get_fields(name)
            if not fields:
                continue
            for key, tf in fields.items():
                rk = key.split('###')[0]
                if rk in ('augmentSkillName1', 'augmentSkillName2') and tf.values:
                    for v in tf.values:
                        if isinstance(v, str) and v:
                            short = v.replace('\\', '/').split('/')[-1].replace('.dbr', '')
                            augments[short] = v
                if rk == 'itemSkillName' and tf.values:
                    for v in tf.values:
                        if isinstance(v, str) and v:
                            short = v.replace('\\', '/').split('/')[-1].replace('.dbr', '')
                            granted[short] = v
                if rk == 'itemSkillAutoController' and tf.values:
                    for v in tf.values:
                        if isinstance(v, str) and v:
                            short = v.replace('\\', '/').split('/')[-1].replace('.dbr', '')
                            controllers[short] = v

    print("# Augment skill paths (augmentSkillName1/2)")
    print("AUGMENT_SKILLS = {")
    for short in sorted(augments):
        print(f"    '{short}': '{augments[short]}',")
    print("}")

    print("\n# Granted skill paths (itemSkillName)")
    print("GRANTED_SKILLS = {")
    for short in sorted(granted):
        print(f"    '{short}': '{granted[short]}',")
    print("}")

    print("\n# Auto-cast controller paths (itemSkillAutoController)")
    print("CONTROLLERS = {")
    for short in sorted(controllers):
        print(f"    '{short}': '{controllers[short]}',")
    print("}")


if __name__ == '__main__':
    main()
