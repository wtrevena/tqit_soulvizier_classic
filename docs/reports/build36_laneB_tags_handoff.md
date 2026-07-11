# build36 lane B - tag handoff summary

**Status: ALREADY WIRED via the data path. No phase-2 integration needed.**
`tools/build_text_arc.py` was NOT modified. Machine-readable detail:
`build36_laneB_tags_handoff.json`.

## How the tags reach Text.arc (data path, no pipeline edit)
`build_svc_database.py` `main()` writes the graft's `_GRAFT_TAGS` dict into
`work/SoulvizierClassic/Database/uber_soul_tags.txt` (alongside the soul/legacy/
extended/thrown tag blocks). `build_text_arc.py` reads that file as its 3rd
argument and (a) emits every key into `modstrings.txt` inside `Text.arc` and
(b) lists every key in the `mod_authored_tags.txt` manifest. `validate_tags.py`
then treats them as mod-owned AND finds them defined -> PASS.

## The three tag classes for the 14 grafted player skills

| Class | Count | Action | Examples |
|---|---|---|---|
| Base-Atlantis `x3tag*` | 8 | none (resolve at runtime from base Text) | Perfect Block, Unyielding Phalanx, Fire Nova, Lightning Dash, Earthbind, Sylvan Protection, Dream Image, Lasting Legacy |
| SV-authored, genuinely new | 8 | authored via `uber_soul_tags.txt` | Slam (+DESC), Fissure (+DESC), Burning Bolts (+DESC), Frost Nova (+DESC) |
| SV-authored, already shipped | 4 | NOT re-added (mod's 0.98i text already defines them) | Rupture NAME/DESC, Flare NAME/DESC |

## The 8 new tags (authored)
`tagSlam_NAME`, `tagSlam_DESC`, `tagSlam_FissureNAME`, `tagSlam_FissureDESC`,
`tagBurningBoltsNAME`, `tagBurningBoltsDESC`, `tagSVAERSkillStorm001`,
`tagSVAERSkillStormDescription001`.

## Why 4 tags are NOT emitted (the duplicate-tag gate catch)
`tagRuptureNAME/DESC` + `tagFlareNAME/DESC` already exist in the mod's SV 0.98i
`Text_EN.arc` (`xuniqueequipment.txt`). `build_text_arc` keeps the FIRST
definition, so re-adding them is a no-op for the same-value ones and a HARD
duplicate-tag-gate failure for `tagRuptureDESC` (0.98i says "Staff Only";
SVAERA's says "Staff or Bow"). The gate caught this on the first Text build;
the fix is to drop these 4 from the graft. The grafted Earth Rupture/Flare
skills reference the tags and resolve to the existing 0.98i definitions (the
only cosmetic residue: Rupture's tooltip reads "Staff Only" though the skill is
Staff-or-Bow; not overridable via the data path, functionally fine).

## Expected tags-gate delta
**None (clean PASS).** Measured on the rebuilt arz + Text.arc:
`validate_tags` = "all 148 referenced mod tags present" + "all 205 authoritative
tags present" -> RESULT PASS. `Duplicate-tag gate OK`. No residual failure.
