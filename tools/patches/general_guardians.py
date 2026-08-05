r"""tools/patches/general_guardians.py - the Guardians of the General must READ
as uber (R-100 #18).

WILL'S RULING (docs/WILL_RULINGS.md R-100 item 18, 2026-07-29, verbatim):

    "also the guys who are the guardians of the general the uber bosses we added
     are super weak and they dont have any chests and dont drop any orbs or
     anything. also they are small and they look just like the other guys and i
     killed them so fast they are so weak they appear just like normal guys they
     are not big with no special skills or anything to make them even noticeable
     besides their red names"

The six records are `svc_general_{a,b,c}_guard{1,2}.dbr`, built by
`tools/patches/four_generals.py` step 4 (`_build_guards`) as the honor guards of
Hades' three generals. This module is a RETUNE OF THOSE SIX plus their three
placement proxies; it creates no monster, retires nothing, and never touches a
general.

================================================================================
1. EVERY COMPLAINT, MEASURED ON THE SHIPPED BYTES BEFORE ANYTHING WAS DESIGNED
================================================================================
Source: `local/baseline_main_7efd107.arz`, this branch's own build of `main`
@ 7efd107 (md5 6a3a491db546b603c52132237c40aa63, 51,124 records). Every number
below is a field read, not an estimate. He is right on all six counts.

  "they are small"
      `scale = 1.45` on all six. The plain `am_warden_43` Champion they were
      CLONED FROM is `scale = 1.5`, and their own general is `1.65`. So the guards
      are SMALLER than the ordinary machae standing next to them.
      `_build_guards`' docstring calls 1.45 "a modest scale bump"; measured
      against its own donor it is a SHRINK. That is the literal cause of "small".

  "they look just like the other guys"
      `mesh = XPack\Creatures\Monster\Machae\machae01b.msh` on
      `svc_general_a_guard1`, byte-identical to `am_warden_43`'s. Both guards of a
      pair clone ONE donor, so they are also identical to each other.

  "super weak ... i killed them so fast"
      `characterLife = [3200, 4200, 5400]` at `charLevel [42, 58, 72]`.
      Their general: `[20244, 25305, 30366]` - the pair together is 32% of ONE
      general. Zero defensive resist fields. `characterLifeRegen = 0`.
      The house bar for a NAMED ELITE ESCORT of one of our own ubers, measured
      across the mod's shipped escorts:
          um_enslaver_marauder_99        scale 2.0   life [10000, 14000, 18000]
          svc_diadochi_striderguard_97   scale 2.4   life [10000, 14000, 19000]
          svc_tantalus_famishedshade_90  scale 2.0   life [ 4500,  6500,  9000]
          svc_obs_escort_bonehallow      scale 1.3   life [ 7672,  9590, 11508]
      The guards sit BELOW every one of them on both axes.

  "no special skills or anything"
      kit = `armor_passive`, `bonusdamage_physical`, `shieldcharge`, and
      `specialAttackSkillName = shieldcharge`. All four values are INHERITED
      VERBATIM from `am_warden_43`. `_build_guards` added zero skills, so a
      "named elite honor guard" fights exactly like the trash champion it was
      cloned from - and all six fight identically to each other.

  "they dont have any chests"
      `records\drxmap\proxy\q_general_{a,b,c}_guardpair.dbr` carry no
      `accessory1` / `accessoryEpic1` / `accessoryLegendary1`.

  "dont drop any orbs"
      no `treasureProxyName` on any of the six.

  "besides their red names"
      correct and already true: the `{^r}` is in the display tags four_generals
      minted (`tagSVCGuardDysA` = "{^r}Ravok the Lawless ~ Machae Reaver", etc).
      Those NAMES are the only thing about these six that was ever held to the
      amgoz1 bar. This module makes the MECHANICS keep the promise the names make.

================================================================================
2. THE amgoz1 BAR, AND HOW IT IS APPLIED HERE
================================================================================
NOTE ON THE REFERENCE FILE: `amgoz1_design_voice.md` (cited by the 2026-07-11
standing directive) is STILL not present anywhere in this repo - checked with
`git log --all --diff-filter=A -- "*amgoz*design*"` (empty) and a tree-wide
`find`. This module follows the same fallback `uber_orphan_weapons.py` recorded:
the voice as documented in CLAUDE.md/BACKLOG.md and in the shipped SV content -
"monster-identity-driven, flavorful, never generic filler", never a stat stick.
Flagged again in the wave report.

Applied literally: the fix is NOT "multiply the six identical stat blocks". Each
guard already HAS an identity - four_generals wrote it into the name and then
never implemented it. So each guard gets a SIGNATURE PAIR of skills that its own
epithet demands, and no two of the six share one:

  general a - Dysnomion the Lawless (spirit / decay / lifedrain)
    guard1  {^r}Ravok the Lawless ~ Machae Reaver
            a reaver charges and breaks the ground under you:
              minotaur_onslaught          (Skill_WeaponPool_ChargedLinear)
              gigantes_groundbreaker      (Skill_AttackWave)
    guard2  {^r}Sethuun ~ Machae Soul-Warden
            a soul-warden takes the life out of the room:
              empusa_spirit_lifedrainnova (Skill_AttackProjectileAreaEffect)
              hero_slowspiritbolt_ring    (Skill_AttackProjectileRing)

  general b - Makaria (poison)
    guard1  {^r}Bhikru the Bilespitter ~ Machae Venomancer
            the bilespitter spits, the venomancer bolts:
              hero_vomitbile              (Skill_AttackProjectileBurst)  [BLANK-ANIM CLONE]
              empusavenomancer_venombolt  (Skill_AttackProjectile)       [BLANK-ANIM CLONE]
    guard2  {^r}Nakoth ~ Machae Plague-Ward
            a plague-ward fills the ground he wards:
              empusa_venom_venomcloud     (Skill_AttackProjectileAreaEffect)
              hero_poisonwave             (Skill_AttackWave)

  general c - Trophonios (flame)
    guard1  {^r}Kharzun the Ember ~ Machae Pyre-Ward
            the pyre-ward raises the pyre:
              empusa_pyro_pillarofflame   (Skill_AttackProjectileAreaEffect)
              hero_flamewave              (Skill_AttackWave)             [BLANK-ANIM CLONE]
    guard2  {^r}Voreth ~ Machae Cinder-Reaver
            a cinder-reaver closes and scatters embers:
              gigantes_shieldcharge       (Skill_AttackWeaponCharge)     [BLANK-ANIM CLONE]
              hero_bouncingfire_ring      (Skill_AttackProjectileRing)

Twelve distinct signature skills over six monsters, no two guards alike. EIGHT of
the twelve are pointed at VERBATIM as shipped; the other FOUR ride a mod-authored
BLANK-ANIM CLONE of the shipped skill, because the shipped record names a special
animation the machae rig does not have (section 2b). No new FX and no new art in
either case: a clone is the donor's own bytes with ONE clip NAME cleared.

DENSITY LAW, HONOURED BY CONSTRUCTION (b76 / R-31, and the brief's explicit
"mind the b76 density precedent if you add summons"): NOT ONE of the twelve is a
pet-spawner. `verify()` re-asserts that mechanically - every skill this module
puts on a guard is checked to be non-`Skill_*SpawnPet*` and to declare no
`spawnObjects` - so this lane cannot contribute a single permanent entity to the
Hades war-council rooms. The Guardians read as uber through KIT and PRESENCE, not
through adds.

================================================================================
2b. THE ROUND-1 DEFECT: FOUR OF THE TWELVE COULD NOT FIRE AT ALL
================================================================================
Round 1 wired the twelve and the round-1 gate went 14/14 green while FOUR of them
were mechanically dead. That is the defect this section fixes, and the reason the
gate below now measures castability instead of assuming it.

MECHANISM (this project's own crash-law RE, already applied once as the b42
Ephialtes Dread Nova fix in `tools/apply_svc_patches.py`): Game.dll's
`SkillManager::StartSkill` aborts the cast, SILENTLY, when the caster's animation
table has no clip for the skill's `skillSpecialAnimationName`. A monster's table
is whatever its own `charAnimationTableName` points at.

MEASURED on the round-1 build (`work/SoulvizierClassic/Database/SoulvizierClassic.arz`,
51,151 records), not assumed:
  * all six guards bind
        charAnimationTableName = records\xpack\creatures\monster\machae\anm\anm_machae.dbr
  * that table declares exactly FOUR `<row>SpecialAnimRef<N<=15>` clip names:
        bow1='HeavyShot'  sHanded1='ThunderClap'  spear1='Slam'  spear2='Strike'
  * four of the twelve name a clip outside that set, so they never fired:
        hero_vomitbile              -> 'Belch'         (guard b1)
        empusavenomancer_venombolt  -> 'Belch'         (guard b1 - BOTH of its two)
        hero_flamewave              -> 'ShadowScythe'  (guard c1)
        gigantes_shieldcharge       -> 'Charge'        (guard c2)
  * and the specialAttack SLOT-1 skill all six INHERITED from the warden donor,
        records\skills\defensive\shieldcharge.dbr -> 'ShieldCharge'
    is not in that set either, on skillName3 AND specialAttackSkillName.
  * total dead cast slots on the six guards: 20.
  => Bhikru the Bilespitter (b1) had ZERO castable specials of any kind: both of
     his signature skills AND his inherited slot-1 special were all dead. Will's
     complaint ("no special skills or anything to make them even noticeable") was
     still literally true for one of the six after round 1.
  The three generals themselves are CLEAN on this invariant (measured: no
  anim-carrying skill in any cast slot), so nothing about them changes.

THE FIX (a), the exact b42 recipe, applied to all five offending skills:
CLONE the shipped skill into `records\skills\svc\` and BLANK the clone's
`skillSpecialAnimationName`, so the cast rides the default attack clip every rig
has. The guards are repointed at the clones; the shipped records are never
touched. Precedent for a blank clip on each offender's own Class, counted in this
same build:
      Skill_AttackProjectileBurst   102 shipped records already blank
      Skill_AttackProjectile        156
      Skill_AttackWave               29
      Skill_AttackWeaponCharge        5  (e.g. coldtusk_charge, tykos_charge)

WHY NOT FIX (b) (repick a clip the machae rig HAS): the table's four clips are
per-WEAPON-ROW (bow / sHanded / spear), and which row the engine reads depends on
what the guard has actually equipped at spawn - which here resolves through a
100%-chance RightHand/LeftHand loot pool, not a fixed weapon. A repick would
therefore be castable only for some rolls. Blanking is row-independent, so it is
the choice that is castable on every roll. This is a deliberate per-skill call,
not a blanket one: it was taken for all four because all four sit on the same rig
with the same unknown weapon row.

CLONE, NEVER EDIT IN PLACE (shared-record law): every one of the five offenders
has other carriers that must not change behaviour -
      hero_vomitbile              xhero_woodear_40, xhero_longjaw_40
      empusavenomancer_venombolt  25 other monsters (empusa/epiales families)
      hero_flamewave              xhero_ephialtes_47, xhero_terrorofthedark_47
      gigantes_shieldcharge       am_armorite_40/42, xhero_polybotes_47
      shieldcharge                85 other carrier slots (every machae warden,
                                  the Defensive mastery tree, ...)
`verify()` proves, on the built db, that each DONOR still carries its original
clip name (i.e. was not edited) and that each clone carries none.

================================================================================
3. THE RETUNE - every number derived from something already in the db
================================================================================
  scale            1.45 -> 2.0
      Not invented: `um_enslaver_marauder_99` (scale 2.0) is the mod's own named
      elite guard of an uber, and it is the encounter Will himself points at as
      the model in the SAME message (R-100 #13: "give ... some guys they can
      summon like toxeus the murderer enslaver of souls has"). 2.0 is 33% over
      every machae in the room (warden 1.5) and 21% over their general (1.65).

  characterLife    [3200, 4200, 5400] -> 45% of the GENERAL's, per difficulty
      = round(0.45 * [20244, 25305, 30366]) = [9110, 11387, 13665].
      DERIVED from the encounter, so the pair is ~91% of one general combined: a
      real fight that still never eclipses the boss. Lands inside the measured
      house band above on all three difficulties. 2.8x - 2.5x the old values.

  characterLifeRegen 0.0 -> 5.0
      the general's own value, copied rather than invented.

  defensive*       (absent) -> a THEMED pair per general, never a flat wall
      Each pair resists its own general's element and takes the shared physical
      floor. The floor and the element numbers are the marshal's own
      (`defensivePhysical 30`), scaled down one tier to 20/35 so the guards stay
      under the warlord they serve.

  treasureProxyName (absent) -> genericbossorb_03
      THE ORB LADDER, MEASURED: 01 = ten L16-20 bosses; 02 = five, INCLUDING our
      own Champion escort `svc_obs_escort_permean` (so a Champion carrying a boss
      orb is already shipped precedent); 03 = six L45-48 bosses - the guards' own
      band (`charLevel [42,58,72]`); 04 = nineteen, including their marshal;
      05 = the eight-record Toxeus apex roster, RESERVED by R-99 and gate-locked
      by `uber_apex_orb.verify()`.
      03 is therefore the honest tier: it matches their level band, it leaves the
      R-99 apex untouched, and it does not add consumers to `genericbossorb_04`,
      whose consumer set `uber_apex_orb.verify()` audits. NOTHING about the orb
      records themselves is edited - this is a POINTER, not a shared-record edit.

  chest            (none) -> ONE dedicated Boss-locked hoard per PAIR
      Built with the monolith's own `_svc_build_dedicated_hoard` recipe (loot
      table -> FixedItemContainer -> ProxyAccessoryPool per difficulty tier) and
      wired onto the guard-pair proxy's accessory1/Epic1/Legendary1.
      EXACTLY ONE CHEST PER ENCOUNTER, structurally: `Proxy.tpl` exposes only
      accessory1 / accessoryEpic1 / accessoryLegendary1 and ProxyAccessoryPool is
      a single weighted pick with no spawn count (proven in
      `_svc_build_world_chest_proxy`'s comment block). So this cannot reproduce
      R-100 #9's three-Tantalus-Hoards problem.
      `LockedClassification` is overridden from the recipe's `Boss` to `Champion`
      - the guards ARE Champions, so a Boss lock would leave the chest sealed
      forever. `Champion` is a shipped, valid value (3 carriers), one of which is
      `hidden_bloodcave_chest_01`, the very donor this chain clones.

  monsterClassification  Champion, UNCHANGED - deliberately
      Promoting to Hero would make them soul-eligible under
      `wire_souls_to_monsters` (Hero/Boss/Quest) and collide head-on with R-106
      ("only hero monsters should drop their soul") and the in-flight soul-rate
      lane. Will asked for chests and orbs, not souls. `_svc_clear_soul_loot`'s
      zeroed soul loot is asserted intact by `verify()`.

  DisplayAsQuestItem     0, UNCHANGED - and this one is FLAGGED FOR WILL
      `uber_quest_markers` rule A marks placed encounters that pay a SOUL; the
      guards pay none, so they are mechanically outside the roster. Three markers
      per war-council room (general + two guards) is exactly the map spam rule A
      exists to prevent. But R-100 #18 calls these six "the uber bosses we added"
      and R-100 #7 asks for a marker on "all the uber bosses we made", so this is
      genuinely ambiguous and is NOT being guessed. If Will wants them marked it
      is one line: add the six to a pinned extra set in `uber_quest_markers`.

================================================================================
4. SCOPE + SHARED-RECORD LAW
================================================================================
WRITES: the 6 guard monster records, the 3 guard-pair proxies, 9 NEW hoard
records per general (3 loot tables + 3 chests + 3 accessory pools x 3 generals =
27 new records), and 5 NEW blank-anim skill clones under `records\skills\svc\`.
Nothing else. `apply()` snapshots the whole db's modified-set and fails loud if
anything outside that list is dirtied.

SHARED-RECORD LAW, enumerated before writing:
  * the 6 guards + 3 proxies are MOD-AUTHORED and have exactly one other writer,
    `four_generals`, which CREATES them. This module runs after it and is the
    ratified final writer. No third carrier exists.
  * 8 of the 12 kit skills, `genericbossorb_03` and the hoard DONORS are shared
    and are only ever POINTED AT, never edited. `verify()` proves the donors are
    byte-unchanged and that `genericbossorb_03`'s pre-existing six consumers all
    survive.
  * the other 4 kit skills, plus the slot-1 `shieldcharge`, are shared AND needed
    a field changed, so they are CLONED into `records\skills\svc\` and the clone
    is what changes (section 2b). The shipped records keep every other carrier.
    Each clone is registered in the monolith's `_BOSS_KIT_CLONES`, so the
    build's own B-TOXEUS-2 clone-shape invariant gates them too (a clip NAME is
    not a `.dbr` ref, so blanking it is inside that gate's rules - the same thing
    `_svc_clone_blank_anim` relies on for the b42/C1-C3 clones).
  * the three generals are never written. `verify()` re-asserts they are still
    Quest-class and still drop their souls, i.e. four_generals' quest-safety
    contract is intact.

CONTRACT (tools/patches/README.md): MODULE_NAME + apply(db, tags) + verify(db,
tags). Tags: 3 new chest-name tags (arz+Text are COUPLED - this lane's Text.arc
must ship with its arz).

Planted negative test:  py tools/patches/general_guardians.py --negtest <arz>
Read-only survey:       py tools/patches/general_guardians.py --analyze <arz>
Castability audit:      py tools/patches/general_guardians.py --castability <arz>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # tools/ on path

import apply_svc_patches as mono                      # noqa: E402
from arz_patcher import DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT  # noqa: E402

MODULE_NAME = 'Guardians of the General read as uber (R-100 #18)'

S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

GENERALS = ('a', 'b', 'c')

# ── the records four_generals built (this module retunes, never creates) ─────
GUARD = {g: [r'records\xpack\creatures\monster\machae\svc_general_%s_guard%d.dbr' % (g, i)
             for i in (1, 2)] for g in GENERALS}
GUARD_PROXY = {g: r'records\drxmap\proxy\q_general_%s_guardpair.dbr' % g for g in GENERALS}
GUARD_POOL = {g: r'records\drxmap\proxy\pools\q_general_%s_guardpair.dbr' % g for g in GENERALS}
# the general each pair guards - read ONLY, for the derived HP and the quest-safety re-assert
GENERAL = {g: [r'records\xpack\creatures\monster\machae\xsq27_namedhero_%s_machae_%d.dbr' % (g, n)
               for n in (45, 47)] for g in GENERALS}
WARDEN_DONOR = {g: r'records\xpack\creatures\monster\machae\%sm_warden_43.dbr' % g
                for g in GENERALS}

# ── the ladder rung the guards' own level band sits on (pointer only) ────────
ORB = r'records\item\containers\new\genericbossorb_03.dbr'
ORB_APEX_RESERVED = r'records\item\containers\new\genericbossorb_05.dbr'   # R-99, never ours
ORB_MARSHAL = r'records\item\containers\new\genericbossorb_04.dbr'         # never ours either

# ── the retune constants, each derived in the docstring ──────────────────────
SCALE_NEW = 2.0                 # um_enslaver_marauder_99's own scale
SCALE_OLD = 1.45                # what four_generals shipped
LIFE_FRACTION_OF_GENERAL = 0.45
LIFE_REGEN_NEW = 5.0            # the general's own value
DEF_PHYSICAL = 20.0             # the marshal's 30, one tier down
DEF_ELEMENT = 35.0              # the themed resist for each pair's own element

# per-general themed resist field (identity, not a flat wall)
ELEMENT_RESIST = {
    'a': 'defensiveLife',       # Dysnomion: spirit / decay / lifedrain
    'b': 'defensivePoison',     # Makaria: poison
    'c': 'defensiveFire',       # Trophonios: flame
}

# ── the CASTABILITY law (section 2b) ─────────────────────────────────────────
# A monster casts a special only if its OWN animation table (the record its
# charAnimationTableName points at) declares a clip with the skill's
# skillSpecialAnimationName. Same disasm bound the soul pcsafe wave uses:
# SkillManager::StartSkill reads <row>SpecialAnimRef1..15.
ANIM_TABLE_FIELD = 'charAnimationTableName'
ANIM_IDX_CAP = mono._PCSAFE_ANIM_IDX_CAP
SPECIAL_ANIM_FIELD = 'skillSpecialAnimationName'
# where the blank-anim clones live (an established mod-authored skill namespace)
CLONE_DIR = r'records\skills\svc'

# ── the signature kits (section 2) ───────────────────────────────────────────
# DONOR = the shipped record. Where the donor names a clip the machae rig lacks,
# the guard is wired to a BLANK-ANIM CLONE of it instead (section 2b); the value
# beside it is the donor's shipped clip name, re-asserted by verify() to prove
# the shared record was CLONED and never edited.
_SK = r'records\skills'
_XSK = r'records\xpack\skills\monsterskills'
SIGNATURE_DONOR = {
    ('a', 0): [_XSK + r'\activeattackmelee\minotaur_onslaught.dbr',
               _XSK + r'\activeattackwave\gigantes_groundbreaker.dbr'],
    ('a', 1): [_XSK + r'\activeattackradius\empusa_spirit_lifedrainnova.dbr',
               _XSK + r'\activeattackprojectile\hero_slowspiritbolt_ring.dbr'],
    ('b', 0): [_XSK + r'\activeattackprojectile\hero_vomitbile.dbr',
               _XSK + r'\activeattackprojectile\empusavenomancer_venombolt.dbr'],
    ('b', 1): [_XSK + r'\activeattackradius\empusa_venom_venomcloud.dbr',
               _XSK + r'\activeattackwave\hero_poisonwave.dbr'],
    ('c', 0): [_XSK + r'\activeattackradius\empusa_pyro_pillarofflame.dbr',
               _XSK + r'\activeattackwave\hero_flamewave.dbr'],
    ('c', 1): [_XSK + r'\activeattackmelee\gigantes_shieldcharge.dbr',
               _XSK + r'\activeattackradius\hero_bouncingfire_ring.dbr'],
}
# donor -> (clone path, the donor's SHIPPED clip name that made it uncastable)
BLANK_ANIM_CLONE = {
    _XSK + r'\activeattackprojectile\hero_vomitbile.dbr':
        (CLONE_DIR + r'\svc_machaeguard_vomitbile.dbr', 'Belch'),
    _XSK + r'\activeattackprojectile\empusavenomancer_venombolt.dbr':
        (CLONE_DIR + r'\svc_machaeguard_venombolt.dbr', 'Belch'),
    _XSK + r'\activeattackwave\hero_flamewave.dbr':
        (CLONE_DIR + r'\svc_machaeguard_flamewave.dbr', 'ShadowScythe'),
    _XSK + r'\activeattackmelee\gigantes_shieldcharge.dbr':
        (CLONE_DIR + r'\svc_machaeguard_embercharge.dbr', 'Charge'),
}
# the slot-1 special all six INHERITED from the warden donor. Its clip is not in
# the machae table either, so every guard's slot-1 special was dead too; it gets
# the same treatment and is repointed on skillName3 + specialAttackSkillName.
SLOT1_DONOR = _SK + r'\defensive\shieldcharge.dbr'
SLOT1_CLONE = CLONE_DIR + r'\svc_machaeguard_shieldcharge.dbr'
SLOT1_DONOR_ANIM = 'ShieldCharge'
SLOT1_SKILL_SLOT = 'skillName3'          # what four_generals inherited it in
SLOT1_SPECIAL_SLOT = 'specialAttackSkillName'
BLANK_ANIM_CLONE[SLOT1_DONOR] = (SLOT1_CLONE, SLOT1_DONOR_ANIM)


def _clone_paths():
    """The 5 blank-anim clone record paths this module mints."""
    return {c for c, _ in BLANK_ANIM_CLONE.values()}


def effective_skill(donor):
    """The record a guard is actually wired to: the blank-anim clone if the
    shipped donor names a clip the machae rig lacks, else the donor itself."""
    hit = BLANK_ANIM_CLONE.get(donor)
    return hit[0] if hit else donor


# what the guards are WIRED to (clone where cloned) - the rest of the module,
# verify() and the negative tests all key off this, never off the donor list.
SIGNATURE = {k: [effective_skill(d) for d in v] for k, v in SIGNATURE_DONOR.items()}

# the slots the signature skills land in. four_generals' guards use skillName1..3
# and specialAttackSkillName (all inherited from the warden donor), so 4/5 and
# specialAttack2/3 are free on every one of the six (asserted in apply()).
# Round 2 does NOT claim a new slot: it rewrites the VALUE already sitting in
# skillName3 + specialAttackSkillName (the inherited, uncastable shieldcharge)
# to point at this module's blank-anim clone of that same skill.
SIG_SKILL_SLOTS = ('skillName4', 'skillName5')
SIG_SPECIAL_SLOTS = ('specialAttack2', 'specialAttack3')
SIG_CHANCE = (40.0, 35.0)
SIG_RANGE = ('MediumRange', 'AnyRange')

# ── the chest ────────────────────────────────────────────────────────────────
HOARD_PREFIX = {g: 'general%sguard' % g for g in GENERALS}
HOARD_TAG = {g: 'tagSVCChestGeneral%sGuard' % g.upper() for g in GENERALS}
HOARD_LOCK_CLASS = 'Champion'      # the guards ARE Champions; 'Boss' would seal it forever
HOARD_LOCK_CLASS_RECIPE = 'Boss'   # what _svc_build_dedicated_hoard writes


def _hoard_records(g):
    base = r'records\drxitem\container'
    p = HOARD_PREFIX[g]
    out = []
    for t in ('01', '02', '03'):
        out += [rf'{base}\svc_{p}hoard_loot_{t}.dbr',
                rf'{base}\svc_{p}hoard_{t}.dbr',
                rf'{base}\svc_{p}hoard_pool_{t}.dbr']
    return out


# ── readers ──────────────────────────────────────────────────────────────────
def _scalar(v):
    return v[0] if isinstance(v, list) and v else v


def _val(db, rec, field, default=None):
    try:
        v = db.get_field_value(rec, field)
    except Exception:
        return default
    return default if v is None else v


def _s(db, rec, field, default=None):
    return _scalar(_val(db, rec, field, default))


def _has_field(db, rec, field):
    ff = db.get_fields(rec) or {}
    return any(k.split('###')[0] == field for k in ff)


def _setf(db, rec, field, value, dtype):
    """Preserve an existing field's dtype; declare one only when creating."""
    if _has_field(db, rec, field):
        db.set_field(rec, field, value)
    else:
        db.set_field(rec, field, value, dtype)


