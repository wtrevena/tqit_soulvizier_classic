r"""orb_loot_breadth - WILL 2026-08-10 (R-210): the uber's MYSTICAL ORB pays every
class too.

WILL, VERBATIM: "for the mystical orbs that the uber monsters drop, the items
should drop with increased breadth as well so all classes of items could be
dropped"

WHAT THIS MODULE IS. R-180 fixed the CHESTS that morning: every mod chest now names
the aggregate weapon master `svc_unique_weapons_{n,e,l}01`, so legendary spears went
0 -> 22. Will's "as well" is the other half of the loot economy - the on-death orb.
MEASURED on the build76 ship arz: the orb tables carry the IDENTICAL collapsed
weapon row (`1h_all_*01` = axe/club/sword, bow and staff named directly, SPEAR
forgotten), so **0 spears were reachable from 15 of the 18 uber orb tables, at every
tier and every difficulty**. The three that were already fine are orb05's
`svc_uberorb_apex_*`, and only because they live in an `\svc\` folder and R-180's
mod-ownership sweep therefore reached them. This module finishes that sweep on the
tables the ownership rule could not see, from the same shared implementation.

The full RCA, the derived scope, the measured before/after table and every
preserved-field law live in `tools/svc_orb_breadth.py`. Read that file first.

WHAT IT WRITES - per in-scope orb loot table, and nothing else:
  * the tier-correct breadth master into the ONE free loot1 member slot (w800);
  * loot1Chance (weapons) 13/14 -> 40 and loot6Chance (shields) 13/14 -> 30, the
    values orb05 has already shipped since build75, via a helper that takes
    max(existing, target) and refuses to switch a dormant slot on.
Every other field of every table, and every proxy / accessory pool / chest record
in every chain, is proven field-identical after the sweep (S4-SCOPE below). So
numSpawn equations, the relic row, the potion row, the armour rows, the mesh, the
gold generator, the level equation and `description tagEndChest02` are exactly what
shipped: only the CLASSES the weapon row can pay widen.

ORDERING. Registered after `chest_loot_breadth` (which authors the masters - both
callers use the same idempotent builder, so there is no collision) and after
`red_uber_orbs` (which ADDS uber consumers, and the scope is derived from uber
carriers), immediately before the no-op `visuals`. An S4b collision WARN naming
this module and `chest_loot_breadth` would be a real finding: their table sets are
disjoint by construction (`chest_loot_breadth` sweeps mod-owned `\svc\` tables,
this one sweeps the uber drop chains) EXCEPT for orb05's three apex tables, which
are already widened by the time this module runs and are therefore a no-op here.

GATE (verify, post-finalization): `svc_orb_breadth.audit_db` over the final db -
O1 every in-scope table reaches every weapon class at its own difficulty (SPEAR
named explicitly), O2 the per-branch pool floor, O2b the breadth master is still
NAMED in the weapon row, O3 no legendary GEAR on the normal branch, O4 every uber
orb chain resolves end to end at all three difficulties and the derived scope never
shrinks below its measured floor.
Standalone twin: `py tools/gate_orb_loot_breadth.py <arz>`.
Negative tests:  `py tools/debug/negtest_orb_breadth.py <arz>`.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import svc_loot_breadth as SLB
import svc_orb_breadth as SOB

MODULE_NAME = ("orb loot breadth - every uber's mystical orb pays every weapon "
               "class, SPEAR included (R-210)")


def _base_rows(required, who):
    """The base-game Monster.tpl rows, via red_uber_orbs' already-cached loader.

    The scope is derived over mod UNION base for R-200's HOLE 2 reason: a roster
    derived over the mod db alone is blind to a base-only uber. Never fatal here -
    every record this module WRITES lives in the mod overlay - so a missing base
    arz downgrades LOUDLY (the fx_dangling_cleanup B-GATE-HARDEN-1 idiom) instead
    of silently narrowing the scope.
    """
    try:
        import red_uber_orbs as RUO
    except ImportError as exc:                       # pragma: no cover - packaging
        print("  [orb_loot_breadth] WARNING cannot import red_uber_orbs (%s); the "
              "uber roster runs MOD-ONLY this build. No silent pass: this line IS "
              "the downgrade." % exc)
        return None
    rows = RUO.load_base_rows(required=required, who=who)
    if not rows:
        print("  [orb_loot_breadth] WARNING base-game universe unavailable; the "
              "uber roster runs MOD-ONLY this build (a base-only uber's orb cannot "
              "be seen). No silent pass: this line IS the downgrade.")
    return rows


def apply(db, tags):
    print("\n=== patches-registry: %s ===" % MODULE_NAME)
    lk = SLB.Lookup(db)
    base_rows = _base_rows(required=False, who='orb_loot_breadth.apply()')

    # ── 1. the shared masters (idempotent; chest_loot_breadth normally wins) ──
    masters = SLB.ensure_masters(db, lk, verbose=False)
    if not masters:
        raise SystemExit(
            "[orb_loot_breadth] the breadth masters could not be authored, so the "
            "orbs cannot be widened. `chest_loot_breadth` authors the same three "
            "records from the same builder and runs first, so this means the "
            "donor `all_l01` LootMasterTable is missing - a build-input problem, "
            "not something to skip past.")
    lk.refresh()

    # ── 2. scope, measured and printed (the wave report IS the build log) ────
    carriers = SOB.uber_proxies(db, base_rows)
    chains = SOB.orb_chains(db, lk, base_rows)
    tables = SOB.scope_tables(db, lk, base_rows)
    print("  ORB BREADTH: %d uber carrier(s) name %d proxy/proxies -> %d loot "
          "table(s) across %d difficulty chain(s)"
          % (sum(len(v) for v in carriers.values()), len(carriers), len(tables),
             sum(1 for c in chains if c[1] is not None)))
    for proxy_l in sorted(carriers):
        real = lk.real(proxy_l)
        print("      %-34s %2d uber carrier(s)%s"
              % (proxy_l.rsplit('\\', 1)[-1], len(carriers[proxy_l]),
                 '' if real else '   ** DOES NOT RESOLVE (verify() will red) **'))
    if len(carriers) < SOB.MIN_PROXIES or len(tables) < SOB.MIN_TABLES:
        raise SystemExit(
            "[orb_loot_breadth] SCOPE COLLAPSED at apply(): %d proxy/proxies and %d "
            "table(s), measured floor %d/%d. Widening nothing while reporting "
            "success is the exact failure this module exists to prevent."
            % (len(carriers), len(tables), SOB.MIN_PROXIES, SOB.MIN_TABLES))

    # ── 3. the before-image for the scope proof ─────────────────────────────
    watched = [t for t, _tier in tables.values()]
    watched += [c[0] for c in chains if c[1] is not None]      # proxies
    watched += [c[2] for c in chains if c[2]]                  # accessory pools
    watched += [c[3] for c in chains if c[3]]                  # chest records
    before = SOB.snapshot(db, watched)

    # ── 4. the widening (the R-180 contract, applied per difficulty slot) ────
    changes, _ = SOB.widen_chains(db, lk, base_rows)
    print("  ORB BREADTH: weapon row widened on %d of %d table(s); %d already "
          "carried it (orb05's apex tables, widened by chest_loot_breadth)."
          % (len(changes), len(tables), len(tables) - len(changes)))

    # ── 5. S4-SCOPE PROOF: only the two allowed fields moved, and only up ────
    after = SOB.snapshot(db, list(before))
    illegal = []
    raised = 0
    for rec, bf in before.items():
        for field in SOB.field_diffs(bf, after.get(rec, {})):
            if not SOB.is_allowed_change(field):
                illegal.append('%s.%s' % (rec.rsplit('\\', 1)[-1], field))
                continue
            if field.endswith('Chance'):
                old = float((bf.get(field, ([0], None))[0] or [0])[0])
                new = float((after[rec].get(field, ([0], None))[0] or [0])[0])
                if new < old:
                    illegal.append('%s.%s LOWERED %g -> %g'
                                   % (rec.rsplit('\\', 1)[-1], field, old, new))
                else:
                    raised += 1
    if illegal:
        raise SystemExit(
            "[orb_loot_breadth] SCOPE PROOF FAILED: %d field(s) outside the allowed "
            "set moved (allowed: loot1Name*/loot1Weight* on the free member slot, "
            "loot1Chance, loot6Chance, and chances may only RISE): %s. Every orb's "
            "identity - numSpawn equations, the relic/potion/armour rows, the mesh, "
            "the gold generator and the level equation - must come through this "
            "sweep byte-unchanged." % (len(illegal), sorted(illegal)[:12]))
    print("  ORB BREADTH: scope proof PASS - %d record(s) watched (tables + every "
          "proxy/pool/chest in every chain); the only fields that moved are the one "
          "added loot1 member and %d chance raise(s), no chance lowered, no member "
          "removed." % (len(before), raised))
    print("=== orb_loot_breadth done ===\n")


def verify(db, tags):
    """Fail-loud orb-breadth gate over the FINAL assembled db."""
    lk = SLB.Lookup(db)
    base_rows = _base_rows(required=False, who='orb_loot_breadth.verify()')
    problems, stats = SOB.audit_db(db, lk, base_rows)
    if problems:
        for p in problems[:20]:
            print("  ORB BREADTH OFFENDER: %s" % p)
        raise SystemExit(
            "orb_loot_breadth gate FAILED: %d problem(s); an uber's mystical orb "
            "cannot pay every weapon class at its own difficulty (the "
            "no-legendary-spears defect class, R-180's twin on the orb side)"
            % len(problems))
    if not stats:
        raise SystemExit(
            "orb_loot_breadth gate FAILED: no uber orb table was audited at all "
            "(the scope derivation broke - it must never be empty)")
    worst = min(stats.items(), key=lambda kv: kv[1][1])
    spearless = [t for t, s in stats.items() if not s[2].get('WeaponHunting_Spear')]
    if spearless:                                   # belt and braces over O1
        raise SystemExit(
            "orb_loot_breadth gate FAILED: %d table(s) still reach no spear at "
            "their own tier: %s" % (len(spearless), sorted(spearless)[:6]))
    print("  orb_loot_breadth gate PASS: %d uber orb loot table(s) audited; every "
          "one pays all %d weapon classes at its own difficulty (SPEAR included). "
          "Thinnest pool: %s [%s] = %d items."
          % (len(stats), len(SLB.REQUIRED_WEAPON_CLASSES),
             SLB._n(worst[0]).rsplit('\\', 1)[-1], worst[1][0], worst[1][1]))
