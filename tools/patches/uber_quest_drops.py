r"""tools/patches/uber_quest_drops.py - R-101 P0: our uber clones must not hand
out the QUEST ITEMS they inherited from the quest bosses they were cloned from.

WILL, VERBATIM (two reports, which is what turned this into a defect CLASS):

    "when you cloned the monster to create the Soul of the Unferried, you
     literally clone another monster in the game who is a quest monster who
     drops Charon's Oar, and now this monster is also dropping Charon's Oar."

    "Same thing with the Key of the Warden of Souls, that is now a farmable item
     from the uber boss you made that you cloned from the warden of souls, they
     now drop the key of the warden of souls which they should not"

MECHANISM: cloning a quest boss copies `perPartyMemberDropItemName`, the field
the base game uses to hand every party member a quest key / journal item. The
clone keeps pointing at the donor's quest item, so a unique, quest-GATING item
becomes farmable off a repeatable uber encounter.

=============================================================================
THE SWEEP - re-measured on THIS lane's own baseline, not taken on trust
=============================================================================
`py tools/debug/probe_quest_coupled_fields.py local/baseline_main.arz` against
the build from `main` (md5 6a3a491db546b603c52132237c40aa63, 51,124 records)
reproduces R-101 exactly:

  itemClassification==Quest records in DB : 62
  um_* records in DB                      : 611
  um_* carrying perPartyMemberDropItemName:  3   <- ALL 3 point at a Quest item

  our uber                                 leaked quest item
  um_charonform2_ferryman_99   ->  xsq12_charonsoar.dbr      (Charon's Oar)
  um_polisgaoler_99            ->  z_wardenofsoulskey.dbr    (Key of the Warden of Souls)
  um_polisgaoler_unbound_99    ->  z_wardenofsoulskey.dbr    (same key, NOT reported by
                                                              Will - found by the sweep)

Inbound census agrees from the other direction:
  xsq12_charonsoar   <- 5 holders: boss_charonform2_39/41/43 + testcharon01 (all
                        legitimate base-game Charon forms) + our uber.
  z_wardenofsoulskey <- 3 holders: xsecrethero_wardenofsouls_48 (legitimate) +
                        BOTH of our Gaolers.

MEASURED CORRECTION to R-101's wording: R-101 says clear the field "and any
matching chance field". There IS no matching chance field - `perPartyMemberDrop
Chance` is ABSENT (dtype None) on all three records. Nothing to clear; verify()
instead asserts it stays absent-or-zero, so a future re-add cannot sneak a
percentage-gated leak past the gate.

=============================================================================
THE DONORS ARE THE WHOLE RISK - and this module never touches them
=============================================================================
R-101: "Do NOT touch the donors - boss_charonform2_*, testcharon01 and
xsecrethero_wardenofsouls_48 must stay byte-identical, or the actual quests
break. That is the whole risk in this change and it must be proven, not
asserted."

Three independent proofs, all in this file plus the wave's record-diff:
  1. `apply()` records EXACTLY which records it wrote (`_TOUCHED`); `verify()`
     asserts no donor is in that set.
  2. `verify()` asserts every donor STILL carries its quest drop, with the exact
     expected item path - so the real quests provably still hand out their item.
  3. the wave's arz record-diff vs this same baseline must show the donors as
     unchanged (no MODIFIED entry) - a byte-level proof at the artifact.

=============================================================================
THE GATE (process law #4) - a ROSTER INVARIANT, not three named exceptions
=============================================================================
    No `um_*` record may carry a `perPartyMemberDropItemName` that resolves to
    an item with `itemClassification == Quest`.

Stated over the whole roster because the roster GROWS, and this defect class
arrived precisely because a clone was assumed safe. The field ITSELF is
legitimate, so the ban is quest-only: a non-quest per-party drop on an uber must
stay GREEN (planted as a must-stay-green negative).

`apply()` deliberately fixes the three MEASURED records by name rather than
data-driven-clearing whatever it finds: a 4th inherited leak must make the build
go RED and be looked at by a human, not be silently laundered.

WIDER SWEEP (R-101 asked for it "even where it changes nothing") - other
quest-shaped fields on our 611 ubers, reported, NOT changed by this module:
  * `DisplayAsQuestItem = 1` on 24 ubers. NOT a leak - on a creature record this
    is the minimap exclamation-marker rig (`uber_quest_markers`, R-100 #7), which
    Will explicitly ASKED to have on every uber. Left alone.
  * `quest = 1` on exactly 2 records - `um_polisgaoler_99` and
    `um_polisgaoler_unbound_99`, inherited from the quest boss
    `xsecrethero_wardenofsouls_48`. This is a genuine second inheritance from the
    same clone, and NO other uber in the DB carries it. It is NOT cleared here:
    flipping a monster's quest flag changes how the engine treats a live
    encounter (respawn/limit/tracking) and the Gaoler encounter is Will's, so it
    is a design call, not a mechanical fix. Registered as open DEBT
    (BL-R101-QUESTFLAG-1) and put back to Will. verify() PINS the current value
    so it cannot drift silently while the question is open.

Contract (tools/patches/README.md): MODULE_NAME + apply(db, tags) + verify.
"""

