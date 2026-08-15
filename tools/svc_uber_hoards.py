r"""svc_uber_hoards.py - THE UBER/BOSS CHEST GENEROSITY CONTRACT (Will 2026-08-14, R-251).

WILL, VERBATIM (2026-08-14), five separate reports in one play session:
  (BL-W0814-11) "are you kidding me. this is outrageous ... literally just dropped two
                 items one thing of gold and incarnation of guan-yu's grace"
  (BL-W0814-13) "same problem with the chest guarded by tantalus"
  (BL-W0814-5)  "aphoryteus (spelled wrong) dread hoard is a terrible chest, it got
                 nerfed somewhere along the way and needs to drop more items"
  (BL-W0814-2)  "the obsidian hoard chests ... in locations such as the obsidian halls
                 are still nerfed too much. if these share the same record as the chest -
                 toxeus the murderer, devourer of blood hidden's chest we need to
                 seperate those records since those should be tuned differently"
  (BL-W0814-7)  "the gift box in the secret places need to increase the number of items
                 dropped by 3x"

THE ONE SHARED CAUSE, MEASURED ON THE SHIPPED b888f022 ARZ - NOT REASONED
--------------------------------------------------------------------------
Five chests nerfed identically is one cause, and it is not a number. It is a WIRE:

  `apply_svc_patches._svc_standardize_boss_chests` (b42 round-2, an implementer's scope
  decision - `docs/reports/b42_fixedboss_dedup.md` S3.3, never a Will ruling) ran at
  finalization and rewrote EVERY placed-uber hoard chest's `tables` field to a BASE-GAME
  `records\item\containers\defaultloot\boss_default_<lo>-<hi>.dbr` - "the Cyclops chest
  FORM". Its own report says the consequence out loud: *"The old bespoke guaranteed-unique
  loot tables are left unreferenced."*

MEASURED CONSEQUENCES on the shipped arz (`tools/gate_uber_hoard_generosity.py` prints
every one of these as a table):
  * 21 of the 30 uber/boss hoard chests named a base-game table, not their own.
  * 18 of the 27 `svc_*hoard_loot_0N` records had ZERO references anywhere in 51,312
    records - dead weight the player could never open. (The nine that survived are the
    three general-guard families, which the repoint roster never listed.)
  * A tenth family, `svc_dorushoard_*` - the Great Hall of Propontis chest - had no
    table of its own AT ALL, which is the second half of the same defect: see below.
  * So R-180 (weapon breadth), R-181 (armour parity) and R-220 (orb/chest widening)
    spent three waves tuning records nothing opens, and FOUR fail-loud gates stayed
    green on them. The R-240 gate record's own "hoards 1.730 gear/open" line is a
    measurement of dead records.
  * What the player actually opened instead: S = (6.90 + 7.82)/2 = 7.36 spawn
    iterations at group chances 14/27/10/21/25/14 (sum 1.11) - against the Devourer's
    stash, the chest Will holds up as correct, at S = 18.96 and 40/40/-/21/40/40
    (sum 1.81). And crucially NO guaranteed row: every mod hoard table ships
    `loot3Chance = 100` with a tier-correct unique + relic; `boss_default_*` ships 10.
  * `svc_dorushoard_*` - the Great Hall of Propontis chest, BL-W0814-11 - is a
    `clone_record` of the Obsidian Hoard chest. Before the repoint it therefore SHARED
    `svc_obsidianhoard_loot_0N`, and it still carries `description = tagSVCObsidianHoard`,
    so a chest in Propontis is LABELLED "Obsidian Hoard" in game. That is Will's
    record-separation report, confirmed to the byte, and it is why he wrote "the obsidian
    hoard chests ... in locations such as the obsidian halls".
  * R-240's volume trim then hit the same family a second time. For the 21 dead tables
    that was invisible; for the SIX general-guard tables - the one family still wired to
    its own loot - it was real: `*2.4/*2.8` -> `*0.2188/*0.25`, the most starved gear
    surface in the mod.

WHAT R-251 DOES, AND THE LINE IT DOES NOT CROSS
------------------------------------------------
1. WIRING (the shared cause, fixed once, at the cause). `_svc_wire_boss_hoard_chests`
   replaces the repoint: every hoard chest names ITS OWN `svc_<family>hoard_loot_<tier>`,
   and the missing Dorus family is authored as its own records in the CONTENT pass so it
   is a separate surface every breadth module and gate sees. One edit, all 30 chests,
   and Will's record-separation ask satisfied structurally rather than per chest.
2. VOLUME (the second nerf, undone by scope). The family LEAVES R-240's trim scope
   (`svc_loot_volume.R251_UBER_HOARD_EXEMPT`) exactly the way R-247.7(a) took the
   Devourer's stash out, so the tables keep the volume the monolith AUTHORS them with -
   `(3+(1.8*numberOfPlayers))*2.4` / `*2.8` - and this file is their volume authority.
   Nothing is invented: 2.4/2.8 is the mod's own authored value, it is what the TESTHUB
   cage twin still carries, and it sits BELOW the Devourer's stash 3.8/4.1, so the
   mega chest stays the crown exactly as the R-247 record requires.
3. THE GIFT BOX (Will's literal number). The Secret Present box - `proxyspawner_sp_chest`
   -> `proxy_sp_chest` -> `sp_chest_0N` (`description = tagSecretPresentBOX`) ->
   `loottable_sp_0N`, placed 5x across DarkForestEnter / SecretForest2 / PillagedVillage,
   which is why Will wrote "the secret places" plural - gets its item count multiplied by
   EXACTLY 3: `*1.8/*2.1` -> `*5.4/*6.3`.

NOT TOUCHED, deliberately, and each for a stated reason:
  * the polis-vault cage - R-240's trim IS what Will asked for there ("from the two
    chests, you get guaranteed 1 legendary item"); he has not complained about it. This
    is also why `gate_loot_distribution`'s D7X2 anchor stays green: that anchor is
    derived from the CAGE's post-trim volume, and the cage does not move here.
  * every orb table - R-242 shipped 0/50/75 by difficulty and froze the apex. Will's
    five reports are CHESTS.
  * the Devourer's stash - R-247.7(a) already owns those three records.
  * COMPOSITION anywhere - members, weights, group chances and the guaranteed row belong
    to R-180/R-181/R-220. R-251 moves a `tables` pointer and a `numSpawn` multiplier.

Shared by `tools/gate_uber_hoard_generosity.py` (standalone), the in-build gate
`tools/patches/uber_hoard_generosity.verify()` and `tools/debug/negtest_uber_hoards.py`,
so the three can never disagree (the `gate_relic_difficulty_tiers` precedent).
"""
import re
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import svc_loot_breadth as SLB
import svc_loot_distribution as SLD

