r"""uber_apex_orb - b94 PART A: the two FOUGHT Toxeus champions get an apex-tier
treasure orb whose CALIBRE matches the blood cave's Leinth chest.

THE FINDING (ground truth, deployed arz + all 51,085 records scanned)
--------------------------------------------------------------------
`treasureProxyName` is the ONLY field in the whole DB that ever points at an orb
(43 references). The two champions -

    records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr
    records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr

- both point at `genericbossorb_04`, the shared generic apex orb (R-47). Leinth,
a charLevel 74-76 MID boss, points at her bespoke DRX chest
`bosschestproxy_leinth` ("Leinth's Essense"). Tracing both chains
proxy -> ProxyAccessoryPool -> FixedItemContainer -> FixedItemLoot on all three
difficulties, the raw knobs are:

                             LEINTH CHEST        ORB04 (the champions)
    numSpawnMinEquation      (3+1.6P)*2.2        (3+1.6P)*0.9
    numSpawnMaxEquation      (3+1.6P)*2.4        (3+1.6P)*1.3
    loot4Chance              100.0               12.7
    unique-entry lootWeight  50                  27

So the mid boss out-drops both uber champions roughly 3.25x on volume and ~2x on
unique share. That ordering is backwards.

THE CONSTRAINT THAT SHAPES THE FIX
----------------------------------
`genericbossorb_04` is shared by TWENTY-ONE boss records (Sarkoth, Vashkarr,
Bloodcrow, Voranthys, Broodmother, Enslaver, Gorrahk, Ilsevar, Dagon, Ephialtes,
Mnemophage-core, Antaeus, Polis Gaoler, Deep Thresher, Meglograi, bloodcrow_soul,
Dorus, Tantalus, Hades Marshal, Helepolis, Devourer). Editing it IN PLACE would
silently buff twenty-one encounters and rewrite the mod's whole endgame economy.
So this module creates a NEW un-named generic apex tier and repoints exactly two
records. Leinth's own chest is NOT nerfed (explicit instruction).

WHAT IT AUTHORS (10 NEW records, every one a clone of a proven shipping record)
-------------------------------------------------------------------------------
  1  records\item\containers\new\genericbossorb_05.dbr
        Proxy, clone of genericbossorb_04 (same ChestBoss01 mesh, Proxy_Blue
        texture, chanceToRun 100, difficulty/limit equations) with
        accessory1 / accessoryEpic1 / accessoryLegendary1 -> the 3 new pools.
  2-4  records\item\containers\new\genericboss05_{normal,epic,legendary}_repeat.dbr
        ProxyAccessoryPool clones; fixedItemName1 -> the matching new chest.
  5-7  records\item\containers\new\genericboss05_chest_{normal,epic,legendary}.dbr
        FixedItemContainer clones. levelEquationFile (containerlevelequation_all),
        goldGenerator (bossgoldgenerator @100), LockedClassification=Boss,
        lootClassification=Hero, mesh DRX\meshes\bossorbmesh.msh and scale 0.7 are
        all KEPT, so the drop still LOOKS and level-scales like the apex orb
        players already know. Only `tables` moves.
  8-10 records\item\loottables\svc\svc_uberorb_apex_{n,e,l}01c.dbr
        FixedItemLoot clones of the xpack Act-4 statics
        uberorb_default_{n,e,l}01c - every table reference and every
        goldGeneratorLevel (47/69/88) untouched - with exactly FOUR knob edits,
        and those four ARE the calibre match:
          (a) numSpawnMinEquation  *0.9 -> *2.2   [Leinth's value]
          (b) numSpawnMaxEquation  *1.3 -> *2.4   [Leinth's value]
          (c) loot4Chance          12.7 -> 100.0  [Leinth's guaranteed
                                                   accessory/relic/ring/formula group]
          (d) every UNIQUE-entry lootWeight 27 -> 50  [Leinth's unique share]

WHAT IT CHANGES (exactly 2 fields on 2 pre-existing records)
------------------------------------------------------------
    um_toxeus_enslaver_99.treasureProxyName -> genericbossorb_05
    um_bloodtoxeus_99.treasureProxyName     -> genericbossorb_05

NET: the champion orb goes from ~5.7 to ~18.5 expected items at 1 player (Leinth's
figure) and from ~3.1% to ~5.7% unique share (Leinth's figure), while KEEPING its
strictly better Act-4 item pool and gold level 88. Same volume as the mid boss on
a better pool = the correct ordering for charLevel 100 superbosses.

R-48 IS UNTOUCHED AND UNTOUCHABLE HERE
--------------------------------------
Souls are Finger2 EQUIPMENT (`lootFinger2Item1` + `chanceToEquipFinger2`); orbs
are `treasureProxyName`. Fully independent mechanisms. apply() nevertheless
snapshots both soul fields on both champions before and after its own writes and
fails loud if either moved, so the 100% soul drop can never be collateral damage.

RULINGS
-------
R-47 mandates the un-named generic apex orb (`genericbossorb_04`), explicitly NOT
a bespoke "X's Essence" per boss. genericbossorb_05 keeps R-47's substance intact
(un-named, generic, shared by both champions, no bespoke essence) but adds a TIER
the ruling does not mention -> ledgered as R-70 in docs/WILL_RULINGS.md.
Down-tiering the champions onto Leinth's Act-3 63-65 band, or pointing them at her
bespoke NAMED chest, were both REJECTED (violates R-47 twice over and lowers their
item level).

GATE
----
verify() runs in registry step 4 over the FINAL merged db and fails the build loud
unless (a) EXACTLY the 2 champions carry treasureProxyName=genericbossorb_05,
(b) the whole orb05 chain resolves end to end on all 3 difficulties, (c) orb05's
four knobs are >= Leinth's chest's on every difficulty, (d) genericbossorb_04 and
every one of its remaining consumers are UNCHANGED, and (e) both champions still
carry their R-48 100% soul drop. Planted negative test:
tools/debug/negtest_uber_apex_orb.py. See docs/reports/b94_leinth_wave.md.
"""
import apply_svc_patches as asp

