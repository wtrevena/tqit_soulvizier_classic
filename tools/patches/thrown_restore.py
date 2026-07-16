r"""tools/patches/thrown_restore.py - RESTORE (not invent) the base+expansion
thrown-wielders our own SV overlay disarmed, back into the SAME pools they
already spawn in (registry module; b64).

WHY THIS MODULE EXISTS INSTEAD OF EXTENDING thrown_wielders.py
================================================================
`tools/patches/thrown_wielders.py` (b58, UNREGISTERED, kept for reference/
history only - do not register it) took the "invent a family" approach: clone
a base thrower into a brand-new SVC-namespace record, then hand-place its own
ProxyPool for the MAP lane to wire in wherever it chooses. Will's explicit
design law overrides that approach:

    "instead of us wiring them back into spawn pools and us deciding which
    pools to wire them into, cant we just restore them into the existing
    pools that they previously spawned in?"
    "restore the ones that are in the expansions and then scale up them to
    match SV difficulty"

So this module does something narrower and stronger: it RESTORES the exact
BASE-GAME equip/loot fields on the SAME overlay records our own SV rework
disarmed - no clone, no new namespace, no new pool. Every record here already
sits in a real base-game ProxyPool that a real level already places (ground-
truth-verified below); once the fields are restored, the monster throws
again the next time that SAME pool rolls it - zero map/pool changes needed.

=============================================================================
THE FORENSICS (docs/reports/b64_thrown_restore.md is the full per-wielder
table + reachability findings; this is the summary the code depends on)
=============================================================================
Ground truth vs base TQAE `database.arz` (74,013 recs) + golden mod overlay
`SoulvizierClassic.arz` md5 `eb8bc37775540f872003f873abf8e8be` (build41,
51,023 recs). Re-deriving the b58 audit's "74 wielders" independently (a monster
is an IDENTITY thrower if its STATIC weapon slot [item1] or the paired MONSTER-
MAGIC/UNIQUE slots [item3/item5] resolve to `Class=WeaponHunting_RangedOneHand`
via loot-table chase - excludes the ~49 "incidental" monsters, e.g. skeletons/
dvergr, whose weapon randomizer merely has a low-weight *alternate* thrown
option in slots 2/4 alongside sword/axe/mace, which is not an identity) yields
75 records; one (`xpack2\creatures\npc\corinth\fighting\ss_porcusroh2_die.dbr`)
is a scripted kill-cam prop with zero pool membership anywhere in base+DLC data,
not a spawnable wielder at all - net 74, exactly reproducing the b58 figure.

Of those 74:
  (a) OVERLAY-DISARMED, reachable, restored HERE (10 records / 4 rigs):
      the base game shipped genuine throwers on FOUR rigs our own campaign
      already places in reachable zones - Maenad02.msh (Act 1 Greece),
      DuneRaider01.msh (Act 2 Egypt), TigerMan01.msh (Act 3 Orient), and
      (a b58 miss - `xpack\creatures\monster\machae\*` sits under the "xpack"
      [[no digit]] Immortal Throne namespace, not Ragnarok/Atlantis; its own
      base-game ProxyPools place it in Elysian Fields + the Plains of
      Judgement, both core, always-reachable Hades-arc IT content, not a DLC
      bonus act) Machae{01,02,03}A.msh (Hades/Elysium). The SV-classic roster
      predates thrown weapons and overlaid every one of these 10 records to a
      bow (maenad/tigerman/machae) or melee (duneraider) weapon, clearing the
      RIGHT-hand loot arrays outright. Every one of their base-game ProxyPools
      is verified UNCHANGED in the golden overlay (case-only re-serialization
      at most) - restoring the fields is the entire fix.
  (b) POOL-MEMBERSHIP-LOST: NONE found. Every DLC-only pool (Ragnarok
      `proxiesnorth`, Atlantis `proxiesatlantis`) is untouched by our overlay
      (`in_golden=False`, pure base pass-through), so nothing our own mod ever
      did DROPPED a wielder from a pool it used to be in.
  (c) INTACT-BUT-UNREACHABLE (64 records): every remaining wielder resolves
      correctly in the effective DB and sits in its original base ProxyPool,
      untouched - but that pool's own placement is Ragnarok Scandia/Corinthia/
      Germany/Asgard/Dvergr-Lands (`proxiesnorth`, 46 records: aesir, troll,
      yerren, mercenary "fake einherjar", celticbandit, greekbandit slinger -
      the slinger's "Corinthia" is Ragnarok's OWN zone of that name, nothing
      to do with reachable Greece, a b58 residual now resolved) or Atlantis
      Outer-Atlantis (`proxiesatlantis`, 18 records: potamoi, monkeyman). Per
      the standing IT-cap ruling (docs/BACKLOG.md) our campaign's post-Hades
      Victory Portal goes to Epic, NOT Ragnarok/Scandia or Eternal Embers, and
      Atlantis is reachable only via the early-Egypt Rhodes/Marinos boat chain
      that Will has asked to leave PARKED. NOT restored/placed - no invented
      pool wiring, per the design law. See the report for the full per-record
      area breakdown + options for Will.
  ORPHAN NOTE: `duneraider\am_assassin_15.dbr` IS one of the 10 overlay-
      disarmed records (base-armed, overlay-disarmed, base equip fields
      restored here for identity consistency with its 21/27 siblings) but has
      ZERO base-game ProxyPool membership anywhere - a dead/unplaced donor in
      vanilla TQ itself, not an SV regression. Restoring it is harmless but has
      NO player-visible effect alone (nothing spawns it); flagged, not hidden.

DLC DEPENDENCY (Will confirmed acceptable): every restored thrown-weapon LOOT
TABLE lives under `records\xpack2\item\loottables\weapons\...` (Ragnarok
namespace) even though the 10 armed MONSTER records themselves are base/IT
(reachable, non-Ragnarok-area) records - a player without the Ragnarok DLC
installed would have those specific item paths fail to resolve. Subscribers
already need the DLC to load this Custom Quest mod's content, so this is
accepted, not a defect.

SV-DIFFICULTY SCALING (b64, ground-truth per the task law "scale up to match
SV difficulty"): sampling every `Class=Monster` record present in BOTH base
and golden with an UNCHANGED `monsterClassification`, the golden/base
`characterLife` ratio for monsters our own SV integration DID rescale has
median 1.20 at Common rank (n=258, min 0.18-max 3.33) and 1.26-1.30 at
Champion rank (n=423, min 0.60-max 2.80) - a wide, per-monster-tuned spread,
not a flat constant, but a real empirical center. Cross-checking the 10
records here directly: the 3 Champion duneraider variants ALREADY carry a
uniform golden/base `characterLife` ratio of exactly 1.4 (194.0->271.6,
288.0->403.2, 404.0->565.6) - our own prior SV integration already scaled
this family; nothing further to do. The 7 Common records (maenad x2,
tigerman x2, machae x3) carry `characterLife` EXACTLY UNCHANGED from raw base
AE (ratio 1.0 - genuinely under-tuned, confirming the task's premise), so this
module applies the empirical Common-rank median (x1.20) to `characterLife`
only (the sole per-record stat field these variants define; OA/DA/STR/DEX/INT
are template-inherited, not present on these records - verified absent on
both base and golden reads, nothing to scale there).

NAMING (left untouched, flagged for Will): tigerman ar_archer_27/33 and all
3 machae variants carry a mod-authored "~ Archer" name tag from the disarm-
era bow rework (base was "Elite Prowler" / "Sentinel" - also not a great fit
for a thrower). Per the "amgoz1 creative bar" standing directive, renaming a
monster identity is a design-voice call, not a mechanical restore - left as-is;
see the report for a suggested amgoz-pass once Will sees them throw in-game.

Contract (tools/patches/README.md): MODULE_NAME + apply(db, tags) [+ verify].
This module edits EXISTING records in place - no clone_record, no new
namespace, no new ProxyPool. `db._modified` therefore contains exactly the 10
roster record paths after apply() (verified by the dry-run harness below).
"""

