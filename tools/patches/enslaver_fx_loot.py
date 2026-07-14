"""build40 registry module -- ENSLAVER FX + LOOT (Will 2026-07-13).

Will (2026-07-13, pink-circled screenshot of "Toxeus the Murderer, Enslaver of Souls"
+ his summoned demons):
  (a) the demons he SUMMONS are GREEN -> make them BLACK,
  (b) the Enslaver himself has green AND black smoke -> make it ALL black,
  (c) give the Enslaver really GOOD ITEMS, tiered N/E/L,
  (d) give the summoned demons GOOD WEAPONS too.

Registry contract (tools/patches/README.md): expose MODULE_NAME + apply(db, tags),
operating on the SAME db/tags the monolith (apply_svc_patches._create_enslaver) already
built. The registry runs this AFTER the monolith, so um_toxeus_enslaver_99 (boss),
um_enslaver_marauder_99 (his HOSTILE summoned marauder), svc_enslaver_summonmarauders,
and svc_enslaver_darksmoke_charfxpak (b38's dark-smoke CharFxPak) already exist.

=========================== FX RCA (docs/reports/b40_enslaver_fx_loot.md) ===========================
Root cause, proven from baseline_build38.arz + the shipped Resources (texture colour-sampled):

  BOSS (um_toxeus_enslaver_99): a charcoal skeleton on RevenantPoison.msh. That mesh is
    StandardSkinned (NO glow shader) with the charcoal skin overriding the diffuse, so the
    boss BODY is black - not green. b38 added a dark-smoke shroud on charFxPakRunningNames,
    but RunningNames renders ONLY WHILE MOVING; when the boss stands still there is no shroud.
    The green Will sees on/around the boss is (1) the ever-present swarm of GREEN marauders he
    summons at 70% + (2) any idle gap the running-gated smoke leaves. FIX: give the boss the
    Devourer's PROVEN persistent-aura pattern - an auto-cast Skill_BuffSelfToggled whose
    charFxPakSelfNames renders the dark smoke ALWAYS (idle + moving). (The Devourer, on the
    SAME rig, reads crimson precisely because its envenom buff's charFxPakSelfNames aura is
    always on.) charFxPakSelfNames is ZERO-precedent on Monster records (0/51007) -> we do NOT
    put it on the monster; we use the skill-buff route the base game + Devourer use.

  MARAUDER (um_enslaver_marauder_99): a ShadowStalker.msh demon. TWO CONFIRMED green sources
    (DXT endpoints sampled from the shipped .tex):
      1. charFxPakRunningNames = drxshadowcloakrunning_fx_pak -> a lightning/bolt energy trail
         whose lightning_missile01b.tex has PURE-GREEN texels (8,252,0). FIX: replace it with
         the dark-smoke CharFxPak (kills the green weapon-energy trail; black while running).
      2. ShadowStalker.msh's glow map ShadowStalker01Glow.tex has BRIGHT green-cyan emissive
         spots (0,184,176). An emissive glow shows THROUGH smoke, so masking alone will not fully
         kill it. FIX: override baseTexture to SV 0.98i's own dark, non-green shadowstalker skin
         `wahr` (base 17,11,54 + paired wahrglow blue-purple, greenest +4 -> NOT green). The mod's
         Endless Hunt already recolours this exact mesh via baseTexture (shadowstalker_iceheart),
         so baseTexture-driven recolour is the established mod pattern. LAUNCH-GATED (§colour): the
         exact rendered marauder colour needs Will's in-game read; fallback = a one-line baseTexture
         revert. Also give the marauder the SAME persistent dark-smoke aura (belt-and-suspenders).

  PRESERVED: the Devourer (um_bloodtoxeus_99) crimson is a SEPARATE record and is UNTOUCHED
    (TOXEUS LORE LAW). The friendly pet-of-pet marauders (player's soul summon, Pet.tpl, built by
    the monolith BEFORE this module) are OUT of scope + carry Pet.tpl crash risk -> documented
    follow-up, not touched here.

=========================== LOOT (c/d) ===========================
  BOSS: already drops the apex boss-orb chest (treasureProxyName genericbossorb_04) + its soul
    (Finger2 @66%) + potions/relics/amulet (lootMisc1-3). Will wants a GUARANTEED signature good
    item. Following the mod's boss-loot pattern (per-tier FixedWeight table wired to a free lootMisc
    slot, pointing at mastertable POOLS so the engine rolls a proper affixed unique at kill-time -
    NOT a hand-placed fixed item that "bakes badly"): a per-tier `svc_enslaver_hoard_{n,e,l}` unique
    hoard (weapon + jewelry + armour unique pools) wired to the boss's FREE lootMisc4 @ 100%.

  MARAUDER: already equips dyn_1h/unique_1h mastertables but the unique weight is a token 4/5004
    (~0.08%). Will wants GOOD WEAPONS. Bump the unique-1h proportion so most marauders wield a
    unique. They are a Monster (NOT a Pet) -> normal equip fields are crash-safe (the Pet.tpl
    equipment-copy crash law does not apply). dropItems stays 0 (a transient summon must never drop
    loot -> infinite-summon exploit); "good weapons" = they WIELD good weapons.

ENGINE/CRASH LAWS honoured: no clone_record on a soul (the aura buff is a SKILL clone, not a soul);
no explicit dtype on cloned-record VALUE overrides (INT/FLOAT trap) - only STRING fields carry an
explicit S; charFxPak lives on MONSTER records + on a Skill_BuffSelfToggled (the base envenom class),
NEVER on the SpawnPet skill (svc_enslaver_summonmarauders is untouched); no Monster.tpl->Pet.tpl
equipment copy; new loot tables via _ensure_record; no em dashes.
"""

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import apply_svc_patches as asp
from arz_patcher import DATA_TYPE_STRING as S, DATA_TYPE_FLOAT as F, DATA_TYPE_INT as I

