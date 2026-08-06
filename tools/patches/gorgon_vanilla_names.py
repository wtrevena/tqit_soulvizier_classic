r"""gorgon_vanilla_names - PR-4 (Steam player Flozer44, 2026-07-28, reached Knossos):
the two Gorgon spellcasters show their vanilla names SWAPPED - the player saw
"Impious"/"Geomancy Adept" (his paraphrase) on the wrong monsters.

Will's decision (2026-08-06): RESTORE THE FULL VANILLA NAMES, un-swapped.

--------------------------------------------------------------------------------
GROUND TRUTH - MEASURED FROM THE BYTES
--------------------------------------------------------------------------------
The two gorgon-caster archetypes, identified by each creature's OWN skill kit
(never guessed):

  ar_pyromancer_13/16  kit = BlazingWeapons + PillarofFlame          -> FIRE
  ar_venomancer_13/16  kit = Arachnos_VenomBolt + Arachne PoisonCloud -> POISON

BASE TQAE (stock Titan Quest) database.arz assigns:
  FIRE  ar_pyromancer_13/16 -> description = tagMonsterName1263
  POISON ar_venomancer_13/16 -> description = tagMonsterName1256

BASE TQAE Text_EN.arc (and SV 0.98i's Text_EN, byte-for-byte the same strings):
  tagMonsterName1263 = "Gorgon ~ Geomancer"
  tagMonsterName1256 = "Gorgon ~ Profaner"

So in stock Titan Quest the FIRE caster is "Gorgon ~ Geomancer" and the POISON
caster is "Gorgon ~ Profaner". (The literals "Impious"/"Geomancy Adept" appear in
NO text source - they are the player's paraphrase of "Profaner"/"Geomancer".)

Soulvizier 0.98i (which our merge carries VERBATIM) FLIPPED the record->tag
pointers relative to base - it did NOT change the strings:
  FIRE  ar_pyromancer_13/16 -> tagMonsterName1256 ("Gorgon ~ Profaner")   [SWAPPED]
  POISON ar_venomancer_13/16 -> tagMonsterName1263 ("Gorgon ~ Geomancer") [SWAPPED]

That flip is exactly what the player saw: the fire caster and the poison caster
wear each other's vanilla title.

--------------------------------------------------------------------------------
THE FIX - the smallest correct change: repoint the descriptionTag
--------------------------------------------------------------------------------
The two vanilla strings already exist and resolve correctly (they are base-game
tags, present in base Text_EN.arc AND our built Text.arc). Nothing about the TEXT
is wrong - only which record points at which tag. So the minimal, un-swapping fix
is to repoint the `description` field on the 4 records back to the base-game
assignment:

  ar_pyromancer_13/16 : description 1256 -> 1263  ("Gorgon ~ Geomancer")
  ar_venomancer_13/16 : description 1263 -> 1256  ("Gorgon ~ Profaner")

We do NOT edit the text the tags resolve to (that would move the misnomer, not fix
the swap, and would clobber the shared base string on any other carrier). We do NOT
mint new tags (no new player-visible surface). This restores the exact stock-TQ
display names on the correct creatures.

SHARED-RECORD LAW: in the built merged DB the two tags 1256/1263 are carried by
EXACTLY these 4 gorgon-caster records and nothing else (the XPack4 chaos gorgons
use the DISTINCT tags x4tagMonsterName1256Chaos/1263Chaos). verify() re-asserts
that the union of carriers is exactly our 4 targets, so a future merge that added a
5th carrier of either tag would fail the build loudly rather than ship a half-fix.

The fix is bound to each creature's IDENTITY, not its filename: apply() and
verify() both re-check the kit signature (BlazingWeapons for fire, Arachnos_
VenomBolt for poison) before/after touching the name, so a record whose kit no
longer matches its archetype can never be silently mis-named.

IN-GAME CONFIRMATION: a display-name change is provable from the rebuilt Text.arc
read-back (done in this lane); the only launch-gated part is a player eyeballing
the two monsters near Knossos - the orchestrator owns deploys.
"""
import os
import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))   # tools/ on path

MODULE_NAME = "PR-4: restore vanilla gorgon caster names (un-swap)"

# Base-TQAE-correct name tags (proven from base database.arz record->tag mapping).
FIRE_TAG = 'tagMonsterName1263'    # "Gorgon ~ Geomancer" (on the fire pyromancer in base TQ)
POISON_TAG = 'tagMonsterName1256'  # "Gorgon ~ Profaner"  (on the poison venomancer in base TQ)

