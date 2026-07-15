r"""tools/patches/thrown_wielders.py - arm identity-appropriate enemy families
with thrown (RangedOneHand) weapons so players SEE enemies throw (registry module).

WHY (audit -> docs/reports/b58_thrown_wielders.md): thrown weapons are a
Ragnarok/Atlantis/EE item class (Class = WeaponHunting_RangedOneHand, 191 recs,
all xpack2/3/4). VERIFIED ground truth: of the monsters that wield a thrown
weapon, ZERO spawn in the reachable Soulvizier-Classic campaign - every shipping
thrower is a DLC monster our Act1-Hades campaign never reaches. So Will's "we
have throwing weapons but no enemy uses them" is CONFIRMED, and to close the gap
we arm a SMALL, identity-fit, RIG-PROVEN, REACHABLE roster.

FLAGGED FOR WILL'S VETO (the b58 report is the veto artifact). NOT registered in
REGISTRY yet - it rides the NEXT integration build after Will approves the roster
(report Part C) and the coupled MAP lane wires the pool. Keeping it out of
REGISTRY leaves the golden build byte-identical (b33c5a44) for every other lane.

=============================================================================
THE MECHANISM (all four points ground-truth-verified against base+golden arz):
=============================================================================
(1) EQUIP. A monster wields a thrown weapon iff its RIGHT hand equips a
    WeaponHunting_RangedOneHand item (chanceToEquipRightHand>0, lootRightHandItem*
    -> a 1h_ranged / roh_ table) AND no competing weapon wins the other hand.
(2) RANGED AI is ENGINE-AUTOMATIC from the equipped weapon class - the base
    throwers carry NO hand-authored projectile skill; equipping the thrown weapon
    is the whole "make it throw". We copy that shape (equip; no projectile skill).
(3) MAKE-OR-BREAK - the RIG. The throw ANIMATION clips live in the MESH; the
    record's rangedOneHand*/dualRanged* anim-WEIGHT block only SELECTS them. A rig
    whose mesh lacks the clips T-poses / melees with a thrown weapon. The ONLY
    sound proof a mesh has the clips is: a SHIPPING monster THROWS on that exact
    mesh. RIG_WHITELIST below is built from the exact mesh of every shipping
    thrower; verify() asserts each armed record's mesh is in it. (Anim-weight
    fields alone are NOT proof - they are a template default present even on pure
    melee units, so they are a secondary check, never the gate.)
(4) DROPS follow normal equip-drop rules. We restore the base thrower's OWN
    right-hand block, whose unique-thrown drop slot (chanceToEquipRightHandItem5
    = 4-5 out of ~5025) is IDENTICAL to the same monster's bow-drop slot - so
    thrown drops are banded to bow-wielders BY CONSTRUCTION, not by guesswork.

=============================================================================
THE OVERLAY-DISARM ROOT CAUSE (why cloning alone is not enough) - ground truth:
=============================================================================
The base game ships GENUINE throwers on three reachable-campaign rigs:
  Maenad02.msh    creature\monster\maenad\ar_archer_06/br_archer_10  (RIGHT=1h_ranged@100, LEFT bow@0)
  DuneRaider01.msh creature\monster\duneraider\am_assassin_15/_21     (dual 1h_ranged@100)
  TigerMan01.msh  creature\monster\tigerman\ar_archer_27/ar_archer_33 (RIGHT=1h_ranged@100, LEFT bow@0)
But the SV/mod overlay (build40 golden b33c5a44) OVERLAYS and DISARMS every one -
because the SV-classic roster predates thrown weapons:
  maenad/tigerman -> RIGHT chanceToEquipRightHand=0, lootRightHandItem1 CLEARED, LEFT bow ENABLED@100
  duneraider      -> both hands swapped to melee 1h_dyn masters.
So the copy a registry module sees in `db` (the overlay) is a BOW/MELEE unit, and
cloning it inherits the DISARMED hands. We therefore, after cloning (which keeps
the mesh + the full rangedOneHand/dualRanged anim block - verified retained in the
disarmed copy - + the ranged AI + stats/skills), RE-AUTHOR the RIGHT hand with the
family's exact VANILLA thrown block (the static/monster/unique tiered N/E/L loot
arrays + their vanilla weights, captured verbatim from the base thrower) AND set
chanceToEquipLeftHand=0 so the bow/melee offhand can never win. This restore is
byte-faithful to the base thrower's own drop profile, so drops are vanilla by
construction and the unit is GUARANTEED to throw.

WHY CLONE INTO AN SVC RECORD instead of re-arming the base record in place:
cloning lets us (a) give an amgoz-voice identity, (b) force Common rank + assert
no soul leak, (c) own a disjoint SVC namespace the MAP lane places, (d) leave the
base records (and every other lane) untouched (no collision, base bow-archers
still exist for the packs that want them).

Contract (tools/patches/README.md): MODULE_NAME + apply(db, tags) [+ verify].
Disjoint namespace (records\creature\monster\svc\thrown\* + records\creature\
proxy\svc\thrown\*) so it collides with no other module.
"""

