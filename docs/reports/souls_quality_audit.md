# Souls Quality Audit - build40 ground truth (GOOD / MINOR-GAP / DEFICIENT)

> Ground-truth comparison of EVERY soul ring in the deployed build40 database against its
> SV 0.98i original (the design bible for generated souls). Read-only audit; no artifact was
> modified. No em dashes by house style.

## 1. Scope + ground truth

- **Audited artifact:** `work/SoulvizierClassic/Database/SoulvizierClassic.arz`,
  md5 `b33c5a447f3a8ca652c14f78d4ad1dd4` (55,351,206 B) = the **build40 GOLDEN** arz
  (BACKLOG build40 gate record), re-hashed at audit time.
- **SV original baseline:** `upstream/soulvizier_098i/Database/database.arz` (51,186 records).
- **Reference resolution:** mod arz UNION base-game TQAE `database.arz` (74,013 records),
  matching how the engine overlays the mod on the base DB.
- **Text:** shipped `work/SoulvizierClassic/Resources/Text.arc` (build40, md5 `c910da65...`)
  union base `Text_EN.arc`; icon presence vs shipped `SVItems.arc` / `Items.arc` entries.
- **Method:** every record under `records\item\equipmentring\soul\` with the Jewelry_Ring
  class/template was enumerated (2,398 rings), grouped into families by tier suffix, matched
  to the SV original by exact path (else basename), and graded per the rubric in section 2.
  Probe: session scratchpad `souls_audit_engine2.py` (read-only; per-family JSON evidence).

**Independent cross-checks (run against this exact arz):**
`tools/validate_soul_augments.py` = **PASS** (4,938 skill refs, 1,390 activation chains, 0 dangling,
0 inactive - the B-SOUL-PROC-1/2 classes are CLEAN in build40), and `tools/validate_summon_pets.py`
(B-SUMMON-1 contract) - see section 7.

## 2. Rubric (the 6 graded axes)

1. **Stat fidelity vs SV intent** - any nonzero SV stat now zero/absent (hand-boosts are LAW, only losses count).
2. **Augment liveness** - no +0/absent `augmentSkillLevelN` behind a set `augmentSkillNameN`; refs resolve; N<=E<=L tier progression.
3. **Granted-skill soundness + identity** - itemSkillName resolves to a real castable Skill_* (anim universally
   playable, controller template/chance/trigger/radius live, itemSkillLevel >= 1); family-roster identity fit
   (skill_quality diversity law respected).
4. **Pet kit fidelity** - spawnObjects resolve; pet has a live kit (vs SV's); permanence not silently regressed
   from SV; equip slots resolve (upstream 'x' disable markers exempt).
5. **Name/desc flavor** - name tag resolves in shipped Text, carries the {^F} soul prefix; SV flavor text not lost;
   amgoz1 voice: SV names untouched, generated souls use the '<Monster> Soul' standard, hand-designed uber souls
   keep evocative names (naming exemption).
6. **Icon correctness** - tier icon matches the ring's tier; texture present in shipped arcs.

**Grades:** DEFICIENT = at least one functional defect a player can hit. MINOR-GAP = cosmetic/obtainability/
fidelity evidence, soul still fully functional. GOOD = clean on all six axes.

## 3. Headline numbers

| Metric | Count |
|---|---:|
| Soul rings in build40 arz | 2398 |
| Soul families enumerated (total) | 871 |
| **Gradeable souls (REAL)** | **708** |
| ... with an SV 0.98i original | 608 |
| ... mod-new (judged on amgoz1 bar + internal consistency) | 100 |
| **GOOD** | **548** |
| **MINOR-GAP** | **155** |
| **DEFICIENT** | **5** |
| Non-graded scaffolding families (appendix, sec 8) | 163 |

> **Round-2 correction (2026-07-14).** The original audit reported DEFICIENT = 3 and graded
> `spider\bloodtip_soul` and `vulture\gustleech_soul` GOOD. A roster-wide monotonicity re-scan
> found both carry a granted-skill tier inversion (`itemSkillLevel` weaker at a higher rarity)
> the v1 inversion detector missed - it keyed only on `augmentSkillLevel`, never on
> `itemSkillLevel`. Both are re-graded **DEFICIENT** below (sec 4). DEFICIENT is now 5 (the same
> single class, not a new defect type); GOOD drops 550->548. The detector is fixed in
> `tools/debug/_souls_quality_audit.py` (adds `GRANT-LEVEL-TIER-INVERSION`).

MINOR-GAP breakdown (family-level, one family can carry several):

| Evidence class | Families | Reading |
|---|---:|---|
| DROP-GATED-CHANCE-0 | 79 | Souls whose only carriers are Common/Champion monsters; the documented Hero/Boss/Quest-only drop gate zeroes them, so they cannot drop (design question, sec 5 P3-a) |
| ICON-UNIFORM-N | 54 | svc_uber uber souls whose Epic + Legendary rings still show the Normal-tier icon (sec 5 P2-b) |
| SUMMON-SKILL-NYMPH-ICON | 17 | mod-authored boss-summon skills still carry Lyia the nymph's icon; fix already exists on unmerged branch feat/b40-soul-icons (sec 5 P2-c) |
| NO-FINGER2-DROPPER | 5 | referenced ONLY as enchanting-formula reagents; no monster carries them at all (sec 5 P3-b) |
| PET-EQUIP-DANGLING-UPSTREAM | 2 | pet equip slot dangles exactly as SV shipped it (engine skips; hygiene) |
| PET-KIT-SMALLER-THAN-SV | 1 | summoned pet lost part of its SV kit (sec 5 P2-d) |

**The port is faithful.** Across the 608 SV-inherited souls, stat fidelity findings are 2 families
(both LAW hand-edits, noted not fixable), zero dead augments, zero broken proc chains, zero lost granted
skills, zero lost SV flavor text, zero unresolved name tags, and every icon texture resolves in the
shipped arcs. The defect surface is the tier-inversion class (a higher-rarity ring strictly weaker than
a lower-rarity ring on the SAME named skill): 3 in the mod-new svc_uber generation (augment levels,
uniform icons) plus 2 SV-inherited grant-level inversions (`bloodtip`, `gustleech`) that are byte-
identical to SV 0.98i - amgoz1 data-entry oversights the mod faithfully carried forward (sec 4).
Obtainability wiring is the other surface (sec 5).

## 4. DEFICIENT souls (all 5) - the P1 fix items

All five share ONE class: a **higher-rarity ring is strictly WEAKER than a lower-rarity ring on the
SAME named skill**. A player who farms the Epic/Legendary gets a worse item than the tier below - the
classic 'DONE means DONE' repeat-report shape once someone notices. Two provenances:

**4a. The 3 mod-generated svc_uber souls** (Legendary augment levels run n/e/l = 1/2/1, and for
Crowboar the granted-skill level too). Healthy siblings from the same generator (bloodrunner, xix) run
augments 1/2/3 and itemSkillLevel 3/5/8, so the intended progression is unambiguous. Residual of the
B-SOUL-PROC-1 `_DIFF_SCALE` level-floor backstop (create_uber_souls floored n/e to 1 but the L
re-derive clamped back to 1).

| Soul | Records (exact) | Defect (ground truth) | Fix (raise-only; keep Will's skill picks) |
|---|---|---|---|
| Crowboar Soul (LAW-adjacent: hand novelty, improve around it) | `records\item\equipmentring\soul\svc_uber\crowboar_soul_{n,e,l}.dbr` | augments drxonslaught + drxlethalstrike at n/e/l = 1/2/**1**; itemSkillLevel (Summon Carrion Crow) 1/2/**1** | on `_l`: augmentSkillLevel1=3, augmentSkillLevel2=3, itemSkillLevel=3 (bloodrunner/xix progression) |
| Onyxspine the Dismemberer Soul | `records\item\equipmentring\soul\svc_uber\onyxspine_soul_{n,e,l}.dbr` | augments drxonslaught + drxlightningbolt_chainlightning at n/e/l = 1/2/**1** (grant arachnos_venombolt at itemSkillLevel 3/5/8 is healthy) | on `_l`: augmentSkillLevel1=3, augmentSkillLevel2=3 |
| Steamcrawler Soul | `records\item\equipmentring\soul\svc_uber\steamcrawler_soul_{n,e,l}.dbr` | augments drxfireenchantment + drxarmorhandling at n/e/l = 1/2/**1** (no granted skill; the iskLvl 0/0/1 residue is inert) | on `_l`: augmentSkillLevel1=3, augmentSkillLevel2=3 |

**4b. The 2 SV-inherited souls** (round-2 finding; the v1 detector missed these because it never
checked `itemSkillLevel`). Both grant a per-level-scaled skill at a LOWER level on the higher-rarity
ring. Both are **byte-identical to SV 0.98i** (`upstream/soulvizier_098i`), so fixing them is a
deliberate divergence from SV-original data - judged an **amgoz1 data-entry oversight**, not intent:
every OTHER field on both rings tiers upward correctly n->e->l (bloodtip characterLife 120/218/318, its
own leech 20/34/50; gustleech deflect 5/7/9, offensiveLifeMin 12/21/29). Both are obtainable Hero souls
(66% finger2). **RATIFIED by Will 2026-07-14** ("bloodtip 5/7/9 + gustleech 10/12/14 ship as-is") - the
WILL-VETO flag is CLEARED; the fix ships (historical revert path kept in the module). See
`souls_quality_fix.md` D1.

| Soul | Records (exact) | Defect (ground truth) | Fix (raise-only; grant NAME untouched) |
|---|---|---|---|
| Bloodtip the Devourer Soul (SV) | `records\item\equipmentring\soul\spider\bloodtip_soul_{n,e,l}.dbr` | grants `soulskills\bloodtip_devour.dbr` (Devour, per-level leech, maxLvl 20) at itemSkillLevel n/e/l = 5/**1**/9 - Epic (leech 14) weaker than Normal (leech 30). Carrier `um_bloodtip_18` (Hero, 66%) | on `_e`: itemSkillLevel 1->7 => 5/7/9 (leech 30/42/46) |
| Gustleech Soul (SV) | `records\item\equipmentring\soul\vulture\gustleech_soul_{n,e,l}.dbr` | grants `sv\gustleech\leechstrike_soul.dbr` (per-level leech, maxLvl 20) at itemSkillLevel n/e/l = 10/**4**/**7** - Epic (leech 26) AND Legendary (leech 38) weaker than Normal (leech 50). Carrier `um_gustleech_28` (Hero, 66%) | on `_e`: itemSkillLevel 4->12; on `_l`: 7->14 => 10/12/14 (leech 50/58/66) |

Root-cause hardening (shipped in `tools/patches/souls_quality.py` round-2): the module fixes all 5
raise-only, and its `verify()` extends the tier-monotonicity check (n<=e<=l on augment AND grant levels,
same-skill-name-guarded) to **EVERY** soul equipmentring family, not just svc_uber, so the class cannot
regress anywhere. A durable generator clamp in `tools/create_uber_souls.py` (`max(l_level, e_level)`)
remains a good belt-and-suspenders follow-up for the mod-generated arm.

## 5. Prioritized FIX LIST (after the P1 trio)

### P2 (should fix before the next content build)

**P2-a. Tomb Guardian uber soul is unobtainable. -> RESOLVED (FIX-WAVE-2 D2 / FIX 5).**
`svc_uber\um_tombguardian_soul_{n,e,l}` ('Tomb Guardian ~ Hound of Anubis Soul') is carried ONLY by
`records\creature\monster\tombguardian\um_tombguardian_26.dbr` (`monsterClassification=Common`), which -
the audit missed this - STILL attaches the soul via `lootFinger2Item1`, only gated off by
`chanceToEquipFinger2=0.0` (a referenced-but-unobtainable ghost, wired by `_place_orphan_monsters`
"against the Hero/Boss/Quest design"). **Will directed 2026-07-14: "Do not promote tomb guardian and do
not have him drop a soul."** So instead of reclassifying to Hero, FIX 5 keeps it Common, DETACHES the
soul (`lootFinger2Item1` cleared), RETIRES the 3 now-unreferenced soul records, and DROPS the
`tagSVCSoulTombguardian` tag. Verified: 0 residual references, no dangling ref. See `souls_quality_fix.md`
sec 3 (P2-a).

**P2-b. Uber souls: Epic/Legendary rings show the Normal-tier icon (54 families, ~108 records).**
Every `svc_uber\*_soul_e/_l.dbr` carries `bitmap=SVItems\jewelry\soul_n_icon.tex`. The icon law is
`soul_{n,e,l}_icon.tex` per tier (CLAUDE.md key lessons; every SV-inherited soul obeys it). One-line batch
fix in the uber-soul generation (`create_uber_souls.py`): set the tier icon from the tier suffix. Purely
cosmetic, zero gameplay risk, arc textures already shipped (soul_e/soul_l icons resolve in SVItems.arc).

**P2-c. Boss-summon skills show the nymph icon (17 souls).**
Known, fixed on the UNMERGED branch `feat/b40-soul-icons` (commit `9db3f5f`): `_build_boss_summon()` clones
`summon_lyia.dbr` and never overrode `skillUpBitmapName`/`skillDownBitmapName`. This audit independently
re-confirms all 17 grantor souls in the build40 arz (pygmalion, phagia/meritamen, sarpedon, eaterofdays,
palai/longnu, xeiwang, blood_toxeus, broodmother, enslaver, ferryman, hadesmarshal, kravmoloch, mnemophage,
mountainblade, neferkha, tantalus, voranthys). Action: integrate that branch in the next integration build;
no new work needed.

**P2-d. Soulfeeder's pet lost part of its SV kit.**
`bonescourge\soulfeeder_soul` summons `bonepet20`; vs the SV original the pet is missing
`bonescourge_spiritbreath.dbr` (the other loss, `drxplaceholder.dbr`, is an upstream disable marker and
correct to drop). Restore the spirit-breath attack to the pet's kit (identity: the Soulfeeder IS a
spirit-devourer; the breath is its signature). Change class: pet skill wiring in the pet-kit wave files.

### P3 (design decisions / hygiene; several are one-line notes for Will)

**P3-a. 79 souls are drop-dead because only Common/Champion monsters carry them.**
The 2026-07-05 yeti-fix design gate (only Hero/Boss/Quest drop souls) zeroes `chanceToEquipFinger2` on
every Common/Champion carrier, so these souls (Satyr Peltast, Cave Bat, Yeti, the harpy hags/crones,
maenad mooks, ichthian mooks, zombie mooks, ...) can no longer drop AT ALL, while several are still
enchanting-formula reagents (e.g. `satyrpawn_soul` feeds `n_01_rare_axe_formula`). In SV these dropped
from their common monsters. Decision for Will (one line in the gate, both files): add 'Champion' to the
wire gate (documented option in CLAUDE.md), re-tier the affected souls onto family Heroes, or accept them
as formula-only ghosts. Full family list in the graded table (evidence 'drop-gated'). Note: Keres
Aphiastas sits in this set BY LAW (the F1 fix wave deliberately de-wired it at the root - leave it).

**P3-b. 5 souls are never carried by ANY monster** (their only references are enchanting-formula
reagent slots): `\satyrmagi_soul`, `\satyrveteranpeltast_soul`, `antlion\frostmandible_soul`, `empusa\alcestis_soul`, `zombie\oythroneus_soul`.
Even re-opening the Common/Champion gate would not surface these; they need a carrier (family Hero) or a
conscious 'formula-only ghost' designation.

**P3-c. Pet equip-slot dangles inherited from SV** (`sandwraith\djel_soul` pet's
`lootFinger1Item2=RingAll_01-08.dbr`, `tigerman\miaomiao_soul` pet's `lootLowerBodyItem5=GreavesCaster_N03.dbr`;
plus keleos' literal `x` disable markers). SV ships the identical dangles; the engine skips them
gracefully (validate_summon_pets upstream-leniency class). Optional hygiene: point at real loot tables.

**P3-d. DB hygiene (SV-inherited dead weight, zero player impact):** 74 Dropbox 'conflicted copy'
duplicate rings, 31 per-family `soultemplate` scaffolds, 7 `_n_`/`_n_soul` duplicate scaffolds, 30
`soul\test\` dev-scratch rings - all byte-inherited from SV 0.98i (identical counts upstream), all
unreferenced. Optionally prune in the build to shave arz size; zero urgency.

### LAW-NOTED (Will's hand-tuning or approved waves; noted, NOT listed as fixable)

- `pharaohshonorguard\pharaohshonorguard_soul`: SV's -13/-15/-18% total-speed downside removed by an
  explicit hand edit (`apply_svc_patches.py` soul spec: 'remove total speed penalty', replaced with a
  movement-only -9% run speed). Deliberate redesign.
- `svc_uber\kallixenia_soul`: the uber redesign intentionally diverges from the SV original
  (which still ships untouched at `abyssalliche\kallixenia_soul_{n,e,l}` and is graded separately).
- 5 granted-skill reassignments by the build37 skill_quality wave (corpsemanager lifedrain->Devour,
  theetheralone lifedrain->Leeching Vein, phagia summon->Meritamen, palai bolt->Summon Long-Nu,
  xeiwang absorb->Summon Xei-Wang) - Will-approved identity-true moves, roster-locked by the
  fail-loud diversity gate.
- No finding in this audit touches Will's hand-tuned Occult or Hunting mastery content; every proposed
  fix edits soul/pet/icon records only.

## 6. Graded table - every gradeable soul (708 families)

Grouped DEFICIENT first, then MINOR-GAP, then GOOD (alphabetical within group). `SV` = has an SV 0.98i
original (exact path or basename match); `mod-new` souls are judged on the amgoz1 bar + internal
consistency. `Tiers` lists the ring variants found. Family key = `<type-dir>\<soul basename>`.

| Soul family | Name (shipped Text) | Tiers | SV | Grade | Evidence |
|---|---|---|---|---|---|
| `svc_uber\crowboar_soul` | {^F}Crowboar Soul | e/l/n | mod-new | DEFICIENT | !AUGMENT-LEVEL-TIER-INVERSION:n/e/l=[1.0, 2.0, 1.0]; E/L tiers show the N-tier icon |
| `svc_uber\onyxspine_soul` | {^F}Onyxspine the Dismemberer Soul | e/l/n | mod-new | DEFICIENT | !AUGMENT-LEVEL-TIER-INVERSION:n/e/l=[1.0, 2.0, 1.0]; E/L tiers show the N-tier icon |
| `svc_uber\steamcrawler_soul` | {^F}Steamcrawler Soul | e/l/n | mod-new | DEFICIENT | !AUGMENT-LEVEL-TIER-INVERSION:n/e/l=[1.0, 2.0, 1.0]; E/L tiers show the N-tier icon |
| `spider\bloodtip_soul` | {^F}Bloodtip the Devourer Soul | e/l/n | SV | DEFICIENT | !GRANT-LEVEL-TIER-INVERSION:itemSkillLevel(bloodtip_devour) n/e/l=[5,1,9] - Epic weaker than Normal (SV-inherited oversight; round-2 fix 5/7/9) |
| `vulture\gustleech_soul` | {^F}Gustleech Soul | e/l/n | SV | DEFICIENT | !GRANT-LEVEL-TIER-INVERSION:itemSkillLevel(leechstrike_soul) n/e/l=[10,4,7] - Epic+Legendary weaker than Normal (SV-inherited oversight; round-2 fix 10/12/14) |
| `\darksatyrelitearcher_soul` | {^F}Dark Satyr Elite Skirmisher Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\darksatyrelitepeltast_soul` | {^F}Dark Satyr Elite Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\darksatyrelitesoldier_soul` | {^F}Dark Satyr Elite Warrior Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\darksatyrfiremagi_soul` | {^F}Dark Satyr Fire Magi Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\darksatyrpeltast_soul` | {^F}Dark Satyr Peltast Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\darksatyrpillager_soul` | {^F}Dark Satyr Pillager Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\darksatyrravager_soul` | {^F}Dark Satyr Ravager Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\darksatyrshaman_soul` | {^F}Dark Satyr Shaman Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\darksatyrspiritcaller_soul` | {^F}Dark Satyr Spirit Caller Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\darksatyrveteranpeltast_soul` | {^F}Dark Satyr Veteran Peltast Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\desecrateddeadsoldier_soul` | {^F}Desecrated Dead Soldier Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\exhumeddeadsoldier_soul` | {^F}Exhumed Dead Soldier Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\mountainsatyrelitepeltast_soul` | {^F}Mountain Satyr Elite Peltast Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\mountainsatyrelitesoldier_soul` | {^F}Mountain Satyr Elite Warrior Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\mountainsatyrpeltast_soul` | {^F}Mountain Satyr Peltast Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\mountainsatyrpillager_soul` | {^F}Mountain Satyr Pillager Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\mountainsatyrravager_soul` | {^F}Mountain Satyr Ravager Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\mountainsatyrsoldier_soul` | {^F}Mountain Satyr Warrior Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\mountainsatyrveteranpeltast_soul` | {^F}Mountain Satyr Veteran Peltast Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\mountainsatyrveteransoldier_soul` | {^F}Mountain Satyr Veteran Warrior Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\satyrarcher_soul` | {^F}Satyr Skirmisher Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\satyrchampion_soul` | {^F}Satyr Brute Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\satyrelitepeltast_soul` | {^F}Satyr Elite Peltast Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\satyrguardian_soul` | {^F}Satyr Guardian Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\satyrhuntermounted_soul` | {^F}Satyr Boar Rider Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\satyrmagi_soul` | {^F}Satyr Magi Soul | e/l/n | SV | MINOR-GAP | no finger2 dropper (other refs exist) |
| `\satyrpawn_soul` | {^F}Satyr Scout Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\satyrpeltast_soul` | {^F}Satyr Peltast Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\satyrpillager_soul` | {^F}Satyr Pillager Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\satyrshaman_soul` | {^F}Satyr Shaman Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\satyrsoldier_soul` | {^F}Satyr Warrior Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\satyrspiritcaller_soul` | {^F}Satyr Spirit Caller Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\satyrveteranarcher_soul` | {^F}Satyr Veteran Skirmisher Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `\satyrveteranpeltast_soul` | {^F}Satyr Veteran Peltast Soul | e/l/n | SV | MINOR-GAP | no finger2 dropper (other refs exist) |
| `\satyrveteransoldier_soul` | {^F}Satyr Veteran Warrior Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `antlion\frostmandible_soul` | {^F}Ice Mandible Soul | e/l/n | SV | MINOR-GAP | no finger2 dropper (other refs exist) |
| `automatoi\pygmalion_soul` | {^F}Pygmalion Replicator Soul | e/l/n | SV | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons) |
| `bat\cavebat_soul` | {^F}Cave Bat Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `bat\giganticbat_soul` | {^F}Gigantic Bat Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `beetle\firebeetle_soul` | {^F}Fire Beetle Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `boar\ravenousboar_soul` | {^F}Ravenous Boar Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `bonescourge\soulfeeder_soul` | {^F}Soul-feeder Soul | e/l/n | SV | MINOR-GAP | summoned pet kit smaller than SV original |
| `carrionbird\carrionlord_soul` | {^F}Carrion Lord Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `carrionbird\plaguebird_soul` | {^F}Plague Bird Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `carrionbird\plaguelord_soul` | {^F}Plague Lord Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `dragonian\dragonianfiretalon_soul` | {^F}Dragonian Firetalon Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `empusa\alcestis_soul` | {^F}Empusa Soul Carver Soul | e/l/n | SV | MINOR-GAP | no finger2 dropper (other refs exist) |
| `empusa\frostreaver_soul` | {^F}Empusa Frost Reaver Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `empusa\pyromancer_soul` | {^F}Empusa Pyromancer Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `empusa\soulcarver_soul` | {^F}Empusa Soul Carver Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `empusa\venomancer_soul` | {^F}Empusa Venomancer Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `gorgon\gorgonarcher_soul` | {^F}Gorgon Archer Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `gorgon\gorgonguard_soul` | {^F}Gorgon Guard Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `harpy\brushharpycrone_soul` | {^F}Brush Harpy Crone Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `harpy\brushharpyhag_soul` | {^F}Brush Harpy Hag Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `harpy\brushharpywitch_soul` | {^F}Brush Harpy Witch Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `harpy\cragharpycrone_soul` | {^F}Crag Harpy Crone Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `harpy\cragharpyhag_soul` | {^F}Crag Harpy Hag Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `harpy\rockharpycrone_soul` | {^F}Rock Harpy Crone Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `harpy\rockharpyhag_soul` | {^F}Rock Harpy Hag Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `harpy\rockharpywitch_soul` | {^F}Rock Harpy Witch Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `human\phagia_soul` | {^F}Meritamen the Shadowcaller Soul | e/l/n | SV | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons); grant reassigned by skill_quality wave (law): summon_phagia.dbr -> summon_meritamen.dbr |
| `ichthian\coastalichthianmyrmidon_soul` | {^F}Coastal Ichthian Myrmidon Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `ichthian\coastalichthianshaman_soul` | {^F}Coastal Ichthian Shaman Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `ichthian\fenichthianmurklord_soul` | {^F}Fen Ichthian Murk Lord Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `ichthian\fenichthianmyrmidon_soul` | {^F}Fen Ichthian Myrmidon Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `ichthian\fenichthianshaman_soul` | {^F}Fen Ichthian Shaman Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `keres\aphiastas_soul` | {^F}Aphiastas Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `maenad\maenadalchemist_soul` | {^F}Maenad Alchemist Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `maenad\maenadrogue_soul` | {^F}Maenad Rogue Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `maenad\maenadscout_soul` | {^F}Maenad Vanguard Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `maenad\maenadshadowblade_soul` | {^F}Maenad Shadowblade Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `maenad\maenadstalker_soul` | {^F}Maenad Stalker Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `maenad\maenadtracker_soul` | {^F}Maenad Tracker Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `minotaur\sarpedon_soul` | {^F}War-King Sarpedon Soul | e/l/n | SV | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons) |
| `orthus\orthus_soul` | {^F}Orthus Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `sandwraith\djel_soul` | {^F}Djel Firesprite Soul | e/l/n | SV | MINOR-GAP | pet equip slot dangles (SV ships the same dangle; engine skips) |
| `sepulchralwyrm\eaterofdays_soul` | {^F}Eater of Days Soul | e/l/n | SV | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons) |
| `sepulchralwyrm\palai_soul` | {^F}Long Nu the Flame Mother Soul | e/l/n | SV | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons); grant reassigned by skill_quality wave (law): palai_bigbolt.dbr -> summon_longnu.dbr |
| `skeleton\awakeneddeadarcher_soul` | {^F}Awakened Dead Archer Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `skeleton\desecrateddeadarcher_soul` | {^F}Desecrated Dead Archer Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `skeleton\exhumeddeadarcher_soul` | {^F}Exhumed Dead Archer Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `skeleton\xeiwang_soul` | {^F}Xeiwang Flame of Hatred Soul | e/l/n | SV | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons); grant reassigned by skill_quality wave (law): xeiwang_absorb.dbr -> summon_xeiwang.dbr |
| `svc_uber\blinkfang_soul` | {^F}Spider Brooding Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\blood_toxeus_soul` | {^F}Toxeus the Murderer, Devourer of Blood Soul | e/l/n | mod-new | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons) |
| `svc_uber\bloodrunner_soul` | {^F}Blood Hurdler Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\boss_charon_soul` | {^F}Charon Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\boss_coldworm50_soul` | {^F}Cold Worm Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\broodmother_soul` | {^F}Broodmother Soul | e/l/n | mod-new | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons) |
| `svc_uber\dagon_soul` | {^F}Dagon Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\droolbog_soul` | {^F}Chief Bullfrog Droolbog Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\enslaver_soul` | {^F}Toxeus the Murderer, Enslaver of Souls Soul | e/l/n | mod-new | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons) |
| `svc_uber\ferryman_soul` | {^F}Soul of the Unferried | e/l/n | mod-new | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons) |
| `svc_uber\frost_soul` | {^F}Ice Mandible Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\glittertail_soul` | {^F}Glittertail the Conjurer Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\hadesmarshal_soul` | {^F}Marshal's Command | e/l/n | mod-new | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons) |
| `svc_uber\hero_junshan_soul` | {^F}Jun Shan, Warrior-Monk Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\kallixenia_soul` | {^F}Kallixenia ~ Liche Queen Soul | e/l/n | SV | MINOR-GAP | note: LAW: uber redesign; SV original ships untouched at abyssalliche\kallixenia_soul_{n,e,l} |
| `svc_uber\kazept_soul` | {^F}Kazept of the Flail Star Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\koroush_soul` | {^F}Koroush, Lurker of Samarkand Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\kravmoloch_soul` | {^F}Kravmoloch, Keeper of the Wheel Soul | e/l/n | mod-new | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons) |
| `svc_uber\kydoimos_soul` | {^F}Kydoimos Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\leinth_soul` | {^F}Leinth Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\mnemophage_soul` | {^F}Soul of the Mnemophage | e/l/n | mod-new | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons) |
| `svc_uber\mountainblade_soul` | {^F}Huo-ren, the Mountainblade Soul | e/l/n | mod-new | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons) |
| `svc_uber\murderbunny_soul` | {^F}Murder Bunny Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\n_emgiec_soul` | {^F}Rong Saberbane the Hacker Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\n_mega_soul` | {^F}Rong Saberbane the Boss Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\n_vio_soul` | {^F}Rong Saberbane the Wizard Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\neferkha_soul` | {^F}Neferkha, the Rimebound Pharaoh Soul | e/l/n | mod-new | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons) |
| `svc_uber\nekhekh_soul` | {^F}Nekhekh Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\nkac_soul` | {^F}Nkac Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\phlebas_soul` | {^F}Phlebas the Tidebane Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\possessedboar_soul` | {^F}Possessedboar Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\quest_celtheano_soul` | {^F}Celtheano Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\rebil_soul` | {^F}Rebil Witfury Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\shadowhero_soul` | {^F}Phantom Weaver Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\shockooth_soul` | {^F}Shocktooth the Thunderbringer Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\sp_hades_soul` | {^F}Hades Soul (SP) | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\sp_toxeus_soul` | {^F}Toxeus the Murderer Soul (SP) | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\tantalus_soul` | {^F}Soul of the Insatiable | e/l/n | mod-new | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons) |
| `svc_uber\trachius_soul` | {^F}Trachius Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\uber_soul` | {^F}Waeizhi Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\ubericeraptor_soul` | {^F}Ice Raptor ~ Brood Mother Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\um_feth_soul` | {^F}Feth Thundertail Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\um_prox_soul` | {^F}Ancient Limos, Soul Stealer Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\um_tombguardian_soul` | {^F}Tomb Guardian ~ Hound of Anubis Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon; drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `svc_uber\vileslash_soul` | {^F}Vileslash the Uncatchable Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\voranthys_soul` | {^F}Voranthys the Sepulchral Soul | e/l/n | mod-new | MINOR-GAP | summon skill shows nymph icon (fix in-flight: feat/b40-soul-icons) |
| `svc_uber\xhero_nightsmistress_soul` | {^F}Alcestis Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\xix_soul` | {^F}Xix the Thunderclaw Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_arthur_soul` | {^F}Arthur Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_ben_soul` | {^F}Ben Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_chooch_soul` | {^F}Chooch Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_cory_soul` | {^F}Cory Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_dave_soul` | {^F}Dave Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_david_soul` | {^F}David Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_frazier_soul` | {^F}Frazier Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_josh_soul` | {^F}Josh Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_morgan_soul` | {^F}Morgan Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_nate_soul` | {^F}Nate Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_parnell_soul` | {^F}Parnell Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_scott_soul` | {^F}Scott Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_shawn_soul` | {^F}Shawn Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_tildavtilde_soul` | {^F}~V~ Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `svc_uber\z_tom_soul` | {^F}Tom Soul | e/l/n | mod-new | MINOR-GAP | E/L tiers show the N-tier icon |
| `tigerman\miaomiao_soul` | {^F}Miao Miao Soul | e/l/n | SV | MINOR-GAP | pet equip slot dangles (SV ships the same dangle; engine skips) |
| `vulture\infectedvulture_soul` | {^F}Infected Vulture Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `vulture\vulturelord_soul` | {^F}Vulture Lord Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `yeti\hulkingyeti_soul` | {^F}Hulking Yeti Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `yeti\yeti_soul` | {^F}Yeti Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `zombie\coldburnedcorpse_soul` | {^F}Coldburned Corpse Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `zombie\festeringzombie_soul` | {^F}Festering Zombie Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `zombie\noxiouszombie_soul` | {^F}Noxious Zombie Soul | e/l/n | SV | MINOR-GAP | drop-gated: only Common/Champion monsters carry it (design gate zeroes them) |
| `zombie\oythroneus_soul` | {^F}Orythroneus the Plaguebringer Soul | e/l/n | SV | MINOR-GAP | no finger2 dropper (other refs exist) |
| `\awakeneddeadsoldier_soul` | {^F}Awakened Dead Soldier Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `\satyrfiremagi_soul` | {^F}Satyr Fire Magi Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `abyssalliche\arene_soul` | {^F}Arene, Priestess of the Dead Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `abyssalliche\chromaticliche_soul` | {^F}Chromatic Liche Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `abyssalliche\kallixenia_soul` | {^F}Kallixenia ~ Liche Queen Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `anouran\gleekthenimble_soul` | {^F}Chief Bullfrog Gleek the Nimble Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `anouran\longbellow_soul` | {^F}Chief Bullfrog Longbellow Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `anouran\polywok_soul` | {^F}Chief Shaman Polywok Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `anouran\quak_soul` | {^F}Chief Bullfrog Quak the Cannibal Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `anouran\schlilsh_soul` | {^F}Tribal Shaman Schlilsh Toadskin Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `anouran\woodear_soul` | {^F}Tribal Shaman Wood-Ear Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `anteok\elatos_soul` | {^F}Elatos Lord of the Greenwood Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `anteok\kartones_soul` | {^F}Kartones, Watcher of the Forest Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `anteok\myrto_soul` | {^F}Myrto of the Shadow Grove Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `anteok\surryln_soul` | {^F}Surryln the Belligerent Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `antlion\camelbane_soul` | {^F}Camelbane Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `antlion\slimebrood_soul` | {^F}Slimebrood Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `arachnos\arachne_soul` | {^F}Arachne Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `arachnos\bloodfang_soul` | {^F}Bloodfang Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `arachnos\ikzkat_soul` | {^F}Ik'zkat'tni Frostspinner Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `arachnos\ishtilnintheye_soul` | {^F}Ishtil Nintheye Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `arachnos\morth_soul` | {^F}Morth'tik the Crimson Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `arachnos\raxildarkspine_soul` | {^F}Raxil Darkspine Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `arachnos\runelordkkinzir_soul` | {^F}Runelord K'kin'zir Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `arachnos\scorix_soul` | {^F}Scorix Grimchitin Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `arachnos\tiknat_soul` | {^F}Tik'nat the Dreamspinner Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `arachnos\turgoxmancather_soul` | {^F}Turgox Mancatcher Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `arachnos\webshot_soul` | {^F}S'ckti'nkt Webshot Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `arachnos\xaktiletherweb_soul` | {^F}Xaktil Etherweb Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `arachnos\zkarflamespinner_soul` | {^F}Z'kar Flamespinner Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ascacophus\bramblethorn_soul` | {^F}Bramblehorn Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ascacophus\deadtrunk_soul` | {^F}Deathtrunk Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ascacophus\gatekeeper_soul` | {^F}Ascacophus ~ Gate Keeper Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ascacophus\strongbark_soul` | {^F}Strongbark Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `automatoi\cadmus_soul` | {^F}Cadmus the Golem King Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `automatoi\hesperos_soul` | {^F}Hesperos the Flameforged Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `automatoi\talos_soul` | {^F}Talos Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `automatoi\tatos_soul` | {^F}Toitos the Coldplated Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `bandari\bandari_soul` | {^F}Bandari Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `bat\astralwing_soul` | {^F}Astralwing Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `bat\blackbite_soul` | {^F}Black Bite Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `bat\blastfang_soul` | {^F}Blast Fang Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `bat\elephantsnatcher_soul` | {^F}Elephantsnatcher Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `bat\goatsucker_soul` | {^F}Goat Sucker Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `bat\leatherwing_soul` | {^F}Leather Wing Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `beetle\blackshell_soul` | {^F}Blackshell Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `beetle\grimshell_soul` | {^F}Grimshell Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `beetle\novashell_soul` | {^F}Novashell Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `beetle\plagueshell_soul` | {^F}Plagueshell Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boar\adonisbane_soul` | {^F}Adonis' Bane Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boar\calydonianboar_soul` | {^F}Calydonian Boar Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boar\coldtusk_soul` | {^F}Coldtusk Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boar\duskyboar_soul` | {^F}Dusky Boar Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boar\erymanthianboar_soul` | {^F}Erymanthian Boar Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boar\nemeanboar_soul` | {^F}Nemean Boar Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boar\possesedboar_soul` | {^F}Possessed Boar Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boar\snowhoof_soul` | {^F}Snowhoof Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boar\sow_soul` | {^F}Crommyonian Sow Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boar\stygianboar_soul` | {^F}Stygian Boar Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boarman\cepharis_soul` | {^F}Cepharis Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boarman\kratosbristleback_soul` | {^F}Kratos Bristleback Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boarman\marnosrockbiter_soul` | {^F}Marnos Rockbiter Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boarman\otimosstonecrusher_soul` | {^F}Otimos Stonecrusher Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `boarman\roksosbonebreaker_soul` | {^F}Roksos Bonebreaker Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `bogdweller\chillbranch_soul` | {^F}Chillbranch Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `bogdweller\darkmarsh_soul` | {^F}Darkmarsh Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `bogdweller\emberoak_soul` | {^F}Emberoak Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `bogdweller\thelurker_soul` | {^F}The Lurker Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `bonescourge\lash_soul` | {^F}Lash Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `bonescourge\stygianreaver_soul` | {^F}Stygian Reaver Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `bonescourge\theflayer_soul` | {^F}The Flayer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `carrionbird\birdofsorrow_soul` | {^F}Bird of Sorrow Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `carrionbird\bloodwing_soul` | {^F}Blood Wing Soul | -/e/l/n | SV | GOOD | clean on all 6 axes |
| `carrionbird\carrioncrow_soul` | {^F}Carrion Crow Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `carrionbird\childsnatcher_soul` | {^F}Child Snatcher Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `carrionbird\cindercrow_soul` | {^F}Cinder Crow Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `carrionbird\direflock_soul` | {^F}Dire Flock Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `carrionbird\mutabeak_soul` | {^F}Mutabeak Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `carrionbird\plaguefeast_soul` | {^F}Plague Feast Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `carrionbird\stormbird_soul` | {^F}Storm Crow Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `centaur\keron_soul` | {^F}Keron Oakhoof Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `centaur\mulgorflamespear_soul` | {^F}Mulgor Flamespear Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `centaur\nessus_soul` | {^F}Nessus Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `centaur\panos_soul` | {^F}Panos Lord of the Briarwood Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `centaur\seikios_soul` | {^F}Seikios Briskshot Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `centaur\sergoslongstride_soul` | {^F}Sergos Longstride Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `centaur\sildorbarbnet_soul` | {^F}Sildor Barb Net Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `cerberus\cerberus_soul` | {^F}Cerberus Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `charon\charon_soul` | {^F}Charon Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `chimera\chimera_soul` | {^F}Chimera Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `cryptworm\coldcreep_soul` | {^F}Coldcreep Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `cryptworm\flarecrawler_soul` | {^F}Flarecrawler Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `cryptworm\vilerotter_soul` | {^F}Vilerotter Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `cryptworm\whitewidow_soul` | {^F}White Widow Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `cyclops\brontes_soul` | {^F}Brontes Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `cyclops\clytius_soul` | {^F}Clytius Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `cyclops\halimedes_soul` | {^F}Halimedes Elder Savage Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `cyclops\polyphemus_soul` | {^F}Polyphemus Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `cyclops\steropes_soul` | {^F}Steropes Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `demonbull\yaoguai_soul` | {^F}Yaoguai Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `djinn\adarathelovely_soul` | {^F}Adara the Lovely Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `djinn\bloodsistersafiya_soul` | {^F}Bloodsister Safiya Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `djinn\bloodsistersagira_soul` | {^F}Bloodsister Sagira Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `djinn\kamala_soul` | {^F}Kamala the Pale Sister Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `djinn\kenti_soul` | {^F}Kenti the Defiler Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `djinn\leng_soul` | {^F}Leng-Chuxi Dark Djinn Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `dragonian\bloodskinner_soul` | {^F}Bloodskinner Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `dragonian\mukesha_soul` | {^F}Mukesha the Grim Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `dragonian\rockskin_soul` | {^F}Narok the Rockskin Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `dragonian\sargoth_soul` | {^F}Sargoth Manbane Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `dragonian\tarthon_soul` | {^F}Tarthon Na'Arak Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `dragonian\vort_soul` | {^F}Vort the Red Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `dragonian\wasing_soul` | {^F}Wisang Deathdealer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `dragonliche\dragonliche_soul` | {^F}Dragon Liche Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `dragonliche\permean_soul` | {^F}Permian Extinguisher Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `duneraider\ammet_soul` | {^F}Ammet Flamestrider Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `duneraider\badruthemad_soul` | {^F}Badru the Mad Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `duneraider\hazur_soul` | {^F}Hazur, Phantom of the Wastes Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `duneraider\iznu_soul` | {^F}Iznu Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `duneraider\morloc_soul` | {^F}Morloc the Darkblade Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `duneraider\najja_soul` | {^F}Najja the Parched Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `duneraider\satefdunefrost_soul` | {^F}Satef Dunefrost Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `duneraider\thefacelessone_soul` | {^F}The Faceless One Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `duneraider\udje_soul` | {^F}Udje Flame of the Desert Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `elemental\sentinel_soul` | {^F}Sentinel of Ruin Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `elemental\skinmelter_soul` | {^F}Skinmelter Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `empusa\canace_soul` | {^F}Canace the Serpent Queen Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `empusa\coronis_soul` | {^F}Coronis Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `empusa\feira_soul` | {^F}Feiratixia the Inferno Queen Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `empusa\helike_soul` | {^F}Helike Dark Temptress Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `empusa\lenyxia_soul` | {^F}Lenyxia, Blind Siren of Styx Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `empusa\metriche_soul` | {^F}Metriche Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `empusa\nightmistress_soul` | {^F}The Night Mistress Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `empusa\proseia_soul` | {^F}Proseia ~ Daemon Captain Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `empusa\thyia_soul` | {^F}Thyia of the Stygian Frosts Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `empusa\viluktia_soul` | {^F}Viluktia, Stygian Succubus Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `epiales\bthokite_soul` | {^F}Bth'okite Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `epiales\kiakes_soul` | {^F}Ki'Akes Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `epiales\vaekas_soul` | {^F}Va'ekas Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `epiales\voidlash_soul` | {^F}Voidlash Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `eurynomus\corpsemanager_soul` | {^F}Corpse Manager Soul | e/l/n | SV | GOOD | grant reassigned by skill_quality wave (law): lifedrain.dbr -> bloodtip_devour.dbr |
| `eurynomus\frostdweller_soul` | {^F}Frostdweller Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `eurynomus\legion_soul` | {^F}Legion Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `eurynomus\merenre_soul` | {^F}Merenre the Hidden Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `eurynomus\nyx_soul` | {^F}Child of Nyx Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `eurynomus\pandarus_soul` | {^F}Pandarus Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `eurynomus\soulstrangler_soul` | {^F}Soulstrangler Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `eurynomus\stillborn_soul` | {^F}The Stillborn Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `eurynomus\whitestalker_soul` | {^F}The White Stalker Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `formicid\generalptchkkath_soul` | {^F}General Ptch'k'k'ath the Manslayer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `formicid\generalyrrtik_soul` | {^F}General Yrrt'ik Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `formicid\kika_soul` | {^F}General Ki'irrt'ka Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `formicid\queenchkaatrh_soul` | {^F}Queen Ch'kaatrh Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `formicid\queenchkra_soul` | {^F}Queen Ch'kra the Dark Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `formicid\queenkkiitr_soul` | {^F}Queen K'kiitr Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `formicid\queentkhekt_soul` | {^F}Queen Tk'Hetk Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `formicid\queenychtsskl_soul` | {^F}Queen Ycht'ssk'l Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `furies\alecto_soul` | {^F}Alecto the Unceasing Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `furies\athenos_soul` | {^F}Athenos the Nimble Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `furies\damperos_soul` | {^F}Damperos Bloodflight Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `furies\megaera_soul` | {^F}Megaera the Grudging Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `furies\rustsnarl_soul` | {^F}Rustsnarl Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `furies\tisiphone_soul` | {^F}Tisiphone the Avenger Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ghost\hodesugo_soul` | {^F}Hodesugo the Fallen Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ghost\hydromancer_soul` | {^F}Shui-Zhu the Hydromancer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ghost\spectramancer_soul` | {^F}The Spectramancer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ghost\theetheralone_soul` | {^F}The Etheral One Soul | e/l/n | SV | GOOD | grant reassigned by skill_quality wave (law): lifedrain.dbr -> syrinx_chainleech.dbr |
| `giantturtle\oldsnapper_soul` | {^F}Old Snapper Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `giantturtle\roughneck_soul` | {^F}Roughneck Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `giantturtle\stormtide_soul` | {^F}Stormtide Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gigantes\antaeus_soul` | {^F}Antaeus Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gigantes\ephialtes_soul` | {^F}Ephialtes Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gigantes\koios_soul` | {^F}Koios Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gigantes\polybotes_soul` | {^F}Polybotes Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gigantes\wardenofsouls_soul` | {^F}Warden of Souls Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gorgon\aquardia_soul` | {^F}Aquardia the Coral Queen Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gorgon\cenobia_soul` | {^F}Cenobia Queen of Snakes Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gorgon\euryale_soul` | {^F}Euryale Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gorgon\gorgonslayer_soul` | {^F}Gorgon Slayer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gorgon\iolanthe_soul` | {^F}Iolanthe Viper of Hellas Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gorgon\kalieas_soul` | {^F}Kaliyas the Mystic Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gorgon\kaublasia_soul` | {^F}Kaublasia, the Fire Aspect Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gorgon\keleos_soul` | {^F}Keleos the Forktongued Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gorgon\medusa_soul` | {^F}Medusa Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gorgon\neptis_soul` | {^F}Neptis the Snakeborn Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `gorgon\sstheno_soul` | {^F}Stheno Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `graeae\deino_soul` | {^F}Deino Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `graeae\enyo_soul` | {^F}Enyo Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `graeae\pemphredo_soul` | {^F}Pemphredo Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `guardianstatue\colossusofkarnak_soul` | {^F}Colossus of Karnak Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `guardianstatue\fistoframses_soul` | {^F}Fist of Ramses Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `guardianstatue\lichofthevizier_soul` | {^F}Lich of the Vizier Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `guardianstatue\slabskin_soul` | {^F}Slabskin Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `guardianstatue\stonekeeper_soul` | {^F}Stonekeeper Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `hades\hades_soul` | {^F}Hades Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `harpy\aello_soul` | {^F}Aello the Talon of the Storm Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `harpy\celaeno_soul` | {^F}Celaeno the Dark Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `harpy\cragharpywitch_soul` | {^F}Crag Harpy Witch Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `harpy\cyanae_soul` | {^F}Cyanae the Harbinger Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `harpy\letha_soul` | {^F}Letha the Carrion Queen Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `harpy\nicothoe_soul` | {^F}Nicothoe Grimfeather Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `harpy\ocypete_soul` | {^F}Ocypete the Swiftwing Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `harpy\podarce_soul` | {^F}Podarce Reaver of Pelion Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `hydra\hydra_soul` | {^F}Lernean Hydra Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `hydradon\carnisaur_soul` | {^F}Carnisaur Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `hydradon\ironskin_soul` | {^F}Ironskin Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `hydradon\longjaw_soul` | {^F}Longjaw Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `hydradon\rottingdevourer_soul` | {^F}The Rotting Devourer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `hydradon\shadefeaster_soul` | {^F}Shade Feaster Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `hydradon\stonehide_soul` | {^F}Stonehide Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `hydradon\vilethroat_soul` | {^F}Vilethroat Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `hyenabeast\bloodhound_soul` | {^F}Bloodhound Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `hyenabeast\coldpaw_soul` | {^F}Coldpaw Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `hyenabeast\sandprowler_soul` | {^F}Sandprowler Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ichthian\behemoth_soul` | {^F}Khojasteh the Behemoth Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ichthian\cenonstormborn_soul` | {^F}Cenon Stormborn Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ichthian\cylismurkweed_soul` | {^F}Cylis Murkweed Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ichthian\dapoyan_soul` | {^F}Dapoyan the Deepstalker Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ichthian\indrajit_soul` | {^F}Indrajit the Tsunami Lord Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ichthian\malnordarktide_soul` | {^F}Malnor Darktide Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ichthian\mehrdadcoralskin_soul` | {^F}Mehrdad Coralskin Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ichthian\melchiorbloodhand_soul` | {^F}Melchior Bloodhand Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ichthian\tidanblacksea_soul` | {^F}Tidan Blacksea Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ichthian\vidja_soul` | {^F}Vidja the Shipwrecker Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `jackalman\akiiki_soul` | {^F}Akiiki the Black Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `jackalman\nefethys_soul` | {^F}Nefethys, Feral Hermit Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `jackalman\pashj_soul` | {^F}Pashj the Infected Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `jackalman\sadiki_soul` | {^F}Sadiki ~ Champion of Anubis Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `jackalman\slobberjaw_soul` | {^F}Slobberjaw Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `jackalman\snaptooth_soul` | {^F}Snaptooth Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `jackalman\suhad_soul` | {^F}Suhad the Sleepweaver Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `jackalman\yazid_soul` | {^F}Yazid the Mystic Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `jackalman\ziak_soul` | {^F}Ziak the Stormchaser Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `junglecreep\haronomi_soul` | {^F}Haronomi, Spirit of Death Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `junglecreep\shodema_soul` | {^F}Shodema, Spirit of Life Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `junglecreep\speckledjim_soul` | {^F}Speckled Jim Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `karkinos\barnacle_soul` | {^F}Barnacle Claw Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `karkinos\deeptresher_soul` | {^F}Deeptresher Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `karkinos\gargantuankarkinos_soul` | {^F}Gargantuan Karkinos Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `karkinos\pthirus_soul` | {^F}Pthirus Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `karkinos\pubos_soul` | {^F}Pubos Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `karkinos\seawrack_soul` | {^F}Seawrack Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `karkinos\spinebreaker_soul` | {^F}Spinebreaker Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `keres\akhlys_soul` | {^F}Akhlys Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `keres\anaplekte_soul` | {^F}Anaplekte Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `keres\lycantes_soul` | {^F}Lycantes Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `keres\meglograi_soul` | {^F}Meglograi the Hag Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `keres\nosos_soul` | {^F}Nosos Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `keres\tempia_soul` | {^F}Tempia Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `lamia\damaris_soul` | {^F}Damaris the Cruel Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `lamia\dayria_soul` | {^F}Dayria the Emerald Watcher Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `lamia\erebenea_soul` | {^F}Erebenea the Bloodletter Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `lamia\eritaina_soul` | {^F}Eritaina the Stormprowler Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `lamia\hilaera_soul` | {^F}Hilaera Stonerunner Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `lamia\vanya_soul` | {^F}Vanya Darkheart Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `limos\ancientlimoslifeater_soul` | {^F}Ancient Limos Life Eater Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `limos\darkhellion_soul` | {^F}Dark Hellion Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `limos\flayerofsouls_soul` | {^F}Flayer of Souls Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `limos\frozenhorror_soul` | {^F}The Frozen Horror Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `limos\inemios_soul` | {^F}Inemios the Manafeaster Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `limos\limoslifeater_soul` | {^F}Limos Lifeeater Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `limos\sybaris_soul` | {^F}Sybaris Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `limos\thefiend_soul` | {^F}The Fiend Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `limos\venemurax_soul` | {^F}Venemurax Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `lostsoul\aberkios_soul` | {^F}Aberkios of the Ashes Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `lostsoul\daeros_soul` | {^F}Dearos Elemental Disciple Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `lostsoul\kingaegimius_soul` | {^F}King Aegimius Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `lostsoul\kingdorus_soul` | {^F}King Dorus Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `lostsoul\nikias_soul` | {^F}Nikias Betrayer of Sparta Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `lostsoul\pedaeus_soul` | {^F}Pedaeus the Unwary Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `lostsoul\queenalkiste_soul` | {^F}Queen Alkiste Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `lostsoul\tyrnaios_soul` | {^F}Tyrnaios, Haunting King of Cyprus Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `machae\aorg_soul` | {^F}Warlord Aorg Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `machae\dysnomion_soul` | {^F}Dysnomion Machae High General Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `machae\hadronicus_soul` | {^F}Hadronicus the Guardian Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `machae\impulsos_soul` | {^F}Impulsos, Legendary Marksman Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `machae\javaras_soul` | {^F}Javaras the Manabane Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `machae\kanatos_soul` | {^F}Kanatos Frostreaver Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `machae\karnahk_soul` | {^F}Sentinel Kar-Nahk Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `machae\korlhrut_soul` | {^F}Envoy Kor-Lhrut Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `machae\makaria_soul` | {^F}Makaria Machae High General Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `machae\mordanokath_soul` | {^F}Mordanokath Daemonic Assasin Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `machae\nokhai_soul` | {^F}Sentinel Nok-hai Guardian of the Necklace Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `machae\trophonios_soul` | {^F}Trophonios Machae High General Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\alethadarkclaw_soul` | {^F}Aletha Darkclaw Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\amynta_soul` | {^F}Amynta Nimblebow Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\bloodcrow_soul` | {^F}Bloodcrow Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\calybe_soul` | {^F}Calybe the Wardancer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\cisseis_soul` | {^F}Cisseis Fleetslash Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\cyniga_soul` | {^F}Cyniga Beastslayer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\dimanae_soul` | {^F}Dimanae the Intagliated Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\ecunis_soul` | {^F}High Warden Ecunis Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\ino_soul` | {^F}Ino Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\inoniastrongheart_soul` | {^F}Inonia Strongheart Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\isadora_soul` | {^F}Isadora Sunspear Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\kyrashadowdancer_soul` | {^F}Kyra Shadowdancer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\laneiraflameheart_soul` | {^F}Laneira Flameheart Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\liniashieldbreaker_soul` | {^F}Linia Shieldbreaker Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\liophotia_soul` | {^F}Liophotia Dawn's Flame Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\lyia_soul` | {^F}Lyia Leafsong Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\lysiaspellbreaker_soul` | {^F}Lysia Spellbreaker Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\maenadhuntress_soul` | {^F}Maenad Huntress Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\maenadsorceress_soul` | {^F}Maenad Sorceress Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\maenadvanguard_soul` | {^F}Maenad Vanguard Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\maevewaterguard_soul` | {^F}Maeve Waterguard Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\neneasharpclaw_soul` | {^F}Nenea Sharpclaw Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\nuying_soul` | {^F}Nuying the Mindrender Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\nymeaswiftshot_soul` | {^F}Nymea Swiftshot Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\phas_soul` | {^F}Phasyleia, Dionysos' Favored Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `maenad\vakiya_soul` | {^F}High Priestess Vakiya Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `manticore\manticore_soul` | {^F}Manticore Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `mantid\shadowslash_soul` | {^F}Shadowslash Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `mantid\stingeye_soul` | {^F}Sting Eye Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `melinoe\demastia_soul` | {^F}Demastia Swiftsword Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `melinoe\endeis_soul` | {^F}Blood Mistress Endeis the Unholy Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `melinoe\hekaline_soul` | {^F}Hekaline the Outcast Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `melinoe\insenzia_soul` | {^F}Insenzia the Chaosmind Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `melinoe\leucothea_soul` | {^F}Blood Queen Leucothea Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `melinoe\stygasia_soul` | {^F}Stygasia the Bloodshaper Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `minotaur\kajnotchblade_soul` | {^F}Kaj Notchblade Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `minotaur\minotaurlord_soul` | {^F}Minotaur Lord Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `minotaur\orkushornstrike_soul` | {^F}Orkus Hornstrike Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `mummy\asoris_soul` | {^F}Asoris, Otherworldly Guardian Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `mummy\embalmeddeadadept_soul` | {^F}Embalmed Dead Adept Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `mummy\hanifthecruel_soul` | {^F}Hanif the Cruel Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `mummy\khenti_soul` | {^F}Khenti Frostgrave Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `mummy\menkare_soul` | {^F}Menkare the Dark Pharaoh Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `mummy\nebkemi_soul` | {^F}Neb-kemi Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `mummy\nebtaan_soul` | {^F}Nebtaan The Tomb-king of Egypt Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `mummy\nexeu_soul` | {^F}Nexeu Doomed Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `mummy\radementes_soul` | {^F}Radementes Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `mummy\senusnet_soul` | {^F}Senusnet Mal Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `mummy\tath_soul` | {^F}Tath Stormblight Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `neanderthal\barmanu_soul` | {^F}Barmanu Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `neanderthal\grom_soul` | {^F}Grom Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `neanderthal\regnok_soul` | {^F}Regnok Sky-Fury Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `neanderthal\rong_soul` | {^F}Rong Saberbane Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `neanderthal\sinel_soul` | {^F}Sinel the Frost-King Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `neanderthal\torskullcrusher_soul` | {^F}Tor Skullcrusher Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `neanderthal\vuji_soul` | {^F}Vuji Dark Seer of the Mountains Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `neanderthal\yama_soul` | {^F}Yemi the Beastmaster | e/l/n | SV | GOOD | clean on all 6 axes |
| `neanderthal\yurgrattlebone_soul` | {^F}Yurg Rattlebone Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `nightblossom\nightblossom_soul` | {^F}Nightblossom Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `nightstalker\ikaie_soul` | {^F}Ikaie, Cold of the Night Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `nightstalker\kafele_soul` | {^F}Kafele the Silent Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `nightstalker\minkah_soul` | {^F}Minkah Lord of Fury Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `nightstalker\serafemos_soul` | {^F}Serafemos the Vile | e/l/n | SV | GOOD | clean on all 6 axes |
| `nymph\syrinx_soul` | {^F}Syrinx of the Tainted Meadow Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `odontotyrannus\beast_soul` | {^F}Warbeast Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `odontotyrannus\krog_soul` | {^F}Krog the Toothless Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `odontotyrannus\rockhorn_soul` | {^F}Rockhorn Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `odontotyrannus\terrorofthedark_soul` | {^F}Terror of the Dark Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `orthus\emberteeth_soul` | {^F}Emberteeth Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `orthus\plaguemaw_soul` | {^F}Plaguebreath Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `peng\izuka_soul` | {^F}Izuka Sleepwing Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `peng\tuska_soul` | {^F}Tuska Grimclaw Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `peng\xiao_soul` | {^F}Xiao Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `pharaohshonorguard\pharaohshonorguard_soul` | {^F}Pharaoh's Honor Guard Soul | e/l/n | SV | GOOD | note: LAW (hand-edited in build scripts): [n] LOST-SV-STATS:characterTotalSpeedModifier:-13; note: LAW (hand-edited in build scripts): [e] LOST-SV-STATS:characterTotalSpeedModifier:-15; note: LAW (hand-edited in build scripts): [l] LOST-SV-STATS:characterTotalSpeedModifier:-18 |
| `quillvine\hellflower_soul` | {^F}Hellflower Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `raptor\fluxfang_soul` | {^F}Flux Fang Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `raptor\phyraxus_soul` | {^F}Phyraxus Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `raptor\spawnofchi_soul` | {^F}Spawn of Chi Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ratman\brutus_soul` | {^F}Brutus Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ratman\hiramitzu_soul` | {^F}Hiramitzu the Infector Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ratman\menzus_soul` | {^F}Menzus Bone-Reader Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ratman\nerbilblackbag_soul` | {^F}Nerbil Blackbag Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ratman\spindlefur_soul` | {^F}Spindlefur Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `ratman\wheedletongue_soul` | {^F}Wheedletongue the Magnificent Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `reptillian\annorek_soul` | {^F}Annorek Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `reptillian\barroc_soul` | {^F}Barroc Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `reptillian\drottuk_soul` | {^F}Drottuk Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `reptillian\hetzu_soul` | {^F}Hetzu Guardian of the Nile Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `reptillian\nebwavi_soul` | {^F}Nebwawi Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `reptillian\ssark_soul` | {^F}Ssark Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `saberlion\furyclaw_soul` | {^F}Clawfury Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `sandwing\bloodmistressneith_soul` | {^F}Bloodmistress Neith Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `sandwing\iteneika_soul` | {^F}Itenieka Scourgewing Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `sandwing\naeemah_soul` | {^F}Naeemah Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `sandwing\nathifa_soul` | {^F}Nathifa the Unblemished Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `sandwing\sandqueenmasika_soul` | {^F}Sandqueen Masika Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `sandwraith\adacil_soul` | {^F}Adacil, Dark Acolyte Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `sandwraith\sandwraith_soul` | {^F}Sandwraith Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `sandwraith\sandwraithlord_soul` | {^F}Sand Wraithlord Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `sandwraith\sobaan_soul` | {^F}Sobaan the Sunscorched Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\algosfrostwind_soul` | {^F}Algos Frostwind Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\alosstonefist_soul` | {^F}Alos Stonefist Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\caldordarkbow_soul` | {^F}Caldor Darkbow Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\cibaris_soul` | {^F}Cibaris Plainsrider Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\drusil_soul` | {^F}Drusil Thornweaver Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\durgos_soul` | {^F}Durgos Hawkeye Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\fernos_soul` | {^F}Fernos Charskin Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\karato_soul` | {^F}Karato Stormfist Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\katosbloodblade_soul` | {^F}Katos Bloodblade Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\kornelios_soul` | {^F}Kornelios Lifeweaver Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\nesis_soul` | {^F}Nesis Fleshmender Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\otos_soul` | {^F}Warchief Otos Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\paphos_soul` | {^F}Warchief Paphos Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\petraeus_soul` | {^F}Petraeus Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\priposfirestring_soul` | {^F}Pripos Firestring Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\rakanizeus_soul` | {^F}Rakanizeus Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\rassus_soul` | {^F}Rassus Rockhoof Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\scirtus_soul` | {^F}Scirtus Flamehorn Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `satyr\skiron_soul` | {^F}Skiron Emberwood Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `scarab\scarabaeus_soul` | {^F}Scarabaeus Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `scorpion\frostbite_soul` | {^F}Frostbite Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `scorpion\rocksting_soul` | {^F}Rocksting Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `scorpion\sulphurclaw_soul` | {^F}Sulphurclaw Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `scorpion\voidsting_soul` | {^F}Voidsting Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `scorpos\ancientscorpos_soul` | {^F}Ancient Scorpos Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `scorpos\kaaltspeartail_soul` | {^F}Kaalt Speartail Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `scorpos\nehebkau_soul` | {^F}Nehebkau Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `scorpos\raliel_soul` | {^F}Raliel-nar Ravager of the Dunes Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `scorpos\spikeclaw_soul` | {^F}Spikeclaw Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `shadowstalker\nephitek_soul` | {^F}Nephi'tek the Lasher Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `shadowstalker\sehrtunkah_soul` | {^F}Sehr'tun Kah Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `siegestrider\leveler_soul` | {^F}Leveler Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\aristeus_soul` | {^F}Aristeus, Prince of the Storm Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\boneash_soul` | {^F}Boneash Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\bonefletcher_soul` | {^F}Bonefletcher Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\bonehallow_soul` | {^F}Bonehallow Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\bonelord_soul` | {^F}Bonelord Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\cinderbone_soul` | {^F}Cinder Bone Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\demophon_soul` | {^F}Demophon Fallen King of Athens Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\ereumedes_soul` | {^F}Ereumedes the Howling Storm Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\fenuku_soul` | {^F}Fenuku Martyr of the Crimson Brotherhood Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\frostmarrow_soul` | {^F}Frost Marrow Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\hekos_soul` | {^F}Hekos Bonehunter Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\herkaenis_soul` | {^F}Herkaenis the Impaler Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\jibao_soul` | {^F}Ji Bao the Dishonored Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\leucus_soul` | {^F}Leucus I Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\manetho_soul` | {^F}Manetho, Light of Heliopolis Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\menon_soul` | {^F}Menon, Prince of the Bow Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\nahoth_soul` | {^F}Nahoth the Hellborn Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\nefesiris_soul` | {^F}Nefesiris the Tainted Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\polypas_soul` | {^F}Polypas, Prince of the Blade Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\qian-zi_soul` | {^F}Qian-zi the Bladedancer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\rotbone_soul` | {^F}Rot Bone Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\spinebone_soul` | {^F}Spinebone Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\theophrastos_soul` | {^F}Theophrastos the Plump Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\theron_soul` | {^F}Theron Skullshot Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\toxeus_soul` | {^F}Toxeus the Murderer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\trojax_soul` | {^F}Trojax Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\umayma_soul` | {^F}Umayma Flayed Witch Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\xenokrates_soul` | {^F}Xenokrates of the Shadowblade Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `skeleton\zheng_soul` | {^F}Zheng Stormstaff Soul | -/e/l/n | SV | GOOD | clean on all 6 axes |
| `spider\akumozon_soul` | {^F}Akumozon Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `spider\arachnesshame_soul` | {^F}Arachne's Shame Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `spider\ararat_soul` | {^F}Ararat the Corrupter Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `spider\gardenhorror_soul` | {^F}Garden Horror Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `spider\thebloatedone_soul` | {^F}The Bloated One Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `spider\venombane_soul` | {^F}Venom Bane Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `spider\venophobia_soul` | {^F}Venophobia Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `sprite\gorlab_soul` | {^F}Gorlab the Charred One Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `sprite\rimepuck_soul` | {^F}Rimepuck Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `svc_uber\04_spiritcaller_soul` | {^F}Soul of the Blood Shaman | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\ainex_soul` | {^F}Ainex, Queen of Crows Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\aithon_embercrown_soul` | {^F}Aithon, the Ember-Crowned Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\anapaest_soul` | {^F}Soul of Anapaest the Dishonored | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\bwpriest_soul` | {^F}Blood Cult - High Priest Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\charsi_soul` | {^F}Charsi Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\diadochi_soul` | {^F}Ash of the Funeral Games | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\drowned_king_soul` | {^F}Soul of the Coin-Drowned | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\egypt_monolith_soul` | {^F}Monolith Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\gheed_soul` | {^F}Gheed Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\gitar3_soul` | {^F}Gitar Shrine Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\gorgus_soul` | {^F}Gorgus - Obi One Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\gorrahk_soul` | {^F}Gorrahk the Tombsplitter Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\ilsevar_soul` | {^F}Ilsevar the Ashen Watch Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\jabarto_soul` | {^F}Team Jabarto Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\jiaco_soul` | {^F}jiaco Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\jo7_raptor_soul` | {^F}Jungle Raptor ~ Fleshrender Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\kaets_soul` | {^F}Kaets Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\kir4_soul` | {^F}Kir Trap Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\kreeloo_soul` | {^F}Kreeloo Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\less_soul` | {^F}Less Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\lillued_soul` | {^F}Big Lued Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\lilluedchild_soul` | {^F}Lil' Lued Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\nomnom_soul` | {^F}Plague Feast Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\numberouane_soul` | {^F}Numberouane Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\polisgaoler_soul` | {^F}Soul of the Gaoler | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\rainbowbright_soul` | {^F}General Yrrt'ik Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\sarkoth_soul` | {^F}Sarkoth the Glasswright Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\toxeus_hunt_soul` | {^F}Toxeus the Murderer, the Endless Hunt Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\um_anklesickle_soul` | {^F}Ankle Sickle Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\um_thetrap_soul` | {^F}The Trap Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\vashkarr_soul` | {^F}Vashkarr, Eldest of the Ancients Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\waking_dread_soul` | {^F}Soul of the Waking Dread | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\yerk_soul` | {^F}yerk yerk Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `svc_uber\zilla_soul` | {^F}Zilla Soul | e/l/n | mod-new | GOOD | clean on all 6 axes |
| `telkine\aktaios_soul` | {^F}Aktaios Soul | -/e/l/n | SV | GOOD | clean on all 6 axes |
| `telkine\megalesios_soul` | {^F}Megalesios Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `telkine\ormenos_soul` | {^F}Ormenos Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `terracotta\qinshi_soul` | {^F}Qin Shi's Guardian Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `terracotta\rustedrelic_soul` | {^F}Rust Relic Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `tigerman\jing_soul` | {^F}Jing Arcfang Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `tigerman\myojang_soul` | {^F}Myojang the Voidmage Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `tigerman\nishoba_soul` | {^F}Nishoba Priest of the Mountains Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `tigerman\sajaki_soul` | {^F}Sajaki, Cat of the Seventh Pit Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `tigerman\shaohsin_soul` | {^F}Shao Hsin the Wanderer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `tigerman\shihou_soul` | {^F}Shihou, Fang of Flames Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `tombguardian\foulbeast_soul` | {^F}Tombspawn Foulbeast Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `tombguardian\hesysunebef_soul` | {^F}Hesy-su-neb-ef Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `tombguardian\thetombkeeper_soul` | {^F}The Tombkeeper Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `tombrot\cursedcreeper_soul` | {^F}Curse Creeper Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `tombrot\deathclot_soul` | {^F}Death Clot Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `tombrot\fissureslug_soul` | {^F}Fissure Slug Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `tombrot\spellremnant_soul` | {^F}Spellremnant Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `troglodyte\kondorthemighty_soul` | {^F}Kondor the Mighty Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `troglodyte\kortex_soul` | {^F}Kortex the Forgeborn Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `troglodyte\orokskullcracker_soul` | {^F}Orok Skullcracker Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `troglodyte\thanekaorak_soul` | {^F}Thane Kaorak Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `troglodyte\torak_soul` | {^F}Torak Rageswing Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `troglodyte\uraka_soul` | {^F}Uraka Spellsmiter Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `troglodyte\warraghammerfist_soul` | {^F}Warrag Hammerfist Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `typhon\typhon_soul` | {^F}Typhon Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `typhon\undeadtyphon_soul` | {^F}Undead Typhon Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `vulture\diseasedvulture_soul` | {^F}Diseased Vulture Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `vulture\sandbeak_soul` | {^F}Sandbeak Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `vulture\shadowfeather_soul` | {^F}Shadowfeather Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `vulture\wraithwing_soul` | {^F}Wrathwing Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `wraith\alastor_soul` | {^F}Alastor Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `wraith\dariusdeathwalker_soul` | {^F}Darius Deathwalker Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `wraith\graklosthegraveless_soul` | {^F}Graklos the Graveless Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `wraith\kuwei_soul` | {^F}Kuwei Harbinger of Disease Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `wraith\thrydosdarksoul_soul` | {^F}Thrydos Darksoul Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `wraith\xerkosthebetrayer_soul` | {^F}Xerkos the Betrayer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `yerren\cliffrunner_soul` | {^F}Cliffrunner Clan Battle Master Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `yerren\jayanta_soul` | {^F}Jayanta the Manhunter Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `yerren\mountainstrider_soul` | {^F}Mountainstrider Tribal Elder Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `yerren\swiftstream_soul` | {^F}Swiftstream Chieftain of the Five Clans Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `yerren\wolfbiter_soul` | {^F}Wolfbiter Clan Hunt Master Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `yeti\boulderfoot_soul` | {^F}Boulderfoot Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `yeti\coldshoulder_soul` | {^F}Coldshoulder Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `yeti\gargantuanyeti_soul` | {^F}Gargantuan Yeti Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `zombie\deathwalker_soul` | {^F}Deathwalker Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `zombie\galenos_soul` | {^F}Galenos the Poisoned Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `zombie\hetmun_soul` | {^F}Hetmun, Unfaltering Guardian of Ramses Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `zombie\huang_soul` | {^F}Huang Fay the Unclean Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `zombie\jizhao_soul` | {^F}Jizhao Gearmaster Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `zombie\kemrat_soul` | {^F}Kemrat the Magmawalker Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `zombie\komara_soul` | {^F}Komara, the Life Bane Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `zombie\melalos_soul` | {^F}Melalos Lord of Decay Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `zombie\nkrumah_soul` | {^F}Nkrumah the Enslaved Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `zombie\orythroneus_soul` | {^F}Orythroneus the Plaguebringer Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `zombie\refnat_soul` | {^F}Refnat Soulshot Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `zombie\reshelf_soul` | {^F}Reshelf Undying King of Nubia Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `zombie\rotskin_soul` | {^F}Rotskin Soul | e/l/n | SV | GOOD | clean on all 6 axes |
| `zombie\shuang_soul` | {^F}Shuang Frostdraw Soul | e/l/n | SV | GOOD | clean on all 6 axes |