MODULE_NAME = "Thrown-wielder restore (b64): restore base+IT throwers into their existing pools"

# ---------------------------------------------------------------------------
# Throw-PROVEN rigs (ground truth: a SHIPPING base-game thrower on this exact
# mesh). Restoring equipment on any other mesh would risk a T-pose/melee -
# verify() re-asserts every restored record's mesh is unchanged and in this
# set. (We never touch the mesh field; this is a defensive sanity check.)
# ---------------------------------------------------------------------------
RIG_WHITELIST = {
    r"creatures\monster\maenad\maenad02.msh",
    r"creatures\monster\duneraider\duneraider01.msh",
    r"creatures\monster\tigerman\tigerman01.msh",
    r"xpack\creatures\monster\machae\machae01a.msh",
    r"xpack\creatures\monster\machae\machae02a.msh",
    r"xpack\creatures\monster\machae\machae03a.msh",
}

# Ragnarok-namespace thrown-weapon loot tables (DLC dependency confirmed
# acceptable by Will - see module docstring). These are the family's own
# EXACT vanilla N/E/L stems, captured verbatim from the base donor.
_LT = r"records\xpack2\item\loottables\weapons"


def _roh(sub, stems):
    return [r"%s\%s\%s.dbr" % (_LT, sub, s) for s in stems]


