r"""black_poison - THE DEVOURER'S BLACK POISON (Will ruled 2026-07-16, R-1).

WILL VERBATIM (2026-07-16): "we have wanted the devourer to have a literal black
poison asset from the beginning and use that all along ... that is how we were going
to replace the green poison effect that he had was make a black one and wire it in".

WHAT THIS SHIPS
--------------------------------------------------------------------------------
A NEW envenom-lineage weapon-poison skill `svc_black_poison` (BLACK, not green, not
crimson), wired onto the DEVOURER's whole poison surface, replacing the crimson
`bloodtoxeus_envenomweapon` he currently carries:
  * um_bloodtoxeus_99 (the FOUGHT Devourer)  : initialSkillName + skillName3
  * bloodtoxeus_1..3  (the SOUL-SUMMON pets) : skillName3
The EoAT pet's poison (buffSelfSkillName) is repointed to svc_black_poison by the
toxeus_endofallthings module (its _BLACK_POISON const now names this record).

His BLOOD/crimson IDENTITY is UNTOUCHED (per Will: "only the POISON goes black"):
newskeleton_crimson skin, melinoe_bloodboil nova, the leinth blood aura on his
monster record - all stay. Only the weapon-poison buff goes black.

THE EMPIRICAL TINT MODEL (proven against the golden build45 arz, md5 917d9047)
--------------------------------------------------------------------------------
`skillWeaponTint{Red,Green,Blue}` are ADDITIVE EMISSIVE glow multipliers on the
weapon mesh. Proven from the whole DB (394 tinted weapon buffs, local/tint_scan.py):
  - (0,0,0) is the inert "NO TINT" default (195 records) -> a zero channel is OFF,
    not black. So BLACK LIGHT IS UNREACHABLE via the tint channel (you cannot emit
    black; zero = no glow, the weapon's natural look).
  - Pure-channel markers: base green envenom (0.25,1.0,0.25); the Devourer's crimson
    bloodtoxeus_envenomweapon (1.0,0.25,0.25); frost strike (0.0,0.3,0.8); storm
    strike (0.4,0.0,0.8); necrevive (0.0,1.0,0.0).
  - The DARKEST RENDERABLE non-zero tint in the entire DB is (0.1,0.1,0.1), shipped
    on `hero_shadowenchantmentbuff` - a real, in-engine SHADOW ENCHANTMENT. This is
    the near-black "shadow" register the engine actually draws.

HOW BLACK IS ACHIEVED (two layers, load-bearing black is grounded)
--------------------------------------------------------------------------------
1. LOAD-BEARING: weapon tint = (0.1,0.1,0.1). This is a DIRECT engine emissive
   parameter (NOT a baked .pfx), identical to the shipped hero_shadowenchantmentbuff
   shadow enchant, so it DEFINITIVELY renders a dark/charcoal glow - never green,
   never crimson. This alone removes the green Will complained about. Black light is
   unreachable (additive channels), so (0.1,0.1,0.1) is the empirical darkest black.
2. PARTICLE: charFxPakSelfNames = svc_black_poison_charfxpak, a new weapon char-fx
   pak that mirrors the green weapon-poison pak's structure (particle attached to
   'R Hand' + 'L Hand') but swaps the green 343_Weapon_PoisonFX for 343_dark_smoke
   (SVEffects/ambient/dark_smoke.pfx) - the WILL_DECISIONS-sanctioned "proven dark
   smoke" already worn by the confirmed-dark Enslaver ENCOUNTER rig
   (svc_enslaver_darksmoke_charfxpak). This is the "black poison dripping from the
   weapon" layer. ** PLAYER-SURFACE FLAG (rule 3, the 343_dark_smoke renders-green
   caution): the PARTICLE's final black-vs-green render is a Will in-game color check.
   The tint-black above does NOT depend on it; if the smoke reads green in-game the
   fix is a one-line pak swap (or clearing charFxPakSelfNames -> tint-only black) and
   the load-bearing black still stands. **

PAYLOAD (poison/vitality, matching the Devourer's tier): cloned from his own crimson
bloodtoxeus_envenomweapon (his lineage, his-tier poison), so it keeps his poison
(offensiveSlowPoisonMin=90 / 5s) + slow, and ADDS a black vitality-decay DoT
(offensiveSlowLifeMin) so it reads "black poison" = venom + life-rot.

GATE COMPLIANCE (the enslaver_pet_fx b55 green-marker gate): the green marker for
buffSelfSkillName is the substring 'envenom' (excluded only for 'bloodtoxeus'). This
record is named `svc_black_poison` (NO 'envenom' substring), so it is transparently
clear of the green marker - never flagged, never stripped.

No em dashes anywhere. All refs resolve (run the resolves gate).
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # tools/
import apply_svc_patches as asp  # noqa: F401 (shared idioms / index parity)

MODULE_NAME = 'black_poison'

# ── the new black poison skill + its weapon char-fx pak ──────────────────────
BLACK_POISON = r'records\skills\monster skills\buff_self\svc_black_poison.dbr'
BLACK_POISON_PAK = r'records\skills\monster skills\buff_self\svc_black_poison_charfxpak.dbr'

# ── donors (DB-verified present in build45) ──────────────────────────────────
_CRIMSON = r'records\skills\monster skills\buff_self\bloodtoxeus_envenomweapon.dbr'  # his crimson lineage
_GREEN_WEAPON_PAK = r'records\effects\weaponenchantments\343_weapon_poisoncharfxpak.dbr'  # structure donor
_DARK_SMOKE = r'records\effects\custom\343_dark_smoke.dbr'  # the proven dark smoke EffectEntity

# ── the Devourer poison surface to rewire (crimson -> black) ─────────────────
_DEVOURER_MON = r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr'
_DEVOURER_PETS = [r'records\skills\soulskills\pets\bloodtoxeus_%d.dbr' % i for i in (1, 2, 3)]

# ── the black tint (empirical darkest renderable; hero_shadowenchantmentbuff) ─
_TINT_BLACK = 0.10000000149011612  # exact float the shadow-enchant ships

# ── vitality-decay DoT added on top of the inherited poison (Devourer tier) ──
_VIT_DECAY_MIN = 60.0
_VIT_DECAY_DURATION = 5.0


def _has(db, p):
    return db.has_record(p)


def _build_black_poison_pak(db):
    """New weapon char-fx pak: the green weapon-poison pak's R/L-Hand attach
    structure, particle swapped green->343_dark_smoke (black smoke drip)."""
    if not _has(db, _GREEN_WEAPON_PAK):
        raise SystemExit("[black_poison] weapon-pak donor missing: %s" % _GREEN_WEAPON_PAK)
    if not _has(db, _DARK_SMOKE):
        raise SystemExit("[black_poison] dark-smoke FX missing: %s" % _DARK_SMOKE)
    db.clone_record(_GREEN_WEAPON_PAK, BLACK_POISON_PAK)
    # keep particleEffectAttachPoints (['R Hand','L Hand']); swap both particles
    # to the dark smoke (value-only override preserves the STRING-list dtype).
    ap = db.get_field_value(BLACK_POISON_PAK, 'particleEffectAttachPoints')
    n = len(ap) if isinstance(ap, list) else 1
    db.set_field(BLACK_POISON_PAK, 'particleEffectNames', [_DARK_SMOKE] * max(n, 2))
    db._modified.add(BLACK_POISON_PAK)


def _build_black_poison(db):
    """svc_black_poison: clone the Devourer's crimson envenom (his lineage + his-tier
    poison payload), then go BLACK (dark tint + dark-smoke pak) and add a vitality
    decay DoT. Value-only overrides preserve donor dtypes."""
    if not _has(db, _CRIMSON):
        raise SystemExit("[black_poison] crimson donor missing: %s" % _CRIMSON)
    db.clone_record(_CRIMSON, BLACK_POISON)
    # 1. LOAD-BEARING BLACK: dark near-black weapon tint (shadow-enchant register).
    db.set_field(BLACK_POISON, 'skillWeaponTintRed', _TINT_BLACK)
    db.set_field(BLACK_POISON, 'skillWeaponTintGreen', _TINT_BLACK)
    db.set_field(BLACK_POISON, 'skillWeaponTintBlue', _TINT_BLACK)
    # 2. PARTICLE: swap the crimson leinth blood aura -> black smoke weapon drip.
    db.set_field(BLACK_POISON, 'charFxPakSelfNames', BLACK_POISON_PAK)
    # 3. PAYLOAD: keep the inherited poison + slow; add a black vitality-decay DoT.
    db.set_field(BLACK_POISON, 'offensiveSlowLifeMin', _VIT_DECAY_MIN)
    db.set_field(BLACK_POISON, 'offensiveSlowLifeDurationMin', _VIT_DECAY_DURATION)
    db._modified.add(BLACK_POISON)


def _rewire_devourer(db):
    """Repoint every crimson-envenom reference in the Devourer family to the black
    poison. The fought monster (initialSkillName + skillName3) + his 3 soul pets
    (skillName3). Only the crimson buff ref is touched; his kit/identity is intact."""
    def _repoint(rec, field):
        v = db.get_field_value(rec, field)
        v0 = (v[0] if isinstance(v, list) else v) or ''
        if str(v0).replace('/', '\\').lower() == _CRIMSON.lower():
            db.set_field(rec, field, BLACK_POISON)   # value-only -> preserves STRING dtype
            return True
        return False

    touched = []
    if not _has(db, _DEVOURER_MON):
        raise SystemExit("[black_poison] Devourer monster missing: %s" % _DEVOURER_MON)
    for f in ('initialSkillName', 'skillName3'):
        if _repoint(_DEVOURER_MON, f):
            touched.append('%s.%s' % (_DEVOURER_MON.rsplit(chr(92), 1)[-1], f))
    for pet in _DEVOURER_PETS:
        if not _has(db, pet):
            raise SystemExit("[black_poison] Devourer pet missing: %s" % pet)
        if _repoint(pet, 'skillName3'):
            touched.append('%s.skillName3' % pet.rsplit(chr(92), 1)[-1])
    if len(touched) < 5:
        raise SystemExit("[black_poison] expected 5 crimson->black rewires, got %d: %r"
                         % (len(touched), touched))
    return touched


def apply(db, tags):
    print("\n=== [black_poison] THE DEVOURER'S BLACK POISON (Will R-1) ===")
    for r in (BLACK_POISON, BLACK_POISON_PAK):
        if _has(db, r):
            raise SystemExit("[black_poison] collision (record already exists): %s" % r)
    _build_black_poison_pak(db)
    _build_black_poison(db)
    touched = _rewire_devourer(db)
    print("  [black_poison] built svc_black_poison (tint %.2f black + dark-smoke pak, "
          "poison+vitality); rewired %d Devourer crimson->black refs: %s"
          % (_TINT_BLACK, len(touched), ', '.join(touched)))
    return tags


def _gv1(db, rec, f):
    v = db.get_field_value(rec, f)
    return v[0] if isinstance(v, list) else v


def verify(db, tags=None):
    """POST-FINALIZATION fail-loud gate. Assert the black poison is BLACK (no green
    tint / no green particle) and the whole Devourer poison surface points at it."""
    P = []
    for r in (BLACK_POISON, BLACK_POISON_PAK):
        if not db.has_record(r):
            raise SystemExit('black_poison.verify FAILED (missing): %s' % r)
    # (a) tint is the dark near-black register on every channel (NOT green, NOT crimson)
    for ch in ('Red', 'Green', 'Blue'):
        t = float(_gv1(db, BLACK_POISON, 'skillWeaponTint%s' % ch) or 0.0)
        if t > 0.2:
            P.append('tint %s=%.3f not dark (>0.2): black poison would glow bright' % (ch, t))
    g = float(_gv1(db, BLACK_POISON, 'skillWeaponTintGreen') or 0.0)
    r = float(_gv1(db, BLACK_POISON, 'skillWeaponTintRed') or 0.0)
    if g >= 0.9:
        P.append('GREEN tint survived (skillWeaponTintGreen=%.2f) - the exact bug' % g)
    if r >= 0.9:
        P.append('CRIMSON tint survived (skillWeaponTintRed=%.2f)' % r)
    # (b) particle is the dark smoke, not the green weapon-poison FX
    pak = (_gv1(db, BLACK_POISON, 'charFxPakSelfNames') or '').replace('/', '\\').lower()
    if pak != BLACK_POISON_PAK.lower():
        P.append('charFxPakSelfNames != svc_black_poison_charfxpak (%r)' % pak)
    parts = db.get_field_value(BLACK_POISON_PAK, 'particleEffectNames')
    parts = [str(x).replace('/', '\\').lower() for x in (parts if isinstance(parts, list) else [parts] if parts else [])]
    if not parts or any('343_dark_smoke' not in p for p in parts):
        P.append('black-poison pak particle is not the dark smoke: %r' % parts)
    if any('poisonfx' in p or '343_weapon_poison' in p for p in parts):
        P.append('GREEN weapon-poison particle survived in the pak: %r' % parts)
    # (c) name carries no 'envenom' substring (green-marker safety)
    if 'envenom' in BLACK_POISON.lower():
        P.append('record name contains "envenom" - trips the b55 green marker')
    # (d) payload: poison retained + vitality decay added
    if float(_gv1(db, BLACK_POISON, 'offensiveSlowPoisonMin') or 0) <= 0:
        P.append('poison payload lost (offensiveSlowPoisonMin<=0)')
    if float(_gv1(db, BLACK_POISON, 'offensiveSlowLifeMin') or 0) <= 0:
        P.append('vitality-decay payload missing (offensiveSlowLifeMin<=0)')
    # (e) the WHOLE Devourer poison surface is black (no crimson envenom left on it)
    surface = [(_DEVOURER_MON, 'initialSkillName'), (_DEVOURER_MON, 'skillName3')]
    surface += [(p, 'skillName3') for p in _DEVOURER_PETS]
    for rec, fld in surface:
        v = (_gv1(db, rec, fld) or '').replace('/', '\\').lower()
        if v != BLACK_POISON.lower():
            P.append('%s.%s not black poison: %r' % (rec.rsplit(chr(92), 1)[-1], fld, v))
        if 'bloodtoxeus_envenomweapon' in v:
            P.append('%s.%s still crimson envenom' % (rec.rsplit(chr(92), 1)[-1], fld))
    if P:
        raise SystemExit('black_poison.verify FAILED:\n  ' + '\n  '.join(P))
    print('  black_poison.verify OK: svc_black_poison is BLACK (dark tint %.2f, dark-smoke '
          'weapon pak, poison+vitality); Devourer fought-monster (initial+skillName3) + 3 '
          'soul pets all repointed crimson->black; zero green/crimson tint survives.'
          % _TINT_BLACK)
    return tags
