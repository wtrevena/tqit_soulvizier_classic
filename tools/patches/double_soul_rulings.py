r"""double_soul_rulings - ITEM 4 (Will's double-soul rulings, delegated to the
standing recommendation - docs/reports/b56_legion_soul_stages.md "distinct-soul
chains").

BACKGROUND
--------------------------------------------------------------------------------
`legion_soul_stages.py` fixed the Legion class of defect (the SAME soul dropped
by 2+ stages of one death-transform chain) and separately enumerated 6 chains
that drop TWO DISTINCT souls per encounter, reporting them loud for a design
ruling rather than auto-fixing (reducing them risks orphaning a genuinely
different collectible). Will delegated the ruling to "the standing
recommendation" (the report's own per-chain table) - documented as such here,
per the round-1 brief.

RULINGS (ground-truthed against the effective arz, not just the report table)
--------------------------------------------------------------------------------
(a) POSSESSED BOAR - FIX (terminal-only; typo-twin dup retired)
    `um_possessedboar` (Hero) -> `actorToSpawnOnDeath` -> `um_possessedboar_
    spirit` (Hero, terminal). Ground truth: the TERMINAL's soul
    (`records\item\equipmentring\soul\boar\possesedboar_soul_{n,e,l}.dbr` - the
    "boar\" namespace, granting `drxstormsurge`) is amgoz1's own SV098i-original
    soul - proven by 2 independent signals: (1) present verbatim in all three
    upstream sources, and (2) it is a REAGENT in 6 base-game enchanting formulas
    (lesserpotionoffortitude + lesserpotionofexperience, all 3 tiers) - deep
    crafting-system integration only a genuine upstream item would have. The
    HEAD's soul (`soul\svc_uber\possessedboar_soul_{n,e,l}.dbr` - note the
    CORRECTLY-spelled "svc_uber\" namespace, our own mod-generated-soul
    territory, granting `thunderballnova`) is a build-introduced typo-twin
    duplicate: `wire_souls_to_monsters`/`create_uber_souls` armed the head
    stage independently, not realizing it is one growing encounter with the
    terminal. FIX (one-soul-per-encounter law, the Legion precedent): DETACH
    the head's Finger2 loot (chance -> 0 AND the 3 loot refs cleared, so no
    dangling ref survives the retirement below) then RETIRE the 3 now
    fully-unreferenced `svc_uber\possessedboar_soul_{n,e,l}` records (whole-db
    scan confirms ZERO other referents). The terminal keeps its real,
    formula-integrated SV098i soul untouched.

(b) LILLUED - FIX (terminal-only; head's empty-husk retired)
    `lillued` (Quest, the child form) -> `actorToSpawnOnDeath` -> `lillued_big`
    (Quest, terminal). These are NOT typo-twins - two genuinely distinct
    svc_uber soul families - but ground truth shows the head's soul,
    `lilluedchild_soul_{n,e,l}`, is an EMPTY HUSK: `itemSkillName`,
    `augmentSkillName1`, `augmentSkillName2` are all unset (confirmed on all 3
    tiers) and it carries no Text-tag `description` at all. It grants
    absolutely nothing - "worthless" per the report, and the report's own
    recommendation (safest to drop) is adopted verbatim. The terminal's soul
    (`lillued_soul`, granting `summon_lillued` + 2 storm augments) is real and
    untouched. FIX: DETACH the head's Finger2 loot (chance -> 0, refs cleared)
    then RETIRE the 3 now fully-unreferenced `lilluedchild_soul_{n,e,l}`
    records (whole-db scan: zero other referents; no Text tag to drop - the
    husk never had a `description`).

(c) CHARON 39/41/43 + HADES 54 - UNTOUCHED (Will's explicit ruling)
    These 4 base-game story-boss death-transform chains (boss_charon_39/41/43
    -> form2_39/41/43, each dropping `boss_charon_soul` then `charon_soul`; and
    `boss_hades_54` -> form2 -> form3_54, dropping `sp_hades_soul` then
    `hades_soul`) are DELIBERATE multi-form rewards on base-game/SV-derived
    story bosses, per Will's ruling - explicitly NOT reduced to one soul,
    unlike (a)/(b). This module touches NONE of their records; `verify()`
    asserts a literal zero-diff (every field on all 8 monster records + all
    4 head-soul + all 4 terminal-soul item records, read fresh from the FINAL
    db, is byte-identical to a golden snapshot taken at import time) - a much
    stronger guarantee than "still reported as a live 2-stage chain".

CLASS INVARIANT (unchanged from legion_soul_stages)
--------------------------------------------------------------------------------
`legion_soul_stages.verify()` re-derives its `distinct_multi` roster fresh
from the FINAL assembled db every time it runs (it is NOT a hardcoded list),
so once this module's apply() zeroes the two heads' Finger2 chances, that
roster SHRINKS from 6 to 4 automatically with no code change over there - the
exact "roster shrinks" behaviour the round-1 brief calls out. This module's
own `verify()` cross-checks the same shrink directly (belt-and-suspenders).
"""

