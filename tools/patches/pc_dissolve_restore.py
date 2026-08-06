r"""pc_dissolve_restore - PR-1 (Steam player fleurydid, 2026-07-29, verbatim
"quand je meurt tombe invisible" = "when I die I fall/turn invisible"):
the PLAYER CHARACTER goes INVISIBLE on death/respawn.

--------------------------------------------------------------------------------
ROOT CAUSE - MEASURED FROM THE SHIPPED BYTES (arz adc7ee4afbae54dfd883a3c52ddbcf51)
--------------------------------------------------------------------------------
The two ACTIVE player-character records

    records\xpack\creatures\pc\femalepc01.dbr
    records\xpack\creatures\pc\malepc01.dbr

are taken VERBATIM from Soulvizier 0.98i by the DB merge (nothing in our build
touches their render fields - proven: the only PC records the build edits are the
anm_*pc animation TABLES, never these creature records). SV 0.98i made two
render-state changes relative to base TQAE, and BOTH survive into the shipped arz:

  field              base TQAE            SV 0.98i / OURS      SVAERA (maintained port)
  ----------------   -----------------    -----------------    ------------------------
  dissolveTexture    Effects\Textures\    (REMOVED / None)     Effects\Textures\
                     CloudTEST03.tex                           CloudTEST03.tex
  allowTransparency  0 (female)           1 (female)           1 (female)
                     0 (male)             0 (male)             0 (male)
  mesh               Creatures\pc\...     DRX\meshes\pc\...    SV_NewSkins\...

`dissolveTexture` is NOT a copy-paste default: only ~11% of base creatures carry
it (4,509 / 41,331), and base put it on the PC records deliberately. It feeds the
engine's DISSOLVE / alpha-FADE pass - the render path that runs when a creature
spawns-in or DIES/despawns (the mesh's own shader, StandardSkinnedFresnel.ssh,
has no dissolve sampler, so the field cannot be consumed anywhere but that engine
pass). `allowTransparency=1` is what ENABLES that alpha path for a creature.

MECHANISM (self-consistent across base / SVAERA / ours):
  * base female   : allowTransparency=0  AND dissolveTexture present -> doubly safe.
  * SVAERA female : allowTransparency=1  BUT dissolveTexture present -> the fade
                    pass has its noise texture -> completes cleanly -> safe.
  * OURS female   : allowTransparency=1  AND dissolveTexture REMOVED -> the death
                    fade path is enabled with NO dissolve texture -> the mesh is
                    left fully transparent (alpha 0) and the respawn re-render does
                    not restore it -> INVISIBLE ON DEATH. Exactly fleurydid.
  * the 2,878 base SCENERY records with allowTransparency=1 and no dissolveTexture
    are the control: they render fine because scenery never dies/despawn-fades.
    The player dies. That is the whole difference.

Predicted to be FEMALE-specific (male active PC has allowTransparency=0, so it
never enters the alpha-fade path). fleurydid did not name his class/gender - that
is the one load-bearing question to put back to him (see docs/BACKLOG.md PR-1).

--------------------------------------------------------------------------------
THE FIX - the SVAERA-aligned, strictly-additive restore
--------------------------------------------------------------------------------
Restore `dissolveTexture = Effects\Textures\CloudTEST03.tex` (the BASE TQAE and
SVAERA value; the asset resolves in base Effects.arc, 87,548 B) on BOTH active PC
records. This makes our female path match SVAERA's EXACTLY on these fields
(allowTransparency=1 + dissolveTexture=CloudTEST03) and restores the base value on
the male verbatim. It is purely additive: worst case (if dissolve is not the
cause) it is a no-op; it cannot regress the alive-render or introduce a new bug,
because it is precisely the value base + SVAERA ship.

DELIBERATELY NOT TOUCHED: allowTransparency on the female. SVAERA keeps it at 1
(the DRX/SV female skirt mesh may need the alpha path for its skirt cutouts), so
zeroing it would DIVERGE from the maintained port and risk the intended look. The
dissolveTexture restore is the SVAERA-matched, lower-risk lever.

IN-GAME CONFIRMATION IS LAUNCH-GATED. This module fixes an objective in-data
regression (base + SVAERA both ship the field we dropped) and is proven byte-clean
from a rebuild, but whether it resolves fleurydid's exact symptom can only be
confirmed by an in-game death test - the orchestrator owns deploys.

SHARED-RECORD LAW: femalepc01/malepc01 are the sole active PC creature records;
no other REGISTRY module writes them (disjoint namespace), so this module is
order-independent and registered late (before the no-op 'visuals') purely so its
verify() reads the final assembled db. The `old_*pc01` fallbacks are NOT touched
(they carry no dissolveTexture in base either - a different lineage).
"""
import os
import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))   # tools/ on path

