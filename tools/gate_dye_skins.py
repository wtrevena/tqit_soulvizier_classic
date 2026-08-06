r"""GATE: every OBTAINABLE costume dye must reskin the PC to a texture that
resolves in the SHIPPED arc set. If it does not, the engine paints the player
flat GREY (the Flozer44 PR-2 report).

WHAT IT CHECKS
--------------
For the given built `.arz`:
  * a dye is a record with Class == OneShot_Dye;
  * a dye is OBTAINABLE iff a LootItemTable lists it in a `lootName*` slot
    (proven complete: dyes are referenced by nothing else, and the world map
    places no dye item or dye loot-table directly - PR-2 map scan);
  * a dye greys a player of gender G iff its `{male,female}Texture` for gender G
    does not resolve. Resolution follows the TQ rule: the first path component is
    the arc name, so `Creatures\PC\...tex` is served by a `Creatures.arc` in the
    mod Resources OR the base game.

PASS  = zero OBTAINABLE dye references a missing skin texture.
Orphan dyes (in no loot table -> unobtainable) that reference a missing skin are
reported as NOTES, never failures: a player can never receive them.

Like the champion_mesh asset gate, if the Creatures arcs cannot be reached the
gate reports UNAVAILABLE (fail only under SVC_REQUIRE_GATES=1) rather than a false
pass - an anim/skin gate that cannot see its arcs must never green silently.

Usage:
  py tools/gate_dye_skins.py <built.arz> [--game DIR] [--mod-resources DIR]
  py tools/gate_dye_skins.py <built.arz> --negtest   # planted-failure self-test
"""
import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase
from arc_patcher import ArcArchive


def _norm(s):
    return s.replace('\\', '/').lower()


def _creatures_arcs(game_dir, mod_resources):
    """Every Creatures.arc that ships/loads: mod Resources first (shadow), then base."""
    out = []
    seen = set()
    dirs = []
    if mod_resources:
        dirs.append(Path(mod_resources))
    env = os.environ.get('SVC_MOD_RESOURCES')
    if env:
        dirs.append(Path(env))
    for pat in ('work/*/Resources', 'local/*/Resources'):
        dirs.extend(sorted(Path('.').glob(pat)))
    dirs.append(Path(game_dir) / 'Resources')
    for d in dirs:
        p = d / 'Creatures.arc'
        rp = str(p).lower()
        if rp in seen:
            continue
        seen.add(rp)
        if p.is_file():
            out.append(p)
    return out


def _skin_universe(game_dir, mod_resources):
    rels = set()
    arcs = _creatures_arcs(game_dir, mod_resources)
    for a in arcs:
        arc = ArcArchive.from_file(a)
        for e in arc.entries:
            if e.entry_type == 3 and e.name:
                rels.add(_norm(e.name))
    return rels, arcs


def _rel_of(texref):
    p = _norm(texref or '')
    a, _, rel = p.partition('/')
    return rel if a == 'creatures' else None


def check(arz_path, game_dir, mod_resources, extra_db=None):
    db = extra_db if extra_db is not None else ArzDatabase.from_arz(Path(arz_path))
    names = db.record_names()
    dyes = [n for n in names if str(db.get_field_value(n, 'Class')) == 'OneShot_Dye']
    dyes_l = set(_norm(n) for n in dyes)

    obtainable = set()
    for n in names:
        if 'LootItemTable' not in str(db.get_field_value(n, 'Class')):
            continue
        f = db.get_fields(n)
        for k, tf in f.items():
            if not k.split('###')[0].startswith('lootName'):
                continue
            for v in tf.values:
                if isinstance(v, str) and _norm(v) in dyes_l:
                    obtainable.add(_norm(v))

    universe, arcs = _skin_universe(game_dir, mod_resources)
    has_creatures_arc = bool(arcs)

    problems, notes = [], []
    checked = 0
    for n in dyes:
        obt = _norm(n) in obtainable
        for fld in ('maleTexture', 'femaleTexture'):
            v = db.get_field_value(n, fld)
            v = v[0] if isinstance(v, list) else v
            rel = _rel_of(v)
            if rel is None:
                continue
            checked += 1
            if rel not in universe:
                msg = f'{n} :: {fld} -> {v} does NOT resolve in any shipped Creatures.arc'
                if obt:
                    problems.append('OBTAINABLE ' + msg)
                else:
                    notes.append('orphan(unobtainable) ' + msg)
    return {
        'dyes': len(dyes), 'obtainable': len(obtainable), 'checked': checked,
        'arcs': [str(a) for a in arcs], 'has_creatures_arc': has_creatures_arc,
        'problems': problems, 'notes': notes,
    }


