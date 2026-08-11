r"""svc_loot_ownership.py - WHO OWNS A LOOT TABLE'S DISTRIBUTION (R-181 / R-220,
BL-R181-DEBT-7).

THE DEFECT CLASS THIS FILE EXISTS TO KILL, stated as the bug report it came from
--------------------------------------------------------------------------------
R-180 gave every mod chest a weapon row that pays every class. R-181 gave every mod
chest armour at weapon-row parity, and shipped a per-surface distribution gate.
R-220 then widened FIFTEEN MORE loot tables - `uberorb_default_*` and
`boss_charon_*01b`, the uber mystical orbs - and those fifteen live OUTSIDE the
`\svc\` folder that R-181's ownership rule keys on. So R-220 widened their WEAPON
row and nobody at all owned their ARMOUR: measured on the shipped build80 arz they
ran weapon:armour 3.4:1 to 8.4:1 with a thinnest worn slot of 0.007 pieces per open
against the D7 floor of 0.52. Both fail-loud gates were GREEN the whole time,
because a table no module claims is a table no gate audits.

The hole was never "someone forgot a table". It was that OWNERSHIP WAS A FOLDER
NAME. A module could write a loot table that no distribution surface covered, and
nothing in the build could tell.

THE RULE THIS FILE ENFORCES
---------------------------
    Every loot table a module WRITES must be inside the distribution gate's
    surface set.

Not "every mod-owned table" - every WRITTEN table, whoever wrote it and wherever it
lives. Coverage is proven from the writes, so a future lane that widens a sixteenth
table in a new folder is inside the contract the moment it writes, with no list to
remember to update.

EXACTLY WHAT THE WITNESSES REACH, because a gate must not overstate itself
--------------------------------------------------------------------------------
The round-2 vet of this lane found the PASS line claiming "every loot table written in
this build" while neither witness could see `tools/apply_svc_patches.py` - the 19k-line
monolith, which runs OUTSIDE `run_registry` (so no touch log) and writes some loot rows
directly (so no builder). Enforced reach, stated plainly:

  * REGISTRY MODULES - both witnesses.
  * ANY caller of the four shared builders, anywhere, including dry runs and the
    negative battery - the ledger.
  * THE MONOLITH'S HOARD AUTHORING - the 27 `svc_*hoard_loot_{01,02,03}` gear containers
    it clones from the blood-cave mega chest. These now call `note_write` at both
    authoring sites, so the ledger covers them; measured, all 27 are inside the audited
    surface set.

  NOT covered, by decision, and registered as BL-R181-DEBT-10: the monolith's
  `_restore_thrown_weapon_drops`, which writes `loot6Name5/6` on base-game
  `containers\defaultloot\` monster tables. Those writes copy a value straight OUT of the
  base arz - they restore a base-game row to its base-game shape rather than widening a
  mod surface - and base-game MONSTER loot is BL-R181-DEBT-2, an explicit Will decision.
  Pulling them into the surface set would demand mod distribution thresholds of base-game
  monster tables, which is a design change, not a gate fix.

TWO INDEPENDENT WITNESSES, because one of them is only available inside a build
--------------------------------------------------------------------------------
1. THE LEDGER (this module). Every shared loot builder - `svc_loot_breadth`'s
   `widen_weapon_row` / `set_guaranteed_theme` / `retarget_guaranteed_weapon` and
   `svc_armor_breadth`'s `widen_armor_rows` - calls `note_write()`. Those four
   functions are the ONLY sanctioned way to move a loot row in this codebase, so
   any caller anywhere (registry module, standalone tool, dry run, negtest) is
   recorded. This witness works outside a build, which is what makes the negative
   test possible.
2. THE REGISTRY TOUCH LOG. `tools/patches/__init__.run_registry` already records
   every `db._modified.add()` against the module that made it, and now persists it
   as `db._registry_touch_log` for the post-finalization gates. That witness catches
   a module that writes loot fields RAW, bypassing the builders entirely.

Neither witness may be silently absent: `svc_armor_breadth.ownership_problems`
ANNOUNCES a missing touch log rather than passing quietly (the B-GATE-HARDEN-1
idiom), and the ledger is process-global so it cannot go missing at all.

DELIBERATELY NOT A REGISTRY OF NAMES. There is no list of tables here and there
never may be: the moment coverage is a typed list, the next lane's table is outside
it and the gate is green again. Coverage is DERIVED - see
`svc_armor_breadth.all_surfaces`, which reads R-220's own scope derivation.
"""

# {norm(table): sorted set of writer labels}. Process-global on purpose: the whole
# point is that a table written ANYWHERE in this process is visible to the gate that
# runs at the end of it. A build is one process.
_WRITES = {}


def _n(s):
    return str(s).replace('/', '\\').lower()


def note_write(table, writer):
    """Record that `writer` wrote loot rows on `table`. Idempotent per (table, writer).

    Called from the shared builders themselves rather than from their callers, so a
    new caller cannot forget to register - registering IS writing.
    """
    if not table:
        return
    _WRITES.setdefault(_n(table), set()).add(str(writer))


def writes():
    """{norm(table): [writer, ...]} - every loot table written in this process."""
    return {t: sorted(w) for t, w in _WRITES.items()}


def writers_of(table):
    return sorted(_WRITES.get(_n(table), ()))


def reset():
    """Drop the ledger. ONLY for tests that need a clean process-global (the negative
    battery builds several throwaway dbs in one process)."""
    _WRITES.clear()


def registry_writes(db):
    """{norm(table): [module, ...]} from the registry's own per-module touch log.

    Returns None - never an empty dict - when the log is absent, so the caller can
    tell "no module wrote a loot table" apart from "this gate is running blind" and
    announce the difference.
    """
    log = getattr(db, '_registry_touch_log', None)
    if log is None:
        return None
    out = {}
    for module, record in log:
        out.setdefault(_n(record), set()).add(str(module))
    return {t: sorted(m) for t, m in out.items()}
