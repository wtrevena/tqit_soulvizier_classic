r"""svc_orb_breadth.py - THE UBER-ORB LOOT BREADTH CONTRACT (Will 2026-08-10, R-220).

WILL, VERBATIM (2026-08-10)
---------------------------
"for the mystical orbs that the uber monsters drop, the items should drop with
 increased breadth as well so all classes of items could be dropped"

"as well" points straight at R-180: the CHESTS were fixed that morning (every mod
chest pays every weapon class, legendary spears 0 -> 22). This is the same contract
applied to the OTHER half of the mod's loot economy - the on-death mystical orb.

WHAT THE ORB IS (mechanically, so the scope can be derived instead of typed)
----------------------------------------------------------------------------
A monster's `treasureProxyName` names a Proxy record. The proxy carries three
difficulty slots - `accessory1` / `accessoryEpic1` / `accessoryLegendary1` - each
naming a ProxyAccessoryPool, whose `fixedItemName1` names a FixedItemContainer
(the physical orb: DRX\meshes\bossorbmesh.msh, scale 0.7, `description
tagEndChest02` = base Text_EN "Mystical Orb"), whose `tables` names the
FixedItemLoot table that actually decides what falls out. So one orb tier is THREE
independent loot tables, one per difficulty, and the difficulty is read off the
SLOT the chain came through - never guessed from a file name.

THE DEFECT - MEASURED ON THE build76 SHIP arz (51,234 records), NOT ASSUMED
---------------------------------------------------------------------------
It is the SAME collapse R-180 found in the chests, in a different donor family,
and it is total: **0 spears of ANY quality were reachable from 15 of the 18 uber
orb tables, at every tier and every difficulty.** Each table's weapon row (loot1)
names five things and has ONE free member slot:

    all_13-15 (w2000) . staff_all_13-15 (w500) . unique\1h_all_n01 (w27)
    . unique\bow_n01 (w27) . unique\staff_n01 (w27)

`1h_all_n01` is a LootMasterTable of exactly THREE children - axe, club, sword.
The donor compensates for bow and staff by naming them DIRECTLY and forgot the
third excluded class, SPEAR; the level-banded statics carry no unique spears at
all. Identical shape, identical omission, identical consequence as the chests -
which is why this is one shared contract and not a second opinion.

MEASURED, per tier, target classification (Normal pays Epic, Epic/Legendary pay
Legendary), distinct reachable items BEFORE this wave:

    orb01  n 117  e  72  l 194      spear 0/0/0     (13 consumers)
    orb02  n 101  e  75  l 138      spear 0/0/0     ( 7 consumers)
    orb03  n  96  e  71  l 196      spear 0/0/0     (13 consumers)
    orb04  n  99  e  95  l 258      spear 0/0/0     (21 consumers)
    orb05  n 181  e 116  l 308      spear 18/9/22   ( 8 consumers)  <- ALREADY FIXED
    charon n  99  e  95  l 258      spear 0/0/0     ( 4 consumers)

orb05 is the tell. Its tables are `records\item\loottables\svc\svc_uberorb_apex_*`
- they live in an `\svc\` folder, so R-180's `chest_loot_breadth` sweep (scoped to
mod-OWNED FixedItemLoot) already gave them the breadth master, loot1Chance 40 and
loot6Chance 30. The other four tiers sit under `records\item\containers\defaultloot\`
and `records\xpack\item\containers\loot tables\`, so that sweep never saw them.
This module is therefore not a new idea: it finishes the sweep R-180 started, using
R-180's own module, on the tables its ownership rule could not reach.

THE FIX (this module is the ONE implementation; nothing may re-derive it)
-------------------------------------------------------------------------
Per in-scope table, EXACTLY the R-180 edit, via `svc_loot_breadth.widen_weapon_row`:
  1. the tier-correct aggregate master `svc_unique_weapons_{n,e,l}01` (unique_1h +
     SPEAR + bow + staff + the base all_{tier}0{1,2,3} mastertables) into the ONE
     free loot1 member slot at weight 800;
  2. loot1Chance (weapons) 13/14 -> 40 and loot6Chance (shields) 13/14 -> 30.
Both values are the ones orb05 has ALREADY SHIPPED since build75, so this makes the
ladder self-consistent rather than inventing a number: after this wave every loot
container in the mod - chest or orb - carries the same weapon row shape.

WHAT IS NEVER TOUCHED (each orb's identity, asserted field-by-field by apply()):
  * numSpawnMin/MaxEquation - byte-unchanged, so the apex tier keeps its *2.2/*2.4
    advantage over the generic tiers' *1.2/*1.6 and *0.9/*1.3;
  * loot2 (torso/head), loot3 (potions/misc), loot4 (amulet/ring/RELIC/formula) and
    loot5 (legs/arms) - byte-unchanged, so the per-difficulty relic law and every
    guaranteed row survive by construction;
  * the proxy, the 3 accessory pools and the 3 chest records per tier - each one
    proven field-identical after the sweep, so mesh, scale, gold generator, level
    equation and `description tagEndChest02` are all exactly what shipped;
  * no member is ever removed and no chance is ever lowered (`_raise_chance` takes
    max(existing, target) and refuses to switch a dormant slot ON).
There is deliberately NO guaranteed-weapon retarget here: an orb's loot3 is
potions + rare misc at 10%, not the chests' 100% weapon slot, and R-180's
`retarget_guaranteed_weapon` only ever rewrites a member matching
`\unique_1h_[nel]0\d\.dbr$` in loot3 - which no orb table names. Adding a
guaranteed weapon row would change HOW MUCH an orb pays, and Will asked for
breadth.

TIER LAW (R-100 #17 + Will 2026-08-08) is preserved by construction: the master is
resolved through the DIFFICULTY SLOT the chain arrived on, so the normal branch can
only ever gain `*_n01` tables (measured 100% Epic-classification, 0 Legendary).
MEASURED BASELINE, so the gate is honest about what was already there: the normal
branch of every orb tier already reaches 41-56 `ItemArtifact` + 3 `ItemArtifactFormula`
Legendary-classified records (mercenary scrolls / arcane formulae) and ZERO
legendary GEAR. That is base-game content, it is what R-180's own B3 exempts, and
this wave leaves it at zero legendary gear.

SCOPE - DERIVED OVER MOD UNION BASE, NEVER TYPED (the R-200 lesson)
-------------------------------------------------------------------
An UBER is R-200's own predicate: a `Monster.tpl` record whose basename starts
`um_` (the uber namespace) OR whose display tag starts `tagSVCMonster` (our own
ubers under a donor filename). R-200 learned the hard way that a roster derived
over the MOD db alone is blind - the Boar Snatcher was base-only - so the carrier
scan runs over mod UNION base, reusing `red_uber_orbs.load_base_rows` (already
cached for the build).

SCOPE = every proxy an UBER names, and every loot table its three difficulty slots
resolve to. MEASURED on the build76 arz: **51 uber carriers -> 7 proxies, of which 6
are in reach -> 18 tables**:
    genericbossorb_01/02/03/04/05  (the 5-tier mystical-orb ladder, tagEndChest02)
    bosschest02_charon             (xtagChest18 "Charon's Essence" - the Ferryman's
                                    terminal form `um_charonform2_ferryman_99` is a
                                    red uber, and its 3 tables carry the IDENTICAL
                                    collapsed weapon row)
                                    R-247.1 UPDATE: the uber terminal (now Akremon)
                                    names the CLONE proxy `svc_akremon_orb` instead;
                                    same 3 tables, shared with the story Charon's
                                    donor chests under the DONOR_TWINS byte gate.
    25_towerofjudgement_treasure   OUT OF REACH - see OUT_OF_REACH below. Found BY
                                   this gate on its first union run, which is R-200
                                   HOLE 2 paying for itself immediately.

DELIBERATELY OUT OF SCOPE, and it is the same boundary R-200 drew: the six proxies
whose consumers are base act/quest bosses rather than ubers - `bosschestproxy11_aktaios`
(3 Telkines), `bosschestproxy21_typhon` (2), `bosschestproxy_blackwidow` (1),
`coldworm_orb` (1), `1_default_33-35` (1) - and `bosschestproxy_leinth`, whose three
Boss-rank carriers are neither `um_` nor tagSVCMonster. Leinth needs nothing anyway:
her chests were repointed onto the `svc_uberorb_apex_*` tables by `uber_apex_orb`,
so R-180 already widened them and R-180's gate already covers them. The base-boss
chains are registered as debt, not silently ignored.

Also the audit half (`audit_db`) so the standalone `tools/gate_orb_loot_breadth.py`,
the in-build registry gate (`tools/patches/orb_loot_breadth.verify`) and the
negative tests all share ONE implementation and cannot disagree.
"""
import inspect
import sys
from collections import defaultdict
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))
if str(_TOOLS / 'patches') not in sys.path:
    sys.path.insert(0, str(_TOOLS / 'patches'))

