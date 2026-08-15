r"""negtest_uber_hoards.py - the NEGATIVE battery for R-250 (Will 2026-08-14).

A gate nobody has watched FAIL is a gate nobody should trust, and R-250 exists because
four fail-loud gates were GREEN for three waves while twenty-one uber chests paid
base-game loot. So every check in `tools/svc_uber_hoards.problems()` gets a planted
defect that must make it - and preferably only it - go RED, plus an ANTI-INERT positive
control proving the healthy fixture is green in the first place.

The fixture is a STUB db (no arz needed), so this runs in a second and can be part of
any lane's static battery:

    py tools/debug/negtest_uber_hoards.py
    py tools/patches/uber_hoard_generosity.py --negtest     # same battery, module door

Exit 0 = every plant was caught and the healthy fixture is clean.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1]
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import svc_loot_breadth as SLB          # noqa: E402
import svc_uber_hoards as SUH           # noqa: E402

_C = SUH.CONTAINER_DIR
_FAMILIES = ('tantalus', 'obsidian', 'ephialtes')
_BASE_TABLE = r'records\item\containers\defaultloot\boss_default_63-65.dbr'

# The guaranteed row, per tier - the pair H8 reads. The unique half is the mod's own
# breadth master (what `retarget_guaranteed_weapon` leaves in a shipped arz), the relic
# half the base game's act-4 relic table; both carry their tier in the name, which is
# exactly what makes the leak machine-checkable.
_GUAR_UNIQUE = {t: r'records\item\loottables\svc\svc_unique_weapons_%s01.dbr'
                   % SUH.TIER_LETTER[t] for t in SUH.TIERS}
_GUAR_RELIC = {t: r'records\xpack\item\loottables\relics\%s_act4_relics.dbr' % t
               for t in SUH.TIERS}


class _TF(object):
    """The minimum of arz_patcher.TypedField the contract actually reads."""

    def __init__(self, values):
        self.values = list(values)


class _Stub(object):
    def __init__(self):
        self.d = {}
        self._modified = set()

    # -- the ArzDatabase surface svc_loot_breadth.Lookup + svc_uber_hoards use --
    def record_names(self):
        return list(self.d)

    def has_record(self, n):
        return n in self.d

    def get_fields(self, n):
        rec = self.d.get(n)
        if rec is None:
            return None
        return {k: _TF([v]) for k, v in rec.items()}

    def get_field_value(self, n, f):
        rec = self.d.get(n)
        return None if rec is None else rec.get(f)

    def set_field(self, n, f, v, dt=None):
        self.d.setdefault(n, {})[f] = v


def _healthy():
    """A post-R-250 database in miniature: 3 families, wired, at authored volume."""
    db = _Stub()
    for fam in _FAMILIES:
        for tier in SUH.TIERS:
            chest = r'%s\svc_%shoard_%s.dbr' % (_C, fam, tier)
            table = r'%s\svc_%shoard_loot_%s.dbr' % (_C, fam, tier)
            db.d[chest] = {'templateName': r'database\Templates\FixedItemContainer.tpl',
                           'tables': table,
                           'description': 'tagSVC%sHoard' % fam.title()}
            db.d[table] = {'templateName': r'database\Templates\FixedItemLoot.tpl',
                           'numSpawnMinEquation': SUH.HOARD_MIN_EQ,
                           'numSpawnMaxEquation': SUH.HOARD_MAX_EQ,
                           'loot3Chance': 100.0,
                           'loot3Name1': _GUAR_UNIQUE[tier],
                           'loot3Name2': _GUAR_RELIC[tier]}
    for i, path in enumerate(SUH.GIFT_TABLES):
        tier = SUH.TIERS[i]
        db.d[path] = {'templateName': r'database\Templates\FixedItemLoot.tpl',
                      'numSpawnMinEquation': SUH.GIFT_MIN_EQ,
                      'numSpawnMaxEquation': SUH.GIFT_MAX_EQ,
                      'loot1Name3': _GUAR_UNIQUE[tier],
                      'loot4Name2': _GUAR_RELIC[tier]}
        db.d[SUH.GIFT_CHESTS[i]] = {
            'templateName': r'database\Templates\FixedItemContainer.tpl',
            'tables': path, 'description': 'tagSecretPresentBOX'}
    for path in SUH.STASH_TABLES:
        db.d[path] = {'templateName': r'database\Templates\FixedItemLoot.tpl',
                      'numSpawnMinEquation': SUH.HOARD_BRACKET + '*3.8',
                      'numSpawnMaxEquation': SUH.HOARD_BRACKET + '*4.1',
                      'loot3Chance': 100.0}
    db.d[_BASE_TABLE] = {'templateName': r'database\Templates\FixedItemLoot.tpl',
                         'numSpawnMinEquation': '(3+(1.6*numberOfPlayers))*1.5',
                         'numSpawnMaxEquation': '(3+(1.6*numberOfPlayers))*1.7',
                         'loot3Chance': 10.0}
    return db


# ── the plants ───────────────────────────────────────────────────────────────
def _p_h1_repoint(db):
    """THE b42 DEFECT ITSELF: a hoard chest repointed to base-game Cyclops loot."""
    db.d[r'%s\svc_tantalushoard_03.dbr' % _C]['tables'] = _BASE_TABLE


def _p_h2_orphan(db):
    """A hoard table nothing names - the state 18 records shipped in."""
    db.d[r'%s\svc_ghosthoard_loot_02.dbr' % _C] = {
        'templateName': r'database\Templates\FixedItemLoot.tpl',
        'numSpawnMinEquation': SUH.HOARD_MIN_EQ,
        'numSpawnMaxEquation': SUH.HOARD_MAX_EQ, 'loot3Chance': 100.0}


def _p_h3_trimmed(db):
    """R-240's trim reaching the family again (the carve-out silently lost)."""
    t = db.d[r'%s\svc_obsidianhoard_loot_01.dbr' % _C]
    t['numSpawnMinEquation'] = SUH.HOARD_BRACKET + '*0.2188'
    t['numSpawnMaxEquation'] = SUH.HOARD_BRACKET + '*0.25'