# record -> (archetype, base-correct description tag, kit-signature substring that
# BINDS the name to the creature's own identity). skillName1 must contain the
# signature (lowercased) or the record is not the archetype we think it is.
TARGETS = {
    r'records\creature\monster\gorgon\ar_pyromancer_13.dbr': ('FIRE', FIRE_TAG, 'blazingweapons'),
    r'records\creature\monster\gorgon\ar_pyromancer_16.dbr': ('FIRE', FIRE_TAG, 'blazingweapons'),
    r'records\creature\monster\gorgon\ar_venomancer_13.dbr': ('POISON', POISON_TAG, 'arachnos_venombolt'),
    r'records\creature\monster\gorgon\ar_venomancer_16.dbr': ('POISON', POISON_TAG, 'arachnos_venombolt'),
}

# The full set of name tags this fix touches (for the shared-record union check).
GORGON_CASTER_TAGS = frozenset({FIRE_TAG, POISON_TAG})


def _norm(p):
    return str(p).replace('/', '\\').lower()


def _gv1(db, rec, field):
    v = db.get_field_value(rec, field)
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _kit_ok(db, rec, sig):
    """True iff the record's skillName1 identifies it as the expected archetype."""
    s1 = _norm(_gv1(db, rec, 'skillName1') or '')
    return sig in s1


def apply(db, tags):
    print("\n=== [gorgon_vanilla_names] PR-4: restore the vanilla gorgon caster names (un-swap) ===")
    changed = 0
    for rec, (arch, want_tag, sig) in TARGETS.items():
        if not db.has_record(rec):
            raise SystemExit(
                "gorgon_vanilla_names: target record MISSING: %s "
                "(the merge no longer ships it?) - refusing to no-op silently" % rec)
        # bind the name to the creature's OWN kit before renaming it
        if not _kit_ok(db, rec, sig):
            raise SystemExit(
                "gorgon_vanilla_names: %s is not the expected %s archetype "
                "(skillName1=%r lacks %r) - refusing to (re)name a record whose "
                "identity does not match." % (rec, arch, _gv1(db, rec, 'skillName1'), sig))
        cur = _gv1(db, rec, 'description')
        if cur == want_tag:
            print("    %-22s (%-6s) description already = %s (no write)"
                  % (rec.rsplit('\\', 1)[-1], arch, want_tag))
            continue
        db.set_field(rec, 'description', want_tag)
        db._modified.add(rec)
        changed += 1
        print("    %-22s (%-6s) description: %s -> %s"
              % (rec.rsplit('\\', 1)[-1], arch, cur, want_tag))
    print("=== [gorgon_vanilla_names] %d record(s) un-swapped; verify() runs "
          "post-finalization ===\n" % changed)
    return tags


def verify(db, tags=None):
    problems = []

    # 1. each target carries the base-correct tag AND still matches its archetype kit.
    for rec, (arch, want_tag, sig) in TARGETS.items():
        if not db.has_record(rec):
            problems.append("target record MISSING at verify: %s" % rec)
            continue
        got = _gv1(db, rec, 'description')
        if got != want_tag:
            problems.append(
                "%s (%s caster) carries description=%r, expected %s (the vanilla "
                "name for this archetype)." % (rec, arch, got, want_tag))
        if not _kit_ok(db, rec, sig):
            problems.append(
                "%s no longer matches the %s kit signature %r (skillName1=%r) - the "
                "name is no longer bound to the creature's identity."
                % (rec, arch, sig, _gv1(db, rec, 'skillName1')))

    # 2. SHARED-RECORD LAW: the two gorgon-caster tags are carried by EXACTLY our 4
    #    targets in the whole merged DB. A 5th carrier means the merge introduced a
    #    creature that also wears one of these names - our repoint would then be a
    #    half-fix. Fail loud so it is investigated, not shipped.
    carriers = {t: [] for t in GORGON_CASTER_TAGS}
    for n in db.record_names():
        d = _gv1(db, n, 'description')
        if d in carriers:
            carriers[d].append(_norm(n))
    all_carriers = set(carriers[FIRE_TAG]) | set(carriers[POISON_TAG])
    expected = {_norm(r) for r in TARGETS}
    unexpected = sorted(all_carriers - expected)
    if unexpected:
        problems.append(
            "SHARED-RECORD LAW: tags %s are also carried by non-target record(s): %s "
            "- the un-swap would be incomplete." % (sorted(GORGON_CASTER_TAGS), unexpected))
    missing = sorted(expected - all_carriers)
    if missing:
        problems.append(
            "target record(s) no longer carry either gorgon-caster tag: %s" % missing)

    if problems:
        for p in problems:
            print("  GORGON-NAME OFFENDER: %s" % p)
        raise SystemExit("gorgon_vanilla_names.verify FAILED: %d problem(s)" % len(problems))

    print("  [gorgon_vanilla_names].verify OK: fire pyromancer -> %s (Gorgon ~ Geomancer), "
          "poison venomancer -> %s (Gorgon ~ Profaner); both tags carried by exactly the "
          "4 target records." % (FIRE_TAG, POISON_TAG))
    return tags