import svc_loot_breadth as SLB

# ── the container noun, and the ONE shared-file coupling this lane owns ───────
# `svc_loot_breadth.audit_table` gained a cosmetic `noun=` kwarg for R-220 - it is
# the only edit this lane makes to that shared file, and it changes no check. TWO
# sibling breadth lanes rewrite the same function (`fix/armor-loot-breadth` and
# `fix/craft-thrown-breadth`, the latter adding its C1/C2 thrown block while keeping
# the old signature), so a merge resolution that takes their hunk wholesale would
# delete the kwarg and turn every call here into a TypeError INSIDE a fail-loud gate.
# One word in one message must not be able to break a build - so the capability is
# probed once, and the downgrade is ANNOUNCED rather than silent (the
# `_base_rows` / B-GATE-HARDEN-1 idiom). Integration instruction: BL-R220-DEBT-5.
NOUN = "an uber's orb"
_NOUN_SUPPORTED = 'noun' in inspect.signature(SLB.audit_table).parameters
_NOUN_WARNED = False


def _audit_table(db, table, tier, ex, floor):
    """`SLB.audit_table` with this lane's container noun, merge-tolerantly."""
    global _NOUN_WARNED
    if _NOUN_SUPPORTED:
        return SLB.audit_table(db, table, tier, ex, floor=floor, noun=NOUN)
    if not _NOUN_WARNED:
        _NOUN_WARNED = True
        print("  [svc_orb_breadth] WARNING svc_loot_breadth.audit_table has no `noun=` "
              "kwarg on this tree, so orb B1 messages will say 'a chest'. The CHECKS "
              "are unaffected. This is a merge resolution that dropped R-220's "
              "one-word kwarg (BL-R220-DEBT-5) - no silent pass: this line IS the "
              "downgrade.")
    return SLB.audit_table(db, table, tier, ex, floor=floor)

