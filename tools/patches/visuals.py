#!/usr/bin/env python3
r"""build37 VISUALS registry module (patches-registry contract: MODULE_NAME + apply(db, tags)).

Spec: scratchpad/specs/visuals_and_livebugs_audit_spec.md (backlog #28 + #37 + B-PORTAL-1).
Binding: WILL_DECISIONS_2026-07-11.md, VISUALS section.

WHY THIS MODULE WRITES ZERO BYTES
---------------------------------
The build37 visuals item is a pure MAP-LANE wave. Every visible change is a Levels.arc
co-location (portal swirl FX) or set-piece placement (the caged Blood Demon tableau, the
Rhodes secret encounter), authored as additive 0x05 injects in the map tool. Those are owned
by the map lane and are enumerated below as the MAP_DELTAS manifest (reported, not applied
here). The wave's DB footprint is ZERO by spec: every record the map wave places is amgoz1's
own SV 0.98i content, already merged and resolving in SoulvizierClassic.arz, and the sign-off
default is explicitly "no arz/Text/Quests change" (Levels-only deploy). Writing any record here
would force an arz coupling the spec says must not exist, so this module writes nothing to
db or tags. That also makes it a perfect registry identity-proof contributor: it provably
changes zero bytes of the built arz.

WHAT IT DOES INSTEAD
--------------------
It is the wave's DB-side PRECONDITION INVARIANT. apply() fail-loud asserts that every record
the build37 visuals map wave co-locates or places resolves in the just-built arz with the
expected engine Class, and that the one secret door is inert (locked=0) so it cannot repeat the
B-TEMPLE-DOOR-1 locked-door-with-no-unlock hazard. If a future DB change drops or reclasses any
of these records, this guard stops the build before the map lane can inject a dangling DBR
(a documented map hazard). The authoritative map-delta list lives here in code (MAP_DELTAS) so
the map lane and the gates share one source of truth, and it is echoed to the build log.

Sprite-pit (Part A / B-SPRITE-1): NO DB change. The fix is to ship the already-in-map
2-spawner + Delphi pit density (build35 baseline) and have Will re-test; the ProxyPool respawn
driver lands only if it is still broken after the re-test (WILL_DECISIONS). The pit records are
guarded here read-only so the map wave's existing spawner injects keep resolving.

Portal look (B-PORTAL-1): DRX swirl FX co-location (records\drxmap\effects\objefx\
map_portal_aura.dbr, the DRX asset Will picked) at every flat-blue portal panel. The richer
mesh/class swap stays a later, coupled upgrade and is NOT done here (WILL_DECISIONS).
"""

MODULE_NAME = 'visuals'

