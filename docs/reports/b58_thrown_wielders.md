# b58 - Thrown-Wielder Audit + Arming Proposal (Will veto artifact)

> **Auditor lane. VERIFY-FIRST.** Will (2026-07-14): *"I see we have throwing weapons
> in the game now, but there are no enemies who use the throwing items."*
> This report answers, from ground truth: (1) do any enemies wield thrown weapons in
> reachable play? (2) if not, which identity-appropriate families should we arm, and how?
>
> **Ground truth sources (read-only):**
> - Effective DB = base TQAE `database.arz` (74,013 recs) overlaid by golden mod
>   `SoulvizierClassic.arz` md5 **`b33c5a447f3a8ca652c14f78d4ad1dd4`** (build40, 51,029 recs).
> - World map = `local/Levels_merged.arc` -> `world/world01.map`, canonical Levels md5
>   **`9981085b78f1600cc0b31c3bec4cfd92`** (2,282 levels), cross-checked vs **stock TQAE**
>   `Resources/Levels.arc` and the **SVAERA** reference map.
> - No heavy build; all findings are static reads of the golden artifacts.

---

## VERDICT (TL;DR)

**Will's observation is CONFIRMED.** Zero thrown-wielding enemies spawn in the
reachable Soulvizier Classic campaign (Act 1 Greece -> Act 4 Hades/IT + the SV blood-cave
areas). Reasoning, all ground-truth:

1. **Thrown weapons are a Ragnarok/Atlantis/Eternal-Embers-era item class** (`Class =
   WeaponHunting_RangedOneHand`, template `WeaponHunting_RangedOneHand`, 191 records, all
   under `xpack2/xpack3/xpack4`). The SV-classic roster + the base Act1-Hades roster
   predate them.
2. **Every monster that wields a thrown weapon is a DLC monster or a dev-test dummy.** Of
   74 monster records whose weapon slot resolves to a thrown weapon, **0 are base Act1-Hades
   monsters and 0 are SV / mod (drx*, SVC) monsters.** They are all Ragnarok (Aesir,
   greekbandit slingers, troll skulks, yerren throwers, mercenary skirmishers, dvergr,
   ancient titans), Atlantis (monkeyman flingers, potamoi throwers), or `zz_dev` test rigs.
3. **The only thrown-wielder spawn vector physically placed in a "campaign-namespace"
   level is a Ragnarok Act-5 overlay that our campaign never reaches.** Exactly one proxy
   in one Greece-folder level can roll a thrown-user, and its monsters are **charLevel 37+**
   (Ragnarok tier) fed from Ragnarok's Corinthia proxy set - it activates only in the
   Ragnarok Act-5 playthrough, which the SV-classic campaign gates off (ends at Hades; DLC
   acts cancelled - proven by the 256-controller sweep; and Will's own extensive Act-1 play
   shows no throwers).
4. **Throwing weapons DO exist as loot** (184 thrown weapon items are reachable through the
   world's item/loot closure), which is exactly what Will sees: players find and equip
   thrown weapons, but no reachable enemy is seen using one.

So the design gap is real: to see enemies throw, we must **arm identity-appropriate
reachable families** (Part C). This report is the veto artifact for that roster.

---

## PART A - VERIFICATION (the numbers)

### A1. What a "thrown weapon" is
| Metric | Value |
|---|---|
| `Class = WeaponHunting_RangedOneHand` records (effective DB) | **191** |
| Namespace | all `xpack2` (Ragnarok) / `xpack3` (Atlantis) / `xpack4` (EE) |
| Base Act1-Hades thrown weapons | **0** |
| SV / mod (drx*, SVC) thrown weapons | **0** |

Thrown weapons never existed in classic TQ:IT / SV 0.98i; they are a Ragnarok addition.

### A2. Monster equipment mechanism (how a monster wields a weapon)
A monster's main-hand weapon comes from the **`lootRightHandItem1..N`** equip slot (offhand =
`lootLeftHandItem*`; rings/souls = `lootFinger*`; that is how this mod attaches souls). The
slot value is a loot table (or item) resolved at spawn; `chanceToEquipRightHand` (%) gates
whether it equips at all. A monster **throws** iff its equipped right-hand item is a
`WeaponHunting_RangedOneHand` weapon **and** its rig carries the throw animation set (Part B).

