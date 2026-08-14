r"""r247_bloodcave_rulings - R-247 parts 7(a)/7(b)/7(c) (Will 2026-08-13).

WILL, VERBATIM (2026-08-13, ANGRY):
  "wtf did you do to all the chests like toxeus the murderer devourer of blood's
   stash? Revert it back to what it was dropping in the original sv you nerfed the
   fuck out of it. also on normal difficulty toxeus the murderer devourer of blood
   wasnt even there guarding his stash, he should spawn there 100% of the time on
   every difficulty. also something else got messed up where toxeus the murderer,
   enslaver of souls is spawning in the entrance to the blood cave next to the
   tattered parchment where toxeus the murderer, devourer of blood should be
   spawning at a 33% rate."

Full measurement + supersession record: docs/WILL_RULINGS.md R-247 parts 7+8 and the
R-240 amendment. Three fixes, all arz-side:

7(a) THE STASH REVERT (supersedes R-240 for EXACTLY three records).
     Measured: the ONLY wave that nerfed the Devourer's stash was R-240's volume trim
     (numSpawn *3.8/*4.1 -> *0.323..0.4305 = ~19 -> ~1.6-2.1 loot iterations solo, an
     ~11-12x cut). R-242 measured NOT involved (chances sit at the pre-R-242 40.0;
     the relic row 21.2 is byte-equal to SV). This module restores the SV 0.98i
     ORIGINAL numSpawn equations VERBATIM (measured from the md5-pinned upstream arz,
     `(3+(1.8*numberOfPlayers))*3.8` min / `*4.1` max) on the three
     `loottable_hidden_bloodcave_0{1,2,3}` tables, which `svc_loot_volume.
     R247_STASH_EXEMPT` simultaneously removes from R-240's trim scope + V1 ceiling -
     so this module is the single volume authority for exactly those records.
     Chances/weights/members are deliberately NOT reverted: the shipped 40.0 group
     chances (vs SV 14/33/31/14), the widened weights and the svc-unique member rows
     carry R-181's distribution contract and the mod's own uniques, and each is >=
     its SV value - so the reverted chest pays >= original-SV richness on every axis.
     The revert class was ENUMERATED by a full both-arz numSpawn sweep: these 3 are
     the ONLY SV-original stash-chest tables the trim reached (the other 15 trimmed
     SV records are uber-ORB tables = the R-242 orb class, untouched; the
     cage/hoard/vault stash chests are mod-authored with no SV original - flagged for
     Will in the lane report, not reverted).

7(b) THE STASH GUARD ON EVERY DIFFICULTY (hardening; the bytes were already 100%).
     Measured: `pools\egg_blooddragon` is difficulty-invariant - spawn 4/4, champions
     3/3 @100 (blood dragons), name1..3 = um_bloodtoxeus_99, proxyPoolEquation
     NEUTRALIZED, proxy difficulty file = difficulty_04 (the file EVERY proven boss
     proxy uses), limits [1..110] N/E/L. Under the mod's RE'd + negative-tested spawn
     model (champions REPLACE mains; guaranteed mains = spawnMax - championMax = 1)
     the Devourer was ALREADY guaranteed on every difficulty; Will's Normal absence
     is not derivable from any decoded DB field. This module hardens the pool to the
     in-game-PROVEN `_BT_POOL` byte-shape class (per-slot limit1..3=1 + weight 150 -
     the exact shape that delivers the Devourer at the entrance ambush), bounding any
     runtime champion-shortfall re-pick to one Devourer per slot. The residual
     channels (engine champion-budget runtime behaviour; a per-difficulty flag on the
     map INSTANCE) are BL-R247-DEBT-6 with the escalation path (dedicated solo guard
     proxy, the q_yard shape) pre-designed; the closing proof is Will's Normal look.

7(c) THE PARCHMENT SPOT (supersedes the A1/build36 warband placement AT THIS SPOT).
     Measured root cause: TWO set-pieces share `drxFirstxistion_connection` - the b79
     33% Devourer ambush (`q_bloodtoxeus_ambush`, wired CORRECTLY: pool = 1 Devourer
     + 2 blood demons, chanceToRun 33) and the A1/build36 Enslaver WARBAND
     (`q_enslaver_warband`, chanceToRun 100, Enslaver + 4 marauders) ~26.6u apart.
     Will meets the 100% warband beside the parchment and reads it as the Devourer
     spawn gone wrong. Fix: `q_enslaver_warband.chanceToRun 100 -> 0` - the placed
     instance goes dormant and the chamber holds exactly the ruled state (Devourer
     @33%, Enslaver gone). KNOWN R-18 COLLISION (the warband was "the dependable
     per-encounter beat"): relocating it to a deeper pocket is a map-lane spec change
     = BL-R247-DEBT-7, a WILL DECISION. His other spawns (rare roam, egypt/orient
     undead-pool rares, TESTHUB yard `q_yard_enslaver`) are asserted untouched.

REGISTRY POSITION: after `loot_volume_trim` + `orb_legendary_chance` (this module
must be the LAST writer of the three tables' numSpawn fields; apply() FAILS LOUD if
the R-240 trim has not already run - which simultaneously proves the ordering) and
before the no-op `visuals`.

Negative test: py tools/patches/r247_bloodcave_rulings.py --negtest  (stub-db plants)
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

MODULE_NAME = ("R-247.7 blood-cave rulings - Devourer stash reverted to original-SV "
               "volume, stash guard hardened to the proven pool shape, the Enslaver "
               "warband dormant at the parchment spot")

# ── 7(a) the three stash tables ─────────────────────────────────────────────
_STASH_TABLES = tuple(
    'records\\drxitem\\container\\loottable_hidden_bloodcave_0%d.dbr' % i
    for i in (1, 2, 3))
_BRACKET = '(3+(1.8*numberOfPlayers))'
# SV 0.98i originals, measured from the md5-pinned upstream arz (identical on all 3
# tiers): min *3.8, max *4.1  ->  ~18.24 / ~19.68 iterations solo.
_SV_MIN_EQ = _BRACKET + '*3.8'
_SV_MAX_EQ = _BRACKET + '*4.1'
# The R-240-trimmed values this module expects to find (per-tier calibration);
# apply() FAILS LOUD on anything else - drift means the trim moved or a new writer
# appeared, and a silent overwrite would hide it.
_TRIMMED = {
    _STASH_TABLES[0]: ('*0.323', '*0.3485'),
    _STASH_TABLES[1]: ('*0.361', '*0.3895'),
    _STASH_TABLES[2]: ('*0.399', '*0.4305'),
}
# Drift detectors (asserted, never written): the shipped composition this revert
# deliberately KEEPS (see module docstring for why).
_KEPT_CHANCES = {'loot1Chance': 40.0, 'loot2Chance': 40.0,
                 'loot5Chance': 40.0, 'loot6Chance': 40.0}
_RELIC_ROW = ('loot4Chance', 21.2)   # byte-equal to the SV original

# ── 7(b) the stash guard pool ───────────────────────────────────────────────
_EGG_POOL = 'records\\drxmap\\proxy\\pools\\egg_blooddragon.dbr'
_EGG_PROXY = 'records\\drxmap\\proxy\\egg_blooddragon_pack.dbr'
_DEVOURER = 'records\\xpack\\creatures\\monster\\skeleton\\um_bloodtoxeus_99.dbr'
_DRAGON = 'records\\drxcreatures\\blooddragons\\blooddragon01.dbr'

# ── 7(c) the parchment-spot records ─────────────────────────────────────────
_WARBAND_PROXY = 'records\\drxmap\\proxy\\q_enslaver_warband.dbr'
_AMBUSH_PROXY = 'records\\drxmap\\proxy\\q_bloodtoxeus_ambush.dbr'
_LONE_PROXY = 'records\\drxmap\\proxy\\q_bloodtoxeus_lone.dbr'
_YARD_ENSLAVER_PROXY = 'records\\drxmap\\proxy\\q_yard_enslaver.dbr'

# Collateral guards: one orb table + the R-240 trim signature it must KEEP (prove the
# carve-out reached only the stash), asserted in verify().
_ORB_SENTINELS = (
    'records\\item\\containers\\defaultloot\\uberorb_default_13-15.dbr',
    'records\\xpack\\item\\containers\\loot tables\\boss_charon_n01b.dbr',
)
_ORB_TRIMMED = ('*0.2283', '*0.2609')


def _gv(db, rec, field, default=None):
    v = db.get_field_value(rec, field)
    if isinstance(v, list):
        v = v[0] if v else None
    return default if v is None else v


def _close(a, b, tol=0.05):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def apply(db, tags):
    print("\n=== patches-registry: %s ===" % MODULE_NAME)
    problems = []

    # ── 7(a): revert the stash volume to the SV originals ────────────────────
    for rec in _STASH_TABLES:
        if not db.has_record(rec):
            raise SystemExit("[r247_bloodcave] stash table MISSING: %s" % rec)
        mn = str(_gv(db, rec, 'numSpawnMinEquation', ''))
        mx = str(_gv(db, rec, 'numSpawnMaxEquation', ''))
        want_mn, want_mx = _TRIMMED[rec]
        if not (mn.endswith(want_mn) and mx.endswith(want_mx)
                and mn.startswith(_BRACKET) and mx.startswith(_BRACKET)):
            raise SystemExit(
                "[r247_bloodcave] 7(a) PRE-STATE DRIFT on %s: numSpawn = %r/%r, "
                "expected the R-240-trimmed %s/%s. Either the trim moved, a new "
                "writer appeared, or this module is mis-ordered (it must run AFTER "
                "loot_volume_trim). Refusing to overwrite an unmeasured state."
                % (rec.rsplit('\\', 1)[-1], mn, mx, want_mn, want_mx))
        for f, want in list(_KEPT_CHANCES.items()) + [_RELIC_ROW]:
            got = _gv(db, rec, f)
            if not _close(got, want):
                raise SystemExit(
                    "[r247_bloodcave] 7(a) composition drift on %s: %s = %r, "
                    "expected ~%s. The revert KEEPS composition; a moved chance "
                    "means another wave touched these tables - measure first."
                    % (rec.rsplit('\\', 1)[-1], f, got, want))
        db.set_field(rec, 'numSpawnMinEquation', _SV_MIN_EQ)
        db.set_field(rec, 'numSpawnMaxEquation', _SV_MAX_EQ)
        db._modified.add(rec)
    print("  [7a] Devourer stash volume reverted to SV 0.98i originals on 3 tables: "
          "%s / %s (~18.2/19.7 iterations solo; was ~1.6-2.1 after R-240)"
          % (_SV_MIN_EQ, _SV_MAX_EQ))

    # ── 7(b): harden the stash-guard pool to the proven _BT_POOL shape ───────
    if not db.has_record(_EGG_POOL):
        raise SystemExit("[r247_bloodcave] 7(b) pool MISSING: %s" % _EGG_POOL)
    for i in (1, 2, 3):
        nm = str(_gv(db, _EGG_POOL, 'name%d' % i, '')).lower()
        if nm != _DEVOURER:
            raise SystemExit(
                "[r247_bloodcave] 7(b) pool shape drift: name%d = %r, expected the "
                "Devourer (the b91 guaranteed-main shape). Measure before writing."
                % (i, nm))
    shape = (int(_gv(db, _EGG_POOL, 'spawnMin', 0)), int(_gv(db, _EGG_POOL, 'spawnMax', 0)),
             int(_gv(db, _EGG_POOL, 'championMin', -1)), int(_gv(db, _EGG_POOL, 'championMax', -1)),
             float(_gv(db, _EGG_POOL, 'championChance', 0.0)))
    if shape != (4, 4, 3, 3, 100.0):
        raise SystemExit(
            "[r247_bloodcave] 7(b) pool counts drift: spawn/champ = %r, expected "
            "(4, 4, 3, 3, 100.0) - the b91 shape. Measure before writing." % (shape,))
    eq = _gv(db, _EGG_POOL, 'proxyPoolEquation', '') or ''
    if str(eq).strip():
        raise SystemExit("[r247_bloodcave] 7(b) proxyPoolEquation re-armed on the egg "
                         "pool (%r) - the champion-cap law requires it empty." % eq)
    for i in (1, 2, 3):
        db.set_field(_EGG_POOL, 'limit%d' % i, 1)
        db.set_field(_EGG_POOL, 'weight%d' % i, 150)
    db._modified.add(_EGG_POOL)
    print("  [7b] egg_blooddragon hardened to the proven _BT_POOL shape class: "
          "limit1..3=1 + weight1..3=150 (guaranteed 1 Devourer main + 3 dragon "
          "champions, difficulty-invariant; residuals -> BL-R247-DEBT-6)")

    # ── 7(c): the warband goes dormant at the parchment spot ─────────────────
    if not db.has_record(_WARBAND_PROXY):
        raise SystemExit("[r247_bloodcave] 7(c) proxy MISSING: %s" % _WARBAND_PROXY)
    ctr = _gv(db, _WARBAND_PROXY, 'chanceToRun')
    if not _close(ctr, 100.0):
        raise SystemExit(
            "[r247_bloodcave] 7(c) warband pre-state drift: chanceToRun = %r, "
            "expected 100.0 (the A1 set-piece). Measure before writing." % ctr)
    db.set_field(_WARBAND_PROXY, 'chanceToRun', 0.0)
    db._modified.add(_WARBAND_PROXY)
    print("  [7c] q_enslaver_warband chanceToRun 100 -> 0: the parchment chamber now "
          "holds exactly the ruled state (Devourer @33%% via q_bloodtoxeus_ambush; "
          "Enslaver gone). Relocation = BL-R247-DEBT-7 (Will decision, map lane).")

    if problems:
        raise SystemExit("[r247_bloodcave] %d problem(s)" % len(problems))


def _check(db):
    """The R-247.7 contract over the FINAL db. Returns a list of problem strings."""
    out = []
    # 7(a) - the SV originals are IN and composition never moved.
    for rec in _STASH_TABLES:
        if not db.has_record(rec):
            out.append("7a %s MISSING" % rec)
            continue
        mn = str(_gv(db, rec, 'numSpawnMinEquation', ''))
        mx = str(_gv(db, rec, 'numSpawnMaxEquation', ''))
        if mn != _SV_MIN_EQ or mx != _SV_MAX_EQ:
            out.append("7a %s numSpawn = %r/%r, must be the SV originals %r/%r "
                       "(a later writer re-trimmed the stash or the revert never ran)"
                       % (rec.rsplit('\\', 1)[-1], mn, mx, _SV_MIN_EQ, _SV_MAX_EQ))
        for f, want in list(_KEPT_CHANCES.items()) + [_RELIC_ROW]:
            if not _close(_gv(db, rec, f), want):
                out.append("7a %s %s = %r, must stay ~%s (composition is KEPT by the "
                           "revert)" % (rec.rsplit('\\', 1)[-1], f, _gv(db, rec, f), want))
    # 7(a) collateral - the carve-out reached ONLY the stash: orb sentinels stay
    # at the R-240/R-241 trimmed multipliers.
    for rec in _ORB_SENTINELS:
        if not db.has_record(rec):
            out.append("7a-collateral orb sentinel MISSING: %s" % rec)
            continue
        mn = str(_gv(db, rec, 'numSpawnMinEquation', ''))
        mx = str(_gv(db, rec, 'numSpawnMaxEquation', ''))
        if not (mn.endswith(_ORB_TRIMMED[0]) and mx.endswith(_ORB_TRIMMED[1])):
            out.append("7a-collateral %s numSpawn = %r/%r - the orb class must KEEP "
                       "its R-240 trim (%s/%s); the stash carve-out leaked"
                       % (rec.rsplit('\\', 1)[-1], mn, mx, *_ORB_TRIMMED))
    # 7(b) - the hardened guaranteed-guard shape.
    if not db.has_record(_EGG_POOL):
        out.append("7b pool MISSING: %s" % _EGG_POOL)
    else:
        for i in (1, 2, 3):
            if str(_gv(db, _EGG_POOL, 'name%d' % i, '')).lower() != _DEVOURER:
                out.append("7b egg pool name%d is not the Devourer" % i)
            if int(_gv(db, _EGG_POOL, 'limit%d' % i, 0) or 0) != 1:
                out.append("7b egg pool limit%d != 1 (per-slot cap, the proven "
                           "_BT_POOL shape)" % i)
            if int(_gv(db, _EGG_POOL, 'weight%d' % i, 0) or 0) != 150:
                out.append("7b egg pool weight%d != 150" % i)
        if (int(_gv(db, _EGG_POOL, 'spawnMin', 0)), int(_gv(db, _EGG_POOL, 'spawnMax', 0))) != (4, 4):
            out.append("7b egg pool spawnMin/Max != 4/4")
        if (int(_gv(db, _EGG_POOL, 'championMin', -1)), int(_gv(db, _EGG_POOL, 'championMax', -1))) != (3, 3):
            out.append("7b egg pool championMin/Max != 3/3")
        if not _close(_gv(db, _EGG_POOL, 'championChance'), 100.0):
            out.append("7b egg pool championChance != 100")
        if str(_gv(db, _EGG_POOL, 'proxyPoolEquation', '') or '').strip():
            out.append("7b egg pool proxyPoolEquation re-armed")
        for i in (1, 2, 3):
            if str(_gv(db, _EGG_POOL, 'nameChampion%d' % i, '')).lower() != _DRAGON:
                out.append("7b egg pool nameChampion%d is not blooddragon01 (the "
                           "ruled 1-Devourer+3-dragons roster)" % i)
    if db.has_record(_EGG_PROXY):
        lim = str(_gv(db, _EGG_PROXY, 'difficultyLimitsFile', '')).lower()
        if 'limit_bloodtoxeus' not in lim:
            out.append("7b egg proxy difficultyLimitsFile = %r, must stay the no-cap "
                       "limit_bloodtoxeus (b91)" % lim)
    else:
        out.append("7b proxy MISSING: %s" % _EGG_PROXY)
    # 7(c) - warband dormant; every OTHER Enslaver/Devourer surface intact.
    if not _close(_gv(db, _WARBAND_PROXY, 'chanceToRun'), 0.0):
        out.append("7c q_enslaver_warband chanceToRun = %r, must be 0.0 (dormant at "
                   "the parchment spot per R-247.7c)"
                   % _gv(db, _WARBAND_PROXY, 'chanceToRun'))
    if not _close(_gv(db, _AMBUSH_PROXY, 'chanceToRun'), 33.0):
        out.append("7c q_bloodtoxeus_ambush chanceToRun = %r, must stay 33.0 (the "
                   "ruled parchment rate)" % _gv(db, _AMBUSH_PROXY, 'chanceToRun'))
    if not _close(_gv(db, _LONE_PROXY, 'chanceToRun'), 100.0):
        out.append("7c q_bloodtoxeus_lone chanceToRun = %r, must stay 100.0"
                   % _gv(db, _LONE_PROXY, 'chanceToRun'))
    if db.has_record(_YARD_ENSLAVER_PROXY):
        if not _close(_gv(db, _YARD_ENSLAVER_PROXY, 'chanceToRun'), 100.0):
            out.append("7c q_yard_enslaver chanceToRun = %r, must stay 100.0 (the "
                       "Enslaver's yard is untouched by 7c)"
                       % _gv(db, _YARD_ENSLAVER_PROXY, 'chanceToRun'))
    else:
        out.append("7c q_yard_enslaver MISSING (the Enslaver's remaining guaranteed "
                   "surface must exist)")
    return out


def verify(db, tags):
    problems = _check(db)
    if problems:
        for p in problems:
            print("  R-247.7 OFFENDER: %s" % p)
        raise SystemExit("[r247_bloodcave_rulings] verify FAILED: %d problem(s)"
                         % len(problems))
    print("  [r247_bloodcave_rulings] verify OK: stash at SV volume (3 tables, "
          "composition kept, orb sentinels still trimmed), stash guard hardened "
          "(1 Devourer + 3 dragons, all difficulties), warband dormant @0%% with "
          "ambush @33%% / lone @100%% / yard @100%% intact")


# ── planted negatives (stub db) ──────────────────────────────────────────────
def _negtest():
    class _Stub(object):
        def __init__(self):
            self.d = {}
            self._modified = set()

        def has_record(self, n):
            return n in self.d

        def get_field_value(self, n, f):
            rec = self.d.get(n)
            return None if rec is None else rec.get(f)

        def set_field(self, n, f, v, dt=None):
            self.d.setdefault(n, {})[f] = v

    def healthy():
        db = _Stub()
        for rec in _STASH_TABLES:
            db.d[rec] = {'numSpawnMinEquation': _SV_MIN_EQ,
                         'numSpawnMaxEquation': _SV_MAX_EQ,
                         'loot1Chance': 40.0, 'loot2Chance': 40.0,
                         'loot5Chance': 40.0, 'loot6Chance': 40.0,
                         'loot4Chance': 21.200000762939453}
        for rec in _ORB_SENTINELS:
            db.d[rec] = {'numSpawnMinEquation': '(3+(1.6*numberOfPlayers))' + _ORB_TRIMMED[0],
                         'numSpawnMaxEquation': '(3+(1.6*numberOfPlayers))' + _ORB_TRIMMED[1]}
        db.d[_EGG_POOL] = {'spawnMin': 4, 'spawnMax': 4, 'championMin': 3,
                           'championMax': 3, 'championChance': 100.0,
                           'proxyPoolEquation': ''}
        for i in (1, 2, 3):
            db.d[_EGG_POOL]['name%d' % i] = _DEVOURER
            db.d[_EGG_POOL]['limit%d' % i] = 1
            db.d[_EGG_POOL]['weight%d' % i] = 150
            db.d[_EGG_POOL]['nameChampion%d' % i] = _DRAGON
        db.d[_EGG_PROXY] = {'difficultyLimitsFile':
                            'records\\proxies orient\\limit_bloodtoxeus.dbr'}
        db.d[_WARBAND_PROXY] = {'chanceToRun': 0.0}
        db.d[_AMBUSH_PROXY] = {'chanceToRun': 33.0}
        db.d[_LONE_PROXY] = {'chanceToRun': 100.0}
        db.d[_YARD_ENSLAVER_PROXY] = {'chanceToRun': 100.0}
        return db

    base = healthy()
    if _check(base):
        print("negtest BROKEN: healthy stub fails the contract:")
        for p in _check(base):
            print("   ", p)
        return 1

    plants = [
        ("stash re-trimmed", lambda d: d.set_field(_STASH_TABLES[0], 'numSpawnMinEquation', _BRACKET + '*0.323')),
        ("stash composition moved", lambda d: d.set_field(_STASH_TABLES[1], 'loot1Chance', 14.0)),
        ("relic row moved", lambda d: d.set_field(_STASH_TABLES[2], 'loot4Chance', 100.0)),
        ("orb carve-out leak", lambda d: d.set_field(_ORB_SENTINELS[0], 'numSpawnMinEquation', '(3+(1.6*numberOfPlayers))*1.2')),
        ("guard slot uncapped", lambda d: d.set_field(_EGG_POOL, 'limit2', 0)),
        ("guard crowd-out", lambda d: d.set_field(_EGG_POOL, 'championMax', 4)),
        ("guard equation re-armed", lambda d: d.set_field(_EGG_POOL, 'proxyPoolEquation', 'records\\proxies orient\\proxypoolequation_02.dbr')),
        ("guard lost the Devourer", lambda d: d.set_field(_EGG_POOL, 'name1', _DRAGON)),
        ("guard limit window regressed", lambda d: d.set_field(_EGG_PROXY, 'difficultyLimitsFile', 'records\\proxies orient\\limit_area002.dbr')),
        ("warband re-armed", lambda d: d.set_field(_WARBAND_PROXY, 'chanceToRun', 100.0)),
        ("ambush rate drift", lambda d: d.set_field(_AMBUSH_PROXY, 'chanceToRun', 50.0)),
        ("yard enslaver lost", lambda d: d.d.pop(_YARD_ENSLAVER_PROXY)),
    ]
    bad = 0
    for label, plant in plants:
        db = healthy()
        plant(db)
        if _check(db):
            print("  negtest OK  (caught): %s" % label)
        else:
            print("  negtest FAIL (missed): %s" % label)
            bad += 1
    print("negtest: %d/%d plants caught" % (len(plants) - bad, len(plants)))
    return 1 if bad else 0


if __name__ == '__main__':
    if '--negtest' in sys.argv:
        sys.exit(_negtest())
    print(__doc__)