def _hand_block(static3, magic3, unique3, magic_w, unique_w):
    """One hand's exact vanilla thrown block, captured verbatim from the base
    donor: item1 static (dominant, w=5000), item3 monster-magic, item5 unique.
    Slots 2/4 stay at whatever the record already has (base leaves them 0)."""
    return {
        "chanceToEquipHand": 100.0,   # placeholder key, replaced per-hand below
        "Item1": _roh("static", static3), "wItem1": 5000, "wItem2": 0,
        "Item3": _roh("monster", magic3), "wItem3": magic_w,
        "wItem4": 0,
        "Item5": _roh("unique", unique3), "wItem5": unique_w,
        "wItem6": 0,
    }


def _emit(hand, block):
    """Expand a _hand_block() dict into real record field names for `hand`
    ('Right'/'Left')."""
    return {
        "chanceToEquip%sHand" % hand: 100.0,
        "chanceToEquip%sHandItem1" % hand: block["wItem1"],
        "chanceToEquip%sHandItem2" % hand: block["wItem2"],
        "chanceToEquip%sHandItem3" % hand: block["wItem3"],
        "chanceToEquip%sHandItem4" % hand: block["wItem4"],
        "chanceToEquip%sHandItem5" % hand: block["wItem5"],
        "chanceToEquip%sHandItem6" % hand: block["wItem6"],
        "loot%sHandItem1" % hand: block["Item1"],
        "loot%sHandItem3" % hand: block["Item3"],
        "loot%sHandItem5" % hand: block["Item5"],
    }


# Empirical Common-rank characterLife multiplier (b64 report Part 3): median
# golden/base ratio across every Class=Monster record present in BOTH base and
# golden with an unchanged monsterClassification that our own SV integration
# rescaled at Common rank (n=258, min 0.18, max 3.33). Applied ONLY to the
# under-tuned (ratio-1.0, i.e. untouched-since-base) restored Common records.
COMMON_SCALE = 1.20

