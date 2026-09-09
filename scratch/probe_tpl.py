"""Extract the UI template definitions + prove the base game NEVER uses BitmapSingle
for a SkillPaneCtrl.skillPaneBaseBitmap. Read-only."""
import sys
from pathlib import Path
TOOLS = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\tools")
sys.path.insert(0, str(TOOLS))
from arc_patcher import ArcArchive
from arz_patcher import ArzDatabase

TARC = Path(r"C:\Program Files (x86)\Steam\steamapps\common"
            r"\Titan Quest Anniversary Edition\Toolset\Templates.arc")
arc = ArcArchive.from_file(TARC)
names = [e.name for e in arc.entries if e.entry_type == 3]
want = ["bitmapuiaware", "bitmapsingle", "skillpanectrl"]
for w in want:
    hit = [n for n in names if w in n.lower()]
    for h in hit:
        data = arc.get_file(h)
        txt = data.decode("utf-16-le", errors="replace") if data[:2]==b"\xff\xfe" else data.decode("utf-8", errors="replace")
        print("\n########## %s (%d bytes) ##########" % (h, len(data)))
        # print variable names + a few key attrs
        import re
        for m in re.finditer(r'name\s*=\s*"([^"]+)"[^\n]*', txt):
            pass
        # crude: print lines mentioning bitmap/name/class/type
        for line in txt.splitlines():
            ls = line.strip()
            if any(k in ls.lower() for k in ("bitmapname", 'name = "bitmap', "variable", "<group", "class", "defaultvalue", "description")):
                if len(ls) < 200:
                    print("   ", ls)

# base game: any BitmapSingle referenced as a skill pane base bitmap?
print("\n\n===== base game: templates of every SkillPaneCtrl.skillPaneBaseBitmap target =====")
BASE = Path(r"C:\Program Files (x86)\Steam\steamapps\common"
            r"\Titan Quest Anniversary Edition\Database\database.arz")
bdb = ArzDatabase.from_arz(BASE)
BI = {n.lower().replace("/", "\\"): n for n in bdb.record_names()}
def gv(r, f):
    v = bdb.get_field_value(r, f); return v[0] if isinstance(v, list) else v
tmpl_counts = {}
n_ctrl = 0
for low, real in BI.items():
    if not low.endswith("panectrl.dbr"):
        continue
    tn = gv(real, "templateName") or ""
    if "skillpanectrl" not in tn.lower():
        continue
    n_ctrl += 1
    for field in ("skillPaneBaseBitmap", "skillPaneBaseReallocationBitmap"):
        tgt = gv(real, field)
        tgt = tgt[0] if isinstance(tgt, list) else tgt
        if not tgt: continue
        tr = BI.get(str(tgt).lower().replace("/", "\\"))
        tt = (gv(tr, "templateName") if tr else "<missing>") or "<none>"
        tt = str(tt).rsplit("\\",1)[-1]
        tmpl_counts[tt] = tmpl_counts.get(tt, 0) + 1
print("base SkillPaneCtrl records:", n_ctrl)
print("templates used by their skillPaneBaseBitmap / reallocation targets:")
for t, c in sorted(tmpl_counts.items()):
    print("   %-24s x%d" % (t, c))
