r"""uber_apex_orb - b94 PART A: ONE apex drop calibre, shared by all THREE blood
cave bosses - both FOUGHT Toxeus champions AND Leinth.

WILL'S DECISION 2026-07-27 (verbatim), which SUPERSEDES the original design pass
-------------------------------------------------------------------------------
    "increase the tier of the items dropped by leinth's orb to match the tier
     dropped by the champions' orb and give that to both toxeus variants and
     also to leinth"

So this is NOT "raise the champions to Leinth". It is: build ONE apex drop that
combines Leinth's GENEROSITY (quantity) with the champions' TIER (item pool), and
give that single calibre to all three. Leinth is INCLUDED and UPGRADED, never
nerfed and never left behind.

THE FINDING (ground truth, deployed arz + all 51,085 records scanned)
--------------------------------------------------------------------
`treasureProxyName` is the ONLY field in the whole DB that ever points at an orb
(43 references). The two champions -

    records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr
    records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr

- both point at `genericbossorb_04`, the shared generic apex orb (R-47). Leinth
(all three variants) points at her bespoke DRX chest `bosschestproxy_leinth`
("Leinth's Essense"). Each side wins on a DIFFERENT axis, which is why the fix
has to combine them rather than pick one:

                             LEINTH CHEST            ORB04 (the champions)
    numSpawnMinEquation      (3+1.6P)*2.2            (3+1.6P)*0.9       <- her win
    numSpawnMaxEquation      (3+1.6P)*2.4            (3+1.6P)*1.3       <- her win
    loot4Chance              100.0                   12.7               <- her win
    unique-entry lootWeight  50                      27                 <- her win
    loot tables              Act-3 63-65 band        xpack Act-4 statics <- their win
    levelEquationFile        c03 / e_c03 / l_c02     containerlevelequation_all
                             (normal+epic DIVIDE                        <- their win
                              the player level)      (`1*1`, uncapped)
    goldGeneratorLevel       30 / 50 / 64            47 / 69 / 88       <- their win

Modelled expected items at 1 player: Leinth 18.51, orb04 5.70. The NEW shared
apex table is 21.16 - above BOTH, on the champions' better pool.

SOLE-OWNERSHIP PROOF (the precondition for upgrading her chest IN PLACE)
------------------------------------------------------------------------
Scanning EVERY field of ALL 51,085 records for a reference to
`bosschestproxy_leinth` finds EXACTLY THREE, and all three are Leinth's own
variants (`q_leinth_47/49/50`, field `treasureProxyName`). Nothing else in the
database touches her chest chain. So her chain can be upgraded in place with a
provably zero blast radius, which is strictly better than repointing her at the
generic orb: she keeps her bespoke "Leinth's Essense" name, her
`DRX\meshes\leinth_chest.msh` and her richer gold generator, and the retirement
protocol is never engaged (nothing of hers is retired). apply() re-proves the
sole-ownership on the live db and refuses to touch her chain otherwise.

THE CONSTRAINT THAT SHAPES THE CHAMPION HALF
--------------------------------------------
`genericbossorb_04` is shared by TWENTY-ONE boss records (Sarkoth, Vashkarr,
Bloodcrow, Voranthys, Broodmother, Enslaver, Gorrahk, Ilsevar, Dagon, Ephialtes,
Mnemophage-core, Antaeus, Polis Gaoler, Deep Thresher, Meglograi, bloodcrow_soul,
Dorus, Tantalus, Hades Marshal, Helepolis, Devourer). Editing it IN PLACE would
silently buff twenty-one encounters and rewrite the mod's whole endgame economy.
So the champions get a NEW un-named generic apex tier (orb05) and orb04 keeps
serving its other 19 consumers byte-unchanged.

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

WHAT IT CHANGES (8 fields on 5 pre-existing records - nothing else)
-------------------------------------------------------------------
CHAMPIONS (2 records, 1 field each) - they move onto the new generic apex tier:
    um_toxeus_enslaver_99.treasureProxyName -> genericbossorb_05
    um_bloodtoxeus_99.treasureProxyName     -> genericbossorb_05

LEINTH (3 records, 2 fields each) - her SOLE-OWNED chests are upgraded IN PLACE
to the SAME apex tables, so all three bosses share one identical calibre:
    bosschest_leinth_01_normal   .tables            -> svc_uberorb_apex_n01c
                                 .levelEquationFile -> containerlevelequation_all
    bosschest_leinth_02_epic     .tables            -> svc_uberorb_apex_e01c
                                 .levelEquationFile -> containerlevelequation_all
    bosschest_leinth_03_legendary.tables            -> svc_uberorb_apex_l01c
                                 .levelEquationFile -> containerlevelequation_all

Leinth's monster records are NOT touched at all: `treasureProxyName` still names
her own `bosschestproxy_leinth`, so R-71's "her bespoke chest survives" guarantee
(asserted by tools/patches/leinth_wave.py) stays green by construction.

DELIBERATELY NOT CHANGED ON HER CHESTS, each for a stated reason:
  * `mesh` (DRX\meshes\leinth_chest.msh), `scale` 1.2 and `description`
    (tagLeinthChest = "Leinth's Essense") - her bespoke player-visible identity.
  * `goldGenerator` (typhongoldgenerator) - it is RICHER than the champions'
    bossgoldgenerator: goldAmountEquation `(L^1.6)*48` vs `(L^1.6)*24`. Switching
    her to theirs would have been a GOLD NERF. She keeps hers AND inherits the
    higher generatorLevel (30/50/64 -> 47/69/88) from the shared apex table, so
    her gold roughly +66% on Legendary.
  * `LockedClassification` (absent on hers, 'Boss' on theirs) - it is not an
    item-tier field, and every consumer including orb04's own chests carries
    `locked = 0`, so it is inert. Adding an untested lock field to a boss chest
    is pure downside.

NET, at 1 player, on all three difficulties (model + raw knobs both in the report):
    Enslaver / Devourer   5.70 -> 21.16 expected items   (3.71x)
    Leinth               18.51 -> 21.16 expected items   (1.14x)  + a full tier
Every one of the six loot-group chances on the apex table is >= Leinth's old
table's on every difficulty, so she is provably not nerfed on ANY axis; apply()
and verify() both assert that group-by-group rather than asserting it in prose.

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
(un-named, generic, shared by both champions, no NEW bespoke essence authored) but
adds a TIER the ruling does not mention -> ledgered as R-70 in
docs/WILL_RULINGS.md. Leinth's pre-existing bespoke chest is neither created nor
retired by this module, only re-tiered, so R-47's "no bespoke essence per boss"
prohibition (which is about AUTHORING new ones) is not engaged.
Down-tiering the champions onto Leinth's Act-3 63-65 band was REJECTED (it lowers
their item level, the opposite of Will's instruction). Repointing Leinth at the
generic orb was also REJECTED once sole-ownership was proven: it would silently
destroy her "Leinth's Essense" name and her chest mesh for no mechanical gain,
and the brief explicitly authorised the in-place upgrade on that proof.

GATE
----
verify() runs in registry step 4 over the FINAL merged db and fails the build loud
unless (a) EXACTLY the 2 champions carry treasureProxyName=genericbossorb_05,
(b) the whole orb05 chain resolves end to end on all 3 difficulties, (c) orb05's
four knobs are >= Leinth's ORIGINAL chest's on every difficulty, (d)
genericbossorb_04 and every one of its remaining consumers are UNCHANGED, (e) both
champions still carry their R-48 100% soul drop, (f) all THREE of Leinth's chests
resolve to the same apex tables + level equation the champions use, (g) her
bespoke identity fields (mesh/scale/description/goldGenerator) are intact and all
three of her monster records still name her own proxy, and (h) the apex table is
>= her ORIGINAL table on every one of the six loot-group chances and on
goldGeneratorLevel (the no-nerf proof, computed rather than asserted). Her three
original loot tables are deliberately LEFT IN THE DB (retirement protocol) and are
what (c) and (h) read as the live reference. Planted negative test:
tools/debug/negtest_uber_apex_orb.py. See docs/reports/b94_leinth_wave.md.
"""
import apply_svc_patches as asp

