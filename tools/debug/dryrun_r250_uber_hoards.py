r"""dryrun_r250_uber_hoards.py - apply R-250 IN MEMORY to a built arz, then gate it.

WHY THIS EXISTS. R-250 lands in three places a static reader cannot join up on its own:
the monolith's finalization wiring, a scope predicate inside R-240's trim, and one
registry module. Proving "the gates are green AFTER the fix" would otherwise need a full
DB build - and the lane that writes the fix is not the lane that owns builds. So this
reproduces exactly what the three of them do, on a db loaded from a shipped arz, and
then runs the whole coexisting battery over the result. It is a PROOF HARNESS, never a
build step: it writes no file and is not imported by anything in the pipeline.

WHAT IT REPRODUCES, and where the real thing lives:
  0. `_create_obsidian_roulette` (content pass)    - the guaranteed relic row, per tier.
     ROUND-2. The roulette wrote the NORMAL-tier relic into all three Obsidian tiers, so
     the Epic/Legendary hoards guaranteed an Essence relic. R-250's own wiring is what
     makes that leak REACHABLE (and therefore gate-visible), which is why the battery
     below now runs `gate_relic_difficulty_tiers` and why this step must be simulated
     alongside the wiring rather than assumed.
  1. `_create_propontis_superboss` (content pass)  - author svc_dorushoard_loot_0N and
     point Dorus's chests at it.

     ONE DELIBERATE DIFFERENCE, stated rather than hidden. The real build clones the
     blood-cave donor in the CONTENT pass and the loot-breadth / armour-parity REGISTRY
     modules then widen the result, because `svc_loot_breadth.chest_tables` sweeps every
     mod-owned FixedItemLoot record and the new table is one. This harness cannot run
     those modules (they need the whole registry and the tags dict), so it clones the
     POST-BREADTH SIBLING `svc_obsidianhoard_loot_0N` instead - the same donor, the same
     recipe, already carrying the widening, and the table Dorus's chests SHARED before
     R-250 separated them. Cloning the raw donor here instead reds `gate_loot_distribution`
     D3/D5/D8 on exactly the three new records and nothing else, which is a measurement
     of the missing widening, not of R-250. The authored tables are also registered with
     the ownership ledger below, so OWN1 proves the distribution gate really does cover
     them rather than silently dropping them (an `infer_tier` miss would surface here).
  2. `svc_loot_volume._r250_exempt` (the trim's scope) - restore every uber/boss hoard
     table to the authored *2.4/*2.8 the carve-out preserves.
  3. `_svc_wire_boss_hoard_chests` (finalization)   - every hoard chest names its own table.
  4. `uber_hoard_generosity.apply`                  - the Secret Present box at 3x.

Usage:
  py tools/debug/dryrun_r250_uber_hoards.py <arz>            # apply + gate + report
  py tools/debug/dryrun_r250_uber_hoards.py <arz> --before   # gate the arz as-is (control)
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1]
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from arz_patcher import ArzDatabase          # noqa: E402
import svc_loot_breadth as SLB               # noqa: E402
import svc_uber_hoards as SUH                # noqa: E402
import svc_loot_volume as SLV                # noqa: E402
import svc_armor_breadth as SAB              # noqa: E402
import svc_loot_distribution as SLD          # noqa: E402
import svc_chest_artifacts as SCA            # noqa: E402
import svc_loot_ownership as OWN             # noqa: E402
import gate_relic_difficulty_tiers as GRT    # noqa: E402

_C = SUH.CONTAINER_DIR
# The POST-BREADTH sibling (see the header for why, and what the alternative measures).
# `--raw-donor` swaps in the blood-cave donor the real content pass clones.
_DONOR = {t: r'%s\svc_obsidianhoard_loot_%s.dbr' % (_C, t) for t in SUH.TIERS}
_RAW_DONOR = {t: r'%s\loottable_hidden_bloodcave_%s.dbr' % (_C, t) for t in SUH.TIERS}
_GUAR_UNIQUE = {
    '01': r'records\xpack\item\loottables\weapons\mastertables\unique_1h_n01.dbr',
    '02': r'records\xpack\item\loottables\weapons\mastertables\unique_1h_e01.dbr',
    '03': r'records\xpack\item\loottables\weapons\mastertables\unique_1h_l01.dbr',
}
_GUAR_RELIC = {
    '01': r'records\xpack\item\loottables\relics\01_act4_relics.dbr',
    '02': r'records\xpack\item\loottables\relics\02_act4_relics.dbr',
    '03': r'records\xpack\item\loottables\relics\03_act4_relics.dbr',
}


def simulate(db, lk, raw_donor=False):
    """Return a list of human-readable change lines."""
    log = []
    donors = _RAW_DONOR if raw_donor else _DONOR

    # (0) the Obsidian roulette's guaranteed row, per tier.
    #
    # ROUND-2 ADDITION, and the reason the battery below now runs the relic gate. The
    # roulette wrote the NORMAL-tier constants into loot_01/02/03 alike, so the Epic and
    # Legendary Obsidian Hoards guaranteed an Essence relic. Nothing saw it because the
    # relic gate walks the WIRE and those chests named `boss_default_*` - so R-250's own
    # wiring is what makes the leak reachable, and simulating the wiring WITHOUT this
    # would report a red the real build does not have (or, worse, hide a real one).
    # Ordered first because step (1) clones these tables for the Dorus family.
    for t in SUH.TIERS:
        table = lk.real(r'%s\svc_obsidianhoard_loot_%s.dbr' % (_C, t))
        if not table:
            continue
        got = SLB._n(SLB._sc(db.get_field_value(table, 'loot3Name2')) or '')
        if got == SLB._n(_GUAR_RELIC[t]):
            continue
        # `loot3Name2` ONLY. The real fix also makes `loot3Name1` per-tier, but this db
        # is post-R-180, where `retarget_guaranteed_weapon` has already replaced that
        # slot with the mod's all-classes `svc_unique_weapons_<tier>01` breadth master.
        # Writing the base-game `unique_1h_<tier>01` back over it here would simulate a
        # regression the real build does not have (and would red D3's spear floor) - the
        # same post-vs-pre-module distinction the `--raw-donor` note above describes.
        db.set_field(table, 'loot3Name2', _GUAR_RELIC[t])
        db._modified.add(table)
        log.append('tier row svc_obsidianhoard_loot_%s: %s -> %s'
                   % (t, got.rsplit('\\', 1)[-1], _GUAR_RELIC[t].rsplit('\\', 1)[-1]))
    lk.refresh()

    # (1) the missing Dorus family, authored on the shared recipe
    for t in SUH.TIERS:
        chest = lk.real(r'%s\svc_dorushoard_%s.dbr' % (_C, t))
        if not chest:
            continue
        table = r'%s\svc_dorushoard_loot_%s.dbr' % (_C, t)
        if not lk.real(table):
            donor = lk.real(donors[t])
            if not donor:
                log.append('MISSING DONOR %s' % donors[t])
                continue
            db.clone_record(donor, table)
            db.set_field(table, 'loot3Chance', 100.0)
            db.set_field(table, 'loot3Weight1', 100)
            db.set_field(table, 'loot3Name2', _GUAR_RELIC[t])
            db.set_field(table, 'loot3Weight2', 60)
            if raw_donor:
                # What the CONTENT pass writes. In a real build R-180's
                # `retarget_guaranteed_weapon` then repoints this from the base game's
                # 3-class `unique_1h_<tier>01` to the mod's all-classes breadth master
                # `svc_unique_weapons_<tier>01` - which is what puts SPEAR in the
                # guaranteed slot and is what D3's spear floor is measuring. Writing it
                # here and NOT retargeting is the whole difference between the two donor
                # modes, and it is worth seeing: it reds D3/D5/D8 on these three records.
                db.set_field(table, 'loot3Name1', _GUAR_UNIQUE[t])
            db._modified.add(table)
            # The real content pass registers the write, so OWN1 can prove the
            # distribution gate covers the new surface. Do the same here or the
            # harness would pass on a coverage hole the build would catch.
            OWN.note_write(table, 'dryrun_r250 (dorus hoard)')
            log.append('authored %s (clone of %s + guaranteed row)'
                       % (table.rsplit('\\', 1)[-1], donors[t].rsplit('\\', 1)[-1]))
    lk.refresh()

    # (2) the carve-out's effect: the authored volume, kept
    for key, (real, _f, _tr) in sorted(SUH.tables(db, lk).items()):
        mn = SLB._sc(db.get_field_value(real, 'numSpawnMinEquation'))
        if str(mn) == SUH.HOARD_MIN_EQ:
            continue
        db.set_field(real, 'numSpawnMinEquation', SUH.HOARD_MIN_EQ)
        db.set_field(real, 'numSpawnMaxEquation', SUH.HOARD_MAX_EQ)
        db._modified.add(real)
        log.append('volume %s: %s -> %s' % (key.rsplit('\\', 1)[-1], mn, SUH.HOARD_MIN_EQ))

    # (3) the wiring
    for key, (real, _f, _tr) in sorted(SUH.chests(db, lk).items()):
        want = SUH.table_for(real)
        got = SLB._n(SLB._sc(db.get_field_value(real, 'tables')) or '')
        if got == SLB._n(want):
            continue
        db.set_field(real, 'tables', lk.real(want) or want)
        db._modified.add(real)
        log.append('wired %s: %s -> %s' % (key.rsplit('\\', 1)[-1],
                                           got.rsplit('\\', 1)[-1],
                                           SLB._n(want).rsplit('\\', 1)[-1]))

    # (4) the Secret Present box at 3x
    for path in SUH.GIFT_TABLES:
        real = lk.real(path)
        if not real:
            continue
        if str(SLB._sc(db.get_field_value(real, 'numSpawnMinEquation'))) == SUH.GIFT_MIN_EQ:
            continue
        db.set_field(real, 'numSpawnMinEquation', SUH.GIFT_MIN_EQ)
        db.set_field(real, 'numSpawnMaxEquation', SUH.GIFT_MAX_EQ)
        db._modified.add(real)
        log.append('gift box %s -> %s / %s'
                   % (SLB._n(path).rsplit('\\', 1)[-1], SUH.GIFT_MIN_EQ, SUH.GIFT_MAX_EQ))
    lk.refresh()
    return log


def _battery(db, lk):
    """Every coexisting contract R-250 could plausibly disturb, in one pass."""
    results = []
    r250 = {}
    results.append(('R-250 uber hoard generosity (H1-H8)', SUH.problems(db, lk, r250)))
    results.append(('R-240 loot volume (V1-V7b)', SLV.problems(db, lk, {})))
    results.append(('R-181 loot distribution (D1-D9)', SAB.audit_db(db)[0]))
    results.append(('R-181 loot ownership (OWN1/OWN2)', SAB.ownership_problems(db, lk)))
    results.append(('R-180 chest loot breadth', SLB.audit_db(db)[0]))
    results.append(('R-240 chest artifacts', SCA.problems(db, lk)))
    # ROUND-2: this line is the round-1 miss, and it belongs here more than anywhere.
    # R-250 is the wave that makes 30 previously-orphaned branches REACHABLE, and this
    # gate only ever sees a branch something points at - so R-250 is precisely the change
    # that can turn it red without touching a single record it checks. Measured on the
    # shipped b888f022: 51 branches / 0 findings before, 81 / 8 after the wiring alone.
    grt_problems, grt_branches = GRT.audit_db(db)
    r250['relic_branches'] = grt_branches
    results.append(('R-238 relic/unique difficulty tiers (%d branches)' % grt_branches,
                    grt_problems))
    return results, r250


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/debug/dryrun_r250_uber_hoards.py <arz> [--before]")
        return 2
    db = ArzDatabase.from_arz(Path(argv[1]))
    lk = SLB.Lookup(db)
    before = '--before' in argv[2:]
    raw = '--raw-donor' in argv[2:]
    if not before:
        print("\n=== R-250 dry run: applying the wave in memory%s ==="
              % (' (RAW DONOR - expect D3/D5/D8 on the 3 new Dorus tables, which is the '
                 'missing breadth widening this harness cannot run)' if raw else ''))
        for line in simulate(db, lk, raw_donor=raw):
            print("   %s" % line)
    else:
        print("\n=== R-250 dry run: CONTROL, arz measured as built ===")

    results, r250 = _battery(db, lk)
    print("\n=== gate battery %s R-250 ===" % ('BEFORE' if before else 'AFTER'))
    bad = 0
    for label, problems in results:
        if problems:
            bad += 1
            print("  RED   %-40s %d finding(s)" % (label, len(problems)))
            for p in problems[:4]:
                print("           %s" % str(p)[:180])
        else:
            print("  GREEN %-40s 0 findings" % label)
    if not before and not results[0][1]:
        print("\n  " + SUH.pass_line(r250))
    print()
    return 1 if (bad and not before) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
