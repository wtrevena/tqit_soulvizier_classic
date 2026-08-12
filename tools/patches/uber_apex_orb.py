r"""uber_apex_orb - ONE apex drop calibre for the WHOLE Toxeus roster AND Leinth.

⚠️ IF YOU READ ONLY ONE PARAGRAPH: this module is NOT a two-champion module any
more. It was one (b94 PART A), and a stale reading of that is exactly how the
Endless Hunt ended up with no orb at all. The scope is now **every Toxeus
CREATURE record in the database**, and the roster is DERIVED by scanning the db
(`toxeus_roster()`), never hand-typed. Both `apply()` and `verify()` cross-check
that derived roster against a pinned allow-list, so a Toxeus variant somebody
adds later REDS THE BUILD instead of being silently dropped.

WILL'S DECISION 2026-07-29 (verbatim, R-99) - THE CURRENT SCOPE
---------------------------------------------------------------
    "i didnt tell you to increase the drop of all the champions, just the toxeus
     variants (all variants we made and didnt make) and leinth. they should drop
     more items than the normal champions"

and, answering the two judgement calls the first pass raised:

    "give all versions of toxeus the new apex orb, if some good items drop since
     someone got lucky and found and killed the low-level Toxeus with no fixed
     spawn and they get some great items, so be it"

So the scope is SETTLED AND MAXIMAL: every Toxeus creature record goes on
`genericbossorb_05`. Two consequences are deliberate and must not be "fixed":
  * `um_toxeus_21` is charLevel 25/45/65 and gets the Act-4 apex orb anyway. The
    balance objection was raised and **OVERRULED WITH REASONS** (he has no fixed
    spawn - he is a `nameChampion` roll in 6 Act-1/Act-2 undead pools - so
    meeting him is already a lucky accident and Will would rather reward the
    accident than protect the curve). Do NOT quietly scale him to a lesser tier
    "in the spirit of" the ruling.
  * the two `zzdev` dev dummies are INCLUDED, not excluded. See THE ZZDEV PAIR.

WILL'S DECISION 2026-07-27 (verbatim, R-72), still in force for the calibre
---------------------------------------------------------------------------
    "increase the tier of the items dropped by leinth's orb to match the tier
     dropped by the champions' orb and give that to both toxeus variants and
     also to leinth"

So this is NOT "raise the champions to Leinth". It is: build ONE apex drop that
combines Leinth's GENEROSITY (quantity) with the champions' TIER (item pool), and
give that single calibre to everyone on it. Leinth is INCLUDED and UPGRADED,
never nerfed and never left behind. R-99 changes WHO is on the orb; it does not
re-tune the orb ("more items than the normal champions" is already satisfied by
the calibre: 21.16 modelled expected items vs orb04's 5.70).

THE ROSTER, AND WHY IT IS DERIVED AND NOT TYPED (the R-99 lesson)
-----------------------------------------------------------------
b94 wired the two FOUGHT champions from a hand-typed pair. b98 built the Endless
Hunt in a parallel lane. Neither lane owned the other's half of the roster, so
the third champion - the one Will has actually fought in play - shipped with NO
`treasureProxyName` at all and nobody noticed for two waves. A hand-typed list is
what caused that, so this module derives its roster from the live database:

    toxeus_roster(db) = every record whose PATH contains 'toxeus'
                        AND whose templateName is database\templates\monster.tpl

measured on the R-99 BUILT arz `6a3a491db546b603c52132237c40aa63` (51,124 records),
against the tip baseline `aea688b23acefe1b48ae31a0df4cc423` (a build of `main`,
51,124 records, made in the same environment) - NOT on the round-1 md5
`967b1f97...`, which was a 44-module PRE-merge build the gate record disowns as a
baseline of the tip. That predicate returns EXACTLY these 8 records - the roster
R-99 enumerates, with nothing missing and nothing extra:

    record                                     charLevel   BEFORE R-99
    um_toxeus_enslaver_99  (Enslaver of Souls) 40/68/100   genericbossorb_05
    um_bloodtoxeus_99      (Devourer of Blood) 40/68/100   genericbossorb_05
    um_toxeus_hunt_99      (the Endless Hunt)  40/68/100   NONE  <- the gap
    um_toxeus_hunt_l_99    (endless variant)   40/68/100   NONE  <- the gap
    um_toxeus_99           (SP Toxeus, Hero)   33/66/99    NONE
    um_toxeus_21           (Athens, Boss)      25/45/65    genericbossorb_01
    z_toxeus               (zzdev dummy)       40/56/71    NONE
    old_z_toxeus           (zzdev dummy)       40/56/71    NONE

TWO INDEPENDENT CROSS-CHECKS run inside the gate, so the predicate cannot rot:

 1. PINNED ALLOW-LIST. `ROSTER_PINNED` names all 8. The derived set is asserted
    EQUAL to it. A new `um_toxeus_*` variant therefore REDS THE BUILD (with a
    message telling the next lane to ratify it) instead of being silently
    dropped, which is the precise failure this ruling exists to close.
 2. NAME-TAG DERIVATION. The roster is re-derived a second way - every record
    on ANY template EXCEPT `Pet.tpl` whose `description` is one of the roster's
    four display tags - and the two derivations are diffed. This catches a Toxeus
    authored OUTSIDE the `toxeus` path namespace **that REUSES one of the four
    roster display tags**, including one minted on a bespoke boss template rather
    than Monster.tpl (this scan used to filter on Monster.tpl, and planted
    negative R3 proved that filter made it hollow for exactly that case - the R3
    donor is a `Typhon2.tpl` boss). Widening it was measured to add ZERO hits in
    the live db. Pet.tpl stays excluded on purpose: the nine Toxeus summon pets
    are out of roster scope by design and carry their own `*Pet` tags, so a lane
    naming a summon after its master must not red the build.

    ⚠️ EXACT RESIDUAL BOUND OF THIS CROSS-CHECK, MEASURED - do not overclaim it.
    Because the tag set is built FROM the path-derived roster, a Toxeus authored
    outside the `toxeus` namespace that ALSO invents a brand-new display tag is
    invisible to BOTH derivations. Measured on the real built arz by planting the
    two distinguishable cases (a clone outside the namespace, orb04, given first
    a roster tag and then a new one):
        outside namespace + REUSES `tagMonsterHemorrheus`  -> gate=FAIL  (caught)
        outside namespace + new `tagSVCMonsterToxeusR2Bound` -> gate=PASS (BLIND)
    The blind spot is EMPTY today, checked three independent ways over all 51,124
    records: zero records outside the namespace carry a `*toxeus*` controller,
    zero wear a `*toxeus*` soul in any `lootFinger2Item*` slot, and zero point at
    `genericbossorb_05`. Registered as `BL-b101-DEBT-8`. Closing it would need a
    THIRD derivation keyed on something a new variant cannot rename away (the
    controller or the soul it wears); that is deliberately not attempted here
    because it is out of R-99's scope and would be an unmeasured widening.
    The tag derivation legitimately returns 2 extra base-game records
    (`am_assassin_04`, `am_assassin_06`): they are charLevel 4/6 Act-1 Common
    "Desecrated Dead Assassin" skeletons that merely REUSE the base-game text tag
    `tagMonsterName190`. They carry no Toxeus controller, no boss/hero rank, no
    soul and no orb, so they are NOT Toxeus and are pinned as known false
    positives in `_TAG_FALSE_POSITIVES`. Any THIRD tag-only hit reds the build.

WHAT IS DELIBERATELY *NOT* IN THE ROSTER, and why (stated so a later reader does
not "fix" it): the nine `Pet.tpl` records `toxeus_enslaver_{1,2,3}`,
`bloodtoxeus_{1,2,3}` and `toxeus_eoat_{1,2,3}`. Those are the player's SUMMONED
Toxeus pets, not encounters - a pet has no death loot to give - and beyond design
it is a CRASH RISK: `treasureProxyName` is a Monster.tpl loot field, and this
repo's hardest-won lesson (CLAUDE.md) is that copying ANY equipment/loot field
from Monster.tpl onto Pet.tpl crashes the game. The `templateName == monster.tpl`
half of the predicate is load-bearing for exactly that reason, not decoration.

THE ONE `Monster.tpl` NEIGHBOUR A READER WILL ASK ABOUT, so it is answered here
rather than left to look like an oversight: `um_enslaver_marauder_99` sits in the
SAME `records\creature\monster\shadowstalker\` folder as three roster champions
(`um_toxeus_enslaver_99`, `um_toxeus_hunt_99`, `um_toxeus_hunt_l_99`), is a
`Monster.tpl` record, and carries NO `treasureProxyName`. Excluding it is CORRECT
and is not an accident of the path predicate: its tag `tagSVCMonsterEnslaverMarauder`
resolves in `apply_svc_patches.py` to `'{^r}Enslaved Shadow Marauder'` and its own
constant there is commented `# hostile Champion` - it is the Enslaver's SUMMONED
minion, a Champion-rank add, not a Toxeus variant and not an uber encounter. It
has no `toxeus` path token and does not wear a roster display tag, so both
derivations agree it is out, which is the right answer. (Measured folder-by-folder
over every folder containing a roster record; nothing else in any of them is
Toxeus-adjacent.)

⚠️ BUILD-ORDER FACT THAT LOOKS LIKE A BUG AND IS NOT. `um_toxeus_hunt_l_99` does
not exist when this module's `apply()` runs: it is authored later in the registry
by `toxeus_hunt_endless` (registered AFTER this module) as a clone of the FINAL
`um_toxeus_hunt_99` with exactly ONE field changed (`controller`), an invariant
that module asserts itself. So the endless variant INHERITS `genericbossorb_05`
by construction - the identical mechanism `toxeus_souls_100` relies on for the
100% soul. `apply()` therefore tolerates its absence (`ROSTER_DEFERRED`) while
`verify()`, which runs over the FINAL merged db, requires it present and on
orb05. If the registry order ever changes, `verify()` fires.

THE CALIBRE FINDING (ground truth, all records scanned)
-------------------------------------------------------
`treasureProxyName` is the ONLY field in the whole DB that ever points at an orb.
The two b94 champions -

    records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr
    records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr

- both pointed at `genericbossorb_04`, the shared generic apex orb (R-47). Leinth
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

THE CONSTRAINT THAT SHAPES THE WHOLE DESIGN
-------------------------------------------
`genericbossorb_04` was shared by TWENTY-ONE boss records (Sarkoth, Vashkarr,
Bloodcrow, Voranthys, Broodmother, Enslaver, Gorrahk, Ilsevar, Dagon, Ephialtes,
Mnemophage-core, Antaeus, Polis Gaoler, Deep Thresher, Meglograi, bloodcrow_soul,
Dorus, Tantalus, Hades Marshal, Helepolis, Devourer). Editing it IN PLACE would
silently buff twenty-one encounters and rewrite the mod's whole endgame economy -
which is precisely the fear R-99 opens with ("i didnt tell you to increase the
drop of all the champions"). So the roster gets a NEW un-named generic apex tier
(orb05) and orb04 keeps serving its other 19 consumers byte-unchanged.

R-99 adds a SECOND donor tier to protect for the same reason: `um_toxeus_21` is
leaving `genericbossorb_01`, which has 11 consumers. Its other 10 (Elephant
Snatcher, Mormo, Kaublasia, Calybe x2, Rakanizeus x2, Melalos x3) must stay
exactly where they are. The blast-radius proof is therefore DERIVED rather than
written against orb04 by name: `apply()` snapshots every orb any roster record is
leaving, and proves each one is byte-unchanged and loses EXACTLY the roster
records that left it and nothing else.

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

WHAT IT CHANGES (1 field on each roster record + 2 fields x 3 Leinth chests)
----------------------------------------------------------------------------
THE TOXEUS ROSTER (7 records at apply() time, 8 in the shipped db) - every one
moves onto the new generic apex tier, `treasureProxyName -> genericbossorb_05`:
    um_toxeus_enslaver_99   (was genericbossorb_04, moved by b94)
    um_bloodtoxeus_99       (was genericbossorb_04, moved by b94)
    um_toxeus_hunt_99       (had NO orb field at all - R-99's headline fix)
    um_toxeus_99            (had NO orb field at all)
    um_toxeus_21            (was genericbossorb_01 - the OVERRULED balance call)
    z_toxeus                (had NO orb field at all - zzdev, see below)
    old_z_toxeus            (had NO orb field at all - zzdev, see below)
    um_toxeus_hunt_l_99     (inherited from the Hunt by the later clone, above)

Five of those records have no `treasureProxyName` field at all before this
module, so the write ADDS the field (`DATA_TYPE_STRING`, the
`_amend_boss_loot_orbs` idiom); on the three that already carry it the value is
overwritten with no dtype argument (the cloned-record dtype trap).

THE ZZDEV PAIR - PLACEMENT MEASURED, NOT ASSUMED (R-99 required this)
---------------------------------------------------------------------
⚠️ CORRECTED 2026-07-29 (b101 round 2). An earlier version of this docstring said
`z_arthur` had "0 placements, so the chain is unreachable in the shipped map".
**THAT WAS WRONG**, and it was wrong in the direction that matters. It came from a
ONE-HOP census; re-measuring with the multi-hop walk found the placement. The
claim is corrected here rather than quietly dropped, because a stale comment in
this exact module is what sent two earlier lanes wrong.

Both are Iron Lore dev leftovers (`FileDescription = "SPAWNED ON ARTHUR DEATH"`,
Champion rank, charLevel 40/56/71, `dropItems = 0`). MEASURED against the shipped
`Levels.arc` (`fc0adcc0713839a685b32d6e122653be`, 2,282 levels walked, 0 unparsed
`0x05` sections, 17,348 distinct placed paths / 491,885 instances indexed) and the
built db:
  * `old_z_toxeus`: 0 static `0x05` placements, 0 db referrers, no placed ancestor
    within 3 hops -> genuinely INERT. Its orb can never fire in this map.
  * `z_toxeus`: 0 static placements of its OWN, but it IS REACHABLE at hop 1.
    Its single db referrer is
    `records\xpack\creatures\monster\zzdev\z_arthur.dbr .actorToSpawnOnDeath`, and
    `z_arthur` **IS STATICALLY PLACED** - exactly ONE `0x05` instance, in
    `XPack\Levels\Area01_Rhodes\Undergrounds\ScrabledEggs_Floor06.lvl`. `z_arthur`
    is a `Monster.tpl`, `monsterClassification = Quest`, charLevel 40/56/71 record
    (`FileDescription = "Satyr"`). So killing that one placed z_arthur spawns
    z_toxeus, and z_toxeus now drops the Act-4 apex orb.
    HONEST LIMIT OF THIS FINDING: static placement proves the record is IN the
    level, NOT that a player can walk to it or that the engine spawns it. Whether
    that Rhodes underground spot is player-reachable is LAUNCH-GATED and is
    registered as debt - it is not claimed here either way.
Both carry `dropItems = 0`, so neither drops equipped gear. The orb is the
separate `treasureProxyName` mechanism, and the SHIPPED DB CORROBORATES that the
two are independent rather than this being an engine assumption: scanning all
51,124 records, EXACTLY FIVE `Monster.tpl` records combine `dropItems == 0` with a
`treasureProxyName`, and three of them are `q_leinth_47/49/50` -> the bespoke
`bosschestproxy_leinth`, i.e. a shipped, gate-proven, PLAYER-FACING drop that this
very module protects with fourteen planted negatives. (The other two are the zzdev
pair this lane just wired. 63 `Monster.tpl` records carry a proxy in total.) So a
`dropItems = 0` record demonstrably still gets its treasure proxy honoured in this
mod's own live content. HONEST LIMIT: that is DB-side corroboration by precedent,
not an in-game observation - nothing in this lane was launched, and whether the
orb visibly drops on kill remains launch-gated (`BL-b101-DEBT-3`/`-5`). This
matters because it sets the severity of `BL-b101-DEBT-2`: if `dropItems = 0` also
suppressed the proxy, z_toxeus's apex orb would be inert and the Will-decision
item would be moot. So the honest summary is "one of the two is inert, the other
is live-but-obscure", NOT "both inert".
R-99 pre-authorised this outcome in Will's own words - "if some good items drop
since someone got lucky ... so be it" - and included them explicitly, so the
finding is recorded rather than acted on. Neither is deleted, retired, blanked or
renamed (RETIREMENT PROTOCOL): code-unreferenced is not proof of dead, and this is
a Will-ratified inclusion, not a cleanup.

ALSO MEASURED, and NOT a zzdev record: `um_toxeus_99` (the inherited SP Toxeus,
Hero, 33/66/99) has 0 static placements, 0 db referrers and NO placed ancestor
within 3 hops - it is as inert as `old_z_toxeus` in this map. Its orb is wired per
R-99 ("all versions") and is simply dormant until something places or pools him.
Registered as debt so it is a known dormancy, not a silent one.

Re-measure everything above with
`py tools/debug/b101_toxeus_placement_census.py <built.arz> <Levels.arc>`.

LEINTH (3 records, 2 fields each) - her SOLE-OWNED chests are upgraded IN PLACE
to the SAME apex tables, so all three bosses share one identical calibre:
    bosschest_leinth_01_normal   .tables            -> svc_uberorb_apex_n01c
                                 .levelEquationFile -> containerlevelequation_all
    bosschest_leinth_02_epic     .tables            -> svc_uberorb_apex_e01c
                                 .levelEquationFile -> containerlevelequation_all
    bosschest_leinth_03_legendary.tables            -> svc_uberorb_apex_l01c
                                 .levelEquationFile -> containerlevelequation_all

Leinth's monster records are NOT touched at all: `treasureProxyName` still names
her own `bosschestproxy_leinth`, so R-73's "her bespoke chest survives" guarantee
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

R-48 / R-91 ARE UNTOUCHED AND UNTOUCHABLE HERE
-----------------------------------------------
Souls are Finger2 EQUIPMENT (`lootFinger2Item1` + `chanceToEquipFinger2`); orbs
are `treasureProxyName`. Fully independent mechanisms. apply() nevertheless
snapshots the three soul fields on EVERY roster record before and after its own
writes and fails loud if any of them moved, so neither the three fought champions'
100% (R-48 + R-91) nor `um_toxeus_99`'s 66 nor `um_toxeus_21`'s 50 can ever become
collateral damage. verify() re-asserts the literal 100.0 on the three fought
champions by name, because those are the numbers the rulings state.

RULINGS
-------
⚠️ **"R-72" IS AMBIGUOUS IN THE LEDGER - THERE ARE TWO.** Every "R-72" in this
module means the one ledgered `IMPLEMENTED b94 (feat/leinth-wave)`, the ORB
CALIBRE ruling ("the orb the two Toxeus champions drop is not the same calibre as
the one Leinth drops"). The OTHER R-72, ledgered `IMPLEMENTED b96
(feat/vashkarr-soul)`, is Vashkarr's spear-and-shield SOUL retune and has nothing
to do with orbs. The collision is pre-existing, is not this lane's to renumber, and
is registered as `BL-b101-DEBT-1`; this note exists so a reader who lands on the
wrong one is not sent down the wrong ruling.

R-47 mandates the un-named generic apex orb (`genericbossorb_04`), explicitly NOT
a bespoke "X's Essence" per boss. genericbossorb_05 keeps R-47's substance intact
(un-named, generic, shared by the whole Toxeus roster, no NEW bespoke essence
authored) but adds a TIER the ruling does not mention -> ledgered as R-72 in
docs/WILL_RULINGS.md; R-99 then widened WHO sits on that tier. Leinth's
pre-existing bespoke chest is neither created nor retired by this module, only
re-tiered, so R-47's "no bespoke essence per boss" prohibition (which is about
AUTHORING new ones) is not engaged.
Down-tiering the champions onto Leinth's Act-3 63-65 band was REJECTED (it lowers
their item level, the opposite of Will's instruction). Repointing Leinth at the
generic orb was also REJECTED once sole-ownership was proven: it would silently
destroy her "Leinth's Essense" name and her chest mesh for no mechanical gain,
and the brief explicitly authorised the in-place upgrade on that proof.
Scaling `um_toxeus_21` down to a lesser tier was REJECTED BY WILL EXPLICITLY, on
reasons recorded in R-99. Excluding the zzdev pair was REJECTED BY WILL EXPLICITLY
("all versions" is unambiguous).

GATE
----
verify() runs in registry step 4 over the FINAL merged db and fails the build loud
unless (a) the DERIVED Toxeus roster equals `ROSTER_PINNED` exactly, every member
carries treasureProxyName=genericbossorb_05, and the set of orb05 carriers is
EXACTLY that roster (nothing non-Toxeus crept onto the apex tier - R-47/R-99's
"not all champions" guarantee), plus the second, name-tag-based derivation agrees
modulo the two pinned base-game false positives; (b) the whole orb05 chain
resolves end to end on all 3 difficulties; (c) orb05's four knobs are >= Leinth's
ORIGINAL chest's on every difficulty; (d) every DONOR tier a roster record left
(genericbossorb_04 and genericbossorb_01) still exists, still carries no roster
record, and still serves at least its remaining consumers, with the orb04 donor
chain untouched; (e) the three fought champions still carry their R-48/R-91 100%
soul drop; (f) all THREE of Leinth's chests resolve to the same apex tables +
level equation the roster uses; (g) her bespoke identity fields
(mesh/scale/description/goldGenerator) are intact and all three of her monster
records still name her own proxy; and (h) the apex table is >= her ORIGINAL table
on every one of the six loot-group chances and on goldGeneratorLevel (the no-nerf
proof, computed rather than asserted). Her three original loot tables are
deliberately LEFT IN THE DB (retirement protocol) and are what (c) and (h) read as
the live reference. Planted negative tests:
tools/debug/negtest_uber_apex_orb.py. Placement census:
tools/debug/b101_toxeus_placement_census.py.
See docs/reports/b94_leinth_wave.md and docs/reports/b101_toxeus_apex_roster.md.
"""
import apply_svc_patches as asp
from arz_patcher import DATA_TYPE_STRING

