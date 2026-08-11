r"""chest_loot_breadth - WILL 2026-08-10: every mod chest can pay every weapon class.

WILL, VERBATIM: "we need to update the chests in the test hub in the place where the
Polybotes Soul drops in the prison of souls so that they drop different items since
right now I am seeing every chest drop the same items pretty much ever playthrough,
there are never any legendary spears dropped it is basically the same items dropped
over and over by all chests. we need to expand the bredth of the legendary items
dropped in the testhub chests and also in the steam version."

WHAT THIS MODULE IS. The Gaoler cage half (per-chest themes + the 3-variant accessory
pools that stop the six physical chests mirroring one another) lives in
`tools/patches/polis_vault.py`. THIS module is the BLAST RADIUS: the identical collapsed
weapon row was inherited by EVERY chest the mod owns, because they are all clones of the
DRX donor `loottable_hidden_bloodcave_0N` - 40 mod-owned chest loot tables, all of them
with 0 reachable legendary spears (measured on the live DEV arz 9c190b99). Will asked for
the breadth "in the testhub chests and also in the steam version", so it is applied ONCE,
here, over every mod-owned gear chest plus the 3 DRX donors themselves, from the single
shared implementation in `tools/svc_loot_breadth.py`. That also closes BL-b102-DEBT-4 (the
shared `_OBS_GUAR_*` carriers) structurally: no builder needs to remember the rule.

WHAT IT WRITES (all additive or a strict raise; nothing is ever removed or lowered):
  * the 3 aggregate weapon masters `svc_unique_weapons_{n,e,l}01` (if polis_vault has not
    already authored them - both callers use the same idempotent builder);
  * per chest table: the master into the ONE free loot1 member slot at weight 800, the
    weapon-row chance 14 -> 40 and the shield-row chance 14 -> 30;
  * per chest table: the GUARANTEED loot3 weapon member repointed from `unique_1h_*01`
    (axe/mace/sword only) to the master (every weapon class, spear included). The WEIGHT
    is preserved, so each chest's guaranteed weapon:relic split is exactly what shipped.

ORDERING. Registered LATE (immediately before the no-op 'visuals'), because it must sweep
the FINAL assembled db: the monolith's `_svc_build_dedicated_hoard` (8 hoard families),
`general_guardians` (3 guard-pair hoards), `uber_apex_orb` (the apex orb tables) and
`polis_vault` (the cage) all author chest tables, and a table authored after this sweep
would keep the collapsed row. Tables polis_vault already widened are detected and skipped,
so there is no S4b collision between the two modules.

GATE (verify, post-finalization): `svc_loot_breadth.audit_db` over the final db - every
mod-owned chest table must reach at least one item of EVERY weapon class at its own tier
(spear named explicitly), clear the per-tier pool floor, and keep Normal free of legendary
gear. Standalone twin: `py tools/gate_chest_loot_breadth.py <arz>`.
Negative tests: `py tools/debug/negtest_chest_breadth.py <arz>`.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import svc_loot_breadth as SLB

MODULE_NAME = 'chest_loot_breadth'


def _has_weapon_row(db, real):
    for _i, name, _w in SLB._slot_members(db, real, 1):
        if '\\weapons\\' in SLB._n(name):
            return True
    return False


def apply(db, tags):
    print("\n=== chest_loot_breadth: every mod chest pays every weapon class ===")
    lk = SLB.Lookup(db)
    masters = SLB.ensure_masters(db, lk)
    if not masters:
        print("  LOOT BREADTH: no masters authored (donors missing); sweep skipped.")
        return
    lk.refresh()

    targets = []
    exempt_low = {SLB._n(k) for k in SLB.EXEMPT}
    for table in SLB.chest_tables(db, lk):
        if SLB._n(table) in exempt_low:
            continue
        targets.append(table)
    # The DRX donors every mod chest is cloned from (the esti / hidden-bloodcave mega
    # chest is one of them, so the canonical + Steam blood-cave chest gains the breadth
    # too, and no future clone can re-inherit the collapsed row).
    donor_tiers = {SLB._n(p): t for t, p in SLB.DRX_DONORS.items()}

    widened = 0
    retargeted = 0
    skipped_no_weapons = []
    for table in targets + [p for p in SLB.DRX_DONORS.values()]:
        real = lk.real(table)
        if not real:
            continue
        tier = donor_tiers.get(SLB._n(table)) or SLB.infer_tier(db, real, lk)
        if tier is None:
            skipped_no_weapons.append('%s (no tier-identifiable member)' % real)
            continue
        if not _has_weapon_row(db, real):
            skipped_no_weapons.append('%s (no weapon row)' % real)
            continue
        if SLB.widen_weapon_row(db, real, tier, lk):
            widened += 1
        if SLB.retarget_guaranteed_weapon(db, real, tier, lk):
            retargeted += 1

    print("  LOOT BREADTH: %d chest table(s) in scope + %d DRX donor(s); weapon row "
          "widened on %d, guaranteed weapon slot re-aimed on %d."
          % (len(targets), len(SLB.DRX_DONORS), widened, retargeted))
    if skipped_no_weapons:
        # Never silent: a chest table with no weapon row cannot be widened, and the
        # verify() gate below will fail it unless it is EXEMPT with a reason.
        print("  LOOT BREADTH: %d table(s) carry no weapon row and were NOT widened:"
              % len(skipped_no_weapons))
        for s in skipped_no_weapons:
            print("      %s" % s)
    for k, why in sorted(SLB.EXEMPT.items()):
        print("  LOOT BREADTH: EXEMPT %s - %s" % (k.rsplit('\\', 1)[-1], why))
    print("=== chest_loot_breadth done ===\n")


def verify(db, tags):
    """Fail-loud build-wide breadth gate over the FINAL assembled db."""
    problems, stats = SLB.audit_db(db)
    if problems:
        for p in problems[:20]:
            print("  CHEST BREADTH OFFENDER: %s" % p)
        raise SystemExit("chest_loot_breadth gate FAILED: %d problem(s); a mod chest "
                         "cannot pay every weapon class at its own tier (the "
                         "no-legendary-spears defect class)" % len(problems))
    if stats:
        worst = min(stats.items(), key=lambda kv: kv[1][1])
        print("  chest_loot_breadth gate PASS: %d mod chest table(s) audited; every one "
              "pays all %d weapon classes at its own tier (SPEAR included). Thinnest "
              "pool: %s [%s] = %d items."
              % (len(stats), len(SLB.REQUIRED_WEAPON_CLASSES),
                 SLB._n(worst[0]).rsplit('\\', 1)[-1], worst[1][0], worst[1][1]))
    else:
        raise SystemExit("chest_loot_breadth gate FAILED: no mod chest loot table was "
                         "audited at all (scope rule broken - it must never be empty)")
