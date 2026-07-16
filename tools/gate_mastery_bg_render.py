r"""MASTERY-UI RENDER GATE (build60, fail-loud): every UI background / icon
bitmap referenced by a LIVE mastery skill-pane record must RESOLVE in the shipped
arc set (mod Resources UNION base-game Resources, engine-faithful archive rule),
AND every one of the 9 live pane-background records must be the vanilla
`BitmapUIAware` widget class with a non-empty `bitmapNames` array.

Born from the build60 black-background RCA (docs/reports/b60_mastery_bg_render.md):
the b37/b38 waves repointed the pane texture but left the record a `BitmapSingle`,
whose singular `bitmapName` the UI-aware pane slot never reads -> the texture
resolved in the arc yet the pane rendered BLACK. This gate makes BOTH failure
modes un-shippable:

  (A) RESOLUTION - a pane/chrome bitmap ref whose arc entry is absent from every
      shipped mod arc and every base-game arc (the old `SkillsPanel\...diablo`
      class, and any future mistyped path).
  (B) STRUCTURE  - a pane background that is not `BitmapUIAware` + `bitmapNames`
      (the exact regression that shipped in build40 and reads as black in-game).

Archive rule (matches tools/validate_render_chain.EngineArcResolver): a plain
`<Arc>\<inner>` ref resolves in the mod Resources `<Arc>.arc` first, else the base
`<game>\Resources\<Arc>.arc`; an `XPackN\<Arc>\<inner>` ref resolves only in
`<game>\Resources\XPackN\<Arc>.arc`.

Scope = LIVE player masteries only: masteries 1-8 (`records\ingameui\player
skills\mastery {1..8}\`), Dream/9 (`records\xpack\ui\skills\mastery 9\`), and the
shared chrome (`records\ingameui\player skills\mastery base\`). The dead
`mastery 9\11-15-06\` ArtManager backup and the 0-referenced `records\skills\
scroll skills\masteries\earth\` DRX dev tree are intentionally EXCLUDED (a player
can never reach them; see the report).

usage: py tools/gate_mastery_bg_render.py <mod.arz> <mod_resources_dir> <game_dir>
exit 0 = PASS, 1 = FAIL (unresolved ref or wrong pane structure), 2 = load error.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase   # noqa: E402
from arc_patcher import ArcArchive    # noqa: E402

XPACK_SCOPES = ("xpack", "xpack2", "xpack3", "xpack4")

_UI = "records\\ingameui\\player skills\\mastery %d\\"
_DREAM = "records\\xpack\\ui\\skills\\mastery 9\\"
_MB = "records\\ingameui\\player skills\\mastery base\\"

_PANE_DIRS = [_UI % n for n in range(1, 9)] + [_DREAM]
_PANE_LEAVES = ("skillpanebasebitmap.dbr", "skillpanereallocationbitmap.dbr")

# every field on any of these records whose value is a `.tex` is a bitmap ref
_BITMAP_FIELD_HINT = "bitmap"


class _ArcResolver:
    def __init__(self, mod_res, game_dir):
        self.mod_res = Path(mod_res) if mod_res else None
        self.game = Path(game_dir)
        self._cache = {}

    def _names(self, folder, arcname):
        if folder is None or not Path(folder).is_dir():
            return None
        key = (str(folder).lower(), arcname.lower())
        if key in self._cache:
            return self._cache[key]
        cand = Path(folder) / (arcname + ".arc")
        if not cand.exists():
            hits = [p for p in Path(folder).glob("*.arc") if p.stem.lower() == arcname.lower()]
            cand = hits[0] if hits else None
        names = None
        if cand and cand.exists():
            try:
                arc = ArcArchive.from_file(cand)
                names = {e.name.lower().replace("\\", "/") for e in arc.entries if e.name}
            except Exception:
                names = None
        self._cache[key] = names
        return names

    def resolve(self, ref):
        parts = str(ref).replace("/", "\\").split("\\")
        if len(parts) < 2:
            return (False, "too-short")
        p0 = parts[0].lower()
        if p0 in XPACK_SCOPES and len(parts) >= 3:
            names = self._names(self.game / "Resources" / parts[0], parts[1])
            inner = "/".join(parts[2:]).lower()
            if names is None:
                return (False, "no %s\\%s.arc" % (parts[0], parts[1]))
            return (inner in names, "%s\\%s.arc" % (parts[0], parts[1]))
        inner = "/".join(parts[1:]).lower()
        mod = self._names(self.mod_res, parts[0])
        if mod is not None and inner in mod:
            return (True, "MOD:%s.arc" % parts[0])
        base = self._names(self.game / "Resources", parts[0])
        if base is not None and inner in base:
            return (True, "base:%s.arc" % parts[0])
        return (False, "UNRESOLVED %s.arc(mod=%s base=%s)" % (
            parts[0], "absent" if mod is None else "no-entry",
            "absent" if base is None else "no-entry"))


def validate(arz_path, mod_resources, game_dir):
    db = ArzDatabase.from_arz(Path(arz_path))
    recmap = {n.lower().replace("/", "\\"): n for n in db.record_names()}
    res = _ArcResolver(mod_resources, game_dir)

    def rec(p):
        return recmap.get(p.lower().replace("/", "\\"))

    def fvals(recname, field):
        for k, tf in (db.get_fields(recname) or {}).items():
            if k.split("###")[0] == field:
                return list(tf.values)
        return None

    print("=" * 72)
    print("MASTERY-UI RENDER GATE (build60): resolution + pane structure")
    print("  arz :", arz_path)

    live_dirs = _PANE_DIRS + [_MB]
    unresolved = []
    struct_bad = []
    checked_refs = 0

    # (A) resolution: every .tex on every LIVE mastery UI record
    for n in db.record_names():
        nl = n.lower().replace("/", "\\")
        if not any(nl.startswith(d.lower()) for d in live_dirs):
            continue
        for k, tf in (db.get_fields(n) or {}).items():
            kf = k.split("###")[0]
            if _BITMAP_FIELD_HINT not in kf.lower():
                continue
            for v in tf.values:
                s = str(v)
                if not s.lower().endswith(".tex"):
                    continue
                checked_refs += 1
                ok, where = res.resolve(s)
                if not ok:
                    unresolved.append((n, kf, s, where))

    # (B) structure: the 9 live panes must be BitmapUIAware + non-empty bitmapNames
    panes = 0
    for d in _PANE_DIRS:
        for leaf in _PANE_LEAVES:
            r = rec(d + leaf)
            if not r:
                struct_bad.append((d + leaf, "RECORD MISSING"))
                continue
            panes += 1
            tpl = str((fvals(r, "templateName") or [""])[0])
            names = fvals(r, "bitmapNames")
            if not tpl.lower().endswith("bitmapuiaware.tpl"):
                struct_bad.append((r, "templateName=%r (want BitmapUIAware.tpl)" % tpl))
            if not names or not str(names[0]).strip():
                struct_bad.append((r, "bitmapNames empty/absent (pane will render BLACK)"))

    print("  live UI records scanned; bitmap .tex refs checked: %d" % checked_refs)
    print("  pane-background records structurally checked: %d" % panes)

    fails = 0
    for n, kf, s, where in unresolved:
        print("  UNRESOLVED: %s :: %s -> %s  [%s]" % (n, kf, s, where))
        fails += 1
    for r, msg in struct_bad:
        print("  STRUCT-FAIL: %s :: %s" % (r, msg))
        fails += 1

    if fails:
        print("RESULT: FAIL - %d mastery-UI render defect(s); this build does not ship"
              % fails)
        return 1
    print("RESULT: PASS - all %d pane/chrome bitmap refs resolve; %d panes are "
          "BitmapUIAware w/ bitmapNames" % (checked_refs, panes))
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(validate(sys.argv[1], sys.argv[2], sys.argv[3]))
