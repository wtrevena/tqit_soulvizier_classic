r"""uber_quest_markers - R-39's SIXTH sub-item: "the exclamation-marker mechanism
extended to all placed ubers".

WILL'S RULING (docs/WILL_RULINGS.md R-39, 2026-07-16), the clause this module owns:
    "... the exclamation-marker mechanism extended to all placed ubers ..."

Ships with the rest of the Cold Worm lane (R-39 ruled: ONE lane, not piecemeal).


================================================================================
1. WHAT THE "EXCLAMATION-MARKER MECHANISM" ACTUALLY IS
================================================================================
It is a DB-side Monster field: `DisplayAsQuestItem`.

b91 round 1 recorded this sub-item as BLOCKED on the premise that "the marker is
not a DB-side monster property ... so placing a marker means editing level blobs
in Levels.arc". **That premise is WRONG and is corrected here.** Ground truth,
measured over the shipped arz (`local/baseline_build47.arz`, 51,085 records):

    DisplayAsQuestItem value distribution : {0: 23100, 1: 145}
    non-zero carriers by Class            : Monster 124, Pet 4,
                                            FixedItemContainer 4,
                                            FixedItemQuestObject 3, Megalesios 3,
                                            Decoration 3, FixedItemDoor 2,
                                            Guard 1, Npc 1
    present on Monster records            : 4601 / 4601 (absent on 0)

So it is a universal Monster.tpl field, and 124 Monster records already ship with
it set. The carrier set is unambiguous about what it means - it is the "show this
entity as a quest objective" flag:

  * every base-game quest boss (Medusa/Sstheno/Euryale, Arachne, Minotaur Lord,
    Alastor, the Spartan centaur, Megalesios, the Cyclops brothers, Kondor)
  * every xsq named quest hero (Forest Lord, Lich Queen, Machae envoys, Empusae)
  * the escort/rescue NPCs (`xsq09_trappednpc_a..k`, `xsq03_escortworker`)
  * quest OBJECTS, DOORS and CHESTS (`xsq06_keyslotfordoor_*`,
    `xsq06_leverdoor{a,b}`, `xsq05_mushroomchest`, `jo10 - jade figurine chest`)
  * and the POI records under `records\poi\**` (Class `AreaOfInterest`), which is
    the base game's own map-marker namespace and carries the same field.

**It is already LIVE in this mod on the very boss the ruling is about.**
`records\test\boss_coldworm50.dbr` (Cold Worm) has `DisplayAsQuestItem = 1` on
`main`, unchanged by b91. That is the marker Will saw and asked us to extend - the
mechanism was never missing, it was simply never applied to the rest of the roster.

Consequence: this sub-item is DB-side, needs NO `Levels.arc` build, and is NOT
blocked by `SVC_SVAERA_ARC` / `SVC_SV_ARC` (BL-b89-DEBT-4 / BL-b90-DEBT-2).
No map bytes are touched by this module.


================================================================================
2. WHAT "ALL PLACED UBERS" MEANS - ROSTER-DERIVED, ZERO HARDCODED NAMES
================================================================================
"Placed uber" already has ONE canonical, mechanical definition in this repo, and
this module reuses it rather than inventing a second one. It is
`build_svc_database.soul_spawn_provenance_sets(db)` -> `placed_members`: monsters
referenced by a mod PLACEMENT record under `records\drxmap\proxy*` (the
`q_*_lone` / warband / `svc_*_pool` proxies). That is the same source of truth
that drives the PLACED_UBER 66% soul-release rate (R-42), so the marker roster
and the drop-rate roster can never silently disagree.

Two mechanical rules narrow that set to the ENCOUNTERS (rule A) and then widen it
back across transform chains (rule B):

  RULE A - SOUL-PAYING CHAIN.
    A placed record qualifies only if IT, or some form in its
    `actorToSpawnOnDeath` chain, actually pays out a soul
    (`chanceToEquipFinger2 > 0`). This is the same chain test
    `tools/sweep_soul_drop_slots.py` already uses.
    WHY: the placement proxies also carry the boss's RETINUE - the Four Generals'
    six `svc_general_*_guard{1,2}`, `svc_vashkarr_{lance,warlock}`,
    `svc_dorus_royalguard_71`, `svc_diadochi_striderguard_97`, the obsidian-
    roulette escorts. Those are adds, not ubers; a marker on each of them would be
    map spam. None of them drops a soul, so the rule excludes them mechanically -
    no hand-maintained name list to rot.

  RULE B - MARK EVERY *DEDICATED* FORM OF THE CHAIN.
    Once an encounter qualifies, the forms in its `actorToSpawnOnDeath` chain are
    marked too, so the marker survives the transform (Tantalus -> Tantalus
    Unbound, Charon -> Charon Form2, Polis Gaoler -> Polis Gaoler Unbound,
    Mnemophage -> Mnemophage Core).
    BUT a form is only marked when EVERY record that spawns it is itself in the
    roster - i.e. the form is exclusive to placed ubers. Expanded to a fixpoint.
    WHY THE EXCLUSIVITY TEST: `records\creature\monster\ghost\as_ghosthero_32.dbr`
    is Neferkha's terminal form AND the terminal form of five ROAMING mummy heroes
    (`um_tath_27`, `um_khenti_31`, `um_nebtaan_32`, `um_radementes_31`,
    `us_menkare_33`). A naive "mark the whole chain" would put a quest marker on
    every ghost those five leave behind, anywhere on the map - exactly the map
    spam this sub-item must not create. Shared forms are reported and left alone;
    the marker stops at the uber itself.

DERIVATION PROOF (this is why the two rules are not invented):
    Exactly ONE placed uber already carried the marker on `main`:
    `um_polisgaoler_99` (chance 0) -> `um_polisgaoler_unbound_99` (chance 66).
    **BOTH forms carry `DisplayAsQuestItem = 1` in shipped content.** The shipped
    precedent is therefore literally rule A + rule B applied to that one boss;
    this module applies the same rule to the rest of the roster instead of
    stopping at one. Nothing about the shape of the change is new.

Also excluded, mechanically:
  * non-Monster classes (a placement proxy's `*.msh` mesh strings land in
    `placed_members` as basename noise - 8 of them; they resolve to no Monster
    record and are dropped);
  * anything not classified Hero / Boss / Quest (asserted, never silently
    skipped: a placed soul-paying encounter outside those ranks would be a
    roster defect and fails the module loud).


================================================================================
3. THE GATE (a new content class ships its gate)
================================================================================
The new invariant this lane introduces:

    EVERY placed-uber encounter record, and every form of its transform chain,
    must carry DisplayAsQuestItem = 1.

`verify()` runs in registry step 4 over the FINAL merged db (after the entire
gate battery) and fails the BUILD loud on any roster member sitting at 0. It also
re-asserts the pre-existing carriers this lane relies on (Cold Worm and both
Polis Gaoler forms), so a later writer cannot silently regress the mechanism the
ruling is built on.

Planted negative test proves the gate is not vacuous:
    py tools/patches/uber_quest_markers.py --negtest
It plants (1) a roster member reset to 0 - must be flagged; (2) a retinue add
(no soul in its chain) - must NOT be in the roster, i.e. the roster is not
"everything the proxies reference"; (3) an untouched control - must be clean.

Read-only analysis of any arz:
    py tools/patches/uber_quest_markers.py --analyze <arz>


================================================================================
4. SCOPE
================================================================================
ONE field (`DisplayAsQuestItem`) on Monster records that are already in the
placed-uber roster. No new records, no tags, no Text.arc surface, no skills, no
loot, no drop rates, no pools, no proxies, no map. apply() proves the scope
mechanically: it snapshots `DisplayAsQuestItem` across EVERY record before and
after its own writes and fails loud if the changed set is anything other than the
roster it computed.

dtype: the field already exists on every Monster record, so `set_field` is called
WITHOUT an explicit dtype (CLAUDE.md's dtype-preservation law); the value written
mirrors the field's own dtype (INT -> 1, FLOAT -> 1.0) so the re-encode is
type-exact.

ORDERING: registered immediately after `coldworm_buffs` (same ruling, same lane)
and immediately before `visuals` (which writes nothing). It is therefore the
ratified final registry writer of this field. It reads `chanceToEquipFinger2`,
which `toxeus_souls_100` (R-48) writes earlier in the registry - running after it
means the roster is computed against the final rates, and both Toxeus champions
(100%) qualify under rule A either way.

NOT PROVEN IN-GAME BY THIS MODULE. The field's rendering is engine-side; it is
proven live by 124 base-game carriers plus Cold Worm and Polis Gaoler in this very
mod, but Will's fresh-character DEV verify is still the launch gate for the lane
(BL-b91-DEBT-4). See docs/reports/b91_coldworm_buffs.md sec 7.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import build_svc_database as bsd
from arz_patcher import DATA_TYPE_INT

MODULE_NAME = "placed-uber quest markers (R-39, 6th sub-item)"

FIELD = 'DisplayAsQuestItem'
CHANCE = 'chanceToEquipFinger2'
CHAIN = 'actorToSpawnOnDeath'

# Ranks a placed, soul-paying encounter is allowed to hold. Anything outside this
# set that still satisfies rule A is a roster defect and fails the module loud
# rather than being silently skipped.
ENCOUNTER_RANKS = {'hero', 'boss', 'quest'}

# Monster-family Classes that can carry the marker. 'Megalesios' is the base
# game's own bespoke boss Class (3 records, all already marked) and is included
# so a placed record on that Class could never be silently dropped.
MONSTER_CLASSES = {'monster', 'megalesios'}

# Pre-existing carriers this lane's premise rests on. verify() re-asserts them so
# a later writer cannot regress the mechanism out from under R-39.
PREEXISTING_ANCHORS = (
    (r'records\test\boss_coldworm50.dbr',
     'Cold Worm - the marker Will saw; R-39 asks to EXTEND this'),
    (r'records\xpack\creatures\monster\gigantes\um_polisgaoler_99.dbr',
     'Polis Gaoler form 1 - the shipped rule-A+B precedent'),
    (r'records\xpack\creatures\monster\gigantes\um_polisgaoler_unbound_99.dbr',
     'Polis Gaoler terminal form - the shipped rule-B precedent'),
)


# ── small readers ───────────────────────────────────────────────────────────
def _scalar(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _val(db, rec, field, default=None):
    try:
        v = _scalar(db.get_field_value(rec, field))
    except Exception:
        return default
    return default if v is None else v


def _marker_of(db, rec):
    """Current DisplayAsQuestItem as a float, or None when the field is absent."""
    f = db.get_fields(rec)
    if not f:
        return None
    for key, tf in f.items():
        if key.split('###')[0] == FIELD:
            try:
                return float(_scalar(tf.values))
            except (TypeError, ValueError):
                return None
    return None


def _marker_dtype(db, rec):
    f = db.get_fields(rec) or {}
    for key, tf in f.items():
        if key.split('###')[0] == FIELD:
            return tf.dtype
    return None


def _cls(db, rec):
    return str(_val(db, rec, 'Class', '') or '').lower()


def _rank(db, rec):
    return str(_val(db, rec, 'monsterClassification', '') or '').lower()


def _chain(db, rec):
    """The full actorToSpawnOnDeath chain starting at `rec` (rec included)."""
    out, seen, cur = [], set(), rec
    while cur and cur.lower() not in seen:
        seen.add(cur.lower())
        out.append(cur)
        nxt = _val(db, cur, CHAIN)
        nxt = str(nxt).strip() if nxt else ''
        if not nxt or not db.has_record(nxt):
            break
        cur = nxt
    return out


def _chain_pays_soul(db, rec):
    """RULE A: does any form in rec's chain actually pay a soul out?"""
    for form in _chain(db, rec):
        try:
            if float(_val(db, form, CHANCE, 0.0) or 0.0) > 0.0:
                return form
        except (TypeError, ValueError):
            continue
    return None


