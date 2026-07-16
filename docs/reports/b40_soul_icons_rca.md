# b40 - Soul granted-summon-skill icon RCA + fix (nymph on every soul)

Lane: `feat/b40-soul-icons`. Author: b40 soul-icons implementer, 2026-07-13.
Ground truth: `baseline_build38.arz` (== build38a arz `6631f252`, LIVE on Steam) +
shipped `SoulvizierClassicDEV/Resources` arcs.

## Will's report (2026-07-13)
> Every SOUL's granted summon skill shows the SAME icon - e.g. "Summon Toxeus the
> Murderer" displays a nymph-guy icon; ALL souls have this identical wrong icon on
> their granted summon ability.

This is the granted-SKILL icon (the ability button on the equipped soul), distinct
from the soul JEWELRY icon (the ring bitmap in inventory).

## Root cause (confirmed in code + the live arz)
The summon-the-boss souls are built by the shared helper
`tools/apply_svc_patches.py :: _build_boss_summon()`. To get a crash-safe
`Skill_SpawnPet` baseline it **clones `records\skills\soulskills\summon_lyia.dbr`**
(Lyia Leafsong, a nature nymph) and then overrides the gameplay fields
(display tag, mana, cooldown, `spawnObjects`, petLimit, ...). It **never overrode
`skillUpBitmapName` / `skillDownBitmapName`**, so every cloned boss summon inherited
Lyia's icon:

```
summon_lyia.dbr  skillUpBitmapName = DRXtextures\skill icons\soul\summonlyiaup.tex   (the "nymph-guy")
                 skillDownBitmapName = DRXtextures\skill icons\soul\summonlyiadown.tex
```

`_build_boss_summon` (pre-fix, ~line 9771):
```python
db.clone_record(ss, summon_skill)          # ss = summon_lyia  -> nymph icon comes along
sf(summon_skill, 'isPetDisplayable', 1)
sf(summon_skill, 'skillDisplayName', display_tag)
sf(summon_skill, 'skillManaCost', [...])
...                                         # NO skillUp/DownBitmapName override -> nymph sticks
db._modified.add(summon_skill)
```
No Python anywhere writes the nymph icon explicitly (`grep summonlyia tools/**.py` =
0 hits); it is purely inherited via the clone. The inline summon builders that DO set
their own icon (e.g. Rakanizeus at line ~634, the SV-upstream `*_summon.dbr` skills)
are unaffected - which is why only the `_build_boss_summon` family showed the nymph.

## Scope - who is affected (enumerated from `baseline_build38.arz`)
`tools/debug/_probe_soul_icons.py` groups all 2458 soul records by their granted
skill's `skillUpBitmapName`. The nymph group (`summonlyiaup.tex`) = **56 soul
records = 17 boss families x 3 tiers (n/e/l) + Lyia's own 5 soul tiers**:

| # | Boss soul | summon skill | notes |
|---|---|---|---|
| 1 | blood_toxeus (Toxeus the Murderer / Devourer of Blood) | summon_bloodtoxeus | Will's example |
| 2 | enslaver (Toxeus Enslaver) | summon_toxeus_enslaver | Will's example |
| 3 | pygmalion | summon_pygmalion | |
| 4 | phagia (Meritamen Shadowcaller) | summon_meritamen | |
| 5 | sarpedon | summon_sarpedon | |
| 6 | eaterofdays | summon_eaterofdays | |
| 7 | palai (Long Nu) | summon_longnu | |
| 8 | xeiwang | summon_xeiwang | |
| 9 | broodmother | summon_broodmother | |
| 10 | ferryman (Charon) | summon_charon_oarsman | |
| 11 | hadesmarshal | summon_hadesmarshal | built in `patches/four_generals.py` (calls `mono._build_boss_summon`) |
| 12 | kravmoloch | summon_kravmoloch_warden | |
| 13 | mnemophage | summon_mnemophage | |
| 14 | mountainblade | summon_mountainblade | |
| 15 | neferkha | summon_neferkha | built in `patches/neferkha.py` (calls `M._build_boss_summon`) |
| 16 | tantalus | summon_tantalus_shade | |
| 17 | voranthys | summon_voranthys | |
| - | lyia | summon_lyia | **NOT built via `_build_boss_summon`; nymph is CORRECT (Lyia is a nymph) - left unchanged** |

All 14 `_build_boss_summon` call sites (monolith + the two patch modules) route
through the one helper, so a single fix inside it covers 100% of them.

Two **pet-of-pet** summons also clone Lyia via `_build_boss_summon`
(`svc_enslaver_petmarauders`, `summon_broodmother_wyrmlings`) but are
`isPetDisplayable=0` and are not granted to the player, so their button icon is
never shown. They are re-iconed to the neutral default anyway for tidiness.

## Fix (data-driven, in the owning helper)
`tools/apply_svc_patches.py` (no registry module needed - `_build_boss_summon` lives
in the monolith; UI/icon fixes on our own records are allowed under the F5 precedent):