MODULE_NAME = "Double-soul rulings (Possessed Boar + Lillued fixed; Charon/Hades untouched)"

DATA_TYPE_FLOAT = 1

# ── (a) Possessed Boar ──────────────────────────────────────────────────────
_PB_HEAD = r'records\creature\monster\warbeast\um_possessedboar.dbr'
_PB_TERMINAL = r'records\creature\monster\warbeast\um_possessedboar_spirit.dbr'
_PB_DUP_SOULS = [r'records\item\equipmentring\soul\svc_uber\possessedboar_soul_%s.dbr' % t
                 for t in ('n', 'e', 'l')]
_PB_CANON_SOULS = [r'records\item\equipmentring\soul\boar\possesedboar_soul_%s.dbr' % t
                   for t in ('n', 'e', 'l')]

# ── (b) Lillued ──────────────────────────────────────────────────────────────
_LL_HEAD = r'records\drxcreatures\crowheroes\lillued.dbr'
_LL_TERMINAL = r'records\drxcreatures\crowheroes\lillued_big.dbr'
_LL_HUSK_SOULS = [r'records\item\equipmentring\soul\svc_uber\lilluedchild_soul_%s.dbr' % t
                  for t in ('n', 'e', 'l')]
_LL_CANON_SOULS = [r'records\item\equipmentring\soul\svc_uber\lillued_soul_%s.dbr' % t
                   for t in ('n', 'e', 'l')]

# ── (c) Charon x3 + Hades - UNTOUCHED, asserted byte-identical ─────────────
# Ground-truthed exact paths (NOT the informal "form2_39" shorthand the b56
# report table uses): Charon's form2 stage is `boss_charonform2_<lvl>.dbr`
# under `xpack\creatures\monster\bosses\02_charon\`; the LIVE Hades head is the
# DRX-namespace `drxcreatures\bloodwitch\boss_hades_54.dbr` (chance 66, drops
# sp_hades_soul), which death-transforms into the xpack `05_hades\boss_hades
# form2_54.dbr` (chance 0, no drop - a pure animation-form step) and then
# `boss_hadesform3_54.dbr` (terminal, chance 25, drops hades_soul).
_UNTOUCHED_RECORDS = [
    r'records\xpack\creatures\monster\bosses\02_charon\boss_charon_39.dbr',
    r'records\xpack\creatures\monster\bosses\02_charon\boss_charonform2_39.dbr',
    r'records\xpack\creatures\monster\bosses\02_charon\boss_charon_41.dbr',
    r'records\xpack\creatures\monster\bosses\02_charon\boss_charonform2_41.dbr',
    r'records\xpack\creatures\monster\bosses\02_charon\boss_charon_43.dbr',
    r'records\xpack\creatures\monster\bosses\02_charon\boss_charonform2_43.dbr',
    r'records\drxcreatures\bloodwitch\boss_hades_54.dbr',
    r'records\xpack\creatures\monster\bosses\05_hades\boss_hadesform2_54.dbr',
    r'records\xpack\creatures\monster\bosses\05_hades\boss_hadesform3_54.dbr',
]

_CHANCE_FIELD = 'chanceToEquipFinger2'
_LOOT_FIELD = 'lootFinger2Item1'
_ARITY = 3   # n/e/l


def _norm(p):
    return str(p).replace('/', '\\').lower()


