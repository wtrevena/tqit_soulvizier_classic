r"""toxeus_hunt_endless - THE ENDLESS PURSUIT (b98, R-80).

WILL'S RULING (verbatim, 2026-07-28):
    "yeah lets have the endless pursuit only be on legendary"

--------------------------------------------------------------------------------
WHY THIS NEEDS A SECOND RECORD (the mechanism, proven, not assumed)
--------------------------------------------------------------------------------
"You can kite him back and forth from where he spawns" is NOT a monster field. All
4,600 Monster records in the DB carry ZERO leash/aggro/chase/pursuit field; the
whole class lives on CONTROLLER records, reached through the monster's scalar
`controller` field. The Endless Hunt points at
`records\controllers\monster\controller_shadowstalker01_hidden.dbr`:
    MaxPursuitDistance = 60.0     <- he breaks off 60 world-units from his origin
    PursuitTime        = 20000    <- and gives up after 20 seconds
    RoamBehavior       = Roam     <- then wanders back
That is the kite, field for field.

PER-DIFFICULTY PURSUIT IS NOT EXPRESSIBLE ON ONE RECORD. Two independent proofs:
  * EMPIRICAL: across every controller record in the DB, MaxPursuitDistance and
    PursuitTime are array-valued ZERO times (the count of controller records varies
    with the denominator - see the CARRIER-COUNT NOTE below - but ZERO does not).
    The only controller field ever array-valued anywhere is LeadChance, which proves
    controllers CAN carry per-difficulty arrays and that these two do not.
  * AUTHORITATIVE: the engine's own Toolset/Templates.arc declares, in
    templates/controllermonster.tpl, MaxPursuitDistance class="variable" and
    PursuitTime class="variable", while LeadChance is class="array". In TQ,
    class="array" IS the [normal,epic,legendary] triple. And templates/monster.tpl
    declares `controller` class="variable" - one monster, one controller, all three
    difficulties.
A Legendary-gated buff/aura skill cannot do it either: skills move STATS, they
cannot write controller fields. So the honest route is a second monster record
selected by the proxy's own poolLegendary1 slot - and that has a shipped donor
pattern: 29 base-game proxies already resolve to DIFFERENT monsters per difficulty
through pool slots (e.g. `ag_demon_djinnsprite_01t_ambush.dbr`, whose pool1 names
the *_ambush behavioural variants and whose poolEpic1 names the plain ones).

--------------------------------------------------------------------------------
WHAT THIS SHIPS
--------------------------------------------------------------------------------
1. `records\controllers\monster\controller_toxeus_hunt_endless.dbr` - a CLONE of
   controller_shadowstalker01_hidden (so the ambush identity is preserved verbatim:
   ControllerMonsterHidden, appearDistance 12, NeverFlee), overridden with
       MaxPursuitDistance 1000.0   (controller_aktaios ships exactly this; it is
                                    the highest monster value in the DB)
       PursuitTime        100000   (shipped, incl. controller_hydra,
                                    controller_terracotta, controller_typhonminion)
       RoamBehavior       NeverRoam (shipped, widely)
   ⚠️ CARRIER-COUNT NOTE (round 2, after the adversarial vet reported different
   numbers): the three census figures round 1 quoted (21 / 107 / 504) came from a
   different DENOMINATOR than the vet's (15 / 69 / 531) and than a mod-arz-only
   re-run (8 / 31 / 250 records under `records\controllers\`). Every one of those
   denominators is defensible - mod arz alone, mod arz unioned with the base-game
   DB, or "controller-class" by Class rather than by path - and the CONCLUSION is
   identical under all three: these fields are scalars by template declaration, and
   each value this module writes has at least one named shipped carrier (verified
   individually by record, not by count). Bare counts are not load-bearing here and
   should not be quoted without their denominator.
       MinTimeBeforeRoam / MaxTimeBeforeRoam 0
       ForgiveRate        0.2      (Aktaios: anger decays slowly)
   CLONED, NEVER EDITED IN PLACE: controller_shadowstalker01_hidden is shared by 15
   monsters, including the Enslaver's own marauders. Editing it would make every
   shadowstalker ambusher in the game relentless (BL-103: fix at the right layer -
   and the right layer here is a NEW record).
   FleeBehavior stays NeverFlee. Aktaios's FleeWhenEnemyClose / maxFleeCount 100 are
   deliberately NOT copied: a hunter that flees is nonsense.

2. `records\creature\monster\shadowstalker\um_toxeus_hunt_l_99.dbr` - the Endless
   Hunt with EXACTLY ONE field changed: `controller`.

3. `records\drxmap\proxy\pools\q_toxeus_hunt_lone_endless.dbr` - a single-member
   pool, and `q_toxeus_hunt_lone.poolLegendary1` repointed at it. pool1 and
   poolEpic1 keep naming the base pool (toxeus_hunt_encounter sets them), so
   Normal and Epic fight the kiteable Hunt and Legendary fights the relentless one.

--------------------------------------------------------------------------------
THE MAINTENANCE HAZARD, AND WHY IT IS STRUCTURALLY IMPOSSIBLE HERE
--------------------------------------------------------------------------------
A second record doubles every future Hunt edit - soul rate, kit, spear, tuning -
and a missed edit silently gives Legendary players a differently-balanced monster.
TWO THINGS MAKE THAT UNREACHABLE:
  * the variant is GENERATED at build time as a clone-then-override of the base, so
    there is no hand-maintained second copy to drift; and
  * verify() asserts base and variant differ in EXACTLY the `controller` field and
    in NOTHING else, fail-loud.
ORDERING is load-bearing to both: this module is registered AFTER every writer of
the base record (toxeus_hunt_encounter, toxeus_champion_kits, boss_skill_fix,
toxeus_souls_100 and uber_quest_markers), so the clone captures the FINAL base -
including the R-81 100% soul rate and the DisplayAsQuestItem marker.

--------------------------------------------------------------------------------
THE LIMIT WILL MUST KNOW ABOUT (reported, not hidden)
--------------------------------------------------------------------------------
The ROAMING spawns cannot be difficulty-split. ProxyPool has `nameN` with no
`nameEpicN`/`nameLegendaryN` counterpart, and the 345 roaming pools the Hunt rides
are NATIVE base-game pools shared by hundreds of proxies across all difficulties.
So the roaming Hunt stays the BASE (kiteable) record even on Legendary; only the
FIXED Hades Palace encounter carries the endless variant. That is also the SAFEST
shape: MaxPursuitDistance 1000 is proven on Aktaios, a FIXED ARENA boss in bounded
space, which is exactly what the Hades Palace floor placement gives it.
"""

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))   # tools/ on path