MODULE_NAME = 'enslaver_fx_loot'

# ── Monolith-built records (all DB-verified present in baseline_build38.arz) ──
_BOSS = asp._EN_BOSS                 # um_toxeus_enslaver_99 (charcoal skeleton, RevenantPoison rig)
_MARAUDER = asp._EN_MARAUDER         # um_enslaver_marauder_99 (his HOSTILE summoned ShadowStalker demon)
_DARKSMOKE_PAK = asp._EN_DARKSMOKE_FXPAK   # svc_enslaver_darksmoke_charfxpak -> 343_dark_smoke (b38)
_AURA_DONOR = asp._BT_SK_ENVENOM     # bloodtoxeus_envenomweapon: pure-FX Skill_BuffSelfToggled
                                     # (all offensive/defensive stats 0, no weaponEnchantment; the
                                     # Devourer's PROVEN persistent-aura shell)

# ── NEW records ──
_DARK_AURA = r'records\skills\monster skills\buff_self\svc_enslaver_darkaura.dbr'
# SV 0.98i shadowstalker skin: dark blue-purple (base 17,11,54 / wahrglow 19,2,57), NOT green.
# Resolves in the shipped SVTextures.arc (A9-verified). First path component = archive name.
_MARAUDER_SKIN = r'SVTextures\creatures\shadowstalker\wahr.tex'
_HOARD = {t: rf'records\item\loottables\svc\svc_enslaver_hoard_{t}.dbr' for t in 'nel'}

