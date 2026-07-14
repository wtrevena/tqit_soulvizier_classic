"""b39 boss-skill audit (surfaces A + B).

Loads a built .arz and dumps, for every NEW boss + summoned pet:
  Surface A (fought monster): monsterClassification, initialSkillName,
    attackSkillName, every skillName<N>/skillLevel<N>, every
    specialAttack[<N>]SkillName + Chance + Range, and whether each referenced
    skill record RESOLVES in the db. A "castable special" = non-empty SkillName,
    Chance > 0, and the skill resolves.
  Surface B (summoned pet): monsterClassification, spawnObjectsTimeToLive (TTL),
    the AI-fired slots (attackSkillName + specialAttack1..5), petLimit (read off
    the summon skill), and the same resolve check.

Usage:  py tools/debug/b39_boss_skill_audit.py <built.arz>
No writes. Read-only. Deterministic.
"""
import os
import re
import sys

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
from arz_patcher import ArzDatabase  # noqa: E402


def _n(p):
    return (p or '').replace('/', '\\').lower()


def _base(p):
    p = _n(p)
    return p.rsplit('\\', 1)[-1].replace('.dbr', '') if p else ''


# ── enumeration ──────────────────────────────────────────────────────────────
M = 'records\\'
FOUGHT = [
    ('four_generals', 'Dysnomion (a) L45', M + r'xpack\creatures\monster\machae\xsq27_namedhero_a_machae_45.dbr'),
    ('four_generals', 'Dysnomion (a) L47', M + r'xpack\creatures\monster\machae\xsq27_namedhero_a_machae_47.dbr'),
    ('four_generals', 'Makaria (b) L45', M + r'xpack\creatures\monster\machae\xsq27_namedhero_b_machae_45.dbr'),
    ('four_generals', 'Makaria (b) L47', M + r'xpack\creatures\monster\machae\xsq27_namedhero_b_machae_47.dbr'),
    ('four_generals', 'Trophonios (c) L45', M + r'xpack\creatures\monster\machae\xsq27_namedhero_c_machae_45.dbr'),
    ('four_generals', 'Trophonios (c) L47', M + r'xpack\creatures\monster\machae\xsq27_namedhero_c_machae_47.dbr'),
    ('four_generals', 'Menoetes/Marshal', M + r'xpack\creatures\monster\machae\svc_um_hadesmarshal_80.dbr'),
    ('diadochi', 'Helepolis', M + r'xpack\creatures\monster\siegestrider\um_helepolis_99.dbr'),
    ('polis_vault', 'Alkyoneus form1', M + r'xpack\creatures\monster\gigantes\um_polisgaoler_99.dbr'),
    ('polis_vault', 'Alkyoneus form2 (terminal)', M + r'xpack\creatures\monster\gigantes\um_polisgaoler_unbound_99.dbr'),
    ('neferkha', 'Neferkha', M + r'creature\monster\neferkha\um_neferkha_99.dbr'),
    ('toxeus_suite', 'Toxeus Hunt (Legendary Stalker)', M + r'creature\monster\shadowstalker\um_toxeus_hunt_99.dbr'),
    ('monolith', 'Enslaver', M + r'creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr'),
    ('monolith', 'Enslaver Marauder', M + r'creature\monster\shadowstalker\um_enslaver_marauder_99.dbr'),
    ('monolith', 'Devourer / Blood Toxeus', M + r'xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr'),
    ('monolith', 'Tantalus form1', M + r'xpack\creatures\monster\lostsoul\um_tantalus_99.dbr'),
    ('monolith', 'Tantalus form2 (unbound)', M + r'xpack\creatures\monster\lostsoul\um_tantalus_unbound_99.dbr'),
    ('monolith', 'Charon form1', M + r'xpack\creatures\monster\bosses\02_charon\um_charon_ferryman_99.dbr'),
    ('monolith', 'Charon form2', M + r'xpack\creatures\monster\bosses\02_charon\um_charonform2_ferryman_99.dbr'),
    ('monolith', 'Mnemophage shell', M + r'xpack\creatures\monster\epiales\um_mnemophage_99.dbr'),
    ('monolith', 'Mnemophage core', M + r'xpack\creatures\monster\epiales\um_mnemophage_core_99.dbr'),
    ('monolith', 'Ephialtes', M + r'xpack\creatures\monster\epiales\um_ephialtes_99.dbr'),
    ('monolith', 'Dorus', M + r'xpack\creatures\monster\lostsoul\um_dorus_99.dbr'),
    ('monolith', 'Broodmother', M + r'creature\monster\sepulchralwyrm\um_broodmother_99.dbr'),
    ('monolith', 'Kravmoloch', M + r'creature\monster\skeleton\um_kravmoloch_99.dbr'),
    # obsidian-wave apex bosses (donor lineage of Kravmoloch; supplemental)
    ('monolith', 'Gorrahk (Eldest, Kravmoloch donor)', M + r'creature\monster\skeleton\um_gorrahk_99.dbr'),
    ('monolith', 'Vashkarr', M + r'creature\monster\dragonian\um_vashkarr_99.dbr'),
    ('monolith', 'Ilsevar', M + r'creature\monster\skeleton\um_ilsevar_99.dbr'),
    ('monolith', 'Sarkoth', M + r'creature\monster\abyssalliche\um_sarkoth_99.dbr'),
]

