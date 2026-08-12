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
  N10 the b79 armour rows restored on an R-220 orb table, one per donor family - the
     BL-R181-DEBT-7 defect itself, which BOTH loot gates passed for a whole build
     because no surface audited those tables;
  N14 the POOL-EVENNESS BOUND defeated - the narrow level-banded armour members raised
     FLAT to ARMOR_UNIQUE_WEIGHT on the worst orb surface. That is what round 1 of
     BL-R181-DEBT-7 shipped, and it multiplied one greaves record ~31x into a 4.5%
     single-item share. See the note beside it for the half that is deliberately NOT
     pinned, and why;
  N11 the SYNTHETIC ORPHAN, planted twice: a module writes a gear loot table that no
     distribution surface covers, once through the shared builder (the LEDGER witness)
     and once as a raw field write (the REGISTRY TOUCH LOG witness). No threshold can
     see this defect - it is a rule about WRITES - and it is the shape of the fifteen
     tables R-220 wrote outside `\svc\`.

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
import svc_loot_ownership as OWN

L = r'records\item\loottables\svc'
CAGE_L = rf'{L}\polisvault_01.dbr'          # chest_01 Legendary variant a (martial)
CAGE_LC = rf'{L}\polisvault_01_lc.dbr'      # chest_01 Legendary variant c (warden)
HOARD_L = r'records\drxitem\container\svc_charonhoard_loot_03.dbr'
APEX_L = rf'{L}\svc_uberorb_apex_l01c.dbr'   # a red-uber Mystical Orb chest / Leinth
# The D7 REFERENCE surface: ARMOR_SLOT_FLOOR (0.52/open) was calibrated on this exact
# table's 0.6229 reading, and its S_eff of 10.58 is ARMOR_SLOT_FLOOR_REF_SPAWN. N12/N13
# are the two negatives that keep D7 demonstrably switched ON here.
APEX_E = rf'{L}\svc_uberorb_apex_e01c.dbr'
SPEAR_ITEM = r"records\item\equipmentweapon\spear\u_e_scorpion'stail.dbr"
UNIQUE_TORSO_L = r'records\xpack\item\loottables\torso\mastertables\unique_torso_l01.dbr'
# BL-R181-DEBT-7's own surfaces: an R-220 orb table from each of the two donor families.
ORB_CHARON_L = r'records\xpack\item\containers\loot tables\boss_charon_l01b.dbr'
ORB_BANDED_E = r'records\item\containers\defaultloot\uberorb_default_43-45.dbr'
# The single worst pool-evenness surface in the mod: its `legsall_e03` member (N=6) puts
# 46.4% of its own mass on ONE item, so it is where the evenness bound earns its keep.
ORB_BANDED_WORST = r'records\item\containers\defaultloot\uberorb_default_49-51.dbr'
# The SYNTHETIC ORPHAN: a loot table written by a module and covered by no surface -
# the exact shape of the fifteen R-220 tables before this lane. Deliberately OUTSIDE
# `\svc\`, because inside it the mod-ownership sweep would (correctly) cover it and
# there would be no orphan to catch.
ORPHAN = r'records\item\containers\defaultloot\negtest_orphan_loot_l01.dbr'

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
    #
    # ⚠ R-240 COUPLING (`BL-R240-DEBT-8`). `load_fixed` applies the R-181 wave ONLY, so
    # on a pre-R-240 arz the D7 anchor surface still measures its untrimmed volume and
    # D7X2 legitimately reds - the anchor working, not a defect in this build. That ONE
    # problem is expected here and is therefore named and set aside rather than either
    # (a) failing the control, which makes the whole battery red for a documented
    # coupling, or (b) loosening the control to "few problems", which would let a real
    # regression hide behind it. Everything else must still be empty, and the set-aside
    # problem is PRINTED so it can never become invisible.
    problems, reports = SAB.audit_db(base, base_lk)
    expected = [p for p in problems if p.startswith('D7X2')]
    unexpected = [p for p in problems if not p.startswith('D7X2')]
    ok = (not unexpected) and len(reports) > 0
    print("%s POSITIVE CONTROL: R-181 build passes (%d surfaces, %d problem(s): %d "
          "unexpected + %d expected-D7X2-on-a-pre-R-240-arz)"
          % ('OK ' if ok else 'XX ', len(reports), len(problems),
             len(unexpected), len(expected)))
    for p in expected:
        print("      (expected, BL-R240-DEBT-8) %s" % p[:150])
    if not ok:
        fails.append('positive control (whole build)')
        for p in unexpected[:8]:
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

    # ── N10/N11: BL-R181-DEBT-7. The armour rows R-220 left to nobody, and the
    #    OWNERSHIP rule that makes "written by a module, audited by no surface"
    #    structurally impossible rather than merely fixed once.

    # N10 - the R-220 armour rows reverted to exactly what b79 shipped, on one table
    #      from EACH donor family. Before this lane both were invisible: the sweep did
    #      not write them and `all_surfaces` did not audit them, so both loot gates were
    #      green while the thinnest worn slot paid 0.007-0.029 pieces per open. This is
    #      the defect itself, replanted, so the coverage cannot quietly regress.
    def _revert_orb_armour(table):
        def _m(d, k):
            real = k.real(table)
            for g in SAB.armor_groups(d, real):
                d.set_field(real, 'loot%dChance' % g, 26.0)
                for i, nm, _w in SLB._slot_members(d, real, g):
                    n = SLB._n(nm)
                    if 'svc_unique_armor' in n:
                        d.set_field(real, 'loot%dName%d' % (g, i), '')
                        d.set_field(real, 'loot%dWeight%d' % (g, i), 0)
                    elif SAB._UNIQUE_ARMOR_RE.search(n):
                        d.set_field(real, 'loot%dWeight%d' % (g, i), 27)
        return _m

    for label, table, tier in (('charon', ORB_CHARON_L, 'l'),
                               ('level-banded', ORB_BANDED_E, 'e')):
        check("D6/D7b the b79 armour rows restored on the %s orb table (the "
              "BL-R181-DEBT-7 defect itself)" % label,
              _revert_orb_armour(table),
              lambda d, k, t=table, tr=tier: [p for p in audit_surface_of(d, k, t, tr)
                                              if p.startswith(('D6', 'D7'))])

    # N14 - THE EVENNESS BOUND (ARMOR_UNIQUE_REF_TOP_SHARE). Defeat it: every
    #      unique-armour member on the worst level-banded orb table raised FLAT to
    #      ARMOR_UNIQUE_WEIGHT, which is exactly what round 1 of this lane shipped and
    #      exactly what pushed that surface to a 4.5% single-item share.
    #
    # ⚠️ WHAT IS NOT PINNED HERE, stated rather than implied. The bound's OTHER half -
    #    handing the withheld weight to the aggregate master - was planted too and came
    #    back GREEN, so it is NOT shipped as a negative. Measured: forcing the master
    #    back to ARMOR_MASTER_WEIGHT on all 15 orb tables moves the worst worn-slot yield
    #    0.04517 -> 0.04249 per spawn iteration against D7b's 0.0375 floor, i.e. it
    #    spends about 6% of the headroom and reds nothing. The surplus is therefore a
    #    BALANCE CHOICE living inside D7b's margin, not a gate-enforced invariant, and it
    #    is registered as BL-R181-DEBT-11 rather than dressed up as a guarded one.
    def _flatten_bound(d, k):
        real = k.real(ORB_BANDED_WORST)
        for g in SAB.armor_groups(d, real):
            for i, nm, _w in SLB._slot_members(d, real, g):
                n = SLB._n(nm)
                if 'svc_unique_armor' in n:
                    d.set_field(real, 'loot%dWeight%d' % (g, i), SAB.ARMOR_MASTER_WEIGHT)
                elif SAB._UNIQUE_ARMOR_RE.search(n):
                    d.set_field(real, 'loot%dWeight%d' % (g, i), SAB.ARMOR_UNIQUE_WEIGHT)
    check("D5 the pool-evenness bound defeated - narrow banded members flat at %d "
          "(round 1 of this lane)" % SAB.ARMOR_UNIQUE_WEIGHT,
          _flatten_bound,
          lambda d, k: [p for p in audit_surface_of(d, k, ORB_BANDED_WORST, 'e')
                        if p.startswith('D5')])

    # N11 - THE SYNTHETIC ORPHAN. A module writes a gear loot table that no surface
    #      audits. No threshold can catch this - only a rule about WRITES can - and it
    #      is the exact shape of the defect: R-220 wrote fifteen tables outside `\svc\`
    #      and R-181's folder-shaped ownership rule never looked at them.
    #      Planted twice, once per witness, because they catch different bugs: the
    #      LEDGER sees a module that goes through the shared builders, the REGISTRY
    #      TOUCH LOG sees one that writes loot fields raw.
    def _own_case(label, plant, expect):
        OWN.reset()                       # the ledger is process-global by design
        d, k = load_fixed(arz)
        plant(d, k)
        probs = SAB.ownership_problems(d, k)
        hit = [p for p in probs if p.startswith(expect)]
        if not hit:
            fails.append(label)
        print("%s %-70s -> %s" % ('OK ' if hit else 'XX ', label,
                                  'RED (correct)' if hit else 'GREEN (BLIND)'))

    def _plant_ledger_orphan(d, k):
        d.clone_record(k.real(ORB_CHARON_L), ORPHAN)
        k.refresh()
        SAB.widen_armor_rows(d, ORPHAN, 'l', k)     # the builder registers the write

    _own_case("OWN1 a module writes a gear loot table no surface audits (via the "
              "shared builder)", _plant_ledger_orphan, 'OWN1')

    def _plant_raw_orphan(d, k):
        d.clone_record(k.real(ORB_CHARON_L), ORPHAN)
        k.refresh()
        d.set_field(ORPHAN, 'loot2Chance', 40.0)    # raw write, no builder involved
        d._registry_touch_log = [('negtest_raw_writer', ORPHAN)]

    _own_case("OWN2 a module writes loot rows RAW on a table no surface audits",
              _plant_raw_orphan, 'OWN2')

    # POSITIVE CONTROL 3: the fixed build's own ownership is clean, and the touch-log
    # witness is exercised rather than merely absent - a gate that only ever runs in its
    # downgraded form is a gate nobody has tested.
    OWN.reset()
    dpc, kpc = load_fixed(arz)
    dpc._registry_touch_log = [('orb_armor_rows', t)
                               for _key, (t, _tier) in SAB.orb_scope(dpc, kpc).items()]
    own_ok = not SAB.ownership_problems(dpc, kpc)
    print("%s POSITIVE CONTROL: every loot table this wave writes is inside a "
          "distribution surface (both witnesses live)" % ('OK ' if own_ok else 'XX '))
    if not own_ok:
        fails.append('positive control (ownership)')
        for p in SAB.ownership_problems(dpc, kpc)[:6]:
            print("      %s" % p)
    OWN.reset()

    # ── N12/N13: D7X, THE REFERENCE SURFACE. The round-2 vet found D7 switched OFF on
    #    all three `svc_uberorb_apex_*` surfaces - including the very one ARMOR_SLOT_FLOOR
    #    was calibrated on - by a 1.78e-15 shortfall in a weighted S_eff against a bare
    #    `spawn >= ARMOR_SLOT_FLOOR_REF_SPAWN`. Nothing failed; the PASS line went on
    #    claiming the floor held. These two pin it from both sides: N12 plants a real
    #    armour regression in the band that was unguarded, N13 attacks the structural
    #    check itself.

    # N12 - an armour cut on the REFERENCE surface, deep enough to breach the LIVE
    #      absolute floor. Only D7 being genuinely ASSERTED on this surface catches it.
    #
    # ⚠ REWRITTEN BY R-240 (round 4), and the reason is the whole point of the check.
    # This case used to hardcode `svc_uberorb_apex_e01c` as "the REFERENCE surface" and
    # a fixed 25% cut, because that was the surface and the margin when the floor was
    # 0.52/open. R-240 re-anchored `ARMOR_SLOT_FLOOR` onto `gaoler cage chest_01 [l]`
    # and, deriving it as per-iteration-strength x the trimmed anchor volume, moved it
    # to 0.0644/open - about 8x lower. The old plant then MEASURED GREEN: a 25% cut on
    # a surface calibrated at ~0.62/open lands at ~0.47, still an order of magnitude
    # above the new floor. The battery was still asserting the SUPERSEDED contract and
    # reported a blind spot it had itself been made blind to.
    #
    # So both hardcodings are gone. The target is read from
    # `SLD.ARMOR_SLOT_FLOOR_REF_SURFACE` and the cut is SIZED FROM THE LIVE FLOOR, which
    # makes the check self-calibrating: whoever moves the anchor or the floor next gets
    # a plant that still lands just under it, and this case cannot silently rot again.
    def _ref_report(d, k):
        _probs, reps = SAB.audit_db(d, k)
        return next((r for r in reps
                     if r.get('label') == SLD.ARMOR_SLOT_FLOOR_REF_SURFACE), None)

    def _cut_reference_armour(d, k):
        rep = _ref_report(d, k)
        if rep is None:
            return                     # D7X already reds this; probe returns [] -> XX
        # ARMOUR SLOTS ONLY. `slot_mass` carries weapon slots too, and D7's floor is an
        # ARMOUR floor - sizing the cut off a weapon slot compares two different things
        # and produces a nonsense factor (the first draft of this rewrite did exactly
        # that and asked for a -25% cut).
        mass = rep.get('slot_mass') or {}
        worst = min([mass.get(s, 0.0) for s in SLD.ARMOR_SLOTS] or [0.0])
        # Put the thinnest worn slot 10% BELOW the live floor. Guard the degenerate
        # case so a surface already under the floor still gets a real cut.
        f = (SLD.ARMOR_SLOT_FLOOR / worst) * 0.9 if worst > SLD.ARMOR_SLOT_FLOOR else 0.5
        for t in rep.get('tables', []):
            real = k.real(t)
            if not real:
                continue
            for g in SAB.armor_groups(d, real):
                d.set_field(real, 'loot%dChance' % g, SAB.ARMOR_ROW_CHANCE * f)

    def _probe_reference_d7(d, k):
        probs, _reps = SAB.audit_db(d, k)
        return [p for p in probs
                if p.startswith('D7 ') and SLD.ARMOR_SLOT_FLOOR_REF_SURFACE in p]

    check("D7 armour cut below the LIVE floor on the LIVE reference surface (%s, "
          "floor %.4f/open)" % (SLD.ARMOR_SLOT_FLOOR_REF_SURFACE, SLD.ARMOR_SLOT_FLOOR),
          _cut_reference_armour, _probe_reference_d7)

    # N12b - WHAT THE 8x FLOOR DROP ACTUALLY COST, as a number rather than a claim.
    #      R-240's re-derivation is correct (holding 0.52/open against a container that
    #      now spawns ~1.1 iterations would be D7 turning into a numSpawn demand), but
    #      "the floor came down 8x" is the kind of sentence that gets read as harmless.
    #      This measures the real consequence on the surface the OLD anchor protected:
    #      how deep an armour cut the apex orb can now absorb before ANY check reds.
    #      Reported, not asserted - the number belongs in `BL-R240-DEBT-9`, and a test
    #      that asserts a hole stays open is not a test.
    dslack, kslack = load_fixed(arz)
    _p, reps_slack = SAB.audit_db(dslack, kslack)
    apex = next((r for r in reps_slack
                 if 'apex_e01c' in ' '.join(str(t) for t in r.get('tables', []))), None)
    if apex is None:
        print("     D7-SLACK on the old anchor: apex_e01c is NOT in the audit set")
    else:
        mass = apex.get('slot_mass') or {}
        S = apex.get('S_eff', 0.0) or 1.0
        worst = min([mass.get(s, 0.0) for s in SLD.ARMOR_SLOTS] or [0.0])
        d7_cut = 100.0 * (1.0 - SLD.ARMOR_SLOT_FLOOR / worst) if worst else 0.0
        d7b_cut = (100.0 * (1.0 - SLD.ARMOR_SLOT_FLOOR_PER_SPAWN / (worst / S))
                   if worst else 0.0)
        # The pre-R-240 comparison is DERIVED here, not quoted from memory: the old
        # floor was the literal 0.52/open, so the cut it demanded on this same measured
        # surface is 1 - 0.52/worst. Printing both from the same reading is what makes
        # "the floor came down 8x" a number instead of a sentence.
        old_cut = 100.0 * (1.0 - 0.52 / worst) if worst else 0.0
        print("     D7-SLACK on the OLD anchor (svc_uberorb_apex_e01c, d7_asserted=%s): "
              "thinnest ARMOUR slot %.4f/open over S=%.2f. An armour cut must now exceed "
              "%.1f%% to red D7 (floor %.4f) and %.1f%% to red D7b (floor %.4f). Against "
              "the pre-R-240 floor of 0.52/open the same surface demanded %.1f%%. THIS IS "
              "THE PRICE OF THE RE-ANCHOR - see BL-R240-DEBT-9."
              % (apex.get('d7_asserted'), worst, S, d7_cut, SLD.ARMOR_SLOT_FLOOR,
                 d7b_cut, SLD.ARMOR_SLOT_FLOOR_PER_SPAWN, old_cut))

    # N13 - D7X itself. Move the reference volume just above the reference surface's own
    #      S_eff and the surface falls out of D7 exactly as it did in round 1. D7X must
    #      RED. If this comes back green the tolerance is the only thing standing between
    #      this gate and a silent re-exclusion, and a single constant edit would undo it.
    saved_ref = SLD.ARMOR_SLOT_FLOOR_REF_SPAWN
    try:
        SLD.ARMOR_SLOT_FLOOR_REF_SPAWN = saved_ref * 1.001
        d7x = [p for p in SAB.audit_db(base, base_lk)[0] if p.startswith('D7X')]
    finally:
        SLD.ARMOR_SLOT_FLOOR_REF_SPAWN = saved_ref
    ok = bool(d7x)
    print("%s %-70s -> %s"
          % ('OK ' if ok else 'XX ',
             "D7X the reference surface falls out of D7 (the round-1 defect)",
             'RED (correct)' if ok else 'GREEN (BLIND - D7 can be switched off silently)'))
    if not ok:
        fails.append("D7X reference-surface exclusion")

    # ── N7-N9: the D3 SIZE EXEMPTION (b81 / R-186). An exemption is the one construct
    #    that can silently switch a gate off, so it gets more negatives than the rules it
    #    carves out of. These do not plant loot edits; they attack the exemption itself.
    def _d3x(mutate):
        saved_min, saved_set = SLD.D3_MIN_CLASS_UNIVERSE, SLD.D3_ERA_EXEMPT
        try:
            mutate()
            return SLD.era_exemption_problems(SLD.Db(base))
        finally:
            SLD.D3_MIN_CLASS_UNIVERSE, SLD.D3_ERA_EXEMPT = saved_min, saved_set

    def _grow():
        # thrown holds 5 Legendary records; drop the threshold under that and the
        # exemption must declare itself void rather than keep protecting the class.
        SLD.D3_MIN_CLASS_UNIVERSE = 4

    def _typo():
        SLD.D3_ERA_EXEMPT = ('thrwon',)

    for label, mut in (("D3X the exempt class grew past D3_MIN_CLASS_UNIVERSE", _grow),
                       ("D3X the exemption names a slot that does not exist", _typo)):
        got = _d3x(mut)
        ok = bool(got)
        print("%s  %-72s -> %s" % ('OK ' if ok else 'FAIL', label,
                                   'RED (correct)' if ok else 'GREEN (WRONG)'))
        if not ok:
            fails.append(label)

    # N9 - and the exemption must be LOAD-BEARING, not decoration: with it removed, the
    #      shipped build's thrown class must actually red D3. If this comes back green the
    #      carve-out is protecting nothing and should be deleted.
    saved_set = SLD.D3_ERA_EXEMPT
    try:
        SLD.D3_ERA_EXEMPT = ()
        d3 = [p for p in SAB.audit_db(base, base_lk)[0]
              if p.startswith('D3') and 'thrown' in p]
    finally:
        SLD.D3_ERA_EXEMPT = saved_set
    ok = bool(d3)
    print("%s  %-72s -> %s" % ('OK ' if ok else 'FAIL',
                               "D3X exemption removed (it must be load-bearing)",
                               ('RED (correct), %d D3 thrown finding(s)' % len(d3)) if ok
                               else 'GREEN (WRONG - the exemption is decoration)'))
    if not ok:
        fails.append("D3X exemption is decoration")

    print()
    if fails:
        print("NEGTEST FAILED: %d" % len(fails))
        for f in fails:
            print("   - %s" % f)
        return 1
    print("NEGTEST PASS: every planted skew reds the distribution gate, the D3 size "
          "exemption reds when it stops being earned and is load-bearing when it is, and "
          "both the fixed build and its deliberate themes stay green.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
