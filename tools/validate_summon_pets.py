r"""Build-time validator: every soul-granted SUMMON must spawn a complete,
renderable, usable pet (the B-SUMMON-1 gate).

Root problem this guards against: soul summon skills point at pet records that
were authored by cloning + field surgery. Silent failure classes shipped
(Will's 2026-07-08 live session): a NAKED pet (equipment slots pointed at
player-tier Epic/Legendary uniques, which a DB-wide audit proved NEVER
auto-equip on a monster/pet: of ~25,000 working monster/pet equip slots, zero
reference a player Epic/Legendary unique - every working slot uses a dynamic
LOOT TABLE or a monster/low-tier item), a FLOATING-WEAPON / immobile pet (mesh
and charAnimationTable not a rig-compatible pairing), and an INERT pet
(dangling skill / controller / equipment refs). None of these crash; they just
ship broken summons.

Strict-vs-proven scoping (what keeps this gate false-positive-free):
  - A pet that already exists in the SV 0.98i UPSTREAM database is
    UPSTREAM-PROVEN (years of SV play). Its findings are reported as WARN
    only (upstream ships deliberate 'x' / drxplaceholder / xxx-prefixed
    disable markers that the engine skips gracefully).
  - A pet NOT in the upstream (i.e. authored by THIS build) is held to the
    full strict contract and FAILS the build on any violation.
  - Reference resolution matches the runtime: mod .arz UNION base-game .arz
    (the engine overlays the mod on the base database).

The strict per-pet contract:
  a. mesh non-empty;
  b. RIG PAIRING: (mesh, charAnimationTableName) is used by at least one
     Monster-template record (mod or base) or by any upstream/base pet - a
     proven-rendering pairing (catches the floating/immobile class);
  c. charAnimationTableName, if non-empty, resolves;
  d. EQUIPMENT: every loot path on an enabled (chanceToEquip > 0) slot
     resolves (mod-or-base), and no DIRECT (non-loot-table) item is a
     player-tier Epic/Legendary unique (never auto-equips -> naked pet);
  e. controller non-empty and resolves;
  f. every skillName* / specialAttack*SkillName / initialSkillName /
     attackSkillName reference resolves.
Plus per-chain: the summon skill's spawnObjects is non-empty and every entry
resolves.

Usage:
  py tools/validate_summon_pets.py <final.arz> [<base_game.arz>] [<upstream_sv098i.arz>]

(The build + bootstrap gates pass all three; a bare single-arg run still
works but without base-resolution or upstream leniency, so expect noise.)

Exit codes:
  0 = every strict (mod-authored) soul-granted summon chain is complete
  1 = one or more strict chains broken (details printed)
  2 = usage / input error
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

SOUL_MARKERS = ('\\soul\\', '/soul/')
SPAWN_CLASSES = ('Skill_SpawnPet', 'Skill_AttackProjectileSpawnPet')

EQUIP_SLOTS = ('LeftHand', 'RightHand', 'Forearm', 'Finger1', 'Finger2',
               'Head', 'Torso', 'LowerBody', 'Misc1', 'Misc2', 'Misc3')

SKILL_REF_FIELDS_EXACT = ('initialSkillName', 'attackSkillName')


def _norm(path):
    return str(path).replace('/', '\\').lower().strip()


def _mkfield(db):
    def field(rec, name):
        ff = db.get_fields(rec)
        if not ff:
            return None
        for key, tf in ff.items():
            if key.split('###')[0] == name and tf.values:
                return tf.values
        return None
    return field


def _collect_pairings(db, templates=('Monster',)):
    """(mesh, anim) pairings used by records of the given templates in db."""
    field = _mkfield(db)
    pairs = set()
    for n in db.record_names():
        if templates is not None and db._record_types.get(n) not in templates:
            continue
        m = field(n, 'mesh')
        if not m or not str(m[0]).strip():
            continue
        a = field(n, 'charAnimationTableName')
        a_n = _norm(a[0]) if a and str(a[0]).strip() else ''
        pairs.add((_norm(m[0]), a_n))
    return pairs


def validate(arz_path, base_path=None, upstream_path=None):
    db = ArzDatabase.from_arz(Path(arz_path))
    field = _mkfield(db)

    modset = {_norm(n): n for n in db.record_names()}
    baseset = set()
    upset = set()
    proven_pairings = _collect_pairings(db, ('Monster',))

    if base_path:
        base = ArzDatabase.from_arz(Path(base_path))
        baseset = {_norm(n) for n in base.record_names()}
        proven_pairings |= _collect_pairings(base, ('Monster', 'Pet'))
    if upstream_path:
        up = ArzDatabase.from_arz(Path(upstream_path))
        upset = {_norm(n) for n in up.record_names()}
        # ANY upstream pairing is proven by SV play (Monster or Pet or other).
        proven_pairings |= _collect_pairings(up, ('Monster', 'Pet'))

    def resolve(path):
        n = _norm(path)
        if n in modset:
            return modset[n]
        if n in baseset:
            return f'<base>{n}'
        return None

    def resolve_mod(path):
        return modset.get(_norm(path))

    problems = []   # (severity, chain, reason); severity in ('FAIL', 'WARN')
    chains = 0
    pets_checked = set()

    def check_pet(chain, pet_rec):
        if pet_rec in pets_checked:
            return
        pets_checked.add(pet_rec)
        # upstream-proven pets -> findings become warnings, never failures
        sev = 'WARN' if _norm(pet_rec) in upset else 'FAIL'
        # a. mesh
        mesh = field(pet_rec, 'mesh')
        mesh = mesh[0] if mesh else None
        if not mesh or not str(mesh).strip():
            problems.append((sev, chain, f"pet {pet_rec} has EMPTY mesh (invisible)"))
            return
        # b. rig pairing
        anim = field(pet_rec, 'charAnimationTableName')
        anim = anim[0] if anim else None
        anim_n = _norm(anim) if anim and str(anim).strip() else ''
        if (_norm(mesh), anim_n) not in proven_pairings:
            problems.append((sev, chain,
                             f"pet {pet_rec} rig pairing NOT proven: mesh={mesh} + "
                             f"anim={anim or '(empty)'} matches no proven-rendering "
                             f"record (floating/immobile risk)"))
        # c. anim resolves
        if anim_n and not resolve(anim_n):
            problems.append((sev, chain, f"pet {pet_rec} charAnimationTableName "
                                         f"does not resolve: {anim}"))
        # d. equipment
        for slot in EQUIP_SLOTS:
            ch = field(pet_rec, f'chanceToEquip{slot}')
            if not ch or float(ch[0]) <= 0:
                continue
            for idx in range(1, 7):
                w = field(pet_rec, f'chanceToEquip{slot}Item{idx}')
                if not w or int(float(w[0])) <= 0:
                    continue  # zero-weight sub-slot never selected
                items = field(pet_rec, f'loot{slot}Item{idx}')
                if not items:
                    continue
                for ip in items:
                    if not isinstance(ip, str) or not ip.strip():
                        continue
                    target = resolve(ip)
                    if not target:
                        problems.append((sev, chain,
                                         f"pet {pet_rec} equip {slot} item does "
                                         f"not resolve (mod or base): {ip}"))
                        continue
                    ipl = _norm(ip)
                    if '\\loottables\\' in ipl:
                        continue  # dynamic loot table = the proven path
                    mod_target = resolve_mod(ip)
                    if mod_target:
                        cls = field(mod_target, 'itemClassification')
                        if cls and str(cls[0]) in ('Epic', 'Legendary'):
                            problems.append((sev, chain,
                                             f"pet {pet_rec} equips DIRECT "
                                             f"player-tier {cls[0]} unique in "
                                             f"{slot}: {ip} (never auto-equips -> "
                                             f"NAKED pet; use the source monster's "
                                             f"loot tables)"))
        # e. controller
        ctl = field(pet_rec, 'controller')
        ctl = ctl[0] if ctl else None
        if not ctl or not str(ctl).strip():
            problems.append((sev, chain, f"pet {pet_rec} has EMPTY controller (inert AI)"))
        elif not resolve(ctl):
            problems.append((sev, chain, f"pet {pet_rec} controller does not "
                                         f"resolve (mod or base): {ctl}"))
        # f. skill refs
        ff = db.get_fields(pet_rec) or {}
        for key, tf in ff.items():
            fname = key.split('###')[0]
            is_skill_ref = (fname in SKILL_REF_FIELDS_EXACT or
                            fname.startswith('skillName') or
                            (fname.startswith('specialAttack') and
                             fname.endswith('SkillName')))
            if not is_skill_ref or not tf.values:
                continue
            for v in tf.values:
                if not isinstance(v, str) or not v.strip():
                    continue
                if not v.lower().endswith('.dbr'):
                    continue  # non-path junk ('x', xxx-disables without .dbr)
                if not resolve(v):
                    problems.append((sev, chain,
                                     f"pet {pet_rec} skill ref <{fname}> does "
                                     f"not resolve (mod or base): {v}"))

    for name in db.record_names():
        low = name.lower()
        if not any(m in low for m in SOUL_MARKERS):
            continue
        if db._record_types.get(name) == 'Monster':
            continue  # monster records parked under soul\test\
        isn = field(name, 'itemSkillName')
        isn = isn[0] if isn else None
        if not isn or not str(isn).strip():
            continue
        skill = resolve_mod(isn)
        if not skill:
            continue  # dangling refs are validate_soul_augments' job
        cls = field(skill, 'Class')
        if not cls or str(cls[0]) not in SPAWN_CLASSES:
            continue
        chains += 1
        chain = f"{name} -> {skill}"
        sev = 'WARN' if _norm(skill) in upset else 'FAIL'
        spawn = field(skill, 'spawnObjects')
        if not spawn or not any(str(s).strip() for s in spawn):
            problems.append((sev, chain, "summon skill has EMPTY spawnObjects "
                                         "(summons nothing)"))
            continue
        for pet_path in spawn:
            if not str(pet_path).strip():
                continue
            pet = resolve_mod(pet_path)
            if not pet:
                problems.append((sev, chain, f"spawnObjects entry does not "
                                             f"resolve in the mod .arz: {pet_path}"))
                continue
            check_pet(chain, pet)

    fails = [(c, r) for s, c, r in problems if s == 'FAIL']
    warns = [(c, r) for s, c, r in problems if s == 'WARN']

    print("=" * 72)
    print("SUMMON PET VALIDATOR (B-SUMMON-1 gate)")
    print(f"  .arz                : {arz_path}")
    print(f"  base .arz           : {base_path or '(none - reduced fidelity)'}")
    print(f"  upstream .arz       : {upstream_path or '(none - no leniency)'}")
    print(f"  soul summon chains  : {chains}")
    print(f"  pet records checked : {len(pets_checked)}")
    print(f"  STRICT failures     : {len(fails)}")
    print(f"  upstream warnings   : {len(warns)}")
    print("=" * 72)

    if warns:
        print("\nWARN (upstream-proven pets; SV shipped these, engine skips "
              "gracefully - not build-blocking):\n")
        for chain, reason in warns:
            print(f"[WARN] {chain}")
            print(f"    {reason}\n")

    if fails:
        print("\nFAIL - broken MOD-AUTHORED soul-granted summon chain(s):\n")
        for chain, reason in fails:
            print(f"[BROKEN] {chain}")
            print(f"    {reason}\n")
        return 1

    print("\nPASS - every mod-authored soul-granted summon spawns a complete, "
          "renderable, usable pet.")
    return 0


def main(argv):
    if len(argv) < 2 or len(argv) > 4:
        print(__doc__)
        print("ERROR: expected 1-3 arguments (final .arz [base .arz] [upstream .arz]).")
        return 2
    arz = Path(argv[1])
    if not arz.is_file():
        print(f"ERROR: .arz not found: {arz}")
        return 2
    base = argv[2] if len(argv) > 2 and str(argv[2]).strip() else None
    upstream = argv[3] if len(argv) > 3 and str(argv[3]).strip() else None
    for p in (base, upstream):
        if p and not Path(p).is_file():
            print(f"ERROR: .arz not found: {p}")
            return 2
    return validate(arz, base, upstream)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
