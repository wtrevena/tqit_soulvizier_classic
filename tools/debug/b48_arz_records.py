"""b48: compare deployed-arz NPC records for the hub travelers vs donor vs legacy.

Dumps 'talk/clickable'-relevant fields for:
  svc_helos_trav_sparta (mute), svc_helos_trav_garden (sibling),
  portal_master_helos (legacy multi-menu), knossos_boatmantoegypt (donor).
Then checks EVERY svc_helos_trav_* / svc_area_return_* record exists in the arz.
"""
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
from arz_patcher import ArzDatabase

DEP_ARZ = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
               r"\CustomMaps\SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz")

INTEREST = [
    r"records\quests\svc_helos_trav_sparta.dbr",
    r"records\quests\svc_helos_trav_garden.dbr",
    r"records\quests\svc_helos_trav_secret.dbr",
    r"records\quests\portal_master_helos.dbr",
    r"records\quests\svc_testhub_master.dbr",
    r"records\quests\svc_testhub_return.dbr",
    r"records\creature\npc\speaking\greece\knossos_boatmantoegypt.dbr",
]
# fields relevant to "is this a clickable/talk NPC + boat capable"
KEYS = ["Class", "description", "FileDescription", "messageDialogTag",
        "chatGreeting", "conversation", "monsterName", "isBoat", "questGiver",
        "characterRacialProfile", "actorMeshRadius", "characterImpetusValue"]

def main():
    db = ArzDatabase.from_arz(DEP_ARZ)
    names = set(n.lower() for n in db.record_names())
    print("="*100)
    for rec in INTEREST:
        f = db.get_fields(rec)
        if f is None:
            print(f"\n{rec}\n  <<< NOT IN ARZ >>>")
            continue
        print(f"\n{rec}")
        allkeys = list(f.keys())
        # print the interesting ones present + anything with 'dialog'/'chat'/'convers'/'boat'
        shown = set()
        for k in KEYS:
            if k in f:
                print(f"    {k:28s} = {f[k].value}")
                shown.add(k)
        for k in allkeys:
            kl = k.lower()
            if k in shown: continue
            if any(s in kl for s in ("dialog","chat","convers","boat","speak","greet","talk")):
                print(f"    {k:28s} = {f[k].value}")
    # roster presence
    print("\n" + "="*100)
    print("ROSTER presence in deployed arz:")
    roster = [f"records\\quests\\svc_helos_trav_{a}.dbr" for a in
              ("garden","secret","sparta","uber","bossarena","warband","dorus","tantalus","charon","mnemophage","ephialtes")]
    roster += [f"records\\quests\\svc_area_return_{a}.dbr" for a in
               ("dorus","tantalus","charon","mnemophage","ephialtes","warband")]
    for r in roster:
        present = r.lower() in names
        mark = "  <<<< SPARTA" if "sparta" in r else ""
        print(f"    {'OK ' if present else 'MISSING'} {r}{mark}")

    # field-level identity check: sparta vs garden (should be identical structure)
    print("\n" + "="*100)
    print("FIELD DIFF: svc_helos_trav_sparta vs svc_helos_trav_garden (non-identical fields):")
    fa = db.get_fields(r"records\quests\svc_helos_trav_sparta.dbr")
    fb = db.get_fields(r"records\quests\svc_helos_trav_garden.dbr")
    if fa and fb:
        allk = list(dict.fromkeys(list(fa.keys()) + list(fb.keys())))
        diffs = 0
        for k in allk:
            va = fa[k].value if k in fa else "<absent>"
            vb = fb[k].value if k in fb else "<absent>"
            if va != vb:
                print(f"    {k:28s} sparta={va!r}  garden={vb!r}")
                diffs += 1
        print(f"  total differing fields: {diffs} (expected: description only)")

if __name__ == "__main__":
    main()