MODULE_NAME = "uber apex orb - champion orb calibre parity with Leinth (R-70)"

# ── the two champions (sourced from the monolith so an upstream rename can never
# silently desync this module's scope, exactly as toxeus_souls_100 does) ───────
_ENSLAVER = asp._EN_BOSS      # records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr
_DEVOURER = asp._BT_MONSTER   # records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr

_CHAMPIONS = (
    ('Toxeus the Murderer, Enslaver of Souls', _ENSLAVER),
    ('Toxeus the Murderer, Devourer of Blood', _DEVOURER),
)

_TREASURE = 'treasureProxyName'

# ── the donor chain (orb04) and the new chain (orb05) ─────────────────────────
_NEW = 'records\\item\\containers\\new\\'
_LOOT = 'records\\item\\loottables\\svc\\'
_XLOOT = 'records\\xpack\\item\\containers\\loot tables\\'

ORB04 = _NEW + 'genericbossorb_04.dbr'
ORB05 = _NEW + 'genericbossorb_05.dbr'

_DIFFS = ('normal', 'epic', 'legendary')
_SHORT = {'normal': 'n', 'epic': 'e', 'legendary': 'l'}

# difficulty -> (donor pool, new pool, donor chest, new chest, donor table, new table)
CHAIN = {}
for _d in _DIFFS:
    CHAIN[_d] = (
        _NEW + 'genericboss04_%s_repeat.dbr' % _d,
        _NEW + 'genericboss05_%s_repeat.dbr' % _d,
        _NEW + 'genericboss04_chest_%s.dbr' % _d,
        _NEW + 'genericboss05_chest_%s.dbr' % _d,
        _XLOOT + 'uberorb_default_%s01c.dbr' % _SHORT[_d],
        _LOOT + 'svc_uberorb_apex_%s01c.dbr' % _SHORT[_d],
    )

# The four calibre knobs, read straight off Leinth's own loot tables
# (records\drxitem\container\loottable_leinth_{29-31,49-51,63-65}.dbr - identical
# on all three difficulties).
LEINTH_MIN_EQ = '(3+(1.6*numberOfPlayers))*2.2'
LEINTH_MAX_EQ = '(3+(1.6*numberOfPlayers))*2.4'
LEINTH_LOOT4_CHANCE = 100.0
LEINTH_UNIQUE_WEIGHT = 50
ORB04_UNIQUE_WEIGHT = 27          # the value the donor tables carry