MODULE_NAME = "Endless Hunt: Legendary-only endless pursuit (R-80)"

DATA_TYPE_INT = 0
DATA_TYPE_FLOAT = 1
DATA_TYPE_STRING = 2

_BASE_MON = r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr'
_VAR_MON = r'records\creature\monster\shadowstalker\um_toxeus_hunt_l_99.dbr'
_DONOR_CTRL = r'records\controllers\monster\controller_shadowstalker01_hidden.dbr'
_VAR_CTRL = r'records\controllers\monster\controller_toxeus_hunt_endless.dbr'
_BASE_POOL = r'records\drxmap\proxy\pools\q_toxeus_hunt_lone.dbr'
_VAR_POOL = r'records\drxmap\proxy\pools\q_toxeus_hunt_lone_endless.dbr'
_PROXY = r'records\drxmap\proxy\q_toxeus_hunt_lone.dbr'

# field -> (value, dtype). Every value has a named shipped precedent (see docstring).
_ENDLESS = (
    ('MaxPursuitDistance', 1000.0, DATA_TYPE_FLOAT),
    ('PursuitTime', 100000, DATA_TYPE_INT),
    ('RoamBehavior', 'NeverRoam', DATA_TYPE_STRING),
    ('MinTimeBeforeRoam', 0, DATA_TYPE_INT),
    ('MaxTimeBeforeRoam', 0, DATA_TYPE_INT),
    ('ForgiveRate', 0.2, DATA_TYPE_FLOAT),
)
# the ONE field allowed to differ between base and variant
_ALLOWED_DIFF = 'controller'


def _norm(p):
    return str(p).replace('/', '\\').lower()


def _gv1(db, rec, f):
    v = db.get_field_value(rec, f)
    return v[0] if isinstance(v, list) and v else v


def _fieldmap(db, rec):
    """{base field name: tuple(values)} for a whole record (order-insensitive)."""
    out = {}
    ff = db.get_fields(rec) or {}
    for k, tf in ff.items():
        out[k.split('###')[0]] = tuple(tf.values or [])
    return out