# ─────────────────────────────────────────────────────────────────────────────
# THE FAMILY, DERIVED FROM THE RECORD NAMES AND NEVER TYPED
#
# A typed roster is how BL-R181-DEBT-7 shipped fifteen starving surfaces through two
# green gates: the next lane's family is outside the list and the gate is green again.
# So the family is a NAME SHAPE - `<container>\svc_<fam>hoard_<01|02|03>.dbr` for the
# chest and `..._loot_<01|02|03>.dbr` for its table - and a new uber hoard is inside
# this contract the moment it is authored with the house naming.
# ─────────────────────────────────────────────────────────────────────────────
CONTAINER_DIR = r'records\drxitem\container'
TIERS = ('01', '02', '03')
TIER_LETTER = {'01': 'n', '02': 'e', '03': 'l'}

_CHEST_RE = re.compile(
    r'^records\\drxitem\\container\\svc_(?P<fam>[a-z0-9]+)hoard_(?P<tier>0[123])\.dbr$')
_TABLE_RE = re.compile(
    r'^records\\drxitem\\container\\svc_(?P<fam>[a-z0-9]+)hoard_loot_(?P<tier>0[123])\.dbr$')

# ── THE AUTHORED VOLUME (the value the monolith writes; this file gates it) ──
# `_svc_build_dedicated_hoard` and the Obsidian roulette both author every hoard table
# with these exact two equations. R-240 trimmed them; R-251 takes the family out of that
# trim's scope, so "the authored value" and "the shipped value" become the same thing
# again and this contract can assert an EXACT string rather than a band.
HOARD_BRACKET = '(3+(1.8*numberOfPlayers))'
HOARD_MIN_MULT = 2.4
HOARD_MAX_MULT = 2.8

