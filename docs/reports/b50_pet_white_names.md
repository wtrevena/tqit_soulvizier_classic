# b50 - Pet name color: Toxeus and his minions read RED as pets

**Status:** FIX IMPLEMENTED + dry-run VERIFIED (round 1). Branch `feat/b50-pet-white-names` off `d11d3c0` (build38a).
Fix commit `0cea96a` (RCA at `ddca8ed`). See the IMPLEMENTATION + VERIFICATION sections at the end.
**Report (Will 2026-07-13):** "when toxeus and his minions are pets, there names should be white not red."
**Ground truth:** `baseline_build38.arz` (== DEV/Steam arz `6631f252`) + shipped `work/SoulvizierClassic/Resources/Text.arc`.

---

## TL;DR

- A summoned pet's **displayed in-game name is its `description` field** (a Text tag name). Confirmed on 218 pet
  records: every `Class=Pet` record carries the name in `description`; `charName` is always empty.
- Six boss-summon pet families point their `description` at the **same name tag as the hostile world boss they were
  cloned from**, and that shared tag's TEXT **embeds a literal `{^r}` (red) color code**. TQ renders the embedded
  code verbatim, so the FRIENDLY pet's floating name reads RED exactly like the enemy - regardless of the pet being
  `monsterClassification=Common`.
- **Exactly 6 pet families / 18 pet records are affected** (proven against the deployed arz + shipped Text.arc). Every
  other pet (58 families / 200 records) is already plain/white. There are zero non-red colored pets.
- The 6 red tags are each shared **1 hostile world record : 3 friendly pet clones**. So the fix must **mint a
  separate white pet-name tag and repoint only the pet's `description`** - it must NOT edit the shared tag text
  (that would strip red from the hostile world boss too).
- **Cleanest data-driven fix point: a single post-pass `_whiten_pet_display_names(db, tags)` inside
  `run_registry_gates()`** (tools/apply_svc_patches.py ~16801). It runs over the FINAL assembled db (monolith +
  registry modules) with the fully-populated `tags` manifest, so one helper covers every family including the
  registry-module Hades Marshal - no hand-list.

---

## 1. Mechanism: how a boss-summon pet gets its displayed name

`_build_boss_summon(db, source_path, pet_paths, summon_skill, display_tag, desc_tag, ...)`
(tools/apply_svc_patches.py:9608) builds each pet by cloning a Lyia pet baseline, copying the source boss's rig, and
setting fields. The name-bearing line is:

```
9696:        sf(path, 'description', desc_tag)     # pet's displayed name  = desc_tag
```

- `desc_tag` is the pet's **display name** (the `description` field). Confirmed against the arz: every pet's
  `description` is the tag shown over its head / in the target frame; `charName` is unused (None on all 218 pets).
- `display_tag` is a **different** field - it is set on the SUMMON SKILL as `skillDisplayName`
  (line 9779), i.e. the "Summon X" button text, not the pet's world name. (Not the bug.)
- The color is NOT on the pet record and NOT a per-rank engine choice here: it is **embedded in the tag's TEXT
  string** (e.g. `{^r}...`). A `{^r}` prefix in the resolved string forces red on the floating name even though the
  pet is `monsterClassification=Common` (set at line 9698). Pets whose name string carries no code render in the
  engine's default friendly color (white) - which is what all the already-correct pets do.

TQ color codes seen in this file: `{^r}` red (hostile), `{^w}` white, `{^F}` magenta/pink (souls), `{^G}` green
(SV escort/minion flavor). Souls correctly use `{^F}`; hostile world monsters correctly use `{^r}`/`{^G}`.

### Confirmed from `baseline_build38.arz` + shipped `Text.arc`

Each affected tag is shared verbatim between exactly ONE hostile world record and its THREE pet clones:

