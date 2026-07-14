"""b48: DRY-RUN the patched hub-quest chain on the pristine SVAERA base sv_commonmechanics.qst.

Verifies my build_quest_files edit:
  - the full chain applies without exception (round-trip stable + delta asserts pass)
  - svc_testhub_master is referenced 0x (dead 7-port master dropped)
  - svc_testhub_return present (2 ports), all 11 travelers + 6 returns present
  - total boat offers dropped 30 -> 23 (the 7 dead master offers gone)
NO build, NO write to any arc - pure in-memory patch of a copied base blob.
"""
import sys, struct
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
import qst_format as qf
from arc_patcher import ArcArchive
import build_quest_files as bqf

# reference_mods is gitignored (not vendored into linked worktrees) - read from the main repo.
BASE_ARC = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\reference_mods"
                r"\SVAERA_customquest\Resources\Quests.arc")

def count_boat(data):
    tree = qf.parse(data)
    def walk(items, acc):
        pend = None
        for it in items:
            if it[0] == "field" and it[1] == "actionClassName":
                pend = it[2][1]
            elif it[0] == "block":
                if pend == "Action_BoatDialog":
                    d = {x[1]: (x[2][1]) for x in it[1] if x[0]=="field"}
                    acc.append(d.get("npc","").lower())
                pend = None
                walk(it[1], acc)
    acc = []
    for b in tree:
        walk(b, acc)
    return acc

arc = ArcArchive.from_file(BASE_ARC)
base = arc.get_file("sv_commonmechanics.qst")
if base is None:
    for e in arc.entries:
        if e.name.lower().endswith("sv_commonmechanics.qst"):
            base = arc.decompress(e); break
print(f"base sv_commonmechanics.qst: {len(base)} bytes, base boat offers: {len(count_boat(base))}")

# apply the PATCHED chain
p = bqf._add_helos_portal_travel(base)
p = bqf._add_testhub_portal_travel(p)      # <-- my fix: master dropped, return kept
p = bqf._add_helos_traveler_hub_travel(p)

# round-trip stability
assert qf.serialize(qf.parse(p)) == p, "round-trip NOT stable"

offers = count_boat(p)
from collections import Counter
c = Counter(offers)
print(f"patched boat offers: {len(offers)}  (expected 23 = 4 portal + 2 return + 17 hub)")
print("per-NPC offer counts:")
for npc, n in sorted(c.items()):
    print(f"    {n:>2}  {npc.split(chr(92))[-1]}")

# assertions
tm = sum(v for k,v in c.items() if "svc_testhub_master" in k)
tr = c.get(r"records\quests\svc_testhub_return.dbr", 0)
sparta = c.get(r"records\quests\svc_helos_trav_sparta.dbr", 0)
travelers = sum(1 for k in c if "svc_helos_trav_" in k)
returns = sum(1 for k in c if "svc_area_return_" in k)
print("\nASSERTIONS:")
print(f"  svc_testhub_master offers = {tm}  (expect 0 - dead master dropped)  {'OK' if tm==0 else 'FAIL'}")
print(f"  svc_testhub_return offers = {tr}  (expect 2)                        {'OK' if tr==2 else 'FAIL'}")
print(f"  svc_helos_trav_sparta     = {sparta}  (expect 1)                    {'OK' if sparta==1 else 'FAIL'}")
print(f"  distinct travelers        = {travelers}  (expect 11)               {'OK' if travelers==11 else 'FAIL'}")
print(f"  distinct area returns     = {returns}  (expect 6)                  {'OK' if returns==6 else 'FAIL'}")
print(f"  total offers              = {len(offers)}  (expect 23; was 30)     {'OK' if len(offers)==23 else 'FAIL'}")
ok = tm==0 and tr==2 and sparta==1 and travelers==11 and returns==6 and len(offers)==23
print("\nDRY-RUN " + ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