# ── Per-tier unique mastertable POOLS for the hoard (engine rolls an affixed unique at kill-time).
#    All DB-verified present per tier (dry-run resolve gate below fails loud on any miss). ──
def _hoard_members(t):
    return [
        rf'records\xpack\item\loottables\weapons\mastertables\unique_1h_{t}01.dbr',   # his blade
        rf'records\item\loottables\amulet\mastertables\unique\amulet_{t}01.dbr',       # amulet
        rf'records\item\loottables\finger\mastertables\unique\finger_{t}01.dbr',       # ring
        rf'records\item\loottables\torso\mastertables\unique\torsoall_{t}01.dbr',      # torso
        rf'records\item\loottables\head\mastertables\uniques\headall_{t}01.dbr',       # head (note: 'uniques')
        rf'records\item\loottables\arms\mastertables\unique\armall_{t}01.dbr',         # arms
        rf'records\item\loottables\legs\mastertables\unique\legsall_{t}01.dbr',        # legs
    ]


# =============================================================================
# helpers
# =============================================================================
def _real(db, path):
    if hasattr(asp, '_resolve_record'):
        r = asp._resolve_record(db, path)
        if r is not None:
            return r
    return path if db.has_record(path) else None


def _next_skill_slot(db, rec, hi=30):
    """Return (last-used skillName index)+1 so the aura APPENDS after the record's existing
    kit - never gap-filling (some records inherit gaps, e.g. the marauder's 6/7/8; appending
    keeps the existing skills contiguous and untouched)."""
    last = 0
    for i in range(1, hi + 1):
        v = db.get_field_value(rec, f'skillName{i}')
        filled = not (v is None
                      or (isinstance(v, list) and (not v or str(v[0]).strip() == ''))
                      or (isinstance(v, str) and v.strip() == ''))
        if filled:
            last = i
    return last + 1 if last + 1 <= hi else None


# =============================================================================
# FX: kill the green (boss + summoned marauder) -> all black
# =============================================================================
def _create_dark_aura(db):
    """Clone the Devourer's pure-FX toggled buff and repoint its persistent self-aura to the
    dark-smoke CharFxPak. This is the ALWAYS-ON (idle + moving) black shroud that the b38
    running-gated charFxPakRunningNames could not provide. Shared by boss + marauder."""
    donor = _real(db, _AURA_DONOR)
    if donor is None:
        raise SystemExit(f"[enslaver_fx_loot] FX: aura donor missing ({_AURA_DONOR})")
    if _real(db, _DARKSMOKE_PAK) is None:
        raise SystemExit(f"[enslaver_fx_loot] FX: dark-smoke CharFxPak missing ({_DARKSMOKE_PAK})")
    db.clone_record(donor, _DARK_AURA)
    # charFxPakSelfNames EXISTS on the donor as STRING -> value-only override (no INT/FLOAT dtype).
    db.set_field(_DARK_AURA, 'charFxPakSelfNames', _DARKSMOKE_PAK, S)
    db._modified.add(_DARK_AURA)
    # Register in the monolith's clone-shape gate (B-TOXEUS-2): full clone_record adds NO field +
    # the one changed ref resolves, so the invariant proves this clone is loader-safe.
    if hasattr(asp, '_BOSS_KIT_CLONES') and \
            not any(c == _DARK_AURA for _d, c in asp._BOSS_KIT_CLONES):
        asp._BOSS_KIT_CLONES.append((_AURA_DONOR, _DARK_AURA))


