r"""toxeus_legendary_stalker - ITEM 3 (B-TOXEUS-STALKER-1, APPROVED-BY-WILL-2026-07-14).

WHAT THIS SHIPS
--------------------------------------------------------------------------------
A strictly-Legendary-only, FIXED-placement Toxeus stalker encounter, via the
PROVEN base-game "Hydra pattern" (docs/reports/el_boss_audit.md S2): a proxy
whose `pool1` (Normal) is EMPTY and whose `poolEpic1` (Epic) is EMPTY, with
ONLY `poolLegendary1` populated - so the proxy resolves to nothing at all on
Normal or Epic and spawns ONLY when the game is running at Legendary
difficulty. This is a real data-only gate (ground-truthed against the shipped
`records\proxies boss\boss\minobossproxy_aniketos.dbr` / `questbossproxy_
celtheano.dbr` - both "no pool1 at all, poolEpic1/poolLegendary1 = a
guaranteed single-member boss pool" - our own build's most recent live proof,
"Aniketos E/L restore", build41 gate record). This is DELIBERATELY NOT the
`limit_legendary_only` ProxyLimits artifact toxeus_suite.py authors inert as
an UNTESTED experiment (a `difficultyLimitsFilewindow only ever SCALES a
monster's level, it never filters whether the proxy resolves at all - see
docs/MULTIPLAYER_COMPAT.md M4.6 and the toxeus_suite docstring's own "Option 1
vs Option 2" framing). Pool-slot gating is Option 1, the proven one.

Reuses the SHIPPED Endless Hunt stalker record family verbatim - no new
monster clone. `records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr`
(ShadowStalker rig, Boss, charLevel [40,68,100], already wired with its own
`{^F}` svc_uber soul at the Boss release rate, 25%) is the SAME record the
roaming Endless Hunt (toxeus_suite.py PART C) sweeps into Hades trash pools.
This fixed proxy just gives him ONE additional, guaranteed, findable Hades
appearance alongside his existing roaming odds - same monster, same soul,
same drops, by construction (there is only one `um_toxeus_hunt_99` record).

Proxy: clones the gate-proven `q_bloodtoxeus_lone` donor (_BT_PROXY - the
exact same donor toxeus_suite.py's ambush proxy already clones), inheriting
its no-cap `difficultyLimitsFile` (`limit_bloodtoxeus`, [1..110] on every
difficulty - already correctly sized for `um_toxeus_hunt_99`'s L100 ceiling),
then:
  - `pool1` cleared to '' (was q_bloodtoxeus_lone's pool - Normal now empty)
  - `weight1` cleared to 0 (no residual Normal-tier configuration)
  - `poolLegendary1` (NEW field on this record) = the new single-member pool
  - `weightLegendary1` (NEW field) = 10 (matches the Aniketos precedent)
  - `mesh`/`scale` overridden to the Hunt's own ShadowStalker silhouette
    (`ShadowStalker.msh`, scale 1.9 - matches his actual in-monster scale) so
    the editor/engine preview reads as him, not the donor's Blood-Toxeus
    silhouette (mirrors `_create_blood_toxeus_proxy`'s own preview-mesh idiom)
  - `chanceToRun` stays 100 (donor value) - a guaranteed encounter once a
    Legendary character reaches the spot, matching "findable but fixed"
poolEpic1/weightEpic1 are intentionally NEVER set (absent = Epic empty,
exactly like Hydra's own "Normal+Epic empty" shape - cleaner than Aniketos,
which sets poolEpic1 too and is therefore Epic+Legendary, not Legendary-only).

Registered in `apply_svc_patches._MOD_AUTHORED_SPAWN_PROXIES` (main_monster =
um_toxeus_hunt_99) so the shared spawn-eligibility gate covers this placement
too (idempotent re-registration, mirrors toxeus_suite.py's own idiom).

MAP PLACEMENT (ground-truthed, on-mesh, collision-guarded)
--------------------------------------------------------------------------------
Surveyed on the deployed CANONICAL map (`work/SoulvizierClassic/Resources/
Levels.arc`, md5 eb8bc377's paired build41 CANON Levels md5 3f05c227) with
`tools/debug/survey_uberboss_spots.py`. Placement level:
`xpack/levels/area08_hadespalace/hadespalace_floor04_04.lvl` (Hades Palace -
the SAME level as the shipped General-B honor-guard encounter, build41
B41_GUARDB_KEY; Y=15.0 matches every other placement on this floor). Spot
`local(38.0, 45.0)`, clr=100% on ALL THREE tilesets (Normal/Epic/Legendary -
survey checks all three even though only Legendary ever resolves the
monster), reachable component #1 (the main walkable mass, 76,499 cells),
~29u from the nearest existing encounter (`q_general_b_guardpair` @
68.39,40.26) and 7-17u from the nearest static set-dressing (hp_prisoncorner
/hp_urn decoration meshes - non-blocking clearance, confirmed by the clr=100%
navmesh read itself), 0 collision with any functional entity (quest NPCs/
proxies/gate objects all cluster at x>=44,z>=58 or z<=23 - a genuinely quiet
back pocket of the floor). Calibration cross-check: the tool's frame-
correction reproduces the SHIPPED `q_general_b_guardpair` coordinate at
d=0.10u (same tool, same frame, proven-correct - see the survey transcript in
docs/reports/b65_lowlift_wave.md).

INJECT_SPECS entry (`build_section_surgery.py`) is added in a SEPARATE,
disjoint edit (this module is DB-only); see B65_TOXEUS_STALKER_KEY there.
"""

