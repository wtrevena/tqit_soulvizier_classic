#!/usr/bin/env python3
"""Probe arz for summon skills + unbounded-summoner pattern.

Unbounded pattern = a Skill_SpawnPet / skill with spawnObjects[] that has
NO petLimit (or petLimit huge) AND NO spawnObjectsTimeToLive, esp. with a
short cooldown. Also dumps named monster skill chains.

Usage: py tools/debug/summon_probe.py <arz> [--name SUBSTR] [--sweep]
"""
import sys, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase


def gv(db, rec, f):
    v = db.get_field_value(rec, f)
    if isinstance(v, list):
        return v[0] if len(v) == 1 else v
    return v


def fields(db, rec):
    fs = db.get_fields(rec)
    return fs or {}


def spawn_targets(db, rec):
    out = []
    fs = fields(db, rec)
    for k in fs:
        if k.lower().startswith('spawnobjects') and 'timetolive' not in k.lower() and 'maximum' not in k.lower() and 'minimum' not in k.lower():
            v = fs[k].value
            if isinstance(v, list):
                out += [x for x in v if isinstance(x, str) and x.strip()]
            elif isinstance(v, str) and v.strip():
                out.append(v)
    return out


def summarize_skill(db, rec):
    fs = fields(db, rec)
    cls = gv(db, rec, 'Class')
    tgt = spawn_targets(db, rec)
    petlimit = gv(db, rec, 'petLimit')
    ttl = gv(db, rec, 'spawnObjectsTimeToLive')
    cd = gv(db, rec, 'skillCooldownTime')
    smax = gv(db, rec, 'spawnMaximumNumber') or gv(db, rec, 'spawnLimit')
    return dict(cls=cls, targets=tgt, petLimit=petlimit, ttl=ttl, cd=cd, spawnMax=smax)


SKILL_REF_FIELDS = ['attackSkillName','specialAttackSkillName','specialAttack2SkillName',
    'specialAttack3SkillName','specialAttack4SkillName','specialAttack5SkillName',
    'initialSkillName','buffSelfSkillName','buffSelf2SkillName','skillName']


def monster_skills(db, rec):
    fs = fields(db, rec)
    refs = []
    for k in fs:
        kl = k.lower()
        if kl.startswith('skillname') or kl in [f.lower() for f in SKILL_REF_FIELDS]:
            v = fs[k].value
            v = v[0] if isinstance(v, list) and v else v
            if isinstance(v, str) and v.strip().lower().endswith('.dbr'):
                refs.append((k, v.strip()))
    return refs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('arz')
    ap.add_argument('--name', default=None)
    ap.add_argument('--sweep', action='store_true')
    ap.add_argument('--skill', default=None, help='dump one skill record fields')
    args = ap.parse_args()
    db = ArzDatabase.from_arz(Path(args.arz))
    names = list(db.record_names())

    if args.skill:
        for n in names:
            if args.skill.lower() in n.lower():
                fs = fields(db, n)
                print(f'=== {n} ===')
                for k in fs:
                    if any(s in k.lower() for s in ('spawn','pet','cooldown','class','summon','ttl','timetolive','limit')):
                        print(f'  {k} = {fs[k].value}')
        return

    if args.name:
        matches = [n for n in names if args.name.lower() in n.lower()]
        print(f'{len(matches)} records match {args.name!r}')
        for n in matches[:40]:
            cls = gv(db, n, 'Class')
            print(f'--- {n}  Class={cls}')
            for k, v in monster_skills(db, n):
                sk = summarize_skill(db, v) if db.has_record(v) else None
                print(f'    {k}: {v}  {sk}')
        return

    if args.sweep:
        # every record with spawnObjects[] that has NO petLimit>0 and NO ttl
        offenders = []
        allsum = 0
        for n in names:
            tgt = spawn_targets(db, n)
            if not tgt:
                continue
            allsum += 1
            s = summarize_skill(db, n)
            pl = s['petLimit']
            ttl = s['ttl']
            cd = s['cd'] or 0
            has_cap = (isinstance(pl,(int,float)) and pl and pl>0) or (isinstance(ttl,(int,float)) and ttl and ttl>0) or (isinstance(s['spawnMax'],(int,float)) and s['spawnMax'] and s['spawnMax']>0)
            if not has_cap:
                offenders.append((n, s))
        print(f'total skills with spawnObjects: {allsum}')
        print(f'UNCAPPED (no petLimit, no ttl, no spawnMax): {len(offenders)}')
        for n, s in offenders:
            print(f'  {n}')
            print(f'     cls={s["cls"]} cd={s["cd"]} targets={s["targets"]}')
        return


if __name__ == '__main__':
    main()
