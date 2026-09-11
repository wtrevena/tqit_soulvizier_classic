r"""svc_loot_slots - THE ONE IMPLEMENTATION of the monster loot-slot model (R-260).

Shared by the build helper (`apply_svc_patches._svc_guarantee_unique`), the registry
module `tools/patches/phantom_loot_slots.py`, and the two standalone gates
`tools/gate_no_phantom_loot_slots.py` + `tools/gate_guaranteed_drops_measured.py`, so
a number the build prints and a number a gate re-derives come from the same arithmetic.

THE ENGINE MODEL (Toolset Templates.arc -> templates\templatebase\characterloot.tpl,
included by monster.tpl; re-measured for R-258 and again for R-260):

  * exactly ELEVEN equip/loot slot groups exist: Head Torso Forearm LowerBody LeftHand
    RightHand Finger1 Finger2 Misc1 Misc2 Misc3. Each declares `chanceToEquip<S>`
    (real: the percent the SLOT rolls at all), `chanceToEquip<S>Item1..6` (int: RELATIVE
    WEIGHTS among the slot's rows - one row is picked per roll) and `loot<S>Item1..6`
    (file_dbr arrays, one entry per difficulty N/E/L).
  * `Misc4`, `Misc5`, `Misc6` and `Neck` are declared by NOTHING: 0 of 566 templates,
    0 of 74,013 base-AE records, 0 of SV 0.98i / 0.9 / 0.4.1. A field with one of those
    names is dead data the engine never reads. This module STRIPS them and the gate holds
    the arz at zero tolerance.
  * `dropItems` (monster.tpl) drops the equipped items on death.

  So the MEASURED chance that a given loot table drops off a monster is

        chanceToEquip<S>  x  weight(row) / sum(weights of the slot's rows)

  summed over every (slot, row) that names the table. Every gate arm here re-derives
  that from the final bytes; nothing is asserted by hand.

THE R-260 SLOT POLICY (what `wire_misc_drop` does, in order; every outcome is printed and
returned as a disposition, and the roster below pins the shipped one per record):

  A  EMPTY    a Misc slot with chance 0 and all six rows empty (order Misc3, Misc2,
              Misc1): chance = the intended %, row 1 = the table at weight 100.
  B  DORMANT  a Misc slot with chance 0 whose rows still carry tables (they never rolled):
              chance = the intended %, the table on the first free row at weight 100,
              every inherited row MUTED by weight (values kept - retirement protocol).
              Nothing observable is displaced: the slot paid 0 before.
  C  TAKEOVER a LIVE slot already at chance 100 (the R-258 pattern): the table on the
              first free row at 100, the live rows muted by weight. ONLY for an intended
              100%, ONLY on a slot the caller PINS with a written reason (the displaced
              rows are documented per record in docs/WILL_RULINGS.md R-260 and the
              BL-R260 debts). The slot chance is never moved.
  D  SHARE    (intended % < 100 only, and only when the caller opts in) a live slot is
              shared WITHOUT SKEW: the slot chance is raised by exactly the intended %
              and the new row gets weight W * pct / chance, which keeps every existing
              row's ABSOLUTE drop % byte-identical (chance x w_i / W before == after) and
              gives the new table exactly the intended %. The gate proves both halves.
              Requires the compensating weight to be an integer; otherwise the next
              slot in order is tried.
  X  FAIL     anything else raises SystemExit naming the record and printing its full
              slot map. A slot is never shared with its weights skewed, silently or not.

Idempotent: a table already riding a real Misc row at the intended measured % is left
alone (disposition 'kept'); any other pre-existing state is a fail-loud drift.

dtype discipline: this module never passes a dtype to set_field. A brand-new field takes
its dtype from the Python value (float chance -> FLOAT, int weight -> INT, str list ->
STRING), an existing field keeps the dtype it has.
"""
import re

SLOTS = ('Head', 'Torso', 'Forearm', 'LowerBody', 'LeftHand', 'RightHand',
         'Finger1', 'Finger2', 'Misc1', 'Misc2', 'Misc3')
MISC_ORDER = ('Misc3', 'Misc2', 'Misc1')
ROWS = (1, 2, 3, 4, 5, 6)
W_GUARANTEED = 100
TOL = 1e-4          # percent; chance fields are float32 on the wire

