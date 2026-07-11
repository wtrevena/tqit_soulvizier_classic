#!/usr/bin/env python3
"""build36 CONTENT WAVE - donor-existence + key-field probe (READ-ONLY).
Verifies every donor record path across C1-C7 resolves in the mod arz UNION the
base game arz, so the implementer does not iterate on missing-donor build fails.
No em dashes."""
import sys, struct, zlib
from pathlib import Path

REPO = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
MOD = REPO / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'
BASE = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Database\database.arz')


def read_lp_string(data, offset):
    n = struct.unpack_from('<i', data, offset)[0]
    offset += 4
    return data[offset:offset + n].decode('latin-1'), offset + n


def load_names(arz_path):
    raw = Path(arz_path).read_bytes()
    (magic, version, rt_offset, rt_size, rt_count,
     st_offset, st_size) = struct.unpack_from('<HHiiiii', raw, 0)
    is_tqit = (magic == 2)
    st = raw[st_offset:st_offset + st_size]
    sp = 0
    st_count = struct.unpack_from('<i', st, sp)[0]; sp += 4
    strings = []
    for _ in range(st_count):
        s, sp = read_lp_string(st, sp)
        strings.append(s)
    names = set()
    pos = rt_offset
    for _ in range(rt_count):
        name_id = struct.unpack_from('<i', raw, pos)[0]; pos += 4
        _t, pos = read_lp_string(raw, pos)
        pos += 8  # data_offset + csize
        if is_tqit:
            pos += 4
        pos += 8  # timestamp
        nm = strings[name_id] if name_id < len(strings) else ''
        names.add(nm.lower().replace('/', '\\'))
    return names


mod = load_names(MOD)
base = load_names(BASE)
allnames = mod | base
print(f"mod={len(mod)} base={len(base)} union={len(allnames)}")


def chk(label, paths):
    print(f"\n== {label} ==")
    for p in paths:
        key = p.lower().replace('/', '\\')
        where = 'MOD' if key in mod else ('BASE' if key in base else '!!!MISSING!!!')
        print(f"  [{where:14}] {p}")


chk('C1 Tantalus', [
    r'records\xpack\creatures\monster\lostsoul\xhero_aberkios_43.dbr',
    r'records\skills\boss skills\alastor_circleofdecay.dbr',
    r'records\skills\boss skills\sandwraithlord_summonsandwraiths.dbr',
    r'records\skills\monster skills\buff_self\toxeus_envenomweapon.dbr',
    r'records\skills\spirit\lifedrain.dbr',
    r'records\skills\stealth\poisongasbomb.dbr',
    r'records\skills\nature\plague.dbr',
    r'records\skills\spirit\deathchillaura_ravagesoftime.dbr',
    r'records\skills\spirit\drxdeathchillaura_ravagesoftime.dbr',
    r'records\skills\stealth\lethalstrike.dbr',
    r'records\xpack\creatures\monster\lostsoul\uw_am_lostsoul_warrior_38.dbr',
    r'records\xpack\creatures\monster\lostsoul\uw_ar_lostsoul_archer_37.dbr',
    r'records\effects\spirit\343_wraithlordspawn_fx01.dbr',
    r'records\effects\spirit\343_wraithlorddeath_fx01.dbr',
    r'records\skills\boss skills\boss_conversionimmunity.dbr',
    r'records\skills\monster skills\passive_buffs\hero_scaling.dbr',
    r'records\skills\monster skills\defense\armor_passive.dbr',
    r'records\skills\monster skills\globalproperties_legendary01.dbr',
    r'records\drxmap\proxy\q_leinth_lone.dbr',
    r'records\drxmap\proxy\pools\q_leinth_lone.dbr',
    r'records\proxies boss\herolimit_all.dbr',
    r'records\proxies orient\difficulty_04.dbr',
    r'records\drxitem\container\svc_obsidianhoard_01.dbr',
    r'records\drxitem\container\svc_obsidianhoard_pool_01.dbr',
    r'records\drxitem\container\hidden_bloodcave_chest_01.dbr',
    r'records\proxies orient\limit_obsidianbosses.dbr',
])

chk('C2 Charon/GoldenBough', [
    r'records\xpack\creatures\monster\bosses\02_charon\boss_charon_43.dbr',
    r'records\xpack\creatures\monster\bosses\02_charon\boss_charonform2_43.dbr',
    r'records\xpack\creatures\monster\bosses\02_charon\charon_minion_30.dbr',
    r'records\xpack\skills\bossskills\charon_deathchillaura_minions.dbr',
    r'records\xpack\skills\bossskills\charon_geyserform2.dbr',
    r'records\xpack\skills\bossskills\charon_swoopstomp.dbr',
    r'records\xpack\skills\bossskills\charon_geyserform1.dbr',
    r'records\xpack\skills\bossskills\charon_summon.dbr',
    r'records\item\equipmentamulet\u_e_blessingofthegods.dbr',
    r'records\xpack\item\containers\bosschest02_charon_01.dbr',
    r'records\xpack\item\containers\bosschestpool02_charon_01.dbr',
    r'records\xpack\item\containers\proxies\bosschest02_charon.dbr',
    r'records\skills\storm\drxcoldaura.dbr',
    r'records\skills\soulskills\melinoe_bloodboil.dbr',
])