def _build_controller(db):
    if not db.has_record(_DONOR_CTRL):
        raise SystemExit("[toxeus_hunt_endless] donor controller missing: %s" % _DONOR_CTRL)
    if not db.has_record(_VAR_CTRL):
        db.clone_record(_DONOR_CTRL, _VAR_CTRL)
    for f, v, dt in _ENDLESS:
        # every one of these exists on the shipped donor record -> value-only
        # override (passing dtype on a cloned record is the INT/FLOAT corruption trap)
        if db.get_field_value(_VAR_CTRL, f) is None:
            db.set_field(_VAR_CTRL, f, v, dt)
        else:
            db.set_field(_VAR_CTRL, f, v)
    db.set_field(_VAR_CTRL, 'FileDescription',
                 'Endless pursuit (R-80): no leash, no roam-back, never forgets')
    db._modified.add(_VAR_CTRL)
    print("  controller cloned: MaxPursuitDistance 60 -> 1000 (Aktaios), "
          "PursuitTime 20000 -> 100000, Roam -> NeverRoam, ForgiveRate 1.0 -> 0.2; "
          "NeverFlee + the ambush identity kept.")


def _build_variant(db):
    if not db.has_record(_BASE_MON):
        raise SystemExit("[toxeus_hunt_endless] base monster missing: %s" % _BASE_MON)
    if db.has_record(_VAR_MON):
        raise SystemExit(
            "[toxeus_hunt_endless] %s already exists - this module is the sole "
            "author of the endless variant and refuses to overwrite a record "
            "somebody else made." % _VAR_MON)
    db.clone_record(_BASE_MON, _VAR_MON)
    db.set_field(_VAR_MON, 'controller', _VAR_CTRL)
    db._modified.add(_VAR_MON)
    # prove the ONE-FIELD invariant immediately, not only at verify() time.
    diff = _one_field_diff(db)
    if diff != {_ALLOWED_DIFF}:
        raise SystemExit(
            "[toxeus_hunt_endless] the freshly-generated variant differs from the "
            "base in %s, expected exactly {'controller'}. The clone-then-override "
            "generator is broken." % sorted(diff))
    print("  variant authored: %s = the FINAL base record with ONE field changed "
          "(controller); every other field identical by construction."
          % _VAR_MON.rsplit('\\', 1)[-1])


def _one_field_diff(db):
    a, b = _fieldmap(db, _BASE_MON), _fieldmap(db, _VAR_MON)
    return {k for k in set(a) | set(b) if a.get(k) != b.get(k)}


def _wire_pool_and_proxy(db):
    from apply_svc_patches import _ensure_record
    import apply_svc_patches as asp
    S, I, F = DATA_TYPE_STRING, DATA_TYPE_INT, DATA_TYPE_FLOAT
    _ensure_record(db, _VAR_POOL, r'database\Templates\ProxyPool.tpl')
    db.set_field(_VAR_POOL, 'templateName', r'database\Templates\ProxyPool.tpl', S)
    db.set_field(_VAR_POOL, 'FileDescription',
                 'Endless-pursuit Endless Hunt, LEGENDARY only (1)', S)
    db.set_field(_VAR_POOL, 'name1', _VAR_MON, S)
    db.set_field(_VAR_POOL, 'weight1', 10, I)
    db.set_field(_VAR_POOL, 'spawnMin', 1, I)
    db.set_field(_VAR_POOL, 'spawnMax', 1, I)
    db.set_field(_VAR_POOL, 'championChance', 0.0, F)
    db.set_field(_VAR_POOL, 'championMin', 0, I)
    db.set_field(_VAR_POOL, 'championMax', 0, I)
    db._modified.add(_VAR_POOL)

    if not db.has_record(_PROXY):
        raise SystemExit(
            "[toxeus_hunt_endless] the fixed encounter proxy is missing (%s); "
            "toxeus_hunt_encounter must run before this module." % _PROXY)
    if db.get_field_value(_PROXY, 'poolLegendary1') is None:
        db.set_field(_PROXY, 'poolLegendary1', _VAR_POOL, S)
        db.set_field(_PROXY, 'weightLegendary1', 10, I)
    else:
        db.set_field(_PROXY, 'poolLegendary1', _VAR_POOL)
        db.set_field(_PROXY, 'weightLegendary1', 10)
    db._modified.add(_PROXY)

    already = any(spec.get('pool') == _VAR_POOL
                  for spec in asp._MOD_AUTHORED_SPAWN_PROXIES)
    if not already:
        asp._MOD_AUTHORED_SPAWN_PROXIES.append({
            'proxy': _PROXY,
            'pool': _VAR_POOL,
            'main_monster': _VAR_MON,
            'name': 'q_toxeus_hunt_lone poolLegendary1 (endless-pursuit Hunt, L only)',
        })
    print("  poolLegendary1 -> %s (Normal/Epic keep the base kiteable Hunt)."
          % _VAR_POOL.rsplit('\\', 1)[-1])