MODULE_NAME = ("Uber quest-item leaks (R-101): clear the inherited "
               "perPartyMemberDropItemName on our 3 quest-boss clones")

# ---------------------------------------------------------------------------
# THE MEASURED LEAK SET. Each row: our uber, the quest item it leaked, and the
# LEGITIMATE holders of that same item which must stay untouched.
# ---------------------------------------------------------------------------
_Q = r"records\xpack\quests\objects\items"
_CHARON = r"records\xpack\creatures\monster\bosses\02_charon"
_GIG = r"records\xpack\creatures\monster\gigantes"

LEAKS = [
    {
        # Will 2026-08-11 (the Golden Bough rework): this record path is FROZEN
        # but its CONTENTS are no longer Charon - `tools/patches/charon_rework.py`
        # rewrites it in place as "Ormenos, the Bough in Bloom" from the SV
        # hellflower, which carries no `perPartyMemberDropItemName` at all.
        # THIS ROW STAYS AND IS STILL LOAD-BEARING: charon_rework is registered
        # AFTER this module precisely so this clear still runs against the
        # pre-rework contents (apply() SystemExits if the field is already gone,
        # which is the correct alarm if the ordering is ever changed). After the
        # rework the field is absent rather than empty, which verify() accepts.
        # If charon_rework is reverted, this row is needed unchanged.
        "record": _CHARON + r"\um_charonform2_ferryman_99.dbr",
        "name_tag": "tagSVCMonsterOrmenosBloom",   # was tagSVCMonsterCharonFerryman
        "item": _Q + r"\xsq12_charonsoar.dbr",
        "item_label": "Charon's Oar",
        "reported_by_will": True,
    },
    {
        "record": _GIG + r"\um_polisgaoler_99.dbr",
        "name_tag": "tagSVCMonsterPolisGaoler",
        "item": _Q + r"\z_wardenofsoulskey.dbr",
        "item_label": "Key of the Warden of Souls",
        "reported_by_will": True,
    },
    {
        "record": _GIG + r"\um_polisgaoler_unbound_99.dbr",
        "name_tag": "tagSVCMonsterPolisGaolerUnbound",
        "item": _Q + r"\z_wardenofsoulskey.dbr",
        "item_label": "Key of the Warden of Souls",
        "reported_by_will": False,     # found by the sweep, not by play
    },
]

# The legitimate carriers of each leaked quest item. These drive the REAL
# quests; if any of them stops handing out its item the quest breaks. This
# module must never write to them, and verify() proves both halves.
DONORS = {
    _Q + r"\xsq12_charonsoar.dbr": [
        _CHARON + r"\boss_charonform2_39.dbr",
        _CHARON + r"\boss_charonform2_41.dbr",
        _CHARON + r"\boss_charonform2_43.dbr",
        _CHARON + r"\testcharon01.dbr",
    ],
    _Q + r"\z_wardenofsoulskey.dbr": [
        _GIG + r"\xsecrethero_wardenofsouls_48.dbr",
    ],
}

# The fields this module clears / pins. `perPartyMemberDropChance` is ABSENT on
# all three records (measured) - it is listed so verify() can prove it stays
# that way rather than assuming it.
_DROP_FIELD = "perPartyMemberDropItemName"
_CHANCE_FIELD = "perPartyMemberDropChance"

# WIDER-SWEEP pin: the inherited `quest` flag, reported to Will, NOT changed.
# verify() pins the CURRENT value so it cannot drift while the question is open.
_QUEST_FLAG_PINNED = {
    _GIG + r"\um_polisgaoler_99.dbr": 1,
    _GIG + r"\um_polisgaoler_unbound_99.dbr": 1,
}

