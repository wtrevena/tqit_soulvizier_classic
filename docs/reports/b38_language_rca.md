# B38 Language-switch RCA + fix (Steam report: "cant change the language")

Lane: `feat/b38-language` (base d6ed889). Author: b38 language RCA+fix implementer.
Steam user 535044547: "cant change the language". Will promised publicly to look into it.

## TL;DR

- **Root cause (proven):** our mod ships a single, language-agnostic
  `Resources/Text.arc` (one `modstrings.txt`) that re-emits **~10,600 base-game
  vanilla tags with values byte-identical to the base game's English**. The
  TQAE engine loads the base per-language text first, then **overlays
  modStrings.txt on top regardless of the selected language**. So when a player
  switches to German/French/etc., the base UI/items/skills/monsters/dialog DO
  load localized, but our English overlay immediately **clobbers ~11,284 of
  those localized strings back to English**. The language switch therefore looks
  broken ("cant change the language").
- **It is NOT** "no text / raw tags / cannot open the menu." Vanilla content
  switches language, then most of it snaps back to English. Genuinely mod-only
  content (souls, SV areas, DRX skills) stays English in every language because
  no translation exists upstream (SV/DRX were English-only) - that part is
  unavoidable and expected.
- **Fix (implemented, this branch):** `build_text_arc.py` now DROPS any SV tag
  whose value is byte-identical to the player's base-game `Text_EN.arc`.
  Re-emitting those is a no-op in English (the engine resolves the same string
  from the base text underneath) but is exactly what clobbers other languages.
  Mod-owned + golden-frozen tags are never dropped.
- **Impact (dry-run proven, real code path):** modStrings shrinks 14,663 -> 4,063
  tags; **~93% of the clobbered localized strings are restored in every
  non-English language** (German 11,284 -> 770 clobbered); **provably ZERO
  English regression** (only byte-identical values were dropped).
- No heavy build was run (build machine is owned by another workflow). Fast
  gates only: `py_compile`, PowerShell parse, and a full dry-run harness against
  the real SV + base-game text.

---

## 1. How TQAE resolves text per language for a Custom Quest mod (engine rules)

Established from Engine.dll string/RE evidence plus the mod's known-working
English behavior.

### Rule 1 - base game text is per-language, selected by the language setting

`<game>/Text/` ships **13** per-language archives:
`Text_BR/CH/CZ/DE/EN/ES/FR/IT/JA/KO/PL/RU/UK.arc`. Engine.dll exposes a
`LocalizationManager` with `Language01`..`Language13`, `LanguageTag`,
`LanguageString`, `LanguageNumberForLocale`, and constructs the base text
archive name at runtime from a bare `Text_` prefix + the active language tag +
`.arc` (the literal `Text_EN.arc` is NOT in the binary; the `Text_` prefix and
`.arc`/`.txt` suffixes are, adjacent to `tagLanguage13`). So selecting German
loads `Text_DE.arc`, French loads `Text_FR.arc`, etc.

### Rule 2 - a Custom Quest mod overlays a SINGLE language-agnostic modStrings.txt

Engine.dll contains the fixed literal **`Text\modStrings.txt`** (NO `%s`, no
language variant). This is the custom-map/mod text override: **one** file,
loaded **regardless of the selected language**, layered ON TOP of the base
per-language text. Our `Resources/Text.arc` packs exactly one entry
(`modstrings.txt`) and it resolves this override (lookup is case/dir tolerant -
our root `modstrings.txt` satisfies `Text\modStrings.txt`).

### Rule 3 - the overlay WINS over base text (proven)

The mod redefines `tagMasteryTitle05` = "Occult Mastery" (base game value is the
vanilla Rogue-mastery label). In-game the select screen shows "Occult Mastery",
so **modStrings.txt overrides the base-game definition** of a tag. Overlay =
mod wins on any shared tag.

### Rule 4 - base text IS loaded underneath (proven)

Our `modstrings.txt` defines 14,956 tags but the base `Text_EN.arc` has 17,541;
**6,171 base-game tags are absent from our modstrings** (core UI, notes, DLC
strings). The live mod shows correct English for those, so the engine must be
resolving them from the base `Text_EN.arc` it loads underneath. This is the
premise that makes the fix safe: a tag we DON'T emit still resolves - from the
player's localized base text.

### Consequence for language switching

For a non-English player: base `Text_<LANG>.arc` loads localized, then our
single English `modStrings.txt` overlays and **wins on every tag it defines**.
Because our modStrings re-emits SV's entire English corpus (which is mostly the
vanilla tag set carried forward unchanged), the overlay clobbers a huge fraction
of the localized base text back to English.

---

## 2. Root cause, quantified