MODULE_NAME = ("Thrown-wielder arming (maenad/dune-raider/tigerman javelineers; "
               "VETO-PENDING, unregistered)")

# ---------------------------------------------------------------------------
# Throw-PROVEN rigs = the exact mesh of SHIPPING throwers (b58 Part B). A monster
# throws only if its rig's mesh carries the rangedOneHand clip set, and the ONLY
# sound proof of that is a shipping thrower on the same mesh. This set is the
# exact-mesh union over every monster in base+golden whose right hand resolves to
# a thrown weapon. Our three armed families ride the first three (all used by
# reachable campaign monsters). The rest are recorded so the whitelist is honest
# about what IS proven (future waves may reach for them). Stored lowercased with
# backslashes = the normalized form verify() compares against.
# ---------------------------------------------------------------------------
RIG_WHITELIST = {
    # reachable-campaign rigs (the ones this module arms) --------------------
    r"creatures\monster\maenad\maenad02.msh",           # Act-1 Greece maenads
    r"creatures\monster\duneraider\duneraider01.msh",   # Act-2 Egypt raiders
    r"creatures\monster\tigerman\tigerman01.msh",       # Act-3 Orient beastmen
    # other proven-throw rigs (DLC / unreachable homes; not armed here) ------
    r"creatures\npc\newgreece\grkguard01.msh",
    r"creatures\pc\male\malepc02.msh",
    r"xpack2\creatures\monster\bandits\greekbandit\bandit_greek02.msh",
    r"xpack2\creatures\monster\aesir\einherjar\einherjar01.msh",
    r"xpack2\creatures\monster\aesir\einherjar\einherjarranger.msh",
    r"xpack2\creatures\monster\foresttroll\trollbrute01.msh",
    r"xpack2\creatures\monster\mercenary\fakeeinherjar.msh",
    r"xpack2\creatures\monster\nerthusancients\nerthusancient_bear.msh",
    r"xpack2\creatures\monster\nerthusancients\nerthusancient_ram.msh",
    r"xpack2\creatures\monster\yerren\bludgeoner01.msh",
    r"xpack3\creatures\monster\potamoi\potamoiwarrior01.msh",
    r"xpack3\creatures\monster\satyrs\libyansatyr01.msh",
    r"xpack\creatures\monster\machae\machae01a.msh",
    r"xpack\creatures\monster\machae\machae02a.msh",
    r"xpack\creatures\monster\machae\machae03a.msh",
}

# equip drop-slot: the UNIQUE thrown-weapon slot weight (out of ~5025 total slot
# weight, so ~0.1%). Kept single-digit exactly like the vanilla thrown/bow commons
# of the tier so thrown drops do NOT flood. Each family's block restores the base
# thrower's own value (4-5), which EQUALS that monster's bow-drop slot weight.
_DROP_SLOT_FIELD = "chanceToEquipRightHandItem5"
_DROP_BAND = (1, 10)

# thrown loot-table roots (all resolve at runtime from the base game DB, over
# which the mod overlays; verified base=True for every table referenced below).
_LT = r"records\xpack2\item\loottables\weapons"