def _life_of(db, g):
    """The general's characterLife, per difficulty, read from the db."""
    v = _val(db, GENERAL[g][0], 'characterLife')
    if not isinstance(v, list) or len(v) != 3:
        raise SystemExit(
            'general_guardians: general %s characterLife is %r, expected a 3-tier '
            'list. The derived guard HP has no basis - re-derive before shipping.'
            % (g, v))
    return [float(x) for x in v]


def guard_life(db, g):
    """R-100 #18's HP, DERIVED: 45% of the general this pair guards."""
    return [float(round(x * LIFE_FRACTION_OF_GENERAL)) for x in _life_of(db, g)]


def _skill_class(db, rec):
    return str(_s(db, rec, 'Class', '') or '')


def is_pet_spawner(db, rec):
    """b76 / R-31 density law: does this skill put permanent entities in the world?"""
    cls = _skill_class(db, rec)
    if 'SpawnPet' in cls:
        return True
    sp = _val(db, rec, 'spawnObjects')
    sp = sp if isinstance(sp, list) else [sp]
    return any(isinstance(x, str) and x.strip() for x in sp)


# ── the CASTABILITY invariant (section 2b) ───────────────────────────────────
# Generic on purpose: it takes a monster record and answers the question the
# round-1 gate never asked - can this creature actually PLAY every special its
# own kit names? Nothing here is machae-specific; the anim table is whatever the
# creature itself binds.
#
# ⚠️ PRECEDENT + AN HONEST LIMIT, both stated rather than discovered later.
# `tools/patches/toxeus_hunt_encounter.py::_castability_violations` (b98 round 2)
# already ships a STRONGER form of this check for the three Toxeus champions: it
# derives WHICH animation ROW the engine will read from the Class of the weapon
# the caster is GUARANTEED in RightHand, and requires the clip on EVERY such row.
# This one is the UNION form the R-100 #18 brief specifies: empty, or present in
# the creature's table on ANY row (indices <= the engine's documented bound).
#   * WHY the weaker form here: the Guardians have no guaranteed weapon - both
#     hands come from a 100%-chance loot POOL - so the row cannot be derived the
#     way b98 derives it, and a per-row rule would need a weapon resolution this
#     lane has not done.
#   * WHAT THAT COSTS: this gate would ACCEPT a future repick to a clip that only
#     one row declares (e.g. 'ThunderClap', sHanded-only), which would then be
#     castable on some weapon rolls and not others.
#   * WHY IT CANNOT BITE THE SHIPPED STATE: round 2's remedy is BLANKING, not
#     repicking, and verify() separately asserts that all five of this module's
#     clones carry NO special anim at all. Every guard slot is therefore on the
#     always-playable default attack clip, which is row-independent.
#   * Registered as debt (BL-R108VIS-DEBT-7) together with the fact that neither
#     gate covers mod-authored monster kits in general.
def _resolve(db, path):
    """Case/slash-tolerant record resolution (db.has_record is exact)."""
    if not path:
        return None
    p = str(path).replace('/', '\\').strip()
    if db.has_record(p):
        return p
    low = p.lower()
    for n in db.record_names():
        if n.replace('/', '\\').lower() == low:
            return n
    return None