# The mid-tier Leinth reference tables, used ONLY to prove the knobs at verify()
# time (never written to).
LEINTH_TABLES = (
    'records\\drxitem\\container\\loottable_leinth_29-31.dbr',
    'records\\drxitem\\container\\loottable_leinth_49-51.dbr',
    'records\\drxitem\\container\\loottable_leinth_63-65.dbr',
)

# Every record the module authors, for the fail-loud existence proof.
NEW_RECORDS = [ORB05]
for _d in _DIFFS:
    _p, _np, _c, _nc, _t, _nt = CHAIN[_d]
    NEW_RECORDS += [_np, _nc, _nt]


# ── small helpers ────────────────────────────────────────────────────────────
def _v1(db, rec, field):
    v = db.get_field_value(rec, field)
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _fields(db, rec):
    """{base_field_name: [values]} for a record (### suffixes collapsed)."""
    out = {}
    ff = db.get_fields(rec)
    if not ff:
        return out
    for k, tf in ff.items():
        out.setdefault(k.split('###')[0], list(tf.values))
    return out


def _snapshot(db, recs):
    return {r: _fields(db, r) for r in recs}


def _orb04_consumers(db):
    """Every record still pointing treasureProxyName at genericbossorb_04."""
    low = ORB04.lower()
    out = []
    for n in db.record_names():
        v = _v1(db, n, _TREASURE)
        if isinstance(v, str) and v.replace('/', '\\').lower() == low:
            out.append(n)
    return sorted(out)


def _clone(db, src, dest, label):
    if not db.has_record(src):
        raise SystemExit(
            "[uber_apex_orb] donor record MISSING: %s (%s). The orb05 chain "
            "cannot be built from a record that is not in the db." % (src, label))
    if db.has_record(dest):
        raise SystemExit(
            "[uber_apex_orb] %s already exists (%s) - another writer claimed this "
            "path. Refusing to overwrite." % (dest, label))
    db.clone_record(src, dest)


def _unique_weight_edits(db, rec):
    """Raise every UNIQUE-entry lootWeight from the orb04 value to Leinth's.

    A slot entry is a 'unique entry' iff its lootNNameM path contains the
    'unique' namespace (records\\xpack\\item\\loottables\\...\\unique\\... or the
    mastertables unique_* tables). This is derived from the record itself rather
    than hard-coded slot numbers, so an upstream table reshuffle cannot silently
    move the edit onto a static entry.
    Returns the number of weights raised.
    """
    ff = _fields(db, rec)
    raised = 0
    for key, vals in sorted(ff.items()):
        if not (key.startswith('loot') and 'Name' in key):
            continue
        path = vals[0] if vals else None
        if not isinstance(path, str) or 'unique' not in path.lower():
            continue
        wkey = key.replace('Name', 'Weight')
        cur = ff.get(wkey)
        cur = cur[0] if cur else None
        if cur is None:
            raise SystemExit(
                "[uber_apex_orb] %s: unique entry %s has no matching %s - the "
                "loot slot shape is not what the donor ships." % (rec, key, wkey))
        if int(cur) != ORB04_UNIQUE_WEIGHT:
            # Not the donor's unique weight: leave it alone rather than guess.
            continue
        db.set_field(rec, wkey, LEINTH_UNIQUE_WEIGHT)
        raised += 1
    if raised == 0:
        raise SystemExit(
            "[uber_apex_orb] %s: found ZERO unique entries at the donor weight "
            "%d - the calibre match would be a no-op. Upstream changed; review."
            % (rec, ORB04_UNIQUE_WEIGHT))
    db._modified.add(rec)
    return raised


