r"""THE shared soul -> ACT classifier for the XP-potion forge formulas (R-100 #11).

WILL, VERBATIM (R-100 #11): "there are forge formulas for experience potions that
require souls from a specific act, but the souls that we added for the new
monsters we added into those acts and probably the souls we added that were
missing do not have the proper classification on them so you cant use them in
the forge formulas."

WHAT THE "CLASSIFICATION" ACTUALLY IS - MEASURED, and it is NOT a field.
SV 0.98i ships 12 `ItemArtifactFormula` records:

    records\item\formulas\{n,e,l}_{01..04}_lesserpotionofexperience_formula.dbr

`{n,e,l}` = the difficulty tier of the potion, `{01..04}` = the ACT
(1 Greece, 2 Egypt, 3 Orient, 4 Hades). Each formula's three reagent slots
(`reagent1BaseName` / `reagent2BaseName` / `reagent3BaseName`, all three carrying
the SAME list) enumerate, LITERALLY:

    [ 0X_actY_anysoul.dbr, <every soul of that act at that difficulty> ]

e.g. `e_01_lesserpotionofexperience_formula` holds 152 entries: the
`02_act1_anysoul` display item plus 151 `*_soul_e.dbr` paths. So a soul is "act
N" **iff it is named in act N's formula list**. There is no act field to set: a
soul we mint is unusable in the forge until its path is appended to the right
list. (Proof: tools/debug/probe_xp_formula_reagents.py.)

THE ACT SIGNALS. A soul's act cannot be invented, so every assignment below is
derived from evidence already in the database, in this precedence order, and a
soul that no signal resolves is REPORTED, never guessed:

  S0 already listed by a formula                 (the authority; nothing to do)
  S1 a sibling TIER of the same soul is listed   (n/e/l triples share an act)
  S2 the dropping monster lives under            -> act 4
     `records\xpack\` (Immortal Throne = Hades)
  S3 the dropping monster is spawned by a base   -> that region's act
     population proxy under `records\proxies <region>\`
     (greek -> 1, egypt -> 2, orient -> 3), by dominant majority
  S4 other classified souls dropped by monsters  -> that act
     in the SAME monster folder, when unanimous
  S5 other classified souls in the SAME soul     -> that act
     folder, when unanimous

S3/S4/S5 are majority/unanimity rules over the base game's OWN act assignment of
the same creature family, so the mod's souls inherit the game's own answer rather
than a designer's guess.

NOT COVERED, deliberately: there is no act-5 (Ragnarok) or act-6 formula in SV
0.98i or the base game, so a soul whose monster lives under `records\xpack2\` /
`records\xpack3\` has no list to join. Those are reported, not forced into act 4.
"""
from collections import Counter, defaultdict

FORMULA_FMT = r'records\item\formulas\%s_%02d_lesserpotionofexperience_formula.dbr'
FORMULA_TIERS = ('n', 'e', 'l')
FORMULA_ACTS = (1, 2, 3, 4)
REAGENT_FIELDS = ('reagent1BaseName', 'reagent2BaseName', 'reagent3BaseName')

# `records\proxies <region>\...` -> act. The base game's population proxies are
# filed by region, and region == act for the first three acts.
PROXY_REGION_ACT = (('greek', 1), ('egypt', 2), ('orient', 3))

_SOUL_DIR_MARKER = 'equipmentring\\soul\\'


def _n(s):
    return str(s).replace('/', '\\').lower()


def _stem(p):
    return _n(p).rsplit('\\', 1)[-1].replace('.dbr', '')


def soul_tier(path):
    """'n' / 'e' / 'l' from a soul record path, or None."""
    st = _stem(path)
    for t in FORMULA_TIERS:
        if st.endswith('_' + t):
            return t
    # SV's own untiered normal souls (soul\test\um_alethadarkclaw.dbr) read as
    # the NORMAL tier: their _e / _l siblings carry the suffix, this one does not.
    return 'n' if st else None


def soul_base(path):
    st = _stem(path)
    for t in FORMULA_TIERS:
        if st.endswith('_' + t):
            return _n(path).rsplit('\\', 1)[0] + '\\' + st[:-2]
    return _n(path).rsplit('\\', 1)[0] + '\\' + st


def _field_values(db, rec, field):
    ff = db.get_fields(rec) or {}
    for k, tf in ff.items():
        if k.split('###')[0] == field:
            return [v for v in tf.values if isinstance(v, str) and v]
    return []


def read_formula_membership(db):
    """{soul path (normalized) -> act} from the 12 shipped formulas, plus
    {(tier, act) -> formula record} for the ones that exist."""
    act_of = {}
    formulas = {}
    names = {_n(x): x for x in db.record_names()}
    for tier in FORMULA_TIERS:
        for act in FORMULA_ACTS:
            rec = names.get(_n(FORMULA_FMT % (tier, act)))
            if not rec:
                continue
            formulas[(tier, act)] = rec
            for v in _field_values(db, rec, REAGENT_FIELDS[0]):
                act_of[_n(v)] = act
    return act_of, formulas


