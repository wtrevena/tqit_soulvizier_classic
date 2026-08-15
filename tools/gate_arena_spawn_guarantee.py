#!/usr/bin/env python3
r"""R-253 GATE (BL-W0814-12): a REPEATABLE-DESTINATION encounter may never depend on
one-shot quest state, a player-level window, or a sub-100 spawn chance.

THE DEFECT CLASS
----------------
Will 2026-08-14, verbatim: "when i went to the boss arena this time there was no boss
there. does he not spawn 100% of the time? the boss arena needs more work."

The Boss Arena is a DESTINATION: a place the player travels to, expecting the fight to
be there. SV built its encounter out of a TWO-step quest -
    STEP-2  Condition_EnterVolume(volume_startolympianarena, isResettable=0)
         -> Action_SpawnEntityAtLocation(boss_satyrshaman proxy, location_bossarenacenter)
- and a TQ quest step completes exactly ONCE per character, persisted in the .que save.
So after the first clear the arena is empty forever. Two further gates could each empty
it on their own: the proxy's difficultyLimitsFile was the base quest-proxy window
(min/max PLAYER level 29-36 / 41-55 / 60-75), and the proxy carried quest=1 with NO
chanceToRun at all, unlike every shipped placed uber (q_tantalus_lone: quest=0,
chanceToRun=100).

Three independent single-points-of-no-spawn, none of which any existing gate could see,
because every existing spawn gate reasons about the DB pool alone. This gate reasons
about the whole chain - MAP placement, QUEST neutralization, DB eligibility - and it is
the invariant gate that ships with the "repeatable destination encounter" content class
(process law 4).

THE INVARIANT (per registered destination encounter)
---------------------------------------------------
  C1 PLACED  : the encounter's spawner proxy is placed EXACTLY ONCE, statically, in its
               host level (build_section_surgery.INJECT_SPECS), as a plain 0x05 instance
               (no 0x14 binding) - flags=0, so the engine re-spawns it on every stream.
               EVERY option that can bind or track an instance is refused, `wants_0x14`
               included (it was missed in round 1: three of the four options were banned
               and the fourth produced the same bound shape).
  C2 NO ONE-SHOT SOURCE: the ported .qst carries ZERO Action_SpawnEntityAtLocation for
               that (entity, location). The upstream quest must still HAVE one (else the
               registry is stale and the check is vacuous), the neutralizer must remove
               it, the result must round-trip, and NOTHING else may change (every other
               action in the file is preserved byte-for-byte).
  C3 WIRED   : the neutralizer is actually called by the quest-port dispatcher - a
               defined-but-uncalled fix is the build22 "inert fix" lesson.
  C4 UNCONDITIONAL: the DB module's declared SPAWN_GUARANTEE has no suppressor -
               quest flag 0, chanceToRun 100, a player-level window that spans [1..110]
               on ALL difficulties, an EMPTY pool equation, and >= 1 guaranteed main.
  C5 (--arz)   the built arz matches that declaration exactly, and the main monster's
               charLevel is inside the window on all three difficulties.
  C6 (--quests) the BUILT Quests.arc really has zero such spawn actions.
  C7 (--map)    the BUILT map really places the proxy exactly once in the host level.
  C8 REWARD  : the destination PAYS, and keeps paying. A place the player travels to
               must guard something, and the hoard built for it must still be the hoard
               it opens: statically, the chest is not enrolled in a pass that repoints
               it at a base-game boss_default_* bracket (the single shared cause behind
               Will's five 2026-08-14 chest reports, which also left 18 of 27
               svc_*hoard_loot_0N records unreferenced in the shipped arz); with --arz,
               each tier's chest names its OWN loot record and that record still carries
               its guaranteed high-value slot.
  C9 (--arz) VOLUME TRUTH: the hoard ships at the SAME volume as an already-shipped PEER
               family, tier for tier - because the value the hoard BUILDER writes is not
               the value that ships (R-240's trim rewrites it), so any number published
               about this chest has to be checked against the arz, not against the mint
               site. `volume_exempt: True` inverts the check rather than silencing it.

C1-C4 + C8's static half are STATIC (source + the pristine upstream .qst): they run in
any worktree with no build. C5-C9 are the same invariant re-proved on real artifacts at
ship time.

USAGE
  py tools/gate_arena_spawn_guarantee.py
  py tools/gate_arena_spawn_guarantee.py --arz work/SoulvizierClassic/Database/SoulvizierClassic.arz
  py tools/gate_arena_spawn_guarantee.py --quests work/SoulvizierClassic/Resources/Quests.arc
  py tools/gate_arena_spawn_guarantee.py --map local/Levels_merged.arc
  py tools/gate_arena_spawn_guarantee.py --negtest
"""
import sys
import copy
import struct
import argparse
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / 'contracts'))

import qst_format                                                   # noqa: E402
from arc_patcher import ArcArchive                                  # noqa: E402

BS = chr(92)


# ── the registry of REPEATABLE-DESTINATION encounters ────────────────────────────────
# Every entry is an encounter the player TRAVELS TO and expects to find. Adding a new
# destination encounter means adding a row here; the gate then holds it to the whole
# invariant. `neutralizer` names the build_quest_files function that removes the quest's
# one-shot spawn; `pre` names transforms that must run before it (the port's own order).
DESTINATIONS = [
    {
        'label': 'Boss Arena / Olympian Arena (Aithon, the Ember-Crowned)',
        'level_key': 'levels/world/bossarena/boss_arena.lvl',
        'proxy_dbr': r'records\proxies custom\bossarena\boss_satyrshaman.dbr',
        'quest': 'bossarena.qst',
        'spawn_entity': r'records\proxies custom\bossarena\boss_satyrshaman.dbr',
        'spawn_location': r'records\quests\location_bossarenacenter.dbr',
        'pre': ['_fix_bossarena_entervolume'],
        'neutralizer': '_neutralize_bossarena_spawn',
        'db_module': 'bossarena',          # tools/patches/<name>.py, must expose SPAWN_GUARANTEE
    },
]