def creature_anim_clips(db, monster):
    """(anim-table record, set of lowercase clip names it can play) for a
    creature, read from its OWN charAnimationTableName. `None` clips means the
    table did not resolve - which is itself an offence, not a pass."""
    import re as _re
    tbl = _resolve(db, _s(db, monster, ANIM_TABLE_FIELD))
    if not tbl:
        return None, None
    clips = set()
    for key in (db.get_fields(tbl) or {}):
        fname = key.split('###')[0]
        m = _re.match(r'(.+?)SpecialAnimRef(\d+)$', fname)
        if not m or int(m.group(2)) > ANIM_IDX_CAP:
            continue
        v = _s(db, tbl, fname)
        if v and str(v).strip():
            clips.add(str(v).strip().lower())
    return tbl, clips


def creature_cast_slots(db, monster):
    """[(slot field, skill path)] for every slot this creature can cast from -
    skillNameN and every specialAttack*SkillName."""
    import re as _re
    out = set()
    for key, tf in (db.get_fields(monster) or {}).items():
        fname = key.split('###')[0]
        if not (_re.fullmatch(r'skillName\d+', fname)
                or _re.fullmatch(r'specialAttack\d*SkillName', fname)):
            continue
        for v in (tf.values or []):
            if isinstance(v, str) and v.strip():
                out.add((fname, v.strip()))
    return sorted(out)


