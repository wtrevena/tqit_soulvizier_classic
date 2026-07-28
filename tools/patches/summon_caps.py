r"""summon_caps - restore the missing spawn-TTL on the unbounded boss-summon skills
that make the sepulcher / tomb-guardian chain accumulate entities without bound (b76).

WHY THIS EXISTS (RCA: docs/reports/b76_chumbi_freeze_rca.md)
------------------------------------------------------------
Will (2026-07-16, P0): "so much lag with the monsters ... the game is frozen ... the
infinite summon of the skeleton dog guys tomb guardian ... the uber boss whos name has
sepulcher in it ... the summon issue is also an issue, both are making the game freeze."

The named boss is `um_voranthys_99` (records\creature\monster\questbosses\), the apex
Obsidian uber. Its signature skill is `sepulchralwyrm_firebreath` ("sepulcher") and b39's
`boss_skill_fix` ENABLED its three previously-dormant (skillLevel-0, never-fired) summon
specials:
  * aktaios_summontombguardians  -> aktaios_tombguardian_21/24/27   (the "tomb guardians")
  * alastor_summonskeletonwarrior -> alastor_skeletonsoldier_07     (the "skeleton guys")
  * alastor_summonskeletonarcher  -> alastor_skeletonarcher_07
Every one of these summon SKILLS carries a petLimit (a single-digit CONCURRENT cap: 9/8/8)
but has **NO `spawnObjectsTimeToLive`** - so summoned minions are PERMANENT. With no TTL the
boss re-summons on cooldown the instant a minion dies to refill the cap, the fight never
reaches a steady state, and dead-minion corpses + summon FX accumulate. Stacked with the b76
Monster Test Yard (10 such bosses in one HiddenValley01 spot - REMOVED in the map lane), it
froze the game; but even STANDING ALONE a permanent-summon Voranthys degrades over a long
fight. The recursive `summonpet_undeadmelee01` (the skeleton priest's own summon: petLimit 5,
3s cooldown, NO TTL) is the same defect one hop deeper.

VANILLA CONVENTION (the fix is a RESTORATION, not an invention)
---------------------------------------------------------------
SV 0.98i's OWN variant of the identical tomb-guardian skill,
`records\skills\sv\shodema\aktaios_summontombguardians.dbr`, ships
`spawnObjectsTimeToLive = 5.0` (+ petLimit 3). And this repo's own `four_generals` archer
musters deliberately add `spawnObjectsTimeToLive = 20.0` ("finite TTL (quest-safe)") to a
donor that lacked one. So a finite TTL on a boss summon is the established, precedent-backed
convention here; the `boss skills\` copies of these skills simply lost it.

WHAT THIS MODULE DOES (ADDITIVE - one field, fully reversible)
-------------------------------------------------------------
Adds `spawnObjectsTimeToLive` to each unbounded boss-summon skill in the sepulcher/
tomb-guardian chain, at a precedent-matched value. It does NOT touch petLimit (already a
single-digit hard concurrent cap, vanilla-shipped), spawnObjects, cooldown, or any pet
record - so the CONCURRENT cap and the summon roster are unchanged; the minions now simply
despawn on their own instead of persisting forever. Idempotent (skips any skill that already
carries a positive TTL). Fail-loud if a listed skill record is absent.

SHARED-SKILL NOTE (honest scope): aktaios_summontombguardians / alastor_summonskeleton* are
ALSO used by the base Egypt-telkine Aktaios and the base necromancer Alastor. Adding a TTL
there is an intended, SV-aligned side effect (their summoned minions now self-despawn, exactly
as SV's shodema tomb-guardian variant already does) - a mild improvement, never a difficulty
cut (the boss keeps re-summoning on cooldown up to the same petLimit). The `um_*_99` apex
pet FAMILIES (aktaios_tombguardian_*, alastor_skeleton*) are NOT edited (a parallel lane owns
boss-summon pet families); only the SKILL's TTL field is set.

⚠️ WILL-VETO: the TTL values (tomb guardians 5.0 = SV shodema; skeletons 20.0 = four_generals
precedent). Bump/lower freely - the fix is the PRESENCE of a finite TTL, not the exact second.
"""
from pathlib import Path
import sys

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))
from arz_patcher import DATA_TYPE_FLOAT  # noqa: E402

