# Rant Scroll Corpus & Alignment Vet

> **Ask (Will, 2026-07-14):** "have a vet compare the Devourer of Blood rant scroll to the other
> ones in the game that are vanilla and especially any that amgoz1 made and see if we need to change
> our one to make it more in alignment with the others but with respect that this is probably the
> strongest and most arrogant monster in the game besides og Toxeus SP."
>
> **Scope:** read-only corpus + judging pass. Branch `feat/rant-scroll-align` (worktree
> `.claude/worktrees/rant-align`, branched from `feat/toxeus-encounter-suite`). Merges after the
> parchment (map) lane in integration.
>
> **Calibration:** Blood Toxeus (`um_bloodtoxeus_99`, "Toxeus the Murderer, Devourer of Blood") sits
> at the top of the arrogance/menace hierarchy, second ONLY to the original Secret-Passage Toxeus
> (`um_toxeus_99`). Alignment = match the GAME's readable conventions (what a scroll looks/reads
> like), NOT flatten his voice.

---

## 0. TL;DR verdict

**Our screed is already the strongest-aligned readable in the mod on voice, tone, lore, and length.
There is exactly ONE convention it violates, and it is a pure formatting issue: it is a single
227-word unbroken block.** Every comparable readable in the game (vanilla parchments AND amgoz1's own
in-cave `finalletter`) breaks its body into paragraphs. Our own donor, `finalletter`, uses `^n^n`.

- **Warranted change (format only, ZERO words altered):** insert `^n^n` paragraph breaks at the
  screed's 3 natural beats, mirroring the `finalletter` donor. Also correct a factually-wrong code
  comment that claims `finalletter` has "no newline tokens" (it has `^n^n`).
- **Do NOT change:** the `^r` blood-red lead (matches the in-cave sibling `finalletter`); the direct
  second-person taunt (his arrogance, and it has a vanilla precedent); the absence of a signature
  (matches every vanilla *villain* readable); the length (227w ~= `finalletter` 221w, both near the
  top of the vanilla range but not beyond it); the voice/lore (canon-perfect).
- The proposed revised text is in **Section 7**. The word-level content remains **Will-gated** per the
  amgoz1 creative-bar rule; this branch stages only the break insertion + comment fix so nothing
  ships without his read.

---

## 1. Method & sources (all ground-truth, read-only)

| Corpus | Records source | Text source |
|---|---|---|
| Vanilla (base + IT + Ragnarok + Atlantis + Eternal Embers) | `TQAE/Database/database.arz` (74,013 records) | `TQAE/Text/Text_EN.arc` (17,540 tags) |
| amgoz1 / SV 0.98i | `upstream/soulvizier_098i/Database/database.arz` (diffed vs base) | `upstream/soulvizier_098i/Resources/Text_EN.arc` (14,652 tags, overlaid on base) |
| Our screed | `tools/patches/toxeus_suite.py` Part B `_RANT_TEXT` | authored inline -> `tags['tagSVCToxeusRantTEXT']` |
| Lore continuity | `docs/BLOOD_TOXEUS_DESIGN.md` §1.2, `docs/reports/toxeus_suite_recon.md` §4 | - |

Method: extract every `.arz` record carrying a non-empty `itemText` field, resolve that tag to its
display string via the Text arc, then measure structure (word count, `^n` line-break tokens, caret
color codes, person/tense, salutation, signature). SV isolated by diffing SV records/text against
base (SV-new records + text-changed records). All in TQAE, all resolves confirmed. Probe scripts in
scratchpad (`corpus_probe*.py`); JSON dumps `base_prose.json`, `sv_prose_new.json`.

**TQAE text encoding note:** the readable body is one Text tag (one line). In-body line breaks are the
caret token `^n` (braced `{^n}`/`{^N}` in vanilla, unbraced `^n` in `finalletter`). Both render; the
scroll window also word-wraps, so a missing break does not overflow, it just reads as a wall.

---

## 2. Our screed (verbatim + metrics)

**Record:** `records\item\svc\svc_toxeus_rant.dbr` (clone of the `finalletter` Parchment chassis,
`itemClassification=Magical`). **Name:** `{^r}The Murderer's Screed`. **On-ground:** `A Parchment
Slick with Blood`. **Body tag:** `tagSVCToxeusRantTEXT`.