# ---------------------------------------------------------------------------
# DB-SIDE PRECONDITION INVARIANT
# Every record the build37 visuals map wave co-locates/places must resolve with
# this Class. (field, expected) pairs add an extra byte-level assert; expected
# None means "field must be present/non-None" only.
#   role: 'core'   -> map wave places it in the default wave  -> fail-loud
#         'sprite' -> Part A pit chain (no DB change)          -> fail-loud (must keep resolving)
#         'optional'-> mystic_rhodes (default SKIP placement)  -> fail-loud (record still must resolve)
# ---------------------------------------------------------------------------
REQUIRED_RECORDS = [
    # --- B-PORTAL-1 swirl FX + the two born-open portal classes it decorates ---
    (r'records\drxmap\effects\objefx\map_portal_aura.dbr', 'EffectEntity', [], 'core',
     'DRX portal-swirl FX; co-located at each flat-blue portal (Will pick)'),
    (r'records\quests\portal_olympianarena1.dbr', 'GridEntrance', [], 'core',
     'outbound portal; the flat-blue-panel offender the swirl masks'),
    (r'records\quests\portal_olympianarena2.dbr', 'GridExitOneWay', [], 'core',
     'return-side landing; swirl is a cosmetic marker only (not a B-PORTAL-3 fix)'),
    # --- Part B TIER 1: the caged Blood Demon tableau at the Delphi occult tent ---
    (r'records\drxmap\dress\blooddemon_medium01.dbr', 'Npc', [], 'core',
     'Idling Blood Demon; completes amgoz1 "occultist binds demons" tableau (cages already placed)'),
    (r'records\drxmap\dress\qi_tomeofhealing01.dbr', 'Decoration', [], 'core',
     "occultist's healing tome on the tent table"),
    (r'records\drxmap\dress\scrolls.dbr', 'Decoration', [], 'core',
     "occultist's scrolls on the tent table"),
    # --- Part B TIER 2: the Rhodes-underground secret encounter ---
    (r'records\drxmap\xurder\dng_bossroom_secretdoor.dbr', 'FixedItemDoor', [('locked', 0)], 'core',
     'hidden boss-room wall-reveal; locked=0 -> inert-safe, no unlock quest needed'),
    (r'records\drxcreatures\crowheroes\jiaco.dbr', 'Monster', [('monsterClassification', 'Quest')], 'core',
     'one-time named crow hero "Jiaco"'),
    # --- Part B OPTIONAL: redundant early-Greece respec NPC (default SKIP placement) ---
    (r'records\xpack\creatures\npc\mystics\mystic_rhodes.dbr', 'NpcSkillReallocator', [], 'optional',
     'skill-reallocator already live at 2 other spots; valley04 copy is a nice-to-have'),
    # --- Part A: sprite-pit chain (no DB change; guarded so map spawner injects keep resolving) ---
    (r'records\drxmap\pitsprites\t1_pitspawner_01.dbr', 'Monster', [], 'sprite',
     'invincible stationary seeder (Delphi + HVBorder04 pits)'),
    (r'records\drxmap\pitsprites\t1_pitspawner_02.dbr', 'Monster', [], 'sprite',
     'second seeder of the SV-density 2-spawner pit'),
    (r'records\drxmap\pitsprites\t1_skill_pitspawner_lildude_0x.dbr', 'Skill_SpawnPetMonster', [], 'sprite',
     'primary continuous seeder (buffSelf, 0 mana, 12s)'),
    (r'records\drxmap\pitsprites\t1_lildude_01.dbr', 'Monster', [], 'sprite', 'exploding 1-HP suicide sprite'),
    (r'records\drxmap\pitsprites\t1_lildude_02.dbr', 'Monster', [], 'sprite', 'exploding 1-HP suicide sprite'),
    (r'records\drxmap\pitsprites\t1_lildude_03.dbr', 'Monster', [], 'sprite', 'exploding 1-HP suicide sprite'),
]

# ---------------------------------------------------------------------------
# MAP-DELTA MANIFEST (Levels.arc, owned by the map lane; reported, NOT applied here)
# Every entry is an additive 0x05 inject, flags=0, identity rot, no 0x14 (the proven
# append-only v0x11 path; atmosphere/prop/NPC/inert-door are all flags=0 in SV). Coords
# are SV-LOCAL (shared levels are not grid-shifted). Each dict:
#   host  : exact LEVELS-index fname key (load-bearing; two valley04.lvl exist)
#   dbr   : record path
#   xyz   : SV-local coord (float32)
#   action: 'append' (into an existing INJECT_SPECS block) | 'new-block' | 'colocate'
#   note  : intent
# ---------------------------------------------------------------------------
AURA_DBR = r'records\drxmap\effects\objefx\map_portal_aura.dbr'