MODULE_NAME = 'summon_caps'

# skill path -> intended spawnObjectsTimeToLive (seconds). Precedent cited in the docstring.
# All are Skill_*SpawnPet* records in the sepulcher / tomb-guardian summon chain that ship a
# single-digit petLimit but NO TTL (the b76 unbounded-accumulation offenders).
_TTL_TARGETS = {
    r'records\skills\boss skills\aktaios_summontombguardians.dbr': 5.0,   # SV shodema value
    r'records\skills\boss skills\alastor_summonskeletonwarrior.dbr': 20.0,  # four_generals precedent
    r'records\skills\boss skills\alastor_summonskeletonarcher.dbr': 20.0,
    r'records\skills\monster skills\summonpet_undeadmelee01.dbr': 20.0,   # recursive skeleton-priest summon
}

# a positive TTL is "capped"; treat <=0 / absent as uncapped.
_TTL_FIELD = 'spawnObjectsTimeToLive'


# ---------------------------------------------------------------------------
# B76 ROUND 2: the class gate (was a diagnostic; promoted 2026-07-28)
# ---------------------------------------------------------------------------
# WHY THIS EXISTS. verify() above only re-asserts the FOUR known sepulcher-chain
# targets, so a brand-new unbounded fast summoner - the Chumbi-Valley freeze class
# Will hit as a P0 - would ship unnoticed. sweep_uncapped() found the class but was
# labelled "DIAGNOSTIC (not a build gate)". It is now a gate with a curated waiver.
#
# WHAT THE GATE IS NOT. It is deliberately NOT "petLimit without a TTL": ~140 HEALTHY
# skills have exactly that shape (a single-digit CONCURRENT cap is itself a bound, and
# the vanilla convention for many pets is a permanent minion under a hard cap). Firing
# on that would be a false-positive machine and the gate would be whitelisted to death.
# The gated shape is the genuinely unbounded one sweep_uncapped() already encodes:
#     Skill_*SpawnPet*  AND  no positive petLimit  AND  no positive TTL  AND  cd < 10s
# i.e. nothing bounds the concurrent count, nothing expires a minion, and the summon
# re-fires fast enough to accumulate without limit.
#
# THE WAIVER. Seeded with EXACTLY the 8 records the b76 sweep found on the shipped arz
# (2026-07-28 re-run: still exactly 8, no drift), each verified individually - base-game
# or upstream-inherited, dead or test, and NONE placed. Evidence per record below.
# Anything NEW fails the build loud. Adding an entry here needs the same evidence:
# provenance, who references it, and whether it is placed in the world map.
_UNCAPPED_WAIVERS = {
    # -- base-game E3-demo leftover: spawns "E3 Demo Monsters\GoldenSkeleton", a
    #    pre-release asset. Present in the stock TQAE database.arz (inherited debt, not
    #    ours to fix); referenced by 0 records in the shipped arz; not placed.
    r'records\skills\boss skills\telkine_projectilespawnpet.dbr':
        'BASE-GAME (in stock database.arz); spawns the E3-demo GoldenSkeleton; '
        '0 referencing records; not placed in the world map.',
    # -- the DRX/SV duplicate-path twin of the record above (the `records\skills\skills\`
    #    namespace duplication that pervades the upstream merges). Same content.
    r'records\skills\skills\boss skills\telkine_projectilespawnpet.dbr':
        'duplicate-path twin of records\\skills\\boss skills\\telkine_projectilespawnpet.dbr '
        '(upstream `records\\skills\\skills\\` namespace duplication); 0 referencing '
        'records; not placed.',
    # -- base-game retired pre-release Nature mastery (`\old\` namespace).
    r'records\skills\nature\old\oldnaturemastery_animalcompanion.dbr':
        'BASE-GAME (in stock database.arz); `\\old\\` = the retired pre-release Nature '
        'mastery; 0 referencing records; not placed.',
    r'records\skills\skills\nature\old\oldnaturemastery_animalcompanion.dbr':
        'duplicate-path twin of records\\skills\\nature\\old\\oldnaturemastery_animalcompanion'
        '.dbr; 0 referencing records; not placed.',
    # -- upstream event-summoning content. Absent from the stock arz (mod-inherited, not
    #    authored here). Explicit ttl=0.0. Neither the skill nor its spawner appears
    #    ANYWHERE in the 2.09 GB world blob - verified by whole-blob scan, 0 hits - so
    #    no placed entity can ever fire them.
    r'records\events\summoning\01_skill_zombiemelee_swarm_a.dbr':
        'upstream event content (absent from the stock arz); ttl=0.0; 0 referencing '
        'records; not placed (whole-world-blob scan, 0 hits).',
    r'records\events\summoning\01_skill_zombiemelee_swarm_a_1sec_cd.dbr':
        'upstream event content (absent from the stock arz); ttl=0.0; the ONLY waived '
        'record with a live reference (records\\events\\spawners\\zombie\\'
        '01_spawner_zombiemelee_swarm_a.dbr buffSelfSkillName + skillName2) - but that '
        'spawner is itself NOT placed: a whole-world-blob scan of Levels.arc finds 0 '
        'hits for the spawner, the skill, or the substring "zombiemelee_swarm". Nothing '
        'in the shipped world can instantiate it.',
    # -- DRX authoring leftover: the filename is literally "copy (2) of".
    r'records\skills\nature\copy (2) of drxregrowth.dbr':
        'DRX authoring leftover (the filename is literally "copy (2) of"); 0 referencing '
        'records; not placed.',
    # -- a `\test\` namespace bait record.
    r'records\skills\earth\test\stoneform_spawn_bait.dbr':
        '`\\test\\` namespace bait record; 0 referencing records; not placed.',
}


