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

# The shipped PC animation tables. B-SOUL-PROC-2 (build29): Game.dll
# SkillManager::StartSkill ABORTS a cast whose skillSpecialAnimationName the
# caster's animation table cannot start, so a soul-granted SUMMON skill whose
# special anim is not universally playable NEVER SPAWNS ITS PET (the summon
# half of "souls skills and summons are broken"). The chain check therefore
# starts at the GRANTING ITEM, not at the pet.
PC_ANM_TABLES = (
    'records\\creature\\pc\\anm\\anm_malepc01.dbr',
    'records\\creature\\pc\\anm\\anm_femalepc.dbr',
)


def _pc_universal_anims(db, modset):
    import re
    universal = None
    for tbl in PC_ANM_TABLES:
        rec = modset.get(_norm(tbl))
        if not rec:
            return None
        rows = {}
        for key, tf in (db.get_fields(rec) or {}).items():
            fname = key.split('###')[0]
            m = re.match(r'(.+?)SpecialAnimRef(\d+)$', fname)
            if m and tf.values and str(tf.values[0]).strip():
                rows.setdefault(m.group(1), set()).add(str(tf.values[0]).lower())
        for names in rows.values():
            universal = set(names) if universal is None else (universal & names)
    return universal or set()

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


# ── B-SUMMON-2 foreign-anim gate (invisible-body class) ──────────────────────
# The primary, continuously-played animation slots. A foreign-skeleton override
# on one of THESE (for a weapon class the pet actually equips) is what skins the
# body mesh to a bone hierarchy it lacks -> INVISIBLE body (bwpriest/lillued).
# Special/buff/die/stun slots are excluded: they fire rarely (or never, for an
# unused skill) so an inherited foreign override there is latent, not breaking
# (e.g. every working exemplar - boneash/rakanizeus/pharaohguard - carries a
# residual Maenad sHandedSpecialAnim1 yet renders fine).
_PRIMARY_ANIM_SUFFIXES = ('attackanim1', 'attackanim2', 'attackanim3',
                          'attackidleanim', 'walkanim', 'runanim')
_WEAPON_CLASS_PREFIXES = ('dhanded', 'shanded', 'spear', 'bow', 'staff',
                          'unarmed', 'thrown', 'shield')


def _anim_family(path):
    """Creature family token from a .anm / .msh / anm-table .dbr path, taken as
    the segment after 'monster' (case-insensitive). None if there is no
    'monster' segment (NPC / generic / effects anims - universal-skeleton, never
    treated as foreign). Examples: Creatures\\Monster\\JackalMan\\ANM\\x.anm ->
    'jackalman'; records\\creature\\monster\\djinn\\anm\\anm_djinn.dbr -> 'djinn';
    XPack\\Creatures\\Monster\\Melinoe\\ANM\\x.anm -> 'melinoe'."""
    parts = _norm(path).split('\\')
    for i, p in enumerate(parts):
        if p == 'monster' and i + 1 < len(parts):
            return parts[i + 1]
    return None


def _weapon_class(field_name):
    low = field_name.lower()
    for w in _WEAPON_CLASS_PREFIXES:
        if low.startswith(w):
            return w
    return None


def _is_primary_anim_field(field_name):
    w = _weapon_class(field_name)
    if not w:
        return False
    return field_name.lower()[len(w):] in _PRIMARY_ANIM_SUFFIXES