MAP_DELTAS = {
    # === PART C / B-PORTAL-1: 11 swirl co-locations at the 11 aura-less portals ===
    # 5 outbound GridEntrance (portal_olympianarena1) = the actual flat-blue-panel fix:
    'portal_aura': [
        {'host': 'levels/world/greece/knossos/underground/maze03.lvl',
         'dbr': AURA_DBR, 'xyz': (290.70, 1.20, 152.50), 'action': 'colocate',
         'note': 'aura at maze03 -> UberDungeon GridEntrance (P1)'},
        {'host': 'levels/world/greece/athens/underground/catacube02_floorlast.lvl',
         'dbr': AURA_DBR, 'xyz': (20.00, 1.20, 46.00), 'action': 'colocate',
         'note': 'aura at Sparta-crypt GridEntrance (P1)'},
        {'host': 'xpack/levels/area01_rhodes/rhodes_secretvista_01.lvl',
         'dbr': AURA_DBR, 'xyz': (138.50, 18.40, 33.10), 'action': 'colocate',
         'note': 'aura at Secret-Place S1 GridEntrance (P1)'},
        {'host': 'xpack/levels/secret_place/darkforestenter.lvl',
         'dbr': AURA_DBR, 'xyz': (17.90, 7.00, 38.50), 'action': 'colocate',
         'note': 'aura at Secret-Place S3 GridEntrance (P1)'},
        {'host': 'levels/world/olympus/gardenofmerchants.lvl',
         'dbr': AURA_DBR, 'xyz': (142.30, -39.00, 79.10), 'action': 'colocate',
         'note': 'aura at Garden G3 GridEntrance (P1)'},
        # 6 return-side GridExitOneWay (portal_olympianarena2) = cosmetic markers:
        {'host': 'levels/world/orient/silkroad/hiddenvalley01.lvl',
         'dbr': AURA_DBR, 'xyz': (56.90, 17.60, 138.10), 'action': 'colocate',
         'note': 'aura at Garden G4 return landing (P2)'},
        {'host': 'xpack/levels/area01_rhodes/rhodes_secretvista_01.lvl',
         'dbr': AURA_DBR, 'xyz': (137.10, 17.00, 43.10), 'action': 'colocate',
         'note': 'aura at Secret-Place S4 return landing (P2)'},
        {'host': 'xpack/levels/secret_place/darkforestenter.lvl',
         'dbr': AURA_DBR, 'xyz': (23.90, 2.00, 30.50), 'action': 'colocate',
         'note': 'aura at Secret-Place S2 return landing (P2)'},
        {'host': 'levels/world/olympus/gardenofmerchants.lvl',
         'dbr': AURA_DBR, 'xyz': (130.30, -39.00, 79.10), 'action': 'colocate',
         'note': 'aura at Garden G2 return landing (P2)'},
        {'host': 'levels/world/olympus/gardenofmerchants.lvl',
         'dbr': AURA_DBR, 'xyz': (130.30, -39.00, 73.10), 'action': 'colocate',
         'note': 'aura at Helos H2 return landing (P2)'},
        {'host': 'levels/world/greece/startingtownver2/startingfarmland06d.lvl',
         'dbr': AURA_DBR, 'xyz': (68.00, -0.40, 181.00), 'action': 'colocate',
         'note': 'aura at Helos H1 return landing (P2)'},
    ],
    # === PART B TIER 1: caged Blood Demon + tent props (APPEND to existing occult block) ===
    'tier1_delphi': [
        {'host': 'levels/world/greece/delphi/delphilowlands04.lvl',
         'dbr': r'records\drxmap\dress\blooddemon_medium01.dbr', 'xyz': (1.967, 10.062, 12.120),
         'action': 'append', 'note': 'Idling Blood Demon inside the already-placed medium cage'},
        {'host': 'levels/world/greece/delphi/delphilowlands04.lvl',
         'dbr': r'records\drxmap\dress\qi_tomeofhealing01.dbr', 'xyz': (10.172, 11.449, 1.148),
         'action': 'append', 'note': "occultist's healing tome on the table"},
        {'host': 'levels/world/greece/delphi/delphilowlands04.lvl',
         'dbr': r'records\drxmap\dress\scrolls.dbr', 'xyz': (11.348, 9.325, 1.253),
         'action': 'append', 'note': "occultist's scrolls on the table"},
    ],
    # === PART B TIER 2: Rhodes secret encounter (NEW INJECT_SPECS block) ===
    'tier2_rhodes': [
        {'host': 'xpack/levels/area01_rhodes/undergrounds/scrabledeggs_floor06.lvl',
         'dbr': r'records\drxmap\xurder\dng_bossroom_secretdoor.dbr', 'xyz': (10.930, -0.040, 53.950),
         'action': 'new-block', 'note': 'hidden boss-room door (FixedItemDoor, locked=0 inert)'},
        {'host': 'xpack/levels/area01_rhodes/undergrounds/scrabledeggs_floor06.lvl',
         'dbr': r'records\drxcreatures\crowheroes\jiaco.dbr', 'xyz': (47.180, 0.590, 68.680),
         'action': 'new-block', 'note': 'crow hero "Jiaco" (Monster, Quest-class one-time)'},
    ],
    # === PART B OPTIONAL: redundant early-Greece respec NPC (default SKIP) ===
    'optional_mystic': [
        {'host': 'levels/world/greece/area002/valley04.lvl',
         'dbr': r'records\xpack\creatures\npc\mystics\mystic_rhodes.dbr', 'xyz': (125.790, 25.830, 51.920),
         'action': 'new-block', 'note': 'OPTIONAL respec NPC; greece/area002 valley04 (full path load-bearing)'},
    ],
}