def _norm_rec(p):
    return str(p).replace('/', '\\').strip().lower()


_UNCAPPED_WAIVERS_NORM = {_norm_rec(k): v for k, v in _UNCAPPED_WAIVERS.items()}


def _ttl_of(db, rec):
    v = db.get_field_value(rec, _TTL_FIELD)
    if isinstance(v, list):
        v = v[0] if v else None
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _is_spawn_skill(db, rec):
    cls = db.get_field_value(rec, 'Class')
    if isinstance(cls, list):
        cls = cls[0] if cls else None
    return isinstance(cls, str) and 'spawnpet' in cls.lower().replace(' ', '')


def apply(db, tags=None):
    changed = []
    for skill, ttl in _TTL_TARGETS.items():
        if not db.has_record(skill):
            raise SystemExit(
                "summon_caps: target skill '%s' absent from the arz - the sepulcher "
                "summon chain moved; re-run the b76 RCA sweep before shipping." % skill)
        if not _is_spawn_skill(db, skill):
            raise SystemExit(
                "summon_caps: target '%s' is not a SpawnPet skill (Class=%r) - refusing "
                "to add a spawn TTL to a non-summon record." % (skill, db.get_field_value(skill, 'Class')))
        cur = _ttl_of(db, skill)
        if cur is not None and cur > 0:
            changed.append((skill, cur, cur, 'already-capped'))
            continue
        db.set_field(skill, _TTL_FIELD, float(ttl), DATA_TYPE_FLOAT)
        db._modified.add(skill)
        changed.append((skill, cur, float(ttl), 'TTL-added'))
    print("=== summon_caps: restored finite spawn-TTL on %d boss-summon skills (b76) ===" %
          sum(1 for c in changed if c[3] == 'TTL-added'))
    for skill, old, new, how in changed:
        print("  %-12s %-60s  %s -> %.1fs" % (how, skill.split('\\')[-1], old, new))
    return tags


def check_no_new_unbounded(db, cooldown_max=10.0):
    """B76 round-2 CLASS GATE (was a diagnostic). Returns (offenders, stale_waivers).

    `offenders` = every record sweep_uncapped() flags that is NOT in _UNCAPPED_WAIVERS -
    i.e. a NEW unbounded fast summoner. Non-empty means the build must die.
    `stale_waivers` = waived records the sweep no longer flags (they were capped, renamed
    or dropped upstream). Reported as hygiene, never fatal, and never auto-removed: the
    RETIREMENT PROTOCOL says "unreferenced" is not sufficient grounds to delete a record
    of intent, and the same applies to the evidence attached to a waiver.

    Split out of verify() so the planted negative test can exercise the class gate on a
    synthetic db without the four real sepulcher targets."""
    flagged = {_norm_rec(r): (r, cd, pl, ttl) for r, cd, pl, ttl in
               sweep_uncapped(db, cooldown_max=cooldown_max)}
    offenders = [v for k, v in sorted(flagged.items()) if k not in _UNCAPPED_WAIVERS_NORM]
    stale = sorted(k for k in _UNCAPPED_WAIVERS_NORM if k not in flagged)
    return offenders, stale


