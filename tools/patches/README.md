# patches-registry - the module contract

> The monolith `tools/apply_svc_patches.py` (~16k lines) is being split so
> content waves can own **disjoint modules** and run **in parallel**. This
> package is the ordered manifest + the machinery that runs the modules and
> proves coherency. **Round 1 (bootstrap) ships `REGISTRY` EMPTY** - the build
> is byte-identical to the pre-registry build. Content waves add their modules
> (one `REGISTRY` line each, on their own branch).

This README is the authoritative contract. Code your module against **this**.

---

## 1. What a module IS

A module is one file `tools/patches/<name>.py` that defines **exactly** two
public names:

```python
MODULE_NAME = "Four Generals quest upgrade"   # non-empty str: logs + gates

def apply(db, tags):
    # mutate db (records) and tags (Text) IN PLACE. No return value is used.
    ...
```

`_load_module` (in `__init__.py`) validates this **fail-loud** at build time:
a missing/empty `MODULE_NAME`, a missing/non-callable `apply`, or an import
error aborts the build with a clear message. There is no partial contract.

`apply` takes **positional** `(db, tags)`. Do not add required parameters.

---

## 2. The `db` and `tags` objects (identical to the monolith's)

These are the **same objects** the monolith authored - you are appending to a
fully-built DB, not starting fresh.

### `db` - `arz_patcher.ArzDatabase` (in-memory `.arz`)
Author records with the monolith's own idioms:

```python
from apply_svc_patches import _ensure_record    # tools/ is on sys.path

path = r"records\item\svc\my_thing.dbr"
_ensure_record(db, path, "database\\Templates\\Jewelry_Ring.tpl")  # bare record
db.set_field(path, "itemNameTag", "tagSVCMyThing")   # value: int/float/str/bool or list
val = db.get_field_value(path, "itemNameTag")
db.clone_record(src_path, dest_path)                 # copy a record (case-alias etc.)
db.has_record(path)          # bool
db.record_names()            # list[str]
```

Field-type rule (hard-won, see `CLAUDE.md`): **never pass an explicit `dtype`
to `set_field` on a cloned record** - INT/FLOAT corruption silently zeroes
values. Let `set_field` infer, or match the existing field's type.

Every write marks `db._modified` (via `set_field`/`clone_record`/`_ensure_record`
or a direct `db._modified.add(path)`). The registry keys the collision gate and
`write_arz` off this set. **Do not reassign `db._modified`.**

### `tags` - `dict[str, str]` (Text tags)
```python
tags["tagSVCMyThing"] = "My Thing"                   # tagKey -> displayed text
tags["tagSVCMyThingDESC"] = "Flavor text that renders in the tooltip."
```
`build_text_arc.py` turns `tags` into `Text.arc`. Any tag your records
**reference** (name/desc) but you never **add** here is caught by the build's
text-tag invariant. Add every tag you reference.

---

## 3. Execution order (the coherency guarantee)

`build_svc_database.py` runs, in this exact order:

```
1. apply_all_extended_patches(db, ..., _defer_gates=True)   # monolith CONTENT
2. run_registry(db, tags)                                   # THESE modules, in REGISTRY order
3. apply_svc_patches.run_registry_gates(db, tags, ...)      # the WHOLE gate battery
```

Consequences you can rely on:

- Your `apply` runs **after** all monolith content and **after** earlier
  REGISTRY modules, and **before** the entire fail-loud gate battery.
- **Every monolith gate validates your records too.** The battery relocated
  into `run_registry_gates` includes: pet parity / gear / skill-kit, Runemaster
  golem-button, boss-kit clone-shape, mod-spawn-proxy eligibility, supra
  dead-refs, unclassified soul-leak, soul-augment resolution, soul-itemskill
  activation, Dorus soul amendment, granted-skill diversity, soul-summon
  identity, soul naming, MP spawn-equation (no `/`), portal born-open. Then, in
  `build_svc_database.py` after the `.arz` is written: container loot-shape,
  B-SUMMON-1 summon-pet validation, A9 render-chain, A7 Occult/Hunting golden,
  F2 summons-contract. **Nothing a module does escapes these.** Write clean
  content and the gates confirm it; write broken content and the build fails
  loud with the offender.
- The soul **drop-rate forcer** and **soul-desc-itemtext wiring** run in the
  battery too, so souls/monsters your module adds are drop-rate-normalized and
  desc-wired the same as monolith souls.

If your content needs to run **before** some monolith content (rare), it does
not belong in a registry module yet - raise it; do not reorder the monolith.

---

## 4. Coherency gates the registry itself enforces

Run over the modules (in `run_registry`), independent of the monolith battery:

- **S4a registry-integrity** - `REGISTRY` has no duplicate entries; every entry
  runs **exactly once, in manifest order**. The manifest order hash is logged
  and asserted (a mid-run mutation or reorder aborts the build).
- **S4b module-collision WARN** - after each module the build logs how many
  records + tags it touched. If **two modules write the same record (or tag)**,
  the build prints a loud `WARNING collision gate` naming **both** modules.
  Later-wins is legal registry semantics, but it is **never silent**. Keep
  modules **disjoint**; if you must co-edit a record, make the ordering explicit
  in `REGISTRY` and expect the warning.

---

## 5. The identity proof (permanent CI-style check)

With `REGISTRY == []`, `run_registry` does not touch `db` or `db._modified`, so
the full build produces an `.arz` **byte-identical** to the pre-bootstrap build
from the same base. This is the proof that the restructure changed nothing.

How to run it (same env for both; `PYTHONHASHSEED=0` is auto-pinned by the
build):

```
# A) baseline: build with the pre-registry code (or with REGISTRY empty and the
#    build_svc_database registry hook reverted)
# B) build with this bootstrap and REGISTRY == []
# The two SoulvizierClassic.arz MD5s MUST be equal.
md5sum <A>/SoulvizierClassic.arz <B>/SoulvizierClassic.arz
```

This bootstrap was landed **only** after that pair matched (see the commit
message / handoff for the exact MD5). Any future change to the registry seam
must re-prove it: **empty registry => byte-identical arz.**

Fast pre-flight (no build): `py tools/patches/_check_registry.py` validates
every REGISTRY module imports + satisfies the contract and prints the order
hash.

---

## 6. The template

`tools/patches/_smoke_example.py` is the copy-me reference module (a strict
no-op, intentionally **not** in `REGISTRY`). Start there:

```
copy tools/patches/_smoke_example.py -> tools/patches/<your_module>.py
# edit MODULE_NAME + apply(); append '<your_module>' to REGISTRY (your branch)
py tools/patches/_check_registry.py
```

---

## 7. Checklist for a content wave

- [ ] File `tools/patches/<name>.py` with `MODULE_NAME` (non-empty str) +
      `def apply(db, tags)`.
- [ ] All record writes via `_ensure_record` / `db.set_field` / `db.clone_record`
      (no explicit `dtype` on cloned records).
- [ ] Every referenced Text tag added to `tags`.
- [ ] Module is **disjoint** from other waves' records (no collisions expected).
- [ ] Appended one line to `REGISTRY` (your branch).
- [ ] `py tools/patches/_check_registry.py` passes.
- [ ] A full build passes every gate with your module registered.
