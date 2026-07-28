r"""audit_soul_identity - b97: the SOUL-vs-MONSTER identity table (Will 2026-07-27).

WILL'S REPORT (verbatim):
    "we also need to do an audit of the hero monsters vs the souls that they drop
     since i can see that some of the heroes are dropping the wrong souls or souls
     for other boss monsters i think"

Emits the full audit table over ANY built/deployed .arz: every creature record with
a LIVE soul drop -> the soul family it drops -> that soul's display tag -> the
monster's own display tag -> a verdict.

VERDICTS
  MATCH            the soul's identity IS the monster's identity.
  MISMATCH         the monster drops a soul whose identity belongs to a DIFFERENT
                   named creature that ALSO drops it live. The bug class.
  SHARED-ARCHETYPE the soul is named for a COMMON monster type (Satyr Fire Magi,
                   Sandwraith, ...) and no carrier owns the name; the family's
                   named uniques are the only way to obtain it. By design.
  NAME-DRIFT       sole live carrier whose display name simply differs from its
                   soul's ("Wither Mound" <-> Speckled Jim Soul). Nobody's identity
                   is stolen; renaming is a TEXT decision, not a data bug.

The MISMATCH verdict is computed by the SHIPPED GATE itself
(tools/patches/soul_identity.find_identity_thieves) - this tool and the build gate
can never disagree about what counts as an identity thief.

USAGE
  py tools/audit_soul_identity.py <arz> [sv098i_Text_EN.arc] [mod_Text.arc]
                                        [--markdown <out.md>]
Defaults resolve SV 0.98i's Text_EN.arc from ./upstream and, when a mod Text.arc is
given, layers the mod-authored tags on top.
"""
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arc_patcher import ArcArchive
from arz_patcher import ArzDatabase


def load_arc_tags(path, into=None):
    tags = {} if into is None else into
    p = Path(path)
    if not p.is_file():
        print(f"  WARNING: text archive not found: {p}", file=sys.stderr)
        return tags
    arc = ArcArchive.from_file(p)
    for entry in arc.entries:
        nm = getattr(entry, 'name', '')
        if not nm.lower().endswith('.txt'):
            continue
        txt = arc.get_text(nm)
        if not txt:
            continue
        for line in txt.splitlines():
            line = line.strip()
            if not line or line.startswith('//') or '=' not in line:
                continue
            key, _, val = line.partition('=')
            tags[key.strip().lower()] = val.strip()
    return tags


def build_table(arz_path, tagmap):
    """Returns (rows, families). One row per (creature record, soul family)."""
    # The gate module is the single source of truth for identity matching; feed it
    # the same tag table via the module-global the build normally sets.
    import apply_svc_patches as asp
    asp._SV098I_NAME_TAGS = dict(tagmap)
    from patches import soul_identity as si

    db = ArzDatabase.from_arz(Path(arz_path))
    thieves, families = si.find_identity_thieves(db, {})

    def text_of(key):
        return tagmap.get(str(key or '').lower(), '')

    # soul family -> the set of live carriers, already computed by the gate
    rows = []
    for fam, e in families.items():
        owned = bool(e['matched'])
        for bucket in ('matched', 'unmatched'):
            for rec, disp in e[bucket]:
                if bucket == 'matched':
                    verdict = 'MATCH'
                elif rec in thieves:
                    verdict = 'MISMATCH'
                elif len(e['unmatched']) == 1 and not owned:
                    verdict = 'NAME-DRIFT'
                else:
                    verdict = 'SHARED-ARCHETYPE'
                try:
                    chance = float(si._scalar(
                        db.get_field_value(rec, 'chanceToEquipFinger2')) or 0.0)
                except (TypeError, ValueError):
                    chance = 0.0
                rows.append({
                    'record': rec,
                    'monster': disp or '(unresolved tag)',
                    'cls': str(si._scalar(
                        db.get_field_value(rec, 'monsterClassification')) or ''),
                    'chance': chance,
                    'family': fam,
                    'soul': e['display'] or f'({fam})',
                    'verdict': verdict,
                    'owner': (e['matched'][0][1] if e['matched'] else ''),
                })
    rows.sort(key=lambda r: (r['verdict'] != 'MISMATCH', r['soul'].lower(),
                             r['record'].lower()))
    return rows, families, thieves


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    arz = argv[1]
    rest = [a for a in argv[2:] if not a.startswith('--')]
    md_out = None
    if '--markdown' in argv:
        md_out = argv[argv.index('--markdown') + 1]

    repo = Path(__file__).resolve().parent.parent
    sv_text = Path(rest[0]) if rest else (
        repo / 'upstream' / 'soulvizier_098i' / 'Resources' / 'Text_EN.arc')
    tagmap = load_arc_tags(sv_text)
    if len(rest) > 1:
        load_arc_tags(rest[1], tagmap)
    print(f"display-name tags loaded: {len(tagmap)}", file=sys.stderr)

    rows, families, thieves = build_table(arz, tagmap)

    counts = defaultdict(int)
    for r in rows:
        counts[r['verdict']] += 1
    print(f"\nAUDIT SCOPE  arz={arz}")
    print(f"  live soul-dropping creature records : "
          f"{len({r['record'] for r in rows})}")
    print(f"  distinct soul families dropped      : {len(families)}")
    print(f"  distinct monster display names      : "
          f"{len({r['monster'] for r in rows})}")
    for v in ('MATCH', 'MISMATCH', 'SHARED-ARCHETYPE', 'NAME-DRIFT'):
        print(f"  {v:18s}: {counts[v]}")

    if md_out:
        lines = ["| Verdict | Monster (display) | Cls | Drop% | Soul dropped (display) "
                 "| Rightful owner | Record |",
                 "|---|---|---|---|---|---|---|"]
        for r in rows:
            lines.append(
                f"| {r['verdict']} | {r['monster']} | {r['cls']} | {r['chance']:g} "
                f"| {r['soul']} | {r['owner'] or '-'} | `{r['record']}` |")
        Path(md_out).write_text("\n".join(lines) + "\n", encoding='utf-8')
        print(f"\nmarkdown table -> {md_out} ({len(rows)} rows)")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