def verify(db, tags=None):
    """Fail-loud, TWO invariants (last-writer semantics - reads the FINAL record state):

    (1) TARGETED: every sepulcher-chain skill this module caps must carry a positive
        spawn TTL in the final arz (the original b76 check).
    (2) CLASS (b76 round 2, 2026-07-28): no NEW unbounded fast summoner anywhere in the
        arz. See _UNCAPPED_WAIVERS for the shape gated, why it is NOT a blanket
        "petLimit without TTL" rule, and the per-record evidence for the 8 seeded
        waivers. This is the half that would actually catch the next Chumbi-Valley
        freeze class - (1) alone only re-checks four records we already knew about."""
    bad = []
    for skill in _TTL_TARGETS:
        if not db.has_record(skill):
            bad.append((skill, 'MISSING'))
            continue
        ttl = _ttl_of(db, skill)
        if ttl is None or ttl <= 0:
            bad.append((skill, 'UNCAPPED ttl=%r' % ttl))
    if bad:
        raise SystemExit("summon_caps.verify FAIL - uncapped sepulcher-chain summon "
                         "skills survived to the final arz:\n" +
                         '\n'.join('  %s  (%s)' % b for b in bad))
    print("  summon_caps.verify: %d sepulcher-chain summon skills all carry a finite "
          "spawn-TTL (b76)" % len(_TTL_TARGETS))

    offenders, stale = check_no_new_unbounded(db)
    if offenders:
        raise SystemExit(
            "summon_caps.verify FAIL - %d NEW UNBOUNDED FAST SUMMONER(S) in the final arz "
            "(Skill_*SpawnPet* with NO petLimit, NO spawnObjectsTimeToLive and cooldown "
            "< 10s = minions accumulate without bound; this is the b76 Chumbi-Valley "
            "freeze class Will hit as a P0):\n" % len(offenders) +
            '\n'.join('  %-72s cd=%.2f petLimit=%r ttl=%r' % (r, cd, pl, ttl)
                      for r, cd, pl, ttl in offenders) +
            "\n\nFIX (in this order):\n"
            "  1. give the skill a finite spawnObjectsTimeToLive (the SV/vanilla convention -\n"
            "     see this module's _TTL_TARGETS and their cited precedents), or a positive\n"
            "     petLimit if a hard CONCURRENT cap is the right bound; or\n"
            "  2. if it is genuinely dead/base/test content, add it to _UNCAPPED_WAIVERS with\n"
            "     the SAME evidence the 8 seeded entries carry: provenance (in the stock arz or\n"
            "     not), how many records reference it, and whether it is placed in the world map.\n"
            "     A waiver without that evidence is not acceptable.")
    print("  summon_caps.verify: no new unbounded fast summoners (%d waived: base/dead/test, "
          "each evidenced)" % len(_UNCAPPED_WAIVERS_NORM))
    if stale:
        print("    NOTE: %d waiver(s) no longer flagged by the sweep (capped/renamed/dropped "
              "upstream). Kept, not auto-removed - retirement protocol:" % len(stale))
        for s in stale:
            print("      %s" % s)


