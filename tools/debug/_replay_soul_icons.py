r"""b40 dry-run replay: prove the granted-skill-icon fix against the LIVE baseline.

Loads baseline_build38.arz (the build38a DB shipped on Steam, which carries the
BUGGED nymph icons), then replays exactly what the fixed _build_boss_summon now
does - calls apply_svc_patches._set_summon_skill_icon() on every boss-summon
Skill_SpawnPet - and re-audits:

  1. BEFORE: every affected boss summon shows the Lyia nymph (summonlyiaup).
  2. AFTER : each summon shows its mapped/default icon (never the nymph).
  3. Soul re-scan: NO player-facing soul's granted Skill_SpawnPet shows the nymph
     except lyia_soul -> summon_lyia (correct; Lyia IS a nymph).
  4. Every AFTER icon (up + down) resolves in the shipped Resources .arc set.

Usage: py tools/debug/_replay_soul_icons.py <baseline.arz> <resources_dir>
"""
import sys
import os
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from arz_patcher import ArzDatabase
from arc_patcher import ArcArchive
import apply_svc_patches as M

NYMPH = r'drxtextures\skill icons\soul\summonlyiaup.tex'


def norm(p):
    return (p or '').replace('/', '\\').lower().strip()


def field0(fields, name):
    if not fields:
        return None
    for key, tf in fields.items():
        if key.split('###')[0] == name and tf.values and str(tf.values[0]).strip():
            return str(tf.values[0])
    return None


def main():
    arz_path, res_dir = sys.argv[1], sys.argv[2]
    db = ArzDatabase.from_arz(Path(arz_path))
    names = list(db.record_names())
    low = {norm(n): n for n in names}

    def resolve(ref):
        return low.get(norm(ref))

    # Arc resolution cache
    arc_cache = {}

    def icon_resolves(path):
        parts = norm(path).split('\\')
        archive, rest = parts[0], '/'.join(parts[1:])
        if archive not in arc_cache:
            p = Path(res_dir) / f'{archive}.arc'
            arc_cache[archive] = ({e.name.replace('\\', '/').lower()
                                   for e in ArcArchive.from_file(p).entries}
                                  if p.exists() else None)
        files = arc_cache[archive]
        return files is not None and rest in files

    # ---- Enumerate soul -> granted Skill_SpawnPet (player-facing) ----
    souls = [n for n in names
             if 'equipmentring\\soul' in norm(n) and norm(n).endswith('.dbr')]

    def granted_spawnpet(soul):
        isk = field0(db.get_fields(soul), 'itemSkillName')
        sk = resolve(isk) if isk else None
        if not sk:
            return None
        if field0(db.get_fields(sk), 'Class') != 'Skill_SpawnPet':
            return None
        return sk

    # affected = every distinct soul-granted SpawnPet currently showing the nymph,
    # EXCEPT summon_lyia (Lyia's own soul, correct). This is exactly the set the
    # fixed _build_boss_summon re-icons.
    affected = {}
    for soul in souls:
        sk = granted_spawnpet(soul)
        if not sk:
            continue
        up = field0(db.get_fields(sk), 'skillUpBitmapName')
        if norm(up) == NYMPH and 'summon_lyia' not in norm(sk):
            affected.setdefault(sk, up)

    # pet-of-pet summons the build also re-icons (not player-facing)
    petofpet = [r'records\skills\soulskills\svc_enslaver_petmarauders.dbr',
                r'records\skills\soulskills\summon_broodmother_wyrmlings.dbr']

    print(f"BASELINE: {arz_path}")
    print(f"Player-facing boss summons still on the NYMPH icon (pre-fix): "
          f"{len(affected)}")
    for sk in sorted(affected):
        print(f"    {sk.rsplit(chr(92),1)[-1]}")

    # ---- Replay the fix ----
    replayed = list(affected) + [resolve(p) for p in petofpet if resolve(p)]
    for sk in replayed:
        M._set_summon_skill_icon(db, sk)

    # ---- AFTER assertions ----
    failures = []
    print("\nAFTER (each summon -> new up icon; RESOLVE check):")
    for sk in sorted(replayed):
        base = M._summon_skill_basename(sk)
        exp_up, exp_down = M._SUMMON_SKILL_ICON.get(base, M._DEFAULT_SUMMON_ICON)
        got_up = field0(db.get_fields(sk), 'skillUpBitmapName')
        got_down = field0(db.get_fields(sk), 'skillDownBitmapName')
        tag = 'DEFAULT' if base not in M._SUMMON_SKILL_ICON else 'mapped'
        okup = icon_resolves(got_up)
        okdn = icon_resolves(got_down)
        if norm(got_up) != norm(exp_up) or norm(got_down) != norm(exp_down):
            failures.append(f"{base}: icon mismatch got={got_up}")
        if norm(got_up) == NYMPH:
            failures.append(f"{base}: STILL NYMPH")
        if not okup:
            failures.append(f"{base}: up icon does NOT resolve: {got_up}")
        if not okdn:
            failures.append(f"{base}: down icon does NOT resolve: {got_down}")
        print(f"    [{tag:7s}] {base:26s} -> {got_up.rsplit(chr(92),1)[-1]:22s} "
              f"up={'OK' if okup else 'FAIL'} down={'OK' if okdn else 'FAIL'}")

    # ---- Soul re-scan: no player-facing soul on the nymph except Lyia ----
    still_nymph = defaultdict(list)
    for soul in souls:
        sk = granted_spawnpet(soul)
        if not sk:
            continue
        up = field0(db.get_fields(sk), 'skillUpBitmapName')
        if norm(up) == NYMPH:
            still_nymph[norm(sk)].append(soul)

    print("\nSoul re-scan: player-facing souls STILL on the nymph after fix:")
    leftover = {sk: v for sk, v in still_nymph.items() if 'summon_lyia' not in sk}
    if not leftover:
        n_lyia = sum(len(v) for sk, v in still_nymph.items() if 'summon_lyia' in sk)
        print(f"    NONE (except {n_lyia} lyia_soul tiers -> summon_lyia, correct)")
    else:
        for sk, v in leftover.items():
            failures.append(f"leftover nymph: {sk} ({len(v)} souls)")
            print(f"    LEFTOVER {sk} <- {[s.rsplit(chr(92),1)[-1] for s in v]}")

    # Spot-check Will's example explicitly
    bt = resolve(r'records\skills\soulskills\summon_bloodtoxeus.dbr')
    if bt:
        print(f"\nWill's example  summon_bloodtoxeus (Summon Toxeus the Murderer):"
              f"\n    up   = {field0(db.get_fields(bt), 'skillUpBitmapName')}")

    print("\n" + ("REPLAY PASS - fix verified against the live baseline"
                  if not failures else "REPLAY FAIL:\n  " + "\n  ".join(failures)))
    sys.exit(0 if not failures else 1)


if __name__ == '__main__':
    main()