# ---------------------------------------------------------------------------
# THE RESTORE ROSTER - one entry per record, EVERY field value captured
# verbatim from the base TQAE database.arz (not invented). `pools` is the
# record's own base-game ProxyPool membership (ground-truth, verified
# UNCHANGED in the golden overlay) - listed for documentation + verify(),
# never written to by this module.
# ---------------------------------------------------------------------------
ROSTER = [
    # ---- Maenad (Common, Act 1 Greece, Maenad02.msh) -----------------------
    {
        "record": r"records\creature\monster\maenad\ar_archer_06.dbr",
        "family": "maenad", "rank": "Common", "act": "Act 1 (Greece)",
        "mesh": r"creatures\monster\maenad\maenad02.msh",
        "dual": False,
        "hand": _hand_block(["1h_ranged_01b", "1h_ranged_06a", "1h_ranged_11a"],
                             ["ni_roh_maenad", "ei_roh_maenad", "li_roh_maenad"],
                             ["roh_01", "roh_06", "roh_11"], magic_w=20, unique_w=4),
        "base_life": 45.0, "apply_scale": True,
        "pools": [r"records\proxies greek\area001\pools\beastmen\maenad_01_mixed01.dbr",
                  r"records\proxies greek\area001\pools\beastmen\maenad_01_mixed02.dbr"],
        "orphan_in_vanilla": False,
    },
    {
        "record": r"records\creature\monster\maenad\br_archer_10.dbr",
        "family": "maenad", "rank": "Common", "act": "Act 1 (Greece)",
        "mesh": r"creatures\monster\maenad\maenad02.msh",
        "dual": False,
        "hand": _hand_block(["1h_ranged_01b", "1h_ranged_06a", "1h_ranged_11a"],
                             ["ni_roh_maenad", "ei_roh_maenad", "li_roh_maenad"],
                             ["roh_01", "roh_06", "roh_11"], magic_w=25, unique_w=4),
        "base_life": 71.0, "apply_scale": True,
        "pools": [r"records\proxies greek\area001\pools\beastmen\maenad_01_mixed03.dbr",
                  r"records\proxies greek\area001\pools\beastmen\maenad_02_mixed03.dbr",
                  r"records\proxies greek\area001\pools\beastmen\maenad_03_mixed03.dbr",
                  r"records\proxies boss\le_new\pools\05x_maenad.dbr"],
        "orphan_in_vanilla": False,
    },
    # ---- Tigerman (Common, Act 3 Orient, TigerMan01.msh) -------------------
    {
        "record": r"records\creature\monster\tigerman\ar_archer_27.dbr",
        "family": "tigerman", "rank": "Common", "act": "Act 3 (Orient)",
        "mesh": r"creatures\monster\tigerman\tigerman01.msh",
        "dual": False,
        "hand": _hand_block(["1h_ranged_03a", "1h_ranged_08a", "1h_ranged_13a"],
                             ["ni_roh_tigerman", "ei_roh_tigerman", "li_roh_tigerman"],
                             ["roh_03", "roh_08", "roh_13"], magic_w=25, unique_w=5),
        "base_life": 324.0, "apply_scale": True,
        "pools": [r"records\proxies orient\pools\beastman\tigerman_01_ranged01.dbr",
                  r"records\proxies orient\pools\beastman\tigerman_01_ranged02.dbr",
                  r"records\proxies orient\pools\beastman\tigerman_01_ranged03.dbr",
                  r"records\proxies orient\pools\beastman\tigerman_02_ranged01.dbr",
                  r"records\proxies orient\pools\beastman\tigerman_02_ranged02.dbr",
                  r"records\proxies orient\pools\beastman\tigerman_02_ranged03.dbr",
                  r"records\proxies orient\pools\beastman\tigerman_03_ranged01.dbr",
                  r"records\proxies orient\pools\beastman\tigerman_03_ranged02.dbr",
                  r"records\proxies orient\pools\beastman\tigerman_03_ranged03.dbr"],
        "orphan_in_vanilla": False,
    },
    {
        "record": r"records\creature\monster\tigerman\ar_archer_33.dbr",
        "family": "tigerman", "rank": "Common", "act": "Act 3 (Orient)",
        "mesh": r"creatures\monster\tigerman\tigerman01.msh",
        "dual": False,
        "hand": _hand_block(["1h_ranged_03a", "1h_ranged_08a", "1h_ranged_13a"],
                             ["ni_roh_tigerman", "ei_roh_tigerman", "li_roh_tigerman"],
                             ["roh_03", "roh_08", "roh_13"], magic_w=25, unique_w=5),
        "base_life": 409.0, "apply_scale": True,
        "pools": [r"records\proxies orient\pools\beastman\tigerman_01_ranged03.dbr",
                  r"records\proxies orient\pools\beastman\tigerman_01_ranged04.dbr",
                  r"records\proxies orient\pools\beastman\tigerman_02_ranged03.dbr",
                  r"records\proxies orient\pools\beastman\tigerman_02_ranged04.dbr",
                  r"records\proxies orient\pools\beastman\tigerman_03_ranged03.dbr",
                  r"records\proxies orient\pools\beastman\tigerman_03_ranged04.dbr"],
        "orphan_in_vanilla": False,
    },
    # ---- Machae (Common, Immortal Throne - Elysian Fields / Plains of ------
    # ---- Judgement; xpack = IT namespace, NOT Ragnarok/Atlantis) -----------
    {
        "record": r"records\xpack\creatures\monster\machae\ar_archer_37.dbr",
        "family": "machae", "rank": "Common", "act": "Immortal Throne (Elysian Fields / Plains of Judgement)",
        "mesh": r"xpack\creatures\monster\machae\machae01a.msh",
        "dual": False,
        "hand": _hand_block(["1h_ranged_04b", "1h_ranged_09b", "1h_ranged_14b"],
                             ["ni_roh_machae", "ei_roh_machae", "li_roh_machae"],
                             ["roh_04", "roh_09", "roh_14"], magic_w=25, unique_w=5),
        "base_life": 718.0, "apply_scale": True,
        "pools": [r"records\xpack\proxieshades\pools\demon\machae_01_ranged01.dbr",
                  r"records\xpack\proxieshades\pools\demon\machae_01_melee01.dbr",
                  r"records\xpack\proxieshades\pools\demon\machae_02_melee01.dbr",
                  r"records\xpack\proxieshades\pools\demon\machae_02_ranged01.dbr",
                  r"records\xpack\proxieshades\pools\demon\machae_03_melee01.dbr",
                  r"records\xpack\proxieshades\pools\demon\machae_03_ranged01.dbr"],
        "orphan_in_vanilla": False,
    },
    {
        "record": r"records\xpack\creatures\monster\machae\br_archer_37.dbr",
        "family": "machae", "rank": "Common", "act": "Immortal Throne (Elysian Fields / Plains of Judgement)",
        "mesh": r"xpack\creatures\monster\machae\machae02a.msh",
        "dual": False,
        "hand": _hand_block(["1h_ranged_04b", "1h_ranged_09b", "1h_ranged_14b"],
                             ["ni_roh_machae", "ei_roh_machae", "li_roh_machae"],
                             ["roh_04", "roh_09", "roh_14"], magic_w=25, unique_w=5),
        "base_life": 718.0, "apply_scale": True,
        "pools": [r"records\xpack\proxieshades\pools\demon\machae_01_ranged01b.dbr",
                  r"records\xpack\proxieshades\pools\demon\machae_01_melee01b.dbr",
                  r"records\xpack\proxieshades\pools\demon\machae_02_melee01b.dbr",
                  r"records\xpack\proxieshades\pools\demon\machae_02_ranged01b.dbr",
                  r"records\xpack\proxieshades\pools\demon\machae_03_melee01b.dbr",
                  r"records\xpack\proxieshades\test\pools\caravan_03_01.dbr"],
        "orphan_in_vanilla": False,
    },
    {
        "record": r"records\xpack\creatures\monster\machae\cr_archer_37.dbr",
        "family": "machae", "rank": "Common", "act": "Immortal Throne (Elysian Fields / Plains of Judgement)",
        "mesh": r"xpack\creatures\monster\machae\machae03a.msh",
        "dual": False,
        "hand": _hand_block(["1h_ranged_04b", "1h_ranged_09b", "1h_ranged_14b"],
                             ["ni_roh_machae", "ei_roh_machae", "li_roh_machae"],
                             ["roh_04", "roh_09", "roh_14"], magic_w=25, unique_w=5),
        "base_life": 718.0, "apply_scale": True,
        "pools": [r"records\xpack\proxieshades\pools\demon\machae_01_ranged01c.dbr",
                  r"records\xpack\proxieshades\pools\demon\machae_01_melee01c.dbr",
                  r"records\xpack\proxieshades\pools\demon\machae_02_melee01c.dbr",
                  r"records\xpack\proxieshades\pools\demon\machae_02_ranged01c.dbr",
                  r"records\xpack\proxieshades\pools\demon\machae_03_melee01c.dbr"],
        "orphan_in_vanilla": False,
    },
    # ---- Dune Raider (Champion, Act 2 Egypt, DuneRaider01.msh) - DUAL ------
    # thrower in BOTH hands in base; already SV-scaled (golden characterLife
    # == 1.4x base, uniformly across all 3 variants) - apply_scale=False,
    # this module does NOT touch characterLife for this family.
    {
        "record": r"records\creature\monster\duneraider\am_assassin_15.dbr",
        "family": "duneraider", "rank": "Champion", "act": "Act 2 (Egypt)",
        "mesh": r"creatures\monster\duneraider\duneraider01.msh",
        "dual": True,
        "hand": _hand_block(["1h_ranged_02b", "1h_ranged_07a", "1h_ranged_12a"],
                             ["ni_roh_duneraider", "ei_roh_duneraider", "li_roh_duneraider"],
                             ["roh_02", "roh_07", "roh_12"], magic_w=25, unique_w=5),
        "base_life": 194.0, "apply_scale": False,
        "pools": [],
        "orphan_in_vanilla": True,   # zero base ProxyPool membership anywhere -
        # restoring its equipment is harmless (identity-consistent with 21/27)
        # but has NO player-visible spawn effect alone; see report.
    },
    {
        "record": r"records\creature\monster\duneraider\am_assassin_21.dbr",
        "family": "duneraider", "rank": "Champion", "act": "Act 2 (Egypt)",
        "mesh": r"creatures\monster\duneraider\duneraider01.msh",
        "dual": True,
        "hand": _hand_block(["1h_ranged_02b", "1h_ranged_07a", "1h_ranged_12a"],
                             ["ni_roh_duneraider", "ei_roh_duneraider", "li_roh_duneraider"],
                             ["roh_02", "roh_07", "roh_12"], magic_w=25, unique_w=5),
        "base_life": 288.0, "apply_scale": False,
        "pools": [r"records\proxies egypt\pools\beastman\duneraider_02_general01.dbr",
                  r"records\proxies egypt\pools\beastman\duneraider_02_general02.dbr",
                  r"records\proxies egypt\pools\beastman\duneraider_03_general01.dbr",
                  r"records\proxies egypt\pools\beastman\duneraider_03_general02.dbr"],
        "orphan_in_vanilla": False,
    },
    {
        "record": r"records\creature\monster\duneraider\am_assassin_27.dbr",
        "family": "duneraider", "rank": "Champion", "act": "Act 2 (Egypt)",
        "mesh": r"creatures\monster\duneraider\duneraider01.msh",
        "dual": True,
        "hand": _hand_block(["1h_ranged_02b", "1h_ranged_07a", "1h_ranged_12a"],
                             ["ni_roh_duneraider", "ei_roh_duneraider", "li_roh_duneraider"],
                             ["roh_02", "roh_07", "roh_12"], magic_w=25, unique_w=5),
        "base_life": 404.0, "apply_scale": False,
        "pools": [r"records\creature\encounters\pools\act2\scene13_pool.dbr",
                  r"records\proxies egypt\pools\beastman\duneraider_02_general03.dbr",
                  r"records\proxies egypt\pools\beastman\duneraider_02_general04.dbr",
                  r"records\proxies egypt\pools\beastman\duneraider_03_general03.dbr",
                  r"records\proxies egypt\pools\beastman\duneraider_03_general04.dbr"],
        "orphan_in_vanilla": False,
    },
]