MODULE_NAME = ("uber apex orb - ONE apex drop calibre for both Toxeus champions "
               "AND Leinth (R-70)")

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

# ── LEINTH'S OWN CHAIN (Will 2026-07-27: she is INCLUDED, upgraded in place) ──
# Sole-ownership was proven by scanning EVERY field of ALL 51,085 records: the
# only references to her proxy are the three q_leinth_* variants' treasureProxyName.
# apply() re-proves it on the live db before touching anything.
_DRXC = 'records\\drxitem\\container\\'

LEINTH_PROXY = _DRXC + 'bosschestproxy_leinth.dbr'

LEINTH_VARIANTS = (
    'records\\drxcreatures\\bloodwitch\\q_leinth_47.dbr',
    'records\\drxcreatures\\bloodwitch\\q_leinth_49.dbr',
    'records\\drxcreatures\\bloodwitch\\q_leinth_50.dbr',
)

# difficulty -> her ProxyAccessoryPool (untouched; listed so the gate can prove it)
LEINTH_POOLS = {
    'normal':    _DRXC + 'bosschestpool_leinth_01_normal.dbr',
    'epic':      _DRXC + 'bosschestpool_leinth_02_epic.dbr',
    'legendary': _DRXC + 'bosschestpool_leinth_03_legendary.dbr',
}

