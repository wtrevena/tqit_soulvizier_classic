"""legion_soul_stages - one soul per death-transform encounter (b56).

WHY THIS EXISTS (RCA in docs/reports/b56_legion_soul_stages.md)
---------------------------------------------------------------
Will (2026-07-14): "the hero monster legion is dropping souls at multiple stages
of his life as he dies and gets bigger."

The hero **Legion** (records\\creature\\monster\\eurynomus\\um_legion_28*) is a
FOUR-stage death-transform chain wired by `actorToSpawnOnDeath`:

    um_legion_28  ->  um_legion_28a  ->  um_legion_28b  ->  um_legion_28c
      (Hero, lvl 14 each; um_legion_28c is TERMINAL: no onward transform)

Every one of the four stages is its own monster record and EACH carries the
identical soul drop (`chanceToEquipFinger2`=66, `lootFinger2Item1`=legion_soul).
So a single Legion encounter can yield up to FOUR copies of the same soul. Root
cause: the build's soul wiring (`build_svc_database.wire_souls_to_monsters`)
gates on rank Hero/Boss/Quest and treats every stage as an independent dropper;
it does not know the four records are one growing monster. (The three
non-terminal stages even point their _n tier at the broken Dropbox
"...conflicted copy 2013-08-07" legion_soul path; only the terminal um_legion_28c
uses the clean legion_soul_n.dbr.)

DESIGN INTENT (the established uber-boss law: Tantalus / Charon-Unferried /
Mnemophage / Golden Bough all put the soul on the FINAL form only, clearing the
inherited Finger2 soul on every non-terminal form): ONE soul per encounter,
dropped by the FINAL (terminal) stage.

WHAT THIS MODULE FIXES (and, deliberately, what it does NOT)
-----------------------------------------------------------
It fixes the exact defect Will reported and its class: a death-transform chain
where the SAME soul item is dropped by two or more stages that lie on one forward
path. For each such soul it keeps the drop on the DEEPEST (terminal-most) stage
and zeroes `chanceToEquipFinger2` on every shallower stage - following the
`_apply_aphiastas_finger2_zero` house pattern (chance -> 0, the lootFinger2Item1
refs left intact and inert). This is ORPHAN-PROOF by construction: a stage is
only zeroed when the SAME soul is still dropped by a deeper stage on its own
chain, so the soul stays obtainable (exactly ONE drop). For Legion: keep
um_legion_28c, zero um_legion_28 / _28a / _28b.

It DOES NOT touch death-transform chains whose stages drop DISTINCT souls (head
= an svc_uber soul, terminal = a different base-path soul: possessedboar,
base-game Charon x3, base-game Hades, lillued). Reducing those to one soul is a
design decision (which of two genuinely-different collectibles is canonical) and
zeroing a stage there would ORPHAN a distinct soul - the very inverse defect the
task guards against. Those chains are reported LOUD (never silent) for a design
ruling; see docs/reports/b56_legion_soul_stages.md "distinct-soul chains".

TIMING (why the fix survives the build)
---------------------------------------
Runs in run_registry (after all soul wiring: wire_souls_to_monsters +
create_uber_souls + apply_all_extended_patches all precede it) and BEFORE the
drop-rate forcer in run_registry_gates. The forcer only ever boosts records with
chanceToEquipFinger2 > 0 (testing 100%) or leaves rates untouched (release
66/25), so a stage this module set to 0 stays 0 in BOTH build modes - identical
to how _apply_aphiastas_finger2_zero's zeroes survive. verify() re-checks the
invariant in the post-finalization phase (step 4), fail-loud.
"""

MODULE_NAME = "Legion soul-stages (one soul per death-transform encounter)"

_SPAWN_FIELD = 'actorToSpawnOnDeath'
_CHANCE_FIELD = 'chanceToEquipFinger2'
_LOOT_FIELD = 'lootFinger2Item1'


# ── small value helpers (get_field_value returns scalar OR list) ─────────────
def _scalar(v):
    return (v[0] if v else None) if isinstance(v, list) else v


def _as_list(v):
    return [] if v is None else (v if isinstance(v, list) else [v])


def _soul_basename(ref):
    """'legion_soul_n (amgoz... conflicted copy).dbr' -> 'legion_soul';
    'charon_soul_e.dbr' -> 'charon_soul'. Tier suffix + parenthetical stripped so
    the three _n/_e/_l tiers of one soul collapse to a single identity."""
    import os
    stem = os.path.basename(str(ref)).rsplit('.dbr', 1)[0]
    stem = stem.split(' (')[0].strip()
    low = stem.lower()
    for suf in ('_n', '_e', '_l'):
        if low.endswith(suf):
            return stem[:-2]
    return stem