MODULE_NAME = ("uber apex orb - ONE apex drop calibre for the WHOLE Toxeus roster "
               "AND Leinth (R-72 + R-99)")

# ── the two b94 champions (sourced from the monolith so an upstream rename can
# never silently desync this module's scope, exactly as toxeus_souls_100 does).
# These are NO LONGER the scope - see ROSTER_PINNED - but they are still named
# individually because the R-48 100% soul assertion is stated about them by name.
_ENSLAVER = asp._EN_BOSS      # records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr
_DEVOURER = asp._BT_MONSTER   # records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr
_HUNT = r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr'
_HUNT_L = r'records\creature\monster\shadowstalker\um_toxeus_hunt_l_99.dbr'
_SP_TOXEUS = r'records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr'
_TOXEUS_21 = r'records\creature\monster\skeleton\um_toxeus_21.dbr'
_Z_TOXEUS = r'records\xpack\creatures\monster\zzdev\z_toxeus.dbr'
_OLD_Z_TOXEUS = r'records\xpack\creatures\monster\zzdev\old_z_toxeus.dbr'

_CHAMPIONS = (
    ('Toxeus the Murderer, Enslaver of Souls', _ENSLAVER),
    ('Toxeus the Murderer, Devourer of Blood', _DEVOURER),
)