# difficulty -> her FixedItemContainer (THE two-field in-place upgrade lands here)
LEINTH_CHESTS = {
    'normal':    _DRXC + 'bosschest_leinth_01_normal.dbr',
    'epic':      _DRXC + 'bosschest_leinth_02_epic.dbr',
    'legendary': _DRXC + 'bosschest_leinth_03_legendary.dbr',
}

# difficulty -> her ORIGINAL mid-tier loot table. These are NEVER written to and
# NEVER deleted (retirement protocol); they stay in the db as the live reference
# the no-nerf proof reads. Keyed by difficulty so the comparison is like-for-like.
LEINTH_TABLES_BY_DIFF = {
    'normal':    _DRXC + 'loottable_leinth_29-31.dbr',
    'epic':      _DRXC + 'loottable_leinth_49-51.dbr',
    'legendary': _DRXC + 'loottable_leinth_63-65.dbr',
}
LEINTH_TABLES = tuple(LEINTH_TABLES_BY_DIFF[d] for d in _DIFFS)

# The champions' uncapped level equation ('1*1'), which every one of the 366
# top-band containers in the db uses - including all of our own SVC boss hoards
# and the DRX hidden blood-cave chests. Leinth's legendary chest is ALREADY on the
# functionally identical l_c02; only her normal + epic chests carry the Act-3
# down-scaling caps this replaces.
LEVEL_EQ_ALL = ('records\\xpack\\item\\containers\\equations\\'
                'containerlevelequation_all.dbr')

# Fields on her chests that MUST survive the upgrade untouched (her bespoke
# player-visible identity + her richer gold generator). Proven field-by-field.
LEINTH_CHEST_KEEP = ('mesh', 'scale', 'description', 'goldGenerator',
                     'goldGeneratorChance', 'lootClassification', 'locked',
                     'ActorName', 'Class', 'templateName')

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


def _all_referrers(db, target):
    """Every (record, field) in the WHOLE db whose value names `target`.

    Deliberately scans EVERY field of EVERY record rather than just
    treasureProxyName: the whole point of the sole-ownership proof is that
    NOTHING anywhere (a pool, a quest object, another proxy) also consumes
    Leinth's chain, so a treasureProxyName-only scan would not be a proof.
    """
    low = target.replace('/', '\\').lower()
    hits = []
    for n in db.record_names():
        ff = db.get_fields(n)
        if not ff:
            continue
        for k, tf in ff.items():
            for val in tf.values:
                if isinstance(val, str) and val.replace('/', '\\').lower() == low:
                    hits.append((n, k.split('###')[0]))
    return sorted(set(hits))


def _group_chances(db, table):
    """[loot1Chance .. loot6Chance] as floats (missing -> 0.0)."""
    ff = _fields(db, table)
    out = []
    for i in range(1, 7):
        v = ff.get('loot%dChance' % i)
        try:
            out.append(float(v[0]) if v else 0.0)
        except (TypeError, ValueError):
            out.append(0.0)
    return out