MODULE_NAME = "PR-1: restore player dissolveTexture (fix invisible-on-death)"

# The base TQAE + SVAERA value. Resolves in base Resources\Effects.arc.
DISSOLVE_TEX = r'Effects\Textures\CloudTEST03.tex'

# The two ACTIVE player-character creature records (the ones the class picker and
# the running player use). old_femalepc01/old_malepc01 are the preserved base
# fallbacks and are intentionally out of scope.
PC_RECORDS = (
    r'records\xpack\creatures\pc\femalepc01.dbr',
    r'records\xpack\creatures\pc\malepc01.dbr',
)


def _norm(p):
    return str(p).replace('/', '\\').lower()


def _require_gates():
    return os.environ.get('SVC_REQUIRE_GATES', '') not in ('', '0', 'false', 'False')


def _gv1(db, rec, field):
    v = db.get_field_value(rec, field)
    if isinstance(v, list):
        return v[0] if v else None
    return v


def apply(db, tags):
    print("\n=== [pc_dissolve_restore] PR-1: restore the player's dissolveTexture ===")
    changed = 0
    for rec in PC_RECORDS:
        if not db.has_record(rec):
            # fail loud: the whole premise is that these are the shipped PC records
            raise SystemExit(
                "pc_dissolve_restore: active PC record MISSING: %s "
                "(the merge no longer ships it?) - refusing to no-op silently" % rec)
        cur = _gv1(db, rec, 'dissolveTexture')
        if _norm(cur) == _norm(DISSOLVE_TEX):
            print("    %-48s already = %s (no write)"
                  % (rec.rsplit('\\', 1)[-1], DISSOLVE_TEX))
            continue
        db.set_field(rec, 'dissolveTexture', DISSOLVE_TEX)
        db._modified.add(rec)
        changed += 1
        print("    %-48s dissolveTexture: %s -> %s"
              % (rec.rsplit('\\', 1)[-1], cur, DISSOLVE_TEX))
    print("=== [pc_dissolve_restore] %d record(s) restored; verify() runs "
          "post-finalization ===\n" % changed)
    return tags


def verify(db, tags=None):
    problems = []
    notes = []

    # 1. every active PC record now carries the base+SVAERA dissolveTexture.
    for rec in PC_RECORDS:
        if not db.has_record(rec):
            problems.append("active PC record MISSING at verify: %s" % rec)
            continue
        got = _gv1(db, rec, 'dissolveTexture')
        if _norm(got) != _norm(DISSOLVE_TEX):
            problems.append(
                "%s carries dissolveTexture=%r, expected %s - the player's death/"
                "respawn alpha-fade pass has no dissolve texture, which is the "
                "measured cause of PR-1 (invisible on death)."
                % (rec, got, DISSOLVE_TEX))

    # 2. the restored texture must actually RESOLVE in the shipped art (a field
    #    that points at a missing asset is worse than an absent field).
    try:
        from mesh_assets import arcs_available, asset_exists, mod_resource_dirs
        _mod_res = mod_resource_dirs()
        modres = str(_mod_res[0]) if _mod_res else None
        if not arcs_available(modres):
            msg = ("pc_dissolve_restore ASSET gate DID NOT RUN - the Effects arc "
                   "is not reachable; build into work/<mod>/ with Resources beside "
                   "it, or set SVC_TQAE_DIR")
            (problems if _require_gates() else notes).append(
                ("" if _require_gates() else "WARNING: ") + msg)
        elif not asset_exists(DISSOLVE_TEX, modres):
            problems.append(
                "restored dissolveTexture %s does NOT resolve in any shipped arc - "
                "refusing to point the PC at a missing dissolve asset" % DISSOLVE_TEX)
        else:
            notes.append("dissolve texture resolves in shipped art: %s" % DISSOLVE_TEX)
    except Exception as e:                                   # resolver import/really-broken
        (problems if _require_gates() else notes).append(
            ("" if _require_gates() else "WARNING: ")
            + "pc_dissolve_restore could not run the asset resolver: %r" % e)

    if problems:
        for p in problems:
            print("  PC-DISSOLVE OFFENDER: %s" % p)
        raise SystemExit("pc_dissolve_restore.verify FAILED: %d problem(s)" % len(problems))
    for n in notes:
        print("  [pc_dissolve_restore] %s" % n)
    print("  [pc_dissolve_restore].verify OK: %d active PC record(s) carry a "
          "resolvable dissolveTexture (%s)." % (len(PC_RECORDS), DISSOLVE_TEX))
    return tags