# ── THE ROSTER ──────────────────────────────────────────────────────────────
def _spawn_parents(db):
    """form (lower) -> set of records that name it via actorToSpawnOnDeath."""
    parents = {}
    for name in db.record_names():
        f = db.get_fields(name)
        if not f:
            continue
        for key, tf in f.items():
            if key.split('###')[0] != CHAIN:
                continue
            for v in tf.values:
                if isinstance(v, str) and v.strip():
                    parents.setdefault(v.strip().lower(), set()).add(name)
    return parents


def placed_uber_roster(db):
    """Return (targets, excluded_adds, shared_forms, mesh_noise).

    targets       - ordered record names that MUST carry the marker (rule A
                    encounters + rule B dedicated chain forms), deduplicated.
    excluded_adds - placed Monster records with no soul anywhere in their chain
                    (retinue/adds); reported, never marked.
    shared_forms  - chain forms skipped by rule B's exclusivity test, as
                    (form, sorted non-roster parents); reported, never marked.
    mesh_noise    - placed_members basenames that resolve to no Monster record.
    """
    _random_members, placed_members = bsd.soul_spawn_provenance_sets(db)

    by_base = {}
    for name in db.record_names():
        if _cls(db, name) in MONSTER_CLASSES:
            by_base.setdefault(bsd._soul_record_basename(name), []).append(name)

    # ── RULE A: the placed, soul-paying ENCOUNTERS ──────────────────────────
    entries, excluded_adds, mesh_noise, bad_rank = [], [], [], []
    for mb in sorted(placed_members):
        paths = by_base.get(mb)
        if not paths:
            mesh_noise.append(mb)
            continue
        for rec in sorted(paths):
            if not _chain_pays_soul(db, rec):
                excluded_adds.append(rec)
                continue
            rank = _rank(db, rec)
            if rank not in ENCOUNTER_RANKS:
                bad_rank.append((rec, rank))
                continue
            entries.append(rec)

    if bad_rank:
        raise AssertionError(
            'uber_quest_markers: placed soul-paying encounter(s) outside '
            'Hero/Boss/Quest - roster defect, not silently skipped: '
            + ', '.join(f'{r} (rank={k!r})' for r, k in bad_rank))

    # ── RULE B: expand across DEDICATED transform forms, to a fixpoint ───────
    parents = _spawn_parents(db)
    targets, seen = [], set()
    for rec in entries:
        if rec.lower() not in seen:
            seen.add(rec.lower())
            targets.append(rec)

    shared = {}
    grew = True
    while grew:
        grew = False
        for rec in list(targets):
            nxt = _val(db, rec, CHAIN)
            nxt = str(nxt).strip() if nxt else ''
            if not nxt or not db.has_record(nxt):
                continue
            if nxt.lower() in seen or _cls(db, nxt) not in MONSTER_CLASSES:
                continue
            outside = sorted(p for p in parents.get(nxt.lower(), ())
                             if p.lower() not in seen)
            if outside:
                shared[nxt] = outside      # shared with non-uber spawners
                continue
            seen.add(nxt.lower())
            targets.append(nxt)
            grew = True

    # a form that only LOOKED shared while the roster was still growing is not
    # shared once the fixpoint is reached
    shared_forms = sorted((f, [p for p in ps if p.lower() not in seen])
                          for f, ps in shared.items()
                          if f.lower() not in seen)
    shared_forms = [(f, ps) for f, ps in shared_forms if ps]

    # ...and, for the same reason, a record that rule A filed as a soul-less
    # "add" is NOT an add if rule B ultimately claimed it as a DEDICATED chain
    # form. A transform stage pays no soul of its own, so rule A always sees it
    # that way; only the fixpoint knows whether it belongs to the roster.
    # This became reachable in the 2026-07-28 debt-wave integration: fix/debt-db
    # closes soul_spawn_provenance_sets() forward over actorToSpawnOnDeath
    # (the R-42 legion fold-in), so placed provenance now reaches transform
    # stages and rule A sees forms it never used to. Marking output is
    # unaffected (roster stays 25 / 23 newly marked); this keeps the REPORT and
    # the plant-3 invariant ("no add is also a target") honest.
    excluded_adds = [a for a in excluded_adds if a.lower() not in seen]

    return targets, excluded_adds, shared_forms, mesh_noise


