"""GOLDEN FREEZE GUARD for the owner's hand-tuned masteries (A7, build29).

Occult (mastery UI slot 5) and Hunting (mastery UI slot 6) carry Will's manual
hand-tuning (STANDING RULE: never revert them; content changes need owner
sign-off). This tool freezes their COMPLETE observable state into a golden
snapshot (tools/occult_hunting_golden.json) and fail-loudly gates every build
against it:

  captured state (re-derived from the FINAL artifacts, not from build scripts):
    - every UI record under records\\ingameui\\player skills\\mastery {5,6}\\
      plus the xpack/xpack3 panectrl overrides: full field map + record_type
      (covers slot bindings, positions, button lists);
    - the TREE: each slot's skillName target skill record (full field map +
      record_type), plus one hop of buffSkillName/petSkillName sub-records
      (delegating classes keep their payload there);
    - the tree skillName LISTS per mastery (readable drift reports);
    - the effective Text state of every name/desc tag referenced by any
      captured record, plus the mastery-select screen tags
      (tagSkillName050/060, tagMasteryTitle/Brief/Description05/06): EVERY
      definition line, per text file, in order (the engine keeps the FIRST
      definition, so definition order is load-bearing - B-MASTERY-LABEL-1).

  drift policy: ANY difference vs the golden fails the build unless the drift
  key is listed in the golden's "owner_approved_overrides" object (add the key
  printed in the failure output, with a short justification string as value,
  only after Will signs the change off).

usage:
  generate  : py tools/validate_mastery_golden.py --generate <arz> <text.arc>
              [--out tools/occult_hunting_golden.json]
  validate  : py tools/validate_mastery_golden.py <arz> [<text.arc>]
              [--golden tools/occult_hunting_golden.json]
              (text.arc omitted -> tag checks are SKIPPED: the arz-build gate;
               the Text-build gate passes both)
exit codes: 0 = PASS, 1 = DRIFT (or golden missing in validate mode), 2 = usage/load error.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase  # noqa: E402
from arc_patcher import ArcArchive   # noqa: E402

GOLDEN_DEFAULT = Path(__file__).resolve().parent / 'occult_hunting_golden.json'

MASTERIES = {'5': 'Occult', '6': 'Hunting'}

# UI record roots per mastery slot (lowercase, backslash convention).
_UI_DIR = 'records\\ingameui\\player skills\\mastery %s\\'
_PANE_OVERRIDES = ('records\\xpack\\ui\\skills\\mastery %s\\panectrl.dbr',
                   'records\\xpack3\\ui\\skills\\mastery %s\\panectrl.dbr')

# mastery-select screen tags (B-MASTERY-LABEL-1: duplicates are load-bearing).
_SELECT_TAGS = {
    '5': ('tagSkillName050', 'tagMasteryTitle05', 'tagMasteryBrief05',
          'tagMasteryDescription05'),
    '6': ('tagSkillName060', 'tagMasteryTitle06', 'tagMasteryBrief06',
          'tagMasteryDescription06'),
}

# skill fields whose targets are captured one hop deep (delegation payloads).
_SUBREF_FIELDS = ('buffSkillName', 'petSkillName')


def _norm(p):
    return str(p).replace('/', '\\').lower().strip()


def _field_map(db, rec):
    """record -> {fieldName: [dtype, [values as str/int/float]]} (### merged)."""
    out = {}
    ff = db.get_fields(rec)
    if not ff:
        return out
    for key, tf in ff.items():
        fname = key.split('###')[0]
        vals = []
        for v in tf.values:
            if isinstance(v, float):
                # stable, compact float representation
                vals.append(repr(round(v, 6)))
            else:
                vals.append(str(v))
        # merge multi-### fields by concatenation in encounter order
        if fname in out:
            out[fname][1].extend(vals)
        else:
            out[fname] = [int(tf.dtype), vals]
    return out


def _looks_like_tag(v):
    s = str(v).strip()
    return (s.lower().startswith('tag') and '\\' not in s and '/' not in s
            and '.' not in s and 3 < len(s) < 64 and ' ' not in s)


def capture(arz_path, text_path):
    db = ArzDatabase.from_arz(Path(arz_path))
    recmap = {_norm(n): n for n in db.record_names()}

    def resolve(p):
        return recmap.get(_norm(p))

    snap = {'masteries': {}, 'tags': {}, 'owner_approved_overrides': {}}
    all_tags = set()

    for slot, label in MASTERIES.items():
        ui_prefix = _UI_DIR % slot
        ui_recs = sorted(n for n in db.record_names()
                         if _norm(n).startswith(ui_prefix))
        for tmpl in _PANE_OVERRIDES:
            r = resolve(tmpl % slot)
            if r:
                ui_recs.append(r)

        records = {}
        tree = []
        skill_recs = []
        for rec in ui_recs:
            fm = _field_map(db, rec)
            records[rec] = {'record_type': db._record_types.get(rec, ''),
                            'fields': fm}
            base = _norm(rec).rsplit('\\', 1)[-1]
            if base.startswith('skill') or base == 'mastery.dbr':
                sn = fm.get('skillName')
                if sn and sn[1] and str(sn[1][0]).strip():
                    tree.append(str(sn[1][0]))
                    tgt = resolve(sn[1][0])
                    if tgt:
                        skill_recs.append(tgt)

        # the skill records themselves + 1 hop of delegation sub-records
        hop = []
        for srec in skill_recs:
            fm = _field_map(db, srec)
            records[srec] = {'record_type': db._record_types.get(srec, ''),
                             'fields': fm}
            for f in _SUBREF_FIELDS:
                v = fm.get(f)
                if v and v[1] and str(v[1][0]).strip():
                    sub = resolve(v[1][0])
                    if sub and sub not in records:
                        hop.append(sub)
        for sub in hop:
            records[sub] = {'record_type': db._record_types.get(sub, ''),
                            'fields': _field_map(db, sub)}

        # tags referenced by anything captured
        for rec, blob in records.items():
            for fname, (dt, vals) in blob['fields'].items():
                for v in vals:
                    if _looks_like_tag(v):
                        all_tags.add(str(v).strip())
        all_tags.update(_SELECT_TAGS[slot])

        snap['masteries'][slot] = {
            'label': label,
            'tree_skill_names': tree,
            'records': records,
        }

    # Text state: EVERY definition of every captured tag, per file, in order.
    if text_path:
        defs = {t: [] for t in all_tags}
        want = {t.lower(): t for t in all_tags}
        arc = ArcArchive.from_file(Path(text_path))
        for entry in sorted((e for e in arc.entries if e.name), key=lambda e: e.name):
            if not entry.name.lower().endswith('.txt'):
                continue
            txt = arc.get_text(entry.name)
            if txt is None:
                continue
            # Capture [file, value] pairs in ENCOUNTER ORDER (the engine keeps
            # the FIRST definition, so order is load-bearing) - but NOT absolute
            # line numbers, which shift whenever unrelated tags are added above
            # and would false-positive the guard.
            for line in txt.splitlines():
                line = line.strip().lstrip('﻿')
                if not line or line.startswith('//') or '=' not in line:
                    continue
                k, _, val = line.partition('=')
                hit = want.get(k.strip().lower())
                if hit:
                    defs[hit].append([entry.name, val])
        snap['tags'] = {t: defs[t] for t in sorted(defs)}
    else:
        snap['tags'] = None
    return snap


def _diff(golden, current, check_tags):
    """Return list of (drift_key, human message)."""
    drifts = []
    for slot in MASTERIES:
        g = golden['masteries'].get(slot, {})
        c = current['masteries'].get(slot, {})
        label = g.get('label', slot)
        if g.get('tree_skill_names') != c.get('tree_skill_names'):
            drifts.append((f"tree::{slot}",
                           f"{label} tree skillName list changed:\n"
                           f"      golden : {g.get('tree_skill_names')}\n"
                           f"      current: {c.get('tree_skill_names')}"))
        grecs = g.get('records', {})
        crecs = c.get('records', {})
        for rec in sorted(set(grecs) | set(crecs)):
            if rec not in crecs:
                drifts.append((f"record::{rec}", f"{label}: record REMOVED: {rec}"))
                continue
            if rec not in grecs:
                drifts.append((f"record::{rec}", f"{label}: record ADDED: {rec}"))
                continue
            if grecs[rec].get('record_type') != crecs[rec].get('record_type'):
                drifts.append((f"rectype::{rec}",
                               f"{label}: record_type changed on {rec}: "
                               f"{grecs[rec].get('record_type')!r} -> "
                               f"{crecs[rec].get('record_type')!r}"))
            gf = grecs[rec].get('fields', {})
            cf = crecs[rec].get('fields', {})
            for fname in sorted(set(gf) | set(cf)):
                if gf.get(fname) != cf.get(fname):
                    drifts.append((f"field::{rec}::{fname}",
                                   f"{label}: {rec} :: {fname}: "
                                   f"{gf.get(fname)} -> {cf.get(fname)}"))
    if check_tags and golden.get('tags') is not None and current.get('tags') is not None:
        gt, ct = golden['tags'], current['tags']
        for tag in sorted(set(gt) | set(ct)):
            if gt.get(tag) != ct.get(tag):
                drifts.append((f"tag::{tag}",
                               f"Text tag definitions changed for {tag}:\n"
                               f"      golden : {gt.get(tag)}\n"
                               f"      current: {ct.get(tag)}"))
    return drifts


def validate(arz_path, text_path=None, golden_path=GOLDEN_DEFAULT):
    golden_path = Path(golden_path)
    print("=" * 72)
    print("OCCULT/HUNTING GOLDEN FREEZE GUARD (A7)")
    print(f"  arz    : {arz_path}")
    print(f"  text   : {text_path if text_path else '(none - tag checks SKIPPED)'}")
    print(f"  golden : {golden_path}")
    if not golden_path.exists():
        print("RESULT: FAIL - golden snapshot missing; generate it with --generate "
              "(a build must never silently run unguarded)")
        return 1
    golden = json.loads(golden_path.read_text(encoding='utf-8'))
    current = capture(arz_path, text_path)
    overrides = golden.get('owner_approved_overrides', {}) or {}
    drifts = _diff(golden, current, check_tags=bool(text_path))
    hard = [(k, m) for k, m in drifts if k not in overrides]
    waived = [(k, m) for k, m in drifts if k in overrides]
    for k, m in waived:
        print(f"  WAIVED drift (owner-approved '{overrides[k]}'): {k}")
    if hard:
        for k, m in hard:
            print(f"  GOLDEN DRIFT [{k}]\n      {m}")
        print(f"RESULT: FAIL - {len(hard)} unapproved drift(s) in the hand-tuned "
              f"Occult/Hunting state. Revert them, or get Will's sign-off and add "
              f"each key to owner_approved_overrides in {golden_path.name}.")
        return 1
    print(f"RESULT: PASS - Occult/Hunting golden state intact "
          f"({len(waived)} waived, {len(drifts) - len(hard) - len(waived)} other)")
    return 0


def main(argv):
    args = [a for a in argv[1:]]
    if not args:
        print(__doc__)
        return 2
    out = GOLDEN_DEFAULT
    golden = GOLDEN_DEFAULT
    if '--out' in args:
        i = args.index('--out')
        out = Path(args[i + 1]); del args[i:i + 2]
    if '--golden' in args:
        i = args.index('--golden')
        golden = Path(args[i + 1]); del args[i:i + 2]
    if args and args[0] == '--generate':
        if len(args) < 3:
            print("usage: --generate <arz> <text.arc> [--out <json>]")
            return 2
        snap = capture(args[1], args[2])
        out.write_text(json.dumps(snap, indent=2, sort_keys=True) + '\n',
                       encoding='utf-8')
        n_rec = sum(len(m['records']) for m in snap['masteries'].values())
        n_tag = len(snap['tags'] or {})
        print(f"golden written: {out} ({n_rec} records, {n_tag} tags)")
        return 0
    arz = args[0]
    text = args[1] if len(args) > 1 else None
    return validate(arz, text, golden)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