## 7. Verification record

- Audited arz re-hashed at audit time: md5 `b33c5a447f3a8ca652c14f78d4ad1dd4` == build40 GOLDEN.
- `tools/validate_soul_augments.py <build40 arz>` = **PASS** (0 dangling refs, 0 inactive grants across
  1,390 granted-skill chains) - independently corroborates this audit's zero proc-chain findings.
- `tools/validate_summon_pets.py <build40 arz> <base arz> <SV arz>` = **PASS** ('every mod-authored
  soul-granted summon spawns a complete, renderable, usable pet'); only WARNs are upstream-leniency
  classes plus a benign engine-clamp note on `svc_uber\kaets_soul_{n,e,l}` (itemSkillLevel exceeds the
  1-entry spawnObjects ladder; the engine clamps to the last pet entry).
- This audit ran NO build; it is a pure read of the deployed artifacts (concurrency law respected).

## 8. Appendix - non-graded scaffolding families (enumerated for completeness)

| Category | Families | What they are | SV parity |
|---|---:|---|---|
| WILDCARD | 21 | 'Any X Soul' enchanting-formula reagent wildcards (01/02/03_actN_anysoul, any*herosoul); stat-less by design, referenced by 54 formula reagent slots | byte-inherited from SV |
| TEMPLATE | 31 | per-family `soultemplate.dbr` authoring scaffolds (placeholder tagSoulName) | byte-inherited from SV |
| CONFLICTED-DUP | 74 | Dropbox "(amgoz-qosmio's conflicted copy 2013-08-07)" duplicate rings | identical 74 in SV |
| SV-DUP | 7 | `X_soul_n_`/`_n__e`/`_n__l` and `X_n_soul` duplicate scaffolds beside the real `X_soul_{n,e,l}` (cyclops trio, athenos, 3 vultures) | identical in SV |
| DEV-TEST | 30 | `soul\test\` dev-scratch rings (123 records) | all 123 in SV |

Full family list per category:

- **WILDCARD** (21): `\01_act1_anysoul`, `\01_act2_anysoul`, `\01_act3_anysoul`, `\01_act4_anysoul`, `\02_act1_anysoul`, `\02_act2_anysoul`, `\02_act3_anysoul`, `\02_act4_anysoul`, `\03_act1_anysoul`, `\03_act2_anysoul`, `\03_act3_anysoul`, `\03_act4_anysoul`, `\anycarrionbirdherosoul`, `\anycentaurherosoul`, `\anyharpyherosoul`, `\anymaenadherosoul`, `\anysatyrherosoul`, `\anyscarabherosoul`, `\anysoul`, `\anytroglodyteherosoul`, `melinoe\anysia_soul`

- **TEMPLATE** (31): `\soultemplate`, `arachnos\soultemplate`, `boarman\soultemplate`, `chimera\soultemplate`, `djinn\soultemplate`, `dragonian\soultemplate`, `eurynomus\soultemplate`, `ghost\soultemplate`, `harpy\soultemplate`, `junglecreep\soultemplate`, `karkinos\soultemplate`, `lamia\soultemplate`, `maenad\soultemplate`, `minotaur\soultemplate`, `mummy\soultemplate`, `neanderthal\soultemplate`, `peng\soultemplate`, `raptor\soultemplate`, `ratman\soultemplate`, `satyr\soultemplate`, `scarab\soultemplate`, `scorpion\soultemplate`, `scorpos\soultemplate`, `skeleton\soultemplate`, `telkine\soultemplate`, `tigerman\soultemplate`, `tombrot\soultemplate`, `troglodyte\soultemplate`, `vulture\soultemplate`, `zombie\copy of soultemplate`, `zombie\soultemplate`

- **SV-DUP** (7): `cyclops\brontes_soul_n_`, `cyclops\polyphemus_soul_n_`, `cyclops\steropes_soul_n_`, `furies\athenos_n_soul`, `vulture\diseasedvulture_n_soul`, `vulture\infectedvulture_n_soul`, `vulture\vulturelord_n_soul`

- **DEV-TEST** (30): `test\alethadarkclaw_soul`, `test\amynta_soul`, `test\bloodcrow_soul`, `test\bramblethorn_soul`, `test\deadtrunk_soul`, `test\dimanae_soul`, `test\gatekeeper_soul`, `test\ino_soul`, `test\inoniastrongheart_soul`, `test\isadora_soul`, `test\kyrashadowdancer_soul`, `test\laneiraflameheart_soul`, `test\liniashieldbreaker_soul`, `test\lyia_soul`, `test\lysiaspellbreaker_soul`, `test\maenadalchemist_soul`, `test\maenadhuntress_soul`, `test\maenadrogue_soul`, `test\maenadscout_soul`, `test\maenadshadowblade_soul`, `test\maenadsorceress_soul`, `test\maenadstalker_soul`, `test\maenadtracker_soul`, `test\maenadvanguard_soul`, `test\maevewaterguard_soul`, `test\menon_soul`, `test\neneasharpclaw_soul`, `test\nymeaswiftshot_soul`, `test\strongbark_soul`, `test\vakiya_soul`

- **CONFLICTED-DUP** (74): `djinn\adarathelovely_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `djinn\bloodsistersafiya_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `djinn\bloodsistersagira_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `djinn\kamala_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `djinn\kenti_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `djinn\leng_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `dragonian\bloodskinner_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `dragonian\mukesha_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `dragonian\rockskin_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `dragonian\sargoth_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `dragonian\tarthon_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `dragonian\vort_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `dragonian\wasing_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `dragonliche\dragonliche_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `dragonliche\permean_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `duneraider\ammet_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `duneraider\badruthemad_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `duneraider\hazur_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `duneraider\iznu_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `duneraider\morloc_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `duneraider\najja_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `duneraider\satefdunefrost_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `duneraider\thefacelessone_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `duneraider\udje_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `elemental\skinmelter_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `empusa\alcestis_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `empusa\canace_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `empusa\coronis_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `empusa\feira_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `empusa\helike_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `empusa\lenyxia_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `empusa\metriche_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `empusa\nightmistress_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `empusa\proseia_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `empusa\thyia_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `empusa\viluktia_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `epiales\bthokite_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `epiales\kiakes_soul_e (amgoz-qosmio's conflicted copy 2013-08-07)`, `epiales\kiakes_soul_l (amgoz-qosmio's conflicted copy 2013-08-07)`, `epiales\kiakes_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `epiales\vaekas_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `epiales\voidlash_soul_e (amgoz-qosmio's conflicted copy 2013-08-07)`, `epiales\voidlash_soul_l (amgoz-qosmio's conflicted copy 2013-08-07)`, `epiales\voidlash_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `eurynomus\corpsemanager_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `eurynomus\frostdweller_soul_e (amgoz-qosmio's conflicted copy 2013-08-07)`, `eurynomus\frostdweller_soul_l (amgoz-qosmio's conflicted copy 2013-08-07)`, `eurynomus\frostdweller_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `eurynomus\legion_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `eurynomus\merenre_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `eurynomus\stillborn_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `eurynomus\whitestalker_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `formicid\generalptchkkath_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `formicid\generalyrrtik_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `formicid\kika_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `formicid\queenchkaatrh_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `formicid\queenchkra_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `formicid\queenkkiitr_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `formicid\queentkhekt_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `formicid\queenychtsskl_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `furies\alecto_soul_e (amgoz-qosmio's conflicted copy 2013-08-07)`, `furies\alecto_soul_l (amgoz-qosmio's conflicted copy 2013-08-07)`, `furies\alecto_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `furies\athenos_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `furies\damperos_soul_e (amgoz-qosmio's conflicted copy 2013-08-07)`, `furies\damperos_soul_l (amgoz-qosmio's conflicted copy 2013-08-07)`, `furies\damperos_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `furies\megaera_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `furies\rustsnarl_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `furies\tisiphone_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `ghost\hodesugo_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `ghost\theetheralone_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `giantturtle\stormtide_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`, `gigantes\antaeus_soul_n (amgoz-qosmio's conflicted copy 2013-08-07)`

---
*Produced by the souls-quality audit lane (feat/souls-quality) against build40; evidence JSON +*
*probe scripts in the session scratchpad. Fixes ship in a later integration build per the*
*concurrency plan (no heavy builds in this lane).*
