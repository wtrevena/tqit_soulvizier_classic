r"""red_uber_orbs - EVERY red uber drops the mystical orb, and a gate that says so.

WILL, VERBATIM (2026-08-10, ledgered R-200):

    "boar snatcher legendary spider should drop a mystical orb like the other red
     uber monsters"

===============================================================================
1. WHAT "THE MYSTICAL ORB" IS, AND WHAT WILL ACTUALLY SAW
===============================================================================
"Mystical orb" is Will's own name for the generic boss orb, and it is literal:
every `genericbossorb_0N` chest in this mod carries `description = tagEndChest02`,
and the base game's `Text_EN.arc` defines `tagEndChest02 = Mystical Orb`
(measured in the shipped base arc; the family siblings are `xtagChest17 = Hades'
Essence`, `xtagChest18 = Charon's Essence`, `tagEndChest01 = Typhon's Essence`).
b53 already settled that the generic orb - NOT a bespoke "X's Essence" - is the
mod convention (R-47), and `docs/reports/b53_orb_essence.md` predicted this exact
sentence: "the base game already ships tagEndChest02 = Mystical Orb - literally
his 'mystical orb'".

THE BOAR SNATCHER, IDENTIFIED FROM THE BYTES (not from the name in the report):
    display tag   tagAEMonsterName06 = "Boar Snatcher"   (base Text_EN, xmonsters.txt)
    records       records\creature\monster\spider\um_boareater_40.dbr  charLevel 15
                  records\creature\monster\spider\um_boareater_42.dbr  charLevel 17
                  records\creature\monster\spider\um_boareater_44.dbr  charLevel 19
    class         Monster.tpl, monsterClassification = Boss  -> a RED name
    folder        ...\monster\spider\  -> Will's "legendary spider" is exact
    placement     Greece/Area003/PineForest04 + Greece/MiniDungeons/SpartaOptCave03,
                  present in BASE and in our DEPLOYED map (docs/reports/el_boss_audit.md)
    orb           **NONE** - no `treasureProxyName` field at all, on any of the three

The record name says "boareater" and the DISPLAY name says "Boar Snatcher"; that
mismatch is why a name-based search for "boarsnatcher" finds nothing but the
monster is real. Resolve through the tag, never through the filename.

===============================================================================
2. THE CLASS - DERIVED, AND DERIVED OVER *MOD UNION BASE*
===============================================================================
    RED UBER  =  a `Monster.tpl` record, `monsterClassification == 'Boss'`
                 (the repo's own word for RED - `_amend_boss_loot_orbs` in the
                 monolith is documented as "Give red (Boss) custom bosses the
                 base-game on-death chest-orb the red act bosses drop"),
                 AND either
                   (a) basename starts with `um_`  - the uber-monster namespace
                       already used as THE uber roster by `uber_quest_drops`
                       (R-101 swept "all 611 ubers" on exactly this predicate), or
                   (b) it wears a `tagSVCMonster*` display tag - i.e. it is one of
                       OUR OWN authored uber bosses even when it kept a donor's
                       filename. Rule (b) adds exactly THREE records beyond rule
                       (a) - `boss_dagon_66`, `svc_um_hadesmarshal_80` and
                       `boss_satyrshaman_55` - and the first two were already on
                       orb04, so rule (b) earns its keep on ONE genuine miss:
                       Aithon, the Ember-Crowned (the b43 Olympian-Arena apex).

MEASURED over the runtime universe (base TQAE `database.arz` 74,013 records
overlaid by the built mod arz `SoulvizierClassic.arz` 51,204 records - 7,169
distinct Monster.tpl records; rank census Common 2368 / Champion 1580 / unset 1542
/ Hero 941 / Boss 458 / Quest 280):

    red ubers (the class above)            55
      already carrying a resolving orb     41
      MISSING one                          14   <- 8 fixed here, 6 EXEMPT (sec 4)

⚠️ THE SCOPE BOUNDARY, STATED HONESTLY SO NOBODY WIDENS IT BY ACCIDENT.
There are 458 Boss-class Monster.tpl records in the runtime universe and 346 of
them carry no `treasureProxyName`. This module does NOT touch the other 333: they
are the base game's own act/quest bosses (138 `boss_*`, 53 `x4_*` Eternal Embers,
30 `jinchan_*`, 12 `aesir_*`, the Ragnarok/Atlantis chains...), which pay out
through level-placed quest chests and their own bespoke proxies. Wiring an orb
onto all of them would rewrite the whole endgame economy - which is precisely the
fear R-99 opens with ("i didnt tell you to increase the drop of all the
champions"). The class Will named is the UBER class, and that is what is gated.
Residual registered as `BL-R200-DEBT-1`.

===============================================================================
3. WHY NO GATE CAUGHT THIS - TWO HOLES, BOTH CLOSED HERE
===============================================================================
HOLE 1 - THERE WAS NO ORB-BREADTH GATE AT ALL, ONLY HAND-TYPED LISTS.
Every orb wiring in the repo is a typed target list: `_BOSS_ORB_TARGETS` in
`apply_svc_patches._amend_boss_loot_orbs` (13 entries, its own comment scoping the
breadth to "all shipped custom Boss-class"), `general_guardians` (its 6 guards),
`polis_vault` / `diadochi` / `four_generals` / `devourer_kit` / `leinth_wave`
(their own bosses). The only orb GATES that existed are `uber_apex_orb.verify()`
- scoped to the 8-record Toxeus roster plus Leinth - and `general_guardians`'
own. Nothing anywhere asserted the CLASS invariant, so a red uber with no orb was
not a gate failure; it was invisible. R-99 already learned this lesson once, in
this exact domain, and wrote it down: a hand-typed list is how the Endless Hunt
shipped with no orb for two waves.

HOLE 2 - EVERY ROSTER DERIVATION IN THIS REPO RUNS OVER THE MOD DB ONLY.
This is the hole that actually hid the Boar Snatcher, and it would have survived a
naively-written class gate. `um_boareater_40/42/44` are BASE-GAME records that the
mod never overrides, so they are absent from the built arz - `toxeus_roster()`,
`uber_quest_drops.scan_uber_quest_leaks()`, `uber_quest_markers`' placed-member
roster and `_BOSS_ORB_TARGETS` alike can only ever see `db`. But the RUNTIME
resolution universe is mod UNION base (the model `_validate_container_loot_shapes`
and `fx_dangling_cleanup.verify()` already use), and the player fights whatever is
in that union. So this module's roster is derived over the UNION, and its gate
fails on a base-only red uber exactly as loudly as on one of ours.

The base arz is freed (`del base_db`, build_svc_database.py) long before the
registry runs, so this module loads it itself - 0.6s, cached for the module's
lifetime, resolved through `check_build_inputs` ('base_arz'), then `$SVC_BASE_ARZ`,
then the Steam default. apply() REQUIRES it (the Boar Snatcher cannot be imported
without it and silently skipping the fix Will asked for is not an option);
verify() DOWNGRADES loudly to mod-only if it is unreadable rather than skipping -
the `fx_dangling_cleanup` B-GATE-HARDEN-1 idiom, never a silent pass.

===============================================================================
4. THE 14 MISSES, AND WHY 6 OF THEM ARE CORRECTLY ORB-LESS
===============================================================================
FIXED (8) - record, charLevel[normal], tier, and why that tier:

  um_boareater_40      15   orb01   WILL'S REPORT. Boar Snatcher.
  um_boareater_42      17   orb01     "     (imported from base - sec 5)
  um_boareater_44      19   orb01     "
  um_neferkha_99       32   orb02   OURS (Neferkha, the Rimebound Pharaoh, Cold
                                    Tombs tier-1). His `actorToSpawnOnDeath`
                                    terminal `as_ghosthero_32` is SHARED with five
                                    roaming mummy heroes (the exclusivity fact
                                    `uber_quest_markers` rule B is built on), so
                                    the orb MUST sit on Neferkha himself - putting
                                    it on the terminal would hand an apex orb to
                                    every mummy hero on the map.
  um_frost_36          36   orb02   SV 0.98i red uber (FileDescription "Uber hero").
  um_phagia_44         44   orb03   SV 0.98i red uber whose LOWER twin
                                    `um_phagia_34` has been on orb02 all along -
                                    the same monster, one tier orb-less.
  boss_satyrshaman_55  55   orb04   OURS (Aithon, the Ember-Crowned, b43 arena
                                    apex, tagSVCMonsterAithon). Rule (b) catch.
                                    `bossarena.py` gave him a rich on-death
                                    EQUIPMENT table and a soul; the orb is a
                                    different field and was simply never wired.
  um_kravmoloch_99     74   orb04   OURS. Above every band -> the apex GENERIC
                                    tier. NOT orb05: R-99 reserves orb05 for the
                                    Toxeus roster and `uber_apex_orb.verify()`
                                    fails the build if any non-Toxeus record lands
                                    on it. This module asserts that too (sec 6 g).

EXEMPT (6) - pinned WITH the condition that earns the exemption, and every
condition is RE-PROVEN mechanically by verify() so a stale exemption reds the
build instead of rotting (the `uber_quest_markers._exempt_closure` discipline):

  TRANSFORM SHELLS (4). The encounter's TERMINAL form carries the orb, so the
  shell must not - otherwise the fight pays twice and drops an orb mid-transform.
  This is not invented here: `_amend_boss_loot_orbs` already scopes its own
  content-wave targets "terminal form only" and DEFENSIVELY CLEARS the Mnemophage
  shell (`_MN_ORB_SHELL`, "shell: stay orb-less").
      um_charon_ferryman_99  -> um_charonform2_ferryman_99  (bosschest02_charon)
      um_mnemophage_99       -> um_mnemophage_core_99       (genericbossorb_04)
      um_polisgaoler_99      -> um_polisgaoler_unbound_99   (genericbossorb_04)
      um_tantalus_99         -> um_tantalus_unbound_99      (genericbossorb_04)
  EXEMPTION CONDITION (asserted): the named terminal exists AND carries a
  treasureProxyName that RESOLVES. Strip the terminal's orb and this gate fires.

  SOUL-SUMMON COPIES (2), under `records\item\equipmentring\soul\test\`:
      um_bloodcrow_50.dbr  +  um_bloodcrow_50_l.dbr   (both dropItems = 0)
  These are the PLAYER'S summoned Bloodcrow, not an encounter - the FOUGHT
  `records\test\um_bloodcrow_50.dbr` is the one on orb04. A summon has no death
  loot to give. EXEMPTION CONDITION (asserted): `dropItems == 0`. Flip it to 1 and
  this gate fires, because then it would be claiming to be a dropper.

===============================================================================
5. HOW THE BOAR SNATCHER IS WIRED (the base-override mechanics)
===============================================================================
A mod `.arz` record REPLACES its base counterpart WHOLESALE - the engine does not
merge fields. So a stub record carrying only `treasureProxyName` would delete the
spider's kit, mesh, controller and stats. The three records are therefore IMPORTED
FIELD-FOR-FIELD from the base arz first (the proven
`build_svc_database.import_base_game_bosses` / `_import_base_game_record` idiom:
`_ensure_record` with the donor's own `templateName`, then every field copied with
its OWN dtype), and only then does the orb field get added. apply() PROVES the
import: after the write, each imported record must equal its base original on
EVERY field except the single added `treasureProxyName` - measured, not asserted.

`treasureProxyName` is ABSENT (not blank) on all 8 targets, so every write ADDS
the field as `DATA_TYPE_STRING` (the `_amend_boss_loot_orbs` idiom). No explicit
dtype is ever passed to a field that already exists (CLAUDE.md's dtype trap).

===============================================================================
6. THE TIER LADDER - MEASURED, AND THE PIN IS CROSS-CHECKED AGAINST IT
===============================================================================
The five generic tiers differ ONLY in their loot table + level equation; all five
share the same `DRX\meshes\bossorbmesh.msh`, scale 0.7 and `tagEndChest02` name,
so every one of them IS "the mystical orb" and this change adds no new look.
Measured consumer bands (charLevel[normal] of each tier's pre-existing consumers):

    tier    loot table                    level eq   band     example consumers
    orb01   uberorb_default_13-15         a04        16-20    Mormo, Elephant Snatcher,
                                                              Rakanizeus, Melalos, Calybe
    orb02   uberorb_default_19-21         b03        33-35    Grimshell, Phagia(34), Permean
    orb03   uberorb_default_29-31         c03        42-48    Inkeyes, Uber, Palai, Xaiweng,
                                                              the 6 General's Guardians
    orb04   xpack uberorb_default_n01c    _all       38-58    the whole custom apex roster
    orb05   svc_uberorb_apex_n01c         _all       RESERVED (R-99, Toxeus only)

TIER RULE (mechanical, and it reproduces all 8 pins with no special-casing):
    the tier whose band is at MINIMUM DISTANCE from the record's charLevel[0],
    orb05 excluded, ties broken toward the LOWER tier.
`verify()` recomputes the bands from the FINAL db (excluding this module's own
targets, so the bands stay the pre-existing ones and the check is stable) and
fails if any pin stops being the minimum-distance tier. That makes the pins
evidence, not taste, and tells a future lane which tier a new uber belongs on.

BLAST RADIUS: this module only ADDS consumers to shared tiers; it never edits an
orb, a pool, a chest or a loot table, and it never removes a consumer.
`uber_apex_orb.DONOR_TIER_FLOORS` is explicitly a FLOOR ("a later lane may
legitimately ADD a consumer to a generic tier"), so orb01's 10 and orb04's 19 are
unaffected. orb05 is untouched, which keeps `uber_apex_orb.verify()`'s "the set of
orb05 carriers is EXACTLY the Toxeus roster" assertion green.

===============================================================================
7. THE GATE (process law #4: a new content class ships its gate)
===============================================================================
`verify()` runs in registry step 4 over the FINAL merged db (union base) and fails
the build loud unless ALL of:
  (a) every RED UBER either carries a treasureProxyName that RESOLVES in mod UNION
      base, or is in EXEMPT;
  (b) every EXEMPT entry still EXISTS and is still IN the roster (no stale
      exemption) and its stated condition still holds (shell: the named terminal
      resolves and carries a resolving orb; summon: dropItems == 0);
  (c) all 8 wired targets carry EXACTLY their pinned tier;
  (d) the 3 imported Boar Snatcher records exist in the MOD db (the override
      landed) and still read `monsterClassification = Boss`;
  (e) every pinned tier still exists and its whole 3-difficulty chain
      (proxy -> accessory pool -> chest -> loot table) resolves;
  (f) each pin is still the minimum-distance tier for its charLevel (sec 6);
  (g) NOTHING this module wired sits on orb05 (R-99's reserved Toxeus apex).

Planted negatives (`py tools/patches/red_uber_orbs.py --negtest <built.arz>`):
  N1 a wired target's orb removed                          -> must FAIL
  N2 a red uber's orb pointed at a non-existent record     -> must FAIL (resolution)
  N3 a NEW red uber planted with no orb                    -> must FAIL (THE class
     half - this is the Boar Snatcher regression itself)
  N4 a shell's TERMINAL stripped of its orb                -> must FAIL. NOTE,
     measured: for all four shipped shells the terminal is ITSELF a red uber, so
     check (a) fires first and (b) is belt-and-braces; (b) is the one that catches
     a terminal OUTSIDE the class, which is the shape a future transform could take.
  N5 a summon exemption flipped to dropItems = 1           -> must FAIL
  N6 a stale exemption naming a non-roster record          -> must FAIL
  N7 a pin moved to a tier that is not minimum-distance    -> must FAIL (planted on
     BOTH the pin and the record, so check (c) agrees with itself and only the
     ladder rule (f) can fire)
  N8 a `um_*` HERO-rank record with no orb                 -> must stay GREEN
     (scope proof: the gate is RED-only; it does not demand an orb from the 412
     Hero-rank ubers, and a lane that widened it there would be inventing policy)
  N9 the untouched control                                 -> must PASS

Read-only audit of any arz:  py tools/patches/red_uber_orbs.py --analyze <arz>
Contract (tools/patches/README.md): MODULE_NAME + apply(db, tags) + verify(db, tags).
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from arz_patcher import DATA_TYPE_STRING

MODULE_NAME = ("red uber orbs - the Boar Snatcher's mystical orb + the "
               "red-uber orb-breadth class gate (R-200)")

# ── the class predicate ──────────────────────────────────────────────────────
_MONSTER_TPL = 'templates\\monster.tpl'
_RED_RANK = 'boss'
_UBER_TOKEN = 'um_'            # rule (a): the uber-monster namespace
_OURS_TAG_PREFIX = 'tagsvcmonster'   # rule (b): our own authored uber bosses

_TREASURE = 'treasureProxyName'

# ── the orb ladder ───────────────────────────────────────────────────────────
_NEW = 'records\\item\\containers\\new\\'
ORB01 = _NEW + 'genericbossorb_01.dbr'
ORB02 = _NEW + 'genericbossorb_02.dbr'
ORB03 = _NEW + 'genericbossorb_03.dbr'
ORB04 = _NEW + 'genericbossorb_04.dbr'
ORB05 = _NEW + 'genericbossorb_05.dbr'          # R-99 RESERVED - never wired here

# The tiers this module is allowed to choose from, in ascending order. orb05 is
# deliberately absent: it is the Toxeus apex and uber_apex_orb.verify() fails the
# build if a non-Toxeus record lands on it.
LADDER = (ORB01, ORB02, ORB03, ORB04)

_DIFF_FIELDS = (('accessory1', 'normal'),
                ('accessoryEpic1', 'epic'),
                ('accessoryLegendary1', 'legendary'))

# ── THE BOAR SNATCHER (base-only; imported before it can be wired) ───────────
_SPIDER = 'records\\creature\\monster\\spider\\'
BOAR_SNATCHER = (
    _SPIDER + 'um_boareater_40.dbr',
    _SPIDER + 'um_boareater_42.dbr',
    _SPIDER + 'um_boareater_44.dbr',
)
BOAR_SNATCHER_TAG = 'tagAEMonsterName06'        # base Text_EN: "Boar Snatcher"

# Records this module must IMPORT from the base arz before writing (they do not
# exist in the mod overlay at all). Full field-for-field copy - a partial overlay
# record would REPLACE the base record and delete the monster's kit.
IMPORT_FROM_BASE = BOAR_SNATCHER

# ── THE WIRE SET: record -> (tier, charLevel[normal] measured, why) ──────────
WIRE = {
    BOAR_SNATCHER[0]: (ORB01, 15, "Boar Snatcher (tagAEMonsterName06) - WILL'S REPORT R-200"),
    BOAR_SNATCHER[1]: (ORB01, 17, "Boar Snatcher - WILL'S REPORT R-200"),
    BOAR_SNATCHER[2]: (ORB01, 19, "Boar Snatcher - WILL'S REPORT R-200"),
    r'records\creature\monster\neferkha\um_neferkha_99.dbr':
        (ORB02, 32, "OURS: Neferkha, the Rimebound Pharaoh - terminal as_ghosthero_32 "
                    "is SHARED with 5 mummy heroes, so the orb rides the uber himself"),
    r'records\creature\monster\limos\um_frost_36.dbr':
        (ORB02, 36, "SV 0.98i red uber (FileDescription 'Uber hero')"),
    r'records\creature\monster\human\um_phagia_44.dbr':
        (ORB03, 44, "SV 0.98i red uber whose lower twin um_phagia_34 was on orb02 already"),
    r'records\creature\monster\bossarena\boss_satyrshaman_55.dbr':
        (ORB04, 55, "OURS: Aithon, the Ember-Crowned (b43 arena apex) - the rule-(b) catch"),
    r'records\creature\monster\skeleton\um_kravmoloch_99.dbr':
        (ORB04, 74, "OURS: above every band -> the apex GENERIC tier (orb05 is R-99 reserved)"),
}

# ── THE EXEMPT SET: record -> (kind, payload, why) ──────────────────────────
# 'shell'  payload = the terminal form that MUST carry a resolving orb
# 'summon' payload = None; the condition is dropItems == 0
EXEMPT = {
    r'records\xpack\creatures\monster\bosses\02_charon\um_charon_ferryman_99.dbr':
        ('shell', r'records\xpack\creatures\monster\bosses\02_charon\um_charonform2_ferryman_99.dbr',
         # Will 2026-08-11: this record is no longer Charon. `tools/patches/
         # charon_rework.py` rewrites it IN PLACE as ORMENOS, THE GILDED ROOT
         # (the record PATH is frozen because build_section_surgery places the
         # forecourt proxy by name, and three gates key on the basename). The
         # exemption is unchanged in kind - it is still a transform shell whose
         # terminal carries the orb - but the reason the terminal carries
         # bosschest02_charon changed: the hellflower donor inherits NO
         # treasureProxyName, so charon_rework SETS it explicitly. That is not
         # cosmetic: svc_orb_breadth derives its scope as "every proxy an UBER
         # names" and enforces MIN_PROXIES=6 / MIN_TABLES=18, and this terminal
         # is the ONLY uber naming that proxy, so retargeting it (the b53/Dagon
         # treatment the lore wants) would drop the scope to 5/15 and red
         # orb_loot_breadth. Registered as BL-BOUGH-DEBT-4.
         "transform shell - the terminal (Ormenos, the Bough in Bloom) carries "
         "bosschest02_charon"),
    r'records\xpack\creatures\monster\epiales\um_mnemophage_99.dbr':
        ('shell', r'records\xpack\creatures\monster\epiales\um_mnemophage_core_99.dbr',
         "transform shell - _amend_boss_loot_orbs DEFENSIVELY CLEARS this one "
         "(_MN_ORB_SHELL, 'shell: stay orb-less'); the Core carries orb04"),
    r'records\xpack\creatures\monster\gigantes\um_polisgaoler_99.dbr':
        ('shell', r'records\xpack\creatures\monster\gigantes\um_polisgaoler_unbound_99.dbr',
         "transform shell - the Unbound Gaoler carries orb04"),
    r'records\xpack\creatures\monster\lostsoul\um_tantalus_99.dbr':
        ('shell', r'records\xpack\creatures\monster\lostsoul\um_tantalus_unbound_99.dbr',
         "transform shell - Tantalus Unbound carries orb04"),
    r'records\item\equipmentring\soul\test\um_bloodcrow_50.dbr':
        ('summon', None,
         "the PLAYER'S summoned Bloodcrow (dropItems 0); the FOUGHT "
         r"records\test\um_bloodcrow_50.dbr is the one on orb04"),
    r'records\item\equipmentring\soul\test\um_bloodcrow_50_l.dbr':
        ('summon', None,
         "the PLAYER'S summoned Bloodcrow, Legendary copy (dropItems 0)"),
}

# populated by apply(); read by verify() so the base arz is loaded at most once.
_BASE_ROWS = None
_BASE_STATE = 'unloaded'        # 'ok' | 'missing' | 'unloaded'

_BASE_FIELDS_WANTED = ('templateName', 'monsterClassification', 'charLevel',
                       _TREASURE, 'description', 'dropItems')


# ── small readers ───────────────────────────────────────────────────────────
def _norm(p):
    return str(p).replace('/', '\\').lower()


def _v1(db, rec, field):
    v = db.get_field_value(rec, field)
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _fields(db, rec):
    """{base_field_name: (values, dtype)} for a record (### suffixes collapsed)."""
    out = {}
    ff = db.get_fields(rec)
    if not ff:
        return out
    for k, tf in ff.items():
        out.setdefault(k.split('###')[0], (list(tf.values), tf.dtype))
    return out


_NAME_INDEX = {}          # id(db) -> ({norm: realkey}, record_count)


def _index(db):
    """{norm(record): real key} for `db`, rebuilt whenever the record count moves.

    A linear `record_names()` scan per lookup is 51k comparisons and this module
    resolves hundreds of refs (every orb chain link, every exemption terminal),
    so the index is what keeps both the build and --negtest cheap. Keyed on the
    record COUNT so a module that adds records (including this one) invalidates it.
    """
    cached = _NAME_INDEX.get(id(db))
    n = len(db._raw_records)
    if cached is None or cached[1] != n:
        cached = ({_norm(k): k for k in db.record_names()}, n)
        _NAME_INDEX[id(db)] = cached
    return cached[0]


def _resolve(db, path):
    """The real key matching `path`, tolerating '/'-vs-'\\' and case."""
    if db.has_record(path):
        return path
    return _index(db).get(_norm(path))


def _level(v):
    """charLevel[normal] as an int, or None."""
    if isinstance(v, list):
        v = v[0] if v else None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


# ── the base-game half of the runtime universe ──────────────────────────────
def _base_arz_path():
    """Resolve the base TQAE database.arz: check_build_inputs -> $SVC_BASE_ARZ ->
    the Steam default. Returns a Path or None."""
    env = os.environ.get('SVC_BASE_ARZ', '').strip()
    cands = []
    try:
        import check_build_inputs as cbi
        try:
            cands.append(cbi.resolve('base_arz', given=(env or None), verbose=False))
        except Exception:                       # noqa: BLE001 - fall through, never mask
            pass
    except ImportError:
        pass
    if env:
        cands.append(Path(env))
    cands.append(Path(r'C:\Program Files (x86)\Steam\steamapps\common'
                      r'\Titan Quest Anniversary Edition\Database\database.arz'))
    for c in cands:
        try:
            if c is not None and Path(c).is_file():
                return Path(c)
        except OSError:
            continue
    return None


def load_base_rows(required, who):
    """{norm(record): {field: value}} for every base-game Monster.tpl record.

    Cached for the module's lifetime (apply() loads it, verify() reuses it).
    `required=True` fails the build loud when the base arz cannot be read.
    """
    global _BASE_ROWS, _BASE_STATE
    if _BASE_STATE != 'unloaded':
        if _BASE_STATE == 'missing' and required:
            raise SystemExit(
                "[red_uber_orbs] %s NEEDS the base-game database.arz and it is "
                "unreadable. The Boar Snatcher (um_boareater_40/42/44) exists ONLY "
                "in the base game, so without it R-200's fix cannot be written at "
                "all - and shipping a build that silently drops the fix Will asked "
                "for is not an option. Set SVC_BASE_ARZ or pass the base arz as "
                "the 5th build argument." % who)
        return _BASE_ROWS
    path = _base_arz_path()
    if path is None:
        _BASE_STATE, _BASE_ROWS = 'missing', {}
        if required:
            return load_base_rows(True, who)     # re-enter -> raises above
        print("  [red_uber_orbs] WARNING base-game database.arz not found; the "
              "red-uber roster runs MOD-ONLY this build (a base-only red uber "
              "cannot be checked). No silent pass: this line IS the downgrade.")
        return _BASE_ROWS
    from arz_patcher import ArzDatabase
    bdb = ArzDatabase.from_arz(path)
    # `_all` (the FULL field map, needed to import a record) is kept ONLY for the
    # handful of records this module actually imports. Keeping it for all ~5.5k
    # base Monster records would hold a second full field graph in memory for the
    # rest of a build that already carries several 50k-record databases.
    want_all = {_norm(p) for p in IMPORT_FROM_BASE}
    rows = {}
    for n in bdb.record_names():
        tpl = _v1(bdb, n, 'templateName')
        if not (isinstance(tpl, str) and _norm(tpl).endswith(_MONSTER_TPL)):
            continue
        key = _norm(n)
        row = {f: _v1(bdb, n, f) for f in _BASE_FIELDS_WANTED}
        row['_name'] = n
        row['_all'] = _fields(bdb, n) if key in want_all else None
        rows[key] = row
    _BASE_ROWS, _BASE_STATE = rows, 'ok'
    print("  [red_uber_orbs] base-game universe loaded: %d Monster.tpl record(s) "
          "from %s" % (len(rows), path))
    return _BASE_ROWS


# ── THE ROSTER (derived over mod UNION base) ────────────────────────────────
def red_uber_roster(db, base_rows):
    """{norm(record): row} for every RED UBER in the runtime universe.

    row = {'name', 'src' ('MOD'|'BASE'), 'rank', 'level', 'orb', 'desc', 'drop'}
    The mod overlay WINS on any record present in both (that is the engine's own
    resolution order, and it is why an imported+wired Boar Snatcher reads as MOD).
    """
    out = {}

    def _consider(name, rank, level, orb, desc, drop, src):
        if str(rank or '').strip().lower() != _RED_RANK:
            return
        base = _norm(name).rsplit('\\', 1)[-1]
        ours = str(desc or '').lower().startswith(_OURS_TAG_PREFIX)
        if not (base.startswith(_UBER_TOKEN) or ours):
            return
        out[_norm(name)] = {'name': name, 'src': src, 'rank': rank,
                            'level': _level(level), 'orb': orb, 'desc': desc,
                            'drop': drop, 'rule': 'a' if base.startswith(_UBER_TOKEN) else 'b'}

    for key, row in (base_rows or {}).items():
        _consider(row['_name'], row['monsterClassification'], row['charLevel'],
                  row[_TREASURE], row['description'], row['dropItems'], 'BASE')
    for n in db.record_names():
        tpl = _v1(db, n, 'templateName')
        if not (isinstance(tpl, str) and _norm(tpl).endswith(_MONSTER_TPL)):
            continue
        _consider(n, _v1(db, n, 'monsterClassification'), _v1(db, n, 'charLevel'),
                  _v1(db, n, _TREASURE), _v1(db, n, 'description'),
                  _v1(db, n, 'dropItems'), 'MOD')
    return out


def _resolves(db, base_rows, ref):
    """Does `ref` name a record that exists in the runtime universe (mod|base)?"""
    if not isinstance(ref, str) or not ref.strip():
        return False
    key = _norm(ref)
    if _resolve(db, ref) is not None:
        return True
    return key in (base_rows or {})


def _tier_bands(db, exclude):
    """{tier: (lo, hi)} charLevel band of each ladder tier's consumers, EXCLUDING
    `exclude` (this module's own targets) so the bands stay the pre-existing ones.
    A tier with no other consumer is reported as None and skipped by the rule."""
    bands = {}
    ex = {_norm(e) for e in exclude}
    for orb in LADDER:
        low = _norm(orb)
        levels = []
        for n in db.record_names():
            if _norm(n) in ex:
                continue
            t = _v1(db, n, _TREASURE)
            if isinstance(t, str) and _norm(t) == low:
                lv = _level(_v1(db, n, 'charLevel'))
                if lv is not None:
                    levels.append(lv)
        bands[orb] = (min(levels), max(levels)) if levels else None
    return bands


def _tier_for(level, bands):
    """The minimum-distance tier for `level`; ties break toward the LOWER tier."""
    best, best_d = None, None
    for orb in LADDER:                       # ascending -> first wins a tie
        band = bands.get(orb)
        if band is None:
            continue
        lo, hi = band
        d = 0 if lo <= level <= hi else (lo - level if level < lo else level - hi)
        if best_d is None or d < best_d:
            best, best_d = orb, d
    return best


# ── apply ───────────────────────────────────────────────────────────────────
def _import_base_record(db, base_rows, path):
    """Copy a base-game record into the overlay field-for-field, dtype-exact.
    Mirrors build_svc_database.import_base_game_bosses."""
    from apply_svc_patches import _ensure_record
    row = (base_rows or {}).get(_norm(path))
    if row is None:
        raise SystemExit(
            "[red_uber_orbs] base record MISSING from the base-game arz: %s. "
            "R-200 names the Boar Snatcher explicitly; it cannot be wired if the "
            "record is not there." % path)
    allf = row['_all']
    if not allf:
        raise SystemExit(
            "[red_uber_orbs] %s has no cached field map. Only records listed in "
            "IMPORT_FROM_BASE keep one (a memory choice); adding an import target "
            "means adding it there too." % path)
    tpl = allf.get('templateName', ([''], None))[0]
    tpl = tpl[0] if tpl else ''
    _ensure_record(db, path, str(tpl))
    for fname, (vals, dtype) in allf.items():
        if not vals:
            continue
        db.set_field(path, fname, vals[0] if len(vals) == 1 else list(vals), dtype)
    db._modified.add(path)
    return allf


def apply(db, tags):
    print("\n=== patches-registry: %s ===" % MODULE_NAME)
    base_rows = load_base_rows(required=True, who='apply()')

    # ── 1. import the base-only records (the Boar Snatcher) ─────────────────
    imported = {}
    for path in IMPORT_FROM_BASE:
        if _resolve(db, path) is not None:
            raise SystemExit(
                "[red_uber_orbs] %s ALREADY exists in the mod overlay. This module "
                "expects to be the record's first author (measured: absent on "
                "main). Another lane now owns it - make the ordering explicit and "
                "re-measure before overwriting." % path)
        imported[path] = _import_base_record(db, base_rows, path)
    print("  imported %d base-only record(s) into the overlay (field-for-field, "
          "dtype-exact): %s"
          % (len(imported), ", ".join(p.rsplit('\\', 1)[-1] for p in IMPORT_FROM_BASE)))

    # ── 2. scope snapshot: every record's treasureProxyName BEFORE ──────────
    before = {}
    for n in db.record_names():
        t = _v1(db, n, _TREASURE)
        if t is not None:
            before[_norm(n)] = _norm(t)

    # ── 3. wire the orbs ────────────────────────────────────────────────────
    for path, (orb, level, why) in sorted(WIRE.items()):
        real = _resolve(db, path)
        if real is None:
            raise SystemExit(
                "[red_uber_orbs] target MISSING from the db: %s (%s). Every target "
                "was measured present on main; a rename or a deletion must be a "
                "human decision, not a silent skip." % (path, why))
        if _resolve(db, orb) is None:
            raise SystemExit(
                "[red_uber_orbs] orb tier MISSING: %s (needed by %s)" % (orb, path))
        cur = _v1(db, real, _TREASURE)
        if cur is None:
            db.set_field(real, _TREASURE, orb, DATA_TYPE_STRING)   # ADD the field
        else:
            db.set_field(real, _TREASURE, orb)                     # never re-dtype
        got = _level(_v1(db, real, 'charLevel'))
        if got != level:
            raise SystemExit(
                "[red_uber_orbs] %s charLevel is %r, the pinned tier was chosen "
                "against %r. The ladder pin is evidence, not taste - re-measure "
                "before shipping." % (path, got, level))
        print("    %-56s lvl %-3s -> %-20s  %s"
              % (real.rsplit('\\', 1)[-1], level, orb.rsplit('\\', 1)[-1], why))

    # ── 4. SCOPE PROOF: exactly the WIRE set changed, nothing else ──────────
    after = {}
    for n in db.record_names():
        t = _v1(db, n, _TREASURE)
        if t is not None:
            after[_norm(n)] = _norm(t)
    moved = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
    want = {_norm(p) for p in WIRE}
    if moved != want:
        raise SystemExit(
            "[red_uber_orbs] SCOPE PROOF FAILED: treasureProxyName changed on %s, "
            "expected exactly %s (unintended: %s; missed: %s)"
            % (sorted(moved), sorted(want), sorted(moved - want), sorted(want - moved)))

    # ── 5. IMPORT PROOF: each imported record == base, except the added orb ─
    for path, allf in imported.items():
        real = _resolve(db, path)
        now = _fields(db, real)
        diffs = []
        for f in set(allf) | set(now):
            if f == _TREASURE:
                continue
            a = allf.get(f, ([], None))[0]
            b = now.get(f, ([], None))[0]
            if list(a) != list(b):
                diffs.append(f)
        if diffs:
            raise SystemExit(
                "[red_uber_orbs] IMPORT PROOF FAILED on %s: %d field(s) differ from "
                "the base original beyond the added orb: %s. A mod record REPLACES "
                "its base counterpart wholesale, so any drift here is a live "
                "regression on the monster itself." % (path, len(diffs), sorted(diffs)[:12]))
        if _norm(now.get(_TREASURE, ([''], None))[0][0]) != _norm(WIRE[path][0]):
            raise SystemExit(
                "[red_uber_orbs] IMPORT PROOF FAILED on %s: the orb field did not "
                "land." % path)
    print("  scope proof: exactly %d record(s) changed treasureProxyName; the %d "
          "imported record(s) are field-identical to their base originals except "
          "the added orb." % (len(moved), len(imported)))

    # ── 6. the class audit, printed so the wave report is the build log ────
    roster = red_uber_roster(db, base_rows)
    missing = [r for k, r in sorted(roster.items())
               if not r['orb'] and k not in {_norm(e) for e in EXEMPT}]
    print("  RED UBER class after this module: %d record(s); %d exempt "
          "(%d transform shells + %d soul-summon copies); %d still orb-less"
          % (len(roster), len(EXEMPT),
             sum(1 for v in EXEMPT.values() if v[0] == 'shell'),
             sum(1 for v in EXEMPT.values() if v[0] == 'summon'), len(missing)))
    if missing:
        print("    STILL ORB-LESS (verify() will red the build): %s"
              % [r['name'] for r in missing])


# ── verify: THE GATE ────────────────────────────────────────────────────────
def verify(db, tags):
    base_rows = load_base_rows(required=False, who='verify()')
    problems = []
    roster = red_uber_roster(db, base_rows)
    exempt_low = {_norm(e) for e in EXEMPT}

    # (a) every red uber carries a RESOLVING orb, or is exempt
    for key, row in sorted(roster.items()):
        if key in exempt_low:
            continue
        orb = row['orb']
        if not orb:
            problems.append(
                "RED UBER WITH NO ORB: %s (%s, rank %s, charLevel %s, rule %s). "
                "R-200: every red uber drops the mystical orb. Either wire it in "
                "WIRE (tier = the minimum-distance band, sec 6) or, if it is a "
                "transform shell or a summon copy, add it to EXEMPT WITH the "
                "condition that earns the exemption written down."
                % (row['name'], row['src'], row['rank'], row['level'], row['rule']))
        elif not _resolves(db, base_rows, orb):
            problems.append(
                "RED UBER WITH A DANGLING ORB: %s -> %r does not resolve in mod "
                "UNION base; the drop would silently yield nothing."
                % (row['name'], orb))

    # (b) no stale exemption, and every exemption condition still holds
    for path, (kind, payload, why) in sorted(EXEMPT.items()):
        key = _norm(path)
        if key not in roster:
            problems.append(
                "STALE EXEMPTION: %s is no longer a RED UBER (renamed, deleted or "
                "declassed), so the exemption is dead config. Remove it or fix the "
                "record. (%s)" % (path, why))
            continue
        if kind == 'shell':
            term = _resolve(db, payload)
            if term is None:
                problems.append(
                    "SHELL EXEMPTION BROKEN: %s is exempt because its terminal form "
                    "%s carries the orb, but that terminal is GONE." % (path, payload))
                continue
            torb = _v1(db, term, _TREASURE)
            if not _resolves(db, base_rows, torb):
                problems.append(
                    "SHELL EXEMPTION BROKEN: %s is exempt only because %s carries a "
                    "resolving orb - it now reads %r, so the WHOLE encounter drops no "
                    "orb." % (path, payload, torb))
        elif kind == 'summon':
            real = _resolve(db, path)
            drop = _level(_v1(db, real, 'dropItems')) if real else None
            if drop not in (0, None) and drop != 0:
                problems.append(
                    "SUMMON EXEMPTION BROKEN: %s is exempt as the player's SUMMONED "
                    "copy (dropItems 0) but now reads dropItems=%r - it is claiming "
                    "to be a dropper, so it must carry an orb or stop dropping."
                    % (path, drop))
        else:
            problems.append("EXEMPT entry %s has unknown kind %r" % (path, kind))

    # (c) every wired target carries EXACTLY its pinned tier
    for path, (orb, level, why) in sorted(WIRE.items()):
        real = _resolve(db, path)
        if real is None:
            problems.append("wired target MISSING from the final db: %s" % path)
            continue
        got = _v1(db, real, _TREASURE)
        if not isinstance(got, str) or _norm(got) != _norm(orb):
            problems.append(
                "%s treasureProxyName = %r, expected %s (R-200 pin: %s)"
                % (path, got, orb, why))

    # (d) the Boar Snatcher override actually landed in the MOD db
    for path in BOAR_SNATCHER:
        real = _resolve(db, path)
        if real is None:
            problems.append(
                "BOAR SNATCHER MISSING from the mod overlay: %s. The base record is "
                "only overridden if we ship our own copy - without it R-200 does "
                "nothing in game." % path)
            continue
        rank = str(_v1(db, real, 'monsterClassification') or '').lower()
        if rank != _RED_RANK:
            problems.append(
                "%s monsterClassification = %r, expected 'Boss' - the import must "
                "not have changed what the monster IS." % (path, rank))
        desc = _v1(db, real, 'description')
        if desc != BOAR_SNATCHER_TAG:
            problems.append(
                "%s description = %r, expected %s ('Boar Snatcher') - the import "
                "copied the wrong record." % (path, desc, BOAR_SNATCHER_TAG))

    # (e) every pinned tier's 3-difficulty chain resolves end to end
    for orb in sorted({w[0] for w in WIRE.values()}):
        real = _resolve(db, orb)
        if real is None:
            problems.append("orb tier %s is GONE from the db" % orb)
            continue
        for field, label in _DIFF_FIELDS:
            pool = _v1(db, real, field)
            p = _resolve(db, pool) if isinstance(pool, str) else None
            if p is None:
                problems.append("%s.%s (%s) does not resolve: %r"
                                % (orb, field, label, pool))
                continue
            chest = _v1(db, p, 'fixedItemName1')
            c = _resolve(db, chest) if isinstance(chest, str) else None
            if c is None:
                problems.append("%s -> %s.fixedItemName1 does not resolve: %r"
                                % (orb, pool, chest))
                continue
            table = _v1(db, c, 'tables')
            if not _resolves(db, base_rows, table):
                problems.append("%s -> %s.tables does not resolve: %r"
                                % (orb, chest, table))

    # (f) each pin is still the minimum-distance tier for its charLevel
    bands = _tier_bands(db, exclude=WIRE.keys())
    for path, (orb, level, why) in sorted(WIRE.items()):
        want = _tier_for(level, bands)
        if want is not None and _norm(want) != _norm(orb):
            problems.append(
                "TIER PIN NO LONGER MINIMAL: %s (charLevel %d) is pinned to %s but "
                "the measured bands %s now put it on %s. The ladder moved - re-pin "
                "it deliberately, do not let the pin rot."
                % (path, level, orb.rsplit('\\', 1)[-1],
                   {k.rsplit('\\', 1)[-1]: v for k, v in bands.items()},
                   want.rsplit('\\', 1)[-1]))

    # (g) nothing this module wired sits on R-99's reserved Toxeus apex
    for path, (orb, _l, _w) in sorted(WIRE.items()):
        if _norm(orb) == _norm(ORB05):
            problems.append(
                "%s is wired to genericbossorb_05, which R-99 RESERVES for the "
                "Toxeus roster - uber_apex_orb.verify() fails the build on any "
                "non-Toxeus carrier." % path)

    if problems:
        raise SystemExit(
            "[red_uber_orbs] R-200 RED-UBER ORB GATE FAILED (%d):\n  - %s"
            % (len(problems), "\n  - ".join(problems)))

    orbless = sum(1 for k, r in roster.items()
                  if not r['orb'] and k not in exempt_low)
    print("  red-uber orb gate PASS: %d red uber(s) in the runtime universe "
          "(%s), %d wired by this module, %d exempt with their conditions re-proven, "
          "%d orb-less."
          % (len(roster),
             'mod UNION base' if _BASE_STATE == 'ok' else 'MOD-ONLY - base arz unreadable',
             len(WIRE), len(EXEMPT), orbless))


# ── CLI: --analyze / --negtest ──────────────────────────────────────────────
def _load(arz):
    from arz_patcher import ArzDatabase
    return ArzDatabase.from_arz(Path(arz))


def _analyze(arz):
    db = _load(arz)
    base_rows = load_base_rows(required=False, who='--analyze')
    roster = red_uber_roster(db, base_rows)
    exempt_low = {_norm(e) for e in EXEMPT}
    print("\nRED UBER roster (mod UNION base): %d" % len(roster))
    print("%-74s %-5s %-5s %-6s %s" % ('record', 'src', 'rule', 'lvl', 'orb'))
    for key, r in sorted(roster.items(), key=lambda kv: (kv[1]['level'] or 0, kv[0])):
        mark = '  EXEMPT' if key in exempt_low else ('' if r['orb'] else '  ** NO ORB **')
        print("%-74s %-5s %-5s %-6s %s%s"
              % (r['name'], r['src'], r['rule'], r['level'],
                 (str(r['orb']).rsplit('\\', 1)[-1] if r['orb'] else '-'), mark))
    bands = _tier_bands(db, exclude=WIRE.keys())
    print("\nmeasured tier bands (excluding this module's targets):")
    for orb in LADDER:
        print("  %-24s %s" % (orb.rsplit('\\', 1)[-1], bands.get(orb)))


def _snapshot_field(db, rec, field):
    """[(key, values-copy, dtype)] for every slot of `field` on `rec`.

    The VALUES ARE COPIED, not the TypedField: `ArzDatabase.set_field` mutates
    `tf.values` IN PLACE, so holding the object would hand the undo the mutated
    state and the negative would leak into every later case (measured - it did).
    """
    ff = db.get_fields(rec) or {}
    return [(k, list(ff[k].values), ff[k].dtype)
            for k in list(ff) if k.split('###')[0] == field]


def _restore_field(db, rec, field, saved):
    """Put `field` back exactly as `_snapshot_field` found it (absent stays absent)."""
    ff = db.get_fields(rec) or {}
    from arz_patcher import TypedField
    for k in [k for k in list(ff) if k.split('###')[0] == field]:
        del ff[k]
    for k, vals, dtype in saved:
        ff[k] = TypedField(dtype, list(vals))


def _del_field(db, rec, field):
    """Delete `field` from `rec` entirely (never blank it - field-absence parity).
    Returns an undo callable."""
    real = _resolve(db, rec)
    saved = _snapshot_field(db, real, field)
    ff = db.get_fields(real) or {}
    for k, _v, _d in saved:
        del ff[k]
    db._modified.add(real)
    return lambda: _restore_field(db, real, field, saved)


def _set_field(db, rec, field, value):
    """set_field with an undo callable that restores the exact prior value."""
    real = _resolve(db, rec)
    saved = _snapshot_field(db, real, field)
    db.set_field(real, field, value)
    return lambda: _restore_field(db, real, field, saved)


def _drop_record(db, path):
    """Remove a planted record cleanly (undo for a planted clone)."""
    for store in ('_raw_records', '_record_types', '_record_timestamps', '_decoded_cache'):
        d = getattr(db, store, None)
        if isinstance(d, dict):
            d.pop(path, None)
    db._modified.discard(path)


def _negtest(arz):
    """Plant negatives against a REAL built arz.

    ONE db is loaded and apply()'d, then each negative is planted, verified and
    UNDONE. Reloading the arz per case would re-decode 51,204 records nine times;
    the undo path keeps the whole battery to a single decode pass while still
    running every case against the real, fully-applied build state.
    """
    db = _load(arz)
    apply(db, {})

    def run(label, mutate, must_fail=True):
        undo = mutate(db) if mutate is not None else (lambda: None)
        try:
            verify(db, {})
            ok, got = (not must_fail), 'PASS'
        except SystemExit as exc:
            first = [ln.strip() for ln in str(exc).splitlines() if ln.strip()]
            ok = must_fail
            got = 'FAIL (%s)' % (first[1][:110] if len(first) > 1 else first[0][:110])
        finally:
            undo()
        print("  [%s] %-62s -> %s" % ('OK ' if ok else 'BAD', label, got))
        return ok

    results = []
    tgt = BOAR_SNATCHER[0]                      # Will's own record, charLevel 15
    shell = r'records\xpack\creatures\monster\lostsoul\um_tantalus_99.dbr'
    term = EXEMPT[shell][1]
    summon = r'records\item\equipmentring\soul\test\um_bloodcrow_50.dbr'
    NEW_RED = r'records\creature\monster\skeleton\um_negtest_reduber_99.dbr'
    NEW_HERO = r'records\creature\monster\arachnos\um_negtest_hero_18.dbr'
    STALE = r'records\creature\monster\skeleton\um_negtest_nonexistent_99.dbr'

    other = r'records\creature\monster\beetle\um_grimshell_33.dbr'   # NOT in WIRE
    results.append(run("N1 a wired target's orb removed",
                       lambda d: _del_field(d, tgt, _TREASURE)))
    # deliberately on a NON-wired red uber, so check (c)'s pin assertion cannot
    # fire first and mask the dangling-resolution half of check (a).
    results.append(run("N2 a red uber's orb points at a non-existent record",
                       lambda d: _set_field(d, other, _TREASURE,
                                            r'records\item\containers\new\nope_99.dbr')))

    def _plant_new_red_uber(d):
        d.clone_record(_resolve(d, r'records\creature\monster\skeleton\um_gorrahk_99.dbr'),
                       NEW_RED)
        _del_field(d, NEW_RED, _TREASURE)
        d._modified.add(NEW_RED)
        return lambda: _drop_record(d, NEW_RED)
    results.append(run("N3 a NEW red uber planted with no orb (the R-200 regression)",
                       _plant_new_red_uber))

    results.append(run("N4 a shell's TERMINAL stripped of its orb",
                       lambda d: _del_field(d, term, _TREASURE)))
    results.append(run("N5 a summon exemption flipped to dropItems = 1",
                       lambda d: _set_field(d, summon, 'dropItems', 1)))

    def _stale_exemption(_d):
        EXEMPT[STALE] = ('summon', None, 'planted stale exemption')
        return lambda: EXEMPT.pop(STALE, None)
    results.append(run("N6 a stale exemption naming a non-roster record", _stale_exemption))

    def _wrong_tier(d):
        # move BOTH the pin and the record, so check (c) agrees with itself and
        # only the minimum-distance rule (f) can fire - otherwise (c) would mask it.
        old = WIRE[tgt]
        WIRE[tgt] = (ORB04, old[1], old[2])
        undo_rec = _set_field(d, tgt, _TREASURE, ORB04)

        def _undo():
            WIRE[tgt] = old
            undo_rec()
        return _undo
    results.append(run("N7 a pin moved to a tier that is not minimum-distance",
                       _wrong_tier))

    def _hero_no_orb(d):
        d.clone_record(_resolve(d, r'records\creature\monster\arachnos\um_scorix_18.dbr'),
                       NEW_HERO)
        d.set_field(NEW_HERO, 'monsterClassification', 'Hero')
        _del_field(d, NEW_HERO, _TREASURE)
        return lambda: _drop_record(d, NEW_HERO)
    results.append(run("N8 a um_* HERO-rank record with no orb (scope: stays GREEN)",
                       _hero_no_orb, must_fail=False))

    results.append(run("N9 the untouched control", None, must_fail=False))

    bad = results.count(False)
    print("\nnegtest: %d/%d as designed" % (len(results) - bad, len(results)))
    if bad:
        raise SystemExit("red_uber_orbs negtest FAILED on %d case(s)" % bad)


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == '--analyze':
        _analyze(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == '--negtest':
        _negtest(sys.argv[2])
    else:
        print(__doc__)
        print("usage: py tools/patches/red_uber_orbs.py --analyze|--negtest <arz>")