> ^rYou found the wet page. Good. Read it aloud, so the walls remember your voice too. They called me
> a murderer as if the word were an insult, as if it were not a crown. I opened Athens throat by
> throat, and the city thanked me with its silence. Then your heroes came and cut me down in the dark
> and called that the end of the sentence. It was not even the comma. The cult drowned me in the
> cauldron beneath the falls and boiled the poison out of my marrow, and they poured the blood of the
> drowned back into my dry veins until I was full, fuller than any living thing has the right to be. I
> do not kill for coin now, nor for quiet. I kill because every heartbeat in this cave is a debt, and
> I have come to collect all of them at once. You feel it already: the itch beneath the skin, the
> small wounds that will not close. That is only me, reading you the way you are reading me. When you
> bleed, I am taking back what was always mine. Come to the deep door. Bring your friends. I will open
> every one of you at once, and drink the room dry, and leave this page for the next fool who mistakes
> an ending for a stop.

**Metrics:** words = **227**; chars = 1108; `^n` line-breaks = **0**; caret codes = `{^r: 1}` (lead
only); first-person = yes; second-person = yes; salutation = none (direct address); signature = none.

**Lore continuity (canon-perfect vs `BLOOD_TOXEUS_DESIGN.md` §1.2):** "cut me down in the dark" =
Athens catacombs; "drowned me in the cauldron beneath the falls and boiled the poison out of my
marrow / poured the blood of the drowned back into my dry veins" = the cult's cauldron-resurrection
verbatim; "Come to the deep door" = "left him at the deepest door"; "the next fool who mistakes an
ending for a stop" = "the last sentence anyone who reaches the sanctuary's heart will ever hear read
aloud." First-person "I" throughout honors the **LORE LAW** (Will 2026-07-11): the original murderer
is the eternal progenitor whom the blood form *continues* (same "I"), not a separate risen entity.

---

## 3. The blood-cave letter chain (the amgoz1 anchor)

The only pre-existing readable in the blood-cave chain is **`finalletter`** (the dying adventurer's
blood-written note that starts the widow/Ling reward quest). It is the ONLY narrative prose readable
that SV 0.98i adds over vanilla (Section 5), it is our screed's **exact donor chassis**, and it lives
in the **same cave**, so it is the single most load-bearing style anchor.

**`records\drxmap\quest\finalletter.dbr`** [ItemEquipment / Parchment] on-ground `Tattered Parchment`
(`tagFinalLetterONGROUND`), body `tagFinalLetterTEXT`. **221 words**, caret `{^r: 1, ^n: 2}`:

> **^r**I write this in my own blood here, in what will surely be my final hours, as I am too wounded
> to escape this place. Adventurer, be warned: there is nothing but suffering and death in the caverns
> beyond. Demons and witches and blood...so much blood. Let not your hubris undo you as mine has
> undone me. [...] please, leave this place now and find my wife, Ling, in the village of Zhidan. Tear
> off the bottom half of this note and deliver it to her. If you honor this request, you will be
> justly rewarded, for my wife is a powerful healer. **^n^n**My dear Ling, I cannot return to you, and
> have not time to explain. [...] Oh, my time is too short, I love you I love you I love

**What `finalletter` establishes for this exact cave (the conventions our scroll should echo):**
1. **Leads with `^r`** (blood-red) - thematically the "written in blood" convention of this cave. Our
   screed matches this. (Vanilla never leads with a color code - Section 4 - so the `^r` lead is an
   amgoz1/DRX cave convention, and matching the sibling is correct, not a defect.)
2. **Breaks its body with `^n^n`** at the one logical seam (the two halves of the letter). It does NOT
   run as one block. **This is the convention our screed currently misses.**
3. First-person, addressed to the reader ("Adventurer"), no signature. Our screed matches.
4. **~221 words** - nearly identical to our 227. Length alignment is excellent.

There is no second readable in the chain (the widow reward is dialog, not a scroll). Our screed
becomes the **second** readable in the cave - the villain's reply to the victim's letter. Keeping the
same `^r` lead and (with the fix) the same `^n^n` break style makes the two read as a matched pair:
the victim's warning and the predator's boast, on the same blood-soaked stationery.

---