chk('C3 Mnemophage', [
    r'records\xpack\creatures\monster\epiales\ur_overmind_46.dbr',
    r'records\xpack\creatures\monster\epiales\as_nightmare_43.dbr',
    r'records\skills\monster skills\attack_radius\disruption.dbr',
    r'records\skills\sv\refnat\chainconvert.dbr',
    r'records\skills\sv\refnat\chainconvert_cascade.dbr',
    r'records\xpack\skills\dream\sandsofsleep.dbr',
    r'records\xpack\skills\dream\distortreality.dbr',
    r'records\skills\monster skills\summoning_pets\epiales_summon2.dbr',
    r'records\skills\monster skills\attack_projectile\monster_energydrain.dbr',
    r'records\skills\monster skills\attack_radius\ondeath_voidnova.dbr',
    r'records\skills\monster skills\attack_radius\ondeath_necronova.dbr',
    r'records\xpack\effects\boss effects\hades2_shadowcloud_charfxpak.dbr',
    r'records\xpack\item\equipmentarmor\amulet\u_l_001.dbr',
    r'records\xpack\skills\dream\distortreality_temporalrift.dbr',
    r'records\xpack\skills\dream\drxpsionictouch_multihit.dbr',
    r'records\xpack\creatures\monster\epiales\um_voidlash_46.dbr',
])

chk('C4 Ephialtes', [
    r'records\xpack\creatures\monster\epiales\xhero_cthulekes_45.dbr',
    r'records\skills\monster skills\attack_radius\ixion_cry.dbr',
    r'records\xpack\skills\artifactskills\l_da_morpheusdreamweb_dreamstorm.dbr',
    r'records\skills\spirit\drxvisionofdeath.dbr',
    r'records\xpack\skills\monsterskills\activeattackmelee\monster_takedown.dbr',
    r'records\skills\monster skills\attack_radius\ondeath_zombienoxiousfumes.dbr',
    r'records\xpack\effects\particles\skilleffects\dreamskillfx\troubleddreamsdebuff_charfxpak01.dbr',
    r'records\xpack\item\equipmentarmor\helm\mi_l_keresmage.dbr',
    r'records\skills\spirit\visionofdeath.dbr',
])

chk('C5 Ereban relic', [
    r'records\xpack\item\charms\01_act4_erebancrystal.dbr',
    r'records\xpack\item\charms\02_act4_erebancrystal.dbr',
    r'records\xpack\item\charms\03_act4_erebancrystal.dbr',
    r'records\item\loottables\animalrelics\01_act1_turtleshell.dbr',
    r'records\xpack\creatures\monster\troglodyte\em_brute_43.dbr',
    r'records\xpack\creatures\monster\troglodyte\em_brute_45.dbr',
    r'records\item\lootmagicalaffixes\animalrelics\bonuses\offensive_+%damage_01.dbr',
    r'records\item\lootmagicalaffixes\suffix\default\character_attributestrength_01.dbr',
    r'records\item\lootmagicalaffixes\forge\bonuses\defensive_armor_02.dbr',
])

chk('C6 Dorus + C7 uplifts', [
    r'records\xpack\creatures\monster\lostsoul\um_dorus_99.dbr',
    r'records\skills\monster skills\attack_wave\coral_tsunami.dbr',
    r'records\skills\monster skills\attack_spell\rottengrasp.dbr',
    r'records\skills\sv\dreadaura.dbr',
    r'records\skills\soulskills\pcsafe\ichthian_tidalstrike.dbr',
    r'records\xpack\item\charms\01_act4_spinyshell.dbr',
    # Vashkarr
    r'records\xpack\creatures\monster\ancientdragonian\um_vashkarr_99.dbr',
    r'records\skills\monster skills\attack_melee\dragonian_firebreath.dbr',
    r'records\skills\monster skills\attack_projectile\halimedes_terrifyingroar.dbr',
    r'records\skills\monster skills\ondeath\skills\firenova.dbr',
    r'records\skills\monster skills\attack_projectile\dragonian_stormorb.dbr',
    # Wyrm cold tide
    r'records\proxies orient\pools\demon\svc_wyrmhorde_03.dbr',
    r'records\skills\monster skills\attack_melee\gargantuanyeti_freezingbreath.dbr',
    r'records\skills\monster skills\attack_melee\dragonliche_freezingbreath.dbr',
    r'records\skills\monster skills\ondeath\skills\frostnova.dbr',
    r'records\skills\monster skills\attack_radius\ondeath_frostnova.dbr',
    # Broodmother
    r'records\xpack\creatures\monster\sepulchralwyrm\um_broodmother_99.dbr',
    r'records\skills\monster skills\ondeath\ondeath_spawnskeleton.dbr',
    r'records\skills\monster skills\attack_melee\sepulchralwyrm_firebreath.dbr',
    r'records\xpack\creatures\monster\sepulchralwyrm\um_sepulchralwyrm_common_31.dbr',
    # Obsidian Kravmoloch
    r'records\drxmap\proxy\pools\q_obs_warband.dbr',
    r'records\skills\boss skills\yaoguai_summonshadowstalkers.dbr',
])
