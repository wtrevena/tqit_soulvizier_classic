r"""tools/patches/thrown_wielders.py - arm identity-appropriate enemies with
thrown (RangedOneHand) weapons so players SEE enemies throw (registry module).

WHY (audit -> docs/reports/b58_thrown_wielders.md): thrown weapons are a
Ragnarok/Atlantis/EE item class (Class = WeaponHunting_RangedOneHand, 191 recs,
all xpack2/3/4). VERIFIED ground truth: of 74 monsters that wield a thrown
weapon, ZERO are base Act1-Hades and ZERO are SV/mod - every one is a DLC or
zz_dev monster, and none spawn in the reachable SV-classic campaign (the sole
"campaign-namespace" vector, a greekbandit-slinger proxy in Greece PineForest05,
is a level-37 Ragnarok Act-5 Corinthia overlay our campaign never reaches). So
Will's "no enemies use the throwing items" is CONFIRMED, and to close the gap we
arm a small, identity-fit, rig-proven roster.

FLAGGED FOR WILL'S VETO (b58 report is the veto artifact). NOT registered in
REGISTRY yet - it rides the NEXT integration build after Will approves the roster
(Part C of the report) and the coupled MAP lane places the pool's proxy. Keeping
it out of REGISTRY leaves the golden build byte-identical for every other lane.

DONOR PATTERN (b58 Part B): a monster throws iff it (1) equips a RangedOneHand
weapon in lootRightHandItem1 at chanceToEquipRightHand>0 AND (2) sits on a rig
whose mesh carries the rangedOneHand animation clip set (the make-or-break -
a rig without it T-poses / melees). Ranged throw AI is then ENGINE-automatic from
the weapon class (no hand-authored projectile skill). We guarantee (1) and (2) by
CLONING a shipped, throw-proven donor and re-tiering it - the clone inherits the
full rangedOneHand anim block + equip wiring + ranged AI shape.

INTEGRATION PREREQUISITE (reported, not done here): the donor ar_slinger_37 is a
BASE-game record; a registry module's apply(db, tags) only sees the mod overlay.
So the monolith must import the donor into the overlay first (exactly like
build_svc_database.import_base_game_bosses does for base bosses). apply() below
fails loud if the donor is absent, naming the prerequisite.

Contract (tools/patches/README.md): MODULE_NAME + apply(db, tags) [+ optional
verify(db, tags)] on the SAME db/tags the monolith built. Disjoint namespace
(records\creature\monster\svc\bandit\svc_bandit_peltast_* + one SVC pool) so it
collides with no other module.
"""

MODULE_NAME = "Thrown-wielder arming (Greek bandit peltast; VETO-PENDING, unregistered)"

# --- throw-proven rigs (meshes shipping thrown-users use; b58 Part B rig whitelist) ---
RIG_WHITELIST = {
    r"xpack2\creatures\monster\bandits\greekbandit\bandit_greek02.msh",
    r"creatures\pc\male\malepc01.msh",
    r"creatures\pc\male\malepc02.msh",
    r"creatures\npc\newgreece\grkguard01.msh",
    r"xpack3\creatures\monster\satyrs\libyansatyr01.msh",
    r"xpack2\creatures\monster\mercenary\fakeeinherjar.msh",
    r"xpack2\creatures\monster\yerren\bludgeoner01.msh",
    r"xpack2\creatures\monster\foresttroll\trollbrute01.msh",
    r"xpack2\creatures\monster\dvergr\dvergrlurker01.msh",
    r"xpack2\creatures\monster\aesir\einherjar\einherjar01.msh",
    r"xpack2\creatures\monster\aesir\einherjar\einherjarranger.msh",
    r"xpack2\creatures\monster\nerthusancients\nerthusancient_bear.msh",
    r"xpack2\creatures\monster\nerthusancients\nerthusancient_ram.msh",
    r"xpack3\creatures\monster\potamoi\potamoiwarrior01.msh",
}

# Human/Greek-identity donor: the vanilla Greek-bandit slinger (bandit_greek02.msh).
_DONOR = r"records\xpack2\creatures\monster\greekbandit\ar_slinger_37.dbr"

# Tier-scaled static RangedOneHand equip tables (what the vanilla slinger equips).
_ROH_TABLE = {
    5:  r"records\xpack2\item\loottables\weapons\static\1h_ranged_05a.dbr",
    10: r"records\xpack2\item\loottables\weapons\static\1h_ranged_10a.dbr",
    15: r"records\xpack2\item\loottables\weapons\static\1h_ranged_15a.dbr",
}