Measured from the live deployed `Text.arc` (SoulvizierClassicDEV) vs the base
game `Text_EN.arc`/`Text_DE.arc`:

| bucket | count | meaning |
|---|---:|---|
| our modstrings tags | 14,956 | (14,663 excluding uber soul tags) |
| genuinely mod-new (not in base EN) | 3,586 | souls / SV areas / DRX - English-only, unavoidable |
| overlap with base EN | 11,370 | **these clobber localized base text** |
| ...byte-identical to base EN | **10,651** | pure redundant re-emission, zero benefit |
| ...SV/DRX reworded vs base EN | 719 | intentional English rewordings (+ a little junk) |
| German strings forced to English (before) | **11,284** | == the visible "cant change language" bug |

**71% of our modStrings.txt is vanilla text re-stated verbatim** - it does
nothing for English and exists only to break every other language.

Contributing structural defect: `build_text_arc.build_modstrings()` extracts the
WHOLE of SV 0.98i's `Text_EN.arc` (57-file corpus: commonequipment, monsters,
skills, ui, dialog, menu, npc, quest, x2/x3/x4 ...) into one modstrings.txt,
with no filter against the base game. SV was a TQ:IT English mod, so most of that
corpus is just vanilla English.

---

## 3. The fix (implemented on this branch)

`tools/build_text_arc.py` - during the per-file SV emission, **drop any tag whose
value is byte-identical to the player's base-game `Text_EN.arc` value.** In
English it resolves to the same string from the base text underneath (no change);
in every other language the localized base value is no longer clobbered.

Key correctness details (each was a real trap caught during dry-run):

1. **First-wins preservation (the `tagGate01` trap).** A tag can appear in
   multiple SV files with different values (e.g. `commonequipment.txt`
   tagGate01="Gate" [== base] then `xuniqueequipment.txt` tagGate01="Magnificent
   gate"). The engine keeps the FIRST. A naive drop removed the first "Gate" and
   let the later "Magnificent gate" leak through, silently CHANGING English. Fix:
   a `seen_keys` set claims a key on its first occurrence even when dropped, so a
   later different value can never leak in. Verified: 0 English changes.
2. **Manifest protection.** `validate_tags.py` requires every mod-authored tag
   (`mod_authored_tags.txt`) to be present in Text.arc. One such tag,
   `xtagMysteriousPortal` = "Mysterious Portal", is base-identical and would have
   been dropped -> build gate failure. Protected set = `collect_mod_authored_tags()`,
   never dropped.
3. **Golden freeze protection.** `validate_mastery_golden.py` freezes the exact
   Text.arc definition of 110 Occult/Hunting name/desc tags (Will's hand-tuned
   masteries). **50 of them are base-identical** (e.g. `tagMasteryTitle06`,
   `tagSkillDescription052`) and would have been dropped -> golden gate failure
   AND a revert of tuned text. Protected via `load_golden_protected_tags()`
   (reads `occult_hunting_golden.json`), never dropped.

Wiring:
- `build_text_arc(sv, out, uber, base_en_arc_path)` loads the base-game
  `Text_EN.arc` and passes its tags + the protected set into `build_modstrings`.
- `scripts/bootstrap_working_mod.ps1` sets `$env:SVC_BASE_TEXT_EN` =
  `<TQAE_ROOT>\Text\Text_EN.arc` before the text build (also accepted as the 4th
  positional arg). Reads the player's OWN game install - nothing base-game is
  redistributed in the repo.
- Kill-switch `SVC_NO_I18N_DECLOBBER=1` reverts to the old clobbering behavior.
  If the base-game Text_EN.arc is absent, the build degrades to old behavior with
  a loud warning (never fails for this reason).

Files changed: `tools/build_text_arc.py`, `scripts/bootstrap_working_mod.ps1`.

---

## 4. Proof (dry-run against real SV + base-game text; real code path)

`build_modstrings` was run for real (not re-implemented) against
`upstream/soulvizier_098i/Resources/Text_EN.arc` + the base game `Text_EN.arc`:

- modstrings: **OLD 14,663 -> NEW 4,063** tags (dropped 10,600).
- **English effective-value mismatches OLD vs NEW: 0** (raw and meaningful).
  Effective English value = `modStrings.get(tag)` else `base_EN.get(tag)`;
  identical for every tag because only byte-identical values were dropped.
- `xtagMysteriousPortal` present (manifest-protected). Occult label intact.
- **All 110 golden tags preserved** (108 defined in modstrings, 0 lost; 2
  resolve from base with empty defs in the golden snapshot too). 50 golden tags
  were base-identical and were correctly protected.
- Every dropped key was byte-identical to base `Text_EN` AND unprotected.

Per-language restoration (base-present tags no longer clobbered):

| lang | clobbered BEFORE | clobbered AFTER | restored | % |
|---|---:|---:|---:|---:|
| DE | 11,284 | 770 | 10,514 | 93.2% |
| FR | 11,283 | 770 | 10,513 | 93.2% |
| ES | 11,284 | 770 | 10,514 | 93.2% |
| IT | 11,284 | 770 | 10,514 | 93.2% |
| RU | 11,276 | 770 | 10,506 | 93.2% |
| PL | 11,340 | 770 | 10,570 | 93.2% |
| BR | 11,369 | 769 | 10,600 | 93.2% |
| JA | 11,356 | 770 | 10,586 | 93.2% |
| KO | 11,369 | 770 | 10,599 | 93.2% |
| CH | 11,360 | 769 | 10,591 | 93.2% |
| CZ | 11,272 | 765 | 10,507 | 93.2% |
| UK |  9,926 | 769 |  9,157 | 92.3% |

The residual ~770 per language that stay English = 719 SV/DRX intentional
rewordings + ~50 golden Occult/Hunting tags + a couple manifest tags. All are
kept on purpose (see decisions below).

Gates that stay green by construction (not run - needs the .arz + build machine,
owned by another workflow): `validate_tags` (manifest protected), the golden text
gate (110 golden tags preserved), the in-build duplicate-tag gate (dropping only
removes lines). Fast gates run: `py_compile tools/build_text_arc.py` OK;
PowerShell parse of `bootstrap_working_mod.ps1` OK.

---

## 5. Decisions for Will (design layer, NOT implemented)

The safe engineering fix above restores ~93% of localization with zero English
change. The remaining choices are design calls:

1. **The 719 SV/DRX rewordings (still English in other languages).** These are
   tags where SV/DRX intentionally changed the vanilla wording (e.g. DRX renames
   "Crushing Damage" -> "Wound Damage"). Keeping them (current fix) preserves the
   mod's English identity but leaves them English in every language. Dropping
   them too would fully localize vanilla content but revert those English strings
   to vanilla wording. Recommend KEEP (mod identity), revisit only if a specific
   language complaint names one.
2. **FAILBOAT debug junk (English bug, pre-existing).** 4 rewording tags ship
   literal debug text overriding clean base English, e.g. `CharacterAttackSpeed`
   = "{...}% Attack Speed ^y(FAILBOAT)" (also CharacterRunSpeed,
   CharacterSpellCastSpeed, DamageModifierPoison). This is visible in ENGLISH
   today. Dropping/fixing these 4 both removes the junk in English and restores
   localization. Low-risk bonus cleanup - recommend fixing in a follow-up (it is
   an English-visible change so flagged, not done here).
3. **Which languages to "claim support for."** The mod cannot fully localize its
   own content (no SV/DRX translations exist). After this fix the honest posture
   is: "vanilla content is in your language; Soulvizier's added content (souls,
   SV areas, custom skills) is English-only." Recommend saying exactly that in
   the Workshop description rather than claiming per-language support.