### A3. Who wields thrown weapons in the effective DB
- **Direct equippers (thrower in a `loot*HandItem*` slot):** 4 records - `x2q06_thor`
  (Ragnarok quest boss) + 3 `xpack4\...\zz_dev\*` developer dummies. **None ship/spawn.**
- **Weapon-slot thrown-wielders (slot resolves to a thrown-weapon loot table):** **74**
  records. Family breakdown (all DLC / dev):

  | Family (rig) | Records | Class | Level tier | Rig mesh (throw-capable) |
  |---|---|---|---|---|
  | greekbandit **slinger** | 6 | Common | 37-43 | `bandit_greek02.msh`, `pc\male\malepc02.msh` |
  | celticbandit **slinger** | 10 | Common | 39-43 | (bandit rigs) |
  | mercenary **skirmisher** | 3 | Common | 42-46 | `mercenary\fakeeinherjar.msh` |
  | troll **skulk** | 12 | Common | 39-46 | `foresttroll\trollbrute01.msh` |
  | yerren **thrower** | 3 | Common | 43-47 | `yerren\bludgeoner01.msh` |
  | aesir **fodder_thrower / jarl** | 7 | Common/Champ/Hero | 45-52 | `aesir\einherjar\*.msh` |
  | dvergr **warrior** | 3 | Common | 43-47 | `dvergr\dvergrlurker01.msh` |
  | nerthus **ancient_earth/forest** (titans) | 6 | Quest boss | 42-48 | `nerthusancients\*.msh` |
  | monkeyman **flinger** (Atlantis) | 6 | Common | 29-37 | `xpack3\...\satyrs\libyansatyr01.msh` |
  | potamoi **thrower** (Atlantis) | 12 | Common | 36-40 | `xpack3\potamoi\potamoiwarrior01.msh` |
  | npc `ss_porcusroh2`, `x2q06_thor` | 2 | Champ/Quest | 15/48 | `newgreece\grkguard01.msh`, `pc\male\malepc01.msh` |
  | `zz_dev` dummies | 4 | Hero | 50 | (dvergr / nerthus rigs) |

- **Thrown-droppers only (thrown reaches a non-weapon slot - `lootMisc2`/`lootFinger2` - so
  they DROP a thrown weapon but do not wield it):** the 137-monster loot closure that touches
  a thrown weapon at all is **entirely** `xpack2/3/4` + 4 `drxcreatures\bloodwitch\d_reaver_*`.
  The 4 DRX reavers reach a thrown weapon only through a generic drop table (misc slot), not a
  weapon slot - they do **not** throw. (Low-priority drop note, not a wield.)

### A4. Spawn reachability (the make-or-break)
The merged `world01.map` is the full stock TQAE world - it **physically contains** every
Ragnarok/Atlantis/EE level (726 xpack4 + 288 xpack2 + 258 xpack3 level blobs), so a naive
"referenced in the map" closure lights up 54 throwers. **That is an artifact of unreachable
DLC-act levels being present in the file.** Attributing every spawn to the **level** that
places it, and separating campaign levels (greece/egypt/orient/xpack-IT/xbloodcave/babylon/
olympus/bossarena/uberdungeon) from the gated DLC-act levels (xpack2/3/4):

- **Thrown-wielder monsters directly placed in ANY level blob: 0.** They only spawn via
  proxy pools.