# The three FOUGHT champions whose souls R-48 (+ R-91) put at 100%. Asserted by
# name in verify() (e) because the rulings state the number about these records.
_SOUL_100_CHAMPIONS = (
    ('Toxeus the Murderer, Enslaver of Souls', _ENSLAVER),
    ('Toxeus the Murderer, Devourer of Blood', _DEVOURER),
    ('Toxeus the Murderer, the Endless Hunt', _HUNT),
)

# ── R-99 ROSTER ──────────────────────────────────────────────────────────────
# The roster is DERIVED (toxeus_roster) and only CHECKED against this pin. The
# pin exists so a NEW Toxeus variant reds the build instead of being silently
# dropped - which is exactly how the Endless Hunt shipped orb-less for two waves.
ROSTER_PINNED = (
    _ENSLAVER,      # Toxeus the Murderer, Enslaver of Souls   40/68/100
    _DEVOURER,      # Toxeus the Murderer, Devourer of Blood   40/68/100
    _HUNT,          # Toxeus the Murderer, the Endless Hunt    40/68/100
    _HUNT_L,        # ... his Legendary endless pursuit variant
    _SP_TOXEUS,     # SP Toxeus (Hero, inherited)              33/66/99
    _TOXEUS_21,     # Athens Toxeus (Boss, inherited)          25/45/65
    _Z_TOXEUS,      # Iron Lore zzdev dummy                    40/56/71
    _OLD_Z_TOXEUS,  # Iron Lore zzdev dummy                    40/56/71
)