def apply(db, tags):
    print("\n=== [toxeus_hunt_endless] b98 THE ENDLESS PURSUIT (R-80) ===")
    _build_controller(db)
    _build_variant(db)
    _wire_pool_and_proxy(db)
    print("=== [toxeus_hunt_endless] done (verify() runs post-finalization) ===\n")
    return tags


def verify(db, tags=None):
    problems = []

    # (1) THE ONE-FIELD INVARIANT - the whole anti-drift argument rests on it.
    if not db.has_record(_BASE_MON):
        problems.append("base monster missing: %s" % _BASE_MON)
    elif not db.has_record(_VAR_MON):
        problems.append("endless variant missing: %s" % _VAR_MON)
    else:
        diff = _one_field_diff(db)
        if diff != {_ALLOWED_DIFF}:
            problems.append(
                "DRIFT: the endless variant and the base Endless Hunt differ in %s "
                "(expected exactly {'controller'}). A later writer touched one and "
                "not the other, so Legendary players would fight a differently "
                "balanced monster." % sorted(diff))
        if _norm(_gv1(db, _VAR_MON, 'controller')) != _norm(_VAR_CTRL):
            problems.append("variant controller=%r != %s"
                            % (_gv1(db, _VAR_MON, 'controller'), _VAR_CTRL))
        if _norm(_gv1(db, _BASE_MON, 'controller')) == _norm(_VAR_CTRL):
            problems.append(
                "the BASE Endless Hunt now points at the endless controller too - "
                "Normal and Epic would become unkiteable, which R-80 does not say")

    # (2) the controller actually carries the endless numbers, and the SHARED
    #     donor was not edited in place (the 15-monster blast radius).
    if not db.has_record(_VAR_CTRL):
        problems.append("endless controller missing: %s" % _VAR_CTRL)
    else:
        for f, want, _dt in _ENDLESS:
            got = _gv1(db, _VAR_CTRL, f)
            same = (abs(float(got) - float(want)) < 0.001
                    if isinstance(want, (int, float)) and got is not None
                    else got == want)
            if not same:
                problems.append("endless controller %s=%r (expected %r)" % (f, got, want))
        if _gv1(db, _VAR_CTRL, 'FleeBehavior') != 'NeverFlee':
            problems.append("endless controller FleeBehavior=%r (a hunter must not flee)"
                            % _gv1(db, _VAR_CTRL, 'FleeBehavior'))
        if _gv1(db, _VAR_CTRL, 'Class') != 'ControllerMonsterHidden':
            problems.append("endless controller lost the ambush class (Class=%r)"
                            % _gv1(db, _VAR_CTRL, 'Class'))
    if db.has_record(_DONOR_CTRL):
        d_dist = _gv1(db, _DONOR_CTRL, 'MaxPursuitDistance')
        d_time = _gv1(db, _DONOR_CTRL, 'PursuitTime')
        if float(d_dist or 0) > 60.0 or int(d_time or 0) > 20000:
            problems.append(
                "BLAST RADIUS: the SHARED donor %s was edited in place "
                "(MaxPursuitDistance=%r, PursuitTime=%r) - that would make all 15 "
                "monsters that use it relentless, including the Enslaver's marauders"
                % (_DONOR_CTRL, d_dist, d_time))
    else:
        problems.append("donor controller missing: %s" % _DONOR_CTRL)

    # (3) the difficulty split is actually wired on the proxy.
    if not db.has_record(_PROXY):
        problems.append("proxy missing: %s" % _PROXY)
    else:
        pl = _gv1(db, _PROXY, 'poolLegendary1')
        if _norm(pl) != _norm(_VAR_POOL):
            problems.append("R-80: %s poolLegendary1=%r != the endless pool %s"
                            % (_PROXY, pl, _VAR_POOL))
        for f in ('pool1', 'poolEpic1'):
            v = _gv1(db, _PROXY, f)
            if _norm(v) != _norm(_BASE_POOL):
                problems.append(
                    "R-80: %s %s=%r != the BASE pool %s - Normal/Epic must keep the "
                    "kiteable Hunt" % (_PROXY, f, v, _BASE_POOL))
    if not db.has_record(_VAR_POOL):
        problems.append("endless pool missing: %s" % _VAR_POOL)
    else:
        if _norm(_gv1(db, _VAR_POOL, 'name1')) != _norm(_VAR_MON):
            problems.append("endless pool name1=%r != %s"
                            % (_gv1(db, _VAR_POOL, 'name1'), _VAR_MON))
        for i in range(2, 19):
            if _gv1(db, _VAR_POOL, 'name%d' % i):
                problems.append("endless pool has an extra member name%d" % i)

    if problems:
        for p in problems:
            print("  ENDLESS-PURSUIT OFFENDER: %s" % p)
        raise SystemExit("toxeus_hunt_endless.verify FAILED: %d problem(s)" % len(problems))
    print("  [toxeus_hunt_endless].verify OK: Legendary resolves the endless "
          "variant (pursuit 1000 / 100000 / NeverRoam, NeverFlee kept); Normal and "
          "Epic keep the base Hunt; base and variant differ in EXACTLY 'controller'; "
          "the 15-monster shared donor controller is untouched.")
    return tags


