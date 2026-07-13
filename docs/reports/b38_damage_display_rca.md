# b38 - "Damage display is not working" RCA + fix

**Lane:** b38-damage (branch `feat/b38-damage`, base `d6ed889`)
**Steam report (user 962807512):** "The damage display is not working."
**Verdict:** ROOT CAUSE FOUND, DB-side, FIXED. Registry module
`tools/patches/damage_display.py`. Not engine-side. Not a font/Text.arc problem.

---

## TL;DR

The floating combat-damage numbers over enemies do not render because our
database's `records\xpack\game\gameengine.dbr` is **missing the seven
Anniversary-Edition FontStyle pointer fields** that bind a font to each
damage-number category:

```
DamageNormalStyle  DamageElementalStyle  DamageOnPlayerStyle  DamageOverTimeStyle
HealingStyle       HealingOnPlayerStyle  PlayerImpairmentStyle
```

SoulVizier 0.98i ships a **pre-Anniversary** `gameengine.dbr` that predates
those fields; our build loads SV 0.98i as its base db and no tool patches
gameengine, so we inherit the incomplete record verbatim. With no FontStyle
bound, the engine has nothing to render those floating numbers with, so they do
not appear.

The fix binds the seven missing fields to the base-game FontStyle records (which
resolve from the base `database.arz`). It touches exactly **one record**, adds
**seven string fields**, creates **zero records** and **zero Text tags**, and
changes **no SoulVizier design field**. Proven by dry-run replay.

**Diagnostic signature (matches the mechanism):** critical-hit numbers still
appear (SV's record kept `CriticalHitOnMonsterStyle`/`CriticalHitOnPlayerStyle`)
but normal / elemental / damage-over-time numbers do not. If the user reports
"I see yellow crit numbers but no white/colored regular numbers," that is a
one-to-one confirmation.

---

## 1. How TQAE renders floating damage numbers

The Anniversary-Edition engine reads the combat-text font styling from the
**game-engine record**. Each damage category has a dedicated `...Style` field
pointing at a `Records\UI\FontStyles\*.dbr` FontStyle record, which supplies the
font, size, color, and drop-shadow used to draw that number:

| gameengine field | FontStyle record | color (base) | what it draws |
|---|---|---|---|
| `DamageNormalStyle` | `DamageNormal.dbr` | white | normal hit numbers on monsters |
| `DamageElementalStyle` | `DamageElemental.dbr` | pink | elemental hit numbers |
| `DamageOverTimeStyle` | `DamageOverTime.dbr` | orange | DoT ticks (burn/poison/bleed) |
| `DamageOnPlayerStyle` | `DamageOnPlayer.dbr` | desat red | damage the player takes |
| `HealingStyle` / `HealingOnPlayerStyle` | `Healing.dbr` / `HealingOnPlayer.dbr` | - | heal numbers |
| `PlayerImpairmentStyle` | `PlayerImpairment.dbr` | - | stun/freeze/etc. floaters |
| `CriticalHitOnMonsterStyle` | `CriticalHitOnMonster.dbr` | - | crit numbers (SV KEPT this one) |

If a `...Style` field is absent, the engine has no FontStyle for that category
and renders no floating number for it.

### Which gameengine record is authoritative (proof)

TQAE keeps **two** game-engine records: `records\game\gameengine.dbr` (non-xpack)
and `records\xpack\game\gameengine.dbr` (xpack). The `Damage*Style` fields exist
**only in the xpack record** in the base game:

- base `records\game\gameengine.dbr` (222 fields): **no** `Damage*Style` fields.
- base `records\xpack\game\gameengine.dbr` (239 fields): **has all** of them.

Vanilla TQAE unquestionably shows damage numbers. Therefore the engine reads the
**xpack** record for combat-text styles (if it read the non-xpack one, vanilla
would have no styles and no numbers). TQAE is Immortal-Throne-based, so the xpack
record is always in force. `records\xpack\game\gameengine.dbr` is the record to
fix.

(The bug report itself is the second proof that our mod's record is authoritative
in-game: a total-conversion Custom-Quest arz overrides base records, so our
incomplete gameengine is what loads. If the base record were used, numbers would
work.)

---

## 2. Evidence: the divergence

Diff of `records\xpack\game\gameengine.dbr`, base game `database.arz` vs our live
build36a arz (`baseline_build36.arz`, md5 `63ca7cf8...`):

```
DIFF DamageElementalStyle:   BASE = Records\UI\FontStyles\DamageElemental.dbr   BASELINE = <MISSING>
DIFF DamageNormalStyle:      BASE = Records\UI\FontStyles\DamageNormal.dbr      BASELINE = <MISSING>
DIFF DamageOnPlayerStyle:    BASE = Records\UI\FontStyles\DamageOnPlayer.dbr    BASELINE = <MISSING>
DIFF DamageOverTimeStyle:    BASE = Records\UI\FontStyles\DamageOverTime.dbr    BASELINE = <MISSING>
DIFF HealingStyle:           BASE = Records\UI\FontStyles\Healing.dbr           BASELINE = <MISSING>
DIFF HealingOnPlayerStyle:   BASE = Records\UI\FontStyles\HealingOnPlayer.dbr   BASELINE = <MISSING>
DIFF PlayerImpairmentStyle:  BASE = Records\UI\FontStyles\PlayerImpairment.dbr  BASELINE = <MISSING>
# survived in SV's record (case-only diff, harmless), which is why crits still show:
     CriticalHitOnMonsterStyle  = records\ui\fontstyles\criticalhitonmonster.dbr
     CriticalHitOnPlayerStyle   = records\ui\fontstyles\criticalhitonplayer.dbr
```

The FontStyle records themselves are **fine**. All seven live in the base
`database.arz` (each pointing at `Fonts\Albertus MT Light.fnt`, a base font the
shipped mod already uses for item/skill text). Our arz does **not** ship these
seven FontStyle records, so the references resolve from the base game. The only
break is the missing pointers in gameengine.

Probe scripts (scratchpad, READ-ONLY):
`probe_damage_records.py`, `probe_damage_diff.py`, `probe_key_dtype.py`,
`probe_fontstyles_exist.py`.

## 3. Provenance: this comes from SV upstream, not our build

- SV 0.98i extract `local/extract_sv/records/xpack/game/gameengine.dbr`: has only
  `CriticalHitOnMonsterStyle` / `CriticalHitOnPlayerStyle`; **lacks** all seven
  Damage/Healing/Impairment style fields.
- base AE extract `local/extract_ae/records/xpack/game/gameengine.dbr`: has all.
- `build_svc_database.py` loads SV 0.98i as its base db (`db = ArzDatabase.from_arz(sv098_path)`),
  and **no build tool patches gameengine** (grep: only diagnostic dump/check
  tools reference it). So the incomplete SV record passes straight through.
- The sibling copies in our arz (`drxgameengine.dbr`, `copy of gameengine.dbr`,
  `xxxgameengine.dbr`) also lack the fields: the whole SV/DRX gameengine lineage
  is pre-AE. This is a systemic upstream gap, not a build error.

Conclusion: an **old-mod-on-Anniversary** class defect. SV predates the AE
combat-text fields; nobody re-added them when SV was brought onto TQAE.

## 4. The fix

`tools/patches/damage_display.py` (registry module, added to `REGISTRY` just
before `visuals`):

- On `records\xpack\game\gameengine.dbr`, bind each of the seven missing
  `...Style` fields to its base-game FontStyle record (lowercase paths, matching
  the record's existing style-field convention; `set_field` infers `DATA_TYPE_STRING`,
  the same type every existing style pointer uses; no explicit dtype -> obeys the
  cloned-record INT/FLOAT-corruption law).
- Idempotent: only binds a field that is currently empty; never clobbers an
  existing binding (so it is a no-op the day upstream ships a complete record).
- `verify(db, tags)` post-finalization hook fails the build loud if any of the
  seven is still unbound after finalization.

**Why this is allowed under the design laws:** gameengine.dbr is a base-game
record, and these are pure UI display-styling fields. Re-adding them is a
UI-defect fix on a base record (the ho-ui F5 precedent), not a design change. It
touches **none** of SoulVizier's deliberate gameengine edits (camera distances,
loot prefix/suffix modifiers, combat-equation record, drop rates, XP equation,
etc. are all left exactly as SV set them). No golden exists for gameengine, so no
golden waiver applies.