# ── THE SECRET PRESENT (BL-W0814-7): Will's "3x", as a multiplier on the SV original ──
GIFT_TABLES = tuple(r'%s\loottable_sp_%s.dbr' % (CONTAINER_DIR, t) for t in TIERS)
GIFT_CHESTS = tuple(r'%s\sp_chest_%s.dbr' % (CONTAINER_DIR, t) for t in TIERS)
GIFT_BRACKET = '(1+(1.8*numberOfPlayers))'
GIFT_SV_MIN_MULT = 1.8          # measured on the shipped arz, identical on all 3 tiers
GIFT_SV_MAX_MULT = 2.1
GIFT_FACTOR = 3.0               # "increase the number of items dropped by 3x"
GIFT_MIN_MULT = GIFT_SV_MIN_MULT * GIFT_FACTOR      # 5.4
GIFT_MAX_MULT = GIFT_SV_MAX_MULT * GIFT_FACTOR      # 6.3

# ── THE CROWN: the Devourer's stash keeps the highest volume in the mod (R-247.7a) ──
STASH_TABLES = tuple(r'%s\loottable_hidden_bloodcave_%s.dbr' % (CONTAINER_DIR, t)
                     for t in TIERS)
STASH_MIN_MULT = 3.8

# ── The base-game family the b42 repoint sent every hoard chest to ──────────
BASE_LOOT_MARK = '\\containers\\defaultloot\\'

# The never-empty floor, READ from R-240 rather than re-typed so the two contracts can
# never disagree about what "a chest that opens and drops nothing" means (build28/29/30
# P0). The import is LAZY and must stay that way: `svc_loot_volume` imports THIS module
# at module level for its R-251 carve-out, so a module-level import back would be a
# cycle. Resolving it at call time keeps one definition and no cycle.
def _min_spawn_floor():
    from svc_loot_volume import MIN_SPAWN_MIN_SOLO
    return MIN_SPAWN_MIN_SOLO


# The tier reader, READ from `gate_relic_difficulty_tiers` for the same reason: one
# implementation of "what tier is this loot row", shared by the wire-walking gate and
# this family-walking one, so they can never disagree about a leak. Lazy for symmetry
# with the floor above and so this module stays importable from anywhere.
def _tier_check(db, lk, table, want, ctx):
    from gate_relic_difficulty_tiers import check_loot_table_tier
    return check_loot_table_tier(db, lk, table, want, ctx)


def format_eq(bracket, mult):
    """Render a multiplier the way the shipped records render one (`*2.4`, not
    `*2.400000`) so a re-run that computes the same number writes the same bytes.
    Byte-identical to `svc_loot_volume.format_eq` on purpose."""
    txt = ('%.4f' % mult).rstrip('0').rstrip('.')
    return '%s*%s' % (bracket, txt or '0')


HOARD_MIN_EQ = format_eq(HOARD_BRACKET, HOARD_MIN_MULT)
HOARD_MAX_EQ = format_eq(HOARD_BRACKET, HOARD_MAX_MULT)
GIFT_MIN_EQ = format_eq(GIFT_BRACKET, GIFT_MIN_MULT)
GIFT_MAX_EQ = format_eq(GIFT_BRACKET, GIFT_MAX_MULT)
GIFT_SV_MIN_EQ = format_eq(GIFT_BRACKET, GIFT_SV_MIN_MULT)
GIFT_SV_MAX_EQ = format_eq(GIFT_BRACKET, GIFT_SV_MAX_MULT)


def is_hoard_table(path):
    """Is this record one of the uber/boss hoard loot tables R-251 governs?

    Name-shape based and shared with `svc_loot_volume.R251_UBER_HOARD_EXEMPT`, so the
    trim's scope carve-out and this contract's scope are the SAME set by construction -
    they cannot drift into a gap the way a second typed list would."""
    return bool(_TABLE_RE.match(SLB._n(path)))


def is_hoard_chest(path):
    return bool(_CHEST_RE.match(SLB._n(path)))


