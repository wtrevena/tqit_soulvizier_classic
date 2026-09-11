r"""GATE (R-261): every restored chest pays AT LEAST its SV 0.98i original - COUNT and QUALITY,
measured on the WIRE the player opens, against the upstream arz itself.

WILL, VERBATIM (2026-08-13/14, BL-W0814-2/-5/-7/-11/-13):
  "wtf did you do to all the chests like toxeus the murderer devourer of blood's stash? Revert
   it back to what it was dropping in the original sv you nerfed the fuck out of it"
  "the obsidian hoard chests ... are still nerfed too much. if these share the same record as
   the chest - toxeus the murderer, devourer of blood hidden's chest we need to seperate those
   records since those should be tuned differently"
  "Another terrible chest aphoryteus (spelled wrong) dread hoard is a terrible chest"
  "literally just dropped two items one thing of gold and incarnation of guan-yu's grace. are
   you kidding me. this is outrageous"
  "same problem with the chest guarded by tantalus"
  "the gift box in the secret places need to increase the number of items dropped by 3x"

WHY A FIFTH CHEST GATE EXISTS (the four before it were all green while the chests were gutted):
  `gate_chest_loot_breadth` (R-180) audits WHAT a table can pay; `gate_loot_distribution` (R-181)
  in WHAT PROPORTIONS; `gate_loot_volume` (R-240) HOW MUCH, against the mod's OWN bands;
  `gate_uber_hoard_generosity` (R-251) WHETHER THE TUNED TABLE IS THE ONE THAT OPENS, and pins the
  hoard family at the mod's authored value. None of them ever compared a chest to the thing Will
  compares it to: WHAT THE ORIGINAL SOULVIZIER PAID. The b42 repoint (2026-07-13) and the R-240
  sweep (2026-08-11) each passed every gate of their day because every band was a mod-authored
  number that the nerf itself could re-author. This gate's floor is NOT authored here: it is READ
  from `upstream/soulvizier_098i/Database/database.arz` on every run, and the only constants in
  this file are PINS that prove the upstream arz is the one the floor was derived on.

WHAT IT ASSERTS (per chest, per tier, solo `numberOfPlayers = 1`)
  P1 WIRE      the chest record the player opens names the table the SV original names (the
               SV-original class) / its OWN `svc_<fam>hoard_loot_<tier>` (the hoard class).
  P2 COUNT     spawn iterations min, max and mean, and the expected items per open
               (S x sum of group chances, the house model in `svc_loot_distribution.ChestProfile`)
               are >= the SV original's; the Secret Present box is EXACTLY 3.0x (Will's number);
               the hoard family is >= the R-251 floor (`svc_uber_hoards.HOARD_MIN_EQ/MAX_EQ`).
  P3 CHANCES   every loot-group chance is >= the SV original's (so the count floor holds under
               BOTH engine readings of `FixedItemLoot` - independent groups per iteration, or one
               group per iteration); the hoard family keeps its guaranteed row at >= 100.
  P4 QUALITY   per loot group, the weight share on `unique` rows is >= the SV original's, and
               every SV member row is still present at weight > 0 (a superset, never a swap).
  P5 FORM      both equations keep `numberOfPlayers` (the build28/29/30 "opens and drops NOTHING"
               P0) - re-asserted here because a bare literal can evaluate to a big number and pass
               P2 while the engine evaluates it to 0.
  P6 PIN       the upstream table read for the floor carries the pinned SV equations, so a
               modified or wrong upstream arz cannot silently lower the floor.
  SURFACED, NOT ASSERTED: Leinth's chest (`bosschest_leinth_0N`, an SV-original DRX chest) sits
               under the R-242 apex-orb freeze at ~1/9 of its SV volume. Two Will statements one day
               apart point opposite ways for that one record (R-242 08-12 "keep their current" vs
               08-13 "all the chests ... revert to original sv"). Printed every run as an INFO row
               with its debt id; it becomes an assertion only by a Will ruling (`BL-R261-DEBT-1`).

    py tools/gate_chest_generosity_sv_parity.py [arz] [--sv <sv098i arz>]   # exit 1 on a finding
    py tools/gate_chest_generosity_sv_parity.py [arz] --table                # the parity table
    py tools/gate_chest_generosity_sv_parity.py [arz] --negtest              # planted re-nerfs
    py tools/gate_chest_generosity_sv_parity.py [arz] --control <arz>        # a pre-fix arz must RED

ANTI-INERT: `--negtest` plants every re-nerf this repo has actually shipped - the b42 repoint of a
hoard chest to `boss_default_*`, the R-240 trim values on the stash / a hoard / the gift box, a
group chance under SV, a unique row zeroed, a guaranteed row demoted, a bare-literal equation -
INTO THE REAL build103 ARZ IN MEMORY and demands the gate RED on each and return GREEN after each
restoration. The post-write battery in `tools/build_svc_database.py` calls `validate()` below on
the written artifact under `SVC_REQUIRE_GATES=1`.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from arz_patcher import ArzDatabase          # noqa: E402
import svc_loot_breadth as SLB                # noqa: E402
import svc_loot_distribution as SLD           # noqa: E402
import svc_uber_hoards as SUH                 # noqa: E402

DEFAULT_ARZ = HERE.parent / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'
CONTAINER = SUH.CONTAINER_DIR
TIERS = SUH.TIERS
EPS = 1e-6

# ─────────────────────────────────────────────────────────────────────────────
# THE ROSTER
#
# SV-ORIGINAL class: the chest exists in SV 0.98i; its floor is READ from the upstream arz.
#   factor = the documented multiple of the SV volume (1.0 = parity, 3.0 = Will's gift-box
#   number); exact = the volume must EQUAL factor x SV, not merely reach it.
# HOARD class: no SV original exists (mod-authored); derived from the R-251 name shape, never
#   typed, so a new hoard is inside this gate the moment it is named.
# ─────────────────────────────────────────────────────────────────────────────
SV_ORIGINALS = (
    {'label': "the Devourer's stash", 'why': 'R-247.7a: SV volume verbatim, composition a superset',
     'chest': CONTAINER + r'\hidden_bloodcave_chest_%s.dbr',
     'table': CONTAINER + r'\loottable_hidden_bloodcave_%s.dbr',
     'factor': 1.0, 'exact': False},
    {'label': 'the Secret Present box', 'why': 'BL-W0814-7: item count exactly 3x SV',
     'chest': CONTAINER + r'\sp_chest_%s.dbr',
     'table': CONTAINER + r'\loottable_sp_%s.dbr',
     'factor': 3.0, 'exact': True},
)

# P6 PINS: the SV 0.98i equations the floor was derived on (measured on the upstream arz md5
# `check_build_inputs` verifies). A floor read from an arz that does not carry these is a floor
# read from the wrong file, and the gate says so instead of asserting against it.
SV_PINS = {
    CONTAINER + r'\loottable_hidden_bloodcave_%s.dbr':
        ('(3+(1.8*numberOfPlayers))*3.8', '(3+(1.8*numberOfPlayers))*4.1'),
    CONTAINER + r'\loottable_sp_%s.dbr':
        ('(1+(1.8*numberOfPlayers))*1.8', '(1+(1.8*numberOfPlayers))*2.1'),
}

# SURFACED ONLY (BL-R261-DEBT-1): Leinth's chest, an SV-original DRX chest frozen as an orb.
LEINTH_CHESTS = (CONTAINER + r'\bosschest_leinth_01_normal.dbr',
                 CONTAINER + r'\bosschest_leinth_02_epic.dbr',
                 CONTAINER + r'\bosschest_leinth_03_legendary.dbr')

# The b42 destination every hoard chest was repointed to (P1's named cause).
BASE_LOOT_MARK = SUH.BASE_LOOT_MARK


def _short(p):
    return SLB._n(p).rsplit('\\', 1)[-1]


def _unique(path):
    return 'unique' in SLB._n(path)


def profile(d, table):
    """The measured pay profile of ONE FixedItemLoot table, solo.

    Same arithmetic as `svc_loot_distribution.ChestProfile` (S x sum of live group chances) so
    this gate and the R-181/R-240 gates can never disagree about what a table pays; plus the
    per-group composition this gate compares to SV.
    """
    real = d.real(table)
    if not real:
        return None
    f = d.fields(real)
    mn_eq = str((f.get('numSpawnMinEquation') or [''])[0])
    mx_eq = str((f.get('numSpawnMaxEquation') or [''])[0])
    mn = SLD.eval_spawn(mn_eq, 1)
    mx = SLD.eval_spawn(mx_eq, 1)
    mn = 0.0 if mn is None else mn
    mx = 0.0 if mx is None else mx
    groups = {}
    mass = 0.0
    for g in range(1, 7):
        c = f.get('loot%dChance' % g)
        chance = float(c[0]) if c else 0.0
        rows = {}
        for i in range(1, 7):
            nm = f.get('loot%dName%d' % (g, i))
            wt = f.get('loot%dWeight%d' % (g, i))
            if nm and isinstance(nm[0], str) and nm[0].strip():
                w = float(wt[0]) if wt else 0.0
                if w > 0:
                    rows[SLB._n(nm[0])] = rows.get(SLB._n(nm[0]), 0.0) + w
        tot = sum(rows.values())
        ushare = (sum(w for p, w in rows.items() if _unique(p)) / tot) if tot > 0 else 0.0
        groups[g] = {'chance': chance, 'rows': rows, 'total': tot, 'unique_share': ushare}
        if tot > 0:
            mass += chance / 100.0
    mean = (mn + mx) / 2.0
    return {'real': real, 'min_eq': mn_eq, 'max_eq': mx_eq, 'min': mn, 'max': mx, 'mean': mean,
            'mass': mass, 'expected': mean * mass, 'expected_onepick': mean * min(1.0, mass),
            'groups': groups}


def _ge(a, b):
    return a + EPS >= b


def _chest_table(d, chest):
    real = d.real(chest)
    if not real:
        return None, None
    return real, SLB._n(d.gv(real, 'tables') or '')


def problems_sv_originals(d, sv, report):
    """P1-P6 for the SV-original class. `sv` may be None (then only the pins are reported)."""
    out = []
    rows = report.setdefault('rows', [])
    for spec in SV_ORIGINALS:
        for tier in TIERS:
            chest = spec['chest'] % tier
            table = spec['table'] % tier
            lab = '%s %s' % (spec['label'], tier)
            creal, got = _chest_table(d, chest)
            # P1 the wire, against the SV chest's own wire
            if creal is None:
                out.append('P1 %s: chest %s is MISSING from the build' % (lab, _short(chest)))
                continue
            want = SLB._n(table)
            if sv is not None:
                _sreal, sgot = _chest_table(sv, chest)
                if sgot:
                    want = sgot
            if got != want:
                out.append('P1 %s: %s names %s; the SV original opens %s%s'
                           % (lab, _short(chest), _short(got) or '(nothing)', _short(want),
                              ' - the b42 `_svc_standardize_boss_chests` repoint shape'
                              if BASE_LOOT_MARK in got else ''))
                continue
            b = profile(d, got)
            if b is None:
                out.append('P1 %s: %s names %s, which does not exist' % (lab, _short(chest), _short(got)))
                continue
            # P5 form
            for fld, eq in (('numSpawnMinEquation', b['min_eq']), ('numSpawnMaxEquation', b['max_eq'])):
                if 'numberOfPlayers' not in eq:
                    out.append('P5 %s: %s.%s = %r lost its `numberOfPlayers` term (the build28/29/30 '
                               'P0: the engine evaluates a bare literal to 0 and the chest drops '
                               'NOTHING)' % (lab, _short(got), fld, eq))
            # P6 the pin on the upstream table
            pins = SV_PINS.get(spec['table'])
            s = profile(sv, table) if sv is not None else None
            if sv is not None and s is None:
                out.append('P6 %s: the SV 0.98i arz has no %s - the floor cannot be read; wrong '
                           'upstream file?' % (lab, _short(table)))
                continue
            if s is not None and pins and (s['min_eq'], s['max_eq']) != tuple(pins):
                out.append('P6 %s: the upstream %s reads %r/%r, not the pinned SV equations %r/%r; '
                           'the floor would be derived from the wrong file'
                           % (lab, _short(table), s['min_eq'], s['max_eq'], pins[0], pins[1]))
                continue
            if s is None:
                continue
            fac = spec['factor']
            rows.append((lab, s, b, fac))
            # P2 count
            for key in ('min', 'max', 'mean', 'expected'):
                want_v = s[key] * fac
                if spec['exact'] and key in ('min', 'max'):
                    if abs(b[key] - want_v) > EPS:
                        out.append('P2 %s: %s %s = %.4f, must be EXACTLY %.1fx the SV %.4f = %.4f '
                                   '(%s)' % (lab, _short(got), key, b[key], fac, s[key], want_v,
                                             spec['why']))
                elif not _ge(b[key], want_v):
                    out.append('P2 %s: %s %s = %.4f is UNDER the SV original %.4f x %.1f = %.4f '
                               '(%s)' % (lab, _short(got), key, b[key], s[key], fac, want_v,
                                         spec['why']))
            # P3 chances, P4 quality
            for g in range(1, 7):
                sg, bg = s['groups'][g], b['groups'][g]
                if sg['total'] <= 0:
                    continue
                if not _ge(bg['chance'], sg['chance']):
                    out.append('P3 %s: %s loot%dChance = %.3f is UNDER the SV original %.3f'
                               % (lab, _short(got), g, bg['chance'], sg['chance']))
                if bg['total'] <= 0:
                    out.append('P4 %s: %s loot%d has NO live rows; SV carries %d'
                               % (lab, _short(got), g, len(sg['rows'])))
                    continue
                if not _ge(bg['unique_share'], sg['unique_share']):
                    out.append('P4 %s: %s loot%d unique share %.4f is UNDER the SV original %.4f '
                               '(quality)' % (lab, _short(got), g, bg['unique_share'],
                                              sg['unique_share']))
                for p in sg['rows']:
                    if p not in bg['rows']:
                        out.append('P4 %s: %s loot%d lost the SV member %s (weight 0 or removed); '
                                   'a restored chest is a SUPERSET of its original'
                                   % (lab, _short(got), g, _short(p)))
    return out


def problems_hoards(d, db, report):
    """P1/P2/P3/P5 for the R-251 hoard family (floor = the R-251 authored volume, never typed here)."""
    out = []
    floor_mn = SLD.eval_spawn(SUH.HOARD_MIN_EQ, 1) or 0.0
    floor_mx = SLD.eval_spawn(SUH.HOARD_MAX_EQ, 1) or 0.0
    chests = SUH.chests(db)
    report['hoards'] = len(chests)
    worst = None
    for key in sorted(chests):
        real, fam, tier = chests[key]
        lab = 'hoard %s %s' % (fam, tier)
        want = SLB._n(SUH.table_for(real))
        got = SLB._n(d.gv(real, 'tables') or '')
        if got != want:
            out.append('P1 %s: %s names %s, not its OWN %s%s'
                       % (lab, _short(real), _short(got) or '(nothing)', _short(want),
                          ' - the b42 `_svc_standardize_boss_chests` repoint to Cyclops-grade '
                          'base loot, the ONE shared cause behind BL-W0814-2/-5/-11/-13'
                          if BASE_LOOT_MARK in got else ''))
            continue
        b = profile(d, got)
        if b is None:
            out.append('P1 %s: %s names %s, which does not exist' % (lab, _short(real), _short(got)))
            continue
        for fld, eq in (('numSpawnMinEquation', b['min_eq']), ('numSpawnMaxEquation', b['max_eq'])):
            if 'numberOfPlayers' not in eq:
                out.append('P5 %s: %s.%s = %r lost its `numberOfPlayers` term (build28/29/30 P0)'
                           % (lab, _short(got), fld, eq))
        if not _ge(b['min'], floor_mn) or not _ge(b['max'], floor_mx):
            out.append('P2 %s: %s spawns %.4f..%.4f solo, UNDER the R-251 floor %.4f..%.4f '
                       '(%s / %s) - the R-240 trim shape that starved the general-guard hoards'
                       % (lab, _short(got), b['min'], b['max'], floor_mn, floor_mx,
                          SUH.HOARD_MIN_EQ, SUH.HOARD_MAX_EQ))
        if not _ge(b['groups'][3]['chance'], 100.0):
            out.append('P3 %s: %s loot3Chance = %.3f, the guaranteed unique+relic row must stay '
                       '>= 100 (what Will opened as "one thing of gold and incarnation of '
                       "guan-yu's grace\")" % (lab, _short(got), b['groups'][3]['chance']))
        if worst is None or b['mean'] < worst[0]:
            worst = (b['mean'], _short(got))
    report['worst_hoard'] = worst
    return out


def surfaced(d, sv):
    """INFO rows this gate prints but does not assert (BL-R261-DEBT-1)."""
    rows = []
    for chest in LEINTH_CHESTS:
        creal, got = _chest_table(d, chest)
        if creal is None:
            continue
        b = profile(d, got) if got else None
        s, sgot = None, None
        if sv is not None:
            _sr, sgot = _chest_table(sv, chest)
            s = profile(sv, sgot) if sgot else None
        rows.append((_short(chest), _short(got), b, _short(sgot) if sv is not None and sgot else '-', s))
    return rows


def problems_for(db, sv_db, report=None):
    rep = report if report is not None else {}
    d = SLD.Db(db)
    sv = SLD.Db(sv_db) if sv_db is not None else None
    P = problems_sv_originals(d, sv, rep)
    P += problems_hoards(d, db, rep)
    rep['surfaced'] = surfaced(d, sv)
    return P


def print_table(report, title):
    print('  %s' % title)
    print('  %-28s %9s %9s %7s %7s %8s %8s %7s' % (
        'chest', 'S sv', 'S build', 'mass sv', 'mass b', 'E[it] sv', 'E[it] b', 'factor'))
    for lab, s, b, fac in report.get('rows', []):
        print('  %-28s %9.3f %9.3f %7.3f %7.3f %8.3f %8.3f %7.1f'
              % (lab, s['mean'], b['mean'], s['mass'], b['mass'], s['expected'], b['expected'], fac))
    w = report.get('worst_hoard')
    if w:
        print('  %-28s %9s %9.3f   (R-251 floor %.3f; %d chests by name shape)'
              % ('leanest hoard: ' + w[1], '-', w[0],
                 ((SLD.eval_spawn(SUH.HOARD_MIN_EQ, 1) or 0) + (SLD.eval_spawn(SUH.HOARD_MAX_EQ, 1) or 0)) / 2,
                 report.get('hoards', 0)))
    for chest, got, b, sgot, s in report.get('surfaced', []):
        print("  SURFACED, not asserted (BL-R261-DEBT-1): %s opens %s S=%.3f mass=%.3f%s - Leinth's "
              "chest is frozen as an orb by R-242 (Will 08-12) and is an SV-original chest under "
              "Will 08-13; needs a ruling"
              % (chest, got, b['mean'] if b else 0.0, b['mass'] if b else 0.0,
                 ('; SV opens %s S=%.3f mass=%.3f' % (sgot, s['mean'], s['mass'])) if s else ''))


def load_sv(sv_arz=None):
    """The upstream SV 0.98i arz through the one preflight resolver.

    NOTE (`BL-R261-DEBT-6`): `resolve()` md5-verifies the FALLBACK ladder only. A path
    supplied explicitly here (`--sv`, or argv into the build) short-circuits the ladder
    and is used AS-IS, UNHASHED, by that module's documented design - so on an explicit
    path the floor is guarded by P6's equation pin alone, not by a hash.
    """
    import check_build_inputs as CBI
    try:
        p = CBI.resolve('sv098i_arz', sv_arz, verbose=False)
    except CBI.MissingInput as e:
        print('gate_chest_generosity_sv_parity: cannot resolve the SV 0.98i arz:\n%s' % e)
        return None
    return ArzDatabase.from_arz(Path(p))


def validate(arz_path, sv_arz=None, sv_db=None):
    """Builder entry point: 0 = PASS, 1 = FAIL, 2 = cannot run (no SV arz to read the floor)."""
    arz = Path(arz_path)
    if not arz.exists():
        print('gate_chest_generosity_sv_parity: arz not found: %s' % arz)
        return 2
    if sv_db is None:
        sv_db = load_sv(sv_arz)
        if sv_db is None:
            return 2
    db = ArzDatabase.from_arz(arz)
    rep = {}
    P = problems_for(db, sv_db, rep)
    print_table(rep, 'SV-PARITY TABLE on %s (solo; E[it] = S x sum of live group chances)' % arz.name)
    if P:
        for p in P[:80]:
            print('  R-261 OFFENDER: %s' % p)
        print('gate_chest_generosity_sv_parity: FAIL (%d problem(s))' % len(P))
        return 1
    print("gate_chest_generosity_sv_parity: PASS - %d SV-original chest tiers pay >= their SV 0.98i "
          "original on count, chances and unique share (the Secret Present box exactly 3.0x), "
          "%d hoard chests open their own table at or above the R-251 floor with the guaranteed "
          "row intact (leanest %s at %.2f iterations)"
          % (len(rep.get('rows', [])), rep.get('hoards', 0),
             (rep.get('worst_hoard') or (0, '-'))[1], (rep.get('worst_hoard') or (0, '-'))[0]))
    return 0


def control(arz_path, sv_db):
    """A pre-fix artifact (e.g. build92 b888f022) must be RED here, or the gate is inert."""
    db = ArzDatabase.from_arz(Path(arz_path))
    rep = {}
    P = problems_for(db, sv_db, rep)
    print_table(rep, 'CONTROL on %s (expected: RED)' % Path(arz_path).name)
    if P:
        print('gate_chest_generosity_sv_parity: ANTI-INERT CONTROL OK - the control arz is RED '
              '(%d problem(s)); first: %s' % (len(P), P[0][:100]))
        return 0
    print('gate_chest_generosity_sv_parity: ANTI-INERT CONTROL FAILED - the control arz is GREEN')
    return 1


def negtest(arz_path, sv_db):
    """Planted re-nerfs on the REAL arz in memory: each must RED, each restoration must GREEN."""
    db = ArzDatabase.from_arz(Path(arz_path))
    if problems_for(db, sv_db):
        print('  negtest: the input arz is already RED; point it at a post-R-251 arz')
        return 1
    lk = SLB.Lookup(db)
    stash = lk.real(CONTAINER + r'\loottable_hidden_bloodcave_01.dbr')
    gift = lk.real(CONTAINER + r'\loottable_sp_02.dbr')
    gift_chest = lk.real(CONTAINER + r'\sp_chest_03.dbr')
    stash_chest = lk.real(CONTAINER + r'\hidden_bloodcave_chest_02.dbr')
    hoard_chest = lk.real(CONTAINER + r'\svc_dorushoard_01.dbr')
    hoard_tab = lk.real(CONTAINER + r'\svc_tantalushoard_loot_01.dbr')
    eph_tab = lk.real(CONTAINER + r'\svc_ephialteshoard_loot_03.dbr')
    obs_tab = lk.real(CONTAINER + r'\svc_obsidianhoard_loot_02.dbr')
    plants = (
        ("the b42 repoint: Propontis (Dorus) hoard chest -> boss_default_41-43", hoard_chest, 'tables',
         r'records\item\containers\defaultloot\boss_default_41-43.dbr', 'P1'),
        ("the stash chest re-wired onto a hoard table (a share)", stash_chest, 'tables',
         CONTAINER + r'\svc_obsidianhoard_loot_02.dbr', 'P1'),
        ("the R-240 trim on the stash: *3.8 -> *0.323", stash, 'numSpawnMinEquation',
         '(3+(1.8*numberOfPlayers))*0.323', 'P2'),
        ("the stash max under SV: *4.1 -> *4.0", stash, 'numSpawnMaxEquation',
         '(3+(1.8*numberOfPlayers))*4.0', 'P2'),
        ("the gift box un-tripled: *6.3 -> *2.1 (the SV value, not Will's 3x)", gift,
         'numSpawnMaxEquation', '(1+(1.8*numberOfPlayers))*2.1', 'P2'),
        ("the gift box OVER 3x: *5.4 -> *5.5 (exact means exact)", gift, 'numSpawnMinEquation',
         '(1+(1.8*numberOfPlayers))*5.5', 'P2'),
        ("the R-240 CANON_TRIM on a hoard: *2.4 -> *0.2188", hoard_tab, 'numSpawnMinEquation',
         '(3+(1.8*numberOfPlayers))*0.2188', 'P2'),
        ("a hoard's guaranteed row demoted to the boss_default 10", eph_tab, 'loot3Chance', 10.0, 'P3'),
        ("a stash group chance under SV (loot2 33 -> 10)", stash, 'loot2Chance', 10.0, 'P3'),
        ("the stash's unique_1h row zeroed (quality)", stash, 'loot1Weight3', 0, 'P4'),
        ("a bare literal on a hoard (build28/29/30 P0)", obs_tab, 'numSpawnMaxEquation', '13.44', 'P5'),
        ("the gift box's `numberOfPlayers` term stripped", gift, 'numSpawnMinEquation', '15.12', 'P5'),
    )
    bad = 0
    for label, rec, field, value, arm in plants:
        if rec is None:
            print('  negtest FAIL: fixture record for %r is missing' % label)
            bad += 1
            continue
        before = db.get_field_value(rec, field)
        db.set_field(rec, field, value)
        got = problems_for(db, sv_db)
        hit = [p for p in got if p.startswith(arm + ' ')]
        if hit:
            print('  negtest OK  (caught %s): %-64s -> %s' % (arm, label, hit[0][:90]))
        elif got:
            print('  negtest FAIL (wrong arm, wanted %s): %s -> %s' % (arm, label, got[0][:90]))
            bad += 1
        else:
            print('  negtest FAIL (MISSED): %s' % label)
            bad += 1
        db.set_field(rec, field, before)
        if problems_for(db, sv_db):
            print("  negtest FAIL: restoration after '%s' left the arz RED" % label)
            bad += 1
    print('negtest: %s - %d planted re-nerf(s) on %s'
          % ('PASS (ANTI-INERT CONTROL OK: every plant RED, every restoration GREEN)' if not bad
             else 'FAIL (%d)' % bad, len(plants), Path(arz_path).name))
    return 1 if bad else 0


def main(argv):
    args = [a for i, a in enumerate(argv[1:], 1)
            if not a.startswith('--') and argv[i - 1] not in ('--sv', '--control')]
    arz = args[0] if args else DEFAULT_ARZ
    sv_arz = argv[argv.index('--sv') + 1] if '--sv' in argv else None
    sv_db = load_sv(sv_arz)
    if sv_db is None:
        return 2
    if '--negtest' in argv:
        return negtest(arz, sv_db)
    if '--table' in argv:
        db = ArzDatabase.from_arz(Path(arz))
        rep = {}
        P = problems_for(db, sv_db, rep)
        print_table(rep, 'SV-PARITY TABLE on %s' % Path(arz).name)
        print('  (%d problem(s))' % len(P))
        return 0
    rc = validate(arz, sv_db=sv_db)
    if '--control' in argv:
        crc = control(argv[argv.index('--control') + 1], sv_db)
        return rc or crc
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv))