def _droppers(db):
    """{soul path -> set(monster record)} from lootFinger2Item1."""
    out = defaultdict(set)
    for rec in db.record_names():
        for v in _field_values(db, rec, 'lootFinger2Item1'):
            if _SOUL_DIR_MARKER in _n(v):
                out[_n(v)].add(_n(rec))
    return out


def _proxy_region_acts(db):
    """{monster record -> Counter(act)} from base population-proxy membership."""
    out = defaultdict(Counter)
    for rec in db.record_names():
        rl = _n(rec)
        if not rl.startswith('records\\proxies'):
            continue
        seg = rl.split('\\')[1]
        act = next((a for key, a in PROXY_REGION_ACT if key in seg), None)
        if act is None:
            continue
        ff = db.get_fields(rec) or {}
        for k, tf in ff.items():
            for v in tf.values:
                if isinstance(v, str) and '\\creature' in _n(v):
                    out[_n(v)][act] += 1
    return out


def _dominant(counter):
    """The clearly-dominant key, or None. Dominant = sole key, or at least twice
    every other key summed (so a family that genuinely spans acts stays
    unresolved instead of being coin-flipped)."""
    if not counter:
        return None
    top, cnt = counter.most_common(1)[0]
    rest = sum(v for k, v in counter.items() if k != top)
    return top if (rest == 0 or cnt >= 2 * rest) else None


def classify_soul_acts(db):
    """Return (assignments, unresolved, stats).

    assignments: {soul path (as stored in the db) -> (act, signal)} for every
                 soul NOT already listed by a formula that evidence can place.
    unresolved:  [(soul path, reason)] - reported, never guessed.
    stats:       Counter of signal -> count.
    """
    act_of, _formulas = read_formula_membership(db)
    drop_of = _droppers(db)
    region_of = _proxy_region_acts(db)

    souls = [r for r in db.record_names()
             if _SOUL_DIR_MARKER in _n(r) and 'anysoul' not in _n(r)]

    # folder-level act priors, learned from the souls the formulas already place
    soul_folder_acts = defaultdict(Counter)
    monster_folder_acts = defaultdict(Counter)
    for p, a in act_of.items():
        soul_folder_acts['\\'.join(p.split('\\')[:-1])][a] += 1
        for m in drop_of.get(p, ()):
            monster_folder_acts['\\'.join(m.split('\\')[:-1])][a] += 1

    # S1 needs the base -> tier map
    tiers_of_base = defaultdict(dict)
    for s in souls:
        t = soul_tier(s)
        if t:
            tiers_of_base[soul_base(s)][t] = _n(s)

    assignments = {}
    unresolved = []
    stats = Counter()
    for s in souls:
        p = _n(s)
        if p in act_of:
            stats['S0-already-listed'] += 1
            continue
        tier = soul_tier(s)
        if tier is None:
            unresolved.append((s, 'no n/e/l tier suffix'))
            continue
        sig = act = None
        # S1 sibling tier
        sib = {act_of[q] for q in tiers_of_base.get(soul_base(s), {}).values()
               if q in act_of}
        if len(sib) == 1:
            act, sig = sib.pop(), 'S1-sibling-tier'
        ms = drop_of.get(p, set())
        if act is None and any(m.startswith('records\\xpack\\') for m in ms):
            if not any(m.startswith(('records\\xpack2\\', 'records\\xpack3\\'))
                       for m in ms):
                act, sig = 4, 'S2-xpack-namespace'
        if act is None and ms:
            votes = Counter()
            for m in ms:
                votes.update(region_of.get(m, {}))
            d = _dominant(votes)
            if d:
                act, sig = d, 'S3-proxy-region'
        if act is None and ms:
            votes = Counter()
            for m in ms:
                votes.update(monster_folder_acts.get('\\'.join(m.split('\\')[:-1]), {}))
            d = _dominant(votes)
            if d:
                act, sig = d, 'S4-monster-folder'
        if act is None:
            fa = soul_folder_acts.get('\\'.join(p.split('\\')[:-1]))
            if fa and len(fa) == 1:
                act, sig = next(iter(fa)), 'S5-soul-folder'
        if act is None:
            if not ms:
                unresolved.append((s, 'no monster drops it (unobtainable)'))
            elif any(m.startswith(('records\\xpack2\\', 'records\\xpack3\\'))
                     for m in ms):
                unresolved.append((s, 'act 5/6 monster - no act-5 formula exists'))
            else:
                unresolved.append((s, 'no dominant act signal'))
            continue
        assignments[s] = (act, sig)
        stats[sig] += 1
    return assignments, unresolved, stats