# populated by apply(); read by verify() to prove no donor was written.
_TOUCHED = set()


def _norm(s):
    return str(s).replace("/", "\\").lower()


def _scalar(v):
    return v[0] if isinstance(v, list) and v else v


def _fv(fields, key):
    """Scalar value of `key` in a decoded field map (fast: no linear fallback
    scan on the common ABSENT case, which matters for the full-DB sweep)."""
    if not fields:
        return None
    tf = fields.get(key)
    if tf is None:
        for k, v in fields.items():
            if "###" in k and k.split("###")[0] == key:
                tf = v
                break
    return _scalar(tf.value) if tf is not None else None


def quest_item_paths(db):
    """Every record in the DB with itemClassification == Quest (lowercased)."""
    out = set()
    for n in db.record_names():
        v = _fv(db.get_fields(n), "itemClassification")
        if v and str(v).strip().lower() == "quest":
            out.add(_norm(n))
    return out


def scan_uber_quest_leaks(db):
    """(carriers, leaks) - the R-101 invariant, over the WHOLE roster.

    carriers = [(record, item)] for every `um_*` record with a per-party drop.
    leaks    = the subset whose item is itemClassification == Quest.
    """
    quest = quest_item_paths(db)
    carriers, leaks = [], []
    for n in db.record_names():
        if not _norm(n).split("\\")[-1].startswith("um_"):
            continue
        fields = db.get_fields(n)
        item = _fv(fields, _DROP_FIELD)
        if not item or not str(item).strip():
            continue
        carriers.append((n, str(item)))
        if _norm(item) in quest:
            leaks.append((n, str(item)))
    return carriers, leaks


# ---------------------------------------------------------------------------
def apply(db, tags):
    """Clear the inherited quest drop on the three MEASURED ubers. Nothing else
    is written - in particular no donor, no item record, no pool."""
    _TOUCHED.clear()
    for leak in LEAKS:
        rec = leak["record"]
        if not db.has_record(rec):
            raise SystemExit(
                "uber_quest_drops: %s is absent from the DB. It is one of the "
                "three MEASURED R-101 leaks and must exist by the time this "
                "module runs (registered after every boss-creating module). If "
                "the record was legitimately retired, retire its LEAKS row too "
                "- do not let the roster and the fix drift." % rec)
        cur = _scalar(db.get_field_value(rec, _DROP_FIELD))
        if cur is None:
            raise SystemExit(
                "uber_quest_drops: %s no longer carries %s at all. Something "
                "upstream already changed it; re-measure before assuming this "
                "module is still needed (probe_quest_coupled_fields.py)."
                % (rec, _DROP_FIELD))
        if _norm(cur) not in ("", _norm(leak["item"])):
            raise SystemExit(
                "uber_quest_drops: %s carries an UNEXPECTED per-party drop %r "
                "(measured: %r). Re-measure before clearing - the roster moved."
                % (rec, cur, leak["item"]))
        # existing STRING field -> value swap, no explicit dtype (clone-safe).
        # Same idiom the monolith uses to clear a record-reference string
        # (apply_svc_patches: itemSkillName / proxyPoolEquation -> '').
        db.set_field(rec, _DROP_FIELD, "")
        _TOUCHED.add(_norm(rec))