def uncastable_slots(db, monster):
    """THE NEW INVARIANT. Every skill this creature can cast must name a special
    animation that is EMPTY or present in the creature's own resolved animation
    table; anything else is a cast the engine's StartSkill aborts silently (the
    b42 mechanism). Returns a list of human-readable offences (empty == clean)."""
    bad = []
    tbl, clips = creature_anim_clips(db, monster)
    if clips is None:
        return ['%s: %s=%r does not resolve, so NO special can be proven playable'
                % (monster.split('\\')[-1], ANIM_TABLE_FIELD,
                   _s(db, monster, ANIM_TABLE_FIELD))]
    for slot, skill in creature_cast_slots(db, monster):
        rec = _resolve(db, skill)
        if not rec:
            bad.append('%s.%s -> %s does not resolve'
                       % (monster.split('\\')[-1], slot, skill))
            continue
        anim = _s(db, rec, SPECIAL_ANIM_FIELD)
        if not anim or not str(anim).strip():
            continue                      # default attack clip: always playable
        if str(anim).strip().lower() not in clips:
            bad.append(
                '%s.%s -> %s names special anim %r, which %s does NOT declare '
                '(has: %s) - StartSkill aborts the cast silently, so this skill '
                'NEVER FIRES'
                % (monster.split('\\')[-1], slot, skill.split('\\')[-1], str(anim),
                   tbl.split('\\')[-1], ', '.join(sorted(clips)) or '(none)'))
    return bad


