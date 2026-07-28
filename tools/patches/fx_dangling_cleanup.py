"""fx_dangling_cleanup - B-FX-DANGLING-1 + BLOODHOUND-DYINGFX hygiene sweep.

WHY THIS EXISTS (docs/BACKLOG.md P2 "B-FX-DANGLING-1", P0 CRASH PINNED block
"HYGIENE" line; docs/reports/b91_fx_dangling.md)
----------------------------------------------------------------------------
Two dangling-reference debts were filed off the build30 delta vet and the
2026-07-12 crash triage and then orphaned when their parent lanes moved on.
This module closes both, plus the one leftover the F3 supra-weapon fix left
behind, in the single place a roster-wide sweep belongs.

--- ITEM 1: the Chris\\UnarmedProjectile_FX01 particle refs -------------------

`Records\\SandBox\\Chris\\UnarmedProjectile_FX01.dbr` does not exist in the mod
arz, in the SV/DRX upstreams, or in the base-game database (proven against the
UNION of the built arz + `<TQAE>/Database/database.arz`: 92,311 record names,
0 hits; the whole `records\\sandbox\\` namespace ships 536 OTHER records, so
this is a genuinely missing sibling, not a missing namespace).

177 records reference it from `particleEffectName2` (177 slots) and
`particleEffectName3` (176 slots) = **353 dangling slots**, which is the "~353"
the BACKLOG entry counts. The affected set includes PLAYER content - the Earth
mastery's `drxflamesurge` + `drxvolcanicorb` (live + scroll + backup copies) -
so players lose an FX layer, and every slot is a permanent false positive in
`contracts_resources`.

**Why STRIP and not repoint (base-game absence parity).** Of the 177 records,
69 also exist in the stock TQAE database. In **69 of 69** the base-game copy has
`particleEffectName2` **ABSENT**, and in 68 of 68 `particleEffectName3` ABSENT
(0 carry the dangling ref, 0 carry any other value). So vanilla's shape for
these exact records is "no slot 2/3 at all": the SV/DRX overlay ADDED a ref to
an FX record that never shipped. Deleting the field restores byte-shape parity
with the game's own records. A repoint would invent an FX layer vanilla does
not have, and an empty-string ref is the B-TOXEUS-2 loader-abort class - both
rejected.

**Why the paired `particleEffectAttachPoint2/3` are DELIBERATELY KEPT.** The
BACKLOG entry proposed stripping them as "orphaned leftovers". The evidence
says otherwise: in the SAME 69 base-game records, `particleEffectAttachPoint2`
is **PRESENT** (69/69) and `particleEffectAttachPoint3` PRESENT (68/68) while
the Name slots are absent - i.e. an attach point with no name slot IS the
vanilla shape (731 such orphaned attach-point slots exist across the mod arz,
inherited straight from the base game). Stripping them would DEVIATE from base
parity, not restore it. This also matches the house precedent: the build30 F7a
fix on the 3 pcsafe clones stripped `particleEffectName2/3` and nothing else
(`apply_svc_patches._fix_wave30_render_and_refs`). The BACKLOG's attach-point
sub-item is therefore closed as REJECTED-BY-EVIDENCE, not silently dropped.

**F7a is superseded (BL-103 fix-upstream), and was measurably a no-op.** The 3
`pcsafe` records build30's F7a targets are B-SOUL-PROC-2 CLONES minted LATER in
the pipeline from their PLAIN sources - which still carry the dangling ref. The
build log proves both halves: F7a itself reports
`F7a pcsafe souls: stripped 0 dangling UnarmedProjectile_FX01 particle refs
(3 records)` (nothing to strip at its point in the run), and by the time the
registry reaches this module all 3 clones carry the ref. F7a therefore never
actually fixed anything; this sweep runs LAST over the FINAL assembled db and
fixes the whole class at its source. F7a is left in place as a documented,
harmless no-op safety net, and the re-mint count is printed every build so a
future reordering is never silent.

--- ITEM 2: BLOODHOUND-DYINGFX (6 summoned-bloodhound dyingFxPak refs) --------

Filed in the P0 crash block as "a real defect, NOT this crash". **Ground truth
on the current arz: ALREADY RESOLVED.** All 6 bloodhound bodies
(`b_bloodhound_33/34/35`, `c_bloodhound_40/42/44`) carry
`dyingFxPak = records\\drxcreatures\\bloodhound\\effects\\fxpak_deathfx_burst.dbr`,
which RESOLVES - it is exactly the repoint target the BACKLOG line names. A
roster-wide sweep finds **0 dangling `dyingFxPak` refs** anywhere in the arz
(the 7 that look dangling against the mod arz alone - 4 `boss_daemonbull_yaoguai_*`
and 3 `crowheroes\\zilla*` - all resolve in the base-game DB and are false
positives of a mod-only scan).

Since there is nothing left to repoint, this module ships the **permanent gate**
the debt never had: `verify()` fails the build loud if ANY record's `dyingFxPak`
stops resolving against the union. That converts a one-shot cleanup into an
invariant, so the class cannot silently return. A planted-regression negative
test lives in `tools/verify_fx_refs.py --self-test`.

--- ITEM 3: supra wep_spear bumpTexture (finishing build30 F3) ----------------

F3 repointed `records\\drxitem\\supra\\wep_spear.dbr` from the broken DRX mesh to
the base `Items\\EquipmentWeapon\\Spear\\Default\\RSpear14B.msh` and stripped its
DRX `baseTexture` (the DRX skin's UVs fit only the DRX mesh). It left the
sibling `bumpTexture = DRXtextures\\items\\supra\\skins\\wep_spearbmp.tex` behind
- the same DRX skin set, on a mesh that carries its own internal textures. It is
stripped here for the same reason and by the same mechanism, completing F3.

DETERMINISM / IDEMPOTENCE
-------------------------
The record sweep iterates `db.record_names()` in the arz's own stable order and
writes no wall-clock/random/hash-ordered data. A re-run finds 0 remaining
dangling Chris slots and strips nothing - the module is a fixed point.

SCOPE PROOF
-----------
`apply()` snapshots every record's full field-key set before and after its own
writes and `SystemExit`s unless the changed set is exactly the intended one
(the Chris-bearing records + wep_spear) and the only keys that changed are the
whitelisted ones. Nothing else in the arz can move under this module.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

MODULE_NAME = ("FX dangling-ref cleanup (B-FX-DANGLING-1 Chris particle slots + "
               "BLOODHOUND-DYINGFX gate + F3 spear bumpTexture)")

# The missing FX record (compare case/slash-insensitively).
_CHRIS_REF = r'records\sandbox\chris\unarmedprojectile_fx01.dbr'

# Only these field families are ever touched.
_NAME_PREFIX = 'particleEffectName'

# build30 F7a already stripped these three; listed so apply() can assert the two
# fixes agree instead of silently double-handling them.
_F7A_RECORDS = (
    r'records\skills\soulskills\pcsafe\arachne_venomspray.dbr',
    r'records\skills\soulskills\pcsafe\hero_sonicwave.dbr',
    r'records\skills\soulskills\pcsafe\yeti_sonicroar.dbr',
)

_SPEAR = r'records\drxitem\supra\wep_spear.dbr'
_SPEAR_STRIP = ('bumpTexture',)

# Fields whose values name another .dbr and must resolve (the dyingFxPak gate
# widened to the whole FX-reference family it belongs to).
_FX_REF_FIELDS = ('dyingFxPak',)


def _norm(s):
    return str(s).replace('/', '\\').lower().strip()


def _emitted_keys(fields):
    """Field bases this record will actually EMIT. `_encode_fields` omits a field
    whose `values` list is empty, so a key with no values is already absent from
    the built record - it must NOT count as present, or the scope proof compares
    two different things and every record that merely CARRIES an empty key reads
    as changed (the round-2 false-positive: 148 phantom 'unintended' records)."""
    return {k.split('###')[0] for k, tf in (fields or {}).items() if tf.values}


def _strip(db, rec, field_bases):
    """Delete fields from a record entirely (values=[] -> _encode_fields omits
    them -> ABSENT in the built record, never present-but-empty). This is
    apply_svc_patches._strip_record_fields' mechanism, re-stated locally so the
    module has no import-order coupling to the monolith."""
    fields = db.get_fields(rec)
    if not fields:
        return 0
    want = set(field_bases)
    n = 0
    for key, tf in fields.items():
        if key.split('###')[0] in want and tf.values:
            tf.values = []
            n += 1
    if n:
        db._modified.add(rec)
    return n


def _chris_name_slots(db, rec):
    """Base names of every particleEffectName<N> field on `rec` whose value is
    the dangling Chris ref. Returns [] for every clean record."""
    fields = db.get_fields(rec)
    if not fields:
        return []
    out = []
    for key, tf in fields.items():
        base = key.split('###')[0]
        if not base.startswith(_NAME_PREFIX):
            continue
        if not base[len(_NAME_PREFIX):].isdigit():
            continue
        if any(isinstance(v, str) and _norm(v) == _CHRIS_REF for v in tf.values):
            out.append(base)
    return sorted(set(out))


def apply(db, tags):
    names = list(db.record_names())

    # ── scope-proof snapshot: every record's EMITTED field-key set, before ──
    before = {n: _emitted_keys(db.get_fields(n)) for n in names}

    # ── ITEM 1: strip the dangling Chris particleEffectName<N> slots ────────
    targets = {}
    for n in names:
        slots = _chris_name_slots(db, n)
        if slots:
            targets[n] = slots
    if not targets:
        raise SystemExit(
            "fx_dangling_cleanup: expected the B-FX-DANGLING-1 Chris refs to be "
            "present before this module runs, found NONE. Either an earlier lane "
            "already fixed them (retire this module and close the BACKLOG item) "
            "or the sweep predicate broke - investigate, do not ignore.")

    n_slots = 0
    for rec, slots in sorted(targets.items()):
        n_slots += _strip(db, rec, slots)

    # F7a ORDERING FACT (measured, build b91 round 1). The 3 records build30's F7a
    # strips are B-SOUL-PROC-2 `pcsafe` CLONES, and the clone step re-mints them
    # from their still-dangling PLAIN sources AFTER F7a has run - so by the time
    # the registry reaches this module they carry the Chris ref again. F7a is
    # therefore a symptom patch on 3 records that the pipeline immediately undoes;
    # this sweep, running last over the FINAL assembled db, is the upstream fix
    # (BL-103). Reported loudly either way so a future reordering is never silent.
    reminted = sorted(r for r in _F7A_RECORDS
                      if _norm(r) in {_norm(t) for t in targets})
    print(f"  fx_dangling_cleanup: {len(reminted)}/{len(_F7A_RECORDS)} build30-F7a "
          f"pcsafe record(s) had been RE-MINTED with the dangling ref by the "
          f"B-SOUL-PROC-2 clone step after F7a ran; this sweep re-strips them "
          f"(F7a is now redundant, kept as a documented no-op safety net).")

    # ── ITEM 3: finish F3 - the leftover DRX skin companion on wep_spear ────
    n_spear = 0
    if db.has_record(_SPEAR):
        n_spear = _strip(db, _SPEAR, _SPEAR_STRIP)
    else:
        raise SystemExit(f"fx_dangling_cleanup: {_SPEAR} missing (F3 record).")

    # ── scope proof (roster-wide) ──────────────────────────────────────────
    expected = {_norm(r) for r in targets}
    if n_spear:
        expected.add(_norm(_SPEAR))
    moved = set()
    for n in names:
        # A stripped field keeps its KEY with values=[]; compare EMITTED shape
        # (what _encode_fields will actually write), on both sides.
        if _emitted_keys(db.get_fields(n)) != before[n]:
            moved.add(_norm(n))
    unexpected = sorted(moved - expected)
    missing = sorted(expected - moved)
    if unexpected or missing:
        raise SystemExit(
            "fx_dangling_cleanup SCOPE PROOF FAILED: "
            f"{len(unexpected)} unintended record(s) changed {unexpected[:10]}; "
            f"{len(missing)} intended record(s) did not change {missing[:10]}")

    print(f"  fx_dangling_cleanup: stripped {n_slots} dangling "
          f"UnarmedProjectile_FX01 particleEffectName slot(s) across "
          f"{len(targets)} record(s) (base-game absence parity; paired "
          f"particleEffectAttachPoint slots deliberately KEPT - vanilla ships "
          f"them orphaned); stripped {n_spear} leftover DRX skin field(s) on "
          f"wep_spear (finishes build30 F3). Scope proof: exactly "
          f"{len(moved)}/{len(names)} records changed, all intended.")


# ── the permanent gate (step 4, over the FINAL merged db) ───────────────────
def verify(db, tags):
    """Fail the build loud if (a) any Chris particle ref survived, or (b) ANY
    record's dyingFxPak stops resolving (the BLOODHOUND-DYINGFX invariant)."""
    names = list(db.record_names())
    union = {_norm(n) for n in names}

    # The base-game DB is the other half of the resolution universe. It is not
    # available in every build layout (scratch/determinism runs), so its absence
    # DOWNGRADES the dyingFxPak check to mod-only instead of skipping it - a
    # mod-authored dangling ref is still caught, and the loud note says which
    # mode ran (no silent skip; cf. B-GATE-HARDEN-1).
    base_seen = False
    try:
        from build_svc_database import BASE_DB_PATH_HINT  # optional hook
    except ImportError:
        BASE_DB_PATH_HINT = None
    base_path = None
    for cand in (BASE_DB_PATH_HINT,
                 r'C:\Program Files (x86)\Steam\steamapps\common'
                 r'\Titan Quest Anniversary Edition\Database\database.arz'):
        if cand and Path(cand).is_file():
            base_path = Path(cand)
            break
    if base_path is not None:
        try:
            from arz_patcher import ArzDatabase
            bdb = ArzDatabase.from_arz(base_path)
            union |= {_norm(n) for n in bdb.record_names()}
            base_seen = True
        except Exception as exc:      # noqa: BLE001 - never mask as a pass
            print(f"  [fx_dangling_cleanup] WARNING could not read the base-game "
                  f"DB for the resolution union ({exc}); running MOD-ONLY.")

    # (a) Chris refs must be gone.
    survivors = []
    for n in names:
        if _chris_name_slots(db, n):
            survivors.append(n)
    if survivors:
        raise SystemExit(
            f"fx_dangling_cleanup.verify FAIL: {len(survivors)} record(s) still "
            f"carry the dangling {_CHRIS_REF}: {survivors[:10]}")

    # (b) dyingFxPak must resolve everywhere (BLOODHOUND-DYINGFX invariant).
    dangling = []
    checked = 0
    for n in names:
        ff = db.get_fields(n)
        if not ff:
            continue
        for key, tf in ff.items():
            if key.split('###')[0] not in _FX_REF_FIELDS:
                continue
            for v in tf.values:
                if not isinstance(v, str) or not v.strip():
                    continue
                checked += 1
                if _norm(v) not in union:
                    dangling.append((n, key.split('###')[0], v))
    if dangling:
        raise SystemExit(
            "fx_dangling_cleanup.verify FAIL (BLOODHOUND-DYINGFX invariant): "
            f"{len(dangling)} dangling dyingFxPak ref(s): {dangling[:10]}")

    # (c) the 6 bloodhound bodies specifically still point at the burst pak.
    BURST = r'records\drxcreatures\bloodhound\effects\fxpak_deathfx_burst.dbr'
    hounds = sorted(n for n in names
                    if 'drxcreatures\\bloodhound\\' in _norm(n)
                    and _norm(n).split('\\')[-1].startswith(('b_bloodhound_',
                                                             'c_bloodhound_')))
    bad = [h for h in hounds if _norm(db.get_field_value(h, 'dyingFxPak')
                                      if not isinstance(
                                          db.get_field_value(h, 'dyingFxPak'), list)
                                      else (db.get_field_value(h, 'dyingFxPak')
                                            or [''])[0]) != _norm(BURST)]
    if len(hounds) != 6 or bad:
        raise SystemExit(
            "fx_dangling_cleanup.verify FAIL: expected exactly 6 summoned-"
            f"bloodhound bodies all on {BURST}; found {len(hounds)} "
            f"({[Path(h).name for h in hounds]}), off-target: {bad}")

    if _norm(db.get_field_value(_SPEAR, 'bumpTexture') or ''):
        raise SystemExit(
            "fx_dangling_cleanup.verify FAIL: wep_spear.bumpTexture came back "
            "(build30 F3 DRX-skin strip).")

    mode = 'union(mod+base)' if base_seen else 'MOD-ONLY (base DB unavailable)'
    print(f"  fx_dangling_cleanup.verify OK: 0 Chris particle refs remain; "
          f"{checked} dyingFxPak ref(s) all resolve [{mode}]; 6/6 summoned "
          f"bloodhounds on fxpak_deathfx_burst; wep_spear DRX skin fields absent")
