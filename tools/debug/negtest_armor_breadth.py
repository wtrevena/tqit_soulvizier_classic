r"""negtest_armor_breadth.py - PLANTED NEGATIVES for the loot-DISTRIBUTION gate (R-181).

Will 2026-08-10: "also what about the armor? i am not really seeing armor drops like
shields, chest plates, helmets, etc." and "you overcorrected, that run 4 scorpions tail
spears dropped".

Proves the distribution contract in `tools/svc_loot_distribution.py` actually FIRES.
Each case breaks ONE invariant on a fresh in-memory copy and asserts the audit reds; the
positive controls assert the fixed build is green AND that a DELIBERATE theme bias stays
green (a gate that reds every intentional design decision is a gate that gets switched
off - the b63 threshold lesson).

The planted defects are the REAL defect classes, not synthetic ones:
  N1 the shipped armour rows restored verbatim (chance 33/31/30 + unique weights
     100/200/100) - Will's "i am not really seeing armor drops";
  N2 the armour master authored with a per-slot bias (its equal-weight law broken);
  N3 the shipped weapon weighting restored (theme spear bias 100/60/40 + unique_1h back
     to one class's weight in the master) - Will's "you overcorrected";
  N4 one spear wired in directly at a dominating weight - the "4 copies of the SAME
     legendary spear" failure, planted as a single-item share instead of a volume effect
     so D4 is proven independently of D2;
  N5 an armour chance row switched off entirely (weapons drown armour);
  N6 a whole worn slot starved by aiming its unique member at the wrong slot;
  N7 the MIRROR - the weapon row's legendary-share parity reverted on an apex orb table,
     which inverts the surface to 85% armour. Not hypothetical: that is exactly what the
     first R-181 round shipped into three live surfaces before the vet caught it.

INPUT: any arz. The wave is applied IN MEMORY first (the same code path the build takes,
and it is idempotent), so this runs against a pre-fix arz as well as a post-fix build and
always tests the CURRENT contract rather than a stale artefact.

Usage: py tools/debug/negtest_armor_breadth.py <arz>
Exit 0 = every negative fired and both positive controls passed.
"""
import contextlib
import io
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_TOOLS))
sys.path.insert(0, str(_TOOLS.parent))
from arz_patcher import ArzDatabase
import svc_armor_breadth as SAB
import svc_loot_breadth as SLB
import svc_loot_distribution as SLD

L = r'records\item\loottables\svc'
CAGE_L = rf'{L}\polisvault_01.dbr'          # chest_01 Legendary variant a (martial)
CAGE_LC = rf'{L}\polisvault_01_lc.dbr'      # chest_01 Legendary variant c (warden)
HOARD_L = r'records\drxitem\container\svc_charonhoard_loot_03.dbr'
APEX_L = rf'{L}\svc_uberorb_apex_l01c.dbr'   # a red-uber Mystical Orb chest / Leinth
SPEAR_ITEM = r"records\item\equipmentweapon\spear\u_e_scorpion'stail.dbr"
UNIQUE_TORSO_L = r'records\xpack\item\loottables\torso\mastertables\unique_torso_l01.dbr'

# The shipped (pre-R-181) armour-row shape, so N1 is a verbatim revert and not a guess.
SHIPPED_ROWS = {2: 33.0, 5: 31.0, 6: 30.0}
SHIPPED_UNIQUE_W = {2: 100, 5: 200, 6: 100}


def load_fixed(path):
    """Load an arz and apply the R-181 wave in memory (quietly).

    The wave sequence itself lives in `svc_armor_breadth.apply_wave` so the negtests,
    `gate_loot_distribution.py --apply` and the in-build gate cannot drift apart about
    what "after the wave" means.
    """
    return SAB.apply_wave(ArzDatabase.from_arz(Path(path)))