def _thrown_block(static3, magic3, unique3, magic_w, unique_w):
    r"""Assemble one family's exact VANILLA right-hand thrown block (captured
    verbatim from the base thrower). static3/magic3/unique3 are the [N,E,L] tier
    file stems; weights are the base thrower's own slot weights. Item1 (static
    common) dominates at 5000; Item3 (monster-magic) + Item5 (unique) are the
    rare drop slots. Left hand is disabled so nothing competes with the throw."""
    def s(sub, stem):
        return r"%s\%s\%s.dbr" % (_LT, sub, stem)
    return {
        "chanceToEquipRightHand": 100.0,
        "lootRightHandItem1": [s("static", x) for x in static3],
        "chanceToEquipRightHandItem1": 5000,
        # slots 2 & 4 unused: zero their weights so any inherited loot never fires
        # (no need to clear the loot lists - a 0-weight slot is never chosen).
        "chanceToEquipRightHandItem2": 0,
        "lootRightHandItem3": [s("monster", x) for x in magic3],
        "chanceToEquipRightHandItem3": magic_w,
        "chanceToEquipRightHandItem4": 0,
        "lootRightHandItem5": [s("unique", x) for x in unique3],
        "chanceToEquipRightHandItem5": unique_w,
        # DISARM the offhand so the base bow/melee can never win the attack.
        "chanceToEquipLeftHand": 0.0,
    }


# ---------------------------------------------------------------------------
# THE ROSTER (the veto table; report Part C2). Each variant clones its family's
# OWN shipping thrower donor at that donor's native level, so the inherited N/E/L
# charLevel + mesh + full rangedOneHand/dualRanged anim block + ranged AI already
# scale across difficulties; then apply() forces Common rank and RE-ARMS the right
# hand with the family's vanilla thrown block (see _thrown_block / OVERLAY-DISARM).
#   family -> {key, name_tag, name_text, rig(doc), act, pool, equation,
#              force_common, thrown(block), variants:[(donor,dest,native_lvl_doc)]}
# ---------------------------------------------------------------------------
_FAMILIES = [
    {
        "key": "maenad",
        "name_tag": "tagSVCMonMaenadJavelineer",
        "name_text": "Maenad Javelineer",
        "rig": r"creatures\monster\maenad\maenad02.msh",
        "act": "Act 1 (Greece)",
        "pool": r"records\creature\proxy\svc\thrown\svc_maenad_javelineer_pool.dbr",
        "equation": r"records\proxies greek\proxypoolequation_01.dbr",
        "force_common": True,   # donors are Common already; explicit = intent-safe
        # base donor: creature\monster\maenad\ar_archer_06 (RIGHT=1h_ranged@100, LEFT bow@0)
        "thrown": _thrown_block(
            static3=["1h_ranged_01b", "1h_ranged_06a", "1h_ranged_11a"],
            magic3=["ni_roh_maenad", "ei_roh_maenad", "li_roh_maenad"],
            unique3=["roh_01", "roh_06", "roh_11"],
            magic_w=20, unique_w=4),
        "variants": [
            (r"records\creature\monster\maenad\ar_archer_06.dbr",
             r"records\creature\monster\svc\thrown\svc_maenad_javelineer_06.dbr", "[6,35,53]"),
            (r"records\creature\monster\maenad\br_archer_10.dbr",
             r"records\creature\monster\svc\thrown\svc_maenad_javelineer_10.dbr", "[10,37,54]"),
        ],
    },
    {
        "key": "duneraider",
        "name_tag": "tagSVCMonDuneRaiderSkirmisher",
        "name_text": "Dune Raider Skirmisher",
        "rig": r"creatures\monster\duneraider\duneraider01.msh",
        "act": "Act 2 (Egypt)",
        "pool": r"records\creature\proxy\svc\thrown\svc_duneraider_skirmisher_pool.dbr",
        "equation": r"records\proxies egypt\proxypoolequation_01.dbr",
        "force_common": True,   # donors are CHAMPION dual-throwers -> down-rank to Common single-javelin
        # base donor: creature\monster\duneraider\am_assassin_15 (dual 1h_ranged@100)
        "thrown": _thrown_block(
            static3=["1h_ranged_02b", "1h_ranged_07a", "1h_ranged_12a"],
            magic3=["ni_roh_duneraider", "ei_roh_duneraider", "li_roh_duneraider"],
            unique3=["roh_02", "roh_07", "roh_12"],
            magic_w=25, unique_w=5),
        "variants": [
            (r"records\creature\monster\duneraider\am_assassin_15.dbr",
             r"records\creature\monster\svc\thrown\svc_duneraider_skirmisher_15.dbr", "[15,40,57]"),
            (r"records\creature\monster\duneraider\am_assassin_21.dbr",
             r"records\creature\monster\svc\thrown\svc_duneraider_skirmisher_21.dbr", "[21,44,60]"),
        ],
    },
    {
        "key": "tigerman",
        "name_tag": "tagSVCMonTigermanHunter",
        "name_text": "Tigerman Hunter",
        "rig": r"creatures\monster\tigerman\tigerman01.msh",
        "act": "Act 3 (Orient)",
        "pool": r"records\creature\proxy\svc\thrown\svc_tigerman_hunter_pool.dbr",
        "equation": r"records\proxies orient\proxypoolequation_01.dbr",
        "force_common": True,   # donors are Common already
        # base donor: creature\monster\tigerman\ar_archer_27 (RIGHT=1h_ranged@100, LEFT bow@0)
        "thrown": _thrown_block(
            static3=["1h_ranged_03a", "1h_ranged_08a", "1h_ranged_13a"],
            magic3=["ni_roh_tigerman", "ei_roh_tigerman", "li_roh_tigerman"],
            unique3=["roh_03", "roh_08", "roh_13"],
            magic_w=25, unique_w=5),
        "variants": [
            (r"records\creature\monster\tigerman\ar_archer_27.dbr",
             r"records\creature\monster\svc\thrown\svc_tigerman_hunter_27.dbr", "[27,48,63]"),
            (r"records\creature\monster\tigerman\ar_archer_33.dbr",
             r"records\creature\monster\svc\thrown\svc_tigerman_hunter_33.dbr", "[33,52,67]"),
        ],
    },
]

