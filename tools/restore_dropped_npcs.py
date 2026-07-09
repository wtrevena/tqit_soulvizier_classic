r"""D3 (BUILD30): restore the placed-but-missing SV/SVAERA entity records.

THE GAP THIS CLOSES
-------------------
The shipped merged world map (local/Levels_merged.arc) is built from SVAERA's
Levels.arc (tools/svaera_plus_portals.py). SVAERA's map PLACES 68 entity
instances (67 distinct records) whose .dbr record definitions live ONLY in
SVAERA's database. build_svc_database.py builds the mod arz from SV 0.98i (+ 0.9
/ 0.4.1 + the base game) and NEVER merges SVAERA's database, so those 67 records
are absent from both the mod arz and the base game arz. In-game they SILENTLY
FAIL to spawn (town dyers, the Great Wall vendor row, the Delphi oceanid proxy).
The MAP-REF-1 contract (tools/contracts/contracts_map.py) flags exactly these 68
placements.

WHERE THE RECORDS ACTUALLY LIVE (ground truth, D3 investigation 2026-07-09)
---------------------------------------------------------------------------
NONE of the 67 records exist in upstream/soulvizier_098i|0.9|041 (checked by
exact path, by all_sv<->records prefix swap, and by basename). They are SVAERA
content. The real SVAERA database is NOT in the repo (reference_mods/
SVAERA_customquest/Database/SVAERA_customquest.arz is a 2 KB empty stub); the
only full copy on this machine is the Steam Workshop install:
    C:/Program Files (x86)/Steam/steamapps/workshop/content/475150/
        2076433374/SVAERA_customquest/Database/SVAERA_customquest.arz  (~68 MB)
65 of the 67 placed records resolve there (all under their EXACT placed path -
SVAERA already stores the dyers under records\all_sv\..., so NO prefix remap is
needed). The 2 that do not resolve anywhere are corrupt map references (a stray
leading space after "setdress\\") - the base game holds the correct un-spaced
records, so these are DE-PLACE / whitelist candidates for the MAP lane, not
records to restore here (see DEPLACE_PLACED).

=> This module is SOURCE-AGNOSTIC: it restores whatever placed records it can
   find in the ordered `upstream_dbs` you pass it. For it to actually close the
   gap the caller MUST include the SVAERA database in `upstream_dbs` (SVAERA
   first, then the SV upstreams as closure fallbacks). See restore_dropped_npcs.

WHAT IT IMPORTS
---------------
For every placed record it can source it imports that record AND its full
recursive .dbr reference closure: any record referenced by an imported record
that is absent from BOTH the live db AND the base game arz is itself imported
from `upstream_dbs` (recursively). Placed records are stored under their PLACED
name (so the map reference resolves); closure children keep their own referenced
path. Existing records ALWAYS win (never overwritten). Import preserves field
data types exactly and iterates in sorted order so the build stays byte-
reproducible.

FAIL-LOUD / KNOWN-UNRESOLVABLE
-----------------------------
An unresolvable record (no source in db, base, or any upstream_db) raises
SystemExit UNLESS it is in the documented KNOWN_UNRESOLVABLE allowlist (the 2
corrupt-path placed records + the SVAERA-internal dangling refs SVAERA itself
ships). This fails loud on a NEW / unexpected gap (a real regression) while
tolerating pre-existing upstream data debt - the same leniency the render-chain
/ summon validators apply to upstream SV content.

House rule: no em dashes anywhere.
"""

import os
import sys
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase  # noqa: E402  (type hint + parity with build)

_BS = chr(92)

# The only full copy of the SVAERA database on this machine is the Steam Workshop
# install (see the module docstring). The build's normal SV upstreams cannot
# satisfy any placed record, so D3 sources from here. Override with $SVC_SVAERA_ARZ.
_SVAERA_DEFAULT = (
    r"C:\Program Files (x86)\Steam\steamapps\workshop\content"
    r"\475150\2076433374\SVAERA_customquest\Database\SVAERA_customquest.arz")


def find_svaera_arz():
    """Return the SVAERA_customquest .arz Path (env $SVC_SVAERA_ARZ or the known
    Workshop path), or None if it is not present on this machine."""
    cand = os.environ.get('SVC_SVAERA_ARZ') or _SVAERA_DEFAULT
    p = Path(cand)
    return p if p.is_file() else None


