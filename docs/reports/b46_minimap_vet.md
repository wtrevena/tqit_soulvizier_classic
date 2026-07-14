# b46 minimap fix - INDEPENDENT ADVERSARIAL VET (round 1)

> Verdict: **NO_GO** (round 1 is an incomplete, in-game-unproven fix to a two-symptom bug).
> The map-tooling change itself is CLEAN and SAFE and should be RETAINED - the NO_GO is about
> completeness (label unaddressed) and lack of any in-game proof, NOT about the edit being unsafe.
> Vet worktree: feat/b46-minimap @ 9420380. All evidence re-derived independently from the
> DEPLOYED DEV map (`SoulvizierClassicDEV/Resources/Levels.arc`, 688,688,154 B) + base `database.arz`.

## What I VERIFIED independently (all PASS)

- **crypt_floor1 (idx 2280)**: corner (-2578,0,-2682), dims (160,11,160...), **dbr='' EMPTY**,
  960x960 type-2 TGA present at abs offset 740132206 (len 2,764,818 = 18+960*960*3). Root cause real.
- **GoM (idx 2276)**: dbr = `.../olympus/olympus_gom.dbr`; that record is **ABSENT** from base
  database.arz -> dangling, confirmed. GoM->olympus.dbr repoint lands inside the mapIndex-4 extent.
- **Reused zones exist w/ correct mapIndex**: knossos=0, sparta=0, olympus=4, helos=0. No new
  DB/Text records minted (validate_tags is a non-issue for the zone side).
- **LEVELS byte-exact round-trip**: build_level_index(parse(map)) == original (384,499 B, identical).
- **Surgical diff**: exactly 14 entries change, ALL are targets, ONLY the dbr field; 0 non-target
  entries change; dbr-changed idx set == target idx set. Matches implementer claim.
- **QUESTS byte-identical**: section sha256 7ad0f054, 11,460 B, untouched (fix never touches quests).
- **Navmeshes untouched**: structural - the override mutates only entry['dbr']/['dbr_raw']; no level
  blob (0x0b/0x0a) is ever read or written. Confirmed dbr/dbr_raw has exactly 2 consumers.
- **Build path**: apply_zone_dbr_overrides() wired into main() at line 1297, mutates merged_levels
  in place BEFORE both build_level_index calls (1300 intermediate, 1452 final) and before any
  TESTHUB branch -> runs on canonical + TESTHUB. NOT a hand-hacked arc. Fail-loud on fname drift.
- **py_compile PASS; git clean.**
- **Sweep completeness (independent enumeration)**: no SV-relocated interior with empty dbr was
  missed. The other empty-dbr+TGA levels are BASE AE expansion dungeons (Rhodes ScrambledEggs,
  Epirus, Elysian, Styx, Judgment) - correctly out of scope (walked into from zoned parents).
  boss_arena has a valid zone (correctly untouched); coldtombs correctly skipped (0,0 = no TGA).

## MECHANISM: now WELL-SUPPORTED (still not in-game-proven)

The Helos-hub destination map is a clean natural experiment. Of 11 outbound teleport destinations:
- **Reported broken / being fixed = exactly the zoneless ones**: Uber (empty), Sparta Crypt (empty),
  Secret Place/DarkForestEnter (empty), GoM (dangling).
- **Not reported / left alone = all 7 land in ALREADY-ZONED levels**: BossArena(olympus),
  Warband(easternsilkroad), Dorus(teleport_02medea), Tantalus/Charon/Mnemophage(teleport_04styx),
  Ephialtes(teleport_05plainsofjudgment).

This **refutes** the competing "boat-teleport never fires a region/map transition" hypothesis (that
would break ALL 11, not just the zoneless ones), and confirms the zone-dbr is the discriminator. The
crypt georeference is sane (~700u east of the Delphi-underground cluster; extends the Greece page
modestly). Confidence in the minimap fix is HIGH for Uber/GoM/SpartaCrypt.

## BLOCKING ISSUES

1. **[HIGH] Symptom 2 (the "Village of Helos" label) is EXPLICITLY UNFIXED.** The implementer
   deferred it to "round 2" (needs 0x17 RE, no proven round-trip tooling). Will reported ONE bug
   with TWO symptoms; only the minimap is addressed. Under the standing DONE-means-DONE directive,
   triage-into-follow-up = not done. VERIFY item 4 (labels resolve) fails.
2. **[HIGH] No in-game confirmation.** The mechanism is inferred; the implementer states a launch is
   REQUIRED and cannot be done statically (and the vet is barred from launching). The reported
   symptom is not confirmed resolved. This is expected at this stage, but it means the change must
   NOT be represented as resolving the report until Will confirms the minimap in-game.
3. **[MEDIUM] RCA internal contradiction.** The RCA frames both symptoms as ONE root cause ("missing
   map/region identity"); the result doc then says the label is a SEPARATE 0x17 mechanism that the
   zone fix does not touch. VERIFY item 1 ("the defect explains BOTH symptoms") is therefore not
   established - it is two mechanisms, one fixed, one deferred.

## NON-BLOCKING / FLAG

- **[MEDIUM] Secret Place cluster (11 levels)** parked at Z~-5900..-6200 is ~2000u beyond Greece's
  current composited Z-extent (mapIndex-0 cornerZ max -3943). Continent is INFERRED (=Greece). Risk:
  it composites as a detached island or possibly falls off the Greek page (imagery still misplaced).
  Not the reported bug; strictly not-worse than black-void; one-constant swap if wrong. Watch it.
- **[LOW] crypt_floor1 -> knossos.dbr** though the physically nearest Greek content is Delphi
  underground (~700u) not Knossos (all west, >1100u). Moot under continent-paging (Version A);
  suboptimal under per-zone-paging (Version B). delphi.dbr would align better if paging is per-zone.

## RETAIN GUIDANCE

Keep the round-1 map edit (it is clean, safe, well-scoped, and likely fixes the Uber minimap). To
clear GO: (a) round-2 label fix, and (b) an in-game confirmation on DEV that the Uber Dungeon minimap
draws under the player and the label no longer reads "Village of Helos".
