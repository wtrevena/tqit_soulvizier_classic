r"""turtleshell_relics - ITEM 2 (two new relics on the proven Turtle Shell pattern).

GROUND-TRUTH: what "the magenta turtle shell custom relic" actually is
-----------------------------------------------------------------------
Will's phrase describes the mod's proven Common-tier `ItemCharm` relic recipe,
first established in this codebase as the vanilla base-game donor
`records\item\animalrelics\{01,02,03}_act1_turtleshell.dbr` (Turtle Shell:
`Class=ItemCharm`, `itemClassification=Common`, 5-shard `completedRelicLevel=5`,
a single scaling stat `defensiveBlockModifier=[1,2,3,4,5]`, its own
`bonusTableName` completion-bonus `LootRandomizerTable`, and a FixedWeight loot
table `records\item\loottables\animalrelics\01_act1_turtleshell.dbr`). ALL
Relic/Charm-class items (this one included) render their name in the engine's
signature MAGENTA/pink tooltip color - a `Class=ItemCharm`/`ItemRelic`
convention, not a per-item `{^F}` text-color tag (none of Turtle Shell,
Emberscale, or Ereban Heartstone below carry `{^F}`; verified against all
three records). Two custom relics ALREADY clone this exact shape in
`tools/apply_svc_patches.py`:
  - D10 Emberscale (`_create_emberscale_charm`): clones the turtle-shell ITEM
    donor directly (so it keeps the turtle-shell icon/mesh - visually still
    "the magenta turtle shell" in-game, just re-flavored), 5-shard fire+armor-
    melt ladder, dropped by the Flameguard Slayer.
  - C5 Ereban Heartstone (`_create_ereban_heartstone`): a different ITEM donor
    (Ereban Crystal) but the SAME turtle-shell FixedWeight LOOT-TABLE donor +
    wiring shape, dropped by the Ereban Brutes.
This module clones that exact, twice-proven pattern for the two BACKLOG asks
(NEW-RELIC-DIONYSUS-TRICKSTER + NEW-RELIC-DUNE-FIEND), reusing the turtle-shell
ITEM donor (so both new relics are also, literally, magenta turtle shells in
silhouette - zero new art, per the efficiency law) and the turtle-shell loot-
table donor (matching both existing precedents).

(a) DIONYSUS TRICKSTER ARCHERS -> "The Reveler's Ruse"
-----------------------------------------------------------------------------
Ground-truthed the monster family (no in-game text literally says "Dionysus
trickster archer" - satyrs are Dionysus's mythic revelers, and the request is
Will's own flavor description of a real, distinct roster family): the
Satyr Archer line, `records\creature\monster\satyr\ar_archer_{01..06}.dbr`
(base-game/SV098i Act 1 Greece beastmen). Its own dedicated soul family proves
it is treated as one distinct identity in our systems: `satyrarcher_soul_*`
(tagMonsterName049 "Satyr ~ Skirmisher", ar_archer_01-03) graduating to
`satyrveteranarcher_soul_*` (tagMonsterName051/052 "Satyr ~ Veteran
Skirmisher", ar_archer_04-06) - a hit-and-run RANGED "skirmisher" identity,
which is exactly the trickster-archer fantasy (evasive, precise, never toe-to-
toe). [R-260 CORRECTION, 2026-09-10: the original text here said "`lootMisc4` is
verified genuinely free on every body in the family (no Misc4 field at all)". It was
free because `Misc4` is not a `characterloot.tpl` variable - it is free on EVERY
record in existence and the engine never reads it, so the charm never dropped from
any archer between 2026-07-15 and R-260. The drop now rides a REAL Misc slot through
`apply_svc_patches._svc_guarantee_unique` at a MEASURED 7% (ar_archer_01..04: the
dormant Misc3; ar_archer_05/06: a rate-preserving share of the live Misc3), and
`verify()` re-derives the rate from the final bytes.]

Stats (5-shard ladder, matching the turtle-shell/Emberscale/Ereban shape):
attack speed (the skirmisher's hit-and-run precision) + % pierce damage bonus
(archer signature damage type) - deliberately simple, one step richer than the
Turtle Shell's single stat, matching Emberscale/Ereban's multi-field ladders.
Completion bonus table mirrors Emberscale's exact weight-1500 shape with
archer-flavored entries (pierce/OA/dexterity/strength/life/poison-resist -
poison-resist via the GENERIC `prefix\default` affix, not the existing
Dionysus'-Wineskin-specific bonus record, to avoid theming collision with that
already-shipped base relic).

(b) DUNE FIEND -> ALREADY HAS ONE (no new relic authored)
-----------------------------------------------------------------------------
Per the backlog's own conditional ("FIRST verify dune fiends don't already
drop one"): they do. `records\creature\monster\antlion\em_dunefiend_{32,34}.dbr`
already drop `records\item\animalrelics\{01,02,03}_act2_fiendcarapace.dbr`
("Fiend Carapace") at `chanceToEquipMisc1=12.0` - ground-truthed present in
ALL THREE upstream sources (SV098i/0.9/041) AND absent from vanilla base-game
`database.arz`, so this is amgoz1's own SV098i-original desert-terror relic
(same Turtle-Shell `ItemCharm`/Common/5-shard shape, its own bonus table
`lootmagicalaffixes\animalrelics\0N_act2_rigidcarapace.dbr`), not something we
built and not a gap to fill. This module authors NOTHING for Dune Fiend;
`verify()` asserts the pre-existing wiring is still intact (regression guard,
not a new feature).
"""