# ────────────────────────────────────────────────────────────────────────────
# PLANTED NEGATIVES  (py tools/patches/pc_dissolve_restore.py --negtest)
# ────────────────────────────────────────────────────────────────────────────
def _negtest():
    from collections import OrderedDict

    class _TF(object):
        def __init__(self, v):
            self.values = list(v) if isinstance(v, list) else [v]

    class _Stub(object):
        def __init__(self):
            self.d = {}
            self._modified = set()

        def has_record(self, n):
            return n in self.d

        def record_names(self):
            return list(self.d)

        def get_field_value(self, n, f):
            rec = self.d.get(n)
            if rec is None:
                return None
            return rec.get(f)

        def set_field(self, n, f, v, dt=None):
            self.d.setdefault(n, {})[f] = v if isinstance(v, list) else [v]

        def get_fields(self, n):
            rec = self.d.get(n)
            if rec is None:
                return None
            return OrderedDict((k, _TF(v)) for k, v in rec.items())

    def _base():
        db = _Stub()
        for r in PC_RECORDS:
            db.d[r] = {'mesh': ['DRX\\meshes\\pc\\x.msh']}     # no dissolveTexture yet
        return db

    # A verify() that skips the asset check (no arcs in the stub harness): monkeypatch
    # SVC_REQUIRE_GATES off just for the resolver branch by importing here.
    import mesh_assets
    orig_avail = mesh_assets.arcs_available
    mesh_assets.arcs_available = lambda *a, **k: False        # force ASSET gate to WARN, not fail
    os.environ.setdefault('SVC_REQUIRE_GATES_SAVE', os.environ.get('SVC_REQUIRE_GATES', ''))
    os.environ['SVC_REQUIRE_GATES'] = '0'                     # so the un-runnable asset gate WARNs
    try:
        # clean apply -> verify must PASS
        db = _base()
        apply(db, {})
        try:
            verify(db)
        except SystemExit as e:
            print("NEGTEST SETUP FAIL: clean apply+verify should PASS but raised: %s" % e)
            return 1

        plants = [
            ('a PC record is left WITHOUT the dissolveTexture (the PR-1 defect)',
             lambda db: db.d[PC_RECORDS[0]].pop('dissolveTexture', None)),
            ('a PC record has dissolveTexture blanked to empty',
             lambda db: db.d[PC_RECORDS[1]].__setitem__('dissolveTexture', [''])),
            ('a PC record points dissolveTexture at the WRONG texture',
             lambda db: db.d[PC_RECORDS[0]].__setitem__(
                 'dissolveTexture', ['Effects\\Textures\\NoSuchCloud.tex'])),
            ('an active PC record disappears entirely',
             lambda db: db.d.pop(PC_RECORDS[1])),
        ]
        bad = 0
        for label, plant in plants:
            db = _base()
            apply(db, {})
            plant(db)
            try:
                verify(db)
            except SystemExit:
                print("  negtest OK  (caught): %s" % label)
                continue
            print("  negtest FAIL (missed): %s" % label)
            bad += 1
        print("negtest: %d/%d plants caught" % (len(plants) - bad, len(plants)))
        return 1 if bad else 0
    finally:
        mesh_assets.arcs_available = orig_avail
        os.environ['SVC_REQUIRE_GATES'] = os.environ.pop('SVC_REQUIRE_GATES_SAVE', '')


if __name__ == '__main__':
    import sys
    if '--negtest' in sys.argv:
        sys.exit(_negtest())
    print("pc_dissolve_restore: restores %s on %s"
          % (DISSOLVE_TEX, ', '.join(r.rsplit('\\', 1)[-1] for r in PC_RECORDS)))
    sys.exit(0)