def _collect_mesh_anim_families(db, templates, out=None):
    """mesh(norm) -> set of creature families PROVEN to render on that mesh, from
    records of the given templates: the family of each record's
    charAnimationTableName plus the family of every per-record .anm override it
    carries. This is what permits a legitimate cross-family rig (e.g. the
    ElderDjinn body driven by Bat flying anims, or a Dragonian body driven by
    CrocMan anims): if a real Monster with that mesh uses the family, it renders.
    Mod-authored pets (the records under test) are intentionally NOT a source."""
    field = _mkfield(db)
    if out is None:
        out = {}
    for n in db.record_names():
        if templates is not None and db._record_types.get(n) not in templates:
            continue
        m = field(n, 'mesh')
        if not m or not str(m[0]).strip():
            continue
        mesh = _norm(m[0])
        fams = out.setdefault(mesh, set())
        a = field(n, 'charAnimationTableName')
        if a and str(a[0]).strip():
            fam = _anim_family(a[0])
            if fam:
                fams.add(fam)
        for key, tf in (db.get_fields(n) or {}).items():
            for v in (tf.values or []):
                if isinstance(v, str) and v.lower().endswith('.anm'):
                    fam = _anim_family(v)
                    if fam:
                        fams.add(fam)
                    break
    return out


def _reachable_weapon_classes(field):
    """Weapon-anim classes a pet can actually play, from its hand-equip chances.
    Conservative: a single equipped hand -> one-hand melee (sHanded); both hands
    -> dual-wield (dHanded) reachable too; unarmed is always reachable (a
    disarmed pet falls back to it)."""
    def _chance(name):
        v = field(name)
        try:
            return float(v[0]) if v else 0.0
        except (TypeError, ValueError):
            return 0.0
    lh = _chance('chanceToEquipLeftHand')
    rh = _chance('chanceToEquipRightHand')
    reach = {'unarmed'}
    if lh > 0 and rh > 0:
        reach.add('dhanded')
    if lh > 0 or rh > 0:
        reach.add('shanded')
    return reach


