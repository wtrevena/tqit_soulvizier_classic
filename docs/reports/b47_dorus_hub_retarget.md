# b47 HUB RETARGET SPEC (for b39 hub-v2 integration) - Kroisos traveler

> Trust: INTEGRATION SPEC. b47 renamed + relocated the Propontis super-boss (was
> "Dorus, the Drowned King" in the Great Tomb of Dorus, now **Kroisos, the Coin-Drowned**
> in the Tomb of the Queens / Medea_TempleUG_Tomb03). The Helos hub traveler that carries
> the player to that encounter must be retargeted. **b39 hub-v2 owns the authoritative
> traveler**; this spec is applied there at integration. b47 also applied the same edits
> to its own branch copy (build38a base) for coherence, so if b39 and b47 both touched
> `svc_helos_trav_dorus`, reconcile using THIS spec as the source of truth. No em dashes.

## The traveler
- Outbound record: `records\quests\svc_helos_trav_dorus.dbr` (placed in Helos; unchanged spot).
- Return record: `records\quests\svc_area_return_dorus.dbr` (placed in the destination tomb).
- Menu label tag: `tagSVCHelosToDorus`. Name tag: `tagSVCNpcTravDorus`. (KEYS unchanged.)

## 1. Rename the labels (tags pipeline, apply_svc_patches._create_helos_traveler_hub)
| tag | OLD value | NEW value |
|---|---|---|
| `tagSVCNpcTravDorus` (name) | `Traveler: Medea Tomb (Dorus)` | `Traveler: Tomb of the Queens (Kroisos)` |
| `tagSVCHelosToDorus` (dest) | `The Drowned King (Medea Tomb)` | `Kroisos, the Coin-Drowned` |

(b47 already set these in its branch's `HELOS_HUB_OUTBOUND` row for `svc_helos_trav_dorus`.)

## 2. Retarget the outbound boat-teleport landing (build_quest_files.py HELOS_HUB_TRAVEL)
- OLD target: **WORLD (312, 1, -8462)** = Medea_TempleUG_Tomb01 LOCAL (52,60) - the old boss
  spot, right beside the base-game quest King Dorus shade (WORLD (276,-8472)).
- NEW target: **WORLD (428, 1, -8113)** = Medea_TempleUG_Tomb03 LOCAL (75, 1.0, 55), ~8u NW
  of Kroisos at WORLD (436,-8117). Surveyed on the canonical map (Levels_merged 60a62880,
  survey_uberboss_spots.py --base 72): d=0.14u, clr@3.0 100%/100%/100% (N/E/L), comp#1/259143.
- The RETURN teleport target is UNCHANGED (Helos plaza WORLD (-5980, 1, 909)).

## 3. Retarget the return-NPC placement (build_section_surgery.py HELOS_HUB_RETURN_SPECS)
- Host key changes with `DORUS_HOST_KEY` (now `xpack/levels/area02_medea/undergrounds/medea_templeug_tomb03.lvl`).
- OLD: Tomb01 LOCAL (49.0, 1.2, 63.0).
- NEW: Tomb03 LOCAL **(72.0, 1.0, 57.0)** = WORLD (425,-8111), ~11.7u from Kroisos; on-mesh
  d=0.14u, clr@3.0 100% all sets, comp#1. (b47 already applied this via the shared
  `DORUS_HOST_KEY` constant + updated coord.)

## Cross-wave notes
- **b44 landing-clearance gate:** the new landing WORLD (428,-8113) / LOCAL (75,55) is on-mesh
  clr@3.0 100% all 3 tilesets, comp#1 - already clearance-clean; include it in the gate's spot list.
- **b48 hub-traveler audit:** the Dorus traveler's destination + labels change per this spec;
  fold into the 17-traveler audit so the "responds + lands on-mesh" checks use the new coords.
- **b42 majestic chests:** the 3-region-tuned chests apply at the NEW boss location - see
  b47_dorus.md "b42 dependency".