def wire_souls_into_xp_formulas(db, verbose=True):
    """Append every evidence-assigned soul to its act+tier formula's reagent
    lists. Idempotent (membership is a set), deterministic (sorted), additive
    only: no existing entry is ever removed or reordered away - the formula's
    original first entry (the `0X_actY_anysoul` display item) stays first.

    Returns (added, unresolved, stats).
    """
    act_of, formulas = read_formula_membership(db)
    assignments, unresolved, stats = classify_soul_acts(db)
    if not formulas:
        if verbose:
            print("  XP-forge acts: no lesserpotionofexperience formulas in this "
                  "db - nothing to wire")
        return 0, unresolved, stats

    per_formula = defaultdict(list)
    for soul, (act, _sig) in assignments.items():
        tier = soul_tier(soul)
        key = (tier, act)
        if key in formulas:
            per_formula[key].append(soul)

    added = 0
    for key in sorted(per_formula):
        rec = formulas[key]
        for field in REAGENT_FIELDS:
            existing = _field_values(db, rec, field)
            if not existing:
                continue
            have = {_n(v) for v in existing}
            new = [s for s in sorted(per_formula[key]) if _n(s) not in have]
            if not new:
                continue
            db.set_field(rec, field, list(existing) + new)
            db._modified.add(rec)
            if field == REAGENT_FIELDS[0]:
                added += len(new)
                if verbose:
                    print("    %s_%02d formula: +%d souls (now %d reagent entries)"
                          % (key[0], key[1], len(new), len(existing) + len(new)))
    if verbose:
        print("  XP-forge acts (R-100 #11): %d soul->formula memberships added; "
              "signals: %s" % (added, dict(stats)))
        if unresolved:
            why = Counter(r for _s, r in unresolved)
            print("    UNRESOLVED (reported, never guessed): %d - %s"
                  % (len(unresolved), dict(why)))
    return added, unresolved, stats


# ─────────────────────────────────────────────────────────────────────────────
# THE GATE (process law #4: a new player-visible surface ships its gate).
# Negative tests: tools/debug/negtest_xp_forge_acts.py plants a violation of
# each invariant below and proves this function reds on every one.
# ─────────────────────────────────────────────────────────────────────────────
def verify_xp_formula_membership(db):
    """Fail-loud invariants over the 12 XP-potion formulas. Returns a list of
    problem strings (empty == PASS).

    I1  every reagent path RESOLVES to a real record (a dangling reagent is a
        forge entry the player can never satisfy - the failure mode that makes
        this whole item a player-facing block).
    I2  the three reagent slots of a formula carry the SAME list (SV's shipped
        invariant: any of the three slots accepts any eligible soul).
    I3  the formula's own `0X_actY_anysoul` display item is still entry [0].
    I4  NO CROSS-TIER CONTAMINATION: an `e_` formula may not list a `_n` or `_l`
        soul, and so on. This is what a mis-assigned soul looks like.
    I5  every soul the classifier assigns to (tier, act) IS in that formula.
    """
    problems = []
    act_of, formulas = read_formula_membership(db)
    if not formulas:
        return ["no lesserpotionofexperience formulas present"]
    have = {_n(x) for x in db.record_names()}
    tier_num = {'n': '01', 'e': '02', 'l': '03'}
    for (tier, act), rec in sorted(formulas.items()):
        lists = [_field_values(db, rec, f) for f in REAGENT_FIELDS]
        first = lists[0]
        for i, lst in enumerate(lists[1:], start=2):
            if [_n(v) for v in lst] != [_n(v) for v in first]:
                problems.append(
                    "I2 %s: reagent%dBaseName differs from reagent1BaseName "
                    "(%d vs %d entries)" % (rec, i, len(lst), len(first)))
        want_any = 'records/item/equipmentring/soul/%s_act%d_anysoul.dbr' % (
            tier_num[tier], act)
        if not first or _n(first[0]) != _n(want_any):
            problems.append("I3 %s: entry[0] is %r, expected the display item %r"
                            % (rec, first[0] if first else None, want_any))
        for v in first:
            if _n(v) not in have:
                problems.append("I1 %s: reagent %s does not resolve to a record"
                                % (rec, v))
            st = _stem(v)
            if 'anysoul' in st:
                continue
            for other in FORMULA_TIERS:
                if other != tier and st.endswith('_' + other):
                    problems.append(
                        "I4 %s (tier %s): lists a %s-tier soul %s"
                        % (rec, tier, other, v))
    assignments, _unresolved, _stats = classify_soul_acts(db)
    for soul, (act, sig) in assignments.items():
        tier = soul_tier(soul)
        rec = formulas.get((tier, act))
        if rec is None:
            continue
        if _n(soul) not in {_n(v) for v in _field_values(db, rec, REAGENT_FIELDS[0])}:
            problems.append("I5 %s: assigned act %d (%s) but not listed in %s"
                            % (soul, act, sig, rec))
    return problems
