#!/usr/bin/env python3
r"""GATE: prove the proxy -> pool -> monster chain for q_bloodtoxeus_lone resolves in the
DEPLOYED (built) SoulvizierClassic.arz. Read-only. No em dashes.

Chain:
  records\drxmap\proxy\q_bloodtoxeus_lone.dbr            (Class ProxyMonster/etc)
    -> proxy 'pool*' field references the ProxyPool ...
  records\drxmap\proxy\pools\q_bloodtoxeus_lone.dbr      (Class ProxyPool)
    -> pool 'dbrPtr*'/name* fields reference the monster ...
  records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr  (Class Monster)
"""
import sys
from pathlib import Path

REPO = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
sys.path.insert(0, str(REPO / 'tools' / 'debug'))
from arz_lookup import load_arz, decode_fields

PROXY = r'records\drxmap\proxy\q_bloodtoxeus_lone.dbr'
POOL  = r'records\drxmap\proxy\pools\q_bloodtoxeus_lone.dbr'
MON   = r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr'


def get(records, path):
    return records.get(path.lower())


def main():
    arz = sys.argv[1] if len(sys.argv) > 1 else str(
        REPO / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz')
    print(f'ARZ = {arz}')
    raw, strings, records = load_arz(arz)
    print(f'records = {len(records)}\n')

    ok = True

    # 1. Proxy present + its pool references
    r = get(records, PROXY)
    if not r:
        print(f'FAIL: proxy {PROXY} NOT in arz'); ok = False
    else:
        f = decode_fields(raw, strings, r)
        print(f'[PROXY] {r["name"]}  Class={f.get("Class")}')
        pool_refs = []
        for k, v in f.items():
            if 'pool' in k.lower() or (v and isinstance(v[0], str) and 'pools' in str(v[0]).lower()):
                print(f'    {k} = {v}')
                for vv in v:
                    if isinstance(vv, str) and vv.strip():
                        pool_refs.append(vv)
        # also show any dbr-looking string fields
        for k, v in f.items():
            if v and isinstance(v[0], str) and v[0].lower().endswith('.dbr') and 'pool' not in k.lower():
                print(f'    {k} = {v}')
        # verify each referenced pool exists
        for pr in pool_refs:
            key = pr.replace('/', '\\').lower()
            exists = key in records
            print(f'    -> pool ref {pr}: {"RESOLVES" if exists else "MISSING"}')
            if not exists:
                ok = False

    # 2. Pool present + its monster references
    r = get(records, POOL)
    if not r:
        print(f'\nFAIL: pool {POOL} NOT in arz'); ok = False
    else:
        f = decode_fields(raw, strings, r)
        print(f'\n[POOL] {r["name"]}  Class={f.get("Class")}')
        mon_refs = []
        for k, v in f.items():
            if v and isinstance(v[0], str) and v[0].lower().endswith('.dbr'):
                print(f'    {k} = {v}')
                for vv in v:
                    if isinstance(vv, str) and vv.strip().lower().endswith('.dbr'):
                        mon_refs.append(vv)
        # show weight/param fields for context
        for k in ('minSpawn', 'maxSpawn', 'spawnChance', 'champion', 'championChance',
                  'proxyWeight', 'weight'):
            if k in f:
                print(f'    {k} = {f[k]}')
        for mr in mon_refs:
            key = mr.replace('/', '\\').lower()
            exists = key in records
            tag = ''
            if key == MON.lower():
                tag = '  <== um_bloodtoxeus_99'
            print(f'    -> monster ref {mr}: {"RESOLVES" if exists else "MISSING"}{tag}')
            if not exists:
                ok = False

    # 3. Monster present
    r = get(records, MON)
    if not r:
        print(f'\nFAIL: monster {MON} NOT in arz'); ok = False
    else:
        f = decode_fields(raw, strings, r)
        print(f'\n[MONSTER] {r["name"]}  Class={f.get("Class")}')
        for k in ('description', 'monsterClassification', 'charLevel', 'characterLife',
                  'scale', 'characterModelName'):
            if k in f:
                print(f'    {k} = {f[k]}')

    print(f'\n=== CHAIN GATE: {"PASS" if ok else "FAIL"} ===')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
