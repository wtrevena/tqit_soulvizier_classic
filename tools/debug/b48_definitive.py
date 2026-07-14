"""b48 DEFINITIVE: every boat-dialog in deployed sv_commonmechanics.qst, in engine order.

Correct encoding (confirmed by raw dump):
  actions block items = [field actionCount, (field actionClassName, block detail)*N]
  conditions block    = [field conditionCount, (field conditionClassName, block detail)*N]
Walk raw items IN ORDER (do not dict-collapse repeated className keys).
For each trigger (header, conditions, actions triple inside a step's trigger container):
  list every Action_BoatDialog: npc, dest(x,y,z signed), tag  -> the travel offer.
"""
import sys, struct
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
import qst_format as qf
from arc_patcher import ArcArchive

DEP = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
           r"\CustomMaps\SoulvizierClassicDEV\Resources\Quests.arc")

def s32(v):
    return struct.unpack("<i", struct.pack("<I", v))[0] if isinstance(v, int) else v

def blocks(items):
    return [it[1] for it in items if it[0] == "block"]

def detail_of(block_items):
    d = {}
    for it in block_items:
        if it[0] == "field":
            d[it[1]] = it[2][1]
    return d

def parse_entries(container_items):
    """Return ordered list of (className, detail_dict) from a conditions/actions block."""
    out = []
    pending_name = None
    for it in container_items:
        if it[0] == "field" and it[1] in ("conditionClassName", "actionClassName"):
            pending_name = it[2][1]
        elif it[0] == "block":
            if pending_name is not None:
                out.append((pending_name, detail_of(it[1])))
                pending_name = None
    return out

def header_of(block_items):
    d = {}
    for it in block_items:
        if it[0] == "field":
            d[it[1]] = it[2][1]
    return d

arc = ArcArchive.from_file(DEP)
data = arc.get_file("sv_commonmechanics.qst")
tree = qf.parse(data)
steps_items = tree[1]
sbl = blocks(steps_items)  # 1101 blocks: [StepDef, Container, Sentinel] * 367

# Walk step-triples
boat_offers = []   # global order list of (npc, x,y,z, tag, step_num, trig_num, act_num)
trigger_rows = []  # (step_num, trig_num, isActive, cond_summary, boat_list, act_names)

n_steps = len(sbl) // 3
for s in range(n_steps):
    stepdef = sbl[3*s]
    container = sbl[3*s + 1]
    citems = container[1] if isinstance(container, tuple) else container
    # container is a block's items? sbl entries are the items-lists already (blocks() returns it[1])
    citems = container
    # trigger container children: header, conditions, actions triples
    cbl = blocks(citems)
    # group into triples
    t = 0
    idx = 0
    while idx + 2 < len(cbl) + 1 and idx < len(cbl):
        # expect header, conditions, actions
        header = cbl[idx]
        if idx+2 >= len(cbl):
            break
        cond_block = cbl[idx+1]
        act_block = cbl[idx+2]
        hdr = header_of(header)
        conds = parse_entries(cond_block)
        acts = parse_entries(act_block)
        # sanity: conditions block must have started with conditionCount, actions with actionCount
        boat = [(nm, d) for nm, d in acts if nm == "Action_BoatDialog"]
        for an, ad in boat:
            boat_offers.append(dict(
                step=s, trig=t, npc=ad.get("npc",""),
                x=s32(ad.get("x",0)), y=s32(ad.get("y",0)), z=s32(ad.get("z",0)),
                tag=ad.get("tag",""), onOff=ad.get("onOff")))
        cond_names = [c[0] for c in conds]
        cond_tokens = [d.get("tokenName") for _n,d in conds if "tokenName" in d]
        if boat or "Action_BoatDialog" in [a[0] for a in acts]:
            trigger_rows.append(dict(step=s, trig=t, isActive=hdr.get("isActive"),
                                     disp=hdr.get("displayTag",""),
                                     conds=cond_names, tokens=cond_tokens,
                                     nboat=len(boat), boat=boat))
        t += 1
        idx += 3

print(f"steps={n_steps}  total boat offers={len(boat_offers)}")
print("="*140)
# Group offers by NPC
from collections import defaultdict, OrderedDict
by_npc = OrderedDict()
for o in boat_offers:
    by_npc.setdefault(o["npc"], []).append(o)
print(f"Distinct boat-dialog NPCs: {len(by_npc)}")
for npc, offers in by_npc.items():
    print(f"\nNPC: {npc}   ({len(offers)} offers stacked)")
    for o in offers:
        mark = "  <<<< SPARTA" if "sparta" in o["tag"].lower() else ""
        print(f"    step{o['step']} trig{o['trig']}  tag={o['tag']:<28} dest=({o['x']:>6},{o['y']:>4},{o['z']:>7}) onOff={o['onOff']}{mark}")

print("\n" + "="*140)
print("ENGINE-ORDER list of all boat offers (global registration order):")
for k, o in enumerate(boat_offers):
    mark = "  <<<< SPARTA" if "sparta" in o["tag"].lower() else ""
    npc_short = o["npc"].split("\\")[-1]
    print(f"  #{k:>2} step{o['step']} T{o['trig']:>2}  npc={npc_short:<34} tag={o['tag']:<28} dest=({o['x']:>6},{o['y']:>4},{o['z']:>7}){mark}")