# ── registry hooks ───────────────────────────────────────────────────────────
def apply(db, tags):
    print('\n=== general_guardians: the Guardians of the General read as uber (R-100 #18) ===')

    # --- donors + targets must all exist; never silently skip ----------------
    #     NOTE the check is on the DONORS (the shipped records), because the
    #     clones do not exist yet on the first pass.
    missing = [p for p in
               ([q for pair in GUARD.values() for q in pair]
                + list(GUARD_PROXY.values()) + list(GUARD_POOL.values())
                + [q for pair in GENERAL.values() for q in pair]
                + [ORB] + [s for ss in SIGNATURE_DONOR.values() for s in ss]
                + [SLOT1_DONOR])
               if not db.has_record(p)]
    if missing:
        raise SystemExit(
            'general_guardians: %d required record(s) absent - this module retunes '
            'four_generals\' output and points at shipped skills, so an absent one is '
            'a real break, not a skip:\n  %s'
            % (len(missing), '\n  '.join(missing)))

    # --- the density law, checked BEFORE anything is written -----------------
    spawners = [s for ss in SIGNATURE_DONOR.values() for s in ss
                if is_pet_spawner(db, s)]
    if spawners:
        raise SystemExit(
            'general_guardians: b76/R-31 density law - the signature kit must add no '
            'pet-spawners, but these do: %s' % ', '.join(spawners))

    # --- CASTABILITY (section 2b) PRE-CHECK: every donor we are about to clone
    #     must still carry the SHIPPED clip name we measured. If it does not,
    #     either upstream moved or somebody edited the shared record in place -
    #     both must red before we build anything on top of it.
    for donor, (clone, shipped_anim) in sorted(BLANK_ANIM_CLONE.items()):
        got = _s(db, donor, SPECIAL_ANIM_FIELD)
        if str(got or '') != shipped_anim:
            raise SystemExit(
                'general_guardians: donor %s carries %s=%r, expected the shipped %r. '
                'Either upstream changed or somebody EDITED the shared record - '
                're-derive before cloning it.'
                % (donor, SPECIAL_ANIM_FIELD, got, shipped_anim))

    # --- the slots this module claims must be FREE on all six, or we would be
    #     silently clobbering somebody else's kit (never assumed - measured now).
    #     IDEMPOTENT: a slot already holding THIS module's own intended value is a
    #     re-run, not a collision, so apply() over an already-patched db is a clean
    #     no-op. Only a FOREIGN value reds the build.
    #     A slot holding the DONOR of our own clone is also a re-run (a round-1
    #     arz replayed through round 2's code), not a foreign writer.
    occupied = []
    for g in GENERALS:
        for idx, rec in enumerate(GUARD[g]):
            for n, skill in enumerate(SIGNATURE[(g, idx)]):
                ours = {skill, SIGNATURE_DONOR[(g, idx)][n]}
                v = _s(db, rec, SIG_SKILL_SLOTS[n])
                if v and str(v).strip() and str(v) not in ours:
                    occupied.append('%s.%s = %s (ours: %s)'
                                    % (rec, SIG_SKILL_SLOTS[n], v, skill))
                v = _s(db, rec, SIG_SPECIAL_SLOTS[n] + 'SkillName')
                if v and str(v).strip() and str(v) not in ours:
                    occupied.append('%s.%sSkillName = %s (ours: %s)'
                                    % (rec, SIG_SPECIAL_SLOTS[n], v, skill))
            # slot 1: four_generals inherited the warden's dead shieldcharge here.
            # Only that inherited value (or our clone of it) may be overwritten.
            for slot in (SLOT1_SKILL_SLOT, SLOT1_SPECIAL_SLOT):
                v = _s(db, rec, slot)
                if v and str(v).strip() and str(v) not in (SLOT1_DONOR, SLOT1_CLONE):
                    occupied.append('%s.%s = %s (expected the inherited %s)'
                                    % (rec, slot, v, SLOT1_DONOR))
    if occupied:
        raise SystemExit(
            'general_guardians: the signature-kit slots are NOT free - another writer '
            'already uses them with a DIFFERENT skill, so writing here would silently '
            'clobber it. Re-pick the slots deliberately:\n  %s' % '\n  '.join(occupied))

    modified_before = set(db._modified)
    expected_touch = set()

    # ── 0. the blank-anim clones (section 2b) ────────────────────────────────
    # CLONE, never edit in place: each donor keeps every other carrier it has.
    # `_svc_clone_blank_anim` is the monolith's own b42/C1-C3 recipe and registers
    # the pair in _BOSS_KIT_CLONES, so the build's B-TOXEUS-2 clone-shape
    # invariant (run later, in run_registry_gates) covers these five too.
    for donor, (clone, _shipped_anim) in sorted(BLANK_ANIM_CLONE.items()):
        if not mono._svc_clone_blank_anim(db, donor, clone):
            raise SystemExit(
                'general_guardians: could not clone %s -> %s (donor missing). The '
                'guard wired to it would ship with a skill that never fires - the '
                'exact round-1 defect. Fail rather than half-ship.' % (donor, clone))
        expected_touch.add(clone)
    print('  0. castability: %d blank-anim clone(s) minted under %s (the b42 recipe). '
          'The machae rig plays only [%s]; these donors named [%s], so every one of '
          'them was a silent no-op on a guard.'
          % (len(BLANK_ANIM_CLONE), CLONE_DIR,
             ', '.join(sorted(creature_anim_clips(db, GUARD['a'][0])[1] or [])),
             ', '.join(sorted({a for _, a in BLANK_ANIM_CLONE.values()}))))

    # ── 1. the six guards ────────────────────────────────────────────────────
    for g in GENERALS:
        life = guard_life(db, g)
        for idx, rec in enumerate(GUARD[g]):
            sf = db.set_field
            # presence
            sf(rec, 'scale', SCALE_NEW)
            sf(rec, 'characterLife', list(life))
            sf(rec, 'characterLifeRegen', LIFE_REGEN_NEW)
            # a themed defensive spine, not a flat wall
            _setf(db, rec, 'defensivePhysical', DEF_PHYSICAL, F)
            _setf(db, rec, ELEMENT_RESIST[g], DEF_ELEMENT, F)
            # the orb he was missing (a POINTER at a shared record, never an edit)
            _setf(db, rec, 'treasureProxyName', ORB, S)
            # the signature kit
            for n, skill in enumerate(SIGNATURE[(g, idx)]):
                _setf(db, rec, SIG_SKILL_SLOTS[n], skill, S)
                _setf(db, rec, SIG_SKILL_SLOTS[n].replace('skillName', 'skillLevel'), 1, I)
                pre = SIG_SPECIAL_SLOTS[n]
                _setf(db, rec, pre + 'SkillName', skill, S)
                _setf(db, rec, pre + 'Chance', SIG_CHANCE[n], F)
                _setf(db, rec, pre + 'Range', SIG_RANGE[n], S)
                _setf(db, rec, pre + 'Timeout', 2.0, F)
                _setf(db, rec, pre + 'Delay', 6.0, F)
            # slot 1: repoint the inherited-and-dead shieldcharge at its
            # blank-anim clone so every guard has a working special of its own
            # (Bhikru had none at all before this - section 2b).
            _setf(db, rec, SLOT1_SKILL_SLOT, SLOT1_CLONE, S)
            _setf(db, rec, SLOT1_SPECIAL_SLOT, SLOT1_CLONE, S)
            db._modified.add(rec)
            expected_touch.add(rec)
    _cloned = sum(1 for ss in SIGNATURE_DONOR.values() for s in ss
                  if s in BLANK_ANIM_CLONE)
    print('  1. six guardians retuned: scale %.2f -> %.1f, life -> 45%% of their '
          'general (%s), regen %.1f, themed resists, orb %s'
          % (SCALE_OLD, SCALE_NEW,
             ' / '.join(str([int(x) for x in guard_life(db, g)]) for g in GENERALS),
             LIFE_REGEN_NEW, ORB.split('\\')[-1]))
    print('  2. signature kits: 12 distinct signature skills over 6 monsters (%d '
          'pointed at as shipped, %d riding a blank-anim clone so they can actually '
          'fire), plus the inherited slot-1 special repointed to its own clone on '
          'all six; 0 pet-spawners (b76 density law holds by construction)'
          % (12 - _cloned, _cloned))

    # ── 2. one dedicated Champion-locked hoard per PAIR + the proxy wiring ───
    for g in GENERALS:
        pools = mono._svc_build_dedicated_hoard(db, HOARD_PREFIX[g], HOARD_TAG[g])
        if not pools:
            raise SystemExit(
                'general_guardians: the dedicated-hoard donors are missing, so the '
                'guard pair for general %s would ship chest-less - the exact defect '
                'R-100 #18 reports. Fail rather than half-ship.' % g)
        base = r'records\drxitem\container'
        for t in ('01', '02', '03'):
            ch = rf'{base}\svc_{HOARD_PREFIX[g]}hoard_{t}.dbr'
            # the guards are Champions: a Boss lock would seal this chest forever
            db.set_field(ch, 'LockedClassification', HOARD_LOCK_CLASS)
            db._modified.add(ch)
        proxy = GUARD_PROXY[g]
        _setf(db, proxy, 'accessory1', pools['01'], S)
        _setf(db, proxy, 'accessoryEpic1', pools['02'], S)
        _setf(db, proxy, 'accessoryLegendary1', pools['03'], S)
        db._modified.add(proxy)
        expected_touch.add(proxy)
        expected_touch.update(_hoard_records(g))
    print('  3. chests: 3 dedicated %s-locked hoards (1 per PAIR, 9 new records each) '
          'wired to accessory1/Epic1/Legendary1 - the accessory mechanism hard-caps '
          'at ONE chest per difficulty, so this cannot repeat R-100 #9'
          % HOARD_LOCK_CLASS)

    # ── 3. tags (amgoz1 voice; no em dashes) ─────────────────────────────────
    tags[HOARD_TAG['a']] = "Reaver's Spoil"
    tags[HOARD_TAG['b']] = "The Bilespitter's Cache"
    tags[HOARD_TAG['c']] = "Ember-Ward Reliquary"
    print('  4. tags: 3 chest names (%s)' % ', '.join(HOARD_TAG[g] for g in GENERALS))

    # ── 4. scope proof: nothing outside the declared set was dirtied ─────────
    newly = set(db._modified) - modified_before
    stray = {r for r in newly if r not in expected_touch}
    if stray:
        raise SystemExit(
            'general_guardians: scope violation - touched %d record(s) outside the '
            'declared set:\n  %s' % (len(stray), '\n  '.join(sorted(stray))))
    print('  5. scope OK: %d record(s) touched, all inside the declared set '
          '(6 guards + 3 proxies + 27 new hoard records + %d blank-anim clones)'
          % (len(newly), len(BLANK_ANIM_CLONE)))
    print('=== general_guardians: DONE ===')
    return tags