def table_for(chest_path):
    """`svc_<fam>hoard_<tier>.dbr` -> its OWN `svc_<fam>hoard_loot_<tier>.dbr`."""
    m = _CHEST_RE.match(SLB._n(chest_path))
    if not m:
        return None
    return r'%s\svc_%shoard_loot_%s.dbr' % (CONTAINER_DIR, m.group('fam'), m.group('tier'))


def chests(db, lk=None):
    """{norm(chest): (real, family, tier)} for every uber/boss hoard chest in `db`."""
    lk = lk or SLB.Lookup(db)
    out = {}
    for name in db.record_names():
        m = _CHEST_RE.match(SLB._n(name))
        if m:
            out[SLB._n(name)] = (name, m.group('fam'), m.group('tier'))
    return out


def tables(db, lk=None):
    """{norm(table): (real, family, tier)} for every uber/boss hoard loot table."""
    lk = lk or SLB.Lookup(db)
    out = {}
    for name in db.record_names():
        m = _TABLE_RE.match(SLB._n(name))
        if m:
            out[SLB._n(name)] = (name, m.group('fam'), m.group('tier'))
    return out


def referrers(db, wanted):
    """{norm(table): [(record, field), ...]} - who NAMES each of `wanted`.

    A full-db string sweep rather than a check of the `tables` field alone: an orphan
    is "nothing anywhere points here", and the b42 defect proves that a table can be
    perfectly well-formed, perfectly tuned, and simply unreachable."""
    want = {SLB._n(w) for w in wanted}
    out = {w: [] for w in want}
    for rec in db.record_names():
        if SLB._n(rec) in want:
            continue                       # a table naming itself is not a referrer
        for key, tf in (db.get_fields(rec) or {}).items():
            for v in tf.values:
                if isinstance(v, str) and SLB._n(v) in want:
                    out[SLB._n(v)].append((rec, key.split('###')[0]))
    return out


def _solo(eq):
    v = SLD.eval_spawn(eq, players=1)
    return 0.0 if v is None else v


def _gv(lk, rec, field):
    v = lk.gv(rec, field)
    return v