# Per-host parseback +N expectation (gate_build32_parseback extension), default wave
# (optional_mystic EXCLUDED). Every OTHER section (0x0b/0x06/0x14) stays byte-identical.
PARSEBACK_EXPECT = {
    'levels/world/greece/delphi/delphilowlands04.lvl': 3,
    'xpack/levels/area01_rhodes/undergrounds/scrabledeggs_floor06.lvl': 2,
    'levels/world/orient/silkroad/hiddenvalley01.lvl': 1,
    'levels/world/greece/knossos/underground/maze03.lvl': 1,
    'levels/world/greece/athens/underground/catacube02_floorlast.lvl': 1,
    'xpack/levels/area01_rhodes/rhodes_secretvista_01.lvl': 2,
    'xpack/levels/secret_place/darkforestenter.lvl': 2,
    'levels/world/olympus/gardenofmerchants.lvl': 3,
    'levels/world/greece/startingtownver2/startingfarmland06d.lvl': 1,
    # + 'levels/world/greece/area002/valley04.lvl': 1  # only if optional_mystic taken
}


def _resolves(db, path):
    """True if the record exists in the arz (accepts \\ or / separators, case-exact)."""
    if hasattr(db, 'has_record') and db.has_record(path):
        return True
    alt = path.replace('\\', '/') if '\\' in path else path.replace('/', '\\')
    return hasattr(db, 'has_record') and db.has_record(alt)


def _class_of(db, path):
    for p in (path, path.replace('\\', '/'), path.replace('/', '\\')):
        c = db.get_field_value(p, 'Class')
        if c is not None:
            return c[0] if isinstance(c, list) and c else c
    return None


def _field(db, path, field):
    for p in (path, path.replace('\\', '/'), path.replace('/', '\\')):
        v = db.get_field_value(p, field)
        if v is not None:
            return v[0] if isinstance(v, list) and v else v
    return None


def apply(db, tags):
    """Fail-loud DB precondition invariant for the build37 visuals map wave.

    Writes NOTHING to db/tags (arz identity preserved; wave stays Levels-only). Asserts every
    record the map wave co-locates/places resolves with the expected Class + inert-door check.
    Echoes the map-delta manifest to the build log so it rides in the build record.
    """
    failures = []
    for path, exp_cls, checks, role, _note in REQUIRED_RECORDS:
        if not _resolves(db, path):
            failures.append('MISSING record: %s (%s)' % (path, role))
            continue
        cls = _class_of(db, path)
        if exp_cls and (cls is None or exp_cls.lower() not in str(cls).lower()):
            failures.append('WRONG Class: %s -> %r (expected %s)' % (path, cls, exp_cls))
        for fname, expv in checks:
            got = _field(db, path, fname)
            if expv is None:
                if got is None:
                    failures.append('MISSING field %s on %s' % (fname, path))
            elif got != expv:
                failures.append('FIELD %s on %s = %r (expected %r)' % (fname, path, got, expv))

    if failures:
        raise SystemExit(
            '[patches.visuals] build37 visuals DB precondition FAILED - the map wave would inject '
            'dangling/mis-classed DBRs:\n  ' + '\n  '.join(failures))

    n_deltas = sum(len(v) for k, v in MAP_DELTAS.items() if k != 'optional_mystic')
    print('[patches.visuals] OK - %d records resolve (portal FX + portal classes + TIER1 + TIER2 '
          '+ sprite chain + optional mystic); arz byte-unchanged.' % len(REQUIRED_RECORDS))
    print('[patches.visuals] MAP-DELTA manifest (Levels.arc, map lane owns): %d default injects '
          '(+1 if optional mystic_rhodes taken):' % n_deltas)
    for group, deltas in MAP_DELTAS.items():
        opt = ' [OPTIONAL, default SKIP]' if group == 'optional_mystic' else ''
        print('    %s%s: %d' % (group, opt, len(deltas)))
    print('[patches.visuals] parseback +N per host (default wave): ' +
          ', '.join('%s +%d' % (h.split('/')[-1], n) for h, n in PARSEBACK_EXPECT.items()))
    # This module deliberately does not touch `tags` (no Text change in the visuals default path).
    return {'module': MODULE_NAME, 'records_guarded': len(REQUIRED_RECORDS),
            'map_deltas_default': n_deltas, 'arz_bytes_written': 0}


if __name__ == '__main__':
    # Standalone self-check against the current built arz (no build needed).
    import sys
    from pathlib import Path
    WT = Path(__file__).resolve().parents[2]
    MAIN = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
    # tools/ lives in the worktree; the built arz (work/, gitignored) only in the main checkout.
    sys.path.insert(0, str((WT / 'tools')))
    sys.path.insert(0, str((MAIN / 'tools')))
    from arz_patcher import ArzDatabase
    candidates = [WT / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz',
                  MAIN / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz']
    arz = next((c for c in candidates if c.exists()), candidates[-1])
    print('self-check arz =', arz)
    db = ArzDatabase.from_arz(arz)
    print(apply(db, {}))
