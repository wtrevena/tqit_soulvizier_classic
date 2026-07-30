r"""PROBE (read-only): R-101 - what QUEST-COUPLED state did our uber clones
inherit from the quest bosses they were cloned from?

R-101 fixes `perPartyMemberDropItemName`. Its "WIDER LESSON" section asks for
more than that:

    "we have cloned base-game quest bosses repeatedly to make ubers, and nobody
     enumerated what else a quest boss carries that a repeatable encounter must
     not inherit ... The lane should also sweep our clones for other
     quest-coupled fields (quest triggers, one-shot flags, journal hooks,
     `questItem*`-style references) and report what it finds, even where it
     changes nothing."

So this prints THREE things against a built `.arz`:
  1. every `um_*` record carrying `perPartyMemberDropItemName` (with dtype +
     the matching chance field + whether the item is itemClassification=Quest);
  2. the inbound-reference census for each leaked quest item (which records
     point at it), so the legitimate donors are named and can be proved
     untouched;
  3. THE WIDER SWEEP: every field name anywhere on an `um_*` record that looks
     quest-coupled (quest/journal/onetime/oneshot/unique-spawn), with the set of
     distinct values, so a second leak class cannot hide.

Usage:
  py tools/debug/probe_quest_coupled_fields.py <db.arz>
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # tools/
sys.path.insert(0, str(HERE))
from arz_patcher import ArzDatabase  # noqa: E402

DTYPE = {0: "INT", 1: "FLOAT", 2: "STRING", 3: "BOOL"}
QUEST_HINTS = ("quest", "journal", "onetime", "one_time", "oneshot",
               "perpartymember", "questitem")


def norm(s):
    return str(s).replace("/", "\\").lower()


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    def ff(n):
        return db.get_fields(n)

    def v(fields, key):
        tf = (fields or {}).get(key)
        if tf is None:
            for k, t in (fields or {}).items():
                if k.split("###")[0] == key:
                    tf = t
                    break
        if tf is None:
            return None, None
        val = tf.value
        return (val[0] if isinstance(val, list) and val else val), tf.dtype

    # ---- quest-classified items -------------------------------------------
    quest_items = set()
    for n in db.record_names():
        cls, _ = v(ff(n), "itemClassification")
        if cls and str(cls).strip().lower() == "quest":
            quest_items.add(norm(n))
    print("itemClassification==Quest records in DB: %d" % len(quest_items))

    ubers = [n for n in db.record_names() if norm(n).split("\\")[-1].startswith("um_")]
    print("um_* records in DB: %d" % len(ubers))

    # ---- 1. per-party drops on ubers --------------------------------------
    print("\n" + "=" * 88)
    print("1) EVERY um_* RECORD CARRYING perPartyMemberDropItemName")
    rows = []
    for n in ubers:
        fields = ff(n)
        drop, dt = v(fields, "perPartyMemberDropItemName")
        if not drop or not str(drop).strip():
            continue
        chance, cdt = v(fields, "perPartyMemberDropChance")
        desc, _ = v(fields, "description")
        rows.append((n, drop, dt, chance, cdt, desc, norm(drop) in quest_items))
    leaks = [r for r in rows if r[6]]
    print("   total carriers: %d   of which point at a QUEST item: %d"
          % (len(rows), len(leaks)))
    for n, drop, dt, chance, cdt, desc, isq in sorted(rows, key=lambda r: (not r[6], r[0])):
        print("   %s" % ("*** QUEST-ITEM LEAK ***" if isq else "(non-quest per-party drop)"))
        print("     record : %s   [%s]" % (n, desc))
        print("     drop   : %r  dtype=%s" % (drop, DTYPE.get(dt, dt)))
        print("     chance : %r  dtype=%s" % (chance, DTYPE.get(cdt, cdt)))

    # ---- 2. inbound census for each leaked item ---------------------------
    print("\n" + "=" * 88)
    print("2) INBOUND REFERENCES to each leaked quest item (the donors that must NOT change)")
    for item in sorted({norm(r[1]) for r in leaks}):
        holders = []
        for n in db.record_names():
            d, _ = v(ff(n), "perPartyMemberDropItemName")
            if d and norm(d) == item:
                holders.append(n)
        print("   %s  <- %d holder(s)" % (item, len(holders)))
        for h in sorted(holders):
            tag = "  OUR UBER (leak)" if norm(h).split("\\")[-1].startswith("um_") else "  legit donor"
            print("       %s%s" % (h, tag))

    # ---- 3. the wider sweep -----------------------------------------------
    print("\n" + "=" * 88)
    print("3) WIDER SWEEP - every quest-shaped FIELD present on any um_* record")
    found = {}
    for n in ubers:
        for k, tf in (ff(n) or {}).items():
            base = k.split("###")[0]
            if not any(h in base.lower() for h in QUEST_HINTS):
                continue
            val = tf.value
            val = val[0] if isinstance(val, list) and val else val
            if val in (None, "", 0, 0.0):
                continue
            found.setdefault(base, {}).setdefault(str(val), []).append(n)
    if not found:
        print("   (none)")
    for field in sorted(found):
        print("   FIELD %s" % field)
        for val, recs in sorted(found[field].items()):
            print("       %-58s on %d record(s)" % (val, len(recs)))
            for r in sorted(recs)[:6]:
                print("           %s" % r)


if __name__ == "__main__":
    main()