# ── the invariant, shared by verify() and the negative test ─────────────────
def marker_violations(db, targets=None):
    """Every roster member (and every anchor) must sit at DisplayAsQuestItem=1."""
    if targets is None:
        targets, _adds, _shared, _noise = placed_uber_roster(db)
    bad = []
    for rec in targets:
        cur = _marker_of(db, rec)
        if cur is None:
            bad.append((rec, 'FIELD ABSENT'))
        elif cur != 1.0:
            bad.append((rec, f'{FIELD}={cur}'))
    for rec, why in PREEXISTING_ANCHORS:
        if not db.has_record(rec):
            bad.append((rec, f'ANCHOR RECORD MISSING ({why})'))
            continue
        cur = _marker_of(db, rec)
        if cur != 1.0:
            bad.append((rec, f'ANCHOR REGRESSED to {cur} ({why})'))
    return bad


def _snapshot_markers(db):
    snap = {}
    for name in db.record_names():
        v = _marker_of(db, name)
        if v is not None:
            snap[name] = v
    return snap


# ── registry hooks ──────────────────────────────────────────────────────────
def apply(db, tags):
    targets, excluded_adds, shared_forms, mesh_noise = placed_uber_roster(db)

    before = _snapshot_markers(db)
    already = [r for r in targets if before.get(r) == 1.0]

    for rec in targets:
        dtype = _marker_dtype(db, rec)
        if dtype is None:
            raise AssertionError(
                f'uber_quest_markers: {FIELD} absent on {rec} - the field is '
                'universal on Monster.tpl, so an absent field means the record '
                'is not the shape this module assumes')
        # MINIMAL TOUCH (arz_patcher's core design law): a record already at 1
        # is left as raw compressed passthrough bytes rather than decoded and
        # re-encoded for a no-op write. Keeps the touched set == the changed set.
        if before.get(rec) == 1.0:
            continue
        db.set_field(rec, FIELD, 1 if dtype == DATA_TYPE_INT else 1.0)

    after = _snapshot_markers(db)
    changed = sorted(k for k in after if before.get(k) != after[k])
    expected = sorted(set(targets) - set(already))
    if changed != expected:
        raise AssertionError(
            'uber_quest_markers: scope violation - changed set != computed '
            f'roster.\n  unexpected: {sorted(set(changed) - set(expected))}\n'
            f'  missing   : {sorted(set(expected) - set(changed))}')

    print(f'  {MODULE_NAME}: roster {len(targets)} placed-uber record(s) '
          f'({len(already)} already marked, {len(changed)} newly marked); '
          f'excluded {len(excluded_adds)} retinue/add record(s) with no soul in '
          f'their chain and {len(shared_forms)} SHARED transform form(s); '
          f'{len(mesh_noise)} mesh-basename non-record(s) ignored; 0 tag(s)')


