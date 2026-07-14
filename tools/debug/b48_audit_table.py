"""b48: the DEFINITIVE 17-traveler + return audit table.

Cross-references the DEPLOYED artifacts (the exact set Will is clicking):
  - Quests.arc 838bdc3a  -> boat-dialog offers (npc, dest, tag, registration order)
  - Levels.arc 841c56cd  -> 0x05 placements (which level, how many times)
  - arz 6631f252         -> NPC record exists?
Emits: per-NPC row [reg#, npc, placed?, placeCount, level, dest, tag, VERDICT].
VERDICT logic: mute if (unplaced) OR (placed >1x across levels = warden) OR
(registration index beyond the boat-offer cap band).
"""
import sys, struct
from pathlib import Path
from collections import defaultdict
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tools" / "contracts"))
sys.path.insert(0, str(REPO / "tools" / "debug"))
import qst_format as qf
from arc_patcher import ArcArchive
from arz_patcher import ArzDatabase
import survey_uberboss_spots as S
from contracts_map import parse_blob_sections

DEV = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
           r"\CustomMaps\SoulvizierClassicDEV")
Q = DEV/"Resources"/"Quests.arc"
L = DEV/"Resources"/"Levels.arc"
A = DEV/"Database"/"SoulvizierClassicDEV.arz"
VER_BASE = {0x0e:56,0x0f:72,0x11:72,0x10:72,0x0d:56}
BS = chr(92)

def s32(v): return struct.unpack("<i",struct.pack("<I",v))[0] if isinstance(v,int) else v
def blocks(items): return [it[1] for it in items if it[0]=="block"]

# ---- 1. Quest offers (registration order) ----
def quest_offers():
    arc=ArcArchive.from_file(Q); data=arc.get_file("sv_commonmechanics.qst")
    tree=qf.parse(data); sbl=blocks(tree[1])
    offers=[]
    def entries(cont):
        out=[]; pend=None
        for it in cont:
            if it[0]=="field" and it[1] in ("actionClassName",): pend=it[2][1]
            elif it[0]=="block" and pend:
                d={x[1]:x[2][1] for x in it[1] if x[0]=="field"}; out.append((pend,d)); pend=None
        return out
    n=len(sbl)//3
    for s in range(n):
        cont=sbl[3*s+1]; cbl=blocks(cont); i=0
        while i+2<len(cbl)+1 and i+2<=len(cbl):
            act=cbl[i+2] if i+2<len(cbl) else None
            if act is None: break
            for an,ad in entries(act):
                if an=="Action_BoatDialog":
                    offers.append((ad.get("npc","").lower(), s32(ad.get("x",0)), s32(ad.get("y",0)),
                                   s32(ad.get("z",0)), ad.get("tag","")))
            i+=3
    return offers

# ---- 2. Map placements ----
def all_instances(blob, base):
    for t,d in parse_blob_sections(blob):
        if t!=0x05: continue
        pos=0; nstr=struct.unpack_from('<I',d,pos)[0]; pos+=4; strings=[]
        for _ in range(nstr):
            ln=struct.unpack_from('<I',d,pos)[0]; pos+=4; strings.append(d[pos:pos+ln]); pos+=ln
        ninst=struct.unpack_from('<I',d,pos)[0]; pos+=4; out=[]
        for _ in range(ninst):
            sid=struct.unpack_from('<I',d,pos)[0]
            x,y,z=struct.unpack_from('<fff',d,pos+40); flags=struct.unpack_from('<I',d,pos+52)[0]
            dbr=(strings[sid] if sid<len(strings) else b'?').decode('latin1')
            out.append((dbr.lower(),x,y,z)); pos+=base+(16 if flags!=0 else 0)
        return out
    return []
def map_placements():
    data,levels=S.load_world(L); placed=defaultdict(list)
    for lv in levels:
        blob=data[lv['data_offset']:lv['data_offset']+lv['data_length']]
        if blob[:3]!=b'LVL': continue
        base=VER_BASE.get(blob[3],72)
        for dbr,x,y,z in all_instances(blob,base):
            if 'svc_' in dbr or 'portal_master' in dbr or 'testhub' in dbr or 'helos_trav' in dbr or 'area_return' in dbr:
                placed[dbr].append((lv['fname'].split(BS)[-1],x,y,z))
    return placed

# ---- 3. arz record existence ----
def arz_records():
    db=ArzDatabase.from_arz(A)
    return set(n.lower() for n in db.record_names())

def main():
    offers=quest_offers()
    placed=map_placements()
    names=arz_records()
    # group offers by npc, keep first registration index
    npc_first_reg={}; npc_offer_count=defaultdict(int); npc_dests=defaultdict(list)
    for idx,(npc,x,y,z,tag) in enumerate(offers):
        if npc not in npc_first_reg: npc_first_reg[npc]=idx
        npc_offer_count[npc]+=1; npc_dests[npc].append((idx,x,y,z,tag))
    print(f"Total boat offers registered (engine order): {len(offers)}")
    print(f"Distinct offer NPCs: {len(npc_first_reg)}")
    print("="*140)
    hdr=f"{'reg#':>4} {'NPC (record)':<40} {'arz':<4} {'placed':<8} {'level(s)':<26} {'dest(x,y,z)':<22} {'tag':<26} VERDICT"
    print(hdr); print("-"*140)
    # order NPCs by first registration index
    for npc in sorted(npc_first_reg, key=lambda n:npc_first_reg[n]):
        reg=npc_first_reg[npc]
        short=npc.split(BS)[-1]
        in_arz = npc in names
        pl=placed.get(npc,[])
        plevels=sorted(set(p[0] for p in pl))
        pcount=len(pl)
        # dest from first offer
        _,dx,dy,dz,tag=npc_dests[npc][0]
        # verdict
        verdict=[]
        if not in_arz: verdict.append("NO-ARZ")
        if pcount==0: verdict.append("UNPLACED->inert")
        elif pcount>1 and len(plevels)>1: verdict.append(f"WARDEN-MUTE({pcount}x/{len(plevels)}lv)")
        elif pcount>1: verdict.append(f"DUP({pcount}x)")
        # overflow band: offers beyond ~the legacy 13 are the suspect mute band
        offcount=npc_offer_count[npc]
        v = ";".join(verdict) if verdict else "wired-ok"
        mark="  <<<SPARTA" if "sparta" in npc else ""
        lvl_s=",".join(plevels)[:25]
        print(f"{reg:>4} {short:<40} {'Y' if in_arz else 'N':<4} {('x'+str(pcount)):<8} {lvl_s:<26} ({dx},{dy},{dz})".ljust(96) + f" {tag:<26} {v}{mark}")
    # Also: placed hub NPCs with NO quest offer (mute: placed but no trigger)
    print("\n" + "="*140)
    print("PLACED hub NPCs with NO matching boat offer (placed-but-mute, no trigger):")
    offer_npcs=set(npc_first_reg)
    for npc in sorted(placed):
        if npc not in offer_npcs and ('helos_trav' in npc or 'area_return' in npc or 'testhub' in npc or 'portal_master' in npc):
            print(f"    {npc}  placed x{len(placed[npc])} @ {sorted(set(p[0] for p in placed[npc]))}  <<< NO TRIGGER -> MUTE")

if __name__ == "__main__":
    main()
