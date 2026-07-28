"""emberteeth_summon - SOUL-EMBERTEETH-SUMMON (Will 2026-07-14, verbatim:
"emberteeth soul should let you summon him").

BACKLOG source: docs/BACKLOG.md "QUEUED FEATURE: SOUL-EMBERTEETH-SUMMON (APPROVED
by Will 2026-07-14, not yet scheduled)". Report: docs/reports/b91_debt_db.md.

GROUND TRUTH (decoded from the b90 golden arz `c1a8fa2a`, BEFORE this module)
---------------------------------------------------------------------------
`records\\creature\\monster\\orthrus\\um_emberteeth.dbr`

| field | value |
|---|---|
| monsterClassification | `Hero` |
| charLevel | `[18, 43, 58]` (the LOWEST-level summon source in the whole roster) |
| characterLife | `[2355.2, 2944.0, 3532.8]` |
| characterRacialProfile | `Demon` |
| description | `tagNewHero12` |
| baseTexture | `Creatures\\monster\\orthrus\\brimstoneorthus01.tex` (a brimstone orthrus - the two-headed fire hound) |
| his own kit | `retaliation_1fireperlevelx100levels`, `orthus_firebreath` (specialAttack2), `ondeath_fireorb`, `emberteeth_meleeattack`, `physdmg_meleeonly`, `pillarofflame` (specialAttack3), `armor_passive` |
| soul drop | `chanceToEquipFinger2 = 50.0` (RANDOM-pool roamer; UNCHANGED by this module) |

His soul family `records\\item\\equipmentring\\soul\\orthus\\emberteeth_soul_{n,e,l}.dbr`
(name tag `tagSoulName331`, itemLevel 18/42/59) **grants no skill at all today** -
it is a pure fire-stat ring (`offensiveFireMin` 6/13/18, `offensiveSlowFire*` burn,
`retaliationFire*`, `defensiveFire` 30/42/53). So "let you summon him" is genuinely
unbuilt, exactly as the triage said (`grep -ril emberteeth tools/` finds only the
monster + its melee skill).

WHAT THIS MODULE DOES
---------------------
1. Builds `emberteeth_{1,2,3}` (3 permanent pets) + `summon_emberteeth.dbr` (a
   manual-cast `Skill_SpawnPet` button) through the shared, proven
   `apply_svc_patches._build_boss_summon` pipeline with `source =
   um_emberteeth.dbr` - so the pet IS Emberteeth: his own mesh/texture/anim
   table/attack skill/attribute cadence/skill kit, his race + voice + distress
   group (the b81 `_align_pet_identity` law, R-11), his own gear mirrored through
   the sanctioned `_set_pet_equipment` loot-table path (NEVER Monster.tpl
   equipment/loot field copies - the documented crash class), the D19 pet-mobility
   assert, the b40 granted-skill icon and the b71 pet-bar portrait.
2. Wires all three soul tiers to that summon via `_wire_summon_soul`
   (`itemSkillLevel` 1/2/3 -> the epic soul spawns the epic-tier pet, R-43's
   companion check) and strips any inherited `itemSkillAutoController` so it is a
   pet BUTTON, never an on-attack proc (the D21 Long Nu / R-44 crowboar law).
3. **Keeps every existing benefit.** `_wire_summon_soul` writes only
   `itemSkillName` / `itemSkillLevel`; the fire offence, burn, retaliation and
   `defensiveFire` stats on all three rings are untouched (proven in the
   record-diff: the ONLY new keys on the soul records are the two skill fields).
   The soul's display name `tagSoulName331` is deliberately NOT renamed - Will
   asked for a summon, not a rename.

TIER BAND (derived from the roster, not invented)
-------------------------------------------------
`char_level` mirrors the source exactly `[18, 43, 58]`. For life, the shipped
player-facing boss-summon pets fall into two clear life-per-charLevel clusters:
the flagship uber bosses at ~250-296/level (Mountainblade 11000/43, Xeiwang
12000/48) and the lesser summons at ~119-167/level (`_build_boss_summon` callers
at :7690 and :15141). Emberteeth is a mid-tier `tagNewHero` Hero, not an uber
boss, so he takes the LOWER cluster: ~133/level normal rising to ~164/level
legendary -> `[2400, 6000, 9500]`. That is strictly progressing, above his wild
form at every tier (the roster-wide pet convention), and nowhere near the uber
band. Damage and regen are scaled off Mountainblade's L43 numbers by the same
charLevel ratio.

ICON / PORTRAIT (player-surface checklist, standing law 3)
----------------------------------------------------------
The granted-skill icon is `DRXtextures\\skill icons\\soul\\summonchimera{up,down}`
- a fire-breathing multi-headed beast glyph, the closest on-identity match for a
two-headed brimstone orthrus. It is **arc-verified present** in the shipped
`DRXtextures.arc` and **verified UNCLAIMED** by any other `_SUMMON_SKILL_ICON`
entry (no icon collision, the b85 bwpriest lesson). No `chimera_party_*` portrait
ships, so the pet-bar portrait falls back to the neutral summon-proxy - never the
Lyia nymph - which is the same documented position as pygmalion / eaterofdays /
xeiwang / mountainblade. A bespoke Emberteeth portrait is registered as debt
(art call, WILL-CONFIRM), not silently deferred.

ORDER
-----
Registered after every soul-wiring + rate module and before `fx_dangling_cleanup`
/ `visuals`, so it sees the FINAL soul records and its own new skill records are
still swept by the FX hygiene pass and validated by the whole gate battery
(pet parity / gear / skill-kit, soul-augment resolution, soul-summon identity,
soul naming, validate_summon_pets, A9 render chain, F2 summons contract).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

MODULE_NAME = ("SOUL-EMBERTEETH-SUMMON (Will 2026-07-14: 'emberteeth soul should "
               "let you summon him')")

_SRC = r'records\creature\monster\orthrus\um_emberteeth.dbr'
_PETS = [rf'records\skills\soulskills\pets\emberteeth_{i}.dbr' for i in (1, 2, 3)]
_SUMMON = r'records\skills\soulskills\summon_emberteeth.dbr'
_SOULS = [rf'records\item\equipmentring\soul\orthus\emberteeth_soul_{t}.dbr'
          for t in 'nel']

_DISPLAY_TAG = 'tagSVCSummonEmberteeth'
# The pet's in-game name = the SOURCE monster's own description tag, so the pet
# bar reads exactly what the wild hero reads (the b81 identity law).
_DESC_TAG = 'tagNewHero12'

# On-identity granted-skill icon (see the module docstring). Registered into the
# shared data-driven map so _set_summon_skill_icon picks it up - the module never
# hardcodes bitmap fields on the skill itself (the b85 bwpriest collision lesson).
_ICON = (r'DRXtextures\skill icons\soul\summonchimeraup.tex',
         r'DRXtextures\skill icons\soul\summonchimeradown.tex')

_CHAR_LEVEL = [18, 43, 58]                       # == the source's own band
_LIFE = [2400.0, 6000.0, 9500.0]                 # lower cluster, ~133-164/level
_LIFE_REGEN = [10.0, 25.0, 45.0]
_DMG_MIN = [28.0, 65.0, 90.0]
_DMG_MAX = [45.0, 105.0, 145.0]


def _norm(s):
    return str(s).replace('/', '\\').lower()


def _one(db, rec, field, default=None):
    """First value of a field (arz fields are always value LISTS)."""
    v = db.get_field_value(rec, field)
    if isinstance(v, list):
        return v[0] if v else default
    return default if v is None else v


def apply(db, tags):
    import apply_svc_patches as M

    if not db.has_record(_SRC):
        raise SystemExit(f"emberteeth_summon: source monster missing: {_SRC}")
    for s in _SOULS:
        if not db.has_record(s):
            raise SystemExit(f"emberteeth_summon: soul tier missing: {s}")

    # ── ground-truth assert: the soul must NOT already grant a summon ────────
    # If a future lane builds this, the module must be retired rather than
    # silently double-wiring (no quiet no-op).
    pre = db.get_field_value(_SOULS[0], 'itemSkillName')
    pre = (pre[0] if pre else '') if isinstance(pre, list) else (pre or '')
    if _norm(pre) == _norm(_SUMMON):
        raise SystemExit(
            "emberteeth_summon: the soul ALREADY points at summon_emberteeth - "
            "another lane built this. Retire this module and close the BACKLOG "
            "item instead of running it twice.")

    # Snapshot the fire-stat payload of every tier so we can PROVE nothing the
    # player already gets is lost (Will: 'keep existing value').
    KEEP = ('offensiveFireMin', 'offensiveFireMax', 'offensiveSlowFireMin',
            'offensiveSlowFireDurationMin', 'retaliationFireMin',
            'retaliationSlowFireMin', 'retaliationSlowFireDurationMin',
            'defensiveFire', 'itemNameTag', 'itemLevel', 'levelRequirement',
            'itemClassification', 'itemQualityTag', 'bitmap', 'mesh')
    before = {s: {k: list(db.get_field_value(s, k) or []) if
                  isinstance(db.get_field_value(s, k), list)
                  else db.get_field_value(s, k) for k in KEEP} for s in _SOULS}

    # ── register the icon BEFORE building (the builder reads the map) ────────
    key = M._summon_skill_basename(_SUMMON)
    clash = [k for k, v in M._SUMMON_SKILL_ICON.items()
             if k != key and _norm(v[0]) == _norm(_ICON[0])]
    if clash:
        raise SystemExit(
            f"emberteeth_summon: icon {_ICON[0]} is already claimed by {clash} - "
            f"pick an unclaimed glyph (the b85 bwpriest collision lesson).")
    M._SUMMON_SKILL_ICON[key] = _ICON

    # ── build the pets + the manual-cast summon button ──────────────────────
    if not M._build_boss_summon(
            db, _SRC, _PETS, _SUMMON, _DISPLAY_TAG, _DESC_TAG,
            char_level=list(_CHAR_LEVEL), life=list(_LIFE),
            life_regen=list(_LIFE_REGEN),
            dmg_min=list(_DMG_MIN), dmg_max=list(_DMG_MAX)):
        # loadout omitted -> _mirror_source_loadout(strict=True) mirrors whatever
        # the orthrus itself equips (a beast rig equips nothing, so the pet stays
        # barehanded exactly like its wild form - the A1 gear-parity law).
        raise SystemExit("emberteeth_summon: _build_boss_summon FAILED")

    # ── wire all three soul tiers to it (manual-cast, tier 1/2/3) ───────────
    M._wire_summon_soul(db, _SOULS, _SUMMON)   # name_tag omitted: NO rename

    # ── prove nothing the player already had was lost ───────────────────────
    lost = []
    for s in _SOULS:
        for k, v in before[s].items():
            now = db.get_field_value(s, k)
            if isinstance(now, list):
                now = list(now)
            if now != v:
                lost.append((s, k, v, now))
    if lost:
        raise SystemExit(
            "emberteeth_summon: the summon wiring CHANGED pre-existing soul "
            f"benefits (Will: keep existing value): {lost[:8]}")

    tags[_DISPLAY_TAG] = 'Summon Emberteeth'

    print(f"  emberteeth_summon: 3 permanent pets from um_emberteeth's own rig "
          f"(Hero band {_CHAR_LEVEL}, life {_LIFE}) + manual-cast summon button; "
          f"all 3 soul tiers wired 1/2/3 with every pre-existing fire stat intact")


def verify(db, tags):
    """Runs over the FINAL merged db (step 4, after the whole gate battery)."""
    import apply_svc_patches as M   # noqa: F401 - kept for symmetry/debugging

    problems = []
    if not db.has_record(_SUMMON):
        problems.append(f"summon skill missing: {_SUMMON}")
    else:
        spawn = db.get_field_value(_SUMMON, 'spawnObjects') or []
        spawn = spawn if isinstance(spawn, list) else [spawn]
        if [_norm(x) for x in spawn] != [_norm(p) for p in _PETS]:
            problems.append(f"summon spawnObjects {spawn} != the 3 emberteeth pets")
        if _one(db, _SUMMON, 'isPetDisplayable', 0) != 1:
            problems.append("summon is not player-displayable (should be a pet button)")
        if 'summonlyia' in _norm(_one(db, _SUMMON, 'skillUpBitmapName', '')):
            problems.append("summon still wears the Lyia NYMPH icon (b40 law)")

    # The pets must BE Emberteeth: same mesh + same race as the source.
    src_mesh = _one(db, _SRC, 'mesh', '')
    src_race = _one(db, _SRC, 'characterRacialProfile', '')
    for p in _PETS:
        if not db.has_record(p):
            problems.append(f"pet missing: {p}")
            continue
        m = _one(db, p, 'mesh', '')
        if _norm(m) != _norm(src_mesh):
            problems.append(f"{p} mesh {m!r} != source {src_mesh!r} (not Emberteeth)")
        r = _one(db, p, 'characterRacialProfile', '')
        if _norm(r) != _norm(src_race):
            problems.append(f"{p} race {r!r} != source {src_race!r} (R-11/b81)")
        ttl = db.get_field_value(p, 'spawnObjectsTimeToLive')
        if ttl not in (None, [], '', 0, [0], [0.0], 0.0):
            problems.append(f"{p} carries spawnObjectsTimeToLive={ttl} (must be "
                            f"permanent - the Lyia Leafsong convention)")

    # All three tiers manual-cast at 1/2/3, and the fire payload survived.
    for i, s in enumerate(_SOULS):
        sk = _one(db, s, 'itemSkillName', '')
        lv = _one(db, s, 'itemSkillLevel')
        if _norm(sk) != _norm(_SUMMON):
            problems.append(f"{s} itemSkillName {sk!r} != {_SUMMON}")
        if lv != i + 1:
            problems.append(f"{s} itemSkillLevel {lv} != {i + 1} (epic soul must "
                            f"spawn the epic-tier pet - R-43 companion check)")
        ctrl = db.get_field_value(s, 'itemSkillAutoController')
        if ctrl not in (None, [], ''):
            problems.append(f"{s} still carries itemSkillAutoController={ctrl!r} "
                            f"(a summon soul is a BUTTON, never an on-attack proc "
                            f"- the D21 Long Nu / R-44 crowboar law)")
        if not _one(db, s, 'defensiveFire'):
            problems.append(f"{s} lost its pre-existing defensiveFire benefit")

    if problems:
        for p in problems[:15]:
            print(f"  EMBERTEETH OFFENDER: {p}")
        raise SystemExit(f"emberteeth_summon.verify FAILED: {len(problems)} problem(s)")

    print("  emberteeth_summon.verify OK: 3 permanent Emberteeth pets on his own "
          "mesh + race, manual-cast summon button (non-nymph icon), all 3 soul "
          "tiers at itemSkillLevel 1/2/3 with their fire payload intact")