def problems(db, lk=None, report=None):
    """The whole R-251 contract, H1-H8. Returns a list of problem strings (empty = GREEN).

    Every check names the record, what it found, what it expected, and which of Will's
    five reports it protects - because a gate line nobody can act on is a gate line
    nobody reads.
    """
    lk = lk or SLB.Lookup(db)
    rep = report if report is not None else {}
    out = []

    chest_map = chests(db, lk)
    table_map = tables(db, lk)
    rep['chests'] = len(chest_map)
    rep['tables'] = len(table_map)

    # ── H1 WIRING: every hoard chest names its OWN table ─────────────────────
    # THE shared-cause gate. This is the check that would have caught b42 the day it
    # shipped, and the one that reds on every pre-R-251 artifact by design.
    for key in sorted(chest_map):
        real, fam, tier = chest_map[key]
        want = table_for(real)
        got = _gv(lk, real, 'tables')
        gotn = SLB._n(got or '')
        if not got:
            out.append("H1 %s names NO loot table at all (`tables` empty). An uber "
                       "chest with no table opens and pays nothing."
                       % SLB._n(real).rsplit('\\', 1)[-1])
        elif gotn != SLB._n(want):
            why = (" - this is the b42 `_svc_standardize_boss_chests` repoint to the "
                   "base game's Cyclops-grade boss loot, the ONE shared cause behind "
                   "BL-W0814-2/-5/-11/-13" if BASE_LOOT_MARK in gotn else "")
            out.append("H1 %s names %s but its OWN table is %s%s"
                       % (SLB._n(real).rsplit('\\', 1)[-1],
                          gotn.rsplit('\\', 1)[-1],
                          SLB._n(want).rsplit('\\', 1)[-1], why))
        elif not lk.real(want):
            out.append("H1 %s names %s, which does not exist in the database"
                       % (SLB._n(real).rsplit('\\', 1)[-1],
                          SLB._n(want).rsplit('\\', 1)[-1]))

    # ── H2 NO ORPHANS: every hoard table is reachable from some container ────
    if table_map:
        refs = referrers(db, [t for (t, _f, _tr) in table_map.values()])
        orphans = sorted(k for k, v in refs.items() if not v)
        rep['orphans'] = len(orphans)
        for k in orphans:
            out.append("H2 %s is referenced by NOTHING in the database - a loot table "
                       "no container names is a table no player can open, and three "
                       "breadth waves tuned exactly this class of dead record"
                       % k.rsplit('\\', 1)[-1])

    # ── H3 VOLUME: the authored uber volume, exactly ─────────────────────────
    worst = (0.0, '-')
    for key in sorted(table_map):
        real, fam, tier = table_map[key]
        mn, mx = _gv(lk, real, 'numSpawnMinEquation'), _gv(lk, real, 'numSpawnMaxEquation')
        short = key.rsplit('\\', 1)[-1]
        if str(mn) != HOARD_MIN_EQ or str(mx) != HOARD_MAX_EQ:
            out.append("H3 %s carries numSpawn %r/%r; R-251 pins the family at %r/%r "
                       "(the value the monolith authors, kept by taking the family out "
                       "of R-240's trim scope). A drift here means a new writer appeared "
                       "or the R-251 carve-out stopped covering this record."
                       % (short, mn, mx, HOARD_MIN_EQ, HOARD_MAX_EQ))
        s = (_solo(mn) + _solo(mx)) / 2.0
        if s > worst[0]:
            worst = (s, short)
    rep['worst_hoard_spawn'] = worst

    # ── H4 FORM: co-op scaling kept, and the never-empty floor holds ─────────
    floor = _min_spawn_floor()
    for key in sorted(table_map):
        real, _f, _t = table_map[key]
        short = key.rsplit('\\', 1)[-1]
        for field in ('numSpawnMinEquation', 'numSpawnMaxEquation'):
            eq = str(_gv(lk, real, field) or '')
            if 'numberOfPlayers' not in eq:
                out.append("H4 %s.%s = %r lost its `numberOfPlayers` term. A bare "
                           "literal is the build28/29/30 P0 - the engine's evaluator "
                           "returned 0 and the chest opened and dropped NOTHING."
                           % (short, field, eq))
        lo = _solo(str(_gv(lk, real, 'numSpawnMinEquation') or ''))
        if lo < floor:
            out.append("H4 %s spawns %.3f iteration(s) solo, under the never-empty "
                       "floor %.2f" % (short, lo, floor))

    # ── H5 GUARANTEED ROW: the slot the base-game repoint destroyed ──────────
    for key in sorted(table_map):
        real, _f, _t = table_map[key]
        ch = _gv(lk, real, 'loot3Chance')
        try:
            chv = float(ch)
        except (TypeError, ValueError):
            chv = -1.0
        if abs(chv - 100.0) > 0.01:
            out.append("H5 %s has loot3Chance=%r, not 100. The guaranteed unique+relic "
                       "row IS what separates an uber hoard from a Cyclops chest, and "
                       "losing it is what Will opened as 'one thing of gold and "
                       "incarnation of guan-yu's grace'." % (key.rsplit('\\', 1)[-1], ch))

    # ── H6 THE GIFT BOX: Will's literal 3x ──────────────────────────────────
    for path in GIFT_TABLES:
        real = lk.real(path)
        short = SLB._n(path).rsplit('\\', 1)[-1]
        if not real:
            out.append("H6 %s is MISSING - the Secret Present box has no loot table" % short)
            continue
        mn, mx = _gv(lk, real, 'numSpawnMinEquation'), _gv(lk, real, 'numSpawnMaxEquation')
        if str(mn) != GIFT_MIN_EQ or str(mx) != GIFT_MAX_EQ:
            out.append("H6 %s carries numSpawn %r/%r; BL-W0814-7 is exactly 3x the SV "
                       "original (%r/%r -> %r/%r)"
                       % (short, mn, mx, GIFT_SV_MIN_EQ, GIFT_SV_MAX_EQ,
                          GIFT_MIN_EQ, GIFT_MAX_EQ))
        for field, eq in (('numSpawnMinEquation', mn), ('numSpawnMaxEquation', mx)):
            if 'numberOfPlayers' not in str(eq or ''):
                out.append("H6 %s.%s = %r lost its `numberOfPlayers` term (build28/29/30 P0)"
                           % (short, field, eq))

    # ── H7 SEPARATION: Will's record-separation ask, as an invariant ────────
    # No two hoard chests may share a loot table, and no hoard chest may share the
    # Devourer's stash tables. This is the check that makes "these should be tuned
    # differently" structural instead of a promise someone has to keep.
    seen = {}
    stash = {SLB._n(s) for s in STASH_TABLES}
    for key in sorted(chest_map):
        real, fam, tier = chest_map[key]
        got = SLB._n(_gv(lk, real, 'tables') or '')
        if not got:
            continue
        short = key.rsplit('\\', 1)[-1]
        if got in stash:
            out.append("H7 %s shares the Devourer's stash table %s. Will 2026-08-14: "
                       "\"we need to seperate those records since those should be tuned "
                       "differently\"." % (short, got.rsplit('\\', 1)[-1]))
        if got in seen and seen[got] != short:
            out.append("H7 %s and %s BOTH name %s - two uber chests on one loot record "
                       "cannot be tuned independently (BL-W0814-2)"
                       % (seen[got], short, got.rsplit('\\', 1)[-1]))
        seen.setdefault(got, short)

    # ── H8 TIER: the guaranteed row must match the table's OWN difficulty ────
    # R-251 round-2, and the reason it exists is the whole point of this lane. Will's
    # 2026-08-08 leak #2 fixed exactly this in `_svc_build_dedicated_hoard` and the
    # Obsidian ROULETTE kept writing the Normal-tier constants into all three tiers, so
    # a Legendary Obsidian Hoard guaranteed an Essence relic. It survived because
    # `gate_relic_difficulty_tiers` walks the WIRE (proxy -> pool -> chest -> `tables`)
    # and those chests named `boss_default_*` until R-251 - the b42 orphan blind spot,
    # measured: that gate reaches 51 branches on the shipped b888f022 and 81 after
    # R-251 wires the family up, and 8 of the 30 newly-reachable branches were leaks.
    #
    # So this check walks the FAMILY, not the wire: every hoard table is tier-checked
    # from its own `_loot_<tier>` suffix whether or not anything points at it yet. That
    # is strictly stronger, and it is the shape that catches the next b42 - a table can
    # be orphaned (H2) AND wrong-tier, and H2 alone would let the tier leak land the
    # moment someone re-wires it. Measured on the shipped arz: exactly 2 findings, both
    # the Obsidian leak; every other family and all three gift tables are already clean,
    # so this gate reds on the defect and on nothing else.
    for key in sorted(table_map):
        real, _f, tier = table_map[key]
        for p in _tier_check(db, lk, real, TIER_LETTER[tier], ''):
            out.append("H8 %s - a hoard's guaranteed row must match its OWN difficulty "
                       "(Will 2026-08-08 leak #2, which the Obsidian roulette re-opened)"
                       % p)
    for path in GIFT_TABLES:
        real = lk.real(path)
        if not real:
            continue
        tier = SLB._n(path).rsplit('_', 1)[-1].split('.')[0]
        for p in _tier_check(db, lk, real, TIER_LETTER.get(tier, 'n'), ''):
            out.append("H8 %s - the Secret Present box is per-difficulty too" % p)

    # ── H3 THE CROWN, MEASURED (not compared as bare multipliers) ────────────
    # The Devourer's stash stays the richest surface in the mod (R-247.7a is its volume
    # authority, so this is one-way: R-251 may not lift anything past it). Comparing
    # multipliers alone was wrong AND partial - the gift box rides a DIFFERENT bracket
    # ((1+1.8n) vs (3+1.8n)), so 5.4 > 3.8 as a number while the box is still well under
    # the stash in items, and the box was outside the check entirely. Compare the thing
    # that matters instead: solo spawn iterations. Measured: hoard 12.48, gift 16.38,
    # stash 18.96.
    # Read the stash's OWN equations rather than re-deriving them: R-247.7(a) owns that
    # record, and a constant copied here would silently stop tracking it.
    stash_real = lk.real(STASH_TABLES[0])
    stash_s = ((_solo(str(_gv(lk, stash_real, 'numSpawnMinEquation') or ''))
                + _solo(str(_gv(lk, stash_real, 'numSpawnMaxEquation') or ''))) / 2.0
               if stash_real else 0.0)
    for label, mn_eq, mx_eq in (
            ('the R-251 hoard volume', HOARD_MIN_EQ, HOARD_MAX_EQ),
            ('the Secret Present box', GIFT_MIN_EQ, GIFT_MAX_EQ)):
        s = (_solo(mn_eq) + _solo(mx_eq)) / 2.0
        rep['crown_%s' % ('hoard' if 'hoard' in label else 'gift')] = s
        if stash_s and s >= stash_s:
            out.append("H3 %s pays %.2f iteration(s) solo, meeting or exceeding the "
                       "Devourer's stash at %.2f - the blood-cave mega chest must stay "
                       "the richest surface in the mod (R-247.7a)" % (label, s, stash_s))
    rep['crown_stash'] = stash_s
    return out