def _fix_enslaver_fx(db):
    _create_dark_aura(db)

    # ── BOSS: persistent dark-smoke aura (auto-cast) + keep b38 running smoke. Body already
    #    black (no-glow RevenantPoison + charcoal skin). ──
    B = _real(db, _BOSS)
    if B is None:
        raise SystemExit(f"[enslaver_fx_loot] FX: boss missing ({_BOSS})")
    db.set_field(B, 'initialSkillName', _DARK_AURA, S)   # auto-toggle the black aura on spawn
    slot = _next_skill_slot(db, B)
    if slot is None:
        raise SystemExit("[enslaver_fx_loot] FX: no free boss skill slot for the aura")
    db.set_field(B, f'skillName{slot}', _DARK_AURA, S)   # monster must "have" the initial skill
    db.set_field(B, f'skillLevel{slot}', 1, I)
    db._modified.add(B)

    # ── MARAUDER: (1) replace the GREEN shadowcloak running FX with dark smoke, (2) recolour the
    #    green mesh glow via a dark, non-green SV shadowstalker skin, (3) persistent dark aura. ──
    M = _real(db, _MARAUDER)
    if M is None:
        raise SystemExit(f"[enslaver_fx_loot] FX: marauder missing ({_MARAUDER})")
    db.set_field(M, 'charFxPakRunningNames', [_DARKSMOKE_PAK], S)   # green lightning trail -> black smoke
    db.set_field(M, 'baseTexture', _MARAUDER_SKIN, S)               # green glow -> dark non-green skin
    db.set_field(M, 'initialSkillName', _DARK_AURA, S)
    mslot = _next_skill_slot(db, M)
    if mslot is None:
        raise SystemExit("[enslaver_fx_loot] FX: no free marauder skill slot for the aura")
    db.set_field(M, f'skillName{mslot}', _DARK_AURA, S)
    db.set_field(M, f'skillLevel{mslot}', 1, I)
    db._modified.add(M)
    print(f"  [FX] dark aura (persistent charFxPakSelfNames=343_dark_smoke) auto-cast on boss "
          f"(skill{slot}) + marauder (skill{mslot}); marauder green shadowcloak->dark smoke, "
          f"skin->wahr (dark non-green). Devourer crimson untouched.")


# =============================================================================
# LOOT (c): guaranteed tiered unique hoard on the boss
# =============================================================================
def _fixedweight(db, path, members, desc):
    """The mod's boss-loot FixedWeight-table idiom (mirrors _create_crimsonverdict_loot):
    _ensure_record (NOT clone) so explicit dtypes are correct + safe."""
    asp._ensure_record(db, path, 'Database\\Templates\\LootItemTable_FixedWeight.tpl')
    db._record_types[path] = 'LootItemTable_FixedWeight'
    db.set_field(path, 'Class', 'LootItemTable_FixedWeight', S)
    db.set_field(path, 'templateName', 'Database\\Templates\\LootItemTable_FixedWeight.tpl', S)
    db.set_field(path, 'FileDescription', desc, S)
    db.set_field(path, 'brokenRandomizerChance', 0.0, F)
    db.set_field(path, 'prefixRandomizerChance', 0.0, F)
    db.set_field(path, 'suffixRandomizerChance', 0.0, F)
    for i, m in enumerate(members, start=1):
        db.set_field(path, f'lootName{i}', m, S)
        db.set_field(path, f'lootWeight{i}', 100, I)
    db._modified.add(path)


def _add_enslaver_loot(db):
    B = _real(db, _BOSS)
    if B is None:
        raise SystemExit(f"[enslaver_fx_loot] LOOT: boss missing ({_BOSS})")
    # build the 3 per-tier hoard tables (fail loud if a unique pool does not resolve).
    for t in 'nel':
        members = _hoard_members(t)
        missing = [m for m in members if _real(db, m) is None]
        if missing:
            raise SystemExit("[enslaver_fx_loot] LOOT: unique pool(s) missing for tier "
                             f"{t.upper()}: {missing}")
        _fixedweight(db, _HOARD[t], members,
                     f"Enslaver hoard - guaranteed unique ({t.upper()})")
    # wire to the boss's FREE lootMisc4 @ 100% (a guaranteed good unique per kill).
    if db.get_field_value(B, 'lootMisc4Item1') not in (None, '', 0):
        raise SystemExit("[enslaver_fx_loot] LOOT: boss lootMisc4 is NOT free")
    db.set_field(B, 'lootMisc4Item1', [_HOARD['n'], _HOARD['e'], _HOARD['l']], S)  # NEW field -> STRING
    db.set_field(B, 'chanceToEquipMisc4', 100.0)          # NEW field -> FLOAT (guaranteed)
    db.set_field(B, 'chanceToEquipMisc4Item1', 100)       # NEW field -> INT (only member)
    db.set_field(B, 'dropItems', 1)                       # already 1; explicit
    db._modified.add(B)
    print("  [LOOT] Enslaver hoard: 3 per-tier FixedWeight unique tables (weapon+jewelry+armour "
          "pools) -> boss lootMisc4 @ 100% guaranteed, on top of the boss-orb chest + soul.")