MIN_WINDOW = (1, 110)   # the always-on player-level window a destination spawn must span


# ── helpers ──────────────────────────────────────────────────────────────────────────
def _norm(p):
    if isinstance(p, bytes):
        p = p.decode('latin1')
    return p.replace('/', BS).lower()


def _count_spawn_actions(data, entity, location):
    """Number of Action_SpawnEntityAtLocation blocks spawning `entity` at `location`."""
    ent = _norm(entity).replace(BS, '/')
    loc = _norm(location).replace(BS, '/')

    def strs(items, out):
        for it in items:
            if it[0] == 'block':
                strs(it[1], out)
            elif it[0] == 'field' and it[2][0] == 'str':
                out.add(it[2][1].replace(BS, '/').lower())
        return out

    def walk(items, n):
        for i, it in enumerate(items):
            if it[0] == 'block':
                n = walk(it[1], n)
            elif (it[0] == 'field' and it[1] == 'actionClassName'
                    and it[2][0] == 'str'
                    and it[2][1] == 'Action_SpawnEntityAtLocation'
                    and i + 1 < len(items) and items[i + 1][0] == 'block'):
                f = strs(items[i + 1][1], set())
                if ent in f and loc in f:
                    n += 1
        return n

    total = 0
    for blk in qst_format.parse(data):
        total = walk(blk, total)
    return total


def _action_class_census(data):
    """{actionClassName: count} over the whole quest - the 'nothing else changed' oracle."""
    census = {}

    def walk(items):
        for it in items:
            if it[0] == 'block':
                walk(it[1])
            elif it[0] == 'field' and it[1] == 'actionClassName' and it[2][0] == 'str':
                census[it[2][1]] = census.get(it[2][1], 0) + 1
    for blk in qst_format.parse(data):
        walk(blk)
    return census


def _upstream_quests_arc(bqf):
    """The pristine SV Quests.arc, resolved for a worktree too (upstream/ is gitignored,
    so a worktree checkout is EMPTY - fall back to the MAIN checkout's cache)."""
    cands = [Path(bqf.UPSTREAM_SV_QUESTS)]
    rel = Path(bqf.UPSTREAM_SV_QUESTS)
    root = TOOLS.parent
    cands.append(root / rel)
    gitfile = root / '.git'
    if gitfile.is_file():
        try:
            txt = gitfile.read_text(encoding='utf-8', errors='replace').strip()
            if txt.startswith('gitdir:'):
                gd = Path(txt.split(':', 1)[1].strip())
                # <main>/.git/worktrees/<name> -> <main>
                main = gd.parent.parent.parent
                cands.append(main / rel)
        except OSError:
            pass
    for c in cands:
        if c.exists():
            return ArcArchive.from_file(c), c
    raise SystemExit(
        'GATE arena-spawn: upstream SV Quests.arc not found (looked in: %s). It is the '
        'pristine source of the quest under test; set SVC_SV098I_QUESTS_ARC or populate '
        'upstream/.' % ', '.join(str(c) for c in cands))


def _upstream_quest_bytes(arc, basename):
    bl = basename.lower()
    for e in arc.entries:
        if e.entry_type == 3 and (e.name.lower() == bl
                                  or e.name.lower().endswith('/' + bl)
                                  or e.name.lower().endswith(BS + bl)):
            return arc.decompress(e)
    raise SystemExit(f'GATE arena-spawn: {basename} not in the upstream Quests.arc')


# ── the checks ───────────────────────────────────────────────────────────────────────
def check_placed(d, inject_specs, problems):
    """C1: placed exactly once, statically, plain 0x05 (no 0x14)."""
    specs = None
    for k, v in inject_specs.items():
        if _norm(k) == _norm(d['level_key']):
            specs = v
            break
    if specs is None:
        problems.append(f"{d['label']}: host level {d['level_key']} has NO INJECT_SPECS "
                        f"entry - the spawner is not placed anywhere, so the encounter "
                        f"can only ever come from one-shot quest state.")
        return
    want = _norm(d['proxy_dbr'])
    hits = [s for s in specs if _norm(s[0]) == want]
    if len(hits) != 1:
        problems.append(f"{d['label']}: spawner {d['proxy_dbr']} is placed {len(hits)} "
                        f"time(s) in {d['level_key']}; the invariant is EXACTLY 1 "
                        f"(0 = no boss on any visit, >1 = duplicate encounters).")
        return
    spec = hits[0]
    if len(spec) < 4:
        problems.append(f"{d['label']}: placement spec is malformed ({spec!r})")
        return
    opts = spec[4] if len(spec) > 4 else {}
    if not isinstance(opts, dict):
        problems.append(f"{d['label']}: placement options must be a dict, got {opts!r}")
        return
    # Every option in build_section_surgery._normalize_spec that can produce a TRACKED or
    # BOUND instance. 'wants_0x14' was missing in round 1 (vet finding): it is the third
    # way to get a 0x14 binding onto an instance, so a destination registered with
    # {'wants_0x14': True} would have passed C1 while violating the invariant C1 encodes.
    for banned in ('x14_payload', 'x14', 'wants_0x14', 'flags', 'uniqueid'):
        if banned in opts:
            problems.append(
                f"{d['label']}: placement carries '{banned}' - a destination spawner must "
                f"be a plain flags=0 0x05 instance with no 0x14 binding (a tracked/bound "
                f"instance is not re-spawned on revisit, which is the bug this gate "
                f"exists for).")


