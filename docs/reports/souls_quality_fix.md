# Souls Quality FIX (feat/souls-quality) - round 1 + round 2

> Fixes for the tier-inversion + icon defects found in `docs/reports/souls_quality_audit.md`
> (full-roster ground-truth audit of the build40 GOLDEN arz, md5 `b33c5a44`). All fixes land in
> ONE registry module `tools/patches/souls_quality.py` (`apply()` + a fail-loud `verify()`), touch
> ONLY soul equipmentring records, and avoid every LAW namespace (Occult/Hunting/mastery/kallixenia/
> pharaohshonorguard). No em dashes by house style.
>
> **Round-2 (2026-07-14)** extends round-1 after a vet found the round-0 audit UNDER-reported the
> DEFICIENT set: a roster-wide monotonicity re-scan of the GOLDEN arz found **5** inverted soul
> families, not 3. The 2 extra families (`spider\bloodtip_soul`, `vulture\gustleech_soul`) carry the
> same defect class on `itemSkillLevel` and are now fixed here; `verify()` is widened roster-wide so
> the class cannot recur anywhere.

## 1. What shipped (the fix set)

One registry module, `tools/patches/souls_quality.py` (REGISTRY position 13, after `boss_skill_fix`,
before `visuals`), with `apply()` + a fail-loud `verify()` hook. It fixes **all 5** tier inversions in
the shipped roster (raise-only) plus the svc_uber per-tier icon law, and installs a roster-wide
regression gate.

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

**Total intended diff: 111 records** = 108 icon rings + 3 NEW level-only records (`bloodtip_soul_e`,
`gustleech_soul_e`, `gustleech_soul_l`). The 3 svc_uber `_l` level records are already in the 108-icon
set (they are svc_uber e/l rings with wrong icons), so only the 3 SV records add to the count.

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

### P2-a Tomb Guardian obtainability -> WILL DECISION (not a cheap fix)

Ground truth shows `um_tombguardian_26` = **Common**, charLevel 26, characterLife **609**, name
`tagMonsterName294`, spawned as a *champion* in mummy caster packs; its Hero cousin `um_foulbeast_28` =
**Hero**, characterLife **5612** (9x), name `tagNewHero266`. So it is a genuine Common Anubis Hound, not
a mis-classified uber. Reclassifying it to Hero is a pack-BALANCE change (hero loot/XP/CC everywhere it
spawns), so it belongs with the P3-a drop-gate decision, not the cosmetic fixes. Options for Will:
(a) reclassify to Hero; (b) point a real Hero/Boss Anubis Hound at `um_tombguardian_soul`; (c) accept as
a correctly-gated Common (the gate working as intended).

### P2-d Soulfeeder pet spirit-breath -> AUDIT FALSE POSITIVE (nothing to fix)

The mod's `bonepet20` already casts `bonescourge_spiritbreath.dbr` (wired at BOTH `skillName4` and
`specialAttack2SkillName`, both resolving). The audit's "loss" was SV's `xxx`-prefixed DISABLED variant
+ the `drxplaceholder.dbr` marker. "Restoring" the SV path would add a dangling/duplicate skill = a
regression. Correctly left untouched.

### P2-c boss-summon nymph icons (17 souls) -> handled on another branch

Already fixed on the unmerged `feat/b40-soul-icons` (commit `9db3f5f`). Integrate that branch in the next
integration build; NOT duplicated here (would collide with that branch's edits).

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
artifact the audit graded) - **RESULT: PASS**:

1. **Intended-only diff** - `db._modified` after `apply()` == exactly the predicted set (108 wrong-icon
   e/l rings UNION the 3 SV level records = **111**). 0 unexpected, 0 missing.
2. **Field minimality** - each touched record changed ONLY `bitmap` (icon rings) and/or the intended
   level field(s); every other field byte-identical.
3. **Correctness** - all 5 families now run non-decreasing: crowboar aug 1/2/3 + grant 1/2/3; onyxspine
   aug 1/2/3 (grant 3/5/8 untouched); steamcrawler aug 1/2/3; bloodtip grant 5/7/9; gustleech grant
   10/12/14. Every e/l ring shows its own tier icon.
4. **`verify()` passes** - roster-wide monotonicity + svc_uber icon gates green.
5. **Idempotency** - a 2nd `apply()` touches 0 new records.
6. **Negative tests** - `verify()` fail-louds on an injected svc_uber inversion, on an injected
   NON-svc_uber (bloodtip) inversion (names the family), AND on an injected wrong-tier icon.

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

## 5. WILL VETO / DECISION items

- **WILL VETO - SV-original divergence (bloodtip + gustleech).** FIX 2 changes two `itemSkillLevel`
  arrays that are **byte-identical to SV 0.98i**. We judge them amgoz1 data-entry oversights (the rest of
  each ring tiers upward correctly; a farmed Epic/Legendary that grants a weaker skill than the common
  Normal is the exact 'DONE means DONE' repeat-report shape) and fix them raise-only to
  `bloodtip 5/7/9`, `gustleech 10/12/14`. **If Will considers SV's exact numbers sacrosanct here, revert
  the `_SV_INVERSION_FIX` block** (the svc_uber trio + icon fixes stand independently). Two knobs if Will
  wants the fix but more conservative: (a) clamp to SV's own peak rather than extend past it -
  `gustleech 10/10/10` (flat grant, tiers still differ on base stats), `bloodtip 5/7/9` already stays
  within SV's own [5,9] span; (b) any other monotonic non-decreasing values.
- **Creative renames: NONE.** This round changes no soul name or description text (no tag edits).
- **DECISION - P2-a Tomb Guardian** (sec 3): reclassifying the Common `um_tombguardian_26` to Hero is a
  pack-balance change, deliberately NOT auto-applied. Pick option (a)/(b)/(c).
- **INTEGRATE - P2-c** `feat/b40-soul-icons` (`9db3f5f`) in the next integration build for the 17
  nymph-iconed boss-summon skills.

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