| Shared name tag | Resolved TEXT (shipped) | Hostile world record | Friendly pet records |
|---|---|---|---|
| `tagMonsterHemorrheus` | `{^r}Toxeus the Murderer, Devourer of Blood` | `um_bloodtoxeus_99` | `bloodtoxeus_{1,2,3}` |
| `tagSVCMonsterEnslaver` | `{^r}Toxeus the Murderer, Enslaver of Souls` | `um_toxeus_enslaver_99` | `toxeus_enslaver_{1,2,3}` |
| `tagSVCMonsterEnslaverMarauder` | `{^r}Enslaved Shadow Marauder` | `um_enslaver_marauder_99` | `enslaver_marauder_{1,2,3}` |
| `tagSVCMonsterBroodmother` | `{^r}The Broodmother of the Deep` | `um_broodmother_99` | `broodmother_{1,2,3}` |
| `tagSVCMonsterVoranthys` | `{^r}Voranthys, the Sepulchral` | `um_voranthys_99` | `voranthys_{1,2,3}` |
| `tagSVCMonsterHadesMarshal` | `{^r}Menoetes, Marshal of the Dead` | `svc_um_hadesmarshal_80` | `hadesmarshal_{1,2,3}` |

This 1:3 sharing is the smoking gun and the reason the tag itself cannot be edited: `um_bloodtoxeus_99` etc. are the
hostile world monsters and must STAY `{^r}`.

Will's report ("toxeus and his minions") maps to the first three rows (Devourer-of-Blood Toxeus, Enslaver Toxeus,
and the Enslaved Shadow Marauder minions). The remaining three (Broodmother, Voranthys, Hades Marshal) are the
same bug on other bosses - included per the task's "fix all pets data-driven, not a hand-list."

---

## 2. Every `_build_boss_summon` (and A10) pet family + its name source

Rows marked **RED** are the bug. `desc` = the tag written into the pet's `description`.

### Monolith `_build_boss_summon` direct callers (tools/apply_svc_patches.py)

| # | Family | Call site | Pet records | `desc` tag | Color |
|---|---|---|---|---|---|
| 1 | Blood Toxeus (Devourer of Blood) | 9795 | `bloodtoxeus_{1,2,3}` | `tagMonsterHemorrheus` | **RED** |
| 2 | Enslaver marauders | 10158 | `enslaver_marauder_{1,2,3}` | `tagSVCMonsterEnslaverMarauder` | **RED** |
| 3 | Enslaver (Toxeus) | 10176 | `toxeus_enslaver_{1,2,3}` | `tagSVCMonsterEnslaver` | **RED** |
| 4 | Xeiwang | 10743 | `xeiwang_{1,2,3}` | `tagNewHero196` (`Xeiwang, Flame of Hatred`) | white |
| 5 | Huo-ren / Mountainblade | 10797 | `mountainblade_{1,2,3}` | `tagNewHero289` | white |
| 6 | Broodmother wyrmlings (pet-of-pet) | 13098 | `broodmother_wyrmling_{1,2,3}` | `tagSVCMonsterBroodmotherWyrmling` (`Broodmother Wyrmling`) | white |
| 7 | Broodmother | 13118 | `broodmother_{1,2,3}` | `tagSVCMonsterBroodmother` | **RED** |
| 8 | Voranthys | 13784 | `voranthys_{1,2,3}` | `tagSVCMonsterVoranthys` | **RED** |
| 9 | Tantalus - Famished Shade | 15194 | `tantalus_shade_{1,2,3}` | `tagSVCPetFamishedShade` (`Famished Shade`) | white (dedicated pet tag) |
| 10 | Charon - Oarsman | 15397 | `charon_oarsman_{1,2,3}` | `tagSVCPetOarsman` (`Drowned Oarsman`) | white (dedicated pet tag) |
| 11 | Mnemophage - Phantasm | 15620 | `mnemophage_phantasm_{1,2,3}` | `tagSVCPetMnemPhantasm` (`Stolen Nightmare`) | white (dedicated pet tag) |
| 12 | Kravmoloch - Bound Warden | 16253 | `kravmoloch_warden_{1,2,3}` | `tagSVCPetBoundWarden` (`Bound Warden`) | white (dedicated pet tag) |