1. Module-level `_SUMMON_SKILL_ICON` map (summon-skill basename -> `(up, down)`) with
   a fitting per-boss icon, plus `_DEFAULT_SUMMON_ICON` = a neutral generic-summon
   glyph (`summonproxyup`) for any unlisted summon (**never the nymph**).
2. Helper `_set_summon_skill_icon(db, summon_skill)` - looks up the map (default
   fallback) and sets `skillUpBitmapName` + `skillDownBitmapName`. No explicit dtype:
   the cloned summon already carries both as string fields, so `set_field` preserves
   the string type (cloned-record dtype-safety law).
3. One call at the end of `_build_boss_summon`, right after `spawnObjects`.

Because the only call site is inside `_build_boss_summon` (which only ever creates
OUR summon skills), SV-original/amgoz1 summon skills (the 96-record satyr group,
`summon_lyia`, etc.) are never passed to it and stay byte-identical. Deliberate SV
design is preserved.

### Icon mapping (every path arc-verified, up + down, in shipped Resources)
Icons are reused EXISTING skill glyphs (no new art), chosen by monster family:
- blood_toxeus -> `spirit\lichekingup` (undead overlord; a worthy Toxeus-family boss commanding crimson revenants)
- enslaver -> `stealth\stalkerup` (he is a ShadowSTALKER demon)
- pygmalion -> `hunting\rapidconstructup` (the Replicator builds automatoi constructs)
- meritamen -> `soul\phagiasummonup` (the dedicated Phagia/Meritamen summon glyph, previously unused)
- sarpedon -> `scroll\summonsatyrwarriorup` (horned warrior ~ minotaur war-king)
- eaterofdays -> `SVTextures extinctionup` (sepulchral wyrm that devours existence)
- longnu -> `soul\summonhydraup` (serpent-dragon; the Flame Mother's dragonlings)
- xeiwang -> `spirit\skellysummonup` (he is a skeleton)
- broodmother -> `soul\summonslimebroodup` (summon-brood glyph)
- charon_oarsman -> `SVTextures drownedspiritup` (drowned souls of the Styx)
- hadesmarshal -> `soul\wrathofthestyxup` (marshal of Hades)
- kravmoloch -> `spirit\bonefiendup` (skeletal bound warden; source um_gorrahk skeleton)
- mnemophage -> `dream\nightmareup` (source is `epiales\as_nightmare`; a memory-eating nightmare)
- mountainblade -> `SVTextures bladecircleup` (dragonian blade-warrior)
- neferkha -> `soul\scarabswarmup` (Egyptian mummy/pharaoh)
- tantalus_shade -> `soul\specterstrikeup` (a famished shade; source lostsoul)
- voranthys -> `soul\voidsnapup` (sepulchral wyrm void-maw)

## Verification (dry-run replay vs the live baseline - no heavy build)
`tools/debug/_replay_soul_icons.py baseline_build38.arz <DEV Resources>` loads the
live-on-Steam DB (which carries the bugged nymph icons), replays exactly what the
fixed `_build_boss_summon` does (`_set_summon_skill_icon` on each boss summon), and
re-audits. Result: **REPLAY PASS**
- BEFORE: 17 player-facing boss summons on the nymph.
- AFTER: each shows its mapped icon; every up + down icon RESOLVES in the shipped
  arcs; the 2 pet-of-pet summons show the default (non-nymph).
- Soul re-scan: NO player-facing soul still on the nymph EXCEPT the 5 lyia_soul tiers
  (-> summon_lyia, correct).
- Will's example: `summon_bloodtoxeus` up icon = `DRXtextures\skill icons\spirit\lichekingup.tex` (not the nymph).

Other gates: `py_compile` OK; `tools/patches/_check_registry.py` OK (11 modules,
registry untouched); every icon path independently arc-verified via
`tools/debug/_verify_icon_paths.py` (ALL RESOLVE).

## Files
- FIX: `tools/apply_svc_patches.py` (`_SUMMON_SKILL_ICON`, `_DEFAULT_SUMMON_ICON`,
  `_summon_skill_basename`, `_set_summon_skill_icon`; one call in `_build_boss_summon`).
- Probes/harness (debug, not wired into the build): `tools/debug/_probe_soul_icons.py`,
  `_probe_soul_jewelry.py`, `_list_arc_icons.py`, `_verify_icon_paths.py`,
  `_replay_soul_icons.py`.

## Notes / follow-ups (out of scope here)
- The jewelry ring icon is a shared generic soul gem (`SVItems\jewelry\soul_{n,e,l}_icon.tex`,
  by difficulty, NOT per-boss) - unchanged; the ask was the granted-skill button.
- The 96-record SV-upstream group all share `summonsatyrwarriorup` - that is amgoz1's
  original design (many different `*_summon.dbr` skills, one shared icon) and is left
  as-is; not part of Will's report.
- The pet PARTY-UI `StatusIcon` on boss-summon pets is a separate surface (Lyia-clone
  residue) and is not the button icon Will reported; left for a future pass if desired.
