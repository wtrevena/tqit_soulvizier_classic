"""tools/patches/damage_display.py - restore AE floating combat-text font styles.

RCA (docs/reports/b38_damage_display_rca.md): SoulVizier 0.98i ships a pre-
Anniversary xpack gameengine.dbr that predates the TQAE floating-damage-number
FontStyle pointer fields. Our build inherits that record verbatim
(build_svc_database.py loads SV 0.98i as its base db; no tool patches
gameengine), so records\\xpack\\game\\gameengine.dbr - the record the TQAE
engine reads for combat-text styles - is MISSING these seven fields that base
TQAE has:

    DamageNormalStyle, DamageElementalStyle, DamageOnPlayerStyle,
    DamageOverTimeStyle, HealingStyle, HealingOnPlayerStyle, PlayerImpairmentStyle

With no FontStyle bound, the engine renders no floating number for those damage
categories -> the Steam report "the damage display is not working". The
CriticalHit*Style fields DID survive in SV's record, so critical-hit numbers
still show - that split (crits show, normal/elemental/DoT numbers do not) is the
diagnostic signature of this defect.

FIX: bind the seven missing style fields to the base-game FontStyle records. Our
arz does not ship those FontStyle records (records\\ui\\fontstyles\\damage*.dbr,
healing*.dbr, playerimpairment.dbr), so they resolve from the base
database.arz - this adds only seven string fields to one record and creates no
new records. This is a UI-defect fix on a base-game record (the ho-ui F5
precedent); it touches NO SoulVizier design field (camera, loot, combat
equations, drop rates, etc. are all left exactly as SV set them).

MINIMALITY PROOF: scratchpad replay_damage_display.py replays this module
against a copy of baseline_build36.arz and asserts ONLY
records\\xpack\\game\\gameengine.dbr is in db._modified, and ONLY these seven
fields were added (every other field byte-identical).

CONTRACT (tools/patches/README.md): MODULE_NAME + apply(db, tags), operating on
the SAME db the monolith built; the fail-loud gates run LAST over everything.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # tools/ on path

MODULE_NAME = 'Damage display font-styles (AE floating combat text)'

# The record the TQAE (Immortal-Throne-based) engine reads for combat-text
# styles. Proven authoritative: base TQAE keeps the Damage*Style fields ONLY in
# the xpack gameengine (the non-xpack records\game\gameengine.dbr lacks them),
# yet vanilla TQAE shows damage numbers -> the engine reads the xpack record.
GAMEENGINE = r'records\xpack\game\gameengine.dbr'

# field -> base-game FontStyle record. Values are lowercase to match this
# record's existing style-field convention (its CriticalHit*Style, ItemBanner,
# SkillName, ... refs are all lowercase). Path resolution is case-insensitive
# and every target FontStyle lives in the base database.arz.
STYLE_FIELDS = {
    'DamageNormalStyle':     r'records\ui\fontstyles\damagenormal.dbr',
    'DamageElementalStyle':  r'records\ui\fontstyles\damageelemental.dbr',
    'DamageOnPlayerStyle':   r'records\ui\fontstyles\damageonplayer.dbr',
    'DamageOverTimeStyle':   r'records\ui\fontstyles\damageovertime.dbr',
    'HealingStyle':          r'records\ui\fontstyles\healing.dbr',
    'HealingOnPlayerStyle':  r'records\ui\fontstyles\healingonplayer.dbr',
    'PlayerImpairmentStyle': r'records\ui\fontstyles\playerimpairment.dbr',
}


def apply(db, tags):
    if not db.has_record(GAMEENGINE):
        raise SystemExit(
            "damage_display: %s absent from db - cannot restore combat-text "
            "styles (build base changed?)" % GAMEENGINE)

    added = []
    for field, value in STYLE_FIELDS.items():
        cur = db.get_field_value(GAMEENGINE, field)
        if cur:
            # Already bound (base already complete, or a prior module set it):
            # do not clobber an existing binding.
            continue
        # New string field: let set_field infer DATA_TYPE_STRING (dtype 2), the
        # same type every existing style-pointer field on this record uses.
        # Do NOT pass an explicit dtype (cloned-record INT/FLOAT-corruption law).
        db.set_field(GAMEENGINE, field, value)
        added.append(field)

    print("    damage_display: bound %d combat-text style field(s): %s"
          % (len(added), ", ".join(added) if added else "(none - already complete)"))


def verify(db, tags):
    """Post-finalization coherency guard: every combat-text style field is bound
    on the live xpack gameengine. Fail-loud if a later phase dropped one."""
    missing = [f for f in STYLE_FIELDS if not db.get_field_value(GAMEENGINE, f)]
    if missing:
        raise SystemExit(
            "damage_display verify: xpack gameengine still missing combat-text "
            "style field(s): %s" % ", ".join(missing))
