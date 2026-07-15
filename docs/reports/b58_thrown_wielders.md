# b58 - Thrown-Wielder Arming (Will veto artifact)

> **VERIFY-FIRST.** Will (2026-07-14): *"I see we have throwing weapons in the game now,
> but there are no enemies who use the throwing items."*
> This report answers, from ground truth: (1) do any enemies wield thrown weapons in
> reachable play? (2) which identity-appropriate families did we arm, how, and why is it safe?
>
> **Ground-truth sources (read-only):**
> - Effective DB = base TQAE `database.arz` (74,013 recs) overlaid by golden mod
>   `SoulvizierClassic.arz` md5 **`b33c5a447f3a8ca652c14f78d4ad1dd4`** (build40, 51,029 recs).
> - World map = `local/Levels_merged.arc` -> `world/world01.map`, canonical Levels md5
>   **`9981085b78f1600cc0b31c3bec4cfd92`** (2,282 levels), cross-checked vs **stock TQAE**
>   `Resources/Levels.arc` and the **SVAERA** reference map.
> - No heavy build; every finding is a static read of the golden artifacts. Probes:
>   session `twa_gt_donors.py` / `twa_gt_blocks.py` / `twa_gt_anim.py` / `twa_gt_pool.py` / `twa_vet.py`.

---

## VERDICT (TL;DR)

**Will's observation is CONFIRMED, and the fix is built + fully verified (veto-pending).**

1. **No reachable enemy wields a thrown weapon.** Thrown weapons are a Ragnarok/Atlantis/EE
   item class (`Class = WeaponHunting_RangedOneHand`, 191 records, all `xpack2/3/4`). Of the
   74 monsters whose weapon slot resolves to a thrown weapon, **0 spawn in the reachable
   Act1-Hades + SV campaign** (Part A). Throwing weapons DO drop as loot (the mod's own
   `_restore_thrown_weapon_drops`), which is exactly what Will sees.
2. **ROOT CAUSE (ground truth) - it is NOT "no rig can throw."** The base game shipped
   genuine throwers on **three reachable-campaign rigs** (Greek maenad, Egyptian dune raider,
   Oriental tigerman). **The SV/mod overlay DISARMS every one** (maenad/tigerman -> bow;
   dune raider -> melee) because the SV-classic roster predates thrown weapons. So the enemies
   who *should* throw already exist on our own maps - the overlay just took the javelins away.
3. **THE FIX (`tools/patches/thrown_wielders.py`, UNREGISTERED - golden stays byte-identical):**
   arm **3 identity-fit families x 2 tiers = 6 Common thrown-wielders** by cloning each family's
   base thrower (inheriting the throw-proven mesh + the full ranged anim block + the ranged AI)
   and **re-authoring the right hand with that family's exact vanilla thrown block** + disabling
   the offhand. Drops are banded to bow-wielders **by construction**. Rides the next integration
   build after Will's veto + the coupled MAP-lane placement.

> This report **corrects two claims** in the first-pass audit scaffold (which proposed a Greek
> bandit *slinger* on `bandit_greek02`): (i) the slinger's only identity home is the **Act-5
> Corinthia** bandit set our campaign never reaches; (ii) the audit parked "maenad" as HIGH risk
> ("no throw-proven maenad rig") - **ground truth: `Maenad02.msh` IS throw-proven** (the base
> game ships genuine maenad throwers on it). The families below ride rigs that **reachable
> campaign monsters already use**, so the MAP lane has a real, identity-matched home for each.

---

## PART A - VERIFICATION (no reachable enemy throws)

| Metric | Value |
|---|---|
| `Class = WeaponHunting_RangedOneHand` records (effective DB) | **191** (all `xpack2/3/4`) |
| Base Act1-Hades thrown weapons / SV-mod thrown weapons | **0 / 0** |
| Monsters whose weapon slot resolves to a thrown weapon | **74** - all DLC (Aesir, greekbandit slinger, troll skulk, yerren, mercenary, dvergr, nerthus titan, monkeyman, potamoi) or `zz_dev` |
| Thrown-wielders **directly placed** in any level blob | **0** (they spawn only via proxy pools) |
| Thrown-wielder-spawning proxies in a **campaign-namespace** level | **1** - `xpack2\proxiesnorth\area001 corinthia\human_greekbandit_01t` in `Greece/Area003/PineForest05.LVL` |