def _p_h4_literal(db):
    """The build28/29/30 P0: a bare literal, evaluator returns 0, chest pays nothing."""
    db.d[r'%s\svc_ephialteshoard_loot_02.dbr' % _C]['numSpawnMinEquation'] = '48'


def _p_h5_no_guarantee(db):
    """The guaranteed unique+relic row demoted to the base game's 10%."""
    db.d[r'%s\svc_ephialteshoard_loot_03.dbr' % _C]['loot3Chance'] = 10.0


def _p_h6_giftbox_unapplied(db):
    """BL-W0814-7 never landed: the box still at its SV original volume."""
    db.d[SUH.GIFT_TABLES[1]]['numSpawnMinEquation'] = SUH.GIFT_SV_MIN_EQ
    db.d[SUH.GIFT_TABLES[1]]['numSpawnMaxEquation'] = SUH.GIFT_SV_MAX_EQ


def _p_h7_shared(db):
    """Two uber chests on one loot record - Will's record-separation report."""
    db.d[r'%s\svc_obsidianhoard_03.dbr' % _C]['tables'] = \
        r'%s\svc_tantalushoard_loot_03.dbr' % _C


def _p_h7_stash(db):
    """An uber chest sharing the Devourer's stash: the exact thing Will asked about."""
    db.d[r'%s\svc_obsidianhoard_02.dbr' % _C]['tables'] = SUH.STASH_TABLES[1]


def _p_h8_relic_tier(db):
    """THE ROUND-2 DEFECT ITSELF: the Obsidian roulette's Normal-tier relic written into
    the Epic table, so a Legendary-grade chest guarantees an Essence relic. Measured live
    on the shipped b888f022, and invisible to the wire-walking relic gate until R-250
    made the branch reachable."""
    db.d[r'%s\svc_obsidianhoard_loot_02.dbr' % _C]['loot3Name2'] = _GUAR_RELIC['01']