def _default_game():
    return os.environ.get('SVC_TQAE_DIR',
                          r'C:\Program Files (x86)\Steam\steamapps\common'
                          r'\Titan Quest Anniversary Edition')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('arz')
    ap.add_argument('--game', default=_default_game())
    ap.add_argument('--mod-resources', default=None)
    ap.add_argument('--negtest', action='store_true',
                    help='plant a broken obtainable dye and confirm it is caught')
    a = ap.parse_args()

    require = os.environ.get('SVC_REQUIRE_GATES') == '1'
    db = ArzDatabase.from_arz(Path(a.arz))

    if a.negtest:
        # find an obtainable dye and break its maleTexture, expect a problem
        r0 = check(a.arz, a.game, a.mod_resources, extra_db=db)
        if not r0['has_creatures_arc']:
            print('NEGTEST SKIPPED: no Creatures.arc reachable to resolve against')
            return 0
        names = db.record_names()
        dyes_l = {r.lower() for r in names
                  if str(db.get_field_value(r, 'Class')) == 'OneShot_Dye'}
        victim = None
        for n in names:
            if 'LootItemTable' not in str(db.get_field_value(n, 'Class')):
                continue
            f = db.get_fields(n)
            for k, tf in f.items():
                if not k.split('###')[0].startswith('lootName'):
                    continue
                for v in tf.values:
                    if isinstance(v, str) and v.lower() in dyes_l:
                        victim = v
                        break
                if victim:
                    break
            if victim:
                break
        if not victim:
            print('NEGTEST SKIPPED: no obtainable dye found')
            return 0
        db.set_field(victim, 'maleTexture',
                     'Creatures\\PC\\Male\\malepc01_DOES_NOT_EXIST_negtest.tex')
        r1 = check(a.arz, a.game, a.mod_resources, extra_db=db)
        caught = any('DOES_NOT_EXIST_negtest' in p for p in r1['problems'])
        print(f'NEGTEST: planted broken obtainable dye {victim}')
        print(f'  caught by gate: {caught}')
        return 0 if caught else 1

    r = check(a.arz, a.game, a.mod_resources, extra_db=db)
    print(f'dye_skins gate: {r["dyes"]} dyes, {r["obtainable"]} obtainable, '
          f'{r["checked"]} texture refs checked')
    for aarc in r['arcs']:
        print(f'  Creatures.arc: {aarc}')
    if not r['has_creatures_arc']:
        msg = ('dye_skins gate DID NOT RUN - no Creatures.arc reachable under the mod '
               'Resources or game dir; cannot resolve PC skin textures. '
               'Build into the work/ layout or pass --mod-resources.')
        if require:
            print('FAIL: ' + msg)
            return 1
        print('WARNING (UNAVAILABLE): ' + msg)
        return 0
    if r['notes']:
        print(f'  NOTE: {len(r["notes"])} orphan (unobtainable) dye(s) reference a '
              f'missing skin - harmless, a player can never receive them:')
        for m in r['notes'][:6]:
            print('     - ' + m)
        if len(r['notes']) > 6:
            print(f'     ... (+{len(r["notes"]) - 6} more)')
    if r['problems']:
        print(f'FAIL: {len(r["problems"])} OBTAINABLE dye(s) reference a missing skin '
              f'(would grey the PC):')
        for p in r['problems'][:20]:
            print('     - ' + p)
        return 1
    print('PASS: every obtainable dye resolves to a shipped skin texture '
          '(zero grey-dye paths).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