def check_quest_neutralized(d, bqf, upstream_arc, problems):
    """C2: the ported quest has no one-shot spawn, and nothing else changed."""
    raw = _upstream_quest_bytes(upstream_arc, d['quest'])
    before = _count_spawn_actions(raw, d['spawn_entity'], d['spawn_location'])
    if before < 1:
        problems.append(
            f"{d['label']}: the UPSTREAM {d['quest']} has no Action_SpawnEntityAtLocation "
            f"for {d['spawn_entity']} - the registry row is stale and this check would "
            f"pass vacuously. Re-derive it before shipping.")
        return
    data = raw
    for fn in d.get('pre', []):
        data = getattr(bqf, fn)(data)
    out = getattr(bqf, d['neutralizer'])(data)
    after = _count_spawn_actions(out, d['spawn_entity'], d['spawn_location'])
    if after != 0:
        problems.append(f"{d['label']}: after {d['neutralizer']} the quest still has "
                        f"{after} one-shot spawn action(s) for {d['spawn_entity']}.")
    if qst_format.serialize(qst_format.parse(out)) != out:
        problems.append(f"{d['label']}: the neutralized {d['quest']} does not round-trip "
                        f"stably - refusing to ship a mangled quest.")
    # nothing else changed: every OTHER action class keeps its exact count
    cb, ca = _action_class_census(data), _action_class_census(out)
    for k in set(cb) | set(ca):
        exp = cb.get(k, 0) - (before if k == 'Action_SpawnEntityAtLocation' else 0)
        if ca.get(k, 0) != exp:
            problems.append(
                f"{d['label']}: {d['neutralizer']} changed {k} count "
                f"{cb.get(k, 0)} -> {ca.get(k, 0)} (expected {exp}); it must remove ONLY "
                f"the one-shot spawn action.")


def check_wired(d, bqf_source, problems):
    """C3: the neutralizer is CALLED by the port (build22 'inert fix' lesson)."""
    body = bqf_source.split('def ' + d['neutralizer'], 1)
    if len(body) < 2:
        problems.append(f"{d['label']}: {d['neutralizer']} is not defined in "
                        f"build_quest_files.")
        return
    calls = bqf_source.count(d['neutralizer'] + '(')
    if calls < 1:
        problems.append(
            f"{d['label']}: {d['neutralizer']} is DEFINED but never CALLED - the quest "
            f"would still ship its one-shot spawn (the build22 inert-fix lesson).")


def check_declaration(d, decl, problems):
    """C4: the DB module's declared spawn guarantee has no suppressor."""
    lo, hi = decl.get('limit_window', (None, None))
    if decl.get('quest_flag', 1) != 0:
        problems.append(f"{d['label']}: declared quest_flag={decl.get('quest_flag')!r}; a "
                        f"world-placed destination spawner must declare 0.")
    if float(decl.get('chance_to_run', 0)) != 100.0:
        problems.append(f"{d['label']}: declared chanceToRun="
                        f"{decl.get('chance_to_run')!r}; must be 100.0 "
                        f"('does he not spawn 100% of the time?').")
    if lo is None or lo > MIN_WINDOW[0] or hi < MIN_WINDOW[1]:
        problems.append(
            f"{d['label']}: declared player-level window {(lo, hi)} does not span "
            f"{MIN_WINDOW} - a level window is exactly how the arena went empty "
            f"(the base quest window was 29-36 Normal).")
    if decl.get('pool_equation', None) != '':
        problems.append(f"{d['label']}: declared pool_equation="
                        f"{decl.get('pool_equation')!r}; must be empty so the literal "
                        f"spawn counts are the runtime counts.")
    if int(decl.get('min_guaranteed_mains', 0)) < 1:
        problems.append(f"{d['label']}: declared min_guaranteed_mains="
                        f"{decl.get('min_guaranteed_mains')!r}; must be >= 1.")


def _hoard_records(prefix):
    base = r'records\drxitem\container'
    return {t: (rf'{base}\svc_{prefix}hoard_{t}.dbr',
                rf'{base}\svc_{prefix}hoard_loot_{t}.dbr') for t in ('01', '02', '03')}