# Authored LATER in the registry (by toxeus_hunt_endless, a clone of the FINAL
# _HUNT record), so it cannot exist when apply() runs and MUST exist by verify().
ROSTER_DEFERRED = (_HUNT_L,)

# The derivation predicate, spelled out so the gate messages can quote it.
_ROSTER_TOKEN = 'toxeus'
_MONSTER_TPL = 'templates\\monster.tpl'
# The second (name-tag) derivation scans EVERY template except this one - see
# _roster_by_name_tag for why the exclusion is Pet.tpl and nothing else.
_PET_TPL = 'templates\\pet.tpl'

# Base-game records that share a Toxeus display tag but are NOT Toxeus: charLevel
# 4/6 Act-1 Common "Desecrated Dead Assassin" skeletons
# (ActorName Greece_Creature_Monster_Skeleton_DesecratedDeadAssassin01) that
# merely reuse the base-game text tag tagMonsterName190. No Toxeus controller, no
# Hero/Boss rank, no soul, no orb. Pinned so the second derivation can subtract
# them and still fire on a THIRD, genuinely new tag-only hit.
_TAG_FALSE_POSITIVES = (
    r'records\creature\monster\skeleton\quest\am_assassin_04.dbr',
    r'records\creature\monster\skeleton\quest\am_assassin_06.dbr',
)

_TREASURE = 'treasureProxyName'

# ── the donor chain (orb04) and the new chain (orb05) ─────────────────────────
_NEW = 'records\\item\\containers\\new\\'
_LOOT = 'records\\item\\loottables\\svc\\'
_XLOOT = 'records\\xpack\\item\\containers\\loot tables\\'

ORB01 = _NEW + 'genericbossorb_01.dbr'
ORB04 = _NEW + 'genericbossorb_04.dbr'
ORB05 = _NEW + 'genericbossorb_05.dbr'

# The tiers a roster record LEAVES, with the number of consumers that must still
# be on each one afterwards. FLOORS, not equalities: a later lane may legitimately
# ADD a consumer to a generic tier, but nothing here may ever strip one.
# MEASURED on the TIP BASELINE aea688b23acefe1b48ae31a0df4cc423 (a fully gated
# exit-0 build of `main`, 51,124 records, 55,475,172 B, made in this environment),
# and re-confirmed at apply time inside the real 45-module build:
#   genericbossorb_04: 21 consumers, the 2 b94 champions left  -> 19 remain
#   genericbossorb_01: 11 consumers, um_toxeus_21 leaves (R-99) -> 10 remain
# The baseline build's own log prints the orb04 half verbatim:
#   "scope proof: orb04 chain byte-unchanged; consumers 21 -> 19 (the 2 champions
#    moved to orb05)".
# ⚠️ DO NOT re-cite 967b1f97137bf6479c18c08e9dd6ffc4 here. These same two numbers
# reproduce on it, but it is a 44-MODULE PRE-merge build (its log reads
# "[37/44] uber_apex_orb" and never reaches weapon_gate_truth), so the BACKLOG gate
# record disowns it as a baseline of the tip. Citing a disowned artifact as a
# measurement basis is how a stale number outlives the build that produced it.
DONOR_TIER_FLOORS = {
    ORB04: 19,
    ORB01: 10,
}

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
# The two multipliers, split out so R-240's era check can trim them through the same
# transform the trim itself uses instead of re-typing 2.2/2.4 in a second place.
# Parsed from the equations above so the pair can never disagree with them.
LEINTH_MIN_MULT = float(LEINTH_MIN_EQ.rsplit('*', 1)[1])
LEINTH_MAX_MULT = float(LEINTH_MAX_EQ.rsplit('*', 1)[1])
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


def _norm(p):
    return str(p).replace('/', '\\').lower()


def _consumers_of(db, orb):
    """Every record pointing treasureProxyName at `orb` (case/slash tolerant)."""
    low = _norm(orb)
    return sorted(n for n in db.record_names()
                  if isinstance(_v1(db, n, _TREASURE), str)
                  and _norm(_v1(db, n, _TREASURE)) == low)


def _orb04_consumers(db):
    """Every record still pointing treasureProxyName at genericbossorb_04."""
    return _consumers_of(db, ORB04)


# ── R-99: THE DERIVED ROSTER ─────────────────────────────────────────────────
def toxeus_roster(db):
    """Every Toxeus CREATURE record in the LIVE db, derived - never typed.

    Predicate: record path contains 'toxeus' AND templateName is Monster.tpl.

    Both halves are load-bearing:
      * the path token is what makes this find a variant a future lane adds
        without telling this module (the Endless Hunt failure);
      * the Monster.tpl half is what keeps the nine `Pet.tpl` Toxeus summon pets
        (toxeus_enslaver_{1,2,3}, bloodtoxeus_{1,2,3}, toxeus_eoat_{1,2,3}) out.
        A pet has no death loot, and `treasureProxyName` is a Monster.tpl LOOT
        field - writing one onto Pet.tpl is the documented CRASH trap in
        CLAUDE.md, not merely a design mistake.

    Sorted, so every message and every proof table is order-stable.
    """
    out = []
    for n in db.record_names():
        if _ROSTER_TOKEN not in n.lower():
            continue
        tpl = _v1(db, n, 'templateName')
        if isinstance(tpl, str) and _norm(tpl).endswith(_MONSTER_TPL):
            out.append(n)
    return sorted(out)


def _roster_by_name_tag(db, roster):
    """SECOND, independent derivation: records whose `description` is one of the
    display tags the path-derived roster uses, on ANY template except Pet.tpl.

    This is the derivation that catches a Toxeus authored OUTSIDE the 'toxeus'
    path namespace **that REUSES one of the roster's display tags**, which the
    path predicate alone cannot see.

    ⚠️ SCOPE IT HONESTLY. The tag set below is built FROM the path-derived roster,
    so this cross-check cannot see a Toxeus that is outside the namespace AND
    invents a NEW display tag. Measured, not assumed: a clone outside the
    namespace on `genericbossorb_04` reds the gate when given `tagMonsterHemorrheus`
    and stays GREEN when given a fresh `tagSVCMonsterToxeusR2Bound`. That blind
    spot is empty today (0 records outside the namespace carry a toxeus
    controller, a toxeus soul, or orb05, over all 51,124 records) and the residual
    bound is registered as `BL-b101-DEBT-8`.

    IT DELIBERATELY DOES **NOT** FILTER ON Monster.tpl, and that is a FIX, not an
    oversight. It used to, and planted negative R3 proved the filter made the
    whole cross-check hollow for the case that matters most: a boss authored on a
    BESPOKE template. The R3 donor `boss_titan_typhon_42` is
    `database\\Templates\\Typhon2.tpl`, so a Monster.tpl-filtered scan skipped it
    and the gate stayed green while wearing a champion's display tag. Every one of
    this mod's own uber bosses could likewise be minted on a bespoke boss
    template. Widening the scan was MEASURED to add ZERO hits in the live db
    (the only carriers of the four roster tags are the 8 roster records plus the 2
    pinned am_assassin false positives, all Monster.tpl), so this strictly
    strengthens the gate without risking a false red.

    Pet.tpl IS excluded, for a stated reason rather than by accident: the nine
    Toxeus summon pets are deliberately out of roster scope (a pet has no death
    loot, and `treasureProxyName` on Pet.tpl is the documented CRASH trap), and
    they legitimately carry their OWN `*Pet` display tags
    (`tagMonsterHemorrheusPet`, `tagSVCMonsterEnslaverPet`,
    `tagMonsterToxeusEoATPet` - measured). A future lane naming a summon after its
    master is normal content work and must not red the build.
    """
    tags = {_v1(db, r, 'description') for r in roster}
    tags.discard(None)
    out = []
    for n in db.record_names():
        tpl = _v1(db, n, 'templateName')
        if isinstance(tpl, str) and _norm(tpl).endswith(_PET_TPL):
            continue
        if _v1(db, n, 'description') in tags:
            out.append(n)
    return sorted(out), sorted(tags)


