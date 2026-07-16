"""Phase 1: SVAERA goodies audit - name-set diff across 4 databases.

SVAERA = reference SVAERA_customquest.arz (Steam workshop live install)
OURS   = work/SoulvizierClassic/Database/SoulvizierClassic.arz (overlay)
SV098  = upstream soulvizier 0.98i database.arz
BASE   = TQAE stock database.arz

Effective-ours  = OURS names UNION BASE names
Effective-svaera= SVAERA names UNION BASE names

We want records SVAERA overlays (SVAERA arz names) that are ABSENT from our
effective DB. Split by whether SV098 also has them (SV-content-we-dropped) vs
SVAERA-authored-new (neither base nor SV098).
"""
import sys
import json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, r"C:\Users\willi\repos\tqit_soulvizier_classic\tools")
from arz_patcher import ArzDatabase

SVAERA = Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\475150\2076433374\SVAERA_customquest\Database\SVAERA_customquest.arz")
OURS   = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz")
SV098  = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Database\database.arz")
BASE   = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Database\database.arz")

OUTDIR = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\scratch_audit\svaera_goodies")


def norm(s):
    return str(s).replace('/', '\\').lower().strip()


def load_names(path, label):
    print(f"Loading {label}: {path.name}")
    db = ArzDatabase.from_arz(path)
    names = {norm(n): n for n in db.record_names()}
    print(f"  {label}: {len(names)} records")
    return db, names


def family(nname):
    """Bucket a normalized record name into a coarse family."""
    p = nname
    if not p.startswith('records\\'):
        return 'other:' + p.split('\\')[0]
    parts = p.split('\\')
    # records\<a>\<b>\...
    a = parts[1] if len(parts) > 1 else '?'
    b = parts[2] if len(parts) > 2 else '?'
    c = parts[3] if len(parts) > 3 else '?'
    if a == 'item':
        return f'item\\{b}'
    if a == 'creature' or a == 'creatures':
        return f'creature\\{b}'
    if a == 'skills':
        return f'skills\\{b}'
    if a in ('xpack', 'xpack2', 'xpack3', 'xpack4'):
        return f'{a}\\{b}\\{c}'
    if a == 'controllers':
        return f'controllers\\{b}'
    return f'{a}\\{b}'


def main():
    _, sv_names = load_names(SVAERA, 'SVAERA')
    _, our_names = load_names(OURS, 'OURS')
    _, sv098_names = load_names(SV098, 'SV098')
    _, base_names = load_names(BASE, 'BASE')

    sv = set(sv_names)
    our = set(our_names)
    sv098 = set(sv098_names)
    base = set(base_names)

    eff_ours = our | base

    # SVAERA overlay records absent from our effective DB
    absent = sv - eff_ours
    # split: SVAERA-authored-new (not in SV098 either) vs SV-content-we-dropped
    authored_new = absent - sv098          # SVAERA invented, we lack, SV098 lacks
    sv_dropped = absent & sv098            # existed in SV098, SVAERA has, we dropped

    # Also: SVAERA arz overlay total that is NOT base (their authored/override footprint)
    sv_overlay_nonbase = sv - base

    print("\n==== NAME-SET SUMMARY ====")
    print(f"SVAERA records total          : {len(sv)}")
    print(f"OURS records total            : {len(our)}")
    print(f"SV098 records total           : {len(sv098)}")
    print(f"BASE records total            : {len(base)}")
    print(f"Effective-ours (OURS|BASE)    : {len(eff_ours)}")
    print(f"SVAERA overlay non-base        : {len(sv_overlay_nonbase)}")
    print(f"SVAERA absent-from-ours (all)  : {len(absent)}")
    print(f"  - SVAERA-authored-new (no SV098): {len(authored_new)}")
    print(f"  - SV098-content-we-dropped      : {len(sv_dropped)}")

    def bucketize(nameset):
        b = defaultdict(list)
        for n in nameset:
            b[family(n)].append(n)
        return b

    absent_b = bucketize(absent)
    authored_b = bucketize(authored_new)
    dropped_b = bucketize(sv_dropped)

    def dump_buckets(bk, title, fh):
        fh.write(f"\n### {title} (total {sum(len(v) for v in bk.values())})\n")
        for fam in sorted(bk, key=lambda k: -len(bk[k])):
            fh.write(f"  {len(bk[fam]):5d}  {fam}\n")

    with open(OUTDIR / 'p1_buckets.txt', 'w', encoding='utf-8') as fh:
        fh.write("SVAERA GOODIES AUDIT - Phase 1 name-set buckets\n")
        fh.write(f"SVAERA={len(sv)} OURS={len(our)} SV098={len(sv098)} BASE={len(base)} EFF_OURS={len(eff_ours)}\n")
        fh.write(f"absent={len(absent)} authored_new={len(authored_new)} sv_dropped={len(sv_dropped)}\n")
        dump_buckets(absent_b, "ABSENT-FROM-OURS (all SVAERA overlay records we lack)", fh)
        dump_buckets(authored_b, "SVAERA-AUTHORED-NEW (absent, and not in SV098)", fh)
        dump_buckets(dropped_b, "SV098-CONTENT-WE-DROPPED (absent, but SV098 had it)", fh)

    # Persist name lists for phase 2/3 (use ORIGINAL casing from SVAERA)
    out = {
        'counts': {
            'svaera': len(sv), 'ours': len(our), 'sv098': len(sv098), 'base': len(base),
            'eff_ours': len(eff_ours), 'sv_overlay_nonbase': len(sv_overlay_nonbase),
            'absent': len(absent), 'authored_new': len(authored_new), 'sv_dropped': len(sv_dropped),
        },
        'authored_new': sorted(sv_names[n] for n in authored_new),
        'sv_dropped': sorted(sv_names[n] for n in sv_dropped),
        'absent_buckets': {k: sorted(sv_names[n] for n in v) for k, v in absent_b.items()},
    }
    with open(OUTDIR / 'p1_names.json', 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1)

    print(f"\nWrote {OUTDIR / 'p1_buckets.txt'} and p1_names.json")


if __name__ == '__main__':
    main()
