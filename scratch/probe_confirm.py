"""Corroborate the BitmapSingle-vs-BitmapUIAware template downgrade across ALL 9
masteries (base + reallocation background records), and check upstream sources +
controller-variant resolution. Read-only."""
import sys
from pathlib import Path
TOOLS = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\tools")
sys.path.insert(0, str(TOOLS))
from arz_patcher import ArzDatabase
from arc_patcher import ArcArchive

MOD = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
           r"\CustomMaps\SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz")
BASE = Path(r"C:\Program Files (x86)\Steam\steamapps\common"
            r"\Titan Quest Anniversary Edition\Database\database.arz")
UP_SV = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Database\database.arz")
UP_AERA = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Database\SVAERA.arz")
INGAMEUI_ARC = Path(r"C:\Program Files (x86)\Steam\steamapps\common"
                    r"\Titan Quest Anniversary Edition\Resources\InGameUI.arc")

def load(p):
    if not p.exists():
        print("  (missing: %s)" % p); return None
    db = ArzDatabase.from_arz(p)
    return db, {n.lower().replace("/", "\\"): n for n in db.record_names()}

def tmpl(dbpair, name):
    if dbpair is None: return None
    db, idx = dbpair
    r = idx.get(name.lower().replace("/", "\\"))
    if not r: return "<absent>"
    t = db.get_field_value(r, "templateName")
    t = (t[0] if isinstance(t, list) else t) or ""
    return t.rsplit("\\", 1)[-1]

print("loading arzs ...")
mod = load(MOD); base = load(BASE)
sv = load(UP_SV) if UP_SV.exists() else None
aera = None
for cand in [UP_AERA,
             Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\database\SVAERA.arz")]:
    if cand.exists():
        aera = load(cand); break

FOLDERS = {1: r"records\ingameui\player skills\mastery 1",
           2: r"records\ingameui\player skills\mastery 2",
           3: r"records\ingameui\player skills\mastery 3",
           4: r"records\ingameui\player skills\mastery 4",
           5: r"records\ingameui\player skills\mastery 5",
           6: r"records\ingameui\player skills\mastery 6",
           7: r"records\ingameui\player skills\mastery 7",
           8: r"records\ingameui\player skills\mastery 8",
           9: r"records\xpack\ui\skills\mastery 9"}

print("\n== template per mastery bg record (MOD | BASE | SV098i | SVAERA) ==")
downgraded = 0
for slot, folder in FOLDERS.items():
    for suf in ("skillpanebasebitmap.dbr", "skillpanereallocationbitmap.dbr"):
        name = folder + "\\" + suf
        mt = tmpl(mod, name); bt = tmpl(base, name)
        st = tmpl(sv, name) if sv else "-"
        at = tmpl(aera, name) if aera else "-"
        flag = ""
        if mt == "BitmapSingle.tpl" and bt == "BitmapUIAware.tpl":
            flag = "  <<< DOWNGRADED"; downgraded += 1
        print("  m%d %-32s MOD=%-18s BASE=%-18s SV=%-18s AERA=%-18s%s"
              % (slot, suf, mt, bt, st, at, flag))
print("\nDOWNGRADED (BitmapSingle where base is BitmapUIAware):", downgraded, "/ 18")

# resolve the base game's bitmapNames entries (mouse + controller variants)
print("\n== does base InGameUI.arc carry both mouse + controller bg variants? ==")
arc = ArcArchive.from_file(INGAMEUI_ARC)
entries = set(e.name.lower().replace("/", "\\") for e in arc.entries if e.entry_type == 3)
for p in [r"skills\warfareskillbackground01.tex",
          r"controller\skills\warfareskillbackground01.tex",
          r"skills\warfareskillreallocationbackground01.tex",
          r"controller\skills\warfareskillreallocationbackground01.tex",
          r"skills\stealthskillbackground01.tex",
          r"controller\skills\stealthskillbackground01.tex"]:
    print("   %-58s %s" % (p, "PRESENT" if p in entries else "*** ABSENT ***"))