def _no_nerf_problems(db, apex_table, leinth_table, diff):
    """Prove the apex table is >= Leinth's ORIGINAL on every reward axis.

    Returns a list of problem strings (empty == she is not nerfed). This is
    COMPUTED from the two records, never asserted in prose, so an upstream table
    change that would quietly cost her something fails the build.
    """
    problems = []
    if not (db.has_record(apex_table) and db.has_record(leinth_table)):
        return ["%s: cannot run the no-nerf proof (apex or Leinth table missing)"
                % diff]

    # (1) every one of the six loot-group chances
    apex_c = _group_chances(db, apex_table)
    lein_c = _group_chances(db, leinth_table)
    for i, (a, l) in enumerate(zip(apex_c, lein_c), 1):
        if a + 1e-6 < l:
            problems.append(
                "%s: NERF - apex loot%dChance %.2f < Leinth's original %.2f"
                % (diff, i, a, l))

    # (2) spawn-count multipliers
    for f in ('numSpawnMinEquation', 'numSpawnMaxEquation'):
        a, l = _mult(_v1(db, apex_table, f)), _mult(_v1(db, leinth_table, f))
        if a is not None and l is not None and a + 1e-6 < l:
            problems.append("%s: NERF - apex %s multiplier %s < Leinth's %s"
                            % (diff, f, a, l))

    # (3) gold
    try:
        a = float(_v1(db, apex_table, 'goldGeneratorLevel') or 0)
        l = float(_v1(db, leinth_table, 'goldGeneratorLevel') or 0)
        if a + 1e-6 < l:
            problems.append("%s: NERF - apex goldGeneratorLevel %s < Leinth's %s"
                            % (diff, a, l))
    except (TypeError, ValueError):
        problems.append("%s: goldGeneratorLevel unreadable on one of the tables" % diff)
    return problems


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

    # ── Leinth snapshot: her ORIGINAL tables, her proxy, her pools, her chests
    #    and her three monster records, all BEFORE any write ──────────────────
    leinth_tables_before = _snapshot(db, [r for r in LEINTH_TABLES
                                          if db.has_record(r)])
    leinth_untouchable_before = _snapshot(
        db, [r for r in ([LEINTH_PROXY] + list(LEINTH_POOLS.values())
                         + list(LEINTH_VARIANTS)) if db.has_record(r)])
    leinth_chests_before = _snapshot(db, [r for r in LEINTH_CHESTS.values()
                                          if db.has_record(r)])

    for _label, rec in _CHAMPIONS:
        if not db.has_record(rec):
            raise SystemExit(
                "[uber_apex_orb] champion record MISSING from the db: %s (%s). "
                "Refusing to ship a build that silently drops the ruling."
                % (rec, _label))

    # ── SOLE-OWNERSHIP PROOF, re-run on the LIVE db ──────────────────────────
    # Will's decision includes Leinth, and the in-place upgrade of her chest is
    # only safe if NOTHING else in the database consumes her chain. Prove it
    # here rather than trusting the design pass: scan every field of every
    # record, and require the referrer set to be exactly her three variants.
    refs = _all_referrers(db, LEINTH_PROXY)
    expected_refs = sorted((r, _TREASURE) for r in LEINTH_VARIANTS)
    if refs != expected_refs:
        raise SystemExit(
            "[uber_apex_orb] SOLE-OWNERSHIP PROOF FAILED for %s.\n"
            "  found   : %s\n  expected: %s\n"
            "Leinth's chest chain may only be upgraded IN PLACE while she is its "
            "ONLY consumer. Something else now references it, so an in-place "
            "edit would have an unproven blast radius. Refusing."
            % (LEINTH_PROXY.rsplit('\\', 1)[-1], refs, expected_refs))
    print("  sole-ownership proof: %s is referenced by EXACTLY %d record(s), all "
          "of them Leinth's own variants (whole-db scan, every field)"
          % (LEINTH_PROXY.rsplit('\\', 1)[-1], len(refs)))

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

    # ── 6. LEINTH IS INCLUDED (Will 2026-07-27) ─────────────────────────────
    # Her three SOLE-OWNED chests are upgraded IN PLACE onto the SAME apex tables
    # the champions now use, plus the champions' uncapped level equation. Exactly
    # two fields per chest; her monster records and her proxy/pools are NOT
    # touched, so her bespoke "Leinth's Essense" identity survives intact.
    for d in _DIFFS:
        chest = LEINTH_CHESTS[d]
        apex_table = CHAIN[d][5]
        if not db.has_record(chest):
            raise SystemExit(
                "[uber_apex_orb] Leinth chest MISSING from the db: %s (%s). "
                "Will's decision includes her, so this is not skippable."
                % (chest, d))

        # No-nerf proof BEFORE the write, against the table she is leaving.
        nerf = _no_nerf_problems(db, apex_table, LEINTH_TABLES_BY_DIFF[d], d)
        if nerf:
            raise SystemExit(
                "[uber_apex_orb] REFUSING to move Leinth onto the apex table - it "
                "would NERF her, and the instruction is explicit that she must "
                "not be nerfed:\n  - " + "\n  - ".join(nerf))

        tbl_before = _v1(db, chest, 'tables')
        eq_before = _v1(db, chest, 'levelEquationFile')
        db.set_field(chest, 'tables', apex_table)
        db.set_field(chest, 'levelEquationFile', LEVEL_EQ_ALL)
        db._modified.add(chest)
        print("  Leinth chest (%s): tables %s -> %s | levelEquationFile %s -> %s"
              % (d,
                 str(tbl_before).rsplit('\\', 1)[-1],
                 apex_table.rsplit('\\', 1)[-1],
                 str(eq_before).rsplit('\\', 1)[-1],
                 LEVEL_EQ_ALL.rsplit('\\', 1)[-1]))

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

    # (iii) Leinth's ORIGINAL loot tables are byte-unchanged. They are retired
    #       from service but NOT edited and NOT deleted (retirement protocol), so
    #       they stay in the db as the live reference the no-nerf proof reads.
    leinth_tables_after = _snapshot(db, list(leinth_tables_before))
    if leinth_tables_after != leinth_tables_before:
        raise SystemExit(
            "[uber_apex_orb] Leinth's ORIGINAL loot tables were edited. They must "
            "stay byte-identical: they are the reference the no-nerf proof reads, "
            "and editing them would destroy the ability to prove she was not "
            "nerfed.")

    # (iv) Her proxy, her pools and her three MONSTER records are untouched, so
    #      R-71's "her bespoke chest survives" guarantee holds by construction.
    leinth_untouchable_after = _snapshot(db, list(leinth_untouchable_before))
    if leinth_untouchable_after != leinth_untouchable_before:
        moved = sorted(r for r in leinth_untouchable_before
                       if leinth_untouchable_after.get(r) != leinth_untouchable_before[r])
        raise SystemExit(
            "[uber_apex_orb] Leinth's proxy/pools/monster records changed (%s). "
            "This module upgrades her CHESTS only; her treasureProxyName must "
            "keep naming her own bespoke chest (R-71 asserts it too)." % moved)

    # (v) On her chests, EXACTLY the two intended fields moved and every bespoke
    #     identity field survived, proven field-by-field rather than in prose.
    for d in _DIFFS:
        chest = LEINTH_CHESTS[d]
        before, after = leinth_chests_before.get(chest, {}), _fields(db, chest)
        changed = sorted(k for k in set(before) | set(after)
                         if before.get(k) != after.get(k))
        if changed != ['levelEquationFile', 'tables']:
            raise SystemExit(
                "[uber_apex_orb] Leinth chest (%s) changed fields %s; expected "
                "EXACTLY ['levelEquationFile', 'tables']. Any other field moving "
                "is collateral damage to her bespoke identity." % (d, changed))
        for k in LEINTH_CHEST_KEEP:
            if before.get(k) != after.get(k):
                raise SystemExit(
                    "[uber_apex_orb] Leinth chest (%s): bespoke identity field %r "
                    "moved %r -> %r. Her name/mesh/scale/gold generator must "
                    "survive the re-tier." % (d, k, before.get(k), after.get(k)))

    print("  scope proof: orb04 chain byte-unchanged; consumers %d -> %d (the 2 "
          "champions moved to orb05); R-48 soul wiring untouched; Leinth "
          "RE-TIERED in place (2 fields x 3 chests, identity + gold generator "
          "kept, originals preserved, proven not-nerfed group-by-group)"
          % (len(consumers_before), len(consumers_after)))


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

    # (f) LEINTH IS ON THE SAME APEX CALIBRE (Will 2026-07-27). All three of her
    #     chests must resolve to the same apex tables + level equation the
    #     champions use, or she has been left behind.
    for d in _DIFFS:
        chest = LEINTH_CHESTS[d]
        apex_table = CHAIN[d][5]
        if not db.has_record(chest):
            problems.append("Leinth chest MISSING: %s" % chest)
            continue
        got = _v1(db, chest, 'tables')
        if not isinstance(got, str) or got.replace('/', '\\').lower() != apex_table.lower():
            problems.append(
                "Leinth chest (%s) tables = %r, expected the shared apex table %s "
                "- she must drop the SAME calibre as the champions" % (d, got, apex_table))
        got = _v1(db, chest, 'levelEquationFile')
        if not isinstance(got, str) or got.replace('/', '\\').lower() != LEVEL_EQ_ALL.lower():
            problems.append(
                "Leinth chest (%s) levelEquationFile = %r, expected %s - without "
                "the uncapped equation her items stay down-tiered on normal/epic"
                % (d, got, LEVEL_EQ_ALL))

    # (g) Her bespoke identity survived the re-tier, and her monster records still
    #     name her own proxy (never the generic orb).
    for d in _DIFFS:
        chest = LEINTH_CHESTS[d]
        if not db.has_record(chest):
            continue
        mesh = _v1(db, chest, 'mesh')
        if not isinstance(mesh, str) or 'leinth_chest' not in mesh.lower():
            problems.append("Leinth chest (%s) mesh = %r - her bespoke chest mesh "
                            "must survive the re-tier" % (d, mesh))
        desc = _v1(db, chest, 'description')
        if desc != 'tagLeinthChest':
            problems.append("Leinth chest (%s) description = %r, expected "
                            "tagLeinthChest (\"Leinth's Essense\")" % (d, desc))
        gold = _v1(db, chest, 'goldGenerator')
        if not isinstance(gold, str) or 'typhongoldgenerator' not in gold.lower():
            problems.append(
                "Leinth chest (%s) goldGenerator = %r - she must keep the RICHER "
                "typhongoldgenerator (x48/x64 vs bossgoldgenerator's x24/x32); "
                "switching her to the champions' generator is a gold NERF" % (d, gold))
    for rec in LEINTH_VARIANTS:
        if not db.has_record(rec):
            problems.append("Leinth variant MISSING: %s" % rec)
            continue
        tp = _v1(db, rec, _TREASURE)
        if not isinstance(tp, str) or 'bosschestproxy_leinth' not in tp.lower():
            problems.append(
                "%s treasureProxyName = %r - she keeps her OWN bespoke chest "
                "proxy; the re-tier happens inside her chain, never by repointing "
                "her at the generic orb" % (rec.rsplit('\\', 1)[-1], tp))

    # (h) THE NO-NERF PROOF, computed against her preserved ORIGINAL tables.
    for d in _DIFFS:
        problems.extend(_no_nerf_problems(db, CHAIN[d][5],
                                          LEINTH_TABLES_BY_DIFF[d], d))

    if problems:
        raise SystemExit(
            "[uber_apex_orb] R-70 VERIFY FAILED (one apex calibre for all three "
            "blood-cave bosses):\n  - " + "\n  - ".join(problems))
    print("  [uber_apex_orb] verify OK: both champions on genericbossorb_05 and "
          "Leinth's 3 chests on the SAME apex tables + level equation; chain "
          "resolves on n/e/l; all four calibre knobs >= her original chest; her "
          "bespoke mesh/name/gold generator intact and her variants still on her "
          "own proxy; no-nerf proof green on all 6 loot groups x 3 difficulties; "
          "genericbossorb_04 + its %d other consumers untouched; R-48 intact"
          % len(_orb04_consumers(db)))
