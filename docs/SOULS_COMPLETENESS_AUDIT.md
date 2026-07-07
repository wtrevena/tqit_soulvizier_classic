# Souls Completeness Audit

> Read-only audit of soul coverage in the built `SoulvizierClassic.arz`, produced against
> `work/SoulvizierClassic/Database/SoulvizierClassic.arz` for design-planning purposes: which
> Hero/Boss/Quest monsters have a wired, functional soul; which have a soul that exists but is
> unwired or a stub; which have no soul at all; and the full boss roster with core skills, as raw
> material for designing new souls. No em dashes by house style.

---

## 1. Methodology

**Database reads.** All records were read with the repo's own `.arz` reader,
`tools/arz_patcher.py`'s `ArzDatabase` class (`ArzDatabase.from_arz(path)`, `db.get_fields(name)`,
`db.record_names()`), the same module `tools/build_svc_database.py` and `tools/apply_svc_patches.py`
import and patch with. No binary format was reverse-engineered for this audit; the existing,
already-proven reader was reused as-is. Two new throwaway scripts (scratchpad only, not committed)
did the enumeration:

- **`audit_souls.py`** enumerates every `.dbr` record whose `monsterClassification` field is
  `Hero`, `Boss`, or `Quest` (the exact same field/value gate `wire_souls_to_monsters` in
  `tools/build_svc_database.py:340,364` uses to decide who is allowed to drop a soul), and
  classifies soul coverage per record, then deduplicates by `description` tag (the shared name-tag
  across a monster's Normal/Epic/Legendary level variants) into unique monsters.
- **`audit_bosses_deepdive.py`** repeats the enumeration filtered to `monsterClassification == Boss`,
  resolves every wired soul's granted skill/augments/stats (to detect stubs), and pulls each boss's
  own `skillName*` fields (its combat kit) as raw material for future soul design. It also loads
  each upstream `database.arz` (098i / 0.9 / 041 / 0.4 / beta04.1) with the same reader and diffs
  the set of distinct soul `(monster_type_dir, clean_name)` pairs (using
  `build_svc_database.py`'s own `parse_soul_name()` logic, copied verbatim) against the current
  build's soul catalog.

**How "wired" vs "not wired" is read.** Per `wire_souls_to_monsters`
(`tools/build_svc_database.py:248-427`), a monster's soul lives in the **Finger2** equipment slot:
`lootFinger2Item1` (the item reference, an `[N, E, L]` triplet or single path) and
`chanceToEquipFinger2` (the float percent chance that gates the drop; AE has no separate
"lootFinger2Chance" field, `chanceToEquipFinger2` **is** the overall equip/drop chance). A monster
counts as:
- **HAS** a wired soul if `lootFinger2Item1` references a path containing `soul` AND
  `chanceToEquipFinger2 > 0`.
- **Soul exists but NOT wired** if either (a) the same soul reference exists but
  `chanceToEquipFinger2 == 0` (explicitly gated off, e.g. by the 2026-07-05 Common/Champion fix), or
  (b) there is no soul reference on the monster at all, but a plausibly-matching soul item exists
  elsewhere in the database under `equipmentring\soul\` whose catalog name fuzzy-matches the
  monster's file name (same scoring heuristic `wire_souls_to_monsters` itself uses to find a match
  when auto-wiring: exact/prefix/substring name match plus a same-type-directory bonus, threshold
  score >= 10).
- **NONE** if there is no soul reference and no plausible catalog match.

**How a soul "stub" is detected.** A soul item record is flagged a stub if it has no
`itemSkillName` (no granted proc/summon), no `augmentSkillName1..4` (no granted skill-tree bonus),
and no nonzero core stat field (`characterLife/Mana/Strength/Intelligence/Dexterity`,
`characterOffensiveAbility/DefensiveAbility`, `offensivePhysicalMin/Max`, `defensivePhysical`,
`defensiveProtection`, `augmentAllLevel`) i.e. equipping it does essentially nothing; or if
`itemSkillName` is set but the referenced skill record does not resolve in the database (a broken
reference) or resolves with no `Class` (a placeholder record).

**A correction made mid-audit (important limitation of a naive approach).** An initial pass
restricted the record scan to paths containing `\creature\`/`\creatures\` (mirroring several
existing repo scripts, e.g. `tools/list_monsters_by_class.py`'s template-based approach). That
scan undercounted: it silently missed every monster living under `records\drxcreatures\`
(one path segment, not `\creatures\` as a delimited segment - e.g. the real SV/DRX superbosses
`q_leinth_47.dbr`, `murderbunny.dbr`), `records\drxmap\`, `records\test\`, and
`records\item\equipmentring\soul\test\`/`records\skills\...` (dev-scratch duplicates and
summoned-minion proxy records that also legitimately carry `monsterClassification`). The final
scripts scan **every** `.dbr` record in the database and gate purely on the `monsterClassification`
field value (matching the real production gate exactly), which recovered 169 additional
Hero/Boss/Quest records the path-filtered version missed, including 5 real named superbosses
(SP Toxeus `um_toxeus_99`, Leinth `q_leinth_47`, Murder Bunny, Cold Worm `boss_coldworm50`, Dagon
`boss_dagon_66`) that all turned out to already have functional wired souls.

**Caveats / known limitations of this audit:**
- **Dedup is by `description` tag.** Level/difficulty variants (Normal/Epic/Legendary, and
  multi-act reappearances such as Hades Form 3 or Aktaios) sharing one name tag are merged into one
  "unique monster" row, keeping the best (highest-ranked) status across variants. This is
  deliberate (it is how the game names them to the player) but means a variant-level count (997
  raw Hero/Boss/Quest records) differs from the unique-monster count (662).
  A few pre-fight "stage" forms that share a tag with their final form (`typhon_chains.dbr` sharing
  `tagMonsterName382` with the real farmable `boss_titan_typhon_*`; Hades Forms 1/2 sharing
  `xtagMonsterHades` with Form 3) are therefore correctly folded into their final form's HAS status,
  not reported as separate gaps, matching the documented design (only the final form that actually
  dies and drops loot needs a soul).
- **Non-combat "utility prop" records.** 15 records carry `monsterClassification` of `Boss` or
  `Quest` purely as a side effect of being built on `Monster.tpl`, but are not real fightable
  monsters (scripting triggers such as `xq02_greysoundrat.dbr`, `FileDescription`: "Used to Control
  the Sound System for the Grey Battle"; a 1-HP quest-chest blocker "Meliboea"). These were detected
  heuristically (`invincible == 1` or `characterLife < 200`, no `skillName*` fields, no soul
  reference at all) and are called out as a distinct `N/A (not a monster)` severity in Table A
  rather than silently dropped or miscounted as a real gap, and are excluded from the Table B boss
  roster (Table B is meant to be design input for real fights).
- **Skill lists in Table B are raw, not curated.** Every resolved `skillName*` field is listed
  (capped at 8 shown per boss, with a total count for the rest) exactly as stored; this includes
  generic shared passives (`armor_passive`, `globalproperties_normal01`, etc.) alongside genuinely
  signature attacks, because the ask was raw material for soul design, not a curated highlight reel.
- **`FileDescription` is a developer comment field**, not gameplay data; a few multi-variant bosses
  show a `FileDescription` from whichever variant happened to be scanned first, which can look
  mismatched (e.g. Hades Form 3's row shows "Not in game - credits scene only", a comment that
  belongs to the `credits_hades.dbr` variant folded into the same group). Treat it as a hint only.
- No `.arz` file in the repo was modified. All inspection was read-only; the two throwaway scripts
  live in the session scratchpad, not the repo.

---

## 2. TABLE A: soul-coverage gaps among Hero/Boss/Quest monsters

Of **662 unique Hero/Boss/Quest monsters** (662 distinct `description` tags; 997 raw records
counting level/difficulty variants), **616 already HAS a wired, working soul**. The remaining 46
rows below are every monster that is not a clean HAS, in full (no sampling/truncation).

Severity key: **High** = a real farmable Boss with no soul at all (none found: every Boss-classified
fightable monster in this build already has a soul; see Table B). **Medium** = a Hero or Quest
monster with no soul and no plausible existing-soul match. **Low** = a soul reference exists but is
unwired (zero chance) or only a low-confidence fuzzy match was found. **N/A (not a monster)** = a
non-combat scripting/utility record that happens to carry a Hero/Boss/Quest classification field but
is not a real fight (called out for completeness per "never drop findings", not a design gap).

| Severity | Name/Tag | What it is | Classification | Record | Levels | Variants | Status |
|---|---|---|---|---|---|---|---|
| Medium | tagMonsterName317 | Fleshrender | Hero | `records\creature\monster\rumormonsters\orient\jo7_raptor_30.dbr` | 30,33,36,50,52,54,65,67,69 | 3 | NONE |
| Medium | tagNewHero290 | Ambush! | Hero | `records\creature\monster\tidecrawler\um_anklesickle_13_ambush.dbr` | 13,39,57 | 1 | NONE |
| Medium | tagNewHero55 | no soul reference, no plausible catalog match | Hero | `records\creature\devices\darkobelisk\egypt_monolith_50.dbr` | 50,70,93 | 1 | NONE |
| Medium | tagNewHero62 | no soul reference, no plausible catalog match | Hero | `records\creature\devices\firetrap\um_thetrap_25.dbr` | 25,45,68 | 1 | NONE |
| Medium | tagAbomShaman | no soul reference, no plausible catalog match | Quest | `records\drxcreatures\bloodabomination\04_spiritcaller_40.dbr` | 40,41,42,56,57,58,71,72,73 | 3 | NONE |
| Medium | tagAnapaestNAME | 1H + Shield | Quest | `records\drxcreatures\drxdishonorguard\anapaest_45.dbr` | 51,64,75 | 1 | NONE |
| Medium | tagBWHighPriest | no soul reference, no plausible catalog match | Quest | `records\drxcreatures\bloodwitch\c_disciple_miniboss.dbr` | 39,56,71 | 1 | NONE |
| Medium | tagD2NPCakara | Kallixenia -- staff - Spirit-based powers -- Death Effect: Effects\Particles\Story\LichQueenNPCXform_FX -- Shown on Minimap | Quest | `records\drxcreatures\xurder\d2npc\01_akara.dbr` | 36,54,69 | 1 | NONE |
| Medium | tagD2NPCcharsi | no soul reference, no plausible catalog match | Quest | `records\drxcreatures\xurder\d2npc\01_charsi.dbr` | 36,54,69 | 1 | NONE |
| Medium | tagD2NPCgheed | no soul reference, no plausible catalog match | Quest | `records\drxcreatures\xurder\d2npc\01_gheed.dbr` | 36,54,69 | 1 | NONE |
| Medium | tagGitar3 | no soul reference, no plausible catalog match | Quest | `records\drxcreatures\crowheroes\gitar3.dbr` | 1 | 1 | NONE |
| Medium | tagJiaco | dw (champion) | Quest | `records\drxcreatures\crowheroes\jiaco.dbr` | 40,57,71 | 1 | NONE |
| Medium | tagLilLued | Standing Child | Quest | `records\drxcreatures\crowheroes\lillued.dbr` | 8 | 1 | NONE |
| Medium | tagMonsterName171 | Plague Feast | Quest | `records\drxcreatures\crowheroes\nomnom.dbr` | 13,39,56 | 1 | NONE |
| Medium | tagSkillName165 | Banner that is part of Bad Idea Quest #1- Has Death Anm & Disolves on Death | Quest | `records\xpack\quests\npc\non speaking\side\xsq22_killable_banner.dbr` | 34,53,68 | 1 | NONE |
| Medium | tagUrderBigLued | Hero - Blood Pact (Aura) / Djinn Blast / Elemental Chaos / Haste Aura | Quest | `records\drxcreatures\crowheroes\lillued_big.dbr` | 40,57,71 | 1 | NONE |
| Medium | tagUrderGorgus | DW Swords | Quest | `records\drxcreatures\crowheroes\gorgus.dbr` | 45,60,73 | 1 | NONE |
| Medium | tagUrderJabarto | not configured yet | Quest | `records\drxcreatures\crowheroes\jabarto.dbr` | 18,42,58 | 1 | NONE |
| Medium | tagUrderKaets | no soul reference, no plausible catalog match | Quest | `records\drxcreatures\crowheroes\kaets.dbr` | 44,60,73 | 1 | NONE |
| Medium | tagUrderKir4 | no soul reference, no plausible catalog match | Quest | `records\drxcreatures\crowheroes\kir4.dbr` | 20 | 1 | NONE |
| Medium | tagUrderKreeloo | no soul reference, no plausible catalog match | Quest | `records\drxcreatures\crowheroes\kreeloo.dbr` | 21,44,60 | 1 | NONE |
| Medium | tagUrderLess | no soul reference, no plausible catalog match | Quest | `records\drxcreatures\crowheroes\less.dbr` | 10,37,54 | 1 | NONE |
| Medium | tagUrderNumberouane | DW Swords | Quest | `records\drxcreatures\crowheroes\numberouane.dbr` | 45,60,73 | 1 | NONE |
| Medium | tagUrderZilla | DW Swords | Quest | `records\drxcreatures\crowheroes\zilla.dbr` | 45,60,73 | 4 | NONE |
| Medium | tagYerk | club | Quest | `records\drxcreatures\crowheroes\yerk.dbr` | 41,57,71 | 2 | NONE |
| Medium | xtagKillable_ElysianHero10 | Elysium Messenger -- Doesn't attack monsters -- Generates 2x anger -- Can Trigger BV / Appears as Quest | Quest | `records\xpack\quests\npc\non speaking\side\xsq21_escortmessenger.dbr` | 34,53,68 | 1 | NONE |
| Medium | xtagKillable_RhodesLaborer | Doesn't attack monsters - Generates extra anger -- Can Trigger BVs | Quest | `records\xpack\quests\npc\non speaking\side\xsq03_escortworker.dbr` | 30,50,56 | 1 | NONE |
| Medium | xtagMonsterFormicidHero03 | axe + shield | Quest | `records\drxcreatures\crowheroes\rainbowbright.dbr` | 46,61,74 | 1 | NONE |
| Low | tagMonsterNameSFM276 | Bow | Hero | `records\test\outsider_hero_poison_46.dbr` | 46,61,74 | 1 | NOT_WIRED_NO_REF |
| Low | tagMonsterNameSFM277 | 1H | Hero | `records\test\outsider_hero_melee_46.dbr` | 46,61,74 | 1 | NOT_WIRED_NO_REF |
| Low | tagMonsterNameSFM278 | Staff | Hero | `records\test\outsider_hero_caster_46.dbr` | 46,61,74 | 1 | NOT_WIRED_NO_REF |
| N/A (not a monster) | (no tag) | Used to Control the Sound System for the Grey Battle | Boss | `records\xpack\quests\npc\non speaking\main\xq02_greysoundrat.dbr` | 6,36,56 | 1 | NONE |
| N/A (not a monster) | (no tag) | Used to Control the Sound System for the Charon Battle | Boss | `records\xpack\quests\npc\non speaking\main\xq03_charonsoundrat.dbr` | 6,36,56 | 1 | NONE |
| N/A (not a monster) | (no tag) | Used to Control the Zapping of the Crystals Back and Forth | Boss | `records\xpack\quests\npc\non speaking\scripted\crystal_ss_rat.dbr` | 6,36,56 | 1 | NONE |
| N/A (not a monster) | (no tag) | Used to Control the Looping of Shade A walking into ToJ | Boss | `records\xpack\quests\npc\non speaking\scripted\toj_ss_rat a.dbr` | 6,36,56 | 1 | NONE |
| N/A (not a monster) | (no tag) | Used to Control the Looping of Shade B walking into ToJ | Boss | `records\xpack\quests\npc\non speaking\scripted\toj_ss_rat b.dbr` | 6,36,56 | 1 | NONE |
| N/A (not a monster) | (no tag) | Used to Control the Looping of Shade C walking into ToJ | Boss | `records\xpack\quests\npc\non speaking\scripted\toj_ss_rat c.dbr` | 6,36,56 | 1 | NONE |
| N/A (not a monster) | (no tag) | Used to Control the Looping of Shade D walking into ToJ | Boss | `records\xpack\quests\npc\non speaking\scripted\toj_ss_rat d.dbr` | 6,36,56 | 1 | NONE |
| N/A (not a monster) | (no tag) | Used to Control the Looping of Shade E walking into ToJ | Boss | `records\xpack\quests\npc\non speaking\scripted\toj_ss_rat e.dbr` | 6,36,56 | 1 | NONE |
| N/A (not a monster) | (no tag) | Used to Control if quest can be completed in Multiplayer | Boss | `records\xpack\quests\npc\non speaking\side\xsq03_multiplayerrat.dbr` | 6,36,56 | 1 | NONE |
| N/A (not a monster) | (no tag) | Used to Control the Zapping of the Crystals Back and Forth | Boss | `records\xpack\quests\npc\non speaking\scripted\crystal_ss_rat c.dbr` | 6,36,56 | 1 | NONE |
| N/A (not a monster) | (no tag) | Used to Control the Zapping of the Crystals Back and Forth | Boss | `records\xpack\quests\npc\non speaking\scripted\crystal_ss_rat d.dbr` | 6,36,56 | 1 | NONE |
| N/A (not a monster) | (no tag) | Used to Control the Zapping of the Crystals Back and Forth | Boss | `records\xpack\quests\npc\non speaking\scripted\crystal_ss_rat e.dbr` | 6,36,56 | 1 | NONE |
| N/A (not a monster) | (no tag) | Used to Control the Zapping of the Crystals Back and Forth | Boss | `records\xpack\quests\npc\non speaking\scripted\crystal_ss_rat f.dbr` | 6,36,56 | 1 | NONE |
| N/A (not a monster) | Meliboea | Locks the chest if talk to ling first | Boss | `records\drxmap\quest\blockersquirrel.dbr` | 1 | 1 | NONE |
| N/A (not a monster) | (no tag) | Quest" Class Rat used to keep ToJ Chests Locked -- Killed Via Quest | Quest | `records\xpack\quests\npc\non speaking\side\xsq20_ratforchests.dbr` | 6,36,56 | 1 | NONE |


### Upstream soul-roster cross-check

Every soul that exists in any upstream Soulvizier variant (098i, 0.9, 041, 0.4, beta04.1) is present
in the current build's soul catalog. **Zero souls were lost from the upstream roster** in this
build; nothing here indicates content regression from upstream on the soul-item side.

| Upstream variant | Total soul (type,name) pairs | Missing from current build |
|---|---|---|
| soulvizier_098i | 808 | none |
| soulvizier_0.9 | 726 | none |
| soulvizier_041 | 620 | none |
| soulvizier_0.4 | 620 | none |
| soulvizier_beta04.1 | 620 | none |


---

## 3. TABLE B: boss roster needing designed souls (full roster)

Every `monsterClassification == Boss` record in the built database, deduplicated by `description`
tag (60 unique bosses; 186 raw records across level/difficulty variants; 14 additional raw records
excluded as non-combat utility props, see Methodology). For each: the representative record path
(highest-level variant), the level spread across all variants, its own signature/core skills (from
`skillName*` fields, capped at 8 listed with a total count), and its existing soul's granted
content (or STUB / NO SOUL RECORD).

**Headline finding: only 1 of 60 bosses lacks a functional soul** - **Limos Lifeeater**
(`records\creature\monster\limos\um_frost_36.dbr`, tag `tagMonsterName169`, Demon race, levels
36/54/69). Its three soul variants (`limoslifeater_soul_{n,e,l}.dbr`) all resolve as real item
records but grant nothing: no `itemSkillName`, no `augmentSkillName1-4`, no nonzero stat field on
any of the three tiers. This matches the previously-tracked "Priority 5: Soul Reworks" item in the
repo's (stale, per `CLAUDE.md`) `SOUL_AUDIT.md`, independently reconfirmed here directly against the
built `.arz`. All previously-flagged "no soul at all" superbosses in that older document (SP Toxeus,
Leinth, Murder Bunny, Secret Passage Hades, Cold Worm, Dagon) were independently verified in this
audit to now have fully wired, functional souls with `chanceToEquipFinger2` of 66-100%.

| Boss Name/Tag | Record Path | Levels | Core/Signature Skills | Existing Soul Status |
|---|---|---|---|---|
| tagNewHero27 | `records\creature\monster\bat\um_elephantsnatcher_17.dbr` | 17,50,66 | automatoi_minstun [Skill_Passive] - ^gFrost Strike<br>hero_modifier [Skill_Passive] - ^gFrost Strike<br>bonusdamage_physical [Skill_Passive] - Adds Absolute Phys. Dmg +10 per level for 100 levels<br>physdmg_meleeonly01 [Skill_Passive] - Phys. Dmg scaling for melee enemies in Epic/Legendary - zerg monsters<br>nessus_meleeattack [Skill_AttackWeapon] - tagSkillName133<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic01 [Skill_Passive] - Global Monster Adjustment - Epic - No Longer Active<br>... (9 total skillName fields) | `elephantsnatcher_soul_e.dbr` grants lifedrain [Skill_AttackSpellChaos]; augments: +2 drxbattlerage; stats: offensivePhysicalMin=10.0, offensivePhysicalMax=20.0, characterLifeModifier=8.0<br>`elephantsnatcher_soul_l.dbr` grants lifedrain [Skill_AttackSpellChaos]; augments: +2 drxbattlerage; stats: offensivePhysicalMin=10.0, offensivePhysicalMax=20.0, characterLifeModifier=8.0<br>`elephantsnatcher_soul_n.dbr` grants lifedrain [Skill_AttackSpellChaos]; augments: +2 drxbattlerage; stats: offensivePhysicalMin=10.0, offensivePhysicalMax=20.0, characterLifeModifier=8.0 |
| tagNewHero63 | `records\creature\monster\beetle\um_grimshell_33.dbr` | 33,54,69 | armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>flameskull_ring [Skill_AttackProjectileFan] - tagSkillName042<br>stygianreaver_bolt [Skill_AttackProjectile] - tagSkillName042<br>physdmg_meleeonly01 [Skill_Passive] - Phys. Dmg scaling for melee enemies in Epic/Legendary - zerg monsters<br>bonusdamage_vita_+1perlevelx100 [Skill_Passive] - ^gFrost Strike<br>ondeath_necronova [Skill_AttackProjectileRing] - tagSkillName193<br>shriekbrood_ghost_summon3 [Skill_SpawnPet]<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>... (10 total skillName fields) | `grimshell_soul_e.dbr` grants stygianreaver_bolt [Skill_AttackProjectile]; augments: +3 drxspellbreaker, +2 drxdeathchillaura_necrosis; stats: characterLife=269.0<br>`grimshell_soul_l.dbr` grants stygianreaver_bolt [Skill_AttackProjectile]; augments: +4 drxspellbreaker, +3 drxdeathchillaura_necrosis; stats: characterLife=391.0<br>`grimshell_soul_n.dbr` grants stygianreaver_bolt [Skill_AttackProjectile]; augments: +2 drxspellbreaker, +1 drxdeathchillaura_necrosis; stats: characterLife=160.0 |
| tagMonsterName293 | `records\creature\monster\bossarena\boss_satyrshaman_55.dbr` | 55,69,75 | damage_arenafirebonus [Skill_BuffRadiusToggled]<br>arena_flamesurge [Skill_AttackProjectileFan] - tagSkillName113<br>arena_volcanicorb [Skill_AttackProjectile] - tagSkillName114<br>arena_volcanicorb_immolation [Skill_ProjectileModifier] - tagSkillName101<br>arena_volcanicorb_fragmentation [Skill_ProjectileModifier] - tagSkillName106<br>arena_meteor [Skill_DropProjectileTelekinesis] - teh big one<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>... (11 total skillName fields) | `darksatyrshaman_soul_e.dbr` augments: +2 drxregrowth; stats: characterMana=92.0, characterIntelligence=19.0<br>`darksatyrshaman_soul_l.dbr` augments: +3 drxregrowth; stats: characterMana=132.0, characterIntelligence=30.0<br>`darksatyrshaman_soul_n.dbr` augments: +1 drxregrowth; stats: characterMana=60.0, characterIntelligence=10.0 |
| tagNewHero316 | `records\creature\monster\carrionbird\us_mormo_16.dbr` | 16,41,57 | etherealshock [Skill_AttackRadiusLightning] - tagNewSkill301<br>ternion [Skill_AttackWeaponRangedSpread] - tagSkillName213<br>physdmg_meleeonly02 [Skill_Passive] - Phys. Dmg scaling for melee enemies in Epic/Legendary - weak zerg monsters<br>drxdeathward [Skill_PassiveOnLifeBuffSelf] - tagSkillName039<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>dodgeprojectile_1%perlevelx100 [Skill_Passive] - +5% per level<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic01 [Skill_Passive] - Global Monster Adjustment - Epic - No Longer Active<br>... (13 total skillName fields) | `stormbird_soul_e.dbr` augments: +3 drxstormwispsummoning; stats: characterLife=141.0<br>`stormbird_soul_l.dbr` augments: +4 drxstormwispsummoning; stats: characterLife=236.0<br>`stormbird_soul_n.dbr` augments: +2 drxstormwispsummoning; stats: characterLife=72.0 |
| tagNewHero236 | `records\creature\monster\dragonlich\um_permean_35.dbr` | 35,56,70 | permean_aura [Skill_BuffRadiusToggled]<br>permean_summon [Skill_SpawnPet] - tagSkillName068<br>permean_sandspire [Skill_AttackProjectileBurst] - Pierce + Phys damage<br>permean_sandbreath [Skill_AttackWave] - Fumble + Disrupt + Pierce/Fire damage<br>permean_extinction [Skill_AttackRadius] - Phys/Fire + Total Speed Slow<br>permean_sandstorm [Skill_AttackRadius] - Used on death - no damage<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>uber_scaling [Skill_Passive] - ^gFrost Strike<br>... (10 total skillName fields) | `permean_soul_e.dbr` grants permean_extinction [Skill_AttackRadius]; augments: +4 drxenslavespirit; stats: characterLife=245.0, offensivePhysicalMin=24.0<br>`permean_soul_l.dbr` grants permean_extinction [Skill_AttackRadius]; augments: +5 drxenslavespirit; stats: characterLife=372.0, offensivePhysicalMin=31.0<br>`permean_soul_n.dbr` grants permean_extinction [Skill_AttackRadius]; augments: +3 drxenslavespirit; stats: characterLife=150.0, offensivePhysicalMin=15.0 |
| tagNewHero179 | `records\creature\monster\gorgon\um_kaublasia_19.dbr` | 19,46,63 | bonusdamage_fire_+1perlevelx100 [Skill_Passive] - ^gFrost Strike<br>damagephysical_passivemodifier01 [Skill_Passive] - 10% physical damage per level<br>kaublasia_firebonus [Skill_BuffRadiusToggled]<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>duneraider_flamestrike [Skill_DropProjectileTelekinesis] - Flames from the sky<br>kaublasia_burst [Skill_AttackProjectileRing] - tagSkillName022<br>drxheatshield [Skill_BuffOther]<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>... (13 total skillName fields) | `kaublasia_soul_e.dbr` augments: +6 bowtraining, +4 drxfireenchantment_brimstone; stats: characterDexterity=24.0, characterDefensiveAbility=50.0<br>`kaublasia_soul_l.dbr` augments: +7 bowtraining, +5 drxfireenchantment_brimstone; stats: characterDexterity=29.0, characterDefensiveAbility=76.0<br>`kaublasia_soul_n.dbr` augments: +5 bowtraining, +3 drxfireenchantment_brimstone; stats: characterDexterity=15.0, characterDefensiveAbility=28.0 |
| tagNewHero182 | `records\creature\monster\human\um_phagia_44.dbr` | 34,44,55,60,70,75 | armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic01 [Skill_Passive] - Global Monster Adjustment - Epic - No Longer Active<br>globalproperties_legendary01 [Skill_Passive] - Global Monster Adjustment - Legendary - No Longer Active | `phagia_soul_e.dbr` grants summon_phagia [Skill_SpawnPet]<br>`phagia_soul_l.dbr` grants summon_phagia [Skill_SpawnPet]<br>`phagia_soul_n.dbr` grants summon_phagia [Skill_SpawnPet]<br>`maenadsorceress_soul_e.dbr` augments: +2 drxlightningbolt; stats: characterIntelligence=24.0<br>`maenadsorceress_soul_l.dbr` augments: +3 drxlightningbolt; stats: characterIntelligence=36.0<br>`maenadsorceress_soul_n.dbr` augments: +1 drxlightningbolt; stats: characterIntelligence=14.0 |
| tagMonsterName169 | `records\creature\monster\limos\um_frost_36.dbr` | 36,54,69 | limos_consumelife02 [Skill_AttackSpell] - ^gLife Leech<br>attack_damagemodifier_02 [Skill_Passive] - 10% physical damage per level - 50 Levels<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>physdmg_meleeonly [Skill_Passive] - Phys. Dmg scaling for melee enemies in Epic/Legendary<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic01 [Skill_Passive] - Global Monster Adjustment - Epic - No Longer Active<br>globalproperties_legendary01 [Skill_Passive] - Global Monster Adjustment - Legendary - No Longer Active<br>hero_cold [Skill_Passive] - ^gFrost Strike | `limoslifeater_soul_e.dbr` STUB (no itemSkillName, no augmentSkillName1-4, no nonzero core stat fields)<br>`limoslifeater_soul_l.dbr` STUB (no itemSkillName, no augmentSkillName1-4, no nonzero core stat fields)<br>`limoslifeater_soul_n.dbr` STUB (no itemSkillName, no augmentSkillName1-4, no nonzero core stat fields) |
| tagNewHero307 | `records\creature\monster\limos\um_uber_45.dbr` | 45,61,73 | armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>physdmg_meleeonly [Skill_Passive] - Phys. Dmg scaling for melee enemies in Epic/Legendary<br>drxcoldaura [Skill_BuffSelfToggled] - COLD AURA<br>glacialassault [Skill_WeaponPool_ChargedLinear] - Changed melee attack - +Cold + ADCTH +MS slow<br>bonusdamage_cold_+5perlevelx500 [Skill_Passive] - ^gFrost Strike<br>chance_freeze [Skill_Passive] - ^gFrost Strike<br>frostattack_radius03 [Skill_AttackProjectileRing] - tagSkillName193<br>chillingair [Skill_AttackProjectileAreaEffect] - tagNewSkill59<br>... (13 total skillName fields) | `uber_soul_e.dbr` grants barmanu_blizzard [Skill_DropProjectileTelekinesis]; augments: +4 drxcoldaura, +3 drxfreezingblast; stats: characterLifeModifier=12.0<br>`uber_soul_l.dbr` grants barmanu_blizzard [Skill_DropProjectileTelekinesis]; augments: +5 drxcoldaura, +4 drxfreezingblast; stats: characterLifeModifier=15.0<br>`uber_soul_n.dbr` grants barmanu_blizzard [Skill_DropProjectileTelekinesis]; augments: +3 drxcoldaura, +2 drxfreezingblast; stats: characterLifeModifier=9.0 |
| tagNewHero317 | `records\creature\monster\naiad\ur_uber_45.dbr` | 45,60,73 | syrinx_corruptionswrath [Skill_AttackProjectile] - tagSkillName189<br>ondeath_voidnova [Skill_AttackProjectileRing] - tagSkillName193<br>healthregen_+1perlevelx100 [Skill_Passive] - ^gFrost Strike<br>voidlash_boltburst [Skill_AttackProjectileBurst] - tagSkillName113<br>junglecreep_summon4 [Skill_SpawnPet] - Dark Junglecreep<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>disruption [Skill_AttackProjectileAreaEffect] - Disruption + level*3 DA reduction<br>voidlash_burst [Skill_AttackProjectileAreaEffect] - tagNewSkill55<br>... (13 total skillName fields) | `syrinx_soul_e.dbr` grants syrinx_chainleech [Skill_AttackChain]; augments: +2 drxsylvannymphsummons; stats: characterDexterity=22.0<br>`syrinx_soul_l.dbr` grants syrinx_chainleech [Skill_AttackChain]; augments: +3 drxsylvannymphsummons; stats: characterDexterity=33.0<br>`syrinx_soul_n.dbr` grants syrinx_chainleech [Skill_AttackChain]; augments: +1 drxsylvannymphsummons; stats: characterDexterity=15.0 |
| tagMonsterName004 | `records\creature\monster\questbosses\boss_chimaera_35.dbr` | 29,32,35,49,51,53,64,66,68 | chimera_firebreath [Skill_AttackProjectileRing] - Short-Range Attack - Fire DoT x 3 sec<br>chimera_deathring [Skill_AttackRadius] - Chimera's Death Ring - Lightning Dmg + Fumble and Skill Disruption for 4 Sec<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>globalproperties_legendary_boss [Skill_Passive] - Global Monster Adjustment - Legendary<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>boss_conversionimmunity [Skill_Passive] - Boss Skill - Immunity to Conversion/Taunt/Fear/Petrify + 90% Mana Leech Resist + 50% Burn Resistance + 90% Percent Life Resistance + Racial Bonus vs Pets +Disruption Immunity + Life Leech Resistance + Total Life + Dodging<br>all_hpscaling_passive [Skill_Passive] - tagSkillName027<br>... (9 total skillName fields) | `chimera_soul_e.dbr` grants summon_chimera [Skill_SpawnPet]; stats: characterDexterity=-28.0, characterLifeModifier=16.0<br>`chimera_soul_l.dbr` grants summon_chimera [Skill_SpawnPet]; stats: characterDexterity=-37.0, characterLifeModifier=19.0<br>`chimera_soul_n.dbr` grants summon_chimera [Skill_SpawnPet]; stats: characterDexterity=-20.0, characterLifeModifier=14.0 |
| tagMonsterName122 | `records\creature\monster\questbosses\boss_chinatelkine_ormenos_44.dbr` | 38,41,44,55,57,59,70,71,73 | ormenos_droptelekinesis [Skill_DropProjectileTelekinesis] - Drop stuff from the ceiling - Physical Damage<br>ormenos_telekinesis [Skill_AttackTelekinesis] - Picks up stalactites and throws them - Phys Dmg<br>ormenos_summonfiresprites [Skill_AttackProjectileSpawnPet] - Summon Fire Sprites<br>ormenos_energyblast [Skill_AttackProjectile] - Cold + Life + Disruption + Slow x 3 sec<br>ormenos_shortrangeblasts [Skill_AttackProjectile] - Cold + Life Dmg<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>... (13 total skillName fields) | `ormenos_soul_e.dbr` grants ormenos_energyblast [Skill_AttackProjectileFan]; stats: characterMana=377.0<br>`ormenos_soul_l.dbr` grants ormenos_energyblast [Skill_AttackProjectileFan]; stats: characterMana=458.0<br>`ormenos_soul_n.dbr` grants ormenos_energyblast [Skill_AttackProjectileFan]; stats: characterMana=220.0 |
| tagMonsterName155 | `records\creature\monster\questbosses\boss_cyclops_polyphemus_20.dbr` | 16,19,20,41,43,44,57,59 | cyclops_treebreakerroar [Skill_AttackProjectileRing] - Sweet<br>cyclops_stomp [Skill_AttackRadius] - Cyclops' Stomp Attack - Phys Dmg and 3-4 sec disruption<br>cyclops_clubslam [Skill_AttackProjectile] - Cyclops' Club Slam - High Phys Dmg + Low Lightning Dmg + stun for 2-3 sec<br>cyclops_terrifyingroar [Skill_AttackProjectileRing] - Cyclops roars and slows his enemies + drops their OA+DA by 100 for 6 seconds<br>cyclops_treebreakercharge [Skill_AttackWeapon] - Super Sweet<br>cyclops_attack [Skill_AttackWeapon] - 50 Armor Reduction x 5 sec / Uses 1H attack<br>typhon_passiveproperties [Skill_Passive] - Difficulty Adjustment<br>bonusdamage_physical_+8perlevelx100 [Skill_Passive] - ^gFrost Strike<br>... (17 total skillName fields) | `polyphemus_soul_e.dbr` grants cyclops_groundsmash [Skill_AttackProjectile]; stats: characterLife=241.0, offensivePhysicalMin=27.0, characterLifeModifier=12.0<br>`polyphemus_soul_l.dbr` grants cyclops_groundsmash [Skill_AttackProjectile]; stats: characterLife=340.0, offensivePhysicalMin=39.0, characterLifeModifier=14.0<br>`polyphemus_soul_n.dbr` grants cyclops_groundsmash [Skill_AttackProjectile]; stats: characterLife=120.0, offensivePhysicalMin=15.0, characterLifeModifier=10.0 |
| tagMonsterName1184 | `records\creature\monster\questbosses\boss_daemonbull_yaoguai_41.dbr` | 35,38,41,53,55,57,68,70,71 | yaoguai_demoncharge [Skill_AttackWeaponCharge] - Yaoguai's Demon-Bull Charge - High Phys Dmg w 50% Pierce + 4 sec Disruption<br>yaoguai_gore [Skill_AttackRadius] - Yaoguai's Melee Goring Attack - Phys + Bleed DoT<br>yaoguai_flamering [Skill_AttackRadius] - Yaoguai's Flame Ring Attack - Fire DoT<br>yaoguai_summonshadowstalkers [Skill_SpawnPetMonster] - Yaoguai summons his ShadowStalker friends<br>attack_damagemodifier_02 [Skill_Passive] - 10% physical damage per level - 50 Levels<br>yaoguai_stonehand [Skill_AttackProjectileDebuf]<br>charge_concussivedamage [Skill_AttackWeaponCharge] - tagSkillName137<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>... (14 total skillName fields) | `yaoguai_soul_e.dbr` grants yaoguai_flamering [Skill_AttackRadius]; stats: characterLifeModifier=18.0<br>`yaoguai_soul_l.dbr` grants yaoguai_flamering [Skill_AttackRadius]; stats: characterLifeModifier=22.0<br>`yaoguai_soul_n.dbr` grants yaoguai_flamering [Skill_AttackRadius]; stats: characterLifeModifier=15.0 |
| tagMonsterName1186 | `records\creature\monster\questbosses\boss_dragonliche_63.dbr` | 57,60,63,71,73,75 | dragonliche_freezingbreath [Skill_AttackProjectileRing] - Short-Range Wide-Spread Attack - Cold DoT + 6-8 Sec Freezing<br>dragonliche_buffetingwings [Skill_AttackProjectileRing] - Cold Dmg + Slow for 7-9 Sec + Fumble + Disruption<br>dragonliche_decomposition [Skill_AttackRadius] - Slows + Lowers Resistance + Lowers OA/DA + Poisons DoT + %Life Dmg + Steals Pets for 10 seconds<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>globalproperties_legendary_boss [Skill_Passive] - Global Monster Adjustment - Legendary<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>boss_conversionimmunity [Skill_Passive] - Boss Skill - Immunity to Conversion/Taunt/Fear/Petrify + 90% Mana Leech Resist + 50% Burn Resistance + 90% Percent Life Resistance + Racial Bonus vs Pets +Disruption Immunity + Life Leech Resistance + Total Life + Dodging<br>... (9 total skillName fields) | `dragonliche_soul_e.dbr` grants galeforce [Skill_AttackRadius]<br>`dragonliche_soul_l.dbr` grants galeforce [Skill_AttackRadius]<br>`dragonliche_soul_n.dbr` grants galeforce [Skill_AttackRadius] |
| tagMonsterName1182 | `records\creature\monster\questbosses\boss_gargantuanyeti_38.dbr` | 32,35,38,51,53,55,66,68,70 | gargantuanyeti_freezingbreath [Skill_AttackProjectileRing] - Short-Range Wide-Spread Attack - Cold Dmg + 4 Sec Freeze<br>attack_damagemodifier_02 [Skill_Passive] - 10% physical damage per level - 50 Levels<br>gargantuanyeti_iceblast [Skill_AttackProjectileRing] - Cold Dmg + 30% Slow for 3 Sec (Ring)<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>globalproperties_legendary_boss [Skill_Passive] - Global Monster Adjustment - Legendary<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>boss_conversionimmunity [Skill_Passive] - Boss Skill - Immunity to Conversion/Taunt/Fear/Petrify + 90% Mana Leech Resist + 50% Burn Resistance + 90% Percent Life Resistance + Racial Bonus vs Pets +Disruption Immunity + Life Leech Resistance + Total Life + Dodging<br>... (10 total skillName fields) | `gargantuanyeti_soul_e.dbr` grants yeti_freezingblast [Skill_AttackBuffRadius]; augments: +4 drxcoldaura; stats: characterLife=344.0, characterDexterity=-27.0<br>`gargantuanyeti_soul_l.dbr` grants yeti_freezingblast [Skill_AttackBuffRadius]; augments: +5 drxcoldaura; stats: characterLife=413.0, characterDexterity=-40.0<br>`gargantuanyeti_soul_n.dbr` grants yeti_freezingblast [Skill_AttackBuffRadius]; augments: +3 drxcoldaura; stats: characterLife=200.0, characterDexterity=-20.0 |
| tagMonsterName143 | `records\creature\monster\questbosses\boss_gorgon_euryale_23.dbr` | 17,20,23,42,44,46,58,59,61 | gorgon_iceenchantment [Skill_BuffSelfToggled] - tagSkillName027<br>Records\Skills\Boss Skills\Gorgon_SummonGuards.dbr (UNRESOLVED)<br>gorgon_petrify [Skill_AttackProjectile] - Gorgon's Petrifying Gaze<br>Records\Skills\Boss Skills\Gorgon_SummonArchers.dbr (UNRESOLVED)<br>gorgon_healing [Skill_GiveBonus] - Healin' for da Gorgon Queens<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>globalproperties_legendary_boss [Skill_Passive] - Global Monster Adjustment - Legendary<br>... (13 total skillName fields) | `euryale_soul_e.dbr` grants drxregrowth [Skill_GiveBonus]; augments: +3 drxstormnimbus_heartoffrost; stats: characterMana=276.0, characterIntelligence=21.0, characterDexterity=13.0<br>`euryale_soul_l.dbr` grants drxregrowth [Skill_GiveBonus]; augments: +4 drxstormnimbus_heartoffrost; stats: characterMana=375.0, characterIntelligence=32.0, characterDexterity=21.0<br>`euryale_soul_n.dbr` grants drxregrowth [Skill_GiveBonus]; augments: +2 drxstormnimbus_heartoffrost; stats: characterMana=150.0, characterIntelligence=14.0, characterDexterity=7.0 |
| tagMonsterName145 | `records\creature\monster\questbosses\boss_gorgon_medusa_24.dbr` | 18,21,24,42,44,46,58,60,61 | gorgon_fireenchantment [Skill_BuffSelfToggled] - tagSkillName105<br>Records\Skills\Boss Skills\Gorgon_SummonGuards.dbr (UNRESOLVED)<br>gorgon_petrify [Skill_AttackProjectile] - Gorgon's Petrifying Gaze<br>Records\Skills\Boss Skills\Gorgon_SummonArchers.dbr (UNRESOLVED)<br>regrowth [Skill_GiveBonus] - tagSkillName072<br>regrowth_acceleratedgrowth [Skill_Modifier] - tagSkillName075<br>regrowth_dissemination [SkillSecondary_ChainBonus] - tagSkillName073<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>... (15 total skillName fields) | `medusa_soul_e.dbr` grants medusa_petrify [Skill_AttackProjectile]; augments: +3 drxfireenchantment; stats: characterIntelligence=15.0, characterDexterity=17.0<br>`medusa_soul_l.dbr` grants medusa_petrify [Skill_AttackProjectile]; augments: +4 drxfireenchantment; stats: characterIntelligence=21.0, characterDexterity=23.0<br>`medusa_soul_n.dbr` grants medusa_petrify [Skill_AttackProjectile]; augments: +2 drxfireenchantment; stats: characterIntelligence=8.0, characterDexterity=10.0 |
| tagMonsterName144 | `records\creature\monster\questbosses\boss_gorgon_sstheno_22.dbr` | 16,19,22,41,43,45,57,59,60 | takedown [Skill_AttackWeaponCharge] - tagSkillName089<br>gorgon_poisonenchant [Skill_BuffSelfToggled] - tagSkillName057<br>Records\Skills\Boss Skills\Gorgon_SummonGuards.dbr (UNRESOLVED)<br>gorgon_petrify [Skill_AttackProjectile] - Gorgon's Petrifying Gaze<br>Records\Skills\Boss Skills\Gorgon_SummonArchers.dbr (UNRESOLVED)<br>regrowth [Skill_GiveBonus] - tagSkillName072<br>regrowth_acceleratedgrowth [Skill_Modifier] - tagSkillName075<br>regrowth_dissemination [SkillSecondary_ChainBonus] - tagSkillName073<br>... (16 total skillName fields) | `sstheno_soul_e.dbr` augments: +3 drxenvenomweapon, +3 speartraining; stats: characterStrength=19.0, characterDexterity=18.0, characterOffensiveAbility=62.0, offensivePhysicalMin=18.0<br>`sstheno_soul_l.dbr` augments: +4 drxenvenomweapon, +4 speartraining; stats: characterStrength=29.0, characterDexterity=28.0, characterOffensiveAbility=91.0, offensivePhysicalMin=25.0<br>`sstheno_soul_n.dbr` augments: +2 drxenvenomweapon, +2 speartraining; stats: characterStrength=12.0, characterDexterity=12.0, characterOffensiveAbility=35.0, offensivePhysicalMin=10.0 |
| tagMonsterName120 | `records\creature\monster\questbosses\boss_greektelkine_megalesios_27.dbr` | 21,24,27,44,46,48,60,61,63 | megalesios_summon_limos [Skill_AttackProjectileSpawnPet] - Spawns Limos Minions<br>megalesios_spectralblast [Skill_AttackSpellChaos] - Short Range - High Lightning Damage<br>megalesios_spawnmegalesiosspirit [Skill_SpawnMegalesiosSpirit]<br>megalesios_uberblast [Skill_AttackSpellChaos] - Giganto Blast for Blowing up Conduit<br>megalesios_thunderball [Skill_AttackProjectileAreaEffect] - tagSkillName020<br>megalesios_thunderball_concussiveblast [Skill_ProjectileModifier] - tagSkillName021<br>megalesios_rangedenergyblast [Skill_AttackProjectile] - Long Range - High Life Damage + 2 sec disruption<br>telkine_mindcontrolblast [Skill_AttackRadius] - Radius Attack Skill with Lightning Dmg + Conversion for 10-12 Seconds (vs. Pets)<br>... (17 total skillName fields) | `megalesios_soul_e.dbr` grants thunderballnova [Skill_AttackProjectileRing]; augments: +4 drxthunderball; stats: characterMana=211.0<br>`megalesios_soul_l.dbr` grants thunderballnova [Skill_AttackProjectileRing]; augments: +5 drxthunderball; stats: characterMana=292.0<br>`megalesios_soul_n.dbr` grants thunderballnova [Skill_AttackProjectileRing]; augments: +3 drxthunderball; stats: characterMana=125.0 |
| tagMonsterName126 | `records\creature\monster\questbosses\boss_hydra_66.dbr` | 60,63,66 | hydra_firebreath [Skill_AttackProjectileBurst] - Fire DoT x 3 sec<br>hydra_arcticbreath [Skill_AttackProjectileBurst] - Cold DoT + Slow for 6 Sec<br>hydra_poisonbreath [Skill_AttackProjectileBurst] - Poison DoT + % Life Dmg + Lower Resistances + Disruption + Fumble x 8 sec<br>hydra_superbite [Skill_AttackWeapon] - High-Damage Physical w 15% Pierce + Poison DoT<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>globalproperties_legendary_boss [Skill_Passive] - Global Monster Adjustment - Legendary<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>... (10 total skillName fields) | `hydra_soul_e.dbr` grants summon_hydra [Skill_SpawnPet]; stats: characterLife=397.0, offensivePhysicalMin=31.0, offensivePhysicalMax=63.0<br>`hydra_soul_l.dbr` grants summon_hydra [Skill_SpawnPet]; stats: characterLife=557.0, offensivePhysicalMin=37.0, offensivePhysicalMax=76.0<br>`hydra_soul_n.dbr` grants summon_hydra [Skill_SpawnPet]; stats: characterLife=275.0, offensivePhysicalMin=19.0, offensivePhysicalMax=42.0 |
| tagMonsterName1185 | `records\creature\monster\questbosses\boss_manticore_56.dbr` | 50,53,56,65,68,70 | manticore_lightningbreath [Skill_AttackProjectileRing] - Short-Range Attack - Lightning Dmg<br>manticore_poisonquills [Skill_AttackProjectileBurst] - Fires poisonous quills from his tail - Phys + Poison DoT x 3 sec + Disruption-Fumble x 3 Sec<br>manticore_pounce [Skill_AttackWeapon] - High-Damage Physical w 15% Pierce + Poison DoT<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>globalproperties_legendary_boss [Skill_Passive] - Global Monster Adjustment - Legendary<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>boss_conversionimmunity [Skill_Passive] - Boss Skill - Immunity to Conversion/Taunt/Fear/Petrify + 90% Mana Leech Resist + 50% Burn Resistance + 90% Percent Life Resistance + Racial Bonus vs Pets +Disruption Immunity + Life Leech Resistance + Total Life + Dodging<br>... (9 total skillName fields) | `manticore_soul_e.dbr` grants manticore_quills [Skill_AttackProjectileBurst]<br>`manticore_soul_l.dbr` grants manticore_quills [Skill_AttackProjectileBurst]<br>`manticore_soul_n.dbr` grants manticore_quills [Skill_AttackProjectileBurst] |
| tagMonsterName286 | `records\creature\monster\questbosses\boss_minotaurlord_26.dbr` | 20,23,26,44,46,47,59,61,62 | dualweapontraining [Skill_WPAttack_BasicAttack] - Allows dual wield / Adds chance to use both weapons at once<br>earthfury [Skill_AttackProjectileAreaEffect] - AE small radius - Blast of Rock<br>onslaught [Skill_WeaponPool_ChargedLinear] - Changed melee attack - each hit increases melee damage modifier<br>onslaught_ardor [Skill_Modifier] - Battle Rage modifier - increases attack and movement speed<br>onslaught_hamstring [Skill_Modifier] - Battle Rage modifier - adds bonus damage<br>bonusdamage_fire_+1perlevelx100 [Skill_Passive] - ^gFrost Strike<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>... (14 total skillName fields) | `minotaurlord_soul_e.dbr` augments: +4 drxdualweapontraining, +3 drxonslaught; stats: characterStrength=36.0, characterOffensiveAbility=90.0, offensivePhysicalMin=19.0, defensivePhysical=16.0<br>`minotaurlord_soul_l.dbr` augments: +5 drxdualweapontraining, +4 drxonslaught; stats: characterStrength=49.0, characterOffensiveAbility=115.0, offensivePhysicalMin=27.0, defensivePhysical=20.0<br>`minotaurlord_soul_n.dbr` augments: +3 drxdualweapontraining, +2 drxonslaught; stats: characterStrength=25.0, characterOffensiveAbility=50.0, offensivePhysicalMin=10.0, defensivePhysical=15.0 |
| tagMonsterName1183 | `records\creature\monster\questbosses\boss_neanderthalchief_barmanu_37.dbr` | 31,34,37,51,53,54,66,68,69 | barmanu_warshout [Skill_AttackProjectileRing] - Medium-Range Wide-Spread Attack - 3-5 Sec Stun<br>barmanu_blizzard [Skill_DropProjectileTelekinesis] - Frost Storm<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>globalproperties_legendary_boss [Skill_Passive] - Global Monster Adjustment - Legendary<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>boss_conversionimmunity [Skill_Passive] - Boss Skill - Immunity to Conversion/Taunt/Fear/Petrify + 90% Mana Leech Resist + 50% Burn Resistance + 90% Percent Life Resistance + Racial Bonus vs Pets +Disruption Immunity + Life Leech Resistance + Total Life + Dodging<br>attack_damagemodifier_02 [Skill_Passive] - 10% physical damage per level - 50 Levels<br>... (10 total skillName fields) | `barmanu_soul_e.dbr` grants barmanu_blizzard [Skill_DropProjectileTelekinesis]; augments: +8 blunttraining, +4 drxwarhorn; stats: characterOffensiveAbility=91.0, defensivePhysical=9.0<br>`barmanu_soul_l.dbr` grants barmanu_blizzard [Skill_DropProjectileTelekinesis]; augments: +9 blunttraining, +5 drxwarhorn; stats: characterOffensiveAbility=128.0, defensivePhysical=11.0<br>`barmanu_soul_n.dbr` grants barmanu_blizzard [Skill_DropProjectileTelekinesis]; augments: +7 blunttraining, +3 drxwarhorn; stats: characterOffensiveAbility=60.0, defensivePhysical=8.0 |
| tagMonsterName110 | `records\creature\monster\questbosses\boss_necromancer_alastor_24.dbr` | 18,21,24,42,44,46,58,60,61 | alastor_rangedblast [Skill_AttackProjectile] - Cold + Life Damage<br>alastor_summonskeletonwarrior [Skill_AttackProjectileSpawnPet] - Spawns Skeletal Minions<br>alastor_summonskeletonarcher [Skill_AttackProjectileSpawnPet] - Spawns Skeletal Minions<br>ondeath_necronova [Skill_AttackProjectileRing] - tagSkillName193<br>alastor_manaleech [Skill_AttackSpell] - Mana Leech<br>alastor_lifeleech [Skill_AttackSpell] - Life Leech<br>alastor_circleofdecay [Skill_BuffAttackRadiusToggled] - Circle of Decay - Cold+Life Dmg<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>... (14 total skillName fields) | `alastor_soul_e.dbr` augments: +3 drxdeathchillaura, +3 stafftraining; stats: characterLife=158.0, characterMana=204.0, characterIntelligence=23.0<br>`alastor_soul_l.dbr` augments: +4 drxdeathchillaura, +4 stafftraining; stats: characterLife=251.0, characterMana=281.0, characterIntelligence=33.0<br>`alastor_soul_n.dbr` augments: +2 drxdeathchillaura, +2 stafftraining; stats: characterLife=82.0, characterMana=114.0, characterIntelligence=16.0 |
| tagMonsterName1180 | `records\creature\monster\questbosses\boss_pharaohshonorguard4_31.dbr` | 25,28,31,47,48,51,62,63,66 | attack_damagemodifier_02 [Skill_Passive] - 10% physical damage per level - 50 Levels<br>construct_resists [Skill_Passive] - (CPF) Resistances for Statues and Robots<br>battlestandard [Skill_SpawnPet] - tagSkillName174<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>globalproperties_legendary_boss [Skill_Passive] - Global Monster Adjustment - Legendary<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>boss_conversionimmunity [Skill_Passive] - Boss Skill - Immunity to Conversion/Taunt/Fear/Petrify + 90% Mana Leech Resist + 50% Burn Resistance + 90% Percent Life Resistance + Racial Bonus vs Pets +Disruption Immunity + Life Leech Resistance + Total Life + Dodging<br>... (10 total skillName fields) | `pharaohshonorguard_soul_e.dbr` grants summon_pharaohguard [Skill_SpawnPet]; stats: characterLife=302.0, characterStrength=16.0, characterDefensiveAbility=43.0, offensivePhysicalMin=33.0<br>`pharaohshonorguard_soul_l.dbr` grants summon_pharaohguard [Skill_SpawnPet]; stats: characterLife=433.0, characterStrength=26.0, characterDefensiveAbility=76.0, offensivePhysicalMin=45.0<br>`pharaohshonorguard_soul_n.dbr` grants summon_pharaohguard [Skill_SpawnPet]; stats: characterLife=175.0, characterStrength=10.0, characterDefensiveAbility=20.0, offensivePhysicalMin=20.0 |
| tagMonsterName060 | `records\creature\monster\questbosses\boss_sandwraithlord_34.dbr` | 23,28,31,34,46,48,51,53,61,63,66,68 | sandwraithlord_sandwave [Skill_AttackWave] - Pierce + Extreme slow<br>sandwraithlord_fireball [Skill_AttackProjectileAreaEffect] - Fireball<br>sandwraithlord_summonsandwraiths [Skill_SpawnPetMonster] - Summon 4 Sandwraiths<br>sandwraithlord_sandblast [Skill_AttackProjectileBurst] - Sandwraith Sandblast - Slows Player + Pierce Dmg<br>attack_damagemodifier_02 [Skill_Passive] - 10% physical damage per level - 50 Levels<br>sandwraithlord_sandstorm [Skill_AttackRadius] - Radius Attack for 3 sec disruption + 3 sec reduced resistances + instant phys dmg + 3 sec reduced OA-DA + 3 Sec Reduced Speed<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>... (13 total skillName fields) | `sandwraith_soul_e.dbr` grants lifedrain [Skill_AttackSpellChaos]; augments: +3 drxphantomstrike, +2 drxravagesoftime<br>`sandwraith_soul_l.dbr` grants lifedrain [Skill_AttackSpellChaos]; augments: +3 drxphantomstrike, +2 drxravagesoftime<br>`sandwraith_soul_n.dbr` grants lifedrain [Skill_AttackSpellChaos]; augments: +3 drxphantomstrike, +2 drxravagesoftime<br>`sandwraithlord_soul_e.dbr` grants sandsandstorm [Skill_AttackRadius]; stats: characterOffensiveAbility=84.0<br>`sandwraithlord_soul_l.dbr` grants sandsandstorm [Skill_AttackRadius]; stats: characterOffensiveAbility=124.0<br>`sandwraithlord_soul_n.dbr` grants sandsandstorm [Skill_AttackRadius]; stats: characterOffensiveAbility=54.0 |
| tagMonsterName043 | `records\creature\monster\questbosses\boss_scarabaeus_27.dbr` | 21,24,27,44,46,48,60,61,63 | scarabaeus_ranged_causticsputum [Skill_AttackProjectileBurst] - Short-Range Wide-Spread Attack - Poison Dmg x 3 Sec + Slow Total Speed<br>scarabaeus_layeggs [Skill_AttackProjectileSpawnPet] - Lays Eggs that hatch into beetles<br>meleeattack_+5physicalperlvlx100 [Skill_AttackWeapon] - tagSkillName133<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>globalproperties_legendary_boss [Skill_Passive] - Global Monster Adjustment - Legendary<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>boss_conversionimmunity [Skill_Passive] - Boss Skill - Immunity to Conversion/Taunt/Fear/Petrify + 90% Mana Leech Resist + 50% Burn Resistance + 90% Percent Life Resistance + Racial Bonus vs Pets +Disruption Immunity + Life Leech Resistance + Total Life + Dodging<br>... (10 total skillName fields) | `scarabaeus_soul_e.dbr` grants scarabaeus_poisonspray [Skill_AttackProjectileBurst]; augments: +4 drxpoisongasbomb_shrapnel; stats: characterLife=369.0, defensivePhysical=8.0<br>`scarabaeus_soul_l.dbr` grants scarabaeus_poisonspray [Skill_AttackProjectileBurst]; augments: +5 drxpoisongasbomb_shrapnel; stats: characterLife=518.0, defensivePhysical=9.0<br>`scarabaeus_soul_n.dbr` grants scarabaeus_poisonspray [Skill_AttackProjectileBurst]; augments: +3 drxpoisongasbomb_shrapnel; stats: characterLife=233.0, defensivePhysical=7.0 |
| tagMonsterName115 | `records\creature\monster\questbosses\boss_scorposking_30.dbr` | 24,27,30,46,48,50,61,63,65 | nehebkau_sting [Skill_AttackWeapon] - Melee Sting w Poison Dmg<br>character_speedall [Skill_BuffRadiusToggled] - 20% Total Speed + 5% per level for 10 levels.<br>nehebkau_summonscorpions [Skill_SpawnPetMonster] - Summons Black Scorpions<br>nehebkau_earthfury [Skill_AttackRadius] - Radius Attack - Slow Attack + Phys. Dmg<br>nehebkau_poisongasbomb [Skill_AttackProjectile] - tagSkillName194<br>nehebkau_poisongasbomb_shrapnel [Skill_ProjectileModifier] - tagSkillName195<br>nehebkau_rotcloud [Skill_AttackProjectileAreaEffect] - Poison dmg + Poison dps + slow run speed<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>... (15 total skillName fields) | `nehebkau_soul_e.dbr` grants nehebkau_poisongasbomb [Skill_AttackProjectile]; augments: +4 drxpoisongasbomb<br>`nehebkau_soul_l.dbr` grants nehebkau_poisongasbomb [Skill_AttackProjectile]; augments: +5 drxpoisongasbomb<br>`nehebkau_soul_n.dbr` grants nehebkau_poisongasbomb [Skill_AttackProjectile]; augments: +3 drxpoisongasbomb |
| tagMonsterName097 | `records\creature\monster\questbosses\boss_spartacentaur_15.dbr` | 9,11,15,36,38,40,54,55,57 | nessus_summonminions [Skill_BuffRadius]<br>damagephysical_passivemodifier01 [Skill_Passive] - 10% physical damage per level<br>bosscharge [Skill_AttackWeaponCharge] - tagSkillName005<br>nessus_bleedattack [Skill_AttackRadius] - AoE Melee Bleeding + Pierce<br>nessus_meleeattack [Skill_AttackWeapon] - tagSkillName133<br>speed_enduranceaura [Skill_BuffRadiusToggled] - AE Instant Heal / +% Damage / +300% Life Regen<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>... (13 total skillName fields) | `nessus_soul_e.dbr` grants nessus_enduranceaura [Skill_BuffRadiusToggled]; augments: +2 drxwarhorn; stats: characterStrength=19.0, offensivePhysicalMin=21.0, defensiveProtection=25.0<br>`nessus_soul_l.dbr` grants nessus_enduranceaura [Skill_BuffRadiusToggled]; augments: +3 drxwarhorn; stats: characterStrength=30.0, offensivePhysicalMin=28.0, defensiveProtection=38.0<br>`nessus_soul_n.dbr` grants nessus_enduranceaura [Skill_BuffRadiusToggled]; augments: +1 drxwarhorn; stats: characterStrength=12.0, offensivePhysicalMin=12.0, defensiveProtection=12.0 |
| tagMonsterName114 | `records\creature\monster\questbosses\boss_spiderqueen_arachne_22.dbr` | 16,19,22,41,43,45,57,59,60 | character_speedall [Skill_BuffRadiusToggled] - 20% Total Speed + 5% per level for 10 levels.<br>summonpet_spider01 [Skill_SpawnPet] - Summons Spiders.  GOSH.<br>arachne_ranged_poisonspit [Skill_AttackProjectile] - Poison Dmg + Poison DoT for 5 seconds<br>arachne_close_poisoncloud [Skill_AttackProjectileAreaEffect] - Poison Dmg<br>arachne_meleeattack [Skill_AttackWeapon] - tagSkillName133<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>globalproperties_legendary_boss [Skill_Passive] - Global Monster Adjustment - Legendary<br>... (13 total skillName fields) | `arachne_soul_e.dbr` grants arachne_venomspray [Skill_AttackProjectile]; augments: +4 swordtraining, +3 drxcalculatedstrike; stats: characterDexterity=16.0<br>`arachne_soul_l.dbr` grants arachne_venomspray [Skill_AttackProjectile]; augments: +5 swordtraining, +4 drxcalculatedstrike; stats: characterDexterity=23.0<br>`arachne_soul_n.dbr` grants arachne_venomspray [Skill_AttackProjectile]; augments: +3 swordtraining, +2 drxcalculatedstrike; stats: characterDexterity=10.0 |
| tagMonsterName066 | `records\creature\monster\questbosses\boss_talos_50.dbr` | 44,47,50,59,62,65 | talos_flamethrower [Skill_AttackProjectileRing] - Long-Range Attack - Burn DoT x 3 sec + Stun x 4 seconds<br>talos_stomp [Skill_AttackRadius] - Phys + Lightning Dmg + Stun x 3 sec<br>talos_fistblast [Skill_AttackWeapon] - Direct Physical Damage - Default Attack<br>talos_fistswing [Skill_AttackWeapon] - Phys. Damage + 5 sec Disruption-Fumble<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>globalproperties_legendary_boss [Skill_Passive] - Global Monster Adjustment - Legendary<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>... (10 total skillName fields) | `talos_soul_e.dbr` grants talos_flamethrower [Skill_AttackProjectileBurst]; augments: +5 drxconcussiveblow, +5 drxfireenchantment_stoneskin; stats: offensivePhysicalMin=29.0, offensivePhysicalMax=41.0, defensivePhysical=10.0, defensiveProtection=67.0<br>`talos_soul_l.dbr` grants talos_flamethrower [Skill_AttackProjectileBurst]; augments: +6 drxconcussiveblow, +6 drxfireenchantment_stoneskin; stats: offensivePhysicalMin=40.0, offensivePhysicalMax=54.0, defensivePhysical=12.0, defensiveProtection=87.0<br>`talos_soul_n.dbr` grants talos_flamethrower [Skill_AttackProjectileBurst]; augments: +4 drxconcussiveblow, +4 drxfireenchantment_stoneskin; stats: offensivePhysicalMin=20.0, offensivePhysicalMax=30.0, defensivePhysical=10.0, defensiveProtection=50.0 |
| tagMonsterName123 | `records\creature\monster\questbosses\boss_terracottamage_bandari_40.dbr` | 34,37,40,53,54,56,68,69,71 | bandari_teleportself [Skill_AttackSpellTeleportSelf]<br>bandari_energyblast [Skill_AttackProjectile] - Cold + Life Dmg + Slow for 2 Sec<br>stormnimbus [Skill_BuffSelfToggled] - tagSkillName027<br>stormnimbus_heartoffrost [Skill_Modifier] - tagSkillName028<br>stormnimbus_staticcharge [Skill_Modifier] - tagSkillName029<br>bandari_eruption [Skill_AttackProjectileAreaEffect] - tagSkillName109<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>... (13 total skillName fields) | `bandari_soul_e.dbr` grants drxstormnimbus [Skill_BuffSelfToggled]; stats: defensiveProtection=21.0<br>`bandari_soul_l.dbr` grants drxstormnimbus [Skill_BuffSelfToggled]; stats: defensiveProtection=38.0<br>`bandari_soul_n.dbr` grants drxstormnimbus [Skill_BuffSelfToggled]; stats: defensiveProtection=10.0 |
| tagMonsterName382 | `records\creature\monster\questbosses\boss_titan_typhon_48.dbr` | 1,42,45,48,58,60,63,72,73,75 | typhon_skilltransferzeus [Skill_TyphonSkillTransfer] - Transfers skills from statue to typhon<br>typhon_boltofzeus [Skill_AttackProjectile] - Typhon - Zeus' Thunderbolt<br>typhon_demeterspoisonbolt [Skill_AttackProjectile] - Typhon - Demeter's Poison Bolt<br>typhon_earthenbarrier [Skill_AttackBuffRadius] - Stuns and Disrupts player for 6 seconds + phys dmg<br>typhon_lifeleech [Skill_BuffAttackRadiusDuration] - Life Leech - Steals 45% life x 2 sec + Returns a TON of HP<br>typhon_manaleech [Skill_BuffAttackRadiusDuration] - Mana Leech + 15% Burn + Skill Disruption for 6 seconds<br>typhon_meteorshower [Skill_DropProjectileTelekinesis] - Fiery Rocks from Heaven<br>typhon_passiveproperties [Skill_Passive] - Difficulty Adjustment<br>... (17 total skillName fields) | `hades_soul_e.dbr` grants hades_star [Skill_AttackProjectileMultiHit]; augments: +5 drxternion, +5 drxbladehoning; stats: characterLife=256.0, characterMana=304.0, characterDefensiveAbility=149.0<br>`hades_soul_l.dbr` grants hades_star [Skill_AttackProjectileMultiHit]; augments: +6 drxternion, +6 drxbladehoning; stats: characterLife=314.0, characterMana=415.0, characterDefensiveAbility=193.0<br>`hades_soul_n.dbr` grants hades_star [Skill_AttackProjectileMultiHit]; augments: +4 drxternion, +4 drxbladehoning; stats: characterLife=150.0, characterMana=200.0, characterDefensiveAbility=100.0<br>`typhon_soul_e.dbr` grants typhon_meteorstorm [Skill_DropProjectileTelekinesis]; stats: characterLife=328.0, characterMana=272.0, characterStrength=22.0, characterIntelligence=25.0<br>`typhon_soul_l.dbr` grants typhon_meteorstorm [Skill_DropProjectileTelekinesis]; stats: characterLife=418.0, characterMana=338.0, characterStrength=31.0, characterIntelligence=30.0<br>`typhon_soul_n.dbr` grants typhon_meteorstorm [Skill_DropProjectileTelekinesis]; stats: characterLife=200.0, characterMana=150.0, characterStrength=16.0, characterIntelligence=16.0 |
| tagMonsterName361 | `records\creature\monster\questbosses\boss_xiao_39.dbr` | 33,36,39,52,54,56,67,69,70 | xiao_summonpengs [Skill_SpawnPetMonster] - Summon Pengs<br>meleeattack_+3physicalandlightningperlvlx100 [Skill_AttackWeapon] - tagSkillName133<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic_boss [Skill_Passive] - Global Monster Adjustment - Epic<br>globalproperties_legendary_boss [Skill_Passive] - Global Monster Adjustment - Legendary<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>boss_conversionimmunity [Skill_Passive] - Boss Skill - Immunity to Conversion/Taunt/Fear/Petrify + 90% Mana Leech Resist + 50% Burn Resistance + 90% Percent Life Resistance + Racial Bonus vs Pets +Disruption Immunity + Life Leech Resistance + Total Life + Dodging<br>all_hpscaling_passive [Skill_Passive] - tagSkillName027<br>... (9 total skillName fields) | `xiao_soul_e.dbr` grants peng_summon [Skill_SpawnPet]; stats: offensivePhysicalMin=20.0, offensivePhysicalMax=24.0, characterLifeModifier=-30.0<br>`xiao_soul_l.dbr` grants peng_summon [Skill_SpawnPet]; stats: offensivePhysicalMin=28.0, offensivePhysicalMax=30.0, characterLifeModifier=-36.0<br>`xiao_soul_n.dbr` grants peng_summon [Skill_SpawnPet]; stats: offensivePhysicalMin=11.0, offensivePhysicalMax=14.0, characterLifeModifier=-24.0 |
| tagNewHero321 | `records\creature\monster\ratman\um_inkeyes2_45.dbr` | 43,59,72 | attack_damagemodifier_02 [Skill_Passive] - 10% physical damage per level - 50 Levels<br>bonusdamage_physical [Skill_Passive] - Adds Absolute Phys. Dmg +10 per level for 100 levels<br>bonusdamage_vita_+1perlevelx100 [Skill_Passive] - ^gFrost Strike<br>takedown [Skill_AttackWeaponCharge] - tagSkillName089<br>deathchillaura [Skill_BuffRadiusToggled]<br>throwingknife_multi [Skill_AttackProjectileBurst] - tagSkillName052<br>empusa_spirit_lifedrainnova [Skill_AttackProjectileAreaEffect] - Drains life and mana from enemies in the vicinity<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>... (12 total skillName fields) | `wheedletongue_soul_e.dbr` augments: +3 drxenvenomweapon_neurotoxin, +3 drxcalculatedstrike; stats: characterLife=219.0<br>`wheedletongue_soul_l.dbr` augments: +4 drxenvenomweapon_neurotoxin, +4 drxcalculatedstrike; stats: characterLife=319.0<br>`wheedletongue_soul_n.dbr` augments: +2 drxenvenomweapon_neurotoxin, +2 drxcalculatedstrike; stats: characterLife=130.0 |
| tagNewHero87 | `records\creature\monster\satyr\um_rakanizeus_17 (pcos modstridende kopi 2014-09-10).dbr` | 17,44,61 | damage_lightningbonus [Skill_BuffRadiusToggled]<br>character_speedall [Skill_BuffRadiusToggled] - 20% Total Speed + 5% per level for 10 levels.<br>attack_damagemodifier_01 [Skill_Passive] - 10% physical damage per level<br>rakanizeus_stormsurge [Skill_OnHitAttackRadius] - tagSkillName019<br>rakanizeus_lightning [Skill_AttackProjectileFan] - tagSkillName193<br>hero_modifier [Skill_Passive] - ^gFrost Strike<br>bonusdamage_lightning_+1perlevelx100 [Skill_Passive] - ^gFrost Strike<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>... (11 total skillName fields) | `rakanizeus_soul_e.dbr` grants summon_rakanizeus [Skill_SpawnPet]; augments: +5 drxstormsurge, +4 drxlightningbolt_chainlightning; stats: characterLife=200, characterMana=100, characterStrength=40, characterDexterity=40<br>`rakanizeus_soul_l.dbr` grants summon_rakanizeus [Skill_SpawnPet]; augments: +5 drxstormsurge, +4 drxlightningbolt_chainlightning; stats: characterLife=200, characterMana=100, characterStrength=40, characterDexterity=40<br>`rakanizeus_soul_n.dbr` grants summon_rakanizeus [Skill_SpawnPet]; augments: +5 drxstormsurge, +4 drxlightningbolt_chainlightning; stats: characterLife=200, characterMana=100, characterStrength=40, characterDexterity=40 |
| tagNewHero181 | `records\creature\monster\sepulchralwyrm\um_palai_47.dbr` | 47,63,78 | palai_firebreath [Skill_AttackProjectileRing] - Short-Range Attack - Fire Dmg + 3 sec Burn DoT<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>palai_ringofflame [Skill_BuffAttackRadiusToggled] - NO VISUAL EFFECT<br>deflectprojectiles_passive [Skill_Passive] - 5% chance to deflect projectiles x 20 levels<br>meleeattack_+3physicalandfireperlvlx100 [Skill_AttackWeapon] - tagSkillName133<br>physdmg_meleeonly [Skill_Passive] - Phys. Dmg scaling for melee enemies in Epic/Legendary<br>palai_nova [Skill_AttackProjectileRing] - tagSkillName193<br>retaliation_1fireperlevelx100levels [Skill_Passive] - 3 fire retaliation per level x 100 levels<br>... (13 total skillName fields) | `palai_soul_e.dbr` grants palai_bigbolt [Skill_AttackProjectileFan]; augments: +4 drxringofflame; stats: offensivePhysicalMin=30.0, characterLifeModifier=19.0<br>`palai_soul_l.dbr` grants palai_bigbolt [Skill_AttackProjectileFan]; augments: +5 drxringofflame; stats: offensivePhysicalMin=42.0, characterLifeModifier=20.0<br>`palai_soul_n.dbr` grants palai_bigbolt [Skill_AttackProjectileFan]; augments: +3 drxringofflame; stats: offensivePhysicalMin=20.0, characterLifeModifier=15.0 |
| tagMonsterName190 | `records\creature\monster\skeleton\um_toxeus_21.dbr` | 25,45,65 | laytrap_multitrap [Skill_AttackProjectileSpawnPet] - tagSkillName083<br>battlerage [Skill_PassiveOnHitBuffSelf] - tagSkillName002<br>flashpowder [Skill_AttackRadius] - tagSkillName058<br>lethalstrike [Skill_AttackWeapon] - tagSkillName061<br>lethalstrike_mortalwound [Skill_Modifier] - tagSkillName197<br>openwound [Skill_Passive] - tagSkillName063<br>toxeus_bladestorm [Skill_AttackProjectileRing] - tagSkillName052<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>... (17 total skillName fields) | `toxeus_soul_e.dbr` grants toxeus_flashpowder [Skill_AttackRadius]; augments: +6 drxlethalstrike, +6 drxbattlerage; stats: offensivePhysicalMin=80.0, offensivePhysicalMax=110.0, defensiveProtection=26.0, characterLifeModifier=10.0<br>`toxeus_soul_l.dbr` grants toxeus_flashpowder [Skill_AttackRadius]; augments: +8 drxlethalstrike, +7 drxbattlerage; stats: offensivePhysicalMin=120.0, offensivePhysicalMax=160.0, defensiveProtection=36.0, characterLifeModifier=15.0<br>`toxeus_soul_n.dbr` grants toxeus_flashpowder [Skill_AttackRadius]; augments: +5 drxlethalstrike, +5 drxbattlerage; stats: offensivePhysicalMin=55.0, offensivePhysicalMax=75.0, defensiveProtection=15.0, characterLifeModifier=6.0 |
| tagNewHero196 | `records\creature\monster\skeleton\um_xaiweng_48.dbr` | 48,59,71 | xeiwang_absorb [Skill_AttackRadius] - AE Instant Heal / +300% Life Regen<br>xeiwang_boltburst [Skill_AttackProjectileBurst] - tagSkillName113<br>xeiwang_strike [Skill_AttackWeapon] - Melee Fire Attack with Burn DoT<br>xeiwang_charge [Skill_AttackWeaponCharge] - tagSkillName137<br>meleeattack [Skill_AttackWeapon] - No bonus or effect - Used for chaining<br>lifeleech_resist_+1perlevelx100 [Skill_Passive] - ^gFrost Strike<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>resist_undead [Skill_Passive] - (CPF TQ UNDEAD RESISTS) 100% Life Leech / 100% Bleeding<br>... (16 total skillName fields) | `xeiwang_soul_e.dbr` grants xeiwang_absorb [Skill_AttackRadius]; augments: +6 axetraining; stats: characterDexterity=36.0<br>`xeiwang_soul_l.dbr` grants xeiwang_absorb [Skill_AttackRadius]; augments: +7 axetraining; stats: characterDexterity=47.0<br>`xeiwang_soul_n.dbr` grants xeiwang_absorb [Skill_AttackRadius]; augments: +5 axetraining; stats: characterDexterity=27.0 |
| tagBlackWidow | `records\creature\monster\typhon\spiderblackwidow01.dbr` | 45,60,73 | spiderwidow_toxicbite [Skill_AttackWeapon] - tagSkillName041<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>albinospiderqueen_rangedweb [Skill_AttackProjectileDebuf] - Fires a webbed net projectile.<br>elementalresistance_10xlevel [Skill_Passive] - Grants 10% Elemental resistance per level x 10 levels<br>boss_conversionimmunity [Skill_Passive] - Boss Skill - Immunity to Conversion/Taunt/Fear/Petrify + 90% Mana Leech Resist + 50% Burn Resistance + 90% Percent Life Resistance + Racial Bonus vs Pets +Disruption Immunity + Life Leech Resistance + Total Life + Dodging<br>blackwidow_poisonshot [Skill_AttackProjectile] - Poison Dmg<br>venomnova [Skill_AttackProjectileRing] - tagSkillName042 | `arachnesshame_soul_e.dbr` grants arachneshame_rangedweb [Skill_AttackProjectileDebuf]; stats: offensivePhysicalMin=18.0<br>`arachnesshame_soul_l.dbr` grants arachneshame_rangedweb [Skill_AttackProjectileDebuf]; stats: offensivePhysicalMin=28.0<br>`arachnesshame_soul_n.dbr` grants arachneshame_rangedweb [Skill_AttackProjectileDebuf]; stats: offensivePhysicalMin=10.0 |
| tagNewHero177 | `records\creature\monster\zombie\um_melalos_19_test.dbr` | 19,44,61 | weakening_strike [Skill_AttackWeapon]<br>melalos_zombie_summon3 [Skill_SpawnPet]<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>physdmg_meleeonly [Skill_Passive] - Phys. Dmg scaling for melee enemies in Epic/Legendary<br>bonusdamage_poisonvita_+1perlevelx100 [Skill_Passive] - ^gFrost Strike<br>plaguebolts [Skill_AttackProjectileBurst]<br>plaguebolt_fragments [Skill_ProjectileModifier]<br>rottengrasp [Skill_AttackProjectile]<br>... (12 total skillName fields) | `melalos_soul_e.dbr` grants summon_zombiesoldier [Skill_SpawnPet]; augments: +3 drxdarkcovenant, +3 drxplague; stats: characterLife=90, characterDefensiveAbility=65.0, characterLifeModifier=10.0<br>`melalos_soul_l.dbr` grants summon_zombiesoldier [Skill_SpawnPet]; augments: +4 drxdarkcovenant, +4 drxplague; stats: characterLife=120, characterDefensiveAbility=93.0, characterLifeModifier=14.0<br>`melalos_soul_n.dbr` grants summon_zombiesoldier [Skill_SpawnPet]; augments: +2 drxdarkcovenant, +2 drxplague; stats: characterLife=60, characterDefensiveAbility=35.0, characterLifeModifier=6.0 |
| xtagMonsterHades | `records\drxcreatures\bloodwitch\boss_hades_54.dbr` | 53,55,57,68,70,71,78,79,80 | hadesall_sicklesweep [Skill_AttackRadius] - tagSkillName027<br>hadesall_selfbuff [Skill_Passive] - tagSkillName027<br>hades1_shadowbolt [Skill_AttackProjectileBurst] - tagSkillName022<br>hades1_shadowstar_single [Skill_AttackProjectile] - tagSkillName193<br>hades_regen_passive [Skill_Passive] - tagSkillName017<br>all_hpscaling_passive [Skill_Passive] - tagSkillName027<br>boss_conversionimmunity [Skill_Passive] - Boss Skill - Immunity to Conversion/Taunt/Fear/Petrify + 90% Mana Leech Resist + 50% Burn Resistance + 90% Percent Life Resistance + Racial Bonus vs Pets +Disruption Immunity + Life Leech Resistance + Total Life + Dodging<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>... (11 total skillName fields) | `hades_soul_e.dbr` grants hades_star [Skill_AttackProjectileMultiHit]; augments: +5 drxternion, +5 drxbladehoning; stats: characterLife=256.0, characterMana=304.0, characterDefensiveAbility=149.0<br>`hades_soul_l.dbr` grants hades_star [Skill_AttackProjectileMultiHit]; augments: +6 drxternion, +6 drxbladehoning; stats: characterLife=314.0, characterMana=415.0, characterDefensiveAbility=193.0<br>`hades_soul_n.dbr` grants hades_star [Skill_AttackProjectileMultiHit]; augments: +4 drxternion, +4 drxbladehoning; stats: characterLife=150.0, characterMana=200.0, characterDefensiveAbility=100.0<br>`sp_hades_soul_e.dbr` grants melinoe_bloodboil [Skill_AttackRadius]; augments: +4 drxdeathchillaura, +4 drxternion; stats: offensivePhysicalMin=65.0, offensivePhysicalMax=100.0, characterLifeModifier=16.0<br>`sp_hades_soul_l.dbr` grants melinoe_bloodboil [Skill_AttackRadius]; augments: +5 drxdeathchillaura, +5 drxternion; stats: offensivePhysicalMin=100.0, offensivePhysicalMax=150.0, characterLifeModifier=22.0<br>`sp_hades_soul_n.dbr` grants melinoe_bloodboil [Skill_AttackRadius]; augments: +3 drxdeathchillaura, +3 drxternion; stats: offensivePhysicalMin=40.0, offensivePhysicalMax=65.0, characterLifeModifier=10.0 |
| tagBWLeinth | `records\drxcreatures\bloodwitch\q_leinth_49.dbr` | 47,49,50,62,64,65,74,75,76 | armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>melinoe_bloodboil [Skill_AttackRadius] - Drains blood and life from enemies in its radius<br>leinth_bloodall_defaultattack [Skill_AttackProjectile] - Ranged Bleeding Damage Attack<br>hero_flesheater [Skill_SpawnPet]<br>leinth_aura [Skill_BuffRadiusToggled]<br>leinth_heatseeker [Skill_SpawnPet] - Ranged Bleeding Damage Attack<br>leinth_summon_uglies [Skill_SpawnPet]<br>leinth_bloodall_02 [Skill_AttackProjectile] - Ranged Bleeding Damage Attack<br>... (15 total skillName fields) | `leinth_soul_e.dbr` grants melinoe_bloodboil [Skill_AttackRadius]; augments: +3 drxdarkcovenant, +3 drxplague; stats: characterLifeModifier=12.0<br>`leinth_soul_l.dbr` grants melinoe_bloodboil [Skill_AttackRadius]; augments: +4 drxdarkcovenant, +4 drxplague; stats: characterLifeModifier=18.0<br>`leinth_soul_n.dbr` grants melinoe_bloodboil [Skill_AttackRadius]; augments: +2 drxdarkcovenant, +2 drxplague; stats: characterLifeModifier=8.0 |
| tagUrderMunder | `records\drxcreatures\crowheroes\murderbunny.dbr` | 66,79,99 | armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>sandwraith_sandblast [Skill_AttackProjectile] - Sandwraith Sandblast - Slows Player + Pierce Dmg<br>retaliation_1fireperlevelx100levels [Skill_Passive] - 3 fire retaliation per level x 100 levels<br>maggot_spit [Skill_AttackProjectileSpawnPet]<br>physdmg_meleeonly [Skill_Passive] - Phys. Dmg scaling for melee enemies in Epic/Legendary<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>globalproperties_epic01 [Skill_Passive] - Global Monster Adjustment - Epic - No Longer Active<br>globalproperties_legendary01 [Skill_Passive] - Global Monster Adjustment - Legendary - No Longer Active<br>... (9 total skillName fields) | `murderbunny_soul_e.dbr` grants cyclops_groundsmash [Skill_AttackProjectile]; augments: +5 drxonslaught, +4 drxlethalstrike; stats: offensivePhysicalMin=130.0, offensivePhysicalMax=200.0, characterLifeModifier=18.0<br>`murderbunny_soul_l.dbr` grants cyclops_groundsmash [Skill_AttackProjectile]; augments: +6 drxonslaught, +5 drxlethalstrike; stats: offensivePhysicalMin=190.0, offensivePhysicalMax=280.0, characterLifeModifier=25.0<br>`murderbunny_soul_n.dbr` grants cyclops_groundsmash [Skill_AttackProjectile]; augments: +4 drxonslaught, +3 drxlethalstrike; stats: offensivePhysicalMin=80.0, offensivePhysicalMax=130.0, characterLifeModifier=12.0 |
| tagNewHero81 | `records\item\equipmentring\soul\test\um_bloodcrow_50_l.dbr` | 50,65,80 | lightningbolt [Skill_AttackRadiusLightning] - tagSkillName025<br>attack_damagemodifier_02 [Skill_Passive] - 10% physical damage per level - 50 Levels<br>bonusdamage_fire_+1perlevelx100 [Skill_Passive] - ^gFrost Strike<br>fireenchantment [Skill_BuffRadiusToggled]<br>fireenchantment_brimstone [Skill_Modifier] - tagSkillName104<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>fireenchantment_stoneskin [Skill_Modifier] - tagSkillName100<br>bloodcrowzombie_summon3 [Skill_SpawnPet]<br>... (15 total skillName fields) | `bloodcrow_soul_e.dbr` augments: +5 drxfireenchantment, +4 drxstudyprey; stats: characterLifeModifier=-12.0<br>`bloodcrow_soul_l.dbr` augments: +6 drxfireenchantment, +5 drxstudyprey; stats: characterLifeModifier=-14.0<br>`bloodcrow_soul_n.dbr` augments: +4 drxfireenchantment, +3 drxstudyprey; stats: characterLifeModifier=-10.0 |
| tagMonsterName121 | `records\skills\boss skills\summoned minions\aktaios_mirage_33.dbr` | 27,30,33,48,50,52,57,60,63,65,67,77,80,83 | aktaios_fireball [Skill_AttackProjectileAreaEffect] - Fireball<br>physdmg_meleeonly01 [Skill_Passive] - Phys. Dmg scaling for melee enemies in Epic/Legendary - zerg monsters<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal | `aktaios_soul_e.dbr` grants firefragmentnova [Skill_AttackProjectileRing]; augments: +5 drxvolcanicorb, +4 drxvolcanicorb_immolation; stats: characterMana=284.0, defensivePhysical=-13.0<br>`aktaios_soul_l.dbr` grants firefragmentnova [Skill_AttackProjectileRing]; augments: +6 drxvolcanicorb, +5 drxvolcanicorb_immolation; stats: characterMana=409.0, defensivePhysical=-15.0<br>`aktaios_soul_n.dbr` grants firefragmentnova [Skill_AttackProjectileRing]; augments: +4 drxvolcanicorb, +3 drxvolcanicorb_immolation; stats: characterMana=185.0, defensivePhysical=-11.0 |
| tagD2Boss004 | `records\test\boss_coldworm50.dbr` | 30,50,65 | records\skills\boss skills\d2custom\coldworm_layegg.dbr (UNRESOLVED)<br>records\skills\boss skills\d2custom\coldworm_summonbugs.dbr (UNRESOLVED)<br>records\skills\boss skills\d2custom\coldworm_summonbug.dbr (UNRESOLVED)<br>records\skills\boss skills\d2custom\coldworm_dropceiling.dbr (UNRESOLVED)<br>records\skills\boss skills\d2custom\coldworm_poisongas.dbr (UNRESOLVED)<br>records\skills\boss skills\d2custom\coldworm_shockwave.dbr (UNRESOLVED)<br>records\skills\boss skills\d2custom\coldworm_shockwave_sec.dbr (UNRESOLVED)<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>... (13 total skillName fields) | `boss_coldworm50_soul_e.dbr` grants gargantuanyeti_iceblast [Skill_AttackProjectileRing]; augments: +3 drxcoldaura, +3 drxplague; stats: characterLife=120, characterMana=80, characterLifeModifier=10.0<br>`boss_coldworm50_soul_l.dbr` grants gargantuanyeti_iceblast [Skill_AttackProjectileRing]; augments: +5 drxcoldaura, +5 drxplague; stats: characterLife=150, characterMana=100, characterLifeModifier=15.0<br>`boss_coldworm50_soul_n.dbr` grants gargantuanyeti_iceblast [Skill_AttackProjectileRing]; augments: +2 drxcoldaura, +2 drxplague; stats: characterLife=80, characterMana=50, characterLifeModifier=5.0 |
| tagD2Boss033 | `records\test\boss_dagon_66.dbr` | 50,65,80 | records\skills\boss skills\d2custom\dagon_shadowstar_single.dbr (UNRESOLVED)<br>records\skills\boss skills\d2custom\dagon_summonwater.dbr (UNRESOLVED)<br>records\skills\boss skills\d2custom\dagon_tidalwave.dbr (UNRESOLVED)<br>hydra_superbite [Skill_AttackWeapon] - High-Damage Physical w 15% Pierce + Poison DoT<br>records\skills\boss skills\d2custom\dagon_mudstorm.dbr (UNRESOLVED)<br>records\xpack\skills\dream\pet\pcloudpet_petskill_pcloud.dbr (UNRESOLVED)<br>Records\Game\D2GlobalProperties_Normal01.dbr (UNRESOLVED)<br>Records\Game\D2GlobalProperties_Epic_Boss.dbr (UNRESOLVED)<br>... (11 total skillName fields) | `dagon_soul_e.dbr` grants arachne_venomspray [Skill_AttackProjectile]; augments: +3 drxenvenomweapon, +3 drxplague; stats: offensivePhysicalMin=35.0, offensivePhysicalMax=55.0, characterLifeModifier=12.0<br>`dagon_soul_l.dbr` grants arachne_venomspray [Skill_AttackProjectile]; augments: +4 drxenvenomweapon, +4 drxplague; stats: offensivePhysicalMin=55.0, offensivePhysicalMax=80.0, characterLifeModifier=18.0<br>`dagon_soul_n.dbr` grants arachne_venomspray [Skill_AttackProjectile]; augments: +2 drxenvenomweapon, +2 drxplague; stats: offensivePhysicalMin=20.0, offensivePhysicalMax=35.0, characterLifeModifier=8.0 |
| tagNewHero200 | `records\test\um_calybe_20.dbr` | 20,43,58 | drxdualweapontraining [Skill_WPAttack_BasicAttack] - Allows dual wield / Adds chance to use both weapons at once<br>drxdualwieldtechnique_jumpslash [Skill_WPAttack_BasicAttack] - Double Stroke - double hits with both weapons in the span of a normal attack<br>drxdualwieldtechnique_crosscut [Skill_WPAttack_BasicAttack] - Cross Cut - Hits 2 enemies and causes bleeding<br>drxdualwieldtechnique_tumult [Skill_WPAttack_BasicAttack] - Eviscerate - modifies damage and causes bleeding<br>drxdualwieldtechnique_wardance [Skill_WPAttack_BasicAttack] - Trinity<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>calybe_wave [Skill_AttackWave] - tagNewSkill338<br>calybe_buff [Skill_BuffSelfToggled] - Bleed% + AS<br>... (15 total skillName fields) | `calybe_soul_e.dbr` grants calybe_eclipse [Skill_AttackRadius]; augments: +4 drxdualwieldtechnique_wardance, +3 drxdualwieldtechnique_crosscut; stats: characterLife=-60, characterDexterity=30, characterOffensiveAbility=50.0<br>`calybe_soul_l.dbr` grants calybe_eclipse [Skill_AttackRadius]; augments: +4 drxdualwieldtechnique_wardance, +3 drxdualwieldtechnique_crosscut; stats: characterLife=-60, characterDexterity=30, characterOffensiveAbility=50.0<br>`calybe_soul_n.dbr` grants calybe_eclipse [Skill_AttackRadius]; augments: +4 drxdualwieldtechnique_wardance, +3 drxdualwieldtechnique_crosscut; stats: characterLife=-60, characterDexterity=30, characterOffensiveAbility=50.0 |
| xtagMonsterGraeae1 | `records\xpack\creatures\monster\bosses\01_graeae\boss_deino_39.dbr` | 38,40,42,55,56,58,70,71,72 | graeae_smallproj [Skill_AttackProjectileBurst] - tagSkillName022<br>graeae_lightningclap [Skill_AttackRadius] - tagSkillName027<br>graeae_hastheeye [Skill_BuffSelfToggled] - tagSkillName110<br>graeae_largeproj [Skill_AttackProjectileBurst] - tagSkillName022<br>graeae_thunderstorm [Skill_AttackProjectileAreaEffect] - tagSkillName151<br>graeae_hastheeye_animation [Skill_BuffSelfDuration] - tagSkillName027<br>graeae_lightningclap_witheye [Skill_AttackRadius] - tagSkillName027<br>boss_scaling [Skill_Passive] - ^gFrost Strike<br>... (14 total skillName fields) | `deino_soul_e.dbr` grants deino_lightningclap [Skill_AttackRadius]; stats: characterLife=228.0<br>`deino_soul_l.dbr` grants deino_lightningclap [Skill_AttackRadius]; stats: characterLife=314.0<br>`deino_soul_n.dbr` grants deino_lightningclap [Skill_AttackRadius]; stats: characterLife=125.0 |
| xtagMonsterGraeae2 | `records\xpack\creatures\monster\bosses\01_graeae\boss_enyo_39.dbr` | 38,40,42,55,56,58,70,71,72 | graeae_smallproj [Skill_AttackProjectileBurst] - tagSkillName022<br>graeae_lightningclap [Skill_AttackRadius] - tagSkillName027<br>graeae_hastheeye [Skill_BuffSelfToggled] - tagSkillName110<br>graeae_largeproj [Skill_AttackProjectileBurst] - tagSkillName022<br>graeae_thunderstorm [Skill_AttackProjectileAreaEffect] - tagSkillName151<br>graeae_hastheeye_animation [Skill_BuffSelfDuration] - tagSkillName027<br>graeae_lightningclap_witheye [Skill_AttackRadius] - tagSkillName027<br>boss_scaling [Skill_Passive] - ^gFrost Strike<br>... (14 total skillName fields) | `enyo_soul_e.dbr` grants enyo_thunderstorm [Skill_AttackProjectileAreaEffect]; stats: characterMana=235.0, characterStrength=-44.0, characterIntelligence=29.0<br>`enyo_soul_l.dbr` grants enyo_thunderstorm [Skill_AttackProjectileAreaEffect]; stats: characterMana=332.0, characterStrength=-54.0, characterIntelligence=36.0<br>`enyo_soul_n.dbr` grants enyo_thunderstorm [Skill_AttackProjectileAreaEffect]; stats: characterMana=125.0, characterStrength=-30.0, characterIntelligence=20.0 |
| xtagMonsterGraeae3 | `records\xpack\creatures\monster\bosses\01_graeae\boss_pemphredo_40.dbr` | 39,41,43,56,57,59,71,72 | graeae_smallproj [Skill_AttackProjectileBurst] - tagSkillName022<br>graeae_lightningclap [Skill_AttackRadius] - tagSkillName027<br>graeae_hastheeye [Skill_BuffSelfToggled] - tagSkillName110<br>graeae_largeproj [Skill_AttackProjectileBurst] - tagSkillName022<br>graeae_thunderstorm [Skill_AttackProjectileAreaEffect] - tagSkillName151<br>graeae_hastheeye_animation [Skill_BuffSelfDuration] - tagSkillName027<br>graeae_lightningclap_witheye [Skill_AttackRadius] - tagSkillName027<br>boss_scaling [Skill_Passive] - ^gFrost Strike<br>... (14 total skillName fields) | `pemphredo_soul_e.dbr` grants pemphredo_thunderspark [Skill_AttackProjectileBurst]; stats: characterMana=179.0, characterStrength=-27.0, characterIntelligence=23.0<br>`pemphredo_soul_l.dbr` grants pemphredo_thunderspark [Skill_AttackProjectileBurst]; stats: characterMana=255.0, characterStrength=-36.0, characterIntelligence=32.0<br>`pemphredo_soul_n.dbr` grants pemphredo_thunderspark [Skill_AttackProjectileBurst]; stats: characterMana=90.0, characterStrength=-20.0, characterIntelligence=15.0 |
| xtagMonsterCharon | `records\xpack\creatures\monster\bosses\02_charon\boss_charonform2_43.dbr` | 42,44,46,58,59,61,72,73,74 | charon_projectiletrigger [Skill_TurretFireControl]<br>charon_selfbuff [Skill_Passive] - tagSkillName027<br>charon_geyserform2 [Skill_CharonGeysers]<br>charon_swoopstomp [Skill_AttackRadius] - tagSkillName027<br>charon_tidalwave [Skill_AttackWave] - xtagSkillDreamName005<br>boss_scaling [Skill_Passive] - ^gFrost Strike<br>all_hpscaling_passive [Skill_Passive] - tagSkillName027<br>boss_conversionimmunity [Skill_Passive] - Boss Skill - Immunity to Conversion/Taunt/Fear/Petrify + 90% Mana Leech Resist + 50% Burn Resistance + 90% Percent Life Resistance + Racial Bonus vs Pets +Disruption Immunity + Life Leech Resistance + Total Life + Dodging<br>... (12 total skillName fields) | `charon_soul_e.dbr` grants charon_buffself [Skill_BuffSelfDuration]; stats: characterMana=165.0<br>`charon_soul_l.dbr` grants charon_buffself [Skill_BuffSelfDuration]; stats: characterMana=239.0<br>`charon_soul_n.dbr` grants charon_buffself [Skill_BuffSelfDuration]; stats: characterMana=100.0<br>`boss_charon_soul_e.dbr` grants talos_flamethrower [Skill_AttackProjectileBurst]; augments: +4 drxvolcanicorb, +3 drxringofflame; stats: characterLife=160, characterMana=120, characterIntelligence=64<br>`boss_charon_soul_l.dbr` grants talos_flamethrower [Skill_AttackProjectileBurst]; augments: +5 drxvolcanicorb, +4 drxringofflame; stats: characterLife=200, characterMana=150, characterIntelligence=80<br>`boss_charon_soul_n.dbr` grants talos_flamethrower [Skill_AttackProjectileBurst]; augments: +3 drxvolcanicorb, +2 drxringofflame; stats: characterLife=120, characterMana=90, characterIntelligence=48 |
| xtagMonsterCerberus | `records\xpack\creatures\monster\bosses\03_cerberus\boss_cerberus_44.dbr` | 43,45,47,59,60,62,72,73,74 | cerberus_acidpuddle_summon [Skill_AttackProjectileSpawnPet] - xtagScroll008<br>cerberus_acidbite [Skill_AttackWeapon]<br>cerberus_acidbreath [Skill_AttackProjectileRing] - tagSkillName113<br>cerberus_crackfire [Skill_CerberusGeysers]<br>cerberus_roar [Skill_AttackWave] - tagSkillName113<br>boss_scaling [Skill_Passive] - ^gFrost Strike<br>all_hpscaling_passive [Skill_Passive] - tagSkillName027<br>boss_conversionimmunity [Skill_Passive] - Boss Skill - Immunity to Conversion/Taunt/Fear/Petrify + 90% Mana Leech Resist + 50% Burn Resistance + 90% Percent Life Resistance + Racial Bonus vs Pets +Disruption Immunity + Life Leech Resistance + Total Life + Dodging<br>... (12 total skillName fields) | `cerberus_soul_e.dbr` grants cerberus_breathwave [Skill_AttackWave]; stats: characterStrength=17.0, characterDexterity=33.0<br>`cerberus_soul_l.dbr` grants cerberus_breathwave [Skill_AttackWave]; stats: characterStrength=22.0, characterDexterity=44.0<br>`cerberus_soul_n.dbr` grants cerberus_breathwave [Skill_AttackWave]; stats: characterStrength=10.0, characterDexterity=25.0 |
| xtagMonsterSkeletalTyphon | `records\xpack\creatures\monster\bosses\04_skeletaltyphon\boss_skeletaltyphon_48.dbr` | 44,46,48,59,61,63,73,74,75 | skeletaltyphon_boneshard [Skill_AttackProjectileBurst] - tagSkillName022<br>skeletaltyphon_bonespire [Skill_AttackProjectile]<br>skeletaltyphon_bonetrapgrenade [Skill_AttackProjectileDebuf]<br>skeletaltyphon_spiritbreath [Skill_AttackProjectileRing] - tagSkillName113<br>boss_scaling [Skill_Passive] - ^gFrost Strike<br>all_hpscaling_passive [Skill_Passive] - tagSkillName027<br>boss_conversionimmunity [Skill_Passive] - Boss Skill - Immunity to Conversion/Taunt/Fear/Petrify + 90% Mana Leech Resist + 50% Burn Resistance + 90% Percent Life Resistance + Racial Bonus vs Pets +Disruption Immunity + Life Leech Resistance + Total Life + Dodging<br>armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>... (11 total skillName fields) | `undeadtyphon_soul_e.dbr` grants skeletaltyphon_bonespire [Skill_AttackProjectileFan]; augments: +5 drxenslavespirit, +3 drxbladehoning<br>`undeadtyphon_soul_l.dbr` grants skeletaltyphon_bonespire [Skill_AttackProjectileFan]; augments: +6 drxenslavespirit, +4 drxbladehoning<br>`undeadtyphon_soul_n.dbr` grants skeletaltyphon_bonespire [Skill_AttackProjectileFan]; augments: +4 drxenslavespirit, +2 drxbladehoning |
| tagNewHero228 | `records\xpack\creatures\monster\gigantes\um_antaeus_49.dbr` | 49,63,75 | armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>antaeus_chargedstrike [Skill_WeaponPool_ChargedFinale] - +Phys% + Vitality dmg + Poison dmg<br>bonusdamage_physical [Skill_Passive] - Adds Absolute Phys. Dmg +10 per level for 100 levels<br>antaeus_aura [Skill_BuffRadiusToggled]<br>antaeus_spear [Skill_AttackProjectile] - tagSkillName042<br>antaeus_blink [Skill_AttackSpellTeleportSelf]<br>antaeus_surge [Skill_AttackRadius] - Yaoguai's Flame Ring Attack - Fire DoT<br>globalproperties_normal01 [Skill_Passive] - Global Monster Adjustment - Normal<br>... (13 total skillName fields) | `antaeus_soul_e.dbr` grants antaeus_chargedstrike [Skill_WeaponPool_ChargedFinale]; augments: +3 swordtraining; stats: offensivePhysicalMin=45.0<br>`antaeus_soul_l.dbr` grants antaeus_chargedstrike [Skill_WeaponPool_ChargedFinale]; augments: +4 swordtraining; stats: offensivePhysicalMin=60.0<br>`antaeus_soul_n.dbr` grants antaeus_chargedstrike [Skill_WeaponPool_ChargedFinale]; augments: +2 swordtraining; stats: offensivePhysicalMin=30.0 |
| tagNewHero188 | `records\xpack\creatures\monster\karkinos\um_deeptresher_47.dbr` | 47,62,72 | thresher_strike [Skill_AttackWeapon] - Melee Fire Attack with Burn DoT<br>thresher_geyser [Skill_AttackProjectileAreaEffect] - tagNewSkill55<br>giantkarkinos_flightofthekondor [Skill_AttackSpellTeleportSelf] - Burrow under the ground and then pop up to attack the enemy<br>giantkarkinos_trapimmunity [Skill_Passive] - Immunty to Trap Damage + Stun and Slow Resistance<br>automatoi_minstun [Skill_Passive] - ^gFrost Strike<br>physdmg_meleeonly [Skill_Passive] - Phys. Dmg scaling for melee enemies in Epic/Legendary<br>damagebleeding_shredder [Skill_Passive] - 15% chance of 6 bleed damage x 3 seconds - +4 dmg per level for 20 levels<br>thresher_harden [Skill_BuffSelfDuration] - tagSkillName027<br>... (15 total skillName fields) | `deeptresher_soul_e.dbr` grants thresher_geyser [Skill_AttackProjectileAreaEffect]; stats: characterDefensiveAbility=100.0, offensivePhysicalMin=58.0, offensivePhysicalMax=67.0, defensiveProtection=54.0<br>`deeptresher_soul_l.dbr` grants thresher_geyser [Skill_AttackProjectileAreaEffect]; stats: characterDefensiveAbility=128.0, offensivePhysicalMin=78.0, offensivePhysicalMax=82.0, defensiveProtection=78.0<br>`deeptresher_soul_n.dbr` grants thresher_geyser [Skill_AttackProjectileAreaEffect]; stats: characterDefensiveAbility=60.0, offensivePhysicalMin=40.0, offensivePhysicalMax=50.0, defensiveProtection=40.0 |
| tagNewHero180 | `records\xpack\creatures\monster\keres\um_meglograi_48.dbr` | 48,64,78 | meglograi_blink [Skill_AttackSpellTeleportSelf]<br>meglograi_attack [Skill_AttackProjectile] - tagSkillName042<br>meglograi_burst [Skill_AttackRadius] - AE Instant Heal / +300% Life Regen<br>meglograi_bat [Skill_AttackProjectile] - tagSkillName042<br>meglograi_wave [Skill_AttackWave] - xtagSkillDreamName004<br>uber_scaling [Skill_Passive] - ^gFrost Strike<br>hero_modifier [Skill_Passive] - ^gFrost Strike<br>boss_conversionimmunity [Skill_Passive] - Boss Skill - Immunity to Conversion/Taunt/Fear/Petrify + 90% Mana Leech Resist + 50% Burn Resistance + 90% Percent Life Resistance + Racial Bonus vs Pets +Disruption Immunity + Life Leech Resistance + Total Life + Dodging<br>... (12 total skillName fields) | `meglograi_soul_e.dbr` grants meglograi_burst [Skill_AttackRadius]; stats: characterMana=215.0, characterDexterity=32.0, characterDefensiveAbility=64.0, defensivePhysical=-3.0<br>`meglograi_soul_l.dbr` grants meglograi_burst [Skill_AttackRadius]; stats: characterMana=303.0, characterDexterity=43.0, characterDefensiveAbility=88.0, defensivePhysical=-4.0<br>`meglograi_soul_n.dbr` grants meglograi_burst [Skill_AttackRadius]; stats: characterMana=125.0, characterDexterity=25.0, characterDefensiveAbility=35.0, defensivePhysical=-3.0 |
| tagNewHero82 | `records\xpack\creatures\monster\lostsoul\bloodcrow_soul.dbr` | 50,65,80 | armor_passive [Skill_Passive] - +1 Armor per Level - 650 Levels<br>bonusdamage_physical [Skill_Passive] - Adds Absolute Phys. Dmg +10 per level for 100 levels<br>bonusdamage_poisonvita_+1perlevelx100 [Skill_Passive] - ^gFrost Strike<br>ondeath_necronova [Skill_AttackProjectileRing] - tagSkillName193<br>drxdeathchillaura [Skill_BuffRadiusToggled] - tagSkillName035<br>deathchillaura_necrosis [Skill_Modifier] - tagSkillName037<br>deathchillaura_ravagesoftime [Skill_BuffRadiusToggled]<br>bonusdamage_physical_+8perlevelx100 [Skill_Passive] - ^gFrost Strike<br>... (16 total skillName fields) | `bloodcrow_soul_e.dbr` augments: +5 drxfireenchantment, +4 drxstudyprey; stats: characterLifeModifier=-12.0<br>`bloodcrow_soul_l.dbr` augments: +6 drxfireenchantment, +5 drxstudyprey; stats: characterLifeModifier=-14.0<br>`bloodcrow_soul_n.dbr` augments: +4 drxfireenchantment, +3 drxstudyprey; stats: characterLifeModifier=-10.0 |


---

## 4. Counts summary

| Metric | Count |
|---|---|
| Total Hero/Boss/Quest monster records scanned (all level/difficulty variants) | 997 |
| Total .dbr records in built database | 50,241 |
| Unique Hero/Boss/Quest monsters (deduplicated by description tag) | 662 |
| &nbsp;&nbsp;- HAS a wired, working soul | 616 |
| &nbsp;&nbsp;- Soul exists but NOT wired / zero-chance / low-confidence match only | 3 |
| &nbsp;&nbsp;- NONE (no soul, no plausible match) | 43 |
| &nbsp;&nbsp;&nbsp;&nbsp;of which non-combat utility-prop records (not real design gaps) | 15 |
| &nbsp;&nbsp;&nbsp;&nbsp;of which real Medium/Low severity design gaps | 31 (28 Medium + 3 Low) |
| Unique monsters by classification: Hero | 500 (493 HAS / 4 NONE / 3 not-wired) |
| Unique monsters by classification: Quest | 88 (63 HAS / 25 NONE, of which 1 is a utility prop) |
| Unique monsters by classification: Boss | 74 (60 HAS / 14 NONE, all 14 are utility props - 0 real Boss gaps) |
| Total unique bosses (`monsterClassification == Boss`, deduplicated) | 74 |
| &nbsp;&nbsp;- Non-combat utility-prop records excluded from the fightable roster | 14 |
| &nbsp;&nbsp;- Real fightable boss roster (Table B) | 60 |
| &nbsp;&nbsp;&nbsp;&nbsp;- HAS a functional soul | 59 |
| &nbsp;&nbsp;&nbsp;&nbsp;- STUB soul only (needs a real design) | 1 (Limos Lifeeater) |
| &nbsp;&nbsp;&nbsp;&nbsp;- NO soul record at all | 0 |
| Upstream soul (type,name) pairs missing from current build (any variant) | 0 |

**Bottom line for design planning:** the boss tier is essentially complete (59/60 functional,
1 stub to redesign). The real remaining soul-design backlog is concentrated in the **Quest**
classification - specifically the DRX **Crow Heroes** roster (`records\drxcreatures\crowheroes\`:
Gorgus, Jiaco, Kaets, Kir4, Kreeloo, Less, Lil Lued, Big Lued, Nomnom, Numberouane, Rainbowbright,
Yerk, Zilla, Gitar3) plus a handful of one-off DRX quest minibosses (the Bloodwitch High Priest/
disciple miniboss, the Blood Abomination Spirit Caller, Anapaest, the "D2NPC" trio Akara/Charsi/
Gheed) and a few Hero-classified oddities (the Egypt dark obelisk, the fire trap, an ambush
tidecrawler, a rumor-monster raptor). None of these are stubs; they simply have never had a soul
authored for them.

---

## 5. Wiring recipe (quoted verbatim from source)

The following rules are quoted exactly as written in the repo (not paraphrased), for use when
designing and implementing any new soul from Table B or Table A above.

### 5.1 Bare `_ensure_record` vs `clone_record` for souls

From `docs/CONTENT_PLAYBOOK.md`  Section 13 (failure-graveyard table):

> | `clone_record` to make a new soul | Drags source soul stats that corrupt saved items | Create
> souls bare with `_ensure_record`; set only intended fields (`create_uber_souls.py:614-619`) |

From `CLAUDE.md`  "Key technical lessons":

> - **Never `clone_record` for souls:** brings stat values that corrupt saved items; use bare
>   `_ensure_record()`.

The `_ensure_record` helper itself (`tools/apply_svc_patches.py:18-26`, also duplicated in
`tools/build_svc_database.py:509`):

```python
def _ensure_record(db, path, template):
    """Create a new empty record in the database if it doesn't exist."""
    if not db.has_record(path):
        db.ensure_string(path)
        db._raw_records[path] = (db.ensure_string(path), b'')
        db._record_types[path] = template
        db._record_timestamps[path] = 0
        db._decoded_cache[path] = OrderedDict()
        db._modified.add(path)
```

### 5.2 Permanent pets: `spawnObjectsTimeToLive: []`

From `CLAUDE.md`  "Key technical lessons":

> - **Permanent pets:** remove `spawnObjectsTimeToLive` (set to `[]`). Reference soul: Lyia
>   Leafsong.

From `docs/CONTENT_PLAYBOOK.md`  Section 6.2 ("Permanent pets (the TTL trick)"):

> A soul pet should be permanent (no despawn timer). The trick: the summon skill must NOT carry a
> `spawnObjectsTimeToLive` field (equivalently, set it to `[]`). Verified: the built
> `records\skills\soulskills\summon_rakanizeus.dbr` has `spawnObjects` (the 3 pet paths) but NO
> `spawnObjectsTimeToLive` at all.

And in the same file's failure-graveyard table (Section 13):

> | Leaving `spawnObjectsTimeToLive` on a soul summon | Pet despawns after the TTL | Omit the field
> (clone from Lyia's permanent `summon_lyia.dbr`); never add a TTL
> (`apply_svc_patches.py:444-452`) |

### 5.3 The Pet.tpl vs Monster.tpl field-copy crash rule

From `docs/CONTENT_PLAYBOOK.md`  Section 6.1 ("The Pet.tpl vs Monster.tpl crash rule (hard lesson,
made concrete)"), quoted in full:

> A pet MUST use `Database\Templates\Pet.tpl` (Class `Pet`), NOT a Monster template. Copying ANY
> equipment or loot field FROM a Monster.tpl record INTO a Pet.tpl record CRASHES the game - even
> merely changing the value of an existing shared field via a dtype-overwriting copy. Only
> ANIMATION and SKILL fields are safe to copy from the source monster. This is why the pet builders
> (`_create_rakanizeus_pet_skill` etc., `apply_svc_patches.py:320+`):
>
> - CLONE the pet from **Lyia Leafsong** (`records\skills\soulskills\pets\
>   lyialeafsong_{1,2,3}.dbr`), which is already a valid permanent `Pet` with full
>   equipment/skills/all required Pet.tpl fields, so the clone inherits a correct Pet schema
>   (`apply_svc_patches.py:331-335`).
> - Copy ONLY animation fields (`_copy_animation_fields`, matches `Anim`/`anim` in the field name,
>   `apply_svc_patches.py:217-261`) and ONLY UPDATE existing skill fields (`_update_existing_fields`
>   with `_SKILL_PREFIXES`, never adding new fields, dtype-preserving,
>   `apply_svc_patches.py:270-300`) from the real monster.
> - Set equipment via `_set_pet_equipment` (`apply_svc_patches.py:303-317`) with HARDCODED item
>   paths and NO dtype (preserving the cloned field dtypes), NEVER by copying the monster's
>   equipment fields.

And the corresponding failure-graveyard row (Section 13):

> | Copying equipment/loot fields from Monster.tpl into a Pet.tpl record | Crashes the game (even
> changing an existing shared field's value) | Clone the pet from Lyia (valid Pet.tpl); copy ONLY
> animation + update-only skill fields; set equipment via `_set_pet_equipment` with hardcoded paths
> (`apply_svc_patches.py:303-317`) |

Also relevant, the dtype-preservation rule that compounds with the above (`CLAUDE.md`):

> - **dtype preservation:** never pass explicit dtype to `set_field()` on cloned records - INT/FLOAT
>   corruption silently zeroes values (pet spawn failure).

### 5.4 The `{^F}` name-tag prefix convention

From `CLAUDE.md`  "Key technical lessons":

> - **`{^F}` prefix** required on soul name tags for pink/magenta text.

From `docs/CONTENT_PLAYBOOK.md`  Section 13 (failure-graveyard table):

> | Soul name tag with no `{^F}` prefix | Soul name renders in default color, not the pink soul
> color | Prefix the Text.arc VALUE with `{^F}` (`create_uber_souls.py:575`) |

Live examples from `tools/apply_svc_patches.py` (the Text.arc tag VALUES the build authors,
`{^F}` = pink/magenta color matching the original SV soul style):

```python
# Soul name tags ({^F} = pink/magenta color, matching original SV soul style)
tags['tagSVCSoulColdWorm'] = '{^F}Cold Worm Soul'
tags['tagSVCSoulSPToxeus'] = '{^F}Soul of Toxeus the Murderer (SP)'
tags['tagSVCSoulLeinth'] = '{^F}Soul of Leinth the Blood Witch'
tags['tagSVCSoulMurderBunny'] = '{^F}Soul of the Murder Bunny'
tags['tagSVCSoulSPHades'] = '{^F}Soul of Hades (SP)'
tags['tagSVCSoulDagon'] = '{^F}Soul of Dagon'
```

### 5.5 Icon path convention

From `CLAUDE.md`  "Key technical lessons":

> - **Soul icon paths:** `SVItems\jewelry\soul_{n,e,l}_icon.tex` (first path component = archive
>   name).

From `docs/CONTENT_PLAYBOOK.md`  Section 1.3 ("Asset paths are archive-name-first"):

> An asset path's FIRST path component is the `.arc` archive it lives in. Example:
> `SVItems\jewelry\soul_n_icon.tex` resolves from `SVItems.arc`; `drx\meshes\n_soulmesh.msh`
> from `drx.arc`; `Creatures\Monster\Skeleton\ RevenantFire.msh` from the base `Creatures`/xpack
> archives. If an icon shows as a grey box or a mesh is invisible, the archive is missing or
> stripped.

And Section 13's failure-graveyard row for the common mistake:

> | Soul `bitmap` pointing at `Items\miscellaneous\{n,e,l}_soul.tex` | That path is not in
> `Items.arc`; icon shows as a grey box | Point `bitmap` at `SVItems\jewelry\soul_{n,e,l}_icon.tex`;
> `fix_soul_bitmaps` fixes strays at build end (`build_svc_database.py:1325-1358`) |

The exact field/value pair as coded (`tools/apply_svc_patches.py:1215,1294`):

```python
'bitmap': (DATA_TYPE_STRING, r'SVItems\jewelry\soul_n_icon.tex'),
```

### 5.6 The Text.arc tag validator

From `tools/validate_tags.py` module docstring, quoted in full (this is the build-time gate that
gave rise to the orphaned-tag bug fix referenced in `CLAUDE.md`):

> Build-time validator: every mod name/description tag in the .arz must resolve to a string in the
> final Text.arc.
>
> Root problem this guards against: create_uber_souls.py regenerates a different tag->monster
> mapping on every build (as the candidate pool shrinks), while build_text_arc.py is a separate
> invocation with no staleness coupling. If Text.arc is built against an older tag list than the
> .arz, a soul item ends up referencing a tag (e.g. tagSoulSVC9005 / tagSoulSVC9006) that is absent
> from Text.arc, so the raw tag string shows in-game instead of the soul name.
>
> What "mod-owned" means (the design that keeps this false-positive-free):
>   A tag is MOD-OWNED iff the mod's build actually AUTHORS it into its own Text.arc. The build now
>   emits that authoritative set to a manifest (mod_authored_tags.txt, written by build_text_arc.py
>   next to Text.arc) which is the union of every tag the build's emitters source:
>     - build_text_arc.py OCCULT_FIX_TAGS + QUEST_INTEGRATION_TAGS
>     - build_svc_database.py MOD_DESC_FIX_TAGS values (tagbreachDESC, ...)
>     - uber_soul_tags.txt keys (soul + legacy + extended, incl. tagD2Boss*)
>   Membership in that written set - NOT a hard-coded tag prefix - decides mod-ownership. Base-game
>   tags the .arz merely carries forward (tagNewMonster*, tagItem*, tagMonsterNameSFM*, ...) are
>   overlaid on the engine's own text and are NOT in the manifest, so they never produce false
>   positives even though they are referenced by the .arz.
>
> Usage:
>   py tools/validate_tags.py <final.arz> <final_text.arc> [authoritative_tags.txt]
>                             [mod_authored_tags.txt]
>
> Exit codes:
>   0 = all referenced mod tags present in Text.arc
>   1 = one or more mod tags missing (details printed)
>   2 = usage / input error (could not read an input file)

And the corresponding failure-graveyard row (`docs/CONTENT_PLAYBOOK.md` Section 13):

> | A `.arz` name\desc tag missing from `Text.arc` (e.g. `tagSoulSVC9005\9006`) | Raw `tag...`
> string shows in-game | `validate_tags.py` gate fails the build; author the tag into the pipeline
> so it lands in `Text.arc` (`validate_tags.py`, gate at `bootstrap_working_mod.ps1:335-367`) |

**Practical implication for any new soul from this audit:** any new `itemNameTag`/description tag
value authored for a Table A/B soul must be added to the build's tag-authoring pipeline (so it
lands in the `mod_authored_tags.txt` manifest) before running `validate_tags.py`, or the build gate
will fail loud rather than silently shipping a raw-tag string in-game.

---

## 6. ADDENDUM: second-pass verification findings (independent re-scan)

A second, independent pass over the same built `.arz` (same reader, different filter
construction: creature-pathed records with `monsterClassification` in Hero/Boss/Quest
OR a boss-ish identity, deliberately NOT repeating `wire_souls_to_monsters`'s
`'monster' in Class/templateName` gate so that unique-class bosses `Class=Hades` /
`Cerberus` / `Ormenos` / `Megalesios` / `SpiritHost` and unclassified boss-named fight
props are also swept) confirmed everything above and surfaced four findings the first
pass could not see. These supersede the affected rows/claims above where noted.

### 6.1 P1 BUG - Ainex, Queen of Crows drops a soul that does not exist

`records\xpack\creatures\monster\empusa\um_ainex_45.dbr` (Hero, an SV superboss,
levels 45/62/73) is counted as "HAS a wired soul" in Table A's 616 because it carries:

```
lootFinger2Item1     = [records/item/equipmentring/soul/empusa/ainex_soul_n.dbr,
                        .../ainex_soul_e.dbr, .../ainex_soul_l.dbr]
chanceToEquipFinger2 = 100.0   (testing build)
dropItems            = 1
```

**None of those three soul records exist anywhere in the built database** (0 records
match `ainex` under `equipmentring`). Verified upstream: SV 0.98i carries the exact
same dangling `lootFinger2Item1` on `um_ainex_45.dbr` (at `chanceToEquipFinger2=5.0`)
and ALSO has no `ainex_soul_*` item records; nor do 0.9/041. **This is a boss whose
soul the original SV developers never finished** - they wired the drop and never
authored the item (ask B, textbook case). Killing her rolls the Finger2 slot and
equips/drops nothing.

Why the build's own safety nets miss it:

- `_place_orphan_monsters` (`tools/apply_svc_patches.py:3119-3170`) explicitly lists
  `('um_ainex_45', 'empusa', 'Ainex Lv45', 45)` and would auto-create a fallback soul,
  but it first checks `_has_soul(db, rec)` - and `_has_soul`
  (`apply_svc_patches.py:2853-2864`) only tests that `lootFinger2Item1` *mentions* a
  path containing "soul", never that the record resolves. The dangling reference
  therefore disables her own fallback.
- The name tag is already authored: `tags['tagSVCSoulAinex'] = '{^F}Soul of Ainex'`
  (`apply_svc_patches.py:4358`), so Text.arc is ready and `validate_tags` passes.

**Fix shape:** author `ainex_soul_{n,e,l}.dbr` under `soul\empusa\` (bare
`_ensure_record`, Section 5.1) with an empusa/crow-themed kit - her monster record's
signature skills are `empusa_spirit_lifedrainnova` (AttackProjectileAreaEffect),
`inkeyes_blink` (AttackSpellTeleportSelf), `throwingknife_multi`
(AttackProjectileBurst) - and harden `_has_soul()` to also require
`db.has_record(ref)` so this class of dangling reference can never silently gate the
fallback again.

### 6.2 MED BUG - "Inhabited Statue" (Champion fight prop) drops the Megalesios telkine soul at full chance

`records\creature\monster\questbosses\boss_greektelkine_megalesiosstatue_{21,24,27}.dbr`
are the possessed-statue props of the Megalesios fight: `Class=SpiritHost`,
`monsterClassification=Champion`. All three carry
`lootFinger2Item1 = soul\telkine\megalesios_soul_{n,e,l}` with
`chanceToEquipFinger2 = 100.0` in the built DB.

This violates the documented design gate (only Hero/Boss/Quest drop souls; the
2026-07-05 yeti fix). The gate misses them through the SAME loophole family as the
yeti bug, one filter deeper: `wire_souls_to_monsters`'s Common/Champion zeroing pass
(`build_svc_database.py:312-357`) only visits records with `'monster'` in
`Class`/`templateName`, so `SpiritHost` records are never zeroed, and
`_force_100_pct_soul_drops` (which correctly keys on existing `chance > 0`) then
boosts their SV-inherited nonzero chance to 100. Result: a farmable-adds source for a
Telkine boss soul. Fix shape: widen the zeroing pass beyond the `'monster'` substring
gate (or explicitly zero `chanceToEquipFinger2` on the three statue records).

### 6.3 LOW - Legion is wired to a Dropbox conflict-file soul; 77 junk soul records ship in the DB

`um_legion_28.dbr`, `um_legion_28a.dbr`, `um_legion_28b.dbr` (Hero "Legion",
eurynomus) reference ``soul\eurynomus\legion_soul_n (amgoz-qosmio's conflicted copy
2013-08-07).dbr`` as their soul; only `um_legion_28c.dbr` points at the clean
`legion_soul_n.dbr`. The conflicted-copy record exists in the DB, so the drop works,
but it is a single `_n` record (no `[n,e,l]` difficulty array - Epic/Legendary kills
drop the Normal-tier soul) and a data-hygiene wart. In total **77 soul records named
"... (amgoz-qosmio's conflicted copy 2013-08-07)" or "copy of ..." ship in the built
DB**, inherited from SV 0.98i's own source tree; the rest of them are unwired
duplicates of clean records. Fix shape: repoint the three Legion records at
`legion_soul_{n,e,l}` like `_28c`.

### 6.4 The never-completed (STAT-ONLY) soul surface - 40 wired souls that grant no skill, augment, or summon

Grading every soul item actually wired to a Hero/Boss/Quest monster (554 wired soul
bases in total): **514 grant a real skill/augment/summon (FULL); 40 are pure stat
sticks the original SV developers never finished** (no `itemSkillName`, no
`augmentSkillName*`, stats only). This is the concrete "souls that never got
completed" surface for ask B beyond the boss tier - the prior mod waves already
overhauled 78 generic souls (`_overhaul_generic_souls`) and authored 140 `svc_uber`
souls; these 40 are what remains. One is Boss-tier (Ancient Limos, Table B's headline
stub); the other 39 are Hero/Quest named monsters. Monster core skills listed as
design raw material (boilerplate passives filtered).

| # | Soul base | Dropped by | Cls | Lv (N/E/L) | Monster's core skills (design input) |
|---|-----------|-----------|-----|------------|----------------------------------------|
| 1 | `ancientscorpos` | Ancient Scorpos ~ Beast of Legend | Hero | 20/23/26 | `scorpos_sting`, `hero_scaling`, `attack_damagemodifier_02`, `boss_conversionimmunity`, `poisonspit_nova`, `heartofoak`, `rally` |
| 2 | `aorg` | Warlord Aorg | Hero | 43/59/72 | `hero_scaling`, `elementalresistance_10xlevel`, `boss_conversionimmunity`, `bonusdamage_physical`, `hero_hadesbolt`, `hero_slowspiritbolt_ring` |
| 3 | `behemoth` | Khojasteh the Behemoth | Hero | 39/57/70 | `waterwave_ring`, `hero_scaling`, `hero_physical`, `shark_summon`, `charge_concussivedamage`, `drxrally`, `attack_damagemodifier_02` |
| 4 | `birdofsorrow` | Bird of Sorrow | Hero | 6/35/53 | `birdofsorrow_bonusdamage`, `hero_scaling`, `hero_vitality`, `visionofdeath`, `physdmg_meleeonly02`, `hero_modifier` |
| 5 | `blackbite` | Black Bite | Hero | 16/41/57 | `vampirebat_vampiricbite`, `hero_scaling`, `hero_vitality`, `wraithlord_petskill_deathnova`, `arachnosbloodlust_aoe`, `physdmg_meleeonly01`, `bonusdamage_%life_+1%perlevelx100` |
| 6 | `blastfang` | Blast Fang | Hero | 13/39/56 | `vampirebat_vampiricbite`, `hero_scaling`, `hero_fire`, `orthus_firebreath`, `revenant_burningtouch`, `physdmg_meleeonly01`, `pillarofflame` |
| 7 | `cepharis` | Cepharis ~ Master of the Flame | Quest | 12/14/18 | `fireenchantment`, `hero_scaling`, `attack_damagemodifier_02`, `boss_conversionimmunity`, `fireenchantment_brimstone`, `fireenchantment_stoneskin`, `flamesurge` |
| 8 | `coastalichthianmyrmidon` | Koroush, Lurker of Samarkand | Hero | 39/56/70 | `drx_summon_shadow_stalker`, `drxcalculatedstrike`, `hero_scaling`, `hero_energy`, `magebane`, `nightstalker_shadowbolt`, `spiritenhancement` |
| 9 | `coldburnedcorpse` | Putrescent Zombie ~ Blightcaster | Quest | 35/37/53 | `plague`, `paralysisresistance_10xlevel`, `elementalresistance_10xlevel`, `ondeath_zombienoxiousfumes`, `resist_undead2`, `zombiecaster_poisonorbspread` |
| 10 | `coldpaw` | Cold Paw | Hero | 29/52/67 | `enchantment_cold`, `hero_scaling`, `hero_cold`, `frostattack_radius01`, `bonusdamage_cold_+1perlevelx100`, `physdmg_meleeonly`, `borealic_icecoat` |
| 11 | `coldtusk` | Coldtusk | Hero | 17/42/58 | `hero_scaling`, `hero_cold`, `bonusdamage_cold_+1perlevelx100`, `coldtusk_charge`, `coldtusk_icecrystals`, `physdmg_meleeonly` |
| 12 | `diseasedvulture` | Corpse Wake | Hero | 24/49/64 | `razorquill_megaburst`, `hero_scaling`, `hero_modifier`, `razorbird_retaliation`, `ondeath_bladeorb`, `character_vampiriaura`, `bladestorm` |
| 13 | `emberteeth` | Ember Teeth | Hero | 18/43/58 | `emberteeth_meleeattack`, `retaliation_1fireperlevelx100levels`, `hero_scaling`, `hero_fire`, `orthus_firebreath`, `ondeath_fireorb`, `physdmg_meleeonly` |
| 14 | `fistoframses` | Fist of Ramses | Hero | 36/46/71 | `reptillian_shout`, `sd_globalproperties_normal01`, `sd_globalproperties_epic01`, `hero_scaling`, `hero_physical`, `boss_conversionimmunity`, `construct_resists` |
| 15 | `flarecrawler` | Flare Crawler | Hero | 29/49/64 | `flarecrawler_minionsummon`, `flarecrawler_bonusdamage`, `hero_scaling`, `hero_fire`, `bonusdefense_burnresist_+1%perlevelx100`, `racial_insectoid`, `crawler_boltfan` |
| 16 | `flayerofsouls` | Flayer of Souls | Hero | 43/59/72 | `hero_scaling`, `elementalresistance_10xlevel`, `boss_conversionimmunity`, `physdmg_meleeonly`, `hero_limos_consumelife`, `hero_hadesbolt` |
| 17 | `frozenhorror` | The Frozen Horror | Hero | 43/60/73 | `stormnimbus`, `hero_scaling`, `elementalresistance_10xlevel`, `physdmg_meleeonly`, `stormnimbus_heartoffrost`, `bonusdamage_cold_+1perlevelx100`, `frozenhorror_orb` |
| 18 | `gorlab` | Blood Hurdler / Gorlab the Charred One | Hero | 35/37/54 | `firesprite_flametouch`, `ringofflame`, `hero_scaling`, `flamesurge`, `flamesurge_flamearch`, `flamesurge_barrage`, `ondeath_fireorb` |
| 19 | `inemios` | Inemios the Manafeaster | Hero | 41/58/71 | `inemios_minionsummon`, `manafeast_consumemana`, `hero_scaling`, `hero_energy`, `attack_damagemodifier_02`, `inemios_bonusdamage`, `manafeast_bolt` |
| 20 | `legion` | Legion | Hero | 14/40/56 | `melee_lifeleech_01`, `sd_globalproperties_normal01`, `sd_globalproperties_epic01`, `hero_scaling`, `hero_physical`, `monster_consumelife`, `automatoi_minstun` |
| 21 | `legion_soul_n` *(the conflict-file record, Section 6.3)* | Legion | Hero | 14/40/56 | `melee_lifeleech_01`, `sd_globalproperties_normal01`, `sd_globalproperties_epic01`, `hero_scaling`, `hero_physical`, `physdmg_meleeonly01`, `automatoi_minstun` |
| 22 | `leng` | Leng-Chuxi, Dark Djinn | Hero | 45/62/73 | `leng_orb`, `leng_minionsummon`, `hero_modifier`, `hero_vitality`, `leng_orbnova`, `leng_projectiletrigger` |
| 23 | `limoslifeater` | Ancient Limos ~ Soul Stealer | Boss | 36/54/69 | `limos_consumelife02`, `hero_cold`, `attack_damagemodifier_02`, `physdmg_meleeonly` |
| 24 | `mulgorflamespear` | Mulgor Flamespear | Hero | 16/41/57 | `fireenchantment`, `earthfury_flaming`, `hero_scaling`, `hero_fire`, `earthfury_ring`, `damagephysical_passivemodifier01` |
| 25 | `mutabeak` | Mutabeak | Hero | 12/38/55 | `mutabeak_minionsummon`, `mutabeak_bonusdamage`, `hero_scaling`, `hero_elemental`, `physdmg_meleeonly02` |
| 26 | `nemeanboar` | Nemean Boar | Hero | 17/45/60 | `stampede_aura`, `hero_scaling`, `bonusdamage_fire_+1perlevelx100`, `monster_charge_unarmed`, `physdmg_meleeonly01` |
| 27 | `nicothoe` | Nicothoe Grimfeather | Hero | 18/42/58 | `nicothoe_bolt`, `nicothoe_minionsummon`, `hero_scaling`, `hero_vitality`, `nicothoe_smallboltring`, `physdmg_meleeonly`, `hero_modifier` |
| 28 | `nokhai` | Sentinel Nok-hai, Guardian of the Necklace | Hero | 45/60/73 | `ternion_bow`, `envenomweapon`, `hero_scaling`, `elementalresistance_10xlevel`, `boss_conversionimmunity`, `bonusdamage_physical`, `toxindistillation` |
| 29 | `pthirus` | Pthirus | Hero | 36/54/69 | `envenomweapon`, `physdmg_meleeonly01`, `hero_scaling`, `elementalresistance_10xlevel`, `boss_conversionimmunity`, `hero_poisongasball`, `toxindistillation` |
| 30 | `rotbone` | Rot Bone | Hero | 14/40/56 | `revenant_wiltingtouch`, `hero_scaling`, `ondeath_poisonorb`, `attack_damagemodifier_01`, `rotcloud`, `resist_undead` |
| 31 | `rottingdevourer` | The Rotting Devourer | Hero | 27/34/42 | `envenomweapon`, `hero_poisonwave`, `hero_scaling`, `elementalresistance_10xlevel`, `boss_conversionimmunity`, `physdmg_meleeonly01`, `drxenvenomweapon_neurotoxin` |
| 32 | `scorix` | Scorix Grimchitin | Hero | 18/42/58 | `scorix_boltfan1`, `hero_scaling`, `hero_bleed`, `racial_insectoid`, `scorix_boltfan2`, `bonusdamage_poisonvita_+1perlevelx100`, `damagephysical_passivemodifier01` |
| 33 | `stygianboar` | Stygian Boar | Hero | 16/44/58 | `drxskelly_petskill_deathtouch`, `drxdeathchillaura`, `hero_scaling`, `drxdeathward`, `visionofdeath`, `physdmg_meleeonly01`, `drxspiritward_spiritbane` |
| 34 | `tarthon` | Tarthon Na'Arak | Hero | 34/53/68 | `damage_lightningbonus`, `damagelightning_lightningball`, `hero_scaling`, `dragonian_reflection`, `attack_damagemodifier_02`, `thunderball`, `thunderball_concussiveblast` |
| 35 | `terrorofthedark` | Terror of the Dark | Hero | 47/62/74 | `hero_scaling`, `elementalresistance_10xlevel`, `boss_conversionimmunity`, `physdmg_meleeonly`, `hero_flamewave`, `drxabyssal_flameliche_rainoffire` |
| 36 | `thebloatedone` | The Bloated One | Quest | 45/60/73 | `hero_scaling`, `elementalresistance_10xlevel`, `boss_conversionimmunity`, `racial_insectoid`, `physdmg_meleeonly01`, `bloatedone_layeggs`, `albinospider_lifelightningbonus` |
| 37 | `thelurker` | The Lurker | Hero | 38/55/70 | `yama_aura`, `bogdweller_bite`, `hero_scaling`, `elementalresistance_10xlevel`, `boss_conversionimmunity`, `racial_plant`, `physdmg_meleeonly01` |
| 38 | `thetombkeeper` | The Tombkeeper | Hero | 30/51/66 | `hero_scaling`, `defense_undeadresists`, `tombguardian_flamering`, `wraithlord_petskill_deathnova`, `physdmg_meleeonly`, `hero_modifier` |
| 39 | `vilerotter` | Vile Crawl | Hero | 28/51/66 | `arachne_close_poisoncloud`, `hero_scaling`, `hero_poison`, `racial_insectoid`, `scarabaeus_ranged_causticsputum`, `physdmg_meleeonly01` |
| 40 | `webshot` | S'ckti'nkt Webshot | Hero | 36/56/69 | `webshot`, `hero_scaling`, `hero_modifier`, `racial_insectoid`, `summon_spiders`, `albinospiderqueen_rangedweb`, `adacil_lifeleachbolt` |

### 6.5 Scan-scope notes and corrections to earlier sections

- **Correction to Table A / Section 4 counts:** `um_ainex_45` must be moved from the
  "HAS a wired, working soul" bucket (616) to a new **P1 broken** bucket (Section
  6.1). Effective: 615 HAS, 1 BROKEN-REF.
- **Correction to Table B's headline:** "only 1 of 60 bosses lacks a functional soul"
  remains true for `monsterClassification == Boss` records, but Ainex (Hero-classified
  SV superboss at 100% wired chance) is a second de-facto boss-tier design target, and
  the 39 Hero/Quest rows of Section 6.4 are the long tail.
- The second pass also swept boss-named fight props that carry NO
  `monsterClassification` at all and were therefore invisible to the classification
  gate of the first pass: `boss_pharaohshonorguard_spirit.dbr` (the unkillable spirit
  phase), `talos_decoration.dbr`, `typhonstatue{apollo,demeter,hades,zeus}.dbr` (+
  `backup_`/`copy of` author relics), `typhon_chain_object.dbr`,
  `megalesiosfirewall.dbr`, `megalesiosconduit.dbr`, and the Canopic Shrine obelisks
  (`pharaohshonorguard_obelisk{a-d}_{20,25}.dbr`, Common). All are scenery/props of
  fights whose REAL boss records are fully wired (all 12 `boss_pharaohshonorguard{1-4}`
  records carry the `pharaohshonorguard` souls at 100%); none needs a soul. No action.
- The legacy `records\xpack\creatures\monster\bosses\01_graeae\old\` Graeae
  records (9 records: `boss_{deino,enyo,pemphredo}_*_old.dbr`) have no wired soul, but
  the live non-old Graeae records are fully wired with FULL souls; the `old` variants
  are unreachable leftovers. No action.
- 103 of the 2,270 soul item records are unwired STUB placeholders by design (~87
  per-folder `soultemplate.dbr` authoring templates and 16 `any*herosoul` /
  `anysoul` placeholders). Verified: no monster references any of them. No action.

### 6.6 Priority queue distilled from the whole audit

1. **P1**: create `ainex_soul_{n,e,l}` (tag exists; kit in 6.1) and harden
   `_has_soul()` with a `db.has_record()` check.
2. **MED**: zero the three `megalesiosstatue` Champion records' `chanceToEquipFinger2`
   (or widen the zeroing pass beyond the `'monster'` Class filter).
3. **Design wave (ask B)**: Ancient Limos (Table B headline) + the 39 Hero/Quest
   stat-only souls (Section 6.4) + the ~28 Medium no-soul monsters of Table A
   (crow heroes, D2NPC trio, blood-cave quest heroes, jo7 raptors, Ankle Sickle).
4. **LOW**: repoint `um_legion_28/a/b` at the clean `legion_soul_{n,e,l}`; decide the
   device-hero policy (Monolith, The Trap).
