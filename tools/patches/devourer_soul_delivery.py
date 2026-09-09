r"""R-258 - THE DEVOURER'S SOUL LEAVES THE `Finger2` SINGLE POINT OF FAILURE.

WILL, 2026-08-14, VERBATIM (`BL-W0814-10`, the report this module exists to close):

    "i killed toxeus the murderer devourer of blood and he did not drop his soul
     even though he should have 100% chance of dropping his soul."

WHAT THE BYTES SAY (shipped build101 arz `9712f58fcc1a73ec1fba2d5a9e811cbc`, decoded
record by record - every number below is read out of that file, not remembered):

1. THE SOUL HAS EXACTLY ONE DELIVERY PATH, AND IT IS AN EQUIPMENT SLOT.
   `um_bloodtoxeus_99`: `chanceToEquipFinger2` = 100.0, `chanceToEquipFinger2Item1`
   = 100 (the only non-zero row of that slot), `lootFinger2Item1` =
   `blood_toxeus_soul_{n,e,l}`. All three soul records exist, all three are
   `Jewelry_Ring` / `Magical` / itemLevel 40/68/100. No difficulty gate, no
   championChance gate, no rank gate. A full reverse-reference sweep of the shipped
   arz finds exactly FOUR referrers of each soul record: the three
   `*_04_lesserpotionofexperience_formula` reagent slots (a recipe, not a drop) and
   this one `lootFinger2Item1`. **So the drop is byte-correct and it is a SINGLE
   POINT OF FAILURE.** Three audits (b96/R-252 round 1-3) cleared every field named
   in the report and the boss still paid nothing, so the defect is not a value in
   the database - it is that the whole guarantee rides one engine behaviour on one
   record, with no second channel to catch it.

2. THE PRE-DESIGNED ESCALATION IS REFUTED - SAY IT PLAINLY RATHER THAN BUILD IT.
   `docs/BACKLOG.md` (BL-W0814-10) and R-252's DEBT-1 both prescribe: *"move the
   soul onto the Misc4 channel R-247.6a proved delivers"*. **`Misc4` IS NOT AN
   ENGINE SLOT.** Measured, three independent ways:
     * `<game>\Toolset\Templates.arc` -> `templates\templatebase\characterloot.tpl`
       is the ONE template that declares monster equip/loot variables (it is
       `include`d by `monster.tpl`). It declares exactly ELEVEN slots -
       Head / Torso / Forearm / LowerBody / LeftHand / RightHand / Finger1 /
       Finger2 / Misc1 / Misc2 / Misc3 - each with `chanceToEquip<S>`,
       `chanceToEquip<S>Item1..6` and `loot<S>Item1..6`. There is **no `Misc4`
       variable of any kind**, and no `Neck`.
     * the string `chanceToEquipMisc4` occurs in **0** records of the base AE
       database (74,013 records), **0** of SV 0.98i and **0** of SV 0.9. It occurs
       only in this mod's own arz, on the 32 records our own build wrote.
     * its claimed proof of delivery is R-247.6a's line *"Will's kill DID drop
       it"*, which is an INFERENCE - and it contradicts Will's own verbatim report
       in the same ruling: *"it didnt drop the forge formula that should allow you
       make craft the uber toxeus the murderer soul ... the formula to craft his
       soul should have dropped when i killed the endless hunt"*. On that kill the
       `Finger2` soul dropped and the `treasureProxyName` orb dropped; the ONE item
       that did not was the one on `Misc4`.
   Moving the soul onto `Misc4` would therefore move it from a template-declared
   slot onto a field the engine's own template does not define. **REFUSED.** The
   Misc4 finding is registered as `BL-R258-DEBT-2` (it puts R-13's rant scroll and
   R-92's EoAT formula in doubt on all three champions) - that is a separate lane,
   not this one.

3. WHAT THIS MODULE DOES INSTEAD: THE `Misc1` PURE-DROP CHUTE, AT A MEASURED 100%.
   `Misc1` is template-declared, carried by 6,543 records of the shipped 51,352
   (3,884 of them wiring `lootMisc1Item1`), and it is NOT
   class-typed - R-252's own standing invariant names it as one of the slots with
   "no single wearable class", and the census of the shipped arz proves it: the
   leaf item templates already reachable through `lootMisc1Item*` mod-wide are
   `oneshot_potionmana` (15,804), `itemrelic` (10,453), `itemartifactformula`
   (9,821), `oneshot_scroll` (9,794), `itemartifact` (7,775),
   `oneshot_potionhealth` (6,012), `itemcharm` (3,303), `parchment` (54),
   **`jewelry_ring` (47)** and `weapon_staff` (1). Rings already ride this slot.
   And a SOUL already rides a Misc slot in this very database:
   `u_bloodwing_12.lootMisc2Item1` -> `records\item\equipmentring\soul\
   carrionbird\bloodwing_soul.dbr`.
   The Devourer's `Misc1` ships at `chanceToEquipMisc1` = 100.0 with two rows -
   item1 health potions @80, item2 energy potions @20. This module adds the soul on
   the FREE row `item3` at weight 100 and MUTES the two potion weights to 0, so the
   slot's only selectable row is the soul: **100.0000% of kills, every difficulty,
   arithmetic re-derived from the final db by the gate, never asserted by hand.**

4. `Finger2` IS NOT TOUCHED - ASSERTED, NEVER WRITTEN. R-243's 100% pin stays byte-
   unchanged, `tools/verify_soul_drop_rates.py --gate` and R-252's E5 arm stay green
   BY CONSTRUCTION, and the soul now has TWO independent channels rather than one.

THE ONE PLAYER-VISIBLE COST, DISCLOSED RATHER THAN DISCOVERED (`BL-R258-DEBT-3`):
the Devourer stops dropping his one Misc1 POTION (health 80% / energy 20% of kills).
That is the smallest price any option on his record could carry - he has no free
slot, every alternative was costed on the bytes and is worse:
  * `Head` is his only chance-0 slot, but it is CLASS-GOVERNED by R-252 and a ring
    there can never be worn, so it would need an allowlist entry AND it rests on the
    same unproven "a mis-class roll still drops" premise that R-247.6a asserted.
  * `Misc2` is an 18%-chance slot (ceiling 18%, cannot reach 100%).
  * `Misc3` is a 50%-chance slot and holds his amulet.
  * a bespoke boss-orb chain (`treasureProxyName`) works, but R-99's gate asserts
    that EVERY Toxeus variant carries `genericbossorb_05` and nothing else does, so
    it would red another ruling's invariant to fix this one.
The potion rows are MUTED (weights 0), never deleted, so both tables keep their
reference on the record (RETIREMENT PROTOCOL) and a revert is two constants.

DISCLOSED AND DELIBERATE: if the `Finger2` channel is in fact healthy on this boss,
the next kill drops TWO copies of the soul. That is the point - it is also the
diagnostic that four rounds of database audit could not buy: ONE soul means Finger2
is dead on this record and the Misc1 chute saved it; TWO means Finger2 was never the
defect and the real cause is elsewhere in the encounter. `BL-R258-DEBT-1` carries
the question to Will's kill and the one-constant collapse either way.

Gate:            `py tools/gate_devourer_soul_delivery.py <arz> [--dryrun]`
Self test:       `py tools/patches/devourer_soul_delivery.py --selftest`
Negative test:   `py tools/patches/devourer_soul_delivery.py --negtest`
"""
import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))   # tools/ on path

