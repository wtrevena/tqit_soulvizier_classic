"""R-247 class-wide boss-form + uber-band audit (read-only probe).

Ruling 4 of R-247 (Will 2026-08-13): enumerate EVERY multi-form boss
(actorToSpawnOnDeath chains) and every uber-tier boss in the shipped arz;
measure form-vs-form (scale / HP / damage / defense) and boss-vs-uber-band.

Usage:
    py tools/debug/r247_boss_form_audit.py <path-to-arz> [--json OUT]

Read-only. Never writes the arz. Output: the full audit table used by
docs/BACKLOG.md's R-247 lane record.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase  # noqa: E402


def _val(fields, key, default=None):
    tf = fields.get(key)
    if tf is None or not tf.values:
        return default
    return tf.values


def _one(fields, key, default=None):
    v = _val(fields, key)
    if v is None or v == []:
        return default
    return v[0]


def measure(db, rec):
    f = db.get_fields(rec)
    if f is None:
        return None
    def arr3(key):
        v = _val(f, key)
        if not v:
            return None
        if len(v) == 1:
            return [v[0]] * 3
        return list(v[:3])
    out = {
        'record': rec,
        'class': _one(f, 'Class', ''),
        'classification': _one(f, 'monsterClassification', ''),
        'name_tag': _one(f, 'description', ''),
        'mesh': _one(f, 'mesh', ''),
        'scale': _one(f, 'scale', 1.0),
        'actorHeight': _one(f, 'actorHeight', None),
        'actorRadius': _one(f, 'actorRadius', None),
        'level': arr3('charLevel'),
        'life': arr3('characterLife'),
        'handMin': arr3('handHitDamageMin'),
        'handMax': arr3('handHitDamageMax'),
        'oa': arr3('characterOffensiveAbility'),
        'da': arr3('characterDefensiveAbility'),
        'armor': arr3('defensiveProtection'),
        'runSpeed': _one(f, 'characterRunSpeed', None),
        'spawn_on_death': _one(f, 'actorToSpawnOnDeath', ''),
        'resists': {k: _val(f, k) for k in (
            'defensivePhysical', 'defensiveFire', 'defensiveCold',
            'defensiveLightning', 'defensivePoison', 'defensiveLife',
            'defensiveBleeding', 'defensiveElementalResistance')
            if _val(f, k)},
        'skills': {},
    }
    for i in list(range(1, 33)):
        k = 'skillName%d' % i
        s = _one(f, k)
        if s:
            out['skills'][k] = s
    for k in ('specialAttackSkillName', 'specialAttack2SkillName',
              'specialAttack3SkillName', 'specialAttack4SkillName',
              'specialAttack5SkillName'):
        s = _one(f, k)
        if s:
            out['skills'][k] = s
    return out


def fmt(m):
    if m is None:
        return '  <missing>'
    life = m['life'] or ['?'] * 3
    hand = ['%s-%s' % (a, b) for a, b in zip(m['handMin'] or ['?'] * 3,
                                             m['handMax'] or ['?'] * 3)]
    return ('  scale=%-5s height=%-6s lvl=%s life=%s hand=%s oa=%s da=%s '
            'run=%s mesh=%s' % (
                m['scale'], m['actorHeight'], m['level'], life, hand,
                m['oa'], m['da'], m['runSpeed'],
                (m['mesh'] or '').split('\\')[-1]))


def main():
    arz = Path(sys.argv[1])
    db = ArzDatabase.from_arz(arz)
    names = list(db.record_names())

    # ---- 1. every actorToSpawnOnDeath chain among creature records ----
    chains = []          # (head, [form1, form2, ...])
    heads = {}
    tails = set()
    for rec in names:
        rl = rec.lower()
        if 'creature' not in rl:
            continue
        m = db.get_fields(rec)
        if m is None:
            continue
        tf = m.get('actorToSpawnOnDeath')
        if tf and tf.values and tf.values[0]:
            heads[rec] = tf.values[0]
            tails.add(tf.values[0].lower())

    for head in sorted(heads):
        if head.lower() in tails:
            continue  # not a chain head, an intermediate
        chain = [head]
        cur = head
        seen = {head.lower()}
        while True:
            nxt = heads.get(cur)
            if nxt is None:
                # case-insensitive lookup
                for k, v in heads.items():
                    if k.lower() == cur.lower():
                        nxt = v
                        break
            if not nxt or nxt.lower() in seen:
                break
            chain.append(nxt)
            seen.add(nxt.lower())
            cur = nxt
        chains.append(chain)

    # ---- 2. uber roster: Boss-classification um_*/svc_* level>=90 or named ----
    ubers = []
    for rec in names:
        rl = rec.lower()
        if 'creature' not in rl:
            continue
        base = rl.rsplit('\\', 1)[-1]
        if not (base.startswith('um_') or base.startswith('svc_um_')):
            continue
        m = measure(db, rec)
        if m is None or m['class'] != 'Monster':
            continue
        if m['classification'] not in ('Boss', 'Quest'):
            continue
        ubers.append(m)

    print('=' * 100)
    print('R-247 AUDIT over %s (%d records)' % (arz, len(names)))
    print('=' * 100)

    print('\n--- MULTI-FORM CHAINS (%d) ---' % len(chains))
    report = []
    for chain in sorted(chains, key=lambda c: c[0].lower()):
        ms = []
        print('\nCHAIN: %s' % ' -> '.join(c.rsplit('\\', 1)[-1] for c in chain))
        for rec in chain:
            m = measure(db, rec)
            if m is None:
                # resolve case-insensitively
                for n in names:
                    if n.lower() == rec.lower():
                        m = measure(db, n)
                        break
            ms.append(m)
            print(fmt(m))
        # verdict: form2 vs form1 (only boss-tier chains matter, but list all)
        if len(ms) >= 2 and ms[0] and ms[1]:
            a, b = ms[0], ms[-1]
            try:
                smaller = float(b['scale'] or 1) < float(a['scale'] or 1)
                ha = (a['actorHeight'] or 0) or 0
                hb = (b['actorHeight'] or 0) or 0
                shorter = hb < ha and hb and ha
                weaker_hp = (a['life'] and b['life']
                             and float(b['life'][1]) < float(a['life'][1]))
                weaker_dmg = (a['handMax'] and b['handMax']
                              and float(b['handMax'][1]) < float(a['handMax'][1]))
                flags = []
                if smaller:
                    flags.append('SMALLER(scale)')
                if shorter:
                    flags.append('SHORTER(height)')
                if weaker_hp:
                    flags.append('WEAKER(hp)')
                if weaker_dmg:
                    flags.append('WEAKER(dmg)')
                verdict = ('BLATANT' if (smaller and weaker_hp) else
                           ('FLAG' if flags else 'OK'))
                print('  VERDICT vs form1: %s %s' % (verdict, flags))
                report.append({'chain': chain, 'verdict': verdict,
                               'flags': flags,
                               'forms': ms})
            except (TypeError, ValueError) as e:
                print('  VERDICT: UNMEASURED (%s)' % e)
                report.append({'chain': chain, 'verdict': 'UNMEASURED',
                               'flags': [], 'forms': ms})

    print('\n--- UBER ROSTER (%d Boss-class um_*) ---' % len(ubers))
    lifes = []
    for m in sorted(ubers, key=lambda x: x['record'].lower()):
        print('%s' % m['record'].rsplit('\\', 1)[-1])
        print(fmt(m))
        if m['life']:
            lifes.append(float(m['life'][1]))
    if lifes:
        lifes.sort()
        print('\nUBER BAND (Epic characterLife, single-record): '
              'min=%d p25=%d median=%d p75=%d max=%d n=%d' % (
                  lifes[0], lifes[len(lifes)//4], lifes[len(lifes)//2],
                  lifes[3*len(lifes)//4], lifes[-1], len(lifes)))

    if '--json' in sys.argv:
        out = Path(sys.argv[sys.argv.index('--json') + 1])
        out.write_text(json.dumps(
            {'chains': report, 'ubers': ubers}, indent=1, default=str),
            encoding='utf-8')
        print('\nJSON written: %s' % out)


if __name__ == '__main__':
    main()