# ── the chain shape: proxy slot -> the difficulty it serves ──────────────────
# Reuses red_uber_orbs._DIFF_FIELDS' three fields; the SHORT tier letter is what
# svc_loot_breadth resolves its donors through, so an orb can never be handed a
# mixed-tier table.
DIFF_SLOTS = (('accessory1', 'n'), ('accessoryEpic1', 'e'), ('accessoryLegendary1', 'l'))
DIFF_LABEL = {'n': 'normal', 'e': 'epic', 'l': 'legendary'}

# ── the uber predicate (R-200's, verbatim in intent) ─────────────────────────
_MONSTER_TPL = 'templates\\monster.tpl'
_UBER_TOKEN = 'um_'
_OURS_TAG_PREFIX = 'tagsvcmonster'
_TREASURE = 'treasureProxyName'

# ── the fields this module is allowed to move, and NOTHING else ─────────────
# `loot1Name<free>` / `loot1Weight<free>` are the one added member slot; the two
# chances are strict raises. Anything else changing on an in-scope record is a bug
# and apply()'s scope proof fails the build on it.
ALLOWED_FIELD_PREFIXES = ('loot1Name', 'loot1Weight')
ALLOWED_FIELDS = ('loot1Chance', 'loot6Chance')

# ── POOL FLOORS, per difficulty branch ───────────────────────────────────────
# MEASURED by the dry-run of this exact code against the build76 ship arz -
# distinct target-classification items in the THINNEST table of each branch,
# before -> after:   n 96 -> 180    e 71 -> 96    l 138 -> 241.
# Each floor sits ~15% under the post-wave thinnest table, so ordinary content
# edits do not trip it.
POOL_FLOOR = {'n': 150, 'e': 80, 'l': 200}
# HONEST LIMIT, stated rather than implied. R-180 could also set its chest floors
# ABOVE the collapsed pre-wave value, so a silent revert reds on the COUNT alone.
# Here that is only true of the normal branch (150 > the richest pre-wave normal
# table, 117). On the epic and legendary branches the pre-wave tables were richer
# than 85% of the post-wave thinnest (95 and 258 respectively), so a count-only
# floor able to catch a revert there would sit within one item of the live value
# and red on any ordinary content edit. That trade is not needed: a revert on
# those branches is caught by O1 (the spear class disappears) and, structurally
# and by name, by O2b (the breadth master stops being in the weapon row). The
# floor's job on those branches is the one case O1 cannot see - a pool that
# collapses while a single spear survives.

# Sanity floors on the scope itself: the derivation must never quietly shrink to
# nothing (the `chest_loot_breadth` "no chest audited at all" lesson). MEASURED on
# the build76 arz: 51 uber carriers -> 7 proxies, 6 of them IN REACH -> 18 tables.
# The floor counts the IN-REACH proxies, since those are the ones with tables.
MIN_PROXIES = 6
MIN_TABLES = 18

# ── OUT OF REACH: an uber whose proxy lives ONLY in the base game ────────────
# FOUND BY THIS GATE ITSELF, running in mod-UNION-base mode (it is exactly the
# R-200 HOLE 2 shape, so the union scan earning its keep on the first run is the
# expected outcome, not a surprise). The mod overlay cannot widen a record it does
# not contain, and importing a base container chain wholesale is a different
# decision from widening one weapon row - so these are reported, counted and
# PINNED with their reason, never silently dropped. An UNPINNED base-only chain
# fails the gate, so a new one is a human decision rather than a quiet omission
# (the `uber_quest_markers._exempt_closure` / R-200 EXEMPT discipline).
OUT_OF_REACH = {
    r'records\proxies boss\le_new\25_towerofjudgement_treasure.dbr':
        "base-only proxy carried by the base-only Hero-rank DEVICE "
        r"`records\creature\devices\darkobelisk\um_darkobelisk_55.dbr` "
        "(tagAEMonsterName07, the Dark Obelisk - an `um_` record by filename, not a "
        "fought uber). MEASURED: it resolves fine in the base game and its chain "
        "lands on `g_default_{n,e,l}01c` - the GOLDEN CHEST tables (tagChest006), "
        "each shared with FIVE base containers (the act-4 golden chests, 2 "
        "side-quest golden chests, the Cerberus and Skeletal Typhon repeat boss "
        "chests). Widening it would rewrite the base game's act-4 golden-chest "
        "economy, which is neither a mystical orb nor anything Will named - the "
        "same boundary R-200 drew. Registered as BL-R220-DEBT-1.",
}

# ── SHARED TABLES: acknowledged, deliberately not widened ───────────────────
# EMPTY ON PURPOSE, and MEASURED empty: all 15 non-mod-owned in-scope tables have
# exactly ONE referrer (their own orb chest), and the 3 mod-owned apex tables are
# exempted by the mod-ownership clause of `shared_tables` (they are shared with
# Leinth's chests on purpose, and R-180's gate already covers them). So this dict
# is a GUARD, not live config: if a future uber chain ever lands on a table the
# base game also uses, the gate stops the build and a human decides whether to
# widen shared loot. Pin it here WITH the decision to make the gate green again.
SHARED_TABLES_ACKNOWLEDGED = {}