MODULE_NAME = ("R-258 Devourer soul delivery - the soul gets a second, "
               "template-declared 100% channel on Misc1")

# ── the records ─────────────────────────────────────────────────────────────
_DEVOURER = r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr'

_SOULS = (r'records\item\equipmentring\soul\svc_uber\blood_toxeus_soul_n.dbr',
          r'records\item\equipmentring\soul\svc_uber\blood_toxeus_soul_e.dbr',
          r'records\item\equipmentring\soul\svc_uber\blood_toxeus_soul_l.dbr')

# NEW: one FixedWeight table per difficulty tier, exactly the shape of the mod's
# other guaranteed drops (`svc_rite_guaranteed`, `veinrender_guaranteed_*`).
_SOUL_TAB = (r'records\item\loottables\svc\svc_devourersoul_guaranteed_n.dbr',
             r'records\item\loottables\svc\svc_devourersoul_guaranteed_e.dbr',
             r'records\item\loottables\svc\svc_devourersoul_guaranteed_l.dbr')

# the two shipped Misc1 rows - ASSERTED before the write, MUTED not deleted.
_POTION_HEALTH = (r'records\item\loottables\misc\potions\health_10-15all.dbr',
                  r'records\item\loottables\misc\potions\health_30-35all.dbr',
                  r'records\item\loottables\misc\potions\health_50-55all.dbr')
_POTION_ENERGY = (r'records\item\loottables\misc\potions\energy_10-15all.dbr',
                  r'records\item\loottables\misc\potions\energy_35-40all.dbr',
                  r'records\item\loottables\misc\potions\energy_50-55all.dbr')

