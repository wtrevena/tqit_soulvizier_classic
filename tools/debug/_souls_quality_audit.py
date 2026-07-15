r"""SOULS QUALITY AUDIT engine (read-only, ground truth) - the probe behind
docs/reports/souls_quality_audit.md. Enumerates every soul ring in the
DEPLOYED arz (work/SoulvizierClassic/Database, build40 GOLDEN b33c5a44 at
audit time), matches each to its SV 0.98i original, grades every family on
the 6-axis rubric (stats / augment liveness / proc chain / pet kit /
name+desc / icon), and writes per-family JSON evidence next to this script.

Usage:  py tools/debug/_souls_quality_audit.py     (no build, ~4 min, 3 arz loads)

Family classification (non-REAL categories are SV-inherited scaffolding,
enumerated but not graded):

  - CONFLICTED-DUP : SV-inherited Dropbox 'conflicted copy' duplicate rings
  - SV-DUP         : SV's own duplicate scaffolding (X_soul_n_ / _n__e / _n__l)
  - TEMPLATE       : SV per-family soultemplate scaffolding records
  - WILDCARD       : 'Any X Soul' enchanting-formula reagent wildcards
  - DEV-TEST       : records under soul\test\ (all SV-inherited dev scratch)
  - REAL           : gradeable souls (GOOD / MINOR-GAP / DEFICIENT)

v1 false-positive fixes: roster-locked family grants exempt from SHARED-GRANT;
pet-equip dangling refs that are upstream disable markers ('x') or upstream-
proven pets downgraded to WARN; icon mismatch compared vs SV bitmap; nymph
summon-skill icon checked (in-flight feat/b40-soul-icons); augment-level
tier inversions promoted to DEFICIENT.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# tools/debug/_souls_quality_audit.py -> repo/worktree root is 2 levels up.
# The tools/ import comes from the SAME checkout as this script; the audited
# artifacts come from the MAIN checkout's work/ (the deployed build), so the
# probe always describes the shipped arz no matter which worktree runs it.
WT = Path(__file__).resolve().parents[2]
REPO = Path(r"C:/Users/willi/repos/tqit_soulvizier_classic")
sys.path.insert(0, str(WT / "tools"))
from arz_patcher import ArzDatabase          # noqa: E402
from arc_patcher import ArcArchive           # noqa: E402

MOD_ARZ = REPO / "work/SoulvizierClassic/Database/SoulvizierClassic.arz"
SV_ARZ = REPO / "upstream/soulvizier_098i/Database/database.arz"
BASE_ARZ = Path(r"C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Database/database.arz")
MOD_TEXT = REPO / "work/SoulvizierClassic/Resources/Text.arc"
BASE_TEXT = Path(r"C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Text/Text_EN.arc")
SVITEMS_ARC = REPO / "work/SoulvizierClassic/Resources/SVItems.arc"
ITEMS_ARC = REPO / "work/SoulvizierClassic/Resources/Items.arc"
OUT = Path(__file__).parent / "_souls_quality_audit.json"  # regenerable output

SOUL_PREFIX = 'records\\item\\equipmentring\\soul\\'
SPAWN_CLASSES = ('Skill_SpawnPet', 'Skill_AttackProjectileSpawnPet')
CTRL_TEMPLATE = 'database\\templates\\skillautocastcontroller.tpl'
PC_ANM_TABLES = (
    'records\\creature\\pc\\anm\\anm_malepc01.dbr',
    'records\\creature\\pc\\anm\\anm_femalepc.dbr',
)
ROSTER_LOCKED = {
    'lifedrain.dbr', 'firefragmentnova.dbr', 'arachne_venomspray.dbr',
    'ringoflightning.dbr', 'melinoe_bloodboil.dbr', 'harpy_lightningaura.dbr',
    'toxeus_flashpowder.dbr', 'cyclops_groundsmash.dbr',
    # roster-exempt summons (skill_quality.SUMMON_EXEMPT)
    'skeleton_summon.dbr', 'skeletonarcher_summon.dbr', 'mummy_summon.dbr',
    'carrioncrow_summon.dbr', 'formicid_summon.dbr', 'peng_summon.dbr',
    'summon_zombiesoldier.dbr', 'foulbeast_summon_soul.dbr',
}
EXCLUDE_NUMERIC = {
    'actorHeight', 'actorRadius', 'castsShadows', 'allowTransparency',
    'cannotPickUp', 'cannotPickUpMultiple', 'DisplayAsQuestItem',
    'dexterityRequirement', 'intelligenceRequirement', 'strengthRequirement',
    'levelRequirement', 'itemLevel', 'itemCost', 'itemSkillLevel',
    'maxStackSize', 'dropSound3D', 'glowTextureScale',
}


def _norm(p):
    return str(p).replace('/', '\\').lower().strip()


def fields_of(db, rec):
    ff = db.get_fields(rec)
    out = {}
    if not ff:
        return out
    for key, tf in ff.items():
        fname = key.split('###')[0]
        if tf.values:
            out[fname] = list(tf.values)
    return out


def sval(fd, name):
    v = fd.get(name)
    if v and isinstance(v[0], str) and v[0].strip():
        return v[0].strip()
    return None


def nval(fd, name):
    v = fd.get(name)
    if v is None:
        return None
    try:
        return float(v[0])
    except (TypeError, ValueError):
        return None


def load_text_tags(arc_path):
    tags = {}
    arc = ArcArchive.from_file(Path(arc_path))
    for entry in arc.entries:
        nm = getattr(entry, 'name', '') or ''
        if not nm.lower().endswith('.txt'):
            continue
        try:
            txt = arc.get_text(nm)
        except Exception:
            continue
        if not txt:
            continue
        for line in txt.splitlines():
            line = line.strip().lstrip('﻿')
            if not line or line.startswith('//') or '=' not in line:
                continue
            k, _, v = line.partition('=')
            k = k.strip()
            if k and k not in tags:
                tags[k] = v.strip()
    return tags


def arc_entry_names(arc_path):
    try:
        arc = ArcArchive.from_file(Path(arc_path))
        return {(getattr(e, 'name', '') or '').replace('/', '\\').lower()
                for e in arc.entries}
    except Exception:
        return set()


def pc_universal_anims(db, recmap):
    universal = None
    for tbl in PC_ANM_TABLES:
        rec = recmap.get(_norm(tbl))
        if not rec:
            return set()
        rows = defaultdict(set)
        for key, tf in (db.get_fields(rec) or {}).items():
            fname = key.split('###')[0]
            m = re.match(r'(.+?)SpecialAnimRef(\d+)$', fname)
            if m and tf.values and str(tf.values[0]).strip():
                rows[m.group(1)].add(str(tf.values[0]).lower())
        for names in rows.values():
            universal = set(names) if universal is None else (universal & names)
    return universal or set()


def main():
    print("loading MOD arz ...", flush=True)
    mod = ArzDatabase.from_arz(MOD_ARZ)
    print("loading SV arz ...", flush=True)
    sv = ArzDatabase.from_arz(SV_ARZ)
    print("loading BASE arz ...", flush=True)
    base = ArzDatabase.from_arz(BASE_ARZ)

    mod_map = {_norm(n): n for n in mod.record_names()}
    sv_map = {_norm(n): n for n in sv.record_names()}
    base_map = {_norm(n): n for n in base.record_names()}

    def resolves(path):
        n = _norm(path)
        return n in mod_map or n in base_map

    mod_tags = load_text_tags(MOD_TEXT)
    base_tags = load_text_tags(BASE_TEXT) if BASE_TEXT.is_file() else {}
    svitems = arc_entry_names(SVITEMS_ARC)
    items_arc = arc_entry_names(ITEMS_ARC)
    universal_anims = pc_universal_anims(mod, mod_map)

    # nymph icon reference (summon_lyia baseline used by _build_boss_summon)
    lyia = next((n for n in mod.record_names()
                 if _norm(n).endswith('\\summon_lyia.dbr')), None)
    nymph_icons = set()
    if lyia:
        lfd = fields_of(mod, lyia)
        for f in ('skillUpBitmapName', 'skillDownBitmapName'):
            v = sval(lfd, f)
            if v:
                nymph_icons.add(_norm(v))
    print(f"nymph icons: {nymph_icons}", flush=True)

    # ---- enumerate soul rings in MOD ------------------------------------
    soul_rings = []
    for n in mod.record_names():
        nn = _norm(n)
        if not nn.startswith(SOUL_PREFIX):
            continue
        fd = fields_of(mod, n)
        cls = sval(fd, 'Class')
        tpl = _norm(sval(fd, 'templateName') or '')
        if cls == 'ArmorJewelry_Ring' or tpl.endswith('jewelry_ring.tpl'):
            soul_rings.append((n, fd))
    print(f"soul rings in mod: {len(soul_rings)}", flush=True)

    sv_rings = {}
    for n in sv.record_names():
        nn = _norm(n)
        if '\\soul\\' not in nn:
            continue
        fd = fields_of(sv, n)
        cls = sval(fd, 'Class')
        tpl = _norm(sval(fd, 'templateName') or '')
        if cls == 'ArmorJewelry_Ring' or tpl.endswith('jewelry_ring.tpl'):
            sv_rings[nn] = fd
    sv_by_base = defaultdict(list)
    for nn in sv_rings:
        sv_by_base[nn.rsplit('\\', 1)[-1]].append(nn)

    # ---- reverse reference index over MOD --------------------------------
    print("building reverse-ref index ...", flush=True)
    refs = defaultdict(list)
    mon_class = {}
    finger2 = {}
    for n in mod.record_names():
        ff = mod.get_fields(n)
        if not ff:
            continue
        chance = None
        floot = None
        cls = None
        for key, tf in ff.items():
            fname = key.split('###')[0]
            if not tf.values:
                continue
            v0 = tf.values[0]
            if fname == 'monsterClassification' and isinstance(v0, str):
                cls = v0
            elif fname == 'chanceToEquipFinger2':
                try:
                    chance = float(v0)
                except (TypeError, ValueError):
                    pass
            elif fname.startswith('lootFinger2Item'):
                floot = (floot or [])
                floot += [str(x) for x in tf.values if isinstance(x, str)]
            for x in tf.values:
                if isinstance(x, str) and '\\soul\\' in _norm(x):
                    refs[_norm(x)].append((n, fname))
        if cls:
            mon_class[n] = cls
        if floot:
            finger2[n] = (chance or 0.0, floot)

    # ---- hand-touched (law) soul families --------------------------------
    law_sources = [WT / 'tools/apply_svc_patches.py',
                   WT / 'tools/create_uber_souls.py',
                   WT / 'tools/uber_soul_designs.py']
    law_sources += sorted((WT / 'tools/patches').glob('*.py'))
    law_tokens = set()
    pat = re.compile(r'([a-z0-9_]+?)_soul(?:_[nel])?\b')
    for p in law_sources:
        try:
            src = p.read_text(encoding='utf-8', errors='replace').lower()
        except Exception:
            continue
        for m in pat.finditer(src):
            law_tokens.add(m.group(1))

    families = defaultdict(lambda: {'tiers': {}, 'dir': '', 'sv_any': False,
                                    'sv_exact_all': True})

    def tier_of(basename):
        m = re.match(r'^(.*?)_(n|e|l)\.dbr$', basename)
        if m:
            return m.group(1), m.group(2)
        return basename[:-4] if basename.endswith('.dbr') else basename, '-'

    skill_cache = {}

    def skill_info(path):
        nn = _norm(path)
        if nn in skill_cache:
            return skill_cache[nn]
        info = {'resolves': False}
        rec = mod_map.get(nn)
        dbx = mod
        if rec is None and nn in base_map:
            rec, dbx = base_map[nn], base
        if rec is not None:
            fd = fields_of(dbx, rec)
            info = {
                'resolves': True,
                'class': sval(fd, 'Class'),
                'anim': sval(fd, 'skillSpecialAnimationName'),
                'display': sval(fd, 'skillDisplayName'),
                'spawnObjects': [str(x) for x in fd.get('spawnObjects', [])
                                 if isinstance(x, str) and x.strip()],
                'ttl': fd.get('spawnObjectsTimeToLive', []),
                'up_icon': sval(fd, 'skillUpBitmapName'),
                'in_sv': nn in sv_map,
            }
        skill_cache[nn] = info
        return info

    def pet_info(path):
        nn = _norm(path)
        rec = mod_map.get(nn)
        dbx = mod
        if rec is None and nn in base_map:
            rec, dbx = base_map[nn], base
        if rec is None:
            return {'resolves': False}
        fd = fields_of(dbx, rec)
        kit = []
        for f, v in fd.items():
            if (re.match(r'skillName\d+$', f) or f in ('attackSkillName', 'initialSkillName')
                    or re.match(r'specialAttack\d*SkillName$', f)):
                for x in v:
                    if isinstance(x, str) and x.strip():
                        kit.append(_norm(x))
        hand = nval(fd, 'handHitDamageMin') or 0.0
        atk = sval(fd, 'attackSkillName')
        equip_bad = []
        for f, v in fd.items():
            if f.startswith('loot') and 'Item' in f:
                for x in v:
                    if (isinstance(x, str) and x.strip() and len(x.strip()) > 3
                            and 'placeholder' not in x.lower()
                            and not resolves(x)):
                        equip_bad.append((f, x))
        return {'resolves': True, 'kit': kit, 'hand': hand, 'attackSkill': atk,
                'equip_dangling': equip_bad, 'in_sv': nn in sv_map}

    def sv_pet_info(path):
        nn = _norm(path)
        rec = sv_map.get(nn)
        if rec is None:
            return None
        fd = fields_of(sv, rec)
        kit = []
        for f, v in fd.items():
            if (re.match(r'skillName\d+$', f) or f in ('attackSkillName', 'initialSkillName')
                    or re.match(r'specialAttack\d*SkillName$', f)):
                for x in v:
                    if isinstance(x, str) and x.strip():
                        kit.append(_norm(x))
        return {'kit': kit, 'hand': nval(fd, 'handHitDamageMin') or 0.0,
                'attackSkill': sval(fd, 'attackSkillName')}

    n_rings = 0
    for rec, fd in soul_rings:
        nn = _norm(rec)
        basename = nn.rsplit('\\', 1)[-1]
        fam, tier = tier_of(basename)
        rel = nn[len(SOUL_PREFIX):]
        fam_dir = rel.rsplit('\\', 1)[0] if '\\' in rel else ''
        key = f"{fam_dir}\\{fam}"
        F = families[key]
        F['dir'] = fam_dir
        n_rings += 1

        ev = {'record': rec}
        svfd = sv_rings.get(nn)
        sv_exact = svfd is not None
        if svfd is None:
            F['sv_exact_all'] = False
            cands = sv_by_base.get(basename, [])
            if cands:
                svfd = sv_rings[cands[0]]
                ev['sv_match'] = cands[0]
        if svfd is not None:
            F['sv_any'] = True
            ev['sv'] = 'exact' if sv_exact else 'byname'

        problems = []
        minors = []
        infos = []

        # name/desc
        name_tag = sval(fd, 'itemNameTag') or sval(fd, 'description')
        ev['name_tag'] = name_tag
        if not name_tag:
            problems.append('NO-NAME-TAG')
        else:
            txt = mod_tags.get(name_tag, base_tags.get(name_tag))
            if txt is None:
                problems.append(f'NAME-TAG-UNRESOLVED:{name_tag}')
            else:
                ev['name'] = txt
                if not txt.startswith('{^'):
                    minors.append('NAME-NO-COLOR-PREFIX')
        it = sval(fd, 'itemText')
        if it:
            ev['itemText'] = it
            if it not in mod_tags and it not in base_tags:
                problems.append(f'DESC-TAG-UNRESOLVED:{it}')
        if svfd is not None and sval(svfd, 'itemText') and not it:
            minors.append('LOST-SV-DESC')

        # icon
        bmp = sval(fd, 'bitmap')
        ev['bitmap'] = bmp
        sv_bmp = sval(svfd, 'bitmap') if svfd is not None else None
        if not bmp:
            problems.append('NO-ICON')
        else:
            bl = _norm(bmp)
            m = re.search(r'soul_([nel])_icon\.tex$', bl)
            if m and tier in 'nel' and m.group(1) != tier:
                if sv_bmp and _norm(sv_bmp) == bl:
                    minors.append('ICON-TIER-MISMATCH-SV-PARITY')
                else:
                    minors.append(f'ICON-UNIFORM-N:{tier} tier shows soul_{m.group(1)} icon')
            parts = bl.split('\\')
            inner = '\\'.join(parts[1:]) if len(parts) > 1 else bl
            if inner not in svitems and inner not in items_arc:
                minors.append(f'ICON-TEX-NOT-IN-ARC:{bmp}')

        # augments
        n_aug = 0
        for k in (1, 2, 3, 4):
            an = sval(fd, f'augmentSkillName{k}')
            if not an:
                continue
            n_aug += 1
            lvl = nval(fd, f'augmentSkillLevel{k}')
            if lvl is None or lvl < 1:
                problems.append(f'DEAD-AUGMENT:augmentSkillName{k}='
                                f'{an.rsplit(chr(92), 1)[-1]} level={lvl}')
            if not resolves(an):
                problems.append(f'AUGMENT-DANGLING:{an}')
        for k in (1, 2):
            an = sval(fd, f'augmentMasteryName{k}')
            if an:
                n_aug += 1
                lvl = nval(fd, f'augmentMasteryLevel{k}')
                if lvl is None or lvl < 1:
                    problems.append(f'DEAD-MASTERY-AUGMENT:{an} level={lvl}')
                if not resolves(an):
                    problems.append(f'MASTERY-AUGMENT-DANGLING:{an}')

        # granted skill
        isn = sval(fd, 'itemSkillName')
        ev['granted'] = isn
        summon = None
        if isn:
            si = skill_info(isn)
            if not si['resolves']:
                problems.append(f'GRANT-DANGLING:{isn}')
            else:
                ev['granted_class'] = si.get('class')
                ev['granted_name'] = si.get('display')
                if not (si.get('class') or '').startswith('Skill'):
                    problems.append(f'GRANT-NOT-SKILL:{isn} class={si.get("class")}')
                anim = si.get('anim')
                if anim and anim.lower() not in universal_anims:
                    problems.append(f'GRANT-ANIM-NOT-CASTABLE:{anim}')
                lvl = nval(fd, 'itemSkillLevel')
                if lvl is None or lvl < 1:
                    problems.append(f'GRANT-LEVEL-0:itemSkillLevel={lvl}')
                ctl = sval(fd, 'itemSkillAutoController')
                if ctl:
                    cn = _norm(ctl)
                    crec = mod_map.get(cn) or base_map.get(cn)
                    if crec is None:
                        problems.append(f'CONTROLLER-DANGLING:{ctl}')
                    else:
                        cdb = mod if cn in mod_map else base
                        cfd = fields_of(cdb, crec)
                        tpl = _norm(sval(cfd, 'templateName') or '')
                        if tpl != CTRL_TEMPLATE:
                            problems.append(f'CONTROLLER-WRONG-TEMPLATE:{tpl}')
                        ch = nval(cfd, 'chanceToRun')
                        if ch is None or ch <= 0:
                            problems.append(f'CONTROLLER-NEVER-FIRES:chanceToRun={ch}')
                        if not sval(cfd, 'triggerType'):
                            problems.append('CONTROLLER-EMPTY-TRIGGER')
                        if sval(cfd, 'targetType') == 'Enemy':
                            rad = nval(cfd, 'autoTargetRadius')
                            if rad is None or rad < 1.0:
                                problems.append(f'CONTROLLER-NO-TARGET-RADIUS:{rad}')
                if (si.get('class') or '') in SPAWN_CLASSES:
                    summon = si
                    # nymph icon on a MOD-authored summon skill (b40 lane, unmerged)
                    up = si.get('up_icon')
                    if (up and _norm(up) in nymph_icons and not si.get('in_sv')
                            and 'summon_lyia' not in _norm(isn)):
                        minors.append('SUMMON-SKILL-NYMPH-ICON (fix in-flight: feat/b40-soul-icons)')

        # summon / pet chain
        if summon is not None:
            spawns = summon['spawnObjects']
            if not spawns:
                problems.append('SUMMON-NO-SPAWNOBJECTS')
            ttl = [x for x in summon.get('ttl', []) if isinstance(x, (int, float)) and x]
            for sp in spawns:
                pi = pet_info(sp)
                if not pi['resolves']:
                    problems.append(f'PET-DANGLING:{sp}')
                    continue
                ev['pet'] = sp
                dead = (pi['hand'] or 0) <= 0 and not pi['attackSkill'] and not pi['kit']
                svp = sv_pet_info(sp)
                if dead:
                    if svp and ((svp['hand'] or 0) > 0 or svp['attackSkill'] or svp['kit']):
                        problems.append(f'PET-KIT-LOST-VS-SV:{sp}')
                    else:
                        minors.append('PET-ZERO-DAMAGE:'
                                      + sp.rsplit('\\', 1)[-1])
                if svp and len(pi['kit']) < len(svp['kit']):
                    lost = sorted(set(svp['kit']) - set(pi['kit']))
                    minors.append(f'PET-KIT-SMALLER-THAN-SV:-{len(lost)}:'
                                  + ','.join(x.rsplit('\\', 1)[-1] for x in lost[:3]))
                if pi['equip_dangling']:
                    if pi.get('in_sv'):
                        minors.append(f'PET-EQUIP-DANGLING-UPSTREAM:{pi["equip_dangling"][:1]}')
                    else:
                        problems.append(f'PET-EQUIP-DANGLING:{pi["equip_dangling"][:2]}')
            if isn:
                sv_sk = sv_map.get(_norm(isn)) or sv_map.get(
                    _norm(isn).replace('\\pcsafe\\', '\\'))
                if sv_sk is not None:
                    svskfd = fields_of(sv, sv_sk)
                    sv_ttl = [x for x in svskfd.get('spawnObjectsTimeToLive', [])
                              if isinstance(x, (int, float)) and x]
                    if ttl and not sv_ttl:
                        problems.append(f'PET-TIMED-WAS-PERMANENT-IN-SV:ttl={ttl}')
                    elif sv_ttl and not ttl:
                        infos.append('pet now PERMANENT (SV was timed)')

        # stat fidelity vs SV
        if svfd is not None:
            lost = []
            changed = 0
            added = 0
            for f in set(svfd) | set(fd):
                if f in EXCLUDE_NUMERIC:
                    continue
                a = svfd.get(f)
                b = fd.get(f)
                try:
                    av = float(a[0]) if a is not None else 0.0
                    bv = float(b[0]) if b is not None else 0.0
                except (TypeError, ValueError, IndexError):
                    continue
                if av != 0.0 and bv == 0.0:
                    lost.append(f'{f}:{av:g}')
                elif av != 0.0 and bv != 0.0 and av != bv:
                    changed += 1
                elif av == 0.0 and bv != 0.0:
                    added += 1
            if lost:
                minors.append('LOST-SV-STATS:' + ','.join(sorted(lost)[:6]))
                ev['lost_stats'] = sorted(lost)
            ev['changed_stats'] = changed
            ev['added_stats'] = added
            sv_isn = sval(svfd, 'itemSkillName')
            if sv_isn and not isn:
                problems.append(f'LOST-SV-GRANT:{sv_isn}')
            elif sv_isn and isn:
                a = _norm(sv_isn).rsplit('\\', 1)[-1]
                b = _norm(isn).rsplit('\\', 1)[-1]
                if a != b:
                    ev['grant_reassigned'] = f'{a} -> {b}'
            sv_naug = sum(1 for k in (1, 2, 3, 4) if sval(svfd, f'augmentSkillName{k}'))
            if sv_naug > n_aug:
                minors.append(f'FEWER-AUGMENTS-THAN-SV:{n_aug}<{sv_naug}')

        # stub
        has_stat = False
        for f, v in fd.items():
            if f in EXCLUDE_NUMERIC or f.startswith(('item', 'aug')):
                continue
            if (f.startswith(('character', 'offensive', 'defensive',
                              'retaliation', 'racial', 'skill'))
                    and isinstance(v[0], (int, float)) and float(v[0]) != 0.0):
                has_stat = True
                break
        if not has_stat and not isn and n_aug == 0:
            problems.append('STUB-NO-EFFECT')

        F['tiers'][tier] = {'ev': ev, 'problems': problems, 'minors': minors,
                            'infos': infos,
                            'item_level': nval(fd, 'itemSkillLevel'),
                            'aug_levels': [nval(fd, f'augmentSkillLevel{k}')
                                           for k in (1, 2, 3, 4)
                                           if sval(fd, f'augmentSkillName{k}')]}

    print(f"rings audited: {n_rings}; families: {len(families)}", flush=True)

    # grant sharing (REAL families only, computed after categorization)
    def category(key, F):
        fam = key.rsplit('\\', 1)[-1]
        recs = [T['ev']['record'].lower() for T in F['tiers'].values()]
        if any('conflicted copy' in r for r in recs):
            return 'CONFLICTED-DUP'
        if fam.endswith('_n_') or fam.endswith('_soul_n'):
            # X_soul_n_ scaffolding groups as fam 'X_soul_n_' (tiers -,e,l via _n__e)
            if fam.endswith('_n_'):
                return 'SV-DUP'
        if re.search(r'_n_soul$', fam):
            return 'SV-DUP'   # X_n_soul.dbr scaffolding next to the real X_soul_{n,e,l}
        if 'soultemplate' in fam:
            return 'TEMPLATE'
        if re.match(r'^0\d_act\d_anysoul$', fam) or fam == 'anysoul' or \
                (fam.startswith('any') and fam.endswith('soul')):
            return 'WILDCARD'
        if F['dir'].split('\\')[0] == 'test':
            return 'DEV-TEST'
        return 'REAL'

    cats = {key: category(key, F) for key, F in families.items()}

    grant_counts = defaultdict(set)
    for key, F in families.items():
        if cats[key] != 'REAL':
            continue
        for t, T in F['tiers'].items():
            g = T['ev'].get('granted')
            if g:
                grant_counts[_norm(g).rsplit('\\', 1)[-1]].add(key)

    results = {}
    for key, F in sorted(families.items()):
        cat = cats[key]
        fam_problems = []
        fam_minors = []
        fam_infos = []
        droppers = set()
        gated = set()
        other_refs = set()
        for t, T in F['tiers'].items():
            fam_problems += [f'[{t}] {p}' for p in T['problems']]
            fam_minors += [f'[{t}] {m}' for m in T['minors']]
            fam_infos += T['infos']
            nn = _norm(T['ev']['record'])
            for r, f in refs.get(nn, []):
                if f.startswith('lootFinger2Item'):
                    ch, _ = finger2.get(r, (0.0, []))
                    tag = (f'{mon_class.get(r, "?")}:'
                           f'{r.rsplit(chr(92), 1)[-1]}')
                    if ch > 0:
                        droppers.add(tag)
                    else:
                        gated.add(tag)
                elif not f.startswith('chanceToEquip'):
                    other_refs.add(r.rsplit('\\', 1)[-1])
        if cat == 'REAL' and not droppers:
            if gated:
                fam_minors.append(
                    'DROP-GATED-CHANCE-0 (only Common/Champion monsters carry '
                    f'it, design gate zeroes them: {sorted(gated)[:2]})')
            elif other_refs:
                fam_minors.append(f'NO-FINGER2-DROPPER (refs: {sorted(other_refs)[:3]})')
            else:
                fam_minors.append('UNOBTAINABLE-NO-REFERENCES')

        tiers = sorted(F['tiers'])
        if cat == 'REAL' and set('nel') - set(tiers) and tiers != ['-']:
            fam_minors.append(f'MISSING-TIERS:{sorted(set("nel") - set(tiers))}')
        try:
            seq = [F['tiers'][t]['aug_levels'] for t in ('n', 'e', 'l')
                   if t in F['tiers']]
            if len(seq) == 3 and all(len(s) == len(seq[0]) for s in seq):
                for i in range(len(seq[0])):
                    vals = [s[i] for s in seq]
                    if None not in vals and not (vals[0] <= vals[1] <= vals[2]):
                        fam_problems.append(
                            f'AUGMENT-LEVEL-TIER-INVERSION:n/e/l={vals}')
                        break
        except Exception:
            pass
        # itemSkillLevel (granted-skill) tier inversion - only meaningful when the
        # SAME grant is present in all 3 tiers (a per-level-scaled skill granted at
        # a LOWER level on the higher-rarity ring). This class is separate from the
        # augment-level inversion above; the v1 detector missed itemSkillLevel-only
        # inversions (e.g. spider\bloodtip_soul 5/1/9, vulture\gustleech_soul 10/4/7).
        try:
            if all(t in F['tiers'] for t in ('n', 'e', 'l')):
                grants = [_norm(F['tiers'][t]['ev'].get('granted') or '')
                          for t in ('n', 'e', 'l')]
                ilv = [F['tiers'][t].get('item_level') for t in ('n', 'e', 'l')]
                if all(grants) and len(set(grants)) == 1 and None not in ilv \
                        and not (ilv[0] <= ilv[1] <= ilv[2]):
                    fam_problems.append(
                        f'GRANT-LEVEL-TIER-INVERSION:n/e/l={ilv}')
        except Exception:
            pass

        if cat == 'REAL':
            gset = set()
            for t, T in F['tiers'].items():
                g = T['ev'].get('granted')
                if g:
                    gset.add(_norm(g).rsplit('\\', 1)[-1])
            for g in gset:
                if g in ROSTER_LOCKED:
                    continue
                n_share = len(grant_counts[g])
                if n_share > 8:
                    fam_minors.append(f'SHARED-GRANT:{g} on {n_share} families')

        fam = key.rsplit('\\', 1)[-1]
        law = any(tok == fam or tok == fam.replace('_soul', '')
                  for tok in law_tokens) or \
            any(len(tok) > 4 and (tok in fam) for tok in law_tokens)
        # LAW downgrade: stat deviations on hand-edited souls are Will's
        # deliberate redesign (build-script soul edits = law), not defects.
        if law:
            kept = []
            for m in fam_minors:
                if 'LOST-SV-STATS' in m or 'FEWER-AUGMENTS-THAN-SV' in m:
                    fam_infos.append('LAW (hand-edited in build scripts): ' + m)
                else:
                    kept.append(m)
            fam_minors = kept
        grade = None
        if cat == 'REAL':
            grade = 'DEFICIENT' if fam_problems else (
                'MINOR-GAP' if fam_minors else 'GOOD')
        results[key] = {
            'family': fam, 'dir': F['dir'], 'cat': cat, 'sv': F['sv_any'],
            'tiers': tiers, 'grade': grade, 'law': law,
            'problems': fam_problems, 'minors': fam_minors, 'infos': fam_infos,
            'droppers': sorted(droppers)[:6],
            'records': {t: F['tiers'][t]['ev'].get('record') for t in F['tiers']},
            'name': next((F['tiers'][t]['ev'].get('name') for t in tiers
                          if F['tiers'][t]['ev'].get('name')), None),
            'granted': next((F['tiers'][t]['ev'].get('granted') for t in tiers
                             if F['tiers'][t]['ev'].get('granted')), None),
            'granted_name': next((F['tiers'][t]['ev'].get('granted_name')
                                  for t in tiers
                                  if F['tiers'][t]['ev'].get('granted_name')), None),
            'grant_reassigned': next((F['tiers'][t]['ev'].get('grant_reassigned')
                                      for t in tiers
                                      if F['tiers'][t]['ev'].get('grant_reassigned')), None),
            'lost_stats': {t: F['tiers'][t]['ev'].get('lost_stats')
                           for t in tiers if F['tiers'][t]['ev'].get('lost_stats')},
            'pet': next((F['tiers'][t]['ev'].get('pet') for t in tiers
                         if F['tiers'][t]['ev'].get('pet')), None),
        }

    from collections import Counter
    cc = Counter(r['cat'] for r in results.values())
    gc = Counter(r['grade'] for r in results.values() if r['grade'])
    sv_real = sum(1 for r in results.values() if r['cat'] == 'REAL' and r['sv'])
    print(json.dumps({'cats': dict(cc), 'grades': dict(gc),
                      'real_with_sv': sv_real}, indent=1))

    OUT.write_text(json.dumps({'rings': n_rings, 'results': results},
                              indent=1), encoding='utf-8')
    print(f"wrote {OUT}")


if __name__ == '__main__':
    main()
