r"""audit_soul_identity - b97: the SOUL-vs-MONSTER identity table (Will 2026-07-27).

WILL'S REPORT (verbatim):
    "we also need to do an audit of the hero monsters vs the souls that they drop
     since i can see that some of the heroes are dropping the wrong souls or souls
     for other boss monsters i think"

Emits the full audit table over ANY built/deployed .arz: every record with a LIVE
soul drop -> the soul it drops -> that soul's display name -> the monster's own
display name -> a verdict.

SCOPE (round 2). ROSTER-WIDE: every record path, not just \creature(s)\. Round 1
scoped both this tool and the shipped gate to paths containing \creature(s)\,
which silently skipped 97 live carriers - all of records\drxcreatures\ (shipping
DRX/Urder content), records\test\, records\item\equipmentring\soul\test\ and the
pet trees - and with them a REAL mismatch ('Akara' dropping the Kallixenia soul).
Only pets and quest spawn proxies are excluded, and only because they cannot hand
the player anything; see soul_identity._is_soul_carrier for the proof that
excluding them fails safe.

VERDICTS
  MATCH             the soul's identity IS the monster's identity.
  MISMATCH          the monster drops a soul whose identity belongs to a DIFFERENT
                    named creature that ALSO drops it live. The bug class.
  ARCHETYPE-SHARED  no live carrier owns the soul's name, AND a record that DOES
                    own it exists in the roster carrying the same soul but gated
                    dead (rank-gated Common/Champion, or an unbound/bound variant
                    of the same boss). The soul is named for a monster TYPE or a
                    prior form; the named uniques are the only live source. By
                    design - zeroing them would make the soul unobtainable.
  NAME-DRIFT        no live carrier owns the soul's name and NO record anywhere
                    carries that name: the soul is simply its carrier's soul under
                    a different spelling ("Wither Mound" <-> Speckled Jim Soul).
                    Renaming is a TEXT decision, not a data bug.

The MATCH/MISMATCH split is computed by the SHIPPED GATE itself
(tools/patches/soul_identity.find_identity_thieves) - this tool and the build gate
can never disagree about what counts as an identity thief. ARCHETYPE-SHARED vs
NAME-DRIFT is decided from the DATA (does an owner record exist?), never from a
row count: round 1 split them on "exactly 1 unmatched carrier" and consequently
filed three archetype rows (Cynisca, Corpse Wake, Meritamen) as name drift.

USAGE
  py tools/audit_soul_identity.py <arz> [sv098i_Text_EN.arc] [mod_Text.arc]
                                        [--markdown <out.md>]
Both text archives default to resolved locations (SV 0.98i via
tools/check_build_inputs.py, the mod Text.arc from the deployed CustomMaps tree),
so the tool runs in a fresh worktree with no upstream/ cache staged by hand.
Pass paths explicitly to pin them.
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


def resolve_sv_text():
    r"""SV 0.98i Text_EN.arc, via the shared build-input resolver.

    upstream/ is gitignored, so a fresh `git worktree add` hands the lane an EMPTY
    cache; round 1 hard-defaulted to <repo>/upstream/... and simply did not run
    there. check_build_inputs knows the $SVC_SV098I_TEXT_ARC env var, the main
    checkout's cache and the installed locations.
    """
    repo = Path(__file__).resolve().parent.parent
    local = repo / 'upstream' / 'soulvizier_098i' / 'Resources' / 'Text_EN.arc'
    if local.is_file():
        return local
    try:
        import check_build_inputs as cbi
        for fn in ('resolve', 'resolve_input', 'resolve_one'):
            f = getattr(cbi, fn, None)
            if f is None:
                continue
            try:
                got = f('sv098i_text_arc')
            except Exception:
                continue
            p = Path(getattr(got, 'path', got) or '')
            if p.is_file():
                return p
    except Exception as exc:  # noqa: BLE001 - advisory
        print(f"  note: check_build_inputs resolution unavailable ({exc})",
              file=sys.stderr)
    return local


def resolve_mod_text():
    r"""The mod's own Text.arc - needed for every mod-authored soul/monster name
    (tagSVCSoul*, tagSoulSVC*). Without it those carriers are skipped as
    unjudgeable and the table under-reports."""
    repo = Path(__file__).resolve().parent.parent
    for cand in (repo / 'work' / 'SoulvizierClassic' / 'Resources' / 'Text.arc',
                 Path.home() / 'OneDrive' / 'Documents' / 'My Games'
                 / 'Titan Quest - Immortal Throne' / 'CustomMaps'
                 / 'SoulvizierClassicDEV' / 'Resources' / 'Text.arc',
                 Path.home() / 'OneDrive' / 'Documents' / 'My Games'
                 / 'Titan Quest - Immortal Throne' / 'CustomMaps'
                 / 'SoulvizierClassic' / 'Resources' / 'Text.arc'):
        if cand.is_file():
            return cand
    return None


def build_table(arz_path, tagmap):
    """Returns (rows, groups, thieves). One row per (record, soul name)."""
    # The gate module is the single source of truth for scope + identity matching;
    # feed it the same tag table via the module-global the build normally sets.
    import apply_svc_patches as asp
    asp._SV098I_NAME_TAGS = dict(tagmap)
    from patches import soul_identity as si

    db = ArzDatabase.from_arz(Path(arz_path))
    thieves, groups = si.find_identity_thieves(db, {})

    def text_of(key):
        return tagmap.get(str(key or '').lower(), '')

    # ── every record that references a soul AT ALL (live or gated dead), so an
    # unowned soul name can be told apart from a soul whose owner is merely gated.
    soul_display = si.soul_display_map(db, tagmap)
    all_refs = []
    for name in db.record_names():
        refs = si._soul_refs(db, name)
        if not refs:
            continue
        all_refs.append((name, text_of(si._scalar(
            db.get_field_value(name, 'description'))), refs))

    def gated_owner(entry):
        """A record that owns this soul's NAME and carries the same soul item,
        but is not live. Presence of one = ARCHETYPE-SHARED, absence = NAME-DRIFT."""
        items = {r.replace('/', '\\').lower() for r in entry['souls']}
        best = []
        for rec, disp, refs in all_refs:
            if not disp or si._chance_of(db, rec) > 0:
                continue
            if not any(r.replace('/', '\\').lower() in items for r in refs):
                continue
            if si.identity_match(disp, entry['display']):
                best.append((rec, disp))
        return best

    rows = []
    for _key, e in groups.items():
        owned = bool(e['matched'])
        gated = [] if owned else gated_owner(e)
        for bucket in ('matched', 'unmatched'):
            for rec, disp in e[bucket]:
                if bucket == 'matched':
                    verdict = 'MATCH'
                elif rec in thieves:
                    verdict = 'MISMATCH'
                elif gated:
                    verdict = 'ARCHETYPE-SHARED'
                else:
                    verdict = 'NAME-DRIFT'
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
                    'family': ' + '.join(sorted(e['families'])),
                    'soul': si._strip_color(e['display']) or '(unnamed)',
                    'verdict': verdict,
                    'owner': (e['matched'][0][1] if e['matched']
                              else (gated[0][1] + ' [gated]' if gated else '')),
                })
    rows.sort(key=lambda r: (r['verdict'] != 'MISMATCH', r['soul'].lower(),
                             r['record'].lower()))
    return rows, groups, thieves, si


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    arz = argv[1]
    # NOTE: the flag's VALUE must not fall through into the positional list -
    # round 1 did exactly that, so `--markdown out.md` was also parsed as the SV
    # Text_EN path and the tool died on an assert deep inside ArcArchive.
    md_out = None
    rest, skip = [], False
    for a in argv[2:]:
        if skip:
            skip = False
            continue
        if a == '--markdown':
            skip = True
            md_out = argv[argv.index(a) + 1]
        elif not a.startswith('--'):
            rest.append(a)

    sv_text = Path(rest[0]) if rest else resolve_sv_text()
    tagmap = load_arc_tags(sv_text)
    mod_text = Path(rest[1]) if len(rest) > 1 else resolve_mod_text()
    if mod_text:
        load_arc_tags(mod_text, tagmap)
    print(f"display-name tags loaded: {len(tagmap)}  "
          f"(sv={sv_text}, mod={mod_text})", file=sys.stderr)

    rows, groups, thieves, si = build_table(arz, tagmap)

    counts = defaultdict(int)
    for r in rows:
        counts[r['verdict']] += 1
    cls = defaultdict(int)
    for r in {row['record']: row for row in rows}.values():
        cls[r['cls'] or '(none)'] += 1
    unres = {r for r, _f in getattr(si.find_identity_thieves,
                                    'last_unresolved', [])}
    print(f"\nAUDIT SCOPE  arz={arz}")
    print(f"  live soul-dropping records (roster-wide, pets/proxies out): "
          f"{len({r['record'] for r in rows})}")
    print(f"  distinct soul NAMES dropped         : {len(groups)}")
    print(f"  distinct monster display names      : "
          f"{len({r['monster'] for r in rows})}")
    print(f"  carriers skipped as unjudgeable     : {len(unres)}")
    print(f"  by monsterClassification            : {dict(sorted(cls.items()))}")
    for v in ('MATCH', 'MISMATCH', 'ARCHETYPE-SHARED', 'NAME-DRIFT'):
        print(f"  {v:18s}: {counts[v]}")

    if md_out:
        lines = ["| Verdict | Monster (display) | Cls | Drop% | Soul dropped (display) "
                 "| Rightful owner | Record | Soul item family |",
                 "|---|---|---|---|---|---|---|---|"]
        for r in rows:
            lines.append(
                f"| {r['verdict']} | {r['monster']} | {r['cls']} | {r['chance']:g} "
                f"| {r['soul']} | {r['owner'] or '-'} | `{r['record']}` "
                f"| `{r['family']}` |")
        Path(md_out).write_text("\n".join(lines) + "\n", encoding='utf-8')
        print(f"\nmarkdown table -> {md_out} ({len(rows)} rows)")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