def calibrate(db, lk=None):
    """Print the family, one row per chest, so every number above can be read as data."""
    lk = lk or SLB.Lookup(db)
    chest_map, table_map = chests(db, lk), tables(db, lk)
    refs = referrers(db, [t for (t, _f, _tr) in table_map.values()]) if table_map else {}
    print("\n=== R-251 uber/boss hoard family: %d chest(s), %d table(s) ==="
          % (len(chest_map), len(table_map)))
    print("%-34s %-8s %-34s %-30s %8s" % ('CHEST', 'TIER', 'NAMES', 'OWN TABLE', 'S solo'))
    for key in sorted(chest_map):
        real, fam, tier = chest_map[key]
        got = SLB._n(_gv(lk, real, 'tables') or '(none)')
        own = SLB._n(table_for(real))
        t = lk.real(got)
        s = 0.0
        if t:
            s = (_solo(str(_gv(lk, t, 'numSpawnMinEquation') or ''))
                 + _solo(str(_gv(lk, t, 'numSpawnMaxEquation') or ''))) / 2.0
        print("%-34s %-8s %-34s %-30s %8.2f"
              % (key.rsplit('\\', 1)[-1], TIER_LETTER.get(tier, '?'),
                 got.rsplit('\\', 1)[-1], own.rsplit('\\', 1)[-1]
                 + ('' if SLB._n(got) == own else '  <-- NOT WIRED'), s))
    orphans = sorted(k for k, v in refs.items() if not v)
    print("\norphan hoard tables (referenced by nothing): %d%s"
          % (len(orphans), ('  ' + ', '.join(o.rsplit('\\', 1)[-1] for o in orphans))
             if orphans else ''))
    print("\n=== the Secret Present gift box (BL-W0814-7) ===")
    for path in GIFT_TABLES:
        real = lk.real(path)
        if not real:
            print("   %-30s MISSING" % SLB._n(path).rsplit('\\', 1)[-1])
            continue
        mn = str(_gv(lk, real, 'numSpawnMinEquation') or '')
        mx = str(_gv(lk, real, 'numSpawnMaxEquation') or '')
        print("   %-30s %-36s %-36s S=%.2f"
              % (SLB._n(path).rsplit('\\', 1)[-1], mn, mx,
                 (_solo(mn) + _solo(mx)) / 2.0))
    print("\n=== the crown (R-247.7a, untouched here) ===")
    for path in STASH_TABLES:
        real = lk.real(path)
        if real:
            mn = str(_gv(lk, real, 'numSpawnMinEquation') or '')
            mx = str(_gv(lk, real, 'numSpawnMaxEquation') or '')
            print("   %-30s %-36s %-36s S=%.2f"
                  % (SLB._n(path).rsplit('\\', 1)[-1], mn, mx,
                     (_solo(mn) + _solo(mx)) / 2.0))


def pass_line(report):
    return ("R-251 PASS: %d uber/boss hoard chest(s) each name their OWN loot table, "
            "%d hoard table(s) are reachable and pinned at %s / %s with the guaranteed "
            "100%% row intact (worst %.2f iteration(s) on %s), no two chests share a "
            "record and none shares the Devourer's stash, and the Secret Present box "
            "pays exactly 3x its SV original."
            % (report.get('chests', 0), report.get('tables', 0),
               HOARD_MIN_EQ, HOARD_MAX_EQ,
               report.get('worst_hoard_spawn', (0.0, '-'))[0],
               report.get('worst_hoard_spawn', (0.0, '-'))[1]))
