# Souls Quality - round-1 FIX (feat/souls-quality)

> Round-1 fixes for the defects found in `docs/reports/souls_quality_audit.md`
> (full-roster ground-truth audit of the build40 GOLDEN arz, md5 `b33c5a44`).
> All fixes land in ONE registry module `tools/patches/souls_quality.py` and touch
> ONLY the mod-generated `svc_uber` soul namespace. No SV-original soul, no
> Occult/Hunting hand-tuning, no other module's records. No em dashes by house style.

## 1. What shipped (the fix set)

One new registry module, `tools/patches/souls_quality.py` (REGISTRY position 13, after
`boss_skill_fix`, before `visuals`), with `apply()` + a fail-loud `verify()` hook.

### FIX 1 (P1) - the 3 DEFICIENT souls: Legendary was WEAKER than Epic

Root cause (audit sec 4, re-confirmed on ground truth): `create_uber_souls` scales
`SOUL_DESIGNS`' base level 1 by the per-tier `_DIFF_SCALE` (0.6/0.8/1.0) -> raw n/e/l
= 0/0/1; then the `_fix_soul_skill_levels` backstop (build36, B-SOUL-PROC-1) BUMPS
level-0 grants to the per-tier default (n->1, e->2) but SKIPS the L ring because its
scaled value was already 1 (>=1). Net: **n/e/l = 1/2/1** - the Legendary ring is
strictly worse than the Epic. Healthy siblings from the same generator (bloodrunner,
xix) run 1/2/3.

FIX: raise the L-tier levels to 3 (the bloodrunner/xix Legendary value). We only ever
RAISE, so the fix is order-independent w.r.t. the backstop (which runs AFTER this
module in `run_registry_gates` and only bumps level-0; it leaves our >=1 L ring alone
and independently completes n/e = 1/2).

| Soul (record `..._soul_l.dbr`) | Field(s) set to 3 | augment n/e/l BEFORE -> AFTER |
|---|---|---|
| `svc_uber\crowboar_soul_l` | augmentSkillLevel1, augmentSkillLevel2, **itemSkillLevel** | 1/2/1 -> **1/2/3** (grant too) |
| `svc_uber\onyxspine_soul_l` | augmentSkillLevel1, augmentSkillLevel2 | 1/2/1 -> **1/2/3** (grant already 3/5/8) |
| `svc_uber\steamcrawler_soul_l` | augmentSkillLevel1, augmentSkillLevel2 | 1/2/1 -> **1/2/3** (no grant; correct) |

Will's SKILL PICKS are untouched (crowboar still Summons Carrion Crow, onyxspine still
grants Ring of Lightning). Only the tier LEVEL of the existing augments/grant changes.

### FIX 2 (P2-b) - Epic + Legendary rings showed the Normal-tier icon (54 families)

Every `create_uber_souls`-generated `svc_uber` e/l ring carried
`bitmap=SVItems\jewelry\soul_n_icon.tex` (the generator hardcodes SOUL_BITMAP for all
tiers). The icon law (CLAUDE.md key lessons) is `soul_{n,e,l}_icon.tex` per tier. FIX:
rewrite the tier letter in place -> e rings show `soul_e_icon`, l rings show
`soul_l_icon`. Purely cosmetic; the soul_e/soul_l textures already ship in
`SVItems.arc` (verified present). **108 rings across 54 families** (54 e + 54 l);
n-tier rings were already correct and are untouched.

The 47 module-authored `svc_uber` souls (hadesmarshal, diadochi, neferkha, polis_vault,
etc.) already carry correct per-tier icons and are NOT in the fixed set, so this module
stays disjoint from every other registry module.

## 2. The `verify()` gate (fail-loud regression guard)

Runs post-finalization over the FINAL assembled db (step 4, after the backstop + drop
forcer). Two invariants over the WHOLE `svc_uber` roster, so the class cannot silently
regress in a future content build:

- **Tier monotonicity** - `augmentSkillLevel1..4` (where the augment name is present in
  all n/e/l) and `itemSkillLevel` (where the grant is present in all n/e/l) must be
  non-decreasing `n<=e<=l`. This is the audit's recommended "tier-monotonicity build
  gate". Ground truth: only the 3 fixed families ever violated it; after the fix the
  whole roster is monotonic.
- **Per-tier icon law** - no `svc_uber` e/l/n ring may carry a `soul_{n,e,l}_icon`
  whose tier letter != the ring's tier.

Both negative-tested (see sec 4): the gate fail-louds on an injected inversion AND on an
injected wrong-tier icon.

## 3. What was NOT fixed, and why (curiosity findings + design decisions)

The audit's other MINOR-GAPs were each ground-truth-verified before acting. Two of them
did NOT survive verification as "cheap-in-passing fixes":

### P2-a Tomb Guardian obtainability -> WILL DECISION (not a cheap fix)

The audit proposed reclassifying `um_tombguardian_26` to Hero so its uber soul can drop.
Ground truth shows this is a **balance change, not an icon-class fix**:

- `um_tombguardian_26` = **Common**, charLevel 26, characterLife **609**, name
  `tagMonsterName294` (a generic monster name), spawned as a *champion* in mummy caster
  packs (`mummy_02/03_caster0*` nameChampion11/15).
- its Hero cousin `um_foulbeast_28` = **Hero**, charLevel 28, characterLife **5612**
  (9x), name `tagNewHero266`, extra hero skills (ondeath_frostorb + frozen_orb).