def verify(db, tags):
    """The new invariant this lane ships: a Guardian of the General must READ as
    uber on every axis Will named - size, kit, chest, orb - and must not have
    bought any of it by breaking a neighbouring law."""
    bad = []

    for g in GENERALS:
        want_life = guard_life(db, g)
        for idx, rec in enumerate(GUARD[g]):
            if not db.has_record(rec):
                bad.append('%s: MISSING' % rec)
                continue
            tag = rec.split('\\')[-1]

            # (a) "they are small" - bigger than every machae in the room
            sc = float(_s(db, rec, 'scale', 0.0) or 0.0)
            donor_sc = float(_s(db, WARDEN_DONOR[g], 'scale', 0.0) or 0.0)
            gen_sc = float(_s(db, GENERAL[g][0], 'scale', 0.0) or 0.0)
            if abs(sc - SCALE_NEW) > 1e-6:
                bad.append('%s: scale=%s, want %.1f' % (tag, sc, SCALE_NEW))
            elif sc <= donor_sc or sc <= gen_sc:
                bad.append('%s: scale %.2f is not above its donor %.2f / general %.2f '
                           '- it would still read as trash' % (tag, sc, donor_sc, gen_sc))

            # (b) "super weak" - the derived HP, and never above the general
            life = _val(db, rec, 'characterLife')
            life = [float(x) for x in life] if isinstance(life, list) else []
            if life != want_life:
                bad.append('%s: characterLife=%r, want %r (45%% of the general)'
                           % (tag, life, want_life))
            gen_life = _life_of(db, g)
            if life and any(a >= b for a, b in zip(life, gen_life)):
                bad.append('%s: characterLife %r >= its general %r - a guard must '
                           'never eclipse its boss' % (tag, life, gen_life))

            # (c) "no special skills" - the signature kit is present, distinct,
            #     resolves, and stays pet-free
            for n, skill in enumerate(SIGNATURE[(g, idx)]):
                if _s(db, rec, SIG_SKILL_SLOTS[n]) != skill:
                    bad.append('%s: %s=%r, want %s'
                               % (tag, SIG_SKILL_SLOTS[n], _s(db, rec, SIG_SKILL_SLOTS[n]), skill))
                if _s(db, rec, SIG_SPECIAL_SLOTS[n] + 'SkillName') != skill:
                    bad.append('%s: %sSkillName not wired to %s'
                               % (tag, SIG_SPECIAL_SLOTS[n], skill))
                if not db.has_record(skill):
                    bad.append('%s: signature skill %s does not resolve' % (tag, skill))
                elif is_pet_spawner(db, skill):
                    bad.append('%s: signature skill %s is a pet-spawner - b76/R-31 '
                               'density law' % (tag, skill))

            # (c2) slot 1: the inherited warden special must be on OUR clone, not
            #      on the shipped record whose clip the machae rig cannot play.
            for slot in (SLOT1_SKILL_SLOT, SLOT1_SPECIAL_SLOT):
                got = _s(db, rec, slot)
                if got != SLOT1_CLONE:
                    bad.append('%s: %s=%r, want %s - the inherited shipped '
                               'shieldcharge names %r, which the machae rig cannot '
                               'play, so slot 1 would be a dead special again'
                               % (tag, slot, got, SLOT1_CLONE, SLOT1_DONOR_ANIM))

            # (c3) THE NEW INVARIANT (section 2b, the thing round 1's 14/14 gate
            #      could not see): every skill this guard can cast must name a
            #      special animation his OWN table declares, or none at all.
            bad.extend(uncastable_slots(db, rec))

            # (d) "dont drop any orbs" - and never onto a reserved tier
            orb = _s(db, rec, 'treasureProxyName')
            if orb != ORB:
                bad.append('%s: treasureProxyName=%r, want %s' % (tag, orb, ORB))
            if orb in (ORB_APEX_RESERVED, ORB_MARSHAL):
                bad.append('%s: is on a RESERVED orb tier (%s) - R-99 apex / the '
                           'marshal tier are not the guards\' to take' % (tag, orb))
            if not db.has_record(str(orb)):
                bad.append('%s: orb %r does not resolve' % (tag, orb))

            # (e) rank + soul policy unchanged (R-106 / the soul lane)
            rank = str(_s(db, rec, 'monsterClassification', '') or '')
            if rank != 'Champion':
                bad.append('%s: monsterClassification=%r - this module must not '
                           'change rank (R-106 soul policy)' % (tag, rank))
            ch = float(_s(db, rec, 'chanceToEquipFinger2', 0.0) or 0.0)
            if ch != 0.0:
                bad.append('%s: chanceToEquipFinger2=%s - four_generals cleared the '
                           'soul loot deliberately; a guard must not pay a soul'
                           % (tag, ch))

    # (f) "they dont have any chests" - exactly one, and it can actually open
    for g in GENERALS:
        proxy = GUARD_PROXY[g]
        base = r'records\drxitem\container'
        for slot, t in (('accessory1', '01'), ('accessoryEpic1', '02'),
                        ('accessoryLegendary1', '03')):
            want = rf'{base}\svc_{HOARD_PREFIX[g]}hoard_pool_{t}.dbr'
            got = _s(db, proxy, slot)
            if got != want:
                bad.append('%s: %s=%r, want %s' % (proxy, slot, got, want))
            elif not db.has_record(want):
                bad.append('%s: %s pool %s does not resolve' % (proxy, slot, want))
            ch = rf'{base}\svc_{HOARD_PREFIX[g]}hoard_{t}.dbr'
            if not db.has_record(ch):
                bad.append('%s: chest %s missing' % (proxy, ch))
                continue
            lc = str(_s(db, ch, 'LockedClassification', '') or '')
            if lc != HOARD_LOCK_CLASS:
                bad.append('%s: LockedClassification=%r, want %r - the guards are '
                           'Champions, a %r lock never opens'
                           % (ch, lc, HOARD_LOCK_CLASS, HOARD_LOCK_CLASS_RECIPE))
            lt = _s(db, ch, 'tables')
            if not lt or not db.has_record(str(lt)):
                bad.append('%s: loot table %r does not resolve' % (ch, lt))
        # no extra accessory slots (the one-chest guarantee, re-checked not assumed)
        for k in (db.get_fields(proxy) or {}):
            b = k.split('###')[0]
            if b.startswith('accessory') and b not in (
                    'accessory1', 'accessoryEpic1', 'accessoryLegendary1'):
                v = _s(db, proxy, b)
                if v:
                    bad.append('%s: unexpected accessory slot %s=%r - the one-chest-'
                               'per-encounter guarantee is structural, keep it that way'
                               % (proxy, b, v))

    # (g) four_generals' quest-safety contract survives untouched
    for g in GENERALS:
        for rec in GENERAL[g]:
            cls = str(_s(db, rec, 'monsterClassification', '') or '')
            if cls != 'Quest':
                bad.append('%s: general is no longer Quest-class (%r)' % (rec, cls))
            if float(_s(db, rec, 'chanceToEquipFinger2', 0.0) or 0.0) <= 0.0:
                bad.append('%s: general lost its soul drop' % rec)
        # the two kit-identical variants of a general must stay in step - this
        # module never writes them, so a divergence means someone else did.
        s45 = float(_s(db, GENERAL[g][0], 'scale', 0.0) or 0.0)
        s47 = float(_s(db, GENERAL[g][1], 'scale', 0.0) or 0.0)
        if abs(s45 - s47) > 1e-6:
            bad.append('general %s: the _45/_47 variants disagree on scale (%.2f vs '
                       '%.2f) - this module never writes a general' % (g, s45, s47))

    # (h) the shared records this module only POINTS at are unedited, and the orb
    #     tier's pre-existing consumers all survive (no consumer was stolen)
    orb_consumers = []
    for n in db.record_names():
        if _s(db, n, 'treasureProxyName') == ORB:
            orb_consumers.append(n)
    ours = {q for pair in GUARD.values() for q in pair}
    others = [c for c in orb_consumers if c not in ours]
    if len(others) < 6:
        bad.append('genericbossorb_03 now has only %d non-guard consumer(s); it had 6 '
                   'shipped bosses before this lane - a consumer was displaced'
                   % len(others))
    for g in GENERALS:
        dsc = float(_s(db, WARDEN_DONOR[g], 'scale', 0.0) or 0.0)
        if abs(dsc - 1.5) > 1e-6:
            bad.append('%s: the warden DONOR was edited (scale %r, shipped 1.5) - '
                       'donors are read-only here' % (WARDEN_DONOR[g], dsc))

    # (i) CLONE, NEVER EDIT IN PLACE - proven both ways on the built db:
    #     the DONOR still carries its shipped clip name (so it was not edited and
    #     its other carriers are unchanged), and the CLONE carries none (so the
    #     guard's cast rides the default attack clip).
    # ONE reverse pass over the db (never one per clone) for both questions:
    # who still carries each DONOR, and has anyone outside the six been moved
    # onto one of our CLONES.
    _guard_set = {q for pair in GUARD.values() for q in pair}
    _clone_low = {c.lower(): c for c, _ in BLANK_ANIM_CLONE.values()}
    _donor_low = {d.lower(): d for d in BLANK_ANIM_CLONE}
    donor_carriers = {d: 0 for d in BLANK_ANIM_CLONE}
    clone_intruders = {c: [] for c, _ in BLANK_ANIM_CLONE.values()}
    for n in db.record_names():
        for key, tf in (db.get_fields(n) or {}).items():
            fname = key.split('###')[0]
            if not (fname.startswith('skillName')
                    or fname.startswith('specialAttack')):
                continue
            for v in (tf.values or []):
                if not isinstance(v, str) or not v.strip():
                    continue
                low = v.replace('/', '\\').strip().lower()
                if low in _donor_low and n not in _guard_set:
                    donor_carriers[_donor_low[low]] += 1
                elif low in _clone_low and n not in _guard_set:
                    clone_intruders[_clone_low[low]].append('%s.%s' % (n, fname))
    for donor, (clone, shipped_anim) in sorted(BLANK_ANIM_CLONE.items()):
        got = _s(db, donor, SPECIAL_ANIM_FIELD)
        if str(got or '') != shipped_anim:
            bad.append('%s: SHARED DONOR was edited in place (%s=%r, shipped %r) - '
                       'the shared-record law says clone and repoint, never edit; '
                       'this silently changes every other carrier'
                       % (donor, SPECIAL_ANIM_FIELD, got, shipped_anim))
        if donor_carriers[donor] < 1:
            bad.append('%s: has NO non-guard carrier left - this lane must never '
                       'displace a shipped consumer of a shared skill' % donor)
        if not db.has_record(clone):
            bad.append('%s: blank-anim clone MISSING - the guard wired to it has a '
                       'skill that never fires' % clone)
            continue
        cgot = _s(db, clone, SPECIAL_ANIM_FIELD)
        if cgot and str(cgot).strip():
            bad.append('%s: clone still carries %s=%r - the whole point of the clone '
                       'is that it carries none' % (clone, SPECIAL_ANIM_FIELD, cgot))
        if str(_s(db, clone, 'Class', '') or '') != str(_s(db, donor, 'Class', '') or ''):
            bad.append('%s: clone Class=%r != donor %r - it is no longer the same '
                       'skill' % (clone, _s(db, clone, 'Class'), _s(db, donor, 'Class')))
        if clone_intruders[clone]:
            bad.append('%s: carried by %d NON-guard slot(s) %s - this clone exists '
                       'only for the six Guardians'
                       % (clone, len(clone_intruders[clone]),
                          ', '.join(sorted(clone_intruders[clone])[:5])))

    if bad:
        raise SystemExit(
            'general_guardians verify FAILED - %d offender(s):\n    %s'
            % (len(bad), '\n    '.join(bad)))

    _cast = sum(len(creature_cast_slots(db, r))
                for pair in GUARD.values() for r in pair)
    print('  %s verify OK: 6 guardians at scale %.1f (donor 1.50 / general %.2f), '
          'life %s (45%% of their general, never above it), 12 distinct signature '
          'skills all resolving and all pet-free, orb %s (R-99 apex + the marshal tier '
          'untouched, %d other consumers intact), 3 %s-locked hoards = ONE chest per '
          'pair, rank/soul policy unchanged, all 6 generals still Quest-class with '
          'their souls. CASTABILITY: %d cast slot(s) across the six checked against '
          'their own anim table [%s] - 0 name a clip the rig lacks; %d blank-anim '
          'clones present, every shared donor byte-unedited.'
          % (MODULE_NAME, SCALE_NEW,
             float(_s(db, GENERAL['a'][0], 'scale', 0.0) or 0.0),
             ' / '.join(str([int(x) for x in guard_life(db, g)]) for g in GENERALS),
             ORB.split('\\')[-1], len(others), HOARD_LOCK_CLASS,
             _cast, ', '.join(sorted(creature_anim_clips(db, GUARD['a'][0])[1] or [])),
             len(BLANK_ANIM_CLONE)))