def sweep_uncapped(db, cooldown_max=10.0):
    """The classifier behind the B76 round-2 class gate (promoted from DIAGNOSTIC to a
    build gate on 2026-07-28 - see check_no_new_unbounded + _UNCAPPED_WAIVERS).

    Every Skill_*SpawnPet* record with a short cooldown (< cooldown_max) that has
    NEITHER a positive petLimit NOR a positive spawnObjectsTimeToLive - the unbounded-
    summoner pattern. Deliberately narrower than "petLimit without a TTL", which ~140
    HEALTHY skills legitimately are. Returns [(rec, cd, petLimit, ttl)]."""
    out = []
    for rec in db.record_names():
        if not _is_spawn_skill(db, rec):
            continue
        pl = db.get_field_value(rec, 'petLimit')
        pl = (pl[0] if isinstance(pl, list) and pl else pl)
        ttl = _ttl_of(db, rec)
        cd = db.get_field_value(rec, 'skillCooldownTime')
        cd = (cd[0] if isinstance(cd, list) and cd else cd) or 0.0
        try:
            cd = float(cd)
        except (TypeError, ValueError):
            cd = 0.0
        capped_conc = isinstance(pl, (int, float)) and pl and pl > 0
        capped_ttl = ttl is not None and ttl > 0
        if not capped_conc and not capped_ttl and cd < cooldown_max:
            out.append((rec, cd, pl, ttl))
    return out


def _mk_spawn_skill(db, rec, cooldown=1.0, pet_limit=None, ttl=None,
                    cls='Skill_SpawnPetMonster'):
    """Plant a synthetic SpawnPet skill into a throwaway db. Registers it in the raw-record
    index (so record_names/has_record see it) and seeds the decode cache (so get_fields
    returns the synthetic fields without a decompress)."""
    from collections import OrderedDict
    from arz_patcher import TypedField, DATA_TYPE_STRING, DATA_TYPE_INT
    fields = OrderedDict([
        ('Class', TypedField(DATA_TYPE_STRING, [cls])),
        ('spawnObjects', TypedField(DATA_TYPE_STRING, [r'records\creature\monster\x.dbr'])),
        ('skillCooldownTime', TypedField(DATA_TYPE_FLOAT, [float(cooldown)])),
    ])
    if pet_limit is not None:
        fields['petLimit'] = TypedField(DATA_TYPE_INT, [int(pet_limit)])
    if ttl is not None:
        fields['spawnObjectsTimeToLive'] = TypedField(DATA_TYPE_FLOAT, [float(ttl)])
    db._raw_records[rec] = ('Skill', b'')
    db._decoded_cache[rec] = fields
    return rec


