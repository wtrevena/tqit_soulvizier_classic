r"""craft_thrown_breadth - WILL 2026-08-10: mythic formulas drop on Normal too, every
reagent is findable, and the legendary THROWN weapons finally drop.

WILL, VERBATIM: "i meant do the mythic formulas drop. they can drop in normal as well,
but the legendary items should not drop in normal. All of the reagents need to be
droppable somewhere in the game, ideally from chests since that is where people will
look. if players farm legendary long enough, they should be able to find all the
reagents without having to farm a specific area or a specific character (except for the
monster unique droppable items like the green items that are needed to build some of the
formulas...). Yes we should make the legendary thrown weapons droppable."

WHAT THIS MODULE IS. R-180 widened what the chests can pay by WEAPON CLASS. This is the
CRAFT-CHAIN half: what the chests can pay towards actually BUILDING the 42 uber ("supra")
craftables, plus the one weapon class R-180 could not reach because the database has no
table for it. The whole contract - every constant, every derivation, both halves of every
gate - lives in `tools/svc_craft_thrown.py`, so this module, the standalone gate
`tools/gate_craft_thrown_breadth.py` and the negative tests cannot disagree (the
gate_relic_difficulty_tiers / svc_loot_breadth precedent).

WHAT IT WRITES (all additive or a strict raise; nothing is removed, no weight lowered):
  * `supra.dbr` into each `01_act{1..4}_arcaneformulae` table at ~1% of that table's own
    total, so mythic formulas drop on NORMAL as well - rarer than the 2% the base game
    already gives them on Epic and the 5% on Legendary. Formulas are
    `itemClassification = Common` ItemArtifactFormula records, so no legendary GEAR moves;
  * `svc_unique_thrown_{n,e,l}01`, the unique one-hand-ranged table this era's database
    never had, wired into `svc_unique_weapons_{tier}01` as its SEVENTH class by
    `svc_loot_breadth._master_members` (so thrown becomes payable in every mod chest's
    weapon row AND its guaranteed slot). Normal names only the itemLevel-30 wands, so the
    tier law holds by construction;
  * `svc_craft_reagents_{torso,amulet,ring,artifact,orphanmi}_l01` - the 14 reagents no
    chest could pay, plus the one green whose only monster is a dev duplicate - each hung
    off the LEGENDARY-tier host master(s) the chest pools already reach. The artifact
    family hangs off THREE hosts (`04_l_misc` + `amulet_l01` + `finger_l01`) because
    `04_l_misc` is reached by exactly ONE of the 19 legendary chest surfaces and that one
    is the apex uber-boss orb - which would have put six reagents behind a single boss
    family, the thing Will explicitly ruled out;
  * the 4 thrown formulas repointed off three RAGNAROK (`xpack2\...\1hranged\`) records
    that do not exist in this build. Charon's Toll, Hati, The Last Word and Sanguine
    Orbit were uncraftable by anyone; a record that is not in the database cannot be put
    into a loot pool, so repointing them onto thrown records that DO exist is the only
    available fix. They are repointed into the house shape (2 ordinary + 1 green, all of
    the result's own item Class) that 43 of the 59 uber formulas already use.

ORDER IS LOAD-BEARING: registered immediately BEFORE `chest_loot_breadth`. The thrown
tables must exist before that module's `ensure_masters` runs, because a master member
whose donor does not resolve is silently skipped. `polis_vault` calls the same idempotent
builder earlier and will have authored 7-member masters; `chest_loot_breadth`'s call then
rewrites them with the eighth (thrown) member. This module never writes a chest or hoard
`FixedItemLoot` record, an orb table, or a hoard weight.

RECORD OVERLAP WITH THE CONCURRENT LANES - NOT EMPTY. Byte-measured baseline -> lane:
7 added / 0 removed / 15 modified, and three of the 15 are
`svc_unique_weapons_{n,e,l}01`, which `fix/armor-loot-breadth` (b80) also rewrites via
the same `svc_loot_breadth._master_members`. Everything else is disjoint from b79 and
b80. The binding merge resolution is in `tools/svc_craft_thrown.py`'s docstring.

GATE (verify, post-finalization), over the FINAL assembled db:
  F1 every uber craftable has a chest-droppable formula on EVERY difficulty tier;
  G0 no reagent names a record that is absent from the database;
  G1 every non-MI reagent is reachable from the Legendary-tier chest pools;
  G2 the committed MI exemption roster still equals the roster the rule derives;
  G3 every MI/green exemption is earned by a LIVE monster, or the green is chest-placed
     instead - and the committed no-live-carrier roster still matches the database;
  G4 every non-MI reagent is payable by at least half of the legendary chest SURFACES
     (union reachability cannot tell 19 surfaces from 1);
  C1/C2 the thrown class is payable at every mod chest's own tier, with zero legendary
     thrown on Normal (also enforced from inside `svc_loot_breadth.audit_table`, so
     `py tools/gate_chest_loot_breadth.py` covers it too).
Standalone twin: `py tools/gate_craft_thrown_breadth.py <arz>`.
Negative tests:  `py tools/debug/negtest_craft_thrown.py <arz>`.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import svc_craft_thrown as SCT
import svc_loot_breadth as SLB

MODULE_NAME = 'craft_thrown_breadth'


def apply(db, tags):
    print("\n=== craft_thrown_breadth: mythic formulas everywhere, reagents findable, "
          "thrown droppable ===")
    lk = SLB.Lookup(db)

    formula_changes = SCT.wire_mythic_formulas_into_normal(db, lk)
    thrown = SCT.ensure_thrown_tables(db, lk)
    reagents = SCT.ensure_reagent_tables(db, lk)
    host_changes = SCT.wire_reagent_hosts(db, lk)
    repoints = SCT.repoint_thrown_formula_reagents(db, lk)

    n_reagents = sum(len(v) for v in SCT.REAGENT_PLACEMENTS.values())
    n_hosts = len({h for hs in SCT.REAGENT_HOSTS.values() for h, _w in hs})
    # COUNT HONESTLY: each Normal act table takes TWO memberships (supra + supra_special),
    # so 4 tables produce 8 changes. Report the tables and the memberships separately.
    n_tables = len({c.split(':', 1)[0] for c in formula_changes})
    print("  CRAFT/THROWN: %d Normal formula table(s) now name the supra pools "
          "(%d membership(s) written this run); %d thrown table(s) authored; %d reagent "
          "table(s) carrying %d reagent(s) hung off %d distinct legendary host record(s) "
          "via %d membership(s); %d thrown formula(s) repointed off the Ragnarok ghosts."
          % (n_tables, len(formula_changes), len(thrown), len(reagents), n_reagents,
             n_hosts, len(host_changes), len(repoints)))
    if not thrown:
        print("  CRAFT/THROWN: WARNING no thrown table was authored - the breadth master "
              "will keep six classes and verify() will fail loud.")
    print("=== craft_thrown_breadth done ===\n")


def verify(db, tags):
    """Fail-loud build-wide craft-chain + thrown gate over the FINAL assembled db."""
    problems, stats = SCT.audit_db(db)
    if problems:
        for p in problems[:20]:
            print("  CRAFT/THROWN OFFENDER: %s" % p)
        raise SystemExit(
            "craft_thrown_breadth gate FAILED: %d problem(s); the uber-craft chain is "
            "not completable or the thrown class is unpayable" % len(problems))
    f = stats['formulas']
    r = stats['reagents']
    print("  craft_thrown_breadth gate PASS: all %d uber craftables have a "
          "chest-droppable formula on n/e/l (%d/%d/%d formula records reachable); "
          "%d reagents = %d MI (monster-farmed, exempt) + %d ordinary + %d artifact + "
          "%d missing, %d reachable from Legendary chests, thinnest non-MI spread %d of "
          "%d legendary chest surfaces (floor %d); thrown payable on %d mod chest "
          "table(s) with 0 legendary thrown on Normal."
          % (f['l'][1], f['n'][2], f['e'][2], f['l'][2],
             r['total'], r['mi'], r['ordinary'], r['artifact'], r['missing'],
             r['reachable_l'], r['spread_min'], r['surfaces'], r['spread_floor'],
             stats['chests']))