So `um_tombguardian_26` is a genuine Common Anubis Hound, NOT a mis-classified uber.
Reclassifying it to Hero would give a 609-HP hero-bar mob everywhere it spawns in normal
mummy packs (hero loot, XP, CC resistances) - a gameplay change Will should sign off on.
This belongs with the P3-a drop-gate decision (souls gated off because their carriers are
Common/Champion), not with the cosmetic fixes. **Options for Will:** (a) reclassify
`um_tombguardian_26` to Hero (audit's recipe; makes it a weak hero in packs);
(b) point a real Hero/Boss Anubis Hound at `um_tombguardian_soul`; (c) accept it as a
correctly-gated formula/ghost soul (the design gate working as intended for a Common mob).

### P2-d Soulfeeder pet spirit-breath -> AUDIT FALSE POSITIVE (nothing to fix)

Ground truth: the mod's `bonepet20` (and every bonepet the Soulfeeder summon spawns)
**already casts** `bonescourge_spiritbreath.dbr` - it is wired at BOTH `skillName4` and
`specialAttack2SkillName`, and the skill record
`records\skills\spirit\drxpet\drxpet_skills\bonescourge_spiritbreath.dbr` resolves in the
mod arz. The audit's "missing spirit-breath" flag came from the pet-kit comparison seeing
SV's `xxx`-prefixed DISABLED variant on `bonepet01`'s `skillName4` (+ the
`records\drxplaceholder.dbr` disable marker) as "in SV, not in mod". The mod actually has
spirit-breath ACTIVE (SV had it disabled at that slot). "Restoring" the SV path would add
a dangling/duplicate skill = a regression. Correctly left untouched.

### P2-c boss-summon nymph icons (17 souls) -> handled on another branch

Already fixed on the unmerged `feat/b40-soul-icons` (commit `9db3f5f`, `_build_boss_summon`
overriding `skillUpBitmapName`/`skillDownBitmapName`). Integrate that branch in the next
integration build; NOT duplicated here (would collide with that branch's edits).

### P3 items -> Will design decisions (unchanged; see the audit)

P3-a (79 souls drop-dead behind the Hero/Boss/Quest gate - add Champion to the gate?),
P3-b (5 formula-only souls with no monster carrier), P3-c (SV-inherited pet equip
dangles), P3-d (SV DB hygiene: dup rings / templates / test rings). Unchanged.

### LAW-noted (untouched, as required)

`pharaohshonorguard_soul` downside redesign, `svc_uber\kallixenia_soul` uber redesign
(diverges from its SV original by design), the 5 build37 `skill_quality` grant
reassignments, and ALL Occult/Hunting mastery content. The fix asserts its diff avoids
these (sec 4): 0 touched records match Occult/Hunting/kallixenia/pharaohshonorguard.

### No SV-drift restoration, no granted-skill redesign, no dead-augment repair needed

The audit proved these are already clean on the shipped arz: 0 dead augments, 0 broken
proc chains, 0 lost SV grants/flavor (`validate_soul_augments` PASS), and the 2 stat-
fidelity findings are LAW hand-edits. Nothing to restore/redesign/repair. This round is
therefore the tier-inversion + icon law only.

## 4. Verification record (no heavy build; dry-run replay only)

Replay `tools/debug/souls_quality_replay.py <build40 arz>` over the build40 GOLDEN arz
(`b33c5a44`, the same artifact the audit graded) - **RESULT: PASS**:

1. **Intended-only diff** - `db._modified` after `apply()` == exactly the predicted set
   (108 wrong-icon e/l rings; the 3 deficient `_l` souls are a subset). 0 unexpected, 0
   missing. `write_arz` independently reports "Modified records: 108".
2. **Field minimality** - each touched record changed ONLY `bitmap` (icon rings) and/or
   the intended L-tier level fields (the 3 souls); every other field byte-identical.
3. **Correctness** - crowboar/onyxspine/steamcrawler now run augment n/e/l = 1/2/3;
   crowboar grant 1/2/3; onyxspine grant 3/5/8 (untouched); every e/l ring shows its own
   tier icon.
4. **`verify()` passes** - roster-wide monotonicity + icon gates green.
5. **Idempotency** - a 2nd `apply()` touches 0 new records.
6. **Negative tests** - `verify()` fail-louds on an injected inversion AND on an injected
   wrong-tier icon.

**Namespace safety** (`probe_namespace_safety.py`): all 108 touched records are under
`\soul\svc_uber\` (54 e + 54 l); **0** hits on Occult/Hunting/mastery/kallixenia/
pharaohshonorguard.

**Soul contracts** (patched temp arz = build40 GOLDEN + this module, written via
`write_arz`; run vs baseline too to prove no regression):

| Contract | Baseline (b33c5a44) | Patched | 
|---|---|---|
| `validate_soul_augments` | PASS (0 dangling, 0 inactive) | **PASS** (0 dangling, 0 inactive) |
| `validate_summon_pets` | PASS | **PASS** (identical WARN set incl. the benign kaets clamp) |
| `validate_tags` | PASS | **PASS** |

`validate_tags` is also PASS **by construction**: this module adds no tags and changes no
`itemNameTag`/`itemText`/`description` field, so the arz's referenced-tag set is identical
to baseline.

**Fast gates:** `py -m py_compile tools/patches/souls_quality.py tools/patches/__init__.py`
OK; `py tools/patches/_check_registry.py` OK (14 modules, order `39d94e3201684246`).

## 5. WILL VETO / DECISION items

- **Creative renames: NONE.** This round changes no soul name or description text (no tag
  edits). Nothing to veto on naming.
- **DECISION - P2-a Tomb Guardian** (sec 3): reclassifying the Common `um_tombguardian_26`
  to Hero is a pack-balance change, deliberately NOT auto-applied. Pick option (a)/(b)/(c).
- **INTEGRATE - P2-c** `feat/b40-soul-icons` (`9db3f5f`) in the next integration build for
  the 17 nymph-iconed boss-summon skills.

## 6. Files

- `tools/patches/souls_quality.py` - the fix module (apply + verify).
- `tools/patches/__init__.py` - REGISTRY += `souls_quality` (position 13, before `visuals`).
- `tools/debug/souls_quality_replay.py` - the dry-run replay + fail-loud proof (reusable).
- `docs/reports/souls_quality_audit.md` - the round-0 audit this fixes.

Ships in a later integration build per the concurrency plan (no heavy build in this lane).