def _soul_drop(db, rec):
    """(chance:float, [soul refs]) for rec's Finger2 soul loot. Only refs whose
    path contains 'soul' count (matches the monolith's own soul test)."""
    ch = _scalar(db.get_field_value(rec, _CHANCE_FIELD))
    try:
        ch = float(ch) if ch is not None else 0.0
    except (TypeError, ValueError):
        ch = 0.0
    refs = [str(v) for v in _as_list(db.get_field_value(rec, _LOOT_FIELD))
            if v and 'soul' in str(v).lower()]
    return ch, refs


def _analyze(db):
    """Pure read-only analysis of the FINAL assembled db. Returns a dict:

      to_zero            : sorted list of records (non-terminal same-soul dups
                           whose chance must be 0)
      same_soul_chains   : list of {soul, keep, zeroed:[...]} (the fixed defect)
      distinct_multi     : list of {members:[...], souls:[...]} = forward chains
                           that still carry >=2 DISTINCT souls (reported, NOT
                           auto-fixed)
      inverse_empty      : list of Hero/Boss/Quest transform HEADS whose whole
                           forward chain drops NO soul (unobtainable-soul check)
    """
    names = db.record_names()
    norm = {n.replace('/', '\\').lower(): n for n in names}

    # forward death-transform edges (only where the target resolves to a record)
    fwd = {}
    for n in names:
        v = _scalar(db.get_field_value(n, _SPAWN_FIELD))
        if v and str(v).strip():
            t = norm.get(str(v).replace('/', '\\').lower())
            if t:
                fwd[n] = t
    indeg = {}
    for _a, b in fwd.items():
        indeg[b] = indeg.get(b, 0) + 1

    def fwd_set(start, limit=64):
        """Set of records strictly forward-reachable from start (cycle-safe)."""
        out, seen, cur = set(), {start}, start
        while cur in fwd and len(out) < limit:
            nxt = fwd[cur]
            if nxt in seen:
                break
            out.add(nxt)
            seen.add(nxt)
            cur = nxt
        return out

    def fwd_chain(start, limit=64):
        chain, seen, cur = [start], {start}, start
        while cur in fwd and len(chain) < limit:
            nxt = fwd[cur]
            if nxt in seen:
                break
            chain.append(nxt)
            seen.add(nxt)
            cur = nxt
        return chain

    # every soul-dropping record -> its soul basename(s) (normally one)
    droppers = {}
    for n in names:
        ch, refs = _soul_drop(db, n)
        if ch > 0 and refs:
            droppers[n] = sorted({_soul_basename(r) for r in refs})

    # index droppers by soul basename
    by_soul = {}
    for rec, bases in droppers.items():
        for b in bases:
            by_soul.setdefault(b, set()).add(rec)

    # SAME-SOUL defect: a soul S with two droppers A,B where B is forward-reachable
    # from A. Then A is a non-terminal duplicate for S -> zero it. The kept stage
    # is the terminal-most (reaches no other S-dropper forward).
    to_zero = set()
    same_soul_chains = []
    for soul in sorted(by_soul):
        ds = by_soul[soul]
        if len(ds) < 2:
            continue
        zeroed_here = sorted(a for a in ds if fwd_set(a) & ds)
        if not zeroed_here:
            continue  # 2+ droppers but none forward-reaches another (parallel
                      # difficulty variants, e.g. hades_soul on form3_50/52/54)
        keep = sorted(a for a in ds if not (fwd_set(a) & ds))
        to_zero.update(zeroed_here)
        same_soul_chains.append({'soul': soul, 'keep': keep, 'zeroed': zeroed_here})

    # DISTINCT-soul multi-soul chains (reported, not fixed): a forward chain, from
    # a true head, that carries >=2 stages dropping souls, AFTER the same-soul
    # zeroing is applied in-model.
    distinct_multi = []
    heads = sorted(h for h in fwd if indeg.get(h, 0) == 0)
    for h in heads:
        chain = fwd_chain(h)
        live = [m for m in chain if m in droppers and m not in to_zero]
        soul_ids = sorted({b for m in live for b in droppers[m]})
        if len(live) >= 2 and len(soul_ids) >= 2:
            distinct_multi.append({'members': chain, 'live': live,
                                   'souls': soul_ids})

    # INVERSE defect: Hero/Boss/Quest transform head whose whole forward chain
    # drops NO soul anywhere (an encounter that should award a soul but cannot).
    def rank(rec):
        for f in ('monsterClassification', 'Class'):
            val = _scalar(db.get_field_value(rec, f))
            if val:
                return str(val)
        return '?'

    inverse_empty = []
    for h in heads:
        if rank(h) not in ('Hero', 'Boss', 'Quest'):
            continue
        chain = fwd_chain(h)
        if not any(m in droppers for m in chain):
            inverse_empty.append(h)

    return {
        'to_zero': sorted(to_zero),
        'same_soul_chains': same_soul_chains,
        'distinct_multi': distinct_multi,
        'inverse_empty': inverse_empty,
    }