# The undeclared variables. Misc4..Misc9 rather than only 4/5/6 so a future "Misc7"
# cannot slip past a gate written for the three we happened to ship.
PHANTOM_RE = re.compile(r'^(?:chanceToEquip|loot)(?:Misc[4-9]|Neck)', re.IGNORECASE)


# ── value helpers (work on the real ArzDatabase and on the negtest stubs) ────
def norm(p):
    return str(p or '').replace('/', '\\').strip().lower()


def _vals(v):
    if v is None:
        return []
    if isinstance(v, (list, tuple)):
        return list(v)
    return [v]


def gv1(db, rec, field, default=None):
    v = _vals(db.get_field_value(rec, field))
    return v[0] if v else default


def gl(db, rec, field):
    return [str(x) for x in _vals(db.get_field_value(rec, field)) if str(x).strip()]


def fnum(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def inum(v, default=0):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def close(a, b, tol=TOL):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def same_tables(got, want):
    return [norm(x) for x in got] == [norm(x) for x in want]


def rec_index(db):
    """{lowercased record name: stored spelling}; the arz stores names lowercase but
    references mixed-case (the R-252 round-3 lesson). Cached on the db by record count."""
    n = len(db.record_names())
    cached = getattr(db, '_r260_rec_index', None)
    if cached is not None and cached[0] == n:
        return cached[1]
    idx = {}
    for name in db.record_names():
        idx.setdefault(norm(name), name)
    try:
        db._r260_rec_index = (n, idx)
    except AttributeError:
        pass
    return idx


def resolve(db, path):
    if not path:
        return None
    if db.has_record(path):
        return path
    return rec_index(db).get(norm(path))


def short(rec):
    return str(rec).rsplit('\\', 1)[-1]


# ── phantom fields ───────────────────────────────────────────────────────────
def _base_keys(db, rec):
    f = db.get_fields(rec)
    if not f:
        return []
    return [str(k).split('###')[0] for k in f]


def phantom_fields(db, rec):
    """Sorted list of the undeclared slot variables carried by `rec`."""
    return sorted({k for k in _base_keys(db, rec) if PHANTOM_RE.match(k)})


def scan_phantom(db):
    """{record: [phantom fields]} over the whole db (0 tolerance is the gate)."""
    out = {}
    for name in db.record_names():
        ph = phantom_fields(db, name)
        if ph:
            out[name] = ph
    return out


def strip_phantom(db, rec):
    """Remove every phantom field from `rec`; returns the list removed. Uses the
    ArzDatabase.remove_field API when present (marks modified + fires listeners) and
    falls back to deleting from the fields dict for the plain-dict negtest stubs."""
    removed = []
    for name in phantom_fields(db, rec):
        if hasattr(db, 'remove_field'):
            if db.remove_field(rec, name):
                removed.append(name)
        else:
            f = db.get_fields(rec)
            for k in [k for k in list(f) if str(k).split('###')[0] == name]:
                del f[k]
                removed.append(name)
            try:
                db._modified.add(rec)
            except AttributeError:
                pass
    return removed


# ── slot model ───────────────────────────────────────────────────────────────
def slot_state(db, rec, slot):
    """{'chance': float, 'rows': {i: (weight:int, loot:[str])}} for rows 1..6.
    A row with neither a weight nor a loot field present reads (0, [])."""
    rows = {}
    for i in ROWS:
        w = inum(gv1(db, rec, 'chanceToEquip%sItem%d' % (slot, i), 0))
        loot = gl(db, rec, 'loot%sItem%d' % (slot, i))
        rows[i] = (w, loot)
    return {'chance': fnum(gv1(db, rec, 'chanceToEquip%s' % slot, 0.0)), 'rows': rows}


def classify(db, rec, slot):
    """'live' (chance > 0), 'dormant' (chance 0 but a row carries weight or loot) or
    'empty' (chance 0, six empty rows)."""
    st = slot_state(db, rec, slot)
    if st['chance'] > 0:
        return 'live'
    for w, loot in st['rows'].values():
        if w > 0 or loot:
            return 'dormant'
    return 'empty'


def free_row(db, rec, slot):
    """First row with weight 0 AND no loot, or None."""
    st = slot_state(db, rec, slot)
    for i in ROWS:
        w, loot = st['rows'][i]
        if w == 0 and not loot:
            return i
    return None


def row_share(db, rec, slot, row):
    """chance x weight(row) / sum(weights), in percent, re-derived from the db."""
    st = slot_state(db, rec, slot)
    total = sum(w for w, _l in st['rows'].values())
    if total <= 0:
        return 0.0
    return st['chance'] * (float(st['rows'][row][0]) / float(total))


def item_shares(db, rec, tables):
    """[(slot, row, pct)] for every (real slot, row) whose loot array IS `tables`."""
    out = []
    for slot in SLOTS:
        st = slot_state(db, rec, slot)
        for i in ROWS:
            if same_tables(st['rows'][i][1], tables):
                out.append((slot, i, row_share(db, rec, slot, i)))
    return out


def item_share(db, rec, tables):
    """The measured % of kills that drop `tables`, summed over every real slot/row."""
    return sum(p for _s, _r, p in item_shares(db, rec, tables))


def describe(db, rec):
    """Multi-line slot map of a record, for fail-loud messages and the build log."""
    lines = []
    for slot in SLOTS:
        st = slot_state(db, rec, slot)
        rows = ['%d:w=%d:%s' % (i, w, ','.join(short(x).replace('.dbr', '') for x in loot) or '-')
                for i, (w, loot) in st['rows'].items() if w or loot]
        lines.append('    %-9s chance=%-7g %s' % (slot, st['chance'], ' | '.join(rows) or '(empty)'))
    ph = phantom_fields(db, rec)
    if ph:
        lines.append('    PHANTOM  %s' % ', '.join(ph))
    return '\n'.join(lines)


# ── the writer ───────────────────────────────────────────────────────────────
LEDGER = []      # every disposition wire_misc_drop produced in this process, in order


def _fail(rec, why, db=None):
    msg = "[R-260 svc_loot_slots] %s: %s" % (short(rec), why)
    if db is not None:
        msg += "\n  slot map of %s:\n%s" % (rec, describe(db, rec))
    raise SystemExit(msg)


def _set(db, rec, field, value):
    db.set_field(rec, field, value)


def _write_row(db, rec, slot, row, tables, weight):
    _set(db, rec, 'loot%sItem%d' % (slot, row), [str(t) for t in tables])
    _set(db, rec, 'chanceToEquip%sItem%d' % (slot, row), int(weight))


def _mute_rows(db, rec, slot, keep_row):
    muted = []
    st = slot_state(db, rec, slot)
    for i, (w, loot) in st['rows'].items():
        if i == keep_row or w == 0:
            continue
        _set(db, rec, 'chanceToEquip%sItem%d' % (slot, i), 0)
        muted.append((i, w, list(loot)))
    return muted


def wire_misc_drop(db, rec, tables, pct, slot=None, why=None, share=False, label=None):
    """Put `tables` (an [n, e, l] array of loot-table or item paths) on a REAL Misc slot
    of `rec` at a MEASURED `pct` percent of kills, by the policy in the module docstring.

    slot   - pin a slot ('Misc1'/'Misc2'/'Misc3'); required for a tier-C takeover and
             then `why` (the per-record displacement note) is required too.
    share  - opt in to the rate-preserving share (tier D) for an intended % below 100.
    Returns the disposition dict (also appended to LEDGER). Raises SystemExit on any
    state the policy does not cover.
    """
    real = resolve(db, rec)
    if real is None:
        raise SystemExit("[R-260 svc_loot_slots] record MISSING: %s" % rec)
    rec = real
    tables = [str(t) for t in tables]
    if len(tables) != 3:
        _fail(rec, "expected a 3-entry [n, e, l] loot array, got %r" % (tables,))
    for t in tables:
        if resolve(db, t) is None:
            _fail(rec, "loot entry does not resolve: %s" % t)
    pct = float(pct)
    if not (0.0 < pct <= 100.0):
        _fail(rec, "intended %% must be in (0, 100], got %r" % pct)
    if slot is not None and slot not in MISC_ORDER:
        _fail(rec, "slot must be one of %s, got %r" % (MISC_ORDER, slot))
    label = label or short(tables[0]).replace('.dbr', '')

    stripped = strip_phantom(db, rec)
    disp = {'record': rec, 'label': label, 'tables': tables, 'pct': pct,
            'stripped': stripped, 'slot': None, 'row': None, 'tier': None,
            'muted': [], 'why': why, 'measured': None}

    # idempotency: already riding a real Misc row?
    existing = [(s, r, p) for s, r, p in item_shares(db, rec, tables)]
    if existing:
        measured = sum(p for _s, _r, p in existing)
        if slot is not None and any(s != slot for s, _r, _p in existing):
            _fail(rec, "%s already rides %r but the caller pins %s" % (label, existing, slot), db)
        if not close(measured, pct):
            _fail(rec, "%s already rides %r at a MEASURED %.4f%%, intended %.4f%% - a "
                       "previous pass left an unmeasured state; refusing to guess"
                  % (label, existing, measured, pct), db)
        disp.update(slot=existing[0][0], row=existing[0][1], tier='kept', measured=measured)
        LEDGER.append(disp)
        return disp

    cands = [slot] if slot else list(MISC_ORDER)
    states = {s: classify(db, rec, s) for s in cands}
    chosen = None

    # A - an empty slot
    for s in cands:
        if states[s] == 'empty':
            chosen = (s, 1, 'A')
            break
    # B - a dormant slot with a free row
    if chosen is None:
        for s in cands:
            if states[s] == 'dormant' and free_row(db, rec, s) is not None:
                chosen = (s, free_row(db, rec, s), 'B')
                break
    # C - takeover of a pinned live slot already at 100 (intended 100 only)
    if chosen is None and slot is not None and states[slot] == 'live':
        st = slot_state(db, rec, slot)
        if close(pct, 100.0) and close(st['chance'], 100.0) and free_row(db, rec, slot) is not None:
            if not why:
                _fail(rec, "a tier-C takeover of live %s needs a written `why` (the "
                           "displaced rows must be documented per record)" % slot, db)
            chosen = (slot, free_row(db, rec, slot), 'C')
    # D - rate-preserving share of a live slot (intended < 100, opt-in)
    if chosen is None and share and pct < 100.0:
        for s in cands:
            if states[s] != 'live':
                continue
            st = slot_state(db, rec, s)
            fr = free_row(db, rec, s)
            total = sum(w for w, _l in st['rows'].values())
            if fr is None or total <= 0:
                continue
            w_new = total * pct / st['chance']
            if abs(w_new - round(w_new)) > 1e-6 or round(w_new) < 1:
                continue
            chosen = (s, fr, 'D')
            break
    if chosen is None:
        _fail(rec, "no slot satisfies the R-260 policy for %s @ %g%% (pinned=%r, share=%r, "
                   "states=%r). EMPTY/DORMANT Misc slots: none usable; a live slot may only be "
                   "taken over at 100%% when pinned with a reason, or shared without skew "
                   "below 100%% when the caller opts in and the compensating weight is an "
                   "integer. Nothing was written." % (label, pct, slot, share, states), db)

    s, row, tier = chosen
    if tier in ('A', 'B'):
        _set(db, rec, 'chanceToEquip%s' % s, float(pct))
        muted = _mute_rows(db, rec, s, row) if tier == 'B' else []
        _write_row(db, rec, s, row, tables, W_GUARANTEED)
    elif tier == 'C':
        muted = _mute_rows(db, rec, s, row)
        _write_row(db, rec, s, row, tables, W_GUARANTEED)
    else:   # D
        st = slot_state(db, rec, s)
        total = sum(w for w, _l in st['rows'].values())
        w_new = int(round(total * pct / st['chance']))
        _set(db, rec, 'chanceToEquip%s' % s, float(st['chance'] + pct))
        _write_row(db, rec, s, row, tables, w_new)
        muted = []
    try:
        db._modified.add(rec)
    except AttributeError:
        pass

    measured = item_share(db, rec, tables)
    if not close(measured, pct):
        _fail(rec, "AFTER WRITE the measured share of %s is %.6f%%, intended %.6f%% (tier %s "
                   "on %s row %d) - the arithmetic did not close" % (label, measured, pct, tier, s, row), db)
    disp.update(slot=s, row=row, tier=tier, muted=muted, measured=measured)
    LEDGER.append(disp)
    return disp


def format_disposition(d):
    tag = {'A': 'EMPTY slot', 'B': 'DORMANT slot, inherited rows muted',
           'C': 'TAKEOVER of a live 100%% slot, live rows muted', 'D': 'SHARE, rate-preserving',
           'kept': 'already wired'}.get(d['tier'], d['tier'])
    s = ("  [R-260] %-28s -> %s row %d @ MEASURED %.4f%% (intended %g%%; tier %s: %s)"
         % (short(d['record']), d['slot'], d['row'], d['measured'], d['pct'], d['tier'], tag))
    if d['muted']:
        s += "; muted %s" % ', '.join('row %d w%d %s' % (i, w, ','.join(short(x) for x in loot))
                                       for i, w, loot in d['muted'])
    if d['stripped']:
        s += "; stripped dead %s" % ','.join(d['stripped'])
    return s


# ── THE ROSTER: the 32 phantom carriers of build102 `7dad9a8a`, re-homed ─────
_LT = r'records\item\loottables'
_RR = [_LT + r'\animalrelics\svc_revelersruse\%s_revelersruse.dbr' % t for t in ('01', '02', '03')]
_SS = [_LT + r'\animalrelics\svc_sepulchralscale\%s_sepulchralscale.dbr' % t for t in ('01', '02', '03')]
_ST = [_LT + r'\animalrelics\svc_sanguinetithe\%s_sanguinetithe.dbr' % t for t in ('01', '02', '03')]
_EH = [_LT + r'\animalrelics\svc_erebanheartstone\%s_erebanheartstone.dbr' % t for t in ('01', '02', '03')]
RITE_TABLE = _LT + r'\svc\svc_rite_guaranteed.dbr'
DEVOURER_MASTER = _LT + r'\svc\svc_devourer_misc4_master.dbr'
RANT_TABLE = _LT + r'\svc\toxeus_rant_perplayer.dbr'
_BOUGH = [r'records\item\equipmentamulet\svc_goldenbough_%s.dbr' % t for t in 'nel']
_LETHE = [r'records\item\equipmentjewelry\amulet\svc_uber\lethesdraught.dbr'] * 3
_MASK = [r'records\item\equipmenthelm\svc_maskofdread_%s.dbr' % t for t in 'nel']
DEVOURER = r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr'
DEVOURER_SOUL_TABLES = [_LT + r'\svc\svc_devourersoul_guaranteed_%s.dbr' % t for t in 'nel']

_SATYR = r'records\creature\monster\satyr\ar_archer_%02d.dbr'
_WYRM = r'records\creature\monster\sepulchralwyrm\%s.dbr'
_SILENI = r'records\drxcreatures\bloodabomination\%s.dbr'
_BRUTE = r'records\xpack\creatures\monster\troglodyte\em_brute_%d.dbr'


def _e(label, record, tables, pct, slot, row, tier, **kw):
    d = {'label': label, 'record': record, 'tables': list(tables), 'pct': float(pct),
         'slot': slot, 'row': row, 'tier': tier}
    d.update(kw)
    return d


# tier D pins: the slot's chance and weights BEFORE the share, read off build102 so the
# gate can prove every pre-existing row's absolute % did not move. A future lane that
# retunes those rows must update the pin in the same commit (the R-252 E2d discipline).
_D_AMULET_05 = dict(base_chance=0.5, base_rows={1: 5000, 5: 4})
_D_AMULET_10 = dict(base_chance=1.0, base_rows={1: 5000, 5: 4})
_D_AMULET_20 = dict(base_chance=2.0, base_rows={1: 5000, 5: 8})

ROSTER = (
    # The Reveler's Ruse (turtleshell_relics, 7%) on the six Satyr Archers
    [_e("Reveler's Ruse", _SATYR % i, _RR, 7.0, 'Misc3', 2, 'B') for i in (1, 2, 3, 4)]
    + [_e("Reveler's Ruse", _SATYR % i, _RR, 7.0, 'Misc3', 2, 'D', **_D_AMULET_05) for i in (5, 6)]
    # Sepulchral Scale (Group G, 7%) on the 4 champion worms + their 4 frostwyrm twins
    + [_e('Sepulchral Scale', _WYRM % ('um_sepulchralwyrm_%s' % lv), _SS, 7.0, 'Misc3', 2, 'B')
       for lv in ('31', '34', '37', '40')]
    + [_e('Sepulchral Scale', _WYRM % ('svc_frostwyrm_%s' % lv), _SS, 7.0, 'Misc3', 2, 'B')
       for lv in ('31', '34', '37', '40')]
    # Sanguine Tithe (A3, 7%) on the nine Sileni combat bodies
    + [_e('Sanguine Tithe', _SILENI % n, _ST, 7.0, 'Misc3', 2, 'D', **_D_AMULET_05)
       for n in ('01_bladedancer_35', '01_bladedancer_36', '01_bladedancer_37',
                 '02_spearrunner_37', '02_spearrunner_38', '02_spearrunner_39')]
    + [_e('Sanguine Tithe', _SILENI % n, _ST, 7.0, 'Misc3', 2, 'D', **_D_AMULET_10)
       for n in ('03_ravager_38', '03_ravager_39', '03_ravager_40')]
    # Ereban Heartstone (C5, 10%) on the two Ereban brutes
    + [_e('Ereban Heartstone', _BRUTE % lv, _EH, 10.0, 'Misc3', 2, 'D', **_D_AMULET_20)
       for lv in (43, 45)]
    # the guaranteed seven, minus the Devourer (withheld - see below)
    + [_e('Rite of the Undivided (R-13)',
          r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr',
          [RITE_TABLE] * 3, 100.0, 'Misc1', 3, 'C'),
       _e('Rite of the Undivided (R-92)',
          r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr',
          [RITE_TABLE] * 3, 100.0, 'Misc1', 3, 'C'),
       _e('Rite of the Undivided (R-92, endless)',
          r'records\creature\monster\shadowstalker\um_toxeus_hunt_l_99.dbr',
          [RITE_TABLE] * 3, 100.0, 'Misc1', 3, 'C'),
       _e('Golden Bough (R-231)',
          r'records\xpack\creatures\monster\bosses\02_charon\um_charonform2_ferryman_99.dbr',
          _BOUGH, 100.0, 'Misc3', 4, 'B'),
       _e("Lethe's Draught",
          r'records\xpack\creatures\monster\epiales\um_mnemophage_99.dbr',
          _LETHE, 100.0, 'Misc2', 4, 'C'),
       _e('Mask of the Waking Dread',
          r'records\xpack\creatures\monster\epiales\um_ephialtes_99.dbr',
          _MASK, 100.0, 'Misc2', 4, 'C')]
)

# The Devourer's phantom channel carried the R-13 rant+rite master (a pick-one 50/50).
# He has NO empty or dormant Misc slot, Misc1 + Finger2 are frozen byte-identical to
# build102 by BL-R258-DEBT-1, and the only takeovers left (Misc2 at 18, Misc3 at 50)
# would displace live hand-designed rolls for a 50% rite - so the channel is WITHHELD
# (dead fields stripped, records kept) and re-homed by Will's call: BL-R260-DEBT-1.
WITHHELD = (
    {'label': 'Devourer rant + rite master (R-13, R-15/17)', 'record': DEVOURER,
     'tables': [DEVOURER_MASTER] * 3, 'debt': 'BL-R260-DEBT-1'},
)


def check_no_phantom(db):
    """Gate arm: every record must carry ZERO phantom slot variables."""
    found = scan_phantom(db)
    return ["PHANTOM %s carries %s" % (short(r), ', '.join(f)) for r, f in sorted(found.items())]


def check_roster(db):
    """Gate arm: every roster record delivers its item at the intended MEASURED % on
    the pinned real slot/row, with the tier's side conditions; the withheld record
    carries nothing phantom and references its master nowhere. Returns problems."""
    P = []
    for e in ROSTER:
        rec = resolve(db, e['record'])
        lab = '%s on %s' % (e['label'], short(e['record']))
        if rec is None:
            P.append("MISSING record: %s" % e['record'])
            continue
        ph = phantom_fields(db, rec)
        if ph:
            P.append("%s: still carries phantom %s" % (lab, ', '.join(ph)))
        if not inum(gv1(db, rec, 'dropItems', 0)):
            P.append("%s: dropItems is off - equipped items never hit the ground" % lab)
        for t in e['tables']:
            if resolve(db, t) is None:
                P.append("%s: loot entry does not resolve: %s" % (lab, t))
        shares = item_shares(db, rec, e['tables'])
        measured = sum(p for _s, _r, p in shares)
        if not close(measured, e['pct']):
            P.append("%s: MEASURED %.4f%% of kills, intended %.4f%% (rides %r)"
                     % (lab, measured, e['pct'], shares))
        if [(s, r) for s, r, _p in shares] != [(e['slot'], e['row'])]:
            P.append("%s: rides %r, the roster pins %s row %d"
                     % (lab, [(s, r) for s, r, _p in shares], e['slot'], e['row']))
            continue
        st = slot_state(db, rec, e['slot'])
        if e['tier'] in ('A', 'B', 'C'):
            if not close(st['chance'], e['pct']):
                P.append("%s: chanceToEquip%s = %r, expected %g" % (lab, e['slot'], st['chance'], e['pct']))
            if st['rows'][e['row']][0] != W_GUARANTEED:
                P.append("%s: row %d weight %r, expected %d"
                         % (lab, e['row'], st['rows'][e['row']][0], W_GUARANTEED))
            rivals = [(i, w) for i, (w, _l) in st['rows'].items() if i != e['row'] and w > 0]
            if rivals:
                P.append("%s: %s carries competing non-zero rows %r - the item is no longer "
                         "the slot's only pick" % (lab, e['slot'], rivals))
        elif e['tier'] == 'D':
            want_chance = e['base_chance'] + e['pct']
            if not close(st['chance'], want_chance):
                P.append("%s: chanceToEquip%s = %r, expected %g (= %g base + %g intended)"
                         % (lab, e['slot'], st['chance'], want_chance, e['base_chance'], e['pct']))
            base_total = float(sum(e['base_rows'].values()))
            for i, w in e['base_rows'].items():
                want = e['base_chance'] * w / base_total
                got = row_share(db, rec, e['slot'], i)
                if st['rows'][i][0] != w:
                    P.append("%s: %s row %d weight %r, the pre-existing row's weight was %d "
                             "and must not move" % (lab, e['slot'], i, st['rows'][i][0], w))
                if not close(got, want, 1e-6):
                    P.append("%s: %s row %d now drops %.6f%% of kills, was %.6f%% before the "
                             "share - the share SKEWED an existing row" % (lab, e['slot'], i, got, want))
            others = [i for i, (w, _l) in st['rows'].items()
                      if w > 0 and i != e['row'] and i not in e['base_rows']]
            if others:
                P.append("%s: %s grew unpinned rows %r" % (lab, e['slot'], others))
        else:
            P.append("%s: roster tier %r unknown" % (lab, e['tier']))
    for w in WITHHELD:
        rec = resolve(db, w['record'])
        lab = '%s on %s' % (w['label'], short(w['record']))
        if rec is None:
            P.append("MISSING record: %s" % w['record'])
            continue
        ph = phantom_fields(db, rec)
        if ph:
            P.append("%s: still carries phantom %s" % (lab, ', '.join(ph)))
        shares = item_shares(db, rec, w['tables'])
        if shares:
            P.append("%s: WITHHELD under %s but rides %r - a re-homing needs its own ruling "
                     "and a roster entry, not a silent wire" % (lab, w['debt'], shares))
        for t in w['tables']:
            if resolve(db, t) is None:
                P.append("%s: the withheld table was DELETED (%s) - retirement protocol: "
                         "records stay, only the dead channel goes" % (lab, t))
    return P


def check_devourer_freeze(db):
    """The BL-R258-DEBT-1 freeze, restated so this lane's gate says it too: the
    Devourer's Finger2 pin and Misc1 chute are exactly R-258's."""
    P = []
    rec = resolve(db, DEVOURER)
    if rec is None:
        return ["MISSING record: %s" % DEVOURER]
    if not close(gv1(db, rec, 'chanceToEquipFinger2', 0.0), 100.0):
        P.append("Devourer chanceToEquipFinger2 = %r, R-243's pin is 100" % gv1(db, rec, 'chanceToEquipFinger2'))
    if not close(item_share(db, rec, DEVOURER_SOUL_TABLES), 100.0):
        P.append("Devourer R-258 Misc1 soul chute measures %.4f%%, expected 100"
                 % item_share(db, rec, DEVOURER_SOUL_TABLES))
    if [(s, r) for s, r, _p in item_shares(db, rec, DEVOURER_SOUL_TABLES)] != [('Misc1', 3)]:
        P.append("Devourer R-258 soul tables ride %r, expected Misc1 row 3"
                 % item_shares(db, rec, DEVOURER_SOUL_TABLES))
    return P