# ────────────────────────────────────────────────────────────────────────────
# PLANTED NEGATIVES  (py tools/patches/gorgon_vanilla_names.py --negtest)
# ────────────────────────────────────────────────────────────────────────────
def _negtest():
    from collections import OrderedDict

    class _TF(object):
        def __init__(self, v):
            self.values = list(v) if isinstance(v, list) else [v]

    class _Stub(object):
        def __init__(self):
            self.d = {}
            self._modified = set()

        def has_record(self, n):
            return n in self.d

        def record_names(self):
            return list(self.d)

        def get_field_value(self, n, f):
            rec = self.d.get(n)
            if rec is None:
                return None
            return rec.get(f)

        def set_field(self, n, f, v, dt=None):
            self.d.setdefault(n, {})[f] = v if isinstance(v, list) else [v]

        def get_fields(self, n):
            rec = self.d.get(n)
            if rec is None:
                return None
            return OrderedDict((k, _TF(v)) for k, v in rec.items())

    def _base():
        # the SV-SWAPPED pre-state, exactly as the merge ships it
        db = _Stub()
        db.d[r'records\creature\monster\gorgon\ar_pyromancer_13.dbr'] = {
            'description': ['tagMonsterName1256'],
            'skillName1': [r'Records\Skills\Monster Skills\Buff_Other\BlazingWeapons.dbr']}
        db.d[r'records\creature\monster\gorgon\ar_pyromancer_16.dbr'] = {
            'description': ['tagMonsterName1256'],
            'skillName1': [r'Records\Skills\Monster Skills\Buff_Other\BlazingWeapons.dbr']}
        db.d[r'records\creature\monster\gorgon\ar_venomancer_13.dbr'] = {
            'description': ['tagMonsterName1263'],
            'skillName1': [r'Records\Skills\Monster Skills\Attack_Projectile\Arachnos_VenomBolt.dbr']}
        db.d[r'records\creature\monster\gorgon\ar_venomancer_16.dbr'] = {
            'description': ['tagMonsterName1263'],
            'skillName1': [r'Records\Skills\Monster Skills\Attack_Projectile\Arachnos_VenomBolt.dbr']}
        return db

    # clean apply -> verify must PASS
    db = _base()
    apply(db, {})
    try:
        verify(db)
    except SystemExit as e:
        print("NEGTEST SETUP FAIL: clean apply+verify should PASS but raised: %s" % e)
        return 1

    plants = [
        ('fire caster left with the SWAPPED (poison) name',
         lambda db: db.d[r'records\creature\monster\gorgon\ar_pyromancer_13.dbr']
             .__setitem__('description', ['tagMonsterName1256'])),
        ('poison caster left with the SWAPPED (fire) name',
         lambda db: db.d[r'records\creature\monster\gorgon\ar_venomancer_16.dbr']
             .__setitem__('description', ['tagMonsterName1263'])),
        ('a fifth (non-target) creature also wears a gorgon-caster tag',
         lambda db: db.d.__setitem__(r'records\creature\monster\gorgon\intruder_99.dbr',
             {'description': ['tagMonsterName1263'], 'skillName1': ['x']})),
        ('a target record disappears entirely',
         lambda db: db.d.pop(r'records\creature\monster\gorgon\ar_venomancer_13.dbr')),
        ('a target loses its archetype kit (name no longer bound to identity)',
         lambda db: db.d[r'records\creature\monster\gorgon\ar_pyromancer_16.dbr']
             .__setitem__('skillName1', ['records\\skills\\nothing.dbr'])),
    ]
    bad = 0
    for label, plant in plants:
        db = _base()
        apply(db, {})
        plant(db)
        try:
            verify(db)
        except SystemExit:
            print("  negtest OK  (caught): %s" % label)
            continue
        print("  negtest FAIL (missed): %s" % label)
        bad += 1
    print("negtest: %d/%d plants caught" % (len(plants) - bad, len(plants)))
    return 1 if bad else 0


if __name__ == '__main__':
    import sys
    if '--negtest' in sys.argv:
        sys.exit(_negtest())
    print("gorgon_vanilla_names: fire pyromancer -> %s, poison venomancer -> %s"
          % (FIRE_TAG, POISON_TAG))
    sys.exit(0)