def _p_h8_unique_tier(db):
    """The other half of the same leak: the guaranteed UNIQUE left at Normal tier on the
    Legendary table. Planted separately because on the shipped arz this half was masked
    by R-180 retargeting the slot downstream - a fix that depends on a later module is
    not a fix, and this plant is what keeps that true."""
    db.d[r'%s\svc_tantalushoard_loot_03.dbr' % _C]['loot3Name1'] = _GUAR_UNIQUE['01']


def _p_h8_gift_tier(db):
    """The Secret Present box is per-difficulty too, and R-250 is the wave that changes
    it - so its tiers get the same watch."""
    db.d[SUH.GIFT_TABLES[2]]['loot4Name2'] = _GUAR_RELIC['02']


def _p_h3_crown_lost(db):
    """The crown inverted: the Devourer's stash re-tuned DOWN until the hoards and the
    gift box out-pay it. R-247.7(a) says the blood-cave mega chest stays the richest
    surface in the mod, and comparing bare multipliers could never see this (the gift box
    rides a different bracket) - which is why H3 now measures solo iterations."""
    for path in SUH.STASH_TABLES:
        db.d[path]['numSpawnMinEquation'] = SUH.HOARD_BRACKET + '*1'
        db.d[path]['numSpawnMaxEquation'] = SUH.HOARD_BRACKET + '*1.1'


PLANTS = [
    ('N1 H1 a hoard chest repointed to base-game Cyclops loot (the b42 defect)',
     _p_h1_repoint, 'H1'),
    ('N2 H2 a hoard loot table nothing references (the 18 shipped orphans)',
     _p_h2_orphan, 'H2'),
    ('N3 H3 R-240 trim reaches the family again (carve-out lost)',
     _p_h3_trimmed, 'H3'),
    ('N4 H4 numSpawn given a bare literal (build28/29/30 P0)', _p_h4_literal, 'H4'),
    ('N5 H5 the guaranteed 100% unique+relic row demoted', _p_h5_no_guarantee, 'H5'),
    ('N6 H6 the Secret Present box left at its SV volume (BL-W0814-7 not applied)',
     _p_h6_giftbox_unapplied, 'H6'),
    ('N7 H7 two uber chests share one loot record', _p_h7_shared, 'H7'),
    ('N8 H7 an uber chest shares the Devourer stash table', _p_h7_stash, 'H7'),
    ('N9 H8 a Normal-tier relic on the Epic hoard table (the R-250 round-2 defect)',
     _p_h8_relic_tier, 'H8'),
    ('N10 H8 a Normal-tier guaranteed unique on the Legendary hoard table',
     _p_h8_unique_tier, 'H8'),
    ('N11 H8 a wrong-tier relic on the Secret Present box', _p_h8_gift_tier, 'H8'),
    ('N12 H3 the Devourer stash re-tuned below the hoards + gift box (crown inverted)',
     _p_h3_crown_lost, 'H3'),
]


def main(argv):
    print("\n=== R-250 negative battery (uber/boss chest generosity) ===")
    # ANTI-INERT positive control. If the healthy fixture is not green, every RED below
    # proves nothing at all - which is the failure mode BL-R240-DEBT-8 was written about.
    base = _healthy()
    clean = SUH.problems(base, SLB.Lookup(base))
    if clean:
        for p in clean:
            print("  CONTROL FINDING: %s" % p)
        print("\nBATTERY FAIL: the HEALTHY fixture is not clean, so no planted negative "
              "below can prove anything.")
        return 1
    print("  CONTROL: healthy fixture is GREEN (0 findings) - the battery is not inert.")

    failures = 0
    for label, plant, want in PLANTS:
        db = _healthy()
        plant(db)
        found = SUH.problems(db, SLB.Lookup(db))
        hit = [f for f in found if f.startswith(want)]
        if not hit:
            print("  MISS  %-72s (expected a %s finding, got %d finding(s): %s)"
                  % (label, want, len(found), found[:2]))
            failures += 1
        else:
            print("  CAUGHT %-71s -> %s" % (label, hit[0][:110]))
    print()
    if failures:
        print("BATTERY FAIL: %d of %d plant(s) went UNDETECTED." % (failures, len(PLANTS)))
        return 1
    print("BATTERY PASS: %d of %d plants caught, healthy fixture green."
          % (len(PLANTS), len(PLANTS)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
