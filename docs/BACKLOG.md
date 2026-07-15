# BACKLOG - Open issues (as of 2026-07-08, from Will's live TESTHUB play session)
> 🏺 **SVAERA-ADOPT (APPROVED-CONCEPT recon, 2026-07-14, awaiting Will's picks).** Full audit of "what
> SVAERA has that we don't": `docs/reports/svaera_goodies_audit.md` (repro `scratch_audit/svaera_goodies/*.py`).
> SVAERA arz = **110,495 records** (live workshop install `2076433374`; NB the in-repo `reference_mods` copy has
> NO Database arz, only Levels/Quests - the `docs/reference_mods.md` "0 MB DB" line is wrong). **30,714** SVAERA
> records absent from our effective DB (OURS∪BASE=92,259); **all 30,714 are SVAERA-authored-new, 0 are SV098
> content we dropped** (clean proof our overlay covers 100% of SV 0.98i). **Finding (2) divergence = SKIP as a
> class:** SVAERA re-templated + rebalanced ~every common record (sampled monsters 120/120, weapons 120/120, every
> mastery 100% diverge from BOTH base and SV098 - the "Steam fork with nerfs"; no surgical-fix subset to lift;
> contradicts amgoz1 classic + Will's mastery hand-tuning). **The good vein is ADDITIVE content.**
> **HEADLINE ADOPT (S effort, ZERO art coupling, verified droppable, art already in our shipped `drx.arc`/
> `DRXtextures.arc`/base):** 5 thematic Greek/Egyptian sets = 13 legendary/epic items -
> **Thoth's Favor** (`drxset049`, Egyptian, 2×Leg), **Hector's Bronze Armor** (`drxset051`, Trojan, 3×Epic),
> **Robes of the Pythia** (`drxset052`, Delphi, 2×Epic), **Patroclus' Disguise** (`drxset053`, Achilles, 3×Leg),
> **Might of Hephaestus** (`drxset058`, 3×Leg). All byte-present + functional (60-71 loot refs each) + absent from
> ours. Adopt via the EXISTING `build_svc_database.py::_graft_import_closure()` + Text-tag port + one SVC loot
> wire; no map, no new art arc. **Tier 2 (M, flavorful):** The Hunting Paradox (`newset002`, Laelaps+Teumessian
> fox), The Elephantine Triad (`newset005`, Khnum/Anuket/Satis), curated Greek/Egyptian legendary uniques bundle
> (Meteorite, Scepter of Lamashtu, Stormcrack, Nature's Revenge, Sickle of Kronos, Osiris' Atef, Vengeance of
> Sekhmet, Symbol of Hathor - filter OUT Norse/Chinese) - gated by the **`_DRX_Meshes.arc` art lever** (we ship a
> GUTTED 858KB vs SVAERA's 430MB; un-gutting or a subset-arc unlocks ~146 Leg + ~3,077 Epic `u_mod_*` at once).
> **Tier 3 (M-L):** `sv_ew` Artemis bestiary (Moon Wolf ~ Hound of Artemis + Artemisian Oceanid nymphs) - fits
> amgoz1 monster-identity bible; art in unshipped `N66_Mods.arc`+`SV_NewSkins.arc` + needs map placement.
> **Tier 4 (QoL):** `NpcItemUpgrader` free-upgrade town NPCs (54); blood weapon-enchant FX (Toxeus theme).
> **DELIBERATELY-SKIP families:** all xpack2/3/4 (Ragnarok/Atlantis/EE DLC), `item\formulas` (11,364 economy),
> the §3 stat-override rebalance, SVAERA's own souls model (`\soul\*`+`soulskills`, conflicts with ours),
> `OneShot_Dye` dyes, `mod_allcaravans` (we have Super Caravan), `sv_endgame` crystal-hub, mercenary-scroll system,
> `game\svic` economy. **Permission precedent:** the SVAERA mastery graft (below, 2026-07-10) recorded soa's verbal
> OK for additive SVAERA use - confirm it covers items/monsters before ship. Verified 8/8 candidates end-to-end
> (truly absent + functional, not cut). **Recommended first wave: the 5 clean sets as one drop-pack.**
> ⚡ **BUILD-SPEED: PREFIX CACHE DEFAULT-ON (2026-07-14, main) - harness gate PASSED, default flipped.**
> `tools/verify_cache_determinism.py` ran on main @ `7c38c9e` (clean machine, no build contention, serial):
> **COLD** (SVC_PREFIX_CACHE=1 SVC_CACHE_REFRESH=1 SVC_RELEASE_DROPS=1 PYTHONHASHSEED=0, forced MISS+STORE)
> exit 0 in **209s**, arz md5 `b33c5a447f3a8ca652c14f78d4ad1dd4` == build40 GOLDEN (55,351,206 B), tags md5
> `fe855a77324e99cc37ea3326c0cdc2b2`. **WARM** (same env, no refresh) exit 0 in **134s**, log-proven HIT on the
> same snapshot, arz + tags md5s IDENTICAL. COLD == WARM == GOLDEN bit-for-bit; a HIT saves ~75s (36%).
> Graft-flip negative test: SVC_GRAFT_SVAERA=0 changed the key and forced a MISS (wrong-hit class proven
> guarded); the graft-OFF full build itself aborts in `mastery_ui_audit` on the absent graft record
> `records/skills/warfare/drx_clubslam_fissure.dbr` - a pre-existing graft-OFF/registry incompatibility, NOT a
> cache defect. On that PASS, `tools/prefix_cache.py enabled()` now defaults **ON**; opt out with
> `SVC_PREFIX_CACHE=0` (or off/false/no), `SVC_NO_CACHE=1` still hard-disables, `SVC_CACHE_REFRESH=1` still
> forces a fresh store. Key/fingerprint logic and the advisory miss-to-cold fallback are UNCHANGED - staleness
> is always a MISS (the key covers input arz md5s + prefix env flags + the whole tools/ source tree), so the
> flip cannot change output bytes, only time. NOTE: because tools/*.py content is in the key, committing or
> reverting any tools file changes future keys (safe MISS, one cold rebuild).
> ⚡ **BUILD-SPEED: RECORD-INDEX (2026-07-14, main) - biggest remaining DB win, BYTE-IDENTICAL.** The extended
> phase re-scanned all ~51k records on every `_add_monster_to_pools` call (~28 calls) and on the substring
> `_find_record`. New shared, mutation-invalidated `_RecordIndex` (in `apply_svc_patches.py`) computes the derived
> views once: `name_lower` (for `_find_record`), lowercased-value `blob` + `has_name` (for pool discovery), invalidated
> by a new zero-cost `ArzDatabase._mutation_listeners` hook (set_field/clone_record notify; empty for every other tool)
> plus structural new-record detection. Also **de-shadowed the dual `_find_record`**: the early exact-path resolver was
> DEAD (Python rebinds the later substring def at import, so every call already ran the substring/first-match version);
> removed it, kept the substring impl as the single canonical (byte-identical behavior). **PROOF (both full DB builds
> EXIT=0, SVC_RELEASE_DROPS=1, cache-refresh):** arz md5 `b33c5a447f3a8ca652c14f78d4ad1dd4` == build40 GOLDEN, bit-for-bit,
> before AND after. Text/Levels(canonical+TESTHUB)/Quests unaffected by construction (their tooling imports neither
> changed module). **DB build 330s -> 211s; extended phase 175.1s -> 50.6s (124.5s / 71% cut).** Equivalence unit-tested
> (`scratchpad/ridx_proto.py`, 25 seeds + 5 edge classes) and real-ArzDatabase integration-tested vs a reference copy of
> the original scans. Files: `tools/apply_svc_patches.py`, `tools/arz_patcher.py`.

> 🗡️ **B39 BOSS-SKILL FIX (MERGED+BUILT+GATED in build39-dev, `feat/b39-boss-skills` @ `95edf55`).** Will
> (2026-07-13): the new bosses "not using skills when you fight them / when summoned". Audit (both surfaces):
> Surface B (soul-summoned pets) HEALTHY; Surface A (fought bosses) had a level-0 skill-wiring defect on **10
> apex bosses**. New registry module `tools/patches/boss_skill_fix.py` (position 11, after every boss-creating
> module, before `visuals`) makes 27 field edits at **per-skill donor-matched levels** (no clones/souls/pets, no
> damage rebalance): enables level-0 summon/attack specials, dead passives (boss_conversionimmunity/scaling/
> hero_scaling/toxeus_passiveproperties/armor_passive), auras, and restores Helepolis's displaced turret. `verify()`
> is **roster-derived + fail-loud** (scans every `um_*_99`, aborts on ANY chance>0 level-0 special + flags a boss
> not in the fix table) so a missed/new boss can't ship silently. Round-2 fixed the round-1 miss of
> **`um_voranthys_99`** (whole kit was level 0). Dry-run replay vs `baseline_build38.arz` (= build38-dev `fcd5dcab`):
> 27 edits, verify OK, idempotent, all 10 bosses clean, roster 0 leftovers, pets untouched, negative test PASS.
> Full RCA: `docs/reports/b39_boss_skills_rca.md`. **RE-VERIFIED in build39-dev** vs true build38a
> `6631f252`: 10 bosses CHANGED (32 skill-field diffs only - skillLevelN/skillNameN/specialAttack3*, 0 design drift),
> verify OK - see BUILD39-DEV GATE RECORD below.

> 🧩 **BUILD38 INTEGRATION (2026-07-13, main) - 5 GO-vetted lanes merged + integration fixes.** Merges (all
> clean, order hash `7ed29402a38d` -> `7c74a51f6ed8`, REGISTRY now 11 modules): `feat/b38-mastery-ui` @ `43611fc`,
> `feat/b38-damage` @ `ab5f5ac`, `feat/b38-enslaver-v2` @ `e2f87ef`, `feat/b38-language` @ `e22c62a`,
> `chore/b38-workshop-description` @ `475cfee`. Integration fixes commit `f1d53af` (+ reconcile `630bb9b`). NOT
> deployed; canonical build36a stays LIVE. **Full DB build + gate record DONE 2026-07-13 (see BUILD38-DEV GATE
> RECORD below): arz `fcd5dcab`, Text `dff9ad01`, all gates green, record-diff ZERO unexplained.** The Enslaver-residual
> stalker `limit=1` follow-up is now BUILT+VERIFIED (build38a, HEAD `2073fe6`): DEV-staged arz advances to `6631f252`
> (Text/Quests/map byte-identical); see BUILD38A GATE RECORD below.
> **FIXED this wave:**
> - **Mastery UI** (`mastery_ui_audit` module, after `hunting_occult_ui`): 8 graft icon repoints (7 `_DRX_Textures`
>   dead refs + 1 empty -> resolving XPack3/InGameUI arcs); Earth Rupture DE-DUP (graft `drxrupture`/`drxrupture_flare`
>   relabelled to the freed base tags `tagSkillName113` "Flame Surge" / `tagSkillName103` "Flame Arch"; SV `drxflamesurge`
>   stays the canonical Rupture) + Earth col-428 reflow (chains contiguous, base lower); Dream (xpack mastery 9)
>   background repointed off the black `skillbackgrounddiablo.tex` to the Spirit backdrop. **Nature "Sylvan Protection"
>   name wired in integration** (`drx_nymph_petmodifier_rootwave.skillDisplayName -> x3tagSkillNatureSylvanProtection`
>   + `...Desc`; base-game x3 tags, resolve at runtime, no Text.arc entry). Dry-run replay vs `baseline_build36.arz`:
>   15 records modified, 0 added, all asserts PASS.
> - **Damage numbers** (`damage_display` module, before `visuals`): bound the 7 missing AE floating-combat-text
>   FontStyle pointers (`DamageNormal/Elemental/OnPlayer/OverTime/Healing/HealingOnPlayer/PlayerImpairment`) on
>   `records\xpack\game\gameengine.dbr` (SV's pre-AE record lacked them -> only crits showed). Dry-run replay: 1
>   record, +7 STRING fields, 0 new records/tags, idempotent, verify() PASS.
> - **Enslaver v2** (`apply_svc_patches.py`): `_EN_SWEEP_K` 300 -> 600 (= /10 vs build36a K=60), ceiling 1/24000,
>   NEW per-slot `limit=1` = STRUCTURAL no-double (<=1 Enslaver per pool per trigger); fail-loud verify asserts it.
>   Reconciled with the `toxeus_suite` Hades-Hunt `_LS_MAX_P=1/2400` decoupling (both survive; stale x60/x300 +
>   1/12000 comments refreshed to x600 / 1/24000).
> - **Language** (`build_text_arc.py`): i18n de-clobber drops SV tags byte-identical to base-game Text_EN (they were
>   overriding non-English base text = the "cannot change language" Steam defect). **Integration hardened the
>   DIRECT-RUN path**: when `SVC_BASE_TEXT_EN` + 4th arg are both absent, `build_text_arc.py` now self-resolves the
>   base Text_EN.arc from the Steam install (doctor.sh discovery), warns loudly, falls back only if truly absent;
>   `SVC_NO_I18N_DECLOBBER=1` still the kill switch.
> - **Earthfury cd regression (Anapaest ruling)** FIXED in integration (`f1d53af`): player-cast `pcsafe\earthfury_ring`
>   was 16.0 in build37-dev vs 5.0 in build36a. TRACE-PROVEN root cause: `skill_quality` (registry module) re-runs the
>   castability wave during `run_registry`, minting the pcsafe clone from the still-16.0 plain BEFORE the deferred
>   `run_registry_gates` phase where A4 lowers it; the idempotent monolith wave then preserved the stale 16.0. A4
>   (`_apply_flashpowder_rework`) now also forces the pcsafe clone to 5.0 (guarded). Sole affected skill (Flame
>   Nova/Flash Powder have no special anim -> never pcsafe-cloned). **Confirming gate: next full DB build must show
>   `pcsafe\earthfury_ring` skillCooldownTime == 5.0.**
> - **Workshop description**: `docs/WORKSHOP_DESCRIPTION.bbcode` merged (already pushed LIVE to Steam as metadata-only).
> **RESIDUALS (open, recorded not fixed):**
> - **Storm UI slot25** -> `drxspellbreaker_spellshock2.dbr` is a PRE-EXISTING SV-ORIGINAL dead reference (present in
>   098i; the referenced skill never existed). DOCUMENTED, NOT TOUCHED - needs Will's design call (invent the skill,
>   repoint, or accept the harmless phantom button). SV-original, so out of a safe UI pass.
> - **Enslaver residual**: the `limit=1` cap is per-pool-per-trigger (structural). Two INDEPENDENT spawn points
>   surfacing an Enslaver close enough to fight together has no engine global cap; the /10 frequency cut makes it a
>   ~once-in-hundreds-of-acts event (also ~100x rarer cross-field). Endless-Hunt stalker (`toxeus_suite`) had the SAME
>   latent per-trigger-duplicate defect (Hades-only, rarer, UNSHIPPED b37) - **FIXED + BUILT+VERIFIED (build38a)**:
>   `_sweep_inject_legendary_stalker` now stamps per-slot `limit%d=_LS_SLOT_LIMIT`(=1) on the Hunt's name slot
>   (mirrors the Enslaver v2 cap) + `_verify_legendary_stalker_sweep` asserts weight==1 / limit==1 / p_slot<=1/2400
>   on EVERY stalker slot, fail-loud on any miss. Full DB build GREEN (build38a, HEAD `2073fe6`): the apply-time gate
>   asserted the cap LIVE on all 345/345 Hades pools; record-diff vs build38-dev = 345 CHANGED, each ONLY the Hunt slot
>   gaining `limit=1`, ZERO unexplained, 0 collateral. See BUILD38A GATE RECORD below.
> - **Language in-game spot-check = HARD pre-Steam gate**: the de-clobber restores ~93% localization by construction,
>   but an actual in-game language-switch test on a real non-English client MUST pass before any Steam push touching
>   Text.arc. Also FAILBOAT debug junk (4 rewording tags, English-VISIBLE today) recommended for a follow-up cleanup.
> - **Will tour checks** (in-game, cannot be gate-verified here): damage numbers appear on normal/elemental/DoT hits;
>   the 8 repointed mastery icons + Dream background render (no black pane, no missing icons); Earth Rupture chain
>   shows ONE Rupture with the reflowed layout. Screenshots requested.
>
> 🧪 **BUILD40 GATE RECORD (2026-07-14, main HEAD `32ea0e8` + this BACKLOG commit) - FULL coupled canonical + TESTHUB
> build GREEN; 12 b40-integ lanes (b41-b53 minus b51 docs-only) at `d8485fe` + the warden P1 fix at `32ea0e8`.** First
> build to ship the b41/b42/b43/b45/b46/b47 CANONICAL map changes + b48 established returns (canonical rebuild since
> build36a); DB carries b42 chests/nova + b43 arena/Aithon + b49 enslaver/hunt + b50 pet-white + b52 Dagon + b53 orb.
> Staged to `work/` + `local/`, NOT deployed; canonical Steam build36a stays LIVE; DEV deploy pending a TQ-exit window.
> **ARTIFACT MD5s:** arz `b33c5a447f3a8ca652c14f78d4ad1dd4` (55,351,206 B, 51,029 records = build39 51,015 + 14) -
> SUPERSEDES build39 `5bf7dac2`; Text.arc `c910da653f23ff84598b69833854d9db` (87,555 B) - SUPERSEDES `e1b73e05`;
> Quests.arc `37cf867f3550f5031dba5cb1cf31f30f` (194,801 B) - SUPERSEDES `7655f17e`; canonical Levels
> `9981085b78f1600cc0b31c3bec4cfd92` (688,691,745 B, `local/Levels_merged.arc`) - SUPERSEDES build36a `60a62880`
> (FIRST canonical rebuild since build36a); TESTHUB Levels `d4965d298ee308a4e31ffd39802ce404` (688,677,830 B,
> `local/Levels_merged_TESTHUB.arc`) - SUPERSEDES build39 `4fcc058c`. Baselines: `baseline_build39.arz` = build39 arz
> `5bf7dac2`; `baseline_canonical_b39.arc` = build36a canonical `60a62880`.
> **DB BUILD** (PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1): arz written (51,029 records); registry **13 modules order
> `b82195e9551a`** (was 12 `4c688f58`; +bossarena b43 at pos 9/13); RELEASE drops (66% Hero/Quest, 25% Boss);
> `run_registry_verifies` GREEN (4 verify hooks skill_quality + toxeus_suite + damage_display + boss_skill_fix all OK;
> boss_skill_fix roster `um_*_99` clean of level-0 specials, all enables survived finalization); golden Occult/Hunting
> PASS (35 waived). Collision gate: 2 records LATER-wins (legal registry semantics, logged), tags clean.
> **WARDEN P1 FIX (C-RES-DBR-1, `32ea0e8`):** `bossarena.py` scrubs `ember_satyr_warden_55.lootLowerBodyItem1` (the 3
> dangling `{N,E,L}_SatyrBrute` leg-loot refs, no explicit dtype per the cloned-record law). Fresh-arz probe: warden
> record **0 unresolved .dbr fields** (was 3); `contracts_resources` **1 P1 -> 0 P1**. Zero gameplay change (slot
> dropped nothing, same as the base donor).
> **RECORD-DIFF AUDIT** (`baseline_build39` `5bf7dac2` vs new `b33c5a44`): **14 ADDED / 0 REMOVED / 1035 MODIFIED, ZERO
> unexplained.** 14 ADDED = `ember_satyr_warden_55` (b43) + `svc_{charon,dorus,ephialtes,tantalus}_chest` (b42) +
> `aithon_embercrown_soul_{n,e,l}` (b43) + `svc_testhub_return_{bossarena,garden,secret,sparta,uber}` (b48) +
> `ephialtes_dread_nova` (b42). 1035 MODIFIED bucket 100% to lanes: **990** b49 undead+hades pool sweeps (273 enslaver +
> 345 hunt + breadth-restrict), **18** b50 pet-white nameplates, **13** b42/b43/b47 boss records, **6** b49
> shadowstalker rig, **3** b43 arena portals, **3** item/loot, **1** boss_skill_fix, **1** b52 dagon.
> **TEXT** i18n de-clobber ENABLED (17,541 base Text_EN tags): dropped **10,600** SV tags byte-identical to base;
> `validate_tags` PASS (all **321** referenced mod tags + **367** authoritative tags resolve in Text.arc; new b52 Dagon
> `tagSVCMonsterDagon`, b47 Kroisos, b43 Aithon tags resolve); golden A7 PASS (41 waived, 0 other); 2 pre-existing base
> monster-name WARN (`tagNewMonster66/46`, non-blocking backlog).
> **QUESTS** (`build_quest_files`, exit 0): quest-record contract PASS (**107** entry_type==3 records); **25** hub
> boat-dialog triggers + TESTHUB portal rig (7 hub + 2 return ports) appended to the always-loaded `sv_commonmechanics`
> refire step (registry law: no new QUESTS-section registration -> map 256-window parity intact).
> **CANONICAL MAP** (`SVC_TEST_HUB` unset -> `Levels_merged.arc`): mapdiff vs `baseline_canonical_b39` **PASS** - section
> order identical, QUESTS(0x1b) byte-identical (11,460 B, **256-window parity**), navmesh(0x0b) **0 changed**
> (byte-identical), 0 level add/remove, **18** intended blobs (b43 boss_arena, b47 Medea_TempleUG x2, b45 ThebesOptTombA,
> b41 HadesPalace/Styx/Judgment/Elysian/GardenofMerchants/DarkForestEnter, b48 established returns); 2282 levels, 0 bad
> offsets/magic/zero-ints. The b48 round-3 established returns (Garden/Secret/Uber/Sparta) are a deliberate CANONICAL
> warden-mute bugfix (see `docs/reports/b48_sparta_mute_fix.md`) - hence the canonical rebuild.
> **TESTHUB MAP** (`SVC_TEST_HUB=1` -> `Levels_merged_TESTHUB.arc`): mapdiff **PASS** - **27** changed blobs (18 canonical
> + 9 hub placements: HiddenValley01 Helos plaza + 8 return landings), QUESTS 256-parity byte-identical, navmesh 0
> changed, 0 add/remove; 2282 levels, 0 bad offsets/magic/zero-ints.
> **CONTRACTS:** resources/souls/summons **0 P0/0 P1** (4904 native P2: resources 4792, summons 112, souls 0) - warden
> `C-RES-DBR-1` P1 **GONE**; map vs canonical + map vs TESTHUB each **0 P0/0 P1** (3 native P2 = pre-existing base-game
> XPack portal reciprocity) - hub travelers + boss portals resolve in the new arz.
> **DEBUG GATES:** `gate_landing_clearance` HARD (TESTHUB v2 + b41b42) **25/25 PASS, 0 DEADLY/FAIL**;
> `gate_travel_npc_invariants` **T1-T6 PASS** (0 walk-throughs canon+TESTHUB; 25 hub records 0x canonical / 1x TESTHUB;
> 5 per-area returns; cross-file map==quests==arz 25+5 records; T6 scanned both fresh arcs); `gate_traveler_responds`
> **0 mute** (G-COLLISION/WARDEN/ORPHAN/DEST PASS; 30 placed NPCs / 31 routes). In-build enslaver roaming-sweep OK (273)
> + hunt stalker-sweep OK (345) + world-chest verify OK + collision legal.
> **NOT DEPLOYED:** staged to `work/` (arz/Text/Quests) + `local/` (canonical + TESTHUB Levels); DEV deploy pending a
> TQ-exit window; TESTHUB is local-only (never uploaded to Steam); canonical build36a untouched. Canonical rebuild + QA
> required for the b48 established-return canonical change before promote.
>
> 🧪 **BUILD39-DEV GATE RECORD (2026-07-13, main HEAD `87b0cae` + this BACKLOG commit) - FULL-REGISTRY DB + Text +
> Quests + TESTHUB-map build GREEN; both b39 DEV lanes integrated (boss-skill fix + Helos hub v2).** Merges:
> `feat/b39-boss-skills` @ `95edf55` (boss_skill_fix registry module, pos 11/12) + `feat/b39-hub-v2` @ `87b0cae`
> (8 new traveler NPC records + 25 quest triggers + TESTHUB placements + WILL_TEST_GUIDE); disjoint file sets,
> 0 conflicts. Staged to `work/` + `local/` TESTHUB, NOT deployed; canonical build36a stays LIVE; DEV deploy pending
> a TQ-exit window.
> **ARTIFACT MD5s:** arz `5bf7dac29beb75757178179c363af2cf` (55,354,147 B, 51,015 records = build38a 51,007 + 8 hub) -
> SUPERSEDES build38a `6631f252`; Text.arc `e1b73e050975b63521a30062c21e009b` (87,360 B) - SUPERSEDES `dff9ad01`;
> Quests.arc `7655f17e5a5f8bf13956ef456ca10595` (194,754 B) - SUPERSEDES `838bdc3a`; TESTHUB Levels
> `4fcc058c590ab0719e224940ba0b9266` (688,686,024 B, `local/Levels_merged_TESTHUB.arc`) - SUPERSEDES `841c56cd`.
> UNCHANGED (never rebuilt): canonical Levels `60a628807c1746e7bbde14946de62107` (688,682,781 B). Baseline for the
> diff: `baseline_build38a.arz` = build38a arz `6631f252`.
> **DB BUILD** (PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1): exit 0; registry **12 modules order `4c688f58d1aa`** (was 11
> `7c74a51f6ed8`; +boss_skill_fix at 11/12); RELEASE drops (66% Hero/Quest, 25% Boss); `run_registry_verifies` GREEN
> (verify hooks skill_quality + toxeus_suite + damage_display + **boss_skill_fix** OK; `boss_skill_fix.verify` OK:
> roster `um_*_99` clean of level-0 specials, all enables survived finalization); golden Occult/Hunting PASS (35
> waived). Collision gate: 2 records (`um_toxeus_hunt_99` <- toxeus_suite+boss_skill_fix, `um_helepolis_99` <-
> diadochi+boss_skill_fix) LATER-wins (legal registry semantics, logged) = boss_skill_fix repairs skill-wiring ON TOP
> of the boss-creating modules.
> **RECORD-DIFF AUDIT** (`baseline_build38a` `6631f252` vs new `5bf7dac2`): **8 ADDED / 0 REMOVED / 10 CHANGED, ZERO
> unexplained**, 0 forbidden clobbers. 8 ADDED = hub-v2 traveler NPCs `svc_helos_trav_{devourer,vashkarr,obsidian}` +
> `svc_area_return_{uber,sparta,devourer,vashkarr,obsidian}` (all `records\quests\svc_*`, mod namespace). 10 CHANGED =
> the enumerated bosses (voranthys/helepolis/dorus/kravmoloch/gorrahk/ilsevar/toxeus_hunt/vashkarr/sarkoth/
> broodmother_99); **32 field-diffs, every field in {skillLevelN, skillNameN, specialAttack3*}** (boss_skill_fix
> skill-wiring/animation) - **0 life/damage/cost/HP/design-value drift, 0 dtype-forbidden** (programmatic allowlist
> check: 0 fields outside the set, 0 forbidden-field hits).
> **TEXT** i18n de-clobber ENABLED (17,541 base Text_EN tags loaded): dropped **10,600** SV tags byte-identical to
> base-game Text_EN; `validate_tags` PASS (all **311** referenced mod tags resolve in Text.arc); golden A7 PASS (41
> waived, 0 other); duplicate-tag gate OK. New hub-v2 tags (`tagSVCHelosToUber`="The Uber Dungeon" + `tagSVCNpcTrav*`/
> `tagSVCHelosTo*` for devourer/vashkarr/obsidian) resolve.
> **QUESTS** (`build_quest_files`, exit 0): quest-record contract PASS (**107** entry_type==3 records loadable); Helos
> traveler hub = **25 per-area boat-dialog triggers** (14 outbound + 11 returns) appended to the always-loaded
> `sv_commonmechanics` refire step (registry law: no new QUESTS-section registration); 6 area quests round-trip OK.
> **TESTHUB MAP** (`SVC_TEST_HUB=1` -> `Levels_merged_TESTHUB.arc`, canonical untouched): world01.map QUESTS section
> **255 entries** (4 SV quests spliced in-window, widowletter idx 99 -> **256-window parity intact**); 25 hub NPCs into
> Helos (hiddenvalley01) + returns into boss landings (crypt_floor1/spartacryptlevel2/boss_arena/drxbc2/...); 2282
> levels, **0 bad offsets / 0 bad magic / 0 zero-ints**.
> **CONTRACTS:** souls/summons/resources 0 P0/0 P1 (**4905** native P2, == build38a); map (NEW arz + TESTHUB Levels
> `4fcc058c`) 0 P0/0 P1 (**3** native P2 = pre-existing base-game XPack portal reciprocity) - **hub travelers + boss
> portals resolve in the new arz**.
> **GATE_TRAVEL_NPC_INVARIANTS PASS:** T1 **0 walk-throughs** (canonical + TESTHUB, SV-native baseline=3); T2 **25 hub
> records 0x canonical / 1x TESTHUB** (warden law); T5 cross-file **map==quests==arz (25 records)** + 15 label tags
> resolve; canonical byte-pure.
> **NOT DEPLOYED:** staged to `work/` (arz/Text/Quests) + `local/Levels_merged_TESTHUB.arc`; DEV deploy pending a
> TQ-exit window (Will playing build38a-dev); TESTHUB is local-only (never uploaded to Steam), canonical Steam
> build36a untouched.
>
> 🧪 **BUILD38A GATE RECORD (2026-07-13, main HEAD `2073fe6`) - DB-ONLY rebuild of the Endless-Hunt stalker
> per-slot `limit=1` cap (two-in-one-trigger fix); the ONLY delta vs build38-dev is 345 Hades pools gaining the cap.**
> Staged to `work/`, NOT deployed; canonical build36a stays LIVE.
> **ARTIFACT MD5s:** arz `6631f25219be1b8f9874c95af68755c7` (55,340,923 B) - SUPERSEDES build38-dev arz `fcd5dcab`
> in DEV staging (+1,360 B = 345 added int fields). UNCHANGED + NOT REBUILT (the fix authors no tags/quests/map):
> Text.arc `dff9ad01ec1d81064f426d9456470eaf` (87,261 B), Quests.arc `838bdc3a` (194,581 B), canonical Levels
> `60a62880` (688,682,781 B), TESTHUB Levels `841c56cd` (688,688,154 B). Baseline for the diff: `baseline_build38.arz`
> = build38-dev arz `fcd5dcab`.
> **DB BUILD** (PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1): exit 0; registry 11 modules order `7c74a51f6ed8`; RELEASE drop
> rates (66% Hero/Quest, 25% Boss); `run_registry_verifies` GREEN (verify hooks skill_quality + toxeus_suite +
> damage_display OK); golden Occult/Hunting PASS (35 waived). **STALKER APPLY-TIME GATE LIVE PASS:**
> `_verify_legendary_stalker_sweep` asserted 345 eligible Hades trash pools carry the Hunt at weight 1 + per-slot
> limit 1 (p_slot <= 1/2400, <=1 Hunt/trigger); 0 non-Hades / boss / quest / hero leaks; band [40,68,100]. Enslaver
> sweep unchanged (1224 pools; its own `limit=1` already shipped in build38-dev).
> **RECORD-DIFF AUDIT** (build38-dev `fcd5dcab` vs new `6631f252`, 51,007 records both): 0 ADDED / 0 REMOVED /
> **345 CHANGED, ZERO unexplained**, 0 clobbers. EVERY delta = one Hades stalker pool (`records\xpack\proxieshades\...`)
> whose Hunt name slot gains exactly `limitN=1` (Int); 1 field/record, 0 other fields, 0 dtype changes, 0 collateral.
> Cross-verified against the new arz (strict audit): the `limitN` index IS the Hunt's name slot
> (`um_toxeus_hunt_99`) at weight 1 on all 345; the changed-set == the FULL set of Hunt-bearing pools (345); every
> Hunt pool now carries the cap, none missed.
> **VALIDATE_TAGS** PASS: all 308 referenced mod tags + 351 authoritative tags resolve in the UNCHANGED Text.arc (new
> arz authored 0 new tags -> no Text rebuild needed/done).
> **CONTRACTS:** souls/summons/resources 0 P0/0 P1 (4905 native P2); map (new arz + TESTHUB Levels `841c56cd`) 0 P0/0
> P1 (3 native P2 = pre-existing base-game XPack portal reciprocity) - hub NPCs resolve in the new arz.
> **UNTOUCHED:** DB-only pass wrote only the arz (+ its report/tags sidecars); Text `dff9ad01`, Quests `838bdc3a`,
> canonical + TESTHUB Levels byte-identical to build38-dev (never rebuilt).
>
> 🧪 **BUILD38-DEV GATE RECORD (2026-07-13, main HEAD `39a11707`) - FULL-REGISTRY DB BUILD GREEN + de-clobbered
> Text; DB+Text ONLY (map/Quests stay build37-dev).** First full heavy build of the b38 integration (mastery UI +
> damage display + enslaver-v2 + language de-clobber + earthfury fix). Everything staged to `work/`, NOT deployed;
> canonical build36a stays LIVE.
> **ARTIFACT MD5s:** arz `fcd5dcab40359aa94b421dd8cef4b81e` (55,339,563 B), Text.arc `dff9ad01ec1d81064f426d9456470eaf`
> (87,261 B). UNCHANGED (DB+Text-only pass, verified): Quests.arc `838bdc3a` (194,581 B), TESTHUB Levels `841c56cd`
> (688,688,154 B, `local/Levels_merged_TESTHUB.arc`), canonical Levels `60a62880` (688,682,781 B). NOTE: `work/`
> staged Levels = canonical `60a62880` (pre-existing staging; TESTHUB is local-only per standing rule). Baseline for
> the diff: `baseline_build37.arz` `56d6db22` (== build37-dev arz).
> **DB BUILD** (PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1): exit 0 in 346s; registry 11 modules order `7c74a51f6ed8`;
> RELEASE drop rates (66% Hero/Quest, 25% Boss); `run_registry_verifies` post-finalization phase GREEN (verify hooks
> skill_quality + toxeus_suite + damage_display OK); pet + container-shape + summon gates GREEN; golden Occult/Hunting
> PASS (35 waived in-build, 0 other).
> **RECORD-DIFF AUDIT** (baseline build37-dev vs new arz): 0 ADDED / 0 REMOVED / 1242 CHANGED, **ZERO unexplained**,
> 0 clobbers. Every delta maps to exactly one lane: **15 MASTERY** UI records (UI/display fields ONLY - 0 design-field,
> 0 dtype changes: 8 graft-icon repoints + Earth de-dup `drxrupture`->Flame Surge / `drxrupture_flare`->Flame Arch +
> Earth col-428 reflow 4 slots [bitmapPositionY] + Dream m9 bg 2 + Nature `drx_nymph_petmodifier_rootwave`
> skillDisplayName/Desc); **1 DAMAGE** `records\xpack\game\gameengine.dbr` (+7 FontStyle STRING fields, all ADDED);
> **1 EARTHFURY** `pcsafe\earthfury_ring` `skillCooldownTime` 16.0->5.0 (RESTORES build36a canonical 5.0, fixes the
> build37-dev regression flagged in that record's OBSERVATIONS); **1225 ENSLAVER** spawn-pool records =
> `_EN_SWEEP_K` 300->600 (existing main weights x2, e.g. 3000->6000) + NEW per-slot `limitN=1` (all 1225 additions == 1;
> `um_toxeus_enslaver_99` present in both builds). Mastery design-field changes: 0; dtype changes: 0.
> **TEXT** i18n de-clobber ENABLED (17,541 base Text_EN tags loaded): dropped **10,600** SV tags byte-identical to
> base-game Text_EN; 4,414 total tags emitted. `validate_tags` PASS (all 308 referenced mod tags + 351 authoritative
> resolve); golden A7 PASS (41 waived, 0 other); duplicate-tag gate OK. SANITY-DIFF vs baseline Text `8c7229db`: 10,600
> dropped / 0 added; **every dropped tag byte-identical to base Text_EN** (0 not-in-base, 0 value-mismatch); Nature
> `x3tagSkillNatureSylvanProtection`(+Desc) resolve in base-game Text_EN.
> **CONTRACTS:** souls/summons/resources 0 P0/0 P1 (4905 native P2); map (NEW arz + TESTHUB Levels `841c56cd`) 0 P0/0
> P1 (3 native P2 = pre-existing base-game XPack portal reciprocity) - **hub NPCs resolve in the new arz**.
> **QUESTS/LEVELS UNTOUCHED:** DB+Text-only pass wrote only the arz + Text.arc; Quests `838bdc3a` + TESTHUB Levels
> `841c56cd` byte-identical to build37-dev (never rebuilt).
>
> 🧪 **BUILD37-DEV GATE RECORD (2026-07-13, main HEAD `46bf0f2`) - FIRST FULL-REGISTRY DB BUILD GREEN + TESTHUB
> map + Text + Quests.** First full-registry build after the gate-fix (relocated `skill_quality` diversity gate to a
> post-finalization `run_registry_verifies` phase; 2 HC souls added to ALLOW). Everything staged to `work/` + `local/`,
> NOT deployed; canonical build36a stays LIVE.
> **ARTIFACT MD5s:** arz `56d6db22` (55,334,381 B), Text.arc `8c7229db` (377,150 B), Quests.arc `838bdc3a`
> (194,581 B), TESTHUB Levels `841c56cd` (688,688,154 B). Canonical `Levels_merged.arc` UNCHANGED `60a62880`
> (688,682,781 B; NOT rebuilt). Baseline for the diff: `baseline_build36.arz` `63ca7cf8` (== build36a canonical arz).
> **DB BUILD** (PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1): exit 0; registry 9 modules order `7ed29402a38d`; RELOCATED
> post-finalization diversity gate GREEN (8 family skills roster-locked; HC `ringoflightning`+`melinoe_bloodboil` now
> rostered); pet gates PET-STAT-MIRROR/PET-GEAR-PARITY GREEN; internal contracts 0 P0/0 P1 (112 native P2); golden
> Occult/Hunting PASS.
> **RECORD-DIFF AUDIT** (baseline vs new arz): 124 ADDED / 0 REMOVED / 1394 CHANGED, ZERO unexplained, 0 clobbers.
> ADDED = registry bosses (neferkha/toxeus_suite/polis_vault/diadochi/four_generals) + 17 Helos-hub quest records.
> CHANGED breakdown: 1224 spawn-pool records = BL-ENSLAVER-SPAWNS `_EN_SWEEP_K` 60->300 (existing weights x5) +
> toxeus_suite Endless-Hunt hades-only sweep (345 additive `um_toxeus_hunt_99` inserts at weight 1, old=None); 125
> souls = skill_quality de-filler/roster reassignment; 21 UI = hunting_occult_ui all-8-mastery shape law; 6 bloodhound
> `dyingFxPak` + enslaver smoke FX = lane-A; remainder = H/O improvement wave. (`um_toxeus_enslaver_99` present in
> both builds, unchanged.)
> **TEXT** golden A7 guard PASS (41 waived, 0 other); duplicate-tag gate OK; 351 uber tags added; `validate_tags`
> PASS (all 308 referenced mod tags + 351 authoritative tags resolve in Text.arc).
> **QUESTS** exactly 17 Helos-hub boat-dialog triggers appended to `sv_commonmechanics.qst`; entry-diff vs build36a
> `56acee66` = ONLY `sv_commonmechanics.qst` changed (107 entries, 0 added/removed); quest-record contract PASS
> (107 loadable); world01.map QUESTS section byte-identical canonical==TESTHUB (`226461e7`, 255 entries, NO new
> registration, 256-window intact).
> **TESTHUB MAP** (SVC_TEST_HUB=1 -> `Levels_merged_TESTHUB.arc`, canonical untouched): rig NPC into Random09A;
> walk-through de-place M2 72inst/33lvl; `gate_travel_npc_invariants` T1-T6 PASS (17 hub records map==quests==arz,
> each 1x TESTHUB / 0x canonical, 0 walk-throughs); contracts map 0 P0/0 P1 (3 native P2); contracts
> souls/summons/resources 0 P0/0 P1 (4911 native P2).
> **INPUTS RESTORED** (gitignored build deps absent on machine): `reference_mods/SVAERA_customquest/Resources/
> Quests.arc` (from SVAERA workshop item 2076433374, `b786666c`) + `upstream/soulvizier_098i/Resources/XPack/
> Quests.arc` (from in-repo `third_party/soulvizier098i.zip`, `a1b8020b`).
> **OBSERVATIONS (non-blocking, for the tuning lane):** (1) pcsafe `earthfury_ring` `skillCooldownTime` is 5.0 in
> build36a and 16.0 in this build (opposite the A4 "16->5" build-log narrative; sanctioned skill-domain change,
> worth a human glance). (2) stale "x60" comment in `toxeus_suite._sweep_inject_legendary_stalker` (the Enslaver
> monolith sweep is now x300, not x60; cosmetic).
> ⛴️ **BUILD36a P0 HOTFIX SHIPPED (2026-07-12) - walk-through travel portals REMOVED (Will TRAVEL LAW).**
> Fix for the LIVE Steam breakage (item 3759792705: "walk south in Helos -> teleported to Garden of Merchants,
> no way back"). Every walk-through/proximity teleport we authored is stripped from the canonical map; ALL
> cross-area travel is now NPC boat-dialog (Helos portal-master out; per-area `svc_testhub_return` NPC / SV rift
> shrine back). Fix commit `0f08297`, tag `build36a`. **Map tooling only** (`tools/build_section_surgery.py`);
> **arz/Text/Quests SHIP UNCHANGED from build36** (return NPC record + dialog already shipped inert). Canonical
> `Levels_merged.arc` md5 `60a628807c1746e7bbde14946de62107` (was `b42be44f`, 688,682,781 B); arz `63ca7cf8` /
> Text `2af4ce38` / Quests `56acee66` reused byte-identical. Blob-diff vs build36 = EXACTLY 9 changed level
> blobs (7 portal levels + crypt_floor1 + spartacryptlevel2), 0 added/removed. Gates GREEN: navmeshes 24/24,
> seam-lattice 24/0, entrance-landing PASS, map contracts 0 P0/0 P1 (3 native P2). **STEAM: SHIPPED 2026-07-12**
> (SteamCMD "Upload complete", item 3759792705, Visibility 0/public, cached login; push-gates F9+F7 PASS after the
> whitelist below). **DEV (SoulvizierClassicDEV): map STAGED to work/; the DEV `Resources/Levels.arc` copy is
> DEFERRED while TQ.exe is running** (Will actively playing) - copy `local/Levels_merged.arc` over the DEV
> `Resources/Levels.arc` when TQ exits; NEVER kill TQ.exe.
> - **Removal inventory (20 authored teleports):** 16 walk-through GridEntrance/GridExitOneWay/map_portal_aura
>   REMOVED from INJECT_SPECS (Helos H1/R2+swirl, HV01 G1/G4+swirl, Garden G2/G3/H2/R1+swirl, vista S1/S4,
>   Secret S2/S3, maze03->Uber, catacube->Sparta) + 4 native 0x06/0x05 return doors DISABLED (SC2 REWRITE_0X06,
>   crypt APPEND_0X06, crypt REMOVE_0X05 - SV-original untouched). KEPT: Helos + Olympus portal-master NPCs,
>   rift shrines teleportshrine_gom + teleportshrineorient01. PROMOTED TESTHUB->canonical: 4 svc_testhub_return
>   NPCs (Garden/Secret/Uber/Sparta).
> - ⚠️ **PUSH-GATE WHITELIST ADDED (SHIP OPERATOR, 2026-07-12):** `tools/contracts/whitelist_quests.txt` gained
>   ONE justified entry - `QST-DOOR-UNLOCK bossarena.qst :: records/quests/portal_olympianarena1.dbr`. Removing
>   the portal left bossarena.qst's `Action_UnlockFixedItem` naming a now-unplaced door (engine name-lookup
>   no-ops; harmless, travel is NPC-based). This is the intended consequence of the P0; the alternative (Quests
>   rebuild) is barred by the ship-unchanged constraint. **FOLLOW-UP:** a future Quests.arc rebuild should drop
>   the dead unlock action from bossarena.qst, then remove this whitelist line.
> - ⚠️ **DEBUG GATE FOLLOW-UPS (out of P0 scope, per the fix commit's GATE IMPACT):** the standalone
>   `tools/debug/gate_*.py` scripts that assert the removed portals (gate_doors_hub, gate_sparta_*,
>   gate_portal_*, gate_openness_collateral, gate_portal_records_global, compare_gridentrance_0x14) +
>   gate_testhub_inert (canonical now places 4 return NPCs) must be retired/updated before they are re-run.
>   Also rename Text tags tagSVCNpcTestHubReturn/tagSVCTestHubReturnChat to drop "(Test Rig)".

> 🛠️ **BUILD36 AMENDMENT (A1-A9) - DB IMPLEMENTED + GATED GREEN (2026-07-12, `feat/build36-amendment`,
> off main `32a4967`, HEAD `5526bef`).** Nine-item final DB pass; all in `tools/apply_svc_patches.py`
> (A5 also `tools/build_svc_database.py`; A5 doc corrections in `build_quest_files.py` +
> `docs/QUEST_STATE_INJECT.md` + `docs/MODDING_PLAYBOOK.md` graveyard). Built arz + Text; the map lane
> owns the deltas below. **Verified in the built arz + full gate battery GREEN** (5 invariants, 3 pet
> gates, golem button, B-SUMMON-1, C6 Dorus, F1/F2/F3/F6, A9 render-chain w/ real art, golden w/ 5
> flash-powder waivers, `_verify_boss_orbs` NEW + negative-test, naming gate negative-test, contracts
> souls 0/summons 0P1/resources only the pre-existing `anm_dreamcopy` P1).
> **A1 ENSLAVER WARBAND + B6 MARAUDER LAW** (`_create_enslaver_warband`, built between `_create_enslaver`
>   and the roaming sweep; whitelisted in `_EN_YARD_POOLS`): Option-A championChance set-piece
>   `q_enslaver_warband` pool/proxy = 1 leader + 4 "{^r}Enslaved Shadow Marauder" champions
>   (spawnMax=5/championMin=Max=4/championChance=100, chanceToRun=100, limit_obsidianbosses [1..110]);
>   name KEPT per Will. B6: marauder buffed to the DEPLOYED demon-Toxeus block ([13000,18000,24000],
>   str480/dex660/int420, scale2.0, resists Life100/Pierce80/Phys30, KEEP dmg300/380); summon petLimit
>   12->4 (WILL_DECISIONS); leader = 2.5x = [32500,45000,60000], dmg350/500, scale2.4, CC-immune;
>   friendly soul-pet marauders match the demon ladder.
> **A2 BOSS ORBS** (`_amend_boss_loot_orbs` + `_verify_boss_orbs`, after all uber builders): 12 boss
>   records get `treasureProxyName=genericbossorb_04` (J1 Enslaver ON + J2 breadth: Blood Toxeus,
>   Vashkarr, Broodmother, Dorus, 4 Obsidian wardens, Tantalus->`um_tantalus_unbound_99` TERMINAL,
>   Mnemophage->core, Ephialtes; Charon already inherits; marauders/heroes excluded). Marauder stays
>   orb-less.
> **A3 MAKARIA** Venom Cloud `skillCooldownTime` 25->8 (`makaria_venomcloud.dbr`, edit-shared).
> **A4 ANAPAEST** Earth Fury `skillCooldownTime` 16->5 on the PLAIN `earthfury_ring.dbr` pre-castability
>   -wave so the pcsafe clone inherits 5.0 (shared x4 bruiser souls).
> **A5 ACT-5 FIX C** (arz-only): `portal_hadesscandia` += RequireNoDLC=TQA2, IT->EE teleport +=TQX4,
>   `endportal_hades` UN-gated (Victory Portal revealed for DLC owners -> Epic), redundant 2nd portal
>   +=TQX4; `fixeditemtyphonportal` untouched. + doc corrections (quest identity = md5 of FULL registry
>   path).
> **A6 SOUL WIRES** (`_wire_missing_boss_souls`): `hellflower_soul` -> `us_hellflower_37` @66 (fresh);
>   `limoslifeater_soul` -> `um_frost_36` @66 (UNCONDITIONAL REPLACE of the thin `um_frost_soul` husk).
> **A7 21 HANDCRAFTED SOULS** (`_apply_dewired_hero_handcraft`, run FIRST in `apply_all_extended_patches`):
>   owned-override table, evocative names + signature grants + amgoz downsides + per-tier itemLevel.
> **A8 OBSIDIAN BALANCE (B1-B7)**: Voranthys (12/18/25k, scale2.5, freezingbreath signature + slot
>   reshuffle, pet breath+scale); escort soul-flood fix (soul-less clones of permean+bonehallow);
>   Ilsevar (10/15/21k, scale3.0, CC-immune, soul->manual-cast `ilsevar_drainnova` clone CD16, tier 3/5/8);
>   Sarkoth (13/20/28k, regen40/70/100, scale3.0, CC-immune, `svc_sarkoth_whelp` blooddragon summons);
>   TESTHUB yard chest -> golden poolchest tier; Vashkarr (shadow-shroud via charFxPakRunningNames on the
>   monster + defensiveStun100 + scale3.0 + Wrath-of-the-Eldest enrage, stacks on C7); B7 Eldest soul
>   physres 84/114.8/140 -> 30/45/60 + flat armor + HP + -8% runspeed (Gorrahk soul same).
> **A9 EVOCATIVE-NAME RESTORATION**: `_HAND_DESIGNED_SOUL_TAGS` extended (Anapaest -> "{^F}Soul of
>   Anapaest the Dishonored", etc.); the auto-transform in `_apply_soul_naming_standard` also exempts the
>   whitelist so evocative names win end-to-end; naming gate stays green (negative-tested).
> **MAP DELTAS (hand-off to the map lane, NOT touched here):** (1) A1 place `q_enslaver_warband` at one
>   walkable shadow-touched coord (5-monster footprint, extents ~4.0); (2) A8/B5 re-verify the
>   `q_vashkarr_lone` placement density at the new scale 3.0; (3) A8/B1-B3 in-game clipping/pathing
>   check on the 3x guardians in the TESTHUB yard + Obsidian Halls. A5 is arz-only (no map change).
> **Coupled ship set:** arz + Text.arc. NOT DEPLOYED (map deltas + Steam land in the coupled wave).

> 🩸🐉 **BUILD36 CONTENT WAVE (C1-C7) - DB IMPLEMENTED (2026-07-11, `feat/build36-content-wave`,
> round 1).** Four new uber bosses + the Ereban relic + Dorus amendments + uplift picks, all DB-side
> (arz + Text; map lane owns the C1-C4 placements, already landed). Branch is off `feat/build36-fix-wave`.
> All content in `tools/apply_svc_patches.py` (one appended `_create_*` section + dispatch hooks + the
> F6 hand-designed-soul whitelist). Baseline = fix-wave HEAD `182690e`.
> **C1 TANTALUS, THE INSATIABLE** (`_create_tantalus_uberboss`): 2 forms via `actorToSpawnOnDeath`
>   (Insatiable [15/20/27k]@[52,74,90] -> Hunger Unbound [9/12/16k]), WraithLord spawn/death FX, poison
>   shroud (`toxeus_envenomweapon` initialSkillName), widened Circle of Decay (r 4.5 clone), form-2
>   shade-wave summon (`svc_tantalus_raiseshades`, lost-soul spawns), 2 Famished-Shade escorts, no-cap
>   `limit_tantalus`, reused Obsidian hoard, **S2 ONE-SUMMON soul `{^F}Soul of the Insatiable`** (Famished
>   Shade on the wraith rig, amgoz hunger downside `characterLifeRegen -3/-4.5/-6.5`, FileDescription
>   Hades, 66% Finger2 on form2 ONLY), TESTHUB yard.
> **C2 CHARON, THE UNFERRIED (Golden Bough)** (`_create_goldenbough_boss`): genuine 2-phase (Unferried
>   [22/28/34k]@[48,72,100] Charon01 -> risen giant [24/30/36k] Charon02, actorHeight 2.0), deathchill
>   cold shroud added to an empty slot on both forms, **form-2 final-kill burst via an owner-approved
>   `deathEffect` on the monster clone** (the vet byte-truth: the form-2 donor carries no effect fields;
>   monster clones are not clone-shape-gated, so the add is safe), 2 oarsman escorts, no-cap
>   `limit_goldenbough`, hoard, **THE GOLDEN BOUGH** custom Legendary amulet (guaranteed on form2),
>   **S1 cold/vitality stat soul `{^F}Soul of the Unferried`** (melinoe_bloodboil grant + drxcoldaura +
>   ravagesoftime; S1 not S2 because the CharonGhost oarsman body != the Charon02 dropper body would trip
>   the fix-wave F2 identity gate - a verifier-wins call), NO-DLC (0 xpack2/3/4), yard.
> **C3 THE MNEMOPHAGE (Pools of Mnemosyne)** (`_create_mnemophage_superboss`): 2-phase shell
>   (**overmind.tex + scale 2.5 per the cross-spec law**, [14/19/25k]@[46,68,100], the 16-slot keep/add
>   psionic kit + energy-drain + on-death void-nova) -> core "the Unremembered" (voidlash skin, [7/9.5/
>   12.5k], scale 1.8, on-death necro-nova, no soul), psionic mindshroud (`hades2_shadowcloud`), 2
>   nightmare escorts, no chest (the differentiator), **Lethe's Draught** custom Legendary caster amulet
>   (field-validity-audited), **S2 phantasm summon soul `{^F}Soul of the Mnemophage`** (Epiales rig,
>   run-speed downside), yard. FEEDS on nightmares (Ephialtes sires them).
> **C4 EPHIALTES, THE WAKING DREAD (Dread Halls)** (`_create_dreadhalls_uberboss`): SINGLE-PHASE,
>   band [58,78,97]/HP [15/20/27k], **epiales_overlord.tex + scale 2.2** (cross-spec split from the
>   Mnemophage's overmind.tex + 2.5), fear spine on Skill_AttackRadius (ixion_cry Dread Roar + Dreamstorm
>   nova + Vision of Death) + takedown chase + on-death nova, Dread Shroud (`troubleddreams` FX), 2
>   nightmare escorts, no-cap `limit_ephialtes`, hoard, **Mask of the Waking Dread** custom helm (keeps
>   the donor's visionofdeath grant), **S1 dread-sower stat soul `{^F}Soul of the Waking Dread`**
>   (Dreamstorm fear-nova grant + the load-bearing `characterManaRegenModifier -40/-55/-70` downside).
>   Ephialtes OWNS the active fear nova; the Golden Bough soul keeps only a stat trickle.
> **C5 EREBAN HEARTSTONE** (`_create_ereban_heartstone`): 3-tier weapon+shield physical/earth relic off
>   em_brute_43/45 (10% lootMisc4), petrify-on-hit + defensivePetrify capstone @5/5, 6 donor ladders
>   zeroed. **The dtype traps handled explicitly**: petrify keys + lootMisc4 chance written as FLOAT
>   (absent-on-donor fields; an INT there reads ~0 and never procs/drops).
> **C6 DORUS AMENDMENTS** (`_apply_dorus_amendments`): hold-and-drown re-theme on the built um_dorus_99
>   (rottengrasp root + Dread-Pall dreadaura + coral tsunami + slow-decay-poison touch, casts anim-blanked
>   for the royalty rig) + themed soul grant (ichthian tidal strike + fear + run-speed downside).
> **C7 UPLIFT PICKS** (`_apply_content_uplift_picks`): Vashkarr dragonfire birthright (family breath +
>   terrifying roar + 16-jet firenova death + soul reflect/fear); Sepulchral Wyrm cold tide (4 frost
>   champions freezing-breath + shatter-on-death, repointed into svc_wyrmhorde_03); Broodmother death
>   crescendo (ondeath frostnova + last-brood + cold breath, anim-kept fire->cold); Obsidian **Keeper of
>   the Wheel** jackpot warden Kravmoloch (new Boss [16/22/30k]@L74 + call-the-table summon + 5th soul,
>   name5 @ weight 4 in q_obs_warband).
> **C8 TEXT**: every new name/desc/soul-flavor tag rides the tags dict -> uber_soul_tags.txt ->
>   build_text_arc.py; the 4 hand-designed uber-soul names are whitelisted in the F6 provenance gate
>   (`_HAND_DESIGNED_SOUL_TAGS`) so they KEEP their "{^F}Soul of X" flavor (Will's ruling).
> **CONTENT-WAVE GATES (all GREEN):** boss-kit clone-shape (14 pairs incl. the decay/shadewave/mindshroud/
>   dreadshroud/coldbreath/kravmoloch-summon clones), spawn-eligibility (25 mod-authored proxies incl. the
>   4 new boss + 4 yard proxies, spawnMax-championMax>=1 + L90/97/100 <= no-cap [1..110]), soul-leak (0 -
>   every form-1/core/escort clone has its inherited Finger2 soul cleared), soul-augment (all resolve),
>   the 3 A1 pet gates (stat-mirror/gear-parity/skill-kit, 15 families incl. tantalus/mnemophage summons),
>   F2 soul-summon-identity (tantalus/mnemophage summons match their dropper mesh), F6 naming (4 hand-
>   designed souls whitelisted; kravmoloch/dorus follow the standard). Donor-existence probe
>   (`tools/debug/probe_build36_content_donors.py`) GREEN for every content donor.
> **GATES (FULL REAL BUILD, GREEN after merging the fix wave `5e2e30b`):** the fix-wave round-1 merge
>   fixed the three blockers that were flagged pre-merge (F1 conflicted-copy `legion_soul` skip; F2
>   `_SUMMON_IDENTITY_ALLOW` voranthys; activation onyxspine/steamcrawler). Full arz build exit 0 ("Done."):
>   F1 cross-wire OK; spawn-eligibility OK (25 mod-authored proxies incl. the 4 new boss + 4 yard);
>   soul-leak 0 (every form-1/core/escort clone has its inherited Finger2 soul cleared); soul-augment OK;
>   soul item-skill activation OK (1400 souls; Kravmoloch soul made stat+augment to clear the F3 Ground-
>   Smash roster gate); F3 diversity OK; F2 identity OK (15 summon families incl. tantalus/mnemophage);
>   F6 naming OK (63 OURS-path souls + 2158 SV auto-whitelisted; the 6 hand-designed evocative souls in
>   `_HAND_DESIGNED_SOUL_TAGS`); boss-kit clone-shape OK (12 pairs); MP 44 eqs '/'-free; Occult/Hunting
>   golden PASS. **Text.arc built + validate_tags PASS** (250 referenced mod tags + 266 authoritative all
>   present). **validate_render_chain PASS** (every new skin/FX/mesh resolves; 28 upstream WARN). **Contracts
>   souls/summons/resources: 0 P0 / 0 ADDED P1** (souls 0/0, summons 0/0, resources 0 P0 + the SAME 1
>   pre-existing P1 the shipped work arz carries - `anm_dreamcopy`, 5 unresolved dream-pet anim clips, a
>   pre-existing mod-record bug NOT this wave, verified identical on the shipped arz). The 3 authored
>   resource P1s my clones briefly added (inherited base-only refs) were eliminated: Charon-escort
>   `skillName7` blanked, Dorus coral tsunami uses the raw upstream skill, Broodmother coldbreath dropped
>   (the crescendo keeps its frostnova + last-brood). Coupled ship set: arz + Text.arc. NOT DEPLOYED
>   (no map/quests/steam; the C1-C4 map placements land in the coupled map wave).


> 🛠️ **BUILD36 FIX WAVE - ROUND 1 (2026-07-11, `feat/build36-fix-wave`, branched off main `31a0bce`).**
> Seven live-test fixes (F1-F7) implemented + built + all gates green + negative-tested. Built (RELEASE)
> arz md5 `07de3349dcc5b854508a610aea23584b` (55,043,244 B), Text.arc md5 `b9ecb973ae84808dab46dc38a651c9ea`
> (372,752 B). NOT deployed. Items:
> - **F1 wrong-soul matcher (Cave of Whispers "white spider drops Ararat's soul" + Siege Strider drops
>   Leveler Soul).** `wire_souls_to_monsters` verifier-v7 rule: `qualifies=(score==100) or (score>0 and
>   type_bonus>0)`. Kills all 64 cross-wires + 8 flood pools. NEW fail-loud gate `_verify_no_fuzzy_cross_wire`
>   (snapshot SV pairings pre-wire -> flag any NEW Hero/Boss/Quest drop that is neither exact nor same-family,
>   skipping amgoz git-conflict-copy junk). **Side effect (spec §4-sanctioned house pattern):** de-wiring makes
>   `create_uber_souls` newly generate the named heroes' OWN identity souls (Phantom Weaver -> `shadowhero_soul`,
>   Spider Brooding -> `blinkfang_soul`), so they drop their own soul, not Ararat's; Thunder Crawl (`um_storm_16`)
>   drops nothing; the real owner `um_ararat_36` keeps `ararat_soul`.
> - **F2 Meritamen true summon.** D22 job in `_apply_group4_summons`: `phagia_soul_{n,e,l}` ("Meritamen the
>   Shadowcaller Soul") now grants `summon_meritamen` -> a `meritamen.msh` sand-spirit with the full kit incl.
>   the friendly `shadowstalker_summon3`. Real Phagia (`um_phagia_44` -> `maenadsorceress_soul`) untouched. NEW
>   REGISTRY-SCOPED gate `_verify_soul_summon_identity` (allow-set: `voranthys`, an intentional themed cross-mesh
>   summon). Fixed the wrong `BOSS_SOULS_DESIGN.md:895` row.
> - **F3 Ground Smash de-filler.** GS kept on its 6-soul roster (Brontes/Steropes/Polyphemus/Surryln/Sow/Gorrahk);
>   camelbane -> `myrto_tremor`; all other 25 fillers -> stat-only (never another over-shared filler). Anchored
>   soul-basename matcher (kills the `beast_soul`->`foulbeast_soul` bleed + mountain-satyr hijack). Restored
>   `foulbeast_soul` -> its SV `records\skills\sv\foulbeast\foulbeast_summon_soul.dbr` (present, no port).
>   Neutralized `_guess_element` physical->GS latent default (returns None -> stat-only). NEW fail-loud gate
>   `_verify_granted_skill_diversity` (hard-fail GS off-roster + ceiling 15; WARN-list the element fillers).
> - **F4 Shadow Stalker.** `skill_shadowzap` AoE petrify 2.0-4.0 + stun 0.8-2.0 + confuse 0.5-1.5 (chance valves
>   65/45/35); dead `specialAttack2` teleport slot cleared on all 20 tiers + resist floor (~8-29%). Occult
>   exception (not golden-tracked). Edit-in-place.
> - **F5 Bloodcrow Flame Nova + Flash Powder.** `firefragmentnova` cd 8->4; Occult `drxflashpowder` cd 15->6 +
>   pierce ladders + `offensiveProjectileFumbleMin` (len-12) + duration 8; `toxeus_flashpowder` cd 20->10;
>   enemy `um_droolbog_43` repointed to base `flashpowder`. Golden gate: 5 per-field `owner_approved_overrides`
>   (Will-authorized); NEGATIVE-TESTED (mutating `drxpoisongasbomb` still fails loud -> scoped waiver proven).
> - **F6 soul naming.** 54 curated OUR-soul renames to `{^F}<Monster> Soul` (+ Xeiwang/limoslifeater SV
>   RESTORES) + an auto-transform for uncovered OURS `Soul of X` (e.g. Blood Shaman). NEW **path-based**
>   provenance gate `_verify_soul_naming` (SV-original-path souls auto-whitelisted, the winning verifier
>   correction #3; SV soul paths captured in `build_svc_database`). SV-original names (e.g. Leveler Soul) untouched.
> - **F7 small items.** (a) Storm mastery-4 panel: Skill25 moved (128,217)->(128,279) off Skill06. (b) Rupture
>   tooltip "Staff Only" -> "Staff or Bow" via `build_text_arc` `TEXT_FIX_TAGS` (single-def, dup-gate-safe).
>   (c) SOUL DESC RENDERING: `_wire_soul_desc_itemtext` wires `itemText` -> the authored DESC tag on 114 souls
>   so amgoz-style flavor text renders. (d) Dayria: `dayria_wolfsummons` ADDED to `dayria_{1,2,3}` specialAttack3
>   + registered.
> - **F1-ripple reconciliations (owned-file, since `create_uber_souls`/`uber_soul_designs.py` are never-commit
>   strays):** B-SOUL-PROC-1 level backstop (create_uber_souls' `_DIFF_SCALE` floored SOUL_DESIGNS level-1 to 0
>   on n/e -> fixed 4 item-skill + 8 augment level-0 grants); MANUAL-CAST backstop (cleared the on-attack
>   controller on the newly-generated mod-authored `summon_mountainblade` chain); foulbeast pet naked-Finger2
>   equip slot zeroed; A4 Aphiastas-zero now gracefully skips the records F1 already de-wired at the root.
> - **GATES (all green):** 5 fail-loud DB invariants + 3 pet gates + RUNEMASTER-GOLEM-BUTTON + golem/soul
>   render validators + the 4 NEW fix-wave gates (F1 cross-wire, F2 summon-identity, F3 diversity, F6 naming) +
>   Occult/Hunting golden freeze (5 waived) + in-build summons contract (B-SUMMON-1 + F2 run_contracts) all
>   PASS. NEGATIVE-TESTED all 5 (F1/F2/F3/F6 seed->SystemExit; F5 golden scoped-waiver). Contracts (with
>   `--text-arc`): **souls 0 P0/0 P1/0 P2, summons 0 P0/0 P1, resources 0 P0/1 P1** (`C-RES-ASSET-1`
>   `anm_dreamcopy` = pre-existing DRX Dream-mastery asset debt, not F1-F7) + 4896 P2 pre-existing SV/DRX debt.
> - **NOTES / open (for Will / follow-up):** (1) the F1 house-pattern new souls (`shadowhero_soul` etc.) are
>   named by `create_uber_souls` from the record name (e.g. "Shadowhero Soul"), not the monster's display
>   ("Phantom Weaver") - a naming-polish item; if Will prefers the de-wired heroes to drop NOTHING instead,
>   that needs a `create_uber_souls` filter change (not-owned). (2) 7 orphan `{^F}Soul of X` tags remain in
>   Text.arc (no soul record references them -> never render; pre-existing dead strings). (3) F5's ~9 off-theme
>   flash-powder souls + the element-filler over-shares (lifedrain 20 / venomspray 14 / etc.) are WARN-listed
>   for the standing souls quality pass, not reassigned this wave.

> 🩸🔧 **BUILD36 LANE A - ROUND 2 (2026-07-11, `feat/build36-lane-a`).** The independent vet returned
> NO_GO on round 1 (1 P2 + 2 P3 + curiosity findings). ALL fixed this round (all in `apply_svc_patches.py`):
> - **A8 GOLEM PANEL (P2, the blocker) - FIXED.** Round 1's "A8 vetted correct, no code fix needed" was
>   WRONG: the golem's `skill23` SkillButton was ORPHANED - it sat in NO mastery-10 panectrl's
>   `tabSkillButtons`, so TQ (no auto-discovery) would never show the Rune Golem on the Runemaster tree.
>   `fix_mastery_panel_buttons` only covers ingameui masteries 1-8 and lives in the parallel-owned
>   `build_svc_database.py`; Lane B's Runemaster buffs edit only menhirwall/mines (NOT the panel). Fix:
>   `_rg_wire_runemaster_panel` reconstructs BOTH base-game mastery-10 panectrl overrides (xpack2 Ragnarok-
>   tier + xpack3 Atlantis-tier, from the verified base field set - base_db is freed + the SV-0.98i-rooted
>   working db never carried the Ragnarok UI) and APPENDS `Skill23` (additive, never renumbers). Covers
>   both DLC configs, the same multi-tier pattern fix_mastery_panel_buttons uses for M1-8. NEW fail-loud
>   gate `_verify_runemaster_golem_button` (Skill23 in BOTH panes + button->summon); negative-tested
>   (`tools/debug/rg_panel_gate_negtest.py` - passes wired, FAILS on dropped button / missing pane /
>   mis-pointed button; idempotent).
> - **PYGMALION PER-TIER (P3) - FIXED.** `_relocate_pet_buffslot_summon` registered the relocated summon
>   at a FLAT level 1, so `replicate.petLimit=3;4;5` indexed to 3 on all soul tiers. New `_tier_source_level`
>   registers the summon at the SOURCE's per-tier level (replicate `skillLevel8=1;2;3` -> the n/e/l pets
>   get 1/2/3 -> petLimit 3/4/5). Threaded `tier=i+1` through `_mirror_source_skill_kit`; the same helper
>   replaces the old raw-array `_source_skill_level` at the kit-registration call (a pet is ONE creature -
>   a level ARRAY on a pet record is meaningless; now always a per-tier scalar). Verified vs the real
>   Pygmalion source (`tools/debug/tier_level_check.py`).
> - **LATENT PET-SUMMON LOSS - HARDENED.** `_relocate_pet_buffslot_summon` used to DELETE the vacated buff
>   slot unconditionally, so a pet with all 5 special slots full + a buff-slot summon would silently LOSE
>   the summon (the skill-kit gate would not catch it). Now the buff slot is deleted ONLY when the summon
>   was relocated (or already fires from an AI slot); otherwise it is KEPT so the PET-SKILL-KIT gate flags
>   it loud. No real pet hits this (all 9 relocate), so zero behaviour change on the shipped set.
> - **BLOODTOXEUS COMMENT (P3) - FIXED.** Rewrote the misleading `_create_blood_toxeus_summon` comment: it
>   claimed an svc->common gear substitution that does not happen. BUILD-ORDER-verified reality: the summon
>   reads `um_bloodtoxeus_99` (a `um_toxeus_99` clone = COMMON gear) BEFORE `_wire_blood_toxeus_loot` swaps
>   the hands to svc, so the pet mirrors the common tables directly (the vet's finding; comment-only).
> - **A5 DORUS polish (curiosity) - ADDRESSED.** (1) Removed the duplicate `skillName6=boss_conversionimmunity`
>   (the donor already registers it at `skillName16`; boss keeps immunity). (2) Swapped soul augment2 from
>   the cold `drxdeathchillaura` to the vitality/decay `drxdeathchillaura_ravagesoftime` (Ravages of Time) -
>   matches the spec's "vitality/decay drx* mod" + his corpse-king vitality sheet; a proven soul augment
>   (Blood-Toxeus soul uses it, gate-green).
> - **TRIAGED (vet-blessed acceptable, flagged for Will):** Dorus soul granted-MOVE (`itemSkillName=None` -
>   the Vashkarr "really-good stat soul" precedent; adding an active is a design escalation needing its own
>   vet), Dorus heavy-melee `attackSkillName` (donor has none -> basic weapon melee + Thunder casts; a
>   special heavy-melee risks anim-castability), Pygmalion "make it crazy" uncapped replicate (kept faithful
>   native `petLimit=3;4;5` per spec "do NOT silently add"). A6 warden is DB-only BY DESIGN (map/quests wave
>   completes it - `docs/reports/build36_laneA_map_needs.md`).
> **GATES (round 2, all GREEN):** full arz rebuild MD5 `32de31a6` (round-1 was `590deb99`; changed by
> design), Text.arc `b89bfe3e` (371,990 B). Built to scratch `local/laneA_r2/` (main `work/` untouched).
> IN-BUILD: the 5 fail-loud invariants + boss-kit clone-shape (5 pairs) + spawn-eligibility (17 proxies)
> + Occult/Hunting golden-freeze + the 3 pet gates (12 families stat-mirror + gear-parity both ways, 201
> pets skill-kit) + the NEW `RUNEMASTER-GOLEM-BUTTON` gate (Skill23 in BOTH panes) all PASS. VERIFIED IN
> THE BUILT ARZ: xpack2 panectrl 23 buttons + xpack3 25, both carry Skill23 -> `_drx_runegolem`;
> pygmalion_1/2/3 replicate in specialAttack5 at skillLevel 1/2/3; Dorus soul aug2 = ravagesoftime (n/e/l),
> um_dorus_99 skillName6 empty (dedup) + skillName16 keeps conversionimmunity. EXTERNAL: golem render-chain
> validator PASS (168 refs), A9 soul render-chain PASS (233 pets/3032 refs, 22 upstream WARN), contracts
> souls+summons+resources **0 P0 / 0 P1** (4891 P2 = pre-existing SV/DRX debt), validate_tags PASS (148 mod
> + 203 authoritative), Text duplicate-tag gate OK. NEGATIVE-TESTED: the new golem gate
> (`tools/debug/rg_panel_gate_negtest.py` - green wired; FAILS on dropped button / missing pane /
> mis-pointed button; idempotent) + the 3 pet gates (`negtest_pet_gates.py`, 12 baseline violations). Det-2x
> deferred to the phase-2 vet per the one-build cap (pipeline deterministic by construction, PYTHONHASHSEED=0;
> the new code adds no sets/unordered-dict iteration). NOT DEPLOYED.
>
> 🩸 **BUILD36 LANE A - DB CONTENT WAVE (2026-07-11, `feat/build36-lane-a`, round 1).** Eight items,
> all DB-side (arz + Text), no map/quests/steam. Reference baseline = the ref build of main @88d2b03
> (`ref_88d2b03.arz` md5 `72eacf8a`); record_diff runs vs it.
> - **A1 PET BUILDER OVERHAUL** (`apply_svc_patches._build_boss_summon` + 3 new fail-loud gates):
>   (1) 12-STAT SOURCE MIRROR - every `_build_boss_summon` pet now mirrors the source monster's
>   `characterAttackSpeed/RunSpeed/SpellCastSpeed/Dexterity/Strength/Intelligence` (+ each Modifier);
>   the 30 boss-summon pets were stuck at the Lyia archer clone (atkSpd 0.5 / DEX 81 / STR 44 / INT 17
>   = 38-56% of the hostile swing rate, near-zero scaling). (2) `_mirror_source_skill_kit` - restores
>   the dropped `specialAttack2-5` boss combat kit (skips hostile `Skill_SpawnPetMonster`) + registers
>   it. (3) STRICT source GEAR MIRROR - `_mirror_source_loadout(strict=True)` auto-derives each pet's
>   loadout from its source (svc/unique source slots get a common substitute), and non-source slots are
>   zeroed, so a pet carries EXACTLY the source's gear (Will's law). bloodtoxeus keeps its weapon;
>   Xeiwang stays gearless; the enslaver skeleton/marauder get their weapons. (4) `_fix_sv_pet_summons`
>   global relocation of buff-slot friendly summons into AI-fired slots (fixes Pygmalion/Aquardia/Dayria
>   "never summons"). THREE NEW GATES wired into the build like the 5 invariants: **PET-STAT-MIRROR**
>   (`_verify_summon_pet_parity`), **PET-GEAR-PARITY** (`_verify_summon_pet_gear`, two-way), **PET-SKILL-KIT**
>   (`_verify_summon_pet_skill_kit`, no summon in a non-AI slot, no hostile spawner on a friendly pet).
>   Negative-tested: `tools/debug/negtest_pet_gates.py` fires all 3 on the e3810219 baseline (90 stat /
>   15 gear / 12 skill violations = bloodtoxeus/enslaver/Pygmalion et al), green after fix.
> - **A2 ENSLAVER REWORK** (`_create_enslaver`): the boss is now an ALL-BLACK SKELETON on the Blood-
>   Toxeus rig (clone um_toxeus_99 -> RevenantPoison.msh + NewSkeleton_Charcoal.tex + Undead; deleted the
>   inherited green `toxeus_envenomweapon` initialSkill; attackSkillName -> toxeus_attackskill). Super-
>   strong ShadowStalker-demon marauders [5000/8500/13000] + rapid many-summon (burst 6 / cd 2 /
>   petLimit 12, summon chance 70); friendly pet-of-pet + yard pack 10; soul renamed
>   `{^F}Toxeus the Murderer, Enslaver of Souls Soul`.
> - **A3 SANGUINE TITHE** (`_create_sanguine_tithe`): the mod's 3rd custom charm - a JEWELRY blood relic
>   (life leech + vitality + %-current-life bleed, GUARANTEED 5/5 leech) off the 9 Sileni combat bodies
>   (7% lootMisc4), Demon's-Blood-donor pattern (no new art); Sileni names -> green `{^G}` via
>   build_text_arc TEXT_FIX_TAGS.
> - **A4 APHIASTAS SOUL DROP -> 0** (`_apply_aphiastas_finger2_zero`): chanceToEquipFinger2=0 on the 7
>   Aphiastas keres records (souls-only Finger2 proven), loot refs + potion recipe kept; runs before the
>   drop-forcer so it holds in test AND release.
> - **A5 PROPONTIS SUPER BOSS "Dorus, the Drowned King"** (`_create_propontis_superboss`, DB side only):
>   Boss [41,57,71] HP 13.5/18.5/24k on the questline royalty rig, ThunderClap/ball + raise-court summon;
>   Common courtier fodder + Champion royal-guard escorts; lone pool/proxy; Boss-locked hoard (reuses the
>   Obsidian Hoard chest/pool); dense S1 stat soul; TESTHUB yard. **Map placement pending -> see
>   `docs/reports/build36_laneA_map_needs.md`** (host Medea_TempleUG_Tomb01, primary WORLD (312,1.2,-8462)).
> - **A6 WARDEN SPLIT-FIX** (DB side): added the 2 singly-placed master records
>   `svc_testhub_master_helos/_cave` (reuse the same tags, no Text change) so the double-placed hub NPC
>   (byte-proven H1 mute-but-visible) is retired. **Quests trigger + map placement pending -> same report.**
> - **A7 TEXT TAGS**: every new/changed name+desc tag rides the tags dict -> uber_soul_tags.txt ->
>   `build_text_arc.py`; the Sileni `{^G}` override went through TEXT_FIX_TAGS (single-definition) to
>   avoid the duplicate-tag gate. tags invariant must pass clean.
> - **A8 RUNE GOLEM VET+FINISH**: hostile review of the pre-vet graft (main @88d2b03) = CORRECT. "mastery
>   10" IS Runemaster (base slots 1-22 are Runemaster skills), skill23 is the correct free UI slot, the
>   golem's `Skill_DefensiveGround` class + `masteryLevelRequired=None` MATCH sibling `menhirwall`, prereq
>   repointed to vanilla, render closure resolves. `validate_render_chain_golem.py` PASSES with real args.
>   No code fix needed. Minor note (in-game only): skillMaxLevel 16 vs the 20-tier pet ladder is a faithful
>   SVAERA-snapshot artifact (tiers 17-20 vestigial, harmless).
> **GATES (all GREEN, verified this round):** full arz rebuild `590deb99` (50,652 recs, vs ref@88d2b03
> `72eacf8a`) - the 5 fail-loud invariants + boss-kit clone-shape (5 pairs) + spawn-eligibility (17
> proxies) + golden-freeze all PASS; the THREE NEW pet gates PASS (12 families stat-mirror + gear-parity
> both ways, 201 pets skill-kit); det pending (single build this round). `negtest_pet_gates.py` fires all
> 3 on the e3810219 baseline (90/15/12) + PASS on the build36 arz. `validate_render_chain_golem.py` PASS
> (real args). Text.arc rebuilt from restored SV source: duplicate-tag gate OK, `validate_tags` PASS (148
> mod refs + 203 authoritative). Contracts summons+resources **0 P0 / 0 P1** (4891 P2 = pre-existing
> SV/DRX debt). Coupled ship set on the eventual wave: arz + Text (+ Quests/Levels for the A5/A6 map wave).
> **OPEN (for Will / in-game vet):** eyeball bloodtoxeus/all-pet damage after the STR/INT raw-mirror
> (may over-tune); confirm the A2 all-black skeleton renders + summon cadence; the A5 map placement +
> A6 quests/map split are separate waves; A3 jewelry relic-slot scarcity QA (fallback = weapon+jewelry);
> A2 enslaver boss keeps full Hero loot (renders geared - clear the equip tables only if Will wants a
> lean rare). Full detail: the build36 specs + `docs/reports/build36_laneA_map_needs.md`. NOT DEPLOYED.

> 🕷️ **BROODMOTHER NEST - MAP LANE PLACED (build35, 2026-07-11; tag build35).** The map lane placed
> the DB lane's broodmother-nest proxies (arz `a947e98d` + Text `3fb65c20`, both already staged in
> `work/`), per `docs/BROODMOTHER_NEST_DESIGN.md`. **This is the FIRST canonical-map content change
> since build32b** (Will-approved; intended). NEW map MD5s (det-2x reproduced byte-identical, each
> built twice): canonical `local/Levels_merged.arc` = **`391b267461bbb7e75b0f965d6e298ff7`** (was
> build34 `d5259629`); TESTHUB `local/Levels_merged_TESTHUB.arc` = **`ea928648e2ede29abe00a6e87ff4900c`**
> (was build34 `8d30ec53`). arz/Text/Quests UNCHANGED by the map lane.
> **WHAT (map hooks, `tools/build_section_surgery.py` sole-owned; svaera_plus_portals.py untouched -
> tombobs02 already routes through the INJECT_SPECS v0e branch):**
>   (1) CANONICAL SET-PIECE = `BROODNEST_SPECS` (7 proxies) APPENDED to `INJECT_SPECS`'s existing
>       tombobs02 roulette list (order-preserving -> roulette keeps its indices). Host
>       `levels/world/orient/typhonug/tombobs02.lvl` (the doc's recommended primary, the deep Act-3
>       Obsidian Halls hall the roulette already dresses). Applies to BOTH variants (canonical uses
>       INJECT_SPECS; TESTHUB layers hub extras on top).
>   (2) TESTHUB YARD = `q_yard_broodmother` APPENDED (9th entry) to `build_hub_extra_specs()`'s HV01
>       list (SVC_TEST_HUB-gated -> canonical byte-unchanged in HV01).
> **PLACEMENT MANIFEST (host level; LOCAL x,y,z; nest center local (184,192), 6-egg ring r=10u,
> floor local Y 1.20; surveyed on-mesh in ALL 3 tilesets, 100% clearance at each record's real
> placementExtents [mother 3.5u, eggs 2.5u], nearest native > extents+2u):**
>   - `q_broodmother_lone`  tombobs02  L(184.0,1.2,192.0)  WORLD(-1794,-73.8,-298)  clr all-3-set 100%, nearestNative 14.4u
>   - `q_broodnest_egg_a`   tombobs02  L(184.0,1.2,202.0)   ring N
>   - `q_broodnest_egg_b`   tombobs02  L(175.3,1.2,197.0)   ring NW
>   - `q_broodnest_egg_c`   tombobs02  L(175.3,1.2,187.0)   ring SW
>   - `q_broodnest_egg_d`   tombobs02  L(184.0,1.2,182.0)   ring S
>   - `q_broodnest_egg_e`   tombobs02  L(192.7,1.2,187.0)   ring SE
>   - `q_broodnest_egg_f`   tombobs02  L(192.7,1.2,197.0)   ring NE
>   - `q_yard_broodmother`  hiddenvalley01 (TESTHUB)  L(89.0,6.6,100.0)  42.3u from nearest yard group (obs_ilsevar)
> **ROULETTE SEPARATION (Will's >=40u no-merge rule):** the nest sits 82.0u from the corner-C
> warband edge (placementExtents 4.0) and 128.2u from corner-A; min point-to-corner-centre dCornerA
> 132.2u / dCornerC 86.0u. World corner tombobs02 = (-1978,-75,-490). Corners A local (50.4,143.6),
> C (200.4,97.6). Far past 40u -> encounters cannot merge.
> **GATES (all GREEN, both variants):** parse-back (`gate_build32_parseback.py`, extended: M10
> tombobs02 now expects the 7 broodnest appended after the 2 roulette; MYARD now +9 incl
> q_yard_broodmother) PASS on canonical (M8+M9+M10) and TESTHUB (M8+M9+M10+MYARD+RIG); MAP-REF-1
> (`run_contracts.py --only map`, both maps vs arz `a947e98d`) 0 P0/0 P1 (3 P2 = pre-existing
> base-game XPack Act3/Styx portals, not the nest); navmesh 24/24 both; groups-bindings 374/374
> both; det-2x both byte-identical. **BLOB-DIFF proof:** canonical NEW vs build34 `d5259629` = EXACTLY
> 1 level changed (tombobs02, section 0x05 only, count 580->587 = +7 set-piece); TESTHUB NEW vs
> build34 `8d30ec53` = EXACTLY 2 levels (tombobs02 0x05 580->587 set-piece + hiddenvalley01 0x05
> 230->231 = +1 yard broodmother). Every other level+section byte-identical.
> **STAGING:** the new canonical `391b2674` is STAGED into `work/SoulvizierClassic/Resources/Levels.arc`
> (the coupled ship trio is now arz `a947e98d` + Text `3fb65c20` + Levels `391b2674`; ships on the NEXT
> Steam package after Will's DEV pass, per the QA-gated ship law). Packager TESTHUB-MD5 guard state OK
> (work Levels `391b2674` != TESTHUB `ea928648` -> no abort). **NOT DEPLOYED** (no dist/ write, no
> SteamCMD, no CustomMaps copy). Deploy coupling on the eventual wave: canonical Levels + arz + Text
> ship together (the set-piece is inert without the arz records/tags, already present).


> 🧭 **STANDING RULING - IMMORTAL-THRONE CAP (Will, 2026-07-10).** The campaign stays capped at
> **Immortal Throne (Hades)** for now. Do NOT make Atlantis or anything past IT reachable. Focus is
> fine-tuning the Greece-to-Hades game. The Tartarus-arena-gates fix and the Rhodes->Atlantis entry
> cap are **PARKED** under this ruling (see the build32-ship note's Tartarus/Atlantis recon block
> below, now marked PARKED). This joins the prior "campaign ends at Hades for ALL DLC combos" rule
> (HANDOFF_LIVE_STATE §6) - DLC integration remains CANCELLED; revisit only if Will later decides to
> add the post-IT areas. Quote (Will): "lets not make atlantis or anything past immortal throne
> reachable for now and we will fine tune immortal throne then if we want to add in the other areas
> later then we can."

> 🕷️ **BROODMOTHER NEST - DB LANE IMPLEMENTED (2026-07-10, Will 'proceed with the broodmother nest
> implementation'; 7 flagged decisions DELEGATED = take each doc recommendation, amgoz1 taste, NO
> artificial caps).** The deferred apex of the N7 sepulchral-wyrm-horde chain, per
> `docs/BROODMOTHER_NEST_DESIGN.md`. Baseline = graft-lane Group 0 arz `ef52a476`. NEW arz
> **`a947e98dd97d5cd4fe5eb8eded302b37`** (det-2x reproduced byte-identical). Text COUPLED + changed:
> `6c84d66d`->**`3fb65c20`** (6 new tags). Quests/Levels UNCHANGED. record_diff vs `ef52a476` = EXACTLY
> **25 ADDED + 0 MODIFIED + 0 REMOVED**, 0 collateral.
> **RECORDS (apply_svc_patches `_create_broodmother_nest`, hooked AFTER `_create_wyrm_hordes`):**
> boss `um_broodmother_99` (Eater-of-Days `um_eaterofdays_45` derivation - D13-render+summon-proven rig;
> Boss, band [40,58,74], HP [22k,30k,40k], scale 1.9/height 2.4, cold wall Life100/Pierce60/Cold80/
> Phys30; kept the eater's anim-safe wyrm kit + Hero->Boss passives + firebreath + the brood-summon);
> the UNCAPPED hostile brood-summon `svc_broodnest_summon` (yaoguai clone, boss-kit clone-shape gated;
> burst 4 / cd 5s / petLimit 24; spawns PURE common wyrmlings `um_sepulchralwyrm_common_31` - fodder
> churn, no scale-spam); egg-cluster hatch pool `svc_broodnest_hatch` (3-6 common, champ 0);
> `limit_broodnest` (herolimit_all clone bumped to [1..110]); lone-boss pool `svc_broodmother_pool`
> (spawnMax=3/championMin=Max=2 -> 1 guaranteed mother + 2 `um_sepulchralwyrm_40` elder-worm escorts;
> LAW holds); 1 lone proxy `q_broodmother_lone` + 6 egg proxies `q_broodnest_egg_{a..f}` (all
> chanceToRun=100, no-cap limit; map lane places them, recommended host tombobs02); the SOUL chain -
> fresh manual `summon_broodmother` + `broodmother_{1,2,3}` pets via `_build_boss_summon` (NO
> itemSkillAutoController; D19 mobility + damage-sanity STRICT) PLUS the pet-of-pet brood twist
> (`summon_broodmother_wyrmlings` + `broodmother_wyrmling_{1,2,3}` on the SepulchralWyrm01 rig,
> isPetDisplayable off, petLimit 6 - the friendly broodmother pet auto-raises FRIENDLY wyrmlings,
> Enslaver precedent); soul `broodmother_soul_{n,e,l}` (svc_uber dir; cold/vitality sheet, augments
> drxcoldaura+drxdeathchillaura, weird stat defensiveFreeze 100, 66% Finger2 ONLY on the mother);
> guaranteed apex loot = tier-03 Sepulchral Scale on the mother's dedicated Misc3 slot @100%; TESTHUB
> yard `q_yard_broodmother` pool+proxy (mother + 2 escorts @100%, q_yard_ namespace, REAL records).
> **7 DECISIONS TAKEN (all doc recommendations):** (1) host tombobs02 [MAP lane; DB provides proxies];
> (2) rig = Eater-of-Days (D13-proven); (3) density = 6 clusters + petLimit 24 [crazier / no caps];
> (4) fresh summon_broodmother WITH pet-of-pet friendly wyrmling brood; (5) guaranteed tier-03 scale +
> soul, NO 4th-tier charm rung; (6) egg-sac props = FUNCTIONAL-ONLY [design says don't block; map-lane
> cosmetic follow-up if a clean mesh resolves]; (7) Tartarus/Atlantis = PARKED per the IT-cap ruling
> above [no action]. Refinements noted: the brood-summon spawns pure common wyrmlings (not the scale-
> dropping champion worms) to avoid loot-spam - the 2 guaranteed champion escorts come from the pool;
> limit_broodnest is a herolimit_all clone bumped to [1..110] (build-order-independent) rather than a
> limit_obsidianbosses clone.
> **GATES (all GREEN):** record_diff exactly 25 ADDED/0 else; boss-kit clone-shape 4 pairs OK;
> spawn-eligibility 15 proxies OK (q_broodmother_lone + q_yard_broodmother registered; mother L74 <=
> limit 110; spawnMax-championMax=1); summon-pet STRICT 0 failures (manual-cast law + damage-sanity +
> D19 + clone-shape); soul-augment + activation OK; validate_tags PASS (134 referenced mod tags);
> render-chain (A9/D5) PASS (233 pets/3032 art refs - eaterofdaysmesh + SepulchralWyrm01 + all
> summons); Occult/Hunting golden (A7) PASS; MP spawn-equation '/'-free; soul-leak 0; negtest_roaming_
> yard ALL OK (broodmother pools don't carry the Enslaver -> no whitelist needed; positive/real-arz
> PASS); negtest_container_shape ALL OK; det-2x arz `a947e98d` + Text `3fb65c20` both byte-identical.
> **MAP HANDOFF (MAP-REF-1; arz `a947e98d` must land before placements):** inject the lone proxy
> `records\drxmap\proxy\q_broodmother_lone.dbr` (the mother + 2 escorts set-piece) + 6 egg-cluster
> proxies `records\drxmap\proxy\q_broodnest_egg_{a,b,c,d,e,f}.dbr` in an OPEN >=8u-radius disc of the
> recommended host `levels/world/orient/typhonug/tombobs02.lvl` (survey each on-mesh/all-tilesets/100%
> per the M9/M10 pattern; the 6 eggs ring the mother). YARD SPOT: inject
> `records\drxmap\proxy\q_yard_broodmother.dbr` in the TESTHUB monster yard (SVC_TEST_HUB-gated). All
> are flags=0/no-0x14 q_leinth_lone-shape proxies. Coupling on eventual deploy: arz + Text ship together
> (canonical Levels unchanged until the map lane injects). NOT DEPLOYED (no dist/, no SteamCMD; map
> tools untouched).

> 🎭 **SVAERA MASTERY GRAFT (DB lane, 2026-07-10, Will approved 'yes make them').** Implementing
> `docs/SVAERA_MASTERY_COMPARISON.md` additively (soa verbal permission recorded in
> `docs/PERMISSIONS.md`). **GROUP 0 (ANM-row completion) LANDED:** `build_svc_database`
> `_complete_pc_anim_melee_rows` restores the dropped vanilla melee anim clips
> (Hew/Ensnare/Crosscut/Barrage/ThunderClap) onto the FULL dHanded/sHanded/spear rows of
> anm_malepc01.dbr + anm_femalepc.dbr at indices >15 (byte-identical to base==SVAERA clips; 'Rest'
> preserved; add-only). Unblocks the 6 half-casting melee skills (Exploding Strikes/Hail of
> Axes/Arc Attack/Chi Realignment/Shen Pao/Smoke Cloud) and is the Warfare-Slam prerequisite.
> Paired guard: the soul pcsafe universal set (`apply_svc_patches._pc_universal_special_anims`) is
> bounded at index<=15 so the >15 additions never suppress a soul's pcsafe clone (no soul
> regression if the engine's SpecialAnimRef read cap is truly 15). record-diff vs c7da07f6 =
> EXACTLY the 2 anm tables. **IN-GAME CONFIRM STILL NEEDED (per doc + MASTERY_AUDIT):** whether the
> engine reads SpecialAnimRef>15 - a melee cast test confirms; if the 15-cap is real the additions
> are inert (no regression). Groups 1 (additive skill grafts) + 2 (permissions/ruling docs) status
> tracked in the DB-lane report.

> 🚪 **PORTAL TEST RIG - MAP LANE (Model C boat-dialog NPCs) LANDED (2026-07-10, autonomous map-lane).**
> Places the DB lane's 2 rig NPC records (arz `c7da07f6`) so the flag-gated LOCAL-ONLY travel rig is now
> LIVE on the TESTHUB entry. RESOLVES the map-lane PORTAL-RIG DEFERRAL (see the yard-map-lane note below).
> MAP artifacts: canonical `local/Levels_merged.arc` = **`d5259629`** (688,684,102 B; REPRODUCED
> byte-identical -> the rig is strictly TESTHUB-only); TESTHUB `local/Levels_merged_TESTHUB.arc` =
> **`8d30ec533b19e7775a819a6a9d3c19c7`** (688,689,898 B; det-2x reproduced byte-exact), was build33
> `37f58d29`. Text/Quests/arz UNCHANGED by the map lane (the DB lane's coupled `c7da07f6`/`6c84d66d`/
> `56acee66` ship with it).
> **WHAT (map hooks - `tools/build_section_surgery.py` + `tools/svaera_plus_portals.py`, sole-owned):**
>   (1) `build_hub_extra_specs()` extended with the 7 rig placements (+ the 8 build33 yard placements kept
>       INTACT): 2 `svc_testhub_master` hub NPCs + 5 `svc_testhub_return` NPCs, all flags=0 / no-0x14 /
>       identity-rot, folded into INJECT_SPECS ONLY when SVC_TEST_HUB=1 (append-only -> canonical byte-
>       unchanged).
>   (2) GridEntrance TEST HUB **RETIRED** (Will's order: Model C, NOT the born-open B-PORTAL-1/2/3 blue-pane
>       /walkway-force-teleport/dead-return portals): `merge_hub_into_inject_specs` no longer folds
>       `build_hub_inject_specs` (kept defined+unused for reference); the swap path applies
>       `build_hub_extra_specs()[R09_KEY]` to the SV blood-cave blob. R09_KEY is EXCLUDED from the normal
>       fold (random09a is rebuilt by the swap path). **SIDE EFFECT (a fix):** retiring reverts TESTHUB
>       random09a from the pre-existing build33 AE-silkroad-blob quirk (0x0b 58226, corner/geometry
>       mismatch) BACK to the canonical SV blood-cave swap blob (0x0b 115749 byte-identical to canonical)
>       + the hub master -> the "fewer instances random09a" gate quirk is now GONE (append-only prefix).
> **PLACEMENT MANIFEST (host level; LOCAL x,y,z; WORLD x,y,z; survey vs canonical 0x0b):**
>   - `svc_testhub_master`  startingfarmland06d (AE v0x11)   L(79.5,0.8,189.5)   W(-5968.5,1.8,917.5)  3u E of canonical Almyros, clr@3.0=100%, comp0
>   - `svc_testhub_master`  random09a (SV blood-cave swap)    L(32.0,1.0,45.0)    W(6011,19,3288)       8.6u from the boat-dialog Blood-Cave landing (6018,19,3293) = the dominant blood-cave arrival, clr@3.0=100%, comp0
>   - `svc_testhub_return`  gardenofmerchants (SV-only v0e)   L(133.0,-39.0,73.0) W(1176,-39,-4001)     3u E of landing, comp1 (= the Almyros landing comp), clr@3.0=100%
>   - `svc_testhub_return`  darkforestenter (SV-only v0e)     L(27.0,1.0,30.0)    W(-2393,1,-5790)      3u E of landing, comp0, clr@3.0=100%
>   - `svc_testhub_return`  crypt_floor1 (SV-only v0e)        L(140.0,10.0,229.0) W(-2438,10,-2453)     3u S of landing, single comp, clr@3.0=96%
>   - `svc_testhub_return`  spartacryptlevel2 (SV-only v0e)   L(45.0,-1.6,42.0)   W(-5599,-1.6,-1409)   3u E of landing, comp0, clr@3.0=100%
>   - `svc_testhub_return`  boss_arena (SV-only v0e)          L(131.0,0.0,40.0)   W(-430,0,-3602)       3u E of landing (~90u off volume_startolympianarena), comp0, clr@3.0=100%
> **GATES (all GREEN):** canonical md5 == `d5259629` (byte-identical to build33); parse-back
> M8+M9+M10+MYARD+**RIG** PASS (each rig host = canonical + 1 appended flags=0 NPC, EVERY other section
> incl 0x0b/0x06/0x14 byte-identical; extended `tools/debug/gate_build32_parseback.py` with the RIG
> section + testhub-aware M8); MAP-REF-1 (`run_contracts.py --only map`, TESTHUB vs new arz) 0 P0/0 P1
> (3 P2 = the pre-existing base-game XPack Act3/Styx portals); navmesh 24/24; groups-bindings 374/374
> 0 DEAD (both variants); entrance_landing PASS; det-2x TESTHUB byte-identical (`8d30ec53`). NOTE: the
> untracked, parked `gate_doors_hub.py hubidentity` FAILs ONLY because its hardcoded hub-level whitelist
> predates the Model C rig (flags startingfarmland06d/crypt_floor1 as UNEXPECTED); every level it checks
> shows the correct +1/+8 prefix, and the parse-back RIG section proves the prefix for all 7 hosts.
> **PACKAGER:** the TESTHUB-MD5 guard hashes BOTH files at RUNTIME (no hard-coded md5), so the TESTHUB md5
> change (`4fb76084`->`8d30ec53`) needs NO packager edit; work/ staging holds canonical `d5259629` (guard
> prints OK, would ABORT if `8d30ec53` were ever staged).
> **DEPLOY COUPLING:** TESTHUB `Levels.arc` (`8d30ec53`) + arz (`c7da07f6`) + Text (`6c84d66d`) + Quests
> (`56acee66`) ship together to the DEV entry; canonical `Levels.arc` UNCHANGED.

> 🚪 **PORTAL TEST RIG - DB LANE (Model C boat-dialog NPCs) IMPLEMENTED (2026-07-10, autonomous DB-lane).**
> UNBLOCKS the map-lane PORTAL-RIG DEFERRAL + the DB-lane GROUP 2 DEFERRAL below. Baseline = build33 arz
> `e3810219`. NEW arz `c7da07f6efb8b14c27cf4a628824d133` (det-2x reproduced byte-exact). Text + Quests
> are COUPLED and changed; Levels UNCHANGED (map lane owns placements): Text `346572bb`->`6c84d66d`,
> Quests `6ff23c29`->`56acee66`. Record-diff vs `e3810219` = EXACTLY **2 ADDED + 0 MODIFIED + 0 REMOVED**,
> 0 collateral.
> **RECORDS (apply_svc_patches `_create_testhub_portal_npcs`, hooked right after `_create_helos_portal_
> master`):** 2 NPCs cloned from the proven boat-dialog donor `records\creature\npc\speaking\greece\
> knossos_boatmantoegypt.dbr` (the Almyros/Keryx shape; GreekSailor02 mesh+baseTexture inherited
> BYTE-IDENTICAL -> render-safe per the D5 law):
>   `records\quests\svc_testhub_master.dbr` (HUB portal-master; map lane places it TWICE - Helos plaza +
>     blood-cave-mouth strip) and `records\quests\svc_testhub_return.dbr` (RETURN NPC; map lane places it
>     once inside each of the 5 SV areas). Added UNCONDITIONALLY, INERT on canonical (map places neither).
> **TRIGGERS (build_quest_files `_add_testhub_portal_travel`, CHAINED onto the Helos patch in the always-
> loaded `sv_commonmechanics.qst` refire step; registry law respected - NO new QUESTS registration):**
> one `Condition_OnLevelLoad` trigger per NPC (trigger `max` bumped +2), keyed on the DISTINCT rig records
> ONLY (never canonical Almyros - no leak): HUB (svc_testhub_master) = 7 `Action_BoatDialog` ports; RETURN
> (svc_testhub_return) = 2 ports. Fail-loud ref-delta checks (hub NPC +7, return NPC +2, per-tag deltas) +
> stable round-trip. Parse-back confirms 7+2 ports, exact SIGNED coords, Almyros untouched (4 ports, 0 leak).
> **DESTINATION TABLE (all 7 landing coords SURVEYED on-mesh against canonical d5259629 0x0b navmeshes):**
>   - Garden of Merchants ( 1173,-39,-4001) GardenofMerchants.lvl  tagSVCHelosToGarden  [Almyros table, re-verified]
>   - The Secret Place    (-2396,  2,-5790) DarkForestEnter.lvl    tagSVCHelosToSecret  [re-verified]
>   - The Uber Dungeon    (-2438, 10,-2450) crypt_floor1.lvl       tagSVCHelosToUber    [re-verified]
>   - The Sparta Crypt    (-5602, -2,-1409) SpartaCryptLevel2.lvl  tagSVCHelosToSparta  [re-verified]
>   - The Boss Arena      ( -433,  0,-3602) boss_arena.lvl         tagSVCTestHubToBossArena [NEW; 0x0b-surveyed on-mesh (largest comp 1.38M cells, floorY 0), **90u off volume_startolympianarena** so boss step-in stays player-controlled]
>   - The Blood Cave      ( 6018, 19, 3293) Random09A.lvl          tagSVCTestHubToBloodCave [NEW; **RE-DERIVED** - the spec's (-168,19,2162) is ~6200u STALE (Random09A now at corner (5979,18,3243)); this is proven-band local (29.9,1,26.9)+corner, 27.6u off the jo04 shrine ghost pool, largest comp, floorY 19]
>   - Helos (Return)      (-5980,  1,  909) StartingFarmland06D.lvl tagSVCTestHubToHelos  [NEW; surveyed on-mesh, floorY 0.6]
>   RETURN NPC menu = Helos (-5980,1,909) + Blood Cave (6018,19,3293).
> **TEXT (7 NEW tags via the tags dict -> uber_soul_tags.txt -> Text.arc; the 4 Almyros labels are
> REUSED):** tagSVCNpcTestHubMaster='Waypoint Warden (Test Rig)', tagSVCTestHubMasterChat,
> tagSVCNpcTestHubReturn='Return Warden (Test Rig)', tagSVCTestHubReturnChat, tagSVCTestHubToBossArena=
> 'The Boss Arena', tagSVCTestHubToBloodCave='The Blood Cave', tagSVCTestHubToHelos='Helos (Return)'.
> **STEAM-INERTNESS (explicit mechanism):** `Action_BoatDialog` attaches its menu to the NPC ENTITY in the
> loaded level; canonical places NEITHER rig NPC, so both triggers no-op there (D3 unplaced-record
> precedent + the Almyros shape). Proven by `tools/debug/gate_testhub_portal_rig.py` part B: canonical
> `local/Levels_merged.arc` = **0 master + 0 return** placements. (The rig NPC records + triggers + tags
> DO ship inside arz+Quests+Text but are inert on Steam - the sanctioned flag model.)
> **GATES GREEN:** record-diff = 2 ADDED/0 else; validate_tags PASS (129 mod refs + 185 authoritative);
> contracts quests/souls/summons/resources **0 P0/0 P1** (4891 P2 all pre-existing base/upstream);
> render-chain gate part A (mesh GreekSailor02.msh resolvable + 1 internal shader ok + baseTexture in
> base Creatures.arc; both rig NPCs share donor art); inertness gate part B (0 canonical placements);
> roaming-yard negtest ALL OK (sweep byte-unaffected, still 1224 pools + 1 yard whitelist); in-build
> summon-pet STRICT + A9 render + A7 Occult/Hunting golden + container-loot-shape PASS; det-2x
> byte-identical (arz/Text/Quests). **NOT DEPLOYED (no dist/, no SteamCMD; map tools untouched).**
> **COUPLING on eventual deploy:** arz + Quests + Text ship together (canonical Levels unchanged).
> **HANDOFF TO MAP LANE (to make the rig live on the TESTHUB entry):** extend `build_hub_extra_specs`
> (SVC_TEST_HUB-gated) to place svc_testhub_master at Helos (~local (79.5,0.6,189.5), a few u off canonical
> Almyros) AND at the blood-cave-mouth strip (random09a flank; the HV01 monster yard is a DIFFERENT level,
> so no 40u conflict with the Random09A landing), and svc_testhub_return once inside each of Garden/Secret/
> Uber/Sparta/BossArena a few u from that area's landing coord above. Recommend RETIRING the existing
> Random09A GridEntrance hub's 5 dest pairs (spec sec 8 #7) so Will never tests the known-dead
> appended-host returns. Refresh the packager's TESTHUB-MD5 guard (it hashes at runtime, no hard-coded md5).

> 🗺️ **MONSTER TEST YARD (MAP LANE) + PORTAL-RIG DEFERRAL (2026-07-10, autonomous map-lane).**
> Couples with the DB-lane yard note below (arz `e3810219`). MAP artifacts: canonical
> `local/Levels_merged.arc` = **`d5259629`** (REPRODUCED byte-identical -> the yard change is
> strictly TESTHUB-only); TESTHUB `local/Levels_merged_TESTHUB.arc` = **`37f58d29`**
> (688,649,020 B, det-2x reproduced), was build32b `4fb76084`. Text/Quests UNCHANGED
> (`346572bb`/`6ff23c29`).
> **WHAT (map hook):** `build_section_surgery.py::build_hub_extra_specs()` (was `{}`) now returns
> the 8 monster-yard proxy placements in HiddenValley01 (Silk Road), folded into INJECT_SPECS
> ONLY when `SVC_TEST_HUB=1` (append-only after HV01's 222 base instances -> canonical HV01 byte-
> unchanged; parse-back MYARD proves 222->230, every other section incl. 0x0b navmesh byte-
> identical). Each is a flags=0 / no-0x14 proxy (the q_vashkarr_lone byte-shape). SPOT B reuses
> the existing `q_vashkarr_lone.dbr` (already placed canonical at FotA; 2nd TESTHUB placement
> needs no new record). **FINAL COORDS (re-surveyed on-mesh + clearance vs the real HV01 0x0b
> navmesh; the C obsidian pocket was re-nudged since the raw spec coords hit walls/villager):**
> a down-valley gauntlet from the blood-cave mouth (local, HV01 corner (-134,-120,2174)):
> q_yard_enslaver (23.0,17.0,33.0), q_yard_marauders (31.9,16.2,26.9), q_vashkarr_lone
> (36.0,16.0,28.5), then the OBSIDIAN WARBAND cluster Z87-95 [q_yard_obs_sarkoth (42.0,15.2,91.0),
> q_yard_obs_gorrahk (36.0,15.2,90.0), q_yard_obs_voranthys (47.0,15.4,87.0), q_yard_obs_ilsevar
> (47.0,15.2,95.0), each own guardian + 5-elite warband, mutually >=6.1u, >=9.8u off the villager],
> then q_yard_wyrm (30.0,15.2,113.0) [dFount 30u]. ALL 8: on-mesh, on-largest-component, 100%
> clear at their placementExtents, flags=0.
> **STANDING DEV TEST PATTERN (how to enable/disable the yard AND the portal rig on the DEV entry):**
> BOTH the monster yard AND the Model C portal rig ride the SAME TESTHUB map. [UPDATED 2026-07-10 by the
> portal-rig map lane: the TESTHUB map is now `8d30ec53` (was 37f58d29) and the coupled DB set is arz
> `c7da07f6` + Text `6c84d66d` + Quests `56acee66` (was arz e3810219, no Text/Quests).]
> TO ENABLE: deploy `local/Levels_merged_TESTHUB.arc` (`8d30ec53`) as the DEV entry's
> `Resources/Levels.arc` + arz `c7da07f6` as `SoulvizierClassicDEV.arz` + Text `6c84d66d` as
> `Resources/Text.arc` + Quests `56acee66` as `Resources/Quests.arc` (the four ship as a coupled set).
> YARD: walk a Custom-Quest char into HiddenValley01, out the cave mouth -> Enslaver+marauders,
> Vashkarr+2 champs, the 4 Obsidian guardians+warbands, the wyrm horde (each @100%). PORTAL RIG: at
> Helos, click the "Waypoint Warden (Test Rig)" NPC ~3u E of Almyros -> 7 ports (Garden/Secret/Uber/
> Sparta/Boss Arena/Blood Cave/Helos); in the blood cave (arrive via any hub's "Blood Cave" port ->
> world (6018,19,3293)) the same Warden stands ~8.6u away; inside each SV area a "Return Warden (Test
> Rig)" stands ~3u from where you land -> 2 ports (Helos + Blood Cave). TO DISABLE (restore canonical,
> e.g. for a co-op-safe DEV): deploy `local/Levels_merged.arc` (`d5259629`) as the DEV
> `Resources/Levels.arc` (arz/Text/Quests unchanged; the yard + rig records go inert with no map
> placing them). The yard records ship in the
> shared arz UNCONDITIONALLY but are INERT on canonical/Steam (the packager's live TESTHUB-MD5 guard
> - which hashes `local/Levels_merged_TESTHUB.arc` at runtime, no hard-coded md5 - still ABORTS on
> 37f58d29, so the yard can never reach Workshop). Tune the fight by editing the REAL monster
> records in the arz (see the DB-lane tuning table); the yard follows 1:1.
> **GATES (all GREEN, map-lane):** canonical md5==d5259629; parse-back M8+M9+M10+**MYARD** PASS;
> MAP-REF-1 = 0 P0/0 P1 on TESTHUB vs the new arz (3 P2 = pre-existing base-game XPack Act3/Styx
> portals, not the yard); navmesh 24/24; groups-bindings 374/374 (0 DEAD); det-2x TESTHUB byte-
> identical; all 8 instances on-mesh in the single HV01 tileset. `gate_doors_hub hubidentity`: the
> HV01 yard append passes (canonical is a byte-exact prefix of the +8 hub HV01); its random09a
> "fewer instances" flag is PRE-EXISTING (random09a byte-identical to the shipped build32b TESTHUB
> 4fb76084; that gate is an untracked debug tool with a stale subset assumption for random09a).
> **PORTAL RIG (Helos + blood-cave-entrance hubs): RESOLVED 2026-07-10** (was DEFERRED this build).
> The 2 hub + 5 return Model C NPCs are now PLACED on the TESTHUB entry (TESTHUB map -> `8d30ec53`) and
> the GridEntrance hub is RETIRED - see the PORTAL TEST RIG - MAP LANE note at the TOP of this file for
> the placement manifest, gates, and the random09a-blob fix. [UPDATE 2026-07-10: the DB
> footprint now EXISTS - see the PORTAL TEST RIG - DB LANE note at the TOP of this file (arz c7da07f6,
> +2 NPC records svc_testhub_master/return, boat-dialog triggers, 7 tags). The map-only `build_hub_extra_
> specs` extension to PLACE the 2 hub + 5 return NPCs is now unblocked; the destination coords are surveyed.] The portal spec's settled
> mechanism (Model C BoatDialog portal-master, the ONLY one with working returns from appended
> SV-only areas) needs +2 NPC records (`svc_testhub_master`/`svc_testhub_return`), boat-dialog
> triggers in `sv_commonmechanics.qst`, and ~5-7 Text tags - all of which the DB lane explicitly
> DEFERRED (GROUP 2; verified ABSENT from arz e3810219). Placing those NPC records would fail
> MAP-REF-1. The only map-only alternative (born-open GridEntrance) ships exactly the B-PORTAL-1/2/3
> bugs (blue-pane render, walkway force-teleport, DEAD returns from every SV area) the design is
> RETIRING, so it is not a valid deliverable. Will ALREADY has working Helos->SV forward travel via
> the canonical Almyros/portal_master_helos BoatDialog NPC (4 dests), and the existing Random09A
> GridEntrance hub (5 dests, LEFT untouched) covers rough forward walk-testing. TO UNBLOCK: run a
> coordinated portal wave = DB lane builds the 2 NPC records + boat-dialog triggers + tags, THEN the
> map lane places the 2 hub NPCs + 5 return NPCs (Model C) per PORTAL spec sections 1-3. This is a
> map-only-code change here (`build_hub_extra_specs` extension) once those records exist.

> 🧪 **MONSTER TEST YARD (DB LANE) + WRAITHLORD RE-ENABLE (2026-07-10, autonomous DB-lane).**
> Baseline = shipped build32b arz `e27dd1cb`. NEW arz `e3810219379c6d1d809a470d889007ba`
> (det-2x reproduced byte-exact: build1==build2==build3-scratch). Text/Quests/Levels UNCHANGED
> (zero new tags -> Text stays `346572bb`, no coupling). Record-diff vs `e27dd1cb` = EXACTLY
> 13 ADDED + 20 MODIFIED + 0 REMOVED, 0 collateral.
> **GROUP 1 = TEST YARD (apply_svc_patches `_create_test_yard`, hooked between `_create_enslaver`
> and the roaming sweep):** 6 new ProxyPools + 7 new Proxies under `records\drxmap\proxy\` (the
> q_leinth_lone "lone" pattern), ALL pointing at the REAL shipped monster records (never clones),
> so tuning those records tunes the yard fight 1:1. Added UNCONDITIONALLY to the arz but INERT (the
> canonical/Steam map references none; ONLY the TESTHUB map's build_hub_extra_specs [MAP LANE] places
> the proxies). Records: `q_yard_enslaver` (pool name1-3=um_toxeus_enslaver_99 @100, spawn 1/champ 0
> -> boss @100%; he auto-bursts his own marauder summon petLimit8 in-fight), `q_yard_marauders`
> (name1-4=um_enslaver_marauder_99, spawn 3-4/champ 0 -> pack @100%), `q_yard_obs_{sarkoth,gorrahk,
> voranthys,ilsevar}` (name1-3=the ONE guardian, spawnMin=Max=6 + championMin=Max=5 -> 6-5=1
> guaranteed guardian + the 5-elite q_obs_warband set; each corner proxy also carries the
> svc_obsidianhoard_pool_0{1,2,3} accessory chest chain), `q_yard_wyrm` (proxy only; pool1 REUSES
> the shipped svc_wyrmhorde_03 -> 16-6=10 common wyrms + 4-6 champion worms). ALL proxies:
> chanceToRun=100, difficultyLimitsFile=**limit_obsidianbosses [1..110]** (REQUIRED: Enslaver L100 +
> Ilsevar L74 both exceed herolimit_all's 75 Legendary cap), difficulty_04, placementExtents 3.0
> (wyrm 2.5); preview mesh/scale copied from each real monster. **GATE WORK:** (a) precise yard
> whitelist in `_verify_roaming_sweep` (`_EN_YARD_POOLS` = the EXACT `q_yard_enslaver.dbr` pool path)
> excludes it from the swept-set derivation + a NEW bidirectional leak guard (every enslaver-bearing
> pool must be swept-OR-yard); still FAILS if the Enslaver appears >weight 1 in ANY non-yard pool.
> Negative test `tools/debug/negtest_roaming_yard.py` proves BOTH directions (weight-leak FAIL,
> pool-leak FAIL, whitelist-load-bearing FAIL, all with PASS restores) = ALL OK. (b) all 7 new yard
> proxies REGISTERED in `_MOD_AUTHORED_SPAWN_PROXIES` -> spawn-eligibility gate proves each spawns
> its main (13 total OK). **GATES GREEN:** roaming-sweep (1224 swept + 1 yard whitelisted),
> spawn-eligibility (13), boss-kit clone-shape (3, unchanged), container-loot, B-SUMMON-1, A9
> render-chain, A7 golden-freeze (Occult/Hunting intact), F2 summons-contract (0 P0/0 P1),
> validate_tags (127 mod tags resolve). **MAP-REF-1 for the map lane:** the 12 injectable proxy
> records = `records\drxmap\proxy\q_yard_{enslaver,marauders,obs_sarkoth,obs_gorrahk,obs_voranthys,
> obs_ilsevar,wyrm}.dbr` + REUSE the existing `q_vashkarr_lone.dbr` for SPOT B (no new record).
> **GROUP 3 = WRAITHLORD SKELLY RE-ENABLE (build_svc_database `apply_mastery_wave2_boosts`, Spirit
> section):** dropped the `xxx` disable prefix on wraithlord_01..20 skillName15/16 (drx_lichskill_
> skellysummon2/3), re-enabling the Liche King's signature skeleton summon (chain resolves:
> Skill_AttackProjectileSpawnPet -> drx_skelly_01..20, rev2skelly.msh). SURGICAL: skillLevel ladders
> UNTOUCHED (original ramp kept); the redundant soulblight double-slot (skillName4+14) KEPT (dropping
> a duplicate = a slot removal, forbidden without Will's per-item OK). Spirit is slot 8 = OUTSIDE the
> Occult(5)/Hunting(6) golden freeze. REVERTIBLE before the next Steam ship (re-add `xxx`) if his
> in-game pet-cap test shows the capstone over-summons.
> **GROUP 2 = PORTAL RIG DB: DEFERRED (not implemented).** [SUPERSEDED 2026-07-10: IMPLEMENTED in a
> dedicated portal wave - see the PORTAL TEST RIG - DB LANE note at the TOP of this file.] NOT map-only (Model C needs +2 NPC records
> + boat-dialog triggers in build_quest_files + ~5-7 Text tags), but it is a SEPARATE portal lane's
> feature (the yard spec reserves the portal strips for that lane); building its DB footprint in these
> shared files would collide. Also gated on the map lane's 0x0b survey of the Boss Arena landing coord
> (3 derived coords) + the keep-vs-remove GridEntrance-hub decision. A working portal-master (Almyros,
> 4 SV destinations) ALREADY ships canonical. Footprint handed off for a coordinated portal wave.
> **NOT DEPLOYED anywhere (DB lane; no dist/, no SteamCMD).** Coupling on eventual deploy: arz-only
> (no Text/Quests/Levels change from these two groups).

> 🚢 **BUILD32 SHIPPED TO STEAM + VERIFIED (2026-07-10, main session, tag `build32-ship` @ 3401852).**
> Payload fresh-download byte-verified 4/4: arz e27dd1cb / Text 346572bb / Levels d5259629
> (build32b) / Quests 6ff23c29. F9 dist==work 4/4 + F7 contracts on dist 0P0/0P1. Description
> sixth-update entry live (7954 chars). DEV entry = full coupled build32 set (arz redeployed as
> SoulvizierClassicDEV.arz). Steam killed + restarted per standing rule. LIVE CONTENT: Helos
> portal-master (Almyros, 4 destinations), Vashkarr @ FotA (post-fix 50/50 dragonian escorts),
> Obsidian Halls roulette (4 corners), Enslaver of Souls roaming rare, wyrm hordes + Sepulchral
> Scale, thrown weapons + 3 supra supers, Mastery Wave 2, Long Nu manual-summon fix.
> OPEN AFTER SHIP: Will's in-game acceptance (Sarkoth cast anims statically unprovable; blood-cave
> Toxeus group-spawn from b31 still pending his eyes); deferred queue = M13b SD restore,
> portal-master Phase 2, wraithlord re-enable, golden-freeze of the 7 tuned trees post-QA,
> broodmother nest set-piece, Tartarus-gates-if-Atlantis-reachable, hoard lockedSound cosmetic.
> **DESIGN LANDED (2026-07-10, sign-off-first): docs/BROODMOTHER_NEST_DESIGN.md** covers BOTH
> deferred items. (1) Broodmother nest: full amgoz1-voice design (eaterofdays rig boss @ [40,58,74]
> 22/30/40k HP, 4-6 no-cap egg-cluster spawner ring + uncapped brood-summon petLimit 24, ONE
> summon soul, guaranteed tier-03 Sepulchral Scale loot hook; host = Act-3 tomb tombobs02 per the
> byte-verified open-floor survey; record plan + INJECT_SPEC table + gates ready for an implement
> wave). (2) Tartarus/Atlantis RECON RESOLVED: Atlantis is REACHABLE for an Atlantis-DLC owner
> (Rhodes-side Marinos boat chain in base x3mq_atlantisadventure.qst = OnLevelLoad/ConversationStart/
> BoatDialog, all CQ-satisfiable, NOT touched by the IT->Scandia/IT->EE caps which are post-Hades
> only; UNREACHABLE without the DLC), Tartarus entry portal is unlock-loaded, but the 16
> tartarus_entrance_gate01 arena gates are DEAD (no loaded opener). RECOMMEND capping the
> Rhodes->Atlantis entry the same surgical way as Scandia/EE (Quests.arc-only if x3mq idx<256);
> cheap residual checks = confirm x3mq registry idx + Marinos placement at Rhodes.
> **PARKED 2026-07-10 by Will's Immortal-Throne-cap ruling (see the STANDING RULING at the TOP of
> this file):** the campaign stays capped at Immortal Throne (Hades); do NOT make Atlantis or
> anything past IT reachable for now. The Tartarus-arena-gates fix and the Rhodes->Atlantis cap are
> both PARKED under this ruling. Revisit only if Will decides to add the other areas later.

> 🛠️ **BUILD32 FINAL-CONTENT SESSION (2026-07-10, autonomous DB-lane) - GROUPS F/E/B:**
> Baseline = HEAD e3ab0a6 (arz 27e6742 / Text cf3cb227 / Quests 6ff23c29, det-2x).
> **GROUP B = TOXEUS THE MURDERER, ENSLAVER OF SOULS (BACKLOG Enslaver, Will approved).**
> apply_svc_patches `_create_enslaver` + `_sweep_inject_roaming_rare` + `_verify_roaming_sweep`.
> A ROAMING RARE mini-boss: `um_toxeus_enslaver_99` (`{^r}Toxeus the Murderer, Enslaver of Souls`)
> DERIVED from am_deathstalker_55_ambush (the ShadowStalker.msh rig, racialProfile Demon, table-LESS
> inline anim block incl. unarmedRunAnim -> rig-safe + summon-safe; the um_toxeus_99 SP-Toxeus
> lineage rides the KIT+name since the design mandates ShadowStalker.msh which um_toxeus_99 does not
> use). Boss @ scale 2.0, charLevel [40,68,100], life [13000,18000,24000], STR/DEX/INT 480/660/420,
> kit = netherstrike + toxeus_bladestorm + lifedrain + flashpowder + lethalstrike(+mortalwound) +
> character_speedall + hostile marauder-summon + boss passives (conversionimmunity/hero_scaling/
> toxeus_passiveproperties/armor_passive/globalproperties); defensive wall = defensiveLife 100 +
> defensivePierce 80 (NO bloodwitch bleed-wall zpassive, per design). `um_enslaver_marauder_99`
> (Champion, [40,68,100], ~2x hand dmg 190/232, runSpeed 1.7, drxshadowcloakrunning_fx via
> charFxPakRunningNames, own inline anim from the clone). Boss summons them via
> `svc_enslaver_summonmarauders` (yaoguai_summonshadowstalkers clone, Skill_SpawnPetMonster, burst 3 /
> 6s cd / petLimit 8; registered with the boss-kit clone-shape invariant). **THE SWEEP:** enumerate
> ProxyPool.tpl records, keep only act-trash pools (proxies orient/egypt/greek + xpack proxieshades)
> whose basename carries NO boss/quest/hero/summon/ambush marker, whose resolvable name members are
> ALL Class=Monster, that have a free name slot (<18), and whose x60 name-weight reaches >=2400;
> multiply existing name weights x60 and append the boss at weight 1 -> p_slot <= 1/2400 per
> main-slot. `_verify_roaming_sweep` (fail-loud) RE-DERIVES the touched set from the arz and proves:
> ONLY eligible pools touched (0 boss/quest/hero), enslaver at weight 1 with p_slot <= 1/2400 in
> each, boss+marauder charLevel == [40,68,100], summon skills resolve, >=500-pool floor. SOUL
> `enslaver_soul_{n,e,l}` = 66% Finger2 MANUAL summon (summon_toxeus_enslaver via _build_boss_summon
> on the boss rig) with a PET-OF-PET: the friendly Enslaver pet's every inherited HOSTILE-summon ref
> is swapped to a friendly `svc_enslaver_petmarauders` Skill_SpawnPet (built via a 2nd
> _build_boss_summon on the marauder rig) so it raises FRIENDLY marauders, never enemies; Occult
> augments drxanatomy + drxdarklings_darkaperture; weird signature stat defensiveDisruption.
> **ARTIFACTS: arz 9265619d, Text (6 new tags, coupled).** Record-diff vs 79daa74e (post-E) = 14
> ADDED (boss / marauder / 3 souls / hostile summon / 3 marauder pets / 3 enslaver pets / summon
> skill / friendly petmarauders skill) + 1224 MODIFIED (all eligible act-trash pools, x60 + append)
> + 0 REMOVED, 0 collateral. Gates GREEN: roaming-sweep gate PASS (1224 pools, 0 dedicated
> (basename) boss/quest/hero/escort/friendly pools touched; 19 general trash pools legitimately
> contain rare low-weight hero MEMBERS per vanilla - the roaming rare walks among area heroes),
> clone-shape PASS, spawn-eligibility PASS, soul-activation PASS (1406 souls), summon-pet STRICT
> PASS (manual-cast + D19 mobility on the ShadowStalker rig), render/golden PASS, validate_tags PASS
> (127 mod tags), contracts GATE PASS (0 P1, no B record flagged), STRICT 0.
> **GROUP E = N5 THROWN WEAPONS (BACKLOG N5, Will approved all designer recs).** Two halves,
> both run in build_svc_database.main() while base_db is alive (del'd before apply_all_extended):
> (1) `_restore_thrown_weapon_drops(db, base_db)` - the base game drops roh (ranged-one-hand =
> thrown) weapons from Act1-4 monsters via loot6Name5 (static_roh_NN @ w400) + loot6Name6
> (roh_NN @ band weight) on its defaultloot tables; SV DROPPED these in its overrides. Restore
> them VERBATIM (level-matched by the same-named base twin), only into an ACTIVE loot6 slot whose
> Name5/6 are EMPTY (never clobber SV; recon proved all 198 eligible twins have empty Name5/6 +
> live loot6Chance). Fail-loud count gate: restored == eligible-skipped and >= 150; got 198/198,
> skipped 0. (2) `_add_supra_thrown_weapons(db, base_db)` - 3 Legendary supra thrown weapons
> `svc_wep_{sanguineorbit,lastword,charonstoll}` built by copying the base roh uniques that carry
> the design meshes (u_l_03=chakramofthesun01 / us_l_donarsmight=mjolnir01 / u_n_12=fingerofcharon01),
> clearing the donor's native offensive stats, and retuning to wep_spear supra conventions
> (itemLevel/lvlReq 65, Legendary, itemcost_uniquelegendary_primary, DRX trail_wep_dagger,
> augmentAllLevel 1, numRelicSlots 1, hidePrefix/Suffix) + the u_l_05/09/08 projectiles + a fresh
> thematic stat block (Sanguine=phys/bleed/leech, LastWord=phys/lightning/stun + kept
> proj_chainlightning, Charon=phys/vitality/manaburn). 3 ItemArtifactFormula `svc_thrown_*_formula`
> cloned from wep_spear_formula (kept the big affix pools + 03_act4_offense bonus; reagents 1L u_l_08
> + 1E u_e_06 + 1MI mi_l_machae; 500k/10M costs) wired into supra.dbr lootName25-27 + supra_special
> lootName26-28 @ w100. D5 mesh re-scan: all 3 supers' meshes + projectiles + trail RESOLVE.
> **ARTIFACTS: arz 79daa74e, Text (6 new tags, coupled).** Record-diff vs 674f31b4 (post-F) = 6
> ADDED (3 supra weapons + 3 formulas) + 200 MODIFIED (198 defaultloot roh restore + supra.dbr +
> supra_special.dbr) + 0 REMOVED, 0 collateral. Gates GREEN: container loot-shape contract PASS
> (restored slots valid), summon-pet/render/golden PASS, validate_tags PASS (122 mod tags),
> contracts GATE PASS (0 P1, no E record flagged), STRICT 0.
> 
> **GROUP F = N6 OBSIDIAN HALLS TREASURE ROULETTE (docs/OBSIDIAN_ROULETTE_DESIGN.md,
> all decisions locked; map-unblocking - the map lane M10 waits on the q_obs_roulette
> records):** apply_svc_patches `_create_obsidian_roulette`. FOUR guardian bosses derived
> from region natives (rig/anim-safe): `um_sarkoth_99` (from uw_as_abyssalliche_flame_42,
> LicheKing02Flame caster; kit ormenos_droptelekinesis + arena_meteor + volcanicorb trio +
> ringofflame + iceshard/squall + drxspellbreaker + ondeath_frostnova; L40/58/72 HP
> 4.5/7/10.5k), `um_gorrahk_99` (from orient_cm_gildedskeleton_27, GoldenSkeleton01;
> bladestorm + cyclops_groundsmash + cyclops_terrifyingroar + dmg/speed buffs +
> ondeath bladenova 16-knife; HP 6.5/10/15k), `um_voranthys_99` (from boss_dragonliche_57,
> DragonLich01; sepulchralwyrm_firebreath + dragonliche freeze/decomp/buffetwings + alastor
> summonarcher/warrior + aktaios_summontombguardians + ondeath_spawnskeleton + ondeath_necronova;
> HP 5/8/12k), `um_ilsevar_99` (from cm_revenantstorm_17, RevenantStorm; phantomstrike +
> kika_phantomstrike + distortionwave[xpack] + lifedrain + drxdeathchillaura +
> halimedes_terrifyingroar + ondeath_detonate; L42/60/74 HP 5.5/8.5/13k). Shared warband pool
> `q_obs_warband` (spawnMin=Max=6, championChance=100, championMin=Max=5 -> 6-5=1 guaranteed
> main = RANDOM guardian [name1..4 w25], LAW holds; nameChampion1..6 = us_abyssalliche
> flame/frost/plague_42 + um_permean_35 + em_ravager_41 + um_bonehallow_37, equal w). FOUR
> corner proxies `q_obs_roulette_{a,b,c,d}` (chanceToRun=25, pool1=warband,
> accessory1/Epic1/Legendary1 = svc_obsidianhoard_pool_0{1,2,3}, difficulty_04,
> difficultyLimitsFile=limit_obsidianbosses [1..110] no-cap clone, placementExtents 4.0).
> THREE `svc_obsidianhoard_0{1,2,3}` FixedItemContainers (clone the blood-cave mega chest
> hidden_bloodcave_chest_0{1,2,3}: container_hpalace_chestlg01.msh scale 1.4, **LockedClassification
> =Boss/50** [donor was Champion/60], goldGeneratorChance=100, below-mega loot [numSpawn *2.4/*2.8
> vs mega *3.8/*4.1] + guaranteed epic/relic loot3 slot) + 3 loot tables + 3 ProxyAccessoryPools.
> FOUR amgoz1-voice souls (66% Finger2): Sarkoth = MANUAL pcsafe typhon_meteorstorm 2/3/4
> (drxvolcanicorb/stoneskin augs); Gorrahk = MANUAL pcsafe cyclops_groundsmash 3/4/5
> (drxconcussive/onslaught); Voranthys = THE ONE SUMMON (manual summon_voranthys via
> _build_boss_summon on SepulchralWyrm01 rig, D19 mobility + damage-sanity PASS; drxcoldaura/
> deathchill augs; weird stat defensiveFreeze=100); Ilsevar = lifedrain ON-ATTACK proc
> (base_atenemy_onattack - manual-cast law binds only Skill_SpawnPet; drxphantomstrike/
> drxdistortionwave xpack augs; weird stat offensiveFearMin=2). **ARTIFACTS: arz 674f31b4,
> Text (16 new tags, coupled).** Record-diff vs baseline 27e6742 = 35 ADDED (4 guardians / 3
> chests / 3 loot / 3 acc-pools / warband pool / 4 corner proxies / 12 souls / limit / 3
> voranthys pets / summon skill) + 0 MODIFIED + 0 REMOVED, 0 collateral. ALL GATES GREEN:
> summon-pet STRICT PASS (Voranthys manual-cast, no controller), render-chain A9 PASS, golden
> A7 PASS, spawn-eligibility PASS (all 4 corners: 6-5=1 main, L74<=110), clone-shape PASS,
> soul-augment + activation PASS, validate_tags PASS (116 mod tags), contracts GATE PASS (0
> P0/0 P1; the 3 hoard chests' only P2 = openFxPakName/lockedSound refs inherited VERBATIM from
> the mega-chest donor, resolve in-game via drx/base arcs). **MAP-REF-1 for M10:** the 4 corner
> proxy records = `records\drxmap\proxy\q_obs_roulette_{a,b,c,d}.dbr` (each pool1=q_obs_warband
> + accessory chest chain); wire the 4 INJECT_SPECS + shared v0e branch per the design section 6.
>
> 🛠️ **BUILD32 SESSION cont'd (2026-07-10, autonomous DB-lane) - GROUP A + D21 P1:**
> **D21 LONG NU P1 (Will, live Steam b31 - TWO reports, ONE root cause):** 'her soul
> summons ON ATTACK instead of like a summon' + 'she does no damage when summoned'.
> RCA (byte-decoded, arz 6eb3cd6f): her souls are the SV `palai_soul_{n,e,l}`
> (itemNameTag tagSoulName471), which carried an inherited on-attack proc controller
> `base_atenemy_onattack`; build31 set itemSkillName=summon_longnu but LEFT the
> controller, so the game re-cast the summon on EVERY player hit and, with the summon
> skill's petLimit=1, re-summoned/reset her each swing -> she never landed an attack.
> The stray controller is the SINGLE cause of BOTH reports. The pet itself is
> structurally sound (nonzero hand damage 70/110/160, full leveled fire kit
> firebreath/ringofflame/nova, aggressive controller) - verified field-by-field vs the
> working bloodtoxeus pet; NOT damage-dead. FIX (apply_svc_patches `_wire_summon_soul`):
> DELETE any inherited itemSkillAutoController (absent shape, never '' per B-TOXEUS-2) so
> every summon soul is a manual pet button; no-op for the D8/D9/D13/D14/D20 siblings
> (verified controller-free). Wiring resolves LIVE (D7 precedent) -> Will's existing Long
> Nu soul self-heals on the next build. NEW GATES in validate_summon_pets: (1) MANUAL-CAST
> LAW - a soul whose itemSkillName resolves to Skill_SpawnPet* must have NO
> itemSkillAutoController (negative-tested: FAILs on the b31 arz's 3 palai souls, PASS
> post-fix); (2) DAMAGE-SANITY - a summon pet must have nonzero hand damage OR an
> offensive skill OR a support kit (battle-standard totems correctly exempt).
> **GROUP A = Q2 HELOS PORTAL-MASTER (map-unblocking):** new NPC record
> `records\quests\portal_master_helos.dbr` (apply_svc_patches `_create_helos_portal_master`,
> cloned from knossos_boatmantoegypt = the proven boat-dialog Npc shape, name 'Almyros the
> Wayfarer') + a 4-destination boat-dialog trigger (build_quest_files `_add_helos_portal_travel`,
> appended to the always-loaded sv_commonmechanics refire step - registry law, no new
> registration; ONE trigger, FOUR Action_BoatDialog actions on the one npc, base quest-8
> precedent). Destinations (world coords from the map lane PORTAL_MASTER list): Garden of
> Merchants (1173,-39,-4001), The Secret Place (-2396,2,-5790), The Uber Dungeon
> (-2438,10,-2450), The Sparta Crypt (-5602,-2,-1409). 6 new tags (name/chat + 4 menu labels).
> **MAP-LANE COUPLING (MAP-REF-1 satisfied):** the record now lands in the arz -> wire
> `PORTAL_MASTER_SPEC_PENDING` into INJECT_SPECS at startingfarmland06d local
> (76.50,0.60,189.50) on the next map build. **ARTIFACTS: arz `fbd2c6d1`, Text `6fb34430`
> (coupled - 6 new tags), Quests `6ff23c29`.** Record-diff vs Group D 6eb3cd6f = 1 ADDED
> (portal_master_helos) + 3 MODIFIED (palai souls, 1 field each) + 0 REMOVED, 0 collateral.
> ALL GATES GREEN: summon-pet STRICT 0, render PASS, golden PASS, contracts GATE PASS,
> validate_tags PASS (100 mod tags resolve), Quests contract PASS (107). PRESERVED the
> shipped Q1/Q3 Typhon unlock + Olympus herald byte-intact (separate host quest).
> **GROUP C = VASHKARR, ELDEST OF THE ANCIENTS (N4-DB, map-unblocking):**
> apply_svc_patches `_create_vashkarr`. `um_vashkarr_99` (Boss, `{^r}Vashkarr, Eldest of
> the Ancients`) derived from bm_deathlance_32 (AncientDragonian01.msh, anim-safe dragonian
> family), charLevel [38,56,71], HP [12000,16500,21000], boss wall + dragonian melee kit +
> frequent horde summon + boss_conversionimmunity/boss_scaling. Minion horde =
> `svc_vashkarr_summonhorde` (yaoguai_summonshadowstalkers clone, burst 3 / cd 6s, petLimit
> 12) spawning `svc_vashkarr_fodder` (bm_ravager_31-derived Common, laddered [38,56,71]).
> 2 full-strength Champion escorts ALWAYS: `svc_vashkarr_lance` (ravager melee) +
> `svc_vashkarr_warlock` (bs_warlock_40 caster), laddered. Proxy `q_vashkarr_lone`
> (chanceToRun=100) + pool (spawnMax=3 / championChance=100 / championMin=Max=2 -> 1 boss +
> 2 champions; spawnMax-championMax>=1 law holds), difficultyLimitsFile=herolimit_all
> (no-cap, [1..75] contains the band). STAT-ONLY soul `vashkarr_soul_{n,e,l}` ({^F}Soul of
> the Eldest, dense fire/physical ladder + fireEnchant/onslaught augments, 66% Finger2). The
> minion-summon clone is registered with the boss-kit clone-shape invariant (OK, 2 pairs).
> **ARTIFACTS: arz `968c0b6c`, Text (5 new tags, coupled).** Record-diff vs Group A fbd2c6d1
> = 10 ADDED (boss/fodder/2 escorts/proxy/pool/3 souls/horde skill) + 0 MODIFIED + 0 REMOVED,
> 0 collateral. Gates GREEN: summon-pet STRICT 0, render PASS, golden PASS, contracts PASS,
> clone-shape invariant OK, validate_tags PASS (104 mod tags). **MAP-REF-1: records land ->
> map lane injects the Random05A placement + v0e routing (M9 spec in build_section_surgery).**
> **GROUP G = N7 WYRM HORDES + SEPULCHRAL SCALE (map-unblocking):** apply_svc_patches
> `_create_wyrm_hordes`. Transforms the 6 Act-3 tomb `ug_demon_wyrmsprite_0{1,2,3}{n,t}`
> encounters into escalating sepulchral wyrm hordes. `um_sepulchralwyrm_common_31` DERIVED
> (clone of the Champion _31 -> Common, no soul drop) fills the main pool slots. 3 NEW pools
> `svc_wyrmhorde_0{1,2,3}` (cloned from the firesprite pools; the SHARED firesprite pools are
> left untouched) sized 4/8, 6/12, 8/16; tier-03 adds champion config 100/4/6 with the 4
> champion worms (16-6=10 guaranteed mains, spawnMax-championMax>=1 holds). No-cap
> `limit_wyrmhorde` (herolimit_all clone) on all 6 repointed proxies. Sepulchral Scale charm
> `svc_sepulchralscale\0{1,2,3}` (Emberscale/D10 pattern: yeti-fur ARMOR charm clone -> cold /
> frostburn / cold-slow / life per-shard ladder + GUARANTEED completion fear 2/2/3, lvlReq
> 30/44/56, RelicAnimal01 art, yeti-fur working completion table kept) + 3 loot tables, wired
> at 7% on the 4 champion worms via free lootMisc4 (D10 mechanism). **ARTIFACTS: arz
> `27e67420`, Text `cf3cb227` (2 new tags, coupled).** Record-diff vs Group C 968c0b6c = 11
> ADDED (common wyrm/3 charms/3 loot tables/limit/3 pools) + 10 MODIFIED (4 champion worms'
> charm-drop wiring + 6 proxy pool/limit repoints) + 0 REMOVED, 0 collateral. Gates GREEN:
> summon-pet STRICT 0, render PASS, golden PASS, contracts PASS, validate_tags PASS (106).
> **MAP note:** the wyrmsprite proxies are ALREADY placed in the Act-3 tombs (native
> encounters); repointing their pools makes the hordes live with NO new map injection needed.
> **REMAINING build32 groups (full specs below; verified donor recon appended):** B Enslaver,
> E N5 thrown weapons, F N6 obsidian roulette.
>
> **DEFERRED B/E/F - VERIFIED DONOR RECON (2026-07-10, for a fast follow-up):**
> - **F Obsidian:** guardian bases are `as_abyssalliche_flame_42` / `uw_as_abyssalliche_flame_42`
>   (NOT us_abyssalliche), `boss_dragonliche_57` (Voranthys); the golden-skeleton melee monster
>   (Gorrahk) is referenced by the `records\proxies orient\pools\undead\goldenskeleton_*` POOLS
>   (resolve the monster record from a pool's name1). ondeath skills resolve at `records\skills\
>   monster skills\ondeath\skills\{bladenova,frostnova}.dbr` + `...\attack_radius\ondeath_
>   {frostnova,necronova}.dbr` + `...\monster skills\ondeath_spawnskeleton.dbr` (doubled
>   `skills\skills\` variants also exist - use the single-`skills\` path). `arena_meteor` =
>   `records\skills\monster skills\attack_radius\arena_meteor.dbr`; `ormenos_droptelekinesis`
>   OK; cyclops = `records\skills\boss skills\cyclops_terrifyingroar.dbr` + pcsafe
>   `cyclops_groundsmash`. The mega-chest mesh `container_hpalace_chestlg01.msh` sits on a
>   FixedItemContainer - derive from the blood-cave mega chest RECORD. No `limit_obsidianbosses`
>   exists yet (author a herolimit_all-clone no-cap). Voranthys summon = `_build_boss_summon`
>   on SepulchralWyrm01. The Vashkarr proxy/pool + wyrmhorde pool recipes are the exact
>   templates for F's shared warband pool + 4 corner proxies; chest chain = the D10 loot-table
>   + `_ensure_record` LootRandomizerTable pattern.
> - **E Thrown:** supra tables = `records\xpack\item\loottables\arcaneformulae\supra.dbr` +
>   `supra_special.dbr` (add slots 25-27 / 26-28 @w100). Formula template =
>   `records\drxitem\supra\zrecipes\wep_spear_formula.dbr` (ItemArtifactFormula: artifactName +
>   reagent1/2/3BaseName = 1L+1E+1MI). Thrown-weapon base records live under
>   `records\item\equipmentweapon\throwingknife\` (clone for the 3 supers; avoid the fenrirsbite
>   stray mesh). Loot-restore half needs base_db + a diff of the mod-overridden
>   `c_default_*/boss_default_*/bandari_default_*` tables vs the base twins' loot6Name5/6.
> - **B Enslaver:** boss donor = `records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr`
>   (xpack path, the SP Toxeus / ShadowStalker-kin). Summon-shadowstalker donor =
>   `yaoguai_summonshadowstalkers` (Vashkarr-proven clone). toxeus_bladestorm / flashpowder /
>   lethalstrike_mortalwound all resolve. The roaming sweep (`_sweep_inject_roaming_rare`) is
>   the hard kernel: eligibility filter must EXCLUDE boss/quest/hero/escort/friendly pools;
>   pair with a `_verify_roaming_sweep` fail-loud gate (only eligible pools touched, weight-1
>   name-append, 18-slot caps respected).

> 🗺️ **BUILD32a MAP LANE (2026-07-10): M8 + M9 WIRED, gated, DEV-deployed (coupled).**
> **M8 Helos portal-master:** `PORTAL_MASTER_SPEC` LIVE in INJECT_SPECS @ startingfarmland06d
> local (76.50,0.60,189.50) (v0x11 step-6/7 path, NPC byte-shape, no 0x14). Dialog rides the
> DB lane's Quests 6ff23c29 (sv_commonmechanics refire step; COUPLED map+Quests deploy).
> **M9 Vashkarr:** `VASHKARR_SPEC` LIVE @ random05a local (24.00,1.00,31.70) - **FIRST LIVE
> USE of the 5af756c v0e SVAERA-host branch, byte-proven clean**: parse-back gate
> (tools/debug/gate_build32_parseback.py) = random05a 0x05 59->60 instances, appended
> q_vashkarr_lone flags=0 exemplar-rot, flag-aware walk to exact section+blob end, ALL other
> sections byte-identical (incl. the 0x0b navmesh, 76,438 B); farmland06d 995->996, 0x14
> byte-identical. On-mesh RE-verify vs the level's own 0x0b: spot walkable in ALL 3 tilesets
> (radius 0.4/0.6/0.8), 100% clearance in the 3.5u square (survey said 95%), set0 walkable
> cells 60,356 = survey-exact parity. **Gates:** contracts GATE PASS 0 P0/0 P1 (MAP-REF-1=0
> vs arz 27e67420), navmesh 24/24, groups-bindings 374/374 0 dead, det-2x BOTH variants.
> **MD5s: canonical `1dad265e68614ab813b5f9a0aed10286`, TESTHUB `892f8f14bd605f67d2d323af2ced6d88`**
> (build31g baseline f1d31d23 preserved at local/Levels_merged.build31g-baseline.arc).
> Per-level delta vs build31g = EXACTLY 2 blobs: random05a (+1 0x05 instance) +
> startingfarmland06d (+1 0x05 instance). DEV deploy = all four coupled artifacts (Levels +
> Quests 6ff23c29 + arz 27e67420 as SoulvizierClassicDEV.arz + Text cf3cb227; the DEV arz was
> Group-D-stale with ZERO helos/vashkarr records - MAP-REF-1 ordering at DEV required the sync).
> ~~M10 Obsidian corners STILL PENDING~~ (superseded by build32b below). Walk-test:
> (1) Helos plaza - talk to Almyros the Wayfarer, all 4 destinations; (2) FotA cave (ToTomb02
> east of Chang'an) - Vashkarr + 2 champions guard the Majestic Chest, soul drops.

> 🗺️ **BUILD32b MAP LANE (2026-07-10): M10 WIRED - build32 map COMPLETE, ship candidate.**
> DB Group F landed (6c6c0cd, arz 9265619d...): all 4 corner proxy paths byte-verified vs the
> record table (records\drxmap\proxy\q_obs_roulette_{a,b,c,d} + pools\q_obs_warband + the
> obsidianhoard chest chains). `OBS_ROULETTE_SPECS` merged into INJECT_SPECS (collision-
> guarded), v0e branch (M9-proven). **Corner-D re-verify CONFIRMED THE SURVEY FLAG:** at
> (90.8,45.6) walkable only in the radius-0.4 tileset, 71% clearance -> **NUDGED +2.0/+2.0
> within the pocket to (92.8, 1.0, 47.6)**: walkable in ALL 3 tilesets, 100% clearance, same
> flat floor as corner B. A/B/C verified 100%/all-tilesets at the surveyed spots. Parse-back
> gate extended to M10 (57 checks, both variants): tombobs02 578->580 (A@(50.4,143.6) +
> C@(200.4,97.6)), tombobs01 408->410 (B@(220.8,89.6) + D@(92.8,47.6)), all appended flags=0
> exemplar-rot, every other section byte-identical (incl. both 0x0b navmeshes). **Gates:**
> contracts GATE PASS 0 P0/0 P1 (MAP-REF-1=0 vs arz 9265619d), navmesh 24/24, groups-bindings
> 374/374 0 dead, det-2x both variants. **SHIP-CANDIDATE MD5s: canonical
> `d5259629d16e1fa8e39e7a6d59b3e57e`, TESTHUB `4fb76084a275d65682ac38426055acf6`** (baselines
> preserved: build31g f1d31d23, build32a 1dad265e). Whole-map delta byte-proven: exactly 2
> blobs vs build32a (tombobs pair), exactly 4 vs build31g (the four M8/M9/M10 hosts). DEV
> deploy = full coupled build32 set (Levels d5259629 + Quests 6ff23c29 + arz 9265619d as
> SoulvizierClassicDEV.arz + Text 346572bb). Walk-test: Act-3 Obsidian Halls (TyphonUG) -
> each visit rolls the 4 corners at 25% each for a warband + hoard chest.

> 🛠️ **BUILD32 SESSION (2026-07-10, autonomous DB-lane, Will blanket sign-off) - SHIPPED GROUPS:**
> STEP 0 det-2x reproducibility of build31-ship VERIFIED (arz `fc393741` + Text `b7251fd7`
> BOTH reproduce byte-exact from a clean HEAD rebuild, x2 - no process breach).
> **Group D = MASTERY WAVE 2** (docs/MASTERY_AUDIT_2026-07-09.md S3 Wave 2 + PART III):
> Warfare (ancestralhorn/battlestandard uptime, spectralsoldier armband path, warwind feel),
> Nature (FoN 360->180, petBonus +30%% pet-dmg/+160 prot ML1-40, defensiveConvert malus cleared,
> wolf/sylvan dangling FX), Spirit (outsider 360->120+TTL60, deathward 300->180, bonepet
> spiritbreath 'xxx' re-enable + drxplaceholder cleared [skillName6 no-op KEPT], bonescourge FX),
> Dream (timefield cleared, phantasm uptime, psionicbeam x2, mana-ladder extensions, phantomstrike
> self-slow zeroed, phantasm loot dangler), RuneMaster (mastery Life 800->1160 + Mana 0->400,
> menhiraltar cd 240->120) + Neidan (mastery Life 900->1050, terracotta petLimit ->3, deathbomb
> 33->45%%, splash attached to shenpao) as base->mod overrides. **arz `fc393741` -> `6eb3cd6f`**;
> Text UNCHANGED (`b7251fd7`, zero new tags = arz-only, NO coupling); Quests/Levels untouched.
> Record-diff = 6 ADDED (RuneMaster/Neidan overrides) + 118 MODIFIED, **0 REMOVED, 0 unbucketed**
> (WARFARE 23/NATURE 26/SPIRIT 23/DREAM 46/RUNEMASTER 2/NEIDAN 4). ALL GATES GREEN: player-anim
> PASS (40 tree skills; splash's PhantomStrike correctly an inert modifier), summon-pets PASS,
> contracts GATE:PASS, render-chain PASS (22 upstream WARN), golden-freeze Occult/Hunting intact
> (0 waived). det-2x reproducible. **RuneMaster+Neidan castability CONFIRMED already fixed by
> Wave 1 B6** (Ensnare/Flamesurge/ThunderClap/Barrage/Crosscut/Hew ported; NOT re-implemented).
> **DEFERRED (in amgoz1's spirit, honest):** wraithlord skellysummon2/3 re-enable (pet-cap
> unverifiable without a walk-test); golden-freeze tree expansion to the 7 tuned trees (post-QA
> per audit S5 - freeze after Will's walk-test, regenerating the snapshot same step).
> **REMAINING build32 groups (specs intact below):** A Q2 Helos portal-master, B Enslaver,
> C Vashkarr, E N5 thrown weapons, F N6 obsidian roulette, G N7 wyrm hordes.

> 🌙 **BUILD31 OVERNIGHT RUN (2026-07-10, autonomous per Will) - SHIPPED GROUPS:**
> Group1 mastery fixes B1-B6 (06a9a24a) -> D19 immobile-summon fix + PET-MOBILITY gate
> (95e816d3) -> Q3 instant Rhodes unlock + token path + herald NPC (arz bd6ae869 / Quests
> 3db3764c) -> Q4 bossarena/widowletter/chimera (Quests 20ff9f30, arz 754c3279) -> M15 Toxeus
> group-joins (7a59919f) -> Group2 Def/Earth/Storm boosts (3c065e70) -> Group3 D11/D12/D15/
> D16/D17/D18 (arz 3656a83f + Text b622d0d7) -> Group4 D13/D14/D20/D21 summon souls
> (**FINAL arz 0de2ce56 + Text b622d0d7 + Quests 20ff9f30**). Every group: gates + bucketed
> record-diff + commit + DEV deploy. **DEFERRED to the next session (specs intact below):**
> Group5 Q2 Helos portal-master (herald pattern proven by Q3; M8 dest table in
> build_section_surgery), Group6 Enslaver, Group7 Vashkarr, N5 thrown weapons + N6 roulette +
> N7 wyrm hordes + Mastery Wave 2 (build32). ⚠️ N5/N7 design agent output files
> (tasks/ab8a4644fa12b0169.output, tasks/a4e3cbf48ea86eff4.output) were EMPTY (0 bytes) when
> forwarded - coordinator must re-send the full design texts before implementation (the
> coordinator-locked decision summaries are in the train queue entries below).
> **MAP-LANE COUPLINGS OUTSTANDING:** (1) Q3 herald placement: wire
> OLYMPUS_RHODES_NPC_SPEC_PENDING into INJECT_SPECS (record records\quests> portal_master_olympus.dbr is IN the arz now); (2) M15: repoint the parchment demon_01_cluster
> instance to demon_01_cluster_toxeus50.dbr + REMOVE both standalone q_bloodtoxeus proxies
> (drxBC2 + parchment) or double-spawns return; (3) Q4 testquesttoopendoors deregistration.


> This is the authoritative running list of everything still broken or unfinished.
> Ordered roughly by priority. Each item: symptom (what Will saw) → likely cause →
> fix approach → which lane/files. Read docs/HANDOFF_LIVE_STATE.md first for deploy state,
> then docs/PLAYBOOK.md for how to do each kind of change.

> 🚨 **STANDING RULE (Will, 2026-07-09): NEVER REMOVE SKILLS FROM MASTERIES.** Edit fields =
> preferred; add new skills/slots = allowed; REMOVE a skill/tree slot = forbidden without Will's
> explicit per-item approval (removal candidates go on a proposal list back to Will, never into
> a build); re-enabling disabled original content = encouraged; in-record dangling-ref cleanup =
> allowed field-editing, but when in doubt treat it as a removal and ask. Full operational text
> + the Wave 1/2 compliance sweep in the header of docs/MASTERY_AUDIT_2026-07-09.md.

## 🔴 P0 - visible/blocking, confirmed in-game 2026-07-08

### B-OLYMPUS-RHODES-1 - FIX SET COMPLETE (build31g map + Q3 arz/Quests), awaiting Will's walk-test
- **MAP HALF WIRED (build31g, commit d06f334, 2026-07-09 overnight):** the herald NPC
  (portal_master_olympus, cloned from the Knossos boatman) is PLACED at OlympusFinal02
  inst[205], local (305.80,90.20,490.80) = world (1155.80,90.20,-3190.20), 4u from the locked
  xq00 portal on the Typhon plateau (navmesh-verified). Q3 (36a6212) had already shipped the
  record (arz bd6ae869) + boat-dialog quest -> world (700,41,-6466) (Quests 3db3764c) + the
  INSTANT kill-unlock trigger on the engine portal. Player path after Typhon: talk to the
  herald -> Rhodes (guaranteed), or the xq00 portal if the engine honors the kill-unlock.
  Walk-test: kill Typhon, herald dialog -> Rhodes arrival at the base game's own target.
- ORIGINAL ENTRY (history):

### (historical) B-OLYMPUS-RHODES-1 (P0 CAMPAIGN BLOCKER): no working portal after Typhon (Olympus -> Rhodes/Hades)
- **Symptom (Will, fresh session):** killed Typhon at the Olympus summit, no working continuation
  portal to Rhodes; the campaign cannot progress past Olympus. Q1 lane added an
  Action_UnlockFixedItem on the "Olympus - Typhon Defeated" token (in "quest that controls bosses
  and their doors.qst" idx 68, loads fine) - STILL no portal on a genuinely fresh kill.
- **RCA (M7 + M12, byte-definitive):** the base post-Typhon portal `xq00_olympus_portaltorhodes`
  (FixedItemTeleport, `locked=1`, "Opened by Zeus after Typhon Killed") is present at OlympusFinal02
  instance [41]. Its destination is ENGINE-INTERNAL (not in the record, the 0x14 [generic 12B], the
  GROUPS, or the SD - verified in ours AND SVAERA). No quest in ANY arc (base + 5 XPack + SVAERA +
  ours) references it. **"Copy SVAERA" has NOTHING to copy:** instance [41] is BYTE-IDENTICAL across
  SVAERA / ours / base (rec_md5 `0975f9aa…`, flags=1, uid `24018446…`, 0x14 `2900…01000000`, pos
  (305.79,90.11,486.84)); SVAERA's DB is an empty 2KB stub so it uses base's `locked=1` record;
  SVAERA's quest 15 / boss-doors controller / init quest are all byte-identical to base; SVAERA's
  QUESTS registry is a subset of ours (DB-lane Q3: no IT main quest missing). So SVAERA is NOT
  born-open and has NO special portal wiring. (scratchpad inst41_diff.py / svaera_cmp.py / svaera_q.py)
- **FIX (chosen): the boat-dialog NPC (Model C).** A summit "portal master / Hermes" NPC ->
  Action_BoatDialog to the Rhodes arrival - a DATA-DRIVEN teleport that does not depend on the
  engine-internal FixedItemTeleport. Map-side spec READY (build_section_surgery.py
  OLYMPUS_RHODES_NPC_SPEC_PENDING): NPC at OlympusFinal02 local (305.80,90.20,490.80) = world
  (1155.80,90.20,-3190.20), 4u from the portal on the Typhon plateau, navmesh-verified on-mesh +
  100% clear + connected. Rhodes arrival = the base's OWN paired target
  `xq00_rhodes_olympusportaltarget` @ Rhodes_CityFinal_01 = WORLD **(700, 41, -6466)** (on-mesh).
  GATED on the DB lane (a8f5446a) authoring `records\quests\portal_master_olympus.dbr` + the
  boat-dialog quest (MAP-REF-1). Then wire the spec, rebuild both maps, gates, coupled map+Quests
  DEV deploy. Mesh `Credits_Portal.msh` + the portal anms DO resolve (base XPack Items.arc) - render
  is not the blocker; the dead engine destination is.

### B-MERGE-SD-GROUPS-1 (P1, map lane): GROUPS half FIXED (build31e M13a); SD half OPEN (M13b, needs sd_format RE)
- **M13a SHIPPED (build31e, 2026-07-10): the GROUPS restoration.** New merge in
  `svaera_plus_portals.py merge_groups_svaera_base`: SVAERA/base records (SVAERA order, verbatim)
  + SV-extra members appended per-record (4: the HV01 fountain, the SV maze respawn, JadeFigurine,
  1 SV Hades member; levelGUID-validated, 0 stale skips) + the 4 SV-only groups (New Group x2,
  DRXShrineTeleport_Duister, zRespawnSanctuary). RESTORED: Tower-of-Judgement floor-4 respawn
  (32703cac.., the Lane B mandatory-path dead shrine), teleportshrineolympus01 (3c007d48.., the
  Olympus rift stop - B-OLYMPUS-TELESHRINE-1 is thereby RESOLVED BETTER THAN FILED: restored, not
  removed), Shrine_Teleport_Orient 12th member, + base-correct member positions/GUIDs in 42 more
  same-name records (golden chests, unified proxies, the Q15/xQ00 portal-pairing [Any Entity]
  records). NEW fail-loud GATE `tools/verify_groups_bindings.py` (forward per-instance check:
  every placed StrategicMovement*Shrine uid must be GROUPS-bound; the gap contracts_map
  MAP-GROUPS-1 could not catch): **374/374 devices bound, 0 dead** on both variants + the 5
  Lane-B must-bind uids asserted in-build (M13A_MUST_BIND). Walk-test: ToJ floor-4 respawn +
  the Olympus rift shrine + HV01 fountain still binding.
- **M13b RE COMPLETE -> verdict NO-GO (2026-07-10, backlog lane).** Full SD(0x18) format RE +
  round-trip-proven parser landed: **`tools/sd_format.py`** (byte-identical round-trip on all 4
  maps: SV v6, ours v6, SVAERA v7, vanilla v7) + **`docs/SD_FORMAT_RE.md`** (RECIPE). Findings:
  SD = `[magic=2][version 6|7]` then a POSITION-ORDERED list sequence `[listTag][count][records]`
  (listTag is REUSED - 1=env&miniboss, 2=region&audio - so order, not tag, keys the schema).
  Lists: [0] env/fog, [1] region/zone-label (**the SV zone labels**), [2] audio, [3] miniboss, ...
  REGION schema (identical v6<->v7): `a=1 | nameLen+name | guid[16] | color1[4] | color2[4] |
  tagLen+dispTag | t1 | t2`. ENV schema: `a=1 | name | guid[16] | block(120 v6 / 148 v7) |
  [v7-only: effectPathLen+weatherDbrPath]`.
  **What the merge dropped (SV v6 vs SVAERA v7):** 252 region records ALL unreachable DLC/HC
  (X4=130, X2=96, X3=23, +3 HCDun) - campaign caps at Hades so none are entered; the 282 shared
  base-act regions are **byte-identical** v6<->v7. Meanwhile SV's SD carries the 9 SV-only zone
  labels (tagBCX x4, tagMZoneGoM, tagSPDarkForest, tagSPRogueEncampment, tagJoLandia, tagNewMZone1)
  + 17 SV-only env presets (BloodCave/Duister/UberDungeonLevel1/RogueEncampment/...) + SV audio/
  miniboss bindings - all for the RESTORED SV AREAS. **A v7 SD swap loses all of that to gain
  only unreachable DLC + ~10 cosmetic base-act fog presets.** No proven defect is SD-attributed.
  **CLOSE unless** someone wants the cosmetic fog polish: a targeted record-level merge keeping SV
  v6 as base + porting just the ~10 re-authored base-act fog env presets - blocked on the v6->v7
  env-block conversion (the +28 v7 bytes' field semantics), low priority. Region-record edits are
  trivial via sd_format.py; env porting is the only real cost. Full detail: `docs/SD_FORMAT_RE.md`.

### B-PORTAL-1: Portals are ugly flat blue panels / hard-to-see arrows
- **Symptom (Will, screenshots):** the born-open GridEntrance portals now APPEAR (build27 fix
  worked) but render as a **flat 2D blue rectangle** with a small light-blue triangle/arrow, not
  an attractive portal. In Duister (Secret Place) they're flat teal panels floating in the room.
- **Cause:** when we swapped GridEntranceDynamic → base GridEntrance for the born-open fix
  (commit portals-born-open / build27), we kept `mesh` but the base GridEntrance class renders its
  portal-plane placeholder (the blue panel) rather than a nice swirling FX. The dynamic class had
  the pretty visual tied to its open-animation; the static class shows the raw portal quad.
- **Fix approach:** give the portal records a proper portal MESH + FX. Options: (a) find a
  base-game always-open portal that looks good and copy its mesh/fx fields; (b) attach a portal
  particle effect (the Tower-of-Judgment `TJ_JudgementRoom_PortalObject` swirl, or a rift FX) as a
  separate decoration/effect entity co-located with each portal; (c) check if base GridEntrance has
  a `portalFxName`/`meshFxName` field that we left empty. MUST keep born-open + teleport working
  (don't revert to Dynamic). Files: tools/apply_svc_patches.py (the `_make_portals_born_open_*`
  block) for record fields, or tools/build_section_surgery.py to co-locate an FX entity.
- **Verify:** in-game only (visual). Static gate: portal record has a non-empty mesh/fx that resolves.

### B-PORTAL-2: Portal placed in the middle of the walkway (blocks passage)
- **Symptom:** the blue portal to the RHS of the respawn fountain sits **right in the path** -
  Will can't walk past it without being teleported. (Screenshot 1: the flat blue panel east of the
  fountain, on the only route.)
- **Cause:** hub/door portal placement coords chosen for on-mesh + distance-from-friendlies, but
  NOT for "off the natural walking path." A portal you can't avoid = forced teleport.
- **Fix approach:** relocate that portal (and audit all hub portals) OFF the main traffic lane -
  tuck them against a wall/edge so the player walks TO them deliberately. In the blood-cave first
  room the 5 hub portals should be a neat row along a wall, not blocking the tunnel. Files:
  `_HUB_CAVE_ENTRANCES` / `_HUB_CAVE_RETURNS` coords in tools/build_section_surgery.py; the door
  portal coords in the A1/A2/Sparta specs. Re-run gate_doors_hub after moving.
- **NOTE:** this is the TESTHUB hub portals AND possibly canonical doors - check both.
- **2026-07-08:** G1 (the fountain-camp Garden door, the offender Will hit) relocated ~12.4u off
  the walking lane by the map wave. NEW SAME-CLASS HAZARD found by audit: the Sparta door entrance
  P1 in catacube02_floorlast sits 6.0u from the stairsdown01 traffic funnel; relocate it too
  (in the wave). Vista S1 and maze03 A1 placements are fine.

### B-PORTAL-3: Return/back teleport doesn't work (one-way trip)
- **Symptom:** Will teleported to "Duister" (Secret Place) via the panel, could walk around, but
  **could not teleport back**. Also: "all the portals in Duister are broken."
- **Cause:** the return portal (GridExitOneWay landing → its own back-entrance) either wasn't
  swapped to born-open (only the OUTBOUND portal_olympianarena1 was swapped; the RETURN
  portal_olympianarena2 is GridExitOneWay - is IT visible/functional?), OR the Secret Place cluster's
  INTERNAL portals (SV's own darkforest transition portals) are DynGridEntrance that never open
  (same class bug, different records, explicitly out-of-scope in the born-open fix - see
  DYNGRID_GATE_RCA.md note 2). "All portals in Duister broken" strongly implies the 11-level Secret
  Place cluster's own inter-level portals need the same born-open treatment.
- **Fix approach:** (1) verify the return portal_olympianarena2 renders + teleports (GridExitOneWay
  semantics - does it need born-open too? it's a different class); (2) enumerate ALL DynGridEntrance
  portals in the Secret Place cluster (and every SV area) and apply the born-open swap to them too
  (generalize `_make_portals_born_open` beyond portal_olympianarena1 to ALL our-relevant
  DynGridEntrance records that should be always-open). Files: apply_svc_patches born-open block.
- **LIVE UPDATE 2026-07-08 (Will, public build):** the GARDEN OF MERCHANTS return portal is ALSO
  broken (outbound from the fountain camp teleported fine; the return in the Garden did nothing).
  With Duister's returns already confirmed broken, one-way returns are SYSTEMIC: verify and fix the
  returns of ALL FOUR portal areas (Garden, Secret Place, Uber Dungeon, Sparta Crypt). Outbound
  born-open entrances are CONFIRMED WORKING live (first public-build walk-in teleport verified).
- **ROOT-CAUSE DISCRIMINATOR (2026-07-08 byte-level diagnosis):** every 0x14 binding is CORRECT
  (60B prefixed entrances, 48B landings, pairing intact, dest GUIDs verified, no mis-wire). The
  live pattern: entrances hosted in ORIGINAL-INDEX levels fire (G1 in HV01, hub portals in swapped
  Random09A); entrances hosted in APPENDED SV-only levels never fire (G3 in the Garden, S3 + hub
  returns in darkforestenter). Invented return-entrances have zero native precedent (native
  bidirectional doors = one 0x14 mouth + one reciprocal 0x06 descriptor in the destination).
- **FIX RECIPES (handed to the 2026-07-08 map wave):** SPARTA = convert to a NATIVE two-way door by
  repurposing SC2's dangling 0x06 tail descriptor in place (exit d76121ad..., mouth efbf54c9...,
  src catacube GUID 817574a8..., door cell (6,0,4)); remove injected P2/P3/P4. UBER (A1) = DEFER
  (crypt_floor1 is a 2-layer grid; door-cell Y = layer index; needs layer RE first). GARDEN =
  no native map return possible (terrain level); SV's DESIGNED return is the rift shrine
  teleportshrine_gom, VERIFIED FULLY WIRED in our build (Will: walk-test rift travel from the
  Garden shrine). DUISTER = its teleportshrineorient01 shrine is INERT (flags=0, no uid, no GROUPS
  member); wiring it like the Garden shrine gives Duister the same SV-native rift return.
  Escalation if appended-host entrances must ever fire: Frida runtime session in the Garden.
- **Walk-test predictions:** maze03-hosted hub return WORKS; SC2/murderbossroom-hosted returns
  broken until the SC2 conversion; pillagedvillage -> forestobsidiantransition = control case.

### B-SUMMON-1: Summoned pets spawn NAKED / broken (no equipment, some immobile)
- **Symptom (Will):** "Summon Boneash" summons Boneash but he has **no weapon, no helmet, no
  chestplate, no greaves - nothing**. Earlier: the Blood-High-Priest soul's "Call the Blood
  Blade-Dancer" summon appeared as a **floating scythe, immobile** (bug F).
- **Cause:** the wave-created pets (and possibly the base Boneash) have incomplete equipment/visual
  wiring. Per CLAUDE.md lessons: pet equipment must be set via `_set_pet_equipment()` with hardcoded
  item paths - copying loot/equip fields from Monster.tpl → Pet.tpl CRASHES, so pets are authored
  bare and equipment is added back explicitly. If `_set_pet_equipment` wasn't called (or the item
  paths are wrong), the pet spawns naked. The floating-scythe = mesh/animation-table mismatch
  (the pet's mesh is a weapon-only rig, or charAnimationTable doesn't match the body mesh).
- **Fix approach:** THIS IS THE ENTITY CONTRACT SUITE'S JOB (spec in HANDOFF §4b, workflow
  wf_87586bbf-b63 was STOPPED on hold - RESUME it). It must: (1) for every summonable pet, verify
  mesh + charAnimationTable exist and are rig-compatible; (2) verify equipment is wired
  (`_set_pet_equipment` called with resolving paths) OR the pet is intentionally unarmed; (3) fail
  the build on any naked/floating/immobile pet. First fix Boneash + Blade-Dancer, then all wave pets.
  Files: tools/apply_svc_patches.py pet-creation blocks; reference the WORKING Lyia Leafsong pet.
- **Cross-check:** Will said "if this soul has this issue we probably have many others" - treat as
  systemic across ALL summon souls we created (bwpriest x3, lillued x3, and any other spawnObjects).
- **build28 (2026-07-08):** 12 broken pets repointed at their source monsters' loot-table
  loadouts (player uniques never auto-equip -> naked) + NEW validate_summon_pets gate. Verified
  present in the deployed arz (c4aa4d75); validator PASSes with upstream-only WARNs.
- **REPEAT-FILED (Will, live on build28): "summons are broken".** build29 findings, all fixed:
  (1) SOUL-GRANTED summon skills are gated by the SAME StartSkill anim abort as B-SOUL-PROC-2
  (see its RCA v2): a summon skill with a non-playable special anim NEVER SPAWNS its pet
  (strongbark_quillvines anim Roar x8 souls, barmanu_blizzard + gargantuanyeti_iceblast +
  nehebkau-class anim Summon x21 souls) - pcsafe clone + repoint like every other grant;
  (2) 25 soulskills pets (carrioncrow, peng, quillvine_03, skeleton_archer/soldier ladders)
  shipped with EMPTY monsterClassification while every working exemplar (Lyia, Boneash, base
  WraithLord) is Common - set to Common;
  (3) validate_summon_pets extended to cover the FULL chain from GRANTING ITEM to living pet:
  summon-skill castability (anim), itemSkillLevel vs spawnObjects ladder (warn), pet
  monsterClassification, plus the existing mesh/rig/equipment/controller/skill checks.
  Equipment-side (naked/floating) remains as build28 authored it; needs Will's walk verdict on
  freshly summoned pets (saved-item baking does not affect pets, they spawn from the DB).

### B-TOXEUS-1: Blood Toxeus shroud is still GREEN, not RED
- **Symptom (Will, screenshot 2):** the new Toxeus the Murderer, Devourer of Blood boss fights, but
  the **aura/shroud around him is GREEN** (the Athens-Toxeus poison shroud), not red.
- **Cause:** the rename+reskin (toxeus-devourer-rename) changed the MESH to the Athens rig +
  the crimson skin TEXTURE, but the SHROUD is a separate attached FX/skill (the Athens Toxeus has a
  green poison-cloud aura skill or a bound FX). We changed body color but not the aura FX color.
- **Fix approach:** find the aura/shroud FX on um_bloodtoxeus_99 (a skill in its skill list, or a
  charFX/bound-effect field) - it's inherited from the Athens Toxeus (green poison theme). Swap it
  to a red/blood-themed FX (there are red/blood FX in the DRX effects - trail_wep_spear uses blood;
  look for a red aura/cloud). Files: apply_svc_patches _create_blood_toxeus, the monster's FX/skill
  fields. Keep his Blood Boil kit; just recolor the ambient shroud.

## 🟠 P1 - confirmed broken, non-blocking

### B-SPRITE-1: Exploding sprites do not respawn (STILL - reconfirmed 2026-07-08)
- **Symptom:** the exploding sprites near the occultist pyre spawn once, then never again - Will
  stood on the volcano/pyre spawner for minutes, nothing new. (Was task #37A; STILL broken.)
- **Cause (hypothesis):** our placed t1_pitspawner cluster is missing the continuous-spawn config
  (spawn interval / max-alive / respawn-on-death fields) OR is a one-shot-per-level-load spawner
  vs the Greece exemplar's continuous one. Will's leave-and-return discriminator test was never
  reported back - needs it: leave the area + return; if 3 fresh sprites reappear = per-level-load
  refill (config gap); if none = spawner died with its brood (wrong record).
- **Fix approach:** diff our pit records vs the LIVE Greece occultist pit (which spawns
  continuously) field-by-field - spawn timing/limit/controller. Match Greece. Files:
  tools/build_section_surgery.py sprite/pit specs (the B2 block).

### B-TEMPLE-DOOR-1: "Temple Entrance - Locked ~ Sealed By Guardian" won't open
- **Symptom:** killing the guardian in front of the sealed temple door in the blood cave does NOT
  unseal it. (Was task #37C.)
- **DIAGNOSIS 2026-07-08 (byte-proven; 'never ported' REFUTED):** the full unlock chain is present
  and intact in build27. Doors = babtpl_waterfallroom_secretdoor.dbr + waterblocker.dbr
  (FixedItemDoor, locked=1, tagBloodCaveTempleEntrance; waterblocker carries the Sealed By Guardian
  hint tag) in drxbc2.lvl. Controller = open_bloodcave_portal.qst step 0 trigger 'Unlock Waterfall
  Door': Condition_KillAllCreaturesFromProxy(q_highpriest_lone, isResettable=1) ->
  Action_UnlockFixedItem on BOTH doors; ported byte-intact; quest registered at idx 97/256 (inside
  the load window since build22). Guardian proxy/pool/monsters all present under identical names
  (no soul-wave rename). Nothing to port, no slot to add, no rename.
- **Residual = RUNTIME** (quest adoption / proxy-death arming across region streaming; same
  reliability class as the widow-letter window bug). Will's original failing test predates the
  build22 window fix, so the door may ALREADY WORK. **DISCRIMINATOR (Will, on the fresh public-build
  character): in the blood cave waterfall room (drxBC2), kill the lone guardian miniboss in front of
  the Temple Entrance and see if it unlocks.** Unlocks = close this item (build22 fixed it). Still
  sealed = the proxy is not spawning its guardian (population wiring, sibling of B-SPRITE-1) or
  KillAllCreaturesFromProxy is not arming for an adopted control quest; investigate THAT, not the port.

### B-SMOKE-1: Region smoke density far below SV (STILL - reconfirmed)
- **Symptom:** some smoke present, but SV had FAR more, starting the moment you enter the section.
- **Cause:** the C4 atmosphere restore covered ENTITY emitters only; the REGION-WIDE ENVIRONMENT
  half (SD/0x18 or level 0x09 env params - volumetric fog) was never restored (vet hedge on record).
- **2026-07-08 REFUTATION:** the region-env transplant hypothesis is DEAD: the 0x09 env/fog record
  is byte-identical SV vs shipped for every affected level (the v1-vs-v2 divergence is a re-save
  framing marker, not content); SD/0x10 carry no fog delta. DO NOT transplant 0x09/0x17 (framing
  mismatch corrupts). Remaining levers: (a) map side = restore the still-dropped SV Delphi entities
  via INJECT_SPECS at SV-exact coords (delphilowlands02: t1_pitspawner_01 x2, t1_pitspawner_02,
  t1_lildude x6, soundobject_cageglow; delphilowlands04: cage_binding_fx01 + cage props + lildudes
  + vitstaffs; delphilowlands03: lildudes + vitstaffs) - in the 2026-07-08 map wave; (b) DB side =
  audit fog_occult_fx01/pit_fx01/pit_fx02/bugcloud_smallfx emission values vs SV-era - in the
  2026-07-08 DB wave (item 9). If both come back SV-faithful, the residual gap is engine-era
  rendering, not data.

### B-TEXT-TAGS-1: 8 Blood Toxeus / Crimson Verdict tags render as raw strings in-game
- **Symptom:** on the PUBLIC item, Hemorrheus's name, the Crimson Verdict set name, its 4 set-piece
  item names, the Vein Render sword, and the Hemorrhage soul (name + description) display as raw tag
  strings (e.g. `tagSVCSetCrimsonVerdict`) instead of proper names. Verified: the deployed `Text.arc`
  is missing all 8 tags that shipped `.arz` records reference. Confirmed by `validate_tags` and
  enumerated in `docs/MULTIPLAYER_COMPAT.md` §M3.1 (+ the `docs/STEAM_RELEASE.md` pre-flight).
- **The 8 tags (each referenced by a deployed record, absent from `Text.arc`):**
  `tagMonsterHemorrheus`, `tagSVCSetCrimsonVerdict`, `tagSVCSoulHemorrhage`, `tagSVCSoulHemorrhageDESC`,
  `tagSVCarmCrimsonVerdict`, `tagSVChlmCrimsonVerdict`, `tagSVCtorCrimsonVerdict`, `tagSVCwpnVeinRender`.
- **Cause:** the known `build_text_arc.py` ↔ `build_svc_database.py` coupling gap - these tags postdate
  the `mod_authored_tags.txt` manifest, so the build's referenced-mod tag *gate* does not know it owns
  them and passes, yet they never got written into `Text.arc`. Not an MP/determinism/crash problem
  (name/description tags only), so friends-only co-op is unaffected - but it is visible to every public
  subscriber.
- **Fix approach:** add the 8 tags (and audit for siblings) so `build_text_arc.py` emits them, rebuild
  `Text.arc`. **COUPLED DEPLOY: arz + Text.arc must ship together** (tags changed). Then re-verify
  `validate_tags` has zero referenced-and-missing tags, redeploy locally + push the Workshop update.
  Files: `tools/build_text_arc.py`, the tag manifests (`work/.../Database/uber_soul_tags.txt` is the
  LIVE one), and whatever authored these records in `tools/apply_svc_patches.py`.

### B-SOUL-PROC-1: Soul-granted 'Activated on attack' skill never procs (NEW 2026-07-08, P1)
- **Symptom (Will, public build, co-op session, fresh level-5 Occultist):** the Crommyonian Sow
  Soul tooltip says "Grants Skill: Ground Smash (Activated on attack), Cooldown: 8 Seconds" but the
  skill NEVER activates when attacking.
- **Why the existing validator missed it:** validate_soul_augments only checks that
  itemSkillName / itemSkillAutoController REFERENCES RESOLVE; a proc needs the whole activation
  chain to be semantically right (controller Class + activation event + proc chance + the granted
  skill being an executable active skill with a valid animation on the wielder).
- **ROOT CAUSE FOUND (2026-07-08 recon, byte-verified): PORT REGRESSION, SYSTEMIC = 219 souls.**
  The souls set itemSkillName + itemSkillAutoController but omit itemSkillLevel, so the granted
  skill instantiates at level 0 = inactive (tooltip renders, controller has nothing castable).
  Base game sets itemSkillLevel on 876/876 granted-skill items; SV 0.98i on 941/941. A/B proof in
  our own arz: sstheno_soul (same controller + same skill class, level 4) works; gorgonguard_soul
  (SAME skill + SAME controller, level absent) is dead. 211 broken souls come from ONE function
  (apply_svc_patches _overhaul_generic_souls: OVERHAULS dict never includes itemSkillLevel) + 8
  hand-authored itemSkillLevel==0 (snaptooth/orythroneus/rocksting e/l + crowboar n/e).
- **Fix (spec'd, folded into the 2026-07-08 DB wave as item 7):** inject per-tier default
  itemSkillLevel (n/e/l = 1/2/3) in the overhaul apply loop when absent; bump the 8 zeros; extend
  the validator with semantic activation-chain checks (skill Class = Skill_*, itemSkillLevel >= 1,
  controller template = SkillAutoCastController.tpl with chanceToRun > 0 and triggerType set).
  Gate: broken chains 219 -> 0, previously-OK 1,152 souls byte-unchanged.
- **REPEAT-FILED (Will, live on build28, 2026-07-08): "the ground attack in the soul is still not
  working" / "souls skills are broken".** The build28 itemSkillLevel fix IS in the deployed arz
  (c4aa4d75: 1371/1371 granted-skill souls carry level >= 1, sow souls at 1/2/3) so the level fix
  was NECESSARY but NOT SUFFICIENT.
- **RCA v2 (B-SOUL-PROC-2, build29, disasm-proven):** Game.dll SkillManager::StartSkill (log
  string "Animation failed to start in SkillManager::StartSkill" va 0x1035c3b0, gate vcall at va
  0x102561d4) ABORTS the whole cast and returns false when the skill's skillSpecialAnimationName
  cannot start on the CASTER's animation table. Our shipped PC tables (SV's own, byte-identical
  port; anm_malepc01/anm_femalepc) define 32 special-anim names of which only TWO (AoE360,
  Colossus) exist in EVERY weapon row of both sexes. cyclops_groundsmash ("Ground Smash") carries
  anim ClubSlam, a Cyclops-rig animation in NO PC row: the proc can never fire for a player at any
  itemSkillLevel. 39 distinct soul-granted skills carry never-playable monster anims (ClubSlam
  x105 souls, Spit x55, Punch x36, BloodBoil x29, Summon x21, GroundPound, Bite, ...); dozens more
  (ThunderClap/Ensnare/CallOfTheHunt/...) play only with SOME weapon types. Working A/B from
  Will's own sessions: summon_boneash (NO special anim) fired; cyclops_groundsmash (ClubSlam)
  never did. Secondary defect, same chain: the basetemplates autocast controllers the souls
  inherit carry NO autoTargetRadius while every WORKING base-game Enemy/AttackEnemy controller
  carries 10-15 (the only base item using base_atenemy_onattack is the known-broken EE
  sihailongwang spear).
- **FIX (build29, SHIPPED in the wave):** apply_svc_patches _fix_granted_skill_castability:
  every soul-granted skill whose special anim is not universally playable is CLONED to
  records\skills\soulskills\pcsafe\ with the skillSpecialAnimationName field REMOVED entirely
  (exact base-parity: sampled base controller-cast grants carry the field ABSENT, never
  empty-string; wraithlordsummons + 172/204 base proc grants are anim-less) and the souls
  repointed; originals untouched so monsters/pets sharing them (melinoe_bloodboil = Blood
  Toxeus kit, spellbreaker, wraithlord deathnova) keep their animations. Enemy-targeted soul
  controllers lacking autoTargetRadius get 15.0 (base concrete-controller parity); Self/Ally
  controllers are deliberately untouched (base Self controllers use a wide 10-15 radius;
  forcing a small value could suppress self-buff auto-casts). Build29 counts: 60 skills cloned,
  442 soul grants repointed, 6 Enemy controllers given a radius. Invariant + the standalone
  validate_soul_augments now FAIL the build on any non-universal granted anim and any Enemy
  controller without a radius (negative-tested against the build28 arz, which they fail).
  NOTE for testing: TQ saves bake item properties at pickup, so souls already in a bag may keep
  dead grants; verify on FRESHLY DROPPED souls (the build29 starter chest's sow souls were the
  test vehicle; that slot is gone since build30 - use any boss/hero soul drop instead).
- **Same-gate siblings found (NOT fixed in build29, report-only):** player mastery skills with
  monster-only anims are equally uncastable and were already dead in SV (Earth drxmeteor anim
  MeteorShower; Medicine tree TelkineSummonSkeleton/TelekinesisStart; Storm spellbreaker anim
  Drain as a TREE skill). Fixing those changes mastery behavior; needs Will's call.

## 🟡 P2 - pending answers / smaller

### B-FX-DANGLING-1: ~353 pre-existing dangling Chris\UnarmedProjectile_FX01 particle refs (build30 delta vet)
- **Symptom:** arz-wide, ~353 records (incl. player Earth skills drxflamesurge/drxvolcanicorb)
  reference the nonexistent `Records\SandBox\Chris\UnarmedProjectile_FX01.dbr` in
  particleEffectNameN slots. Cosmetic only (the engine skips the missing layer; no crash).
  The 3 pcsafe soul-skill copies were fixed in the build30 F-wave (F7a); the rest are upstream
  SV debt. Fix approach: an F7b-style sweep (strip or repoint) if Will wants the fx layers
  back; else leave. Also inert leftovers to strip in the same pass: orphaned
  particleEffectAttachPoint2/3 on the 3 pcsafe skills; supra wep_spear.dbr's bumpTexture
  (harmless on the base RSpear14B mesh).

### B-GATE-HARDEN-1: build gates SKIP (not FAIL) outside the work/ layout (build30 delta vet)
- The A9 render-chain + F2 summons-contract gates skip loudly when the game dir / staged
  Resources are absent (scratch determinism builds). Optional hardening: an env flag
  (SVC_REQUIRE_GATES=1 -> FAIL instead of SKIP) so a mis-pathed work build can never
  silently skip its gates. Also: persist stage-baseline arz copies (e.g. the D10 0e70ffe6
  baseline) under local/db_backups/ so intermediate record-diffs stay reproducible after
  session scratchpads are cleaned.

### B-AREA-NAME-1: Garden of Merchants minimap label reads 'Duister' (NEW 2026-07-08)
- **Symptom (Will, public build):** he teleported from the fountain camp into a garden/courtyard
  full of merchants (= the Garden of Merchants, destination wiring CORRECT), but the minimap/region
  name displayed 'Duister' (the Secret Place forest naming; Dutch for dark). The restored Garden
  level apparently carries a wrong display-name reference inherited during restoration.
- **Fix approach:** root-cause the level display-name mechanism (level blob field vs tag ref vs
  Text string); fix the Garden label and AUDIT ALL restored areas' labels (Uber Dungeon, Boss Arena,
  Sparta Crypt, Duister itself) for the same inherited-name defect. The 2026-07-08 map wave was told
  to investigate; if the fix is Text-side it rides the next arz+Text coupled push.

### B-TOXEUS-2 (P0, build29 RCA + FIX): Blood Toxeus stopped spawning on build28
- **Symptom (Will, TESTHUB, 2026-07-08):** the cave-mouth Blood Toxeus no longer spawns. Proxy
  q_bloodtoxeus_lone byte-verified present in the TESTHUB map; the SAME proxy+pool spawned him
  2026-07-07 on the build27 arz. Delta = the arz only.
- **RCA (byte-proven, build27-vs-build28 boss closure diff):** proxy + pool + monster stats are
  IDENTICAL; the ONLY closure delta is the B-TOXEUS-1 recolor: (1) new clone
  bloodtoxeus_envenomweapon set weaponEnchantment='' - an empty-string .dbr ref with ZERO
  precedent (base game 0 of 56 weaponEnchantment carriers; build27 0 of 56; enchantment-less
  base Skill_BuffSelfToggled records OMIT the field, 31 of 50); (2) new clone
  bloodtoxeus_summonlildude ADDED charFxPakSelfNames to a Skill_SpawnPetMonster - a field NO
  record of any Skill_SpawnPet* class carries in base or build27 (and the donor never had the
  green pak, so the recolor premise was wrong for this skill). Both zero-precedent field shapes
  are loader-abort suspects (unloadable monster = silent no-spawn). **The arz is shared, so the
  canonical secret-area Hemorrheus is equally dead on the PUBLIC build28 item = live P0.**
- **FIX (build29, Lane A):** the envenom clone DELETES the weaponEnchantment field (base-absence
  parity) and keeps the red leinth-aura pak (proven loadable in that exact field shape via
  leinth_aura_buff on a live-spawning boss); the lildude summon reverts to the shared donor
  record (boss skillName9/specialAttack5SkillName = exact build27 bytes; the clone is no longer
  created). Red-shroud intent KEPT (initialSkillName/skillName3 -> the envenom clone). NEW
  fail-loud invariant _verify_boss_kit_clone_shape (apply_svc_patches): a registered boss-kit
  clone must not add fields its donor lacks, must not blank a donor .dbr ref, and its refs must
  resolve. Negative-tested. Gate: boss + closure field-parity with build27 except the intended
  recolor deltas (verified in the build29 record diff). Will's walk test still decides.

### B-SUPRA-NOTIFY-1 (P3): supra formula grant is SILENT (placeholder tags)
- The Esfri chest quest grant (open_bloodcave_portal.qst, Hidden Chest Control) gives the supra
  formula via Action_GiveItem straight into the bag, but its notification uses SV's placeholder tags
  (tagTitleTagTESTER / tagLOCATIONTAGTESTER) so players get NO visible message and easily miss the
  reward. Inherited SV 0.98i debt, not a port regression. Fix: real notification text (Quests+Text
  coupling). See the 2026-07-08 Esfri recon in the resolved item below.
- **BUILD29 DISASM REFUTATION of the "chest tier-1" plan (LANE B COORDINATION, P0):** the closed
  RCA's mechanism claim ("set loot3Chance=100 on loottable_hidden_bloodcave_0{1,2,3} -> the chest
  always drops exactly 1 supra formula") is FALSE. Game.dll FixedItemContainerController disasm
  (0x10182120 / 0x10181530 / 0x10181da0): a chest spawns numSpawn items and picks ONE loot slot
  PER ITEM by roulette over the slots' chance values (chances are RELATIVE WEIGHTS, not
  independent gates). With the Esti tables' chances summing 113.2 and numSpawn ~18-20, a
  loot3Chance=100 slot would put a supra formula on ~47% of every draw = ~8-9 formulas per open,
  and can never guarantee exactly 1. The ONLY exactly-once mechanism is the EXISTING quest
  Action_GiveItem (Condition_UseFixedItem -> token + GiveItem) - i.e. SV's original design.
  **Lane A therefore left the Esti loot tables byte-identical to build28, and Lane B's
  _neutralize_esti_chest_supra (already written into tools/build_quest_files.py expecting the
  chest-side grant) MUST NOT SHIP - with it the player would get ZERO formulas ever. Keep the
  quest grant; the whole item then needs no change at all (notification tags already resolve).**
- **ALREADY RESOLVED Text-side (verified during build29):** build_text_arc
  QUEST_INTEGRATION_TAGS defines tagLOCATIONTAGTESTER = "The Blood Cave" and tagTitleTagTESTER =
  "Esti's Hidden Chest", so the popup renders real strings, not raw tags (the build29 attempt to
  redefine them tripped the duplicate-tag gate, proving the definitions live). Residual polish
  only: the quest still references the TESTER tag KEYS and "Esti's" is a probable "Esfri's" typo;
  wording pass for Will.

### B-TESTHUB-TOXEUS-1 (Will request 2026-07-08): remove cave-mouth Toxeus from TESTHUB
- The Blood Toxeus/Hemorrheus test spawn ~9.9u outside the blood-cave mouth (TESTHUB-only) BLOCKS
  Will from walking into the cave to test the hub portals. Remove it permanently from the TESTHUB
  injection (canonical never had it; the superboss lives in the waterfall chamber). Routed to the
  map wave; ships in a local interim TESTHUB test build for Will now + the vetted wave build.

### B-OLYMPUS-TELESHRINE-1 - RESOLVED BETTER THAN FILED (build31e M13a, 2026-07-10): shrine RESTORED
- The M13a GROUPS restoration re-bound teleportshrineolympus01 (uid 3c007d48...) into
  Shrine_Teleport_Hades as part of base parity - the Olympus rift shrine now WORKS instead of
  dangling (strictly better than the leave-as-is ruling; nothing removed, base-game behavior
  restored). Walk-verify with the M13 wave: activate the shrine at the Olympus summit approach
  and check it joins the rift/teleport network. History: it was dangling since the original
  merge (SV's TQIT-era Shrine_Teleport_Hades clobbered base's; the M6 recon, check_respawn.py).

### B-DB-HYGIENE-1 (P3): dead orphan record potionexp_test.dbr
- records/item/miscellaneous/oneshot/potionexp_test.dbr carries a corrupted NEGATIVE
  bonusExperiencePoints (int32 overflow of ~4e9) and has ZERO inbound references. Harmless dead
  test artifact from upstream; remove or exclude when convenient (the 2026-07-08 DB wave may
  already handle it as its hygiene item).

### B-DUISTER-EXPLORE: Secret Place ("Duister") first-visit findings incomplete
- Will reached Duister but died to Toxeus before touring the other areas. All 5 hub destinations
  (Knossos/Uber, Garden, Sparta, Secret Place, Murder Bunny) still need a full walk-test once the
  portals are pretty + return works. Duister's own portals all reported broken (see B-PORTAL-3).

### BUILD29 CONTRACT-SUITE DB FIXES (2026-07-08, shipped with the B-SOUL-PROC-2 wave)
Violations found by the finished entity contract suite (feat/contract-suite), fixed in
apply_svc_patches _fix_wave29_contract_items:
- SOUL-NAME-RESOLVES (8): satyrmagi_soul + satyrspiritcaller_soul {n,e,l} carried undefined
  placeholder tagSoul1 -> new tags tagSVCSoulSatyrMagi / tagSVCSoulSatyrSpiritcaller with real
  names; test\kyrashadowdancer_soul {e,l} carried bare tagSoulName -> repointed at the live
  tagSoulName323. (SV 0.98i upstream carries the SAME dangling tags - inherited debt, no
  original names existed to prefer. The test\kyra pair is dropped by ZERO monsters =
  unreachable dev items; tags fixed anyway per the brief. The live maenad kyra souls already
  used tagSoulName323 and are untouched.)
- SOUL-AUGMENT-LEVEL (4): crowboar_soul_n/e augmentSkillLevel1/2 == 0 -> n=1, e=2 (l untouched).
- MONSTER-SKILLS-LOOT (5, was reported as 10 refs): blood-cave bodies ancestralwarrior a-e
  skillName1 pointed at nonexistent Melee_Poison09-12_10.dbr -> repointed at the real
  attackmelee_poison09-12_10.dbr (same dir, SV renamed it).
- MONSTER-SPAWN-ELIGIBILITY (1): bw_priest_houndmaster pool spawnMax=2 with
  championMin=championMax=2 left 0 guaranteed main slots (champion crowd-out, Blood-Toxeus
  class) -> spawnMax=3.
- SUMMON-PET-CLASSIFICATION (25, was reported as 17): soulskills pets missing
  monsterClassification -> Common (see B-SUMMON-1 build29 note).
- B-SUPRA-NOTIFY-1 (2 tags): already resolved by build_text_arc QUEST_INTEGRATION_TAGS
  (see its entry); no change needed.
(68x MAP-REF-1 dropped dyer/Great-Wall NPCs = map lane, not this wave.)

## 🔵 STANDING PENDING WORK (from the master queue - not new bugs)

### BUILD31 DB WAVE QUEUE (Will via coordinator, 2026-07-09; batch as one wave)
Train contents (commit-group order per coordinator 2026-07-09): (0) Q1 Typhon->Rhodes portal
unlock (URGENT, Quests.arc lane - SHIPPED as build30.3, live on Steam 2026-07-09; the unlock
event now lives in the shipped Quests.arc 631a2b4d - build ON it, keep it byte-intact in any
Quests rebuild + gate-assert its survival), (1) MASTERY WAVE 1 broken fixes B1-B6 + the new
player-skill-anim gate (**GATED + GREEN 2026-07-09**, arz 06a9a24a, commit afb30a0 - see the
gate log below), (D19) IMMOBILE HUO-REN SUMMON P1 - **DONE, gated, arz 95e816d3** (see item
below), (Q3+Q4 batch) Olympus herald NPC + kill-gated instant Rhodes unlock (M13a proxy
BossProxy_20_Typhon - verify the placed proxy record name) + Q4 dead-content one-liners
(bossarena EnterVolume volume -> volume_startolympianarena; widowletter honor-branch chest
alignment; chimera .dbr.dbr double-extension coordinated rename; q15 reconciliation per the
audit note - all ride ONE Quests.arc rebuild; Q4 item 4 testquest deregistration = MAP lane),
(2) Mastery Wave 1 Defense/Earth/Storm boosts + D16 Shadow Stalker
+ D17 Core Dweller, (3) D11 + D12 + D15 + **D18a Emberscale icon + D18b Emberscale effect
redesign**, (4) D13 + D14 + **D20 War King Sarpedon summon soul** + **D21 Long Nu the Flame
Mother summon soul (Will 2026-07-09: 'her soul needs to be able to summon her'; standard
recipe + the D19 mobility law from birth; find her records via 'Long Nu'/'Flame Mother' tags;
keep existing augments unless conflicting, report)**, (5) Enslaver (approved),
(6) N4-DB Vashkarr, (7) Q2 portal-master NPC (arz + Quests + Text coupled). N2 Typhon-gate mesh
swap = CANCELLED (Will chose the portal-master model C; existing walk-through portals stay
transitionally, retire in phase 2). BUILD32 additions (Will blanket sign-off 2026-07-09):
**N5 THROWING WEAPONS APPROVED** at ALL designer recommendations (faithful base drop weights
static_roh=400/roh=1/12 bosses; merchants DEFERRED; all 3 supers 'Sanguine Orbit' /
'The Last Word' / 'Charon's Toll'; formulas w100 supra slots 25-27 + supra_special 26-28,
reagents 1L+1E+1MI-thrown; design doc = tasks/ab8a4644fa12b0169.output;
_restore_thrown_weapon_drops faithful-copy + fail-loud gate, _add_supra_thrown_weapons clones
base thrown records - avoid the fenrirsbite stray mesh; D5 full-mesh scan must show the supers
resolve); **N7 sepulchral-wyrm hordes PRE-AUTHORIZED** (implement at designer recommendation
when the doc lands, no further sign-off).

> **GROUP 1 GATE LOG (2026-07-09, DB lane):** arz 06a9a24a (54,660,353 B) vs build30.2 baseline
> 3f605741. Record-diff = EXACTLY 28 records, all bucketed to B1-B6 (0 unbucketed): drxmeteor/
> drxthunderball/drxenslavespirit anim -> '' (B1/2/3); drxweaponpool_shieldsmash min 0->[12..61] +
> modifier 0->[20..50] (B4); nightmare_01..20 skillName1 repoint (lowercase resolving MasterMind
> path) + skillLevel1 min(tier,12) ramp (B5); anm_malepc01 + anm_femalepc gained row-matched
> SpecialAnim/Ref pairs for Taunt/Ensnare/Flamesurge/ThunderClap/Barrage/Crosscut/Hew into free
> idx<=14 (B6, pure additions); two Dream passives '0'->'' (hygiene). Gates ALL PASS: new
> player-skill-anim gate PASS on arz + NEGATIVE test FAILS correctly on the b30.2 baseline
> (Meteor/Thunderball/Bonespire + mp_taunt/hailofaxes/shenpao/breathattack/smokecloud);
> validate_soul_augments 0/0; validate_mastery_golden (Occult/Hunting) intact; validate_summon_pets
> PASS; validate_tags PASS; contracts souls+summons 0 P0/0 P1 (112 pre-existing upstream P2, not
> Group-1 records); det-2x rebuild both == committed 06a9a24a. No gate-code fixes needed.

### D19 FIXED (build31, arz 95e816d3, det-2x, gated): Huo-ren summon was IMMOBILE
- **Symptom (Will, live):** "I can summon Huo-ren the mountainblade... he is broken he doesnt move."
- **ROOT CAUSE (bone-level proof 2026-07-09; the suspected axes all EXONERATED - runSpeed 0.96,
  controller, classification all fine):** (1) the F2 loadout under-mirrored the source -
  um_mountainblade_43 equips RightHand=100 (1h_dyn) + LeftHand=100 (shield) + Torso, the pet got
  Torso ONLY -> WEAPONLESS -> engine uses the UNARMED anim row; (2) anm_dragonian defines NO
  unarmedRunAnim (base dragonians are never unarmed); (3) the source-copied unarmedRunAnim=
  CrocMan_Run.anm is FOREIGN-RIG: flameguardmesh shares 30/30 bone tokens with Dragonian01.msh,
  4 with CrocMan; CrocMan_Run binds 2/19 tracks -> unplayable. Live um_mountainblade/em_ravager
  move because their WEAPONED row falls back to the table's Dragonian_Run; the weaponless pet had
  no fallback -> immobile statue. (Evidence: scratchpad d19_*.py; bone test d19_bone_test.py.)
- **FIX (builder-level, feeds D13/D14/D20/D21/Voranthys/Enslaver from birth):** (a) D9 loadout now
  mirrors the source's hands (RightHand 1h_dyn trio + LeftHand shield trio + Torso) -> pet lives
  on the sHanded row = the exact configuration the LIVE source hero moves with; (b) D8 Xeiwang
  loadout=None premise REFUTED (um_xaiweng_48 equips RightHand/Torso/Forearm/LowerBody @100) ->
  full source-exact commondynamic mirror (also fixes his naked-hand B-SUMMON-1 class); (c) NEW
  fail-loud D19 PET-MOBILITY assert in _build_boss_summon (primary anim row must have TABLE
  RunAnim; stationary-rig tables exempt); (d) validate_summon_pets extended with the same law
  (h. LOCOMOTION: primary row weapon-derived - RightHand=weapon, LeftHand weapon-vs-shield via
  weight>0 loot tables, dual-wield -> dHanded; locomotion must come from the TABLE or a
  table-family override; foreign-family overrides do NOT count). NEGATIVE-TESTED: exactly
  mountainblade_1/2/3 FAIL pre-fix (bwpriest dual-wield correctly passes via dHanded); PASS
  post-fix. Record-diff vs Group-1 06a9a24a = EXACTLY 6 records (mountainblade_1/2/3 + xeiwang
  _1/2/3), every delta a chanceToEquip/loot field. det-2x = 95e816d3 both runs. Pets spawn fresh
  from the DB per cast -> retroactive for existing characters.
- **D7 Toxeus verified NOT in the immobile class** (unarmed but anm_skeleton01 covers
  unarmedRunAnim). His HAND slots left unchanged: the source's RightHand tables are SVC
  set/unique tables (crimsonverdict_guaranteed) = pet auto-equip risk; flag for a later pass.
Mastery specs = docs/MASTERY_AUDIT_2026-07-09.md (§2 broken fixes, §3 Wave 1; the no-removal
standing rule in its header is BINDING). Broken player skills outrank feature items.
Each group: gates + bucketed record-diff + commit; whole set -> independent delta-vet before
ship (coordinator dispatches); DEV-deploy for Will after major groups is fine (local only).
Will's standing ruling: only convert summon-souls he EXPLICITLY names.

- **Q1 IMPLEMENTED (2026-07-09): Olympus -> Rhodes portal unlock.** M7 RCA: the portal record
  (xq00_olympus_portaltorhodes, FixedItemTeleport locked=1 'Opened by Zeus after Typhon
  Killed') is unlocked by an engine-internal campaign hook that never fires in Custom Quest;
  no quest references it. FIX (tools/build_quest_files.py _add_typhon_rhodes_unlock): ONE
  trigger appended to the vanilla controller 'quest that controls bosses and their doors.qst'
  (already in-arc + registered + never completes + already evaluates this exact token):
  OnLevelLoad + OwnsTriggerToken('Olympus - Typhon Defeated') -> Action_UnlockFixedItem
  (canReFire=1; field shapes mirror the HOST file's own byte-verified idioms - no
  isQuestCritical2, no delayTime). Repeat-on-load = idempotent + retroactive for existing
  token-holders (Will's main). Rebuilt Quests.arc 631a2b4d; entry-diff vs shipped 846c43f3 =
  EXACTLY the host quest; quest-record contract PASS (107 records). SHIPPED as build30.3.
  **Q1 FAILED IN-GAME (Will, fresh session, 2026-07-09): Typhon killed, unlock event present,
  still NO portal.** Confirms M7's FixedItemTeleport-destination-is-engine-internal risk.

- **Q3 SHIPPED TO DEV (2026-07-09 night, Will escalation): instant kill unlock + token reload
  path + herald fallback, coupled arz bd6ae869 + Quests 3db3764c + Text 06c04985.**
  - **DB EXONERATED (the 'SV overrides an engine hook' hypothesis REFUTED, full-arz scan
    q3_engine_chain_hunt.py + q3_gameengine_removed.py):** ZERO records in OUR arz AND ZERO in
    BASE reference portaltorhodes/olympusportaltarget/typhontomb_portaltoolympus, any record
    type, any namespace. All 49 engine-namespace overrides (gameengine/combatequations/
    balance/itemcost/quests.dbr) diffed field-by-field vs base: every delta is SV/DRX
    balance/UI identity; quests.dbr byte-identical; NOTHING scene/portal/act/campaign-related.
    There is no data-side hook to restore - base opens xq00 from ENGINE CODE (end-of-campaign
    event) that never fires in Custom Quest.
  - **q15-vs-xq00 ANSWERED:** q15 (tomb->Olympus) works because base DATA unlocks it (quest
    15's own Action_UnlockFixedItem on the Typhon-proxy kill). xq00 has no unlocker in ANY
    data. The kill trigger makes xq00's chain structurally IDENTICAL to the proven q15 chain;
    M13a's GROUPS pairing restore (build31e) supplies the destination side.
  - **SHIPPED (one host-step append, 'quest that controls bosses and their doors.qst'):**
    (1) INSTANT: Condition_KillAllCreaturesFromProxy(Records\Proxies Boss\Boss\
    BossProxy_20_Typhon_Titan.dbr - byte-verified LIVE: quest 15 grants Will's token on this
    exact condition) -> Action_UnlockFixedItem(xq00, canReFire=1); (2) Q1 token+OnLevelLoad
    reload path KEPT (Will's main gets the portal on next Olympus entry, no re-kill);
    (3) HERALD fallback: Action_BoatDialog(records\quests\portal_master_olympus.dbr, onOff=1,
    x=700 y=41 z=-6466 = the base game's own xq00_rhodes_olympusportaltarget landing) gated on
    the token; NPC record cloned from knossos_boatmantoegypt (proven boat-dialog Npc shape,
    GreekSailor02 base art = render-safe), name 'Keryx, Herald of Olympus', 3 new tags
    (validate_tags PASS). **MAP LANE (a4207d65): the record name records\quests\
    portal_master_olympus.dbr + placement spec are now FINAL - wire
    OLYMPUS_RHODES_NPC_SPEC_PENDING into INJECT_SPECS on the next map build.**
  - Gates: quest-record contract PASS (107); Quests entry-diff vs shipped 631a2b4d = EXACTLY
    the host quest with exactly the new strings; arz record-diff vs D19 95e816d3 = EXACTLY
    +1 ADDED (the herald); golden freeze PASS on the pair; all arz internal gates green.
  - **WILL'S TEST (DEV): load main at Olympus summit -> the Rhodes portal should BE OPEN
    (token path fires on level load; M13a pairing gives it a destination). Fresh kill path:
    kill Typhon -> portal opens AT THE KILL, in view, no reload. The herald NPC appears at the
    summit only after the MAP lane wires the placement (next map build) - it is the fallback
    if the portal still teleports nowhere.**

- **Q3 archive (2026-07-09 day): Olympus->Rhodes = COPY SVAERA, not a quest. QUESTS-LANE
  VERDICT: NO restore needed.** Coordinator hypothesis (build22 dropped IT-act main
  quest registrations -> Rhodes campaign won't activate) is REFUTED by byte analysis
  (scratchpad q3_registry_diff.py / q3_content_diff.py / q3_portal_refs.py):
  - SVAERA registers 254 QUESTS entries; ours 256. **SVAERA-registered identities absent from
    our registry: 0.** Every SVAERA main quest (scripted scene_rhodes, xq03_theroadtohades,
    xq06_thethroneofhades, quest 10-15, all XPack2/3/4) is registered, cleanly shifted +4 by the
    build22 SV-quest insertion, all inside the 256 window (Rhodes/Hades at idx 108-138, far in).
  - Quest FILE presence: **0 SVAERA .qst files missing** from our Quests.arc (we ship all 100 +
    our 6). Only ONE file byte-differs from SVAERA: 'quest that controls bosses and their
    doors.qst' (+804B = our Q1 trigger APPENDED = byte-superset, all SVAERA behavior preserved).
    The 2 added endpoint-cap controllers (x4_other_001_control_expansionportals,
    xquest_controlsbossdoors) surgically remove ONLY the POST-Hades IT->EE / IT->Ragnarok
    EXPANSION portals - they do NOT touch Rhodes/Hades progression.
  - **NO quest in SVAERA OR the base game references xq00_olympus_portaltorhodes** (corroborates
    M7). SVAERA (a working Custom Quest that runs the full Rhodes/Hades campaign) drives the
    Olympus->Rhodes transition MAP-SIDE, not via a quest -> the fix belongs to the MAP LANE
    (a4207d65): make our OlympusFinal02 portal instance [41] born-open (locked=0) like SVAERA's,
    OR replicate SVAERA's placed transition. There is nothing for the Quests lane to author.
  - **Q1 unlock trigger recommendation:** it is the ONLY non-SVAERA-faithful edit in our
    Quests.arc and it is INERT (failed in-game). Once the map lane makes the portal born-open it
    is fully redundant. RECOMMEND reverting 'quest that controls bosses and their doors.qst' to
    byte-identical SVAERA (drop _add_typhon_rhodes_unlock) for fidelity; harmless if kept.
    DECISION DEFERRED to coordinator + map-lane mechanism report. If kept, it must remain a
    byte-superset (the survival gate-assert still holds).
  - COUPLED SHIP: map(born-open portal) is the load-bearing change; arz/Quests/Text unchanged on
    the DB lane for Q3.
- **Q2 QUEUED: PORTAL-MASTER NPC for SV-area travel (Will chose model C; map lane M8b has the
  mechanism analysis).** DB+Quests+Text triple: (a) friendly quest-NPC record (base boatman
  class pattern, render-safe mesh per D5 law, amgoz1-voice name e.g. 'Almyros the Wayfarer' +
  'Portal Master' title tag); (b) boat-dialog quest offering the 4 SV destinations (Garden of
  Merchants / Secret Place / Uber Dungeon / Sparta Crypt), each -> Action_BoatDialog teleport
  to landing coords from the map lane (coordinate); QUESTS REGISTRY LAW: events append to an
  already-registered loaded quest (sv_commonmechanics = natural host), NO new registrations;
  verify action shapes against base boatman quests (quest 8 to-egypt, quest 7 knossos) via
  qst_format; (c) confirmation-dialog text tags (validate_tags). All three artifacts couple;
  map lane places the NPC after the record lands. Old boat-dialog failure predated B2 (quests
  now load); pilot walk-test proves it.
- **D16 QUEUED (Will, verbatim: the swap skill 'is basically suicide... make him stronger,
  much stronger'): SHADOW STALKER OVERHAUL - EXPLICIT OCCULT-FREEZE EXCEPTION.** (1) find the
  Stalker's position-swap first ability (teleport-exchange into packs) in the Occult pet kit
  and REMOVE it from the PET kit (Will explicitly sanctioned; pet skill slot, not a player
  tree slot - the no-remove mastery law does not bind; substitute a better skill if one fits,
  report the choice); (2) substantially buff the pet ladder (life/damage/resists/speed, all
  tiers; benchmark = mastery-audit Part II, Stalker ~1440 HP reference; aggressive per Will);
  (3) validate_mastery_golden WILL fire: regenerate the golden baseline for EXACTLY the
  changed records/fields, commit documents the Will-ordered exception verbatim; gate keeps
  guarding all other Occult records. Pets spawn fresh per cast = retroactive for existing
  characters.
- **D17 QUEUED (Will: 'make the volcano guy much stronger in earth mastery'): CORE DWELLER.**
  The Earth magma golem (audit: 781/1940/2250 HP, STR 425, taunt+boulder+stonehand+wildfire).
  Buff substantially ON TOP of the Wave 1 Earth boosts: ~1.5-2x life, meaningful damage
  scaling, armor up, keep the taunt identity (Earth's ONLY pet vs Occult's 5-body package).
  Report before/after ladders. (Reading note: 'volcano guy' = the golem; if Will meant
  Volcanic Orb, the Wave 1 cd 4->1.5 boost already covers it - flagged in the report.)

### BUILD32 TRAIN (queued 2026-07-09; implement AFTER build31 ships)
- **N6-DB: Obsidian Halls treasure roulette - WILL SIGNED OFF (2026-07-09).** Full approved
  design + locked decisions: docs/OBSIDIAN_ROULETTE_DESIGN.md (chanceToRun 25.0/corner;
  Voranthys = the one summon-soul via _build_boss_summon on the SepulchralWyrm01 rig; all
  designer defaults incl. locked Boss-classification mega-chest, 5-elite warbands, no charm,
  Sarkoth soul = pcsafe typhon_meteorstorm 2/3/4). Scope per design section 6:
  _create_obsidian_roulette(db) = 4 guardians (derived natives, wild kits + ondeath skills all
  existence-verified), shared warband pool (spawnMin=Max=6, championChance=100, championMax=5),
  4 corner proxies w/ accessory tiers + no-cap limit clone [1..110], 3 svc_obsidianhoard chests
  (hpalace_chestlg01 mesh scale 1.4, goldGeneratorChance=100, guaranteed epic N /
  legendary-or-epic E/L) + 3 accessory pools + loot tables, 4 amgoz1-voice souls (66% Finger2;
  Ilsevar dream augments MUST use the xpack paths - the base-dream twins DANGLE), tags.
  NEW gates: accessory-chain-resolves + chest-lock-classification==Boss + ondeath resolution.
  In-game confirm item for Will's DEV pass: DropProjectileTelekinesis anim on the liche rig.
  MAP-REF-1 ordering: DB records land in the build32 arz BEFORE map lane M10 injects
  (4 INJECT_SPECS + shared v0e branch).
- **MASTERY WAVE 2** per docs/MASTERY_AUDIT_2026-07-09.md §3 Wave 2: Warfare (horn/standard
  uptime, armband path fix, optional warwind), Nature (force-of-nature 360->180, petBonus ML1-40
  ramp w/ overshoot check, defensiveConvert artifact zeroing, wolf FX hygiene), remaining Spirit
  (outsider 360->120 + TTL 60, deathward 300->180, bonepet xxx-spiritbreath re-enable +
  placeholder cleanup - skillName6 no-op = KEEP or EDIT, never remove, per the standing rule),
  remaining Dream (timefield dead-ref clear, phantasm uptime, psionic beam, mana-ladder
  extensions, phantomstrike self-slow = EDIT to zero/flip not remove, phantasm loot dangler),
  RuneMaster tunes (castability breakage may already be covered in build31 group 1 via the
  anim-table restoration - verify before re-implementing), Neidan tunes (mastery-bar stat-stick
  question = Will decision, splash modifier attachment = verify EE semantics first).
  ⚠️ Dream truncation note: §3 Wave 2 Dream items 2-6 numbers are reconstructed - pull the FULL
  Dream boosts block from Part III (the Dream lane's boosts array) for exact targets before
  writing. ⚠️ Golden-freeze expansion decision (doc §5): freeze the tuned trees AFTER each
  wave's QA, regenerating the snapshot in the same step.
- **N4-DB: Forest of the Ancients cave boss - WILL SIGNED OFF w/ amendments (2026-07-09).**
  Full design = the FotA design agent's final report (coordinator-held). Placement: Random05A.lvl
  cave via ToTomb02 east of Chang'an; Majestic Chest at local (24.01,1.00,28.70) stays UNTOUCHED.
  Band/HP APPROVED: charLevel [38,56,71], HP [12000,16500,21000].
  WILL'S DECISIONS: identity = (B) `{^r}Vashkarr, Eldest of the Ancients`, ANCIENT DRAGONIAN
  warlord, mesh `Creatures\Monster\Dragonian\AncientDragonian01.msh`; derive the kit from the
  DRAGONIAN family for anim-safety (NOT the option-A djinn donor). Escort = FULL-STRENGTH
  dragonian lieutenants (pool spawnMax=3, championChance=100, championMax=2 - satisfies
  spawnMax-championMax>=1): Vashkarr + 2 serious dragonians ALWAYS. Minions ("he should also be
  able to spawn many minions very often") = frequent minion-summon on his kit: clone the
  yaoguai_summonshadowstalkers Skill_SpawnPetMonster pattern -> DRAGONIAN fodder, short cooldown,
  multiple per cast; exact numbers in the implementation sign-off. SOUL = NO SUMMON ("it can just
  be really good"): vashkarr_soul_{n,e,l} = dense aggressive STAT suite at the band, richer than
  the Narok/Vort suites, {^F} tag ('Soul of the Eldest' or similar), 66% drop via
  SVC_RELEASE_DROPS, validate_soul_augments green.
  RECON (build30.2 arz, verified on-disk): `AncientDragonian01.msh` SHIPS on 7 records
  (bm_deathlance_32/34/36 + bm_ravager_31/33/35/37, Common L31-37) = the anim-safety derivation
  base; variants AncientDragonianB01.msh (bs_warlock Champions L34/37/40), AncientDragonianC01.msh
  (br_frostscourge). ESCORT CANDIDATES at band: Champions bs_warlock_40 (ancient-B caster,
  visually kin), em_ravager_41 (flameguardmesh), savage_deathlance_39; dragonian Heroes
  um_mukashi_38 / um_bloodskinner_40 / um_wisang_43 / um_mountainblade_43 (CAVEAT: hero escorts
  each 66%-drop their own souls per kill and Mountainblade is already a summon-boss soul - decide
  if that double reward is intended; the visually-kin pick = bs_warlock + a deathlance/ravager-
  derived full-strength champion clone). CEILING NOTE: shipped dragonians top out at L43, so
  escorts + minions need charLevel [38,56,71] laddered clones for epic/legendary (the
  replicant_41 [41,58,71] pattern). MINION FODDER pick: bm_ravager / bm_deathlance derived (SAME
  ancient mesh = literally 'the Ancients'); proposed cadence for sign-off: burst 3 per cast,
  ~6 s cooldown, minion charLevel [38,56,71] (tune off the decoded donor - VERIFIED at
  records\skills\boss skills\yaoguai_summonshadowstalkers.dbr, plus a skills\skills\ alias).
  PROXY: q_vashkarr_lone (chanceToRun=100) staged in BOTH drxmap\proxy\ and drxmap\proxy\pools\
  per the verified q_bloodtoxeus_lone precedent; limit/difficulty donors ON DISK:
  records\proxies boss\herolimit_all.dbr (verified present); NOTE 'HeroDifficulty_01' does NOT
  exist as a record-name substring - on-disk difficulty donors are the difficulty_01..04
  families (records\proxies orient\, xpack\proxieshades\) + xpack bossdifficulty_01; pull the
  EXACT donor path from the design doc (donor-verbatim rule). Boss passives suite per design
  section 4 (boss_conversionimmunity, all_hpscaling, boss_scaling, globalproperties
  epic/legendary boss, monsterClassification=Boss). RENDER LAW on AncientDragonian01.msh + skin
  (EngineArcResolver). Records: um_vashkarr_99 (named path preferred) + proxy + pool + minion
  skill + soul + tags (validate_tags). MAP-SIDE DEPENDENCY: these records MUST land in the
  build31 arz BEFORE the map lane injects the placement (MAP-REF-1); the map lane adds the v0e
  routing case + INJECT_SPECS in its next wave. All gates + bucketed record-diff.
- **D11: Rally** (coordinator holds the brief).
- **D12: Coastal Ichthian Myrmidon soul boost** (coordinator brief 2026-07-09).
- **D15: reward-potion name colors** (Will: Fortitude + skill-point potions should be the same
  dark red as the experience potions). RECON COMPLETE - ready to implement, pure Text-side:
  the dark red is the leading **`^M` color code** in the tag VALUE (shipped Text.arc:
  `tagNewItem6=^MPotion of Experience`, shared by ALL 48 potionexp_NN records). The four
  uncolored tags, each used by EXACTLY ONE record (arz-wide reverse-scan done, zero sharing,
  so no recolor side effects): `tagNewItem3` = 'Lesser Potion of Fortitude' (potionattri_01),
  `tagNewItem70` = 'Potion of Fortitude' (potionattri_02), `tagNewItem4` = 'Lesser Potion of
  Learning' (potionskill_01), `tagNewItem69` = 'Potion of Learning' (potionskill_02).
  FIX: these are SV-upstream tags (SV Text_EN.arc via build_modstrings), so override through
  the sanctioned single-definition dict `TEXT_FIX_TAGS` in tools/build_text_arc.py (skipped
  during SV emission, duplicate-tag gate stays green): add the four keys with the same values
  prefixed `^M`. No arz change; itemText desc tags untouched; check_duplicate_tags +
  validate_tags must PASS; Text.arc ships coupled with the build31 arz push as always.
- **D14: Phygmalian Replicator summon soul** (Will: "Phygmalian replicator soul should summon the
  soul" = the soul summons the Replicator). Records identified on the build30.2 arz (spelled
  PYGMALION in-data): monster `records\creature\monster\automatoi\um_pygmalion_41.dbr` (Hero,
  single tier, charLevel 41, tag tagNewHero262, mesh `Creatures\Monster\Automatoi\Automatoi01.msh`
  = base-game + texture `SVTextures/creatures/automatoi/pygmalion_body.tex` = SV arc; wears
  `defaultHeadPiece = ...\automatoi\pygmalion_headb.dbr` -> pet NEEDS _set_pet_equipment with
  that head piece per the F2 naked-pet law). Souls `...\soul\automatoi\pygmalion_soul_{n,e,l}.dbr`
  (tag tagSoulName583): augment swordtraining 3/4/5 + petBonusName petbonus_pygmalion_{n,e,l},
  NO itemSkillName proc -> the summon displaces nothing; KEEP augment + petBonus (petBonus buffs
  pets = direct synergy with the new summon).
  **SELF-REPLICATION - WILL'S RULING (2026-07-09, verbatim): "dont have the safe limits on the
  pygmalion replicator replicates make it crazy."** Faithful transplant of the monster's replicate
  kit; ADD NOTHING (no new petLimit, TTL, cooldown, or any artificial constraint). Both
  engineering checks RESOLVED from the decoded records (build30.2 arz):
  (1) NO RECURSION IN-DATA: `replicant_41.dbr`'s full kit is decoded (batter, shieldcharge +
  disruption, shieldsmash, lightning melee w/ slow, armor_passive, construct_resists,
  globalproperties) and it does NOT carry replicate (no skillName8, no buffSelfSkillName). The
  monster's faithful shape = ONE-GENERATION replication: copies do not copy. Ship exactly that.
  (2) ENGINE TOLERANCE MOOT: `replicate.dbr`'s OWN native fields already bound the population -
  petLimit = 3/4/5 (per skill level 1/2/3), skillCooldownTime = 9/8/7 s, petBurstSpawn = 1,
  skillManaCost = 75, skillMaxLevel = 3 (ladder 1/2/3 fits the F1 gate), NO
  spawnObjectsTimeToLive (replicants persist until killed). These are limits the MONSTER lives
  with = faithful = KEEP; nothing new is added per the ruling. No unbounded growth exists, no
  crash mechanism; nothing was silently limited.
  EXPECTED IN-GAME (sign-off numbers): the pet auto-casts Replicate every 9/8/7 s (same buffSelf
  wiring as the monster), building to the native cap of 3/4/5 PERMANENT replicants whose
  charLevel scales 41/58/71 with the skill level; each replicant is a full fighting construct.
  Legendary-tier screen state: the Pygmalion pet + 5 permanent L71 copies, all friendly
  (pet-side Skill_SpawnPet chain, Boneash precedent). `spawnObjects = replicant_41` with
  charLevel [41,58,71] = the ladder's power curve comes free from the skill itself.
  (`copy of replicate.dbr` = Skill_AktaiosMirage upstream junk; ignore.) Full D13 recipe +
  gates; the summon-skill ladder tiers map 1:1 onto replicate's existing 3 levels.
- **D13: Eater of Days summon soul** (Will: "The Eater of Days soul should let you summon him").
  Records identified on the build30.2 arz: monster
  `records\creature\monster\sepulchralwyrm\um_eaterofdays_45.dbr` (Hero-classified, single tier
  L45, tag tagNewHero91, mesh `DRX\meshes\eaterofdaysmesh.msh`, texture
  `DRXTextures\creatures\sepulchralwyrm\sepulchralwyrm_eaterofdays.tex` - DRX arcs ship with the
  mod; render-chain gate must still verify mesh-internal shaders). Souls
  `...\soul\sepulchralwyrm\eaterofdays_soul_{n,e,l}.dbr` carry ONLY an augment
  (drxdeathchillaura 3/4/5), NO itemSkillName proc - the summon grant displaces nothing (keep
  the aura augment). Kit donor skill available: `eaterofdays_necrobolt` (attack_projectile).
  Standard D7/D8/D9 conversion: manual-cast Skill_SpawnPet ladder tiers 1/2/3, itemSkillLevel
  1/2/3 (F1 gate enforces <= skillMaxLevel), permanent pet via _build_boss_summon from the
  boss's OWN mesh/anim/skills, NO monster equipment/loot field copies (_set_pet_equipment
  hardcoded if armor is needed), 'Summon <full name>' tag + {^F} law + uber_soul_tags, gates:
  validate_summon_pets + render_chain + soul_augments + summons contract 0 P1 + bucketed
  record-diff.
- **Boss-summon-soul candidates remaining (for Will's batch approval):** regenerated ranked on
  the build30.2 arz via the real wiring join (lootFinger2Item1): 643 souls wired to monsters,
  61 already summon, 578 do not. Top Boss-class by level: dragonliche L63, manticore L56,
  darksatyrshaman L55, hades L54, bloodcrow + talos L50, antaeus L49, typhon + undeadtyphon +
  meglograi L48, palai + deeptresher L47, syrinx + polyphemus + wheedletongue + uber L45,
  ormenos + cerberus + maenadsorceress(no proc) L44, charon both forms L43, yaoguai L41,
  pemphredo + bandari L40, deino + enyo L39, gargantuanyeti L38, barmanu L37, scarabaeus +
  permean L35, sandwraithlord L34, aktaios L33, grimshell L33, nehebkau L30, sandwraith L29,
  megalesios L27, minotaurlord L26, medusa L24, alastor L24, euryale L23, sstheno + arachne L22,
  toxeus (Athens) L21, calybe L20, nessus L15; notable Hero-class: sp_toxeus L99 (the SP
  superboss), wardenofsouls L48, insenzia/torak/koios L47-48 (procless souls - clean adds).
  Regeneration script (re-runnable on any arz): session scratchpad `rank_summon_candidates.py`;
  full dump `summon_candidates_ranked.txt`.

- **FEATURE (Will 2026-07-09): throwing weapons in the campaign.** The mod already requires
  Ragnarok (Runemaster mastery, XPack2 world levels), so throwing weapons are available engine-side;
  they never drop in Acts 1-4 because vanilla loot tables only place them in Act 5. Wire thrown
  weapons into the campaign loot tables (and consider a thrown-weapon soul or two). Will: "we dont
  even have the throwing objects in the game (although I wish we did)".
- **DESCRIPTION CORRECTIONS for next metadata push (2026-07-09):** (1) known-issues still says the
  Uber Dungeon return is not wired - build30's M1 wired the crypt_floor1 native return door, remove
  that line; (2) requirements: state that MULTIPLAYER (joining a session) requires ALL expansions
  (Ragnarok + Atlantis + Eternal Embers) because the merged world declares all-DLC content
  (server-join "get DLC" bounce, confirmed by a real player 2026-07-09); single-player hard
  requirement stays Eternal Embers. Also warn the Steam "get DLC" redirect lands in an empty cart
  (Steam deep-link bug) - buy from the store pages directly.

- Contract suite - **BUILT + committed** (`tools/contracts/`, branch `feat/contract-suite`). One
  unified 51-contract, 5-lane suite (souls/summons/resources/map/quests) that subsumes BOTH the
  planned entity + map contract suites; every contract has a negative test proving it fires. Run:
  `py tools/contracts/run_contracts.py --arz … --levels-arc local/Levels_merged.arc …` (full
  command in PLAYBOOK §12). Run it before every deploy; fail-loud (exit 1 on any non-whitelisted
  P0/P1). **Against the build29-in-flight artifacts it (correctly) FAILS with 108 P1** on real,
  unfixed defects - do NOT weaken the contracts; fix the records:
  - `SUMMON-PET-CLASSIFICATION` x17 (soulskills pets carrioncrow/peng/… have no
    monsterClassification) -> **B-SUMMON-1** (the DB wave owns this).
  - `MAP-REF-1` x68 (SV `all_sv\creature\npc\dyer\*` NPCs + a few `proxies greek\*` pools are placed
    in Greek/Egypt town levels but never compiled into the arz -> silently fail to spawn) ->
    dropped-SV content (#28 / `DROPPED_CONTENT_AUDIT.md`); restore the records OR, if the dyer
    feature is cut-by-design, list them in `whitelist_map.txt` + `CUT_CONTENT.md`.
  - `MONSTER-SKILLS-LOOT` x10 (drxmap blood-cave `bodies\ancestralwarrior*`/`body01` reference a
    missing `Melee_Poison09-12_10.dbr` skill) -> **NEW**; add the skill or clear the ref.
  - `SOUL-NAME-RESOLVES` x8 (satyrmagi/satyrspiritcaller/kyrashadowdancer souls carry placeholder
    name tags `tagSoul1`/`tagSoulName` that resolve nowhere) -> **B-TEXT-TAGS-1 class**, new souls.
  - `SOUL-AUGMENT-LEVEL` x4 (crowboar_soul_n/e `augmentSkillLevel1/2 == 0` = dead +0 augments) ->
    **B-SOUL-PROC-1 residual** (build29 fixed itemSkillLevel but not these augment levels).
  - `MONSTER-SPAWN-ELIGIBILITY` x1 (`bw_priest_houndmaster` pool: championChance=100/championMin=2/
    spawnMax=2 crowds out its named `c_disciple_39`) -> the Blood-Toxeus no-spawn class, **NEW**.
  Build29 progress the suite confirms vs the frozen build27 baseline: 338 -> 108 P1 (SOUL-PROC-
  ACTIVATION 219->0 = B-SOUL-PROC-1; SUMMON-PET-NAKED 6->0; C-RES-TAGDUP-1 5->0 = B-MASTERY-LABEL-1;
  B-TEXT-TAGS-1 Crimson-Verdict tags now resolve). B-TEMPLE-DOOR/B-PORTAL coverage is already in
  (MAP-DOOR-1, MAP-PORTAL-1/2/3).
- Occult/Hunting mastery UI recheck (#35) - PARTIALLY ROOT-CAUSED 2026-07-08 (B-MASTERY-LABEL-1):
  the mastery SELECT screen shows 'Rogue' because modstrings.txt defines tagSkillName050 /
  tagMasteryBrief05 / tagMasteryTitle05 TWICE (SV's Rogue lines first, the Occult fix block appended
  later; the engine keeps the FIRST definition) and tagMasteryDescription05 still carries vanilla
  Rogue flavor text. Fix = suppress OCCULT_FIX_TAGS keys during per-file emission in
  tools/build_text_arc.py + add tagMasteryDescription05 Occult copy (Will signs off wording) + a
  fail-loud duplicate-tag gate. Owned by the 2026-07-08 DB wave. The in-tree name is correct;
  other masteries are unaffected (single definitions).
- Souls quality pass vs SV originals (#31).
- Toxeus encounter suite: 10-25% canonical entrance spawn, rant scroll (MP per-player), Legendary
  stalker feasibility, 6-player checklist (#32).
- Comprehensive dropped-visuals restoration (#28).
- Cold Tombs (#36) - ON HOLD per Will.

## QUEUED FEATURE: NEW-HERO-PARNASSUS-HOUND (APPROVED by Will 2026-07-14, not yet scheduled)
Will (verbatim): "add a new uber hero to the back corner of the parnassus caves. he could be a
massive fire breathing dog one of the black hounds that breathe fire and he could have other
crazy skills too."
- **Identity:** a massive black hound of the fire-breathing hound family (use the base/SV black
  hound rig that already carries a breath attack as the donor; scale up per the Ephialtes/Mnemophage
  size precedent, watch ceiling clearance in the cave interior). Name/lore to the amgoz1 bar
  (amgoz1_design_voice.md): monster-identity-driven - a hound of Parnassus's depths, fire/ash
  themes; name flagged for Will veto.
- **Kit:** signature fire breath + 2-3 "crazy" donor-based skills at the amgoz1 bar (e.g. leaping
  pounce, ember howl/summon ash-pups, flame trail - designer picks proven-shape donors; boss_skill_fix
  discipline: skills must actually cast, donor-matched levels).
- **Placement:** the BACK CORNER (deepest dead-end) of the Parnassus Caves (Greece Act 1) -
  implementation surveys the level's 0x0b navmesh for the deepest on-mesh pocket with boss+adds
  clearance (survey_uberboss_spots.py), q_<boss>_lone single-spawn proxy (chance TBD by Will -
  default guaranteed like other placed ubers), landing-clearance + containment gates.
- **Rewards:** 3-tier soul ({^F} tags, per-tier icons, granted skill = his identity e.g. the fire
  breath); 3 region-tuned Majestic Chests per the b42 standard.
- **Standard lanes:** DB records via registry module; tags via manifest; INJECT_SPECS placement;
  full gate battery; Will fresh-char verify on DEV after ship.

## QUEUED FEATURE: NEW-RELIC-DIONYSUS-TRICKSTER (APPROVED by Will 2026-07-14, not yet scheduled)
Will (verbatim): "dionysus trickster archers should get a custom relic they drop like the magneta
turtle shell."
- **Pattern to follow (ground-truth it first):** the mod's magenta turtle shell custom relic -
  locate its records in the effective arz (relic/charm item class, shard vs complete mechanics,
  completion bonus table, {^F}/magenta name coloring, icon) and its DROP wiring (which monsters,
  which loot slot/table, what rate). Clone that exact shape - do not invent a new mechanism.
- **Identity:** a custom relic themed to the Dionysus trickster archers (wine/revelry/madness/
  trickery - e.g. intoxicating shot, maddening draught themes). Name + flavor + completion
  bonuses to the amgoz1 bar (amgoz1_design_voice.md); name flagged for Will veto.
- **Drop wiring:** dropped by the Dionysus trickster archer monster family (identify the exact
  records - the satyr trickster archers of the Dionysus cult area; wire ALL family variants/tiers
  N/E/L like the turtle-shell precedent, matching its rate).
- **Standard lanes:** DB records via registry module; tags via manifest ({^F} discipline);
  validate_tags + contracts green; dry-run replay intended-records-only; Will fresh-drop verify
  (TQ bakes item properties at pickup - test with a freshly dropped relic).

## QUEUED FEATURE: NEW-HERO-WARCAMP-SKELETON (APPROVED by Will 2026-07-14, not yet scheduled)
Will (verbatim): "add a new uber hero (new skeleton staged uber hero (kill him multiple times like
the legion monster) each time he respawns he gets bigger and stronger and new skills, give him 3
stages. this new uber hero will go in the back corner of the Upper War-Camp before Medusa."
- **Mechanism donor:** the Legion multi-stage death-transform chain - ground-truth it from
  docs/reports/b56_legion_soul_stages.md (the 2026-07-14 Legion lane mapped the exact stage-chain
  wiring) and clone that proven shape. THREE stages: each death spawns the next form.
- **Escalation per stage:** bigger (scale, mind interior ceiling-clip headroom per the
  Ephialtes/Mnemophage lesson), stronger (HP/damage stepped up), and NEW skills each stage
  (donor-based, proven-shape, boss_skill_fix discipline: must actually cast; stage 3 = the full
  crazy kit). Skeleton rig family; amgoz1-bar identity (a thrice-risen war-camp revenant class
  concept; name/lore flagged for Will veto).
- **SOUL LAW (hard):** soul drops ONLY on the FINAL (3rd) stage - must pass the
  legion_soul_stages verify gate (no chain with >1 soul-bearing stage). 3-tier soul, granted
  skill = his identity.
- **Placement:** the BACK CORNER of the Upper War-Camp (Greece, before Medusa/the Gorgons) -
  navmesh survey for the deepest on-mesh pocket with clearance for the LARGEST (stage 3) form,
  q_<boss>_lone single-spawn proxy, landing-clearance + containment gates; verify the stage
  respawns happen in place (the chain spawns at death location - confirm clearance holds).
- **Rewards:** 3-tier soul + 3 region-tuned Majestic Chests (b42 standard, Greece-tuned).
- **Standard lanes:** DB registry module; tags via manifest; INJECT_SPECS; full gate battery;
  Will fresh-char verify on DEV.

## QUEUED FEATURE: NEW-UBER-FORMULAS-FROM-ORPHANS (status: approved-concept-by-Will-2026-07-14, awaiting his candidate selection)
Will (verbatim): "are there any cool orphaned weapon records that we could use to make new uber
weapons behind? some uber forge formula weapons. add this to the backlog." Full audit +
curated candidate detail + design sketch + reproduce steps: **`docs/reports/orphaned_weapons_curation.md`**.
- **Finding:** the effective DB holds 4,360 weapon records - 3,007 obtainable, **1,069 orphaned**
  (1,054 referenced by nothing; verified across 3 independent vectors), 284 junk. Plenty of "cool"
  orphans (proper name + distinctive art and/or granted skill + lore) to reskin into supra ubers.
- **Proven template (already in-repo):** SVC already added 3 thrown ubers this exact way -
  `svc_thrown_charonstoll/lastword/sanguineorbit` formulas -> `svc_wep_*` results, wired into BOTH
  `records\xpack\item\loottables\arcaneformulae\supra.dbr` + `supra_special.dbr`. Clone that path.
- **Per-candidate build (each pick):** buff/author the result at `records\drxitem\supra\svc_wep_<name>.dbr`
  (lvl-65 Legendary, `numRelicSlots=1`, supra-tier stats, identity-themed `itemSkillName` proc +
  `weaponTrail`; KEEP the orphan's mesh/skin/bitmap - add a bespoke DRX trail for shared-mesh picks,
  Blood Whisper style; picks already at L70-79 usable near as-is). Formula = new `zrecipes\svc_<class>_<name>_formula.dbr`
  OR **reuse one of the 24 orphaned `zrecipes\` duplicate formula shells** (repoint `artifactName` +
  reagents + `description`; the live `recipes\` twin still crafts the original). Recipe name to the
  amgoz1 bar (amgoz1_design_voice.md): **"Mythic Formula - <name>"**; reagents = **2 Legendary + 1 Rare
  thematically matched** to the weapon (per-candidate themes in the report). Add the formula to BOTH
  supra drop tables; add tags via manifest (validate_tags green; arz + Text.arc ship together).
- **Curated menu (14 + 8-axe bench; Will picks which to build - see report for pitches/paths/reagents):**
  Ripulsar & Aquimae (Sword, bespoke lost DRX blades, 0-twin); Helona (Staff, grants a summon);
  Hati (Thrown, Norse moon-wolf, bespoke, 0-twin); Sword Fish (Mace, the joke secret uber, 0-twin);
  Phoenix (Axe, has a live Heat Shield skill); Erysichthon's Hunger / The Furies (Axe, Greek lore);
  Scylla + Charybdis (paired sea-terror Axes); Heartpierce & Doom Herald (DRX cursed-egg Sword/Mace);
  The Munderizer (Staff, the Munderbunny insider egg, magenta name); Di Jun's Pride (Bow, solar,
  rename). Bench: 8 more Greek Legendary axes (Acheron's Touch, Axe of Tereus, Persephone's Caress,
  Torment, Shai'tan, Atropos' Assistant, Enkidu's Stand, Theogenes' Onslaught).
- **Honest gaps:** NO quality orphan Spear (Blood Whisper already the supra spear) or Shield - a new
  spear/shield uber must be authored fresh, not sourced from an orphan.
- **Twin caveat:** shared-mesh Greek axes + the DRX eggs have a live name-twin (droppable item of the
  same name) - the orphan RECORD is still unreferenced/safe, but rename the uber (or frame it as an
  "ascended" variant) and give it distinctive art. 0-twin picks (Ripulsar, Aquimae, Hati, Sword Fish,
  Munderizer) have a fully free identity.
- **Standard lanes:** DB records via registry module; tags via manifest ({^F}/{^r} discipline);
  dry-run replay intended-records-only vs baseline; validate_tags + supra dead-ref invariant green;
  Will fresh-drop verify on DEV (TQ bakes item props at pickup - test a freshly crafted item).

## FIX-ROUND BATCHING NOTE
All the P0/P1 map items (B-PORTAL-1/2/3, B-SPRITE-1, B-SMOKE-1, B-TEMPLE-DOOR-1) share the map
lane → batch into one implement→vet wave, rebuild BOTH artifacts (canonical + TESTHUB), coupled
deploy. The DB items (B-SUMMON-1, B-TOXEUS-1) share apply_svc_patches → one DB wave. B-TEXT-TAGS-1
rides that DB wave (arz + Text.arc ship together). Portals touch BOTH lanes (record fields = DB;
placement = map) - coordinate.

## 🌐 WORKSHOP FEEDBACK (triage inbound player reports here)

The Workshop item (3759792705) is PUBLIC, so players will report problems via **Workshop comments**
and ratings on the item page. There is no automated inbox - Will (or an agent, if he pastes them in)
must read the comments periodically and triage each report INTO THIS BOARD:

1. Reproduce or map the report to an existing item (many will be B-PORTAL-* / B-SUMMON-1 / the raw
   tags B-TEXT-TAGS-1, already known). If it matches, note "also reported on Workshop" on that item.
2. If it is new, file it here with a `B-<AREA>-N` id, the player's description (verbatim), a
   reproduction/cause hypothesis, and the fix lane - same shape as the items above.
3. Distinguish **mod bugs** from **install/environment issues** (missing 4GB LAA patch, loaded a
   normal character into the Custom Quest, base-game version mismatch, subscribed-but-not-downloaded).
   Environment issues → answer in a Workshop reply + capture the FAQ in `docs/SHARE_AND_PLAY.md` /
   `docs/STEAM_RELEASE.md`; do not clutter the bug board with them.
4. When a fix ships, note the build/commit and (optionally) reply on the Workshop comment so the
   reporter knows it is addressed.

Standing watch items likely to draw comments until fixed: the 8 raw tags (B-TEXT-TAGS-1) are visible
to every subscriber right now; portals look rough (B-PORTAL-1). Prioritize those before a wider push.

## ✅ RESOLVED / VERIFIED

### M14 (build31e, 2026-07-10): dead-content-audit small items - dev quest de-registered + stray tombstone de-placed
- `testquesttoopendoors.qst` DE-REGISTERED from the QUESTS(0x1b) load window (was idx 101 - a
  leftover dev quest duplicating door unlocks on unverified conditions and burning a slot of the
  256 window). Registry is now 255 entries; boundary pair (hcdungeon_control + x2_StartQuest)
  intact; quest identity is name-keyed so the post-101 index shift is neutral; one slot FREED for
  future registrations (e.g. z_primrosecontroller if the Primrose secret is ever un-mooted). The
  .qst stays in the arcs harmlessly (never loads). `DEREGISTERED_NATIVE_BASENAMES` +
  fail-loud asserts in svaera_plus_portals.build_ordered_quest_list.
- The stray Atlantis `tombstone.dbr` (locked FixedItemQuestObject, dev placeholder description
  'Hogge', zero quest refs) DE-PLACED from Greek MonsterCave01B (was inst [58]).
  `REMOVE_STRAY_PROP_SPECS` in build_section_surgery.py; the only level blob the build31e wave
  changed (per-level byte-diff proof; M13a lives in the world GROUPS/QUESTS sections).

### B-STARTER-CHEST-1 + B-STARTER-CHEST-2: starter chest RESOLVED (build30.2, in-game verified 2026-07-09)
- **Symptoms:** (1) Will 2026-07-08: the chest should drop 12 inventory bags + 36 potions for co-op;
  (2) Will, live build30: opening the starter chest drops NOTHING (not even potions).
- **ROOT CAUSE (validated end-to-end via DEV A/B tests):** build28 (5af85d3) replaced the record's
  native RunEquation numSpawnMin/MaxEquation '3+(2*numberOfPlayers)' with the bare integer literal
  '48'. The engine evaluates the bare-literal form to 0 on this container -> numSpawn 0 -> the
  WHOLE chest dead (including the untouched potion slot) through b28/b29/b30. The chest had dropped
  bags since v1.0 (17257c8: loot2+loot3 = startingloot_sack at chance 100, native equation); every
  build27-era deployed arz (e.g. c4aa4d75) drops. The build30.1 "byte exoneration" compared
  build30-vs-build29 = broken-vs-broken, and its bare-literal precedent (boss_tartarus min/max='1',
  a different container) did not transfer. Decisive in-game datapoints: SV-original byte-restore
  (arz 39174e9c) = potions drop; equation-form fix (arz c959a372) = potions + bags drop ("that
  worked perfect" - Will 2026-07-09); the literal builds = nothing.
- **FIX (build30.2, grant_all_inventory_bags in tools/build_svc_database.py):** numSpawnMin==Max =
  '46+(2*numberOfPlayers)' (equation FORM, 48 solo, scales co-op like the original); ONE active
  slot loot1Chance=100 with dual tables Health_01-05All w108 : startingloot_sack w36 (3:1 ->
  E[36 potions + 12 bags]; multi-table slots = ubiquitous base FixedItemLoot precedent, e.g.
  defaultloot\hiddenchest_greece_00-15); loot2..6 restored to the record's NATIVE inert shape
  (chance 0, weights 0, NameN fields DELETED not blanked - an empty-string .dbr ref is the
  B-TOXEUS-2 zero-precedent loader-abort shape); NO soul (build29's sow slot stays removed).
- **LESSON (standing):** RunEquation-typed fields require equation-form values - bare integer
  literals can silently evaluate to 0. Byte precedent does not transfer between containers, and
  a byte-diff against another broken build proves nothing: in-game verification is MANDATORY for
  engine-facing constructs.

### A10 SUMMON-THE-BOSS SOULS: Narok the Rockskin + Vort the Red (build29, owner request)
- Both souls now GRANT A MANUAL-CAST SUMMON OF THEIR OWN BOSS (the Boneash-proven pattern:
  pets cloned from Lyia Leafsong's Pet.tpl baseline, rig/skills replaced with the SOURCE
  monster's own, loot-table equipment via _set_pet_equipment, permanent companion, no autocast
  controller). Narok = um_rockskin_42 (storm/spirit staff caster, Ternion + storm orbs); Vort =
  hero_tarthon_na'arak_40 (the record that DISPLAYS "Vort the Red" via tagMonsterName1139 - the
  SV filename mismatch is upstream). Summon skills records\skills\soulskills\summon_{narok,vort}
  .dbr: 250/300/350 energy, 180s recharge, 3-tier pet ladder, boss-name pet nameplates.
- NEEDS WILL SIGN-OFF (aggressive-but-sane per "way more powerful"): Narok pet life
  9500/14000/20000 (source floor 9.3-13.9k), INT 450 STR 250 DEX 200, dmg 60-90/90-140/130-200,
  scale 1.3; Vort pet life 18000/26000/36000 (source floor 17.8-26.8k), STR 450 DEX 350 INT 400,
  dmg 70-100/105-160/150-230, scale 1.55 (source). Soul lines: rockskin ternion augment 3/4/5 ->
  6 uniform, +250 life, mana penalty -80 -> +150, +25% cast, +25 fire res; vort concussive blast
  2/3/4 -> 5 uniform + NEW thunderball augment 4, +200 life/mana, +30% cast, +25 lightning res.
- Gated by: summon-pet chain validator, castability (no special anim), clone-shape rules,
  record-diff enumeration. Fail-loud: a missing source record now ABORTS the build (was a
  print-and-continue WARNING for all pet summons).

### A6 HUNTING BOLT TRAP = FOUND, ALREADY LIVE (build29 decode, REPORT-ONLY - no change made)
- Will's memory of "a custom-modded bolt trap in Hunting" is CORRECT and matches the SHIPPED
  build28 artifact: Hunting (mastery UI slot 6) slot 19 = records\skills\hunting\drxmonsterlure.dbr,
  display name "Lay Trap" (tagSkillName083), Class Skill_AttackProjectileSpawnPet, spawnObjects =
  the full 20-level bolt-trap pet ladder (records\skills\hunting\drxpet\bolttrap_01..20, mesh
  Effects\Hunting\TrapTikiCrossbow.msh, attack = bolttrap_defaultattackskill
  Skill_AttackProjectileBurst, petLimit 3-5, TTL 30s, monsterClassification Common, NO special
  anim = castable). SV 0.98i upstream had the same design but wired only levels 1-2 in
  spawnObjects; the shipped 20-level ladder is richer (hand-tuning). Modifier slots: 20 =
  drxmonsterlure_petmodifier_detonate, 21 = drxmonsterlure_rapidconstruction. Separately, the
  OCCULT tree (slot 5) carries drxlaytrap ("Breach") + drxlaytrap_petmodifier_multishotbolttrap.
  NOTHING to fix; tree untouched per the hand-tuning law.

### A9 SUMMON-PET RENDER-CHAIN VALIDATOR = LIVE (build29)
- tools/validate_render_chain.py, wired into build_svc_database post-write: every soul-granted
  summon pet's mesh + baseTexture + status icons and the summon skill's bar icons must resolve
  in the shipped arcs (mod Resources + game Resources[/XPack*]; TQ archive-name resolution incl.
  the XPack second-component convention). Mod-authored pet mesh/texture = FAIL (invisible-pet
  class of bug); icons + upstream records = WARN. build29: 203 pets / 2852 art refs checked,
  PASS with ~22 upstream WARNs (known cosmetic debt now visible: thunderballnova + some soul
  party icons, albinospider/formicid upstream meshes). Negative-tested (bogus mesh on a mod pet
  correctly fails the build). NOTE: the gate needs the standard work/ layout (a Resources dir
  beside the arz output + the game dir from the base-arz argument); an isolated rebuild to a
  scratch dir SKIPS it loudly instead of false-failing every mod art ref.

### A7 GOLDEN FREEZE GUARD = LIVE (build29)
- tools/occult_hunting_golden.json (generated from the build28 SHIPPED pair arz c4aa4d75 + Text
  38d6582a) freezes the owner's hand-tuned Occult (slot 5) + Hunting (slot 6) state: 125 records
  (UI slots/panectrl x3 priorities/positions + every tree skill + 1 hop of buff/pet delegation
  payloads) + 110 name/desc tag definition lists (per-file, in order - first-definition wins).
  Fail-loud gates: build_svc_database post-write (DB half) + build_text_arc post-write (full
  pair). ANY drift fails the build unless its printed key is added to owner_approved_overrides
  with Will's sign-off. Negative-tested (record-field, tag-value, and tree-membership mutations
  all caught). Validator: tools/validate_mastery_golden.py (also runs standalone).

### B-CHEST-1: Esfri's chest = WORKING AS DESIGNED, one-time per character (RESOLVED 2026-07-08)
- Exhaustive recon (shipped arz + Quests.arc + SV 0.98i upstream, byte-level): the chest
  (proxy_hidden_bloodcave_chest -> hidden_bloodcave_chest_0{1,2,3}, Champion-locked
  FixedItemContainer) drops random gear/gold from its own table; the SUPRA FORMULA comes from the
  QUEST ACTION on Condition_UseFixedItem: Action_BestowTriggerToken('OpenedHiddenChest') +
  Action_GiveItem(supra_special) = exactly ONE random supra formula (1 of 25) placed SILENTLY into
  the bag (placeholder notification tags, see B-SUPRA-NOTIFY-1). The token is permanent per
  character and a Disable Chest trigger kills the proxy on every later level load: NO re-open, ever,
  for that character (not a session-reset chest, by design). The 'entering the area grants a
  formula' memory is REFUTED for BOTH our build and SV upstream (quest logic byte-identical).
  Will action: check bags/caravan for an unnoticed supra recipe scroll; a NEW character can earn
  one again. Quest confirmed inside the load window (idx 97/256) in the shipped map.

### POTIONS VERIFIED DROPPING (2026-07-08, recon + adversarial verify, both PASS)
- Skill point (2), attribute point (2), and experience (48) potions are all present in the shipped
  arz, fully wired, and actively dropping: they ride the SAME live rare-misc loot slot as relics
  across ~1,956 creatures (all acts x N/E/L), deliberately rare (roughly 0.006% common to ~0.5%
  boss per kill for a specific skill/attr potion); exp potions are ALSO sold by Greece market mages
  and all three types are forge-craftable. Progression gating by act is intentional data. No fix
  needed; do not re-investigate. (Reproduce: audit scripts referenced in the 2026-07-08 session.)

## ✅ RESOLVED: deploy / packaging

### B-WORKSHOP-PKG-1: Workshop item shipped as two broken mods "database" + "resources" (FIXED 2026-07-08, commit 1851203, tag workshop-wrapper-fix)
- **Symptom:** subscribers to item 3759792705 saw TWO broken mods "database" and "resources"
  instead of one "SoulvizierClassic". Root cause: package_workshop.ps1 staged database/ and
  resources/ as direct children of the vdf contentfolder, and SteamCMD uploads the contentfolder's
  CONTENTS, so the item root had no SoulvizierClassic wrapper (TQAE treats each top-level folder of a
  workshop item as a mod name).
- **Fix:** package_workshop.ps1 now stages to dist/workshop/content/SoulvizierClassic/{database,
  resources} and upload_workshop.ps1 points the vdf contentfolder at dist/workshop/content (whose
  only child is SoulvizierClassic). The packager wipes the stale wrapperless staging each run,
  asserts the content root has exactly one child, adds a permanent fail-loud TESTHUB guard (aborts if
  the packaged Levels.arc MD5 equals local/Levels_merged_TESTHUB.arc), and prints the packaged
  Levels.arc size + MD5. Verified: canonical map A1BA5DB2F00FFA067A808753A2E1EAC5 (688,691,849 B)
  matches the published copy; 53-file package; item root = a single SoulvizierClassic folder.
  **Re-uploaded and verified LIVE (2026-07-08): a fresh steamcmd download of item 3759792705 shows the
  item root = a single SoulvizierClassic wrapper, so the "two mods" bug is resolved on the live item.**
  Scripts: scripts/package_workshop.ps1, scripts/upload_workshop.ps1.

## build36 content wave ROUND-3 GATE RECORD (2026-07-12 ~00:00, supersedes the round-1 block)
- Round-2 fixes all landed: Charon soul = S2 one-summon (ferryman allow entry); Kravmoloch soul
  grants its summon; dedicated per-boss hoards (Tantalus/Charon/Ephialtes; Mnemophage chestless);
  Dorus soul silent no-op FIXED (non-pcsafe source ref) + new _verify_dorus_soul_amendment gate.
- Round-3 fix: oarsman pet tiers clear the donor's dangling ALL_DamageScaling_Passive (bfca9a5)
  - the B-SUMMON-1 gate caught it on the written arz.
- BUILT: arz md5 f5df1f05786439f6ec51c0fcf92e76c6 (55,184,822 B) local/build36c/Database/;
  Text.arc md5 744b598100ef07cac3a3e023f77a1586.
- GATES: all inline fail-loud gates GREEN in-run (5 invariants, 3 pet gates, golem button,
  B-SUMMON-1, C6 Dorus gate, F1/F2[17 fam]/F3/F6[63+2158], clone-shape 12, spawn-eligibility 25,
  roaming sweep, player-skill anims). A9 render chain PASS standalone vs real art arcs (28
  upstream WARNs - the in-run FAIL was the missing-art environment artifact; Resources populated).
  Golden PASS (5 F5 waivers, 0 other). validate_tags PASS. Contracts: souls 0/0/0, summons 0 P0/P1
  (112 pre-existing P2), resources 0 P0 + ONLY the pre-existing anm_dreamcopy P1.
- Determinism: round-1 proved byte-identical independent rebuild; the convergence rebuild on main
  re-confirms for the final artifact.

## build36 CONVERGENCE GATE RECORD (2026-07-12, ready to deploy)
- Convergence: Vort red skin (FiretalonA x4) + crash mitigation (bloodbeast petLimit 8->4) +
  q_enslaver_warband placement (drxfirstxistion_connection, surveyed 100%).
- Record-diff vs amendment 1b4a8835: EXACTLY 5 changed (4 Vort baseTexture + 1 petLimit), 0 add/rm.
- arz md5 63ca7cf858e4f60f2f9bec8f9eb4ef8f; canonical Levels_merged.arc md5 b42be44f891775f110262da74d714b32; Text.arc md5 2af4ce386578ea144177a3227e07e048.
- Quests.arc UNCHANGED in build36 (comment-only build_quest_files.py diff; A5 is DB-record-level) ->
  reuse the deployed 194092 B Quests.arc (the pre-existing Rhodes-guard build failure is orthogonal).
- GATES: DB inline all green; Text golden intact (5 waivers); canonical blob-diff = exactly 1 blob
  (drxfirstxistion_connection, the warband); navmeshes 24/24 0x0a-stripped; contracts_map PASS
  (0 P0/P1, 4 MAP-REF-1 cleared, warband resolves, 3 pre-existing native-portal P2); contracts
  souls/summons/resources green (only pre-existing anm_dreamcopy P1).
- SHIP MAP = CANONICAL to both Steam + DEV (TESTHUB rebuild skipped - quota; canonical carries all
  content, WILL_TEST_GUIDE.md gives the canonical path to every boss).

## BL-AURA-RADIUS (Will 2026-07-12, design wave candidate for build38)
Increase the effect radius of ALL auras in the game so a player's aura bonuses reach their
pets in battle even when not standing adjacent, and reach allied players on screen in MP.
Scope: every aura-class skill across masteries + soul-granted auras + pet auras.
Design notes: TQ aura radius lives on the skill record (radius/targetRadius fields per
aura template); approach = audit all aura records -> propose per-aura radii (a flat
multiplier is the fallback; screen-scale ~= 30-45m world units) -> balance check vs
always-on party-wide uptime -> H/O golden-freeze waivers where trees are touched ->
implement as registry module (aura_radius.py) with a fail-loud audit gate listing every
touched aura + old->new radius. NOT started (quota); spec-first per the vet law.

## RCA RECORD 2026-07-12 evening: "quests blocked / doors closed" on _Toxeus = SAVE-SIDE, NOT a shipped bug
Byte-level verdict (Opus RCA + Sonnet log check, wf_2c9d497c): Steam AND DEV both carry pure
build36 (all 4 files == baselines; QUESTS registry 255 entries, zero add/remove/reorder vs
build33/34/35, door controllers inside the load window). NO regression shipped; NO build36b.
True cause: repeated crash-loop (ntdll 0xC0000005, SAME offset 0x00062a29 three times:
07-09 20:14, 07-12 01:34, 07-12 16:41 = genuine heap-corruption family, NOT our taskkill)
corrupting quest/door progress mid-save (backup folder shows 0-byte Quest.myw fingerprint).
RECOVERY (Will): (1) close TQ fully, restart Steam, ONE clean reload -> door controllers
re-evaluate tokens on level load, doors should reopen (save retains full 259-quest tree);
leave the crash area immediately, save in town. (2) If progress truly lost: restore
backups/characters/20260709_155432 (or local/save_backups/_Toxeus_2026-07-06_1.zip) with TQ
CLOSED, guarding against Steam Cloud overwrite. NEVER touch a live save.
STILL OPEN: the original Helos->Garden walk-through P0 (never shipped - the hotfix workflow
was stopped pre-implementation twice); relaunched as wf_6f65899d with TQ-session guards
(deploys wait for Will's game to exit rather than killing it). Crash deep-dump analysis
running separately (wf_20582269).

## P0 CRASH PINNED 2026-07-12 (supersedes the hound-summoner framing) - BL-NAVLOAD-HEAP
Deep minidump analysis (5 dumps, 32-bit re-decode): heap corruption detonates inside the
NAVMESH-LOAD path - ProcessRLTD (Engine 0x101f4ba0) streaming deeper blood-cave chambers;
identical ancestor chain in 5/5 dumps; two stable ntdll allocator offsets = delayed
detonation. MAP-SIDE (Levels.arc): the arz petLimit mitigation was provably a no-op (dumps
byte-identical across DB changes). All 39 injected navmeshes validate -> runtime condition;
leading trigger = grid-seam-chain co-residency / dtTileCache tile-coordinate collision
(CAVE_ENTRY_CHAIN_TRACE.md). Kill-events were coincidental timing.
FIX WAVE (next P0, heavy - after build37-dev + Will's tour): confirm first (Frida live-probe
names the culprit chamber, hooks documented in docs/crash/DEEP_DUMP_ANALYSIS_2026-07-12.md;
or Page-Heap w/ Will's approval - registry change + OOM risk on 32-bit), then EITHER Fix B
cluster relocation to XZ-disjoint space (GRID_SHIFT + donor regen; entrance-seam risk at
Random09A/HiddenValley01 - preserve the abutment) OR interior GridEntrance transitions
between deep chambers (native streaming doors - NOT banned teleports - caps co-resident
navmeshes at 1-2). Player guidance meanwhile: save/portal-to-town often between chambers.
HYGIENE (separate, next DB build): 6 summoned-bloodhound dyingFxPak dangling refs ->
fxpak_deathfx_burst.dbr (real defect, NOT this crash).

## BL-ENSLAVER-SMOKE (Will 2026-07-12, tour finding #1, P2 visual - ride the next DB build)
Toxeus the Murderer, Enslaver of Souls (black skeleton leader) renders a GREEN smoke aura;
Will: it must be BLACK. Fix: swap the shroud FX ref on the Enslaver monster record(s)
(wild roamer + warband leader variants; check the Devourer variant is unaffected) to the
proven dark/black smoke FX (the Long Nu-style dark_smoke chosen in WILL_DECISIONS for the
Helepolis). LAW: FX go on the monster record (charFxPakRunningNames-style), NEVER charFxPak
on SpawnPet skills (build28 crash trap). Verify in the built arz + A9 render chain; add to
Will's next tour list.

## ✅ CONFIRMED 2026-07-12: Victory Portal -> EPIC works in-game (Will: killed Hades, portal,
## spawned into Epic). A5/Act-5 fix fully closed - no further action.

## BL-ENSLAVER-SPAWNS (Will 2026-07-12, tour finding #2, P1 balance - post-tour fix round)
In EPIC's first combat area Will met TWO side-by-side "Toxeus the Murderer, Enslaver of
Souls", each with 4 Enslaved Shadow Marauders, and the marauders took ~0 damage.
THREE fixes, one wave:
(1) DUPLICATE SPAWN: the build36 roaming-rare sweep lets adjacent proxies both roll the
    Enslaver. Audit every proxy/pool he was added to; prevent side-by-side duplicates
    (spacing the pools he's in / removing him from adjacent proxies of the same area).
(2) SPAWN RATE: reduce (Will explicit). He should be a RARE encounter, not a doorstep
    greeter in the first Epic field. Consider act/area gating of the roam pools entirely.
(3) MARAUDER TANKINESS: "deployed-demon strength" law + Epic difficulty scaling = near-
    immune marauders. Rebalance so they are killable elites in Epic/Legendary (check
    armor/resist/absorption stacking per-difficulty; they drop nothing, so sponge = pure
    frustration). Keep their DPS threat; cut their effective-HP wall.
Verify vs the warband placement too (the static blood-cave warband keeps its 4 marauders;
these fixes target the ROAMING variant's pools + per-difficulty marauder defenses).