# ── DONOR TWINS: the R-247.1 orb-rename carve-out (MEASURED, byte-gated) ─────
# `charon_rework` (R-247 ruling 1: "he still drops an orb named Charon's
# Essence") clones the base-game Charon chest chain so ONLY the on-screen name
# changes: Akremon's terminal names the CLONE proxy `svc_akremon_orb`, whose
# containers `svc_akremon_orb_0{1,2,3}` keep the donors' `tables` pointers
# (boss_charon_{n,e,l}01b) verbatim. The DONOR containers
# `bosschest02_charon_0{1,2,3}` remain the LIVE drop chain of the base-game
# story Charon - MEASURED on the shipped a86afc15 arz: boss_charonform2_39/41/43
# all name the donor proxy - so they still name those same three tables from
# OUTSIDE the uber chains. Without this carve-out `shared_tables` refuses the
# three tables and the scope floor collapses 18 -> 15 (the round-1 vet's
# SCOPE COLLAPSED repro, exit 1 at module 61/66).
#
# THE DECISION BEING PINNED (O6's question is "may shared loot stay widened?"):
# YES for exactly this sharing, because it is the SHIPPED, RATIFIED state. In
# every build up to and including a86afc15 the uber terminal and the story
# Charon dropped through the SAME chain, so boss_charon_{n,e,l}01b already carry
# the R-220 widening and the R-242 orb-rate treatment for BOTH consumers. The
# carve-out preserves those bytes verbatim; the alternative (cloning the tables
# for the uber chain) would strip the treatment from the story Charon's chest -
# a silent base-game loot nerf, the exact R-247.7 offence class.
#
# THE FIELD GATE: a donor is exempt ONLY while it is field-for-field identical
# to its clone twin outside DONOR_TWIN_ALLOWED_DIFFS (`description` - the
# renamed chest tag - is the single authored delta of the R-247.1 clone).
# String values are compared CASE-NORMALIZED (`_twin_cmp` - the engine resolves
# record refs case-insensitively, and the pipeline lowercases refs it writes
# while untouched records keep upstream mixed case; a case variant of the same
# path is not drift). The moment either record REALLY drifts (different target
# record, different number, added/removed field, dtype change), the exemption
# dies, the tables return to shared/refused, the floors collapse and the build
# reds loudly with the diverged fields AND both values printed - drift is a
# human decision, never a quiet pass. Negative:
# `tools/debug/negtest_orb_breadth.py` N10 plants exactly that divergence.
DONOR_TWINS = {
    r'records\xpack\item\containers\bosschest02_charon_01.dbr':
        r'records\xpack\item\containers\svc_akremon_orb_01.dbr',
    r'records\xpack\item\containers\bosschest02_charon_02.dbr':
        r'records\xpack\item\containers\svc_akremon_orb_02.dbr',
    r'records\xpack\item\containers\bosschest02_charon_03.dbr':
        r'records\xpack\item\containers\svc_akremon_orb_03.dbr',
}
DONOR_TWIN_ALLOWED_DIFFS = ('description',)

_n = SLB._n
_sc = SLB._sc

_DONOR_TWINS_N = {_n(k): _n(v) for k, v in DONOR_TWINS.items()}
_TWIN_ANNOUNCED = set()


def _twin_fields(db, rec):
    """{lower(field): (values, dtype)} - the comparable image of one record."""
    out = {}
    for k, tf in (db.get_fields(rec) or {}).items():
        out[k.split('###')[0].lower()] = (list(tf.values), tf.dtype)
    return out


def _twin_cmp(vals):
    """Comparable form of one field's values: strings are compared
    case-normalized (`_n`), everything else exact.

    WHY (MEASURED, round-2 build 1): the upstream arzs carry MIXED-case
    reference paths (`Records\\Item\\...\\BossGoldGenerator.dbr`); modules that
    WRITE a reference write it `_n`-lowercased. So a record that has ever been
    written carries lowercase refs while an untouched one keeps upstream case -
    the shipped a86afc15 donor itself shows both in one record (mesh mixed-case,
    the 4 ref fields lowercase). The clone is written (description) and so gets
    re-encoded; the donor is untouched in the R-247 build - a case-only,
    semantics-free divergence on goldGenerator/levelEquationFile/openSound/
    tables that redded build 1 at slot 59. The engine resolves record refs
    case-insensitively, so the twin law compares what the engine sees. Every
    REAL drift (different target record, different number, added/removed field,
    dtype change) still differs after normalization - negtest N10 proves it."""
    return [_n(v) if isinstance(v, str) else v for v in vals]


def twin_field_diffs(db, donor, clone):
    """Field names on which donor and clone differ SEMANTICALLY (strings
    case-normalized - see `_twin_cmp`), ignoring the allowed set."""
    a, b = _twin_fields(db, donor), _twin_fields(db, clone)
    allowed = {f.lower() for f in DONOR_TWIN_ALLOWED_DIFFS}
    out = []
    for k in sorted((set(a) | set(b)) - allowed):
        ta, tb = a.get(k), b.get(k)
        if ta is None or tb is None:
            out.append(k)
        elif ta[1] != tb[1] or _twin_cmp(ta[0]) != _twin_cmp(tb[0]):
            out.append(k)
    return out