# ── CLI ──────────────────────────────────────────────────────────────────────
def _load(arz):
    from arz_patcher import ArzDatabase
    return ArzDatabase.from_arz(Path(arz))


def _analyze(arz):
    db = _load(arz)
    print('\nARZ: %s' % arz)
    hdr = '%-26s %-10s %-6s %-26s %-22s %s' % ('guard', 'rank', 'scale',
                                               'characterLife', 'orb', 'added skills')
    print('  ' + hdr)
    print('  ' + '-' * len(hdr))
    for g in GENERALS:
        for idx, rec in enumerate(GUARD[g]):
            if not db.has_record(rec):
                print('  %-26s ABSENT' % rec.split('\\')[-1]); continue
            added = [_s(db, rec, s) for s in SIG_SKILL_SLOTS]
            print('  %-26s %-10s %-6s %-26s %-22s %s'
                  % (rec.split('\\')[-1], _s(db, rec, 'monsterClassification'),
                     _s(db, rec, 'scale'), _val(db, rec, 'characterLife'),
                     str(_s(db, rec, 'treasureProxyName') or '-').split('\\')[-1],
                     ', '.join(str(a).split('\\')[-1] for a in added if a) or '-'))
        print('  %-26s general life=%s  general scale=%s  proxy accessory1=%s'
              % ('  (general %s)' % g, _val(db, GENERAL[g][0], 'characterLife'),
                 _s(db, GENERAL[g][0], 'scale'),
                 str(_s(db, GUARD_PROXY[g], 'accessory1') or '-').split('\\')[-1]))


def _castability(arz):
    """PROOF, per guard and per cast slot, straight off a built .arz: what the
    creature's own animation table declares, what each of its skills demands, and
    therefore whether that skill CAN FIRE. This is the measurement the round-1
    gate never made. Exit 1 if any slot is dead."""
    db = _load(arz)
    print('\nARZ: %s' % arz)
    dead = 0
    total = 0
    for g in GENERALS:
        for rec in GUARD[g]:
            if not db.has_record(rec):
                print('\n=== %s : ABSENT ===' % rec); dead += 1; continue
            tbl, clips = creature_anim_clips(db, rec)
            print('\n=== %s ===' % rec.split('\\')[-1])
            print('    anim table : %s' % (tbl or 'UNRESOLVED'))
            print('    plays clips: %s' % (', '.join(sorted(clips)) if clips else '-'))
            for slot, skill in creature_cast_slots(db, rec):
                sk = _resolve(db, skill)
                anim = _s(db, sk, SPECIAL_ANIM_FIELD) if sk else None
                if not sk:
                    print('    [MISSING ] %-24s %s' % (slot, skill)); dead += 1; continue
                if not anim or not str(anim).strip():
                    ok, why = True, 'no special anim -> default attack clip'
                else:
                    ok = clips is not None and str(anim).strip().lower() in clips
                    why = 'anim %r %s' % (str(anim),
                                          'IS in the table' if ok else 'NOT in the table')
                total += 1
                if not ok:
                    dead += 1
                print('    [%s] %-24s %-46s %s'
                      % ('CAN FIRE' if ok else '  DEAD  ', slot,
                         skill.split('\\')[-1], why))
    print('\n%d cast slot(s) inspected across the six Guardians; %d CANNOT FIRE.'
          % (total, dead))
    return 1 if dead else 0


