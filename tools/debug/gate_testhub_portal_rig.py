#!/usr/bin/env python3
"""GATE: TESTHUB device-court rig (R-246 native-device travel, 2026-08-13).

LINEAGE: the pre-R-246 versions of this gate verified the boat-dialog rig NPCs
(svc_testhub_master/return; render chain + Steam-inertness). R-246 ripped every rig
BOAT ROW; the records survive as MUTE NAMED MARKERS beside the new devices (shared-
record law), and the rig itself is now the 14-door east-field court + T15 return
shrines, whose byte-level invariants live in gate_device_resolution (D1-D7/C/Y).
This gate keeps the two rig checks the device gate does NOT cover:

  A. RENDER CHAIN (D5 law): every R-246 marker/greeter NPC record still in the arz
     must share the PROVEN Knossos-boatman donor mesh + baseTexture byte-identically
     (a marker whose art does not resolve renders invisible/T-posed - the fate the
     b88 lesson warns about; markers are the court's ONLY label surface). When the
     art dirs are present, the donor mesh + internal shaders must also resolve under
     engine-faithful archive scoping.
  B. VARIANT PLACEMENT CENSUS (Steam-inertness, R-246 dispositions): the canonical
     map places EXACTLY the ruled marker set and ZERO hub-only records; the TESTHUB
     map places the full court. Censused by record-name prefix on the 0x05 sections:
        prefix                       canonical   TESTHUB
        svc_testhub_master*              0          0     (retired b48r3)
        svc_testhub_return.dbr           0          0     (retired b48r3 warden-split)
        svc_testhub_return_*             4          5     (area markers; bossarena hub-only)
        svc_helos_trav_*                 0         14     (court markers - NEVER Steam)
        svc_area_return_*                1         10     (maze03 greeter canonical;
                                                           9 more are hub landing markers)
        svc_warden_sparta_crypt          1          1     (the named Warden greeter)

Usage:
  py tools/debug/gate_testhub_portal_rig.py [<arz>] [<canonical.arc>] [<testhub.arc>]
Defaults: work/SoulvizierClassic/Database/SoulvizierClassic.arz; map checks run only
for the paths given. Exit 0 = PASS.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))

from arz_patcher import ArzDatabase              # noqa: E402
import validate_render_chain as vrc              # noqa: E402

DONOR = r'records\creature\npc\speaking\greece\knossos_boatmantoegypt.dbr'
# The full R-246 marker roster (all knossos-boatman clones; records stay in the arz
# under the shared-record law even where placements are TESTHUB-only or zero).
MARKERS = (
    [r'records\quests\svc_helos_trav_%s.dbr' % s for s in
     ('garden', 'secret', 'sparta', 'uber', 'bossarena', 'warband', 'dorus',
      'tantalus', 'charon', 'mnemophage', 'ephialtes', 'devourer', 'vashkarr',
      'obsidian')]
    + [r'records\quests\svc_testhub_return_%s.dbr' % s for s in
       ('garden', 'secret', 'uber', 'sparta', 'bossarena')]
    + [r'records\quests\svc_area_return_%s.dbr' % s for s in
       ('uber', 'dorus', 'tantalus', 'charon', 'mnemophage', 'ephialtes',
        'warband', 'devourer', 'vashkarr', 'obsidian')]
    + [r'records\quests\svc_warden_sparta_crypt.dbr',
       r'records\quests\svc_testhub_master.dbr',       # retired-but-kept
       r'records\quests\svc_testhub_return.dbr']       # retired-but-kept donor
)
# (record-name prefix, canonical count, testhub count)
CENSUS = [
    (b'svc_testhub_master', 0, 0),
    (b'svc_testhub_return.dbr', 0, 0),
    (b'svc_testhub_return_', 4, 5),
    (b'svc_helos_trav_', 0, 14),
    (b'svc_area_return_', 1, 10),
    (b'svc_warden_sparta_crypt', 1, 1),
]


def _norm(s):
    return str(s).replace('/', '\\').lower()


def census_map(path):
    import gate_device_resolution as g
    data, levels, _groups = g.load_map(path)
    counts = {n: 0 for (n, _c, _h) in CENSUS}
    for lv in levels:
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        for (nm, _x, _y, _z, _f, _u, _i) in g.parse_0x05(blob)[0]:
            nb = nm.encode()
            for (n, _c, _h) in CENSUS:
                if n.lower() in nb:
                    counts[n] += 1
    return counts


def main(argv):
    arz = Path(argv[1]) if len(argv) > 1 else \
        REPO / 'work/SoulvizierClassic/Database/SoulvizierClassic.arz'
    fails = []

    # ---- A: render chain ----
    db = ArzDatabase.from_arz(arz)
    recmap = {_norm(n): n for n in db.record_names()}

    def fld(name, key):
        ff = db.get_fields(name) or {}
        for k, tf in ff.items():
            if k.split('###')[0] == key and tf.values:
                return str(tf.values[0])
        return None

    dn = recmap.get(_norm(DONOR))
    if not dn:
        fails.append(f'A: donor MISSING from arz: {DONOR}')
    else:
        dmesh, dtex = fld(dn, 'mesh'), fld(dn, 'baseTexture')
        n_ok = 0
        for p in MARKERS:
            r = recmap.get(_norm(p))
            if not r:
                fails.append(f'A: marker record MISSING from arz (shared-record law): {p}')
                continue
            m, t = fld(r, 'mesh'), fld(r, 'baseTexture')
            if _norm(m) != _norm(dmesh):
                fails.append(f'A: {p} mesh {m!r} != donor {dmesh!r}')
            elif _norm(t) != _norm(dtex):
                fails.append(f'A: {p} baseTexture {t!r} != donor {dtex!r}')
            else:
                n_ok += 1
        mod_res = REPO / 'work/SoulvizierClassic/Resources'
        game = Path(r'C:/Program Files (x86)/Steam/steamapps/common/'
                    r'Titan Quest Anniversary Edition')
        if mod_res.is_dir() and (game / 'Resources').is_dir():
            eng = vrc.EngineArcResolver(str(mod_res), str(game))
            ok_mesh, shaders = vrc.mesh_internal_shaders(eng, dmesh)
            ok_tex, tdet = eng.resolve(dtex)
            bad = [s for s in shaders if not s[1]]
            if not ok_mesh:
                fails.append(f'A: donor mesh unresolved under engine scoping: {dmesh}')
            if bad:
                fails.append(f'A: donor mesh internal shader(s) unresolved: '
                             f'{[s[0] for s in bad]}')
            if not ok_tex:
                fails.append(f'A: donor baseTexture unresolved: {dtex} ({tdet})')
            print(f'  A render: {n_ok}/{len(MARKERS)} markers byte-share donor art; '
                  f'mesh ok={ok_mesh} shaders={len(shaders)} bad={len(bad)}; '
                  f'tex ok={ok_tex}')
        else:
            print(f'  A render: {n_ok}/{len(MARKERS)} markers byte-share donor art '
                  f'(art dirs absent -> engine-scoping shader check SKIPPED)')

    # ---- B: variant placement census ----
    for (label, idx, path) in (('canonical', 1, argv[2] if len(argv) > 2 else None),
                               ('TESTHUB', 2, argv[3] if len(argv) > 3 else None)):
        if not path:
            continue
        counts = census_map(path)
        for (n, c_want, h_want) in CENSUS:
            want = c_want if label == 'canonical' else h_want
            got = counts[n]
            if got != want:
                fails.append(f'B: {label} places {got}x {n.decode()} - the R-246 '
                             f'disposition is exactly {want}')
        print(f'  B census {label}: ' + ' '.join(
            f'{n.decode().rstrip("_")}={counts[n]}' for (n, _c, _h) in CENSUS))

    if fails:
        print(f'TESTHUB DEVICE-COURT RIG GATE: {len(fails)} FAILURE(S)')
        for f in fails:
            print(f'  FAIL {f}')
        return 1
    print('TESTHUB DEVICE-COURT RIG GATE: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