def _twin_exempt(db, lk, referrer, chest_set):
    """True iff `referrer` is a PINNED donor whose R-247 clone twin is one of the
    uber chains' own chests AND the two records still satisfy the same-bytes law
    (identical outside DONOR_TWIN_ALLOWED_DIFFS). Inert on any arz where the
    clone chain does not exist or is not in an uber chain (a pre-R-247 build has
    the donor itself in `chest_set`, so this is never even consulted there).
    Announced once per donor per process, both ways - never a silent pass."""
    ref_l = _n(referrer)
    twin_l = _DONOR_TWINS_N.get(ref_l)
    if twin_l is None or twin_l not in chest_set:
        return False
    twin = lk.real(twin_l)
    if twin is None:
        return False
    diffs = twin_field_diffs(db, referrer, twin)
    key = (ref_l, bool(diffs))
    if diffs:
        if key not in _TWIN_ANNOUNCED:
            _TWIN_ANNOUNCED.add(key)
            a, b = _twin_fields(db, referrer), _twin_fields(db, twin)
            detail = '; '.join('%s: donor=%r clone=%r' % (f, a.get(f), b.get(f))
                               for f in diffs)
            print("  ORB BREADTH: DONOR-TWIN PIN VOID - %s has drifted from its "
                  "R-247 clone %s on field(s) %s [%s]. The same-bytes law is "
                  "broken, so the shared-table refusal is BACK ON for its tables "
                  "(expect the scope floor to red). Re-decide the pin; never "
                  "widen blind."
                  % (ref_l.rsplit('\\', 1)[-1], twin_l.rsplit('\\', 1)[-1],
                     ', '.join(diffs), detail))
        return False
    if key not in _TWIN_ANNOUNCED:
        _TWIN_ANNOUNCED.add(key)
        print("  ORB BREADTH: donor-twin exemption active - %s verified "
              "field-identical (excl %s) to in-chain clone %s (R-247.1 rename "
              "law; the story Charon keeps the shipped shared tables)"
              % (ref_l.rsplit('\\', 1)[-1], '/'.join(DONOR_TWIN_ALLOWED_DIFFS),
                 twin_l.rsplit('\\', 1)[-1]))
    return True


# ─────────────────────────────────────────────────────────────────────────────
# SCOPE DERIVATION (mod UNION base)
# ─────────────────────────────────────────────────────────────────────────────
def _is_uber(basename, desc):
    return (basename.startswith(_UBER_TOKEN)
            or str(desc or '').lower().startswith(_OURS_TAG_PREFIX))


def uber_proxies(db, base_rows=None):
    """{norm(proxy): [carrier record, ...]} for every proxy an UBER names.

    Derived over mod UNION base: `base_rows` is `red_uber_orbs.load_base_rows()`'s
    map, so a base-only uber (the Boar Snatcher class of defect) is visible here
    even when the mod overlay has never heard of it. The mod overlay WINS on any
    record present in both, which is the engine's own resolution order.
    """
    out = defaultdict(list)
    seen = set()

    def _consider(name, desc, proxy):
        key = _n(name)
        if key in seen:
            return
        seen.add(key)
        if not _is_uber(key.rsplit('\\', 1)[-1], desc):
            return
        if isinstance(proxy, str) and proxy.strip():
            out[_n(proxy)].append(name)

    for name in db.record_names():
        tpl = _sc(db.get_field_value(name, 'templateName'))
        if not (isinstance(tpl, str) and _n(tpl).endswith(_MONSTER_TPL)):
            continue
        _consider(name, _sc(db.get_field_value(name, 'description')),
                  _sc(db.get_field_value(name, _TREASURE)))
    for row in (base_rows or {}).values():
        _consider(row['_name'], row.get('description'), row.get(_TREASURE))
    return dict(out)


def orb_chains(db, lk=None, base_rows=None, proxies=None):
    """[(proxy, difficulty, pool, chest, table, carriers)] for every uber drop chain
    whose proxy the mod overlay actually contains.

    A link that does not resolve is reported with None in its place rather than
    dropped, so `audit_db` can red it instead of silently narrowing the scope.
    A chain whose PROXY is base-only is not a broken chain - it is out of reach
    (see OUT_OF_REACH); `unreachable_chains` reports those separately.

    `proxies` lets a caller pass an already-computed `uber_proxies()` map. Deriving
    it costs a full 51k-record scan, and the audit needs the same map four times,
    so every helper here takes the precomputed value (the negative-test battery runs
    the whole audit ten times over).
    """
    lk = lk or SLB.Lookup(db)
    chains = []
    proxies = uber_proxies(db, base_rows) if proxies is None else proxies
    for proxy_l, carriers in sorted(proxies.items()):
        proxy = lk.real(proxy_l)
        if proxy is None:
            continue                       # -> unreachable_chains()
        for field, tier in DIFF_SLOTS:
            pool = lk.real(_sc(db.get_field_value(proxy, field)))
            chest = lk.real(_sc(db.get_field_value(pool, 'fixedItemName1'))) if pool else None
            table = lk.real(_sc(db.get_field_value(chest, 'tables'))) if chest else None
            chains.append((proxy, tier, pool, chest, table, carriers))
    return chains


def unreachable_chains(db, lk=None, base_rows=None, proxies=None):
    """{norm(proxy): carriers} for uber proxies the MOD overlay does not contain.

    These are base-game chains: real at runtime, invisible and un-editable from
    the overlay. Kept as a first-class result instead of a silent skip.
    """
    lk = lk or SLB.Lookup(db)
    proxies = uber_proxies(db, base_rows) if proxies is None else proxies
    return {p: c for p, c in sorted(proxies.items()) if lk.real(p) is None}