### Minimality proof (dry-run replay)

`tools/patches/_probe_damage_display.py` replays the module against a copy of the
live baseline arz and asserts:

```
PASS 1: apply() modified ONLY records\xpack\game\gameengine.dbr
PASS 2a: record set unchanged (50883 records)          # 0 records added/removed
PASS 2b: exactly 7 fields added, all pre-existing fields byte-identical
PASS 2c: all added fields STRING dtype, correct FontStyle targets, 0 Text tags
PASS 3: verify() OK
PASS 4: apply() idempotent (second run modified nothing)
```

## 5. Secondary meaning checked in passing: character-sheet damage stats

Not the cause. The character-window damage-stat FontStyle pointers
(`ItemBaseStats`, `ItemBonuses`, `SkillStatsCurrent`, `SkillName`, ...) are all
**present** in our gameengine (they differ from base only by lowercase path).
The "Damage: X-Y" line on the character sheet is driven by player attributes and
the character-window template, neither of which is affected by the missing
combat-text styles. Nothing to fix here.

## 6. What to tell the user / how to confirm in-game

Cause is a missing engine-display setting inherited from the classic SoulVizier
data (fixed in the next build); it is a data fix, not an engine limitation.

In-game confirmation after the fixed arz is deployed (note: TQ bakes nothing here
- this is live-read each hit, so no fresh character needed, just a fresh game
launch so the new arz loads): hit any enemy and floating white/colored damage
numbers should appear over it, colored orange for damage-over-time (burn/poison),
pink for elemental. Before the fix, only crit numbers appear.

Pre-fix diagnostic to ask the user (optional, strengthens confirmation): "Do you
see the yellow critical-hit numbers but no regular white/colored numbers?" A yes
is a one-to-one match to this root cause.

## 7. Gates run (all green)

- `py -m py_compile` on `damage_display.py`, `_probe_damage_display.py`, `__init__.py` -> OK
- `tools/patches/_check_registry.py` -> `selfcheck OK: 10 module(s)`
- dry-run replay `_probe_damage_display.py` -> ALL CHECKS PASS (section 4)
- all 7 target FontStyle records confirmed present in base game arz (no dangling ref)

No heavy build was run (concurrency rules: main + build machine owned by another
workflow). The full DB build will exercise the module in-line; its behavior there
is identical to the replay (the module runs after the monolith, and the monolith
leaves gameengine without these fields, exactly the state the replay starts from).