# =============================================================================
# LOOT (d): arm the summoned marauders with GOOD weapons
# =============================================================================
def _arm_marauders(db):
    """Bump the hostile marauder's equipped-weapon quality: the token unique weight (4 vs
    dyn 5000 ~= 0.08%) becomes a solid share so most marauders wield a unique 1H. Monster
    record -> normal equip fields (the Pet.tpl crash law does not apply). dropItems stays 0
    (a transient summon must never drop loot)."""
    M = _real(db, _MARAUDER)
    if M is None:
        raise SystemExit(f"[enslaver_fx_loot] MARAUDER-WPN: marauder missing ({_MARAUDER})")
    # slot 1 = dyn_1h, slot 5 = unique_1h (DB-verified on the record). Rebalance the CHOICE
    # weights only (the pool paths are already tiered [n,e,l] mastertables -> good + scaling).
    if db.get_field_value(M, 'lootRightHandItem5') in (None, '', 0):
        raise SystemExit("[enslaver_fx_loot] MARAUDER-WPN: unique-1h slot (Item5) missing")
    db.set_field(M, 'chanceToEquipRightHandItem1', 2500)   # dyn 1H  (~50%)
    db.set_field(M, 'chanceToEquipRightHandItem5', 2500)   # unique 1H (~50%: good weapons)
    db._modified.add(M)
    print("  [MARAUDER-WPN] unique-1h wield share 0.08% -> ~50% (good weapons); dropItems stays 0.")


# =============================================================================
# verify (post-finalization): prove the fix + honour the crash laws
# =============================================================================
def _gv1(db, rec, f):
    v = db.get_field_value(rec, f)
    return v[0] if isinstance(v, list) else v


