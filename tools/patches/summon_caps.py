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


def verify(db, tags=None):
    """Fail-loud: every target summon skill must carry a positive spawn TTL after the
    build finalizes (last-writer semantics - reads the FINAL record state)."""
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


def sweep_uncapped(db, cooldown_max=10.0):
    """DIAGNOSTIC (not a build gate): every Skill_*SpawnPet* record with a short cooldown
    (< cooldown_max) that has NEITHER a positive petLimit NOR a positive spawnObjectsTimeToLive
    - the unbounded-summoner pattern. Returns [(rec, cd, petLimit, ttl)]. Used by the b76 class
    sweep + the negative test below."""
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


def _negtest():
    """Standalone negative test: plant an uncapped fast summoner into a throwaway db and
    assert sweep_uncapped flags it; then cap it and assert it clears. Run:
        py tools/patches/summon_caps.py --negtest
    """
    from collections import OrderedDict
    from arz_patcher import ArzDatabase, TypedField, DATA_TYPE_STRING
    db = ArzDatabase()
    rec = r'records\skills\_negtest\uncapped_fast_summoner.dbr'
    # register directly into the raw-record index (so record_names/has_record see it) and
    # seed the decode cache (so get_fields returns our synthetic fields without decompress).
    db._raw_records[rec] = ('Skill', b'')
    db._decoded_cache[rec] = OrderedDict([
        ('Class', TypedField(DATA_TYPE_STRING, ['Skill_SpawnPetMonster'])),
        ('spawnObjects', TypedField(DATA_TYPE_STRING, [r'records\creature\monster\x.dbr'])),
        ('skillCooldownTime', TypedField(DATA_TYPE_FLOAT, [1.0])),
    ])
    off = sweep_uncapped(db)
    assert any(r[0] == rec for r in off), "negtest FAIL: uncapped fast summoner not flagged"
    db.set_field(rec, 'spawnObjectsTimeToLive', 5.0, DATA_TYPE_FLOAT)
    off2 = sweep_uncapped(db)
    assert not any(r[0] == rec for r in off2), "negtest FAIL: TTL-capped summoner still flagged"
    print("summon_caps._negtest OK: uncapped fast summoner flagged, capped summoner cleared")


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
