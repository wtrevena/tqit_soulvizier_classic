"""BUILD32 MAP-LANE watch poll (local-only, untracked scratch).

Polls the built work arz for the landing of the map-lane's three gating record
sets, and exits (printing which landed) as soon as a not-yet-seen target appears.
Re-invokes the owning agent on exit (run_in_background).

Targets:
  M8 / DB group A : records\\quests\\portal_master_helos.dbr
  M9 / DB group C : records\\drxmap\\proxy\\q_vashkarr_lone.dbr (+ um_vashkarr_99)
  M10 / DB group F: records\\drxmap\\proxy\\q_obs_roulette_a.dbr (+ pool/warband)
"""
import struct, time, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARZ = REPO / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'

TARGETS = {
    'M8_helos':   'portal_master_helos',
    'M9_vashkarr':'q_vashkarr',
    'M10_obs':    'q_obs_roulette',
}

def read_lp(data, off):
    n = struct.unpack_from('<i', data, off)[0]; off += 4
    return data[off:off+n].decode('latin-1'), off+n

def arz_names(path):
    raw = path.read_bytes()
    magic, ver, rt_off, rt_size, rt_count, st_off, st_size = struct.unpack_from('<HHiiiii', raw, 0)
    is_tqit = (magic == 2)
    st = raw[st_off:st_off+st_size]; p = 0
    cnt = struct.unpack_from('<i', st, p)[0]; p += 4
    strings = []
    for _ in range(cnt):
        s, p = read_lp(st, p); strings.append(s)
    names = []; pos = rt_off
    for _ in range(rt_count):
        nid = struct.unpack_from('<i', raw, pos)[0]; pos += 4
        _, pos = read_lp(raw, pos)
        pos += 4 + 4
        if is_tqit: pos += 4
        pos += 8
        names.append(strings[nid].lower() if nid < len(strings) else '')
    return names

def git_head():
    try:
        return subprocess.check_output(['git', '-C', str(REPO), 'log', '-1', '--oneline'],
                                       text=True).strip()
    except Exception as e:
        return f'(git err {e})'

def present(names):
    return {k: any(pat in n for n in names) for k, pat in TARGETS.items()}

def main():
    max_minutes = int(sys.argv[1]) if len(sys.argv) > 1 else 240
    interval = 90
    baseline = present(arz_names(ARZ)) if ARZ.exists() else {k: False for k in TARGETS}
    print(f'[watch] start  head={git_head()}')
    print(f'[watch] baseline present={baseline}')
    deadline = time.time() + max_minutes * 60
    while time.time() < deadline:
        time.sleep(interval)
        try:
            cur = present(arz_names(ARZ))
        except Exception as e:
            print(f'[watch] arz read retry ({e})'); continue
        newly = [k for k in TARGETS if cur[k] and not baseline[k]]
        if newly:
            print(f'[watch] *** LANDED: {newly} ***  head={git_head()}')
            print(f'[watch] full={cur}')
            return 0
    print(f'[watch] timeout after {max_minutes}m; present={present(arz_names(ARZ))} head={git_head()}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