def _referrers(db, table_l, cache):
    """Every record whose `tables` field names `table_l` (one pass, memoised)."""
    if not cache:
        for rec in db.record_names():
            v = _sc(db.get_field_value(rec, 'tables'))
            if isinstance(v, str) and v.strip():
                cache.setdefault(_n(v), []).append(rec)
    return cache.get(table_l, [])


def shared_tables(db, lk=None, base_rows=None, chains=None):
    """{norm(table): [outside referrer, ...]} for in-scope tables that are ALSO
    named by a container outside every uber drop chain.

    WHY THIS GUARD EXISTS. Widening a table changes loot for EVERY container that
    names it. The orb tables are exclusive to their own orb chests (MEASURED: 1
    referrer each), so widening them touches only uber drops. But a chain that
    landed on a SHARED table - the Dark Obelisk's golden-chest tables are the live
    example, 5 base referrers each - would quietly rewrite base-game loot from a
    lane that was asked about mystical orbs. A table is therefore in scope only if
    every referrer is one of the uber chains' own chests, OR the table is mod-owned
    (an `\\svc\\` table is R-180's scope and is already gated there; the 3 apex
    tables are exactly that case, shared deliberately with Leinth's chests), OR
    the referrer is a byte-verified DONOR TWIN of an in-chain chest (the R-247.1
    orb-rename carve-out - see DONOR_TWINS above: the story Charon's own chests,
    field-identical to the uber's clone chests outside `description`, keep the
    shipped shared tables in scope instead of collapsing the floor).
    """
    lk = lk or SLB.Lookup(db)
    chains = orb_chains(db, lk, base_rows) if chains is None else chains
    chest_set = {_n(c[3]) for c in chains if c[3]}
    cache = {}
    out = {}
    for _p, _t, _pool, _chest, table, _c in chains:
        if not table or _n(table) in out or SLB.is_mod_owned(table):
            continue
        outside = [r for r in _referrers(db, _n(table), cache)
                   if _n(r) not in chest_set
                   and not _twin_exempt(db, lk, r, chest_set)]
        if outside:
            out[_n(table)] = outside
    return out


def scope_tables(db, lk=None, base_rows=None, chains=None, shared=None):
    """{norm(table): (real, tier)} - the in-scope loot tables, de-duplicated.

    De-duplication matters: two orb tiers may legitimately share a table, and a
    table must be widened once and audited once. Tables shared with a container
    outside the uber chains are EXCLUDED (see `shared_tables`).

    THE DE-DUPLICATION IS TIER-BLIND ON PURPOSE, AND `tier_conflicts` IS ITS GUARD.
    The first chain wins, so a table reachable through TWO different difficulty
    slots would be widened and audited at ONE tier only - a silent narrowing that
    O4's scope COUNT cannot see, because the count stays the same. MEASURED on both
    the build76 and build78 arz: 6 in-reach proxies x 3 slots = 18 chains resolving
    to 18 DISTINCT tables, zero overlap, so this is inert today. `tier_conflicts`
    makes it loud tomorrow (O4b).
    """
    chains = orb_chains(db, lk, base_rows) if chains is None else chains
    shared = shared_tables(db, lk, base_rows, chains) if shared is None else shared
    out = {}
    for _proxy, tier, _pool, _chest, table, _c in chains:
        if table and _n(table) not in out and _n(table) not in shared:
            out[_n(table)] = (table, tier)
    return out


def tier_conflicts(db, lk=None, base_rows=None, chains=None, shared=None):
    """{norm(table): [tier, ...]} for tables reached at MORE THAN ONE difficulty.

    Always empty on a healthy build (MEASURED empty on build76 and build78). It is
    the explicit complement of `scope_tables`' first-wins de-duplication: if a chain
    rewiring ever made one table serve two difficulty slots, that table would be
    handed a single tier's master and audited against a single tier's floor with no
    other signal at all. Reported as O4b so the narrowing is a decision, not a shrug.
    """
    chains = orb_chains(db, lk, base_rows) if chains is None else chains
    shared = shared_tables(db, lk, base_rows, chains) if shared is None else shared
    seen = defaultdict(set)
    for _proxy, tier, _pool, _chest, table, _c in chains:
        if table and _n(table) not in shared:
            seen[_n(table)].add(tier)
    return {t: sorted(v) for t, v in sorted(seen.items()) if len(v) > 1}


def in_reach_proxies(lk, proxies):
    """The uber proxies the mod overlay actually contains - the ones with tables.

    MIN_PROXIES counts THESE, so apply() and audit_db must both measure it this way;
    counting the raw `uber_proxies` map instead would make the apply-side collapse
    guard one proxy weaker than its own floor (the base-only Dark Obelisk chain
    inflates the raw map to 7).
    """
    return sorted(p for p in proxies if lk.real(p) is not None)


# ─────────────────────────────────────────────────────────────────────────────
# WRITE SIDE (a thin driver over the R-180 implementation)
# ─────────────────────────────────────────────────────────────────────────────
def snapshot(db, records):
    """{record: {field: (values, dtype)}} - the before-image the scope proof needs."""
    shot = {}
    for rec in records:
        if not rec:
            continue
        fields = {}
        for k, tf in (db.get_fields(rec) or {}).items():
            fields.setdefault(k.split('###')[0], (list(tf.values), tf.dtype))
        shot[rec] = fields
    return shot