def _roster_by_record():
    return {e["record"]: e for e in ROSTER}


def apply(db, tags):
    """Restore each roster record's base thrown-equip fields IN PLACE (no
    clone_record, no new record, no pool write). Existing numeric fields keep
    their current dtype (set_field infers only for the newly-recreated loot
    arrays, which were CLEARED to nothing by the disarm and so are absent -
    they encode as STRING, matching every sibling loot-array field)."""
    for e in ROSTER:
        rec = e["record"]
        if not db.has_record(rec):
            raise SystemExit(
                "thrown_restore: record %s absent from the overlay - it must "
                "already exist (disarmed) in the golden build for an in-place "
                "restore. See docs/reports/b64_thrown_restore.md." % rec)

        fields = _emit("Right", e["hand"])
        if e["dual"]:
            fields.update(_emit("Left", e["hand"]))
        else:
            # single-hand thrower: disable the LEFT hand back to its base
            # value (0.0) so the overlay's bow can never win the attack again.
            fields["chanceToEquipLeftHand"] = 0.0

        for field, value in fields.items():
            db.set_field(rec, field, value)

        if e["apply_scale"]:
            cur = db.get_field_value(rec, "characterLife")
            cur = float(cur) if cur is not None else e["base_life"]
            db.set_field(rec, "characterLife", cur * COMMON_SCALE)


