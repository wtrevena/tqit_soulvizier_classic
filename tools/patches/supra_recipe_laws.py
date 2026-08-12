r"""supra_recipe_laws - WILL 2026-08-11: every supra recipe needs a Legendary-only
reagent, no two supra recipes may want the same three things, and no supra ITEM may drop
below Legendary.

WILL, VERBATIM (LAW A): "ok for the four epic craftable reagent's, we need to change it
so that one of the items needed to craft the formula needs to be found in legendary like
the rest of the craftable supra recipes."

WILL, VERBATIM (LAW B): "each craftable supra should have different requirements (we
should not have two formulas that both require stymphalian, plisskey, and deathweavers
legtip)"

WILL, VERBATIM (LAW C): "the last word should not be dropped in epic, only legendary"

WHAT THIS MODULE WRITES (fourteen fields, and nothing else)
-----------------------------------------------------------
Fourteen supra formula records each get ONE `reagentNBaseName` repointed:

  * LAW B, ten of them - the five duplicate groups the build83 arz carried (a SIX-way axe
    group, a three-way mace group and three pairs, 15 of the 42 craftables) collapse to
    42 distinct reagent sets;
  * LAW A, four of them - the four thrown recipes swap their plain Common wand (slot 2)
    for a Legendary-only component, because the one-move alternative was measured and it
    breaks rule C1 (see `tools/svc_supra_recipes.py` for the collateral proof).

Every replacement is a record that already existed, is `itemClassification = Legendary`,
is Legendary-only, and is already reachable from 19/19 Legendary chest surfaces - so no
loot table moves, no new record enters the universe, and rules G1/G4 cannot regress.

ROUND 2 (2026-08-11), AND IT CHANGED THE GATE, NOT JUST A PICK. The vet found LAW A
failing on one of the four recipes Will named. Hati's round-1 slot-2 pick was
`e_da_crescentmoonofartemis`, which satisfied every arm S1 had - Legendary class, no
sub-Legendary chest pool reaches it, a Legendary pool does, no sub-Legendary table names
it - and gated nothing, because a divine artifact is not FOUND, it is MADE, and its
formula is paid by the four EPIC `02_act*_arcaneformulae_table` records. Hati stayed
Epic-craftable inside its own fix.

  * the pick is now `u_l_artemis'silverbow` - built by nothing, drop-only, 19/19
    Legendary surfaces, and a reagent of nothing else;
  * `legendary_only` gained ARM 5, the craft-path check, because arms 1-4 only ever asked
    who PAYS an item and never who can BUILD one. That is the part that matters: it is a
    class of hole, not one bad pick, and the two negatives N2c/N2d now hold it open.

Arm 5 is deliberately NOT "a crafted reagent never gates": every divine artifact in the
game is a craft result (77 of 77), so that rule would have redded the two DRX artifact
craftables with no legal fix. Their gates are paid only by the LEGENDARY `03_act*` tables,
so they are genuinely gated and this module leaves them alone. 42 of 42 craftables carry a
Legendary-gated reagent under the sound rule.

LAW C's own fix is NOT here: it is four memberships in
`svc_craft_thrown.THROWN_MEMBERS['e']` (the supra thrown leave the Epic thrown table and
stay on the Legendary one), because that module OWNS `svc_unique_thrown_e01` and two
modules must never write one record. This module's gate asserts the outcome either way,
so the two halves cannot drift apart.

The whole contract - the fourteen edits, the collateral analysis, the tier reader and all
four rules - lives in `tools/svc_supra_recipes.py`, so this module, the standalone gate
and the negative tests cannot disagree.

ORDER: registered immediately AFTER `craft_thrown_breadth`. That module repoints the four
thrown formulas off the Ragnarok ghosts and authors the thrown tables; this one reads the
formula/result map afterwards and would fail loud on a stale map.

RECORD OVERLAP WITH THE CONCURRENT LANES: ten `records\drxitem\supra\{recipes,zrecipes}\
*_formula.dbr` records and one `svc_unique_thrown_e01`. b84 (`fix/loot-volume-trim`)
writes chest/orb volume records, b86 (`fix/soul-rename-ratified`) writes soul records and
b87 (`feat/charon-rework`) writes the Golden Bough forecourt monster - none of the three
writes a supra formula or a thrown table, so the record intersection is EMPTY. The shared
FILES are `tools/patches/__init__.py` (one REGISTRY line here) and
`docs/SUPRA_CRAFTING_GUIDE.md`.

GATE (verify, post-finalization), over the FINAL assembled db:
  S1 every supra craftable names >= 1 reagent whose only obtain paths are Legendary-tier;
  S2 no two supra craftables name an identical reagent multiset (and no craftable is
     built by two formulas that disagree about its reagents);
  S3 every replacement reagent still resolves, is not one of the 13 dead
     `records\equipmentweapon\axe\` twins, and is reachable from a Legendary chest pool;
  S4 no supra ITEM is reachable from a Normal- or Epic-tier surface (S4), the 38
     craft-only supras are named by no loot table at all (S4b), and the four R-186 made
     droppable are still reachable on Legendary (S4c - relocation, not retirement).
Standalone twin: `py tools/gate_supra_recipe_laws.py <arz>` (also folded into
`py tools/gate_craft_thrown_breadth.py`).
Negative tests:  `py tools/debug/negtest_supra_recipe_laws.py <arz>`.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import svc_loot_breadth as SLB
import svc_supra_recipes as SSR

MODULE_NAME = 'supra_recipe_laws'


def apply(db, tags):
    print("\n=== supra_recipe_laws: a Legendary-only reagent in every recipe, no two "
          "recipes alike, and nothing supra dropping below Legendary ===")
    lk = SLB.Lookup(db)
    changes = SSR.apply_recipe_overrides(db, lk)
    print("  SUPRA/LAWS: %d supra formula(s) repointed (one reagent slot each - 4 for "
          "LAW A's Legendary gate, 10 for LAW B's de-duplication); LAW C is carried by "
          "svc_craft_thrown.THROWN_MEMBERS['e'] (the %d supra thrown leave "
          "svc_unique_thrown_e01 and stay on svc_unique_thrown_l01)."
          % (len(changes), len(SSR.LEGENDARY_DROPPABLE_SUPRAS)))
    print("=== supra_recipe_laws done ===\n")


def verify(db, tags):
    """Fail-loud build-wide supra-recipe gate over the FINAL assembled db."""
    problems, stats = SSR.audit_supra_laws(db)
    if problems:
        for p in problems[:20]:
            print("  SUPRA/LAWS OFFENDER: %s" % p)
        raise SystemExit(
            "supra_recipe_laws gate FAILED: %d problem(s); a supra recipe is craftable "
            "without farming Legendary, two recipes want the same three items, or a "
            "supra item drops below Legendary" % len(problems))
    print("  supra_recipe_laws gate PASS: all %d supra craftables have %d+ Legendary-only "
          "reagent(s) each (%d of %d distinct reagents are Legendary-only), all %d "
          "reagent sets are distinct across %d formula records, and %d supra item(s) are "
          "loot-reachable - %d of them below Legendary."
          % (stats['craftables'], stats['min_gated'], stats['legendary_only_reagents'],
             stats['reagents'], stats['distinct_sets'], stats['formulas'],
             stats['droppable_supras'], stats['sub_legendary_supras']))
