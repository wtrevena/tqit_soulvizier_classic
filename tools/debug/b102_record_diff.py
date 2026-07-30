#!/usr/bin/env python3
<<<<<<< HEAD
r"""b102 (devourer_kit) record-diff: every delta must be ATTRIBUTABLE to the wave.
=======
r"""b102 record-diff: every delta must be ATTRIBUTABLE to R-105/R-106/R-107,
R-100 #11 or R-100 #17. Anything else is an unattributed change and fails.
>>>>>>> feat/soul-economy

Usage:
  py tools/debug/b102_record_diff.py <baseline.arz> <built.arz>

<<<<<<< HEAD
Baseline = a build of `main` @ 7efd107 in THIS environment. The measured baseline
is **6a3a491db546b603c52132237c40aa63**, 55,475,226 B, 51,124 records - which is
byte-identical to the arz the b101 BACKLOG gate record already names as the built
artefact of `feat/toxeus-apex-roster`, i.e. the determinism of the build is itself
proven by the baseline reproducing that md5 exactly.

Built = a build of `feat/devourer-kit` (main + tools/patches/devourer_kit.py).

WHAT THE WHOLE DIFF IS ALLOWED TO BE, and why it is this small. Everything the
wave does is either a NEW record or a named field on a named record:

  ADDED (7)
    skills\monster skills\passive_buffs\svc_toxeus_passiveproperties_monster.dbr
    skills\boss skills\svc_devourer_bloodbath.dbr
    skills\boss skills\svc_devourer_summonbloodspawn.dbr
    skills\boss skills\svc_hunt_summoncoursers.dbr
    drxcreatures\blooddemon\um_devourer_bloodspawn_99.dbr
    drxcreatures\bloodhound\um_hunt_courser_99.dbr
    drxcreatures\bloodhound\skills\svc_courser_bloodspew.dbr

  CHANGED - the 6 Toxeus MONSTERS, one skillName<i> slot each (the reflect
  repoint), plus on the Devourer: defensivePierce, skillName1 +
  specialAttackSkillName (Bloodbath), skillName18 + specialAttack5* (the summon);
  plus on both Hunts: skillName13 + specialAttack5* (the summon); plus
  svc_enslaver_summonmarauders losing its unbound skillSpecialAnimationName.

  REMOVED - MUST BE ZERO. Nothing is retired by this wave. In particular
  toxeus_passiveproperties, melinoe_bloodboil and
  t1_skill_pitspawner_summonlildude_02 must all survive UNCHANGED (the first two
  are proven byte-identical by rule, the third simply must not appear in the diff
  at all).

ATTRIBUTION IS DELIBERATELY STRICT in both directions: an added record must match
a rule on its PATH, a changed record must match on its path AND every one of its
moved fields must be in that rule's allowed set, and ANY removed record fails
outright. A delta that matches nothing is UNATTRIBUTED and is a NO-GO.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase  # noqa: E402


def norm(s):
    return s.lower().replace('/', '\\')


NEW_RECORDS = {norm(p) for p in (
    r'records\skills\monster skills\passive_buffs\svc_toxeus_passiveproperties_monster.dbr',
    r'records\skills\boss skills\svc_devourer_bloodbath.dbr',
    r'records\skills\boss skills\svc_devourer_summonbloodspawn.dbr',
    r'records\skills\boss skills\svc_hunt_summoncoursers.dbr',
    r'records\drxcreatures\blooddemon\um_devourer_bloodspawn_99.dbr',
    r'records\drxcreatures\bloodhound\um_hunt_courser_99.dbr',
    r'records\drxcreatures\bloodhound\skills\svc_courser_bloodspew.dbr',
)}

