"""G1 mapping + anim-token + collision probe (LANE B, read-only).

Pins the ground truth the graft code depends on:
  1. PC malepc01 skillTree1..12 order (which tree = which mastery slot).
  2. UI folder identity: for ingameui 'player skills\\mastery N' (1..9) and
     xpack 'ui\\skills\\mastery N', the skillName of slot02/03 (identifies the
     mastery a folder drives) + the highest occupied slot + a few free cells.
  3. dreamcopypet skillName*/skillLevel* (difficulty-scaling remap target).
  4. Anim-token presence for the non-empty-cast grafts (ShieldSkill02,
     CallOfTheHunt, Colossus, ThunderClap, Hew) per weapon row in our PC tables.
  5. Collision check: does our arz already contain any graft target record?

Usage: py tools/debug/g1_mapping_probe.py [our_arz]
"""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase

OUR = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:/Users/willi/repos/tqit_soulvizier_classic/work/SoulvizierClassic/Database/SoulvizierClassic.arz"


def norm(s):
    return s.replace('/', '\\').lower().strip()


def gv(db, name, f):
    v = db.get_field_value(name, f)
    return (v[0] if isinstance(v, list) and v else v)


def main():
    our = ArzDatabase.from_arz(Path(OUR))
    m = {norm(n): n for n in our.record_names()}

    print("\n== 1. PC malepc01 skillTree1..12 ==")
    pc = m.get(norm(r'records\xpack\creatures\pc\malepc01.dbr'))
    for i in range(1, 13):
        print(f"  skillTree{i} = {gv(our, pc, f'skillTree{i}')}")

    print("\n== 2. UI folder identity (ingameui player skills\\mastery N) ==")
    for mi in range(1, 10):
        base = r'records\ingameui\player skills\mastery %d' % mi
        ident = None
        for slot in (2, 3, 4):
            n = m.get(norm(r'%s\skill%02d.dbr' % (base, slot)))
            if n:
                ident = gv(our, n, 'skillName')
                break
        occupied = [si for si in range(1, 40)
                    if norm(r'%s\skill%02d.dbr' % (base, si)) in m]
        hi = max(occupied) if occupied else 0
        print(f"  ingameui M{mi}: ident(slot)= {ident} | highest slot={hi} "
              f"| count={len(occupied)}")

    print("\n== 2b. xpack UI folder identity (records\\xpack\\ui\\skills\\mastery N) ==")
    for mi in range(1, 13):
        base = r'records\xpack\ui\skills\mastery %d' % mi
        ident = None
        for slot in (2, 3, 4):
            n = m.get(norm(r'%s\skill%02d.dbr' % (base, slot)))
            if n:
                ident = gv(our, n, 'skillName')
                break
        occupied = [si for si in range(1, 40)
                    if norm(r'%s\skill%02d.dbr' % (base, si)) in m]
        if occupied:
            hi = max(occupied)
            print(f"  xpackui M{mi}: ident= {ident} | highest slot={hi} "
                  f"| count={len(occupied)}")

    print("\n== 3. dreamcopypet skillName*/skillLevel* (SVAERA import target's scaling) ==")
    # Our db does NOT have it yet; show what our nightmare pet uses for scaling.
    for probe in (r'records\xpack\skills\dream\pet\nightmare_10.dbr',):
        n = m.get(norm(probe))
        if n:
            print(f"  [our nightmare_10 scaling refs]")
            for k, tf in our.get_fields(n).items():
                bk = k.split('###')[0]
                if bk.startswith('skillName') or bk.startswith('skillLevel'):
                    print(f"     {bk} = {tf.values}")
    # our base difficulty-scaling record present?
    for k in m:
        if 'pet_difficultydamagescaling' in k:
            print(f"  our has scaling record: {m[k]}")

    print("\n== 4. Anim-token presence in our PC tables (per weapon row) ==")
    TOKENS = {'shieldskill02', 'callofthehunt', 'colossus', 'thunderclap', 'hew'}
    for tbl in (r'records\creature\pc\anm\anm_malepc01.dbr',
                r'records\creature\pc\anm\anm_femalepc.dbr'):
        n = m.get(norm(tbl))
        if not n:
            print(f"  [MISSING] {tbl}")
            continue
        rows_by_tok = {t: [] for t in TOKENS}
        for k, tf in our.get_fields(n).items():
            fname = k.split('###')[0]
            mm = re.match(r'(.+?)SpecialAnimRef(\d+)$', fname)
            if mm and tf.values:
                tok = str(tf.values[0]).strip().lower()
                if tok in rows_by_tok:
                    rows_by_tok[tok].append(mm.group(1))
        print(f"  {tbl.rsplit(chr(92),1)[-1]}:")
        for t in sorted(TOKENS):
            rows = sorted(set(rows_by_tok[t]))
            print(f"     {t}: {len(rows)} rows -> {rows}")

    print("\n== 5. Collision check (graft targets must NOT already exist) ==")
    TARGETS = [
        r'records\skills\warfare\drx_clubslam.dbr',
        r'records\skills\warfare\drx_clubslam_fissure.dbr',
        r'records\skills\warfare\drx_ancestralmod.dbr',
        r'records\skills\defensive\drx_activeblock.dbr',
        r'records\skills\defensive\drx_summonphalanx.dbr',
        r'records\skills\earth\drx_firenova.dbr',
        r'records\skills\earth\drxrupture.dbr',
        r'records\skills\earth\drxrupture_burning.dbr',
        r'records\skills\earth\drxrupture_flare.dbr',
        r'records\skills\storm\drx_lightningdash.dbr',
        r'records\skills\storm\drxfrostnova.dbr',
        r'records\skills\nature\drx_earthbind.dbr',
        r'records\skills\nature\drx_nymph_petmodifier_rootwave.dbr',
        r'records\skills\nature\drx_nymph_petskill_rootwave.dbr',
        r'records\xpack\skills\dream\drx_summoncopy.dbr',
        r'records\effects\_drx_effects\storm\storm_frostnova_fx.dbr',
        r'records\effects\_drx_effects\storm\storm_frostnova_fxpak.dbr',
        r'records\xpack\skills\dream\pet\dreamcopypet.dbr',
        r'records\xpack\skills\dream\pet\dreamcopypet_petskill_aura.dbr',
        r'records\xpack\skills\dream\pet\anm\anm_dreamcopy.dbr',
        r'records\skills\boss skills\hero_conversionimmunity_pets.dbr',
    ]
    for t in TARGETS:
        print(f"  {'EXISTS' if norm(t) in m else 'absent'}: {t}")


if __name__ == '__main__':
    main()