def _roster_problems(db, phase):
    """Derive the roster and check it against the pin. Returns (roster, problems).

    `phase` is 'apply' (the deferred endless variant does not exist yet) or
    'verify' (the FINAL db - everything must be present).
    """
    roster = toxeus_roster(db)
    pinned = {_norm(r) for r in ROSTER_PINNED}
    deferred = {_norm(r) for r in ROSTER_DEFERRED}
    got = {_norm(r) for r in roster}
    problems = []

    extra = sorted(got - pinned)
    if extra:
        problems.append(
            "DERIVED a Toxeus creature record that is NOT in ROSTER_PINNED: %s. "
            "R-99 says every Toxeus variant gets genericbossorb_05, so this is "
            "either a new variant that must be ADDED to ROSTER_PINNED (and its "
            "orb ratified) or a false positive that must be excluded EXPLICITLY. "
            "The build reds rather than silently dropping it - that silence is "
            "exactly how the Endless Hunt shipped with no orb." % extra)

    missing = sorted(pinned - got)
    if phase == 'apply':
        # the endless variant is authored later in the registry, by design
        missing = sorted(set(missing) - deferred)
    if missing:
        problems.append(
            "ROSTER_PINNED record(s) MISSING from the db at %s time: %s. A "
            "pinned Toxeus variant vanishing is a rename or a deletion, and "
            "either way the roster this module enforces is no longer the roster "
            "R-99 ratified." % (phase, missing))

    # second derivation - the name-tag cross-check
    by_tag, tags = _roster_by_name_tag(db, roster)
    unexpected = sorted(set(_norm(r) for r in by_tag)
                        - got - {_norm(r) for r in _TAG_FALSE_POSITIVES})
    if unexpected:
        problems.append(
            "a Monster.tpl record carries a Toxeus display tag %s but is NOT in "
            "the path-derived roster and is NOT a pinned base-game false "
            "positive: %s. If it is a Toxeus variant authored outside the "
            "'toxeus' path namespace it must join ROSTER_PINNED; if it is "
            "another base-game tag reuse it must join _TAG_FALSE_POSITIVES with "
            "the evidence written down." % (tags, unexpected))
    return roster, problems


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


def _calibre_era(db, apex_table, diff):
    r"""'pre-R-240' | 'R-240' | None - which committed calibre this apex table carries.

    ⚠ ADDED BY R-240/R-241 (Will 2026-08-11). See `_post_wave_problems` and the
    docs/WILL_RULINGS.md entry "R-241 SUPERSEDES the absolute-floor half of R-72/R-99"
    before touching this. The era is DERIVED through R-240's own transform, so this
    function and the trim cannot drift apart.
    """
    import sys as _sys
    from pathlib import Path as _Path
    _t = _Path(__file__).resolve().parent.parent
    if str(_t) not in _sys.path:
        _sys.path.insert(0, str(_t))
    import svc_loot_volume as SLV
    lo_eq = _v1(db, apex_table, 'numSpawnMinEquation')
    hi_eq = _v1(db, apex_table, 'numSpawnMaxEquation')
    p = SLV.parse_eq(lo_eq)
    if p is None:
        return None
    bracket = p[0]
    got = (_mult(lo_eq), _mult(hi_eq))
    if got == (LEINTH_MIN_MULT, LEINTH_MAX_MULT):
        return 'pre-R-240'
    tier = _SHORT[diff]
    want = SLV.trimmed_multipliers(bracket, LEINTH_MIN_MULT, LEINTH_MAX_MULT, tier)[:2]
    if got == want:
        return 'R-240'
    return None