def check_reward_static(d, decl, problems):
    """C8 (static half): the encounter's chest must not be enrolled in a pass that
    REPOINTS it away from the table it just built.

    `_svc_standardize_boss_chests` walks `_SVC_CHEST_STD` and rewrites each listed
    chest's `tables` to the base game's `boss_default_<bracket>`. MEASURED on the
    SHIPPED arz (build92), per chest, at 1 player, tier 01 - i.e. POST-R-240-trim,
    which is what actually ships:

        bespoke svc_<fam>hoard_loot_01 : (3+1.8P)*0.2188/*0.25 -> 1.05/1.20 spawn
            iterations; chances 40/40/100/21.2/40/40 -> group mass 2.812;
            loot3Chance=100 (svc_unique_weapons_n01 + 01_act4_relics EVERY iteration).
        boss_default_55-57 / 63-65     : (3+1.6P)*1.5/*1.7 -> 6.90/7.82 iterations;
            chances 14/27/10/21.2/25/14 -> group mass 1.112; loot3Chance=10
            (01_l_boss_misc).

    So the repoint is NOT a volume nerf in the naive direction: boss_default runs ~6.5x
    MORE iterations and pays MORE items (expected group hits 7.67-8.70 against
    2.95-3.37). What the repoint destroys is the GUARANTEED unique+relic slot (expected
    1.05-1.20 rolls collapse to 0.69-0.78, and the guarantee itself disappears), and it
    leaves the bespoke table unreferenced. That is the single shared cause behind five
    separate 2026-08-14 reports from Will (BL-W0814-2/5/7/11/13), so a chest shipped for
    a destination encounter may not opt into it.

    ROUND-1 CORRECTION (vet): this docstring previously quoted (3+1.8P)*2.4/*2.8 as the
    bespoke MEASURED volume. That is the value `_svc_build_dedicated_hoard` WRITES;
    R-240's trim (tools/svc_loot_volume.py) rewrites it before the arz ships, and the
    arena family is inside that trim's scope like its 27 siblings. C9 below now asserts
    the SHIPPED number against a peer family rather than trusting any prose.

    SELF-RETIRING, on a property the PASS OWNS: the check fires only while the pass
    still REPOINTS, which the monolith declares as `_SVC_CHEST_STD_REPOINTS` beside
    `_svc_standardize_boss_chests`. When the chest-generosity lane converts it into a
    wiring pass (each chest -> its own svc_<family>hoard_loot_<tier>) it flips that flag
    to False, `_SVC_CHEST_STD` becomes a harmless family roster, and this check goes
    quiet instead of blocking that lane.

    ROUND-3 CORRECTION (vet): this used to retire on the function NAME being absent.
    That only covers deletion/rename - if the generosity lane converted the pass IN
    PLACE (same name, wiring semantics) and the integrator followed this branch's own
    instruction to re-add the roster row, C8 would have redded on a CORRECT
    configuration. The flag is now the condition; a missing flag on an existing pass is
    read as still-repointing, so an older monolith fails loud rather than silently
    opening the hole."""
    prefix = decl.get('hoard_prefix')
    key = decl.get('chest_std_key')
    if not prefix or not key:
        problems.append(f"{d['label']}: SPAWN_GUARANTEE declares no reward "
                        f"(hoard_prefix/chest_std_key) - a destination encounter must "
                        f"declare the hoard it pays out, or C8 is vacuous.")
        return
    try:
        import apply_svc_patches as MONO
    except Exception as e:                                       # noqa: BLE001
        problems.append(f"{d['label']}: cannot import apply_svc_patches for C8 ({e})")
        return
    repointer = getattr(MONO, '_svc_standardize_boss_chests', None)
    roster = getattr(MONO, '_SVC_CHEST_STD', {})
    # The PASS owns the retirement condition, not this gate and not the function name.
    # No pass at all -> nothing repoints. Pass present but no flag -> a pre-R-253
    # monolith, which does repoint (conservative: fail loud, never silently open).
    repoints = (repointer is not None
                and bool(getattr(MONO, '_SVC_CHEST_STD_REPOINTS', True)))
    if repoints and key in roster:
        problems.append(
            f"{d['label']}: '{key}' is registered in _SVC_CHEST_STD while "
            f"_svc_standardize_boss_chests still REPOINTS registered chests at "
            f"records{BS}item{BS}containers{BS}defaultloot{BS}boss_default_*. That "
            f"strands the dedicated hoard this wave builds and ships the exact chest "
            f"Will rejected five times on 2026-08-14. Remove the row (the chest then "
            f"keeps its own table), or land this after the pass stops repointing - and "
            f"when it does stop, set _SVC_CHEST_STD_REPOINTS = False in the same commit, "
            f"which is what retires this check.")


def check_reward_arz(d, decl, db, problems):
    """C8 (arz half): each tier's chest really opens its OWN loot record, and that
    record still carries the guaranteed high-value slot. Works in BOTH worlds - it
    asserts the end state, not the mechanism that produced it."""
    prefix = decl.get('hoard_prefix')
    if not prefix:
        return
    want_chance = float(decl.get('guaranteed_loot_chance', 100.0))
    for t, (chest, loot) in sorted(_hoard_records(prefix).items()):
        if not db.has_record(chest):
            problems.append(f"{d['label']}: arz is missing the reward chest {chest} - "
                            f"the arena would ship reward-less again.")
            continue
        tables = db.get_field_value(chest, 'tables')
        tables = tables[0] if isinstance(tables, list) else tables
        if _norm(tables or '') != _norm(loot):
            problems.append(
                f"{d['label']}: {chest}.tables = {tables!r}, expected its own "
                f"{loot}. A dedicated hoard that points at someone else's table (a "
                f"boss_default_* bracket or a shared family) is the BL-W0814-2/5/7/11/13 "
                f"defect, and it strands {loot}.")
            continue
        got = db.get_field_value(loot, 'loot3Chance')
        got = got[0] if isinstance(got, list) else got
        if got is None or float(got) < want_chance:
            problems.append(
                f"{d['label']}: {loot}.loot3Chance = {got!r} (want >= {want_chance}) - "
                f"the guaranteed unique + relic slot is what makes the hoard a hoard.")


_VOLUME_FIELDS = ('numSpawnMinEquation', 'numSpawnMaxEquation')