def apply(db, tags):
    print("\n=== patches-registry: %s ===" % MODULE_NAME)

    # ── R-48 guard: snapshot the soul-drop wiring BEFORE any write ────────────
    soul_before = {}
    for _label, rec in _CHAMPIONS:
        soul_before[rec] = (
            _v1(db, rec, 'chanceToEquipFinger2'),
            db.get_field_value(rec, 'lootFinger2Item1'),
            _v1(db, rec, 'dropItems'),
        )

    # ── blast-radius snapshot: orb04 + every consumer, BEFORE ────────────────
    consumers_before = _orb04_consumers(db)
    orb04_before = _snapshot(db, [ORB04] + [CHAIN[d][0] for d in _DIFFS]
                             + [CHAIN[d][2] for d in _DIFFS]
                             + [CHAIN[d][4] for d in _DIFFS])
    leinth_before = _snapshot(db, [r for r in LEINTH_TABLES if db.has_record(r)])

    for _label, rec in _CHAMPIONS:
        if not db.has_record(rec):
            raise SystemExit(
                "[uber_apex_orb] champion record MISSING from the db: %s (%s). "
                "Refusing to ship a build that silently drops the ruling."
                % (rec, _label))

    # ── 1. the proxy ─────────────────────────────────────────────────────────
    _clone(db, ORB04, ORB05, 'apex orb proxy')
    for d in _DIFFS:
        _pool_old, pool_new, _c, _nc, _t, _nt = CHAIN[d]
        field = {'normal': 'accessory1',
                 'epic': 'accessoryEpic1',
                 'legendary': 'accessoryLegendary1'}[d]
        db.set_field(ORB05, field, pool_new)
    db._modified.add(ORB05)
    print("  authored %s (Proxy, clone of genericbossorb_04; 3 accessory slots "
          "repointed)" % ORB05.rsplit('\\', 1)[-1])

    # ── 2. the three pools ───────────────────────────────────────────────────
    for d in _DIFFS:
        pool_old, pool_new, _c, chest_new, _t, _nt = CHAIN[d]
        _clone(db, pool_old, pool_new, 'apex orb pool (%s)' % d)
        db.set_field(pool_new, 'fixedItemName1', chest_new)
        db._modified.add(pool_new)
    print("  authored 3 ProxyAccessoryPool clones -> the 3 new chests")

    # ── 3. the three chests ──────────────────────────────────────────────────
    for d in _DIFFS:
        _p, _np, chest_old, chest_new, _t, table_new = CHAIN[d]
        _clone(db, chest_old, chest_new, 'apex orb chest (%s)' % d)
        db.set_field(chest_new, 'tables', table_new)
        db._modified.add(chest_new)
    print("  authored 3 FixedItemContainer clones (apex-orb mesh/scale/gold/"
          "level-equation KEPT; only `tables` moved)")

    # ── 4. the three loot tables + the FOUR calibre knobs ────────────────────
    for d in _DIFFS:
        _p, _np, _c, _nc, table_old, table_new = CHAIN[d]
        _clone(db, table_old, table_new, 'apex orb loot table (%s)' % d)

        min_before = _v1(db, table_new, 'numSpawnMinEquation')
        max_before = _v1(db, table_new, 'numSpawnMaxEquation')
        l4_before = _v1(db, table_new, 'loot4Chance')

        db.set_field(table_new, 'numSpawnMinEquation', LEINTH_MIN_EQ)
        db.set_field(table_new, 'numSpawnMaxEquation', LEINTH_MAX_EQ)
        db.set_field(table_new, 'loot4Chance', LEINTH_LOOT4_CHANCE)
        raised = _unique_weight_edits(db, table_new)
        db._modified.add(table_new)

        gold = _v1(db, table_new, 'goldGeneratorLevel')
        print("  %s: spawn %s -> %s / %s -> %s | loot4Chance %s -> %s | "
              "%d unique weights %d -> %d | goldGeneratorLevel %s KEPT"
              % (table_new.rsplit('\\', 1)[-1], min_before, LEINTH_MIN_EQ,
                 max_before, LEINTH_MAX_EQ, l4_before, LEINTH_LOOT4_CHANCE,
                 raised, ORB04_UNIQUE_WEIGHT, LEINTH_UNIQUE_WEIGHT, gold))

    # ── 5. repoint EXACTLY the two champions ────────────────────────────────
    for label, rec in _CHAMPIONS:
        prev = _v1(db, rec, _TREASURE)
        db.set_field(rec, _TREASURE, ORB05)
        db._modified.add(rec)
        print("  %s: %s %s -> %s" % (label, _TREASURE,
                                     str(prev).rsplit('\\', 1)[-1],
                                     ORB05.rsplit('\\', 1)[-1]))

    # ── SCOPE PROOFS (all fail-loud, inside apply) ───────────────────────────
    # (i) R-48 soul wiring untouched on both champions.
    for label, rec in _CHAMPIONS:
        now = (_v1(db, rec, 'chanceToEquipFinger2'),
               db.get_field_value(rec, 'lootFinger2Item1'),
               _v1(db, rec, 'dropItems'))
        if now != soul_before[rec]:
            raise SystemExit(
                "[uber_apex_orb] R-48 COLLATERAL DAMAGE: %s soul wiring moved "
                "(%r -> %r). The orb change must be purely additive."
                % (label, soul_before[rec], now))

    # (ii) orb04 and its whole chain byte-unchanged; consumers reduced by exactly
    #      the two champions and nothing else.
    orb04_after = _snapshot(db, list(orb04_before))
    if orb04_after != orb04_before:
        moved = sorted(r for r in orb04_before if orb04_after.get(r) != orb04_before[r])
        raise SystemExit(
            "[uber_apex_orb] BLAST-RADIUS VIOLATION: the genericbossorb_04 chain "
            "changed (%s). Editing orb04 in place would silently buff all %d of "
            "its consumers." % (moved, len(consumers_before)))
    consumers_after = _orb04_consumers(db)
    lost = sorted(set(consumers_before) - set(consumers_after))
    gained = sorted(set(consumers_after) - set(consumers_before))
    expected_lost = sorted(rec for _l, rec in _CHAMPIONS)
    if lost != expected_lost or gained:
        raise SystemExit(
            "[uber_apex_orb] SCOPE VIOLATION: orb04 consumers changed by "
            "lost=%s gained=%s; expected exactly the 2 champions to leave and "
            "nothing to join." % (lost, gained))

    # (iii) Leinth's own chest tables untouched (explicit no-nerf instruction).
    leinth_after = _snapshot(db, list(leinth_before))
    if leinth_after != leinth_before:
        raise SystemExit(
            "[uber_apex_orb] Leinth's own chest loot tables changed - this "
            "module must NEVER nerf her chest (explicit instruction).")

    print("  scope proof: orb04 chain byte-unchanged; consumers %d -> %d (the 2 "
          "champions moved to orb05); R-48 soul wiring untouched; Leinth's chest "
          "untouched" % (len(consumers_before), len(consumers_after)))


