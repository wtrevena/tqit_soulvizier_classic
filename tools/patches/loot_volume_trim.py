r"""loot_volume_trim - how MUCH the chests pay (R-240, Will 2026-08-11).

WILL, VERBATIM (2026-08-11):
  "we probably need to trip the loot-volume trim, especially on the steam version
   where maybe from the two chests, you get guaranteed 1 legendary item. on the
   testhub version we can spawn more that is fine."

THIS IS THE SAY-SO `BL-R181-DEBT-5` WAS WAITING FOR. R-181 measured the lever, named
it, and refused to pull it: "numSpawn is the volume lever, and lowering it is a WILL
DECISION, logged as BL-R181-DEBT-5 rather than taken quietly here - it would reduce
drops per open, which is exactly what non-reduction forbids without his say-so." Three
waves then raised composition while volume stood still, which is why the shipped b83
cage pays 36.4 Legendary-grade gear pieces for two chests opened once.

Non-reduction is suspended for VOLUME AND VOLUME ONLY. This module touches exactly two
fields per record - `numSpawnMinEquation` and `numSpawnMaxEquation` - and the scope
proof below fails the build if anything else moves. No member is removed, no weight or
group chance is lowered, the guaranteed 100% row stays 100%, and no pool loses a
single item. Every breadth and distribution property b75-b83 shipped therefore survives
verbatim, and the cross-gate proof is not a claim: `armor_loot_breadth.verify` and
`chest_loot_breadth.verify` both run AFTER this module on the same db.

WHY IT IS REGISTERED LAST (before the no-op `visuals`)
------------------------------------------------------
Two reasons, both load-bearing:
  1. VOLUME IS AN OVERRIDE. `apply_svc_patches` writes `*2.4/*2.8` onto 27 hoard
     tables and `polis_vault` writes the cage's own multipliers. Running last makes
     this module the single authority on volume - an earlier slot would have it
     silently overwritten by whichever module happens to run later, which is the
     failure mode that produced BL-R181-DEBT-7.
  2. THE TESTHUB TWIN IS A CLONE OF THE FINISHED CANONICAL CHAIN. Cloning after every
     breadth and armour edit has landed means the twin inherits all of it for free and
     there is no second copy of the tuning to keep in step. Clone first, trim second -
     `svc_loot_volume.apply_wave` enforces that order in one place.

THE TESTHUB SPLIT, AND THE MAP COUPLING IT CREATES
---------------------------------------------------
There is ONE database and both map variants read it, so "canonical trims, TESTHUB stays
rich" can only be expressed in the RECORDS. The four TESTHUB-only farm duplicates (Will
2026-08-08) currently name the same two container records as the two canonical
placements, so this module clones the whole cage chain to a `_hub` twin and
`build_section_surgery.build_hub_extra_specs` points those four placements at the twin.

  ⚠ The map half needs the TESTHUB Levels variant REBUILT (`SVC_TEST_HUB=1`) to reach
  the game. Until then the four duplicates keep naming the canonical records and DEV's
  cage is trimmed like canonical. That is the SAFE direction - DEV under-pays, Steam
  never over-pays - and the canonical `B41_SPECS` is untouched, so
  `local/Levels_merged.arc` stays byte-identical and the Steam delta stays arz-only.

GATE: `verify()` below runs the whole R-240 contract (V1-V7b) plus this module's own
scope proof. Standalone twin: `py tools/gate_loot_volume.py <arz>` (add `--apply` on a
pre-wave arz, `--calibrate` to re-derive every threshold).
Negatives: `py tools/debug/negtest_loot_volume.py <arz>` - and they plant in BOTH
directions, because a volume contract has two ways to be wrong.

⚠ APPLY-ONCE, NOT IDEMPOTENT. `apply_wave` refuses a second run and says why: the twin
would be re-cloned off the ALREADY-TRIMMED canonical records and the canonical-vs-TESTHUB
split would silently cease to exist (measured: 58 tables drift). `run_registry` already
asserts each module runs exactly once, so a build cannot hit this - the guard is for
anyone driving the wave by hand, and for the `--apply` flag on the standalone gate.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import svc_chest_artifacts as SCA
import svc_loot_breadth as SLB
import svc_loot_volume as SLV

MODULE_NAME = ("loot volume trim - the canonical chests pay a run's worth, not a "
               "vendor's stock, and the TESTHUB farm keeps its own (R-240)")

# The ONLY two fields this module may move on an existing record. Everything else on
# an in-scope loot table is that surface's identity: its members, its weights, its
# group chances, its guaranteed row, its relic tier.
_ALLOWED = ('numSpawnMinEquation', 'numSpawnMaxEquation')


def apply(db, tags):
    print("\n=== patches-registry: %s ===" % MODULE_NAME)
    lk = SLB.Lookup(db)

    # ── 1. the before-image of every record the trim can reach ───────────────
    scope0 = SLV.scope_tables(db, lk)
    if not scope0:
        raise SystemExit(
            "[loot_volume_trim] SCOPE EMPTY: no loot surface was derived from "
            "svc_armor_breadth.all_surfaces. Trimming nothing while reporting success "
            "is exactly how BL-R181-DEBT-7 shipped fifteen starving surfaces through "
            "two green gates.")
    before = {real: {k.split('###')[0]: list(tf.values)
                     for k, tf in (db.get_fields(real) or {}).items()}
              for _k, (real, _t, _h) in scope0.items()}

    # ── 2. the wave: clone the TESTHUB twin, THEN trim canonical ─────────────
    made, changes = SLV.apply_wave(db, lk, verbose=True)
    lk.refresh()

    # ── 3. SCOPE PROOF: on a pre-existing record, ONLY numSpawn moved ────────
    # The twin's records are NEW, so they are not in `before` and are not watched here;
    # V5 is what proves the twin came out right, by comparing it against its canonical
    # counterpart in the finished db rather than by trusting this pass.
    illegal = []
    for real, was in before.items():
        now = {k.split('###')[0]: list(tf.values)
               for k, tf in (db.get_fields(real) or {}).items()}
        base = SLB._n(real).rsplit('\\', 1)[-1]
        for field in sorted(set(was) | set(now)):
            if was.get(field, []) == now.get(field, []):
                continue
            if field not in _ALLOWED:
                illegal.append('%s.%s %r -> %r'
                               % (base, field, was.get(field), now.get(field)))
    if illegal:
        raise SystemExit(
            "[loot_volume_trim] SCOPE PROOF FAILED: %d field(s) outside "
            "numSpawnMin/MaxEquation moved on an existing loot table: %s. This module "
            "is allowed to change how MUCH a surface pays and nothing else - the "
            "moment it touches a member, a weight or a group chance it is silently "
            "redoing R-180/R-181/R-220's work, and the breadth and distribution gates "
            "that run after it would be validating a different wave than the one "
            "anyone reviewed." % (len(illegal), sorted(illegal)[:12]))

    # ── 4. the numbers, in the build log, because the report IS the log ──────
    for real, tier, ch in changes[:8]:
        print("    %-46s [%s] %s"
              % (SLB._n(real).rsplit('\\', 1)[-1], tier, '; '.join(ch)))
    if len(changes) > 8:
        print("    ... and %d more (full table: py tools/gate_loot_volume.py <arz> "
              "--calibrate)" % (len(changes) - 8))
    SLV.calibrate(db, lk)
    print("  VOLUME: scope proof PASS - %d pre-existing record(s) watched, only "
          "numSpawnMin/MaxEquation moved; %d twin record(s) authored."
          % (len(before), len(made)))
    print("=== loot_volume_trim done ===\n")


def verify(db, tags):
    """The R-240 contract (V1-V7b) plus Will's artifact ruling, on the FINAL db.

    Run as a verify() rather than at apply() time deliberately: every other loot module
    has already run by then, so what this measures is the volume the player actually
    gets, not the volume this module left behind a moment before something else moved
    it. If a future module re-inflates a surface, V1/V6 red here and name it.
    """
    lk = SLB.Lookup(db)
    report = {}
    problems = SLV.problems(db, lk, report=report)
    if problems:
        for p in problems[:16]:
            print("  VOLUME OFFENDER: %s" % p)
        raise SystemExit(
            "loot_volume_trim gate FAILED: %d loot surface(s) pay outside their "
            "committed volume band. Will's ruling has two halves and this gate holds "
            "both - the canonical chests may not go back to paying a vendor's stock, "
            "and the TESTHUB farm may not be trimmed away with them." % len(problems))

    art = SCA.problems(db, lk)
    if art:
        for p in art[:16]:
            print("  ARTIFACT OFFENDER: %s" % p)
        raise SystemExit(
            "loot_volume_trim gate FAILED: %d equippable-artifact finding(s). Will "
            "2026-08-11: \"artifacts should never drop from chests\"." % len(art))

    print("  loot_volume_trim gate PASS: %d canonical loot table(s) inside the volume "
          "ceilings (worst %.2f gear/open on %s, cap %.2f); the two-chest cage run pays "
          "%s and still guarantees one at >= %.0f%% of runs on the continuous spawn "
          "model and >= %.0f%% under integer truncation (both gated - the engine's "
          "rounding mode is unproven, BL-R240-DEBT-5); %d TESTHUB twin table(s) "
          "held at shipped volume by a FLOOR; every in-scope numSpawn equation still "
          "carries `numberOfPlayers` and spawns >= %.2f iteration(s) solo. Artifact "
          "ruling: %s."
          % (report.get('canonical', 0), report.get('worst_surface', (0, ''))[0],
             report.get('worst_surface', (0, '-'))[1], SLV.CANON_MAX_GEAR_PER_OPEN,
             SLV.CANON_MAX_CAGE_RUN, 100.0 * SLV.MIN_P_AT_LEAST_ONE,
             100.0 * SLV.MIN_P_AT_LEAST_ONE_TRUNC,
             report.get('hub', 0), SLV.MIN_SPAWN_MIN_SOLO, SCA.pass_line(db, lk)))