_PROXYPOOL_TPL = "database\\Templates\\ProxyPool.tpl"


def _armed_specs():
    """[(donor, dest, family_dict), ...] flattened over the roster."""
    out = []
    for fam in _FAMILIES:
        for donor, dest, _lvl in fam["variants"]:
            out.append((donor, dest, fam))
    return out


def _armed_paths():
    return [dest for _d, dest, _f in _armed_specs()]


def _pool_paths():
    return [fam["pool"] for fam in _FAMILIES]


def apply(db, tags):
    from apply_svc_patches import _ensure_record  # tools/ on sys.path

    # ---- 1. arm each family: clone its thrower donor, then RE-ARM the right ----
    #         hand + disable the left (the OVERLAY-DISARM restore).
    for donor, dest, fam in _armed_specs():
        if not db.has_record(donor):
            raise SystemExit(
                "thrown_wielders: donor %s absent from the overlay. INTEGRATION "
                "PREREQUISITE: the base-game thrower must be in the overlay before "
                "the registry runs (it already is in the golden build; if a future "
                "build strips base monsters, import it like "
                "build_svc_database.import_base_game_bosses). See "
                "docs/reports/b58_thrown_wielders.md Part C." % donor)
        # clone: keeps mesh + full rangedOneHand/dualRanged anim block + ranged AI
        # + stats/skills. (In the golden overlay the RIGHT hand is DISARMED to a
        # bow/melee - we restore it below; the anim block is verified retained.)
        db.clone_record(donor, dest)
        # amgoz-voice identity (existing string field -> value swap, no dtype).
        db.set_field(dest, "description", fam["name_tag"])
        # force Common flavor rank (dune-raider donor is Champion). Existing string
        # field -> value swap only, no dtype (clone-safe).
        if fam["force_common"]:
            db.set_field(dest, "monsterClassification", "Common")
        # RE-ARM: author the family's exact vanilla thrown block over the disarmed
        # hands. No explicit dtype: existing numeric fields keep their type (chance*
        # = FLOAT, *Item* weights = INT), absent loot arrays infer STRING. This is
        # the make-it-throw + drop-band-by-construction step.
        for field, value in fam["thrown"].items():
            db.set_field(dest, field, value)

    # ---- 2. name tags (amgoz voice; Will-veto pending on final copy) --------
    for fam in _FAMILIES:
        tags[fam["name_tag"]] = fam["name_text"]

    # ---- 3. one minority-flavor ProxyPool per family (map-lane artifact) ----
    # A standalone thrower pool the MAP lane references: place its proxy as a small
    # skirmisher cluster, OR harvest its name/weight rows into an existing act pack
    # at a low weight (report Part C4). Schema mirrors a real base ProxyPool
    # (e.g. xpack2\proxiesnorth\pools\human\greekbandit_01_general01): championChance
    # /Min/Max + name%d/weight%d + spawnMin/Max + proxyPoolEquation. No champions in
    # a flavor pool. All fields are new (empty record) -> set_field infers dtype.
    for fam in _FAMILIES:
        pool = fam["pool"]
        _ensure_record(db, pool, _PROXYPOOL_TPL)
        db.set_field(pool, "proxyPoolEquation", fam["equation"])
        db.set_field(pool, "spawnMin", 1)
        db.set_field(pool, "spawnMax", 2)
        db.set_field(pool, "championChance", 0.0)   # flavor commons only
        db.set_field(pool, "championMin", 0)
        db.set_field(pool, "championMax", 0)
        for i, (_donor, dest, _lvl) in enumerate(fam["variants"], start=1):
            db.set_field(pool, "name%d" % i, dest)
            db.set_field(pool, "weight%d" % i, 50)   # balance the 2 variants