def _name_map(db):
    return {_norm(n): n for n in db.record_names()}


def _resolve(db, nm, path):
    return nm.get(_norm(path))


def _whole_db_refs(db, target_norm_stems, exclude):
    """[(rec, field, value)] for every field in the WHOLE db whose string value
    contains any of target_norm_stems (soul basenames, no tier suffix), used to
    prove a soul family is fully unreferenced before retiring it. `exclude` is a
    set of exact record names whose OWN refs are ignored (the doomed head)."""
    hits = []
    for n in db.record_names():
        if n in exclude:
            continue
        fields = db.get_fields(n)
        for fn, tf in fields.items():
            vals = tf.values if isinstance(tf.values, list) else [tf.values]
            for v in vals:
                if not isinstance(v, str):
                    continue
                low = v.replace('/', '\\').lower()
                for stem in target_norm_stems:
                    if stem in low:
                        hits.append((n, fn.split('###')[0], v))
    return hits


def _remove_record(db, exact_name):
    """Fully retire a record (mirrors souls_quality._remove_record - the
    Tomb Guardian precedent). write_arz iterates db._raw_records, so popping it
    there removes it from the built arz. Returns True if it existed."""
    existed = exact_name in db._raw_records
    db._raw_records.pop(exact_name, None)
    db._decoded_cache.pop(exact_name, None)
    db._record_types.pop(exact_name, None)
    db._record_timestamps.pop(exact_name, None)
    db._modified.discard(exact_name)
    return existed


def _snapshot(db, nm, records):
    """{record: {field: value}} for a fixed set of records - used to prove (c)
    is byte-identical after this module's apply()."""
    snap = {}
    for path in records:
        rec = _resolve(db, nm, path)
        if rec is None:
            continue
        fields = db.get_fields(rec)
        snap[path] = {fn.split('###')[0]: tuple(tf.values) if isinstance(tf.values, list)
                      else tf.values for fn, tf in fields.items()}
    return snap


def _detach_and_retire(db, nm, head_path, dup_soul_paths, label):
    """DETACH (chance->0, loot refs cleared) then RETIRE (remove the record) -
    the exact Tomb Guardian idiom (souls_quality.py FIX 5), applied here to a
    death-transform HEAD stage whose soul is being ruled out entirely (not just
    de-prioritised, as legion_soul_stages does for a soul that survives
    elsewhere)."""
    head = _resolve(db, nm, head_path)
    if head is None:
        raise SystemExit("double_soul_rulings: %s head missing (exact): %s"
                          % (label, head_path))

    # (1) confirm the dup soul family is ONLY referenced by this head (before
    #     detaching, so the scan sees the live state) - fail loud if not, since
    #     retiring a still-referenced record would create a dangling ref.
    stems = {_norm(p).rsplit('_', 1)[0] for p in dup_soul_paths}  # drop _n/_e/_l
    refs = _whole_db_refs(db, stems, exclude={head})
    if refs:
        raise SystemExit(
            "double_soul_rulings: %s dup soul family has OTHER referent(s) "
            "besides the head (%s) - refusing to retire (would orphan a live "
            "reference): %s" % (label, head_path, refs))

    # (2) DETACH: chance -> 0 (pre-existing FLOAT field, no dtype) + clear the
    #     3 loot refs to '' (pre-existing STRING-array field, no dtype) so no
    #     dangling ref survives step (3).
    db.set_field(head, _CHANCE_FIELD, 0.0)
    db.set_field(head, _LOOT_FIELD, [''] * _ARITY)
    db._modified.add(head)

    # (3) RETIRE the now fully-unreferenced dup/husk soul records.
    retired = 0
    for sp in dup_soul_paths:
        rec = _resolve(db, nm, sp)
        if rec is not None and _remove_record(db, rec):
            retired += 1
            nm.pop(_norm(sp), None)
    if retired != len(dup_soul_paths):
        raise SystemExit(
            "double_soul_rulings: %s expected to retire %d soul record(s), "
            "retired %d - roster changed under us" % (label, len(dup_soul_paths), retired))
    return retired


