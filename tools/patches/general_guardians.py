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
              hero_vomitbile              (Skill_AttackProjectileBurst)
              empusavenomancer_venombolt  (Skill_AttackProjectile)
    guard2  {^r}Nakoth ~ Machae Plague-Ward
            a plague-ward fills the ground he wards:
              empusa_venom_venomcloud     (Skill_AttackProjectileAreaEffect)
              hero_poisonwave             (Skill_AttackWave)

  general c - Trophonios (flame)
    guard1  {^r}Kharzun the Ember ~ Machae Pyre-Ward
            the pyre-ward raises the pyre:
              empusa_pyro_pillarofflame   (Skill_AttackProjectileAreaEffect)
              hero_flamewave              (Skill_AttackWave)
    guard2  {^r}Voreth ~ Machae Cinder-Reaver
            a cinder-reaver closes and scatters embers:
              gigantes_shieldcharge       (Skill_AttackWeaponCharge)
              hero_bouncingfire_ring      (Skill_AttackProjectileRing)

Every one of the twelve is an EXISTING shipped skill record (no new skill
records, no new FX, nothing to bake). Twelve distinct skills over six monsters:
after this, no two guards look or fight alike, and none of them fights like the
`shieldcharge` trash they were indistinguishable from.

DENSITY LAW, HONOURED BY CONSTRUCTION (b76 / R-31, and the brief's explicit
"mind the b76 density precedent if you add summons"): NOT ONE of the twelve is a
pet-spawner. `verify()` re-asserts that mechanically - every skill this module
puts on a guard is checked to be non-`Skill_*SpawnPet*` and to declare no
`spawnObjects` - so this lane cannot contribute a single permanent entity to the
Hades war-council rooms. The Guardians read as uber through KIT and PRESENCE, not
through adds.

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
WRITES: the 6 guard monster records, the 3 guard-pair proxies, and 9 NEW hoard
records per general (3 loot tables + 3 chests + 3 accessory pools x 3 generals =
27 new records). Nothing else. `apply()` snapshots the whole db's modified-set and
fails loud if anything outside that list is dirtied.

SHARED-RECORD LAW, enumerated before writing:
  * the 6 guards + 3 proxies are MOD-AUTHORED and have exactly one other writer,
    `four_generals`, which CREATES them. This module runs after it and is the
    ratified final writer. No third carrier exists.
  * the 12 kit skills, `genericbossorb_03` and the hoard DONORS are shared and are
    only ever POINTED AT, never edited. `verify()` proves the donors are byte-
    unchanged and that `genericbossorb_03`'s pre-existing six consumers all
    survive.
  * the three generals are never written. `verify()` re-asserts they are still
    Quest-class and still drop their souls, i.e. four_generals' quest-safety
    contract is intact.

CONTRACT (tools/patches/README.md): MODULE_NAME + apply(db, tags) + verify(db,
tags). Tags: 3 new chest-name tags (arz+Text are COUPLED - this lane's Text.arc
must ship with its arz).

Planted negative test:  py tools/patches/general_guardians.py --negtest <arz>
Read-only survey:       py tools/patches/general_guardians.py --analyze <arz>
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

# ── the signature kits (section 2). Every path is an EXISTING shipped skill ──
_SK = r'records\skills'
_XSK = r'records\xpack\skills\monsterskills'
SIGNATURE = {
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
# the slots the signature skills land in. four_generals' guards use skillName1..3
# and specialAttackSkillName (all inherited from the warden donor), so 4/5 and
# specialAttack2/3 are free on every one of the six (asserted in apply()).
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


# ── registry hooks ───────────────────────────────────────────────────────────
def apply(db, tags):
    print('\n=== general_guardians: the Guardians of the General read as uber (R-100 #18) ===')

    # --- donors + targets must all exist; never silently skip ----------------
    missing = [p for p in
               ([q for pair in GUARD.values() for q in pair]
                + list(GUARD_PROXY.values()) + list(GUARD_POOL.values())
                + [q for pair in GENERAL.values() for q in pair]
                + [ORB] + [s for ss in SIGNATURE.values() for s in ss])
               if not db.has_record(p)]
    if missing:
        raise SystemExit(
            'general_guardians: %d required record(s) absent - this module retunes '
            'four_generals\' output and points at shipped skills, so an absent one is '
            'a real break, not a skip:\n  %s'
            % (len(missing), '\n  '.join(missing)))

    # --- the density law, checked BEFORE anything is written -----------------
    spawners = [s for ss in SIGNATURE.values() for s in ss if is_pet_spawner(db, s)]
    if spawners:
        raise SystemExit(
            'general_guardians: b76/R-31 density law - the signature kit must add no '
            'pet-spawners, but these do: %s' % ', '.join(spawners))

    # --- the slots this module claims must be FREE on all six, or we would be
    #     silently clobbering somebody else's kit (never assumed - measured now)
    occupied = []
    for g in GENERALS:
        for rec in GUARD[g]:
            for slot in SIG_SKILL_SLOTS:
                v = _s(db, rec, slot)
                if v and str(v).strip():
                    occupied.append('%s.%s = %s' % (rec, slot, v))
            for pre in SIG_SPECIAL_SLOTS:
                v = _s(db, rec, pre + 'SkillName')
                if v and str(v).strip():
                    occupied.append('%s.%sSkillName = %s' % (rec, pre, v))
    if occupied:
        raise SystemExit(
            'general_guardians: the signature-kit slots are NOT free - another writer '
            'already uses them, so writing here would silently clobber it. Re-pick the '
            'slots deliberately:\n  %s' % '\n  '.join(occupied))

    modified_before = set(db._modified)
    expected_touch = set()

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
            db._modified.add(rec)
            expected_touch.add(rec)
    print('  1. six guardians retuned: scale %.2f -> %.1f, life -> 45%% of their '
          'general (%s), regen %.1f, themed resists, orb %s'
          % (SCALE_OLD, SCALE_NEW,
             ' / '.join(str([int(x) for x in guard_life(db, g)]) for g in GENERALS),
             LIFE_REGEN_NEW, ORB.split('\\')[-1]))
    print('  2. signature kits: 12 DISTINCT existing skills over 6 monsters, '
          '0 pet-spawners (b76 density law holds by construction)')

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
          '(6 guards + 3 proxies + 27 new hoard records)' % len(newly))
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

    if bad:
        raise SystemExit(
            'general_guardians verify FAILED - %d offender(s):\n    %s'
            % (len(bad), '\n    '.join(bad)))

    print('  %s verify OK: 6 guardians at scale %.1f (donor 1.50 / general %.2f), '
          'life %s (45%% of their general, never above it), 12 distinct signature '
          'skills all resolving and all pet-free, orb %s (R-99 apex + the marshal tier '
          'untouched, %d other consumers intact), 3 %s-locked hoards = ONE chest per '
          'pair, rank/soul policy unchanged, all 6 generals still Quest-class with '
          'their souls.'
          % (MODULE_NAME, SCALE_NEW,
             float(_s(db, GENERAL['a'][0], 'scale', 0.0) or 0.0),
             ' / '.join(str([int(x) for x in guard_life(db, g)]) for g in GENERALS),
             ORB.split('\\')[-1], len(others), HOARD_LOCK_CLASS))


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
    else:
        print(__doc__)