def verify(db, tags):
    targets, excluded_adds, shared_forms, _noise = placed_uber_roster(db)
    bad = marker_violations(db, targets)
    if bad:
        raise AssertionError(
            'uber_quest_markers verify FAILED - placed uber(s) without the '
            'quest marker:\n' + '\n'.join(f'    {r}: {w}' for r, w in bad))

    # the exclusion side of the invariant must stay real: an add that silently
    # acquired a soul would change the roster, so re-assert none of the excluded
    # records pays out.
    leaked = [r for r in excluded_adds if _chain_pays_soul(db, r)]
    if leaked:
        raise AssertionError(
            'uber_quest_markers verify FAILED - record(s) classified as '
            f'retinue/adds now pay out a soul: {leaked}')

    # RULE B's exclusivity test must stay real: a shared terminal form must NOT
    # have acquired the marker (that would leak it onto its non-uber spawners).
    leaked_forms = [(f, ps) for f, ps in shared_forms if _marker_of(db, f) == 1.0]
    if leaked_forms:
        raise AssertionError(
            'uber_quest_markers verify FAILED - SHARED transform form(s) carry '
            'the marker, which leaks it onto non-uber spawners:\n'
            + '\n'.join(f'    {f} (also spawned by {ps})' for f, ps in leaked_forms))

    print(f'  {MODULE_NAME} verify OK: {len(targets)}/{len(targets)} placed-uber '
          f'records carry {FIELD}=1 (incl. every dedicated transform-chain form); '
          f'{len(excluded_adds)} retinue/add records correctly unmarked; '
          f'{len(shared_forms)} shared transform form(s) correctly left alone; '
          f'{len(PREEXISTING_ANCHORS)} pre-existing anchors intact')