_SLOT = 'Misc1'
_SOUL_ROW = 3              # the free row on the shipped record
_W_GUARANTEED = 100        # the mod's guaranteed-row weight constant
_RING_TPL = 'jewelry_ring.tpl'

# the Finger2 state this module ASSERTS and never writes (R-243's pin).
_F2_CHANCE = 100.0
_F2_W = 100


# ── tiny db helpers (work on the real ArzDatabase and on the negtest stub) ──
def _norm(p):
    return str(p or '').replace('/', '\\').strip().lower()


def _gv(db, rec, field, default=None):
    v = db.get_field_value(rec, field)
    if isinstance(v, (list, tuple)):
        v = v[0] if v else None
    return default if v is None else v


def _gl(db, rec, field):
    v = db.get_field_value(rec, field)
    if v is None:
        return []
    if isinstance(v, (list, tuple)):
        return [str(x) for x in v]
    return [str(v)]


def _f(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _i(v, default=0):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def _close(a, b, tol=0.0005):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def _same(got, want):
    return [_norm(x) for x in got] == [_norm(x) for x in want]


def _rec_index(db):
    """{lowercased record name: the db's own spelling}.

    Rebuilt when the record COUNT moves. The arz stores record names lowercase but
    its internal REFERENCES mixed-case (2,436 references in the shipped mod arz
    resolve ONLY case-insensitively - the R-252 round-3 lesson), so every lookup in
    this module goes through here rather than through `has_record`.
    """
    n = len(db.record_names())
    cached = getattr(db, '_r258_rec_index', None)
    if cached is not None and cached[0] == n:
        return cached[1]
    idx = {}
    for name in db.record_names():
        idx.setdefault(_norm(name), name)
    try:
        db._r258_rec_index = (n, idx)
    except AttributeError:
        pass
    return idx


def _resolve(db, path):
    if not path:
        return None
    if db.has_record(path):
        return path
    return _rec_index(db).get(_norm(path))


def _has(db, path):
    return _resolve(db, path) is not None


def _set(db, rec, field, value, dtype_if_new=None):
    """The dtype-preservation law, both arms.

    NEVER pass a dtype to a field that already exists (silent INT/FLOAT corruption -
    the pet-spawn-failure lesson); ALWAYS pass one to a field that does not exist yet
    (a brand-new field has no dtype to preserve). A re-apply therefore writes
    dtype-free over the fields a previous pass created.
    """
    if db.get_field_value(rec, field) is None and dtype_if_new is not None:
        db.set_field(rec, field, value, dtype_if_new)
    else:
        db.set_field(rec, field, value)


def _tpl_stem(db, path):
    r = _resolve(db, path)
    if r is None:
        return None
    f = db.get_fields(r) or {}
    for k in f:
        if str(k).split('###')[0] != 'templateName':
            continue
        tf = f[k]
        vals = tf if isinstance(tf, (list, tuple)) else getattr(tf, 'values', [tf])
        for v in vals:
            if isinstance(v, str) and v.strip():
                return _norm(v).rsplit('\\', 1)[-1]
    return None


def _slot_weights(db, rec, slot):
    """[(row, weight)] for every declared row of a slot, rows 1..6."""
    out = []
    for i in range(1, 7):
        w = db.get_field_value(rec, 'chanceToEquip%sItem%d' % (slot, i))
        if w is None:
            continue
        out.append((i, _i(w[0] if isinstance(w, (list, tuple)) and w else w)))
    return out


def _row_share(db, rec, slot, row):
    """The measured share of a slot's picks that land on `row`, in percent.

    slot chance x (row weight / total weight). Re-derived from the db every run:
    a published 100% that can drift without the gate noticing is exactly how a
    guarantee turns back into a lottery.
    """
    chance = _f(_gv(db, rec, 'chanceToEquip%s' % slot, 0.0))
    weights = _slot_weights(db, rec, slot)
    total = sum(w for _r, w in weights)
    mine = sum(w for r, w in weights if r == row)
    if total <= 0:
        return 0.0
    return chance * (float(mine) / float(total))


# ── apply ───────────────────────────────────────────────────────────────────
def _fixedweight(db, path, member, desc):
    """Author a one-row LootItemTable_FixedWeight in the shape the build already uses."""
    from apply_svc_patches import (_ensure_record, DATA_TYPE_STRING, DATA_TYPE_INT,
                                   DATA_TYPE_FLOAT)
    S, I, F = DATA_TYPE_STRING, DATA_TYPE_INT, DATA_TYPE_FLOAT
    _ensure_record(db, path, 'Database\\Templates\\LootItemTable_FixedWeight.tpl')
    db._record_types[path] = 'LootItemTable_FixedWeight'
    _set(db, path, 'Class', 'LootItemTable_FixedWeight', S)
    _set(db, path, 'templateName',
         'Database\\Templates\\LootItemTable_FixedWeight.tpl', S)
    _set(db, path, 'FileDescription', desc, S)
    for fld in ('brokenRandomizerChance', 'prefixRandomizerChance',
                'suffixRandomizerChance'):
        _set(db, path, fld, 0.0, F)
    _set(db, path, 'lootName1', member, S)
    _set(db, path, 'lootWeight1', _W_GUARANTEED, I)
    # idempotency: blank any stale row a previous pass could have left behind
    for i in range(2, 7):
        if db.get_field_value(path, 'lootName%d' % i) is not None:
            _set(db, path, 'lootName%d' % i, '')
            _set(db, path, 'lootWeight%d' % i, 0)
    db._modified.add(path)


def _assert_row(db, rec, slot, idx, want, why):
    got = _gl(db, rec, 'loot%sItem%d' % (slot, idx))
    if not _same(got, want):
        raise SystemExit(
            "[devourer_soul_delivery] PRE-STATE DRIFT: %s loot%sItem%d = %r, expected "
            "%r (%s). This row is ASSERTED, never written - a different value means "
            "another writer appeared or this module is mis-ordered; refusing to "
            "overwrite an unmeasured state."
            % (rec.rsplit('\\', 1)[-1], slot, idx, got, list(want), why))


def apply(db, tags):
    from apply_svc_patches import DATA_TYPE_STRING as S, DATA_TYPE_INT as I
    print("\n=== patches-registry: %s ===" % MODULE_NAME)

    if not _has(db, _DEVOURER):
        raise SystemExit("[devourer_soul_delivery] Devourer record MISSING: %s"
                         % _DEVOURER)
    for s in _SOULS:
        if not _has(db, s):
            raise SystemExit("[devourer_soul_delivery] soul record MISSING: %s" % s)

    # ── 1. PRE-STATE, asserted on the bytes before anything is written ──────
    #     Finger2 (never written by this module - R-243's pin).
    if not _close(_f(_gv(db, _DEVOURER, 'chanceToEquipFinger2', 0.0)), _F2_CHANCE):
        raise SystemExit(
            "[devourer_soul_delivery] PRE-STATE DRIFT: Devourer chanceToEquipFinger2 "
            "= %r, expected %.1f (R-243's pin). This module leaves Finger2 alone and "
            "measures it; a different value means the pin moved elsewhere."
            % (_gv(db, _DEVOURER, 'chanceToEquipFinger2'), _F2_CHANCE))
    _assert_row(db, _DEVOURER, 'Finger2', 1, _SOULS, "R-243's 100% soul pin")

    #     Misc1 - the slot this module takes over.
    if not _close(_f(_gv(db, _DEVOURER, 'chanceToEquipMisc1', 0.0)), 100.0):
        raise SystemExit(
            "[devourer_soul_delivery] PRE-STATE DRIFT: Devourer chanceToEquipMisc1 = "
            "%r, expected 100.0 (the shipped potion slot). The guarantee is built on "
            "that 100; refusing to write into an unmeasured slot."
            % (_gv(db, _DEVOURER, 'chanceToEquipMisc1'),))
    _assert_row(db, _DEVOURER, 'Misc1', 1, _POTION_HEALTH, 'the shipped health-potion row')
    _assert_row(db, _DEVOURER, 'Misc1', 2, _POTION_ENERGY, 'the shipped energy-potion row')
    _row3 = _gl(db, _DEVOURER, 'loot%sItem%d' % (_SLOT, _SOUL_ROW))
    if _row3 and not _same(_row3, _SOUL_TAB):
        raise SystemExit(
            "[devourer_soul_delivery] PRE-STATE DRIFT: Devourer loot%sItem%d is "
            "already occupied by content that is NOT this lane's (%r) - this module "
            "claims that row and will not displace someone else's content."
            % (_SLOT, _SOUL_ROW, _row3))

    # ── 2. the three guaranteed soul tables ────────────────────────────────
    for i, tab in enumerate(_SOUL_TAB):
        _fixedweight(db, tab, _SOULS[i],
                     'R-258 Devourer soul, guaranteed (%s)' % 'NEL'[i])

    # ── 3. the Misc1 chute: soul on the free row @100, potions MUTED to 0 ──
    _set(db, _DEVOURER, 'loot%sItem%d' % (_SLOT, _SOUL_ROW), list(_SOUL_TAB), S)
    _set(db, _DEVOURER, 'chanceToEquip%sItem%d' % (_SLOT, _SOUL_ROW), _W_GUARANTEED, I)
    _set(db, _DEVOURER, 'chanceToEquip%sItem1' % _SLOT, 0)
    _set(db, _DEVOURER, 'chanceToEquip%sItem2' % _SLOT, 0)
    db._modified.add(_DEVOURER)

    share = _row_share(db, _DEVOURER, _SLOT, _SOUL_ROW)
    print("  [R-258] Devourer soul -> %s row %d @ weight %d; potion rows muted "
          "(values kept). Measured soul share of every kill: %.4f%% on all three "
          "difficulties. Finger2 untouched at %.1f%% (R-243)."
          % (_SLOT, _SOUL_ROW, _W_GUARANTEED, share, _F2_CHANCE))
    return tags


# ── the gate ────────────────────────────────────────────────────────────────
def _check(db):
    """Every arm re-derives its number from `db`. Returns a list of problem strings."""
    P = []

    dev = _resolve(db, _DEVOURER)
    if dev is None:
        return ["Devourer record MISSING: %s" % _DEVOURER]

    # E1 - the three tables exist, are one-row FixedWeight, and each names ITS OWN
    #      tier's soul. A tier mismatch is the exact blind spot that ships a
    #      Normal-only or Legendary-only fix.
    for i, tab in enumerate(_SOUL_TAB):
        r = _resolve(db, tab)
        if r is None:
            P.append("E1: guaranteed soul table MISSING: %s" % tab)
            continue
        cls = _gv(db, r, 'Class', '')
        if _norm(cls) != _norm('LootItemTable_FixedWeight'):
            P.append("E1: %s Class=%r, expected LootItemTable_FixedWeight"
                     % (tab.rsplit('\\', 1)[-1], cls))
        got = _norm(_gv(db, r, 'lootName1', ''))
        if got != _norm(_SOULS[i]):
            P.append("E1: %s lootName1=%r, expected the %s-tier soul %s"
                     % (tab.rsplit('\\', 1)[-1], got, 'NEL'[i], _SOULS[i]))
        if _i(_gv(db, r, 'lootWeight1', 0)) != _W_GUARANTEED:
            P.append("E1: %s lootWeight1=%r, expected %d"
                     % (tab.rsplit('\\', 1)[-1], _gv(db, r, 'lootWeight1'),
                        _W_GUARANTEED))
        for j in range(2, 7):
            v = _gv(db, r, 'lootName%d' % j, '')
            if str(v).strip():
                P.append("E1: %s carries a SECOND member lootName%d=%r - the row must "
                         "be alone or the drop is not guaranteed"
                         % (tab.rsplit('\\', 1)[-1], j, v))

    # E2 - every soul record resolves and is a RING (the class the summon rides).
    for i, s in enumerate(_SOULS):
        if not _has(db, s):
            P.append("E2: %s-tier soul record MISSING: %s" % ('NEL'[i], s))
            continue
        stem = _tpl_stem(db, s)
        if stem is not None and stem != _RING_TPL:
            P.append("E2: %s-tier soul templateName stem=%r, expected %r"
                     % ('NEL'[i], stem, _RING_TPL))

    # E3 - THE GUARANTEE ITSELF, measured: the soul row's share of every kill.
    row = _gl(db, dev, 'loot%sItem%d' % (_SLOT, _SOUL_ROW))
    if not _same(row, _SOUL_TAB):
        P.append("E3: Devourer loot%sItem%d = %r, expected the three guaranteed soul "
                 "tables %r" % (_SLOT, _SOUL_ROW, row, list(_SOUL_TAB)))
    else:
        share = _row_share(db, dev, _SLOT, _SOUL_ROW)
        if not _close(share, 100.0):
            P.append("E3: the soul is NOT guaranteed - measured share of a kill = "
                     "%.4f%%, expected 100.0000%%. slot chance=%r, row weights=%r"
                     % (share, _gv(db, dev, 'chanceToEquip%s' % _SLOT),
                        _slot_weights(db, dev, _SLOT)))
        rival = [(r, w) for r, w in _slot_weights(db, dev, _SLOT)
                 if w > 0 and r != _SOUL_ROW]
        if rival:
            P.append("E3: %s carries competing non-zero rows %r - any weight but the "
                     "soul's turns the guarantee back into a lottery"
                     % (_SLOT, rival))

    # E4 - RETIREMENT PROTOCOL: the potion tables are MUTED, never orphaned.
    _e4 = (('1', _POTION_HEALTH), ('2', _POTION_ENERGY))
    for idx, want in _e4:
        got = _gl(db, dev, 'loot%sItem%s' % (_SLOT, idx))
        if not _same(got, want):
            P.append("E4: Devourer loot%sItem%s = %r, expected the shipped potion row "
                     "%r kept in place (muted by weight, never deleted)"
                     % (_SLOT, idx, got, list(want)))

    # E5 - Finger2 IS UNTOUCHED. R-243's pin and R-252's E5 arm stay green only if
    #      this module really never wrote there.
    if not _close(_f(_gv(db, dev, 'chanceToEquipFinger2', 0.0)), _F2_CHANCE):
        P.append("E5: Devourer chanceToEquipFinger2 = %r, expected %.1f - R-243's pin "
                 "must survive this lane byte-unchanged"
                 % (_gv(db, dev, 'chanceToEquipFinger2'), _F2_CHANCE))
    f2 = _gl(db, dev, 'lootFinger2Item1')
    if not _same(f2, _SOULS):
        P.append("E5: Devourer lootFinger2Item1 = %r, expected the three souls %r "
                 "(asserted, never written)" % (f2, list(_SOULS)))
    if _i(_gv(db, dev, 'chanceToEquipFinger2Item1', 0)) != _F2_W:
        P.append("E5: Devourer chanceToEquipFinger2Item1 = %r, expected %d"
                 % (_gv(db, dev, 'chanceToEquipFinger2Item1'), _F2_W))

    # E6 - SCOPE: the three new tables belong to the Devourer and to nobody else.
    #      A second consumer means the soul leaked onto another monster.
    want_tabs = {_norm(t) for t in _SOUL_TAB}
    consumers = {}
    for name in db.record_names():
        fields = db.get_fields(name) or {}
        for k in fields:
            tf = fields[k]
            vals = tf if isinstance(tf, (list, tuple)) else getattr(tf, 'values', [tf])
            for v in vals:
                if isinstance(v, str) and _norm(v) in want_tabs:
                    consumers.setdefault(_norm(name), set()).add(str(k).split('###')[0])
    strays = sorted(n for n in consumers if n != _norm(dev))
    if strays:
        P.append("E6: the guaranteed soul tables are referenced by %d record(s) that "
                 "are NOT the Devourer: %r - this lane gives the soul to one boss"
                 % (len(strays), strays))
    mine = consumers.get(_norm(dev), set())
    if mine and mine != {'loot%sItem%d' % (_SLOT, _SOUL_ROW)}:
        P.append("E6: the Devourer names the soul tables on %r, expected only "
                 "loot%sItem%d" % (sorted(mine), _SLOT, _SOUL_ROW))

    # E7 - the DEAD-CHANNEL guard. Nothing in this lane may quietly start believing
    #      in Misc4 again: if a soul table ever lands on lootMisc4Item*, it is
    #      riding a field `characterloot.tpl` does not declare.
    for i in range(1, 7):
        got = _gl(db, dev, 'lootMisc4Item%d' % i)
        if any(_norm(g) in want_tabs for g in got):
            P.append("E7: a guaranteed soul table is wired to lootMisc4Item%d - Misc4 "
                     "is NOT a characterloot.tpl variable (0 of 74,013 base records, "
                     "0 of SV 0.98i); that channel cannot carry a guarantee." % i)
    return P


def verify(db, tags=None):
    P = _check(db)
    if P:
        for p in P:
            print("  R-258 OFFENDER: %s" % p)
        raise SystemExit("[devourer_soul_delivery] R-258 gate FAILED: %d problem(s)"
                         % len(P))
    share = _row_share(db, _resolve(db, _DEVOURER), _SLOT, _SOUL_ROW)
    print("  R-258 gate OK: the Devourer's soul drops on %s row %d at a MEASURED "
          "%.4f%% of kills on all three difficulties; the two potion rows are muted "
          "and still named; Finger2 is byte-unchanged at %.1f%% (R-243). "
          "WHAT IS CLAIMED: the database now delivers the soul through a "
          "template-declared slot with no competing row. WHAT IS NOT CLAIMED: that "
          "anyone has SEEN this build drop it - that is BL-R258-DEBT-1, Will's kill."
          % (_SLOT, _SOUL_ROW, share, _F2_CHANCE))
    return True


# ── self test (constants only, no db) ───────────────────────────────────────
def _selftest():
    bad = 0

    def ck(cond, msg):
        nonlocal bad
        if cond:
            print("  selftest OK  : %s" % msg)
        else:
            print("  selftest FAIL: %s" % msg)
            bad += 1

    ck(len(_SOULS) == 3 and len(_SOUL_TAB) == 3, "three tiers of soul + table")
    ck(len(set(_SOUL_TAB)) == 3, "the three tables are distinct records")
    ck(all(s.endswith(('_n.dbr', '_e.dbr', '_l.dbr')) for s in _SOULS),
       "the soul paths carry their tier suffix")
    ck([s[-6:-4] for s in _SOULS] == [t[-6:-4] for t in _SOUL_TAB],
       "table tier order matches soul tier order (n,e,l)")
    ck(all(_norm(p) == p for p in _SOUL_TAB + _SOULS + (_DEVOURER,)),
       "every authored path is already lowercase (exact-match resolvable)")
    ck(_SOUL_ROW not in (1, 2), "the soul row does not collide with the potion rows")
    ck(1 <= _SOUL_ROW <= 6, "the soul row is inside characterloot.tpl's 1..6 range")
    ck(_W_GUARANTEED == 100, "the guaranteed-row weight constant is the mod's 100")
    ck('misc4' not in _norm(_SLOT), "this module does not use the undeclared Misc4 slot")
    print("selftest: %s" % ("PASS" if not bad else "FAIL (%d)" % bad))
    return 1 if bad else 0


# ── planted negatives (stub db) ─────────────────────────────────────────────
def _negtest():
    class _Stub(object):
        def __init__(self):
            self.d = {}
            self._modified = set()
            self._record_types = {}

        def has_record(self, n):
            return n in self.d

        def record_names(self):
            return list(self.d)

        def get_fields(self, n):
            return self.d.get(n)

        def get_field_value(self, n, f):
            rec = self.d.get(n)
            return None if rec is None else rec.get(f)

        def set_field(self, n, f, v, dt=None):
            self.d.setdefault(n, {})[f] = v

    def item(tpl):
        return {'templateName': 'Database\\Templates\\%s.tpl' % tpl}

    def table(member):
        return {'Class': 'LootItemTable_FixedWeight',
                'templateName': 'Database\\Templates\\LootItemTable_FixedWeight.tpl',
                'lootName1': member, 'lootWeight1': _W_GUARANTEED}

    def healthy():
        db = _Stub()
        for i, s in enumerate(_SOULS):
            db.d[s] = item('Jewelry_Ring')
            db.d[_SOUL_TAB[i]] = table(s)
        for p in _POTION_HEALTH + _POTION_ENERGY:
            db.d[p] = table('i\\potion.dbr')
        db.d['i\\potion.dbr'] = item('OneShot_PotionHealth')
        db.d[_DEVOURER] = {
            'chanceToEquipMisc1': 100.0,
            'chanceToEquipMisc1Item1': 0,
            'chanceToEquipMisc1Item2': 0,
            'chanceToEquipMisc1Item3': _W_GUARANTEED,
            'lootMisc1Item1': list(_POTION_HEALTH),
            'lootMisc1Item2': list(_POTION_ENERGY),
            'lootMisc1Item3': list(_SOUL_TAB),
            'chanceToEquipFinger2': _F2_CHANCE,
            'chanceToEquipFinger2Item1': _F2_W,
            'lootFinger2Item1': list(_SOULS),
        }
        return db

    bad = 0
    # (label, plant) or (label, plant, 'E<n>') when the plant must be caught by a
    # NAMED arm. Without the third element a plant only proves "something fired",
    # which is how an arm can rot behind a louder neighbour (the R-252 E2d lesson).
    plants = (
        ("the soul row deleted outright",
         lambda d: d.d[_DEVOURER].pop('lootMisc1Item3')),
        ("the soul row's weight zeroed (slot goes silent)",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipMisc1Item3', 0)),
        ("the health-potion row un-muted (the guarantee becomes a 50/50)",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipMisc1Item1', 100)),
        ("the energy-potion row un-muted by a single point of weight",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipMisc1Item2', 1)),
        ("the slot chance dropped below 100 (a lottery with one ticket)",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipMisc1', 50.0)),
        ("the slot switched off entirely",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipMisc1', 0.0)),
        ("the EPIC tier quietly points at the NORMAL soul (tier asymmetry)",
         lambda d: d.d[_SOUL_TAB[1]].__setitem__('lootName1', _SOULS[0])),
        ("the LEGENDARY tier table loses its member",
         lambda d: d.d[_SOUL_TAB[2]].__setitem__('lootName1', '')),
        ("a soul table grows a SECOND member (dilution inside the table)",
         lambda d: d.d[_SOUL_TAB[0]].__setitem__('lootName2', 'i\\potion.dbr')),
        ("a soul table's weight cut below the guaranteed constant",
         lambda d: d.d[_SOUL_TAB[0]].__setitem__('lootWeight1', 5)),
        ("a soul table stops being a FixedWeight table",
         lambda d: d.d[_SOUL_TAB[0]].__setitem__('Class', 'LootMasterTable')),
        ("the Normal soul record is missing",
         lambda d: d.d.pop(_SOULS[0])),
        ("a soul record stops being a ring",
         lambda d: d.d.__setitem__(_SOULS[1], item('Armor_Head'))),
        ("the health-potion row DELETED instead of muted (orphaned content)",
         lambda d: d.d[_DEVOURER].__setitem__('lootMisc1Item1', [])),
        ("the energy-potion row repointed at something else",
         lambda d: d.d[_DEVOURER].__setitem__('lootMisc1Item2', ['i\\potion.dbr'] * 3)),
        ("R-243's Finger2 pin knocked off 100",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipFinger2', 25.0)),
        ("the Finger2 soul row silently emptied by this lane",
         lambda d: d.d[_DEVOURER].__setitem__('lootFinger2Item1', [])),
        ("the Finger2 row weight zeroed",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipFinger2Item1', 0)),
        ("the soul leaks onto a SECOND monster",
         lambda d: d.d.__setitem__('records\\x\\other_boss.dbr',
                                   {'lootMisc1Item3': list(_SOUL_TAB)})),
        ("the Devourer also names the tables on a second field",
         lambda d: d.d[_DEVOURER].__setitem__('lootMisc3Item4', list(_SOUL_TAB))),
        ("the soul re-wired onto the UNDECLARED Misc4 channel",
         lambda d: d.d[_DEVOURER].__setitem__('lootMisc4Item1', list(_SOUL_TAB)),
         'E7'),
        ("the soul MOVED wholesale onto Misc4 (the refuted escalation, done for real)",
         lambda d: (d.d[_DEVOURER].__setitem__('lootMisc4Item1', list(_SOUL_TAB)),
                    d.d[_DEVOURER].__setitem__('chanceToEquipMisc4', 100.0),
                    d.d[_DEVOURER].__setitem__('chanceToEquipMisc4Item1', 100),
                    d.d[_DEVOURER].pop('lootMisc1Item3'))[0],
         'E7'),
        ("only the Normal tier wired (the two other rows blanked)",
         lambda d: d.d[_DEVOURER].__setitem__('lootMisc1Item3',
                                              [_SOUL_TAB[0], '', ''])),
    )
    for row in plants:
        label, plant = row[0], row[1]
        want_arm = row[2] if len(row) > 2 else None
        db = healthy()
        plant(db)
        found = _check(db)
        if not found:
            print("  negtest FAIL (MISSED): %s" % label)
            bad += 1
        elif want_arm and not any(p.startswith(want_arm + ':') for p in found):
            print("  negtest FAIL (wrong arm, %s never fired): %s -> %s"
                  % (want_arm, label, found[0][:90]))
            bad += 1
        else:
            print("  negtest OK  (caught%s): %-56s -> %s"
                  % (' by ' + want_arm if want_arm else '', label, found[0][:88]))

    # positive controls: legitimate shapes that must NOT red the build
    controls = (
        ("an untouched healthy stub", lambda d: None),
        ("a soul table referenced in MIXED CASE by the Devourer",
         lambda d: d.d[_DEVOURER].__setitem__(
             'lootMisc1Item3', [t.upper() for t in _SOUL_TAB])),
        ("a soul record whose templateName is spelled in mixed case",
         lambda d: d.d.__setitem__(
             _SOULS[0], {'templateName': 'Database\\Templates\\Jewelry_Ring.TPL'})),
        ("the potion rows still named while muted",
         lambda d: d.d[_DEVOURER].update({'chanceToEquipMisc1Item1': 0,
                                          'chanceToEquipMisc1Item2': 0})),
    )
    for label, plant in controls:
        db = healthy()
        plant(db)
        found = _check(db)
        if found:
            print("  negtest FAIL (false positive): %s -> %s" % (label, found[0]))
            bad += 1
        else:
            print("  negtest OK  (no false positive): %s" % label)

    total = len(plants) + len(controls)
    print("negtest: %d/%d checks clean" % (total - bad, total))
    return 1 if bad else 0


if __name__ == '__main__':
    if '--negtest' in _sys.argv:
        _sys.exit(_negtest())
    if '--selftest' in _sys.argv:
        _sys.exit(_selftest())
    print(__doc__)