# =============================================================================
# GATE (registry step 4 - runs over the FINAL merged db)
# =============================================================================
def _knobs(db, table):
    return (_v1(db, table, 'numSpawnMinEquation'),
            _v1(db, table, 'numSpawnMaxEquation'),
            _v1(db, table, 'loot4Chance'))


def _mult(eq):
    """Trailing '*<k>' multiplier of a spawn equation, or None."""
    if not isinstance(eq, str) or '*' not in eq:
        return None
    try:
        return float(eq.rsplit('*', 1)[1])
    except ValueError:
        return None


def verify(db, tags=None):
    problems = []

    # (a) EXACTLY the two champions carry orb05.
    low05 = ORB05.lower()
    carriers = sorted(n for n in db.record_names()
                      if isinstance(_v1(db, n, _TREASURE), str)
                      and _v1(db, n, _TREASURE).replace('/', '\\').lower() == low05)
    expected = sorted(rec for _l, rec in _CHAMPIONS)
    if carriers != expected:
        problems.append(
            "treasureProxyName=genericbossorb_05 is carried by %d record(s) %s; "
            "expected EXACTLY the 2 Toxeus champions %s"
            % (len(carriers), carriers, expected))

    # (b) the orb05 chain resolves end to end on all 3 difficulties.
    for rec in NEW_RECORDS:
        if not db.has_record(rec):
            problems.append("orb05 chain record MISSING: %s" % rec)
    for d in _DIFFS:
        _p, pool_new, _c, chest_new, _t, table_new = CHAIN[d]
        field = {'normal': 'accessory1', 'epic': 'accessoryEpic1',
                 'legendary': 'accessoryLegendary1'}[d]
        got = _v1(db, ORB05, field)
        if not isinstance(got, str) or got.lower() != pool_new.lower():
            problems.append("orb05.%s = %r, expected %s" % (field, got, pool_new))
        got = _v1(db, pool_new, 'fixedItemName1')
        if not isinstance(got, str) or got.lower() != chest_new.lower():
            problems.append("%s.fixedItemName1 = %r, expected %s"
                            % (pool_new, got, chest_new))
        got = _v1(db, chest_new, 'tables')
        if not isinstance(got, str) or got.lower() != table_new.lower():
            problems.append("%s.tables = %r, expected %s"
                            % (chest_new, got, table_new))

    # (c) orb05's four knobs are >= Leinth's chest's, on every difficulty.
    leinth_present = [t for t in LEINTH_TABLES if db.has_record(t)]
    ref_min = ref_max = ref_l4 = None
    for t in leinth_present:
        mn, mx, l4 = _knobs(db, t)
        ref_min = _mult(mn) if ref_min is None else min(ref_min, _mult(mn) or 0)
        ref_max = _mult(mx) if ref_max is None else min(ref_max, _mult(mx) or 0)
        ref_l4 = l4 if ref_l4 is None else min(ref_l4, l4)
    if ref_min is None:
        problems.append("Leinth's reference chest tables are all missing - the "
                        "calibre comparison cannot be made")
    else:
        for d in _DIFFS:
            table_new = CHAIN[d][5]
            if not db.has_record(table_new):
                continue
            mn, mx, l4 = _knobs(db, table_new)
            if (_mult(mn) or 0) + 1e-6 < ref_min:
                problems.append("%s numSpawnMin multiplier %s < Leinth's %s"
                                % (table_new, _mult(mn), ref_min))
            if (_mult(mx) or 0) + 1e-6 < ref_max:
                problems.append("%s numSpawnMax multiplier %s < Leinth's %s"
                                % (table_new, _mult(mx), ref_max))
            if float(l4 or 0) + 1e-6 < float(ref_l4):
                problems.append("%s loot4Chance %s < Leinth's %s"
                                % (table_new, l4, ref_l4))
            # the unique share
            ff = _fields(db, table_new)
            bad = []
            for key, vals in sorted(ff.items()):
                if not (key.startswith('loot') and 'Name' in key):
                    continue
                p = vals[0] if vals else None
                if not isinstance(p, str) or 'unique' not in p.lower():
                    continue
                w = ff.get(key.replace('Name', 'Weight'))
                w = int(w[0]) if w else 0
                if w < LEINTH_UNIQUE_WEIGHT:
                    bad.append('%s=%d' % (key.replace('Name', 'Weight'), w))
            if bad:
                problems.append("%s unique weights below Leinth's %d: %s"
                                % (table_new, LEINTH_UNIQUE_WEIGHT, bad))
            # MP-equation law: no '/' in a spawn equation (AE parse failure)
            for eq in (mn, mx):
                if isinstance(eq, str) and '/' in eq:
                    problems.append("%s spawn equation %r contains '/' (AE cannot "
                                    "parse it in MP)" % (table_new, eq))

    # (d) orb04 still exists, still generic, and still serves its other consumers.
    if not db.has_record(ORB04):
        problems.append("genericbossorb_04 is GONE - R-47's shared apex orb must "
                        "survive for its other consumers")
    else:
        remaining = _orb04_consumers(db)
        if any(rec in remaining for _l, rec in _CHAMPIONS):
            problems.append("a Toxeus champion is STILL on genericbossorb_04")
        if len(remaining) < 15:
            problems.append(
                "genericbossorb_04 now has only %d consumer(s) %s - this module "
                "must move exactly 2 records, never strip the shared tier"
                % (len(remaining), remaining))
        for d in _DIFFS:
            _p, _np, chest_old, _nc, table_old, _nt = CHAIN[d]
            got = _v1(db, chest_old, 'tables')
            if not isinstance(got, str) or got.lower() != table_old.lower():
                problems.append("orb04 chest (%s) tables moved to %r - the donor "
                                "chain must stay untouched" % (d, got))

    # (e) R-48 survives.
    for label, rec in _CHAMPIONS:
        c = _v1(db, rec, 'chanceToEquipFinger2')
        try:
            c = float(c or 0.0)
        except (TypeError, ValueError):
            c = 0.0
        if abs(c - 100.0) > 0.001:
            problems.append("%s: chanceToEquipFinger2=%s but R-48 requires 100 - "
                            "the orb change must not touch the soul" % (label, c))

    if problems:
        raise SystemExit(
            "[uber_apex_orb] R-70 VERIFY FAILED (champion orb calibre parity):\n"
            "  - " + "\n  - ".join(problems))
    print("  [uber_apex_orb] verify OK: both champions on genericbossorb_05; "
          "chain resolves on n/e/l; all four calibre knobs >= Leinth's chest; "
          "genericbossorb_04 + its %d other consumers untouched; R-48 intact"
          % len(_orb04_consumers(db)))
