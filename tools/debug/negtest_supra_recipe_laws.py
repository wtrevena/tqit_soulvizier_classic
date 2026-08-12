r"""negtest_supra_recipe_laws.py - NEGATIVE TESTS for the three supra-recipe laws.

A gate that has never been seen to FAIL is not a gate. This plants each defect the
contract exists to catch into an in-memory copy of the database and asserts the gate reds
on it - and asserts the untouched build is green, so a gate that reds on everything (or
on nothing) is caught too.

RUNS AGAINST EITHER ARZ. Given a PRE-wave arz the harness first applies this lane's own
two writes - `svc_craft_thrown.ensure_thrown_tables` (LAW C: the four supra thrown off
the Epic thrown table) and `svc_supra_recipes.apply_recipe_overrides` (LAW A + LAW B: the
fourteen one-slot recipe repoints) - so the negatives can run before a build exists. Both
calls are idempotent, so against a POST-wave arz they are no-ops and the run is identical.

Planted defects, one per arm of the contract:
  N1  S4  - put the four supra thrown back on `svc_unique_thrown_e01`. This is THE
            SHIPPED DEFECT, byte-for-byte: it is how The Last Word reached an Epic chest.
  N2  S1  - demote ONE de-duplication replacement (`u_l_phoenix`) onto an Epic-tier
            table -> Phoenix Ascendant's only Legendary-only reagent stops being one.
            This is the "demote one back" negative the ruling asked for.
  N2b S1  - the same demotion aimed at LAW A: `u_l_scepterofthanatos` onto an Epic-tier
            table -> The Last Word's ONLY Legendary-only reagent stops being one, and
            the recipe is Epic-craftable again.
  N2c S1  - THE CRAFT PATH. Put Hati's gate back on `e_da_crescentmoonofartemis`, which
            passes arms 1-4 (Legendary class, no sub-Legendary chest pool, a Legendary
            pool reaches it, no sub-Legendary table names it) and is nevertheless MADE
            from an EPIC arcane formula. Round 1 shipped exactly this and the gate said
            PASS. Only arm 5 sees it.
  N2d S1  - the false-red guard for arm 5: the four Legendary divine artifacts whose
            formulas are paid ONLY by `03_act*_arcaneformulae_table` must still count as
            Legendary-only, or the two DRX artifact craftables become unfixable by
            construction (every divine artifact in the game is a craft result).
  N3  S1  - unhook `u_l_pagos` from every loot table that names it -> Aquimae's gate is
            no longer FINDABLE, which is uncompletable rather than gated. Proves the
            third arm of `legendary_only` (a Legendary chest pool must still reach it).
  N4  S2  - copy Crystal Tear of Nyx's reagent set onto Aquimae -> a planted duplicate
            group, the defect Will named.
  N5  S2b - make one of a craftable's two formula records disagree with the other about
            its own reagents.
  N6  S3  - repoint a replacement onto its DEAD twin under `records\equipmentweapon\axe\`
            (the path that differs only by the missing `item\` folder level) -> a
            reagent nothing in the database references.
  N7  S4b - plant a NON-thrown supra (Blood Whisper) into a loot table -> the 38
            craft-only supras are built, never found, at any band.
  N8  S4c - strip the four supra thrown off the LEGENDARY table as well -> "only
            legendary" is a relocation, and over-applying it retires R-186's own ask.

Usage: py tools/debug/negtest_supra_recipe_laws.py <arz>
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1]
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))
from arz_patcher import ArzDatabase
import svc_craft_thrown as SCT
import svc_loot_breadth as SLB
import svc_supra_recipes as SSR


def _built(path):
    """A pristine db per test, with this lane's own writes applied (idempotent)."""
    db = ArzDatabase.from_arz(path)
    lk = SLB.Lookup(db)
    SCT.ensure_thrown_tables(db, lk, verbose=False)
    SSR.apply_recipe_overrides(db, lk, verbose=False)
    return db


def _drop_member(db, lk, table, needle):
    real = lk.real(table)
    hit = 0
    for i, nm, _w in SCT._members(db, real):
        if needle in SLB._n(nm):
            db.set_field(real, 'lootName%d' % i, '')
            db.set_field(real, 'lootWeight%d' % i, 0)
            hit += 1
    return hit