### Monolith `_apply_group4_summons` jobs list (11875 -> built at 11969)

| # | Family | Pet records | `desc` tag | Color |
|---|---|---|---|---|
| 13 | D13 Eater of Days | `eaterofdays_{1,2,3}` | `tagNewHero91` | white |
| 14 | D14 Pygmalion | `pygmalion_{1,2,3}` | `tagNewHero262` | white |
| 15 | D20 War-King Sarpedon | `sarpedon_{1,2,3}` | `desc=None` -> source `um_sarpedon_41` desc = `tagNewHero281` | white |
| 16 | D21 Long Nu | `longnu_{1,2,3}` | `tagNewHero181` | white |
| 17 | D22 Meritamen | `meritamen_{1,2,3}` | `tagNewHero182` | white |

### Registry-module callers (tools/patches/*)

| # | Family | Call site | Pet records | `desc` tag | Color |
|---|---|---|---|---|---|
| 18 | Four Generals - Hades Marshal | four_generals.py:392 | `hadesmarshal_{1,2,3}` | `tagSVCMonsterHadesMarshal` | **RED** |
| 19 | Neferkha | neferkha.py:367 | `neferkha` pets | `tagSVCMonsterNeferkha` (`Neferkha ~ the Rimebound Pharaoh`) | white |

### Separate A10 builder `_create_boss_summon_from_source` (spec `_A10_BOSS_SUMMONS`, 825; loop 3302)

Uses its own `spec['pet_desc_tag']`; **does NOT append to `_SUMMON_PET_BUILDS`**.

| # | Family | Pet records | `pet_desc_tag` | Color |
|---|---|---|---|---|
| 20 | Narok the Rockskin | `narok_{1,2,3}` | `tagNewHero88` | white |
| 21 | Vort the Red | `vort_{1,2,3}` | `tagMonsterName1139` (`Vort the Red`) | white |