def check_volume_truth(d, decl, db, problems):
    r"""C9 (arz half) - THE NUMBER IN THE RULING MUST BE THE NUMBER THAT SHIPS.

    THE DEFECT CLASS (found by the R-253 round-1 vet, and worth its own check):
    `_svc_build_dedicated_hoard` mints the family's loot tables with
    `(3+(1.8*numberOfPlayers))*2.4/*2.8`, and R-240's later trim
    (`tools/svc_loot_volume.py`) REWRITES those equations before the arz is written.
    The arena family is inside that trim's scope by the ordinary mod-ownership rule
    (`svc_` prefix / `\svc\` folder), exactly like its 27 already-shipped siblings - the
    scope is derived, never a typed roster (BL-R181-DEBT-7's lesson). So a reader who
    measures at the MINT site, or who runs the hoard builder alone as a dry-run, reads a
    number the shipped arz does not contain. Round 1 of this lane did exactly that and
    published `*2.4/*2.8` as MEASURED in seven places, including the ruling and Will's
    test guide, with the bespoke-vs-boss_default comparison inverted on that axis.

    Neither C8 half could see it: C8 asserts tables-identity and `loot3Chance`, both of
    which the trim leaves alone. Hence C9, asserting the property that actually carries
    the meaning: the destination's hoard ships at the SAME volume as an already-shipped
    PEER family (`volume_peer`), tier for tier. Any divergence - the trim skipping this
    family, a future generosity pass touching one family and not the other, or a
    deliberate carve-out - reds here and forces the ruling to say so out loud.

    `volume_exempt: True` is the declared escape hatch. It is not a way to silence C9:
    it INVERTS it (the arena must then differ from its peer), so an exemption that was
    ruled but never actually landed still fails."""
    prefix = decl.get('hoard_prefix')
    peer = decl.get('volume_peer')
    if not prefix:
        return
    if not peer:
        problems.append(
            f"{d['label']}: SPAWN_GUARANTEE declares a hoard but no 'volume_peer'. C9 "
            f"cannot check that the shipped volume is the volume the ruling states, and "
            f"the mint-site value is NOT the shipped value (R-240 trims it).")
        return
    exempt = bool(decl.get('volume_exempt', False))
    mine, theirs = _hoard_records(prefix), _hoard_records(peer)
    for t in sorted(mine):
        loot, peer_loot = mine[t][1], theirs[t][1]
        if not db.has_record(peer_loot):
            problems.append(
                f"{d['label']}: declared volume_peer {peer!r} has no {peer_loot} in the "
                f"arz, so C9 would pass vacuously. Name a family that really ships.")
            continue
        if not db.has_record(loot):
            continue                      # C8 already reports the missing family
        for f in _VOLUME_FIELDS:
            a = db.get_field_value(loot, f)
            b = db.get_field_value(peer_loot, f)
            a = a[0] if isinstance(a, list) else a
            b = b[0] if isinstance(b, list) else b
            same = str(a) == str(b)
            if same and exempt:
                problems.append(
                    f"{d['label']}: volume_exempt=True but {loot}.{f} = {a!r} is "
                    f"IDENTICAL to peer {peer_loot} - the ruled carve-out never landed, "
                    f"so the ruling promises a volume the arz does not carry.")
            elif not same and not exempt:
                problems.append(
                    f"{d['label']}: {loot}.{f} = {a!r} but peer {peer_loot}.{f} = {b!r}. "
                    f"This hoard is supposed to ship at the SAME volume as its siblings "
                    f"(R-240 governs both). A silent divergence means every number "
                    f"published for this chest - ruling, test guide, code comments - is "
                    f"now wrong. Fix the pass, or declare volume_exempt=True in a ruling.")


def check_arz(d, decl, db, problems):
    """C5: a BUILT arz matches the declaration."""
    proxy, pool, main, limit = (decl['proxy'], decl['pool'],
                                decl['main_monster'], decl['limit'])
    for rec in (proxy, pool, main, limit):
        if not db.has_record(rec):
            problems.append(f"{d['label']}: arz is missing {rec}")
            return

    def g(rec, f, default=None):
        v = db.get_field_value(rec, f)
        if v is None:
            return default
        return v[0] if isinstance(v, list) else v

    if g(proxy, 'quest', 1) != 0:
        problems.append(f"{d['label']}: arz proxy quest={g(proxy, 'quest')} (want 0)")
    if float(g(proxy, 'chanceToRun', 0) or 0) != 100.0:
        problems.append(f"{d['label']}: arz proxy chanceToRun="
                        f"{g(proxy, 'chanceToRun')} (want 100.0)")
    if _norm(g(proxy, 'difficultyLimitsFile', '')) != _norm(limit):
        problems.append(f"{d['label']}: arz proxy difficultyLimitsFile="
                        f"{g(proxy, 'difficultyLimitsFile')} (want {limit})")
    for diff in ('Normal', 'Epic', 'Legendary'):
        for kind, want, cmp_ in (('min', MIN_WINDOW[0], 'le'), ('max', MIN_WINDOW[1], 'ge')):
            f = f'{kind}PlayerLevelEquation{diff}'
            raw = g(limit, f, None)
            if raw is None:
                problems.append(f"{d['label']}: {limit} has no {f}")
                continue
            try:
                val = float(str(raw).split('*')[0])
            except ValueError:
                problems.append(f"{d['label']}: {limit}.{f}={raw!r} is not a plain "
                                f"'<n>*1' window equation")
                continue
            bad = (val > want) if cmp_ == 'le' else (val < want)
            if bad:
                problems.append(f"{d['label']}: {limit}.{f}={val} suppresses the spawn "
                                f"outside the required {MIN_WINDOW} window")
    sm, cc, cm = (g(pool, 'spawnMax', 0), g(pool, 'championChance', 0.0),
                  g(pool, 'championMax', 0))
    mains = sm if (cc or 0) <= 0 else (sm - cm)
    if mains < int(decl['min_guaranteed_mains']):
        problems.append(f"{d['label']}: arz pool guarantees {mains} main(s) "
                        f"(spawnMax={sm}, championChance={cc}, championMax={cm})")
    if (g(pool, 'proxyPoolEquation', '') or '') != '':
        problems.append(f"{d['label']}: arz pool still carries proxyPoolEquation="
                        f"{g(pool, 'proxyPoolEquation')}")
    cl = db.get_field_value(main, 'charLevel')
    cl = cl if isinstance(cl, list) else [cl]
    for lvl in [x for x in cl if x is not None]:
        if float(lvl) > MIN_WINDOW[1]:
            problems.append(f"{d['label']}: main charLevel {lvl} exceeds the window max "
                            f"{MIN_WINDOW[1]} and would be scaled down")


def check_built_quest(d, arc, problems):
    """C6: the BUILT Quests.arc carries no one-shot spawn for this encounter."""
    for e in arc.entries:
        if e.entry_type == 3 and e.name.lower().endswith(d['quest'].lower()):
            n = _count_spawn_actions(arc.decompress(e), d['spawn_entity'],
                                     d['spawn_location'])
            if n:
                problems.append(f"{d['label']}: the BUILT {e.name} still has {n} one-shot "
                                f"spawn action(s) - static + quest = duplicate encounters.")
            return
    problems.append(f"{d['label']}: {d['quest']} is absent from the built Quests.arc")