That one vector is **unreachable in the SV-classic campaign**: its slingers are **charLevel 37+**
(Ragnarok tier) from Ragnarok's **Corinthia (Act-5)** proxy set; `PineForest05`'s base Act-1
population is lvl-3-9 harpies/crows. The placement is **byte-identical in stock TQAE / SVAERA**
(not mod-introduced), and the campaign ends at Hades with the DLC acts gated off (256-controller
sweep + Will's own long Act-1 play show zero throwers).

> Residual (documented, non-blocking): the exact runtime proxy-activation gate for shared-world
> Act-1/Act-5 levels is inferred from monster tier + Ragnarok proxy namespace + stock parity +
> playtest, not byte-proven from engine code. The one input that flips the verdict: if Will has
> ever seen a lone javelin-throwing bandit in the Act-1 pine forest.

**Conclusion:** no reachable enemy wields a thrown weapon. Will is right.

---

## PART B - THE ROOT CAUSE (the overlay disarmed the throwers we already have)

Ground truth from the effective DB (`twa_gt_donors.py`, BASE vs golden `b33c5a44`):

The base game ships **genuine throwers on three rigs that reachable campaign monsters use**.
Each equips a `WeaponHunting_RangedOneHand` weapon in the RIGHT hand; the mod overlay disarms it:

| Family (rig) | Base thrower donor(s) | BASE hands | GOLDEN-overlay hands (DISARMED) |
|---|---|---|---|
| **Maenad** `Creatures\Monster\Maenad\Maenad02.msh` | `maenad\ar_archer_06` (lvl6), `br_archer_10` (lvl10), Common | RIGHT `1h_ranged`@100, LEFT bow@0 | RIGHT@0 + loot CLEARED, LEFT **bow**@100 |
| **Dune Raider** `Creatures\Monster\DuneRaider\DuneRaider01.msh` | `duneraider\am_assassin_15` (lvl15), `am_assassin_21` (lvl21), Champion | dual `1h_ranged`@100 (both hands) | both hands **melee** `1h_dyn`@100 |
| **Tigerman** `Creatures\Monster\TigerMan\TigerMan01.msh` | `tigerman\ar_archer_27` (lvl27), `ar_archer_33` (lvl33), Common | RIGHT `1h_ranged`@100, LEFT bow@0 | RIGHT@0 + loot CLEARED, LEFT **bow**@100 |

So the copy a registry module sees in the overlay `db` is a **bow/melee** unit. **Cloning it
alone would NOT throw** - it would reproduce the disarmed hands. That is the trap the fix avoids.

### Why it is safe to re-arm these clones (four make-or-break checks, all PASS)

1. **RIG (the make-or-break).** The throw animation clips live in the MESH; the record's
   `rangedOneHand*/dualRanged*` anim-weight block only *selects* them. A rig whose mesh lacks the
   clips T-poses. The only sound proof a mesh has them is *a shipping monster throws on that exact
   mesh* - which is precisely why these three rigs qualify (the base throwers above). Verified: the
   **disarmed overlay clone RETAINS the full anim block** (`rangedOneHandAttackAnimWeight1=100`,
   `dualRangedAttackAnimWeight1=100`), identical to base - so re-arming a thrown weapon throws, it
   does not T-pose. `Satyr01.msh` (base Act-1 satyr `am_peltast_*`) carries the same anim-weight
   *fields* yet has **no shipping thrower** - so anim-weight fields are NOT proof; the `RIG_WHITELIST`
   (exact mesh of a shipping thrower) is the gate.
2. **AI.** Ranged throw + keep-distance behavior is **engine-automatic from the equipped weapon
   class**; the base throwers carry no hand-authored projectile skill. We copy that shape.
3. **EQUIP.** Restore the base thrower's own right-hand block (below) and set
   `chanceToEquipLeftHand=0` so the inherited bow/melee offhand can never win the attack.
4. **DROPS.** The base thrower's unique-thrown drop slot (`chanceToEquipRightHandItem5` = 4-5 out
   of ~5025 total slot weight, ~0.1%) is **identical to that same monster's bow-drop slot weight**.
   Restoring the vanilla block bands thrown drops to bow-wielders **by construction** (not guesswork).

### The exact vanilla thrown block per family (captured verbatim from the base thrower)

Every table is base-game and resolves at runtime (mod overlays base). `Item1` (static common)
dominates at weight 5000; `Item3` (monster-magic) + `Item5` (unique) are the rare drop slots:

| Family | `lootRightHandItem1` [N,E,L] static (w=5000) | `lootRightHandItem3` monster-magic (w) | `lootRightHandItem5` unique (w) |
|---|---|---|---|
| Maenad | `1h_ranged_01b / 06a / 11a` | `ni/ei/li_roh_maenad` (20) | `roh_01 / 06 / 11` (4) |
| Dune Raider | `1h_ranged_02b / 07a / 12a` | `ni/ei/li_roh_duneraider` (25) | `roh_02 / 07 / 12` (5) |
| Tigerman | `1h_ranged_03a / 08a / 13a` | `ni/ei/li_roh_tigerman` (25) | `roh_03 / 08 / 13` (5) |

(all under `records\xpack2\item\loottables\weapons\{static,monster,unique}\`).

---

## PART C - THE ARMING (what was built; the veto table)

Design law (amgoz1 voice + the brief): **arm only families where a hurled weapon FITS the
identity and whose rig is throw-proven; never arm everything.** All three are skirmisher/hunter
humanoids for whom a hurled javelin is textbook, and all three ride a rig a reachable campaign
monster already uses - so the MAP lane drops them straight into the matching Act pack.

### C1. The armed roster (THE VETO TABLE)

Module `tools/patches/thrown_wielders.py`. Each variant clones its family's base thrower at that
donor's native level (inheriting the N/E/L `charLevel` + mesh + anim block + ranged AI), forces
**Common** rank, re-arms the right hand with the family's vanilla thrown block, and disables the
offhand. **6 armed records + 3 minority-flavor ProxyPools.**

| Armed record (new, SVC namespace) | Family / rig | Donor (base thrower) | N/E/L charLevel | Rank | Right hand | Drop slot |
|---|---|---|---|---|---|---|
| `svc_maenad_javelineer_06` | Maenad / `Maenad02.msh` | `maenad\ar_archer_06` | [6,35,53] | Common | 1h_ranged @100 | unique w=4 |
| `svc_maenad_javelineer_10` | Maenad / `Maenad02.msh` | `maenad\br_archer_10` | [10,37,54] | Common | 1h_ranged @100 | unique w=4 |
| `svc_duneraider_skirmisher_15` | Dune Raider / `DuneRaider01.msh` | `duneraider\am_assassin_15` | [15,40,57] | Common* | 1h_ranged @100 | unique w=5 |
| `svc_duneraider_skirmisher_21` | Dune Raider / `DuneRaider01.msh` | `duneraider\am_assassin_21` | [21,44,60] | Common* | 1h_ranged @100 | unique w=5 |
| `svc_tigerman_hunter_27` | Tigerman / `TigerMan01.msh` | `tigerman\ar_archer_27` | [27,48,63] | Common | 1h_ranged @100 | unique w=5 |
| `svc_tigerman_hunter_33` | Tigerman / `TigerMan01.msh` | `tigerman\ar_archer_33` | [33,52,67] | Common | 1h_ranged @100 | unique w=5 |

\* The dune-raider base thrower (`am_assassin`) is a **dual-throwing Champion**; we down-rank it
to a **Common single-javelin skirmisher** (offhand disabled) so it reads as flavor trash, not a
mini-boss, and does not out-rate the pack. (Down-rank keeps its base stats; noted for veto.)

**Working display names (amgoz-pass + Will-veto pending):** "Maenad Javelineer",
"Dune Raider Skirmisher", "Tigerman Hunter". Tags `tagSVCMonMaenadJavelineer /
...DuneRaiderSkirmisher / ...TigermanHunter`.

### C2. Mechanics recipe (per armed record, in `apply`)

1. **Clone** the base thrower donor -> a new `records\creature\monster\svc\thrown\*` record
   (inherits mesh + full `rangedOneHand/dualRanged` anim block + ranged AI + stats/skills).
2. **Rename** to the amgoz-voice identity (`description = name_tag`).
3. **Force Common** (`monsterClassification = Common`).
4. **RE-ARM the right hand** with the family's vanilla thrown block (static+magic+unique tiered
   N/E/L arrays + vanilla weights; `chanceToEquipRightHand=100`), and **disable the offhand**
   (`chanceToEquipLeftHand=0`). No explicit `dtype` - existing numeric fields keep their type
   (`chance*`=FLOAT, `*Item*` weights=INT), new loot arrays infer STRING (dtype-corruption-safe).
5. **No soul leak** - Common rank + `chanceToEquipFinger2=0` (base throwers already 0); the mod's
   soul gate only lets Hero/Boss/Quest drop souls, and `verify()` re-asserts it.

### C3. Spawn wiring (DB here + MAP separate - coupled, rides the next integration build)

- **DB (this module):** the 6 armed records + one `ProxyPool` per family
  (`records\creature\proxy\svc\thrown\svc_*_pool.dbr`, schema mirrors a real base pool:
  `championChance/Min/Max=0`, `name%d/weight%d`, `spawnMin/Max`, `proxyPoolEquation` = the Act's
  own equation, all verified to resolve).
- **MAP (separate lane):** place each pool's proxy as a small skirmisher cluster **OR** harvest its
  name/weight rows into the existing Act-1 maenad / Act-2 dune-raider / Act-3 tigerman pack at a
  **minority weight**, so throwers are a *flavor* of the pack (a few javelineers among the melee),
  not the whole pack.
- **Integration prereq:** `apply()` clones base throwers that already live (disarmed) in the golden
  overlay, so no import is needed for the current golden. If a future build strips base monsters,
  import the donor like `build_svc_database.import_base_game_bosses` (the module fails loud with
  this instruction if a donor is absent).

---

## PART D - VERIFICATION OF THE BUILD (dry-run vs golden b33c5a44 + adversarial vet)

Module is **UNREGISTERED** (`REGISTRY` has 13 modules, none is `thrown_wielders`) -> the golden
build stays byte-identical `b33c5a44` for every other lane. The dry-run applies the module to a
copy of the golden and proves:

- **Premise proven:** donor `ar_archer_06` `chanceToEquipRightHand = 0` in the overlay (disarmed) -
  a naive clone would not throw; the re-arm is required and applied.
- **Intended-only delta:** **+9 records** (6 monsters + 3 pools), **0 stray**, **0 existing records
  mutated** (`db._modified` == exactly the 9 new records; base donors untouched).
- **Post-condition:** every armed record = RIGHT `chanceToEquipRightHand=100.0` (FLOAT), LEFT `=0.0`,
  `lootRightHandItem1` = a 3-tier N/E/L thrown STRING array, `wItem1=5000` (INT), unique drop slot
  4-5 (INT, in band), `finger2=0`, `rangedOneHandAttackAnimWeight1=100`, mesh in `RIG_WHITELIST`,
  rank Common.
- **`verify()` OK** (roster-derived; asserts rig-whitelist + anim block + right-thrown + left-disabled
  + drop band + Common + no soul leak + pool integrity).
- **`_negtest()` OK** - 7 broken shapes each rejected: non-thrown weapon, off-whitelist rig, right
  hand unequipped, **left hand re-enabled**, drop weight out of band, non-Common rank, soul-leak.
- **Round-trip:** the 9 new records encode/decode with **0 INT/FLOAT corruption**.
- `py_compile` + `_check_registry` clean.

Full contract suite (needs the 700MB levels arc) runs at integration time per the no-heavy-build
constraint; the module carries its own `verify()`/`_negtest()` and rides the same battery every
registered module faces (soul-leak, mod-spawn-proxy eligibility, clone-shape, etc.).

---

## PART E - OPEN QUESTIONS FOR WILL (veto inputs)

1. **Scope.** Ship all three families (Greece maenad + Egypt dune raider + Orient tigerman), or
   start with one Act (recommended if you want to eyeball it first: **maenad**, since it is the
   earliest and you will see it in Act 1)?
2. **Density.** How common should throwers be in a pack - a rare flavor (~1 in 10) or a distinct
   skirmisher sub-group in specific spots? (Sets the MAP-lane minority weight.)
3. **Dune raider down-rank.** OK to make the dual-throwing Champion assassin a **Common
   single-javelin** skirmisher (keeps its stats, loses champion status/second javelin), or keep it
   a Champion dual-thrower?
4. **Names/lore.** "Maenad Javelineer / Dune Raider Skirmisher / Tigerman Hunter" are working copy -
   want an amgoz-voice pass (e.g. a themed name + one-line bestiary flavor each) before it ships?
5. **Reach further?** Add a matching thrown-wielder in later acts (e.g. a Hades or a Northern-tier
   skirmisher) so throwers recur, or keep it to Acts 1-3?

---

## Appendix - reproduction

All probes read-only vs the golden artifacts (`work/.../SoulvizierClassic.arz` `b33c5a44`,
`"/c/Program Files (x86)/.../database.arz"`, `local/Levels_merged.arc` `9981085b`): donor
BASE-vs-overlay hand diff (`twa_gt_donors.py`), full vanilla block capture (`twa_gt_blocks.py`),
anim-block-retention + loot-table resolution (`twa_gt_anim.py`), ProxyPool schema + equation
resolution (`twa_gt_pool.py`), and the finished-module adversarial vet (`twa_vet.py`:
modified-set, thrower shape, base-untouched, round-trip). Module self-test:
`py tools/patches/thrown_wielders.py <golden.arz>`.