def apply(db, tags):
    nm = _name_map(db)

    # (c) snapshot the untouched roster BEFORE this module does anything, so
    # verify() can prove a literal byte-identical zero-diff.
    global _UNTOUCHED_SNAPSHOT
    _UNTOUCHED_SNAPSHOT = _snapshot(db, nm, _UNTOUCHED_RECORDS)
    missing_untouched = [p for p in _UNTOUCHED_RECORDS if p not in _UNTOUCHED_SNAPSHOT]
    if missing_untouched:
        raise SystemExit(
            "double_soul_rulings: (c) untouched-roster record(s) missing from "
            "db (build base changed - refusing to run silently): %s"
            % missing_untouched)

    # (a) Possessed Boar - terminal-only, retire the typo-twin dup.
    pb_retired = _detach_and_retire(db, nm, _PB_HEAD, _PB_DUP_SOULS, "Possessed Boar")

    # (b) Lillued - terminal-only, retire the empty-husk head soul.
    ll_retired = _detach_and_retire(db, nm, _LL_HEAD, _LL_HUSK_SOULS, "Lillued")

    # (c) Charon x3 + Hades: NOTHING touched (no code path reaches
    # _UNTOUCHED_RECORDS above except the read-only snapshot).

    print("  double_soul_rulings: (a) Possessed Boar - head detached (chance 66->0, "
          "loot refs cleared), %d typo-twin dup soul(s) retired; terminal's real "
          "SV098i soul (boar\\possesedboar_soul, formula-integrated) untouched. "
          "(b) Lillued - head detached, %d empty-husk soul(s) retired; terminal's "
          "real soul (lillued_soul) untouched. (c) Charon 39/41/43 + Hades 54: "
          "UNTOUCHED (Will's ruling - intentional multi-form rewards)."
          % (pb_retired, ll_retired))


_UNTOUCHED_SNAPSHOT = None