# FIRST WAVE roster (recommended: Greek bandit peltast only; satyr trickster is a
# report-C1 follow-up gated on a base-satyr rig anim check). charLevel tiers are
# placeholders sized to the Act-1/2 Greek bandit pools they will join.
#   dest, tier_table_key, charLevel [N,E,L], nameTag
_ROSTER = [
    (r"records\creature\monster\svc\bandit\svc_bandit_peltast_08.dbr", 5,  [8, 40, 55],  "tagSVCMonBanditPeltast"),
    (r"records\creature\monster\svc\bandit\svc_bandit_peltast_11.dbr", 10, [11, 42, 57], "tagSVCMonBanditPeltast"),
    (r"records\creature\monster\svc\bandit\svc_bandit_peltast_14.dbr", 10, [14, 44, 59], "tagSVCMonBanditPeltast"),
]

# A minority-weight ProxyPool the MAP lane places (or refs) among Act-1/2 bandit packs:
# peltasts are a FLAVOR of the pack, not the whole pack.
_POOL = r"records\creature\proxy\svc\bandit\svc_bandit_peltast_pool.dbr"

# equip drop-slot weight band (single-digit, like the vanilla bow-archer of the tier)
_DROP_SLOT_FIELD = "chanceToEquipRightHandItem5"
_DROP_BAND = (1, 10)


def _armed_paths():
    return [spec[0] for spec in _ROSTER]


def apply(db, tags):
    from apply_svc_patches import _ensure_record  # tools/ on sys.path

    if not db.has_record(_DONOR):
        raise SystemExit(
            "thrown_wielders: donor %s absent from the overlay. INTEGRATION "
            "PREREQUISITE: the monolith must import this base-game record into the "
            "overlay first (mirror build_svc_database.import_base_game_bosses). See "
            "docs/reports/b58_thrown_wielders.md Part C4." % _DONOR)

    # Name tag (amgoz-treatment + Will-veto pending on the display copy).
    tags["tagSVCMonBanditPeltast"] = "Bandit Peltast"

    for dest, tkey, clevels, nametag in _ROSTER:
        # 1. clone the throw-proven donor (inherits rangedOneHand anims + equip + AI)
        db.clone_record(_DONOR, dest)
        # 2. re-tier + keep Common (no soul leak)
        db.set_field(dest, "charLevel", list(clevels))
        db.set_field(dest, "monsterClassification", "Common")
        # 3. re-point the equip weapon to the tier-appropriate thrown table; keep 100% equip
        db.set_field(dest, "lootRightHandItem1", [_ROH_TABLE[tkey]])
        db.set_field(dest, "chanceToEquipRightHand", 100.0)
        # 4. drop band (match a bow-archer of the tier; keep uniques from flooding)
        db.set_field(dest, _DROP_SLOT_FIELD, 5)
        # 5. display name
        db.set_field(dest, "description", nametag)

    # minority-weight pool for the map lane to place among bandit packs
    _ensure_record(db, _POOL, "database\\Templates\\ProxyPool.tpl")
    db.set_field(_POOL, "spawnMin", 1)
    db.set_field(_POOL, "spawnMax", 2)
    for i, dest in enumerate(_armed_paths(), start=1):
        db.set_field(_POOL, "name%d" % i, dest)
        db.set_field(_POOL, "weight%d" % i, 12)  # minority weight (bandit warriors are ~50)


def verify(db, tags):
    """Every armed record: exists, Class=Monster, throw-proven rig, rangedOneHand
    anim block present, equips a thrown weapon, drop weight in band, no soul leak."""
    errs = []

    def gv(rec, key):
        v = db.get_field_value(rec, key)
        return v

    def _mesh(rec):
        m = gv(rec, "mesh")
        if isinstance(m, list):
            m = m[0] if m else None
        return (str(m).lower().replace("/", "\\") if m else None)

    def _resolves_thrown(rec):
        v = gv(rec, "lootRightHandItem1")
        vals = v if isinstance(v, list) else [v]
        for t in vals:
            if not t:
                continue
            t = str(t)
            tl = t.lower()
            if "1h_ranged" in tl or "1hranged" in tl or "\\roh" in tl or "rangedonehand" in tl:
                return True
            # or a record whose Class is the thrown class
            if db.has_record(t):
                c = db.get_field_value(t, "Class")
                if c == "WeaponHunting_RangedOneHand":
                    return True
        return False

    for rec in _armed_paths():
        if not db.has_record(rec):
            errs.append("missing armed record %s" % rec); continue
        if db.get_field_value(rec, "Class") != "Monster":
            errs.append("%s is not Class=Monster" % rec)
        mesh = _mesh(rec)
        if mesh not in RIG_WHITELIST:
            errs.append("%s mesh %r not in throw-proven RIG_WHITELIST" % (rec, mesh))
        # rangedOneHand anim block present (throw-capable rig setup)
        if gv(rec, "rangedOneHandAttackAnimWeight1") is None and \
           gv(rec, "dualRangedAttackAnimWeight1") is None:
            errs.append("%s lacks the rangedOneHand anim block (would T-pose/melee)" % rec)
        # equips a thrown weapon
        ceq = gv(rec, "chanceToEquipRightHand")
        if not ceq or float(ceq) <= 0:
            errs.append("%s chanceToEquipRightHand<=0 (won't equip a thrown weapon)" % rec)
        if not _resolves_thrown(rec):
            errs.append("%s lootRightHandItem1 does not resolve to a thrown weapon" % rec)
        # drop band
        d = gv(rec, _DROP_SLOT_FIELD)
        if d is not None and not (_DROP_BAND[0] <= float(d) <= _DROP_BAND[1]):
            errs.append("%s drop-slot weight %s out of band %s" % (rec, d, _DROP_BAND))
        # no soul leak on a Common
        if gv(rec, "chanceToEquipFinger2") and float(gv(rec, "chanceToEquipFinger2") or 0) > 0:
            errs.append("%s Common wields a Finger2 (soul) - soul-leak" % rec)

    # name tag present
    if "tagSVCMonBanditPeltast" not in tags:
        errs.append("name tag tagSVCMonBanditPeltast not added to Text")

    if errs:
        raise SystemExit("thrown_wielders.verify FAILED:\n  " + "\n  ".join(errs))
    print("  thrown_wielders.verify: OK (%d armed records, all throw-proven)" % len(_armed_paths()))