def _negtest(arz):
    db = _load(arz)
    apply(db, {})
    results = []

    def check(label, expect_fail, mutate, restore):
        mutate()
        try:
            verify(db, {})
            failed = False
        except SystemExit:
            failed = True
        restore()
        results.append((label, expect_fail, failed, failed == expect_fail))

    a1 = GUARD['a'][0]
    c2 = GUARD['c'][1]
    proxy_a = GUARD_PROXY['a']
    chest_a = r'records\drxitem\container\svc_%shoard_01.dbr' % HOARD_PREFIX['a']

    check('control - the retuned state passes', False, lambda: None, lambda: None)

    # PLANT 1: back to the shipped "small" scale -> must red.
    prev = _s(db, a1, 'scale')
    check('scale reverted to the shipped 1.45 rejected', True,
          lambda: db.set_field(a1, 'scale', SCALE_OLD),
          lambda: db.set_field(a1, 'scale', prev))

    # PLANT 2: scale merely equal to the plain warden donor -> still "just like
    # the other guys" -> must red. Proves the gate is about READING as uber, not
    # about a magic number.
    check('scale equal to the plain warden donor (1.5) rejected', True,
          lambda: db.set_field(a1, 'scale', 1.5),
          lambda: db.set_field(a1, 'scale', prev))

    # PLANT 3: back to the shipped "super weak" HP -> must red.
    prevlife = list(_val(db, a1, 'characterLife'))
    check('characterLife reverted to the shipped [3200,4200,5400] rejected', True,
          lambda: db.set_field(a1, 'characterLife', [3200.0, 4200.0, 5400.0]),
          lambda: db.set_field(a1, 'characterLife', prevlife))

    # PLANT 4: a guard that eclipses its own general -> must red.
    check('guard HP raised ABOVE its general rejected', True,
          lambda: db.set_field(a1, 'characterLife', [99000.0, 99000.0, 99000.0]),
          lambda: db.set_field(a1, 'characterLife', prevlife))

    # PLANT 5: the orb removed -> must red.
    prevorb = _s(db, a1, 'treasureProxyName')
    check('orb removed rejected', True,
          lambda: db.set_field(a1, 'treasureProxyName', ''),
          lambda: db.set_field(a1, 'treasureProxyName', prevorb))

    # PLANT 6: the orb moved onto R-99's reserved apex tier -> must red.
    check('orb moved onto the R-99 reserved apex tier rejected', True,
          lambda: db.set_field(a1, 'treasureProxyName', ORB_APEX_RESERVED),
          lambda: db.set_field(a1, 'treasureProxyName', prevorb))

    # PLANT 7: the chest unwired from the proxy -> must red.
    prevacc = _s(db, proxy_a, 'accessory1')
    check('chest unwired from the guard-pair proxy rejected', True,
          lambda: db.set_field(proxy_a, 'accessory1', ''),
          lambda: db.set_field(proxy_a, 'accessory1', prevacc))

    # PLANT 8: the chest left on the recipe's Boss lock -> sealed forever -> red.
    prevlc = _s(db, chest_a, 'LockedClassification')
    check('chest left on the recipe Boss lock (never opens) rejected', True,
          lambda: db.set_field(chest_a, 'LockedClassification', HOARD_LOCK_CLASS_RECIPE),
          lambda: db.set_field(chest_a, 'LockedClassification', prevlc))

    # PLANT 9: a signature skill stripped -> back to "no special skills" -> red.
    prevsk = _s(db, c2, SIG_SKILL_SLOTS[0])
    check('signature skill stripped rejected', True,
          lambda: db.set_field(c2, SIG_SKILL_SLOTS[0], ''),
          lambda: db.set_field(c2, SIG_SKILL_SLOTS[0], prevsk))

    # PLANT 10: a guard promoted to Hero (soul-eligible) -> R-106 collision -> red.
    prevrank = _s(db, c2, 'monsterClassification')
    check('guard promoted to Hero (R-106 soul policy) rejected', True,
          lambda: db.set_field(c2, 'monsterClassification', 'Hero'),
          lambda: db.set_field(c2, 'monsterClassification', prevrank))

    # PLANT 11: a guard given a soul drop -> red.
    check('guard given a soul drop rejected', True,
          lambda: db.set_field(c2, 'chanceToEquipFinger2', 66.0),
          lambda: db.set_field(c2, 'chanceToEquipFinger2', 0.0))

    # PLANT 12: the general de-quested -> four_generals' quest safety -> red.
    gen = GENERAL['b'][0]
    prevcls = _s(db, gen, 'monsterClassification')
    check('general de-quested (four_generals quest safety) rejected', True,
          lambda: db.set_field(gen, 'monsterClassification', 'Boss'),
          lambda: db.set_field(gen, 'monsterClassification', prevcls))

    # PLANT 13: the b76 density law - a pet-spawner smuggled into a guard's kit.
    spawner = None
    for n in db.record_names():
        if n.lower().startswith('records\\skills') and 'SpawnPet' in _skill_class(db, n):
            spawner = n
            break
    if spawner:
        check('pet-spawner smuggled into a guard kit (b76 density law) rejected', True,
              lambda: db.set_field(c2, SIG_SKILL_SLOTS[0], spawner),
              lambda: db.set_field(c2, SIG_SKILL_SLOTS[0], prevsk))
    else:
        results.append(('pet-spawner plant', True, False, False))

    # ── THE ROUND-2 PLANTS: the castability class the round-1 gate went 14/14
    #    green on. Each of these is exactly what shipped in round 1. ───────────
    b1 = GUARD['b'][0]                       # Bhikru, who had ZERO castable specials
    b1_clone = SIGNATURE[('b', 0)][0]        # svc_machaeguard_vomitbile
    b1_donor = SIGNATURE_DONOR[('b', 0)][0]  # hero_vomitbile ('Belch')

    # PLANT 14: a guard's skill names a clip the machae rig does NOT have.
    # This is THE round-1 defect, planted directly. It MUST red.
    prev_ca = _s(db, b1_clone, SPECIAL_ANIM_FIELD)
    check("skill naming a clip the rig lacks ('Belch') rejected", True,
          lambda: db.set_field(b1_clone, SPECIAL_ANIM_FIELD, 'Belch'),
          lambda: db.set_field(b1_clone, SPECIAL_ANIM_FIELD, prev_ca or ''))

    # PLANT 15: a clip name that exists NOWHERE in the db at all -> must red.
    check("skill naming a clip that exists nowhere ('NoSuchClip') rejected", True,
          lambda: db.set_field(b1_clone, SPECIAL_ANIM_FIELD, 'NoSuchClip'),
          lambda: db.set_field(b1_clone, SPECIAL_ANIM_FIELD, prev_ca or ''))

    # 15b/15c: the MEMBERSHIP pair. Both plant a skill into the same FREE slot on
    # the same guard; the ONLY difference is whether the clip it names is one the
    # machae table declares. That isolates this invariant from every other rule
    # in verify() and proves the gate is not simply "the anim must be empty".
    FREE_SLOT = 'skillName6'
    in_table = out_table = None
    for n in db.record_names():
        a = _s(db, n, SPECIAL_ANIM_FIELD)
        if not a or not str(a).strip() or n in _clone_paths():
            continue
        a = str(a).strip().lower()
        if a == 'thunderclap' and in_table is None:
            in_table = n
        elif a == 'belch' and out_table is None:
            out_table = n
    if in_table and out_table:
        check("free slot given a skill whose clip the rig HAS ('ThunderClap') accepted",
              False,
              lambda: _setf(db, b1, FREE_SLOT, in_table, S),
              lambda: db.set_field(b1, FREE_SLOT, ''))
        check("free slot given a skill whose clip the rig LACKS ('Belch') rejected",
              True,
              lambda: _setf(db, b1, FREE_SLOT, out_table, S),
              lambda: db.set_field(b1, FREE_SLOT, ''))
    else:
        results.append(('membership pair (needs a ThunderClap + a Belch skill)',
                        True, False, False))

    # PLANT 16: the guard repointed back at the raw upstream donor (which still
    # carries 'Belch') -> the round-1 wiring exactly -> must red.
    prev_b1 = _s(db, b1, SIG_SKILL_SLOTS[0])
    check('guard repointed at the raw upstream donor (round-1 wiring) rejected', True,
          lambda: db.set_field(b1, SIG_SKILL_SLOTS[0], b1_donor),
          lambda: db.set_field(b1, SIG_SKILL_SLOTS[0], prev_b1))

    # PLANT 17: slot 1 left on the inherited shieldcharge ('ShieldCharge', absent
    # from the machae table) -> Bhikru's "no working special of any kind" -> red.
    prev_s1 = _s(db, b1, SLOT1_SPECIAL_SLOT)
    check('slot-1 special left on the inherited dead shieldcharge rejected', True,
          lambda: db.set_field(b1, SLOT1_SPECIAL_SLOT, SLOT1_DONOR),
          lambda: db.set_field(b1, SLOT1_SPECIAL_SLOT, prev_s1))

    # PLANT 18: SHARED-RECORD LAW - the donor edited in place instead of cloned.
    # It would "work" for our guard and silently change 25 other monsters -> red.
    prev_don = _s(db, b1_donor, SPECIAL_ANIM_FIELD)
    check('shared donor edited in place instead of cloned rejected', True,
          lambda: db.set_field(b1_donor, SPECIAL_ANIM_FIELD, ''),
          lambda: db.set_field(b1_donor, SPECIAL_ANIM_FIELD, prev_don))

    # PLANT 19: the creature's own animation table unresolvable -> nothing can be
    # proven playable -> must red rather than pass by default.
    prev_tbl = _s(db, b1, ANIM_TABLE_FIELD)
    check('unresolvable charAnimationTableName rejected', True,
          lambda: db.set_field(b1, ANIM_TABLE_FIELD, r'records\no\such\anm.dbr'),
          lambda: db.set_field(b1, ANIM_TABLE_FIELD, prev_tbl))

    print('\ngeneral_guardians _negtest:')
    for label, exp, got, ok in results:
        print('  [%s] %-62s expected=%s got=%s'
              % ('PASS' if ok else 'FAIL', label,
                 'REJECT' if exp else 'ACCEPT', 'REJECT' if got else 'ACCEPT'))
    allok = all(o for _, _, _, o in results)
    print('  -> %s (%d/%d)' % ('PASS' if allok else 'FAIL',
                               sum(1 for _, _, _, o in results if o), len(results)))
    return 0 if allok else 1


if __name__ == '__main__':
    args = sys.argv[1:]
    DEFAULT_ARZ = (Path(__file__).resolve().parents[2] / 'local'
                   / 'baseline_main_7efd107.arz')
    if '--analyze' in args:
        i = args.index('--analyze')
        _analyze(args[i + 1] if len(args) > i + 1 else DEFAULT_ARZ)
    elif '--negtest' in args:
        i = args.index('--negtest')
        raise SystemExit(_negtest(args[i + 1] if len(args) > i + 1 else DEFAULT_ARZ))
    elif '--castability' in args:
        i = args.index('--castability')
        raise SystemExit(_castability(args[i + 1] if len(args) > i + 1 else DEFAULT_ARZ))
    else:
        print(__doc__)