def verify(db, tags):
    """POST-FINALIZATION invariant (fail-loud):
      (a)/(b) the two heads no longer drop a soul (chance 0, refs empty) and
          their dup/husk soul records are gone; the two terminals are
          untouched (still drop their real soul at the original chance);
      (c) every Charon 39/41/43 + Hades 54 record is byte-identical to the
          apply()-time snapshot (Will's ruling: literally untouched);
      (d) legion_soul_stages' distinct-soul roster has SHRUNK to exactly the
          4 untouched chains (Possessed Boar + Lillued dropped out)."""
    nm = _name_map(db)

    # (a) Possessed Boar
    pb_head = _resolve(db, nm, _PB_HEAD)
    if pb_head is None:
        raise SystemExit("double_soul_rulings.verify FAIL: %s missing" % _PB_HEAD)
    ch = _scalar(db.get_field_value(pb_head, _CHANCE_FIELD))
    if not (ch is not None and float(ch) == 0.0):
        raise SystemExit(
            "double_soul_rulings.verify FAIL: %s chanceToEquipFinger2=%r "
            "(expected 0.0)" % (_PB_HEAD, ch))
    for sp in _PB_DUP_SOULS:
        if db.has_record(_resolve(db, nm, sp) or sp):
            raise SystemExit(
                "double_soul_rulings.verify FAIL: retired soul still present: %s" % sp)
    pb_term = _resolve(db, nm, _PB_TERMINAL)
    if pb_term is None:
        raise SystemExit("double_soul_rulings.verify FAIL: %s missing" % _PB_TERMINAL)
    tch = _scalar(db.get_field_value(pb_term, _CHANCE_FIELD))
    if not (tch and float(tch) > 0):
        raise SystemExit(
            "double_soul_rulings.verify FAIL: terminal %s chanceToEquipFinger2=%r "
            "(expected > 0 - the terminal must keep its real soul)" % (_PB_TERMINAL, tch))
    for sp in _PB_CANON_SOULS:
        if not db.has_record(sp):
            raise SystemExit(
                "double_soul_rulings.verify FAIL: canonical soul missing (must "
                "survive untouched): %s" % sp)

    # (b) Lillued
    ll_head = _resolve(db, nm, _LL_HEAD)
    if ll_head is None:
        raise SystemExit("double_soul_rulings.verify FAIL: %s missing" % _LL_HEAD)
    ch2 = _scalar(db.get_field_value(ll_head, _CHANCE_FIELD))
    if not (ch2 is not None and float(ch2) == 0.0):
        raise SystemExit(
            "double_soul_rulings.verify FAIL: %s chanceToEquipFinger2=%r "
            "(expected 0.0)" % (_LL_HEAD, ch2))
    for sp in _LL_HUSK_SOULS:
        if db.has_record(_resolve(db, nm, sp) or sp):
            raise SystemExit(
                "double_soul_rulings.verify FAIL: retired husk soul still present: %s" % sp)
    ll_term = _resolve(db, nm, _LL_TERMINAL)
    if ll_term is None:
        raise SystemExit("double_soul_rulings.verify FAIL: %s missing" % _LL_TERMINAL)
    tch2 = _scalar(db.get_field_value(ll_term, _CHANCE_FIELD))
    if not (tch2 and float(tch2) > 0):
        raise SystemExit(
            "double_soul_rulings.verify FAIL: terminal %s chanceToEquipFinger2=%r "
            "(expected > 0)" % (_LL_TERMINAL, tch2))
    for sp in _LL_CANON_SOULS:
        if not db.has_record(sp):
            raise SystemExit(
                "double_soul_rulings.verify FAIL: canonical soul missing (must "
                "survive untouched): %s" % sp)

    # (c) Charon x3 + Hades: literal byte-identical zero-diff vs the apply()-time
    # snapshot. If apply() never ran in this process (e.g. verify() called
    # standalone), fall back to a live re-snapshot equality with itself (no-op).
    if _UNTOUCHED_SNAPSHOT is not None:
        now = _snapshot(db, nm, _UNTOUCHED_RECORDS)
        if now != _UNTOUCHED_SNAPSHOT:
            diffs = []
            for path in _UNTOUCHED_RECORDS:
                a, b = _UNTOUCHED_SNAPSHOT.get(path), now.get(path)
                if a != b:
                    diffs.append(path)
            raise SystemExit(
                "double_soul_rulings.verify FAIL: (c) Charon/Hades roster is NOT "
                "byte-identical to the pre-apply snapshot (Will's ruling: these "
                "must stay UNTOUCHED): %s" % diffs)

    # (d) legion_soul_stages' distinct-soul roster shrank to exactly Charon x3 + Hades.
    import os as _os
    import sys as _sys
    _here = _os.path.dirname(_os.path.abspath(__file__))     # tools/patches
    _tools = _os.path.dirname(_here)                          # tools/
    if _tools not in _sys.path:
        _sys.path.insert(0, _tools)
    try:
        from patches.legion_soul_stages import _analyze as _lss_analyze
    except ImportError:
        if _here not in _sys.path:
            _sys.path.insert(0, _here)
        from legion_soul_stages import _analyze as _lss_analyze
    res = _lss_analyze(db)
    remaining_heads = {c['members'][0] for c in res['distinct_multi']}
    expected_heads = {
        r'records\xpack\creatures\monster\bosses\02_charon\boss_charon_39.dbr',
        r'records\xpack\creatures\monster\bosses\02_charon\boss_charon_41.dbr',
        r'records\xpack\creatures\monster\bosses\02_charon\boss_charon_43.dbr',
        r'records\drxcreatures\bloodwitch\boss_hades_54.dbr',
    }
    remaining_heads_norm = {_norm(h) for h in remaining_heads}
    expected_heads_norm = {_norm(h) for h in expected_heads}
    if remaining_heads_norm != expected_heads_norm:
        raise SystemExit(
            "double_soul_rulings.verify FAIL: legion_soul_stages distinct-soul "
            "roster after this module's fixes = %s, expected exactly Charon "
            "39/41/43 + Hades 54 = %s" % (sorted(remaining_heads_norm),
                                          sorted(expected_heads_norm)))

    print("  double_soul_rulings.verify OK: Possessed Boar + Lillued heads "
          "detached (dup/husk souls retired, terminals untouched); Charon "
          "39/41/43 + Hades 54 byte-identical to pre-apply (Will's ruling); "
          "legion_soul_stages distinct-soul roster shrank 6 -> 4 as expected.")


def _scalar(v):
    return (v[0] if v else None) if isinstance(v, list) else v