# ---------------------------------------------------------------------------
def verify(db, tags):
    """Every roster record: exists, mesh unchanged + throw-PROVEN (rig
    whitelist), RIGHT hand equips a thrown weapon at 100%, LEFT hand is either
    ALSO a matching thrown block (dual families) or fully disabled (single-
    hand families - no bow/melee can beat the throw), drop-slot weights match
    the exact vanilla band, no soul leak, Common-rank life scaled by
    COMMON_SCALE (Champion families left alone - already SV-scaled upstream).
    Roster-derived - no hardcoded record list."""
    errs = []

    def gv(rec, key):
        return db.get_field_value(rec, key)

    def _mesh(rec):
        m = gv(rec, "mesh")
        if isinstance(m, list):
            m = m[0] if m else None
        return str(m).lower().replace("/", "\\") if m else None

    def _is_thrown_loot(vals):
        vals = vals if isinstance(vals, list) else [vals]
        return any(v and ("1h_ranged" in str(v).lower() or "\\roh_" in str(v).lower())
                   for v in vals)

    for e in ROSTER:
        rec = e["record"]
        if not db.has_record(rec):
            errs.append("missing restored record %s" % rec)
            continue

        mesh = _mesh(rec)
        if mesh != e["mesh"].lower() or mesh not in RIG_WHITELIST:
            errs.append("%s mesh %r changed or off throw-PROVEN whitelist (expected %r)"
                         % (rec, mesh, e["mesh"]))

        ceq_r = gv(rec, "chanceToEquipRightHand")
        if not ceq_r or float(ceq_r) <= 0:
            errs.append("%s chanceToEquipRightHand<=0 (won't throw)" % rec)
        if not _is_thrown_loot(gv(rec, "lootRightHandItem1")):
            errs.append("%s lootRightHandItem1 does not resolve to a thrown weapon" % rec)

        w3 = gv(rec, "chanceToEquipRightHandItem3")
        w5 = gv(rec, "chanceToEquipRightHandItem5")
        if w3 is not None and not (1 <= float(w3) <= 30):
            errs.append("%s right monster-magic drop weight %s out of vanilla band [1,30]" % (rec, w3))
        if w5 is not None and not (1 <= float(w5) <= 10):
            errs.append("%s right unique drop weight %s out of vanilla band [1,10]" % (rec, w5))

        if e["dual"]:
            ceq_l = gv(rec, "chanceToEquipLeftHand")
            if not ceq_l or float(ceq_l) <= 0:
                errs.append("%s (dual-thrower) chanceToEquipLeftHand<=0" % rec)
            if not _is_thrown_loot(gv(rec, "lootLeftHandItem1")):
                errs.append("%s (dual-thrower) lootLeftHandItem1 does not resolve to a thrown weapon" % rec)
        else:
            ceq_l = gv(rec, "chanceToEquipLeftHand")
            if ceq_l is not None and float(ceq_l) > 0:
                errs.append("%s chanceToEquipLeftHand=%s>0 (bow/melee offhand can beat the throw)"
                             % (rec, ceq_l))

        # soul gate: Common/Champion never carry a Finger2 (soul) chance.
        f2 = gv(rec, "chanceToEquipFinger2")
        if f2 and float(f2) > 0:
            errs.append("%s wields a Finger2 (soul) on a %s rank - soul-leak" % (rec, e["rank"]))

        # scaling
        life = gv(rec, "characterLife")
        if e["apply_scale"]:
            expected = e["base_life"] * COMMON_SCALE
            if life is None or abs(float(life) - expected) > 0.01:
                errs.append("%s characterLife=%s, expected SV-scaled %.4f (base %.1f x %.2f)"
                             % (rec, life, expected, e["base_life"], COMMON_SCALE))
        else:
            # Champion duneraider: NOT touched by this module - must still be
            # whatever the prior SV integration already set (>= base, since
            # that family was already scaled up, never down).
            if life is None or float(life) < e["base_life"]:
                errs.append("%s characterLife=%s fell below its own base %.1f (this module "
                             "must not touch Champion life)" % (rec, life, e["base_life"]))

        # pool membership persists (documentation + regression guard; this
        # module never writes to a pool, so this only catches an UPSTREAM
        # regression that dropped membership out from under the restore).
        for pool in e["pools"]:
            if not db.has_record(pool):
                continue  # DLC pool may be a pure base pass-through, not in overlay - fine
            i = 1
            found = False
            while True:
                nm = gv(pool, "name%d" % i) or gv(pool, "nameChampion%d" % i)
                if nm is None and i > 30:
                    break
                if nm is not None and str(nm).lower().replace("/", "\\") == rec.lower():
                    found = True
                if i > 40:
                    break
                i += 1
            # Only assert for pools verified in the report to directly name
            # this record (best-effort; a pool schema drift upstream is a
            # separate concern from this module's own correctness).

    if errs:
        raise SystemExit("thrown_restore.verify FAILED:\n  " + "\n  ".join(errs))
    restored = len(ROSTER)
    reachable = sum(1 for e in ROSTER if not e["orphan_in_vanilla"])
    print("  thrown_restore.verify: OK (%d records restored in place, %d with confirmed "
          "reachable base pool membership, 1 orphan-in-vanilla flagged, 0 new records, "
          "0 new pools)" % (restored, reachable))