EXEMPLARS = [
    ('EXEMPLAR xhero_aorg_45 (Machae Hero = Marshal donor)', M + r'xpack\creatures\monster\machae\xhero_aorg_45.dbr'),
    ('EXEMPLAR um_leveler_43 (Helepolis donor)', M + r'xpack\creatures\monster\siegestrider\um_leveler_43.dbr'),
    ('EXEMPLAR boss_charon_43 (Charon donor)', M + r'xpack\creatures\monster\bosses\02_charon\boss_charon_43.dbr'),
    ('EXEMPLAR xhero_aberkios_43 (Tantalus donor)', M + r'xpack\creatures\monster\lostsoul\xhero_aberkios_43.dbr'),
    ('EXEMPLAR wardenofsouls_48 (Gaoler donor)', M + r'xpack\creatures\monster\gigantes\xsecrethero_wardenofsouls_48.dbr'),
    ('EXEMPLAR um_khenti_31 (Neferkha donor)', M + r'creature\monster\mummy\um_khenti_31.dbr'),
    ('EXEMPLAR am_deathstalker_55_ambush (Hunt/Enslaver rig donor)', M + r'creature\monster\shadowstalker\am_deathstalker_55_ambush.dbr'),
]

# label, source_monster (or None), [pet paths], summon_skill
def _pets(base, ids=(1, 2, 3)):
    return [M + r'skills\soulskills\pets\%s_%d.dbr' % (base, i) for i in ids]

SS = M + r'skills\soulskills\summon_'
PETS = [
    ('Menoetes/Marshal', M + r'xpack\creatures\monster\machae\svc_um_hadesmarshal_80.dbr', _pets('hadesmarshal'), SS + 'hadesmarshal.dbr'),
    ('Neferkha', M + r'creature\monster\neferkha\um_neferkha_99.dbr', _pets('neferkha'), SS + 'neferkha.dbr'),
    ('Enslaver (pet-of-pet)', M + r'creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr', _pets('toxeus_enslaver'), SS + 'toxeus_enslaver.dbr'),
    ('Enslaver marauder pets', M + r'creature\monster\shadowstalker\um_enslaver_marauder_99.dbr', _pets('enslaver_marauder'), None),
    ('Devourer / Blood Toxeus', M + r'xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr', _pets('bloodtoxeus'), SS + 'bloodtoxeus.dbr'),
    ('Tantalus shade', M + r'xpack\creatures\monster\lostsoul\xhero_aberkios_43.dbr', _pets('tantalus_shade'), SS + 'tantalus_shade.dbr'),
    ('Charon oarsman', M + r'xpack\creatures\monster\bosses\02_charon\charon_minion_30.dbr', _pets('charon_oarsman'), SS + 'charon_oarsman.dbr'),
    ('Mnemophage phantasm', None, _pets('mnemophage_phantasm'), SS + 'mnemophage.dbr'),
    ('Broodmother', M + r'creature\monster\sepulchralwyrm\um_broodmother_99.dbr', _pets('broodmother'), SS + 'broodmother.dbr'),
    ('Broodmother wyrmling', None, _pets('broodmother_wyrmling'), SS + 'broodmother_wyrmlings.dbr'),
    ('Kravmoloch warden', M + r'creature\monster\skeleton\um_gorrahk_99.dbr', _pets('kravmoloch_warden'), SS + 'kravmoloch_warden.dbr'),
    ('Voranthys', M + r'creature\monster\sepulchralwyrm\um_sepulchralwyrm_31.dbr', _pets('voranthys'), SS + 'voranthys.dbr'),
    ('Eater of Days', M + r'creature\monster\sepulchralwyrm\um_eaterofdays_45.dbr', _pets('eaterofdays'), SS + 'eaterofdays.dbr'),
    ('Pygmalion', M + r'creature\monster\automatoi\um_pygmalion_41.dbr', _pets('pygmalion'), SS + 'pygmalion.dbr'),
    ('Sarpedon', M + r'creature\monster\minotaur\um_sarpedon_41.dbr', _pets('sarpedon'), SS + 'sarpedon.dbr'),
    ('Long Nu', None, _pets('longnu'), SS + 'longnu.dbr'),
    ('Meritamen', M + r'creature\monster\sandspirit\us_meritamen_34.dbr', _pets('meritamen'), SS + 'meritamen.dbr'),
]