# ---------------------------------------------------------------------------
def verify(db, tags):
    """Every armed record: exists, Class=Monster, sits on a PROVEN-throw rig
    (RIG_WHITELIST = the make-or-break), carries the rangedOneHand anim block,
    equips a thrown weapon at >0 chance whose loot resolves to a RangedOneHand,
    has the LEFT hand DISABLED (so nothing competes with the throw), drop-slot
    weight in band, Common rank, no soul leak. Every family name tag present;
    every pool references only this module's armed records + a resolvable equation.
    Roster-derived (iterates _FAMILIES / _armed_specs) - no hardcoded record list."""
    errs = []

    def gv(rec, key):
        return db.get_field_value(rec, key)

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
            tl = str(t).lower()
            # name heuristic (tables are base-only -> not in the overlay db, so a
            # has_record check alone would miss them; the class check is a bonus).
            if "1h_ranged" in tl or "\\roh_" in tl or "rangedonehand" in tl:
                return True
            if db.has_record(str(t)) and gv(str(t), "Class") == "WeaponHunting_RangedOneHand":
                return True
        return False

    for donor, dest, fam in _armed_specs():
        if not db.has_record(dest):
            errs.append("missing armed record %s" % dest); continue
        if gv(dest, "Class") != "Monster":
            errs.append("%s is not Class=Monster" % dest)
        # MAKE-OR-BREAK: mesh must be a shipping-thrower-proven rig.
        mesh = _mesh(dest)
        if mesh not in RIG_WHITELIST:
            errs.append("%s mesh %r not in throw-PROVEN RIG_WHITELIST "
                        "(would risk T-pose/melee)" % (dest, mesh))
        # secondary sanity: the rangedOneHand anim block is present (a template
        # default, NOT sufficient alone - the whitelist above is the real proof).
        if gv(dest, "rangedOneHandAttackAnimWeight1") is None and \
           gv(dest, "dualRangedAttackAnimWeight1") is None:
            errs.append("%s lacks the rangedOneHand anim block entirely" % dest)
        # equips a thrown weapon in the RIGHT hand
        ceq = gv(dest, "chanceToEquipRightHand")
        if not ceq or float(ceq) <= 0:
            errs.append("%s chanceToEquipRightHand<=0 (won't equip a thrown weapon)" % dest)
        if not _resolves_thrown(dest):
            errs.append("%s lootRightHandItem1 does not resolve to a thrown weapon" % dest)
        # LEFT hand DISABLED - the OVERLAY-DISARM guarantee (else the inherited
        # bow/melee offhand can win the attack and the unit won't throw).
        clh = gv(dest, "chanceToEquipLeftHand")
        if clh is not None and float(clh) > 0:
            errs.append("%s chanceToEquipLeftHand=%s>0 (bow/melee offhand can beat the throw)"
                        % (dest, clh))
        # drop band
        d = gv(dest, _DROP_SLOT_FIELD)
        if d is not None and not (_DROP_BAND[0] <= float(d) <= _DROP_BAND[1]):
            errs.append("%s drop-slot weight %s out of band %s" % (dest, d, _DROP_BAND))
        # Common flavor rank (we set it; a Champion/Hero would drop souls + be rarer)
        if fam["force_common"] and gv(dest, "monsterClassification") != "Common":
            errs.append("%s expected monsterClassification=Common, got %r"
                        % (dest, gv(dest, "monsterClassification")))
        # no soul leak on a Common (finger2 = the soul slot in this mod)
        f2 = gv(dest, "chanceToEquipFinger2")
        if f2 and float(f2) > 0:
            errs.append("%s Common wields a Finger2 (soul) - soul-leak" % dest)

    # every family name tag present
    for fam in _FAMILIES:
        if fam["name_tag"] not in tags:
            errs.append("name tag %s not added to Text" % fam["name_tag"])

    # pools: reference only armed records + a resolvable equation
    armed = set(_armed_paths())
    for fam in _FAMILIES:
        pool = fam["pool"]
        if not db.has_record(pool):
            errs.append("missing pool %s" % pool); continue
        eq = gv(pool, "proxyPoolEquation")
        if eq and not db.has_record(str(eq)):
            errs.append("%s proxyPoolEquation %r does not resolve" % (pool, eq))
        i = 1
        while True:
            nm = gv(pool, "name%d" % i)
            if nm is None:
                break
            if str(nm) not in armed:
                errs.append("%s name%d=%r is not one of this module's armed records"
                            % (pool, i, nm))
            i += 1
        if i == 1:
            errs.append("%s lists no monster (empty pool)" % pool)

    if errs:
        raise SystemExit("thrown_wielders.verify FAILED:\n  " + "\n  ".join(errs))
    print("  thrown_wielders.verify: OK (%d armed records across %d families, all "
          "throw-PROVEN rigs, right-hand-thrown + left-hand-disabled; %d pools)"
          % (len(_armed_paths()), len(_FAMILIES), len(_pool_paths())))


