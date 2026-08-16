r"""R-257 round-2 COLD-ORDER CONTROL - the P0 reproduced, and the fix proved, five ways.

    py tools/debug/r257_cold_order_control.py [--arz <built.arz>] [--root <checkout>]

WHAT WENT WRONG (round 1, found by the vet, reproduced end-to-end). `enslaver_shroud`
put the Enslaver family on a MOD-AUTHORED mesh that ships in exactly one archive, the
mod's own `Resources\Creatures.arc` - and round 1 staged that archive AFTER the
database build. Three fail-loud gates inside the build read it
(`enslaver_shroud` M2, `validate_render_chain` A9, `champion_mesh.verify`), so the
cold build died at the first one. Worse, `bootstrap_working_mod.ps1` caught the
non-zero exit and quietly copied the RAW upstream SV 0.98i database over the mod
database, then carried on into Text/Quests/deploy.

Round 1 also asked the wrong ADDRESS: the rig arm demanded the asset in every
`mesh_assets.mod_resource_dirs()` hit - a SEARCH PATH including `local/*/Resources` -
so a stale scratch tree could red-lock a build whose own shipped archive was perfect.

THE FIVE RUNS

  A  the SHIPPED state (a Creatures.arc with no rig)            -> apply() must ABORT
     The gate must still bite. A fix that made this pass would have hidden the defect.
  B  after the fixed order (the archive staged FIRST)           -> apply() must PASS
  C  B's good anchor while stale archives sit on the glob path  -> must PASS
     Round 1 would have failed here forever.
  D  build_svc_database's own preflight over a stale archive    -> must RESTAGE, then PASS
     THE SHIP LANE DOES NOT RUN THE BOOTSTRAP. `docs/PLAYBOOK.md` drives
     `build_svc_database.py` directly, so a fix living only in the bootstrap would
     have failed the very next ship. This is the run that covers the real path.
  E  the same with SVC_AUTOSTAGE_CREATURES=0                    -> must NOT restage, must FAIL
     The autostage is a convenience, never a way to pass a gate that should red.

Read-only with respect to the checkout: D and E work on temp copies.
"""
import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default=str(ROOT),
                    help='the checkout whose work/ tree stands in for a ship checkout')
    ap.add_argument('--arz', help='a BUILT .arz to run the modules over '
                                  '(default: <root>/work/SoulvizierClassic/Database/'
                                  'SoulvizierClassic.arz)')
    a = ap.parse_args()

    root = Path(a.root).resolve()
    arz = Path(a.arz) if a.arz else \
        root / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'
    ship_res = root / 'work' / 'SoulvizierClassic' / 'Resources'
    if not arz.exists():
        print('CONTROL UNRUNNABLE: no built .arz at %s (pass --arz)' % arz)
        return 2

    tools = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(tools))
    sys.path.insert(0, str(tools / 'patches'))
    os.chdir(str(root))                      # the glob path must be the real one
    os.environ['SVC_REQUIRE_GATES'] = '1'

    import mesh_assets
    from arz_patcher import ArzDatabase
    import enslaver_shroud as es
    import champion_mesh as cm
    import build_svc_database as bsd

    ok = True

    def run(label, anchor, expect):
        nonlocal ok
        mesh_assets.set_shipping_resource_dir(anchor)
        print('\n' + '=' * 78)
        print('%s\n  anchor = %s' % (label, anchor))
        print('=' * 78)
        st, detail = es.rig_asset_state()
        print('  rig_asset_state -> %s\n    %s' % (st, detail[:200]))
        got = 'PASS'
        try:
            db = ArzDatabase.from_arz(arz)
            # registry order: enslaver_shroud (retires the belief channels) runs
            # before champion_mesh (the single writer of `mesh`).
            es.apply(db, {})
            cm.apply(db, {})
        except SystemExit as e:
            got = 'ABORT'
            print('  !!! SystemExit from apply(): %s' % str(e)[:280])
        good = (got == expect)
        print('  --> %s (expected %s)  %s' % (got, expect, 'OK' if good else '<<< WRONG'))
        ok &= good

    run('RUN A  SHIPPED STATE: the mod Creatures.arc as deployed, no rig in it',
        ship_res, 'ABORT')

    tmp = Path(tempfile.mkdtemp(prefix='svc_step0e_'))
    good_res = tmp / 'SoulvizierClassic' / 'Resources'
    good_res.mkdir(parents=True)
    try:
        print('\n--- bootstrap Step 0e, for real (the single writer, the real inputs) ---')
        import build_creatures_dye_skins_arc as bcd
        bcd.stage(good_res / 'Creatures.arc')

        run('RUN B  AFTER THE FIX: the archive was staged BEFORE the build', good_res,
            'PASS')

        dirs = [str(p) for p in mesh_assets.mod_resource_dirs()]
        print('\n--- RUN C environment: what a glob sweep would have asked ---')
        print('  mod_resource_dirs() = %d dir(s): %r' % (len(dirs), dirs))
        print('  of those, holding a Creatures.arc WITHOUT the rig: %r'
              % [d for d in dirs if (Path(d) / 'Creatures.arc').exists()
                 and Path(d).resolve() != good_res.resolve()])
        run('RUN C  the SAME good anchor, with this checkout\'s stale archives still '
            'on the glob path', good_res, 'PASS')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for label, autostage, want_action, want_state in (
            ('RUN D  build_svc_database\'s OWN preflight over a stale archive '
             '(autostage ON, the default) - THE SHIP LANE\'S PATH', '1',
             'RESTAGED', 'PASS'),
            ('RUN E  the same with SVC_AUTOSTAGE_CREATURES=0 - a convenience must '
             'never become a way to pass a gate that should red', '0',
             'LEFT ALONE', 'FAIL')):
        tmp = Path(tempfile.mkdtemp(prefix='svc_preflight_'))
        res = tmp / 'SoulvizierClassic' / 'Resources'
        res.mkdir(parents=True)
        shutil.copy2(ship_res / 'Creatures.arc', res / 'Creatures.arc')
        before = (res / 'Creatures.arc').stat().st_size
        os.environ['SVC_AUTOSTAGE_CREATURES'] = autostage
        mesh_assets.set_shipping_resource_dir(res)
        print('\n' + '=' * 78)
        print('%s\n  seeded with this checkout\'s staged archive (%d B)' % (label, before))
        print('=' * 78)
        try:
            bsd._preflight_mod_creatures_arc(res)
        except SystemExit as e:
            print('  !!! SystemExit from the preflight: %s' % str(e)[:220])
        after = (res / 'Creatures.arc').stat().st_size
        action = 'RESTAGED' if after != before else 'LEFT ALONE'
        st, _d = es.rig_asset_state()
        good = (st == want_state) and (action == want_action)
        print('  archive %d -> %d B (%s); rig_asset_state -> %s'
              % (before, after, action, st))
        print('  --> %s (expected %s + %s)' % ('OK' if good else '<<< WRONG',
                                               want_action, want_state))
        ok &= good
        os.environ.pop('SVC_AUTOSTAGE_CREATURES', None)
        shutil.rmtree(tmp, ignore_errors=True)

    print('\n' + '=' * 78)
    print('R-257 COLD-ORDER CONTROL: %s'
          % ('ALL FIVE RUNS BEHAVED AS SPECIFIED' if ok else 'FAILED'))
    print('=' * 78)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