MODULE_NAME = "Turtle-shell-pattern relics (Reveler's Ruse; Dune Fiend already-has-one guard)"

DATA_TYPE_STRING = 2
DATA_TYPE_FLOAT = 1
DATA_TYPE_INT = 0

_TURTLE_DONOR = {t: r'records\item\animalrelics\%s_act1_turtleshell.dbr' % t
                 for t in ('01', '02', '03')}
_TURTLE_LOOT_DONOR = r'records\item\loottables\animalrelics\01_act1_turtleshell.dbr'

# ── (a) Reveler's Ruse (Satyr Archer / Dionysus trickster-archer relic) ─────
_RR_CHARM = {t: r'records\item\animalrelics\svc_revelersruse\%s_revelersruse.dbr' % t
             for t in ('01', '02', '03')}
_RR_BONUS = {t: r'records\item\lootmagicalaffixes\animalrelics\svc_revelersruse\%s_revelersruse.dbr' % t
             for t in ('01', '02', '03')}
_RR_LOOT = {t: r'records\item\loottables\animalrelics\svc_revelersruse\%s_revelersruse.dbr' % t
            for t in ('01', '02', '03')}
_RR_ARCHERS = [r'records\creature\monster\satyr\ar_archer_01.dbr',
               r'records\creature\monster\satyr\ar_archer_02.dbr',
               r'records\creature\monster\satyr\ar_archer_03.dbr',
               r'records\creature\monster\satyr\ar_archer_04.dbr',
               r'records\creature\monster\satyr\ar_archer_05.dbr',
               r'records\creature\monster\satyr\ar_archer_06.dbr']
_RR_LEVELREQ = {'01': 5, '02': 24, '03': 38}
_RR_DROP_PCT = 7.0   # matches the turtle-shell/Emberscale precedent rate
_RR_SLOTS_ON = ('bow',)
_RR_SLOTS_OFF = ('sword', 'axe', 'mace', 'spear', 'staff', 'shield', 'amulet',
                 'armband', 'bodyArmor', 'bracelet', 'greaves', 'helmet', 'ring')