# ---------------------------------------------------------------------------
# MANIFEST - the MAP-REF-1 subjects on the current shipped map.
# Regenerate after any map change with:
#   py tools/contracts/run_contracts.py --only map --arz ... --levels-arc ... \
#       --out viol.json   (then read the MAP-REF-1 subjects)
# ---------------------------------------------------------------------------
# PLACEMENTS: the 67 distinct records MAP-REF-1 flags (placed in the shipped
# world map but absent from the mod arz + base game). value = sorted level(s).
PLACEMENTS = {
    'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_02a_sparta.dbr': ['Levels/World/Greece/Area002/Valley01.LVL'],
    'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_02b_sparta.dbr': ['Levels/World/Greece/Area002/Valley01.LVL'],
    'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_04a_megara.dbr': ['Levels/World/Greece/Area004/CoastalTown01.LVL'],
    'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_04b_megara.dbr': ['Levels/World/Greece/Area004/CoastalTown01.LVL'],
    'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_07a_delphi.dbr': ['Levels/World/Greece/Delphi/DelphiCenter01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_07b_delphi.dbr': ['Levels/World/Greece/Delphi/DelphiCenter01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_10a_athens_.dbr': ['Levels/World/Greece/Athens/AthensCity03.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_10b_athens.dbr': ['Levels/World/Greece/Athens/AthensCity03.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_12a_herakleion.dbr': ['Levels/World/Greece/Knossos/KnossosTownStartA.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\01_greece_dyer_12b_herakleion.dbr': ['Levels/World/Greece/Knossos/KnossosTownStartA.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\02_egypt_dyer_01a_rhakotis.dbr': ['Levels/World/Egypt/Rhakotis/Rhakotis02.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\02_egypt_dyer_01b_rhakotis.dbr': ['Levels/World/Egypt/Rhakotis/Rhakotis02.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\02_egypt_dyer_03a_memphis.dbr': ['Levels/World/Egypt/Memphis/256x256MemphisCityArea.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\02_egypt_dyer_03b_memphis.dbr': ['Levels/World/Egypt/Memphis/256x256MemphisCityArea.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\02_egypt_dyer_06a_thebes.dbr': ['Levels/World/Egypt/Thebes/Thebes02.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\02_egypt_dyer_06b_thebes.dbr': ['Levels/World/Egypt/Thebes/Thebes02.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_02a_babylon-outskirts.dbr': ['Levels/World/Babylon/HangingGardensExit01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_02b_babylon-outskirts.dbr': ['Levels/World/Babylon/HangingGardensExit01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_03a_shangshung-village.dbr': ['Levels/World/Orient/SilkRoad/BaseCampForest02.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_03b_shangshung-village.dbr': ['Levels/World/Orient/SilkRoad/BaseCampForest02.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_06a_village-of-zhidan.dbr': ['Levels/World/Orient/GreatWall/RoadToTown03A.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_06b_village-of-zhidan.dbr': ['Levels/World/Orient/GreatWall/RoadToTown03A.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_07a_changan.dbr': ['Levels/World/Orient/ChangAn/ChangAnCity06.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\03_orient_dyer_07b_changan.dbr': ['Levels/World/Orient/ChangAn/ChangAnCity06.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\04_hades_dyer_01a_rhodes.dbr': ['XPack/Levels/Area01_Rhodes/Rhodes_CityFinal_01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\04_hades_dyer_01b_rhodes.dbr': ['XPack/Levels/Area01_Rhodes/Rhodes_CityFinal_01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\04_hades_dyer_05a_city-of-lost-souls.dbr': ['XPack\\Levels\\Area04_Styx\\Undergrounds\\Styx_CryptUG_StoneTransitionIII01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\04_hades_dyer_05b_city-of-lost-souls.dbr': ['XPack\\Levels\\Area04_Styx\\Undergrounds\\Styx_CryptUG_StoneTransitionIII01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\04_hades_dyer_07a_elysium.dbr': ['XPack\\Levels\\Area06_Elysian\\Elysian_Fields_04.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\04_hades_dyer_07b_elysium.dbr': ['XPack\\Levels\\Area06_Elysian\\Elysian_Fields_04.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\04b_atlantis_dyer_01a_gadir.dbr': ['XPack3\\Levels\\Iberia\\Gadir01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\04b_atlantis_dyer_04a_atlas-mountains.dbr': ['XPack3\\Levels\\Iberia\\AtlasMountains14.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\04b_atlantis_dyer_07a_atlantis-high-district.dbr': ['XPack3\\Levels\\Atlantis\\AtlantisHigh02b.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\04b_atlantis_dyer_08a_tartarus.dbr': ['XPack3\\Levels\\Tartarus\\Underground/TransitionCave01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\04b_atlantis_dyer_08b_tartarus.dbr': ['XPack3\\Levels\\Tartarus\\Underground/TransitionCave01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_01a_corinth.dbr': ['XPack2/Levels/Corinthia/Corinthia.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_01b_corinth.dbr': ['XPack2/Levels/Corinthia/Corinthia.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_03a_heuneburg.dbr': ['XPack2\\Levels\\CelticHeartlands\\HeuneburgOutskirts02.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_03b_heuneburg.dbr': ['XPack2\\Levels\\CelticHeartlands\\HeuneburgOutskirts02.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_05a_glauberg.dbr': ['XPack2\\Levels\\CelticHeartlands\\Glauberg02.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_05b_glauberg.dbr': ['XPack2\\Levels\\CelticHeartlands\\Glauberg02.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_07a_gylfis-settlement.dbr': ['XPack2\\Levels\\Scandia\\KingGylfisSettlement.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_07b_gylfis-settlement.dbr': ['XPack2\\Levels\\Scandia\\KingGylfisSettlement.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_09a_dark-lands.dbr': ['XPack2\\Levels\\DarkLands\\Underground\\MFC01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_09b_dark-lands.dbr': ['XPack2\\Levels\\DarkLands\\Underground\\MFC01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_10a_valholl.dbr': ['XPack2\\Levels\\Asgard\\Underground\\ValhollCave08.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\05_north_dyer_10b_valholl.dbr': ['XPack2\\Levels\\Asgard\\Underground\\ValhollCave08.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_01a_summer-palace.dbr': ['XPack4\\Levels\\Act1\\Underground\\YaoSummerResidence.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_01b_summer-palace.dbr': ['XPack4\\Levels\\Act1\\Underground\\YaoSummerResidence.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_05a_village-of-xiao.dbr': ['XPack4/Levels/Act1/06RiceFields/1_6RiceFields04.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_05b_village-of-xiao.dbr': ['XPack4/Levels/Act1/06RiceFields/1_6RiceFields04.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_06a_pingyang.dbr': ['XPack4/Levels/Act2/01Pingyang/2_1Pingyang05.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_06b_pingyang.dbr': ['XPack4/Levels/Act2/01Pingyang/2_1Pingyang05.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_09a_asyut-encampment.dbr': ['XPack4/Levels/Act3/01TheDunes/3_1TheDunes01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_09b_asyut-encampment.dbr': ['XPack4/Levels/Act3/01TheDunes/3_1TheDunes01.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_13a_thebes.dbr': ['XPack4/Levels/Act3/01TheDunes/3_1TheDunes20.lvl'],
    'records\\all_sv\\creature\\npc\\dyer\\06_east_dyer_13b_thebes.dbr': ['XPack4/Levels/Act3/01TheDunes/3_1TheDunes20.lvl'],
    'records\\creature\\npc\\alchemists\\03_orient_alchemist_greatwall.dbr': ['Levels/World/Orient/GreatWall/RoadToTown03A.lvl'],
    'records\\creature\\npc\\item_breaker\\a03_free_upgrader_greatwall.dbr': ['Levels/World/Orient/GreatWall/RoadToTown03A.lvl'],
    'records\\creature\\npc\\item_upgrader\\a03_unique_upgrader_greatwall.dbr': ['Levels/World/Orient/GreatWall/RoadToTown03A.lvl'],
    'records\\creature\\npc\\soulcollectors\\sc_orient_greatwall_01.dbr': ['Levels/World/Orient/GreatWall/RoadToTown03A.lvl'],
    'records\\creature\\npc\\soulcollectors\\sc_orient_greatwall_02.dbr': ['Levels/World/Orient/GreatWall/RoadToTown03A.lvl'],
    'records\\creature\\npc\\uniquetrader\\03_orient_trader_greatwall.dbr': ['Levels/World/Orient/GreatWall/RoadToTown03A.lvl'],
    'records\\proxies greek\\area005\\ag_magical_oceanid_02n.dbr': ['Levels/World/Greece/Delphi/DelphiLowlands04.lvl'],
    'records\\sceneryorient\\structure\\building\\town\\setdress\\ orienttownsetdresssqbasketveg02.dbr': ['Levels/World/Orient/GreatWall/RoadToTown03A.lvl'],
    'records\\sceneryorient\\structure\\building\\town\\setdress\\ orienttownsetdresstablegroup.dbr': ['Levels/World/Orient/GreatWall/RoadToTown03A.lvl', 'Levels/World/Orient/SilkRoad/HiddenValley01.lvl'],
    'records\\xpack\\creatures\\npc\\enchanter\\enchanter_greatwall.dbr': ['Levels/World/Orient/GreatWall/RoadToTown03A.lvl'],
}

# DEPLACE_PLACED: placed records that resolve in NO source. The map path carries a
# stray leading space after "setdress\\" (a corrupt reference); the base game holds
# the correct un-spaced records
# (records\sceneryorient\...\setdress\orienttownsetdresstablegroup.dbr etc). These
# CANNOT be restored (a space-named record would be a bogus duplicate). They are
# DE-PLACE / whitelist candidates for the MAP lane (fix or drop the placement).
DEPLACE_PLACED = frozenset({
    'records\\sceneryorient\\structure\\building\\town\\setdress\\ orienttownsetdresssqbasketveg02.dbr',
    'records\\sceneryorient\\structure\\building\\town\\setdress\\ orienttownsetdresstablegroup.dbr',
})

# KNOWN_DANGLING_CLOSURE: records referenced from within the restored SVAERA
# closure that resolve in NO available source (mod arz + base game arz + SVAERA +
# SV 0.98i/0.9/0.4.1). These are SVAERA's OWN pre-existing dangling references
# (data debt SVAERA itself ships with) - cosmetic effects, a dev-sandbox effect,
# a sound pak, a hunting skill and formula-item essences that SVAERA never
# defines. They are tolerated (counted, documented) rather than fatal, exactly
# like the render-chain / summon validators tolerate upstream SV data debt.
KNOWN_DANGLING_CLOSURE = frozenset({
    'records\\effects\\combat\\skill_adrenaline_fx01.dbr',
    'records\\effects\\combat\\skill_lethal_strike01.dbr',
    'records\\item\\formulaitems\\f_e_essenceofmakiheraclesmight_a1.dbr',
    'records\\item\\formulaitems\\f_e_essenceofprotectionofsobekra_a2.dbr',
    'records\\item\\formulaitems\\f_l_essenceofmakiheraclesmight_a1.dbr',
    'records\\item\\formulaitems\\f_l_essenceofprotectionofsobekra_a2.dbr',
    'records\\item\\formulaitems\\f_n_essenceofmakiheraclesmight_a1.dbr',
    'records\\item\\formulaitems\\f_n_essenceofprotectionofsobekra_a2.dbr',
    'records\\sandbox\\chris\\unarmedprojectile_fx01.dbr',
    'records\\skills\\hunting\\weaponskill_doubledraw.dbr',
    'records\\sounds\\soundpak\\spells\\nature\\spiritanimalcastpak.dbr',
})

KNOWN_UNRESOLVABLE = DEPLACE_PLACED | KNOWN_DANGLING_CLOSURE


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _norm(s):
    """Normalize a record path / .dbr reference to arz-key form (backslash, lower)."""
    if isinstance(s, bytes):
        s = s.decode('latin-1')
    return s.replace('/', _BS).lower().strip()


def _ensure_record(db, path, template):
    """Create a new empty record if absent (identical to build_svc_database._ensure_record)."""
    if not db.has_record(path):
        db.ensure_string(path)
        db._raw_records[path] = (db.ensure_string(path), b'')
        db._record_types[path] = template
        db._record_timestamps[path] = 0
        db._decoded_cache[path] = OrderedDict()
        db._modified.add(path)


def _template_of(fields):
    """First templateName value from a decoded fields dict (record_type / .tpl)."""
    if not fields:
        return ''
    for key, tf in fields.items():
        if key.split('###')[0] == 'templateName' and tf.values:
            return str(tf.values[0])
    return ''


def _dbr_refs(fields):
    """Every .dbr reference (normalized) held by a decoded fields dict."""
    out = []
    if not fields:
        return out
    for key, tf in fields.items():
        for v in tf.values:
            if isinstance(v, str) and v.strip().lower().endswith('.dbr'):
                out.append(_norm(v))
    return out


def _import_record(db, store_name, src_fields):
    """Import src_fields into db under store_name, preserving dtypes exactly.

    Follows tools/build_svc_database.py._import_base_game_record: create the
    record with its templateName as the record_type, then set every field with
    its ORIGINAL dtype (never let set_field auto-detect - the dtype-preservation
    lesson). Multi-value fields keep their list; single-value fields their scalar.
    """
    template = _template_of(src_fields)
    _ensure_record(db, store_name, template)
    for key, tf in src_fields.items():
        fn = key.split('###')[0]
        vals = list(tf.values) if tf.values else []
        if len(vals) == 1:
            db.set_field(store_name, fn, vals[0], tf.dtype)
        elif len(vals) > 1:
            db.set_field(store_name, fn, vals, tf.dtype)


# ---------------------------------------------------------------------------
# public entry point
# ---------------------------------------------------------------------------
def restore_dropped_npcs(db, upstream_dbs, base_db=None, verbose=True,
                         resource_arc_dir=None, base_game_dir=None, text_arc=None):
    """Restore the placed-but-missing SV/SVAERA records + their .dbr closure.

    Args:
      db            : the live ArzDatabase being built (tools/arz_patcher.py).
      upstream_dbs  : ordered list of source ArzDatabase to pull records from,
                      HIGHEST PRIORITY FIRST. For this map the placed records live
                      in SVAERA, so pass the SVAERA database FIRST, then the SV
                      upstreams (098i, 0.9, 041) as closure fallbacks:
                          [svaera_db, db098i, db09, db041]
                      (The SV upstreams alone CANNOT satisfy any placed record -
                      see the module docstring.)
      base_db       : the base game ArzDatabase. REQUIRED in practice: it is how
                      the closure knows which referenced records already resolve
                      at runtime and must NOT be re-imported. Passing None makes
                      the closure over-import every base-resolvable record; a loud
                      warning is printed.
      verbose       : print the progress + summary.
      resource_arc_dir, base_game_dir, text_arc : optional. If all three are
                      given, the imported records' mesh/texture and name-tag
                      references are validated against the shipped art arcs +
                      Text, and unresolved ones are reported as WARN (never fatal).

    Returns a summary dict. Idempotent and no-op safe (records already present
    are skipped). Raises SystemExit on an UNEXPECTED unresolvable record (one not
    in KNOWN_UNRESOLVABLE) - a real map/data regression that must not ship silent.
    """
    log = (lambda *a: print(*a)) if verbose else (lambda *a: None)
    log("\n=== Restore dropped SV/SVAERA placed records (D3) ===")

    mod_names = set(_norm(n) for n in db.record_names())
    if base_db is not None:
        base_names = set(_norm(n) for n in base_db.record_names())
    else:
        base_names = set()
        log("  WARNING: base_db is None - closure will over-import base-game "
            "records and miscount unresolvables. Pass the base game ArzDatabase.")

    if not upstream_dbs:
        raise SystemExit("restore_dropped_npcs: upstream_dbs is empty; nothing to "
                         "source from (pass the SVAERA database at least).")

    up_maps = [({_norm(n): n for n in d.record_names()}, d) for d in upstream_dbs]

    def find_source(name):
        for m, d in up_maps:
            if name in m:
                return (m[name], d)
        return None

    # ---- Phase A: discovery (order-independent set of records to import) ----
    to_import = {}          # store_name -> (orig_name, src_db)
    deplace = []            # placed records with no source (DE-PLACE candidates)
    dangling = {}           # closure child with no source -> {parents}
    unexpected = {}         # unexpected unresolvable -> {parents} (fail loud)
    worklist = []

    for placed in sorted(PLACEMENTS):
        p = _norm(placed)
        if p in mod_names:
            continue                    # idempotent: already restored / present
        src = find_source(p)
        if src is None:
            deplace.append(p)           # e.g. the corrupt-path setdress records
            continue
        to_import[p] = src
        worklist.append(p)

    processed = set()
    while worklist:
        store = worklist.pop()
        if store in processed:
            continue
        processed.add(store)
        orig, sdb = to_import[store]
        for ref in _dbr_refs(sdb.get_fields(orig)):
            if ref in mod_names or ref in base_names or ref in to_import:
                continue                # already resolves at runtime / queued
            csrc = find_source(ref)
            if csrc is None:
                if ref in KNOWN_DANGLING_CLOSURE:
                    dangling.setdefault(ref, set()).add(store)
                else:
                    unexpected.setdefault(ref, set()).add(store)
                continue
            to_import[ref] = csrc
            worklist.append(ref)

    # ---- fail loud on UNEXPECTED gaps (regressions), not on documented ones ----
    bad_placed = [p for p in deplace if p not in DEPLACE_PLACED]
    if bad_placed:
        raise SystemExit(
            "restore_dropped_npcs: %d placed record(s) have NO source and are not "
            "documented DE-PLACE candidates (map/data regression):\n  %s"
            % (len(bad_placed), "\n  ".join(sorted(bad_placed))))
    if unexpected:
        lines = ["restore_dropped_npcs: %d closure reference(s) resolve in NO source "
                 "and are not in KNOWN_DANGLING_CLOSURE (fail-loud):" % len(unexpected)]
        for r in sorted(unexpected):
            lines.append("  %s   <- e.g. %s" % (r, sorted(unexpected[r])[0]))
        raise SystemExit("\n".join(lines))

    # ---- Phase B: apply in sorted order (byte-reproducible) ----
    imported_placed, imported_children, imported_names = 0, 0, []
    for store in sorted(to_import):
        if db.has_record(store):        # idempotent guard (existing records win)
            continue
        orig, sdb = to_import[store]
        _import_record(db, store, sdb.get_fields(orig))
        imported_names.append(store)
        if store in {_norm(x) for x in PLACEMENTS}:
            imported_placed += 1
        else:
            imported_children += 1

    # ---- optional art/tag validation of the imported records ----
    art_warns, tag_warns = [], []
    if resource_arc_dir and base_game_dir and text_arc:
        art_warns, tag_warns = _validate_art_tags(
            db, imported_names, resource_arc_dir, base_game_dir, text_arc, log)
    elif verbose:
        log("  (art/tag validation skipped - pass resource_arc_dir + base_game_dir "
            "+ text_arc to enable)")

    K = len(deplace) + len(dangling)
    log("\n  --- restore summary ---")
    log("  N placed records restored : %d  (of %d flagged; %d unresolvable placed)"
        % (imported_placed, len(PLACEMENTS), len(deplace)))
    log("  M closure children imported: %d" % imported_children)
    log("  total records imported     : %d" % len(imported_names))
    log("  K unresolvable             : %d  (%d corrupt-path placed + %d SVAERA "
        "dangling closure refs; all documented)" % (K, len(deplace), len(dangling)))
    if deplace:
        log("    DE-PLACE candidates (map lane):")
        for p in sorted(deplace):
            log("      %s  @ %s" % (p, ", ".join(PLACEMENTS.get(_orig_key(p), ['?']))))
    if dangling:
        log("    SVAERA-internal dangling closure refs (tolerated):")
        for r in sorted(dangling):
            log("      %s" % r)
    if art_warns or tag_warns:
        log("  WARN art/tag unresolved: %d mesh/texture, %d name-tag"
            % (len(art_warns), len(tag_warns)))

    return {
        'placed_restored': imported_placed,
        'closure_children': imported_children,
        'total_imported': len(imported_names),
        'unresolvable': K,
        'deplace': sorted(deplace),
        'dangling': sorted(dangling),
        'art_warns': art_warns,
        'tag_warns': tag_warns,
        'imported_names': imported_names,
    }


def _orig_key(norm_name):
    """Map a normalized placed name back to its PLACEMENTS key (for reporting)."""
    for k in PLACEMENTS:
        if _norm(k) == norm_name:
            return k
    return norm_name


# ---------------------------------------------------------------------------
# optional: art + name-tag resolution of the imported records
# (mirrors tools/validate_render_chain.py's arc-resolution conventions; read-only)
# ---------------------------------------------------------------------------
def _validate_art_tags(db, imported_names, resource_arc_dir, base_game_dir, text_arc, log):
    """Report imported records whose mesh/texture refs miss the shipped arcs, or
    whose name tag misses Text. Returns (art_warns, tag_warns). Never fatal."""
    from arc_patcher import ArcArchive

    game = Path(base_game_dir)
    roots = [Path(resource_arc_dir), game / 'Resources', game / 'Resources' / 'XPack',
             game / 'Resources' / 'XPack2', game / 'Resources' / 'XPack3',
             game / 'Resources' / 'XPack4']
    roots = [r for r in roots if r.is_dir()]
    _arc_cache = {}

    def arc_index(archive):
        key = archive.lower()
        if key in _arc_cache:
            return _arc_cache[key]
        names = set()
        for root in roots:
            cand = root / (archive + '.arc')
            if not cand.exists():
                hits = [p for p in root.glob('*.arc') if p.stem.lower() == key]
                cand = hits[0] if hits else None
            if cand and cand.exists():
                try:
                    arc = ArcArchive.from_file(cand)
                except Exception:
                    continue
                for e in arc.entries:
                    if e.name:
                        names.add(e.name.lower().replace('\\', '/'))
        _arc_cache[key] = names
        return names

    def art_resolves(ref):
        parts = str(ref).replace('/', '\\').split('\\')
        if len(parts) < 2:
            return False
        if parts[0].lower() in ('xpack', 'xpack2', 'xpack3', 'xpack4') and len(parts) >= 3:
            if '/'.join(parts[2:]).lower() in arc_index(parts[1]):
                return True
        return '/'.join(parts[1:]).lower() in arc_index(parts[0])

    text_keys = _load_text_keys(text_arc, game)

    art_warns, tag_warns = [], []
    art_ext = ('.msh', '.tex', '.anm')
    for name in imported_names:
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            fn = key.split('###')[0]
            for v in tf.values:
                if not isinstance(v, str) or not v.strip():
                    continue
                low = v.strip().lower()
                if low.endswith(art_ext):
                    if not art_resolves(v):
                        art_warns.append((name, fn, v))
                elif fn.lower() == 'description' and (low.startswith('tag') or low.startswith('xtag')):
                    if v.strip() not in text_keys:
                        tag_warns.append((name, fn, v))
    for w in sorted(set(art_warns))[:40]:
        log("    WARN[mesh/tex] %s :: %s -> %s" % w)
    for w in sorted(set(tag_warns))[:40]:
        log("    WARN[name-tag] %s :: %s -> %s" % w)
    return sorted(set(art_warns)), sorted(set(tag_warns))


def _load_text_keys(text_arc, game_dir):
    """Union of key= names across the mod Text.arc + base game Text_EN.arc."""
    from arc_patcher import ArcArchive
    keys = set()
    cands = [Path(text_arc)]
    bt = Path(game_dir) / 'Text' / 'Text_EN.arc'
    if bt.exists():
        cands.append(bt)
    for path in cands:
        if not path.is_file():
            continue
        try:
            arc = ArcArchive.from_file(path)
        except Exception:
            continue
        for e in arc.entries:
            if not (e.name and e.name.lower().endswith('.txt')):
                continue
            raw = arc.decompress(e)
            if raw[:2] == b'\xff\xfe':
                txt = raw[2:].decode('utf-16-le', 'replace')
            elif raw[:3] == b'\xef\xbb\xbf':
                txt = raw[3:].decode('utf-8', 'replace')
            else:
                txt = raw.decode('utf-8', 'replace')
            for line in txt.split('\n'):
                line = line.strip('\r').strip()
                if not line or line.startswith('//') or '=' not in line:
                    continue
                keys.add(line.partition('=')[0].strip())
    return keys