def validate(arz_path, base_path=None, upstream_path=None):
    db = ArzDatabase.from_arz(Path(arz_path))
    field = _mkfield(db)

    modset = {_norm(n): n for n in db.record_names()}
    baseset = set()
    upset = set()
    universal_anims = _pc_universal_anims(db, modset)
    proven_pairings = _collect_pairings(db, ('Monster',))
    # per-mesh proven animation families (B-SUMMON-2 gate): mod Monsters only
    # (mod-authored pets are the records UNDER TEST, never a proof source).
    mesh_families = _collect_mesh_anim_families(db, ('Monster',))

    base = None
    basemap = {}
    if base_path:
        base = ArzDatabase.from_arz(Path(base_path))
        basemap = {_norm(n): n for n in base.record_names()}
        baseset = set(basemap)
        proven_pairings |= _collect_pairings(base, ('Monster', 'Pet'))
        _collect_mesh_anim_families(base, ('Monster', 'Pet'), mesh_families)
    if upstream_path:
        up = ArzDatabase.from_arz(Path(upstream_path))
        upset = {_norm(n) for n in up.record_names()}
        # ANY upstream pairing is proven by SV play (Monster or Pet or other).
        proven_pairings |= _collect_pairings(up, ('Monster', 'Pet'))
        _collect_mesh_anim_families(up, ('Monster', 'Pet'), mesh_families)

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
        # b2. FOREIGN-ANIMATION gate (B-SUMMON-2, the invisible-body class):
        # a per-record .anm override whose creature family is not proven to
        # render on this pet's mesh, played on a PRIMARY slot of an EQUIPPED
        # weapon class, skins the body to a foreign skeleton -> INVISIBLE body
        # (Will's build28 blade-dancer + Lil'Lued). Legitimate cross-family rigs
        # (ElderDjinn+Bat, Dragonian+CrocMan) pass because a real same-mesh
        # Monster vouches the family; NPC/generic anims (no family) are skipped.
        proven_fams = set(mesh_families.get(_norm(mesh), set()))
        table_fam = _anim_family(anim_n) if anim_n else None
        if table_fam:
            proven_fams.add(table_fam)   # the mesh's OWN table family is proven
        reach = _reachable_weapon_classes(lambda nm: field(pet_rec, nm))
        for key, tf in (db.get_fields(pet_rec) or {}).items():
            fname = key.split('###')[0]
            wclass = _weapon_class(fname)
            if not wclass:
                continue
            val = tf.values[0] if tf.values else None
            if not isinstance(val, str) or not val.lower().endswith('.anm'):
                continue
            fam = _anim_family(val)
            if not fam or fam in proven_fams:
                continue  # unknown/NPC family, or a family proven on this mesh
            active = wclass in reach
            if not active:
                continue  # a weapon class the pet never equips can never play
                          # this anim -> not a render risk (pure latent noise).
            if _is_primary_anim_field(fname):
                problems.append((sev, chain,
                                 f"pet {pet_rec} plays a FOREIGN-skeleton "
                                 f"animation on its body mesh: <{fname}>={val} "
                                 f"(family '{fam}') is not proven on mesh {mesh} "
                                 f"and this weapon class is EQUIPPED -> INVISIBLE "
                                 f"body (B-SUMMON-2). Match the source monster's "
                                 f"anim set or drive from a same-family table."))
            else:
                # an equipped class, but a rarely-played slot (special/buff/die/
                # stun): inherited-foreign but not continuously on the body ->
                # latent, report-only (this is why boneash/rakanizeus render fine
                # despite a residual Maenad sHandedSpecialAnim1).
                problems.append(('WARN', chain,
                                 f"pet {pet_rec} carries a foreign-family "
                                 f"override <{fname}>={val} (family '{fam}') not "
                                 f"proven on mesh {mesh} (equipped class, rarely-"
                                 f"played slot; latent invisible-body risk)"))
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
        # g. classification (build29): every working exemplar pet (Lyia,
        # Boneash, base WraithLord) carries monsterClassification=Common; a
        # missing classification leaves the pet outside the engine's
        # class-driven handling.
        mc = field(pet_rec, 'monsterClassification')
        if not mc or not str(mc[0]).strip():
            problems.append((sev, chain,
                             f"pet {pet_rec} has EMPTY monsterClassification "
                             f"(working exemplars all carry 'Common')"))
        # h. LOCOMOTION (D19, the immobile-pet class; bone-level proof
        # 2026-07-09): a foreign-family per-record RunAnim override does NOT
        # play (CrocMan_Run binds 2/19 bone tracks on the dragonian/flameguard
        # skeleton); live monsters still move because their WEAPONED row falls
        # back to the TABLE clip. A pet whose PRIMARY row has no TABLE RunAnim
        # (and no same-family override) has NOTHING playable -> immobile statue
        # (Huo-ren/mountainblade: weaponless -> unarmed row; anm_dragonian has
        # no unarmedRunAnim; the CrocMan override is foreign). LAW: the primary
        # row's RunAnim must come from the TABLE or a table-family override.
        # Rigs whose table defines NO RunAnim on ANY row are stationary by
        # design (turret/vine class) and are exempt.
        if anim_n:
            _tname = None
            _tdb = None
            if anim_n in modset:
                _tdb, _tname = db, modset[anim_n]
            elif base is not None and anim_n in basemap:
                _tdb, _tname = base, basemap[anim_n]
            if _tname:
                _tf = _tdb.get_fields(_tname) or {}
                _tbl_fields = {}
                for _k, _v in _tf.items():
                    _bk = _k.split('###')[0]
                    if _bk.endswith('RunAnim') and _v.values \
                            and str(_v.values[0]).strip():
                        _tbl_fields[_bk.lower()] = str(_v.values[0])
                # primary row: RightHand is always a weapon; LeftHand is a
                # weapon only when its loot tables are not shield tables
                # (weapon+shield -> sHanded; two weapons -> dHanded).
                def _hand(nm):
                    v = field(pet_rec, f'chanceToEquip{nm}')
                    try:
                        return bool(v) and float(v[0]) > 0
                    except (TypeError, ValueError):
                        return False

                def _lh_is_shield():
                    # only sub-slots the engine can SELECT (weight > 0) count;
                    # Lyia-clone residue rides in zero-weight ItemN slots.
                    for _i in range(1, 7):
                        _w = field(pet_rec, f'chanceToEquipLeftHandItem{_i}')
                        try:
                            if not _w or int(float(_w[0])) <= 0:
                                continue
                        except (TypeError, ValueError):
                            continue
                        _it = field(pet_rec, f'lootLeftHandItem{_i}')
                        for _p in (_it or []):
                            if isinstance(_p, str) and _p.strip() \
                                    and 'shield' not in _p.lower():
                                return False
                    return True
                rh_w = _hand('RightHand')
                lh_w = _hand('LeftHand') and not _lh_is_shield()
                if rh_w and lh_w:
                    prim = 'dhanded'
                elif rh_w or lh_w:
                    prim = 'shanded'
                else:
                    prim = 'unarmed'
                prim_field = {'dhanded': 'dHandedRunAnim',
                              'shanded': 'sHandedRunAnim',
                              'unarmed': 'unarmedRunAnim'}[prim]
                if _tbl_fields and prim_field.lower() not in _tbl_fields:
                    # table locomotion missing for the primary row; a pet-record
                    # override only counts if it is the table's OWN family
                    ov = field(pet_rec, prim_field)
                    ov_fam = _anim_family(ov[0]) if ov and str(ov[0]).strip() \
                        else None
                    if not (ov_fam and table_fam and ov_fam == table_fam):
                        problems.append((sev, chain,
                                         f"pet {pet_rec} IMMOBILE (D19): primary "
                                         f"anim row '{prim}' has no TABLE RunAnim "
                                         f"in {anim} and its override "
                                         f"{ov[0] if ov else '(none)'} is not the "
                                         f"table's own family "
                                         f"('{ov_fam}' vs '{table_fam}') -> no "
                                         f"playable locomotion. Equip the source "
                                         f"monster's weapon (table-covered row) "
                                         f"or use a table with {prim_field}."))
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
        # CASTABILITY of the summon skill itself (build29, B-SOUL-PROC-2): a
        # special anim the PC cannot universally play means StartSkill aborts
        # and the pet NEVER spawns, regardless of how complete the pet is.
        if universal_anims is not None:
            anim = field(skill, 'skillSpecialAnimationName')
            if anim and str(anim[0]).strip() and \
                    str(anim[0]).lower() not in universal_anims:
                problems.append((sev, chain,
                                 f"summon skill carries special anim "
                                 f"'{anim[0]}' NOT universally playable by the "
                                 f"PC (cast aborts, pet never spawns)"))
        spawn = field(skill, 'spawnObjects')
        if not spawn or not any(str(s).strip() for s in spawn):
            problems.append((sev, chain, "summon skill has EMPTY spawnObjects "
                                         "(summons nothing)"))
            continue
        # level-vs-array sanity (WARN only; the engine clamps to the last
        # array entry, but a granted level far past the authored spawnObjects
        # ladder is a design smell worth surfacing).
        lvl = field(name, 'itemSkillLevel')
        n_spawn = len([s for s in spawn if str(s).strip()])
        if lvl and int(lvl[0]) > n_spawn:
            problems.append(('WARN', chain,
                             f"granted itemSkillLevel {int(lvl[0])} exceeds "
                             f"spawnObjects ladder length {n_spawn} (engine "
                             f"clamps to the last pet entry)"))
        # ── build30/F1 gate (vet-proven miss): a summon-soul's granted level must
        # not exceed the summon skill's own skillMaxLevel - the engine clamps the
        # granted level to skillMaxLevel BEFORE the spawnObjects lookup, so
        # levels 4/6/8 on a max-3 skill collapse every difficulty tier onto the
        # SAME pet (the D8 xeiwang bug: Table-B PROC_LV stomped the 1/2/3 tier
        # wiring). Mod-authored chains FAIL the build; upstream-proven WARN. ──
        mx = field(skill, 'skillMaxLevel')
        if lvl and mx and int(lvl[0]) > int(mx[0]):
            problems.append((sev, chain,
                             f"granted itemSkillLevel {int(lvl[0])} EXCEEDS the "
                             f"summon skill's skillMaxLevel {int(mx[0])} (engine "
                             f"clamps - every tier grants the same pet; tier "
                             f"wiring must be 1..{int(mx[0])})"))
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