def audit_surface_of(db, lk, table, tier='l'):
    d = SLD.Db(db)
    return SLD.audit_surface(d, SLD.Distributor(d), 'probe', [table], None, tier)[0]


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/debug/negtest_armor_breadth.py <arz>")
        return 2
    arz = argv[1]
    fails = []

    base, base_lk = load_fixed(arz)

    # ── POSITIVE CONTROL 1: the whole fixed build is green.
    problems, reports = SAB.audit_db(base, base_lk)
    ok = (not problems) and len(reports) > 0
    print("%s POSITIVE CONTROL: R-181 build passes (%d surfaces, %d problems)"
          % ('OK ' if ok else 'XX ', len(reports), len(problems)))
    if not ok:
        fails.append('positive control (whole build)')
        for p in problems[:8]:
            print("      %s" % p)

    # ── POSITIVE CONTROL 2: the DELIBERATE warden armour bias is still green as part
    #    of its surface. A gate that cannot tell a designed theme from a defect is
    #    worthless; this is the case that proves it can.
    cage = [s for s in SAB.cage_surfaces(base_lk) if s[0].endswith('[l]')]
    ok2 = True
    for label, tabs, wts, tier in cage:
        d = SLD.Db(base)
        probs = SLD.audit_surface(d, SLD.Distributor(d), label, tabs, wts, tier)[0]
        if probs:
            ok2 = False
            for p in probs[:4]:
                print("      %s" % p)
    print("%s POSITIVE CONTROL: the themed cage surfaces (incl. the warden armour "
          "bias) stay green" % ('OK ' if ok2 else 'XX '))
    if not ok2:
        fails.append('positive control (themed surfaces)')

    def check(label, mutate, probe):
        d, k = load_fixed(arz)
        mutate(d, k)
        hit = bool(probe(d, k))
        if not hit:
            fails.append(label)
        print("%s %-70s -> %s" % ('OK ' if hit else 'XX ', label,
                                  'RED (correct)' if hit else 'GREEN (BLIND)'))

    # N1 - the shipped armour rows, restored verbatim.
    def _revert_rows(d, k):
        real = k.real(CAGE_L)
        for g, chance in SHIPPED_ROWS.items():
            d.set_field(real, 'loot%dChance' % g, chance)
            for i, nm, _w in SLB._slot_members(d, real, g):
                if SAB._UNIQUE_ARMOR_RE.search(SLB._n(nm)):
                    d.set_field(real, 'loot%dWeight%d' % (g, i), SHIPPED_UNIQUE_W[g])
                if 'svc_unique_armor' in SLB._n(nm):
                    d.set_field(real, 'loot%dName%d' % (g, i), '')
                    d.set_field(real, 'loot%dWeight%d' % (g, i), 0)
    check("D6/D7 shipped armour rows restored (33/31/30 + unique weights 100/200/100)",
          _revert_rows,
          lambda d, k: [p for p in audit_surface_of(d, k, CAGE_L)
                        if p.startswith(('D6', 'D7'))])

    # N2 - the armour master's EQUAL-WEIGHT law broken (shields 5x the other slots).
    #      This is the master's own invariant: it is the even-spread instrument, and a
    #      per-slot bias smuggled into it would tilt every surface at once.
    def _unbalance_master(d, k):
        real = k.real(SAB.ARMOR_MASTER['l'])
        for i in range(1, 7):
            nm = SLB._sc(d.get_field_value(real, 'lootName%d' % i))
            if not nm:
                continue
            if 'shield' in SLB._n(nm):
                d.set_field(real, 'lootWeight%d' % i, SAB._SLOT_WEIGHT * 12)
    check("D9 armour master's equal-weight law broken (shield member at 12x)",
          _unbalance_master,
          lambda d, k: [p for p in audit_surface_of(d, k, CAGE_LC)
                        if p.startswith(('D1', 'D2', 'D9'))])

    # N3 - the shipped weapon weighting restored: Will's "you overcorrected". It must
    #      red on D8 (the weapon side measured in its OWN denominator). D1/D2 alone
    #      would NOT catch it once armour parity lands - armour then carries half the
    #      mass, so the same skew reads as ~21% of total gear. That blind spot is the
    #      whole reason D8 exists, and this case is the proof.
    def _revert_weapons(d, k):
        master = k.real(SLB.MASTER['l'])
        d.set_field(master, 'lootWeight1', 1000)          # unique_1h back to 1 class
        real = k.real(CAGE_L)
        for i, nm, _w in SLB._slot_members(d, real, 1):    # the loot1 1H correction
            if SAB._UNIQUE_1H_RE.search(SLB._n(nm)):
                d.set_field(real, 'loot1Weight%d' % i, 200)
        d.set_field(real, 'loot3Weight1', 100)            # broad  ] the shipped martial
        d.set_field(real, 'loot3Weight2', 60)             # spear  ] theme, written LAST
        d.set_field(real, 'loot3Weight3', 40)             # 1H     ] so nothing overwrites it
    check("D8 shipped spear over-weighting restored (theme 100/60/40 + 1-class 1H)",
          _revert_weapons,
          lambda d, k: [p for p in audit_surface_of(d, k, CAGE_L)
                        if p.startswith('D8')])

    # N4 - ONE spear wired in directly at a dominating weight (the literal
    #      "4 copies of the same legendary spear", planted as a single-item share).
    def _plant_dominant_item(d, k):
        real = k.real(CAGE_L)
        item = k.real(SPEAR_ITEM)
        SLB._set_str(d, real, 'loot3Name2', item)
        d.set_field(real, 'loot3Weight2', 4000)
    check("D4/D5 one spear wired in directly at a dominating weight",
          _plant_dominant_item,
          lambda d, k: [p for p in audit_surface_of(d, k, CAGE_L)
                        if p.startswith(('D4', 'D5'))])

    # N5 - an armour row switched off entirely (weapons drown armour).
    #      PLANTED ON THE MARTIAL VARIANT, NOT THE WARDEN ONE, and the reason is the
    #      contract: the warden theme's GUARANTEED slot deliberately pays armour
    #      (armour master 400 + shield 60 + torso 40 of 1000), so killing its CHANCE rows
    #      leaves ~1.0 armour piece per slot per open still arriving - correctly green.
    #      `polisvault_01` (martial) has an all-weapon guaranteed slot, so its armour
    #      comes only from the chance rows and switching them off is a real starvation.
    def _kill_row(d, k):
        real = k.real(CAGE_L)
        for g in SAB.armor_groups(d, real):
            d.set_field(real, 'loot%dChance' % g, 0.0)
    check("D6/D7 every armour CHANCE row switched off on the martial cage variant",
          _kill_row,
          lambda d, k: [p for p in audit_surface_of(d, k, CAGE_L)
                        if p.startswith(('D6', 'D7'))])

    # N7 - the MIRROR. Revert the weapon row's legendary-share parity on an apex orb
    #      table (master back to R-180's flat BREADTH_WEIGHT) and the surface inverts to
    #      ~0.17:1 weapon:armour - 85% armour. This is the over-correction the first
    #      R-181 round actually shipped into three live surfaces, so it is planted rather
    #      than argued: it proves MIN_WEAPON_ARMOUR_RATIO is load-bearing and that
    #      "fix the armour" cannot quietly become "bury the weapons".
    def _revert_weapon_parity(d, k):
        real = k.real(APEX_L)
        for i, nm, _w in SLB._slot_members(d, real, 1):
            if SAB._WEAPON_MASTER_RE.search(SLB._n(nm)):
                d.set_field(real, 'loot1Weight%d' % i, SLB.BREADTH_WEIGHT)
    check("D6b weapon-row share parity reverted on the apex orb table (armour buries "
          "weapons)",
          _revert_weapon_parity,
          lambda d, k: [p for p in audit_surface_of(d, k, APEX_L)
                        if p.startswith('D6b')])

    # N6 - a whole worn slot starved by aiming its unique member at another slot.
    def _starve_slot(d, k):
        real = k.real(HOARD_L)
        for g in SAB.armor_groups(d, real):
            for i, nm, _w in SLB._slot_members(d, real, g):
                n = SLB._n(nm)
                if 'unique_head' in n or 'svc_unique_armor' in n:
                    d.set_field(real, 'loot%dName%d' % (g, i), UNIQUE_TORSO_L)
    check("D3/D7 the helm slot starved (its unique member re-aimed at torso)",
          _starve_slot,
          lambda d, k: [p for p in audit_surface_of(d, k, HOARD_L)
                        if p.startswith(('D3', 'D7'))])

    print()
    if fails:
        print("NEGTEST FAILED: %d" % len(fails))
        for f in fails:
            print("   - %s" % f)
        return 1
    print("NEGTEST PASS: every planted skew reds the distribution gate, and both the "
          "fixed build and its deliberate themes stay green.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