def _unhook_everywhere(db, lk, item):
    """Blank `item` out of every loot table that names it, whatever the field is called.

    NOT `_drop_member`: that only knows `lootNameN`, and a base level-banded unique table
    is a `LootItemTable_DynWeight` whose members sit in differently-named slots. A
    negative test that silently edits nothing is worse than no negative test, so this
    walks the fields and returns the count the caller prints."""
    rev = SCT.reverse_index(db)
    target = SLB._n(item)
    hit = 0
    for holder in sorted(rev.get(target, ())):
        if not SLB.is_loot_table(lk, holder):
            continue
        for k in list((db.get_fields(holder) or {})):
            base = k.split('###')[0]
            vals = (db.get_fields(holder) or {})[k].values
            if any(isinstance(v, str) and SLB._n(v) == target for v in vals):
                db.set_field(holder, base, '')
                hit += 1
    return hit


def _reagents_of_result(db, lk, result):
    for f, r in SCT.uber_formulas(db, lk).items():
        if SLB._n(r) == SLB._n(result):
            return lk.real(f), SCT.reagents_of(db, lk.real(f))
    raise SystemExit('negtest: no formula builds %s' % result)


def _run(label, rule, db, expect_fail=True):
    problems, _stats = SSR.audit_supra_laws(db)
    hit = [p for p in problems if p.startswith(rule)]
    ok = bool(hit) if expect_fail else not problems
    print("  %-4s %-4s %-52s %s" % (label, rule, ('EXPECT RED' if expect_fail
                                                  else 'EXPECT GREEN'),
                                    'PASS' if ok else 'FAIL'))
    if hit:
        print("        %s" % hit[0][:170])
    if not ok and not expect_fail:
        for p in problems[:3]:
            print("        UNEXPECTED %s" % p[:170])
    return ok


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/debug/negtest_supra_recipe_laws.py <arz>")
        return 2
    arz = Path(argv[1])
    results = []
    print("\n=== negative tests: supra recipe laws (S1 Legendary gating, S2 uniqueness, "
          "S4 no supra below Legendary) ===")

    # N0 control - the lane's own output must be GREEN.
    results.append(_run('N0', '', _built(arz), expect_fail=False))

    # N1 - the four supra thrown back on the Epic thrown table (the shipped defect)
    db = _built(arz)
    lk = SLB.Lookup(db)
    for p in SSR.LEGENDARY_DROPPABLE_SUPRAS:
        SCT.add_member(db, lk.real(SSR.EPIC_THROWN_TABLE), p, 10, lk)
    results.append(_run('N1', 'S4', db))

    # N2 - demote ONE replacement onto an Epic-tier table
    db = _built(arz)
    lk = SLB.Lookup(db)
    SCT.add_member(db, lk.real(SSR.EPIC_THROWN_TABLE),
                   r"records\item\equipmentweapon\axe\u_l_phoenix.dbr", 1, lk)
    results.append(_run('N2', 'S1', db))

    # N2b - the same demotion aimed at LAW A's own pick
    db = _built(arz)
    lk = SLB.Lookup(db)
    SCT.add_member(db, lk.real(SSR.EPIC_THROWN_TABLE),
                   r"records\item\equipmentweapon\club\u_l_scepterofthanatos.dbr", 1, lk)
    results.append(_run('N2b', 'S1', db))

    # N2c - THE CRAFT PATH, and this is the negative round 1 did not have. Put Hati's
    # gate back on `e_da_crescentmoonofartemis`: a reagent that is itemClassification =
    # Legendary, that no Normal or Epic chest pool reaches, that a Legendary pool DOES
    # reach, and that no sub-Legendary loot table names - so it passes arms 1-4 of
    # `legendary_only` exactly as it did in round 1 - but which is MADE by
    # `e_da_crescentmoonofartemis_formula`, and that formula is paid by the four EPIC
    # `02_act*_arcaneformulae_table` records. Only arm 5 can see this, so this test is
    # the proof that arm 5 exists and fires. If it ever goes green, the gate has gone
    # back to blessing an Epic-craftable reagent as a Legendary gate.
    db = _built(arz)
    lk = SLB.Lookup(db)
    hati = lk.real(r'records\drxitem\supra\zrecipes\svc_thrown_hati_formula.dbr')
    SLB._set_str(db, hati, 'reagent2BaseName',
                 lk.real(r'records\xpack\item\artifacts\e_da_crescentmoonofartemis.dbr'))
    results.append(_run('N2c', 'S1', db))

    # N2d - the OTHER side of arm 5, and the reason it is not a blanket "crafted reagents
    # never gate" rule: the two DRX artifact craftables are built from divine artifacts,
    # and EVERY divine artifact in the game is a craft result (77 of 77). Their gates -
    # Thoth's Glory, Ikon of Zeus, Marduk's Tablet, Golden Eye - are paid only by the
    # LEGENDARY `03_act*_arcaneformulae_table` records, so arm 5 must PASS them. This is
    # the false-red guard: a gate that reds on everything is not a gate.
    db = _built(arz)
    lk = SLB.Lookup(db)
    ex = SLB.Expander(db, lk)
    pools = {t: SCT.chest_pool(db, lk, ex, t) for t in SSR.TIERS}
    ok = True
    for art in ('l_da_thothsglory', 'l_da_ikonofzeus',
                'l_da_mardukstabletofdestiny', 'l_da_goldeneyeofsunwukong'):
        good, why = SSR.legendary_only(
            db, lk, ex, r'records\xpack\item\artifacts\%s.dbr' % art, pools)
        if not good:
            ok = False
            print("        UNEXPECTED RED %s: %s" % (art, why))
    print("  %-4s %-4s %-52s %s" % ('N2d', 'S1', 'EXPECT GREEN (Legendary-formula '
                                    'artifacts still gate)', 'PASS' if ok else 'FAIL'))
    results.append(ok)

    # N3 - a gate reagent that nothing can pay is uncompletable, not gated
    db = _built(arz)
    lk = SLB.Lookup(db)
    n = _unhook_everywhere(db, lk, r'records\item\equipmentweapon\sword\u_l_pagos.dbr')
    print("       (unhooked u_l_pagos from %d loot-table membership(s))" % n)
    results.append(_run('N3', 'S1', db))

    # N4 - a planted duplicate reagent set
    db = _built(arz)
    lk = SLB.Lookup(db)
    _f, donor = _reagents_of_result(db, lk, r'records\drxitem\supra\wep_dagger.dbr')
    victim, _rg = _reagents_of_result(db, lk,
                                      r'records\drxitem\supra\svc_wep_aquimae.dbr')
    for i, p in enumerate(donor, start=1):
        SLB._set_str(db, victim, 'reagent%dBaseName' % i, lk.real(p))
    results.append(_run('N4', 'S2', db))

    # N5 - two formulas of one craftable disagreeing about its reagents
    db = _built(arz)
    lk = SLB.Lookup(db)
    twin = lk.real(r'records\drxitem\supra\zrecipes\wep_shield_formula.dbr')
    SLB._set_str(db, twin, 'reagent1BaseName',
                 lk.real(r"records\item\equipmentweapon\axe\u_l_phoenix.dbr"))
    results.append(_run('N5', 'S2b', db))

    # N6 - a replacement repointed onto its DEAD twin
    db = _built(arz)
    lk = SLB.Lookup(db)
    dead = lk.real(r"records\equipmentweapon\axe\u_l_phoenix.dbr")
    if not dead:
        print("  N6   S3   SKIPPED (no dead twin in this database)")
    else:
        f = lk.real(r'records\drxitem\supra\zrecipes\wep_axe_formula.dbr')
        SLB._set_str(db, f, 'reagent1BaseName', dead)
        saved = SSR.NEW_REAGENTS
        try:
            SSR.NEW_REAGENTS = tuple(sorted(set(saved) - {
                r"records\item\equipmentweapon\axe\u_l_phoenix.dbr"} | {dead}))
            results.append(_run('N6', 'S3', db))
        finally:
            SSR.NEW_REAGENTS = saved

    # N7 - a NON-thrown supra planted into a loot table: the other 38 are craft-only at
    #      every band, so ANY table naming one is a leak even on Legendary.
    db = _built(arz)
    lk = SLB.Lookup(db)
    SCT.add_member(db, lk.real(SSR.LEG_THROWN_TABLE),
                   r'records\drxitem\supra\wep_spear.dbr', 1, lk)
    results.append(_run('N7', 'S4b', db))

    # N8 - over-applying LAW C: strip the four off the LEGENDARY table too
    db = _built(arz)
    lk = SLB.Lookup(db)
    n = sum(_drop_member(db, lk, SSR.LEG_THROWN_TABLE,
                         SLB._n(p).rsplit('\\', 1)[-1][:-4])
            for p in SSR.LEGENDARY_DROPPABLE_SUPRAS)
    print("       (dropped %d supra thrown membership(s) from the Legendary table)" % n)
    results.append(_run('N8', 'S4c', db))

    bad = results.count(False)
    print("\n%d/%d negative tests behaved as specified." % (len(results) - bad,
                                                            len(results)))
    if bad:
        print("NEGTEST FAIL: the gate does not catch what it claims to catch.")
        return 1
    print("NEGTEST PASS.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