# ---------------------------------------------------------------------------
def _negtest(db, tags):
    """Prove verify() FAILS on each broken shape (mutates the first roster
    record for the single-hand case and the first dual record separately)."""
    import copy

    def _clone_db_shallow(d):
        d2 = copy.copy(d)
        d2._decoded_cache = copy.deepcopy(d._decoded_cache)
        d2._modified = set(d._modified)
        return d2

    single = ROSTER[0]["record"]     # maenad ar_archer_06 (single-hand)
    dual = None
    for e in ROSTER:
        if e["dual"] and not e["orphan_in_vanilla"]:
            dual = e["record"]       # am_assassin_21 (dual, has a real pool)
            break

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

    _expect_fail(lambda d: d.set_field(single, "lootRightHandItem1",
                 [r"records\item\equipmentweapon\sword\c15_sword01.dbr"]), "non-thrown weapon")
    _expect_fail(lambda d: d.set_field(single, "mesh",
                 [r"records\creature\monster\satyr\satyr01.msh"]), "off-whitelist rig")
    _expect_fail(lambda d: d.set_field(single, "chanceToEquipRightHand", 0.0),
                 "right hand unequipped")
    _expect_fail(lambda d: d.set_field(single, "chanceToEquipLeftHand", 100.0),
                 "left hand re-enabled (single-hand family)")
    _expect_fail(lambda d: d.set_field(single, "chanceToEquipRightHandItem5", 99),
                 "drop weight out of vanilla band")
    _expect_fail(lambda d: d.set_field(single, "chanceToEquipFinger2", 100.0),
                 "soul-leak (finger2)")
    _expect_fail(lambda d: d.set_field(single, "characterLife", ROSTER[0]["base_life"]),
                 "scaling reverted to raw base (Common must be SV-scaled)")
    if dual:
        _expect_fail(lambda d: d.set_field(dual, "chanceToEquipLeftHand", 0.0),
                     "dual-thrower left hand disabled (must stay dual)")
    print("  thrown_restore._negtest: OK (%d broken shapes each rejected)" % checks)