def check_built_map(d, map_path, problems):
    """C7: the BUILT map places the spawner exactly once in the host level, flags=0."""
    from merge_levels_binary import parse_sections
    from contracts_map import parse_level_index, parse_blob_sections, SEC_LEVELS
    arc = ArcArchive.from_file(Path(map_path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    secs = {s['type']: s for s in parse_sections(data)}
    ls = secs[SEC_LEVELS]
    levels = parse_level_index(data[ls['data_offset']:ls['data_offset'] + ls['size']])
    key = _norm(d['level_key']).replace(BS, '/')
    blob = None
    for lv in levels:
        if lv['fname'].replace(BS, '/').lower().endswith(key):
            blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
            break
    if blob is None:
        problems.append(f"{d['label']}: level {d['level_key']} not in the built map")
        return
    want = _norm(d['proxy_dbr'])
    base = 56 if blob[3] == 0x0e else 72
    for t, sec in parse_blob_sections(blob):
        if t != 0x05:
            continue
        pos = 0
        nstr = struct.unpack_from('<I', sec, pos)[0]; pos += 4
        strings = []
        for _ in range(nstr):
            ln = struct.unpack_from('<I', sec, pos)[0]; pos += 4
            strings.append(sec[pos:pos + ln].decode('latin1')); pos += ln
        ninst = struct.unpack_from('<I', sec, pos)[0]; pos += 4
        found = []
        for _ in range(ninst):
            sid = struct.unpack_from('<I', sec, pos)[0]
            flags = struct.unpack_from('<I', sec, pos + 52)[0]
            nm = strings[sid] if sid < len(strings) else '?'
            if _norm(nm) == want:
                found.append(flags)
            pos += base + (16 if flags != 0 else 0)
        if len(found) != 1:
            problems.append(f"{d['label']}: the BUILT map places the spawner "
                            f"{len(found)} time(s) in {d['level_key']} (want exactly 1)")
        elif found[0] != 0:
            problems.append(f"{d['label']}: the BUILT placement has flags={found[0]} - a "
                            f"tracked instance is not re-spawned on revisit")
        return
    problems.append(f"{d['label']}: {d['level_key']} has no 0x05 section")


# ── driver ───────────────────────────────────────────────────────────────────────────
def run(dests, arz=None, quests=None, map_path=None, verbose=True):
    import build_section_surgery as BSS
    import build_quest_files as BQF
    bqf_source = (TOOLS / 'build_quest_files.py').read_text(encoding='utf-8',
                                                            errors='replace')
    upstream_arc, upstream_path = _upstream_quests_arc(BQF)
    problems = []
    for d in dests:
        check_placed(d, BSS.INJECT_SPECS, problems)
        check_quest_neutralized(d, BQF, upstream_arc, problems)
        check_wired(d, bqf_source, problems)
        mod = __import__('patches.' + d['db_module'], fromlist=['SPAWN_GUARANTEE'])
        decl = getattr(mod, 'SPAWN_GUARANTEE', None)
        if not isinstance(decl, dict):
            problems.append(f"{d['label']}: tools/patches/{d['db_module']}.py exposes no "
                            f"SPAWN_GUARANTEE declaration")
        else:
            check_declaration(d, decl, problems)
            check_reward_static(d, decl, problems)
            if arz:
                from arz_patcher import ArzDatabase
                _db = ArzDatabase.from_arz(Path(arz))
                check_arz(d, decl, _db, problems)
                check_reward_arz(d, decl, _db, problems)
                check_volume_truth(d, decl, _db, problems)
        if quests:
            check_built_quest(d, ArcArchive.from_file(Path(quests)), problems)
        if map_path:
            check_built_map(d, map_path, problems)
    if verbose:
        print(f'GATE arena-spawn-guarantee: {len(dests)} destination encounter(s); '
              f'upstream quest source {upstream_path}')
        print(f'  modes: static=YES arz={bool(arz)} quests={bool(quests)} '
              f'map={bool(map_path)}')
    return problems


def negtest():
    """Planted negatives: each must be CAUGHT. A gate that cannot fail is not a gate."""
    import build_section_surgery as BSS
    import build_quest_files as BQF
    import patches.bossarena as MOD

    cases = []
    base = DESTINATIONS[0]

    # N1: the placement is missing entirely (the pre-R-253 state)
    saved = BSS.INJECT_SPECS[base['level_key']]
    BSS.INJECT_SPECS[base['level_key']] = [s for s in saved
                                           if _norm(s[0]) != _norm(base['proxy_dbr'])]
    cases.append(('N1 spawner not placed', run([base], verbose=False)))
    # N2: the placement is duplicated
    BSS.INJECT_SPECS[base['level_key']] = list(saved) + [
        (base['proxy_dbr'].encode('latin1'), 1.0, 2.0, 3.0)]
    cases.append(('N2 spawner placed twice', run([base], verbose=False)))
    # N13 (C1): the placement is registered with 'wants_0x14' - the FOURTH bind/track
    # option in build_section_surgery._normalize_spec, and the one round 1 forgot. It
    # appends 0x14 metadata for the instance, i.e. the tracked/bound shape C1's own
    # rationale says is not re-spawned on revisit, so C1 must refuse it like the others.
    BSS.INJECT_SPECS[base['level_key']] = [
        (s[0], s[1], s[2], s[3], dict(s[4] if len(s) > 4 else {}, wants_0x14=True))
        if _norm(s[0]) == _norm(base['proxy_dbr']) else s
        for s in saved]
    cases.append(('N13 placement bound via wants_0x14', run([base], verbose=False)))
    BSS.INJECT_SPECS[base['level_key']] = saved

    # N3: the quest neutralizer is a no-op (the one-shot spawn survives)
    real = getattr(BQF, base['neutralizer'])
    setattr(BQF, base['neutralizer'], lambda data: data)
    cases.append(('N3 quest keeps its one-shot spawn', run([base], verbose=False)))
    # N4: the neutralizer OVERREACHES - it also eats an unrelated action (here the
    # STEP-1 Action_ShowNpc that the doors/hub machinery reuses by record name).
    def _overreach(data):
        tree = qst_format.parse(real(data))

        def strip(items):
            out, i, done = [], 0, False
            while i < len(items):
                it = items[i]
                if it[0] == 'block':
                    sub, sdone = strip(it[1])
                    out.append(('block', sub))
                    done = done or sdone
                    i += 1
                    continue
                if (not done and it[0] == 'field' and it[1] == 'actionClassName'
                        and it[2][0] == 'str' and it[2][1] == 'Action_ShowNpc'
                        and i + 1 < len(items) and items[i + 1][0] == 'block'):
                    i += 2
                    done = True
                    continue
                out.append(it)
                i += 1
            return out, done
        newtree = []
        for blk in tree:
            sub, _ = strip(blk)
            newtree.append(sub)
        return qst_format.serialize(newtree)
    setattr(BQF, base['neutralizer'], _overreach)
    cases.append(('N4 neutralizer eats an unrelated action', run([base], verbose=False)))
    setattr(BQF, base['neutralizer'], real)

    # N5..N9: declaration suppressors
    real_decl = MOD.SPAWN_GUARANTEE
    for label, mut in (
            ('N5 player-level window reintroduced', {'limit_window': (29, 36)}),
            ('N6 sub-100 spawn chance', {'chance_to_run': 50.0}),
            ('N7 quest-only proxy', {'quest_flag': 1}),
            ('N8 champion crowd-out', {'min_guaranteed_mains': 0}),
            ('N9 spawn-count equation left on', {'pool_equation': 'poolValue*1'}),
            ('N10 reward not declared at all', {'hoard_prefix': None,
                                                'chest_std_key': None})):
        bad = copy.deepcopy(real_decl)
        bad.update(mut)
        MOD.SPAWN_GUARANTEE = bad
        cases.append((label, run([base], verbose=False)))
    MOD.SPAWN_GUARANTEE = real_decl

    # N11 (C8): the reward chest gets enrolled in the repointing roster - the wiring
    # that gutted five chests on 2026-08-14. Must be caught with NO build.
    import apply_svc_patches as MONO
    # INTEGRATION (build97): R-251 shipped as build95 and REPLACED
    # `_svc_standardize_boss_chests` with the wiring pass `tools/svc_uber_hoards.py`, so
    # the attribute the N11/N12/N17/N18 worlds are ABOUT no longer exists on main. C8
    # itself reads it with getattr(...) and correctly retires (that is negtest N12's whole
    # point), but the negatives must still be able to CONSTRUCT the repointing world or
    # they degrade to vacuous passes. Synthesize a stand-in for the duration, and remove
    # it again after N18 so nothing leaks into the live gate run below.
    _synth_repointer = not hasattr(MONO, '_svc_standardize_boss_chests')
    if _synth_repointer:
        MONO._svc_standardize_boss_chests = lambda *a, **k: None
    _key = real_decl['chest_std_key']
    _had = _key in MONO._SVC_CHEST_STD
    MONO._SVC_CHEST_STD[_key] = ('55-57', '63-65', '63-65')
    cases.append(('N11 reward chest repointed to a base boss_default_* table',
                  run([base], verbose=False)))
    if not _had:
        del MONO._SVC_CHEST_STD[_key]

    # N12 (C8): ... and the check must RETIRE ITSELF once nothing repoints, or it
    # blocks the chest-generosity lane forever. SHAPE A: the pass is deleted/renamed.
    _repointer = MONO._svc_standardize_boss_chests
    del MONO._svc_standardize_boss_chests
    MONO._SVC_CHEST_STD[_key] = ('55-57', '63-65', '63-65')
    _retired = run([base], verbose=False)
    MONO._svc_standardize_boss_chests = _repointer
    if not _had:
        del MONO._SVC_CHEST_STD[_key]
    print('  %s N12 C8 self-retires when no repointing pass exists (roster becomes safe)'
          % ('PASS   ' if not _retired else 'FAIL   '))
    for p in _retired:
        print(f'      - {p}')

    # N17 (C8, R-253 vet round 3): SHAPE B - the generosity lane converts the pass IN
    # PLACE (same function name, wiring semantics) and flips the flag the pass owns. The
    # roster row is then CORRECT and must NOT red. Retiring on the function NAME alone
    # would have failed exactly here, blocking the lane this branch tells the integrator
    # to hand the row back to.
    _flag = getattr(MONO, '_SVC_CHEST_STD_REPOINTS', True)
    MONO._SVC_CHEST_STD_REPOINTS = False
    MONO._SVC_CHEST_STD[_key] = ('55-57', '63-65', '63-65')
    _converted = run([base], verbose=False)
    MONO._SVC_CHEST_STD_REPOINTS = _flag
    if not _had:
        del MONO._SVC_CHEST_STD[_key]
    print('  %s N17 C8 self-retires when the pass is converted IN PLACE '
          '(_SVC_CHEST_STD_REPOINTS=False, function still present)'
          % ('PASS   ' if not _converted else 'FAIL   '))
    for p in _converted:
        print(f'      - {p}')

    # N18 (C8): and the flag must not be a blanket off-switch - a pass that still
    # repoints while the row is registered stays caught even if some other lane removed
    # the flag entirely (missing flag = still repointing).
    _flag2 = MONO._SVC_CHEST_STD_REPOINTS
    del MONO._SVC_CHEST_STD_REPOINTS
    MONO._SVC_CHEST_STD[_key] = ('55-57', '63-65', '63-65')
    cases.append(('N18 repointing pass with the declaration flag missing entirely',
                  run([base], verbose=False)))
    MONO._SVC_CHEST_STD_REPOINTS = _flag2
    if not _had:
        del MONO._SVC_CHEST_STD[_key]

    # N19 (C8, build97 integration): and the world main ACTUALLY ships - no repointing
    # pass at all, the roster row registered anyway - must stay quiet, because the chest
    # keeps its own table with or without the row. This is the live post-R-251 shape, and
    # it is the reason the roster row was deliberately not re-added at integration.
    _no_pass = []
    if _synth_repointer:
        del MONO._svc_standardize_boss_chests
        MONO._SVC_CHEST_STD[_key] = ('55-57', '63-65', '63-65')
        _no_pass = run([base], verbose=False)
        if not _had:
            del MONO._SVC_CHEST_STD[_key]
        print('  %s N19 C8 is quiet on the LIVE post-R-251 shape (no repointing pass, '
              'roster row present)' % ('PASS   ' if not _no_pass else 'FAIL   '))
        for p in _no_pass:
            print(f'      - {p}')

    # ── N14..N16 (C9 VOLUME TRUTH) ───────────────────────────────────────────────────
    # C9 needs an arz, but the invariant it encodes is exactly the one a dry-run cannot
    # be trusted for, so its negatives run against a MINIMAL fake db instead of gating on
    # a build. The fake carries only what C9 reads (has_record + numSpawn equations), and
    # the SHIPPED equations are the real ones re-measured from build92's arz.
    _SHIPPED = {'01': ('(3+(1.8*numberOfPlayers))*0.2188', '(3+(1.8*numberOfPlayers))*0.25'),
                '02': ('(3+(1.8*numberOfPlayers))*0.228', '(3+(1.8*numberOfPlayers))*0.266'),
                '03': ('(3+(1.8*numberOfPlayers))*0.252', '(3+(1.8*numberOfPlayers))*0.294')}
    _MINTED = ('(3+(1.8*numberOfPlayers))*2.4', '(3+(1.8*numberOfPlayers))*2.8')

    class _FakeDb(object):
        """Only what check_volume_truth reads."""

        def __init__(self, rows):
            self._rows = {_norm(k): v for k, v in rows.items()}

        def has_record(self, name):
            return _norm(name) in self._rows

        def get_field_value(self, name, field):
            return self._rows.get(_norm(name), {}).get(field)

    def _rows(prefix, per_tier):
        base = r'records\drxitem\container'
        out = {}
        for t, (mn, mx) in per_tier.items():
            out[rf'{base}\svc_{prefix}hoard_loot_{t}.dbr'] = {
                'numSpawnMinEquation': mn, 'numSpawnMaxEquation': mx}
            out[rf'{base}\svc_{prefix}hoard_{t}.dbr'] = {}
        return out

    def _c9(decl_mut, mine, peer_rows):
        probs = []
        decl = copy.deepcopy(real_decl)
        decl.update(decl_mut)
        db = _FakeDb(dict(mine, **peer_rows))
        check_volume_truth(base, decl, db, probs)
        return probs

    _peer = _rows(real_decl['volume_peer'], _SHIPPED)
    _pfx = real_decl['hoard_prefix']
    # N14: the R-240 trim skips the arena family, so it ships at the MINT value while
    # every sibling ships trimmed - the exact divergence that would make the ruling's
    # published numbers wrong again, in the other direction.
    cases.append(('N14 hoard volume diverges from its shipped peer (trim skipped it)',
                  _c9({}, _rows(_pfx, {t: _MINTED for t in _SHIPPED}), _peer)))
    # N15: a ruling grants an R-240 carve-out but the code never landed it, so the arz
    # still matches the peer. An exemption that exists only on paper must red.
    cases.append(('N15 volume_exempt ruled but never landed in the arz',
                  _c9({'volume_exempt': True}, _rows(_pfx, _SHIPPED), _peer)))
    # N16: volume_peer names a family that does not ship - C9 would pass vacuously.
    cases.append(('N16 volume_peer names a family absent from the arz',
                  _c9({'volume_peer': 'nosuchfamily'}, _rows(_pfx, _SHIPPED), _peer)))
    # P1: and the real, shipped shape (arena == peer, no exemption) must be CLEAN.
    _c9_clean = _c9({}, _rows(_pfx, _SHIPPED), _peer)
    print('  %s P1 C9 clean when the hoard ships at its peer volume'
          % ('PASS   ' if not _c9_clean else 'FAIL   '))
    for p in _c9_clean:
        print(f'      - {p}')

    ok = True
    for label, probs in cases:
        caught = bool(probs)
        print(f'  {"CAUGHT " if caught else "MISSED "} {label}'
              + ('' if caught else '   <-- THE GATE IS BLIND HERE'))
        ok = ok and caught
    # and the real configuration must be CLEAN
    live = run([base], verbose=False)
    print(f'  {"PASS   " if not live else "FAIL   "} P0 the shipped configuration is clean')
    for p in live:
        print(f'      - {p}')
    return (ok and not live and not _retired and not _converted and not _c9_clean
            and not _no_pass)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--arz', help='built .arz to verify the DB half against')
    ap.add_argument('--quests', help='built Quests.arc to verify the quest half against')
    ap.add_argument('--map', dest='map_path', help='built Levels.arc to verify placement')
    ap.add_argument('--negtest', action='store_true', help='run the planted negatives')
    a = ap.parse_args()
    if a.negtest:
        print('GATE arena-spawn-guarantee NEGTEST')
        sys.exit(0 if negtest() else 1)
    problems = run(DESTINATIONS, a.arz, a.quests, a.map_path)
    if problems:
        print(f'\nGATE arena-spawn-guarantee: FAIL ({len(problems)} problem(s))')
        for p in problems:
            print(f'  - {p}')
        sys.exit(1)
    print('GATE arena-spawn-guarantee: PASS - every destination encounter spawns '
          'unconditionally, from a static placement, with no one-shot quest source.')


if __name__ == '__main__':
    main()
