# b47 - DORUS RENAME + RELOCATE (Will 2026-07-13)

> Branch `feat/b47-dorus` (base da918c5 = build38a). Round 1. No heavy build - dry-run
> replay/injection on COPIES only. Ground truth: canonical `local/Levels_merged.arc`
> (md5 60a62880), `baseline_build38.arz`. No em dashes.

## The bug (Will, verbatim)
> "dorus the king doesnt make sense where it is at in the great tomb of dorus. there is
> already a king dorus there. This character needs to get renamed, placed elsewhere. I
> must have meant to place this in another tomb or dungeon area near where this king dorus
> is, but this is totally wrong and doesnt make sense cause killing king dorus is part of a
> quest and now you just added two more king doruses right next to him that are even stronger."

Will's clarification: the quest is FINE, do NOT touch it. Another boss shares the name
"King Dorus" (the main-quest character); ours was placed standing right next to him.

## 1. RCA

**(a) Our boss + its records** (created by `apply_svc_patches._create_propontis_superboss`,
build36 A5; re-themed by C6 `_apply_dorus_amendments`):
- boss `records\xpack\creatures\monster\lostsoul\um_dorus_99.dbr` (Boss [41,57,71], HP
  13.5/18.5/24k, scale 1.6, crowned `xSQ06_Royalty_NonQuest.msh` rig, ThunderClap/ball +
  raise-court summon; C6 added coral-tsunami / rotten-grasp / dread-pall = a water/greed boss).
- escorts `svc_dorus_courtier_71` / `svc_dorus_royalguard_71`; summon `svc_dorus_raisecourt`;
  pool/proxy `q_dorus_lone`; hoard `svc_dorushoard_0{1,2,3}`; soul `drowned_king_soul_{n,e,l}`;
  TESTHUB yard `q_yard_dorus`.
- **OLD display name = `{^r}Dorus, the Drowned King`** (`tagSVCMonsterDrownedKing`); soul
  `{^F}Soul of the Drowned King` runtime, but SHIPPED as `{^F}Dorus, the Drowned King Soul`
  (a second definition lived in `_SOUL_NAME_STANDARD` and overwrote the runtime tag).

**(b) Where it was placed** (verified in the canonical map 60a62880 via the injection dry-run):
- Canonical placement M4 (`build_section_surgery.UBERBOSS_SPECS`): `q_dorus_lone` proxy in
  **Medea_TempleUG_Tomb01** (the Great Tomb of Dorus) at LOCAL (52,1.2,60) = **WORLD (312,-8462)**.
- The base-game QUEST King Dorus shade `xsq06_king_dorus` sits at WORLD (276,-8472) in the SAME
  level - **~37u away**. So a player walking the xSQ06 "Hidden Treasure of Dorus" tomb meets
  our Boss ("Dorus, the Drowned King", HP 24k) right beside the quest's own King Dorus. Exactly
  Will's "two more king doruses right next to him, even stronger" (the second "more" = the
  q_<boss>_lone duplicate that b42 fixes template-wide).

**(c) Name check (light, per Will - quest is fine, no quest-wiring RCA):**
- The REAL quest King Dorus = record `records\xpack\creatures\monster\lostsoul\xsq06_king_dorus_41.dbr`
  (Hero, HP 3500) + its map instance `xsq06_king_dorus` (Tomb01 inst[37]). **We NEVER edit it.**
- Ours (`um_dorus_99`) is a SEPARATE record, CLONED FROM that donor (read-only clone source).
  Two distinct records with a colliding DISPLAY name. Confirmed: the rename + relocate touch
  ONLY our records/placement; `xsq06_king_dorus_41` and its Tomb01 instance are byte-untouched.

## 2. RENAME -> **Kroisos, the Coin-Drowned**  [FLAGGED FOR WILL'S TOUR VETO]

A DISTINCT identity, not a King Dorus. **Kroisos** is the myth-byword for wealth ("rich as
Croesus"); a greed/hoard identity that fits the crowned drowned-royalty rig AND the C6
water/drowning/greed kit, and slots into the mod's real-Greek uber roster (Tantalus, Charon,
Mnemosyne, Ephialtes) as its "wealth" member (Tantalus = hunger, Kroisos = hoarding). Clearly
not "King Dorus", and now in a different tomb entirely. amgoz1 voice: `<Name>, the <Epithet>`,
myth-grounded, epithet-driven.

| surface | OLD | NEW |
|---|---|---|
| boss nameplate | `{^r}Dorus, the Drowned King` | **`{^r}Kroisos, the Coin-Drowned`** |
| soul (marquee) | `{^F}Dorus, the Drowned King Soul` | **`{^F}Soul of the Coin-Drowned`** |
| soul desc | "Torn from Dorus, the last king of Propontis ..." | re-themed to Kroisos/greed (no Dorus, no King) |
| TESTHUB traveler | `Traveler: Medea Tomb (Dorus)` | `Traveler: Tomb of the Queens (Kroisos)` |
| royal-guard escort | `{^r}Drowned Royal Guard` | unchanged (collision-free) |

- Internal record ids (`um_dorus_99`, `q_dorus_lone`, `svc_dorus_*`, `drowned_king_soul_*`,
  tag KEYS) are UNCHANGED - never player-visible; only display TEXT changes. This keeps the
  proxy -> pool -> name chain, the orb map, and C6 intact and low-risk.
- Soul naming pipeline (the tricky part): moved `tagSVCSoulDrownedKing` INTO
  `_HAND_DESIGNED_SOUL_TAGS` and OUT of `_SOUL_NAME_STANDARD` (the Anapaest precedent) so the
  bespoke "{^F}Soul of the Coin-Drowned" WINS end-to-end and passes the `_verify_soul_naming` gate.
