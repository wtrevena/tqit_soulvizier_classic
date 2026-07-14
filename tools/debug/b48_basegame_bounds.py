"""b48: mine the BASE GAME quests for the engine-proven boat-dialog trigger bounds.

For every base/xpack .qst: parse into steps->triggers. Report:
  - max Action_BoatDialog actions in a SINGLE trigger (actions-per-boat-trigger bound)
  - max OnLevelLoad triggers in a SINGLE step (per-step OnLevelLoad bound)
  - any step that hosts multiple boat-dialog triggers (proves multi-trigger boat steps)
This tells us whether the fix should be 1-trigger-many-actions or few-triggers.
"""
import sys, struct
from pathlib import Path
from collections import Counter
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
import qst_format as qf
from arc_patcher import ArcArchive

BASE = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Resources")
ARCS = [BASE/"Quests.arc", BASE/"xpack"/"Quests.arc", BASE/"XPack2"/"Quests.arc",
        BASE/"XPack3"/"Quests.arc", BASE/"XPack4"/"Quests.arc"]

def blocks(items): return [it[1] for it in items if it[0]=="block"]
def fields(items):
    d={}
    for it in items:
        if it[0]=="field": d[it[1]]=it[2]
    return d

def parse_entries(container_items):
    out=[]; pend=None
    for it in container_items:
        if it[0]=="field" and it[1] in ("conditionClassName","actionClassName"):
            pend=it[2][1]
        elif it[0]=="block" and pend is not None:
            out.append(pend); pend=None
    return out

def analyze_qst(data):
    """Return (max_boat_actions_in_a_trigger, max_onlevelload_triggers_in_a_step,
               max_boat_triggers_in_a_step)."""
    try:
        tree=qf.parse(data)
    except Exception:
        return (0,0,0,0)
    if len(tree)<2: return (0,0,0,0)
    steps=tree[1]; sbl=blocks(steps)
    max_boat_act=0; max_oll_step=0; max_boat_trig_step=0; total_boat_trig=0
    n=len(sbl)//3
    for s in range(n):
        cont=sbl[3*s+1] if 3*s+1<len(sbl) else None
        if cont is None: continue
        cf=fields(cont)
        if "max" not in cf: continue
        cbl=blocks(cont)
        # triples: header, conditions, actions
        oll_in_step=0; boat_trig_in_step=0
        i=0
        while i+2 < len(cbl)+1 and i+2 <= len(cbl):
            if i+2>len(cbl): break
            cond_b=cbl[i+1] if i+1<len(cbl) else None
            act_b=cbl[i+2] if i+2<len(cbl) else None
            if cond_b is None or act_b is None: break
            conds=parse_entries(cond_b)
            acts=parse_entries(act_b)
            if "Condition_OnLevelLoad" in conds: oll_in_step+=1
            nboat=sum(1 for a in acts if a=="Action_BoatDialog")
            if nboat>0:
                boat_trig_in_step+=1; total_boat_trig+=1
                max_boat_act=max(max_boat_act,nboat)
            i+=3
        max_oll_step=max(max_oll_step,oll_in_step)
        max_boat_trig_step=max(max_boat_trig_step,boat_trig_in_step)
    return (max_boat_act,max_oll_step,max_boat_trig_step,total_boat_trig)

glob_maxboat=0; glob_maxoll=0; glob_maxboattrig=0
best_boat=None; best_oll=None; best_boattrig=None
nqst=0
for arc_path in ARCS:
    if not arc_path.exists(): continue
    arc=ArcArchive.from_file(arc_path)
    for e in arc.entries:
        if not e.name.lower().endswith(".qst"): continue
        data=arc.get_file(e.name)
        if not data: continue
        nqst+=1
        mb,mo,mbt,tot=analyze_qst(data)
        if mb>glob_maxboat: glob_maxboat=mb; best_boat=(arc_path.parent.name+"/"+e.name,mb)
        if mo>glob_maxoll: glob_maxoll=mo; best_oll=(arc_path.parent.name+"/"+e.name,mo)
        if mbt>glob_maxboattrig: glob_maxboattrig=mbt; best_boattrig=(arc_path.parent.name+"/"+e.name,mbt,tot)

print(f"scanned {nqst} base/xpack .qst files")
print(f"MAX Action_BoatDialog actions in a SINGLE trigger: {glob_maxboat}   e.g. {best_boat}")
print(f"MAX Condition_OnLevelLoad triggers in a SINGLE step: {glob_maxoll}   e.g. {best_oll}")
print(f"MAX boat-dialog TRIGGERS in a SINGLE step: {glob_maxboattrig}   e.g. {best_boattrig}")