**Result: 6 RED families / 18 pet records** (#1,2,3,7,8,18). All other pet families already render white. The
whole-arz sweep (64 pet families / 218 records) found these 6 `{^r}` tags and zero other embedded-color pets.

**The mod already established the correct pattern** for the four newest bosses (#9-12): a dedicated plain
`tagSVCPet*` name for the friendly pet, separate from the hostile `tagSVCMonster*` `{^r}`/`{^G}` world tag. The six
red families are the older ones that never got that split. The fix generalizes that existing convention.

---

## 3. Recommended fix point (cleanest, data-driven, covers all)

### Why not the obvious options

- **Editing the tag text** (strip `{^r}` from `tagSVCMonsterEnslaver` etc.) is WRONG: the tag is shared with the
  hostile world boss (`um_toxeus_enslaver_99` ...), which must stay red. Proven in section 1.
- **Rewriting each call site / hand-listing the 6** violates "data-driven, not a hand-list" and misses future pets.
- **Stripping color inside `_build_boss_summon`** cannot work alone: at line 9696 the helper only knows the tag
  NAME (`desc_tag`), not its `{^r}...` text (the text lives in the `tags` manifest authored elsewhere, frequently
  AFTER the summon call - e.g. the Enslaver builds at 10176 but authors `tags['tagSVCMonsterEnslaver']` at 10226).

### The fix: one post-pass in `run_registry_gates()`

Add `_whiten_pet_display_names(db, tags)` and call it **near the top of `run_registry_gates(db, tags, ...)`**
(tools/apply_svc_patches.py:16801). This location is decisive because the build pipeline is:

```
build_svc_database.py:
  extended_tags = apply_all_extended_patches(db, _defer_gates=True)   # monolith content + tags
  run_registry(db, extended_tags)                                     # registry modules (four_generals!) mutate tags
  run_registry_gates(db, extended_tags, ...)                          # <-- runs over the FINAL db + full tags
  ... extended_tags written to uber_soul_tags.txt -> Text.arc (validate_tags gates it)
```

By `run_registry_gates`, the db holds **every** pet family (monolith + registry modules) and `tags` holds **every**
authored string (including four_generals' `tags['tagSVCMonsterHadesMarshal']`, four_generals.py:469). Mutating
`extended_tags` here still reaches the manifest (it is iterated at write time), so any minted white tag ships in
Text.arc and passes `validate_tags`. (Direct callers that pass `_defer_gates=False` run `run_registry_gates` at
apply_all_extended_patches' tail; they have no registry modules, so the 5 monolith red families are still covered
and nothing regresses.)

### Algorithm (self-limiting, no hand-list)

```
def _whiten_pet_display_names(db, tags):
    for pet in <every Class=='Pet' record>:            # builder-agnostic roster (see note)
        dtag = db.get_field_value(pet, 'description')
        text = tags.get(dtag)                            # SVC-authored strings only
        if not text or '{^' not in text:                # base/SV plain tags -> already white -> skip
            continue
        if <no hostile color code, e.g. only {^w}>:      # optional: target {^r}/{^G}, leave {^w}
            continue
        white_tag = dtag + 'Pet'                          # deterministic sibling (idempotent)
        tags.setdefault(white_tag, _strip_leading_color(text))   # plain, matching house convention
        db.set_field(pet, 'description', white_tag)       # repoint ONLY the pet; hostile tag untouched
```

- **Roster:** iterate `Class=='Pet'` records (or restrict to `records\skills\soulskills\pets\`). This is the ONE
  fully data-driven roster that catches every builder - the monolith, the registry modules, AND the A10 path (which
  is absent from `_SUMMON_PET_BUILDS`). Keying the ACTION off "tag text has a color code" makes the pass a no-op on
  the 58 already-white families and self-limits to exactly the 6 red ones - no family list to maintain.
  (`_SUMMON_PET_BUILDS` is an acceptable alternative roster but would silently miss A10 Narok/Vort; they are white
  today so it is benign, but the `Class=='Pet'` roster is strictly more robust.)
- **White form:** strip the leading `{^r}` to PLAIN text, matching the six existing friendly-pet names
  (`Famished Shade`, `Drowned Oarsman`, `Stolen Nightmare`, `Bound Warden`, `Broodmother Wyrmling`,
  `Neferkha ~ the Rimebound Pharaoh`) which are all plain and render white. Equivalent explicit alternative:
  prepend `{^w}` (the task brief's suggestion) - visually identical; pick one and keep it consistent. Recommend
  plain-strip (house style + zero new assumptions about `{^w}` behavior).
- **Idempotent + resolves:** `white_tag = dtag + 'Pet'` is deterministic; `setdefault` is safe on re-run; the new
  tag is authored into `tags` so it ships and `validate_tags` passes. The hostile `dtag` string is never modified.

### What to leave alone (laws respected)

- Do NOT touch the hostile world records (`um_*_99`, `svc_um_hadesmarshal_80`) or their `{^r}` tags.
- Do NOT touch desc/description-tooltip tags, soul tags (`{^F}`), pet stats (PET-STAT-MIRROR), or pet skill kits
  (PET-SKILL-KIT). Only the pet's `description` (display NAME) field is repointed.
- New white tags must resolve in Text.arc (authored into the `tags` manifest) - the registry contract + tag
  pipeline stays intact; add the minted tags to any tag-authoring allow/whitelist if a gate requires it.
- No `clone_record` on souls; no explicit dtype on cloned records - the pass only calls `set_field(..., 'description',
  white_tag)` (string, existing field, dtype preserved) and mutates the Python `tags` dict.

### Compose with sibling waves

- **b40-soul-icons** already edited `_build_boss_summon` (added `_set_summon_skill_icon`) - the recommended fix
  does NOT touch `_build_boss_summon`; it adds an independent post-pass in `run_registry_gates`, so it composes
  cleanly.
- **b49** edits Enslaver constants (a different concern - stats/loot, not the display-name tag). No overlap: b49
  touches the Enslaver builder; b50 touches the shared post-pass. Coordinate only if b49 renames the Enslaver's
  `description` tag (it should not).

---

## 4. Verification performed (read-only)

- Enumerated every `_build_boss_summon` / `_create_boss_summon_from_source` caller (monolith + `tools/patches/`).
- Probed `baseline_build38.arz`: 218 `Class=Pet` records; `description` is the name field (charName always None).
- Resolved every pet `description` against shipped `work/.../Text.arc` (over base `Text_EN.arc`): 6 tags embed
  `{^r}`, 0 embed any other color, 58 are plain.
- Proved each of the 6 red tags is shared 1 hostile world record : 3 pet clones (section 1 table).
- Confirmed the tag->manifest handoff: `run_registry_gates` gets the shared `tags`; `build_svc_database` writes
  `extended_tags.items()` to `uber_soul_tags.txt` -> `build_text_arc.py` -> `Text.arc` -> `validate_tags`.

Probe scripts: `scratchpad/probe_all_pet_colors.py`, `probe_shared_tags.py`, `probe_pet_names.py`,
`probe_work_text.py` (session scratchpad).

**No source was modified. No build was run. TQ.exe / Steam untouched.** (RCA phase.)

---

## 5. IMPLEMENTATION (round 1, commit `0cea96a`)

Exactly as the RCA recommended: ONE data-driven post-pass, no hand-list, `_build_boss_summon` untouched
(so it composes cleanly with b40-soul-icons).

**New function** `_whiten_pet_display_names(db, tags)` (tools/apply_svc_patches.py, just before
`run_registry_gates`). Algorithm:

```
for rec in db.record_names():
    if db.get_field_value(rec, 'Class') != 'Pet':      continue   # friendly-pet roster only
    dtag = db.get_field_value(rec, 'description')                  # the pet's displayed NAME tag
    text = tags.get(dtag)
    if not text or '{^' not in text:                   continue   # plain -> already white -> skip
    white_text = re.sub(r'\{\^.\}', '', text).strip()             # strip the color code -> plain
    if not white_text or white_text == text:           continue
    white_tag = dtag + 'Pet'                                       # deterministic white sibling
    tags.setdefault(white_tag, white_text)                        # author into the tag manifest
    db.set_field(rec, 'description', white_tag)                    # repoint ONLY the pet
```

**Wired** as the FIRST action in `run_registry_gates(db, tags, ...)` (one call line + comment). That
location is decisive (confirmed against the pipeline):
`build_svc_database.py` runs `apply_all_extended_patches` (monolith tags) -> `run_registry` (registry
modules; four_generals authors `tags['tagSVCMonsterHadesMarshal']`) -> **`run_registry_gates`** ->
writes `extended_tags.items()` to `uber_soul_tags.txt` -> `build_text_arc.py` folds those into
`Text.arc` AND into the `mod_authored_tags.txt` manifest -> `validate_tags` gates it. So by the time
the pass runs, all 6 red tags AND all 18 pet records are present, and every minted `*Pet` tag ships to
Text.arc and passes `validate_tags`.

**Design choices (all per RCA):**
- **Roster = `Class=='Pet'`** (not `_SUMMON_PET_BUILDS`): the one fully data-driven roster that catches
  the monolith builder, the registry modules, AND the separate A10 Narok/Vort builder. It is also the
  correct SAFETY boundary - it never touches the hostile `Class=='Monster'` world records that share the
  tag, so the world boss/minion stays `{^r}` red.
- **Action keyed on "the name text embeds a color code"** -> a no-op on the ~1372 already-plain pets,
  self-limits to exactly the 6 colored families. Base-game monster names are plain (the engine colors a
  hostile red at runtime), so only the mod's own explicitly-`{^r}` tags are ever touched.
- **White form = strip the color code to PLAIN** (matches the mod's own convention: the four newest
  bosses' friendly forms - Famished Shade / Drowned Oarsman / Stolen Nightmare / Bound Warden - are all
  plain and render white). Idempotent (deterministic key; minted text has no code, so a re-run skips).
- **Laws respected:** no `clone_record`; `set_field` on the existing STRING `description` with NO dtype
  (type preserved); pet stats (PET-STAT-MIRROR), gear, skill kits (PET-SKILL-KIT), and desc-tooltip tags
  all untouched. Only the displayed NAME color changes.

## 6. VERIFICATION (no heavy build - dry-run replay on a COPY of the baseline)

`scratchpad/b50_dryrun_verify.py`: loaded a COPY of `baseline_build38.arz` (51,007 records; the built
arz whose pet `description` fields are byte-identical to what the pass sees in-memory), built the `tags`
manifest from the shipped `Text.arc` (all 6 red tags resolved verbatim to their source text), and ran
`_whiten_pet_display_names`. Result **PASS**:

- **All 18 red pet records whitened** (6 families x 3): `bloodtoxeus_{1,2,3}` (Devourer of Blood),
  `toxeus_enslaver_{1,2,3}` (the Enslaver), `enslaver_marauder_{1,2,3}` (his minions),
  `broodmother_{1,2,3}`, `voranthys_{1,2,3}`, `hadesmarshal_{1,2,3}`. Each pet's `description` is
  repointed to a plain `*Pet` sibling that resolves (e.g. `tagSVCMonsterEnslaver` ->
  `tagSVCMonsterEnslaverPet` = `Toxeus the Murderer, Enslaver of Souls`, no `{^r}`).
- **All 6 hostile WORLD records STILL `{^r}` red** (unchanged, not in the whited set):
  `um_bloodtoxeus_99`, `um_toxeus_enslaver_99`, `um_enslaver_marauder_99`, `um_broodmother_99`,
  `um_voranthys_99`, `svc_um_hadesmarshal_80` (all `Class=Monster`; their shared red tag is untouched).
- **Sample already-white pets UNTOUCHED:** broodmother wyrmling (pet-of-pet), Charon's Drowned Oarsman,
  Eater of Days, Long Nu, Meritamen, Huo-ren Mountainblade - all unchanged.
- **Global invariants:** whited-set == red-pet-set (exactly 18, no over/under-reach); all 6 minted white
  tags resolve and are plain; all 6 hostile red tags still `{^r}` in the manifest. A whole-arz sweep
  independently confirmed there are **exactly 6 colored pet families / 18 records** and zero other colored
  pets - the fix covers 100% of the bug with zero collateral.

**Gates:** `py -m py_compile tools/apply_svc_patches.py` OK; `tools/patches/_check_registry.py` selfcheck OK.

**Scope notes (curiosity findings, NOT defects in this fix):**
- **Kroisos:** no records in build38 at all (its boss-summon is not built in the ground truth). If a
  future wave adds a Kroisos boss-summon Class==Pet with a `{^r}` name, this data-driven pass whitens it
  automatically - no code change needed.
- **Dorus (b47's lane):** exists but has **zero `Class==Pet` records** in build38. Its `{^r}` entries are
  the hostile world monsters `um_dorus_99` and `svc_dorus_royalguard_71` (`Class=Monster`, correctly left
  red). `svc_dorus_raisecourt` is a `Skill_SpawnPetMonster` boss COMBAT skill (the hostile Dorus raises
  hostile adds), not a player pet. NOTE for integrators: a `Skill_SpawnPetMonster` that spawns a
  Monster-class entity as a PLAYER pet-of-pet is a DIFFERENT mechanism this `Class=='Pet'` pass does not
  cover (and must not, since the same record is hostile in the world). Not present in build38; flag for
  b47 if Dorus's court is ever made a player pet with an embedded-color name.