# per-shard 5-value ladders (shards 1..5)
_RR_STATS = {
    '01': {'characterAttackSpeedModifier': [2.0, 4.0, 6.0, 8.0, 10.0],
           'offensivePierceModifier': [3.0, 6.0, 9.0, 12.0, 15.0]},
    '02': {'characterAttackSpeedModifier': [4.0, 8.0, 12.0, 16.0, 20.0],
           'offensivePierceModifier': [5.0, 10.0, 15.0, 20.0, 25.0]},
    '03': {'characterAttackSpeedModifier': [6.0, 12.0, 18.0, 24.0, 30.0],
           'offensivePierceModifier': [7.0, 14.0, 21.0, 28.0, 35.0]},
}
_AFF = r'records\item\lootmagicalaffixes'
_RR_BONUS_ENTRIES = {
    '01': [(_AFF + r'\animalrelics\bonuses\offensive_damagepierce_01.dbr', 250),
           (_AFF + r'\suffix\default\character_abilityoffensive_02.dbr', 300),
           (_AFF + r'\suffix\default\character_attributedexterity_01.dbr', 300),
           (_AFF + r'\suffix\default\character_attributestrength_01.dbr', 250),
           (_AFF + r'\suffix\default\character_attributelife_01.dbr', 200),
           (_AFF + r'\prefix\default\defensive_resistpoison_01.dbr', 200)],
    '02': [(_AFF + r'\animalrelics\bonuses\offensive_damagepierce_03.dbr', 250),
           (_AFF + r'\suffix\default\character_abilityoffensive_04.dbr', 300),
           (_AFF + r'\suffix\default\character_attributedexterity_03.dbr', 300),
           (_AFF + r'\suffix\default\character_attributestrength_03.dbr', 250),
           (_AFF + r'\suffix\default\character_attributelife_02.dbr', 200),
           (_AFF + r'\prefix\default\defensive_resistpoison_02.dbr', 200)],
    '03': [(_AFF + r'\animalrelics\bonuses\offensive_damagepierce_05.dbr', 250),
           (_AFF + r'\suffix\default\character_abilityoffensive_06.dbr', 300),
           (_AFF + r'\suffix\default\character_attributedexterity_05.dbr', 300),
           (_AFF + r'\suffix\default\character_attributestrength_05.dbr', 250),
           (_AFF + r'\suffix\default\character_attributelife_03.dbr', 200),
           (_AFF + r'\prefix\default\defensive_resistpoison_03.dbr', 200)],
}

# ── (b) Dune Fiend regression guard (nothing authored; verify-only) ────────
_DF_MONSTERS = [r'records\creature\monster\antlion\em_dunefiend_32.dbr',
                r'records\creature\monster\antlion\em_dunefiend_34.dbr']
_DF_RELIC = {t: r'records\item\animalrelics\%s_act2_fiendcarapace.dbr' % t
             for t in ('01', '02', '03')}