## 4. Vanilla readable corpus & conventions

**Counts (base TQAE `database.arz`):** 857 records carry `itemText`. Of these:
- **~39 narrative parchment/note readables** - the lore corpus (Immortal Throne `xpack` = 17, Eternal
  Embers `xpack4` = 18, Ragnarok `xpack2` = 1, plus 3 Set's-Betrayal relic lore). 36 exceed 40 words.
- **93 `OneShot_Scroll`/`OneShot_Scroll_Eternal`** - mechanical labels (skill scrolls, potion/dye
  text). Median **11 words**, no prose, no codes. NOT the comparison class - a "rant scroll" is a
  narrative parchment, not a mechanical scroll.
- The remainder are item flavor (relics, charms, artifacts).

**Narrative parchment conventions (n = 39 prose readables; word count min 41 / median 129 / max 296):**

| Convention | Vanilla norm | Evidence |
|---|---|---|
| **Format** | Epistolary (salutation + named recipient) OR titled treatise/journal/poem | "Dear Mom,", "Commander Azibo,", "O Dark Lord, hear my plea!", "0600 / Epirus Catacombs / West Flank" |
| **Leading color code** | **None** (0/39 start with a caret color) | every vanilla note opens on plain text |
| **Line breaks** | Braced `{^n}` / `{^N}`, used heavily (24/39 have breaks; up to 9 in one note) | salutation break + paragraph breaks; single-`{^n}` for list rows |
| **Person** | First-person letters to a second person | 26/39 first-person, 26/39 second-person |
| **Signature** | Personal letters signed; **villain/journal declarations are UNSIGNED** | signed: Duaenre, Scout Zuka, Misenus, Zhao; **unsigned:** parchment14, parchment02, parchment04 |
| **Length** | 41-296 words, median ~129 | our 227 is high-normal, matches parchment01 (219) + finalletter (221) |
| **Emphasis color** | rare `{^y}` (yellow) inline | a handful of notes only |

**The mightiest-speaker anchor - `xpack\...\parchment14.dbr` (a demon war-general reporting to his
Dark Lord):**

> Such sweet music, the wailing of men.{^N}{^N}The siege continues, My Lord. My blade cuts through
> their soldiers like a scythe through wheat. I feast upon their sorrow, their despair. [...] Not even
> the comfort of death awaits those foolish enough to oppose us.{^N}{^N}Soon, our dominance shall be
> complete. You shall hold the world of the living in the palm of your hand [...] pray for the day
> when the death can stop and the torture begin.

This is vanilla's most menacing/arrogant readable, and the closest register to our screed. Note the
key calibration point: **even vanilla's most menacing voice is a servant boasting UPWARD to a lord**
("My Lord", "Your Eminence"). It opens with a striking declarative line ("Such sweet music, the
wailing of men."), revels in slaughter in the first person, escalates to grandiosity, and is
**unsigned**. It also **breaks into paragraphs** with `{^N}{^N}`.

**Our screed is a genuine apex-predator taunt aimed straight at the reader** - a register *above*
anything vanilla, because no vanilla readable is authored by a being who considers himself the top of
the food chain. That is correct for Blood Toxeus (calibration: #2 after OG Toxeus). "Alignment" must
therefore be about *format* (breaks, codes, length), not about deferring his voice to vanilla's
servant-boast humility. Do not flatten it.

---

## 5. amgoz1 / SV 0.98i additions (isolated by diff vs base)

SV 0.98i's database has 1,056 `itemText` records (vs 857 base); 726 are SV-new. **After removing item
flavor and boilerplate, amgoz1 added exactly ONE narrative prose readable: `finalletter` (Section 3).**

- The 24 `records\drxitem\scrolls\*` "scrolls" are the **anti-cheat boilerplate** ("This item is
  unusable outside the custom game...") reused verbatim across soul-scroll items - not lore.
- The other SV-new prose (poison-orb relics, potion labels) is item flavor.
- SV **rewrote zero vanilla lore notes**; its 42 text-changed prose records are relic descriptions
  where SV inlined the "Can enchant..." clause - mechanical, not narrative.

**Conclusion:** the entire amgoz1 narrative-readable style bible for this mod = `finalletter`. Our
screed already clones its chassis, its `^r` lead, its person, its no-signature, and its length. The
one thing it does not yet copy is its **`^n^n` paragraph break**.

---

## 6. Side-by-side

| Dimension | Vanilla norm (39 parchments) | amgoz1 `finalletter` (in-cave sibling) | Our screed | Aligned? |
|---|---|---|---|---|
| Words | 41-296 (median 129) | 221 | **227** | YES (high-normal, ~= sibling) |
| Leading color code | none | `^r` | `^r` | YES to sibling (intentional cave convention) |
| Paragraph breaks | `{^n}`/`{^N}`, 24/39 | `^n^n` (1 seam) | **none (0)** | **NO - the one gap** |
| Person | 1st to 2nd | 1st to 2nd | 1st to 2nd | YES |
| Salutation | usually (letters) | "Adventurer," implied | direct ("You found...") | YES (villain/direct precedent: parchment09) |
| Signature | personal signed / villain unsigned | unsigned | unsigned | YES (matches villain subtype) |
| Tone | comedic..somber..menacing | somber warning | apex menace | YES (register above vanilla, correct for rank) |
| Lore grounding | canon | canon | canon (§1.2 verbatim) | YES |
| No em/en dashes (house rule) | vanilla uses " - " | clean | clean | YES (ours correctly avoids) |

**Nine of ten dimensions already align.** The lone miss is paragraph breaks.

---

## 7. The one warranted change (format only) + proposed text

Break the wall into the screed's 4 natural beats using `^n^n` (the `finalletter` donor's token, for
in-cave continuity), changing **zero words**:

1. **The boast** - "...the city thanked me with its silence." `^n^n`
2. **The resurrection** - "...fuller than any living thing has the right to be." `^n^n`
3. **The purpose / the bleed** - "...reading you the way you are reading me." `^n^n`
4. **The invitation** - "When you bleed... mistakes an ending for a stop."

**Proposed `_RANT_TEXT` (breaks shown as line gaps; each is a literal `^n^n`):**

> ^rYou found the wet page. Good. Read it aloud, so the walls remember your voice too. They called me
> a murderer as if the word were an insult, as if it were not a crown. I opened Athens throat by
> throat, and the city thanked me with its silence.
>
> Then your heroes came and cut me down in the dark and called that the end of the sentence. It was
> not even the comma. The cult drowned me in the cauldron beneath the falls and boiled the poison out
> of my marrow, and they poured the blood of the drowned back into my dry veins until I was full,
> fuller than any living thing has the right to be.
>
> I do not kill for coin now, nor for quiet. I kill because every heartbeat in this cave is a debt,
> and I have come to collect all of them at once. You feel it already: the itch beneath the skin, the
> small wounds that will not close. That is only me, reading you the way you are reading me.
>
> When you bleed, I am taking back what was always mine. Come to the deep door. Bring your friends. I
> will open every one of you at once, and drink the room dry, and leave this page for the next fool
> who mistakes an ending for a stop.

This matches the vanilla multi-paragraph norm AND the sibling `finalletter`'s `^n^n`, reads as a real
TQ parchment instead of one runaway block, and preserves every syllable of his voice.

**Staged on this branch** (`feat/rant-scroll-align`): the `^n^n` insertion + a correction to the Part
B comment that wrongly claimed `finalletter` has "no newline tokens." **Word-level content stays
Will-gated** (amgoz1 creative-bar): if he wants a hair more menace or a different beat split, the
break points are trivially movable. Nothing deploys without his read.

---

## 8. Options Will may want to consider (NOT applied - his call)

These respect "don't flatten his voice" and are offered only as levers, not recommendations:

- **`^r` on each paragraph.** `finalletter` sets `^r` once and lets it ride across `^n^n`; our staged
  change does the same (proven-rendering parity with the sibling). If a paragraph ever renders in the
  default color after a break in-game, re-prefix each beat with `^r`. Launch-gated visual check.
- **A one-line title/attribution flourish.** Vanilla poems/pamphlets sometimes open with a byline
  ("by Minkah, Lord of Poesy"). A single opener like "^rTo whoever still breathes:" would push it
  further toward the epistolary norm - but it risks softening the cold open ("You found the wet
  page."), which is arguably his best arrogance. Recommend leaving the cold open.
- **Nothing else.** Voice, tone, lore, length, name, and on-ground label are all correct and distinct
  from the sibling ("A Parchment Slick with Blood" vs `finalletter`'s "Tattered Parchment").

---

## 9. Alignment Judge verdict (independent pass, 2026-07-14)

**VERDICT: ALIGNED.** Keep the screed as it now stands (with the format-only `^n^n` break fix from
Section 7). No word-level change is warranted. The screed matches the game's readable conventions on
every axis and sits correctly at the apex of the corpus's voice range as the second-most-arrogant
monster's readable, with no authored text above it to defer to.

This pass re-derived the corpus from ground truth independently (base `database.arz` = 74,013 records +
`Text_EN.arc` = 17,540 tags; SV 0.98i arz/arc = 51,186 records + 14,652 tags), re-verified the
Section 3-7 claims, and added the one check the calibration hinges on: the OG Toxeus SP relationship.

### 9.1 The OG Toxeus SP relationship (the load-bearing calibration check)

Will's calibration ranks Blood Toxeus #2 in arrogance, "second only to OG Toxeus SP" (`um_toxeus_99`).
The judge check: does OG Toxeus SP carry any authored text our screed must read subordinate to?

**Ground-truth answer: OG Toxeus SP has ZERO authored prose.** `um_toxeus_99` is a plain `Monster`
record whose only authored string is `description = tagMonsterName190 = "Toxeus the Murderer"`. A full
scan of the merged base+SV text corpus finds exactly TWO values containing "Toxeus": his name
(`tagMonsterName190`) and his soul name (`tagSoulName505 = {^F}Toxeus the Murderer Soul`). No readable,
lore paragraph, quest line, or death quote anywhere in the game mentions Toxeus or the word "murderer."
The Athens variant (`um_toxeus_21`) and the dev record (`z_toxeus`) carry the same single name tag and
nothing more.

Two consequences, both of which STRENGTHEN the ALIGNED verdict:

1. **There is no text competitor.** Our screed is the only authored Toxeus-voice prose in the entire
   game (base + SV + mod). There is nothing in the readable corpus for it to be "subordinate in menace"
   to; the only being ranked above it (OG Toxeus SP) speaks with a name and a body count, not with
   words. So the screed being the single most arrogant readable in the game is not an over-reach, it is
   the correct and only possibility.
2. **It channels the progenitor rather than superseding him.** Per the LORE LAW (Will 2026-07-11) the
   original murderer is the eternal progenitor whom the blood form continues as the same "I." The screed
   speaks in exactly that first-person continuous voice ("They called me a murderer... I opened Athens
   throat by throat... your heroes came and cut me down... The cult drowned me in the cauldron... poured
   the blood of the drowned back into my dry veins"). It never claims to be a new, greater being than the
   Secret-Passage Toxeus; it claims to BE him, refilled. It out-arrogances everyone except OG Toxeus SP
   by definition, because it IS OG Toxeus SP's own voice carried one rung past death. Calibration
   satisfied exactly.

### 9.2 Per-axis final ruling

| Axis | Corpus norm | Our screed (live) | Ruling |
|---|---|---|---|
| Length | 41-296 words, median 129; sibling finalletter 221 | 227 | ALIGNED (high-normal, ~= sibling) |
| Blood-red `^r` lead | vanilla 0/39; in-cave sibling finalletter leads `^r` | leads `^r` | ALIGNED to the cave's "written in blood" convention |
| Paragraph breaks | 24/39 vanilla break; finalletter `^n^n` | 3x `^n^n` (was 0) | ALIGNED (fixed in Section 7; confirmed live) |
| Person | 1st to 2nd | 1st + 2nd | ALIGNED |
| Salutation / open | letters salute; parchment09 cold-opens the reader | direct cold-open taunt | ALIGNED (precedented villain deviation, correct for apex rank) |
| Signature | villain/journal declarations unsigned (parchment14/02/04) | unsigned | ALIGNED |
| Register / menace | comedic..somber..menacing; peak = parchment14 (servant boasting UP to a Dark Lord) | apex predator taunting the reader directly | ALIGNED, correctly ABOVE vanilla's ceiling (no vanilla speaker is top-of-food-chain) |
| Anachronism | none | none (elevated, timeless; no slang or meme) | ALIGNED (reads as a TQ readable, not a modern outlier) |
| Lore canon | n/a | Section 1.2 verbatim (cauldron, boiled marrow, blood of the drowned, deepest door, last sentence) | ALIGNED |
| Em/en dashes (house rule) | vanilla uses " - " | none | ALIGNED |
| OG Toxeus SP subordination | OG has no authored text; same "I" | channels the progenitor, does not supersede | ALIGNED |

Eleven of eleven axes align. The lone prior gap (no paragraph breaks) was correctly closed by the
Section 7 format fix.

### 9.3 Independent corroboration of the corpus claims

- **finalletter is the sole amgoz1 narrative readable.** SV 0.98i adds 5 new prose records of 40+ words;
  4 are poison-orb `ItemRelic` flavor blurbs (41 words each), leaving exactly one on-ground
  `ItemEquipment` readable: `finalletter` (221 words, leads `^r`, one `^n^n` break, unsigned, 1st+2nd
  person). Confirmed as both the style anchor and the in-cave sibling.
- **The Section 7 change is format-only.** The committed diff (22b2039) inserts `^n^n` at three beats and
  alters zero words; the live `_RANT_TEXT` measures 227 words, 3x `^n^n`, one `^r` lead. `py_compile` PASS.
- **Vanilla menace anchors verified verbatim:** parchment14 ("Such sweet music, the wailing of men.",
  demon general to "My Lord", 146w, unsigned, paragraph-broken, boasts upward); parchment09 ("welcome to
  the first day of the rest of your unlife!", direct 2nd-person cold-open, 151w); parchment01 ("Dear
  Mom,", 219w). None lead with a color code; all break into paragraphs.

### 9.4 Word-level: keep as-is (Will-gated)

No misalignment requires a word change, so none is proposed; the word-level content stays gated to Will
per the amgoz1 creative bar. The recommendation is to **keep the current text.** The only outstanding
lever is the one already flagged in Section 8: if a paragraph ever renders in the default color after an
`^n^n` break in-game, re-prefix each beat with `^r` (a launch-gated visual check; finalletter proves
`^r` rides across `^n^n`, so this is precautionary only).

**Optional arrogance dials (NOT applied; offered only because Will's ask foregrounds "the strongest and
most arrogant monster").** The screed already reads at its ceiling. These are the two more-arrogant
variants the judge tested against the current text, each changing content and therefore Will-gated:

- **A (hungrier invitation).** "Bring your friends." becomes "Bring your friends. Bring all of them.
  There is room in me." Leans the apex-appetite harder (canon-consistent with "drink the room dry" and
  "fuller than any living thing has the right to be"). Judge note: the terse original lands harder;
  recommend KEEP.
- **B (sharper sign-off, rejected).** "...the next fool who mistakes an ending for a stop." tested against
  "...the next fool who mistakes an ending for a door" (a door he controls, tying to "come to the deep
  door"). Judge note: REJECT the variant. The original "stop" completes the grammar-of-death conceit the
  screed sets up earlier ("the end of the sentence... It was not even the comma"); changing the last word
  breaks that payoff. This is load-bearing craft, not filler; KEEP "stop."

Both are dials, not fixes. The judge's position is that the current text needs neither; if Will wants
more teeth, A is the safer of the two. Bottom line for Will's question ("do we need to change our one to
make it more in alignment / more arrogant?"): **no.** It is already the game's most arrogant readable, it
is aligned to the game's readable conventions after the paragraph-break fix, and the only voice above it
is his own earlier self, who never wrote anything down.

---

## Appendix A - integration note

`tools/patches/toxeus_suite.py` is also touched by the parchment (map/DB) lane's queued
championChance retune (backlog #172), but in a different region of the file (the spawn-pool area, not
Part B `_RANT_TEXT` ~lines 204-218 or its comment ~lines 199-203). A 3-way merge should be clean;
this branch merges after the parchment lane per the integration plan.

## Appendix B - raw corpus dumps

Full resolved text for every readable is in the scratchpad JSON (`base_prose.json` = 39 vanilla prose
readables sorted by length; `sv_prose_new.json` = SV-new prose; `base_readables.json` = all 857).
Regenerate with `scratchpad/corpus_probe3.py` (read-only; base + SV arz/arc).