def apply(db, tags):
    """Zero chanceToEquipFinger2 on every non-terminal stage that drops a soul
    ALSO dropped by a deeper stage of its own death-transform chain (keep the
    terminal-most drop). Loud, never silent."""
    res = _analyze(db)

    zeroed = 0
    for rec in res['to_zero']:
        ch, _refs = _soul_drop(db, rec)
        if ch <= 0:
            continue  # already 0 (idempotent)
        # existing FLOAT field -> no explicit dtype (dtype-safe; refs kept inert).
        db.set_field(rec, _CHANCE_FIELD, 0.0)
        db._modified.add(rec)
        zeroed += 1

    print("  legion_soul_stages: same-soul death-transform chains reduced to the "
          "final stage only:")
    if not res['same_soul_chains']:
        print("    (none found)")
    for c in res['same_soul_chains']:
        print("    soul '%s': keep %s ; zeroed %d non-terminal stage(s): %s"
              % (c['soul'], [_short(x) for x in c['keep']],
                 len(c['zeroed']), [_short(x) for x in c['zeroed']]))
    print("  legion_soul_stages: %d non-terminal soul drop(s) zeroed "
          "(chance->0, loot refs kept inert)." % zeroed)

    # Report (do NOT fix) death-transform chains that carry >=2 DISTINCT souls.
    # Auto-zeroing one would orphan a genuinely-different collectible (inverse
    # defect) - a design ruling, see the b56 report.
    if res['distinct_multi']:
        print("  legion_soul_stages: NOTE - %d death-transform chain(s) drop "
              ">=2 DISTINCT souls (NOT auto-fixed; design ruling needed - see "
              "docs/reports/b56_legion_soul_stages.md):" % len(res['distinct_multi']))
        for c in res['distinct_multi']:
            print("    %s  ::  souls=%s"
                  % (' -> '.join(_short(m) for m in c['members']), c['souls']))

    if res['inverse_empty']:
        print("  legion_soul_stages: NOTE - %d Hero/Boss/Quest transform head(s) "
              "with NO soul anywhere in the chain (unobtainable-soul candidates): "
              "%s" % (len(res['inverse_empty']),
                      [_short(x) for x in res['inverse_empty']]))


def verify(db, tags):
    """POST-FINALIZATION invariant (fail-loud): no death-transform chain has more
    than ONE stage dropping the SAME soul item. I.e. for every soul, no dropper
    is forward-reachable from another dropper of that same soul. This is exactly
    the Legion defect; it holds by construction after apply() and is re-checked
    here over the FINAL assembled db (after the drop-rate forcer)."""
    res = _analyze(db)
    if res['to_zero']:
        # Any record still needing zeroing = a same-soul chain with >1 live stage.
        offenders = []
        for c in res['same_soul_chains']:
            offenders.append("soul '%s' still dropped by non-terminal stage(s) %s"
                             % (c['soul'], [_short(x) for x in c['zeroed']]))
        raise SystemExit(
            "legion_soul_stages.verify FAIL: %d death-transform chain(s) still "
            "drop the SAME soul from >1 stage (one soul per encounter violated):\n"
            "    %s" % (len(res['same_soul_chains']), "\n    ".join(offenders)))
    n_chains = len(res['same_soul_chains'])  # 0 after a clean apply
    print("  legion_soul_stages.verify OK: no death-transform chain drops the "
          "same soul from >1 stage (%d same-soul chain(s) already reduced; "
          "%d distinct-soul chain(s) reported for design ruling; %d empty-chain "
          "inverse candidate(s))."
          % (n_chains, len(res['distinct_multi']), len(res['inverse_empty'])))


def _short(rec):
    """Trim a record path to its basename for compact logs."""
    import os
    return os.path.basename(str(rec))
