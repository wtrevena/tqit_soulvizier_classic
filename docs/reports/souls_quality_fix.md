# Souls Quality FIX (feat/souls-quality) - round 1 + round 2 + FIX-WAVE-2

> Fixes for the tier-inversion + icon defects found in `docs/reports/souls_quality_audit.md`
> (full-roster ground-truth audit of the build40 GOLDEN arz, md5 `b33c5a44`). All fixes land in
> ONE registry module `tools/patches/souls_quality.py` (`apply()` + a fail-loud `verify()`), touch
> ONLY soul equipmentring records plus (FIX-WAVE-2) the one tomb-guardian monster loot slot, and
> avoid every LAW namespace (Occult/Hunting/mastery/kallixenia/pharaohshonorguard). No em dashes.
>
> **Round-2 (2026-07-14)** extends round-1 after a vet found the round-0 audit UNDER-reported the
> DEFICIENT set: a roster-wide monotonicity re-scan of the GOLDEN arz found **5** inverted soul
> families, not 3. The 2 extra families (`spider\bloodtip_soul`, `vulture\gustleech_soul`) carry the
> same defect class on `itemSkillLevel` and are now fixed here; `verify()` is widened roster-wide so
> the class cannot recur anywhere.
>
> **FIX-WAVE-2 (2026-07-14, Will directives verbatim: "fix any blatant errors that you detect ...
> fix the crowboar soul's summoned crow bug. fix all the other bugs as well ... the 17 boss-summon
> skills sharing the nymph icon")** adds, all in the same module + gated fail-loud:
> - **D1 RATIFIED:** Will ratified `bloodtip 5/7/9` + `gustleech 10/12/14` "ship as-is" - the round-0
>   WILL-VETO flag is **CLEARED** (the `_SV_INVERSION_FIX` block is kept as the documented historical
>   revert path). See sec 5.
> - **D2 Tomb Guardian orphan-soul retirement** (FIX 5): keep Common, detach + retire the
>   referenced-but-unobtainable `um_tombguardian_soul` cleanly with its tag. See sec 3 + the module.
> - **D3 crowboar summoned-crow bug** (FIX 4): the crow (and 3 same-shape svc_uber siblings) reset
>   every attack because the ring auto-cast its summon on-attack; fix to manual-cast (the Lyia
>   convention). See sec 3.5.
> - **D4 nymph icons:** `feat/b40-soul-icons` (`9db3f5f`) VERIFIED to merge cleanly onto current main
>   (merge-tree, 0 conflicts) -> a REQUIRED member of the integration merge set (sec 5).
> - **D5 blatant-error sweep** of the 155 MINOR-GAP list: classified; every blatant DATA error is the
>   icon class (already fixed here + on the b40 branch); the rest are design decisions / a false
>   positive, left documented (sec 5.5).

## 1. What shipped (the fix set)

One registry module, `tools/patches/souls_quality.py` (REGISTRY position 13, after `boss_skill_fix`,
before `visuals`), with `apply()` + a fail-loud `verify()` hook. It fixes **all 5** tier inversions in
the shipped roster (raise-only, FIX 1+2), the svc_uber per-tier icon law (FIX 3), the **crowboar
summoned-crow controller bug + 3 same-shape siblings** (FIX 4, sec 3.5), and the **Tomb Guardian
orphan-soul retirement** (FIX 5, sec 3), and installs four roster-wide fail-loud regression gates
(monotonicity, icon, no-on-attack-controller, tombguardian-retired).

### FIX 1 (P1) - the 3 mod-generated svc_uber souls: Legendary was WEAKER than Epic

Root cause (audit sec 4a): `create_uber_souls` scales `SOUL_DESIGNS`' base level 1 by the per-tier
`_DIFF_SCALE` (0.6/0.8/1.0) -> raw n/e/l = 0/0/1; then the `_fix_soul_skill_levels` backstop (build36,
B-SOUL-PROC-1) BUMPS level-0 grants to the per-tier default (n->1, e->2) but SKIPS the L ring because
its scaled value was already 1 (>=1). Net: **n/e/l = 1/2/1** - the Legendary ring is strictly worse
than the Epic. Healthy siblings from the same generator (bloodrunner, xix) run 1/2/3.

FIX: raise the L-tier levels to 3 (the bloodrunner/xix Legendary value). We only ever RAISE, so the fix
is order-independent w.r.t. the backstop (which runs AFTER this module in `run_registry_gates` and only
bumps level-0; it leaves our >=1 L ring alone and independently completes n/e = 1/2).

| Soul (record `..._soul_l.dbr`) | Field(s) set to 3 | n/e/l BEFORE -> AFTER |
|---|---|---|
| `svc_uber\crowboar_soul_l` | augmentSkillLevel1, augmentSkillLevel2, **itemSkillLevel** | 1/2/1 -> **1/2/3** (grant Summon Carrion Crow too) |
| `svc_uber\onyxspine_soul_l` | augmentSkillLevel1, augmentSkillLevel2 | 1/2/1 -> **1/2/3** (grant untouched; see below) |
| `svc_uber\steamcrawler_soul_l` | augmentSkillLevel1, augmentSkillLevel2 | 1/2/1 -> **1/2/3** (no grant; correct) |

Will's SKILL PICKS are untouched. Only the tier LEVEL of the existing augments/grant changes.
**Onyxspine grant note (corrects a round-1 report imprecision):** onyxspine's GRANTED skill is
`records\skills\scroll skills\arachnos_venombolt.dbr` (a venom bolt) at itemSkillLevel n/e/l = **3/5/8**
- already monotonic and left untouched. Its chain-lightning is `drxlightningbolt_chainlightning.dbr` =
**augmentSkillName2** (one of the two inverted augments raised above), NOT the grant. (The round-1 report
wrongly called it "Ring of Lightning" and called it the grant; the grant edit set is unchanged and correct.)

### FIX 2 (round-2, P1) - the 2 SV-inherited souls: grant WEAKER at a higher rarity

Both grant a per-level-scaled skill (skillMaxLevel 20) at a LOWER `itemSkillLevel` on the higher-rarity
ring, so a farmed Epic/Legendary is strictly worse than the common Normal. Both are OBTAINABLE Hero
souls (`um_bloodtip_18` / `um_gustleech_28`, `chanceToEquipFinger2=66`). Confirmed real inversions
(the granted skills' per-level arrays scale up, so a lower level = a weaker proc):

| Soul | Grant (per-level skill) | itemSkillLevel n/e/l | leech-min at those levels | Fix (raise-only) |
|---|---|---|---|---|
| `spider\bloodtip_soul` | `soulskills\bloodtip_devour.dbr` (Devour) | 5/**1**/9 | 30/**14**/46 | `_e` 1->7 => **5/7/9** (30/42/46) |
| `vulture\gustleech_soul` | `sv\gustleech\leechstrike_soul.dbr` (Leechstrike) | 10/**4**/**7** | 50/**26**/**38** | `_e` 4->12, `_l` 7->14 => **10/12/14** (50/58/66) |

Raise-only preserves each soul's Normal anchor and its granted-skill NAME; it only lifts the
under-levelled tier(s) above the tier below them. Both targets stay well within skillMaxLevel (20).

**PROVENANCE - flagged for Will (sec 5 WILL VETO).** These two `itemSkillLevel` arrays are
**byte-identical to SV 0.98i** (`upstream/soulvizier_098i`), so fixing them is a deliberate divergence
from SV-original data. They are judged amgoz1 DATA-ENTRY OVERSIGHTS, not intent: every OTHER field on
both rings tiers UPWARD correctly n->e->l (bloodtip characterLife 120/218/318, its own ring leech
20/34/50; gustleech deflect 5/7/9, offensiveLifeMin 12/21/29, run-speed 10/13/18). No designer scales 8
base stats upward per tier and then makes the granted skill weaker on the better ring.

### FIX 3 (P2-b) - Epic + Legendary rings showed the Normal-tier icon (54 families)

Every `create_uber_souls`-generated `svc_uber` e/l ring carried
`bitmap=SVItems\jewelry\soul_n_icon.tex` (the generator hardcodes SOUL_BITMAP for all tiers). The icon
law (CLAUDE.md key lessons) is `soul_{n,e,l}_icon.tex` per tier. FIX: rewrite the tier letter in place
-> e rings show `soul_e_icon`, l rings show `soul_l_icon`. Purely cosmetic; the soul_e/soul_l textures
already ship in `SVItems.arc` (verified present). **108 rings across 54 families** (54 e + 54 l);
n-tier rings were already correct and are untouched. The 47 module-authored `svc_uber` souls
(hadesmarshal, diadochi, neferkha, ...) already carry correct per-tier icons and are NOT in the fixed
set, so this module stays disjoint from every other registry module.

**Total intended diff (FIX-WAVE-2): 114 records MODIFIED + 3 REMOVED** (dry-run replay, exact match).
= 106 icon rings (108 wrong-icon svc_uber e/l MINUS the 2 removed tombguardian e/l rings) + 12
crow-controller records (crowboar/glittertail/koroush/nkac n/e/l) + 6 level-fix records + 1 tombguardian
monster detach, unioned (overlaps: crowboar e/l are in both icon + controller; crowboar_l in
icon+controller+level; glittertail/koroush/nkac e/l in icon+controller). REMOVED = the 3
`um_tombguardian_soul_{n,e,l}` records. Record count 51,029 -> 51,026.

## 2. The `verify()` gate (fail-loud regression guard) - now ROSTER-WIDE

Runs post-finalization over the FINAL assembled db (step 4, after the backstop + drop forcer). Two
invariants:

- **Tier monotonicity (ROSTER-WIDE).** For **EVERY** soul equipmentring family with all 3 tiers,
  `augmentSkillLevel1..4` (where the augment NAME is present AND IDENTICAL across n/e/l) and
  `itemSkillLevel` (where the granted skill NAME is present AND IDENTICAL across n/e/l) must be
  non-decreasing `n<=e<=l`. This is widened from round-1's svc_uber-only scope precisely so the class
  cannot recur on a NON-svc_uber soul (the bloodtip/gustleech miss). The **same-name guard** is
  load-bearing: a family whose Epic ring grants a DIFFERENT skill than its Normal ring is not an
  inversion of one skill, so its levels are not comparable (comparing them would false-positive the
  build gate on a legitimate design). Ground-truth check: the guarded predicate flags exactly the 5
  inverted families on GOLDEN and 0 after the fix; a presence-only (unguarded) variant flags the SAME 5
  today, so the guard adds zero false negatives now and prevents false positives on future content.
- **Per-tier icon law (svc_uber).** No `svc_uber` e/l/n ring may carry a `soul_{n,e,l}_icon` whose tier
  letter != the ring's tier. (The audit found 0 non-svc_uber icon defects, so this stays svc_uber-scoped.)

All three negative-tested (sec 4): the gate fail-louds on an injected **svc_uber** inversion, on an
injected **NON-svc_uber** (bloodtip) inversion - proving the widening bites - AND on an injected
wrong-tier icon.

### Correction to the round-1 report's completeness claim

The round-1 report stated "only the 3 fixed families ever violated it; after the fix the whole roster is
monotonic." That was FALSE: a roster-wide re-scan of the same GOLDEN arz found **5** inverted families
(the 3 svc_uber + `spider\bloodtip_soul` 5/1/9 + `vulture\gustleech_soul` 10/4/7). The round-1 `verify()`
"passed" only because it was scoped svc_uber-only and never looked at the other 2. Round-2 fixes all 5
AND widens the gate roster-wide, so the completeness claim now holds by construction and by the negative
test.

## 3. What was NOT fixed, and why (curiosity findings + design decisions)

The audit's other MINOR-GAPs were each ground-truth-verified before acting. Two did NOT survive
verification as "cheap-in-passing fixes":

### P2-a Tomb Guardian -> RESOLVED per Will (FIX 5 / D2): keep Common, retire the soul

Will's directive (2026-07-14): "Do not promote tomb guardian and do not have him drop a soul."
Ground truth (gt_probe over the GOLDEN arz) shows `um_tombguardian_26` = **Common**, charLevel 26,
characterLife **609**, name `tagMonsterName294` (a genuine Common Anubis Hound; its Hero cousin
`um_foulbeast_28` = **Hero**, life **5612**, 9x), and - the audit missed this - it STILL carries the
uber soul in a loot path: `lootFinger2Item1 = [um_tombguardian_soul_{n,e,l}]`, only gated off by
`chanceToEquipFinger2 = 0.0` (force-zeroed by `_gate_common_soul_leaks`). The wiring is created by
`apply_svc_patches._place_orphan_monsters`, which - by its own comment - wires it "against the
Hero/Boss/Quest design". So today the soul is **referenced-but-unobtainable**: attached to the loot
table but never droppable. Whole-DB scan: the ONLY reference to `um_tombguardian_soul` anywhere is this
one monster (no enchanting formula, no other carrier).

FIX 5 (module `apply()`, guarded/idempotent), matching Will's directive exactly:
- **keep** `monsterClassification = Common` and `chanceToEquipFinger2 = 0.0` (do NOT promote);
- **detach** the soul from `um_tombguardian_26.lootFinger2Item1` (cleared to `['','','']`), so nothing
  references the soul and there is no dangling loot ref once it is removed;
- **retire** the now-unreferenced `um_tombguardian_soul_{n,e,l}` records (removed from the arz);
- **drop** the dangling name tag `tagSVCSoulTombguardian` from the tags dict (its only referents were
  the 3 removed rings), so `Text.arc` carries no orphan name.

Verified on the patched arz (dry-run): 3 soul records gone, **0** records still reference
`um_tombguardian_soul` (no new dangling ref), class Common + chance 0 preserved. `verify()` fail-louds
if the soul is ever re-attached or re-created. Root-cause follow-up (documented, not required): a future
change could make `_place_orphan_monsters` skip soul creation for deny-listed records, at which point
every step of FIX 5 no-ops cleanly.

### P2-d Soulfeeder pet spirit-breath -> AUDIT FALSE POSITIVE (nothing to fix)

The mod's `bonepet20` already casts `bonescourge_spiritbreath.dbr` (wired at BOTH `skillName4` and
`specialAttack2SkillName`, both resolving). The audit's "loss" was SV's `xxx`-prefixed DISABLED variant
+ the `drxplaceholder.dbr` marker. "Restoring" the SV path would add a dangling/duplicate skill = a
regression. Correctly left untouched.

### FIX 4 / D3 - crowboar summoned-crow "resets before acting" (+ 3 same-shape siblings)

Will (2026-07-14): "fix the crowboar soul's summoned crow bug". Ground truth (gt_probe / gt_sweep over
the GOLDEN arz):

- `crowboar_soul_{n,e,l}` grants the SHARED mook skill `records\skills\soulskills\carrioncrow_summon.dbr`
  (Skill_SpawnPet, `petBurstSpawn=1`, `petLimit=10`, permanent, `isPetDisplayable=0`) via `itemSkillName`,
  with `itemSkillAutoController = base_atenemy_onattack`. So every wearer attack re-casts Summon Carrion
  Crow; the burst+limit re-spawns the whole flock, resetting the crows before they can act (the reported
  bug). The crow PETS themselves (`carrioncrow_1/2/3`) are valid Pet.tpl aggressive friendlies - the bug
  is the summon WIRING, not the pet.
- The mod's worn companion-summon convention is **UNANIMOUS (18/18)**: Lyia Leafsong + the 17 boss-summon
  souls (blood_toxeus, enslaver, hadesmarshal, neferkha, tantalus, mnemophage, kravmoloch, voranthys,
  broodmother, mountainblade, ferryman, pygmalion, sarpedon, eaterofdays, xeiwang, palai, phagia) carry
  **NO `itemSkillAutoController`** (manual-cast) + `petLimit=1` + a permanent pet. Cast once, the pet
  persists and fights.

**FIX (match the convention; per-soul; ZERO shared-skill collateral):** REMOVE `itemSkillAutoController`
from the deviant svc_uber companion-summon rings, so the summon becomes manual-cast (exactly the Lyia
model) and the flock persists instead of resetting. The shared summon SKILLS are NOT touched, so the
SV-original on-attack SWARM souls that share them (carrionlord + direflock share carrioncrow_summon; 6
skeleton-raiser souls share skeleton_summon; aphiastas shares summon_firesprite; graklos shares
wraith_summon - all designed "raise-a-swarm-on-attack" identities, most drop-gated) are 100% unaffected.

**Sweep (same bug = same wave):** the exact defect class = an **svc_uber** companion-summon soul granting
a **PERMANENT (no-TTL)** SpawnPet skill that carries an **on-attack** auto-controller. Exactly 4 families
qualify roster-wide (the brief's "petLimit=1" was imprecise - crowboar is petLimit 10; the true signature
is the on-attack-controller-on-a-permanent-companion-summon deviation). All fixed, all 3 tiers each = 12
records:

| Family | grant (shared skill, NOT edited) | controller removed | petLimit |
|---|---|---|---|
| `svc_uber\crowboar_soul` | carrioncrow_summon | base_atenemy_onattack | 10 |
| `svc_uber\glittertail_soul` | summon_firesprite | awakeneddeadsoul_onattack | 5 |
| `svc_uber\koroush_soul` | wraith_summon | base_atenemy_onattack | 5 |
| `svc_uber\nkac_soul` | skeleton_summon | base_atenemy_onattack | 5 |

(mountainblade was probe-flagged then cleared: its controller field is already empty = manual-cast; NOT
touched.) **Pet.tpl safety:** touches only the item ring controller field - no pet record, no
Monster.tpl->Pet.tpl copy, no `spawnObjectsTimeToLive` change. `verify()` fail-louds if any svc_uber
permanent-summon soul carries an on-attack controller (regression guard). **Known minor residual** (NOT
the reported bug; optional future polish): `carrioncrow_summon` ships `isPetDisplayable=0`, so the
manual-cast crow fights but shows no pet-window health bar; a fully clean companion would need a dedicated
per-soul summon skill (the convention) rather than the shared mook skill - left for a content pass since
the skill is shared with the SV souls. `validate_summon_pets` stays **PASS** (pets unchanged).

### P2-c boss-summon nymph icons (17 souls) -> D4: REQUIRED integration merge-set member

Fixed on `feat/b40-soul-icons` (commit `9db3f5f`; overrides `skillUpBitmapName`/`skillDownBitmapName` on
the 17 lyia-cloned boss-summon skills). VERIFIED it still applies to current main: `git merge-tree
--write-tree main feat/b40-soul-icons` returns a clean tree (`c64ee9a`) with **0 conflicts** (auto-merges
`tools/apply_svc_patches.py`). So per the directive it stays its own branch and is a **REQUIRED member of
the integration merge set** - NOT duplicated here (would collide). It is disjoint from this module and
from FIX 4 (the 4 FIX-4 souls grant mook summons with their own mook icons, not the nymph icon; the b40
branch edits the 17 nymph-iconed lyia-cloned skills).

### P3 items -> Will design decisions (unchanged; see the audit)

P3-a (79 souls drop-dead behind the Hero/Boss/Quest gate - add Champion?), P3-b (5 formula-only souls
with no monster carrier), P3-c (SV-inherited pet equip dangles), P3-d (SV DB hygiene). Unchanged.

### LAW-noted (untouched, as required)

`pharaohshonorguard_soul` downside redesign, `svc_uber\kallixenia_soul` uber redesign, the 5 build37
`skill_quality` grant reassignments, and ALL Occult/Hunting mastery content. **Disjointness proven**
(sec 4): the 111 touched records carry 0 hits on Occult/Hunting/mastery/kallixenia/abyssalliche/
pharaohshonorguard, and 0 on `corpsemanager` (skill_quality reassigns corpsemanager's GRANT to the
`bloodtip_devour` *skill* - a different record from our `bloodtip_soul` *ring* edit).

## 4. Verification record (no heavy build; dry-run replay + patched-arz contracts)

Replay `tools/debug/souls_quality_replay.py <build40 arz>` over the build40 GOLDEN arz (`b33c5a44`, the
artifact the audit graded) - **RESULT: PASS** (FIX-WAVE-2, all 5 fixes):

1. **Intended-only diff** - `db._modified` after `apply()` == exactly the predicted **114** modified
   records; AND exactly **3** records REMOVED (the tombguardian souls). 0 unexpected, 0 missing.
2. **Field minimality** - each modified record changed ONLY its allowed field(s): `bitmap` (icon rings),
   the intended level field(s), `itemSkillAutoController` REMOVED (crow rings), or `lootFinger2Item1`
   cleared (tombguardian monster); every other field byte-identical.
3. **Correctness** - all 5 families run non-decreasing (crowboar aug+grant 1/2/3; onyxspine aug 1/2/3,
   grant 3/5/8 untouched; steamcrawler aug 1/2/3; bloodtip grant 5/7/9; gustleech grant 10/12/14); every
   e/l ring shows its own tier icon; the 4 crow-class rings (12 records) have NO controller (grants
   intact); um_tombguardian_26 carries no soul ref (Common + chance 0 preserved) and the 3 tombguardian
   soul records are gone with 0 residual references.
4. **`verify()` passes** - all four gates green (monotonicity + svc_uber icon + crow-controller +
   tombguardian-retired).
5. **Idempotency** - a 2nd `apply()` modifies 0 new records and removes 0 more.
6. **Negative tests (5)** - `verify()` fail-louds on: an injected svc_uber inversion; an injected
   NON-svc_uber (bloodtip) inversion (names the family); an injected wrong-tier icon; an injected
   on-attack controller on an svc_uber permanent summon (names crowboar); and a re-attached tombguardian
   soul on the monster loot.

**Contracts on the patched arz (build40 GOLDEN + this module, written via `write_arz`):**
- `validate_soul_augments <patched>` = **PASS** (0 dangling, 0 inactive; 4,926 skill refs / 1,390
  activation chains).
- `validate_summon_pets <patched> <base> <sv098>` = **PASS** ("every mod-authored soul-granted summon
  spawns a complete, renderable, usable pet"; only the pre-existing kaets_soul engine-clamp WARN - the
  crow-controller removal touches no pet).
- **Resource dangling-ref check (targeted, patched arz):** the 3 tombguardian soul records are GONE and
  **0** records anywhere still reference `um_tombguardian_soul` - so the removal introduces no dangling
  `.dbr` ref; the detached loot slot is `['','','']` (empty, not a path). `validate_tags` is PASS by
  construction (the dropped `tagSVCSoulTombguardian`'s only referents were the 3 removed rings; no other
  tag/field touched).
- Fast gates: `py -m py_compile` (module + replay + `__init__`) OK; `py tools/patches/_check_registry.py`
  OK (14 modules, order `39d94e3201684246...`).

**Namespace safety** (`probe_ns_safety_r2.py`): all 111 touched records are under
`records\item\equipmentring\soul\`; the 3 NON-svc_uber records are exactly `spider\bloodtip_soul_e`,
`vulture\gustleech_soul_e`, `vulture\gustleech_soul_l`; **0** hits on any LAW namespace; **0**
corpsemanager records.

**Soul contracts** (patched temp arz = build40 GOLDEN + this module, written via `write_arz`; run vs
baseline GOLDEN too to prove no regression). Base = TQAE `database.arz`; upstream = SV 0.98i
`database.arz`:

| Contract (invocation) | Baseline (b33c5a44) | Patched | Delta |
|---|---|---|---|
| `validate_soul_augments <arz>` | **PASS** exit 0 (0 dangling, 0 inactive) | **PASS** exit 0 | none |
| `validate_summon_pets <arz> <base> <upstream>` (the build-gate invocation) | **PASS** exit 0 | **PASS** exit 0 | none |
| `validate_summon_pets <arz>` (bare single-arg) | exit 1 (234 strict + 91 warn) | exit 1 (234 strict + 91 warn) | **byte-identical** |

`validate_tags` is **PASS by construction**: this module adds no tags and changes no
`itemNameTag`/`itemText`/`description` field, so the arz's referenced-tag set is identical to baseline.

> **On the bare single-arg `validate_summon_pets` exit code (corrects a round-1 report ambiguity).**
> The round-1 report labeled `validate_summon_pets` "PASS" - correct for the **3-arg** invocation the
> build/bootstrap gate actually runs (base-resolution + upstream leniency; exit 0). A **bare single-arg**
> run (no base arz, no upstream arz) returns **exit 1** with 234 "strict" failures + 91 upstream warnings
> - this is the tool's own documented "expect noise" behavior (its usage note: "a bare single-arg run
> still works but without base-resolution or upstream leniency, so expect noise"). Crucially the result
> is **byte-identical baseline vs patched** (234/91 both), so this module - which touches ZERO pet
> records - introduces zero regression under ANY invocation. Not a blocker and not this module's concern.

**Fast gates:** `py -m py_compile tools/patches/souls_quality.py tools/patches/__init__.py
tools/debug/souls_quality_replay.py tools/debug/_souls_quality_audit.py` OK;
`py tools/patches/_check_registry.py` OK (14 modules, order `39d94e3201684246`).

## 5. WILL DECISION items (status)

- **D1 - RATIFIED (was WILL-VETO): bloodtip + gustleech ship as-is.** Will 2026-07-14 (verbatim): "yes
  fix any blatant errors that you detect ... bloodtip 5/7/9 + gustleech 10/12/14 ship as-is". The round-0
  WILL-VETO flag is **CLEARED**. FIX 2 stands: `bloodtip 5/7/9`, `gustleech 10/12/14` (raise-only, grant
  NAMES untouched). These two `itemSkillLevel` arrays are byte-identical to SV 0.98i, so this is a
  deliberate divergence from SV-original data (amgoz1 data-entry oversights). The `_SV_INVERSION_FIX`
  block in the module is kept as the documented **HISTORICAL REVERT PATH**: deleting it restores SV's
  exact numbers (the svc_uber trio + icon + crow + tombguardian fixes stand independently).
- **D2 - APPLIED: Tomb Guardian** (sec 3, FIX 5) - kept Common, soul detached + retired with its tag, per
  Will's directive. No promotion.
- **D3 - APPLIED: crowboar crow + 3 siblings** (sec 3.5, FIX 4) - manual-cast, per the Lyia convention.
- **D4 - REQUIRED merge-set member: `feat/b40-soul-icons`** (`9db3f5f`) - merges cleanly onto main
  (0 conflicts); must be in the integration merge set for the 17 nymph-iconed boss-summon skills.
- **Creative renames: NONE.** No soul name/description text changed (the only tag touched is the DROPPED
  `tagSVCSoulTombguardian`, part of retiring that soul).

## 5.5 D5 - blatant-error sweep of the 155 MINOR-GAP list

Every MINOR-GAP class in `souls_quality_audit.md` sec 3, classified BLATANT DATA ERROR vs SUBJECTIVE
POLISH / DESIGN, per Will's directive ("classify each ... fix every blatant error via the module ... leave
polish documented"):

| MINOR-GAP class | Count | Verdict | Disposition |
|---|---:|---|---|
| ICON-UNIFORM-N (svc_uber e/l show the N-tier icon) | 54 fam / ~108 rings | **BLATANT** (wrong icon data) | **FIXED** here (FIX 3) |
| SUMMON-SKILL-NYMPH-ICON (boss summons show Lyia's icon) | 17 souls | **BLATANT** (wrong icon data) | **FIXED** on `feat/b40-soul-icons` (D4, required merge-set) |
| DROP-GATED-CHANCE-0 (only Common/Champion carry it) | 79 fam | SUBJECTIVE / design | LEFT documented - correct data under the deliberate Hero/Boss/Quest drop law (P3-a); re-tier / add Champion / accept = a Will design call, NOT wrong data. (`um_tombguardian_soul` is in this set but is a mod-authored orphan Will told us to retire - handled by FIX 5, distinct from the SV-original drop tradeoff.) |
| NO-FINGER2-DROPPER (formula-only reagents) | 5 souls | SUBJECTIVE / design | LEFT documented - they resolve + are used as enchant reagents (P3-b); giving them a carrier is a design call, not a data fix. |
| PET-EQUIP-DANGLING-UPSTREAM | 2 souls | SUBJECTIVE / upstream-faithful | LEFT documented - SV ships the identical dangle; the engine skips it (P3-c). |
| PET-KIT-SMALLER-THAN-SV (soulfeeder) | 1 soul | FALSE POSITIVE | LEFT - bonepet20 already casts bonescourge_spiritbreath (verified). |

**Conclusion:** the only blatant DATA errors in the 155-item list are the two icon classes, both now
covered (FIX 3 + the D4 branch). The DEFICIENT tier inversions (5, FIX 1+2) are the audit's separate P1
set, also fixed. The two blatant errors NOT in the audit's MINOR-GAP list but detected during
ground-truthing (crowboar crow controller, tombguardian orphan soul) are fixed by FIX 4 + FIX 5. All
remaining MINOR-GAP items are design decisions / a false positive, left documented untouched.

## 6. Files

- `tools/patches/souls_quality.py` - the fix module (apply + roster-wide verify).
- `tools/patches/__init__.py` - REGISTRY includes `souls_quality` (position 13, before `visuals`).
- `tools/debug/souls_quality_replay.py` - the dry-run replay + fail-loud proof (reusable; updated for
  the 5-family fix + the roster-wide negative test).
- `tools/debug/_souls_quality_audit.py` - the round-0 audit probe; its inversion detector now also
  catches `itemSkillLevel`-only inversions (`GRANT-LEVEL-TIER-INVERSION`) so a re-run is self-correcting.
- `docs/reports/souls_quality_audit.md` - the audit this fixes (round-2 corrections: DEFICIENT 3->5,
  bloodtip/gustleech re-graded).

Ships in a later integration build per the concurrency plan (no heavy build in this lane).