4. **Full localization** (ship translated `Text_XX.arc` for mod content) is out
   of reach without translators for 3,586 mod strings and is not proposed.

---

## 6. Deploy + in-game verification (for the integration wave / Will)

This is a text-only change; deploy couples arz+Text (rebuild both together per
the standing rule). After the b38 integration wave rebuilds with this branch:

1. `scripts/bootstrap_working_mod.ps1` (will print
   `i18n de-clobber ENABLED: <N> base-game Text_EN tags loaded` and
   `dropped ~10,6xx vanilla tags byte-identical to base-game Text_EN`).
2. Deploy to CustomMaps, restart Steam + TQ (mandatory per standing rule),
   hash-verify the deploy landed.
3. In-game: set language = German (or any non-English) in Options. Load the
   Custom Quest. EXPECT: menus, item stats, base skill names, monster names,
   dialog now in German; only Soulvizier souls / SV-area / custom DRX-skill text
   in English. BEFORE this fix almost everything was English regardless of the
   setting.
4. Sanity in English: unchanged from today (souls, Occult "Occult Mastery"
   label, Hunting names all still correct).

## 7. Notes / adjacent findings

- `scripts/deploy_text_arc.ps1` is a DEAD pre-modStrings script that copies SV's
  raw `Text_EN.arc` into CustomMaps as `Text_EN.arc`. Not in the live deploy
  path (`deploy_to_custommaps.ps1`), but if ever run it would ship a stray
  `Text_EN.arc`. Recommend deleting it (out of scope here).
- The engine mod-override path is a FIXED `Text\modStrings.txt` (no language
  variant), so per-language MOD text cannot be shipped via that mechanism - which
  is why the fix is "stop clobbering the base per-language text," not "ship
  translated modStrings."