def _post_wave_problems(db, apex_table, leinth_table, diff):
    r"""The R-72/R-99 calibre proof, AS AMENDED BY R-240 + R-241 (Will 2026-08-11).

    WHY THIS FUNCTION EXISTS AT ALL - read this before "simplifying" it away.

    R-72/R-99 (Will 2026-07-27) put the whole Toxeus roster AND Leinth on ONE apex
    drop calibre, and `_no_nerf_problems` proves it by comparing the apex tables
    against Leinth's own frozen reference tables (loottable_leinth_{29-31,49-51,63-65},
    deliberately never written per the retirement protocol). That proof has TWO halves
    braided together, and R-241 cuts exactly one of them:

      UNITY   - Leinth sits on the SAME tables as the roster; she is never singled out
                and never left behind. THIS SURVIVES R-241 COMPLETELY. Will lowered the
                shared calibre for everyone including her, which is the opposite of
                singling her out. It is still asserted, in two places: verify() (g)
                proves her three chests point at `CHAIN[d][5]`, and P3 below re-proves
                that the table those chests reach is the very table this function was
                handed, so the two checks cannot pass while pointing at different
                records.

      ABSOLUTE - the apex calibre is never numerically below her b96-era frozen
                numbers. THIS IS WHAT R-241 SUPERSEDES, and it is superseded by Will's
                own words: "you made the orbs way too good... those dont need to have
                guaranteed legendary drops, they should just have a chance to drop
                legendary items, but a low chance." An absolute floor pinned to
                *2.2/*2.4 and loot4Chance 100.0 is precisely the vending machine he is
                describing, so it cannot also be the law that forbids fixing it.

    A LANE MAY NOT QUIETLY DELETE ANOTHER RULING'S PROOF, so the supersession is
    written down (docs/WILL_RULINGS.md, R-241's entry, with this collision named) and
    the check is REPLACED rather than dropped. What replaces it is strictly more
    specific: instead of ">= a floor", the post-wave era asserts "== the committed
    R-240/R-241 value, re-derived every run", so drift in EITHER direction reds. The
    old proof is not deleted from the codebase either - `_no_nerf_problems` still runs
    verbatim at apply() time (the migration guard, where R-240/R-241 have not yet run
    and her frozen tables are still the right comparand), and still runs verbatim here
    whenever the arz is pre-R-240, which is what keeps the ship lane's rollback-artifact
    control meaningful (BL-R240-DEBT-8).

    THE AXES R-241 DOES NOT TOUCH ARE STILL PROVED AGAINST HER ORIGINALS: gold, and
    every loot group chance except the ones R-241's census named for demotion. A trim
    lane gets to lower the two things Will pointed at and nothing else.
    """
    import sys as _sys
    from pathlib import Path as _Path
    _t = _Path(__file__).resolve().parent.parent
    if str(_t) not in _sys.path:
        _sys.path.insert(0, str(_t))
    import svc_loot_volume as SLV
    import svc_orb_legendary as SOL

    problems = []
    if not (db.has_record(apex_table) and db.has_record(leinth_table)):
        return ["%s: cannot run the calibre proof (apex or Leinth table missing)" % diff]

    era = _calibre_era(db, apex_table, diff)
    if era is None:
        lo_eq = _v1(db, apex_table, 'numSpawnMinEquation')
        hi_eq = _v1(db, apex_table, 'numSpawnMaxEquation')
        tier = _SHORT[diff]
        p = SLV.parse_eq(lo_eq)
        want = (SLV.trimmed_multipliers(p[0], LEINTH_MIN_MULT, LEINTH_MAX_MULT,
                                        tier)[:2] if p else ('?', '?'))
        return ["%s: apex %s carries numSpawn *%s/*%s, which is NEITHER the "
                "pre-R-240 shared calibre *%s/*%s NOR R-240's committed trim of it "
                "*%s/*%s. One apex calibre for the whole roster and Leinth means one "
                "of two committed numbers, not a third one nobody chose."
                % (diff, apex_table, _mult(lo_eq), _mult(hi_eq),
                   LEINTH_MIN_MULT, LEINTH_MAX_MULT, want[0], want[1])]

    if era == 'pre-R-240':
        # Nothing has been trimmed yet: the ORIGINAL proof is exactly right, and is
        # what the rollback-artifact control needs to see. Run it verbatim.
        return _no_nerf_problems(db, apex_table, leinth_table, diff)

    # ── era == 'R-240': the amended proof ────────────────────────────────────
    # P1 - GOLD. Untouched by both rulings, so the original floor still stands.
    try:
        a = float(_v1(db, apex_table, 'goldGeneratorLevel') or 0)
        l = float(_v1(db, leinth_table, 'goldGeneratorLevel') or 0)
        if a + 1e-6 < l:
            problems.append("%s: NERF - apex goldGeneratorLevel %s < Leinth's %s "
                            "(R-240/R-241 authorise a VOLUME and a CHANCE cut, not a "
                            "gold cut)" % (diff, a, l))
    except (TypeError, ValueError):
        problems.append("%s: goldGeneratorLevel unreadable on one of the tables" % diff)

    # P2 - LOOT GROUP CHANCES. Still >= Leinth's original on every group R-241 did
    #      NOT name; == the committed R-241 target on the ones it did. The demoted
    #      set is read from R-241's own contract, not re-typed, so widening that
    #      contract widens this check automatically and narrowing it re-arms the
    #      original floor on the group that left.
    apex_c = _group_chances(db, apex_table)
    lein_c = _group_chances(db, leinth_table)
    for i, (a, l) in enumerate(zip(apex_c, lein_c), 1):
        want = SOL.FAMILY_CHANCE_EXPECTED.get(i)
        if want is not None:
            if abs(a - want) > max(SOL.FAMILY_CHANCE_TOL, 1e-6):
                problems.append(
                    "%s: apex loot%dChance %.4f, expected R-241's committed %.4f. This "
                    "is the row Will's ruling demoted (\"they should just have a chance "
                    "to drop legendary items, but a low chance\"); it may not drift back "
                    "up toward the old %.1f guarantee, and it may not be cut further by "
                    "a lane that never measured what that costs."
                    % (diff, i, a, want, l))
        elif a + 1e-6 < l:
            problems.append(
                "%s: NERF - apex loot%dChance %.2f < Leinth's original %.2f. R-241 "
                "demotes ONLY the rows its census named (%s); every other group still "
                "owes her the R-72/R-99 floor."
                % (diff, i, a, l,
                   ', '.join('loot%dChance' % g
                             for g in sorted(SOL.FAMILY_CHANCE_EXPECTED)) or 'none'))

    # P3 - UNITY, re-proved here rather than trusted from (g): the table Leinth's own
    #      chest reaches IS the table this proof was handed. Without this, (g) and this
    #      function could both be green while asserting about different records.
    chest = LEINTH_CHESTS.get(diff)
    if chest and db.has_record(chest):
        got = str(_v1(db, chest, 'tables') or '').replace('/', '\\').lower()
        if got != str(apex_table).replace('/', '\\').lower():
            problems.append(
                "%s: UNITY BROKEN - Leinth's chest reaches %r but the calibre proof was "
                "run against %r. R-241 lowers ONE shared calibre for everyone; the "
                "moment her chest and the roster's read different tables, a 'trim' has "
                "become the singling-out R-72/R-99 exists to forbid."
                % (diff, got, apex_table))
    return problems