- **Alternates for Will:** (2) `Kroisos, the Sunken Miser`; (3) impersonal `the Coin-Drowned`.

## 3. RELOCATE -> **Tomb of the Queens (Medea_TempleUG_Tomb03)**, deep south vault

Survey (`scratchpad/survey_dorus_relocate.py` over the canonical map) of the two candidate
sibling tombs "near where King Dorus is":

| candidate | verdict |
|---|---|
| **Tomb03** (Tomb of the Queens of Dorus, v0x11, corner (353,0,-8168)) | **CHOSEN.** NO named royal/quest char (0 king/queen/aegimius hits); a lost-soul court (sarcophagi + undead ambushes = the drowned court he raises) + 4 golden treasure chests (hoard continuity); one dominant nav component (259,143 cells). |
| Tomb02 (v0x0e, corner (-592,0,-7884)) | REJECTED - contains `xsq06_king_aegimius` (another named king) + `medea_sister` NPC. Would REPEAT the exact "boss next to a named quest royal" mistake. |

**New placement: LOCAL (83.0, 1.0, 51.0) = WORLD (436, -8117)** - the deep SOUTH treasure vault,
~128u from the north crypt entrance (a proper "boss at the far end" descent), guarding the
southern golden chests. Tool-verified on the canonical map (`survey_uberboss_spots.py --base 72`):
d=0.14u, clr@4.0 100%/100%/100% (N/E/L), clr@6.0 100% all sets, comp#1/259143; nearest floor
instance ~11u, nearest golden chest ~18u (room for boss + 2 champion escorts + the raise-court
wave + b42's 3 majestic chests). v0x11 -> auto-routes through the proven `inject_into_0x05_v11`
base-72 branch (same as the 4 other build36 bosses).

- OLD Tomb01 placement REMOVED completely (host key + M4 coord + testhub return all moved).
  Append-only injection from a fresh base blob = Tomb01 returns to base-pristine (243 instances),
  **zero orphan proxy beside King Dorus.**
- The boss is now in a DIFFERENT level than the quest King Dorus - they can never share a screen.

## 4. Quest safety proof (light, per Will)
- `xsq06_king_dorus_41` (record) + `xsq06_king_dorus` (Tomb01 instance): NEVER edited. The diff's
  only `xsq06_king_dorus` mention is an explanatory comment. Donor is a read-only clone SOURCE.
- No Quests(.qst) logic touched except ONE boat-teleport COORD (the TESTHUB hub landing); the
  world-map QUESTS(0x1b) 256-window is byte-untouched (no `build_ordered_quest_list` change).

## 5. VERIFY (all green - `scratchpad/verify_b47.py`, dry-run on COPIES)
- **DB rename replay** (baseline_build38.arz copy): soul survives the naming standard un-flattened
  as `{^F}Soul of the Coin-Drowned`; `_verify_soul_naming` gate PASS (53 OURS-path souls OK); soul
  record `itemNameTag` KEY unchanged -> validate_tags-compatible; set memberships correct.
- **Map injection dry-run** (Tomb01+Tomb03 blob copies from 60a62880): CONFIRMED the shipped bug
  (Tomb01 has 1 q_dorus_lone at WORLD (312,-8462), ~37u from the King Dorus shade, and it is the
  ONLY mod proxy there -> clean removal). Injecting into Tomb03: 0x05 count 252 -> 253 (+1),
  proxy at LOCAL (83,1,51) flags=0 exemplar-rot; **ONLY the 0x05 section changed; the 0x0b navmesh
  is byte-IDENTICAL** (navmesh untouched); Tomb03 has NO named royal to collide with.
- `py_compile` OK (3 files); `_check_registry.py` OK (11 modules, order hash stable).
- Blob-diff scope: only the two intended level blobs change (Tomb01 loses the proxy on rebuild,
  Tomb03 gains it); all other level blobs + all navmeshes + QUESTS(0x1b) byte-identical by
  construction (no code touching them).

## 6. Commits (feat/b47-dorus)
- `803b9dc` b47 RENAME (apply_svc_patches.py)
- `c96eeca` b47 RELOCATE (build_section_surgery.py + build_quest_files.py)
- (this commit) docs: b47_dorus.md + b47_dorus_hub_retarget.md

## 7. Cross-wave dependencies (integration)
- **b39 hub-v2** owns the authoritative "Medea tomb (Dorus)" traveler -> apply
  `b47_dorus_hub_retarget.md` (new label + landing WORLD (428,-8113)). b47 applied the same to
  its own branch copy for coherence.
- **b42** owns the duplicate/template fix + the 3 majestic chests -> they apply at the NEW boss
  location: host `medea_templeug_tomb03.lvl`, boss LOCAL (83,1,51) = WORLD (436,-8117), clr@6=100%
  (room to ring the boss). Note: today the hoard rides as the proxy's DB accessory pool; if b42
  places map-side chests, use this pocket.
- **b44** landing-clearance gate: new landing (75,55)/WORLD (428,-8113) is clr@3.0 100% comp#1.
- **b48** hub-traveler audit: the Dorus traveler destination + labels changed per the retarget spec.
- **b45** (frame-bug containment moves): Dorus is a DESIGN-error move owned by THIS lane; b47 is
  authoritative if b45 also touched it.

## 8. Follow-ups / notes (not blockers)
- `docs/WILL_TEST_GUIDE.md` hub section still names the Dorus traveler's old label/area; update at
  integration (b48 owns hub QA docs).
- Internal record ids retain the `dorus`/`drowned_king` namespace by design (safe, invisible).
