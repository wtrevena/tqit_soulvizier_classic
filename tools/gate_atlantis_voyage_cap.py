r"""ATLANTIS SEA-VOYAGE CAP GATE (fail-loud, golden allow-list, negative-tested).

WHY
---
R-210 (branch `fix/portal-atlantis-cap`, build78) removed the Atlantis / Ragnarok /
Eternal-Embers PAGES from the act-selection UI. It explicitly did NOT close the
travel route, and registered the leak as `BL-PORTALCAP-DEBT-1`:

  "an Atlantis-DLC owner can still SAIL Rhodes -> Gadir -> Atlantis. The page is
   gone, the voyage is not."

Will, 2026-08-10: Atlantis is disabled in this mod. Standing ruling (Will,
2026-07-10): "lets not make atlantis or anything past immortal throne reachable
for now". This gate is the artifact proof that the voyage is closed too.

THE ROUTE, AND WHERE IT IS CUT (full RCA in docs/ATLANTIS_VOYAGE_CAP.md)
-----------------------------------------------------------------------
Atlantis is NOT a post-Hades act - it branches from RHODES, mid-Immortal-Throne,
which is why neither existing IT cap ever covered it. The chain is:

  xpack3_findmarinos.qst  (map QUESTS idx 207)   journal only, no travel
     -> x3mq_Marinos_Rhodes  spawned ONLY by the DLCActorSpawner
        `x3mq_marinos_rhodes_spawner.dbr` (the actor itself has ZERO static
        placements in our world01.map - byte-verified)
     -> x3mq_AtlantisAdventure.qst (idx 211) step "START QUEST: Second Talk
        Marinos": Condition_ConversationStart(x3mq_marinos_rhodes)
        -> Action_BoatDialog(rhodes_boatmantogadir)        [Rhodes -> Gadir]
     -> in Gadir, Marinos_Gadir steps ... -> step "GO TO ATLANTIS: Sixth Talk
        Marinos" -> Action_BoatDialog(gadir_boatmantoatlantis)  [-> ATLANTIS]
  XPack3TartarusPortal.qst (idx 205): talking to a Senechal unlocks the Tartarus
  portal, from Gadir or from Corinth (Corinth = the Ragnarok act, itself already
  A5-capped; its Senechal is a DLCActorSpawner too).

The quests live in the base game's `Resources\XPack3\Quests.arc` and the map
registers them under the `XPack3/Quests/...` namespace, so the A5 md5-full-
registry-path trap applies: a mod copy at the plain `Quests.arc` root is NEVER
consulted for them. The cap is therefore done at the DB-record layer (the A5
pattern: a .dbr's identity IS its record path and the mod .arz overrides the base
.arz per path - runtime-confirmed by the A5 Act-5 fix).

WHAT IT ASSERTS (all against the FINAL written .arz, artifact proof)
-------------------------------------------------------------------
  V1  both DLCActorSpawner records are PRESENT in the mod .arz (anti-inert) and
      carry NO `actorToSpawn` (template default = "", so they spawn nothing),
      while `dlcRequirement` is still exactly the base value (we suppressed the
      spawn, we did not widen the DLC gate)
  V2  both boundary boat NPCs are PRESENT with startVisible == 0 and
      IncludeInMap == 0 (hidden, and no minimap ghost - the A5 ghost lesson)
  V3  both Tartarus portals carry an AND-unsatisfiable DLC gate
      (RequireDLC and RequireNoDLC share a token - the A5-proven idiom)
  V4  the mod .arz overrides NO `records\xpack3\` record outside the golden
      allow-list (over-reach / collateral-damage check)
  V5  the DERIVED list of resolvable Atlantis-transit routes is EMPTY

usage:
  validate : py tools/gate_atlantis_voyage_cap.py <arz>
  negtest  : py tools/gate_atlantis_voyage_cap.py <arz> --negtest
exit codes: 0 = PASS, 1 = a transit route is resolvable / the cap is missing,
2 = usage.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase, DATA_TYPE_STRING  # noqa: E402

# ── THE CAPPED RECORDS (single source of truth; build_svc_database imports these)
MARINOS_SPAWNER = (r'records\xpack3\quests\npc\speaking'
                   r'\x3mq_marinos_rhodes_spawner.dbr')
SENECHAL_SPAWNER = (r'records\xpack3\creatures\npc\tartarus'
                    r'\senechaloftartarus_corinth_spawner.dbr')
RHODES_BOATMAN = (r'records\xpack3\creatures\npc\teleporters'
                  r'\rhodes_boatmantogadir.dbr')
ATLANTIS_BOATMAN = (r'records\xpack3\creatures\npc\teleporters'
                    r'\gadir_boatmantoatlantis.dbr')
TARTARUS_PORTAL_GADIR = r'records\xpack3\tartarus\portaltotartarus.dbr'
TARTARUS_PORTAL_CORINTH = (r'records\xpack3\tartarus'
                           r'\portaltotartarusfromcorinth.dbr')

# DLCActorSpawner records whose `actorToSpawn` we delete. Deleting the field
# leaves the template's own declared default ("" - `DLCActorSpawner.tpl`,
# type file_dbr, defaultValue ""), so the spawner has nothing to spawn. This is
# the same "field absence IS the declared default" argument R-210 shipped on.
SPAWNERS_CAPPED = (MARINOS_SPAWNER, SENECHAL_SPAWNER)
# The base value each spawner MUST keep, so a cap can never widen the DLC gate.
SPAWNER_DLC_REQUIREMENT = 'DLC2'

# The two boat NPCs that carry the only transitions from the reachable
# Immortal-Throne world INTO the XPack3 act, and onward onto Atlantis itself.
# Hidden, not deleted: `startVisible = 0` is a retail-shipped configuration on
# 604 base-game records, and NO quest in ANY of the five base quest archives
# fires Action_ShowNpc at either of them (byte-verified), so nothing can undo it.
HIDDEN_CARRIERS = (RHODES_BOATMAN, ATLANTIS_BOATMAN)

# A5-proven AND-unsatisfiable DLC gate: RequireDLC == RequireNoDLC == this token
# means "owns TQA2 AND does not own TQA2", which no player can satisfy, so the
# fixed item never spawns. (Shipped precedent for the AND semantics:
# endportal_hades_normal_epic.dbr, RequireDLC=TQX4 + RequireNoDLC=TQA2.)
TARTARUS_PORTALS = (TARTARUS_PORTAL_GADIR, TARTARUS_PORTAL_CORINTH)
UNSAT_DLC_TOKEN = 'TQA2'

# Every Atlantis-transit route that exists in the built artifacts, and the exact
# set of records whose suppression closes it. A route counts as RESOLVABLE (i.e.
# the gate REDs) unless EVERY record listed for it is proven suppressed.
ATLANTIS_TRANSIT_ROUTES = (
    ('Rhodes -> Gadir  (x3mq_AtlantisAdventure "START QUEST: Second Talk '
     'Marinos" -> Action_BoatDialog(rhodes_boatmantogadir))',
     (MARINOS_SPAWNER, RHODES_BOATMAN)),
    ('Gadir -> Atlantis  (x3mq_AtlantisAdventure "GO TO ATLANTIS: Sixth Talk '
     'Marinos" -> Action_BoatDialog(gadir_boatmantoatlantis))',
     (MARINOS_SPAWNER, ATLANTIS_BOATMAN)),
    ('Gadir -> Tartarus  (XPack3TartarusPortal step "Gadir" -> '
     'Action_UnlockFixedItem(portaltotartarus))',
     (MARINOS_SPAWNER, RHODES_BOATMAN, TARTARUS_PORTAL_GADIR)),
    ('Corinth -> Tartarus  (XPack3TartarusPortal step "Corinth" -> '
     'Action_UnlockFixedItem(portaltotartarusfromcorinth))',
     (SENECHAL_SPAWNER, TARTARUS_PORTAL_CORINTH)),
)

# The ONLY `records\xpack3\` records the mod .arz may override: the mastery
# skill-panel controllers that fix_mastery_panel_buttons() legitimately authors,
# plus this cap's own records. Anything else is over-reach.
_MASTERY_PANECTRL = re.compile(
    r'(?i)^records\\xpack3\\ui\\skills\\mastery \d+\\panectrl\.dbr$')
GOLDEN_XPACK3_OVERRIDES = frozenset(
    SPAWNERS_CAPPED + HIDDEN_CARRIERS + TARTARUS_PORTALS)


def _norm(name):
    return name.replace('/', '\\').lower()


def _fieldmap(db, rec):
    """{plain field name: [values]} for a record, or None if the record is absent."""
    ff = db.get_fields(rec)
    if ff is None:
        return None
    out = {}
    for key, tf in ff.items():
        name = key.split('###')[0]
        vals = tf.values if isinstance(tf.values, list) else [tf.values]
        out.setdefault(name, []).extend([v for v in vals if v is not None])
    return out


def _spawner_suppressed(db, rec):
    fm = _fieldmap(db, rec)
    return fm is not None and 'actorToSpawn' not in fm


def _carrier_suppressed(db, rec):
    fm = _fieldmap(db, rec)
    return (fm is not None
            and fm.get('startVisible') == [0]
            and fm.get('IncludeInMap') == [0])


def _portal_suppressed(db, rec):
    fm = _fieldmap(db, rec)
    if fm is None:
        return False
    req = {str(v) for v in fm.get('RequireDLC', [])}
    noreq = {str(v) for v in fm.get('RequireNoDLC', [])}
    return bool(req and noreq and (req & noreq))


def validate_db(db, label='<db>'):
    """Run every check against an in-memory ArzDatabase. Returns 0 PASS / 1 FAIL."""
    fails = []
    print('=== ATLANTIS SEA-VOYAGE CAP GATE: %s ===' % label)

    # ---- V1: the two DLCActorSpawner records -------------------------------
    for rec in SPAWNERS_CAPPED:
        short = rec.rsplit('\\', 1)[-1]
        fm = _fieldmap(db, rec)
        if fm is None:
            fails.append(
                'V1 %s is ABSENT from the mod .arz, so the BASE game record (which '
                'spawns the DLC actor) is what the player gets - the cap never ran, '
                'or a later pass deleted it.' % short)
            continue
        if 'actorToSpawn' in fm:
            fails.append('V1 %s still carries actorToSpawn = %s, so it still spawns '
                         'the DLC actor.' % (short, fm['actorToSpawn']))
            continue
        got = [str(v) for v in fm.get('dlcRequirement', [])]
        if got != [SPAWNER_DLC_REQUIREMENT]:
            fails.append('V1 %s dlcRequirement is %s, expected [%r] - the cap must '
                         'suppress the SPAWN, never widen the DLC gate.'
                         % (short, got, SPAWNER_DLC_REQUIREMENT))
            continue
        print('  V1 OK  %s present, actorToSpawn ABSENT (template default ""), '
              'dlcRequirement still %s' % (short, SPAWNER_DLC_REQUIREMENT))

    # ---- V2: the two boundary boat NPCs ------------------------------------
    for rec in HIDDEN_CARRIERS:
        short = rec.rsplit('\\', 1)[-1]
        fm = _fieldmap(db, rec)
        if fm is None:
            fails.append(
                'V2 %s is ABSENT from the mod .arz, so the BASE game record (a '
                'visible, travel-capable boat NPC) is what the player gets.' % short)
            continue
        sv, im = fm.get('startVisible'), fm.get('IncludeInMap')
        if sv != [0]:
            fails.append('V2 %s startVisible = %s (expected [0]) - the boat NPC is '
                         'visible and can be talked to.' % (short, sv))
        elif im != [0]:
            fails.append('V2 %s IncludeInMap = %s (expected [0]) - a hidden NPC with '
                         'a live map icon is the A5 minimap-ghost bug.' % (short, im))
        else:
            print('  V2 OK  %s startVisible=0, IncludeInMap=0 (hidden, no map ghost)'
                  % short)

    # ---- V3: the two Tartarus act portals ----------------------------------
    for rec in TARTARUS_PORTALS:
        short = rec.rsplit('\\', 1)[-1]
        fm = _fieldmap(db, rec)
        if fm is None:
            fails.append('V3 %s is ABSENT from the mod .arz, so the BASE game portal '
                         'record is what the player gets.' % short)
            continue
        if not _portal_suppressed(db, rec):
            fails.append(
                'V3 %s has no AND-unsatisfiable DLC gate (RequireDLC=%s '
                'RequireNoDLC=%s); the Tartarus act portal can still spawn.'
                % (short, fm.get('RequireDLC'), fm.get('RequireNoDLC')))
            continue
        print('  V3 OK  %s RequireDLC=%s AND RequireNoDLC=%s (unsatisfiable)'
              % (short, fm.get('RequireDLC'), fm.get('RequireNoDLC')))

    # ---- V4: no collateral xpack3 override ---------------------------------
    strays = sorted(
        n for n in db.record_names()
        if _norm(n).startswith('records\\xpack3\\')
        and _norm(n) not in GOLDEN_XPACK3_OVERRIDES
        and not _MASTERY_PANECTRL.match(_norm(n)))
    if strays:
        fails.append('V4 the mod .arz overrides %d xpack3 record(s) outside the '
                     'golden allow-list: %s' % (len(strays), ', '.join(strays[:6])))
    else:
        print('  V4 OK  the only xpack3 records the mod overrides are this cap\'s %d '
              'and the mastery skill-panel controllers'
              % len(GOLDEN_XPACK3_OVERRIDES))

    # ---- V5: the derived route list ----------------------------------------
    resolvable = []
    for label_route, recs in ATLANTIS_TRANSIT_ROUTES:
        open_links = []
        for r in recs:
            if r in SPAWNERS_CAPPED:
                ok = _spawner_suppressed(db, r)
            elif r in HIDDEN_CARRIERS:
                ok = _carrier_suppressed(db, r)
            else:
                ok = _portal_suppressed(db, r)
            if not ok:
                open_links.append(r.rsplit('\\', 1)[-1])
        if open_links:
            resolvable.append('%s  [open link(s): %s]'
                              % (label_route, ', '.join(open_links)))
    if resolvable:
        fails.append('V5 %d resolvable Atlantis-transit route(s) remain:\n      - %s'
                     % (len(resolvable), '\n      - '.join(resolvable)))
    else:
        print('  V5 OK  resolvable Atlantis-transit routes = [] (all %d known routes '
              'closed at EVERY link)' % len(ATLANTIS_TRANSIT_ROUTES))

    if fails:
        print('\nRESULT: FAIL - %d check(s) failed' % len(fails))
        for f in fails:
            print('  FAIL: %s' % f)
        return 1
    print('\nRESULT: PASS - ZERO resolvable Atlantis-transit paths in this artifact; '
          'the campaign stays capped at Immortal Throne (Will 2026-07-10 / R-211).')
    return 0


def _plant(db, which):
    """Negative test: re-introduce a defect the gate must catch."""
    if which == 'respawn':
        db.set_field(MARINOS_SPAWNER, 'actorToSpawn',
                     r'Records\XPack3\Quests\NPC\Speaking\x3mq_Marinos_Rhodes.dbr',
                     DATA_TYPE_STRING)
        print('  [negtest] put actorToSpawn back on the Rhodes Marinos spawner')
    elif which == 'unhide':
        db.set_field(RHODES_BOATMAN, 'startVisible', 1)
        print('  [negtest] re-enabled the Rhodes captain (startVisible=1)')
    elif which == 'ungate':
        ff = db.get_fields(TARTARUS_PORTAL_CORINTH) or {}
        for k in list(ff):
            if k.split('###')[0] == 'RequireNoDLC':
                del ff[k]
        db._modified.add(TARTARUS_PORTAL_CORINTH)
        print('  [negtest] dropped RequireNoDLC from the Corinth Tartarus portal')
    elif which == 'overreach':
        from apply_svc_patches import _ensure_record
        stray = (r'records\xpack3\creatures\npc\teleporters'
                 r'\gadir_boatmantomalta.dbr')
        _ensure_record(db, stray, r'database\Templates\Npc.tpl')
        print('  [negtest] planted a collateral xpack3 override (%s)' % stray)


def validate(arz_path, plant=None):
    p = Path(arz_path)
    if not p.is_file():
        print('gate_atlantis_voyage_cap: no such .arz: %s' % p)
        return 2
    db = ArzDatabase.from_arz(p)
    if plant:
        _plant(db, plant)
    return validate_db(db, label=str(p))


def main(argv):
    args = argv[1:]
    if not args:
        print(__doc__)
        return 2
    neg = '--negtest' in args
    args = [a for a in args if a != '--negtest']
    if not args:
        print('usage: py tools/gate_atlantis_voyage_cap.py <arz> [--negtest]')
        return 2
    if not neg:
        return validate(args[0])

    ok = True
    for which in ('respawn', 'unhide', 'ungate', 'overreach'):
        print('\n--- NEGTEST: plant=%s ---' % which)
        rc = validate(args[0], plant=which)
        if rc == 0:
            print('NEGTEST %s: FAIL - the gate did NOT catch the planted defect'
                  % which)
            ok = False
        else:
            print('NEGTEST %s: PASS - the gate caught it' % which)
    print('\nNEGTEST RESULT: %s' % ('PASS - all 4 planted defects caught' if ok
                                    else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