def _negtest():
    """py tools/patches/toxeus_hunt_endless.py --negtest"""
    from collections import OrderedDict

    class _TF(object):
        def __init__(self, v):
            self.values = v

    class _Stub(object):
        def __init__(self):
            self.d = {}
            self._modified = set()

        def has_record(self, n):
            return n in self.d

        def record_names(self):
            return list(self.d)

        def get_fields(self, n):
            f = self.d.get(n)
            if f is None:
                return None
            return OrderedDict((k, _TF(v)) for k, v in f.items())

        def get_field_value(self, n, f):
            return self.d.get(n, {}).get(f)

        def set_field(self, n, f, v, dt=None):
            self.d.setdefault(n, {})[f] = v if isinstance(v, list) else [v]

    def _base():
        db = _Stub()
        db.d[_DONOR_CTRL] = {'MaxPursuitDistance': [60.0], 'PursuitTime': [20000],
                             'FleeBehavior': ['NeverFlee'],
                             'Class': ['ControllerMonsterHidden']}
        ctrl = {'Class': ['ControllerMonsterHidden'], 'FleeBehavior': ['NeverFlee']}
        for f, v, _dt in _ENDLESS:
            ctrl[f] = [v]
        db.d[_VAR_CTRL] = ctrl
        mon = {'Class': ['Monster'], 'charLevel': [40, 68, 100],
               'chanceToEquipFinger2': [100.0],
               'controller': [_DONOR_CTRL]}
        db.d[_BASE_MON] = dict(mon)
        var = dict(mon)
        var['controller'] = [_VAR_CTRL]
        db.d[_VAR_MON] = var
        db.d[_BASE_POOL] = {'name1': [_BASE_MON]}
        db.d[_VAR_POOL] = {'name1': [_VAR_MON]}
        db.d[_PROXY] = {'pool1': [_BASE_POOL], 'poolEpic1': [_BASE_POOL],
                        'poolLegendary1': [_VAR_POOL]}
        return db

    plants = [
        ('variant drifts from base (a second field differs)',
         lambda db: db.d[_VAR_MON].__setitem__('chanceToEquipFinger2', [25.0])),
        ('the SHARED donor controller was edited in place',
         lambda db: db.d[_DONOR_CTRL].__setitem__('MaxPursuitDistance', [1000.0])),
        ('Legendary stops resolving the endless variant',
         lambda db: db.d[_PROXY].__setitem__('poolLegendary1', [_BASE_POOL])),
        ('Normal silently gets the endless variant too',
         lambda db: db.d[_PROXY].__setitem__('pool1', [_VAR_POOL])),
        ('the hunter learns to flee',
         lambda db: db.d[_VAR_CTRL].__setitem__('FleeBehavior', ['FleeWhenEnemyClose'])),
    ]
    try:
        verify(_base())
    except SystemExit as e:
        print("NEGTEST SETUP FAIL: the clean stub should PASS but raised: %s" % e)
        return 1
    bad = 0
    for label, plant in plants:
        db = _base()
        plant(db)
        try:
            verify(db)
        except SystemExit:
            print("  negtest OK  (caught): %s" % label)
            continue
        print("  negtest FAIL (missed): %s" % label)
        bad += 1
    print("negtest: %d/%d plants caught" % (len(plants) - bad, len(plants)))
    return 1 if bad else 0


if __name__ == '__main__':
    import sys
    sys.exit(_negtest() if '--negtest' in sys.argv else 0)