# ── CLI: read-only analysis + the planted negative test ─────────────────────
def _load(arz):
    from arz_patcher import ArzDatabase
    return ArzDatabase.from_arz(Path(arz))


def _analyze(arz):
    db = _load(arz)
    targets, adds, shared, noise = placed_uber_roster(db)
    marked = [r for r in targets if _marker_of(db, r) == 1.0]
    print(f'\nARZ: {arz}')
    print(f'  placed-uber roster           : {len(targets)}')
    print(f'  already DisplayAsQuestItem=1 : {len(marked)}')
    print(f'  would be newly marked        : {len(targets) - len(marked)}')
    print(f'  excluded retinue/adds        : {len(adds)}')
    print(f'  excluded SHARED chain forms  : {len(shared)}')
    print(f'  mesh-basename non-records    : {len(noise)}')
    print('\n  --- ROSTER ---')
    for r in targets:
        print(f'    [{"X" if _marker_of(db, r) == 1.0 else " "}] {r}'
              f'  rank={_rank(db, r)}')
    print('\n  --- EXCLUDED (retinue/adds, no soul in chain) ---')
    for r in adds:
        print(f'        {r}  rank={_rank(db, r)}')
    print('\n  --- EXCLUDED (shared transform forms - marking these would leak) ---')
    for f, ps in shared:
        print(f'        {f}\n            also spawned by: {", ".join(ps)}')
    print('\n  --- mesh-basename noise ---')
    print('        ' + ', '.join(noise))