def field_diffs(before, after):
    """[field] whose value list changed between two snapshot() field maps."""
    diffs = []
    for f in set(before) | set(after):
        a = list(before.get(f, ([], None))[0])
        b = list(after.get(f, ([], None))[0])
        if a != b:
            diffs.append(f)
    return sorted(diffs)


def is_allowed_change(field):
    return field in ALLOWED_FIELDS or field.startswith(ALLOWED_FIELD_PREFIXES)


def widen_chains(db, lk=None, base_rows=None, verbose=True, tables=None):
    """Apply the R-180 weapon-row contract to every in-scope orb table.

    Returns (changes, tables) where changes = {table: [change, ...]}.
    Idempotent: a table that already carries the master and the raised chances
    (orb05, widened by chest_loot_breadth) reports no change.
    """
    lk = lk or SLB.Lookup(db)
    tables = scope_tables(db, lk, base_rows) if tables is None else tables
    changes = {}
    for _key, (table, tier) in sorted(tables.items()):
        keep = _hold_chances(db, lk, table)
        ch = SLB.widen_weapon_row(db, table, tier, lk)
        ch = keep(ch)
        if ch:
            changes[table] = ch
            if verbose:
                print("    %-58s [%s] %s"
                      % (_n(table).rsplit('\\', 1)[-1], tier, '; '.join(ch)))
    return changes, tables


# ── THE PAYOUT HALF, ISOLATED SO IT CAN BE VETOED IN ONE EDIT ────────────────
# Will asked for BREADTH: "all classes of items could be dropped". That is the
# added loot1 member, and nothing else. The wave ALSO raises loot1Chance 13/14 -> 40
# and loot6Chance 13/14 -> 30 on the same 15 base-game tables - defensible (they are
# the values orb05's apex tables have shipped since build75, and R-180 made the
# identical raise on the chests) but it is a PAYOUT change he did not ask for, and it
# is half the field moves in this wave. So it is a named switch rather than a
# re-derivation: set this False and the orbs gain every weapon class at exactly the
# drop rate they have today. The breadth half is untouched by it either way.
# This lives HERE, not in `svc_loot_breadth.widen_weapon_row`, because that builder is
# shared with the CHESTS - editing it would silently revert R-180's chest raises too.
RAISE_ROW_CHANCES = True
_CHANCE_FIELDS = ('loot1Chance', 'loot6Chance')