SKILL_RE = re.compile(r'^skillName(\d+)$')
LEVEL_RE = re.compile(r'^skillLevel(\d+)$')
SPECIAL_RE = re.compile(r'^specialAttack(\d*)SkillName$')


class Auditor:
    def __init__(self, db):
        self.db = db
        self._names = {n.lower() for n in db.record_names()}

    def resolves(self, ref):
        return _n(ref) in self._names

    def gv(self, rec, f):
        v = self.db.get_field_value(rec, f)
        return v[0] if isinstance(v, list) else v

    def skill_slots(self, rec):
        """Return {slot_index: (skillref, level)} for skillName<N>."""
        ff = self.db.get_fields(rec) or {}
        levels = {}
        skills = {}
        for k, tf in ff.items():
            base = k.split('###')[0]
            ml = LEVEL_RE.match(base)
            if ml and tf.values:
                levels[int(ml.group(1))] = tf.values[0]
        for k, tf in ff.items():
            base = k.split('###')[0]
            ms = SKILL_RE.match(base)
            if ms and tf.values and str(tf.values[0]).strip():
                idx = int(ms.group(1))
                skills[idx] = (str(tf.values[0]), levels.get(idx))
        return dict(sorted(skills.items()))

    def special_slots(self, rec):
        """Return list of (label, skillref, chance, range) for specialAttack slots
        in canonical order ('', 2, 3, 4, 5, 6...)."""
        ff = self.db.get_fields(rec) or {}
        found = {}
        for k, tf in ff.items():
            base = k.split('###')[0]
            m = SPECIAL_RE.match(base)
            if m and tf.values and str(tf.values[0]).strip():
                suf = m.group(1)  # '' or '2'..
                found[suf] = str(tf.values[0])
        out = []
        order = [''] + [str(i) for i in range(2, 12)]
        for suf in order:
            if suf in found:
                chance = self.gv(rec, 'specialAttack%sChance' % suf)
                rng = self.gv(rec, 'specialAttack%sRange' % suf)
                out.append(('specialAttack%s' % suf, found[suf], chance, rng))
        return out

    def kit_in_skillnames(self, rec):
        return {_n(s) for (s, _lv) in self.skill_slots(rec).values()}

    def audit_fought(self, label, module, rec):
        db = self.db
        print('\n' + '=' * 78)
        print('[A] %-28s (%s)' % (label, module))
        print('    %s' % rec)
        if not db.has_record(rec):
            print('    !!! RECORD MISSING')
            return {'missing': True, 'label': label}
        cls = self.gv(rec, 'monsterClassification')
        init = self.gv(rec, 'initialSkillName')
        atk = self.gv(rec, 'attackSkillName')
        print('    class=%s  initialSkill=%s  attackSkill=%s'
              % (cls, _base(init) or '-', _base(atk) or '-'))
        skills = self.skill_slots(rec)
        print('    skillName slots (%d):' % len(skills))
        for idx, (s, lv) in skills.items():
            r = 'OK' if self.resolves(s) else 'DEAD-REF'
            print('      skillName%-2d lvl=%-3s %-40s %s' % (idx, lv, _base(s), r))
        specials = self.special_slots(rec)
        # map normalized skillref -> level (from skillName slots)
        lvl_by_ref = {_n(s): lv for (s, lv) in skills.values()}
        castable = 0
        level0 = 0
        print('    specialAttack slots (%d):' % len(specials))
        for (slot, s, chance, rng) in specials:
            res = self.resolves(s)
            ch = 0.0 if chance is None else float(chance)
            slvl = lvl_by_ref.get(_n(s))   # None = not in a skillName slot
            good = res and ch > 0
            if good:
                castable += 1
            flag = []
            if not res:
                flag.append('DEAD-REF')
            if ch <= 0:
                flag.append('CHANCE=0')
            if slvl is None:
                flag.append('NO-SKILLNAME-SLOT')
            elif slvl == 0:
                flag.append('LEVEL0-SPECIAL')
                level0 += 1
            print('      %-16s chance=%-6s lvl=%-4s range=%-11s %-32s %s'
                  % (slot, ch, slvl, rng, _base(s),
                     ' '.join(flag) if flag else 'CASTABLE'))
        # core passives that should never be level 0 (vs the vanilla invariant).
        # globalproperties_epic/legendary + all_hpscaling are difficulty-scaled and
        # ARE level 0 in vanilla, so they are excluded from this flag.
        DEAD_PASSIVE_RE = re.compile(
            r'(armor_passive|hero_scaling|boss_scaling|_conversionimmunity|'
            r'passiveproperties|bonusdamage_|resist)', re.I)
        dead_pass = []
        for idx, (s, lv) in skills.items():
            if lv == 0 and DEAD_PASSIVE_RE.search(_base(s)):
                dead_pass.append('skillName%d=%s' % (idx, _base(s)))
        if dead_pass:
            print('    !!! LEVEL-0 CORE PASSIVES: %s' % ', '.join(dead_pass))
        print('    >>> SUMMARY A: %d skills, %d CASTABLE specials, %d LEVEL0-specials, '
              '%d dead passives' % (len(skills), castable, level0, len(dead_pass)))
        return {'label': label, 'module': module, 'class': cls,
                'n_skills': len(skills), 'castable_specials': castable,
                'level0_specials': level0, 'dead_passives': len(dead_pass)}

    def audit_pet(self, label, source, pets, summon):
        db = self.db
        print('\n' + '=' * 78)
        print('[B] %-28s  summon=%s' % (label, _base(summon) or '-'))
        pet_limit = None
        ttl_summon = None
        max_lvl = None
        spawn_objs = None
        if summon and db.has_record(summon):
            pet_limit = self.gv(summon, 'petLimit')
            ttl_summon = self.gv(summon, 'spawnObjectsTimeToLive')
            max_lvl = self.gv(summon, 'skillMaxLevel')
            spawn_objs = db.get_field_value(summon, 'spawnObjects')
            print('    summon petLimit=%s skillMaxLevel=%s TTL=%s spawnObjects=%s'
                  % (pet_limit, max_lvl, ttl_summon,
                     [_base(x) for x in (spawn_objs if isinstance(spawn_objs, list) else [spawn_objs] if spawn_objs else [])]))
        elif summon:
            print('    !!! SUMMON SKILL MISSING: %s' % summon)
        if source:
            src_specials = sum(1 for (_sl, s, ch, _r) in self.special_slots(source)
                               if self.resolves(s) and ch and float(ch) > 0)
            print('    source=%s  (source has %d castable specials)'
                  % (_base(source), src_specials) if db.has_record(source)
                  else '    source MISSING: %s' % source)
        rows = []
        for p in pets:
            if not db.has_record(p):
                print('    - %-24s !!! PET MISSING' % _base(p))
                rows.append({'pet': _base(p), 'missing': True})
                continue
            cls = self.gv(p, 'monsterClassification')
            ttl = db.get_field_value(p, 'spawnObjectsTimeToLive')
            ai = []
            for slot in ('attackSkillName', 'specialAttackSkillName',
                         'specialAttack2SkillName', 'specialAttack3SkillName',
                         'specialAttack4SkillName', 'specialAttack5SkillName'):
                s = self.gv(p, slot)
                if s and str(s).strip():
                    suf = slot.replace('SkillName', '').replace('specialAttack', 'sa').replace('attack', 'atk')
                    chance = None
                    if slot.startswith('specialAttack'):
                        cslot = slot.replace('SkillName', 'Chance')
                        chance = self.gv(p, cslot)
                    ai.append((suf, str(s), chance, self.resolves(s)))
            n_ai = sum(1 for (_sl, s, ch, res) in ai
                       if res and (ch is None or float(ch) > 0))
            ttlv = ttl if not isinstance(ttl, list) else ttl
            print('    - %-22s class=%-8s TTL=%s  AI-slots=%d' % (_base(p), cls, ttlv, len(ai)))
            for (suf, s, ch, res) in ai:
                flag = 'OK' if res else 'DEAD-REF'
                chs = '' if ch is None else ' chance=%s' % ch
                print('        %-6s %-38s%s %s' % (suf, _base(s), chs, flag))
            rows.append({'pet': _base(p), 'class': cls, 'n_ai': len(ai), 'ttl': ttlv})
        return {'label': label, 'pet_limit': pet_limit, 'rows': rows}


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path or not os.path.exists(path):
        print('Usage: py tools/debug/b39_boss_skill_audit.py <built.arz>')
        sys.exit(2)
    print('Loading %s ...' % path)
    db = ArzDatabase.from_arz_path(path) if hasattr(ArzDatabase, 'from_arz_path') else ArzDatabase.from_arz(__import__('pathlib').Path(path))
    a = Auditor(db)
    print('\n\n########## SURFACE A: FOUGHT MONSTER RECORDS ##########')
    for module, label, rec in FOUGHT:
        a.audit_fought(label, module, rec)
    print('\n\n########## EXEMPLARS (known-good vanilla/xpack bosses) ##########')
    for label, rec in EXEMPLARS:
        a.audit_fought(label, 'exemplar', rec)
    print('\n\n########## SURFACE B: SUMMONED PET RECORDS ##########')
    for (label, source, pets, summon) in PETS:
        a.audit_pet(label, source, pets, summon)
    print('\n\nDONE.')


if __name__ == '__main__':
    main()