MODULE_NAME = "Toxeus Legendary-only stalker (B-TOXEUS-STALKER-1, Hydra pattern)"

DATA_TYPE_STRING = 2
DATA_TYPE_FLOAT = 1
DATA_TYPE_INT = 0

_STALKER_POOL = r'records\drxmap\proxy\pools\q_toxeus_hunt_lone.dbr'
_STALKER_PROXY = r'records\drxmap\proxy\q_toxeus_hunt_lone.dbr'
_STALKER_MESH = r'Creatures\Monster\ShadowStalker\ShadowStalker.msh'
_STALKER_SCALE = 1.9


def _norm(p):
    return str(p).replace('/', '\\').lower()


def apply(db, tags):
    import apply_svc_patches as asp

    donor_proxy = asp._BT_PROXY          # q_bloodtoxeus_lone
    hunt_monster = r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr'

    if not db.has_record(donor_proxy):
        raise SystemExit(
            "toxeus_legendary_stalker: donor proxy missing (exact): %s "
            "(monolith must build Blood Toxeus before this module runs)" % donor_proxy)
    if not db.has_record(hunt_monster):
        raise SystemExit(
            "toxeus_legendary_stalker: the Endless Hunt monster is missing "
            "(exact): %s (toxeus_suite PART C must run before this module)"
            % hunt_monster)
    if db.has_record(_STALKER_PROXY):
        raise SystemExit(
            "toxeus_legendary_stalker: %s already exists - refusing to "
            "overwrite" % _STALKER_PROXY)

    # ── pool: single-member, guaranteed, no champion escort (a lone fixed
    #    stalker - the roaming Hunt already provides the pack-hunter feel). ──
    _ensure_pool(db, hunt_monster)

    # ── proxy: clone the gate-proven Blood-Toxeus donor, then re-gate to
    #    Legendary-only + repoint the preview to the Hunt's own silhouette. ──
    db.clone_record(donor_proxy, _STALKER_PROXY)
    P = _STALKER_PROXY
    db.set_field(P, 'pool1', '')                       # pre-existing field -> no dtype; Normal empty
    db.set_field(P, 'weight1', 0)                       # pre-existing field -> no dtype
    db.set_field(P, 'poolLegendary1', _STALKER_POOL, DATA_TYPE_STRING)   # NEW field -> explicit dtype
    db.set_field(P, 'weightLegendary1', 10, DATA_TYPE_INT)               # NEW field -> explicit dtype
    # poolEpic1/weightEpic1 intentionally never set (absent = Epic empty too,
    # the Hydra "Normal+Epic empty" shape - see module docstring).
    db.set_field(P, 'mesh', _STALKER_MESH)              # pre-existing field -> no dtype
    db.set_field(P, 'scale', _STALKER_SCALE)            # pre-existing field -> no dtype
    db._modified.add(P)

    # ── register for the shared spawn-eligibility invariant (idempotent). ──
    already = any(spec.get('proxy') == _STALKER_PROXY
                  for spec in asp._MOD_AUTHORED_SPAWN_PROXIES)
    if not already:
        asp._MOD_AUTHORED_SPAWN_PROXIES.append({
            'proxy': _STALKER_PROXY,
            'pool': _STALKER_POOL,
            'main_monster': hunt_monster,
            'name': 'q_toxeus_hunt_lone (Legendary-only fixed Endless Hunt stalker)',
        })

    print("  toxeus_legendary_stalker: q_toxeus_hunt_lone authored (pool1/poolEpic1 "
          "EMPTY, poolLegendary1 -> single-member um_toxeus_hunt_99 pool); "
          "registered for spawn-eligibility.")


def _ensure_pool(db, hunt_monster):
    from apply_svc_patches import _ensure_record
    PL = _STALKER_POOL
    _ensure_record(db, PL, r'database\Templates\ProxyPool.tpl')
    S, I = DATA_TYPE_STRING, DATA_TYPE_INT
    db.set_field(PL, 'templateName', r'database\Templates\ProxyPool.tpl', S)
    db.set_field(PL, 'FileDescription', 'Legendary-only fixed Endless Hunt stalker (1)', S)
    db.set_field(PL, 'name1', hunt_monster, S)
    db.set_field(PL, 'weight1', 10, I)
    db.set_field(PL, 'spawnMin', 1, I)
    db.set_field(PL, 'spawnMax', 1, I)
    db.set_field(PL, 'championChance', 0.0, DATA_TYPE_FLOAT)
    db.set_field(PL, 'championMin', 0, I)
    db.set_field(PL, 'championMax', 0, I)
    db._modified.add(PL)