def _create_revelers_ruse(db, tags):
    """(a) build the Reveler's Ruse charm chain: 3 tier charms (clone the
    turtle-shell ITEM donor - same visual silhouette as Emberscale/Ereban's
    precedent, zero new art), 3 completion-bonus tables, 3 FixedWeight loot
    tables, and the 7% wiring on all 6 Satyr Archer bodies (a REAL Misc slot, R-260)."""
    S, F = DATA_TYPE_STRING, DATA_TYPE_FLOAT

    for t in ('01', '02', '03'):
        donor = _TURTLE_DONOR[t]
        if not db.has_record(donor):
            raise SystemExit("turtleshell_relics: turtle charm donor missing (exact): %s" % donor)
        for path, _w in _RR_BONUS_ENTRIES[t]:
            if not db.has_record(path):
                raise SystemExit("turtleshell_relics: completion-bonus affix missing (exact): %s" % path)
    if not db.has_record(_TURTLE_LOOT_DONOR):
        raise SystemExit("turtleshell_relics: turtle loot-table donor missing (exact): %s" % _TURTLE_LOOT_DONOR)
    for mon in _RR_ARCHERS:
        if not db.has_record(mon):
            raise SystemExit("turtleshell_relics: Satyr Archer body missing (exact): %s" % mon)

    for t in ('01', '02', '03'):
        # ── charm (clone -> override; no dtype on existing donor fields) ──
        charm = _RR_CHARM[t]
        db.clone_record(_TURTLE_DONOR[t], charm)
        sf = db.set_field
        sf(charm, 'description', 'tagSVCRevelersRuse')
        sf(charm, 'itemText', 'tagSVCRevelersRuseDESC')
        sf(charm, 'FileDescription', 'Attack speed + pierce damage (trickster archer)')
        sf(charm, 'levelRequirement', _RR_LEVELREQ[t])
        # the turtle's block identity is zeroed (Reveler's Ruse is offensive)
        sf(charm, 'defensiveBlockModifier', [0.0, 0.0, 0.0, 0.0, 0.0])
        sf(charm, 'characterDefensiveBlockRecoveryReduction', 0.0)
        for fname, arr in _RR_STATS[t].items():
            sf(charm, fname, list(arr), F)   # NEW fields on the turtle donor -> explicit FLOAT
        # bow-only (a trickster archer's own relic - not shield-eligible like
        # the turtle donor; turtle's 'shield'=1 must be cleared)
        sf(charm, 'shield', 0)
        for slot in _RR_SLOTS_ON:
            sf(charm, slot, 1)
        for slot in _RR_SLOTS_OFF:
            sf(charm, slot, 0)
        sf(charm, 'bonusTableName', _RR_BONUS[t])
        db._modified.add(charm)

        # ── completion-bonus table (NEW record) ──
        bt = _RR_BONUS[t]
        from apply_svc_patches import _ensure_record
        _ensure_record(db, bt, r'database\Templates\LootRandomizerTable.tpl')
        db.set_field(bt, 'templateName', r'database\Templates\LootRandomizerTable.tpl', S)
        db.set_field(bt, 'Class', 'LootRandomizerTable', S)
        total_w = 0
        for i, (path, w) in enumerate(_RR_BONUS_ENTRIES[t], start=1):
            db.set_field(bt, 'randomizerName%d' % i, path, S)
            db.set_field(bt, 'randomizerWeight%d' % i, w, DATA_TYPE_INT)
            total_w += w
        if total_w != 1500:
            raise SystemExit("turtleshell_relics: tier %s bonus weights sum %d != 1500" % (t, total_w))
        db._modified.add(bt)

        # ── loot table (clone the turtle FixedWeight table) ──
        lt = _RR_LOOT[t]
        db.clone_record(_TURTLE_LOOT_DONOR, lt)
        db.set_field(lt, 'lootName1', charm)
        db._modified.add(lt)

    # ── wire all 6 Satyr Archer bodies at 7% on a REAL Misc slot (R-260) ──
    # Until R-260 this wrote `lootMisc4Item1` - a variable `characterloot.tpl` does not
    # declare (it has exactly Misc1..Misc3) - so the charm never dropped from any
    # archer. `_svc_guarantee_unique` now lands it by the R-260 policy: ar_archer_01..04
    # carry a DORMANT Misc3 (chance 0 over amulet rows that never rolled) -> Misc3 at 7%
    # with those rows muted by weight; ar_archer_05/06 have Misc3 live at 0.5% -> the
    # rate-preserving SHARE (chance 7.5, charm weight 70056 against the amulet rows'
    # 5004, so the amulets keep their exact 0.5% and the charm measures exactly 7%).
    from apply_svc_patches import _svc_guarantee_unique
    loot_arr = [_RR_LOOT['01'], _RR_LOOT['02'], _RR_LOOT['03']]
    for mon in _RR_ARCHERS:
        _svc_guarantee_unique(db, mon, loot_arr, pct=_RR_DROP_PCT, share=True,
                              label="Reveler's Ruse")

    tags['tagSVCRevelersRuse'] = "The Reveler's Ruse"
    tags['tagSVCRevelersRuseDESC'] = (
        'Torn from a satyr skirmisher who never fought fair - one shot to '
        'distract, one to disarm, one to finish the joke. Wine-warmed hands '
        'never miss twice.')
    print("  turtleshell_relics (a): The Reveler's Ruse - 3 charms (turtle-shell "
          "item clone, bow-only, attack speed + pierce dmg 5-shard ladder) + "
          "3 bonus tables (w1500) + 3 loot tables; wired all 6 Satyr Archer "
          "bodies (ar_archer_01..06) on a REAL Misc slot @ a measured %.0f%% (R-260)."
          % _RR_DROP_PCT)


def apply(db, tags):
    _create_revelers_ruse(db, tags)
    # (b) Dune Fiend: nothing to author - see module docstring. Confirmed at
    # apply-time too (not just verify) so a build fails loud immediately if
    # the pre-existing wiring the whole design rests on ever regresses.
    _assert_dunefiend_relic_intact(db)


def _assert_dunefiend_relic_intact(db):
    for mon in _DF_MONSTERS:
        if not db.has_record(mon):
            raise SystemExit("turtleshell_relics: Dune Fiend body missing (exact): %s" % mon)
        chance = db.get_field_value(mon, 'chanceToEquipMisc1')
        chance = chance[0] if isinstance(chance, list) and chance else chance
        refs = db.get_field_value(mon, 'lootMisc1Item1')
        refs = refs if isinstance(refs, list) else ([refs] if refs else [])
        expected = [_DF_RELIC[t] for t in ('01', '02', '03')]
        if not (chance and float(chance) > 0):
            raise SystemExit(
                "turtleshell_relics: Dune Fiend %s no longer drops its "
                "pre-existing relic (chanceToEquipMisc1=%r) - the "
                "NEW-RELIC-DUNE-FIEND 'already has one' finding is now FALSE; "
                "re-evaluate whether a new relic is needed" % (mon, chance))
        for e in expected:
            if not any(_norm(r) == _norm(e) for r in refs):
                raise SystemExit(
                    "turtleshell_relics: Dune Fiend %s lootMisc1 no longer "
                    "references %s (got %r)" % (mon, e, refs))
    for t in ('01', '02', '03'):
        if not db.has_record(_DF_RELIC[t]):
            raise SystemExit("turtleshell_relics: Fiend Carapace tier %s record "
                              "missing (exact): %s" % (t, _DF_RELIC[t]))


