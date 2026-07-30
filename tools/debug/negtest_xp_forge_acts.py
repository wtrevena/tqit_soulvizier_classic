"""negtest_xp_forge_acts.py - PLANTED NEGATIVES for the R-100 #11 forge gate.

Proves soul_act_classifier.verify_xp_formula_membership() actually fires. Each
case breaks ONE invariant on a fresh in-memory copy of a real built arz and
asserts the gate reds with the matching invariant id; the positive control
asserts the unmodified build is green.

Usage: py tools/debug/negtest_xp_forge_acts.py <built.arz>
Exit 0 = every negative fired and the control passed.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase
import soul_act_classifier as sac


def load(p):
    return ArzDatabase.from_arz(Path(p))


def main(argv):
    arz = argv[1]
    fails = []

    # ---- POSITIVE CONTROL --------------------------------------------------
    db = load(arz)
    ctrl = sac.verify_xp_formula_membership(db)
    ok = not ctrl
    print("%s POSITIVE CONTROL: unmodified build is %s"
          % ('OK ' if ok else 'XX ', 'GREEN' if ok else 'RED: %s' % ctrl[:3]))
    if not ok:
        fails.append('positive control red')

    _act_of, formulas = sac.read_formula_membership(db)
    n1 = formulas[('n', 1)]
    e1 = formulas[('e', 1)]

    def vals(d, rec, f=sac.REAGENT_FIELDS[0]):
        return sac._field_values(d, rec, f)

    def check(label, mutate, want_id):
        d = load(arz)
        mutate(d)
        got = sac.verify_xp_formula_membership(d)
        hit = any(p.startswith(want_id) for p in got)
        if not hit:
            fails.append('%s: gate did not fire %s (got %s)'
                         % (label, want_id, got[:2]))
        print("%s %-58s -> %s"
              % ('OK ' if hit else 'XX ', label,
                 'RED %s (correct)' % want_id if hit else 'GREEN (BLIND)'))

    # I1 dangling reagent
    check("I1 a reagent pointing at a record that does not exist",
          lambda d: d.set_field(n1, sac.REAGENT_FIELDS[0],
                                vals(d, n1) + [r'records\item\equipmentring\soul\NOPE_soul_n.dbr']),
          'I1')
    # I2 the three slots disagree
    check("I2 reagent2BaseName made to disagree with reagent1BaseName",
          lambda d: d.set_field(n1, sac.REAGENT_FIELDS[1],
                                vals(d, n1, sac.REAGENT_FIELDS[1])[:-1]),
          'I2')
    # I3 the anysoul display item no longer first
    check("I3 the anysoul display item dropped from entry[0]",
          lambda d: [d.set_field(n1, f, vals(d, n1, f)[1:])
                     for f in sac.REAGENT_FIELDS],
          'I3')
    # I4 cross-tier contamination
    check("I4 a legendary-tier soul listed in the NORMAL act-1 formula",
          lambda d: [d.set_field(n1, f, vals(d, n1, f) +
                                 [r'records\item\equipmentring\soul\arachnos\arachne_soul_l.dbr'])
                     for f in sac.REAGENT_FIELDS],
          'I4')
    # I5 an assigned soul missing from its formula (simulates the shipped bug:
    # a minted soul that never made it into the list).
    #
    # ⚠️ THIS TEST USED TO BE VACUOUS AND REPORTED ITSELF AS BLIND. It picked its
    # target from `classify_soul_acts(d)` on the UNMUTATED db - but the wiring
    # pass runs to a FIXED POINT, so on a real build every evidence-assignable
    # soul is already listed, `classify_soul_acts` returns an EMPTY assignment
    # map (the build log's own "signals in the final round:
    # {'S0-already-listed': 2149}"), `target` came back None, and the mutation
    # never happened. The gate was then correctly green and the test called it
    # "GREEN (BLIND)" - a false accusation against a working invariant, which is
    # just as bad as a false green.
    #
    # Correct construction: take a soul the formula ALREADY lists, and one whose
    # OTHER tiers are listed too, so that once it is removed the classifier
    # re-derives its act from S1-sibling-tier and I5 must fire. Anything the
    # classifier could not re-derive would (rightly) not be an I5 violation.
    def _reclassifiable_member(d):
        listed_e = [v for v in vals(d, e1) if 'anysoul' not in sac._stem(v)]
        n1_have = {sac._n(v) for v in vals(d, n1)}
        for v in listed_e:
            sib_n = sac.soul_base(v) + '.dbr'          # the n-tier sibling path
            if sac._n(sib_n) in n1_have:
                return v
        return None

    def drop_an_assigned(d):
        target = _reclassifiable_member(d)
        if target is None:
            raise SystemExit(
                "negtest I5 setup: no act-1 epic soul in e_01 whose NORMAL "
                "sibling is listed in n_01 - cannot construct a soul the "
                "classifier is guaranteed to re-derive, so the I5 negative "
                "would be vacuous. Refusing to report a pass it did not earn.")
        for f in sac.REAGENT_FIELDS:
            d.set_field(e1, f, [v for v in vals(d, e1, f)
                                if sac._n(v) != sac._n(target)])
    check("I5 an act-assigned soul removed from its formula (the shipped bug)",
          drop_an_assigned, 'I5')

    print()
    if fails:
        print("NEGTEST FAILED: %d" % len(fails))
        for f in fails:
            print("   - %s" % f)
        return 1
    print("NEGTEST PASS: every planted violation reds the gate and the "
          "unmodified build is green.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
