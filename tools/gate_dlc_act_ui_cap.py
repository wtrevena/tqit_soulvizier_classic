r"""PORTAL-PAGE / ACT-SELECTION DLC-CAP GATE (fail-loud, golden allow-list).

WHY
---
Will, 2026-08-10: "in the portal page i see atlantis which should be disabled in
this mod". Root cause (RCA in docs/PORTAL_PAGE_DLC_CAP.md):

  The in-game portal window's page list is ONE database record,
  `records\ingameui\teleportmap\teleportmap.dbr` (template
  `database\Templates\InGameUI\WorldlMapWindow.tpl`). Each act page is a triple
  of fields `<Page>Button` / `<Page>MapImage` / `<Page>ZoneList`. The base TQAE
  record carries SEVEN pages: Greece, Egypt, Orient, Hades (Immortal Throne,
  Olympus folded in) AND the three DLC acts Scandia (Ragnarok, x2tagMNorth),
  Atlantis (x3tagQAct06) and China (Eternal Embers, x4tagMChina).

  SV 0.98i ships its own IT-era `teleportmap.dbr` (4 pages, no DLC), but
  `build_svc_database.strip_ui_overrides()` deletes EVERY `records\ingameui\*`
  record except the mastery skill trees (SV's TQIT-era UI breaks AE's modern UI).
  With no mod override left, the record resolves from the BASE game .arz, so a
  DLC-owning player sees the three DLC act tabs. Same story for the quest log's
  act buttons in `records\ingameui\player quests\questwindow.dbr` (buttons 5/6/7
  point at the XPack2/XPack3/XPack4 quest-log tabs; SV's own copy has 1-4 only).

  The fix (build_svc_database.apply_dlc_act_ui_cap) imports the BASE record into
  the mod .arz AFTER strip_ui_overrides and deletes exactly the DLC fields. This
  gate is the fail-loud proof that the capped record is actually IN the shipped
  artifact (the "inert fix" trap: a cap applied BEFORE the strip would be deleted
  again and ship nothing) and that it lists ZERO DLC-act entries.

WHAT IT ASSERTS (all against the FINAL written .arz, artifact proof)
-------------------------------------------------------------------
  T1  teleportmap.dbr is PRESENT in the mod .arz          (survived the strip)
  T2  none of the 9 banned DLC page fields exist on it
  T3  its page-field set == the committed golden allow-list, exactly
  T4  no field VALUE on it names a DLC act namespace (xpack2/3/4, atlantis,
      scandia, china). Plain `XPack\...` (Immortal Throne) stays legal.
  T5  questwindow.dbr is PRESENT, DLC buttons/maps 5-7 absent, 1-4 exact,
      and no field VALUE names a DLC act namespace
  T6  the DERIVED portal page list (every `<Page>Button` field present) ==
      ['Greece', 'Egypt', 'Orient', 'Hades'] - ZERO DLC-act pages
  T7  the mod .arz overrides NO other `records\ingameui\teleportmap\*` record
      (no stray DLC zone/tab override sneaking back in)

STANDING RULING THIS ENFORCES
-----------------------------
"IMMORTAL-THRONE CAP (Will, 2026-07-10): the campaign stays capped at Immortal
Throne (Hades). Do NOT make Atlantis or anything past IT reachable." (BACKLOG)

usage:
  validate : py tools/gate_dlc_act_ui_cap.py <arz>
  negtest  : py tools/gate_dlc_act_ui_cap.py <arz> --negtest
exit codes: 0 = PASS, 1 = the cap is missing / a DLC act entry is back, 2 = usage.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase  # noqa: E402

TELEPORTMAP = r'records\ingameui\teleportmap\teleportmap.dbr'
QUESTWINDOW = r'records\ingameui\player quests\questwindow.dbr'

# ── THE GOLDEN ALLOW-LISTS (committed contract) ──────────────────────────────
# Exactly the page-bearing fields the capped teleportmap.dbr MAY carry. This is
# the base TQAE record's page field set MINUS the three DLC acts. Note the base
# record has NO OlympusButton / OlympusZoneList (Olympus is a zone inside
# HadesZoneList; only the shared OlympusMapImage field exists), so those two stay
# absent too - an exact set match catches a re-add in either direction.
GOLDEN_TELEPORTMAP_PAGE_FIELDS = frozenset({
    'GreeceButton', 'GreeceMapImage', 'GreeceZoneList',
    'EgyptButton', 'EgyptMapImage', 'EgyptZoneList',
    'OrientButton', 'OrientMapImage', 'OrientZoneList',
    'HadesButton', 'HadesImage', 'HadesZoneList',
    'OlympusMapImage',
})

# The 9 fields whose presence IS the bug.
BANNED_TELEPORTMAP_FIELDS = frozenset({
    'ScandiaButton', 'ScandiaMapImage', 'ScandiaZoneList',      # Ragnarok
    'AtlantisButton', 'AtlantisMapImage', 'AtlantisZoneList',   # Atlantis
    'ChinaButton', 'ChinaMapImage', 'ChinaZoneList',            # Eternal Embers
})

# Every page-prefix the template knows about, so T3 can classify a field as
# "page-bearing" without hard-coding the union of golden + banned twice.
_PAGE_PREFIXES = ('Greece', 'Egypt', 'Orient', 'Hades', 'Olympus',
                  'Scandia', 'Atlantis', 'China')
_PAGE_SUFFIXES = ('Button', 'MapImage', 'ZoneList', 'Image')

# The portal page list the player must see (order = draw order, top to bottom).
GOLDEN_PORTAL_PAGES = ('Greece', 'Egypt', 'Orient', 'Hades')

GOLDEN_QUESTWINDOW_FIELDS = frozenset(
    ['questLocationButton%d' % i for i in (1, 2, 3, 4)]
    + ['questMapBitmap%d' % i for i in (1, 2, 3, 4)])
BANNED_QUESTWINDOW_FIELDS = frozenset(
    ['questLocationButton%d' % i for i in (5, 6, 7)]
    + ['questMapBitmap%d' % i for i in (5, 6, 7)])

# A DLC-ACT namespace in a field VALUE. `xpack` alone is Immortal Throne and is
# LEGAL (HadesImage = XPack\UI\TeleportMap\WorldMap05.tex; questLocationButton4 =
# Records\XPack\Quests\...), so the digit is required. No legitimate value on
# either capped record contains atlantis / scandia / china (verified against the
# base-game records this cap is derived from).
_DLC_VALUE = re.compile(r'(?i)xpack[234]|atlantis|scandia|china')


def _fieldmap(db, rec):
    """{plain field name: [str values]} for a record, or None if absent."""
    ff = db.get_fields(rec)
    if ff is None:
        return None
    out = {}
    for key, tf in ff.items():
        name = key.split('###')[0]
        vals = tf.value if isinstance(tf.value, list) else [tf.value]
        out.setdefault(name, []).extend([v for v in vals if v is not None])
    return out


def _is_page_field(name):
    for p in _PAGE_PREFIXES:
        if name.startswith(p) and name[len(p):] in _PAGE_SUFFIXES:
            return True
    return False


def validate_db(db, label='<db>'):
    """Run every check against an in-memory ArzDatabase. Returns 0 PASS / 1 FAIL."""
    fails = []
    print('=== PORTAL-PAGE / ACT-SELECTION DLC-CAP GATE: %s ===' % label)

    # ---- T1/T2/T3/T4/T6: the portal page ------------------------------------
    tm = _fieldmap(db, TELEPORTMAP)
    if tm is None:
        fails.append(
            'T1 teleportmap.dbr is ABSENT from the mod .arz, so the base game\'s '
            'DLC-laden record is what the player gets. Either the cap never ran, or '
            'it ran BEFORE strip_ui_overrides() and was deleted again (the inert-fix '
            'trap: apply_dlc_act_ui_cap MUST run after strip_ui_overrides).')
    else:
        print('  T1 OK  teleportmap.dbr present (%d fields) - survived strip_ui_overrides'
              % len(tm))

        back = sorted(BANNED_TELEPORTMAP_FIELDS & set(tm))
        if back:
            fails.append('T2 DLC act page field(s) are BACK on teleportmap.dbr: %s'
                         % ', '.join(back))
        else:
            print('  T2 OK  none of the 9 DLC page fields present')

        pages = {n for n in tm if _is_page_field(n)}
        if pages != set(GOLDEN_TELEPORTMAP_PAGE_FIELDS):
            extra = sorted(pages - set(GOLDEN_TELEPORTMAP_PAGE_FIELDS))
            missing = sorted(set(GOLDEN_TELEPORTMAP_PAGE_FIELDS) - pages)
            fails.append('T3 teleportmap.dbr page-field set != golden (extra=%s missing=%s)'
                         % (extra or 'none', missing or 'none'))
        else:
            print('  T3 OK  page-field set == golden (%d fields)' % len(pages))

        bad_vals = []
        for name, vals in sorted(tm.items()):
            for v in vals:
                if isinstance(v, str) and _DLC_VALUE.search(v):
                    bad_vals.append('%s = %s' % (name, v))
        if bad_vals:
            fails.append('T4 teleportmap.dbr field VALUES still name a DLC act: %s'
                         % '; '.join(bad_vals[:8]))
        else:
            print('  T4 OK  no field value names a DLC act namespace '
                  '(plain XPack / Immortal Throne stays legal)')

        rendered = [p for p in _PAGE_PREFIXES if (p + 'Button') in tm]
        if tuple(rendered) != GOLDEN_PORTAL_PAGES:
            fails.append('T6 the rendered portal page list is %s, golden is %s'
                         % (rendered, list(GOLDEN_PORTAL_PAGES)))
        else:
            print('  T6 OK  portal pages = %s (ZERO DLC-act entries)' % (rendered,))

    # ---- T5: the quest-log act buttons --------------------------------------
    qw = _fieldmap(db, QUESTWINDOW)
    if qw is None:
        fails.append(
            'T5 questwindow.dbr is ABSENT from the mod .arz, so the base game\'s '
            'record (act buttons 5/6/7 = Ragnarok/Atlantis/Eternal Embers) is what '
            'the player gets.')
    else:
        back = sorted(BANNED_QUESTWINDOW_FIELDS & set(qw))
        acts = {n for n in qw if n.startswith(('questLocationButton', 'questMapBitmap'))}
        bad_vals = [
            '%s = %s' % (n, v) for n, vals in sorted(qw.items()) for v in vals
            if isinstance(v, str) and _DLC_VALUE.search(v)]
        if back:
            fails.append('T5 DLC quest-log act field(s) are BACK on questwindow.dbr: %s'
                         % ', '.join(back))
        elif acts != set(GOLDEN_QUESTWINDOW_FIELDS):
            fails.append('T5 questwindow.dbr act-field set != golden (extra=%s missing=%s)'
                         % (sorted(acts - set(GOLDEN_QUESTWINDOW_FIELDS)) or 'none',
                            sorted(set(GOLDEN_QUESTWINDOW_FIELDS) - acts) or 'none'))
        elif bad_vals:
            fails.append('T5 questwindow.dbr field VALUES still name a DLC act: %s'
                         % '; '.join(bad_vals[:8]))
        else:
            print('  T5 OK  quest-log act buttons/maps = 1-4 only (Greece/Egypt/'
                  'Orient/Immortal Throne), no DLC act tab')

    # ---- T7: no stray teleportmap override ----------------------------------
    strays = sorted(n for n in db.record_names()
                    if n.replace('/', '\\').lower().startswith(
                        'records\\ingameui\\teleportmap\\')
                    and n.replace('/', '\\').lower() != TELEPORTMAP)
    if strays:
        fails.append('T7 the mod .arz overrides %d extra teleportmap record(s): %s'
                     % (len(strays), ', '.join(strays[:6])))
    else:
        print('  T7 OK  teleportmap.dbr is the only teleportmap record the mod overrides')

    if fails:
        print('\nRESULT: FAIL - %d check(s) failed' % len(fails))
        for f in fails:
            print('  FAIL: %s' % f)
        return 1
    print('\nRESULT: PASS - the portal page and the quest log list ZERO DLC-act '
          'entries; the campaign stays capped at Immortal Throne (Will 2026-07-10).')
    return 0


def _plant(db, which):
    """Negative test: re-introduce a defect the gate must catch."""
    if which == 'atlantis':
        # exactly the base-game shape the cap removes
        db.set_field(TELEPORTMAP, 'AtlantisButton',
                     r'Records\ingameui\teleportmap\atlantisbutton.dbr', 2)
        db.set_field(TELEPORTMAP, 'AtlantisMapImage',
                     r'XPack3\ingameui\teleportmap\worldmap_atlantis.tex', 2)
        db._modified.add(TELEPORTMAP)
        print('  [negtest] planted AtlantisButton + AtlantisMapImage back onto '
              'teleportmap.dbr')
    elif which == 'dropgreece':
        ff = db.get_fields(TELEPORTMAP) or {}
        for k in list(ff):
            if k.split('###')[0] == 'GreeceButton':
                del ff[k]
        db._modified.add(TELEPORTMAP)
        print('  [negtest] dropped the legitimate GreeceButton page from teleportmap.dbr')
    elif which == 'questlog':
        db.set_field(QUESTWINDOW, 'questLocationButton6',
                     r'Records\XPack3\Quests\QuestLog UI\QuestLocationButton6.dbr', 2)
        db._modified.add(QUESTWINDOW)
        print('  [negtest] planted the Atlantis quest-log act button back onto '
              'questwindow.dbr')


def validate(arz_path, plant=None):
    p = Path(arz_path)
    if not p.is_file():
        print('gate_dlc_act_ui_cap: no such .arz: %s' % p)
        return 2
    db = ArzDatabase.from_arz(p)
    if plant:
        _plant(db, plant)
    return validate_db(db, label=str(p))


def main(argv):
    args = argv[1:]
    if not args:
        print(__doc__)
        return 2
    neg = '--negtest' in args
    args = [a for a in args if a != '--negtest']
    if not args:
        print('usage: py tools/gate_dlc_act_ui_cap.py <arz> [--negtest]')
        return 2
    if not neg:
        return validate(args[0])

    # Three planted defects; the gate must RED on every one.
    ok = True
    for which in ('atlantis', 'dropgreece', 'questlog'):
        print('\n--- NEGTEST: plant=%s ---' % which)
        rc = validate(args[0], plant=which)
        if rc == 0:
            print('NEGTEST %s: FAIL - the gate did NOT catch the planted defect' % which)
            ok = False
        else:
            print('NEGTEST %s: PASS - the gate caught it' % which)
    print('\nNEGTEST RESULT: %s' % ('PASS - all 3 planted defects caught' if ok
                                    else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