def verify(db, tags):
    """POST-FINALIZATION invariant (fail-loud):
      - the proxy exists, pool1/poolEpic1 are EMPTY, poolLegendary1 resolves
        to a pool whose sole member is um_toxeus_hunt_99;
      - the reused monster is untouched (Boss, charLevel [40,68,100], still
        wired with its own soul) - this module must never mutate it;
      - the proxy is registered in _MOD_AUTHORED_SPAWN_PROXIES."""
    import apply_svc_patches as asp

    hunt_monster = r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr'
    P = _STALKER_PROXY
    if not db.has_record(P):
        raise SystemExit("toxeus_legendary_stalker.verify FAIL: proxy missing: %s" % P)

    pool1 = db.get_field_value(P, 'pool1')
    if pool1 not in (None, ''):
        raise SystemExit(
            "toxeus_legendary_stalker.verify FAIL: %s pool1=%r (expected empty - "
            "Legendary-only gate broken, Normal would spawn him)" % (P, pool1))
    pool_epic = db.get_field_value(P, 'poolEpic1')
    if pool_epic not in (None, ''):
        raise SystemExit(
            "toxeus_legendary_stalker.verify FAIL: %s poolEpic1=%r (expected "
            "empty - Legendary-ONLY gate broken, Epic would spawn him too)"
            % (P, pool_epic))
    pool_leg = db.get_field_value(P, 'poolLegendary1')
    pool_leg = pool_leg[0] if isinstance(pool_leg, list) and pool_leg else pool_leg
    if _norm(pool_leg) != _norm(_STALKER_POOL):
        raise SystemExit(
            "toxeus_legendary_stalker.verify FAIL: %s poolLegendary1=%r != %s"
            % (P, pool_leg, _STALKER_POOL))
    weight_leg = db.get_field_value(P, 'weightLegendary1')
    weight_leg = weight_leg[0] if isinstance(weight_leg, list) and weight_leg else weight_leg
    if not weight_leg or int(weight_leg) <= 0:
        raise SystemExit(
            "toxeus_legendary_stalker.verify FAIL: %s weightLegendary1=%r "
            "(expected > 0)" % (P, weight_leg))

    if not db.has_record(_STALKER_POOL):
        raise SystemExit("toxeus_legendary_stalker.verify FAIL: pool missing: %s" % _STALKER_POOL)
    name1 = db.get_field_value(_STALKER_POOL, 'name1')
    name1 = name1[0] if isinstance(name1, list) and name1 else name1
    if _norm(name1) != _norm(hunt_monster):
        raise SystemExit(
            "toxeus_legendary_stalker.verify FAIL: pool name1=%r != %s"
            % (name1, hunt_monster))
    # single-member pool: no name2..18 populated.
    for i in range(2, 19):
        extra = db.get_field_value(_STALKER_POOL, 'name%d' % i)
        if extra not in (None, ''):
            raise SystemExit(
                "toxeus_legendary_stalker.verify FAIL: pool has an extra "
                "member name%d=%r (expected single-member)" % (i, extra))

    # the reused monster must be untouched by this module.
    if not db.has_record(hunt_monster):
        raise SystemExit("toxeus_legendary_stalker.verify FAIL: reused monster missing: %s" % hunt_monster)
    mc = db.get_field_value(hunt_monster, 'monsterClassification')
    mc = mc[0] if isinstance(mc, list) and mc else mc
    if mc != 'Boss':
        raise SystemExit(
            "toxeus_legendary_stalker.verify FAIL: %s monsterClassification=%r "
            "!= 'Boss' (this module must not mutate the reused monster)"
            % (hunt_monster, mc))
    cl = db.get_field_value(hunt_monster, 'charLevel')
    if list(cl) != [40, 68, 100]:
        raise SystemExit(
            "toxeus_legendary_stalker.verify FAIL: %s charLevel=%r != [40,68,100]"
            % (hunt_monster, cl))

    registered = any(spec.get('proxy') == P for spec in asp._MOD_AUTHORED_SPAWN_PROXIES)
    if not registered:
        raise SystemExit(
            "toxeus_legendary_stalker.verify FAIL: %s not registered in "
            "_MOD_AUTHORED_SPAWN_PROXIES" % P)

    print("  toxeus_legendary_stalker.verify OK: pool1/poolEpic1 EMPTY, "
          "poolLegendary1 -> single-member um_toxeus_hunt_99 pool; reused "
          "monster untouched (Boss, [40,68,100]); registered for "
          "spawn-eligibility.")