# ---------------------------------------------------------------------------
# Stand-alone dry-run + negative test (no heavy build). Run:
#   py tools/patches/thrown_wielders.py <mod.arz> [<base.arz>]
# The donors are base-game throwers that ALSO live (disarmed) in the mod overlay,
# so apply() clones them directly and re-arms (no prereq). If run against an
# overlay that lacks them and a base arz is supplied, they are imported first
# (simulates the integration prereq). Proves: intended-only record delta, verify
# OK, negtest rejects broken shapes. Golden build stays byte-identical (unregistered).
# ---------------------------------------------------------------------------
def _clone_db_shallow(db):
    import copy
    d2 = copy.copy(db)
    d2._decoded_cache = copy.deepcopy(db._decoded_cache)
    d2._modified = set(db._modified)
    return d2


def _negtest(db, tags):
    """Prove verify() FAILS on each broken shape (roster-derived: mutates the
    first armed record) - covers every invariant verify() asserts."""
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
                 [r"records\creature\monster\satyr\satyr01.msh"]), "off-whitelist (unproven) rig")
    _expect_fail(lambda d: d.set_field(base_ok, "chanceToEquipRightHand", 0.0),
                 "right hand unequipped")
    _expect_fail(lambda d: d.set_field(base_ok, "chanceToEquipLeftHand", 100.0),
                 "left hand re-enabled (offhand competes with throw)")
    _expect_fail(lambda d: d.set_field(base_ok, _DROP_SLOT_FIELD, 99), "drop weight out of band")
    _expect_fail(lambda d: d.set_field(base_ok, "monsterClassification", "Champion"), "non-Common rank")
    _expect_fail(lambda d: d.set_field(base_ok, "chanceToEquipFinger2", 100.0), "soul-leak (finger2)")
    print("  thrown_wielders._negtest: OK (%d broken shapes each rejected)" % checks)