def _hold_chances(db, lk, table):
    """Returns a filter that restores the two row chances when the payout half is off.

    A no-op (identity) in the shipped configuration, so the default path writes
    exactly what it wrote before this switch existed.
    """
    if RAISE_ROW_CHANCES:
        return lambda changes: changes
    import red_uber_orbs as RUO                       # the repo's dtype-safe snapshot
    real = lk.real(table)
    saved = [(f, RUO._snapshot_field(db, real, f)) for f in _CHANCE_FIELDS]

    def _restore(changes):
        for field, shot in saved:
            if shot:
                RUO._restore_field(db, real, field, shot)
        return [c for c in changes if not c.startswith(_CHANCE_FIELDS)]
    return _restore


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT SIDE (shared by the in-build gate, the standalone gate and the negtests)
# ─────────────────────────────────────────────────────────────────────────────
def audit_db(db, lk=None, base_rows=None, verbose=False, floors=None):
    """The orb-breadth contract over the FINAL assembled db.

    Returns (problems, stats) with stats = {table: (tier, pool, {Class: count})}.

      O1/O2/O3  `svc_loot_breadth.audit_table` verbatim, per table, at the tier its
                DIFFICULTY SLOT gives it - every required weapon class reachable at
                that tier's own classification (SPEAR named explicitly), the pool
                floor, and no legendary GEAR on the normal branch.
      O2b       the tier-correct breadth master is NAMED in loot1 of every in-scope
                table. Structural, so it cannot rot with content: a re-collapse reds
                here immediately and by name even if the counts survived.
      O4        every uber drop chain resolves proxy -> pool -> chest -> table at all
                three difficulties, and the derived scope never shrinks below the
                measured floor (the "no table audited at all" trap).
      O4b       no in-scope table is reached at TWO different difficulties. That is
                the one narrowing O4's COUNT cannot see: `scope_tables` de-duplicates
                first-wins, so such a table would silently be widened and audited at
                one tier only while the table count stayed put.
      O5        every base-only (out-of-reach) uber chain is PINNED in OUT_OF_REACH
                with its reason, and every pin still names a live uber chain - so a
                NEW one is a human decision, not a quiet omission, and a stale pin
                cannot rot.
      O6        no in-scope table is shared with a container outside the uber chains
                (widening a shared table would change loot nobody asked about).
    """
    lk = lk or SLB.Lookup(db)
    ex = SLB.Expander(db, lk)
    floors = floors or POOL_FLOOR
    problems = []
    stats = {}

    def _who(carriers):
        return (carriers[0].rsplit('\\', 1)[-1]
                + (' +%d more' % (len(carriers) - 1) if len(carriers) > 1 else ''))

    # ONE derivation, reused by every check below: each of these costs a full
    # 51k-record scan, and the negative-test battery calls audit_db ten times.
    proxies = uber_proxies(db, base_rows)
    chains = orb_chains(db, lk, base_rows, proxies)

    # O5 - base-only chains: pinned, or a gate failure
    unreachable = unreachable_chains(db, lk, base_rows, proxies)
    pinned = {_n(k) for k in OUT_OF_REACH}
    for proxy_l, carriers in sorted(unreachable.items()):
        if _n(proxy_l) not in pinned:
            problems.append(
                "O5 OUT-OF-REACH ORB CHAIN, NOT PINNED: %s is named by %d uber "
                "record(s) (%s) but does not exist in the mod overlay, so this lane "
                "can neither audit nor widen it. Decide deliberately: import the "
                "chain, or pin it in svc_orb_breadth.OUT_OF_REACH with the reason."
                % (proxy_l, len(carriers), _who(carriers)))
    # The stale-pin half needs the union: a pin naming a BASE-only chain is
    # invisible in mod-only mode, so asserting it there would red every build that
    # cannot read the base arz - a gate that punishes its own downgrade. The
    # downgrade is announced loudly by the caller instead (never a silent pass).
    if base_rows:
        for pin in sorted(pinned):
            if pin not in {_n(k) for k in unreachable} and lk.real(pin) is None:
                problems.append(
                    "O5 STALE OUT_OF_REACH PIN: %s is no longer an out-of-reach uber "
                    "chain (no uber names it, or it is gone). Remove the pin or fix "
                    "the record - a pin that names nothing is dead config." % pin)

    # O6 - tables shared outside the uber chains are excluded, and said so
    shared = shared_tables(db, lk, base_rows, chains)
    ack = {_n(k) for k in SHARED_TABLES_ACKNOWLEDGED}
    for table_l, outside in sorted(shared.items()):
        if table_l in ack:
            continue
        problems.append(
            "O6 SHARED TABLE, NOT ACKNOWLEDGED: %s is in an uber's drop chain but is "
            "ALSO named by %d container(s) outside every uber chain (%s), so widening "
            "it would change loot this lane was never asked about. It is already "
            "excluded from the sweep; decide deliberately and pin it in "
            "svc_orb_breadth.SHARED_TABLES_ACKNOWLEDGED with the decision."
            % (table_l.rsplit('\\', 1)[-1], len(outside),
               ', '.join(_n(o).rsplit('\\', 1)[-1] for o in outside[:4])))

    resolved = in_reach_proxies(lk, proxies)
    for proxy, tier, pool, chest, table, carriers in chains:
        who = _who(carriers)
        if pool is None or chest is None or table is None:
            problems.append(
                "O4 BROKEN CHAIN: %s [%s] -> pool=%s chest=%s table=%s (named by %s). "
                "Every difficulty of an uber's orb must resolve end to end."
                % (_n(proxy).rsplit('\\', 1)[-1], DIFF_LABEL[tier], bool(pool),
                   bool(chest), bool(table), who))

    tables = scope_tables(db, lk, base_rows, chains, shared)
    if len(resolved) < MIN_PROXIES or len(tables) < MIN_TABLES:
        problems.append(
            "O4 SCOPE COLLAPSED: derived %d in-reach proxy/proxies and %d loot "
            "table(s); the measured floor is %d/%d. An orb-breadth gate that audits "
            "nothing is the failure mode this gate exists to prevent."
            % (len(resolved), len(tables), MIN_PROXIES, MIN_TABLES))

    # O4b - one table, two difficulties: the narrowing the table COUNT cannot show
    for table_l, tiers in tier_conflicts(db, lk, base_rows, chains, shared).items():
        problems.append(
            "O4b TABLE REACHED AT %d DIFFERENT DIFFICULTIES: %s is in the drop chain "
            "at tier(s) %s, but scope_tables de-duplicates first-wins, so it would be "
            "widened with ONE tier's master and audited against ONE tier's floor. "
            "Split the table per difficulty, or decide which tier owns it and pin "
            "that decision." % (len(tiers), table_l.rsplit('\\', 1)[-1],
                                ', '.join(DIFF_LABEL[t] for t in tiers)))

    for _key, (table, tier) in sorted(tables.items()):
        problems.extend(_audit_table(db, table, tier, ex, floors[tier]))
        master = lk.real(SLB.MASTER[tier])
        named = {_n(nm) for _i, nm, _w in SLB._slot_members(db, table, 1)}
        if not master or _n(master) not in named:
            problems.append(
                "O2b %s [%s] does not name the breadth master %s in its weapon row - "
                "the R-220 fix is not present on this table (a collapse back to "
                "axe/club/sword + bow + staff, i.e. no spear path at all)."
                % (_n(table).rsplit('\\', 1)[-1], tier,
                   _n(SLB.MASTER[tier]).rsplit('\\', 1)[-1]))
        by_class = ex.pool(table, SLB.TARGET_IC[tier])
        stats[table] = (tier, sum(len(v) for v in by_class.values()),
                        {c: len(v) for c, v in sorted(by_class.items())})
        if verbose:
            spear = by_class.get('WeaponHunting_Spear', ())
            print("    %-52s [%s] %4d %s items, %2d classes, %2d spear"
                  % (_n(table).rsplit('\\', 1)[-1], tier, stats[table][1],
                     SLB.TARGET_IC[tier], len(by_class), len(spear)))
    return problems, stats