- **Thrown-wielder-spawning proxies placed in a NON-xpack (campaign-namespace) level: exactly
  1** - `xpack2\proxiesnorth\area001 corinthia\human_greekbandit_01t.dbr`, placed in
  `Levels/World/Greece/Area003/PineForest05.LVL`. Its pool `greekbandit_01_general01`
  (ProxyPool) lists 3 slinger variants (`ar_slinger_37/39/41`) at weight 5 each out of a
  180-weight pool (~8% of that proxy's common spawns).
- **This vector is unreachable in the SV-classic campaign.** Proof:
  - The slingers are **charLevel [37, 53, 67]** (Ragnarok tier). `PineForest05`'s *base*
    Act-1 population is harpies/crows at **charLevel 3-9** (`proxies greek\area003\`, and the
    mod even tuned that base proxy with `poolLegendary*`). A level-37 bandit cannot be an
    Act-1 first-visit enemy.
  - The proxy is a **Ragnarok Corinthia** proxy (`xpack2\proxiesnorth\area001 corinthia\`,
    `difficultyLimitsFile = limit_area001`). `PineForest05.LVL` is a shared-world level that
    serves Act-1 (base low-level proxies) **and** Ragnarok Act-5 Corinthia (this level-37
    overlay); the engine activates the set matching the current act/region. Our campaign
    never enters Ragnarok, so the overlay never fires.
  - This placement is **identical in stock TQAE, SVAERA, and our merged map** (not something
    the mod introduced) and the mod deliberately left the overlay untouched while tuning the
    genuine Act-1 proxy - consistent with it being unreachable content.
  - Corroborated by the standing fact (memory + 256-controller sweep): **the campaign ends at
    Hades; DLC acts are gated off**, and by Will's own long Act-1 play showing zero throwers.

  > Residual (documented, not blocking): the exact runtime proxy-activation gate for
  > shared-world levels is engine behavior we infer rather than byte-prove. Every static
  > signal (monster tier, Ragnarok proxy namespace, mod's own tuning choices) and the
  > empirical playtest agree it does not fire in Act-1. If Will has *ever* seen a lone
  > javelin-throwing bandit in the Act-1 pine forest, tell us - it would mean this one vanilla
  > overlay does fire and the roster below should account for it.

**Conclusion:** no reachable enemy wields a thrown weapon. Will is right.

---

## PART B - THE DONOR PATTERN (how a thrown-user actually works)

Ground truth from `records\xpack2\creatures\monster\greekbandit\ar_slinger_37.dbr` (the
cleanest Greek-identity donor):

1. **Equip the thrown weapon.** `chanceToEquipRightHand = 100` and
   `lootRightHandItem1 = [1h_ranged_05a.dbr, 1h_ranged_10a.dbr, 1h_ranged_15a.dbr]` (a
   level-tiered static RangedOneHand loot table under `xpack2\item\loottables\weapons`). That
   is the entire "make it throw" wiring - it always spawns holding a thrown weapon.
2. **Ranged AI is engine-automatic.** The slinger has **no explicit ranged attack skill** -
   its only `skillName*` are passives (`Armor_Passive`, `BonusDamage_Physical`) plus a
   hunting-net special (`ensnare`, `specialAttackRange = LongRange`). Once a
   `WeaponHunting_RangedOneHand` weapon is equipped, the engine drives the throw attack +
   keep-distance behavior from the **weapon class**. Copy the shape: equip + (optional)
   LongRange special; do not hand-author a projectile skill.
3. **The rig must carry the throw animation set (MAKE-OR-BREAK).** The record carries the full
   `rangedOneHandAttackAnim* / rangedOneHandAlertAnim* / ...Run/Walk/Die/Flee/Special*` and
   `dualRanged*` timing blocks; the actual `.anm` clips resolve from the **mesh**. A monster
   whose mesh lacks the `rangedOneHand` clip set will T-pose or fall back to melee with the
   thrown weapon. **Every armed record must sit on a mesh proven to have `rangedOneHand`
   anims.**
4. **Drops follow normal equip-drop rules.** The equipped weapon can drop on death; the
   record's rare/unique equip slot (`chanceToEquipRightHandItem5`) is a low single-digit
   weight. Keep it that way so thrown drops don't flood (compare the matching bow-archer of
   the same tier - both are ranged commons).

### Rig whitelist (meshes proven to carry `rangedOneHand` anims - from the 74 shippers)
```
xpack2\creatures\monster\bandits\greekbandit\bandit_greek02.msh   <- GREEK bandit (human)
creatures\pc\male\malepc01.msh / malepc02.msh                     <- human male PC rig
creatures\npc\newgreece\grkguard01.msh                            <- GREEK guard NPC (human)
xpack3\creatures\monster\satyrs\libyansatyr01.msh                 <- SATYR rig (Atlantis monkeyman)
xpack2\creatures\monster\mercenary\fakeeinherjar.msh              <- human skirmisher
xpack2\creatures\monster\dvergr\dvergrlurker01.msh                <- dvergr
xpack2\creatures\monster\foresttroll\trollbrute01.msh             <- troll
xpack2\creatures\monster\yerren\bludgeoner01.msh                  <- yerren (ape)
xpack2\creatures\monster\aesir\einherjar\einherjar01.msh / einherjarranger.msh
xpack2\creatures\monster\nerthusancients\nerthusancient_bear.msh / _ram.msh
xpack3\creatures\monster\potamoi\potamoiwarrior01.msh
```
The **Greek/human** rigs (`bandit_greek02`, `malepc*`, `grkguard01`) and the **satyr** rig
(`libyansatyr01`) are the identity-relevant, throw-proven options for our Greek/Egyptian/
Oriental campaign.

---

## PART C - ARMING PROPOSAL (needs Will's veto before it ships)

Design law: **arm only families where a hurled weapon FITS the identity** (amgoz1 voice:
monster-identity-driven, never generic filler) and whose **rig is throw-proven**. Do **not**
arm everything.

### C1. Candidate families (identity fit x rig-anim support x reachable placement)

| # | Proposed family | Identity fit | Rig (throw-proven?) | Reachable placement | Risk |
|---|---|---|---|---|---|
| 1 | **Greek bandit peltast** (javelineer) | Skirmisher/raider who peppers you before the melee closes - textbook thrown identity | `bandit_greek02.msh` **YES** (the slinger's own rig) | join the existing Act1-2 Greek bandit/brigand packs (base `proxies greek\...` human pools) | **LOW** |
| 2 | **Satyr trickster** (stone/javelin hurler) | Capering satyr who hurls and dances away - amgoz-flavored trickster | `libyansatyr01.msh` **YES** (Atlantis flinger) - but Atlantis look; verify the base Act-1 satyr mesh before reskinning | Act-1 satyr groves (satyr pools) | **MED** (rig identity: confirm base-satyr mesh has the anims, else the Libyan look clashes) |
| 3 | Amazon / maenad skirmisher | Huntress hurling javelins - strong identity | **NO throw-proven maenad/amazon rig** in the shipped set | Act-1/2 maenad areas | **HIGH** (needs a rig with `rangedOneHand` anims; defer until a rig is verified or borrow a human-female PC rig) |

**Recommended first wave: #1 only (Greek bandit peltast).** It is the lowest-risk, most
identity-coherent, throw-proven arming, and it drops the player straight into "enemies who
throw" in early Act 1 where Will will see it immediately. #2 is a strong follow-up once the
base-satyr mesh anim set is confirmed. #3 is parked pending a verified rig.

### C2. Proposed armed roster (the veto table)

| Record (new, SVC namespace) | Rig mesh | Weapon (equip loot) | Equip rate | Drop | Class | Tier N/E/L | Placement |
|---|---|---|---|---|---|---|---|
| `svc_bandit_peltast_08` | `bandit_greek02.msh` | `xpack2\...\1h_ranged_05a` (tier-scaled) | `chanceToEquipRightHand=100` | rare-slot wt 5 (match bow-archer) | Common | 8 / 40 / 55 | Act-1 Greek bandit pools |
| `svc_bandit_peltast_11` | " | `...1h_ranged_10a` | 100 | 5 | Common | 11 / 42 / 57 | Act-1/2 bandit pools |
| `svc_bandit_peltast_14` | " | `...1h_ranged_10a` | 100 | 5 | Common | 14 / 44 / 59 | Act-2 bandit pools |
| *(follow-up, veto-gated)* `svc_satyr_trickster_0x` | `libyansatyr01.msh` (or base satyr, verify) | `...1h_ranged_05a` | 100 | 5 | Common | Act-1 satyr tiers | Act-1 satyr pools |

Tiers/levels are placeholders sized to their placement; final numbers set at integration to
match the pool they join. **Names/lore are amgoz-treatment + Will-veto pending** - "peltast"
and "trickster" are working identities, not final copy.

### C3. Mechanics recipe (per armed record)
1. **Clone a throw-proven donor** (`ar_slinger_37` for humans; `ar_monkeyman_flinger_29` for
   satyr) -> inherits the full `rangedOneHand` anim block + equip wiring + ranged AI shape.
   *(Cloning a Monster is safe; the Pet.tpl equipment-copy ban applies only to pets/souls.)*
2. **Re-tier** `charLevel` to the target placement tier; keep `monsterClassification=Common`.
3. **Re-point** `lootRightHandItem1` to the tier-appropriate `1h_ranged_*` static table;
   confirm `chanceToEquipRightHand=100`.
4. **Drop band:** set the unique/rare equip slot weight (`chanceToEquipRightHandItem5`) to the
   same single-digit weight the matching **bow-archer** of that tier uses, so thrown drops do
   not out-rate bow drops.
5. **No soul leak:** Common rank -> **no** `lootFinger2*` soul (the build's soul-leak gate
   enforces this; only Hero/Boss/Quest drop souls).
6. **Re-skin** texture/bumpmap to the local bandit/satyr palette (amgoz visual pass).

### C4. Spawn wiring (DB + MAP, coupled - rides the next integration build)
Arming a record does nothing until it spawns. Two coupled deltas:
- **DB (this module):** create the armed monster records (+ a small ProxyPool that mixes them
  into the existing bandit/satyr pool at a minority weight, mirroring how the vanilla slinger
  pool carries archers at weight 5). **Integration prerequisite:** the monolith must import the
  base donor (`ar_slinger_37`) into the overlay first (exactly like `import_base_game_bosses`
  does for base bosses), because a registry module's `apply(db, tags)` only sees the mod db.
- **MAP (separate lane, reported here):** add the armed pool's proxy to the chosen reachable
  Act-1/2 Greek bandit levels (or extend an existing bandit proxy's pool ref). Minority weight
  so throwers are a *flavor* of the pack, not the whole pack.

### C5. Verification the module ships with (`tools/patches/thrown_wielders.py`)
`verify(db, tags)` asserts, for every armed record:
- record exists and `Class = Monster`;
- `mesh` is in the throw-proven **RIG_WHITELIST**;
- the `rangedOneHand` anim block is present (throw-capable);
- `chanceToEquipRightHand > 0` and `lootRightHandItem1` resolves to >=1
  `WeaponHunting_RangedOneHand` weapon/table;
- the equip drop-slot weight is within the sane band (`1..10`);
- no `lootFinger2*` soul on a Common (no soul leak).
A `_negtest()` proves `verify` **fails** on each broken shape (non-thrown weapon, off-whitelist
rig, out-of-band drop).

### C6. Open questions for Will (veto inputs)
1. **Scope:** first wave = Greek bandit peltast only (recommended), or peltast + satyr
   trickster together?
2. **Density:** how common should throwers be - a rare flavor (~1 in 12 of a bandit pack) or a
   distinct "skirmisher" sub-pack that shows up in specific spots?
3. **Satyr look:** accept the Atlantis `libyansatyr01` rig for the trickster, or hold satyr
   until the base Act-1 satyr mesh is confirmed throw-capable?
4. **Reach:** Greece only (Act 1-2), or also arm a matching Egyptian/Oriental raider so throwers
   recur across acts?
5. **Amazon/maenad:** park (no throw-proven rig) or invest in a rig fix?

---

## Appendix - reproduction
All probes are read-only against the golden artifacts (`work/.../SoulvizierClassic.arz`
`b33c5a44`, `local/Levels_merged.arc` `9981085b`, stock TQAE `database.arz` + `Levels.arc`):
class sweep, reverse-reference graph thrown<-pool<-proxy<-level, per-level attribution vs
stock/SVAERA, donor dump, rig-whitelist extraction. Scripts in the session scratchpad
(`twa_*.py`).
