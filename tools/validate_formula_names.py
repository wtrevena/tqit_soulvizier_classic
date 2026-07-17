"""Build-time validator (B80): every OBTAINABLE DRX supra craft formula's
rendered display name must reference its crafted result's own rendered name,
per the mod's "<Mythic|Arcane> Formula - <ResultName>" convention.

Root problem this guards against: a formula shell's `description` field can be
left pointed at (or accidentally repointed to) another formula's donor tag -
the exact Galefury/Crystalline-Mask bug Will reported 2026-07-16 (b80). The
formula still crafts the RIGHT result (artifactName is correct), but the
in-game recipe list shows the WRONG name for it. A structural (no-Text)
version of this gate also runs at DB-build time (tools/patches/formula_names.py
verify()); THIS validator is the full text-resolved sweep, run against the
built .arz + Text.arc, so it also catches a hand-typo'd BRAND-NEW tag (no
sharing involved) that the structural gate cannot see.

Convention (derived empirically from the 41 correctly-named formulas; see
docs/reports/b80_formula_names.md): the formula's description tag renders as
"<optional ^X color><Mythic|Arcane> Formula - <ResultName>" where <ResultName>
matches the crafted result's own itemNameTag text with any leading ^X color
code stripped from both sides before comparing (two self-consistent color/
prefix-word sub-conventions coexist: the original 25 recipes\\ formulas use
"^rMythic Formula - " matching a "^r"-prefixed result name; the b66-added
zrecipes\\ formulas use "Mythic Formula - " / "Arcane Formula - " (thrown
family) with NO leading color on either side - both are legitimate, this gate
only requires the NAME TEXT itself to match, not the color/prefix-word style).

Some obtainable results (records\\drxitem\\supra\\artifact_plus2.dbr,
artifact_mortoksskull.dbr - ItemArtifactSupra class) carry no itemNameTag at
all (no fixed display name; the formula name is their only identity). These
are reported as N/A, not failures.

Usage:
  py tools/validate_formula_names.py <final.arz> <final_text.arc>

Exit codes:
  0 = every obtainable formula's name matches its result (or is waived/N-A)
  1 = one or more mismatches (details printed)
  2 = usage / input error
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase
from arc_patcher import ArcArchive

SUPRA_TABLE = r'records\xpack\item\loottables\arcaneformulae\supra.dbr'
SUPRA_SPECIAL = r'records\xpack\item\loottables\arcaneformulae\supra_special.dbr'

# (formula record path, lowercased) -> reason. Populate ONLY for a genuinely
# SV/design-intended name that deliberately does not match its result's own
# name (checked against SV 0.98i originals first - see report). Empty today:
# the one prior mismatch (Galefury/Crystalline Mask) was a bug, not a design
# choice, and is fixed by tools/patches/formula_names.py.
NAME_TEXT_WAIVERS = {}

# Results with no fixed itemNameTag (procedural ItemArtifactSupra items whose
# only identity is the formula name) - reported as N/A, never a failure.
NO_FIXED_NAME_RESULTS = {
    r'records\drxitem\supra\artifact_plus2.dbr',
    r'records\drxitem\supra\artifact_mortoksskull.dbr',
}


def _norm(p):
    return p.replace('/', '\\').lower()


def _strip_color(s):
    if s and len(s) >= 2 and s[0] == '^':
        return s[2:]
    return s


def _field(db, rec, name):
    if rec is None:
        return None
    fields = db.get_fields(rec)
    if not fields:
        return None
    for key, tf in fields.items():
        if key.split('###')[0] == name:
            return tf.values[0] if tf.values else None
    return None


def _rec_lookup(db):
    return {_norm(n): n for n in db.record_names()}


def _loot_formula_refs(db, table_rec):
    fields = db.get_fields(table_rec)
    if not fields:
        return []
    out = []
    for key, tf in fields.items():
        if key.split('###')[0].startswith('lootName') and tf.values:
            v = tf.values[0]
            if isinstance(v, str) and v.strip():
                out.append(v)
    return out


def load_text_tagmap(text_arc_path):
    arc = ArcArchive.from_file(Path(text_arc_path))
    text = arc.get_text('modstrings.txt')
    if text is None:
        for entry in arc.entries:
            if getattr(entry, 'name', '').lower().endswith('.txt'):
                text = arc.get_text(entry.name)
                if text is not None:
                    break
    tags = {}
    if text is None:
        return tags
    for line in text.split('\n'):
        line = line.strip('\r').strip()
        if not line or line.startswith('//') or '=' not in line:
            continue
        k, _, v = line.partition('=')
        tags[k.strip()] = v
    return tags


def check(arz_path, text_arc_path):
    db = ArzDatabase.from_arz(Path(arz_path))
    tagmap = load_text_tagmap(text_arc_path)
    lookup = _rec_lookup(db)

    def find(name):
        return lookup.get(_norm(name)) if name else None

    supra = find(SUPRA_TABLE)
    supra_special = find(SUPRA_SPECIAL)
    if not supra and not supra_special:
        print(f"  ERROR: neither {SUPRA_TABLE} nor {SUPRA_SPECIAL} found in {arz_path}")
        return 2

    wired = set()
    for t in (supra, supra_special):
        if t:
            for r in _loot_formula_refs(db, t):
                wired.add(_norm(r))

    mismatches = []
    na = []
    checked = 0
    for ref in sorted(wired):
        rec = find(ref)
        if rec is None:
            mismatches.append((ref, "record missing from arz", None, None))
            continue
        if _field(db, rec, 'Class') != 'ItemArtifactFormula':
            continue
        artifact_name = _field(db, rec, 'artifactName')
        if artifact_name and _norm(artifact_name) in {_norm(p) for p in NO_FIXED_NAME_RESULTS}:
            na.append(rec)
            continue

        desc_tag = _field(db, rec, 'description')
        formula_text = tagmap.get(desc_tag) if desc_tag else None
        result_rec = find(artifact_name) if artifact_name else None
        result_name_tag = _field(db, result_rec, 'itemNameTag') if result_rec else None
        result_text = tagmap.get(result_name_tag) if result_name_tag else None

        if not formula_text or not result_text:
            mismatches.append((rec, "description or result name tag does not "
                                     "resolve in Text.arc", desc_tag, result_name_tag))
            continue

        formula_suffix = None
        if ' - ' in formula_text:
            _, _, formula_suffix = formula_text.partition(' - ')
        formula_clean = _strip_color(formula_suffix) if formula_suffix else None
        result_clean = _strip_color(result_text)
        checked += 1

        if formula_clean != result_clean:
            if _norm(rec) in {_norm(p) for p in NAME_TEXT_WAIVERS}:
                continue
            mismatches.append((rec, f"formula says {formula_text!r} but result "
                                     f"({artifact_name}) is named {result_text!r}",
                                desc_tag, result_name_tag))

    print(f"  Checked {checked} obtainable formula(s) ({len(wired)} wired total, "
          f"{len(na)} N/A - no fixed result name)")
    if mismatches:
        print(f"\n  FORMULA-NAME MISMATCHES ({len(mismatches)}):")
        for rec, reason, desc_tag, result_tag in mismatches:
            print(f"    {rec}")
            print(f"      {reason}")
        return 1
    print("  All obtainable formula names match their results. PASS")
    return 0


def main():
    if len(sys.argv) < 3:
        print("Usage: validate_formula_names.py <final.arz> <final_text.arc>")
        return 2
    arz_path = Path(sys.argv[1])
    text_arc_path = Path(sys.argv[2])
    if not arz_path.exists():
        print(f"ERROR: arz not found: {arz_path}")
        return 2
    if not text_arc_path.exists():
        print(f"ERROR: Text.arc not found: {text_arc_path}")
        return 2
    return check(arz_path, text_arc_path)


if __name__ == '__main__':
    sys.exit(main())
