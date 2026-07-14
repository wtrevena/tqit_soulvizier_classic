r"""tools/patches/souls_quality.py - round-1 souls quality fixes.

RCA + evidence: docs/reports/souls_quality_audit.md (full-roster ground-truth
audit of the build40 GOLDEN arz, md5 b33c5a44). Two defect classes are fixed
here; both live ENTIRELY inside the mod-generated svc_uber soul namespace
(create_uber_souls.py output) and touch NO SV-original soul, NO Occult/Hunting
hand-tuning, and NO other registry module's records (disjointness proven in the
report + scratchpad probes).

--------------------------------------------------------------------------------
FIX 1 (P1, the 3 DEFICIENT souls) - Legendary tier WEAKER than Epic
--------------------------------------------------------------------------------
crowboar / onyxspine / steamcrawler uber souls run augment levels n/e/l = 1/2/1
(crowboar also itemSkillLevel 1/2/1): the Legendary ring is strictly worse than
the Epic. Root cause (audit sec 4): create_uber_souls scales SOUL_DESIGNS' base
level 1 by the per-tier _DIFF_SCALE (0.6/0.8/1.0) -> raw n/e/l = 0/0/1, then the
B-SOUL-PROC-1 level backstop (_fix_soul_skill_levels) BUMPS level-0 grants to the
per-tier default (n->1, e->2) but SKIPS the L ring because its scaled value was
already 1 (>=1) -> the inversion. Healthy siblings from the SAME generator
(bloodrunner, xix) run 1/2/3, so the intended progression is unambiguous.

FIX: set the L-tier augment (and, for crowboar, granted-skill) levels to 3, the
bloodrunner/xix Legendary value. We RAISE only (never lower), so this is
order-independent w.r.t. the backstop, which runs AFTER this module in
run_registry_gates and only ever bumps level-0 (it leaves our >=1 L ring alone
and independently completes n/e = 1/2). Will's skill PICKS are untouched - only
the tier LEVEL of the existing augment/grant changes.

--------------------------------------------------------------------------------
FIX 2 (P2-b, 54 families / 108 rings) - Epic + Legendary show the Normal icon
--------------------------------------------------------------------------------
Every create_uber_souls-generated svc_uber e/l ring carries
bitmap=SVItems\jewelry\soul_n_icon.tex (the generator hardcodes SOUL_BITMAP for
all tiers). The icon law (CLAUDE.md key lessons; every SV-inherited soul obeys
it) is soul_{n,e,l}_icon.tex per tier. FIX: rewrite the tier letter in place so
an e ring shows soul_e_icon and an l ring shows soul_l_icon. Purely cosmetic;
the soul_e/soul_l textures already ship in SVItems.arc. Rings whose soul icon
already matches their tier (the 47 module-authored svc_uber souls: hadesmarshal,
diadochi, neferkha, ...) are left untouched, so this module stays disjoint.

--------------------------------------------------------------------------------
NOT fixed here (see the report's FIX-LIST + WILL-DECISION sections)
--------------------------------------------------------------------------------
* P2-a Tomb Guardian obtainability: ground truth shows um_tombguardian_26 is a
  genuine COMMON 609-HP Anubis Hound (name tagMonsterName294) spawned as a
  champion in mummy caster packs - NOT a mis-classified uber (its Hero cousin
  um_foulbeast_28 has 5612 HP + a hero name tag). Reclassifying it to Hero is a
  BALANCE change across normal packs, not a cheap-in-passing icon fix -> a Will
  design decision, flagged in the report (grouped with the P3-a drop-gate call).
* P2-c boss-summon nymph icons: already fixed on the unmerged feat/b40-soul-icons
  branch (commit 9db3f5f); integrate that branch (no duplicate work here).
* P2-d Soulfeeder pet spirit-breath: verified an AUDIT FALSE POSITIVE - the mod's
  bonepet20 already casts bonescourge_spiritbreath (skillName4 +
  specialAttack2SkillName, both resolving). The audit's "loss" was SV's
  xxx-prefixed DISABLED variant + the drxplaceholder marker; nothing to restore.

Module contract (tools/patches/README.md): MODULE_NAME + apply(db, tags), plus a
post-finalization verify(db, tags) that fail-louds the tier-monotonicity + icon
invariants over the FINAL assembled db so the class cannot silently regress.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # tools/ on path

MODULE_NAME = 'Souls quality (svc_uber tier inversion + per-tier icons)'

_UBER = '\\soul\\svc_uber\\'

# FIX 1: the 3 DEFICIENT souls - exact L-tier target levels (audit sec 4). Values
# match the healthy bloodrunner/xix Legendary tier (3). We only RAISE.
_DEFICIENT_L_FIX = {
    r'records\item\equipmentring\soul\svc_uber\crowboar_soul_l.dbr':
        {'augmentSkillLevel1': 3, 'augmentSkillLevel2': 3, 'itemSkillLevel': 3},
    r'records\item\equipmentring\soul\svc_uber\onyxspine_soul_l.dbr':
        {'augmentSkillLevel1': 3, 'augmentSkillLevel2': 3},
    r'records\item\equipmentring\soul\svc_uber\steamcrawler_soul_l.dbr':
        {'augmentSkillLevel1': 3, 'augmentSkillLevel2': 3},
}

# soul_{n,e,l}_icon.tex family (the tier-icon standard). Case-insensitive match.
_SOUL_ICON_RE = re.compile(r'(?i)soul_([nel])_icon\.tex$')


def _norm(p):
    return str(p).replace('/', '\\').lower().strip()


def _first(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _sval(db, rec, field):
    v = _first(db.get_field_value(rec, field))
    return v.strip() if isinstance(v, str) and v.strip() else None


def _ival(db, rec, field):
    v = _first(db.get_field_value(rec, field))
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _name_map(db):
    """normalized path -> exact stored record name (get_fields is case-sensitive)."""
    return {_norm(n): n for n in db.record_names()}


def _tier_of(norm_name):
    m = re.search(r'_soul_([nel])\.dbr$', norm_name)
    return m.group(1) if m else None


def _iter_uber_rings(db, nm=None):
    """(exact_name, norm_name, tier) for every svc_uber soul ring with an n/e/l tier."""
    names = nm.values() if nm is not None else db.record_names()
    for n in names:
        nn = _norm(n)
        if _UBER not in nn or not nn.endswith('.dbr'):
            continue
        tier = _tier_of(nn)
        if tier:
            yield n, nn, tier


def apply(db, tags):
    nm = _name_map(db)

    # ── FIX 1: DEFICIENT L-tier level inversion (raise-only, clobber-safe) ──────
    lvl_edits = 0
    for path, fields in _DEFICIENT_L_FIX.items():
        rec = nm.get(_norm(path))
        if rec is None:
            raise SystemExit(
                "souls_quality: DEFICIENT target absent from db: %s (build base "
                "changed - refusing to run silently)" % path)
        for field, target in fields.items():
            cur = _ival(db, rec, field)
            if cur is None:
                # The field must exist (augment/grant already authored) so
                # set_field preserves its INT dtype. A missing field would mean
                # the soul shape changed under us - fail loud rather than guess.
                raise SystemExit(
                    "souls_quality: %s missing field %s (expected authored by "
                    "create_uber_souls) - shape changed" % (path, field))
            if cur < target:
                # Field exists -> no explicit dtype (INT preserved; the
                # cloned-record dtype-corruption law is about NEW fields).
                db.set_field(rec, field, target)
                lvl_edits += 1

    # ── FIX 2: per-tier soul icons on svc_uber e/l rings ───────────────────────
    icon_edits = 0
    for rec, nn, tier in _iter_uber_rings(db, nm):
        bmp = _sval(db, rec, 'bitmap')
        if not bmp:
            continue
        m = _SOUL_ICON_RE.search(bmp)
        if not m or m.group(1) == tier:
            continue  # not a standard soul icon, or already the correct tier
        new_bmp = _SOUL_ICON_RE.sub('soul_%s_icon.tex' % tier, bmp)
        db.set_field(rec, 'bitmap', new_bmp)  # existing STRING field, dtype kept
        icon_edits += 1

    print("    souls_quality: raised %d DEFICIENT L-tier level(s) (crowboar/"
          "onyxspine/steamcrawler); fixed %d svc_uber e/l tier-icon(s)"
          % (lvl_edits, icon_edits))


def _monotonicity_violations(db, nm=None):
    """Every svc_uber family with all 3 tiers: augmentSkillLevel1..4 (where the
    augment NAME is present in all 3 tiers) and itemSkillLevel (where the grant is
    present in all 3) must be non-decreasing n<=e<=l. Returns [(family, field, [n,e,l])]."""
    nm = nm if nm is not None else _name_map(db)
    fam = {}
    for rec, nn, tier in _iter_uber_rings(db, nm):
        m = re.search(r'\\svc_uber\\(.+?)_soul_[nel]\.dbr$', nn)
        if m:
            fam.setdefault(m.group(1), {})[tier] = rec
    bad = []
    for clean, tiers in sorted(fam.items()):
        if not all(t in tiers for t in ('n', 'e', 'l')):
            continue
        recs = [tiers['n'], tiers['e'], tiers['l']]
        for k in (1, 2, 3, 4):
            names = [_sval(db, r, 'augmentSkillName%d' % k) for r in recs]
            if not all(names):
                continue
            lv = [_ival(db, r, 'augmentSkillLevel%d' % k) for r in recs]
            if None not in lv and not (lv[0] <= lv[1] <= lv[2]):
                bad.append((clean, 'augmentSkillLevel%d' % k, lv))
        isn = [_sval(db, r, 'itemSkillName') for r in recs]
        if all(isn):
            lv = [_ival(db, r, 'itemSkillLevel') for r in recs]
            if None not in lv and not (lv[0] <= lv[1] <= lv[2]):
                bad.append((clean, 'itemSkillLevel', lv))
    return bad


def _icon_violations(db, nm=None):
    """Every svc_uber ring whose bitmap is a soul_{n,e,l}_icon must match its tier.
    Returns [(record, tier, bitmap)]."""
    nm = nm if nm is not None else _name_map(db)
    bad = []
    for rec, nn, tier in _iter_uber_rings(db, nm):
        bmp = _sval(db, rec, 'bitmap')
        if not bmp:
            continue
        m = _SOUL_ICON_RE.search(bmp)
        if m and m.group(1) != tier:
            bad.append((rec, tier, bmp))
    return bad


def verify(db, tags):
    """POST-FINALIZATION fail-loud gates (run over the FINAL assembled db, after
    run_registry_gates' backstop + drop forcer). Proves the tier-inversion class
    and the per-tier icon law hold across the WHOLE svc_uber roster, so the class
    cannot silently regress in a future content build."""
    nm = _name_map(db)

    mono = _monotonicity_violations(db, nm)
    if mono:
        lines = '\n'.join("      %s %s n/e/l=%s" % (c, f, lv) for c, f, lv in mono)
        raise SystemExit(
            "souls_quality verify: svc_uber augment/grant tier INVERSION "
            "(Legendary weaker than Epic) on %d field(s):\n%s" % (len(mono), lines))

    icons = _icon_violations(db, nm)
    if icons:
        lines = '\n'.join("      %s (tier %s) has %s"
                          % (r.rsplit('\\', 1)[-1], t, b) for r, t, b in icons)
        raise SystemExit(
            "souls_quality verify: %d svc_uber ring(s) show a wrong-tier soul "
            "icon:\n%s" % (len(icons), lines))

    print("    souls_quality verify OK: svc_uber tiers monotonic (n<=e<=l) + "
          "per-tier icons correct across the roster")