def _no_nerf_problems(db, apex_table, leinth_table, diff):
    """Prove the apex table is >= Leinth's ORIGINAL on every reward axis.

    Returns a list of problem strings (empty == she is not nerfed). This is
    COMPUTED from the two records, never asserted in prose, so an upstream table
    change that would quietly cost her something fails the build.

    ⚠ STILL THE LAW AT APPLY() TIME, and on any PRE-R-240 arz. R-240/R-241 are
    registered LAST, so when apply() calls this the apex tables still carry the
    b96-era calibre and Leinth's frozen tables are the correct comparand - the
    migration this proof was written for is proved exactly as it always was. What
    changed is only the POST-wave reading; see `_post_wave_problems`.
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

    # ── R-99: DERIVE the roster and check it against the pin BEFORE anything ─
    roster, roster_problems = _roster_problems(db, 'apply')
    if roster_problems:
        raise SystemExit(
            "[uber_apex_orb] R-99 ROSTER DERIVATION FAILED at apply time:\n  - "
            + "\n  - ".join(roster_problems))
    print("  R-99 roster DERIVED from the db (path contains '%s' AND templateName "
          "is Monster.tpl): %d record(s), == ROSTER_PINNED minus the %d deferred "
          "clone(s)" % (_ROSTER_TOKEN, len(roster), len(ROSTER_DEFERRED)))

    # ── R-48/R-91 guard: snapshot the soul wiring on EVERY roster record ─────
    # Not just the two champions: um_toxeus_99 sits at 66 and um_toxeus_21 at 50,
    # and this module must not move those either. The proof is a diff, so it
    # covers rates it does not know the value of.
    soul_before = {}
    for rec in roster:
        soul_before[rec] = (
            _v1(db, rec, 'chanceToEquipFinger2'),
            db.get_field_value(rec, 'lootFinger2Item1'),
            _v1(db, rec, 'dropItems'),
        )

    # ── blast-radius snapshot: EVERY donor tier a roster record is leaving ───
    # DERIVED, not written against orb04 by name: R-99 moves um_toxeus_21 off
    # genericbossorb_01 as well, and orb01's other 10 consumers deserve the same
    # protection orb04's 19 get.
    donor_orbs = sorted({_norm(_v1(db, r, _TREASURE)) for r in roster
                         if isinstance(_v1(db, r, _TREASURE), str)
                         and _norm(_v1(db, r, _TREASURE)) != _norm(ORB05)})
    donor_consumers_before = {o: _consumers_of(db, o) for o in donor_orbs}
    donor_snapshot_before = _snapshot(db, [o for o in donor_orbs if db.has_record(o)])
    for o in donor_orbs:
        others = [c for c in donor_consumers_before[o]
                  if _norm(c) not in {_norm(r) for r in roster}]
        print("  donor tier to protect: %s - %d consumer(s), %d of them NOT Toxeus "
              "and staying put" % (o.rsplit('\\', 1)[-1],
                                   len(donor_consumers_before[o]), len(others)))

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

    # ── 5. repoint EXACTLY the DERIVED Toxeus roster (R-99) ─────────────────
    # Five of the eight records have no treasureProxyName field at all, so the
    # write ADDS it and needs the dtype; the three that already carry a string
    # get a value-only write (the cloned-record dtype trap in CLAUDE.md).
    added = moved = 0
    for rec in roster:
        prev = _v1(db, rec, _TREASURE)
        if prev is None:
            db.set_field(rec, _TREASURE, ORB05, DATA_TYPE_STRING)
            added += 1
            shown = 'NONE (field absent)'
        else:
            db.set_field(rec, _TREASURE, ORB05)
            if _norm(prev) != _norm(ORB05):
                moved += 1
            shown = str(prev).rsplit('\\', 1)[-1]
        db._modified.add(rec)
        print("  %-24s %s %-24s -> %s"
              % (rec.rsplit('\\', 1)[-1], _TREASURE, shown,
                 ORB05.rsplit('\\', 1)[-1]))
    print("  R-99: %d Toxeus record(s) on the apex orb (%d gained the field for "
          "the FIRST time, %d moved off a lower tier); the Legendary endless "
          "variant inherits it later from the Hunt by clone."
          % (len(roster), added, moved))

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
    # (i) R-48/R-91 soul wiring untouched on EVERY roster record, whatever rate
    #     each one carried (100 / 66 / 50 / 0). A diff, not a magic number.
    for rec in roster:
        now = (_v1(db, rec, 'chanceToEquipFinger2'),
               db.get_field_value(rec, 'lootFinger2Item1'),
               _v1(db, rec, 'dropItems'))
        if now != soul_before[rec]:
            raise SystemExit(
                "[uber_apex_orb] R-48/R-91 COLLATERAL DAMAGE: %s soul wiring moved "
                "(%r -> %r). Souls are Finger2 EQUIPMENT and orbs are "
                "treasureProxyName - the orb change must be purely additive."
                % (rec, soul_before[rec], now))

    # (ii) EVERY donor tier a roster record left is byte-unchanged and lost
    #      EXACTLY the roster records that left it - nothing else, and nothing
    #      joined. Derived, so orb01 (um_toxeus_21's old tier, 11 consumers) is
    #      protected identically to orb04 (19 consumers).
    roster_low = {_norm(r) for r in roster}
    donor_after = _snapshot(db, list(donor_snapshot_before))
    if donor_after != donor_snapshot_before:
        changed = sorted(r for r in donor_snapshot_before
                         if donor_after.get(r) != donor_snapshot_before[r])
        raise SystemExit(
            "[uber_apex_orb] BLAST-RADIUS VIOLATION: a donor orb record was "
            "EDITED (%s). The whole reason a new tier was minted is that these "
            "records serve other encounters and must stay byte-identical."
            % changed)
    for orb, before in donor_consumers_before.items():
        after = _consumers_of(db, orb)
        lost = sorted(set(before) - set(after))
        gained = sorted(set(after) - set(before))
        expected_lost = sorted(c for c in before if _norm(c) in roster_low)
        if lost != expected_lost or gained:
            raise SystemExit(
                "[uber_apex_orb] SCOPE VIOLATION on %s: consumers lost=%s "
                "gained=%s; expected exactly the Toxeus record(s) %s to leave and "
                "nothing to join. %d non-Toxeus consumer(s) must be untouched."
                % (orb, lost, gained, expected_lost,
                   len(before) - len(expected_lost)))
        print("  blast radius %s: %d -> %d consumer(s) (%d Toxeus left, %d "
              "non-Toxeus untouched)"
              % (orb.rsplit('\\', 1)[-1], len(before), len(after),
                 len(expected_lost), len(after)))

    # (ii-b) the orb04 DONOR CHAIN (pools/chests/tables the orb05 clones came
    #        from) is byte-unchanged too - a clone must never write back.
    orb04_after = _snapshot(db, list(orb04_before))
    if orb04_after != orb04_before:
        changed = sorted(r for r in orb04_before
                         if orb04_after.get(r) != orb04_before[r])
        raise SystemExit(
            "[uber_apex_orb] BLAST-RADIUS VIOLATION: the genericbossorb_04 chain "
            "changed (%s). Editing orb04 in place would silently buff all %d of "
            "its consumers." % (changed, len(consumers_before)))

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
    #      R-73's "her bespoke chest survives" guarantee holds by construction.
    leinth_untouchable_after = _snapshot(db, list(leinth_untouchable_before))
    if leinth_untouchable_after != leinth_untouchable_before:
        moved = sorted(r for r in leinth_untouchable_before
                       if leinth_untouchable_after.get(r) != leinth_untouchable_before[r])
        raise SystemExit(
            "[uber_apex_orb] Leinth's proxy/pools/monster records changed (%s). "
            "This module upgrades her CHESTS only; her treasureProxyName must "
            "keep naming her own bespoke chest (R-73 asserts it too)." % moved)

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

    print("  scope proof: %d Toxeus record(s) on orb05 (roster DERIVED, == pin); "
          "orb04 chain + every donor tier byte-unchanged, orb04 consumers %d -> "
          "%d; R-48/R-91 soul wiring untouched on the whole roster; Leinth "
          "RE-TIERED in place (2 fields x 3 chests, identity + gold generator "
          "kept, originals preserved, proven not-nerfed group-by-group)"
          % (len(roster), len(consumers_before), len(_orb04_consumers(db))))


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

    # (a) THE R-99 ROSTER INVARIANT, in both directions.
    #     a1: the derived roster == ROSTER_PINNED (nothing new, nothing lost) and
    #         the second, name-tag derivation agrees;
    #     a2: EVERY roster record carries orb05;
    #     a3: the orb05 carrier set is EXACTLY the roster - nothing that is NOT a
    #         Toxeus variant may sit on the apex tier. This is the invariant the
    #         old planted NEGATIVE 2 protected ("a third record must FAIL"); it is
    #         not weakened, it just has a bigger legitimate roster now, and it is
    #         what keeps R-99's opening reassurance ("we did NOT raise all the
    #         champions") true.
    roster, roster_problems = _roster_problems(db, 'verify')
    problems.extend(roster_problems)

    for rec in roster:
        got = _v1(db, rec, _TREASURE)
        if not isinstance(got, str) or _norm(got) != _norm(ORB05):
            extra = ''
            if _norm(rec) == _norm(_HUNT):
                extra = (" This is the Endless Hunt - the champion Will has "
                         "actually fought - and it is the record that shipped "
                         "with NO orb at all for two waves.")
            elif _norm(rec) in {_norm(r) for r in ROSTER_DEFERRED}:
                extra = (" This one is a build-time CLONE of um_toxeus_hunt_99 "
                         "made by toxeus_hunt_endless, so it inherits the orb "
                         "only if that module still runs AFTER this one - check "
                         "the registry order in tools/patches/__init__.py.")
            problems.append(
                "%s treasureProxyName = %r, expected genericbossorb_05 - R-99 "
                "puts EVERY Toxeus variant on the apex orb.%s"
                % (rec.rsplit('\\', 1)[-1], got, extra))

    carriers = _consumers_of(db, ORB05)
    creep = sorted(set(_norm(c) for c in carriers) - {_norm(r) for r in roster})
    if creep:
        problems.append(
            "SCOPE CREEP onto the apex tier: %d record(s) carry "
            "treasureProxyName=genericbossorb_05 that are NOT Toxeus variants: "
            "%s. genericbossorb_05 exists precisely so the shared genericbossorb_04 "
            "tier does not move; anything non-Toxeus joining orb05 is the failure "
            "R-99 opens by ruling out." % (len(creep), creep))

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

    # (c) orb05's four knobs, measured against Leinth's chest's - AS AMENDED BY
    #     R-240 + R-241 (Will 2026-08-11).
    #
    #     ⚠ THIS IS A SECOND, INDEPENDENT COPY of the law `_post_wave_problems`
    #     amends, and it has to move with it or the amendment is cosmetic: (h) would
    #     accept the trim and (c) would abort the build three lines later on the same
    #     three records. The round-3 vet found (h); this one was behind it.
    #
    #     Both eras keep the SHAPE of the check - "orb05's knobs are exactly the
    #     shared calibre, whatever the shared calibre currently is". Only the
    #     reference value moves, and it moves through R-240's own transform rather
    #     than being re-typed, so (c) cannot drift away from the trim or from (h).
    #     The two knobs R-240/R-241 do NOT touch - the unique-share weights and the
    #     no-'/'-in-an-MP-equation law, both below - are untouched in both eras.
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
        import sys as _sys
        from pathlib import Path as _Path
        _t = _Path(__file__).resolve().parent.parent
        if str(_t) not in _sys.path:
            _sys.path.insert(0, str(_t))
        import svc_loot_volume as _SLV
        import svc_orb_legendary as _SOL
        for d in _DIFFS:
            table_new = CHAIN[d][5]
            if not db.has_record(table_new):
                continue
            mn, mx, l4 = _knobs(db, table_new)
            era = _calibre_era(db, table_new, d)
            # The reference this difficulty is actually held to. In the R-240 era it
            # is Leinth's own numbers put through the committed trim for this tier -
            # i.e. she and the roster are still on ONE calibre, that calibre is just
            # the one Will asked for on 2026-08-11.
            d_min, d_max, d_l4 = ref_min, ref_max, ref_l4
            if era == 'R-240':
                _p = _SLV.parse_eq(_v1(db, table_new, 'numSpawnMinEquation'))
                if _p is not None:
                    d_min, d_max = _SLV.trimmed_multipliers(
                        _p[0], ref_min, ref_max, _SHORT[d])[:2]
                d_l4 = _SOL.FAMILY_CHANCE_EXPECTED.get(4, ref_l4)
            _era_note = ('' if era != 'R-240' else
                         " (R-240/R-241 calibre; Leinth's b96 reference *%s/*%s @%s "
                         "trimmed for tier %s - see docs/WILL_RULINGS.md)"
                         % (ref_min, ref_max, ref_l4, _SHORT[d]))
            if (_mult(mn) or 0) + 1e-6 < d_min:
                problems.append("%s numSpawnMin multiplier %s < Leinth's %s%s"
                                % (table_new, _mult(mn), d_min, _era_note))
            if (_mult(mx) or 0) + 1e-6 < d_max:
                problems.append("%s numSpawnMax multiplier %s < Leinth's %s%s"
                                % (table_new, _mult(mx), d_max, _era_note))
            if float(l4 or 0) + 1e-6 < float(d_l4):
                problems.append("%s loot4Chance %s < Leinth's %s%s"
                                % (table_new, l4, d_l4, _era_note))
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

    # (d) EVERY donor tier the roster left still exists, still carries NO Toxeus
    #     record, and still serves at least its measured remaining consumers.
    #     R-99 adds orb01 to this: um_toxeus_21 left it, and its other 10
    #     consumers (Elephant Snatcher, Mormo, Kaublasia, Calybe x2, Rakanizeus
    #     x2, Melalos x3) deserve the same protection orb04's 19 get.
    roster_low = {_norm(r) for r in roster}
    for orb, floor in sorted(DONOR_TIER_FLOORS.items()):
        if not db.has_record(orb):
            problems.append(
                "%s is GONE - a donor tier a Toxeus record left must survive for "
                "its OTHER consumers (R-47's shared generic orb)"
                % orb.rsplit('\\', 1)[-1])
            continue
        remaining = _consumers_of(db, orb)
        still = sorted(c for c in remaining if _norm(c) in roster_low)
        if still:
            problems.append(
                "%s STILL carries Toxeus record(s) %s - R-99 moves every Toxeus "
                "variant to the apex orb" % (orb.rsplit('\\', 1)[-1], still))
        if len(remaining) < floor:
            problems.append(
                "%s now has only %d consumer(s) %s, below the measured floor of "
                "%d - this module moves Toxeus records ONTO orb05, it never "
                "strips a shared tier from the encounters that depend on it"
                % (orb.rsplit('\\', 1)[-1], len(remaining), remaining, floor))
    if db.has_record(ORB04):
        for d in _DIFFS:
            _p, _np, chest_old, _nc, table_old, _nt = CHAIN[d]
            got = _v1(db, chest_old, 'tables')
            if not isinstance(got, str) or got.lower() != table_old.lower():
                problems.append("orb04 chest (%s) tables moved to %r - the donor "
                                "chain must stay untouched" % (d, got))

    # (e) R-48 (+ R-91) survives on all THREE fought champions. Souls are Finger2
    #     equipment, orbs are treasureProxyName; the two mechanisms are
    #     independent, and this is where that independence is PROVEN rather than
    #     asserted in prose.
    for label, rec in _SOUL_100_CHAMPIONS:
        if not db.has_record(rec):
            problems.append("%s: record MISSING, so its R-48/R-91 100%% soul drop "
                            "cannot be verified" % label)
            continue
        c = _v1(db, rec, 'chanceToEquipFinger2')
        try:
            c = float(c or 0.0)
        except (TypeError, ValueError):
            c = 0.0
        if abs(c - 100.0) > 0.001:
            problems.append("%s: chanceToEquipFinger2=%s but R-48/R-91 requires "
                            "100 - the orb change must not touch the soul"
                            % (label, c))

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

    # (h) THE CALIBRE PROOF, computed against her preserved ORIGINAL tables - AS
    #     AMENDED BY R-240 + R-241 (Will 2026-08-11). `_post_wave_problems` runs the
    #     ORIGINAL `_no_nerf_problems` verbatim on a pre-R-240 arz and the amended
    #     proof on a trimmed one; read its docstring for which half of R-72/R-99
    #     survives (unity: all of it) and which half is superseded (the absolute
    #     floor on the two axes Will pointed at). The supersession is recorded in
    #     docs/WILL_RULINGS.md rather than resolved here.
    eras = set()
    for d in _DIFFS:
        problems.extend(_post_wave_problems(db, CHAIN[d][5],
                                            LEINTH_TABLES_BY_DIFF[d], d))
        eras.add(_calibre_era(db, CHAIN[d][5], d))
    # ONE calibre means one ERA too: a db where Normal was trimmed and Legendary was
    # not is not "one apex calibre for the whole roster", it is two, and each
    # difficulty would pass its own check in isolation.
    if len(eras) > 1:
        problems.append(
            "the three difficulties are in DIFFERENT calibre eras (%s). R-72/R-99's "
            "whole point is one shared calibre; a half-applied R-240 gives the roster "
            "two, and every per-difficulty check above still passes."
            % ', '.join('%s: %s' % (d, _calibre_era(db, CHAIN[d][5], d))
                        for d in _DIFFS))

    if problems:
        raise SystemExit(
            "[uber_apex_orb] R-72 + R-99 VERIFY FAILED (one apex calibre for the "
            "WHOLE Toxeus roster and Leinth):\n  - " + "\n  - ".join(problems))
    # The PASS line NAMES THE ERA. "all four calibre knobs >= her original chest" is
    # true only before R-240/R-241; printing it unconditionally on a trimmed db would
    # be the gate telling the ship lane the opposite of what it just proved.
    _era = sorted({_calibre_era(db, CHAIN[d][5], d) for d in _DIFFS})
    _era_txt = (
        "all four calibre knobs >= her original b96 chest (pre-R-240 calibre)"
        if _era == ['pre-R-240'] else
        "all four calibre knobs EXACTLY on the R-240/R-241 shared calibre - Leinth's "
        "own b96 numbers put through the committed trim, so she and the roster are "
        "still on ONE calibre and it is the LOWER one Will ordered on 2026-08-11 "
        "(\"you made the orbs way too good\"); the absolute-floor half of R-72/R-99 is "
        "SUPERSEDED, recorded in docs/WILL_RULINGS.md, and the unity half is proved "
        "here twice (chest->table identity + one era across all three difficulties)")
    print("  [uber_apex_orb] verify OK: the DERIVED Toxeus roster is %d record(s) "
          "(%s) and EVERY one is on genericbossorb_05, with the orb05 carrier set "
          "EXACTLY equal to it (no scope creep); Leinth's 3 chests on the SAME "
          "apex tables + level equation; chain resolves on n/e/l; %s; her bespoke "
          "mesh/name/gold generator intact and her variants still on her own proxy; "
          "calibre proof green on all 6 loot groups x 3 difficulties; donor tiers "
          "intact (orb04 %d other consumers, orb01 %d); R-48/R-91 100%% souls intact "
          "on all 3 fought champions"
          % (len(roster), ', '.join(r.rsplit('\\', 1)[-1][:-4] for r in roster),
             _era_txt, len(_orb04_consumers(db)), len(_consumers_of(db, ORB01))))