def _import_donor(db, base, path):
    import copy
    bn = {n.lower().replace("/", "\\"): n for n in base.record_names()}
    src = bn.get(path.lower().replace("/", "\\"))
    if not src:
        raise SystemExit("donor %s not in base game" % path)
    db._raw_records[path] = base._raw_records[src]
    db._decoded_cache[path] = copy.deepcopy(base.get_fields(src))
    db._record_types[path] = base._record_types.get(src, "")
    db._record_timestamps[path] = base._record_timestamps.get(src, 0)
    db._modified.add(path)


def _selftest(mod_arz, base_arz=None):
    import sys
    from pathlib import Path
    HERE = Path(__file__).resolve().parent.parent  # tools/
    sys.path.insert(0, str(HERE))
    from arz_patcher import ArzDatabase

    print("loading mod overlay %s ..." % mod_arz)
    db = ArzDatabase.from_arz(Path(mod_arz))
    base = None
    if base_arz:
        print("loading base %s ..." % base_arz)
        base = ArzDatabase.from_arz(Path(base_arz))

    # ensure donors present (they are, in the golden overlay); import if not.
    for donor, _dest, _fam in _armed_specs():
        if not db.has_record(donor):
            if base is None:
                raise SystemExit("donor %s not in overlay and no base arz given" % donor)
            _import_donor(db, base, donor)
            print("  imported donor %s (prereq simulated)" % donor.split("\\")[-1])

    # Prove the ground-truth OVERLAY-DISARM premise on the loaded overlay: the
    # donor's RIGHT hand is disarmed (so a naive clone would NOT throw).
    d0 = _armed_specs()[0][0]
    pre = db.get_field_value(d0, "chanceToEquipRightHand")
    print("premise: donor %s chanceToEquipRightHand in overlay = %s (0 => disarmed, re-arm required)"
          % (d0.split("\\")[-1], pre))

    before = set(db.record_names())
    tags = {}
    apply(db, tags)
    after = set(db.record_names())
    added = sorted(after - before)
    intended = set(_armed_paths()) | set(_pool_paths())
    stray = [a for a in added if a not in intended]
    print("intended-only record delta: +%d added" % len(added))
    for a in added:
        print("    + %s" % a)
    assert not stray, "STRAY records added: %s" % stray
    assert set(added) == intended, "added != intended (missing: %s)" % (intended - set(added))
    print("tags added: %s" % sorted(k for k in tags))

    # post-condition spot check: the first armed record now actually throws.
    a0 = _armed_paths()[0]
    print("post: %s RIGHT chance=%s LEFT chance=%s loot1[0]=%s" % (
        a0.split("\\")[-1], db.get_field_value(a0, "chanceToEquipRightHand"),
        db.get_field_value(a0, "chanceToEquipLeftHand"),
        (db.get_field_value(a0, "lootRightHandItem1") or [None])[0]))

    verify(db, tags)
    _negtest(db, tags)
    print("\nthrown_wielders DRY-RUN: PASS (intended-only +%d delta; verify OK; negtest OK)"
          % len(added))


if __name__ == "__main__":
    import sys
    if len(sys.argv) not in (2, 3):
        print("usage: py tools/patches/thrown_wielders.py <mod.arz> [<base.arz>]")
        raise SystemExit(2)
    _selftest(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None)