# ---------------------------------------------------------------------------
def verify(db, tags):
    """R-101's gate + the donor-safety proof."""
    errs = []

    def gv(rec, key):
        return _fv(db.get_fields(rec), key)

    # ---- 1. THE ROSTER INVARIANT (DB-wide, not 3 named exceptions) ---------
    carriers, leaks = scan_uber_quest_leaks(db)
    for rec, item in leaks:
        errs.append("QUEST-ITEM LEAK %s -> %s (itemClassification==Quest). No "
                    "um_* record may hand out a quest item: it makes a "
                    "quest-gating item farmable off a repeatable encounter "
                    "(R-101)." % (rec, item))

    # ---- 2. the three measured records are actually cleared ----------------
    for leak in LEAKS:
        rec = leak["record"]
        if not db.has_record(rec):
            errs.append("measured leak record %s missing" % rec)
            continue
        cur = gv(rec, _DROP_FIELD)
        if cur not in (None, "") and str(cur).strip():
            errs.append("%s still carries %s=%r (expected cleared)"
                        % (rec, _DROP_FIELD, cur))
        ch = gv(rec, _CHANCE_FIELD)
        if ch is not None and float(ch or 0) > 0:
            errs.append("%s grew a %s=%r - a percentage-gated quest drop is "
                        "still a quest drop" % (rec, _CHANCE_FIELD, ch))

    # ---- 3. DONOR SAFETY: not written, and still functional ----------------
    for item, donors in DONORS.items():
        for d in donors:
            if _norm(d) in _TOUCHED:
                errs.append("DONOR WRITTEN: this module wrote to %s. Donors "
                            "must stay byte-identical or the real quest breaks "
                            "(R-101)." % d)
            if not db.has_record(d):
                errs.append("donor %s vanished from the DB" % d)
                continue
            got = gv(d, _DROP_FIELD)
            if _norm(got) != _norm(item):
                errs.append("DONOR BROKEN: %s should still hand out %s, has %r. "
                            "The real quest would stop granting its item."
                            % (d, item, got))

    # ---- 4. WIDER-SWEEP PIN: the inherited quest flag, held for Will -------
    for rec, expected in _QUEST_FLAG_PINNED.items():
        if not db.has_record(rec):
            continue
        got = gv(rec, "quest")
        if got is None or int(float(got)) != expected:
            errs.append("%s quest flag drifted to %r (pinned at %r pending "
                        "Will's call - BL-R101-QUESTFLAG-1). If this was a "
                        "deliberate decision, update the pin AND the ruling."
                        % (rec, got, expected))

    if errs:
        raise SystemExit("uber_quest_drops.verify FAILED:\n  " + "\n  ".join(errs))

    n_donors = sum(len(v) for v in DONORS.values())
    print("  uber_quest_drops.verify: OK (%d um_* per-party-drop carriers in the "
          "DB, 0 pointing at a Quest item; %d measured leaks cleared; %d donors "
          "unwritten and still handing out their quest item; quest-flag pin held "
          "on %d record(s))"
          % (len(carriers), len(LEAKS), n_donors, len(_QUEST_FLAG_PINNED)))


# ---------------------------------------------------------------------------
# PLANTED NEGATIVES - both directions, per R-101.
# ---------------------------------------------------------------------------
def _negtest(db, tags):
    """Save/restore against the real db (a deepcopy of ~51k decoded records is
    minutes and gigabytes). Restoration is proved: verify() must be GREEN again
    at the end."""
    checks = 0

    def _case(pairs, mutate, label, expect_fail=True):
        nonlocal checks
        mod_before = set(db._modified)
        snap = [(r, k, db.get_field_value(r, k)) for r, k in pairs]
        mutate()
        try:
            verify(db, dict(tags))
            passed = True
        except SystemExit:
            passed = False
        finally:
            for r, k, old in snap:
                db.set_field(r, k, old if old is not None else "")
            db._modified.clear()
            db._modified.update(mod_before)
        if expect_fail and passed:
            raise SystemExit("negtest: expected verify FAIL for %s, but it PASSED" % label)
        if not expect_fail and not passed:
            raise SystemExit("negtest: expected verify PASS for %s, but it FAILED" % label)
        checks += 1

    # --- MUST RED: re-add each of the three leaks (R-101's own negative) ----
    for leak in LEAKS:
        _case([(leak["record"], _DROP_FIELD)],
              lambda l=leak: db.set_field(l["record"], _DROP_FIELD, l["item"]),
              "re-added quest drop %s on %s" % (leak["item_label"], leak["record"]))

    # --- MUST RED: the leak class on a DIFFERENT uber (roster invariant) ----
    other = r"records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr"
    if not db.has_record(other):
        raise SystemExit("negtest: %s absent - the roster-invariant negative "
                         "needs an uber outside the measured leak set" % other)
    _case([(other, _DROP_FIELD)],
          lambda: db.set_field(other, _DROP_FIELD, _Q + r"\xsq12_charonsoar.dbr"),
          "a DIFFERENT uber grew a quest per-party drop")

    # --- MUST RED: a donor stops handing out its quest item ----------------
    donor = DONORS[_Q + r"\xsq12_charonsoar.dbr"][0]
    _case([(donor, _DROP_FIELD)],
          lambda: db.set_field(donor, _DROP_FIELD, ""),
          "legit donor %s stripped of its quest drop" % donor)

    # --- MUST RED: the pinned wider-sweep quest flag drifts ----------------
    pinned = list(_QUEST_FLAG_PINNED)[0]
    _case([(pinned, "quest")],
          lambda: db.set_field(pinned, "quest", 0),
          "the pinned inherited quest flag flipped without a ruling")

    # --- MUST STAY GREEN: the field itself is LEGITIMATE -------------------
    # R-101 asks for this explicitly: "add a non-quest per-party drop to confirm
    # the gate does NOT fire on that (it must stay a quest-only ban, since the
    # field itself is legitimate)."
    #
    # It is planted on an uber OUTSIDE the measured leak set, because on one of
    # the three the separate "your measured fix is applied" assertion would fire
    # and the case would prove nothing about the quest-only ban.
    if not db.has_record(other):
        raise SystemExit("negtest: %s absent - no non-leak uber to plant the "
                         "must-stay-green case on" % other)
    nonquest_item = None
    for n in sorted(db.record_names()):          # sorted == deterministic pick
        if not _norm(n).startswith(_norm(r"records\item\equipmentring\soul\svc_uber")):
            continue
        cls = _fv(db.get_fields(n), "itemClassification")
        if cls and str(cls).strip().lower() != "quest":
            nonquest_item = n
            break
    if nonquest_item is None:
        raise SystemExit("negtest: could not find a NON-quest item to plant the "
                         "must-stay-green case with")
    _case([(other, _DROP_FIELD)],
          lambda: db.set_field(other, _DROP_FIELD, nonquest_item),
          "a NON-quest per-party drop (%s) on an uber" % nonquest_item,
          expect_fail=False)

    verify(db, dict(tags))
    print("  uber_quest_drops._negtest: OK (%d planted cases - 6 must-RED, "
          "1 must-stay-GREEN - and verify is GREEN again after full restore)" % checks)