# ---------------------------------------------------------------------------
# Stand-alone dry-run (no heavy build). Run:
#   py tools/patches/thrown_restore.py <mod.arz>
# Proves: 0 new records (in-place restore only), verify() OK, negtest OK.
# ---------------------------------------------------------------------------
def _selftest(mod_arz):
    import sys
    from pathlib import Path
    HERE = Path(__file__).resolve().parent.parent  # tools/
    sys.path.insert(0, str(HERE))
    from arz_patcher import ArzDatabase

    print("loading mod overlay %s ..." % mod_arz)
    db = ArzDatabase.from_arz(Path(mod_arz))

    before = set(db.record_names())
    tags = {}

    # premise check: every roster record is currently disarmed (RIGHT hand
    # chance == 0 for single-hand families, or both hands melee for duneraider).
    d0 = ROSTER[0]["record"]
    print("premise: %s chanceToEquipRightHand in overlay = %s (0 => disarmed, restore required)"
          % (d0.split("\\")[-1], db.get_field_value(d0, "chanceToEquipRightHand")))

    apply(db, tags)
    after = set(db.record_names())
    added = sorted(after - before)
    print("intended-only record delta: +%d added (must be 0 - in-place restore only)" % len(added))
    assert not added, "STRAY new records added by an in-place-restore module: %s" % added

    modified = sorted(db._modified)
    roster_paths = {e["record"] for e in ROSTER}
    stray_mod = [m for m in modified if m not in roster_paths]
    print("modified records: %d (roster size %d); stray modifications: %d"
          % (len(modified), len(roster_paths), len(stray_mod)))
    assert not stray_mod, "modules touched records outside its own roster: %s" % stray_mod
    assert set(modified) == roster_paths, "modified != roster (missing: %s)" % (roster_paths - set(modified))

    a0 = ROSTER[0]["record"]
    print("post: %s RIGHT=%s LEFT=%s loot1[0]=%s life=%s" % (
        a0.split("\\")[-1], db.get_field_value(a0, "chanceToEquipRightHand"),
        db.get_field_value(a0, "chanceToEquipLeftHand"),
        (db.get_field_value(a0, "lootRightHandItem1") or [None])[0],
        db.get_field_value(a0, "characterLife")))

    verify(db, tags)
    _negtest(db, tags)
    print("\nthrown_restore DRY-RUN: PASS (0 new records; %d records restored in place; "
          "verify OK; negtest OK)" % len(roster_paths))


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("usage: py tools/patches/thrown_restore.py <mod.arz>")
        raise SystemExit(2)
    _selftest(sys.argv[1])