def verify(db, tags=None):
    problems = []
    B = _real(db, _BOSS)
    M = _real(db, _MARAUDER)
    A = _real(db, _DARK_AURA)

    # ---- FX ----
    if A is None:
        problems.append("dark-aura skill missing")
    else:
        if str(_gv1(db, A, 'charFxPakSelfNames')).replace('/', '\\').lower() \
                != _DARKSMOKE_PAK.replace('/', '\\').lower():
            problems.append("dark aura charFxPakSelfNames not the dark-smoke pak")
        # CRASH LAW: the aura must be a buff-self skill, NEVER a SpawnPet class.
        cls = str(db.get_field_value(A, 'Class') or db._record_types.get(A, ''))
        if 'spawnpet' in cls.lower():
            problems.append(f"dark aura is a SpawnPet class ({cls}) - crash-law violation")
    for lbl, rec in (('boss', B), ('marauder', M)):
        if rec is None:
            problems.append(f"{lbl} record missing")
            continue
        if str(_gv1(db, rec, 'initialSkillName')).replace('/', '\\').lower() \
                != _DARK_AURA.replace('/', '\\').lower():
            problems.append(f"{lbl} initialSkillName is not the dark aura")
        kit = [str(_gv1(db, rec, f'skillName{i}') or '').replace('/', '\\').lower()
               for i in range(1, 31)]
        if _DARK_AURA.replace('/', '\\').lower() not in kit:
            problems.append(f"{lbl} kit does not carry the dark aura skill")
    # marauder: green shadowcloak replaced + dark skin + no green-producing FX field remains
    if M is not None:
        run = _gv1(db, M, 'charFxPakRunningNames')
        if str(run).replace('/', '\\').lower() != _DARKSMOKE_PAK.replace('/', '\\').lower():
            problems.append(f"marauder charFxPakRunningNames still {run} (green shadowcloak not replaced)")
        if 'shadowcloak' in str(run).lower():
            problems.append("marauder still references the green shadowcloak FX")
        if str(_gv1(db, M, 'baseTexture')).replace('/', '\\').lower() \
                != _MARAUDER_SKIN.replace('/', '\\').lower():
            problems.append("marauder baseTexture not the dark wahr skin")
    # CRASH LAW: the SpawnPet skill must carry NO charFxPak field
    SP = _real(db, asp._EN_SUMMON_MARAUDERS) if hasattr(asp, '_EN_SUMMON_MARAUDERS') else None
    if SP is not None:
        ff = db.get_fields(SP) or {}
        if any(k.split('###')[0].lower().startswith('charfxpak') for k in ff):
            problems.append("svc_enslaver_summonmarauders (SpawnPet) carries a charFxPak - crash-law violation")
    # PRESERVE: Devourer crimson untouched
    DV = _real(db, r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr')
    if DV is not None:
        if str(_gv1(db, DV, 'baseTexture')).lower().find('crimson') < 0:
            problems.append("Devourer baseTexture no longer crimson (should be untouched)")

    # ---- LOOT ----
    for t in 'nel':
        HP = _real(db, _HOARD[t])
        if HP is None:
            problems.append(f"hoard table {t} missing")
            continue
        members = [_gv1(db, HP, f'lootName{i}') for i in range(1, 20)]
        members = [m for m in members if m and str(m).strip()]
        if not members:
            problems.append(f"hoard {t} empty")
        for m in members:
            if _real(db, m) is None:
                problems.append(f"hoard {t} member unresolved: {m}")
    if B is not None:
        if float(_gv1(db, B, 'chanceToEquipMisc4') or 0) != 100.0:
            problems.append("boss lootMisc4 not @100%")
        lm = db.get_field_value(B, 'lootMisc4Item1')
        lm = lm if isinstance(lm, list) else [lm]
        if [str(x).replace('/', '\\').lower() for x in lm] != \
                [_HOARD[t].replace('/', '\\').lower() for t in 'nel']:
            problems.append(f"boss lootMisc4Item1 not the 3 hoard tables: {lm}")
        # marauder good weapons
        if M is not None:
            w1 = int(_gv1(db, M, 'chanceToEquipRightHandItem1') or 0)
            w5 = int(_gv1(db, M, 'chanceToEquipRightHandItem5') or 0)
            if w5 < w1 or w5 < 1000:
                problems.append(f"marauder unique-weapon weight too low (Item1={w1}, Item5={w5})")
            if int(_gv1(db, M, 'dropItems') or 0) != 0:
                problems.append("marauder dropItems != 0 (summon loot exploit)")

    if problems:
        for p in problems[:30]:
            print(f"  ENSLAVER-FX-LOOT OFFENDER: {p}")
        raise SystemExit(f"enslaver_fx_loot verify FAILED: {len(problems)} problem(s)")
    print("  [enslaver_fx_loot] verify PASS: boss+marauder all-black (persistent dark aura; "
          "marauder green shadowcloak->smoke + wahr skin), crash laws honoured (aura is a buff-self "
          "skill, SpawnPet carries no charFxPak, no Pet equip copy), Devourer crimson preserved; "
          "tiered unique hoard @100% + good marauder weapons.")


def apply(db, tags):
    print("\n=== [enslaver_fx_loot] build40 ENSLAVER FX + LOOT (Will 2026-07-13) ===")
    _fix_enslaver_fx(db)     # a + b: all black
    _add_enslaver_loot(db)   # c: tiered good items
    _arm_marauders(db)       # d: good demon weapons
    print("=== [enslaver_fx_loot] done (verify() runs post-finalization) ===\n")
    return tags