def _negtest():
    """PLANTED NEGATIVE TESTS for both halves of this module. Run:
        py tools/patches/summon_caps.py --negtest

    Half 1 (original, b76): sweep_uncapped flags an uncapped fast summoner and clears it
    once a TTL is added.
    Half 2 (b76 ROUND 2, 2026-07-28): the promoted CLASS GATE. Planting a NEW unbounded
    fast summoner must make check_no_new_unbounded report it and verify() KILL the build;
    a WAIVED record must not; and the healthy shapes ~140 real skills have (petLimit
    without a TTL; a long cooldown) must NOT be flagged - the false-positive guard that
    keeps this from becoming a blanket petLimit-no-TTL rule."""
    from arz_patcher import ArzDatabase
    ok = True

    def check(label, cond, extra=''):
        nonlocal ok
        ok &= bool(cond)
        print('  [%s] %s%s' % ('PASS' if cond else 'FAIL', label,
                              ('  -- ' + extra) if (extra and not cond) else ''))

    print('=== summon_caps planted negative tests ===')
    print(' half 1: the classifier (b76)')
    db = ArzDatabase()
    rec = _mk_spawn_skill(db, r'records\skills\_negtest\uncapped_fast_summoner.dbr')
    check('uncapped fast summoner is flagged',
          any(r[0] == rec for r in sweep_uncapped(db)))
    db.set_field(rec, 'spawnObjectsTimeToLive', 5.0, DATA_TYPE_FLOAT)
    check('TTL-capped summoner clears',
          not any(r[0] == rec for r in sweep_uncapped(db)))

    print(' half 2: the CLASS GATE (b76 round 2)')
    # A: a NEW unbounded fast summoner must be reported as an offender.
    db2 = ArzDatabase()
    new = _mk_spawn_skill(db2, r'records\skills\_negtest\brand_new_unbounded_summoner.dbr',
                          cooldown=1.5)
    offs, stale = check_no_new_unbounded(db2)
    check('A new unbounded fast summoner is an OFFENDER',
          [o[0] for o in offs] == [new], str(offs))

    # B: and verify() must KILL the build on it (not just report).
    db3 = ArzDatabase()
    for skill, ttl in _TTL_TARGETS.items():           # satisfy invariant (1) first, so
        _mk_spawn_skill(db3, skill, cooldown=1.0, ttl=ttl)   # (2) is what fails
    _mk_spawn_skill(db3, r'records\skills\_negtest\brand_new_unbounded_summoner.dbr',
                    cooldown=1.5)
    try:
        verify(db3)
        check('B verify() dies on a new unbounded summoner', False, 'no SystemExit raised')
    except SystemExit as ex:
        msg = str(ex)
        check('B verify() dies on a new unbounded summoner',
              'brand_new_unbounded_summoner' in msg and 'UNBOUNDED' in msg, msg[:200])

    # C: a WAIVED record in the same shape must NOT trip the gate...
    db4 = ArzDatabase()
    waived = next(iter(_UNCAPPED_WAIVERS))
    _mk_spawn_skill(db4, waived, cooldown=0.0)
    offs4, _ = check_no_new_unbounded(db4)
    check('C waived record does NOT trip the gate', offs4 == [], str(offs4))

    # ...and verify() must pass cleanly with only waived offenders present.
    db5 = ArzDatabase()
    for skill, ttl in _TTL_TARGETS.items():
        _mk_spawn_skill(db5, skill, cooldown=1.0, ttl=ttl)
    _mk_spawn_skill(db5, waived, cooldown=0.0)
    try:
        verify(db5)
        check('C2 verify() passes with only waived offenders', True)
    except SystemExit as ex:
        check('C2 verify() passes with only waived offenders', False, str(ex)[:200])

    # D: FALSE-POSITIVE GUARDS. The ~140 healthy skills that carry a petLimit but no TTL
    #    must NOT be flagged, and neither must a long-cooldown summoner. If either fires,
    #    this gate has become the blanket rule the build46 debt line explicitly forbids.
    db6 = ArzDatabase()
    pl_only = _mk_spawn_skill(db6, r'records\skills\_negtest\healthy_petlimit_no_ttl.dbr',
                              cooldown=1.0, pet_limit=5)
    slow = _mk_spawn_skill(db6, r'records\skills\_negtest\slow_uncapped_summoner.dbr',
                           cooldown=60.0)
    ttl_only = _mk_spawn_skill(db6, r'records\skills\_negtest\healthy_ttl_no_petlimit.dbr',
                               cooldown=1.0, ttl=20.0)
    not_a_summon = _mk_spawn_skill(db6, r'records\skills\_negtest\not_a_spawn_skill.dbr',
                                   cooldown=1.0, cls='Skill_AttackProjectile')
    offs6, _ = check_no_new_unbounded(db6)
    names6 = [o[0] for o in offs6]
    check('D1 petLimit-without-TTL is NOT flagged (the ~140 healthy skills)',
          pl_only not in names6, str(names6))
    check('D2 long-cooldown (60s) uncapped summoner is NOT flagged', slow not in names6,
          str(names6))
    check('D3 TTL-without-petLimit is NOT flagged', ttl_only not in names6, str(names6))
    check('D4 a non-SpawnPet skill is NOT flagged', not_a_summon not in names6, str(names6))
    check('D5 nothing at all flagged in the healthy db', names6 == [], str(names6))

    # E: waiver hygiene - a waived record absent from the arz is reported STALE, never fatal.
    check('E absent waivers are reported stale, not fatal',
          len(check_no_new_unbounded(ArzDatabase())[1]) == len(_UNCAPPED_WAIVERS_NORM))

    print('  NEGTEST', 'PASS' if ok else 'FAIL')
    if not ok:
        raise SystemExit(1)


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--negtest', action='store_true')
    ap.add_argument('--sweep', metavar='ARZ', help='run sweep_uncapped over an arz')
    a = ap.parse_args()
    if a.negtest:
        _negtest()
    if a.sweep:
        from arz_patcher import ArzDatabase
        db = ArzDatabase.from_arz(Path(a.sweep))
        offs = sweep_uncapped(db)
        print("sweep_uncapped: %d records (SpawnPet, cd<10s, no petLimit, no TTL)" % len(offs))
        for r, cd, pl, ttl in offs:
            print("  %-70s cd=%.2f petLimit=%r ttl=%r" % (r, cd, pl, ttl))