DEVOURER = norm(r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr')
HUNTS = {norm(r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr'),
         norm(r'records\creature\monster\shadowstalker\um_toxeus_hunt_l_99.dbr')}
ENSLAVER = norm(r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr')
OTHER_TOXEUS = {norm(r'records\creature\monster\skeleton\um_toxeus_21.dbr'),
                norm(r'records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr')}
ENSLAVER_SUMMON = norm(r'records\skills\boss skills\svc_enslaver_summonmarauders.dbr')

# Records that MUST NOT move at all - the whole point of the clone-not-edit work.
MUST_BE_UNTOUCHED = {
    norm(r'records\skills\monster skills\passive_buffs\toxeus_passiveproperties.dbr'):
        'the SHARED Toxeus passive (9 PET carriers + a DRX crow hero) - R-107 Part 2',
    norm(r'records\skills\soulskills\melinoe_bloodboil.dbr'):
        'the SHARED Bloodbath donor (6 Toxeus PET carriers)',
    norm(r'records\drxmap\pitsprites\t1_skill_pitspawner_summonlildude_02.dbr'):
        'the SHARED pit-spawner (2 other carriers) - RETIREMENT PROTOCOL',
    norm(r'records\drxcreatures\blooddemon\c_large_blooddemon_40.dbr'):
        'the Gorged Bloodspawn DONOR',
    norm(r'records\drxcreatures\bloodhound\c_bloodhound_44.dbr'):
        'the Courser DONOR',
    norm(r'records\drxcreatures\bloodhound\skills\puke.dbr'):
        'the Courser-spit DONOR',
    norm(r'records\skills\monster skills\passive_buffs\quak_bloodfrenzy.dbr'):
        "Blood Frenzy - present already, asserted not re-authored",
}
# and every pet that must keep 100/33 reflect
MUST_BE_UNTOUCHED.update({
    norm(r'records\skills\soulskills\pets\%s_%d.dbr' % (fam, i)):
        'a Toxeus PET - must keep the ORIGINAL 100/33 reflect (R-107 Part 2)'
    for fam in ('toxeus_enslaver', 'bloodtoxeus', 'toxeus_eoat') for i in (1, 2, 3)})
MUST_BE_UNTOUCHED[norm(r'records\drxcreatures\crowheroes\less.dbr')] = \
    'a DRX crow hero that is not ours to retune (R-107 Part 2)'

_SKILLNAME = re.compile(r'^skillName\d+$')
_SKILLLEVEL = re.compile(r'^skillLevel\d+$')


def _reflect_repoint_only(f):
    return bool(_SKILLNAME.match(f))


RULES = [
    ('b102 new records', lambda r: r in NEW_RECORDS, lambda f: True),

    ('b102 Devourer (reflect repoint + pierce + Bloodbath + summon)',
     lambda r: r == DEVOURER,
     lambda f: (_SKILLNAME.match(f) or _SKILLLEVEL.match(f) or f in {
         'defensivePierce', 'specialAttackSkillName',
         'specialAttack5SkillName', 'specialAttack5Chance'})),

    ('b102 Endless Hunt N+L (reflect repoint + courser summon)',
     lambda r: r in HUNTS,
     lambda f: (_SKILLNAME.match(f) or _SKILLLEVEL.match(f) or f in {
         'specialAttack5SkillName', 'specialAttack5Chance'})),

    ('b102 Enslaver (reflect repoint only)',
     lambda r: r == ENSLAVER, _reflect_repoint_only),

    ('b102 um_toxeus_21 / um_toxeus_99 (reflect repoint only)',
     lambda r: r in OTHER_TOXEUS, _reflect_repoint_only),

    ('b102 Enslaver summon (unbound B-SOUL-PROC-2 anim deleted)',
     lambda r: r == ENSLAVER_SUMMON,
     lambda f: f == 'skillSpecialAnimationName'),
]


def attribute(rec, fields):
    for lane, rec_ok, fld_ok in RULES:
        if rec_ok(rec):
            bad = {f for f in fields if not fld_ok(f)}
            return lane, bad
    return None, set(fields)


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    base = ArzDatabase.from_arz(Path(argv[0]))
    built = ArzDatabase.from_arz(Path(argv[1]))

    bmap = {norm(n): n for n in base.record_names()}
    tmap = {norm(n): n for n in built.record_names()}
    bnames, tnames = set(bmap), set(tmap)
    added = sorted(tnames - bnames)
    removed = sorted(bnames - tnames)

    def val(f, k):
        return (f[k].dtype, list(f[k].values)) if k in f else None

    changed = {}
    for n in sorted(bnames & tnames):
        fb = base.get_fields(bmap[n]) or {}
        ft = built.get_fields(tmap[n]) or {}
        d = {}
        for k in sorted(set(fb) | set(ft)):
            vb, vt = val(fb, k), val(ft, k)
            if vb != vt:
                d[k.split('###')[0]] = (vb, vt)
        if d:
            changed[n] = d

    print('=' * 78)
    print('b102 DEVOURER-KIT RECORD DIFF')
    print('  baseline : %s' % argv[0])
    print('  built    : %s' % argv[1])
    print('  records  : baseline %d -> built %d' % (len(bnames), len(tnames)))
    print('  ADDED %d / REMOVED %d / CHANGED %d' % (len(added), len(removed), len(changed)))
    print('=' * 78)

    buckets = defaultdict(list)
    unattributed = []

    for n in added:
        lane, _ = attribute(n, set())
        if lane is None:
            unattributed.append(('ADDED', n, set()))
        else:
            buckets[lane].append('ADDED   ' + n)
    for n in removed:
        unattributed.append(('REMOVED', n, set()))
    for n, d in changed.items():
        lane, bad = attribute(n, set(d))
        if lane is None or bad:
            unattributed.append(('CHANGED', n, bad or set(d)))
        else:
            buckets[lane].append('CHANGED ' + n + '  [' + ', '.join(sorted(d)) + ']')

    print('\n--- ATTRIBUTION ---')
    for lane in sorted(buckets):
        print('\n[%s]  %d record(s)' % (lane, len(buckets[lane])))
        for line in buckets[lane]:
            print('   ' + line)

    print('\n--- THE CLONE-NOT-EDIT PROOF (records that must be byte-unchanged) ---')
    leaks = []
    for rec, why in sorted(MUST_BE_UNTOUCHED.items()):
        if rec not in tnames:
            print('   MISSING   %s  (%s)' % (rec, why))
            leaks.append(rec)
        elif rec in changed:
            print('   ** MOVED  %s  fields=%s  (%s)'
                  % (rec, sorted(changed[rec]), why))
            leaks.append(rec)
        else:
            print('   unchanged %s' % rec)

    print('\n--- FIELD DETAIL (every changed record) ---')
    for n, d in changed.items():
        print('\n  %s' % n)
        for k, (vb, vt) in d.items():
            print('     %-30s %r -> %r' % (k, vb, vt))

    print('\n' + '=' * 78)
    fail = bool(unattributed) or bool(leaks)
    if unattributed:
        print('UNATTRIBUTED DELTAS: %d  ** NO-GO **' % len(unattributed))
        for kind, n, bad in unattributed:
            print('   %-8s %s %s'
                  % (kind, n, ('fields=' + ','.join(sorted(bad))) if bad else ''))
    if leaks:
        print('SHARED-RECORD LEAKS: %d  ** NO-GO **' % len(leaks))
    if fail:
        return 1
    print('RESULT: PASS - %d ADDED / 0 REMOVED / %d CHANGED, every one attributable '
          'to b102, and all %d shared/donor records byte-unchanged.'
          % (len(added), len(changed), len(MUST_BE_UNTOUCHED)))
=======
Baseline = a build of `main` in THIS environment, made BEFORE any of this lane's
edits (local/baseline_main.arz, md5 6a3a491db546b603c52132237c40aa63,
55,475,226 B, 51,124 records, main @ 7efd107).

THE THREE LEGITIMATE DELTA CLASSES, each checked against the code that produced
it rather than against a list typed into this file:

  A  chanceToEquipFinger2 on a soul carrier, and the new value is EXACTLY what
     build_svc_database.ruled_soul_equip_rate() says (the ONE shared
     classifier). No other field on that record may differ.
  B  reagent1/2/3BaseName on one of the 12 lesserpotionofexperience formulas,
     and the change is ADDITIVE ONLY - every baseline entry still present, in
     the same order, with new entries appended.
  C  the Polis vault loot tables' guaranteed slots moving off the normal-tier
     donors (unique_1h_n01 / 01_act4_relics) onto the chest's own legendary
     tier (unique_1h_l01 / 03_act4_relics).

A REMOVED record is ALWAYS a failure (retirement protocol: this lane withdrew
chest PLACEMENTS, never records). An ADDED record is a failure too - none of the
three items creates content.

Exit 0 = every delta attributed, 0 removed, 0 added.
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / 'patches'))

from arz_patcher import ArzDatabase          # noqa: E402
import build_svc_database as bsd             # noqa: E402
import apply_svc_patches as asp              # noqa: E402
import soul_act_classifier as sac            # noqa: E402


def norm(s):
    return str(s).lower().replace('/', '\\')


def fields_of(db, name):
    out = {}
    ff = db.get_fields(name)
    if not ff:
        return out
    for k, tf in ff.items():
        out.setdefault(k.split('###')[0], list(tf.values))
    return out


_NORMAL_TIER = ('unique_1h_n01.dbr', '01_act4_relics.dbr')
_LEGENDARY_TIER = ('unique_1h_l01.dbr', '03_act4_relics.dbr')


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    old = ArzDatabase.from_arz(Path(argv[1]))
    new = ArzDatabase.from_arz(Path(argv[2]))
    old_names = {norm(n): n for n in old.record_names()}
    new_names = {norm(n): n for n in new.record_names()}
    print("baseline records: %d   built records: %d" % (len(old_names), len(new_names)))

    removed = sorted(set(old_names) - set(new_names))
    added = sorted(set(new_names) - set(old_names))
    print("REMOVED: %d    ADDED: %d" % (len(removed), len(added)))

    # the ruled rate for every carrier, from the SHARED classifier over the BUILT db
    rmem, pmem = bsd.soul_spawn_provenance_sets(new)
    ruled = {}
    for rec, cls, cur in asp._soul_carrier_roster(new):
        ruled[norm(rec)] = bsd.ruled_soul_equip_rate(rec, cls, cur, rmem, pmem)
    # the 12 formulas
    _act_of, formulas = sac.read_formula_membership(new)
    formula_recs = {norm(r) for r in formulas.values()}
    # the vault loot tables
    import polis_vault as pv
    vault_loot = {norm(x) for x in pv._CHEST_LOOT}

    classes = Counter()
    unattributed = []
    field_hist = Counter()
    for key in sorted(set(old_names) & set(new_names)):
        fo = fields_of(old, old_names[key])
        fn = fields_of(new, new_names[key])
        changed = [f for f in set(fo) | set(fn) if fo.get(f) != fn.get(f)]
        if not changed:
            continue
        for f in changed:
            field_hist[f] += 1
        ok = True
        why = []
        for f in changed:
            if f == 'chanceToEquipFinger2' and key in ruled:
                want = ruled[key]
                got = float(fn.get(f, [0])[0])
                if want is not None and abs(got - want) < 0.01:
                    why.append('A')
                    continue
                ok = False
                why.append('A?%s(want %s got %s)' % (f, want, got))
            elif f in sac.REAGENT_FIELDS and key in formula_recs:
                before = [norm(v) for v in fo.get(f, [])]
                after = [norm(v) for v in fn.get(f, [])]
                if after[:len(before)] == before and len(after) >= len(before):
                    why.append('B')
                    continue
                ok = False
                why.append('B?%s(not additive)' % f)
            elif key in vault_loot and f.lower().startswith('loot'):
                b = norm(fo.get(f, [''])[0] if fo.get(f) else '')
                a = norm(fn.get(f, [''])[0] if fn.get(f) else '')
                if any(b.endswith(m) for m in _NORMAL_TIER) and \
                   any(a.endswith(m) for m in _LEGENDARY_TIER):
                    why.append('C')
                    continue
                ok = False
                why.append('C?%s(%s -> %s)' % (f, b, a))
            else:
                ok = False
                why.append('X:%s' % f)
        if ok:
            classes[''.join(sorted(set(why)))] += 1
        else:
            unattributed.append((new_names[key], why))

    print("\nATTRIBUTED modified records by class:")
    for k, v in sorted(classes.items()):
        print("   class %-6s %d" % (k or '(none)', v))
    print("   TOTAL attributed: %d" % sum(classes.values()))
    print("\nchanged-field histogram: %s" % dict(field_hist))

    fail = False
    if removed:
        fail = True
        print("\nFAIL - REMOVED records (%d):" % len(removed))
        for r in removed[:20]:
            print("   ", r)
    if added:
        fail = True
        print("\nFAIL - ADDED records (%d):" % len(added))
        for r in added[:20]:
            print("   ", r)
    if unattributed:
        fail = True
        print("\nFAIL - UNATTRIBUTED modified records (%d):" % len(unattributed))
        for r, why in unattributed[:25]:
            print("    %-72s %s" % (r, why))
    if fail:
        return 1
    print("\nPASS: %d modified records, ALL attributed to R-105/106/107 (A), "
          "R-100 #11 (B) or R-100 #17 (C); 0 REMOVED, 0 ADDED."
          % sum(classes.values()))
>>>>>>> feat/soul-economy
    return 0


if __name__ == '__main__':
<<<<<<< HEAD
    sys.exit(main(sys.argv[1:]))
=======
    sys.exit(main(sys.argv))
>>>>>>> feat/soul-economy