# ---------------------------------------------------------------------------
# Stand-alone dry-run (no heavy build):
#   py tools/patches/uber_quest_drops.py <mod.arz>
# ---------------------------------------------------------------------------
def _selftest(mod_arz):
    import sys
    from pathlib import Path
    HERE = Path(__file__).resolve().parent.parent  # tools/
    sys.path.insert(0, str(HERE))
    from arz_patcher import ArzDatabase

    print("loading mod overlay %s ..." % mod_arz)
    db = ArzDatabase.from_arz(Path(mod_arz))
    tags = {}

    print("\n--- PRE-STATE (as SHIPPED) ---")
    carriers, leaks = scan_uber_quest_leaks(db)
    print("  um_* per-party-drop carriers: %d   QUEST-ITEM LEAKS: %d" % (len(carriers), len(leaks)))
    for rec, item in sorted(leaks):
        print("    LEAK %s -> %s" % (rec, item))
    print("  donors and what they hand out:")
    for item, donors in DONORS.items():
        for d in donors:
            print("    %s -> %s" % (d, db.get_field_value(d, _DROP_FIELD)))

    before = set(db.record_names())
    mod_before = set(db._modified)
    apply(db, tags)
    added = sorted(set(db.record_names()) - before)
    assert not added, "this module must add NO records, added: %s" % added
    wrote = sorted(set(db._modified) - mod_before)
    print("\nrecords written by apply(): %d" % len(wrote))
    for w in wrote:
        print("    ~ %s" % w)
    assert {_norm(w) for w in wrote} == {_norm(l["record"]) for l in LEAKS}, \
        "apply() wrote outside the measured leak set"

    print("\n--- POST-STATE ---")
    carriers, leaks = scan_uber_quest_leaks(db)
    print("  um_* per-party-drop carriers: %d   QUEST-ITEM LEAKS: %d" % (len(carriers), len(leaks)))
    print("  donors STILL hand out:")
    for item, donors in DONORS.items():
        for d in donors:
            print("    %s -> %s" % (d, db.get_field_value(d, _DROP_FIELD)))

    verify(db, tags)
    _negtest(db, tags)
    print("\nuber_quest_drops DRY-RUN: PASS (0 new records; %d cleared; donors "
          "untouched; verify OK; negtest OK)" % len(LEAKS))


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("usage: py tools/patches/uber_quest_drops.py <mod.arz>")
        raise SystemExit(2)
    _selftest(sys.argv[1])