def _negtest(arz):
    """Prove the gate is not vacuous. Four plants over a throwaway db."""
    db = _load(arz)
    targets, adds, shared, _noise = placed_uber_roster(db)
    apply(db, {})

    clean = marker_violations(db, targets)
    control_ok = (clean == [])

    # PLANT 1: a roster member reset to 0 must be flagged.
    victim = targets[0]
    db.set_field(victim, FIELD, 0)
    plant1 = any(r == victim for r, _ in marker_violations(db, targets))
    db.set_field(victim, FIELD, 1)

    # PLANT 2: the anchor regression must be flagged.
    anchor = PREEXISTING_ANCHORS[0][0]
    prev = _marker_of(db, anchor)
    db.set_field(anchor, FIELD, 0)
    plant2 = any(r == anchor for r, _ in marker_violations(db, targets))
    db.set_field(anchor, FIELD, int(prev))

    # PLANT 3: the roster must NOT be "everything the proxies reference" - a
    # retinue add with no soul in its chain must be absent from it.
    plant3 = bool(adds) and all(a not in targets for a in adds)

    # PLANT 4: a SHARED transform form must be excluded, and apply() must have
    # left it unmarked - otherwise the marker leaks to its non-uber spawners.
    if shared:
        sf = shared[0][0]
        plant4 = (sf not in targets) and (_marker_of(db, sf) != 1.0)
        sf_label = f'{sf} (also spawned by {len(shared[0][1])} non-uber(s))'
    else:
        plant4, sf_label = False, 'NONE FOUND - the leak test is vacuous'

    print('\nuber_quest_markers _negtest:')
    print(f'  unmarked-roster-member plant flagged : {plant1}')
    print(f'  anchor-regression plant flagged      : {plant2}')
    print(f'  retinue adds excluded from roster    : {plant3} '
          f'({len(adds)} adds, e.g. {adds[0] if adds else "-"})')
    print(f'  shared chain form left unmarked      : {plant4}')
    print(f'                                         {sf_label}')
    print(f'  correctly-marked control is clean    : {control_ok} ({clean})')
    ok = plant1 and plant2 and plant3 and plant4 and control_ok
    print(f'  -> {"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


if __name__ == '__main__':
    args = sys.argv[1:]
    DEFAULT_ARZ = (Path(__file__).resolve().parent.parent.parent
                   / 'local' / 'baseline_build47.arz')
    if '--analyze' in args:
        i = args.index('--analyze')
        _analyze(args[i + 1] if len(args) > i + 1 else DEFAULT_ARZ)
    elif '--negtest' in args:
        i = args.index('--negtest')
        raise SystemExit(_negtest(
            args[i + 1] if len(args) > i + 1 else DEFAULT_ARZ))
    else:
        print(__doc__)