# ----------------------------------------------------------------------------
# Stand-alone dry-run + negative test (no heavy build). Run:
#   py tools/patches/thrown_wielders.py <mod.arz> <base.arz>
# It imports the base donor into the overlay (simulating the monolith prereq),
# applies, verifies, proves intended-only record delta, and runs the negtest.
# ----------------------------------------------------------------------------
def _negtest(db, tags):
    """Prove verify() FAILS on each broken shape."""
    import copy as _copy
    base_ok = _armed_paths()[0]
    checks = 0

    def _expect_fail(mutate, label):
        nonlocal checks
        d2 = _clone_db_shallow(db)
        mutate(d2)
        try:
            verify(d2, dict(tags))
        except SystemExit:
            checks += 1
            return
        raise SystemExit("negtest: expected verify FAIL for %s, but it passed" % label)

    _expect_fail(lambda d: d.set_field(base_ok, "lootRightHandItem1",
                 [r"records\item\equipmentweapon\sword\c15_sword01.dbr"]), "non-thrown weapon")
    _expect_fail(lambda d: d.set_field(base_ok, "mesh",
                 [r"records\creature\monster\satyr\satyr01.msh"]), "off-whitelist rig")
    _expect_fail(lambda d: d.set_field(base_ok, _DROP_SLOT_FIELD, 99), "drop weight out of band")
    print("  thrown_wielders._negtest: OK (%d broken shapes each rejected)" % checks)


def _clone_db_shallow(db):
    # a cheap per-test copy: re-decode nothing; just deep-copy the decoded caches we touch.
    import copy
    d2 = copy.copy(db)
    d2._decoded_cache = copy.deepcopy(db._decoded_cache)
    d2._modified = set(db._modified)
    return d2


def _selftest(mod_arz, base_arz):
    import sys, os
    from pathlib import Path
    HERE = Path(__file__).resolve().parent.parent  # tools/
    sys.path.insert(0, str(HERE))
    from arz_patcher import ArzDatabase

    print("loading mod overlay %s ..." % mod_arz)
    db = ArzDatabase.from_arz(Path(mod_arz))
    print("loading base %s ..." % base_arz)
    base = ArzDatabase.from_arz(Path(base_arz))

    # simulate the monolith prereq: import the base donor into the overlay
    if not db.has_record(_DONOR):
        bn = {n.lower().replace("/", "\\"): n for n in base.record_names()}
        src = bn.get(_DONOR.lower())
        if not src:
            raise SystemExit("donor %s not in base game" % _DONOR)
        fields = base.get_fields(src)
        db._raw_records[_DONOR] = base._raw_records[src]
        db._decoded_cache[_DONOR] = __import__("copy").deepcopy(fields)
        db._record_types[_DONOR] = base._record_types.get(src, "")
        db._record_timestamps[_DONOR] = base._record_timestamps.get(src, 0)
        db._modified.add(_DONOR)
        print("  imported donor into overlay (monolith prereq simulated)")

    before = set(db.record_names())
    tags = {}
    apply(db, tags)
    after = set(db.record_names())
    added = sorted(after - before)
    intended = set(_armed_paths()) | {_POOL}
    stray = [a for a in added if a not in intended]
    print("intended-only record delta: +%d added" % len(added))
    for a in added:
        print("    + %s" % a)
    assert not stray, "STRAY records added: %s" % stray
    assert set(added) == intended, "added != intended (missing: %s)" % (intended - set(added))

    verify(db, tags)
    _negtest(db, tags)
    print("\nthrown_wielders DRY-RUN: PASS (intended-only delta; verify OK; negtest OK)")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("usage: py tools/patches/thrown_wielders.py <mod.arz> <base.arz>")
        raise SystemExit(2)
    _selftest(sys.argv[1], sys.argv[2])
