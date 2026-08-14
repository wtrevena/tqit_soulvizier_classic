#!/usr/bin/env python3
"""GATE: traveler-NPC rig - render chain + variant census (R-248 restored travelers).

LINEAGE: pre-R-246 this gate verified the boat-dialog rig NPCs; R-246 turned them
into mute device markers; R-248 reverted the devices (in-game refuted, graveyarded -
MODDING_PLAYBOOK sec 10/10a) and the SAME records are LIVE one-shot-armed boat
travelers again. The placement roster is identical to the R-246 disposition (the
revert moved records back, not away), so the census table is unchanged - only its
MEANING changed: these are clickable travelers now, not markers. The two checks:

  A. RENDER CHAIN: every travel NPC record in the arz must share the PROVEN
     Knossos-boatman donor mesh + baseTexture byte-identically (a traveler whose
     art does not resolve renders invisible/T-posed - the b88 lesson; these NPCs
     are the ENTIRE travel surface now). When the art dirs are present, the donor
     mesh + internal shaders must also resolve under engine-faithful scoping.
  B. VARIANT PLACEMENT CENSUS (Steam-inertness, R-248 dispositions): the canonical
     map places EXACTLY the canonical traveler set and ZERO hub-only records; the
     TESTHUB map places the full restored rig. By record-name prefix on 0x05:
        prefix                       canonical   TESTHUB
        svc_testhub_master*              0          0     (retired b48r3)
        svc_testhub_return.dbr           0          0     (retired b48r3 warden-split)
        svc_testhub_return_*             4          5     (in-area returns; bossarena hub-only)
        svc_helos_trav_*                 0         14     (plaza launchers - NEVER Steam)
        svc_area_return_*                1         10     (maze03 uber greeter canonical;
                                                           9 boss-area returns hub-only)
        svc_warden_sparta_crypt          1          1     (the Warden, catacombs)

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
# The full traveler roster (all knossos-boatman clones; records stay in the arz
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
    import gate_travel_y_terrain as g
    data, levels = g.load_map(path)
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
                fails.append(f'B: {label} places {got}x {n.decode()} - the R-248 '
                             f'disposition is exactly {want}')
        print(f'  B census {label}: ' + ' '.join(
            f'{n.decode().rstrip("_")}={counts[n]}' for (n, _c, _h) in CENSUS))

    if fails:
        print(f'TRAVELER RIG GATE (R-248): {len(fails)} FAILURE(S)')
        for f in fails:
            print(f'  FAIL {f}')
        return 1
    print('TRAVELER RIG GATE (R-248): PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
