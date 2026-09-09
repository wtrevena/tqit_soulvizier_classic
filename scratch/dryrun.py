"""Dry-run replay of mastery_bg_render on a COPY of the DEPLOYED build40 arz
(b33c5a44): apply -> verify() -> write -> prove intended-only delta -> run the
new render gate -> capture the exact golden drift keys for m5/m6.
"""
import sys
from pathlib import Path

REPO = Path(r"C:/Users/willi/repos/tqit_soulvizier_classic")
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tools" / "patches"))
from arz_patcher import ArzDatabase   # noqa

GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition")
DEV = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassicDEV")
ARZ = DEV / "Database" / "SoulvizierClassicDEV.arz"
MOD_RES = DEV / "Resources"
OUT = Path(__file__).resolve().parent / "patched.arz"

import mastery_bg_render as mod            # noqa
import gate_mastery_bg_render as gate      # noqa
import validate_mastery_golden as golden   # noqa


def field_map(db, rec):
    out = {}
    for k, tf in (db.get_fields(rec) or {}).items():
        out[k.split("###")[0]] = (tf.dtype, [str(x) for x in tf.values])
    return out


# 1. baseline snapshot of ALL records (field maps) BEFORE
print(">>> loading deployed arz (b33c5a44) ...")
before = ArzDatabase.from_arz(ARZ)
before_maps = {n: field_map(before, n) for n in before.record_names()}

# 2. apply module on a fresh load
db = ArzDatabase.from_arz(ARZ)
mod.apply(db, {})
mod.verify(db, {})

# 3. intended-only delta: which records changed vs before?
changed = []
for n in db.record_names():
    if field_map(db, n) != before_maps.get(n):
        changed.append(n)
print("\n>>> records changed by module: %d" % len(changed))
for n in sorted(changed):
    print("    ", n)

# categorize
pane = [n for n in changed if n.lower().endswith(("skillpanebasebitmap.dbr", "skillpanereallocationbitmap.dbr"))]
chrome = [n for n in changed if "mastery base" in n.lower()]
other = [n for n in changed if n not in pane and n not in chrome]
print("\n  panes changed: %d (expect 18)  chrome changed: %d (expect 4)  OTHER: %d (expect 0)"
      % (len(pane), len(chrome), len(other)))
if other:
    print("  !!! UNEXPECTED changed records:", other)

# 4. show one before/after
ex = r"records\ingameui\player skills\mastery 1\skillpanebasebitmap.dbr"
print("\n>>> example m1 base-bg AFTER:")
for k, v in field_map(db, ex).items():
    print("     %-20s %s" % (k, v))

# 5. write + run render gate
db.write_arz(OUT)
print("\n>>> RENDER GATE on patched arz:")
rc_gate = gate.validate(str(OUT), str(MOD_RES), str(GAME))
print(">>> gate rc =", rc_gate)

# 6. golden drift for m5/m6 (arz-only, no text) - capture exact keys to waive
print("\n>>> GOLDEN drift keys introduced (m5/m6):")
g = golden.__dict__
gp = json._default_decoder if False else None  # noqa
import json
gold = json.loads((REPO / "tools" / "occult_hunting_golden.json").read_text(encoding="utf-8"))
cur = golden.capture(str(OUT), None)
drifts = golden._diff(gold, cur, check_tags=False)
overrides = gold.get("owner_approved_overrides", {})
new_keys = [k for k, m in drifts if k not in overrides]
already = [k for k, m in drifts if k in overrides]
print("   drift keys already waived:", len(already))
for k in already:
    print("      (waived)", k)
print("   NEW drift keys needing a waiver:", len(new_keys))
for k in new_keys:
    print("      ", k)