def _norm(p):
    return str(p).replace('/', '\\').lower()


def verify(db, tags):
    """POST-FINALIZATION invariant (fail-loud):
      (a) 3 Reveler's Ruse charms exist, bow-only, non-zero 5-shard ladders,
          bonus tables resolve, all 6 archer bodies MEASURED at the intended rate (R-260);
      (b) the pre-existing Dune Fiend Fiend Carapace wiring is still intact
          (regression guard for the 'already has one' finding)."""
    for t in ('01', '02', '03'):
        charm = _RR_CHARM[t]
        if not db.has_record(charm):
            raise SystemExit("turtleshell_relics.verify FAIL: charm missing: %s" % charm)
        for slot in _RR_SLOTS_OFF:
            v = db.get_field_value(charm, slot)
            v = v[0] if isinstance(v, list) and v else v
            if v not in (0, 0.0, None):
                raise SystemExit(
                    "turtleshell_relics.verify FAIL: %s slot %s should be 0, got %r"
                    % (charm, slot, v))
        for fname in _RR_STATS[t]:
            v = db.get_field_value(charm, fname)
            v = v if isinstance(v, list) else [v]
            if not v or not any(float(x) > 0 for x in v):
                raise SystemExit(
                    "turtleshell_relics.verify FAIL: %s field %s not a "
                    "positive ladder: %r" % (charm, fname, v))
        bt = db.get_field_value(charm, 'bonusTableName')
        bt = bt[0] if isinstance(bt, list) and bt else bt
        if _norm(bt) != _norm(_RR_BONUS[t]):
            raise SystemExit(
                "turtleshell_relics.verify FAIL: %s bonusTableName=%r != %s"
                % (charm, bt, _RR_BONUS[t]))
        if not db.has_record(_RR_BONUS[t]):
            raise SystemExit("turtleshell_relics.verify FAIL: bonus table missing: %s" % _RR_BONUS[t])
        if not db.has_record(_RR_LOOT[t]):
            raise SystemExit("turtleshell_relics.verify FAIL: loot table missing: %s" % _RR_LOOT[t])
        lname = db.get_field_value(_RR_LOOT[t], 'lootName1')
        lname = lname[0] if isinstance(lname, list) and lname else lname
        if _norm(lname) != _norm(charm):
            raise SystemExit(
                "turtleshell_relics.verify FAIL: %s lootName1=%r != %s"
                % (_RR_LOOT[t], lname, charm))

    # R-260: the drop is MEASURED off the final bytes (slot chance x row weight / sum of
    # weights over every real slot) and must equal the intended rate; a phantom-slot
    # field on the record is a failure in itself.
    import svc_loot_slots as _sls
    expected = [_RR_LOOT[t] for t in ('01', '02', '03')]
    for mon in _RR_ARCHERS:
        ph = _sls.phantom_fields(db, mon)
        if ph:
            raise SystemExit("turtleshell_relics.verify FAIL: %s carries undeclared slot "
                             "fields %s (R-260)" % (mon, ph))
        got = _sls.item_share(db, mon, expected)
        if not _sls.close(got, _RR_DROP_PCT):
            raise SystemExit(
                "turtleshell_relics.verify FAIL: %s drops the Reveler's Ruse at a MEASURED "
                "%.4f%% of kills, intended %.4f%% (rides %r)"
                % (mon, got, _RR_DROP_PCT, _sls.item_shares(db, mon, expected)))
        if tags.get('tagSVCRevelersRuse') != "The Reveler's Ruse":
            raise SystemExit("turtleshell_relics.verify FAIL: tagSVCRevelersRuse missing/wrong")

    _assert_dunefiend_relic_intact(db)
    print("  turtleshell_relics.verify OK: Reveler's Ruse 3/3 charms + 6/6 "
          "archer bodies wired; Dune Fiend pre-existing relic intact "
          "(no duplicate authored).")
